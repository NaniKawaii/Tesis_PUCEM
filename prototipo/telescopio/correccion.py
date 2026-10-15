"""Componente de inteligencia artificial: corrección del error de apuntado.

Idea: cada vez que el telescopio hace GoTo hacia un objeto y el usuario lo
centra con los botones de ajuste fino, se registra cuánto hubo que corregir
(Δaz, Δalt). Esos errores no son aleatorios: dependen de la nivelación del
trípode, de la flexión de las piezas impresas en 3D y de la holgura de los
ejes, y por tanto dependen de la dirección (az, alt) hacia la que se apunta.

Con esos registros se entrena un modelo que predice el error para cualquier
dirección y se aplica antes de mover los motores. Se comparan dos modelos:

- "lineal": regresión lineal sobre funciones trigonométricas de (az, alt),
  equivalente a un modelo de apuntado clásico de pocos términos.
- "red_neuronal": perceptrón multicapa (MLP) que puede aprender errores no
  lineales que el modelo clásico no captura.

La evaluación usa validación cruzada (cada punto se predice con un modelo que
no lo vio al entrenar) y la prueba de Wilcoxon para datos pareados.
"""

from __future__ import annotations

from dataclasses import dataclass

import joblib
import numpy as np
from scipy.stats import wilcoxon
from sklearn.compose import TransformedTargetRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

TIPOS = ("lineal", "red_neuronal")
MINIMO_MUESTRAS = 10


def caracteristicas(az: np.ndarray, alt: np.ndarray) -> np.ndarray:
    a, h = np.radians(np.asarray(az, float)), np.radians(np.asarray(alt, float))
    return np.column_stack([np.sin(a), np.cos(a), np.sin(h), np.cos(h),
                            np.sin(a) * np.sin(h), np.cos(a) * np.sin(h)])


def error_en_cielo_arcmin(d_az, d_alt, alt) -> np.ndarray:
    """Separación angular real en el cielo (un Δaz pesa menos cerca del cenit)."""
    d_az, d_alt = np.asarray(d_az, float), np.asarray(d_alt, float)
    return 60.0 * np.hypot(d_az * np.cos(np.radians(alt)), d_alt)


def _crear_estimador(tipo: str):
    if tipo == "lineal":
        base = make_pipeline(StandardScaler(), Ridge(alpha=1e-3))
    elif tipo == "red_neuronal":
        base = make_pipeline(StandardScaler(), MLPRegressor(
            hidden_layer_sizes=(16, 16), activation="tanh", solver="lbfgs",
            alpha=1e-2, max_iter=5000, random_state=0))
    else:
        raise ValueError(f"Tipo de modelo desconocido: {tipo}. Use uno de {TIPOS}")
    return TransformedTargetRegressor(regressor=base, transformer=StandardScaler())


class ModeloCorreccion:
    def __init__(self, tipo: str = "red_neuronal"):
        self.tipo = tipo
        self._estimador = _crear_estimador(tipo)
        self.n_muestras = 0

    def entrenar(self, az, alt, d_az, d_alt) -> "ModeloCorreccion":
        if len(az) < MINIMO_MUESTRAS:
            raise ValueError(f"Se necesitan al menos {MINIMO_MUESTRAS} registros; hay {len(az)}")
        self._estimador.fit(caracteristicas(az, alt), np.column_stack([d_az, d_alt]))
        self.n_muestras = len(az)
        return self

    def predecir(self, az: float, alt: float) -> tuple[float, float]:
        d = self._estimador.predict(caracteristicas([az], [alt]))[0]
        return float(d[0]), float(d[1])

    def guardar(self, ruta: str) -> None:
        joblib.dump(self, ruta)

    @staticmethod
    def cargar(ruta: str) -> "ModeloCorreccion":
        return joblib.load(ruta)


@dataclass
class Evaluacion:
    tipo: str
    n: int
    error_sin_correccion: np.ndarray  # arcmin, por muestra
    error_con_correccion: np.ndarray  # arcmin, por muestra (validación cruzada)
    p_valor_wilcoxon: float

    def resumen(self) -> dict:
        def rms(x):
            return float(np.sqrt(np.mean(x ** 2)))
        return {
            "tipo": self.tipo,
            "n": self.n,
            "rms_sin_arcmin": round(rms(self.error_sin_correccion), 2),
            "rms_con_arcmin": round(rms(self.error_con_correccion), 2),
            "mediana_sin_arcmin": round(float(np.median(self.error_sin_correccion)), 2),
            "mediana_con_arcmin": round(float(np.median(self.error_con_correccion)), 2),
            "reduccion_rms_pct": round(100 * (1 - rms(self.error_con_correccion)
                                              / rms(self.error_sin_correccion)), 1),
            "p_valor_wilcoxon": float(f"{self.p_valor_wilcoxon:.3g}"),
        }


def evaluar(tipo: str, az, alt, d_az, d_alt, pliegues: int = 5) -> Evaluacion:
    """Validación cruzada: error residual si se hubiera aplicado la corrección."""
    az, alt, d_az, d_alt = (np.asarray(v, float) for v in (az, alt, d_az, d_alt))
    n = len(az)
    if n < MINIMO_MUESTRAS:
        raise ValueError(f"Se necesitan al menos {MINIMO_MUESTRAS} registros; hay {n}")
    residuo_az, residuo_alt = np.empty(n), np.empty(n)
    for entreno, prueba in KFold(min(pliegues, n), shuffle=True, random_state=0).split(az):
        modelo = ModeloCorreccion(tipo).entrenar(az[entreno], alt[entreno],
                                                 d_az[entreno], d_alt[entreno])
        pred = modelo._estimador.predict(caracteristicas(az[prueba], alt[prueba]))
        residuo_az[prueba] = d_az[prueba] - pred[:, 0]
        residuo_alt[prueba] = d_alt[prueba] - pred[:, 1]
    sin = error_en_cielo_arcmin(d_az, d_alt, alt)
    con = error_en_cielo_arcmin(residuo_az, residuo_alt, alt)
    p = wilcoxon(sin, con, alternative="greater").pvalue
    return Evaluacion(tipo, n, sin, con, p)

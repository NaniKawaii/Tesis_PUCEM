"""Modelo de error de apuntado de una montura altacimutal.

Este módulo es la **única** definición de los términos de error del proyecto. Lo usan:

- `simulador.py`, para **generar** el error de monturas sintéticas;
- `alineacion.py`, para **ajustar** los términos de sesión con 2 o 3 puntos reales;
- `analisis/`, para calcular la línea base clásica contra la que se compara la IA.

Tener una sola definición es deliberado: si el simulador y el ajuste usaran fórmulas
distintas, el experimento compararía dos cosas que no son la misma, y no habría forma de
notarlo desde los resultados.

Términos
--------
Son los del modelo clásico de una montura altacimutal. Se dividen en dos grupos según
cuándo cambian (ver `docs/08-diseno-definitivo.md` §3):

- **De sesión:** cambian cada vez que se arma el equipo. Se calibran al empezar la noche.
- **Persistentes:** son propiedades de *esta* montura. Se mantienen entre sesiones, y son
  los que tiene sentido aprender.

Convenciones
------------
- `az` y `alt` en **grados**; los errores, en **minutos de arco**.
- `d_az` es el error medido **sobre el eje de azimut**, no sobre el cielo. Cerca del cenit un
  mismo `d_az` se ve mucho más pequeño en el cielo: para la separación real usar
  `error_en_cielo_arcmin`.
- Los signos son una convención interna. No importa cuál se elija mientras el generador y el
  ajuste usen la misma, porque el ajuste absorbe el signo en el valor del parámetro.

Todos los términos son **lineales en sus parámetros**, así que el modelo clásico se ajusta
por mínimos cuadrados ordinarios (ver `ajustar`). Lo que la IA aprende es justamente lo que
este modelo lineal **no** puede representar.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Iterable, Sequence

import numpy as np

# Por encima de esta altitud, tan(alt) y sec(alt) se disparan y el modelo degenera.
# A la latitud de Portoviejo (~1° S) la Luna pasa muy cerca del cenit, así que este caso
# ocurre de verdad y no es una precaución teórica.
ALT_MAX_MODELO = 85.0

TERMINOS_SESION = ("indice_az", "indice_alt", "desnivel_ns", "desnivel_eo")

TERMINOS_PERSISTENTES = (
    "colimacion",
    "no_perpendicularidad",
    "flexion",
    "holgura_az",
    "holgura_alt",
    "deriva_az",
    "deriva_alt",
)

TERMINOS = TERMINOS_SESION + TERMINOS_PERSISTENTES

TEMPERATURA_REF = 25.0


@dataclass
class ParametrosError:
    """Términos del modelo de apuntado, en minutos de arco.

    `deriva_az` y `deriva_alt` van en minutos de arco por grado Celsius respecto de
    `TEMPERATURA_REF`.
    """

    # De sesión: cambian en cada montaje
    indice_az: float = 0.0
    indice_alt: float = 0.0
    desnivel_ns: float = 0.0
    desnivel_eo: float = 0.0
    # Persistentes: propiedades de esta montura
    colimacion: float = 0.0
    no_perpendicularidad: float = 0.0
    flexion: float = 0.0
    holgura_az: float = 0.0
    holgura_alt: float = 0.0
    deriva_az: float = 0.0
    deriva_alt: float = 0.0

    def a_vector(self, terminos: Sequence[str] = TERMINOS) -> np.ndarray:
        return np.array([getattr(self, t) for t in terminos], float)

    @classmethod
    def desde_vector(cls, valores: Iterable[float],
                     terminos: Sequence[str] = TERMINOS) -> "ParametrosError":
        p = cls()
        for nombre, valor in zip(terminos, valores):
            setattr(p, nombre, float(valor))
        return p

    def solo(self, terminos: Sequence[str]) -> "ParametrosError":
        """Copia con los demás términos puestos a cero."""
        p = ParametrosError()
        for t in terminos:
            setattr(p, t, getattr(self, t))
        return p


NOMBRES = tuple(f.name for f in fields(ParametrosError))
assert set(NOMBRES) == set(TERMINOS), "TERMINOS y ParametrosError deben coincidir"


def _preparar(az, alt, sentido_az, sentido_alt, temperatura):
    az = np.atleast_1d(np.asarray(az, float))
    alt = np.atleast_1d(np.asarray(alt, float))
    n = max(az.size, alt.size)
    az, alt = np.broadcast_to(az, (n,)), np.broadcast_to(alt, (n,))
    s_az = np.broadcast_to(np.atleast_1d(np.asarray(sentido_az, float)), (n,))
    s_alt = np.broadcast_to(np.atleast_1d(np.asarray(sentido_alt, float)), (n,))
    if temperatura is None:
        temp = np.full(n, TEMPERATURA_REF)
    else:
        temp = np.broadcast_to(np.atleast_1d(np.asarray(temperatura, float)), (n,))
    return az, alt, s_az, s_alt, temp


def columnas_diseno(az, alt, *, sentido_az=0.0, sentido_alt=0.0, temperatura=None,
                    alt_max=ALT_MAX_MODELO) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """Contribución de cada término a (d_az, d_alt), por unidad de parámetro.

    Es la base común del generador y del ajuste: `error_lineal` multiplica estas columnas
    por los parámetros, y `ajustar` las usa como matriz de diseño.

    `sentido_az` y `sentido_alt` valen +1, -1 o 0 según el sentido del último giro de cada
    eje (0 = desconocido o sin movimiento). Modelan la holgura como una histéresis.
    """
    az, alt, s_az, s_alt, temp = _preparar(az, alt, sentido_az, sentido_alt, temperatura)
    a = np.radians(az)
    # El recorte evita que tan() y sec() se disparen cerca del cenit.
    h = np.radians(np.clip(alt, -alt_max, alt_max))
    tan_h, sec_h = np.tan(h), 1.0 / np.cos(h)
    cero = np.zeros_like(a)
    dt = temp - TEMPERATURA_REF

    return {
        # --- de sesión ---
        "indice_az": (np.ones_like(a), cero),
        "indice_alt": (cero, np.ones_like(a)),
        "desnivel_ns": (-np.sin(a) * tan_h, -np.cos(a)),
        "desnivel_eo": (-np.cos(a) * tan_h, np.sin(a)),
        # --- persistentes ---
        "colimacion": (sec_h, cero),
        "no_perpendicularidad": (tan_h, cero),
        "flexion": (cero, -np.cos(h)),
        "holgura_az": (0.5 * s_az, cero),
        "holgura_alt": (cero, 0.5 * s_alt),
        "deriva_az": (dt, cero),
        "deriva_alt": (cero, dt),
    }


def error_lineal(az, alt, p: ParametrosError, *, sentido_az=0.0, sentido_alt=0.0,
                 temperatura=None, alt_max=ALT_MAX_MODELO) -> tuple[np.ndarray, np.ndarray]:
    """Error de apuntado que predice el modelo clásico, en minutos de arco.

    Devuelve (d_az, d_alt) **en coordenadas de eje**. Es lo que el modelo lineal puede
    representar; cualquier otra cosa que ocurra en la montura real queda como residuo, y es
    lo que aprende la IA.
    """
    cols = columnas_diseno(az, alt, sentido_az=sentido_az, sentido_alt=sentido_alt,
                           temperatura=temperatura, alt_max=alt_max)
    d_az = sum(getattr(p, t) * cols[t][0] for t in TERMINOS)
    d_alt = sum(getattr(p, t) * cols[t][1] for t in TERMINOS)
    return np.asarray(d_az, float), np.asarray(d_alt, float)


def matriz_diseno(az, alt, terminos: Sequence[str] = TERMINOS, *, sentido_az=0.0,
                  sentido_alt=0.0, temperatura=None,
                  alt_max=ALT_MAX_MODELO) -> np.ndarray:
    """Matriz de diseño apilada: filas de azimut encima de filas de altitud.

    Forma (2N, len(terminos)). Las primeras N filas corresponden a `d_az` y las siguientes
    N a `d_alt`, en el mismo orden que recibe `ajustar`.
    """
    cols = columnas_diseno(az, alt, sentido_az=sentido_az, sentido_alt=sentido_alt,
                           temperatura=temperatura, alt_max=alt_max)
    return np.column_stack([np.concatenate([cols[t][0], cols[t][1]]) for t in terminos])


@dataclass
class Ajuste:
    parametros: ParametrosError
    terminos: tuple[str, ...]
    residuo_az: np.ndarray  # minutos de arco, en coordenadas de eje
    residuo_alt: np.ndarray
    rms_antes: float  # separación en el cielo, minutos de arco
    rms_despues: float
    n: int

    @property
    def mejora(self) -> float:
        """Fracción del error en el cielo que explica el modelo clásico (0 a 1)."""
        if self.rms_antes <= 0:
            return 0.0
        return 1.0 - self.rms_despues / self.rms_antes


def ajustar(az, alt, d_az, d_alt, terminos: Sequence[str] = TERMINOS, *,
            sentido_az=0.0, sentido_alt=0.0, temperatura=None,
            alt_max=ALT_MAX_MODELO) -> Ajuste:
    """Ajusta los términos indicados por mínimos cuadrados.

    Con `terminos=TERMINOS_SESION` es la **alineación de sesión**: con 2 o 3 puntos se
    resuelven los cuatro términos que cambian en cada montaje.

    Con `terminos=TERMINOS` es la **línea base clásica** del artículo: el modelo contra el
    que se compara la corrección aprendida.
    """
    terminos = tuple(terminos)
    az = np.atleast_1d(np.asarray(az, float))
    alt = np.atleast_1d(np.asarray(alt, float))
    d_az = np.atleast_1d(np.asarray(d_az, float))
    d_alt = np.atleast_1d(np.asarray(d_alt, float))
    n = az.size
    if not (alt.size == d_az.size == d_alt.size == n):
        raise ValueError("az, alt, d_az y d_alt deben tener el mismo largo")
    if n * 2 < len(terminos):
        raise ValueError(
            f"Hacen falta al menos {-(-len(terminos) // 2)} puntos para ajustar "
            f"{len(terminos)} términos; se recibieron {n}")

    A = matriz_diseno(az, alt, terminos, sentido_az=sentido_az, sentido_alt=sentido_alt,
                      temperatura=temperatura, alt_max=alt_max)
    y = np.concatenate([d_az, d_alt])
    solucion, *_ = np.linalg.lstsq(A, y, rcond=None)

    p = ParametrosError.desde_vector(solucion, terminos)
    pred_az, pred_alt = error_lineal(az, alt, p, sentido_az=sentido_az,
                                     sentido_alt=sentido_alt, temperatura=temperatura,
                                     alt_max=alt_max)
    res_az, res_alt = d_az - pred_az, d_alt - pred_alt
    return Ajuste(
        parametros=p,
        terminos=terminos,
        residuo_az=res_az,
        residuo_alt=res_alt,
        rms_antes=rms_en_cielo(d_az, d_alt, alt),
        rms_despues=rms_en_cielo(res_az, res_alt, alt),
        n=n,
    )


def error_en_cielo_arcmin(d_az, d_alt, alt) -> np.ndarray:
    """Separación angular real en el cielo, en minutos de arco.

    Un error de azimut pesa menos cerca del cenit, por eso va multiplicado por cos(alt).
    Esta es la magnitud que se reporta en el artículo: es la que el observador ve.
    """
    d_az = np.asarray(d_az, float)
    d_alt = np.asarray(d_alt, float)
    return np.hypot(d_az * np.cos(np.radians(np.asarray(alt, float))), d_alt)


def rms_en_cielo(d_az, d_alt, alt) -> float:
    e = error_en_cielo_arcmin(d_az, d_alt, alt)
    return float(np.sqrt(np.mean(np.square(e)))) if e.size else 0.0


def sentido(anterior, actual) -> np.ndarray:
    """Signo del movimiento entre dos posiciones: +1, -1 o 0.

    Es el indicador que necesita el término de holgura.
    """
    return np.sign(np.asarray(actual, float) - np.asarray(anterior, float))

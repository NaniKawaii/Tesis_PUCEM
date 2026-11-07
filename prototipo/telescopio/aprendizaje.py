"""Corrección del error de apuntado aprendida: el pipeline del artículo.

Implementa lo que describe `docs/08-diseno-definitivo.md`: la IA aprende el **residuo** que
deja el modelo clásico, se valida **dejando una noche fuera**, y se comparan dos formas de
entrenar (solo datos reales, frente a preentrenamiento en simulación más ajuste fino).

Cadena de corrección
--------------------
Para cada fila: Skyfield da la posición, se le quita lo que explica el modelo clásico, y la
IA predice lo que queda.

    error medido
      = alineación de sesión        (se calibra al empezar la noche, no se aprende)
      + términos persistentes        (modelo clásico, compartido entre noches)
      + lo que prediga el corrector  (la IA)
      + residuo                      (lo que no se logra explicar)

La alineación de sesión va primero porque sus términos cambian en cada montaje: si se
entrenara sobre el error crudo, el modelo intentaría memorizar los desfases de una noche que
no sirven para otra, y la validación dejando una noche fuera dejaría de ser válida.

Lo que sí funciona, medido
--------------------------
El corrector aprendido sobre datos reales **vence al modelo clásico en 6 de 6 sorteos
independientes** (mediana 3,93′ → 3,50′; 4 de 6 con p < 0,05). Esa es la afirmación del
artículo. Se reproduce con:

    python -P analisis/e5_transferencia.py --sorteos 6 --sondeo 0 --monturas 2

El preentrenamiento no funciona: está apagado
---------------------------------------------
**Resultado negativo, medido el 07/11/2026.** Se probaron tres variantes y ninguna se sostiene:

1. **Transferencia por residuo, sin condicionar.** El modelo entrenado en simulación predice y
   su predicción se usa como desplazamiento fijo. No puede funcionar, y es una identidad, no
   una medición: dos monturas distintas apuntadas a las mismas posiciones producen las
   **mismas** entradas, así que el modelo predice lo mismo para las dos. Solo puede dar la
   media de la familia, y la media no es ninguna montura concreta. Ver
   `test_sin_sondeo_el_preentrenado_no_puede_distinguir_dos_monturas`.
2. **Condicionando con puntos de sondeo tomados del arco de la noche** (`con_sondeo`). La
   primera medición dio una mejora clara, p = 0,0078 con 8 noches, que es el mínimo posible.
   Al repetir el experimento con otras monturas de la **misma** distribución, el efecto se
   sostuvo en 4 de 6 sorteos y se dio la vuelta en 2. Era una semilla afortunada.
3. **Con los puntos de sondeo repartidos por el cielo** (`simulador.pointings_de_sondeo`), que
   es lo que se haría en campo. Peor todavía, por dos razones medidas: los pointings a altitud
   alta corrompen la alineación de la sesión, y reajustar los términos clásicos con 6 puntos
   está malísimamente condicionado (ver `sin_noches_reales`).

Por eso `preparar` **no sonda por defecto**. La maquinaria se conserva encendible porque el
resultado negativo es material de la Discusión y hay que poder reproducirlo, no porque se use.

Mecanismo de transferencia, cuando se enciende
----------------------------------------------
Se transfiere **por residuo**, igual para los tres modelos: la predicción del modelo entrenado
en simulación entra como desplazamiento fijo y el modelo ajustado con datos reales aprende lo
que queda. Que el mecanismo sea el mismo para todos es deliberado: si cada modelo usara su
propia forma de transferir (reinicio en caliente para la red, prior para Ridge, árboles
añadidos para el boosting), la comparación entre modelos mezclaría dos efectos.

Orden de las operaciones
------------------------
    cargar -> alinear_sesiones -> entrenar          (lo normal)
    cargar -> preparar(datos, k) -> entrenar        (con sondeo, para reproducir el negativo)

Si se sonda, va después de la alineación: mide el error que **queda** una vez quitados los
términos de sesión; sobre el error crudo mediría los desfases del montaje, que ya se calibran.

Sobre el boosting
-----------------
Se usa `HistGradientBoostingRegressor` de scikit-learn, que implementa el mismo algoritmo de
gradient boosting por histogramas que LightGBM y ya es dependencia del proyecto. Evita añadir
una dependencia más que además hay que compilar en la Raspberry Pi. Al citarlo en el artículo
conviene decir eso mismo: boosting por histogramas, citando a scikit-learn y el artículo de
LightGBM para el algoritmo.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Callable, Iterable, Sequence

import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from .errores import (
    ALT_MAX_MODELO,
    TERMINOS_PERSISTENTES,
    TERMINOS_SESION,
    ParametrosError,
    ajustar,
    error_lineal,
    rms_en_cielo,
)

TIPOS = ("clasico", "ridge", "boosting", "mlp")

# Puntos de alineación al empezar la sesión. En campo son 2 o 3 objetos conocidos, repartidos
# por el cielo; aquí se toman repartidos a lo largo de la sesión, que es el equivalente.
PUNTOS_ALINEACION = 3

# Puntos de sondeo con los que se condiciona el modelo. Son medidas adicionales a las de la
# alineación: en campo, apuntar a 6 objetos conocidos más y anotar el error que queda. Cada
# punto aporta 4 números (az, alt, d_az, d_alt), así que 6 puntos son 24 entradas extra.
PUNTOS_SONDEO = 6

# Valores críticos de la prueba de Nemenyi (Demšar, 2006), para alfa = 0,05 y 0,10.
_Q_NEMENYI = {
    0.05: {2: 1.960, 3: 2.343, 4: 2.569, 5: 2.728, 6: 2.850,
           7: 2.949, 8: 3.031, 9: 3.102, 10: 3.164},
    0.10: {2: 1.645, 3: 2.052, 4: 2.291, 5: 2.459, 6: 2.589,
           7: 2.693, 8: 2.780, 9: 2.855, 10: 2.920},
}


# --------------------------------------------------------------------------- datos


@dataclass
class Datos:
    """Las columnas que necesita el pipeline, ya en arreglos numéricos."""

    sesion: np.ndarray
    az: np.ndarray
    alt: np.ndarray
    d_az: np.ndarray  # minutos de arco, coordenadas de eje
    d_alt: np.ndarray
    sentido_az: np.ndarray
    sentido_alt: np.ndarray
    temperatura: np.ndarray
    inclinacion_ns: np.ndarray
    inclinacion_eo: np.ndarray

    # (n, 4 * puntos). El error medido en los puntos de sondeo de la sesión de cada fila,
    # repetido en todas sus filas. None mientras no se haya sondeado. Lo pone `con_sondeo`.
    sondeo: np.ndarray | None = None
    # (n,) booleano: qué filas **son** los puntos de sondeo. Lo pone `con_sondeo`.
    es_sondeo: np.ndarray | None = None

    def __len__(self) -> int:
        return int(self.az.size)

    @property
    def sesiones(self) -> list[str]:
        vistas: dict[str, None] = {}
        for s in self.sesion:
            vistas.setdefault(str(s), None)
        return list(vistas)

    def submuestra(self, mascara: np.ndarray) -> "Datos":
        return Datos(**{k: (None if v is None else v[mascara])
                        for k, v in self.__dict__.items()})

    @property
    def puntos_sondeo(self) -> int:
        return 0 if self.sondeo is None else self.sondeo.shape[1] // 4

    def observaciones(self) -> "Datos":
        """Quita las filas de sondeo. Son medidas de calibración, no observaciones.

        Hay que quitarlas de todo: del entrenamiento y **también de la evaluación**. Medido el
        07/11/2026: dejarlas dentro multiplicaba por tres el RMS de todas las condiciones,
        porque los pointings de sondeo van a altitudes altas donde el factor `tan(h)` del
        desnivel es casi diez veces el del arco de seguimiento. Seis filas de 486 dominaban la
        medición entera.
        """
        if self.es_sondeo is None or not self.es_sondeo.any():
            return self
        return self.submuestra(~self.es_sondeo)

    def valores_de_sondeo(self, sesion: str) -> tuple[np.ndarray, ...]:
        """Los `(az, alt, d_az, d_alt)` de los puntos de sondeo de una sesión.

        Salen del propio vector de características, así que siguen disponibles aunque las
        filas de sondeo ya se hayan quitado con `observaciones`.
        """
        if self.sondeo is None:
            raise ValueError("Estos datos no traen sondeo")
        filas = _filas_de(self, sesion)
        if filas.size == 0:
            raise ValueError(f"No hay filas de la sesión {sesion!r}")
        k = self.puntos_sondeo
        v = self.sondeo[filas[0]]
        return v[:k], v[k:2 * k], v[2 * k:3 * k], v[3 * k:]

    def de_sesiones(self, nombres: Iterable[str]) -> "Datos":
        quiero = set(map(str, nombres))
        return self.submuestra(np.array([str(s) in quiero for s in self.sesion]))

    def con_errores(self, d_az: np.ndarray, d_alt: np.ndarray) -> "Datos":
        return replace(self, d_az=np.asarray(d_az, float), d_alt=np.asarray(d_alt, float))

    @property
    def rms(self) -> float:
        return rms_en_cielo(self.d_az, self.d_alt, self.alt)


_COLUMNAS = {
    "sesion": ("sesion", str),
    "az": ("az_comandado", float),
    "alt": ("alt_comandado", float),
    "d_az": ("d_az", float),
    "d_alt": ("d_alt", float),
    "sentido_az": ("sentido_az", float),
    "sentido_alt": ("sentido_alt", float),
    "temperatura": ("temperatura_c", float),
    "inclinacion_ns": ("inclinacion_ns", float),
    "inclinacion_eo": ("inclinacion_eo", float),
}


def cargar(ruta: str | Path, calidad_minima: float = 0.0) -> Datos:
    """Lee un CSV con el esquema de seguimiento (`registro.RegistroSeguimiento`)."""
    with Path(ruta).open(encoding="utf-8") as f:
        filas = [fila for fila in csv.DictReader(f)
                 if float(fila.get("calidad", 1.0)) >= calidad_minima]
    if not filas:
        raise ValueError(f"No hay filas utilizables en {ruta}")
    campos = {}
    for destino, (origen, tipo) in _COLUMNAS.items():
        if origen not in filas[0]:
            raise ValueError(f"Falta la columna '{origen}' en {ruta}")
        campos[destino] = np.array([tipo(fila[origen]) for fila in filas],
                                   dtype=object if tipo is str else float)
    return Datos(**campos)


# ------------------------------------------------------- alineación y sondeo


def _indices_repartidos(n: int, puntos: int, margen: float = 0.0) -> np.ndarray:
    """`puntos` índices repartidos entre 0 y n-1, repitiendo si la sesión es más corta.

    `margen` encoge el intervalo por los dos extremos. Sirve para que los puntos de sondeo no
    caigan exactamente sobre los de la alineación: en campo son pointings distintos.
    """
    if n <= 0 or puntos <= 0:
        return np.zeros(0, int)
    bajo, alto = margen * (n - 1), (1.0 - margen) * (n - 1)
    return np.clip(np.round(np.linspace(bajo, alto, puntos)), 0, n - 1).astype(int)


def _filas_de(datos: Datos, nombre: str) -> np.ndarray:
    return np.flatnonzero(np.array([str(s) == nombre for s in datos.sesion]))


def con_sondeo(datos: Datos, puntos: int = PUNTOS_SONDEO,
               desde: str = "primeras") -> Datos:
    """Añade a cada fila el error medido en los puntos de sondeo de **su** sesión.

    Es la pieza que hace transferible el preentrenamiento: sin ella el modelo no puede saber a
    qué montura se enfrenta y solo predice la media de la familia (ver el encabezado del
    módulo). Cada punto aporta su posición y su error, `(az, alt, d_az, d_alt)`, porque un
    patrón de error solo significa algo junto con el lugar del cielo donde se midió.

    Hay que llamarla sobre datos **ya alineados por sesión**: el sondeo mide lo que queda tras
    la alineación, no los desfases del montaje.

    `desde` dice de dónde salen los puntos:

    - `"primeras"` (por defecto): las primeras filas de cada sesión. Es el protocolo real, en
      el que el sondeo se hace **antes** de empezar a seguir, apuntando a objetos conocidos
      repartidos por todo el cielo (`simulador.pointings_de_sondeo`).
    - `"reparto"`: repartidas a lo largo de la sesión. Solo para datos que no traen un sondeo
      propio. **Mide peor**: los puntos caen todos sobre el arco de la noche, unos 80° de
      azimut, y sobre un arco corto los términos del error no se distinguen entre sí. Medido
      el 07/11/2026; es lo que hundía el primer intento de condicionamiento.

    Ojo con el orden de los experimentos: el sondeo usa filas de la propia sesión de prueba, y
    eso es legítimo porque en campo esas medidas se toman antes de observar, igual que la
    alineación. Lo que no sería legítimo es dárselo solo a una de las estrategias.
    """
    if puntos <= 0:
        return replace(datos, sondeo=None, es_sondeo=None)
    if desde not in ("primeras", "reparto"):
        raise ValueError(f"`desde` debe ser 'primeras' o 'reparto', no {desde!r}")

    sondeo = np.zeros((len(datos), 4 * puntos))
    es_sondeo = np.zeros(len(datos), bool)
    for nombre in datos.sesiones:
        filas = _filas_de(datos, nombre)
        if filas.size == 0:
            continue
        if desde == "primeras":
            sel = filas[np.minimum(np.arange(puntos), filas.size - 1)]
        else:
            sel = filas[_indices_repartidos(filas.size, puntos, margen=0.1)]
        sondeo[filas] = np.concatenate([datos.az[sel], datos.alt[sel],
                                        datos.d_az[sel], datos.d_alt[sel]])
        es_sondeo[np.unique(sel)] = True
    return replace(datos, sondeo=sondeo, es_sondeo=es_sondeo)


def preparar(datos: Datos, puntos_sondeo: int = 0,
             desde: str = "primeras") -> tuple[Datos, dict[str, ParametrosError]]:
    """Alinea, sonda y quita las filas de sondeo. Es la entrada normal al pipeline.

    El último paso no es cosmético: ver `Datos.observaciones`. Los valores del sondeo siguen
    disponibles como características y por `Datos.valores_de_sondeo`.
    """
    alineados, ajustes = alinear_sesiones(datos)
    return con_sondeo(alineados, puntos_sondeo, desde).observaciones(), ajustes


def alinear_sesiones(datos: Datos, puntos: int = PUNTOS_ALINEACION
                     ) -> tuple[Datos, dict[str, ParametrosError]]:
    """Quita de cada sesión sus términos de sesión, como hace la alineación en campo.

    Devuelve los datos ya alineados y los parámetros ajustados de cada sesión.

    Los puntos de calibración se toman repartidos a lo largo de la sesión, que equivale a
    alinear sobre 2 o 3 objetos separados en el cielo al empezar la noche. En el protocolo
    real esos puntos se obtienen apuntando a objetos conocidos, no de la propia trayectoria:
    es una diferencia menor, porque estos términos no dependen de la dirección, pero conviene
    declararla en la Discusión.
    """
    d_az = datos.d_az.copy()
    d_alt = datos.d_alt.copy()
    ajustes: dict[str, ParametrosError] = {}

    for nombre in datos.sesiones:
        indices = _filas_de(datos, nombre)
        if indices.size < 2:
            continue
        cal = indices[np.unique(_indices_repartidos(indices.size, puntos))]
        aj = ajustar(datos.az[cal], datos.alt[cal], datos.d_az[cal], datos.d_alt[cal],
                     TERMINOS_SESION)
        pred_az, pred_alt = error_lineal(datos.az[indices], datos.alt[indices], aj.parametros)
        d_az[indices] -= pred_az
        d_alt[indices] -= pred_alt
        ajustes[nombre] = aj.parametros

    return datos.con_errores(d_az, d_alt), ajustes


# ------------------------------------------------------------------- modelos


def caracteristicas(datos: Datos) -> np.ndarray:
    """Entradas del corrector.

    A propósito **no** incluye nada derivado de la reducción de las poleas: el error periódico
    de excentricidad tiene que salir de los datos, no de pistas puestas a mano. Tampoco
    incluye la fase lunar, que no influye en el apuntado y solo invitaría a correlaciones
    espurias con la noche.

    Si los datos vienen sondeados (`con_sondeo`), añade al final las entradas del sondeo. Son
    las que identifican la montura y hacen transferible el preentrenamiento.
    """
    a = np.radians(datos.az)
    h = np.radians(np.clip(datos.alt, -ALT_MAX_MODELO, ALT_MAX_MODELO))
    base = np.column_stack([
        datos.az, datos.alt,
        np.sin(a), np.cos(a), np.sin(2 * a), np.cos(2 * a),
        np.sin(h), np.cos(h), np.tan(h),
        datos.sentido_az, datos.sentido_alt,
        datos.temperatura - 25.0,
        datos.inclinacion_ns, datos.inclinacion_eo,
    ])
    if datos.sondeo is None:
        return base
    return np.hstack([base, datos.sondeo])


def _estimador(tipo: str, semilla: int = 0):
    if tipo == "ridge":
        return make_pipeline(StandardScaler(), Ridge(alpha=1.0))
    if tipo == "boosting":
        return HistGradientBoostingRegressor(
            max_iter=250, learning_rate=0.06, max_depth=6,
            min_samples_leaf=40, l2_regularization=1.0, random_state=semilla)
    if tipo == "mlp":
        return make_pipeline(StandardScaler(), MLPRegressor(
            hidden_layer_sizes=(64, 32), activation="tanh", solver="adam",
            alpha=1e-3, max_iter=600, early_stopping=True, n_iter_no_change=20,
            random_state=semilla))
    raise ValueError(f"Tipo desconocido: {tipo}. Use uno de {TIPOS}")


class _DosSalidas:
    """Un estimador por eje. Uniforma el trato de los tres modelos."""

    def __init__(self, tipo: str, semilla: int = 0):
        self.az = _estimador(tipo, semilla)
        self.alt = _estimador(tipo, semilla + 1)

    def fit(self, X, y_az, y_alt) -> "_DosSalidas":
        self.az.fit(X, y_az)
        self.alt.fit(X, y_alt)
        return self

    def predict(self, X) -> tuple[np.ndarray, np.ndarray]:
        return np.asarray(self.az.predict(X), float), np.asarray(self.alt.predict(X), float)


@dataclass
class Corrector:
    """Corrección completa: términos persistentes + desplazamiento preentrenado + IA."""

    tipo: str
    persistentes: ParametrosError
    modelo: _DosSalidas | None = None
    offset: Callable[[np.ndarray], tuple[np.ndarray, np.ndarray]] | None = None
    n_sesiones: int = 0
    ancho: int = 0  # columnas de entrada con las que se entrenó, para detectar desajustes

    def predecir(self, datos: Datos) -> tuple[np.ndarray, np.ndarray]:
        d_az, d_alt = error_lineal(datos.az, datos.alt, self.persistentes,
                                   sentido_az=datos.sentido_az,
                                   sentido_alt=datos.sentido_alt,
                                   temperatura=datos.temperatura)
        if self.offset is not None or self.modelo is not None:
            X = caracteristicas(datos)
            if self.offset is not None:
                o_az, o_alt = self.offset(X)
                d_az, d_alt = d_az + o_az, d_alt + o_alt
            if self.modelo is not None:
                m_az, m_alt = self.modelo.predict(X)
                d_az, d_alt = d_az + m_az, d_alt + m_alt
        return d_az, d_alt

    def residuo(self, datos: Datos) -> Datos:
        """Lo que queda sin explicar. Es lo que se mide para comparar modelos."""
        p_az, p_alt = self.predecir(datos)
        return datos.con_errores(datos.d_az - p_az, datos.d_alt - p_alt)

    def predecir_ml(self, X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Solo la parte aprendida. Es lo que se transfiere al ajuste fino."""
        ceros = np.zeros(X.shape[0])
        az, alt = ceros, ceros
        if self.offset is not None:
            o_az, o_alt = self.offset(X)
            az, alt = az + o_az, alt + o_alt
        if self.modelo is not None:
            m_az, m_alt = self.modelo.predict(X)
            az, alt = az + m_az, alt + m_alt
        return az, alt


def entrenar(datos: Datos, tipo: str, *, previo: Corrector | None = None,
             semilla: int = 0) -> Corrector:
    """Entrena un corrector sobre datos **ya alineados por sesión**.

    Con `previo`, la parte aprendida de ese corrector entra como desplazamiento fijo y el
    modelo nuevo aprende solo lo que queda: es el ajuste fino de la estrategia B.
    """
    if tipo not in TIPOS:
        raise ValueError(f"Tipo desconocido: {tipo}. Use uno de {TIPOS}")

    X = caracteristicas(datos)
    if previo is not None and previo.ancho and previo.ancho != X.shape[1]:
        raise ValueError(
            f"El corrector previo se entrenó con {previo.ancho} entradas y estos datos tienen "
            f"{X.shape[1]}. Los dos tienen que venir del mismo numero de puntos de sondeo: "
            f"use `con_sondeo` con el mismo valor en los sinteticos y en los reales.")

    offset = previo.predecir_ml if previo is not None else None

    # 1. Términos persistentes del modelo clásico, con los datos reales disponibles.
    aj = ajustar(datos.az, datos.alt, datos.d_az, datos.d_alt, TERMINOS_PERSISTENTES,
                 sentido_az=datos.sentido_az, sentido_alt=datos.sentido_alt,
                 temperatura=datos.temperatura)
    base = Corrector(tipo, aj.parametros, None, offset, len(datos.sesiones), X.shape[1])
    if tipo == "clasico":
        return base

    # 2. La IA aprende lo que queda después de lo clásico y del desplazamiento.
    resto = base.residuo(datos)
    modelo = _DosSalidas(tipo, semilla).fit(X, resto.d_az, resto.d_alt)
    return replace(base, modelo=modelo)


# --------------------------------------------------------- validación por noche


@dataclass
class Resultado:
    """RMS en el cielo por noche de prueba, para un modelo y una estrategia."""

    tipo: str
    estrategia: str  # "real" o "simulacion"
    por_sesion: dict[str, float]
    n_entrenamiento: int

    @property
    def rms(self) -> float:
        valores = np.array(list(self.por_sesion.values()), float)
        return float(np.sqrt(np.mean(valores ** 2))) if valores.size else float("nan")


def dejando_una_noche_fuera(datos: Datos, tipo: str, *, previo: Corrector | None = None,
                            semilla: int = 0) -> Resultado:
    """Entrena con todas las noches menos una y evalúa en la que quedó fuera.

    Nunca se parten las filas al azar: dos filas del mismo minuto son casi la misma
    observación, y mezclarlas entre entrenamiento y prueba infla el resultado.
    """
    nombres = datos.sesiones
    if len(nombres) < 2:
        raise ValueError("Hacen falta al menos 2 sesiones para dejar una fuera")

    por_sesion: dict[str, float] = {}
    for fuera in nombres:
        entrena = datos.de_sesiones([n for n in nombres if n != fuera])
        prueba = datos.de_sesiones([fuera])
        corrector = entrenar(entrena, tipo, previo=previo, semilla=semilla)
        por_sesion[fuera] = corrector.residuo(prueba).rms

    estrategia = "simulacion" if previo is not None else "real"
    return Resultado(tipo, estrategia, por_sesion, len(nombres) - 1)


def sin_noches_reales(datos: Datos, previo: Corrector, *,
                      clasico_del_sondeo: bool = False) -> Resultado:
    """Evalúa un corrector preentrenado en simulación sobre cada noche, sin ajuste fino.

    Es la condición que solo existe gracias al condicionamiento por sondeo: el modelo no ha
    visto nunca esta montura y lo único que sabe de ella son sus puntos de sondeo. Devuelve un
    `Resultado` con el mismo formato que `dejando_una_noche_fuera`, para poder compararlos
    noche a noche con `wilcoxon_pareado`.

    Los términos persistentes del modelo clásico se heredan del corrector preentrenado, o sea
    de la familia sintética. Eso es volver a usar la media de la familia para la parte
    clásica, y es una debilidad declarada de esta condición.

    `clasico_del_sondeo=True` prueba la alternativa: reajustarlos con los puntos de sondeo de
    esa noche. **No funciona, y queda para poder reproducir el hallazgo.** Medido el
    07/11/2026 con 6 puntos repartidos por el cielo: el RMS sube a 105′ de mediana sobre un
    error crudo de 80′, peor que no corregir nada. La razón es el condicionamiento, no el
    rango: con 6 puntos, `sec(h)` (colimación) y `tan(h)` (no perpendicularidad) son casi
    colineales, `lstsq` devuelve coeficientes enormes que se cancelan entre sí en los propios
    puntos, y al extrapolarlos al arco de seguimiento el error explota. Que haya 12 ecuaciones
    para 7 incógnitas dice que el sistema tiene rango, no que esté bien condicionado.
    """
    if datos.puntos_sondeo == 0:
        raise ValueError(
            "Sin sondeo esta condicion no tiene sentido: el modelo no puede saber a que "
            "montura se enfrenta. Use `con_sondeo` antes.")

    por_sesion = {}
    for s in datos.sesiones:
        noche = datos.de_sesiones([s]).observaciones()
        corrector = previo
        if clasico_del_sondeo:
            p_az, p_alt, p_daz, p_dalt = datos.valores_de_sondeo(s)
            # Desde pointings estáticos no se puede medir la holgura (hace falta invertir el
            # sentido de giro), así que esas columnas quedan en cero y `lstsq` las anula.
            aj = ajustar(p_az, p_alt, p_daz, p_dalt, TERMINOS_PERSISTENTES,
                         sentido_az=np.zeros_like(p_az), sentido_alt=np.zeros_like(p_az),
                         temperatura=np.full_like(p_az, float(np.mean(noche.temperatura))))
            corrector = replace(previo, persistentes=aj.parametros)
        por_sesion[s] = corrector.residuo(noche).rms
    return Resultado(previo.tipo, "simulacion", por_sesion, 0)


def comparar_modelos(datos: Datos, tipos: Sequence[str] = TIPOS, *,
                     previo_por_tipo: dict[str, Corrector] | None = None,
                     semilla: int = 0) -> dict[str, Resultado]:
    return {t: dejando_una_noche_fuera(
        datos, t, previo=(previo_por_tipo or {}).get(t), semilla=semilla) for t in tipos}


# ------------------------------------------------------- curva de aprendizaje (E4)


@dataclass
class PuntoCurva:
    n_noches: int
    estrategia: str
    rms_por_prueba: list[float]

    @property
    def rms(self) -> float:
        v = np.array(self.rms_por_prueba, float)
        return float(np.sqrt(np.mean(v ** 2))) if v.size else float("nan")


def curva_de_aprendizaje(reales: Datos, tipo: str, *, sinteticos: Datos | None = None,
                         n_noches: Sequence[int] | None = None, repeticiones: int = 5,
                         semilla: int = 0) -> list[PuntoCurva]:
    """El experimento E4: error frente al número de noches reales de entrenamiento.

    Con `sinteticos` entrega además la curva de la estrategia B (preentrenar y ajustar). La
    diferencia entre las dos curvas es el aporte del artículo: cuántas noches se ahorran.

    `reales` tiene que venir de `preparar` (alineado y sondeado). Los `sinteticos` se preparan
    aquí dentro, con el mismo número de puntos de sondeo que traigan los reales.

    `n_noches` admite **0** cuando hay `sinteticos`: es el caso que solo existe gracias al
    condicionamiento por sondeo, apuntar con un modelo entrenado únicamente en simulación más
    los puntos de sondeo de la montura. La estrategia A no tiene ese punto: sin noches reales
    no hay nada con que entrenar.
    """
    nombres = reales.sesiones
    if len(nombres) < 3:
        raise ValueError("Hacen falta al menos 3 sesiones para trazar la curva")
    n_noches = n_noches or list(range(1, len(nombres)))

    previo = None
    if sinteticos is not None and tipo != "clasico":
        alineados, _ = alinear_sesiones(sinteticos)
        previo = entrenar(con_sondeo(alineados, reales.puntos_sondeo), tipo, semilla=semilla)

    rng = np.random.default_rng(semilla)
    puntos: list[PuntoCurva] = []

    for n in n_noches:
        if n == 0:
            # Sin noches reales no hay ajuste fino: se evalúa el preentrenado tal cual, sobre
            # todas las noches. No hay contrapartida en la estrategia A.
            if previo is not None:
                puntos.append(PuntoCurva(0, "simulacion", [previo.residuo(reales).rms]))
            continue
        if n >= len(nombres):
            continue
        acumulado: dict[str, list[float]] = {"real": [], "simulacion": []}
        for _ in range(repeticiones):
            orden = list(rng.permutation(nombres))
            entrena = reales.de_sesiones(orden[:n])
            prueba = reales.de_sesiones(orden[n:])
            if len(entrena.sesiones) < 1:
                continue
            acumulado["real"].append(
                entrenar(entrena, tipo, semilla=semilla).residuo(prueba).rms)
            if previo is not None:
                acumulado["simulacion"].append(
                    entrenar(entrena, tipo, previo=previo, semilla=semilla).residuo(prueba).rms)
        for estrategia, valores in acumulado.items():
            if valores:
                puntos.append(PuntoCurva(n, estrategia, valores))

    return puntos


def noches_para_umbral(puntos: Sequence[PuntoCurva], umbral_arcmin: float,
                       estrategia: str) -> int | None:
    """Primera cantidad de noches con la que la curva baja del umbral. None si no lo cruza."""
    candidatos = sorted((p for p in puntos if p.estrategia == estrategia),
                        key=lambda p: p.n_noches)
    for p in candidatos:
        if p.rms <= umbral_arcmin:
            return p.n_noches
    return None


# --------------------------------------------------------------------- estadística


@dataclass
class Friedman:
    estadistico: float
    p: float
    rangos_medios: dict[str, float]
    diferencia_critica: float
    n_bloques: int
    alfa: float

    def separados(self, a: str, b: str) -> bool:
        """¿La diferencia entre dos modelos supera la diferencia crítica de Nemenyi?"""
        return abs(self.rangos_medios[a] - self.rangos_medios[b]) > self.diferencia_critica

    @property
    def mejor(self) -> str:
        return min(self.rangos_medios, key=self.rangos_medios.get)


def friedman_nemenyi(resultados: dict[str, Resultado], alfa: float = 0.05) -> Friedman:
    """Compara modelos sobre las mismas noches: Friedman y luego Nemenyi.

    Cada noche es un bloque. Se usa esta prueba, y no una t de Student, porque compara más de
    dos modelos sobre los mismos bloques y no supone normalidad.
    """
    from scipy.stats import friedmanchisquare

    tipos = list(resultados)
    if len(tipos) < 2:
        raise ValueError("Hacen falta al menos 2 modelos para comparar")
    comunes = sorted(set.intersection(*(set(r.por_sesion) for r in resultados.values())))
    if len(comunes) < 2:
        raise ValueError("Los modelos no comparten suficientes noches")

    matriz = np.array([[resultados[t].por_sesion[s] for t in tipos] for s in comunes], float)
    # Rango 1 = el mejor (menor error) en cada noche.
    rangos = np.apply_along_axis(
        lambda fila: np.argsort(np.argsort(fila)) + 1.0, 1, matriz)

    if len(tipos) >= 3:
        estadistico, p = friedmanchisquare(*matriz.T)
    else:
        from scipy.stats import wilcoxon
        estadistico, p = wilcoxon(matriz[:, 0], matriz[:, 1])

    k, n = len(tipos), len(comunes)
    q = _Q_NEMENYI.get(alfa, _Q_NEMENYI[0.05]).get(k)
    dc = float(q * np.sqrt(k * (k + 1) / (6.0 * n))) if q else float("nan")

    return Friedman(float(estadistico), float(p),
                    {t: float(m) for t, m in zip(tipos, rangos.mean(axis=0))},
                    dc, n, alfa)


def wilcoxon_pareado(a: Resultado, b: Resultado) -> tuple[float, float]:
    """Compara dos condiciones noche a noche. Es la prueba de E4 y E5.

    Con 5 noches el valor de p más bajo posible a dos colas es 0,0625: la prueba no puede
    dar significancia aunque las cinco apunten en la misma dirección. El piso son 6 noches.
    """
    from scipy.stats import wilcoxon

    comunes = sorted(set(a.por_sesion) & set(b.por_sesion))
    if len(comunes) < 2:
        raise ValueError("Hacen falta al menos 2 noches en común")
    x = np.array([a.por_sesion[s] for s in comunes], float)
    y = np.array([b.por_sesion[s] for s in comunes], float)
    if np.allclose(x, y):
        return 0.0, 1.0
    estadistico, p = wilcoxon(x, y)
    return float(estadistico), float(p)


def p_minimo_alcanzable(n_noches: int) -> float:
    """Valor de p más bajo que puede dar un Wilcoxon pareado con n noches, a dos colas.

    Sirve para comprobar antes de medir que el diseño puede dar significancia.
    """
    if n_noches < 1:
        return 1.0
    return min(1.0, 2.0 / (2.0 ** n_noches))

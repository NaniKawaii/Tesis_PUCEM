"""Simulador de montura con aleatorización de dominio.

Genera noches sintéticas de seguimiento para **preentrenar** el corrector de apuntado antes
de tener datos reales (ver `docs/08-diseno-definitivo.md` §4).

Qué hace y qué no
-----------------
El simulador **no aprende ni simula el cielo**: las posiciones verdaderas salen de Skyfield,
igual que en el sistema real. Lo que simula es el **error de la montura**.

Aleatorización de dominio
-------------------------
Cada montura sintética se construye con un vector de parámetros muestreado al azar dentro de
rangos declarados (`RANGOS`). Entrenando sobre muchas monturas, el modelo no aprende *una*
montura: aprende qué forma tienen las funciones de error de apuntado en general. Después, con
la montura real, solo tiene que averiguar cuál miembro de esa familia es.

Por qué el simulador es más rico que el modelo clásico
------------------------------------------------------
Esto es deliberado y es lo más importante del módulo. Si el simulador generara exactamente
los términos de `errores.py`, un ajuste lineal los recuperaría perfectos y la IA no tendría
**nada** que aprender: el resultado "la IA mejora al modelo clásico" sería un artefacto del
simulador, no un hallazgo. Sería razonamiento circular, y un revisor lo detectaría.

Por eso `ParametrosNoLineales` añade efectos que el modelo lineal **no puede representar** y
que existen de verdad en una montura impresa:

- error periódico de las poleas y la correa (excentricidad), con período de una vuelta de polea;
- flexión que no es exactamente proporcional a cos(alt);
- holgura cuya amplitud cambia con la altitud, porque cambia el par que soporta el eje;
- cuantización por micropaso (diente de sierra);
- deriva térmica con un término cuadrático;
- ruido de medida y una deriva lenta propia de cada noche.

Advertencia sobre los rangos
----------------------------
Los valores de `RANGOS` son **estimaciones iniciales** derivadas de la geometría de la montura
(tolerancia de impresión, holgura típica de una correa GT2, precisión con la que se nivela un
trípode a ojo). Con la primera noche real hay que comprobar que la montura cae dentro de los
rangos muestreados y, si no, ampliarlos. Esa comprobación es la validación del simulador y es
un resultado del artículo por derecho propio.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Sequence

import numpy as np

from .errores import (
    TERMINOS_PERSISTENTES,
    TERMINOS_SESION,
    ParametrosError,
    error_en_cielo_arcmin,
    error_lineal,
)
from .registro import RegistroSeguimiento, guardar_seguimiento

# Resolución por micropaso, en minutos de arco, con las reducciones de docs/03
# (14:1 en azimut y 5:1 en altitud, 200 pasos por vuelta y 16 micropasos).
RESOLUCION_AZ_ARCMIN = 0.48
RESOLUCION_ALT_ARCMIN = 1.35

# Luna nueva de referencia y mes sinódico, para la fase aproximada.
_LUNA_NUEVA_REF = datetime(2000, 1, 6, 18, 14, tzinfo=timezone.utc)
_MES_SINODICO_DIAS = 29.530588853


@dataclass
class ParametrosNoLineales:
    """Efectos que el modelo clásico de `errores.py` no puede representar.

    Todos en minutos de arco, salvo donde se indica.
    """

    periodico_az: float = 0.0  # amplitud de la excentricidad de la polea de azimut
    fase_periodico_az: float = 0.0  # radianes
    periodico_alt: float = 0.0
    fase_periodico_alt: float = 0.0
    flexion_cuadratica: float = 0.0  # término en cos(alt)^2, que el modelo lineal no tiene
    holgura_alt_con_carga: float = 0.0  # la holgura crece al bajar la altitud
    deriva_cuadratica: float = 0.0  # minutos de arco por grado Celsius al cuadrado
    ruido_arcmin: float = 0.5  # desviación estándar del ruido de medida
    deriva_noche_arcmin: float = 0.0  # amplitud de la deriva lenta de cada noche


@dataclass
class MonturaSintetica:
    """Una montura concreta: lo que **no** cambia entre sesiones."""

    identificador: str
    persistentes: ParametrosError  # solo los términos de TERMINOS_PERSISTENTES
    no_lineales: ParametrosNoLineales
    reduccion_az: float = 14.0
    reduccion_alt: float = 5.0

    def a_dict(self) -> dict:
        d = {"montura": self.identificador,
             "reduccion_az": self.reduccion_az,
             "reduccion_alt": self.reduccion_alt}
        d.update({f"p_{k}": v for k, v in asdict(self.persistentes).items()
                  if k in TERMINOS_PERSISTENTES})
        d.update({f"nl_{k}": v for k, v in asdict(self.no_lineales).items()})
        return d


# Rangos de aleatorización: (mínimo, máximo). Ver la advertencia del encabezado.
RANGOS: dict[str, tuple[float, float]] = {
    # --- de sesión (se remuestrean en cada noche) ---
    "indice_az": (-120.0, 120.0),  # la referencia inicial puede estar a un par de grados
    "indice_alt": (-60.0, 60.0),
    "desnivel_ns": (-60.0, 60.0),  # nivelar un trípode a ojo deja ~1°
    "desnivel_eo": (-60.0, 60.0),
    # --- persistentes (propios de cada montura) ---
    "colimacion": (-30.0, 30.0),
    "no_perpendicularidad": (-30.0, 30.0),
    "flexion": (0.0, 20.0),  # PETG cargado con dos motores de ~1 kg
    "holgura_az": (0.0, 8.0),  # correa GT2 más polea impresa
    "holgura_alt": (0.0, 10.0),
    "deriva_az": (-0.5, 0.5),  # minutos de arco por grado Celsius
    "deriva_alt": (-0.5, 0.5),
    # --- no lineales ---
    "periodico_az": (0.0, 6.0),
    "periodico_alt": (0.0, 4.0),
    "flexion_cuadratica": (-8.0, 8.0),
    "holgura_alt_con_carga": (0.0, 4.0),
    "deriva_cuadratica": (-0.02, 0.02),
    "ruido_arcmin": (0.3, 1.5),
    "deriva_noche_arcmin": (0.0, 2.0),
}


def _u(rng: np.random.Generator, nombre: str) -> float:
    bajo, alto = RANGOS[nombre]
    return float(rng.uniform(bajo, alto))


def muestrear_montura(rng: np.random.Generator, identificador: str) -> MonturaSintetica:
    """Una montura sintética: términos persistentes y no lineales al azar."""
    persistentes = ParametrosError()
    for nombre in TERMINOS_PERSISTENTES:
        setattr(persistentes, nombre, _u(rng, nombre))
    no_lineales = ParametrosNoLineales(
        periodico_az=_u(rng, "periodico_az"),
        fase_periodico_az=float(rng.uniform(0, 2 * np.pi)),
        periodico_alt=_u(rng, "periodico_alt"),
        fase_periodico_alt=float(rng.uniform(0, 2 * np.pi)),
        flexion_cuadratica=_u(rng, "flexion_cuadratica"),
        holgura_alt_con_carga=_u(rng, "holgura_alt_con_carga"),
        deriva_cuadratica=_u(rng, "deriva_cuadratica"),
        ruido_arcmin=_u(rng, "ruido_arcmin"),
        deriva_noche_arcmin=_u(rng, "deriva_noche_arcmin"),
    )
    return MonturaSintetica(identificador, persistentes, no_lineales)


def muestrear_sesion(rng: np.random.Generator) -> ParametrosError:
    """Los términos que cambian cada vez que se arma el equipo."""
    p = ParametrosError()
    for nombre in TERMINOS_SESION:
        setattr(p, nombre, _u(rng, nombre))
    return p


@dataclass
class PuntoTrayectoria:
    """Un instante de la trayectoria verdadera del objeto."""

    instante: datetime
    az: float  # grados
    alt: float
    fase: float = 1.0  # fracción iluminada, de 0 a 1


def fase_lunar_aproximada(instante: datetime) -> float:
    """Fracción iluminada aproximada, de 0 (nueva) a 1 (llena).

    Aproximación de fase media: sirve como contexto en el registro, no como dato medido.
    Para el análisis del artículo conviene recalcularla con Skyfield.
    """
    if instante.tzinfo is None:
        instante = instante.replace(tzinfo=timezone.utc)
    dias = (instante - _LUNA_NUEVA_REF).total_seconds() / 86400.0
    edad = dias % _MES_SINODICO_DIAS
    return float((1 - np.cos(2 * np.pi * edad / _MES_SINODICO_DIAS)) / 2)


def trayectoria_luna(efemerides, inicio: datetime, duracion_min: float = 90.0,
                     paso_s: float = 1.0, altitud_minima: float = 10.0,
                     altitud_maxima: float = 85.0) -> list[PuntoTrayectoria]:
    """Trayectoria verdadera de la Luna según Skyfield, muestreada cada `paso_s`.

    Descarta los instantes fuera de la franja de altitud utilizable. El tope superior no es
    capricho: a la latitud de Portoviejo (~1° S) la Luna pasa muy cerca del cenit, y ahí una
    montura altacimutal necesita velocidades de azimut enormes y el modelo de apuntado
    degenera. Conviene excluir esa zona y decirlo en la Discusión.
    """
    if inicio.tzinfo is None:
        inicio = inicio.replace(tzinfo=timezone.utc)
    puntos: list[PuntoTrayectoria] = []
    n = int(duracion_min * 60 / paso_s)
    for i in range(n):
        t = inicio + timedelta(seconds=i * paso_s)
        pos = efemerides.altaz("Luna", t)
        if not (altitud_minima <= pos.altitud <= altitud_maxima):
            continue
        puntos.append(PuntoTrayectoria(t, pos.azimut, pos.altitud,
                                       fase_lunar_aproximada(t)))
    return puntos


def _cuantizar(grados: np.ndarray, resolucion_arcmin: float) -> np.ndarray:
    """Redondea al micropaso más cercano. Produce un error en diente de sierra."""
    paso = resolucion_arcmin / 60.0
    return np.round(np.asarray(grados, float) / paso) * paso


def error_no_lineal(az, alt, nl: ParametrosNoLineales, *, sentido_alt=0.0,
                    temperatura=None, reduccion_az: float = 14.0,
                    reduccion_alt: float = 5.0) -> tuple[np.ndarray, np.ndarray]:
    """Parte del error que el modelo clásico no puede representar, en minutos de arco."""
    az = np.atleast_1d(np.asarray(az, float))
    alt = np.atleast_1d(np.asarray(alt, float))
    s_alt = np.broadcast_to(np.atleast_1d(np.asarray(sentido_alt, float)), az.shape)
    h = np.radians(alt)

    # Excentricidad de la polea: un ciclo por vuelta de polea, no por vuelta del eje.
    ciclos_az = 2 * np.pi * reduccion_az * az / 360.0
    ciclos_alt = 2 * np.pi * reduccion_alt * alt / 360.0
    d_az = nl.periodico_az * np.sin(ciclos_az + nl.fase_periodico_az)
    d_alt = nl.periodico_alt * np.sin(ciclos_alt + nl.fase_periodico_alt)

    # Flexión que no es exactamente proporcional a cos(alt).
    d_alt = d_alt + nl.flexion_cuadratica * np.cos(h) ** 2

    # La holgura del eje de altitud crece al bajar, porque crece el par que soporta.
    d_alt = d_alt + nl.holgura_alt_con_carga * s_alt * np.cos(h)

    if temperatura is not None:
        dt = np.asarray(temperatura, float) - 25.0
        d_alt = d_alt + nl.deriva_cuadratica * dt ** 2

    return np.asarray(d_az, float), np.asarray(d_alt, float)


def generar_noche(montura: MonturaSintetica, sesion: ParametrosError,
                  trayectoria: Sequence[PuntoTrayectoria], *, nombre_sesion: str,
                  rng: np.random.Generator, temperatura_inicial: float = 28.0,
                  temperatura_final: float = 22.0,
                  corrector: Callable[[np.ndarray, np.ndarray], tuple[np.ndarray, np.ndarray]] | None = None,
                  objeto: str = "Luna") -> list[RegistroSeguimiento]:
    """Simula una noche de seguimiento y devuelve las filas del registro.

    `corrector` recibe (az_objeto, alt_objeto) y devuelve la corrección a aplicar en minutos
    de arco. Con `None` no se corrige nada: es la condición de línea base (E1).
    """
    if not trayectoria:
        return []

    n = len(trayectoria)
    az_obj = np.array([p.az for p in trayectoria], float)
    alt_obj = np.array([p.alt for p in trayectoria], float)
    fases = np.array([p.fase for p in trayectoria], float)

    # Perfil de temperatura: baja durante la noche, con algo de ruido.
    temp = np.linspace(temperatura_inicial, temperatura_final, n) + rng.normal(0, 0.15, n)
    presion = 1013.0 + rng.normal(0, 1.5, n)

    # Corrección aplicada antes de mover (en minutos de arco).
    if corrector is None:
        corr_az = np.zeros(n)
        corr_alt = np.zeros(n)
    else:
        corr_az, corr_alt = corrector(az_obj, alt_obj)
        corr_az = np.broadcast_to(np.asarray(corr_az, float), (n,))
        corr_alt = np.broadcast_to(np.asarray(corr_alt, float), (n,))

    # Lo que se le ordena a la montura, ya cuantizado al micropaso.
    az_cmd = _cuantizar(az_obj - corr_az / 60.0, RESOLUCION_AZ_ARCMIN)
    alt_cmd = _cuantizar(alt_obj - corr_alt / 60.0, RESOLUCION_ALT_ARCMIN)

    # Sentido del último giro de cada eje: es lo que activa la holgura.
    s_az = np.zeros(n)
    s_alt = np.zeros(n)
    s_az[1:] = np.sign(np.diff(az_cmd))
    s_alt[1:] = np.sign(np.diff(alt_cmd))

    # Error total = términos clásicos + efectos no lineales + ruido.
    completos = replace(sesion)
    for nombre in TERMINOS_PERSISTENTES:
        setattr(completos, nombre, getattr(montura.persistentes, nombre))

    lin_az, lin_alt = error_lineal(az_cmd, alt_cmd, completos, sentido_az=s_az,
                                   sentido_alt=s_alt, temperatura=temp)
    nolin_az, nolin_alt = error_no_lineal(az_cmd, alt_cmd, montura.no_lineales,
                                          sentido_alt=s_alt, temperatura=temp,
                                          reduccion_az=montura.reduccion_az,
                                          reduccion_alt=montura.reduccion_alt)

    nl = montura.no_lineales
    # Deriva lenta de la noche: un paseo aleatorio suave, normalizado a su amplitud.
    deriva = np.cumsum(rng.normal(0, 1, n))
    if np.max(np.abs(deriva)) > 0:
        deriva = deriva / np.max(np.abs(deriva)) * nl.deriva_noche_arcmin

    ruido_az = rng.normal(0, nl.ruido_arcmin, n)
    ruido_alt = rng.normal(0, nl.ruido_arcmin, n)

    # Episodios de nubes: bajan la calidad y empeoran la medida.
    calidad = np.ones(n)
    for _ in range(int(rng.integers(0, 3))):
        centro = int(rng.integers(0, n))
        ancho = int(rng.integers(30, max(31, n // 6)))
        inicio, fin = max(0, centro - ancho), min(n, centro + ancho)
        calidad[inicio:fin] = np.minimum(calidad[inicio:fin], float(rng.uniform(0.1, 0.7)))
    penalizacion = 1.0 + 3.0 * (1.0 - calidad)

    d_az = lin_az + nolin_az + deriva + ruido_az * penalizacion
    d_alt = lin_alt + nolin_alt + ruido_alt * penalizacion

    # Lo que la montura apunta de verdad frente a donde está el objeto.
    d_az_medido = d_az + (az_cmd - az_obj) * 60.0
    d_alt_medido = d_alt + (alt_cmd - alt_obj) * 60.0
    err_cielo = error_en_cielo_arcmin(d_az_medido, d_alt_medido, alt_obj)

    # El encoder de altitud mide el ángulo real del eje, con su propio ruido.
    encoder = alt_cmd + (d_alt / 60.0) + rng.normal(0, 0.01, n)

    # El acelerómetro mide el desnivel, pero no sin ruido: si lo diera exacto, el modelo
    # tendría una ventaja que en la montura real no va a tener.
    incl_ns = sesion.desnivel_ns / 60.0 + rng.normal(0, 0.02, n)
    incl_eo = sesion.desnivel_eo / 60.0 + rng.normal(0, 0.02, n)

    filas = []
    for i, punto in enumerate(trayectoria):
        filas.append(RegistroSeguimiento(
            fecha_utc=punto.instante.isoformat(timespec="seconds"),
            sesion=nombre_sesion,
            montura=montura.identificador,
            origen="simulado",
            objeto=objeto,
            az_objeto=round(float(az_obj[i]), 6),
            alt_objeto=round(float(alt_obj[i]), 6),
            az_comandado=round(float(az_cmd[i]), 6),
            alt_comandado=round(float(alt_cmd[i]), 6),
            sentido_az=float(s_az[i]),
            sentido_alt=float(s_alt[i]),
            encoder_alt=round(float(encoder[i]), 5),
            temperatura_c=round(float(temp[i]), 3),
            presion_hpa=round(float(presion[i]), 2),
            inclinacion_ns=round(float(incl_ns[i]), 5),
            inclinacion_eo=round(float(incl_eo[i]), 5),
            d_az=round(float(d_az_medido[i]), 4),
            d_alt=round(float(d_alt_medido[i]), 4),
            error_cielo_arcmin=round(float(err_cielo[i]), 4),
            fase_lunar=round(float(fases[i]), 4),
            calidad=round(float(calidad[i]), 3),
        ))
    return filas


def trayectoria_sintetica(inicio: datetime, n: int, *, paso_s: float = 1.0,
                          az_inicial: float = 80.0, alt_inicial: float = 25.0,
                          az_por_hora: float = 20.0,
                          alt_por_hora: float = 12.0) -> list[PuntoTrayectoria]:
    """Trayectoria recta aproximada, para pruebas y para usar sin descargar efemérides.

    **No usar para generar datos del artículo:** ahí la trayectoria sale de Skyfield, que es
    la verdad de referencia. Esto solo sirve para ejercitar el código.
    """
    if inicio.tzinfo is None:
        inicio = inicio.replace(tzinfo=timezone.utc)
    puntos = []
    for i in range(n):
        horas = i * paso_s / 3600.0
        t = inicio + timedelta(seconds=i * paso_s)
        puntos.append(PuntoTrayectoria(
            t,
            (az_inicial + az_por_hora * horas) % 360.0,
            min(85.0, alt_inicial + alt_por_hora * horas),
            fase_lunar_aproximada(t),
        ))
    return puntos


def pointings_de_sondeo(inicio: datetime, n: int, *, rng: np.random.Generator,
                        paso_s: float = 45.0, alt_min: float = 20.0,
                        alt_max: float = 65.0) -> list[PuntoTrayectoria]:
    """Los pointings del sondeo: `n` objetos conocidos repartidos por **todo** el cielo.

    No es un trozo de la trayectoria de la noche, y la diferencia resultó decisiva. Medido el
    07/11/2026: con los puntos de sondeo tomados a lo largo del arco de seguimiento (unos 80°
    de azimut) el sondeo no identifica la montura, porque sobre un arco corto los términos del
    error son casi indistinguibles entre sí. Es el mismo fenómeno que
    `test_un_arco_corto_no_deja_ver_la_no_linealidad`.

    Reparte el azimut en todo el círculo y la altitud en el rango utilizable, con algo de
    azar para que dos sondeos no caigan siempre en los mismos sitios. En campo es lo que uno
    hace sin pensarlo: elegir estrellas de alineación separadas, no vecinas.

    El tope de altitud es 65° a propósito, no 85°. Cerca del cenit una montura altazimutal es
    patológica: el factor `tan(h)` del desnivel se dispara (tan 80° = 5,7 frente a tan 45° =
    1) y un pointing de sondeo ahí aporta un error enorme y mal condicionado en vez de
    información. Es el punto ciego del cenit, conocido en monturas altazimutales.

    Al paso de 45 s por pointing, 6 puntos son unos 4 minutos de sesión.
    """
    if inicio.tzinfo is None:
        inicio = inicio.replace(tzinfo=timezone.utc)
    if n <= 0:
        return []

    # Reparto en azimut con un desfase al azar, para cubrir el círculo sin repetir posiciones.
    desfase = float(rng.uniform(0, 360))
    azimuts = (desfase + np.linspace(0.0, 360.0, n, endpoint=False)) % 360.0
    # Altitudes alternadas alto/bajo: cubrir el rango importa tanto como cubrir el azimut,
    # porque la flexión y la no perpendicularidad solo se separan con altitudes distintas.
    altitudes = np.linspace(alt_min, alt_max, n)
    altitudes = altitudes[np.argsort(np.abs(np.arange(n) - (n - 1) / 2.0))]
    altitudes = np.clip(altitudes + rng.normal(0, 2.0, n), alt_min, alt_max)

    puntos = []
    for i, (az, alt) in enumerate(zip(azimuts, altitudes)):
        t = inicio + timedelta(seconds=i * paso_s)
        puntos.append(PuntoTrayectoria(t, float(az), float(alt), fase_lunar_aproximada(t)))
    return puntos


def generar_dataset(ruta_csv: str | Path, *, n_monturas: int = 40, noches_por_montura: int = 3,
                    minutos_por_noche: float = 60.0, paso_s: float = 1.0, semilla: int = 0,
                    efemerides=None, inicio: datetime | None = None,
                    ruta_parametros: str | Path | None = None,
                    puntos_sondeo: int = 0) -> dict:
    """Genera el conjunto sintético completo y lo escribe en CSV.

    Con `efemerides=None` usa la trayectoria aproximada, que sirve para probar el pipeline
    pero **no** para los datos del artículo.

    Cada noche empieza por `puntos_sondeo` pointings repartidos por el cielo y sigue con el
    arco de seguimiento, que es el protocolo de sesión: sondear antes de observar. Así
    `aprendizaje.con_sondeo(..., desde="primeras")` encuentra el sondeo donde lo espera. Con
    `puntos_sondeo=0` se genera solo el arco, y entonces el condicionamiento no tiene de dónde
    salir.

    Devuelve un resumen con el recuento de filas y el error RMS, para dejar constancia.
    """
    rng = np.random.default_rng(semilla)
    inicio = inicio or datetime(2027, 1, 15, 1, 0, tzinfo=timezone.utc)
    ruta_csv = Path(ruta_csv)
    if ruta_csv.exists():
        ruta_csv.unlink()

    total = 0
    errores: list[float] = []
    parametros: list[dict] = []

    for i in range(n_monturas):
        montura = muestrear_montura(rng, f"sim{i:03d}")
        parametros.append(montura.a_dict())
        for j in range(noches_por_montura):
            arranque = inicio + timedelta(days=j * 3 + i * 31)
            if efemerides is not None:
                tray = trayectoria_luna(efemerides, arranque, minutos_por_noche, paso_s)
            else:
                tray = trayectoria_sintetica(
                    arranque, int(minutos_por_noche * 60 / paso_s), paso_s=paso_s,
                    az_inicial=float(rng.uniform(0, 360)),
                    alt_inicial=float(rng.uniform(15, 45)))
            if not tray:
                continue
            # El sondeo va delante del arco: es el orden del protocolo de sesión.
            sondeo = pointings_de_sondeo(arranque, puntos_sondeo, rng=rng)
            filas = generar_noche(montura, muestrear_sesion(rng), sondeo + list(tray),
                                  nombre_sesion=f"{montura.identificador}-n{j}", rng=rng)
            total += guardar_seguimiento(ruta_csv, filas)
            errores.extend(f.error_cielo_arcmin for f in filas)

    if ruta_parametros is not None and parametros:
        import csv as _csv
        ruta_parametros = Path(ruta_parametros)
        ruta_parametros.parent.mkdir(parents=True, exist_ok=True)
        with ruta_parametros.open("w", newline="", encoding="utf-8") as f:
            escritor = _csv.DictWriter(f, fieldnames=list(parametros[0]))
            escritor.writeheader()
            escritor.writerows(parametros)

    e = np.array(errores, float)
    return {
        "filas": total,
        "monturas": n_monturas,
        "sesiones": n_monturas * noches_por_montura,
        "rms_arcmin": float(np.sqrt(np.mean(e ** 2))) if e.size else 0.0,
        "mediana_arcmin": float(np.median(e)) if e.size else 0.0,
        "csv": str(ruta_csv),
    }


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Genera noches sintéticas de seguimiento.")
    p.add_argument("--salida", default="datos/sintetico.csv")
    p.add_argument("--parametros", default=None,
                   help="CSV opcional con los parámetros de cada montura simulada")
    p.add_argument("--monturas", type=int, default=40)
    p.add_argument("--noches", type=int, default=3, help="noches por montura")
    p.add_argument("--minutos", type=float, default=60.0)
    p.add_argument("--paso", type=float, default=1.0, help="segundos entre filas")
    p.add_argument("--semilla", type=int, default=0)
    p.add_argument("--sondeo", type=int, default=0,
                   help="pointings de sondeo al empezar cada noche (0 = sin sondeo)")
    p.add_argument("--skyfield", action="store_true",
                   help="usar efemérides reales (descarga de421.bsp la primera vez)")
    args = p.parse_args(argv)

    efemerides = None
    if args.skyfield:
        from .astro import Efemerides
        from .config import cargar_config
        cfg = cargar_config()
        efemerides = Efemerides(cfg.dir_efemerides, cfg.sitio)

    resumen = generar_dataset(
        args.salida, n_monturas=args.monturas, noches_por_montura=args.noches,
        minutos_por_noche=args.minutos, paso_s=args.paso, semilla=args.semilla,
        efemerides=efemerides, ruta_parametros=args.parametros,
        puntos_sondeo=args.sondeo)

    # Sin caracteres fuera de ASCII: la consola de Windows usa cp1252 por defecto y
    # revienta con el simbolo de minuto de arco.
    print(f"{resumen['filas']} filas | {resumen['monturas']} monturas | "
          f"{resumen['sesiones']} sesiones")
    print(f"Error en el cielo: RMS {resumen['rms_arcmin']:.2f} arcmin | "
          f"mediana {resumen['mediana_arcmin']:.2f} arcmin")
    print(f"Escrito en {resumen['csv']}")
    if not args.skyfield:
        print("Aviso: trayectoria aproximada. Para datos del articulo, usar --skyfield.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

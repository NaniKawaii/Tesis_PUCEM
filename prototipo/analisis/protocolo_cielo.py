"""¿Qué protocolo de medición le conviene al artículo: seguir un arco o recorrer el cielo?

Compara dos formas de obtener los datos de entrenamiento con **la misma** montura sintética:

  arco   el protocolo de `docs/08`: 6 apuntados de sondeo y luego seguir un objeto durante
         4 horas. En la práctica, un arco de unos 80° de azimut, que es lo que recorre la
         Luna en una sesión. Mide con un detector del disco lunar.
  cielo  el protocolo con resolución astrométrica (*plate solving*): N apuntados repartidos
         por todo el cielo utilizable, cada uno resuelto contra el catálogo de estrellas. No
         hace falta que haya un objeto en el campo, solo estrellas.

Y mide dos cosas, porque responden preguntas distintas:

  validación   el corrector aprendido frente al modelo clásico, dejando una noche fuera
               **dentro** de cada protocolo. Es lo que el artículo informa en E3.
  todo el cielo el corrector entrenado con todas las noches de cada protocolo, evaluado en
               noches nuevas de apuntados repartidos por todo el cielo. Es lo que importa
               para apuntar a un planeta o a cualquier objeto celeste: un modelo que solo vio
               un arco tiene que extrapolar al resto del cielo.

Como en `e5_transferencia.py`, cada afirmación se cuenta **en cuántos sorteos se sostiene**:
un efecto que aparece en una semilla no es un resultado.

Uso
---
    python -m analisis.protocolo_cielo --sorteos 6 --noches 6 8 --puntos 60 --sondeo 0
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from telescopio import aprendizaje as ap
from telescopio.registro import guardar_seguimiento
from telescopio.simulador import (
    generar_noche,
    muestrear_montura,
    muestrear_sesion,
    pointings_de_sondeo,
    trayectoria_sintetica,
)

INICIO = datetime(2027, 1, 15, 1, 0, tzinfo=timezone.utc)
FILAS_ARCO = 480   # 4 horas a un paso de 30 s, igual que e5_transferencia
PASO_ARCO_S = 30.0
PASO_CIELO_S = 60.0  # mover, asentar, exponer y resolver: ~1 minuto por apuntado
NOCHES_PRUEBA = 2


def _noche_arco(equipo, j: int, sondeo_n: int, rng: np.random.Generator):
    arranque = INICIO + timedelta(days=3 * j)
    sondeo = pointings_de_sondeo(arranque, sondeo_n, rng=rng)
    arco = trayectoria_sintetica(
        arranque + timedelta(minutes=10), FILAS_ARCO, paso_s=PASO_ARCO_S,
        az_inicial=float(rng.uniform(0, 360)), alt_inicial=float(rng.uniform(12, 45)))
    return generar_noche(equipo, muestrear_sesion(rng), sondeo + arco,
                         nombre_sesion=f"{equipo.identificador}-n{j}", rng=rng)


def _noche_cielo(equipo, j: int, puntos: int, sondeo_n: int, rng: np.random.Generator,
                 etiqueta="cielo"):
    """El mismo sondeo inicial que el arco, y luego apuntados por todo el cielo.

    La estructura es idéntica a la del arco a propósito: los mismos apuntados de sondeo al
    empezar (si los hay) y después los datos. Lo único que cambia entre protocolos es de
    dónde salen los datos: un arco o todo el cielo.
    """
    arranque = INICIO + timedelta(days=3 * j)
    sondeo = pointings_de_sondeo(arranque, sondeo_n, rng=rng, paso_s=PASO_CIELO_S)
    resto = pointings_de_sondeo(arranque + timedelta(minutes=10), puntos - sondeo_n,
                                rng=rng, paso_s=PASO_CIELO_S)
    return generar_noche(equipo, muestrear_sesion(rng), sondeo + resto,
                         nombre_sesion=f"{etiqueta}-n{j}", rng=rng)


def _cargar(ruta: Path, noches: list) -> ap.Datos:
    ruta.unlink(missing_ok=True)
    for filas in noches:
        guardar_seguimiento(ruta, filas)
    return ap.cargar(ruta)


def un_sorteo(carpeta: Path, semilla: int, *, noches: int, puntos: int, sondeo: int,
              tipo: str) -> dict:
    """La misma montura medida con los dos protocolos, más noches de prueba de todo el cielo."""
    # Misma montura y mismas semillas que e5_transferencia, para que la columna del arco
    # reproduzca exactamente su resultado: es la comprobación de que este script mide lo
    # mismo. Cada protocolo tiene su propio generador, para que uno no altere al otro.
    mia = muestrear_montura(np.random.default_rng(semilla + 10_000), "mia")
    rng_arco = np.random.default_rng(semilla + 2)
    rng_cielo = np.random.default_rng(semilla + 3)
    rng_prueba = np.random.default_rng(semilla + 4)

    arco = _cargar(carpeta / f"arco{semilla}.csv",
                   [_noche_arco(mia, j, sondeo, rng_arco) for j in range(noches)])
    cielo = _cargar(carpeta / f"cielo{semilla}.csv",
                    [_noche_cielo(mia, j, puntos, sondeo, rng_cielo) for j in range(noches)])
    # Noches de prueba: sesiones nuevas, apuntados por todo el cielo, nunca vistas al entrenar.
    prueba = _cargar(carpeta / f"prueba{semilla}.csv",
                     [_noche_cielo(mia, 100 + j, puntos, sondeo, rng_prueba, "prueba")
                      for j in range(NOCHES_PRUEBA)])

    # Los tres conjuntos se preparan igual. Con --sondeo 0 la columna del arco es
    # exactamente la condición del resultado del artículo (docs/08: --sondeo 0 --monturas 2).
    arco_p, _ = ap.preparar(arco, sondeo)
    cielo_p, _ = ap.preparar(cielo, sondeo)
    prueba_p, _ = ap.preparar(prueba, sondeo)

    r = {"semilla": semilla}
    for nombre, datos in (("arco", arco_p), ("cielo", cielo_p)):
        clas = ap.dejando_una_noche_fuera(datos, "clasico")
        apr = ap.dejando_una_noche_fuera(datos, tipo)
        _, p = ap.wilcoxon_pareado(clas, apr)
        # Generalización: entrenar con todas las noches y apuntar a todo el cielo.
        g_clas = ap.entrenar(datos, "clasico").residuo(prueba_p).rms
        g_apr = ap.entrenar(datos, tipo).residuo(prueba_p).rms
        r[nombre] = {"clasico": clas.rms, "aprendido": apr.rms, "p": p,
                     "g_clasico": g_clas, "g_aprendido": g_apr,
                     "filas": len(datos), "cobertura_az": float(np.ptp(datos.az))}
    r["sin_corregir"] = prueba_p.rms
    return r


def _resumen(filas: list[dict], noches: int) -> None:
    n = len(filas)
    print(f"\n=== {noches} noches · {n} sorteos ===")
    for prot in ("arco", "cielo"):
        f = [x[prot] for x in filas]
        clas = np.median([x["clasico"] for x in f])
        apr = np.median([x["aprendido"] for x in f])
        gana = sum(x["aprendido"] < x["clasico"] for x in f)
        sig = sum(x["p"] < 0.05 and x["aprendido"] < x["clasico"] for x in f)
        g_c = np.median([x["g_clasico"] for x in f])
        g_a = np.median([x["g_aprendido"] for x in f])
        g_gana = sum(x["g_aprendido"] < x["g_clasico"] for x in f)
        cob = np.median([x["cobertura_az"] for x in f])
        print(f"  {prot:>5s} | validación: clásico {clas:5.2f}' → aprendido {apr:5.2f}'  "
              f"gana {gana}/{n}, p<0,05 en {sig}/{n}")
        print(f"        | todo el cielo: clásico {g_c:5.2f}' → aprendido {g_a:5.2f}'  "
              f"gana {g_gana}/{n}   (azimut cubierto: {cob:.0f}°)")
    sc = np.median([x["sin_corregir"] for x in filas])
    print(f"  sin corrector (solo alineación de sesión), todo el cielo: {sc:.2f}'")


def main(argv: list[str] | None = None) -> int:
    pa = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    pa.add_argument("--sorteos", type=int, default=6)
    pa.add_argument("--noches", type=int, nargs="+", default=[4, 6, 8])
    pa.add_argument("--puntos", type=int, default=60, help="apuntados por noche (protocolo cielo)")
    pa.add_argument("--sondeo", type=int, default=0,
                    help="apuntados de sondeo al empezar cada noche; 0 = condición del artículo")
    pa.add_argument("--modelo", default="boosting", choices=[t for t in ap.TIPOS if t != "clasico"])
    pa.add_argument("--datos", default=None)
    a = pa.parse_args(argv)

    carpeta = Path(a.datos) if a.datos else Path(__file__).resolve().parent.parent / "datos" / "cielo"
    carpeta.mkdir(parents=True, exist_ok=True)
    print(f"Protocolo arco (sondeo {a.sondeo} + {FILAS_ARCO} filas) frente a protocolo cielo "
          f"({a.puntos} apuntados/noche) · modelo {a.modelo} · {a.sorteos} sorteos")

    for noches in a.noches:
        filas = [un_sorteo(carpeta, 20261107 + i * 101, noches=noches, puntos=a.puntos,
                           sondeo=a.sondeo, tipo=a.modelo) for i in range(a.sorteos)]
        _resumen(filas, noches)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

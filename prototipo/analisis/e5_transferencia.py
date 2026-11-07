"""E5: ¿sirve preentrenar en simulación? Reproduce la tabla del artículo.

Compara tres condiciones sobre las **mismas** noches de una montura:

  clasico      modelo clásico ajustado dejando una noche fuera (línea base)
  real_loo     boosting con sondeo, ajustado dejando una noche fuera (estrategia A)
  cero_noches  preentrenado solo en simulación + sondeo, sin ninguna noche real (estrategia B)

Por qué varios sorteos
----------------------
Un solo sorteo de la familia y de la montura no dice nada: al medirlo por primera vez
(07/11/2026) la estrategia B ganaba con p = 0,0078, pero repitiendo el experimento con otras
semillas a tamaño pequeño el resultado se daba la vuelta la mitad de las veces. Así que este
script repite el experimento completo con monturas independientes y cuenta **en cuántos
sorteos se sostiene la conclusión**. Un efecto que solo aparece en una semilla no es un
resultado.

La unidad estadística de cada sorteo es la noche, no el sorteo: es lo que tendrá el
experimento real de campo, una montura y unas ocho noches. El recuento entre sorteos es una
comprobación de robustez que solo se puede hacer en simulación, y hay que presentarla así.

Uso
---
    python -m analisis.e5_transferencia --sorteos 5 --noches 8
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
FILAS_POR_NOCHE = 480  # 4 horas a un paso de 30 s, la duración de una sesión de verdad
PASO_S = 30.0


def _escribir(ruta: Path, monturas, noches: int, semilla: int, puntos: int) -> Path:
    """Cada noche = los `puntos` pointings del sondeo, repartidos por el cielo, y luego el arco.

    El sondeo va **al principio y en posiciones dispersas**, que es el protocolo de campo:
    apuntar a unos objetos conocidos separados entre sí antes de empezar a seguir.
    """
    ruta.unlink(missing_ok=True)
    rng = np.random.default_rng(semilla)
    for equipo in monturas:
        for j in range(noches):
            arranque = INICIO + timedelta(days=3 * j)
            sondeo = pointings_de_sondeo(arranque, puntos, rng=rng)
            arco = trayectoria_sintetica(
                arranque + timedelta(minutes=10), FILAS_POR_NOCHE, paso_s=PASO_S,
                az_inicial=float(rng.uniform(0, 360)),
                alt_inicial=float(rng.uniform(12, 45)))
            guardar_seguimiento(ruta, generar_noche(
                equipo, muestrear_sesion(rng), sondeo + arco,
                nombre_sesion=f"{equipo.identificador}-n{j}", rng=rng))
    return ruta


def un_sorteo(carpeta: Path, semilla: int, *, n_monturas: int, noches_familia: int,
              noches: int, puntos: int, tipo: str) -> dict:
    """Un experimento completo con una familia y una montura independientes."""
    rng_familia = np.random.default_rng(semilla)
    familia = [muestrear_montura(rng_familia, f"s{i:02d}") for i in range(n_monturas)]
    # La montura de prueba es **otro sorteo de la misma distribución**: es la premisa de la
    # aleatorización de dominio. Si no se cumpliera, preentrenar no tendría sentido.
    mia = muestrear_montura(np.random.default_rng(semilla + 10_000), "mia")

    fam = ap.cargar(_escribir(carpeta / f"fam{semilla}.csv", familia,
                              noches_familia, semilla + 1, puntos))
    propia = ap.cargar(_escribir(carpeta / f"mia{semilla}.csv", [mia], noches,
                                 semilla + 2, puntos))

    mia_p, _ = ap.preparar(propia, puntos)

    cond = {
        "clasico": ap.dejando_una_noche_fuera(mia_p, "clasico"),
        "real_loo": ap.dejando_una_noche_fuera(mia_p, tipo),
    }
    if puntos > 0:
        fam_p, _ = ap.preparar(fam, puntos)
        previo = ap.entrenar(fam_p, tipo)
        # Las dos mitades del diagnóstico del 07/11/2026, separadas para ver qué aporta cada
        # una: heredar los términos clásicos de la familia, frente a ajustarlos con el sondeo.
        cond["cero_familia"] = ap.sin_noches_reales(mia_p, previo, clasico_del_sondeo=False)
        cond["cero_noches"] = ap.sin_noches_reales(mia_p, previo, clasico_del_sondeo=True)

    # La afirmación principal del artículo: el corrector aprendido vence al modelo clásico.
    _, p_real_vs_clasico = ap.wilcoxon_pareado(cond["clasico"], cond["real_loo"])
    p_vs_clasico = p_vs_real = float("nan")
    if puntos > 0:
        _, p_vs_clasico = ap.wilcoxon_pareado(cond["clasico"], cond["cero_noches"])
        _, p_vs_real = ap.wilcoxon_pareado(cond["real_loo"], cond["cero_noches"])

    return {
        "semilla": semilla,
        "rms_crudo": propia.rms,
        "rms_alineado": mia_p.rms,
        "rms": {k: v.rms for k, v in cond.items()},
        "p_real_vs_clasico": p_real_vs_clasico,
        "p_vs_clasico": p_vs_clasico,
        "p_vs_real": p_vs_real,
        "friedman": ap.friedman_nemenyi(cond),
        "cobertura_az": float(np.ptp(mia_p.az)),
    }


def main(argv: list[str] | None = None) -> int:
    pa = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    pa.add_argument("--sorteos", type=int, default=5)
    pa.add_argument("--monturas", type=int, default=20, help="monturas sinteticas por sorteo")
    pa.add_argument("--noches-familia", type=int, default=3)
    pa.add_argument("--noches", type=int, default=8, help="noches reales simuladas")
    pa.add_argument("--sondeo", type=int, default=ap.PUNTOS_SONDEO)
    pa.add_argument("--modelo", default="boosting", choices=[t for t in ap.TIPOS
                                                             if t != "clasico"])
    pa.add_argument("--datos", default=None, help="carpeta para los CSV (por defecto datos/e5)")
    a = pa.parse_args(argv)

    carpeta = Path(a.datos) if a.datos else Path(__file__).resolve().parent.parent / "datos" / "e5"
    carpeta.mkdir(parents=True, exist_ok=True)

    print(f"E5: {a.sorteos} sorteos, {a.monturas} monturas sinteticas x {a.noches_familia} "
          f"noches, {a.noches} noches reales, sondeo de {a.sondeo} puntos, modelo {a.modelo}")
    print(f"p minimo alcanzable con {a.noches} noches: {ap.p_minimo_alcanzable(a.noches):.5f}\n")

    claves = ["clasico", "real_loo"]
    if a.sondeo > 0:
        claves += ["cero_familia", "cero_noches"]

    cab = f"{'sorteo':>7s} {'crudo':>8s} {'alineado':>9s}" + \
          "".join(f"{k:>13s}" for k in claves)
    print(cab)
    print("-" * len(cab))

    filas = []
    for i in range(a.sorteos):
        r = un_sorteo(carpeta, 20261107 + i * 101, n_monturas=a.monturas,
                      noches_familia=a.noches_familia, noches=a.noches,
                      puntos=a.sondeo, tipo=a.modelo)
        filas.append(r)
        print(f"{i:>7d} {r['rms_crudo']:>7.1f}' {r['rms_alineado']:>8.2f}'" +
              "".join(f"{r['rms'][k]:>12.2f}'" for k in claves))

    print("\n--- Resumen entre sorteos ---")
    for clave in claves:
        v = np.array([f["rms"][clave] for f in filas])
        print(f"  {clave:>12s}: mediana {np.median(v):.2f}'  "
              f"min {v.min():.2f}'  max {v.max():.2f}'")

    n = len(filas)
    print("\n  --- En cuantos sorteos se sostiene cada afirmacion ---")

    def recuento(mejor: str, peor: str, p_clave: str | None = None) -> None:
        gana = sum(f["rms"][mejor] < f["rms"][peor] for f in filas)
        texto = f"  {mejor} mejor que {peor}: {gana}/{n} sorteos"
        if p_clave:
            sig = sum(f[p_clave] < 0.05 and f["rms"][mejor] < f["rms"][peor] for f in filas)
            texto += f" ({sig}/{n} con p < 0,05 y a favor)"
        print(texto)

    # La afirmacion del articulo: el corrector aprendido vence al modelo clasico.
    recuento("real_loo", "clasico", "p_real_vs_clasico")
    if a.sondeo > 0:
        recuento("cero_noches", "clasico", "p_vs_clasico")
        recuento("cero_noches", "real_loo", "p_vs_real")
        recuento("cero_familia", "clasico")

    print("\n  Un efecto que no se sostiene en la mayoria de los sorteos no es un resultado:")
    print("  si estas cuentas salen repartidas, lo que hay que publicar es eso mismo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

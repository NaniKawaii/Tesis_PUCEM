from dataclasses import replace
from datetime import datetime, timezone

import numpy as np
import pytest

from telescopio.errores import TERMINOS, ParametrosError, ajustar
from telescopio.registro import CAMPOS_SEGUIMIENTO, leer, sesiones
from telescopio.simulador import (
    RANGOS,
    RESOLUCION_AZ_ARCMIN,
    MonturaSintetica,
    ParametrosNoLineales,
    fase_lunar_aproximada,
    generar_dataset,
    generar_noche,
    muestrear_montura,
    muestrear_sesion,
    trayectoria_sintetica,
)

INICIO = datetime(2027, 1, 15, 1, 0, tzinfo=timezone.utc)

PERSISTENTES = ParametrosError(colimacion=6.0, no_perpendicularidad=-8.0, flexion=14.0,
                               holgura_az=5.0, holgura_alt=7.0,
                               deriva_az=0.25, deriva_alt=-0.3)

NO_LINEALES = ParametrosNoLineales(
    periodico_az=5.0, fase_periodico_az=0.7, periodico_alt=3.0, fase_periodico_alt=2.1,
    flexion_cuadratica=6.0, holgura_alt_con_carga=3.0, deriva_cuadratica=0.015,
    ruido_arcmin=0.4, deriva_noche_arcmin=1.5,
)

SESION = ParametrosError(indice_az=40.0, indice_alt=-20.0,
                         desnivel_ns=30.0, desnivel_eo=-22.0)


def _noche(no_lineales=NO_LINEALES, n=1440, semilla=11, paso_s=10.0):
    """Una noche de 4 horas por defecto, que es lo que dura una sesión de verdad.

    La duración importa y no es un detalle: ver
    `test_un_arco_corto_no_deja_ver_la_no_linealidad`.
    """
    montura = MonturaSintetica("prueba", PERSISTENTES, no_lineales)
    tray = trayectoria_sintetica(INICIO, n, paso_s=paso_s)
    rng = np.random.default_rng(semilla)
    return generar_noche(montura, SESION, tray, nombre_sesion="n0", rng=rng)


SIN_NO_LINEALES = replace(NO_LINEALES, periodico_az=0.0, periodico_alt=0.0,
                          flexion_cuadratica=0.0, holgura_alt_con_carga=0.0,
                          deriva_cuadratica=0.0, deriva_noche_arcmin=0.0)


def _residuo_del_modelo_clasico(filas):
    """Ajusta el modelo clásico completo y devuelve el error que queda sin explicar."""
    az = np.array([f.az_comandado for f in filas])
    alt = np.array([f.alt_comandado for f in filas])
    aj = ajustar(az, alt,
                 [f.d_az for f in filas], [f.d_alt for f in filas], TERMINOS,
                 sentido_az=np.array([f.sentido_az for f in filas]),
                 sentido_alt=np.array([f.sentido_alt for f in filas]),
                 temperatura=np.array([f.temperatura_c for f in filas]))
    return aj.rms_despues


def test_una_noche_produce_una_fila_por_instante():
    filas = _noche(n=300)
    assert len(filas) == 300
    assert {f.sesion for f in filas} == {"n0"}
    assert {f.origen for f in filas} == {"simulado"}
    primera = filas[0]
    assert primera.fecha_utc.startswith("2027-01-15")
    assert 0.0 <= primera.fase_lunar <= 1.0
    assert primera.sentido_az == 0.0  # la primera fila no tiene movimiento previo


def test_el_simulador_no_es_un_modelo_clasico_disfrazado():
    """La prueba que protege contra el razonamiento circular.

    Si el simulador solo generara los términos de `errores.py`, el ajuste lineal los
    recuperaría y no quedaría residuo: entonces "la IA mejora al modelo clásico" sería un
    artefacto del simulador y no un hallazgo. Los efectos no lineales tienen que dejar un
    residuo claramente mayor que el ruido.
    """
    residuo_limpio = _residuo_del_modelo_clasico(_noche(SIN_NO_LINEALES))
    residuo_real = _residuo_del_modelo_clasico(_noche(NO_LINEALES))

    # Sin efectos no lineales, el modelo clásico lo explica casi todo: queda el ruido.
    assert residuo_limpio < 1.2
    # Con ellos, queda bastante por aprender.
    assert residuo_real > 2.0 * residuo_limpio
    assert residuo_real > 1.5


def test_un_arco_corto_no_deja_ver_la_no_linealidad():
    """Hallazgo del 06/11/2026, encontrado al escribir la prueba anterior.

    Sobre un arco corto, los efectos no lineales son **indistinguibles** del modelo lineal:
    media vuelta de polea parece una rampa, cos(alt)^2 sobre 4° parece una constante, y la
    holgura que depende de la carga parece holgura a secas. El modelo lineal los absorbe y el
    residuo no crece.

    Es la forma matemática de "una noche es un arco, no la bóveda" (`docs/08` §4): lo que
    limita el aprendizaje no es el número de filas, sino la **cobertura del cielo**. Por eso
    hacen falta varias noches, y por eso la pregunta de cuántas tiene sentido.
    """
    corto = dict(n=120, paso_s=10.0)  # 20 minutos: ~7° de azimut
    largo = dict(n=1440, paso_s=10.0)  # 4 horas: ~80° de azimut

    razon_corto = (_residuo_del_modelo_clasico(_noche(NO_LINEALES, **corto))
                   / _residuo_del_modelo_clasico(_noche(SIN_NO_LINEALES, **corto)))
    razon_largo = (_residuo_del_modelo_clasico(_noche(NO_LINEALES, **largo))
                   / _residuo_del_modelo_clasico(_noche(SIN_NO_LINEALES, **largo)))

    assert razon_corto < 1.3, "en un arco corto la no linealidad debería pasar inadvertida"
    assert razon_largo > 2.0, "en una noche completa sí debería notarse"


def test_el_modelo_clasico_si_explica_la_mayor_parte_del_error():
    """El complemento del anterior: el residuo no puede ser *todo* el error.

    Si lo fuera, el modelo clásico no serviría de línea base y el diseño estaría mal.
    """
    filas = _noche()
    rms_total = float(np.sqrt(np.mean([f.error_cielo_arcmin ** 2 for f in filas])))
    assert _residuo_del_modelo_clasico(filas) < 0.5 * rms_total


def test_las_posiciones_comandadas_caen_en_micropasos():
    filas = _noche(n=200)
    paso = RESOLUCION_AZ_ARCMIN / 60.0
    restos = np.array([f.az_comandado for f in filas]) / paso
    assert np.allclose(restos, np.round(restos), atol=1e-6)


def test_misma_semilla_mismo_resultado():
    assert [f.d_az for f in _noche(semilla=3)] == [f.d_az for f in _noche(semilla=3)]
    assert [f.d_az for f in _noche(semilla=3)] != [f.d_az for f in _noche(semilla=4)]


def test_la_trayectoria_vacia_no_rompe():
    montura = MonturaSintetica("vacia", PERSISTENTES, NO_LINEALES)
    assert generar_noche(montura, SESION, [], nombre_sesion="x",
                         rng=np.random.default_rng(0)) == []


def test_el_corrector_reduce_el_error():
    """Aplicar la corrección correcta antes de mover tiene que bajar el error medido."""
    tray = trayectoria_sintetica(INICIO, 600)
    montura = MonturaSintetica("c", PERSISTENTES, ParametrosNoLineales(ruido_arcmin=0.1))

    sin_corregir = generar_noche(montura, SESION, tray, nombre_sesion="a",
                                 rng=np.random.default_rng(5))

    # Un corrector que conoce los términos de sesión, como tras la alineación.
    from telescopio.errores import error_lineal

    def corrector(az, alt):
        return error_lineal(az, alt, SESION)

    corregido = generar_noche(montura, SESION, tray, nombre_sesion="b",
                              rng=np.random.default_rng(5), corrector=corrector)

    rms = lambda fs: float(np.sqrt(np.mean([f.error_cielo_arcmin ** 2 for f in fs])))
    assert rms(corregido) < 0.5 * rms(sin_corregir)


def test_el_muestreo_respeta_los_rangos_declarados():
    rng = np.random.default_rng(1)
    for i in range(30):
        montura = muestrear_montura(rng, f"m{i}")
        for nombre, (bajo, alto) in RANGOS.items():
            for origen in (montura.persistentes, montura.no_lineales):
                if hasattr(origen, nombre):
                    assert bajo <= getattr(origen, nombre) <= alto, nombre
        # Los términos de sesión no son de la montura: se remuestrean en cada noche.
        assert montura.persistentes.indice_az == 0.0

    sesion = muestrear_sesion(rng)
    assert RANGOS["indice_az"][0] <= sesion.indice_az <= RANGOS["indice_az"][1]
    assert sesion.flexion == 0.0


def test_los_pointings_de_sondeo_cubren_el_cielo_y_no_un_arco():
    """La diferencia que decidió el metodo, medida el 07/11/2026.

    Seis puntos tomados a lo largo del arco de una noche cubren ~80° de azimut y no permiten
    identificar la montura. Seis pointings de sondeo tienen que cubrir el circulo entero y un
    rango amplio de altitud, que es lo que hace uno en campo al elegir estrellas de alineacion
    separadas. Ver `telescopio.simulador.pointings_de_sondeo`.
    """
    from telescopio.simulador import pointings_de_sondeo

    rng = np.random.default_rng(4)
    puntos = pointings_de_sondeo(INICIO, 6, rng=rng)
    assert len(puntos) == 6

    az = np.sort([p.az for p in puntos])
    # Repartidos en el circulo: el hueco mayor entre consecutivos no llega a un cuadrante.
    huecos = np.diff(np.concatenate([az, [az[0] + 360.0]]))
    assert huecos.max() < 90.0, f"azimut mal repartido: {az}"

    alt = np.array([p.alt for p in puntos])
    assert np.ptp(alt) > 40.0, "hace falta rango en altitud para separar flexion y no perp."
    assert (alt >= 15.0).all() and (alt <= 80.0).all()

    # Un arco de 4 horas, en cambio, cubre una fraccion del cielo.
    arco = trayectoria_sintetica(INICIO, 1440, paso_s=10.0)
    assert np.ptp([p.az for p in arco]) < 100.0


def test_dos_sondeos_no_caen_siempre_en_el_mismo_sitio():
    from telescopio.simulador import pointings_de_sondeo

    uno = [p.az for p in pointings_de_sondeo(INICIO, 6, rng=np.random.default_rng(1))]
    dos = [p.az for p in pointings_de_sondeo(INICIO, 6, rng=np.random.default_rng(2))]
    assert uno != dos
    assert [p.az for p in pointings_de_sondeo(INICIO, 6, rng=np.random.default_rng(1))] == uno


def test_un_sondeo_vacio_no_rompe():
    from telescopio.simulador import pointings_de_sondeo

    assert pointings_de_sondeo(INICIO, 0, rng=np.random.default_rng(0)) == []


def test_la_fase_lunar_queda_entre_cero_y_uno():
    for dias in range(0, 60, 3):
        fase = fase_lunar_aproximada(INICIO.replace(day=1) + __import__("datetime").timedelta(days=dias))
        assert 0.0 <= fase <= 1.0


def test_generar_dataset_escribe_un_csv_legible(tmp_path):
    csv = tmp_path / "sintetico.csv"
    parametros = tmp_path / "monturas.csv"
    resumen = generar_dataset(csv, n_monturas=3, noches_por_montura=2,
                              minutos_por_noche=2.0, paso_s=1.0, semilla=0,
                              ruta_parametros=parametros, puntos_sondeo=6)

    # Cada noche son los 6 pointings del sondeo mas el arco de seguimiento.
    assert resumen["filas"] == 3 * 2 * (6 + 120)
    assert resumen["sesiones"] == 6
    assert resumen["rms_arcmin"] > 0

    filas = leer(csv)
    assert len(filas) == resumen["filas"]
    assert list(filas[0]) == CAMPOS_SEGUIMIENTO
    # Seis sesiones distintas: es la unidad con la que se separa entrenamiento y prueba.
    assert len(sesiones(filas)) == 6
    assert len({f["montura"] for f in filas}) == 3

    assert len(leer(parametros)) == 3
    assert "p_flexion" in leer(parametros)[0]


def test_la_linea_de_comandos_funciona_y_no_imprime_fuera_de_ascii(tmp_path, capsys):
    """La consola de Windows usa cp1252: un simbolo de minuto de arco la hace reventar."""
    from telescopio.simulador import main

    salida = tmp_path / "cli.csv"
    assert main(["--salida", str(salida), "--monturas", "2", "--noches", "1",
                 "--minutos", "1", "--paso", "1", "--sondeo", "6"]) == 0

    texto = capsys.readouterr().out
    assert "132 filas" in texto  # 2 monturas x (6 de sondeo + 60 del arco)
    texto.encode("cp1252")  # falla si se cuela un caracter que Windows no sabe imprimir
    assert salida.exists()


def test_generar_dataset_no_acumula_entre_corridas(tmp_path):
    csv = tmp_path / "s.csv"
    uno = generar_dataset(csv, n_monturas=1, noches_por_montura=1, minutos_por_noche=1.0)
    dos = generar_dataset(csv, n_monturas=1, noches_por_montura=1, minutos_por_noche=1.0)
    assert uno["filas"] == dos["filas"] == len(leer(csv))

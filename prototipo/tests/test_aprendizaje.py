from datetime import datetime, timedelta, timezone

import numpy as np
import pytest

from telescopio import aprendizaje as ap
from telescopio.errores import ParametrosError
from telescopio.registro import guardar_seguimiento
from telescopio.simulador import (
    MonturaSintetica,
    ParametrosNoLineales,
    generar_noche,
    muestrear_montura,
    muestrear_sesion,
    pointings_de_sondeo,
    trayectoria_sintetica,
)

SONDEO = 6  # pointings de sondeo al empezar cada noche, como en el protocolo real

INICIO = datetime(2027, 1, 15, 1, 0, tzinfo=timezone.utc)

PERSISTENTES = ParametrosError(colimacion=6.0, no_perpendicularidad=-8.0, flexion=14.0,
                               holgura_az=5.0, holgura_alt=7.0, deriva_az=0.25,
                               deriva_alt=-0.3)
NO_LINEALES = ParametrosNoLineales(periodico_az=5.0, periodico_alt=3.0,
                                   flexion_cuadratica=6.0, holgura_alt_con_carga=3.0,
                                   ruido_arcmin=0.4)


def _csv(tmp_path, nombre="d.csv", n_sesiones=4, filas=150, semilla=3, montura="m0",
         familia=False):
    """Escribe un CSV de seguimiento.

    `familia=True` usa una montura **distinta** en cada sesión, que es lo que hace la
    aleatorización de dominio. Con `False`, todas las sesiones son de la misma montura y solo
    cambian los términos de sesión, que es el caso real de Nashla.

    Cada sesión son `SONDEO` pointings repartidos por el cielo y luego `filas` del arco de
    seguimiento, que es el orden del protocolo: sondear antes de observar.
    """
    ruta = tmp_path / nombre
    ruta.unlink(missing_ok=True)  # guardar_seguimiento anexa: hay que partir de cero
    rng = np.random.default_rng(semilla)
    equipo = MonturaSintetica(montura, PERSISTENTES, NO_LINEALES)
    for j in range(n_sesiones):
        if familia:
            equipo = muestrear_montura(rng, f"{montura}{j}")
        arranque = INICIO + timedelta(days=2 * j)
        sondeo = pointings_de_sondeo(arranque, SONDEO, rng=rng)
        tray = trayectoria_sintetica(arranque + timedelta(minutes=10), filas, paso_s=60.0,
                                     az_inicial=float(rng.uniform(0, 360)),
                                     alt_inicial=float(rng.uniform(15, 40)))
        guardar_seguimiento(ruta, generar_noche(equipo, muestrear_sesion(rng), sondeo + tray,
                                                nombre_sesion=f"{montura}-n{j}", rng=rng))
    return ruta


@pytest.fixture
def datos(tmp_path):
    return ap.cargar(_csv(tmp_path))


def test_cargar_lee_el_esquema_de_seguimiento(datos):
    assert len(datos) == 4 * (SONDEO + 150)
    assert len(datos.sesiones) == 4
    assert datos.rms > 0
    assert np.isfinite(datos.az).all() and np.isfinite(datos.d_az).all()


def test_cargar_avisa_si_falta_una_columna(tmp_path):
    ruta = tmp_path / "malo.csv"
    ruta.write_text("sesion,az_comandado\nx,1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Falta la columna"):
        ap.cargar(ruta)


def test_cargar_puede_filtrar_por_calidad(tmp_path):
    completo = ap.cargar(_csv(tmp_path))
    limpio = ap.cargar(_csv(tmp_path), calidad_minima=0.99)
    assert len(limpio) <= len(completo)


def test_la_alineacion_de_sesion_quita_casi_todo_el_error(datos):
    """Los términos de sesión dominan: son grados, frente a minutos del resto."""
    alineado, ajustes = ap.alinear_sesiones(datos)
    assert alineado.rms < 0.1 * datos.rms
    assert set(ajustes) == set(datos.sesiones)
    # Lo que se calibra son los términos de sesión, no los persistentes.
    assert all(p.flexion == 0.0 for p in ajustes.values())


def test_el_modelo_clasico_explica_parte_del_residuo(datos):
    alineado, _ = ap.alinear_sesiones(datos)
    corrector = ap.entrenar(alineado, "clasico")
    assert corrector.residuo(alineado).rms < alineado.rms
    assert corrector.modelo is None


@pytest.mark.parametrize("tipo", ["ridge", "boosting"])
def test_los_modelos_aprendidos_se_entrenan_y_predicen(datos, tipo):
    alineado, _ = ap.alinear_sesiones(datos)
    corrector = ap.entrenar(alineado, tipo)
    d_az, d_alt = corrector.predecir(alineado)
    assert d_az.shape == (len(alineado),)
    assert np.isfinite(d_az).all() and np.isfinite(d_alt).all()
    # Sobre los propios datos de entrenamiento tiene que mejorar al clásico.
    clasico = ap.entrenar(alineado, "clasico").residuo(alineado).rms
    assert corrector.residuo(alineado).rms < clasico


def test_tipo_desconocido(datos):
    with pytest.raises(ValueError, match="Tipo desconocido"):
        ap.entrenar(datos, "random_forest")


def test_dejando_una_noche_fuera_evalua_cada_noche(datos):
    alineado, _ = ap.alinear_sesiones(datos)
    resultado = ap.dejando_una_noche_fuera(alineado, "clasico")
    assert set(resultado.por_sesion) == set(alineado.sesiones)
    assert resultado.n_entrenamiento == len(alineado.sesiones) - 1
    assert resultado.estrategia == "real"
    assert np.isfinite(resultado.rms)


def test_dejando_una_noche_fuera_exige_dos_sesiones(tmp_path):
    datos = ap.cargar(_csv(tmp_path, n_sesiones=1))
    with pytest.raises(ValueError, match="al menos 2 sesiones"):
        ap.dejando_una_noche_fuera(datos, "clasico")


def test_comparar_modelos_y_friedman(datos):
    alineado, _ = ap.alinear_sesiones(datos)
    resultados = ap.comparar_modelos(alineado, ["clasico", "ridge", "boosting"])
    assert set(resultados) == {"clasico", "ridge", "boosting"}

    fr = ap.friedman_nemenyi(resultados)
    assert fr.n_bloques == 4
    assert set(fr.rangos_medios) == set(resultados)
    # Los rangos medios de k modelos suman k(k+1)/2 por bloque.
    assert sum(fr.rangos_medios.values()) == pytest.approx(3 * 4 / 2)
    assert fr.mejor in resultados
    assert 0.0 <= fr.p <= 1.0


def test_la_diferencia_critica_de_nemenyi_coincide_con_la_formula():
    """Con 3 modelos y 6 noches la diferencia crítica es ~1,35 sobre un rango de 1 a 3."""
    resultados = {
        t: ap.Resultado(t, "real", {f"n{i}": 1.0 + i * 0.1 * k for i in range(6)}, 5)
        for k, t in enumerate(["a", "b", "c"])
    }
    fr = ap.friedman_nemenyi(resultados)
    assert fr.diferencia_critica == pytest.approx(2.343 * np.sqrt(3 * 4 / (6 * 6)), abs=1e-3)
    assert fr.diferencia_critica == pytest.approx(1.35, abs=0.01)


def test_friedman_necesita_al_menos_dos_modelos():
    with pytest.raises(ValueError, match="al menos 2 modelos"):
        ap.friedman_nemenyi({"a": ap.Resultado("a", "real", {"n0": 1.0}, 1)})


def test_wilcoxon_con_resultados_identicos_no_detecta_diferencia():
    a = ap.Resultado("a", "real", {f"n{i}": 1.0 + i for i in range(6)}, 5)
    b = ap.Resultado("b", "simulacion", {f"n{i}": 1.0 + i for i in range(6)}, 5)
    _, p = ap.wilcoxon_pareado(a, b)
    assert p == 1.0


def test_el_piso_son_seis_noches():
    """Con 5 noches el Wilcoxon pareado no puede dar p < 0,05 ni en el mejor caso."""
    assert ap.p_minimo_alcanzable(5) == pytest.approx(0.0625)
    assert ap.p_minimo_alcanzable(5) > 0.05
    assert ap.p_minimo_alcanzable(6) == pytest.approx(0.03125)
    assert ap.p_minimo_alcanzable(6) < 0.05


def test_las_caracteristicas_no_se_disparan_en_el_cenit(datos):
    cerca_del_cenit = datos.submuestra(np.arange(5))
    cerca_del_cenit.alt[:] = 89.9
    X = ap.caracteristicas(cerca_del_cenit)
    assert np.isfinite(X).all()


def test_la_curva_de_aprendizaje_entrega_un_punto_por_cantidad_de_noches(datos):
    alineado, _ = ap.alinear_sesiones(datos)
    puntos = ap.curva_de_aprendizaje(alineado, "clasico", n_noches=[1, 2], repeticiones=2)
    assert {p.n_noches for p in puntos} == {1, 2}
    assert all(p.estrategia == "real" for p in puntos)
    assert all(np.isfinite(p.rms) for p in puntos)


def test_la_curva_exige_tres_sesiones(tmp_path):
    datos = ap.cargar(_csv(tmp_path, n_sesiones=2))
    with pytest.raises(ValueError, match="al menos 3 sesiones"):
        ap.curva_de_aprendizaje(datos, "clasico")


def test_noches_para_umbral():
    puntos = [ap.PuntoCurva(1, "real", [5.0]), ap.PuntoCurva(2, "real", [3.0]),
              ap.PuntoCurva(3, "real", [2.0])]
    assert ap.noches_para_umbral(puntos, 3.5, "real") == 2
    assert ap.noches_para_umbral(puntos, 1.0, "real") is None


def test_sin_sondeo_el_preentrenado_no_puede_distinguir_dos_monturas(tmp_path):
    """La razón exacta por la que falló la transferencia sin condicionamiento.

    Dos monturas **distintas** apuntadas a las mismas posiciones producen exactamente las
    mismas entradas, porque las entradas solo describen dónde está el telescopio y en qué
    condiciones. Así que el modelo predice para las dos lo mismo, por buenas que sean sus
    predicciones: solo puede dar la media de la familia, y la media no es ninguna montura.

    Esto es una identidad, no una medición: se cumple siempre, no depende de la semilla. Y
    cubre a los tres modelos por igual, porque no habla del modelo sino de sus entradas.

    Con el sondeo las entradas sí se separan, que es la condición necesaria. **No basta**: que
    el modelo llegue a usarlas depende de haber visto suficientes monturas distintas al
    entrenar. Al escribir esta prueba, un boosting entrenado sobre 2 sesiones daba la misma
    predicción para las dos, con sondeo y todo: nunca partía por esas columnas, porque no
    había visto variación entre monturas que las justificara. De ahí que la familia sintética
    tenga que ser amplia; el efecto medido está en `analisis/e5_transferencia.py`.

    Ver `docs/08-diseno-definitivo.md` §4.
    """
    datos = ap.cargar(_csv(tmp_path, n_sesiones=2))
    alineado, _ = ap.alinear_sesiones(datos)

    # Misma geometría, errores distintos: dos monturas en las mismas posiciones del cielo.
    otra = alineado.con_errores(alineado.d_az * 2.5 - 3.0, alineado.d_alt * 0.4 + 1.0)

    # Sin sondeo las entradas son idénticas, así que cualquier modelo predice lo mismo para
    # las dos. No es cuestión de ajustar hiperparámetros: no hay información que usar.
    assert np.array_equal(ap.caracteristicas(alineado), ap.caracteristicas(otra))

    # Con sondeo se separan. Es condición necesaria para que la transferencia pueda funcionar.
    assert not np.array_equal(ap.caracteristicas(ap.con_sondeo(alineado)),
                              ap.caracteristicas(ap.con_sondeo(otra)))


def test_el_sondeo_anade_cuatro_numeros_por_punto(datos):
    alineado, _ = ap.alinear_sesiones(datos)
    sondeado = ap.con_sondeo(alineado, 6)

    assert sondeado.sondeo.shape == (len(alineado), 24)
    assert sondeado.puntos_sondeo == 6
    assert ap.caracteristicas(sondeado).shape[1] == ap.caracteristicas(alineado).shape[1] + 24
    assert np.isfinite(sondeado.sondeo).all()


def test_el_sondeo_es_el_mismo_en_toda_la_sesion_y_distinto_entre_sesiones(datos):
    """Identifica la montura-en-esta-noche, así que es constante dentro de la sesión."""
    alineado, _ = ap.alinear_sesiones(datos)
    sondeado = ap.con_sondeo(alineado)

    vectores = []
    for s in sondeado.sesiones:
        filas = sondeado.de_sesiones([s]).sondeo
        assert np.allclose(filas, filas[0]), "dentro de una sesión el sondeo no puede variar"
        vectores.append(filas[0])

    for i in range(len(vectores)):
        for j in range(i + 1, len(vectores)):
            assert not np.allclose(vectores[i], vectores[j])


def test_el_sondeo_de_una_sesion_no_mira_a_las_demas(datos):
    """Sin esto, el sondeo sería una fuga entre noches y la validación no valdría."""
    alineado, _ = ap.alinear_sesiones(datos)
    original = ap.con_sondeo(alineado)

    primera = alineado.sesiones[0]
    otras = np.array([str(s) != primera for s in alineado.sesion])
    estropeado = alineado.con_errores(
        np.where(otras, alineado.d_az + 500.0, alineado.d_az), alineado.d_alt)
    tocado = ap.con_sondeo(estropeado)

    de_primera = np.array([str(s) == primera for s in alineado.sesion])
    assert np.allclose(original.sondeo[de_primera], tocado.sondeo[de_primera])
    assert not np.allclose(original.sondeo[otras], tocado.sondeo[otras])


def test_sondeo_cero_deja_los_datos_como_estaban(datos):
    alineado, _ = ap.alinear_sesiones(datos)
    assert ap.con_sondeo(alineado, 0).sondeo is None
    assert ap.con_sondeo(alineado, 0).es_sondeo is None
    assert ap.con_sondeo(ap.con_sondeo(alineado, 6), 0).puntos_sondeo == 0


def test_el_sondeo_marca_que_filas_son(datos):
    """Hay que saber **qué** filas son el sondeo, no solo cuántas: con ellas se ajustan los
    términos clásicos de la condición de cero noches."""
    alineado, _ = ap.alinear_sesiones(datos)

    primeras = ap.con_sondeo(alineado, 6, desde="primeras")
    for s in primeras.sesiones:
        noche = primeras.de_sesiones([s])
        assert noche.es_sondeo[:6].all(), "con 'primeras' el sondeo va al principio"
        assert not noche.es_sondeo[6:].any()

    repartidas = ap.con_sondeo(alineado, 6, desde="reparto")
    assert repartidas.es_sondeo.sum() <= primeras.es_sondeo.sum() + len(primeras.sesiones)
    assert not np.array_equal(primeras.sondeo, repartidas.sondeo)


def test_desde_desconocido(datos):
    alineado, _ = ap.alinear_sesiones(datos)
    with pytest.raises(ValueError, match="'primeras' o 'reparto'"):
        ap.con_sondeo(alineado, 6, desde="por_ahi")


def test_la_marca_del_sondeo_sobrevive_a_quedarse_con_una_noche(datos):
    alineado, _ = ap.alinear_sesiones(datos)
    sondeado = ap.con_sondeo(alineado, 6)
    una = sondeado.de_sesiones([sondeado.sesiones[1]])
    assert una.es_sondeo is not None and una.es_sondeo.sum() == 6
    assert una.sondeo.shape == (len(una), 24)


def test_cero_noches_usa_el_sondeo_para_los_terminos_clasicos(tmp_path):
    """Heredar los términos clásicos de la familia es volver a usar su media.

    Con `clasico_del_sondeo=True` se ajustan con los 6 puntos de esa noche, que son 12
    ecuaciones para 7 términos. La prueba comprueba que de verdad cambian: si no cambiaran,
    la opción no estaría haciendo nada.
    """
    propia, _ = ap.preparar(ap.cargar(_csv(tmp_path, "propia.csv", n_sesiones=3, semilla=1,
                                           montura="mia")), 6)
    familia, _ = ap.preparar(ap.cargar(_csv(tmp_path, "diversa.csv", n_sesiones=8, semilla=2,
                                            montura="otra", familia=True)), 6)
    previo = ap.entrenar(familia, "boosting")

    de_familia = ap.sin_noches_reales(propia, previo, clasico_del_sondeo=False)
    del_sondeo = ap.sin_noches_reales(propia, previo, clasico_del_sondeo=True)

    assert set(de_familia.por_sesion) == set(del_sondeo.por_sesion)
    assert de_familia.rms != del_sondeo.rms
    # Cuál de las dos gana es una medición, no una identidad: está en analisis/e5_transferencia.py.


def test_preparar_alinea_sondea_y_quita_las_filas_de_sondeo(tmp_path):
    crudos = ap.cargar(_csv(tmp_path))
    listos, ajustes = ap.preparar(crudos, SONDEO)

    assert listos.rms < 0.1 * crudos.rms        # alineado
    assert listos.puntos_sondeo == SONDEO       # sondeado
    assert len(listos) == len(crudos) - 4 * SONDEO  # y sin las filas de calibración
    assert set(ajustes) == set(crudos.sesiones)
    assert set(listos.sesiones) == set(crudos.sesiones)


def test_quitar_el_sondeo_de_la_evaluacion_cambia_el_resultado(tmp_path):
    """Los pointings de sondeo van a altitudes altas y su error es mucho mayor.

    Dejarlos dentro de la evaluación multiplicaba por tres el RMS de todas las condiciones,
    midiendo la calibración en vez de la observación. Ver `Datos.observaciones`.
    """
    alineado, _ = ap.alinear_sesiones(ap.cargar(_csv(tmp_path)))
    con_filas = ap.con_sondeo(alineado, SONDEO)
    sin_filas = con_filas.observaciones()

    assert len(sin_filas) == len(con_filas) - 4 * SONDEO
    assert sin_filas.rms < con_filas.rms
    assert sin_filas.puntos_sondeo == SONDEO  # los valores del sondeo siguen disponibles
    assert sin_filas.observaciones() is sin_filas  # idempotente


def test_los_valores_del_sondeo_sobreviven_a_quitar_sus_filas(tmp_path):
    alineado, _ = ap.alinear_sesiones(ap.cargar(_csv(tmp_path)))
    con_filas = ap.con_sondeo(alineado, SONDEO)
    sesion = con_filas.sesiones[0]

    esperado = con_filas.de_sesiones([sesion]).submuestra(
        con_filas.de_sesiones([sesion]).es_sondeo)
    az, alt, d_az, d_alt = con_filas.observaciones().valores_de_sondeo(sesion)

    assert np.allclose(az, esperado.az) and np.allclose(alt, esperado.alt)
    assert np.allclose(d_az, esperado.d_az) and np.allclose(d_alt, esperado.d_alt)


def test_valores_de_sondeo_sin_sondeo_avisa(datos):
    with pytest.raises(ValueError, match="no traen sondeo"):
        datos.valores_de_sondeo(datos.sesiones[0])


@pytest.mark.parametrize("desde", ["primeras", "reparto"])
def test_una_sesion_mas_corta_que_el_sondeo_no_rompe(tmp_path, desde):
    """Pedir más puntos de sondeo que filas tiene la sesión: repite, no revienta."""
    datos = ap.cargar(_csv(tmp_path, n_sesiones=2, filas=4))  # 2 x (6 + 4) = 20 filas
    sondeado = ap.con_sondeo(datos, 20, desde=desde)
    assert sondeado.sondeo.shape == (len(datos), 80)
    assert np.isfinite(sondeado.sondeo).all()
    assert sondeado.observaciones() is not None


def test_entrenar_avisa_si_el_previo_trae_otro_numero_de_puntos(tmp_path):
    datos = ap.cargar(_csv(tmp_path))
    alineado, _ = ap.alinear_sesiones(datos)
    previo = ap.entrenar(ap.con_sondeo(alineado, 6), "boosting")
    with pytest.raises(ValueError, match="puntos de sondeo"):
        ap.entrenar(ap.con_sondeo(alineado, 3), "boosting", previo=previo)


def test_cero_noches_reales_necesita_sondeo(tmp_path):
    datos = ap.cargar(_csv(tmp_path))
    alineado, _ = ap.alinear_sesiones(datos)
    previo = ap.entrenar(alineado, "boosting")
    with pytest.raises(ValueError, match="Sin sondeo"):
        ap.sin_noches_reales(alineado, previo)


def test_cero_noches_reales_evalua_todas_las_noches(tmp_path):
    propia, _ = ap.preparar(ap.cargar(_csv(tmp_path, "propia.csv", n_sesiones=3, semilla=1,
                                           montura="mia")), 6)
    familia, _ = ap.preparar(ap.cargar(_csv(tmp_path, "diversa.csv", n_sesiones=8, semilla=2,
                                            montura="otra", familia=True)), 6)
    previo = ap.entrenar(familia, "boosting")

    r = ap.sin_noches_reales(propia, previo)
    assert set(r.por_sesion) == set(propia.sesiones)
    assert r.n_entrenamiento == 0  # ninguna noche real: es el sentido de la condición
    assert r.estrategia == "simulacion"
    assert np.isfinite(r.rms)


def test_la_curva_admite_cero_noches_solo_con_simulacion(tmp_path):
    reales, _ = ap.preparar(ap.cargar(_csv(tmp_path, "r.csv", semilla=1, montura="mia")), 6)
    sinteticos = ap.cargar(_csv(tmp_path, "s.csv", n_sesiones=8, semilla=2, montura="otra",
                                familia=True))

    solos = ap.curva_de_aprendizaje(reales, "boosting", n_noches=[0, 1], repeticiones=2)
    assert {p.n_noches for p in solos} == {1}, "sin sintéticos no existe el punto de 0 noches"

    con = ap.curva_de_aprendizaje(reales, "boosting", sinteticos=sinteticos,
                                  n_noches=[0, 1], repeticiones=2)
    cero = [p for p in con if p.n_noches == 0]
    assert len(cero) == 1 and cero[0].estrategia == "simulacion"
    assert np.isfinite(cero[0].rms)

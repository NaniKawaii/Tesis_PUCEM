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
    trayectoria_sintetica,
)

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
    """
    ruta = tmp_path / nombre
    ruta.unlink(missing_ok=True)  # guardar_seguimiento anexa: hay que partir de cero
    rng = np.random.default_rng(semilla)
    equipo = MonturaSintetica(montura, PERSISTENTES, NO_LINEALES)
    for j in range(n_sesiones):
        if familia:
            equipo = muestrear_montura(rng, f"{montura}{j}")
        tray = trayectoria_sintetica(INICIO + timedelta(days=2 * j), filas, paso_s=60.0,
                                     az_inicial=float(rng.uniform(0, 360)),
                                     alt_inicial=float(rng.uniform(15, 40)))
        guardar_seguimiento(ruta, generar_noche(equipo, muestrear_sesion(rng), tray,
                                                nombre_sesion=f"{montura}-n{j}", rng=rng))
    return ruta


@pytest.fixture
def datos(tmp_path):
    return ap.cargar(_csv(tmp_path))


def test_cargar_lee_el_esquema_de_seguimiento(datos):
    assert len(datos) == 4 * 150
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


def test_la_transferencia_por_residuo_no_aporta_sobre_una_familia_centrada(tmp_path):
    """Resultado negativo medido el 06/11/2026, fijado aquí para que no se pierda.

    Un modelo preentrenado sobre muchas monturas distintas solo puede predecir la **media de
    la familia**, y la media no es ninguna montura concreta. Usarla como desplazamiento fijo
    inyecta un error que no guarda relación con la montura real: la correlación entre lo que
    predice y lo que habría que predecir es prácticamente cero.

    Medido con datos de tamaño realista (20 monturas, 8 noches): la correlación entre lo que
    predice el preentrenado y lo que habría que predecir fue de **−0,003 en azimut y +0,031
    en altitud**, mientras inyectaba 2,3′ de desplazamiento. Con el condicionamiento por
    sondeo, la misma correlación subió a **+0,66 y +0,44**.

    Ver `docs/08-diseno-definitivo.md` §4. La reparación es condicionar el modelo con unas
    pocas medidas de sondeo de la montura que tiene delante.
    """
    propia = ap.cargar(_csv(tmp_path, "propia.csv", n_sesiones=3, semilla=1, montura="mia"))
    familia = ap.cargar(_csv(tmp_path, "diversa.csv", n_sesiones=8, semilla=2,
                             montura="otra", familia=True))

    ali_propia, _ = ap.alinear_sesiones(propia)
    ali_familia, _ = ap.alinear_sesiones(familia)

    previo = ap.entrenar(ali_familia, "boosting")
    objetivo = ap.entrenar(ali_propia, "clasico").residuo(ali_propia)
    pred_az, _ = previo.predecir_ml(ap.caracteristicas(ali_propia))

    correlacion = abs(np.corrcoef(pred_az, objetivo.d_az)[0, 1])
    assert correlacion < 0.25, "sobre una familia diversa no debería quedar señal transferible"

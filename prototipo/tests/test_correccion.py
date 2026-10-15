import numpy as np
import pytest

from telescopio.correccion import ModeloCorreccion, error_en_cielo_arcmin, evaluar


def datos_sinteticos(n=60, semilla=1):
    """Errores típicos de una montura: desnivel del trípode + desfase del índice + ruido."""
    rng = np.random.default_rng(semilla)
    az = rng.uniform(0, 360, n)
    alt = rng.uniform(15, 80, n)
    a = np.radians(az)
    d_az = 0.20 + 0.15 * np.sin(a) * np.tan(np.radians(alt)) + rng.normal(0, 0.02, n)
    d_alt = -0.10 + 0.15 * np.cos(a) + rng.normal(0, 0.02, n)
    return az, alt, d_az, d_alt


def test_error_en_cielo_considera_la_altitud():
    assert error_en_cielo_arcmin(1.0, 0.0, 0.0) == pytest.approx(60)
    assert error_en_cielo_arcmin(1.0, 0.0, 60.0) == pytest.approx(30)


@pytest.mark.parametrize("tipo", ["lineal", "red_neuronal"])
def test_la_correccion_reduce_el_error(tipo):
    resumen = evaluar(tipo, *datos_sinteticos()).resumen()
    assert resumen["rms_con_arcmin"] < 0.5 * resumen["rms_sin_arcmin"]
    assert resumen["p_valor_wilcoxon"] < 0.05


def test_pocos_datos():
    with pytest.raises(ValueError):
        ModeloCorreccion("lineal").entrenar([1, 2], [3, 4], [0, 0], [0, 0])


def test_guardar_y_cargar(tmp_path):
    az, alt, d_az, d_alt = datos_sinteticos()
    m = ModeloCorreccion("lineal").entrenar(az, alt, d_az, d_alt)
    ruta = tmp_path / "m.joblib"
    m.guardar(str(ruta))
    assert ModeloCorreccion.cargar(str(ruta)).predecir(100, 40) == pytest.approx(m.predecir(100, 40))

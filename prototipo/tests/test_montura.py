import pytest

from telescopio.montura import diferencia_angular
from telescopio.motores import FinDeCarrera


def test_resolucion_por_defecto_usa_las_reducciones_reales(cfg):
    # 200 pasos × 16 micropasos × 14 de reducción = 124,4 micropasos por grado -> 0,48'
    assert cfg.az.resolucion_arcmin == pytest.approx(0.482, abs=1e-3)
    # En altitud la reducción es 5:1 -> 44,4 micropasos por grado -> 1,35'
    assert cfg.alt.resolucion_arcmin == pytest.approx(1.35, abs=1e-3)


def test_no_mueve_sin_referencia(montura):
    with pytest.raises(RuntimeError):
        montura.mover_a(10, 10)


def test_mover_a_lleva_ambos_ejes_al_destino(montura):
    montura.referenciar(0, 0)
    montura.mover_a(123.4, 56.7)
    az, alt = montura.posicion()
    resolucion = montura.eje("az").resolucion_arcmin / 60
    assert az == pytest.approx(123.4, abs=resolucion)
    assert alt == pytest.approx(56.7, abs=resolucion)


def test_azimut_toma_el_camino_corto(montura):
    montura.referenciar(0, 0)
    montura.mover_a(350, 20)  # mejor girar −10° que +350°
    assert montura.angulo("az") == pytest.approx(-10, abs=0.2)


def test_altitud_fuera_de_rango(montura):
    montura.referenciar(0, 0)
    with pytest.raises(ValueError):
        montura.mover_a(0, 95)


def test_fin_de_carrera_se_propaga(montura):
    montura.referenciar(0, 0)
    montura.motores["alt"].fin_carrera_activo = True
    with pytest.raises(FinDeCarrera):
        montura.mover_a(30, 30)


@pytest.mark.parametrize("a,b,esperado", [(10, 350, 20), (350, 10, -20), (180, 0, -180), (0, 0, 0)])
def test_diferencia_angular(a, b, esperado):
    assert diferencia_angular(a, b) == pytest.approx(esperado)

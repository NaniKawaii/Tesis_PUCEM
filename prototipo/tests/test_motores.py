import threading

import numpy as np
import pytest

from telescopio.config import Eje
from telescopio.motores import FinDeCarrera, MotorSimulado, perfil_trapezoidal


def test_perfil_trapezoidal_respeta_vel_max_y_es_simetrico():
    retardos = perfil_trapezoidal(5000, vel_max=1600, aceleracion=800)
    assert len(retardos) == 5000
    assert np.isclose(retardos.min(), 1 / 1600)
    assert np.allclose(retardos, retardos[::-1])
    assert retardos[0] > retardos[100] > retardos[2500]  # arranca despacio


def test_perfil_corto_es_triangular():
    retardos = perfil_trapezoidal(100, vel_max=1600, aceleracion=800)
    assert retardos.min() > 1 / 1600


def test_motor_simulado_cuenta_pasos_en_ambos_sentidos():
    m = MotorSimulado(Eje("az"), escala_tiempo=0)
    assert m.mover(1000) == 1000
    assert m.mover(-250) == -250
    assert m.posicion == 750


def test_motor_cancelado_no_se_mueve():
    m = MotorSimulado(Eje("az"), escala_tiempo=0)
    cancelar = threading.Event()
    cancelar.set()
    assert m.mover(500, cancelar) == 0
    assert m.posicion == 0


def test_fin_de_carrera_detiene_el_motor():
    m = MotorSimulado(Eje("alt"), escala_tiempo=0)
    m.fin_carrera_activo = True
    with pytest.raises(FinDeCarrera):
        m.mover(100)

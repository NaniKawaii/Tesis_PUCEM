import pytest

from telescopio.prueba_banco import main
from telescopio.sensores import angulo_as5600, entero16, estado_iman_as5600, inclinacion


@pytest.mark.parametrize("alto,bajo,grados", [(0, 0, 0.0), (0x08, 0x00, 180.0), (0x0F, 0xFF, 359.912), (0xF4, 0x00, 90.0)])
def test_angulo_as5600(alto, bajo, grados):
    # los 4 bits altos del primer registro se ignoran (0xF4 → 0x400 = 1024 cuentas = 90°)
    assert angulo_as5600(alto, bajo) == pytest.approx(grados, abs=1e-3)


def test_estado_iman():
    assert estado_iman_as5600(0x20) == "imán correcto"
    assert "sin imán" in estado_iman_as5600(0x00)
    assert "débil" in estado_iman_as5600(0x30)
    assert "fuerte" in estado_iman_as5600(0x28)


def test_entero16_con_signo():
    assert entero16(0x40, 0x00) == 16384
    assert entero16(0xC0, 0x00) == -16384


def test_inclinacion():
    assert inclinacion(0, 0, 1) == pytest.approx((0, 0, 0), abs=1e-9)
    alabeo, cabeceo, total = inclinacion(0, 0.0175, 1)  # ≈ 1° hacia un lado
    assert alabeo == pytest.approx(1.0, abs=0.01) and total == pytest.approx(1.0, abs=0.01)


def test_prueba_de_motor_en_simulacion(capsys):
    main(["motor", "alt", "--grados", "1", "--simulacion"])
    salida = capsys.readouterr().out
    assert "Volviendo" in salida and "micropasos por grado" in salida

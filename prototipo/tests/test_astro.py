from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from telescopio.astro import OBJETOS, Efemerides
from telescopio.config import Config

cfg = Config()
pytestmark = pytest.mark.skipif(not (Path(cfg.dir_efemerides) / "de421.bsp").exists(),
                                reason="falta de421.bsp (se descarga al ejecutar el servidor)")

INSTANTE = datetime(2026, 1, 10, 3, 0, tzinfo=timezone.utc)


def test_todos_los_objetos_tienen_posicion_valida():
    ef = Efemerides(cfg.dir_efemerides, cfg.sitio)
    for p in ef.todos(INSTANTE):
        assert -90 <= p.altitud <= 90
        assert 0 <= p.azimut < 360
        assert type(p.altitud) is float and type(p.azimut) is float  # serializable a JSON
    assert {p.objeto for p in ef.todos(INSTANTE)} == set(OBJETOS)


def test_la_tierra_rota_unos_15_grados_por_hora():
    # Cerca del ecuador un objeto cambia de altitud o azimut notablemente en 1 hora
    ef = Efemerides(cfg.dir_efemerides, cfg.sitio)
    a = ef.altaz("Júpiter", INSTANTE)
    b = ef.altaz("Júpiter", INSTANTE + timedelta(hours=1))
    assert abs(a.altitud - b.altitud) + abs(a.azimut - b.azimut) > 5

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from telescopio.astro import PosicionAltAz  # noqa: E402
from telescopio.config import Config, Sitio  # noqa: E402
from telescopio.montura import Montura  # noqa: E402
from telescopio.sistema import Telescopio, crear_motores  # noqa: E402


class EfemeridesFalsas:
    """Posiciones fijas y controlables para que las pruebas no dependan de la hora."""

    def __init__(self):
        self.sitio = Sitio()
        self.posiciones = {"Júpiter": (120.0, 45.0), "Saturno": (250.0, 30.0), "Marte": (10.0, -20.0)}

    def actualizar_sitio(self, sitio):
        self.sitio = sitio

    def altaz(self, objeto, instante=None):
        az, alt = self.posiciones[objeto]
        return PosicionAltAz(objeto, alt, az, 5.0, "2026-01-01T00:00:00Z")

    def todos(self, instante=None):
        return [self.altaz(o) for o in self.posiciones]


@pytest.fixture
def cfg(tmp_path):
    c = Config()
    c.registro_csv = str(tmp_path / "registro.csv")
    c.modelo_ia = str(tmp_path / "modelo.joblib")
    c.intervalo_seguimiento_s = 0.01
    return c


@pytest.fixture
def montura(cfg):
    return Montura(cfg, *crear_motores(cfg, escala_tiempo=0))


@pytest.fixture
def telescopio(cfg, montura):
    t = Telescopio(cfg, montura=montura, efemerides=EfemeridesFalsas())
    yield t
    t.cerrar()

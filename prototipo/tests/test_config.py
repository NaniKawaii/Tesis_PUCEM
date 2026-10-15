import json

import pytest

from telescopio.config import cargar_config


def test_config_ejemplo_con_reduccion():
    c = cargar_config("config.ejemplo.json")
    assert c.simulacion is False
    assert c.az.reduccion == 5.0 and c.az.resolucion_arcmin == pytest.approx(1.35)
    assert c.az.min_grados == -270  # los valores no indicados conservan el defecto


def test_clave_mal_escrita_da_error(tmp_path):
    ruta = tmp_path / "c.json"
    ruta.write_text(json.dumps({"az": {"reducion": 5}}))
    with pytest.raises(ValueError, match="reducion"):
        cargar_config(ruta)

import numpy as np
import pytest
from fastapi.testclient import TestClient

from telescopio.correccion import error_en_cielo_arcmin
from telescopio.servidor import crear_app


@pytest.fixture
def cliente(telescopio):
    with TestClient(crear_app(telescopio=telescopio)) as c:
        yield c


def esperar_goto(telescopio):
    if telescopio._hilo_goto:
        telescopio._hilo_goto.join(timeout=10)


def test_interfaz_y_estado(cliente):
    assert "Telescopio" in cliente.get("/").text
    e = cliente.get("/api/estado").json()
    assert e["referenciada"] is False and e["simulacion"] is True


def test_objetos_visibles_primero(cliente):
    lista = cliente.get("/api/objetos").json()
    assert [o["objeto"] for o in lista][:2] == ["Júpiter", "Saturno"]
    assert lista[-1] == {"objeto": "Marte", "altitud": -20.0, "azimut": 10.0, "visible": False}


def test_goto_requiere_referencia_y_objeto_visible(cliente):
    r = cliente.post("/api/goto", json={"objeto": "Júpiter"})
    assert r.status_code == 400 and "referencie" in r.json()["detail"]
    cliente.post("/api/referenciar", json={})
    r = cliente.post("/api/goto", json={"objeto": "Marte"})
    assert r.status_code == 400 and "por debajo" in r.json()["detail"]


def test_flujo_completo_goto_centrado_e_ia(cliente, telescopio):
    """Simula una noche de pruebas: la montura tiene un error sistemático que el
    usuario corrige con las flechas; tras varios registros se entrena la IA."""
    cliente.post("/api/referenciar", json={})
    rng = np.random.default_rng(0)
    ef = telescopio.efemerides

    def error_real(az, alt):  # desnivel + desfase de índice (grados)
        return 0.3 + 0.2 * np.sin(np.radians(az)), -0.2 + 0.15 * np.cos(np.radians(az))

    for _ in range(15):
        az, alt = rng.uniform(0, 360), rng.uniform(20, 80)
        ef.posiciones["Júpiter"] = (az, alt)
        assert cliente.post("/api/goto", json={"objeto": "Júpiter", "usar_ia": False}).status_code == 200
        esperar_goto(telescopio)
        e_az, e_alt = error_real(az, alt)
        cliente.post("/api/ajustar", json={"eje": "az", "grados": e_az})
        cliente.post("/api/ajustar", json={"eje": "alt", "grados": e_alt})
        fila = cliente.post("/api/centrado").json()
        assert fila["d_az"] == pytest.approx(e_az, abs=0.12)
        # Tolerancia: con acople directo cada micropaso equivale a 6,75′
        assert fila["error_arcmin"] == pytest.approx(error_en_cielo_arcmin(e_az, e_alt, alt), abs=8)

    assert cliente.get("/api/estado").json()["registros"] == 15
    resumen = cliente.post("/api/ia/entrenar", json={"tipo": "lineal"}).json()
    assert resumen["rms_con_arcmin"] < resumen["rms_sin_arcmin"]

    # Con el modelo activo, el GoTo ya incluye la corrección aprendida
    ef.posiciones["Júpiter"] = (90.0, 50.0)
    objetivo = cliente.post("/api/goto", json={"objeto": "Júpiter", "usar_ia": True}).json()
    esperar_goto(telescopio)
    assert objetivo["correccion_ia"] == "lineal"
    assert objetivo["az_comandado"] - 90.0 == pytest.approx(error_real(90, 50)[0], abs=0.1)


def test_seguimiento_y_detener(cliente, telescopio):
    cliente.post("/api/referenciar", json={})
    assert cliente.post("/api/seguimiento", json={"activo": True}).status_code == 400
    cliente.post("/api/goto", json={"objeto": "Saturno"})
    esperar_goto(telescopio)
    assert cliente.post("/api/seguimiento", json={"activo": True}).json()["siguiendo"] is True
    assert cliente.post("/api/detener", json={}).json()["siguiendo"] is False

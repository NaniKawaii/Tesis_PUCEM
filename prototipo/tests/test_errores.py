import numpy as np
import pytest

from telescopio.errores import (
    ALT_MAX_MODELO,
    TERMINOS,
    TERMINOS_SESION,
    ParametrosError,
    ajustar,
    error_en_cielo_arcmin,
    error_lineal,
    matriz_diseno,
    rms_en_cielo,
    sentido,
)


def _muestra(n=400, semilla=7):
    rng = np.random.default_rng(semilla)
    return {
        "az": rng.uniform(0, 360, n),
        "alt": rng.uniform(15, 80, n),
        "sentido_az": rng.choice([-1.0, 1.0], n),
        "sentido_alt": rng.choice([-1.0, 1.0], n),
        "temperatura": rng.uniform(15, 35, n),
    }


PARAMETROS = ParametrosError(
    indice_az=12.0, indice_alt=-7.0, desnivel_ns=20.0, desnivel_eo=-15.0,
    colimacion=5.0, no_perpendicularidad=-9.0, flexion=11.0,
    holgura_az=4.0, holgura_alt=6.0, deriva_az=0.3, deriva_alt=-0.2,
)


def test_sin_parametros_no_hay_error():
    d_az, d_alt = error_lineal([0, 90, 180], [10, 40, 70], ParametrosError())
    assert np.allclose(d_az, 0) and np.allclose(d_alt, 0)


def test_ajustar_recupera_los_parametros_que_generaron_el_error():
    """El generador y el ajuste comparten definición, así que el ida y vuelta es exacto."""
    m = _muestra()
    d_az, d_alt = error_lineal(m["az"], m["alt"], PARAMETROS, sentido_az=m["sentido_az"],
                               sentido_alt=m["sentido_alt"], temperatura=m["temperatura"])
    aj = ajustar(m["az"], m["alt"], d_az, d_alt, sentido_az=m["sentido_az"],
                 sentido_alt=m["sentido_alt"], temperatura=m["temperatura"])

    for termino in TERMINOS:
        assert getattr(aj.parametros, termino) == pytest.approx(
            getattr(PARAMETROS, termino), abs=1e-6), termino
    assert aj.rms_despues < 1e-9
    assert aj.mejora == pytest.approx(1.0, abs=1e-9)
    assert aj.n == len(m["az"])


def test_alineacion_de_sesion_con_tres_puntos():
    """Cuatro términos de sesión se resuelven con 3 puntos: dos ecuaciones por punto."""
    sesion = ParametrosError(indice_az=35.0, indice_alt=-12.0,
                             desnivel_ns=25.0, desnivel_eo=-18.0)
    az = np.array([30.0, 150.0, 260.0])
    alt = np.array([25.0, 55.0, 40.0])
    d_az, d_alt = error_lineal(az, alt, sesion)

    aj = ajustar(az, alt, d_az, d_alt, TERMINOS_SESION)

    for termino in TERMINOS_SESION:
        assert getattr(aj.parametros, termino) == pytest.approx(
            getattr(sesion, termino), abs=1e-6), termino
    assert aj.terminos == TERMINOS_SESION


def test_ajustar_exige_puntos_suficientes():
    with pytest.raises(ValueError, match="al menos"):
        ajustar([10.0], [20.0], [1.0], [1.0], TERMINOS_SESION)


def test_ajustar_exige_largos_iguales():
    with pytest.raises(ValueError, match="mismo largo"):
        ajustar([10.0, 20.0], [20.0, 30.0], [1.0], [1.0, 2.0], TERMINOS_SESION)


def test_error_en_cielo_pesa_menos_cerca_del_cenit():
    # En el horizonte, un error de azimut se ve entero.
    assert error_en_cielo_arcmin(10.0, 0.0, 0.0) == pytest.approx(10.0)
    # A 60° de altitud, cos(60°) = 0,5: el mismo error de eje se ve a la mitad.
    assert error_en_cielo_arcmin(10.0, 0.0, 60.0) == pytest.approx(5.0)
    # El error de altitud no depende de la altitud.
    assert error_en_cielo_arcmin(0.0, 4.0, 75.0) == pytest.approx(4.0)


def test_el_modelo_no_se_dispara_en_el_cenit():
    """A ~1° S la Luna pasa muy cerca del cenit: tan(alt) no puede volverse infinito."""
    d_az, d_alt = error_lineal([0.0, 45.0], [89.999, 90.0], PARAMETROS)
    assert np.all(np.isfinite(d_az)) and np.all(np.isfinite(d_alt))

    # Por encima del tope, el modelo se evalúa como si estuviera en el tope.
    en_el_tope, _ = error_lineal([45.0], [ALT_MAX_MODELO], PARAMETROS)
    mas_arriba, _ = error_lineal([45.0], [ALT_MAX_MODELO + 3], PARAMETROS)
    assert mas_arriba == pytest.approx(en_el_tope)


def test_matriz_de_diseno_tiene_rango_completo():
    """Si alguna columna fuera combinación de otras, el ajuste no sería único."""
    m = _muestra(n=120, semilla=3)
    A = matriz_diseno(m["az"], m["alt"], TERMINOS, sentido_az=m["sentido_az"],
                      sentido_alt=m["sentido_alt"], temperatura=m["temperatura"])
    assert A.shape == (2 * 120, len(TERMINOS))
    assert np.linalg.matrix_rank(A) == len(TERMINOS)


def test_la_holgura_cambia_de_signo_con_el_sentido_de_giro():
    p = ParametrosError(holgura_az=8.0)
    subiendo, _ = error_lineal([100.0], [45.0], p, sentido_az=1.0)
    bajando, _ = error_lineal([100.0], [45.0], p, sentido_az=-1.0)
    assert subiendo == pytest.approx(4.0)
    assert bajando == pytest.approx(-4.0)
    quieto, _ = error_lineal([100.0], [45.0], p, sentido_az=0.0)
    assert quieto == pytest.approx(0.0)


def test_la_deriva_termica_se_mide_contra_la_temperatura_de_referencia():
    p = ParametrosError(deriva_alt=0.4)
    _, en_referencia = error_lineal([0.0], [45.0], p, temperatura=25.0)
    _, diez_grados_menos = error_lineal([0.0], [45.0], p, temperatura=15.0)
    assert en_referencia == pytest.approx(0.0)
    assert diez_grados_menos == pytest.approx(-4.0)


def test_sentido_y_rms():
    assert list(sentido([10, 20, 30], [12, 20, 25])) == [1.0, 0.0, -1.0]
    assert rms_en_cielo([3.0, 4.0], [4.0, 3.0], [0.0, 0.0]) == pytest.approx(5.0)
    assert rms_en_cielo([], [], []) == 0.0


def test_solo_deja_los_terminos_pedidos():
    recortado = PARAMETROS.solo(TERMINOS_SESION)
    assert recortado.indice_az == PARAMETROS.indice_az
    assert recortado.flexion == 0.0

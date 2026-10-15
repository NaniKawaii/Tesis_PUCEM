"""Control de los motores paso a paso.

- `perfil_trapezoidal`: genera los tiempos entre pasos para arrancar y frenar
  suavemente (rampa de aceleración), evitando que el motor pierda pasos.
- `MotorSimulado`: se usa en la PC para desarrollar sin hardware.
- `MotorTB6600`: genera las señales STEP/DIR/ENA desde los GPIO de la Raspberry Pi.
"""

from __future__ import annotations

import threading
import time
from abc import ABC, abstractmethod

import numpy as np

from .config import Eje


class FinDeCarrera(Exception):
    """El interruptor de límite del eje se activó durante un movimiento."""


def perfil_trapezoidal(n_pasos: int, vel_max: float, aceleracion: float) -> np.ndarray:
    """Retardo (s) antes de cada paso para un movimiento de `n_pasos`.

    La velocidad crece como sqrt(2·a·d) al arrancar, se limita a `vel_max` y
    decrece de forma simétrica al frenar. Si el movimiento es corto, el perfil
    queda triangular (nunca alcanza la velocidad máxima).
    """
    if n_pasos <= 0:
        return np.empty(0)
    k = np.arange(n_pasos, dtype=float)
    v_arranque = np.sqrt(2.0 * aceleracion * (k + 1))
    v_frenado = np.sqrt(2.0 * aceleracion * (n_pasos - k))
    velocidad = np.minimum(np.minimum(v_arranque, v_frenado), vel_max)
    return 1.0 / velocidad


class Motor(ABC):
    def __init__(self, eje: Eje):
        self.eje = eje
        self.posicion = 0  # micropasos desde la referencia
        self.en_movimiento = False

    def mover(self, pasos: int, cancelar: threading.Event | None = None) -> int:
        """Mueve `pasos` micropasos (con signo). Bloquea hasta terminar.

        Devuelve los pasos realmente dados (puede ser menos si se cancela).
        """
        if pasos == 0:
            return 0
        cancelar = cancelar or threading.Event()
        sentido = 1 if pasos > 0 else -1
        retardos = perfil_trapezoidal(abs(pasos), self.eje.vel_max, self.eje.aceleracion)
        self.en_movimiento = True
        dados = 0
        try:
            self._preparar(sentido)
            for dados, espera in self._ejecutar(retardos, cancelar, sentido):
                pass
        finally:
            self.en_movimiento = False
            self._finalizar()
        return dados * sentido

    @abstractmethod
    def _preparar(self, sentido: int) -> None: ...

    @abstractmethod
    def _ejecutar(self, retardos: np.ndarray, cancelar: threading.Event, sentido: int):
        """Generador: da los pasos y produce (pasos_dados, retardo)."""

    def _finalizar(self) -> None:
        pass

    def cerrar(self) -> None:
        pass


class MotorSimulado(Motor):
    """Motor virtual. `escala_tiempo=1` imita la duración real; 0 es instantáneo."""

    def __init__(self, eje: Eje, escala_tiempo: float = 1.0):
        super().__init__(eje)
        self.escala_tiempo = escala_tiempo
        self.fin_carrera_activo = False  # se puede forzar en pruebas

    def _preparar(self, sentido: int) -> None:
        pass

    def _ejecutar(self, retardos, cancelar, sentido):
        acumulado = 0.0
        for i, espera in enumerate(retardos, start=1):
            if cancelar.is_set():
                return
            if self.fin_carrera_activo:
                raise FinDeCarrera(self.eje.nombre)
            self.posicion += sentido
            acumulado += espera * self.escala_tiempo
            if acumulado >= 0.02:  # dormir en bloques de 20 ms
                time.sleep(acumulado)
                acumulado = 0.0
            yield i, espera
        if acumulado:
            time.sleep(acumulado)


class MotorTB6600(Motor):
    """Driver TB6600 conectado a la Raspberry Pi (entradas PUL/DIR/ENA).

    Importa gpiozero solo cuando se usa, para que el resto del código funcione
    en una PC normal.
    """

    ANCHO_PULSO_S = 5e-6  # el TB6600 necesita pulsos de al menos ~2,5 µs

    def __init__(self, eje: Eje):
        super().__init__(eje)
        from gpiozero import Button, DigitalOutputDevice

        if eje.pin_step is None or eje.pin_dir is None:
            raise ValueError(f"Faltan pines STEP/DIR para el eje {eje.nombre}")
        self._step = DigitalOutputDevice(eje.pin_step)
        self._dir = DigitalOutputDevice(eje.pin_dir)
        # ENA del TB6600: en alto deshabilita el driver (motor libre)
        self._ena = DigitalOutputDevice(eje.pin_enable) if eje.pin_enable is not None else None
        self._limite = (Button(eje.pin_fin_carrera, pull_up=True)
                        if eje.pin_fin_carrera is not None else None)
        self.habilitar(True)

    def habilitar(self, activo: bool) -> None:
        if self._ena is not None:
            self._ena.value = 0 if activo else 1

    def _preparar(self, sentido: int) -> None:
        adelante = (sentido > 0) != self.eje.invertido
        self._dir.value = 1 if adelante else 0
        time.sleep(1e-5)  # tiempo de preparación de DIR antes del primer pulso

    @staticmethod
    def _esperar_hasta(instante: float) -> None:
        # time.sleep no es preciso por debajo de ~1 ms; se completa con espera activa
        restante = instante - time.perf_counter()
        if restante > 0.002:
            time.sleep(restante - 0.001)
        while time.perf_counter() < instante:
            pass

    def _ejecutar(self, retardos, cancelar, sentido):
        siguiente = time.perf_counter()
        for i, espera in enumerate(retardos, start=1):
            if cancelar.is_set():
                return
            if self._limite is not None and self._limite.is_pressed:
                raise FinDeCarrera(self.eje.nombre)
            siguiente += espera
            self._esperar_hasta(siguiente - self.ANCHO_PULSO_S)
            self._step.on()
            self._esperar_hasta(siguiente)
            self._step.off()
            self.posicion += sentido
            yield i, espera

    def cerrar(self) -> None:
        self.habilitar(False)
        for dispositivo in (self._step, self._dir, self._ena, self._limite):
            if dispositivo is not None:
                dispositivo.close()

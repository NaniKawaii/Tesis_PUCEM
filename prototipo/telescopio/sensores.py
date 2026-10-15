"""Sensores I²C: encoder magnético AS5600 y acelerómetro del GY-91 (MPU9250).

Las funciones de conversión son puras (se prueban en la PC); las clases que
leen el bus importan smbus2 solo al usarse, en la Raspberry Pi.
"""

from __future__ import annotations

import math

DIRECCIONES_ESPERADAS = {
    0x36: "AS5600 (encoder de altitud)",
    0x68: "MPU9250 (acelerómetro del GY-91)",
    0x76: "BMP280 (barómetro del GY-91)",
    0x77: "BMP280 (barómetro del GY-91, dirección alternativa)",
}


# ----------------------------------------------------------------- conversiones
def angulo_as5600(alto: int, bajo: int) -> float:
    """Registros RAW ANGLE (0x0C, 0x0D) → grados (0–360). Resolución de 12 bits."""
    crudo = ((alto & 0x0F) << 8) | bajo
    return crudo * 360.0 / 4096.0


def estado_iman_as5600(status: int) -> str:
    """Registro STATUS (0x0B): indica si el imán está bien colocado."""
    if not status & 0x20:
        return "sin imán: acerca el imán diametral al chip (1–3 mm)"
    if status & 0x10:
        return "imán demasiado débil o lejos"
    if status & 0x08:
        return "imán demasiado fuerte o cerca"
    return "imán correcto"


def entero16(alto: int, bajo: int) -> int:
    valor = (alto << 8) | bajo
    return valor - 65536 if valor & 0x8000 else valor


def inclinacion(ax: float, ay: float, az: float) -> tuple[float, float, float]:
    """Alabeo, cabeceo e inclinación total (grados) a partir de la gravedad medida.

    Con el sensor plano y el trípode nivelado, los tres valores son ≈ 0.
    """
    alabeo = math.degrees(math.atan2(ay, az))
    cabeceo = math.degrees(math.atan2(-ax, math.hypot(ay, az)))
    norma = math.sqrt(ax * ax + ay * ay + az * az)
    total = math.degrees(math.acos(max(-1.0, min(1.0, az / norma)))) if norma else float("nan")
    return alabeo, cabeceo, total


# ----------------------------------------------------------------- lectura del bus
def abrir_bus(numero: int = 1):
    from smbus2 import SMBus

    return SMBus(numero)


def escanear_i2c(bus) -> list[int]:
    encontrados = []
    for direccion in range(0x03, 0x78):
        try:
            bus.read_byte(direccion)
            encontrados.append(direccion)
        except OSError:
            pass
    return encontrados


class AS5600:
    DIRECCION = 0x36

    def __init__(self, bus):
        self.bus = bus

    def estado(self) -> str:
        return estado_iman_as5600(self.bus.read_byte_data(self.DIRECCION, 0x0B))

    def angulo(self) -> float:
        alto, bajo = self.bus.read_i2c_block_data(self.DIRECCION, 0x0C, 2)
        return angulo_as5600(alto, bajo)


class Acelerometro:
    """MPU9250 en rango de ±2 g (16384 cuentas por g)."""

    DIRECCION = 0x68

    def __init__(self, bus):
        self.bus = bus
        self.bus.write_byte_data(self.DIRECCION, 0x6B, 0x00)  # salir del modo de reposo

    def gravedad(self) -> tuple[float, float, float]:
        d = self.bus.read_i2c_block_data(self.DIRECCION, 0x3B, 6)
        return tuple(entero16(d[i], d[i + 1]) / 16384.0 for i in (0, 2, 4))

    def inclinacion(self, muestras: int = 20) -> tuple[float, float, float]:
        suma = [0.0, 0.0, 0.0]
        for _ in range(muestras):
            for i, v in enumerate(self.gravedad()):
                suma[i] += v
        return inclinacion(*(s / muestras for s in suma))

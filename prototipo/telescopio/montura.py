"""Cinemática de la montura altacimutal: convierte ángulos en pasos de motor,
respeta los límites mecánicos y mueve ambos ejes a la vez."""

from __future__ import annotations

import threading

from .config import Config, Eje
from .motores import Motor


def normalizar_360(grados: float) -> float:
    return grados % 360.0


def diferencia_angular(a: float, b: float) -> float:
    """a − b llevado al intervalo [−180, 180)."""
    return (a - b + 180.0) % 360.0 - 180.0


class Montura:
    def __init__(self, cfg: Config, motor_az: Motor, motor_alt: Motor):
        self.cfg = cfg
        self.motores = {"az": motor_az, "alt": motor_alt}
        self.referenciada = False
        self._cancelar = threading.Event()
        self._candado = threading.Lock()

    def eje(self, nombre: str) -> Eje:
        return self.motores[nombre].eje

    def angulo(self, nombre: str) -> float:
        """Ángulo mecánico actual del eje (sin normalizar)."""
        return self.motores[nombre].posicion / self.eje(nombre).pasos_por_grado

    def posicion(self) -> tuple[float, float]:
        """(azimut 0–360, altitud) hacia donde apunta la montura."""
        return normalizar_360(self.angulo("az")), self.angulo("alt")

    @property
    def en_movimiento(self) -> bool:
        return any(m.en_movimiento for m in self.motores.values())

    def referenciar(self, az: float = 0.0, alt: float = 0.0) -> None:
        """Declara la posición actual como conocida.

        Procedimiento en campo: nivelar el trípode, girar el tubo hacia el norte
        con la marca de referencia y dejarlo horizontal; luego llamar con (0, 0).
        """
        for nombre, angulo in (("az", az), ("alt", alt)):
            self.motores[nombre].posicion = round(angulo * self.eje(nombre).pasos_por_grado)
        self.referenciada = True

    def az_mecanico(self, az: float) -> float:
        """Elige el ángulo equivalente (az + k·360) más cercano dentro del rango
        mecánico, para no enredar los cables ni girar de más."""
        eje, actual = self.eje("az"), self.angulo("az")
        candidatos = [az + k * 360.0 for k in range(-2, 3)]
        validos = [c for c in candidatos if eje.min_grados <= c <= eje.max_grados]
        if not validos:
            raise ValueError(f"Azimut {az:.2f}° fuera del rango mecánico")
        return min(validos, key=lambda c: abs(c - actual))

    def validar_altitud(self, alt: float) -> None:
        eje = self.eje("alt")
        if not eje.min_grados <= alt <= eje.max_grados:
            raise ValueError(f"Altitud {alt:.2f}° fuera del rango mecánico "
                             f"[{eje.min_grados}, {eje.max_grados}]")

    def mover_a(self, az: float, alt: float) -> None:
        """Mueve ambos ejes simultáneamente hasta (az, alt). Bloquea."""
        if not self.referenciada:
            raise RuntimeError("La montura no está referenciada")
        self.validar_altitud(alt)
        destino = {"az": self.az_mecanico(normalizar_360(az)), "alt": alt}
        with self._candado:
            self._cancelar.clear()
            pasos = {n: round(destino[n] * self.eje(n).pasos_por_grado) - self.motores[n].posicion
                     for n in self.motores}
            self._mover_simultaneo(pasos)

    def mover_relativo(self, nombre: str, grados: float) -> None:
        """Ajuste fino de un eje (botones de flecha de la interfaz)."""
        if nombre == "alt":
            self.validar_altitud(self.angulo("alt") + grados)
        else:
            eje = self.eje("az")
            if not eje.min_grados <= self.angulo("az") + grados <= eje.max_grados:
                raise ValueError("Ajuste fuera del rango mecánico de azimut")
        with self._candado:
            self._cancelar.clear()
            self._mover_simultaneo({nombre: round(grados * self.eje(nombre).pasos_por_grado)})

    def _mover_simultaneo(self, pasos: dict[str, int]) -> None:
        errores: list[Exception] = []

        def trabajar(nombre: str, n: int):
            try:
                self.motores[nombre].mover(n, self._cancelar)
            except Exception as e:  # p. ej. FinDeCarrera
                self._cancelar.set()  # si un eje falla, se detiene el otro
                errores.append(e)

        hilos = [threading.Thread(target=trabajar, args=(n, p)) for n, p in pasos.items() if p]
        for h in hilos:
            h.start()
        for h in hilos:
            h.join()
        if errores:
            raise errores[0]

    def detener(self) -> None:
        self._cancelar.set()

    def cerrar(self) -> None:
        self.detener()
        for m in self.motores.values():
            m.cerrar()

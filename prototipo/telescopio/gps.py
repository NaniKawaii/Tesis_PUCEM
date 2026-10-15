"""Lectura del módulo GPS u-blox NEO-6M (NMEA por UART).

Entrega la ubicación del observador y la diferencia entre la hora GPS y el
reloj de la Raspberry Pi (que no tiene batería de reloj y puede estar
desfasada si no hay internet).
"""

from __future__ import annotations

import threading
from datetime import datetime, timedelta, timezone

from .config import Sitio


class LectorGPS:
    def __init__(self, puerto: str, baudios: int = 9600):
        self.puerto, self.baudios = puerto, baudios
        self.sitio: Sitio | None = None
        self.desfase = timedelta(0)  # hora GPS − hora del sistema
        self.con_senal = False
        self.ultimo_error: str | None = None
        self._detener = threading.Event()
        self._hilo = threading.Thread(target=self._bucle, daemon=True)

    def iniciar(self) -> None:
        self._hilo.start()

    def detener(self) -> None:
        self._detener.set()

    def procesar(self, linea: str) -> None:
        """Interpreta una sentencia NMEA ($GPGGA o $GPRMC)."""
        import pynmea2

        try:
            msg = pynmea2.parse(linea)
        except pynmea2.ParseError:
            return
        tipo = msg.sentence_type
        if tipo == "GGA":
            self.con_senal = int(msg.gps_qual or 0) > 0
            if self.con_senal:
                self.sitio = Sitio(msg.latitude, msg.longitude,
                                   float(msg.altitude or 0.0))
        elif tipo == "RMC" and msg.status == "A" and msg.datestamp and msg.timestamp:
            hora_gps = datetime.combine(msg.datestamp, msg.timestamp).replace(tzinfo=timezone.utc)
            self.desfase = hora_gps - datetime.now(timezone.utc)

    def _bucle(self) -> None:
        import serial

        while not self._detener.is_set():
            try:
                with serial.Serial(self.puerto, self.baudios, timeout=1) as puerto:
                    self.ultimo_error = None
                    while not self._detener.is_set():
                        linea = puerto.readline().decode("ascii", errors="ignore").strip()
                        if linea:
                            self.procesar(linea)
            except Exception as e:  # puerto desconectado: se mantiene la última ubicación
                self.con_senal = False
                self.ultimo_error = str(e)
                self._detener.wait(5)

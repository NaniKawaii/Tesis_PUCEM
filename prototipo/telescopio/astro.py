"""Cálculo de posiciones de planetas (altitud y azimut) con Skyfield.

Usa las efemérides DE421 del JPL. La primera vez que se ejecuta descarga el
archivo de421.bsp (~17 MB) en la carpeta de datos; después funciona sin internet.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from skyfield.api import Loader, wgs84

from .config import Sitio

# Nombre que ve el usuario -> nombre del cuerpo en las efemérides DE421
OBJETOS = {
    "Mercurio": "mercury",
    "Venus": "venus",
    "Luna": "moon",
    "Marte": "mars barycenter",
    "Júpiter": "jupiter barycenter",
    "Saturno": "saturn barycenter",
    "Urano": "uranus barycenter",
    "Neptuno": "neptune barycenter",
}


@dataclass
class PosicionAltAz:
    objeto: str
    altitud: float  # grados sobre el horizonte
    azimut: float  # grados desde el norte hacia el este (0–360)
    distancia_ua: float
    instante_utc: str


class Efemerides:
    def __init__(self, dir_datos: str, sitio: Sitio):
        cargador = Loader(dir_datos, verbose=False)
        self._ts = cargador.timescale()
        self._eph = cargador("de421.bsp")
        self._tierra = self._eph["earth"]
        self.actualizar_sitio(sitio)

    def actualizar_sitio(self, sitio: Sitio) -> None:
        self.sitio = sitio
        self._observador = self._tierra + wgs84.latlon(
            sitio.latitud, sitio.longitud, elevation_m=sitio.elevacion_m)

    def _tiempo(self, instante: datetime | None):
        return self._ts.now() if instante is None else self._ts.from_datetime(instante)

    def altaz(self, objeto: str, instante: datetime | None = None) -> PosicionAltAz:
        """Posición aparente del objeto (con refracción atmosférica estándar)."""
        if objeto not in OBJETOS:
            raise KeyError(f"Objeto no soportado: {objeto}")
        t = self._tiempo(instante)
        aparente = self._observador.at(t).observe(self._eph[OBJETOS[objeto]]).apparent()
        alt, az, dist = aparente.altaz(pressure_mbar="standard")
        # float(): Skyfield devuelve tipos de numpy que la API no sabe convertir a JSON
        return PosicionAltAz(objeto, float(alt.degrees), float(az.degrees), float(dist.au),
                             t.utc_iso())

    def todos(self, instante: datetime | None = None) -> list[PosicionAltAz]:
        return [self.altaz(nombre, instante) for nombre in OBJETOS]

"""Configuración del sistema: sitio de observación, ejes de la montura y rutas.

Los valores por defecto corresponden a la proforma de la tesis
(Raspberry Pi 4, drivers TB6600, motores NEMA 23 con acople directo).
Se pueden sobrescribir con un archivo JSON (ver config.ejemplo.json).
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


@dataclass
class Sitio:
    """Ubicación del observador. Por defecto: Portoviejo, Manabí."""

    latitud: float = -1.0546
    longitud: float = -80.4545
    elevacion_m: float = 50.0


@dataclass
class Eje:
    """Parámetros mecánicos y eléctricos de un eje de la montura."""

    nombre: str
    pasos_por_vuelta: int = 200  # motor de 1,8° por paso
    micropasos: int = 16  # configurado con los switches del TB6600
    reduccion: float = 1.0  # vueltas del motor por vuelta del eje (1 = acople directo)
    invertido: bool = False
    min_grados: float = -180.0
    max_grados: float = 180.0
    vel_max: float = 1600.0  # micropasos por segundo
    aceleracion: float = 800.0  # micropasos por segundo²
    pin_step: int | None = None
    pin_dir: int | None = None
    pin_enable: int | None = None
    pin_fin_carrera: int | None = None

    @property
    def pasos_por_grado(self) -> float:
        return self.pasos_por_vuelta * self.micropasos * self.reduccion / 360.0

    @property
    def resolucion_arcmin(self) -> float:
        """Ángulo que avanza el eje con un micropaso, en minutos de arco."""
        return 60.0 / self.pasos_por_grado


def _eje_az() -> Eje:
    return Eje(nombre="azimut", min_grados=-270.0, max_grados=270.0,
               pin_step=17, pin_dir=27, pin_enable=22, pin_fin_carrera=5)


def _eje_alt() -> Eje:
    return Eje(nombre="altitud", min_grados=-5.0, max_grados=90.0,
               pin_step=23, pin_dir=24, pin_enable=25, pin_fin_carrera=6)


@dataclass
class Config:
    sitio: Sitio = field(default_factory=Sitio)
    az: Eje = field(default_factory=_eje_az)
    alt: Eje = field(default_factory=_eje_alt)
    simulacion: bool = True  # True = sin hardware (PC); False = Raspberry Pi
    altitud_minima: float = 10.0  # no apuntar por debajo de esta altitud (árboles, horizonte)
    intervalo_seguimiento_s: float = 5.0
    gps_puerto: str | None = None  # p. ej. "/dev/serial0" para el NEO-6M
    dir_efemerides: str = str(RAIZ / "datos")
    registro_csv: str = str(RAIZ / "datos" / "registro_apuntado.csv")
    modelo_ia: str = str(RAIZ / "datos" / "modelo_correccion.joblib")

    def a_dict(self) -> dict:
        return asdict(self)


def _construir(cls, datos: dict):
    nombres = {f.name for f in fields(cls)}
    desconocidas = set(datos) - nombres
    if desconocidas:
        raise ValueError(f"Claves desconocidas en la configuración de {cls.__name__}: {sorted(desconocidas)}")
    return datos


def cargar_config(ruta: str | Path | None = None) -> Config:
    """Carga la configuración por defecto y le aplica lo que haya en el JSON."""
    cfg = Config()
    if ruta is None:
        return cfg
    datos = json.loads(Path(ruta).read_text(encoding="utf-8"))
    if "sitio" in datos:
        cfg.sitio = Sitio(**_construir(Sitio, datos.pop("sitio")))
    for clave in ("az", "alt"):
        if clave in datos:
            base = asdict(getattr(cfg, clave))
            base.update(_construir(Eje, datos.pop(clave)))
            setattr(cfg, clave, Eje(**base))
    for clave, valor in _construir(Config, datos).items():
        setattr(cfg, clave, valor)
    return cfg

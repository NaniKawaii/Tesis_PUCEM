"""Registro de cada apuntado en un CSV: son los datos para la sección de
Resultados del artículo y para entrenar el modelo de corrección (IA)."""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass, fields
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class RegistroApuntado:
    fecha_utc: str
    sesion: str
    objeto: str
    az_objeto: float  # posición calculada del objeto (grados)
    alt_objeto: float
    correccion_ia: str  # "ninguna", "lineal" o "red_neuronal"
    az_comandado: float  # adonde se mandó la montura tras aplicar la corrección
    alt_comandado: float
    az_centrado: float  # posición de la montura cuando el usuario confirmó el centrado
    alt_centrado: float
    d_az: float  # ajuste que hizo falta respecto de la posición del objeto (grados)
    d_alt: float
    error_arcmin: float  # error en el cielo antes del ajuste manual
    tiempo_goto_s: float

    @staticmethod
    def ahora() -> str:
        return datetime.now(timezone.utc).isoformat(timespec="seconds")


CAMPOS = [f.name for f in fields(RegistroApuntado)]


def guardar(ruta: str | Path, registro: RegistroApuntado) -> None:
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    nuevo = not ruta.exists()
    with ruta.open("a", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=CAMPOS)
        if nuevo:
            escritor.writeheader()
        escritor.writerow(asdict(registro))


def leer(ruta: str | Path) -> list[dict]:
    ruta = Path(ruta)
    if not ruta.exists():
        return []
    with ruta.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))

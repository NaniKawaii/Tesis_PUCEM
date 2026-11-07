"""Registro en CSV: son los datos de la sección de Resultados y los que entrenan la IA.

Hay dos esquemas, a propósito:

- `RegistroApuntado`: **una fila por apuntado**, con el centrado manual del usuario. Es el del
  prototipo v0.1 y se conserva para no romper lo que ya funciona.
- `RegistroSeguimiento`: **una fila por segundo** durante el seguimiento, con los sensores.
  Es el del artículo (ver `docs/08-diseno-definitivo.md` §5).

`RegistroSeguimiento` lo escriben **dos** productores con el mismo formato: el simulador
(`simulador.py`) y el registrador real cuando haya cámara. Que el formato sea uno solo es lo
que permite que el pipeline de entrenamiento, validación y figuras sea también uno solo, y
que lo validado con datos sintéticos sirva tal cual con datos reales.
"""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass, fields
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


def _ahora_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class RegistroApuntado:
    """Esquema v0.1: un apuntado, centrado a mano por el usuario."""

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
        return _ahora_utc()


@dataclass
class RegistroSeguimiento:
    """Esquema del artículo: una fila por segundo durante el seguimiento.

    Unidades: grados para posiciones y ángulos; **minutos de arco** para los errores;
    grados Celsius y hectopascales para el ambiente.

    `d_az` y `d_alt` son el error medido **en coordenadas de eje**: la diferencia entre donde
    apuntó la montura de verdad y donde estaba el objeto. Es lo que mide la cámara. Para la
    separación real en el cielo está `error_cielo_arcmin`, que es la que se reporta.
    """

    fecha_utc: str
    sesion: str  # identificador de la noche: es la unidad de separación entre entrenamiento y prueba
    montura: str  # identificador de la montura (para datos sintéticos: cuál de las simuladas)
    origen: str  # "simulado" o "real"
    objeto: str
    # Verdad de referencia (Skyfield)
    az_objeto: float
    alt_objeto: float
    # Estado de la montura
    az_comandado: float
    alt_comandado: float
    sentido_az: float  # +1, -1 o 0: sentido del último giro, para la holgura
    sentido_alt: float
    encoder_alt: float  # ángulo medido por el AS5600 (grados); NaN si no hay
    # Ambiente
    temperatura_c: float
    presion_hpa: float
    inclinacion_ns: float  # desnivel del trípode leído por el GY-91 (grados)
    inclinacion_eo: float
    # Medición
    d_az: float  # minutos de arco, coordenadas de eje
    d_alt: float
    error_cielo_arcmin: float
    # Contexto
    fase_lunar: float  # fracción iluminada, de 0 a 1
    calidad: float  # calidad del fotograma, de 0 (inservible) a 1 (limpio)

    @staticmethod
    def ahora() -> str:
        return _ahora_utc()


CAMPOS = [f.name for f in fields(RegistroApuntado)]
CAMPOS_SEGUIMIENTO = [f.name for f in fields(RegistroSeguimiento)]


def guardar(ruta: str | Path, registro: RegistroApuntado) -> None:
    """Añade un apuntado al CSV (esquema v0.1)."""
    _anexar(ruta, [asdict(registro)], CAMPOS)


def guardar_seguimiento(ruta: str | Path,
                        registros: RegistroSeguimiento | Iterable[RegistroSeguimiento]) -> int:
    """Añade una o muchas filas de seguimiento al CSV. Devuelve cuántas escribió."""
    if isinstance(registros, RegistroSeguimiento):
        registros = [registros]
    filas = [asdict(r) for r in registros]
    _anexar(ruta, filas, CAMPOS_SEGUIMIENTO)
    return len(filas)


def _anexar(ruta: str | Path, filas: list[dict], campos: list[str]) -> None:
    if not filas:
        return
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    nuevo = not ruta.exists() or ruta.stat().st_size == 0
    with ruta.open("a", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=campos)
        if nuevo:
            escritor.writeheader()
        escritor.writerows(filas)


def leer(ruta: str | Path) -> list[dict]:
    """Lee cualquiera de los dos esquemas tal cual, sin convertir tipos."""
    ruta = Path(ruta)
    if not ruta.exists():
        return []
    with ruta.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def sesiones(filas: Iterable[dict]) -> list[str]:
    """Sesiones presentes, en orden de aparición.

    Es la agrupación que usa la validación dejando una noche fuera.
    """
    vistas: dict[str, None] = {}
    for fila in filas:
        vistas.setdefault(fila["sesion"], None)
    return list(vistas)

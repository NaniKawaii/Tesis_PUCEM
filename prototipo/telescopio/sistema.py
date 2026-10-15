"""Orquestador del telescopio: une efemérides, montura, IA, GPS y registro.

Flujo de un apuntado (y de una medición para el artículo):
  1. goto("Júpiter"): calcula alt/az, aplica la corrección de IA y mueve la montura.
  2. El usuario mira por el ocular/cámara y centra con ajustar().
  3. confirmar_centrado(): se guarda cuánto hubo que corregir (= error de apuntado).
"""

from __future__ import annotations

import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from . import registro
from .astro import OBJETOS, Efemerides
from .config import Config
from .correccion import ModeloCorreccion, error_en_cielo_arcmin, evaluar
from .gps import LectorGPS
from .montura import Montura, diferencia_angular
from .motores import Motor, MotorSimulado, MotorTB6600


def crear_motores(cfg: Config, escala_tiempo: float = 1.0) -> tuple[Motor, Motor]:
    if cfg.simulacion:
        return MotorSimulado(cfg.az, escala_tiempo), MotorSimulado(cfg.alt, escala_tiempo)
    return MotorTB6600(cfg.az), MotorTB6600(cfg.alt)


class Telescopio:
    def __init__(self, cfg: Config, montura: Montura | None = None,
                 efemerides: Efemerides | None = None):
        self.cfg = cfg
        self.montura = montura or Montura(cfg, *crear_motores(cfg))
        self.efemerides = efemerides or Efemerides(cfg.dir_efemerides, cfg.sitio)
        self.sesion = uuid.uuid4().hex[:8]
        self.mensaje = "Listo. Referencie la montura para comenzar."
        self.error: str | None = None
        self.objetivo: dict | None = None
        self._offset_manual = [0.0, 0.0]  # ajustes del usuario durante el seguimiento
        self._seguimiento = threading.Event()
        self._hilo_seguimiento: threading.Thread | None = None
        self._hilo_goto: threading.Thread | None = None
        self.modelo: ModeloCorreccion | None = None
        if Path(cfg.modelo_ia).exists():
            self.modelo = ModeloCorreccion.cargar(cfg.modelo_ia)
        self.gps: LectorGPS | None = None
        if cfg.gps_puerto:
            self.gps = LectorGPS(cfg.gps_puerto)
            self.gps.iniciar()

    # ----------------------------------------------------------------- tiempo y sitio
    def ahora(self) -> datetime:
        desfase = self.gps.desfase if self.gps else None
        instante = datetime.now(timezone.utc)
        return instante + desfase if desfase else instante

    def _actualizar_sitio_gps(self) -> None:
        if self.gps and self.gps.con_senal and self.gps.sitio:
            if self.gps.sitio != self.efemerides.sitio:
                self.efemerides.actualizar_sitio(self.gps.sitio)

    def posicion_objeto(self, objeto: str):
        self._actualizar_sitio_gps()
        return self.efemerides.altaz(objeto, self.ahora())

    def lista_objetos(self) -> list[dict]:
        self._actualizar_sitio_gps()
        instante = self.ahora()
        salida = []
        for p in self.efemerides.todos(instante):
            salida.append({"objeto": p.objeto, "altitud": round(p.altitud, 2),
                           "azimut": round(p.azimut, 2),
                           "visible": p.altitud >= self.cfg.altitud_minima})
        return sorted(salida, key=lambda d: (not d["visible"], -d["altitud"]))

    # ----------------------------------------------------------------- IA
    def _correccion(self, az: float, alt: float, usar: bool) -> tuple[float, float]:
        if usar and self.modelo is not None:
            return self.modelo.predecir(az, alt)
        return 0.0, 0.0

    def entrenar_ia(self, tipo: str) -> dict:
        filas = registro.leer(self.cfg.registro_csv)
        columnas = {c: [float(f[c]) for f in filas] for c in ("az_objeto", "alt_objeto", "d_az", "d_alt")}
        resultado = evaluar(tipo, columnas["az_objeto"], columnas["alt_objeto"],
                            columnas["d_az"], columnas["d_alt"]).resumen()
        self.modelo = ModeloCorreccion(tipo).entrenar(
            columnas["az_objeto"], columnas["alt_objeto"], columnas["d_az"], columnas["d_alt"])
        self.modelo.guardar(self.cfg.modelo_ia)
        return resultado

    def desactivar_ia(self) -> None:
        self.modelo = None
        Path(self.cfg.modelo_ia).unlink(missing_ok=True)

    # ----------------------------------------------------------------- movimientos
    def referenciar(self, az: float = 0.0, alt: float = 0.0) -> None:
        self.detener()
        self.montura.referenciar(az, alt)
        self.mensaje = f"Montura referenciada en az={az:.1f}°, alt={alt:.1f}°."

    def goto(self, objeto: str, usar_ia: bool = True, esperar: bool = False) -> dict:
        if objeto not in OBJETOS:
            raise KeyError(f"Objeto desconocido: {objeto}")
        if not self.montura.referenciada:
            raise RuntimeError("Primero referencie la montura (norte y nivelada).")
        if self.montura.en_movimiento:
            raise RuntimeError("La montura ya se está moviendo.")
        pos = self.posicion_objeto(objeto)
        if pos.altitud < self.cfg.altitud_minima:
            raise ValueError(f"{objeto} está a {pos.altitud:.1f}° de altitud, por debajo "
                             f"del mínimo ({self.cfg.altitud_minima}°).")
        self._seguimiento.clear()  # el seguimiento se reactiva sobre el nuevo objetivo
        usar_ia = usar_ia and self.modelo is not None
        d_az, d_alt = self._correccion(pos.azimut, pos.altitud, usar_ia)
        self._offset_manual = [0.0, 0.0]
        self.objetivo = {
            "objeto": objeto, "az_objeto": pos.azimut, "alt_objeto": pos.altitud,
            "az_comandado": pos.azimut + d_az, "alt_comandado": pos.altitud + d_alt,
            "correccion_ia": self.modelo.tipo if usar_ia else "ninguna",
            "prediccion": (d_az, d_alt), "tiempo_goto_s": None,
        }
        self.error = None
        self._hilo_goto = threading.Thread(target=self._ejecutar_goto, daemon=True)
        self._hilo_goto.start()
        if esperar:
            self._hilo_goto.join()
        return dict(self.objetivo)

    def _ejecutar_goto(self) -> None:
        obj = self.objetivo
        self.mensaje = f"Moviendo hacia {obj['objeto']}..."
        inicio = time.monotonic()
        try:
            self.montura.mover_a(obj["az_comandado"], obj["alt_comandado"])
        except Exception as e:
            self.error, self.mensaje = str(e), f"Movimiento interrumpido: {e}"
            return
        obj["tiempo_goto_s"] = round(time.monotonic() - inicio, 2)
        self.mensaje = (f"{obj['objeto']} alcanzado en {obj['tiempo_goto_s']} s. "
                        "Centre con las flechas y pulse «Objeto centrado».")

    def ajustar(self, eje: str, grados: float) -> None:
        if eje not in ("az", "alt"):
            raise ValueError("El eje debe ser 'az' o 'alt'")
        self.montura.mover_relativo(eje, grados)
        self._offset_manual[0 if eje == "az" else 1] += grados

    def confirmar_centrado(self) -> registro.RegistroApuntado:
        """Guarda el error de apuntado del último GoTo (datos para el artículo y la IA)."""
        if self.objetivo is None or self.objetivo["tiempo_goto_s"] is None:
            raise RuntimeError("No hay un GoTo terminado que confirmar.")
        obj = self.objetivo
        pos = self.posicion_objeto(obj["objeto"])  # el objeto se movió desde el GoTo
        az_m, alt_m = self.montura.posicion()
        d_az, d_alt = diferencia_angular(az_m, pos.azimut), alt_m - pos.altitud
        pred_az, pred_alt = obj["prediccion"]
        fila = registro.RegistroApuntado(
            fecha_utc=registro.RegistroApuntado.ahora(), sesion=self.sesion,
            objeto=obj["objeto"], az_objeto=round(pos.azimut, 4), alt_objeto=round(pos.altitud, 4),
            correccion_ia=obj["correccion_ia"],
            az_comandado=round(obj["az_comandado"], 4), alt_comandado=round(obj["alt_comandado"], 4),
            az_centrado=round(az_m, 4), alt_centrado=round(alt_m, 4),
            d_az=round(d_az, 4), d_alt=round(d_alt, 4),
            error_arcmin=round(float(error_en_cielo_arcmin(d_az - pred_az, d_alt - pred_alt,
                                                            pos.altitud)), 2),
            tiempo_goto_s=obj["tiempo_goto_s"])
        registro.guardar(self.cfg.registro_csv, fila)
        self.mensaje = f"Registrado: error de apuntado {fila.error_arcmin} arcmin."
        return fila

    # ----------------------------------------------------------------- seguimiento
    def seguimiento(self, activo: bool) -> None:
        if not activo:
            self._seguimiento.clear()
            return
        if self.objetivo is None:
            raise RuntimeError("Haga GoTo a un objeto antes de activar el seguimiento.")
        self._seguimiento.set()
        if self._hilo_seguimiento is None or not self._hilo_seguimiento.is_alive():
            self._hilo_seguimiento = threading.Thread(target=self._bucle_seguimiento, daemon=True)
            self._hilo_seguimiento.start()

    @property
    def siguiendo(self) -> bool:
        return self._seguimiento.is_set()

    def _bucle_seguimiento(self) -> None:
        """Recalcula la posición del objeto cada pocos segundos (rotación terrestre)."""
        while self._seguimiento.is_set():
            if not self.montura.en_movimiento and self.objetivo:
                try:
                    pos = self.posicion_objeto(self.objetivo["objeto"])
                    usar = self.objetivo["correccion_ia"] != "ninguna"
                    d_az, d_alt = self._correccion(pos.azimut, pos.altitud, usar)
                    self.montura.mover_a(pos.azimut + d_az + self._offset_manual[0],
                                         pos.altitud + d_alt + self._offset_manual[1])
                except Exception as e:
                    self.error, self.mensaje = str(e), f"Seguimiento detenido: {e}"
                    self._seguimiento.clear()
                    break
            time.sleep(self.cfg.intervalo_seguimiento_s)

    def detener(self) -> None:
        self._seguimiento.clear()
        self.montura.detener()
        self.mensaje = "Movimiento detenido."

    # ----------------------------------------------------------------- estado
    def estado(self) -> dict:
        az, alt = self.montura.posicion()
        gps = None
        if self.gps:
            gps = {"con_senal": self.gps.con_senal, "error": self.gps.ultimo_error}
        sitio = self.efemerides.sitio
        return {
            "referenciada": self.montura.referenciada,
            "en_movimiento": self.montura.en_movimiento,
            "siguiendo": self.siguiendo,
            "azimut": round(az, 3), "altitud": round(alt, 3),
            "objetivo": None if self.objetivo is None else {
                k: v for k, v in self.objetivo.items() if k != "prediccion"},
            "mensaje": self.mensaje, "error": self.error,
            "modelo_ia": None if self.modelo is None else
            {"tipo": self.modelo.tipo, "muestras": self.modelo.n_muestras},
            "registros": len(registro.leer(self.cfg.registro_csv)),
            "simulacion": self.cfg.simulacion, "gps": gps,
            "sitio": {"latitud": sitio.latitud, "longitud": sitio.longitud},
            "hora_utc": self.ahora().isoformat(timespec="seconds"),
        }

    def cerrar(self) -> None:
        self.detener()
        if self.gps:
            self.gps.detener()
        self.montura.cerrar()

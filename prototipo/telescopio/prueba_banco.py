"""Pruebas de banco: comprobar cada componente por separado ANTES de armar la montura.

Ejecutar en la Raspberry Pi, desde la carpeta prototipo/:

    python -m telescopio.prueba_banco i2c                      # ¿se ven el GY-91 y el AS5600?
    python -m telescopio.prueba_banco gps --segundos 120       # ubicación y hora
    python -m telescopio.prueba_banco fin-carrera              # pulsar los interruptores
    python -m telescopio.prueba_banco encoder                  # girar el imán a mano
    python -m telescopio.prueba_banco nivel                    # inclinación del trípode
    python -m telescopio.prueba_banco motor az --grados 10     # ida y vuelta de un eje

Todas aceptan --config config.json. `motor` acepta --simulacion para probar en la PC.
"""

from __future__ import annotations

import argparse
import time

from .config import cargar_config


def prueba_motor(cfg, eje: str, grados: float, simulacion: bool) -> None:
    from .motores import MotorSimulado, MotorTB6600

    parametros = cfg.az if eje == "az" else cfg.alt
    motor = MotorSimulado(parametros, escala_tiempo=1) if simulacion else MotorTB6600(parametros)
    pasos = round(grados * parametros.pasos_por_grado)
    print(f"Eje {parametros.nombre}: {parametros.micropasos} micropasos, reducción {parametros.reduccion}:1 "
          f"→ {parametros.pasos_por_grado:.1f} micropasos por grado.")
    print(f"Moviendo +{grados}° ({pasos} micropasos). Observa el sentido de giro…")
    try:
        inicio = time.monotonic()
        motor.mover(pasos)
        print(f"  listo en {time.monotonic() - inicio:.2f} s. Pausa de 2 s.")
        time.sleep(2)
        print(f"Volviendo −{grados}°…")
        motor.mover(-pasos)
        print("  listo. El eje debe estar exactamente donde empezó (marca una referencia con cinta).")
        print("Si giró al revés de lo esperado, pon \"invertido\": true en ese eje del config.json.")
    finally:
        motor.cerrar()


def prueba_fin_carrera(cfg, segundos: float) -> None:
    from gpiozero import Button

    botones = {}
    for eje in (cfg.az, cfg.alt):
        if eje.pin_fin_carrera is not None:
            botones[eje.nombre] = Button(eje.pin_fin_carrera, pull_up=True)
    if not botones:
        print("No hay pines de fin de carrera configurados.")
        return
    print(f"Pulsa cada interruptor durante los próximos {segundos:.0f} s…")
    previo = {n: None for n in botones}
    fin = time.monotonic() + segundos
    while time.monotonic() < fin:
        for nombre, boton in botones.items():
            if boton.is_pressed != previo[nombre]:
                previo[nombre] = boton.is_pressed
                print(f"  {nombre}: {'ACTIVADO' if boton.is_pressed else 'libre'}")
        time.sleep(0.05)


def prueba_gps(cfg, segundos: float) -> None:
    import serial

    from .gps import LectorGPS

    puerto = cfg.gps_puerto or "/dev/serial0"
    lector = LectorGPS(puerto)
    print(f"Leyendo {puerto} durante {segundos:.0f} s (al aire libre; el primer fix tarda 1–5 min)…")
    lineas = 0
    with serial.Serial(puerto, lector.baudios, timeout=1) as s:
        fin = time.monotonic() + segundos
        while time.monotonic() < fin:
            linea = s.readline().decode("ascii", errors="ignore").strip()
            if not linea:
                continue
            lineas += 1
            lector.procesar(linea)
            if lineas % 20 == 0:
                if lector.con_senal and lector.sitio:
                    print(f"  FIX: lat {lector.sitio.latitud:.5f}, lon {lector.sitio.longitud:.5f}, "
                          f"alt {lector.sitio.elevacion_m:.0f} m; reloj desfasado {lector.desfase.total_seconds():+.1f} s")
                else:
                    print(f"  sin fix todavía ({lineas} sentencias NMEA recibidas)")
    if lineas == 0:
        print("No llegó ningún dato: revisa TX→GPIO15 (pin 10), RX→GPIO14 (pin 8) y que el puerto serie esté activado.")


def prueba_i2c(_cfg, _segundos: float) -> None:
    from .sensores import DIRECCIONES_ESPERADAS, abrir_bus, escanear_i2c

    with abrir_bus() as bus:
        encontrados = escanear_i2c(bus)
    print("Dispositivos I²C encontrados:", ", ".join(f"0x{d:02X}" for d in encontrados) or "ninguno")
    for direccion, nombre in DIRECCIONES_ESPERADAS.items():
        if direccion == 0x77 and 0x76 in encontrados:
            continue
        estado = "OK" if direccion in encontrados else "NO ENCONTRADO"
        print(f"  0x{direccion:02X} {nombre}: {estado}")


def prueba_encoder(_cfg, segundos: float) -> None:
    from .sensores import AS5600, abrir_bus

    with abrir_bus() as bus:
        encoder = AS5600(bus)
        print("Estado del imán:", encoder.estado())
        fin = time.monotonic() + segundos
        while time.monotonic() < fin:
            print(f"  ángulo: {encoder.angulo():7.2f}°", end="\r")
            time.sleep(0.2)
    print()


def prueba_nivel(_cfg, segundos: float) -> None:
    from .sensores import Acelerometro, abrir_bus

    with abrir_bus() as bus:
        acelerometro = Acelerometro(bus)
        print("Ajusta las patas del trípode hasta que la inclinación total sea < 0,1°.")
        fin = time.monotonic() + segundos
        while time.monotonic() < fin:
            alabeo, cabeceo, total = acelerometro.inclinacion()
            print(f"  alabeo {alabeo:+6.2f}°  cabeceo {cabeceo:+6.2f}°  total {total:5.2f}°", end="\r")
            time.sleep(0.3)
    print()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Pruebas de banco del telescopio")
    parser.add_argument("--config", help="archivo JSON de configuración")
    sub = parser.add_subparsers(dest="prueba", required=True)
    m = sub.add_parser("motor", help="mueve un eje ida y vuelta")
    m.add_argument("eje", choices=["az", "alt"])
    m.add_argument("--grados", type=float, default=10.0)
    m.add_argument("--simulacion", action="store_true", help="sin hardware (en la PC)")
    for nombre, ayuda, defecto in (("fin-carrera", "muestra los interruptores", 30), ("gps", "lee el GPS", 120),
                                   ("i2c", "busca el GY-91 y el AS5600", 0), ("encoder", "lee el AS5600", 30),
                                   ("nivel", "inclinación del trípode con el GY-91", 60)):
        p = sub.add_parser(nombre, help=ayuda)
        p.add_argument("--segundos", type=float, default=defecto)
    args = parser.parse_args(argv)
    cfg = cargar_config(args.config)
    if args.prueba == "motor":
        prueba_motor(cfg, args.eje, args.grados, args.simulacion)
    else:
        {"fin-carrera": prueba_fin_carrera, "gps": prueba_gps, "i2c": prueba_i2c,
         "encoder": prueba_encoder, "nivel": prueba_nivel}[args.prueba](cfg, args.segundos)


if __name__ == "__main__":
    main()

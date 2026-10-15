"""Genera esquema.svg: conexiones eléctricas del telescopio automatizado.

Uso:  python3 generar_esquema.py   (no requiere librerías externas)
"""

from pathlib import Path

W, H = 1400, 1080
C = {
    "v12": "#c0392b", "v5": "#e67e22", "v33": "#b9770e", "gnd": "#222222",
    "paso": "#2471a3", "i2c": "#1e8449", "uart": "#7d3c98", "lim": "#a04000",
    "A+": "#222222", "A-": "#1e8449", "B+": "#c0392b", "B-": "#2471a3",
}
el = []


def txt(x, y, s, size=13, anchor="start", weight="normal", color="#111", italic=False):
    st = ' font-style="italic"' if italic else ""
    el.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" fill="{color}"{st}>{s}</text>')


def caja(x, y, w, h, titulo, sub=None, fondo="#f4f6f7", borde="#34495e"):
    el.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fondo}" stroke="{borde}" stroke-width="2"/>')
    txt(x + w / 2, y + 20, titulo, 14, "middle", "bold")
    if sub:
        for i, linea in enumerate(sub.split("|")):
            txt(x + w / 2, y + 37 + 15 * i, linea, 11, "middle", color="#444")


def cable(puntos, color, ancho=2.2, guiones=False):
    d = " ".join(f"{x},{y}" for x, y in puntos)
    g = ' stroke-dasharray="6 4"' if guiones else ""
    el.append(f'<polyline points="{d}" fill="none" stroke="{color}" stroke-width="{ancho}" stroke-linejoin="round"{g}/>')


def punto(x, y, color="#111"):
    el.append(f'<circle cx="{x}" cy="{y}" r="4" fill="{color}"/>')


def borne(x, y, etiqueta, lado="izq", color="#111"):
    el.append(f'<circle cx="{x}" cy="{y}" r="3.5" fill="#fff" stroke="#111" stroke-width="1.5"/>')
    if lado == "izq":
        txt(x + 8, y + 4, etiqueta, 11, color=color)
    elif lado == "der":
        txt(x - 8, y + 4, etiqueta, 11, "end", color=color)
    elif lado == "arriba":
        txt(x, y + 16, etiqueta, 11, "middle", color=color)
    else:
        txt(x, y - 8, etiqueta, 11, "middle", color=color)


def tierra(x, y):
    cable([(x, y), (x, y + 10)], C["gnd"])
    for i, ancho in enumerate((16, 10, 4)):
        el.append(f'<line x1="{x - ancho / 2}" y1="{y + 10 + 4 * i}" x2="{x + ancho / 2}" y2="{y + 10 + 4 * i}" stroke="{C["gnd"]}" stroke-width="2"/>')


# ------------------------------------------------------------------ título
txt(W / 2, 32, "Esquema de conexiones · telescopio automatizado (Raspberry Pi 4 + 2 × TB6600)", 19, "middle", "bold")

# ------------------------------------------------------------------ alimentación
caja(20, 70, 170, 70, "Batería LiFePO4", "12,8 V · 12 Ah|con BMS integrado", "#e9f7ef", "#1e8449")
caja(230, 85, 100, 40, "Fusible 7,5 A", None, "#fdedec", "#c0392b")
caja(370, 85, 110, 40, "Interruptor", None, "#fdedec", "#c0392b")
caja(560, 80, 150, 50, "Paro de emergencia", "contacto NC", "#fdedec", "#c0392b")
caja(370, 165, 110, 40, "Voltímetro", None, "#fdedec", "#c0392b")
caja(560, 175, 170, 70, "Step-down XL4015", "12 V → 5,1 V · 5 A|(ajustar ANTES de conectar)", "#fef5e7", "#b9770e")

cable([(190, 105), (230, 105)], C["v12"], 3)
cable([(330, 105), (370, 105)], C["v12"], 3)
cable([(480, 105), (560, 105)], C["v12"], 3)
punto(520, 105, C["v12"])
cable([(520, 105), (520, 185), (480, 185)], C["v12"], 2)
cable([(520, 185), (520, 210), (560, 210)], C["v12"], 2)
punto(520, 185, C["v12"])
txt(200, 98, "+", 14, weight="bold", color=C["v12"])
tierra(105, 140)
tierra(425, 205)
tierra(645, 245)
txt(28, 182, "El negativo de la batería es la", 11, color="#444")
txt(28, 196, "tierra común (GND) de todo", 11, color="#444")

# bus de 12 V para motores (después del paro de emergencia)
cable([(710, 105), (1380, 105), (1380, 525), (990, 525), (990, 560)], C["v12"], 3)
cable([(990, 105), (990, 300)], C["v12"], 3)
punto(990, 105, C["v12"])
txt(1040, 98, "12 V motores (se corta con el paro de emergencia)", 12, color=C["v12"], weight="bold")

# ------------------------------------------------------------------ Raspberry Pi
caja(520, 300, 280, 460, "Raspberry Pi 4", "pin físico · GPIO", "#eaf2f8", "#2471a3")
# alimentación por USB-C desde el step-down
cable([(730, 245), (730, 275), (660, 275), (660, 300)], C["v5"], 3)
txt(668, 292, "USB-C 5,1 V", 11, color=C["v5"], weight="bold")

# ------------------------------------------------------------------ drivers TB6600
def driver(y0, nombre, gp):
    caja(950, y0, 190, 200, f"TB6600 {nombre}", "SW: OFF OFF ON | ON ON OFF|16 µpasos · 1,5 A", "#fdfefe", "#2471a3")
    # alimentación arriba
    borne(990, y0, "", "arriba")
    borne(1030, y0, "", "arriba")
    txt(984, y0 - 6, "VCC", 11, "end", weight="bold", color=C["v12"])
    txt(1092, y0 - 8, "GND", 11, weight="bold")
    # señales a la izquierda
    nombres = ["PUL+", "PUL−", "DIR+", "DIR−", "ENA+", "ENA−"]
    ys = [y0 + 30 + 22 * i for i in range(6)]
    for n, y in zip(nombres, ys):
        borne(950, y, n, "izq")
    # salidas al motor a la derecha
    salidas = [("A+", y0 + 60), ("A−", y0 + 85), ("B+", y0 + 120), ("B−", y0 + 145)]
    for n, y in salidas:
        borne(1140, y, n, "der")
    # cables de señal desde la Raspberry Pi (positivos)
    for (pin, gpio), y in zip(gp, ys[0::2]):
        cable([(800, y), (950, y)], C["paso"])
        txt(790, y + 4, f"{pin} · GPIO{gpio}", 11, "end", color=C["paso"], weight="bold")
    # negativos unidos a GND de la Raspberry Pi
    cable([(935, ys[1]), (935, ys[5] + 20)], C["gnd"])
    for y in (ys[1], ys[3], ys[5]):
        cable([(935, y), (950, y)], C["gnd"])
    cable([(800, ys[5] + 20), (935, ys[5] + 20)], C["gnd"])
    txt(790, ys[5] + 24, f"{gp[3][0]} · GND", 11, "end", color=C["gnd"], weight="bold")
    # motor
    cx, cy = 1275, y0 + 102
    el.append(f'<circle cx="{cx}" cy="{cy}" r="48" fill="#5d6d7e" stroke="#222" stroke-width="2"/>')
    txt(cx, cy - 4, "M", 22, "middle", "bold", "#fff")
    txt(cx, cy + 16, "NEMA 23", 11, "middle", color="#fff")
    txt(cx, cy + 66, f"Motor de {nombre.lower()}", 12, "middle", "bold")
    colores = ["A+", "A-", "B+", "B-"]
    for (n, y), col, dy in zip(salidas, colores, (-30, -12, 12, 30)):
        cable([(1140, y), (1185, y), (1185, cy + dy), (cx - 46, cy + dy)], C[col], 2.4)
    return ys


driver(300, "AZIMUT", [("11", 17), ("13", 27), ("15", 22), ("9", None)])
driver(560, "ALTITUD", [("16", 23), ("18", 24), ("22", 25), ("20", None)])
# tierra de potencia de los drivers
for y0 in (300, 560):
    cable([(1030, y0), (1030, y0 - 20), (1075, y0 - 20)], C["gnd"])
    tierra(1075, y0 - 20)
for i, linea in enumerate(("Colores típicos JK57HS:", "A+ negro, A− verde, B+ rojo, B− azul", "(verificar las bobinas con multímetro)")):
    txt(1275, 752 + 13 * i, linea, 10, "middle", color="#444")

# ------------------------------------------------------------------ GPS (UART) a la izquierda
caja(230, 520, 160, 120, "GPS NEO-6M", "UART 9600 baud", "#f5eef8", "#7d3c98")
gps = [("VCC", 545, "4 · 5V", C["v5"]), ("RX", 570, "8 · GPIO14 TXD", C["uart"]),
       ("TX", 595, "10 · GPIO15 RXD", C["uart"]), ("GND", 620, "14 · GND", C["gnd"])]
for n, y, etq, col in gps:
    borne(390, y, n, "der")
    cable([(390, y), (520, y)], col)
    txt(528, y + 4, etq, 11, color=col, weight="bold")

# ------------------------------------------------------------------ fines de carrera
caja(230, 670, 160, 80, "Fines de carrera", "altitud −5° y 90°|2 NO en paralelo", "#fbeee6", "#a04000")
for y, etq, col in ((690, "31 · GPIO6", C["lim"]), (725, "30 · GND", C["gnd"])):
    cable([(390, y), (520, y)], col)
    txt(528, y + 4, etq, 11, color=col, weight="bold")
txt(528, 650, "29 · GPIO5: libre (fin de", 10, color="#777")
txt(528, 662, "carrera de azimut opcional)", 10, color="#777")

# ------------------------------------------------------------------ I2C abajo
i2c = [("1 · 3V3", 555, C["v33"], 860), ("3 · SDA", 615, C["i2c"], 875), ("5 · SCL", 675, C["i2c"], 890), ("6 · GND", 735, C["gnd"], 905)]
caja(250, 930, 200, 110, "GY-91", "MPU9250 (0x68) + BMP280 (0x76)|inclinación y presión|fijo en la base", "#e9f7ef", "#1e8449")
caja(860, 930, 200, 110, "AS5600", "encoder magnético (0x36)|ángulo de altitud|pin DIR a GND", "#e9f7ef", "#1e8449")
for (etq, x, col, yb), xi, xd in zip(i2c, (285, 325, 365, 405), (895, 935, 975, 1015)):
    cable([(x, 760), (x, yb)], col)
    cable([(xi, yb), (xd, yb)], col)
    cable([(xi, yb), (xi, 930)], col)
    cable([(xd, yb), (xd, 930)], col)
    punto(x, yb, col)
    txt(x - 5, 778 + 0, etq, 10, "end", color=col, weight="bold")
for n, x in zip(("VIN", "SDA", "SCL", "GND"), (285, 325, 365, 405)):
    borne(x, 930, n, "abajo")
for n, x in zip(("VCC", "SDA", "SCL", "GND"), (895, 935, 975, 1015)):
    borne(x, 930, n, "abajo")
txt(1075, 1000, "cable ≤ 50 cm, trenzado", 11, color="#444")
txt(1075, 1015, "(sube por el centro del plato)", 11, color="#444")

# ------------------------------------------------------------------ leyenda
ley = [("12 V potencia", C["v12"]), ("5 V", C["v5"]), ("3,3 V", C["v33"]), ("GND", C["gnd"]),
       ("Señales de paso", C["paso"]), ("I²C", C["i2c"]), ("UART (GPS)", C["uart"]), ("Fin de carrera", C["lim"])]
txt(1130, 800, "Leyenda", 13, weight="bold")
for i, (n, col) in enumerate(ley):
    y = 820 + 18 * i
    cable([(1130, y), (1160, y)], col, 3)
    txt(1168, y + 4, n, 11)
txt(20, 1070, "Los negativos PUL−, DIR− y ENA− van a un GND de la Raspberry Pi (cableado de cátodo común). ENA en alto = motor libre.", 11, color="#444", italic=True)

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="Arial, Helvetica, sans-serif">'
       f'<rect width="{W}" height="{H}" fill="#ffffff"/>' + "".join(el) + "</svg>")
Path(__file__).with_name("esquema.svg").write_text(svg, encoding="utf-8")
print("esquema.svg generado")

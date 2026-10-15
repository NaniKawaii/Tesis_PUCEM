"""Genera cableado_caja.svg: plano a escala del interior de la caja de control,
visto desde arriba, con la ubicación de las placas, los prensaestopas y el
recorrido de cada cable (C1 a C12).

Las medidas coinciden con montura/montura.scad (caja de 162 × 210 mm).
Uso:  python3 generar_cableado_caja.py   (no requiere librerías externas)
"""

from pathlib import Path

W, H = 1760, 1000
S = 3.4                       # px por mm
X0, Y0 = 190, 300             # esquina de la caja en el plano (v = −105, u = 0)
P, A = 162, 210               # profundidad (u) y ancho (v) de la caja
C = {
    "v12": "#c0392b", "v12l": "#e74c3c", "v5": "#e67e22", "gnd": "#222222", "energia": "#922b21",
    "motor": "#5d6d7e", "paso": "#2471a3", "i2c": "#1e8449", "uart": "#7d3c98",
}
el = []


def X(v):
    return X0 + (v + A / 2) * S


def Y(u):
    return Y0 + u * S


def txt(x, y, s, size=13, anchor="start", weight="normal", color="#111", italic=False, rot=None):
    st = ' font-style="italic"' if italic else ""
    tr = f' transform="rotate({rot} {x} {y})"' if rot is not None else ""
    el.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" fill="{color}"{st}{tr}>{s}</text>')


def rect(u, v, du, dv, fondo, borde="#34495e", ancho=1.5, rx=3, guiones=False):
    g = ' stroke-dasharray="6 4"' if guiones else ""
    el.append(f'<rect x="{X(v):.1f}" y="{Y(u):.1f}" width="{dv * S:.1f}" height="{du * S:.1f}" rx="{rx}" '
              f'fill="{fondo}" stroke="{borde}" stroke-width="{ancho}"{g}/>')


def placa(u, v, du, dv, titulo, sub=None, fondo="#eaf2f8", tam=13):
    rect(u, v, du, dv, fondo)
    cx, cy = X(v + dv / 2), Y(u + du / 2)
    txt(cx, cy + (0 if sub else 5), titulo, tam, "middle", "bold")
    if sub:
        for i, linea in enumerate(sub.split("|")):
            txt(cx, cy + 16 + 13 * i, linea, 10.5, "middle", color="#333")


def cable(puntos, color, n=None, ancho=3.2, pos=0, guiones=False):
    d = " ".join(f"{X(v):.1f},{Y(u):.1f}" for u, v in puntos)
    g = ' stroke-dasharray="7 4"' if guiones else ""
    el.append(f'<polyline points="{d}" fill="none" stroke="{color}" stroke-width="{ancho}" '
              f'stroke-linejoin="round" stroke-linecap="round" opacity="0.92"{g}/>')
    if n:
        u, v = puntos[pos]
        etiqueta(X(v), Y(u), n, color)


def etiqueta(x, y, n, color):
    el.append(f'<rect x="{x - 15:.1f}" y="{y - 9:.1f}" width="30" height="18" rx="9" fill="#fff" stroke="{color}" stroke-width="2"/>')
    txt(x, y + 4.5, n, 11, "middle", "bold", color)


def prensa(u, v, nombre, lado):
    x, y = X(v), Y(u)
    el.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{6.35 * S:.1f}" fill="#fdfefe" stroke="#111" stroke-width="2"/>')
    el.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{3 * S:.1f}" fill="#d5d8dc" stroke="#555" stroke-width="1"/>')
    dx = {"arriba": (0, -30), "izq": (-28, 4), "der": (28, 4)}[lado]
    txt(x + dx[0], y + dx[1], nombre, 11.5, {"arriba": "middle", "izq": "end", "der": "start"}[lado], "bold")


# ------------------------------------------------------------------ título
txt(W / 2, 34, "Cableado dentro de la caja de control · vista desde arriba, a escala", 21, "middle", "bold")
txt(W / 2, 58, "La montura queda arriba (pared con la lengüeta). Medidas en mm, según montura/montura.scad.", 13, "middle", color="#444")

# ------------------------------------------------------------------ caja y zonas
rect(-51, -36, 51, 72, "#f2f3f4", guiones=True)                     # lengüeta bajo la base
txt(X(0), Y(-30), "lengüeta (3 tornillos M5 a la base fija)", 11, "middle", color="#555")
txt(X(0), Y(-14), "▲ hacia la montura", 12, "middle", "bold", "#555")
rect(0, -A / 2, P, A, "#ffffff", "#17202a", 3, 4)
rect(3, -A / 2 + 3, 70, A - 6, "#eafaf1", "none", 0, 0)                 # zona de control
rect(73, -A / 2 + 3, 20, A - 6, "#fef9e7", "none", 0, 0)                # canal
rect(93, -A / 2 + 3, 66, A - 6, "#ebf5fb", "none", 0, 0)                # zona de potencia
for u, linea1, linea2, c in ((36, "ZONA DE CONTROL", "5 V y señales", "#1e8449"),
                             (128, "ZONA DE POTENCIA", "12 V y motores", "#2471a3")):
    txt(X(-A / 2) - 12, Y(u), linea1, 12, "end", "bold", c)
    txt(X(-A / 2) - 12, Y(u) + 16, linea2, 11, "end", color=c)
txt(X(A / 2) + 12, Y(97) + 4, "◀ CANAL DE CABLES", 12, "start", "bold", "#b7950b")
txt(X(A / 2) + 12, Y(97) + 20, "20 mm de ancho", 11, "start", color="#b7950b")

# ------------------------------------------------------------------ placas
placa(17, -38, 56, 85, "Raspberry Pi 4", "con HAT de borneras|en el GPIO", "#d5f5e3")
rect(66, -32, 7, 52, "#1e8449", "#145a32")                           # borneras del HAT
txt(X(-6), Y(64), "borneras GPIO", 10, "middle", color="#145a32")
rect(17, -30, 3, 8, "#111", "#111")                                   # USB-C
txt(X(-26), Y(14.5), "USB-C", 10, "middle", "bold")
placa(17, -98, 54, 24, "Step-down", "salida 5,1 V ↑|↓ entrada 12 V", "#fdebd0", 12)
placa(52, -70, 19, 22, "Wago", "12 V · GND", "#fad7a0", 11)
placa(17, 58, 30, 38, "GPS", "antena en|la tapa", "#e8daef", 12)
placa(55, 64, 16, 20, "GY-91", None, "#d1f2eb", 10)
for nombre, v0, potencia_izq in (("TB6600 azimut", -100, True), ("TB6600 altitud", 4, True)):
    placa(103, v0, 56, 96, nombre, "disipador hacia abajo|sobre separadores de 5 mm", "#d6eaf8")
    # tira de borneras: 6 de potencia y 6 de señal (el orden exacto viene impreso en el driver)
    pot, sen = (v0 + 6, v0 + 50) if potencia_izq else (v0 + 50, v0 + 6)
    rect(93, pot, 10, 40, "#e74c3c", "#922b21", 1.2, 2)
    rect(93, sen, 10, 40, "#5dade2", "#1b4f72", 1.2, 2)
    txt(X(pot + 20), Y(99.5), "VCC GND A+ A− B+ B−", 9.5, "middle", "bold", "#fff")
    txt(X(sen + 20), Y(99.5), "PUL± DIR± ENA±", 9.5, "middle", "bold", "#fff")

# ------------------------------------------------------------------ prensaestopas
prensa(0, 60, "P1 · AS5600 y fines de carrera", "arriba")
prensa(0, -60, "P2 · reserva", "arriba")
prensa(83, -A / 2, "P3 motor az (abajo)", "izq")
txt(X(-A / 2) - 28, Y(83) + 20, "P4 energía (arriba)", 11.5, "end", "bold")
prensa(83, A / 2, "P5 motor alt (abajo)", "der")
txt(X(A / 2) + 28, Y(83) + 20, "P6 reserva (arriba)", 11.5, "start", "bold")

# ------------------------------------------------------------------ cables
cable([(83, -105), (86, -92), (96, -80)], C["motor"], "C1", 5, 1)
cable([(83, 105), (86, 92), (88, 40), (96, 30)], C["motor"], "C2", 5, 2)
cable([(83, -105), (78, -94), (78, -80), (78, -66), (71, -62)], C["energia"], "C3", 5, 2)
cable([(71, -64), (82, -70), (96, -70)], C["v12"], "C4", 2.6, 1)
cable([(71, -64), (75, -50), (75, 26), (96, 26)], C["v12"], None, 2.6)
cable([(71, -56), (80, -54), (96, -62)], C["gnd"], "C5", 2.6, 1)
cable([(71, -56), (77, -46), (77, 20), (96, 20)], C["gnd"], None, 2.6)
cable([(78, -91), (71, -91)], C["v12l"], "C6", 2.6, 1)
cable([(17, -86), (9, -86), (9, -26), (17, -26)], C["v5"], "C7", 3.2, 1)
cable([(73, -14), (86, -14), (96, -36)], C["paso"], "C8", 3, 1)
cable([(73, 10), (84, 30), (84, 70), (96, 72)], C["paso"], "C9", 3, 2)
cable([(0, 60), (10, 54), (52, 52), (66, 18)], C["i2c"], "C10", 3, 2)
cable([(63, 64), (60, 54), (70, 12)], C["i2c"], "C11", 2.4, 1)
cable([(40, 58), (34, 52), (66, 6)], C["uart"], "C12", 2.4, 1)

# ------------------------------------------------------------------ tabla de cables
tx, ty = 1075, 110
txt(tx, ty, "Lista de cables (etiqueta cada uno en ambos extremos)", 15, weight="bold")
filas = [
    ("C1", "Motor azimut", "P3 → TB6600 az: A+ A− B+ B−", "4 × 20 AWG flexible"),
    ("C2", "Motor altitud", "P5 → TB6600 alt: A+ A− B+ B−", "4 × 20 AWG flexible (silicona)"),
    ("C3", "Energía del panel", "P4 → Wago y step-down", "4 × 18 AWG"),
    ("C4", "12 V motores", "Wago → VCC de los 2 TB6600", "18 AWG rojo"),
    ("C5", "GND", "Wago → GND de los 2 TB6600 y step-down", "18 AWG negro"),
    ("C6", "12 V lógica", "C3 → IN+ del step-down", "18 AWG rojo"),
    ("C7", "5 V Raspberry Pi", "OUT step-down → USB-C acodado", "USB-C con puntas libres"),
    ("C8", "Señales azimut", "HAT: GPIO17, 27, 22, GND → TB az", "4 × 24 AWG trenzado"),
    ("C9", "Señales altitud", "HAT: GPIO23, 24, 25, GND → TB alt", "4 × 24 AWG trenzado"),
    ("C10", "AS5600 + fines", "P1 → HAT: 3V3, SDA, SCL, GND, GPIO6", "6 × 24 AWG apantallado"),
    ("C11", "GY-91", "GY-91 → HAT: 3V3, SDA, SCL, GND", "4 × 26 AWG, ≤ 10 cm"),
    ("C12", "GPS", "GPS → HAT: 5 V, TX↔RX, GND", "4 × 26 AWG, ≤ 10 cm"),
]
col = [tx, tx + 46, tx + 176, tx + 452]
for i, h in enumerate(("N.º", "Cable", "Desde → hasta", "Tipo")):
    txt(col[i], ty + 30, h, 12, weight="bold")
el.append(f'<line x1="{tx}" y1="{ty + 37}" x2="{W - 20}" y2="{ty + 37}" stroke="#555" stroke-width="1.2"/>')
colores = ["motor", "motor", "energia", "v12", "gnd", "v12l", "v5", "paso", "paso", "i2c", "i2c", "uart"]
for i, (n, nombre, ruta, tipo) in enumerate(filas):
    y = ty + 58 + 25 * i
    etiqueta(tx + 16, y - 4, n, C[colores[i]])
    txt(col[1], y, nombre, 12, weight="bold")
    txt(col[2], y, ruta, 11.5)
    txt(col[3], y, tipo, 11.5, color="#333")

# ------------------------------------------------------------------ reglas
ry = ty + 58 + 25 * len(filas) + 22
txt(tx, ry, "Reglas para que los cables no se dañen", 15, weight="bold")
reglas = [
    "<tspan font-weight='bold'>Sin jumpers Dupont</tspan> en la caja: se sueltan con la vibración. El GPIO va",
    "   por un <tspan font-weight='bold'>HAT de borneras de tornillo</tspan> (o una placa perforada soldada).",
    "<tspan font-weight='bold'>Punteras</tspan> (terminales tubulares) en todo cable que entra a una bornera.",
    "   Nunca estañes la punta: el estaño cede y el tornillo se afloja.",
    "<tspan font-weight='bold'>Brida a menos de 5 cm de cada borne</tspan>, pasada por dos agujeros vecinos",
    "   del piso: así la vibración nunca tira del borne.",
    "<tspan font-weight='bold'>Prensaestopas bien apretado</tspan>: si tiras del cable desde afuera,",
    "   no debe moverse por dentro (alivio de tensión).",
    "<tspan font-weight='bold'>Potencia y señal separadas</tspan>: 12 V y motores por el canal; I²C y GPS",
    "   en la zona de control. Si se cruzan, que sea en ángulo recto.",
    "<tspan font-weight='bold'>Bucle de servicio</tspan> de 3–5 cm en cada cable para sacar una placa",
    "   sin desconectar las demás.",
    "<tspan font-weight='bold'>Nada sobre los disipadores</tspan> de los TB6600 ni pegado al step-down.",
    "<tspan font-weight='bold'>Termorretráctil</tspan> en todo empalme; ningún empalme dentro de un prensaestopas.",
    "<tspan font-weight='bold'>Antes de energizar:</tspan> multímetro entre 12 V y GND (sin corto) y",
    "   continuidad de cada cable de la lista.",
]
for i, linea in enumerate(reglas):
    vi = not linea.startswith("   ")
    if vi:
        el.append(f'<circle cx="{tx + 5}" cy="{ry + 25 + 19 * i - 4}" r="3" fill="#2471a3"/>')
    txt(tx + 16, ry + 25 + 19 * i, linea.strip() if vi else linea[3:], 12)

# ------------------------------------------------------------------ leyenda y notas
ly = Y(P) + 40
ley = [("Motor", C["motor"]), ("Energía (4 hilos)", C["energia"]), ("12 V", C["v12"]), ("GND", C["gnd"]),
       ("5 V", C["v5"]), ("PUL/DIR/ENA", C["paso"]), ("I²C", C["i2c"]), ("UART", C["uart"])]
for i, (n, c) in enumerate(ley):
    x = X0 + (i % 4) * 190
    y = ly + 22 * (i // 4)
    el.append(f'<line x1="{x}" y1="{y}" x2="{x + 30}" y2="{y}" stroke="{c}" stroke-width="4" stroke-linecap="round"/>')
    txt(x + 38, y + 4, n, 12)
txt(X0, ly + 62, "Los dos TB6600 van orientados igual, con las borneras hacia el canal: en uno la tira de potencia queda hacia el costado", 11.5, color="#444", italic=True)
txt(X0, ly + 80, "y en el otro hacia el centro. El orden exacto de los 12 bornes viene impreso en tu driver. Ajusta los DIP antes de atornillarlos.", 11.5, color="#444", italic=True)

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="Arial, Helvetica, sans-serif">'
       f'<rect width="{W}" height="{H}" fill="#ffffff"/>' + "".join(el) + "</svg>")
Path(__file__).with_name("cableado_caja.svg").write_text(svg, encoding="utf-8")
print("cableado_caja.svg generado")

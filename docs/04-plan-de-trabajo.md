# Paso 5 · Plan de trabajo: de las compras al envío del artículo

## ¿El software va en la Raspberry Pi o es web? → **Las dos cosas**

```
 Celular / laptop                 Raspberry Pi 4 (en la montura)                Hardware
┌──────────────────┐   Wi-Fi   ┌──────────────────────────────────┐   cables   ┌──────────────┐
│ Navegador web    │ ────────▶ │ Software del telescopio (Python) │ ─────────▶ │ 2 × TB6600   │──▶ motores
│ (Chrome, Safari) │ ◀──────── │ · cálculo de planetas            │   GPIO     ├──────────────┤
│ No se instala    │           │ · servidor web (interfaz)        │ ◀───────── │ GPS, IMU,    │
│ nada             │           │ · control de motores e IA        │  UART/I²C  │ encoder      │
└──────────────────┘           └──────────────────────────────────┘            └──────────────┘
```

- **La Raspberry Pi es necesaria.** Los motores se mueven con pulsos eléctricos que salen
  de los pines GPIO de un dispositivo **conectado físicamente** a los drivers. Un servidor
  en Internet no puede generar esos pulsos ni leer el GPS. Por eso el software **se instala
  en la Raspberry Pi**.
- **La interfaz es web.** La Raspberry Pi funciona como servidor y el usuario la abre desde
  el **navegador** de cualquier celular o laptop, sin instalar ninguna aplicación.
- **En el campo, sin Internet:** la Raspberry Pi crea su **propia red Wi-Fi** (p. ej.
  "Telescopio"). El usuario se conecta a esa red y abre `http://10.42.0.1:8000`.
- **Desde lejos (opcional, más adelante):** se puede publicar con un túnel seguro para
  demostraciones remotas, como Ricci et al. (2024). Necesita Internet y medidas de seguridad.
- **Mientras no tengas el hardware:** el mismo software corre en tu **laptop en modo
  simulación**, así que puedes practicar y hacer capturas desde ya (ver `prototipo/README.md`).

---

## Plan paso a paso

Las semanas son orientativas. Los pasos marcados con ⏩ pueden hacerse **en paralelo**.

| # | Paso | Quién | Depende de | Semana |
|---|---|---|---|---|
| 1 | Comprar lo que falta | Nashla | — | 1–2 |
| 2 | Medir las piezas compradas y enviarme las medidas | Nashla | 1 | 2 |
| 3 | Ajustar los STL con esas medidas | Claude | 2 | 2 |
| 4 | Impresión 3D (primero la pieza de prueba) | Nashla + imprenta | 3 | 2–3 |
| 5 ⏩ | Instalar el software en la Raspberry Pi | Nashla + Claude | microSD | 2 |
| 6 ⏩ | Esquema del circuito ✅ y prueba de motores en banco | Nashla | 1 | 3 |
| 7 | Armado mecánico y balanceo | Nashla | 4, 6 | 4 |
| 8 | Calibración y primeras pruebas nocturnas | Nashla + Claude | 5, 7 | 4–5 |
| 9 | Experimentos E1/E2: ≥ 30 apuntados y entrenamiento de la IA | Nashla | 8 | 5–7 |
| 10 | Experimentos E3/E4/E5 con 20 participantes | Nashla | 9 | 7–8 |
| 11 | Análisis estadístico y figuras | Claude + Nashla | 9, 10 | 8 |
| 12 | Completar el artículo, revisión del tutor y envío | Nashla + tutor | 11 | 8–9 |

### 1. Comprar (prioridad según lo que bloquea)

**A. Bloquea la impresión 3D** (hay que medirlo antes de imprimir):
- 2 poleas GT2 de 20 dientes con agujero de 8 mm y ancho de 6 mm.
- Rodamiento giratorio "lazy susan" de 4″ (≈ 102 mm).
- Telescopio (recomendado: Maksutov 90/1250) o, si ya tienes uno, revisar si trae barra Vixen.

**B. Mecánica:**
- Trípode de topografía con rosca 5/8″.
- Perfil de aluminio 2040 de 300 mm y 8 tuercas en T.
- 2 rodamientos 608ZZ y una varilla de acero de 8 mm × 160 mm.
- Correas GT2 cerradas de **600 mm** y **280 mm**.
- Tuerca 5/8″-11 y la tornillería de [`montura/LEEME.md`](../montura/LEEME.md#4-tornillería-y-piezas-compradas).

**C. Electrónica:**
- Batería LiFePO4 de 12,8 V y 12 Ah con su **cargador LiFePO4**.
- *Step-down* XL4015 de 5 V.
- Fusible de 7,5 A con portafusible, interruptor, paro de emergencia y voltímetro.
- Cables de 18 y 22 AWG, borneras y jumpers.
- MicroSD de 32 GB, disipador y ventilador para la Raspberry Pi.
- 2 microswitches y un imán diametral de 6 × 2,5 mm.

**D. Opcional:** Raspberry Pi Camera Module 3, para medir el error de forma objetiva.

### 2. Medidas que necesito

| Medida | Cómo |
|---|---|
| Largo del eje del motor NEMA 23 (desde la brida) | Calibrador |
| Largo total y del cubo de la polea de 20T | Calibrador |
| Lado y alto del lazy susan | Calibrador |
| Ancho mayor de la barra Vixen (si el telescopio la trae) | Calibrador |
| Largo del perfil 2040 comprado | Cinta métrica |

### 4. Encargar la impresión 3D

Entrega al servicio de impresión la carpeta `montura/stl/` y la tabla de la §3 de
`montura/LEEME.md`, que trae el material, las capas, los perímetros y el relleno. Las piezas
ya vienen orientadas y no necesitan soportes. Pide que **impriman primero `prueba_gt2.stl`**
y prueba la correa antes de imprimir el resto. Al recibirlas, mide los agujeros de 22 mm de
los rodamientos y el canal Vixen.

### 5. Software en la Raspberry Pi

1. Con **Raspberry Pi Imager**, grabar *Raspberry Pi OS Lite (64 bits)* en la microSD,
   configurando el usuario, el Wi-Fi y el SSH.
2. Activar el **puerto serie** (para el GPS) y el **I²C** (para el IMU y el encoder) con
   `raspi-config`.
3. Clonar este repositorio, instalar las dependencias y probar en simulación.
4. Configurar la **red Wi-Fi propia** y el **arranque automático** del servidor al
   encender la Raspberry Pi.

➡️ Para este paso te preparo un **script de instalación** que deja todo listo con un solo
comando.

### 6. Circuito

✅ **Listo:** [`circuito/LEEME.md`](../circuito/LEEME.md) tiene el esquema, la tabla de
conexiones cable por cable, la configuración de los TB6600 y una prueba de banco en 11 pasos
con el programa `prueba_banco` (motores, fines de carrera, GPS, I²C, encoder y nivel).

### 9–10. Experimentos (los datos del artículo)

| Experimento | Qué hacer | Mínimo |
|---|---|---|
| E1 | GoTo, centrar y "Objeto centrado (registrar)" | 30 apuntados en ≥ 3 noches, repartidos por el cielo |
| E2 | "Entrenar y evaluar" (lineal y red neuronal) y GoTo con la IA activa | Con los datos de E1 |
| E3 | Cronometrar la búsqueda manual frente al sistema | 20 participantes |
| E4 | Cuestionario SUS | 20 participantes |
| E5 | Latencia de los comandos web | 50 comandos |

**Pendiente de mi parte para estos pasos:**
- Lectura del GY-91 (inclinación y presión) y del AS5600.
- Registro automático de E3 y E5.
- Formulario de consentimiento y cuestionario SUS.
- Script de análisis estadístico, que genera directamente las tablas y la figura del artículo.

### 12. Artículo

El borrador v2 está en [`articulo/articulo_v2.docx`](../articulo/articulo_v2.docx). Todo
lo que está **resaltado en amarillo `[[ ]]`** se completa **solo con datos medidos**.

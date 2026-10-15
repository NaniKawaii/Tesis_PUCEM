# Paso 2 · Revisión de los componentes comprados

> ➡️ Las decisiones finales (telescopio, montura, batería LiFePO4 en lugar de la fuente de 24 V)
> y la lista de compras definitiva están en [03-telescopio-montura-energia.md](03-telescopio-montura-energia.md).

Fuente: factura de MEGATRONICA n.º 004-100-000009208 del 28/01/2026, por un total de
USD 406,19 con IVA. Los precios de la sección "Qué falta" son **estimaciones aproximadas**
para Ecuador y deben cotizarse.

## 1. Veredicto por componente

| # | Componente | Precio | Veredicto | Uso en el prototipo |
|---|---|---|---|---|
| 1 | 2 × NEMA 23 JK57HS76-3004 (1,8°, 3 A, ~1,9 N·m, ~1 kg, eje de 8 mm) | 113,04 | ✅ **Sirve** | Un motor por eje (azimut y altitud). Tiene torque de sobra; el detalle es su peso (~1 kg cada uno), que la estructura de PLA debe soportar. Necesita una **reducción** (ver §2) |
| 2 | 2 × Driver TB6600 (9–42 V) | 38,26 | ✅ **Sirve** | Uno por motor. Configurar los switches en **16 micropasos** y la corriente en **2,5–2,8 A** (el motor admite 3 A; un poco menos evita que se caliente) |
| 3 | Raspberry Pi 4 (2 GB) | 77,99 | ✅ **Sirve** | Cerebro del sistema: efemérides, servidor web, IA y señales STEP/DIR. 2 GB son suficientes. Le faltan la microSD y la alimentación (ver §2) |
| 4 | Pantalla TFT HDMI de 5″ (800×480) | 60,86 | 🟡 **Opcional** | No es necesaria porque todo se controla desde el navegador. Puede usarse como panel local (mostrar la interfaz web o la vista de una cámara) en ferias o demostraciones. Consume energía extra en campo |
| 5 | Encoder magnético AS5600 (12 bits) | 6,03 | ✅ **Sirve (en 1 eje)** | Montado en el eje de **altitud**, mide el ángulo real y permite detectar pasos perdidos o comparar el ángulo comandado con el medido. Es un dato extra para el artículo. Usa I²C (dirección 0x36), sin conflicto con el GY-91 |
| 6 | GY-91 (MPU9250 + BMP280) | 10,87 | ✅ **Sirve** (parcialmente) | **Acelerómetro:** mide la inclinación del trípode, que es una de las principales fuentes de error de apuntado. **BMP280:** da presión y temperatura para corregir la refracción atmosférica en el cálculo. **Magnetómetro:** ❌ no es confiable junto a motores e imanes; no usarlo para buscar el norte |
| 7 | GPS u-blox NEO-6M | 10,35 | ✅ **Sirve** | Ubicación y hora exacta (la Raspberry Pi no tiene reloj con batería). Ya está soportado en el software (`gps.py`). Necesita cielo despejado; el primer *fix* tarda 1–5 min |
| 8 | Batería LiPo 2S 7,4 V 1100 mAh | 17,35 | ❌ **No sirve para los motores** | Los TB6600 necesitan **mínimo 9 V**. Solo podría alimentar la Raspberry Pi con un convertidor *buck*, y únicamente durante ~1 h |
| 9 | BMS 2S 13 A | 4,30 | ❌ **No hace falta** | Es para armar packs de celdas 18650. Una LiPo ya armada se carga con un cargador balanceador, no con un BMS |
| 10 | Indicador de carga 2S | 4,26 | ❌ **No hace falta** | Solo tiene sentido si se usa la batería 2S |

**Resumen:** de USD 353,21 sin IVA, unos **USD 256,54 son el núcleo útil**: motores,
drivers, Raspberry Pi, GPS, IMU y encoder. **USD 60,86** son un extra opcional (la pantalla)
y **USD 25,91** (batería, BMS e indicador) no sirven para mover los motores.

> ℹ️ **Observación para el artículo:** la factura está a nombre de **AFIFSYSTEMS S.A.S.**
> El borrador dice que el proyecto se financió con "fondos propios y donaciones de la
> institución". Si esa empresa pagó los componentes, hay que declararlo en *Fuente de
> financiamiento* (y valorar si es un conflicto de interés).

> ℹ️ Los **acoples para motor** que aparecían en la proforma **no están en la factura**. Es
> una buena noticia: con la reducción por poleas no hacen falta.

## 2. Qué falta comprar

### Imprescindible: sin esto el prototipo no funciona

| Ítem | Para qué | Aprox. USD |
|---|---|---|
| **Fuente conmutada de 24 V y 5 A** (120 W), o de 12 V y 10 A | Alimentar los dos TB6600. A 24 V los NEMA 23 mantienen mejor el torque a velocidad | 15–20 |
| **Convertidor DC-DC *step-down* a 5 V y ≥ 3 A** (p. ej. XL4015 de 5 A) y un cable USB-C de buena calidad | Alimentar la Raspberry Pi 4 desde la misma fuente (necesita 5,1 V y 3 A; el LM2596 queda justo) | 5–8 |
| **MicroSD de 32 GB, clase A1** | Sistema operativo de la Raspberry Pi | 6–10 |
| **Transmisión con reducción**, por eje: polea GT2 de 20 dientes con agujero de **8 mm** para el motor, polea grande GT2 de 60 dientes (o una de 80–100 dientes **impresa en 3D**) para el eje del telescopio y correa GT2 cerrada de 6 mm | Pasar de 6,75′ a **1,35′ por micropaso** con relación 5:1 (o 2,25′ con 3:1). Es el cambio que más mejora la precisión | 15–25 (para 2 ejes) |
| **Rodamientos:** 1 plato giratorio tipo "lazy susan" de ~150 mm para el azimut y 4–6 rodamientos 608ZZ para el eje de altitud | Que los ejes giren suaves y sin juego. El PLA solo, rozando contra PLA, genera holgura y error | 8–12 |
| **2–4 fines de carrera** (microswitch con palanca) | Seguridad: detienen el motor en el tope. Los pines ya están previstos (GPIO 5 y 6) | 2–4 |
| **Cableado:** cable de 4 hilos para motores (≥ 22 AWG), cable de 18 AWG para alimentación, jumpers dupont, borneras, interruptor general y portafusible con fusible de 5 A | Conexiones seguras | 8–12 |
| **Disipadores y ventilador** (o case con ventilador) para la Raspberry Pi | Sin ellos, la Pi 4 baja su velocidad por temperatura dentro de una caja cerrada | 5–8 |

**Subtotal imprescindible: ~USD 65–100**

### Muy recomendable

| Ítem | Para qué | Aprox. USD |
|---|---|---|
| **Pulsador de paro de emergencia** (tipo hongo) que corte la alimentación de los motores | Seguridad en demostraciones con público | 3–5 |
| **Nivel de burbuja circular** | Nivelar el trípode rápido (el acelerómetro lo verifica después) | 1–3 |
| **Cámara**: Raspberry Pi Camera Module 3 o una webcam USB sin lente, con adaptador de 1,25″ impreso en 3D | Hace **objetiva** la medición del error, que se mediría en píxeles en lugar de a ojo. Además permite la IA de visión (una CNN que detecte el planeta), que cumple literalmente el objetivo de "reconocimiento de cuerpos celestes" | 25–40 |

### Según cómo vayas a observar

- **Si observas junto a un enchufe**, con una extensión, basta la fuente de 24 V.
- **Si vas a observar en el campo sin electricidad**, conviene una batería de **12 V**, como
  una LiFePO4 de 12 V y 6 Ah o una de plomo-ácido sellada de 12 V y 7 Ah (como las de
  alarmas). Cuesta unos USD 20–35. Los TB6600 funcionan a 12 V, con algo menos de velocidad.

## 3. Lo que todavía no sé (y cambia la lista)

1. **¿Qué telescopio vas a montar?** Su peso y su largo definen la reducción, el
   contrapeso y si la estructura de PLA aguanta.
2. **¿Cómo está el diseño 3D?** Hay que confirmar si ya prevé rodamientos y poleas.
3. **¿Tienes impresora 3D o filamento?** Recomiendo **PETG** para las piezas que cargan
   peso: el PLA se deforma con el calor si queda al sol.
4. **¿Dónde vas a observar?** Junto a un enchufe o en el campo.

## 4. Conexión de lo comprado a la Raspberry Pi (resumen)

| Componente | Bus | Pines de la Raspberry Pi |
|---|---|---|
| TB6600 azimut | GPIO | STEP 17, DIR 27, ENA 22 |
| TB6600 altitud | GPIO | STEP 23, DIR 24, ENA 25 |
| Fines de carrera | GPIO | 5 (azimut), 6 (altitud), a GND |
| GPS NEO-6M | UART | TX→GPIO 15, RX→GPIO 14 |
| GY-91 + AS5600 | I²C (mismo bus) | SDA GPIO 2, SCL GPIO 3, 3,3 V, GND |
| Pantalla de 5″ | HDMI (+ USB si es táctil) | — |

El software actual ya maneja motores, fines de carrera y GPS. La lectura del IMU (para la
inclinación y la presión) y del encoder se agregará en el paso de integración del hardware.

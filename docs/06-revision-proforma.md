# Revisión de la proforma 000004629 (Megatrónica, 21/10/2026)

Proforma de **Megatrónica** (Sebastián Chamorro) a nombre de AFIFSYSTEMS S.A.S.
Subtotal USD 172,30 · IVA 15 % USD 25,84 · **Total USD 198,14**. Validez: 15 días.

Revisión contra [`05-lista-para-proveedor.md`](05-lista-para-proveedor.md) y el diseño de
[`montura/`](../montura/LEEME.md).

---

## Resumen

| Veredicto | Líneas | Monto |
|---|---|---|
| ✅ Comprar tal cual | 16 | USD 81,51 |
| ⚠️ Comprar, pero cambiando la especificación | 3 | USD 11,65 |
| ⛔ No comprar todavía | 2 | USD 79,13 |

Si se aprueba solo lo correcto, el pedido baja de **USD 198,14 a unos USD 94** con IVA.
Faltan además **19 ítems** de la lista, entre ellos **las poleas GT2**, sin las cuales la
montura no se mueve.

---

## 1. ✅ Comprar tal cual (16 líneas, USD 81,51)

| Línea | Ítem | Total | Comentario |
|---|---|---|---|
| 2 | Step Down 5A XL4015 | 3,47 | Es el convertidor correcto para la Raspberry Pi |
| 3 | Switch balancín 2 pines | 0,65 | **Medirlo al recibirlo** para ajustar el calado del panel |
| 4 | Pulsador hongo 22 mm rojo **NC** con retención | 3,91 | Exactamente el contacto que necesita el paro de emergencia |
| 5 | Mini voltímetro 0–100 V led rojo | 5,65 | **Medirlo al recibirlo**: el calado del panel está dibujado para 45,5 × 26,5 mm y estos suelen ser más chicos |
| 6 | MicroSD 32 GB clase 10 + adaptador | 7,83 | Sirve (la clase A1 sería algo más rápida, pero no es crítico) |
| 7 | Disipadores Raspberry Pi, 3 piezas | 3,48 | |
| 8 | Final de carrera mini × 3 | 1,70 | 2 para el eje de altitud y 1 de repuesto |
| 9 | Cable flexible 18 AWG rojo, 2 m | 0,78 | **Subir a 4 m** (ver §4) |
| 10 | Cable flexible 18 AWG negro, 2 m | 0,78 | **Subir a 4 m** (ver §4) |
| 11 | Kit crimpadora + terminales tubulares, 1200 piezas | 22,17 | Es la inversión que evita que los cables se suelten con la vibración |
| 12 | Prensaestopas PG7 × 9 | 2,35 | Coincide exacto con el diseño |
| 13 | Kit termoencogible, 328 piezas | 6,95 | |
| 14 | Espaciadores hexagonales M3 × 5 mm × 8 | 2,09 | Para levantar los TB6600 y que circule el aire |
| 15 | Rodamientos 608ZZ × 4 | 6,92 | 2 para el eje y 2 de repuesto |
| 16 | Eje de acero 8 mm × 400 mm | 4,78 | Se corta en 160–200 mm y sobra material |
| 21 | Envío Servientrega | 8,00 | |

---

## 2. ⚠️ Cambiar antes de aprobar (3 líneas)

### Línea 17 · Perfil de aluminio **2020** 600 mm (USD 5,22)

**El diseño usa perfil 2040** (20 × 40 mm), no 2020 (20 × 20 mm). Las tres piezas impresas
que abrazan el brazo (zócalo, cabezal y soporte del motor de altitud) están dibujadas para
una sección de 40 × 20 mm.

Dos razones para no aceptar el cambio:

1. **Rigidez.** El brazo es un voladizo de 30 cm que sostiene hasta 3 kg. El 2040 es el
   doble de rígido que el 2020 en la dirección del peso y unas 8 veces más rígido en la
   dirección del giro de azimut. Toda flexión se convierte en error de apuntado, que es
   justamente lo que mide el artículo.
2. **Sujeción.** El cabezal se atornilla con **2 tornillos M5** roscados en los agujeros
   centrales del extremo del perfil. El 2040 tiene dos agujeros centrales; el 2020 tiene
   uno solo.

➡️ **Pedir: perfil de aluminio 2040 (20 × 40 mm), 300 mm.** Si solo lo venden por tramos
largos, 600 mm sirve igual y sobra material. Si de verdad no consiguen 2040, avísame: se
puede reparametrizar el diseño para 2020, pero la montura queda más flexible.

### Línea 18 · Correa dentada GT2 6 mm **por metro** (USD 3,04)

El diseño usa **dos correas cerradas** (en lazo), no correa abierta:

- **Azimut: GT2 de 6 mm, 600 mm cerrada** (también sirve 610 mm)
- **Altitud: GT2 de 6 mm, 280 mm cerrada** (también sirve 300 mm)

Una correa abierta habría que empalmarla, y el empalme produce un salto en el paso justo en
la transmisión cuya precisión se está midiendo. Además 1 m no alcanza para los dos lazos.

➡️ **Pedir: 1 correa cerrada GT2-6 de 600 mm y 1 correa cerrada GT2-6 de 280 mm.**

### Línea 20 · Cable USB tipo A macho – A hembra 3 m (USD 3,39)

No sirve: la Raspberry Pi 4 se alimenta por **USB-C**, y 3 m de cable producen una caída de
voltaje que hace aparecer el aviso de bajo voltaje.

➡️ **Pedir: cable USB-C macho de 30–50 cm** (se corta el otro extremo y se atornilla a la
salida del step-down). Si lo tienen, mejor acodado a 90°.

---

## 3. ⛔ No comprar todavía (2 líneas, USD 79,13)

### Línea 1 · Cargador iMAX B6 80 W 6 A (USD 47,83)

Es el ítem más caro de la proforma, el 28 % del pedido, y **no está decidido todavía**.

- El iMAX B6 **sí** carga LiFePO4 (modo "LiFe"), así que no es un error del proveedor.
- Pero **necesita una fuente externa de 11–18 V y 60–90 W**, que normalmente **no viene
  incluida**. Habría que sumarle unos USD 15–20 más.
- Si se compra una batería LiFePO4 **con BMS integrado** (que es la del diseño), alcanza con
  un **cargador simple de 14,6 V** de USD 15–25, sin fuente aparte y sin riesgo de elegir mal
  el modo en el menú.

➡️ **Primero decidir la batería** (que no está en esta proforma) y comprar el cargador que le
corresponda, idealmente en el mismo lugar. Un cargador mal elegido es la forma más común de
arruinar una batería.

### Línea 19 · Filamento PETG negro 1 kg × 2 (USD 31,30)

Solo hace falta **si el servicio de impresión 3D no pone el material**. La mayoría cobra por
peso con material incluido.

➡️ **Preguntar primero a la imprenta 3D.** Si ellos ponen el material, se ahorran USD 31,30;
pero hay que confirmar que impriman en **PETG** (no solo PLA, que se deforma al sol) y que su
cama sea de al menos **220 × 220 mm**, porque la caja de control mide 213 × 210 mm.

---

## 4. ➕ Lo que falta en la proforma

Son 19 ítems de la lista que el proveedor no coti­zó. Hay que preguntar si los tienen o
buscarlos en otro lado.

### Críticos (sin esto el prototipo no funciona)

| Ítem | Especificación | Cant. |
|---|---|---|
| **Poleas GT2** | **20 dientes, agujero de 8 mm, ancho de 6 mm** | 2 |
| **Batería** | LiFePO4 12,8 V 12 Ah con BMS integrado | 1 |
| Rodamiento giratorio "lazy susan" | 4″ (102 mm) | 1 |
| Trípode de topografía | Aluminio, rosca 5/8″-11 | 1 |
| Tuerca hexagonal | 5/8″-11 UNC | 1 |
| Tuercas en T | M5, para perfil 2040 | 10 |
| Tornillería M5 | M5×10 (12), M5×20 (12), M5×25 (12), M5×30 (2), M5×50 (2), tuercas M5 (25) | — |
| Tornillería M3/M4 | M4×12 (10), prisioneros M3×8 + tuercas M3 (5+5), autorroscantes M2,5×6 (6), M3×8 (15), M3×10 (10) | — |
| Tornillo | 1/4″-20 × 1/2″ | 2 |
| Imán diametral | 6 × 2,5 mm, para el AS5600 (solo si no vino con el módulo) | 1 |

Sin las **poleas GT2** no se mueve ningún eje: es lo primero que hay que confirmar.

### Importantes

| Ítem | Especificación | Cant. |
|---|---|---|
| Portafusible en línea + fusibles | Cuchilla (ATC), fusibles de 7,5 A | 1 + 3 |
| HAT de borneras de tornillo para Raspberry Pi | 40 pines (*GPIO screw terminal HAT*) | 1 |
| Conectores Wago | 221-415 (5 vías) | 3 |
| Cable de 4 hilos de silicona | 20 AWG, extra flexible (motores) | 2 m |
| Cable apantallado | 6 hilos, 24 AWG (AS5600 y fines de carrera) | 1 m |
| Cable multifilar de colores | 24 AWG, kit de 6 colores (señales) | 1 kit |
| Macho de roscar M5 con mango | Para roscar los extremos del perfil | 1 |
| Bridas plásticas | 2,5 × 100 mm | 100 |
| Tapones PG7 | Para los prensaestopas de reserva | 2 |

Además, **subir el cable 18 AWG rojo y negro de 2 m a 4 m de cada uno**: con 2 m no alcanza
para la batería, el panel de energía y el tramo interno de la caja.

### Menores (se consiguen en cualquier ferretería)

Malla o espiral para cables de 10 mm (2 m) y correa de velcro de 25 mm (1 m).

---

## 5. Mensaje sugerido para el proveedor

> Buenas tardes, Sebastián. Gracias por la proforma 4629. Antes de aprobarla necesito tres
> cambios y una consulta:
>
> **Cambios:**
> 1. **Ítem 17:** necesito perfil de aluminio **2040** (20 × 40 mm) de 300 mm, no 2020. ¿Lo
>    tienen?
> 2. **Ítem 18:** en lugar de correa GT2 por metro, necesito **2 correas GT2 de 6 mm
>    cerradas**: una de **600 mm** y una de **280 mm**.
> 3. **Ítem 20:** en lugar del cable USB A-A, necesito un **cable USB-C macho de 30–50 cm**
>    (le voy a cortar el otro extremo).
> 4. **Ítems 9 y 10:** subir el cable 18 AWG rojo y negro a **4 m de cada uno**.
>
> **Por ahora no incluir:** el ítem 1 (cargador iMAX B6) y el ítem 19 (filamento PETG). Los
> confirmo después.
>
> **Consulta:** ¿tienen estos ítems que no aparecen en la proforma?
>
> - 2 poleas GT2 de **20 dientes, agujero de 8 mm, ancho de 6 mm** (es lo más importante)
> - Batería LiFePO4 de 12,8 V y 12 Ah con BMS, y su cargador de 14,6 V
> - Rodamiento giratorio tipo "lazy susan" de 4″ (102 mm)
> - 10 tuercas en T M5 para perfil de aluminio
> - Portafusible en línea con fusibles de 7,5 A
> - HAT de borneras de tornillo para Raspberry Pi (40 pines)
> - 3 conectores Wago 221-415
> - Cable de 4 hilos 20 AWG de silicona (2 m), cable apantallado de 6 hilos 24 AWG (1 m) y
>   kit de cable multifilar 24 AWG de colores
> - Imán diametral de 6 × 2,5 mm para encoder AS5600
> - Bridas plásticas de 2,5 mm y 2 tapones PG7
>
> Quedo atenta.

---

## 6. Observación para el artículo

Esta proforma, igual que la factura de los componentes, está a nombre de **AFIFSYSTEMS
S.A.S.** Hay que decidir qué se declara en "Fuente de financiamiento" y en "Conflicto de
interés" del artículo (ya está marcado en el borrador).

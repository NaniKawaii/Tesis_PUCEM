# Revisión de la proforma 000004629 (Megatrónica, 21/10/2026)

> ✅ **El proveedor envió una V2 el 24/10/2026 que corrige todo lo señalado. El veredicto final y el plan para lo que no tienen están en el [§7](#7-proforma-v2-24102026).** Lo que sigue es la revisión de la primera versión.

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

---

## 7. Proforma V2 (24/10/2026)

**Veredicto: aprobar.** Las 17 líneas son correctas. Subtotal USD 89,25 · IVA USD 13,39 ·
**Total USD 102,64**.

Qué cambió respecto de la V1:

| Punto que se pidió | Resultado |
|---|---|
| Correas cerradas de 600 y 280 mm | ✅ **Resuelto**: 2 correas cerradas de **610 y 280 mm** |
| Cable 18 AWG rojo y negro a 4 m | 🟡 Lo subieron a **3 m** de cada uno |
| Quitar el cargador iMAX B6 | ✅ Quitado |
| Quitar el filamento PETG | ✅ Quitado |
| Perfil 2040 en lugar de 2020 | ❌ **No lo tienen** (y quitaron también el 2020) |
| Cable USB-C en lugar del USB A-A | ❌ **No lo tienen** |

> **La correa de azimut es de 610 mm, no de 600.** La distancia entre ejes pasa de 121,9 a
> **128,3 mm**, que entra holgada en las ranuras del soporte del motor (admiten de 116 a
> 133 mm). No hay que cambiar ninguna pieza impresa.

**Dos cosas pequeñas antes de aprobar** (no son bloqueantes):

1. Subir el cable 18 AWG rojo a **4 m** (son 39 centavos más). Con 3 m queda justo: batería →
   panel, panel → caja y el tramo interno de la caja suman unos 3,4 m de cable rojo.
2. Preguntar si **todavía tienen el perfil 2020** que cotizaron en la V1, por si no aparece
   el 2040 en otro lado.

---

## 8. Lo que no tienen y dónde conseguirlo

El proveedor avisó que **lo que no está en la proforma es lo que no tiene**. Hay que
conseguir estos ítems en otro lado. Ninguno es raro; la mayoría está en ferreterías.

### Críticos (sin esto el prototipo no se mueve)

| Ítem | Dónde buscarlo | Si no aparece |
|---|---|---|
| **2 poleas GT2 de 20 dientes, agujero de 8 mm, ancho de 6 mm** | Tiendas de impresión 3D y CNC (Quito y Guayaquil), Mercado Libre | Avísame: se pueden imprimir, pero una polea impresa de 20 dientes con agujero de 8 mm queda con paredes de 2 mm y es la pieza que más esfuerzo recibe |
| **Perfil de aluminio 2040 (20 × 40 mm), 300 mm** | Distribuidores de perfil estructural, tiendas de CNC e impresión 3D | Ver "Decisión 1" abajo |
| **Rodamiento giratorio "lazy susan" de 4″ (102 mm)** | Ferretería, sección de herrajes para muebles ("base giratoria para mesa") | Avísame |
| **Batería y su cargador** | Ver "Decisión 2" abajo | — |
| **Trípode de topografía con rosca 5/8″** | Tiendas de topografía y construcción | Un trípode de cámara robusto con adaptador de 5/8″ a 1/4″ |
| **10 tuercas en T M5** | Donde consigas el perfil | **Tuercas M5 hexagonales comunes**: entran por el extremo de la ranura y giran para trabar |
| **Tornillería M5, M4, M3 y 1/4″-20** | Ferretería | — |
| **Macho de roscar M5 con mango** | Ferretería | — |
| **Tuerca hexagonal 5/8″-11 UNC** | Ferretería | Viene con algunos trípodes |

### Importantes, con buen reemplazo

| Ítem | Dónde buscarlo | Reemplazo que sirve igual |
|---|---|---|
| Portafusible en línea + fusibles de 7,5 A | **Repuestos automotrices** (fusible de cuchilla) | — |
| HAT de borneras de tornillo para Raspberry Pi | Tiendas de electrónica, Mercado Libre | Placa perforada con borneras soldadas sobre un conector hembra de 40 pines |
| 3 conectores Wago 221-415 | Material eléctrico | **Regleta de borneras** (bornera de paso) de 10 A |
| Cable apantallado de 6 hilos y cable multifilar de señal | — | **Cable de red UTP o FTP (Cat5e)**: trae 4 pares trenzados de 24 AWG, rechaza bien el ruido de los motores y se consigue en cualquier lado. Es un reemplazo mejor que bueno |
| Cable de 4 hilos de silicona 20 AWG (motores) | Electrónica | 4 cables flexibles sueltos de 20 AWG, trenzados y metidos en malla |
| Cable USB-C | Cualquier tienda de celulares | Se compra un cable USB-C común y se le corta un extremo |
| Imán diametral de 6 × 2,5 mm | Mercado Libre, tiendas de imanes | **No es bloqueante**: el AS5600 mide el ángulo real de altitud, que es un dato extra para el artículo, no algo que el sistema necesite para funcionar. Ojo: tiene que ser **diametral**, no axial |
| Bridas plásticas, tapones PG7, velcro, malla para cables | Ferretería | Un prensaestopas de reserva se sella apretándolo sobre un trozo de filamento |

---

## 9. Dos decisiones pendientes

### Decisión 1 · El brazo: perfil 2040 o 2020

| | 2040 (diseño actual) | 2020 (lo que tenían) |
|---|---|---|
| Rigidez en la dirección del peso | referencia | **la mitad** |
| Rigidez en la dirección del giro | referencia | **8 veces menos** |
| Sujeción del cabezal | 2 tornillos M5 en el extremo | 1 solo tornillo |
| Flexión estimada del brazo con 3 kg | ≈ 1,8′ | ≈ 3,6′ |

El 2020 **no arruina el proyecto**: esa flexión es sistemática y repetible, o sea justo el
tipo de error que el modelo de aprendizaje automático está hecho para corregir, y de hecho
daría un resultado interesante para el artículo. Pero empezar con el doble de flexión, en un
trabajo cuyo objetivo es la precisión de apuntado, es arrancar cuesta arriba.

➡️ **Recomendación:** buscar el 2040 junto con las poleas GT2 y el lazy susan, que de todos
modos hay que comprar en otro lado. Si no aparece, me avisas y reparametrizo el diseño para
2020 (es cambiar una variable y regenerar los STL).

### Decisión 2 · La batería

| | LiFePO4 12,8 V 12 Ah (diseño actual) | Plomo-ácido sellada 12 V 7 Ah |
|---|---|---|
| Dónde se consigue | Importada o tiendas especializadas | **Cualquier lado**: es la batería de alarmas y UPS |
| Precio con cargador | USD 60–95 | USD 30–40 |
| Autonomía | ~7 h | ~3–4 h |
| Peso | ~1,5 kg | ~2,2 kg |
| Voltaje | 14,6 V a 10 V: dentro del rango del TB6600 | 13,8 V a 10,5 V: también dentro del rango |

La de plomo-ácido pesa más, pero va colgada entre las patas del trípode haciendo de
contrapeso, así que el peso extra no estorba. Y 3–4 horas alcanzan de sobra para una sesión
de observación.

➡️ **Recomendación:** si la LiFePO4 no aparece rápido, **arrancar con la de plomo-ácido de
12 V y 7 Ah**. Permite empezar las pruebas de inmediato y se puede cambiar después sin tocar
nada del diseño. Si se queda la de plomo-ácido, hay que ajustar en el artículo la Tabla 1 y
la sección de energía.

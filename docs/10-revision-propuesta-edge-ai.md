# Paso 10 · Revisión de la propuesta "Edge-AI en hardware embebido"

Documento recibido del Ing. Corrales el **16/11/2026**: *"Edge-AI en hardware embebido de
bajo coste para el apuntado autónomo de objetos celestes: estudio comparativo de inferencia
en CPU, acelerador y nube"* (v3, 15 páginas, 31 referencias).

> **En una línea:** es una propuesta sólida y bien escrita, pero **es otro proyecto**, no una
> versión mejorada de este. Pide **6 meses** y tú tienes **15 semanas**. Hay **cinco ideas**
> que sí conviene traer, y **dos** caen justo encima de decisiones que ya tenías pendientes
> en [`08-diseno-definitivo.md`](08-diseno-definitivo.md) §13.

---

## 1. Qué es el documento

Una **propuesta de investigación** (no un artículo) para un proyecto de **seis meses** que
produciría **dos manuscritos**: uno para *IEEE Transactions on Instrumentation and
Measurement* y otro para *IEEE Internet of Things Journal*, más un dataset público.

**La pregunta es otra.** Tu artículo pregunta si un corrector aprendido vence al modelo
clásico de apuntado en una montura altacimutal de bajo costo. La propuesta pregunta **dónde
conviene ejecutar el plate solving**: en la CPU de la Pi, en un acelerador Hailo-8L o en la
nube. El apuntado es ahí el banco de pruebas, no el objeto de estudio.

El documento **no está firmado**: los autores figuran como "Author Name, Member, IEEE" y
"Co-Author Name".

---

## 2. Por qué no cabe en tu tesis

**Tu restricción dura son las 15 semanas**, hasta ~19/02/2027, con una rúbrica donde el
**57 % de la nota exige datos medidos reales** ([`07`](07-rubrica-lector.md),
[`08`](08-diseno-definitivo.md)).

La propuesta pide, en su propio cronograma:

| Mes | Qué |
|---|---|
| 1 | Montaje mecánico y caracterización del modelo de error |
| 2 | Dataset v1 y entrenamiento de backbones |
| 3 | Cuantización INT8 e integración de la condición CPU |
| 4 | Compilación del Hailo, auditoría de operadores, función de nube |
| 5 | **90 episodios** más el subestudio de controladores |
| 6 | Análisis y envío de **dos manuscritos** |

Tus 15 semanas se te van completas en lo que la propuesta llama "mes 1 y mes 5". Y eso
suponiendo que el hardware llegue a tiempo, que es justo el riesgo que ya tienes abierto en
el plan B de [`08`](08-diseno-definitivo.md).

---

## 3. Qué costaría cambiarse

**Hardware tuyo que quedaría sin uso: USD 256,54** — exactamente todo el "núcleo útil" de tu
factura, según [`02-componentes.md`](02-componentes.md):

| Componente | USD | Por qué no se usa |
|---|---|---|
| 2 × NEMA 23 JK57HS76 | 113,04 | La propuesta usa NEMA 17 |
| 2 × TB6600 | 38,26 | Usa TMC2209 |
| Raspberry Pi 4 (2 GB) | 77,99 | Pide Pi 5 de 8 GB |
| GPS NEO-6M | 10,35 | No aparece |
| GY-91 | 10,87 | No aparece (su barómetro sí serviría para la refracción) |
| AS5600 | 6,03 | Dice explícitamente "no hay encoder" |

De la proforma de Megatrónica casi todo se reutiliza; lo que no, **las dos correas GT2
cerradas de 610 y 280 mm**, calculadas para tus reducciones de 14:1 y 5:1.

**Hardware nuevo, según la tabla de la propia propuesta: USD 283** (353 con el acelerador):
Pi 5 (80), 2 NEMA 17 (30), 2 TMC2209 (15), Camera Module 3 (25), guía de 50 mm (55),
mecánica 2020 (50), alimentación e INA219 (28), Hailo-8L (70).

> La propuesta marca la Pi 5 y los NEMA 17 como "en posesión". Son del Ing. Corrales, no
> tuyos: tú tienes una Pi 4 y dos NEMA 23.

Y haría falta además: una **cuenta AWS** con facturación, un **PC x86_64 con Linux** para
compilar el modelo del Hailo, y **dos salidas mensuales a cielo oscuro** durante medio año.

**Impacto total: unos USD 540–610** y volver al mes cero.

---

## 4. La propuesta le da la razón a tu montura

Esto no es opinión: sale de los números del propio documento.

**Par en el eje de altitud**

| | Tu diseño | La propuesta |
|---|---|---|
| Motor | NEMA 23, ~0,95 N·m a 1,5 A | NEMA 17, 0,28 N·m a 1,2 A |
| Reducción | 5:1 por correa | Acople directo |
| **Par en el eje** | **~4,75 N·m** | **0,28 N·m** |

Su Figura 4 calcula que un tubo de 2,5 kg con el centroide a 20 cm del eje pide **4,91 N·m**,
y concluye con todas las letras que *"el motor no puede mover el tubo"*: le falta un factor
de 17,4. Solo funciona con el tubo **perfectamente equilibrado** (centroide a ±8 mm y ~150 g
de contrapeso), y ahí le queda 6,3× de margen. Tu montura mueve ese mismo tubo desequilibrado
sin problema, que es lo que pasa en campo cada vez que se cambia de ocular.

**Y en exactitud, igual.** La propuesta explica bien que micropaso ≠ exactitud: el error de
ángulo de paso del motor (±5 %) son **±5,4′** con cualquier subdivisión. Y dice:

> *"Solo un cambio del diseño compra exactitud, una correa GT2 de 5:1 que divide el error de
> paso por cinco hasta ±1,08 minutos de arco… La correa sigue documentada como mejora para la
> construcción de la alumna y no como variable experimental."*

O sea: **reconoce que tu transmisión por correa es lo único que compra exactitud de verdad**,
y la deja fuera de su diseño para no mezclar variables. Con tus reducciones el error
sistemático de paso baja a **±1,08′ en altitud y ±0,39′ en azimut**.

Esto es un argumento para la defensa, y un argumento para proponerle que **su estudio corra
sobre tu montura** en lugar de sobre una nueva.

---

## 5. Las cinco ideas que sí conviene adoptar

### 5.1. Verificar con un solver que no sea el tuyo ⭐

La propuesta mide el error de apuntado contra *"un solver de verificación que no es el
nuestro"*, y da la razón: así **un sesgo sistemático del modelo aprendido no puede
enmascararse**.

Tu diseño mide con cámara, pero no tiene esa separación. Es la idea más valiosa del
documento para ti: es metodología pura, no cuesta hardware, y blinda tu resultado principal
frente a la crítica más obvia que te puede hacer un revisor o el lector.

### 5.2. Un tercer candidato para la decisión de la cámara

[`08`](08-diseno-definitivo.md) §13 tiene la cámara como **pendiente 2**, entre la Pi HQ
Camera con lente de 28 mm (50–80 USD) y la Sony + Tamron (~1 700 USD). La propuesta aporta
una tercera opción con números: **Camera Module 3 + guía de 50 mm y 200 mm de focal**, que da
**6,9 segundos de arco por píxel** con binning 2×2, por unos 80 USD en total.

No digo que sea la mejor para la Luna, que es tu caso de prueba; digo que entra en la
comparación con cifras concretas y que conviene ponerla en la tabla antes de decidir.

### 5.3. Descomponer el modelo de error en cuatro términos físicos

La propuesta separa: **error periódico** (una vez por vuelta, serie de Fourier), **flexión**
(varía con la altitud, polinomio de orden bajo), **refracción** (se calcula con presión y
temperatura, no se aprende) y **backlash más fricción estática** (no se modela, se acota
aproximándose siempre desde la misma dirección).

Lo de aproximarse siempre desde la misma dirección **es gratis y mejora tus mediciones desde
la primera noche**. Y nombrar los cuatro términos sube el nivel técnico de tu §2.4 y de la
discusión sin tocar el experimento.

### 5.4. Latencia en p50 y p95, no media ± DE

Tu E5 reporta media y desviación. La propuesta usa mediana y percentil 95, con el argumento
correcto: *"lo que el lazo de control siente es la cola"*. Son dos líneas en el script de
análisis.

### 5.5. Energía medida con INA219, y el modo sin conectividad

Un **INA219** (USD 3) en el riel de 5 V da **watios-hora por sesión medidos**, que es lo que
hoy tienes como `[[medir]]` en la Tabla 2.

Y la propuesta plantea una buena pregunta: *"¿qué hace el telescopio si la nube no
contesta?"*. Tu sistema ya es inmune, porque la Pi crea su propia red y calcula las
efemérides localmente. **Es una fortaleza que hoy no estás destacando** en la discusión, y
vale un párrafo.

---

## 6. Riesgos del documento

1. **Nada está medido.** Su Figura 5 lo dice: *"DATA IS SYNTHETIC, NOT MEASURED"*. Es honesto
   y es buena práctica —valida el pipeline estadístico, igual que hicimos nosotros en
   [`08`](08-diseno-definitivo.md) §4— pero la propuesta está en el punto cero.
2. **La condición del acelerador puede quedarse sin medir.** Su §E lo reconoce: el Hailo-8L
   solo acepta binarios compilados en x86_64, y sin ese acceso E2 se reportaría como **"no
   medido"**. Es el corazón del segundo manuscrito.
3. **Las 31 referencias no están verificadas.** No revisé ninguna. Si algo de esto entra en
   tu artículo, hay que verificarlas como hicimos con las tuyas en
   [`01`](01-diagnostico-articulo.md).
4. **Dos revistas IEEE es otra liga**, muy por encima de lo que pide un artículo de
   titulación.

---

## 7. Recomendación

**Sigue con tu proyecto y adopta las cinco ideas de la §5.** La 5.1 (solver de verificación
independiente) y la 5.3 (los cuatro términos del error) son las que más suben la calidad del
artículo, y ninguna cuesta dinero ni tiempo de campo.

**Guarda la propuesta como trabajo futuro.** Tu artículo ya cierra proponiendo incorporar una
cámara y visión por computadora; esta propuesta es la continuación natural de esa frase, y
citarla como línea futura suma para los dos.

### Para la conversación con el Ing. Corrales

Ya tenías **pendiente hablar con él** del aporte, la pregunta, H3, el objetivo general, el
objetivo 4 y el título ([`08`](08-diseno-definitivo.md) §13, pendiente 1). Esta propuesta cae
justo en esa conversación, así que conviene llevar las dos cosas juntas y aclarar:

1. **¿Qué es esto para mi tesis?** ¿Reemplaza el enfoque, es un proyecto paralelo al que me
   invita, o es la hoja de ruta de trabajo futuro?
2. **¿Quién pone el hardware?** La Pi 5 y los NEMA 17 que figuran "en posesión" son suyos.
3. **Si participo, ¿cuál es mi autoría?** El documento está con los nombres en blanco.
4. **¿Y si su estudio corre sobre mi montura?** Su propio documento reconoce que la correa de
   5:1 es lo único que compra exactitud, y mi montura ya la tiene, con 17× más par en el eje
   de altitud. Sería la forma de que los dos trabajos se sumen en vez de competir.

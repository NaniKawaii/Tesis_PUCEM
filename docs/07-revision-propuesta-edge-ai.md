# Revisión de la propuesta "Edge-AI en hardware embebido" (v3, nov-2026)

Documento recibido del ingeniero: *"Edge-AI en hardware embebido de bajo coste para el
apuntado autónomo de objetos celestes: estudio comparativo de inferencia en CPU, acelerador
y nube"*, 15 páginas, 31 referencias.

> **Conclusión en una línea:** es una propuesta bien hecha, pero **es otro proyecto**, no una
> versión mejorada del tuyo. Cambiarse costaría unos USD 540–610 y seis meses, y dejaría sin
> uso los USD 256,54 de hardware que ya compraste. Hay **cinco ideas concretas** que sí vale
> la pena traer a tu artículo.

---

## 1. Qué es este documento

Es una **propuesta de investigación** (no un artículo terminado) para un proyecto de
**seis meses** que produciría **dos manuscritos** en revistas IEEE:

- *IEEE Transactions on Instrumentation and Measurement* (el instrumento y el apuntado)
- *IEEE Internet of Things Journal* (la comparación borde-nube)

**La pregunta científica es otra.** Tu artículo pregunta: *¿el aprendizaje automático reduce
el error de apuntado de una montura de bajo costo, y la interfaz web la hace usable?*
La propuesta pregunta: *¿dónde conviene ejecutar el plate solving: en la CPU, en un
acelerador Hailo-8L o en la nube?* El apuntado es ahí el banco de pruebas, no el objeto de
estudio.

**No está firmado.** Los autores figuran como "Author Name, Member, IEEE" y "Co-Author
Name". La autoría no está definida.

---

## 2. Comparación con tu proyecto

| | **Tu artículo** | **La propuesta** |
|---|---|---|
| Entregable | 1 artículo (Esprint Investigación) | 2 manuscritos IEEE + dataset público |
| Duración | En curso, falta medir | 6 meses desde cero |
| Computador | Raspberry Pi 4, 2 GB ✅ *ya la tienes* | Raspberry Pi 5, 8 GB |
| Motores | 2 × NEMA 23, 1,9 N·m ✅ *ya los tienes* | 2 × NEMA 17, 0,40 N·m |
| Drivers | 2 × TB6600 ✅ *ya los tienes* | 2 × TMC2209 |
| Transmisión | Correa GT2, 14:1 y 5:1 | Acople directo |
| Sensores | GPS + GY-91 + AS5600 ✅ *ya los tienes* | Cámara (sin GPS, sin IMU, sin encoder) |
| Estructura | Perfil 2040 + 13 piezas PETG | Perfil 2020 + 8 piezas PETG |
| Cómo se mide el error | Centrado manual en el ocular | Plate solving con cámara |
| Extras necesarios | — | Hailo-8L, cuenta AWS, PC x86 |
| Campaña | ≥30 apuntados + 20 usuarios | 90 episodios + 20 del subestudio |

---

## 3. Lo que costaría cambiarse

**Hardware tuyo que quedaría sin uso: USD 256,54.** Es, exactamente, todo el "núcleo útil"
de tu factura:

| Componente | Precio | Por qué no se usa |
|---|---|---|
| 2 × NEMA 23 JK57HS76 | 113,04 | La propuesta usa NEMA 17 |
| 2 × TB6600 | 38,26 | La propuesta usa TMC2209 |
| Raspberry Pi 4 (2 GB) | 77,99 | La propuesta pide Pi 5 de 8 GB |
| GPS NEO-6M | 10,35 | No aparece en la propuesta |
| GY-91 | 10,87 | No aparece (aunque su barómetro serviría para la corrección por refracción) |
| AS5600 | 6,03 | La propuesta dice explícitamente "no hay encoder" |

De la proforma de Megatrónica, la mayor parte sí se reutilizaría (rodamientos, crimpadora,
prensaestopas, termorretráctil, step-down, panel). Lo que no: **las dos correas GT2 cerradas
de 610 y 280 mm**, que están calculadas para tus reducciones de 14:1 y 5:1.

**Hardware nuevo que habría que comprar: USD 283** (o 353 con el acelerador Hailo-8L), según
la propia tabla de la propuesta: Pi 5 (80), 2 NEMA 17 (30), 2 TMC2209 (15), Camera Module 3
(25), guía de 50 mm (55), mecánica 2020 (50), alimentación e INA219 (28), Hailo-8L (70).

> La propuesta marca la Pi 5 y los NEMA 17 como "en posesión", pero **en posesión del
> ingeniero, no tuya**. Tú tienes una Pi 4 y dos NEMA 23.

**Impacto total: unos USD 540–610.** Y además haría falta:

- Una **cuenta AWS** con facturación activa, para la condición de nube.
- Un **computador x86_64 con Linux** para compilar el modelo del Hailo-8L. La propia
  propuesta lo reconoce en su §E y admite que, sin él, la condición del acelerador se
  reportaría como **"no medido"** — es decir, el núcleo comparativo del artículo quedaría
  incompleto.
- **Al menos dos salidas mensuales a cielo oscuro** durante seis meses.

---

## 4. Un hallazgo técnico importante: tu montura es mejor para lo que mides

Esto no es opinión, sale de los números de la propia propuesta.

**Par disponible en el eje de altitud:**

| | Tu diseño | La propuesta |
|---|---|---|
| Motor | NEMA 23, ~0,95 N·m a 1,5 A | NEMA 17, 0,28 N·m a 1,2 A |
| Reducción | 5:1 por correa | Acople directo |
| **Par en el eje** | **~4,75 N·m** | **0,28 N·m** |

La propuesta calcula (su Figura 4) que un tubo de 2,5 kg con el centroide a 20 cm del eje
pide **4,91 N·m**, y concluye que *"el motor no puede mover el tubo"*: le falta un factor de
17,4. Solo funciona con el tubo **perfectamente equilibrado** (centroide a ±8 mm del eje y
unos 150 g de contrapeso), y ahí le queda un margen de 6,3×.

Tu montura mueve ese mismo tubo desequilibrado **sin despeinarse**. Es una ventaja real de
robustez en campo, donde el balance se pierde al cambiar de ocular.

**Y en exactitud pasa lo mismo.** La propuesta explica muy bien que micropaso ≠ exactitud:
el error de ángulo de paso del motor (±5 %) son **±5,4 minutos de arco** con cualquier
subdivisión. Y dice textualmente:

> *"Solo un cambio del diseño compra exactitud, una correa GT2 de 5:1 que divide el error de
> paso por cinco hasta ±1,08 minutos de arco... La correa sigue documentada como mejora para
> la construcción de la alumna."*

O sea: **la propuesta reconoce que tu transmisión por correa es lo único que compra exactitud
de verdad**, y la deja fuera de su propio diseño para no mezclar variables. Con tus
reducciones el error sistemático de paso baja a **±1,08′ en altitud y ±0,39′ en azimut**.

---

## 5. Lo que sí vale la pena traer a tu artículo

Cinco ideas, todas baratas y compatibles con lo que ya tienes:

### 5.1. Medir el error con cámara en vez de a ojo ⭐ la más valiosa

Tu propia sección de limitaciones ya lo dice: *"El error se midió por el centrado manual en
el ocular, cuya resolución depende del observador"*. La propuesta resuelve eso con una
**Camera Module 3 + un solver astrométrico independiente**, y reporta el error en minutos de
arco RMS.

La cámara **ya estaba en tu lista de compras como "recomendado" (USD 25–35)**. Esto la
asciende a prioridad alta: convierte tu medición principal de subjetiva en objetiva, que es
la crítica más fácil que te puede hacer un revisor.

### 5.2. Descomponer el modelo de error en cuatro términos físicos

La propuesta separa: **error periódico** (una vez por vuelta, se ajusta con serie de
Fourier), **flexión** (varía con la altitud, polinomio de orden bajo), **refracción**
(se calcula con presión y temperatura, no se aprende) y **backlash más fricción estática**
(no se modela, se acota moviendo siempre desde la misma dirección).

Tu artículo trata el error como una caja negra que el modelo aprende. Nombrar estos cuatro
términos en tu §2.4 y en la discusión **sube mucho el nivel técnico** sin cambiar nada del
experimento. Y el truco de "aproximarse siempre desde la misma dirección" para acotar el
backlash es gratis y mejora tus mediciones.

### 5.3. Reportar latencia p50 y p95, no media ± DE

Tu E5 mide latencia web con media y desviación. La propuesta usa **mediana y percentil 95**,
con el argumento correcto: *"una distribución dice más que una media, porque lo que el lazo
de control siente es la cola"*. Es cambiar dos líneas de tu script de análisis.

### 5.4. Medir la energía con un INA219 en vez de estimarla

Tu Tabla 2 tiene la autonomía como `[[medir]]`. Un **INA219** (USD 3) en el riel de 5 V te da
**watios-hora por sesión de observación medidos**, no estimados. Encaja perfecto con tu
argumento de portabilidad y autonomía en campo.

### 5.5. El "modo degradado" como idea de discusión

La propuesta plantea una pregunta buena: *"¿qué hace el telescopio si la nube no contesta?"*
Tu sistema ya es inmune a eso, porque la Raspberry Pi crea su propia red Wi-Fi y calcula las
efemérides localmente. **Eso es una fortaleza de tu diseño que hoy no estás destacando** en
la discusión. Vale un párrafo.

---

## 6. Riesgos y puntos a verificar del documento

1. **Nada está medido todavía.** La Figura 5 lo dice con todas las letras: *"DATA IS
   SYNTHETIC, NOT MEASURED"*. Es honesto y es buena práctica (valida el pipeline
   estadístico), pero significa que la propuesta está en el punto cero.
2. **La condición del acelerador puede quedarse sin medir**, por el tema del compilador x86.
   Es el riesgo que la propia propuesta identifica, y es justo el corazón del segundo paper.
3. **Las 31 referencias habría que verificarlas una por una**, como hicimos con las tuyas en
   [`01-diagnostico-articulo.md`](01-diagnostico-articulo.md). Varias son de 2026 y algunas
   son preprints de arXiv sin publicar. No verifiqué ninguna.
4. **Dos revistas IEEE es otra liga.** *IEEE TIM* e *IEEE IoT Journal* son revistas de alto
   impacto con revisión exigente, muy por encima de lo que pide un artículo de titulación.
5. **La autoría no está definida** y el documento no está firmado.

---

## 7. Recomendación

**Sigue con tu proyecto.** Tienes el artículo armado en el formato de la revista, el diseño
mecánico verificado, el software con 37 pruebas pasando, el hardware comprado y las piezas en
camino. Lo único que falta es **medir**. Cambiarse ahora significa volver al mes cero,
gastar unos USD 540–610 más y apuntar a un entregable mucho más grande del que te piden.

**Toma prestadas las cinco ideas de la §5.** La de la cámara, sobre todo: cuesta USD 25 y
arregla la debilidad metodológica que tu propio artículo ya confiesa.

**Y guarda la propuesta como trabajo futuro.** Tu artículo ya cierra con *"se propone
incorporar una cámara para centrar el objeto automáticamente mediante visión por
computadora"*. La propuesta del ingeniero es exactamente la continuación natural de esa
frase. Citarla como línea futura, con él como coautor de esa etapa, es una salida que suma
para los dos.

### Preguntas para el ingeniero

Antes de decidir nada, conviene aclarar tres cosas:

1. **¿Qué es esto para mi tesis?** ¿Un reemplazo, un proyecto paralelo al que me invita, o
   una hoja de ruta de trabajo futuro?
2. **¿Quién pone el hardware?** La propuesta da por disponibles una Pi 5 y dos NEMA 17 que
   son suyos, no míos.
3. **Si participo, ¿cuál es mi autoría?** El documento está con nombres en blanco.

Y una observación: la propuesta **ya reconoce que la transmisión por correa de mi montura es
lo que compra exactitud**. Vale la pena preguntarle si no conviene que su instrumento la
incorpore, o que mi montura sea la plataforma mecánica de su estudio. Sería la forma de que
los dos trabajos se sumen en vez de competir.

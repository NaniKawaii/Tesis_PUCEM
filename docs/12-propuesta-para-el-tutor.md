# Propuesta de enfoque del artículo, para revisión del tutor

**Para:** Ing. Alex Ricaurte, tutor  
**De:** Nashla Carolina Tuma Zambrano · ntuma6749@pucesm.edu.ec  
**Carrera de Software · Unidad de Integración Curricular · PUCE Sede Manabí**  
**Fecha:** 17 de noviembre de 2026

---

## 1. Propósito de este documento

Ingeniero, le escribo en dos sentidos: **ponerlo al tanto del estado del trabajo**, ahora que
asume la tutoría, y **pedirle su criterio sobre un ajuste de enfoque** que propongo antes de
entrar a la fase de campo.

El documento es breve y está organizado para que pueda revisarlo por partes. Al final hay
**seis preguntas concretas**. La tercera es la que más me importa: si a su juicio el aporte
que propongo es suficiente para el artículo, o si considera que debería ampliarse.

**En una frase, lo que propongo demostrar:**

> Un corrector de aprendizaje automático entrenado sobre el **residuo** del modelo clásico de
> apuntado reduce el error de una montura altacimutal de bajo costo construida con impresión
> 3D, y se cuantifica cuántas noches de observación reales hacen falta para lograrlo.

---

## 2. Estado del trabajo

Para que tenga el panorama completo, esto es lo que ya existe:

| | Estado |
|---|---|
| **Montura** | 13 piezas diseñadas de forma paramétrica, con verificación por computadora de que no hay interferencias en todo el recorrido del tubo. Archivos STL listos para imprimir |
| **Electrónica** | Esquema de conexiones cable por cable, plano de cableado interno y procedimiento de prueba de banco en 11 pasos |
| **Software** | Modelo de error paramétrico, simulador, registrador y cuatro modelos de aprendizaje con validación dejando una noche fuera. 101 pruebas automáticas |
| **Compras** | Componentes principales adquiridos. Pendientes las poleas de transmisión, el rodamiento giratorio y la cámara |
| **Artículo** | Redactado en el formato de la revista Esprint Investigación, con la bibliografía verificada. Pendiente de rehacer la metodología y los resultados según el enfoque que aquí propongo |
| **Campo** | **Sin empezar.** Es lo que viene |

Todo el material está documentado y disponible para su revisión: diseño mecánico, código,
datos de simulación y el registro fechado de cada decisión.

---

## 3. Por qué propongo un ajuste de enfoque

El enfoque aprobado inicialmente sostenía que **el preentrenamiento en simulación con
aleatorización de dominio reduciría el número de noches de observación reales** necesarias
para corregir el apuntado.

Antes de construir el prototipo implementé el simulador y puse a prueba esa hipótesis. Ensayé
**tres variantes, y las tres dieron resultado negativo**:

| Variante | Resultado medido |
|---|---|
| Transferencia directa del residuo | **Empeora** el error en todos los casos. La correlación entre lo predicho y el error real fue de **−0,003**: un modelo entrenado sobre monturas diversas solo puede predecir la media de la familia, porque nada en su entrada le dice a qué montura se enfrenta |
| Condicionamiento con 6 puntos de sondeo | Pareció funcionar (correlación +0,66; azimut de 3,70′ a 2,86′), pero **era una semilla afortunada**: al repetirlo con otras monturas sorteadas de la misma distribución se sostuvo en 4 de 6 y se invirtió en 2. La correlación oscilaba entre 0,009 y 0,737 según la semilla |
| Sondeo repartido por todo el cielo | **Peor**, por dos causas identificadas: los apuntados a altitud alta corrompen la alineación de sesión por el factor tan(*h*), y el reajuste con 6 puntos queda mal condicionado porque sec(*h*) y tan(*h*) son casi colineales, con coeficientes que al extrapolar dan RMS superior a 1 000′ |

Preferí detenerme y medirlo antes que descubrirlo en campo, cuando ya no habría tiempo de
corregir el rumbo.

De este proceso salió una **regla metodológica** que adopté para todo el trabajo y que creo
que vale la pena declarar en el artículo:

> Una prueba de Wilcoxon sobre las noches de *una* montura responde si el efecto es consistente
> entre esas noches. **No** responde si se repetiría con *otra* montura. Son dos preguntas
> distintas, y la segunda solo se contesta repitiendo el experimento completo con varias
> monturas sorteadas de forma independiente.

Por eso todo experimento diseñado en simulación se repite ahora con varios sorteos y se
informa **en cuántos se sostiene**, no solo el valor de p.

### Lo que sí se sostuvo

**En 6 de 6 sorteos independientes, el corrector aprendido sobre el residuo venció al modelo
clásico de apuntado**: mediana de 3,93′ a 3,50′, con p < 0,05 en 4 de esos 6. Ese es el
resultado que propongo como aporte del artículo.

---

## 4. El enfoque que propongo

### Título (16 palabras, sin abreviaturas, dentro del límite de la revista)

> **Corrección del apuntado de una montura altacimutal de bajo costo con aprendizaje automático
> sobre el residuo**

El título vigente ("Sistema inteligente de posicionamiento y seguimiento de objetos celestes
mediante aprendizaje automático e interfaz de control web") promete más de lo que el artículo
demuestra: dice "objetos celestes" cuando el estudio es sobre la Luna, y "interfaz de control
web" cuando la interfaz dejó de ser objeto de estudio.

### Pregunta de investigación

> ¿En qué medida un modelo de aprendizaje automático entrenado sobre el residuo del modelo
> clásico de apuntado reduce el error de una montura altacimutal de bajo costo, y cuántas
> noches de observación hacen falta para lograrlo?

### Objetivo general

> Determinar en qué medida un corrector de aprendizaje automático entrenado sobre el residuo
> del modelo clásico reduce el error de apuntado de una montura altacimutal de bajo costo
> construida con impresión 3D, y cuántas noches de observación reales requiere.

### Objetivos específicos (uno por experimento)

1. Caracterizar el error de apuntado y seguimiento de la montura construida. → **E1**
2. Comparar la transformada de Hough con un detector aprendido como instrumento de medida del
   centro lunar. → **E2**
3. Comparar Ridge, LightGBM y MLP en la corrección del error residual con datos reales. → **E3**
4. Cuantificar la curva de error frente al número de noches de entrenamiento con datos reales.
   → **E4**
5. Validar el sistema completo en lazo cerrado durante seguimiento continuo. → **E5**

### Hipótesis

| | Enunciado | Experimento |
|---|---|---|
| **H1** | El error de apuntado de la montura impresa es sistemático: el modelo clásico explica una parte y queda un residuo no lineal apreciable | E1 |
| **H2** | Los modelos no lineales (LightGBM, MLP) reducen el error residual más que la regresión Ridge | E3 |
| **H3** | Un detector aprendido mide el centro lunar con menor error y menos fallos que la transformada de Hough, sobre todo en fases delgadas | E2 |

La hipótesis del preentrenamiento se retira sin reemplazo. El objetivo 4 queda sin hipótesis
asociada, por ser descriptivo.

---

## 5. Decisión metodológica central

**La inteligencia artificial aprende el residuo, no la posición.**

```
  Skyfield          Modelo de apuntado        Corrector ML         Montura
 (efemérides)     clásico (trigonométrico)     (el residuo)
      │                     │                       │                 │
  alt/az ──────▶  resta los términos  ─────▶  predice lo que  ────▶  pasos de
  verdaderos       conocidos de la montura      queda sin explicar    los motores
                                                       ▲
                                                       │ error medido
                        Cámara + detector ─────────────┘
```

Skyfield calcula la posición de la Luna con precisión de segundos de arco a partir de las
efemérides del Jet Propulsion Laboratory. Entrenar una red para competir con eso sería
resolver un problema ya resuelto. Lo que ningún modelo físico sabe es cuánto flexiona *este*
PETG, cuánta holgura tienen *estas* reducciones impresas y cuánto está desnivelado *este*
trípode.

Primero se ajustan por mínimos cuadrados los términos clásicos conocidos de una montura
altacimutal (desfases de índice, desnivel del eje de azimut, no perpendicularidad entre ejes y
del eje óptico, flexión del tubo) y la inteligencia artificial aprende solo lo que queda. Es el
procedimiento de **Mu et al. (2026)** y **Hu y Zhu (2026)**, de modo que cada decisión tiene
respaldo bibliográfico.

### Los cuatro términos del error, y cómo se trata cada uno

| Término | Tratamiento |
|---|---|
| **Error periódico** | Se captura un campo a intervalos fijos durante una vuelta entera del eje y se ajusta una serie de Fourier al residuo |
| **Flexión** | Varía con la altitud. Se caracteriza con una corrida sobre una rejilla de altitudes y un polinomio de orden bajo |
| **Refracción atmosférica** | **No se aprende**: se calcula con la presión y la temperatura locales y un modelo atmosférico estándar, y se aplica como corrección previa |
| **Backlash y fricción estática** | No se modelan, **se acotan**: todo movimiento comandado llega al objetivo desde la misma dirección, de modo que la histéresis residual queda medida y no estimada |

### Error de sesión frente a error persistente

Esta distinción define el protocolo de medición:

| Tipo | Términos | Cuándo cambia |
|---|---|---|
| **De sesión** | Desfases de índice, desnivel del trípode, cero de azimut | **Cada vez que se arma el equipo** |
| **Persistente** | Flexión, holgura de las reducciones, no perpendicularidad, deriva térmica | Son propiedades de *esta* montura |

Lo de sesión **se calibra**, con una alineación rápida de 2 o 3 puntos al inicio de cada
sesión, más la lectura directa del desnivel con el acelerómetro. Lo persistente **es lo que
aprende el modelo**, y es lo único que se transfiere de una noche a otra.

De aquí sale un argumento que creo que fortalece la justificación del trabajo: un observatorio
atornilla el telescopio a un pilar y su modelo de apuntado vale meses. **Una montura portátil
se vuelve a nivelar cada atardecer.** Si corregirla exigiera muchas noches de datos, el método
sería inútil en la práctica. Que baste con pocas no es una curiosidad académica: decide si el
método sirve o no para equipo portátil.

---

## 6. Diseño experimental

| | Experimento | Qué se mide | Estadística |
|---|---|---|---|
| **E1** | Caracterización del error de la montura | Media, DE, RMS, mediana, IC 95 % | Bootstrap agrupado por noche. Desglose por zona del cielo, fase lunar y temperatura |
| **E2** | Hough frente a detector aprendido | Error del centro (px y ′), % de no detección, fps | Wilcoxon pareado, agrupado por noche |
| **E3** | Ridge / LightGBM / MLP | Error residual RMS (′) | Friedman + Nemenyi, k = 3 |
| **E4** | Curva de error frente al número de noches | RMS contra N noches | Wilcoxon pareado entre N consecutivos |
| **E5** | Sistema completo en lazo cerrado | % del tiempo con la Luna centrada; RMS de seguimiento | Wilcoxon pareado entre tres modos |

Dos salvaguardas metodológicas que quiero señalarle:

- **Validación dejando una noche fuera**, nunca partición aleatoria de filas: dos filas
  consecutivas del mismo minuto son casi la misma observación, y mezclarlas infla el resultado.
- **La posición de verificación la resuelve un procedimiento distinto del que usa el corrector.**
  Si midiera el error con el mismo modelo que lo corrige, un sesgo sistemático quedaría
  enmascarado y el resultado no sería válido.

### Cuántas noches hacen falta

| Noches | Clásico | Aprendido | Gana el aprendido | Con p < 0,05 |
|---|---|---|---|---|
| 6 | 3,78′ | 3,56′ | 5 de 6 sorteos | **0 de 6** |
| 8 | 3,93′ | 3,50′ | **6 de 6 sorteos** | **4 de 6** |

Con 5 noches, una prueba de Wilcoxon pareada **no puede** dar p < 0,05 aunque las cinco
apunten en la misma dirección: el mínimo posible a dos colas es 0,0625. Con 6 el mínimo baja a
0,031, pero la medición de arriba muestra que en la práctica no se alcanza.

**Por eso las 8 noches son un requisito, no un objetivo deseable.** Planifico diez para que
queden ocho.

---

## 7. Lo que propongo retirar, y una consulta administrativa

| Se retira | Razón |
|---|---|
| **Estudio de usabilidad con 20 participantes y escala SUS** | La rúbrica del lector **no contiene ningún ítem de usabilidad**, y el estudio consume semanas de las que no dispongo |
| Predicción de trayectoria (Kalman / LSTM) | Skyfield ya predice la Luna con precisión de segundos de arco |
| Aprendizaje por refuerzo | Es un proyecto de investigación en sí mismo |

Nada de esto se descarta del trabajo: todo pasa a la sección de **trabajo futuro**.

> **Consulta:** retirar el estudio de usabilidad modifica uno de los objetivos del plan de
> titulación aprobado, y el título cambia. **¿Esto requiere algún trámite ante la Unidad de
> Integración Curricular?**

---

## 8. Instrumento de medida y cronograma

### La cámara

Seleccioné una **Raspberry Pi HQ Camera con lente de 25–28 mm** (USD 50–90). El criterio
decisivo fue el campo de visión, no la resolución: el error de apuntado antes de corregir es
del orden de 1°, y un campo estrecho dejaría la Luna fuera del cuadro en buena parte de los
apuntados. Con 13° × 10° la Luna siempre queda dentro, y la escala de ~12″/píxel sobra para
medir un efecto de 26″ mediante ajuste de círculo al limbo lunar.

### Cronograma: quedan 13,6 semanas (17/11/2026 → 19/02/2027)

| Semana | Fechas | Actividad |
|---|---|---|
| 1 | 17–22 nov | Compras pendientes; medición de piezas; impresión de la pieza de prueba |
| 2 | 23–29 nov | Impresión de las 13 piezas; scripts de análisis sobre datos sintéticos |
| 3 | 30 nov–6 dic | Armado mecánico y cableado; prueba de banco de 11 pasos |
| 4 | 7–13 dic | Montaje de la cámara, calibración de escala de placa, balanceo |
| 5 | 14–20 dic | **Primera sesión de prueba. Hito de no retorno** |
| 6–10 | 21 dic–24 ene | **Campaña de observación: 8 noches**, incluyendo sesiones con la Luna de día |
| 11 | 25–31 ene | Análisis E1–E5; tablas y figuras definitivas |
| 12–13 | 1–14 feb | Redacción de Resultados, Discusión y Conclusiones |
| 13,5 | 15–19 feb | Revisión, correcciones, maquetación y entrega |

**Riesgos que asumo y declaro:** la campaña de observación cae sobre las fiestas de fin de
año, y enero es temporada lluviosa en Portoviejo. Dos medidas lo mitigan: incluir sesiones
**con la Luna de día**, que duplican las ventanas de medición, y un **plan B** si el armado se
atrasa, que consiste en caracterizar el error contra blancos terrestres a posiciones conocidas,
ya que E1, E3 y E4 miden el error *de la montura*, no del cielo.

---

## 9. Preguntas concretas

1. **¿Aprueba el cambio de enfoque** y el título propuesto de 16 palabras?
2. **¿El cambio de título, el retiro del estudio de usabilidad y la modificación del objetivo 4
   requieren trámite** ante la Unidad de Integración Curricular?
3. **¿Considera que este aporte es suficiente para el artículo**, o estima que debería
   ampliarse? Si cree que falta algo, le agradecería que me indique qué, para evaluar si cabe
   en las semanas disponibles.
4. **¿Está de acuerdo con fijar 8 noches como requisito** y con el plan B de blancos terrestres
   si el armado se atrasa?
5. **¿Desea figurar como coautor del artículo?** Lo pregunto porque la revista exige declarar
   la contribución de cada autor con la taxonomía CRediT, y necesito saberlo antes de la
   redacción final.
6. **¿Cómo prefiere que le reporte los avances?** Propongo una revisión al cierre de cada hito
   del cronograma, pero me adapto a lo que a usted le resulte práctico.

Quedo atenta a sus observaciones, y a su disposición para reunirnos cuando lo considere
oportuno.

Atentamente,

**Nashla Carolina Tuma Zambrano**  
ntuma6749@pucesm.edu.ec

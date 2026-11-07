# Paso 8 · Diseño definitivo del artículo

Diseño de investigación aprobado el **06/11/2026**. Sustituye el alcance de tres módulos ×
tres modelos × tres formas de entrenar que estaba en `MEMORIA.md`, y sustituye la §5 de
[`07-rubrica-lector.md`](07-rubrica-lector.md).

Dos restricciones lo determinan todo: **15 semanas** (hasta ~19/02/2027) y una rúbrica donde
el **57 % de la nota** exige datos medidos reales.

---

## 1. El aporte, en una frase

> **Pre-entrenar en simulación con aleatorización de dominio reduce la cantidad de noches de
> observación reales que hace falta para que un modelo de aprendizaje automático corrija el
> error de apuntado de una montura altacimutal de bajo costo.**

### Por qué este aporte y no otro

Búsqueda en Scopus del 06/11/2026, con la cuenta de la PUCE:

| Cadena | Resultados | Pertinentes |
|---|---|---|
| bajo costo / Raspberry Pi / impreso en 3D + montura + error de apuntado + ML | **1** | **0** (revisión en chino sobre SLAM visual-inercial y RA) |
| telescopio + error de apuntado + ML (**el núcleo del tema**) | **12** | ~9, todos instrumentos profesionales |
| sim-to-real / aleatorización de dominio / datos sintéticos + apuntado | **3** | **0** |
| eficiencia de datos + apuntado | **6** | **1** (Bergerhoff 2024, antenas) |
| bajo costo + telescopio + IA | 72 | 0 sobre control de montura (todo es análisis de imágenes) |

Tres lecturas:

1. **El campo núcleo tiene doce papeles en toda Scopus.** No es un tema saturado: es un tema
   naciente. Y nueve de esos doce son el South Pole Telescope, MeerKAT+, el Changchun de 1 m,
   SONG y otros radiotelescopios. **Ninguno en una montura de bajo costo.**
2. **El cruce simulación-a-realidad × apuntado está vacío.** Es la brecha.
3. La brecha se puede **afirmar con evidencia verificable** en la introducción, citando la
   cadena y el número de resultados. Eso es exactamente el ítem 8 de la rúbrica.

### Por qué encaja en 15 semanas

Porque **el grueso del trabajo de IA no necesita hardware ni cielo.** El simulador, el
pipeline de entrenamiento, la comparación de modelos y los scripts de estadística y figuras
se construyen y validan con datos sintéticos, en paralelo a la impresión de la montura. Las
noches reales dejan de ser la fuente principal de datos y pasan a ser la **prueba de
transferencia**, que necesita pocas.

Dicho de otro modo: con el enfoque anterior, cada noche nublada era una pérdida. Con este,
el número de noches **es la variable que se mide**.

### Por qué esto califica como investigación original

| Criterio de un artículo de investigación | Verdicto | Evidencia |
|---|---|---|
| Hay una **pregunta contestable y todavía no contestada** | ✅ | Scopus, 06/11/2026: "sim-to-real + apuntado" = 3 documentos, **0 pertinentes**; el campo núcleo = 12 documentos, **0 en monturas de bajo costo** |
| El aporte es **metodológico**, no solo una aplicación | ✅ | No se propone "usar IA para apuntar" (eso ya está hecho), sino **cómo entrenarla con menos datos reales** |
| El resultado es **medible y falsable** | ✅ | H3 puede resultar falsa: si el preentrenamiento no reduce las noches, se rechaza. **Y seguiría siendo publicable**, porque un fallo de transferencia también es un hallazgo |
| Es **reproducible** | ✅ | Código abierto, rangos de aleatorización declarados, dataset en Zenodo con DOI, protocolo de sesión fijo |
| Admite **discusión científica** (ítem 4) | ✅ | Hay tensión real: ¿conviene invertir dos semanas en un simulador o cinco noches más de observación? ¿Un simulador con un modelo de error equivocado ayuda o estorba? |
| **No es conocimiento popular** | ✅ | Ver el contraste de abajo |

**Dónde está la frontera entre lo conocido y lo nuevo.** Esto importa, porque el artículo **no
debe gastar páginas** en lo de la izquierda:

| Ya es conocimiento establecido (va en una frase, con cita) | Lo que este artículo aporta |
|---|---|
| Mover un telescopio con motores paso a paso y una Raspberry Pi — hay cientos de proyectos y OnStep lo resuelve | — |
| Calcular efemérides con Skyfield | — |
| Detectar objetos con YOLO o con la transformada de Hough | — |
| Que un modelo de apuntado clásico corrige el error sistemático de un telescopio | — |
| Que el aprendizaje automático mejora ese modelo **en instrumentos profesionales** (los 12 papeles de §1) | — |
| Que la aleatorización de dominio sirve para transferir de simulación a realidad **en robótica** (Tobin 2017) | — |
| | **Cuántas noches reales se ahorran al preentrenar en simulación el corrector de apuntado de una montura de bajo costo. Nadie lo ha medido.** |

> ⚠️ **Riesgo para la afirmación de novedad.** El trabajo más cercano es **Bergerhoff (2024)**,
> sobre calibración eficiente del apuntado de una antena tratada como caja negra. Hay que
> leerlo y **posicionarse explícitamente frente a él** en la Introducción. Si ya hiciera la
> comparación de eficiencia de datos, la novedad de este artículo se estrecha a la montura de
> bajo costo impresa en 3D y al preentrenamiento en simulación — sigue siendo novedad, pero hay
> que decirlo con precisión y no de más.

> ⚠️ **Limitación que un lector va a levantar:** es **una sola montura**. El resultado no
> generaliza por sí solo. Mitigación: declararlo en la Discusión (lo que **suma** en el ítem 25)
> y publicar los rangos de aleatorización para que otros repliquen.

---

## 2. Pregunta, hipótesis y objetivos

**Pregunta.** ¿En qué medida el pre-entrenamiento en simulación con aleatorización de dominio
reduce el número de noches de observación reales necesarias para que un modelo de aprendizaje
automático corrija el error de apuntado y seguimiento de una montura altacimutal de bajo
costo por debajo del campo visual del instrumento?

**Hipótesis.**

| | Enunciado | Se prueba en |
|---|---|---|
| **H1** | El error de apuntado de la montura impresa es sistemático: un modelo de apuntado clásico explica una parte y queda un residuo no lineal apreciable | E1 |
| **H2** | Los modelos no lineales (LightGBM, MLP) reducen el error residual más que la regresión Ridge | E3 |
| **H3** | El pre-entrenamiento en simulación alcanza un error dado con **menos noches reales** que el entrenamiento solo con datos reales | **E4 (el aporte)** |
| **H4** | Un detector aprendido mide el centro lunar con menor error y menos fallos que la transformada de Hough, sobre todo en fases delgadas | E2 |

**Objetivo general.** Determinar en qué medida el pre-entrenamiento en simulación con
aleatorización de dominio reduce las noches reales necesarias para corregir con aprendizaje
automático el error de apuntado de una montura altacimutal de bajo costo.

**Objetivos específicos** — uno por experimento, sin excepción. Un objetivo sin resultado es
un "No" en el ítem 28.

1. Caracterizar el error de apuntado y seguimiento de la montura construida. → E1
2. Comparar la transformada de Hough con un detector aprendido como instrumento de medida del
   centro lunar. → E2
3. Comparar Ridge, LightGBM y MLP en la corrección del error residual con datos reales. → E3
4. Cuantificar la curva de error frente al número de noches de entrenamiento, para datos
   reales y para pre-entrenamiento en simulación con ajuste fino. → E4
5. Validar el sistema completo en lazo cerrado durante seguimiento continuo. → E5

---

## 3. La arquitectura: la IA aprende el **residuo**, no la posición

Esta es la decisión técnica central del artículo.

```
  Skyfield            Modelo de apuntado           Corrector ML           Montura
 (efemérides)      clásico (trigonométrico)      (el residuo)
      │                      │                        │                     │
  alt/az ───────▶  resta los términos  ───────▶  predice lo que  ──────▶  pasos de
  verdaderos        conocidos de la montura        queda sin explicar      los motores
                                                         ▲
                                                         │ error medido
                        Cámara + detector  ──────────────┘
                     (mide dónde está la Luna de verdad)
```

**Por qué no predecir la posición.** Skyfield calcula la posición de la Luna con precisión de
segundos de arco. Entrenar una red para competir con eso es resolver un problema resuelto, y
un lector que conozca el tema lo va a señalar en los ítems 13 y 25. Lo que ningún modelo
físico sabe es cuánto se flexiona el PETG de *esta* montura, cuánta holgura tienen *estas*
reducciones impresas y cuánto está desnivelado *este* trípode.

**Por qué hay un modelo clásico en medio.** Los términos sistemáticos de una montura
altacimutal son conocidos y se ajustan por mínimos cuadrados: desfases de índice en los dos
ejes, desnivel del eje de azimut en sus dos componentes, no perpendicularidad entre ejes, no
perpendicularidad del eje óptico y flexión del tubo. Quitar primero lo que un modelo lineal
explica y dejar que la IA aprenda solo el resto es lo que hacen **Mu et al. (2026)** y
**Hu y Zhu (2026)**, así que cada decisión tiene cita. Eso resuelve el ítem 13.

> Pendiente: tomar la nomenclatura y la cita de los términos del modelo clásico de uno de esos
> dos artículos al redactar la metodología, no de memoria.

**Entradas del corrector:** azimut y altitud comandados (y sus senos y cosenos), sentido del
último giro de cada eje (para la holgura), temperatura y presión del BMP280, inclinación del
GY-91 y ángulo medido por el AS5600.
**Salidas:** Δaz·cos(alt) y Δalt, en minutos de arco.

**Orden de modelos**, de menos a más, que es el orden defendible:

| # | Modelo | Papel |
|---|---|---|
| 0 | Modelo clásico solo | Línea base física |
| 1 | **Ridge** sobre los términos trigonométricos | Línea base lineal |
| 2 | **LightGBM** | No lineal, tabular, barato de entrenar |
| 3 | **MLP** pequeño | No lineal, comparable con la literatura |

**Nada de LSTM.** Es un problema de regresión, no de secuencia. Un LSTM aquí añade
complejidad sin justificación y cuesta puntos en el ítem 13.

**Validación: dejando una noche fuera.** Nunca partición aleatoria de filas. Dos filas
consecutivas del mismo minuto son casi la misma observación; mezclarlas infla el resultado y
es el error metodológico más fácil de detectar en una revisión.

### Error de sesión frente a error persistente

No todos los términos del error se comportan igual, y la diferencia decide el protocolo de
medición. Esta distinción se incorporó el 06/11/2026, a raíz de una pregunta de Nashla.

| Tipo | Términos | Cuándo cambia |
|---|---|---|
| **De sesión** | Desfases de índice en los dos ejes, desnivel del trípode (dos componentes), cero de azimut | **Cada vez que se arma el equipo.** Son distintos en cada sesión |
| **Persistente** | Flexión de la estructura, holgura de las reducciones, no perpendicularidad de ejes, deriva térmica | Son propiedades de *esta* montura. Se mantienen entre sesiones |

Esto parte el problema en dos, y cada mitad se resuelve de forma distinta:

- **Lo de sesión se calibra, no se aprende.** Cada sesión empieza con una alineación rápida
  sobre 2 o 3 puntos conocidos, que ajusta por mínimos cuadrados solo esos cuatro o cinco
  términos. Además, **el acelerómetro del GY-91 mide el desnivel del trípode directamente**, así
  que dos de ellos se leen en vez de ajustarse. Es lo mismo que hace cualquier montura comercial
  con su alineación de dos o tres estrellas.
- **Lo persistente es lo que aprende la IA.** Es el residuo no lineal que queda después de la
  alineación, y es lo único que de verdad se transfiere de una noche a otra.

Dos consecuencias importantes:

1. **La validación dejando una noche fuera es válida precisamente por esta separación.** Si se
   entrenara sobre el error crudo, el modelo intentaría memorizar los desfases de la noche 1,
   que no sirven para la noche 6. Entrenando sobre el residuo posterior a la alineación, lo
   aprendido sí es comparable entre noches.
2. **Refuerza el aporte del artículo.** Un observatorio atornilla el telescopio a un pilar y su
   modelo de apuntado vale durante meses. Una montura portátil se vuelve a nivelar cada
   atardecer. Si corregirla exigiera ocho noches de datos, el método sería inútil en la
   práctica. Que baste con pocas no es una curiosidad académica: **es lo que decide si el
   método sirve o no para equipo portátil.** Esto va en la Introducción como justificación.

---

## 4. El simulador y la aleatorización de dominio

Es lo nuevo que hay que escribir, y lo primero, porque no depende de nada.

### Para qué sirve la simulación (y qué NO aprende)

> **La simulación no sirve para aprender el cielo. El cielo ya está resuelto.**

Skyfield calcula la posición de la Luna con precisión de segundos de arco, a partir de las
efemérides DE421, de forma determinista. No hay nada que aprender ahí, y entrenar una red para
competir con eso sería absurdo. En el simulador, **el cielo es la entrada, no lo que se
aprende**: Skyfield genera las posiciones verdaderas y encima se le aplica el error.

Lo que se aprende es **el error de la montura**: la función que dice cuánto se desvía el
apuntado según hacia dónde se apunte.

**Por qué esa función es difícil de aprender con pocos datos.** El error depende de la
dirección: en unas zonas del cielo es grande y en otras pequeño. Para aprender la función
completa hay que haberla visto en muchas direcciones. Pero **una noche de seguimiento lunar es
un solo arco**, una línea delgada que cruza la bóveda, no la bóveda entera. Cada noche aporta
una franja distinta según la fecha y la fase. Por eso hacen falta muchas noches: no por
cantidad de filas —sobran, 20 000 por noche— sino por **cobertura del cielo**.

**Qué aporta entonces el pre-entrenamiento.** El simulador genera miles de monturas sintéticas,
cada una con su vector de parámetros, y de cada una la función de error completa sobre **toda**
la bóveda, al instante. Entrenando sobre eso, el modelo no aprende *una* montura: aprende
**qué forma tienen las funciones de error de apuntado** en general — que son suaves, que tienen
cierta estructura trigonométrica, que la holgura aparece como un salto según el sentido de
giro, que la flexión crece hacia el horizonte.

Cuando después llega a la montura real, ya no tiene que descubrir la forma desde cero: solo
tiene que averiguar **cuál miembro de esa familia es tu montura**. Y eso se resuelve con muy
pocos datos.

La analogía que lo deja claro: alguien que ha visto miles de caras necesita dos fotos para
reconocer a una persona nueva. Alguien que nunca ha visto una cara necesita muchísimas más.
El pre-entrenamiento no te enseña tu montura: te enseña *qué es una montura*.

### "¿Y si el trípode funciona bien?"

Dos respuestas, y conviene tenerlas a mano para la defensa:

1. **"Bien" a ojo no es bien para la cámara.** Un armado cuidadoso deja un error del orden de
   1°. El campo visual con el que se mide es de unos **17′ × 10′**. O sea que lo que a simple
   vista parece perfectamente alineado está, para el instrumento, entre tres y seis veces fuera.
   El error que importa es invisible a ojo.
2. **Si la montura fuera perfecta, no habría proyecto.** El error no desaparece con buen
   armado: los NEMA 23 pesan ~1 kg cada uno y flexionan el PETG, las correas y reducciones
   impresas tienen holgura, el trípode nunca queda perfectamente a nivel y **la referencia
   inicial tiene un desfase distinto en cada montaje**. Eso último es la clave: el error se
   vuelve a crear cada vez que se arma el equipo (ver §3, error de sesión frente a persistente).

**Qué hace.** Para una fecha, una hora y el sitio (Portoviejo, ~1° S), Skyfield da el alt/az
verdadero de la Luna. Encima se aplica un modelo de error con un vector de parámetros, más los
efectos no lineales:

| Efecto | Cómo se simula |
|---|---|
| Desnivel del trípode | Dos componentes de inclinación del eje de azimut |
| Desfase de la referencia inicial | Desplazamiento constante por eje |
| Flexión de la estructura | Término dependiente de la altitud |
| No perpendicularidad de ejes | Término cruzado |
| **Holgura de las reducciones impresas** | Histéresis dependiente del sentido de giro |
| Cuantización | Redondeo al micropaso (0,48′ en azimut, 1,35′ en altitud) |
| Deriva térmica | Término lento proporcional a la temperatura |
| Ruido de medida | Ruido del encoder y del detector |

**La aleatorización de dominio.** Cada "noche sintética" se genera con un **vector de
parámetros distinto**, muestreado en rangos amplios y declarados (por ejemplo, desnivel de 0 a
1°, flexión de 0 a 10′, holgura de 0 a 3′). Así el modelo no aprende *una* montura: aprende la
**familia** de monturas de bajo costo. Esa es la idea de Tobin et al. (2017), y es la que
permite que lo aprendido en simulación transfiera a la montura real.

**Requisito de diseño que no se negocia:** el simulador escribe **el mismo esquema de CSV**
que el registrador real. Así el pipeline de entrenamiento, validación, estadística y figuras
es **uno solo**, y lo que se valida con datos sintéticos sirve tal cual con datos reales. Esto
es lo que hace que las semanas 1 a 6 sean productivas sin hardware.

Sobre `astro.py`, `montura.py` y `correccion.py`, que ya existen, esto son unas 200 líneas.

---

## 5. Datos

**Dataset real.** Una fila por segundo, ~20 000 filas por noche:

| Grupo | Columnas |
|---|---|
| Tiempo y sitio | marca de tiempo UTC, latitud, longitud, altura |
| Verdad de referencia | azimut y altitud de Skyfield |
| Estado de la montura | az/alt comandados, pasos por eje, sentido del último giro, ángulo del AS5600 |
| Ambiente | temperatura y presión (BMP280), inclinación (GY-91) |
| Medición | centro detectado en píxeles, Δaz·cos(alt) y Δalt en minutos de arco |
| Contexto | fase lunar, altitud de la Luna, calidad del fotograma |

**Imágenes para el detector:** una cada 10 s. Etiquetado automático con ajuste de círculo más
la posición de Skyfield; se revisan a mano unas 300. Las imágenes van a **Zenodo con DOI**, no
al repositorio.

**Las etiquetas salen casi gratis**, y vale la pena decirlo en la metodología: Skyfield dice
dónde *debería* estar la Luna y el ajuste de círculo dice dónde se ve. Eso convierte el
etiquetado de un cuello de botella en un paso automático.

**Regla, repetida porque es la que más se olvida:** la separación entre entrenamiento y prueba
es **por noche**.

---

## 6. Experimentos y estadística

**Protocolo de cada sesión**, fijo para todas: nivelar, encender, leer el desnivel con el
GY-91, hacer la **alineación rápida sobre 2 o 3 puntos** (que ajusta solo los términos de
sesión de §3) y recién entonces empezar a registrar. Todo lo que se registra después de ese
paso es residuo persistente, y es lo único comparable entre noches.

| | Experimento | Qué se mide | Estadística |
|---|---|---|---|
| **E1** | Caracterización del error de la montura | Media, DE, **RMS**, mediana, IC 95 % | Bootstrap agrupado **por noche**. Desglose por zona del cielo, fase lunar y temperatura |
| **E2** | Hough frente a detector aprendido | Error del centro (px y ′), % de no detección, fps en la Pi | Wilcoxon pareado, agrupado por noche, estratificado por fase |
| **E3** | Ridge / LightGBM / MLP con datos reales | Error residual RMS (′) | **Friedman + Nemenyi**, k = 3, dejando una noche fuera |
| **E4** | **Noches reales frente a simulación + ajuste fino** | Curva de error RMS contra N noches de entrenamiento | **Wilcoxon pareado** por noche de prueba, en cada N |
| **E5** | Sistema completo en lazo cerrado | % del tiempo con la Luna centrada; error RMS de seguimiento | Wilcoxon pareado entre los tres modos |

E5 compara tres modos: solo efemérides · efemérides + corrector · efemérides + corrector +
corrección visual.

El desglose de E1 por zona del cielo, fase y temperatura es gratis —son los mismos datos
vistos de otra forma— y es justamente lo que convierte el ítem 17 en "Sí".

### Cuántas noches hacen falta, con números

Esto no es una opinión, sale de la prueba estadística:

- **E4 necesita 6 noches como mínimo absoluto.** Con una prueba de Wilcoxon pareada de n = 5,
  el valor de p más bajo que se puede obtener a dos colas es 0,0625, **por encima de 0,05
  aunque las cinco noches apunten en la misma dirección**. Con n = 6 el mínimo es 0,031, que ya
  cruza el umbral. Cinco noches no es "poco": es matemáticamente incapaz de dar significancia.
- **E3 funciona con 6 noches.** Con k = 3 modelos y n = 6, la diferencia crítica de Nemenyi es
  ≈ 1,35 sobre un rango de rangos de 1 a 3: se separa si un modelo es consistentemente mejor.
- **Objetivo: 8 noches. Piso: 6.** Por debajo de 6 hay que replantear E4.

Y esto explica por qué se descarta cruzar los dos ejes: con 9 condiciones y 8 noches, la
diferencia crítica de Nemenyi sube a ≈ 4,3 sobre un rango de 1 a 9, y **no se separaría casi
nada**. Mantener cada comparación en 2 o 3 condiciones no es modestia: es lo que permite que
haya resultados significativos.

---

## 7. Lo que se descarta, y por qué

| Se quita | Razón |
|---|---|
| **M2: predicción de trayectoria (Kalman / LightGBM / LSTM)** | Skyfield ya predice la Luna con precisión de segundos de arco. Es un problema resuelto; pesa en los ítems 13 y 25 |
| **Aprendizaje por refuerzo (PPO)** | Es un proyecto de investigación en sí mismo. No cabe en 15 semanas, y Nousiainen et al. (2022) ya ocupó ese nicho en óptica adaptativa |
| **Cruzar modelos × formas de entrenar** | Destruye la potencia estadística (§6) |
| **Estudio de usabilidad con 20 participantes y cuestionario SUS** | La rúbrica **no tiene ningún ítem de usabilidad**, y cuesta semanas que no hay |
| **Tercera forma de entrenar** | Quedan dos: real, y simulación + ajuste fino. Es lo que se compara |

Nada de esto se tira: todo va a **trabajo futuro**, que es justo lo que pide el ítem 29.

> ⚠️ **Hay que consultarlo con el tutor.** Quitar el estudio de usabilidad cambia uno de los
> objetivos del plan de titulación aprobado. Confirmar con el Ing. Corrales antes de escribir,
> y confirmar si el cambio de título necesita trámite.

---

## 8. Título

La revista exige **máximo 18 palabras y sin abreviaturas**, y el ítem 3 de la rúbrica pide que
sea "claro y concreto".

**Qué falla en el título vigente** ("Sistema inteligente de posicionamiento y seguimiento de
objetos celestes mediante aprendizaje automático e interfaz de control web"): promete más de lo
que el artículo demuestra. Dice "objetos celestes" y el estudio es solo sobre la Luna; dice
"interfaz de control web" y la interfaz ya no es objeto de estudio. Un lector que note la
diferencia marca **P** en el ítem 3. Además, "sistema inteligente" no dice qué se investigó.

> ⚠️ Corrección del 06/11/2026: la propuesta anterior de este documento ("Entrenamiento en
> simulación para corregir el error de apuntado de una montura altacimutal de bajo costo con
> aprendizaje automático") estaba mal contada. **Tiene 19 palabras y se pasa del límite.**

### Recomendado (17 palabras)

> **Preentrenamiento en simulación para corregir el apuntado de monturas de bajo costo con
> menos noches de observación**

En inglés (13 palabras):

> *Simulation pre-training to correct the pointing of low-cost mounts with fewer observation
> nights*

Por qué este: cada bloque hace un trabajo y ninguno sobra.

| Bloque | Qué aporta |
|---|---|
| "Preentrenamiento en simulación" | El **método**, que es la novedad |
| "para corregir el apuntado" | La **tarea** |
| "de monturas de bajo costo" | El **objeto**, que es lo que no está en la literatura |
| "con menos noches de observación" | El **resultado medido**, que es el aporte |

Sin el último bloque, el título se lee como un artículo más de "IA corrige el apuntado", que es
justo el terreno ya ocupado por los doce papeles de §1. Ese bloque es lo que separa este
trabajo de ellos, y por eso no se puede quitar.

### Alternativas

| Opción | Palabras | Cuándo usarla |
|---|---|---|
| Preentrenamiento en simulación para corregir el apuntado de monturas **altacimutales** de bajo costo con menos noches de observación | **18** | Si el tutor prefiere más precisión técnica. Queda al límite exacto: no admite cambiar ni una palabra |
| Corrección del apuntado de una montura altacimutal de bajo costo con aprendizaje automático preentrenado en simulación | 16 | Más convencional y fácil de leer, pero **esconde el aporte** y se confunde con lo ya publicado |
| Aleatorización de dominio y eficiencia de datos en la corrección del apuntado de monturas de bajo costo | 17 | La más precisa para un lector especialista, pero densa para un tribunal de Ingeniería de Software |

### Comprobación: ¿el título promete lo que el artículo entrega?

| El título dice | ¿Se entrega? |
|---|---|
| Preentrenamiento en simulación | Sí: §4, y se compara contra entrenar solo con datos reales |
| Corregir el apuntado | Sí: E1, E3, E5 |
| Monturas de bajo costo | Sí, con la salvedad de que **es una sola montura**. Declararlo como limitación en la Discusión (ítem 25) |
| Menos noches de observación | Sí: E4 es exactamente esa medición |

No menciona la Luna ni la cámara, y está bien: son el **caso de prueba y el instrumento de
medida**, no el objeto de estudio. La metodología debe decirlo con todas sus letras en el primer
párrafo, para que nadie espere un estudio sobre la Luna.

---

## 9. Cronograma de 15 semanas

Semana 1 = la del 06/11/2026. Fin ≈ 19/02/2027.

| Sem. | Qué | No depende de hardware |
|---|---|---|
| 1 | Cerrar el diseño con el tutor, ajustar objetivos y título. Comprar lo que falta. Encargar `prueba_gt2.stl` | — |
| 1–2 | **Escribir el simulador y el generador de datos sintéticos** | ✅ |
| 2–3 | Imprimir el resto de piezas. Armar y cablear la electrónica. Prueba de banco (11 pasos) | |
| 2–4 | **Pipeline de ML completo sobre datos sintéticos**: los 4 modelos, validación por noche, scripts de estadística y figuras | ✅ |
| 3–4 | Captura de cámara, registrador del dataset y etiquetado automático | |
| 4–5 | Armado mecánico, balanceo y calibración | |
| 5–6 | Ajuste fino del detector con fotogramas reales (Hough frente a aprendido) | |
| 6–11 | **Observación: mínimo 6 noches, objetivo 8** | |
| 11–12 | Análisis E1–E5. Tablas y figuras definitivas | |
| 12–14 | Escribir Resultados, Discusión y Conclusiones | |
| 14 | Resumen con números y p, abstract, ORCID y CRediT | |
| 15 | Revisión del tutor, correcciones, maquetación Esprint, entrega | |
| 1–14 | ⏩ Repasar la Introducción: una cita por párrafo y frases cortas (ítems 6 y 7) | ✅ |

**Hito de no retorno: fin de la semana 5.** Si la montura no mide para entonces, se activa el
plan B.

### Cómo no depender del clima

La Luna **se ve de día** buena parte del mes, sobre todo en las tardes cercanas al primer
cuarto y en las mañanas cercanas al último. Es brillante de sobra para detectarla contra el
cielo azul con exposición corta. Eso **duplica aproximadamente las ventanas de medición** y
reduce la dependencia de noches despejadas, que en Portoviejo es un riesgo real entre enero y
abril.

Conviene incluir sesiones diurnas en el plan desde el principio, no como parche. Y declararlo
en la metodología: el error de apuntado de la montura es el mismo apunte donde apunte, así que
las sesiones diurnas son datos válidos de E1, E3 y E4.

### Plan B, si el hardware se atrasa

E1, E3 y E4 miden el error **de la montura**, no del cielo. Si el armado se atrasa, se
caracteriza el error contra **blancos a posiciones conocidas** (que hay que levantar con
teodolito o por trigonometría desde GPS) y se completan los tres experimentos sin cielo. Las
noches reales quedan solo para E5, y el artículo se escribe declarando esa limitación en la
Discusión, lo que **suma** en el ítem 25.

---

## 10. Cómo se cubre la rúbrica

| Ítems | Qué los cubre |
|---|---|
| 1–4 (Tema) | El título nuevo, y la tensión "¿vale la pena una montura de bajo costo con IA?" en la Introducción |
| 5–8 (Introducción) | Las 24 referencias + las 7 nuevas; la brecha **afirmada con la cadena de Scopus y su número de resultados** (ítem 8) |
| 9–11 (Objetivos) | Cinco objetivos específicos, uno por experimento |
| 12–13 (Metodología) | El diseño de §3 y §4, con cita por cada decisión (Mu 2026, Hu y Zhu 2026, Tobin 2017) |
| 14 | 6–8 noches × ~20 000 filas, más cientos de miles de filas sintéticas. Supera cualquier mínimo, y se dice con el número |
| 15–16 | Etiquetado automático; Friedman + Nemenyi, Wilcoxon, bootstrap agrupado por noche |
| 17 | El desglose de E1 por zona del cielo, fase lunar y temperatura |
| 18–23 (Resultados) | E1–E5, cada tabla con n, IC 95 % y p. Ningún número sin medición real |
| 24 | Comparación directa con Zhaborovskyy (2024), Mu (2026), Chichura (2025, 2026) y He et al. (2026) — **las métricas se fijan antes de medir para que sean comparables** |
| 25 | Limitaciones declaradas: una montura, un objeto, un sitio |
| 26–27 | El alcance recortado es lo que deja espacio para discutir a fondo |
| 28–31 (Conclusiones) | El hallazgo transferible: cuántas noches hacen falta con y sin simulación |
| 32 (Resumen) | Las cinco partes con números y p, ≤ 250 palabras |
| 33–35 (Bibliografía) | 31 referencias con DOI verificado, todas citadas en el texto |

---

## 11. Referencias nuevas que hay que incorporar

Encontradas en Scopus el 06/11/2026 y ausentes de la bibliografía actual. **Las dos primeras
son de lectura obligatoria antes de redactar.**

1. **He, Y., Hao, L., y Dai, W. (2026).** FinalKAN: A dual-stream KAN network integrating
   multisource features for radio telescope pointing correction. *Advances in Astronomy*,
   2026(1), 7212588. **Acceso abierto.** Lo más reciente del campo.
2. **Bergerhoff, L. (2024).** Learning antenna pointing correction in operations: Efficient
   calibration of a black box. *European Signal Processing Conference (EUSIPCO)*, 2752–2756.
   **El competidor más directo del ángulo de eficiencia de datos**, aunque sea en antenas.
3. **Chichura, P., Drlica-Wagner, A., Crawford, T., y Rahlin, A. (2026).** Telescope control
   with machine learning: Pointing corrections and observation scheduling. *USNC-URSI NRSM
   2026*, 121. Versión nueva del trabajo del South Pole Telescope que ya se cita.
4. **Pointing accuracy improvements for the South Pole Telescope with machine learning.**
   Segundo artículo del mismo grupo; completar autores y año en Scopus.
5. **Zhang, C., Bai, H., Zhang, Y., Cao, Z., y Cui, X. (2024).** Systematic optical axis
   prediction based on machine learning for SONG pointing tracking model. *Proc. SPIE*, 13100,
   131004G.
6. **Haddad-Casamayor, J. L., Bendek, E., Flor…** Optical distortion calibration using
   machine-learning for exoplanet detection. Completar datos en Scopus.
7. **Nisperuza, J., y Valencia, S. (2026).** Characterizing drift-limited performance in
   unguided astrophotography with large-aperture Newtonian telescopes. *Galaxies*. Útil para
   **comparar magnitudes de error con equipo de aficionado**.

Cadena para reproducir la búsqueda del núcleo:

```
TITLE-ABS-KEY ( ( telescope OR "pointing model" ) AND ( "pointing error" OR "pointing correction" ) AND ( "machine learning" OR "neural network" OR "deep learning" ) )
```

---

## 12. Cómo explicarlo en la sustentación

El método se entiende en diez segundos con un ejemplo que ya existe: los **robots bípedos
impresos en 3D que aprenden a caminar en un simulador**. Se entrenan decenas de copias a la vez
en física simulada, y el paso decisivo es endurecer la red sobre **terreno variado** —piedras,
escombros, pendientes— para que no aprenda *un* suelo sino la *familia* de suelos. Después la
red se carga en el robot físico y camina en el mundo real, que nunca es igual al simulador.

Es exactamente el ciclo de este artículo, y la analogía es más cercana de lo que parece: esos
robots también son impresos en 3D, con mecánica barata e imprecisa. Por eso la aleatorización
ayuda tanto; en un robot industrial de precisión apenas haría falta.

**Dónde se rompe la analogía, y conviene decirlo antes de que lo pregunten:**

| | Robot que aprende a caminar | Este artículo |
|---|---|---|
| Tipo de aprendizaje | **Refuerzo**: nadie sabe el torque correcto, hay que descubrirlo por ensayo y error | **Regresión supervisada**: la respuesta correcta se conoce para cada muestra (Skyfield + cámara) |
| Simulador | Física de cuerpos rígidos, contactos, fricción, equilibrio | Trigonometría más media docena de términos de error |
| Qué produce la red | Acciones (cuánto mover cada articulación) | Una predicción del error, en minutos de arco |

La tercera columna es la que hace que esto quepa en 15 semanas y lo otro no.

> ⚠️ **Usar la analogía para explicar, nunca para citar.** El material de divulgación no es
> fuente académica y sus cifras no son resultados. Las citas del método son **Tobin et al.
> (2017)** para la aleatorización de dominio y **Zhao et al. (2020)** para la revisión de
> simulación a realidad.

---

## 13. Pendientes inmediatos

1. **Confirmar con el tutor** el recorte, el título nuevo y la salida del estudio de
   usabilidad. Es lo primero, porque cambia objetivos aprobados.
2. **Decidir la cámara.** La rúbrica no da puntos por la cámara. Una Raspberry Pi HQ Camera
   con lente de ~28 mm da la Luna del mismo tamaño en píxeles (≈ 160 px) por 50–80 USD, se
   conecta directo a la Pi y elimina la capturadora HDMI y el SDK de Sony, que son dos
   dependencias sin probar. Frente a ~1 700 USD de la Sony + Tamron.
3. **Comprar lo que bloquea la impresión** (poleas GT2, rodamiento giratorio) esta semana.
4. **Leer las dos referencias obligatorias** de §11.
5. Fusionar el PR #1 para que `MEMORIA.md` deje de vivir en una rama aparte.

# Paso 7 · La rúbrica del lector y cómo dirigir el artículo

Análisis de `09_01 RUBRICA-CALIFICACIÓN LECTOR-.xlsx` (Unidad de Integración Curricular,
carrera de Software, hoja `UIC-2025-02`) aplicada al estado real del artículo.
Fecha: 06/11/2026.

---

## 1. Cómo se calcula la nota (está en la hoja, no es interpretación)

El lector marca **Sí**, **No** o **P/Parcialmente** en **35 ítems**. Las fórmulas de la hoja son:

| Columna | Fórmula | Valor por ítem |
|---|---|---|
| Sí | `COUNTIF(B15:B57,"*")*2` | **2 puntos** |
| No | `COUNTIF(C15:C57,"*")*0` | **0 puntos** |
| P/Parcialmente | `COUNTIF(D15:D57,"*")` | **1 punto** |

**Nota = (Sí·2 + P) / 2 − 5**, con un máximo de **30 puntos** (35 ítems × 2 = 70; 70/2 − 5 = 30).

Tres consecuencias prácticas:

1. **Cada ítem que pasa de "No" a "Sí" vale 1 punto de la nota final.** De "No" a "Parcialmente", medio punto.
2. El **−5** es un castigo fijo: con 10 puntos crudos la nota es 0. No hay margen para dejar secciones vacías.
3. **No hay ítems de forma** (no se evalúa tipografía, márgenes ni formato de la revista). La rúbrica solo
   mide **contenido científico**. El formato Esprint sigue siendo obligatorio para la revista, pero no da nota aquí.

---

## 2. Dónde está el peso de la nota

| Sección de la rúbrica | Ítems | Puntos | % de los 30 |
|---|---|---|---|
| Tema | 1–4 | 4 | 13 % |
| Introducción | 5–8 | 4 | 13 % |
| Objetivos | 9–11 | 3 | 10 % |
| **Metodología** | 12–17 | **6** | **20 %** |
| **Resultados** | 18–23 | **6** | **20 %** |
| **Discusión** | 24–27 | **4** | **13 %** |
| Conclusiones | 28–31 | 4 | 13 % |
| Resumen | 32 | 1 | 3 % |
| Bibliografía | 33–35 | 3 | 10 % |

**20 de los 35 ítems (Metodología, Resultados, Discusión y Conclusiones) solo se pueden
responder "Sí" si hay datos medidos de verdad.** Eso es el **57 % de la nota**. Es el dato
más importante de todo este documento: la nota no depende de cuántos modelos de IA se
prometan, sino de cuántas noches de datos se alcancen a analizar bien.

---

## 3. Dónde estarías hoy

Estimación si el artículo se entregara hoy, con el `articulo_v2.docx` tal como está (con los
`[[ ]]` sin rellenar) y la bibliografía de 24 referencias ya verificada:

| Sección | Sí | P | No | Por qué |
|---|---|---|---|---|
| Tema (1–4) | 4 | — | — | El tema es de la carrera, original y discutible |
| Introducción (5–8) | 3 | 1 (ítem 6) | — | Hay literatura y brecha; la redacción por párrafos cortos está sin revisar |
| Objetivos (9–11) | 3 | — | — | Están planteados y ligados al problema |
| Metodología (12–17) | 3 | — | **3** (14, 16, 17) | El método está escrito, pero no hay datos recolectados ni análisis hechos |
| Resultados (18–23) | — | — | **6** | No existen |
| Discusión (24–27) | — | — | **4** | No existe |
| Conclusiones (28–31) | — | — | **4** | No existen |
| Resumen (32) | — | — | **1** | Tiene `[[ ]]` en lugar de resultados |
| Bibliografía (33–35) | 3 | — | — | 24 referencias con DOI, actuales y del tema |
| **Total** | **16** | **1** | **18** | |

**Nota estimada: (16·2 + 1) / 2 − 5 = 11,5 / 30.**

Es una estimación, no una predicción: el lector puede ser más duro en Introducción. Pero el
orden de magnitud es el correcto, y señala con precisión dónde están los 18,5 puntos que faltan:
**todos en recolectar datos, analizarlos y escribir Resultados, Discusión y Conclusiones.**

---

## 4. El problema de fondo: el alcance actual no cabe

El diseño de investigación vigente (ver `MEMORIA.md` y el documento de diseño) promete:

- **3 módulos de IA** en cadena (M1 detección, M2 trayectoria, M3 corrección),
- **3 modelos comparados en cada módulo** → 9 modelos,
- **3 formas de entrenar** (A supervisado, B simulación + ajuste fino, C aprendizaje por refuerzo),
- 8–10 noches reales, dataset en Zenodo con DOI, Friedman + Nemenyi por módulo, 6 experimentos.

Y el estado real del proyecto es:

| Qué | Estado |
|---|---|
| Montura impresa en 3D | Diseñada, **sin imprimir** |
| Electrónica armada | Esquema listo, **sin armar**; prueba de banco sin correr |
| Cámara y capturadora HDMI | **Sin comprar** (~1 700 USD, precios sin verificar) |
| Código de captura, dataset, M1, M2, M3 | **Sin escribir** (el repo solo tiene el `correccion.py` del enfoque antiguo) |
| Noches de observación | **0** |

Contra la rúbrica, un alcance así es un riesgo, no una ventaja:

- El ítem 2 (*¿es intelectualmente exigente y original?*) ya se gana con **una** comparación bien hecha.
  Nadie da puntos extra por nueve.
- Los ítems **20 (*resultados de alta calidad*), 22 y 23 (*libre de errores menores y mayores*)
  y 26 (*discusión detallada, sin ser breve o superficial*)** castigan exactamente lo que produce
  un alcance inflado: nueve comparaciones a medias, cada una con poco espacio y poco análisis.
- El ítem 17 (*¿se ha aprovechado todo el potencial de los datos?*) premia **profundidad**, no variedad.
- El artículo tiene un límite de **10 a 20 páginas**. Nueve modelos × 3 formas de entrenar no entran
  con una discusión seria de cada uno.

**La rúbrica recompensa un trabajo angosto y profundo, y castiga uno ancho y superficial.**

---

## 5. Recorte recomendado

> ⚠️ **Superado.** Nashla aprobó el recorte el 06/11/2026, y el enfoque final es más estrecho y
> más defendible que esta propuesta: las búsquedas en Scopus de ese mismo día confirmaron que la
> brecha está en el cruce **simulación-a-realidad × apuntado**. El diseño vigente está en
> [`08-diseno-definitivo.md`](08-diseno-definitivo.md). Lo que sigue se conserva como registro
> del razonamiento. Las secciones 1, 2, 3, 6 y 7 de este documento siguen vigentes.

Propuesta: un solo aporte central, medido a fondo, y lo demás como infraestructura o como
análisis secundario breve.

| Parte | Qué hacer | Por qué |
|---|---|---|
| **Aporte central: M3** (corregir el error de apuntado y seguimiento con IA) | Mantener. 3 modelos: **Ridge** (línea base), **LightGBM**, **MLP**. Friedman + Nemenyi | Ya está implementado en `correccion.py`, los datos los genera la propia montura, y se compara de frente con Zariski et al. (2024) y Chichura et al. (2025) → alimenta directo el ítem 24 |
| **Segundo eje: cómo se entrena** | Mantener solo **A (supervisado real)** frente a **B (simulación + ajuste fino)**, reportando cuántas noches reales necesita cada una | Es el aporte más original y el más barato: "con simulación bastan 3 noches en lugar de 10" es un resultado útil para cualquiera que replique el equipo. Da el ítem 2 por sí solo |
| **M1 detección** | Reducir a **instrumento de medida**, no a contribución: Hough clásico frente a **un** detector aprendido, en una sola tabla | Hace falta para medir el error de forma objetiva. Comparar dos métodos es suficiente para justificar cuál se usó |
| **M2 trayectoria** | **Quitar** (o una sola tabla de media página) | Skyfield ya predice la Luna con precisión. Predecirla con un LSTM es resolver un problema resuelto, y un lector exigente lo va a señalar en los ítems 13 y 25 |
| **C: aprendizaje por refuerzo (PPO)** | **Quitar** | Es un proyecto de investigación en sí mismo. Si no converge, no hay resultado; si converge a medias, cuesta puntos en los ítems 20, 22 y 23 |

Resultado: **3 modelos × 2 formas de entrenar + 1 comparación de detectores.** Cabe en 20 páginas,
se discute a fondo y deja escribir Resultados, Discusión y Conclusiones con datos de verdad.

Lo que se quita no se tira: se menciona en "trabajo futuro", que es justamente lo que pide el
ítem 29 (*conclusiones como aporte propio*).

### Riesgo de hardware que conviene revisar

La cámara elegida (Sony ZV-E10 II + Tamron 17-70, ~1 700 USD) sirve, pero **la rúbrica no da
puntos por la cámara**. Para medir el centro de la Luna, una **Raspberry Pi HQ Camera con un
lente de ~28 mm** da el mismo tamaño de Luna en píxeles (≈ 160 px) por unos 50–80 USD, se
conecta directo a la Pi y **elimina la capturadora HDMI y el SDK de Sony**, que hoy son dos
dependencias sin probar. Vale la pena decidirlo antes de comprar: es el único punto donde se
puede ahorrar más de 1 500 USD y dos riesgos técnicos sin perder un solo punto de la nota.

---

## 6. Qué tiene que decir cada sección para que el ítem salga "Sí"

### Tema (ítems 1–4) · 4 pts — ya alcanzables

- **3. Título claro y concreto.** El título vigente ("Sistema inteligente de posicionamiento y
  seguimiento de objetos celestes mediante aprendizaje automático e interfaz de control web")
  anuncia más de lo que el artículo va a demostrar. Un lector que lea "objetos celestes" y
  encuentre solo la Luna marca **P**. Conviene un título que diga lo que se midió, por ejemplo:
  *"Corrección del error de seguimiento lunar con aprendizaje automático en una montura de bajo
  costo: comparación de tres modelos y dos estrategias de entrenamiento"*.
- **4. Motiva discusión científica.** Se gana nombrando explícitamente la tensión: ¿vale la pena
  una montura de bajo costo con IA frente a una montura comercial? Debe estar en la Introducción.

### Introducción (ítems 5–8) · 4 pts

- **6.** Es el único ítem de redacción: **párrafos con estructura y cláusulas cortas, con punto
  seguido en lugar de comas.** Barato de ganar y hoy está sin revisar. Se hace al final, leyendo
  en voz alta.
- **7.** **Cada párrafo de la Introducción necesita al menos una cita.** Las 24 referencias ya
  verificadas alcanzan; falta colocarlas.
- **8.** La brecha tiene que estar afirmada **con literatura**, no por sentido común: los trabajos
  que corrigen apuntado con IA lo hacen en telescopios profesionales (WIYN, South Pole Telescope);
  no hay evidencia en monturas de bajo costo, ni sobre cuántas noches de datos hacen falta.

### Objetivos (ítems 9–11) · 3 pts

- Los objetivos específicos deben quedar **en correspondencia uno a uno con los experimentos**.
  Si se recorta el alcance, hay que recortar también los objetivos: un objetivo sin resultado es
  un "No" en el ítem 28 (*conclusiones relacionadas con los objetivos*).

### Metodología (ítems 12–17) · 6 pts — aquí se pierden 3 hoy

- **13. Justificar la elección de métodos con citas.** Por qué Ridge como línea base, por qué
  LightGBM, por qué Friedman y Nemenyi en lugar de t de Student. Cada decisión, una cita.
- **14. "La recolección de datos supera ampliamente los niveles mínimos."** Es el ítem que
  justifica todo el cambio a cámara: **8–10 noches × ~20 000 filas** supera con holgura cualquier
  mínimo, y se dice con el número en la tabla. Aquí el enfoque nuevo gana puntos que los
  30 apuntados manuales del enfoque viejo no daban.
- **16. Análisis suficientes y apropiados.** Friedman + Nemenyi, IC 95 % por bootstrap agrupado
  por noche, tamaño del efecto. Ya está decidido; falta ejecutarlo.
- **17. "Aprovechar todo el potencial de los datos."** Con ~20 000 filas por noche se puede
  analizar el error **por zona del cielo, por fase lunar y por temperatura**. Ese desglose es
  justamente lo que convierte este ítem en "Sí", y es gratis: son los mismos datos vistos de
  otra forma.

### Resultados (ítems 18–23) · 6 pts — hoy los 6 son "No"

- **19 y 20. Detallados, precisos, de alta calidad.** Media, DE, RMS, n, IC 95 % y valor de p en
  **cada** tabla. Nunca un número sin su incertidumbre.
- **21. Interpretación con perspicacia.** Ojo: el ítem está en Resultados, pero la guía de la
  revista exige que Resultados **no** interprete. Se resuelve con un cierre sobrio por tabla
  ("el error residual deja de depender del azimut") y la interpretación a fondo en Discusión.
- **22 y 23. Libre de errores menores y mayores.** Esto es lo que se pierde al abarcar demasiado.
- Regla que ya está en el repo y que protege estos seis ítems: **ningún número sin medición real.**

### Discusión (ítems 24–27) · 4 pts

- **24. Comparar los hallazgos con la literatura.** Hay que poder escribir: "la reducción de
  error obtenida (X′ → Y′) es comparable a / menor que la que reportan Zariski et al. (2024) en
  el WIYN". **Esto exige que las métricas sean las mismas que usan esos artículos**; conviene
  fijarlas antes de medir, no después.
- **25. Crítica propia de los métodos.** Reconocer las limitaciones: una sola montura, un solo
  objeto (la Luna), un solo sitio (Portoviejo, ~1° S), separación por noche y no por sitio.
  Admitir limitaciones **sube** la nota aquí.
- **26. Detallada, no superficial.** Un alcance recortado es lo que permite cumplirlo.

### Conclusiones (ítems 28–31) · 4 pts

- **29. Aporte propio, no repetición de resultados.** La conclusión no puede ser "la IA redujo el
  error de X a Y". Tiene que ser una afirmación transferible: *"en una montura de bajo costo el
  error de apuntado es sistemático y predecible, y basta con N noches de datos —o M si se
  pre-entrena en simulación— para corregirlo por debajo del campo visual del instrumento."*
- **31. Resaltar el hallazgo principal.** Un mensaje, uno solo, repetido en resumen, conclusiones
  y presentación.

### Resumen (ítem 32) · 1 pt

- Las cinco partes (introducción, objetivos, metodología, resultados principales, conclusiones)
  **con números y con p**, en un párrafo, ≤ 250 palabras. La revista pide lo mismo, así que un
  solo trabajo cubre las dos exigencias. Se escribe al final.

### Bibliografía (ítems 33–35) · 3 pts — ya alcanzables

- Las 24 referencias con DOI verificado cubren suficiencia, pertinencia y actualidad. **Solo hay
  que citarlas todas en el texto**; una referencia que no se cita es una señal de alarma para
  cualquier lector.

---

## 7. Cómo queda el orden de trabajo

El orden de la rúbrica no es el orden de trabajo. Por valor por hora invertida:

| Prioridad | Qué | Puntos en juego | Depende de |
|---|---|---|---|
| **1** | Decidir el recorte de alcance y ajustar objetivos y título | Habilita 20 ítems | Tu decisión |
| **2** | Armar electrónica, imprimir montura, correr la prueba de banco | Bloquea todo lo demás | Compras |
| **3** | Código de captura, dataset y entrenamiento | — | 2 |
| **4** | Noches de observación (8–10) | Ítems 14, 18–23 | 3 |
| **5** | Análisis estadístico y figuras | Ítems 16, 17, 19–21 | 4 |
| **6** | Escribir Resultados, Discusión y Conclusiones | 14 ítems, 14 pts | 5 |
| **7** | Repasar Introducción: una cita por párrafo y frases cortas | Ítems 6, 7 | — (se puede hacer ya) |
| **8** | Resumen y abstract | Ítem 32 | 6 |

Los pasos **1 y 7 se pueden hacer esta semana** y no dependen de ninguna compra.

---

## 8. Pendiente de confirmar

1. **Fecha de sustentación.** Es el dato que decide cuánto se puede recortar. La hoja trae
   `26/02/2026` y el nombre de la hoja es `UIC-2025-02`, que parecen del período anterior.
2. **La rúbrica de la sustentación oral.** Esta hoja evalúa solo el **manuscrito escrito**
   (máximo 30 puntos) y la firma el **lector**. Si la presentación se califica aparte, hace falta
   ese formato para preparar la defensa; el nombre del archivo (`09_01`) sugiere que es parte de
   un juego de formatos.
3. **Si hay además una rúbrica del tutor**, y cómo se combinan las notas.
4. **Financiamiento.** La factura de los componentes está a nombre de AFIFSYSTEMS S.A.S. Hay que
   declararlo en *Fuente de financiamiento* y revisar si constituye conflicto de interés. No es un
   ítem de la rúbrica, pero sí un problema de integridad que un lector puede levantar.

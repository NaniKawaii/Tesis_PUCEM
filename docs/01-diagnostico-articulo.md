# Paso 1 · Diagnóstico del artículo y del prototipo

Revisión del borrador `artículo.docx` (Drive) frente a la guía de autores de la revista
**Esprint Investigación** (NR003), al plan de titulación y a la proforma de materiales.
Fecha de revisión: 15/10/2026.

---

## 1. Lo más importante (léelo primero)

1. **La sección de Resultados describe pruebas que todavía no existen.** El borrador reporta
   noches de observación, errores de 10–15′, seguimiento de Júpiter durante unos 5 minutos,
   latencia menor a 0,5 s, un tubo de unos 4 kg, transmisión por correa y una webcam con
   astrometría. El prototipo aún no está construido, así que esos datos no pueden publicarse
   tal como están. Un revisor (o el tribunal) puede pedir los datos crudos. **Todos los números
   del artículo deben salir de mediciones reales.** El software de este repositorio está
   hecho para generar esos datos (ver §7).
2. **Falta un aporte medible de la IA.** El propio borrador admite que la IA es
   "incipiente" y está formada por "algoritmos de optimización sencillos", pero el título y
   el objetivo 3 prometen *machine learning* y redes neuronales. Propuesta concreta en §6.
3. **La revista exige resultados con valor de p** en el resumen. El borrador no tiene
   ninguna prueba estadística. El diseño experimental de §7 resuelve esto.
4. **Hay dos referencias que no se pudieron verificar** (Coughlin et al., 2020 y Ramírez y
   Torres, 2021). Además, están en el plan de tesis y en la presentación. Ver §4.
5. **La proforma tiene un problema eléctrico:** el TB6600 necesita entre 9 y 42 V y la
   batería es de 7,4 V. Ver §5.

---

## 2. Cumplimiento de la guía Esprint

| Requisito de la revista | Estado del borrador | Acción |
|---|---|---|
| Título ≤ 18 palabras, sin abreviaturas | ✅ 18 palabras | Mantener o acortar un poco |
| Título en inglés | ✅ | — |
| Autor, filiación, **ORCID**, correspondencia | ❌ Falta el ORCID | Crear ORCID (gratis, orcid.org) y añadir al tutor como coautor si corresponde |
| "Tipo de contribución: Artículo de Investigación" | ❌ Falta | Añadir |
| Resumen ≤ 250 palabras, un párrafo | ❌ **265 palabras** | Reescribir |
| Resumen con 5 partes y **resultados con valores y p** | ❌ No tiene números ni p | Reescribir después de las pruebas |
| No citar figuras ni referencias en el resumen | ⚠️ Menciona librerías y "TB6600, etc." | Quitar detalles de componentes |
| 4–5 palabras clave **en orden alfabético** | ❌ No están ordenadas | p. ej. *astroturismo, control web, inteligencia artificial, posicionamiento telescópico, sistemas embebidos* |
| Abstract y Keywords en inglés | ❌ El "Abstract" está vacío | Traducir al final |
| **Tercera persona** | ❌ Usa "nuestro", "hemos", "presentamos" y "observamos" en casi todas las secciones | Cambiar a "se presenta", "se observó"… |
| Introducción con contexto, estado del arte reciente, brecha, justificación y objetivos | ⚠️ El contenido es bueno, pero faltan citas en el texto y la brecha no se basa en literatura | Añadir citas APA en cada afirmación y declarar la pregunta o hipótesis |
| Metodología con **figura global** del proceso | ❌ No tiene | Hacer un diagrama del flujo: diseño → construcción → pruebas → análisis |
| Metodología: enfoque, diseño, población y muestra, análisis estadístico | ❌ Solo describe la ingeniería | Traer del plan: enfoque cuantitativo, 20 participantes, estadística |
| Figuras 1 y 2 (modelo 3D, circuito) | ❌ Están anunciadas pero no existen | Exportar el CAD y dibujar el esquema (Fritzing o KiCad) |
| Resultados en pasado, sin interpretar, con tablas y figuras | ⚠️ Mezcla interpretación ("cumple con su objetivo") | Separar resultados y discusión |
| Discusión en pasado, sin adjetivos de elogio | ⚠️ "cumple cabalmente", "sinergia exitosa" | Usar un tono neutro |
| Tablas solo con bordes superior e inferior; figuras de 300 dpi; "Nota:" al pie | — | Aplicar al maquetar |
| CRediT con roles taxonómicos | ⚠️ Es un párrafo libre | Listar los roles (Conceptualización, Software, etc.) |
| Referencias APA 7, **alfabéticas**, de los **últimos 5 años**, con DOI | ❌ Sin orden, 2 no verificables, varias sin DOI, una web divulgativa | Ver §4 |
| Extensión de 10 a 20 páginas, Times 12, interlineado 1,5 | — | Verificar al final |

---

## 3. Inconsistencias internas

| Tema | Plan de tesis | Artículo | Proforma |
|---|---|---|---|
| Controlador | ESP32 / ESP8266 | Raspberry Pi ("microcontrolador") | Raspberry Pi 4 (2 GB) |
| Drivers | A4988 / TMC2209 | TB6600 | TB6600 |
| Motores | "paso a paso" | "paso a paso" | NEMA 23 con acople directo (sin reducción) |
| Transmisión | — | Correa dentada | Acoples directos |
| Fines de carrera | — | Sí (con pruebas) | ❌ No están comprados |
| Encoder | — | No se menciona | AS5600 (solo 1 unidad) |
| IMU | — | Acelerómetro y giroscopio | GY-91 (MPU9250 + BMP280) |
| Pantalla | — | No se menciona | TFT HDMI de 5″ |
| IA | Redes neuronales para reconocer y predecir trayectorias | "Ajustes según la intensidad de la imagen" | — |

**Recomendación:** se debe usar lo que de verdad se construya (Raspberry Pi + TB6600 es una
buena elección) y explicar en la Metodología por qué cambió respecto al plan. Por ejemplo:
"se sustituyó el ESP32 por una Raspberry Pi 4 porque ejecuta en el mismo dispositivo el
cálculo de efemérides, el servidor web y el modelo de IA". Una Raspberry Pi **no es un
microcontrolador**: es un computador de placa única (SBC). Hay que corregir ese término.

Otras afirmaciones del borrador que hoy no tienen respaldo y deben eliminarse o
demostrarse: "precisión de reloj atómico" del GPS, "diodos TVS y capacitores", "conexión vía
internet desde otra ubicación", "personas sin experiencia interactuaron" (eso requiere el
estudio de usabilidad) y "tubo de ~4 kg".

---

## 4. Verificación de referencias

| Referencia | Resultado | Acción |
|---|---|---|
| Astropy Collaboration (2013), *A&A* 558, A33 | ✅ Existe | Es una cita clásica, se acepta. Si se usa Skyfield en lugar de Astropy, citar Skyfield (Rhodes, ASCL 1907.024) |
| Ricci et al. (2025) *Proc. SPIE* 13098, 130980T | ✅ Existe ([arXiv:2501.07997](https://arxiv.org/abs/2501.07997)) | El año del volumen SPIE es **2024**. Añadir DOI 10.1117/12.3018331 |
| Fonseca-Campos et al. (2023) *IEEE Access* 11 | ✅ Existe, pero **las páginas están mal** | Las correctas son 143782–143803, DOI 10.1109/ACCESS.2023.3343638 |
| "Carlsten, S.G.; Durbak, M.; Angeli, G.Z." (2024) arXiv:2407.08046 | ⚠️ **El artículo existe pero los autores están mal** | El primer autor es **Zariski, J.** et al. (2024), *Proc. SPIE* 13101, 131010Q. Es una referencia clave para la IA (§6) |
| Dutton (2016) OnStep | ⚠️ Es un repositorio, no un artículo | Se puede citar como software y añadir la URL |
| Landers (2022) TelescopicWatch | ⚠️ Es un blog | Reemplazar por una fuente académica |
| Alnitak Observatory (2023) ARTA | ⚠️ Es una página web | Se acepta como fuente secundaria o se reemplaza |
| **Coughlin et al. (2020)** "Planetary detection using machine learning methods", *A&A* 635, A95 | ❌ **No se encontró**. El DOI no corresponde a ese título | **No usar.** Está también en el plan y en la presentación |
| **Ramírez y Torres (2021)**, RELATEC 20(3) | ❌ **No se encontró** | **No usar** |
| "Lang et al. (2019)" (Proceso de Tesis) | ⚠️ La referencia real es **Lang et al. (2010)**, Astrometry.net, *AJ* 139, 1782 | Ese artículo trata de astrometría de imágenes, **no** de la usabilidad de los GoTo. Citarlo solo para el *plate solving* |
| Ministerio de Turismo (2022), Plan Sectorial | ✅ Plausible | Verificar que diga lo que se cita sobre astroturismo |

> Estas dos referencias tienen el aspecto típico de las generadas por herramientas de IA:
> autores reales con un título y un DOI inventados. Antes de enviar el artículo, conviene
> abrir **cada** DOI y comprobar el título.

Además, el artículo **no tiene citas dentro del texto**: menciona a "Ricci et al." y
"Fonseca-Campos et al." sin año en algunos casos, y las demás referencias no se citan en
ningún sitio. Cada referencia debe citarse al menos una vez y cada cita debe aparecer en la
lista.

---

## 5. Observaciones sobre el hardware de la proforma

| # | Problema | Por qué importa | Sugerencia |
|---|---|---|---|
| 1 | **La batería LiPo 2S (7,4 V) no puede alimentar los TB6600**, que necesitan entre 9 y 42 V | Los motores no se moverán, o lo harán con muy poco torque | Usar una fuente de 12 o 24 V (≥ 5 A) o una batería 3S/4S, más un convertidor *buck* a 5 V 3 A para la Raspberry Pi |
| 2 | **Acople directo:** con 200 pasos × 16 micropasos, cada micropaso equivale a **6,75′** | El ajuste más fino posible es grande para un planeta (Júpiter mide ~0,6′), y el micropaso bajo carga es impreciso | Añadir una reducción, por ejemplo con poleas GT2 de 20T → 100T (5:1), un engranaje impreso o un tornillo sinfín. El software ya admite la `reduccion` en la configuración |
| 3 | Los NEMA 23 pesan ~1 kg cada uno y tienen mucho torque | Una estructura de PLA puede flexionarse | Valorar NEMA 17 con reducción, que es más liviano y suficiente para un tubo pequeño |
| 4 | **Faltan los fines de carrera** que el artículo dice haber probado | Seguridad mecánica | Comprar 2 microswitches (~1 USD). Los pines ya están previstos en el software |
| 5 | Solo hay 1 encoder AS5600, y su dirección I²C es fija (0x36) | No se pueden poner 2 en el mismo bus | Usarlo en un solo eje para verificar pasos perdidos, o añadir un multiplexor TCA9548A |
| 6 | El magnetómetro del MPU9250 queda junto a los motores | Las lecturas de rumbo serán inútiles | Usar el acelerómetro solo para comprobar la nivelación |
| 7 | Las entradas del TB6600 son de 5 V y los GPIO de la Raspberry Pi son de 3,3 V | Normalmente funciona con el cableado de ánodo común, pero conviene comprobarlo | Si falla, usar un convertidor de nivel |

---

## 6. Propuesta para el componente de IA (concreto y medible)

**Corrección del error de apuntado mediante aprendizaje automático.** Esta propuesta sigue
la misma idea que Zariski et al. (2024), que usaron redes neuronales para el apuntado del
telescopio WIYN, pero a escala de bajo costo.

- Una montura casera tiene errores **sistemáticos**: desnivel del trípode, desfase de la
  referencia inicial, flexión del PLA y holgura de los ejes. Todos dependen de la dirección
  hacia la que se apunta.
- En cada prueba se hace un GoTo, el usuario centra el planeta con las flechas y el sistema
  **registra cuánto hubo que corregir**. Ese registro es el error medido.
- Con esos registros se entrenan dos modelos: un **modelo lineal clásico**, que sirve de
  línea base, y una **red neuronal (MLP)**. Se comparan con validación cruzada.
- **Resultado publicable:** "La corrección con red neuronal redujo el error RMS de apuntado
  de X′ a Y′ (n = N; Wilcoxon, p = …)". Esto responde directamente a la H2 y a la H3 del plan.

Esto ya está implementado en `prototipo/telescopio/correccion.py` y se maneja desde la
interfaz web, en el panel "3 · Inteligencia artificial".

Como ampliación opcional, si el tiempo alcanza: con una cámara se puede entrenar una red
convolucional (CNN) que detecte el planeta en la imagen y lo centre automáticamente. Así se
cumpliría literalmente el objetivo de "reconocimiento de cuerpos celestes".

---

## 7. Diseño experimental propuesto (para que el artículo tenga datos reales)

| Experimento | Variable medida | Cómo se mide | Muestra | Estadística (con p) |
|---|---|---|---|---|
| E1. Precisión del GoTo sin IA | Error de apuntado (′) | El software lo registra al confirmar el centrado | ≥ 30 apuntados a planetas o estrellas brillantes, repartidos por todo el cielo | Media, DE, RMS, mediana, IC 95 % |
| E2. Efecto de la corrección con IA | Error residual (′) | Validación cruzada sobre los datos de E1, y luego GoTo reales con el modelo activo | Los mismos ≥ 30 | Wilcoxon pareado sin IA vs. con IA (p < 0,05) |
| E3. Tiempo hasta localizar el planeta | Segundos | Cronómetro: búsqueda manual vs. interfaz web | 20 participantes (según el plan) | Wilcoxon pareado o t pareada |
| E4. Usabilidad de la interfaz | Puntaje **SUS** (0–100) | Cuestionario System Usability Scale de 10 ítems | 20 participantes | Media e IC; prueba t contra el valor de referencia 68 |
| E5. Latencia web | ms | Registro del servidor | ≥ 50 comandos | Media y percentiles |

Así cada objetivo específico tiene un resultado con número, y el resumen puede cumplir la
exigencia de la revista de incluir "valores y significancia estadística".

---

## 8. Hoja de ruta

Ver el [README](../README.md#hoja-de-ruta) del repositorio.

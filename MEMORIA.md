# Memoria del artículo · decisiones vigentes

Este archivo junta **todo lo que Nashla ha decidido y pedido** sobre el artículo (enfoque,
hardware, IA, bibliografía). Lo vigente va arriba; el historial, con fechas absolutas, va al
final. Cada conversación que cambie algo relevante actualiza este archivo.

> Regla del repositorio: los resultados del artículo salen **solo de mediciones reales**.
> Nada de valores estimados, ni siquiera provisionales.

> ⚠️ Este archivo nació en la rama `claude/project-thread-zcrk5b` (PR #1, sin fusionar) y se
> trae aquí actualizado. **Fusionar ese PR o cerrarlo** para que no queden dos versiones.

## Versión vigente (2026-11-06, tarde)

**Qué es:** un artículo científico para la revista *Esprint Investigación*. Es la modalidad del
**proyecto final de titulación** de Nashla; cuando ella dice "tesis" se refiere a esto, no a un
documento por capítulos.
Autora: Nashla Carolina Tuma Zambrano, Ingeniería de Software, PUCE Sede Manabí.
Tutor: Ing. Diego Paul Corrales Vargas, Mg.

**Plazo: 15 semanas** desde el 2026-11-06 → termina alrededor del **19/02/2027**.

**Se califica con la rúbrica del lector** (`09_01 RUBRICA-CALIFICACIÓN LECTOR-.xlsx`): 35 ítems,
Sí = 2 · Parcialmente = 1 · No = 0, nota = (Sí·2 + P)/2 − 5, **máximo 30 puntos**. No hay ítems
de formato. **20 de los 35 ítems (57 % de la nota) exigen datos medidos reales.** Análisis
completo en [`docs/07-rubrica-lector.md`](docs/07-rubrica-lector.md).

**Aporte vigente** (decidido el 2026-11-06, sustituye el alcance anterior):

> Pre-entrenar en simulación con **aleatorización de dominio** reduce la cantidad de **noches
> reales** que hace falta para que un modelo de aprendizaje automático corrija el error de
> apuntado de una montura altacimutal de bajo costo.

**Diseño definitivo completo: [`docs/08-diseno-definitivo.md`](docs/08-diseno-definitivo.md).**
Ese documento es la fuente de verdad del enfoque; lo que sigue es el resumen.

- **La IA aprende el residuo, no la posición.** Skyfield da la posición, un modelo de apuntado
  clásico quita los términos trigonométricos conocidos, y la IA predice lo que queda.
- **El error se parte en dos** (incorporado el 2026-11-06 a raíz de una pregunta de Nashla):
  los términos **de sesión** (desfases de índice, desnivel del trípode, cero de azimut) cambian
  en cada montaje y **se calibran** con una alineación rápida de 2–3 puntos más la lectura del
  GY-91; los términos **persistentes** (flexión, holgura, no perpendicularidad, deriva térmica)
  son los que **aprende la IA** y los únicos comparables entre noches. Sin esta separación, la
  validación dejando una noche fuera no sería válida.
- **La simulación no aprende el cielo**, que Skyfield ya resuelve: aprende **qué forma tienen
  las funciones de error de apuntado** en general, para que con la montura real solo haya que
  averiguar cuál miembro de la familia es. Una noche es un arco, no la bóveda: el cuello de
  botella es la **cobertura del cielo**, no el número de filas.
- **Cuatro modelos, en orden:** modelo clásico → Ridge → LightGBM → MLP. **Nada de LSTM** (es
  regresión, no secuencia).
- **Dos formas de entrenar, no tres:** solo datos reales, frente a simulación + ajuste fino.
- **Validación dejando una noche fuera.** Nunca partición aleatoria de filas.
- **Detección (cámara):** Hough frente a un detector aprendido, como **instrumento de medida**,
  no como contribución. Etiquetado automático con Skyfield + ajuste de círculo.
- **Mínimo 6 noches, objetivo 8.** Con 5 noches la prueba de Wilcoxon pareada no puede bajar de
  p = 0,0625 a dos colas, así que es **matemáticamente incapaz** de dar significancia.
- **Título propuesto** (17 palabras, dentro del límite de 18 de la revista): **"Preentrenamiento
  en simulación para corregir el apuntado de monturas de bajo costo con menos noches de
  observación"**. En inglés: *"Simulation pre-training to correct the pointing of low-cost mounts
  with fewer observation nights"*. Alternativas y el porqué de cada bloque, en `docs/08` §8.
  (Una propuesta anterior de 19 palabras se pasaba del límite y quedó descartada.)

**La brecha está confirmada en Scopus** (búsquedas del 2026-11-06 con la cuenta de la PUCE):
el campo núcleo "telescopio + error de apuntado + ML" tiene **12 documentos en toda Scopus**,
ninguno en monturas de bajo costo; el cruce "sim-to-real + apuntado" devuelve **3 documentos,
ninguno pertinente**. Números y cadenas en `docs/08`, §1.

### Descartado (va a trabajo futuro)

| Se quita | Razón |
|---|---|
| M2: predicción de trayectoria (Kalman / LightGBM / LSTM) | Skyfield ya predice la Luna; es un problema resuelto |
| Aprendizaje por refuerzo (PPO, Gymnasium) | No cabe en 15 semanas; Nousiainen et al. (2022) ya ocupó el nicho |
| Cruzar modelos × formas de entrenar (9 condiciones) | Destruye la potencia estadística: la diferencia crítica de Nemenyi sube a ≈ 4,3 sobre un rango de 1 a 9 |
| Estudio de usabilidad con 20 participantes y SUS | La rúbrica no tiene ningún ítem de usabilidad |
| Tercera forma de entrenar | Quedan dos |

### Pendientes abiertos

1. **Confirmar el recorte con el tutor.** Quitar el estudio de usabilidad cambia un objetivo del
   plan aprobado, y el cambio de título puede necesitar trámite. **Es lo primero.**
2. **Decidir la cámara.** Raspberry Pi HQ Camera + lente de ~28 mm (≈ 160 px de Luna, 50–80 USD,
   directo a la Pi, sin capturadora HDMI ni SDK de Sony) frente a Sony ZV-E10 II + Tamron 17-70
   (~1 700 USD, precios sin verificar, dos dependencias sin probar). La rúbrica no da puntos por
   la cámara.
3. Comprar lo que **bloquea la impresión 3D**: poleas GT2 20T y rodamiento giratorio de 4″.
4. Leer **He et al. (2026, FinalKAN)** y **Bergerhoff (2024, EUSIPCO)** antes de redactar.
5. Agregar al software: simulador de montura con aleatorización de dominio, captura de cámara,
   registrador del dataset y el corrector de residuo. **Empezar por el simulador**: no depende
   de hardware.
6. Incorporar las 7 referencias nuevas de `docs/08`, §11, y completar en Scopus las que están
   incompletas.
7. Fusionar o cerrar el PR #1.

> No escribir código nuevo sin el OK de Nashla.

## Hardware vigente

| Parte | Qué | Estado |
|---|---|---|
| Montura | Altacimutal impresa en PETG, reducciones 14:1 (az) y 5:1 (alt), barra Vixen | Diseñada ([`montura/`](montura/LEEME.md)), **sin imprimir** |
| Motores y drivers | 2 NEMA 23 + 2 TB6600 a 16 micropasos | **Comprados** |
| Control | Raspberry Pi 4 (2 GB) | **Comprada** |
| Sensores | GPS NEO-6M, GY-91, AS5600, fines de carrera | Comprados / en proforma |
| Energía | LiFePO4 12,8 V 12 Ah + step-down 5,1 V | Comprada / en proforma |
| Cámara | **Por decidir** (ver pendiente 2) | Sin comprar |

- **No comprar** NEMA 17 + TMC2209 + reducción 1:100: ya hay NEMA 23 + TB6600 y la montura está
  diseñada para ellos.
- Pico/Arduino para los pulsos: solo si la prueba de banco muestra tirones.
- La pantalla TFT de 5″, el BMS 2S y el indicador 2S no hacen falta.

## Cómo no depender del clima

La Luna se ve **de día** buena parte del mes (tardes cerca del primer cuarto, mañanas cerca del
último), y es brillante de sobra para detectarla contra el cielo azul. Las sesiones diurnas son
datos válidos de E1, E3 y E4, porque el error de la montura es el mismo apunte a donde apunte.
Incluirlas desde el principio, no como parche: en Portoviejo las noches despejadas son un riesgo
real entre enero y abril.

## Documentos de referencia

- Rúbrica del lector y mapeo ítem por ítem: [`docs/07-rubrica-lector.md`](docs/07-rubrica-lector.md)
- **Diseño definitivo: [`docs/08-diseno-definitivo.md`](docs/08-diseno-definitivo.md)**
- Diseño de investigación anterior (alcance de 3 módulos, **superado**): https://claude.ai/artifact/4XbEmnoXNMFJLUJhT8dVS1
- Bibliografía Scopus (24 referencias + cadenas de búsqueda): https://claude.ai/artifact/FEWEZ6H28HfpPHiWjPHY2t
- Carpeta de Drive de la tesis (Artículo v1, v2, v2.1): https://drive.google.com/drive/folders/1K1phWblEYKiIeQ4W515I4zOXwpfBdLNP

## Historial

- **2026-11-04:** Nashla cambia el título del Artículo v2.1 en Drive.
- **2026-11-06:** nuevo enfoque: cámara en la montura en vez de telescopio, app web, seguir la
  Luna desde Ecuador y comparar varios modelos de IA.
- **2026-11-06:** se propone que la IA corrija el error de la montura (Ridge / LightGBM /
  LSTM). Nashla confirma que la IA cumple los tres papeles: detectar, predecir y corregir.
- **2026-11-06:** pide comparar tres formas de entrenar (A supervisado, B simulación + ajuste
  fino, C refuerzo); se recomienda como eje del artículo.
- **2026-11-06:** se integra el equipo de otro chat: Sony ZV-E10 II + Tamron 17-70, capturadora
  HDMI, plate solving como referencia; se descarta cambiar los motores.
- **2026-11-06:** se entrega la bibliografía Scopus (24 referencias verificadas).
- **2026-11-06 (tarde):** Nashla reinicia el trabajo en un chat nuevo y aclara que "tesis"
  significa su proyecto de titulación por artículo científico.
- **2026-11-06 (tarde):** entrega la **rúbrica del lector**. Se descifra la fórmula (máximo 30
  puntos) y se establece que el 57 % de la nota exige datos reales.
- **2026-11-06 (tarde):** informa que el plazo es de **15 semanas** y pide un enfoque centrado
  en IA y en cómo entrenar modelos. Autoriza buscar en Scopus directamente.
- **2026-11-06 (tarde):** búsquedas en Scopus **confirman la brecha** (12 documentos en el campo
  núcleo, 0 en bajo costo, 0 en sim-to-real + apuntado) y aportan 7 referencias nuevas.
- **2026-11-06 (tarde):** Nashla aprueba el **enfoque definitivo**: aleatorización de dominio y
  pre-entrenamiento en simulación para reducir las noches reales necesarias. Se descartan M2, el
  refuerzo y el estudio de usabilidad.
- **2026-11-06 (tarde):** Nashla pregunta para qué sirve la simulación si el trípode funciona
  bien. La pregunta destapa un hueco del diseño: faltaba separar el error **de sesión** (se
  calibra en cada montaje) del **persistente** (lo aprende la IA). Se incorpora a `docs/08` §3 y
  §4, junto con el protocolo fijo de cada sesión y la analogía del robot bípedo para la defensa.
- **2026-11-06 (tarde):** se fija el **título** (17 palabras) y se documenta en `docs/08` §1 la
  comprobación de que el trabajo cumple los criterios de un artículo de investigación original,
  con la frontera explícita entre lo que ya es conocimiento establecido y lo que aporta.
- **2026-11-06 (tarde):** se reparte el trabajo en `docs/09-manos-a-la-obra.md` (tres frentes en
  paralelo; el de software no depende del hardware). Al revisar `prototipo/` aparecen tres
  desajustes que hay que corregir antes de generar datos: la reducción está en acople directo
  (1.0 en vez de 14:1 y 5:1), la validación cruzada parte las filas al azar en vez de dejar una
  noche fuera, y el esquema del registro es por apuntado en vez de por segundo. `docs/04` queda
  marcado como superado en su plan, aunque sigue vigente su parte técnica.
- **2026-11-06 (tarde):** primer código del enfoque nuevo: `errores.py` (modelo paramétrico
  compartido por el simulador y la alineación), `simulador.py` (aleatorización de dominio),
  `registro.py` con el esquema por segundo, y corrección de la reducción por defecto en
  `config.py`, que estaba en acople directo. 60 pruebas en verde. Al escribir las pruebas se
  midió que **sobre un arco corto los efectos no lineales son indistinguibles del modelo
  lineal** (razón 1,04 en 20 minutos frente a 3,13 en 4 horas): la cobertura del cielo, y no el
  número de filas, es lo que limita el aprendizaje. Queda en `docs/08` §4.
- **2026-11-06 (tarde):** se cierra el PR #1 sin fusionar. Solo aportaba la versión anterior de
  `MEMORIA.md` (alcance de 3 módulos x 3 modelos x 3 formas de entrenar, ya superado) y una
  línea del README que esta rama ya tiene. La rama `claude/project-thread-zcrk5b` queda en el
  remoto como registro histórico. Este archivo pasa a ser la única fuente de verdad.
- **2026-11-06 (tarde):** `aprendizaje.py` con los cuatro modelos (clásico, Ridge, boosting,
  MLP), alineación por sesión, validación dejando una noche fuera, curva de aprendizaje y
  Friedman + Nemenyi. Se usa `HistGradientBoostingRegressor` de scikit-learn en lugar de
  LightGBM: es el mismo algoritmo, ya es dependencia y evita compilar en la Raspberry Pi.
  **Resultado negativo medido:** la transferencia por residuo **empeora** el error en todos
  los casos, porque un modelo preentrenado sobre monturas diversas solo puede predecir la
  media de la familia (correlación −0,003 con el error real). **Reparación probada:**
  condicionar el modelo con 6 puntos de sondeo sube la correlación a +0,66 y baja el error de
  azimut de 3,70' a 2,86' sin ninguna noche real. **Pendiente de la decisión de Nashla**,
  porque cambia el método de `docs/08` §4.
- **2026-11-07:** Nashla autoriza rehacer la transferencia con condicionamiento por sondeo. Se
  implementa (`con_sondeo`, `sin_noches_reales`, `pointings_de_sondeo`, `analisis/e5_transferencia.py`)
  y **el resultado es negativo en las tres variantes**. Cambia el aporte del artículo.
  - La reparación del 06/11 **era una semilla afortunada**. Daba 2,92' con cero noches reales y
    p = 0,0078, el mínimo posible con 8 noches. Al repetir el mismo experimento con otras
    monturas sorteadas de la **misma** distribución, se sostuvo en 4 de 6 sorteos y se dio la
    vuelta en 2. También la correlación de +0,66 era inestable: entre semillas iba de 0,009 a
    0,737, en los dos sentidos.
  - Tercera variante, con los puntos de sondeo repartidos por todo el cielo (que es lo que se
    haría en campo): **peor**, por dos causas medidas. Los pointings a altitud alta corrompen
    la alineación de la sesión, porque el ajuste de 4 términos de sesión absorbe su error
    persistente, que es enorme por el factor `tan(h)` (punto ciego del cenit). Y reajustar los
    términos clásicos con 6 puntos está malísimamente condicionado: tiene rango completo, pero
    `sec(h)` y `tan(h)` son casi colineales y `lstsq` da coeficientes que explotan al
    extrapolar (RMS > 1 000'). **Tener rango no es estar bien condicionado.**
  - **Lo que sí se sostiene, 6 de 6 sorteos:** el corrector aprendido vence al modelo clásico,
    mediana 3,93' -> 3,50', 4 de 6 con p < 0,05. Ese es el resultado del artículo.
  - El sondeo queda implementado y **apagado por defecto**, con las mediciones en los
    docstrings, para poder reproducir el negativo en la Discusión.
  - Se retira de las pruebas el aserto estadístico del resultado negativo del 06/11: estaba
    colgado de una semilla (entre semillas el valor iba de 0,029 a 0,737, y la prueba exigía
    < 0,25). Lo sustituye una **identidad**, que no depende de la semilla: dos monturas
    distintas en las mismas posiciones producen las mismas entradas, así que ningún modelo sin
    sondeo puede distinguirlas. 101 pruebas en verde.
  - **Regla nueva del repositorio:** un valor de p sobre las noches de una montura no dice si
    el efecto se repetiría con otra montura. Todo experimento diseñado en simulación se repite
    con varios sorteos independientes y se publica en cuántos se sostiene. Queda en `docs/08`
    §6 y en `analisis/LEEME.md`.
- **2026-11-07 · PENDIENTE CON EL TUTOR:** el aporte (`docs/08` §1), la pregunta, H3, el
  objetivo general y el objetivo 4 (§2) y el título (§8) estaban construidos sobre el
  preentrenamiento y **ya no corresponden**. Quedan tachados, con propuesta de reemplazo al
  lado, y marcados para hablarlos con el Ing. Corrales. Título propuesto (16 palabras):
  "Corrección del apuntado de una montura altacimutal de bajo costo con aprendizaje automático
  sobre el residuo". H1, H2, H4 y los objetivos 1, 2, 3 y 5 se mantienen intactos.

# Paso 11 · Tu artículo en una página

Escrito el **16/11/2026**, porque había demasiadas cosas abiertas a la vez: el aporte quedó
tachado el 07/11, el título también, la cámara seguía sin decidirse y el 16/11 llegó la
propuesta del tutor. Este documento **cierra todo eso** y deja una sola respuesta por
pregunta.

Si solo vas a leer una cosa del repositorio, que sea esta.

---

## 1. Tu artículo, en una frase

> **Un corrector aprendido sobre el residuo del modelo clásico reduce el error de apuntado de
> una montura altacimutal de bajo costo impresa en 3D, y hacen falta ocho noches de
> observación para demostrarlo.**

Eso es todo. No es el preentrenamiento en simulación (se cayó, y está medido en
[`08`](08-diseno-definitivo.md) §4). No es el estudio de inferencia en CPU, acelerador y nube
(es otro proyecto, [`10`](10-revision-propuesta-edge-ai.md)). No es la interfaz web.

**Es el único resultado que se sostuvo en 6 de 6 sorteos independientes:** mediana 3,93′ →
3,50′. Modesto, pero real, medible en el tiempo que te queda y tuyo.

---

## 2. Las decisiones que estaban abiertas, ya cerradas

### Título (16 palabras, sin abreviaturas)

> **Corrección del apuntado de una montura altacimutal de bajo costo con aprendizaje
> automático sobre el residuo**

### Pregunta

> ¿En qué medida un modelo de aprendizaje automático entrenado sobre el residuo del modelo
> clásico de apuntado reduce el error de una montura altacimutal de bajo costo, y cuántas
> noches de observación hacen falta para lograrlo?

### Objetivo general

> Determinar en qué medida un corrector de aprendizaje automático entrenado sobre el residuo
> del modelo clásico reduce el error de apuntado de una montura altacimutal de bajo costo
> construida con impresión 3D, y cuántas noches de observación reales requiere.

### Hipótesis: quedan tres, no cuatro

| | Enunciado | Experimento |
|---|---|---|
| **H1** | El error de apuntado de la montura impresa es sistemático: el modelo clásico explica una parte y queda un residuo no lineal apreciable | E1 |
| **H2** | Los modelos no lineales (LightGBM, MLP) reducen el error residual más que la regresión Ridge | E3 |
| **H3** | Un detector aprendido mide el centro lunar con menor error y menos fallos que la transformada de Hough, sobre todo en fases delgadas | E2 |

**La antigua H3 (preentrenamiento) se elimina**, no se reemplaza. La antigua H4 pasa a ser H3.

**El objetivo 4 se queda sin hipótesis, y está bien.** Pasa a ser descriptivo: *"Cuantificar
la curva de error frente al número de noches de entrenamiento con datos reales"*. No toda
pregunta necesita hipótesis; algunas se responden midiendo y mostrando la curva. La rúbrica
pide objetivos con resultado, no hipótesis por objetivo.

Los cinco objetivos específicos y los cinco experimentos **no cambian**.

---

## 3. Qué estudias exactamente

Dos cosas, y conviene tenerlas separadas en la cabeza:

| | |
|---|---|
| **El objeto de estudio** | El error de apuntado de **tu** montura. No el cielo: Skyfield ya calcula dónde está la Luna con precisión de segundos de arco. Lo que nadie sabe es cuánto flexiona *este* PETG, cuánta holgura tienen *estas* correas y cuánto está desnivelado *este* trípode |
| **La comparación** | Modelo clásico de apuntado **contra** modelo clásico + corrector aprendido. Y entre correctores: Ridge, LightGBM y MLP |

**El instrumento de medida es la cámara**, y la Luna es el caso de prueba porque es brillante,
su posición se conoce con exactitud y se ve también de día.

### Lo que tienes que leer (es poco)

1. **Mu et al. (2026)** y **Hu y Zhu (2026)** — de ahí sale la nomenclatura de los términos del
   modelo clásico. No los cites de memoria.
2. **He et al. (2026, FinalKAN)** y **Bergerhoff (2024, EUSIPCO)** — las dos de lectura
   obligatoria de [`08`](08-diseno-definitivo.md) §11.

Son cuatro artículos. No necesitas estudiar aprendizaje automático desde cero: necesitas poder
explicar **por qué el modelo aprende el residuo y no la posición**, que es la decisión central
y está en [`08`](08-diseno-definitivo.md) §3.

---

## 4. Qué se programa (y quién lo programa)

**Yo escribo el código. Tú no programas nada.** Está en
[`09`](09-manos-a-la-obra.md) §4 y se mantiene:

| Estado | Módulos |
|---|---|
| ✅ Hechos | `errores.py`, `simulador.py`, `registro.py`, `aprendizaje.py` · 101 pruebas en verde |
| ⏳ Me faltan | `alineacion.py`, los scripts de `analisis/`, `camara.py`, `deteccion.py`, el panel web, `instalar.sh` |

Lo que **sí te toca** es entenderlo lo suficiente para defenderlo. Para eso está
[`08`](08-diseno-definitivo.md) §12, que es el guion de la sustentación.

---

## 5. Qué construyes del prototipo

La montura ya está diseñada, sin interferencias y con los STL listos. No hay nada que
rediseñar. Lo que falta es **comprar, imprimir y armar**:

| | Estado |
|---|---|
| Piezas 3D, circuito, plano de cableado, orden de armado | ✅ Listos en `montura/` y `circuito/` |
| Poleas GT2 de 20 dientes y rodamiento *lazy susan* | ❌ **Sin comprar. Bloquean todo** |
| Cámara | ❌ **Sin comprar. Bloquea todas las mediciones** |
| Medidas con calibrador de las piezas que ya tienes | ❌ Pendientes ([`09`](09-manos-a-la-obra.md) §5) |

---

## 6. La cámara: decidida

**Raspberry Pi HQ Camera (IMX477) con lente C-mount de 25 a 28 mm. USD 50–90.**

Por qué esa y no las otras dos, con el número que decide:

| | Campo de visión | Escala | La Luna |
|---|---|---|---|
| **HQ Camera + 25–28 mm** ✅ | **13° × 10°** | ~12″/píxel | 145–163 px |
| Camera Module 3 + guía de 200 mm (la de la propuesta) | **1,9° × 1,0°** | ~3″/píxel | 320 px |
| Sony + Tamron | — | — | ~1 700 USD, fuera de presupuesto |

**El número que decide es el campo de visión, no la resolución.** Tu error de apuntado *antes*
de corregir es del orden de **1°**. Con el campo de 1,0° de alto de la segunda opción, la Luna
se te sale del cuadro en buena parte de los apuntados, y un apuntado sin medición es un dato
perdido. Con 10° de alto, la Luna **siempre** está dentro.

¿Y alcanza la resolución? Sí: el efecto que tienes que medir es de 0,43′ ≈ 26″, o sea unos
2 píxeles. Ajustando un círculo al limbo lunar (que es lo que hace Hough, y por eso E2 existe)
la precisión es de medio píxel, unos 6″. Te sobra un factor de cuatro.

Ventajas de paso: se conecta directo a la Pi por cable CSI, sin capturadora HDMI ni SDK de
Sony, que eran dos dependencias sin probar.

> Al montarla hay que **calibrar la escala de placa**, usando el diámetro angular conocido de
> la Luna. Es media hora de trabajo y da un dato que va en la metodología.

---

## 7. El artículo que ya está escrito

Esto también causaba confusión: **el `articulo_v2.docx` que está en tu Drive corresponde al
alcance anterior.** No se parchea, se rehace en parte.

| Qué pasa con cada sección | |
|---|---|
| ✅ **Se queda** | El formato Esprint, la maquetación, la bibliografía y buena parte de la Introducción |
| ✏️ **Se reescribe** | Título, resumen, pregunta, objetivos, hipótesis, metodología, resultados, discusión y conclusiones |
| ❌ **Se elimina** | El estudio de usabilidad con 20 participantes y la escala SUS (la rúbrica no tiene ningún ítem de usabilidad), y las referencias a "objetos celestes" y a la interfaz web como objeto de estudio |

Eso **no es trabajo perdido**: la estructura, el formato y las referencias son la mitad del
trabajo de un artículo, y están hechas. Lo que se reescribe se reescribe en las semanas 12 a
13, cuando ya haya números.

---

## 8. Cronograma, recalculado desde hoy

**Quedan 13,6 semanas** (16/11/2026 → 19/02/2027). El cronograma de
[`08`](08-diseno-definitivo.md) §9 arrancaba el 06/11 y el frente de hardware no se movió, así
que esto lo reemplaza:

| Semana | Fechas | Tú | Yo |
|---|---|---|---|
| **1** | 16–22 nov | **Comprar cámara, poleas y lazy susan.** Medir las piezas con calibrador. Hablar con el tutor. Imprimir `prueba_gt2.stl` | `alineacion.py` |
| **2** | 23–29 nov | Imprimir las 13 piezas | Scripts de `analisis/` (E1–E5 con datos sintéticos) |
| **3** | 30 nov–6 dic | Armar la mecánica y cablear. **Prueba de banco, 11 pasos** | `camara.py` |
| **4** | 7–13 dic | Montar la cámara. Calibrar la escala de placa. Balancear | `deteccion.py` (Hough y aprendido) |
| **5** | 14–20 dic | **Primera sesión de prueba.** ⚠️ Hito de no retorno | Panel web de alineación y seguimiento |
| **6–10** | 21 dic–24 ene | **Las 8 noches.** Incluye Luna de día | Ajustes y apoyo |
| **11** | 25–31 ene | — | Análisis E1–E5, tablas y figuras definitivas |
| **12–13** | 1–14 feb | Escribir Resultados, Discusión y Conclusiones | Apoyo en redacción |
| **13,5** | 15–19 feb | Revisión del tutor, correcciones, maquetación, **entrega** | |

**Las semanas 6 a 10 caen sobre Navidad y Año Nuevo.** Son cinco semanas para ocho noches,
y la Luna de día ayuda, pero no sobra margen: si en la semana 5 la montura no mide, se activa
el plan B de [`08`](08-diseno-definitivo.md) (blancos terrestres a posiciones conocidas, sin
cielo).

---

## 9. Lo único que te toca esta semana

Tres cosas. Nada más.

1. **Comprar**, hoy si se puede, porque bloquean todo lo demás:
   - 2 poleas GT2 de 20 dientes, agujero de 8 mm, ancho de 6 mm
   - 1 rodamiento giratorio *lazy susan* de 4″ (102 mm)
   - 1 Raspberry Pi HQ Camera + lente C-mount de 25–28 mm
2. **Medir con calibrador** las siete medidas de [`09`](09-manos-a-la-obra.md) §5 y mandármelas.
3. **Hablar con el tutor** con el mensaje de abajo.

---

## 10. Qué decirle al Ing. Corrales

> Ingeniero, buenas tardes. Le escribo por dos cosas.
>
> **1. El enfoque del artículo.** Al comprobar en simulación el preentrenamiento que habíamos
> planteado, el resultado fue negativo en las tres variantes que probé, así que ese ya no puede
> ser el aporte. Lo que sí se sostuvo en 6 de 6 repeticiones independientes es que **el
> corrector aprendido sobre el residuo vence al modelo clásico de apuntado** (mediana 3,93′ →
> 3,50′). Propongo que ese sea el aporte, con este título de 16 palabras:
>
> *"Corrección del apuntado de una montura altacimutal de bajo costo con aprendizaje automático
> sobre el residuo"*
>
> Eso implica eliminar la hipótesis del preentrenamiento y el estudio de usabilidad con la
> escala SUS, porque la rúbrica del lector no tiene ningún ítem de usabilidad y las 13 semanas
> que quedan no alcanzan. ¿Lo del título y el objetivo necesitan algún trámite?
>
> **2. Su propuesta de Edge-AI.** La leí completa y me parece muy buena, pero no me cabe: pide
> seis meses, 90 episodios y dos manuscritos, y a mí me quedan 13 semanas. Además usaría
> NEMA 17, TMC2209 y una Pi 5, y yo ya tengo comprados NEMA 23, TB6600 y una Pi 4.
>
> Sí quiero tomar de ahí cuatro ideas que mejoran mi artículo sin costo: verificar el apuntado
> con un solver independiente del mío, descomponer el error en los cuatro términos físicos,
> reportar la latencia en p50 y p95, y medir la energía con un INA219.
>
> Y una propuesta: su documento dice que la correa de 5:1 es lo único que compra exactitud
> frente al error de ángulo de paso, y mi montura ya la tiene, con 17 veces más par en el eje
> de altitud que la suya. ¿Tendría sentido que su estudio corra sobre mi montura, en lugar de
> construir una nueva? Así los dos trabajos se suman.
>
> Quedo atenta.

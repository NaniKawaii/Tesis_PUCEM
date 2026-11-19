# Paso 13 · Un tema sólido: cuerpos celestes, con tu montura y tu Sony

Escrito el **19/11/2026**, después de la nota de voz del Ing. Ricaurte (18/11) y de tu
respuesta: quieres un tema sólido, que use lo que ya compraste —incluida la **Sony ZV-E10 II
con el Tamron 17-70**— y cuyo objetivo sean **los cuerpos celestes**, no solo la Luna.

> **En una línea:** la montura se calibra **fotografiando el cielo con la Sony y resolviendo
> la foto contra un catálogo de estrellas** (*plate solving*), en la propia Raspberry Pi. Eso
> da el error de apuntado exacto en cualquier punto del cielo, sin Luna y sin telescopio. Con
> esos datos se compara el modelo clásico con el corrector aprendido, y la Pi con la nube.

---

## 1. Por qué hay que cambiar: el resultado actual solo vale sobre el arco

El resultado de noviembre **se sostiene**: el corrector aprendido le gana al modelo clásico
en 6 de 6 sorteos, 3,93′ → 3,51′, 4 con p < 0,05. Lo volví a correr hoy con los parámetros
documentados y sale igual. **El documento que le enviaste al Ing. Ricaurte está bien.**

Pero hoy medí algo que no habíamos medido: **qué pasa fuera del arco donde se entrenó.** El
diseño actual sigue a la Luna unas 4 horas, o sea un arco de cielo. Para apuntar a un planeta
o a una estrella, el modelo tiene que servir en **todo** el cielo.

Simulación, 8 noches, 6 sorteos independientes (`analisis/protocolo_cielo.py --sondeo 0`):

| Cómo se tomaron los datos | Error en el arco | Error en todo el cielo |
|---|---|---|
| Ninguna corrección (solo alineación de la noche) | — | **12,9′** |
| **Arco** (seguir la Luna): clásico | 3,93′ | 16,7′ |
| **Arco** (seguir la Luna): aprendido | **3,51′** | 15,5′ |
| **Todo el cielo** (60 fotos resueltas por noche): clásico | — | 7,3′ |
| **Todo el cielo** (60 fotos resueltas por noche): aprendido | — | **6,3′** |

Léelo así:

- **Entrenado sobre el arco, el modelo empeora el apuntado en el resto del cielo**: 15–17′
  contra 12,9′ sin corregir nada. El 3,5′ es real, pero solo donde se entrenó.
- **Entrenado con fotos repartidas por todo el cielo, el error baja a ~6–7′ en todas partes**,
  la mitad que sin corregir y menos de la mitad que con el arco.

Esto es justo lo que el Ing. Ricaurte vio al leer tu documento: *"solo habla de la Luna"*.
Tenía razón, y ahora hay un número que lo demuestra.

> Todo esto es **simulación**. Sirve para elegir el diseño; los resultados del artículo salen
> del campo.

---

## 2. El tema

**Título de trabajo:**

> *Apuntado autónomo de cuerpos celestes con una montura altacimutal de bajo costo:
> calibración por resolución astrométrica en el borde y corrección del error con aprendizaje
> automático*

**La idea, en tres pasos:**

1. La montura apunta a un sitio del cielo. La Sony toma una foto de 2–4 s.
2. La Pi resuelve la foto contra un catálogo de estrellas (ASTAP) y sabe **exactamente**
   adónde quedó apuntando. La diferencia con lo que pidió es el error, en minutos de arco.
3. Con unas 60 fotos por noche, repartidas por todo el cielo, se ajusta el modelo de error.
   Después la montura apunta a la Luna, a los planetas o a las estrellas que quieras.

**Por qué la Sony sirve tan bien:**

| | Sony ZV-E10 II + Tamron a ~50 mm |
|---|---|
| Campo | ~27° × 18°: cualquier error de la montura cabe en la foto |
| Escala | ~15″ por píxel: un error de 5′ son ~20 píxeles, se mide de sobra |
| Peso | ~0,9 kg, la mitad que un Maksutov: menos carga para la montura |
| Telescopio | **No hace falta.** La cámara es el instrumento de medida |

A esa focal, ASTAP resuelve con su base de estrellas de campo amplio (W08). Todo corre en la
Pi 4 que ya tienes.

---

## 3. Preguntas e hipótesis

| | Pregunta | Qué se mide | ¿Sale un resultado sí o sí? |
|---|---|---|---|
| **P1** | ¿Qué error de apuntado logra la montura en todo el cielo tras calibrarse por plate solving? | Error en minutos de arco, en noches nuevas, sobre cuerpos celestes reales | **Sí.** Es una medición |
| **P2** | ¿El corrector aprendido reduce el error frente al modelo clásico? | Wilcoxon pareado, dejando una noche fuera, 8 noches | Sí, y **cualquiera de las dos respuestas se publica** |
| **P3** | ¿Conviene resolver en la Pi o en la nube? | Latencia p50/p95, tasa de éxito, energía (Wh), funcionamiento sin internet | **Sí.** Es una medición |
| **P4** | ¿Un modelo entrenado en un trozo del cielo sirve en el resto? | Se entrena con un sector de azimut y se evalúa en el resto, con los mismos datos | **Sí**, sin noches extra |

**Por qué este tema es sólido:** tres de las cuatro preguntas son **mediciones de ingeniería**
que dan un número aunque nada salga como se espera. El artículo no depende de que la IA gane.

**Sobre P2, con honestidad:** en simulación, con datos de todo el cielo, el corrector
aprendido le gana al clásico en 4 de 6 sorteos, y con significancia en 1 de 6. Con la huella
de sesión (`--sondeo 6`) sube a 5 de 6 en todo el cielo y 2 de 6 significativos. **Es una
mejora pequeña y no está garantizada.** Por eso P2 es una pregunta y no una promesa: si el
clásico gana, eso también es un resultado, y el artículo lo dice.

---

## 4. Respuesta al Ing. Ricaurte: qué me gusta, qué no, qué quiero cambiar

Es lo que te pidió en la nota de voz. Puedes enviarlo tal cual o adaptarlo.

### Lo que me gusta y adopto

1. **Que el telescopio resuelva el plate solving él mismo, sin portátil.** Es el centro del
   tema nuevo.
2. **Los cuerpos celestes en general**, no solo la Luna.
3. **Comparar la Pi con la nube**, con latencia en mediana y percentil 95, coste y energía
   medida con un INA219, y la pregunta de qué pasa sin conectividad.
4. **Verificar con un solver que no es el mío**: ASTAP para operar y astrometry.net para
   verificar, para que un sesgo del modelo no se esconda.
5. **Los cuatro términos físicos del error** (periódico, flexión, refracción, backlash) y
   aproximarse siempre desde la misma dirección.
6. **Hipótesis fijadas antes de medir.**

### Lo que no me cabe

1. **Los seis meses y los 90 episodios.** Me quedan unas 13 semanas.
2. **El hardware nuevo** (Pi 5, NEMA 17, TMC2209, Camera Module 3, guía de 50 mm). Dejaría sin
   uso los USD 257 que ya invertí. Además, su propia Figura 4 muestra que un NEMA 17 en acople
   directo no puede mover un tubo desequilibrado; mi montura, con NEMA 23 y correa de 5:1, sí.
3. **El Hailo-8L y entrenar un solver neuronal en INT8.** Necesita compilar en un PC x86,
   reunir un dataset y entrenar redes: es un proyecto entero por sí solo, y su propio documento
   reconoce que podría quedar "no medido".
4. **AWS Lambda con facturación.** Prefiero la API gratuita de astrometry.net como condición de
   nube: mide lo mismo sin coste.
5. **Dos manuscritos IEEE.** Mi meta es un artículo, probablemente en la revista de la PUCE.

### Lo que propongo cambiar

- **Correr el estudio sobre mi montura** (NEMA 23, TB6600, correas 14:1 y 5:1), con mi Pi 4 y
  mi **Sony ZV-E10 II + Tamron 17-70** como cámara.
- **Dos condiciones de cómputo**: la CPU de la Pi 4 (ASTAP) frente a la nube (astrometry.net).
  El acelerador queda como trabajo futuro.
- **Mantener el corrector aprendido** como la parte de inteligencia artificial, comparado con
  el modelo clásico de apuntado.
- Una pregunta para usted: **¿le parece bien este alcance para el artículo de titulación?**

---

## 5. Cronograma: 13 semanas, hasta el ~19/02/2027

| Semanas | Fechas | Qué |
|---|---|---|
| 1–2 | 19/11 – 02/12 | **Probar la Sony con la Pi** (ver §6). Instalar ASTAP en la Pi. Resolver una foto tomada a mano desde tu casa: no necesita la montura. Cuenta gratuita en astrometry.net |
| 3–5 | 03/12 – 23/12 | Terminar la montura. Programa de sesión: 60 fotos repartidas por el cielo, ~1 hora. Primera noche de prueba |
| 6–10 | 24/12 – 27/01 | **8 noches de campo** de ~1 hora. Una noche final de validación con la Luna, planetas y estrellas brillantes |
| 11–13 | 28/01 – 19/02 | Análisis (P1–P4) y redacción |

**Ventaja frente al diseño anterior:** cada noche son ~60 minutos, no 4 horas. En la época de
lluvias de Manabí es mucho más fácil encontrar una hora despejada que cuatro.

---

## 6. Riesgos y qué hacer con cada uno

| Riesgo | Plan |
|---|---|
| **Que la Pi no pueda disparar la Sony por USB** | Es lo primero que se prueba. Sony lista el ZV-E10 II en su SDK de control remoto; con `gphoto2` no encontré confirmación, así que hay que probarlo con la cámara en modo "PC Remote". Si ninguno funciona, la salida HDMI con una capturadora |
| **Nubes** (temporada de lluvias) | Sesiones de 1 hora; si al 27/01 hay 6 noches y no 8, se informa la dirección del efecto y que no alcanzó significancia (docs/08 §6) |
| **El corrector aprendido no gana** | P2 es una pregunta: se publica lo que salga. P1, P3 y P4 no dependen de eso |
| **La montura no está lista a tiempo** | Las semanas 1–2 no necesitan la montura, así que no se pierden |

---

## 7. Qué cambia en lo que ya está hecho

- **El software casi no cambia.** El corrector, la validación dejando una noche fuera, las
  pruebas estadísticas y el simulador se quedan. Se añaden la captura con la Sony, la llamada
  a ASTAP y el programa de sesión de 60 fotos.
- **El hardware no cambia.** Lo comprado se usa entero. Se agrega un **INA219** (~USD 3) para
  medir la energía.
- **La recomendación de la Pi HQ Camera** de [`11`](11-tu-articulo-en-una-pagina.md) **queda
  retirada**: la Sony ya es tuya y sirve mejor para este tema.
- **El detector del disco lunar** pasa a ser una demostración de la noche de validación, no el
  instrumento de medida.

---

## 8. Reproducir los números de la §1

```bash
cd prototipo
python -m analisis.e5_transferencia --sorteos 6 --sondeo 0 --monturas 2 --noches 8
python -m analisis.protocolo_cielo --sorteos 6 --noches 6 8 --puntos 60 --sondeo 0
python -m analisis.protocolo_cielo --sorteos 6 --noches 6 8 --puntos 60 --sondeo 6
```

La columna "arco" de `protocolo_cielo` reproduce exactamente el resultado de `e5` (3,93′ →
3,51′, 6 de 6): es la comprobación de que los dos scripts miden lo mismo.

# Paso 14 · Respuesta al Ing. Ricaurte: título con tecnologías y revisión de su hardware

Escrito el **20/11/2026**. Nashla le envió los títulos de [`13`](13-tema-solido.md) y él
respondió:

> *"Sí Nashla, pero debes sumar tecnologías en el título como te pasé, del que te compartí si
> pudiste leer algo, para que me digas qué cambios te gustarían o qué no te agrada."*

Con eso envió dos archivos:

- **`Propuesta_Final_v3_ES.docx`**: es **idéntico, byte por byte**, al que ya revisamos el
  19/11. No trae nada nuevo. La respuesta de [`13`](13-tema-solido.md) §4 sigue valiendo.
- **`hardware.zip`**: lo nuevo. Es el diseño completo de su montura. Trae la lista de
  materiales, la lista de compras, una guía de ensamblaje de 10 pasos, el cableado y 20
  piezas en OpenSCAD con sus STL (soporte del tubo, contrapeso, soporte de la Camera Module 3,
  bases de los motores y acoples).

---

## 1. El título, con tecnologías

Su título era:

> *Edge-AI en hardware embebido de bajo coste para el apuntado autónomo de objetos celestes:
> estudio comparativo de inferencia en CPU, acelerador y nube*

Las tecnologías que nombra son **Edge-AI, hardware embebido, CPU, acelerador y nube**. La
propuesta conserva su estructura y cuatro de las cinco. Solo sale el acelerador, porque el
Hailo-8L no cabe en el plazo (§2).

### Opción A, la recomendada: la más cercana a la suya

> **Edge-AI en hardware embebido de bajo costo para el apuntado autónomo de cuerpos celestes:
> resolución astrométrica en CPU embebida frente a la nube y corrección del error con
> aprendizaje automático**
>
> *Edge-AI on low-cost embedded hardware for autonomous pointing at celestial objects:
> astrometric plate solving on an embedded CPU versus the cloud, and machine-learning error
> correction*

Conserva su primera mitad casi palabra por palabra. Él va a reconocer su título.

### Opción B: nombra la placa

> *Edge-AI en una Raspberry Pi para el apuntado autónomo de cuerpos celestes: plate solving
> local frente a la nube y corrección del error con aprendizaje automático*

### Opción C: la más corta

> *Apuntado autónomo de cuerpos celestes con Edge-AI: Raspberry Pi, plate solving y
> aprendizaje automático en una montura de bajo costo*

### Una precaución sobre "Edge-AI"

En su propuesta, la IA en el borde era el propio *solver*: una red neuronal. En la tuya, el
*plate solving* lo hace ASTAP, que **no** es IA: es astrometría clásica. La IA en el borde es
el **corrector del error**, que se ejecuta en la Raspberry Pi. El título es correcto, pero un
revisor puede preguntar *"¿dónde está la IA en el borde?"*. La respuesta es esa, y la
Introducción ya lo dice en el objetivo.

---

## 2. Su hardware: qué te gusta, qué no y qué cambiarías

### Lo que me gusta y adopto

| Idea | Por qué |
|---|---|
| **Medir la energía con un INA219** | Ya estaba adoptada. Cuesta unos USD 3 |
| **Un condensador de 100 µF por driver** | Buena práctica para los picos de corriente. Barato y no cambia el diseño |
| **Contrapeso ajustable** (`counterweight_bracket`) | La Sony con lente pesa ~0,9 kg. Equilibrarla reduce la carga del eje de altitud y el error por flexión |
| **"Equilibrar primero, taladrar después"** | Buscar el centro de masa real de la cámara con un palo redondo antes de fijarla. Gratis y útil |
| **Su advertencia sobre el rocío** | En Manabí, con la humedad de la costa, el rocío en el lente puede acabar la sesión antes que la montura. Conviene un parasol o una cinta calefactora USB |
| **Ajustar los dos drivers igual** | Misma corriente en ambos ejes, para que respondan igual |

### Lo que no me cabe

**1. La Camera Module 3 y el telescopio guía (USD 80).** Mi Sony con su lente ya da una
escala parecida, y sin comprar nada:

| | Su diseño | Mi Sony a 50–70 mm |
|---|---|---|
| Escala de la imagen | 6,9″ por píxel | 11–15″ por píxel |
| Campo | angosto | ~19–27° de ancho |
| Costo nuevo | USD 80 | **USD 0**, ya la tengo |

Su propia lista de materiales dice que **sin óptica** la Camera Module 3 tiene un campo de
66° y no resuelve de forma estable. La Sony con lente no tiene ese problema. Un error de
apuntado de 5′ son 19–27 píxeles: se mide de sobra.

**2. Los NEMA 17 en acople directo no pueden con la Sony.** Sus notas lo calculan: el motor da
0,28 N·m. Con ~0,9 kg de cámara, eso alcanza solo si el centro de masa queda a **menos de
~3 cm** del eje. Mi eje de altitud, con NEMA 23 y correa 5:1, da ~4,75 N·m: unas 17 veces
más.

**3. La exactitud la compra la correa, no el micropaso.** Lo dicen sus propias notas: el
micropaso 1/256 del TMC2209 no corrige el error de ±5,4′ de cada paso del motor. La correa
5:1 lo baja a ±1,08′, y él la deja como mejora futura. **Mi montura ya la tiene**: 5:1 en
altitud y 14:1 en azimut (±0,39′).

**4. Rehacer la estructura.** Su diseño usa extrusión 2020, piezas impresas nuevas y una lista
de compras de **USD 200**, más 70 del Hailo. El mío ya está diseñado, con la proforma de
Megatrónica comprada, y usa todo lo que tengo.

**5. El Hailo-8L.** Necesita un PC x86 para compilar el modelo, y su propia guía lo deja para
"solo cuando exista el host x86". No cabe en 13 semanas. Queda como trabajo futuro.

### Lo que propongo

- **Mantener mi montura** (NEMA 23, TB6600, correas 14:1 y 5:1, Pi 4) y **mi Sony** como
  instrumento de medida.
- **Sumar de su diseño**: el INA219, los condensadores, el contrapeso, la regla de equilibrar
  primero y la protección contra el rocío.
- **Una pregunta**: la Pi 5 y los NEMA 17 figuran "en posesión" en su lista. ¿Son suyos? Si
  me prestara la Pi 5, podría sumar una tercera condición de cómputo sin comprar nada. No es
  imprescindible.

---

## 3. Mensaje listo para enviar

> Buenas tardes, Ingeniero. Sí revisé su propuesta y el hardware que me envió.
>
> **Título.** Le sumé las tecnologías manteniendo su estructura:
>
> *"Edge-AI en hardware embebido de bajo costo para el apuntado autónomo de cuerpos celestes:
> resolución astrométrica en CPU embebida frente a la nube y corrección del error con
> aprendizaje automático"*
>
> Solo quité el acelerador, porque el Hailo necesita un PC x86 para compilar y no me alcanza
> el tiempo. Lo dejo como trabajo futuro.
>
> **Lo que me gusta y adopto:** el plate solving en el propio equipo, la comparación con la
> nube (latencia p50/p95, energía con INA219, funcionamiento sin internet), verificar con un
> segundo solver, los cuatro términos del error, el contrapeso con la regla de equilibrar
> primero, los condensadores por driver y la protección contra el rocío.
>
> **Lo que cambiaría:**
>
> 1. Usar mi Sony con su lente en lugar de la Camera Module 3 con guía: da 11–15″ por píxel,
>    suficiente para medir errores de minutos de arco, y ya la tengo.
> 2. Usar mi montura (NEMA 23 con correas 5:1 y 14:1). Como dicen sus notas, la exactitud la
>    da la correa, no el micropaso. Además, los NEMA 17 en directo solo moverían la Sony si
>    queda equilibrada a menos de ~3 cm del eje.
> 3. Así uso todo lo que ya compré, y en lugar de USD 200 a 270 solo agrego el INA219.
>
> Una consulta: la Pi 5 y los NEMA 17 que figuran "en posesión", ¿son suyos?
>
> ¿Le parece bien este título y este alcance?

# Paso 9 · Manos a la obra: quién hace qué, y en qué orden

Reparto concreto del trabajo para las 15 semanas, a partir del diseño de
[`08-diseno-definitivo.md`](08-diseno-definitivo.md). Sustituye el plan de
[`04-plan-de-trabajo.md`](04-plan-de-trabajo.md), que corresponde al enfoque anterior.

---

## 1. Lo que ya está hecho (no lo rehagas)

Antes de nada: buena parte de lo que hace falta **ya existe en este repositorio**.

| Ya está | Dónde | Estado |
|---|---|---|
| Piezas de la montura, diseñadas y sin interferencias | [`montura/`](../montura/LEEME.md) | **STL listos para imprimir** |
| Guía de impresión: material, capas, perímetros, relleno, orientación | `montura/LEEME.md` §3 | Lista |
| Tornillería y piezas compradas que hacen falta | `montura/LEEME.md` §4 | Lista |
| Orden de armado | `montura/LEEME.md` §7 | Listo |
| Esquema de conexiones, cable por cable | [`circuito/`](../circuito/LEEME.md) §1 | Listo |
| Configuración de los interruptores DIP de los TB6600 | `circuito/LEEME.md` §2 | Lista |
| Prueba de banco en 11 pasos, con programa | `circuito/LEEME.md` §4 | Lista, **sin ejecutar** |
| Plano de cableado dentro de la caja de control | `circuito/LEEME.md` §6 | Listo |
| Lista de compras con especificaciones | [`docs/05`](05-lista-para-proveedor.md) | Lista |
| Revisión de la proforma del proveedor | [`docs/06`](06-revision-proforma.md) | Hecha, V2 aprobada |
| Software base: efemérides, motores, montura, web, registro, corrección | [`prototipo/`](../prototipo/README.md) | v0.1, corre en simulación |

**Lo que falta no es diseño: es ejecutar, y escribir el software nuevo del artículo.**

---

## 2. Tres desajustes en el código que hay que arreglar primero

Encontrados el 06/11/2026 al revisar `prototipo/` contra el diseño nuevo. Los tres dañan los
datos si no se corrigen **antes** de generar nada.

### 2.1 La reducción está puesta en acople directo

`config.py` define `reduccion: float = 1.0` con el comentario "1 = acople directo", y el
docstring del módulo dice "NEMA 23 con acople directo". Pero [`docs/03`](03-telescopio-montura-energia.md)
decidió reducciones de **14:1 en azimut** y **5:1 en altitud**, y la montura de `montura/` está
diseñada para ellas.

Con los valores actuales, `pasos_por_grado` sale 14 veces (azimut) y 5 veces (altitud) más
pequeño de lo real: **cada movimiento quedaría corto por ese factor.** Valores correctos:

| Eje | Reducción | Pasos por grado | Resolución |
|---|---|---|---|
| Azimut | 14:1 | 124,4 | **0,48′** por micropaso |
| Altitud | 5:1 | 44,4 | **1,35′** por micropaso |

### 2.2 La validación cruzada parte las filas al azar

`correccion.py` usa `KFold`, que reparte las filas aleatoriamente. Con el registro actual (una
fila por apuntado manual) era defendible. **Con el registro nuevo, de una fila por segundo, es
un error grave:** dos filas del mismo minuto son casi la misma observación, así que caerían una
en entrenamiento y otra en prueba, y el resultado quedaría inflado.

Hay que cambiarlo por **validación dejando una noche fuera** (`GroupKFold` agrupando por
sesión). Es el error metodológico más fácil de detectar en una revisión, y el más caro.

### 2.3 El esquema del registro es de otro experimento

`registro.py` guarda **una fila por apuntado**, con el centrado manual del usuario. El diseño
nuevo necesita **una fila por segundo** con sensores: temperatura, presión, inclinación, ángulo
del encoder, sentido del último giro, fase lunar y centro detectado en la imagen.

Hay que añadir un esquema nuevo, conservando el viejo para no romper lo que ya funciona.

---

## 3. El orden: tres frentes en paralelo

```
 Frente A · SIMULACIÓN Y SOFTWARE        Frente B · HARDWARE           Frente C · ARTÍCULO
 (no depende de nada, empieza ya)        (depende de compras)          (empieza ya)
 ─────────────────────────────────       ──────────────────────        ───────────────────
 Sem 1-2  modelo de error + simulador     Sem 1   comprar lo que falta  Sem 1  hablar con
 Sem 2-4  pipeline de ML completo         Sem 1-2 medir las piezas             el tutor
          sobre datos sintéticos          Sem 2-3 imprimir y armar      Sem 1-14 repasar la
 Sem 3-4  captura y registrador           Sem 3   prueba de banco               Introducción
 Sem 5-6  detector lunar                  Sem 4-5 armado y calibración          (ítems 6 y 7)
                          │                           │
                          └────────── Sem 6-11 ───────┘
                               NOCHES DE OBSERVACIÓN
                                mínimo 6, objetivo 8
                                        │
                        Sem 11-12  análisis  →  Sem 12-15  redacción
```

**El frente A no espera a nadie.** Es el punto entero del enfoque: mientras la montura está en
la impresora, el software del artículo ya se está escribiendo y validando.

---

## 4. Qué escribo yo, y en qué orden

Todo dentro de `prototipo/`. Cada módulo se entrega con sus pruebas automáticas.

| # | Archivo | Qué hace | Bloquea a |
|---|---|---|---|
| **1** | `telescopio/errores.py` | **El modelo de error paramétrico.** Dado (az, alt), un vector de parámetros y el estado (sentido de giro, temperatura), devuelve Δaz y Δalt | 2, 3, 5 |
| **2** | `telescopio/simulador.py` | **Aleatorización de dominio.** Muestrea vectores de parámetros, genera noches sintéticas con posiciones reales de Skyfield y escribe el dataset | 4 |
| **3** | `telescopio/registro.py` (ampliar) | Esquema nuevo de una fila por segundo. **El simulador y el registrador real escriben el mismo formato** | 4 |
| **4** | `telescopio/correccion.py` (rehacer) | Los cuatro modelos, validación dejando una noche fuera, preentrenamiento más ajuste fino, Friedman y Nemenyi | 6 |
| **5** | `telescopio/alineacion.py` | Calibración de sesión: ajusta por mínimos cuadrados los términos de sesión con 2 o 3 puntos más la lectura del GY-91 | noches |
| **6** | `analisis/` | Scripts que generan **las tablas y figuras del artículo** (E1 a E5) directamente desde el CSV | redacción |
| 7 | `telescopio/camara.py` | Captura de fotogramas y volcado del dataset de imágenes | cuando haya cámara |
| 8 | `telescopio/deteccion.py` | Hough frente a detector aprendido | 7 |
| 9 | `telescopio/servidor.py` (ampliar) | Interfaz: panel de alineación, panel de seguimiento en vivo, panel de entrenamiento | 7 |
| 10 | `instalar.sh` | Instalación en la Raspberry Pi con un solo comando, más arranque automático y red Wi-Fi propia | cuando haya Pi lista |

**La decisión de diseño que sostiene todo:** el punto 1 es un módulo **compartido**. El
simulador lo usa para *generar* el error, y la alineación de sesión lo usa para *ajustarlo* a
los datos reales. Una sola definición de los términos, usada en los dos lados: así no puede
haber desacuerdo entre lo que se simula y lo que se mide.

### De dónde salen los rangos de aleatorización

Es la única pieza del simulador que puede invalidarlo, así que conviene decirlo claro: los
rangos iniciales se derivan de la geometría de la montura (tolerancia de impresión, holgura
típica de una correa GT2, precisión con que se nivela un trípode) y **se declaran en el
artículo**.

Luego, con la primera noche real, se comprueba si la montura cae dentro de los rangos
muestreados. Si no cae, se amplían y se reentrena. **Esa comprobación no es un trámite: es la
validación del simulador**, y es un resultado del artículo por derecho propio.

---

## 5. Qué te toca a ti

Ordenado por lo que bloquea a lo demás.

### Esta semana

1. **Hablar con el Ing. Corrales.** Es lo único que puede invalidar todo lo demás: quitar el
   estudio de usabilidad cambia un objetivo aprobado, y el título nuevo puede necesitar trámite.
2. **Decidir la cámara** (ver [`docs/08`](08-diseno-definitivo.md) §13, pendiente 2).
3. **Comprar lo que bloquea la impresión 3D:** 2 poleas GT2 de 20 dientes con agujero de 8 mm, y
   el rodamiento giratorio *lazy susan* de 4″. Sin ellos la montura no se mueve.
4. **Medir con calibrador y mandarme los números.** Esto es lo que yo no puedo hacer y bloquea
   el ajuste de los STL:

   | Medida | De qué |
   |---|---|
   | Largo del eje desde la brida | Motor NEMA 23 |
   | Largo total y largo del cubo | Polea de 20 dientes |
   | Lado y alto | Rodamiento *lazy susan* |
   | Largo, ancho sin borneras, alto y cuánto sobresalen las borneras | TB6600 |
   | Lado y distancia entre agujeros | Placa del AS5600 |
   | Largo del cable de la antena | GPS |
   | Largo del cable del motor | NEMA 23 |

### Semanas 2 a 5

5. Imprimir **primero** `prueba_gt2.stl` y probar la correa. Recién después, el resto.
6. Armar y cablear siguiendo [`circuito/LEEME.md`](../circuito/LEEME.md) §6.
7. **Ejecutar la prueba de banco de 11 pasos** y mandarme el resultado de cada una.
8. Armado mecánico y balanceo, siguiendo `montura/LEEME.md` §7.

### Semanas 6 a 11

9. **Las noches.** Mínimo 6, objetivo 8. Incluye sesiones con la **Luna de día**, que no
   dependen del clima nocturno.
10. Protocolo fijo en cada sesión: nivelar, encender, leer el desnivel, alineación de 2 o 3
    puntos, y recién entonces registrar.

### En paralelo, desde ya

11. Leer **He et al. (2026, FinalKAN)** y **Bergerhoff (2024, EUSIPCO)**.
12. Repasar la Introducción: una cita por párrafo y frases cortas. Son los ítems 6 y 7 y no
    dependen de nada.
13. Crear el **ORCID** (gratis, orcid.org). Lo pide la revista.

---

## 6. Qué necesito para empezar hoy

**Nada.** Esa es la respuesta corta, y es a propósito.

El modelo de error y el simulador se escriben con lo que ya está decidido: el sitio
(Portoviejo), las reducciones (14:1 y 5:1), los micropasos (16) y la geometría de la montura
que está en `montura/`. El umbral de error objetivo queda como parámetro hasta que decidas la
cámara.

Lo único que sí te pido antes de que yo escriba código, porque es la regla del repositorio: el
visto bueno de los puntos 1 a 4 de §4, que son los que generan los datos del artículo.

---

## 7. Cómo verás que avanza

Cada módulo se entrega con pruebas automáticas que puedes correr en tu PC sin hardware:

```bash
cd prototipo && python -m pytest
```

Y el simulador producirá, desde la semana 2, un CSV con noches sintéticas que puedes abrir en
Excel. Desde la semana 4 vas a poder ver **las figuras del artículo ya dibujadas** con datos
simulados: las mismas que después se van a rellenar con los datos reales. Eso te deja enseñarle
avances concretos al tutor mucho antes de tener la montura armada.

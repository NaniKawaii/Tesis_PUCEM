# Memoria del artículo · decisiones vigentes

Este archivo junta **todo lo que Nashla ha decidido y pedido** sobre el artículo (enfoque,
hardware, IA, bibliografía). Lo vigente va arriba; el historial, con fechas absolutas, va al
final. Cada conversación que cambie algo relevante actualiza este archivo mediante un PR.

> Regla del repositorio: los resultados del artículo salen **solo de mediciones reales**.
> Nada de valores estimados, ni siquiera provisionales.

## Versión vigente (2026-11-06)

**Qué es:** un artículo científico (no tesis) para la revista *Esprint Investigación*.
Autora: Nashla Carolina Tuma Zambrano, Ingeniería de Software, PUCE Sede Manabí.
Tutor: Ing. Diego Paul Corrales Vargas, Mg.

**Título vigente** (lo cambió Nashla el 2026-11-04 en el Google Doc v2.1):
"Sistema inteligente de posicionamiento y seguimiento de objetos celestes mediante
aprendizaje automático e interfaz de control web".
Alternativa sugerida, más precisa: "Comparación de modelos de aprendizaje automático para el
seguimiento lunar con una montura de bajo costo controlada por web".

**Enfoque:** un prototipo de montura altacimutal motorizada que lleva una **cámara** (ya no un
telescopio) en una barra Vixen, se controla desde una **aplicación web** y **sigue a la Luna**
desde Portoviejo, Ecuador (~1° S). La IA cumple tres papeles en cadena y en cada uno se
comparan tres modelos. El eje original del artículo es comparar **tres formas de entrenar** la IA.

**Documentos de referencia:**
- Diseño de investigación completo: https://claude.ai/artifact/4XbEmnoXNMFJLUJhT8dVS1
- Bibliografía Scopus (24 referencias + cadenas de búsqueda): https://claude.ai/artifact/FEWEZ6H28HfpPHiWjPHY2t
- Carpeta de Drive de la tesis (Artículo v1, v2, v2.1 con telescopio): https://drive.google.com/drive/folders/1K1phWblEYKiIeQ4W515I4zOXwpfBdLNP

### Pendientes abiertos

1. Confirmar el diseño de investigación completo (el papel de la IA ya está confirmado).
2. Comprar la Sony ZV-E10 II + Tamron 17-70 y la capturadora HDMI; probar el Sony Camera
   Remote SDK (pedir la descarga a Sony) o gphoto2.
3. Agregar al software: captura de cámara, registrador del dataset y los módulos M1, M2 y M3.
4. Generar un dataset sintético para probar el pipeline antes de las noches reales.
5. Actualizar el Artículo v2.1 con la nueva metodología (cámara, 3 papeles, 3 formas de entrenar).
6. Buscar en Scopus con la cuenta de la PUCE y confirmar las referencias marcadas "verificar".

> No escribir código nuevo sin el OK de Nashla.

## Telescopio → cámara (qué cambia respecto de las versiones en Drive)

Las versiones v1, v2 y v2.1 se **adaptan, no se tiran**: montura, electrónica, software y la
mitad de las referencias siguen valiendo.

| Aspecto | Antes (telescopio) | Ahora (cámara) |
|---|---|---|
| Instrumento | Telescopio de hasta 3 kg con ocular | Cámara de foto/video en la barra Vixen (rosca 1/4″) |
| Medición del error | El usuario centra el objeto con botones | La cámara detecta la Luna en cada fotograma |
| Tarea | Apuntado (GoTo) a planetas | Apuntado y seguimiento continuo; caso de estudio la Luna |
| Datos | ≥ 30 apuntados manuales | Miles de fotogramas por noche; dataset publicado en Zenodo |
| IA | Ridge frente a MLP | 3 módulos × 3 modelos + 3 formas de entrenar |
| Estadística | Wilcoxon | Friedman + Nemenyi por módulo |
| Usuarios (E3, E4) | Centrales | Secundarios u opcionales |

## La IA: tres papeles en cadena (confirmado 2026-11-06)

Un ciclo por segundo: **M1 detecta → M2 predice → M3 corrige → la montura se mueve.**

| Módulo | Línea base clásica | Modelo IA 1 | Modelo IA 2 | Qué se mide |
|---|---|---|---|---|
| **M1 Detección** (centro de la Luna en la imagen) | Umbral + círculo de Hough (OpenCV); plate solving con ASTAP para estrellas | YOLOv8n (Ultralytics) | CNN ligera (MobileNetV3, PyTorch) | Error del centro en px y en ′, % sin detección, fps en la Pi |
| **M2 Trayectoria** (solo con lo que ve la cámara) | Filtro de Kalman (filterpy) | LightGBM | LSTM (PyTorch) | Error a 10 s y 60 s frente a Skyfield |
| **M3 Corrección** del error de la montura | Ridge con términos trigonométricos | LightGBM | LSTM | Error RMS de seguimiento en ′ |

- **Lazo cerrado / servocontrol visual:** M1 ve dónde está la Luna en el video y la montura
  se ajusta hasta centrarla. Se comparan 3 modos: solo efemérides, efemérides + M3, y
  efemérides + M3 + corrección visual con M1.
- **Skyfield calcula la posición**; la IA no la calcula, corrige el error. Para M2, Skyfield
  es la respuesta correcta contra la que se califica (M2 sirve para objetos sin efemérides).
- **Plate solving (ASTAP / astrometry.net)** es el método clásico de referencia y calibra la
  montura al iniciar la noche.
- Un clasificador simple descarta fotogramas con nubes o mala calidad (parte de M1).
- Hipótesis H1–H4: detector aprendido mejor que Hough en fases delgadas/nubes; LightGBM o
  LSTM mejor que Kalman; los 3 correctores reducen el error y los no lineales más que Ridge;
  con M1 + M3 la Luna pasa más tiempo centrada que sin IA.

## Tres formas de entrenar la IA (eje del artículo, pedido 2026-11-06)

| Forma | Cómo | Datos | Librerías |
|---|---|---|---|
| **A. Supervisado con datos reales** | Grabar noches, etiquetado automático (efemérides + cámara), entrenar en PC | 8–10 noches reales | scikit-learn, LightGBM, PyTorch |
| **B. Simulación + ajuste fino** (sim-to-real) | Entrenar con datos sintéticos (Skyfield + simulador de montura con errores + Lunas renderizadas) y ajustar con pocas noches reales | Simulación + 2–3 noches reales | Skyfield, OpenCV, PyTorch |
| **C. Aprendizaje por refuerzo** | Un agente mueve los motores y recibe premio cuando la Luna queda centrada; primero en simulador, luego real | Simulador + sesiones reales | Gymnasium, Stable-Baselines3 (PPO) |

Respaldo si C no converge: aprendizaje en línea con **River**. Las tres se califican igual
(error en ′ y % del tiempo con la Luna centrada, sobre noches no vistas) y se reporta cuántas
noches reales necesitó cada una.

## Hardware vigente

| Parte | Qué | Estado |
|---|---|---|
| Cámara principal y sensor | **Sony ZV-E10 II** (APS-C, 26 MP) | Elegida, por comprar |
| Lente | **Tamron 17-70 mm f/2.8 (B070S)**; a 70 mm la Luna ocupa ~160 px | Elegido, por comprar |
| Video en vivo a la Pi | **Capturadora HDMI → USB**, leída con OpenCV | Por comprar (~15–25 USD) |
| Disparo de fotos | Sony Camera Remote SDK para Linux ARM (pedir a Sony) o gphoto2 | Por probar |
| Montura | Altacimutal impresa en PETG, reducciones 14:1 (az) y 5:1 (alt), **barra Vixen** | Diseñada ([`montura/`](montura/LEEME.md)) |
| Motores y drivers | **2 NEMA 23 + 2 TB6600** a 16 micropasos | **Comprados** |
| Control | **Raspberry Pi 4 (2 GB)**: efemérides, web, video, inferencia | Comprada |
| Sensores | GPS NEO-6M, GY-91, AS5600, fines de carrera | Comprados / en proforma |
| Energía | LiFePO4 12,8 V 12 Ah + step-down 5,1 V | Comprada / en proforma |
| Respaldo de medición | Raspberry Pi HQ Camera o Camera Module 3 | Opcional |

- **No comprar** NEMA 17 + TMC2209 + reducción 1:100 (lo proponía otro chat): ya hay NEMA 23 +
  TB6600 y la montura está diseñada para ellos.
- Pico/Arduino para los pulsos: solo si la prueba de banco muestra tirones.
- Lentes gran angular (Viltrox 13 mm, Sigma 16 mm): no hacen falta para el artículo.
- Precios de la Sony + Tamron (~1 700 USD) **sin verificar**.

## Dataset, experimentos y estadística

- Una fila por fotograma (1 por segundo): tiempo, posición de Skyfield, pasos y ángulos de la
  montura, inclinación, ambiente y error medido (Δaz·cos(alt), Δalt). ~20 000 filas por noche.
- Imágenes para M1: 1 cada 10 s, etiquetadas con ajuste de círculo; ~300 revisadas a mano.
  Las imágenes van a **Zenodo con DOI**, no a este repositorio.
- **Separar entrenamiento y prueba por noche, no por fila.**
- Experimentos: E1 error sin IA, E2 detectores, E3 predictores, E4 correctores, E5 sistema
  completo en vivo, E6 generalización a Júpiter/Venus (opcional).
- Estadística: Friedman + Nemenyi (o Wilcoxon con Holm) por módulo; Wilcoxon pareado en E5;
  IC 95 % por bootstrap agrupado por noche; tamaño del efecto.

## Bibliografía

24 referencias con DOI verificado en Crossref, en 6 grupos (IA para corregir el apuntado,
servocontrol visual, detección de la Luna, formas de entrenar, método clásico y física lunar,
modelos y estadística) y 7 cadenas `TITLE-ABS-KEY` para Scopus. Detalle en el documento:
https://claude.ai/artifact/FEWEZ6H28HfpPHiWjPHY2t

Las más cercanas al aporte: Zhaborovskyy et al. (2024, *Artificial Satellites*), Mu et al.
(2026, *RAA*), Chichura et al. (2025, South Pole Telescope), Ghiasvand et al. (2024,
*Frontiers in Robotics and AI*), Nousiainen et al. (2022, *A&A*, refuerzo) y Tobin et al.
(2017, domain randomization). LightGBM, PPO y Nemenyi/Demšar no tienen DOI.
No hay acceso directo a Scopus: Nashla entra con la cuenta de la PUCE.

## Historial

- **2026-11-04:** Nashla cambia el título del Artículo v2.1 en Drive.
- **2026-11-06:** nuevo enfoque: cámara en la montura en vez de telescopio, app web, seguir la
  Luna desde Ecuador y comparar varios modelos de IA.
- **2026-11-06:** se propone que la IA corrija el error de la montura (Ridge / LightGBM /
  LSTM). Nashla confirma que la IA cumple **los tres papeles**: detectar, predecir y corregir.
- **2026-11-06:** pide comparar **tres formas de entrenar** (A supervisado, B simulación +
  ajuste fino, C refuerzo); se recomienda como eje del artículo.
- **2026-11-06:** se integra el equipo de otro chat: Sony ZV-E10 II + Tamron 17-70,
  capturadora HDMI, plate solving como referencia; se descarta cambiar los motores.
- **2026-11-06:** se entrega la bibliografía Scopus (24 referencias verificadas).

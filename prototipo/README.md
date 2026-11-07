# Prototipo · software del telescopio automatizado (v0.1)

Software que corre en la **Raspberry Pi 4**. Calcula la posición de los planetas, mueve la
montura altacimutal con los drivers TB6600, sirve la interfaz web y registra cada apuntado
para medir la precisión y entrenar la corrección por IA.

Funciona también en una PC en **modo simulación**, sin hardware, para avanzar mientras se
arma la parte mecánica.

![Interfaz web](../docs/img/interfaz-web-v0.1.png)

## Arquitectura

```
Navegador (PC / celular)  ──HTTP──▶  servidor.py (FastAPI)
                                          │
                                     sistema.py  ── orquesta el flujo GoTo → centrado → registro
              ┌──────────────┬───────────┼─────────────┬──────────────┐
          astro.py       montura.py  correccion.py   registro.py     gps.py
       (Skyfield, DE421)  (ángulos ↔ pasos,  (IA de la v0.1,   (CSV: apuntados  (NEO-6M,
                           límites)        ver la tabla)     y seguimiento)   NMEA)

  Aparte del lazo de control, el pipeline del artículo:
      errores.py  ──▶  simulador.py  ──▶  aprendizaje.py  ──▶  analisis/
     (modelo del      (noches           (alineación,          (tablas del
      error)           sintéticas)       modelos, estadística)  artículo)
                              │
                         motores.py  ── rampa de aceleración, MotorSimulado / MotorTB6600 (GPIO)
```

| Módulo | Qué hace |
|---|---|
| `config.py` | Sitio (por defecto, Portoviejo), parámetros de cada eje (micropasos, reducción, pines, límites) |
| `astro.py` | Altitud y azimut aparentes de Mercurio, Venus, la Luna, Marte, Júpiter, Saturno, Urano y Neptuno |
| `motores.py` | Perfil trapezoidal de velocidad para no perder pasos; pulsos STEP/DIR/ENA; fines de carrera |
| `montura.py` | Conversión de grados a pasos, camino más corto en azimut, límites mecánicos, movimiento simultáneo de los 2 ejes |
| `correccion.py` | IA de la **v0.1**, todavía usada por `sistema.py` y `servidor.py`. Parte las filas al azar, que para datos por segundo infla el resultado: **no usar para el artículo**. Se retira cuando la interfaz migre a `aprendizaje.py` |
| `errores.py` | El modelo de error paramétrico, **compartido**: el simulador lo usa para generar el error y la alineación para ajustarlo. Una sola definición de los términos |
| `simulador.py` | Aleatorización de dominio: muestrea monturas sintéticas y genera noches, con efectos **no lineales** que el modelo clásico no puede representar |
| `aprendizaje.py` | **El pipeline del artículo**: alineación por sesión, modelo clásico, Ridge / boosting / MLP sobre el residuo, validación dejando una noche fuera, Friedman + Nemenyi y Wilcoxon |
| `analisis/` | Los experimentos que producen las tablas del artículo. Ver [`analisis/LEEME.md`](analisis/LEEME.md) |
| `registro.py` | CSV `datos/registro_apuntado.csv`: los datos crudos para el artículo |
| `gps.py` | Ubicación y hora desde el GPS (la Raspberry Pi no tiene reloj con batería) |
| `sistema.py` | Flujo completo: GoTo, ajuste fino, confirmación del centrado, seguimiento, entrenamiento de la IA |
| `servidor.py` + `static/index.html` | API REST e interfaz web accesible (botones grandes, `aria-live`, adaptada a celular) |

## Uso en una PC (simulación)

```bash
cd prototipo
python3 -m venv .venv && source .venv/bin/activate     # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m telescopio.servidor                            # abrir http://localhost:8000
```

La primera vez se descargan las efemérides `de421.bsp` (~17 MB) en `datos/`.

Pasos en la interfaz: **Referenciar** → elegir un planeta visible → **Apuntar** → centrar con
las flechas → **Objeto centrado (registrar)**. Con 10 registros o más se puede **entrenar la IA**.

## Uso en la Raspberry Pi

1. Copiar `config.ejemplo.json` a `config.json` y ajustar los pines, los micropasos (según los
   switches del TB6600) y la **reducción** de la transmisión.
2. Activar el puerto serie para el GPS (`raspi-config` → Interface → Serial: login shell
   **no**, hardware **sí**).
3. Ejecutar `python -m telescopio.servidor --config config.json`.
4. Desde cualquier dispositivo de la misma red, abrir `http://<ip-de-la-pi>:8000`.

### Conexiones previstas (BCM)

| Señal | Eje azimut | Eje altitud |
|---|---|---|
| PUL+ (STEP) | GPIO 17 | GPIO 23 |
| DIR+ | GPIO 27 | GPIO 24 |
| ENA+ | GPIO 22 | GPIO 25 |
| Fin de carrera (a GND) | — (límite por software ±270°) | GPIO 6 (2 interruptores en paralelo: −5° y 90°) |
| PUL− / DIR− / ENA− | GND | GND |

GPS NEO-6M: TX → GPIO 15 (RXD), RX → GPIO 14 (TXD), VCC 5 V, GND.
Alimentación: batería LiFePO4 de 12,8 V → TB6600 y *step-down* de 5,1 V → Raspberry Pi (ver `docs/03-telescopio-montura-energia.md`). Configurar los TB6600 en 16 micropasos y 1,5 A.

## Pruebas automáticas

```bash
python -m pytest
```

Las pruebas cubren el perfil de velocidad, la cinemática, los límites, los fines de carrera,
la IA con datos sintéticos, la API y un flujo completo simulado (15 apuntados, entrenamiento
y GoTo corregido).

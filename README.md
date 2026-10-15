# Tesis PUCEM · Sistema de posicionamiento telescópico con IA y control web

**Autora:** Nashla Carolina Tuma Zambrano · Ingeniería de Software, PUCE Sede Manabí
**Tutor:** Ing. Diego Paul Corrales Vargas, Mg.
**Modalidad:** publicación de un artículo científico (revista *Esprint Investigación*).

## Contenido

| Carpeta | Qué hay |
|---|---|
| [`docs/01-diagnostico-articulo.md`](docs/01-diagnostico-articulo.md) | Revisión del borrador frente a la guía de la revista, verificación de referencias, observaciones sobre el hardware, propuesta de IA y diseño experimental |
| [`docs/02-componentes.md`](docs/02-componentes.md) | Revisión de los componentes comprados (factura): qué sirve, qué no y qué falta comprar |
| [`docs/03-telescopio-montura-energia.md`](docs/03-telescopio-montura-energia.md) | Telescopio recomendado, diseño de la montura, baterías para campo y lista de compras definitiva |
| [`montura/`](montura/LEEME.md) | **Piezas imprimibles en 3D** de la montura universal (OpenSCAD paramétrico + STL), guía de impresión y armado |
| [`prototipo/`](prototipo/README.md) | Software del prototipo: cálculo de planetas, control de motores, interfaz web, registro de pruebas y corrección por IA |

Los documentos originales (borrador, plan, guía de la revista, proforma) están en el Drive.

## Hoja de ruta

Vamos paso a paso. ✅ = hecho en este repositorio.

1. ✅ **Diagnóstico** del artículo, de las referencias y de la proforma.
2. ✅ **Software del prototipo v0.1** en modo simulación: GoTo, interfaz web, registro de
   apuntados y corrección por IA (lineal frente a red neuronal), con 29 pruebas automáticas.
3. ✅ **Decidir el hardware final:** revisión de la factura ([docs/02](docs/02-componentes.md))
   y decisiones de telescopio, montura y baterías ([docs/03](docs/03-telescopio-montura-energia.md)).
   Pendiente: **comprar** según la lista definitiva y revisar tu diseño 3D actual.
4. ⬜ **Armar la electrónica** y probar los motores en banco, con la Raspberry Pi y
   `config.json`.
5. 🟡 **Montura impresa en 3D:** piezas diseñadas y verificadas sin interferencias
   ([montura/](montura/LEEME.md)). Pendiente: imprimir la pieza de prueba GT2, imprimir todo y armar.
6. ⬜ **Noches de prueba (E1, E2):** ≥ 30 apuntados registrados y entrenamiento y evaluación de la IA.
7. ⬜ **Pruebas con usuarios (E3, E4):** 20 participantes, tiempos y cuestionario SUS.
   Script de análisis estadístico.
8. ⬜ **Reescribir el artículo** con los datos reales: resumen ≤ 250 palabras con valores
   de p, tercera persona, figura de metodología, referencias verificadas, APA 7 en orden alfabético.
9. ⬜ Traducción del abstract, ORCID, CRediT, maquetación según la plantilla y envío.

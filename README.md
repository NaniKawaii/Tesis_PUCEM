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
| [`docs/04-plan-de-trabajo.md`](docs/04-plan-de-trabajo.md) | **Plan paso a paso** (compras → impresión → circuito → software → pruebas → artículo) y cómo funciona el software (Raspberry Pi + web) |
| [`docs/05-lista-para-proveedor.md`](docs/05-lista-para-proveedor.md) | **Lista de compras para el proveedor**: solo lo que falta, con especificaciones y cantidades |
| [`docs/06-revision-proforma.md`](docs/06-revision-proforma.md) | **Revisión de la proforma de Megatrónica**: qué comprar, qué cambiar, qué no comprar y qué falta |
| [`articulo/`](articulo/LEEME.md) | **Artículo científico v2** en Word con el formato de la revista Esprint |
| [`circuito/`](circuito/LEEME.md) | **Esquema de conexiones**, tabla pin por pin, configuración de los TB6600, prueba de banco paso a paso y **plano de cableado dentro de la caja** |
| [`montura/`](montura/LEEME.md) | **Piezas imprimibles en 3D** de la montura universal (OpenSCAD paramétrico + STL), guía de impresión y armado |
| [`prototipo/`](prototipo/README.md) | Software del prototipo: cálculo de planetas, control de motores, interfaz web, registro de pruebas y corrección por IA |

**En Google Drive** (carpeta de la tesis):
- **"Artículo científico – versiones"**: la v1 (borrador original), la v2 y la v2.1
  (Google Docs editables, con figuras; la v2.1 agrega la caja de control). El Word más reciente,
  con las ecuaciones del editor, está en `articulo/articulo_v2.docx`.
- **"Documentos del prototipo"**: el plan de trabajo, la guía del circuito, la guía de la
  montura y la lista de compras, como Google Docs.

El código, los STL y los scripts viven en este repositorio. Los Google Docs son copias
de trabajo: si se edita uno, conviene avisar para sincronizar la versión del repositorio.

## Hoja de ruta

Vamos paso a paso. ✅ = hecho en este repositorio.

1. ✅ **Diagnóstico** del artículo, de las referencias y de la proforma.
2. ✅ **Software del prototipo v0.1** en modo simulación: GoTo, interfaz web, registro de
   apuntados y corrección por IA (lineal frente a red neuronal), con 37 pruebas automáticas.
3. ✅ **Decidir el hardware final:** revisión de la factura ([docs/02](docs/02-componentes.md))
   y decisiones de telescopio, montura y baterías ([docs/03](docs/03-telescopio-montura-energia.md)).
   Pendiente: **comprar** según la lista definitiva y revisar tu diseño 3D actual.
4. 🟡 **Electrónica:** esquema de conexiones y programa de prueba de banco listos
   ([circuito/](circuito/LEEME.md)). Pendiente: armar y ejecutar las 11 pruebas.
5. 🟡 **Montura impresa en 3D:** piezas diseñadas y verificadas sin interferencias
   ([montura/](montura/LEEME.md)). Pendiente: imprimir la pieza de prueba GT2, imprimir todo y armar.
6. ⬜ **Noches de prueba (E1, E2):** ≥ 30 apuntados registrados y entrenamiento y evaluación de la IA.
7. ⬜ **Pruebas con usuarios (E3, E4):** 20 participantes, tiempos y cuestionario SUS.
   Script de análisis estadístico.
8. 🟡 **Artículo:** versión 2 reescrita con el formato de la revista y 15 referencias
   verificadas ([articulo/](articulo/LEEME.md)). Pendiente: completar los `[[ ]]` con los datos de las pruebas.
9. ⬜ Traducción del abstract, ORCID, CRediT, maquetación según la plantilla y envío.

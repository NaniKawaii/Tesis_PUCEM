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
| [`docs/07-rubrica-lector.md`](docs/07-rubrica-lector.md) | **La rúbrica del lector**: cómo se calcula la nota (máximo 30 puntos), dónde está el peso y qué debe decir cada sección para que el ítem salga "Sí" |
| [`docs/08-diseno-definitivo.md`](docs/08-diseno-definitivo.md) | ⭐ **Diseño definitivo del artículo**: el aporte, la brecha confirmada en Scopus, la arquitectura de la IA, el simulador, los experimentos, la estadística y el cronograma de 15 semanas |
| [`docs/09-manos-a-la-obra.md`](docs/09-manos-a-la-obra.md) | ⭐ **Quién hace qué y en qué orden**: los tres frentes en paralelo, los módulos de software por escribir, tus pasos semana a semana y las medidas que hacen falta |
| [`MEMORIA.md`](MEMORIA.md) | **Decisiones vigentes** del artículo, con su historial fechado |
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
6. ✅ **Rúbrica y enfoque definitivo:** la nota del manuscrito sale de la rúbrica del lector
   ([docs/07](docs/07-rubrica-lector.md)) y el aporte del artículo quedó fijado el 06/11/2026
   ([docs/08](docs/08-diseno-definitivo.md)): **pre-entrenar en simulación con aleatorización de
   dominio para reducir las noches reales necesarias.** Brecha confirmada en Scopus.
7. ⬜ **Simulador de montura** con aleatorización de dominio y pipeline de ML sobre datos
   sintéticos. **No depende del hardware: es lo primero que se escribe.**
8. ⬜ **Captura de cámara, registrador del dataset** y ajuste fino del detector lunar.
9. ⬜ **Observación: mínimo 6 noches, objetivo 8** (incluidas sesiones con la Luna de día, para
   no depender del clima nocturno). Experimentos E1–E5 y análisis estadístico.
10. 🟡 **Artículo:** la versión 2 está reescrita con el formato de la revista
    ([articulo/](articulo/LEEME.md)), pero hay que **rehacer objetivos, metodología e hipótesis**
    según [docs/08](docs/08-diseno-definitivo.md). Los `[[ ]]` se completan solo con datos medidos.
11. ⬜ Traducción del abstract, ORCID, CRediT, maquetación según la plantilla y envío.

> ⏳ **Plazo: 15 semanas desde el 06/11/2026** (≈ 19/02/2027). Hito de no retorno: si la montura
> no mide al final de la semana 5, se activa el plan B de [docs/08](docs/08-diseno-definitivo.md#plan-b-si-el-hardware-se-atrasa).

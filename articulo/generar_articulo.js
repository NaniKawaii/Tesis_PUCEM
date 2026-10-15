// Genera el artículo en Word con el formato de la revista Esprint Investigación.
// Uso: node generar_articulo.js   →   articulo_v2.docx
//
// Convención de edición: el texto entre [[ ]] es un dato pendiente. Se resalta en
// amarillo en el Word y SOLO debe reemplazarse con datos medidos en las pruebas.

const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell, Footer,
  AlignmentType, WidthType, BorderStyle, LineRuleType, PageNumber, TabStopType, LevelFormat,
  Math: OMath, MathRun, MathFraction, MathRadical, MathSuperScript, MathSubScript,
} = require("docx");

const FUENTE = "Times New Roman";
const TAM = 24; // 12 pt
const ANCHO_TEXTO = 9072; // A4 (11906) − 2 × 2,5 cm (1417)
const FIG = path.join(__dirname, "figuras");

// ----------------------------------------------------------------- texto
// Admite [[pendiente]] (resaltado) y _cursiva_ dentro de un párrafo.
function runs(texto, base = {}) {
  return texto.split(/(\[\[.*?\]\]|_[^_]+_)/).filter(Boolean).map((t) => {
    if (t.startsWith("[[")) return new TextRun({ ...base, text: t, highlight: "yellow" });
    if (t.startsWith("_") && t.endsWith("_")) return new TextRun({ ...base, text: t.slice(1, -1), italics: true });
    return new TextRun({ ...base, text: t });
  });
}
const P = (texto, op = {}) => new Paragraph({ alignment: AlignmentType.JUSTIFIED, children: runs(texto, op.run), ...op.par });
const centro = (texto, run = {}) => new Paragraph({ alignment: AlignmentType.CENTER, children: runs(texto, run) });
const H1 = (texto) => new Paragraph({ spacing: { before: 240, after: 120 }, keepNext: true, children: [new TextRun({ text: texto, bold: true })] });
const H2 = (texto) => new Paragraph({ spacing: { before: 120, after: 60 }, keepNext: true, children: [new TextRun({ text: texto, bold: true, italics: true })] });
const vineta = (texto) => new Paragraph({ alignment: AlignmentType.JUSTIFIED, numbering: { reference: "vinetas", level: 0 }, children: runs(texto) });
const nota = (texto) => new Paragraph({ alignment: AlignmentType.JUSTIFIED, spacing: { after: 200 }, children: [new TextRun({ text: "Nota: ", italics: true, size: 20 }), ...runs(texto, { size: 20 })] });
const rotulo = (tipo, n, texto) => new Paragraph({ keepNext: true, spacing: { before: 200 }, children: [new TextRun({ text: `${tipo} ${n}. `, bold: true }), ...runs(texto, { italics: true })] });

function figura(n, archivo, titulo, notaTexto, anchoCm) {
  const buf = fs.readFileSync(path.join(FIG, archivo));
  const ancho = buf.readUInt32BE(16), alto = buf.readUInt32BE(20); // cabecera PNG
  const px = Math.round(anchoCm / 2.54 * 96);
  return [
    rotulo("Figura", n, titulo),
    new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, children: [new ImageRun({ type: "png", data: buf, transformation: { width: px, height: Math.round(px * alto / ancho) } })] }),
    nota(notaTexto),
  ];
}

// Tabla con bordes solo arriba, abajo y bajo el encabezado (estilo de la revista)
function tabla(n, titulo, filas, anchos, notaTexto) {
  const total = anchos.reduce((a, b) => a + b, 0);
  const ninguno = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
  const linea = { style: BorderStyle.SINGLE, size: 8, color: "000000" };
  const t = new Table({
    width: { size: total, type: WidthType.DXA },
    columnWidths: anchos,
    borders: { top: linea, bottom: linea, left: ninguno, right: ninguno, insideHorizontal: ninguno, insideVertical: ninguno },
    rows: filas.map((fila, i) => new TableRow({
      tableHeader: i === 0,
      children: fila.map((celda, j) => new TableCell({
        width: { size: anchos[j], type: WidthType.DXA },
        borders: i === 0 ? { bottom: linea } : {},
        margins: { top: 40, bottom: 40, left: 80, right: 80 },
        children: [new Paragraph({ spacing: { line: 240 }, alignment: j === 0 ? AlignmentType.LEFT : AlignmentType.CENTER,
          children: runs(celda, { size: 20, bold: i === 0 }) })],
      })),
    })),
  });
  return [rotulo("Tabla", n, titulo), t, nota(notaTexto)];
}

// Ecuación centrada con su número a la derecha
function ecuacion(n, partes) {
  return new Paragraph({
    tabStops: [{ type: TabStopType.CENTER, position: ANCHO_TEXTO / 2 }, { type: TabStopType.RIGHT, position: ANCHO_TEXTO }],
    children: [new TextRun("\t"), new OMath({ children: partes }), new TextRun(`\t(${n})`)],
  });
}
const M = (t) => new MathRun(t);

// ----------------------------------------------------------------- contenido
const cuerpo = [];
const add = (...x) => x.flat().forEach((e) => cuerpo.push(e));

add(
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 }, children: [new TextRun({ text: "Sistema de posicionamiento telescópico con corrección de apuntado mediante aprendizaje automático y control web", bold: true, size: 28 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 240 }, children: [new TextRun({ text: "Telescope positioning system with machine-learning pointing correction and web-based control", italics: true })] }),
  centro("Nashla Carolina Tuma Zambrano¹*, [[Diego Paul Corrales Vargas² — confirmar coautoría del tutor]]"),
  centro("¹ Pontificia Universidad Católica del Ecuador, Sede Manabí, Facultad de Ingeniería, Portoviejo, Ecuador, 130107", { size: 20 }),
  centro("² [[Filiación del tutor: institución, ciudad, país, código postal]]", { size: 20 }),
  centro("ntuma6749@pucesm.edu.ec, ORCID: [[0000-0000-0000-0000]]", { size: 20 }),
  centro("[[correo institucional del tutor]], ORCID: [[0000-0000-0000-0000]]", { size: 20 }),
  centro("*Correspondencia: ntuma6749@pucesm.edu.ec", { size: 20 }),
  new Paragraph({ spacing: { before: 200 }, children: [new TextRun({ text: "Tipo de contribución: ", bold: true }), new TextRun("Artículo de investigación")] }),
);

const RESUMEN = "La observación con telescopios convencionales exige localizar los objetos de forma manual, una barrera técnica que limita su uso en la educación y el astroturismo. El objetivo de este trabajo fue diseñar, construir y evaluar un sistema de posicionamiento telescópico de bajo costo que corrige su error de apuntado mediante aprendizaje automático y se controla desde una interfaz web. Se construyó una montura altacimutal impresa en 3D, compatible con telescopios de hasta 3 kg con cola de milano Vixen, accionada por motores paso a paso con reducciones de 14:1 y 5:1 y controlada por una Raspberry Pi 4 que calcula efemérides planetarias en tiempo real. En cada apuntado se registró el ajuste manual necesario para centrar el objeto, y con esos datos se entrenaron un modelo lineal y una red neuronal multicapa que predicen el error sistemático de la montura. Se evaluaron [[N]] apuntados mediante validación cruzada y la prueba de Wilcoxon, y la usabilidad con 20 participantes mediante la escala SUS. El error cuadrático medio de apuntado sin corrección fue de [[X]]′ y se redujo a [[Y]]′ con la corrección por [[modelo]] ([[Z]] %; p = [[valor]]). El tiempo para localizar un planeta disminuyó de [[A]] s con búsqueda manual a [[B]] s con el sistema (p = [[valor]]), y la interfaz obtuvo un puntaje SUS de [[S]]. Se concluye que [[conclusión principal sustentada en los datos]].";
add(
  new Paragraph({ alignment: AlignmentType.JUSTIFIED, spacing: { before: 200 }, children: [new TextRun({ text: "Resumen: ", bold: true }), ...runs(RESUMEN)] }),
  new Paragraph({ alignment: AlignmentType.JUSTIFIED, children: [new TextRun({ text: "Palabras clave: ", bold: true }), new TextRun("aprendizaje automático, astroturismo, control web, montura altacimutal, posicionamiento telescópico.")] }),
  new Paragraph({ alignment: AlignmentType.JUSTIFIED, spacing: { before: 200 }, children: [new TextRun({ text: "Abstract: ", bold: true }), ...runs("[[Traducir al inglés el resumen final, una vez completados los datos.]]")] }),
  new Paragraph({ alignment: AlignmentType.JUSTIFIED, children: [new TextRun({ text: "Keywords: ", bold: true }), new TextRun("alt-azimuth mount, astrotourism, machine learning, telescope positioning, web-based control.")] }),
);

// ---------------------------------------------------------------- 1. Introducción
add(H1("1. Introducción"),
  P("La observación del cielo con un telescopio es una de las experiencias con mayor capacidad para despertar el interés por la ciencia. Sin embargo, en los telescopios convencionales el usuario debe localizar cada objeto de forma manual: necesita conocer sus coordenadas, orientarse en el cielo y compensar el movimiento aparente que produce la rotación de la Tierra. Esta barrera técnica restringe el uso de los telescopios en aulas, clubes de astronomía y actividades de divulgación. En la región andina el problema adquiere además una dimensión económica, porque el astroturismo se ha consolidado como una actividad emergente vinculada al desarrollo local: en 2023 se conformó en Quito la primera red andina de emprendedores en astroturismo (Pinzón et al., en prensa), en Ecuador se han diseñado productos astroturísticos para áreas protegidas (Casanova Imbaquingo et al., 2024) y en Brasil el astroturismo se ha descrito como una forma de turismo de experiencia asociada al ecoturismo (Mello, 2023)."),
  P("Los telescopios con apuntado automático (sistemas _GoTo_) resuelven la localización, pero las soluciones comerciales son cerradas y su costo es elevado para instituciones educativas. Como alternativa han surgido proyectos de hardware y software abierto, como el controlador OnStep (Dutton, s. f.) o los equipos impresos en 3D de OpenAstroTech (OpenAstroTech, s. f.), y estudios que caracterizan monturas construidas con componentes de bajo costo. Barends et al. (2025) evaluaron una montura robótica altacimutal hecha con perfiles de aluminio y reductores impresos en 3D, y reportaron errores medios de apuntado de aproximadamente 1,6° en azimut y 0,415° en altitud. Estos valores, mayores que el campo visual de un ocular de bajo aumento, muestran que la precisión sigue siendo la principal limitación de las monturas de bajo costo. En el control de los motores paso a paso, Fonseca-Campos et al. (2023) demostraron que los perfiles de velocidad necesarios para un movimiento suave pueden generarse en microcontroladores comunes, sin hardware especializado."),
  P("En paralelo, las interfaces web han simplificado la operación remota de telescopios. Ricci et al. (2024) describieron el control de un telescopio de 1 m en Italia desde un navegador, lo que permitió que estudiantes de bachillerato en Japón realizaran observaciones sin instalar software especializado. Por otra parte, el aprendizaje automático comenzó a aplicarse a la corrección del apuntado en telescopios profesionales: Zariski et al. (2024) reemplazaron el modelo de apuntado físico tradicional del telescopio WIYN de 3,5 m por una combinación de una red neuronal recurrente y árboles de gradiente, y Chichura et al. (2025) entrenaron modelos XGBoost que redujeron en un 33 % el error combinado de apuntado del South Pole Telescope, de 15,9″ a 10,6″."),
  P("Estos antecedentes revelan una brecha: la corrección del apuntado mediante aprendizaje automático se ha estudiado en instrumentos profesionales de alta precisión, pero en la literatura revisada no se encontraron evaluaciones de esta técnica en monturas de bajo costo, donde los errores sistemáticos (desnivel del trípode, desfase de la referencia inicial, flexión y holguras de las piezas) son mayores y, por tanto, potencialmente más corregibles. Tampoco se encontraron sistemas que integren en una sola plataforma abierta la montura de bajo costo, la corrección por aprendizaje automático y el control web orientado a usuarios no especializados."),
  P("En consecuencia, el objetivo de este trabajo fue diseñar, construir y evaluar un sistema de posicionamiento telescópico de bajo costo, adaptable a telescopios convencionales livianos, que corrige su error de apuntado mediante aprendizaje automático y se controla desde una interfaz web. Se plantearon tres hipótesis: (H1) el sistema posiciona el telescopio con un error cuadrático medio (RMS) menor que 30′, la mitad del campo visual típico de un ocular de bajo aumento (≈1°); (H2) la corrección por aprendizaje automático reduce significativamente el error de apuntado respecto del apuntado sin corrección; y (H3) el uso de la interfaz web reduce el tiempo de localización de un planeta frente a la búsqueda manual y alcanza una usabilidad superior al valor de referencia de 68 puntos de la escala SUS (Lewis, 2018)."),
  P("El artículo se organiza de la siguiente manera: la sección 2 describe el diseño mecánico, electrónico y de software, el método de corrección y el procedimiento experimental; la sección 3 presenta los resultados; la sección 4 los discute frente a trabajos previos; y la sección 5 resume las conclusiones."),
);

// ---------------------------------------------------------------- 2. Metodología
add(H1("2. Metodología"),
  P("La investigación tuvo un enfoque cuantitativo, de tipo aplicado y tecnológico, con un diseño experimental de medidas repetidas. El proceso se organizó en cuatro etapas: diseño, construcción, experimentación y análisis (Figura 1). Los resultados de cada prueba retroalimentaron el diseño cuando fue necesario."),
  figura(1, "fig1-metodologia.png", "Etapas de la metodología", "Elaboración propia.", 16),

  H2("2.1. Diseño mecánico"),
  P("Se diseñó una montura altacimutal de un solo brazo, modelada de forma paramétrica en OpenSCAD para que sus medidas puedan adaptarse a los componentes disponibles (Figura 2). La cabeza de la montura se fabricó con diez piezas impresas en 3D en PETG, que se monta sobre un trípode comercial de aluminio con rosca de 5/8″; se evitó imprimir el trípode porque su flexión degradaría la precisión. El eje de azimut gira sobre un rodamiento plano de 102 mm y es accionado por una corona dentada GT2 de 280 dientes impresa en el borde del plato giratorio, con una polea de 20 dientes en el motor (reducción de 14:1). El eje de altitud es una varilla de acero de 8 mm apoyada en dos rodamientos 608ZZ y accionada por una polea impresa de 100 dientes (reducción de 5:1). El brazo es un perfil de aluminio 2040, más rígido que una pieza impresa."),
  P("Para que el sistema pueda adaptarse a cualquier telescopio convencional liviano, el tubo se fija mediante una mordaza de cola de milano tipo Vixen, el estándar más extendido en telescopios pequeños; los telescopios con pie de rosca 1/4″-20 o con anillas se montan sobre una barra Vixen impresa. La carga máxima de diseño fue de 3 kg. Antes de fabricar las piezas se verificó por computadora que no existieran interferencias entre ellas en todo el recorrido del tubo, de −5° a 90° de altitud. La resolución angular de cada eje se calculó con la Ecuación 1:"),
  ecuacion(1, [M("θ = "), new MathFraction({ numerator: [M("360°")], denominator: [M("N · m · R")] })]),
  P("donde θ es el ángulo que avanza el eje por cada micropaso, N = 200 es el número de pasos por vuelta del motor, m = 16 es el número de micropasos configurado en el controlador y R es la relación de reducción de la transmisión."),
  figura(2, "fig2-montura-3d.png", "Modelo 3D de la montura altacimutal con un telescopio de referencia", "Elaboración propia. Telescopio Maksutov-Cassegrain de 90 mm representado de forma simplificada.", 9),

  H2("2.2. Diseño electrónico"),
  P("El controlador central fue una Raspberry Pi 4 (2 GB), elegida porque ejecuta en un mismo dispositivo el cálculo de efemérides, el servidor web y el modelo de aprendizaje automático. Esta elección sustituyó al microcontrolador ESP32 considerado en la planificación inicial, que no permitía ejecutar estas tareas de forma local. Dos controladores TB6600, configurados en 16 micropasos y 1,5 A, accionan los motores paso a paso NEMA 23 a partir de las señales de paso, dirección y habilitación generadas por los pines GPIO. Un módulo GPS u-blox NEO-6M proporciona la ubicación y la hora UTC; un módulo GY-91 (acelerómetro y barómetro) mide la inclinación del trípode y la presión atmosférica; y un codificador magnético AS5600 mide el ángulo real del eje de altitud. Dos interruptores de fin de carrera detienen el eje de altitud en los extremos de su recorrido. Para la operación en campo, el sistema se alimentó con una batería LiFePO4 de 12,8 V y 12 Ah, con fusible, interruptor general y un pulsador de paro de emergencia que corta solo la alimentación de los motores. La Figura 3 muestra el esquema de conexiones completo."),
  figura(3, "fig3-circuito.png", "Esquema de conexiones del sistema", "Elaboración propia. Los números corresponden a los pines físicos de la Raspberry Pi 4.", 16),
  tabla(1, "Componentes principales del prototipo", [
    ["Componente", "Modelo", "Cantidad", "Costo (USD)"],
    ["Motor paso a paso", "NEMA 23 JK57HS76 (1,9 N·m)", "2", "113,04"],
    ["Controlador de motor", "TB6600 (9–42 V)", "2", "38,26"],
    ["Computador de placa única", "Raspberry Pi 4 (2 GB)", "1", "77,99"],
    ["Receptor GPS", "u-blox NEO-6M", "1", "10,35"],
    ["Sensor inercial y barómetro", "GY-91 (MPU9250 + BMP280)", "1", "10,87"],
    ["Codificador magnético", "AS5600 (12 bits)", "1", "6,03"],
    ["Batería", "LiFePO4 12,8 V, 12 Ah", "1", "[[ ]]"],
    ["Piezas impresas", "PETG, ≈ 690 g", "10", "[[ ]]"],
    ["Mecánica y tornillería", "Rodamientos, correas GT2, perfil 2040, trípode", "—", "[[ ]]"],
    ["Total", "", "", "[[ ]]"],
  ], [2700, 3372, 1300, 1700], "Precios sin IVA. Los componentes electrónicos corresponden a la factura de compra; los demás, [[completar con los costos reales]]."),

  H2("2.3. Software"),
  P("El software se desarrolló en Python y se ejecuta en la Raspberry Pi. Las posiciones aparentes de los planetas y de la Luna se calcularon con la biblioteca Skyfield (Rhodes, 2019) a partir de las efemérides DE421 del Jet Propulsion Laboratory, para la ubicación y la hora entregadas por el GPS y con corrección por refracción atmosférica. El movimiento de los motores sigue un perfil de velocidad trapezoidal, con aceleración y frenado progresivos para evitar la pérdida de pasos (Fonseca-Campos et al., 2023), y ambos ejes se mueven de forma simultánea. Un servidor web desarrollado con FastAPI expone una interfaz accesible desde cualquier navegador de la red local (Figura 4): la Raspberry Pi crea su propia red inalámbrica, por lo que no se requiere conexión a Internet. Desde la interfaz el usuario elige un planeta visible, ordena el apuntado, centra el objeto con botones de ajuste fino y confirma el centrado. El software se verificó con 37 pruebas automáticas y en un modo de simulación sin hardware."),
  figura(4, "fig4-interfaz-web.png", "Interfaz web de control del telescopio", "Captura del prototipo en modo de simulación. [[Reemplazar por una captura del sistema real.]]", 15),

  H2("2.4. Corrección del apuntado mediante aprendizaje automático"),
  P("Cada vez que el usuario confirmó el centrado de un objeto, el sistema registró el ajuste que fue necesario respecto de la posición calculada, (Δa, Δh) en azimut y altitud. Como un desplazamiento en azimut equivale a un ángulo menor en el cielo cerca del cenit, el error de apuntado en el cielo se calculó con la Ecuación 2:"),
  ecuacion(2, [M("e = "), new MathRadical({ children: [
    new MathSuperScript({ children: [M("(Δa · cos(h))")], superScript: [M("2")] }), M(" + "),
    new MathSuperScript({ children: [M("Δh")], superScript: [M("2")] }) ] })]),
  P("donde h es la altitud del objeto. Con los registros se entrenaron dos modelos que predicen el error sistemático (Δa, Δh) en función de la dirección de apuntado (a, h), representada por funciones trigonométricas de ambos ángulos: un modelo lineal con regularización Ridge, equivalente a un modelo de apuntado clásico de pocos términos, y una red neuronal de perceptrón multicapa con dos capas ocultas de 16 neuronas y activación tangente hiperbólica, ambos implementados con scikit-learn (Pedregosa et al., 2011). Al aplicar la corrección, el sistema envía los motores a la posición calculada más el error predicho (Ecuación 3):"),
  ecuacion(3, [new MathSubScript({ children: [M("p")], subScript: [M("comando")] }), M(" = "),
    new MathSubScript({ children: [M("p")], subScript: [M("calculada")] }), M(" + "), M("f̂(a, h)")]),
  P("Para estimar el desempeño sin sesgo, cada modelo se evaluó mediante validación cruzada de 5 pliegues: el error residual de cada apuntado se calculó con un modelo que no había visto ese apuntado durante el entrenamiento."),

  H2("2.5. Procedimiento experimental"),
  P("Antes de cada sesión, el trípode se niveló, la montura se orientó al norte con la marca de referencia y se sincronizaron la hora y la ubicación mediante el GPS. Se realizaron cinco experimentos:"),
  vineta("E1, precisión del apuntado: se efectuaron al menos 30 apuntados a planetas y estrellas brillantes distribuidos por todo el cielo, durante [[n]] noches, con un telescopio [[modelo, abertura y focal]] y un ocular de [[25]] mm. Se registró el error de cada apuntado según la Ecuación 2."),
  vineta("E2, efecto de la corrección: con los datos de E1 se compararon el error sin corrección y el error residual con cada modelo, mediante validación cruzada. [[Si se realizan, describir también los apuntados reales con el modelo activo.]]"),
  vineta("E3, tiempo de localización: 20 participantes (estudiantes universitarios, docentes y personas vinculadas a la divulgación y al turismo), seleccionados mediante muestreo no probabilístico intencional, localizaron un planeta con búsqueda manual y con el sistema, en orden aleatorio. Se cronometró el tiempo hasta tener el planeta en el ocular."),
  vineta("E4, usabilidad: al terminar, cada participante respondió la escala SUS de 10 ítems (Brooke, 1996), cuyo puntaje va de 0 a 100."),
  vineta("E5, latencia: se registró el tiempo entre la orden enviada desde la interfaz web y el inicio del movimiento en al menos 50 comandos."),
  P("Los participantes firmaron un consentimiento informado y sus datos se registraron de forma anónima. [[Indicar si se obtuvo la aprobación de un comité de ética.]]"),

  H2("2.6. Análisis estadístico"),
  P("Los resultados se resumieron con la media, la desviación estándar, el valor RMS, la mediana y el intervalo de confianza del 95 %. La normalidad de las diferencias se evaluó con la prueba de Shapiro-Wilk. El error con y sin corrección (E2) y los tiempos de localización (E3) se compararon con la prueba t para muestras relacionadas o, si no se cumplía la normalidad, con la prueba de rangos con signo de Wilcoxon. El puntaje SUS se comparó con el valor de referencia de 68 mediante una prueba t para una muestra. Se usó un nivel de significancia α = 0,05 y se reportó el tamaño del efecto. Los análisis se realizaron en Python con SciPy [[y versión]]."),
);

// ---------------------------------------------------------------- 3. Resultados
add(H1("3. Resultados"),
  P("[[IMPORTANTE: esta sección se redacta en tiempo pasado y solo con datos medidos. No completar ninguna tabla con valores estimados.]]"),
  H2("3.1. Características del sistema construido"),
  P("La Tabla 2 resume las características técnicas obtenidas del diseño. Con las reducciones de 14:1 y 5:1, la resolución angular fue de 0,48′ en azimut y de 1,35′ en altitud por micropaso, frente a 6,75′ del acople directo considerado en la planificación inicial."),
  tabla(2, "Características técnicas del sistema", [
    ["Característica", "Azimut", "Altitud"],
    ["Reducción de la transmisión", "14:1", "5:1"],
    ["Resolución por micropaso (Ecuación 1)", "0,48′", "1,35′"],
    ["Velocidad máxima de apuntado", "[[≈ 16]] °/s", "[[≈ 20]] °/s"],
    ["Recorrido", "±270°", "−5° a 90°"],
    ["Carga máxima de diseño", "3 kg", "3 kg"],
    ["Autonomía con batería", "[[medir]] h", ""],
    ["Costo total del prototipo", "[[USD]]", ""],
  ], [4372, 2350, 2350], "Valores de diseño; [[confirmar la velocidad y la autonomía con mediciones]]."),
  H2("3.2. Precisión del apuntado (E1)"),
  P("Se registraron [[N]] apuntados durante [[n]] noches. El error de apuntado sin corrección fue de [[media ± DE]]′, con un valor RMS de [[ ]]′ (Tabla 3). [[Describir: en qué zonas del cielo fue mayor el error y si el planeta quedó dentro del campo del ocular en todos los casos.]]"),
  tabla(3, "Error de apuntado sin corrección", [
    ["Estadístico", "Δa · cos h (′)", "Δh (′)", "Error en el cielo (′)"],
    ["Media ± DE", "[[ ]]", "[[ ]]", "[[ ]]"],
    ["Mediana", "[[ ]]", "[[ ]]", "[[ ]]"],
    ["RMS", "[[ ]]", "[[ ]]", "[[ ]]"],
    ["Percentil 95", "[[ ]]", "[[ ]]", "[[ ]]"],
  ], [3072, 2000, 2000, 2000], "n = [[N]] apuntados."),
  H2("3.3. Efecto de la corrección por aprendizaje automático (E2)"),
  P("[[Describir los resultados de la Tabla 4: cuál modelo redujo más el error, el porcentaje de reducción y el valor p.]]"),
  tabla(4, "Error de apuntado con y sin corrección (validación cruzada de 5 pliegues)", [
    ["Condición", "RMS (′)", "Mediana (′)", "Reducción (%)", "p (Wilcoxon)"],
    ["Sin corrección", "[[ ]]", "[[ ]]", "—", "—"],
    ["Modelo lineal", "[[ ]]", "[[ ]]", "[[ ]]", "[[ ]]"],
    ["Red neuronal (MLP)", "[[ ]]", "[[ ]]", "[[ ]]", "[[ ]]"],
  ], [2672, 1600, 1600, 1600, 1600], "n = [[N]]. El software genera estos valores con el botón «Entrenar y evaluar»."),
  P("[[Figura 5: diagrama de cajas del error sin corrección, con modelo lineal y con red neuronal.]]"),
  H2("3.4. Tiempo de localización, usabilidad y latencia (E3, E4 y E5)"),
  tabla(5, "Resultados de las pruebas con usuarios", [
    ["Variable", "Manual", "Con el sistema", "p", "Tamaño del efecto"],
    ["Tiempo de localización (s), media ± DE", "[[ ]]", "[[ ]]", "[[ ]]", "[[ ]]"],
    ["Puntaje SUS (0–100), media ± DE", "—", "[[ ]]", "[[ ]] (frente a 68)", "[[ ]]"],
  ], [3472, 1400, 1600, 1300, 1300], "n = 20 participantes. Latencia web (E5): [[media ± DE]] ms en [[n]] comandos."),
);

// ---------------------------------------------------------------- 4. Discusión
add(H1("4. Discusión"),
  P("[[Comenzar con el hallazgo principal, en tiempo pasado. Ejemplo de estructura: «La corrección por aprendizaje automático redujo el error de apuntado de X′ a Y′…».]]"),
  P("El error de apuntado sin corrección ([[X]]′) [[fue menor / del mismo orden]] que el reportado por Barends et al. (2025) para una montura de bajo costo con reductores impresos (≈1,6° en azimut y 0,415° en altitud). [[Interpretar la diferencia: transmisión por correas GT2 frente a reductores impresos, resolución de 0,48′ y 1,35′, nivelación con el acelerómetro.]]"),
  P("La reducción del error obtenida con la corrección ([[Z]] %) [[es comparable / mayor / menor]] que la reducción del 33 % reportada por Chichura et al. (2025) en el South Pole Telescope, aunque en una escala de error distinta: segundos de arco en un instrumento profesional frente a minutos de arco en una montura de bajo costo. Este resultado es relevante porque muestra que la idea de Zariski et al. (2024) y Chichura et al. (2025), aprender el error sistemático de la montura a partir de sus propios registros, también es aplicable a hardware de bajo costo, donde los errores sistemáticos son mayores. [[Comparar el modelo lineal y la red neuronal: si la red no superó al modelo lineal, explicarlo por el tamaño de la muestra.]]"),
  P("En cuanto al uso, [[interpretar el tiempo de localización y el puntaje SUS]]. Al igual que en el trabajo de Ricci et al. (2024), la interfaz web permitió operar el telescopio desde cualquier dispositivo sin instalar software, y la red inalámbrica propia de la Raspberry Pi permitió hacerlo en lugares sin Internet, una condición frecuente en los sitios de astroturismo rural (Casanova Imbaquingo et al., 2024; Pinzón et al., en prensa)."),
  P("El estudio tuvo limitaciones. El error se midió por el centrado manual en el ocular, cuya resolución depende del observador; una cámara con resolución astrométrica (Lang et al., 2010) permitiría una medición más objetiva. La montura altacimutal produce rotación de campo, que no afecta la observación visual de planetas pero limita la astrofotografía de larga exposición. El modelo de corrección es válido para un montaje concreto del trípode y debe reentrenarse si cambia el telescopio. Finalmente, la muestra de usuarios fue pequeña y no probabilística, por lo que los resultados de usabilidad no son generalizables. [[Agregar las limitaciones observadas durante las pruebas.]]"),
);

// ---------------------------------------------------------------- 5. Conclusiones
add(H1("5. Conclusiones"),
  P("Se diseñó y construyó un sistema de posicionamiento telescópico de bajo costo, adaptable a telescopios convencionales de hasta 3 kg mediante una interfaz Vixen, que integra una montura altacimutal impresa en 3D, el cálculo de efemérides en tiempo real, la corrección del apuntado mediante aprendizaje automático y el control desde un navegador web."),
  P("[[Conclusión sobre H1 (precisión), con el valor medido.]] [[Conclusión sobre H2 (efecto de la corrección), con el porcentaje y el valor p.]] [[Conclusión sobre H3 (tiempo y usabilidad).]]"),
  P("Como trabajo futuro se propone incorporar una cámara para centrar el objeto de forma automática mediante visión por computadora, ampliar el catálogo a la Luna, estrellas brillantes y objetos de cielo profundo, y evaluar el sistema en actividades de astroturismo en zonas rurales del Ecuador."),
);

// ---------------------------------------------------------------- Declaraciones
add(H1("Conflicto de interés"),
  P("Los autores declaran que no existe conflicto de interés. [[Confirmar: si AFIFSYSTEMS S.A.S. financió los componentes, evaluar si debe declararse.]]"),
  H1("Fuente de financiamiento"),
  P("[[Completar: «La investigación fue financiada con fondos propios de la autora» o indicar la entidad que la financió (por ejemplo, AFIFSYSTEMS S.A.S.).]]"),
  H1("Contribución de autoría (CRediT)"),
  P("Nashla Carolina Tuma Zambrano: conceptualización, metodología, software, validación, análisis formal, investigación, gestión de datos, visualización, redacción – preparación del borrador original, financiamiento. [[Diego Paul Corrales Vargas]]: supervisión, administración del proyecto, redacción – revisión y edición. [[Ajustar según las contribuciones reales.]]"),
  H1("Agradecimiento"),
  P("[[Opcional: agradecer a la PUCE Sede Manabí, a los participantes de las pruebas y a quienes facilitaron el lugar de observación.]]"),
  H1("Declaración de uso de herramientas de inteligencia artificial"),
  P("[[Si la revista lo solicita o la autora lo considera pertinente: declarar el uso de asistentes de IA en el diseño, la programación o la redacción, indicando que la autora revisó y asume la responsabilidad del contenido.]]"),
);

// ---------------------------------------------------------------- Referencias
const REFS = [
  "Barends, R. A., Prastyo, H. A., Rozzykin, A. Z., Wahidin, A. B., Wibowo, R. W., Yusuf, A. A., & Oktaviandra, A. (2025). Characterization of do-it-yourself (DIY) ultra compact ITERA robotic telescope (UTOPIA-Scope) mounting. _Indonesian Journal of Aerospace, 23_(2), 117–126. https://doi.org/10.55981/ijoa.2025.4098",
  "Brooke, J. (1996). SUS: A “quick and dirty” usability scale. En P. W. Jordan, B. Thomas, B. A. Weerdmeester e I. L. McClelland (Eds.), _Usability evaluation in industry_ (pp. 189–194). Taylor & Francis.",
  "Casanova Imbaquingo, L. E., Guerrero Cabezas, T. E., Dávila Perugachi, Á. D., & Catucuamba Quinatoa, W. P. (2024). Astroturismo, un producto turístico para áreas protegidas. _Realidad, Tendencias y Desafíos en Turismo (CONDET), 22_(2), 53–74. https://revele.uncoma.edu.ar/index.php/condet/article/view/5463",
  "Chichura, P. M., Rahlin, A., Anderson, A. J., Ansarinejad, B., Archipley, M., Balkenhol, L., Benabed, K., Bender, A. N., Benson, B. A., Bianchini, F., Bleem, L. E., Bouchet, F. R., Bryant, L., Camphuis, E., Carlstrom, J. E., Chang, C. L., Chaubal, P., Chokshi, A., Chou, T.-L., … Zebrowski, J. A. (2025). Pointing accuracy improvements for the South Pole Telescope with machine learning. _Journal of Astronomical Instrumentation, 14_(1), Artículo 2550001. https://doi.org/10.1142/S2251171725500011",
  "Dutton, H. (s. f.). _OnStep: Telescope GoTo controller_ [Software]. GitHub. [[verificar URL: https://github.com/hjd1964/OnStep]]",
  "Fonseca-Campos, J., Reyes-Ramírez, I., Mata-Machuca, J. L., Fonseca-Ruiz, L., Cortez-Herrera, P. N., Flores-Cotera, L. B., & Aguilar-López, R. (2023). Implementation in microcontrollers of an algorithm for the simple generation of speed profiles in a stepper motor and their associated kinematics. _IEEE Access, 11_, 143782–143803. https://doi.org/10.1109/ACCESS.2023.3343638",
  "Lang, D., Hogg, D. W., Mierle, K., Blanton, M., & Roweis, S. (2010). Astrometry.net: Blind astrometric calibration of arbitrary astronomical images. _The Astronomical Journal, 139_(5), 1782–1800. https://doi.org/10.1088/0004-6256/139/5/1782",
  "Lewis, J. R. (2018). The System Usability Scale: Past, present, and future. _International Journal of Human–Computer Interaction, 34_(7), 577–590. https://doi.org/10.1080/10447318.2018.1455307",
  "Mello, D. R. C. (2023). Astroturismo – Viajando para ver as estrelas. _Revista de Turismo Contemporâneo, 11_(1), 169–189. https://periodicos.ufrn.br/turismocontemporaneo/article/view/27440",
  "OpenAstroTech. (s. f.). _Open source astronomy equipment_. https://openastrotech.com/",
  "Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., Blondel, M., Prettenhofer, P., Weiss, R., Dubourg, V., Vanderplas, J., Passos, A., Cournapeau, D., Brucher, M., Perrot, M., & Duchesnay, É. (2011). Scikit-learn: Machine learning in Python. _Journal of Machine Learning Research, 12_, 2825–2830. https://jmlr.org/papers/v12/pedregosa11a.html",
  "Pinzón, G., Vásquez, N., & García, B. (en prensa). First Andean network of entrepreneurs in astrotourism. _Revista Mexicana de Astronomía y Astrofísica, Serie de Conferencias, 60_. https://www.astroscu.unam.mx/rmaa/RMxAC..60/PDF/RMxAC..60_gpinzon-23.pdf [[verificar año y páginas]]",
  "Rhodes, B. (2019). _Skyfield: High precision research-grade positions for planets and Earth satellites generator_ (ascl:1907.024) [Software]. Astrophysics Source Code Library. https://ascl.net/1907.024",
  "Ricci, D., Cabona, L., Salasnich, B., Nicastro, L., Fini, L., Damonte, A., Tosi, S., & Shibata, T. (2024). Easy remote observations using web interfaces: Controlling an Italian telescope from Japan, and more. _Proceedings of SPIE, 13098_, 130980T. https://doi.org/10.1117/12.3018331",
  "Zariski, J., Kratter, K., Logsdon, S., Bender, C., Li, D., Schweiker, H., Rajagopal, J., McBride, B., & Hunting, E. (2024). Deep learning solutions to telescope pointing and guiding. _Proceedings of SPIE, 13101_, 131010Q. https://doi.org/10.1117/12.3018092",
];
add(H1("Referencias"));
REFS.forEach((r) => add(new Paragraph({ alignment: AlignmentType.LEFT, indent: { left: 709, hanging: 709 }, children: runs(r) })));

// ----------------------------------------------------------------- documento
const doc = new Document({
  creator: "Nashla Carolina Tuma Zambrano",
  title: "Sistema de posicionamiento telescópico con corrección de apuntado mediante aprendizaje automático y control web",
  styles: { default: { document: { run: { font: FUENTE, size: TAM }, paragraph: { spacing: { line: 360, lineRule: LineRuleType.AUTO, after: 120 } } } } },
  numbering: { config: [{ reference: "vinetas", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 567, hanging: 283 } } } }] }] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1417, bottom: 1417, left: 1417, right: 1417 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT] })] })] }) },
    children: cuerpo,
  }],
});

// docx-js agrega <w:highlightCs>, que no está en el esquema de Word: se elimina
Packer.toBuffer(doc).then(async (buf) => {
  const JSZip = require(require.resolve("jszip", { paths: [path.dirname(require.resolve("docx"))] }));
  const zip = await JSZip.loadAsync(buf);
  const xml = await zip.file("word/document.xml").async("string");
  zip.file("word/document.xml", xml.replace(/<w:highlightCs [^>]*\/>/g, ""));
  const salida = path.join(__dirname, "articulo_v2.docx");
  fs.writeFileSync(salida, await zip.generateAsync({ type: "nodebuffer", compression: "DEFLATE" }));
  console.log("Generado:", salida);
});

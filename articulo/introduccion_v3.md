# Apuntado autónomo de cuerpos celestes con una montura de bajo costo: resolución astrométrica en una Raspberry Pi y corrección del error con aprendizaje automático

*Autonomous pointing at celestial objects with a low-cost mount: on-board plate solving on a Raspberry Pi and machine-learning error correction*

Nashla Carolina Tuma Zambrano¹*, [[Confirmar coautoría del tutor: Ing. Alex Ricaurte²]]

## 1. Introducción

Apuntar un instrumento a un cuerpo celeste exige saber con precisión hacia dónde mira. Los telescopios con apuntado automático (sistemas _GoTo_) calculan la posición del objeto y mueven la montura hasta ella. Las soluciones comerciales son cerradas y su costo es elevado para instituciones educativas y de divulgación. Como alternativa han surgido proyectos abiertos, como el controlador OnStep (Dutton, s. f.) y los equipos impresos en 3D de OpenAstroTech (OpenAstroTech, s. f.). En la región andina, el interés por estos equipos crece junto con el astroturismo. En Ecuador se han diseñado productos astroturísticos para áreas protegidas (Casanova Imbaquingo et al., 2024), y en 2023 se conformó en Quito la primera red andina de emprendedores en astroturismo (Pinzón et al., en prensa).

El bajo costo tiene un precio en precisión. Barends et al. (2025) caracterizaron una montura robótica altacimutal construida con perfiles de aluminio y reductores impresos en 3D. Midieron errores medios de apuntado de 1,6° en azimut y 0,415° en altitud. Esos errores superan el campo visual de un ocular de bajo aumento, que es de alrededor de 1°. Su origen es sistemático: el desnivel del trípode, el desfase de la referencia inicial, la flexión de las piezas y la holgura de las transmisiones. Como son sistemáticos, dependen de la dirección de apuntado y pueden modelarse. Es lo que hace el modelo de apuntado físico que emplean los telescopios profesionales (Zariski et al., 2024).

Calibrar un modelo de apuntado requiere conocer dónde apuntó realmente el instrumento. En una montura de aficionado, esa medición suele hacerse a mano: el usuario centra una estrella conocida y el sistema registra la corrección. El procedimiento es lento, depende del observador y se limita a unas pocas estrellas. La resolución astrométrica (_plate solving_) ofrece una alternativa automática. A partir de una fotografía del cielo, identifica el patrón de estrellas en un catálogo y devuelve las coordenadas del centro de la imagen, sin información previa sobre la orientación (Lang et al., 2010). El programa ASTAP realiza este cálculo y tiene una versión para la Raspberry Pi (Kleijn, s. f.). Con una cámara sobre la montura, cada fotografía resuelta se convierte en una medición del error de apuntado. Esa medición es posible en cualquier región del cielo donde haya estrellas.

El aprendizaje automático ha comenzado a complementar al modelo clásico. Zariski et al. (2024) reemplazaron el modelo de apuntado físico del telescopio WIYN de 3,5 m por una combinación de una red neuronal recurrente y árboles de gradiente. Chichura et al. (2025) entrenaron modelos XGBoost que redujeron en un 33 % el error combinado de apuntado del South Pole Telescope, de 15,9″ a 10,6″. En antenas de estaciones terrenas, Bergerhoff (2024) calibró la corrección de apuntado durante la operación, con las señales que el sistema ya registra. En todos los casos se trata de instrumentos profesionales, con errores del orden de los segundos de arco.

El lugar donde se ejecuta el cálculo también importa. La resolución astrométrica suele hacerse en un computador portátil o en un servicio en línea, como el de Astrometry.net (Lang et al., 2010). El cómputo en el borde propone procesar los datos cerca de donde se generan. Así se reducen la latencia, el consumo de ancho de banda y la dependencia de la red (Shi et al., 2016). En un instrumento que se opera en el campo, a menudo sin internet, esa diferencia decide si el sistema puede calibrarse por sí mismo. Ricci et al. (2024) mostraron que una interfaz web basta para operar un telescopio a distancia. Ese esquema, sin embargo, depende de una conexión permanente.

Estos antecedentes dejan tres vacíos. Primero, la corrección del apuntado con aprendizaje automático se ha evaluado en instrumentos profesionales (Chichura et al., 2025; Zariski et al., 2024). En la literatura revisada no se encontraron evaluaciones en monturas de bajo costo, cuyos errores son al menos dos órdenes de magnitud mayores (Barends et al., 2025). Segundo, no se encontró una comparación medida entre resolver las imágenes en el propio instrumento y hacerlo en la nube, en términos de latencia, tasa de éxito y energía. Tercero, no está documentado si un modelo calibrado en una región limitada del cielo sirve para apuntar al resto de la bóveda celeste. Es el caso de un modelo entrenado mientras se sigue un solo objeto durante una noche. Esta pregunta es decisiva para un instrumento cuyo propósito es apuntar a cualquier cuerpo celeste.

En consecuencia, el objetivo de este trabajo fue diseñar, construir y evaluar una montura altacimutal de bajo costo que calibra su propio apuntado mediante resolución astrométrica en una Raspberry Pi y corrige el error con aprendizaje automático. Se plantearon cuatro hipótesis. (H1) Tras la calibración, el error cuadrático medio (RMS) de apuntado en todo el cielo es menor que 30′, la mitad del campo visual de un ocular de bajo aumento. (H2) Un corrector aprendido reduce el error respecto del modelo de apuntado clásico. (H3) La resolución en la Raspberry Pi tiene una latencia menor que la del servicio en la nube y funciona sin conexión a internet. (H4) Un modelo calibrado en un sector del cielo tiene un error mayor fuera de ese sector que un modelo calibrado con mediciones repartidas por toda la bóveda.

El artículo se organiza de la siguiente manera. La sección 2 describe la montura, la electrónica, el procedimiento de calibración, los modelos comparados y el diseño experimental. La sección 3 presenta los resultados. La sección 4 los discute frente a los trabajos previos, y la sección 5 resume las conclusiones.

## Referencias

Barends, R. A., Prastyo, H. A., Rozzykin, A. Z., Wahidin, A. B., Wibowo, R. W., Yusuf, A. A., & Oktaviandra, A. (2025). Characterization of do-it-yourself (DIY) ultra compact ITERA robotic telescope (UTOPIA-Scope) mounting. _Indonesian Journal of Aerospace, 23_(2), 117–126. https://doi.org/10.55981/ijoa.2025.4098

Bergerhoff, L. (2024). _Learning antenna pointing correction in operations: Efficient calibration of a black box_ (arXiv:2405.15247). arXiv. https://doi.org/10.48550/arXiv.2405.15247

Casanova Imbaquingo, L. E., Guerrero Cabezas, T. E., Dávila Perugachi, Á. D., & Catucuamba Quinatoa, W. P. (2024). Astroturismo, un producto turístico para áreas protegidas. _Realidad, Tendencias y Desafíos en Turismo (CONDET), 22_(2), 53–74. https://revele.uncoma.edu.ar/index.php/condet/article/view/5463

Chichura, P. M., Rahlin, A., Anderson, A. J., Ansarinejad, B., Archipley, M., Balkenhol, L., Benabed, K., Bender, A. N., Benson, B. A., Bianchini, F., Bleem, L. E., Bouchet, F. R., Bryant, L., Camphuis, E., Carlstrom, J. E., Chang, C. L., Chaubal, P., Chokshi, A., Chou, T.-L., … Zebrowski, J. A. (2025). Pointing accuracy improvements for the South Pole Telescope with machine learning. _Journal of Astronomical Instrumentation, 14_(1), Artículo 2550001. https://doi.org/10.1142/S2251171725500011

Dutton, H. (s. f.). _OnStep: Telescope GoTo controller_ [Software]. GitHub. https://github.com/hjd1964/OnStep

Kleijn, H. (s. f.). _ASTAP, the Astrometric STAcking Program_ [Software]. https://www.hnsky.org/astap.htm

Lang, D., Hogg, D. W., Mierle, K., Blanton, M., & Roweis, S. (2010). Astrometry.net: Blind astrometric calibration of arbitrary astronomical images. _The Astronomical Journal, 139_(5), 1782–1800. https://doi.org/10.1088/0004-6256/139/5/1782

OpenAstroTech. (s. f.). _Open source astronomy equipment_. https://openastrotech.com/

Pinzón, G., Vásquez, N., & García, B. (en prensa). First Andean network of entrepreneurs in astrotourism. _Revista Mexicana de Astronomía y Astrofísica, Serie de Conferencias, 60_. https://www.astroscu.unam.mx/rmaa/RMxAC..60/PDF/RMxAC..60_gpinzon-23.pdf [[verificar año y páginas]]

Ricci, D., Cabona, L., Salasnich, B., Nicastro, L., Fini, L., Damonte, A., Tosi, S., & Shibata, T. (2024). Easy remote observations using web interfaces: Controlling an Italian telescope from Japan, and more. _Proceedings of SPIE, 13098_, 130980T. https://doi.org/10.1117/12.3018331

Shi, W., Cao, J., Zhang, Q., Li, Y., & Xu, L. (2016). Edge computing: Vision and challenges. _IEEE Internet of Things Journal, 3_(5), 637–646. https://doi.org/10.1109/JIOT.2016.2579198

Zariski, J., Kratter, K., Logsdon, S., Bender, C., Li, D., Schweiker, H., Rajagopal, J., McBride, B., & Hunting, E. (2024). Deep learning solutions to telescope pointing and guiding. _Proceedings of SPIE, 13101_, 131010Q. https://doi.org/10.1117/12.3018092

# `analisis/` · Los experimentos que producen las tablas del artículo

Cada script de esta carpeta imprime una tabla que va al artículo, y se puede volver a correr
de cero. Nada de resultados escritos a mano: si una cifra aparece en el artículo, sale de
correr uno de estos scripts.

Los CSV que generan van a `prototipo/datos/<experimento>/` y **no se versionan** (están en el
`.gitignore`). Se regeneran solos.

## Cómo se corre

Desde `prototipo/`, con el entorno virtual:

```bash
./.venv/Scripts/python.exe -P analisis/e5_transferencia.py --sorteos 6
```

El `-P` quita el directorio del script de `sys.path`, así que hay que pasar la **ruta** del
archivo y no `-m analisis.e5_transferencia`.

## Los scripts

| Script | Qué responde | Experimento de `docs/08` |
|---|---|---|
| `e5_transferencia.py` | ¿El corrector aprendido vence al modelo clásico? ¿Sirve preentrenar en simulación? | E3 y E4 |

## Por qué todos repiten el experimento con varios sorteos

Porque un sorteo no dice nada, y casi nos cuesta un resultado falso.

El 07/11/2026, la primera medición del preentrenamiento dio una mejora clara y
estadísticamente significativa (p = 0,0078, el mínimo posible con 8 noches). Al repetir el
**mismo** experimento con otras monturas sorteadas de la **misma** distribución, el efecto se
sostuvo en 4 de 6 sorteos y se dio la vuelta en 2. O sea: no era un resultado, era una
semilla afortunada.

De ahí la regla de esta carpeta:

> Un efecto que no se sostiene en la mayoría de los sorteos independientes no se publica como
> resultado. Si las cuentas salen repartidas, lo que se publica es eso: que salen repartidas.

Cada script imprime al final un recuento de en cuántos sorteos se sostiene cada afirmación,
precisamente para que esto no se pueda pasar por alto al redactar.

## Qué no hacen estos scripts

**No sustituyen a los datos reales.** Corren sobre noches simuladas, y sirven para dos cosas:
diseñar el método antes de gastar noches de telescopio, y detectar errores de razonamiento
mientras todavía son baratos. Los resultados del artículo salen de mediciones reales; estos
scripts dicen qué merece la pena medir y con cuántas noches.

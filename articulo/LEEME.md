# Artículo científico · versión 2

`articulo_v2.docx` es el artículo reescrito según la guía de autores de **Esprint
Investigación**: A4, márgenes de 2,5 cm, Times New Roman 12, interlineado 1,5, texto
justificado, numeración de páginas, tablas solo con bordes horizontales, ecuaciones con el
editor de Word, figuras con "Nota:" y referencias APA 7 en orden alfabético. Tiene 14
páginas (la revista pide de 10 a 20).

> ⚠️ **Todo lo resaltado en amarillo `[[ ]]` es un dato pendiente.** Se completa
> **únicamente con mediciones reales** de las pruebas. No se debe rellenar con valores
> estimados, ni siquiera de forma provisional.

## Qué cambió respecto del borrador original

| Aspecto | Borrador original | Versión 2 |
|---|---|---|
| Resultados | Describían pruebas que no se habían hecho (10–15′, Júpiter durante 5 min, tubo de 4 kg…) | Se eliminaron. Quedan tablas vacías para los datos reales y solo los resultados de diseño que ya son verificables |
| Aporte de IA | "Incipiente", sin método ni medición | **Corrección del error de apuntado con aprendizaje automático** (modelo lineal frente a red neuronal), con validación cruzada y prueba de Wilcoxon |
| Hipótesis | No había | H1 (precisión < 30′), H2 (la IA reduce el error), H3 (tiempo y SUS > 68) |
| Resumen | 265 palabras, sin números ni p, sin abstract | **228 palabras**, con las 5 partes que pide la revista y espacios para los valores y el p. El abstract se traduce al final |
| Persona gramatical | Primera persona ("hemos", "nuestro") | Tercera persona impersonal ("se diseñó", "se registró") |
| Palabras clave | Sin orden | 5, en orden alfabético, en español e inglés |
| Metodología | Solo descripción de ingeniería | Enfoque, diseño, Figura 1 de proceso, Ecuaciones 1–3, experimentos E1–E5, muestra y análisis estadístico |
| Hardware | Contradicciones (ESP32 frente a Raspberry Pi, correa frente a acople directo, fines de carrera no comprados) | Coherente con lo que se construye, explicando el cambio de ESP32 a Raspberry Pi |
| Adaptabilidad | Solo un telescopio | **Universal:** cola de milano Vixen, telescopios de hasta 3 kg |
| Referencias | 7, sin citas en el texto, 2 inexistentes y otras con datos erróneos | **15 verificadas**, con DOI cuando existe, todas citadas en el texto |
| Figuras | Anunciadas pero inexistentes | 4 figuras: metodología, modelo 3D, alimentación e interfaz |

## Lo que tienes que completar

1. **Datos de autoría:** ORCID (gratis en orcid.org), la coautoría y filiación del tutor, y
   la contribución CRediT.
2. **Financiamiento y conflicto de interés:** aclarar el papel de AFIFSYSTEMS S.A.S.
3. **Después de las pruebas:** todos los `[[ ]]` de las secciones de resumen, resultados,
   discusión y conclusiones.
4. **Figuras pendientes:**
   - Esquema de conexiones (paso 6 del plan).
   - Captura de la interfaz real.
   - Figura 5, el diagrama de cajas que genera el script de análisis.
5. **Verificar 2 referencias**, marcadas en el documento: la URL de OnStep y el año y las
   páginas de Pinzón et al.
6. **Abstract** en inglés, al final.

## Cómo regenerar el Word

Si cambias el texto en `generar_articulo.js`:

```bash
cd articulo && node generar_articulo.js
```

Si prefieres editar directamente en Word, edita `articulo_v2.docx` y deja de usar el script.

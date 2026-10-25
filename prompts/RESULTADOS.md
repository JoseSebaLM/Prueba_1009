# Banco de prompts: resultados de consistencia

- **Fecha:** 2026-10-25 · **Modelo:** `gemini-3.5-flash-lite` · **Repeticiones por prompt:** 5 (el mínimo de la actividad es 3)
- **Cómo se reproduce:** `python -m prompts.test_consistencia` (desde la raíz del proyecto). El registro estructurado queda en [`registro_resultados.json`](registro_resultados.json).
- **Qué cuenta como éxito:** la respuesta es JSON válido (después de limpiar marcas de markdown) **y** trae todas las `claves_esperadas`. Un JSON válido sin esas claves cuenta como fallo. Los fallos del servicio (red, 429, 5xx) se registran aparte, para no atribuírselos al prompt.

| Prompt | Para qué sirve en PM1 | Esquema (`responseSchema`) | Resultado |
|---|---|---|---|
| `clasificar_eje` | Ubicar la duda del estudiante en uno de los 4 ejes de la PAES M1 | Sí (con `enum` de ejes) | 5/5 (100 %) |
| `generar_pista` | Dar una pista sin resolver el ejercicio | Sí (con `enum` de dificultad) | 5/5 (100 %) |
| `extraer_datos_problema` | Separar los datos y la incógnita de un enunciado | No, solo la instrucción en el prompt de sistema | 5/5 (100 %) |

## Observaciones

- **Ningún prompt necesitó ajuste:** todos superaron el umbral de 2/3 desde la primera medición.
- **Contenido, además de estructura:** en una revisión manual de 2 respuestas por prompt, `clasificar_eje` eligió `numeros` (correcto para un descuento porcentual), `generar_pista` sugirió aplicar la propiedad distributiva sin revelar x = −4, y `extraer_datos_problema` identificó los 2 datos y la incógnita (área del rectángulo).
- **Instrucción sola vs. instrucción + esquema:** con este modelo y este enunciado, el prompt sin `responseSchema` fue tan consistente como los que lo usan. Aun así, en PM1 conviene usar el esquema cuando el código toma decisiones con la respuesta (por ejemplo, un `if` sobre el eje), porque el `enum` limita los valores posibles y la API lo aplica al generar.

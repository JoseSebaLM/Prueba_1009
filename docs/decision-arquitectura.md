# Decisión de arquitectura: elección de modelo

- **Fecha de la medición:** 2026-10-25 (14:33, hora de Chile)
- **Fuente de precios:** [ai.google.dev/gemini-api/docs/pricing](https://ai.google.dev/gemini-api/docs/pricing), consultada el 2026-10-25 (página actualizada el 2026-10-22). Precios de la capa de pago; en la capa gratuita que usa el proyecto el costo es 0, pero se compara lo que costaría PM1 en producción.
- **Datos crudos:** [`resultados_medicion_modelos.json`](resultados_medicion_modelos.json), generados con [`medir_modelos.py`](medir_modelos.py) (`python -m docs.medir_modelos`).

## Modelo elegido

**`gemini-3.5-flash-lite`**, configurado en la constante `MODELO` de [`src/consumir_gemini.py`](../src/consumir_gemini.py).

## Diagrama de arquitectura

El flujo completo (funciones, llave, manejo de errores, cálculo de costo y datos que cruzan cada flecha) está en **[diagrama_arquitectura.md](diagrama_arquitectura.md)**. El modelo elegido es el valor de `MODELO` que `armar_peticion` pone en la URL `…/models/MODELO:generateContent`; cambiar de modelo no altera ninguna otra caja del diagrama.

## Comparación de candidatos

Mismo código y misma red para los dos candidatos. La latencia se midió con 4 repeticiones de la misma pregunta: *"Un alumno pregunta: ¿cómo despejo x en 3x + 5 = 20? Dale una pista sin resolverlo."* La calidad se midió con 3 preguntas representativas de PAES M1, una por eje.

| Criterio | `gemini-3.5-flash-lite` | `gemini-3.6-flash` |
|---|---|---|
| Precio entrada (USD / 1 M tokens) | 0,30 | 0,75 (sube a 1,50 desde el 1-ene-2027) |
| Precio salida, incluye pensamiento (USD / 1 M tokens) | 2,50 | 3,75 (sube a 7,50 desde el 1-ene-2027) |
| Peticiones exitosas (prueba de latencia) | 4/4 | 3/4 (1 error 503 por alta demanda) |
| Latencia promedio | **2,65 s** (2,27 – 3,29 s) | **12,88 s** (11,17 – 15,08 s) |
| Tokens de salida promedio (respuesta + pensamiento) | 92 (sin pensamiento) | 723 (≈ 85 % son tokens de pensamiento) |
| Costo promedio por petición | **0,00024 USD** | **0,00273 USD** (≈ 11 veces más) |
| Costo estimado con 50 000 peticiones/mes (500 estudiantes × 100 preguntas) | ≈ 12 USD | ≈ 137 USD (≈ 273 USD desde 2027) |
| Calidad · Álgebra: pista sin resolver `2(x − 3) = 4x + 2` | ✅ Pista correcta (distributiva), no revela x = −4 | ✅ Pista correcta (distributiva), no revela x = −4 |
| Calidad · Números: descuento de $12.000 a $9.000 | ✅ 25 %, 3 pasos claros | ✅ 25 %, 3 pasos claros |
| Calidad · Probabilidad: suma 7 con dos dados | ✅ 6/36 = 1/6, lista los 6 casos | ✅ 6/36 = 1/6, lista los 6 casos |

Mini-rúbrica de calidad usada: ¿es matemáticamente correcta?, ¿da la pista sin resolver cuando se pide?, ¿usa un lenguaje adecuado para un estudiante de 4° medio? Las respuestas completas están en el JSON de resultados.

**Tercer candidato probado:** también se midió `gemini-3.8-flash` (el Flash vigente, mismo precio que 3.6). No se pudo usar: falló en las 7 peticiones de la medición (503 por alta demanda, 429 por cuota y tiempos de espera sobre 30 s), y también en las 14 de dos corridas anteriores ese mismo día. Por eso no aparece en la tabla con datos de latencia ni de calidad.

## Justificación

PM1 es un tutor para estudiantes que preparan la PAES M1 por su cuenta. Responde muchas dudas cortas, y del otro lado hay un estudiante esperando en vivo. Para este caso **pesaron más la latencia y el costo, porque la calidad empató**: en las 3 preguntas representativas ambos modelos dieron respuestas correctas, con pistas que no resuelven el ejercicio y un lenguaje adecuado.

Con calidad equivalente, `gemini-3.5-flash-lite` responde en unos 2,7 s, frente a casi 13 s, y cuesta unas 11 veces menos por petición. La diferencia se explica casi entera por los tokens de "pensamiento" que `gemini-3.6-flash` genera antes de responder: se cobran como salida y se esperan como latencia. Además, `gemini-3.5-flash-lite` fue el único candidato sin errores de disponibilidad durante la medición (4/4).

## Alternativa descartada y por qué

**Descarté `gemini-3.6-flash`.** Razonó más, pero para estas preguntas eso no mejoró la respuesta: las tres quedaron igual de correctas. A cambio fue unas 5 veces más lento (12,9 s promedio, una espera difícil de tolerar en un tutor) y unas 11 veces más caro, y su precio se duplica desde enero de 2027. También tuvo 1 error 503 en 4 intentos.

Lo reconsideraría si PM1 necesita resolver problemas de varios pasos donde el modelo liviano empiece a equivocarse, por ejemplo problemas de modelación largos o de geometría con varias figuras. En ese caso convendría usarlo solo para esas preguntas, no para todas.

`gemini-3.8-flash` quedó descartado por **disponibilidad**: el 2026-10-25 no respondió ninguna de las peticiones. Vale la pena medirlo de nuevo en el Módulo 2, cuando el cliente tenga reintentos con espera creciente.

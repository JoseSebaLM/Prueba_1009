# Diagrama de arquitectura — PM1 (miniaplicación del Gate 1)

Camino de una pregunta de un estudiante de PAES M1, desde que se escribe hasta que vuelve la respuesta y su costo. Las cajas son las funciones reales de `src/consumir_gemini.py`; cada flecha indica el dato que transporta.

```mermaid
flowchart TD
    U["Estudiante / main.py<br/>pregunta de matemática M1"]
    ENV[(".env<br/>GEMINI_API_KEY")]
    A["armar_peticion(pregunta)<br/>valida: pregunta no vacía → ValueError<br/>valida: llave presente → ValueError"]
    E["enviar_peticion(url, encabezados, cuerpo)<br/>try: requests.post(timeout=30)"]
    API[["API Gemini<br/>POST /v1beta/models/MODELO:generateContent"]]
    X["extraer_texto(datos)<br/>candidates[0].content.parts[0].text"]
    C["calcular_costo(datos, precio_entrada, precio_salida)<br/>usageMetadata: prompt + candidates + thoughts"]

    U -- "pregunta (str)" --> A
    ENV -. "os.getenv('GEMINI_API_KEY')" .-> A
    A -- "url + encabezados (x-goog-api-key) + cuerpo JSON" --> E
    E -- "POST HTTPS" --> API
    API -- "respuesta HTTP + JSON" --> E
    E -- "respuesta cruda (dict)" --> X
    E -- "respuesta cruda (dict)" --> C
    X -- "texto generado (str)" --> U
    C -- "costo en USD (float)" --> U

    E -. "ConnectionError / Timeout → RuntimeError<br/>HTTP ≠ 200 (400, 401, 403, 404, 429, 5xx) → RuntimeError<br/>JSONDecodeError → RuntimeError" .-> ERR
    X -. "KeyError / IndexError → RuntimeError" .-> ERR
    A -. "ValueError" .-> ERR
    ERR["Manejo de errores<br/>quien llama atrapa (ValueError, RuntimeError)<br/>y muestra un mensaje claro, sin traceback"]
```

## Qué responde el diagrama

| Pregunta | Respuesta |
|---|---|
| Orden de las funciones | `armar_peticion` → `enviar_peticion` → `extraer_texto` (y `calcular_costo` sobre la misma respuesta cruda) |
| Dónde vive y se usa la llave | En `.env` (nunca en el repo). Solo `armar_peticion` la lee con `os.getenv` y la pone en el header `x-goog-api-key` |
| Dónde se manejan los errores | Validación en `armar_peticion`; conexión, tiempo límite, código HTTP y formato JSON en `enviar_peticion`; dato faltante en `extraer_texto` |
| Dónde se calcula el costo | En `calcular_costo`, después de recibir la respuesta, con `usageMetadata` |
| Qué cruza cada flecha | pregunta → URL + encabezados + cuerpo → JSON crudo → texto / costo |

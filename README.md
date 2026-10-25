# PM1 — Tutor de matemática PAES M1 (miniaplicación del Gate 1)

Miniaplicación en Python que consulta a **Google Gemini** para ayudar a estudiantes que preparan la PAES de Competencia Matemática 1 (M1). Recibe la duda de un estudiante, **la clasifica por eje** (números, álgebra y funciones, geometría, probabilidad y estadística) y **genera una pista que no resuelve el ejercicio**. Usa un prompt de sistema, pide la salida en JSON estructurado, maneja los errores previsibles y calcula el costo de cada petición.

Proyecto del programa *Especialización en Desarrollo con IA Generativa* (Skillnest · Accenture), Módulo 1 · Gate 1. Es la primera capa del proyecto que crecerá hasta el Gate 3 (tutor con RAG, expuesto por API y en contenedor).

## Requisitos

- **Python 3** (probado con Python 3.14.3) y **Git**.
- Una **API key gratuita de Google AI Studio**: https://aistudio.google.com/apikey (no requiere tarjeta).

## Instalación

### Windows (PowerShell)

```powershell
git clone https://github.com/JoseSebaLM/Prueba_1009.git pm1
cd pm1
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
```

En `notepad`, reemplaza `tu_llave_aqui` por tu llave real (sin comillas ni espacios) y guarda.

Si al activar el entorno aparece *"la ejecución de scripts está deshabilitada"*, ejecuta una sola vez `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` y vuelve a activarlo.

### macOS / Linux

```bash
git clone https://github.com/JoseSebaLM/Prueba_1009.git pm1
cd pm1
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Abre `.env` con tu editor y reemplaza `tu_llave_aqui` por tu llave real.

## Variables de entorno

| Variable | Descripción |
|---|---|
| `GEMINI_API_KEY` | Llave de Google AI Studio. Va solo en `.env`, que está excluido en `.gitignore` y **nunca** se sube al repositorio. |

## Ejecutar

Todos los comandos se ejecutan **desde la raíz del proyecto** y con el entorno virtual activo (debe verse `(.venv)` al inicio de la línea).

| Comando | Qué hace |
|---|---|
| `python main.py` | Tutor con una duda de ejemplo: muestra el eje, la pista y el costo |
| `python main.py "¿Cómo calculo el 15 % de 8.000?"` | Lo mismo, con tu propia duda |
| `python src/consumir_gemini.py` | Prueba mínima de conexión con Gemini |
| `python -m prompts.test_consistencia` | Corre el banco de prompts 5 veces por prompt y regenera `prompts/registro_resultados.json` |
| `python -m docs.medir_modelos` | Vuelve a medir latencia, costo y calidad de los modelos candidatos |

Salida esperada de `python main.py` (el texto exacto cambia en cada ejecución):

```text
Duda del estudiante: No entiendo cómo resolver 2(x - 3) = 4x + 2. ¿Me ayudas?
Eje PAES M1: algebra_y_funciones (confianza 0.99)
Respuesta del modelo (pista): Primero, aplica la propiedad distributiva en el lado izquierdo...
Concepto clave: Ecuación lineal de primer grado · Dificultad: baja
Costo estimado de las 2 peticiones: 0.000336 USD
Proceso terminado sin errores.
```

Si algo falla (llave inválida, sin conexión, cuota agotada, modelo saturado), el programa muestra `No se pudo completar la operación:` con el motivo, sin traceback. Un error **429** o **503** es temporal: espera un momento y vuelve a intentarlo.

## Estructura

```text
├── main.py                        punto de entrada de la miniaplicación
├── src/
│   └── consumir_gemini.py         armar_peticion, enviar_peticion, extraer_texto,
│                                  parsear_respuesta_json, calcular_costo
├── prompts/
│   ├── banco.py                   banco de 3 prompts de sistema (con su estructura JSON esperada)
│   ├── test_consistencia.py       prueba de consistencia contra la API real
│   ├── registro_resultados.json   registro generado por la prueba
│   └── RESULTADOS.md              resumen y observaciones
├── docs/
│   ├── diagrama_arquitectura.md   diagrama del flujo (Mermaid)
│   ├── decision-arquitectura.md   elección de modelo con datos reales
│   ├── medir_modelos.py           script de medición de modelos
│   ├── resultados_medicion_modelos.json
│   ├── evidencia_peticion_autenticada.txt
│   └── evidencia_b7_pruebas_errores.txt
├── tests/                         pruebas automatizadas (Módulo 2)
├── requirements.txt               dependencias con versión exacta
└── .env.example                   plantilla de variables de entorno (sin valores reales)
```

## Decisiones técnicas

- **Modelo:** `gemini-3.5-flash-lite`, elegido con datos de latencia, costo y calidad. Ver [docs/decision-arquitectura.md](docs/decision-arquitectura.md).
- **Arquitectura:** ver [docs/diagrama_arquitectura.md](docs/diagrama_arquitectura.md).
- **Llamada a la API REST directa** con `requests`. La llave viaja en el header `x-goog-api-key` y no en la URL, para que no aparezca en mensajes de error. Todas las peticiones usan `timeout=30`.
- **Errores:** `armar_peticion` valida la entrada (`ValueError`). `enviar_peticion` maneja conexión, tiempo límite, códigos HTTP distintos de 200 y JSON inválido (`RuntimeError`). `extraer_texto` maneja el dato faltante y `parsear_respuesta_json` el JSON incompleto del modelo.
- **Privacidad:** el proyecto usa la capa gratuita de Gemini, donde Google puede usar lo enviado para mejorar sus productos. Por eso **nunca se envían datos personales de estudiantes**.

## Registro del ensayo de instalación limpia

*(se completa en la sección siguiente tras el ensayo)*

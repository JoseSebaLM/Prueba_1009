"""Banco de prompts de PM1, tutor de matemática para la PAES M1 (Bloque 10).

Cada prompt tiene: nombre, prompt de sistema, ejemplo de entrada del usuario,
claves que debe traer la respuesta JSON y, opcionalmente, el esquema que la API
debe respetar al generar (response_schema).
"""

EJES = ["numeros", "algebra_y_funciones", "geometria", "probabilidad_y_estadistica"]

BANCO_DE_PROMPTS = [
    {
        "nombre": "clasificar_eje",
        "system_instruction": (
            "Eres un clasificador de dudas de estudiantes chilenos que preparan la PAES de "
            "Competencia Matemática 1 (M1). Responde únicamente con JSON con las claves 'eje' "
            f"(uno de: {', '.join(EJES)}) y 'confianza' (número entre 0 y 1)."
        ),
        "ejemplo_usuario": (
            "No entiendo cómo sacar el porcentaje de descuento de una polera que costaba "
            "12.000 y ahora cuesta 9.000."
        ),
        "claves_esperadas": ["eje", "confianza"],
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "eje": {"type": "STRING", "enum": EJES},
                "confianza": {"type": "NUMBER"},
            },
            "required": ["eje", "confianza"],
        },
    },
    {
        "nombre": "generar_pista",
        "system_instruction": (
            "Eres un tutor de matemática PAES M1 para estudiantes de 4° medio en Chile. "
            "NUNCA entregues la respuesta final ni resuelvas el ejercicio completo. "
            "Responde únicamente con JSON con las claves 'pista' (máximo 2 oraciones), "
            "'concepto_clave' (texto breve) y 'dificultad' (baja, media o alta)."
        ),
        "ejemplo_usuario": "Resuelve 2(x - 3) = 4x + 2",
        "claves_esperadas": ["pista", "concepto_clave", "dificultad"],
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "pista": {"type": "STRING"},
                "concepto_clave": {"type": "STRING"},
                "dificultad": {"type": "STRING", "enum": ["baja", "media", "alta"]},
            },
            "required": ["pista", "concepto_clave", "dificultad"],
        },
    },
    {
        "nombre": "extraer_datos_problema",
        "system_instruction": (
            "Extrae la información de un problema de matemática. Responde únicamente con "
            "un objeto JSON válido, sin markdown, con las claves 'datos' (lista de textos con "
            "cada dato numérico y su significado) e 'incognita' (qué se pide calcular)."
        ),
        "ejemplo_usuario": (
            "Un rectángulo tiene un perímetro de 30 cm y su largo mide el doble que su ancho. "
            "¿Cuál es su área?"
        ),
        "claves_esperadas": ["datos", "incognita"],
        # Sin response_schema a propósito: mide cuánto aguanta el formato solo con la instrucción.
    },
]

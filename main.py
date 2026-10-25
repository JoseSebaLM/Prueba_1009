"""Punto de entrada de PM1: tutor de matemática PAES M1 (miniaplicación del Gate 1).

Recibe la duda de un estudiante, la clasifica por eje de la PAES M1 y genera una
pista que no resuelve el ejercicio. Muestra también el costo estimado de las peticiones.

Uso (desde la raíz del proyecto):
    python main.py                                  # usa una duda de ejemplo
    python main.py "¿Cómo despejo x en 3x + 5 = 20?"
"""

import sys

from prompts.banco import BANCO_DE_PROMPTS
from src.consumir_gemini import (
    PRECIO_ENTRADA,
    PRECIO_SALIDA,
    armar_peticion,
    calcular_costo,
    enviar_peticion,
    extraer_texto,
    parsear_respuesta_json,
)

DUDA_DE_EJEMPLO = "No entiendo cómo resolver 2(x - 3) = 4x + 2. ¿Me ayudas?"
PROMPTS = {prompt["nombre"]: prompt for prompt in BANCO_DE_PROMPTS}


def consultar_con_prompt(nombre_prompt, duda):
    """Envía la duda con un prompt del banco y devuelve (respuesta como dict, costo en USD)."""
    prompt = PROMPTS[nombre_prompt]
    url, encabezados, cuerpo = armar_peticion(duda, prompt["system_instruction"], prompt.get("response_schema"))
    datos = enviar_peticion(url, encabezados, cuerpo)
    respuesta = parsear_respuesta_json(extraer_texto(datos), prompt["claves_esperadas"])
    return respuesta, calcular_costo(datos, PRECIO_ENTRADA, PRECIO_SALIDA)


def main():
    duda = " ".join(sys.argv[1:]) or DUDA_DE_EJEMPLO
    print("Duda del estudiante:", duda)
    try:
        clasificacion, costo_clasificacion = consultar_con_prompt("clasificar_eje", duda)
        pista, costo_pista = consultar_con_prompt("generar_pista", duda)
    except (ValueError, RuntimeError) as error:
        print("No se pudo completar la operación:", error)
        sys.exit(1)

    print(f"Eje PAES M1: {clasificacion['eje']} (confianza {clasificacion['confianza']:.2f})")
    print(f"Respuesta del modelo (pista): {pista['pista']}")
    print(f"Concepto clave: {pista['concepto_clave']} · Dificultad: {pista['dificultad']}")
    print(f"Costo estimado de las 2 peticiones: {costo_clasificacion + costo_pista:.6f} USD")
    print("Proceso terminado sin errores.")


if __name__ == "__main__":
    main()

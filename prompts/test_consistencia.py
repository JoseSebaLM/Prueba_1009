"""Corre cada prompt del banco varias veces y registra cuántas respuestas fueron válidas (Bloque 10).

Ejecutar desde la raíz del proyecto:  python -m prompts.test_consistencia
Genera prompts/registro_resultados.json.
"""

import json
import time
from datetime import datetime
from pathlib import Path

from prompts.banco import BANCO_DE_PROMPTS
from src.consumir_gemini import MODELO, armar_peticion, enviar_peticion, extraer_texto, parsear_respuesta_json

INTENTOS = 5  # el mínimo de la actividad es 3
PAUSA_SEGUNDOS = 2  # espaciar las llamadas para no gatillar el error 429


def probar_prompt(prompt):
    """Ejecuta un prompt INTENTOS veces y devuelve el conteo de éxitos y el motivo de cada fallo."""
    exitos = 0
    fallos = []
    for intento in range(INTENTOS):
        try:
            url, encabezados, cuerpo = armar_peticion(
                prompt["ejemplo_usuario"], prompt["system_instruction"], prompt.get("response_schema")
            )
            texto = extraer_texto(enviar_peticion(url, encabezados, cuerpo))
            parsear_respuesta_json(texto, prompt["claves_esperadas"])
            exitos += 1
        except ValueError as error:  # JSON inválido o claves faltantes: falla del prompt
            fallos.append({"intento": intento + 1, "tipo": "formato", "motivo": str(error)})
            print(f"  {prompt['nombre']} intento {intento + 1} falló (formato): {error}")
        except RuntimeError as error:  # red, cuota o error HTTP: falla del servicio, no del prompt
            fallos.append({"intento": intento + 1, "tipo": "servicio", "motivo": str(error)[:120]})
            print(f"  {prompt['nombre']} intento {intento + 1} falló (servicio): {str(error)[:80]}")
        time.sleep(PAUSA_SEGUNDOS)
    return exitos, fallos


if __name__ == "__main__":
    registro = {"fecha": datetime.now().astimezone().isoformat(timespec="seconds"), "modelo": MODELO, "prompts": {}}
    for prompt in BANCO_DE_PROMPTS:
        exitos, fallos = probar_prompt(prompt)
        print(f"{prompt['nombre']}: {exitos}/{INTENTOS} respuestas válidas")
        registro["prompts"][prompt["nombre"]] = {
            "exitos": exitos,
            "intentos": INTENTOS,
            "consistencia": f"{exitos / INTENTOS:.0%}",
            "usa_response_schema": "response_schema" in prompt,
            "fallos": fallos,
        }

    ruta = Path(__file__).parent / "registro_resultados.json"
    ruta.write_text(json.dumps(registro, indent=2, ensure_ascii=False), encoding="utf-8")
    print("Registro guardado en", ruta)

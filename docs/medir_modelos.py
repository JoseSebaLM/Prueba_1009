"""Compara dos modelos candidatos de Gemini por latencia, costo y calidad (Bloque 9).

Ejecutar desde la raíz del proyecto:  python -m docs.medir_modelos
Guarda los resultados en docs/resultados_medicion_modelos.json.
"""

import json
import time
from datetime import datetime
from pathlib import Path

from src.consumir_gemini import armar_peticion, calcular_costo, enviar_peticion, extraer_texto

# Precios de pago en USD por 1 millón de tokens (ai.google.dev/gemini-api/docs/pricing, consultada 2026-10-25)
MODELOS = {
    "gemini-3.5-flash-lite": {"entrada": 0.30, "salida": 2.50},
    "gemini-3.6-flash": {"entrada": 0.75, "salida": 3.75},
    "gemini-3.8-flash": {"entrada": 0.75, "salida": 3.75},
}

PREGUNTA_LATENCIA = "Un alumno pregunta: ¿cómo despejo x en 3x + 5 = 20? Dale una pista sin resolverlo."
REPETICIONES = 4

PREGUNTAS_CALIDAD = [
    {
        "eje": "algebra_y_funciones",
        "pregunta": "Soy estudiante de 4° medio. ¿Cómo despejo x en 2(x - 3) = 4x + 2? Dame solo una pista, sin resolverlo.",
        "criterio": "Da una pista útil (distribuir el 2) y NO entrega el resultado x = -4.",
    },
    {
        "eje": "numeros",
        "pregunta": "Una polera costaba $12.000 y ahora cuesta $9.000. ¿Qué porcentaje de descuento tiene? Explícalo en pocos pasos.",
        "criterio": "Resultado correcto: 25 %, con procedimiento claro.",
    },
    {
        "eje": "probabilidad_y_estadistica",
        "pregunta": "Si lanzo dos dados, ¿cuál es la probabilidad de que la suma sea 7? Explícalo en pocos pasos.",
        "criterio": "Resultado correcto: 6/36 = 1/6, con los 6 casos favorables.",
    },
]

PAUSA_SEGUNDOS = 2


def consultar(pregunta, modelo, precios):
    """Hace una petición y devuelve latencia, tokens, costo y texto; o el error si falló."""
    url, encabezados, cuerpo = armar_peticion(pregunta, modelo=modelo)
    inicio = time.perf_counter()
    try:
        datos = enviar_peticion(url, encabezados, cuerpo)
        texto = extraer_texto(datos)
    except RuntimeError as error:
        return {"ok": False, "error": str(error)[:200], "latencia_s": round(time.perf_counter() - inicio, 2)}
    latencia = time.perf_counter() - inicio
    uso = datos["usageMetadata"]
    costo = calcular_costo(datos, precios["entrada"] / 1_000_000, precios["salida"] / 1_000_000)
    return {
        "ok": True,
        "latencia_s": round(latencia, 2),
        "tokens_entrada": uso.get("promptTokenCount", 0),
        "tokens_salida": uso.get("candidatesTokenCount", 0),
        "tokens_pensamiento": uso.get("thoughtsTokenCount", 0),
        "costo_usd": round(costo, 8),
        "texto": texto.strip(),
    }


def medir_modelo(modelo, precios):
    """Mide latencia promedio con REPETICIONES y responde las preguntas de calidad."""
    mediciones = []
    for i in range(REPETICIONES):
        resultado = consultar(PREGUNTA_LATENCIA, modelo, precios)
        estado = f"{resultado['latencia_s']:.2f} s" if resultado["ok"] else f"FALLÓ ({resultado['error'][:60]})"
        print(f"  {modelo} latencia {i + 1}/{REPETICIONES}: {estado}")
        mediciones.append(resultado)
        time.sleep(PAUSA_SEGUNDOS)

    exitosas = [m for m in mediciones if m["ok"]]
    resumen = {
        "peticiones_exitosas": f"{len(exitosas)}/{REPETICIONES}",
        "latencia_promedio_s": round(sum(m["latencia_s"] for m in exitosas) / len(exitosas), 2) if exitosas else None,
        "costo_promedio_usd": round(sum(m["costo_usd"] for m in exitosas) / len(exitosas), 8) if exitosas else None,
        "tokens_salida_promedio": round(sum(m["tokens_salida"] + m["tokens_pensamiento"] for m in exitosas) / len(exitosas)) if exitosas else None,
    }

    calidad = []
    for caso in PREGUNTAS_CALIDAD:
        resultado = consultar(caso["pregunta"], modelo, precios)
        print(f"  {modelo} calidad [{caso['eje']}]: {'ok' if resultado['ok'] else 'FALLÓ'}")
        calidad.append({**caso, **resultado})
        time.sleep(PAUSA_SEGUNDOS)

    return {"precios_usd_por_millon": precios, "resumen": resumen, "mediciones_latencia": mediciones, "calidad": calidad}


if __name__ == "__main__":
    resultados = {
        "fecha": datetime.now().astimezone().isoformat(timespec="seconds"),
        "pregunta_latencia": PREGUNTA_LATENCIA,
        "modelos": {},
    }
    for modelo, precios in MODELOS.items():
        print(f"Midiendo {modelo}...")
        resultados["modelos"][modelo] = medir_modelo(modelo, precios)
        print(f"  resumen: {resultados['modelos'][modelo]['resumen']}\n")

    ruta = Path(__file__).parent / "resultados_medicion_modelos.json"
    ruta.write_text(json.dumps(resultados, indent=2, ensure_ascii=False), encoding="utf-8")
    print("Resultados guardados en", ruta)

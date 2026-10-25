"""Consulta a Gemini y devuelve el texto generado, con validación y manejo de errores."""

import json
import os
import re

import requests
from dotenv import load_dotenv

load_dotenv()  # lee el archivo .env de la raíz del proyecto

MODELO = "gemini-3.5-flash-lite"  # elegido en docs/decision-arquitectura.md
URL_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
# Precios de pago de MODELO en USD por token (ai.google.dev/gemini-api/docs/pricing, consultada 2026-10-25)
PRECIO_ENTRADA = 0.30 / 1_000_000
PRECIO_SALIDA = 2.50 / 1_000_000


def armar_peticion(pregunta, system_instruction=None, response_schema=None, modelo=MODELO):
    """Valida la pregunta y arma la URL, los encabezados y el cuerpo para generateContent.

    El prompt de sistema (system_instruction) y el esquema de salida JSON
    (response_schema) son opcionales: sin ellos, la petición es la misma de antes.
    """
    if not isinstance(pregunta, str) or not pregunta.strip():
        raise ValueError("La pregunta debe ser un texto no vacío.")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Falta GEMINI_API_KEY: revisa tu archivo .env en la raíz del proyecto.")
    url = f"{URL_BASE}/{modelo}:generateContent"
    encabezados = {"x-goog-api-key": api_key}  # la llave va en un header, no en la URL
    cuerpo = {"contents": [{"parts": [{"text": pregunta}]}]}
    if system_instruction:
        cuerpo["systemInstruction"] = {"parts": [{"text": system_instruction}]}  # camelCase exacto de la API
    if response_schema is not None:
        cuerpo["generationConfig"] = {
            "responseMimeType": "application/json",
            "responseSchema": response_schema,
        }
    return url, encabezados, cuerpo


def enviar_peticion(url, encabezados, cuerpo):
    """Envía la petición; maneja errores de conexión, de HTTP y de formato."""
    try:
        respuesta = requests.post(url, headers=encabezados, json=cuerpo, timeout=30)
    except requests.exceptions.ConnectionError as error:
        raise RuntimeError("No se pudo conectar con el servicio. Intenta de nuevo en unos segundos.") from error
    except requests.exceptions.Timeout as error:
        raise RuntimeError("El servicio tardó demasiado en responder. Intenta de nuevo.") from error
    if respuesta.status_code != 200:
        raise RuntimeError(f"La API respondió con error HTTP {respuesta.status_code}: {respuesta.text[:300]}")
    try:
        return respuesta.json()
    except requests.exceptions.JSONDecodeError as error:
        raise RuntimeError("La respuesta del servicio no llegó en formato JSON válido.") from error


def extraer_texto(datos):
    """Devuelve el texto generado; avisa con claridad si no está donde se esperaba.

    El modelo puede dividir la respuesta en varias partes, así que se unen todas
    las partes de texto (sin las de razonamiento interno, marcadas con "thought").
    """
    try:
        partes = datos["candidates"][0]["content"]["parts"]
    except (KeyError, IndexError) as error:
        raise RuntimeError(
            "La respuesta no trae el texto generado en candidates[0].content.parts."
        ) from error
    textos = [parte["text"] for parte in partes if "text" in parte and not parte.get("thought")]
    if not textos:
        raise RuntimeError("La respuesta llegó sin texto generado.")
    return "".join(textos)


def parsear_respuesta_json(texto, claves_requeridas):
    """Limpia marcas de markdown, convierte el texto a dict y valida las claves requeridas."""
    texto_limpio = texto.strip()
    texto_limpio = re.sub(r"^```(?:json)?\s*", "", texto_limpio)  # quita ``` o ```json del inicio
    texto_limpio = re.sub(r"\s*```$", "", texto_limpio)  # quita ``` del final
    try:
        datos = json.loads(texto_limpio)
    except json.JSONDecodeError as error:
        raise ValueError("La respuesta del modelo no es JSON válido.") from error
    if not isinstance(datos, dict):
        raise ValueError("La respuesta del modelo es JSON, pero no es un objeto con claves.")
    faltantes = [clave for clave in claves_requeridas if clave not in datos]
    if faltantes:
        raise ValueError(f"A la respuesta le faltan las claves: {faltantes}")
    return datos


def calcular_costo(datos, precio_entrada, precio_salida):
    """Calcula el costo en USD de una respuesta a partir de usageMetadata.

    Los precios se reciben como parámetros (USD por token) porque cambian según
    el modelo y la fecha. Los tokens de pensamiento (thoughtsTokenCount) se
    cobran como salida, así que se suman a candidatesTokenCount.
    """
    try:
        uso = datos["usageMetadata"]
        tokens_entrada = uso["promptTokenCount"]
    except KeyError as error:
        raise RuntimeError("La respuesta no trae usageMetadata.promptTokenCount para calcular el costo.") from error
    tokens_salida = uso.get("candidatesTokenCount", 0) + uso.get("thoughtsTokenCount", 0)
    return tokens_entrada * precio_entrada + tokens_salida * precio_salida


def obtener_dato_de_prueba(pregunta):
    """Función principal: orquesta armar -> enviar -> extraer."""
    url, encabezados, cuerpo = armar_peticion(pregunta)
    datos = enviar_peticion(url, encabezados, cuerpo)
    return extraer_texto(datos)


if __name__ == "__main__":
    try:
        print(obtener_dato_de_prueba("Confirma en una frase corta que esta conexión funciona."))
    except (ValueError, RuntimeError) as error:
        print("No se pudo completar la operación:", error)

"""Consulta a Gemini y devuelve el texto generado, con validación y manejo de errores."""

import os

import requests
from dotenv import load_dotenv

load_dotenv()  # lee el archivo .env de la raíz del proyecto

MODELO = "gemini-3.5-flash-lite"  # nombre exacto del modelo, confirmado en AI Studio
URL_BASE = "https://generativelanguage.googleapis.com/v1beta/models"


def armar_peticion(pregunta):
    """Valida la pregunta y arma la URL, los encabezados y el cuerpo para generateContent."""
    if not isinstance(pregunta, str) or not pregunta.strip():
        raise ValueError("La pregunta debe ser un texto no vacío.")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Falta GEMINI_API_KEY: revisa tu archivo .env en la raíz del proyecto.")
    url = f"{URL_BASE}/{MODELO}:generateContent"
    encabezados = {"x-goog-api-key": api_key}  # la llave va en un header, no en la URL
    cuerpo = {"contents": [{"parts": [{"text": pregunta}]}]}
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
    """Devuelve el texto generado; avisa con claridad si no está donde se esperaba."""
    try:
        return datos["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError) as error:
        raise RuntimeError(
            "La respuesta no trae el texto generado en candidates[0].content.parts[0].text."
        ) from error


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

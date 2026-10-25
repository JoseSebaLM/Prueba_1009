"""Consulta a Gemini y devuelve el texto generado (versión refactorizada)."""

import os

import requests
from dotenv import load_dotenv

load_dotenv()  # lee el archivo .env de la raíz del proyecto

MODELO = "gemini-3.5-flash-lite"  # nombre exacto del modelo, confirmado en AI Studio
URL_BASE = "https://generativelanguage.googleapis.com/v1beta/models"


def armar_peticion(pregunta):
    """Arma la URL, los encabezados y el cuerpo para generateContent."""
    url = f"{URL_BASE}/{MODELO}:generateContent"
    encabezados = {"x-goog-api-key": os.getenv("GEMINI_API_KEY")}  # la llave va en un header, no en la URL
    cuerpo = {"contents": [{"parts": [{"text": pregunta}]}]}
    return url, encabezados, cuerpo


def enviar_peticion(url, encabezados, cuerpo):
    """Envía la petición y devuelve la respuesta convertida a dict."""
    respuesta = requests.post(url, headers=encabezados, json=cuerpo, timeout=30)
    return respuesta.json()


def extraer_texto(datos):
    """Devuelve el texto generado que viene dentro de la respuesta."""
    return datos["candidates"][0]["content"]["parts"][0]["text"]


def obtener_dato_de_prueba(pregunta):
    """Función principal: orquesta armar -> enviar -> extraer."""
    url, encabezados, cuerpo = armar_peticion(pregunta)
    datos = enviar_peticion(url, encabezados, cuerpo)
    return extraer_texto(datos)


if __name__ == "__main__":
    print(obtener_dato_de_prueba("Confirma en una frase corta que esta conexión funciona."))

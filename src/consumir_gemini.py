"""Primera versión: consulta a Gemini y devuelve el texto generado."""

import os

import requests
from dotenv import load_dotenv

load_dotenv()  # lee el archivo .env de la raíz del proyecto

MODELO = "gemini-3.5-flash-lite"  # nombre exacto del modelo, confirmado en AI Studio
URL_BASE = "https://generativelanguage.googleapis.com/v1beta/models"


def obtener_dato_de_prueba(pregunta):
    api_key = os.getenv("GEMINI_API_KEY")
    url = f"{URL_BASE}/{MODELO}:generateContent"
    encabezados = {"x-goog-api-key": api_key}  # la llave va en un header, no en la URL
    cuerpo = {"contents": [{"parts": [{"text": pregunta}]}]}
    respuesta = requests.post(url, headers=encabezados, json=cuerpo, timeout=30)
    datos = respuesta.json()  # JSON -> dict
    return datos["candidates"][0]["content"]["parts"][0]["text"]


if __name__ == "__main__":
    print(obtener_dato_de_prueba("Confirma en una frase corta que esta conexión funciona."))

"""
Modulo para la llamada al LLM usando Ollama local.
"""

import requests

OLLAMA_URL = "http://localhost:11434/api"
LLM_MODEL = "llama3.2:3b"


def generar_respuesta(prompt):
    """
    Envia el prompt al LLM y devuelve la respuesta.
    """
    try:
        respuesta = requests.post(
            f"{OLLAMA_URL}/generate",
            json={
                "model": LLM_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "num_predict": 500
                }
            },
            timeout=300
        )
        respuesta.raise_for_status()
        return respuesta.json()["response"]
    except requests.exceptions.ConnectionError:
        raise ConnectionError(
            "No se pudo conectar con Ollama. "
            "Asegurate de que Ollama esta corriendo: ollama serve"
        )
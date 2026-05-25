"""
Modulo para generacion de embeddings usando Ollama local.
"""

import requests

OLLAMA_URL = "http://localhost:11434/api"
EMBED_MODEL = "nomic-embed-text"


def embed(texto: str) -> list:
    """
    Genera un embedding vectorial para un texto dado.
    """
    try:
        respuesta = requests.post(
            f"{OLLAMA_URL}/embeddings",
            json={
                "model": EMBED_MODEL,
                "prompt": texto
            },
            timeout=60
        )
        respuesta.raise_for_status()
        return respuesta.json()["embedding"]
    except requests.exceptions.ConnectionError:
        raise ConnectionError(
            "No se pudo conectar con Ollama. "
            "Asegurate de que Ollama esta corriendo: ollama serve"
        )
"""Cliente HTTP para embeddings mediante Ollama.

Realiza llamadas secuenciales por cada fragmento de texto debido a que el endpoint 
``/api/embeddings`` de Ollama no gestiona procesamiento por lotes (batching) nativo. 
Utiliza la configuración centralizada del objeto global SETTINGS.
"""

from __future__ import annotations

import urllib3
import requests

from .config import SETTINGS


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def embed(text: str) -> list[float]:
    """Devuelve el embedding de ``text`` usando el modelo configurado."""
    response = requests.post(
        f"{SETTINGS.ollama_url}/embeddings",
        json={"model": SETTINGS.embed_model, "prompt": text},
        verify=SETTINGS.verify_ssl,
        timeout=60,
    )
    response.raise_for_status()
    payload = response.json()
    if "embedding" not in payload:
        raise RuntimeError(f"Respuesta inesperada del embedder: {payload}")
    return payload["embedding"]


def embed_many(texts: list[str]) -> list[list[float]]:
    """Procesa una lista de textos secuencialmente para obtener sus vectores."""
    return [embed(t) for t in texts]
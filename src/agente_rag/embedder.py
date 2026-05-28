"""Cliente HTTP para embeddings mediante Ollama.

Realiza llamadas secuenciales por cada fragmento de texto debido a que el endpoint 
``/api/embeddings`` de Ollama no gestiona procesamiento por lotes (batching) nativo. 
Utiliza la configuración centralizada del objeto global SETTINGS.
"""

from __future__ import annotations

import urllib3
import requests
from openai import OpenAI

from .config import SETTINGS


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def embed(text: str, servidor: str | None = None) -> list[float]:
    """Devuelve el embedding de ``text`` usando el modelo configurado."""
    if servidor == "poligpt":
        if not SETTINGS.poligpt_api_key:
            raise ValueError("Falta la variable de entorno POLIGPT_API_KEY para conectar con la API de la UPV.")
        client_api = OpenAI(api_key=SETTINGS.poligpt_api_key, base_url=SETTINGS.poligpt_base_url)
        res = client_api.embeddings.create(input=text, model=SETTINGS.embed_model)
        return res.data[0].embedding

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


def embed_many(texts: list[str], servidor: str | None = None) -> list[list[float]]:
    """Procesa una lista de textos secuencialmente para obtener sus vectores."""
    return [embed(t, servidor=servidor) for t in texts]
"""Cliente HTTP para generación con soporte dual (Ollama / PoliGPT) y captura de métricas.

Devuelve la respuesta del modelo junto con las 4 métricas exigidas para la banda 7:
- prompt_tokens
- output_tokens
- tokens_per_sec
- latency_s

Gestiona de manera transparente las llamadas locales a Ollama y las llamadas remotas 
a la infraestructura PoliGPT de la UPV utilizando el SDK oficial de OpenAI.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

import urllib3
import requests
from openai import OpenAI

from .config import SETTINGS


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@dataclass
class Generation:
    text: str
    prompt_tokens: int
    output_tokens: int
    tokens_per_sec: float
    latency_s: float
    model: str


def generate(prompt: str, *, temperature: float = 0.2, model: str | None = None, servidor: str | None = None) -> Generation:
    """Genera una respuesta a partir del prompt usando enrutamiento local o remoto."""
    chosen_model = model or SETTINGS.llm_model
    
    # Enrutamiento basado en la variable de control explícita 'servidor'
    if servidor is not None:
        es_modelo_poligpt = (servidor == "poligpt")
    else:
        # Fallback por si se llama directamente sin servidor
        es_modelo_poligpt = any(keyword in chosen_model.lower() for keyword in ["gpt", "claude", "mini", "gemma3"])
    
    t0 = time.time()
    
    if es_modelo_poligpt:
        # --- ENRUTAMIENTO POLIGPT (API OpenAI-Compatible de la UPV) ---
        if not SETTINGS.poligpt_api_key:
            raise ValueError("Falta la variable de entorno POLIGPT_API_KEY para conectar con la API de la UPV.")
            
        client_api = OpenAI(api_key=SETTINGS.poligpt_api_key, base_url=SETTINGS.poligpt_base_url)
        
        res_llm = client_api.chat.completions.create(
            model=chosen_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )
        
        elapsed = time.time() - t0
        
        # Extracción de métricas desde la estructura nativa de OpenAI usage
        prompt_tokens = res_llm.usage.prompt_tokens if res_llm.usage else 0
        output_tokens = res_llm.usage.completion_tokens if res_llm.usage else 0
        texto_generado = res_llm.choices[0].message.content or ""
        tokens_per_sec = output_tokens / elapsed if elapsed > 0 else 0.0
        
    else:
        # --- ENRUTAMIENTO OLLAMA LOCAL ---
        response = requests.post(
            f"{SETTINGS.ollama_url}/generate",
            json={
                "model": chosen_model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": temperature},
            },
            verify=SETTINGS.verify_ssl,
            timeout=180,
        )
        elapsed = time.time() - t0
        response.raise_for_status()
        payload = response.json()

        texto_generado = payload["response"]
        prompt_tokens = int(payload.get("prompt_eval_count", 0))
        output_tokens = int(payload.get("eval_count", 0))
        eval_duration_ns = int(payload.get("eval_duration", 0))
        
        # Priorizar la duración exacta del servidor Ollama si está disponible
        if eval_duration_ns > 0:
            tokens_per_sec = output_tokens / (eval_duration_ns / 1e9)
        else:
            tokens_per_sec = output_tokens / elapsed if elapsed > 0 else 0.0

    return Generation(
        text=texto_generado,
        prompt_tokens=prompt_tokens,
        output_tokens=output_tokens,
        tokens_per_sec=round(tokens_per_sec, 2),
        latency_s=round(elapsed, 2),
        model=chosen_model,
    )
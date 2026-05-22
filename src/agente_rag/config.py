"""Carga de configuración desde entorno (.env soportado vía python-dotenv).

Centralizamos aquí la lectura de variables para que el resto del paquete no
toque ``os.environ`` directamente. Adaptado para el Asistente DNI Valencia.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def _bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "si", "sí"}


@dataclass(frozen=True)
class Settings:
    ollama_url: str
    llm_model: str
    embed_model: str
    verify_ssl: bool
    chroma_path: Path
    collection_name: str
    api_host: str
    api_port: int
    corpus_dir: Path
    
    # Añadimos las variables de PoliGPT requeridas para la Banda 7
    poligpt_api_key: str | None
    poligpt_base_url: str

    @classmethod
    def from_env(cls) -> Settings:
        repo_root = Path(__file__).resolve().parents[2]
        
        # 🔍 Intentamos detectar de manera inteligente el nombre de vuestra carpeta de textos
        ruta_corpus = repo_root / "base conocimiento"
        if not ruta_corpus.exists():
            ruta_corpus = repo_root / "base_conocimiento"
        if not ruta_corpus.exists():
            ruta_corpus = repo_root / "corpus" # Por si acaso

        return cls(
            ollama_url=os.getenv("OLLAMA_URL", "http://localhost:11434/api"),
            llm_model=os.getenv("LLM_MODEL", "llama3.2:3b"), # <-- Ajustado a vuestro LLM de desarrollo
            embed_model=os.getenv("EMBED_MODEL", "nomic-embed-text"),
            verify_ssl=_bool("VERIFY_SSL", True),
            chroma_path=Path(os.getenv("CHROMA_PATH", str(repo_root / "data" / "chroma"))),
            collection_name=os.getenv("COLLECTION_NAME", "dni_valencia_v3"), # <-- Colección limpia para DNI
            api_host=os.getenv("API_HOST", "127.0.0.1"),
            api_port=int(os.getenv("API_PORT", "8000")),
            corpus_dir=Path(os.getenv("CORPUS_DIR", str(ruta_corpus))), # <-- Apunta dinámicamente a vuestros .txt
            
            # Captura segura de credenciales de la UPV
            poligpt_api_key=os.getenv("POLIGPT_API_KEY"),
            poligpt_base_url=os.getenv("POLIGPT_BASE_URL", "https://api.poligpt.upv.es/v1")
        )


SETTINGS = Settings.from_env()
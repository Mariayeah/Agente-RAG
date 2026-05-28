"""Troceo del corpus adaptado para el Asistente DNI Valencia.

Usamos ``RecursiveCharacterTextSplitter`` con parámetros optimizados (1000, 250)
para garantizar que las parejas de Pregunta/Respuesta del corpus de DNI Valencia 
no queden truncadas, manteniendo la trazabilidad al archivo de origen (Banda 6).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter


@dataclass
class Chunk:
    id: str
    text: str
    source: str
    chunk_index: int


def load_corpus(corpus_dir: Path) -> list[dict]:
    """Carga todos los .txt de ``corpus_dir`` en memoria."""
    if not corpus_dir.exists():
        raise FileNotFoundError(f"Corpus no encontrado en {corpus_dir}")
    docs = []
    for path in sorted(corpus_dir.glob("*.txt")):
        docs.append({"name": path.name, "text": path.read_text(encoding="utf-8")})
    if not docs:
        raise RuntimeError(f"No hay archivos .txt válidos en {corpus_dir}")
    return docs


def split_documents(
    docs: list[dict],
    *,
    chunk_size: int = 1000,  # <-- Optimizado para el formato de preguntas de DNI
    chunk_overlap: int = 250, # <-- Proporción del 25% para asegurar el contexto continuo
) -> list[Chunk]:
    """Trocea cada documento conservando trazabilidad al archivo origen."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    chunks: list[Chunk] = []
    for doc in docs:
        for i, piece in enumerate(splitter.split_text(doc["text"])):
            chunks.append(
                Chunk(
                    id=f"{doc['name']}__chunk_{i:04d}",
                    text=piece,
                    source=doc["name"],
                    chunk_index=i,
                )
            )
    return chunks
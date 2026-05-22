"""Indexación y retrieval con ChromaDB persistente adaptado para DNI Valencia.

ChromaDB en disco (``persistent_client``) asegura que el índice vectorial sobreviva 
entre ejecuciones, reduciendo el tiempo de arranque de ``consultar.py`` a < 2 segundos.
Implementa inversión de distancia a score para facilitar la evaluación (Banda 7).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import chromadb

from .chunker import Chunk
from .config import SETTINGS
from .embedder import embed


@dataclass
class RetrievedChunk:
    source: str
    text: str
    score: float
    chunk_id: str


def _client(path: Path) -> chromadb.api.ClientAPI:
    """Garantiza la existencia del directorio y levanta el cliente persistente."""
    path.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(path))


def build_index(chunks: list[Chunk]) -> int:
    """Construye (o reemplaza) la colección física con vuestros chunks de DNI.

    Forzamos métrica coseno (``hnsw:space=cosine``) para que las distancias estén
    acotadas y los scores sean perfectamente interpretables y comparables.
    """
    client = _client(SETTINGS.chroma_path)
    
    # Si la colección antigua de DNI ya existe en disco, la eliminamos para evitar duplicados residuales
    if SETTINGS.collection_name in [c.name for c in client.list_collections()]:
        client.delete_collection(SETTINGS.collection_name)
        
    col = client.create_collection(
        SETTINGS.collection_name,
        metadata={"hnsw:space": "cosine"},
    )
    
    # Ingesta masiva en la base de datos persistente
    col.add(
        ids=[c.id for c in chunks],
        embeddings=[embed(c.text) for c in chunks],
        documents=[c.text for c in chunks],
        metadatas=[{"source": c.source, "chunk_index": c.chunk_index} for c in chunks],
    )
    return col.count()


def _open_collection() -> chromadb.api.models.Collection.Collection:
    """Abre de forma segura la colección persistente configurada."""
    client = _client(SETTINGS.chroma_path)
    return client.get_collection(SETTINGS.collection_name)


def retrieve(question: str, *, k: int = 5) -> list[RetrievedChunk]:
    """Top-k retrieval semántico. Aplica la fórmula ``score = 1 - distance``."""
    col = _open_collection()
    q_emb = embed(question)
    
    if not q_emb:
        return []
        
    res = col.query(query_embeddings=[q_emb], n_results=k)
    out: list[RetrievedChunk] = []
    
    if res["ids"] and res["ids"][0]:
        for i in range(len(res["ids"][0])):
            distance = float(res["distances"][0][i])
            out.append(
                RetrievedChunk(
                    source=res["metadatas"][0][i]["source"],
                    text=res["documents"][0][i],
                    # Transformación formal: a menor distancia, mayor score de similitud
                    score=round(1.0 - distance, 4),
                    chunk_id=res["ids"][0][i],
                )
            )
    return out
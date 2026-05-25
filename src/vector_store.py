"""
Modulo para la gestion del vector store usando ChromaDB.
"""

import chromadb
from embeddings import embed  # Import directo, no relativo con punto


def crear_vector_store(chunks):
    """
    Crea un vector store con ChromaDB e indexa todos los chunks.
    """
    cliente = chromadb.Client()
    coleccion = cliente.create_collection("dni_knowledge")

    total = len(chunks)

    for i, chunk in enumerate(chunks):
        coleccion.add(
            ids=[chunk["id"]],
            embeddings=[embed(chunk["texto"])],
            documents=[chunk["texto"]],
            metadatas=[{"fuente": chunk["fuente"]}]
        )

        if (i + 1) % 50 == 0 or (i + 1) == total:
            print(f"  - Indexados {i + 1}/{total} chunks")

    return coleccion
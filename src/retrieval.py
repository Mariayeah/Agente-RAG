"""
Modulo para la recuperacion de chunks relevantes.
"""

from embeddings import embed  # Import directo


def recuperar_chunks(coleccion, pregunta, k=5):
    """
    Recupera los k chunks mas similares a la pregunta.
    """
    q_emb = embed(pregunta)
    resultados = coleccion.query(query_embeddings=[q_emb], n_results=k)

    chunks = resultados["documents"][0]
    fuentes = [m["fuente"] for m in resultados["metadatas"][0]]

    return chunks, fuentes
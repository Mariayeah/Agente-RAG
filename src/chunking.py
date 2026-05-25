"""
Modulo para la division de documentos en chunks.
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunkear_documentos(documentos, chunk_size=500, chunk_overlap=100):
    """
    Divide una lista de documentos en chunks.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\nQ:", "\n\nA:", "\n\n", "\n", ".", " ", ""]
    )

    todos_chunks = []

    for doc in documentos:
        pedazos = splitter.split_text(doc["texto"])

        for i, pedazo in enumerate(pedazos):
            todos_chunks.append({
                "id": f"{doc['nombre']}_chunk_{i:03d}",
                "texto": pedazo,
                "fuente": doc["nombre"]
            })

        print(f"  - {doc['nombre']}: {len(pedazos)} chunks")

    return todos_chunks
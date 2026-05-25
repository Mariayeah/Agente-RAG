"""
Punto de entrada del agente RAG para la asociacion DNI.
Banda 5 - Minimo para aprobar.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from carga_corpus import cargar_corpus
from chunking import chunkear_documentos
from vector_store import crear_vector_store
from retrieval import recuperar_chunks
from prompt import build_prompt
from llm import generar_respuesta


# ============================================================
# INICIALIZACION (una sola vez al importar)
# ============================================================

BASE_DIR = Path(__file__).parent.absolute()
RUTA_CORPUS = BASE_DIR / "base conocimiento"

print(f"Cargando corpus desde: {RUTA_CORPUS}")
documentos = cargar_corpus(str(RUTA_CORPUS))

print("Chunking...")
chunks = chunkear_documentos(documentos, chunk_size=500, chunk_overlap=100)

print("Indexando en vector store...")
coleccion = crear_vector_store(chunks)

print(f"Agente listo. Total chunks: {len(chunks)}\n")


# ============================================================
# FUNCION PRINCIPAL
# ============================================================

def consultar(pregunta: str, conversation_id: str = None) -> dict:
    """
    Funcion principal del agente.
    Usa k=10 para mejor recuperacion de contexto.
    """
    # Recuperar chunks (k=10 para mas contexto)
    chunks_rec, fuentes = recuperar_chunks(coleccion, pregunta, k=10)
    
    # Construir prompt usando el template mejorado
    prompt = build_prompt(pregunta, chunks_rec, fuentes)
    
    # Generar respuesta con LLM
    respuesta = generar_respuesta(prompt)
    
    # Fuentes unicas
    fuentes_unicas = list(set(fuentes))
    
    return {
        "respuesta": respuesta,
        "fuentes": fuentes_unicas,
        "chunks": chunks_rec,
        "metricas": None,
        "trazas": None
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python consultar.py \"<pregunta>\"")
        sys.exit(1)
    
    pregunta = " ".join(sys.argv[1:])
    resultado = consultar(pregunta)
    
    print("\n" + "=" * 60)
    print("RESPUESTA:")
    print("=" * 60)
    print(resultado["respuesta"])
    print("\n" + "=" * 60)
    print("FUENTES:")
    print("=" * 60)
    for f in resultado["fuentes"]:
        print(f"  - {f}")
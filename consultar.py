"""Punto de entrada del contrato (Opción A — módulo Python)."""

from __future__ import annotations
import json
import sys
from pathlib import Path
import requests
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Configuración de Ollama Local
OLLAMA_URL = "http://localhost:11434/api"
LLM_MODEL = "llama3.2:3b"  # El modelo que descargaste
EMBED_MODEL = "nomic-embed-text" # Modelo de embeddings obligatorio

# --- 1. Inicialización y carga en ChromaDB (Fase Offline) ---
def inicializar_vector_store():
    # Iniciamos ChromaDB en memoria (para persistencia en disco se usaría PersistentClient)
    client = chromadb.Client()
    
    # Usamos dni_v2 para forzar a ChromaDB a crear una colección nueva con los chunks mejorados
    col = client.get_or_create_collection("dni_v2")
    
    # Si la colección ya tiene documentos, no volvemos a procesarlos
    if col.count() > 0:
        return col

    # Cargar los 16.txt desde la carpeta base_conocimiento
    docs = []
    base_path = Path("base conocimiento")
    if not base_path.exists():
        print(f"Advertencia: No se encontró la carpeta {base_path}", file=sys.stderr)
        return col

    for path in sorted(base_path.glob("*.txt")):
        docs.append({"name": path.name, "text": path.read_text(encoding="utf-8")})
        
    # Chunking Mejorado: fragmentos más grandes (1000) para no cortar las preguntas y respuestas
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=250)
    chunks = []
    for doc in docs:
        for i, c in enumerate(splitter.split_text(doc["text"])):
            # Guardamos el nombre del archivo fuente en los metadatos (Para la Banda 6)
            chunks.append({"id": f"{doc['name']}_{i}", "text": c, "source": doc["name"]})
            
    # Función auxiliar para vectorizar texto con Ollama
    def embed(text):
        r = requests.post(f"{OLLAMA_URL}/embeddings", json={"model": EMBED_MODEL, "prompt": text})
        return r.json().get("embedding", [])

    # Insertamos los chunks y sus vectores en ChromaDB
    if chunks:
        # Extraemos listas paralelas para Chroma
        ids = [ch["id"] for ch in chunks]
        textos = [ch["text"] for ch in chunks]
        metadatos = [{"source": ch["source"]} for ch in chunks]
        vectores = [embed(t) for t in textos]

        col.add(ids=ids, embeddings=vectores, documents=textos, metadatas=metadatos)
        
    return col

# Instanciamos la base de datos al cargar el módulo
coleccion_dni = inicializar_vector_store()

def embed_query(text):
    r = requests.post(f"{OLLAMA_URL}/embeddings", json={"model": EMBED_MODEL, "prompt": text})
    return r.json().get("embedding", [])

# --- 2. Función del Contrato (Fase Online) ---
def consultar(pregunta: str, conversation_id: str | None = None) -> dict:
    """Función obligatoria del contrato (enunciado §9, opción A)."""
    
    # 1. Convertir la pregunta a vector
    q_emb = embed_query(pregunta)
    
    # 2. Buscar los 5 chunks más relevantes
    res = coleccion_dni.query(query_embeddings=[q_emb], n_results=5)
    
    documentos_recuperados = res["documents"][0] if res.get("documents") else []
    metadatos_recuperados = res["metadatas"][0] if res.get("metadatas") else []
    
    contexto = "\n\n".join(documentos_recuperados)
    
    # 3. Construir Prompt estricto anti-alucinaciones (Para la Banda 5)
    prompt = f"""Eres un asistente de la asociación DNI. Responde SOLO usando el contexto. Si no está, di que no lo sabes.
CONTEXTO:
{contexto}

PREGUNTA: {pregunta}
RESPUESTA:"""

    # 4. Llamar al LLM local (Ollama)
    r = requests.post(f"{OLLAMA_URL}/generate", json={
        "model": LLM_MODEL, 
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.2}
    })
    
    respuesta_llm = r.json().get("response", "Error de conexión con el LLM.")
    
    # 5. Extraer fuentes únicas de los metadatos (Para la Banda 6)
    fuentes = list(set([m["source"] for m in metadatos_recuperados]))

    # Retornar el diccionario EXACTO que pide el contrato
    return {
        "respuesta": respuesta_llm,
        "fuentes": fuentes,
        "chunks": documentos_recuperados,
        "metricas": None,
        "trazas": None
    }

def _main(argv: list[str]) -> int:
    if len(argv) < 2:
        print('Uso: python consultar.py "<pregunta>"', file=sys.stderr)
        return 2
    pregunta = " ".join(argv[1:])
    result = consultar(pregunta)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(_main(sys.argv))
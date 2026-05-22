"""Punto de entrada del contrato (Opción A — módulo Python)."""

from __future__ import annotations
import json
import sys
import os
from pathlib import Path
import requests
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from openai import OpenAI

# Cargar variables de entorno (.env)
load_dotenv()

# Configuración por defecto
SERVIDOR_LLM = "ollama_local" # Puede ser "ollama_local" o "poligpt"
OLLAMA_URL = "http://localhost:11434/api"
LLM_MODEL = "llama3.2:3b"  
EMBED_MODEL = "nomic-embed-text" 

# --- 1. Inicialización y carga en ChromaDB (Fase Offline) ---
def inicializar_vector_store():
    client = chromadb.Client()
    col = client.get_or_create_collection("dni_v2")
    
    if col.count() > 0:
        return col

    docs = []
    base_path = Path("base conocimiento")
    if not base_path.exists():
        print(f"Advertencia: No se encontró la carpeta {base_path}", file=sys.stderr)
        return col

    for path in sorted(base_path.glob("*.txt")):
        docs.append({"name": path.name, "text": path.read_text(encoding="utf-8")})
        
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=250)
    chunks = []
    for doc in docs:
        for i, c in enumerate(splitter.split_text(doc["text"])):
            chunks.append({"id": f"{doc['name']}_{i}", "text": c, "source": doc["name"]})
            
    def embed(text):
        r = requests.post(f"{OLLAMA_URL}/embeddings", json={"model": EMBED_MODEL, "prompt": text})
        return r.json().get("embedding", [])

    if chunks:
        ids = [ch["id"] for ch in chunks]
        textos = [ch["text"] for ch in chunks]
        metadatos = [{"source": ch["source"]} for ch in chunks]
        vectores = [embed(t) for t in textos]

        col.add(ids=ids, embeddings=vectores, documents=textos, metadatas=metadatos)
        
    return col

coleccion_dni = inicializar_vector_store()

def embed_query(text):
    r = requests.post(f"{OLLAMA_URL}/embeddings", json={"model": EMBED_MODEL, "prompt": text})
    return r.json().get("embedding", [])

# --- 2. Función del Contrato (Fase Online) ---
def consultar(pregunta: str, conversation_id: str | None = None) -> dict:
    """Función obligatoria del contrato (enunciado §9, opción A)."""
    
    q_emb = embed_query(pregunta)
    res = coleccion_dni.query(query_embeddings=[q_emb], n_results=5)
    
    documentos_recuperados = res["documents"][0] if res.get("documents") else []
    metadatos_recuperados = res["metadatas"][0] if res.get("metadatas") else []
    
    contexto = "\n\n".join(documentos_recuperados)
    
    prompt = f"""Eres un asistente de la asociación DNI. Responde SOLO usando el contexto. Si no está, di que no lo sabes.
CONTEXTO:
{contexto}

PREGUNTA: {pregunta}
RESPUESTA:"""

    respuesta_llm = "Error de conexión."

    try:
        # Llamar al LLM dependiendo del servidor elegido
        if SERVIDOR_LLM == "ollama_local":
            r = requests.post(f"{OLLAMA_URL}/generate", json={
                "model": LLM_MODEL, 
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.2}
            })
            respuesta_llm = r.json().get("response", "Error de conexión con el LLM local.")
            
        elif SERVIDOR_LLM == "poligpt":
            # Conexión a la API de la UPV usando la librería de OpenAI
            client = OpenAI(
                base_url=os.environ.get("POLIGPT_BASE_URL"),
                api_key=os.environ.get("POLIGPT_API_KEY")
            )
            resp = client.chat.completions.create(
                model=LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            respuesta_llm = resp.choices[0].message.content
            
    except Exception as e:
        respuesta_llm = f"Error en la generación: {str(e)}"
    
    fuentes = list(set([m["source"] for m in metadatos_recuperados]))

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
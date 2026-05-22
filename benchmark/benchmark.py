# scripts/build_index.py
import os
import shutil  # <-- IMPORTANTE: Añade esta librería nativa aquí arriba
from pathlib import Path
import requests
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "nomic-embed-text")
CHROMA_PATH = os.environ.get("CHROMA_PATH", "./data/chroma")
COLLECTION_NAME = os.environ.get("COLLECTION_NAME", "dni_valencia")

def build_vector_store():
    # 🔥 LIMPIEZA ABSOLUTA DE CACHÉ Y PERTENENCIAS ANTERIORES
    print("Vaciando base de datos anterior para evitar contaminación...")
    if os.path.exists(CHROMA_PATH):
        try:
            shutil.rmtree(CHROMA_PATH)
            print("🗑️ Carpeta de ChromaDB eliminada con éxito.")
        except Exception as e:
            print(f"⚠️ No se pudo borrar automáticamente por permisos: {e}")

    print("Cargando documentos de la asociación DNI...")
    docs = []
    corpus_path = Path("base_conocimiento")
    
    if not corpus_path.exists():
        print("❌ Error: No se encuentra la carpeta 'base_conocimiento'.")
        return

    for path in sorted(corpus_path.glob("*.txt")):
        docs.append({"name": path.name, "text": path.read_text(encoding="utf-8")})
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    
    chunks = []
    for doc in docs:
        split_texts = splitter.split_text(doc["text"])
        for i, text_chunk in enumerate(split_texts):
            chunks.append({
                "id": f"{doc['name']}_{i}",
                "text": text_chunk,
                "source": doc["name"]
            })

    # Ahora sí, creamos el cliente en una ruta completamente limpia
    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)

    print(f"Indexando {len(chunks)} fragmentos limpios en ChromaDB...")
    
    for ch in chunks:
        response = requests.post(
            f"{OLLAMA_URL}/embeddings",
            json={"model": EMBED_MODEL, "prompt": ch["text"]}
        )
        embedding = response.json()["embedding"]
        
        collection.add(
            ids=[ch["id"]],
            embeddings=[embedding],
            documents=[ch["text biographical"] if "text biographical" in ch else ch["text"]],
            metadatas=[{"source": ch["source"]}]
        )
    
    print("¡Base de conocimientos indexada desde cero con éxito! 🎉")

if __name__ == "__main__":
    build_vector_store()
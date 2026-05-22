# scripts/build_index.py
import os
from pathlib import Path
import requests
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

# 1. Cargar las variables de entorno del archivo .env que creamos
load_dotenv()

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "nomic-embed-text")
CHROMA_PATH = os.environ.get("CHROMA_PATH", "./data/chroma")
COLLECTION_NAME = os.environ.get("COLLECTION_NAME", "dni_valencia")

def build_vector_store():
    # 2. Cargar el corpus de la asociación DNI
    print("Cargando documentos de la asociación DNI...")
    docs = []
    corpus_path = Path("base conocimiento")
    
    if not corpus_path.exists():
        print("❌ Error: No se encuentra la carpeta 'base conocimiento'.")
        return

    for path in sorted(corpus_path.glob("*.txt")):
        docs.append({"name": path.name, "text": path.read_text(encoding="utf-8")})
    
    # 3. Configurar el Chunking (Banda 6: Justificar tamaño y overlap en el informe)
    # Usamos los valores recomendados por el manual técnico
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    
    chunks = []
    for doc in docs:
        split_texts = splitter.split_text(doc["text"])
        for i, text_chunk in enumerate(split_texts):
            chunks.append({
                "id": f"{doc['name']}_{i}",
                "text": text_chunk,
                "source": doc["name"] # Guardamos el origen para la Banda 6 (Citar fuentes)
            })

    # 4. Conectar con ChromaDB de forma PERSISTENTE en disco (Evita borrar los datos)
    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)

    # 5. Generar Embeddings e Indexar en la Base de Datos
    print(f"Indexando {len(chunks)} fragmentos en ChromaDB utilizando {EMBED_MODEL}...")
    
    for ch in chunks:
        # Llamada a Ollama local para vectorizar el texto
        response = requests.post(
            f"{OLLAMA_URL}/embeddings",
            json={"model": EMBED_MODEL, "prompt": ch["text"]}
        )
        embedding = response.json()["embedding"]
        
        # Añadir a la colección guardando el texto y los metadatas de origen
        collection.add(
            ids=[ch["id"]],
            embeddings=[embedding],
            documents=[ch["text"]],
            metadatas=[{"source": ch["source"]}] # Clave para poder citar el archivo después
        )
    
    print("¡Base de conocimientos indexada con éxito y guardada en disco! 🎉")

if __name__ == "__main__":
    build_vector_store()
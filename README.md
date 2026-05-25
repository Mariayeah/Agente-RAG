# Agente RAG - Asociacion DNI

## Descripcion

Agente conversacional para responder preguntas sobre la asociacion DNI (Damos Nuestra Ilusion) utilizando RAG (Retrieval-Augmented Generation).

## Requisitos

- Python 3.10 o superior
- Ollama instalado y corriendo
- Modelos descargados:
  - `llama3.2:3b` (LLM)
  - `nomic-embed-text` (embeddings)

## Instalacion

```bash
# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt

# Descargar modelos de Ollama
ollama pull llama3.2:3b
ollama pull nomic-embed-text

# Asegurar que Ollama esta corriendo
ollama serve
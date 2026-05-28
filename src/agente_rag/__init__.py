"""Agente RAG — Desarrollo del Asistente DNI Valencia.

Estructura del paquete modularizado (Siguiendo la plantilla oficial):
- config: Centralización de variables de entorno, constantes y rutas (.env).
- chunker: Carga de los 16 .txt del corpus de DNI Valencia y troceo adaptado.
- embedder: Cliente HTTP para embeddings mediante Ollama (nomic-embed-text).
- retriever: Inicialización de ChromaDB persistente y motor de búsqueda semántica.
- generator: Cliente HTTP para generación con soporte dual (Ollama / PoliGPT) y métricas.
- prompts: Diseño del prompt del sistema con instrucciones de control anti-alucinación.
- pipeline: Orquestador del flujo completo (Retrieval-Augmented Generation).
"""

__version__ = "1.0.0"
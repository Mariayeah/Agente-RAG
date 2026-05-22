"""Orquestador del flujo RAG (Pipeline del Agente): percibir → decidir → actuar.

Une los módulos de búsqueda semántica, construcción del prompt contextual y
generación de texto con métricas avanzadas, asegurando el cumplimiento estricto
del contrato de interfaz del enunciado §9 para el Asistente DNI Valencia.
"""

from __future__ import annotations

from .generator import generate
from .prompts import build_prompt
from .retriever import retrieve


def answer(
    question: str, 
    *, 
    k: int = 5, 
    conversation_id: str | None = None,
    model: str | None = None
) -> dict:
    """Responde a ``question`` siguiendo el contrato de interfaz oficial de la asignatura."""
    
    # 1. Fase de Retrieval: Recuperar los fragmentos de la base de datos persistente
    retrieved = retrieve(question, k=k)
    
    # 2. Fase de Prompteo: Insertar el contexto en la plantilla anti-alucinaciones
    prompt = build_prompt(question, retrieved)
    
    # 3. Fase de Generación: Llamada al LLM (Ollama o PoliGPT) pasando el modelo dinámico
    gen = generate(prompt, model=model)

    # 4. Construcción del contrato oficial con los campos exigidos
    return {
        "respuesta": gen.text.strip(),
        "fuentes": _unique_preserving_order(c.source for c in retrieved),
        "chunks": [
            {"source": c.source, "text": c.text, "score": c.score} for c in retrieved
        ],
        "metricas": {
            "prompt_tokens": gen.prompt_tokens,
            "output_tokens": gen.output_tokens,
            "tokens_per_sec": gen.tokens_per_sec,
            "latencia_s": gen.latency_s,
            "modelo": gen.model,
        },
        "trazas": None,
        "conversation_id": conversation_id,
    }


def _unique_preserving_order(items) -> list[str]:
    """Elimina duplicados de una lista manteniendo el orden de relevancia original."""
    seen: set[str] = set()
    out: list[str] = []
    for it in items:
        if it not in seen:
            seen.add(it)
            out.append(it)
    return out
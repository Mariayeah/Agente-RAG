"""Plantilla del prompt anti-alucinación adaptada para el Asistente DNI Valencia.

Mantiene los cinco bloques estructurales del profesor (rol + instrucciones + 
contexto + restricciones + formato) y la constante exacta de rechazo exigida 
para superar los tests automáticos de no-alucinación de la Banda 5.
"""

from __future__ import annotations

# Constante crítica: Los tests automáticos validan que se devuelva este texto exacto
REJECTION_PHRASE = "No tengo esa información en mis fuentes"


PROMPT_TEMPLATE = """Eres un asistente oficial que orienta a los usuarios sobre la \
asociación juvenil de voluntariado 'Damos Nuestra Ilusión' (DNI) de Valencia.

REGLAS:
- Responde SÓLO con la información explícita del CONTEXTO. Si la respuesta no está, \
di literalmente: "{rejection}".
- Sé claro, cercano y colaborativo, reflejando el espíritu de la asociación.
- Cita siempre el archivo o archivos de los que sale la información, por ejemplo: fuentes: ["07 desayunos logistica.txt"].
- No inventes datos numéricos (horarios, direcciones, fechas de eventos) que no estén \
explícitos en el contexto proporcionado.

CONTEXTO DE LA ASOCIACIÓN DNI VALENCIA:
{context}

PREGUNTA: {question}

RESPUESTA:"""


def build_prompt(question: str, retrieved: list) -> str:
    """Une los chunks recuperados estructurando sus fuentes y rellena la plantilla."""
    # Mantenemos el formato de inyección del profesor para que el LLM identifique el origen de cada bloque
    context = "\n\n".join(f"[{c.source}]\n{c.text}" for c in retrieved)
    
    return PROMPT_TEMPLATE.format(
        rejection=REJECTION_PHRASE,
        context=context,
        question=question,
    )
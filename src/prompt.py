"""
Modulo para la construccion del prompt.
"""

def construir_prompt(pregunta, chunks, fuentes):
    """
    Construye el prompt con contexto y reglas anti-alucinacion.
    """
    contexto = "\n\n".join([
        f"[{fuente}]\n{chunk}"
        for chunk, fuente in zip(chunks, fuentes)
    ])

    prompt = f"""Eres un asistente de la asociacion DNI (Damos Nuestra Ilusion).

INSTRUCCIONES OBLIGATORIAS:
1. Responde SOLAMENTE con la informacion proporcionada en el CONTEXTO.
2. Si la respuesta no aparece en el contexto, responde exactamente: "No tengo esa informacion en mis fuentes".
3. No inventes datos, horarios, fechas, contactos o cualquier informacion que no este en el contexto.
4. Cita siempre el archivo fuente entre parentesis, por ejemplo: (07_desayunos_logistica.txt).
5. Si encuentras contradicciones entre diferentes fuentes, presentalas ambas citando cada archivo.

CONTEXTO:
{contexto}

PREGUNTA DEL USUARIO:
{pregunta}

RESPUESTA:"""

    return prompt
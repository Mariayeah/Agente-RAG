import os
import time
import requests
import chromadb
from openai import OpenAI
from dotenv import load_dotenv

# 1. Cargar la configuración segura del archivo .env
load_dotenv()

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api")
CHROMA_PATH = os.environ.get("CHROMA_PATH", "./data/chroma")
COLLECTION_NAME = os.environ.get("COLLECTION_NAME", "dni_valencia")

# Configuración obligatoria para el benchmark de PoliGPT (UPV)
POLIGPT_API_KEY = os.environ.get("POLIGPT_API_KEY")
POLIGPT_BASE_URL = os.environ.get("POLIGPT_BASE_URL", "https://api.poligpt.upv.es/v1")

def consultar(pregunta: str, conversation_id: str | None = None) -> dict:
    """
    Función obligatoria por contrato de interfaz (Opción A).
    Devuelve la respuesta del agente junto con fuentes, chunks y métricas de rendimiento.
    """
    inicio_tiempo = time.time()
    
    # 2. Conectar al almacenamiento persistente de ChromaDB
    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)
    
    # 3. Generar el embedding de la pregunta del usuario usando el modelo local
    embed_model = os.environ.get("EMBED_MODEL", "nomic-embed-text")
    res_emb = requests.post(
        f"{OLLAMA_URL}/embeddings",
        json={"model": embed_model, "prompt": pregunta}
    )
    res_emb.raise_for_status()
    query_embedding = res_emb.json()["embedding"]
    
    # 4. Fase de Recuperación (Retrieval): Extraemos los top-5 fragmentos más relevantes
    results = collection.query(query_embeddings=[query_embedding], n_results=5)
    
    chunks_recuperados = results["documents"][0] if results["documents"] else []
    metadatas = results["metadatas"][0] if results["metadatas"] else []
    
    # Extraer y limpiar las fuentes reales de los metadatas indexados
    fuentes_citadas = list(set([m["source"] for m in metadatas if m and "source" in m]))
    
    # Unificar el contexto en un único bloque semántico
    contexto = "\n\n".join(chunks_recuperados)
    
    # 5. Diseño del Prompt de Control (Instrucciones Anti-alucinación y Contradicciones)
    prompt_sistema = f"""Eres un asistente oficial de la asociación juvenil de voluntariado 'Damos Nuestra Ilusión' (DNI) de Valencia.
Tu única tarea es responder a la pregunta del usuario utilizando exclusivamente el contexto proporcionado.

REGLAS CRÍTICAS DE CONTROL:
1. ANTI-ALUCINACIÓN: Si la respuesta exacta a la pregunta no se encuentra de forma explícita en el CONTEXTO proporcionado abajo, responde estrictamente: "No tengo esa información en mis fuentes". No inventes nada ni uses suposiciones.
2. CONTRADICCIONES: Si el contexto contiene contradicciones de información (por ejemplo, diferentes horarios para una misma actividad), debes exponer de forma transparente ambas versiones mencionando los nombres de los archivos de origen.
3. RESTRICCIÓN DE ÁMBITO: No utilices tu conocimiento externo o preentrenado bajo ningún concepto.

CONTEXTO DE LA ASOCIACIÓN DNI VALENCIA:
{contexto}

PREGUNTA DEL USUARIO:
{pregunta}

RESPUESTA FUNDAMENTADA CITANDO FUENTES:"""

    # 6. Enrutamiento Inteligente del LLM (Local vs PoliGPT)
    model_llm = os.environ.get("LLM_MODEL", "llama3.2:3b")
    
    # Determinar si el modelo actual pertenece al benchmark de PoliGPT o es local de Ollama
    es_modelo_poligpt = any(keyword in model_llm.lower() for keyword in ["gpt", "claude", "mini", "gemma3"]) or "poligpt" in os.environ.get("LLM_SERVER", "").lower()

    if es_modelo_poligpt:
        # Ejecución vía Cliente OpenAI conectado al Servidor de la UPV (PoliGPT)
        client = OpenAI(api_key=POLIGPT_API_KEY, base_url=POLIGPT_BASE_URL)
        
        res_llm = client.chat.completions.create(
            model=model_llm,
            messages=[{"role": "user", "content": prompt_sistema}],
            temperature=0.2
        )
        respuesta_texto = res_llm.choices[0].message.content
        prompt_tokens = res_llm.usage.prompt_tokens
        output_tokens = res_llm.usage.completion_tokens
    else:
        # Ejecución en máquina local a través de Ollama API
        res_llm = requests.post(
            f"{OLLAMA_URL}/generate",
            json={
                "model": model_llm,
                "prompt": prompt_sistema,
                "stream": False,
                "options": {"temperature": 0.2}
            }
        )
        res_llm.raise_for_status()
        respuesta_datos = res_llm.json()
        respuesta_texto = respuesta_datos["response"]
        prompt_tokens = respuesta_datos.get("prompt_eval_count", 0)
        output_tokens = respuesta_datos.get("eval_count", 0)
    
    # 7. Captura y Cálculo Preciso de Métricas de Rendimiento
    fin_tiempo = time.time()
    latencia_s = round(fin_tiempo - inicio_tiempo, 3)
    tokens_por_segundo = round(output_tokens / latencia_s, 1) if latencia_s > 0 else 0.0

    # 8. Retorno bajo estricto cumplimiento de contrato de la asignatura
    return {
        "respuesta": respuesta_texto,
        "fuentes": fuentes_citadas,
        "chunks": chunks_recuperados,
        "metricas": {
            "prompt_tokens": prompt_tokens,
            "output_tokens": output_tokens,
            "latencia_s": latencia_s,
            "tokens_per_sec": tokens_por_segundo,
            "modelo": model_llm
        },
        "trazas": None
    }

if __name__ == "__main__":
    print("--- Probando Agente DNI Valencia ---")
    # Realizamos una consulta de prueba
    resultado = consultar("¿A qué hora son los desayunos solidarios?")
    print(f"\nRespuesta:\n{resultado['respuesta']}\n")
    print(f"Fuentes utilizadas: {resultado['fuentes']}")
    print(f"Métricas del sistema: {resultado['metricas']}")
import os
import json
import sys
from pathlib import Path
from dotenv import load_dotenv

# Añadimos la raíz del proyecto para importar consultar.py
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import consultar

# Importaciones de RAGAs y Langchain
from datasets import Dataset
from ragas import evaluate

# Ocultamos avisos de desuso internos de la librería para limpiar la terminal
import warnings
warnings.filterwarnings("ignore") 

# Usamos las Clases en Mayúsculas (estándar moderno de RAGAs)
from ragas.metrics import (
    Faithfulness,
    AnswerRelevancy,
    ContextPrecision,
    ContextRecall
)

from langchain_openai import ChatOpenAI, OpenAIEmbeddings

load_dotenv()

ARCHIVO_PREGUNTAS = Path("benchmark/preguntas.json")
ARCHIVO_RESULTADOS = Path("evaluacion/ragas_results.json")

def ejecutar_evaluacion():
    if not ARCHIVO_PREGUNTAS.exists():
        print(f"Error: No se encuentra {ARCHIVO_PREGUNTAS}")
        return

    with open(ARCHIVO_PREGUNTAS, "r", encoding="utf-8") as f:
        preguntas = json.load(f)

    print("🚀 Recopilando respuestas del Agente para evaluar...")
    
    # Fijamos el modelo que elegiste como ganador en el benchmark
    consultar.SERVIDOR_LLM = "poligpt"
    consultar.LLM_MODEL = "gemma3:27b"
    
    datos_ragas = {
        "question": [],
        "answer": [],
        "contexts": [],
        "ground_truth": []
    }

    for p in preguntas:
        # Solo evaluamos las preguntas que tienen respuesta esperada
        if "respuesta_esperada" not in p:
            continue
            
        print(f"  -> Preguntando: {p['pregunta']}")
        respuesta_agente = consultar.consultar(p["pregunta"])
        
        datos_ragas["question"].append(p["pregunta"])
        datos_ragas["answer"].append(respuesta_agente["respuesta"])
        datos_ragas["contexts"].append(respuesta_agente["chunks"])
        datos_ragas["ground_truth"].append(p["respuesta_esperada"])

    # Convertimos los datos al formato Dataset requerido por RAGAs
    dataset = Dataset.from_dict(datos_ragas)

    print("\n⚖️ Iniciando el Juez RAGAs (PoliGPT)... Esto puede tardar un par de minutos.")
    
    # Configuramos PoliGPT como el "Juez"
    juez_llm = ChatOpenAI(
        base_url=os.environ.get("POLIGPT_BASE_URL"),
        api_key=os.environ.get("POLIGPT_API_KEY"),
        model="poligpt" 
    )
    
    # Usamos los embeddings disponibles en PoliGPT
    juez_embeddings = OpenAIEmbeddings(
        base_url=os.environ.get("POLIGPT_BASE_URL"),
        api_key=os.environ.get("POLIGPT_API_KEY"),
        model="nomic-embed-text" 
    )

    try:
        # Ejecutamos la evaluación pasando las clases ya instanciadas
        resultados = evaluate(
            dataset,
            metrics=[
                Faithfulness(),
                AnswerRelevancy(),
                ContextPrecision(),
                ContextRecall()
            ],
            llm=juez_llm,
            embeddings=juez_embeddings
        )
        
        # Extraemos los datos a través de Pandas (máxima estabilidad entre versiones)
        df = resultados.to_pandas()
        
        # Calculamos de forma dinámica las medias globales mapeando las columnas devueltas
        medias_globales = {}
        metricas_instancias = [Faithfulness(), AnswerRelevancy(), ContextPrecision(), ContextRecall()]
        
        for m in metricas_instancias:
            nombre_metrica = m.name
            columna_real = None
            
            if nombre_metrica in df.columns:
                columna_real = nombre_metrica
            elif nombre_metrica.lower() in df.columns:
                columna_real = nombre_metrica.lower()
            else:
                for col in df.columns:
                    if nombre_metrica.lower() in col.lower():
                        columna_real = col
                        break
                        
            if columna_real:
                medias_globales[nombre_metrica] = float(df[columna_real].mean())
            else:
                medias_globales[nombre_metrica] = None
        
        resumen = {
            "medias_globales": medias_globales,
            "detalle_por_pregunta": df.to_dict(orient="records")
        }
        
        ARCHIVO_RESULTADOS.parent.mkdir(parents=True, exist_ok=True)
        
        with open(ARCHIVO_RESULTADOS, "w", encoding="utf-8") as f:
            import math
            # Función recursiva de seguridad para evitar que 'NaN' rompa el formato JSON estándar
            def replace_nan(obj):
                if isinstance(obj, float) and math.isnan(obj):
                    return None
                elif isinstance(obj, dict):
                    return {k: replace_nan(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [replace_nan(i) for i in obj]
                return obj
            
            clean_resumen = replace_nan(resumen)
            json.dump(clean_resumen, f, ensure_ascii=False, indent=2)
            
        print(f"\n🎉 Evaluación RAGAs completada. Resultados guardados en {ARCHIVO_RESULTADOS}")
        print("\n--- NOTAS MEDIAS GLOBALES ---")
        for metrica, valor in medias_globales.items():
            print(f"{metrica}: {valor:.4f}" if valor is not None else f"{metrica}: N/A")
        
    except Exception as e:
        import traceback
        print(f"\n❌ Error durante la evaluación de RAGAs:")
        traceback.print_exc()

if __name__ == "__main__":
    ejecutar_evaluacion()
#!/usr/bin/env python3
"""Script de evaluación automatizada (Benchmark de la Banda 7).

Itera sobre el set fijo de preguntas contra los 4 modelos configurados,
capturando de manera fidedigna las respuestas y las métricas de rendimiento.
"""

import json
import time
import sys
from pathlib import Path

# Añadimos la raíz del proyecto al path para poder importar consultar.py
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import consultar 

ARCHIVO_PREGUNTAS = Path(__file__).resolve().parent / "preguntas.json"
ARCHIVO_RESULTADOS = Path(__file__).resolve().parent / "benchmark.json"

# Los 4 modelos que pide la rúbrica (Banda 7)
MODELOS = [
    # Los 2 locales (pequeños y rápidos)
    {"alias": "gemma3:4b", "servidor": "ollama_local"},
    {"alias": "llama3.2:3b", "servidor": "ollama_local"},
    
    # Los 2 remotos de PoliGPT (grandes y potentes)
    {"alias": "poligpt", "servidor": "poligpt"},
    {"alias": "gemma3:27b", "servidor": "poligpt"} 
]

def ejecutar_benchmark():
    if not ARCHIVO_PREGUNTAS.exists():
        print(f"Error: No se encuentra {ARCHIVO_PREGUNTAS}")
        return

    with open(ARCHIVO_PREGUNTAS, "r", encoding="utf-8") as f:
        preguntas = json.load(f)

    resultados_totales = []

    print("🚀 Iniciando Benchmark de 4 modelos (Banda 7)...")
    
    for modelo in MODELOS:
        alias = modelo["alias"]
        servidor = modelo["servidor"]
        print(f"\n--- Evaluando modelo: {alias} ({servidor}) ---")
        
        # Inyectamos el modelo y el servidor en consultar.py al vuelo
        consultar.SERVIDOR_LLM = servidor
        consultar.LLM_MODEL = alias

        for p in preguntas:
            texto_pregunta = p["pregunta"]
            print(f"Pregunta: {texto_pregunta}")
            
            inicio = time.time()
            
            try:
                # Llamamos a tu agente
                respuesta_agente = consultar.consultar(texto_pregunta)
                latencia = round(time.time() - inicio, 2)
                
                resultado = {
                    "pregunta_id": p["id"],
                    "pregunta": texto_pregunta,
                    "modelo": alias,
                    "servidor": servidor,
                    "respuesta": respuesta_agente["respuesta"],
                    "fuentes_citadas": respuesta_agente["fuentes"],
                    "latencia_segundos": latencia,
                    "tokens_entrada": respuesta_agente["metricas"]["prompt_tokens"], 
                    "tokens_salida": respuesta_agente["metricas"]["output_tokens"]   
                }
                resultados_totales.append(resultado)
                print(f"  ✅ Respondido en {latencia}s")
                
            except Exception as e:
                print(f"  ❌ Error: {e}")

    # Guardamos todos los resultados
    with open(ARCHIVO_RESULTADOS, "w", encoding="utf-8") as f:
        json.dump(resultados_totales, f, ensure_ascii=False, indent=2)
        
    print(f"\n🎉 Benchmark completado. Resultados guardados en {ARCHIVO_RESULTADOS}")

if __name__ == "__main__":
    ejecutar_benchmark()
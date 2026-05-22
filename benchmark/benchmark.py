#!/usr/bin/env python3
"""Script de automatización de Benchmark (Banda 7).

Recorre el set de preguntas fijas contra los 4 modelos declarados 
(2 locales en Ollama y 2 remotos en PoliGPT) y almacena las respuestas 
junto con sus métricas de rendimiento en un JSON crudo.
"""

from __future__ import annotations

import os
import sys
import json
from pathlib import Path

# Inyección del path para localizar el paquete modular en src/
repo_root = Path(__file__).resolve().parents[1]
sys.path.append(str(repo_root / "src"))

from agente_rag.pipeline import answer

# Definición de los 4 modelos oficiales del equipo
MODELOS = [
    {"alias": "llama3.2:3b", "servidor": "ollama_local"},
    {"alias": "qwen2.5:3b", "servidor": "ollama_local"},
    {"alias": "gpt-4o-mini", "servidor": "poligpt"},
    {"alias": "claude-3-5-haiku", "servidor": "poligpt"}
]

def cargar_preguntas() -> list[dict]:
    ruta_preguntas = repo_root / "benchmark" / "preguntas.json"
    if not ruta_preguntas.exists():
        raise FileNotFoundError(f"❌ No se encontró el archivo de preguntas en {ruta_preguntas}")
    with open(ruta_preguntas, "r", encoding="utf-8") as f:
        return json.load(f)

def ejecutar_benchmark():
    print("==================================================================")
    print("📊 INICIANDO BENCHMARK AUTOMATIZADO DE 4 MODELOS — ASISTENTE DNI")
    print("==================================================================")
    
    try:
        preguntas = cargar_preguntas()
        resultados_finales = {}
        
        for mod in MODELOS:
            alias = mod["alias"]
            servidor = mod["servidor"]
            print(f"\n🤖 Evaluando modelo: [{alias}] ({servidor})...")
            
            resultados_finales[alias] = []
            
            for q in preguntas:
                print(f"  👉 Procesando {q['id']} ({q['tipo']})... ", end="", flush=True)
                
                try:
                    # Invocamos el pipeline modular inyectando el modelo actual
                    res_rag = answer(q["pregunta"], model=alias)
                    
                    # Estructuramos el volcado crudo según exige la rúbrica
                    resultados_finales[alias].append({
                        "id": q["id"],
                        "tipo": q["tipo"],
                        "pregunta": q["pregunta"],
                        "respuesta": res_rag["respuesta"],
                        "fuentes": res_rag["fuentes"],
                        "metricas": res_rag["metricas"]
                    })
                    print("✅ Completado.")
                    
                except Exception as e:
                    print(f"❌ Error: {e}")
                    # En caso de fallo de red en un modelo, registramos el hueco para no romper el bucle
                    resultados_finales[alias].append({
                        "id": q["id"],
                        "pregunta": q["pregunta"],
                        "respuesta": f"ERROR DE EJECUCIÓN: {str(e)}",
                        "fuentes": [],
                        "metricas": {"prompt_tokens": 0, "output_tokens": 0, "tokens_per_sec": 0.0, "latencia_s": 0.0, "modelo": alias}
                    })

        # Guardar resultados en el JSON crudo de salida
        ruta_salida = repo_root / "benchmark" / "benchmark.json"
        with open(ruta_salida, "w", encoding="utf-8") as f:
            json.dump(resultados_finales, f, ensure_ascii=False, indent=2)
            
        print("\n==================================================================")
        print(f"🎉 ¡Benchmark finalizado con éxito! Datos crudos guardados en:")
        print(f"📁 {ruta_salida}")
        print("==================================================================")

    except Exception as e:
        print(f"\n❌ Fallo crítico en el orquestador del benchmark: {e}", file=sys.stderr)

if __name__ == "__main__":
    ejecutar_benchmark()
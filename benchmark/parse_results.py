# benchmark/parse_results.py
import json
from pathlib import Path

def generar_tabla_markdown():
    ruta_json = Path("benchmark/benchmark.json")
    ruta_md = Path("benchmark/benchmark.md")
    
    if not ruta_json.exists():
        print("❌ Error: No se encuentra benchmark.json. Ejecuta primero benchmark.py")
        return

    with open(ruta_json, "r", encoding="utf-8") as f:
        pruebas = json.load(f)

    # Agrupar métricas por modelo
    analisis = {}
    for p in pruebas:
        mod = p["modelo_alias"]
        if mod not in analisis:
            analisis[mod] = {
                "servidor": p["servidor"],
                "latencias": [],
                "tokens_s": [],
                "aciertos": 0,
                "total": 0
            }
        
        m = p["metricas"]
        analisis[mod]["latencias"].append(m.get("latencia_s", 0))
        analisis[mod]["tokens_s"].append(m.get("tokens_per_sec", 0))
        analisis[mod]["total"] += 1
        # Contamos como acierto si no se ha marcado como fallo explícito
        if p.get("calidad_subjetiva") != "fallo":
            analisis[mod]["aciertos"] += 1

    # Construir el contenido del archivo Markdown (.md)
    contenido_md = [
        "# 📊 Resultados Globales del Benchmark - Agente DNI\n",
        "Este archivo ha sido autogenerado por el script de postprocesamiento para el informe técnico.\n",
        "| Modelo LLM | Servidor / Origen | Promedio Latencia (s) | Velocidad Media (Tokens/s) | Calidad Subjetiva (Aciertos) |",
        "| :--- | :--- | :---: | :---: | :---: |"
    ]

    for modelo, datos in analisis.items():
        avg_latencia = round(sum(datos["latencias"]) / len(datos["latencias"]), 2)
        avg_tokens_s = round(sum(datos["tokens_s"]) / len(datos["tokens_s"]), 1)
        
        linea = f"| `{modelo}` | {datos['servidor'].upper()} | {avg_latencia} s | {avg_tokens_s} tok/s | {datos['aciertos']} / {datos['total']} |"
        contenido_md.append(linea)

    contenido_md.append("\n## 📝 Notas de interpretación técnica")
    contenido_md.append("- Los modelos locales ejecutan los cálculos directamente sobre la máquina local.")
    contenido_md.append("- Los modelos alojados en PoliGPT aprovechan la infraestructura externa de la UPV.")

    # Guardar el archivo definitivo
    with open(ruta_md, "w", encoding="utf-8") as f:
        f.write("\n".join(contenido_md))
        
    print(f"🎉 Tabla comparativa generada con éxito en '{ruta_md}'")

if __name__ == "__main__":
    generar_tabla_markdown()
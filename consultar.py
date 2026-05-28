#!/usr/bin/env python3
"""
================================================================================
Asistente DNI Valencia — Punto de Entrada Oficial con Soporte de Legado
================================================================================
Mantiene compatibilidad absoluta con scripts de evaluación externos (Banda 7 y 8)
al exponer variables globales de configuración expuestas, delegando la ejecución
real en el pipeline persistente empaquetado en 'src/'.
"""

from __future__ import annotations

import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# 1. Carga del entorno (con ruta explícita a la raíz)
repo_root = Path(__file__).resolve().parent
load_dotenv(dotenv_path=repo_root / ".env")

# 2. Inyección dinámica del path para localizar src/
repo_root = Path(__file__).resolve().parent
sys.path.append(str(repo_root / "src"))

from agente_rag.pipeline import answer

# ==============================================================================
# INTERFAZ DE LEGADO: Variables globales para no romper scripts de tu compañero
# ==============================================================================
SERVIDOR_LLM = "ollama_local"  # Modificable externamente por benchmark.py / ragas.py
LLM_MODEL = "llama3.2:3b"      # Modificable externamente por benchmark.py / ragas.py


def consultar(pregunta: str, conversation_id: str | None = None) -> dict:
    """
    Función de interfaz obligatoria por contrato (§9, Opción A).
    
    Lee dinámicamente el estado de las variables globales del módulo para 
    enrutar la petición al modelo correcto de forma transparente.
    """
    alias_ejecucion = LLM_MODEL
        
    # Delegación en el orquestador modular pasando el modelo y servidor al vuelo
    return answer(
        pregunta, 
        model=alias_ejecucion, 
        servidor=SERVIDOR_LLM,
        conversation_id=conversation_id
    )


def _main(argv: list[str]) -> int:
    """Manejador de la CLI de la terminal."""
    if len(argv) < 2:
        print('Uso correcto en terminal: python consultar.py "<tu pregunta aquí>"', file=sys.stderr)
        return 2
        
    pregunta_cmd = " ".join(argv[1:])
    resultado = consultar(pregunta_cmd)
    
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv))
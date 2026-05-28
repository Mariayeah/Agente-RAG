#!/usr/bin/env python3
"""Punto de entrada oficial del contrato de la asignatura (§9, Opción A).

Actúa como una capa delgada de interfaz (módulo Python) que delega la orquestación 
completa del RAG al paquete modular alojado en 'src/agente_rag/'.
"""

from __future__ import annotations

import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# 1. Carga segura del entorno al inicializar el punto de entrada
load_dotenv()

# 2. Inyección dinámica en el path de ejecución para localizar el paquete en src/
repo_root = Path(__file__).resolve().parent
sys.path.append(str(repo_root / "src"))

# 3. Importación del pipeline unificado de generación y respuesta
from agente_rag.pipeline import answer


def consultar(pregunta: str, conversation_id: str | None = None) -> dict:
    """Función obligatoria por contrato de interfaz exigida en el enunciado.
    
    Toma la consulta del usuario y retorna el JSON estructurado con la respuesta, 
    las fuentes fidedignas mapeadas en disco, los chunks y las métricas avanzadas.
    """
    # Delegamos de manera transparente en el orquestador modular del pipeline
    return answer(pregunta, conversation_id=conversation_id)


def _main(argv: list[str]) -> int:
    """Manejador de la interfaz de línea de comandos (CLI) con codificación limpia."""
    if len(argv) < 2:
        print('Uso correcto en terminal: python consultar.py "<tu pregunta aquí>"', file=sys.stderr)
        return 2
        
    pregunta_cmd = " ".join(argv[1:])
    resultado = consultar(pregunta_cmd)
    
    # Emisión del volcado JSON en UTF-8 puro garantizando que no se rompan caracteres especiales
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv))
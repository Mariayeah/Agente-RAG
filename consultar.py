#!/usr/bin/env python3
"""Punto de entrada oficial exigido por el contrato de la asignatura (§9, opción A).

Invoca el pipeline modularizado del agente RAG alojado en la carpeta 'src/',
asegurando que toda la lógica de dominio esté desacoplada del punto de entrada.
"""

from __future__ import annotations

import sys
import json
from pathlib import Path

# Inyección dinámica del path para localizar la carpeta src/ en el espacio de trabajo
repo_root = Path(__file__).resolve().parent
sys.path.append(str(repo_root / "src"))

# Importamos el orquestador oficial del paquete modular
from agente_rag.pipeline import answer


def consultar(pregunta: str, conversation_id: str | None = None) -> dict:
    """Función de interfaz obligatoria exigida por el contrato del enunciado.
    
    Delega la ejecución completa del RAG al orquestador modular y devuelve el 
    diccionario exacto de la Banda 7 con fuentes, chunks y métricas.
    """
    # Llamamos al pipeline pasándole la pregunta y el id opcional de conversación
    return answer(pregunta, conversation_id=conversation_id)


def _main(argv: list[str]) -> int:
    """Función de ejecución en terminal que emite el JSON bajo codificación limpia."""
    if len(argv) < 2:
        print('Uso correcto en terminal: python consultar.py "<tu pregunta aquí>"', file=sys.stderr)
        return 2
        
    pregunta_cmd = " ".join(argv[1:])
    resultado = consultar(pregunta_cmd)
    
    # Imprimir el JSON estructurado con codificación UTF-8 pura para evitar fallos de acentos en terminales
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv))
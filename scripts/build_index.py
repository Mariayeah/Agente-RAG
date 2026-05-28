#!/usr/bin/env python3
"""Script de inicialización de la base de conocimientos (Pipeline Offline).

Importa la configuración oficial del paquete y ejecuta de manera secuencial 
las fases de carga del corpus, fragmentación semántica (chunking) y construcción 
del índice persistente en ChromaDB aplicando la similitud del coseno.
"""

from __future__ import annotations

import sys
from pathlib import Path
repo_root = Path(__file__).resolve().parents[1]
sys.path.append(str(repo_root / "src"))

# Ahora ya puedes importar vuestros módulos sin errores
from agente_rag.config import SETTINGS
from agente_rag.chunker import load_corpus, split_documents
from agente_rag.retriever import build_index


def main() -> int:
    print("==================================================================")
    print("🚀  INICIANDO PIPELINE DE INGESTA AUTOMÁTICA — ASISTENTE DNI VALENCIA")
    print("==================================================================")
    
    try:
        # 1. Fase de Carga: Lee los 16 archivos .txt desde la ruta configurada dinámicamente
        print(f"📁 Cargando documentos desde: '{SETTINGS.corpus_dir.name}/'...")
        documentos = load_corpus(SETTINGS.corpus_dir)
        print(f"   ↳ Éxito: Se han cargado {len(documentos)} archivos de texto.")

        # 2. Fase de Chunking: Trocea los documentos con los parámetros óptimos (1000, 250)
        print("\n✂️  Aplicando fragmentación recursiva por caracteres...")
        chunks = split_documents(documentos)
        print(f"   ↳ Éxito: Corpus dividido en {len(chunks)} bloques semánticos.")
        print("   ↳ Parámetros de diseño del equipo -> Chunk Size: 1000 | Overlap: 250")

        # 3. Fase de Vectorización y Guardado Persistente en Disco
        print(f"\n🧬 Generando embeddings vectoriales con el modelo '{SETTINGS.embed_model}'...")
        print(f"📦 Guardando índice persistente en la colección '{SETTINGS.collection_name}'...")
        print("⚠️  Nota: Si existía un índice residual previo, se eliminará para evitar duplicaciones.")
        
        # Invocamos la función del retriever físico que fuerza la métrica coseno
        total_indexados = build_index(chunks)
        
        print("\n==================================================================")
        print(f"🎉 ¡Pipeline completado! {total_indexados} fragmentos guardados en disco física y limpiamente.")
        print(f"📁 Ruta de la base de datos: {SETTINGS.chroma_path}")
        print("==================================================================")
        return 0

    except FileNotFoundError as e:
        print(f"\n❌ Error de inicialización: {e}", file=sys.stderr)
        print("💡 Por favor, comprueba que la carpeta de documentos de la asociación existe en la raíz.", file=sys.stderr)
        return 1
        
    except Exception as e:
        print(f"\n❌ Fallo crítico durante el proceso de indexación: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
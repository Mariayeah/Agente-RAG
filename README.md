# Asistente RAG — Asociación DNI Valencia 🤝

Repositorio oficial para la práctica de Asistentes RAG de la asignatura Inteligencia Artificial. Este proyecto implementa un agente conversacional basado en la técnica RAG (Retrieval-Augmented Generation) diseñado para responder preguntas sobre la asociación juvenil de voluntariado **Damos Nuestra Ilusión (DNI)** de Valencia.

## 🚀 Arranque Rápido

**1. Clonar el repositorio y entrar en la carpeta**
```bash
git clone <https://github.com/Mariayeah/Agente-RAG>
cd Agente-RAG
```

**2. Crear entorno virtual e instalar dependencias (Python 3.11+)**
```bash
python -m venv .venv

# En Windows:
.\.venv\Scripts\Activate.ps1
# En Mac/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

**3. Configurar variables de entorno**
Crea un archivo `.env` en la raíz del proyecto y añade tus credenciales para conectar con el juez y los modelos remotos de la UPV:
```env
POLIGPT_BASE_URL="<URL_DEL_SERVIDOR>"
POLIGPT_API_KEY="<TU_API_KEY>"
```

**4. Construir el índice vectorial (si no existe)**
Asegúrate de ejecutar el script de indexación para procesar los documentos de la base de conocimiento y generar la base de datos persistente en ChromaDB antes de hacer la primera consulta:
```bash
python scripts/build_index.py
```

**5. Lanzar una consulta al Agente**
Para hacerle una pregunta al agente, ejecuta el punto de entrada principal:
```bash
python consultar.py "¿Cómo me apunto a los desayunos solidarios?"
```

## 📂 Estructura del Repositorio

El proyecto está organizado siguiendo una arquitectura modular con separación clara de responsabilidades:

*   `base conocimiento/`: Contiene el corpus de documentos `.txt` con la información oficial de la asociación.
*   `benchmark/`: Scripts y resultados de la evaluación empírica (`benchmark.py`, JSON de métricas y análisis).
*   `data/`: Almacenamiento local persistente de la base de datos vectorial ChromaDB.
*   `evaluacion/`: Scripts de evaluación cuantitativa (`evaluar_ragas.py`), resultados del juez PoliGPT y justificación de métricas propias.
*   `scripts/`: Scripts de automatización, incluyendo la construcción del índice (`build_index.py`).
*   `src/agente_rag/`: Paquete central con la lógica modular del pipeline RAG (`chunker.py`, `retriever.py`, `generator.py`, `pipeline.py`, etc.).
*   `consultar.py`: Punto de entrada principal para realizar consultas al agente por terminal.
*   `features.json`: Declaración de rúbrica para el sistema de corrección automático.
*   `informe.pdf`: Memoria técnica con el esquema y resumen del proyecto.
*   `AI_USAGE.md`: Declaración de transparencia sobre el uso de herramientas de IA durante el desarrollo.

## 🏆 Bandas Implementadas

Este proyecto cubre exhaustivamente los siguientes niveles de la rúbrica oficial:

*   **Banda 5 ✓** — Pipeline RAG completo, integrando ChromaDB y LangChain, con un prompt estricto anti-alucinación que fuerza al modelo a rechazar preguntas fuera de ámbito.
*   **Banda 6 ✓** — Trazabilidad total: cada respuesta generada cita explícitamente el archivo fuente del que se ha extraído la información directamente en el prompt.
*   **Banda 7 ✓** — *Benchmark* empírico automatizado comparando 4 modelos distintos (locales: `gemma3:4b`, `llama3.2:3b` vs remotos: `poligpt`, `gemma3:27b`). Se monitorizan métricas de latencia, tokens de entrada/salida y comportamiento.
*   **Banda 8 ✓** — Evaluación cuantitativa del sistema utilizando el framework **RAGAs**. Se utiliza a `poligpt` como juez externo para calcular métricas de *Faithfulness*, *Answer Relevancy*, *Context Precision* y *Context Recall*. Además, se incluyen y justifican métricas de evaluación propias orientadas a la experiencia de usuario y trazabilidad.

## ⚖️ Avisos Legales y Éticos

El modelo y el corpus son material estructurado con fines docentes y de demostración técnica para la Universitat Politècnica de València. Los datos sobre la asociación DNI Valencia reflejan la información provista en los textos del dominio del proyecto. Ningún archivo `.env` con secretos o credenciales se ha subido al repositorio público.

## 👥 Créditos y Autores

Desarrollado por:
* **Christopher Yoris Pulgar - Meryame Ait Boumlik - Maria Mei Algora Bonilla**

Proyecto realizado para la asignatura de **Inteligencia Artificial (3º GTI)**.  
Universitat Politècnica de València, 2026.
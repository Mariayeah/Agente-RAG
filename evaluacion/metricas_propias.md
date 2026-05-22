# Evaluación de Métricas Propias - Asistente RAG DNI

En cumplimiento con los requisitos de la Banda 8, se han diseñado, justificado y aplicado dos métricas de evaluación propias para complementar el análisis realizado con el framework RAGAs. 

Estas métricas abordan dos problemas críticos en sistemas RAG en producción: la fiabilidad estricta de las referencias (Trazabilidad) y la experiencia de usuario (Rendimiento).

---

## 1. Tasa de Alucinación de Fuentes (Source Hallucination Rate)

**Concepto:** Mide el porcentaje de fuentes citadas por el LLM en su respuesta final que *realmente* pertenecen al conjunto de documentos (`chunks`) recuperados por el Retriever para esa consulta en específico.

**Fórmula de Cálculo:** `SHR = (Fuentes Citadas Válidas / Total de Fuentes Citadas por el LLM) * 100`
* *Fuentes Citadas Válidas:* Archivos mencionados en la clave `"fuentes"` de la respuesta que están verdaderamente presentes en los metadatos de los chunks inyectados en el prompt.
* *Nota:* Si el modelo cita una fuente que no está en el corpus (o no se le pasó en esa consulta), el porcentaje bajará drásticamente.

**Justificación para el caso DNI:** La rúbrica exige explícitamente que "si un archivo no aparece en el contexto recuperado, no puede citarse". Los LLMs instruidos a veces intentan complacer al usuario inventando referencias plausibles que suenan reales pero que el retriever no ha encontrado. Esta métrica audita estrictamente la cadena de custodia de la información, asegurando que el modelo no rompe el contrato de veracidad y cita exactamente lo que ha leído.

---

## 2. Puntuación de Viabilidad por Latencia (Latency Usability Score)

**Concepto:** Una métrica orientada a la Experiencia de Usuario (UX) que evalúa la idoneidad del modelo para un entorno de chat en tiempo real. Asigna una puntuación normalizada de 0.0 a 1.0 basada en el tiempo total de respuesta (latencia).

**Umbrales y Cálculo:** * **1.0 (Óptimo):** Latencia $\le$ 2.0 segundos. (El usuario percibe fluidez inmediata).
* **0.0 (Inaceptable):** Latencia $\ge$ 6.0 segundos. (El usuario percibe que el bot ha fallado o es desesperantemente lento).
* **Degradación lineal:** Para latencias entre 2.0 y 6.0 segundos, la puntuación disminuye linealmente.  
  `LUS = 1.0 - ((Latencia - 2.0) / 4.0)`

**Justificación para el caso DNI:** Durante el *benchmark* empírico de la Banda 7, se observaron disparidades considerables: los modelos remotos de PoliGPT mostraron estabilidad, mientras que los modelos locales sufrieron fuertes latencias por carga en memoria (*cold start*), llegando a demorar hasta 22 segundos. Un sistema RAG excelente no solo debe ser preciso (evaluado por RAGAs), sino también operativamente viable. De nada sirve un modelo que alcance un 1.0 en `faithfulness` si el voluntario de la asociación DNI debe interrumpir su trabajo para esperar la respuesta.

## 3. Resumen de la Evaluación Cuantitativa (RAGAs)

La evaluación automática mediante el framework RAGAs (utilizando el modelo `poligpt` como juez sobre las respuestas generadas por `gemma3:27b` a través de la API de la UPV) arrojó los siguientes resultados promedio:

* **Faithfulness (Fidelidad): 0.80** - Alta adherencia al contexto; el modelo evita inventar datos.
* **Context Recall (Recuperación de Contexto): 0.80** - La indexación en ChromaDB (chunks de 1000) es altamente efectiva encontrando la información requerida.
* **Context Precision (Precisión de Contexto): 0.62** - Margen de mejora; el sistema recupera ruido junto con la señal útil.
* **Answer Relevancy (Relevancia de Respuesta): 0.58** - El prompt restrictivo ("di que no lo sabes") provoca penalizaciones frente al juez de RAGAs, que espera respuestas más conversacionales.

**Conclusión General:** El sistema es altamente confiable y seguro (alta fidelidad y recuperación), cumpliendo el objetivo principal de un RAG institucional, aunque la precisión del contexto inyectado podría afinarse con algoritmos de re-ranking.
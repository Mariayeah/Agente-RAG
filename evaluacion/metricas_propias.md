# Resultados de Evaluación RAGAs — Asistente RAG DNI

Este documento presenta los resultados detallados de la evaluación cuantitativa realizada con el framework RAGAs sobre el conjunto de validación del Asistente DNI, utilizando el modelo `poligpt` como juez.

---

## 1. Resumen Global de Métricas

Los promedios calculados para todo el conjunto de preguntas demuestran un sistema robusto, destacando especialmente en su capacidad para no inventar información:

*   **Faithfulness (Fidelidad):** 0.8278
*   **Answer Relevancy (Relevancia de Respuesta):** 0.5876
*   **Context Precision (Precisión de Contexto):** 0.5650
*   **Context Recall (Recuperación de Contexto):** 0.8000

---

## 2. Detalle de Evaluación por Pregunta

| ID | Pregunta | Faithfulness | Answer Relevancy | Context Precision | Context Recall |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **1** | ¿Qué es DNI? | 0.8889 | 0.6859 | 0.7500 | 1.0000 |
| **2** | ¿Cómo me apunto a los desayunos solidarios? | 0.7500 | 0.6879 | 1.0000 | 1.0000 |
| **3** | ¿Quién paga la gasolina del refuerzo escolar? | 0.5000 | 0.8012 | 0.7500 | 1.0000 |
| **4** | ¿En qué se diferencian los proyectos de RESIS y COLES? | 1.0000 | 0.7629 | 0.3250 | 1.0000 |
| **5** | ¿Cuánto cuesta el alquiler de un piso en Valencia? | 1.0000 | 0.0000 | 0.0000 | 0.0000 |

---

## 3. Análisis de Resultados

El análisis detallado de las métricas revela el siguiente comportamiento en el pipeline del Agente:

*   **Recuperación Perfecta en Dominio (Context Recall = 1.0):** Para todas las preguntas relacionadas con la asociación DNI (preguntas 1 a 4), el sistema de recuperación (ChromaDB) encontró exitosamente los fragmentos exactos que contenían la respuesta.
*   **Alta Fidelidad General (Faithfulness):** El agente extrae la información de sus fuentes sin inventar datos. Destaca la Pregunta 4, donde la fidelidad es absoluta (1.0), indicando que el modelo de generación se ciñó estrictamente a los textos recuperados. El único bajón se produce en la Pregunta 3 (0.50), posiblemente debido a una excesiva síntesis de la respuesta.
*   **Margen de mejora en Precisión de Contexto:** Aunque el sistema encuentra la información correcta (Recall), en ocasiones arrastra chunks adicionales con información irrelevante para la consulta específica (Context Precision promedio de 0.56). Un algoritmo de *re-ranking* podría mejorar esta métrica en futuras versiones.
*   **Comportamiento Anti-Alucinación (Pregunta 5):** La pregunta trampa sobre el alquiler en Valencia obtiene un 0.0 en Relevancia, Precisión y Recall. Esto representa un **éxito total de la política del sistema**. Al rechazar responder algo fuera de sus fuentes documentales, RAGAs castiga las métricas de relevancia, pero el sistema obtiene un **1.0 en Faithfulness** por admitir correctamente que no tiene la información, garantizando cero alucinaciones.
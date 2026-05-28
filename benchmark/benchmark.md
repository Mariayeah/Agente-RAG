# Resultados del Benchmark de Modelos — Asistente RAG DNI

A continuación se presenta el documento con la evaluación comparativa actualizada basándose en los últimos datos de ejecución registrados en el sistema.

---

## 1. Tabla Resumen de Métricas Crudas

| ID | Pregunta | Modelo | Servidor | Latencia (s) | Tokens Salida | Comportamiento Destacado |
| :---: | :--- | :--- | :--- | :---: | :---: | :--- |
| **1** | ¿Qué es DNI? | gemma3:4b | ollama_local | 8.08 | 102 | Respuesta completa y fiel. |
| **1** | ¿Qué es DNI? | llama3.2:3b | ollama_local | 7.07 | 102 | Respuesta completa y fiel. |
| **1** | ¿Qué es DNI? | poligpt | poligpt | 32.82 | 265 | Incluye formato Markdown (negritas). |
| **1** | ¿Qué es DNI? | gemma3:27b | poligpt | 4.42 | 100 | Respuesta estructurada y precisa. |
| **2** | ¿Cómo me apunto a los desayunos...? | gemma3:4b | ollama_local | 2.98 | 62 | Tono cercano ("¡Hola!"). |
| **2** | ¿Cómo me apunto a los desayunos...? | llama3.2:3b | ollama_local | 3.50 | 93 | Genera una lista numerada con los pasos. |
| **2** | ¿Cómo me apunto a los desayunos...? | poligpt | poligpt | 61.04 | 158 | Redacción correcta pero latencia alta. |
| **2** | ¿Cómo me apunto a los desayunos...? | gemma3:27b | poligpt | 2.97 | 61 | Precisión directa y rápida. |
| **3** | ¿Quién paga la gasolina del refuerzo? | gemma3:4b | ollama_local | 2.12 | 24 | Respuesta directa y breve. |
| **3** | ¿Quién paga la gasolina del refuerzo? | llama3.2:3b | ollama_local | 1.50 | 37 | Referencia explícita al nombre del archivo. |
| **3** | ¿Quién paga la gasolina del refuerzo? | poligpt | poligpt | 114.27 | 192 | Fiel al contexto pero excesivamente lento. |
| **3** | ¿Quién paga la gasolina del refuerzo? | gemma3:27b | poligpt | 2.51 | 24 | Fiel al contexto con baja latencia. |
| **4** | ¿En qué se diferencian RESIS y COLES? | gemma3:4b | ollama_local | 2.77 | 63 | Sintetiza la diferencia de forma directa. |
| **4** | ¿En qué se diferencian RESIS y COLES? | llama3.2:3b | ollama_local | 2.41 | 106 | Fallo cognitivo: responde con un saludo genérico. |
| **4** | ¿En qué se diferencian RESIS y COLES? | poligpt | poligpt | 136.39 | 540 | Desglose exhaustivo por categorías en Markdown. |
| **4** | ¿En qué se diferencian RESIS y COLES? | gemma3:27b | poligpt | 2.93 | 62 | Extrae información clave sobre los vínculos. |
| **5** | ¿Cuánto cuesta el alquiler en Valencia? | gemma3:4b | ollama_local | 1.84 | 9 | Rechazo estricto exitoso. |
| **5** | ¿Cuánto cuesta el alquiler en Valencia? | llama3.2:3b | ollama_local | 1.13 | 10 | Rechazo estricto exitoso. |
| **5** | ¿Cuánto cuesta el alquiler en Valencia? | poligpt | poligpt | 118.21 | 166 | Rechazo estricto exitoso. |
| **5** | ¿Cuánto cuesta el alquiler en Valencia? | gemma3:27b | poligpt | 2.08 | 10 | Rechazo estricto exitoso. |

---

## 2. Interpretación de los Resultados y Hallazgos

El análisis de los datos JSON revela variaciones muy importantes respecto a pruebas anteriores, destacando problemas de rendimiento en servidores remotos y diferencias en la capacidad de síntesis:

### A. Capacidad de Síntesis e Inferencia Compleja (Pregunta 4)
* **Profundidad vs Rendimiento:** El modelo `poligpt` generó la respuesta más elaborada (540 tokens de salida), dividiendo las diferencias entre RESIS y COLES por público, actividad, entorno y objetivo. Sin embargo, el modelo `llama3.2:3b` falló en la tarea de síntesis, devolviendo un saludo genérico ("¡Hola! Me alegra ayudarte...") y una lista de archivos sin contestar a la pregunta.
* **El equilibrio local:** `gemma3:4b` logró responder correctamente sintetizando que RESIS es para ancianos y COLES para niños en situación vulnerable utilizando solo 63 tokens de salida.

### B. Adherencia al Prompt y Anti-Alucinación (Pregunta 5)
* Todos los modelos sin excepción (gemma3:4b, llama3.2:3b, poligpt y gemma3:27b) pasaron la prueba de control.
* Ante la pregunta sobre el alquiler, los cuatro modelos generaron exactamente la misma cadena de texto de rechazo: "No tengo esa información en mis fuentes.".

### C. Análisis de Latencia Crítica
* **Degradación del servidor PoliGPT:** Se observan latencias anómalas e inaceptables para un entorno de producción en el modelo `poligpt`. Los tiempos de respuesta escalaron desde 32.82 segundos en la primera consulta hasta un máximo de 136.39 segundos en la cuarta pregunta. Incluso para rechazar la pregunta 5, requirió 118.21 segundos.
* **Rendimiento óptimo de Gemma3:27b:** A pesar de ejecutarse también en el servidor remoto `poligpt`, el modelo `gemma3:27b` mantuvo una estabilidad excelente, con latencias comprendidas entre 2.08 y 4.42 segundos.
* **Modelos locales:** `llama3.2:3b` registró el tiempo de respuesta más rápido de toda la prueba con 1.13 segundos en la pregunta 5.
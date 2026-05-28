# Resultados del Benchmark de Modelos — Asistente RAG DNI

Este documento presenta la evaluación y comparación cuantitativa y cualitativa de cuatro modelos de lenguaje (dos locales a través de Ollama y dos remotos a través de la API de PoliGPT) respondiendo a un set fijo de preguntas sobre la asociación DNI (Damos Nuestra Ilusión). 

El objetivo de este benchmark es analizar el rendimiento de cada modelo en términos de latencia, precisión y adherencia a las instrucciones anti-alucinación, manteniendo el resto de parámetros del pipeline RAG constantes (chunk_size = 1000, chunk_overlap = 250, k = 5).

---

## 1. Tabla Resumen de Métricas Crudas

A continuación se tabulan las métricas obtenidas durante la ejecución automática del script `benchmark.py`:

| ID | Pregunta | Modelo | Servidor | Latencia (s) | Fuentes Citadas | Calidad Subjetiva (Acierto/Fallo) |
| :---: | :--- | :--- | :--- | :---: | :--- | :--- |
| **1** | ¿Qué es DNI? | gemma3:4b | ollama_local | 5.46 | 3 | ✅ **Acierto** (Respuesta completa y fiel) |
| **1** | ¿Qué es DNI? | llama3.2:3b | ollama_local | 4.72 | 3 | ✅ **Acierto** (Breve pero correcta) |
| **1** | ¿Qué es DNI? | poligpt | poligpt | 3.90 | 3 | ✅ **Acierto** (Excelente formato con negritas) |
| **1** | ¿Qué es DNI? | gemma3:27b | poligpt | 3.29 | 3 | ✅ **Acierto** (Muy completa y estructurada) |
| **2** | ¿Cómo me apunto a los desayunos... ? | gemma3:4b | ollama_local | 1.70 | 2 | ✅ **Acierto** (Precisión exacta con el FAQ) |
| **2** | ¿Cómo me apunto a los desayunos... ? | llama3.2:3b | ollama_local | 2.20 | 2 | ✅ **Acierto** (Idéntica al FAQ oficial) |
| **2** | ¿Cómo me apunto a los desayunos... ? | poligpt | poligpt | 2.08 | 2 | ✅ **Acierto** (Redacción natural y correcta) |
| **2** | ¿Cómo me apunto a los desayunos... ? | gemma3:27b | poligpt | 2.03 | 2 | ✅ **Acierto** (Precisión absoluta) |
| **3** | ¿Quién paga la gasolina del refuerzo? | gemma3:4b | ollama_local | 1.28 | 3 | ✅ **Acierto** (Directa y al grano) |
| **3** | ¿Quién paga la gasolina del refuerzo? | llama3.2:3b | ollama_local | 0.90 | 3 | ✅ **Acierto** (Formulación correcta) |
| **3** | ¿Quién paga la gasolina del refuerzo? | poligpt | poligpt | 1.20 | 3 | ✅ **Acierto** (Fiel al contexto) |
| **3** | ¿Quién paga la gasolina del refuerzo? | gemma3:27b | poligpt | 1.61 | 3 | ✅ **Acierto** (Fiel al contexto) |
| **4** | ¿En qué se diferencian RESIS y COLES? | gemma3:4b | ollama_local | 1.94 | 4 | ✅ **Acierto** (Sintetiza de forma aceptable) |
| **4** | ¿En qué se diferencian RESIS y COLES? | llama3.2:3b | ollama_local | 0.73 | 4 | ❌ **Fallo** (Insuficiencia cognitiva: dice "No lo sabes") |
| **4** | ¿En qué se diferencian RESIS y COLES? | poligpt | poligpt | 6.07 | 4 | ⭐ **Excelente** (Genera tabla comparativa avanzada) |
| **4** | ¿En qué se diferencian RESIS y COLES? | gemma3:27b | poligpt | 2.60 | 4 | ✅ **Acierto** (Extrae datos de horarios y lugares) |
| **5** | ¿Cuánto cuesta el alquiler en Valencia? | gemma3:4b | ollama_local | 1.12 | 5 | ✅ **Acierto** (Rechazo estricto: "No lo sabes") |
| **5** | ¿Cuánto cuesta el alquiler en Valencia? | llama3.2:3b | ollama_local | 1.17 | 5 | ✅ **Acierto** (Rechazo educado y contextual) |
| **5** | ¿Cuánto cuesta el alquiler en Valencia? | poligpt | poligpt | 1.17 | 5 | ✅ **Acierto** (Rechazo estricto: "No lo sabes") |
| **5** | ¿Cuánto cuesta el alquiler en Valencia? | gemma3:27b | poligpt | 1.53 | 5 | ✅ **Acierto** (Rechazo estricto: "No lo sabes") |

---

## 2. Interpretación de los Resultados y Hallazgos

El análisis cruzado de los datos obtenidos revela patrones fundamentales sobre el comportamiento de las distintas arquitecturas de modelos:

### A. Capacidad de Síntesis e Inferencia Compleja (Pregunta 4)
* **Los modelos grandes dominan:** El modelo comercial de la cola `poligpt` demostró una superioridad aplastante al responder a la pregunta de síntesis multi-documento. No solo extrajo las diferencias, sino que estructuró de forma autónoma una tabla Markdown comparando públicos, actividades, horarios, lugares y objetivos.
* **El colapso de Llama 3.2 (3b):** Al ser un modelo extremadamente compacto, se vio superado por el volumen de contexto inyectado (5 chunks de 1000 caracteres). En lugar de procesar la diferencia, prefirió acogerse a la cláusula de seguridad del prompt y responder `"No lo sabes."`. Esto demuestra una limitación en su ventana de atención efectiva para tareas de razonamiento multi-doc.
* **Gemma 3 (4b) como "Sweet Spot" local:** A pesar de correr en local, superó a Llama logrando redactar una síntesis fluida que explicaba correctamente el enfoque hacia abuelitos (RESIS) frente al apoyo infantil (COLES).

### B. Adherencia al Prompt y Anti-Alucinación (Pregunta 5)
* Todos los modelos pasaron con nota la prueba de control fuera de ámbito (pregunta sobre el precio de los alquileres). Al no estar la información en el contexto de los 16 archivos `.txt`, ninguno inventó datos ficticios.
* Se aprecia una marcada diferencia de estilo: `gemma3:4b`, `gemma3:27b` y `poligpt` aplicaron una **obediencia literal robótica** devolviendo exactamente el token indicado en el prompt (`"No lo sabes."`), mientras que `llama3.2:3b` mostró un comportamiento más natural y conversacional para denegar la respuesta.

### C. Análisis de Latencia y Eficiencia
* **Estabilidad remota:** Las llamadas a través de PoliGPT mostraron una latencia muy controlada (entre 1.1s y 3.9s), con la única excepción de la tabla compleja generada por `poligpt` (6.07s), totalmente justificada por la cantidad de tokens de salida generados.
* **Fluctuación local:** Las respuestas en local dependieron de la complejidad de la tarea. La inicialización de la consulta visual de Gemma 3 tardó 5.46s (cold start de carga en VRAM) pero se estabilizó inmediatamente en torno a 1.1s - 1.9s para el resto de preguntas.

---

## 3. Conclusión y Elección de Modelo para el Grupo

Para la entrega definitiva del Asistente DNI, nuestro equipo ha decidido seleccionar **`gemma3:27b` a través de PoliGPT** como modelo principal de producción (siempre que la red de la UPV esté disponible), manteniendo **`gemma3:4b` en Ollama** como el motor local obligatorio de respaldo.

**Justificación:** `gemma3:27b` ofrece el equilibrio perfecto: combina la precisión quirúrgica y formato profesional de los modelos de escala comercial con una latencia de respuesta excepcionalmente baja (promedio de ~2.2 segundos), superando las limitaciones cognitivas de los modelos locales de 3b sin sacrificar la seguridad anti-alucinaciones que exige la rúbrica.
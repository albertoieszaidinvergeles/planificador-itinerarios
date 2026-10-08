# Uso de inteligencia artificial en el proyecto

> Registro **crítico** del uso de IA: herramienta/modelo, finalidad, propuesta, si se aceptó
> o se rechazó y **cómo lo verificó el equipo**. Sin secretos, sin conversaciones innecesarias
> ni datos personales. Aquí solo se documenta el uso de la IA; la IA **no** sustituye al equipo.

## Registro

| # | Fecha | Herramienta / modelo | Finalidad | Prompt o resumen relevante | Propuesta (aceptada / rechazada) | Comprobación humana |
|---|---|---|---|---|---|---|
| 1 | 08/10/2026 | Asistente de IA (chat) | Redacción y revisión de la documentación inicial: documento técnico y ERS a partir de la plantilla y de los requisitos indicados | «Adapta la ERS a la plantilla del docente con 3–6 RF y 2–4 RNF; marca App 1 / App 2» | **Aceptada con revisión:** estructura de la plantilla conservada, RF/RNF reescritos y contrastados con el enunciado PR01-UD1 por el equipo | Revisión cruzada entre integrantes (ERS §10.2); el equipo valida cada requisito y lo ajusta a lo que realmente implemente |
| 2 | | | | | | |
| 3 | | | | | | |

## Reglas de uso acordadas

1. **App 1 debe ser manual y progresiva:** se puede preguntar y explicar, pero no delegar la generación integral (los procesos de App 1 y App 2 deben distinguirse).
2. **App 2 usa Spec Kit + asistencia de IA por tareas**, con especificación, plan y tareas **anteriores** al código en Git; se registran prompts relevantes depurados.
3. Toda propuesta de la IA se **revisa**: si propone BD, persistencia, pantallas extra o CRUD, se rechaza y se corrige la especificación/plan (error frecuente del enunciado).
4. No se pegan claves, tokens, respuestas privadas ni conversaciones completas.
5. Las decisiones técnicas finales son del equipo y deben poder defenderse en la defensa.

## Puntos de verificación

| Momento | Qué se revisa | Estado |
|---|---|---|
| Tras la ERS (H0) | Que los RF/RNF redactados coinciden con lo implementado | ⬜ |
| Durante App 2 (H9) | Que las tareas generadas no amplían alcance; correcciones anotadas | ⬜ |
| Antes de la entrega (H12) | Que el registro está completo y sin secretos | ⬜ |

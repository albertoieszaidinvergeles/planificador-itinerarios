# Comparativa App 1 vs App 2

> Registro basado en **evidencias reales** (git, pruebas, URLs). No se presupone que App 2
> sea mejor ni se inventan resultados: todo lo marcado «pendiente» se rellena durante el
> trabajo. El esfuerzo de **Clerk** y el de **infraestructura** se registran aparte del
> tiempo de desarrollo funcional.

## 1. Tiempo por fase (horas aproximadas o estimación identificada)

| Fase | App 1 (manual) | App 2 (Spec Kit + Clerk) | Notas |
|---|---|---|---|
| Análisis y ERS | ⬜ pendiente | ⬜ pendiente | En App 2 parte de la ERS base + Anexo C |
| Especificación/plan/tareas (Spec Kit) | — (no aplica) | ⬜ pendiente | Debe ser anterior al código |
| Backend mínimo + contrato | ⬜ pendiente | ⬜ pendiente | |
| Pruebas (pytest + mocks) | ⬜ pendiente | ⬜ pendiente | |
| Frontend + integración | ⬜ pendiente | ⬜ pendiente | |
| Diseño (Tailwind) y revisión | ⬜ pendiente | ⬜ pendiente | |
| Autenticación Clerk | — (no aplica) | ⬜ pendiente | Contar **aparte** |
| Despliegues (Vercel / Docker+EC2) | ⬜ pendiente (Vercel) | ⬜ pendiente (Vercel + EC2) | Contar **aparte** |
| Revisión y corrección de propuestas IA | ⬜ pendiente | ⬜ pendiente | |

## 2. Calidad

| Dimensión | App 1 | App 2 | Evidencia |
|---|---|---|---|
| Legibilidad del código | ⬜ | ⬜ | Revisión de `app1/` vs `app2/` |
| Validaciones (422) | ⬜ | ⬜ | `docs/pruebas.md` T02–T06 |
| Contrato y errores (502/504/401) | ⬜ | ⬜ | Documento técnico §4 + T07–T12 |
| Consistencia con la ERS | ⬜ | ⬜ | ERS §8 trazabilidad |

## 3. Errores (al menos un ejemplo real si hubo)

| App | Problema concreto | Origen | Solución | Evidencia (commit/issue) |
|---|---|---|---|---|
| 1 | ⬜ pendiente | | | |
| 2 | ⬜ pendiente (p. ej. propuesta de la IA con BD que hubo que rechazar) | | | |

## 4. Mantenibilidad

| Cambio pequeño hipotético | App 1 | App 2 | Justificación |
|---|---|---|---|
| Añadir un campo al formulario | ⬜ | ⬜ | (solo razonar; **no** implementarlo) |
| Cambiar de proveedor de IA | ⬜ | ⬜ | Ambos deberían tocar solo `ia.py` |
| Añadir una segunda pantalla | ⬜ | ⬜ | Debe ser difícil/denegado: lo prohíbe el enunciado |

## 5. Utilidad de la IA en el proceso

| Dónde ayudó | Dónde falló o propuso algo fuera de alcance | Decisiones que mantuvo el equipo |
|---|---|---|
| ⬜ pendiente (`docs/uso-ia.md`) | ⬜ pendiente | ⬜ pendiente |

## 6. Conclusión (solo con evidencias)

- ✅ Mismo escenario de aceptación ejecutado en ambas apps (entrada válida, 422, 502/504; App 2 añade 401).
- ⬜ Pendiente: comparación de tiempos, calidad, errores y mantenibilidad con los datos de las tablas anteriores.

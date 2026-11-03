# Comparativa App 1 vs App 2

> Registro basado en **evidencias reales** (git, pruebas, URLs). No se presupone que App 2
> sea mejor ni se inventan resultados: todo lo marcado «pendiente» se rellena durante el
> trabajo. El esfuerzo de **Clerk** y el de **infraestructura** se registran aparte del
> tiempo de desarrollo funcional.

## 1. Tiempo por fase (horas aproximadas o estimación identificada)

| Fase | App 1 (manual) | App 2 (Spec Kit + Clerk) | Notas |
|---|---|---|---|
| Análisis y ERS | ⬜ pendiente | ✅ base y Anexo C | La ERS común se amplía con los requisitos de Clerk |
| Especificación/plan/tareas (Spec Kit) | — (no aplica) | ✅ terminado | Spec, plan y tareas de App 2 versionados antes del código |
| Backend mínimo + contrato | ⬜ pendiente | ✅ terminado | Backend FastAPI con autenticación Clerk |
| Pruebas (pytest + mocks) | ⬜ pendiente | ✅ 45 pasaron | App 2, 29/10/2026; suite offline |
| Frontend + integración | ⬜ pendiente | ✅ terminado | App 2: F01–F19 en `docs/pruebas.md` |
| Diseño (Tailwind) y revisión | ⬜ pendiente | ✅ terminado | Responsive y revisión hasta 320 px |
| Autenticación Clerk | — (no aplica) | 🟡 producción probada parcialmente | Petición autenticada real confirmada; falta documentar captura y flujo completo de Google/cierre de sesión en producción |
| Despliegues (Vercel / Docker+EC2) | ⬜ pendiente (Vercel) | 🟡 Vercel desplegado; EC2 pendiente (~6 h) | URL y respuestas verificadas en `docs/despliegues.md`; contar **aparte** |
| Revisión y corrección de propuestas IA | ⬜ pendiente | ⬜ pendiente | |

## 2. Calidad

| Dimensión | App 1 | App 2 | Evidencia |
|---|---|---|---|
| Legibilidad del código | ⬜ | ⬜ | Revisión de `app1/` vs `app2/` |
| Validaciones (422) | ⬜ | ✅ backend probado | `docs/pruebas.md` T02–T06 y T14 |
| Contrato y errores (502/504/401) | ⬜ | ✅ backend probado | Documento técnico §4 + T07–T12, T14 |
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

- ✅ Suites backend automatizadas: App 1 registró 41 tests pasados el 17/10; App 2 registró 45 el 29/10, con mocks y sin red.
- ✅ App 2 está desplegada en Vercel: la ruta web devuelve `200`, sin token la API devuelve `401` y Alberto confirma que una petición real autenticada funciona.
- ⬜ Pendiente: documentar con captura el flujo completo de Clerk (Google y cierre de sesión) en producción, desplegar en EC2 y comparar tiempos, calidad, errores y mantenibilidad con el resto de datos.
- ⏱️ Alberto estima unas 3 h para el trabajo de despliegue H10; el desglose está en `docs/changelog.md`.

# Política de seguridad / Security Policy

**[🇬🇧 English version below](#security-policy)**

## Versiones compatibles / Supported versions

| Versión / Version | Soportado / Supported |
|---|---|
| `1.x` (rama `main` / `main` branch) | ✅ |
| `< 1.0` | ✅ (mismo repositorio, sin releases anteriores) |

## Cómo reportar una vulnerabilidad / How to report a vulnerability

**El contacto es únicamente GitHub; no se publican correos electrónicos en este repositorio.**
*Contact is **GitHub only**; no email addresses are published in this repository.*

1. **Canal preferido:** ve a la pestaña **Security** del repositorio → **Report a vulnerability**
   (informe de vulnerabilidad privado). Solo lo ven los mantenedores.
   *Preferred channel: open the repository's **Security** tab → **Report a vulnerability**
   (private vulnerability report). Only the maintainers see it.*
2. **Si la opción no aparece** (depende de la configuración del repositorio): contacta con los
   mantenedores a través de GitHub ([`@albertoieszaidinvergeles`](https://github.com/albertoieszaidinvergeles))
   indicando que el asunto es confidencial y **sin detallar la vulnerabilidad en un issue
   público**; el equipo abrirá un canal privado contigo.
   *If the option is not visible (it depends on repository settings), contact the maintainers via
   GitHub ([`@albertoieszaidinvergeles`](https://github.com/albertoieszaidinvergeles)) stating the
   matter is confidential **without detailing the vulnerability in a public issue**; the team will
   open a private channel with you.*

**Qué incluir en el informe / What to include:**

- Descripción del problema y su impacto / Description of the issue and its impact.
- Pasos para reproducirlo / Steps to reproduce it.
- Versión o URL afectada / Affected version or URL.
- Parche o idea de solución, si lo tienes / Patch or fix idea, if you have one.
- Cómo contactarte de forma privada dentro de GitHub / How to reach you privately on GitHub.

**Qué esperar / What to expect:**

- Confirmación de recepción tan pronto como sea posible (buscamos menos de 7 días).
- Evaluación del impacto y, si procede, corrección en `main` y reconocimiento en
  [`CHANGELOG.md`](CHANGELOG.md) (sin detalles que permitan explotar el fallo antes de corregirlo).
- No habrá represalias por informar de buena fe.

*Acknowledgement as soon as possible (we aim for under 7 days), an impact assessment, a fix on
`main` when appropriate, and credit in [`CHANGELOG.md`](CHANGELOG.md) (without details that would
allow exploiting the issue before it is fixed). No retaliation for reports made in good faith.*

## Alcance y buenas prácticas / Scope and good practices

- **Investigación de buena fe:** no accedas a datos de otras personas, no degrades el servicio
  (sin `DoS`), no pruebes claves ajenas y no sigas explotando el fallo una vez avisado.
  *Good-faith research: do not access other people's data, degrade the service (no `DoS`), test
  other people's keys, or keep exploiting the issue once reported.*
- **No es un fallo (diseño esperado):**
  - Las variables `VITE_*` (incluida `VITE_CLERK_PUBLISHABLE_KEY`) son **públicas por diseño**:
    viajan en el bundle del navegador.
  - El rate limit `429` del WAF y el cierre de `/docs` en producción son medidas deliberadas.
  *Not a bug (expected design): `VITE_*` variables (including `VITE_CLERK_PUBLISHABLE_KEY`) are
  public by design (they ship in the browser bundle); the WAF `429` rate limit and the disabled
  `/docs` in production are deliberate measures.*
- **Sí es un fallo:** cualquier secreto (`AI_API_KEY`, `CLERK_SECRET_KEY`, valores reales de
  `.env`) expuesto en git, en un bundle, en logs o en respuestas HTTP; un plan de IA que filtre la
  clave; o cualquier forma de saltarse la verificación del token en App 2.
  *A real bug: any secret (`AI_API_KEY`, `CLERK_SECRET_KEY`, real `.env` values) exposed in git, in
  a bundle, in logs, or in HTTP responses; an AI plan leaking the key; or bypassing token
  verification in App 2.*

## Medidas ya activas / Measures already in place

- `.env` en `.gitignore`; los `.env.example` solo llevan **nombres y valores ficticios**.
- Claves de IA **solo en el backend** (Vercel/EC2); nunca en el frontend ni en git.
- Verificación de tokens de Clerk (JWKS + RS256) en el backend de App 2.
- Saneado de entrada y del formato de respuesta de la IA (`formato.py`), cabeceras de seguridad y
  `/docs` condicionado en producción.

*.env files are gitignored and `.env.example` files carry only fictitious values; AI keys live
only in the backend; Clerk tokens are verified (JWKS + RS256) in App 2's backend; AI input and
response format are sanitized (`formato.py`), with security headers and conditional `/docs` in
production.*

---

<div id="security-policy"></div>

# Security Policy (English Version)

**[🇪🇸 Versión en español](#política-de-seguridad--security-policy)**

## Supported versions

| Version | Supported |
|---|---|
| `1.x` (`main` branch) | ✅ |
| `< 1.0` | ✅ (same repository, no earlier releases) |

## How to report a vulnerability

**Contact is GitHub only; no email addresses are published in this repository.**

1. **Preferred channel:** go to the repository's **Security** tab → **Report a vulnerability**
   (private vulnerability report). Only the maintainers see it.
2. **If the option is not visible** (it depends on repository settings): contact the maintainers
   via GitHub ([`@albertoieszaidinvergeles`](https://github.com/albertoieszaidinvergeles)) stating
   the matter is confidential **without detailing the vulnerability in a public issue**; the team
   will open a private channel with you.

**What to include:** description and impact, steps to reproduce, affected version or URL, patch or
fix idea if available, and how to reach you privately on GitHub.

**What to expect:** acknowledgement as soon as possible (we aim for under 7 days), an impact
assessment, a fix on `main` when appropriate, and credit in [`CHANGELOG.md`](CHANGELOG.md) without
exploitable details. No retaliation for reports made in good faith.

## Scope and good practices

- **Good-faith research:** do not access other people's data, degrade the service (no `DoS`), test
  other people's keys, or keep exploiting the issue once reported.
- **Not a bug (expected design):** `VITE_*` variables (including `VITE_CLERK_PUBLISHABLE_KEY`) are
  public by design; the WAF `429` rate limit and the disabled `/docs` in production are deliberate
  measures.
- **A real bug:** any secret (`AI_API_KEY`, `CLERK_SECRET_KEY`, real `.env` values) exposed in git,
  in a bundle, in logs, or in HTTP responses; an AI plan leaking the key; or bypassing token
  verification in App 2.

## Measures already in place

`.env` files are gitignored and `.env.example` files carry only fictitious values; AI keys live
only in the backend (Vercel/EC2); Clerk tokens are verified (JWKS + RS256) in App 2's backend; AI
input and response format are sanitized (`formato.py`), with security headers and conditional
`/docs` in production.

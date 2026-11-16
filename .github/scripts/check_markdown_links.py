#!/usr/bin/env python3
"""Comprueba los enlaces relativos y las anclas de todos los .md del repositorio.

Comprobaciones / checks:
  * Enlaces relativos a ficheros o carpetas que existan (rompe si no existen).
    Relative links to files or folders that exist (fails if they do not).
  * Anclas internas (`#seccion`) contra los encabezados del propio documento
    (algoritmo de anclas de GitHub) y contra los `id="..."` explícitos del HTML.
    Internal anchors (`#section`) against the document's own headings (GitHub's
    anchor algorithm) and against explicit HTML `id="..."` attributes.
  * Se ignoran los enlaces externos (http/https/mailto) y los anclas vacías.
    External links (http/https/mailto) and empty anchors are ignored.

Uso / usage:  python .github/scripts/check_markdown_links.py
Salida / exit code: 0 si todo está bien, 1 si hay enlaces rotos.
"""

from __future__ import annotations

import re
import sys
import unicodedata
import urllib.parse
from pathlib import Path

# Consolas Windows (cp1252): imprimir símbolos UTF-8 sin reventar.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[2]

EXCLUDE_DIRS = {
    ".git",
    ".github",  # los .md de .github son plantillas, no documentación enlazable
    ".venv",
    "node_modules",
    "dist",
    "__pycache__",
    ".pytest_cache",
    ".specify",
}

SKIP_PREFIX = ("http://", "https://", "mailto:", "tel:", "ftp://")

# [texto](destino "título")  ·  ![alt](destino)  — también en línea.
LINK_RE = re.compile(r"!?\[[^\]]*\]\(\s*([^)\s]+?)(?:\s+\"[^\"]*\")?\s*\)")
HEADING_RE = re.compile(r"^#{1,6}\s+(.*?)\s*#*\s*$", re.MULTILINE)
ID_RE = re.compile(r"id\s*=\s*\"([^\"]+)\"", re.IGNORECASE)
FENCE_RE = re.compile(r"^```.*?^```", re.MULTILINE | re.DOTALL)


def github_slug(text: str) -> str:
    """Ancla de encabezado al estilo de GitHub (github-slugger)."""
    text = re.sub(r"<[^>]+>", "", text)  # quita <em>, <code>…
    text = re.sub(r"[*_`~]", "", text)  # quita marcado básico
    out = []
    for ch in text.strip().lower():
        cat = unicodedata.category(ch)
        if ch in " -" or cat[0] in ("L", "N", "M"):
            out.append(ch)
        # resto (puntuación, emojis, símbolos): eliminado
    return "".join(out).replace(" ", "-")


def collect_targets(path: Path, text: str) -> set[str]:
    """Anclas válidas del documento: id="..." + slugs de sus encabezados."""
    targets = set(ID_RE.findall(text))
    body = FENCE_RE.sub("", text)  # los encabezados dentro de bloques de código no cuentan
    for match in HEADING_RE.finditer(body):
        targets.add(github_slug(match.group(1)))
    return targets


def main() -> int:
    errors: list[str] = []
    checked = 0

    for path in sorted(ROOT.rglob("*.md")):
        if any(part in EXCLUDE_DIRS for part in path.parts):
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"{path.relative_to(ROOT)}: no se pudo leer como UTF-8")
            continue

        anchors = collect_targets(path, text)

        for match in LINK_RE.finditer(text):
            raw = match.group(1).strip()
            if raw.startswith(SKIP_PREFIX):
                continue
            if raw.startswith("#"):  # ancla del mismo documento
                fragment = urllib.parse.unquote(raw[1:]).lower()
                checked += 1
                if fragment and fragment not in anchors:
                    line = text.count("\n", 0, match.start()) + 1
                    errors.append(
                        f"{path.relative_to(ROOT)}:{line}: ancla inexistente -> #{fragment}"
                    )
                continue

            target = urllib.parse.unquote(raw)
            rel, _, fragment = target.partition("#")
            if not rel:
                continue
            checked += 1
            candidate = (path.parent / rel).resolve()
            line = text.count("\n", 0, match.start()) + 1

            if not candidate.exists():
                errors.append(
                    f"{path.relative_to(ROOT)}:{line}: enlace roto -> {target}"
                )
                continue

            if fragment and candidate.suffix.lower() == ".md":
                try:
                    other = candidate.read_text(encoding="utf-8")
                except (UnicodeDecodeError, OSError):
                    continue
                fragment = urllib.parse.unquote(fragment).lower()
                checked += 1
                if fragment not in collect_targets(candidate, other):
                    errors.append(
                        f"{path.relative_to(ROOT)}:{line}: ancla inexistente en "
                        f"{rel} -> #{fragment}"
                    )

    if errors:
        print("Enlaces rotos / Broken links:")
        for error in errors:
            print(f"  ✗ {error}")
        print(f"\n{len(errors)} problema(s) en {checked} enlace(s) comprobado(s).")
        return 1

    print(f"OK: {checked} enlace(s) comprobado(s), sin problemas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

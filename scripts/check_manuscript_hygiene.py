#!/usr/bin/env python3
"""Check outward manuscript, ledger, README, and bibliography for style and public-surface hygiene."""

from __future__ import annotations

import re
import sys
from pathlib import Path

BANNED_SUBSTRINGS = (
    "thermodynamic",
    "eisv",
    "basin",
    "prevented harm",
    "sk-",
    "OPENAI_API_KEY",
    "/Users/cirwel",
)


def main() -> int:
    targets = [
        Path("paper/main.tex"),
        Path("paper/references.bib"),
        Path("README.md"),
        Path("CLAIMS-LEDGER.md"),
        Path("HYPOTHESES.md"),
        Path("docs/REVIEWS.md"),
        Path("docs/DESIGN-CRITIQUE.md"),
    ]
    violations: list[str] = []
    for path in targets:
        if not path.is_file():
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        for lineno, line in enumerate(lines, 1):
            if "\u2014" in line:
                violations.append(f"{path}:{lineno}: unicode em-dash found")
            if path == Path("paper/main.tex") and "---" in line:
                violations.append(f"{path}:{lineno}: LaTeX em-dash '---' found")
            low = line.lower()
            for term in BANNED_SUBSTRINGS:
                if term.lower() in low:
                    violations.append(f"{path}:{lineno}: banned/sensitive substring {term!r}")
            # Flag raw double-hyphen used as prose dash (whitespace--whitespace) in prose
            if path == Path("paper/main.tex") and not line.lstrip().startswith("%") and re.search(r"\s--\s", line):
                violations.append(f"{path}:{lineno}: spaced double-hyphen dash ' -- ' in prose")
            if path != Path("paper/references.bib") and path != Path("paper/main.tex"):
                if re.search(r"\s--\s", line) and "|" not in line and not line.strip().startswith("#"):
                    # allow CLI flags like `--out` and git `unitares-github -- git ...` only inside backticks
                    stripped_code = re.sub(r"`[^`]*`", "", line)
                    if re.search(r"\s--\s", stripped_code):
                        violations.append(f"{path}:{lineno}: spaced double-hyphen dash outside code span")

    if violations:
        for v in violations:
            print(f"VIOLATION: {v}")
        return 1
    print("HYGIENE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Basic, judgement-free facts about the submitted PDF."""
from __future__ import annotations

from pathlib import Path
from typing import List

from .model import Fact

A4 = (595.3, 841.9)
LETTER = (612.0, 792.0)


def page_format(width: float, height: float) -> str:
    for name, (w, h) in (("A4", A4), ("US Letter", LETTER)):
        if abs(width - w) < 2 and abs(height - h) < 2:
            return name
    return "other"


def open_pdf(path: Path):
    import pdfplumber           # imported lazily so that --check-deps works without it
    return pdfplumber.open(str(path))


def basic_facts(pdf) -> List[Fact]:
    meta = pdf.metadata or {}
    first = pdf.pages[0]
    facts = [
        Fact("pdf", "Pages", str(len(pdf.pages))),
        Fact("pdf", "Page size", f"{page_format(first.width, first.height)} "
                                 f"({first.width:.1f} x {first.height:.1f} pt)"),
    ]
    for key in ("Producer", "Creator"):
        if meta.get(key):
            facts.append(Fact("pdf", key, str(meta[key])))
    return facts

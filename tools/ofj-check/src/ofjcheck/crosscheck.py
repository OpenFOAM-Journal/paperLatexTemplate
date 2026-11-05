"""When both PDF and sources are submitted: does the PDF come from these sources?"""
from __future__ import annotations

import re
from typing import TYPE_CHECKING, List, Optional

from . import generations
from .model import CONVENTION, MEDIUM, Evidence, Finding
from .verdict import channel_range

if TYPE_CHECKING:
    from .analyze import Context


def _braced(text: str, start: int) -> Optional[str]:
    """Content of the {...} group starting at text[start] == '{'."""
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1:i]
    return None


def source_title(doc) -> Optional[str]:
    m = re.search(r"\\title\s*(\[[^\]]*\])?\s*(?=\{)", doc.main.masked)
    if not m:
        return None
    return _braced(doc.main.masked, m.end())


def title_words(title: str) -> List[str]:
    text = title.replace("\\OF", "OpenFOAM")
    text = re.sub(r"\\[A-Za-z]+\*?", " ", text)
    return re.findall(r"[A-Za-z]{4,}", text)


def rule_title_match(ctx: "Context") -> List[Finding]:
    title = source_title(ctx.document)
    if not title:
        return []
    words = title_words(title)
    if len(words) < 3:
        return []
    page1 = ctx.pdf_view.compact(0).lower()
    missing = [w for w in words if w.lower() not in page1]
    if len(missing) <= len(words) / 2:
        return []
    return [Finding("XCHK01", "The PDF does not seem to be made from these sources", kind="info",
                    importance=CONVENTION, reliability=MEDIUM,
                    message=f"Most words of the title in the sources ({len(missing)} of {len(words)}) do "
                            "not appear on page 1 of the PDF. The PDF may belong to another version "
                            "of the manuscript.",
                    evidence=[Evidence(ctx.document.main.rel, " ".join(title.split())[:150]),
                              Evidence("PDF p. 1", "missing: " + ", ".join(missing[:8]))])]


def rule_same_generation(source_findings: List[Finding], pdf_findings: List[Finding]) -> List[Finding]:
    src, pdf = channel_range(source_findings), channel_range(pdf_findings)
    if not src or not pdf or src[1] < pdf[0] or pdf[1] < src[0]:
        if src and pdf:
            g = generations.GENERATIONS
            text = (f"PDF: {generations.describe(g[pdf[0]].id, g[pdf[1]].id)}; "
                    f"sources: {generations.describe(g[src[0]].id, g[src[1]].id)}")
            return [Finding("XCHK02", "PDF and sources point to different template generations",
                            kind="info", importance=CONVENTION, reliability=MEDIUM,
                            message="The PDF and the LaTeX sources were not made with the same template "
                                    "version (" + text + "). The PDF may have been built from older "
                                    "sources, or the authors updated only part of the template.",
                            evidence=[Evidence("PDF / sources", text)])]
    return []


def run_crosschecks(ctx: "Context", source_findings: List[Finding],
                    pdf_findings: List[Finding]) -> List[Finding]:
    if any(f.kind == "not-template" for f in source_findings + pdf_findings):
        return []
    return rule_title_match(ctx) + rule_same_generation(source_findings, pdf_findings)

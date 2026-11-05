"""What the PDF rules need from a PDF, extracted once: text, fonts, links and layout.

pdfplumber often drops the spaces between words set in Computer Modern, so
text is also offered in a "compact" form with all whitespace removed;
patterns are matched against that.
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, List, Optional

MAX_PAGES = 60              # pages examined for fonts, links and layout
HEADER_BOTTOM = 62.0        # running heads sit above this (pt from the top)


def base_font(name: str) -> str:
    """'ABCDEF+CMR10' -> 'CMR10'."""
    return (name or "").split("+")[-1]


def is_small_caps(font: str) -> bool:
    return bool(re.search(r"CSC|Caps|SmallCaps|-SC\b", font, re.I))


def is_bold(font: str) -> bool:
    return bool(re.search(r"BX|Bold|-B$|Black|Heavy|Semibold", font, re.I))


def compact(text: str) -> str:
    return re.sub(r"\s+", "", text or "")


def _decode(value) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        for enc in ("utf-8", "latin-1"):
            try:
                return value.decode(enc)
            except UnicodeDecodeError:
                continue
    name = getattr(value, "name", None)
    if name is not None:
        return str(name)
    return str(value)


@dataclass
class Link:
    page: int                  # 1-based
    text: str                  # text under the link rectangle
    dest: str = ""             # named destination (internal link), e.g. "figure.1"
    uri: str = ""              # external link

    @property
    def target_kind(self) -> str:
        """equation | table | figure | lstlisting | section | cite | ... ('' for external)."""
        return self.dest.split(".", 1)[0] if self.dest else ""


class PdfView:
    def __init__(self, pdf):
        self.pdf = pdf
        self.pages = pdf.pages[:MAX_PAGES]
        self.page_count = len(pdf.pages)

    # -------------------------------------------------------------- basics
    @property
    def metadata(self) -> Dict[str, str]:
        return {str(k): _decode(v) for k, v in (self.pdf.metadata or {}).items()}

    @property
    def size(self):
        p = self.pages[0]
        return float(p.width), float(p.height)

    @lru_cache(maxsize=None)
    def text(self, i: int) -> str:
        return self.pages[i].extract_text() or ""

    @lru_cache(maxsize=None)
    def compact(self, i: int) -> str:
        return compact(self.text(i))

    @lru_cache(maxsize=None)
    def lines(self, i: int) -> List[dict]:
        return self.pages[i].extract_text_lines(return_chars=True)

    @lru_cache(maxsize=None)
    def words(self, i: int) -> List[dict]:
        return self.pages[i].extract_words(extra_attrs=["fontname", "size"], keep_blank_chars=False)

    def find_line(self, i: int, pattern: str) -> Optional[str]:
        """The (raw) text line on page i whose compact form matches pattern."""
        rx = re.compile(pattern)
        for line in self.lines(i):
            if rx.search(compact(line["text"])):
                return line["text"].strip()
        return None

    # -------------------------------------------------------------- fonts and layout
    @lru_cache(maxsize=None)
    def font_counts(self) -> Counter:
        counts: Counter = Counter()
        for page in self.pages[:10]:
            for ch in page.chars:
                if ch["text"].strip():
                    counts[base_font(ch["fontname"])] += 1
        return counts

    @lru_cache(maxsize=None)
    def body_font(self) -> str:
        """Most frequent font among text-sized characters (8.5–11.5 pt)."""
        counts: Counter = Counter()
        for page in self.pages[:10]:
            for ch in page.chars:
                if 8.5 <= ch["size"] <= 11.5 and ch["text"].strip():
                    counts[base_font(ch["fontname"])] += 1
        return counts.most_common(1)[0][0] if counts else ""

    @lru_cache(maxsize=None)
    def text_block(self) -> Optional[tuple]:
        """Left and right edge of the body text (body font, normal size), pages 1–4."""
        body = self.body_font()
        xs0, xs1 = [], []
        for page in self.pages[:4]:
            height = float(page.height)
            for ch in page.chars:
                if base_font(ch["fontname"]) == body and 9.0 <= ch["size"] <= 11.5 \
                        and HEADER_BOTTOM < ch["top"] < height - 60 and ch["text"].strip():
                    xs0.append(ch["x0"])
                    xs1.append(ch["x1"])
        if len(xs0) < 50:
            return None
        return min(xs0), max(xs1)

    def line_numbers(self, i: int) -> int:
        """Margin line numbers (lineno): tiny sans-serif digits left of the text block."""
        n = 0
        for w in self.words(i):
            if w["text"].isdigit() and w["x1"] < 69 and w["size"] < 7.5 \
                    and re.search(r"SS|Sans", base_font(w["fontname"])):
                n += 1
        return n

    def header_text(self, i: int) -> str:
        """Running head of page i (text above the text block, without the page number)."""
        parts = [w["text"] for w in self.words(i) if w["bottom"] < HEADER_BOTTOM]
        return " ".join(p for p in parts if not p.isdigit())

    # -------------------------------------------------------------- links
    @lru_cache(maxsize=None)
    def links(self) -> List[Link]:
        out = []
        for page in self.pages:
            for a in page.annots or []:
                data = a.get("data") or {}
                if _decode(data.get("Subtype")).strip("/'") not in ("Link", ""):
                    continue
                dest = data.get("Dest")
                action = data.get("A") or {}
                if dest is None and isinstance(action, dict):
                    dest = action.get("D")
                uri = a.get("uri") or ""
                dest_name = _decode(dest) if isinstance(dest, (bytes, str)) or hasattr(dest, "name") else ""
                x0, x1, top, bottom = a["x0"], a["x1"], a["top"], a["bottom"]
                chars = [c for c in page.chars
                         if x0 - 0.5 <= (c["x0"] + c["x1"]) / 2 <= x1 + 0.5
                         and top - 0.5 <= (c["top"] + c["bottom"]) / 2 <= bottom + 0.5]
                text = "".join(c["text"] for c in chars).strip()
                out.append(Link(page.page_number, text, dest_name.strip("/'"), _decode(uri)))
        return out

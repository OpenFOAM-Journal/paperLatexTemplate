"""Research helper: dump fingerprint-relevant facts from each reference PDF.

Usage: python -I inspect_pdfs.py <pdf_dir> <out_md>
"""
import collections
import sys
from pathlib import Path

import pdfplumber


def words_with_font(page):
    return page.extract_words(extra_attrs=["fontname", "size"], keep_blank_chars=False)


def font_of(words, token):
    for w in words:
        if w["text"].strip(".:") == token:
            return f"{w['fontname'].split('+')[-1]} {w['size']:.1f}pt"
    return "-"


def link_texts(pdf):
    """Text covered by each internal link annotation (hyperref)."""
    out = []
    for page in pdf.pages:
        for a in page.annots or []:
            data = a.get("data", {})
            if data.get("Subtype") and str(data["Subtype"]).strip("/'") != "Link":
                continue
            uri = a.get("uri")
            x0, top, x1, bottom = a["x0"], a["top"], a["x1"], a["bottom"]
            crop = page.within_bbox((max(x0 - 0.5, 0), max(top - 0.5, 0),
                                     min(x1 + 0.5, page.width), min(bottom + 0.5, page.height)))
            txt = (crop.extract_text() or "").replace("\n", " ").strip()
            out.append(("URI " + uri) if uri else txt)
    return out


def main(pdf_dir, out_md):
    lines = ["# Reference PDF inspection\n"]
    for pdf_path in sorted(Path(pdf_dir).glob("*.pdf")):
        with pdfplumber.open(pdf_path) as pdf:
            p1 = pdf.pages[0]
            md = {k: str(v)[:120] for k, v in (pdf.metadata or {}).items()}
            fonts = collections.Counter()
            for page in pdf.pages:
                for ch in page.chars:
                    fonts[ch["fontname"].split("+")[-1]] += 1
            w1 = words_with_font(p1)
            all_words = [w for pg in pdf.pages for w in words_with_font(pg)]
            text1 = p1.extract_text() or ""
            text2 = pdf.pages[1].extract_text() if len(pdf.pages) > 1 else ""
            lines += [f"\n## {pdf_path.name}\n",
                      f"- pages: {len(pdf.pages)}; size: {p1.width:.1f} x {p1.height:.1f} pt",
                      f"- metadata: {md}",
                      f"- fonts: {dict(fonts.most_common())}",
                      f"- 'Introduction' heading font: {font_of(all_words, 'Introduction')}",
                      f"- 'Abstract' label font: {font_of(all_words, 'Abstract')}",
                      f"- 'Figure' caption font: {font_of(all_words, 'Figure')}",
                      f"- 'Table' caption font: {font_of(all_words, 'Table')}",
                      f"- link annotations: {link_texts(pdf)}",
                      "\n<details><summary>page 1 text</summary>\n\n```",
                      text1, "```\n</details>\n",
                      "<details><summary>page 2 first lines</summary>\n\n```",
                      "\n".join((text2 or "").splitlines()[:4]), "```\n</details>"]
    Path(out_md).write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

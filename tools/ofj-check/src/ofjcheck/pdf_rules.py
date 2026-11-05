"""Fingerprint rules for the submitted PDF (docs/FINGERPRINTS.md, sections 6 and 7).

First the title page is checked for the elements every OFJ template has
printed since 2021. If too few are present, the PDF was not made with the
template and only "not the template" findings are reported. Otherwise the
version fingerprints run, together with the anonymity check for review builds
(decision D1).
"""
from __future__ import annotations

import re
from typing import TYPE_CHECKING, List, Optional, Tuple

from .model import (CONVENTION, COSMETIC, INFO, MEDIUM, REQUIRED, STRONG, WEAK, Evidence,
                    Finding)
from .pdf_facts import page_format
from .pdf_view import PdfView, base_font, compact, is_bold, is_small_caps
from .source_rules import (ADVICE_REFS, CHANGE, COPYRIGHT_YEARS, _generation_of_marker,
                           head_copyright_year, signal)

if TYPE_CHECKING:
    from .analyze import Context

TEMPLATE_X = (70.9, 524.4)          # body text block, 2.5 cm margins on A4 (G02+)
G01_X = (126.7, 485.3)              # AMS default margins on US Letter (G01)
TOLERANCE = 4.0

CHANGE_PDF = {
    "layout": "2023-02-08, PR #30: small capitals replaced by bold in headings, abstract and "
              "captions; capitals removed from author names and running heads",
    "metadata": "2023-02-08, PRs #27/#33: title-page metadata as 'DOI / Results with version(s) / "
                "Repository' (before: 'DOI / Version(s) / Repo')",
    "header": "2021-11-22, commit 7aad18e: 'Volume 123 ... ISSN: TBD'; 2022-05-04, commit 48b3c92: "
              "'Volume 2 [Enter correct Journal Section here]' and ISSN 2753-8168",
    "logo": "2022-05-18, commit 029028a: vector logo (OpenFOAMJournal.pdf instead of .png)",
    "received": "2021-11-22, commit 7aad18e: 'Received: ...' placeholder replaced "
                "'Received by the editors'",
    "paper": "2021-08-30, commit 15fc5c2: US Letter → A4; 2021-08-27: 2.5 cm margins",
}

TEX_PRODUCERS = ("pdftex", "xetex", "luatex", "latex", "dvipdf", "tex live", "miktex", "tectonic")
WORD_PROCESSORS = ("microsoft word", "microsoft® word", "word for", "libreoffice", "openoffice",
                   "writer", "google docs", "wps office", "pages")
REPROCESSORS = ("quartz", "ghostscript", "distiller", "print to pdf", "ilovepdf", "smallpdf",
                "pdf24", "acrobat", "skia", "chrome", "pdfsharp", "itext")


def _near(value: float, target: float) -> bool:
    return abs(value - target) <= TOLERANCE


def _ev(page: int, text: Optional[str]) -> Evidence:
    return Evidence(f"PDF p. {page}", (text or "")[:160])


# ---------------------------------------------------------------- template or not

def template_markers(view: PdfView) -> List[Tuple[str, bool, str]]:
    """(element, present, evidence) for the elements of the OFJ title page."""
    p1 = view.compact(0)
    block = view.text_block()
    width, height = view.size
    layout = block is not None and page_format(width, height) in ("A4", "US Letter") and (
        (_near(block[0], TEMPLATE_X[0]) and _near(block[1], TEMPLATE_X[1])) or
        (_near(block[0], G01_X[0]) and _near(block[1], G01_X[1])))
    return [
        ("journal header (Volume ... / ISSN)", bool(re.search(r"ISSN:|Volume\d+.{0,60}Pages|Sxxxx-yyyy", p1)),
         view.find_line(0, r"ISSN:|Volume\d+") or ""),
        ("title-page footnote (Corresponding author / Received)",
         bool(re.search(r"Correspondingauthor|Received:|Receivedbytheeditors", p1)),
         view.find_line(0, r"Received") or ""),
        ("copyright line", bool(re.search(r"\d{4}(TheAuthors|OpenFOAM)", p1)),
         view.find_line(0, r"\d{4}(TheAuthors|OpenFOAM)") or ""),
        ("metadata block (DOI / Repository)", "DOI:" in p1 and bool(re.search(r"Repository:|Repo:", p1)),
         view.find_line(0, r"DOI:") or ""),
        ("page and text block of the template", layout,
         f"{page_format(width, height)}, text from x = {block[0]:.1f} to {block[1]:.1f} pt" if block else
         f"{page_format(width, height)}"),
    ]


def producer_kind(meta: dict) -> str:
    text = f"{meta.get('Producer', '')} {meta.get('Creator', '')}".lower()
    if any(k in text for k in TEX_PRODUCERS):
        return "tex"
    if any(k in text for k in WORD_PROCESSORS):
        return "word-processor"
    if any(k in text for k in REPROCESSORS):
        return "reprocessed"
    return "unknown"


def rule_producer(view: PdfView) -> List[Finding]:
    meta = view.metadata
    kind = producer_kind(meta)
    who = " / ".join(v for v in (meta.get("Producer"), meta.get("Creator")) if v) or "not recorded"
    if kind == "word-processor":
        return [Finding("NOT01", "PDF made with a word processor", kind="not-template",
                        importance=REQUIRED, reliability=STRONG,
                        message=f"The PDF was produced by '{who}', not by LaTeX. The OFJ template is "
                                "a LaTeX template.", evidence=[Evidence("PDF metadata", who)],
                        advice="Please prepare the manuscript with the OFJ LaTeX template.")]
    if kind == "reprocessed":
        return [Finding("PDF17", "PDF was re-processed after LaTeX", kind="info", importance=INFO,
                        reliability=MEDIUM,
                        message=f"The PDF was written by '{who}' (printing to PDF, merging, "
                                "compressing ...). Links and fonts may have been changed, so some "
                                "checks are less reliable.", evidence=[Evidence("PDF metadata", who)])]
    return []


def rule_fonts(view: PdfView) -> List[Finding]:
    body = view.body_font()
    if not body:
        return []
    if re.match(r"CMR\d|LMRoman|LMSerif|LatinModern", body, re.I):
        return []
    if re.match(r"SFRM|EC-|cmr-T1", body, re.I):
        return [Finding("PDF15", "T1-encoded Computer Modern fonts", kind="modified", importance=COSMETIC,
                        reliability=MEDIUM,
                        message=f"The body font is {body} (cm-super), i.e. \\usepackage[T1]{{fontenc}} "
                                "was added; the current template does not load it (proposed in PR #47).",
                        evidence=[Evidence("PDF fonts", body)])]
    return [Finding("PDF15", f"Body font {body} is not Computer Modern", kind="modified",
                    importance=CONVENTION, reliability=MEDIUM,
                    message=f"The main text is set in {body}. The OFJ template uses Computer Modern "
                            "(CMR10 with pdfLaTeX).", evidence=[Evidence("PDF fonts", body)],
                    advice="Please keep the fonts of the template.")]


def not_template_findings(view: PdfView, markers) -> List[Finding]:
    present = [m for m in markers if m[1]]
    missing = [m[0] for m in markers if not m[1]]
    width, height = view.size
    ev = [Evidence("PDF p. 1", f"missing: {name}") for name in missing]
    ev.append(Evidence("PDF", f"page size {page_format(width, height)} ({width:.1f} x {height:.1f} pt), "
                              f"body font {view.body_font() or '-'}"))
    findings = [Finding("NOT02", "Title page of the OFJ template not found", kind="not-template",
                        importance=REQUIRED, reliability=STRONG,
                        message=f"Only {len(present)} of the {len(markers)} elements that every OFJ "
                                "template prints on the first page were found ("
                                + (", ".join(m[0] for m in present) or "none") + "). The PDF was "
                                "almost certainly not made with the OFJ template.",
                        evidence=ev, advice="Please prepare the manuscript with the OFJ LaTeX template.")]
    return findings + rule_producer(view) + rule_fonts(view)


# ---------------------------------------------------------------- version fingerprints

def rule_page_layout(view: PdfView) -> List[Finding]:
    width, height = view.size
    fmt = page_format(width, height)
    block = view.text_block()
    findings = []
    where = f"{fmt}, text block x = {block[0]:.1f}-{block[1]:.1f} pt" if block else fmt
    if fmt == "US Letter" and block and _near(block[0], G01_X[0]):
        findings.append(signal("PDF01", "US Letter with AMS margins (2021 template)", ("G01", "G01"),
                               "The page is US Letter with the narrow AMS text block of the first "
                               "template; since 2021-08-30 the template uses A4 with 2.5 cm margins.",
                               [Evidence("PDF", where)], change=CHANGE_PDF["paper"]))
    elif fmt == "A4" and block and _near(block[0], TEMPLATE_X[0]) and _near(block[1], TEMPLATE_X[1]):
        findings.append(signal("PDF01", "A4 with 2.5 cm margins", ("G02", None),
                               "Page size and text block as in the template since 2021-08-30.",
                               [Evidence("PDF", where)], reliability=STRONG))
    else:
        findings.append(Finding("PDF02", "Page size or margins differ from the template", kind="modified",
                                importance=CONVENTION, reliability=STRONG,
                                message="The template prints on A4 with 2.5 cm margins (text from "
                                        f"x = {TEMPLATE_X[0]} to {TEMPLATE_X[1]} pt). This PDF: {where}.",
                                evidence=[Evidence("PDF", where)],
                                advice="Please keep the page layout of the template."))
    return findings


def _heading_fonts(view: PdfView) -> List[Tuple[str, int, str, float, str]]:
    """(element, page, font, size, text) for section headings, the abstract label and captions."""
    found = []
    for i in range(min(len(view.pages), 6)):
        words = view.words(i)
        for j, w in enumerate(words[:-1]):
            nxt = words[j + 1]
            same_line = abs(nxt["top"] - w["top"]) < 2
            if re.fullmatch(r"\d+\.", w["text"]) and same_line and re.match(r"[A-Za-z]", nxt["text"]) \
                    and w["x0"] > 80:                 # centred, not a numbered list in the margin
                found.append(("section heading", i + 1, base_font(nxt["fontname"]), nxt["size"],
                              f"{w['text']} {nxt['text']}"))
            elif re.fullmatch(r"(Figure|Table|FIGURE|TABLE)", w["text"]) and same_line \
                    and re.fullmatch(r"\d+\.?", nxt["text"]):
                found.append(("caption label", i + 1, base_font(w["fontname"]), w["size"],
                              f"{w['text']} {nxt['text']}"))
        if i == 0:
            for w in words:
                if w["text"].startswith(("Abstract.", "ABSTRACT.")):
                    found.append(("abstract label", 1, base_font(w["fontname"]), w["size"], "Abstract."))
                    break
    return found


def rule_heading_style(view: PdfView) -> List[Finding]:
    items = _heading_fonts(view)
    describe = lambda es: [Evidence(f"PDF p. {p}", f"{el}: '{t}' in {f}") for el, p, f, _, t in es]  # noqa: E731
    caps = [e for e in items if is_small_caps(e[2])]
    bold = [e for e in items if is_bold(e[2])]
    big = [e for e in items if e[0] == "section heading" and e[3] > 11.5]
    findings = []
    if caps:
        findings.append(signal("PDF03", "Headings and captions in small capitals (pre-2023 class)",
                               ("G01", "G06"),
                               "Section headings, the 'Abstract.' label or caption labels are set in "
                               "small capitals, as by the class files before 2023-02-08. The current "
                               "class sets them in bold.", describe(caps[:5]),
                               change=CHANGE_PDF["layout"], importance=REQUIRED))
    elif bold and not big:
        findings.append(signal("PDF03", "Bold headings and captions", ("G07", None),
                               "Headings and caption labels in bold, as in the class since 2023-02-08.",
                               describe(bold[:3]), change=CHANGE_PDF["layout"], reliability=STRONG))
    if big:
        findings.append(Finding("PDF04", "Section headings larger than the template's", kind="modified",
                                importance=CONVENTION, reliability=MEDIUM,
                                message="The template sets section headings in the text size (10 pt), "
                                        f"centred; here they are {big[0][3]:.1f} pt, as in other "
                                        "document classes such as 'article'.",
                                evidence=describe(big[:3]),
                                advice="Please use the OFJ template's document class."))
    return findings


def rule_running_head(view: PdfView) -> List[Finding]:
    for i in range(1, min(len(view.pages), 4)):
        head = view.header_text(i)
        letters = [c for c in head if c.isalpha()]
        if len(letters) < 8:
            continue
        upper = sum(c.isupper() for c in letters) / len(letters)
        ev = [Evidence(f"PDF p. {i + 1} (running head)", head[:120])]
        if upper > 0.9:
            return [signal("PDF05", "Running head in capitals (pre-2023 class)", ("G01", "G06"),
                           "The running head is set in capitals, as by the class before 2023-02-08.",
                           ev, change=CHANGE_PDF["layout"], importance=REQUIRED)]
        return [signal("PDF05", "Running head in mixed case", ("G07", None),
                       "Running head in mixed case, as in the class since 2023-02-08.", ev,
                       change=CHANGE_PDF["layout"], reliability=MEDIUM)]
    return []


def rule_title_page(view: PdfView, ctx: "Context") -> List[Finding]:
    p1 = view.compact(0)
    findings = []
    # metadata labels
    if "Resultswithversion(s):" in p1:
        findings.append(signal("PDF06", "Title-page labels 'Results with version(s) / Repository'", ("G07", None),
                               "As in the class since 2023-02-08.",
                               [_ev(1, view.find_line(0, r"Resultswithversion"))], change=CHANGE_PDF["metadata"]))
    elif re.search(r"Version\(s\):", p1) and re.search(r"Repo:", p1):
        findings.append(signal("PDF06", "Title-page labels 'Version(s) / Repo' (pre-2023 class)", ("G01", "G07"),
                               "The title page labels the metadata 'Version(s)' and 'Repo', as the "
                               "class did before 2023-02-08; now 'Results with version(s)' and "
                               "'Repository'.", [_ev(1, view.find_line(0, r"Version\(s\):"))],
                               change=CHANGE_PDF["metadata"], importance=REQUIRED))
    # journal header
    if "ISSN:2753-8168" in p1:
        findings.append(signal("PDF07", "Header with ISSN 2753-8168", ("G04", None),
                               "Journal header as in the class since 2022-05-04.",
                               [_ev(1, view.find_line(0, r"ISSN:"))], change=CHANGE_PDF["header"]))
    elif "ISSN:TBD" in p1:
        findings.append(signal("PDF07", "Header 'ISSN: TBD' (2021/22 class)", ("G02", "G03"),
                               "The journal header shows 'ISSN: TBD', as the class did from 2021-11-22 "
                               "to 2022-05-03; since then the ISSN 2753-8168.",
                               [_ev(1, view.find_line(0, r"ISSN:"))], change=CHANGE_PDF["header"],
                               importance=REQUIRED))
    elif re.search(r"Sxxxx-yyyy|Volume00,Pages000", p1):
        findings.append(signal("PDF07", "AMS placeholder header (2021 class)", ("G01", "G02"),
                               "The header shows the AMS placeholders 'Volume 00, Pages 000-000' and "
                               "'Sxxxx-yyyy', as the class did before 2021-11-22.",
                               [_ev(1, view.find_line(0, r"Volume|Sxxxx"))], change=CHANGE_PDF["header"],
                               importance=REQUIRED))
    # logo
    first_lines = "".join(l["text"] for l in view.lines(0)[:3])
    if re.search(r"Open\s*FOAM", first_lines) and "Journal" in first_lines:
        findings.append(signal("PDF08", "Vector journal logo", ("G04", None),
                               "The logo is the vector version used since 2022-05-18.",
                               [_ev(1, "logo text 'OpenFOAM Journal'")], change=CHANGE_PDF["logo"],
                               reliability=WEAK))
    # Received placeholder footnote
    if "Receivedbytheeditors" in p1:
        findings.append(signal("PDF10", "'Received by the editors' footnote (2021 class)", ("G01", "G02"),
                               "The title-page footnote reads 'Received by the editors <date>', as in "
                               "the class before 2021-11-22.", [_ev(1, view.find_line(0, r"Receivedby"))],
                               change=CHANGE_PDF["received"], importance=COSMETIC))
    elif "Received:14Juntember2022" in p1:
        findings.append(signal("PDF10", "'Received: 14 Juntember 2022' placeholder", ("G02", None),
                               "The class's date placeholder (since 2021-11-22) is present.",
                               [_ev(1, view.find_line(0, r"Received:"))], change=CHANGE_PDF["received"],
                               reliability=MEDIUM))
    findings += rule_copyright_pdf(view, ctx)
    return findings


def rule_copyright_pdf(view: PdfView, ctx: "Context") -> List[Finding]:
    p1 = view.compact(0)
    m = re.search(r"(\d{4})TheAuthors", p1)
    if not m:
        if re.search(r"\d{4}OpenFOAM\S{0,4}Journal", p1):
            return [signal("PDF09", "Copyright holder 'OpenFOAM Journal' (pre-2022 template)", ("G01", "G02"),
                           "The copyright line names the OpenFOAM Journal; since 2022-03-02 the "
                           "template prints '© The Authors ... CC BY-SA 4.0'.",
                           [_ev(1, view.find_line(0, r"\d{4}OpenFOAM"))], change=CHANGE["copyright_holder"])]
        return [Finding("PDF09", "No copyright line on page 1", kind="modified", importance=COSMETIC,
                        reliability=MEDIUM,
                        message="Every template since 2021 prints a copyright and licence line at the "
                                "bottom of page 1 ('© <year> The Authors. This work is an open access "
                                "article under the CC BY-SA 4.0 license'); this PDF has none, so the "
                                "\\copyrightinfo line was probably removed.",
                        evidence=[Evidence("PDF p. 1", "no copyright line")],
                        advice="Please keep the \\copyrightinfo line of the template.")]
    year = m.group(1)
    current = head_copyright_year(ctx)
    ev = [_ev(1, view.find_line(0, r"\d{4}TheAuthors"))]
    if year == current:
        return [signal("PDF09", f"Copyright year {year}", COPYRIGHT_YEARS.get(year, ("G10", None)),
                       f"Copyright year {year}, as in the current template.", ev, reliability=WEAK)]
    rng = COPYRIGHT_YEARS.get(year)
    msg = (f"The copyright line says {year}; the current template says {current}. The year is "
           "updated by the editor, so this is only a hint")
    if rng:
        from . import generations
        return [signal("PDF09", f"Copyright year {year} (current template: {current})", rng,
                       msg + f": {year} was the template's year in {generations.describe(*rng)}.", ev,
                       change=CHANGE["copyright_year"], importance=COSMETIC, reliability=MEDIUM,
                       advice="")]           # D3: the editor sets the year; nothing for the authors
    return [Finding("PDF09", f"Copyright year {year} (current template: {current})", kind="modified",
                    importance=COSMETIC, reliability=WEAK,
                    message=msg + f"; the template never used {year}, so it was probably edited.",
                    evidence=ev, template_change=CHANGE["copyright_year"])]


NAMED_REF = re.compile(r"^(Eqn|Tab|Fig|Lst)\.")
DEFAULT_REF = re.compile(r"^(Equation|Table|Figure|Listing|Eq\.|Equations|Tables|Figures)")
REF_TARGETS = ("equation", "table", "figure", "lstlisting", "AMS")


def rule_cross_reference_links(view: PdfView, ctx: "Context") -> List[Finding]:
    links = [l for l in view.links() if l.target_kind in REF_TARGETS]
    if not links:
        return []
    template_names = [l for l in links if NAMED_REF.match(l.text)]
    default_names = [l for l in links if DEFAULT_REF.match(l.text)]
    number_only = [l for l in links if re.fullmatch(r"\(?[\d.]+\)?", l.text)]
    ev = lambda ls: [Evidence(f"PDF p. {l.page} (link)", f"'{l.text}' -> {l.dest}") for l in ls[:5]]  # noqa: E731
    if "cleveref" in ctx.head_main_tex:
        return []              # the current template would then put names into links itself
    findings = []
    if template_names:
        findings.append(signal("PDF11", f"Cross-references made with \\autoref ({len(template_names)} links "
                                        "include 'Eqn./Tab./Fig.')", ("G07", "G10"),
                               "The links to equations, tables or figures cover the word as well as "
                               "the number ('Fig. 1'), which is what \\autoref with the template's "
                               "names Tab./Fig./Eqn. produces (template from 2023-02-25 to 2026-03-31). "
                               "The current template writes Fig.~\\ref{...}, which links only the number.",
                               ev(template_names), change=CHANGE["autoref_removed"], advice=ADVICE_REFS))
    if default_names:
        findings.append(signal("PDF11", f"Cross-references made with \\autoref ({len(default_names)} links "
                                        "include 'Equation/Table/Figure')", ("G05", "G10"),
                               "The links cover a word such as 'Figure' as well as the number, which is "
                               "what \\autoref produces (template from 2022-12-27 to 2026-03-31). The "
                               "current template writes Fig.~\\ref{...}, which links only the number.",
                               ev(default_names), change=CHANGE["autoref_added"], advice=ADVICE_REFS))
    if number_only and not findings:
        findings.append(Finding("PDF11", f"Cross-references link only the number ({len(number_only)} links)",
                                kind="consistent", importance=INFO, reliability=WEAK,
                                message="As with Eqn.~\\ref{...} in the current template (or \\ref in "
                                        "templates before 2022-12). Templates from 2022-12-27 to "
                                        "2026-03-31 used \\autoref, which links the word too.",
                                evidence=ev(number_only[:2]),
                                excludes_from="G06", excludes_to="G10"))   # G05 got \autoref only on 12-27
    return findings


def rule_review_build(view: PdfView) -> List[Finding]:
    """Decision D1: submissions are anonymous review builds."""
    p1 = view.compact(0)
    full_text = " ".join(view.text(i) for i in range(len(view.pages)))
    ev = []
    if "Emailaddress:" in p1:
        ev.append(_ev(1, view.find_line(0, r"Emailaddress:")))
    for m in re.finditer(r"[\w.+-]+@[\w-]+\.[\w.-]+", view.text(0)):
        ev.append(_ev(1, m.group(0)))
        break
    orcid = [l for l in view.links() if "orcid.org" in l.uri]
    if orcid:
        ev.append(Evidence(f"PDF p. {orcid[0].page} (link)", orcid[0].uri))
    repo = re.search(r"Repository:(https?://\S{4,60}?)(?:Abstract|$)", p1)
    if repo:
        ev.append(_ev(1, f"Repository: {repo.group(1)}"))
    contrib = re.search(r"AuthorContributions:", compact(full_text))
    if contrib:
        ev.append(Evidence("PDF", "'Author Contributions:' paragraph"))
    if not ev:
        return []
    return [Finding("PDF14", "Author information visible (not an anonymous review build)",
                    kind="anonymity", importance=REQUIRED, reliability=STRONG,
                    message="Submissions are reviewed double-blind, but this PDF shows information that "
                            "identifies the authors. The template's review build ('make review') hides "
                            "names, addresses, e-mails, ORCID links, the repository, acknowledgements "
                            "and author contributions.", evidence=ev,
                    advice="Please submit the anonymous review version built with 'make review'.")]


def rule_line_numbers(view: PdfView, anonymous: bool) -> List[Finding]:
    numbered = view.line_numbers(0)
    if numbered >= 5 and not anonymous:
        return [signal("PDF13", "Line numbers in a non-review build", ("G01", "G06"),
                       "The PDF shows the authors (so it is not a review build) and still has margin "
                       "line numbers, which the template printed in every build before 2023-01-30.",
                       [Evidence("PDF p. 1", f"{numbered} margin line numbers")],
                       change=CHANGE["linenumbers"], importance=COSMETIC, reliability=WEAK)]
    return []


def rule_old_eq_wording(view: PdfView) -> List[Finding]:
    hits = []
    for i in range(len(view.pages)):
        for m in re.finditer(r"Eq\.\(?\d", view.compact(i)):
            hits.append(Evidence(f"PDF p. {i + 1}", m.group(0)))
    if not hits:
        return []
    return [Finding("PDF12", f"Equations referred to as 'Eq.' ({len(hits)}x)", kind="style",
                    importance=CONVENTION, reliability=MEDIUM,
                    message="The current template refers to equations as 'Eqn. 1'; this PDF writes "
                            "'Eq. 1'. This is a convention, not a sign of a particular template version.",
                    evidence=hits[:5], advice=ADVICE_REFS)]


def _spaced_date(text: str) -> str:
    return re.sub(r"(\d{1,2})([A-Za-z]+)(\d{4})", r"\1 \2 \3", text)


def rule_production_pdf(view: PdfView) -> List[Finding]:
    """Journal data instead of the class's placeholders: a production / published version."""
    p1 = view.compact(0)
    data = []
    m = re.search(r"Volume(\d+)\[([^\]]*)\],Pages(\d+)[–-](\d+)", p1)
    if m and (m.group(2) != "EntercorrectJournalSectionhere" or (m.group(3), m.group(4)) != ("1", "999")):
        data.append(f"Volume {m.group(1)} [{m.group(2)}], pages {m.group(3)}-{m.group(4)}")
    for key in ("Received", "Accepted", "Published"):
        d = re.search(key + r":(\d{1,2}[A-Za-z]+\d{4})", p1)
        if d and "Juntember" not in d.group(1) and "Januaril" not in d.group(1) and "Decemby" not in d.group(1):
            data.append(f"{key.lower()} {_spaced_date(d.group(1))}")
    if not data:
        return []
    return [Finding("PRD02", "Production version: journal data on the title page", kind="production",
                    importance=INFO, reliability=STRONG,
                    message="The title page shows real journal data instead of the template's "
                            f"placeholders ({'; '.join(data)}). This is a production or published "
                            "version, not an author submission; author information and the copyright "
                            "year are expected to be filled in.",
                    evidence=[_ev(1, "; ".join(data))])]


def rule_pdf_version_marker(view: PdfView) -> List[Finding]:
    """Optional template version in the PDF metadata (requirement R9)."""
    for key, value in view.metadata.items():
        text = f"{key} {value}"
        m = re.search(r"(?i)ofj[- _]?template[- _]?version\s*[:=]?\s*([\w./-]+)", text) \
            or (re.search(r"(?i)ofj.*template.*version", key) and re.match(r"\s*([\w./-]+)", value))
        if not m:
            continue
        value = m.group(1)
        gen = _generation_of_marker(value)
        if gen is None:
            return [Finding("VER02", f"Template version in the PDF metadata: '{value}'", kind="info",
                            importance=INFO, reliability=STRONG,
                            message="The PDF declares a template version that this version of "
                                    "ofj-check does not know.", evidence=[Evidence("PDF metadata", text[:120])])]
        from . import generations
        rng = (gen, None if gen == generations.CURRENT else gen)
        return [signal("VER02", f"Template version in the PDF metadata: '{value}'", rng,
                       f"The PDF declares template version '{value}' ({gen}).",
                       [Evidence("PDF metadata", text[:120])])]
    return []


def run_pdf_rules(ctx: "Context") -> List[Finding]:
    view = ctx.pdf_view
    markers = template_markers(view)
    if sum(1 for m in markers if m[1]) < 2:
        return not_template_findings(view, markers)
    findings = rule_producer(view) + rule_fonts(view)
    findings += rule_page_layout(view)
    findings += rule_heading_style(view)
    findings += rule_running_head(view)
    findings += rule_title_page(view, ctx)
    findings += rule_cross_reference_links(view, ctx)
    findings += rule_old_eq_wording(view)
    anonymity = rule_review_build(view)
    findings += anonymity
    findings += rule_line_numbers(view, anonymous=not anonymity)
    findings += rule_production_pdf(view)
    findings += rule_pdf_version_marker(view)
    return findings

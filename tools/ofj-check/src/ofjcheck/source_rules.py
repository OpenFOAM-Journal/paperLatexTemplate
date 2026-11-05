"""Fingerprint rules for LaTeX sources (docs/FINGERPRINTS.md, sections 3–5).

Each rule looks at the submission and returns findings. A finding that
points to a range of template generations including the current one is
reported as supporting evidence ("consistent", importance info); a range
that ends before the current generation is reported as "outdated".
"""
from __future__ import annotations

import re
from typing import TYPE_CHECKING, Iterable, List, Optional, Tuple

from . import generations
from .filematch import PROTECTED, production_data, scan_submission
from .inputs import document_class
from .latex import Hit
from .model import (CONVENTION, COSMETIC, INFO, MEDIUM, REQUIRED, STRONG, WEAK, Evidence,
                    Finding)

if TYPE_CHECKING:
    from .analyze import Context

Range = Tuple[Optional[str], Optional[str]]

# Template changes, quoted in the findings (dates are merge dates on master).
CHANGE = {
    "autoref_removed": "2026-03-31, PR #50: \\autoref and the names Tab./Fig./Eqn. were replaced "
                       "by Eqn.~\\ref, Tab.~\\ref, Fig.~\\ref and Lst.~\\ref",
    "autoref_added": "2022-12-27, PR #17: \\autoref introduced; 2023-02-25, PR #37: its names set "
                     "to Tab./Fig./Eqn.; 2026-03-31, PR #50: replaced by Eqn.~\\ref etc.",
    "old_ref_style": "2022-12-27, PR #17: 'Eq.\\ \\ref' / 'Tab.\\ \\ref' replaced by \\autoref; "
                     "since 2026-03-31 (PR #50) the convention is Eqn.~\\ref, Tab.~\\ref",
    "copyright_holder": "2022-03-02, commit 62dec8d: copyright holder changed from the OpenFOAM "
                        "Journal to 'The Authors' under CC BY-SA 4.0",
    "copyright_year": "copyright year 2022 → 2024 on 2025-01-11 (PR #42) and → 2026 on "
                      "2026-01-02 (commit 66b2f6a)",
    "xspace": "2023-02-26, PR #39: \\OF ends in \\xspace instead of a hard space",
    "hyperref": "2023-02-09, PR #36: hyperref moved from ofj.cls into the main preamble",
    "review": "2022-12-27, PR #12: review mode (\\ifdefined\\review, 'make review')",
    "linenumbers": "2022-12-27, PR #12: double spacing only in review mode; 2023-01-30, PR #25: "
                   "line numbers only in review mode",
    "contributions": "2023-01-30, PR #26: author contributions moved to "
                     "parts/author-contributions.tex; 2023-04-30, PR #41: moved back into the main file",
    "footmisc": "2022-11-08, PR #10: numbered footnotes instead of symbols",
    "orcid": "2022-01-14, commit 1d9ee46: \\usepackage{orcidlink} added",
    "cite": "2022-03-02, commit f532bdd: \\usepackage{cite} added",
    "doi": "2021-11-22, commit 7aad18e: \\DOI{00.1000/xxx} replaced by \\DOI{TBD}",
    "changes": "2021-06-14, commit bcf80d5: the track-changes set-up was removed from the template",
    "versions_macro": "2021-04-28, commit 14fbeaa: \\OpenFOAMversion renamed \\OpenFOAMversions",
    "title": "2025-01-11, PR #42: example title changed to '... - Use Title Case'",
    "version_comment": "2023-02-08, PR #32: comment explaining \\OpenFOAMversions added",
}

ADVICE_REFS = ("Please refer to equations, tables, figures and listings as Eqn.~\\ref{...}, "
               "Tab.~\\ref{...}, Fig.~\\ref{...} and Lst.~\\ref{...}, as in the current template.")
ADVICE_UPDATE = "Please prepare the manuscript with the current version of the OFJ LaTeX template."

# Template files that hold example content for the authors to replace.
EXAMPLE_FILES = ("examples.tex", "ofj-template.tex", "Bibliography.bib")

# Copyright line (\copyrightinfo) of the template's main file: year -> generations.
COPYRIGHT_YEARS = {"2022": ("G03", "G08"), "2024": ("G09", "G09"), "2026": ("G10", None)}


def evidence(hits: Iterable[Hit], limit: int = 6) -> List[Evidence]:
    """One evidence entry per source line, at most ``limit``."""
    unique = list({h.location: h for h in hits}.values())
    out = [Evidence(h.location, h.line_text[:160]) for h in unique[:limit]]
    if len(unique) > limit:
        out.append(Evidence(f"... and {len(unique) - limit} more line(s)", ""))
    return out


def signal(rule_id: str, title: str, rng: Range, message: str, ev: List[Evidence],
           change: str = "", importance: str = CONVENTION, reliability: str = STRONG,
           advice: Optional[str] = None) -> Finding:
    """A version signal: consistent with the current template, or pointing to an older one.
    advice=None gives the generic advice to use the current template; '' gives none."""
    current = generations.includes_current(*rng)
    return Finding(rule_id=rule_id, title=title, kind="consistent" if current else "outdated",
                   importance=INFO if current else importance, reliability=reliability,
                   message=message, evidence=ev, implies_from=rng[0], implies_to=rng[1],
                   template_change=change,
                   advice="" if current else (ADVICE_UPDATE if advice is None else advice))


# ---------------------------------------------------------------- template use

def rule_document_class(ctx: "Context") -> List[Finding]:
    doc = ctx.document
    cls = document_class(doc.main.path) or "?"
    hits = doc.search(r"\\documentclass\s*(\[[^\]]*\])?\s*\{[^}]*\}", scope="preamble")
    ev = evidence(hits[:1])
    if cls != "ofj":
        return [Finding("SRC01", f"Not the OFJ document class (\\documentclass{{{cls}}})",
                        kind="not-template", importance=REQUIRED, reliability=STRONG,
                        message=f"The main file {doc.main.rel} uses the class '{cls}'. Papers made "
                                "with the OFJ template use \\documentclass[e-only,10pt,reqno]{ofj}.",
                        evidence=ev, advice="Please prepare the manuscript with the OFJ LaTeX template.")]
    m = re.search(r"\[([^\]]*)\]", hits[0].text) if hits else None
    options = sorted(o.strip() for o in m.group(1).split(",")) if m else []
    if options != ["10pt", "e-only", "reqno"]:
        return [Finding("SRC01", "OFJ class used with different options", kind="modified",
                        importance=CONVENTION, reliability=STRONG,
                        message="The template loads the class as \\documentclass[e-only,10pt,reqno]{ofj}; "
                                f"this submission uses [{', '.join(options)}], which changes the layout.",
                        evidence=ev, advice="Please keep the class options of the template.")]
    return []


def rule_core_macros(ctx: "Context") -> List[Finding]:
    doc = ctx.document
    missing = [m for m in ("OpenFOAMversions", "Repository", "DOI")
               if not doc.search(r"\\" + m + r"\s*\{")]
    if not missing:
        return []
    return [Finding("SRC25", "Template metadata fields removed", kind="modified", importance=CONVENTION,
                    reliability=MEDIUM,
                    message="The template sets " + ", ".join(f"\\{m}" for m in missing) +
                            " in the preamble (printed in the title block), but the submission does not.",
                    advice="Please keep the \\OpenFOAMversions, \\Repository and \\DOI entries of the template.")]


# ---------------------------------------------------------------- exact file matches

def rule_file_matches(ctx: "Context") -> List[Finding]:
    sub = ctx.submission
    matches, mismatches = scan_submission(ctx.index, sub.root)
    included = {f.rel for f in ctx.document.files}
    findings = []
    for m in matches:
        name = m.template_path
        v = m.versions[0]
        if not m.on_master:
            findings.append(Finding(
                "CLS10", f"{m.submitted} matches a development-branch version", kind="modified",
                importance=CONVENTION, reliability=MEDIUM,
                message=f"{m.submitted} is identical to a version of {name} that only existed on a "
                        "development branch of the template, never in a released template.",
                evidence=[Evidence(m.submitted, f"blob {v.blob[:7]}")]))
            continue
        rng = (m.range_from, m.range_to)
        periods = "; ".join(x.period() for x in m.versions if x.on_master)
        if m.production:
            periods += "; identical apart from the publication data filled in by the editor"
        if name.startswith("parts/") or name in EXAMPLE_FILES:
            used = m.submitted in included
            if not used:
                continue                       # unused example file left in the folder: harmless
            f = signal("CLS11", f"Unedited template example file {m.submitted}", rng,
                       f"{m.submitted} is the template's example file {name}, unchanged ({periods}), "
                       "and it is part of the document.",
                       [Evidence(m.submitted, f"identical to template {name}")],
                       reliability=STRONG, importance=CONVENTION)
            f.kind = "placeholder" if f.kind == "consistent" else f.kind
            f.importance = CONVENTION
            f.advice = "Please replace the template's example content with your own."
            findings.append(f)
            continue
        important = REQUIRED if name in ("ofj.cls", "ofjart.cls") else CONVENTION
        if name not in PROTECTED + ("Makefile",):
            important = INFO if generations.includes_current(*rng) else COSMETIC
        findings.append(signal(
            "CLS00", f"{m.submitted}: template version {generations.describe(*rng)}", rng,
            f"{m.submitted} is identical to a version of the template's {name} ({periods}).",
            [Evidence(m.submitted, f"identical to template {name} (blob {v.blob[:7]})")],
            change=f"{name}: " + periods, importance=important, reliability=STRONG))
    for mm in mismatches:
        nearest = mm.nearest
        findings.append(Finding(
            "CLS01", f"{mm.submitted} was modified", kind="modified",
            importance=REQUIRED if mm.template_path in ("ofj.cls", "ofjart.cls") else CONVENTION,
            reliability=STRONG,
            message=f"{mm.submitted} differs from every version of the template's {mm.template_path}. "
                    f"Closest is the version {nearest.period()} ({mm.similarity:.0%} identical; "
                    f"{mm.added} line(s) added, {mm.removed} removed). The template asks authors "
                    "not to change its class and style files.",
            evidence=[Evidence(mm.submitted, d) for d in mm.excerpt],
            implies_from=None, implies_to=None,
            advice=f"Please use the unmodified {mm.template_path} of the current template."))
    return findings


def describe_production(data: dict) -> str:
    parts = []
    if "volume" in data:
        parts.append(f"Volume {data['volume']}")
    if "pages" in data:
        parts.append(f"pages {data['pages']}")
    parts += [f"{k} {data[k]}" for k in ("received", "accepted", "published") if k in data]
    return ", ".join(parts)


def rule_production_sources(ctx: "Context") -> List[Finding]:
    """ofjart.cls with the journal's publication data: a production version, not a submission."""
    root = ctx.submission.root
    for cls in sorted(root.rglob("ofjart.cls")) if root else []:
        data = production_data(cls.read_text(encoding="utf-8", errors="replace"))
        if data:
            return [Finding("PRD01", "Production version: publication data filled in", kind="production",
                            importance=INFO, reliability=STRONG,
                            message="ofjart.cls contains the journal's publication data, which the "
                                    f"editor fills in for publication ({describe_production(data)}). "
                                    "This is a production or published version, not an author "
                                    "submission; author information and the copyright year are "
                                    "expected to be filled in.",
                            evidence=[Evidence(cls.relative_to(root).as_posix(), describe_production(data))])]
    return []


# ---------------------------------------------------------------- cross-references

def rule_autoref_names(ctx: "Context") -> List[Finding]:
    doc = ctx.document
    hits = doc.search(
        r"\\(?:def|renewcommand\*?\s*\{?|newcommand\*?\s*\{?)\\(?:table|figure|equation)autorefname",
        scope="preamble")
    if not hits:
        modern = [h for h in doc.search(r"\\usepackage\s*\[[^\]]*\]\s*\{hyperref\}", scope="preamble")
                  if "linkcolor=black" in h.line_text]
        if not modern:
            return []
        return [Finding("SRC02", "No \\autoref names in the preamble", kind="consistent", importance=INFO,
                        reliability=MEDIUM,
                        message="The preamble has the template's hyperref line (2023+) but not the "
                                "\\autoref names that templates from 2023-02-25 to 2026-03-31 defined "
                                "right after it, as in the current template.",
                        evidence=evidence(modern[:1]), template_change=CHANGE["autoref_removed"],
                        excludes_from="G08", excludes_to="G10")]   # G07 got the names only on 02-25
    return [signal("SRC02", "Preamble defines the \\autoref names Tab./Fig./Eqn.", ("G07", "G10"),
                   "The preamble sets \\tableautorefname, \\figureautorefname or "
                   "\\equationautorefname. The template did this from 2023-02-25 until 2026-03-31; "
                   "the current template no longer uses \\autoref.",
                   evidence(hits), change=CHANGE["autoref_removed"], advice=ADVICE_REFS)]


def rule_autoref_usage(ctx: "Context") -> List[Finding]:
    hits = ctx.document.search(r"\\[aA]utoref\s*\{", scope="body")
    if not hits:
        return []
    return [signal("SRC03", f"Cross-references made with \\autoref ({len(hits)}x)", ("G05", "G10"),
                   "The text refers to equations, tables or figures with \\autoref, as the template "
                   "did from 2022-12-27 until 2026-03-31. The current template writes "
                   "Eqn.~\\ref{...}, Tab.~\\ref{...}, Fig.~\\ref{...} and Lst.~\\ref{...}.",
                   evidence(hits), change=CHANGE["autoref_added"], advice=ADVICE_REFS)]


def rule_current_refs(ctx: "Context") -> List[Finding]:
    hits = ctx.document.search(r"\b(?:Eqn|Tab|Fig|Lst)\.~\\ref\s*\{", scope="body")
    findings = []
    if hits:
        findings.append(signal("SRC04", f"Current reference convention used ({len(hits)}x)",
                               ("G11", None), "Eqn.~\\ref, Tab.~\\ref, Fig.~\\ref or Lst.~\\ref, "
                               "as in the current template.", evidence(hits, 3),
                               change=CHANGE["autoref_removed"], reliability=WEAK))
    cref = ctx.document.search(r"\\[cC]ref\s*\{", scope="body")
    if cref and "cleveref" not in ctx.head_main_tex:
        findings.append(Finding(
            "SRC26", f"Cross-references made with cleveref ({len(cref)}x)", kind="modified",
            importance=CONVENTION, reliability=STRONG,
            message="The text uses \\cref/\\Cref. The current template does not use cleveref "
                    "(it was proposed in PR #52, which is not merged); it writes Eqn.~\\ref{...} etc.",
            evidence=evidence(cref), advice=ADVICE_REFS))
    return findings


def rule_old_ref_style(ctx: "Context") -> List[Finding]:
    findings = []
    old = ctx.document.search(r"\b(?:Eq|Tab)\.\\ \s*\\ref\s*\{", scope="body")
    if old:
        findings.append(signal("SRC05", f"Old reference style 'Eq.\\ \\ref' ({len(old)}x)", ("G01", "G05"),
                               "References are written exactly as in templates before 2022-12-27 "
                               "('Eq.\\ \\ref{...}', 'Tab.\\ \\ref{...}'). The current template writes "
                               "Eqn.~\\ref{...} and Tab.~\\ref{...}.",
                               evidence(old), change=CHANGE["old_ref_style"], reliability=MEDIUM,
                               advice=ADVICE_REFS))
    # Only the abbreviation 'Eq.' is flagged: a word written out ('Figure 3 shows ...') is fine
    # at the start of a sentence.
    other = [h for h in ctx.document.search(r"\bEqs?\.[~ ]?\s*\(?\\(?:eq)?ref\s*\{", scope="body")
             if h not in old]
    if other:
        findings.append(Finding("SRC28", f"Equations referred to as 'Eq.' ({len(other)}x)",
                                kind="style", importance=CONVENTION, reliability=STRONG,
                                message="The current template abbreviates equations as 'Eqn.' "
                                        "(Eqn.~\\ref{...}); these references write 'Eq.'. This is a "
                                        "convention, not a sign of a particular template version.",
                                evidence=evidence(other), advice=ADVICE_REFS))
    return findings


# ---------------------------------------------------------------- preamble

def head_copyright_year(ctx: "Context") -> Optional[str]:
    m = re.search(r"\\copyrightinfo\{(\d{4})\}", ctx.head_main_tex)
    return m.group(1) if m else None


def rule_copyright(ctx: "Context") -> List[Finding]:
    hits = ctx.document.search(r"\\copyrightinfo\s*\{([^}]*)\}\s*\{", scope="preamble")
    if not hits:
        return [Finding("SRC07", "No \\copyrightinfo in the preamble", kind="modified",
                        importance=COSMETIC, reliability=MEDIUM,
                        message="The template sets the copyright line with \\copyrightinfo; the "
                                "submission does not, so the class default is printed.",
                        advice="Please keep the \\copyrightinfo line of the template.")]
    hit = hits[-1]
    year = re.search(r"\{([^}]*)\}", hit.text).group(1).strip()
    line = hit.line_text
    ev = [Evidence(hit.location, line[:160])]
    if "OpenFOAM" in line and "Authors" not in line:
        return [signal("SRC06", "Copyright holder 'OpenFOAM Journal' (pre-2022 template)",
                       ("G01", "G02"), "The copyright line names the OpenFOAM Journal as holder. "
                       "Since 2022-03-02 the template says '© The Authors', CC BY-SA 4.0.", ev,
                       change=CHANGE["copyright_holder"], importance=CONVENTION, reliability=STRONG)]
    current_year = head_copyright_year(ctx)
    if year == current_year:
        return [signal("SRC07", f"Copyright year {year}", COPYRIGHT_YEARS.get(year, ("G10", None)),
                       f"Copyright year {year}, as in the current template.", ev, reliability=WEAK)]
    rng = COPYRIGHT_YEARS.get(year)
    msg = (f"The copyright line says {year}; the current template says {current_year}. The year is "
           "updated by the editor, so this is only a hint")
    if rng:
        msg += f": {year} was the template's year in {generations.describe(*rng)}."
        return [signal("SRC07", f"Copyright year {year} (current template: {current_year})", rng, msg,
                       ev, change=CHANGE["copyright_year"], importance=COSMETIC, reliability=MEDIUM,
                       advice="")]           # D3: the editor sets the year; nothing for the authors
    return [Finding("SRC07", f"Copyright year {year} (current template: {current_year})", kind="modified",
                    importance=COSMETIC, reliability=WEAK,
                    message=msg + f"; the template never used {year}, so it was probably edited.",
                    evidence=ev, template_change=CHANGE["copyright_year"])]


def rule_of_macro(ctx: "Context") -> List[Finding]:
    hits = ctx.document.search(r"\\(?:newcommand|renewcommand|def)\s*\{?\\OF\}?.*", scope="preamble")
    if not hits:
        return []
    line = hits[0].text
    if "xspace" in line:
        return [signal("SRC08", "\\OF defined with \\xspace", ("G07", None),
                       "\\OF ends in \\xspace, as in the template since 2023-02-26.",
                       evidence(hits[:1]), change=CHANGE["xspace"], reliability=STRONG)]
    if re.search(r"textregistered\}\s+\}", line):
        return [signal("SRC08", "\\OF defined with a hard space (pre-2023 template)", ("G01", "G07"),
                       "\\OF ends in a hard space instead of \\xspace, as in templates before "
                       "2023-02-26 (this adds a space before punctuation: 'OpenFOAM® ,').",
                       evidence(hits[:1]), change=CHANGE["xspace"], importance=COSMETIC)]
    return []


def rule_hyperref(ctx: "Context") -> List[Finding]:
    doc = ctx.document
    hits = doc.search(r"\\usepackage\s*(\[[^\]]*\])?\s*\{hyperref\}", scope="preamble")
    if any("linkcolor=black" in h.line_text for h in hits):
        return [signal("SRC09", "hyperref loaded in the main preamble", ("G07", None),
                       "hyperref is loaded at the end of the preamble with black links, as in the "
                       "template since 2023-02-09.", evidence(hits[:1]), change=CHANGE["hyperref"],
                       reliability=MEDIUM)]
    if hits:
        return []
    return [signal("SRC09", "hyperref not loaded in the main preamble", ("G01", "G07"),
                   "The template loads hyperref in the main preamble since 2023-02-09 (before, the "
                   "class ofj.cls loaded it).", [], change=CHANGE["hyperref"], reliability=MEDIUM)]


def _conditional_on_review(text: str, offset: int) -> bool:
    before = text[:offset]
    last_if = before.rfind("\\ifdefined\\review")
    last_fi = max(before.rfind("\\fi\n"), before.rfind("\\fi "), before.rfind("\\fi%"))
    last_else = before.rfind("\\else")
    return last_if > last_fi and not (last_else > last_if)


def rule_review_mode(ctx: "Context") -> List[Finding]:
    doc = ctx.document
    findings = []
    review = doc.search(r"\\ifdefined\s*\\review")
    if review:
        findings.append(signal("SRC10", "Review mode (\\ifdefined\\review) present", ("G05", None),
                               "The document has the template's review mode, introduced 2022-12-27.",
                               evidence(review[:1]), change=CHANGE["review"], reliability=STRONG))
    else:
        findings.append(signal("SRC10", "No review mode (pre-2022-12-27 template)", ("G01", "G05"),
                               "The template's review mode (\\ifdefined\\review ... \\fi, built with "
                               "'make review') is missing. It was added on 2022-12-27 and hides the "
                               "author information for the double-blind review.", [],
                               change=CHANGE["review"], reliability=MEDIUM))
    uncond = []
    for f in doc.files:
        for m in re.finditer(r"\\(linenumbers|doublespacing)\b", f.masked):
            if not _conditional_on_review(f.masked, m.start()):
                line = f.masked.count("\n", 0, m.start()) + 1
                uncond.append(Hit(f, line, m.group(0), f.raw_lines[line - 1].strip()))
    if uncond:
        findings.append(signal("SRC11", "Line numbers / double spacing always on", ("G01", "G06"),
                               "\\linenumbers or \\doublespacing is used outside the review-mode "
                               "condition, as in templates before 2023-01-30 (line numbers) and "
                               "2022-12-27 (double spacing).", evidence(uncond),
                               change=CHANGE["linenumbers"], importance=COSMETIC, reliability=MEDIUM))
    return findings


def rule_author_contributions(ctx: "Context") -> List[Finding]:
    doc = ctx.document
    calls = doc.search(r"\\authorcontributions\s*\{", scope="body")
    in_parts = [h for h in calls if h.file.rel.endswith("author-contributions.tex")]
    if in_parts:
        return [signal("SRC13", "Author contributions in parts/author-contributions.tex", ("G06", "G07"),
                       "The author contributions are in a separate file author-contributions.tex, as "
                       "in the template from 2023-01-30 to 2023-04-29; the current template has them "
                       "in the main file.", evidence(in_parts[:1]), change=CHANGE["contributions"],
                       importance=COSMETIC, reliability=MEDIUM)]
    # scope=body: the preamble defines \authorcontributions with the words "Author Contributions"
    if calls or doc.search(r"(?i)author\s+contributions?", scope="body"):
        return []
    return [Finding("SRC13", "No author contributions statement", kind="modified", importance=REQUIRED,
                    reliability=MEDIUM,
                    message="The template requires the contributions of all authors to be stated "
                            "(\\authorcontributions{...}, CRediT roles); none was found. In review "
                            "builds it is hidden, but it must be in the sources.",
                    advice="Please add the author contributions with \\authorcontributions{...}.")]


def rule_packages(ctx: "Context") -> List[Finding]:
    doc = ctx.document
    pkg = lambda name: doc.search(r"\\usepackage\s*(\[[^\]]*\])?\s*\{[^}]*\b" + name + r"\b[^}]*\}",  # noqa: E731
                                  scope="preamble")
    findings = []
    foot = pkg("footmisc")
    if any("symbol" in h.line_text for h in foot):
        findings.append(signal("SRC14", "Footnote symbols (footmisc[symbol])", ("G02", "G05"),
                               "footmisc is loaded with the option 'symbol', as in templates from "
                               "2021-09-06 to 2022-11-07; since then footnotes are numbered.",
                               evidence(foot[:1]), change=CHANGE["footmisc"], importance=COSMETIC))
    elif any("hang" in h.line_text and "flushmargin" in h.line_text for h in foot):
        findings.append(signal("SRC14", "footmisc[hang,flushmargin]", ("G06", None),
                               "As in the template since 2023-01-30.", evidence(foot[:1]),
                               reliability=MEDIUM))
    for name, since, rng_old, key in (("orcidlink", "2022-01-14", ("G01", "G02"), "orcid"),
                                      ("cite", "2022-03-02", ("G01", "G03"), "cite")):
        if pkg(name):
            continue
        findings.append(signal("SRC15", f"Package '{name}' not loaded", rng_old,
                               f"The template loads \\usepackage{{{name}}} since {since}; this "
                               "preamble does not.", [], change=CHANGE[key], importance=COSMETIC,
                               reliability=WEAK))
    t1 = doc.search(r"\\usepackage\s*\[T1\]\s*\{fontenc\}", scope="preamble")
    if t1:
        findings.append(Finding("SRC27", "T1 font encoding added", kind="modified", importance=COSMETIC,
                                reliability=MEDIUM,
                                message="\\usepackage[T1]{fontenc} is not part of the current template "
                                        "(proposed in PR #47, not merged); it changes the fonts.",
                                evidence=evidence(t1[:1])))
    return findings


def rule_misc_preamble(ctx: "Context") -> List[Finding]:
    doc = ctx.document
    findings = []
    old_doi = doc.search(r"\\DOI\s*\{00\.1000/xxx\}")
    if old_doi:
        findings.append(signal("SRC19", "\\DOI{00.1000/xxx} placeholder (pre-2021-11 template)",
                               ("G01", "G02"), "Templates before 2021-11-22 had \\DOI{00.1000/xxx}; "
                               "since then \\DOI{TBD}.", evidence(old_doi), change=CHANGE["doi"],
                               importance=COSMETIC))
    changes = doc.search(r"\\definechangesauthor\s*\[color=NavyBlue\]\s*\{HN\}|\\newcommand\{\\note\}\[2\]\[\]")
    if changes:
        findings.append(signal("SRC20", "Track-changes set-up of the 2021 template", ("G01", "G01"),
                               "The preamble contains the track-changes definitions that the first "
                               "template had until 2021-06-14.", evidence(changes),
                               change=CHANGE["changes"]))
    singular = doc.search(r"\\OpenFOAMversion\s*\{", scope="preamble")
    if singular:
        findings.append(signal("SRC21", "\\OpenFOAMversion (singular)", ("G01", "G01"),
                               "\\OpenFOAMversion was renamed \\OpenFOAMversions on 2021-04-28.",
                               evidence(singular), change=CHANGE["versions_macro"]))
    nwith = doc.search(r"\\numberwithin\s*\{equation\}\s*\{section\}", scope="preamble")
    if nwith:
        findings.append(Finding("SRC22", "\\numberwithin{equation}{section} enabled", kind="modified",
                                importance=CONVENTION, reliability=STRONG,
                                message="The template has this line commented out with the note "
                                        "'Please don't enable this for submission!'.",
                                evidence=evidence(nwith),
                                advice="Please number equations consecutively, as in the template."))
    comment = doc.search(r"This is the version\(s\) that was used to generate", raw=True)
    if comment:
        findings.append(signal("SRC17", "Template comment on \\OpenFOAMversions (2023+)", ("G07", None),
                               "The explanatory comment added to the template on 2023-02-08 is present.",
                               evidence(comment[:1]), change=CHANGE["version_comment"], reliability=WEAK))
    return findings


def rule_title(ctx: "Context") -> List[Finding]:
    doc = ctx.document
    new = doc.search(r"Journal Publication\s*-\s*Use Title Case")
    old = doc.search(r"\\title\s*\[[^\]]*\]\s*\{\\OF Journal publication\}")
    if new:
        return [signal("SRC18", "Example title of the 2025+ template", ("G09", None),
                       "The title is still the template's example 'OpenFOAM Journal Publication - "
                       "Use Title Case', introduced on 2025-01-11.", evidence(new[:1]),
                       change=CHANGE["title"], reliability=STRONG)]
    if old:
        return [signal("SRC18", "Example title of the pre-2025 template", ("G01", "G08"),
                       "The title is still the example 'OpenFOAM Journal publication' of templates "
                       "before 2025-01-11.", evidence(old[:1]), change=CHANGE["title"])]
    return []


def rule_bibliography(ctx: "Context") -> List[Finding]:
    doc = ctx.document
    style = doc.search(r"\\bibliographystyle\s*\{([^}]*)\}")
    if style:
        name = re.search(r"\{([^}]*)\}", style[-1].text).group(1).strip()
        if name == "IEEEtran":
            return []
        return [Finding("SRC23", f"Bibliography style '{name}' instead of IEEEtran", kind="modified",
                        importance=CONVENTION, reliability=STRONG,
                        message="The template uses \\bibliographystyle{IEEEtran} ('do not change').",
                        evidence=evidence(style[-1:]),
                        advice="Please use \\bibliographystyle{IEEEtran} as in the template.")]
    biblatex = doc.search(r"\\usepackage\s*(\[[^\]]*\])?\s*\{biblatex\}", scope="preamble")
    manual = doc.search(r"\\begin\{thebibliography\}")
    if biblatex or manual:
        how = "biblatex" if biblatex else "a hand-written thebibliography"
        return [Finding("SRC23", f"Bibliography made with {how}", kind="modified", importance=CONVENTION,
                        reliability=MEDIUM,
                        message="The template uses BibTeX with \\bibliographystyle{IEEEtran}.",
                        evidence=evidence((biblatex or manual)[:1]),
                        advice="Please use BibTeX with \\bibliographystyle{IEEEtran} as in the template.")]
    return []


# ---------------------------------------------------------------- placeholders

PLACEHOLDERS = [
    (r"v20xx", "OpenFOAM version placeholder 'v20xx'"),
    (r"github\.com/xxx", "repository placeholder 'https://github.com/xxx'"),
    (r"Maria Jersey|John Smith|Philip Murphy|M\. Jersey|J\. Smith|P\. Murphy", "example author names"),
    (r"Emailaddress\d|\bAddress\d\b", "example address / e-mail"),
    (r"0000-1234-5678-0000", "example ORCID"),
    (r"This is the place for (?:an abstract|introduction)", "example abstract / introduction text"),
    (r"We shall consider the specific transport property", "example introduction text"),
    (r"Theoretical backgroud", "example section title"),
    (r"Use Title Case|\\OF Journal [Pp]ublication\}", "example title"),
    (r"This is an example acknowledgements section", "example acknowledgements"),
    (r"This is a conclusion\.", "example conclusion"),
    (r"Conceptualisation, J\.S\.;", "example CRediT author contributions"),
    (r"code listing caption|Examplary figure|Here is an example figure", "example caption / text"),
]


def rule_placeholders(ctx: "Context") -> List[Finding]:
    doc = ctx.document
    ev, kinds = [], []
    for pattern, label in PLACEHOLDERS:
        hits = doc.search(pattern)
        if hits:
            kinds.append(label)
            ev.append(Evidence(hits[0].location, f"{label}: {hits[0].line_text[:120]}"))
    root = ctx.submission.root
    for mk in sorted(root.rglob("Makefile")) if root else []:
        text = mk.read_text(encoding="utf-8", errors="replace")
        for i, line in enumerate(text.splitlines(), 1):
            if re.match(r"\s*TYPE\s*=\s*SetTypeInMakefile", line):
                kinds.append("article type not set in the Makefile")
                ev.append(Evidence(f"{mk.relative_to(root).as_posix()}:{i}", line.strip()))
    if not kinds:
        return []
    return [Finding("PLC01", f"Template placeholders left in the sources ({len(kinds)})",
                    kind="placeholder", importance=CONVENTION, reliability=STRONG,
                    message="Example content of the template is still present (in the typeset text, "
                            "not in comments): " + "; ".join(kinds) + ". Items inside the review-mode "
                            "branch are hidden in review builds but appear in the final version.",
                    evidence=ev, advice="Please replace all example content of the template.")]


# ---------------------------------------------------------------- dynamic and future rules

def rule_ai_declaration(ctx: "Context") -> List[Finding]:
    """Active as soon as the current template has the AI declaration (PR #53)."""
    if "aiDeclaration" not in ctx.head_main_tex:
        return []
    doc = ctx.document
    if doc.search(r"(?i)Declaration on the Use of Artificial Intelligence") or \
            any(f.rel.endswith("aiDeclaration.tex") for f in doc.files):
        return []
    return [Finding("SRC30", "Mandatory AI declaration missing", kind="outdated", importance=REQUIRED,
                    reliability=STRONG,
                    message="The current template requires a section 'Declaration on the Use of "
                            "Artificial Intelligence' (parts/aiDeclaration.tex), also when no AI tools "
                            "were used. The submission has none.",
                    template_change="PR #53: mandatory AI declaration",
                    advice="Please add the Declaration on the Use of Artificial Intelligence from the "
                           "current template.")]


VERSION_MARKERS = [
    r"\\(?:newcommand|renewcommand|def|providecommand)\s*\{?\\ofjtemplateversion\}?\s*\{([^}]*)\}",
    r"\\ofjtemplateversion\s*\{([^}]*)\}",
    r"%\s*OFJ[- ]template[- ]version\s*[:=]\s*(\S+)",
]


def _generation_of_marker(value: str) -> Optional[str]:
    value = value.strip()
    m = re.fullmatch(r"(?i)g(\d{1,2})", value)
    if m and f"G{int(m.group(1)):02d}" in {g.id for g in generations.GENERATIONS}:
        return f"G{int(m.group(1)):02d}"
    m = re.search(r"(\d{4})[-/.](\d{2})[-/.](\d{2})", value)
    if m:
        first, last = generations.for_period("-".join(m.groups()), None)
        return first
    return None


def _find_version_marker(ctx: "Context") -> Optional[Tuple[str, Evidence]]:
    """The declared template version: in the document, or in a shipped ofj.cls
    (the natural place for an explicit template version, see docs/FINGERPRINTS.md §11)."""
    for pattern in VERSION_MARKERS:
        hits = ctx.document.search(pattern, raw=True)
        if hits:
            return re.search(pattern, hits[0].text).group(1), evidence(hits[:1])[0]
    root = ctx.submission.root
    for cls in sorted(root.rglob("ofj.cls")) if root else []:
        text = cls.read_text(encoding="utf-8", errors="replace")
        m = re.search(VERSION_MARKERS[0], text)
        if m:
            line = text.count("\n", 0, m.start()) + 1
            return m.group(1), Evidence(f"{cls.relative_to(root).as_posix()}:{line}", m.group(0)[:160])
    return None


def rule_version_marker(ctx: "Context") -> List[Finding]:
    """Optional explicit template version (requirement R9); absent in all templates so far."""
    found = _find_version_marker(ctx)
    if not found:
        return []
    value, ev = found
    gen = _generation_of_marker(value)
    if gen is None:
        return [Finding("VER01", f"Template version marker '{value}'", kind="info",
                        importance=INFO, reliability=STRONG,
                        message="The submission declares a template version that this "
                                "version of ofj-check does not know.", evidence=[ev])]
    rng = (gen, None if gen == generations.CURRENT else gen)
    return [signal("VER01", f"Template version marker '{value}'", rng,
                   f"The submission declares template version '{value}' ({gen}).", [ev])]


ALWAYS = [rule_document_class]
OFJ_ONLY = [rule_file_matches, rule_production_sources, rule_core_macros, rule_autoref_names, rule_autoref_usage,
            rule_current_refs, rule_old_ref_style, rule_copyright, rule_of_macro, rule_hyperref,
            rule_review_mode, rule_author_contributions, rule_packages, rule_misc_preamble,
            rule_title, rule_bibliography, rule_placeholders, rule_ai_declaration,
            rule_version_marker]


def run_source_rules(ctx: "Context") -> List[Finding]:
    findings = []
    for rule in ALWAYS:
        findings += rule(ctx)
    if any(f.kind == "not-template" for f in findings):
        return findings          # fingerprints of the OFJ template are meaningless here
    for rule in OFJ_ONLY:
        findings += rule(ctx)
    return findings

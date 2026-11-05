#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
checkStyle.py -- style, formatting and convention checker for OpenFOAM Journal
                 manuscripts prepared with the official LaTeX template.

Copyright 2026 OpenFOAM Journal.  Distributed under the same terms as the
template itself.

    Usage:  python3 checkStyle.py                 # check the whole manuscript
            python3 checkStyle.py --list-rules    # print the rule table
            python3 checkStyle.py --strict        # treat warnings as errors
            python3 checkStyle.py --ignore STY003 --ignore PLC
            python3 checkStyle.py --check-log     # also parse the LaTeX .log

    Exit status: 0 if no errors, 1 if at least one error (or, with --strict,
    at least one warning), 2 on a usage/IO problem.

    No third-party dependencies; Python 3.8 or newer.

===============================================================================
WHY THIS SCRIPT EXISTS
===============================================================================

The template encodes a number of conventions that are easy to get wrong and
tedious to check by hand.  This script checks the ones that can be checked
*deterministically*, so that authors and editors get the same answer every
time, with no LLM and no network access.

Two severities are used, and the distinction matters:

  ERROR  The rule is unambiguous and the false-positive rate is essentially
         zero (a leftover placeholder, a missing mandatory section, a wrong
         cross-reference word).  These should be fixed before submission.

  WARN   The rule encodes a preference or a heuristic that can legitimately
         be wrong in a particular manuscript (spelling variants, title case,
         float placement).  Read them, then use your judgement.

Anything that genuinely requires judgement -- whether the AI declaration is
substantively adequate, whether a caption describes its figure, whether the
prose is clear -- is deliberately NOT checked here.  A checker that cries
wolf gets ignored.

===============================================================================
THE RULES, AND WHERE THEY COME FROM
===============================================================================

Each rule below cites the place in the template that it is derived from, so
that the rule can be re-read, re-interpreted, or removed if we got it wrong.
Rule IDs are stable: please do not renumber them, retire them instead.

--- REF: cross-reference conventions -----------------------------------------
    Source: parts/conclusion.tex -- "equations, tables and figures are
    referred to in the text as Eqn.~\\ref{}, Tab.~\\ref{} and Fig.~\\ref{}";
    parts/introduction.tex additionally uses Lst.~\\ref{} for code listings.
    Commit 437f881 ("replace \\autoref by \\ref") settled the macro to use.

    REF001 ERROR  Wrong word before a cross-reference.  "Figure~\\ref{}",
                  "Table~\\ref{}", "Equation~\\ref{}", "Eq.~\\ref{}",
                  "Listing~\\ref{}" etc. must be Fig./Tab./Eqn./Lst.
    REF002 ERROR  Cross-reference word not followed by a non-breaking space,
                  e.g. "Fig. \\ref{}" or "Fig.\\ref{}" instead of "Fig.~\\ref{}".
                  A normal space allows a line break between the word and the
                  number.
    REF003 ERROR  Cross-reference word disagrees with the label prefix, e.g.
                  "Fig.~\\ref{tab:something}".  Usually a copy-paste slip.
    REF004 ERROR  \\autoref, \\cref or \\Cref used.  The template standardised
                  on plain \\ref preceded by the spelled-out word.
    REF005 ERROR  \\label placed before \\caption inside a float.  LaTeX then
                  records the number of the *preceding* float and every
                  reference to it is silently wrong.
    REF006 WARN   Float (figure/table) with no \\caption or no \\label.
    REF007 WARN   \\eqref used.  Consistent with LaTeX, but the template style
                  is "Eqn.~\\ref{}" so the parentheses would be inconsistent.
    REF008 WARN   Section cross-references are written inconsistently (some as
                  "Sec.~\\ref{}", some as "Section~\\ref{}").  The template
                  does not state which to use, so this only asks for internal
                  consistency; it is NOT an error either way.

--- PLC: leftover template placeholders --------------------------------------
    Source: the shipped content of ofj-template.tex, parts/*.tex and Makefile.
    These are all strings that exist only because nobody replaced them.
    Note that \\DOI{TBD} is deliberately NOT flagged -- ofj-template.tex says
    "leave for submission".

    PLC001 ERROR  \\OpenFOAMversions still contains the placeholder "v20xx".
    PLC002 ERROR  \\Repository still points at "https://github.com/xxx".
    PLC003 ERROR  \\Repository{} is empty in the non-review branch.  The
                  repository is required for the final version.
    PLC004 ERROR  Example author identity left in place: "Maria Jersey",
                  "John Smith", "Philip Murphy", "Address1", "Emailaddress1",
                  or the example ORCID 0000-1234-5678-0000.
    PLC005 ERROR  Title is still the placeholder "... Use Title Case".
    PLC006 ERROR  Placeholder body text from the shipped parts/ files, e.g.
                  "This is the place for an abstract", "This is a conclusion",
                  "Theoretical backgroud", "Examplary figure".
    PLC007 ERROR  The example figure figures/example.png is still included.
    PLC008 ERROR  Makefile still has TYPE = SetTypeInMakefile.  The article
                  type must be chosen (FullPaper, TNote or RevPaper).
    PLC009 WARN   TODO / FIXME / XXX left anywhere in the sources, including
                  in comments.

--- STR: required structure and settings -------------------------------------
    Source: README.md ("Declaration on the Use of Artificial Intelligence",
    "Review Version"), ofj-template.tex and parts/aiDeclaration.tex.

    STR001 ERROR  parts/aiDeclaration.tex is not \\input by the manuscript.
                  README: the section is mandatory for all submissions.
    STR002 ERROR  The AI declaration is inside an \\ifdefined\\review guard.
                  README: it is "deliberately retained in the review version,
                  as reviewers need it to assess the manuscript".
    STR003 ERROR  The author-guidance comment block is still present in
                  parts/aiDeclaration.tex.  The file says to delete it before
                  submission.
    STR004 ERROR  The AI declaration has neither Option A nor Option B active,
                  or has both active.  Exactly one declaration must remain.
    STR005 ERROR  Option B is active but still contains unfilled brackets such
                  as [TOOL, MODEL/VERSION], [PURPOSE, [SECTIONS] or [METHOD.
    STR006 WARN   The "Option A" / "Option B" marker comments are still there.
                  Harmless, but they are meant to be deleted.
    STR007 ERROR  No \\begin{abstract}.  The abstract is required
                  (parts/abstract.tex: "Abstract is required").
    STR008 ERROR  \\bibliographystyle is not IEEEtran.  ofj-template.tex marks
                  this line "do not change".
    STR009 ERROR  \\numberwithin{equation}{section} is enabled.
                  ofj-template.tex: "Please don't enable this for submission!"
    STR010 ERROR  An \\input or \\include names a file that does not exist.
    STR011 WARN   \\documentclass is not the ofj class, or its options were
                  changed from [e-only,10pt,reqno].
    STR012 WARN   \\authorcontributions is missing, or is missing the closing
                  sentence "All authors have read and agreed to the published
                  version of the manuscript."  The journal requires the
                  contributions of all authors to be explicitly stated.
    STR013 WARN   \\authorcontributions still contains the example initials
                  J.S., P.M., F.A. or S.A.  (A warning, not an error: a real
                  author may genuinely have those initials.)

--- REV: double-blind review integrity ---------------------------------------
    Source: README.md "Review Version" and the \\ifdefined\\review guards in
    ofj-template.tex.  Identity must not leak into the review build.

    REV001 ERROR  \\input{parts/acknowledgements} or \\authorcontributions is
                  not inside the \\else branch of an \\ifdefined\\review guard,
                  so it would appear in the review version.
    REV002 WARN   parts/aiDeclaration.tex mentions a name, institution, grant
                  number or repository URL.  It is kept in the review version,
                  so it must stay anonymous.  Heuristic; check by eye.

--- STY: typography and house style ------------------------------------------
    Source: usage throughout the template.  All warnings by design.

    STY001 WARN   Literal "OpenFOAM" in the text.  ofj-template.tex defines
                  \\OF for this, which adds the registered-trademark symbol.
    STY002 WARN   Straight double quote (").  Use ``...'' in LaTeX.
    STY003 WARN   US spelling where the template uses British/-ise forms
                  (the template writes visualisation, discretisation,
                  Conceptualisation).
    STY004 WARN   "e.g." / "i.e." / "cf." / "viz." followed by a plain space.
                  LaTeX then typesets an end-of-sentence space; write
                  "e.g.," or "e.g.\\ " (the template uses both correctly).
    STY005 WARN   \\cite preceded by a plain space instead of "~".
    STY006 WARN   Float placement specifier [h], [h!] or [H].
                  ofj-template.tex: "default placement is top; if the figure
                  occupies more than 75% of a page, the [p] option should be
                  specified."
    STY007 WARN   \\title{} does not look like Title Case.  Heuristic only --
                  acronyms, hyphenation and macros are hard to judge.

--- BIB: bibliography --------------------------------------------------------
    Source: Bibliography.bib and \\bibliographystyle{IEEEtran}.

    BIB001 WARN   Entry missing author, title or year.
    BIB002 WARN   Page range written with a single hyphen ("620-631").
                  BibTeX expects an en-dash: "620--631".
    BIB003 WARN   Entry defined in the .bib file but never cited.

--- LOG: LaTeX log file (only with --check-log) ------------------------------
    Source: the build itself.  These are the errors that only show up after
    compilation, and are cheap to surface.

    LOG001 ERROR  Undefined reference.
    LOG002 ERROR  Label multiply defined.
    LOG003 ERROR  Undefined citation.
    LOG004 WARN   Overfull \\hbox beyond --overfull points (default 10pt),
                  i.e. text sticking out into the margin.

===============================================================================
SUPPRESSING A FALSE POSITIVE
===============================================================================

Regular expressions over LaTeX are never perfect.  Comments, verbatim and
lstlisting environments are excluded automatically.  For anything else, put

    % ofj-check: ignore REF002

on the offending line, or on a line of its own immediately above it.  Several IDs may
be listed, separated by spaces or commas.  Use "ignore all" to silence a line
completely.  Whole rules or whole groups can be disabled for a run with
--ignore REF002 or --ignore STY.

If you find yourself suppressing the same rule again and again, the rule is
probably wrong -- please open an issue on the template repository.
"""

import argparse
import os
import re
import sys

# ---------------------------------------------------------------------------
#  Rule table.  This is the single source of truth for IDs and severities;
#  the header comment above explains the reasoning behind each one.
# ---------------------------------------------------------------------------

ERROR = "ERROR"
WARN = "WARN"

RULES = {
    "REF001": (ERROR, "Wrong word before a cross-reference"),
    "REF002": (ERROR, "Cross-reference word not followed by '~'"),
    "REF003": (ERROR, "Cross-reference word disagrees with the label prefix"),
    "REF004": (ERROR, "\\autoref/\\cref used instead of \\ref"),
    "REF005": (ERROR, "\\label before \\caption inside a float"),
    "REF006": (WARN, "Float without a caption or without a label"),
    "REF007": (WARN, "\\eqref used instead of Eqn.~\\ref"),
    "REF008": (WARN, "Section cross-references written inconsistently"),
    "PLC001": (ERROR, "Placeholder OpenFOAM version 'v20xx'"),
    "PLC002": (ERROR, "Placeholder repository URL"),
    "PLC003": (ERROR, "Empty \\Repository for the final version"),
    "PLC004": (ERROR, "Example author identity left in place"),
    "PLC005": (ERROR, "Placeholder title"),
    "PLC006": (ERROR, "Placeholder body text from the template"),
    "PLC007": (ERROR, "Example figure figures/example.png still included"),
    "PLC008": (ERROR, "Article TYPE not set in the Makefile"),
    "PLC009": (WARN, "TODO/FIXME/XXX left in the sources"),
    "STR001": (ERROR, "AI declaration not included"),
    "STR002": (ERROR, "AI declaration hidden in review mode"),
    "STR003": (ERROR, "AI declaration guidance comments not deleted"),
    "STR004": (ERROR, "AI declaration has no active option, or both"),
    "STR005": (ERROR, "AI declaration Option B has unfilled placeholders"),
    "STR006": (WARN, "AI declaration Option A/B markers not deleted"),
    "STR007": (ERROR, "No abstract"),
    "STR008": (ERROR, "\\bibliographystyle changed from IEEEtran"),
    "STR009": (ERROR, "\\numberwithin{equation}{section} enabled"),
    "STR010": (ERROR, "\\input/\\include of a missing file"),
    "STR011": (WARN, "\\documentclass changed"),
    "STR012": (WARN, "Author contributions missing or incomplete"),
    "STR013": (WARN, "Example author initials in \\authorcontributions"),
    "REV001": (ERROR, "Identifying section not hidden in review mode"),
    "REV002": (WARN, "AI declaration may identify the authors"),
    "STY001": (WARN, "Literal 'OpenFOAM' instead of \\OF"),
    "STY002": (WARN, "Straight double quote"),
    "STY003": (WARN, "US spelling where the template uses British spelling"),
    "STY004": (WARN, "Abbreviation followed by an unescaped space"),
    "STY005": (WARN, "\\cite preceded by a plain space"),
    "STY006": (WARN, "Float placement [h]/[h!]/[H]"),
    "STY007": (WARN, "Title may not be in Title Case"),
    "BIB001": (WARN, "Bibliography entry missing author/title/year"),
    "BIB002": (WARN, "Page range with a single hyphen"),
    "BIB003": (WARN, "Bibliography entry never cited"),
    "LOG001": (ERROR, "Undefined reference"),
    "LOG002": (ERROR, "Label multiply defined"),
    "LOG003": (ERROR, "Undefined citation"),
    "LOG004": (WARN, "Overfull hbox"),
}

# ---------------------------------------------------------------------------
#  Source handling: reading, masking, positions
# ---------------------------------------------------------------------------

VERBATIM_ENVS = ("lstlisting", "verbatim", "Verbatim", "minted", "alltt",
                 "comment")


def blank_out(text, start, end):
    """Replace text[start:end] by spaces, keeping newlines and offsets."""
    chunk = "".join(c if c == "\n" else " " for c in text[start:end])
    return text[:start] + chunk + text[end:]


def mask_verbatim(text):
    """Blank the body of listing/verbatim environments."""
    for env in VERBATIM_ENVS:
        pattern = re.compile(r"\\begin\{" + env + r"\}.*?\\end\{" + env + r"\}",
                             re.DOTALL)
        while True:
            m = pattern.search(text)
            if not m:
                break
            text = blank_out(text, m.start(), m.end())
    return text


def mask_comments(text):
    """Blank LaTeX comments, respecting escaped percent signs."""
    out = list(text)
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c == "\\":
            i += 2
            continue
        if c == "%":
            j = i
            while j < n and text[j] != "\n":
                out[j] = " "
                j += 1
            i = j
        else:
            i += 1
    return "".join(out)


class Source(object):
    """One .tex file, with a raw view and a masked (code-only) view."""

    def __init__(self, path, root_dir):
        self.path = path
        self.rel = os.path.relpath(path, root_dir)
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            self.raw = fh.read()
        self.masked = mask_comments(mask_verbatim(self.raw))
        self.lines = self.raw.splitlines()

    def linecol(self, pos):
        line = self.raw.count("\n", 0, pos) + 1
        col = pos - (self.raw.rfind("\n", 0, pos) + 1) + 1
        return line, col

    def line_text(self, line):
        if 1 <= line <= len(self.lines):
            return self.lines[line - 1]
        return ""


SUPPRESS_RE = re.compile(r"%\s*ofj-check:\s*ignore\s+([A-Za-z0-9 ,]+)")


def suppressed(source, line, rule):
    """True if the finding is silenced by an 'ofj-check: ignore' comment.

    The comment may be at the end of the offending line, or on the line
    immediately above it -- but in the latter case only if that line is a
    comment and nothing else, so that a trailing suppression never silences
    the following line by accident.
    """
    candidates = [source.line_text(line)]
    above = source.line_text(line - 1)
    if above.lstrip().startswith("%"):
        candidates.append(above)
    for text in candidates:
        m = SUPPRESS_RE.search(text)
        if not m:
            continue
        ids = m.group(1).replace(",", " ").split()
        if rule in ids or "all" in ids:
            return True
    return False


class Report(object):
    def __init__(self, ignored):
        self.findings = []
        self.ignored = ignored

    def add(self, rule, source, pos, message, line=None):
        if any(rule == ig or rule.startswith(ig) for ig in self.ignored):
            return
        if source is not None and pos is not None:
            line, col = source.linecol(pos)
        else:
            col = 1
        if source is not None and suppressed(source, line, rule):
            return
        path = source.rel if source is not None else "<build>"
        self.findings.append((path, line, col, RULES[rule][0], rule, message))

    def add_at_line(self, rule, source, line, message):
        self.add(rule, source, None, message, line=line)


# ---------------------------------------------------------------------------
#  Document tree
# ---------------------------------------------------------------------------

INPUT_RE = re.compile(r"\\(?:input|include)\s*\{([^}]*)\}")


def resolve_input(name, root_dir):
    candidates = [name, name + ".tex"]
    for cand in candidates:
        path = os.path.join(root_dir, cand)
        if os.path.isfile(path):
            return path
    return None


def find_root(root_dir, explicit):
    """Locate the main .tex file: the one with \\begin{document}."""
    if explicit:
        return os.path.join(root_dir, explicit) if not os.path.isabs(explicit) \
            else explicit
    candidates = []
    for name in sorted(os.listdir(root_dir)):
        if not name.endswith(".tex"):
            continue
        path = os.path.join(root_dir, name)
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        if "\\begin{document}" in mask_comments(text):
            candidates.append(path)
    if not candidates:
        return None
    # Prefer a file that is not itself \input by another candidate
    # (ofj-template-review.tex inputs ofj-template.tex).
    included = set()
    for path in candidates:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            for m in INPUT_RE.finditer(mask_comments(fh.read())):
                target = resolve_input(m.group(1), root_dir)
                if target:
                    included.add(os.path.realpath(target))
    plain = [p for p in candidates if os.path.realpath(p) in included]
    return plain[0] if plain else candidates[0]


def collect_sources(root_path, root_dir, report):
    """Walk the \\input tree from the root document."""
    sources, seen = [], set()
    queue = [(root_path, None, None)]
    while queue:
        path, parent, pos = queue.pop(0)
        real = os.path.realpath(path)
        if real in seen:
            continue
        seen.add(real)
        src = Source(path, root_dir)
        sources.append(src)
        for m in INPUT_RE.finditer(src.masked):
            target = resolve_input(m.group(1), root_dir)
            if target is None:
                report.add("STR010", src, m.start(),
                           "cannot find the file '%s' referenced here"
                           % m.group(1))
                continue
            queue.append((target, src, m.start()))
    return sources


# ---------------------------------------------------------------------------
#  \ifdefined\review guard tracking
# ---------------------------------------------------------------------------

IF_TOKEN = re.compile(
    r"\\ifdefined\s*\\review\b"
    r"|\\ifdefined\b|\\ifx\b|\\ifnum\b|\\ifdim\b|\\iftrue\b|\\iffalse\b"
    r"|\\if[a-zA-Z]*"
    r"|\\else\b"
    r"|\\fi(?![a-zA-Z])")

REVIEW_IF_RE = re.compile(r"\\ifdefined\s*\\review")


def review_guard_state(text, pos):
    """Return (inside_review_guard, inside_its_else_branch) at offset pos."""
    stack = []
    for m in IF_TOKEN.finditer(text):
        if m.start() >= pos:
            break
        tok = m.group(0)
        if tok.startswith("\\fi"):
            if stack:
                stack.pop()
        elif tok.startswith("\\else"):
            if stack:
                stack[-1][1] = True
        else:
            stack.append([bool(REVIEW_IF_RE.match(tok)), False])
    for is_review, in_else in reversed(stack):
        if is_review:
            return True, in_else
    return False, False


# ---------------------------------------------------------------------------
#  REF: cross-reference conventions
# ---------------------------------------------------------------------------

#  Canonical word for each label prefix used by the template.
LABEL_CANON = {
    "fig": "Fig.",
    "eq": "Eqn.",
    "eqn": "Eqn.",
    "tab": "Tab.",
    "tbl": "Tab.",
    "lst": "Lst.",
    "lstlisting": "Lst.",
    "alg": "Alg.",
    "app": "App.",
}

#  Every variant we recognise, mapped to the canonical form.  A variant that
#  equals its canonical form is correct; anything else triggers REF001.
WORD_CANON = {}
for _variants, _canon in (
        (("Fig.", "Fig", "Figure", "figure", "Figs.", "Figs", "Figures"),
         "Fig."),
        (("Tab.", "Tab", "Table", "table", "Tabs.", "Tables", "Tbl.", "Tbl"),
         "Tab."),
        (("Eqn.", "Eqn", "Eq.", "Eq", "Equation", "equation", "Eqns.", "Eqns",
          "Equations"), "Eqn."),
        (("Lst.", "Lst", "Listing", "listing", "Listings", "List."), "Lst."),
        (("Alg.", "Alg", "Algorithm", "algorithm"), "Alg."),
        (("App.", "App", "Appendix", "appendix"), "App."),
):
    for _v in _variants:
        WORD_CANON[_v] = _canon

SECTION_WORDS = ("Sec.", "Sec", "Section", "section", "Sects.", "Sections")

REF_CMD_RE = re.compile(r"\\(ref|eqref|autoref|cref|Cref|nameref)\s*\{([^}]*)\}")
PREFIX_RE = re.compile(r"([A-Za-z]{1,12}\.?)(~|\\,\s*|\\ |\s+)?$")


def check_references(src, report, section_styles):
    for m in REF_CMD_RE.finditer(src.masked):
        cmd, label = m.group(1), m.group(2).strip()

        if cmd in ("autoref", "cref", "Cref", "nameref"):
            report.add("REF004", src, m.start(),
                       "\\%s is not used in this template; write the word "
                       "followed by '~\\ref{...}'" % cmd)
            continue
        if cmd == "eqref":
            report.add("REF007", src, m.start(),
                       "\\eqref typesets '(1)'; the template style is "
                       "'Eqn.~\\ref{%s}'" % label)
            continue

        prefix = label.split(":", 1)[0].lower() if ":" in label else ""
        expected = LABEL_CANON.get(prefix)

        before = src.masked[max(0, m.start() - 30):m.start()]
        pm = PREFIX_RE.search(before)
        if not pm:
            continue
        word, sep = pm.group(1), pm.group(2) or ""
        word_pos = m.start() - (len(before) - pm.start(1))

        if word in SECTION_WORDS or prefix == "sec":
            if word in SECTION_WORDS:
                section_styles.setdefault(word, []).append((src, word_pos))
                if sep != "~":
                    report.add("REF002", src, word_pos,
                               "write '%s~\\ref{%s}' with a non-breaking "
                               "space" % (word, label))
            continue

        canon = WORD_CANON.get(word)
        if canon is None:
            continue

        if canon != word:
            report.add("REF001", src, word_pos,
                       "write '%s~\\ref{%s}' instead of '%s'"
                       % (canon, label, word))
        elif sep != "~":
            shown = "no space" if sep == "" else "a plain space"
            report.add("REF002", src, word_pos,
                       "'%s' is followed by %s; write '%s~\\ref{%s}'"
                       % (word, shown, word, label))
        elif expected is not None and expected != canon:
            report.add("REF003", src, word_pos,
                       "'%s' does not match the label prefix '%s:'; "
                       "expected '%s'" % (word, prefix, expected))


FLOAT_RE = re.compile(
    r"\\begin\{(figure|table|figure\*|table\*)\}(\[[^\]]*\])?(.*?)"
    r"\\end\{\1\}", re.DOTALL)


def check_floats(src, report):
    for m in FLOAT_RE.finditer(src.masked):
        env, opt, body = m.group(1), m.group(2) or "", m.group(3)
        base = m.end(2) if m.group(2) else m.end(1) + 1

        cap = body.find("\\caption")
        lab = body.find("\\label")
        if cap == -1 or lab == -1:
            missing = []
            if cap == -1:
                missing.append("\\caption")
            if lab == -1:
                missing.append("\\label")
            report.add("REF006", src, m.start(),
                       "%s environment has no %s"
                       % (env, " and no ".join(missing)))
        elif lab < cap:
            report.add("REF005", src, base + lab,
                       "\\label must come after \\caption, otherwise the "
                       "reference points at the wrong number")

        if re.search(r"\[[^\]]*[hH]", opt):
            report.add("STY006", src, m.start(),
                       "placement '%s': the template asks for the default "
                       "(top) placement, or [p] for a float occupying more "
                       "than 75%% of a page" % opt)


def check_section_consistency(report, section_styles):
    if len(section_styles) > 1:
        used = sorted(section_styles)
        for style in used[1:]:
            src, pos = section_styles[style][0]
            report.add("REF008", src, pos,
                       "section references are written both as '%s' and as "
                       "'%s'; pick one" % (used[0], style))


# ---------------------------------------------------------------------------
#  PLC: leftover placeholders
# ---------------------------------------------------------------------------

PLACEHOLDERS = [
    ("PLC001", re.compile(r"\\OpenFOAMversions\s*\{[^}]*v20xx"),
     "replace 'v20xx' with the OpenFOAM version(s) used for the results"),
    ("PLC002", re.compile(r"\\Repository\s*\{\s*https://github\.com/xxx\s*\}"),
     "replace the placeholder repository URL"),
    ("PLC004", re.compile(r"Maria Jersey|John Smith|Philip Murphy"
                          r"|Address\d|Emailaddress\d|0000-1234-5678-0000"),
     "example author information from the template is still present"),
    ("PLC005", re.compile(r"Use Title Case"),
     "the title is still the template placeholder"),
    ("PLC006", re.compile(
        r"This is the place for an abstract"
        r"|This is the place for introduction"
        r"|This is a conclusion\."
        r"|This is an example acknowledgements section"
        r"|This is an example appendix"
        r"|Theoretical backgroud"
        r"|Examplary figure"
        r"|Text in this section"
        r"|Example text:"
        r"|code listing caption"
        r"|\\section\{Example appendix\}"
        r"|\\subsection\{Subsection\}"),
     "placeholder text from the shipped template is still present"),
    ("PLC007", re.compile(r"figures/example\.png"),
     "the example figure is still included"),
]

TODO_RE = re.compile(r"\b(TODO|FIXME|XXX)\b")


def check_placeholders(src, report):
    for rule, pattern, message in PLACEHOLDERS:
        for m in pattern.finditer(src.masked):
            report.add(rule, src, m.start(), message)
    for m in TODO_RE.finditer(src.raw):
        report.add("PLC009", src, m.start(),
                   "'%s' left in the source" % m.group(1))


# ---------------------------------------------------------------------------
#  STR / REV: structure, required settings, review integrity
# ---------------------------------------------------------------------------

AI_FILE = "aiDeclaration"
AI_GUIDANCE_MARKER = "Guidance for authors"
AI_OPTION_A = "no large language models"
AI_OPTION_B = "During the preparation of this work"
AI_BRACKETS = re.compile(r"\[(TOOL|PURPOSE|SECTIONS|METHOD)[^\]\n]*\]?")

IDENTITY_RE = re.compile(
    r"https?://(?:www\.)?(?:github|gitlab|bitbucket|zenodo)\S*"
    r"|\b(?:University|Universit\w+|Institute|Laboratory|Department)\b"
    r"|\bgrant (?:no\.?|number)\b", re.IGNORECASE)


def check_structure(root, sources, report, root_dir):
    masked = root.masked

    # --- mandatory AI declaration ---------------------------------------
    ai_src = None
    for src in sources:
        if AI_FILE in os.path.basename(src.path):
            ai_src = src
            break

    ai_inputs = [m for m in INPUT_RE.finditer(masked) if AI_FILE in m.group(1)]
    if not ai_inputs:
        report.add_at_line("STR001", root, 1,
                           "the mandatory 'Declaration on the Use of "
                           "Artificial Intelligence' section is not included; "
                           "add \\input{parts/aiDeclaration.tex}")
    else:
        pos = ai_inputs[0].start()
        in_guard, _ = review_guard_state(masked, pos)
        if in_guard:
            report.add("STR002", root, pos,
                       "the AI declaration must stay outside the "
                       "\\ifdefined\\review guard: reviewers need it")

    if ai_src is not None:
        if AI_GUIDANCE_MARKER in ai_src.raw:
            idx = ai_src.raw.find(AI_GUIDANCE_MARKER)
            report.add("STR003", ai_src, idx,
                       "delete the author-guidance comment block before "
                       "submission")
        if re.search(r"---\s*Option [AB]", ai_src.raw):
            idx = re.search(r"---\s*Option [AB]", ai_src.raw).start()
            report.add("STR006", ai_src, idx,
                       "delete the 'Option A'/'Option B' marker comments")

        a_active = AI_OPTION_A in ai_src.masked
        b_active = AI_OPTION_B in ai_src.masked
        if a_active and b_active:
            report.add_at_line("STR004", ai_src, 1,
                               "both Option A (no AI use) and Option B "
                               "(AI use) are active; keep exactly one")
        elif not a_active and not b_active:
            if not re.search(r"\\section\*?\{[^}]*Artificial Intelligence",
                             ai_src.masked):
                report.add_at_line("STR004", ai_src, 1,
                                   "no declaration text found; state either "
                                   "that no AI tools were used, or which "
                                   "were used and how the output was "
                                   "verified")
        if b_active:
            for m in AI_BRACKETS.finditer(ai_src.masked):
                shown = m.group(0).strip()
                if len(shown) > 40:
                    shown = shown[:37] + "..."
                report.add("STR005", ai_src, m.start(),
                           "unfilled placeholder '%s' in the declaration"
                           % shown)
        for m in IDENTITY_RE.finditer(ai_src.masked):
            report.add("REV002", ai_src, m.start(),
                       "'%s' may identify the authors; the AI declaration is "
                       "kept in the review version" % m.group(0).strip())

    # --- abstract --------------------------------------------------------
    if not any("\\begin{abstract}" in s.masked for s in sources):
        report.add_at_line("STR007", root, 1, "no \\begin{abstract} found")

    # --- fixed settings --------------------------------------------------
    m = re.search(r"\\bibliographystyle\s*\{([^}]*)\}", masked)
    if m and m.group(1).strip() != "IEEEtran":
        report.add("STR008", root, m.start(),
                   "the bibliography style must remain IEEEtran (found '%s')"
                   % m.group(1))

    for src in sources:
        for m in re.finditer(r"\\numberwithin\s*\{equation\}\s*\{section\}",
                             src.masked):
            report.add("STR009", src, m.start(),
                       "the template says not to enable this for submission")

    m = re.search(r"\\documentclass\s*(\[[^\]]*\])?\s*\{([^}]*)\}", masked)
    if m:
        options = (m.group(1) or "")[1:-1]
        cls = m.group(2).strip()
        if cls != "ofj":
            report.add("STR011", root, m.start(),
                       "expected \\documentclass{ofj}, found '%s'" % cls)
        else:
            wanted = {"e-only", "10pt", "reqno"}
            got = {o.strip() for o in options.split(",") if o.strip()}
            if got != wanted:
                report.add("STR011", root, m.start(),
                           "class options changed from [e-only,10pt,reqno] "
                           "to [%s]" % options)

    # --- author contributions and review integrity -----------------------
    ac = re.search(r"\\authorcontributions\s*\{", masked)
    if ac is None:
        report.add_at_line("STR012", root, 1,
                           "\\authorcontributions is missing; the journal "
                           "requires the contributions of all authors to be "
                           "stated")
    else:
        body = braced_argument(masked, ac.end() - 1)
        if "All authors have read and agreed" not in (body or ""):
            report.add("STR012", root, ac.start(),
                       "add the closing sentence 'All authors have read and "
                       "agreed to the published version of the manuscript.'")
        for m in re.finditer(r"\b(J\.S\.|P\.M\.|F\.A\.|S\.A\.)", body or ""):
            report.add("STR013", root, ac.end() + m.start(),
                       "example initials '%s' from the template" % m.group(1))
            break
        in_guard, in_else = review_guard_state(masked, ac.start())
        if not (in_guard and in_else):
            report.add("STR013" if False else "REV001", root, ac.start(),
                       "\\authorcontributions must sit in the \\else branch "
                       "of \\ifdefined\\review so it is hidden from reviewers")

    for m in INPUT_RE.finditer(masked):
        if "acknowledgement" not in m.group(1).lower():
            continue
        in_guard, in_else = review_guard_state(masked, m.start())
        if not (in_guard and in_else):
            report.add("REV001", root, m.start(),
                       "the acknowledgements must sit in the \\else branch "
                       "of \\ifdefined\\review so they are hidden from "
                       "reviewers")

    # --- repository ------------------------------------------------------
    for m in re.finditer(r"\\Repository\s*\{\s*\}", masked):
        in_guard, in_else = review_guard_state(masked, m.start())
        if in_guard and not in_else:
            continue          # the review branch is meant to be empty
        report.add("PLC003", root, m.start(),
                   "\\Repository is empty; the final version needs the "
                   "repository URL")


def braced_argument(text, open_pos):
    """Return the contents of the {...} group starting at open_pos."""
    if open_pos >= len(text) or text[open_pos] != "{":
        return None
    depth, i = 0, open_pos
    while i < len(text):
        if text[i] == "\\":
            i += 2
            continue
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[open_pos + 1:i]
        i += 1
    return None


# ---------------------------------------------------------------------------
#  STY: typography and house style
# ---------------------------------------------------------------------------

OF_RE = re.compile(r"(?<![\\A-Za-z])OpenFOAM(?![A-Za-z])")
QUOTE_RE = re.compile(r'"')
ABBREV_RE = re.compile(r"\b(e\.g\.|i\.e\.|cf\.|viz\.|et al\.|vs\.)(?=[ ][A-Za-z])")
CITE_RE = re.compile(r"(?<![~\s\\{])[ ]\\cite[tp]?\s*[\[{]")

#  Deliberately conservative: only words where the template itself, or the
#  CRediT list it ships, uses the -ise/-isation form.
US_SPELLINGS = {
    "visualization": "visualisation",
    "visualizations": "visualisations",
    "visualize": "visualise",
    "visualized": "visualised",
    "discretization": "discretisation",
    "discretizations": "discretisations",
    "discretize": "discretise",
    "discretized": "discretised",
    "conceptualization": "conceptualisation",
    "normalization": "normalisation",
    "normalized": "normalised",
    "initialization": "initialisation",
    "initialized": "initialised",
    "parameterization": "parameterisation",
    "parametrization": "parametrisation",
    "optimization": "optimisation",
    "optimized": "optimised",
    "linearization": "linearisation",
    "linearized": "linearised",
    "characterize": "characterise",
    "characterized": "characterised",
    "analyze": "analyse",
    "analyzed": "analysed",
    "behavior": "behaviour",
    "behaviors": "behaviours",
    "modeling": "modelling",
    "modeled": "modelled",
    "neighbor": "neighbour",
    "neighbors": "neighbours",
    "fiber": "fibre",
}
US_RE = re.compile(r"(?<![\\A-Za-z])(" + "|".join(sorted(US_SPELLINGS)) +
                   r")(?![A-Za-z])", re.IGNORECASE)

URLISH_RE = re.compile(r"\\(?:url|href)\s*\{[^}]*\}|https?://\S+")

TITLE_STOPWORDS = {
    "a", "an", "the", "and", "but", "or", "nor", "for", "yet", "so", "as",
    "at", "by", "in", "of", "on", "to", "up", "via", "per", "from", "with",
    "into", "over", "onto", "upon", "than", "that", "then", "when", "if",
    "is", "are", "be", "using",
}


def check_style(src, report):
    text = URLISH_RE.sub(lambda m: " " * len(m.group(0)), src.masked)

    for m in OF_RE.finditer(text):
        # \newcommand{\OF}{OpenFOAM...} legitimately spells it out
        window = text[max(0, m.start() - 60):m.start()]
        if "\\newcommand" in window or "\\renewcommand" in window:
            continue
        report.add("STY001", src, m.start(),
                   "use the \\OF macro, which adds the registered trademark "
                   "symbol")

    for m in QUOTE_RE.finditer(text):
        report.add("STY002", src, m.start(),
                   "use ``...'' rather than a straight double quote")

    for m in US_RE.finditer(text):
        word = m.group(1)
        report.add("STY003", src, m.start(),
                   "'%s': the template uses British spelling ('%s')"
                   % (word, US_SPELLINGS[word.lower()]))

    for m in ABBREV_RE.finditer(text):
        report.add("STY004", src, m.start(),
                   "'%s' followed by a plain space gives an end-of-sentence "
                   "space; write '%s\\ ' or '%s,'"
                   % (m.group(1), m.group(1), m.group(1)))

    for m in CITE_RE.finditer(text):
        report.add("STY005", src, m.start(),
                   "use '~\\cite{...}' so the citation cannot be separated "
                   "from the preceding word by a line break")


def check_title(root, report):
    m = re.search(r"\\title\s*(\[[^\]]*\])?\s*\{", root.masked)
    if not m:
        return
    title = braced_argument(root.masked, m.end() - 1)
    if not title:
        return
    plain = re.sub(r"\\[A-Za-z]+\s*", " ", title)
    plain = re.sub(r"[{}$\\]", " ", plain)
    words = [w for w in re.split(r"[\s/]+", plain.strip()) if w]
    offenders = []
    for i, word in enumerate(words):
        core = word.strip("-—–,.:;()[]")
        if not core or not core[0].isalpha():
            continue
        if core[0].isupper():
            continue
        if i in (0, len(words) - 1):
            offenders.append(core)
        elif core.lower() not in TITLE_STOPWORDS:
            offenders.append(core)
    if offenders:
        report.add("STY007", root, m.start(),
                   "the title should use Title Case; check: %s"
                   % ", ".join(offenders[:6]))


# ---------------------------------------------------------------------------
#  BIB: bibliography
# ---------------------------------------------------------------------------

BIB_ENTRY_RE = re.compile(r"@(\w+)\s*\{\s*([^,]+),", re.IGNORECASE)
CITE_KEYS_RE = re.compile(r"\\cite[tp]?\s*(?:\[[^\]]*\])*\s*\{([^}]*)\}")


def check_bibliography(root, sources, report, root_dir):
    m = re.search(r"\\bibliography\s*\{([^}]*)\}", root.masked)
    if not m:
        return
    cited = set()
    for src in sources:
        for cm in CITE_KEYS_RE.finditer(src.masked):
            cited.update(k.strip() for k in cm.group(1).split(","))

    for name in m.group(1).split(","):
        name = name.strip()
        path = os.path.join(root_dir, name if name.endswith(".bib")
                            else name + ".bib")
        if not os.path.isfile(path):
            report.add("STR010", root, m.start(),
                       "bibliography file '%s' not found" % name)
            continue
        bib = Source(path, root_dir)
        entries = list(BIB_ENTRY_RE.finditer(bib.masked))
        for i, em in enumerate(entries):
            kind, key = em.group(1).lower(), em.group(2).strip()
            end = entries[i + 1].start() if i + 1 < len(entries) \
                else len(bib.masked)
            body = bib.masked[em.end():end]
            if kind in ("comment", "string", "preamble"):
                continue
            for field in ("author", "title", "year"):
                if not re.search(r"\b" + field + r"\s*=", body, re.IGNORECASE):
                    report.add("BIB001", bib, em.start(),
                               "entry '%s' has no %s field" % (key, field))
            pm = re.search(r"\bpages\s*=\s*[{\"]?\s*(\d+)\s*-\s*(\d+)",
                           body, re.IGNORECASE)
            if pm:
                report.add("BIB002", bib, em.end() + pm.start(),
                           "page range '%s-%s' should use an en-dash: "
                           "'%s--%s'" % (pm.group(1), pm.group(2),
                                         pm.group(1), pm.group(2)))
            if key not in cited:
                report.add("BIB003", bib, em.start(),
                           "entry '%s' is never cited" % key)


# ---------------------------------------------------------------------------
#  LOG: LaTeX log file
# ---------------------------------------------------------------------------

LOG_PATTERNS = [
    ("LOG001", re.compile(r"LaTeX Warning: Reference [`'\"]([^'\"]+)' on page "
                          r"(\S+) undefined")),
    ("LOG002", re.compile(r"LaTeX Warning: Label [`'\"]([^'\"]+)' multiply "
                          r"defined")),
    ("LOG003", re.compile(r"(?:LaTeX|Package natbib) Warning: Citation "
                          r"[`'\"]([^'\"]+)'[^\n]*undefined")),
]
OVERFULL_RE = re.compile(r"Overfull \\hbox \(([\d.]+)pt too wide\)"
                         r"[^\n]*?(?:at lines? (\d+)|)")


def check_logs(root_dir, report, threshold, explicit):
    logs = []
    if explicit:
        logs = [explicit]
    else:
        logs = [os.path.join(root_dir, f) for f in sorted(os.listdir(root_dir))
                if f.endswith(".log")]
    if not logs:
        print("checkStyle: no .log file found; run 'make' first",
              file=sys.stderr)
        return
    for path in logs:
        log = Source(path, root_dir)
        for rule, pattern in LOG_PATTERNS:
            for m in pattern.finditer(log.raw):
                report.add(rule, log, m.start(),
                           "%s (from the LaTeX log)" % m.group(0).strip())
        for m in OVERFULL_RE.finditer(log.raw):
            if float(m.group(1)) >= threshold:
                report.add("LOG004", log, m.start(),
                           "overfull hbox, %spt too wide%s"
                           % (m.group(1),
                              " at line " + m.group(2) if m.group(2) else ""))


# ---------------------------------------------------------------------------
#  Makefile
# ---------------------------------------------------------------------------

def check_makefile(root_dir, report):
    path = os.path.join(root_dir, "Makefile")
    if not os.path.isfile(path):
        return
    mk = Source(path, root_dir)
    for m in re.finditer(r"^\s*TYPE\s*=\s*SetTypeInMakefile", mk.raw,
                         re.MULTILINE):
        report.add("PLC008", mk, m.start(),
                   "choose the article type: FullPaper, TNote or RevPaper")


# ---------------------------------------------------------------------------
#  Driver
# ---------------------------------------------------------------------------

def list_rules():
    groups = {}
    for rule, (sev, summary) in sorted(RULES.items()):
        groups.setdefault(rule[:3], []).append((rule, sev, summary))
    for group in sorted(groups):
        print(group)
        for rule, sev, summary in groups[group]:
            print("  %-8s %-6s %s" % (rule, sev, summary))
    print("\nSee the comment block at the top of this script for the "
          "rationale behind each rule.")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Check an OpenFOAM Journal manuscript against the "
                    "conventions of the official LaTeX template.",
        epilog="See the header of this script for the full rule table.")
    parser.add_argument("directory", nargs="?", default=".",
                        help="manuscript directory (default: current)")
    parser.add_argument("--main", metavar="FILE",
                        help="main .tex file (default: auto-detected)")
    parser.add_argument("--ignore", action="append", default=[],
                        metavar="RULE",
                        help="rule ID or group prefix to ignore; repeatable")
    parser.add_argument("--strict", action="store_true",
                        help="treat warnings as errors")
    parser.add_argument("--quiet", action="store_true",
                        help="report errors only")
    parser.add_argument("--check-log", action="store_true",
                        help="also parse the LaTeX .log files")
    parser.add_argument("--log", metavar="FILE",
                        help="a specific .log file to parse (implies "
                             "--check-log)")
    parser.add_argument("--overfull", type=float, default=10.0, metavar="PT",
                        help="overfull hbox threshold in points (default: 10)")
    parser.add_argument("--list-rules", action="store_true",
                        help="print the rule table and exit")
    args = parser.parse_args(argv)

    if args.list_rules:
        list_rules()
        return 0

    root_dir = os.path.abspath(args.directory)
    if not os.path.isdir(root_dir):
        print("checkStyle: not a directory: %s" % root_dir, file=sys.stderr)
        return 2

    report = Report([i.upper() for i in args.ignore])

    root_path = find_root(root_dir, args.main)
    if root_path is None or not os.path.isfile(root_path):
        print("checkStyle: could not find the main .tex file (the one with "
              "\\begin{document}); use --main", file=sys.stderr)
        return 2

    sources = collect_sources(root_path, root_dir, report)
    root = sources[0]

    section_styles = {}
    for src in sources:
        check_references(src, report, section_styles)
        check_floats(src, report)
        check_placeholders(src, report)
        check_style(src, report)
    check_section_consistency(report, section_styles)
    check_title(root, report)
    check_structure(root, sources, report, root_dir)
    check_bibliography(root, sources, report, root_dir)
    check_makefile(root_dir, report)
    if args.check_log or args.log:
        check_logs(root_dir, report, args.overfull, args.log)

    findings = sorted(set(report.findings),
                      key=lambda f: (f[0], f[1], f[2], f[4]))
    if args.quiet:
        findings = [f for f in findings if f[3] == ERROR]

    for path, line, col, sev, rule, message in findings:
        print("%s:%d:%d: %s %s: %s" % (path, line, col, sev, rule, message))

    n_err = sum(1 for f in findings if f[3] == ERROR)
    n_warn = sum(1 for f in findings if f[3] == WARN)

    print("\nchecked %d file(s) from %s: %d error(s), %d warning(s)"
          % (len(sources), os.path.relpath(root_path, root_dir),
             n_err, n_warn))
    if not findings:
        print("No issues found.")

    if n_err or (args.strict and n_warn):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

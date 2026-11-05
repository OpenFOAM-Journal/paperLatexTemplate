"""Render a Report as console text, Markdown or JSON.

Every finding is shown with what triggered it: the evidence, the template
change behind it and its importance (decision D2).
"""
from __future__ import annotations

import json
import textwrap
from pathlib import Path
from typing import List

from . import generations
from .model import IMPORTANCE_ORDER, Finding, Report

FACT_GROUPS = (("input", "Input"), ("pdf", "PDF"), ("source", "LaTeX sources"), ("template", "Template"))
IMPORTANCE_TITLES = {"required": "Required by the current template",
                     "convention": "Template conventions not followed",
                     "cosmetic": "Cosmetic differences",
                     "info": "Supporting evidence / for information"}


def _points_to(f: Finding) -> str:
    if f.implies_from is None and f.implies_to is None:
        return ""
    return generations.describe(f.implies_from, f.implies_to)


def _verdict_lines(report: Report) -> List[str]:
    v = report.verdict
    details = []
    if v.range_from or v.range_to:
        details.append(f"matches {generations.describe(v.range_from, v.range_to)}")
    if v.confidence:
        details.append(f"confidence: {v.confidence}")
    return [v.headline + (f" ({'; '.join(details)})" if details else ""), v.explanation]


def author_message(report: Report) -> List[str]:
    """A ready-to-paste note for the authors, built from the advice of the findings.
    Findings with the generic 'use the current template' advice are merged into one point
    that lists the differences."""
    from .source_rules import ADVICE_UPDATE
    items, generic = [], []
    for importance in IMPORTANCE_ORDER[:3]:            # required, convention, cosmetic
        for f in report.findings:
            if f.importance != importance or not f.advice or f.kind == "consistent":
                continue
            if f.advice == ADVICE_UPDATE:
                generic.append(f.title)
            elif f.advice not in items:
                items.append(f.advice)
    if generic:
        items.append(ADVICE_UPDATE + " Differences found: " + "; ".join(dict.fromkeys(generic)) + ".")
    if not items:
        return []
    current = generations.by_id(generations.CURRENT)
    return (["Dear authors,", "",
             "your submission was checked against the current OpenFOAM Journal LaTeX template "
             f"(version of {current.start}, https://github.com/OpenFOAM-Journal/paperLatexTemplate). "
             "Please address the following points:", ""]
            + [f"- {item}" for item in items])


def render_text(report: Report, width: int = 100) -> str:
    wrap = lambda s, ind="    ": textwrap.fill(s, width, initial_indent=ind, subsequent_indent=ind)  # noqa: E731
    name = report.submission.get("archive") or Path(report.submission["given"]).name
    out = [f"ofj-check {report.tool_version}: {name}", "=" * min(width, 70)]
    head, expl = _verdict_lines(report)
    out += [f"VERDICT: {head}", wrap(expl, "  ") if expl else ""]
    v = report.verdict
    if v.triggers:
        out.append("  Triggered by:")
        out += [textwrap.fill(f"- {t}", width, initial_indent="    ", subsequent_indent="      ")
                for t in v.triggers]
    if v.remarks:
        out.append("  Also:")
        out += [textwrap.fill(f"- {r}", width, initial_indent="    ", subsequent_indent="      ")
                for r in v.remarks]
    out += ["", "-" * min(width, 70), "Details", ""]

    groups = report.findings_by_importance()
    if not report.findings:
        out += ["Findings: none", ""]
    for importance in IMPORTANCE_ORDER:
        items = groups.get(importance) or []
        if not items:
            continue
        out.append(f"{IMPORTANCE_TITLES[importance]} ({len(items)}):")
        if importance == "info":
            for f in items:
                where = f" @ {f.evidence[0].location}" if f.evidence else ""
                out.append(f"  [{f.rule_id}] {f.title}"
                           + (f"  -> {_points_to(f)}" if _points_to(f) else "") + where)
            out.append("")
            continue
        for f in items:
            out.append(f"  [{f.rule_id}] {f.title}  ({f.reliability} signal"
                       + (f", points to {_points_to(f)}" if _points_to(f) else "") + ")")
            out.append(wrap(f.message))
            for ev in f.evidence[:5]:
                out.append(wrap(f"evidence: {ev.location}" + (f": {ev.excerpt}" if ev.excerpt else "")))
            if len(f.evidence) > 5:
                out.append(f"    ... and {len(f.evidence) - 5} more")
            if f.template_change:
                out.append(wrap(f"template change: {f.template_change}"))
        out.append("")

    for title, items in (("Warnings", report.warnings), ("Notes", report.notes)):
        if items:
            out.append(f"{title}:")
            out += [textwrap.fill(f"- {w}", width, initial_indent="  ", subsequent_indent="    ")
                    for w in items]
            out.append("")

    message = author_message(report)
    if message:
        out.append("Suggested message to the authors:")
        out += [textwrap.fill(line, width, initial_indent="  | ",
                              subsequent_indent="  |   " if line.startswith("- ") else "  | ")
                if line else "  |" for line in message]
        out.append("")

    for key, title in FACT_GROUPS:
        facts = [f for f in report.facts if f.group == key]
        if facts:
            out.append(f"{title}:")
            label_w = max(len(f.label) for f in facts)
            out += [f"  {f.label.ljust(label_w)}  {f.value}" for f in facts]
            out.append("")
    return "\n".join(out).rstrip() + "\n"


def _md_escape(text: str) -> str:
    return text.replace("|", "\\|")


def render_markdown(report: Report) -> str:
    name = report.submission.get("archive") or Path(report.submission["given"]).name
    head, expl = _verdict_lines(report)
    v = report.verdict
    out = [f"# OFJ template check: {name}", "",
           f"**Verdict: {head}**", ""]
    if expl:
        out += [expl, ""]
    if v.triggers:
        out += ["Triggered by:", ""] + [f"- {t}" for t in v.triggers] + [""]
    if v.remarks:
        out += ["Also:", ""] + [f"- **{r}**" if r.startswith("NOT ANONYMOUS") else f"- {r}"
                                for r in v.remarks] + [""]
    message = author_message(report)
    if message:
        out += ["### Suggested message to the authors", ""]
        out += [f"> {line}" if line else ">" for line in message] + [""]

    out += ["## Details: what was found", ""]
    if not report.findings:
        out += ["No findings.", ""]
    groups = report.findings_by_importance()
    for importance in IMPORTANCE_ORDER:
        items = groups.get(importance) or []
        if not items:
            continue
        out += [f"### {IMPORTANCE_TITLES[importance]} ({len(items)})", ""]
        if importance == "info":
            out += [f"- **{f.rule_id}** {f.title}" + (f" → {_points_to(f)}" if _points_to(f) else "")
                    + (f" (`{f.evidence[0].location}`)" if f.evidence else "") for f in items]
            out.append("")
            continue
        for f in items:
            out += [f"#### {f.rule_id}: {f.title}", "",
                    f"*{f.reliability} signal · indicates: {f.kind}"
                    + (f" · points to {_points_to(f)}" if _points_to(f) else "") + "*", "",
                    f.message, ""]
            if f.evidence:
                out.append("Evidence:")
                out += [f"- {ev.location}" + (f": `{ev.excerpt}`" if ev.excerpt else "")
                        for ev in f.evidence]
                out.append("")
            if f.template_change:
                out += [f"Template change: {f.template_change}", ""]
            if f.advice:
                out += [f"Suggested note to the authors: {f.advice}", ""]

    for title, items in (("Warnings", report.warnings), ("Notes", report.notes)):
        if items:
            out += [f"## {title}", ""] + [f"- {w}" for w in items] + [""]

    for key, title in FACT_GROUPS:
        facts = [f for f in report.facts if f.group == key]
        if facts:
            out += [f"## {title}", "", "| | |", "|---|---|"]
            out += [f"| {_md_escape(f.label)} | {_md_escape(f.value)} |" for f in facts]
            out.append("")

    out += ["---", f"ofj-check {report.tool_version}, {report.created}. Template generations "
            "and fingerprints: docs/FINGERPRINTS.md.", ""]
    return "\n".join(out)


def render_json(report: Report) -> str:
    return json.dumps(report.to_dict(), indent=2, ensure_ascii=False) + "\n"

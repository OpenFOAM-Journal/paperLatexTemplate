"""Combine all findings into one verdict.

Every finding that points to a range of template generations (or argues
against one) is a vote, weighted by its reliability. The generations that
contradict the least evidence form the estimated range; the newest of them is
the closest generation. Decision D2: the verdict names the findings that
triggered it. Decision D3: cosmetic differences such as the copyright year
never make a submission "outdated" on their own.
"""
from __future__ import annotations

from typing import Iterable, List, Optional, Tuple

from . import generations
from .model import CONVENTION, INFO, MEDIUM, REQUIRED, STRONG, WEAK, Finding, Verdict

WEIGHT = {STRONG: 3, MEDIUM: 2, WEAK: 1}
DECISIVE_IMPORTANCE = (REQUIRED, CONVENTION)
DECISIVE_RELIABILITY = (STRONG, MEDIUM)


def _bounds(first: Optional[str], last: Optional[str]) -> Tuple[int, int]:
    lo = generations.index(first) if first else 0
    hi = generations.index(last) if last else len(generations.GENERATIONS) - 1
    return lo, hi


def is_version_signal(f: Finding) -> bool:
    return f.kind not in ("not-template", "anonymity") and any(
        (f.implies_from, f.implies_to, f.excludes_from, f.excludes_to))


def violations(signals: Iterable[Finding]) -> List[int]:
    """For every generation: total weight of the evidence that contradicts it."""
    n = len(generations.GENERATIONS)
    v = [0] * n
    for f in signals:
        w = WEIGHT.get(f.reliability, 1)
        if f.implies_from or f.implies_to:
            lo, hi = _bounds(f.implies_from, f.implies_to)
            for g in range(n):
                if not lo <= g <= hi:
                    v[g] += w
        if f.excludes_from or f.excludes_to:
            lo, hi = _bounds(f.excludes_from, f.excludes_to)
            for g in range(lo, hi + 1):
                v[g] += w
    return v


def best_generations(signals: List[Finding], candidates: Optional[List[int]] = None) -> List[int]:
    v = violations(signals)
    candidates = candidates if candidates else list(range(len(v)))
    least = min(v[g] for g in candidates)
    return [g for g in candidates if v[g] == least]


def is_decisive(f: Finding) -> bool:
    return f.kind == "outdated" and f.importance in DECISIVE_IMPORTANCE \
        and f.reliability in DECISIVE_RELIABILITY


def _label(f: Finding) -> str:
    return f"{f.rule_id}: {f.title}"


def _gen_text(idx: int) -> str:
    g = generations.GENERATIONS[idx]
    return f"{g.id} ({g.start} to {g.end or 'today'}, '{g.title}')"


def apply_context(findings: List[Finding]) -> None:
    """Adjust findings to what else was found. In a production version (journal data filled in
    by the editor) visible authors and the copyright year are expected, not problems."""
    if not any(f.kind == "production" for f in findings):
        return
    for f in findings:
        if f.kind == "anonymity":
            f.kind, f.importance, f.advice = "info", INFO, ""
            f.title += " (expected in a production version)"
        elif f.rule_id in ("SRC07", "PDF09") and f.title.startswith("Copyright year") and f.kind != "consistent":
            f.kind, f.importance, f.advice = "info", INFO, ""
            f.title += " (set by the editor in a production version)"
            f.implies_from = f.implies_to = None


def _remarks(findings: List[Finding]) -> List[str]:
    remarks = []
    prod = [f for f in findings if f.kind == "production"]
    if prod:
        source = [f for f in prod if f.rule_id == "PRD01"]     # exact values from ofjart.cls
        remarks.append("PRODUCTION VERSION (not an author submission): " +
                       "; ".join(e.excerpt for f in (source or prod)[:1] for e in f.evidence) + ".")
    anon = [f for f in findings if f.kind == "anonymity"]
    if anon:
        remarks.append("NOT ANONYMOUS: the PDF shows author information (" +
                       "; ".join(e.excerpt or e.location for e in anon[0].evidence[:3]) + ").")
    plc = [f for f in findings if f.kind == "placeholder" or f.rule_id == "PLC01"]
    if plc:
        remarks.append("Template placeholders or example content left: " +
                       "; ".join(f.title for f in plc[:4]) + ".")
    xchk = [f for f in findings if f.rule_id.startswith("XCHK")]
    remarks += [f"{f.title}." for f in xchk]
    return remarks


def decide(findings: List[Finding], rules_run: int) -> Verdict:
    if rules_run == 0:
        return Verdict(kind="inconclusive", headline="Nothing could be checked",
                       explanation="No rules were applicable to this input.")
    remarks = _remarks(findings)

    # 1. not the template at all
    not_template = [f for f in findings if f.kind == "not-template"]
    if not_template:
        support = [f for f in findings if f.kind == "consistent" and f.reliability == STRONG]
        conf = "medium" if support else "high"
        expl = not_template[0].message
        if support:
            expl += (" Some template elements were found nevertheless (" +
                     "; ".join(f.rule_id for f in support[:4]) + "), e.g. sources and PDF disagree.")
        return Verdict(kind="not-template", headline="Not made with the OFJ template", confidence=conf,
                       explanation=expl, triggers=[_label(f) for f in not_template], remarks=remarks)

    signals = [f for f in findings if is_version_signal(f)]
    decisive = [f for f in findings if is_decisive(f)]
    minor = [f for f in findings if (f.kind == "outdated" and not is_decisive(f)) or f.kind == "style"]
    major_mod = [f for f in findings if f.kind == "modified" and f.importance in DECISIVE_IMPORTANCE
                 and f.reliability in DECISIVE_RELIABILITY]
    minor_mod = [f for f in findings if f.kind == "modified" and f not in major_mod]
    current = generations.index(generations.CURRENT)

    if not signals and not major_mod:
        return Verdict(kind="inconclusive", headline="No template fingerprints found",
                       explanation="Neither the sources nor the PDF contained anything that tells the "
                                   "template version apart.", remarks=remarks)

    # 2. an older template
    if decisive:
        lo, hi = 0, current
        for f in decisive:
            a, b = _bounds(f.implies_from, f.implies_to)
            lo, hi = max(lo, a), min(hi, b)
        mixed = lo > hi
        best = best_generations(signals, None if mixed else list(range(lo, hi + 1)))
        closest = max(best)
        conflicts = [f for f in signals if f.reliability == STRONG and _contradicts(f, closest)]
        mixed = mixed or bool(conflicts)
        conf = "high" if any(f.reliability == STRONG for f in decisive) and not mixed else "medium"
        gen = generations.GENERATIONS[closest]
        expl = (f"{len(decisive)} finding(s) show that the current template "
                f"({generations.CURRENT}, since {generations.by_id(generations.CURRENT).start}) was not "
                f"used. The submission matches {generations.describe(generations.GENERATIONS[min(best)].id, gen.id)} best.")
        if mixed:
            expl += (" Parts of it come from different template versions (" +
                     "; ".join(_label(f) for f in conflicts[:3]) + ").")
        if major_mod:
            expl += " Template files were also modified: " + "; ".join(f.title for f in major_mod[:3]) + "."
        if minor:
            expl += " Minor differences as well: " + "; ".join(f.title for f in minor[:4]) + "."
        return Verdict(kind="outdated",
                       headline=f"Older template, closest to {gen.id} '{gen.title}'"
                                + (", mixed with other versions" if mixed else "")
                                + (", modified" if major_mod else ""),
                       closest_generation=gen.id, range_from=generations.GENERATIONS[min(best)].id,
                       range_to=gen.id, confidence=conf, explanation=expl,
                       triggers=[_label(f) for f in decisive + major_mod]
                                + [f"(minor) {_label(f)}" for f in minor + minor_mod],
                       remarks=remarks)

    # 3. current generation possible: modified, or current
    best = best_generations(signals) if signals else [current]
    v = violations(signals)
    older = [g for g in range(current) if v[g] == 0]
    weakest = min((v[g] for g in range(current)), default=0)
    conf = "high" if weakest >= 3 else "medium" if weakest >= 1 else "low"
    if older:
        conf_text = ("Nothing points to an older template, but this input cannot tell the current "
                     f"template apart from {', '.join(generations.GENERATIONS[g].id for g in older)}.")
    elif conf == "medium":
        weak_gen = min(range(current), key=lambda g: v[g])
        conf_text = (f"The evidence against {_gen_text(weak_gen)} is weak; the two differ only in "
                     "details that this input shows little of.")
    else:
        conf_text = "Every older generation is ruled out by clear evidence."
    lo = min(best)
    if major_mod:
        return Verdict(kind="modified", headline="Current template, but modified by the authors",
                       closest_generation=generations.CURRENT, range_from=generations.GENERATIONS[lo].id,
                       range_to=None, confidence=conf,
                       explanation="The submission follows the current template but changes parts that "
                                   "authors should not change. " + conf_text,
                       triggers=[_label(f) for f in major_mod] + [f"(minor) {_label(f)}" for f in minor + minor_mod],
                       remarks=remarks)
    headline = "Current template" if not older else "Consistent with the current template"
    if minor or minor_mod:
        headline += ", with minor differences"
    return Verdict(kind="current", headline=headline, closest_generation=generations.CURRENT,
                   range_from=generations.GENERATIONS[lo].id, range_to=None, confidence=conf,
                   explanation=conf_text, triggers=[f"(minor) {_label(f)}" for f in minor + minor_mod],
                   remarks=remarks)


def _contradicts(f: Finding, g: int) -> bool:
    if f.implies_from or f.implies_to:
        lo, hi = _bounds(f.implies_from, f.implies_to)
        if not lo <= g <= hi:
            return True
    if f.excludes_from or f.excludes_to:
        lo, hi = _bounds(f.excludes_from, f.excludes_to)
        if lo <= g <= hi:
            return True
    return False


def channel_range(findings: List[Finding]) -> Optional[Tuple[int, int]]:
    """Best generation range from one channel (PDF or sources), if it has strong signals.
    Weak signals are left out: alone they must not make two channels disagree."""
    signals = [f for f in findings if is_version_signal(f) and f.reliability in (STRONG, MEDIUM)]
    if not any(f.reliability == STRONG for f in signals):
        return None
    best = best_generations(signals)
    return min(best), max(best)

"""Evidence model: what a check found, why it matters, and what it implies (decision D2)."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional

# Importance of a finding for the editor (FINGERPRINTS.md, decision D2).
REQUIRED = "required"        # the current template demands it (e.g. a mandatory section)
CONVENTION = "convention"    # a template convention is not followed (e.g. \autoref)
COSMETIC = "cosmetic"        # visible but harmless (e.g. the copyright year)
INFO = "info"                # context only, no judgement
IMPORTANCE_ORDER = (REQUIRED, CONVENTION, COSMETIC, INFO)

# How reliable the signal is (FINGERPRINTS.md: S / M / W).
STRONG, MEDIUM, WEAK = "strong", "medium", "weak"

# What a finding indicates. "consistent" = evidence compatible with the current template;
# "style" = a template convention not followed, independent of the template version;
# "production" = journal data filled in by the editor (a production / published version).
KINDS = ("outdated", "consistent", "modified", "not-template", "anonymity", "placeholder", "style",
         "production", "info")

# Verdicts, with their exit codes.
VERDICT_EXIT = {"current": 0, "outdated": 1, "modified": 1, "not-template": 2, "inconclusive": 3}
EXIT_ENVIRONMENT = 4
EXIT_INPUT = 5


@dataclass
class Evidence:
    location: str                 # "PDF p. 1", "link on p. 2", "ofj-template.tex:58"
    excerpt: str = ""


@dataclass
class Finding:
    rule_id: str                  # e.g. PDF11, SRC02 (docs/FINGERPRINTS.md)
    title: str
    kind: str
    importance: str
    reliability: str
    message: str                  # what was observed and why it matters
    evidence: List[Evidence] = field(default_factory=list)
    implies_from: Optional[str] = None   # generation range the signal points to
    implies_to: Optional[str] = None
    template_change: str = ""     # "2026-03-31 cd2b7f2: \\autoref replaced by Eqn.~\\ref ..."
    advice: str = ""              # suggested wording for the authors
    excludes_from: Optional[str] = None  # generation range the signal argues against
    excludes_to: Optional[str] = None


@dataclass
class Fact:
    group: str                    # input | pdf | source | template
    label: str
    value: str


@dataclass
class Verdict:
    kind: str                     # key of VERDICT_EXIT
    headline: str
    closest_generation: Optional[str] = None
    range_from: Optional[str] = None
    range_to: Optional[str] = None
    confidence: str = ""
    explanation: str = ""
    triggers: List[str] = field(default_factory=list)   # findings that decided the verdict
    remarks: List[str] = field(default_factory=list)    # also important (anonymity, placeholders ...)

    @property
    def exit_code(self) -> int:
        return VERDICT_EXIT[self.kind]


@dataclass
class Report:
    tool_version: str
    created: str
    submission: Dict[str, str]
    template: Dict[str, str]
    verdict: Verdict
    findings: List[Finding] = field(default_factory=list)
    facts: List[Fact] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def findings_by_importance(self) -> Dict[str, List[Finding]]:
        groups: Dict[str, List[Finding]] = {k: [] for k in IMPORTANCE_ORDER}
        for f in self.findings:
            groups.setdefault(f.importance, []).append(f)
        return groups

    def to_dict(self) -> dict:
        data = asdict(self)
        data["verdict"]["exit_code"] = self.verdict.exit_code
        return data

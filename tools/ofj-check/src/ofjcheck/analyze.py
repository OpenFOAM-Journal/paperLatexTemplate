"""Run all checks on a submission and assemble the report."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, List, Optional

from . import __version__, generations
from .inputs import Submission, document_class
from .model import Fact, Finding, Report
from .template_repo import TemplateRepo, TemplateStatus, catalogue_coverage_warnings
from .verdict import apply_context, decide

CLASS_FILES = ("ofj.cls", "ofjart.cls", "amsart.cls", "jams-l.cls", "orcidlink.sty",
               "tensorNotation.sty", "finiteVolumeNotation.sty", "Makefile")


@dataclass
class Context:
    """Everything a rule may look at. The PDF is opened once and shared."""
    submission: Submission
    repo: TemplateRepo
    template: TemplateStatus
    warnings: List[str] = field(default_factory=list)
    _pdf: object = None
    _document: object = None
    _index: object = None
    _head_main: Optional[str] = None

    @property
    def document(self):
        """The LaTeX document, loaded from the main .tex file and everything it inputs."""
        if self._document is None and self.submission.main_tex is not None:
            from .latex import load_document
            self._document = load_document(self.submission.main_tex, self.submission.root)
        return self._document

    @property
    def index(self):
        """Every version of every template file (exact matching)."""
        if self._index is None:
            from .filematch import TemplateIndex
            self._index = TemplateIndex.build(self.repo, self.template.head.sha)
        return self._index

    @property
    def head_main_tex(self) -> str:
        """The main file of the current template, to compare with its present conventions."""
        if self._head_main is None:
            try:
                self._head_main = self.repo.read_file(self.template.head.sha, "ofj-template.tex") \
                    .decode("utf-8", errors="replace")
            except Exception:  # noqa: BLE001 - the template may have renamed its main file
                self.warnings.append("The current template has no ofj-template.tex; checks that "
                                     "compare with its main file were skipped.")
                self._head_main = ""
        return self._head_main

    @property
    def pdf_view(self):
        """The PDF with cached text, fonts, links and layout (see pdf_view.py)."""
        if getattr(self, "_pdf_view", None) is None:
            from .pdf_view import PdfView
            self._pdf_view = PdfView(self.pdf)
        return self._pdf_view

    @property
    def pdf(self):
        if self._pdf is None and self.submission.pdf is not None:
            from .pdf_facts import open_pdf
            self._pdf = open_pdf(self.submission.pdf)
        return self._pdf

    def close(self) -> None:
        if self._pdf is not None:
            self._pdf.close()
            self._pdf = None


Rule = Callable[[Context], List[Finding]]


def _source_rules(ctx: Context) -> List[Finding]:
    from .source_rules import run_source_rules
    return run_source_rules(ctx)


def _pdf_rules(ctx: Context) -> List[Finding]:
    from .pdf_rules import run_pdf_rules
    return run_pdf_rules(ctx)


# Source rules and PDF rules register here.
SOURCE_RULES: List[Rule] = [_source_rules]
PDF_RULES: List[Rule] = [_pdf_rules]


def _input_facts(sub: Submission) -> List[Fact]:
    facts = [Fact("input", "Checked", {"pdf": "PDF only", "latex": "LaTeX sources only",
                                       "both": "PDF and LaTeX sources"}[sub.mode]),
             Fact("input", "Given path", sub.given_as_typed or sub.given.name)]
    if sub.archive:
        facts.append(Fact("input", "Archive", sub.archive))
    if sub.pdf and sub.pdf != sub.given:
        facts.append(Fact("input", "Manuscript PDF", sub.display(sub.pdf)))
    if sub.main_tex:
        facts.append(Fact("input", "Main .tex file", sub.display(sub.main_tex)))
    if sub.root is not None and sub.mode != "pdf":
        facts.append(Fact("input", ".tex files", str(len(sub.tex_files))))
        if sub.other_pdfs:
            facts.append(Fact("input", "Other PDFs (figures etc.)", str(len(sub.other_pdfs))))
    return facts


def _source_facts(ctx: Context) -> List[Fact]:
    sub = ctx.submission
    facts = []
    if sub.main_tex:
        facts.append(Fact("source", "Document class", document_class(sub.main_tex) or "-"))
        doc = ctx.document
        facts.append(Fact("source", "Files in the document",
                          ", ".join(f.rel for f in doc.files)))
        if doc.missing_inputs:
            ctx.warnings.append("Files input by the document are missing from the submission: "
                                + "; ".join(doc.missing_inputs))
    if sub.root is not None:
        shipped = [name for name in CLASS_FILES if any(sub.root.rglob(name))]
        facts.append(Fact("source", "Template support files shipped",
                          ", ".join(shipped) if shipped else "none"))
    return facts


def _template_facts(status: TemplateStatus) -> List[Fact]:
    current = generations.by_id(generations.CURRENT)
    return [Fact("template", "Template repository", status.url),
            Fact("template", "Compared against", f"{status.ref} at {status.head}"),
            Fact("template", "Template copy", status.source + (
                f", fetched {status.last_fetch:%Y-%m-%d %H:%M} UTC" if status.last_fetch else "")),
            Fact("template", "Current generation", f"{current.id} (since {current.start}): {current.title}"),
            Fact("template", "Fingerprint catalogue covers", generations.CATALOGUE_COMMIT[:7])]


def run_checks(sub: Submission, repo: TemplateRepo, status: TemplateStatus) -> Report:
    ctx = Context(submission=sub, repo=repo, template=status)
    warnings = list(status.warnings)
    warnings += catalogue_coverage_warnings(repo, generations.CATALOGUE_COMMIT, status.head)
    facts = _input_facts(sub) + _template_facts(status)
    findings: List[Finding] = []
    source_findings: List[Finding] = []
    rules_run = 0
    try:
        if sub.mode in ("latex", "both"):
            facts += _source_facts(ctx)
            for rule in SOURCE_RULES:
                source_findings += rule(ctx)
                rules_run += 1
            findings += source_findings
        if sub.mode in ("pdf", "both"):
            from .pdf_facts import basic_facts
            try:
                facts += basic_facts(ctx.pdf)
                view = ctx.pdf_view
                facts += [Fact("pdf", "Body font", view.body_font() or "-"),
                          Fact("pdf", "Margin line numbers (review build)",
                               "yes" if view.line_numbers(0) >= 5 else "no")]
            except Exception as exc:  # noqa: BLE001 - a broken PDF is a result, not a crash
                warnings.append(f"The PDF could not be read: {exc}")
            else:
                pdf_findings: List[Finding] = []
                for rule in PDF_RULES:
                    pdf_findings += rule(ctx)
                    rules_run += 1
                findings += pdf_findings
                if sub.mode == "both":
                    from .crosscheck import run_crosschecks
                    findings += run_crosschecks(ctx, source_findings, pdf_findings)
    finally:
        ctx.close()
    warnings += ctx.warnings
    apply_context(findings)

    return Report(
        tool_version=__version__,
        created=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        submission={"given": sub.given_as_typed or sub.given.name, "mode": sub.mode,
                    "pdf": sub.display(sub.pdf) if sub.pdf else "",
                    "main_tex": sub.display(sub.main_tex) if sub.main_tex else "",
                    "archive": sub.archive or ""},
        template={"url": status.url, "ref": status.ref, "commit": status.head.sha,
                  "commit_date": status.head.date, "source": status.source,
                  "catalogue_commit": generations.CATALOGUE_COMMIT},
        verdict=decide(findings, rules_run),
        findings=findings, facts=facts, warnings=warnings, notes=list(sub.notes))

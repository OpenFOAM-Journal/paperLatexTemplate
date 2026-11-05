"""Command-line interface: ofj-check [options] PATH"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from . import __version__
from .deps import check_dependencies, format_status, missing_required
from .inputs import ARCHIVE_SUFFIXES, InputError, detect_submission
from .model import EXIT_ENVIRONMENT, EXIT_INPUT
from .template_repo import (DEFAULT_MAX_AGE_HOURS, DEFAULT_REF, DEFAULT_URL, TemplateError,
                            default_cache_dir, obtain_template)

EPILOG = f"""\
PATH can be a PDF, a folder with LaTeX sources (with or without the PDF), a single
.tex file, or an archive ({', '.join(ARCHIVE_SUFFIXES)}).

exit codes:
  0  current template          1  outdated or modified template
  2  not the OFJ template      3  inconclusive
  {EXIT_ENVIRONMENT}  missing dependency or template not available
  {EXIT_INPUT}  input cannot be checked
"""


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="ofj-check", formatter_class=argparse.RawDescriptionHelpFormatter, epilog=EPILOG,
        description="Check whether an OpenFOAM Journal submission was prepared with the current "
                    "LaTeX template, and report what suggests otherwise.")
    p.add_argument("path", nargs="?", type=Path, help="submission to check")
    p.add_argument("--version", action="version", version=f"ofj-check {__version__}")
    p.add_argument("--check-deps", action="store_true",
                   help="only check that all required tools and packages are installed")

    g = p.add_argument_group("input")
    g.add_argument("--mode", choices=("auto", "pdf", "latex", "both"), default="auto",
                   help="what to check (default: auto-detect)")
    g.add_argument("--pdf", type=Path, help="the manuscript PDF, if a folder contains several PDFs")
    g.add_argument("--main-tex", type=Path, help="the main .tex file, if there are several")

    g = p.add_argument_group("output")
    g.add_argument("--report", type=Path, metavar="FILE.md", help="also write the report as Markdown")
    g.add_argument("--json", type=Path, metavar="FILE", help="also write the report as JSON ('-' = stdout)")
    g.add_argument("-q", "--quiet", action="store_true", help="print only the verdict line")

    g = p.add_argument_group("template")
    g.add_argument("--template-dir", type=Path,
                   help="use this local git clone of the template instead of the cached copy")
    g.add_argument("--template-url", default=DEFAULT_URL, help=f"(default: {DEFAULT_URL})")
    g.add_argument("--template-ref", default=DEFAULT_REF, help=f"branch to compare with (default: {DEFAULT_REF})")
    g.add_argument("--cache-dir", type=Path, help=f"where the template copy is kept (default: {default_cache_dir()})")
    g.add_argument("--offline", action="store_true", help="never contact GitHub; use the cached copy")
    g.add_argument("--update-template", action="store_true", help="update the cached copy now")
    g.add_argument("--max-age", type=float, default=DEFAULT_MAX_AGE_HOURS, metavar="HOURS",
                   help=f"update the cached copy when older than this (default: {DEFAULT_MAX_AGE_HOURS:g})")
    return p


def _console_safe() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="replace")


def _error(message: str) -> None:
    print(f"ofj-check: error: {message}", file=sys.stderr)


def main(argv: Optional[List[str]] = None) -> int:
    _console_safe()
    args = build_parser().parse_args(argv)

    if args.check_deps:
        statuses = check_dependencies(need_pdf=True)
        print(format_status(statuses))
        return EXIT_ENVIRONMENT if missing_required(statuses) else 0
    if args.path is None:
        build_parser().error("PATH is required (or use --check-deps)")

    try:
        sub = detect_submission(args.path, mode=args.mode, pdf=args.pdf, main_tex=args.main_tex)
    except InputError as exc:
        _error(str(exc))
        return EXIT_INPUT

    with sub:
        statuses = check_dependencies(need_pdf=sub.mode in ("pdf", "both"))
        if missing_required(statuses):
            _error("required dependencies are missing")
            print(format_status(statuses), file=sys.stderr)
            return EXIT_ENVIRONMENT
        try:
            repo, status = obtain_template(url=args.template_url, ref=args.template_ref,
                                           cache_dir=args.cache_dir, template_dir=args.template_dir,
                                           offline=args.offline, force_update=args.update_template,
                                           max_age_hours=args.max_age)
        except TemplateError as exc:
            _error(f"the current template is not available: {exc}")
            return EXIT_ENVIRONMENT

        from .analyze import run_checks
        from .report import render_json, render_markdown, render_text
        report = run_checks(sub, repo, status)

    if args.quiet:
        print(f"{report.verdict.kind}: {report.verdict.headline}")
    else:
        print(render_text(report), end="")
    if args.report:
        args.report.write_text(render_markdown(report), encoding="utf-8")
        if not args.quiet:
            print(f"Markdown report written to {args.report}")
    if args.json:
        if str(args.json) == "-":
            print(render_json(report), end="")
        else:
            args.json.write_text(render_json(report), encoding="utf-8")
    return report.verdict.exit_code

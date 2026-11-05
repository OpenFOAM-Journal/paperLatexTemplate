"""Work out what was submitted: a PDF, a LaTeX folder, or both (also inside an archive).

The submitted files are never modified. Archives are unpacked into a temporary
folder that is removed again when the check is finished.
"""
from __future__ import annotations

import re
import shutil
import tarfile
import tempfile
import zipfile
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import List, Optional

ARCHIVE_SUFFIXES = (".zip", ".tar", ".tar.gz", ".tgz", ".tar.bz2", ".tbz2", ".tar.xz", ".txz")
FIGURE_DIRS = {"figures", "figure", "figs", "fig", "images", "image", "img", "plots", "graphics", "pics"}
TEMPLATE_ASSET_PDFS = {"openfoamjournal.pdf"}     # the journal logo shipped with the template
SKIP_DIRS = {"__MACOSX", ".git", ".svn"}
MAX_MEMBERS = 5000
MAX_UNPACKED_BYTES = 1 << 30           # 1 GiB, protects against archive bombs
MODES = ("auto", "pdf", "latex", "both")

_COMMENT = re.compile(r"(?<!\\)%.*")
_DOCCLASS = re.compile(r"\\documentclass\s*(\[[^\]]*\])?\s*\{([^}]*)\}")


class InputError(Exception):
    """The given path cannot be checked."""


@dataclass
class Submission:
    given: Path
    mode: str                                   # pdf | latex | both
    given_as_typed: str = ""                    # for reports: no machine-specific absolute path
    root: Optional[Path] = None                 # folder holding the sources
    pdf: Optional[Path] = None
    main_tex: Optional[Path] = None
    tex_files: List[Path] = field(default_factory=list)
    other_pdfs: List[Path] = field(default_factory=list)
    archive: Optional[str] = None
    notes: List[str] = field(default_factory=list)
    _tmp: Optional[tempfile.TemporaryDirectory] = field(default=None, repr=False)

    def display(self, path: Optional[Path]) -> str:
        """Path as shown in reports: relative to the submission where possible."""
        if path is None:
            return "-"
        if Path(path) == self.given and self.given_as_typed:
            return self.given_as_typed
        if self.root is not None:
            try:
                return PurePosixPath(Path(path).relative_to(self.root)).as_posix()
            except ValueError:
                pass
        return str(path)

    def cleanup(self) -> None:
        if self._tmp is not None:
            self._tmp.cleanup()
            self._tmp = None

    def __enter__(self) -> "Submission":
        return self

    def __exit__(self, *exc) -> None:
        self.cleanup()


def strip_tex_comments(text: str) -> str:
    return "\n".join(_COMMENT.sub("", line) for line in text.splitlines())


def read_tex(path: Path) -> str:
    return Path(path).read_text(encoding="utf-8", errors="replace")


def document_class(path: Path) -> Optional[str]:
    """The \\documentclass of a .tex file, or None if it is not a main document."""
    text = strip_tex_comments(read_tex(path))
    match = _DOCCLASS.search(text)
    if match and "\\begin{document}" in text:
        return match.group(2).strip()
    return None


def is_archive(path: Path) -> bool:
    name = path.name.lower()
    return any(name.endswith(s) for s in ARCHIVE_SUFFIXES)


def _walk(root: Path, suffix: str) -> List[Path]:
    found = []
    for p in sorted(root.rglob(f"*{suffix}")):
        rel = p.relative_to(root).parts
        if p.is_file() and not any(part in SKIP_DIRS or part.startswith(".") for part in rel[:-1]):
            found.append(p)
    return found


def _safe_target(dest: Path, name: str) -> Optional[Path]:
    pure = PurePosixPath(name.replace("\\", "/"))
    if pure.is_absolute() or ".." in pure.parts or not pure.parts:
        return None
    target = (dest / Path(*pure.parts)).resolve()
    try:
        target.relative_to(dest.resolve())
    except ValueError:
        return None
    return target


def safe_extract(archive: Path, dest: Path) -> List[str]:
    """Unpack regular files only, refusing paths that would escape ``dest``. Returns notes."""
    notes, total, count = [], 0, 0

    def account(size: int) -> None:
        nonlocal total, count
        total += size
        count += 1
        if count > MAX_MEMBERS or total > MAX_UNPACKED_BYTES:
            raise InputError(f"{archive.name} is too large to unpack safely "
                             f"(limit {MAX_MEMBERS} files / {MAX_UNPACKED_BYTES >> 20} MiB)")

    if archive.name.lower().endswith(".zip"):
        try:
            zf = zipfile.ZipFile(archive)
        except zipfile.BadZipFile as exc:
            raise InputError(f"{archive.name} is not a valid zip file: {exc}") from exc
        with zf:
            for info in zf.infolist():
                if info.is_dir():
                    continue
                target = _safe_target(dest, info.filename)
                if target is None:
                    notes.append(f"Skipped unsafe archive entry: {info.filename}")
                    continue
                account(info.file_size)
                target.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(info) as src, open(target, "wb") as out:
                    shutil.copyfileobj(src, out)
        return notes

    try:
        tf = tarfile.open(archive)
    except tarfile.TarError as exc:
        raise InputError(f"{archive.name} is not a valid tar archive: {exc}") from exc
    with tf:
        for member in tf.getmembers():
            if member.isdir():
                continue
            if not member.isfile():
                notes.append(f"Skipped non-regular archive entry: {member.name}")
                continue
            target = _safe_target(dest, member.name)
            if target is None:
                notes.append(f"Skipped unsafe archive entry: {member.name}")
                continue
            account(member.size)
            target.parent.mkdir(parents=True, exist_ok=True)
            src = tf.extractfile(member)
            if src is None:
                continue
            with src, open(target, "wb") as out:
                shutil.copyfileobj(src, out)
    return notes


def find_main_tex(root: Path, tex_files: List[Path], notes: List[str]) -> Optional[Path]:
    candidates = []
    for path in tex_files:
        cls = document_class(path)
        if cls is not None:
            candidates.append((path, cls))
    if not candidates:
        return None

    def rank(item):
        path, cls = item
        return (cls != "ofj",                          # the OFJ class first
                "review" in path.stem.lower(),         # wrappers like *-review.tex last
                len(path.relative_to(root).parts),     # shallowest
                -path.stat().st_size)                  # largest
    candidates.sort(key=rank)
    chosen = candidates[0][0]
    if len(candidates) > 1:
        others = ", ".join(str(p.relative_to(root).as_posix()) for p, _ in candidates[1:])
        notes.append(f"Several main .tex files found; using {chosen.relative_to(root).as_posix()} "
                     f"(others: {others}). Use --main-tex to choose another one.")
    return chosen


def choose_pdf(root: Path, pdfs: List[Path], main_tex: Optional[Path], notes: List[str]) -> Optional[Path]:
    """Pick the manuscript PDF among all PDFs in the folder (figures are PDFs too)."""
    if not pdfs:
        return None
    main_stem = main_tex.stem.lower() if main_tex else None
    min_depth = min(len(p.relative_to(root).parts) for p in pdfs)

    def score(p: Path) -> int:
        rel = p.relative_to(root)
        s = 0
        if main_stem and p.stem.lower().startswith(main_stem):
            s += 4                                     # same jobname as the main .tex
        if "review" in p.stem.lower():
            s += 2                                     # submissions are review builds
        if any(part.lower() in FIGURE_DIRS for part in rel.parts[:-1]) \
                or p.name.lower() in TEMPLATE_ASSET_PDFS:
            s -= 5
        if len(rel.parts) == min_depth:
            s += 1
        return s

    ranked = sorted(pdfs, key=lambda p: (-score(p), -p.stat().st_size))
    best = ranked[0]
    if score(best) < 0:
        notes.append("Only figure PDFs or the journal logo were found in the folder; no "
                     "manuscript PDF. Use --pdf to name it.")
        return None
    if len(ranked) > 1 and score(ranked[1]) >= 0:
        notes.append(f"Several PDFs found; using {best.relative_to(root).as_posix()} as the "
                     "manuscript. Use --pdf to choose another one.")
    return best


def _resolve_option(value: Optional[Path], root: Optional[Path]) -> Optional[Path]:
    if value is None:
        return None
    p = Path(value)
    if p.exists():
        return p.resolve()
    if root is not None and (root / p).exists():
        return (root / p).resolve()
    raise InputError(f"{value} does not exist")


def detect_submission(path: Path, mode: str = "auto", pdf: Optional[Path] = None,
                      main_tex: Optional[Path] = None) -> Submission:
    if mode not in MODES:
        raise InputError(f"unknown mode '{mode}' (choose from {', '.join(MODES)})")
    path = Path(path)
    if not path.exists():
        raise InputError(f"{path} does not exist")
    as_typed = str(path)
    path = path.resolve()
    sub = Submission(given=path, given_as_typed=as_typed, mode="auto")

    if path.is_file():
        name = path.name.lower()
        if name.endswith(".pdf"):
            if mode in ("latex", "both"):
                raise InputError(f"mode '{mode}' needs LaTeX sources, but only a PDF was given")
            sub.mode, sub.pdf = "pdf", path
            return sub
        if is_archive(path):
            sub._tmp = tempfile.TemporaryDirectory(prefix="ofj-check-")
            sub.root = Path(sub._tmp.name).resolve()
            sub.archive = path.name
            try:
                sub.notes += safe_extract(path, sub.root)
            except Exception:
                sub.cleanup()
                raise
        elif name.endswith(".tex"):
            sub.root = path.parent
            main_tex = main_tex or path
        else:
            raise InputError(f"{path.name}: expected a PDF, a .tex file, a folder or an archive "
                             f"({', '.join(ARCHIVE_SUFFIXES)})")
    else:
        sub.root = path

    try:
        root = sub.root
        sub.tex_files = _walk(root, ".tex")
        sub.main_tex = _resolve_option(main_tex, root) or find_main_tex(root, sub.tex_files, sub.notes)
        all_pdfs = _walk(root, ".pdf")
        sub.pdf = _resolve_option(pdf, root) or choose_pdf(root, all_pdfs, sub.main_tex, sub.notes)
        sub.other_pdfs = [p for p in all_pdfs if p != sub.pdf]

        if mode == "auto":
            if sub.main_tex and sub.pdf:
                sub.mode = "both"
            elif sub.main_tex:
                sub.mode = "latex"
            elif sub.pdf:
                sub.mode = "pdf"
                sub.notes.append("No main .tex file (with \\documentclass and \\begin{document}) "
                                 "was found; only the PDF is checked.")
            else:
                raise InputError(f"{path.name}: found neither a main .tex file nor a manuscript PDF")
        else:
            if mode in ("pdf", "both") and not sub.pdf:
                raise InputError("no manuscript PDF found (use --pdf to name it)")
            if mode in ("latex", "both") and not sub.main_tex:
                raise InputError("no main .tex file found (use --main-tex to name it)")
            if mode == "latex":
                sub.pdf = None
            if mode == "pdf":
                sub.main_tex = None
            sub.mode = mode
    except Exception:
        sub.cleanup()
        raise
    return sub

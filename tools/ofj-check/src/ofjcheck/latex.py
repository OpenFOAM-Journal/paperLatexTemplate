"""Load a LaTeX document: follow \\input/\\include from the main file, and mask
comments and verbatim material so that rules only see what LaTeX typesets.

Masking keeps every line in place, so a match can always be reported as
``file:line``.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import List, Optional, Pattern, Union

VERBATIM_ENVS = ("verbatim", "verbatim*", "Verbatim", "lstlisting", "minted", "comment")
_BEGIN_VERB = re.compile(r"\\begin\{(" + "|".join(re.escape(e) for e in VERBATIM_ENVS) + r")\}")
_INLINE_VERB = re.compile(r"\\(?:verb\*?|lstinline)([^\w\s{])(.*?)\1")
_INPUT = re.compile(r"\\(input|include|subfile)\s*\{([^}]+)\}|\\(?:sub)?import\s*\{([^}]*)\}\s*\{([^}]+)\}")
_BEGIN_DOC = re.compile(r"\\begin\{document\}")


def strip_comment(line: str) -> str:
    """Remove a % comment, respecting \\% and \\\\%."""
    i = 0
    while i < len(line):
        c = line[i]
        if c == "\\":
            i += 2
            continue
        if c == "%":
            return line[:i]
        i += 1
    return line


def comment_of(line: str) -> str:
    """The comment part of a line (without the %), or ''."""
    code = strip_comment(line)
    return line[len(code) + 1:] if len(code) < len(line) else ""


def mask(text: str) -> str:
    """Comments removed, verbatim environment contents and inline verbatim blanked."""
    out: List[str] = []
    in_verb: Optional[str] = None
    for line in text.splitlines():
        if in_verb:
            end = f"\\end{{{in_verb}}}"
            pos = line.find(end)
            if pos < 0:
                out.append("")
                continue
            line = " " * pos + line[pos:]
            in_verb = None
        code = strip_comment(line)
        code = _INLINE_VERB.sub(lambda m: " " * len(m.group(0)), code)
        m = _BEGIN_VERB.search(code)
        if m and f"\\end{{{m.group(1)}}}" not in code[m.end():]:
            in_verb = m.group(1)
            code = code[:m.end()] + _keep_options(code[m.end():])
        out.append(code)
    return "\n".join(out)


def _keep_options(rest: str) -> str:
    """Keep an optional [..] argument after \\begin{lstlisting} (caption, label)."""
    stripped = rest.lstrip()
    if stripped.startswith("["):
        end = stripped.find("]")
        if end > 0:
            return rest[:len(rest) - len(stripped) + end + 1]
    return ""


@dataclass
class SourceFile:
    path: Path
    rel: str                     # path relative to the submission root, POSIX style
    raw: str
    masked: str
    in_preamble: bool = False    # included before \begin{document}

    @property
    def raw_lines(self) -> List[str]:
        return self.raw.splitlines()


@dataclass
class Hit:
    file: SourceFile
    line: int                    # 1-based
    text: str                    # the matched text
    line_text: str               # the whole (raw) line, stripped

    @property
    def location(self) -> str:
        return f"{self.file.rel}:{self.line}"


@dataclass
class Document:
    root: Path
    main: SourceFile
    files: List[SourceFile] = field(default_factory=list)   # main first, in input order
    begin_document_offset: int = -1                          # in main.masked
    missing_inputs: List[str] = field(default_factory=list)

    @property
    def preamble(self) -> str:
        end = self.begin_document_offset if self.begin_document_offset >= 0 else len(self.main.masked)
        return self.main.masked[:end]

    def search(self, pattern: Union[str, Pattern], scope: str = "all", raw: bool = False,
               flags: int = 0) -> List[Hit]:
        """Find a regex. scope: all | preamble | body. raw=True also searches comments."""
        rx = re.compile(pattern, flags) if isinstance(pattern, str) else pattern
        hits = []
        for f in self.files:
            text = f.raw if raw else f.masked
            if f is self.main and scope != "all" and self.begin_document_offset >= 0:
                cut = self.begin_document_offset
                lo, hi = (0, cut) if scope == "preamble" else (cut, len(text))
            elif scope == "all" or (scope == "preamble") == f.in_preamble:
                lo, hi = 0, len(text)
            else:
                continue
            raw_lines = f.raw_lines
            for m in rx.finditer(text, lo, hi):
                line = text.count("\n", 0, m.start()) + 1
                line_text = raw_lines[line - 1].strip() if line <= len(raw_lines) else ""
                hits.append(Hit(f, line, m.group(0), line_text))
        return hits


def _relative(root: Path, path: Path) -> str:
    try:
        return PurePosixPath(path.resolve().relative_to(root.resolve())).as_posix()
    except ValueError:
        return path.name


def _resolve_input(name: str, base: Path, root: Path) -> Optional[Path]:
    name = name.strip()
    for directory in (base, root):
        for candidate in (directory / name, directory / f"{name}.tex"):
            if candidate.is_file():
                return candidate
    return None


def load_document(main_tex: Path, root: Optional[Path] = None) -> Document:
    main_tex = Path(main_tex)
    root = Path(root) if root else main_tex.parent
    base = main_tex.parent                  # LaTeX resolves \input relative to the main file

    def load(path: Path, in_preamble: bool) -> SourceFile:
        raw = path.read_text(encoding="utf-8", errors="replace")
        return SourceFile(path=path, rel=_relative(root, path), raw=raw, masked=mask(raw),
                          in_preamble=in_preamble)

    main = load(main_tex, False)
    m = _BEGIN_DOC.search(main.masked)
    doc = Document(root=root, main=main, files=[main], begin_document_offset=m.start() if m else -1)
    seen = {main_tex.resolve()}

    def walk(f: SourceFile, depth: int) -> None:
        if depth > 20:
            return
        for match in _INPUT.finditer(f.masked):
            if match.group(2) is not None:
                name, sub_base = match.group(2), base
            else:
                name, sub_base = match.group(4), f.path.parent / match.group(3)
            target = _resolve_input(name, sub_base, root)
            if target is None:
                doc.missing_inputs.append(f"{f.rel}: {match.group(0)}")
                continue
            if target.resolve() in seen:
                continue
            seen.add(target.resolve())
            in_pre = f.in_preamble or (f is main and 0 <= match.start() and
                                       (doc.begin_document_offset < 0 or
                                        match.start() < doc.begin_document_offset))
            child = load(target, in_pre)
            doc.files.append(child)
            walk(child, depth + 1)

    walk(main, 0)
    return doc

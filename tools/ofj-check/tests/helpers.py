"""Test helpers: tiny PDFs and git repositories built on the fly (no TeX needed)."""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Dict, Optional

A4 = (595.28, 841.89)


def write_minimal_pdf(path: Path, size=A4, producer: str = "pdfTeX-1.40.25",
                      lines=(), creator: str = "LaTeX with hyperref", info: str = "") -> Path:
    """A valid one-page PDF with optional lines of Helvetica text and metadata."""
    w, h = size
    ops = []
    for n, line in enumerate(lines):
        safe = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        ops.append(f"BT /F1 11 Tf 72 {h - 80 - 14 * n:.1f} Td ({safe}) Tj ET")
    stream = "\n".join(ops)
    objects = [
        "<< /Type /Catalog /Pages 2 0 R >>",
        "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {w} {h}] /Contents 4 0 R "
        "/Resources << /Font << /F1 6 0 R >> >> >>",
        f"<< /Length {len(stream)} >>\nstream\n{stream}\nendstream",
        f"<< /Producer ({producer}) /Creator ({creator}) {info} >>",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = bytearray(b"%PDF-1.5\n")
    offsets = []
    for i, body in enumerate(objects, 1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n{body}\nendobj\n".encode("latin-1")
    xref = len(out)
    out += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode()
    for off in offsets:
        out += f"{off:010d} 00000 n \n".encode()
    out += (f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R /Info 5 0 R >>\n"
            f"startxref\n{xref}\n%%EOF\n").encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(bytes(out))
    return path


def write_files(root: Path, files: Dict[str, str]) -> None:
    """Write files byte-exactly (no newline translation, so tests behave alike on all systems)."""
    for rel, content in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8", newline="") as fh:
            fh.write(content)


def git(repo: Path, *args: str) -> str:
    cmd = ["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
           "-c", "init.defaultBranch=master", "-c", "commit.gpgsign=false", "-C", str(repo), *args]
    return subprocess.run(cmd, check=True, capture_output=True, text=True).stdout.strip()


def commit(repo: Path, files: Dict[str, str], message: str, date: Optional[str] = None) -> str:
    write_files(repo, files)
    git(repo, "add", "-A")
    env_date = ["--date", date] if date else []
    git(repo, "commit", "-q", "-m", message, *env_date)
    return git(repo, "rev-parse", "HEAD")


def init_repo(repo: Path) -> Path:
    repo.mkdir(parents=True, exist_ok=True)
    git(repo, "init", "-q")
    return repo


def find_template_repo() -> Optional[str]:
    """A clone of the real OFJ template that contains the catalogue commit, if available:
    $OFJ_TEMPLATE_REPO, the template repository this tool is part of, or ofj-check's cache."""
    import os
    import shutil
    from ofjcheck import generations
    from ofjcheck.template_repo import CLONE_NAME, default_cache_dir
    if not shutil.which("git"):
        return None
    enclosing = next((p for p in Path(__file__).resolve().parents if (p / ".git").is_dir()), None)
    for c in (os.environ.get("OFJ_TEMPLATE_REPO"),
              str(enclosing) if enclosing else None,
              str(default_cache_dir() / CLONE_NAME)):
        if not c or not Path(c).exists():
            continue
        git_dir = Path(c) / ".git" if (Path(c) / ".git").exists() else Path(c)
        ok = subprocess.run(["git", f"--git-dir={git_dir}", "cat-file", "-e", generations.CATALOGUE_COMMIT],
                            capture_output=True).returncode == 0
        if ok:
            return c
    return None


REFERENCE_PDFS = Path(__file__).resolve().parents[1] / "research" / "reference_pdfs"
NEGATIVE_PDFS = Path(__file__).resolve().parents[1] / "research" / "negative_samples"


MAIN_TEX = r"""\documentclass[e-only,10pt,reqno]{ofj}
\begin{document}
Hello.
\end{document}
"""

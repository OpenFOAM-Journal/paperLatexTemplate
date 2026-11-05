"""Exact matching of submitted files against every version of every template file.

The index is built from the template's git history in three git calls:
the first-parent log of master (which versions were on master, and when),
the list of all objects (versions that only existed on branches), and one
batch read of the file contents.
"""
from __future__ import annotations

import difflib
import hashlib
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from . import generations
from .template_repo import TemplateRepo, _git_env

SKIP_SUFFIXES = (".pdf", ".log", ".bbl", ".png", ".jpg", ".aux")
SKIP_PATHS = ("README.md", ".github/", ".gitignore", "LICENSE", "tools/")
# Files the authors must not change; any difference is reported as a modification.
PROTECTED = ("ofj.cls", "ofjart.cls", "amsart.cls", "jams-l.cls", "orcidlink.sty",
             "tensorNotation.sty", "finiteVolumeNotation.sty")
# Files whose differences are expected (authors fill them in); only exact matches count.
_MAKEFILE_SETTING = re.compile(r"^\s*#?\s*(DOCUMENT|TYPE)\s*=")
# Lines of ofjart.cls that the editor fills in for publication ("%JN: change ...").
_EDITORIAL = re.compile(r"\\issueinfo\s*\{|\\pagespan\s*\{|\\datename\s*\}?\s*\{|\\PII\s*\{|"
                        r"%\s*(issue number|month|year)\s*$")


def normalise(data: bytes, name: str = "", editorial: bool = False) -> str:
    """Hash that ignores line endings, trailing whitespace and trailing blank lines.
    In the Makefile the DOCUMENT/TYPE settings, which authors are told to change, are ignored;
    with ``editorial`` the publication data of ofjart.cls (volume, pages, dates) too."""
    text = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n").decode("utf-8", errors="replace")
    lines = [ln.rstrip() for ln in text.split("\n")]
    if name == "Makefile":
        lines = [ln for ln in lines if not _MAKEFILE_SETTING.match(ln)]
    if editorial:
        lines = [ln for ln in lines if not _EDITORIAL.search(ln)]
    while lines and not lines[-1]:
        lines.pop()
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


@dataclass
class FileVersion:
    path: str                   # path in the template repository
    blob: str
    start: Optional[str]        # date it landed on master (None = branch only)
    until: Optional[str] = None  # date it was replaced/removed on master (None = still current)
    start_idx: int = -1         # position in the first-parent history of master
    until_idx: Optional[int] = None
    norm: str = ""
    norm_editorial: str = ""    # same, without the editor's publication data
    text: str = ""

    @property
    def on_master(self) -> bool:
        return self.start is not None

    def period(self) -> str:
        if not self.on_master:
            return "never on master (development branch only)"
        return f"on master from {self.start}" + (f" until {self.until}" if self.until else ", still current")


@dataclass
class FileMatch:
    submitted: str                       # path relative to the submission
    template_path: str
    versions: List[FileVersion]          # all template versions with identical content
    range_from: Optional[str] = None
    range_to: Optional[str] = None
    on_master: bool = True
    production: bool = False             # identical except for the editor's publication data


@dataclass
class FileMismatch:
    submitted: str
    template_path: str
    nearest: FileVersion
    similarity: float
    added: int
    removed: int
    excerpt: List[str] = field(default_factory=list)


def _cat_blobs(repo: TemplateRepo, shas: Iterable[str]) -> Dict[str, Tuple[str, bytes]]:
    shas = list(dict.fromkeys(shas))
    if not shas:
        return {}
    proc = subprocess.run(["git", f"--git-dir={repo.git_dir}", "cat-file", "--batch"],
                          input=("\n".join(shas) + "\n").encode(), capture_output=True,
                          env=_git_env(), check=True)
    out, pos, result = proc.stdout, 0, {}
    for sha in shas:
        nl = out.index(b"\n", pos)
        header = out[pos:nl].decode().split()
        pos = nl + 1
        if len(header) < 3 or header[1] == "missing":
            continue
        size = int(header[2])
        result[sha] = (header[1], out[pos:pos + size])
        pos += size + 1
    return result


def _tracked(path: str) -> bool:
    return not path.endswith(SKIP_SUFFIXES) and not path.startswith(SKIP_PATHS)


class TemplateIndex:
    def __init__(self, versions: Dict[str, List[FileVersion]], commit_gens: List[str]):
        self.versions = versions
        self.commit_gens = commit_gens          # generation of each first-parent commit
        self.by_name: Dict[str, List[str]] = {}
        for path in versions:
            self.by_name.setdefault(Path(path).name, []).append(path)

    def generation_range(self, v: FileVersion) -> Tuple[str, Optional[str]]:
        """Generations whose master history contained this version (last None = up to now)."""
        first = self.commit_gens[v.start_idx]
        if v.until_idx is None:
            return first, None
        return first, self.commit_gens[max(v.until_idx - 1, v.start_idx)]

    @classmethod
    def build(cls, repo: TemplateRepo, ref: str) -> "TemplateIndex":
        log = repo.git("log", "--first-parent", "--reverse", "-m", "--raw", "--no-abbrev",
                       "--no-renames", "--root", "--date=short", "--format=@%H %ad", ref)
        versions: Dict[str, List[FileVersion]] = {}
        commits: List[Tuple[str, str]] = []
        day = ""
        for line in log.splitlines():
            if line.startswith("@"):
                sha, day = line[1:].split()[:2]
                commits.append((sha, day))
            elif line.startswith(":"):
                meta, path = line.split("\t", 1)
                _, _, _, new_sha, status = meta.split()[:5]
                if not _tracked(path):
                    continue
                idx = len(commits) - 1
                hist = versions.setdefault(path, [])
                if hist and hist[-1].until is None:
                    hist[-1].until, hist[-1].until_idx = day, idx
                if not status.startswith("D"):
                    hist.append(FileVersion(path, new_sha, day, start_idx=idx))

        known = {v.blob for hist in versions.values() for v in hist}
        names = {Path(p).name: p for p in versions}
        branch_only: List[Tuple[str, str]] = []
        for line in repo.git("rev-list", "--objects", "--all").splitlines():
            parts = line.split(" ", 1)
            if len(parts) == 2 and parts[0] not in known and Path(parts[1]).name in names \
                    and _tracked(parts[1]):
                branch_only.append((parts[1], parts[0]))
                known.add(parts[0])

        contents = _cat_blobs(repo, [v.blob for h in versions.values() for v in h] +
                              [sha for _, sha in branch_only])
        for path, sha in branch_only:
            kind, _ = contents.get(sha, ("missing", b""))
            if kind == "blob":
                versions.setdefault(path, []).append(FileVersion(path, sha, None))
        for path, hist in versions.items():
            for v in hist:
                data = contents.get(v.blob, ("", b""))[1]
                v.norm = normalise(data, Path(path).name)
                v.norm_editorial = normalise(data, Path(path).name, editorial=True)
                v.text = data.decode("utf-8", errors="replace")
        return cls(versions, generations.commit_generations(commits))

    def candidates(self, name: str) -> List[str]:
        return self.by_name.get(name, [])

    def match(self, data: bytes, name: str, submitted: str) -> Tuple[Optional[FileMatch], Optional[FileMismatch]]:
        """Compare a submitted file with all template files of the same name."""
        paths = self.candidates(name)
        if not paths:
            return None, None
        norm = normalise(data, name)
        norm_ed = normalise(data, name, editorial=True)
        for path in paths:
            same = [v for v in self.versions[path] if v.norm == norm]
            production = False
            if not same and name == "ofjart.cls":
                same = [v for v in self.versions[path] if v.norm_editorial == norm_ed]
                production = bool(same)
            if same:
                on_master = [v for v in same if v.on_master]
                fm = FileMatch(submitted, path, same, on_master=bool(on_master), production=production)
                if on_master:
                    ranges = [self.generation_range(v) for v in on_master]
                    fm.range_from = min((r[0] for r in ranges), key=generations.index)
                    fm.range_to = None if any(r[1] is None for r in ranges) else \
                        max((r[1] for r in ranges), key=generations.index)
                return fm, None
        if name not in PROTECTED:
            return None, None
        return None, self._nearest(data, name, submitted, paths)

    def _nearest(self, data: bytes, name: str, submitted: str, paths: List[str]) -> FileMismatch:
        keep = (lambda ln: not _EDITORIAL.search(ln)) if name == "ofjart.cls" else (lambda ln: True)
        mine = [ln for ln in data.decode("utf-8", errors="replace").replace("\r\n", "\n").splitlines()
                if keep(ln)]
        best, best_ratio = None, -1.0
        for path in paths:
            for v in self.versions[path]:
                theirs = [ln for ln in v.text.splitlines() if keep(ln)]
                sm = difflib.SequenceMatcher(None, theirs, mine, autojunk=False)
                if sm.real_quick_ratio() < best_ratio or sm.quick_ratio() < best_ratio:
                    continue
                ratio = sm.ratio()
                if ratio > best_ratio or (ratio == best_ratio and v.on_master and v.until is None):
                    best, best_ratio = v, ratio
        diff = [d for d in difflib.unified_diff([ln for ln in best.text.splitlines() if keep(ln)], mine,
                                                lineterm="", n=0)
                if not d.startswith(("---", "+++", "@@"))]
        added = sum(1 for d in diff if d.startswith("+"))
        removed = sum(1 for d in diff if d.startswith("-"))
        return FileMismatch(submitted, best.path, best, best_ratio, added, removed,
                            [d[:160] for d in diff[:8]])


_PLACEHOLDER_ISSUES = ("2 [Enter correct Journal Section here]", "123", "00")


def production_data(text: str) -> Dict[str, str]:
    """Publication data the editor filled into ofjart.cls (empty if only placeholders)."""
    data = {}
    m = re.search(r"\\issueinfo\s*\{([^}]*)\}", text)
    if m and m.group(1).strip() not in _PLACEHOLDER_ISSUES:
        data["volume"] = m.group(1).strip()
    m = re.search(r"\\pagespan\s*\{([^}]*)\}\s*\{([^}]*)\}", text)
    if m and (m.group(1), m.group(2)) not in (("1", "999"), ("000", "000")):
        data["pages"] = f"{m.group(1)}-{m.group(2)}"
    for m in re.finditer(r"\\newcommand\s*\{\\datename\}\s*\{(.*)\}", text):   # defined twice
        if "Received:" in m.group(1) and "Juntember" not in m.group(1):
            dates = re.findall(r"(Received|Accepted|Published):\s*([^,}%]+)", m.group(1))
            data.update({k.lower(): v.strip() for k, v in dates})
    return data


def scan_submission(index: TemplateIndex, root: Path,
                    files: Optional[Iterable[Path]] = None) -> Tuple[List[FileMatch], List[FileMismatch]]:
    """Match every file in the submission whose name is a template file name."""
    matches, mismatches = [], []
    paths = files if files is not None else sorted(p for p in Path(root).rglob("*") if p.is_file())
    for p in paths:
        if not index.candidates(p.name):
            continue
        rel = p.relative_to(root).as_posix()
        if any(part.startswith(".") or part == "__MACOSX" for part in Path(rel).parts[:-1]):
            continue
        m, mm = index.match(p.read_bytes(), p.name, rel)
        if m:
            matches.append(m)
        if mm:
            mismatches.append(mm)
    return matches, mismatches

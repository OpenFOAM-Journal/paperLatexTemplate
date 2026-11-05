"""Access to the official template repository: fetch it, keep it fresh, read its history.

The template is kept as a bare git clone in a cache directory, so that every
historical version of every file can be read without checking anything out.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

DEFAULT_URL = "https://github.com/OpenFOAM-Journal/paperLatexTemplate.git"
DEFAULT_REF = "master"
DEFAULT_MAX_AGE_HOURS = 12.0
CLONE_NAME = "paperLatexTemplate.git"
FETCH_STAMP = "ofj-check-last-fetch"
NETWORK_TIMEOUT = 180

# Commits touching only these paths do not change the template itself
# (tools/ holds editor tools such as ofj-check, not part of what authors use).
NON_TEMPLATE_PATHS = ("README.md", ".github/", ".gitignore", "LICENSE", "tools/")


class TemplateError(Exception):
    """The template could not be obtained or read."""


@dataclass
class CommitInfo:
    sha: str
    short: str
    date: str
    subject: str

    def __str__(self) -> str:
        return f"{self.short} ({self.date}) {self.subject}"


@dataclass
class TemplateStatus:
    url: str
    ref: str
    path: Path
    head: CommitInfo
    source: str                       # cloned | updated | cache | cache-stale | local
    last_fetch: Optional[datetime]
    warnings: List[str] = field(default_factory=list)


def default_cache_dir() -> Path:
    if os.environ.get("OFJ_CHECK_CACHE"):
        return Path(os.environ["OFJ_CHECK_CACHE"])
    base = os.environ.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")
    return Path(base) / "ofj-template-check"


def _git_env() -> dict:
    env = dict(os.environ)
    env["GIT_TERMINAL_PROMPT"] = "0"      # never hang on a credential prompt
    return env


def run_git(args: Sequence[str], cwd: Optional[Path] = None, timeout: Optional[float] = None) -> str:
    cmd = ["git"] + ([f"--git-dir={cwd}"] if cwd else []) + list(args)
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, env=_git_env(),
                              timeout=timeout, encoding="utf-8", errors="replace")
    except FileNotFoundError as exc:
        raise TemplateError("git is not installed (run 'ofj-check --check-deps')") from exc
    except subprocess.TimeoutExpired as exc:
        raise TemplateError(f"git {args[0]} timed out after {timeout:.0f} s") from exc
    if proc.returncode != 0:
        msg = (proc.stderr or proc.stdout).strip().splitlines()
        raise TemplateError(f"git {' '.join(args[:2])} failed: {msg[-1] if msg else proc.returncode}")
    return proc.stdout


class TemplateRepo:
    """Read-only view of a template repository (bare clone or the .git of a work tree)."""

    def __init__(self, git_dir: Path):
        self.git_dir = Path(git_dir)

    def git(self, *args: str, timeout: Optional[float] = None) -> str:
        return run_git(args, cwd=self.git_dir, timeout=timeout)

    def resolve(self, ref: str) -> str:
        return self.git("rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}").strip()

    def commit_info(self, rev: str) -> CommitInfo:
        out = self.git("log", "-1", "--date=short", "--format=%H%x00%h%x00%ad%x00%s", rev)
        sha, short, date, subject = out.rstrip("\n").split("\x00", 3)
        return CommitInfo(sha, short, date, subject)

    def first_parent_log(self, rev_range: str) -> List[CommitInfo]:
        out = self.git("log", "--first-parent", "--date=short",
                       "--format=%H%x00%h%x00%ad%x00%s", rev_range)
        return [CommitInfo(*line.split("\x00", 3)) for line in out.splitlines() if line]

    def is_ancestor(self, ancestor: str, descendant: str) -> bool:
        try:
            self.git("merge-base", "--is-ancestor", ancestor, descendant)
            return True
        except TemplateError:
            return False

    def changed_paths(self, sha: str) -> List[str]:
        """Paths changed by a commit relative to its first parent."""
        return [p for p in self.git("diff", "--name-only", f"{sha}^1", sha).splitlines() if p]

    def read_file(self, rev: str, path: str) -> bytes:
        cmd = ["git", f"--git-dir={self.git_dir}", "show", f"{rev}:{path}"]
        proc = subprocess.run(cmd, capture_output=True, env=_git_env())
        if proc.returncode != 0:
            raise TemplateError(f"{path} not found at {rev}")
        return proc.stdout


def _read_stamp(git_dir: Path) -> Optional[datetime]:
    try:
        return datetime.fromisoformat((git_dir / FETCH_STAMP).read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None


def _write_stamp(git_dir: Path, when: datetime) -> None:
    (git_dir / FETCH_STAMP).write_text(when.isoformat(), encoding="utf-8")


def _age_text(then: Optional[datetime], now: datetime) -> str:
    if then is None:
        return "of unknown age"
    hours = (now - then).total_seconds() / 3600
    return f"{hours:.0f} hours old" if hours < 48 else f"{hours / 24:.0f} days old"


def _local_git_dir(template_dir: Path) -> Path:
    try:
        out = run_git(["-C", str(template_dir), "rev-parse", "--absolute-git-dir"])
    except TemplateError as exc:
        raise TemplateError(f"{template_dir} is not a git clone of the template: {exc}") from exc
    return Path(out.strip())


def _resolve_ref(repo: TemplateRepo, ref: str) -> str:
    for candidate in (ref, f"origin/{ref}", f"refs/remotes/origin/{ref}"):
        try:
            return repo.resolve(candidate)
        except TemplateError:
            continue
    raise TemplateError(f"branch or commit '{ref}' not found in the template repository")


def obtain_template(url: str = DEFAULT_URL, ref: str = DEFAULT_REF, cache_dir: Optional[Path] = None,
                    template_dir: Optional[Path] = None, offline: bool = False,
                    force_update: bool = False, max_age_hours: float = DEFAULT_MAX_AGE_HOURS,
                    now: Optional[datetime] = None) -> Tuple[TemplateRepo, TemplateStatus]:
    """Return the template repository, cloning or updating the cached copy as needed."""
    now = now or datetime.now(timezone.utc)
    warnings: List[str] = []

    if template_dir is not None:
        repo = TemplateRepo(_local_git_dir(Path(template_dir)))
        head = repo.commit_info(_resolve_ref(repo, ref))
        warnings.append(f"Using the local template copy in {template_dir}; it is not updated "
                        "automatically (run 'git pull' there to bring it up to date).")
        return repo, TemplateStatus(url=str(template_dir), ref=ref, path=repo.git_dir, head=head,
                                    source="local", last_fetch=None, warnings=warnings)

    cache_dir = Path(cache_dir) if cache_dir else default_cache_dir()
    git_dir = cache_dir / CLONE_NAME
    if not (git_dir / "HEAD").exists():
        if offline:
            raise TemplateError(f"no cached copy of the template in {cache_dir}; run once without "
                                "--offline to download it")
        cache_dir.mkdir(parents=True, exist_ok=True)
        partial = cache_dir / (CLONE_NAME + ".partial")
        if partial.exists():
            shutil.rmtree(partial)        # leftover of our own interrupted clone
        run_git(["clone", "--bare", "--quiet", url, str(partial)], timeout=NETWORK_TIMEOUT)
        partial.rename(git_dir)
        _write_stamp(git_dir, now)
        source, last_fetch = "cloned", now
    else:
        last_fetch = _read_stamp(git_dir)
        stale = last_fetch is None or (now - last_fetch).total_seconds() > max_age_hours * 3600
        source = "cache"
        if offline:
            if stale:
                warnings.append(f"Offline mode: the template copy is {_age_text(last_fetch, now)}; "
                                "newer template changes would not be known.")
        elif force_update or stale:
            try:
                run_git(["fetch", "--quiet", "--prune", "origin", "+refs/heads/*:refs/heads/*"],
                        cwd=git_dir, timeout=NETWORK_TIMEOUT)
                _write_stamp(git_dir, now)
                source, last_fetch = "updated", now
            except TemplateError as exc:
                source = "cache-stale"
                warnings.append(f"Could not update the template ({exc}); using the cached copy, "
                                f"which is {_age_text(last_fetch, now)}.")

    repo = TemplateRepo(git_dir)
    head = repo.commit_info(_resolve_ref(repo, ref))
    return repo, TemplateStatus(url=url, ref=ref, path=git_dir, head=head, source=source,
                                last_fetch=last_fetch, warnings=warnings)


def template_changes_since(repo: TemplateRepo, known_sha: str, head_sha: str) -> List[CommitInfo]:
    """First-parent commits after ``known_sha`` that change the template itself."""
    changes = []
    for commit in repo.first_parent_log(f"{known_sha}..{head_sha}"):
        paths = repo.changed_paths(commit.sha)
        if any(not p.startswith(NON_TEMPLATE_PATHS) for p in paths):
            changes.append(commit)
    return changes


def catalogue_coverage_warnings(repo: TemplateRepo, catalogue_sha: str, head: CommitInfo) -> List[str]:
    """Warn when the template has moved on since the fingerprint catalogue was written."""
    try:
        repo.resolve(catalogue_sha)
    except TemplateError:
        return [f"The fingerprint catalogue refers to template commit {catalogue_sha[:7]}, which is "
                "not in this template repository; results may be unreliable."]
    if not repo.is_ancestor(catalogue_sha, head.sha):
        return [f"The template at {head.short} does not contain catalogue commit {catalogue_sha[:7]}; "
                "the template history was rewritten or a different branch is checked."]
    newer = template_changes_since(repo, catalogue_sha, head.sha)
    if not newer:
        return []
    listing = "; ".join(str(c) for c in newer[:5]) + (" ..." if len(newer) > 5 else "")
    return [f"The template has {len(newer)} change(s) newer than the fingerprint catalogue "
            f"(catalogue covers up to {catalogue_sha[:7]}): {listing}. A paper using the newest "
            "template may be reported as current although these changes are not checked. "
            "Please update the catalogue (docs/FINGERPRINTS.md and src/ofjcheck/generations.py)."]

"""Environment check: is everything ofj-check needs installed, and if not, how to get it."""
from __future__ import annotations

import importlib.util
import platform
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

MIN_PYTHON = (3, 9)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
REQUIREMENTS = PROJECT_ROOT / "requirements.txt"


@dataclass
class DepStatus:
    name: str
    required: bool
    needed_for: str
    ok: bool
    detail: str
    hint: List[str] = field(default_factory=list)


@dataclass
class PlatformInfo:
    system: str                      # "Linux", "Windows", "Darwin"
    distro_id: str = ""              # "ubuntu", "debian", "fedora", ...
    distro_like: str = ""
    wsl: bool = False

    @property
    def label(self) -> str:
        name = self.distro_id or self.system
        return f"{name} (WSL)" if self.wsl else name


def parse_os_release(text: str) -> Dict[str, str]:
    values = {}
    for line in text.splitlines():
        if "=" in line and not line.startswith("#"):
            key, _, value = line.partition("=")
            values[key.strip()] = value.strip().strip('"')
    return values


def detect_platform(os_release: Optional[str] = None, proc_version: Optional[str] = None) -> PlatformInfo:
    system = platform.system()
    info = PlatformInfo(system=system)
    if system != "Linux" and os_release is None:
        return info
    if os_release is None:
        try:
            os_release = Path("/etc/os-release").read_text(encoding="utf-8", errors="replace")
        except OSError:
            os_release = ""
    if proc_version is None:
        try:
            proc_version = Path("/proc/version").read_text(encoding="utf-8", errors="replace")
        except OSError:
            proc_version = ""
    values = parse_os_release(os_release)
    info.system = "Linux"
    info.distro_id = values.get("ID", "").lower()
    info.distro_like = values.get("ID_LIKE", "").lower()
    info.wsl = "microsoft" in proc_version.lower()
    return info


def system_install_command(plat: PlatformInfo, packages: Dict[str, str]) -> str:
    """Install command for the platform; ``packages`` maps package manager -> package names."""
    family = f"{plat.distro_id} {plat.distro_like}"
    for manager, keys in (("apt", ("debian", "ubuntu")), ("dnf", ("fedora", "rhel", "centos")),
                          ("pacman", ("arch",)), ("zypper", ("suse",))):
        if any(k in family for k in keys) and manager in packages:
            prefix = {"apt": "sudo apt install", "dnf": "sudo dnf install",
                      "pacman": "sudo pacman -S", "zypper": "sudo zypper install"}[manager]
            return f"{prefix} {packages[manager]}"
    return f"install {packages.get('generic', packages.get('apt', ''))} with your system's package manager"


def in_virtualenv() -> bool:
    return sys.prefix != getattr(sys, "base_prefix", sys.prefix)


def python_package_hint(plat: PlatformInfo, venv_available: bool) -> List[str]:
    req = REQUIREMENTS if REQUIREMENTS.exists() else Path("requirements.txt")
    if in_virtualenv():
        return [f"{sys.executable} -m pip install -r {req}"]
    venv_dir = PROJECT_ROOT / ".venv"
    steps = []
    if not venv_available:
        steps.append(system_install_command(plat, {"apt": "python3-venv python3-pip",
                                                   "dnf": "python3-pip",
                                                   "pacman": "python-pip",
                                                   "zypper": "python3-pip",
                                                   "generic": "the Python venv and pip modules"}))
    steps += [f"python3 -m venv {venv_dir}",
              f"{venv_dir}/bin/pip install -r {req}",
              "then run ./ofj-check again (it uses .venv automatically)"]
    return steps


def _module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def _module_version(dist: str) -> str:
    try:
        from importlib.metadata import version
        return version(dist)
    except Exception:  # noqa: BLE001 - version is informational only
        return "unknown version"


def venv_works() -> bool:
    """``python -m venv`` needs ensurepip, which Debian/Ubuntu ship separately."""
    return _module_available("venv") and _module_available("ensurepip")


def check_dependencies(need_pdf: bool = True, plat: Optional[PlatformInfo] = None) -> List[DepStatus]:
    plat = plat or detect_platform()
    result = []

    py_ok = sys.version_info[:2] >= MIN_PYTHON
    result.append(DepStatus(
        name="Python", required=True, needed_for="running ofj-check", ok=py_ok,
        detail=f"{platform.python_version()} at {sys.executable}",
        hint=[] if py_ok else [f"Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]} or newer is required: "
                               + system_install_command(plat, {"apt": "python3", "generic": "python3"})]))

    git = shutil.which("git")
    git_detail = "not found"
    if git:
        try:
            git_detail = subprocess.run([git, "--version"], capture_output=True, text=True,
                                        check=True).stdout.strip()
        except (OSError, subprocess.CalledProcessError) as exc:
            git, git_detail = None, f"found but not working: {exc}"
    result.append(DepStatus(
        name="git", required=True, needed_for="fetching the current template and its history",
        ok=git is not None, detail=git_detail,
        hint=[] if git else [system_install_command(plat, {"apt": "git", "dnf": "git", "pacman": "git",
                                                          "zypper": "git", "generic": "git"})]))

    has_pdf = _module_available("pdfplumber")
    result.append(DepStatus(
        name="pdfplumber (Python package)", required=need_pdf, needed_for="reading the submitted PDF",
        ok=has_pdf, detail=_module_version("pdfplumber") if has_pdf else "not installed",
        hint=[] if has_pdf else python_package_hint(plat, venv_works())))
    return result


def missing_required(statuses: List[DepStatus]) -> List[DepStatus]:
    return [s for s in statuses if s.required and not s.ok]


def format_status(statuses: List[DepStatus], plat: Optional[PlatformInfo] = None) -> str:
    plat = plat or detect_platform()
    lines = [f"Environment: {plat.label}, Python {platform.python_version()}"]
    if plat.system != "Linux":
        lines.append("  Note: ofj-check is supported on Linux and WSL; other systems may work but are untested.")
    for s in statuses:
        mark = "OK " if s.ok else ("MISSING" if s.required else "optional, missing")
        lines.append(f"  [{mark}] {s.name}: {s.detail}  ({s.needed_for})")
        for step in s.hint:
            lines.append(f"        -> {step}")
    missing = missing_required(statuses)
    lines.append("All required dependencies are available." if not missing else
                 f"{len(missing)} required dependency(ies) missing: install them as shown above.")
    return "\n".join(lines)

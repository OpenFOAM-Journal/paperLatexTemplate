# Installing ofj-check

ofj-check runs on **Linux** and in **WSL** on Windows. It needs:

| What | Why | Ubuntu / Debian / WSL package |
|---|---|---|
| Python ≥ 3.9 | runs the tool | `python3` (preinstalled) |
| git | downloads the current template and its history | `git` |
| pdfplumber (Python package) | reads the submitted PDF | installed with pip into a virtual environment, see below |

TeX is **not** needed to check papers.

## 1. One-time setup (Ubuntu, Debian, WSL)

```bash
sudo apt install git python3-venv python3-pip
```

Then get the template repository and go to the tool's folder (in WSL a Windows folder
`C:\Users\<you>\…` is `/mnt/c/Users/<you>/…`):

```bash
git clone https://github.com/OpenFOAM-Journal/paperLatexTemplate.git
cd paperLatexTemplate/tools/ofj-check
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
./ofj-check --check-deps
```

`./ofj-check` uses `.venv` automatically. `--check-deps` lists every requirement as `[OK ]`
or `[MISSING]`, together with the command that installs it.

Other distributions: install `git` and the Python `venv`/`pip` modules with your package manager
(Fedora: `sudo dnf install git python3-pip`; Arch: `sudo pacman -S git python-pip`), then follow
the same steps.

*Optional:* `.venv/bin/pip install -e .` also creates the command `.venv/bin/ofj-check`.

## 2. The template copy

On the first run, ofj-check downloads the official template
(<https://github.com/OpenFOAM-Journal/paperLatexTemplate>) into
`~/.cache/ofj-template-check/`, which needs internet access once. After that it updates the
copy when it is more than 12 hours old, and works offline with a warning if GitHub cannot be
reached.

| Option | Effect |
|---|---|
| `--offline` | never contact GitHub, use the cached copy |
| `--update-template` | update the cached copy now |
| `--template-dir DIR` | use an existing local clone instead (it is not updated automatically) |
| `--cache-dir DIR` | keep the copy somewhere else (or set `OFJ_CHECK_CACHE`) |

## 3. Usage

```bash
./ofj-check paper.pdf                         # PDF only (the usual case)
./ofj-check submission/                       # folder with LaTeX sources, with or without PDF
./ofj-check submission.zip --report out.md    # archive; also write a Markdown report
./ofj-check submission/ --pdf build/paper-review.pdf   # choose the manuscript PDF
./ofj-check --help
```

Exit codes: `0` current template · `1` outdated or modified · `2` not the OFJ template ·
`3` inconclusive · `4` missing dependency / template unavailable · `5` input cannot be checked.

## 4. Running the tests

```bash
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests
```

The tests use only the standard library. Tests that need pdfplumber or git are skipped when
these are missing.

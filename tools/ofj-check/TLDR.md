# ofj-check — TL;DR

Checks whether a submission (PDF or zip of LaTeX sources) uses the current OFJ LaTeX template.
Runs in WSL or on Linux.

## Install (once)

```bash
sudo apt install git python3-venv python3-pip
git clone https://github.com/OpenFOAM-Journal/paperLatexTemplate.git
cd paperLatexTemplate/tools/ofj-check
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
./ofj-check --check-deps
```

All lines must say `[OK ]`. Below, `<checker>` is this `tools/ofj-check` folder. Optional, to
run `ofj-check` from any folder:

```bash
echo "alias ofj-check='$PWD/ofj-check'" >> ~/.bashrc && source ~/.bashrc
```

## Check a submission

```bash
<checker>/ofj-check  <path-to>/paper.pdf
<checker>/ofj-check  <path-to>/submission.zip  --report report.md
```

(or just `ofj-check …` with the alias). In WSL a Windows folder `C:\Users\<you>\…` is
`/mnt/c/Users/<you>/…`. The full report is printed; `--report` also saves it as Markdown. The
first run needs internet (it downloads the current template).

## Read the result

The first line says it all:

| Verdict | Meaning |
|---|---|
| **Current template** | fine |
| **Older template, closest to Gxx** | an older template was used; "Triggered by" says why |
| **… modified** | template files were changed |
| **Not made with the OFJ template** | template not used |

Below it: **Also** (e.g. NOT ANONYMOUS), a **suggested message to the authors**, then the details.

More: [README.md](README.md)

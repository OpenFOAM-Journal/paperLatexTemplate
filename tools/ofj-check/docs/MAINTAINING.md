# Maintaining ofj-check

`ofj-check` recognises template versions by fingerprints that were collected from the
template's history. **When the template changes, the fingerprints have to be updated.** This
document describes how, and how the tool is organised.

## How you notice that an update is due

Every run compares the downloaded template with the newest template commit the fingerprint
catalogue knows (`CATALOGUE_COMMIT` in `src/ofjcheck/generations.py`). If the template has
newer commits that change the template itself (not only the README or CI), every report says:

> The template has N change(s) newer than the fingerprint catalogue (catalogue covers up to
> cd2b7f2): … A paper using the newest template may be reported as current although these
> changes are not checked. Please update the catalogue …

Until the catalogue is updated, the tool keeps working: it treats the newest generation it
knows as "current".

## Organisation of the code

| File | Purpose |
|---|---|
| `src/ofjcheck/cli.py` | command line, exit codes |
| `src/ofjcheck/deps.py` | `--check-deps`, install hints for Linux/WSL |
| `src/ofjcheck/template_repo.py` | downloading/updating the template (bare git clone in `~/.cache/ofj-template-check/`), catalogue-coverage warning |
| `src/ofjcheck/inputs.py` | what was submitted: PDF, folder, archive (safe unpacking), main `.tex`, manuscript PDF |
| `src/ofjcheck/generations.py` | **the generations G01–G11 as data**, `CATALOGUE_COMMIT` |
| `src/ofjcheck/filematch.py` | every version of every template file, exact matching, production data in `ofjart.cls` |
| `src/ofjcheck/latex.py` | reading the LaTeX document (`\input` tree, comments and verbatim masked) |
| `src/ofjcheck/source_rules.py` | fingerprint rules for the sources (SRC…, CLS…, PLC…, PRD01, VER01) |
| `src/ofjcheck/pdf_view.py`, `pdf_rules.py` | text, fonts, links and layout of the PDF; PDF rules (PDF…, NOT…, PRD02, VER02) |
| `src/ofjcheck/crosscheck.py` | PDF against sources (XCHK…) |
| `src/ofjcheck/verdict.py` | combining all findings into the verdict |
| `src/ofjcheck/report.py` | text, Markdown and JSON reports, message to the authors |
| `docs/FINGERPRINTS.md` | the catalogue: generations, fingerprints, rule IDs (§11) |
| `research/` | how the catalogue was made: history tables, reference PDFs, scripts |
| `tests/` | unit tests and the history/reference tests (below) |

A finding says which template generations it points to (`implies_from`/`implies_to`) or argues
against (`excludes_from`/`excludes_to`), how reliable it is, and what kind it is (`outdated`,
`consistent`, `modified`, `style`, `production`, …). Rules create version findings with
`signal(...)` in `source_rules.py`, which decides from the range alone whether the finding is
"consistent" (range includes the current generation) or "outdated". The verdict
(`verdict.py`) needs no change when rules are added.

## Procedure when the template has changed

1. **Get the new template.** The tool lives inside the template repository, so `git pull` in
   your clone brings both up to date (`./ofj-check --update-template` also refreshes the
   cached copy the tool compares with).
2. **List what changed** since the catalogue (in the repository):
   ```bash
   git log --first-parent --stat <CATALOGUE_COMMIT>..origin/master -- . ':!tools'
   ```
   Changes under `tools/` (this tool and similar) are not template changes and are ignored by
   the tool.
3. **Decide for each change** whether it leaves a trace in the sources or the PDF that tells
   new from old: a new or changed preamble line, a changed class file (automatic, see 6), a new
   section, a different label in the PDF, a new convention. Changes to comments, the README or
   CI need nothing.
4. **Add a generation** if a change matters (in `src/ofjcheck/generations.py`):
   - append `Generation("G12", "<first commit, 7 chars>", "<date>", None, "<reference commit>", "<title>", "<summary>")`;
     the *first commit* is the first commit **on the first-parent history of master** that
     contains the change (for a merged pull request: the merge commit);
   - give the previous generation its `end` date (the day before);
   - set `CATALOGUE_COMMIT` to the full hash of the newest commit you reviewed (also when you
     add no generation, so the warning goes away).
5. **Add or adjust rules** in `source_rules.py` / `pdf_rules.py`:
   - a new feature present ⇒ `signal(ID, title, ("G12", None), …)`;
   - a feature that the change removed ⇒ `signal(ID, title, ("Gxx", "G11"), …)` with
     `importance` *convention* or *required* if it should make the verdict "older template";
   - weak or "absent" evidence ⇒ `reliability=WEAK` or an `excludes` range;
   - ranges that end in the middle of a generation must include that generation (the history
     test below finds such mistakes);
   - add the change to the `CHANGE` texts, so that reports can quote it.
6. **Class and style files need nothing**: `filematch.py` reads every version of every file from
   the git history at run time.
7. **Update `docs/FINGERPRINTS.md`**: the generation table (§2) and the rule list (§11).
8. **Build a reference PDF** of the new generation (in WSL or Linux, needs TeX Live; run in
   `tools/ofj-check`, where `../..` is the repository):
   ```bash
   ERAS="G12_<date>:<commit>" bash research/scripts/build_refs.sh ../.. research/reference_pdfs /tmp/ofj_refs
   ```
   Files named `G12_….pdf` are picked up by the tests automatically.
9. **Run the tests** (see below). They must all pass.

## Tests

```bash
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests
```

The two tests that matter most when the template changes:

| Test | Checks |
|---|---|
| `tests/test_history_snapshots.py` | **every** state the template ever had on master (52 commits up to `cd2b7f2`) is checked from its sources: each must get the verdict "current" (newest) or "outdated" (all others), and every finding must point to a range containing the commit's own generation. New commits are included automatically once `CATALOGUE_COMMIT` moves. |
| `tests/test_pdf_rules.py` | the same for every reference PDF in `research/reference_pdfs/` |

They need the template's history: the repository this folder is part of (found
automatically), `$OFJ_TEMPLATE_REPO`, or the tool's cached copy; otherwise they are skipped.
Tests that need pdfplumber are skipped without it.

## Playbook for the open template pull requests (status 2026-11-05)

| PR | When merged | What to do |
|---|---|---|
| **#53** mandatory AI declaration | `SRC30` ("Mandatory AI declaration missing", *required*) **switches on by itself**: it is active as soon as the current template's `ofj-template.tex` inputs `aiDeclaration`. | Add generation G12 (first commit = the merge). Add a PDF rule: the heading "Declaration on the Use of Artificial Intelligence" present ⇒ consistent `("G12", None)`; missing ⇒ outdated, *required* (it is kept in review builds). Give `SRC30` the range `("G01", "G11")`. |
| **#52** cleveref | `SRC26` ("\cref used") and the link check `PDF11` **switch off by themselves** when the current template loads cleveref. | Add G12. Sources: `\cref`/`\Cref` ⇒ consistent `("G12", None)`; `Eqn.~\ref` ⇒ `("G11", "G11")`; revise `SRC03`/`SRC04`. PDF: with `nameinlink`, cleveref links include the word ("Fig. 1") like `\autoref` did; tell them apart by plurals ("Figs. 1 and 2"), `\Cref` at sentence starts ("Figure 1") and the link target names. |
| **#47** T1 fonts, IEEEtran.bst | — | `PDF15`: accept cm-super fonts (`SFRM…`) as current; `SRC27` (T1 added) becomes a consistent signal for the new generation. A shipped `IEEEtran.bst` is matched automatically. |
| **#51** listing examples | — | Nothing needed; `examples.tex` and `parts/introduction.tex` versions are matched automatically. |
| **#54** style checker | — | Nothing needed; see below. |

If the template ever declares an explicit version (see "Optional explicit version" in
[FINGERPRINTS.md](FINGERPRINTS.md#11-rules-implemented)), a new generation only needs its entry
in `generations.py`.

## Relation to the style checker of PR #54

PR #54 (`checkStyle.py`, P. Cardiff, open) and `ofj-check` answer different questions and
complement each other:

| | `checkStyle.py` (PR #54) | `ofj-check` |
|---|---|---|
| Question | Does the manuscript follow the template's **rules and conventions**? | **Which version** of the template was used — and was it used at all? |
| Input | LaTeX sources (plus the LaTeX log) | the PDF alone (the usual submission), sources, or both |
| User | authors before submitting, CI of the template repository | editors receiving a submission |
| Knowledge | the current template only | the whole template history (all 52 states, 11 generations) |
| Output | about 45 rules, errors and warnings, file:line | a verdict with confidence and closest generation, the triggering findings, a message to the authors |
| Typical findings | `Figure~\ref` instead of `Fig.~\ref`, British spelling, `[h]` floats, bibliography fields, undefined references | old class files, small-capital headings, `\autoref` links, not anonymous, production version, not the template |

**Overlap** (both check, with different aims): leftover placeholders (`PLC00x` / `PLC01`),
`\bibliographystyle{IEEEtran}` (`STR008` / `SRC23`), `\numberwithin` (`STR009` / `SRC22`),
`\autoref`/`\cref` (`REF004` / `SRC03`, `SRC26`), information hidden in review mode (`REV001` /
`PDF14`), the AI declaration (`STR001`–`STR006` / `SRC30`).

**Possible later integration** (not done; both tools stay independent for now): once
`checkStyle.py` is on the template's master, `ofj-check` already downloads it with the
template. When sources are submitted it could run it on them and add its results as a separate
"Style" section of the report. The shared knowledge (placeholder list, reference conventions)
could then live in one place.

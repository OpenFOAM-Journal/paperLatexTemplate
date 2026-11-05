# ofj-check

Checks whether a submission to the [OpenFOAM Journal](https://journal.openfoam.com/) was
prepared with the current version of the
[official LaTeX template](https://github.com/OpenFOAM-Journal/paperLatexTemplate), and if not,
reports what shows it.

The template has no version number, so `ofj-check` recognises template versions by their
fingerprints: details that changed over the template's history (class files, preamble lines,
fonts and labels in the PDF, how cross-references are linked, …). It knows every version of
the template since 2021, grouped into eleven *generations* (G01–G11), and downloads the
current template from GitHub to compare with.

The tool is for editors; authors do not need it. It lives in `tools/ofj-check/` of the
template repository.

- **In a hurry: [TLDR.md](TLDR.md)** (install and first run in 30 seconds)
- Installation: [docs/INSTALL.md](docs/INSTALL.md)
- Template generations and fingerprints: [docs/FINGERPRINTS.md](docs/FINGERPRINTS.md)
- Keeping the tool up to date when the template changes: [docs/MAINTAINING.md](docs/MAINTAINING.md)

## Quick start

On Linux or in WSL, in `tools/ofj-check/`, once set up as described in
[docs/INSTALL.md](docs/INSTALL.md):

```bash
./ofj-check paper.pdf                          # the usual case: the anonymous review PDF
./ofj-check submission.zip --report paper.md   # sources and PDF in an archive; also a Markdown report
./ofj-check submission/                        # an unpacked folder of sources, with or without PDF
./ofj-check --check-deps                       # is everything installed?
```

| Input | What is checked |
|---|---|
| a PDF | the PDF |
| a folder, a `.tex` file, or a `.zip` / `.tar.gz` | the LaTeX sources, and the manuscript PDF if one is included (figure PDFs and the journal logo are recognised and skipped) |

Options you may need: `--pdf FILE` / `--main-tex FILE` when a folder holds several candidates;
`--mode pdf|latex|both` to check only one part; `--json FILE` for machine-readable output;
`-q` for the verdict line only; `--offline` when there is no internet (uses the cached
template). `./ofj-check --help` lists everything.

The submitted files are never changed. Archives are unpacked into a temporary folder that is
deleted afterwards. Nothing is sent anywhere; the only network access is downloading the
public template from GitHub.

## Reading a report

A report starts with the **verdict**, then everything that led to it.

### The verdict

| Verdict | Exit code | Meaning |
|---|---|---|
| **Current template** | 0 | Nothing points to an older template. "…, with minor differences" lists small points such as a style convention. |
| **Older template, closest to Gxx** | 1 | At least one clear finding shows that the current template was not used. *Closest to* names the newest template generation that fits all evidence; *matches* gives the range of generations that fit. "…, mixed with other versions" means that parts come from different template versions (e.g. old main file, newer class files). "…, modified" means template files were also changed. |
| **Current template, but modified** | 1 | The current template, but with changes the authors should not make (e.g. an edited `ofj.cls`, other margins, another bibliography style). |
| **Not made with the OFJ template** | 2 | The PDF lacks the OFJ title page (journal header, footnote, copyright line, DOI/Repository block, page layout), the sources use another document class, or the PDF was made with a word processor. |
| **Inconclusive** | 3 | Nothing was found that tells template versions apart. |

Exit codes 4 (something missing: dependency or template download) and 5 (input cannot be
checked) mean the check did not run.

**Confidence** says how firmly the evidence supports the verdict:

- *high*: clear evidence, nothing contradicting it;
- *medium*: e.g. "current", but some older generation is ruled out only by weak evidence
  (G10 differs from G11 only in how cross-references are linked), or an "older template"
  verdict with mixed versions;
- *low*: "consistent with the current template", but this input cannot tell it apart from some
  older generation.

**Triggered by** lists the findings that decided the verdict, minor ones marked "(minor)".
Each refers to a rule ID (e.g. `PDF11`) explained in [docs/FINGERPRINTS.md](docs/FINGERPRINTS.md).

**Also** lists what matters regardless of the template version:

- **NOT ANONYMOUS**: the PDF shows author names, e-mail addresses, ORCID links, the repository
  or author contributions, although submissions are reviewed double-blind.
- **PRODUCTION VERSION**: volume, pages and dates are filled in, i.e. a version prepared for or
  after publication, not an author submission. Visible authors and the copyright year are then
  expected and not reported as problems.
- Template placeholders or example content left in the sources (`v20xx`, example authors, …).
- When PDF and sources are submitted together: the PDF does not seem to come from these
  sources, or the two point to different template generations.

### Suggested message to the authors

A ready-to-paste note built from the findings, for example "Please refer to equations, tables,
figures and listings as Eqn.~\ref{...}, …". Review it before sending. The copyright year is
never in it: the editor sets it.

### Details

All findings, grouped by importance:

| Group | Meaning |
|---|---|
| Required by the current template | e.g. an old or modified class file, visible author information |
| Template conventions not followed | e.g. `\autoref` instead of `Fig.~\ref`, leftover placeholders |
| Cosmetic differences | e.g. the copyright year, footnote symbols |
| Supporting evidence / for information | findings consistent with the current template |

Each finding shows its **evidence** (PDF page and text, link target, or `file:line` in the
sources), how reliable the signal is (*strong / medium / weak*), which template generations it
points to, and the **template change** behind it (date and pull request).

**Warnings** at the end deserve attention. Most important: *"The template has N change(s)
newer than the fingerprint catalogue"*. The template was updated after `ofj-check` was last
adapted; newer changes are not checked yet. See [docs/MAINTAINING.md](docs/MAINTAINING.md).

### The template generations

| | Since | In short |
|---|---|---|
| G01 | 2021-04 | first template, US Letter |
| G02 | 2021-08 | A4, 2.5 cm margins |
| G03 | 2022-03 | © The Authors, CC BY-SA 4.0 |
| G04 | 2022-05 | ISSN 2753-8168, vector logo |
| G05 | 2022-11 | Makefile, review mode, `\autoref` |
| G06 | 2023-01 | sections in `parts/` |
| G07 | 2023-02 | today's class files: bold headings, "Results with version(s)" |
| G08 | 2023-04 | author contributions in the main file |
| G09 | 2025-01 | "Use Title Case" title, © 2024 |
| G10 | 2026-01 | © 2026 |
| **G11** | **2026-03** | **`Eqn.~\ref`, `Tab.~\ref`, `Fig.~\ref`, `Lst.~\ref` instead of `\autoref`** (current) |

## What the tool cannot do

- It checks the template, not the content: language, figures, the quality of the AI declaration
  or the bibliography are not judged. (For style and conventions in the sources, see the
  proposed `checkStyle.py` in template PR #54; how the two relate is described in
  [docs/MAINTAINING.md](docs/MAINTAINING.md#relation-to-the-style-checker-of-pr-54).)
- From a PDF alone, versions that look identical cannot be told apart (e.g. G04 and early G05,
  or G07 and G08). The verdict then gives a range.
- A PDF that was printed to PDF, compressed or merged after LaTeX may have lost links and fonts;
  the report warns about this.
- If the template changes, the tool recognises the new version only after its fingerprints have
  been added ([docs/MAINTAINING.md](docs/MAINTAINING.md)); until then it warns.

# OFJ Template — Fingerprint Catalogue

How `ofj-check` recognises template versions. Template repository:
<https://github.com/OpenFOAM-Journal/paperLatexTemplate>, analysed up to `master` = `cd2b7f2`
(2026-03-31).

Supporting material (all in `research/`):

| File | Content |
|---|---|
| `file_versions.md` / `.json` | Every version of every shipped file on `master`, with the dates it was current |
| `reference_pdfs/` | Template PDF as rendered at the end of each generation (final and review builds) |
| `reference_pdfs_inspection.md` | Page size, fonts, link annotations and page-1 text of each reference PDF |
| `negative_samples/` | The same content typeset *without* the template (`article` class) |
| `scripts/` | The scripts that produced all of the above (reproducible) |

---

## 1. Key findings

1. **The template has no version number.** `ofj.cls` still says `v1.01 2020/09/23`;
   the only git tag (`v2023.0`) is not maintained. Everything below has to be inferred.
2. **The class files have been frozen since 9 Feb 2023.** `ofj.cls`, `ofjart.cls`,
   `orcidlink.sty`, `tensorNotation.sty` and `Makefile` have not changed since early 2023.
   Comparing class files can therefore only tell "Feb 2023 or newer" apart from older
   versions. It cannot tell the 2023–2026 generations apart.
3. **Every change since 2023 is in files that authors edit**: `ofj-template.tex` (the preamble
   is marked "Please do not modify") and the `parts/*.tex` examples. Recent generations can
   only be recognised from preamble lines, conventions the authors copied, and what these
   produce in the PDF.
4. **The most useful PDF signal for "current or not" is the hyperlink area of
   cross-references.** With `\autoref` (the template from 2022-12 to 2026-03), the link
   covers "Fig. 1". With `Fig.~\ref` (current), it covers only "1". The visible text is
   identical, but the link annotations differ, and they can be read from any PDF.
   *Caveat:* PR #52 (`cleveref` with `nameinlink`) would bring back word-inclusive links.
5. **Heading style is the clearest visual dividing line.** Small caps (`CMCSC10`) up to
   G06, bold (`CMBX10`) from G07 (PR #30, merged 2023-02-08).

## 2. Template generations

Dates are the day the change landed on `master` (merge date). "Current" = G11.
A generation starts at its **first commit** on the first-parent history of `master`. Several
changes often landed on the same day, so the first commit, not the date, is the exact
boundary (checked against all 52 published states of the template).

| Gen | First commit | On master | Reference PDF | What defines it |
|---|---|---|---|---|
| G01 | `b1d669b` | 2021-04-28 → 2021-08-29 | `G01_2021-07-27_eb037cd` | Initial AMS-derived template; **US Letter**; narrow AMS margins; © OpenFOAM Journal |
| G02 | `15fc5c2` | 2021-08-30 → 2022-03-01 | `G02_2022-01-20_b5edfcf` | **A4**, 2.5 cm margins, black links; "Received: 14 Juntember 2022" placeholder; ISSN TBD; ORCID (2022-01) |
| G03 | `62dec8d` | 2022-03-02 → 2022-05-03 | `G03_2022-03-02_f532bdd` | © 2022 **The Authors, CC BY-SA 4.0**; `\usepackage{cite}` |
| G04 | `48b3c92` | 2022-05-04 → 2022-11-07 | `G04_2022-05-18_029028a` | **ISSN 2753-8168**, "Volume 2 [Enter correct Journal Section here]"; vector logo (05-18) |
| G05 | `8647056` | 2022-11-08 → 2023-01-29 | `G05_2022-12-27_e88d246` | `Makefile`; numbered footnotes; MnSymbol dropped; **review mode** + `\autoref` + full author names (12-27) |
| G06 | `d69512b` | 2023-01-30 → 2023-02-07 | `G06_2023-01-30_f004fab` | **`parts/` split**; `examples.tex`; Makefile `TYPE`; line numbers only in review |
| G07 | `3178e65` | 2023-02-08 → 2023-04-29 | `G07_2023-02-26_0fc4ddf` | **Class files reach today's state** (PRs #27–#36, 02-08/09): bold headings, mixed-case authors, "Results with version(s)/Repository"; hyperref in preamble; `\autoref` names Tab./Fig./Eqn. (02-25); `\xspace` (02-26) |
| G08 | `4f17267` | 2023-04-30 → 2025-01-10 | `G08_2023-04-30_4f17267` | Author contributions moved into main file |
| G09 | `431cc52` | 2025-01-11 → 2026-01-01 | `G09_2025-04-10_e489934` | "Use Title Case" title; © **2024**; typo fixes; conclusion shows `\autoref` usage |
| G10 | `66b2f6a` | 2026-01-02 → 2026-03-30 | `G10_2026-01-02_66b2f6a` | © **2026** |
| **G11** | **`cd2b7f2`** | **2026-03-31 → today** | `G11_2026-03-31_cd2b7f2` | **`\autoref` → `Eqn.~\ref`, `Tab.~\ref`, `Fig.~\ref`, `Lst.~\ref`**; autoref names removed; captioned listing example |
| *G12?* | — | *pending* | — | *PR #53 AI declaration, #52 cleveref, #51 listing examples, #47 T1 fontenc* — see §8 |

`G04a` (`48b3c92`, 2022-05-04) is an extra reference: G04 before the vector logo.

**How far apart are recent generations?** G10 → G11 differs only in the
cross-reference convention. G09 → G10 differs only in the copyright year. G08 → G09 differs
in the title placeholder and the copyright year. These are small differences, which is why
the verdict reports *which* changes are missing, not just "outdated" (decision D2, §10).

## 3. Exact file matching (sources only)

The tool hashes each file the authors ship and looks it up in the version table
(`research/file_versions.md`). It uses a normalised hash (CRLF→LF, trailing whitespace
stripped), because authors on Windows or using Overleaf often re-save files.

| File | Versions | Current since | What a match tells |
|---|---|---|---|
| `ofj.cls` | 10 | 2023-02-09 | ≥ G07, or an exact older generation |
| `ofjart.cls` | 7 (+6 branch-only) | 2023-02-09 | ≥ G07, or an exact older generation |
| `tensorNotation.sty` | 2 | 2022-11-08 | ≥ G05 vs ≤ G04 |
| `orcidlink.sty` | 2 | 2023-02-09 | ≥ G07 vs G02–G06; absent ≤ G01 |
| `Makefile` | 3 | 2023-01-30 | ≥ G06; absent ≤ G04 |
| `ofj-template-review.tex` | 1 | 2022-12-27 | present ⇒ ≥ G05 (Dec 2022) |
| `examples.tex`, `parts/abstract.tex`, `parts/acknowledgements.tex`, `parts/appendix.tex` | 1 each | 2023-01-30 | present ⇒ ≥ G06 |
| `parts/author-contributions.tex` | 1 | removed 2023-04-30 | present ⇒ G06–G07 |
| `parts/introduction.tex`, `section.tex`, `conclusion.tex` | 3 each | 2026-03-31 | usually edited by authors; an unedited copy pins G06–G08 / G09–G10 / G11 |
| `ofj-template.tex` | 34 (+11 branch-only) | 2026-03-31 | always edited; compare the **preamble** only (§4) |
| `amsart.cls`, `jams-l.cls`, `finiteVolumeNotation.sty`, `Bibliography.bib` (current) | 1 | 2021 | no version information; confirms the template package |

A shipped class file that matches **no** known version means it was modified by the authors.
That is a finding in itself; the report shows a diff against the closest version.

## 4. Source fingerprints (`.tex`)

Reliability: **S** = strong (near-certain), **M** = medium (authors may plausibly change it),
**W** = weak (a hint only).

| ID | Signal in the source | Implies | Rel. |
|---|---|---|---|
| SRC01 | `\documentclass[...]{ofj}` | OFJ template used at all | S |
| SRC02 | `\def\tableautorefname{Tab.}` / `figure…` / `equation…` in the preamble | **G07–G10** (2023-02-25 → 2026-03-31): *not current* | S |
| SRC03 | `\autoref{…}` / `\Autoref` used in the body | G05–G10 convention; current requires `Eqn.~\ref` etc. | S (convention) |
| SRC04 | `Eqn.~\ref`, `Tab.~\ref`, `Fig.~\ref`, `Lst.~\ref` used | G11 convention | M (positive) |
| SRC05 | `Eq.\ \ref`, `Tab.\ \ref`, `\eqref` | ≤ G05 convention (before 2022-12-27) | M |
| SRC06 | `\copyrightinfo{2020\|2021}{OpenFOAM… Journal}` | ≤ G02 | M |
| SRC07 | `\copyrightinfo{YEAR}{The Authors. … CC BY-SA 4.0 …}`: 2022 / 2024 / 2026 | G03–G08 / G09 / G10–G11 | M (the editor updates the year) |
| SRC08 | `\usepackage{xspace}` + `\OF` ending in `\xspace` | ≥ G07 (2023-02-26); old `\OF` ends in a hard space `} }` | S |
| SRC09 | hyperref loaded in the main preamble (`colorlinks…black`) | ≥ G07 (2023-02-09) | S |
| SRC10 | `\ifdefined\review` blocks; `ofj-template-review.tex` | ≥ G05 (2022-12-27) | S |
| SRC11 | unconditional `\doublespacing` / `\linenumbers` | ≤ G05 (before 2022-12-27 / 2023-01-30) | S |
| SRC12 | `\input{parts/…}` structure | ≥ G06 (2023-01-30) | M (authors restructure) |
| SRC13 | `\authorcontributions{…}` inline inside the review `\else` | ≥ G08 (2023-04-30); via `parts/author-contributions.tex` ⇒ G06–G07 | M |
| SRC14 | `\usepackage[hang,flushmargin]{footmisc}`; `[symbol]{footmisc}` | ≥ G06; 2021-09 → 2022-11 | S |
| SRC15 | `\usepackage{orcidlink}`, `\usepackage{cite}` | ≥ G02 (2022-01), ≥ G03 (2022-03) | S |
| SRC16 | `\author[M. Jersey]{…}` (short form) | ≥ G07 (2023-02-08) | W |
| SRC17 | comment "This is the version(s) that was used to generate the results" | ≥ G07 (2023-02-08) | M (comments get deleted) |
| SRC18 | title placeholder `Journal publication` vs `Journal Publication - Use Title Case` | ≤ G08 vs ≥ G09 (only if left unedited) | S if present |
| SRC19 | `\DOI{00.1000/xxx}` vs `\DOI{TBD}` | before vs after 2021-11-22 | S |
| SRC20 | `changes` / `comment` packages, track-changes instructions | ≤ G01 (before 2021-06-14) | S |
| SRC21 | `\numberwithin{equation}{section}` active | ≤ G01 (template said "don't enable" from 2021-06-08) | M |
| SRC22 | `lstlisting` with `caption=` and `label=` + `Lst.~\ref` | G11 example | W (positive) |
| SRC23 | `\bibliographystyle{IEEEtran}` | all generations ≥ 2021-04-28 | S (other style ⇒ modified) |
| SRC24 | `Makefile` with `TYPE = …` | ≥ G06 | S |

**Leftover placeholders** (any generation, reported separately as "unedited template content"):
`v20xx`, `github.com/xxx`, `Maria Jersey`/`John Smith`/`Philip Murphy`, `Emailaddress1`,
`Address1`, `This is the place for…`, `Theoretical backgroud`, the example CRediT block,
`Use Title Case`, `SetTypeInMakefile`, `0000-1234-5678-0000`.

## 5. Class-file fingerprints

These apply when the authors ship class files, or modified copies of them.

| ID | Signal | Implies |
|---|---|---|
| CLS01 | `ofjart.cls` `\ExecuteOptions{…letterpaper…}` | G01 (before 2021-08-30) |
| CLS02 | `ofj.cls` `\RequirePackage[margin=2.5cm]{geometry}` | ≥ 2021-08-27 |
| CLS03 | `\PII{S \ISSN(XX)0000-0}` / `\PII{ISSN: TBD}` / `\PII{ISSN: 2753-8168}` | ≤ 2021-11 / G02–G03 / ≥ G04 |
| CLS04 | logo `OpenFOAMJournal.png` vs `.pdf` | before / after 2022-05-18 |
| CLS05 | `\scshape` / `\MakeUppercase` / `\uppercasenonmath` in headings, authors, captions, running heads | ≤ G06 (before 2023-02-09) |
| CLS06 | metadata as `tabular` with "Version(s)/Repo" vs `description` with "Results with version(s)/Repository" | before / after 2023-02-08 |
| CLS07 | `ofj.cls` loads hyperref itself | 2021-08-27 → 2023-02-09 |
| CLS08 | `tensorNotation.sty` declares `MnSymbolE` fonts | ≤ G04 (before 2022-11-08) |
| CLS09 | `\datename` with "Received: 14 Juntember 2022…" | ≥ 2021-11-22 (still current) |

## 6. PDF fingerprints

Measured on the reference PDFs (`research/reference_pdfs_inspection.md`).

| ID | Signal in the PDF | Implies | Rel. |
|---|---|---|---|
| PDF01 | Page size 595.3 × 841.9 pt (A4) vs 612 × 792 (Letter) | ≥ G02 vs G01 / not the template | S |
| PDF02 | Body text block x = 70.9 → 524.4 pt (453.5 pt wide, 2.5 cm margins) | ≥ G02; `article` class gives 117.8 → 476.5 | S |
| PDF03 | Section heading, "Abstract." label, "Figure/Table" caption labels in **CMCSC10** (small caps) vs **CMBX10/CMBX8** (bold) | ≤ G06 vs ≥ G07 | S |
| PDF04 | Author names on title page in capitals (M. JERSEY) vs mixed case | ≤ G06 vs ≥ G07 | S |
| PDF05 | Running head on page 2+: capitalised title/authors vs mixed case / short author names | ≤ G06 vs ≥ G07 | S |
| PDF06 | Metadata labels "Version(s): / Repo:" vs "Results with version(s): / Repository:" | ≤ G06 vs ≥ G07 | S |
| PDF07 | Header: "Volume 00, Pages 000–000 (Xxxx XX, XXXX) / Sxxxx-yyyy(XX)0000-0" · "Volume 123 … ISSN: TBD" · "Volume 2 [Enter correct Journal Section here], Pages 1–999 / ISSN: 2753-8168" | G01 · G02–G03 · ≥ G04 | S |
| PDF08 | Logo text "Open FOAM R Journal" extractable (vector logo) | ≥ 2022-05-18 (G04) | S |
| PDF09 | Footer "© 2021 OpenFOAM® Journal" · "© 2022 The Authors … CC BY-SA 4.0" · © 2024 · © 2026 | ≤ G02 · G03–G08 · G09 · ≥ G10 | M |
| PDF10 | Footnote "∗ Corresponding author / Received: 14 Juntember 2022, …" vs "Received by the editors <date>" | ≥ 2021-11-22 vs older | S |
| PDF11 | **Cross-reference link annotations**: link text "Equation 1" / "Table 1" / "Figure 1" · "Eqn. 1" / "Tab. 1" / "Fig. 1" · "1" only. Classify each link by its named destination (`equation.*`, `table.*`, `figure.*`, `lstlisting.*`, `section.*`); **ignore `cite.*`**, which shows only the number in every generation | G05–G06 (default autoref names) · **G07–G10** (autoref) · G11 or ≤ G04 | **S** |
| PDF12 | Visible reference wording "(1)" / "Equation 1" / "Eqn. 1" / "Lst. 1" | ≤ G04 / G05–G06 / ≥ G07 / G11 example | M |
| PDF13 | Line numbers in the margin of a non-review PDF; double spacing | ≤ G05 (both were always on before 2022-12-27 / 2023-01-30) | W: submissions are review builds (D1), so line numbers are expected |
| PDF14 | Review build: no authors/addresses, empty "Repository:", line numbers | ≥ G05 review mode. **Expected for submissions (D1).** Author names, addresses, e-mails or a repository URL on the title page ⇒ finding "not built with `make review` / anonymity leak" | S |
| PDF15 | Fonts: Computer Modern Type 1 (CMR10 …) + NimbusMonL (listings) | consistent with the template (pdfLaTeX) | M |
| PDF16 | Listing with rounded frame, line numbers, "Listing 1." caption | frame: all generations; captioned example: G11 | W |
| PDF17 | Producer / Creator: `pdfTeX` / `LaTeX with hyperref` | TeX-produced (Overleaf: same plus TeX Live year in `PTEX.Fullbanner`) | M |

## 7. Not-the-template indicators

| ID | Indicator | Rel. |
|---|---|---|
| NOT01 | Producer is not TeX: Microsoft Word, LibreOffice, Google Docs (Skia), Pages/Quartz, … | S |
| NOT02 | No OFJ header block: no "ISSN: 2753-8168", no "Volume … Pages", no logo text | S |
| NOT03 | No "DOI / Results with version(s) / Repository" metadata block | S |
| NOT04 | No copyright footer on page 1 | M |
| NOT05 | Text block or page size outside the template values (PDF01/PDF02) | S |
| NOT06 | Heading fonts or sizes of other classes, e.g. `article`: `CMBX12` 14.3 pt headings, `CMR17` title | S |
| NOT07 | A date line under the title ("November 4, 2026") | M |
| NOT08 | Body font not Computer Modern (Times, Arial, Calibri, Latin Modern under XeLaTeX/LuaLaTeX) | M (LuaLaTeX with the template is still the template) |
| NOT09 | Source: `\documentclass` other than `ofj`; no `ofj.cls` | S |

The negative sample (`research/negative_samples/article_class_same_content.pdf`) shows
NOT02, NOT03, NOT04, NOT05, NOT06 and NOT07 all at once.

## 8. Pending changes (open PRs, inactive until merged)

| PR | Change | Effect on detection once merged |
|---|---|---|
| #53 | Mandatory "Declaration on the Use of Artificial Intelligence" (`parts/aiDeclaration.tex`, outside the review guard) | **Strongest future signal**: missing section ⇒ older template (visible in source and PDF) |
| #52 | `cleveref` with `nameinlink`, `\crefname` Eqn./Fig./Tab./Lst. | `\cref` links include the name ⇒ **PDF11 cannot then tell cleveref apart from autoref**; distinguish via plural forms ("Figs. 1 and 2") and the source. SRC02/SRC03 must be updated |
| #51 | Short/long listing examples in `examples.tex`; label `lst:transportEqn` | weak |
| #47 | `\usepackage[T1]{fontenc}` (EC/cm-super fonts in the PDF), bundled `IEEEtran.bst` | font names change ⇒ PDF15 must accept both |

**Design consequence:** fingerprints will be **data** (one entry per change, each with a
validity interval), not code. When the template changes, adding an entry is enough. Because
the tool pulls `master` at runtime, it can also warn: "the template has commits newer than
the fingerprint catalogue — please review".

## 9. Practical notes for the implementation

- **PDF text extraction drops spaces** inside some CM-font lines ("Thisistheplaceforanabstract").
  Matching must compare text with whitespace removed.
- The ® after OpenFOAM is extracted as "fi" (font encoding quirk). Matching must allow for it.
- The reference PDFs were built with TeX Live 2023 in WSL, with `texlive-science` and
  `texlive-publishers` installed and BibTeX run, so they are faithful builds. The one
  exception: G01–G04 lack the MnSymbol fonts (`texlive-fonts-extra`), which affects only a
  few math glyphs. An earlier build with stubbed packages (2026-11-04, since removed) differed
  from the rebuild only by the bibliography (reference list, `[1]` instead of `[?]`). Every
  fingerprint above was confirmed on both builds.
- Link annotations carry named destinations (`equation.1.1`, `table.1`, `figure.1`,
  `lstlisting.1`, `cite.Weller1998`), which pdfplumber can read. This is what makes PDF11
  robust.

## 10. Design decisions

- **D1 — Submissions are anonymous review builds, usually PDF only, sometimes with LaTeX.**
  PDF analysis is therefore the main path. Missing authors, an empty "Repository:" and line
  numbers are expected. Visible author information is reported.
- **D2 — Every "not current" verdict must say what triggered it.** The verdict names the
  closest generation, then lists each fingerprint that fired. Each one comes with its
  evidence (page/link/font or file:line), the template change it corresponds to (date,
  commit), and its importance: *required* (e.g. the future AI declaration), *convention*
  (e.g. `\autoref`) or *cosmetic*.
- **D3 — An outdated copyright year is reported**, as a hint (*cosmetic*), not as a
  verdict on its own: the editor sets the year.
- **D4 — No TeX needed to check papers.** TeX Live is only needed to rebuild the reference
  PDFs (`research/scripts/build_refs.sh`).

## 11. Rules implemented

### LaTeX sources — `src/ofjcheck/source_rules.py`

| Rule ID in the report | Catalogue entries | Notes |
|---|---|---|
| CLS00 | §3 exact matching (all shipped template files) | generation range from the commit history; class files: *required* |
| CLS01 | §3 modified protected file (`ofj.cls`, `ofjart.cls`, `*.sty`, `amsart.cls`, `jams-l.cls`) | closest version, similarity, diff excerpt |
| CLS10 | §3 file identical to a development-branch-only version | |
| CLS11 | §3 unedited example file (`parts/*.tex`, `ofj-template.tex`) that is part of the document | unused leftovers are not reported |
| SRC01 | SRC01 | not the OFJ class ⇒ only this finding is reported; also wrong class options |
| SRC02–SRC05 | SRC02–SRC05 | autoref names, `\autoref`, current `Eqn.~\ref` convention, old `Eq.\ \ref` |
| SRC06, SRC07 | SRC06, SRC07 | copyright holder and year; the current year is read from the current template (D3) |
| SRC08 | SRC08 | `\OF` with `\xspace` / hard space |
| SRC09 | SRC09 | hyperref in the main preamble |
| SRC10, SRC11 | SRC10, SRC11 | review mode; `\linenumbers`/`\doublespacing` outside the review condition |
| SRC13 | SRC13 | `author-contributions.tex` (G06–G07); missing statement (*required*) |
| SRC14, SRC15 | SRC14, SRC15 | footmisc options; `orcidlink`, `cite` missing |
| SRC17–SRC23 | SRC17–SRC21, SRC23 | comment, title, DOI, track changes, `\OpenFOAMversion`, `\numberwithin`, bibliography style |
| SRC25 | new | `\OpenFOAMversions`/`\Repository`/`\DOI` removed |
| SRC26 | new (PR #52) | `\cref` used although the current template has no cleveref (switches off automatically if it gets it) |
| SRC27 | §8 PR #47 | `[T1]{fontenc}` added |
| SRC30 | §8 PR #53 | mandatory AI declaration: **activates automatically** once the current template contains it |
| PLC01 | §4 placeholders | example content outside comments, including `TYPE = SetTypeInMakefile` |
| VER01 | R9 | optional version marker: `\ofjtemplateversion{...}` (generation id or date) or `% OFJ template version: ...` |

Not implemented, by design: SRC12 (`parts/` structure: authors restructure freely), SRC16
(short author names: too weak), SRC22/SRC24 (covered by SRC04 and the Makefile match).

### PDF — `src/ofjcheck/pdf_view.py`, `src/ofjcheck/pdf_rules.py`

First, page 1 is checked for five elements every template has printed since 2021: the journal
header, the title-page footnote, the copyright line, the DOI/Repository block, and the page
and text block. **Fewer than two present ⇒ not the template**; then only NOT findings are
reported.

| Rule ID in the report | Catalogue entries | Notes |
|---|---|---|
| NOT01 | NOT01 | made with Word, LibreOffice, Google Docs, Pages, ... |
| NOT02 | NOT02–NOT05 | title page of the OFJ template not found (lists the missing elements) |
| PDF01 / PDF02 | PDF01, PDF02, NOT05 | A4 + 2.5 cm text block (G02+); US Letter + AMS margins (G01); anything else ⇒ modified |
| PDF03 | PDF03 | small capitals ⇒ G01–G06 (*required*: old class); bold ⇒ G07+ |
| PDF04 | NOT06 | section headings larger than the text size (other document class) |
| PDF05 | PDF04, PDF05 | running head in capitals ⇒ G01–G06 |
| PDF06 | PDF06 | 'Version(s)/Repo' ⇒ G01–G07; 'Results with version(s)/Repository' ⇒ G07+ |
| PDF07, PDF08, PDF10 | PDF07, PDF08, PDF10 | journal header, vector logo, 'Received' footnote |
| PDF09 | PDF09 | copyright holder and year (current year read from the current template, D3) |
| PDF11 | PDF11 | cross-reference links classified by named destination; citations ignored; switches off automatically if the current template adopts cleveref |
| PDF12 | PDF12 | 'Eq. 1' wording (weak) |
| PDF13 | PDF13 | line numbers in a build that shows the authors (weak) |
| PDF14 | PDF14 (D1) | **author information visible**: e-mail, ORCID link, repository URL, author contributions (*required*) |
| PDF15 | PDF15, NOT08 | body font: CM/Latin Modern fine; cm-super (T1) ⇒ cosmetic; anything else ⇒ convention |
| PDF17 | PDF17 | PDF re-processed after LaTeX (printed to PDF, compressed, ...): checks less reliable |
| VER02 | R9 | optional template version in the PDF metadata (`OFJ-template-version: ...`) |

Verified on all 19 reference PDFs (each points to its own generation; G11 review build
clean; every older generation detected; anonymity reported for every non-review build with
authors), on the `article` negative sample and a synthetic Word PDF, and on a 21-page review
build with pdfLaTeX and with LuaLaTeX (about 2 s each).

Limitation: the running head of G01 (US Letter) sits lower on the page and is not read;
G01 is recognised by its other fingerprints.

### Verdict — `src/ofjcheck/verdict.py`, `src/ofjcheck/crosscheck.py`

1. **Not the template**: any `not-template` finding (SRC01, NOT01, NOT02) decides. Confidence is
   *medium* instead of *high* if strong template evidence exists as well.
2. **Version votes**: every finding with a generation range (or an "excludes" range, e.g.
   number-only links argue against G06–G10) votes with weight strong 3 / medium 2 / weak 1.
   The generations contradicted by the least weight form the estimated range; the newest of
   them is the closest generation.
3. **Older template** if at least one *decisive* finding exists: kind outdated, importance
   required or convention, reliability strong or medium. Cosmetic or weak findings alone (e.g.
   the copyright year, D3) never make a submission outdated; they are listed as "minor".
   Strong findings that contradict the closest generation are reported as *mixed versions*.
4. **Modified** if the current generation fits but a decisive `modified` finding exists (e.g.
   an edited `ofj.cls`, other margins, another bibliography style).
5. **Current** otherwise. Confidence: *high* if every older generation is contradicted by
   evidence of weight ≥ 3, *medium* if by weaker evidence, *low* if some older generation
   cannot be told apart in this input (then "Consistent with the current template").
6. **Remarks** always shown with the verdict: not anonymous (PDF14), placeholders, cross-check results.

Cross-check (PDF + sources): XCHK01 — most title words of the sources missing on PDF page 1;
XCHK02 — PDF and sources point to disjoint generation ranges.

The report starts with the verdict, the triggering findings and the remarks, then a
**suggested message to the authors** built from the findings' advice (the copyright year is
left out, D3), then the details.

Verified: all 52 published template states (sources) and all 19 reference PDFs get the right
verdict (current for G11, older for everything else) with their own generation inside the
estimated range; the `article` sample is "not the template"; cross-checks on matching and
mismatching PDF/source pairs.

### Refinements from tests on real submissions

Four real manuscripts (PDF only, and zip archives with sources) were checked; all verdicts
were confirmed by the editor. They led to these refinements:

| Rule ID | Change |
|---|---|
| PRD01 / PRD02 | new: production version recognised from `ofjart.cls` publication data / the PDF title page; visible authors and the copyright year are then reported for information only |
| CLS00 / CLS01 | `ofjart.cls` compared a second time without the editor's `\issueinfo`, `\pagespan`, `\datename` lines |
| SRC05 / SRC28 / PDF12 | 'Eq.' is a *style* finding (minor, no version range); only `Eq.\ \ref` remains a version clue |
| PDF09 | also reports a missing copyright line |
| XCHK02 | strong and medium evidence only |

### Optional explicit version

No template so far declares its version. Should one in future, `ofj-check` already reads it:
VER01 from `\newcommand{\ofjtemplateversion}{YYYY-MM-DD}` in the document or a shipped
`ofj.cls`, VER02 from a PDF information entry `/OFJTemplateVersion` (for example written by the
class with `\hypersetup{pdfinfo={OFJTemplateVersion={...}}}`). Both map a date to the
generation current on that day. Verified with a prototype built with pdfLaTeX and LuaLaTeX
(`research/scripts/build_version_marker_prototype.sh`, `research/marker_prototype_review.pdf`).

**Ranges corrected by the history test** (the old values were wrong on boundary days):
SRC09 old state → G01–G07 · SRC11 → G01–G06 · SRC14 `[symbol]` → G02–G05 ·
SRC15 `cite` missing → G01–G03 · G06/G07 boundary → first commit `3178e65` (2023-02-08).

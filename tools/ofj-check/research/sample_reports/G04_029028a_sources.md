# OFJ template check: template_G04_029028a

**Verdict: Older template, closest to G05 'Makefile and review mode', modified (matches G04-G05 (2022-05-04 to 2023-01-29); confidence: high)**

9 finding(s) show that the current template (G11, since 2026-03-31) was not used. The submission matches G04-G05 (2022-05-04 to 2023-01-29) best. Template files were also modified: No author contributions statement. Minor differences as well: Copyright year 2022 (current template: 2026); \OF defined with a hard space (pre-2023 template); Line numbers / double spacing always on; Footnote symbols (footmisc[symbol]).

Triggered by:

- CLS11: Unedited template example file ofj-template.tex
- CLS00: ofj.cls: template version G04-G07 (2022-05-04 to 2023-04-29)
- CLS00: ofjart.cls: template version G04-G05 (2022-05-04 to 2023-01-29)
- CLS00: orcidlink.sty: template version G02-G07 (2021-08-30 to 2023-04-29)
- CLS00: tensorNotation.sty: template version G01-G05 (2021-04-28 to 2023-01-29)
- SRC05: Old reference style 'Eq.\ \ref' (2x)
- SRC09: hyperref not loaded in the main preamble
- SRC10: No review mode (pre-2022-12-27 template)
- SRC18: Example title of the pre-2025 template
- SRC13: No author contributions statement
- (minor) SRC07: Copyright year 2022 (current template: 2026)
- (minor) SRC08: \OF defined with a hard space (pre-2023 template)
- (minor) SRC11: Line numbers / double spacing always on
- (minor) SRC14: Footnote symbols (footmisc[symbol])

Also:

- Template placeholders or example content left: Template placeholders left in the sources (11).

### Suggested message to the authors

> Dear authors,
>
> your submission was checked against the current OpenFOAM Journal LaTeX template (version of 2026-03-31, https://github.com/OpenFOAM-Journal/paperLatexTemplate). Please address the following points:
>
> - Please add the author contributions with \authorcontributions{...}.
> - Please replace the template's example content with your own.
> - Please refer to equations, tables, figures and listings as Eqn.~\ref{...}, Tab.~\ref{...}, Fig.~\ref{...} and Lst.~\ref{...}, as in the current template.
> - Please replace all example content of the template.
> - Please prepare the manuscript with the current version of the OFJ LaTeX template. Differences found: ofj.cls: template version G04-G07 (2022-05-04 to 2023-04-29); ofjart.cls: template version G04-G05 (2022-05-04 to 2023-01-29); orcidlink.sty: template version G02-G07 (2021-08-30 to 2023-04-29); tensorNotation.sty: template version G01-G05 (2021-04-28 to 2023-01-29); hyperref not loaded in the main preamble; No review mode (pre-2022-12-27 template); Example title of the pre-2025 template; \OF defined with a hard space (pre-2023 template); Line numbers / double spacing always on; Footnote symbols (footmisc[symbol]).

## Details: what was found

### Required by the current template (3)

#### CLS00: ofj.cls: template version G04-G07 (2022-05-04 to 2023-04-29)

*strong signal · indicates: outdated · points to G04-G07 (2022-05-04 to 2023-04-29)*

ofj.cls is identical to a version of the template's ofj.cls (on master from 2022-05-18 until 2023-02-08).

Evidence:
- ofj.cls: `identical to template ofj.cls (blob ac85db3)`

Template change: ofj.cls: on master from 2022-05-18 until 2023-02-08

Suggested note to the authors: Please prepare the manuscript with the current version of the OFJ LaTeX template.

#### CLS00: ofjart.cls: template version G04-G05 (2022-05-04 to 2023-01-29)

*strong signal · indicates: outdated · points to G04-G05 (2022-05-04 to 2023-01-29)*

ofjart.cls is identical to a version of the template's ofjart.cls (on master from 2022-05-04 until 2023-01-30).

Evidence:
- ofjart.cls: `identical to template ofjart.cls (blob 50c2b3b)`

Template change: ofjart.cls: on master from 2022-05-04 until 2023-01-30

Suggested note to the authors: Please prepare the manuscript with the current version of the OFJ LaTeX template.

#### SRC13: No author contributions statement

*medium signal · indicates: modified*

The template requires the contributions of all authors to be stated (\authorcontributions{...}, CRediT roles); none was found. In review builds it is hidden, but it must be in the sources.

Suggested note to the authors: Please add the author contributions with \authorcontributions{...}.

### Template conventions not followed (8)

#### CLS11: Unedited template example file ofj-template.tex

*strong signal · indicates: outdated · points to G03-G05 (2022-03-02 to 2023-01-29)*

ofj-template.tex is the template's example file ofj-template.tex, unchanged (on master from 2022-03-02 until 2022-11-08), and it is part of the document.

Evidence:
- ofj-template.tex: `identical to template ofj-template.tex`

Suggested note to the authors: Please replace the template's example content with your own.

#### CLS00: orcidlink.sty: template version G02-G07 (2021-08-30 to 2023-04-29)

*strong signal · indicates: outdated · points to G02-G07 (2021-08-30 to 2023-04-29)*

orcidlink.sty is identical to a version of the template's orcidlink.sty (on master from 2022-01-14 until 2023-02-09).

Evidence:
- orcidlink.sty: `identical to template orcidlink.sty (blob bfc397c)`

Template change: orcidlink.sty: on master from 2022-01-14 until 2023-02-09

Suggested note to the authors: Please prepare the manuscript with the current version of the OFJ LaTeX template.

#### CLS00: tensorNotation.sty: template version G01-G05 (2021-04-28 to 2023-01-29)

*strong signal · indicates: outdated · points to G01-G05 (2021-04-28 to 2023-01-29)*

tensorNotation.sty is identical to a version of the template's tensorNotation.sty (on master from 2021-04-28 until 2022-11-08).

Evidence:
- tensorNotation.sty: `identical to template tensorNotation.sty (blob f83fac4)`

Template change: tensorNotation.sty: on master from 2021-04-28 until 2022-11-08

Suggested note to the authors: Please prepare the manuscript with the current version of the OFJ LaTeX template.

#### SRC05: Old reference style 'Eq.\ \ref' (2x)

*medium signal · indicates: outdated · points to G01-G05 (2021-04-28 to 2023-01-29)*

References are written exactly as in templates before 2022-12-27 ('Eq.\ \ref{...}', 'Tab.\ \ref{...}'). The current template writes Eqn.~\ref{...} and Tab.~\ref{...}.

Evidence:
- ofj-template.tex:172: `Beside providing \OF code itself, spatial and temporal discretisation of Eq.\ \ref{eq:genTransEq} can be also described in a precise and concise manner using th`

Template change: 2022-12-27, PR #17: 'Eq.\ \ref' / 'Tab.\ \ref' replaced by \autoref; since 2026-03-31 (PR #50) the convention is Eqn.~\ref, Tab.~\ref

Suggested note to the authors: Please refer to equations, tables, figures and listings as Eqn.~\ref{...}, Tab.~\ref{...}, Fig.~\ref{...} and Lst.~\ref{...}, as in the current template.

#### SRC09: hyperref not loaded in the main preamble

*medium signal · indicates: outdated · points to G01-G07 (2021-04-28 to 2023-04-29)*

The template loads hyperref in the main preamble since 2023-02-09 (before, the class ofj.cls loaded it).

Template change: 2023-02-09, PR #36: hyperref moved from ofj.cls into the main preamble

Suggested note to the authors: Please prepare the manuscript with the current version of the OFJ LaTeX template.

#### SRC10: No review mode (pre-2022-12-27 template)

*medium signal · indicates: outdated · points to G01-G05 (2021-04-28 to 2023-01-29)*

The template's review mode (\ifdefined\review ... \fi, built with 'make review') is missing. It was added on 2022-12-27 and hides the author information for the double-blind review.

Template change: 2022-12-27, PR #12: review mode (\ifdefined\review, 'make review')

Suggested note to the authors: Please prepare the manuscript with the current version of the OFJ LaTeX template.

#### SRC18: Example title of the pre-2025 template

*strong signal · indicates: outdated · points to G01-G08 (2021-04-28 to 2025-01-10)*

The title is still the example 'OpenFOAM Journal publication' of templates before 2025-01-11.

Evidence:
- ofj-template.tex:92: `\title[\OF Journal publication]{\OF Journal publication}`

Template change: 2025-01-11, PR #42: example title changed to '... - Use Title Case'

Suggested note to the authors: Please prepare the manuscript with the current version of the OFJ LaTeX template.

#### PLC01: Template placeholders left in the sources (11)

*strong signal · indicates: placeholder*

Example content of the template is still present (in the typeset text, not in comments): OpenFOAM version placeholder 'v20xx'; repository placeholder 'https://github.com/xxx'; example author names; example address / e-mail; example ORCID; example abstract / introduction text; example introduction text; example section title; example title; example conclusion; example caption / text. Items inside the review-mode branch are hidden in review builds but appear in the final version.

Evidence:
- ofj-template.tex:71: `OpenFOAM version placeholder 'v20xx': \OpenFOAMversions{\OF v20xx}`
- ofj-template.tex:73: `repository placeholder 'https://github.com/xxx': \Repository{https://github.com/xxx}`
- ofj-template.tex:107: `example author names: \author{M. Jersey$^{1,*}$\orcidlink{0000-1234-5678-0000}}`
- ofj-template.tex:108: `example address / e-mail: \address{$^1$Address1}`
- ofj-template.tex:107: `example ORCID: \author{M. Jersey$^{1,*}$\orcidlink{0000-1234-5678-0000}}`
- ofj-template.tex:128: `example abstract / introduction text: This is the place for an abstract.`
- ofj-template.tex:154: `example introduction text: We shall consider the specific transport property $\Q$ and note that its spatial and temporal variation is governed by a`
- ofj-template.tex:197: `example section title: \section{Theoretical backgroud}`
- ofj-template.tex:92: `example title: \title[\OF Journal publication]{\OF Journal publication}`
- ofj-template.tex:212: `example conclusion: This is a conclusion.`
- ofj-template.tex:205: `example caption / text: \caption{Examplary figure}`

Suggested note to the authors: Please replace all example content of the template.

### Cosmetic differences (4)

#### SRC07: Copyright year 2022 (current template: 2026)

*medium signal · indicates: outdated · points to G03-G08 (2022-03-02 to 2025-01-10)*

The copyright line says 2022; the current template says 2026. The year is updated by the editor, so this is only a hint: 2022 was the template's year in G03-G08 (2022-03-02 to 2025-01-10).

Evidence:
- ofj-template.tex:62: `\copyrightinfo{2022}{The Authors. This work is an open access article under the {\color{blue}{\href{https://creativecommons.org/licenses/by-sa/4.0/}{CC BY-SA 4.`

Template change: copyright year 2022 → 2024 on 2025-01-11 (PR #42) and → 2026 on 2026-01-02 (commit 66b2f6a)

#### SRC08: \OF defined with a hard space (pre-2023 template)

*strong signal · indicates: outdated · points to G01-G07 (2021-04-28 to 2023-04-29)*

\OF ends in a hard space instead of \xspace, as in templates before 2023-02-26 (this adds a space before punctuation: 'OpenFOAM® ,').

Evidence:
- ofj-template.tex:64: `\newcommand{\OF}[0]{OpenFOAM\textsuperscript{\textregistered} }`

Template change: 2023-02-26, PR #39: \OF ends in \xspace instead of a hard space

Suggested note to the authors: Please prepare the manuscript with the current version of the OFJ LaTeX template.

#### SRC11: Line numbers / double spacing always on

*medium signal · indicates: outdated · points to G01-G06 (2021-04-28 to 2023-02-07)*

\linenumbers or \doublespacing is used outside the review-mode condition, as in templates before 2023-01-30 (line numbers) and 2022-12-27 (double spacing).

Evidence:
- ofj-template.tex:78: `\doublespacing`
- ofj-template.tex:140: `\linenumbers`

Template change: 2022-12-27, PR #12: double spacing only in review mode; 2023-01-30, PR #25: line numbers only in review mode

Suggested note to the authors: Please prepare the manuscript with the current version of the OFJ LaTeX template.

#### SRC14: Footnote symbols (footmisc[symbol])

*strong signal · indicates: outdated · points to G02-G05 (2021-08-30 to 2023-01-29)*

footmisc is loaded with the option 'symbol', as in templates from 2021-09-06 to 2022-11-07; since then footnotes are numbered.

Evidence:
- ofj-template.tex:49: `\usepackage[symbol]{footmisc}`

Template change: 2022-11-08, PR #10: numbered footnotes instead of symbols

Suggested note to the authors: Please prepare the manuscript with the current version of the OFJ LaTeX template.

### Supporting evidence / for information (3)

- **CLS00** amsart.cls: template version G01-G11 (2021-04-28 to today) → G01-G11 (2021-04-28 to today) (`amsart.cls`)
- **CLS00** finiteVolumeNotation.sty: template version G01-G11 (2021-04-28 to today) → G01-G11 (2021-04-28 to today) (`finiteVolumeNotation.sty`)
- **CLS00** jams-l.cls: template version G01-G11 (2021-04-28 to today) → G01-G11 (2021-04-28 to today) (`jams-l.cls`)

## Notes

- Only figure PDFs or the journal logo were found in the folder; no manuscript PDF. Use --pdf to name it.

## Input

| | |
|---|---|
| Checked | LaTeX sources only |
| Given path | template_G04_029028a |
| Main .tex file | ofj-template.tex |
| .tex files | 1 |
| Other PDFs (figures etc.) | 1 |

## LaTeX sources

| | |
|---|---|
| Document class | ofj |
| Files in the document | ofj-template.tex |
| Template support files shipped | ofj.cls, ofjart.cls, amsart.cls, jams-l.cls, orcidlink.sty, tensorNotation.sty, finiteVolumeNotation.sty |

## Template

| | |
|---|---|
| Template repository | https://github.com/OpenFOAM-Journal/paperLatexTemplate.git |
| Compared against | master at cd2b7f2 (2026-03-31) Merge pull request #50 from jmnobrega/master |
| Template copy | cache, fetched 2026-11-05 11:49 UTC |
| Current generation | G11 (since 2026-03-31): \ref conventions |
| Fingerprint catalogue covers | cd2b7f2 |

---
ofj-check 0.1.0, 2026-11-05 12:23 UTC. Template generations and fingerprints: docs/FINGERPRINTS.md.

# OFJ template check: template_G10_66b2f6a

**Verdict: Older template, closest to G10 'Copyright 2026' (matches G10 (2026-01-02 to 2026-03-30); confidence: high)**

6 finding(s) show that the current template (G11, since 2026-03-31) was not used. The submission matches G10 (2026-01-02 to 2026-03-30) best.

Triggered by:

- CLS11: Unedited template example file ofj-template.tex
- CLS11: Unedited template example file parts/conclusion.tex
- CLS11: Unedited template example file parts/introduction.tex
- CLS11: Unedited template example file parts/section.tex
- SRC02: Preamble defines the \autoref names Tab./Fig./Eqn.
- SRC03: Cross-references made with \autoref (7x)

Also:

- Template placeholders or example content left: Unedited template example file parts/abstract.tex; Unedited template example file parts/acknowledgements.tex; Template placeholders left in the sources (14).

### Suggested message to the authors

> Dear authors,
>
> your submission was checked against the current OpenFOAM Journal LaTeX template (version of 2026-03-31, https://github.com/OpenFOAM-Journal/paperLatexTemplate). Please address the following points:
>
> - Please replace the template's example content with your own.
> - Please refer to equations, tables, figures and listings as Eqn.~\ref{...}, Tab.~\ref{...}, Fig.~\ref{...} and Lst.~\ref{...}, as in the current template.
> - Please replace all example content of the template.

## Details: what was found

### Template conventions not followed (9)

#### CLS11: Unedited template example file ofj-template.tex

*strong signal · indicates: outdated · points to G10 (2026-01-02 to 2026-03-30)*

ofj-template.tex is the template's example file ofj-template.tex, unchanged (on master from 2026-01-02 until 2026-03-31), and it is part of the document.

Evidence:
- ofj-template.tex: `identical to template ofj-template.tex`

Suggested note to the authors: Please replace the template's example content with your own.

#### CLS11: Unedited template example file parts/abstract.tex

*strong signal · indicates: placeholder · points to G06-G11 (2023-01-30 to today)*

parts/abstract.tex is the template's example file parts/abstract.tex, unchanged (on master from 2023-01-30, still current), and it is part of the document.

Evidence:
- parts/abstract.tex: `identical to template parts/abstract.tex`

Suggested note to the authors: Please replace the template's example content with your own.

#### CLS11: Unedited template example file parts/acknowledgements.tex

*strong signal · indicates: placeholder · points to G06-G11 (2023-01-30 to today)*

parts/acknowledgements.tex is the template's example file parts/acknowledgements.tex, unchanged (on master from 2023-01-30, still current), and it is part of the document.

Evidence:
- parts/acknowledgements.tex: `identical to template parts/acknowledgements.tex`

Suggested note to the authors: Please replace the template's example content with your own.

#### CLS11: Unedited template example file parts/conclusion.tex

*strong signal · indicates: outdated · points to G09-G10 (2025-01-11 to 2026-03-30)*

parts/conclusion.tex is the template's example file parts/conclusion.tex, unchanged (on master from 2025-01-11 until 2026-03-31), and it is part of the document.

Evidence:
- parts/conclusion.tex: `identical to template parts/conclusion.tex`

Suggested note to the authors: Please replace the template's example content with your own.

#### CLS11: Unedited template example file parts/introduction.tex

*strong signal · indicates: outdated · points to G09-G10 (2025-01-11 to 2026-03-30)*

parts/introduction.tex is the template's example file parts/introduction.tex, unchanged (on master from 2025-01-11 until 2026-03-31), and it is part of the document.

Evidence:
- parts/introduction.tex: `identical to template parts/introduction.tex`

Suggested note to the authors: Please replace the template's example content with your own.

#### CLS11: Unedited template example file parts/section.tex

*strong signal · indicates: outdated · points to G09-G10 (2025-01-11 to 2026-03-30)*

parts/section.tex is the template's example file parts/section.tex, unchanged (on master from 2025-01-11 until 2026-03-31), and it is part of the document.

Evidence:
- parts/section.tex: `identical to template parts/section.tex`

Suggested note to the authors: Please replace the template's example content with your own.

#### SRC02: Preamble defines the \autoref names Tab./Fig./Eqn.

*strong signal · indicates: outdated · points to G07-G10 (2023-02-08 to 2026-03-30)*

The preamble sets \tableautorefname, \figureautorefname or \equationautorefname. The template did this from 2023-02-25 until 2026-03-31; the current template no longer uses \autoref.

Evidence:
- ofj-template.tex:60: `\def\tableautorefname{Tab.}`
- ofj-template.tex:61: `\def\figureautorefname{Fig.}`
- ofj-template.tex:62: `\def\equationautorefname{Eqn.}`

Template change: 2026-03-31, PR #50: \autoref and the names Tab./Fig./Eqn. were replaced by Eqn.~\ref, Tab.~\ref, Fig.~\ref and Lst.~\ref

Suggested note to the authors: Please refer to equations, tables, figures and listings as Eqn.~\ref{...}, Tab.~\ref{...}, Fig.~\ref{...} and Lst.~\ref{...}, as in the current template.

#### SRC03: Cross-references made with \autoref (7x)

*strong signal · indicates: outdated · points to G05-G10 (2022-11-08 to 2026-03-30)*

The text refers to equations, tables or figures with \autoref, as the template did from 2022-12-27 until 2026-03-31. The current template writes Eqn.~\ref{...}, Tab.~\ref{...}, Fig.~\ref{...} and Lst.~\ref{...}.

Evidence:
- parts/introduction.tex:18: `Herein, $\Q=\Q(\xt)$ is an arbitrary general intensive physical quantity, e.g., a fluid property (scalar or tensor of any rank). Thus, \autoref{eq:genTransEq} i`
- parts/introduction.tex:31: `Besides providing \OF code itself, spatial and temporal discretisation of \autoref{eq:genTransEq} can also be described in a precise and concise manner using th`
- parts/section.tex:3: `Text in this section. Here is an example figure (\autoref{fig:example}).`
- parts/conclusion.tex:3: `This is a conclusion. Notice how equations, tables and figures are referred to in the text as \autoref{eq:genTransEq}, \autoref{tab:FiniteVolumeNotation} and \a`

Template change: 2022-12-27, PR #17: \autoref introduced; 2023-02-25, PR #37: its names set to Tab./Fig./Eqn.; 2026-03-31, PR #50: replaced by Eqn.~\ref etc.

Suggested note to the authors: Please refer to equations, tables, figures and listings as Eqn.~\ref{...}, Tab.~\ref{...}, Fig.~\ref{...} and Lst.~\ref{...}, as in the current template.

#### PLC01: Template placeholders left in the sources (14)

*strong signal · indicates: placeholder*

Example content of the template is still present (in the typeset text, not in comments): OpenFOAM version placeholder 'v20xx'; repository placeholder 'https://github.com/xxx'; example author names; example address / e-mail; example ORCID; example abstract / introduction text; example introduction text; example section title; example title; example acknowledgements; example conclusion; example CRediT author contributions; example caption / text; article type not set in the Makefile. Items inside the review-mode branch are hidden in review builds but appear in the final version.

Evidence:
- ofj-template.tex:84: `OpenFOAM version placeholder 'v20xx': \OpenFOAMversions{\OF v20xx}`
- ofj-template.tex:91: `repository placeholder 'https://github.com/xxx': \Repository{https://github.com/xxx}`
- ofj-template.tex:132: `example author names: \author[M. Jersey]{Maria Jersey$^{1,*}$\orcidlink{0000-1234-5678-0000}}`
- ofj-template.tex:133: `example address / e-mail: \address{$^1$Address1}`
- ofj-template.tex:132: `example ORCID: \author[M. Jersey]{Maria Jersey$^{1,*}$\orcidlink{0000-1234-5678-0000}}`
- parts/abstract.tex:3: `example abstract / introduction text: This is the place for an abstract.`
- parts/introduction.tex:13: `example introduction text: We shall consider the specific transport property $\Q$ and note that its spatial and temporal variation is governed by a`
- parts/section.tex:1: `example section title: \section{Theoretical backgroud}`
- ofj-template.tex:113: `example title: \title[\OF Journal Publication  - Use Title Case]{\OF Journal Publication - Use Title Case}`
- parts/acknowledgements.tex:3: `example acknowledgements: \noindent This is an example acknowledgements section and should only be included !after! the review process and before `
- parts/conclusion.tex:3: `example conclusion: This is a conclusion. Notice how equations, tables and figures are referred to in the text as \autoref{eq:genTransEq}, \`
- ofj-template.tex:189: `example CRediT author contributions: Conceptualisation, J.S.;`
- parts/section.tex:3: `example caption / text: Text in this section. Here is an example figure (\autoref{fig:example}).`
- Makefile:5: `TYPE     = SetTypeInMakefile`

Suggested note to the authors: Please replace all example content of the template.

### Supporting evidence / for information (16)

- **CLS00** amsart.cls: template version G01-G11 (2021-04-28 to today) → G01-G11 (2021-04-28 to today) (`amsart.cls`)
- **CLS00** finiteVolumeNotation.sty: template version G01-G11 (2021-04-28 to today) → G01-G11 (2021-04-28 to today) (`finiteVolumeNotation.sty`)
- **CLS00** jams-l.cls: template version G01-G11 (2021-04-28 to today) → G01-G11 (2021-04-28 to today) (`jams-l.cls`)
- **CLS00** Makefile: template version G06-G11 (2023-01-30 to today) → G06-G11 (2023-01-30 to today) (`Makefile`)
- **CLS00** ofj-template-review.tex: template version G05-G11 (2022-11-08 to today) → G05-G11 (2022-11-08 to today) (`ofj-template-review.tex`)
- **CLS00** ofj.cls: template version G07-G11 (2023-02-08 to today) → G07-G11 (2023-02-08 to today) (`ofj.cls`)
- **CLS00** ofjart.cls: template version G07-G11 (2023-02-08 to today) → G07-G11 (2023-02-08 to today) (`ofjart.cls`)
- **CLS00** orcidlink.sty: template version G07-G11 (2023-02-08 to today) → G07-G11 (2023-02-08 to today) (`orcidlink.sty`)
- **CLS00** tensorNotation.sty: template version G05-G11 (2022-11-08 to today) → G05-G11 (2022-11-08 to today) (`tensorNotation.sty`)
- **SRC07** Copyright year 2026 → G10-G11 (2026-01-02 to today) (`ofj-template.tex:72`)
- **SRC08** \OF defined with \xspace → G07-G11 (2023-02-08 to today) (`ofj-template.tex:74`)
- **SRC09** hyperref loaded in the main preamble → G07-G11 (2023-02-08 to today) (`ofj-template.tex:57`)
- **SRC10** Review mode (\ifdefined\review) present → G05-G11 (2022-11-08 to today) (`ofj-template.tex:87`)
- **SRC14** footmisc[hang,flushmargin] → G06-G11 (2023-01-30 to today) (`ofj-template.tex:50`)
- **SRC17** Template comment on \OpenFOAMversions (2023+) → G07-G11 (2023-02-08 to today) (`ofj-template.tex:81`)
- **SRC18** Example title of the 2025+ template → G09-G11 (2025-01-11 to today) (`ofj-template.tex:113`)

## Notes

- Only figure PDFs or the journal logo were found in the folder; no manuscript PDF. Use --pdf to name it.

## Input

| | |
|---|---|
| Checked | LaTeX sources only |
| Given path | template_G10_66b2f6a |
| Main .tex file | ofj-template.tex |
| .tex files | 9 |
| Other PDFs (figures etc.) | 1 |

## LaTeX sources

| | |
|---|---|
| Document class | ofj |
| Files in the document | ofj-template.tex, parts/abstract.tex, parts/introduction.tex, parts/section.tex, parts/conclusion.tex, parts/acknowledgements.tex |
| Template support files shipped | ofj.cls, ofjart.cls, amsart.cls, jams-l.cls, orcidlink.sty, tensorNotation.sty, finiteVolumeNotation.sty, Makefile |

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

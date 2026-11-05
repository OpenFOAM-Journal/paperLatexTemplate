# OFJ template check: template_G11_cd2b7f2

**Verdict: Current template (matches G11 (2026-03-31 to today); confidence: high)**

Every older generation is ruled out by clear evidence.

Also:

- Template placeholders or example content left: Unedited template example file ofj-template.tex; Unedited template example file parts/abstract.tex; Unedited template example file parts/acknowledgements.tex; Unedited template example file parts/conclusion.tex.

### Suggested message to the authors

> Dear authors,
>
> your submission was checked against the current OpenFOAM Journal LaTeX template (version of 2026-03-31, https://github.com/OpenFOAM-Journal/paperLatexTemplate). Please address the following points:
>
> - Please replace the template's example content with your own.
> - Please replace all example content of the template.

## Details: what was found

### Template conventions not followed (7)

#### CLS11: Unedited template example file ofj-template.tex

*strong signal · indicates: placeholder · points to G11 (2026-03-31 to today)*

ofj-template.tex is the template's example file ofj-template.tex, unchanged (on master from 2026-03-31, still current), and it is part of the document.

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

*strong signal · indicates: placeholder · points to G11 (2026-03-31 to today)*

parts/conclusion.tex is the template's example file parts/conclusion.tex, unchanged (on master from 2026-03-31, still current), and it is part of the document.

Evidence:
- parts/conclusion.tex: `identical to template parts/conclusion.tex`

Suggested note to the authors: Please replace the template's example content with your own.

#### CLS11: Unedited template example file parts/introduction.tex

*strong signal · indicates: placeholder · points to G11 (2026-03-31 to today)*

parts/introduction.tex is the template's example file parts/introduction.tex, unchanged (on master from 2026-03-31, still current), and it is part of the document.

Evidence:
- parts/introduction.tex: `identical to template parts/introduction.tex`

Suggested note to the authors: Please replace the template's example content with your own.

#### CLS11: Unedited template example file parts/section.tex

*strong signal · indicates: placeholder · points to G11 (2026-03-31 to today)*

parts/section.tex is the template's example file parts/section.tex, unchanged (on master from 2026-03-31, still current), and it is part of the document.

Evidence:
- parts/section.tex: `identical to template parts/section.tex`

Suggested note to the authors: Please replace the template's example content with your own.

#### PLC01: Template placeholders left in the sources (14)

*strong signal · indicates: placeholder*

Example content of the template is still present (in the typeset text, not in comments): OpenFOAM version placeholder 'v20xx'; repository placeholder 'https://github.com/xxx'; example author names; example address / e-mail; example ORCID; example abstract / introduction text; example introduction text; example section title; example title; example acknowledgements; example conclusion; example CRediT author contributions; example caption / text; article type not set in the Makefile. Items inside the review-mode branch are hidden in review builds but appear in the final version.

Evidence:
- ofj-template.tex:79: `OpenFOAM version placeholder 'v20xx': \OpenFOAMversions{\OF v20xx}`
- ofj-template.tex:86: `repository placeholder 'https://github.com/xxx': \Repository{https://github.com/xxx}`
- ofj-template.tex:127: `example author names: \author[M. Jersey]{Maria Jersey$^{1,*}$\orcidlink{0000-1234-5678-0000}}`
- ofj-template.tex:128: `example address / e-mail: \address{$^1$Address1}`
- ofj-template.tex:127: `example ORCID: \author[M. Jersey]{Maria Jersey$^{1,*}$\orcidlink{0000-1234-5678-0000}}`
- parts/abstract.tex:3: `example abstract / introduction text: This is the place for an abstract.`
- parts/introduction.tex:13: `example introduction text: We shall consider the specific transport property $\Q$ and note that its spatial and temporal variation is governed by a`
- parts/section.tex:1: `example section title: \section{Theoretical backgroud}`
- ofj-template.tex:108: `example title: \title[\OF Journal Publication  - Use Title Case]{\OF Journal Publication - Use Title Case}`
- parts/acknowledgements.tex:3: `example acknowledgements: \noindent This is an example acknowledgements section and should only be included !after! the review process and before `
- parts/conclusion.tex:3: `example conclusion: This is a conclusion. Notice how equations, tables and figures are referred to in the text as Eqn.~\ref{eq:genTransEq}, `
- ofj-template.tex:184: `example CRediT author contributions: Conceptualisation, J.S.;`
- parts/introduction.tex:22: `example caption / text: \begin{lstlisting}[emph={ddt,div,laplacian}, caption={code listing caption}, label=lstlisting:code]`
- Makefile:5: `TYPE     = SetTypeInMakefile`

Suggested note to the authors: Please replace all example content of the template.

### Supporting evidence / for information (18)

- **CLS00** amsart.cls: template version G01-G11 (2021-04-28 to today) → G01-G11 (2021-04-28 to today) (`amsart.cls`)
- **CLS00** finiteVolumeNotation.sty: template version G01-G11 (2021-04-28 to today) → G01-G11 (2021-04-28 to today) (`finiteVolumeNotation.sty`)
- **CLS00** jams-l.cls: template version G01-G11 (2021-04-28 to today) → G01-G11 (2021-04-28 to today) (`jams-l.cls`)
- **CLS00** Makefile: template version G06-G11 (2023-01-30 to today) → G06-G11 (2023-01-30 to today) (`Makefile`)
- **CLS00** ofj-template-review.tex: template version G05-G11 (2022-11-08 to today) → G05-G11 (2022-11-08 to today) (`ofj-template-review.tex`)
- **CLS00** ofj.cls: template version G07-G11 (2023-02-08 to today) → G07-G11 (2023-02-08 to today) (`ofj.cls`)
- **CLS00** ofjart.cls: template version G07-G11 (2023-02-08 to today) → G07-G11 (2023-02-08 to today) (`ofjart.cls`)
- **CLS00** orcidlink.sty: template version G07-G11 (2023-02-08 to today) → G07-G11 (2023-02-08 to today) (`orcidlink.sty`)
- **CLS00** tensorNotation.sty: template version G05-G11 (2022-11-08 to today) → G05-G11 (2022-11-08 to today) (`tensorNotation.sty`)
- **SRC02** No \autoref names in the preamble (`ofj-template.tex:57`)
- **SRC04** Current reference convention used (7x) → G11 (2026-03-31 to today) (`parts/introduction.tex:18`)
- **SRC07** Copyright year 2026 → G10-G11 (2026-01-02 to today) (`ofj-template.tex:67`)
- **SRC08** \OF defined with \xspace → G07-G11 (2023-02-08 to today) (`ofj-template.tex:69`)
- **SRC09** hyperref loaded in the main preamble → G07-G11 (2023-02-08 to today) (`ofj-template.tex:57`)
- **SRC10** Review mode (\ifdefined\review) present → G05-G11 (2022-11-08 to today) (`ofj-template.tex:82`)
- **SRC14** footmisc[hang,flushmargin] → G06-G11 (2023-01-30 to today) (`ofj-template.tex:50`)
- **SRC17** Template comment on \OpenFOAMversions (2023+) → G07-G11 (2023-02-08 to today) (`ofj-template.tex:76`)
- **SRC18** Example title of the 2025+ template → G09-G11 (2025-01-11 to today) (`ofj-template.tex:108`)

## Notes

- Only figure PDFs or the journal logo were found in the folder; no manuscript PDF. Use --pdf to name it.

## Input

| | |
|---|---|
| Checked | LaTeX sources only |
| Given path | template_G11_cd2b7f2 |
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

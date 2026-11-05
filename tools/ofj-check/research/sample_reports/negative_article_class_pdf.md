# OFJ template check: article_class_same_content.pdf

**Verdict: Not made with the OFJ template (confidence: high)**

Only 0 of the 5 elements that every OFJ template prints on the first page were found (none). The PDF was almost certainly not made with the OFJ template.

Triggered by:

- NOT02: Title page of the OFJ template not found

### Suggested message to the authors

> Dear authors,
>
> your submission was checked against the current OpenFOAM Journal LaTeX template (version of 2026-03-31, https://github.com/OpenFOAM-Journal/paperLatexTemplate). Please address the following points:
>
> - Please prepare the manuscript with the OFJ LaTeX template.

## Details: what was found

### Required by the current template (1)

#### NOT02: Title page of the OFJ template not found

*strong signal · indicates: not-template*

Only 0 of the 5 elements that every OFJ template prints on the first page were found (none). The PDF was almost certainly not made with the OFJ template.

Evidence:
- PDF p. 1: `missing: journal header (Volume ... / ISSN)`
- PDF p. 1: `missing: title-page footnote (Corresponding author / Received)`
- PDF p. 1: `missing: copyright line`
- PDF p. 1: `missing: metadata block (DOI / Repository)`
- PDF p. 1: `missing: page and text block of the template`
- PDF: `page size A4 (595.3 x 841.9 pt), body font CMR10`

Suggested note to the authors: Please prepare the manuscript with the OFJ LaTeX template.

## Input

| | |
|---|---|
| Checked | PDF only |
| Given path | research\negative_samples\article_class_same_content.pdf |

## PDF

| | |
|---|---|
| Pages | 3 |
| Page size | A4 (595.3 x 841.9 pt) |
| Producer | pdfTeX-1.40.25 |
| Creator | LaTeX with hyperref |
| Body font | CMR10 |
| Margin line numbers (review build) | no |

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

# Reference PDF inspection


## article_class_same_content.pdf

- pages: 3; size: 595.3 x 841.9 pt
- metadata: {'Producer': 'pdfTeX-1.40.25', 'Author': '', 'Title': '', 'Subject': '', 'Creator': 'LaTeX with hyperref', 'Keywords': '', 'CreationDate': "D:20261104082335+01'00'", 'ModDate': "D:20261104082335+01'00'", 'Trapped': 'False', 'PTEX.Fullbanner': 'This is pdfTeX, Version 3.141592653-2.6-1.40.25 (TeX Live 2023/Debian) kpathsea version 6.3.5'}
- fonts: {'CMR10': 1332, 'CMTI10': 72, 'CMBX12': 58, 'CMR17': 40, 'CMR12': 37, 'CMMI10': 25, 'CMSY10': 15, 'CMMI8': 14, 'CMBX10': 12, 'CMMI6': 12, 'CMR6': 4, 'CMR8': 3, 'unknown': 3, 'CMEX10': 2, 'CMBX6': 1}
- 'Introduction' heading font: CMBX12 14.3pt
- 'Abstract' label font: CMBX10 10.0pt
- 'Figure' caption font: CMR10 10.9pt
- 'Table' caption font: CMR10 10.9pt
- link annotations: ['1', '1', '1', '1', '1', '1', '1', '1']

<details><summary>page 1 text</summary>

```
An OpenFOAM Paper Written Without the
Template
Maria Jersey and John Smith
November 4, 2026
Abstract
This is the place for an abstract.
1 Introduction
This is the place for introduction.
1.1 Subsection
Example text:
Weshallconsiderthespecifictransportpropertyϕandnotethatitsspa-
tial and temporal variation is governed by a second-order partial differential
equation (PDE), viz.
∂ ·
(ρϕ)+∇ (ρϕU)−Γ ∇2ϕ−S (ϕ) = 0. (1)
ϕ ϕ
∂t
Herein, ϕ = ϕ(x, t) is an arbitrary general intensive physical quantity, e.g.,
afluidproperty(scalarortensorofanyrank). Thus, Eqn.1isoftenreferred
to as a generic transport equation.
OpenFOAMfi (Open Field Operation And Manipulation) is a flexible
and mature C++ Class Library for Computational Continuum Mechan-
ics (CCM) and Multiphysics. Its Object-Oriented-Programming (OOP)
paradigm enables to mimic data types and basic operations of CCM us-
ing top-level syntax as close as possible to the conventional mathematical
notation for tensors and partial differential equations, as shown in Lst. 1.
Listing 1: code listing caption
solve
(
fvm:: ddt(rho ,Phi)
+ fvm:: div(phi , Phi)
=
fvm:: laplacian(Gamma, Phi)
1
```
</details>

<details><summary>page 2 first lines</summary>

```
Table 1: Finite Volume Notation
implicit differential operators
∂[ρϕ]
rate of change J K
```
</details>

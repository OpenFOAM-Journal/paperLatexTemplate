# OpenFOAM Journal: LaTeX Template

This is the official LaTeX Template for the [OpenFOAM Journal](https://journal.openfoam.com/).

## Building

On a Linux system, you can build the template from your terminal:

```shell
make
```

This will build `ofj-template.pdf` from `ofj-template.tex` once, using [latexmk](https://www.ctan.org/pkg/latexmk/).

While writing your publication, you may prefer to continuously build it with

```shell
make continuously
```

which passes the `-pvc` flag to latexmk.

To prepare a review version of your manuscript, you can run

```shell
make review
```

which enables double line spacing and excludes some identifying information (authors and affiliations, repository, acknowledgements). In case you rename `ofj-template.tex`, you need to also adjust the name of the file included in `ofj-template-review.tex`.

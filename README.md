# OpenFOAM Journal: LaTeX Template

This is the official LaTeX Template for the [OpenFOAM Journal](https://journal.openfoam.com/).

## Building

On a Linux system, you can build the template from your terminal:

```shell
make
```

This will build `ofj-template.pdf` from `ofj-template.tex` once, using [latexmk](https://www.ctan.org/pkg/latexmk/).

Note that `ofj-template.pdf` (as long as all PDF files) are ignored by Git in this repository (see `.gitignore`). Include any such PDF files explicitly, if needed, with `git add -f file.pdf`.

While writing your publication, you may prefer to continuously build it with

```shell
make continuously
```

which passes the `-pvc` flag to latexmk.

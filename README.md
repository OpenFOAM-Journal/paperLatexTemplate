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

Set your project name and type in the beginning of the Makefile (see comments).

=======
## Review Version

To prepare a review version of your manuscript, you can run

```shell
make review
```

which enables double line spacing and excludes some identifying information (authors and affiliations, repository, acknowledgements). In case you rename `ofj-template.tex`, you need to also adjust the name of the file included in `ofj-template-review.tex`.

=======
## Contributing

Feel free to [open an issue](https://github.com/OpenFOAM-Journal/paperLatexTemplate/issues) explaining any problems or feature requests. Ideally, it would really help if you could directly [propose changes in a pull request](https://github.com/OpenFOAM-Journal/paperLatexTemplate/pulls) from your fork ([read how](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork)). Describe your contribution in detail in the PR and try to use concise and descriptive commit messages. To keep the history clean, squash multiple related commits into one and update your branch with a force-push.

Your PR will be checked automatically with [GitHub Actions](https://docs.github.com/en/actions) and we can only accept contributions that pass these checks. At the bottom of your PR, you will find the status of these checks. If a red ❌ appears next to any of these checks, click on it to learn more. In the "Summary" view, you can download the LaTeX log files to figure out more. If you only see ✅, then the template builds successfully and you can download the resulting PDF files as build artifcats from the bottom of the "Summary" view.

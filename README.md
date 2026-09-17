# OpenFOAM Journal: LaTeX Template

This is the official LaTeX Template for the [OpenFOAM Journal](https://journal.openfoam.com/).

## Structure

Add your content in the following files and directories:

- `parts/`: Body of the paper
  - Apart from the existing files, add files for more sections here.
- `figures/`: Your figures (create subdirectories, if needed)
- `ofj-template.tex`: Add title, authors, and include files from `parts/`. Include any additional packages here.

The file `examples.tex` include some commonly used LaTeX snippets.

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

## Review Version

To prepare a review version of your manuscript, you can run

```shell
make review
```

which enables double line spacing and excludes some identifying information (authors and affiliations, repository, acknowledgements). In case you rename `ofj-template.tex`, you need to also adjust the name of the file included in `ofj-template-review.tex`.

The template includes a declaration on the use of artificial intelligence in `parts/aiDeclaration.tex`. This declaration is mandatory for all submissions, including when no AI tools were used. It is deliberately retained in the review version, as reviewers need it to assess the manuscript and the accompanying code, so keep it free of any information that identifies you. See the guidance comments in the file, and the journal's author guidelines, for what to declare.

## Checking Style and Conventions

The template ships with `checkStyle.py`, a dependency-free script that checks a
manuscript against the conventions described in this README and in the template
files. Run it from the manuscript directory with

```shell
make check
```

or directly, for example

```shell
python3 checkStyle.py --strict          # treat warnings as errors
python3 checkStyle.py --check-log       # also parse the LaTeX .log files
python3 checkStyle.py --list-rules      # print the rule table
```

It reports two severities. **Errors** are unambiguous: leftover placeholders, a
missing declaration on the use of artificial intelligence, a cross-reference
written as `Figure~\ref{}` instead of `Fig.~\ref{}`, author information that
would leak into the double-blind review version. **Warnings** encode a
preference that may legitimately not apply to your manuscript, such as spelling
variants or float placement; read them and use your judgement. The script exits
non-zero if there is at least one error.

Every rule is documented, with the place in the template it is derived from, in
the comment block at the top of `checkStyle.py`. If a rule is wrong or fires on
something legitimate, silence it for one line with

```latex
Figure~\ref{fig:example} % ofj-check: ignore REF001
```

or for a whole run with `--ignore REF001` (a group prefix such as `--ignore REF`
also works), and please
[open an issue](https://github.com/OpenFOAM-Journal/paperLatexTemplate/issues).

Note that running the check on the *unmodified* template reports a number of
errors by design: the placeholder title, authors, repository and body text are
exactly what the script is meant to catch.

## Contributing

Feel free to [open an issue](https://github.com/OpenFOAM-Journal/paperLatexTemplate/issues) explaining any problems or feature requests. Ideally, it would really help if you could directly [propose changes in a pull request](https://github.com/OpenFOAM-Journal/paperLatexTemplate/pulls) from your fork ([read how](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork)). Describe your contribution in detail in the PR and try to use concise and descriptive commit messages. To keep the history clean, squash multiple related commits into one and update your branch with a force-push.

Your PR will be checked automatically with [GitHub Actions](https://docs.github.com/en/actions) and we can only accept contributions that pass these checks. At the bottom of your PR, you will find the status of these checks. If a red ❌ appears next to any of these checks, click on it to learn more. In the "Summary" view, you can download the LaTeX log files to figure out more. If you only see ✅, then the template builds successfully and you can download the resulting PDF files as build artifcats from the bottom of the "Summary" view.

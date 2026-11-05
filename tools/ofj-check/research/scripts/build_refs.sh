#!/usr/bin/env bash
# Build the template PDF as it was at the end of each generation (reference PDFs).
# Run inside WSL.  Usage: build_refs.sh <repo> <outdir> <workdir>
set -u
REPO=$1; OUT=$2; WORK=$3
mkdir -p "$OUT" "$WORK"
# Stub only packages this TeX install lacks (texlive-science); the template
# body never uses their macros, so the layout is unaffected.
STUBS=/tmp/ofj_stubs; rm -rf "$STUBS"; mkdir -p "$STUBS"
for p in algorithmic stmaryrd; do
  if [ -z "$(kpsewhich $p.sty)" ]; then
    echo "\\ProvidesPackage{$p}[stub]" > "$STUBS/$p.sty"
    echo "WARNING: $p.sty missing, using a stub"
  fi
done
export TEXINPUTS=".:$STUBS//:"
ERAS=${ERAS:-"G01_2021-07-27:eb037cd G02_2022-01-20:b5edfcf G03_2022-03-02:f532bdd G04a_2022-05-04:48b3c92 G04_2022-05-18:029028a G05_2022-12-27:e88d246 G06_2023-01-30:f004fab G07_2023-02-26:0fc4ddf G08_2023-04-30:4f17267 G09_2025-04-10:e489934 G10_2026-01-02:66b2f6a G11_2026-03-31:cd2b7f2"}
for e in $ERAS; do
  era=${e%%:*}; sha=${e##*:}
  dir="$WORK/$era"; rm -rf "$dir"; mkdir -p "$dir"
  git -C "$REPO" archive "$sha" | tar -x -C "$dir"
  for mode in final review; do
    main=ofj-template.tex
    if [ $mode = review ]; then
      [ -f "$dir/ofj-template-review.tex" ] || continue
      main=ofj-template-review.tex
    fi
    job="${era}_${sha}_${mode}"
    ( cd "$dir" &&
      pdflatex -interaction=batchmode -jobname="$job" "$main" >/dev/null 2>&1
      bibtex "$job" >/dev/null 2>&1
      for i in 1 2; do
        pdflatex -interaction=batchmode -jobname="$job" "$main" >/dev/null 2>&1; done )
    if [ -f "$dir/$job.pdf" ]; then
      cp "$dir/$job.pdf" "$OUT/"; status=ok
    else
      status=FAILED
    fi
    errs=$(grep -c '^!' "$dir/$job.log" 2>/dev/null)
    echo "$job $status errors=$errs"
    grep -m3 -A1 '^!' "$dir/$job.log" 2>/dev/null | sed 's/^/    /'
  done
done

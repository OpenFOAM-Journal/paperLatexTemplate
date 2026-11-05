#!/usr/bin/env bash
# Prototype of the proposed template version marker: build the current template with it.
# Usage: build_version_marker_prototype.sh <clone of paperLatexTemplate> <output folder>
set -u
REPO=$(cd "$1" && pwd); OUT=$(cd "$2" && pwd); W=/tmp/ofj_marker; rm -rf $W; mkdir -p $W
git -C "$REPO" archive cd2b7f2 | tar -x -C $W
cd $W
# the proposed lines, right after \ProvidesClass in ofj.cls
python3 - <<'PY'
p = "ofj.cls"
t = open(p).read()
old = "\\ProvidesClass{ofj}[2020/09/23 v1.01 OpenFOAM Journal article documentclass]"
new = ("\\ProvidesClass{ofj}[2027/01/15 v2027-01-15 OpenFOAM Journal article documentclass]\n"
       "% Template version: the release date of the template (YYYY-MM-DD). Do not change.\n"
       "\\newcommand{\\ofjtemplateversion}{2027-01-15}\n"
       "\\AtBeginDocument{\\@ifpackageloaded{hyperref}%\n"
       "  {\\hypersetup{pdfinfo={OFJTemplateVersion={\\ofjtemplateversion}}}}{}}")
assert old in t
open(p, "w").write(t.replace(old, new))
PY
pdflatex -interaction=batchmode -jobname=marker_review ofj-template-review.tex >/dev/null
pdflatex -interaction=batchmode -jobname=marker_review ofj-template-review.tex >/dev/null
grep -c "^!" marker_review.log
cp marker_review.pdf "$OUT/"
mkdir -p "$OUT/marker_src" && cp -r . "$OUT/marker_src/"
python3 - <<'PY'
import re
data = open("marker_review.pdf", "rb").read()
print("Info entry:", re.findall(rb"/OFJTemplateVersion\s*\([^)]*\)", data)[:1])
PY

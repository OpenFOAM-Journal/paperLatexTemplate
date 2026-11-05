#!/usr/bin/env bash
# List LaTeX packages used by any template era that the local TeX install lacks.
cd /tmp/ofj_refs || exit 1
cat */*.tex */*.cls */*.sty 2>/dev/null \
  | grep -oE '\\(usepackage|RequirePackage)(\[[^]]*\])?\{[^}]*\}' \
  | sed -E 's/.*\{(.*)\}/\1/' | tr ',' '\n' | tr -d ' ' | sort -u \
  | while read -r p; do
      [ -z "$p" ] && continue
      if [ -z "$(kpsewhich "$p.sty")" ] && ! ls */"$p.sty" >/dev/null 2>&1; then
        echo "MISSING package: $p"
      fi
    done
for f in IEEEtran.bst; do [ -z "$(kpsewhich $f)" ] && echo "MISSING file: $f"; done
echo "--- installed texlive packages:"
dpkg -l | awk '/^ii +texlive/ {print "  " $2}'

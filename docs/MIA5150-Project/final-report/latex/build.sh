#!/bin/sh
# Build main.pdf in the TeX Live container (no local TeX needed). texlive:latest-medium lacks environ and
# trimspaces (needed by neurips_2026.sty), so they are installed from CTAN in the throwaway container first.
# On Overleaf, just upload main.tex, neurips_2026.sty and references.bib.
cd "$(dirname "$0")"
rm -f main.aux main.bbl main.blg main.fdb_latexmk main.fls main.out
docker run --rm -v "$PWD":/work -w /work texlive/texlive:latest-medium sh -c \
  "tlmgr install environ trimspaces >/dev/null 2>&1; latexmk -g -pdf -interaction=nonstopmode -halt-on-error main.tex >build.log 2>&1; s=\$?; chown -R $(id -u):$(id -g) /work; exit \$s"

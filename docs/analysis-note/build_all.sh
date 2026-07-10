#!/usr/bin/env bash
# Build all three audience-tiered PDFs from the shared source.
# Run on a NERSC LOGIN node (pdflatex/biber are not on the compute nodes):
#     module load texlive/2024
#     bash build_all.sh
# Each target shares preamble.tex + values.tex + technote.bib + the figure set;
# only the driver and its body differ.
set -euo pipefail
cd "$(dirname "$0")"

module load texlive/2024 2>/dev/null || true

targets=(main_note main_primer main_paper)
for t in "${targets[@]}"; do
  echo "=== building ${t}.pdf ==="
  latexmk -pdf -interaction=nonstopmode -halt-on-error "${t}.tex"
done

echo
echo "=== page counts ==="
for t in "${targets[@]}"; do
  if command -v pdfinfo >/dev/null 2>&1; then
    pages=$(pdfinfo "${t}.pdf" 2>/dev/null | awk '/^Pages:/{print $2}')
  else
    pages=$(pdftk "${t}.pdf" dump_data 2>/dev/null | awk '/NumberOfPages/{print $2}' || echo '?')
  fi
  printf '  %-14s %s pp\n' "${t}.pdf" "${pages:-?}"
done

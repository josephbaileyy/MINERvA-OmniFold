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
echo "=== struck-value containment (retracted values must reach the NOTE build only) ==="
# Runs AFTER the builds so the PDF stage has PDFs to read. A paper-bound PDF carrying a struck
# retracted number is a publication defect, not a style nit. See check_dead_containment.py for why
# this is a test rather than an \ifPAPER build flag.
#
# CONTRACT, changed 2026-08-12 on Joseph's decision: exit 0 from this stage means BOTH the source
# and PDF halves ran and passed. Every skip is fatal here. Previously a missing python3 printed
# "containment UNVERIFIED" and the build went on to exit 0, and a missing pdftotext skipped the PDF
# half inside the checker with the same result -- so the check was silently machine-dependent,
# whole on one box and half on another, with no difference in the build's status.
#
# --source-only exists in the checker and MUST NEVER be passed from here. It is for a human
# debugging without a TeX install. Adding it to this line would restore exactly the defect the
# contract change removed, and would look like a fix while doing it.
if ! command -v python3 >/dev/null 2>&1; then
  echo "  FAIL python3 not found -- containment cannot run, and an unverified build must not"
  echo "       report success. Install python3 or run the builds somewhere that has it."
  exit 1
fi
python3 check_dead_containment.py --self-test   # the regex's power test, before trusting its verdict
python3 check_dead_containment.py

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

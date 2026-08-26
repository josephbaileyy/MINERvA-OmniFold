#!/usr/bin/env bash
# Build all three audience-tiered PDFs from the shared source.
# Run on a NERSC LOGIN node (pdflatex/biber are not on the compute nodes):
#     module load texlive/2024
#     bash build_all.sh
# Each target shares preamble.tex + values.tex + technote.bib + the figure set;
# only the driver and its body differ.
#
# WHY THE BUILD STAGE PROVES ITSELF, ADDED 2026-08-19
# ---------------------------------------------------
# This script exited 0, printed all three "building" lines, and passed the containment check
# while `latexmk` said "Nothing to do" for ALL THREE targets and nothing recompiled -- the
# PDFs it validated were dated 2026-08-11 and 2026-08-15. A green run therefore proved
# nothing about current source. The three "building" lines were the giveaway in hindsight:
# they announced an INTENTION, and nothing downstream distinguished "built and passed" from
# "skipped and passed".
#
# So each target now carries a PROOF that its PDF was written by THIS run:
#
#   1. `latexmk -g` forces the rebuild, so "Nothing to do" cannot stand in for a build.
#   2. A marker file is stamped BEFORE the builds and every PDF must be strictly newer than
#      it. This is the check that actually catches the observed failure, and it is STRONGER
#      than "the PDF is newer than its sources": the stale 08-11 PDFs WERE newer than
#      sources that had not been touched since, so a sources-only comparison would have
#      passed exactly the run that went wrong. "Newer than the marker" cannot be satisfied
#      by a file this run did not write.
#   3. The PDF is also required to be newer than each of its declared sources, which catches
#      the other direction: a source edited while the build was running.
#
# Anything that fails these exits non-zero BEFORE the containment stage, because a check
# that validated a stale artifact is worse than no check -- it reports a pass nobody earned.
set -euo pipefail
cd "$(dirname "$0")"

module load texlive/2024 2>/dev/null || true

targets=(main_note main_primer main_paper)

# The sources every target genuinely depends on. Deliberately NOT "every .tex in this
# directory": a note-only body edited after the paper's build would then fail the paper,
# which is a false alarm rather than a defect. The marker check in (2) is what makes this
# list a supplement rather than the whole guarantee, so keeping it narrow costs nothing.
shared_sources=(preamble.tex values.tex technote.bib)

if ! command -v latexmk >/dev/null 2>&1; then
  echo "  FAIL latexmk not found -- no build can happen, and a run that built nothing must"
  echo "       not report success. Load the TeX module: module load texlive/2024"
  exit 1
fi

# (2) The instant every PDF must postdate. `sleep 1` removes the same-second ambiguity in
# `test -nt` on filesystems with coarse timestamps: one second, once, against a LaTeX build.
marker="$(mktemp "${TMPDIR:-/tmp}/build_all_marker.XXXXXX")"
trap 'rm -f "$marker"' EXIT INT TERM
sleep 1

for t in "${targets[@]}"; do
  echo "=== building ${t}.pdf (forced with -g, so \"Nothing to do\" cannot pass for a build) ==="
  if ! latexmk -g -pdf -interaction=nonstopmode -halt-on-error "${t}.tex"; then
    echo "  FAIL latexmk failed for ${t}.tex -- see the log above. No PDF from this target is"
    echo "       trustworthy, so the containment stage is NOT reached."
    exit 1
  fi
  if [ ! -f "${t}.pdf" ]; then
    echo "  FAIL ${t}.pdf does not exist after latexmk reported success."
    exit 1
  fi
  if [ ! "${t}.pdf" -nt "$marker" ]; then
    echo "  FAIL ${t}.pdf was NOT written by this run: it does not postdate the marker stamped"
    echo "       before the builds. latexmk most likely reported \"Nothing to do\" -- which is"
    echo "       exactly the 2026-08-19 defect: a green run over PDFs from a previous week."
    echo "       Delete ${t}.pdf and its .aux/.fls/.fdb_latexmk, then re-run."
    exit 1
  fi
  for s in "${shared_sources[@]}" "${t}.tex"; do
    if [ -e "$s" ] && [ "$s" -nt "${t}.pdf" ]; then
      echo "  FAIL ${s} is NEWER than ${t}.pdf -- the source changed after the PDF was written,"
      echo "       so this PDF does not represent current source. Re-run the build."
      exit 1
    fi
  done
  # Report what was READ, not that a build was attempted: the size and mtime are the evidence.
  echo "  OK   ${t}.pdf written by this run:"
  ls -l "${t}.pdf" | sed 's/^/       /'
done

echo
echo "=== struck-value containment (retracted values must reach the NOTE build only) ==="
# Runs AFTER the builds so the PDF stage has PDFs to read -- and, since 2026-08-19, after
# each PDF has been PROVEN to be this run's output, so a containment PASS is a statement
# about current source rather than about whatever was on disk.
# A paper-bound PDF carrying a struck retracted number is a publication defect, not a style
# nit. See check_dead_containment.py for why this is a test rather than an \ifPAPER build flag.
#
# CONTRACT, changed 2026-08-12 on Joseph's decision: exit 0 from this stage means BOTH the
# source and PDF halves ran and passed. Every skip is fatal here. Previously a missing python3
# printed "containment UNVERIFIED" and the build went on to exit 0, and a missing PDF text
# extractor skipped the PDF half inside the checker with the same result -- so the check was silently
# machine-dependent, whole on one box and half on another, with no difference in the build's
# status. The checker prefers Poppler's pdftotext and uses Ghostscript's txtwrite device as a
# strict fallback; absence or empty output from both remains fatal.
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
  # `|| true` on each pipeline: under `set -o pipefail` a missing or unreadable tool here
  # would abort the script AFTER the builds and containment had already passed, turning a
  # cosmetic stage into a failed build. The page count is information, not a gate.
  if command -v pdfinfo >/dev/null 2>&1; then
    pages=$(pdfinfo "${t}.pdf" 2>/dev/null | awk '/^Pages:/{print $2}' || true)
  else
    pages=$(pdftk "${t}.pdf" dump_data 2>/dev/null | awk '/NumberOfPages/{print $2}' || true)
  fi
  printf '  %-14s %s pp\n' "${t}.pdf" "${pages:-?}"
done

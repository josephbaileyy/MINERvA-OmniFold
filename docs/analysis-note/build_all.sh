#!/usr/bin/env bash
# Build the four audience-tiered PDFs from the shared source: the analysis note, the primer, the
# paper and (since 2026-10-12) the companion PET note; and, since 2026-10-21, the internal records
# document, which is never posted (item 7 below).
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
#
# WHY THE BUILD STAGE ALSO READS THE LOG, ADDED 2026-09-23 (KNOWN_ISSUES row 50)
# -----------------------------------------------------------------------------
# On a COLD tree at 92b2873 this script exited 0 with 93 undefined references in main_note,
# 6 in main_paper and 1 in main_primer; all resolved on a second invocation. latexmk's exit
# status does not report unresolved references, so the exit code said nothing about the `??`
# in the PDFs. (Not reproduced on a cold tree at aeb6668c with a local latexmk 4.83, which
# converged in one invocation -- so the cause is toolchain-dependent, most likely the NERSC
# texlive/2024 module. The check below does not depend on knowing which.)
#
#   4. If the final `${t}.log` records an unresolved reference or citation, latexmk is invoked
#      ONE more time -- the extra pass the cold case needed -- and if it is still unresolved the
#      build FAILS. A missing log also fails: a reference check that did not read one passed
#      nothing. The patterns are LaTeX's own reference/citation warnings; the `T1/cmtt` font
#      shape "undefined" warnings every build prints do NOT match them. TeX wraps log lines at
#      79 columns, so a long `Reference ... undefined` warning can split across two lines and
#      miss its own pattern; LaTeX's end-of-run "There were undefined references" summary is
#      the pattern that carries the check (measured 2026-09-23 with a planted \ref).
#
# DEPOSIT EXPORT AND BODY-POINTER LINT, ADDED 2026-10-21 (DECISION-20261020-joseph-refined-estimator-shorten-delta.md
# item 2: the note is to be made depositable; depositing it stays Joseph's act)
# --------------------------------------------------------------------------------------------------------------
#   5. Before any build, check_body_pointers.py fails the build if the note's BODY (everything main_note.tex inputs
#      before \appendix) prints an internal-only pointer: a tracker row, repository path, file name, digest or
#      "known-issues log" pointer. Those belong in the records document (item 7), which the body cites by tag. Its
#      self-test runs first and shows the patterns fire on a planted body pointer and stay silent on the appendix.
#   6. `bash build_all.sh --export-deposit DIR` additionally writes a comment-free, single-file source tree for
#      deposit to DIR after every gate above has passed: main_note.tex flattened by `latexpand --empty-comments`
#      (comment text removed, the line-ending `%` kept, the sources themselves untouched), the two .bib files without
#      their comment lines, and exactly the figures the note build read (from main_note.fls). The export then proves
#      itself: no comment text may remain in it, it must build, and its PDF must have the same page count and the
#      same extracted text as main_note.pdf. Without the flag nothing is exported.
#
# THE RECORDS DOCUMENT, ADDED 2026-10-21 (DECISION-20261021-joseph-da-and-note-records.md item 2: the analysis note
# posted as supplementary material is not a records ledger)
# ------------------------------------------------------------------------------------------------------------------
#   7. main_records.tex builds the internal records document: the note's former provenance appendix, its audit trail of
#      superseded values and withdrawn results, and the record parts of the release and codebase appendices, moved
#      verbatim. It is never posted and never exported. It is built LAST, after main_note, because its references into
#      the note resolve through main_note.aux (xr-hyper). It is the one build allowed to strike values; the posted note
#      is now checked as outward-facing by the containment stage. Every build's log is also read for multiply-defined
#      labels, which the moved text's labels could otherwise collide into silently: a reference would print the wrong
#      number with no "??" to show it. That FAILS the build; it does not trigger another latexmk run, because a
#      duplicate label does not converge.
#   8. Before any build, check_note_records.py pin requires the NoteRecords2026 citation (technote.bib) to name a full
#      commit sha that is an ancestor of HEAD and holds every App. G tag and records heading the posted note cites with
#      it. Its self-test runs first, on a synthetic repository. Outside the canonical layout (the standalone note
#      repository, or any copy that is not <git checkout>/docs/analysis-note) it reports SKIP, as the Sec. IV check does.
set -euo pipefail
cd "$(dirname "$0")"

export_dir=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --export-deposit)
      if [ "$#" -lt 2 ] || [ -z "$2" ]; then echo "  FAIL --export-deposit needs a directory"; exit 1; fi
      export_dir="$2"; shift 2 ;;
    *) echo "  FAIL unknown argument: $1 (usage: bash build_all.sh [--export-deposit DIR])"; exit 1 ;;
  esac
done
if [ -n "$export_dir" ]; then
  case "$export_dir" in /*) ;; *) export_dir="$PWD/$export_dir" ;; esac
  if [ -e "$export_dir" ] && [ -n "$(ls -A "$export_dir" 2>/dev/null)" ]; then
    echo "  FAIL export directory $export_dir exists and is not empty; a deposit tree must not mix with old files"
    exit 1
  fi
  for tool in latexpand pdftotext; do
    if ! command -v "$tool" >/dev/null 2>&1; then
      echo "  FAIL $tool not found -- the deposit export cannot be written or verified"; exit 1
    fi
  done
fi

module load texlive/2024 2>/dev/null || true

# pet_note is the companion PET note split from main_note on 2026-10-12; it follows the three original
# targets so their order, and every failure message that names one, is unchanged. main_records (item 7)
# is last for the same reason, and because it reads main_note.aux.
targets=(main_note main_primer main_paper pet_note main_records)

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

# (5) The body prints no internal-only pointer. Source-only, so it runs before the builds and a failure costs nothing.
if ! command -v python3 >/dev/null 2>&1; then
  echo "  FAIL python3 not found -- the body-pointer lint cannot run, and an unchecked body must not pass"
  exit 1
fi
echo "=== body-pointer lint (internal pointers belong in the records document) ==="
python3 check_body_pointers.py --self-test   # fires on a planted body pointer, silent on the appendix
python3 check_body_pointers.py

# (8) The records citation is pinned to a merged commit that holds what the note cites. Source and git only.
echo "=== records citation pin (NoteRecords2026 names an ancestor commit holding every cited tag and heading) ==="
python3 check_note_records.py --self-test-pin   # a good pin passes; a branch, a non-ancestor, a missing tag fail
python3 check_note_records.py pin

# (9) N2-1 (note register round n2, director rulings 2026-10-26): the posted note cites records entries by number
# through \recentry{<tag>}; the numbers are generated from app_provenance.tex into records_entry_numbers.tex, which
# preamble.tex inputs. A stale file stops the build here, before any PDF or deposit export is made. The self-test
# shows a stale file and a differing records label each fail, and that the generator and main_records.tex's label
# hook number a fixture alike (with pdflatex).
echo "=== records entry numbers (generated file fresh; generator = the records build's label hook) ==="
python3 check_note_records.py --self-test-entry-numbers
python3 check_note_records.py entry-numbers --check

# (10) The sixteen-cell five-observable result (DECISION-20261027-joseph-5d-integration-then-second-scope-review.md):
# every number it prints is a key of values_fived16.tex, generated from committed readouts pinned by sha256. A stale
# file stops the build here. In the standalone note repository (no readouts) the generator reports SKIP.
echo "=== five-observable values (generated file fresh; readouts pinned) ==="
python3 make_values_fived16.py --self-test
python3 make_values_fived16.py --check

# (2) The instant every PDF must postdate. `sleep 1` removes the same-second ambiguity in
# `test -nt` on filesystems with coarse timestamps: one second, once, against a LaTeX build.
marker="$(mktemp "${TMPDIR:-/tmp}/build_all_marker.XXXXXX")"
trap 'rm -f "$marker"' EXIT INT TERM
sleep 1

# (4) LaTeX's own unresolved-reference warnings. ERE, matched against the final `${t}.log`.
unresolved_re='There were undefined (references|citations)|Reference .* undefined|Citation .* undefined'
max_invocations=2
# (7) LaTeX's own duplicate-label warnings, read from the same final log.
multidef_re='There were multiply-defined labels|Label .* multiply defined'

for t in "${targets[@]}"; do
  echo "=== building ${t}.pdf (forced with -g, so \"Nothing to do\" cannot pass for a build) ==="
  invocation=0
  while :; do
    invocation=$((invocation + 1))
    if ! latexmk -g -pdf -interaction=nonstopmode -halt-on-error "${t}.tex"; then
      echo "  FAIL latexmk failed for ${t}.tex -- see the log above. No PDF from this target is"
      echo "       trustworthy, so the containment stage is NOT reached."
      exit 1
    fi
    # Re-invoke only on evidence of unresolved references; a missing log is judged below.
    if [ -f "${t}.log" ] && grep -Eq "$unresolved_re" "${t}.log" \
        && [ "$invocation" -lt "$max_invocations" ]; then
      echo "  NOTE ${t}.log has unresolved references after latexmk invocation ${invocation};"
      echo "       invoking latexmk once more (the cold-tree pass, KNOWN_ISSUES row 50)."
      continue
    fi
    break
  done
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
  if [ ! -f "${t}.log" ]; then
    echo "  FAIL ${t}.log does not exist, so this run cannot show that ${t}.pdf has no"
    echo "       unresolved references. An unread log is not a clean one."
    exit 1
  fi
  if grep -Eq "$unresolved_re" "${t}.log"; then
    echo "  FAIL ${t}.pdf has unresolved references after ${invocation} latexmk invocation(s);"
    echo "       it would print \"??\" or [?]. First matching lines of ${t}.log:"
    grep -E "$unresolved_re|^LaTeX Warning: (Reference|Citation)" "${t}.log" | head -n 10 | sed 's/^/       /' || true
    exit 1
  fi
  if grep -Eq "$multidef_re" "${t}.log"; then
    echo "  FAIL ${t}.pdf has multiply-defined labels: a reference to one of them can print the wrong"
    echo "       number without any \"??\". First matching lines of ${t}.log:"
    grep -aE "$multidef_re" "${t}.log" | head -n 10 | sed 's/^/       /' || true
    exit 1
  fi
  # Report what was READ, not that a build was attempted: the size and mtime are the evidence.
  echo "  OK   ${t}.pdf written by this run; no unresolved references and no multiply-defined labels in ${t}.log after ${invocation} latexmk invocation(s):"
  ls -l "${t}.pdf" | sed 's/^/       /'
done

echo
echo "=== struck-value containment (struck values must reach the records and PET note builds only) ==="
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
echo "=== records entry numbers vs the records build (every posted number is the records' own label) ==="
# (9), the after-build half: main_records.aux now exists, so every number the posted note can print must equal the
# label the records build gave that entry. Runs only here: CI has no LaTeX, so CI runs the freshness check and Q3.
python3 check_note_records.py entry-numbers --check-aux

echo
echo "=== Sec. IV printed values vs committed receipts ==="
# PRD release audit ea939701, G11 (2026-10-08): the Sec. IV percentages the release cannot recompute are tied to
# their receipts in docs/orchestration/state/. The self-test first proves every printed value, moved by one unit,
# is rejected. In the standalone note repository (no receipts) the checker reports SKIP; the canonical build enforces it.
python3 check_sec4_receipts.py --self-test
python3 check_sec4_receipts.py

echo
echo "=== no input marked pending prints (\\fvpending) ==="
# A \fvpending{...} placeholder marks a readout or figure that has not landed (the covariance export, the two 5D
# figures). It prints "[PENDING: ...]"; a built note or paper that still prints one is refused here, so it never ships.
pending_txt=$(mktemp)
for t in main_note main_paper; do
  # extract to a file first: under pipefail a failed pdftotext piped into grep would read as "no placeholder"
  if ! pdftotext "$t.pdf" "$pending_txt" || ! test -s "$pending_txt"; then
    echo "  FAIL could not extract the text of $t.pdf, so the pending check cannot run"
    exit 1
  fi
  if grep -n "PENDING:" "$pending_txt"; then
    echo "  FAIL $t.pdf prints a pending placeholder (above)"
    exit 1
  fi
  # R06's pull is 2.0096, just over the |z| > 2 trigger: at one decimal it would read as unmet (director, 2026-10-27)
  if grep -nE "R06[^0-9]{0,40}z *= *2\.0([^0-9]|$)" "$pending_txt"; then
    echo "  FAIL $t.pdf prints R06's z with one decimal (above); it must print as 2.01"
    exit 1
  fi
done
rm -f "$pending_txt"
echo "  ok   no pending placeholder in main_note.pdf or main_paper.pdf"

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

if [ -n "$export_dir" ]; then
  echo
  echo "=== deposit export: comment-free source tree in $export_dir ==="
  mkdir -p "$export_dir"
  latexpand --empty-comments -o "$export_dir/main_note.tex" main_note.tex
  for b in publication.bib technote.bib; do
    # biber reads a line whose first non-blank character is % as a comment; drop those lines.
    grep -v '^[[:space:]]*%' "$b" > "$export_dir/$b" || true
  done
  # Exactly the figures this run's note build read, at the same relative paths.
  n_fig=0
  while IFS= read -r f; do
    case "$f" in /*|*../*) continue ;; esac
    [ -f "$f" ] || continue
    mkdir -p "$export_dir/$(dirname "$f")"
    cp "$f" "$export_dir/$f"
    n_fig=$((n_fig + 1))
  done < <(awk '/^INPUT /{p = $2; sub(/^\.\//, "", p); print p}' main_note.fls | grep -E '\.(pdf|png|jpe?g|eps)$' \
           | grep -v '^main_note\.pdf$' | sort -u)
  # Proof 1: no comment text survives (an escaped \% is text, a bare line-ending % is kept on purpose).
  # The grep's own status is not read through a pipe: under pipefail a SIGPIPE from `head` would turn a hit into a pass.
  comment_hits="$(grep -nE '(^|[^\\])%.*[^[:space:]]' "$export_dir/main_note.tex" "$export_dir"/*.bib || true)"
  if [ -n "$comment_hits" ]; then
    echo "  FAIL comment text survives in the export; first lines:"
    printf '%s\n' "$comment_hits" | head -n 5 | sed 's/^/       /' || true
    exit 1
  fi
  # Proof 2: it builds on its own, and prints what the source build printed.
  if ! (cd "$export_dir" && latexmk -g -pdf -interaction=nonstopmode -halt-on-error main_note.tex >/dev/null 2>&1); then
    echo "  FAIL the exported tree does not build; see $export_dir/main_note.log"; exit 1
  fi
  if grep -Eq "$unresolved_re" "$export_dir/main_note.log"; then
    echo "  FAIL the exported tree has unresolved references; see $export_dir/main_note.log"; exit 1
  fi
  pdftotext main_note.pdf "$export_dir/.source.txt"
  pdftotext "$export_dir/main_note.pdf" "$export_dir/.export.txt"
  if ! cmp -s "$export_dir/.source.txt" "$export_dir/.export.txt"; then
    echo "  FAIL the exported tree's PDF text differs from main_note.pdf:"
    diff "$export_dir/.source.txt" "$export_dir/.export.txt" | head -n 10 | sed 's/^/       /' || true
    exit 1
  fi
  rm -f "$export_dir/.source.txt" "$export_dir/.export.txt"
  (cd "$export_dir" && latexmk -c >/dev/null 2>&1 || true)
  echo "  OK   deposit tree written: main_note.tex (flattened, comment-free), 2 .bib files, ${n_fig} figures;"
  echo "       it builds alone, and its PDF text equals main_note.pdf's. Depositing it is Joseph's act."
fi

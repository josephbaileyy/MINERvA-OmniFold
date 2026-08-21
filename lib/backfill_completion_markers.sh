#!/bin/bash
# Stamp completion markers onto artifacts produced BEFORE the BEN-023 resume fix.
#
# WHY THIS IS NEEDED.  lib/resume_guard.sh gates resume on a ".done" marker instead
# of on file size.  Nothing on disk today has one.  Without a backfill, the first
# resume after the fix lands re-runs every completed unit in the campaign -- which is
# correct but can cost thousands of GPU-hours.  This walks a set of outputs, runs a
# real content validator against each, and stamps only the ones that pass.
#
# THIS IS THE HONEST VERSION OF THE ADOPTION.  A validator that opens the file and
# checks its inventory is evidence; `test -s` is not.  Anything that fails validation
# is reported and left unmarked, so the resume re-runs it -- which is exactly what
# should have happened to the comb4dCc slabs 31,34-39.  Read the FAIL list: those are
# the partials the old guard was hiding.
#
# Usage:
#   lib/backfill_completion_markers.sh --validator root  --glob 'uq_5d/universe_sweep/*.root'
#   lib/backfill_completion_markers.sh --validator npz   --glob 'cov_fps/res_toy_*.npz'
#   lib/backfill_completion_markers.sh --validator root --object hXSecND_flat --glob '...'
#   lib/backfill_completion_markers.sh --validator npz --require weights_push --glob '...'
#   lib/backfill_completion_markers.sh --dry-run --validator npz --glob '...'
#
# --validator size is accepted and deliberately loud: it reproduces the defect and is
# only for artifact families where no structural check exists.
set -o pipefail

_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/resume_guard.sh
source "${_HERE}/resume_guard.sh"

VALIDATOR=""; PATTERN=""; OBJECT=""; REQUIRE=(); DRY=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --validator) VALIDATOR="$2"; shift 2 ;;
    --glob)      PATTERN="$2"; shift 2 ;;
    --object)    OBJECT="$2"; shift 2 ;;
    --require)   REQUIRE+=("$2"); shift 2 ;;
    --dry-run)   DRY=1; shift ;;
    -h|--help)   sed -n '2,30p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) echo "[backfill][FAIL] unknown argument: $1" >&2; exit 2 ;;
  esac
done
[[ -n "$VALIDATOR" && -n "$PATTERN" ]] || {
  echo "[backfill][FAIL] --validator {root|npz|size} and --glob are both required" >&2; exit 2; }

validate_one() {
  case "$VALIDATOR" in
    root) rg_valid_root "$1" "$OBJECT" ;;
    npz)  rg_valid_npz "$1" "${REQUIRE[@]}" ;;
    size) [[ -s "$1" ]] ;;
    *) echo "[backfill][FAIL] unknown validator: $VALIDATOR" >&2; exit 2 ;;
  esac
}

if [[ "$VALIDATOR" == "size" ]]; then
  echo "[backfill][WARNING] --validator size stamps on a bare nonempty check. That is the" >&2
  echo "[backfill][WARNING] BEN-023 defect itself: a partial file will be marked complete." >&2
fi

shopt -s nullglob
# shellcheck disable=SC2206  # deliberate glob expansion of the caller's pattern
FILES=( $PATTERN )
shopt -u nullglob
(( ${#FILES[@]} )) || { echo "[backfill] no files matched: ${PATTERN}"; exit 0; }

marked=0; already=0; failed=0; unusable=0
declare -a FAILED_LIST=()
declare -a UNUSABLE_LIST=()
for f in "${FILES[@]}"; do
  [[ -f "$f" ]] || continue
  case "$f" in *.done|*.tmp) continue ;; esac
  rg_is_complete "$f" && { already=$((already+1)); continue; }
  # OI-142: A MARKER WE COULD NOT READ IS NOT OURS TO OVERWRITE.
  #
  # This mattered the moment rg_is_complete stopped honouring a marker that carries neither
  # size nor mtime.  Before that narrowing such a marker returned 0 here and the file counted
  # as `already`; after it, control would fall straight through to `rg_adopt`, which calls
  # rg_mark_complete and OVERWRITES ${f}.done.  For a P4 endpoint receipt that would replace a
  # record of root/merged/central identities, config hash, bkg_mode and the whole producing
  # closure with a generic size+mtime stamp -- destroying provenance to manufacture the pass
  # that the narrowing had just correctly withheld.  That is the OI-142 defect in a new
  # costume: an unreadable marker laundered into a completion claim.
  #
  # So: existing marker, whatever it says -> report it and move on.  A backfill exists to
  # stamp artifacts that have NO marker; adjudicating one that already has a marker it cannot
  # parse is a different decision and belongs to whoever wrote it.
  _bf_marker="$(rg_marker_path "$f")"
  if [[ -e "$_bf_marker" ]]; then
    unusable=$((unusable+1))
    UNUSABLE_LIST+=("${f} -- marker $(rg_marker_defect "$_bf_marker")")
    continue
  fi
  if validate_one "$f"; then
    if (( DRY )); then echo "[backfill] WOULD MARK ${f}"
    else rg_adopt "$f" "backfill, validator=${VALIDATOR}${OBJECT:+ object=${OBJECT}}" >/dev/null; fi
    marked=$((marked+1))
  else
    failed=$((failed+1)); FAILED_LIST+=("$f")
  fi
done

echo "[backfill] pattern=${PATTERN} validator=${VALIDATOR}"
echo "[backfill]   ${already} already marked, ${marked} $( ((DRY)) && echo 'would be ' )marked, ${failed} FAILED validation, ${unusable} LEFT ALONE (unreadable marker)"
if (( unusable )); then
  echo "[backfill] These already carry a marker this library cannot read as completion proof."
  echo "[backfill] They were NOT re-stamped: overwriting a marker we cannot parse would destroy"
  echo "[backfill] whatever it does record (a P4 endpoint receipt, say) to manufacture a pass."
  printf '[backfill]   LEFT ALONE %s\n' "${UNUSABLE_LIST[@]}"
fi
if (( failed )); then
  echo "[backfill] These did NOT validate and were left unmarked, so the resume will regenerate"
  echo "[backfill] them. Under the old size-only guard they would have been skipped as done:"
  printf '[backfill]   FAIL %s\n' "${FAILED_LIST[@]}"
fi
# A failed validation is information, not an error: exit 0 so a backfill sweep over
# many patterns does not abort partway under `set -e`.
exit 0

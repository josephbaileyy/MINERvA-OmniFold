#!/bin/bash
# Per-member output namespacing and IDENTITY-AWARE resume for the M(ii) offset scan.
# Source this; do not execute it. Requires lib/resume_guard.sh to be sourced first.
#
# WHY THIS EXISTS. Every output path in the seven scan legs was a fixed literal with no offset in it,
# so all 50 members wrote to the same namespaces -- and those namespaces already hold the published
# archive at 100/100 and 24/24. A launch would have resume-skipped against the archive, exited 0
# everywhere, finished fast and handed back 50 copies of the archive. The failure shape is the
# dangerous one because it is CHEAP: an expensive wrong answer gets noticed, a fast green one does not.
#
# THE PRIMARY DEFENCE IS STRUCTURAL, NOT A CHECK. The member directory is DERIVED FROM THE OFFSET, so
# a product from another k cannot be in this member's directory to be handed back. That is stronger
# than comparing identities, because there is no identity to compare -- the path already separates
# them. `mr_skip_if_complete` below is defence in depth for the one case the structure cannot cover: a
# file hand-copied into a member directory, where the marker's note is the only evidence.
#
# AND UNSET MEANS ARCHIVE PATHS, DELIBERATELY. With MNV_EST_SEED_OFFSET unset -- every non-scan use of
# these launchers -- MR_MEMBER is empty and every path is exactly what it was before this file
# existed. Only a DECLARED offset creates a member namespace. So the scan is namespaced and the archive
# reproduction path is untouched, and `declared` is the same distinction the product stamps carry
# (seed_offset_policy.declared_offset): declared=0 means nothing can be concluded.
#
# THE ANCHOR IS NOT AN EXCEPTION. k=0 is DECLARED, so member 0 writes to member_k000000/ like every
# other member -- per lane C's determination, "member 0 runs in member_00/, where the archive is not
# present to be handed back". The archive is a READ-ONLY COMPARAND, never a write destination and never
# a resume source. That is exactly what makes bit-exactness checkable: it distinguishes "reproduced the
# archive" from "was handed the archive".
#
# NAMING DIVERGENCE, FLAGGED RATHER THAN ASSUMED. C's determination writes `member_00/` -- a member
# INDEX. This derives `member_k000000/` from the OFFSET instead, because a launcher cannot compute an
# index without knowing the grid, and a second variable carrying the index could DISAGREE with the
# offset in the same run. The offset is the physical quantity; the index is a property of the grid and
# belongs in the plan, which records the index<->offset<->directory mapping. If C prefers the index
# form it needs a second env var and an assertion that the two agree, which is a defect surface this
# form does not have.

# mr_require_valid_offset -- CALL THIS ONCE AT THE TOP OF A LAUNCHER, outside any command
# substitution. A malformed offset must kill the job, and it cannot do so from inside `$( )`:
# `exit` there ends only the subshell, so `OUT="$(mr_prefix ...)"` on a bad offset yielded an EMPTY
# path and the launcher carried on writing to a bad location. Found by running this file's own sanity
# cases rather than by reading it -- the same lesson as the argv probe, one layer down.
mr_require_valid_offset() {
  if [[ -z "${MNV_EST_SEED_OFFSET+x}" ]]; then return 0; fi
  if ! [[ "${MNV_EST_SEED_OFFSET}" =~ ^-?[0-9]+$ ]]; then
    echo "[member] FAIL: MNV_EST_SEED_OFFSET='${MNV_EST_SEED_OFFSET}' is not an integer. It names the" >&2
    echo "[member]   output namespace AND is stamped into every product, so a malformed value would be" >&2
    echo "[member]   recorded as provenance and written to an unintended path. Refusing to run." >&2
    exit 2
  fi
}

# mr_member_dir -> "" when no offset is declared, else "member_k<6-digit signed>/"
mr_member_dir() {
  if [[ -z "${MNV_EST_SEED_OFFSET+x}" ]]; then printf ''; return 0; fi
  local k="${MNV_EST_SEED_OFFSET}"
  if ! [[ "$k" =~ ^-?[0-9]+$ ]]; then
    echo "[member] FAIL: MNV_EST_SEED_OFFSET='${k}' is not an integer; it names the output namespace" >&2
    return 2
  fi
  if [[ "$k" -lt 0 ]]; then printf 'member_kneg%06d/' "$(( -k ))"; else printf 'member_k%06d/' "$k"; fi
}

# mr_prefix <path> -> the path with the member directory inserted before its basename, and the
# directory created. A relative or absolute path both work; "" member leaves the path untouched.
mr_prefix() {
  local p="$1" m d b
  m="$(mr_member_dir)" || return 2
  if [[ -z "$m" ]]; then printf '%s' "$p"; return 0; fi
  d="$(dirname "$p")"; b="$(basename "$p")"
  mkdir -p "${d}/${m}" 2>/dev/null || true
  printf '%s/%s%s' "$d" "$m" "$b"
}

# mr_dir_prefix <dir> -> the directory with the member directory appended, created.
mr_dir_prefix() {
  local p="$1" m
  m="$(mr_member_dir)" || return 2
  if [[ -z "$m" ]]; then printf '%s' "$p"; return 0; fi
  mkdir -p "${p}/${m}" 2>/dev/null || true
  printf '%s/%s' "$p" "${m%/}"
}

# mr_note -> the marker note recording this run's declared offset, or "" when undeclared.
mr_note() {
  if [[ -z "${MNV_EST_SEED_OFFSET+x}" ]]; then printf 'est_seed_offset=undeclared'; return 0; fi
  if ! [[ "${MNV_EST_SEED_OFFSET}" =~ ^-?[0-9]+$ ]]; then printf 'est_seed_offset=MALFORMED'; return 2; fi
  printf 'est_seed_offset=%s' "${MNV_EST_SEED_OFFSET}"
}

# mr_skip_if_complete <out> -- like rg_skip_if_complete, except a complete product whose marker
# records a DIFFERENT offset is a HARD FAILURE (exit 3) rather than a skip.
#
# BEN-023 IN ITS CORRECT FORM. That finding was a resume guard ACCEPTING an incomplete product because
# it existed. Its mirror is a guard accepting a COMPLETE product that belongs to a different member --
# equally silent, and worse here, because the product is valid and correctly stamped for the k that
# made it. Existence-based resume would let stage 1 pass by being handed the archive, which is the one
# outcome stage 1 exists to exclude.
mr_skip_if_complete() {
  local out="$1" marker note want
  marker="$(rg_marker_path "$out")"
  want="$(mr_note)"
  if [[ -f "$marker" ]]; then
    note="$(sed -n 's/.*"note":"\([^"]*\)".*/\1/p' "$marker" 2>/dev/null)"
    if [[ -n "$note" && "$note" == est_seed_offset=* && "$note" != "$want" ]]; then
      echo "[member] FAIL: ${out} is complete but its marker records ${note} while this run is ${want}." >&2
      echo "[member]   A complete product from another member is a HARD FAILURE, never a skip: it is" >&2
      echo "[member]   valid and correctly stamped for the k that made it, so skipping would hand this" >&2
      echo "[member]   member another member's answer with nothing downstream able to tell." >&2
      exit 3
    fi
  fi
  rg_skip_if_complete "$out"
}

# mr_run <out> <cmd...> -- like rg_run, except the completion marker RECORDS THIS RUN'S OFFSET.
#
# THIS IS NOT A CONVENIENCE WRAPPER; WITHOUT IT THE IDENTITY CHECK IS DEAD CODE. `rg_run` calls
# `rg_mark_complete "$out"` with NO note argument, so every marker it writes has an empty note --
# and `mr_skip_if_complete` only fires when the note records a DIFFERENT offset. Markers written by
# `rg_run` would therefore never trigger it, and the check would have been unfalsifiable in exactly
# the regime it exists for. Found by reading rg_run's body rather than its docstring.
mr_run() {
  local out="$1"; shift
  [[ $# -gt 0 ]] || { echo "[member][BUG] mr_run ${out}: no command given" >&2; return 2; }
  rg_begin "$out"
  local rc=0
  "$@" || rc=$?
  if (( rc != 0 )); then
    echo "[member] producer FAILED (rc=${rc}) for ${out} -- no completion marker written" >&2
    return "$rc"
  fi
  [[ -e "$out" ]] || { echo "[member][FAIL] producer returned 0 but ${out} absent" >&2; return 4; }
  rg_mark_complete "$out" "$(mr_note)"
}

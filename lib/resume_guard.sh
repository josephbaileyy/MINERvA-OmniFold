#!/bin/bash
# Completion-proof resume guards.  Source this; do not execute it.
#
# WHY THIS EXISTS (BEN-023 / AUDIT-FINDINGS-20260731 J35, J10).
# The repo-wide resume idiom was
#
#     [[ -s "${OUT}" ]] && { echo "skip (exists)"; exit 0; }
#
# which treats ANY nonempty output as a finished one.  Producers write straight to
# ${OUT}, so an interrupted job leaves a valid-but-incomplete file and the next run
# skips it permanently and silently.  This is not hypothetical: comb4dCc 55971617
# failed on 15/160 missing throws because slabs 31,34-39 were partial leftovers of an
# interrupted multinode run, while all 40 array tasks reported COMPLETED.  It was
# caught only by the combine's --expected-throws manifest gate, downstream and by
# luck.  Size is not proof of completion.
#
# THE FIX.  Completion becomes an explicit, separately written record -- a ".done"
# marker stamped only after the producer exits 0 -- instead of an inference from the
# output's existence.  An interrupted producer cannot leave one behind, so the resume
# re-runs.  The marker is BOUND to the output's size and mtime, so an output that is
# later truncated or half-rewritten invalidates its own marker rather than keeping a
# stale pass.
#
# The marker convention (${OUT}.done, JSON) is deliberately the one
# nd-unfolding/run_p4_unfold_std.sh already uses -- that script is the in-repo
# precedent for a transactional, content-validated resume.  Its receipts are NOT
# readable by rg_is_complete, and deliberately so since OI-142: they carry no size/mtime
# binding, and honouring that absence is exactly what let a truncated marker pass here.
# They are validated by nd-unfolding/p4_check_receipt.py, which checks strictly more than
# this library can -- see the OI-142 note on rg_is_complete.
#
# TWO CALL SHAPES.  Prefer the transactional one where the producer writes a single
# self-contained file:
#
#     rg_skip_if_complete "${OUT}" && exit 0
#     TMP="$(rg_tmp_for "${OUT}")"
#     python3 producer.py --out "${TMP}" || { rm -f "${TMP}"; exit 1; }
#     rg_publish "${TMP}" "${OUT}"
#
# Use the in-place one where the producer derives sibling paths, logs or per-unit
# saves from its --out argument, so redirecting it to a temp path would move those
# too:
#
#     rg_skip_if_complete "${OUT}" && exit 0
#     rg_begin "${OUT}"
#     python3 producer.py --out "${OUT}"
#     rg_mark_complete "${OUT}"
#
# Both close the defect.  The transactional shape additionally leaves no partial at
# ${OUT} at all; the in-place shape leaves one but guarantees it is never mistaken
# for a result.
#
# ADOPTING PRE-EXISTING OUTPUTS.  Artifacts produced before this library landed carry
# no marker, and there is no way to tell a complete one from a partial one after the
# fact -- that is precisely the defect.  So the default is to RE-RUN and say so
# loudly, never to skip on a bare size check again.  To avoid re-running a whole
# campaign's worth of good outputs, stamp them once with a content validator first:
#
#     lib/backfill_completion_markers.sh --validator root --glob '<pattern>'
#
# RESUME_ADOPT_LEGACY=1 adopts an unmarked nonempty output in place, loudly.  It is a
# size check by another name and is only defensible where a validator cannot be
# written; it prints a warning every time so it cannot become the quiet default.
# RESUME_FORCE=1 re-runs everything regardless of markers.

# --- portability: Perlmutter is GNU coreutils, the dev Mac is BSD ------------------
rg_stat_size() { stat -c '%s' "$1" 2>/dev/null || stat -f '%z' "$1" 2>/dev/null; }
rg_stat_mtime() { stat -c '%Y' "$1" 2>/dev/null || stat -f '%m' "$1" 2>/dev/null; }

rg_marker_path() { printf '%s.done\n' "$1"; }

# Unique per-process temp sibling of OUT.  Same directory, so the rename is atomic
# (a cross-filesystem mv is a copy, which is not).
rg_tmp_for() { printf '%s.%s.%s.tmp\n' "$1" "$$" "${RANDOM}${RANDOM}"; }

# Pull one flat "key": <integer> out of the marker without needing python or jq -- this
# runs before setup_salloc_env.sh in several launchers, where neither is guaranteed.
# Deliberately restricted to integer-valued keys (size, mtime): those are the only fields
# rg_is_complete reads, and requiring digits means a free-text `note` that happens to
# contain the word "size" cannot be mistaken for the field.
rg__marker_field() {
  local marker="$1" key="$2" v
  v="$(tr ',' '\n' < "$marker" 2>/dev/null \
       | sed -n "s/.*\"${key}\"[[:space:]]*:[[:space:]]*\([0-9][0-9]*\).*/\1/p" | head -1)"
  [[ -n "$v" ]] || return 1
  printf '%s\n' "$v"
}

# Stamp OUT complete.  Written to a temp file and renamed, so an interrupted stamp
# cannot leave a truncated marker that parses as a pass.
rg_mark_complete() {
  local out="$1" note="${2:-}" marker; marker="$(rg_marker_path "$out")"
  if [[ ! -e "$out" ]]; then
    echo "[resume][BUG] rg_mark_complete called but ${out} does not exist" >&2; return 2
  fi
  printf '{"output":"%s","size":%s,"mtime":%s,"marked_at":"%s","host":"%s","job":"%s","note":"%s"}\n' \
    "$out" "$(rg_stat_size "$out")" "$(rg_stat_mtime "$out")" \
    "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$(hostname 2>/dev/null)" \
    "${SLURM_JOB_ID:-}${SLURM_ARRAY_TASK_ID:+:${SLURM_ARRAY_TASK_ID}}" "$note" \
    > "${marker}.tmp" && mv -f "${marker}.tmp" "$marker"
}

# 0 iff OUT is present AND its marker is present AND the marker still describes it.
#
# OI-142: A MARKER CARRYING NEITHER size NOR mtime IS REFUSED, NOT HONOURED.  This function
# used to `return 0` for one.  The stated reason was that run_p4_unfold_std.sh's receipts
# predate the size/mtime binding and were content-validated before being written -- a claim
# about a marker's PROVENANCE, authorising a test over its SHAPE.  Those are not the same
# thing, and the shape "neither field present" is indistinguishable from an EMPTY, TRUNCATED
# or otherwise malformed marker.  So a half-written stamp read as a finished step: the exact
# BEN-023 defect this library exists to close, re-entering through the library's own
# exemption.  The absence of two fields cannot be a positive credential for anything.
#
# P4 RECEIPTS ARE VALIDATED BY THEIR OWN VALIDATOR, WHICH IS STRICTLY BETTER.
# nd-unfolding/p4_check_receipt.py re-derives every recorded identity and the whole
# producing closure, and rejects an absent, empty, non-JSON or explicitly-null receipt by
# name.  run_p4_unfold_std.sh already resumes through it and has never routed a resume
# decision through this function.  Enumerated for OI-142: no rg_* caller in the repo reads
# nd-unfolding/active_universe_5d/standard/unfolds at all, so this branch protected no live
# caller -- it was pure attack surface.  A legacy shape that genuinely needs honouring must
# bring a credential OF ITS OWN (an explicit `legacy=1`, say), never the absence of fields.
#
# nd-unfolding/sbatch_finalize_5d_bkgaware_gpu.sh's undeclared-route COMB guard checks size
# and mtime directly, by ruling, rather than calling this function.  That stays true and
# stays independent: its ruling is about what that one route may reuse, not about this
# library's default, and it must not be refactored into this call now that the two agree.
#
# Return codes, because "not complete" has two causes an operator must be able to tell apart:
#   0  complete -- marker present and its size+mtime still describe OUT
#   1  not complete -- OUT absent, marker absent/empty, or the binding no longer matches
#   2  marker present but carries NO usable size/mtime binding, so it proves nothing
rg_is_complete() {
  local out="$1" marker size mtime msize mmtime; marker="$(rg_marker_path "$out")"
  [[ -e "$out" && -s "$marker" ]] || return 1
  # `|| =""` on the ASSIGNMENT, not inside the substitution: rg__marker_field returns 1 on a
  # missing key, which would abort a `set -e` caller that is not inside an `if` condition.
  msize="$(rg__marker_field "$marker" size)"  || msize=""
  mmtime="$(rg__marker_field "$marker" mtime)" || mmtime=""
  # BOTH bindings required.  One-of-two is refused too: a marker naming only `size` says
  # nothing about a same-size rewrite, and is just as likely to be a truncation mid-key.
  [[ -n "$msize" && -n "$mmtime" ]] || return 2
  size="$(rg_stat_size "$out")"; mtime="$(rg_stat_mtime "$out")"
  [[ "$msize" == "$size" && "$mmtime" == "$mtime" ]]
}

# Why a marker cannot serve as completion proof, in words that are TRUE of this marker.
# "stale" and "never carried a binding" are different facts and imply different operator
# actions, and before OI-142 every non-matching case was reported as the first one.
rg_marker_defect() {
  local marker="$1" ms mt
  [[ -e "$marker" ]] || { printf 'absent\n'; return 0; }
  [[ -s "$marker" ]] || { printf 'present but EMPTY -- a stamp truncated to nothing\n'; return 0; }
  ms="$(rg__marker_field "$marker" size)"  || ms=""
  mt="$(rg__marker_field "$marker" mtime)" || mt=""
  if [[ -z "$ms" && -z "$mt" ]]; then
    if grep -q '"root_sha256"' "$marker" 2>/dev/null; then
      printf '%s' 'carries NEITHER size nor mtime and looks like a P4 endpoint receipt; '
      printf '%s\n' 'validate it with nd-unfolding/p4_check_receipt.py, which this guard cannot substitute for'
    else
      printf '%s\n' 'carries NEITHER size nor mtime, so it is indistinguishable from a truncated stamp (OI-142)'
    fi
  elif [[ -z "$ms" ]]; then printf 'records mtime but no size, so it is malformed or truncated\n'
  elif [[ -z "$mt" ]]; then printf 'records size but no mtime, so it is malformed or truncated\n'
  else printf 'records size=%s mtime=%s, which no longer describe the file\n' "$ms" "$mt"
  fi
}

# Invalidate any stale marker BEFORE overwriting OUT in place, so a crash midway
# through the rewrite cannot be covered by the previous run's marker.
rg_begin() { rm -f "$(rg_marker_path "$1")" "$(rg_marker_path "$1").tmp"; }

# Explicitly adopt an unmarked output as complete, recording that it was adopted
# rather than produced.  Kept separate from rg_mark_complete so the two are
# distinguishable in the marker afterwards.
rg_adopt() {
  local out="$1" why="${2:-unvalidated legacy artifact}"
  rg_mark_complete "$out" "ADOPTED: ${why}"
}

# The resume decision.  Returns 0 to SKIP, 1 to (re)run.  Callers must act on it:
#   rg_skip_if_complete "${OUT}" && exit 0        # array task / one-shot
#   rg_skip_if_complete "${OUT}" && continue      # loop body
# An optional validator command may follow; it is run as `validator "$OUT"` and, if
# it passes on an unmarked output, that output is adopted and skipped.  That is the
# content-validated resume BEN-023 asks for and is always preferable to
# RESUME_ADOPT_LEGACY.
rg_skip_if_complete() {
  local out="$1"; shift
  if [[ "${RESUME_FORCE:-0}" == "1" ]]; then
    echo "[resume] RESUME_FORCE=1 -- (re)running ${out}"; return 1
  fi
  if rg_is_complete "$out"; then
    echo "[resume] SKIP ${out} (completion marker present and current)"; return 0
  fi
  # A marker EXISTS but did not prove completion.  Say which, and re-run either way: this
  # used to report every such marker as "size/mtime moved since it was stamped", which is a
  # false statement about a marker that never carried those fields (OI-142).  Note this
  # returns BEFORE the adopt paths below, so a marker we could not read is never overwritten
  # by an adoption stamp -- laundering an unreadable marker into a pass is the same defect.
  if [[ -e "$(rg_marker_path "$out")" && -e "$out" ]]; then
    echo "[resume] UNUSABLE MARKER for ${out} -- re-running. The marker $(rg_marker_defect "$(rg_marker_path "$out")")" >&2
    return 1
  fi
  if [[ -s "$out" ]]; then
    if [[ $# -gt 0 ]] && "$@" "$out"; then
      rg_adopt "$out" "content validator '$1' passed"
      echo "[resume] ADOPT+SKIP ${out} (no marker; validator '$1' passed)"; return 0
    fi
    if [[ "${RESUME_ADOPT_LEGACY:-0}" == "1" ]]; then
      echo "[resume][WARNING] ADOPTING ${out} on a bare size check (RESUME_ADOPT_LEGACY=1)." >&2
      echo "[resume][WARNING] This is the BEN-023 defect, opted into deliberately: a partial file" >&2
      echo "[resume][WARNING] is indistinguishable from a complete one here. Prefer a validator." >&2
      rg_adopt "$out" "RESUME_ADOPT_LEGACY=1, size-only"
      echo "[resume] ADOPT+SKIP ${out}"; return 0
    fi
    echo "[resume] ${out} exists but has NO completion marker -- treating as INCOMPLETE and" >&2
    echo "[resume] re-running. If it is a validated pre-BEN-023 artifact, stamp it first with" >&2
    echo "[resume]   lib/backfill_completion_markers.sh   (or set RESUME_ADOPT_LEGACY=1)." >&2
    return 1
  fi
  return 1
}

# Atomic publish of a transactional temp file, then the marker LAST -- so a marker
# always implies a fully renamed output, never the reverse.
rg_publish() {
  local tmp="$1" out="$2" note="${3:-}"
  [[ -e "$tmp" ]] || { echo "[resume][FAIL] rg_publish: temp ${tmp} absent" >&2; return 2; }
  mv -f "$tmp" "$out" || return 3
  rg_mark_complete "$out" "$note"
}

# Run a producer that writes OUT in place, and stamp the marker iff it succeeds.
#
#     rg_run "${OUT}" python3 producer.py --out "${OUT}" --seed 1
#
# This is the shape used for the repo-wide BEN-023 conversion.  Binding "produce" and
# "mark complete" into ONE call is the point: the alternative -- a bare
# rg_mark_complete somewhere after the producer -- has to be placed correctly in
# every one of ~60 heterogeneous launchers, and a single misplacement recreates the
# defect silently.  Here the marker is unreachable unless the producer returned 0.
#
# The producer keeps writing to OUT itself rather than to a temp path, because many
# of these producers derive sibling paths, logs and per-unit saves from their --out
# argument; redirecting it would move those too.  An interruption therefore does
# leave a partial at OUT -- but it leaves no marker, so the next run re-runs instead
# of skipping.  Where the producer writes a single self-contained file, prefer
# rg_tmp_for + rg_publish, which additionally leaves no partial at all.
rg_run() {
  local out="$1"; shift
  [[ $# -gt 0 ]] || { echo "[resume][BUG] rg_run ${out}: no command given" >&2; return 2; }
  rg_begin "$out"
  local rc=0
  "$@" || rc=$?
  if (( rc != 0 )); then
    echo "[resume] producer FAILED (rc=${rc}) for ${out} -- no completion marker written" >&2
    return "$rc"
  fi
  if [[ ! -e "$out" ]]; then
    echo "[resume][FAIL] producer returned 0 but ${out} does not exist" >&2
    return 4
  fi
  rg_mark_complete "$out"
}

# Input-side counterpart: refuse to consume an upstream product that was never
# marked complete.  Only meaningful for inputs this repo's launchers produce.
rg_require_complete_input() {
  local in="$1" who="${2:-input}"
  [[ -s "$in" ]] || { echo "[resume][FAIL] ${who} missing/empty: ${in}" >&2; return 2; }
  if ! rg_is_complete "$in"; then
    echo "[resume][FAIL] ${who} has no valid completion marker: ${in}" >&2
    echo "[resume][FAIL] Its producer may have been interrupted. Stamp it with" >&2
    echo "[resume][FAIL] lib/backfill_completion_markers.sh once validated, or regenerate it." >&2
    return 3
  fi
}

# --- content validators, for the adopt path and for backfill -----------------------
# A ROOT file that opens, is not a zombie and was not recovered from a partial write.
# Recovery is the specific signature of a TFile whose writer died before Close().
rg_valid_root() {
  python3 - "$1" "${2:-}" <<'PY' >/dev/null 2>&1
import sys
import ROOT
path, obj = sys.argv[1], sys.argv[2]
f = ROOT.TFile.Open(path)
ok = bool(f) and not f.IsZombie() and not f.TestBit(ROOT.TFile.kRecovered)
if ok and obj:
    ok = bool(f.Get(obj))
sys.exit(0 if ok else 1)
PY
}

# An npz whose central directory is intact and every member decompresses.  A
# truncated npz opens fine and only fails when a member is actually read.
rg_valid_npz() {
  python3 - "$@" <<'PY' >/dev/null 2>&1
import sys
import numpy as np
path, keys = sys.argv[1], sys.argv[2:]
with np.load(path, allow_pickle=True) as d:
    names = list(d.files)
    for k in keys:
        if k not in names:
            sys.exit(1)
    for k in names:
        _ = d[k]
sys.exit(0)
PY
}

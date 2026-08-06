#!/bin/bash
# Fired by wakerctl when the unified-throw regeneration array leaves the queue.
#
# usage: notify_uthrow_regen.sh <array_job_id>
#
# WHY A SEPARATE NOTIFIER. The first version of this watch reused notify_nominal.sh, which reports
# `pet_fullevent_nominal_weights.npz` — artifacts this array does not produce. It would have fired and
# said "ABSENT", which is worse than no notification: it invents a failure. A notifier must report the
# thing its job actually makes.
#
# WHAT THIS ARRAY IS FOR. The adopted `uq_5d/unified_throw_cov_5d.root` records `n_throws=160`, but the
# slab directory had only throws 0-121 (38 lost from purgeable scratch, and slab 30 left partial at 2
# rows). Tasks 30-39 of `sbatch_uthrow_run_5d_fast.sh` regenerate throws 120-159. Regeneration is
# BIT-REPRODUCIBLE: `unified_throw_cov.py:222-223` seeds per GLOBAL throw index
# (`rng = default_rng(seed + throw_offset + j)`), so throw 122 depends only on `--seed 1000` and its
# index, never on task packing — the repaired ensemble is the original one, not a statistical stand-in.
#
# The report is therefore a COMPLETENESS check, because that is the gate for what comes next: the J28
# re-roll may only be redone on a full 160, and adoption only on that.
set -uo pipefail
JOB="${1:?usage: notify_uthrow_regen.sh <array_job_id>}"
REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold
BODY=/pscratch/sd/j/josephrb/.uthrow_regen_body.txt
SCAN=/pscratch/sd/j/josephrb/scan_slabs.py

PY_NUMPY="${ROOT628_PREFIX:-/global/homes/j/josephrb/.conda/envs/root_6_28}/bin/python3"
[[ -x "${PY_NUMPY}" ]] || PY_NUMPY="python3"

{
  echo "RESTORE / J28: the unified-throw regeneration array ${JOB} has left the queue."
  echo "Fired by wakerctl on $(hostname) at $(date -u +%Y-%m-%dT%H:%M:%SZ), independent of any session."
  echo
  echo "=== per-task outcome (a partial array is the failure mode that matters) ==="
  sacct -j "${JOB}" --format=JobID%18,State,Elapsed,ExitCode,MaxRSS -P 2>/dev/null | head -16
  echo
  echo "=== throw completeness: is the ensemble back to the adopted 160? ==="
  if [[ -f "${SCAN}" ]]; then
    (cd "${REPO}/nd-unfolding" && "${PY_NUMPY}" "${SCAN}" 2>&1 | tail -8)
  else
    echo "  scan_slabs.py missing; counting slabs only:"
    ls "${REPO}"/nd-unfolding/uq_5d/uthrow_slabs_5d_sb/uthrow5d_slab_*.npz 2>/dev/null | wc -l
  fi
  echo
  echo "=== what this unblocks, in order ==="
  echo "  1. ONLY IF 160 distinct throws: re-run rescale_flux_universes.py on the complete set"
  echo "     (the 2026-08-06 re-roll used 122/160, so its absolute numbers were a subsample)."
  echo "  2. Then the combine, then adopt_unified_5d.py in BOTH variants -- the F7 rule at"
  echo "     CORRECTED_UQ_PRODUCTION_STATUS.md:73-78 requires the CV-centered variant, because"
  echo "     ||mean_shift|| is 4.69x the sampling floor."
  echo "  3. Then, and only then, lift the ledger quarantine BY REPLACING numbers."
  echo "  If fewer than 160: do NOT proceed. Report which throw ids are still missing."
  echo
  echo "Log: nd-unfolding/pet/AUTONOMOUS_LOG_20260805.md"
} > "${BODY}" 2>&1

/usr/bin/python3.11 /pscratch/sd/j/josephrb/send_channel_mail.py \
  "[MNV-AUTO] unified-throw regeneration ${JOB} finished -- throw completeness inside" "${BODY}"

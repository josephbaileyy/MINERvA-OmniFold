#!/bin/bash
# PILOT-FB's login-node prep-only smoke (the code audits' request, the director's ruling of 2026-11-18): the prep step
# alone, on a login node, before any job. 0 node-h: no sbatch, no srun, no fit (prep stops before the first fit).
# Usage: pfb_smoke_prep.sh <deploy> <pin> <stage>. It writes <stage>/smoke-edges/ (the twelve forced-bins files and
# INDEX.json) or, on INFEASIBLE, <stage>/smoke-edges.g0.json (G0's record: every role and feature's diagnostics).
# The job (sbatch_pfb.sh) later requires its own prep to reproduce smoke-edges/INDEX.json byte for byte.
# Exit codes: 0 edges written; 6 INFEASIBLE; 4 an input digest; 2 a refusal; other: the prep step's own.
set -o pipefail
D="${1:?deploy}"; PIN="${2:?pin}"; STAGE="${3:?stage}"
[ -z "$SLURM_JOB_ID" ] || { echo "[pfb-smoke] refusing: this is a login-node step and runs outside any Slurm job" >&2; exit 2; }
head_sha=$(git -C "$D" rev-parse HEAD 2>/dev/null)
dirty=$(git -C "$D" status --porcelain --untracked-files=no 2>/dev/null | wc -l)
if [ "$head_sha" != "$PIN" ] || [ "$dirty" -ne 0 ]; then
    echo "[pfb-smoke] refusing: deploy HEAD=$head_sha (pinned $PIN), $dirty modified tracked files" >&2; exit 2
fi
[ ! -e "$STAGE/smoke-edges" ] && [ ! -e "$STAGE/smoke-edges.g0.json" ] || { echo "[pfb-smoke] refusing: a smoke result exists in $STAGE" >&2; exit 2; }
mkdir -p "$STAGE"
source "$D/setup_salloc_env.sh" > "$STAGE/smoke-env.log" 2>&1
NPZ=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz
BKG=/pscratch/sd/j/josephrb/s5c-20260924/runs/p2/bkg_dump.npz
RATIO="$D/$(python3 -c 'import sys; sys.path.insert(0, sys.argv[1]); import rounding_mechanism_probe as r; print(r.STABILITY["ratio"])' "$D/nd-unfolding")"
( cd "$D" && python3 nd-unfolding/fb_pilot_probe.py prep --edges-out "$STAGE/smoke-edges" -- \
    --npz "$NPZ" --bkg "$BKG" --expect-npz-sha256 07fccc1abc7204bc29349b4ba96850986fe91e909e83fc54e8d1a6b3922a649f \
    --expect-bkg-sha256 2addac8f26055c5ed69862e7afe29e12ac51dbe23a8d6eeed79d71bec9d82955 --config R --iters 5 \
    --threads 32 --construction pseudo --truth eavail_shape --amplitude 1.0 --eavail-ratio "$RATIO" --pseudo-seed 990000 \
    --pairs=-:- --tag pfb_smoke --out "$STAGE/smoke-unused" ) > "$STAGE/smoke.log" 2>&1
rc=$?
echo "[pfb-smoke] prep rc=$rc"
[ "$rc" -eq 0 ] && sha256sum "$STAGE/smoke-edges/INDEX.json"
exit "$rc"

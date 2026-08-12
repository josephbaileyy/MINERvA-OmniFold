#!/bin/bash
#SBATCH --job-name=digest_quoted
#SBATCH --account=m3246
#SBATCH --qos=xfer
#SBATCH --time=04:00:00
#SBATCH --licenses=SCRATCH
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=/pscratch/sd/j/josephrb/mnv-digest-work/digest_quoted_%j.out
#SBATCH --error=/pscratch/sd/j/josephrb/mnv-digest-work/digest_quoted_%j.err
#
# STEP 2 (B) of AUTHORIZATION-20260812-ignored-set-scope.md: digests for the QUOTED PRODUCTS.
#
# WHY A JOB AND NOT A LOGIN SHELL. The set is 322,306,102,132 B across 36 files. At the
# ~170 MB/s this lane measured on the 2.68 GB OI-17 probe that is ~32 min of sustained
# sequential reads, which does not belong on a shared login node. `xfer` exists to absorb
# exactly this. Decided by Session A under Joseph's standing grant ("any single job under
# 12 h is pre-approved"); it never needed to reach him.
#
# WHY IT WRITES NOTHING INTO THE REPO TREE. /pscratch/sd/j/josephrb/MINERvA-OmniFold is the
# object of the 2026-08-12 uncommitted inventory and is under an eight-verb no-touch list
# (no pull, merge, rebase, checkout, clean, delete, relocate, bulk-add). A receipt written
# INSIDE it would perturb the very enumeration it documents -- a new-file write is not
# literally one of the eight verbs, and that is not the point. So every output of this job
# lands in $WORK, OUTSIDE the tree, and the receipt is assembled on the local side.
# Session A's instruction was to stream results back and write the receipt locally; this is
# the version of that which needs no rule relaxed.
#
# THE INPUT SET IS DERIVED, NOT REMEMBERED. quoted_paths.txt comes from a regex over
# VALIDATION_LEDGER.md plus docs/analysis-note/*.tex intersected with the ignored-set walk
# (state/cluster-ignored-set-walk-20260812.json). An audit over a list assembled from memory
# tests the tree against the memory rather than the reverse (BEN-193).
#
# READS ONLY. sha256sum and stat. No file is opened for write inside the repo.
set -eo pipefail

REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold
WORK=/pscratch/sd/j/josephrb/mnv-digest-work
LIST="${WORK}/quoted_paths.txt"
JOB="${SLURM_JOB_ID:-nojob}"
OUT="${WORK}/quoted_digests.${JOB}.tsv"
LOG="${WORK}/quoted_digests.${JOB}.log"

mkdir -p "$WORK"

# Whole stream to a file; filter READS of it afterwards. Never pipe a diagnostic through
# tail/head at write time -- truncating at write time destroys the evidence (BEN-026).
{
  echo "=== digest_quoted job ${JOB} on $(hostname) at $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  echo "=== repo ${REPO} (READ ONLY)  work ${WORK}"
  echo "=== list ${LIST} ($(wc -l < "$LIST") paths)"

  n=0; ok=0; missing=0; bytes=0
  T0=$(date +%s)
  while IFS= read -r rel; do
    [ -z "$rel" ] && continue
    f="${REPO}/${rel}"
    n=$((n+1))
    if [ ! -f "$f" ]; then
      echo "[MISS] ${rel}"
      printf '%s\t%s\t%s\t%s\t%s\n' "$rel" "ABSENT" "ABSENT" "ABSENT" "ABSENT" >> "$OUT"
      missing=$((missing+1)); continue
    fi
    sz=$(stat -c %s "$f")
    mt=$(stat -c %y "$f")
    t0=$(date +%s.%N)
    sha=$(sha256sum "$f" | cut -d' ' -f1)
    t1=$(date +%s.%N)
    el=$(echo "$t1 - $t0" | bc)
    rate=$(echo "scale=2; $sz / $el / 1048576" | bc 2>/dev/null || echo NA)
    printf '%s\t%s\t%s\t%s\t%s\n' "$rel" "$sz" "$sha" "$mt" "$el" >> "$OUT"
    echo "[ok  ] ${rel} ${sz} B  ${sha}  ${el}s  ${rate} MiB/s"
    ok=$((ok+1)); bytes=$((bytes+sz))
  done < "$LIST"
  T1=$(date +%s)

  echo "=== totals: seen ${n} digested ${ok} missing ${missing} bytes ${bytes}"
  echo "=== wall_seconds_total $((T1-T0))"
  if [ "$((T1-T0))" -gt 0 ]; then
    echo "=== achieved_MB_per_s $(echo "scale=2; ${bytes} / $((T1-T0)) / 1000000" | bc)"
  fi
  echo "=== DONE at $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
} >>"$LOG" 2>&1

grep -E "totals|wall_seconds_total|achieved|MISS" "$LOG" || true
echo "[digest] tsv=${OUT}"
echo "[digest] log=${LOG}"

#!/bin/bash
#SBATCH --job-name=hpss_p3f_fe
#SBATCH --account=m3246
#SBATCH --qos=xfer
#SBATCH --time=12:00:00
#SBATCH --licenses=SCRATCH
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/p3f_pet_fullevent/logs/hpss_protect_%j.out
#SBATCH --error=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/p3f_pet_fullevent/logs/hpss_protect_%j.err
#
# PROTECT THE SATISFIED HALF OF QUARANTINE CAUSE 5 OFF PURGEABLE SCRATCH.
#
# nd-unfolding/p3f_pet_fullevent/final/ holds 120 selection-shifted FULL-EVENT lateral endpoint ROOTs
# (5 bands x 2 endpoints x 12 playlists) plus their 120 Gate-3 receipts, 1.1 TB, all 120 receipts
# verdict PASS, promoted GATE3_PROMOTED_PASS 2026-07-20T23:58Z
# (docs/orchestration/state/p3f-pet-gate3-promotion-56169838.json). MEASURED 2026-08-11: HPSS holds NO
# copy of this tree (`hsi ls` returns only ~/backups), so scratch is the SOLE copy.
#
# These are the "selection-complete detector samples" half of the 2026-07-12 quarantine's cause 5
# (VALIDATION_LEDGER.md:83-84) -- the one half of that cause already satisfied. Nine throw slabs of the
# adopted 5D ensemble were ALREADY lost off this filesystem (docs/OPEN_ITEMS.md item (g)), turning the
# adopted covariance into a 76.2% subsample. If these 120 go, cause 5 acquires a 120-endpoint C++
# event-loop re-dump in front of it against a binary that would have to be rebuilt from 486e53e.
#
# VERIFICATION IS BY DIGEST, NOT BY SIZE OR BY A LISTING. Per file: local md5 -> hsi put ->
# `hsi hashcreate` (computed SERVER-SIDE, so no 1.1 TB is transferred back) -> compare the two md5s AND
# the size read back from HPSS. A file counts as archived only when the digests match. This is
# deliberately a stronger standard than the Gate-3 source manifest set for itself ("per-file 9.4GB x120
# rehash not performed"): an archive that exists to survive a purge must not inherit the verification
# method that would miss a silent partial purge. `hashcreate` immediately after `put` also runs while
# the file is still in the HPSS disk cache, which is why the digest is affordable at all.
#
# RESUME GUARD VALIDATES COMPLETENESS, NOT EXISTENCE (BEN-023). A per-file marker is written ONLY after
# the digest match, via write-to-temp + rename so a marker is never half-written. A file is re-put
# unless its marker records a verified DIGEST match. A bare non-empty-size test used as completion
# proof is precisely the shape that let 7 partial slabs permanently block their own repair.
#
# (That sentence deliberately DESCRIBES the anti-pattern instead of quoting it. Spelling the token
# sequence out here -- even in a comment saying not to do it -- trips
# test_resume_guard.py::test_no_shell_file_reintroduces_a_size_only_resume_guard, which scans every
# line including comments. The guard is right and must not be weakened to accommodate prose; the
# comment-blindness is filed separately.)
#
# THE READBACK PARSE IS POWER-TESTED, both directions, on the live system before this was submitted:
#   positive  existing file            -> parses 12334, matches local            PASS
#   negative  absent from HPSS         -> parses EMPTY, guard cannot pass         PASS
#   negative  wrong expected size      -> mismatch branch fires                  PASS
#   negative  name that is a PREFIX of the real one -> no match (exact $NF test)  PASS
# and the digest path was proved end-to-end: server-side hashcreate returned
# 5e89461934bf030f0c4881f8dd0a2779, equal to the local md5 of the same file. Smoke artifacts removed.
set -eo pipefail

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
SRC="${REPO}/nd-unfolding/p3f_pet_fullevent/final"
MARKDIR="${REPO}/nd-unfolding/p3f_pet_fullevent/hpss_markers"
LOG_DIR="${REPO}/nd-unfolding/p3f_pet_fullevent/logs"
JOB="${SLURM_JOB_ID:-nojob}"
RUNLOG="${LOG_DIR}/hpss_protect_${JOB}.log"
MANIFEST="${REPO}/nd-unfolding/p3f_pet_fullevent/HPSS_ARCHIVE_MANIFEST.slurm-${JOB}.json"
HPSS_DIR="mnv-p3f-pet-fullevent-final"

mkdir -p "$MARKDIR" "$LOG_DIR"

# Exact-name field-5 extraction. $NF==base is what makes a prefix name unable to match (negative 3).
hpss_size() { hsi -q "ls -l ${HPSS_DIR}/$1" 2>&1 | awk -v b="$1" '$NF==b {print $5; exit}'; }
# hashcreate prints "<md5> (md5) /full/path"; take field 1 of the line carrying the basename.
hpss_md5()  { hsi -q "hashcreate ${HPSS_DIR}/$1" 2>&1 | awk -v b="$1" '$0 ~ b && $2=="(md5)" {print $1; exit}'; }

# Whole stream to a file; filter READS of it afterwards (BEN-026).
{
  echo "=== hpss_protect job ${JOB} on $(hostname) at $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  echo "=== src ${SRC} -> hpss:${HPSS_DIR}"
  hsi -q "mkdir -p ${HPSS_DIR}" 2>&1 || true

  n_total=0; n_skipped=0; n_ok=0; n_failed=0
  for f in "${SRC}"/*.root "${SRC}"/*.json; do
    base="$(basename "$f")"
    mark="${MARKDIR}/${base}.hpss.json"
    lsize="$(stat -c %s "$f")"
    n_total=$((n_total+1))

    # --- resume guard: requires a recorded DIGEST match, not a file's existence ------------------
    if [ -f "$mark" ]; then
      if grep -q '"digest_match": true' "$mark" 2>/dev/null; then
        echo "[skip] ${base} marker records a verified digest match"
        n_skipped=$((n_skipped+1)); continue
      fi
      echo "[redo] ${base} marker present but records NO verified digest match -- re-putting"
    fi

    lmd5="$(md5sum "$f" | cut -d' ' -f1)"
    echo "[put ] ${base} ${lsize} bytes local_md5 ${lmd5} at $(date -u '+%H:%M:%SZ')"
    if ! hsi -q "cd ${HPSS_DIR} ; put ${f} : ${base}" 2>&1; then
      echo "[FAIL] hsi put returned non-zero for ${base}"
      n_failed=$((n_failed+1)); continue
    fi

    # --- evidence is read BACK from HPSS; put's exit code is not the evidence --------------------
    rsize="$(hpss_size "$base" || true)"
    rmd5="$(hpss_md5 "$base" || true)"
    if [ "$rmd5" = "$lmd5" ] && [ "$rsize" = "$lsize" ]; then
      printf '{"file": "%s", "local_size": %s, "hpss_size": %s, "local_md5": "%s", "hpss_md5_server_side": "%s", "digest_match": true, "hpss_path": "%s/%s", "job": "%s", "verified_at_utc": "%s", "verification": "server-side hsi hashcreate md5 compared against local md5, plus size readback"}\n' \
        "$base" "$lsize" "$rsize" "$lmd5" "$rmd5" "$HPSS_DIR" "$base" "$JOB" \
        "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" > "${mark}.tmp"
      mv -f "${mark}.tmp" "$mark"
      echo "[ok  ] ${base} digest verified ${rmd5} size ${rsize}"
      n_ok=$((n_ok+1))
    else
      echo "[FAIL] ${base} verification failed: local md5 ${lmd5} hpss md5 '${rmd5}' | local size ${lsize} hpss size '${rsize}' -- NO marker written"
      n_failed=$((n_failed+1))
    fi
  done

  echo "=== totals: seen ${n_total} skipped ${n_skipped} verified ${n_ok} failed ${n_failed}"
  echo "=== DONE at $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
} >>"$RUNLOG" 2>&1

# Manifest is built from the MARKERS (verified state) and never from the loop's counters, so a crashed
# loop cannot leave a manifest claiming more than was verified.
python3 - "$SRC" "$MARKDIR" "$MANIFEST" "$JOB" "$HPSS_DIR" <<'PYEOF' >>"$RUNLOG" 2>&1
import glob, json, os, sys
src, markdir, out, job, hpss_dir = sys.argv[1:6]
files = sorted(glob.glob(os.path.join(src, "*.root")) + glob.glob(os.path.join(src, "*.json")))
entries, missing = [], []
for f in files:
    base = os.path.basename(f)
    m = os.path.join(markdir, base + ".hpss.json")
    rec = {"file": base, "local_size": os.path.getsize(f), "archived_digest_verified": False}
    if os.path.exists(m):
        try:
            d = json.load(open(m))
            rec.update({"local_md5": d.get("local_md5"),
                        "hpss_md5_server_side": d.get("hpss_md5_server_side"),
                        "hpss_size": d.get("hpss_size"),
                        "archived_digest_verified": bool(d.get("digest_match"))})
        except Exception as e:
            rec["marker_error"] = str(e)
    if not rec["archived_digest_verified"]:
        missing.append(base)
    entries.append(rec)
payload = {
    "schema": "p3f-pet-fullevent-hpss-archive-v2-digest",
    "job": job, "hpss_dir": hpss_dir, "source": src,
    "n_files": len(entries),
    "n_archived_digest_verified": sum(1 for e in entries if e["archived_digest_verified"]),
    "n_not_archived": len(missing),
    "not_archived": missing,
    "complete": len(missing) == 0,
    "verification_scope": (
        "Per file: local md5 (md5sum on scratch) compared against an md5 computed SERVER-SIDE by "
        "`hsi hashcreate`, plus a size read back from HPSS. No file is counted archived without a "
        "digest match. NOT verified: that HPSS will still return these bytes after a tape migration "
        "-- re-run `hsi hashverify` against the stored hash for that, which needs no local copy."),
    "entries": entries,
}
json.dump(payload, open(out, "w"), indent=2)
print(f"[manifest] {out} complete={payload['complete']} "
      f"digest_verified={payload['n_archived_digest_verified']}/{payload['n_files']}")
PYEOF

echo "[hpss] log=${RUNLOG}"
echo "[hpss] manifest=${MANIFEST}"
grep -E "totals|manifest|FAIL" "$RUNLOG" || true

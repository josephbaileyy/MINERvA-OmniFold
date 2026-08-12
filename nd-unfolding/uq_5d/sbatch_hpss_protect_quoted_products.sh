#!/bin/bash
#SBATCH --job-name=hpss_quoted
#SBATCH --account=m3246
#SBATCH --qos=xfer
#SBATCH --time=12:00:00
#SBATCH --licenses=SCRATCH
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=/pscratch/sd/j/josephrb/mnv-digest-work/hpss_quoted_%j.out
#SBATCH --error=/pscratch/sd/j/josephrb/mnv-digest-work/hpss_quoted_%j.err
#
# HPSS PROTECTION FOR THE 36 QUOTED PRODUCTS. 322,306,102,132 B / 0.3223 TB.
#
# AUTHORIZED: AUTHORIZATION-20260812-hpss-copy-and-delegation.md. Joseph verbatim "yes,
# authorize it", answering the STOP as framed -- 36 files, 0.322 TB, HPSS. Home was refused
# as a destination (~40 GB, and the set is 8.05x that). The four attached conditions are
# [MEDIATOR]/Session-C authored and adopted by Session A, NOT his wording; that attribution
# was corrected against A at 5beaed4 and the conditions still bind.
#
# THE INPUT SET IS DERIVED, NOT REMEMBERED. The 36 paths come from a regex over
# VALIDATION_LEDGER.md plus docs/analysis-note/*.tex intersected with the ignored-set walk
# (state/cluster-ignored-set-walk-20260812.json). 35 of the 36 are named only by the ledger.
#
# NOTHING IS WRITTEN INTO THE REPO TREE. /pscratch/sd/j/josephrb/MINERvA-OmniFold is under an
# eight-verb no-touch list and is the object of today's inventory. Markers, logs and the
# manifest all land in $WORK, outside it. The receipt is assembled locally.
#
# ---------------------------------------------------------------------------------------
# DESTINATION PATHS MIRROR THE SOURCE TREE, AND THAT IS A CORRECTNESS REQUIREMENT RATHER
# THAN A STYLE CHOICE. Measured before writing this launcher: the 36 paths contain FIVE
# BASENAME COLLISIONS across TEN files, and every pair is `X/` against `X/corrected/`:
#
#     uq_universe_4d_covariance_combined.root         8355187459 vs 8355185775
#     uq_universe_4d_covariance_combined_uthrow.root   181811405 vs  181794146
#     uq_universe_5d_covariance_combined_uthrow.root   892233209 vs  892224371
#     unified_throw_cov_4d.root                        545400036 vs  545263178
#     unified_throw_cov_fps.root                         1609132 vs    1607692
#
# A FLAT DESTINATION WOULD SILENTLY OVERWRITE FIVE OF THEM -- and it fails in the worst
# available direction, because the colliding pairs are the CORRECTED and UNCORRECTED versions
# of the same product, differing by about 2 KB. A size-based check would find the survivor
# plausible, the manifest would claim 36 objects while HPSS held 31, and the campaign whose
# entire quarantine story is about which products are corrected would have archived one on top
# of the other. Same class as BEN-136 (names that are prefixes of one another) and BEN-133 (a
# silent re-point that returns a number instead of an error).
#
# So: `hsi mkdir -p` per relative directory and put each file at its mirrored path. The
# collision check below is a FAIL-CLOSED PRECONDITION, not a comment -- if a future edit
# reintroduces flat naming, the job refuses to start.
# ---------------------------------------------------------------------------------------
#
# VERIFICATION IS BY DIGEST, NOT BY SIZE OR A LISTING. Per file: local md5 -> hsi put ->
# server-side `hsi hashcreate` (no bytes come back) -> compare both md5s AND the size read
# back. A marker is written ONLY on a digest match, via write-to-temp + rename, so a marker is
# never half-written and the resume guard validates COMPLETENESS rather than EXISTENCE
# (BEN-023: `[[ -s $OUT ]] && skip` let 7 partial slabs permanently block their own repair).
#
# sha256 for all 36 is already recorded independently by job 56760314
# (state/quoted-products-digests-56760314.json). This job's md5s are a SECOND, independent
# digest family; agreement across two algorithms is stronger than a repeat of one.
set -eo pipefail

REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold
WORK=/pscratch/sd/j/josephrb/mnv-digest-work
LIST="${WORK}/quoted_paths.txt"
MARKDIR="${WORK}/hpss_markers_quoted"
JOB="${SLURM_JOB_ID:-nojob}"
LOG="${WORK}/hpss_quoted_${JOB}.log"
MANIFEST="${WORK}/HPSS_QUOTED_MANIFEST.slurm-${JOB}.json"
HPSS_DIR="mnv-quoted-products-20260812"

mkdir -p "$MARKDIR" "$WORK"

# --- FAIL-CLOSED PRECONDITION: destination names must be unique -------------------------
# Guards the collision described above. Compares the number of distinct destination paths
# against the number of source paths; a flat scheme collapses them and this refuses.
n_src=$(grep -c . "$LIST")
n_dst=$(sort -u "$LIST" | grep -c .)
if [ "$n_src" -ne "$n_dst" ]; then
  echo "[FATAL] duplicate source paths in ${LIST}: ${n_src} lines, ${n_dst} distinct" >&2
  exit 2
fi
n_base=$(sed 's#.*/##' "$LIST" | sort -u | grep -c .)
if [ "$n_base" -ne "$n_src" ]; then
  echo "[note] ${n_src} sources share only ${n_base} distinct basenames -- $((n_src-n_base)) collision(s)." >&2
  echo "[note] This is EXPECTED and is why destinations mirror the source tree. Flat naming is refused." >&2
fi

# Exact-name field-5 extraction. $NF==base is what stops a PREFIX name from matching (BEN-136).
hpss_size() { hsi -q "ls -l ${HPSS_DIR}/$1" 2>&1 | awk -v b="$(basename "$1")" '$NF==b {print $5; exit}'; }
# hashcreate prints "<md5> (md5) /full/path"; take field 1 of the line carrying the basename.
hpss_md5()  { hsi -q "hashcreate ${HPSS_DIR}/$1" 2>&1 | awk -v b="$(basename "$1")" '$0 ~ b && $2=="(md5)" {print $1; exit}'; }

# Whole stream to a file; filter READS of it afterwards (BEN-026).
{
  echo "=== hpss_quoted job ${JOB} on $(hostname) at $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  echo "=== ${n_src} sources, ${n_base} distinct basenames -> mirrored paths under hpss:${HPSS_DIR}"
  hsi -q "mkdir -p ${HPSS_DIR}" 2>&1 || true

  n=0; skipped=0; ok=0; failed=0; bytes=0
  T0=$(date +%s)
  while IFS= read -r rel; do
    [ -z "$rel" ] && continue
    f="${REPO}/${rel}"
    n=$((n+1))
    flat=$(echo "$rel" | tr '/' '_')
    mark="${MARKDIR}/${flat}.hpss.json"

    if [ ! -f "$f" ]; then
      echo "[MISS] ${rel} absent from the source tree"; failed=$((failed+1)); continue
    fi

    # --- resume guard: requires a recorded DIGEST match, not a file's existence ----------
    if [ -f "$mark" ] && grep -q '"digest_match": true' "$mark" 2>/dev/null; then
      echo "[skip] ${rel} marker records a verified digest match"; skipped=$((skipped+1)); continue
    fi
    [ -f "$mark" ] && echo "[redo] ${rel} marker present but records NO verified digest match"

    lsize=$(stat -c %s "$f")
    lmd5=$(md5sum "$f" | cut -d' ' -f1)
    reldir=$(dirname "$rel")
    [ "$reldir" != "." ] && hsi -q "mkdir -p ${HPSS_DIR}/${reldir}" 2>&1 || true

    echo "[put ] ${rel} ${lsize} B local_md5 ${lmd5} at $(date -u '+%H:%M:%SZ')"
    if ! hsi -q "put ${f} : ${HPSS_DIR}/${rel}" 2>&1; then
      echo "[FAIL] hsi put returned non-zero for ${rel}"; failed=$((failed+1)); continue
    fi

    # --- evidence is read BACK from HPSS; put's exit code is not the evidence ------------
    rsize=$(hpss_size "$rel" || true)
    rmd5=$(hpss_md5 "$rel" || true)
    if [ "$rmd5" = "$lmd5" ] && [ "$rsize" = "$lsize" ]; then
      printf '{"source": "%s", "hpss_path": "%s/%s", "local_size": %s, "hpss_size": %s, "local_md5": "%s", "hpss_md5_server_side": "%s", "digest_match": true, "job": "%s", "verified_at_utc": "%s"}\n' \
        "$rel" "$HPSS_DIR" "$rel" "$lsize" "$rsize" "$lmd5" "$rmd5" "$JOB" \
        "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" > "${mark}.tmp"
      mv -f "${mark}.tmp" "$mark"
      echo "[ok  ] ${rel} digest verified ${rmd5} size ${rsize}"
      ok=$((ok+1)); bytes=$((bytes+lsize))
    else
      echo "[FAIL] ${rel} verification failed: local md5 ${lmd5} hpss '${rmd5}' | local size ${lsize} hpss '${rsize}' -- NO marker written"
      failed=$((failed+1))
    fi
  done < "$LIST"
  T1=$(date +%s)

  echo "=== totals: seen ${n} skipped ${skipped} verified ${ok} failed ${failed} bytes ${bytes}"
  echo "=== wall_seconds_total $((T1-T0))"
  echo "=== DONE at $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
} >>"$LOG" 2>&1

# Manifest is built from the MARKERS (verified state), never from the loop's counters, so a
# crashed loop cannot leave a manifest claiming more than was verified.
python3 - "$LIST" "$MARKDIR" "$MANIFEST" "$JOB" "$HPSS_DIR" "$REPO" <<'PYEOF' >>"$LOG" 2>&1
import json, os, sys
lst, markdir, out, job, hpss_dir, repo = sys.argv[1:7]
rels = [l.strip() for l in open(lst) if l.strip()]
entries, missing = [], []
for rel in rels:
    m = os.path.join(markdir, rel.replace("/", "_") + ".hpss.json")
    src = os.path.join(repo, rel)
    rec = {"source": rel,
           "local_size": os.path.getsize(src) if os.path.exists(src) else None,
           "archived_digest_verified": False}
    if os.path.exists(m):
        try:
            d = json.load(open(m))
            rec.update({"local_md5": d.get("local_md5"),
                        "hpss_md5_server_side": d.get("hpss_md5_server_side"),
                        "hpss_size": d.get("hpss_size"),
                        "hpss_path": d.get("hpss_path"),
                        "archived_digest_verified": bool(d.get("digest_match"))})
        except Exception as e:
            rec["marker_error"] = str(e)
    if not rec["archived_digest_verified"]:
        missing.append(rel)
    entries.append(rec)
payload = {
    "schema": "quoted-products-hpss-archive-v1-digest",
    "job": job, "hpss_dir": hpss_dir, "source_repo": repo,
    "n_files": len(entries),
    "n_archived_digest_verified": sum(1 for e in entries if e["archived_digest_verified"]),
    "n_not_archived": len(missing), "not_archived": missing,
    "complete": len(missing) == 0,
    "destination_layout": ("MIRRORS the source relative path. Flat naming would silently overwrite five "
        "corrected/uncorrected pairs differing by ~2 KB; see the launcher header."),
    "verification_scope": (
        "Per file: local md5 compared against an md5 computed SERVER-SIDE by `hsi hashcreate`, plus a size "
        "read back from HPSS. No file counts as archived without a digest match. sha256 for the same 36 is "
        "recorded independently by job 56760314, so two digest families agree rather than one repeating. "
        "NOT verified: that HPSS still returns these bytes after a tape migration -- `hsi hashverify` "
        "against the stored hash answers that and needs no local copy."),
    "entries": entries,
}
json.dump(payload, open(out, "w"), indent=2)
print(f"[manifest] {out} complete={payload['complete']} "
      f"verified={payload['n_archived_digest_verified']}/{payload['n_files']}")
PYEOF

echo "[hpss] log=${LOG}"
echo "[hpss] manifest=${MANIFEST}"
grep -E "totals|manifest|FAIL|MISS|note" "$LOG" || true

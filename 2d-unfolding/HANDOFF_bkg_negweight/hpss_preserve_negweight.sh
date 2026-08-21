#!/bin/bash
# HPSS DURABILITY STEP FOR THE HISTORICAL NEGATIVE-WEIGHT DIAGNOSTIC PRODUCTS.
#
# WHAT THIS PRESERVES, AND WHAT THE PRESERVATION DOES NOT MEAN
# ------------------------------------------------------------
# 247 ROOT products back the TWELVE real-data/production `\nw*` values in
# docs/analysis-note/app_negweight.tex: 8 under HANDOFF_bkg_negweight/runs/, 51 under
# uq/negweight_boot/, 188 under uq/negweight_uni/. They live ONLY on purgeable pscratch
# (/global/homes/j/josephrb/MINERvA-OmniFold is a symlink to /pscratch/sd/j/josephrb/...,
# measured, not assumed) and `.gitignore`'s blanket `*.root` keeps every one of them
# untracked. That is the OI-130 class: a quoted number whose evidence nothing binds.
#
# THEY ARE HISTORICAL DIAGNOSTIC EVIDENCE. Preserving them does NOT make the negative-weight
# arm a supported current production path, does not reopen the archived pre-freeze arm, and
# changes no default: the headline 2D path is and stays the binned per-reco-bin purity
# weight. Joseph's ruling for this step is explicit -- preserve, do NOT git-track the ROOT
# population, do NOT rerun the study.
#
# WHY TARS AND NOT 247 `hsi put` CALLS
# ------------------------------------
# The whole set is 13.53 MiB with a largest member of 56,659 B. Small files are the one shape
# HPSS is worst at, and NERSC's own guidance is to aggregate below ~100 MB. Four tars also
# make the RECOVERY test end-to-end and cheap: a `hashverify` over a tar reads every byte of
# every member, and extraction proves the members come back usable rather than merely
# digest-equal in place -- the gap RECEIPT-20260820-oi50-hashverify.md names in its own §5
# ("no object was restored and re-read end-to-end into a usable file").
#
# Per-file sha256 AND md5 for all 247 go into the committed manifest, so any single member
# can still be checked independently after recovery without trusting the tar as a unit.
#
# THE FILE LIST IS DERIVED FROM THE FILESYSTEM, NEVER HARDCODED, AND THE COUNTS ARE
# FAIL-CLOSED. 8/51/188 are the ruled scope; if a glob returns anything else the job refuses
# rather than archiving a subset that a count would later read as complete.
#
# VERIFICATION IS BY DIGEST READ BACK FROM HPSS, not by `put`'s exit code, not by a size, and
# not by a listing. Per tar: local sha256+md5 -> `hsi put` -> server-side `hsi hashcreate`
# md5 -> compare that md5 AND the size read back. A marker is written only on a match, via
# write-to-temp + rename, so the resume guard validates COMPLETENESS and not existence.
#
# NOTHING IS WRITTEN INTO THE REPO TREE. Work, logs, tars, markers and the manifest all land
# in $WORK, outside /pscratch/sd/j/josephrb/MINERvA-OmniFold.
#
# TRAPS THIS SCRIPT IS BUILT AROUND, all previously paid for in this repo:
#   * `hashverify -A <dir>` warns "is a directory - ignored" and exits 0. `-A` means
#     auto-schedule retrievals, NOT "all". Recursion is `-R`, which works. The per-command
#     usage is authoritative; hsi's general help omits hashverify from its recursion list.
#   * `hashverify` RECOMPUTES, so it reads every byte off tape. It is not a metadata read.
#   * A wrapper's last command becomes the job's exit status: OI-50's job read FAILED because
#     its final `grep -v` found nothing. Every rc that matters is captured UNPIPED to a file.
#   * A green gate must prove it did the work: a start marker is stamped BEFORE any transfer.
#
# Usage:  sbatch hpss_preserve_negweight.sh        (or: bash hpss_preserve_negweight.sh)
#
#SBATCH --job-name=hpss_negweight
#SBATCH --account=m3246
#SBATCH --qos=xfer
#SBATCH --time=04:00:00
#SBATCH --licenses=SCRATCH
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=/pscratch/sd/j/josephrb/negweight-durability-20260821/hpss_negweight_%j.out
#SBATCH --error=/pscratch/sd/j/josephrb/negweight-durability-20260821/hpss_negweight_%j.err
set -eo pipefail

REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold
WORK=/pscratch/sd/j/josephrb/negweight-durability-20260821
HPSS_DIR=mnv-negweight-historical-20260821
JOB="${SLURM_JOB_ID:-nojob}"

TARDIR="$WORK/tars"
MARKDIR="$WORK/markers"
LOG="$WORK/preserve_${JOB}.log"
mkdir -p "$TARDIR" "$MARKDIR"

# --- a green run must prove it did the work: marker BEFORE anything moves ----------------
date -u '+%Y-%m-%dT%H:%M:%SZ' > "$WORK/started.marker"
echo "marker stamped BEFORE work, job ${JOB} on $(hostname)" >> "$WORK/started.marker"

# Run-stamped so an idempotent RE-RUN cannot overwrite the first run's BEFORE reading. It did
# exactly that once: run 2 rewrote residency_before_migrate.txt after run 1 had already
# migrated, turning the pre-migration evidence into a post-migration reading under a
# "before" filename. A resume-safe script must not make its own earlier evidence unreadable.
STAMP=$(date -u '+%Y%m%dT%H%M%SZ')

RUNS_REL=2d-unfolding/HANDOFF_bkg_negweight/runs
BOOT_REL=2d-unfolding/uq/negweight_boot
UNI_REL=2d-unfolding/uq/negweight_uni

# --- derive the ruled scope, then refuse if it is not the ruled scope --------------------
list_roots() { (cd "$REPO" && ls -1 "$1"/*.root 2>/dev/null | sort) ; }

: > "$WORK/runs.paths"; list_roots "$RUNS_REL" > "$WORK/runs.paths"
: > "$WORK/boot.paths"; list_roots "$BOOT_REL" > "$WORK/boot.paths"
: > "$WORK/uni.paths";  list_roots "$UNI_REL"  > "$WORK/uni.paths"

n_runs=$(grep -c . "$WORK/runs.paths" || true)
n_boot=$(grep -c . "$WORK/boot.paths" || true)
n_uni=$(grep -c . "$WORK/uni.paths"  || true)

if [ "$n_runs" != "8" ] || [ "$n_boot" != "51" ] || [ "$n_uni" != "188" ]; then
  echo "[FATAL] ruled scope is 8/51/188; filesystem gives ${n_runs}/${n_boot}/${n_uni}." >&2
  echo "[FATAL] Refusing: a subset archived under a complete-looking count is the failure" >&2
  echo "[FATAL] this whole step exists to prevent. Investigate before re-running." >&2
  exit 2
fi

# The sidecars are NOT part of the ruled 247 and are archived under their own name so the
# two sets can never be confused. They are the producing witnesses values.tex cites
# (ia_*.log, the sbatch .out/.err carrying the printed totals), the universe-covariance
# rollup that \nwSystRatio's two operands were traced from, and the figures.
( cd "$REPO" && find "$RUNS_REL" "$BOOT_REL" "$UNI_REL" -type f ! -name '*.root' | sort ) \
  > "$WORK/sidecar.paths"
n_side=$(grep -c . "$WORK/sidecar.paths" || true)
( cd "$REPO" && ls -1 "$UNI_REL"/rollup/*.root 2>/dev/null | sort ) >> "$WORK/sidecar.paths"
sort -u -o "$WORK/sidecar.paths" "$WORK/sidecar.paths"
n_side=$(grep -c . "$WORK/sidecar.paths" || true)

cat "$WORK/runs.paths" "$WORK/boot.paths" "$WORK/uni.paths" > "$WORK/ruled247.paths"

{
  echo "=== hpss_negweight job ${JOB} on $(hostname) at $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  echo "=== ruled scope ${n_runs}/${n_boot}/${n_uni} = $((n_runs+n_boot+n_uni)) ROOTs"
  echo "=== beside-scope sidecars: ${n_side} files (own tar, own name, never counted in the 247)"

  # --- per-file digests, both families ---------------------------------------------------
  : > "$WORK/inventory.tsv"
  while IFS= read -r rel; do
    [ -z "$rel" ] && continue
    f="$REPO/$rel"
    printf '%s\t%s\t%s\t%s\t%s\n' \
      "$rel" "$(stat -c %s "$f")" "$(sha256sum "$f" | cut -d' ' -f1)" \
      "$(md5sum "$f" | cut -d' ' -f1)" "$(stat -c %y "$f")" >> "$WORK/inventory.tsv"
  done < "$WORK/ruled247.paths"
  : > "$WORK/sidecar_inventory.tsv"
  while IFS= read -r rel; do
    [ -z "$rel" ] && continue
    f="$REPO/$rel"
    printf '%s\t%s\t%s\t%s\t%s\n' \
      "$rel" "$(stat -c %s "$f")" "$(sha256sum "$f" | cut -d' ' -f1)" \
      "$(md5sum "$f" | cut -d' ' -f1)" "$(stat -c %y "$f")" >> "$WORK/sidecar_inventory.tsv"
  done < "$WORK/sidecar.paths"
  echo "=== digested $(grep -c . "$WORK/inventory.tsv") ruled + $(grep -c . "$WORK/sidecar_inventory.tsv") sidecar files"

  # --- tars: members are REPO-RELATIVE so extraction rebuilds the tree -------------------
  # --sort=name for a reproducible member order; owner/group zeroed so the archive does not
  # carry this account's numeric ids. mtimes are NOT normalised -- they are evidence.
  build_tar() { # $1 = tar basename, $2 = path list
    tar --sort=name --owner=0 --group=0 --numeric-owner \
        -cf "$TARDIR/$1" -C "$REPO" -T "$2"
    echo "[tar ] $1 $(stat -c %s "$TARDIR/$1") B from $(grep -c . "$2") members"
  }
  build_tar negweight_runs_8.tar    "$WORK/runs.paths"
  build_tar negweight_boot_51.tar   "$WORK/boot.paths"
  build_tar negweight_uni_188.tar   "$WORK/uni.paths"
  build_tar negweight_sidecars.tar  "$WORK/sidecar.paths"

  # --- the archive says what it is, off-repo -------------------------------------------
  cat > "$TARDIR/LABEL.txt" <<'LABEL_EOF'
HISTORICAL DIAGNOSTIC EVIDENCE -- NOT A SUPPORTED CURRENT PRODUCTION PATH.

MINERvA-OmniFold: unbinned background subtraction by negative-weight injection.
Products written 2026-07-07 .. 2026-07-11 on Perlmutter, preserved 2026-08-21.

WHAT THIS IS
  The 247 ROOT products backing the twelve real-data/production \nw* values in the
  analysis note's negative-weight appendix (App. B), plus their producing witnesses:
    negweight_runs_8.tar     8 files  2d-unfolding/HANDOFF_bkg_negweight/runs/*.root
    negweight_boot_51.tar   51 files  2d-unfolding/uq/negweight_boot/*.root
    negweight_uni_188.tar  188 files  2d-unfolding/uq/negweight_uni/*.root
    negweight_sidecars.tar            beside-scope: run logs, figures, and the
                                      uq/negweight_uni/rollup/ universe covariance.
                                      NOT part of the ruled 247.

WHAT IT IS NOT
  * NOT the headline 2D path. The published 2D result uses the BINNED per-reco-bin
    purity down-weight. Nothing here changes that default.
  * NOT a revival of the archived pre-freeze arm, and not authorization to run it.
  * NOT a publication uncertainty product. The two covariance ratios these support are
    agreement diagnostics between two background-subtraction realizations.
  * NOT reproducible by re-running: no run-time git HEAD was recorded, and the producer
    was uncommitted when these were written. See the manifest's `producer` block.

AUTHORITATIVE RECORD
  docs/orchestration/RECEIPT-20260821-negweight-hpss-durability.md and
  docs/orchestration/state/negweight-hpss-manifest-20260821.json in the
  MINERvA-OmniFold repository carry per-file sizes, sha256, md5, the producing commit,
  and the tested recovery route (2d-unfolding/HANDOFF_bkg_negweight/hpss_recover_negweight.sh).
LABEL_EOF
  echo "[label] $(stat -c %s "$TARDIR/LABEL.txt") B"

  # --- put + verify by digest read BACK from HPSS ----------------------------------------
  hsi -q "mkdir -p ${HPSS_DIR}" 2>&1 || true

  # Exact-name field extraction: $NF==base is what stops a PREFIX name from matching.
  hpss_size() { hsi -q "ls -l ${HPSS_DIR}/$1" 2>&1 | awk -v b="$1" '$NF==b {print $5; exit}'; }
  hpss_md5()  { hsi -q "hashcreate ${HPSS_DIR}/$1" 2>&1 | awk -v b="$1" '$0 ~ b && $2=="(md5)" {print $1; exit}'; }

  ok=0; failed=0
  for obj in negweight_runs_8.tar negweight_boot_51.tar negweight_uni_188.tar \
             negweight_sidecars.tar LABEL.txt; do
    mark="$MARKDIR/${obj}.hpss.json"
    if [ -f "$mark" ] && grep -q '"digest_match": true' "$mark" 2>/dev/null; then
      echo "[skip] ${obj} marker records a verified digest match"; ok=$((ok+1)); continue
    fi
    [ -f "$mark" ] && echo "[redo] ${obj} marker present but records NO verified digest match"
    lsize=$(stat -c %s "$TARDIR/$obj")
    lmd5=$(md5sum "$TARDIR/$obj" | cut -d' ' -f1)
    lsha=$(sha256sum "$TARDIR/$obj" | cut -d' ' -f1)
    echo "[put ] ${obj} ${lsize} B md5 ${lmd5} at $(date -u '+%H:%M:%SZ')"
    if ! hsi -q "put ${TARDIR}/${obj} : ${HPSS_DIR}/${obj}" 2>&1; then
      echo "[FAIL] hsi put non-zero for ${obj}"; failed=$((failed+1)); continue
    fi
    rsize=$(hpss_size "$obj" || true)
    rmd5=$(hpss_md5 "$obj" || true)
    if [ "$rmd5" = "$lmd5" ] && [ "$rsize" = "$lsize" ]; then
      printf '{"object": "%s", "hpss_path": "%s/%s", "local_size": %s, "hpss_size": %s, "local_sha256": "%s", "local_md5": "%s", "hpss_md5_server_side": "%s", "digest_match": true, "job": "%s", "verified_at_utc": "%s"}\n' \
        "$obj" "$HPSS_DIR" "$obj" "$lsize" "$rsize" "$lsha" "$lmd5" "$rmd5" "$JOB" \
        "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" > "${mark}.tmp"
      mv -f "${mark}.tmp" "$mark"
      echo "[ok  ] ${obj} server-side md5 ${rmd5} size ${rsize}"
      ok=$((ok+1))
    else
      echo "[FAIL] ${obj}: local md5 ${lmd5} hpss '${rmd5}' | local size ${lsize} hpss '${rsize}' -- NO marker"
      failed=$((failed+1))
    fi
  done
  echo "=== put/verify: ok ${ok} failed ${failed}"

  # --- tape residency ---------------------------------------------------------------------
  # A JUST-WRITTEN OBJECT IS NOT ON TAPE. HPSS writes into the disk cache at storage level 1
  # and migrates to tape later on its own schedule, so an `ls -V` taken straight after a
  # `put` reports DISK and an unwary reader records that as preservation. Level 1 = disk is
  # exactly the state this step exists to get out of: a disk-cache copy is not an archive.
  #
  # So residency is measured TWICE with an explicit `migrate` between, and BOTH readings are
  # kept. The before reading is what makes the after reading mean something -- without it,
  # "level 1 (tape)" could just as well have been true before this job ran.
  for obj in negweight_runs_8.tar negweight_boot_51.tar negweight_uni_188.tar \
             negweight_sidecars.tar LABEL.txt; do
    echo "--- BEFORE migrate: ls -V ${obj}"
    hsi -q "ls -V ${HPSS_DIR}/${obj}" 2>&1
  done > "$WORK/residency_before_migrate.${STAMP}.txt" 2>&1 || true

  hsi -q "migrate -R ${HPSS_DIR}" > "$WORK/migrate.${STAMP}.log" 2>&1
  echo $? > "$WORK/migrate.${STAMP}.rc"
  echo "=== migrate rc $(cat "$WORK/migrate.${STAMP}.rc")"

  for obj in negweight_runs_8.tar negweight_boot_51.tar negweight_uni_188.tar \
             negweight_sidecars.tar LABEL.txt; do
    echo "--- AFTER migrate: ls -V ${obj}"
    hsi -q "ls -V ${HPSS_DIR}/${obj}" 2>&1
    echo "--- AFTER migrate: dump ${obj}"
    hsi -q "dump ${HPSS_DIR}/${obj}" 2>&1 | grep -Ei "TimeLastRead|TimeLastWritten|StorageLevel" || true
  done > "$WORK/residency_after_migrate.${STAMP}.txt" 2>&1 || true
  echo "=== residency written (before and after migrate)"

  # --- archive-side inventory, independent of this job's counters ------------------------
  hsi -q "ls -lRD ${HPSS_DIR}" > "$WORK/archive_listing.txt" 2>&1 || true
  echo "=== archive listing written"
} >> "$LOG" 2>&1

# --- NEGATIVE CONTROL ON THE RESIDENCY INSTRUMENT ---------------------------------------
# A tape-residency check that has only ever been run on tape-resident objects has not been
# shown able to fail. So a throwaway object is put and read IMMEDIATELY, before any migrate:
# `ls -V` must report zero bytes at the tape level for it. That is both the power test and a
# reproduction of the state the five archive objects were in between put and migrate.
CTL_DIR=mnv-negweight-residency-control-20260821
CTL="$WORK/residency_negative_control.${STAMP}.txt"
{
  echo "=== RESIDENCY INSTRUMENT NEGATIVE CONTROL $(date -u '+%Y-%m-%dT%H:%M:%SZ') on $(hostname)"
  echo "=== A freshly-put object must show ZERO bytes at the tape level; an archive object"
  echo "=== after migrate must show its full byte count. Same instrument, same minute."
  printf 'negweight residency instrument negative control %s\n' "$STAMP" > "$WORK/residency_control.txt"
  hsi -q "mkdir -p ${CTL_DIR}" 2>&1 || true
  echo "--- put ---"
  hsi -q "put ${WORK}/residency_control.txt : ${CTL_DIR}/residency_control.txt" 2>&1
  echo "--- ls -V IMMEDIATELY after put: expect 1 (tape) 0, no data at this level ---"
  hsi -q "ls -V ${CTL_DIR}/residency_control.txt" 2>&1
  echo "--- contrast, an archive object AFTER migrate: expect bytes at the tape level ---"
  hsi -q "ls -V ${HPSS_DIR}/negweight_runs_8.tar" 2>&1
} > "$CTL" 2>&1 || true
echo "[hpss] residency negative control -> ${CTL}"

# --- hashverify: recomputes from the data, so it reads every byte off tape ---------------
# -R recurses (the per-command usage is authoritative). -A would mean auto-schedule and
# would silently no-op on a directory at exit 0, which is why it is NOT used.
# rc captured UNPIPED so no downstream filter can become the recorded status.
set +e
hsi -q "hashverify -R ${HPSS_DIR}" > "$WORK/hashverify.log" 2>&1
echo $? > "$WORK/hashverify.rc"
set -e

# --- coverage as a PATH-SET DIFF, not a count ------------------------------------------
# 5 of something is not 5 of the right thing, so the VERIFIED set is compared against the
# HASHED set as sets. The two commands print different shapes and BOTH were measured rather
# than assumed -- the first version of this block assumed both wrong and the step failed loudly
# instead of reporting a coverage it could not compute:
#
#   hashverify:  /home/j/josephrb/<dir>/<obj>: (md5) OK      <- absolute, trailing colon
#   hashlist:    <md5> md5 <dir>/<obj> [hsi]                 <- archive-relative, BARE `md5`
#
# `$2=="(md5)"` matches nothing in hashlist output. That mattered: it emptied one side, and an
# empty-set-vs-empty-set diff is EQUAL, which is the gate-that-cannot-fail shape this repo keeps
# paying for. Hence the non-empty floor below -- the diff alone is not allowed to be the check.
awk '/\(md5\) OK$/ {sub(/:$/, "", $1); print $1}' "$WORK/hashverify.log" \
  | sed 's#^/home/j/josephrb/##' | sort > "$WORK/verified.paths"
hsi -q "hashlist -R ${HPSS_DIR}" > "$WORK/hashlist.log" 2>&1 || true
awk '$2=="md5" {print $3}' "$WORK/hashlist.log" \
  | sed 's#^/home/j/josephrb/##' | sort > "$WORK/hashed.paths"

n_ver=$(grep -c . "$WORK/verified.paths" || true)
n_hsh=$(grep -c . "$WORK/hashed.paths" || true)
# rc recorded, never allowed to abort the script: an aborted step leaves NO rc, and a missing
# rc reads as "not checked" to one reader and "fine" to another.
set +e
diff "$WORK/verified.paths" "$WORK/hashed.paths" > "$WORK/coverage.diff" 2>&1
echo $? > "$WORK/coverage.rc"
set -e
if [ "$n_ver" -lt 5 ] || [ "$n_hsh" -lt 5 ]; then
  echo "COLLECTOR_BLIND verified=${n_ver} hashed=${n_hsh} (expected >= 5)" > "$WORK/coverage.verdict"
elif [ "$(cat "$WORK/coverage.rc")" = "0" ]; then
  echo "COVERAGE_EXACT verified=${n_ver} hashed=${n_hsh} sets identical" > "$WORK/coverage.verdict"
else
  echo "COVERAGE_MISMATCH verified=${n_ver} hashed=${n_hsh} see coverage.diff" > "$WORK/coverage.verdict"
fi

echo "[hpss] work=${WORK}"
echo "[hpss] hashverify.rc=$(cat "$WORK/hashverify.rc")  coverage.rc=$(cat "$WORK/coverage.rc")"
echo "[hpss] coverage: $(cat "$WORK/coverage.verdict")"
grep -E "FATAL|FAIL|put/verify|ruled scope|beside-scope|tar |label" "$LOG" || true
exit 0

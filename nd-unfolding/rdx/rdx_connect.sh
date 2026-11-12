#!/bin/bash
# RDX's connect (RDX-DECLARATION.md §3, §5; the director's rulings of 2026-11-12), one step per go, on one Perlmutter
# login node. Each step runs only on the director's go for this script's sha256, its launcher's and that step.
#   bash rdx_connect.sh SELF STEP PIN [LIMIT]
# STEP  what it does (submit steps: the fence, the cap gate, the launcher's own smoke, then sbatch)
#   s0  clone the deploy at PIN; pre-build provenance against S0's MANIFEST (a mismatch STOPs before any build); base
#       and patched builds from one synced tree; recorded modules; the runtime data manifest by O_NOATIME.
#   s1  submit the 1A pilot (rdx_s1_1A, 2:15:00).
#   c1  O_NOATIME copy of S0's base_cv.root; C-ALIGN-1A; C-TRUTHX; the z3 walk-timing probe.
#   s2  submit the other eleven playlists (rdx_s2_<PL>), each behind its own cap gate; needs c1's PASSes and the
#       director's gates/s2.ok naming PIN.
#   c2  per playlist: O_NOATIME copy of S1's zero loop, C-ALIGN-PL, C-TRUTHX; writes out/loops.sha256 only if all pass.
#   m   O_NOATIME copies of lat_zero.npz and lat_zero_bkg.npz; submit the merge job (rdx_s2_merge, LIMIT from
#       gates/merge.ok, set from the probe).
#   cm  C-TRUTHX-NPZ on the merged dump and sidecar; requires k1.json's PASS.
#   s3a, s3b  submit stage 3's arms (rdx_s3_a, rdx_s3_b, 0:22:00) from the second deploy at PIN (the pin that commits
#       nd-unfolding/rdx/rdx-inputs-SHA256SUMS), after gates/S3a.ok or S3b.ok.
# Every step: refuses unless the host is loginNN and no Slurm job is set; prints the purge-exposed MP-1 inputs' stat
# (S0's base_cv.root, S1's twelve zero loops, lat_zero.npz and lat_zero_bkg.npz) and STOPs if one is missing; checks
# the step's read set against the pinned policy-config.json and RDX's never-read list. No set -u.
SELF=$1; STEP=${2:?step}; PIN=${3:?pin}; LIMIT=${4:-}
B=/pscratch/sd/j/josephrb/rdx-20261112
D=$B/deploy; D3=$B/deploy3; OUT=$B/out; BUILD=$B/build
CANON=/pscratch/sd/j/josephrb/MINERvA-OmniFold
CANON_SRC=$CANON/MINERvA101/MINERvA-101-Cross-Section; OPT=$CANON/MINERvA101/opt
MPARAM=$OPT/etc/MParamFiles/data
MP1=/pscratch/sd/j/josephrb/measurement-paper/phase1/mp1
S0MAN=$MP1/s0/build/MANIFEST.sha256
BASECV=$MP1/s0/evloop/base_cv.root; BASECV_SHA=c76256a495d2deb7c213c2f8203b284bea640d90e697c495f5e11cedc830846b
ZERO=$MP1/s1/evloop/zero; LATD=$MP1/s1/lateral
PLS="1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P"
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
SYSPY=/usr/bin/python3
REPO=https://github.com/josephbaileyy/MINERvA-OmniFold.git
POLICY_REL=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/rpd-reco/prologue3-20261107/policy-config.json
FENCE='^(cov2d|t2a|ll5d|e96data|rpd_|rsn_|rdx_)'   # s1 and m: no other rdx_ job either
case "$STEP" in s2|s3a|s3b) FENCE='^(cov2d|t2a|ll5d|e96data|rpd_|rsn_)' ;; esac   # several rdx_ jobs by design

bail() { echo "REFUSED (nothing written): $*"; rm -f -- "$SELF"; exit 9; }
stop() { echo "STOP: $*"; echo "== rdx connect $STEP rc=8 $(date -u +%FT%TZ)"; rm -f -- "$SELF"; exit 8; }
case "$(hostname -s)" in login[0-9][0-9]) ;; *) bail "host $(hostname -s) is not a login node" ;; esac
[ -z "$SLURM_JOB_ID" ] || bail "a Slurm job is set ($SLURM_JOB_ID)"
case "$STEP" in s0|s1|c1|s2|c2|m|cm|s3a|s3b) ;; *) bail "step $STEP" ;; esac
[[ "$PIN" =~ ^[0-9a-f]{40}$ ]] || bail "pin $PIN is not a 40-hex commit"
DEP=$D; [[ "$STEP" == s3a || "$STEP" == s3b ]] && DEP=$D3
if [ "$STEP" = s0 ] || { [[ "$STEP" == s3a ]] && [ ! -e "$D3" ]; }; then
  [ ! -e "$DEP" ] || bail "$DEP exists"
  git clone --quiet "$REPO" "$DEP" || bail "clone failed"
  git -C "$DEP" -c advice.detachedHead=false checkout --quiet "$PIN" || stop "checkout of $PIN failed"
fi
head=$(git -C "$DEP" rev-parse HEAD 2>/dev/null); porc=$(git -C "$DEP" status --porcelain --untracked-files=all | wc -l)
[ "$head" = "$PIN" ] && [ "$porc" -eq 0 ] || stop "the deploy $DEP is not $PIN clean (HEAD=$head, $porc lines)"
R=$DEP/nd-unfolding/rdx
echo "node $(hostname) $(date -u +%FT%TZ) step $STEP pin $PIN; connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
echo "== the purge-exposed MP-1 inputs (stat only)"
ATIME=("$BASECV"); for pl in $PLS; do ATIME+=("$ZERO/runEventLoopOmniFold_5D_${pl}_zero.root"); done
ATIME+=("$LATD/lat_zero.npz" "$LATD/lat_zero_bkg.npz")
$SYSPY -I -B "$R/rdx_paths.py" atime "${ATIME[@]}" || stop "a purge-exposed MP-1 input is missing"
q=$(squeue --me -h -o '%i|%j|%T') || stop "squeue failed"
echo "squeue --me:"; printf '%s\n' "$q"
fence() { local h; h=$(squeue --me -h -o '%j|%T' | awk -F'|' -v r="$FENCE" '$1 ~ r'); [ -z "$h" ] || stop "fenced or rdx_ jobs are queued or running: $h"; }
policy() { $SYSPY -I -B "$R/rdx_paths.py" policy --config "$DEP/$POLICY_REL" --read "$@" || stop "a read path is protected"; }
capgate() {  # capgate NAME LIMIT
  mkdir -p "$OUT"; touch "$OUT/submissions.log"
  sacct -X -n -P --starttime=2026-11-12 -o JobID,JobName,State,ElapsedRaw,NNodes,TimelimitRaw > "$OUT/sacct.psv" || stop "sacct failed"
  $SYSPY -I -B "$R/rdx_cap.py" --sacct "$OUT/sacct.psv" --submissions "$OUT/submissions.log" --name "$1" --limit "$2" \
    || stop "the cap gate refuses $1 ($2)"
}
submit() {  # submit NAME LIMIT SCRIPT ARGS...
  local name=$1 lim=$2; shift 2
  fence; capgate "$name" "$lim"
  mkdir -p "$OUT/logs"
  local jid; jid=$(sbatch --parsable --job-name="$name" --time="$lim" --output="$OUT/logs/%x_%j.out" "$@") || stop "sbatch $name failed"
  echo "SUBMIT id=$jid name=$name limit=$lim utc=$(date -u +%FT%TZ)" | tee -a "$OUT/submissions.log"
  squeue -j "$jid" -o '%i|%j|%T|%l|%q' 2>&1
}
md5_of() { awk '$2 ~ /bld_'"$1"'\/runEventLoopOmniFold$/ && length($1) == 32 {print $1}' "$BUILD/MANIFEST.md5"; }

case "$STEP" in
s0)
  [ ! -e "$BUILD" ] || stop "$BUILD exists"
  policy "$CANON_SRC" "$OPT/lib" "$S0MAN" "$MPARAM"
  mkdir -p "$BUILD" || stop "mkdir $BUILD"
  for v in base rdx; do rsync -a --exclude 'build' --exclude 'build.*' "$CANON_SRC/" "$BUILD/src_$v/" || stop "rsync $v"; done
  (cd "$BUILD/src_rdx" && patch -p1 --forward < "$R/runEventLoopOmniFold-truthx.patch") || stop "the patch does not apply"
  cmp -s "$BUILD/src_base/runEventLoopOmniFold.cpp" "$CANON_SRC/runEventLoopOmniFold.cpp" || stop "base source is not canonical"
  diffs=$(diff -rq "$BUILD/src_base" "$BUILD/src_rdx" | sort)
  [ "$diffs" = "Files $BUILD/src_base/runEventLoopOmniFold.cpp and $BUILD/src_rdx/runEventLoopOmniFold.cpp differ" ] \
    || stop "unexpected source differences: $diffs"
  $PY -I -B "$R/rdx_provenance.py" --s0-manifest "$S0MAN" --canon-src "$CANON_SRC" --opt-lib "$OPT/lib" \
      --synced "$BUILD/src_base" --out "$BUILD/provenance.json" || stop "pre-build provenance failed (no build)"
  $SYSPY -I -B "$R/rdx_paths.py" manifest --root "$MPARAM" --out "$BUILD/RUNTIME.sha256" > "$BUILD/runtime.json" \
    || stop "the runtime data manifest failed"
  ( source "$CANON/setup_salloc_env.sh" > /dev/null 2>&1
    { echo "# modules"; module list 2>&1; echo "# compiler"; c++ --version 2>&1 | head -1; echo "# ROOT"; root-config --version 2>&1
    } > "$BUILD/environment.txt"
    for v in base rdx; do
      mkdir -p "$BUILD/bld_$v" && cd "$BUILD/bld_$v" || exit 6
      cmake "$BUILD/src_$v" -DCMAKE_INSTALL_PREFIX="$BUILD/opt_$v" -DMAT_DIR="$OPT/lib/cmake/MAT" \
        -DMAT-MINERvA_DIR="$OPT/lib/cmake/MAT-MINERvA" -DUnfoldUtils_DIR="$OPT/lib/cmake/UnfoldUtils" \
        -DGENIEXSecExtract_DIR="$OPT/lib/cmake/GENIEXSecExtract" > cmake.log 2>&1 || exit 7
      make -j 8 runEventLoopOmniFold > make.log 2>&1 || exit 8
    done ) || stop "the build failed (see $BUILD/bld_*/cmake.log, make.log)"
  md5sum "$BUILD"/bld_base/runEventLoopOmniFold "$BUILD"/bld_rdx/runEventLoopOmniFold > "$BUILD/MANIFEST.md5"
  sha256sum "$BUILD"/bld_base/runEventLoopOmniFold "$BUILD"/bld_rdx/runEventLoopOmniFold "$BUILD/provenance.json" \
    "$BUILD/RUNTIME.sha256" "$BUILD/environment.txt" > "$BUILD/MANIFEST.sha256"
  echo "== provenance"; cat "$BUILD/provenance.json"; echo "== environment"; cat "$BUILD/environment.txt"
  echo "== binaries"; cat "$BUILD/MANIFEST.md5"; echo "base md5 beside S0's a6b85ec3068536b0cb278b68d6f40359 (reported, not gated)"
  echo "== RUNTIME.sha256 $(sha256sum "$BUILD/RUNTIME.sha256" | cut -d' ' -f1) ($(wc -l < "$BUILD/RUNTIME.sha256") files)"
  ;;
s1)
  MD5=$(md5_of rdx); [ -n "$MD5" ] || stop "no patched binary in $BUILD/MANIFEST.md5"
  policy "$CANON/2d-unfolding/playlist_manifests/1A_MC.txt" "$CANON/2d-unfolding/playlist_manifests/1A_Data.txt" \
    /pscratch/sd/j/josephrb/minerva/minerva_large_files "$BUILD/bld_rdx/runEventLoopOmniFold"
  fence
  RDX_SMOKE=1 bash "$R/sbatch_rdx_evloop.sh" "$B" "$DEP" 1A "$BUILD/bld_rdx/runEventLoopOmniFold" "$MD5" || stop "the launcher's smoke failed"
  submit rdx_s1_1A 2:15:00 "$R/sbatch_rdx_evloop.sh" "$B" "$DEP" 1A "$BUILD/bld_rdx/runEventLoopOmniFold" "$MD5"
  ;;
c1)
  F=$OUT/evloop/runEventLoopOmniFold_RDX_1A.root; [ -s "$F" ] || stop "no pilot output $F"
  mkdir -p "$OUT/checks"; policy "$BASECV" "$F"
  [ -e "$OUT/stage/base_cv.root" ] || $SYSPY -I -B "$R/rdx_paths.py" stage --dest "$OUT/stage" "$BASECV" "$BASECV_SHA" || stop "staging base_cv failed"
  $PY -I -B -c "import uproot" || stop "the checker python has no uproot"
  $PY -I -B "$R/rdx_align.py" "$OUT/stage/base_cv.root" "$F" --out "$OUT/checks/align_1A.json"; ra=$?
  $PY -I -B "$R/rdx_truthx_rows.py" "$F" --out "$OUT/checks/truthx_rows_1A.json"; rt=$?
  ( source "$CANON/setup_salloc_env.sh" > /dev/null 2>&1; python -I -B "$R/rdx_probe_walk.py" "$F" --out "$OUT/checks/walk_probe.json" )
  echo "C-ALIGN-1A rc=$ra C-TRUTHX rc=$rt"; [ $ra -eq 0 ] && [ $rt -eq 0 ] || stop "C-ALIGN-1A or C-TRUTHX did not pass"
  echo "STAGE 1 CHECKS PASS"
  ;;
s2)
  for c in align_1A truthx_rows_1A; do grep -q '"verdict": "PASS"' "$OUT/checks/$c.json" 2>/dev/null || stop "$c records no PASS"; done
  grep -qx "pin=$PIN" "$OUT/gates/s2.ok" 2>/dev/null || stop "no gates/s2.ok naming $PIN"
  MD5=$(md5_of rdx); [ -n "$MD5" ] || stop "no patched binary"
  policy "$CANON/2d-unfolding/playlist_manifests" /pscratch/sd/j/josephrb/minerva/minerva_large_files
  for pl in $PLS; do
    [ "$pl" = 1A ] && continue
    lim=$(awk -v p="$pl" '$1 == p {print $2}' <<'EOF'
1B 1:00:00
1C 1:15:00
1D 3:30:00
1E 2:45:00
1F 3:45:00
1G 3:15:00
1L 1:00:00
1M 4:45:00
1N 2:45:00
1O 1:00:00
1P 1:00:00
EOF
)
    RDX_SMOKE=1 bash "$R/sbatch_rdx_evloop.sh" "$B" "$DEP" "$pl" "$BUILD/bld_rdx/runEventLoopOmniFold" "$MD5" || stop "smoke $pl"
    submit "rdx_s2_$pl" "$lim" "$R/sbatch_rdx_evloop.sh" "$B" "$DEP" "$pl" "$BUILD/bld_rdx/runEventLoopOmniFold" "$MD5"
    sleep 5   # sacct lags sbatch; unlisted ids are counted from submissions.log anyway
  done
  ;;
c2)
  mkdir -p "$OUT/checks" "$OUT/stage/zero"
  [ ! -e "$OUT/loops.sha256" ] || stop "$OUT/loops.sha256 exists"
  ok=1; : > "$OUT/checks/loops.sha256.partial"
  for pl in $PLS; do
    F=$OUT/evloop/runEventLoopOmniFold_RDX_${pl}.root; [ -s "$F" ] || stop "no output for $pl"
    Z=$ZERO/runEventLoopOmniFold_5D_${pl}_zero.root
    ZSHA=$($SYSPY -I -B -c "import sys; sys.path.insert(0, sys.argv[1]); import fd_ct_period_inputs as C; print(C.ZERO_LOOPS[sys.argv[2]])" "$DEP/nd-unfolding" "$pl") || stop "no zero-loop pin for $pl"
    [ -e "$OUT/stage/zero/$(basename "$Z")" ] || $SYSPY -I -B "$R/rdx_paths.py" stage --dest "$OUT/stage/zero" "$Z" "$ZSHA" || stop "staging $Z"
    $PY -I -B "$R/rdx_align.py" "$OUT/stage/zero/$(basename "$Z")" "$F" --out "$OUT/checks/align_$pl.json" || ok=0
    $PY -I -B "$R/rdx_truthx_rows.py" "$F" --out "$OUT/checks/truthx_rows_$pl.json" || ok=0
    echo "$(sha256sum "$F" | cut -d' ' -f1)  $(basename "$F")" >> "$OUT/checks/loops.sha256.partial"
  done
  [ $ok -eq 1 ] || stop "a per-playlist check did not pass (loops.sha256 not written)"
  mv "$OUT/checks/loops.sha256.partial" "$OUT/loops.sha256"; cat "$OUT/loops.sha256"; echo "STAGE 2 CHECKS PASS"
  ;;
m)
  [ -s "$OUT/loops.sha256" ] || stop "no loops.sha256"
  grep -qx "pin=$PIN" "$OUT/gates/merge.ok" 2>/dev/null && [ -n "$LIMIT" ] && grep -qx "limit=$LIMIT" "$OUT/gates/merge.ok" \
    || stop "no gates/merge.ok naming $PIN and limit $LIMIT"
  policy "$LATD/lat_zero.npz" "$LATD/lat_zero_bkg.npz" "$OUT/evloop"
  read -r LZ LB < <($SYSPY -I -B -c "import sys; sys.path.insert(0, sys.argv[1]); import fd_ct_period_inputs as C; print(C.MP1_ZERO['lat_npz'], C.MP1_ZERO['lat_bkg'])" "$DEP/nd-unfolding")
  for pair in "lat_zero.npz $LZ" "lat_zero_bkg.npz $LB"; do
    set -- $pair; [ -e "$OUT/stage/$1" ] || $SYSPY -I -B "$R/rdx_paths.py" stage --dest "$OUT/stage" "$LATD/$1" "$2" || stop "staging $1"
  done
  RDX_SMOKE=1 bash "$R/sbatch_rdx_merge.sh" "$DEP" "$PIN" "$B" "$LIMIT" || stop "the merge launcher's smoke failed"
  submit rdx_s2_merge "$LIMIT" "$R/sbatch_rdx_merge.sh" "$DEP" "$PIN" "$B" "$LIMIT"
  ;;
cm)
  grep -q '"verdict": "PASS"' "$OUT/checks/k1.json" 2>/dev/null || stop "k1.json records no PASS"
  $PY -I -B "$R/rdx_truthx_npz.py" "$OUT/dumps/lat_RDX_ALL.npz" "$OUT/dumps/truthx_RDX_ALL.npz" --out "$OUT/checks/truthx_npz.json" \
    || stop "C-TRUTHX-NPZ did not pass"
  sha256sum "$OUT"/dumps/lat_RDX_ALL.npz "$OUT"/dumps/lat_RDX_ALL_bkg.npz "$OUT"/dumps/truthx_RDX_ALL.npz | sed "s|$OUT/dumps/|./|"
  echo "MERGE CHECKS PASS"
  ;;
s3a|s3b)
  J=S3a; N=rdx_s3_a; [ "$STEP" = s3b ] && { J=S3b; N=rdx_s3_b; }
  RDX_SMOKE=1 bash "$R/sbatch_rdx_arms.sh" "$DEP" "$PIN" "$B" "$J" || stop "the arms launcher's smoke failed"
  submit "$N" 0:22:00 "$R/sbatch_rdx_arms.sh" "$DEP" "$PIN" "$B" "$J"
  ;;
esac
echo "== rdx connect $STEP rc=0 $(date -u +%FT%TZ)"
rm -f -- "$SELF"; exit 0

#!/bin/bash
# POSITIVE CONTROL ON THE GUARD SET -- the real launcher and the real files, both directions.
#
# WHY THIS EXISTS. Four protections on this path were asserted-but-inert and each was caught only
# by measurement: the keyword search that authorized every candidate; rc 1 admitting a routing
# document; `variant` living in a docstring nothing read; and `--run-class` never passed, so the
# `adoptable: false` refusal was conditioned on a value no caller supplied. Unit tests passed every
# time, because they exercise the predicate and not the launcher. So this runs the launcher.
#
# ⚠ ONE DIRECTION IS NOT REACHABLE HERE, AND THAT IS ITSELF A MEASURED FACT, NOT AN EXCUSE.
# `run_m1_projection.sh` takes `MNV_ADOPTION_RECORD` as a MANDATORY operand at :35 and its REFUSAL
# 1/1a exit 3 at :46-95, BEFORE the projector is invoked at :99. So the launcher cannot reach the
# variant guard, let alone produce, without an adoption record carrying `ADOPTS-SHA256:` matched to
# the measured digest of the source. Only Joseph writes that. Manufacturing one here would be
# performing the act the guard exists to require, so legs A1/A2 measure the launcher's own gate in
# both directions and legs B1-B4 exercise the variant guard through the projector on the same files.
#
# NOTHING HERE ADOPTS. Leg B4's product is a CONTROL and is named so. It is NOT the PROJ
# deliverable: PROJ re-runs through the launcher after ADOPT, with the adoption record in place.
set -uo pipefail
W="${MNV_W:?}"; D="${MNV_D:?}"; P="${MNV_P:?}"
AMEND="$W/docs/orchestration/AMENDMENT-20260918-spec-6.4-candidate-specific-null-exception.md"
OUTD="$D/guardset-control"; mkdir -p "$OUTD"
cd "$W/nd-unfolding"
PY=~/.conda/envs/root_6_28/bin/python3

echo "=== HEAD $(cd "$W" && git rev-parse --short HEAD) ==="
echo "=== measured digests of the two candidates ==="
sha256sum "$P/z-cv.npz" "$P/z-mean.npz"
echo "=== the exception record exists and names the source ==="
ls -l "$AMEND"; grep -c '3d7465f66fbe66b0dfcf09b6fc51249f227fb33e97ae40bc78dda90275e918c5' "$AMEND"

run() {  # run <label> <expect-rc> <must-contain> <cmd...>
  # ⚠ THIS CHECKER WAS BROKEN ON ITS FIRST RUN AND THAT IS WHY IT IS SHAPED THIS WAY.
  # It used to test `expect=REFUSE and rc==0 -> FAIL`. In 58549890 legs B1-B3 SEGFAULTED at
  # rc=139 and every one of them was reported satisfied, because 139 is not 0. Three guards that
  # never executed read as three guards that fired. That is the assessor's finding reproduced
  # inside the instrument built to check for it: uniform failure indistinguishable from success.
  # A refusal is now an EXACT exit code AND its own message. A crash is named as a crash.
  local label="$1" want_rc="$2" must="$3"; shift 3
  echo; echo "################ $label  (expect rc=$want_rc, containing: ${must:0:44})"
  local rc=0; "$@" > "$OUTD/$label.out" 2> "$OUTD/$label.err" || rc=$?
  echo "rc=$rc"
  if [ "$rc" -ge 128 ]; then
    echo "*** CONTROL FAILED: $label CRASHED with signal $((rc-128)); it did not reach any guard"
    tail -4 "$OUTD/$label.err" | sed 's/^/      /'
    return 0
  fi
  if [ "$rc" -ne "$want_rc" ]; then
    echo "*** CONTROL FAILED: $label exited $rc, expected $want_rc"
  fi
  if [ -n "$must" ] && ! grep -qF -- "$must" "$OUTD/$label.out" "$OUTD/$label.err"; then
    echo "*** CONTROL FAILED: $label did not emit the expected text: $must"
  fi
  echo "--- stderr tail ---"; tail -5 "$OUTD/$label.err"
}

# ---- LEG A: the ACTUAL LAUNCHER, its own gate, both directions --------------------------------
export MNV_CODE_ROOT="$W" MNV_DATA_ROOT="$P" MNV_SRC_HIST=hCov_combined5d_total_uthrow \
       MNV_DST_MASK=receiving-cells MNV_EXPECT_VARIANT=cv
run A1_launcher_no_adoption_record 3 "no adoption record" env \
  MNV_ADOPTION_RECORD="$OUTD/does-not-exist.md" MNV_SRC_COV="$P/z-cv.npz" \
  MNV_SRC_CV="$P/z-cv.npz" MNV_OUT="$OUTD/A1.root" bash run_m1_projection.sh
# A2 is the real-path form of the three-document regression: a record that NAMES the right bytes
# and discusses the exception at length still does not ADOPT them.
# A3 closes gap 5's other arm: the exception operand SET but pointing at nothing. It refuses
# before any file is read, so it costs nothing. Its check precedes REFUSAL 1, so it fires even
# without a valid adoption record -- which is the only reason this arm is reachable today.
run A3_exception_set_but_missing 3 "MNV_ADOPTION_EXCEPTION set but no record" env \
  MNV_ADOPTION_EXCEPTION="$OUTD/no-such-exception.md" \
  MNV_ADOPTION_RECORD="$OUTD/does-not-exist.md" MNV_SRC_COV="$P/z-cv.npz" \
  MNV_SRC_CV="$P/z-cv.npz" MNV_OUT="$OUTD/A3.root" bash run_m1_projection.sh

run A2_launcher_exception_record_is_not_an_adoption 3 "does not state an adoption" env \
  MNV_ADOPTION_RECORD="$AMEND" MNV_SRC_COV="$P/z-cv.npz" \
  MNV_SRC_CV="$P/z-cv.npz" MNV_OUT="$OUTD/A2.root" bash run_m1_projection.sh

# ---- LEG B: the variant guard, the actual files, both directions and both crossings ----------
AX=(--src-hist hCov_combined5d_total_uthrow --src-axes pt,pz,eavail,q3,W --keep-axes eavail,W)
run B1_publication_from_MEAN_variant 1 "mean-centering alone is disqualified" $PY project_cov_nd.py \
  --src-cov "$P/z-mean.npz" --src-cv "$P/z-mean.npz" "${AX[@]}" \
  --run-class publication --expect-variant mean --out "$OUTD/B1.root"
run B2_cv_file_declared_mean 1 "declares variant 'cv'" $PY project_cov_nd.py \
  --src-cov "$P/z-cv.npz" --src-cv "$P/z-cv.npz" "${AX[@]}" \
  --run-class publication --expect-variant mean --out "$OUTD/B2.root"
run B3_mean_file_declared_cv 1 "declares variant 'mean'" $PY project_cov_nd.py \
  --src-cov "$P/z-mean.npz" --src-cv "$P/z-mean.npz" "${AX[@]}" \
  --run-class publication --expect-variant cv --out "$OUTD/B3.root"
# B4 is the only leg that WRITES, so it is the only one that needs ROOT. Sourcing the
# environment here and nowhere else is deliberate: B1-B3 above prove the refusals are reachable
# on a bare interpreter, which is the condition a reviewer exercises them in.
source "$W/setup_salloc_env.sh" >/dev/null 2>&1 || true
# B5 closes gap 4, THE PRIORITY. --run-class was once passed zero times, which left the
# `adoptable: false` refusal unreachable -- and that refusal is the most load-bearing guard for
# THIS adoption, because it is what stops a NON-PASSING source being published WITHOUT the
# exception. Every other leg passes publication WITH the exception, so the guard that makes this
# source special has never fired. This is that case: publication + cv + NO exception.
run B5_publication_cv_but_NO_exception 1 "records \`adoptable: false\`" $PY project_cov_nd.py \
  --src-cov "$P/z-cv.npz" --src-cv "$P/z-cv.npz" "${AX[@]}" \
  --run-class publication --expect-variant cv --out "$OUTD/B5.root"

run B4_CONTROL_publication_from_CV_variant 0 "" $PY project_cov_nd.py \
  --src-cov "$P/z-cv.npz" --src-cv "$P/z-cv.npz" "${AX[@]}" \
  --run-class publication --expect-variant cv --adoption-exception "$AMEND" \
  --out "$OUTD/B4_CONTROL_NOT_THE_DELIVERABLE.root"

echo; echo "=== B4's receipt: the fields that must record the identity check ==="
$PY - <<'PYEOF'
import json, glob, sys
for r in sorted(glob.glob("/pscratch/sd/j/josephrb/zdet-DIAGNOSTIC-20260918/guardset-control/*.receipt.json")):
    d = json.load(open(r))
    print(r.split("/")[-1])
    for k in ("runClass","runClassStatus","src_variant_declared","src_variant_measured",
              "adoption_exception","proj_sha256"):
        if k in d: print(f"   {k:24s} {str(d[k])[:150]}")
    sm = d.get("src_metadata", {})
    for k in ("variant","adoptable","scientific_acceptance"):
        if k in sm: print(f"   src_metadata.{k:11s} {sm[k]!r}")
PYEOF
echo; echo "GUARDSET CONTROL COMPLETE -- read the rc and the expect line for each leg."

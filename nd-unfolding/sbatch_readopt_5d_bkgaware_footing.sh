#!/bin/bash
#SBATCH --job-name=readopt5d_footing
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=32 --mem=180G --time=06:00:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=uq_5d/readopt_footing_%j.out --error=uq_5d/readopt_footing_%j.err
#
# BKGAWARE FOOTING RE-ADOPTION (BEN-102). Fills the one empty cell of a 2x2 in (footing x J28).
#
# WHY THIS EXISTS. `sbatch_j28_adopt_5d.sh` passes the J28-corrected --uthrow correctly and NEVER
# passes --combined, so it fell through to `adopt_unified_5d.py:76-77`'s default -- the NON
# background-aware combined product. Proven from the products themselves, not from the launcher:
# `adopt_unified_5d.py:166` stamps `sqrt_tr_old` = the sqrt-trace of the --combined input it was
# given, and the two published values carry 4.357790406860002e-38 (bkgaware) while the two proposed
# replacements carry 4.345454363683128e-38 (non-bkgaware). See
# uq_5d/receipt_construction_contract_5d.json.
#
# THIS ADOPTS NOTHING. The 2026-07-12 quarantine stands, causes 1-6 are open, and values.tex is
# untouched. This produces the footing-matched CANDIDATE so it is ready when the gate opens.
#
# PREDECLARED, with a pre-registered value:
#   docs/orchestration/PREDECLARE-20260811-bkgaware-footing-readopt.md
#   A1_pred = 5.259971e-38 * (5.807716e-38 / 5.802416e-38) = 5.264776e-38 under NO interaction.
#   Branches: B1 controls reproduce + A1 hits the prediction; B2 controls reproduce + A1 misses
#   (a measured interaction between the flux fix and the footing -- physics, escalate); B3 controls
#   do NOT reproduce (a second difference exists and the BEN-102 diagnosis is unsafe -- STOP);
#   B4 UNRESOLVED (unreadable input, OOM, or a missing per-band hCov in the bkgaware file).
#
# NOTHING IS RE-THROWN OR RE-COMBINED. The input throw ROOT is the existing corrected one, unchanged.
#
# TWO RULES THIS LAUNCHER OBEYS THAT ITS PREDECESSOR DID NOT:
#  1. NO `| tail`/`| head` ANYWHERE (BEN-026). `sbatch_j28_adopt_5d.sh:109,111` truncated both
#     adoptions to 25 lines each. The evidence happened to survive with ~7 lines of margin -- which
#     is luck, not a design. Here the whole stream reaches the .out file. That launcher is left
#     BYTE-UNCHANGED so it stays faithful to the run it documents; this is a new script.
#  2. --out IS PASSED EXPLICITLY ON ALL FOUR ARMS. `adopt_unified_5d.py:79-80` defaults --out to the
#     July product and opens it RECREATE, so taking the default would destroy a historical artifact
#     AND let the CV-centered arm silently clobber the mean-centered one, leaving one file that looks
#     like both.
set -eo pipefail   # NOT -u: conda activate aborts under nounset (AGENTS.md)
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1 OMP_NUM_THREADS=32
cd "${REPO}/nd-unfolding"

TAG="20260811_footing"
OUTD="uq_5d/readopt_${TAG}"
mkdir -p "${OUTD}"

UTHROW="uq_5d/unified_throw_cov_5d_fluxfix_20260806_full160.root"
COMB_BKG="uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware.root"
COMB_NON="uq_5d/universe_stage2_5d/uq_universe_5d_covariance_combined.root"

# --- 0. fail closed on inputs, and on the per-band inventory adopt_unified_5d actually needs ------
# Branch B4 exists because a missing hCov_universe5d_<band> in the bkgaware file would make arm A1
# unbuildable by construction. Check it BEFORE spending an hour, and check BOTH files so the failure
# is attributable to one of them rather than to "something".
python3 - "$UTHROW" "$COMB_BKG" "$COMB_NON" <<'PY'
import sys, os
import ROOT
ROOT.gErrorIgnoreLevel = ROOT.kError
uthrow, comb_bkg, comb_non = sys.argv[1:4]
VERT = ["2p2h", "CCQEPauliSupViaKF", "FrAbs_pi", "FrElas_N", "HighQ2", "LowQ2", "MaCCQE",
        "MaRES", "MFP_N", "MvRES", "Rvn2pi", "Rvp2pi", "Flux"]   # adopt_unified_5d.VERT_BANDS
fail = []
for p in (uthrow, comb_bkg, comb_non):
    if not os.path.exists(p):
        fail.append(f"missing input: {p}")
if fail:
    sys.exit("[gate FAIL] " + "; ".join(fail))
f = ROOT.TFile.Open(uthrow, "READ")
for k in ("C_unified", "C_blocksum", "hJointMeanShift"):
    if not f.Get(k):
        fail.append(f"{uthrow} lacks {k}")
n = f.Get("n_throws")
print(f"[gate] {uthrow}: n_throws={n.GetVal() if n else 'ABSENT'}")
null = f.Get("fixed_seed_null_norm")
print(f"[gate] {uthrow}: fixed_seed_null_norm={null.GetVal() if null else 'ABSENT (cause-4 trap)'}")
f.Close()
for label, p in (("bkgaware", comb_bkg), ("non-bkgaware", comb_non)):
    g = ROOT.TFile.Open(p, "READ")
    have = [b for b in VERT if g.Get(f"hCov_universe5d_{b}")]
    tot = g.Get("hCov_combined5d_total")
    print(f"[gate] {label}: {len(have)}/13 vertical bands present; "
          f"hCov_combined5d_total={'present' if tot else 'ABSENT'}")
    if len(have) != 13:
        fail.append(f"{label} missing bands: {sorted(set(VERT) - set(have))}")
    if not tot:
        fail.append(f"{label} lacks hCov_combined5d_total")
    g.Close()
if fail:
    sys.exit("[gate FAIL] " + "; ".join(fail))
print("[gate] inputs complete on both footings -- B4 excluded before any work")
PY

# --- 1..4. the four arms. Each writes its own labelled file; none takes a default -----------------
run_arm () {  # $1=label $2=combined $3=out $4=extra-flag
  echo ""
  echo "########## ARM $1  --combined $2 ${4:-} ##########"
  python3 adopt_unified_5d.py --uthrow "${UTHROW}" --combined "$2" --out "$3" ${4:-}
  echo "########## ARM $1 done -> $3 ##########"
}

run_arm A1_bkgaware_meancentered "${COMB_BKG}" "${OUTD}/adopted_bkgaware_meancentered_${TAG}.root"
run_arm A2_bkgaware_cvcentered   "${COMB_BKG}" "${OUTD}/adopted_bkgaware_cvcentered_${TAG}.root"   --cv-centered
run_arm C1_control_nonbkg_meancentered "${COMB_NON}" "${OUTD}/control_nonbkg_meancentered_${TAG}.root"
run_arm C2_control_nonbkg_cvcentered   "${COMB_NON}" "${OUTD}/control_nonbkg_cvcentered_${TAG}.root" --cv-centered

echo ""
echo "=== the historical products must be UNTOUCHED by this job ==="
for p in uq_5d/universe_stage2_5d/uq_universe_5d_covariance_combined_uthrow.root \
         uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware_uthrow.root \
         uq_5d/rescaled_20260806_full160/adopted_meancentered_20260806_full160.root; do
  TZ=UTC stat -c '%y %s %n' "$p" 2>/dev/null || echo "  (absent) $p"
done

echo ""
echo "[done] four arms in ${OUTD}"
echo "[done] NOTHING ADOPTED. Read C1/C2 against 5.2600e-38 / 5.6609e-38 before reading A1/A2 at all;"
echo "[done] if the controls do not reproduce, that is branch B3 and A1/A2 are not a candidate."

#!/bin/bash
# ==================================================================================================
# EXPIRY CLAUSE (c) RERUN -- all arms, through the launcher's own adopt segment, at PRODUCTION
# DIMENSION, with real ROOT.
#
# NOT `set -e`: every arm must run and report ITS OWN exit code. An aborting driver would turn one
# unexpected result into "the rest did not fire", which is the failure mode that makes a control
# suite unreadable.
# ==================================================================================================
set -uo pipefail

WT="${WT:?worktree}"                 # clean detached worktree under test
SB="${SB:?sandbox}"                  # all writes live here
HARNESS="${HARNESS:?harness dir}"
MIRROR="$SB/mirror"
ND="$MIRROR/nd-unfolding"
LOGS="$SB/logs"
REAL_ARCHIVE="/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware_uthrow.root"
ARCHIVE_DATE="2026-07-14"            # the real archive's mtime; the PREDATES_ARCHIVE excuse's operand
MEAN_ART="adopted_uthrow.root"
CV_ART="adopted_uthrow_cvcentered.root"
MEAN_OUT="uq_universe_5d_covariance_combined_bkgaware_uthrow.root"
CV_OUT="uq_universe_5d_covariance_combined_bkgaware_uthrow_cvcentered.root"

# DIMENSION. 10694 is the only value a verdict may quote; MNV_N exists so the whole suite can be
# rehearsed at a small size to shake out harness bugs before spending the real run.
MNV_N="${MNV_N:-10694}"
NEGBIN=$(( MNV_N > 5000 ? 4242 : MNV_N / 2 ))
BIN_CLIP=$(( MNV_N > 1000 ? 777 : 3 ))
BIN_RAW=$(( MNV_N > 200 ? 100 : 1 ))

# ONE RUN PER SANDBOX. Rehearsal had two concurrent runs sharing one sandbox because a timed-out
# ssh left the first alive; they interleaved into one results.tsv and one arm scored FIRED off the
# OTHER run's stale artifact. A suite whose arms can read a previous run's files is not a suite.
if ! mkdir "$SB/.lock" 2>/dev/null; then
  echo "[FATAL] $SB/.lock exists: another run owns this sandbox. Remove it only after checking"
  echo "        that no run_arms.sh is alive (pgrep -f run_arms.sh)."
  exit 1
fi
trap 'rmdir "$SB/.lock" 2>/dev/null' EXIT

mkdir -p "$LOGS"
RESULTS="$SB/results.tsv"
: > "$RESULTS"

say() { echo "=== $* ==="; }
record() { printf '%s\t%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4" "$5" >> "$RESULTS"; }

# ---------------------------------------------------------------------------- the executing bytes
say "PROVENANCE"
echo "[prov] host $(hostname)"
echo "[prov] worktree HEAD $(git -C "$WT" rev-parse HEAD)"
echo "[prov] worktree dirty entries: $(git -C "$WT" status --porcelain | wc -l)"
echo "[prov] python3 $(python3 -c 'import sys;print(sys.version.split()[0])')  numpy $(python3 -c 'import numpy;print(numpy.__version__)')  ROOT $(python3 -c 'import ROOT;print(ROOT.gROOT.GetVersion())' 2>/dev/null)"
for m in mii_adopt_unified_5d_stamped.py mii_anchor_comparator.py mii_root_payload_classes.py \
         adopt_unified_5d.py seed_offset_policy.py receipt_candidate_stamps_5d.py \
         sbatch_finalize_5d_bkgaware_gpu.sh; do
  echo "[prov] file   $(sha256sum "$WT/nd-unfolding/$m" | cut -d' ' -f1)  $m"
  echo "[prov] gitblob $(git -C "$WT" rev-parse "HEAD:nd-unfolding/$m")  $m"
done

# ---------------------------------------------------------------------------- the symlink mirror
# WHY A MIRROR. The launcher cds into the repo and adopt_unified_5d.py's --prod default is RELATIVE,
# so the segment must run from an nd-unfolding whose cwd holds products/5d/. Writing that into the
# worktree would dirty the tree whose digests this verdict binds. So: every nd-unfolding entry is
# SYMLINKED (so the bytes that execute are provably the worktree's), and only products/ and uq_5d/
# are real directories in the sandbox.
say "MIRROR"
rm -rf "$MIRROR"; mkdir -p "$ND/products/5d" "$ND/uq_5d"
ln -sfn "$WT/docs" "$MIRROR/docs"                 # BINDING_RECEIPT resolves through this
ln -sfn "$WT/2d-unfolding" "$MIRROR/2d-unfolding"
for e in "$WT"/nd-unfolding/*; do
  b="$(basename "$e")"
  case "$b" in products|uq_5d) continue;; esac
  ln -sfn "$e" "$ND/$b"
done
echo "[mirror] $(find "$ND" -maxdepth 1 -type l | wc -l) symlinks; products/ and uq_5d/ are real"
echo "[mirror] receipt resolves: $(test -f "$MIRROR/docs/orchestration/state/ben106-stamp-verify-active-56695424.json" && echo yes || echo NO)"

# ------------------------------------------------------------------- extract + self-test the segment
say "SEGMENT"
bash "$HARNESS/extract_segment.sh" "$WT/nd-unfolding/sbatch_finalize_5d_bkgaware_gpu.sh" \
     "$SB/launcher_adopt_segment.sh" || exit 1
bash "$HARNESS/selftest_segment.sh" "$SB/launcher_adopt_segment.sh"
if [[ $? -ne 0 ]]; then echo "[FATAL] harness negative control failed; no arm below is readable"; exit 1; fi

if [[ "${DRYRUN:-0}" == "1" ]]; then
  echo "[dryrun] plumbing verified; stopping before any adopt run"
  exit 0
fi

# ---------------------------------------------------------------------------- base payload
say "BASE PAYLOAD (production dimension)"
echo "[base] DIMENSION = $MNV_N $([[ "$MNV_N" == 10694 ]] && echo "(production)" || echo "(HARNESS REHEARSAL -- NOT A VERDICT)")"
MNV_ND="$ND" python3 "$HARNESS/build_base.py" --out "$SB/base" --n "$MNV_N" --neg-bin "$NEGBIN" || exit 1
cp "$SB/base/prod_payload.root" "$ND/products/5d/xsec_5d_MEFHC_5iter_lgbm.root"
echo "[base] prod in place: $(ls -l "$ND/products/5d/xsec_5d_MEFHC_5iter_lgbm.root" | awk '{print $5}') bytes"

# ---------------------------------------------------------------------------- helpers
variant() {  # variant <arm> <combined-variant> <g1seed> <g1off> <g1decl> <g2seed> <g2off> <g2decl>
  python3 "$HARNESS/make_variant.py" --base "$SB/base" --dest "$ND/uq_5d/$1" \
    --combined-variant "$2" \
    --g1-seed "$3" --g1-offset "$4" --g1-declared "$5" \
    --g2-seed "$6" --g2-offset "$7" --g2-declared "$8"
}

segment() {  # segment <arm> <k or "undeclared">  -> SEG_RC
  local arm="$1" k="$2"
  local u="uq_5d/$arm/unified_throw_cov_5d.root"
  local c="uq_5d/$arm/universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware.root"
  local o="uq_5d/$arm/universe_stage2_5d_bkgaware"
  # ${VAR:?} INSIDE the subshell: the launcher's own options line is `set -eo pipefail` with NO -u,
  # so an empty UTHROW/COMB would expand to nothing and adopt would answer about a DIFFERENT subject
  # without erroring. Asserted here rather than trusted.
  [[ -f "$ND/$u" && -f "$ND/$c" && -d "$ND/$o" ]] || { echo "[FAIL] arm $arm inputs missing"; SEG_RC=97; return; }
  (
    cd "$ND" || exit 96
    export UTHROW="${u:?}" COMB="${c:?}" OUTD="${o:?}" PYTHONUNBUFFERED=1
    if [[ "$k" == "undeclared" ]]; then unset MNV_EST_SEED_OFFSET; else export MNV_EST_SEED_OFFSET="$k"; fi
    echo "[arm $arm] MNV_EST_SEED_OFFSET=${MNV_EST_SEED_OFFSET-<unset>}  UTHROW=$UTHROW  COMB=$COMB"
    bash "$SB/launcher_adopt_segment.sh"
  )
  SEG_RC=$?          # read UNPIPED: this is the segment's status, not a tail's
  echo "[arm $arm] SEGMENT EXIT = $SEG_RC"
}

gate() {  # gate <tag> <artifact> <archive> <member> <offset>  -> GATE_RC, log at $LOGS/gate_<tag>.log
  local tag="$1"
  ( cd "$ND" && PYTHONUNBUFFERED=1 python3 mii_anchor_comparator.py \
      --artifact "$2" --archive "$3" --member "$4" --offset "$5" --archive-date "$ARCHIVE_DATE" ) \
      > "$LOGS/gate_$tag.log" 2>&1
  GATE_RC=$?          # read UNPIPED and BEFORE anything else touches it
  cat "$LOGS/gate_$tag.log"
  echo "[gate $tag] EXIT = $GATE_RC  (0=PASS 1=INCOMPLETE 2=FAIL)"
}

# The OI-147 measurement, stated as a count so it is falsifiable from the log rather than from prose:
# how many keys came out of `audit_uncomparable` EXCUSED-BUT-UNVERIFIED. The previous clause (c) run
# measured EIGHT of these in every arm; that is exactly what OI-147 claims to have closed.
uncovered_count() { grep -c "EXCUSED BY THE ARCHIVE'S AGE AND NOT VERIFIED BY ANYTHING" "$LOGS/gate_$1.log"; }
partial_count()   { grep -c "PARTIAL COMPARISON" "$LOGS/gate_$1.log"; }

mutate() { python3 "$HARNESS/mutate.py" "$@"; }


# ==================================================================================================
#                                            THE ARMS
# Each arm records EXPECTED and OBSERVED. A suite in which nothing refuses proves nothing, so the
# summary at the bottom is a comparison, not a list.
# ==================================================================================================

# --------------------------------------------------------------- ARM 1: the positive, complete gate
say "ARM 1 -- present-seed k=0 product; the COMPLETE gate must PASS"
variant A1 pos 42 0 1 1000 0 1
segment A1 0
A1DIR="$ND/uq_5d/A1/universe_stage2_5d_bkgaware"
if [[ "$SEG_RC" -eq 0 ]]; then
  python3 "$HARNESS/inspect_diag.py" --member "$A1DIR/$MEAN_OUT"
  python3 "$HARNESS/make_archive.py" --member "$A1DIR/$MEAN_OUT" --out "$SB/archive_pos.root"
  python3 "$HARNESS/make_archive.py" --member "$A1DIR/$CV_OUT"   --out "$SB/archive_pos_cv.root"
  gate A1 "$MEAN_ART" "$SB/archive_pos.root" "$A1DIR/$MEAN_OUT" 0
  echo "[A1] uncovered-by-anything keys = $(uncovered_count A1)   PARTIAL COMPARISON lines = $(partial_count A1)"
  record A1 "present-seed k=0, COMPLETE gate, matched archive" "PASS(0)" "$GATE_RC" \
         "$([[ "$GATE_RC" -eq 0 ]] && echo POSITIVE-PASSED || echo UNEXPECTED)"

  # The cv-centered sibling the launcher builds in the same segment. It exercises the OTHER arm of
  # CONFIG_CENTERING, which is the key whose mismatch mii_root_payload_classes calls "the single
  # worst outcome this path can produce".
  gate A1C "$CV_ART" "$SB/archive_pos_cv.root" "$A1DIR/$CV_OUT" 0
  record A1C "cv-centered sibling, COMPLETE gate" "PASS(0)" "$GATE_RC" \
         "$([[ "$GATE_RC" -eq 0 ]] && echo POSITIVE-PASSED || echo UNEXPECTED)"

  # ARM 1R: the SAME member against the REAL 892 MB archive. This is the direct successor to the
  # previous run's arm A, and the number that matters is uncovered_count: it measured EIGHT.
  say "ARM 1R -- the same member vs the REAL archive (OI-147's own measurement, re-taken)"
  gate A1R "$MEAN_ART" "$REAL_ARCHIVE" "$A1DIR/$MEAN_OUT" 0
  echo "[A1R] uncovered-by-anything keys = $(uncovered_count A1R)   PARTIAL COMPARISON lines = $(partial_count A1R)"
  record A1R "real archive; expect payload-value FAIL and ZERO uncovered keys" \
         "FAIL(2), uncovered=0" "$GATE_RC uncovered=$(uncovered_count A1R) partial=$(partial_count A1R)" \
         "$([[ "$(uncovered_count A1R)" -eq 0 ]] && echo OI147-CLOSED || echo OI147-STILL-OPEN)"
else
  record A1 "present-seed k=0, COMPLETE gate" "segment exit 0" "segment exit $SEG_RC" BLOCKED
fi

# --------------------------------------------------- ARM 2: OI-149, declared adopter / unhooked legs
say "ARM 2 -- declared adopter over TWO UNDECLARED/UNHOOKED legs; the wrapper must REFUSE (OI-149)"
variant A2 pos 42 0 0 1000 0 0
segment A2 0
record A2 "declared k=0 adopter, both legs est_seed_offset_declared=0" "segment exit != 0" \
       "segment exit $SEG_RC" "$([[ "$SEG_RC" -ne 0 ]] && echo FIRED || echo DID-NOT-FIRE)"

# ------------------------------------------------------------- ARM 4: legitimate NEGATIVE raw entry
say "ARM 4 -- a legitimate NEGATIVE raw diagonal entry; must PASS and stay ZERO when clipped"
variant A4 neg 42 0 1 1000 0 1
segment A4 0
A4DIR="$ND/uq_5d/A4/universe_stage2_5d_bkgaware"
if [[ "$SEG_RC" -eq 0 ]]; then
  python3 "$HARNESS/inspect_diag.py" --member "$A4DIR/$MEAN_OUT" --bin "$NEGBIN"
  python3 "$HARNESS/make_archive.py" --member "$A4DIR/$MEAN_OUT" --out "$SB/archive_neg.root"
  gate A4 "$MEAN_ART" "$SB/archive_neg.root" "$A4DIR/$MEAN_OUT" 0
  record A4 "negative raw diag entry, clipped stays 0" "PASS(0)" "$GATE_RC" \
         "$([[ "$GATE_RC" -eq 0 ]] && echo POSITIVE-PASSED || echo UNEXPECTED)"
else
  record A4 "negative raw diag entry" "segment exit 0" "segment exit $SEG_RC" BLOCKED
fi

# ------------------------------------------------- ARM 6 (payload power): the comparison is not vacuous
# Arm 1's archive is a CLONE of arm 1's member, so its payload agreement is true by construction.
# THAT MAKES ARM 1 A CONTROL ON THE GATE, NOT ON THE PAYLOAD -- so the payload comparison needs its
# own power control at production dimension, or "PASS" in arm 1 cannot be distinguished from a
# comparison that compares nothing.
say "ARM P -- payload POWER control: arm 1's member against arm 4's archive; must FAIL on payload"
if [[ -f "$SB/archive_neg.root" && -f "$A1DIR/$MEAN_OUT" ]]; then
  gate A6 "$MEAN_ART" "$SB/archive_neg.root" "$A1DIR/$MEAN_OUT" 0
  record A6 "mismatched payload at 10694^2, bit-exact digests" "FAIL(2)" "$GATE_RC" \
         "$([[ "$GATE_RC" -eq 2 ]] && echo FIRED || echo DID-NOT-FIRE)"
else
  record A6 "payload power control" "FAIL(2)" "inputs missing" BLOCKED
fi

# ------------------------------------------------------- ARM 3: corrupted / inconsistent hDiagCombinedOld
say "ARM 3 -- a corrupted or inconsistent hDiagCombinedOld; must FAIL"
M1="$A1DIR/$MEAN_OUT"
if [[ -f "$M1" ]]; then
  # 3a: the clipped histogram no longer the clip of its own raw pre-image.
  mutate --in "$M1" --out "$SB/m_A3a.root" --set-bin "hDiagCombinedOld@${BIN_CLIP}=1e-77"
  gate A3a "$MEAN_ART" "$SB/archive_pos.root" "$SB/m_A3a.root" 0
  record A3a "clipped diagonal not the clip of its raw pre-image" "FAIL(2)" "$GATE_RC" \
         "$([[ "$GATE_RC" -eq 2 ]] && echo FIRED || echo DID-NOT-FIRE)"

  # 3b: half a pair is not a state.
  mutate --in "$M1" --out "$SB/m_A3b.root" --drop hDiagCombinedOld
  gate A3b "$MEAN_ART" "$SB/archive_pos.root" "$SB/m_A3b.root" 0
  record A3b "hDiagCombinedOld absent, raw present (half a pair)" "FAIL(2)" "$GATE_RC" \
         "$([[ "$GATE_RC" -eq 2 ]] && echo FIRED || echo DID-NOT-FIRE)"

  # 3c: shapes differ between the pair.
  mutate --in "$M1" --out "$SB/m_A3c.root" --pad-bins "hDiagCombinedOld=-1"
  gate A3c "$MEAN_ART" "$SB/archive_pos.root" "$SB/m_A3c.root" 0
  record A3c "clipped shorter than raw (shape mismatch)" "FAIL(2)" "$GATE_RC" \
         "$([[ "$GATE_RC" -eq 2 ]] && echo FIRED || echo DID-NOT-FIRE)"

  # 3d: THE PROBE FOR THE MISSING EXPECTED_ELEMENTS ENTRY. Both histograms lengthened by one ZERO
  # bin, so the pair stays mutually consistent AND the raw sum is mathematically unchanged. Neither
  # diagonal has an EXPECTED_ELEMENTS row, so the coverage branch prints and does not assert. If this
  # is ADMITTED the length gap is REACHABLE. If it is refused, read WHY before calling it covered:
  # appending an element changes numpy's pairwise blocking, so a refusal may come from the trace
  # moving in the last ulps rather than from any check on length.
  mutate --in "$M1" --out "$SB/m_A3d.root" --pad-bins "hDiagCombinedOld=1" --pad-bins "hDiagCombinedOldRaw=1"
  gate A3d "$MEAN_ART" "$SB/archive_pos.root" "$SB/m_A3d.root" 0
  record A3d "PROBE: pair zero-padded to 10695; raw sum unchanged mathematically" "unknown - measured" \
         "$GATE_RC" "$([[ "$GATE_RC" -eq 0 ]] && echo GAP-REACHABLE || echo REFUSED-SEE-LOG)"

  # 3e: the control that stops 3d being read as more general than it is.
  mutate --in "$M1" --out "$SB/m_A3e.root" --pad-bins "hDiagCombinedOld=-1" --pad-bins "hDiagCombinedOldRaw=-1"
  gate A3e "$MEAN_ART" "$SB/archive_pos.root" "$SB/m_A3e.root" 0
  record A3e "CONTROL: pair truncated to 10693; raw sum genuinely changes" "FAIL(2)" "$GATE_RC" \
         "$([[ "$GATE_RC" -eq 2 ]] && echo FIRED || echo DID-NOT-FIRE)"
fi

# ----------------------------------------------- ARM 5: a raw-diagonal mutation that moves the trace
say "ARM 5 -- a raw-diagonal mutation that changes the RAW TRACE; must FAIL"
M4="$A4DIR/$MEAN_OUT"
if [[ -f "$M4" ]]; then
  # 5a is the ISOLATED form and it needs arm 4's fixture. Making the already-negative entry MORE
  # negative leaves clip(raw) at 0.0, so _clip_consistency still PASSES -- the only thing that moves
  # is the raw sum. So this arm tests the sqrt_tr_old recomputation ALONE, with the clip check as a
  # live negative control on itself.
  # SCALED IN PLACE, never read out and piped back. In rehearsal the read-out form produced an EMPTY
  # argument -- stderr was suppressed and `tail -1` swallowed the failure -- and the arm then gated a
  # STALE file from a previous run and recorded FIRED. A negative control that mutates nothing and
  # reports a refusal is the worst possible arm, so the mutation now fails closed if the bin does not
  # move (mutate.py --scale-bin).
  echo "[A5a] doubling arm 4's raw[$NEGBIN] magnitude: stays negative, so clip(raw) is still 0.0"
  mutate --in "$M4" --out "$SB/m_A5a.root" --scale-bin "hDiagCombinedOldRaw@${NEGBIN}=2.0"
  gate A5a "$MEAN_ART" "$SB/archive_neg.root" "$SB/m_A5a.root" 0
  record A5a "raw entry made more negative: clip unchanged, RAW TRACE moves" "FAIL(2)" "$GATE_RC" \
         "$([[ "$GATE_RC" -eq 2 ]] && echo FIRED || echo DID-NOT-FIRE)"
fi
if [[ -f "$M1" ]]; then
  mutate --in "$M1" --out "$SB/m_A5b.root" --set-bin "hDiagCombinedOldRaw@${BIN_RAW}=3.3e-79"
  gate A5b "$MEAN_ART" "$SB/archive_pos.root" "$SB/m_A5b.root" 0
  record A5b "raw entry changed on a positive bin (clip AND trace move)" "FAIL(2)" "$GATE_RC" \
         "$([[ "$GATE_RC" -eq 2 ]] && echo FIRED || echo DID-NOT-FIRE)"
fi

# ==================================================================================================
#              ARM 6 -- THE EXISTING IDENTITY NEGATIVE CONTROLS, re-run at production dimension
# The previous clause (c) run fired these at N=4. They are re-run here because (i) OI-149 changed the
# code they run through, and (ii) an arm that fired on a 4-bin fixture has not fired on the artifact
# the gate will actually see.
# ==================================================================================================

# --- B1/B2: an UNHOOKED leg, both directions. At k=1200 a leg that stamps its own baseline is
# --- provably wrong, which is the power control on the substantive baseline invariant.
say "ARM 6/B1 -- g1 leg at its BASELINE while the process declares k=1200; must REFUSE"
variant B1 pos 42 1200 1 2200 1200 1
segment B1 1200
record B1 "unhooked g1 leg (seed 42) vs declared k=1200" "segment exit != 0" "segment exit $SEG_RC" \
       "$([[ "$SEG_RC" -ne 0 ]] && echo FIRED || echo DID-NOT-FIRE)"

say "ARM 6/B2 -- the same in the OTHER direction: g2 leg at its baseline; must REFUSE"
variant B2 pos 1242 1200 1 1000 1200 1
segment B2 1200
record B2 "unhooked g2 leg (seed 1000) vs declared k=1200" "segment exit != 0" "segment exit $SEG_RC" \
       "$([[ "$SEG_RC" -ne 0 ]] && echo FIRED || echo DID-NOT-FIRE)"

say "ARM 6/B3 -- CROSS-MEMBER: legs built at k=1100, process declares k=1200; must REFUSE"
variant B3 pos 1142 1100 1 2100 1100 1
segment B3 1200
record B3 "legs at k=1100, process declares k=1200" "segment exit != 0" "segment exit $SEG_RC" \
       "$([[ "$SEG_RC" -ne 0 ]] && echo FIRED || echo DID-NOT-FIRE)"

# --- C1/C2: the flag contradicts its own seed, both directions. Mutations of a GOOD product, so the
# --- refusal is attributable to the flag and to nothing about how the product was built.
if [[ -f "$M1" ]]; then
  say "ARM 6/C1 -- g1 _checked flipped to 0 with the seed still present; must REFUSE"
  mutate --in "$M1" --out "$SB/m_C1.root" --set-int "upstream_estimator_seed_g1_checked=0"
  gate C1 "$MEAN_ART" "$SB/archive_pos.root" "$SB/m_C1.root" 0
  record C1 "flag=0 while upstream_estimator_seed_g1 present" "FAIL(2)" "$GATE_RC" \
         "$([[ "$GATE_RC" -eq 2 ]] && echo FIRED || echo DID-NOT-FIRE)"

  say "ARM 6/C2 -- g2 seed deleted with its flag still 1; must REFUSE"
  mutate --in "$M1" --out "$SB/m_C2.root" --drop upstream_estimator_seed_g2
  gate C2 "$MEAN_ART" "$SB/archive_pos.root" "$SB/m_C2.root" 0
  record C2 "flag=1 while upstream_estimator_seed_g2 ABSENT" "FAIL(2)" "$GATE_RC" \
         "$([[ "$GATE_RC" -eq 2 ]] && echo FIRED || echo DID-NOT-FIRE)"

  say "ARM 6/D1 -- the stamped g1 seed mutated to 9999; the baseline recomputation must REFUSE"
  # D1 IS THE ARM THAT ESTABLISHES POWER OVER THE SUBSTANTIVE CHECK. Deleting the
  # baseline+offset recomputation from verify_leg_identity would turn this arm GREEN, which is what
  # makes arm 1's `[identity] OK` non-vacuous.
  mutate --in "$M1" --out "$SB/m_D1.root" --set-int "upstream_estimator_seed_g1=9999"
  gate D1 "$MEAN_ART" "$SB/archive_pos.root" "$SB/m_D1.root" 0
  record D1 "stamped g1 seed 9999 != baseline 42 + offset 0" "FAIL(2)" "$GATE_RC" \
         "$([[ "$GATE_RC" -eq 2 ]] && echo FIRED || echo DID-NOT-FIRE)"
fi

# --- D2: the ABSENT-SEED arm. The writer tolerates a leg with no seed (absence must be a readable
# --- state); the GATE must not, for a DECLARED member.
say "ARM 6/D2 -- declared member whose g1 leg carries NO estimator_seed; wrapper admits, gate must REFUSE"
variant D2 pos none 0 1 1000 0 1
segment D2 0
D2DIR="$ND/uq_5d/D2/universe_stage2_5d_bkgaware"
if [[ "$SEG_RC" -eq 0 ]]; then
  gate D2 "$MEAN_ART" "$SB/archive_pos.root" "$D2DIR/$MEAN_OUT" 0
  record D2 "declared member, g1 leg has no seed" "segment 0 then FAIL(2)" "segment 0, gate $GATE_RC" \
         "$([[ "$GATE_RC" -eq 2 ]] && echo FIRED || echo DID-NOT-FIRE)"
else
  record D2 "declared member, g1 leg has no seed" "segment 0 then FAIL(2)" "segment exit $SEG_RC" \
         "SEGMENT-REFUSED-INSTEAD"
fi

# --- E: the UNDECLARED route. Not a mismatch -- UNVERIFIABLE, and it must still fail. This is the arm
# --- that makes OI-149's hole the one that mattered: because the undeclared route is properly refused,
# --- laundering an unhooked leg through a DECLARED adopter was the only remaining door.
say "ARM 6/E -- UNDECLARED adopter, seeds present; identity must be UNVERIFIABLE and the gate must FAIL"
variant E pos 42 0 0 1000 0 0
segment E undeclared
EDIR="$ND/uq_5d/E/universe_stage2_5d_bkgaware"
if [[ "$SEG_RC" -eq 0 ]]; then
  gate E "$MEAN_ART" "$SB/archive_pos.root" "$EDIR/$MEAN_OUT" 0
  record E "undeclared adopter, undeclared legs" "segment 0 then FAIL(2)" "segment 0, gate $GATE_RC" \
         "$([[ "$GATE_RC" -eq 2 ]] && echo FIRED || echo DID-NOT-FIRE)"
else
  record E "undeclared adopter" "segment 0 then FAIL(2)" "segment exit $SEG_RC" "SEGMENT-REFUSED-INSTEAD"
fi

# ---------------------------------------------------------------- GATE 2's discharge on real bytes
say "SUPPLEMENTARY -- the shipped TH2D read route on the REAL archive (gate 2's discharge)"
( cd "$ND" && python3 mii_anchor_comparator.py \
    --read-one-matrix "$REAL_ARCHIVE:hCov_combined5d_total_uthrow" ) > "$LOGS/gate2_read.log" 2>&1
G2RC=$?
cat "$LOGS/gate2_read.log"
record G2 "read_one_matrix_for_gate2 on the real 892 MB archive" "ok(0)" "$G2RC" \
       "$([[ "$G2RC" -eq 0 ]] && echo OK || echo UNEXPECTED)"

# ==================================================================================================
say "SUMMARY"
printf '%-6s %-62s %-22s %-30s %s\n' ID DESCRIPTION EXPECTED OBSERVED DISPOSITION
while IFS=$'\t' read -r a b c d e; do
  printf '%-6s %-62s %-22s %-30s %s\n' "$a" "$b" "$c" "$d" "$e"
done < "$RESULTS"
echo
echo "[summary] results.tsv at $RESULTS ; per-arm gate logs under $LOGS"

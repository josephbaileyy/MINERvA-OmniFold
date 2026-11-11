#!/bin/bash
# ENS1 stage-2 analysis under addendum A1 (declaration §5; the bound ensemble_estimator_analyze.py --stage 2): 0 node-h,
# login node, from a /dev/shm copy of itself ($1), after the stage-2 full post-run connect read PASS and its receipt went
# to the director. In order:
#   refusals before anything is written: the stage-2 post-run's done file reads 0 and its s2-full-read.json says PASS;
#     stage 1's ens1_stage1.json is at its receipted sha256 (7f5a9ce4) with STAB_PASS; this connect's directory
#     $NEW/analysis-s2 does not exist;
#   the fence (only rs1_* and ens1_* pass; cov2d-* or any other name stops), recorded;
#   the deploy at M_A1, its tracked files clean; the analysis, probe and estimator_stability_analyze at their bound
#     digests; the s5c contract, the sigma receipt (E4's pin, 84266e30...) and the h2 definition at their blobs at M_A1;
#     FD-STAB's SHA256SUMS at e2c35e55 and its readout-2 fd_stab.json at 653356ae (the s_F reproduction); the 70
#     reference copies under $NEW/refs as at the stage-2 dry connect (logs-s2/refs-SHA256SUMS);
#   the bound analysis, read at the deploy, under the sourced environment (Python 3.11):
#     ensemble_estimator_analyze.py --stage 2 --root $NEW --pin M_A1 --refs $NEW/refs ... --stage1 ens1_stage1.json
#     --fdstab-readout fd_stab.json --out ens1_stage2.json
#     rc 0 (a verdict: PASS, BIAS_WORSE or INVALID), 3 (INCOMPLETE) or 4 (STOP). Nothing is repaired.
# Writes only $NEW/analysis-s2/ (refused if it exists). Attempt 1's root is not touched. No set -u.
SELF=$1
M=f4d2d7f3833834390b7b031df61ba1a5765e9900
NEW=/pscratch/sd/j/josephrb/ens1-a1-20261108
D=$NEW/deploy
R=$NEW/analysis-s2
P=$NEW/post-s2-full
S1J=$NEW/analysis-s1/ens1_stage1.json
S1_SHA=7f5a9ce4da8f59f3284715ff6f14f8106034b42c0301ad04979a8ed6b461ad99
S=docs/orchestration/state/measurement-paper/5d-community-20261024
SUMS=$S/fd/receipts-stab-a1r/full/SHA256SUMS
FDR=$S/fd/receipts-stab-a1r/readout/readout-2/fd_stab.json
bail() { rm -f -- "$SELF"; exit 9; }
[ -n "$SELF" ] && [ -f "$SELF" ] || exit 9
[ "$(cat "$P/connect-postrun.done" 2>/dev/null)" = 0 ] && grep -q '"verdict": "PASS"' "$P/s2-full-read.json" 2>/dev/null || bail
[ "$(sha256sum "$S1J" 2>/dev/null | cut -d' ' -f1)" = "$S1_SHA" ] && grep -q '"verdict": "STAB_PASS"' "$S1J" || bail
[ ! -e "$R" ] || bail
mkdir "$R" || bail
exec > "$R/connect-analysis.log" 2>&1
finish() { echo "ens1 a1 stage-2 analysis rc=$1"; date -u +%FT%TZ; echo "$1" > "$R/connect-analysis.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"; date -u +%FT%TZ
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$R/ens1_a1_s2_analysis.sh"
echo "stage-2 post-run: done $(cat "$P/connect-postrun.done"); s2-full-read.json $(sha256sum "$P/s2-full-read.json" | cut -d' ' -f1)"
echo "stage 1: ens1_stage1.json $S1_SHA, STAB_PASS"

echo "== the fence (only rs1_* and ens1_* pass)"
squeue -u josephrb -h -o '%i|%j|%T|%M|%l' > "$R/squeue-before.txt" 2>&1 || { echo "STOP: squeue failed"; finish 9; }
cat "$R/squeue-before.txt"
bad=$(awk -F'|' '$2 !~ /^(rs1_|ens1_)/' "$R/squeue-before.txt")
[ -z "$bad" ] || { echo "FENCE STOP: a cov2d-* job or a job of another name is present:"; printf '%s\n' "$bad"; finish 9; }
echo "FENCE: pass"

echo "== the deploy and the analysis's inputs"
[ "$(git -C "$D" rev-parse HEAD)" = "$M" ] || { echo "STOP: deploy HEAD is not M_A1"; finish 9; }
n=$(git -C "$D" status --porcelain --untracked-files=no | wc -l); echo "HEAD $M; modified tracked files: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy has modified tracked files"; finish 9; }
bad=0
while read -r h p; do
  got=$(sha256sum "$D/$p" | cut -d' ' -f1); echo "$got $p"
  [ "$got" = "$h" ] || { echo "SHA256 MISMATCH $p (want $h)"; bad=$((bad + 1)); }
done <<SHAS
1d6a0448ac75c90a2282ceb8bd5383cf0cae27024c0dbb9a5adc27ff93b11281 nd-unfolding/ensemble_estimator_analyze.py
807c40d3cb64e2e09d2fa9a5b91fb7a786f4eb51090e4291d65b3896b47e3b25 nd-unfolding/ensemble_estimator_probe.py
391fdc82d57357433c52c723599aec86a846564a83d09b70378d5c0fb7a3677b nd-unfolding/estimator_stability_analyze.py
d54fd7c9641901736e58430e666db1ee782a54d9c95bf4439541872567c39c93 docs/orchestration/state/s5c/contract.json
84266e309d1aae0d2db1db315750b8164413a7d0125fcaa4a6c9b25834261a2c docs/orchestration/state/s5e/cand/assess_receipt.json
b67907615fe2e903e60ae6caa1c141fa007676c0a1b3ae9f42490d331bfdda89 nd-unfolding/pv-ladder/readouts/h2_definition.json
e2c35e55402b809f522c86f597df20b058fc0c49596b9595448c4a944be333ee $SUMS
653356ae56087ea74621e61a60c829d63be9a9f15b0b35941e641b22f0be8ea3 $FDR
SHAS
[ "$bad" -eq 0 ] || { echo "STOP: bound bytes"; finish 9; }
( cd "$NEW/refs" && find runs -type f -print0 | sort -z | xargs -0 sha256sum ) > "$R/refs-SHA256SUMS"
cmp -s "$R/refs-SHA256SUMS" "$NEW/logs-s2/refs-SHA256SUMS" && [ "$(grep -c . "$R/refs-SHA256SUMS")" -eq 70 ] \
  || { echo "STOP: the reference copies are not the stage-2 dry connect's"; finish 9; }
echo "reference copies: 70, as at the stage-2 dry connect"

echo "== the bound analysis (sourced environment)"
( source "$D/setup_salloc_env.sh" > "$R/env-analysis.log" 2>&1
  python3 --version
  cd "$D" && PYTHONDONTWRITEBYTECODE=1 nice -n 19 python3 -B nd-unfolding/ensemble_estimator_analyze.py --stage 2 \
    --root "$NEW" --pin "$M" --refs "$NEW/refs" --fdstab-sums "$D/$SUMS" \
    --s5c-contract "$D/docs/orchestration/state/s5c/contract.json" \
    --sigma-receipt "$D/docs/orchestration/state/s5e/cand/assess_receipt.json" \
    --h2-definition "$D/nd-unfolding/pv-ladder/readouts/h2_definition.json" --stage1 "$S1J" --fdstab-readout "$D/$FDR" \
    --out "$R/ens1_stage2.json" ); rc=$?
echo "analysis rc=$rc"
[ -s "$R/ens1_stage2.json" ] && sha256sum "$R/ens1_stage2.json"
n=$(git -C "$D" status --porcelain --untracked-files=no | wc -l); echo "modified tracked files after: $n"
case $rc in
  0) finish 0 ;;
  3) echo "INCOMPLETE (reported unrepaired)"; finish 3 ;;
  4) echo "STOP: a gate failed (reported unrepaired)"; finish 4 ;;
  *) echo "STOP: the analysis exited $rc (reported unrepaired)"; finish 5 ;;
esac

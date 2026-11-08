#!/bin/bash
# ENS1 stage-1 analysis under addendum A1 (declaration §4; the bound ensemble_estimator_analyze.py --stage 1): 0 node-h,
# login node, from a /dev/shm copy of itself ($1), after the full post-run connect read PASS and its receipt went to the
# director. In order:
#   refusals before anything is written: the post-run's done file reads 0 and its a1-full-read.json says PASS; this
#     connect's directory $NEW/analysis-s1 does not exist;
#   the fence (only rs1_* and ens1_* pass; cov2d-* or any other name stops), recorded;
#   the deploy at M_A1, its tracked files clean; the analysis, probe and estimator_stability_analyze at their bound
#     digests; the s5c contract, the sigma receipt (E4's pin, 84266e30...) and the h2 definition at their blobs at M_A1;
#     FD-STAB's SHA256SUMS at e2c35e55; the 20 control-jitter copies under $NEW/refs as at the dry connect;
#   the bound analysis, read at the deploy, under the sourced environment (Python 3.11):
#     ensemble_estimator_analyze.py --stage 1 --root $NEW --pin M_A1 --refs $NEW/refs ... --out ens1_stage1.json
#     rc 0 (a verdict: STAB_PASS, STAB_FAIL or UNINFORMATIVE), 3 (INCOMPLETE) or 4 (STOP). Nothing is repaired.
# Writes only $NEW/analysis-s1/ (refused if it exists). Attempt 1's root is not touched. No set -u.
SELF=$1
M=f4d2d7f3833834390b7b031df61ba1a5765e9900
NEW=/pscratch/sd/j/josephrb/ens1-a1-20261108
D=$NEW/deploy
R=$NEW/analysis-s1
P=$NEW/post-full
S=docs/orchestration/state/measurement-paper/5d-community-20261024
SUMS=$S/fd/receipts-stab-a1r/full/SHA256SUMS
bail() { rm -f -- "$SELF"; exit 9; }
[ -n "$SELF" ] && [ -f "$SELF" ] || exit 9
[ "$(cat "$P/connect-postrun.done" 2>/dev/null)" = 0 ] && grep -q '"verdict": "PASS"' "$P/a1-full-read.json" 2>/dev/null || bail
[ ! -e "$R" ] || bail
mkdir "$R" || bail
exec > "$R/connect-analysis.log" 2>&1
finish() { echo "ens1 a1 stage-1 analysis rc=$1"; date -u +%FT%TZ; echo "$1" > "$R/connect-analysis.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"; date -u +%FT%TZ
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$R/ens1_a1_s1_analysis.sh"
echo "post-run: done $(cat "$P/connect-postrun.done"); a1-full-read.json $(sha256sum "$P/a1-full-read.json" | cut -d' ' -f1)"

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
SHAS
[ "$bad" -eq 0 ] || { echo "STOP: bound bytes"; finish 9; }
( cd "$NEW/refs" && find runs -type f -print0 | sort -z | xargs -0 sha256sum ) > "$R/refs-SHA256SUMS"
cmp -s "$R/refs-SHA256SUMS" "$NEW/logs/refs-SHA256SUMS" && [ "$(grep -c . "$R/refs-SHA256SUMS")" -eq 20 ] \
  || { echo "STOP: the control-jitter copies are not the dry connect's"; finish 9; }
echo "control-jitter copies: 20, as at the dry connect"

echo "== the bound analysis (sourced environment)"
( source "$D/setup_salloc_env.sh" > "$R/env-analysis.log" 2>&1
  python3 --version
  cd "$D" && PYTHONDONTWRITEBYTECODE=1 nice -n 19 python3 -B nd-unfolding/ensemble_estimator_analyze.py --stage 1 \
    --root "$NEW" --pin "$M" --refs "$NEW/refs" --fdstab-sums "$D/$SUMS" \
    --s5c-contract "$D/docs/orchestration/state/s5c/contract.json" \
    --sigma-receipt "$D/docs/orchestration/state/s5e/cand/assess_receipt.json" \
    --h2-definition "$D/nd-unfolding/pv-ladder/readouts/h2_definition.json" --out "$R/ens1_stage1.json" ); rc=$?
echo "analysis rc=$rc"
[ -s "$R/ens1_stage1.json" ] && sha256sum "$R/ens1_stage1.json"
n=$(git -C "$D" status --porcelain --untracked-files=no | wc -l); echo "modified tracked files after: $n"
case $rc in
  0) finish 0 ;;
  3) echo "INCOMPLETE (reported unrepaired)"; finish 3 ;;
  4) echo "STOP: a gate failed (reported unrepaired)"; finish 4 ;;
  *) echo "STOP: the analysis exited $rc (reported unrepaired)"; finish 5 ;;
esac

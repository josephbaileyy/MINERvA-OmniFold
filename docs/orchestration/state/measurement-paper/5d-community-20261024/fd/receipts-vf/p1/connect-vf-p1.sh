#!/bin/bash
# V_F Phase 1 (FD-VF-ADDITION-DECLARATION.md §3, §7.3; amendment A1), one login02 connect: claim $BA atomically, a fresh
# clone of the bound commit, the 22 bound blobs, root_6_28 checked, the 541 on-node tests (amendment A3) with no skip, then
# fd_vf_addition.py chain under timeout 3600. Writes only under $BA; nothing to CFS; 0 node-h; removes nothing it did
# not create. Every gate needs its command to succeed AND its output to be the expected one. No set -u (conda).
BA=/pscratch/sd/j/josephrb/vf-20261125-p1
M=c0fa0d01aa05d5b6bb9793919768491d8d8a0c23
ENV=$HOME/.conda/envs/root_6_28
stop() { echo "STOP: $*"; exit "${STOP_RC:-9}"; }
h=$(hostname) && [ "$h" = login02 ] || STOP_RC=2 stop "not login02 (${h:-hostname failed})"
mkdir "$BA" 2>/dev/null || STOP_RC=2 stop "$BA exists or cannot be created"    # atomic claim: fails on anything there
mkdir "$BA/receipts" "$BA/logs" "$BA/tmp" || stop "mkdir"
export TMPDIR=$BA/tmp                                    # before any here-document, command substitution or python
export XDG_CACHE_HOME=$BA/tmp/xdg-cache                  # fontconfig's cache (matplotlib calls fc-list) stays in $BA
ts=$(date -u +%FT%TZ) && [ -n "$ts" ] || stop "date"
printf '%s\n%s\n' "$h" "$ts" > "$BA/receipts/host.txt" || stop "host.txt"
porcelain_empty() {                                      # succeeds only if git succeeded and printed nothing
  local out
  out=$(git -C "$BA/deploy" -c status.showUntrackedFiles=all status --porcelain --ignored --untracked-files=all) || return 2
  [ -z "$out" ] || { printf '%s\n' "$out" | head -20; return 1; }
}
git clone -q --no-checkout https://github.com/josephbaileyy/MINERvA-OmniFold.git "$BA/deploy" > "$BA/logs/clone.log" 2>&1 || stop "clone"
git -C "$BA/deploy" -c advice.detachedHead=false checkout -q --detach "$M" || stop "checkout"
head=$(git -C "$BA/deploy" rev-parse HEAD) && [ "$head" = "$M" ] || stop "HEAD ${head:-unreadable} is not the bound commit"
porcelain_empty || stop "porcelain after checkout"
want=(
  "974027b1bc17213423365c76cf71f6101c370ddd nd-unfolding/fd_vf_addition.py"
  "877bb6333302d1cd419d65d7ce1f373001046f57 nd-unfolding/tests/test_fd_vf_addition.py"
  "1f3979046c0517786ed3b1a6f92004ec6cf68fcf nd-unfolding/fd_cpl_addition.py"
  "07899d161bdb84fe6e6b549a3b8ee5886dde77a7 nd-unfolding/fd_gencmp_e.py"
  "9e0272fab22643749df64ea91a6727130a77c9f5 nd-unfolding/fd_gencmp.py"
  "b5fbcef304f1c46e0c02e5e08d83a902840bd313 nd-unfolding/fd_gencmp_kin.py"
  "e4c530b25afda48e0036de24416cea43e467dc45 nd-unfolding/fd_f0_regrade.py"
  "c7d8cead01a2e376e01cc73cada3ce1eeb484160 nd-unfolding/fd_g_compare.py"
  "d225b108d800924ef28ada28e7d31c94c54b802f nd-unfolding/fd_g_diag.py"
  "6f25954affa62d6e16cda5c079f9b09d01b53a1e nd-unfolding/fd_g_followup.py"
  "b4376088e337a64ca74468f2e82d9f1ef1b3a800 nd-unfolding/fd_flux_boot.py"
  "76d1c5b8b41da48d93f60775c63a1411faa334c4 nd-unfolding/fd_g_figures.py"
  "943bb2f2294614569e0efa343bfbc2fe20829ded nd-unfolding/fd_g_figures_check.py"
  "31976e7002c592536a256664ea3a438673a541a1 nd-unfolding/fd_data_product.py"
  "3fb82c6e81ed4709b83b2ee634b4c6b83e0ba16d nd-unfolding/fd_deposit_candidate.py"
  "1542ed946f701bff62ec6fe8c08cdc7c2424c599 nd-unfolding/s1_assemble.py"
  "b6aee05dda0568e400db2706df2d49c9448514e6 nd-unfolding/s5p_stage1_inspect.py"
  "ded1c2b105e10c4e7137db9bb67bf966d20d3bbf docs/orchestration/state/measurement-paper/5d-community-20261024/fd/with-vf/block/vf_block.npz"
  "713c12c703b8b3ce4cb83155bd74ff1eb868d22e docs/orchestration/state/measurement-paper/5d-community-20261024/fd/with-vf/block/vf_block.json"
  "88b6cafcf15212606bfab56ea7b4a2cd4ea88a24 docs/orchestration/state/measurement-paper/5d-community-20261024/FD-VF-ADDITION-DECLARATION.md"
  "3ba0b367b8b8e1d54102a0d88dcb54884a643095 docs/orchestration/state/measurement-paper/5d-community-20261024/FD-VF-ADDITION-AMENDMENT-A1.md"
  "61d28b1f78e24665a730fb50ccea5a78ad3ad685 docs/orchestration/state/measurement-paper/5d-community-20261024/FD-VF-ADDITION-AMENDMENT-A2.md"
)
[ "${#want[@]}" = 22 ] || stop "the blob list holds ${#want[@]} entries, not 22"
rec=""; n=0
for w in "${want[@]}"; do
  b=${w%% *}; p=${w#* }
  g=$(git -C "$BA/deploy" rev-parse "$M:$p") || stop "cannot resolve $p"
  [ "$g" = "$b" ] || stop "blob $p is $g, not $b"
  rec+="$g $p"$'\n'; n=$((n + 1))
done
[ "$n" = 22 ] || stop "checked $n blobs, not 22"
printf '%s' "$rec" > "$BA/receipts/deploy-blobs.txt" || stop "deploy-blobs.txt"
echo "deploy ok at $M: $n blobs"
hook=$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook) && [ -n "$hook" ] || stop "conda hook"
eval "$hook" || stop "conda hook eval"
conda activate "$ENV" || stop "conda activate"
[ "$CONDA_PREFIX" = "$ENV" ] || stop "CONDA_PREFIX is ${CONDA_PREFIX:-unset}"
py=$(command -v python3) && [ "$py" = "$ENV/bin/python3" ] || stop "python3 is ${py:-not found}"
PY="env -u PYTHONPATH $ENV/bin/python3"
export MPLCONFIGDIR=$BA/tmp/mpl-tests PYTHONDONTWRITEBYTECODE=1  # before the probe: no cache or bytecode outside $BA
v=$($PY -I -B -c 'import sys, numpy, matplotlib; print(sys.version.split()[0], numpy.__version__, matplotlib.__version__)') \
  || stop "the version probe failed"
printf '%s\n' "$v" > "$BA/receipts/env.txt" || stop "env.txt"
[ "$v" = "3.11.14 1.26.4 3.10.8" ] || stop "not E-A2's renderer: $v"
cd "$BA/deploy/nd-unfolding/tests" || stop "tests dir"
# the on-node selection of amendment A3: ten modules whole and test_fd_gencmp_e without StepCR, 541 tests
timeout 3600 $PY -B -m unittest -v test_fd_vf_addition test_fd_cpl_addition test_fd_g_compare test_fd_g_diag \
  test_fd_g_followup test_fd_flux_boot test_fd_f0_regrade test_fd_g_figures test_fd_deposit_candidate \
  test_fd_data_product test_fd_gencmp_e.Sets test_fd_gencmp_e.Stage test_fd_gencmp_e.Materialize test_fd_gencmp_e.Chain \
  > "$BA/logs/tests.out" 2> "$BA/logs/tests.log"
trc=$?
# unittest writes its report to stderr (tests.log; anything the tests print to stdout goes to tests.out). It must hold
# exactly one "Ran N tests" line, and its last three non-blank lines must be the closing block: the rule,
# "Ran 541 tests in Ts", and "OK" alone (a skip ends "OK (skipped=N)").
verdict=$(awk 'NF { a[++n] = $0 } /^Ran [0-9]+ tests? in / { r++ }
  END { if (r == 1 && n >= 3 && a[n] == "OK" && a[n-1] ~ /^Ran 541 tests in [0-9.]+s$/ && a[n-2] ~ /^-+$/) print "PASS";
        else printf "FAIL: %d Ran lines; %s | %s | %s", r, a[n-2], a[n-1], a[n] }' "$BA/logs/tests.log") \
  || verdict="FAIL: awk"
printf 'tests rc=%s %s\n' "$trc" "$verdict" > "$BA/logs/tests.summary" || stop "tests.summary"
cat "$BA/logs/tests.summary"
[ "$trc" = 0 ] && [ "$verdict" = PASS ] || stop "tests (rc $trc; $verdict; a skip ends 'OK (skipped=N)')"
porcelain_empty || stop "the tests left files in the deploy"
unset MPLCONFIGDIR                                       # the chain sets its own, under $BA/run
t0=$(date -u +%FT%TZ) && [ -n "$t0" ] || stop "date"
printf 'chain start %s\n' "$t0" >> "$BA/receipts/host.txt" || stop "host.txt"
cd "$BA" || stop "cd $BA"
timeout 3600 $PY -I -B "$BA/deploy/nd-unfolding/fd_vf_addition.py" chain --scratch /pscratch/sd/j/josephrb \
  --run-e /pscratch/sd/j/josephrb/gencmp-e-20261101/rerun1 --run-dir "$BA/run" > "$BA/logs/chain.out" 2> "$BA/logs/chain.err"
rc=$?
echo "chain rc=$rc"; tail -n 5 "$BA/logs/chain.out"; tail -n 5 "$BA/logs/chain.err"
final=$rc
bad() { echo "RECEIPT: $*"; [ "$final" = 0 ] && final=7; }  # a receipt failure never leaves a successful exit
printf 'rc=%s\n' "$rc" >> "$BA/logs/chain.out" || bad "chain.out"
t1=$(date -u +%FT%TZ) && [ -n "$t1" ] || { bad "date"; t1=unknown; }
printf 'chain rc=%s end %s\n' "$rc" "$t1" >> "$BA/receipts/host.txt" || bad "host.txt"
if [ -d "$BA/run" ]; then
  if ( set -o pipefail; cd "$BA/run" && find . -type f ! -path './tmp/*' ! -path './mpl/*' -print0 | sort -z \
         | xargs -0 -r sha256sum ) > "$BA/receipts/run.sha256"; then
    nf=$(wc -l < "$BA/receipts/run.sha256") && [ "$nf" -gt 0 ] && echo "run files hashed: $nf" || bad "run.sha256 empty"
  else bad "run.sha256 incomplete"; fi
else bad "no run directory"; fi
if porcelain_empty; then pa="porcelain after: empty"; else pa="porcelain after: NOT empty or unreadable"; [ "$final" = 0 ] && final=8; fi
echo "$pa"; printf '%s\n' "$pa" > "$BA/logs/porcelain-after.txt" || bad "porcelain-after.txt"
exit "$final"

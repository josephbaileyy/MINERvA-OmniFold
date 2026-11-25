#!/bin/bash
# V_F Phase 1 (FD-VF-ADDITION-DECLARATION.md §3, §7.3; amendment A1), one login02 connect: a fresh clone of the bound
# commit into $BA/deploy, the bound blobs checked, the eleven test modules with no skip in root_6_28, then
# fd_vf_addition.py chain under timeout 3600. Writes only under $BA; nothing to CFS; 0 node-h. No set -u (conda).
BA=/pscratch/sd/j/josephrb/vf-20261125-p1
M=c0fa0d01aa05d5b6bb9793919768491d8d8a0c23
[ "$(hostname)" = login02 ] || { echo "STOP: not login02 ($(hostname))"; exit 2; }
[ -e "$BA" ] && { echo "STOP: $BA exists"; exit 2; }
mkdir -p "$BA"/{receipts,logs,tmp} || exit 2
{ hostname; date -u +%FT%TZ; } > "$BA/receipts/host.txt"
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$BA/deploy" > "$BA/logs/clone.log" 2>&1 || { echo "STOP: clone"; exit 3; }
cd "$BA/deploy" && git -c advice.detachedHead=false checkout -q --detach "$M" || { echo "STOP: checkout"; exit 3; }
[ "$(git rev-parse HEAD)" = "$M" ] || { echo "STOP: HEAD not the bound commit"; exit 9; }
[ -z "$(git status --porcelain --ignored)" ] || { echo "STOP: porcelain not empty"; exit 9; }
want="
974027b1bc17213423365c76cf71f6101c370ddd nd-unfolding/fd_vf_addition.py
877bb6333302d1cd419d65d7ce1f373001046f57 nd-unfolding/tests/test_fd_vf_addition.py
1f3979046c0517786ed3b1a6f92004ec6cf68fcf nd-unfolding/fd_cpl_addition.py
07899d161bdb84fe6e6b549a3b8ee5886dde77a7 nd-unfolding/fd_gencmp_e.py
9e0272fab22643749df64ea91a6727130a77c9f5 nd-unfolding/fd_gencmp.py
b5fbcef304f1c46e0c02e5e08d83a902840bd313 nd-unfolding/fd_gencmp_kin.py
e4c530b25afda48e0036de24416cea43e467dc45 nd-unfolding/fd_f0_regrade.py
c7d8cead01a2e376e01cc73cada3ce1eeb484160 nd-unfolding/fd_g_compare.py
d225b108d800924ef28ada28e7d31c94c54b802f nd-unfolding/fd_g_diag.py
6f25954affa62d6e16cda5c079f9b09d01b53a1e nd-unfolding/fd_g_followup.py
b4376088e337a64ca74468f2e82d9f1ef1b3a800 nd-unfolding/fd_flux_boot.py
76d1c5b8b41da48d93f60775c63a1411faa334c4 nd-unfolding/fd_g_figures.py
943bb2f2294614569e0efa343bfbc2fe20829ded nd-unfolding/fd_g_figures_check.py
31976e7002c592536a256664ea3a438673a541a1 nd-unfolding/fd_data_product.py
3fb82c6e81ed4709b83b2ee634b4c6b83e0ba16d nd-unfolding/fd_deposit_candidate.py
1542ed946f701bff62ec6fe8c08cdc7c2424c599 nd-unfolding/s1_assemble.py
b6aee05dda0568e400db2706df2d49c9448514e6 nd-unfolding/s5p_stage1_inspect.py
ded1c2b105e10c4e7137db9bb67bf966d20d3bbf docs/orchestration/state/measurement-paper/5d-community-20261024/fd/with-vf/block/vf_block.npz
713c12c703b8b3ce4cb83155bd74ff1eb868d22e docs/orchestration/state/measurement-paper/5d-community-20261024/fd/with-vf/block/vf_block.json
88b6cafcf15212606bfab56ea7b4a2cd4ea88a24 docs/orchestration/state/measurement-paper/5d-community-20261024/FD-VF-ADDITION-DECLARATION.md
3ba0b367b8b8e1d54102a0d88dcb54884a643095 docs/orchestration/state/measurement-paper/5d-community-20261024/FD-VF-ADDITION-AMENDMENT-A1.md
61d28b1f78e24665a730fb50ccea5a78ad3ad685 docs/orchestration/state/measurement-paper/5d-community-20261024/FD-VF-ADDITION-AMENDMENT-A2.md
"
bad=0
while read -r h p; do [ -z "$h" ] && continue; g=$(git rev-parse "$M:$p"); echo "$g $p"; [ "$g" = "$h" ] || bad=1; done <<< "$want" > "$BA/receipts/deploy-blobs.txt"
[ $bad = 0 ] || { echo "STOP: a blob differs"; cat "$BA/receipts/deploy-blobs.txt"; exit 9; }
echo "deploy ok at $M: $(wc -l < "$BA/receipts/deploy-blobs.txt") blobs"
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28"
export TMPDIR=$BA/tmp MPLCONFIGDIR=$BA/tmp/mpl-tests PYTHONDONTWRITEBYTECODE=1
PY="env -u PYTHONPATH python3"
$PY -c 'import sys, numpy, matplotlib; print(sys.version.split()[0], numpy.__version__, matplotlib.__version__)' > "$BA/receipts/env.txt" 2>&1
[ "$(cat "$BA/receipts/env.txt")" = "3.11.14 1.26.4 3.10.8" ] || { echo "STOP: not E-A2's renderer: $(cat "$BA/receipts/env.txt")"; exit 9; }
cd "$BA/deploy/nd-unfolding/tests" && timeout 3600 $PY -B -m unittest -v test_fd_vf_addition test_fd_cpl_addition test_fd_g_compare \
  test_fd_g_diag test_fd_g_followup test_fd_flux_boot test_fd_f0_regrade test_fd_g_figures test_fd_deposit_candidate \
  test_fd_data_product test_fd_gencmp_e > "$BA/logs/tests.log" 2>&1
trc=$?; sk=$(grep -cE '\.\.\. skipped|skipped=' "$BA/logs/tests.log")
echo "tests rc=$trc skipped_lines=$sk $(grep -E '^Ran|^OK|^FAILED' "$BA/logs/tests.log" | tr '\n' ' ')" | tee "$BA/logs/tests.summary"
[ $trc = 0 ] && [ "$sk" = 0 ] || { echo "STOP: tests"; exit 9; }
cd "$BA/deploy" && [ -z "$(git status --porcelain --ignored)" ] || { echo "STOP: the tests left files in the deploy"; exit 9; }
echo "chain start $(date -u +%FT%TZ)" | tee -a "$BA/receipts/host.txt"
cd "$BA" && unset MPLCONFIGDIR && timeout 3600 $PY -I -B "$BA/deploy/nd-unfolding/fd_vf_addition.py" chain \
  --scratch /pscratch/sd/j/josephrb --run-e /pscratch/sd/j/josephrb/gencmp-e-20261101/rerun1 --run-dir "$BA/run" \
  > "$BA/logs/chain.out" 2> "$BA/logs/chain.err"
rc=$?; echo "rc=$rc" >> "$BA/logs/chain.out"
echo "chain rc=$rc end $(date -u +%FT%TZ)" | tee -a "$BA/receipts/host.txt"
tail -n 5 "$BA/logs/chain.out"; tail -n 5 "$BA/logs/chain.err"
(cd "$BA/run" 2>/dev/null && find . -type f ! -path './tmp/*' ! -path './mpl/*' -print0 | sort -z | xargs -0 sha256sum > "$BA/receipts/run.sha256")
echo "run files hashed: $(wc -l < "$BA/receipts/run.sha256" 2>/dev/null)"
cd "$BA/deploy" && echo "porcelain after: $(git status --porcelain --ignored | wc -l)" | tee "$BA/logs/porcelain-after.txt"
exit $rc

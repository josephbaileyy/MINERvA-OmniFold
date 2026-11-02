#!/bin/bash
# GENCMP amendment E: deploy at M (binding ruling 1). Writes only under $B.
B=/pscratch/sd/j/josephrb/gencmp-e-20261101
M=6cd095d6773a45c8deef47d298245ea270a636ae
[ -e "$B" ] && { echo "STOP: $B exists"; exit 2; }
mkdir -p "$B"/{receipts,logs,tmp} || exit 2
{ hostname; date -u +%FT%TZ; } > "$B/receipts/deploy-host.txt"
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$B/deploy" > "$B/logs/clone.log" 2>&1 || { echo clone failed; exit 3; }
cd "$B/deploy" && git -c advice.detachedHead=false checkout -q --detach "$M" || exit 3
[ "$(git rev-parse HEAD)" = "$M" ] || { echo "HEAD not M"; exit 9; }
[ -z "$(git status --porcelain)" ] || { echo "porcelain not empty"; exit 9; }
want="07899d161bdb84fe6e6b549a3b8ee5886dde77a7 nd-unfolding/fd_gencmp_e.py
9e0272fab22643749df64ea91a6727130a77c9f5 nd-unfolding/fd_gencmp.py
51b77bb53b195d622b66bf4daad902e45f09a66c nd-unfolding/fd_g_figures.py
fdaa9dc13c983249d385d16425aff26bdf235097 nd-unfolding/fd_g_figures_check.py
fe60ff68344facab0436f2befd97ced6a490d477 nd-unfolding/tests/test_fd_gencmp_e.py
728e7812efe47b71da102f7a180fd7870e2cfb60 docs/orchestration/state/measurement-paper/5d-community-20261024/fd/gencmp-e/INPUTS.sha256"
bad=0
while read -r h p; do g=$(git rev-parse "$M:$p"); echo "$g $p"; [ "$g" = "$h" ] || bad=1; done <<< "$want" > "$B/receipts/deploy-blobs.txt"
cat "$B/receipts/deploy-blobs.txt"
[ $bad = 0 ] || { echo "STOP: a blob differs"; exit 9; }
echo "deploy ok at $M"

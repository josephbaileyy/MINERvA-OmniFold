#!/usr/bin/env bash
# regenA amendment A3: local ladder read. Run from regenA3/.
set -u
PY=/Users/josephbailey/cov2d-work/figenv/rootmpl3108/bin/python
WT=/Users/josephbailey/local-research/wt-ibu-chi2-a3
REL=/Users/josephbailey/cov2d-work/figfetch/er-anc/cov_ptpl_minerva_inclusive_6GeV.root
R2=../../measurement-paper/5d-community-20261024/fd/receipts-ref-c2c1/step2/read-2/readout.json
PINS=(../tier1/units/old/c2_central.npz ../tier1/units/e/c2_central.npz ../tier1/score.out "$R2" "$WT/2d-unfolding/compare_to_paper_fullcov.py" "$REL")
shasum -a 256 "${PINS[@]}" > receipts/pins_before.sha256 || exit 2
test -z "$(git -C "$WT" status --porcelain -- 2d-unfolding)" || { echo "module tree dirty"; exit 3; }
date -u +%FT%TZ > receipts/run_time.txt
PYTHONDONTWRITEBYTECODE=1 "$PY" ladder.py --module-dir "$WT/2d-unfolding" --release "$REL" \
  --npz-old ../tier1/units/old/c2_central.npz --npz-e ../tier1/units/e/c2_central.npz \
  --readout "$R2" --score ../tier1/score.out --out out/ladder.json > receipts/ladder.stdout 2> receipts/ladder.stderr
echo "rc=$?" >> receipts/run_time.txt
date -u +%FT%TZ >> receipts/run_time.txt
shasum -a 256 "${PINS[@]}" > receipts/pins_after.sha256
cmp -s receipts/pins_before.sha256 receipts/pins_after.sha256 && echo "C-PINS: equal before and after" >> receipts/run_time.txt || echo "C-PINS: CHANGED" >> receipts/run_time.txt

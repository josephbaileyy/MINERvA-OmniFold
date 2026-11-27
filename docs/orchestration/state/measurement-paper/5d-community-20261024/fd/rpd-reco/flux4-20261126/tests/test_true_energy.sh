#!/bin/bash
# test_true_energy.sh: rpd_flux4_fetch.sh's step 2b, the true-energy join record check (in place of flux3's identity with
# the previous run's products; the director's acceptance of 2026-11-26), cut from the fetch itself and run in a temp
# directory against fixture records: run/flux-extract.json's true_energy block and run/flux-factors-<PL>.npz with an
# energy column. MAT_PYTHON is this machine's python3 (with numpy). Then each mutant of the block against the same
# cases, and a static check that a failed record exits 15 before the success exit.
# usage: bash test_true_energy.sh
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
FETCH="$HERE/../rpd_flux4_fetch.sh"
BLOCK=$(awk '/^echo "== 2b\. the true-energy join record/ {f=1} f {print} f && /^echo "true-energy record check rc=\$terc"/ {exit}' "$FETCH")
[ "$(printf '%s\n' "$BLOCK" | wc -l | tr -d ' ')" -ge 40 ] || { echo "SETUP: could not cut step 2b from the fetch"; exit 9; }
SIDE=641ba34c5ebde6d1881c705b862fab144a6fbb8a58ef3d84e59f1c8ba030a79e
LAT=6ca02c3d8b09dfd168b5184c03d433a7bd65749f5f6fc4cefecdbed7b6ce052f
printf '%s\n' "$BLOCK" | grep -qF "' $SIDE $LAT" || { echo "FAIL: the block does not pass the pinned sidecar and lat_zero digests"; exit 1; }
ex=$(grep -n 'finish 15; }' "$FETCH" | head -1 | cut -d: -f1); ok=$(grep -n '\[ "\$mrc" -eq 0 \] && \[ "\$prc" -eq 0 \] && finish 0' "$FETCH" | cut -d: -f1)
grep -qF '[ "$terc" -eq 0 ] || { echo "STOP: the true-energy join record did not hold' "$FETCH" && [ -n "$ex" ] && [ -n "$ok" ] && [ "$ex" -lt "$ok" ] \
  || { echo "FAIL: a failed record does not exit 15 before the success exit"; exit 1; }
echo "ok   the block is cut from rpd_flux4_fetch.sh; a failed record exits 15 before the success exit"
T=$(mktemp -d) || exit 9
trap 'rm -rf -- "$T"' EXIT

# fixture EDIT: writes run/flux-extract.json and the 12 products; EDIT is a Python statement on `te` (the record) and
# `prod` (playlist -> energy array), applied before writing.
fixture() {
  rm -rf -- "$T/run"; mkdir -p "$T/run"
  python3 -I - "$T/run" "$SIDE" "$LAT" "$1" <<'EOF'
import json, sys
import numpy as np
run, side, lat, edit = sys.argv[1:]
pls = ("1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P")
rows = {pl: 6 + i for i, pl in enumerate(pls)}
prod = {pl: np.linspace(2.0, 9.0, rows[pl]) for pl in pls}
spots = {pl: {"rows": [0, rows[pl] - 1], "run": [1, 2], "subrun": [1, 1], "event": [5, 9],
              "energy_GeV": [float(prod[pl][0]), float(prod[pl][-1])]} for pl in pls}
te = {"source": {"path": "/x/truthx_RDX_ALL.npz", "sha256": side, "npz_sha256": lat, "schema": "rdx-truthx-sidecar/1",
                 "rows": sum(rows.values())},
      "block_rows": dict(rows), "median_GeV": 5.0, "spots": spots, "status": "PASS"}
drop = set()
exec(edit)
json.dump({"true_energy": te, "factor_products": {}}, open(f"{run}/flux-extract.json", "w"))
for pl in pls:
    arrays = {"factor": np.ones(rows[pl])}
    if pl not in drop:
        arrays["energy"] = prod[pl]
    np.savez(f"{run}/flux-factors-{pl}.npz", **arrays)
EOF
}

run() {  # run BLOCK -> prints the block's output and "terc=N"
  ( cd "$T" && MAT_PYTHON=python3 bash -c "$1"$'\necho "terc=$terc"' ) 2>&1
}

check() {  # check NAME EXPECTED_TERC EXPECTED_LINE OUTPUT
  rc=$(printf '%s\n' "$4" | sed -n 's/^terc=//p' | tail -1)
  if [ "$rc" = "$2" ] && printf '%s\n' "$4" | grep -qF -- "$3"; then [ "$QUIET" = 1 ] || echo "ok   $1 (terc $rc)"
  else [ "$QUIET" = 1 ] || { echo "FAIL $1: terc [$rc], want $2 and [$3]"; printf '%s\n' "$4" | sed 's/^/     /'; }
       fails=$((fails + 1)); fi
}

cases() {  # cases BLOCK
  fixture "pass"; check "a consistent record and products: PASS" 0 "TRUE_ENERGY RECORD: PASS" "$(run "$1")"
  fixture "te['status'] = 'STOP'"; check "status not PASS: FAIL" 1 "status 'STOP'" "$(run "$1")"
  fixture "te['source']['sha256'] = '0' * 64"; check "another sidecar digest: FAIL" 1 "is not the pinned sidecar" "$(run "$1")"
  fixture "te['source']['npz_sha256'] = '1' * 64"; check "another lat_zero digest: FAIL" 1 "is not lat_zero" "$(run "$1")"
  fixture "del te['spots']['1G']"; check "a playlist missing from the spot rows: FAIL" 1 "do not name the 12 playlists" "$(run "$1")"
  fixture "del te['block_rows']['1P']"; check "a playlist missing from the block rows: FAIL" 1 "do not name the 12 playlists" "$(run "$1")"
  fixture "te['spots']['1C']['event'] = [5]"; check "a spot list shorter than its rows: FAIL" 1 "1C: spot rows malformed" "$(run "$1")"
  fixture "te['spots']['1D'] = dict(te['spots']['1D'], rows=[0], run=[1], subrun=[1], event=[5], energy_GeV=[2.0])"
  check "a single spot row (fewer than the two ends): FAIL" 1 "1D: spot rows malformed" "$(run "$1")"
  fixture "prod['1E'] = prod['1E'].copy(); prod['1E'][2] = np.nan"; check "a NaN energy: FAIL" 1 "1E: energy column not finite and positive" "$(run "$1")"
  fixture "prod['1G'] = prod['1G'].copy(); prod['1G'][3] = np.inf"; check "an infinite energy (positive, not finite): FAIL" 1 "1G: energy column not finite and positive" "$(run "$1")"
  fixture "prod['1F'] = -prod['1F']"; check "negative energies: FAIL" 1 "1F: energy column not finite and positive" "$(run "$1")"
  fixture "prod['1L'] = prod['1L'][:-1]"; check "an energy column one row short: FAIL" 1 "1L: energy column missing, not float64" "$(run "$1")"
  fixture "prod['1M'] = prod['1M'].astype(np.float32)"; check "a float32 energy column: FAIL" 1 "1M: energy column missing, not float64" "$(run "$1")"
  fixture "drop.add('1N')"; check "a product without the energy column: FAIL" 1 "1N: energy column missing" "$(run "$1")"
  fixture "prod['1O'] = prod['1O'].reshape(-1, 1)"; check "a 2-D energy column of the block's length: FAIL" 1 "1O: energy column missing, not float64" "$(run "$1")"
  fixture "pass"; rm -f "$T/run/flux-extract.json"; check "no flux-extract.json: FAIL" 1 "flux-extract.json unreadable" "$(run "$1")"
  fixture "pass"; rm -f "$T/run/flux-factors-1B.npz"; check "a product missing: FAIL" 1 "1B: product unreadable" "$(run "$1")"
}

fails=0; QUIET=0
cases "$BLOCK"
echo "TRUE-ENERGY-TESTS :: $([ "$fails" -eq 0 ] && echo PASS || echo "FAIL ($fails)")"
[ "$fails" -eq 0 ] || exit 1

# Mutants: NAME<TAB>OLD<TAB>NEW, each OLD occurring exactly once in the block.
TAB=$(printf '\t')
MUTANTS="status-unchecked${TAB}if te.get(\"status\") != \"PASS\":${TAB}if False:
sidecar-unchecked${TAB}if src.get(\"sha256\") != side:${TAB}if False:
lat-unchecked${TAB}if src.get(\"npz_sha256\") != lat:${TAB}if False:
playlists-unchecked${TAB}if sorted(spots) != sorted(pls) or sorted(blocks) != sorted(pls):${TAB}if False:
blocks-unchecked${TAB} or sorted(blocks) != sorted(pls):${TAB}:
spot-lengths-unchecked${TAB} or any(len(s.get(k, [])) != n for k in (\"run\", \"subrun\", \"event\", \"energy_GeV\")):${TAB}:
spot-ends-unchecked${TAB}if n < 2 or any(${TAB}if n < 1 or any(
finite-unchecked${TAB}np.all(np.isfinite(e)) and np.all(e > 0)${TAB}np.all(e > 0)
positive-unchecked${TAB}np.all(np.isfinite(e)) and np.all(e > 0)${TAB}np.all(np.isfinite(e))
length-unchecked${TAB} or len(e) != blocks.get(pl):${TAB}:
dtype-unchecked${TAB} or e.dtype != np.float64${TAB}
ndim-unchecked${TAB} or e.ndim != 1${TAB}
missing-energy-ignored${TAB}if \"energy\" in z.files else None${TAB}if \"energy\" in z.files else np.ones(blocks.get(pl) or 1)
verdict-always-zero${TAB}sys.exit(1 if bad else 0)${TAB}sys.exit(0)"
QUIET=1; killed=0; total=0
while IFS="$TAB" read -r name old new; do
  total=$((total + 1))
  n=$(python3 -I -c 'import sys; print(sys.argv[1].count(sys.argv[2]))' "$BLOCK" "$old")
  [ "$n" = 1 ] || { echo "MUTANT $name: old text occurs $n times"; continue; }
  M=$(python3 -I -c 'import sys; t, a, b = sys.argv[1:]; print(t.replace(a, b, 1), end="")' "$BLOCK" "$old" "$new")
  fails=0; cases "$M"
  if [ "$fails" -gt 0 ]; then killed=$((killed + 1)); echo "KILLED   $name ($fails cases)"; else echo "SURVIVED $name"; fi
done <<< "$MUTANTS"
echo "TRUE-ENERGY-MUTANTS :: $killed/$total killed"
[ "$killed" -eq "$total" ]

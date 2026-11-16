#!/bin/bash
# Stand-in test of re2c_rollup_g2r.py, invoked exactly as re2c_run.sh's step() invokes a script (python3 -I, runpy, cwd
# $O). A stub re2c_rollup.py in a fake deploy keeps the real module's names (NS_R, partb_sums reading the committed part-B
# SHA256SUMS.J*, Path(f"{NS_R}/out", label, "xsec.root") per J2 universe, main() parsing --arm/--out/--results) and
# writes what it saw. The fake deploy carries the part-B sums at <B>; products.tsv (from <M>) is staged apart, as in the
# connect, and passed by --products-tsv.
#   bash test_driver.sh <wt> <M> <B>
set -u
WT=$1; M=$2; B=$3; H=$(cd "$(dirname "$0")" && pwd); PY=${PY:-/opt/homebrew/bin/python3.13}
T0=$(mktemp -d "${TMPDIR:-/tmp}/tdrv.XXXXXX"); D=$T0/deploy; fail=0
ok() { echo "PASS $1"; }; bad() { echo "FAIL $1"; fail=1; }
SUMS=docs/orchestration/state/2d-closeout/stageF/methods/re2/run/partb_readout/sums
PT=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d/g2r/readout/data/products.tsv.txt
TSV=$T0/products.tsv.txt
mkdir -p "$D/2d-unfolding/re2/partc" "$D/$SUMS"
for f in $(git -C "$WT" ls-tree --name-only "$B" "$SUMS/"); do git -C "$WT" show "$B:$f" > "$D/$f"; done
git -C "$WT" show "$M:$PT" > "$TSV"
cat > "$D/2d-unfolding/re2/partc/re2c_rollup.py" <<'STUB'
import argparse, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
SUMS_R = HERE.parents[2] / "docs/orchestration/state/2d-closeout/stageF/methods/re2/run/partb_readout/sums"
NS_R = "/pscratch/sd/j/josephrb/2d-closeout-re2-20261023/partb"
def partb_sums():
    out = {}
    for f in sorted(SUMS_R.glob("SHA256SUMS.J*")):
        for ln in f.read_text().splitlines():
            d, rel_ = ln.split()
            out[rel_] = d
    return out
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--results")
    ap.add_argument("--arm"); a = ap.parse_args()
    sums = partb_sums(); seen = {}
    for rel_ in sums:
        lab = rel_[:-len("/xsec.root")]
        p = Path(f"{NS_R}/out", lab, "xsec.root")
        seen[lab] = [str(p), sums[rel_]]
    Path(a.out).mkdir(parents=True, exist_ok=True)
    Path(a.out, "stub.json").write_text(json.dumps({"argv": sys.argv, "arm": a.arm, "seen": seen}))
    return 0
if __name__ == "__main__":
    raise SystemExit("the stub must not run as __main__")
STUB
step() {  # re2c_run.sh's step(), verbatim apart from the stdout file and the recorded status
  local cwd=$1 out=$2 script=$3; shift 3
  (cd "$cwd" && "$PY" -I -B -c "import sys, runpy; D, S = sys.argv[1], sys.argv[2]; \
sys.path[:0] = [D + '/2d-unfolding/uq', D + '/2d-unfolding', D]; sys.argv = [S] + sys.argv[3:]; \
runpy.run_path(S, run_name='__main__')" "$D" "$script" "$@") > "$out" 2>&1
}
run() { O=$T0/$1; mkdir -p "$O"; step "$O" "$O/log" "$H/re2c_rollup_g2r.py" --driver-mode "$2" --deploy "$D" --products-tsv "$TSV" --sidecar "$O.g2r_driver.json" --arm refined --out "$O/s5" --results "$O/results"; echo $?; }
rc=$(run g2r g2r)
"$PY" - "$T0/g2r" "$TSV" "$rc" <<'CHK' && ok "g2r: 175 U_ redirected to G2R's path with G2R's digest, others unchanged, sidecar, rc 0" || { bad g2r; cat "$T0/g2r/log"; }
import json, sys
o, pt, rc = sys.argv[1], sys.argv[2], int(sys.argv[3])
s = json.load(open(f"{o}/s5/stub.json")); side = json.load(open(f"{o}.g2r_driver.json")); import os; assert sorted(os.listdir(f"{o}/s5")) == ["stub.json"]
rows = {f"U_{r[4].split(':')[0]}_{r[4].split(':')[1]}": r for r in (l.split("\t") for l in open(pt).read().splitlines()) if r[3] == "g2r"}
U = {k: v for k, v in s["seen"].items() if k.startswith("U_")}
assert rc == 0 and len(U) == 175 and set(U) == set(rows), (rc, len(U))
for k, (p, d) in U.items():
    assert p == rows[k][1] and d == rows[k][2], k
NS = "/pscratch/sd/j/josephrb/2d-closeout-re2-20261023/partb/out"
other = {k: v for k, v in s["seen"].items() if not k.startswith("U_")}
assert other and all(v[0] == f"{NS}/{k}/xsec.root" for k, v in other.items())
assert s["arm"] == "refined" and "--driver-mode" not in s["argv"] and "--deploy" not in s["argv"]
assert side["mode"] == "g2r" and side["redirected"] == {"n_labels": 175, "n_calls": 175} and side["rollup_rc"] == 0
assert len(side["mapping"]) == 175
print("other labels unchanged:", len(other))
CHK
rc=$(run ident identity)
"$PY" - "$T0/ident" "$rc" <<'CHK' && ok "identity: every path and digest is part B's, nothing redirected, rc 0" || { bad identity; cat "$T0/ident/log"; }
import json, sys
o, rc = sys.argv[1], int(sys.argv[2])
s = json.load(open(f"{o}/s5/stub.json")); side = json.load(open(f"{o}.g2r_driver.json")); import os; assert sorted(os.listdir(f"{o}/s5")) == ["stub.json"]
NS = "/pscratch/sd/j/josephrb/2d-closeout-re2-20261023/partb/out"
assert rc == 0 and all(v[0] == f"{NS}/{k}/xsec.root" for k, v in s["seen"].items())
assert side["mode"] == "identity" and side["redirected"]["n_calls"] == 0 and side["mapping"] == {}
CHK
rc=$(run badmode bogus); [ "$rc" != 0 ] && grep -q 'driver-mode bogus' "$T0/badmode/log" && ok "an unknown mode refuses (rc $rc)" || { bad badmode; cat "$T0/badmode/log"; }
printf 'x' >> "$TSV"; rc=$(run badtsv g2r); [ "$rc" != 0 ] && grep -q 'is not a0f86fe1' "$T0/badtsv/log" && ok "an altered products.tsv refuses (rc $rc)" || { bad badtsv; cat "$T0/badtsv/log"; }
git -C "$WT" show "$M:$PT" > "$TSV"
f=$(ls "$D/$SUMS"/SHA256SUMS.J2a.1); sed -n '2,$p' "$f" > "$f.t" && mv "$f.t" "$f"; rc=$(run badsums g2r); [ "$rc" != 0 ] && grep -q "U_\* labels are not G2R's 175" "$T0/badsums/log" && ok "a part-B sums set missing a U_ label refuses (rc $rc)" || { bad badsums; cat "$T0/badsums/log"; }
find "$T0" -type f -exec rm -f {} +; find "$T0" -depth -type d -exec rmdir {} \;
[ -e "$T0" ] && echo "left: $T0"
[ "$fail" = 0 ] && echo "DRIVER TEST PASS" || echo "DRIVER TEST FAILED"
exit $fail

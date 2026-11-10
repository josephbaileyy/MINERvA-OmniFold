#!/bin/bash
# s5e candidate R, A3: recompute the 153 per-quantity rounding shifts behind assess_receipt.json's
# data_rounding_probe_over_data_sigma with the receipt's own producer (the director's ruling of 2026-11-09, route (b)),
# on a Perlmutter login node, in one foreground ssh session, after the director's go. Read-only toward s5e's tree:
#   preconditions: $X (this run's own directory) absent; the assess/data directory exists (a stat, no listing); no
#     process on this node names s5e-20260925 (listed and refused); squeue --me printed;
#   a fresh clone at 2f958652 (the commit the assessment's analysis was frozen at) into $X/deploy, clean (porcelain
#     --ignored 0) before and after; s5e_analyze_candidate.py at cc00829e, the s5c contract at d54fd7c9, and
#     assess_receipt.json (from the clone's 843fc99e, where it was committed) at 84266e30;
#   a3_extract.py, written below from this script and checked at its sha256, runs the producer's lines :147-151
#     verbatim (their text pinned at 01aee82c) on the 103 inputs, each read once through O_NOATIME with its sha256 and
#     its stat before and after; U and names from the producer's s5c_coverage.reported_functionals on the contract;
#   the gate: median, max and argmax equal the receipt's 0.7829505732456221, 2.5837789197284393 and J145 exactly, or a
#     STOP with only $X/out/STOP.json written.
# Writes only $X (deploy, the copied receipt, a3_extract.py, out/ with the CSV and JSON, and the log). Nothing is written
# into s5e's tree. No set -u. Any stop is final. Launched from a /dev/shm copy of itself, whose path is $1.
SELF=$1
M=2f958652f092e4e8938dbfa7b8142791e0c8e18d
RM=843fc99ef9dcec1545e41e4c7ab95d45810a38fd
X=/pscratch/sd/j/josephrb/s5e-a3-extract-20261109
A=/pscratch/sd/j/josephrb/s5e-20260925/runs/cand/assess
PY=$HOME/.conda/envs/root_6_28/bin/python3
PRODUCER_SHA=cc00829eb7baf2e64cbeb9165fd89a3ef232c54fdb7d354c3688542d6e73514a
LINES_SHA=01aee82c24adb408142de2698b093fa7117dd0d21c313dd4b6fcc1e892d8d97c
CONTRACT_SHA=d54fd7c9641901736e58430e666db1ee782a54d9c95bf4439541872567c39c93
RECEIPT_SHA=84266e309d1aae0d2db1db315750b8164413a7d0125fcaa4a6c9b25834261a2c
EXTRACT_SHA=15f9b923a5754b19d8b1cc50d43f5c2bcf11191c2ac3dedb3746ccc1f9d7fb1f
bail() { rm -f -- "$SELF"; exit 9; }
[ ! -e "$X" ] && [ -d "$A/data" ] && [ -d "$A/data/boot" ] && [ -x "$PY" ] || bail
mkdir "$X" || bail
LOG=$X/extract.log
exec > "$LOG" 2>&1
finish() { echo "s5e-a3 extract rc=$1"; date -u +%FT%TZ; echo "$1" > "$X/extract.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$X/s5e_a3_extract.sh"
echo "squeue --me:"; squeue --me -h -o "%i %j %T"
others=$(pgrep -u "$USER" -af 's5e-20260925' | grep -v -e "pgrep" -e "$SELF" || true)
echo "processes on this node naming s5e-20260925: ${others:-none}"
[ -z "$others" ] || { echo "STOP: a process on this node names s5e-20260925: to the director"; finish 9; }
D=$X/deploy
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$D" > "$X/clone.log" 2>&1 || { echo "STOP: clone"; finish 3; }
git -C "$D" -c advice.detachedHead=false checkout -q "$M" || { echo "STOP: checkout"; finish 3; }
[ "$(git -C "$D" rev-parse HEAD)" = "$M" ] || { echo "STOP: HEAD is not 2f958652"; finish 9; }
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "HEAD $M; porcelain --ignored lines before: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy is not clean"; finish 9; }
C=$D/docs/orchestration/state/s5c/contract.json
for pair in "nd-unfolding/s5e_analyze_candidate.py $PRODUCER_SHA" "docs/orchestration/state/s5c/contract.json $CONTRACT_SHA"; do
  set -- $pair; got=$(sha256sum "$D/$1" | cut -d' ' -f1); echo "$1 sha256 $got"
  [ "$got" = "$2" ] || { echo "STOP: $1 is not the pinned file"; finish 9; }
done
git -C "$D" show "$RM:docs/orchestration/state/s5e/cand/assess_receipt.json" > "$X/assess_receipt.json" || { echo "STOP: receipt"; finish 9; }
got=$(sha256sum "$X/assess_receipt.json" | cut -d' ' -f1); echo "assess_receipt.json at $RM sha256 $got"
[ "$got" = "$RECEIPT_SHA" ] || { echo "STOP: the receipt is not the pinned one"; finish 9; }
cat > "$X/a3_extract.py" <<'PYEOF'
"""s5e candidate R, A3: the 153 per-quantity rounding shifts behind assess_receipt.json's data_rounding_probe_over_data_sigma
(median, max, argmax), recomputed by the receipt's own producer, s5e_analyze_candidate.py at 2f958652 (the director's
ruling of 2026-11-09, route (b)).

The producer computes them inline in main(), :147-151 at 2f958652. Those four source lines are executed here verbatim:
their text is read from the deploy's own file, whose sha256 is checked, and the text's sha256 is recorded. Two names
they use are supplied, and nothing else changes:
  - load_fn reads each file once through O_NOATIME, records its sha256 and stat before and after, and hands the bytes
    to the producer's own s5e_analyze_candidate.load_fn unchanged (np.load takes a file object);
  - glob.glob returns the committed file list (review2/r2_integrity.json: assess/data holds data_R, data_R_upcast,
    data_R_jitteredge1 and 2, and boot/ boot_b1..boot_b100), so no directory is listed. sorted() is the producer's own.
U and names come from s5c_coverage.reported_functionals on the frozen s5c contract, as the producer's main() does (:101).
The gate: median, max and argmax, computed by the expression of :153-154, must equal the receipt's three values exactly
(float ==, and the name). On any mismatch nothing but a STOP record is written.

Usage: python3 -I -B a3_extract.py <deploy> <assess dir: .../runs/cand/assess> <contract json> <receipt json> <out dir>
                                   <producer sha256> <lines sha256 or "-">
"""
import hashlib
import io
import json
import os
import sys
from pathlib import Path

D, A, CONTRACT, RECEIPT, RO = (Path(x) for x in sys.argv[1:6])
PRODUCER_SHA, LINES_SHA = sys.argv[6], sys.argv[7]
sys.path.insert(0, str(D / "nd-unfolding"))
import numpy as np  # noqa: E402

import s5e_analyze_candidate as AC  # noqa: E402

sha = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
src = (D / "nd-unfolding" / "s5e_analyze_candidate.py").read_bytes()
assert sha(src) == PRODUCER_SHA, ("the producer is not the pinned file", sha(src))
assert Path(AC.__file__).resolve() == (D / "nd-unfolding" / "s5e_analyze_candidate.py").resolve(), AC.__file__
lines = src.decode().splitlines(keepends=True)
LINE_NOS = (147, 148, 150, 151)
body = "".join(lines[n - 1] for n in LINE_NOS)
assert body.startswith("        dsig = ") and "jmax = np.max(np.array(jit), axis=0)" in body, body
SUMMARY = '{"median": float(np.median(jmax)), "max": float(jmax.max()),\n' \
          '                                                             "argmax": names[int(jmax.argmax())]}'
assert SUMMARY in "".join(lines[152:154]), "the summary expression is not :153-154's"
code = "\n".join(l[8:] for l in body.splitlines()) + "\n"   # dedent the method body's 8 spaces, nothing else
lines_sha = sha(body.encode())
assert LINES_SHA in ("-", lines_sha), ("the extracted lines are not the pinned text", lines_sha)

FILES = {"boot": [str(A / "data" / "boot" / f"boot_b{i}.npz") for i in range(1, 101)],
         "jit": [str(A / "data" / f"data_R_jitteredge{i}.npz") for i in (1, 2)]}
PATTERNS = {str(A / "data" / "boot" / "boot_b*.npz"): FILES["boot"],
            str(A / "data" / "data_R_jitteredge*.npz"): FILES["jit"]}


class Glob:
    @staticmethod
    def glob(pattern):
        return list(PATTERNS[pattern])   # a KeyError for any pattern but the producer's two


inputs = {}
# O_NOATIME is required. A3_LOCAL_TEST=1 (the lane's local fixture test on a machine without it) is the only exception,
# and it is recorded in the output; the cluster connect unsets it.
LOCAL_TEST = os.environ.get("A3_LOCAL_TEST") == "1"
NOATIME = getattr(os, "O_NOATIME", None)
if NOATIME is None and not LOCAL_TEST:
    raise SystemExit("STOP: this platform has no O_NOATIME")


def st(p):
    s = os.stat(p)
    return {"size": s.st_size, "mtime_ns": s.st_mtime_ns, "atime_ns": s.st_atime_ns, "ino": s.st_ino}


def load_fn(path, U):
    p = str(path)
    assert p not in inputs, ("read twice", p)
    before = st(p)
    fd = os.open(p, os.O_RDONLY | (NOATIME or 0))
    try:
        chunks = []
        while True:
            c = os.read(fd, 1 << 22)
            if not c:
                break
            chunks.append(c)
    finally:
        os.close(fd)
    b = b"".join(chunks)
    after = st(p)
    inputs[p] = {"sha256": sha(b), "bytes": len(b), "stat_before": before, "stat_after": after}
    if before != after and not LOCAL_TEST:
        raise SystemExit(f"STAT CHANGED across the read of {p}")
    return AC.load_fn(io.BytesIO(b), U)


contract_bytes = CONTRACT.read_bytes()
U, names = AC.sc.reported_functionals(json.loads(contract_bytes))
receipt_bytes = RECEIPT.read_bytes()
rec = json.loads(receipt_bytes)
assert names == rec["functional_names"] and len(names) == 153, "the contract's names are not the receipt's 153"
ns = {"np": np, "glob": Glob, "sorted": sorted, "load_fn": load_fn, "A": A, "U": U}
exec(compile(code, "s5e_analyze_candidate.py:147-151", "exec"), ns)
jmax, names_ = ns["jmax"], names
summary = eval(SUMMARY, {"np": np, "jmax": jmax, "names": names_, "float": float, "int": int})
want = rec["A3"]["data_rounding_probe_over_data_sigma"]
match = {k: summary[k] == want[k] for k in ("median", "max", "argmax")}
assert len(inputs) == 103 and sorted(inputs) == sorted(FILES["boot"] + FILES["jit"] + [str(A / "data" / "data_R_upcast.npz")])
record = {
    "schema": "s5e-a3-rounding-shifts/1",
    "what": "the 153 per-quantity A3 rounding shifts, max over the two jitteredge perturbations of |U f - U f_upcast| "
            "over the data-bootstrap sigma (100 replicas), by s5e_analyze_candidate.py:147-151 at 2f958652",
    "first_pinned_here": "these 103 inputs' sha256 are recorded here for the first time; the check is the identity of "
                         "the computed median, max and argmax with assess_receipt.json's",
    "producer": {"path": "nd-unfolding/s5e_analyze_candidate.py", "sha256": sha(src), "lines": list(LINE_NOS),
                 "lines_text_sha256": lines_sha, "summary_lines": [153, 154]},
    "contract": {"path": str(CONTRACT), "sha256": sha(contract_bytes)},
    "receipt": {"path": str(RECEIPT), "sha256": sha(receipt_bytes), "A3": want},
    "computed": summary, "match": match, "gate": all(match.values()),
    "numpy": np.__version__, "python": sys.version.split()[0], "o_noatime": NOATIME is not None, "local_test": LOCAL_TEST,
    "threads": {k: os.environ.get(k) for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")},
    "inputs": inputs,
}
RO.mkdir(parents=True, exist_ok=False)
if not record["gate"]:
    (RO / "STOP.json").write_text(json.dumps(record, indent=1) + "\n")
    print("STOP: the computed A3 summary is not the receipt's", json.dumps({"computed": summary, "want": want}))
    sys.exit(5)
rows = ["index,name,shift_over_data_sigma"] + [f"{i},{n},{float(v)!r}" for i, (n, v) in enumerate(zip(names, jmax))]
csv_bytes = ("\n".join(rows) + "\n").encode()
(RO / "a3_rounding_shifts.csv").write_bytes(csv_bytes)
record["csv"] = {"name": "a3_rounding_shifts.csv", "sha256": sha(csv_bytes), "rows": len(names)}
(RO / "a3_rounding_shifts.json").write_text(json.dumps(record, indent=1) + "\n")
print(json.dumps({"gate": True, "computed": summary, "csv_sha256": record["csv"]["sha256"], "lines_sha256": lines_sha}))
PYEOF
got=$(sha256sum "$X/a3_extract.py" | cut -d' ' -f1); echo "a3_extract.py sha256 $got"
[ "$got" = "$EXTRACT_SHA" ] || { echo "STOP: a3_extract.py is not the pinned script"; finish 9; }
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0
unset A3_LOCAL_TEST
echo "python $("$PY" -c 'import sys, numpy; print(sys.version.split()[0], "numpy", numpy.__version__)'); threads 1; nice 19; ionice idle"
( cd "$X" && nice -n 19 ionice -c3 env -u PYTHONPATH "$PY" -I -B "$X/a3_extract.py" "$D" "$A" "$C" "$X/assess_receipt.json" "$X/out" \
    "$PRODUCER_SHA" "$LINES_SHA" )
rc=$?
echo "extract rc=$rc"
ls -la "$X/out" 2>&1
for f in a3_rounding_shifts.csv a3_rounding_shifts.json STOP.json; do
  [ -e "$X/out/$f" ] && echo "$f sha256 $(sha256sum "$X/out/$f" | cut -d' ' -f1) bytes $(stat -c %s "$X/out/$f")"
done
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "porcelain --ignored lines after: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy changed"; finish 9; }
finish $rc

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

"""COV2D's pilot readout (COV2D-DECLARATION.md sections 2, 8, 9.12, 10): control (2b), section 9.12, the REPRICE
check and the DVS read, from the pilot job's outputs. root_6_28 with MAT (the job's environment).

* (2b): the pilot's E_R-argv unfold on (2a)'s kept file must reproduce E_R's hXSec2D (part B's out/ER/xsec.root, sha256
  a5c13fc3..., re2c_rollup.py:110) under RE-2's own equality rule, ``re2_k1.compare`` imported unchanged: at most 1e-8
  relative on the 205 reported cells with the same cell set; bitwise equality reported, not deciding.
* Section 9.12: the MaRES:0 universe unfold and the first J3 lateral on (2a)'s file must reproduce part B's U_MaRES_0
  and S3_BeamAngleX0 by the same rule. Each part B product is checked against part B's committed sums
  (``re2c_rollup.partb_sums``) before it is read, through an O_NOATIME copy; a missing product is INVALID.
* A failure of (2b) or 9.12 stops (c) (section 2) and, with the STOP count at one, ends it unless Joseph rules
  otherwise (section 6 (iii)); the readout says so and goes to the director.
* REPRICE (section 8): a run class whose pilot wall per run exceeds 1.25 x part B's wall per run. Part B's is its job's
  elapsed time (partb_readout/ledger.tsv) x min(lanes, runs) / runs (partb_jobs.tsv), preflight included; a toy's
  baseline is the central run's.
* The DVS read (the director's ruling (b)): the staged copy's and the CFS original's MB/s, as the job recorded them.

MEASURES: the pilot's controls and walls. CANNOT AUTHORIZE: the bulk; the readout goes to the director first.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
for p in (HERE, REPO / "2d-unfolding" / "re2", REPO / "2d-unfolding" / "re2" / "partc"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
import cov2d as c  # noqa: E402

RE2RUN = REPO / "docs/orchestration/state/2d-closeout/stageF/methods/re2/run"
REPRICE = 1.25
CLASS_OF = {"P912_L": "lateral", "L_": "lateral", "P2b": "central", "X_": "central", "T_": "toy", "B_": "replica",
            "P912_U": "universe", "U_": "universe"}
PARTB_CLASS_JOBS = {"central": ["J1"], "universe": ["J2a", "J2b", "J2c", "J2d"], "lateral": ["J3"],
                    "replica": ["J4a", "J4b", "J4c"]}
COMPARE = {"2b": ("P2b_ER", "ER"), "9.12_universe": ("P912_U_MaRES_0", "U_MaRES_0"),
           "9.12_lateral": ("P912_L_BeamAngleX_0", "S3_BeamAngleX0")}


def class_of(label: str) -> str:
    for prefix, k in CLASS_OF.items():
        if label.startswith(prefix):
            return k
    raise c.Refusal(f"no run class for {label}")


def partb_wall_per_run(ledger_tsv: str, jobs_tsv: str) -> dict:
    """Part B's wall per run per class: elapsed x min(lanes, runs) / runs, averaged over the class's jobs."""
    el = {r[1].replace("re2b-", ""): int(r[6]) for r in (ln.split("\t") for ln in ledger_tsv.splitlines()[1:]) if r}
    lay = {r[0]: (int(r[3]), int(r[5])) for r in (ln.split("\t") for ln in jobs_tsv.splitlines()[1:]) if r}
    out = {}
    for k, jobs in PARTB_CLASS_JOBS.items():
        per = [el[j] * min(lay[j][0], lay[j][1]) / lay[j][1] for j in jobs]
        out[k] = sum(per) / len(per)
    out["toy"] = out["central"]
    return out


def reprice(walls_tsv: str, baseline: dict) -> dict:
    """Per class: the pilot's mean wall per run, its ratio to part B's, and whether it is above 1.25."""
    per = {}
    for ln in walls_tsv.splitlines():
        if not ln.strip():
            continue
        label, t0, t1, rc = ln.split("\t")
        if int(rc) == 0:
            per.setdefault(class_of(label), []).append(int(t1) - int(t0))
    out = {}
    for k, v in per.items():
        w = sum(v) / len(v)
        out[k] = {"pilot_s": w, "partb_s": baseline[k], "ratio": w / baseline[k], "reprice": w > REPRICE * baseline[k]}
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--o", required=True, help="the run namespace (out/, walls.pilot.*.tsv, SHA256SUMS.pilot.*, logs/)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    import re2_k1 as k1
    import re2c_rollup as ro
    import cov2d_pseudo_write as pw
    O = Path(a.o)
    rec = {"stop": [], "invalid": []}
    ours = {}
    for f in sorted(O.glob("SHA256SUMS.pilot.*")):
        for ln in f.read_text().splitlines():
            sha, rel = ln.split()
            ours[rel] = sha
    sums = ro.partb_sums()
    with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as td:
        refs = {}

        def ref(label):   # part B's product, pinned (E_R by its sha, the rest by part B's sums), as an O_NOATIME copy
            if label not in refs:
                src = f"{ro.NS_R}/out/{label}/xsec.root"
                want = pw.PINS["er"][1] if label == "ER" else sums.get(f"{label}/xsec.root")
                if want is None or not os.path.exists(src):
                    raise FileNotFoundError(src)
                d = Path(td) / label
                d.mkdir()
                refs[label] = pw.copy_noatime(src, d, want)[0]
            return refs[label]
        cells = None
        rec["controls"] = {}
        for name, (mine, theirs) in COMPARE.items():
            p = O / "out" / mine / "xsec.root"
            if f"{mine}/xsec.root" not in ours or not p.exists():
                rec["invalid"].append(f"{name}: the pilot's {mine} is missing or undigested")
                continue
            if hashlib.sha256(p.read_bytes()).hexdigest() != ours[f"{mine}/xsec.root"]:
                rec["invalid"].append(f"{name}: {mine}'s sha256 is not the job's")
                continue
            try:
                r = ref(theirs)
            except (FileNotFoundError, c.Refusal) as e:
                rec["invalid"].append(f"{name}: part B's {theirs}: {e}")
                continue
            ref_x = k1.xsec(r)
            if cells is None:   # E_R's 205 reported cells, hXSec2D > 0 in C order (re2_k1's convention)
                cells = np.flatnonzero(k1.xsec(ref("ER")).ravel(order="C") > 0)
            cmp_ = k1.compare(k1.xsec(p), ref_x, cells)
            cmp_["pass"] = cmp_["max_rel"] <= k1.TOL and cmp_["same_cell_set"]
            rec["controls"][name] = cmp_
            if not cmp_["pass"]:
                rec["stop"].append(f"{name} did not reproduce part B (section 2/9.12): {cmp_}")
    walls = "".join(f.read_text() for f in sorted(O.glob("walls.pilot.*.tsv")))
    base = partb_wall_per_run((RE2RUN / "partb_readout" / "ledger.tsv").read_text(),
                              (RE2RUN / "partb_jobs.tsv").read_text())
    rec["reprice"] = reprice(walls, base)
    rec["reprice_classes"] = sorted(k for k, v in rec["reprice"].items() if v["reprice"])
    dvs = sorted((O / "logs").glob("dvs-rate-*.json"))
    rec["dvs_rate"] = json.loads(dvs[-1].read_text()) if dvs else "not recorded"
    if rec["stop"]:
        rec["verdict"] = "STOP"
        rec["consequence"] = "(c)'s second STOP (section 6 (iii)): (c) ends unless Joseph rules otherwise"
    elif rec["invalid"]:
        rec["verdict"] = "INVALID"
    else:
        rec["verdict"] = "PASS"
    Path(a.out).write_text(json.dumps(rec, indent=1, sort_keys=True))
    print(f"COV2D-PILOT {rec['verdict']} reprice={rec['reprice_classes']} invalid={len(rec['invalid'])}")
    return {"PASS": 0, "STOP": 3}.get(rec["verdict"], 2)


if __name__ == "__main__":
    sys.exit(main())

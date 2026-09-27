#!/usr/bin/env python3
"""s5p Stage 7: the batch-sequential calibration controller for one null (amendment 7 candidate).

Run by the production queue between calibration batches. It evaluates the null's claim p-values (total and
shape; ``s5p_joint.test_null``: the observed statistics against the calibration products present, every shift
variant) and applies ``s5p_inference.sequential_decision`` to each, with the decision thresholds of the frozen
family (every Holm level alpha / j, j = 1..m, and 0.01, 0.05). It writes one status file per look
(``<status-dir>/<null>-B<B>.json``) and ``<status-dir>/<null>-final.json`` when it stops.

Exit 0: continue (launch the next batch); 3: stopped (the rule is met for both tests, or the declared maximum
is reached); any other code is an error and stops the queue.

MEASURES: whether the frozen stopping rule is met. CANNOT AUTHORIZE: a rejection (the evaluator's Holm step
decides); a stop that the rule does not give.
"""
from __future__ import annotations

import argparse
import datetime
import glob
import json
from pathlib import Path

import numpy as np

import s5p_inference as si
import s5p_joint as sj


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--design", type=Path, required=True)
    ap.add_argument("--v", type=Path, required=True)
    ap.add_argument("--null", required=True)
    ap.add_argument("--status-dir", type=Path, required=True)
    a = ap.parse_args(argv)
    design = json.loads(a.design.read_text())
    spec = design["nulls"][a.null]
    seq = spec["calibration_n"]
    if not isinstance(seq, dict) or "max" not in seq:
        raise SystemExit(f"{a.null}: not a sequential calibration")
    a.status_dir.mkdir(parents=True, exist_ok=True)
    files = sorted(glob.glob(spec["calibration_glob"]))
    B = len(files)
    status = {"schema": "s5p-seqstop/1", "null": a.null, "B": B, "max": int(seq["max"]),
              "utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
              "design_sha256": sj.sha256(a.design), "v_sha256": sj.sha256(a.v)}
    if B == 0:
        status.update({"stop": False, "reason": "no calibration product yet"})
    else:
        stage1 = json.loads(Path(design["stage1"]).read_text())
        supported = json.loads(Path(design["s5c_contract"]).read_text())["measurement"]["partition_J"]["supported_cells"]
        U, names, pz_index = sj.j_matrix(stage1, supported)
        model = sj.Model(design, U)
        V = np.asarray(np.load(a.v, allow_pickle=False)["V"], float)
        coefs = [float(c) for c in design.get("shift_coefficients", [0.0])]
        entry = sj.test_null(model, design, a.null, V, names, pz_index, files, coefs)
        m = 2 * len(design["nulls"])
        th = sorted(set(si.holm_thresholds(design["alpha_family"], m)) | {0.01, 0.05})
        dec = {s: si.sequential_decision(entry[s]["k"], entry[s]["B"], th) for s in ("total", "shape")}
        rule = all(d["stop"] for d in dec.values())
        status.update({"files_first_last": [files[0], files[-1]], "decisions": dec, "thresholds": th,
                       "stop": rule or B >= int(seq["max"]),
                       "reason": "rule met for both tests" if rule else ("maximum reached" if B >= int(seq["max"]) else "continue")})
    (a.status_dir / f"{a.null}-B{B}.json").write_text(json.dumps(status, indent=1) + "\n")
    if status["stop"]:
        (a.status_dir / f"{a.null}-final.json").write_text(json.dumps(status, indent=1) + "\n")
        print(json.dumps({"null": a.null, "B": B, "stop": True, "reason": status["reason"]}))
        return 3
    print(json.dumps({"null": a.null, "B": B, "stop": False, "reason": status["reason"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

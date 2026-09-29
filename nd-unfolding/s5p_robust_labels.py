#!/usr/bin/env python3
"""s5p: the reported sub-fine-residual robustness labels under the owner's A7 ruling (report only).

Ruling (docs/orchestration/RULING-20260929-s5p-A7-robustness-flag.md): for each hypothesis REJECTED by the primary
(kappa = 2) Holm procedure with determinacy (``decisions``), the label is "robust to the sub-fine residual" if it is
also rejected by the full Holm re-run at kappa = 3 (``decisions_robust_kappa``), else "not robust"; every other
hypothesis gets "not applicable".

This reads the frozen evaluator's output (``s5p_joint.py evaluate``) and writes a SEPARATE file; it computes no
statistic and changes no decision. The frozen field ``robust_to_the_sub_fine_residual`` (a boolean per test: equal
decision labels in the two runs) stays in the evaluator output unchanged; for a rejection it carries the same
information as the label, for any other test it is not a flag under the ruling.

MEASURES: nothing. CANNOT AUTHORIZE: a claim, a decision or a change of the frozen rules.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROBUST, NOT_ROBUST, NA = "robust to the sub-fine residual", "not robust", "not applicable"
RULING = "docs/orchestration/RULING-20260929-s5p-A7-robustness-flag.md"


def labels(decisions: dict, decisions_robust_kappa: dict) -> dict:
    if set(decisions) != set(decisions_robust_kappa):
        raise SystemExit("the primary and the kappa_robust Holm runs cover different tests")
    out = {}
    for test, d in decisions.items():
        if d["decision"] != "rejected":
            out[test] = NA
        else:
            out[test] = ROBUST if decisions_robust_kappa[test]["decision"] == "rejected" else NOT_ROBUST
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--evaluate", type=Path, required=True, help="the s5p_joint.py evaluate output (read only)")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        raise SystemExit(f"refusing to overwrite {a.out}")
    raw = a.evaluate.read_bytes()
    res = json.loads(raw)
    lab = labels(res["decisions"], res["decisions_robust_kappa"])
    out = {"schema": "s5p-robust-labels/1", "ruling": RULING,
           "evaluate": str(a.evaluate), "evaluate_sha256": hashlib.sha256(raw).hexdigest(),
           "code_sha256": hashlib.sha256(Path(__file__).resolve().read_bytes()).hexdigest(),
           "labels": lab,
           "frozen_field_unchanged": res.get("robust_to_the_sub_fine_residual")}
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(lab, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

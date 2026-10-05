"""Compare two `--inputs-only` run directories (predecessor `run_replicate.py` vs `run_design.py`).

Equal means: every `replicate_arrays.npz` member byte-identical (same keys, dtypes, shapes), the
engine input digests (`input_digests_before_arm`) equal, the selection's row digests equal, and the
run identity equal. Writes a JSON verdict and exits 1 on any difference.

    compare_inputs_runs.py --predecessor <dir> --study <dir> --output <json>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np


def arrays(path: Path) -> dict[str, tuple[str, tuple, str]]:
    with np.load(path) as z:
        return {k: (str(z[k].dtype), tuple(z[k].shape),
                    hashlib.sha256(np.ascontiguousarray(z[k]).tobytes()).hexdigest())
                for k in sorted(z.files)}


def compare(pred: Path, study: Path) -> dict:
    a, b = arrays(pred / "replicate_arrays.npz"), arrays(study / "replicate_arrays.npz")
    ra = json.loads((pred / "inputs_receipt.json").read_text())
    rb = json.loads((study / "inputs_receipt.json").read_text())
    out = {"predecessor": str(pred), "study": str(study),
           "arrays_keys_equal": sorted(a) == sorted(b),
           "arrays_members": {k: a.get(k) == b.get(k) for k in sorted(set(a) | set(b))},
           "input_digests_before_arm_equal":
               ra["input_digests_before_arm"] == rb["input_digests_before_arm"],
           "selection_row_digests_equal": all(
               ra["selection"][k] == rb["selection"][k]
               for k in ("prior_rows_sha256", "pseudo_rows_sha256",
                         "prior_identity_sha256", "pseudo_identity_sha256")),
           "selection_record_equal": ra["selection"] == rb["selection"],
           "run_identity_equal": ra["run_identity"] == rb["run_identity"],
           "counts_equal": ra["counts"] == rb["counts"],
           "counts": rb["counts"],
           "input_digests_before_arm": rb["input_digests_before_arm"],
           "prior_rows_sha256": rb["selection"]["prior_rows_sha256"],
           "pseudo_rows_sha256": rb["selection"]["pseudo_rows_sha256"],
           "code_commit": {"predecessor": ra.get("code_commit"), "study": rb.get("code_commit")}}
    out["all_equal"] = bool(out["arrays_keys_equal"] and all(out["arrays_members"].values())
                            and out["input_digests_before_arm_equal"]
                            and out["selection_row_digests_equal"]
                            and out["run_identity_equal"] and out["counts_equal"])
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--predecessor", type=Path, required=True)
    ap.add_argument("--study", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    result = compare(args.predecessor, args.study)
    args.output.write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: result[k] for k in ("all_equal", "arrays_keys_equal",
                                              "input_digests_before_arm_equal",
                                              "selection_row_digests_equal",
                                              "selection_record_equal",
                                              "run_identity_equal", "counts_equal")}))
    return 0 if result["all_equal"] else 1


if __name__ == "__main__":
    sys.exit(main())

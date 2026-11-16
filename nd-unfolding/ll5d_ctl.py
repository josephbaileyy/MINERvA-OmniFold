#!/usr/bin/env python3
"""LL5D amendment A1b.1: the procedure controls' bitwise check (LL5D-DECLARATION.md section 10, and section 11 step 6's
"every control passing"). The pilot writes the four control products (``ll5d_b`` role ``control``, on the data); this
step compares each with S1's committed product of the same procedure, bitwise: the ``xsec_flat`` array's dtype, shape
and bytes. It writes one control record, which the bulk's connect pins by its sha256.

The references are S1's committed products in this repository, each pinned here by path and sha256. A reference whose
digest differs, or a missing product or reference, refuses (INVALID, rc 5, unrepaired). A control that differs is FAIL
(rc 6): section 10 reads any control failure as INVALID, reported unrepaired, and the bulk is not submitted.

Exit 8 is OR-ed in on an atime move, as in ll5d and ll5d_b.

    python3 -B nd-unfolding/ll5d_ctl.py --unfolds <products dir> --repo <deploy root> --out <controls.json>
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import fd_1b_inv as inv  # noqa: E402
import ll5d_b  # noqa: E402

SCHEMA = "ll5d-controls/1"
KEY = "xsec_flat"
S1_DIR = "docs/orchestration/state/measurement-paper/5d-community-20261024/s1/readout/s1_assembly"
# Each control (ll5d_b.CONTROLS) and S1's product of the same procedure: set A's replica b = 1 (bootstrap seed 1,
# jitter seed 101) and the three single-universe unfolds of the data. Digests as S1's SHA256SUMS records them.
REFERENCES = {
    "setA_b1": (f"{S1_DIR}/data_b1_j101.npz", "95a9f09c44b1fa997242c3fa4740400084fa98ce78ca6e99f38f6970e65fbabf"),
    "MaRES_0": (f"{S1_DIR}/S1_MaRES_0.npz", "aa3ed226ed866a92a9b41fcd5e9f94b32c8928364f9986f1bddde3a317644667"),
    "Flux_0": (f"{S1_DIR}/S1_Flux_0.npz", "17e872735e5c9df7926b27215155b2b701dde20959498cb0345d230b99636d27"),
    "GEANT_Pion_0": (f"{S1_DIR}/S1_GEANT_Pion_0.npz", "2972f5a33a8464da9d9f7e8b98d2c3a428f5a1c35db02eda7e5f73309a7b817a"),
}
RC_FAIL, RC_INVALID = 6, 5


class Refusal(RuntimeError):
    """An input is not what the step is defined on: INVALID, reported unrepaired."""


def _read(path: Path) -> tuple[bytes, str]:
    """The file's bytes and sha256, read once through O_NOATIME."""
    if not path.exists():
        raise Refusal(f"missing {path}")
    with inv.open_noatime(path) as fh:
        raw = fh.read()
    return raw, hashlib.sha256(raw).hexdigest()


def _array(raw: bytes, path: Path) -> np.ndarray:
    z = np.load(io.BytesIO(raw), allow_pickle=False)
    if KEY not in z.files:
        raise Refusal(f"{path} holds no {KEY}")
    return np.asarray(z[KEY])


def compare(a: np.ndarray, b: np.ndarray) -> dict:
    """Bitwise equality of two arrays: the same dtype, the same shape and the same bytes. The counts and the largest
    difference are descriptive and gate nothing."""
    same_dtype, same_shape = a.dtype == b.dtype, a.shape == b.shape
    equal = bool(same_dtype and same_shape and a.tobytes() == b.tobytes())
    out = {"equal": equal, "dtype": [a.dtype.str, b.dtype.str], "shape": [list(a.shape), list(b.shape)],
           "same_dtype": bool(same_dtype), "same_shape": bool(same_shape)}
    if same_shape:
        diff = np.asarray(a, np.float64) != np.asarray(b, np.float64)
        out["elements_differing"] = int(np.count_nonzero(diff))
        out["max_abs_difference"] = float(np.max(np.abs(np.asarray(a, np.float64) - np.asarray(b, np.float64)))) if a.size else 0.0
    return out


def controls(unfolds: Path, repo: Path) -> dict:
    """The four controls against their references; PASS only if every one is bitwise equal."""
    if tuple(REFERENCES) != tuple(ll5d_b.CONTROLS):
        raise Refusal(f"the references {tuple(REFERENCES)} are not the declared controls {tuple(ll5d_b.CONTROLS)}")
    rows = {}
    for c, (rel, want) in REFERENCES.items():
        ref_path = repo / rel
        ref_raw, ref_sha = _read(ref_path)
        if ref_sha != want:
            raise Refusal(f"{rel}: sha256 {ref_sha}, not the pinned {want}")
        prod_path = unfolds / ll5d_b.product_name("data", "control", c)
        prod_raw, prod_sha = _read(prod_path)
        rows[c] = {"product": prod_path.name, "product_sha256": prod_sha, "reference": rel, "reference_sha256": ref_sha,
                   **compare(_array(prod_raw, prod_path), _array(ref_raw, ref_path))}
    passes = all(r["equal"] for r in rows.values())
    return {"schema": SCHEMA, "step": "controls", "key": KEY, "controls": rows,
            "verdict": "PASS" if passes else "FAIL", "failed": [c for c, r in rows.items() if not r["equal"]],
            "code_sha256": {"ll5d_ctl.py": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--unfolds", type=Path, required=True)
    ap.add_argument("--repo", type=Path, required=True, help="the deploy's root, where S1's committed products are")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        raise Refusal(f"refusing to overwrite {a.out}")
    inv.OPENED.clear()
    try:
        rec = controls(a.unfolds, a.repo)
    except (Refusal, inv.Refusal) as exc:
        bad = {"schema": SCHEMA, "step": "controls", "verdict": "INVALID", "why": str(exc), "atime": inv.atime_check()}
        a.out.with_suffix(".invalid.json").write_text(json.dumps(bad, indent=1, sort_keys=True))
        print(f"LL5D-CONTROLS INVALID ({exc})")
        return RC_INVALID | (ll5d_b.ll5d.ATIME_RC if bad["atime"]["moved"] else 0)
    rec["atime"] = inv.atime_check()
    a.out.write_text(json.dumps(rec, indent=1, sort_keys=True))
    print(f"LL5D-CONTROLS verdict={rec['verdict']} failed={rec['failed']}")
    return (0 if rec["verdict"] == "PASS" else RC_FAIL) | (ll5d_b.ll5d.ATIME_RC if rec["atime"]["moved"] else 0)


if __name__ == "__main__":
    sys.exit(main())

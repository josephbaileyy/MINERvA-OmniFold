#!/usr/bin/env python3
"""T2A's decomposition at C_T' (the director's follow-on 1 after D1, 2026-11-14; COV2D-G2R-DECLARATION.md:135-137).

The bound T2A code, `fd/tier2-20261110/t2a/code/t2a_split.py` (sha256 462ff4e2…, committed), run UNCHANGED through its
own main(). The one difference is its input pins. main() checks each input against the module-level dict PINS[T]
before reading it. This driver loads t2a_split.py from its committed bytes (refusing any other sha256), replaces
PINS[T] for the mode it is given, and then calls t2a_split.main() with the same arguments T2A used. Nothing else in
t2a_split is touched:
  - MODULE_PINS: fd_1b_null.py ec1402db…, cov2d_null.py a92c0506…, cov2d.py 76cbceba…, which are the same bytes at the
    G2R commit 401733bc as at T2A's;
  - RANKS (73, 139), N_MC (2,000,000), A1_CHI2_TOL ("A5"), every control and every number.
Modes:
  cov2d   PINS[T] is left as committed. On COV2D's committed blocks, score and null, this reproduces the committed
          t2a_<T>.json. This is control C0, run first; c0_compare.py compares its record with the committed one.
  g2r     PINS[T]'s blocks, score and null become the G2R readout's blocks_g2r_<T>.npz, score_g2r_<T>.json and
          null_g2r_<T>.json, at the sha256 their out.sha256 recorded. The capture keeps its committed pin: the 300
          error vectors E_<T>.npz are the same ones (COV2D-G2R-DECLARATION.md:88-90).
t2a_split's own controls then run against the G2R inputs: A1, A2, A4, and A3 (the null rebuilt on laws_at_T of the
G2R blocks' band arrays must reproduce null_g2r_<T>.json's q_joint within one se_joint). Any failure is t2a_split's
STOP (rc 8, <stem>.STOP.json), reported unrepaired.
A sidecar <out stem>.driver.json records the mode, the PINS used and t2a_split's sha256. The t2a record itself is
t2a_split's own output, byte for byte.
    python3 -I -B t2a_g2r.py --mode {cov2d|g2r} --t2a-split PATH -- <t2a_split.main arguments>
"""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

T2A_SPLIT_SHA = "462ff4e204530a231af35b850b91d9ffe19eb9f6596ee6aace4aeb29449a2f79"
G2R_PINS = {   # out.sha256 of $O/readout/<T>/ (receipt fd/receipts-cov2d/g2r/readout/<T>/out.sha256.txt)
    "G18": {"blocks": "55ad7cc4faa4680b49391a9d68f52fcaa707150bd1300915063d66a16be9bfbe",
            "score": "27374aab74793444ee20561ced1066247b225a40067092d7d181e186128b9ec2",
            "null": "d6b84ec086477d615a3240f3bdf4ea677ad0f24f801cfe912b885ac1e225f003"},
    "AR23": {"blocks": "c060cb40232e0112ec440951f94841e87fc98b542a165eed2c8242898508a70a",
             "score": "fb6d1f7fddfa18124bf097087a2f895582ef0991f9888c5ab1ce16cefbbe3079",
             "null": "ae82601d7f8b2f5474bfe2a6060245c854eae2cbf90d706e8f1276971ff45872"},
}


def main(argv) -> int:
    sep = argv.index("--")
    head, rest = argv[:sep], argv[sep + 1:]
    mode = head[head.index("--mode") + 1]
    path = Path(head[head.index("--t2a-split") + 1])
    assert mode in ("cov2d", "g2r"), mode
    got = hashlib.sha256(path.read_bytes()).hexdigest()
    if got != T2A_SPLIT_SHA:
        print(f"T2A-G2R REFUSED: {path} is {got}, not the committed t2a_split.py {T2A_SPLIT_SHA}")
        return 2
    spec = importlib.util.spec_from_file_location("t2a_split", path)
    t2a = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(t2a)
    T = rest[rest.index("--truth") + 1]
    out = Path(rest[rest.index("--out") + 1])
    committed = dict(t2a.PINS[T])
    if mode == "g2r":
        t2a.PINS[T] = {**G2R_PINS[T], "capture": committed["capture"]}
    side = {"schema": "t2a-g2r-driver/1", "mode": mode, "truth": T, "t2a_split_sha256": got,
            "pins_committed": committed, "pins_used": t2a.PINS[T], "module_pins": t2a.MODULE_PINS,
            "ranks": list(t2a.RANKS), "n_mc": t2a.N_MC, "a1_chi2_tol": t2a.A1_CHI2_TOL,
            "label": "descriptive only (COV2D-G2R-DECLARATION.md:135-137); t2a_split.main() unchanged, PINS[T] as listed"}
    rc = t2a.main(rest)
    side["t2a_split_rc"] = rc
    out.with_name(out.stem + ".driver.json").write_text(json.dumps(side, indent=1) + "\n")
    print(f"T2A-G2R mode={mode} truth={T} rc={rc}")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

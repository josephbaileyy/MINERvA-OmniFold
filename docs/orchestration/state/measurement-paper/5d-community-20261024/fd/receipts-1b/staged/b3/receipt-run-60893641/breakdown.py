"""1B binding 3, stage 3: a descriptive breakdown of receipt 60893641's section 2b STOP (the director, 2026-11-06).

Confined to the record (the director's correction): it reads only the committed receipt.json and the bound
fd_1b_mc / fd_1b_toys / s1_assemble constants that label the 900 declared draws, each checked first. No declared input
is read and compose is not rerun (amendment 2 section 8: the STOP goes unrepaired). An item the record cannot answer is
printed as "not in the record". Decides nothing, writes only its stdout. Run from a checkout's nd-unfolding/:

    PYTHONPATH=$PWD python3 -B .../b3/receipt-run-60893641/breakdown.py <receipt.json>

For section 2b the receipt keeps the flagged draws' indices and the largest per-draw cell count
(``denominator_check``: ``sorted(bad)`` and ``max(bad.values())``), and nothing per cell.
"""
import hashlib
import json
import sys
from pathlib import Path

import fd_1b_mc as m
import fd_1b_toys as toys
import s1_assemble

RECEIPT_SHA = "9995f55adb7846e230c2e982221d20e7c5c1136daf5cb4576e355544bb54fa3d"
CODE_SHA = {"fd_1b_mc.py": "062628b69976f730d9d394e64ecf6f93d9952654306471ac0119542c6b07dd67",
            "fd_1b_toys.py": "869a65c3bcce1a3b56ecd197ecdf3b6cf2741e0611f91b582c3064f67967bc08"}
NOT = "not in the record"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main(receipt_path: str) -> None:
    rp = Path(receipt_path)
    if sha(rp) != RECEIPT_SHA:
        sys.exit(f"STOP {rp}: sha256 is not {RECEIPT_SHA}")
    for mod in (m, toys):
        p = Path(mod.__file__)
        if sha(p) != CODE_SHA[p.name]:
            sys.exit(f"STOP {p}: not the bound blob")
    print(f"inputs: receipt.json {RECEIPT_SHA}; fd_1b_mc 062628b6, fd_1b_toys 869a65c3 (constants only); "
          f"python {sys.version.split()[0]}")
    r = json.loads(rp.read_text())
    den = r["denominator"]
    flagged = set(den["draws_with_nonpositive_cells"])
    labels = [(t, sd) for t in m.TRUTHS for sd in m.TOY_SEEDS[t]]       # receipt(): draw d is labels[d]
    assert len(labels) == 900 and max(flagged) < 900
    n_int = len(toys.INTERACTION_BANDS)
    n_det = len(toys.DETECTOR_DRAW_ORDER)
    assert all(b in s1_assemble.EXPECT for b in toys.INTERACTION_BANDS)

    print("\n== 1. the flagged cells (distinct cells, each one's frequency, 5D bin, reporting cell R00-R15, d_CV)")
    print(f"  {NOT}: denominator_check keeps no cell identities. The record has {den['n1']['cells']} denominator "
          f"cells, and its N1 on them: {den['n1']['pairs_above']} (cell, draw) pairs above {r['n1_bound']}, max "
          f"{den['n1']['max']:.3f}")

    print("\n== 2. per truth (the truth labels the seed range only; the composite denominator is the universes')")
    for t in m.TRUTHS:
        ds = [d for d, (tt, _) in enumerate(labels) if tt == t]
        nf = sum(d in flagged for d in ds)
        print(f"  {t:7s} draws {ds[0]}..{ds[-1]}: flagged {nf} of {len(ds)}, clean {len(ds) - nf}")
    print("  binding 3 runs g18 and ar23 only (the no-plug-in path); the receipt checks all 900 declared draws")

    print("\n== 3. per draw, the number of non-positive cells")
    print(f"  flagged draws {len(flagged)} of 900; max {den['max_cells']}; median and the rest of the distribution: "
          f"{NOT} (only max(bad.values()) is kept)")

    print("\n== 4. mechanism")
    print(f"  whether the flagged cells are the sparse low-d_CV cells of amendment 2 section 5: {NOT}")
    print(f"  universes per draw, by construction (toys.draw, draw_universes): 1 flux + {n_int} interaction + "
          f"{n_det} detector = {1 + n_int + n_det}, in every draw. The detector universes' denominators are the CV's "
          f"(receipt(): A2.1 (e2), check D), so the composite denominator's departures are the flux universe's and "
          f"the {n_int} interaction universes': {1 + n_int} terms")
    print("  the per-row record beside it (matmul, descriptive; rows with a_D < 0 where a_CV > 0):")
    for k in ("wt", "wr", "bkgw"):
        nc = r["exact"][k]["negative_composite"]
        cf = nc["clipped_fraction_per_draw"]
        print(f"    {k:5s} rows {r['exact'][k]['rows']}: in some draw {nc['rows_in_some_draw']}, draws with any "
              f"{nc['draws_with_any']}, max per draw {nc['rows_max_per_draw']}; clipped fraction per draw median "
              f"{cf['median']:.4f}, max {cf['max']:.4f}")
    print(f"  negative-weight universes: {r['negative_weight_universes']}")

    print("\n== 5. the 8 clean draws")
    clean = sorted(set(range(900)) - flagged)
    for d in clean:
        print(f"  draw {d:3d}: {labels[d][0]:6s} seed {labels[d][1]}")
    print(f"  their universes, and anything else distinctive about them: {NOT} (the draws' universes are rebuilt only "
          f"from the flux constraint, a declared input)")


if __name__ == "__main__":
    main(sys.argv[1])

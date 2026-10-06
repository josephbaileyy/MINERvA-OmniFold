"""Exact-paired DEV check from existing operands only (no fitting).

    pgc_dev_paired.py --pet-source SRC --selections <dir of selection_*.npz> \
        --dev3n <dir of dev3N-*/iterations/iterNN.npz> --out dev_paired.json

The PET finalists' development runs `dev3N-{H2S1T24,L128S1T24}-{F0,F1,T*-<case>}` used the same
predecessor `replicate_arrays.npz` (identical digests) as the matched GBDT study's selections. Each
PET push at the finalist's k (H2S1T24 5, L128S1T24 4) is scored here with the matched study's own
scorer (`scalar_scoring.Scorer`), so both methods share one definition:
- E_avail R against the replicate's pseudodata truth;
- E_avail x proton and E_avail x neutron class recoveries, also against pseudodata truth.

The PET E_avail R is required to equal the committed dev3N score to 1e-9; the scorer refuses
otherwise. The GBDT values are the committed matched-study task rows: efficiency-corrected, both
truth sets, seeds 1-3, every k. Simulation only; descriptive (two draws per case).
"""
from __future__ import annotations

import argparse
import gzip
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import pgc_source  # noqa: E402

FINALISTS = {"H2S1T24": 5, "L128S1T24": 4}
UNITS = [("F0", "dev"), ("F1", "dev"), ("T0", "D1_m0.350"), ("T1", "D1_m0.350"),
         ("T0", "D4c_p_up"), ("T1", "D4c_p_up"), ("T0", "D4d_n_up"), ("T1", "D4d_n_up")]
GBDT_K = (3, 7, 10)
TOL = 1e-9
DEV3N = "nd-unfolding/pet/final_design/results/dev3N"
ROWS = "nd-unfolding/pet/final_design/scalar/results/matched_task_rows-20260925.jsonl.gz"


def run_name(design: str, sel: str, case: str) -> str:
    return f"dev3N-{design}-{sel}" + ("" if case == "dev" else f"-{case}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pet-source", type=Path, required=True)
    ap.add_argument("--selections", type=Path, required=True)
    ap.add_argument("--dev3n", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    src = pgc_source.activate(a.pet_source)
    import scalar_scoring as ss
    import selection_data as sd

    rows = [json.loads(line) for line in gzip.open(a.pet_source / ROWS, "rt")]
    receipt = json.loads((a.pet_source / "nd-unfolding/pet/final_design/scalar/"
                          "extract_receipt.json").read_text())
    units = []
    sel_cache: dict[str, dict] = {}
    for sel, case in UNITS:
        if sel not in sel_cache:
            sel_cache[sel] = sd.load_selection(a.selections / f"selection_{sel}.npz")
        prob = sd.build_problem(sel_cache[sel], sel, case)
        scorer = ss.Scorer(prob)
        sel_sha = receipt["selections"][sel]["replicate_arrays"][case]["sha256"]
        rec = {"selection": sel, "case": case, "replicate_arrays_sha256": sel_sha,
               "oracle": {"eavail_R": scorer.oracle["eavail"]["recovery"],
                          "joint_p_R": scorer.oracle["topology"]["joint_eavail_p"]["recovery"],
                          "joint_n_R": scorer.oracle["topology"]["joint_eavail_n"]["recovery"]},
               "pet": {}, "gbdt": {}}
        for design, k in FINALISTS.items():
            name = run_name(design, sel, case)
            committed = json.loads((a.pet_source / DEV3N / f"{name}.scores.json").read_text())
            if committed["provenance"]["replicate_arrays_sha256"] != sel_sha:
                raise SystemExit(f"{name}: replicate arrays differ from the matched selection")
            it = [r for r in committed["iterations"] if r["k"] == k][0]
            f = a.dev3n / name / "iterations" / f"iter{k - 1:02d}.npz"
            with np.load(f) as z:
                push = np.asarray(z["push"], np.float64)
            s = scorer.score(push)
            diff = abs(s["eavail"]["recovery"] - it["push"]["aggregate"]["recovery"])
            if not diff <= TOL:
                raise SystemExit(f"{name}: E_avail R {s['eavail']['recovery']} differs from the "
                                 f"committed {it['push']['aggregate']['recovery']} by {diff}")
            rec["pet"][design] = {"k": k, "eavail_R": s["eavail"]["recovery"],
                                  "eavail_R_by_region": s["eavail"]["recovery_by_region"],
                                  "eavail_residual_l1": s["eavail"]["residual_l1"],
                                  "eavail_injected_l1": s["eavail"]["injected_l1"],
                                  "joint_p_R": s["topology"]["joint_eavail_p"]["recovery"],
                                  "joint_n_R": s["topology"]["joint_eavail_n"]["recovery"],
                                  "committed_eavail_R_abs_diff": diff,
                                  "iteration_file_sha256": it["file_sha256"]}
        for ts in ("truth4_species", "truth4"):
            for k in GBDT_K:
                sel_rows = sorted((r for r in rows if r["selection"] == sel and r["case"] == case
                                   and r["method"] == "omnifold"
                                   and r["miss"] == "efficiency_corrected"
                                   and r["truth_set"] == ts and r["k"] == k),
                                  key=lambda r: r["seed"])
                rec["gbdt"][f"{ts}@k{k}"] = {
                    "seeds": [r["seed"] for r in sel_rows],
                    "eavail_R": [r["R"] for r in sel_rows],
                    "joint_p_R": [r["R_joint_p"] for r in sel_rows],
                    "joint_n_R": [r["R_joint_n"] for r in sel_rows]}
        units.append(rec)
    doc = {"schema": "pet-gbdt-comparison/dev-paired/1", "pet_source": src["commit"],
           "pet_files_loaded": pgc_source.loaded_files(a.pet_source), "units": units,
           "note": "PET re-scored with the matched study's scorer; GBDT = committed task rows; "
                   "two draws per case; descriptive"}
    a.out.write_text(json.dumps(doc, indent=1) + "\n")
    for u in units:
        g = u["gbdt"]["truth4_species@k7"]
        print(u["selection"], u["case"],
              {d: round(v["eavail_R"], 3) for d, v in u["pet"].items()},
              "GBDT k7 sp", [round(x, 3) for x in g["eavail_R"]],
              "jointp PET", {d: round(v["joint_p_R"] or 0, 3) for d, v in u["pet"].items()},
              "GBDT", [round(x or 0, 3) for x in g["joint_p_R"]])
    return 0


if __name__ == "__main__":
    sys.exit(main())

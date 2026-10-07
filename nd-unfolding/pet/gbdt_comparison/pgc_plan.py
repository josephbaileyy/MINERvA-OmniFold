"""Write the frozen task list of the final-bank GBDT fill-in (`PLAN-20261005.md` section 4).

    pgc_plan.py --pet-source <bc356b0c checkout> --out tasks.json

Tasks are the look-1 PET runs of H2S1T24K5 (whose `replicate_arrays.npz` every design of the same
stage x draw x case shares; refused otherwise), in the declared execution order. The order is part
of the plan: it decides what is complete if the CPU budget stop fires.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

SCORED_FB = "nd-unfolding/pet/final_design/results/final/scored_fb"
ARRAY_SOURCE_DESIGN = "H2S1T24K5"
DESIGNS = ("H2S1T24K5", "L128S1T24K4", "CTLrefK3", "CrefK3")

# (stage, run-name case suffix or None for the stage's development tilt, draws)
TIER1_BLOCKS = [
    ("E0", "S4F", None, range(0, 30)),
    ("E4", "S4S", "D4c_p_up", range(0, 20)),
    ("E3", "S4F", "D1_m0.350", range(0, 30)),
    ("E5", "S4S", "D3_p0.35", range(0, 20)),
    ("E0", "S4F", None, range(30, 60)),
    ("E4", "S4S", "D4c_p_up", range(20, 40)),
    ("E3", "S4F", "D1_m0.350", range(30, 60)),
    ("E5", "S4S", "D3_p0.35", range(20, 40)),
]
TIER2_CASES = ["null", "D4d_n_down", "D1_p0.350", "R1_x1.05_D1_p0.350", "R1_x0.95_D1_p0.350"]
TIER3_CASES = ["D4d_n_up", "D5_nuwro", "D5_gibuu", "D2_bump_c0.3", "D4c_p_down",
               "D1_p0.350XD4c_p_up", "D3_m0.35", "D4a_pipm_up", "D4b_pi0_up", "D1_m0.700",
               "D1_p0.175", "D2_bump_c1.0", "D5p_nuwro", "R2_x1.01_D1_p0.350"]
LIBRARY_DRAWS = range(0, 8)


def run_name(stage: str, fb: int, case: str | None, design: str = ARRAY_SOURCE_DESIGN) -> str:
    return f"{stage}-{design}-FB{fb}" + (f"-{case}" if case else "")


def tasks() -> list[dict]:
    out = []
    for group, stage, case, draws in TIER1_BLOCKS:
        out += [{"tier": 1, "group": group, "run": run_name(stage, r, case), "seed": 1 + r}
                for r in draws]
    for tier, cases in ((2, TIER2_CASES), (3, TIER3_CASES)):
        for case in cases:
            out += [{"tier": tier, "group": case, "run": run_name("S4S", r, case), "seed": 1 + r}
                    for r in LIBRARY_DRAWS]
    return out


def check_shared_arrays(pet_source: Path, task_list: list[dict]) -> dict[str, str]:
    """Every design's committed score of the same stage x draw x case names the same
    `replicate_arrays.npz` digest; returns {run: digest}."""
    scored = pet_source / SCORED_FB
    digests: dict[str, str] = {}
    problems = []
    for t in task_list:
        seen = defaultdict(list)
        for d in DESIGNS:
            f = scored / f"{t['run'].replace(ARRAY_SOURCE_DESIGN, d)}.design_scores.json"
            if not f.exists():
                continue
            doc = json.loads(f.read_text())
            seen[doc["provenance"]["replicate_arrays_sha256"]].append(d)
        if ARRAY_SOURCE_DESIGN not in sum(seen.values(), []) or len(seen) != 1:
            problems.append((t["run"], dict(seen)))
            continue
        digests[t["run"]] = next(iter(seen))
    if problems:
        raise SystemExit(f"designs do not share replicate arrays: {problems[:3]}")
    return digests


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pet-source", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    tl = tasks()
    if len({t["run"] for t in tl}) != len(tl):
        raise SystemExit("duplicate task")
    digests = check_shared_arrays(a.pet_source, tl)
    for t in tl:
        t["replicate_arrays_sha256"] = digests[t["run"]]
    a.out.write_text(json.dumps({"schema": "pet-gbdt-comparison/tasks/1",
                                 "plan": "nd-unfolding/pet/gbdt_comparison/PLAN-20261005.md",
                                 "n": len(tl), "tasks": tl}, indent=1) + "\n")
    print(f"{len(tl)} tasks -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

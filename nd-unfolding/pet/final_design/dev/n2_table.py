"""Development N2 table (S-N2 screen, Amendment 3b): the estimator-seed sd of R_E0 at fixed events for
each design at a given k, from the S3P seed runs (DEV draws 0-1, estimator seeds: base, -s1, -s2, -s3;
the same seeds for every design). The number is `decide.Rules.N2`'s pooled within-draw sd (no second
implementation). Development evidence only.

    python n2_table.py --scores <dir of S3P *.design_scores.json> --designs H2S1:5 L128S1:5 H2S1E16:4 \
        --out n2.json
Run names: S3P-<CID>K<run K>-DEV<r>[-s<t>]; each score file must contain the requested k.

results/s3p/ left main on 2026-10-07 (family A3) and is at evidence/simplification-2026-10-07-fc97eaf9;
results/s3n/ stays. See results/README.md.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "analysis"))
import decide  # noqa: E402

NAME = re.compile(r"^S3P-(?P<cid>[A-Za-z0-9]+?)K(?P<k>\d+)-DEV(?P<rep>[01])(?:-s(?P<seed>\d+))?$")


def seed_runs(scores: Path, cid: str) -> list[dict]:
    out = []
    for f in sorted(scores.glob(f"S3P-{cid}K*-DEV*.design_scores.json")):
        m = NAME.match(f.name[: -len(".design_scores.json")])
        if m and m["cid"] == cid:
            out.append({"score": str(f), "replicate": f"DEV{m['rep']}", "seed": m["seed"] or "0"})
    return out


def n2(scores: Path, cid: str, k: int) -> dict:
    runs = seed_runs(scores, cid)
    c = decide.Candidate(cid, {"k": k, "runs": [], "seed_runs": runs})
    rules = decide.Rules({"decision_set": [cid], "n_final": 1, "n_stress": 1}, {})
    v = rules.N2(c).as_dict()
    return {"k": k, "n_seed_runs": len(c.seed_runs), "problems": c.problems,
            "verdict": v["verdict"], "pooled_within_draw_sd": v["numbers"].get("pooled_within_draw_sd"),
            "draws": v["numbers"].get("draws")}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scores", type=Path, required=True)
    ap.add_argument("--designs", nargs="+", required=True, help="CID:k")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    res = {}
    for d in a.designs:
        cid, k = d.split(":")
        res[cid] = n2(a.scores, cid, int(k))
        print(cid, k, res[cid]["verdict"], res[cid]["pooled_within_draw_sd"], res[cid]["n_seed_runs"])
    a.out.write_text(json.dumps(res, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

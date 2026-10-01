"""Assemble the `decide.py` evidence file from the frozen declaration and the scored runs (after UNBLIND).

Inputs: the frozen declaration (`freeze/EVIDENCE_DECLARATION-*.json`: decision set, anchors, m, looks, n_final,
n_stress, n_required, library), directories of `*.design_scores.json` for the FINAL (S4F) and library (S4S)
stages, the N2 seed runs, the cost file (`cost_from_receipts.py`) and optional coverage files. Draw cuts are the
declaration's: FINAL draws < n_final (per look: look L uses draws < L x n_final), library draws < n_stress, and the
cases in n_required (D4c up, D3 +0.35) draws < n_required[case] (Amendments 3e/3f: only the first N draws in draw
order enter). Rows beyond a cut are listed under `unused` and never enter the evidence.

    python build_evidence.py --declaration ../freeze/EVIDENCE_DECLARATION-20260927.json \
        --scores <S4F dir> <S4S dir> --seed-runs H2S1T24K5='<dir>/S3P-H2S1T24K5-DEV*' \
        L128S1T24K4='<dir>/S3P-L128S1T24K5-DEV*' --cost cost.json [--coverage NAME=path ...] \
        [--look 1] --out evidence.json
Candidate names are `<CID>K<k>` (e.g. H2S1T24K5); run names `<STAGE>-<CID>K<k>-FB<r>[-<case>][-b<m>]`.
"""
from __future__ import annotations

import argparse
import glob
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from score_design import canonical_case, classify_case  # noqa: E402

RUN = re.compile(r"^(?P<stage>S4F|S4S)-(?P<cand>[A-Za-z0-9]+K\d+)-FB(?P<rep>\d+)(?P<rest>.*)$")
SEED = re.compile(r"-DEV(?P<rep>\d+)(?:-s(?P<seed>\d+))?\.design_scores\.json$")


def case_of(doc: Mapping[str, Any]) -> str:
    return canonical_case(doc["case"]["case"])


def collect(decl: Mapping[str, Any], score_dirs: list[Path], look: int) -> tuple[dict, list]:
    n_final, n_stress = int(decl["n_final"]) * look, int(decl["n_stress"])
    n_req = {canonical_case(k): int(v) for k, v in decl.get("n_required", {}).items()}
    names = set(decl["decision_set"]) | set(decl.get("anchors", []))
    runs: dict[str, list] = {n: [] for n in names}
    unused = []
    for d in score_dirs:
        for f in sorted(Path(d).glob("*.design_scores.json")):
            m = RUN.match(f.name[: -len(".design_scores.json")])
            if not m or m["cand"] not in names:
                continue
            doc = json.loads(f.read_text())
            case, rep, stage = case_of(doc), int(m["rep"]), m["stage"]
            if "-b" in m["rest"]:
                continue                      # coverage members are not FINAL/library evidence
            limit = n_final if stage == "S4F" else n_req.get(case, n_stress)
            entry = {"score": str(f), "replicate": f"FB{rep}", "stage": stage}
            if rep >= limit:
                unused.append({**entry, "case": case, "limit": limit})
                continue
            runs[m["cand"]].append(entry)
    return runs, unused


def seed_runs(pattern: str) -> list[dict]:
    out = []
    for f in sorted(glob.glob(pattern if pattern.endswith(".json") else pattern + ".design_scores.json")):
        m = SEED.search(f)
        if m:
            out.append({"score": f, "replicate": f"DEV{m['rep']}", "seed": m["seed"] or "0"})
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--declaration", type=Path, required=True)
    ap.add_argument("--scores", type=Path, nargs="+", required=True)
    ap.add_argument("--seed-runs", nargs="*", default=[], metavar="NAME=GLOB")
    ap.add_argument("--cost", type=Path, default=None, help="cost_from_receipts.py output")
    ap.add_argument("--coverage", nargs="*", default=[], metavar="NAME=PATH")
    ap.add_argument("--look", type=int, default=1)
    ap.add_argument("--previous", type=Path, default=None, help="look-1 decision file (look 2)")
    ap.add_argument("--provisional", action="store_true")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    decl = json.loads(a.declaration.read_text())
    for case in decl.get("library", []):
        classify_case(case)
    runs, unused = collect(decl, a.scores, a.look)
    seeds = dict(x.split("=", 1) for x in a.seed_runs)
    cov = dict(x.split("=", 1) for x in a.coverage)
    cost = json.loads(a.cost.read_text())["candidates"] if a.cost else {}
    cands = {}
    for name, rr in runs.items():
        k = int(re.search(r"K(\d+)$", name).group(1))
        cid = name[: name.rindex("K")]
        d: dict[str, Any] = {"k": k, "runs": rr, "provenance_complete": True}
        if name in seeds:
            d["seed_runs"] = seed_runs(seeds[name])
        c = cost.get(cid) or cost.get(name)
        if c and c.get("evidence_cost"):
            d["cost"] = c["evidence_cost"]
        if name in cov:
            d["coverage"] = cov[name]
        cands[name] = d
    ev = {k: v for k, v in decl.items() if k not in ("note", "candidates")}
    ev.update({"look": a.look, "candidates": cands, "unused_rows": unused,
               "built_by": "analysis/build_evidence.py"})
    if a.previous:
        ev["previous"] = str(a.previous)
    if a.provisional:
        ev["provisional"] = True
    a.out.write_text(json.dumps(ev, indent=1) + "\n")
    for n, d in cands.items():
        print(f"{n}: {len(d['runs'])} runs, {len(d.get('seed_runs', []))} seed runs, "
              f"cost {'yes' if 'cost' in d else 'no'}, coverage {'yes' if 'coverage' in d else 'no'}")
    print(f"unused rows (beyond the declared cuts): {len(unused)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

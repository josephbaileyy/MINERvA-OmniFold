"""Sizing-pilot input for `sizing.py` from the S3P pilot's scored runs (PROTOCOL-20260925 section 8,
Amendment 2c item 6). DEV evidence only: the pilot's observations never enter the final.

Reads `*.design_scores.json` (score_design.py) of the S3P runs, loads each finalist with
`decide.Candidate` at its frozen K and forms the declared contrasts with `decide.paired_diff` and
`decide.NI_MARGINS` (no second implementation of the endpoint getters or margins):

* FINAL (sizes n_F): the section-6.5 non-inferiority contrasts small - large on E0, the moderate and
  good regions and E3, and U1 (R_E0 against the historical floor) for every finalist;
* library (sizes the E4/E5 cases' draw count): the non-inferiority contrasts on E4 and E5, and U4/U5
  (LB > 0.10) for every finalist.

Seed-variant runs (`-s<tag>`, the N2 estimator-seed runs) are excluded from the contrasts.

    python build_pilot.py --scores <dir> --small H2S1:5 --large L128S1:5 --bonferroni-m 2 \
        --final-out pilot_final.json --library-out pilot_library.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import decide  # noqa: E402

NAME = re.compile(r"^S3P-(?P<cid>[A-Za-z0-9]+)K(?P<k>\d+)-DEV(?P<rep>\d+)(?P<rest>.*)$")
FINAL_NI = ("E0", "moderate", "good", "E3")
U_LB_FLOOR = 0.10              # section 6.1 U4/U5: LB > 0.10
LIBRARY_NI = ("E4", "E5")


def candidate(scores: Path, cid: str, k: int) -> decide.Candidate:
    runs = []
    for f in sorted(scores.glob("S3P-*.design_scores.json")):
        m = NAME.match(f.name[: -len(".design_scores.json")])
        if not m or m["cid"] != cid or int(m["k"]) != k or re.search(r"-s\w+$", m["rest"]):
            continue
        runs.append({"score": str(f), "replicate": m["rep"], "stage": "S3P"})
    if not runs:
        raise SystemExit(f"no S3P runs for {cid} K={k} under {scores}")
    c = decide.Candidate(cid, {"k": k, "runs": runs})
    if c.problems:
        raise SystemExit(f"{cid}: " + "; ".join(c.problems))
    return c


def contrast(small, large, ep: str) -> dict:
    d = decide.paired_diff(small, large, ep)
    return {"id": f"6.5 {ep} ({small.name} - {large.name})", "values": d["diff"].tolist(),
            "replicates": d["replicates"], "margin": decide.NI_MARGINS[ep], "kind": "ni"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scores", type=Path, required=True)
    ap.add_argument("--small", required=True, help="ID:K")
    ap.add_argument("--large", required=True, help="ID:K")
    ap.add_argument("--bonferroni-m", type=int, required=True)
    ap.add_argument("--looks-planned", type=int, default=2)
    ap.add_argument("--final-out", type=Path, required=True)
    ap.add_argument("--library-out", type=Path, required=True)
    a = ap.parse_args(argv)
    (sid, sk), (lid, lk) = (x.split(":") for x in (a.small, a.large))
    small, large = candidate(a.scores, sid, int(sk)), candidate(a.scores, lid, int(lk))
    head = {"bonferroni_m": a.bonferroni_m, "looks_planned": a.looks_planned,
            "source": "S3P pilot (DEV bank), analysis/build_pilot.py"}
    final = [contrast(small, large, ep) for ep in FINAL_NI]
    case, getter = decide.ENDPOINT_GETTERS["E0"]
    for c in (small, large):
        v = c.values(case, getter)
        final.append({"id": f"U1 {c.name}", "values": [v[r] for r in sorted(v)],
                      "replicates": sorted(v), "margin": decide.PROTOCOL_U1_FLOOR, "kind": "level"})
    library = [contrast(small, large, ep) for ep in LIBRARY_NI]
    for rule, ep in (("U4", "E4"), ("U5", "E5")):
        case, getter = decide.ENDPOINT_GETTERS[ep]
        for c in (small, large):
            v = c.values(case, getter)
            library.append({"id": f"{rule} {c.name}", "values": [v[r] for r in sorted(v)],
                            "replicates": sorted(v), "margin": U_LB_FLOOR, "kind": "level"})
    a.final_out.write_text(json.dumps({**head, "contrasts": final}, indent=1) + "\n")
    a.library_out.write_text(json.dumps({**head, "contrasts": library}, indent=1) + "\n")
    for c in final + library:
        print(f"{c['id']}: n={len(c['values'])} reps={c['replicates']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

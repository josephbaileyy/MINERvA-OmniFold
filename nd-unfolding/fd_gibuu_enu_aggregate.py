#!/usr/bin/env python3
"""The p_parallel > 4.5 GeV/c aggregate of the GiBUU E_nu coverage readout, for FD-DIRECTOR-RULINGS.md section 5
(state/measurement-paper/5d-community-20261024/): from nd-unfolding/pv-ladder/readouts/gibuu_enu_coverage.json
(H2-DEFINITION-ADDENDUM-GIBUU-DOMAIN.md section 1), pinned by digest, for each of GENIE CV and NuWro:
* the share of the in-phase-space cross section at p_parallel 4.5-60, the sum of by_pz[].share_of_in_ps over the
  four bands above 4.5;
* the share of that from E_nu > 20 GeV, sum(share_of_in_ps * share_E_gt_20) over the same bands, divided by it;
* the 1.5-4.5 band's share_of_in_ps and share_E_gt_20, copied.
These are GENIE CV's and NuWro's shares, which GiBUU 2019's sample, stopping at E_nu = 20 GeV, cannot hold. None is a
GiBUU number.

Controls C0-C3 each refuse (exit 1, nothing written): the digest, schema and cut (C0); the bands tile 1.5-60 with 4.5
an edge (C1); each generator's shares sum to 1 and its band counts to n_in_ps (C2); the bands' E_nu > 20 GeV shares
recombine to share_E_gt_20_all_in_ps (C3).

MEASURES: nothing; arithmetic on one committed readout. CANNOT AUTHORIZE: a reading, a claim or any printed wording.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

_ND = Path(__file__).resolve().parent
REPO = _ND.parent
READOUT = "nd-unfolding/pv-ladder/readouts/gibuu_enu_coverage.json"
OUT = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/readout/fd_gibuu_enu_aggregate.json"
PIN = "9ee26883e32e85cd72e083022ef4c42440370665b17bdec0c272596f9650813c"
SCHEMA_IN = "gibuu-enu-coverage/1"
SCHEMA = "fd-gibuu-enu-aggregate/1"
E_CUT = 20.0
GENERATORS = ("genie_cv", "nuwro")
LOW, SPLIT, HIGH = 1.5, 4.5, 60.0
TOL = 1e-12
LABELS = {
    "what": "GENIE CV's and NuWro's share of the in-phase-space cross section from E_nu > 20 GeV, at p_parallel "
            "1.5-4.5 and over 4.5-60 GeV/c, the share GiBUU 2019's sample, which stops at E_nu = 20 GeV "
            "(KNOWN_ISSUES 82), cannot hold",
    "not": "not a GiBUU number: each share is the named generator's, from its own events up to its generation range",
    "source": "nd-unfolding/pv-ladder/readouts/gibuu_enu_coverage.json, generators.<g>.by_pz[].share_of_in_ps and "
              "share_E_gt_20 (H2-DEFINITION-ADDENDUM-GIBUU-DOMAIN.md section 1)",
    "for": "state/measurement-paper/5d-community-20261024/FD-DIRECTOR-RULINGS.md section 5 (GiBUU on the eight "
           "p_parallel < 4.5 cells)",
    "formula": "share_of_in_ps(4.5-60) = sum_b share_of_in_ps[b]; share_E_gt_20(4.5-60) = sum_b share_of_in_ps[b] * "
               "share_E_gt_20[b] / share_of_in_ps(4.5-60), over the by_pz bands b with pz[0] >= 4.5",
    "cannot_authorize": "a reading, a claim, a caption or any printed wording; these are Joseph's",
}


class Stop(Exception):
    pass


def check(control: str, name: str, ok: bool, why: str = "differs") -> None:
    print(f"{control} {'PASS' if ok else 'FAIL'}: {name}" + ("" if ok else f" ({why})"), flush=True)
    if not ok:
        raise Stop(f"{control}: {name}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path, pin: str) -> dict:
    got = sha256(path)
    check("C0", "readout sha256 is the pin", got == pin, f"{got} != {pin}")
    r = json.loads(path.read_text())
    check("C0", f"schema {SCHEMA_IN}", r.get("schema") == SCHEMA_IN, repr(r.get("schema")))
    check("C0", f"e_cut_gev {E_CUT}", r.get("e_cut_gev") == E_CUT, repr(r.get("e_cut_gev")))
    check("C0", "generators", sorted(r.get("generators", {})) == sorted(GENERATORS), repr(sorted(r.get("generators", {}))))
    return r


def aggregate(name: str, g: dict) -> dict:
    bands = g["by_pz"]
    edges = [b["pz"] for b in bands]
    tiles = (edges[0][0] == LOW and edges[-1][1] == HIGH
             and all(a[1] == b[0] for a, b in zip(edges, edges[1:])) and all(a < b for a, b in edges))
    check("C1", f"{name}: bands tile {LOW}-{HIGH}", tiles, repr(edges))
    check("C1", f"{name}: {SPLIT} is an edge and 1.5-4.5 is one band", edges[0] == [LOW, SPLIT], repr(edges[0]))
    total = sum(b["share_of_in_ps"] for b in bands)
    check("C2", f"{name}: share_of_in_ps sums to 1", abs(total - 1) <= TOL, repr(total))
    n = sum(b["n_events"] for b in bands)
    check("C2", f"{name}: n_events sum to n_in_ps", n == g["n_in_ps"], f"{n} != {g['n_in_ps']}")
    above = sum(b["share_of_in_ps"] * b["share_E_gt_20"] for b in bands)
    check("C3", f"{name}: bands recombine to share_E_gt_20_all_in_ps",
          abs(above - g["share_E_gt_20_all_in_ps"]) <= TOL, f"{above} != {g['share_E_gt_20_all_in_ps']}")
    hi = [i for i, b in enumerate(bands) if b["pz"][0] >= SPLIT]
    s_hi = sum(bands[i]["share_of_in_ps"] for i in hi)
    e_hi = sum(bands[i]["share_of_in_ps"] * bands[i]["share_E_gt_20"] for i in hi) / s_hi
    key = f"generators.{name}.by_pz"
    return {
        "generation_range_gev": g["generation_range_gev"],
        "pz_1.5_4.5": {"share_of_in_ps": bands[0]["share_of_in_ps"], "share_E_gt_20": bands[0]["share_E_gt_20"],
                       "keys": [f"{key}[0].share_of_in_ps", f"{key}[0].share_E_gt_20"]},
        "pz_4.5_60": {"share_of_in_ps": s_hi, "share_E_gt_20": e_hi, "bands": [bands[i]["pz"] for i in hi],
                      "keys": [f"{key}[{i}].{k}" for i in hi for k in ("share_of_in_ps", "share_E_gt_20")]},
    }


def build_args(argv):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--readout", type=Path, default=REPO / READOUT)
    p.add_argument("--out", type=Path, default=REPO / OUT)
    return p.parse_args(argv)


def run(a, pin: str = PIN) -> int:
    try:
        r = load(a.readout, pin)
        gens = {n: aggregate(n, r["generators"][n]) for n in GENERATORS}
    except Stop as e:
        print(f"REFUSED: {e}; nothing written", file=sys.stderr, flush=True)
        return 1
    out = {"schema": SCHEMA, "labels": LABELS, "e_cut_gev": E_CUT,
           "inputs_sha256": {"gibuu_enu_coverage": pin},
           "code_sha256": {"fd_gibuu_enu_aggregate.py": sha256(Path(__file__).resolve())},
           "generators": gens}
    a.out.write_text(json.dumps(out, indent=1, allow_nan=False) + "\n")
    print(json.dumps({"wrote": str(a.out), "sha256": sha256(a.out)}), flush=True)
    return 0


def main(argv=None) -> int:
    return run(build_args(argv))


if __name__ == "__main__":
    sys.exit(main())

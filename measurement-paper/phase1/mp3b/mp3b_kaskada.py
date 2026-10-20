#!/usr/bin/env python3
"""MP3-B kaskada_on check (director's ruling 2): collect compare_kaskada.C outputs and apply the declared rule.

  RULE: if every comparable pair is RNG-aligned and every event completed under kaskada_on = 1 has an identical
  final state under kaskada_on = 0 (same particles, four-momenta within TOL), kaskada_on = 0 is the PRIMARY H
  sample and (A) with kaskada_on = 1 is reported beside it, flagged. If any pair differs, (A) with kaskada_on = 1
  stays primary and the differences are reported. A misaligned pair cannot be compared and is reported as such;
  the switch condition is then not met (nothing shown identical), so kaskada_on = 1 stays primary.

Usage: python3 mp3b_kaskada.py --compare-dir GEN/compare --out OUT.json
"""
import argparse
import json
from pathlib import Path


def parse(path: Path) -> dict:
    d = {"file": str(path), "pdg_shift": {}, "pdg_fewer_in_k1": {}, "pdg_more_in_k1": {}, "examples": []}
    for line in path.read_text().splitlines():
        p = line.split()
        if not p:
            continue
        if p[0] == "NO_COMPARISON":
            d["no_comparison"] = " ".join(p[1:])
        elif p[0] == "PDG_SHIFT":
            d["pdg_shift"][p[1]] = {"n_particles": int(p[2]), "mean_dE_k1_minus_k0_MeV": float(p[3]),
                                    "max_abs_dE_MeV": float(p[4]), "max_abs_dp_MeV": float(p[5]) if len(p) > 5 else None}
        elif p[0] in ("PDG_FEWER_IN_K1", "PDG_MORE_IN_K1"):
            d[p[0].lower()][p[1]] = int(p[2])
        elif p[0] == "EXAMPLE":
            d["examples"].append(int(p[1]))
        elif p[0].startswith("FILE_"):
            d[p[0].lower()] = p[1]
        elif len(p) == 2:
            try:
                d[p[0].lower()] = float(p[1]) if "." in p[1] or "e" in p[1].lower() else int(p[1])
            except ValueError:
                d[p[0].lower()] = p[1]
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--compare-dir", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    pairs = {f.stem: parse(f) for f in sorted(a.compare_dir.glob("*.txt"))}
    comp = {k: v for k, v in pairs.items() if "no_comparison" not in v}
    aligned = {k: v.get("rng_aligned") == 1 for k, v in comp.items()}
    ident = {k: aligned[k] and v.get("n_post_within_tol") == v.get("n_compared") and v.get("n_k1") == v.get("n_k0")
             for k, v in comp.items()}
    tot = lambda key: sum(int(v.get(key, 0)) for v in comp.values())  # noqa: E731
    out = {"rule": __doc__.split("RULE:")[1].split("Usage")[0].strip(),
           "n_pairs_compared": len(comp), "pairs_without_comparison": {k: v["no_comparison"] for k, v in pairs.items()
                                                                      if "no_comparison" in v},
           "n_pairs_misaligned": sum(not x for x in aligned.values()),
           "misaligned_pairs": [k for k, x in aligned.items() if not x],
           "events_compared": tot("n_compared"), "events_post_exact": tot("n_post_exact"),
           "events_post_within_tol": tot("n_post_within_tol"),
           "events_post_momentum_different": tot("n_post_momentum_different"),
           "events_post_content_different": tot("n_post_content_different"),
           "max_post_abs_diff_MeV": max([float(v.get("max_post_abs_diff_mev", 0)) for v in comp.values()] or [0.0]),
           "identical_on_every_completed_event": bool(comp) and all(ident.values()) and not out_missing(pairs),
           "pairs": pairs}
    agg_shift, fewer, more = {}, {}, {}
    for v in comp.values():
        for g, s in v["pdg_shift"].items():
            t = agg_shift.setdefault(g, {"n_particles": 0, "sum_dE": 0.0, "max_abs_dE_MeV": 0.0, "max_abs_dp_MeV": 0.0})
            t["n_particles"] += s["n_particles"]
            t["max_abs_dp_MeV"] = max(t["max_abs_dp_MeV"], s["max_abs_dp_MeV"] or 0.0)
            t["sum_dE"] += s["mean_dE_k1_minus_k0_MeV"] * s["n_particles"]
            t["max_abs_dE_MeV"] = max(t["max_abs_dE_MeV"], s["max_abs_dE_MeV"])
        for g, c in v["pdg_fewer_in_k1"].items():
            fewer[g] = fewer.get(g, 0) + c
        for g, c in v["pdg_more_in_k1"].items():
            more[g] = more.get(g, 0) + c
    for t in agg_shift.values():
        t["mean_dE_k1_minus_k0_MeV"] = t.pop("sum_dE") / t["n_particles"]
    out.update(pdg_shift_aggregate=agg_shift, events_with_fewer_of_pdg_in_k1=fewer, events_with_more_of_pdg_in_k1=more)
    out["PRIMARY_H_SAMPLE"] = "k0 (kaskada_on = 0)" if out["identical_on_every_completed_event"] else "k1 (kaskada_on = 1, run A)"
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    print("KASKADA", json.dumps({k: out[k] for k in out if k not in ("pairs", "rule")}))


def out_missing(pairs) -> bool:
    """A completed k1 chunk without a comparison (e.g. its seed aborted under k0) means 'not shown identical'."""
    return any("no_comparison" in v and not v["no_comparison"].startswith("k1_dropped") for v in pairs.values())


if __name__ == "__main__":
    main()

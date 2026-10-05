"""The `coverage.py` spec for one finalist from its released coverage manifests and their scored members
(PROTOCOL-20260925 section 9, Amendments 5 and 5b).

Each manifest row is one bootstrap member `S5-<CID>K<k>-FB<r>[-D4c_p_up]-b<m>`; its scores are
`<scores dir>/<row>.design_scores.json` (`jobs/score_cov.sh`). Members are grouped by replicate r; every replicate must
carry exactly the B members the manifest lists, and every listed member must be scored (fail closed: no replicate is
dropped silently). The development-tilt manifest feeds C1-C4 ("dev"), the D4c-up manifest C5 ("d4c"); either may be
omitted while its group is still blinded.

    python coverage_spec.py --candidate H2S1T24K5 --dev ../runs/s5c_a5_H2S1T24.tsv <scores dir> \
        [--d4c ../runs/s5d_a5_H2S1T24.tsv <scores dir>] --out coverage_spec.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROW = re.compile(r"^S5-(?P<cand>[A-Za-z0-9]+K\d+)-FB(?P<rep>\d+)(?P<case>-D4c_p_up)?-b(?P<m>\d+)$")
B_MEMBERS = 6


def group(manifest: Path, scores: Path, candidate: str, d4c: bool) -> list[dict]:
    reps: dict[int, dict[int, Path]] = {}
    for line in manifest.read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        name = line.split("\t")[0]
        m = ROW.match(name)
        if not m or m["cand"] != candidate or bool(m["case"]) != d4c:
            raise SystemExit(f"{manifest.name}: row {name} is not a {'D4c' if d4c else 'dev-tilt'} member of {candidate}")
        f = scores / f"{name}.design_scores.json"
        if not f.exists():
            raise SystemExit(f"{name}: not scored ({f} missing)")
        reps.setdefault(int(m["rep"]), {})[int(m["m"])] = f
    out = []
    for r in sorted(reps):
        if sorted(reps[r]) != list(range(1, B_MEMBERS + 1)):
            raise SystemExit(f"replicate FB{r}: members {sorted(reps[r])}, want 1..{B_MEMBERS}")
        out.append({"replicate": f"FB{r}", "members": [str(reps[r][b]) for b in range(1, B_MEMBERS + 1)]})
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--candidate", required=True, help="e.g. H2S1T24K5")
    ap.add_argument("--dev", nargs=2, type=Path, metavar=("MANIFEST", "SCORES"))
    ap.add_argument("--d4c", nargs=2, type=Path, metavar=("MANIFEST", "SCORES"))
    ap.add_argument("--bonferroni-m", type=int, default=2, help="C rules keep m = 2 (Amendment 3a item 5)")
    ap.add_argument("--look", type=int, default=1)
    ap.add_argument("--previous", type=Path, default=None, help="look-1 coverage output (look 2 only)")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if not (a.dev or a.d4c):
        ap.error("give --dev and/or --d4c")
    k = int(re.search(r"K(\d+)$", a.candidate).group(1))
    spec = {"candidate": a.candidate, "k": k, "bonferroni_m": a.bonferroni_m, "look": a.look, "looks_planned": 2,
            "B": B_MEMBERS, "dev": group(*a.dev, a.candidate, False) if a.dev else [],
            "d4c": group(*a.d4c, a.candidate, True) if a.d4c else []}
    if a.previous:
        spec["previous"] = str(a.previous)
    a.out.write_text(json.dumps(spec, indent=1) + "\n")
    print(f"{a.candidate} k={k}: {len(spec['dev'])} dev-tilt and {len(spec['d4c'])} D4c replicates "
          f"x {B_MEMBERS} members -> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

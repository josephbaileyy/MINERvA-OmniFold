"""Test C positive controls P1-P3 (DECLARATION.md) on outputs fetched from scratch.

    python3 controls.py <fetched dir> [playlist ...]

<fetched dir> holds <pl>_MC.csv.gz, <pl>_MC.log, <pl>_truth.csv.gz and <pl>_truth.log as
written by run.sh. With no playlist list, all 12 are required. On a pass for every
requested playlist, writes inputs/enu/<pl>.csv.gz (the true_enu column only),
inputs/truth/<pl>.csv.gz (a copy) and inputs/fetched.sha256. Always writes controls.json
and prints the report. Exits 1 if any control fails.
"""

import gzip
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SAVED = HERE.parent / "inputs" / "events"
REPLAY = np.load(HERE.parent / "inputs" / "replay" / "playlists.npz")
ALL = ["1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P"]
TOL, MIN_GEN, MAX_BELOW = 1e-3, 100, 1e-4


def lines(path):
    with gzip.open(path, "rt") as f:
        return f.read().splitlines()


def p1(fetched, pl):
    new, old = lines(fetched / f"{pl}_MC.csv.gz"), lines(SAVED / f"{pl}_MC.csv.gz")
    head_ok = new[0] == old[0] + ",true_enu"
    stripped = [ln.rsplit(",", 1)[0] for ln in new]
    same = len(new) == len(old) and stripped[1:] == old[1:]
    first = next((i for i, (a, b) in enumerate(zip(stripped[1:], old[1:])) if a != b), None)
    return {"rows_new": len(new) - 1, "rows_saved": len(old) - 1, "header_ok": head_ok,
            "identical": bool(same and head_ok), "first_mismatch_row": first}


def p2(fetched, pl):
    t = pd.read_csv(fetched / f"{pl}_truth.csv.gz")
    g = t[t.cell < 224].groupby("cell")[["n", "sumw", "sumwdup"]].sum().reindex(range(224), fill_value=0)
    ref = REPLAY[f"{pl}_T"]
    big = g.n.to_numpy() >= MIN_GEN
    out = {"cells_checked": int(big.sum()), "outside_grid_sumw": float(t[t.cell == 224].sumw.sum()),
           "duplicate_entries": float(t.ndup.sum())}
    for name, v in (("with_duplicates", g.sumw.to_numpy()), ("deduplicated", (g.sumw - g.sumwdup).to_numpy())):
        rel = np.abs(v[big] / ref[big] - 1)
        out[name] = {"max_rel": float(rel.max()), "worst_cell": int(np.flatnonzero(big)[rel.argmax()]),
                     "total_rel": float(v.sum() / ref.sum() - 1), "pass": bool(rel.max() <= TOL)}
    return out


def p3(fetched, pl):
    log = (fetched / f"{pl}_truth.log").read_text()
    m = re.search(r"(\d+) signal, (\d+) duplicate keys, (\d+) with E_nu < E_mu", log)
    signal, below = (int(m.group(1)), int(m.group(3))) if m else (0, -1)
    r = pd.read_csv(fetched / f"{pl}_MC.csv.gz")
    fidcc = (r.pdg == 14) & (r.current == 1) & (r.fid == 1)
    bad = int((~np.isfinite(r.true_enu[fidcc]) | (r.true_enu[fidcc] <= 0)).sum())
    frac = below / signal if signal else float("nan")
    return {"signal": signal, "below_emu": below, "below_fraction": frac, "reco_fidcc_bad_enu": bad,
            "pass": bool(m and frac < MAX_BELOW and bad == 0)}


def main():
    fetched = Path(sys.argv[1])
    pls = sys.argv[2:] or ALL
    res = {"tolerance": TOL, "min_generated": MIN_GEN, "playlists": {}}
    for pl in pls:
        res["playlists"][pl] = {"P1": p1(fetched, pl), "P2": p2(fetched, pl), "P3": p3(fetched, pl)}
    ok1 = all(v["P1"]["identical"] for v in res["playlists"].values())
    ver = {k: all(v["P2"][k]["pass"] for v in res["playlists"].values()) for k in ("with_duplicates", "deduplicated")}
    ok3 = all(v["P3"]["pass"] for v in res["playlists"].values())
    version = "with_duplicates" if ver["with_duplicates"] else "deduplicated" if ver["deduplicated"] else None
    res["P1"] = {"pass": ok1}
    res["P2"] = {"pass_with_duplicates": ver["with_duplicates"], "pass_deduplicated": ver["deduplicated"], "version": version}
    res["P3"] = {"pass": ok3}
    res["all_pass"] = bool(ok1 and version and ok3 and set(pls) == set(ALL))
    for pl, v in res["playlists"].items():
        print(f"{pl}: P1 identical={v['P1']['identical']} rows {v['P1']['rows_new']}/{v['P1']['rows_saved']}"
              f" first mismatch {v['P1']['first_mismatch_row']}")
        for k in ("with_duplicates", "deduplicated"):
            q = v["P2"][k]
            print(f"    P2 {k}: max |rel| {q['max_rel']:.2e} (cell {q['worst_cell']}), total {q['total_rel']:+.2e}, pass={q['pass']}")
        print(f"    P2 cells checked {v['P2']['cells_checked']}, duplicate entries {v['P2']['duplicate_entries']:.0f}")
        q = v["P3"]
        print(f"    P3 E_nu<E_mu {q['below_emu']}/{q['signal']}, reco fid nu_mu CC bad E_nu {q['reco_fidcc_bad_enu']}, pass={q['pass']}")
    print(f"P1 {ok1}; P2 with duplicates {ver['with_duplicates']}, deduplicated {ver['deduplicated']} -> {version};"
          f" P3 {ok3}; all 12 playlists: {set(pls) == set(ALL)}")
    (HERE / "controls.json").write_text(json.dumps(res, indent=1))
    if not (ok1 and version and ok3):
        sys.exit(1)
    for d in ("enu", "truth"):
        (HERE / "inputs" / d).mkdir(parents=True, exist_ok=True)
    for pl in pls:
        e = pd.read_csv(fetched / f"{pl}_MC.csv.gz", usecols=["true_enu"])
        with gzip.GzipFile(HERE / "inputs" / "enu" / f"{pl}.csv.gz", "wb", mtime=0) as f:
            f.write(e.to_csv(index=False, float_format="%.15g").encode())
        shutil.copyfile(fetched / f"{pl}_truth.csv.gz", HERE / "inputs" / "truth" / f"{pl}.csv.gz")
    sums = [f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}" for p in sorted(fetched.iterdir()) if p.is_file()]
    (HERE / "inputs" / "fetched.sha256").write_text("\n".join(sums) + "\n")


if __name__ == "__main__":
    main()

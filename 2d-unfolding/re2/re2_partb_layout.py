#!/usr/bin/env python3
"""RE-2 part B: the production runs, their packing into jobs, and each job's projected charge and limit.

    re2_partb_layout.py --units run/j0_readout/units.json --runs-out run/partb_runs.tsv --jobs-out run/partb_jobs.tsv \
        --checks-out run/partb_checks.tsv

Every run repeats the argv of the purity product it replaces, as J0 did for its references (RE2-DECLARATION.md §3),
with ``--bkg-mode negweight-refined --refine-n-estimators 400 --refine-num-leaves 31`` in place of purity:

* J1: ``ER``, the refined CV that becomes ``E_R``; ``C0_cv``, the same unfold again (Stage C's C0 row and the
  seed-42 CV of the S4(ii) panel), so the adopted product has its own repeat; ``C0_unit``, the unit-factor bootstrap.
* J2: the 175 universes of the July sweep (``sweeps.json`` "pn/", less the 10 laterals, the 2 Rvp1pi and CV), with
  J0's universe argv (K1-U4-U6 reproduced the July files with it).
* J3: the 10 active laterals of Stage C S3.  J4: S1, bootstrap seeds 1-300, three streams.

Labels are Stage C's member names without ``2dc_P_`` (``S1_001``, ``S3_BeamAngleX0``, ``S4U_NormDISCC0_s42``), the
period test's (``pu_PA_b01``), and ``U_<band>_<index>`` for the July universes, so the post-processing copies change
only the directory they read.
* J6: S4(i), seeds 45/48/51/54 x bootstrap seeds 1-20.  J7: S4(ii), Stage C's 35 S4U and 4 S4CV rows.
* J8: the 37 period rows of the period-unfold test (its ``jobs.tsv``).

Each run's time is J0's measured maximum for its class (``units.json``). The period control, which J0 ran only in
the purity arm, is the purity control's time x the refined/purity ratio of the PA central. Runs are packed onto
the job's lanes longest first, into the lane with the least load. A J0 lane was busy 99.97 % or more of its span
(``RE2-DECLARATION-B.md`` §3), so a job's wall time is its preflight plus its longest lane, and an exclusive node
is charged for that wall time. The limit is 1.25 x the wall time, rounded up to a minute, and must be under 12 h.

MEASURES: nothing. CANNOT AUTHORIZE: a job (the director binds part B).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ST = REPO / "docs/orchestration/state/2d-closeout"
SWEEPS = (ST / "stageB/evidence/b-genie-truth/sweeps.json",
          "15b57de9124f204bf3cdf8cd0660c467783bf633bf0d45bfbd4e2506b19be2e4")
PERIOD_JOBS = (ST / "period-unfold-20261014/scripts/jobs.tsv",
               "c2283eb37343780b1b4d3754f8e5dc323480b102ddf9a9d0c13d858b237f5421")
LATERALS = [f"{b}_{i}" for b in ("BeamAngleX", "BeamAngleY", "MuonResolution", "Muon_Energy_MINERvA",
                                 "Muon_Energy_MINOS") for i in (0, 1)]
PANEL_U = ["NormDISCC:0", "Flux:23", "MaRES:0", "MaCCQE:0", "2p2h:0", "MinosEfficiency:0", "Muon_Energy_MINOS:0"]
PANEL_SEEDS = [42, 45, 48, 51, 54]
REFINED = "--bkg-mode negweight-refined --refine-n-estimators 400 --refine-num-leaves 31"
COMMON = "--mcfile $MC --iters 5 --use-weights --estimator lgbm"
PREFLIGHT_S = 300      # stat checks of the DTN-hashed inputs and the small pscratch digests (§4 of the declaration)
FACTOR = 1.25
MAX_LIMIT_S = 12 * 3600
# J0's packing fractions (RE2-J0-REPORT.md §5 F1): steps / charge, 64-CPU lanes (J0b) and 128-CPU lanes (J0a after
# its preflight). Printed beside each job's own projection, for comparison only.
J0_FRACTION = {64: 0.825, 128: 0.763}
# job -> (lane CPUs, number of jobs it is split into)
JOBS = {"J1": (64, 1), "J2": (128, 4), "J3": (128, 1), "J4": (64, 3), "J6": (64, 1), "J7": (128, 1), "J8": (64, 1)}
DIAGNOSTIC = {"J7"}


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def pinned(path_sha):
    path, want = path_sha
    if sha256(path) != want:
        raise RuntimeError(f"{path}: sha256 is not the pinned {want}")
    return path


def universes() -> list[str]:
    """The 175 July universes, as `--universe` values (band:index), in sorted sweeps.json order."""
    names = sorted(k[3:] for k in json.loads(pinned(SWEEPS).read_text()) if k.startswith("pn/"))
    out = []
    for n in names:
        band, idx = n.rsplit("_", 1) if n != "CV" else ("CV", "")
        if n == "CV" or n in LATERALS or band == "Rvp1pi":
            continue
        out.append(f"{band}:{idx}")
    if len(out) != 175:
        raise RuntimeError(f"{len(out)} universes, expected 175")
    return out


def tag(u: str) -> str:
    return u.replace(":", "_")


def runs(t: dict) -> list[dict]:
    uni = "--omnifile $UNI --flux-universe-file $FLUXU --verbose " + COMMON
    cv = "--omnifile $CV " + COMMON
    r = []

    def add(job, label, cpus, args, est):
        r.append({"job": job, "label": label, "cpus": cpus, "script": "re2", "args": f"{args} {REFINED}",
                  "est_s": est})

    add("J1", "ER", 64, f"{cv} --seed 42 --branch-select all", t["central"])
    add("J1", "C0_cv", 64, f"{cv} --seed 42 --branch-select all", t["central"])
    add("J1", "C0_unit", 64, f"{cv} --seed 42 --bootstrap-seed 1 --bootstrap-streams three --unit-factors",
        t["central"])
    for u in universes():
        add("J2", f"U_{tag(u)}", 128, f"{uni} --seed 42 --universe {u} --branch-select derived", t["universe"])
    for lat in LATERALS:
        add("J3", f"S3_{lat.replace('_', '')}", 128,
            f"--omnifile $ACT/runEventLoopOmniFold_5D_MEFHC_active_{lat}.root {COMMON} --seed 42 --branch-select all",
            t["lateral"])
    for n in range(1, 301):
        add("J4", f"S1_{n:03d}", 64, f"{cv} --seed 42 --bootstrap-seed {n} --bootstrap-streams three", t["replica"])
    for s in PANEL_SEEDS[1:]:
        for n in range(1, 21):
            add("J6", f"S4B_s{s}_{n:02d}", 64, f"{cv} --seed {s} --bootstrap-seed {n} --bootstrap-streams three",
                t["replica"])
    for u in PANEL_U:
        for s in PANEL_SEEDS:
            add("J7", f"S4U_{u.replace(':', '')}_s{s}", 128,
                f"{uni} --seed {s} --universe {u} --branch-select derived", t["universe"])
    for s in PANEL_SEEDS[1:]:
        add("J7", f"S4CV_s{s}", 64, f"{cv} --seed {s} --branch-select all", t["central"])
    for row in csv.DictReader(open(pinned(PERIOD_JOBS)), delimiter="\t"):
        p, bseed = row["period"], row["bootstrap_seed"]
        args = (f"--omnifile $P/inputs/runEventLoopOmniFold_{p}.root --mcfile $P/flux/runEventLoopMC_{p}.root "
                f"--iters 5 --use-weights --estimator lgbm --seed {row['seed']} --branch-select all")
        if bseed != "-":
            args += f" --bootstrap-seed {bseed} --bootstrap-streams both"
        add("J8", row["name"], 64, args, t["period_ctrl"] if p == "ALL" else t["period"])
    return r


def times(units: dict) -> dict:
    e = {k: v["elapsed_s"] for k, v in units["runs"].items()}
    cls = lambda labels: max(e[x] for x in labels)  # noqa: E731
    t = {"central": cls(["D_cv", "D_unit"]),
         "universe": cls(["F_MaCCQE0", "F_Flux23", "F_MaRES0", "F_NormDISCC0"]),
         "lateral": cls(["FL_BAX0", "FL_BAX0_rep"]),
         "replica": cls([f"RB_{i:03d}" for i in range(1, 9)] + ["RB_001_rep", "D_unit"]),
         "period": cls(["RF_PA", "RPR_PA_b01"])}
    t["period_ctrl"] = math.ceil(e["P_ctrl"] * e["RF_PA"] / e["P_PA"])
    return t


def pack(job_runs: list[dict], n_lanes: int) -> list[list[dict]]:
    lanes = [[] for _ in range(n_lanes)]
    load = [0.0] * n_lanes
    for r in sorted(job_runs, key=lambda x: -x["est_s"]):   # stable: ties keep the declared order
        i = min(range(n_lanes), key=lambda k: (load[k], k))
        lanes[i].append(r)
        load[i] += r["est_s"]
    return lanes


def limit_str(s: float) -> str:
    m = math.ceil(s / 60)
    return f"{m // 60:02d}:{m % 60:02d}:00"


# ---- the production readout's checks (read by re2_k1.py; RE2-DECLARATION-B.md §5) ---------------------------------
J0_OUT = "/pscratch/sd/j/josephrb/2d-closeout-re2-20261023/j0/out"
SC_OUT = "/pscratch/sd/j/josephrb/2d-closeout-stageC-production-20261015/out"
D2 = ("/pscratch/sd/j/josephrb/methods-paper/re1-20261022/out/2d/d2_data_refined.npz",
      "71ca3e5fc97cfc0625d84484d9c1f4a59476feacfd3813cdc98d89782329488a")
J0_SUMS = [ST / "stageF/methods/re2/run/j0_readout" / f"SHA256SUMS.{j}" for j in ("J0a", "J0b")]
SC_SUMS = (ST / "stageC/production/evidence/production/SHA256SUMS.pscratch",
           "eab367a67b5664fe2d3d45298bac7bd80a5f43ad01a2c72b82b4b56f3c38ff78")
# July universes measured null (NormDISCC) or below the power floor (EtaNCEL) against the July CV, purity arm:
# NormDISCC_0/1 <= 1.5e-11, EtaNCEL_0/1 3.0e-7, every other universe >= 1.08e-2 (RE2-DECLARATION-B.md §5.1).
NULL_U = ("NormDISCC:0", "NormDISCC:1")
WEAK_U = ("EtaNCEL:0", "EtaNCEL:1")
U_MIN_SHIFT = "1e-4"


def sums(path: Path) -> dict:
    out = {}
    for line in path.read_text().splitlines():
        d, n = line.split(None, 1)
        out[n.strip()] = d
    return out


def checks(allr: list[dict]) -> list[dict]:
    j0 = {}
    for p in J0_SUMS:
        j0.update(sums(p))
    sc = sums(pinned(SC_SUMS))
    labels = {r["label"] for r in allr}
    rows = []

    def add(cid, kind, test, ref, sha="", hist="", min_shift=""):
        if test not in labels or (ref.startswith("run:") and ref[4:] not in labels):
            raise RuntimeError(f"{cid}: {test} or {ref} is not a part-B run")
        rows.append({"id": cid, "kind": kind, "test": test, "ref": ref, "ref_sha256": sha, "hist": hist,
                     "min_shift": min_shift})

    def j0ref(label):
        return f"{J0_OUT}/{label}/xsec.root", j0[f"{label}/xsec.root"]

    def scref(name):
        return f"{SC_OUT}/{name}/xsec.root", sc[f"out/{name}/xsec.root"]

    # the adopted product: its repeat, D2, J0's refined CV, and the efficiency the figure reads (CHK-eff)
    add("PB-ER-rep", "le", "ER", "run:C0_cv")
    add("PB-ER-D2", "le", "ER", *D2)
    add("PB-ER-J0", "le", "ER", *j0ref("D_cv"))
    add("PB-ER-eff", "le", "ER", *j0ref("C_cv"), hist="hEff2D")
    add("PB-unit", "le", "C0_unit", "run:C0_cv")
    add("PB-unit-J0", "le", "C0_unit", *j0ref("D_unit"))
    for u in NULL_U:
        add(f"PB-null-{tag(u)}", "le", f"U_{tag(u)}", "run:ER")
    # cross-job repeats: the same argv in J0 and in part B
    for j0l, pb in (("F_MaCCQE0", "U_MaCCQE_0"), ("F_Flux23", "U_Flux_23"), ("F_MaRES0", "U_MaRES_0"),
                    ("F_NormDISCC0", "U_NormDISCC_0"), ("FL_BAX0", "S3_BeamAngleX0"), ("RF_PA", "pu_PA_s42"),
                    ("RPR_PA_b01", "pu_PA_b01"), *((f"RB_{i:03d}", f"S1_{i:03d}") for i in range(1, 9))):
        add(f"PB-J0-{pb}", "le", pb, *j0ref(j0l))
    # the S4(ii) panel at seed 42 against J2's product for the same universe (Muon_Energy_MINOS:0 has none)
    for u in PANEL_U:
        if f"U_{tag(u)}" in labels:
            add(f"PB-panel-{tag(u)}", "le", f"S4U_{u.replace(':', '')}_s42", f"run:U_{tag(u)}")
    # the refined background stream on the data, every replica against Stage C's purity replica of the same seeds
    for r in allr:
        if r["label"].startswith(("S1_", "S4B_")):
            add(f"PB-stream-{r['label']}", "stream", r["label"], *scref(f"2dc_P_{r['label']}"))
    # power: every universe outside the null and weak bands, every lateral, the seeds, a replica, the periods
    for r in allr:
        if r["label"].startswith("U_"):
            u = options_of(r["args"])["--universe"]
            if u not in NULL_U + WEAK_U:
                add(f"PB-pow-{r['label']}", "differs", r["label"], "run:ER", min_shift=U_MIN_SHIFT)
        elif r["label"].startswith("S3_"):
            add(f"PB-pow-{r['label']}", "differs", r["label"], "run:ER", min_shift="1e-6")
    for test, ref in (("S1_001", "ER"), ("S4B_s45_01", "S1_001"), ("S4CV_s45", "ER"), ("pu_PA_b01", "pu_PA_s42"),
                      ("pu_PA_s43", "pu_PA_s42"), ("pu_PB_s42", "pu_CTRL_s42")):
        add(f"PB-pow-{test}", "differs", test, f"run:{ref}", min_shift="1e-6")
    return rows


def options_of(args: str) -> dict:
    toks, out, i = args.split(), {}, 0
    while i < len(toks):
        if i + 1 < len(toks) and not toks[i + 1].startswith("--"):
            out[toks[i]] = toks[i + 1]
            i += 2
        else:
            out[toks[i]] = True
            i += 1
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--units", type=Path, required=True, help="J0's units.json (re2_units.py)")
    ap.add_argument("--runs-out", type=Path, required=True)
    ap.add_argument("--jobs-out", type=Path, required=True)
    ap.add_argument("--checks-out", type=Path, required=True)
    a = ap.parse_args(argv)
    t = times(json.loads(a.units.read_text()))
    allr = runs(t)
    jobs = []
    for job, (cpus, n_split) in JOBS.items():
        mine = [r for r in allr if r["job"] == job]
        chunks = [mine[i::n_split] for i in range(n_split)] if n_split > 1 else [mine]
        for k, chunk in enumerate(chunks):
            name = job if n_split == 1 else f"{job}{'abcdefgh'[k]}"
            lanes = pack(chunk, 256 // cpus)
            for i, lane in enumerate(lanes, 1):
                for r in lane:
                    r.update(job=name, lane=f"{name}.{i}")
            longest = max(sum(r["est_s"] for r in ln) for ln in lanes)
            wall = PREFLIGHT_S + longest
            lim = math.ceil(FACTOR * wall / 60) * 60
            if lim >= MAX_LIMIT_S:
                raise RuntimeError(f"{name}: limit {lim} s is not under 12 h")
            steps = sum(r["est_s"] * r["cpus"] for r in chunk) / 256 / 3600
            jobs.append({"job": name, "class": job, "gated": "yes" if job in DIAGNOSTIC else "no",
                         "lanes": len(lanes), "lane_cpus": cpus, "runs": len(chunk), "longest_lane_s": longest,
                         "preflight_s": PREFLIGHT_S, "wall_s": wall, "limit": limit_str(lim),
                         "projected_node_h": round(wall / 3600, 4), "cap_node_h": round(lim / 3600, 4),
                         "steps_node_h": round(steps, 4),
                         "j0_fraction_node_h": round(steps / J0_FRACTION[cpus], 4)})
    order = {j["job"]: i for i, j in enumerate(jobs)}
    allr.sort(key=lambda r: (order[r["job"]], r["lane"]))
    with open(a.runs_out, "w", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["job", "lane", "label", "cpus", "script", "args", "est_s"])
        for r in allr:
            w.writerow([r["job"], r["lane"], r["label"], r["cpus"], r["script"], r["args"], r["est_s"]])
    with open(a.jobs_out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(jobs[0]), delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(jobs)
    chk = checks(allr)
    with open(a.checks_out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(chk[0]), delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(chk)
    core = [j for j in jobs if j["gated"] == "no"]
    tot = lambda js, k: round(sum(j[k] for j in js), 4)  # noqa: E731
    kinds = {k: sum(1 for c in chk if c["kind"] == k) for k in ("le", "stream", "differs")}
    print(json.dumps({"times_s": t, "n_runs": len(allr), "n_jobs": len(jobs), "checks": kinds,
                      "core": {k: tot(core, k) for k in ("projected_node_h", "cap_node_h", "steps_node_h",
                                                         "j0_fraction_node_h")},
                      "all": {k: tot(jobs, k) for k in ("projected_node_h", "cap_node_h", "steps_node_h",
                                                        "j0_fraction_node_h")}}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())

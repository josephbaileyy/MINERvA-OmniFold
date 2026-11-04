"""COV2D's run and job tables, and the job-side input checks (COV2D-DECLARATION.md sections 4.4, 7, 8, 10; the
director's rulings of 2026-11-04 on staging and re-hashing).

* ``tables(truth)``: the 786 runs of one truth (central 1, universes 175, laterals 10, replicas 300, toys 300), each
  with part B's own argv for its class (RE2/run/partb_runs.tsv: J1 for the central and the toys, J2 for the
  universes, J3 for the laterals, J4 for the replicas) plus ``--data-file`` (d_T, or the toy's own file). Packing is
  part B's layout (section 8): 4 universe jobs (2 lanes x 128 CPUs), 1 lateral-and-central job (2 x 128), 3 replica
  jobs and 3 toy jobs (4 x 64). Each job's limit is part B's rule, ceil-to-the-minute of 1.25 x (its longest lane +
  300 s), from part B's per-run estimates; ``limit_of`` reproduces part B's own limits (a test).
* ``check``: the inputs a job's runs read, before any run. The staged copies ($CV, the laterals) are re-hashed through
  O_NOATIME against the staging record (inputs.stat, sha256 3614ebad...); a mismatch or a missing file stops the job,
  with no re-stage (the director's rule). The data files are hashed against step B's record (pseudo_b.json). $UNI,
  which is not staged, is stat-checked against part B's DTN record (size, mtime, inode), as part B's jobs did. The
  --mcfile and flux-universe files are hashed against RE-2's pins. Nothing is read without O_NOATIME.

  python cov2d_jobs.py tables --truth G18 --out DIR
  python cov2d_jobs.py check --runs RUNS --job JOB --stats INPUTS_STAT --pseudo-b PSEUDO_B_JSON

MEASURES: tables and checks. CANNOT AUTHORIZE: a submission.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import cov2d as c  # noqa: E402

COMMON = ["--mcfile", "$MC", "--iters", "5", "--use-weights", "--estimator", "lgbm", "--seed", "42"]
REFINE = ["--bkg-mode", "negweight-refined", "--refine-n-estimators", "400", "--refine-num-leaves", "31"]
EST = {"central": 866, "universe": 1150, "lateral": 1678, "replica": 920, "toy": 866}   # part B's per-run estimates
PREFLIGHT_S = 300
LATERAL_FILES = [f"runEventLoopOmniFold_5D_MEFHC_active_{b}_{i}.root" for b in c.LATERAL_BANDS for i in (0, 1)]
UNI_STAT = "171117087867 1783523295 882725391507234642"   # part B's DTN record (partb_readout/preflight/inputs.stat)
PINS = {"$MC": "d40aea69235cdc98644e1bb3e622e579d6b81904c004c83fe50465079989f316",
        "$FLUXU": "5eecae84509ba8ededbe8fdee63508d8e36cd057cc0547a940383f80248580eb",
        "$K2A": "7eb39088a42844b48ec1f8e1b6b586b8d8d4363611d68b726112f9f75c99b9db"}   # (2a)'s kept file (the pilot)
PILOT_EST = {"universe64": 1150}   # part B's J7: universe-type runs at 64 CPUs, 1,121 s each (estimate 43,714 s / 39)


def argv(kind: str, data_file: str, extra: str = "") -> list[str]:
    """Part B's argv for the class, plus --data-file."""
    if kind in ("central", "toy"):
        a = ["--omnifile", "$CV", *COMMON, "--branch-select", "all", *REFINE]
    elif kind == "universe":
        a = ["--omnifile", "$UNI", "--flux-universe-file", "$FLUXU", "--verbose", *COMMON, "--universe", extra,
             "--branch-select", "derived", *REFINE]
    elif kind == "lateral":
        a = ["--omnifile", f"$ACT/{extra}", *COMMON, "--branch-select", "all", *REFINE]
    elif kind == "replica":
        a = ["--omnifile", "$CV", *COMMON, "--bootstrap-seed", extra, "--bootstrap-streams", "three", *REFINE]
    else:
        raise c.Refusal(f"unknown run class {kind}")
    return a + ["--data-file", data_file]


def limit_of(longest_lane_s: int) -> str:
    s = math.ceil(1.25 * (longest_lane_s + PREFLIGHT_S) / 60) * 60
    return f"{s // 3600:02d}:{s % 3600 // 60:02d}:00"


def runs_of(truth: str) -> list[dict]:
    real = f"$D/data_{c.REALIZATION_SEED[truth]}.root"
    out = [{"kind": "central", "label": f"X_{truth}", "args": argv("central", real)}]
    for b in c.ORDER:
        for i in range(c.BANDS[b]):
            out.append({"kind": "universe", "label": f"U_{truth}_{b}_{i}", "args": argv("universe", real, f"{b}:{i}")})
    for f in LATERAL_FILES:
        lab = f[len("runEventLoopOmniFold_5D_MEFHC_active_"):-len(".root")]
        out.append({"kind": "lateral", "label": f"L_{truth}_{lab}", "args": argv("lateral", real, f)})
    for n in range(1, 301):
        out.append({"kind": "replica", "label": f"B_{truth}_{n:03d}", "args": argv("replica", real, str(n))})
    for s in c.TOY_SEEDS[truth]:
        out.append({"kind": "toy", "label": f"T_{truth}_{s}", "args": argv("toy", f"$D/data_{s}.root")})
    return out


def pack(runs: list[dict], truth: str) -> tuple[list[dict], list[dict]]:
    """(run rows with job and lane, job rows), part B's layout."""
    by = {k: [r for r in runs if r["kind"] == k] for k in EST}
    plan = []      # (job name, runs, lanes, lane_cpus)
    U = by["universe"]
    for j, part in zip("abcd", (U[0:44], U[44:88], U[88:132], U[132:175])):
        plan.append((f"{truth}_U{j}", part, 2, 128))
    plan.append((f"{truth}_L", by["central"] + by["lateral"], 2, 128))
    for kind, tag in (("replica", "B"), ("toy", "T")):
        R = by[kind]
        for j, k0 in zip("abc", (0, 100, 200)):
            plan.append((f"{truth}_{tag}{j}", R[k0:k0 + 100], 4, 64))
    rows, jobs = [], []
    for name, part, lanes, cpus in plan:
        lane_s = [0] * lanes
        for k, r in enumerate(part):
            lane = k % lanes
            lane_s[lane] += EST[r["kind"]]
            rows.append({**r, "job": name, "lane": f"{name}.{lane + 1}", "cpus": cpus})
        jobs.append({"job": name, "lanes": lanes, "lane_cpus": cpus, "runs": len(part), "longest_lane_s": max(lane_s),
                     "wall_s": max(lane_s) + PREFLIGHT_S, "limit": limit_of(max(lane_s))})
    return rows, jobs


def pilot() -> tuple[list[dict], list[dict]]:
    """The pilot (section 10): (2b) and section 9.12 on (2a)'s kept file, then x_hat_T, one universe, one replica, one
    lateral and one toy at G18, on one node in three lanes at part B's CPU counts per class."""
    real, toy = f"$D/data_{c.REALIZATION_SEED['G18']}.root", f"$D/data_{c.TOY_SEEDS['G18'][0]}.root"
    lat0 = LATERAL_FILES[0]
    lanes = [
        (128, [("P912_L_BeamAngleX_0", "lateral", argv("lateral", "$K2A", lat0)),
               ("L_G18_BeamAngleX_0", "lateral", argv("lateral", real, lat0))]),
        (64, [("P2b_ER", "central", argv("central", "$K2A")),
              ("X_G18", "central", argv("central", real)),
              (f"T_G18_{c.TOY_SEEDS['G18'][0]}", "toy", argv("toy", toy))]),
        (64, [("B_G18_001", "replica", argv("replica", real, "1")),
              ("P912_U_MaRES_0", "universe", argv("universe", "$K2A", "MaRES:0")),
              ("U_G18_Flux_0", "universe", argv("universe", real, "Flux:0"))]),
    ]
    rows, lane_s = [], []
    for k, (cpus, runs) in enumerate(lanes):
        t = 0
        for label, kind, a in runs:
            t += EST[kind]
            rows.append({"kind": kind, "label": label, "args": a, "job": "pilot", "lane": f"pilot.{k + 1}", "cpus": cpus})
        lane_s.append(t)
    return rows, [{"job": "pilot", "lanes": len(lanes), "lane_cpus": 128, "runs": len(rows),
                   "longest_lane_s": max(lane_s), "wall_s": max(lane_s) + PREFLIGHT_S, "limit": limit_of(max(lane_s))}]


def tables(truth: str, out: Path) -> dict:
    rows, jobs = pilot() if truth == "pilot" else pack(runs_of(truth), truth)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / f"runs_{truth}.tsv", "w") as f:
        f.write("job\tlane\tlabel\tcpus\tscript\targs\test_s\n")
        for r in rows:
            f.write(f"{r['job']}\t{r['lane']}\t{r['label']}\t{r['cpus']}\tre2\t{' '.join(r['args'])}\t{EST[r['kind']]}\n")
    with open(out / f"jobs_{truth}.tsv", "w") as f:
        f.write("job\tlanes\tlane_cpus\truns\tlongest_lane_s\twall_s\tlimit\n")
        for j in jobs:
            f.write("\t".join(str(j[k]) for k in ("job", "lanes", "lane_cpus", "runs", "longest_lane_s", "wall_s",
                                                   "limit")) + "\n")
    return {"runs": len(rows), "jobs": len(jobs), "projected_node_h": sum(j["wall_s"] for j in jobs) / 3600}


def noatime_sha256(path: str) -> str:
    h = hashlib.sha256()
    fd = os.open(path, os.O_RDONLY | os.O_NOATIME)
    try:
        while True:
            b = os.read(fd, 1 << 24)
            if not b:
                break
            h.update(b)
    finally:
        os.close(fd)
    return h.hexdigest()


def check(runs_tsv: Path, job: str, stats: Path, pseudo_b: Path, env: dict) -> dict:
    """The inputs of ``job``'s runs. ``env`` maps $CV, $ACT, $UNI, $MC, $FLUXU, $D to paths."""
    rows = [ln.rstrip("\n").split("\t") for ln in open(runs_tsv)][1:]
    mine = [r for r in rows if r[0] == job]
    if not mine:
        raise c.Refusal(f"{job} has no runs")
    args = " ".join(r[5] for r in mine)
    record = {ln.split()[-1]: (ln.split()[0], " ".join(ln.split()[1:4])) for ln in open(stats) if ln.strip()}
    files = json.loads(Path(pseudo_b).read_text())["files"]
    data_sha = {Path(f["path"]).name: f["sha256"] for f in files}
    bad, done = [], {}

    def staged(path):
        if path not in record:
            bad.append(f"{path} is not in the staging record")
        elif not os.path.exists(path):
            bad.append(f"{path} is missing (purged?): stop, no re-stage")
        else:
            got = noatime_sha256(path)
            done[path] = got
            if got != record[path][0]:
                bad.append(f"{path} sha256 {got} != staged {record[path][0]}")
    if "$CV" in args:
        staged(env["$CV"])
    for f in LATERAL_FILES:
        if f"$ACT/{f}" in args:
            staged(f"{env['$ACT']}/{f}")
    if "$UNI" in args:
        s = os.stat(env["$UNI"])
        got = f"{s.st_size} {int(s.st_mtime)} {s.st_ino}"
        done[env["$UNI"]] = got
        if got != UNI_STAT:
            bad.append(f"$UNI stat {got} != part B's DTN record {UNI_STAT}")
    for var, want in PINS.items():
        if var in args:
            got = noatime_sha256(env[var])
            done[env[var]] = got
            if got != want:
                bad.append(f"{var} sha256 {got} != {want}")
    for name in sorted({a.split("/")[-1] for r in mine for a in r[5].split() if a.startswith("$D/")}):
        p = f"{env['$D']}/{name}"
        if name not in data_sha:
            bad.append(f"{name} is not in step B's record")
        elif not os.path.exists(p):
            bad.append(f"{p} is missing")
        else:
            got = noatime_sha256(p)
            done[p] = got
            if got != data_sha[name]:
                bad.append(f"{name} sha256 {got} != step B's {data_sha[name]}")
    return {"job": job, "runs": len(mine), "checked": done, "problems": bad}


CAP_NODE_H = 165.8          # COV2D-BINDING-1.md ruling 3
PSEUDO_LIMIT = "03:00:00"   # cov2d_pseudo.sbatch


def hms(t: str) -> int:
    h, m, s = (int(x) for x in t.split(":"))
    return 3600 * h + 60 * m + s


def gate(sacct_psv: str, limits: dict, want: str) -> dict:
    """The charge gate: every ended cov2d-* attempt's elapsed node-h, plus every unfinished attempt's limit, plus the
    wanted job's limit, must be at most the cap. ``sacct_psv``: sacct -X -n -P -o JobID,JobName,State,ElapsedRaw,
    NNodes rows; ``limits``: {job: limit} from the jobs tables and the pseudo job; an attempt's job is its JobName
    after the "cov2d-" prefix."""
    spent, held = 0.0, 0.0
    for ln in sacct_psv.splitlines():
        if not ln.strip():
            continue
        _, name, state, elapsed, nodes = ln.split("|")[:5]
        if not name.startswith("cov2d-"):
            continue
        if state.split()[0] in ("PENDING", "RUNNING", "REQUEUED", "CONFIGURING", "SUSPENDED"):
            held += hms(limits[name[len("cov2d-"):]]) / 3600 * max(int(nodes or 1), 1)
        else:
            spent += int(elapsed or 0) / 3600 * max(int(nodes or 1), 1)
    total = spent + held + hms(limits[want]) / 3600
    return {"spent": spent, "held": held, "want": want, "want_node_h": hms(limits[want]) / 3600, "total": total,
            "cap": CAP_NODE_H, "pass": total <= CAP_NODE_H}


DVS_BYTES = 4 << 30   # the director's ruling (b), 2026-11-04: a few GB, timed, in place of a full CFS-read lateral


def read_rate(path: str, nbytes: int) -> dict:
    """The first nbytes of path through O_NOATIME, timed: MB/s, and the digest of what was read."""
    import time
    h, done = hashlib.sha256(), 0
    t0 = time.monotonic()
    fd = os.open(path, os.O_RDONLY | os.O_NOATIME)
    try:
        while done < nbytes:
            b = os.read(fd, min(1 << 24, nbytes - done))
            if not b:
                break
            h.update(b)
            done += len(b)
    finally:
        os.close(fd)
    dt = time.monotonic() - t0
    return {"path": path, "bytes": done, "seconds": dt, "MB_per_s": done / 1e6 / dt if dt > 0 else None,
            "sha256_of_prefix": h.hexdigest()}


def dvs_rate(staged: str, cfs: str, nbytes: int = DVS_BYTES) -> dict:
    """The staged copy's read rate beside the CFS original's (DVS from a compute node), on the same prefix."""
    a, b = read_rate(staged, nbytes), read_rate(cfs, nbytes)
    return {"staged": a, "cfs": b, "prefix_equal": a["sha256_of_prefix"] == b["sha256_of_prefix"],
            "declared_departure": "replaces the full CFS-read lateral of COV2D-DECLARATION.md section 8 :432-433 and "
                                  "section 10 :549 (the director's ruling (b)): staging is complete"}


def main(argv_=None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("tables")
    p.add_argument("--truth", required=True, choices=sorted(c.TOY_SEEDS) + ["pilot"])
    p.add_argument("--out", required=True)
    p = sub.add_parser("gate")
    p.add_argument("--sacct", required=True)
    p.add_argument("--tables", required=True)
    p.add_argument("--want", required=True)
    p = sub.add_parser("dvs-rate")
    p.add_argument("--staged", required=True)
    p.add_argument("--cfs", required=True)
    p.add_argument("--bytes", type=int, default=DVS_BYTES)
    p = sub.add_parser("check")
    for k in ("--runs", "--job", "--stats", "--pseudo-b"):
        p.add_argument(k, required=True)
    a = ap.parse_args(argv_)
    if a.cmd == "tables":
        print(json.dumps(tables(a.truth, Path(a.out))))
        return 0
    if a.cmd == "dvs-rate":
        print(json.dumps(dvs_rate(a.staged, a.cfs, a.bytes), indent=1))
        return 0
    if a.cmd == "gate":
        limits = {f"pseudo_{t}": PSEUDO_LIMIT for t in c.TOY_SEEDS}
        for f in Path(a.tables).glob("jobs_*.tsv"):
            for ln in f.read_text().splitlines()[1:]:
                row = ln.split("\t")
                limits[row[0]] = row[6]
        rec = gate(Path(a.sacct).read_text(), limits, a.want)
        print(json.dumps(rec))
        return 0 if rec["pass"] else 3
    env = {k: os.environ.get(k[1:], "") for k in ("$CV", "$ACT", "$UNI", "$MC", "$FLUXU", "$D", "$K2A")}
    rec = check(Path(a.runs), a.job, Path(a.stats), Path(a.pseudo_b), env)
    print(json.dumps(rec, indent=1))
    return 0 if not rec["problems"] else 4


if __name__ == "__main__":
    sys.exit(main())

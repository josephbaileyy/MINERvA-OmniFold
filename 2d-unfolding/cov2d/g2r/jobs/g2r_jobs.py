"""COV2D-G2R's run and job tables, the job-side input checks, the order, the charge gate and the environment test's
comparison (COV2D-G2R-DECLARATION.md sections 3, 4, 6-8; binding 1 addendum C1 ruling 2; addendum J1).

* ``tables``: every job of the campaign.
  - ``envtest``: the cluster-environment test, two lanes of 128 CPUs: MaRES:0 at the data through the pre-patch driver
    (COV2D's deploy, PRE_M) and through the patched driver with the flag off. Each lane is one unfold reading $UNI
    cold, so its estimate is the measured full-read universe unfold, ENVTEST_EST_S, not part B's per-run 1,150 s.
  - ``prepare``: one node, no unfold.
  - ``D_Ua``-``D_Ud``: part (a), the 175 universe unfolds at the data. Each is part B's own J2 row (partb_runs.tsv,
    read at its digest) with its job, lanes and CPUs, plus ``--miss-map $MAP``.
  - the two override-off reruns of section 3's noise floor, named in J1 before any run: OFF, part B's rows exactly,
    at the end of D_Ud's second lane (part B's J2d.2 holds 21 runs), so they read $UNI warm in a long job.
  - ``<T>_Ua``-``<T>_Ud``: part (+), COV2D's universe rows and packing (cov2d_jobs.pack, imported), plus
    ``--miss-map $MAP``.
  Limits follow part B's rule (cov2d_jobs.limit_of); the prepare's is fixed.
* ``check``: before any run, the inputs the job's runs read, as cov2d_jobs.check does for COV2D. $UNI's stat against part
  B's DTN record, $MC and $FLUXU against RE-2's pins, the map against the committed prepare record's sha256, and each
  tune's realization against COV2D's committed step-B record (G8). Every read uses O_NOATIME. A missing realization
  is a problem: G8's regeneration is its own connect.
* ``order``: each job once. The prepare needs the committed environment test's PASS. Every unfold job needs the
  committed prepare's PASS. Every unfold job but D_Ua needs D_Ua's first --miss-map run done (rc 0 and its product
  on disk): the LightGBM end-to-end check on the real map.
* ``gate``: the charge gate at CAP_NODE_H, over ``cov2dg2r-*`` attempts only, refusing any it cannot price. Held
  includes the limits of submitted ids that sacct does not list yet (the sacct-lag ruling). For an unfold job it also
  projects the whole campaign (spent + held + every job not yet submitted): over the cap is a STOP to the director (rc
  9), not a trim.
* ``envtest``: the two products compared under RE-2's bound rule (ENVTEST_TOL), since configuration (a) is LightGBM's
  non-deterministic mode and same-CPU reruns differ by up to 6.4e-13 (RE2-J0-REPORT.md:106-107). Every histogram's
  contents and errors agree cell by cell, as RE-2's ``le`` checks (re2_k1.compare, re2_k1.py:153-158): max |a/b - 1|
  <= ENVTEST_TOL over the cells with b != 0, and |a| <= ENVTEST_TOL x max |b| in the cells with b = 0, which RE-2
  leaves unconstrained (the director's ruling). Every TParameter agrees to that relative tolerance, and every JSON-valued
  TNamed leaf by leaf: floats to that relative tolerance, integers, booleans and strings exactly. A NaN in the same
  place on both sides, or the same infinity, agrees (the audit's j5). Every other TNamed must be equal, except ENVTEST_DIFFER, the code and paths that differ by
  design. ``runConfig`` must agree once ``out`` is set aside and the patched run's ``miss_map`` is null. Whether each
  object is also bitwise is recorded; it does not decide.
* ``products``: the readout's products TSV for one point, from the tables and the jobs' SHA256SUMS files.

MEASURES: tables, checks, the order, the gate and the comparison. CANNOT AUTHORIZE: a submission.
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
COV2D = HERE.parents[1]
REPO = HERE.parents[3]
sys.path[:0] = [str(COV2D), str(COV2D / "jobs"), str(HERE.parent)]
import cov2d as c  # noqa: E402
import cov2d_jobs as cj  # noqa: E402

CAP_NODE_H = 110.0                    # COV2D-G2R-DECLARATION.md section 7
PREFIX = "cov2dg2r-"                  # J1: matches every "cov2d" fence; COV2D's own gate prices only "cov2d-"
OFF = ("Flux:23", "MaRES:0")          # section 3's noise floor, named in J1 before any run
ENVTEST_UNIVERSE = "MaRES:0"
PRE_M = "a60547692df5f963e428cdfe4661fc51ab785b7b"   # COV2D's deploy (binding 2 A2): the pre-patch driver 938c53c5...
PARTB_RUNS = (REPO / "docs/orchestration/state/2d-closeout/stageF/methods/re2/run/partb_runs.tsv",
              "526b70e0cda78ef476f921d817ff264f67f1b8844b241ca4e65083a196a1127b")
MAP_ARGS = ["--miss-map", "$MAP"]
PREPARE_LIMIT = "02:00:00"
ENVTEST_EST_S = 2738                  # full-read universe unfold, max (2d-closeout/stageB/REPORT.md:174)
REC = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d/g2r"
ENVTEST_RECORD = REC + "/envtest/envtest.json"
PREPARE_RECORD = REC + "/prepare/g2r_prepare.json"
FIRST = ("envtest", "prepare", "D_Ua")      # D_Ua needs only the prepare; every other unfold job also D_Ua's first run
ENVTEST_DIFFER = ("driverFile", "driverSha256", "omnifoldHelperFile", "runArgv")
ENVTEST_TOL = 1e-8                # RE-2's bound equality rule (RE2-DECLARATION.md:42; RE2-J0-REPORT.md:79)
UNFINISHED = ("PENDING", "RUNNING", "REQUEUED", "CONFIGURING", "SUSPENDED", "COMPLETING", "RESIZING")


def partb_rows() -> list[list[str]]:
    data = PARTB_RUNS[0].read_bytes()
    if hashlib.sha256(data).hexdigest() != PARTB_RUNS[1]:
        raise c.Refusal(f"{PARTB_RUNS[0].name} is not {PARTB_RUNS[1][:8]}...")
    return [ln.split("\t") for ln in data.decode().splitlines()[1:] if ln.strip()]


def universe_of(args: str) -> str:
    a = args.split()
    return a[a.index("--universe") + 1]


def runs() -> list[dict]:
    """Every run: job, lane, label, cpus, args, est_s, point (data | G18 | AR23), role (g2r | off | pre | post), universe."""
    out = []
    pb = [r for r in partb_rows() if r[0].startswith("J2")]
    by_uni = {universe_of(r[5]): r for r in pb}
    if len(pb) != 175 or set(by_uni) != {f"{b}:{i}" for b in c.ORDER for i in range(c.BANDS[b])}:
        raise c.Refusal("part B's J2 rows are not the 175 universes of the bank")
    pre = by_uni[ENVTEST_UNIVERSE]
    for k, role in ((1, "pre"), (2, "post")):
        out.append({"job": "envtest", "lane": f"envtest.{k}", "label": f"E_{role}_MaRES_0", "cpus": int(pre[3]),
                    "args": pre[5], "est_s": ENVTEST_EST_S, "point": "data", "role": role, "universe": ENVTEST_UNIVERSE})
    for r in pb:
        uni = universe_of(r[5])
        out.append({"job": "D_U" + r[0][2:], "lane": "D_U" + r[1][2:], "label": "A_" + r[2][2:], "cpus": int(r[3]),
                    "args": r[5] + " " + " ".join(MAP_ARGS), "est_s": int(r[6]), "point": "data", "role": "g2r",
                    "universe": uni})
    for uni in OFF:
        r = by_uni[uni]
        out.append({"job": "D_Ud", "lane": "D_Ud.2", "label": "O_" + r[2][2:], "cpus": int(r[3]), "args": r[5],
                    "est_s": int(r[6]), "point": "data", "role": "off", "universe": uni})
    for truth in ("G18", "AR23"):
        rows, _ = cj.pack(cj.runs_of(truth), truth)
        for r in rows:
            if r["kind"] != "universe":
                continue
            uni = r["args"][r["args"].index("--universe") + 1]
            out.append({"job": r["job"], "lane": r["lane"], "label": "C" + r["label"][1:], "cpus": r["cpus"],
                        "args": " ".join(r["args"] + MAP_ARGS), "est_s": cj.EST["universe"], "point": truth,
                        "role": "g2r", "universe": uni})
    return out


def jobs(rs: list[dict]) -> list[dict]:
    out = [{"job": "prepare", "lanes": 0, "lane_cpus": 0, "runs": 0, "longest_lane_s": 0, "wall_s": 0,
            "limit": PREPARE_LIMIT}]
    for name in dict.fromkeys(r["job"] for r in rs):
        mine = [r for r in rs if r["job"] == name]
        lanes = dict.fromkeys(r["lane"] for r in mine)
        lane_s = [sum(r["est_s"] for r in mine if r["lane"] == ln) for ln in lanes]
        out.append({"job": name, "lanes": len(lanes), "lane_cpus": max(r["cpus"] for r in mine), "runs": len(mine),
                    "longest_lane_s": max(lane_s), "wall_s": max(lane_s) + cj.PREFLIGHT_S,
                    "limit": cj.limit_of(max(lane_s))})
    return out


RUN_COLS = ("job", "lane", "label", "cpus", "args", "est_s", "point", "role", "universe")
JOB_COLS = ("job", "lanes", "lane_cpus", "runs", "longest_lane_s", "wall_s", "limit")


def tables(out: Path) -> dict:
    rs = runs()
    js = jobs(rs)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "runs_g2r.tsv", "w") as f:
        f.write("\t".join(RUN_COLS) + "\n")
        for r in rs:
            f.write("\t".join(str(r[k]) for k in RUN_COLS) + "\n")
    with open(out / "jobs_g2r.tsv", "w") as f:
        f.write("\t".join(JOB_COLS) + "\n")
        for j in js:
            f.write("\t".join(str(j[k]) for k in JOB_COLS) + "\n")
    return {"runs": len(rs), "jobs": len(js), "held_node_h": sum(cj.hms(j["limit"]) for j in js) / 3600}


def read_runs(path: Path) -> list[dict]:
    lines = Path(path).read_text().splitlines()
    if tuple(lines[0].split("\t")) != RUN_COLS:
        raise c.Refusal(f"{path} is not a runs_g2r table")
    return [dict(zip(RUN_COLS, ln.split("\t"))) for ln in lines[1:] if ln.strip()]


def read_limits(path: Path) -> dict:
    lines = Path(path).read_text().splitlines()
    if tuple(lines[0].split("\t")) != JOB_COLS:
        raise c.Refusal(f"{path} is not a jobs_g2r table")
    return {ln.split("\t")[0]: ln.split("\t")[6] for ln in lines[1:] if ln.strip()}


def committed_data_sha(truth: str) -> dict:
    files = json.loads((REPO / cj.PSEUDO_RECORD.format(truth=truth)).read_text())["files"]
    return {Path(f["path"]).name: f["sha256"] for f in files}


def check(runs_tsv: Path, job: str, map_sha: str | None, env: dict) -> dict:
    """The inputs of ``job``'s runs. ``env`` maps $UNI, $MC, $FLUXU, $MAP, $D to paths."""
    mine = [r for r in read_runs(runs_tsv) if r["job"] == job]
    if not mine:
        raise c.Refusal(f"{job} has no runs")
    args = " ".join(r["args"] for r in mine)
    bad, done = [], {}
    if "$UNI" in args:
        s = os.stat(env["$UNI"])
        done[env["$UNI"]] = f"{s.st_size} {int(s.st_mtime)} {s.st_ino}"
        problem = cj.uni_stat_problem(env["$UNI"])
        if problem:
            bad.append(problem)
    for var in ("$MC", "$FLUXU"):
        if var in args:
            got = cj.noatime_sha256(env[var])
            done[env[var]] = got
            if got != cj.PINS[var]:
                bad.append(f"{var} sha256 {got} != {cj.PINS[var]}")
    if "$MAP" in args:
        if not map_sha:
            bad.append("the job reads the map, but no committed map sha256 was given")
        elif not os.path.exists(env["$MAP"]):
            bad.append(f"{env['$MAP']} is missing")
        else:
            got = cj.noatime_sha256(env["$MAP"])
            done[env["$MAP"]] = got
            if got != map_sha:
                bad.append(f"$MAP sha256 {got} != the committed prepare record's {map_sha}")
    points = {r["point"] for r in mine}
    if len(points) != 1:
        bad.append(f"{job} mixes points {sorted(points)}")
    for truth in sorted(points - {"data"}):
        want = committed_data_sha(truth)
        for name in sorted({a.split("/")[-1] for r in mine for a in r["args"].split() if a.startswith("$D/")}):
            p = f"{env['$D']}/{name}"
            if name not in want:
                bad.append(f"{name} is not in {truth}'s step-B record")
            elif not os.path.exists(p):
                bad.append(f"{p} is missing: G8's regeneration is its own connect")
            else:
                got = cj.noatime_sha256(p)
                done[p] = got
                if got != want[name]:
                    bad.append(f"{name} sha256 {got} != step B's {want[name]} (G8)")
    return {"job": job, "runs": len(mine), "checked": done, "problems": bad}


def order(job: str, committed: dict, submitted: set, first_run_done: bool, map_sha: str | None) -> list[str]:
    """What blocks ``job`` (empty: it may go). ``committed``: {path: parsed record or None} from origin/main."""
    if job in submitted:
        return [f"{job} was already submitted (each job once)"]
    need = []
    env_rec, prep_rec = committed.get(ENVTEST_RECORD), committed.get(PREPARE_RECORD)
    if job != "envtest" and (env_rec or {}).get("verdict") != "PASS":
        need.append(f"the environment test's PASS ({ENVTEST_RECORD}) on origin/main")
    if job not in ("envtest", "prepare"):
        if (prep_rec or {}).get("verdict") != "PASS":
            need.append(f"the prepare's PASS ({PREPARE_RECORD}) on origin/main")
        elif not map_sha or prep_rec.get("map_npz_sha256") != map_sha:
            need.append("the map sha256 is not the committed prepare record's")
    if job not in FIRST and not first_run_done:
        need.append("D_Ua's first --miss-map run done (rc 0, its product on disk)")
    return need


def first_run_done(o: Path) -> bool:
    for walls in sorted(Path(o).glob("walls.D_Ua.*.tsv")):
        for ln in walls.read_text().splitlines():
            f = ln.split("\t")
            if len(f) == 4 and f[3] == "0" and (Path(o) / "out" / f[0] / "xsec.root").is_file():
                return True
    return False


def gate(sacct_psv: str, limits: dict, want: str, submitted: dict) -> dict:
    """``sacct_psv``: JobID|JobName|State|ElapsedRaw|NNodes rows; ``submitted``: {id: job} from submissions.log."""
    if want not in limits:
        raise c.Refusal(f"{want} is not a jobs_g2r row")
    spent = held = 0.0
    listed = set()
    for ln in sacct_psv.splitlines():
        if not ln.strip():
            continue
        jid, name, state, elapsed, nodes = ln.split("|")[:5]
        if not name.startswith(PREFIX):
            continue
        job = name[len(PREFIX):]
        if job not in limits:
            raise c.Refusal(f"sacct lists an unknown G2R job {name}: the gate cannot price it")
        listed.add(jid.split(".")[0])
        n = max(int(nodes or 1), 1)
        if state.split()[0] in UNFINISHED:
            held += cj.hms(limits[job]) / 3600 * n
        else:
            spent += int(elapsed or 0) / 3600 * n
    lagging = sorted(i for i in submitted if i not in listed)
    for i in lagging:
        held += cj.hms(limits[submitted[i]]) / 3600
    total = spent + held + cj.hms(limits[want]) / 3600
    rest = [j for j in limits if j != want and j not in set(submitted.values())]
    projection = total + sum(cj.hms(limits[j]) for j in rest) / 3600
    rec = {"spent": spent, "held": held, "lagging_ids": lagging, "want": want,
           "want_node_h": cj.hms(limits[want]) / 3600, "total": total, "cap": CAP_NODE_H, "pass": total <= CAP_NODE_H,
           "not_yet_submitted": rest, "projection": projection, "stop": False}
    if want not in ("envtest", "prepare") and projection > CAP_NODE_H:
        rec["stop"] = True
        rec["why"] = (f"the campaign's projection {projection:.3f} node-h passes the cap {CAP_NODE_H}: "
                      "a STOP to the director, not a trim")
    return rec


def rel_diff(a, b) -> float:
    """RE-2's ``le`` metric, cell by cell (re2_k1.compare, re2_k1.py:153-158): max |a/b - 1| over the cells with b != 0
    (RE-2's reported cells are all b > 0); a cell with b = 0 counts |a| / max |b| (the director's ruling: RE-2 leaves
    such cells unconstrained). Cells equal on both sides count 0, a NaN in the same place on both sides included (the
    audit's j5). Any other non-finite cell, a shape mismatch, or a nonzero a where b is all zero, gives inf."""
    import numpy as np
    a, b = np.asarray(a, np.float64), np.asarray(b, np.float64)
    if a.shape != b.shape:
        return float("inf")
    differ = ~((a == b) | (np.isnan(a) & np.isnan(b)))
    x, y = a[differ], b[differ]
    if x.size == 0:
        return 0.0
    if not (np.all(np.isfinite(x)) and np.all(np.isfinite(y))):
        return float("inf")
    nz = y != 0.0
    worst = float(np.max(np.abs(x[nz] / y[nz] - 1.0), initial=0.0))
    if np.any(~nz):
        finite_b = np.abs(b[np.isfinite(b)])
        m = float(finite_b.max()) if finite_b.size else 0.0
        worst = max(worst, float(np.max(np.abs(x[~nz]))) / m if m > 0.0 else float("inf"))
    return worst


def same_float(a: float, b: float, tol: float) -> bool:
    """|a - b| <= tol x max(|a|, |b|), with equal values (infinities included) and NaN on both sides agreeing (j5)."""
    if a == b or (math.isnan(a) and math.isnan(b)):
        return True
    if not (math.isfinite(a) and math.isfinite(b)):
        return False
    return abs(a - b) <= tol * max(abs(a), abs(b))


def json_problems(a, b, path: str, tol: float) -> list[str]:
    """Leaf-by-leaf agreement of two parsed JSON values: floats to ``tol`` relative, everything else exactly."""
    if isinstance(a, bool) or isinstance(b, bool) or a is None or b is None or isinstance(a, str) or isinstance(b, str):
        return [] if (type(a) is type(b) and a == b) else [f"{path}: {a!r} != {b!r}"]
    if isinstance(a, dict) and isinstance(b, dict):
        if set(a) != set(b):
            return [f"{path}: keys differ {sorted(set(a) ^ set(b))}"]
        return [p for k in sorted(a) for p in json_problems(a[k], b[k], f"{path}.{k}", tol)]
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [f"{path}: lengths {len(a)} != {len(b)}"]
        return [p for i, (x, y) in enumerate(zip(a, b)) for p in json_problems(x, y, f"{path}[{i}]", tol)]
    if isinstance(a, int) and isinstance(b, int):
        return [] if a == b else [f"{path}: {a} != {b}"]
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return [] if same_float(float(a), float(b), tol) else [f"{path}: {a!r} != {b!r} beyond {tol}"]
    return [f"{path}: {a!r} and {b!r} are not comparable"]


def envtest(pre: str, post: str, tol: float = None) -> dict:
    """The two products compared (see the module docstring)."""
    import ROOT
    import numpy as np
    tol = ENVTEST_TOL if tol is None else tol

    def objects(path):
        try:
            f = ROOT.TFile.Open(path)
        except OSError:
            f = None
        if not f or f.IsZombie():
            raise c.Refusal(f"{path} does not open")
        h, p, n = {}, {}, {}
        for key in f.GetListOfKeys():
            o = key.ReadObj()
            name = key.GetName()
            if o.InheritsFrom("TH1"):
                nb = (o.GetNbinsX() + 2) * (o.GetNbinsY() + 2) * (o.GetNbinsZ() + 2)
                h[name] = (np.array([o.GetBinContent(i) for i in range(nb)], np.float64),
                           np.array([o.GetBinError(i) for i in range(nb)], np.float64), o.ClassName())
            elif o.ClassName().startswith("TParameter"):
                p[name] = o.GetVal()
            elif o.ClassName() == "TNamed":
                n[name] = o.GetTitle()
        f.Close()
        return h, p, n
    (h1, p1, n1), (h2, p2, n2) = objects(pre), objects(post)
    problems, hist_rel, bitwise = [], {}, {}
    if set(h1) != set(h2):
        problems.append(f"histograms differ in name: {sorted(set(h1) ^ set(h2))}")
    for k in sorted(set(h1) & set(h2)):
        (a1, e1, t1), (a2, e2, t2) = h1[k], h2[k]
        hist_rel[k] = max(rel_diff(a2, a1), rel_diff(e2, e1))
        bitwise[k] = a1.tobytes() == a2.tobytes() and e1.tobytes() == e2.tobytes()
        if t1 != t2:
            problems.append(f"histogram {k} is a {t1} and a {t2}")
        elif not hist_rel[k] <= tol:
            problems.append(f"histogram {k} differs by {hist_rel[k]:.3g} relative, beyond {tol}")
    if set(p1) != set(p2):
        problems.append(f"TParameters differ in name: {sorted(set(p1) ^ set(p2))}")
    for k in sorted(set(p1) & set(p2)):
        bitwise[f"param:{k}"] = p1[k] == p2[k]
        if not same_float(p1[k], p2[k], tol):
            problems.append(f"TParameter {k}: {p1[k]!r} != {p2[k]!r} beyond {tol}")
    rc1, rc2 = json.loads(n1.get("runConfig", "{}")), json.loads(n2.get("runConfig", "{}"))
    if rc2.get("miss_map") is not None:
        problems.append("the patched run's miss_map is not null: the flag was not off")
    for d in (rc1, rc2):
        d.pop("out", None)
    rc2.pop("miss_map", None)
    problems += json_problems(rc1, rc2, "runConfig", tol)
    for k in sorted((set(n1) | set(n2)) - set(ENVTEST_DIFFER) - {"runConfig"}):
        a, b = n1.get(k), n2.get(k)
        bitwise[f"named:{k}"] = a == b
        if a is None or b is None:
            problems.append(f"TNamed {k} is in one product only")
            continue
        try:
            ja, jb = json.loads(a), json.loads(b)
        except ValueError:
            if a != b:
                problems.append(f"TNamed {k} differs")
            continue
        problems += json_problems(ja, jb, k, tol)
    if "g2rMissMap" in n2:
        problems.append("the patched run records g2rMissMap with the flag off")
    return {"schema": "cov2d-g2r-envtest-2", "pre": pre, "post": post, "tol": tol, "rule": "RE-2 le per cell: max|a/b-1| over b!=0 (re2_k1.compare); b=0 cells |a|<=tol*max|b|",
            "histograms": len(h1), "parameters": len(p1), "named": len(n1), "hist_rel_diff": hist_rel,
            "bitwise": bitwise, "all_bitwise": all(bitwise.values()),
            "set_aside": list(ENVTEST_DIFFER) + ["runConfig.out", "runConfig.miss_map (null)"],
            "problems": problems, "verdict": "PASS" if not problems else "INVALID"}


def products(runs_tsv: Path, o: Path, point: str) -> list[list[str]]:
    """The readout's TSV rows for ``point``: label, path, sha256, role, universe (data: role g2r and off)."""
    sums = {}
    for f in sorted(Path(o).glob("SHA256SUMS.*")):
        for ln in f.read_text().splitlines():
            if ln.strip():
                digest, rel = ln.split(None, 1)
                if rel in sums and sums[rel] != digest:
                    raise c.Refusal(f"{rel} has two digests")
                sums[rel] = digest
    rows = []
    for r in read_runs(runs_tsv):
        if r["point"] != point or r["role"] not in ("g2r", "off"):
            continue
        rel = f"{r['label']}/xsec.root"
        if rel not in sums:
            raise c.Refusal(f"{r['label']} has no digest in SHA256SUMS")
        rows.append([r["label"], str(Path(o) / "out" / rel), sums[rel], r["role"], r["universe"]])
    return rows


def main(argv_=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("tables")
    p.add_argument("--out", required=True, type=Path)
    p = sub.add_parser("check")
    p.add_argument("--runs", required=True, type=Path)
    p.add_argument("--job", required=True)
    p.add_argument("--map-sha", default="")
    p = sub.add_parser("order")
    for k in ("--job", "--deploy", "--submissions", "--o"):
        p.add_argument(k, required=True)
    p = sub.add_parser("map-sha")
    p.add_argument("--deploy", required=True)
    p = sub.add_parser("gate")
    for k in ("--sacct", "--tables", "--submissions", "--want"):
        p.add_argument(k, required=True)
    p = sub.add_parser("envtest")
    for k in ("--pre", "--post", "--out"):
        p.add_argument(k, required=True)
    p = sub.add_parser("products")
    for k in ("--runs", "--o", "--point", "--out"):
        p.add_argument(k, required=True)
    a = ap.parse_args(argv_)
    try:
        return _main(a)
    except c.Refusal as exc:
        print(json.dumps({"refused": str(exc)}))
        return 5


def committed_records(deploy: str) -> dict:
    import subprocess
    out = {}
    for path in (ENVTEST_RECORD, PREPARE_RECORD):
        r = subprocess.run(["git", "-C", deploy, "show", f"origin/main:{path}"], capture_output=True)
        out[path] = json.loads(r.stdout) if r.returncode == 0 else None
    return out


def submissions(path: Path) -> dict:
    """{id: job} from submissions.log lines '<utc> M=<sha> job=<job> id=<id> limit=<hh:mm:ss>'."""
    out = {}
    for ln in (Path(path).read_text().splitlines() if Path(path).exists() else []):
        w = dict(x.split("=", 1) for x in ln.split()[1:] if "=" in x)
        out[w["id"]] = w["job"]
    return out


def _main(a) -> int:
    if a.cmd == "tables":
        print(json.dumps(tables(a.out)))
        return 0
    if a.cmd == "map-sha":
        rec = committed_records(a.deploy)[PREPARE_RECORD]
        sha = (rec or {}).get("map_npz_sha256", "") if (rec or {}).get("verdict") == "PASS" else ""
        print(sha)
        return 0 if sha else 3
    if a.cmd == "order":
        committed = committed_records(a.deploy)
        prep = committed[PREPARE_RECORD] or {}
        need = order(a.job, committed, set(submissions(Path(a.submissions)).values()), first_run_done(Path(a.o)),
                     prep.get("map_npz_sha256"))
        print(json.dumps({"job": a.job, "blocked_by": need}))
        return 3 if need else 0
    if a.cmd == "gate":
        rec = gate(Path(a.sacct).read_text(), read_limits(Path(a.tables) / "jobs_g2r.tsv"), a.want,
                   submissions(Path(a.submissions)))
        print(json.dumps(rec))
        return 9 if rec["stop"] else (0 if rec["pass"] else 3)
    if a.cmd == "envtest":
        rec = envtest(a.pre, a.post)
        Path(a.out).write_text(json.dumps(rec, indent=1, sort_keys=True))
        print(f"G2R-ENVTEST {rec['verdict']}")
        return 0 if rec["verdict"] == "PASS" else 5
    if a.cmd == "products":
        rows = products(Path(a.runs), Path(a.o), a.point)
        Path(a.out).write_text("".join("\t".join(r) + "\n" for r in rows))
        print(f"{len(rows)} products for {a.point}")
        return 0
    env = {k: os.environ.get(k[1:], "") for k in ("$UNI", "$MC", "$FLUXU", "$MAP", "$D")}
    rec = check(a.runs, a.job, a.map_sha or None, env)
    print(json.dumps(rec, indent=1))
    return 0 if not rec["problems"] else 4


if __name__ == "__main__":
    sys.exit(main())

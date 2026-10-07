#!/usr/bin/env python3
"""s5p production: a read-only runtime diagnostic of the seeds lost to task timeouts.

MEASURES: for every finished production task (a task log with an end line or a time-limit kill), which seeds
completed, which one was running when the task was killed (INTERRUPTED) and which were never reached
(NEVER STARTED); the recorded per-experiment unfolding time (``seconds_unfold``, printed by s5p_nullexp.py
after each seed); how that time splits into lane, node and residual effects; and whether, among COMPLETED
experiments, the residual time is associated with the unshifted null statistics (T_total, T_shape) computed
with the frozen s5p_joint code exactly as the controller computes them.

CANNOT ESTABLISH: that the missing experiments are unbiased. The association is measured only on completed
experiments; the interrupted experiments' statistics are unobserved, and a null association among completed
ones does not bound the tail that timed out. It changes no frozen rule, product, status or job.

Run from a code tree whose nd-unfolding holds the frozen s5p_joint/s5p_inference (cwd = that tree; the
design's relative paths resolve there). Writes only --out.
"""
from __future__ import annotations

import argparse
import collections
import datetime
import glob
import json
import os
import re

import numpy as np

import s5p_joint as sj

HDR = re.compile(r"^\[s5c\] task=(\d+) name=(\S+) job=(\d+) host=(\S+) start=(\S+)Z")
END = re.compile(r"^\[s5c\] task=(\d+) name=(\S+) rc=(\d+) end=(\S+)Z")
SEC = re.compile(r'^\{"out": "(\S+?)_s(\d+)\.npz", "rc": (-?\d+), "seconds": ([0-9.]+)\}')
KILL = re.compile(r"^\[(\S+?)\] error: \*\*\* JOB \d+ ON \S+ CANCELLED AT \S+ DUE TO (.+?) \*\*\*")


def utc(s: str) -> float:
    return datetime.datetime.fromisoformat(s.rstrip("Z")).replace(tzinfo=datetime.timezone.utc).timestamp()


def ranks(x: np.ndarray) -> np.ndarray:
    o = np.argsort(x, kind="mergesort")
    r = np.empty(len(x))
    r[o] = np.arange(len(x), dtype=float)
    xs = x[o]
    i = 0
    while i < len(x):  # average ties
        j = i
        while j + 1 < len(x) and xs[j + 1] == xs[i]:
            j += 1
        r[o[i:j + 1]] = (i + j) / 2.0
        i = j + 1
    return r


def spearman(x: np.ndarray, y: np.ndarray, n_perm: int, rng) -> dict:
    if len(x) < 8:
        return {"n": int(len(x)), "rho": None}
    rx, ry = ranks(np.asarray(x, float)), ranks(np.asarray(y, float))
    rx, ry = rx - rx.mean(), ry - ry.mean()
    rho = float(rx @ ry / np.sqrt((rx @ rx) * (ry @ ry)))
    perm = np.array([abs(rng.permutation(rx) @ ry) for _ in range(n_perm)]) / np.sqrt((rx @ rx) * (ry @ ry))
    return {"n": int(len(x)), "rho": round(rho, 4), "perm_p_two_sided": round(float((np.sum(perm >= abs(rho)) + 1) / (n_perm + 1)), 4),
            "approx_se": round(1 / np.sqrt(len(x) - 1), 4)}


def median_polish(cells: list[tuple[str, str, float]], iters: int = 20) -> tuple[dict, dict, float]:
    """log-time = overall + lane + node (robust two-way fit by alternating medians)."""
    y = np.array([c[2] for c in cells])
    lanes = sorted({c[0] for c in cells})
    nodes = sorted({c[1] for c in cells})
    L = {k: 0.0 for k in lanes}
    N = {k: 0.0 for k in nodes}
    mu = float(np.median(y))
    for _ in range(iters):
        for k in lanes:
            L[k] = float(np.median([v - mu - N[n] for (l, n, v) in cells if l == k]))
        for k in nodes:
            N[k] = float(np.median([v - mu - L[l] for (l, n, v) in cells if n == k]))
        mu = float(np.median([v - L[l] - N[n] for (l, n, v) in cells]))
    return L, N, mu


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--design", default="docs/orchestration/state/s5p/prod/design.json")
    ap.add_argument("--tables", default="docs/orchestration/state/s5p/prod/tables")
    ap.add_argument("--logs", required=True)
    ap.add_argument("--v", required=True)
    ap.add_argument("--time-limit-s", type=float, default=7200.0)
    ap.add_argument("--perm", type=int, default=5000)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rng = np.random.default_rng(20260929)
    design = json.load(open(a.design))
    sj.check_v(design, a.v)
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # 1. task inventory from the logs and the frozen task tables
    table_rows = {}
    for t in glob.glob(os.path.join(a.tables, "*.tsv")):
        for line in open(t):
            if line.startswith("#") or not line.strip():
                continue
            f = line.rstrip("\n").split("\t")
            m = re.search(r"--pseudo-seeds\t(\d+):(\d+)", line)
            out = f[f.index("--out") + 1]
            tag = f[f.index("--tag") + 1]
            table_rows[f[0]] = {"first": int(m.group(1)), "last": int(m.group(2)), "out": out, "tag": tag}
    tasks, unfinished = [], 0
    for path in sorted(glob.glob(os.path.join(a.logs, "*.out"))):
        hdr, end, kill, secs = None, None, None, {}
        for line in open(path, errors="replace"):
            if hdr is None and (m := HDR.match(line)):
                hdr = m
            elif m := END.match(line):
                end = m
            elif m := KILL.match(line):
                kill = m
            elif m := SEC.match(line):
                secs[int(m.group(2))] = (float(m.group(4)), int(m.group(3)))
        if hdr is None:
            continue
        if end is None and kill is None:
            unfinished += 1
            continue
        name = hdr.group(2)
        row = table_rows[name]
        batch_key, idx = name.rsplit("_", 1)
        lane = re.sub(r"-b\d+$", "", batch_key)
        start = utc(hdr.group(5))
        seeds = list(range(row["first"], row["last"] + 1))
        prod = {s: os.path.join(row["out"], f"{row['tag']}_s{s}.npz") for s in seeds}
        exists = {s: os.path.exists(prod[s]) for s in seeds}
        rec = {"name": name, "lane": lane, "batch": batch_key, "task": int(idx), "log": os.path.basename(path),
               "host": hdr.group(4), "start": hdr.group(5) + "Z", "outcome": "completed" if end else f"killed: {kill.group(2)}",
               "seeds": {}}
        interrupted_found = False
        for pos, s in enumerate(seeds):
            if exists[s] and s in secs:
                st = {"state": "completed", "position": pos, "seconds": secs[s][0], "rc": secs[s][1],
                      "mtime": os.path.getmtime(prod[s])}
            elif exists[s]:
                st = {"state": "anomaly: product without a log line", "position": pos}
            elif s in secs:
                st = {"state": "anomaly: log line without a product", "position": pos}
            elif end is not None:
                st = {"state": "anomaly: completed task missing this seed", "position": pos}
            elif not interrupted_found:
                interrupted_found = True
                st = {"state": "interrupted", "position": pos}
            else:
                st = {"state": "never started", "position": pos}
            rec["seeds"][s] = st
        if kill is not None:
            k_t = utc(kill.group(1))
            rec["kill_utc"] = kill.group(1) + "Z"
            rec["kill_minus_start_s"] = round(k_t - start, 1)
            if abs(rec["kill_minus_start_s"] - a.time_limit_s) > 300:  # timestamp zone check failed: use the limit
                k_t = start + a.time_limit_s
                rec["kill_time_source"] = "start + time limit (log timestamp inconsistent)"
            done = [st["mtime"] for st in rec["seeds"].values() if st["state"] == "completed"]
            for s, st in rec["seeds"].items():
                if st["state"] == "interrupted":
                    st["elapsed_at_kill_s_lower_bound"] = round(k_t - (max(done) if done else start), 1)
                    st["elapsed_includes_task_setup"] = not done
        tasks.append(rec)

    # 2. null statistics of every finished product (the controller's unshifted c = 0 statistics)
    stage1 = json.load(open(design["stage1"]))
    supported = json.load(open(design["s5c_contract"]))["measurement"]["partition_J"]["supported_cells"]
    U, names, pz_index = sj.j_matrix(stage1, supported)
    model = sj.Model(design, U)
    V = np.asarray(np.load(a.v, allow_pickle=False)["V"], float)
    tstat = {}

    def stats_for(glob_pat, null_key, seed0):
        files = sj.product_files(glob_pat)
        if not files:
            return {}
        nspec = design["nulls"][null_key]
        mu, var = sj.prediction(nspec["prediction"], U)
        dom = np.ones(len(names), bool) if nspec.get("domain") != "pz_lt_6" else (pz_index <= 1)
        F, seeds = sj.ensemble(model, files)
        tt, ts = sj.statistics(F, mu, var, V, dom, seed0, seeds=seeds)
        return {int(s): (float(x), float(y)) for s, x, y in zip(seeds, tt, ts)}

    for key, spec in design["nulls"].items():
        tstat[f"cal-{key}"] = stats_for(spec["calibration_glob"], key, spec["surrogate_seed0"])
    for key, spec in design["power"].items():
        tstat[f"pow-{key}"] = stats_for(spec["glob"], spec.get("null", "MnvTune_v1"), spec["surrogate_seed0"])

    # 3. runtime decomposition (non-cold completed experiments; position 0 carries the cache build)
    comp = [(t["lane"], t["host"], s, st) for t in tasks for s, st in t["seeds"].items() if st["state"] == "completed"]
    warm = [(l, h, float(np.log(st["seconds"]))) for (l, h, s, st) in comp if st["position"] > 0]
    L, N, mu = median_polish(warm)
    y = np.array([v for (_, _, v) in warm])
    r_lane = np.array([v - mu - L[l] for (l, _, v) in warm])
    r_both = np.array([v - mu - L[l] - N[h] for (l, h, v) in warm])
    mad = lambda z: float(np.median(np.abs(z - np.median(z))))  # noqa: E731
    decomposition = {"n_warm_experiments": len(warm), "overall_median_s": round(float(np.exp(mu)), 1),
                     "lane_factor": {k: round(float(np.exp(v)), 3) for k, v in L.items()},
                     "node_factor_top": dict(sorted(((k, round(float(np.exp(v)), 3)) for k, v in N.items()), key=lambda kv: -kv[1])[:12]),
                     "node_factor_range": [round(float(np.exp(min(N.values()))), 3), round(float(np.exp(max(N.values()))), 3)],
                     "log_time_sd": {"raw": round(float(y.std()), 4), "after_lane": round(float(r_lane.std()), 4), "after_lane_and_node": round(float(r_both.std()), 4)},
                     "log_time_mad": {"raw": round(mad(y), 4), "after_lane": round(mad(r_lane), 4), "after_lane_and_node": round(mad(r_both), 4)},
                     "cold_over_warm_median_ratio": round(float(np.median([st["seconds"] for (_, _, _, st) in comp if st["position"] == 0]) /
                                                                np.median([st["seconds"] for (_, _, _, st) in comp if st["position"] > 0])), 3)}

    # 4. runtime vs null statistic among completed experiments (diagnostic only)
    assoc = {}
    for lane in sorted({t["lane"] for t in tasks}):
        rows = [(h, s, st) for (l, h, s, st) in comp if l == lane and st["position"] > 0 and s in tstat.get(lane, {})]
        if not rows:
            continue
        resid = np.array([np.log(st["seconds"]) - mu - L[lane] - N[h] for (h, s, st) in rows])
        raw = np.array([np.log(st["seconds"]) for (h, s, st) in rows])
        Tt = np.array([tstat[lane][s][0] for (h, s, st) in rows])
        Ts = np.array([tstat[lane][s][1] for (h, s, st) in rows])
        assoc[lane] = {"raw_log_time_vs_T_total": spearman(raw, Tt, a.perm, rng), "raw_log_time_vs_T_shape": spearman(raw, Ts, a.perm, rng),
                       "node_adjusted_log_time_vs_T_total": spearman(resid, Tt, a.perm, rng),
                       "node_adjusted_log_time_vs_T_shape": spearman(resid, Ts, a.perm, rng)}
        slow = resid > np.quantile(resid, 0.9)
        pct_t = ranks(Tt) / max(len(Tt) - 1, 1)
        pct_s = ranks(Ts) / max(len(Ts) - 1, 1)
        assoc[lane]["slowest_decile_median_T_percentile"] = {"total": round(float(np.median(pct_t[slow])), 3), "shape": round(float(np.median(pct_s[slow])), 3), "n": int(slow.sum())}

    # 5. lost seeds
    lost = collections.defaultdict(lambda: collections.Counter())
    interrupted = []
    for t in tasks:
        for s, st in t["seeds"].items():
            lost[t["lane"]][st["state"]] += 1
            if st["state"] == "interrupted":
                typical = float(np.exp(mu + L.get(t["lane"], 0.0) + N.get(t["host"], 0.0)))
                same_task = [x["seconds"] for x in t["seeds"].values() if x["state"] == "completed" and x["position"] > 0]
                interrupted.append({"lane": t["lane"], "batch": t["batch"], "task": t["task"], "seed": s, "host": t["host"],
                                    "position": st["position"], "elapsed_at_kill_s_lower_bound": st["elapsed_at_kill_s_lower_bound"],
                                    "includes_task_setup": st["elapsed_includes_task_setup"],
                                    "lane_node_typical_s": round(typical, 1),
                                    "ratio_to_typical_lower_bound": round(st["elapsed_at_kill_s_lower_bound"] / typical, 2),
                                    "same_task_completed_warm_s": [round(v, 1) for v in same_task],
                                    "node_factor": round(float(np.exp(N.get(t["host"], 0.0))), 3)})
    by_node = collections.defaultdict(lambda: [0, 0])
    for t in tasks:
        by_node[t["host"]][0] += 1
        by_node[t["host"]][1] += t["outcome"].startswith("killed")
    out = {"schema": "s5p-lost-seed-runtime-diagnostic/1", "measured_utc": now, "design_sha256": sj.sha256(a.design),
           "v_sha256": sj.sha256(a.v), "tasks_finished": len(tasks), "tasks_unfinished_skipped": unfinished,
           "tasks_killed": sum(t["outcome"].startswith("killed") for t in tasks),
           "kill_reasons": dict(collections.Counter(t["outcome"] for t in tasks if t["outcome"] != "completed")),
           "seed_states_by_lane": {k: dict(v) for k, v in sorted(lost.items())},
           "runtime_decomposition": decomposition,
           "nodes_with_kills": {h: {"tasks": n, "killed": k, "node_factor": round(float(np.exp(N.get(h, 0.0))), 3)}
                                for h, (n, k) in sorted(by_node.items(), key=lambda kv: -kv[1][1]) if k},
           "interrupted_seeds": interrupted,
           "association_completed_only": assoc,
           "reading_limits": ["association is measured on COMPLETED experiments only; the interrupted experiments' statistics are unobserved",
                              "a null association does not establish that the missing experiments are unbiased",
                              "elapsed_at_kill is a lower bound on the interrupted experiment's runtime (it had not finished)",
                              "never-started seeds: lost by position given the earlier seeds' runtimes; see the record for the assumptions"],
           "tasks": tasks}
    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=1, default=float)
    brief = {k: out[k] for k in ("measured_utc", "tasks_finished", "tasks_unfinished_skipped", "tasks_killed", "kill_reasons",
                                 "seed_states_by_lane", "runtime_decomposition", "nodes_with_kills", "association_completed_only")}
    print(json.dumps(brief, indent=1))
    print(json.dumps(interrupted, indent=0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

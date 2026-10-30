#!/usr/bin/env python3
"""Run the figure diagnosis's jobs (jobs.tsv), each through run_vision.sh, with one retry and a 900 s limit.

usage: XMODEL_DIR=<scratch> python3 -I fig_runs.py <data-dir> <out-dir> [--kind abs|pair|probe] [--only RATER]
A job whose output already ends with "END" (or, for the probe, holds a NUMBER line) is not run again. A job that fails
both attempts is logged FAILED in <out-dir>/status.tsv. sol2 runs 3 at a time and gemini 2 at a time, as the r22
rater runs did. --kind probe runs the vision probe (PROBE.prompt.txt on probe.png) twice per rater instead."""
import concurrent.futures as cf
import csv
import subprocess
import sys
import time
from pathlib import Path

D, OUT = Path(sys.argv[1]), Path(sys.argv[2])
T = Path(__file__).resolve().parent
P = T.parent / "prompts"
kind = sys.argv[sys.argv.index("--kind") + 1] if "--kind" in sys.argv else None
only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
OUT.mkdir(parents=True, exist_ok=True)
if kind == "probe":
    png = Path(sys.argv[sys.argv.index("--png") + 1])
    jobs = [dict(job=f"probe.{m}.r{k}", rater=m, prompt="PROBE", images=str(png / "probe.png"), caption="-")
            for m in ("sol2", "gemini") for k in (1, 2)]
else:
    jobs = [r for r in csv.DictReader(open(D / "jobs.tsv"), delimiter="\t") if kind in (None, r["kind"])]
jobs = [j for j in jobs if only in (None, j["rater"])]


def done(j):
    f = OUT / f"{j['job']}.txt"
    if not f.exists():
        return False
    t = f.read_text(errors="replace")
    return "NUMBER:" in t if j["prompt"] == "PROBE" else t.rstrip().endswith("END")


def one(j):
    if done(j):
        return j["job"], "cached"
    cap = j["caption"].split()
    if len(cap) > 1:   # a pair: both captions, labelled
        tf = OUT / f".{j['job']}.cap"
        tf.write_text("".join(f"{lab}: {Path(c).read_text()}" for lab, c in zip(("A", "B"), cap)))
        cap = [str(tf)]
    for attempt in (1, 2):
        t0 = time.time()
        try:
            r = subprocess.run(["bash", str(T / "run_vision.sh"), j["rater"], str(P / f"{j['prompt']}.prompt.txt"),
                                str(OUT / f"{j['job']}.txt"), cap[0] if cap else "-"] + j["images"].split(),
                               capture_output=True, text=True, timeout=900)
            rc = r.returncode
        except subprocess.TimeoutExpired:
            rc = "timeout"
        with open(OUT / "status.tsv", "a") as f:
            f.write(f"{j['job']}\tattempt={attempt}\trc={rc}\tsecs={int(time.time() - t0)}\n")
        if rc == 0 and done(j):
            return j["job"], "ok"
    with open(OUT / "status.tsv", "a") as f:
        f.write(f"{j['job']}\tFAILED\n")
    return j["job"], "FAILED"


pools = {"sol2": cf.ThreadPoolExecutor(3), "gemini": cf.ThreadPoolExecutor(2)}
futs = [pools[j["rater"]].submit(one, j) for j in jobs]
res = [f.result() for f in futs]
print(f"{len(res)} jobs: " + ", ".join(f"{k} {sum(r[1] == k for r in res)}" for k in ("ok", "cached", "FAILED")))

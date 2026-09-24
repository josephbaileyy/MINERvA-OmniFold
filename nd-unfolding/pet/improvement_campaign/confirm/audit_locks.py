"""Audit of the confirmatory run directories for concurrent writers (review BLOCK, 2026-09-24).

The run lock of `661cb5b9`-`e61ba86c` (mkdir + owner file) was not atomic, so two jobs could have
worked on one run directory at once. For every run directory of the given stages this collects:

* the jobs that EXECUTED the driver there (`run-<job>.log`, written only after a claim), with their
  start/end from `sacct`;
* pairwise time overlap of those jobs -- two drivers alive on one run directory at once;
* the receipt/state segments (job, first, last iteration): contiguous, non-overlapping, and every
  executing job accounted for;
* `fits.jsonl`: each (iteration, step) fitted exactly once.

A run with any overlap, duplicate fit, or segment inconsistency is SUSPECT. Standard library only;
run on Perlmutter (needs `sacct`):  `python3 audit_locks.py <stage dir> ... --output audit.json`.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter
from datetime import datetime
from pathlib import Path


def sacct_intervals(jobs: set[str]) -> dict[str, tuple[float, float, str]]:
    out: dict[str, tuple[float, float, str]] = {}
    ids = sorted(jobs)
    for i in range(0, len(ids), 200):
        text = subprocess.run(["sacct", "-X", "-n", "-P", "-j", ",".join(ids[i:i + 200]),
                               "-o", "JobID,Start,End,State"], capture_output=True, text=True,
                              check=True).stdout
        for line in text.splitlines():
            jid, start, end, state = line.split("|")
            def ts(x: str) -> float:
                return (datetime.fromisoformat(x).timestamp()
                        if x not in ("Unknown", "None", "") else float("inf"))
            out[jid] = (ts(start), ts(end), state)
    return out


def audit_run(run: Path, iv: dict) -> dict:
    jobs = sorted({m.group(1) for p in run.glob("run-*.log")
                   if (m := re.match(r"run-(\d+)\.log$", p.name))})
    # A job's DRIVER interval on this run: from the job's start (an upper bound on how early it
    # could have claimed) to its run log's last write (the driver's last output: it logs until it
    # exits). The job itself may live on (other rows, scoring) after its driver released the run,
    # so job-level overlap alone is not a concurrent writer; driver-level overlap is.
    overlaps, job_overlaps = [], []
    drv = {j: (iv[j][0], (run / f"run-{j}.log").stat().st_mtime) for j in jobs if j in iv}
    for i, a in enumerate(jobs):
        for b in jobs[i + 1:]:
            if a in iv and b in iv:
                s = max(iv[a][0], iv[b][0])
                e = min(iv[a][1], iv[b][1])
                if s < e:
                    job_overlaps.append({"jobs": [a, b], "overlap_s": round(e - s)})
                s = max(drv[a][0], drv[b][0])
                e = min(drv[a][1], drv[b][1])
                if s < e:
                    overlaps.append({"jobs": [a, b], "driver_overlap_s": round(e - s)})
    state = {}
    for name in ("state.json", "receipt.json"):   # state.json is current (written per iteration)
        if (run / name).exists():
            try:
                state = json.loads((run / name).read_text())
            except json.JSONDecodeError:
                state = {"_unreadable": name}
            break
    segs = state.get("segments", [])
    seg_problems = []
    expect = 0
    for sgm in segs:
        first = sgm.get("first_iteration")
        last = sgm.get("last_iteration", first - 1 if first is not None else None)
        if first != expect:
            seg_problems.append(f"segment {sgm.get('job')} starts at {first}, expected {expect}")
        if last is not None and last >= (first or 0):
            expect = last + 1
    seg_jobs = {str(s.get("job")) for s in segs}
    unaccounted = [j for j in jobs if j not in seg_jobs]
    fits = Counter()
    if (run / "fits.jsonl").exists():
        for line in (run / "fits.jsonl").read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                fits[(r.get("iteration"), r.get("step"))] += 1
    dup = sorted(f"{k[0]}/{k[1]}x{v}" for k, v in fits.items() if v > 1)
    suspect = bool(overlaps or dup or seg_problems)
    return {"run": run.name, "status": (run / "status.txt").read_text().strip()
            if (run / "status.txt").exists() else None,
            "executing_jobs": jobs, "overlaps": overlaps, "job_level_overlaps": job_overlaps, "segments": len(segs),
            "segment_problems": seg_problems, "jobs_without_segment": unaccounted,
            "duplicate_fits": dup, "suspect": suspect}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("stages", type=Path, nargs="+")
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    runs = [r for st in args.stages for r in sorted(st.iterdir())
            if r.is_dir() and (r / "run_identity.json").exists()]
    jobs = {m.group(1) for r in runs for p in r.glob("run-*.log")
            if (m := re.match(r"run-(\d+)\.log$", p.name))}
    iv = sacct_intervals(jobs) if jobs else {}
    result = {"audited_at": datetime.now().astimezone().isoformat(), "runs": {}}
    for r in runs:
        result["runs"][f"{r.parent.name}/{r.name}"] = audit_run(r, iv)
    sus = [k for k, v in result["runs"].items() if v["suspect"]]
    result["summary"] = {"runs_audited": len(runs), "jobs": len(jobs), "suspect": sus,
                         "runs_with_jobs_without_segment": [
                             k for k, v in result["runs"].items() if v["jobs_without_segment"]]}
    args.output.write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result["summary"], indent=1))


if __name__ == "__main__":
    main()

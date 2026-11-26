"""Summarize inputs/sacct.psv (TZ=UTC sacct -X for the four test C jobs) into sacct.txt.

Charge = sum(ElapsedRaw x AllocCPUS / 2) / 128 / 3600 node-hours: AllocCPUS counts
logical CPUs, two per physical core, 128 physical cores per Perlmutter CPU node.
"""

from pathlib import Path

import pandas as pd

PLS = ["1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P"]
MODE = {"62041128": "reco", "62041129": "truth", "62041281": "reco", "62041282": "truth"}

s = pd.read_csv(Path(__file__).resolve().parent / "inputs" / "sacct.psv", sep="|", dtype=str)
s["job"], s["task"] = s.JobID.str.split("_").str[0], s.JobID.str.split("_").str[1].astype(int)
s["mode"], s["playlist"] = s.job.map(MODE), s.task.map(lambda i: PLS[i])
s["sec"], s["cpus"] = s.ElapsedRaw.astype(int), s.AllocCPUS.astype(int)
print(f"{len(s)} tasks; states {s.State.value_counts().to_dict()}; exit codes {s.ExitCode.value_counts().to_dict()}")
print(f"{'JobID':14}{'mode':7}{'pl':4}{'State':11}{'Exit':6}{'Elapsed':10}{'Start (UTC)':21}{'End (UTC)':21}{'CPUs':>5}  Node")
for _, r in s.sort_values(["Start", "JobID"]).iterrows():
    print(f"{r.JobID:14}{r['mode']:7}{r.playlist:4}{r.State:11}{r.ExitCode:6}{r.Elapsed:10}{r.Start + 'Z':21}{r.End + 'Z':21}{r.cpus:>5}  {r.NodeList}")
for m in ("reco", "truth"):
    t = s[s["mode"] == m]
    print(f"{m}: {len(t)} tasks, total {t.sec.sum()} s, longest {t.sec.max()} s ({t.loc[t.sec.idxmax(), 'playlist']})")
core_h = (s.sec * s.cpus / 2).sum() / 3600
print(f"first start {s.Start.min()}Z, last end {s.End.max()}Z")
print(f"total {s.sec.sum()} task-s; {core_h:.3f} physical-core-h; charge {core_h / 128:.4f} node-h (declared bound 0.94)")

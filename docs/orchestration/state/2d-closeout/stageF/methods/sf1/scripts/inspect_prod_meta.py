"""Summarize the metadata of the first 200 production calibration products (by seed) of each SF-1 null."""
import collections, glob, json, sys
from pathlib import Path
import numpy as np

ROOT = "/pscratch/sd/j/josephrb/s5p-20260926/runs/prod/cal"
NULLS = {"NuWro_21_09": 1260000, "GENIE_2_12_10_CV": 1220000, "GENIE_2_12_10_MEC": 1240000}
out = {}
for n, base in NULLS.items():
    files = sorted((p for p in glob.glob(f"{ROOT}/{n}/cal_{n}_s*.npz") if ".partial" not in Path(p).name),
                   key=lambda p: int(Path(p).stem.rsplit("_s", 1)[1]))
    seeds = [int(Path(p).stem.rsplit("_s", 1)[1]) for p in files]
    first = files[:200]
    code = collections.Counter(); jobs = collections.Counter(); dev = collections.Counter(); other = collections.Counter()
    for p in first:
        m = json.loads(str(np.load(p, allow_pickle=False)["meta"]))
        code[json.dumps(m["code_sha256"], sort_keys=True)] += 1
        jobs[m.get("slurm_job")] += 1
        dev[json.dumps(m["development"])] += 1
        other[json.dumps({k: m.get(k) for k in ("config", "capacity", "iters", "input_npz_sha256", "bkg_dump_sha256", "detector_bands")}, sort_keys=True)] += 1
    out[n] = {"n_total": len(files), "seed_min": seeds[0], "seed_max": seeds[-1], "first200_seed_range": [seeds[0], seeds[199]],
              "first200_missing_in_range": sorted(set(range(seeds[0], seeds[199] + 1)) - set(seeds[:200])),
              "code": dict(code), "jobs": dict(jobs), "development": dict(dev), "other": dict(other),
              "hyp": m["hypothesis"], "keys": sorted(np.load(first[0]).files)}
print(json.dumps(out, indent=1))

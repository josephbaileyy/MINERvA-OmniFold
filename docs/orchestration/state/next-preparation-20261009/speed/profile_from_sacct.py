"""Reduce the preserved Perlmutter ``sacct`` rows to the timing operands of the speed report.

Inputs are the files in ``operands/`` (read-only ``sacct`` queries of completed
jobs, 2026-10-09). Output: ``results/profile.json``. Standard library only.

Definitions (per batch step):
  * ``cpu_per_elapsed`` = TotalCPU / ElapsedRaw, the mean number of busy logical
    CPUs; it includes OpenMP spin-waiting, so it over-states useful work.
  * ``serial_upper_s`` = (k * E - CPU) / (k - 1) with k the OpenMP thread count:
    the largest single-threaded wall time compatible with E and CPU if every
    other second ran k-wide. It assumes serial phases burn one CPU.
  * node-h = E * billing / 256 / 3600 (Perlmutter CPU node billing 256).
"""

import json
import os
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
OPS = os.path.join(HERE, "operands")
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 5))
NODE_BILLING = 256
NODE_MEM_GB = 487802 * 2**20 / 1e9          # regular_1 AllocTRES mem=487802M


def cpu_s(s):
    days = 0
    if "-" in s:
        d, s = s.split("-")
        days = int(d)
    parts = [float(x) for x in s.split(":")]
    while len(parts) < 3:
        parts.insert(0, 0.0)
    return days * 86400 + parts[0] * 3600 + parts[1] * 60 + parts[2]


def size_gb(s):
    unit = {"K": 2**10, "M": 2**20, "G": 2**30, "T": 2**40}
    return float(s[:-1]) * unit[s[-1]] / 1e9 if s and s[-1] in unit else None


def rows(name):
    with open(os.path.join(OPS, name)) as fh:
        lines = [ln.rstrip("\n").split("|") for ln in fh if "|" in ln]
    head = lines[0]
    return [dict(zip(head, ln)) for ln in lines[1:] if ln[0] != "JobID"]


def billing(r):
    tres = dict(kv.split("=", 1) for kv in r.get("AllocTRES", "").split(",") if "=" in kv)
    return int(tres.get("billing", tres.get("cpu", 0)))


def q(xs):
    xs = sorted(xs)
    return {"n": len(xs), "min": xs[0], "p10": xs[len(xs) // 10], "median": st.median(xs),
            "mean": st.mean(xs), "p90": xs[(9 * len(xs)) // 10], "max": xs[-1]}


def batch_summary(batch, threads, billing_units):
    el = [float(r["ElapsedRaw"]) for r in batch]
    cpu = [cpu_s(r["TotalCPU"]) for r in batch]
    out = {"elapsed_s": q(el), "cpu_per_elapsed": q([c / e for c, e in zip(cpu, el)]),
           "serial_upper_s": q([(threads * e - c) / (threads - 1) for c, e in zip(cpu, el)]),
           "serial_upper_fraction": q([(threads * e - c) / (threads - 1) / e
                                       for c, e in zip(cpu, el)]),
           "max_rss_gb": q([size_gb(r["MaxRSS"]) for r in batch]),
           "max_disk_read_gb": q([size_gb(r["MaxDiskRead"]) for r in batch]),
           "node_h": q([e * billing_units / NODE_BILLING / 3600 for e in el]),
           "omp_threads": threads, "billing": billing_units}
    out["elapsed_max_over_min"] = out["elapsed_s"]["max"] / out["elapsed_s"]["min"]
    return out


def main():
    prof = {"schema": "speed-profile/1", "inputs": sorted(os.listdir(OPS))}

    rep = rows("sacct_59410433_steps.psv")
    alloc = {r["JobID"]: r for r in rep if "." not in r["JobID"]}
    batch = [r for r in rep if r["JobID"].endswith(".batch")]
    prof["lgbm_cv_replica_shared64"] = {
        "what": "VL170 production replicas: LightGBM, CV omnifile, --qos shared, 64 CPUs, "
                "OMP_NUM_THREADS=64 (array 59410433)",
        "states": sorted({r["State"] for r in alloc.values()}),
        **batch_summary(batch, 64, billing(next(iter(alloc.values()))))}

    misc = rows("sacct_exact_pilots_ki85_steps.psv")
    mb = {r["JobID"].replace(".batch", ""): r for r in misc if r["JobID"].endswith(".batch")}
    ma = {r["JobID"]: r for r in misc if "." not in r["JobID"]}
    prof["exact_gbt_cv_fullnode"] = {
        "what": "quoted central E_C: sklearn exact GBT, CV omnifile, regular full node (53116554)",
        **batch_summary([mb["53116554"]], 128, billing(ma["53116554"]))}
    prof["lgbm_cv_replica_fullnode"] = {
        "what": "VL170 pilot replica seed 1, regular full node, OMP_NUM_THREADS=128 (59409026_1)",
        **batch_summary([mb["59409026_1"]], 128, billing(ma["59409026_1"]))}
    prof["lgbm_cv_replica_shared64_pilots"] = {
        "what": "VL170 pilot replicas 2-3 on shared 64 (59409027)",
        **batch_summary([mb[k] for k in mb if k.startswith("59409027")], 64, 64)}
    prof["lgbm_ki85_toy_shared64"] = {
        "what": "KI-85 diagnostic runs, shared 64 (59466329/59466330/59469539)",
        **batch_summary([mb[k] for k in mb if k.startswith(("59466329", "59466330", "59469539"))],
                        64, 64)}

    uni = rows("sacct_universe_sweeps_batch.psv")
    with open(os.path.join(REPO, "2d-unfolding/uq/universes_full_list.txt")) as fh:
        ulist = [ln.strip() for ln in fh if ln.strip()]
    real = [r for r in uni if float(r["ElapsedRaw"]) > 300]
    skipped = [r for r in uni if float(r["ElapsedRaw"]) <= 300]
    sweeps = {}
    for master, label in (("55677843", "purity_newomni (background-aware purity)"),
                          ("55677842", "negweight")):
        b = [r for r in real if r["JobID"].startswith(master + "_")]
        s = batch_summary(b, 128, 256)
        by_band = {}
        for r in b:
            idx = int(r["JobID"].split("_")[1].split(".")[0])
            band = ulist[idx - 1].split(":")[0]
            by_band.setdefault(band, []).append(size_gb(r["MaxRSS"]))
        s["max_rss_gb_by_band"] = {k: {"n": len(v), "median": st.median(v), "max": max(v)}
                                   for k, v in sorted(by_band.items())}
        s["tasks_rss_over_shared64_alloc_gb"] = sum(size_gb(r["MaxRSS"]) > 121920 * 2**20 / 1e9
                                                    for r in b)
        s["what"] = f"universe sweep {label}: LightGBM, universe omnifile (171.1 GB), " \
                    "regular full node, OMP_NUM_THREADS=128, array " + master
        sweeps[master] = s
    prof["lgbm_universe_sweeps_fullnode"] = sweeps
    prof["lgbm_universe_sweeps_skipped_tasks"] = len(skipped)
    cvs = {k: [r for r in real if r["JobID"].startswith(k + ".")] for k in ("55677844", "55677845")}
    prof["lgbm_cv_on_universe_file_fullnode"] = {
        k: batch_summary(v, 128, 256) for k, v in cvs.items()}

    # Natural experiment: the same CV unfold (no --universe) on the 2.1 GB CV omnifile and on
    # the 171 GB universe omnifile, both on a regular full node at 128 threads.
    e_cv = prof["lgbm_cv_replica_fullnode"]["elapsed_s"]["median"]
    e_cv_uni = st.mean(prof["lgbm_cv_on_universe_file_fullnode"][k]["elapsed_s"]["median"]
                       for k in cvs)
    e_uni = prof["lgbm_universe_sweeps_fullnode"]["55677843"]["elapsed_s"]["median"]
    c_cv = prof["lgbm_cv_replica_fullnode"]["cpu_per_elapsed"]["median"] * e_cv
    c_cv_uni = st.mean(prof["lgbm_cv_on_universe_file_fullnode"][k]["cpu_per_elapsed"]["median"]
                       * prof["lgbm_cv_on_universe_file_fullnode"][k]["elapsed_s"]["median"]
                       for k in cvs)
    prof["universe_file_excess"] = {
        "cv_unfold_on_cv_file_s": e_cv, "cv_unfold_on_universe_file_s": e_cv_uni,
        "excess_s": e_cv_uni - e_cv, "excess_cpu_s": c_cv_uni - c_cv,
        "excess_cpu_per_excess_wall": (c_cv_uni - c_cv) / (e_cv_uni - e_cv),
        "f_io_universe_task": (e_uni - e_cv) / e_uni,
        "f_io_cv_on_universe_file": (e_cv_uni - e_cv) / e_cv_uni,
        "rss_excess_per_file_gb": (prof["lgbm_universe_sweeps_fullnode"]["55677843"]["max_rss_gb"]
                                   ["median"] - prof["lgbm_cv_replica_fullnode"]["max_rss_gb"]
                                   ["median"]) / 171.117087867,
        "caveat": "n = 1 CV-file full-node run against n = 2 universe-file CV runs on other "
                  "dates and nodes; the 374 universe tasks give the spread of the latter",
    }
    prof["node_mem_gb"] = NODE_MEM_GB
    out = os.path.join(HERE, "results", "profile.json")
    with open(out, "w") as fh:
        json.dump(prof, fh, indent=1, sort_keys=True)
    print(json.dumps({k: prof["universe_file_excess"][k] for k in
                      ("excess_s", "excess_cpu_per_excess_wall", "f_io_universe_task",
                       "rss_excess_per_file_gb")}, indent=1))


if __name__ == "__main__":
    main()

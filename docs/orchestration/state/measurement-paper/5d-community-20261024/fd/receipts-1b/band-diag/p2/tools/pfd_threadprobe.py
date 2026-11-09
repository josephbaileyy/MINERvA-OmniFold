"""1B pre-check Part 1, in-lane thread probe (the director's choice (i) for P2 and P3).

Run as one srun step with the lanes' exact shape, after the same setup_salloc_env.sh source as s5c_array.sh. It reads
no analysis input, imports only numpy, lightgbm and threadpoolctl, and prints one JSON object to stdout; the wrapper
redirects stdout into the job's output directory. Its fields are the ones P3's probe must reproduce: the four thread
variables, SLURM_CPUS_PER_TASK, the affinity size and threadpool_info after importing numpy and lightgbm.
"""
import json
import os
import sys

record = {
    "thread_variables": {k: os.environ.get(k, "<unset>")
                         for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS")},
    "SLURM_CPUS_PER_TASK": os.environ.get("SLURM_CPUS_PER_TASK", "<unset>"),
    "SLURM_JOB_ID": os.environ.get("SLURM_JOB_ID", "<unset>"),
    "SLURM_STEP_ID": os.environ.get("SLURM_STEP_ID", "<unset>"),
    "affinity_size": len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else "<unavailable>",
    "os_cpu_count": os.cpu_count(),
    "python": sys.version.split()[0],
    "executable": sys.executable,
}
try:
    import numpy as np
    import lightgbm as lgb
    import threadpoolctl
    record["numpy"] = np.__version__
    record["lightgbm"] = lgb.__version__
    record["threadpoolctl"] = threadpoolctl.__version__
    info = threadpoolctl.threadpool_info()
    record["threadpool_info"] = [{k: i.get(k) for k in ("user_api", "internal_api", "prefix", "version", "num_threads",
                                                         "filepath")} for i in info]
    omp = [i.get("num_threads") for i in info if i.get("user_api") == "openmp"]
    record["openmp_default_num_threads"] = omp if omp else "<no openmp pool loaded>"
    record["status"] = "ok"
except Exception as e:  # recorded, not raised: a probe failure does not stop the lanes
    record["status"] = f"failed: {type(e).__name__}: {e}"
print(json.dumps(record, indent=1, sort_keys=True))

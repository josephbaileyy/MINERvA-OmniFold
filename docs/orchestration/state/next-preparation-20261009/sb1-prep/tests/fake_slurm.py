"""A local stand-in for ``sbatch`` and ``sacct``, for ``test_launch_chain.py`` only.

    fake_slurm.py sbatch [sbatch options] SCRIPT    queue a job; print its id
    fake_slurm.py drain                             run queued jobs in id order
    fake_slurm.py sacct -j IDS -o FIELDS [...]      print accounting rows

State lives in ``$FAKE_SLURM_STATE`` (a JSON file). ``drain`` runs each job's script with ``bash``,
the ``--export`` variables, ``SLURM_JOB_ID`` and the ``--chdir``/``--output``/``--error`` it was
given, after its dependencies: ``afterok`` needs every named job to have exited 0, otherwise the job
is CANCELLED (``--kill-on-invalid-dep=yes``); ``afterany`` needs them to have finished. ``sacct``
reports each job's measured elapsed and exit state; ``MaxRSS``, ``MaxDiskRead``, ``ElapsedRaw`` and
billing can be overridden per job name from ``$FAKE_SLURM_OVERRIDES`` (JSON), because a laptop run
of a 4,000-row fixture has no meaningful I/O or timing. Nothing here talks to a scheduler.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

STATE = Path(os.environ["FAKE_SLURM_STATE"])


def load():
    return json.loads(STATE.read_text()) if STATE.exists() else {"next": 1000, "jobs": {}}


def save(st):
    STATE.write_text(json.dumps(st, indent=1))


def sbatch(args):
    opts, script = {}, None
    i = 0
    while i < len(args):
        a = args[i]
        if a.startswith("--") and "=" in a:
            k, v = a[2:].split("=", 1)
            opts[k] = v
        elif a.startswith("--"):
            opts[a[2:]] = True
        else:
            script = a
        i += 1
    st = load()
    jid = str(st["next"])
    st["next"] += 1
    st["jobs"][jid] = {"opts": opts, "script": script, "state": "PENDING"}
    save(st)
    print(jid)


def parse_export(spec):
    env = dict(os.environ)
    for item in spec.split(",")[1:]:                     # "ALL,K=V,..."
        k, v = item.split("=", 1)
        env[k] = v
    return env


def drain():
    st = load()
    for jid in sorted(st["jobs"], key=int):
        job = st["jobs"][jid]
        dep = job["opts"].get("dependency")
        if dep:
            kind, *ids = dep.split(":")
            states = [st["jobs"][i]["state"] for i in ids]
            if kind == "afterok" and any(s != "COMPLETED" for s in states):
                job["state"] = "CANCELLED"
                save(st)
                continue
        env = parse_export(job["opts"]["export"])
        env["SLURM_JOB_ID"] = jid
        name = job["opts"].get("job-name", "job")
        out = job["opts"]["output"].replace("%x", name).replace("%j", jid)
        err = job["opts"]["error"].replace("%x", name).replace("%j", jid)
        t0 = time.time()
        with open(out, "w") as fo, open(err, "w") as fe:
            rc = subprocess.run(["bash", job["script"]], env=env, cwd=job["opts"]["chdir"],
                                stdout=fo, stderr=fe).returncode
        job.update(state="COMPLETED" if rc == 0 else "FAILED", exit=rc,
                   elapsed=max(1, int(round(time.time() - t0))))
        save(st)


def sacct(args):
    ids = args[args.index("-j") + 1].split(",")
    fields = args[args.index("-o") + 1].split(",")
    over = json.loads(os.environ.get("FAKE_SLURM_OVERRIDES", "{}"))
    st = load()
    print("|".join(fields))
    for jid in ids:
        job = st["jobs"][jid]
        name = job["opts"].get("job-name", "job")
        o = over.get(name, {})
        bill = o.get("billing", 256 if name in ("sb1_UL", "sb1_SL") else 64)
        base = {"JobID": jid, "JobName": name, "State": job["state"],
                "ElapsedRaw": str(o.get("ElapsedRaw", job.get("elapsed", 0))),
                "MaxRSS": "", "MaxDiskRead": "",
                "AllocTRES": f"billing={bill},cpu={bill},mem=1M,node=1",
                "ExitCode": f"{job.get('exit', 0)}:0"}
        print("|".join(base.get(f, "") for f in fields))
        batch = dict(base, JobID=f"{jid}.batch", JobName="batch",
                     MaxRSS=o.get("MaxRSS", "1000K"), MaxDiskRead=o.get("MaxDiskRead", "1000K"))
        print("|".join(batch.get(f, "") for f in fields))


if __name__ == "__main__":
    cmd, rest = sys.argv[1], sys.argv[2:]
    {"sbatch": sbatch, "drain": lambda _: drain(), "sacct": sacct}[cmd](rest)

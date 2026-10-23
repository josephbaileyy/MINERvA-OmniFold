"""IBU-1 product meta checks and writer attribution (BINDING-C.md ruling 2).

For every product in ``--products``, check its meta against the bound ``config.json`` through the bound code's own
``unit_seeds`` and ``comparator_path`` (imported from the deploy, not retyped), and attribute it to the job whose task
log printed it. Code and input digests are not recorded per product: ``ibu1.py`` checks them at process start and
refuses (exit 4) before any write, so they are attested per writing job, from its task logs, in ``jobs``: no
refusal line, and every OI-136 guard line reports ``outside_expect_root=0`` (all code loaded from the pinned deploy).

Prints one JSON document and exits 1 if any product fails, is attributed to no job or to more than one, or if a
writing job's log shows a refusal.
"""
import argparse
import hashlib
import importlib.util
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

SCHEMA = {"experiments": "ibu1-experiment/1", "bootstrap": "ibu1-bootstrap/1", "data": "ibu1-data/1"}
LOG = re.compile(r"^task-(?P<task>.+)-(?P<job>\d+)\.log$")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 24), b""):
            h.update(block)
    return h.hexdigest()


def load_bound(code: Path):
    spec = importlib.util.spec_from_file_location("ibu1_bound", code)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def writers(logs: Path) -> tuple[dict, dict]:
    """(unit, seed-or-None) -> job ids whose task logs printed it; and per job, the refusals seen.

    ``run_data`` prints no per-product line, so a data unit's key is (task name, None) for each job with a log of
    that task whose guard finished (its ``[oi136] inventory`` line)."""
    seen, refusals, guard = defaultdict(set), defaultdict(list), defaultdict(list)
    for log in sorted(logs.iterdir()):
        m = LOG.match(log.name)
        if not m:
            continue
        job = m["job"]
        for line in log.read_text(errors="replace").splitlines():
            if line.startswith("[oi136] inventory:"):
                seen[("task", m["task"])].add(job)
                outside = re.search(r"outside_expect_root=(\d+)", line)
                guard[job].append(-1 if outside is None else int(outside[1]))
            if line.startswith("refusing"):
                refusals[job].append(f"{log.name}: {line}")
            if not line.startswith("{"):
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if "unit" in rec:
                seen[(rec["unit"], rec.get("seed"))].add(job)
    return seen, refusals, guard


def check(path: Path, units: dict, bound) -> dict:
    m = re.match(r"^(?P<unit>.+?)(_s(?P<seed>\d+))?\.npz$", path.name)
    unit_name, seed = m["unit"], None if m["seed"] is None else int(m["seed"])
    z = np.load(path, allow_pickle=False)
    meta = json.loads(str(z["meta"]))
    c = {"unit_known": unit_name in units}
    if not c["unit_known"]:
        return {"unit": unit_name, "seed": seed, "checks": c, "pass": False}
    u = units[unit_name]
    c["schema"] = meta.get("schema") == SCHEMA[u["kind"]]
    c["meta.unit"] = meta.get("unit") == unit_name
    c["meta.arm"] = meta.get("arm") == u["arm"]
    if u["kind"] == "experiments":
        pairs = dict(bound.unit_seeds(u))
        c["seed_declared"] = seed in pairs
        c["meta.pseudo_seed"] = meta.get("pseudo_seed") == seed
        c["meta.split_key"] = seed in pairs and meta.get("split_key") == pairs[seed]
        c["meta.truth"] = meta.get("truth") == u["truth"]
        c["meta.amplitude"] = meta.get("amplitude") == u["amplitude"]
        c["meta.ratio"] = meta.get("ratio") == u.get("ratio")
        cpath = bound.comparator_path(u, seed)
        gate = meta.get("comparator")
        if cpath is None:
            c["comparator_absent_as_declared"] = gate is None
        else:
            c["comparator_path"] = gate is not None and gate.get("path") == str(cpath)
            c["comparator_pass"] = gate is not None and gate.get("pass") is True
            c["f_of_present"] = "f_of" in z.files
    elif u["kind"] == "bootstrap":
        e = u["experiment"]
        c["meta.pseudo_seed"] = meta.get("pseudo_seed") == e["pseudo_seed"]
        c["meta.split_key"] = meta.get("split_key") == e["split_key"]
        c["meta.replicas"] = meta.get("replicas") == u["replicas"]
        n = u["replicas"][1] - u["replicas"][0] + 1
        c["replica_rows"] = all(z[k].shape[0] == n for k in z.files if k.startswith("F_"))
        c["comparator_pass"] = (meta.get("comparator") or {}).get("pass") is True
        c["controls_pass"] = all(v.get("pass", True) for v in (meta.get("controls") or {}).values())
    return {"unit": unit_name, "seed": seed, "checks": c, "pass": all(c.values())}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--code", type=Path, required=True, help="deployed nd-unfolding/ibu1/ibu1.py")
    ap.add_argument("--config", type=Path, required=True, help="deployed nd-unfolding/ibu1/config.json")
    ap.add_argument("--products", type=Path, required=True)
    ap.add_argument("--logs", type=Path, required=True)
    ap.add_argument("--jobs", required=True, help="name=jobid,... for the jobs that may have written products")
    a = ap.parse_args()
    bound = load_bound(a.code)
    units = {u["name"]: u for u in json.loads(a.config.read_text())["units"]}
    jobs = dict(kv.split("=") for kv in a.jobs.split(","))
    names = {v: k for k, v in jobs.items()}
    seen, refusals, guard = writers(a.logs)
    rows, ok = [], True
    for p in sorted(a.products.glob("*.npz")):
        r = check(p, units, bound)
        key = ("task", r["unit"]) if units.get(r["unit"], {}).get("kind") == "data" else (r["unit"], r["seed"])
        by = sorted(seen.get(key, set()))
        r.update(file=str(p.resolve()), sha256=sha256(p), mtime=p.stat().st_mtime, writer=[names.get(j, j) for j in by])
        r["attributed"] = len(by) == 1 and by[0] in names
        r["pass"] = r["pass"] and r["attributed"]
        ok &= r["pass"]
        rows.append(r)
    job_rows = {n: {"jobid": j, "refusals": refusals.get(j, []), "guard_lines": len(guard.get(j, [])),
                    "guard_outside_expect_root_nonzero": sum(1 for x in guard.get(j, []) if x != 0),
                    "products": sum(1 for r in rows if r["writer"] == [n])} for n, j in jobs.items()}
    ok &= all(not v["refusals"] and not v["guard_outside_expect_root_nonzero"] for v in job_rows.values())
    fails = [r["file"] for r in rows if not r["pass"]]
    print(json.dumps({"pass": ok, "products_dir": str(a.products.resolve()), "logs_dir": str(a.logs.resolve()),
                      "n_products": len(rows), "failing": fails, "jobs": job_rows, "products": rows}, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

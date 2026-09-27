#!/usr/bin/env python3
"""s5p Stage 7: generate the production task tables, queues and evaluator design from one frozen spec.

Nothing here computes. From ``--spec`` (JSON: the common s5p_nullexp inputs, the nulls with their hypothesis
files, prediction files and seed bases, the power alternatives, the batch geometry, the queue parameters and
the evaluator inputs) it writes, deterministically:

* per null and batch b: ``<out>/tables/cal-<null>-b<b>.tsv`` (lines of ``per_line`` seeds; batch b covers seeds
  base + batch*b ... base + min(batch*(b+1), max) - 1);
* per power alternative and amplitude: ``<out>/tables/pow-<key>-a<amp>.tsv``;
* per null a queue ``<out>/queues/cal-<null>.q``: for each batch, one line that runs the sequential controller
  (``s5p_seqstop.py``; exit 0 continue, 3 stopped) and, if it continues, submits the batch through the meter,
  then one line that waits for the batch's job to leave the scheduler; a final controller line records the
  stop at the maximum;
* a power queue ``<out>/queues/pow.q``;
* the evaluator design ``<out>/design.json`` (``s5p_joint.py evaluate``; calibration counts from the
  controllers' final status files).

Seed ranges are checked disjoint across every table before anything is written (F3: implementation guard).

MEASURES: nothing. CANNOT AUTHORIZE: any launch (the meter admits; the queues run only from a clean deploy).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def seeds_of_batch(base: int, b: int, batch: int, mx: int) -> range:
    return range(base + batch * b, base + min(batch * (b + 1), mx))


def lines_for(seeds: range, per_line: int) -> list[tuple[int, int]]:
    s = list(seeds)
    return [(s[i], s[min(i + per_line, len(s)) - 1]) for i in range(0, len(s), per_line)]


def task_line(name: str, common: list[str], extra: list[str], first: int, last: int, tag: str, out: str) -> str:
    return "\t".join([name, "s5p_nullexp.py", *common, *extra, "--pseudo-seeds", f"{first}:{last}", "--tag", tag, "--out", out])


def submit(spec: dict, table: str, label: str, ntasks: int, measures: str) -> str:
    q = spec["queue"]
    return (f'cd "$S5C_DEPLOY" && /usr/bin/python3.11 nd-unfolding/s5c_meter.py --budget {q["budget"]} --ledger {q["ledger"]} submit '
            f'--stage {q["stage"]} --pool {q["pool"]} --qos {q["qos"]} --ntasks {ntasks} --throttle {q["throttle"]} '
            f'--timelimit-h {q["timelimit_h"]} --billing {q["billing"]} --label {label} --measures "{measures}" '
            f'--cannot-authorize "a p-value, rejection, size or power verdict by itself" -- -C cpu --cpus-per-task=32 --mem=56G '
            f'--output={q["logs"]}/%x-%A_%a.out "$S5C_DEPLOY/nd-unfolding/s5c_array.sh" "$S5C_DEPLOY" "$S5C_PIN" '
            f'"$S5C_DEPLOY/{table}" {q["products"]}')


def controller(rel: str, ctl: dict, key: str, extra: str = "") -> str:
    """The controller runs in the analysis environment (numpy, scipy) from the deploy root, so the design's
    repo-relative paths resolve; the environment is sourced in a subshell, never piped."""
    return (f'(cd "$S5C_DEPLOY" && source ./setup_salloc_env.sh > /dev/null 2>&1; PYTHONPATH=nd-unfolding python3 nd-unfolding/s5p_seqstop.py '
            f'--design {rel}/design.json --v {ctl["v"]} --null {key} --status-dir {ctl["status_dir"]}{extra})')


def wait_line(label: str) -> str:
    """Wait until the batch's job has left the scheduler; a failed squeue counts as 'not yet' (review round 2
    M6: an empty answer from a failed query must not end the wait)."""
    return (f'until out=$(squeue -h --me -n s5p-{label} 2>/dev/null) && [ -z "$out" ]; do sleep 120; done; '
            f'echo "s5p-{label} left the scheduler"')


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--spec", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True, help="repo-relative directory (docs/orchestration/state/s5p/prod)")
    a = ap.parse_args(argv)
    spec = json.loads(a.spec.read_text())
    g = spec["geometry"]
    batch, per_line, mx = int(g["batch"]), int(g["per_line"]), int(g["max"])
    nb = -(-mx // batch)
    used: list[tuple[int, int, str]] = []
    tables: dict[str, list[str]] = {}
    queues: dict[str, list[str]] = {}
    rel = a.out.as_posix().rstrip("/")
    ctl = spec["controller"]
    ve = spec.get("v_ensemble")
    if ve:
        seeds = range(int(ve["seed_base"]), int(ve["seed_base"]) + int(ve["n"]))
        used.append((seeds.start, seeds.stop - 1, "v-ensemble"))
        out = f"{spec['products_root']}/v/null_mnvtune"
        rows = [task_line(f"v-ensemble_{i}", spec["common_args"], ["--hypothesis", spec["nulls"]["MnvTune_v1"]["hypothesis"]], f, l,
                          "v_mnvtune", out) for i, (f, l) in enumerate(lines_for(seeds, per_line))]
        tables["tables/v-ensemble.tsv"] = [f"# s5p production: the V ensemble (MnvTune null, seeds {seeds.start}-{seeds.stop - 1}); used ONLY to build V, never as calibration"] + rows
        queues["queues/v.q"] = [f"# s5p production: the V ensemble. Run with S5C_NS={spec['ns']}.",
                                submit(spec, f"{rel}/tables/v-ensemble.tsv", "s5p_prod_v", len(rows), "s5p production V ensemble (the metric; power only)"),
                                wait_line("s5p_prod_v")]
    for key, n in spec["nulls"].items():
        q = [f"# s5p production calibration of the null {key} (batch-sequential; generated by nd-unfolding/s5p_production.py). Run with S5C_NS={spec['ns']}."]
        if ve:
            q.append(f'until [ -e {ctl["v"]} ]; do sleep 300; done; echo "V present"')
        for b in range(nb):
            seeds = seeds_of_batch(int(n["seed_base"]), b, batch, mx)
            used.append((seeds.start, seeds.stop - 1, f"{key}-b{b}"))
            name = f"cal-{key}-b{b}"
            out = f"{spec['products_root']}/cal/{key}"
            rows = [task_line(f"{name}_{i}", spec["common_args"], ["--hypothesis", n["hypothesis"]], f, l, f"cal_{key}", out)
                    for i, (f, l) in enumerate(lines_for(seeds, per_line))]
            tables[f"tables/{name}.tsv"] = [f"# s5p production: calibration batch {b} of {key}, seeds {seeds.start}-{seeds.stop - 1}"] + rows
            label = f"s5p_cal_{key}_b{b}"
            q.append(f'rc=0; {controller(rel, ctl, key)} || rc=$?; '
                     f'if [ $rc = 0 ]; then m=0; {submit(spec, f"{rel}/tables/{name}.tsv", label, len(rows), f"s5p production calibration {key} batch {b}")} || m=$?; '
                     f'if [ $m = 3 ]; then {controller(rel, ctl, key, " --force-stop budget")}; [ $? = 3 ] || exit 9; elif [ $m != 0 ]; then exit $m; fi; '
                     f'elif [ $rc = 3 ]; then echo "{key} stopped before batch {b}"; else exit $rc; fi')
            q.append(wait_line(label))
        q.append(f'rc=0; {controller(rel, ctl, key, ' --force-stop "batches exhausted"')} || rc=$?; [ $rc = 3 ] || exit 9')
        queues[f"queues/cal-{key}.q"] = q
    pq = [f"# s5p production power ensembles (generated by nd-unfolding/s5p_production.py). Run with S5C_NS={spec['ns']}."]
    power = {}
    for key, p in spec["power"].items():
        for amp in p["amplitudes"]:
            n_amp = int(p["n"])
            base = int(p["seed_base"]) + int(round(1000 * float(amp)))
            seeds = range(base, base + n_amp)
            tag = f"{key}_a{amp}"
            used.append((seeds.start, seeds.stop - 1, f"pow-{tag}"))
            name = f"pow-{tag}"
            out = f"{spec['products_root']}/pow/{tag}"
            null_key = p.get("null", "MnvTune_v1")
            extra = ["--hypothesis", spec["nulls"][null_key]["hypothesis"], "--alternative", p["ratio"],
                     "--alternative-truth", p["truth"], "--alternative-amplitude", str(amp)]
            rows = [task_line(f"{name}_{i}", spec["common_args"], extra, f, l, f"pow_{tag}", out) for i, (f, l) in enumerate(lines_for(seeds, per_line))]
            tables[f"tables/{name}.tsv"] = [f"# s5p production: power alternative {key} at amplitude {amp}, seeds {seeds.start}-{seeds.stop - 1}"] + rows
            label = f"s5p_pow_{key}_a{str(amp).replace('.', 'p')}"
            pq.append(submit(spec, f"{rel}/tables/{name}.tsv", label, len(rows), f"s5p production power {key} a={amp}"))
            pq.append(wait_line(label))
            power[tag] = {"glob": f"{out}/pow_{tag}_s*.npz", "surrogate_seed0": base + 500000, "n": n_amp, "null": null_key}
    queues["queues/pow.q"] = pq
    used.sort()
    for (a0, a1, n0), (b0, b1, n1) in zip(used, used[1:]):
        if b0 <= a1:
            raise SystemExit(f"seed ranges overlap: {n0} {a0}-{a1} and {n1} {b0}-{b1}")
    design = dict(spec["evaluator"])
    if ve:
        design["v_ensemble_glob"] = f"{spec['products_root']}/v/null_mnvtune/v_mnvtune_s*.npz"
        design["v_ensemble_n"] = int(ve["n"])
    design["nulls"] = {key: {"prediction": n["prediction"], "domain": n.get("domain"),
                             "calibration_glob": f"{spec['products_root']}/cal/{key}/cal_{key}_s*.npz",
                             "calibration_n": {"max": mx, "sequential_status": f"{ctl['status_dir']}/{key}-final.json"},
                             "surrogate_seed0": int(n["seed_base"]) + 500000} for key, n in spec["nulls"].items()}
    design["power"] = {k: {"glob": v["glob"], "surrogate_seed0": v["surrogate_seed0"], "n": v["n"], "null": v["null"]}
                       for k, v in power.items()}
    a.out.mkdir(parents=True, exist_ok=True)
    for sub in ("tables", "queues"):
        (a.out / sub).mkdir(exist_ok=True)
    for path, rows in {**tables, **queues}.items():
        (a.out / path).write_text("\n".join(rows) + "\n")
    (a.out / "design.json").write_text(json.dumps(design, indent=1) + "\n")
    print(json.dumps({"tables": len(tables), "queues": len(queues), "seed_ranges": len(used),
                      "calibration_lines_max": sum(len(r) - 1 for k, r in tables.items() if "/cal-" in k)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

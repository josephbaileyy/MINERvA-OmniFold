#!/usr/bin/env python3
"""s5p report-only lost-seed recovery (owner decision 2026-10-05, DECISION-20261005-...-lost-seed-recovery.md §2).

Subcommands:
- ``tables``: write task tables that rerun exactly the given seeds, each with its frozen row's arguments.
  - Only ``--pseudo-seeds`` (one seed per task) and ``--out`` (the recovery directory) change; the task name gains
    ``-s<seed>-rec``. Every other argument is byte-identical to the frozen row whose seed range contains the seed.
  - Phase ``determinism`` reruns a fixed, pre-declared set of already-completed seeds:
    - per calibration null, the smallest completed seed of its first batch and the last batch's completed seed that
      ran latest in its task;
    - per power lane, its completed seed that ran latest in its task.
  - Phase ``recovery`` reruns every seed that ``seed-states.json`` classifies as interrupted or never started.
  - Phase ``retry`` reruns the seeds of ``--seeds-file``. It comes from ``missing`` (recovery seeds with no finished
    product).
- ``missing``: the manifest seeds that have no finished product in their recovery directory.
- ``determinism``: compare each rerun product with its original (criterion fixed before the check runs).
  - Every non-``meta`` array must be bitwise identical, in dtype, shape and bytes.
  - The ``meta`` JSON must be equal after removing exactly the per-run fields in ``VOLATILE``.
  - The rerun's ``slurm_job`` must be one of the determinism array's task ids and must differ from the original's.
  - The original and the rerun must be different files.
  - Anything else is FAIL, reported per seed. No tolerance is applied after the fact.
- ``resolve``: build union directories (symlinks to every frozen product plus the recovered ones). Write a
  report-only copy of the design whose globs name the unions and whose counts are the union counts.
  - Each lane's union must equal its submitted seeds minus an explicit ``--residual`` list (seeds lost twice).
  - Each recovered product's provenance (pseudo seed, code and input sha256, hypothesis and alternative sha256) must
    match the lane's frozen products.
- ``frozen-s``: the recovered draws scored against each null's FROZEN shift variants (the S built from the frozen
  calibration ensemble).
  - It first re-derives the frozen null T arrays through ``s5p_joint.test_null`` and requires them to reproduce
    ``joint-evaluate.json``'s k and B exactly.
  - It then counts the recovered draws at or above the observed statistic in every claim and robustness variant.
  - It gives the complete-set claim p and the Holm-with-determinacy decisions, plus the worst and best corners for
    any residual missing draws.
- ``stopping``: the frozen sequential rule (``s5p_inference.sequential_decision``, with ``s5p_seqstop``'s thresholds
  and minimum) re-applied at each frozen look, to the complete products of the batches before that look. Each look
  records whether it reproduces the frozen status file's k, B and stop. Run on the FROZEN design (no recovered
  products), every look must reproduce, which is the Phase 0 self-validation.

Recovered products never enter the production directories or the frozen globs. The frozen evaluation, its B and its
primary decisions are unchanged.

MEASURES: the outcomes of the lost draws, labelled as a report-only resolution of the missing-seed sensitivity.
CANNOT AUTHORIZE: a revised primary decision, a change to any frozen rule, or any submission (the meter and the
procedure govern those).
"""
from __future__ import annotations

import argparse
import glob as _glob
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

LOST_STATES = ("interrupted", "never started")
NS = "/pscratch/sd/j/josephrb/s5p-20260926"
VOLATILE_TOP = ("slurm_job", "seconds_unfold")   # per-run fields written by s5p_nullexp.py
VOLATILE_NESTED = ("refinement", "seconds")       # s5n_pseudo.refinement_evidence's wall time
PROVENANCE = ("code_sha256", "input_npz_sha256", "bkg_dump_sha256", "schema", "config", "iters", "capacity")


# ------------------------------------------------------------------------------------------------ tables

def read_table(path: Path) -> tuple[str, list[list[str]]]:
    lines = path.read_text().splitlines()
    header = lines[0] if lines and lines[0].startswith("#") else ""
    rows = [ln.split("\t") for ln in lines if ln and not ln.startswith("#")]
    return header, rows


def arg(row: list[str], flag: str) -> str:
    i = row.index(flag)
    return row[i + 1]


def with_arg(row: list[str], flag: str, value: str) -> list[str]:
    if row.count(flag) != 1:
        raise SystemExit(f"{row[0]}: {flag} appears {row.count(flag)} times")
    i = row.index(flag)
    return row[:i + 1] + [value] + row[i + 2:]


def seed_rows(tables_dir: Path) -> dict[int, tuple[str, list[str]]]:
    """seed -> (table name, frozen row), over every production table; a seed in two rows is an error."""
    out: dict[int, tuple[str, list[str]]] = {}
    for t in sorted(tables_dir.glob("*.tsv")):
        _, rows = read_table(t)
        for row in rows:
            first, last = (int(v) for v in arg(row, "--pseudo-seeds").split(":"))
            for s in range(first, last + 1):
                if s in out:
                    raise SystemExit(f"seed {s} in two rows: {out[s][1][0]} and {row[0]}")
                out[s] = (t.name, row)
    return out


def lane_of(task_lane: str) -> tuple[str, str]:
    """'cal-GENIE_2_12_10_CV' -> ('cal', 'GENIE_2_12_10_CV'); 'pow-P1_a1.0' -> ('pow', 'P1_a1.0')."""
    kind, _, name = task_lane.partition("-")
    if kind not in ("cal", "pow") or not name:
        raise SystemExit(f"unknown lane {task_lane!r}")
    return kind, name


def classify(seed_states: dict) -> dict[str, dict[str, list[int]]]:
    """lane -> state -> sorted seeds, from the frozen task-log classification."""
    out: dict[str, dict[str, list[int]]] = {}
    for t in seed_states["tasks"]:
        for s, st in t["seeds"].items():
            out.setdefault(t["lane"], {}).setdefault(st["state"], []).append(int(s))
    for lane in out:
        for st in out[lane]:
            out[lane][st].sort()
    return out


def batch_of(table_name: str) -> int:
    return int(table_name.rsplit("-b", 1)[1].split(".")[0])


def latest(seeds: list[int], positions: dict[int, int]) -> int:
    return min(seeds, key=lambda s: (-positions[s], s))


def determinism_seeds(cls: dict, rows: dict, positions: dict[int, int]) -> list[int]:
    """Calibration: per null, the smallest completed seed of its first batch (it ran first in its task) and the last
    batch's completed seed that ran latest in its task. Power: per lane, the completed seed that ran latest in its
    task. A rerun runs every seed first in a fresh process, so a late-position seed tests that a product does not
    depend on what ran before it; the power seeds cover the --alternative code path."""
    chosen = []
    for lane in sorted(k for k in cls if k.startswith("cal-")):
        done = cls[lane].get("completed", [])
        batches = sorted({batch_of(rows[s][0]) for s in done})
        chosen.append(min(s for s in done if batch_of(rows[s][0]) == batches[0]))
        chosen.append(latest([s for s in done if batch_of(rows[s][0]) == batches[-1]], positions))
    for lane in sorted(k for k in cls if k.startswith("pow-")):
        chosen.append(latest(cls[lane].get("completed", []), positions))
    return chosen


def cmd_tables(a) -> int:
    seed_states = json.loads(a.seed_states.read_text())
    cls = classify(seed_states)
    rows = seed_rows(a.tables)
    positions = {int(s): int(st["position"]) for t in seed_states["tasks"] for s, st in t["seeds"].items()}
    if a.phase == "determinism":
        seeds = determinism_seeds(cls, rows, positions)
    elif a.phase == "recovery":
        seeds = sorted(s for lane in cls for st in LOST_STATES for s in cls[lane].get(st, []))
    else:
        if a.seeds_file is None:
            raise SystemExit("phase retry needs --seeds-file")
        seeds = sorted(int(s) for s in json.loads(a.seeds_file.read_text()))
        lost = {s for lane in cls for st in LOST_STATES for s in cls[lane].get(st, [])}
        if not set(seeds) <= lost:
            raise SystemExit(f"retry seeds that were never lost: {sorted(set(seeds) - lost)[:10]}")
    by_lane: dict[str, list[list[str]]] = {}
    lane_by_seed = {s: lane for lane in cls for st in cls[lane] for s in cls[lane][st]}
    for s in seeds:
        if s not in rows:
            raise SystemExit(f"seed {s} is in no frozen table row")
        lane = lane_by_seed[s]
        kind, name = lane_of(lane)
        tname, row = rows[s]
        out_dir = f"{a.root}/{a.phase}/{kind}/{name}"
        if a.phase == "retry":  # a retried seed writes where its first recovery attempt would have
            out_dir = f"{a.root}/recovery/{kind}/{name}"
        if arg(row, "--out").rstrip("/") == out_dir.rstrip("/"):
            raise SystemExit("the recovery directory equals a production directory")
        new = with_arg(with_arg(row, "--pseudo-seeds", f"{s}:{s}"), "--out", out_dir)
        new[0] = f"{row[0]}-s{s}-rec"
        by_lane.setdefault(lane, []).append(new)
    a.out_dir.mkdir(parents=True, exist_ok=True)
    manifest = {"phase": a.phase, "seed_states_sha256": hashlib.sha256(a.seed_states.read_bytes()).hexdigest(),
                "root": a.root, "tables": {}}
    for lane, rs in sorted(by_lane.items()):
        p = a.out_dir / f"rec-{a.phase}-{lane}.tsv"
        if p.exists():
            raise SystemExit(f"refusing to overwrite {p}")
        p.write_text(f"# s5p report-only {a.phase} rerun of {len(rs)} seeds of {lane} (frozen rows; only "
                     f"--pseudo-seeds and --out changed)\n" + "\n".join("\t".join(r) for r in rs) + "\n")
        manifest["tables"][p.name] = {"lane": lane, "n": len(rs),
                                      "seeds": [int(arg(r, "--pseudo-seeds").split(":")[0]) for r in rs]}
    total = sum(v["n"] for v in manifest["tables"].values())
    manifest["n_seeds"] = total
    # submission tables: every row is self-contained (its own --out), so lanes may share an array; split into
    # --parts near-equal parts so that the meter's per-array reservation (ntasks x time limit x billing) fits.
    allrows = [r for lane in sorted(by_lane) for r in by_lane[lane]]
    k, parts = a.parts, []
    for i in range(k):
        chunk = allrows[i * len(allrows) // k:(i + 1) * len(allrows) // k]
        p = a.out_dir / f"rec-{a.phase}-part{i + 1}.tsv"
        if p.exists():
            raise SystemExit(f"refusing to overwrite {p}")
        p.write_text(f"# s5p report-only {a.phase} rerun, part {i + 1} of {k}: {len(chunk)} tasks, one seed each\n"
                     + "\n".join("\t".join(r) for r in chunk) + "\n")
        parts.append({"table": p.name, "ntasks": len(chunk), "first": chunk[0][0], "last": chunk[-1][0]})
    if sum(x["ntasks"] for x in parts) != total:
        raise SystemExit("parts do not cover every row")
    manifest["submission_parts"] = parts
    (a.out_dir / f"rec-{a.phase}-manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    print(json.dumps({k: v["n"] for k, v in manifest["tables"].items()}), "total", total)
    return 0


def product_path(root: str, phase_dir: str, lane: str, tag: str, seed: int) -> Path:
    kind, name = lane_of(lane)
    return Path(root) / phase_dir / kind / name / f"{tag}_s{seed}.npz"


def cmd_missing(a) -> int:
    man = json.loads(a.manifest.read_text())
    rows = seed_rows(a.tables)
    miss = [s for t in man["tables"].values() for s in t["seeds"]
            if not product_path(man["root"], "recovery", t["lane"], arg(rows[s][1], "--tag"), s).exists()]
    a.out.write_text(json.dumps(sorted(miss)) + "\n")
    print(len(miss), "recovery seeds without a finished product")
    return 0


# ------------------------------------------------------------------------------------------- determinism

def load_meta(npz) -> dict:
    return json.loads(str(npz["meta"]))


def strip_volatile(meta: dict) -> dict:
    """A copy of ``meta`` without exactly the per-run fields (VOLATILE_TOP at the top level, ``seconds`` inside any
    ``refinement`` dict). Everything else stays and must match."""
    def walk(o, parent=None):
        if isinstance(o, dict):
            return {k: walk(v, k) for k, v in o.items()
                    if not (parent is None and k in VOLATILE_TOP)
                    and not (parent == VOLATILE_NESTED[0] and k == VOLATILE_NESTED[1])}
        if isinstance(o, list):
            return [walk(v, parent) for v in o]
        return o
    return walk(meta)


def products_equivalent(p1: Path, p2: Path) -> tuple[bool, list[str], dict, dict]:
    a, b = np.load(p1, allow_pickle=False), np.load(p2, allow_pickle=False)
    diffs = []
    if sorted(a.files) != sorted(b.files):
        diffs.append(f"keys differ: {sorted(set(a.files) ^ set(b.files))}")
    for k in sorted((set(a.files) & set(b.files)) - {"meta"}):
        x, y = a[k], b[k]
        if x.dtype != y.dtype or x.shape != y.shape or x.tobytes() != y.tobytes():
            d = ""
            if x.shape == y.shape and np.issubdtype(x.dtype, np.number) and np.issubdtype(y.dtype, np.number):
                den = np.maximum(np.abs(x.astype(float)), 1e-300)
                d = f" max|rel diff| {float(np.max(np.abs(x.astype(float) - y.astype(float)) / den)):.3e}"
            diffs.append(f"{k}: not bitwise identical{d}")
    ma, mb = (load_meta(a), load_meta(b)) if "meta" in a.files and "meta" in b.files else ({}, {})
    if "meta" in a.files and "meta" in b.files:
        sa, sb = strip_volatile(ma), strip_volatile(mb)
        if sa != sb:
            keys = sorted(k for k in set(sa) | set(sb) if sa.get(k) != sb.get(k))
            diffs.append(f"meta differs beyond the volatile fields in: {keys}")
    return not diffs, diffs, ma, mb


def cmd_determinism(a) -> int:
    man = json.loads(a.manifest.read_text())
    rows = seed_rows(a.tables)
    allowed = {str(x).strip() for x in a.job_ids.read_text().split() if str(x).strip()}
    if not allowed:
        raise SystemExit("no determinism array task ids given")
    res, ok = {}, True
    for t in man["tables"].values():
        for s in t["seeds"]:
            orig_row = rows[s][1]
            tag = arg(orig_row, "--tag")
            orig = Path(arg(orig_row, "--out")) / f"{tag}_s{s}.npz"
            rerun = product_path(man["root"], man["phase"], t["lane"], tag, s)
            r = {"orig": str(orig), "rerun": str(rerun)}
            if not orig.exists() or not rerun.exists():
                r.update(identical=False, diffs=[f"missing: orig {orig.exists()} rerun {rerun.exists()}"])
            elif orig.resolve() == rerun.resolve():
                r.update(identical=False, diffs=["the original and the rerun are the same file"])
            else:
                same, diffs, mo, mr = products_equivalent(orig, rerun)
                job = mr.get("slurm_job")
                if job is None or str(job) not in allowed:
                    same, diffs = False, diffs + [f"rerun slurm_job {job!r} is not a determinism array task id"]
                if job is not None and str(job) == str(mo.get("slurm_job")):
                    same, diffs = False, diffs + ["rerun slurm_job equals the original's"]
                r.update(identical=same, diffs=diffs, rerun_slurm_job=job, orig_slurm_job=mo.get("slurm_job"))
            res[str(s)] = r
            ok &= r["identical"]
    out = {"criterion": ("every non-meta array bitwise identical; meta equal after removing exactly "
                         f"{list(VOLATILE_TOP)} and {VOLATILE_NESTED[0]}.{VOLATILE_NESTED[1]}; the rerun's "
                         "slurm_job a determinism task id different from the original's; distinct files "
                         "(fixed in advance)"),
           "n": len(res), "verdict": "PASS" if ok and len(res) == man["n_seeds"] else "FAIL", "seeds": res}
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    print(out["verdict"], f"{sum(r['identical'] for r in res.values())}/{len(res)} equivalent")
    return 0 if out["verdict"] == "PASS" else 1


# --------------------------------------------------------------------------------------------- resolve

def seed_of(p: Path) -> int:
    return int(p.name.rsplit("_s", 1)[1].split(".")[0])


def finished(pattern: str) -> list[Path]:
    return sorted(Path(p) for p in _glob.glob(pattern) if ".partial" not in Path(p).name)


def provenance(meta: dict) -> dict:
    out = {k: meta.get(k) for k in PROVENANCE}
    out["hypothesis_sha256"] = (meta.get("hypothesis") or {}).get("sha256")
    alt = meta.get("alternative")
    out["alternative"] = None if alt is None else {k: alt.get(k) for k in ("sha256", "truth", "amplitude")}
    return out


def cmd_resolve(a) -> int:
    design = json.loads(a.design.read_text())
    man = json.loads(a.manifest.read_text())
    cls = classify(json.loads(a.seed_states.read_text()))
    residual = set(int(s) for s in json.loads(a.residual.read_text())) if a.residual else set()
    recovered_by_lane: dict[str, set[int]] = {}
    for t in man["tables"].values():
        recovered_by_lane.setdefault(t["lane"], set()).update(t["seeds"])
    if a.union_root.exists():
        raise SystemExit(f"refusing to reuse {a.union_root}")
    new = json.loads(json.dumps(design))
    report = {}
    specs = [("cal", k, v, "calibration_glob") for k, v in design["nulls"].items()] + \
            [("pow", k, v, "glob") for k, v in design.get("power", {}).items()]
    for kind, key, spec, gk in specs:
        lane = f"{kind}-{key}"
        frozen = finished(spec[gk])
        pattern = Path(spec[gk])
        rec_dir = Path(man["root"]) / "recovery" / kind / key
        rec = sorted(p for p in rec_dir.glob(pattern.name) if ".partial" not in p.name) if rec_dir.is_dir() else []
        submitted = set(s for st in cls.get(lane, {}).values() for s in st)
        lost = set(s for st in LOST_STATES for s in cls.get(lane, {}).get(st, []))
        f_seeds, r_seeds = [seed_of(p) for p in frozen], [seed_of(p) for p in rec]
        if set(f_seeds) & set(r_seeds):
            raise SystemExit(f"{lane}: a seed is both frozen and recovered")
        if set(r_seeds) != recovered_by_lane.get(lane, set()) - residual:
            raise SystemExit(f"{lane}: recovered {len(r_seeds)} != manifest {len(recovered_by_lane.get(lane, set()))}"
                             f" - residual")
        if set(f_seeds) | set(r_seeds) != submitted - residual or not residual & submitted <= lost:
            raise SystemExit(f"{lane}: union {len(set(f_seeds) | set(r_seeds))} != submitted {len(submitted)} "
                             f"- residual {len(residual & submitted)}")
        ref = {json.dumps(provenance(json.loads(str(np.load(p, allow_pickle=False)["meta"]))), sort_keys=True)
               for p in frozen[:: max(1, len(frozen) // 20)]}
        if len(ref) != 1:
            raise SystemExit(f"{lane}: the frozen products' provenance is not uniform ({len(ref)} variants)")
        for p in rec:
            m = json.loads(str(np.load(p, allow_pickle=False)["meta"]))
            if int(m.get("pseudo_seed", -1)) != seed_of(p):
                raise SystemExit(f"{p}: pseudo_seed {m.get('pseudo_seed')} != file seed")
            if json.dumps(provenance(m), sort_keys=True) not in ref:
                raise SystemExit(f"{p}: provenance differs from the lane's frozen products")
        d = a.union_root / kind / key
        d.mkdir(parents=True)
        for p in frozen + rec:
            (d / p.name).symlink_to(p.resolve())
        new_spec = new["nulls"][key] if kind == "cal" else new["power"][key]
        new_spec[gk] = str(d / pattern.name)
        if kind == "cal":
            new_spec["calibration_n"] = len(frozen) + len(rec)
        else:
            new_spec["n"] = len(frozen) + len(rec)
        report[lane] = {"frozen": len(frozen), "recovered": len(rec), "union": len(frozen) + len(rec),
                        "submitted": len(submitted), "residual_missing": len(residual & submitted)}
    new["_report_only"] = ("resolution of the missing-seed sensitivity (DECISION-20261005 §2): the frozen design with "
                           "union globs and counts; not the frozen design, not a primary evaluation")
    a.out_design.write_text(json.dumps(new, indent=1) + "\n")
    (a.out_design.with_suffix(".report.json")).write_text(json.dumps(report, indent=1) + "\n")
    print(json.dumps(report))
    return 0


# ------------------------------------------------------------------------------- frozen-S and stopping

def _setup(design: dict, v_path: Path):
    import s5p_joint as sj
    stage1 = json.loads(Path(design["stage1"]).read_text())
    supported = json.loads(Path(design["s5c_contract"]).read_text())["measurement"]["partition_J"]["supported_cells"]
    U, names, pz_index = sj.j_matrix(stage1, supported)
    sj.check_v(design, v_path)
    V = np.asarray(np.load(v_path, allow_pickle=False)["V"], float)
    coefs = [float(c) for c in design.get("shift_coefficients", [0.0])]
    return sj, sj.Model(design, U), V, names, pz_index, coefs


def variant_shifts(sj, design: dict, key: str, names: list, S, coefs) -> tuple[list, list]:
    """Exactly test_null's claim variants and kappa_robust variants, in its order."""
    m1 = design.get("m1_shift", {}).get(key)
    claim = [(str(c), (c * S if S is not None else None)) for c in (coefs if S is not None else [0.0])]
    robust = []
    if m1 is not None and "none" not in m1:
        d1, _ = sj.load_shift({k: v for k, v in m1.items() if k in ("path", "sha256")}, len(names))
        claim += [(f"m1+{m1['kappa']}", m1["kappa"] * d1), (f"m1-{m1['kappa']}", -m1["kappa"] * d1)]
        robust = [(f"m1+{m1['kappa_robust']}", m1["kappa_robust"] * d1), (f"m1-{m1['kappa_robust']}", -m1["kappa_robust"] * d1)]
    return claim, robust


def counts_ge(t_obs: float, t: np.ndarray) -> int:
    return int(np.sum(np.asarray(t, float) >= t_obs))


def cmd_frozen_s(a) -> int:
    import s5p_inference as si
    design = json.loads(a.design.read_text())
    frozen_eval = json.loads(a.evaluate.read_text())
    man = json.loads(a.manifest.read_text())
    sj, model, V, names, pz_index, coefs = _setup(design, a.v)
    residual = set(int(s) for s in json.loads(a.residual.read_text())) if a.residual else set()
    out, claims, robust_claims, worst, best = {"tests": {}}, {}, {}, {}, {}
    for key, spec in design["nulls"].items():
        files = sj.product_files(spec["calibration_glob"])
        entry = sj.test_null(model, design, key, V, names, pz_index, files, coefs)
        nulls = entry.pop("_nulls")
        fe = frozen_eval["tests"][key]
        for s in ("total", "shape"):  # the re-derivation must reproduce the frozen evaluation exactly
            if (entry[s]["k"], entry[s]["B"]) != (fe[s]["k"], fe[s]["B"]):
                raise SystemExit(f"{key}:{s}: re-derived k, B {entry[s]['k']}, {entry[s]['B']} != frozen "
                                 f"{fe[s]['k']}, {fe[s]['B']}")
        spec_mu = sj.prediction(spec["prediction"], model.U)
        mu, var = spec_mu
        dom = np.ones(len(names), bool) if spec.get("domain") != "pz_lt_6" else (pz_index <= 1)
        F, seeds = sj.ensemble(model, files)
        pspec = design.get("process_shift", {}).get(key)
        D, d_pairs = sj.load_shift(pspec, len(names))
        S = sj.shift_vector(pspec, D, d_pairs, F, mu, var, V, dom)[0] if D is not None else None
        claim_v, robust_v = variant_shifts(sj, design, key, names, S, coefs)
        for (name, sv), (tt_n, ts_n) in zip(claim_v, nulls):  # the same shifts as the frozen nulls
            tt_c, ts_c = sj.statistics(F + (sv if sv is not None else 0.0), mu, var, V, dom, spec["surrogate_seed0"],
                                       seeds=seeds)
            if tt_c.tobytes() != tt_n.tobytes() or ts_c.tobytes() != ts_n.tobytes():
                raise SystemExit(f"{key} {name}: the re-derived frozen null T differs from test_null's")
        lane = f"cal-{key}"
        rec_seeds = sorted(s for t in man["tables"].values() if t["lane"] == lane for s in t["seeds"]
                           if s not in residual)
        rows = {s: r for s, r in seed_rows(a.tables).items() if s in rec_seeds}
        rec_files = [str(product_path(man["root"], "recovery", lane, arg(rows[s][1], "--tag"), s)) for s in rec_seeds]
        M_res = len([s for t in man["tables"].values() if t["lane"] == lane for s in t["seeds"] if s in residual])
        Fr, sr = sj.ensemble(model, rec_files) if rec_files else (np.zeros((0, F.shape[1])), np.zeros(0, np.int64))
        tt_o, ts_o = sj.statistics(model.f_data[None, :], mu, var, V, dom, 0, draw=False)
        tobs = {"total": float(tt_o[0]), "shape": float(ts_o[0])}
        per_variant = {}
        for group, vs in (("claim", claim_v), ("robust", robust_v)):
            for name, sv in vs:
                tn = sj.statistics(F + (sv if sv is not None else 0.0), mu, var, V, dom, spec["surrogate_seed0"],
                                   seeds=seeds)
                trc = sj.statistics(Fr + (sv if sv is not None else 0.0), mu, var, V, dom, spec["surrogate_seed0"],
                                    seeds=sr) if len(rec_files) else (np.zeros(0), np.zeros(0))
                per_variant[name] = {"group": group}
                for i, s in enumerate(("total", "shape")):
                    kf, kr = counts_ge(tobs[s], tn[i]), counts_ge(tobs[s], trc[i])
                    per_variant[name][s] = {"k_frozen": kf, "B_frozen": int(tn[i].size), "k_recovered": kr,
                                            "M_recovered": int(trc[i].size), "M_residual": M_res,
                                            "max_recovered_T": float(np.max(trc[i])) if trc[i].size else None,
                                            "T_obs": tobs[s]}
        res = {}
        for s in ("total", "shape"):
            def p_of(names_, extra_k=0, extra_b=0):
                best_ = None
                for n in names_:
                    v = per_variant[n][s]
                    k = v["k_frozen"] + v["k_recovered"] + extra_k
                    B = v["B_frozen"] + v["M_recovered"] + extra_b
                    p = (k + 1) / (B + 1)
                    if best_ is None or p > best_["p"]:
                        best_ = {"p": p, "k": k, "B": B, "variant": n}
                return best_
            cn = [n for n, _ in claim_v]
            rn = cn + [n for n, _ in robust_v]
            res[s] = {"claim": p_of(cn), "robust": p_of(rn),
                      "worst_residual": p_of(cn, M_res, M_res), "best_residual": p_of(cn, 0, M_res)}
            claims[f"{key}:{s}"] = {k: res[s]["claim"][k] for k in ("p", "k", "B")}
            robust_claims[f"{key}:{s}"] = {k: res[s]["robust"][k] for k in ("p", "k", "B")}
            worst[f"{key}:{s}"] = {k: res[s]["worst_residual"][k] for k in ("p", "k", "B")}
            best[f"{key}:{s}"] = {k: res[s]["best_residual"][k] for k in ("p", "k", "B")}
        out["tests"][key] = {"per_variant": per_variant, "complete_set": res,
                             "frozen_reproduced": {s: [fe[s]["k"], fe[s]["B"]] for s in ("total", "shape")}}
    alpha = design["alpha_family"]
    out["decisions_complete_set"] = si.holm_determined(claims, alpha)
    out["decisions_complete_set_kappa3"] = si.holm_determined(robust_claims, alpha)
    out["decisions_worst_residual"] = si.holm_determined(worst, alpha)
    out["decisions_best_residual"] = si.holm_determined(best, alpha)
    out["primary_decisions"] = {k: v["decision"] for k, v in frozen_eval["decisions"].items()}
    out["label"] = ("REPORT ONLY: the recovered draws scored against the FROZEN shift variants; the primary decisions "
                    "are those of the frozen evaluation")
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: v["decision"] for k, v in out["decisions_complete_set"].items()}))
    return 0


def cmd_stopping(a) -> int:
    import s5p_inference as si
    design = json.loads(a.design.read_text())  # the report-only union design (resolve)
    sj, model, V, names, pz_index, coefs = _setup(design, a.v)
    rows = seed_rows(a.tables)
    m = 2 * len(design["nulls"])
    th = sorted(set(si.holm_thresholds(design["alpha_family"], m)) | {0.01, 0.05})
    out = {}
    for key, spec in design["nulls"].items():
        frozen_spec = json.loads(a.frozen_design.read_text())["nulls"][key]
        min_b = int(frozen_spec["calibration_n"].get("min", 0))
        looks = sorted(json.loads(p.read_text()) for p in Path(a.status_dir).glob(f"{key}-B*.json"))
        files = [Path(p) for p in sj.product_files(spec["calibration_glob"])]
        batch = {p: batch_of(rows[seed_of(p)][0]) for p in files}
        res = []
        n_batches_seen = 0
        for look in sorted(looks, key=lambda st: st["B"]):
            if look["B"] == 0:
                continue
            n_batches_seen += 1  # a look follows each batch (the frozen queue: a look after every batch)
            sub = [str(p) for p in files if batch[p] < n_batches_seen]
            entry = sj.test_null(model, design, key, V, names, pz_index, sub, coefs)
            entry.pop("_nulls", None)
            dec = {s: si.sequential_decision(entry[s]["k"], entry[s]["B"], th) for s in ("total", "shape")}
            rule = all(d["stop"] for d in dec.values()) and len(sub) >= min_b
            fd = look.get("decisions", {})
            same_as_frozen = (len(sub) == look["B"] and all(
                (fd.get(s, {}).get("k"), fd.get(s, {}).get("B"), fd.get(s, {}).get("stop")) ==
                (dec[s]["k"], dec[s]["B"], dec[s]["stop"]) for s in ("total", "shape")))
            res.append({"frozen_look": f"{key}-B{look['B']}.json", "frozen_B": look["B"],
                        "reproduces_frozen_look": same_as_frozen,
                        "frozen_reason": look.get("reason"), "batches_before_look": n_batches_seen,
                        "complete_B": len(sub), "rule_stops_complete": rule,
                        "decisions": {s: {k: dec[s][k] for k in ("k", "B", "p", "look_interval", "stop")}
                                      for s in dec}})
        out[key] = res
    out["label"] = ("REPORT ONLY: the frozen sequential rule re-applied at each frozen look to the complete products "
                    "of the batches before it; the frozen stops are unchanged")
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: [r["rule_stops_complete"] for r in v] for k, v in out.items() if k != "label"}))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("tables")
    t.add_argument("--phase", choices=("determinism", "recovery", "retry"), required=True)
    t.add_argument("--seed-states", type=Path, required=True)
    t.add_argument("--tables", type=Path, required=True, help="the frozen production tables directory")
    t.add_argument("--root", default=f"{NS}/recovery")
    t.add_argument("--out-dir", type=Path, required=True)
    t.add_argument("--parts", type=int, default=1, help="number of submission tables (arrays)")
    t.add_argument("--seeds-file", type=Path, help="phase retry: a JSON list of seeds (from 'missing')")
    ms = sub.add_parser("missing")
    ms.add_argument("--manifest", type=Path, required=True)
    ms.add_argument("--tables", type=Path, required=True)
    ms.add_argument("--out", type=Path, required=True)
    d = sub.add_parser("determinism")
    d.add_argument("--manifest", type=Path, required=True)
    d.add_argument("--tables", type=Path, required=True)
    d.add_argument("--job-ids", type=Path, required=True,
                   help="every task id of the determinism array (sacct -j <array> -n -o JobID, both id forms)")
    d.add_argument("--out", type=Path, required=True)
    r = sub.add_parser("resolve")
    r.add_argument("--design", type=Path, required=True)
    r.add_argument("--manifest", type=Path, required=True)
    r.add_argument("--seed-states", type=Path, required=True)
    r.add_argument("--residual", type=Path, help="a JSON list of seeds lost twice (allowed to stay missing)")
    r.add_argument("--union-root", type=Path, required=True)
    r.add_argument("--out-design", type=Path, required=True)
    f = sub.add_parser("frozen-s")
    f.add_argument("--design", type=Path, required=True, help="the FROZEN design")
    f.add_argument("--evaluate", type=Path, required=True, help="the frozen joint-evaluate.json")
    f.add_argument("--v", type=Path, required=True)
    f.add_argument("--manifest", type=Path, required=True)
    f.add_argument("--tables", type=Path, required=True)
    f.add_argument("--residual", type=Path)
    f.add_argument("--out", type=Path, required=True)
    s = sub.add_parser("stopping")
    s.add_argument("--design", type=Path, required=True, help="the report-only union design from resolve")
    s.add_argument("--frozen-design", type=Path, required=True)
    s.add_argument("--v", type=Path, required=True)
    s.add_argument("--tables", type=Path, required=True)
    s.add_argument("--status-dir", type=Path, required=True)
    s.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if getattr(a, "out", None) is not None and a.cmd != "missing" and Path(a.out).exists():
        raise SystemExit(f"refusing to overwrite {a.out}")
    return {"tables": cmd_tables, "missing": cmd_missing, "determinism": cmd_determinism, "resolve": cmd_resolve,
            "frozen-s": cmd_frozen_s, "stopping": cmd_stopping}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())

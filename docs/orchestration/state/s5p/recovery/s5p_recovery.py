#!/usr/bin/env python3
"""s5p report-only lost-seed recovery (owner decision 2026-10-05, DECISION-20261005-...-lost-seed-recovery.md §2).

Subcommands:
- ``tables``: write task tables that rerun exactly the given seeds with their frozen rows' arguments.
  - Only ``--pseudo-seeds`` (one seed per task) and ``--out`` (the recovery directory) change; the task name gains a
    ``-rec`` suffix. Every other argument is byte-identical to the frozen row whose seed range contains the seed.
  - Phase ``determinism`` reruns a fixed, pre-declared set of already-completed calibration seeds (per null:
    the smallest completed seed of the first batch, and the last batch's completed seed that ran latest in its task;
    10 seeds). Phase ``recovery`` reruns every seed that
    ``seed-states.json`` classifies as interrupted or never started (calibration and power).
- ``determinism``: compare each rerun product with its original. PASS only if every array in both ``.npz`` files is
  bitwise identical (the criterion fixed before the check runs). Any difference is reported per seed and makes the
  result FAIL; no tolerance is applied after the fact.
- ``resolve``: build union directories (symlinks to every frozen product plus the recovered ones), write a
  report-only copy of the design whose globs name them and whose counts are the union counts, and require each
  union to equal the submitted seed set exactly. The frozen ``s5p_joint.py evaluate`` is then run on that copy by
  the procedure, not by this script.

Recovered products never enter the production directories or the frozen globs: the frozen evaluation, its B and its
primary decisions are unchanged. MEASURES: the outcomes of the lost draws. CANNOT AUTHORIZE: a revised primary
decision, a change to any frozen rule, or any submission (the meter and the procedure govern those).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

LOST_STATES = ("interrupted", "never started")
NS = "/pscratch/sd/j/josephrb/s5p-20260926"


def read_table(path: Path) -> tuple[str, list[list[str]]]:
    lines = path.read_text().splitlines()
    header = lines[0] if lines and lines[0].startswith("#") else ""
    rows = [ln.split("\t") for ln in lines if ln and not ln.startswith("#")]
    return header, rows


def arg(row: list[str], flag: str) -> str:
    i = row.index(flag)
    return row[i + 1]


def with_arg(row: list[str], flag: str, value: str) -> list[str]:
    i = row.index(flag)
    if row.count(flag) != 1:
        raise SystemExit(f"{row[0]}: {flag} appears {row.count(flag)} times")
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


def determinism_seeds(cls: dict, rows: dict, positions: dict[int, int]) -> list[int]:
    """For each calibration null: the smallest completed seed of its first batch (it ran first in its task), and the
    completed seed of its last batch that ran latest in its task (ties: the smallest seed). A rerun runs every seed
    first in a fresh process, so the second choice tests that a product does not depend on what ran before it."""
    chosen = []
    for lane in sorted(k for k in cls if k.startswith("cal-")):
        done = cls[lane].get("completed", [])
        batches = sorted({batch_of(rows[s][0]) for s in done})
        chosen.append(min(s for s in done if batch_of(rows[s][0]) == batches[0]))
        last = [s for s in done if batch_of(rows[s][0]) == batches[-1]]
        chosen.append(min(last, key=lambda s: (-positions[s], s)))
    return chosen


def cmd_tables(a) -> int:
    seed_states = json.loads(a.seed_states.read_text())
    cls = classify(seed_states)
    rows = seed_rows(a.tables)
    positions = {int(s): int(st["position"]) for t in seed_states["tasks"] for s, st in t["seeds"].items()}
    if a.phase == "determinism":
        seeds = determinism_seeds(cls, rows, positions)
    else:
        seeds = sorted(s for lane in cls for st in LOST_STATES for s in cls[lane].get(st, []))
    by_lane: dict[str, list[list[str]]] = {}
    lane_by_seed = {s: lane for lane in cls for st in cls[lane] for s in cls[lane][st]}
    for s in seeds:
        if s not in rows:
            raise SystemExit(f"seed {s} is in no frozen table row")
        lane = lane_by_seed[s]
        kind, name = lane_of(lane)
        tname, row = rows[s]
        out_dir = f"{a.root}/{a.phase}/{kind}/{name}"
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


def npz_identical(p1: Path, p2: Path) -> tuple[bool, list[str]]:
    a, b = np.load(p1, allow_pickle=False), np.load(p2, allow_pickle=False)
    diffs = []
    if sorted(a.files) != sorted(b.files):
        diffs.append(f"keys differ: {sorted(set(a.files) ^ set(b.files))}")
    for k in sorted(set(a.files) & set(b.files)):
        x, y = a[k], b[k]
        if x.dtype != y.dtype or x.shape != y.shape or x.tobytes() != y.tobytes():
            d = ""
            if x.shape == y.shape and np.issubdtype(x.dtype, np.number) and np.issubdtype(y.dtype, np.number):
                den = np.maximum(np.abs(x.astype(float)), 1e-300)
                d = f" max|rel diff| {float(np.max(np.abs(x.astype(float) - y.astype(float)) / den)):.3e}"
            diffs.append(f"{k}: not bitwise identical{d}")
    return not diffs, diffs


def cmd_determinism(a) -> int:
    man = json.loads(a.manifest.read_text())
    rows = seed_rows(a.tables)
    res, ok = {}, True
    for tname, t in man["tables"].items():
        kind, name = lane_of(t["lane"])
        for s in t["seeds"]:
            orig_row = rows[s][1]
            tag = arg(orig_row, "--tag")
            orig = Path(arg(orig_row, "--out")) / f"{tag}_s{s}.npz"
            rerun = Path(man["root"]) / man["phase"] / kind / name / f"{tag}_s{s}.npz"
            if not orig.exists() or not rerun.exists():
                res[str(s)] = {"identical": False, "diffs": [f"missing: orig {orig.exists()} rerun {rerun.exists()}"]}
                ok = False
                continue
            same, diffs = npz_identical(orig, rerun)
            res[str(s)] = {"identical": same, "diffs": diffs, "orig": str(orig), "rerun": str(rerun)}
            ok &= same
    out = {"criterion": "every array of every rerun product bitwise identical to its original (fixed in advance)",
           "n": len(res), "verdict": "PASS" if ok and len(res) == man["n_seeds"] else "FAIL", "seeds": res}
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    print(out["verdict"], f"{sum(r['identical'] for r in res.values())}/{len(res)} identical")
    return 0 if out["verdict"] == "PASS" else 1


def cmd_resolve(a) -> int:
    design = json.loads(a.design.read_text())
    man = json.loads(a.manifest.read_text())
    cls = classify(json.loads(a.seed_states.read_text()))
    recovered: dict[str, set[int]] = {}
    for t in man["tables"].values():
        recovered.setdefault(t["lane"], set()).update(t["seeds"])
    union_root = a.union_root
    if union_root.exists():
        raise SystemExit(f"refusing to reuse {union_root}")
    new = json.loads(json.dumps(design))
    report = {}
    specs = [("cal", k, v, "calibration_glob") for k, v in design["nulls"].items()] + \
            [("pow", k, v, "glob") for k, v in design.get("power", {}).items()]
    for kind, key, spec, gk in specs:
        lane = f"{kind}-{key}"
        frozen = sorted(Path(p) for p in __import__("glob").glob(spec[gk]) if ".partial" not in Path(p).name)
        pattern = Path(spec[gk])
        rec_dir = Path(man["root"]) / man["phase"] / kind / key
        rec = sorted(p for p in rec_dir.glob(pattern.name) if ".partial" not in p.name) if rec_dir.is_dir() else []
        submitted = set(s for st in cls.get(lane, {}).values() for s in st)
        seed_of = lambda p: int(p.name.rsplit("_s", 1)[1].split(".")[0])
        have = [seed_of(p) for p in frozen] + [seed_of(p) for p in rec]
        if len(have) != len(set(have)):
            raise SystemExit(f"{lane}: a seed is both frozen and recovered")
        if set(have) != submitted:
            raise SystemExit(f"{lane}: union {len(set(have))} != submitted {len(submitted)} "
                             f"(missing {sorted(submitted - set(have))[:10]})")
        d = union_root / kind / key
        d.mkdir(parents=True)
        for p in frozen + rec:
            (d / p.name).symlink_to(p.resolve())
        new_spec = new["nulls"][key] if kind == "cal" else new["power"][key]
        new_spec[gk] = str(d / pattern.name)
        if kind == "cal":
            new_spec["calibration_n"] = len(have)
        else:
            new_spec["n"] = len(have)
        report[lane] = {"frozen": len(frozen), "recovered": len(rec), "union": len(have), "submitted": len(submitted)}
    new["_report_only"] = ("resolution of the missing-seed sensitivity (DECISION-20261005 §2): the frozen design with "
                           "union globs and counts; not the frozen design, not a primary evaluation")
    a.out_design.write_text(json.dumps(new, indent=1) + "\n")
    print(json.dumps(report))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("tables")
    t.add_argument("--phase", choices=("determinism", "recovery"), required=True)
    t.add_argument("--seed-states", type=Path, required=True)
    t.add_argument("--tables", type=Path, required=True, help="the frozen production tables directory")
    t.add_argument("--root", default=f"{NS}/recovery")
    t.add_argument("--out-dir", type=Path, required=True)
    t.add_argument("--parts", type=int, default=1, help="number of submission tables (arrays)")
    d = sub.add_parser("determinism")
    d.add_argument("--manifest", type=Path, required=True)
    d.add_argument("--tables", type=Path, required=True)
    d.add_argument("--out", type=Path, required=True)
    r = sub.add_parser("resolve")
    r.add_argument("--design", type=Path, required=True)
    r.add_argument("--manifest", type=Path, required=True)
    r.add_argument("--seed-states", type=Path, required=True)
    r.add_argument("--union-root", type=Path, required=True)
    r.add_argument("--out-design", type=Path, required=True)
    a = ap.parse_args(argv)
    return {"tables": cmd_tables, "determinism": cmd_determinism, "resolve": cmd_resolve}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())

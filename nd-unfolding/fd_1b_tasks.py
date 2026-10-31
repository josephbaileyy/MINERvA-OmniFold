#!/usr/bin/env python3
"""1B's step tables, lane tables and submit lines (state/measurement-paper/5d-community-20261024/FD-1B-DECLARATION.md
sections 6 and 7, bound by FD-1B-BINDING.md). Each job is one or more single-node submissions of the committed packer
(``state/gpu-timing-20261023/tools/sbatch_timing_packed.sh``: ``--exclusive --no-requeue``, 8 lanes of 32 CPUs and
56 GB), each lane running ``fd_f1_lane.py`` over its steps, each step one ``fd_1b_toys.py run`` invocation.

The jobs' contents, nodes and limits are the declaration's section 7 table, with its job 2a split into 2a-0 and 2a by
FD-1B-STAGE2-DECLARATION.md section 4 (the director's ruling 1); the packer splits each job's items, in the
declared order, into contiguous chunks as even as possible over its lanes, and refuses a packing whose fullest lane
differs from the declared "most per lane". A submit line is refused unless it is account m3246, QOS regular,
constraint cpu, a limit under 12 h equal to the declared one, and the committed packer.

    fd_1b_tasks.py tables --job 2a --deploy D --pins-sha256 X --out-dir DIR
    fd_1b_tasks.py submit --job 2a --deploy D --pin SHA

MEASURES: nothing. CANNOT AUTHORIZE: any job; each stage's binding names the jobs it authorizes.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import fd_1b_toys as toys  # noqa: E402
import fd_f1_tasks  # noqa: E402

P = "/pscratch/sd/j/josephrb"
B = f"{P}/fd-1b-20261030"
BANK = f"{P}/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware"
DETECTOR = f"{P}/s5p-20260926/bank_detector"
CONSTRAINT = f"{P}/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt"
PREP = f"{P}/fd-f1-20261027/f1b3/prep"
PINS = f"{B}/pins.json"
TABLE_REL = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b/tables"
PACKER_REL = "docs/orchestration/state/gpu-timing-20261023/tools/sbatch_timing_packed.sh"
ACCOUNT, QOS, CONSTRAINT_FLAG = "m3246", "regular", "cpu"
LANES_PER_NODE, CPUS, MEM = 8, 32, "56G"
MAX_LIMIT_H = 12.0

# (arm, mode, first, last) item runs, in the declared order. The derivation's 176 universes are split by the
# stage-2 declaration: the four of DERIVATION_FIRST run in 2a-0, so their walls are measured first, and the rest in 2a.
DERIVATION_FIRST = ("CV", "Flux_0", "MaRES_1", "GEANT_Pion_0")
JOBS = {
    "2a-0": {"nodes": 1, "limit": "01:00:00", "most_per_lane": 1,
             "items": [("derivation", "derivation", "first", None), ("pilot", "toy", 2_600_000, 2_600_001),
                       ("repro-g18", "half", 806_000, 806_000), ("repro-ar23", "half", 807_000, 807_000)]},
    "2a": {"nodes": 3, "limit": "02:40:00", "most_per_lane": 9,
           "items": [("pilot", "toy", 2_600_002, 2_600_015), ("pilot", "half", 2_600_000, 2_600_007),
                     ("derivation", "derivation", "rest", None)]},
    "2b": {"nodes": 2, "limit": "02:30:00", "most_per_lane": 7, "items": [("control", "toy", 2_610_000, 2_610_099)]},
    "2c": {"nodes": 3, "limit": "03:00:00", "most_per_lane": 9, "items": [("control", "toy", 2_610_100, 2_610_299)]},
    "3i": {"nodes": 3, "limit": "03:00:00", "most_per_lane": 9,
           "items": [("g18", "toy", 2_620_000, 2_620_099), ("ar23", "toy", 2_630_000, 2_630_099)]},
    "3f": {"nodes": 5, "limit": "03:30:00", "most_per_lane": 10,
           "items": [("g18", "toy", 2_620_100, 2_620_299), ("ar23", "toy", 2_630_100, 2_630_299)]},
}
DECLARED_CAPS = {"2a-0": 1.0, "2a": 8.0, "2b": 5.0, "2c": 9.0, "3i": 9.0, "3f": 17.5}
STAGE_CEILINGS = {"2": 23.0, "3": 26.5}


def hours(limit: str) -> float:
    h, m, s = (int(v) for v in limit.split(":"))
    return h + m / 60 + s / 3600


def cap(job: str) -> float:
    return JOBS[job]["nodes"] * hours(JOBS[job]["limit"])


def derivation_universes(which: str) -> list[str]:
    """The derivation's universes in S1's order: DERIVATION_FIRST ("first") or every other one ("rest")."""
    every = ["CV"] + toys.s1_universes()
    if not set(DERIVATION_FIRST) <= set(every):
        raise SystemExit(f"[FAIL] DERIVATION_FIRST names universes S1 did not unfold: {set(DERIVATION_FIRST) - set(every)}")
    if which == "first":
        return list(DERIVATION_FIRST)
    if which == "rest":
        return [u for u in every if u not in DERIVATION_FIRST]
    raise SystemExit(f"[FAIL] no derivation selection {which!r}")


def expand(job: str) -> list[tuple[str, str, object]]:
    """The job's unfolds, one (arm, mode, seed or universe) per unfold, in the declared order."""
    out = []
    for arm, mode, first, last in JOBS[job]["items"]:
        if mode == "derivation":
            out += [(arm, mode, u) for u in derivation_universes(first)]
        else:
            out += [(arm, mode, s) for s in range(first, last + 1)]
    return out


def chunks(items: list, n: int) -> list[list]:
    q, r = divmod(len(items), n)
    out, i = [], 0
    for k in range(n):
        m = q + (1 if k < r else 0)
        out.append(items[i:i + m])
        i += m
    return out


def out_dir(arm: str, mode: str) -> str:
    return f"{B}/runs/{arm}" + ("-half" if (arm == "pilot" and mode == "half") else "")


def tag(arm: str, mode: str) -> str:
    return f"fd1b_{arm}" + ("_half" if (arm == "pilot" and mode == "half") else "")


def step_args(arm: str, mode: str, what: list, pins_sha256: str) -> list[str]:
    truth = toys.ARMS[arm][0]
    args = ["run", "--arm", arm, "--mode", mode]
    args += ["--universes", ",".join(what)] if mode == "derivation" else ["--seeds", f"{what[0]}:{what[-1]}"]
    if arm.startswith("repro"):
        args.append("--no-draws")
    args += ["--npz", fd_f1_tasks.NPZ[0], "--bkg", fd_f1_tasks.BKG[0], "--expect-npz-sha256", fd_f1_tasks.NPZ[1],
             "--expect-bkg-sha256", fd_f1_tasks.BKG[1], "--bank", BANK, "--detector-dir", DETECTOR, "--pins", PINS,
             "--expect-pins-sha256", pins_sha256, "--flux-constraint", CONSTRAINT]
    if toys.TRUTHS[truth] is not None:
        args += ["--prep", PREP]
    return args + ["--threads", str(CPUS), "--tag", tag(arm, mode), "--out", out_dir(arm, mode)]


def steps(job: str, pins_sha256: str) -> list[list[str]]:
    spec = JOBS[job]
    lanes = chunks(expand(job), spec["nodes"] * LANES_PER_NODE)
    most = max(len(c) for c in lanes)
    if most != spec["most_per_lane"]:
        raise SystemExit(f"[FAIL] job {job}: fullest lane has {most} unfolds, the declaration says {spec['most_per_lane']}")
    rows = []
    for lane, chunk in enumerate(lanes):
        runs: list[tuple[str, str, list]] = []
        for arm, mode, x in chunk:  # consecutive unfolds of one arm and mode become one step
            if runs and runs[-1][:2] == (arm, mode):
                runs[-1][2].append(x)
            else:
                runs.append((arm, mode, [x]))
        for arm, mode, what in runs:
            name = f"fd1b_{job}_{arm}_{mode}_{what[0]}"
            rows.append([str(lane), name, "fd_1b_toys.py", *step_args(arm, mode, what, pins_sha256)])
    return rows


def lanes_table(job: str, table_dir: str) -> list[list[str]]:
    return [[f"fd1b_{job}_lane{k}", "fd_f1_lane.py", "--steps", f"{table_dir}/fd1b-{job}-steps.tsv", "--lane", str(k)]
            for k in range(JOBS[job]["nodes"] * LANES_PER_NODE)]


def check_deploy(deploy: str) -> None:
    """Every path a job reads or writes is on pscratch; nothing goes to CFS."""
    if not deploy.startswith(P + "/"):
        raise SystemExit(f"[FAIL] the deploy {deploy} is not under {P}")


def submit_lines(job: str, deploy: str, pin: str) -> list[str]:
    spec = JOBS[job]
    check_deploy(deploy)
    if not 0 < hours(spec["limit"]) < MAX_LIMIT_H:
        raise SystemExit(f"[FAIL] job {job}: limit {spec['limit']} is not under {MAX_LIMIT_H} h")
    if abs(cap(job) - DECLARED_CAPS[job]) > 1e-9:
        raise SystemExit(f"[FAIL] job {job}: cap {cap(job)} != declared {DECLARED_CAPS[job]}")
    for stage, ceiling in STAGE_CEILINGS.items():
        if sum(cap(j) for j in JOBS if j.startswith(stage)) > ceiling + 1e-9:
            raise SystemExit(f"[FAIL] stage {stage}'s caps exceed its ceiling {ceiling}")
    table = f"{deploy}/{TABLE_REL}/tasks-fd1b-{job}.tsv"
    out = []
    for n in range(spec["nodes"]):
        first, last = n * LANES_PER_NODE, n * LANES_PER_NODE + LANES_PER_NODE - 1
        out.append(" ".join(["sbatch", "-A", ACCOUNT, "-q", QOS, "-C", CONSTRAINT_FLAG, "-t", spec["limit"],
                             "-J", f"fd1b{job}n{n}", "-o", f"{B}/logs/%x_%j.out", f"{deploy}/{PACKER_REL}", deploy, pin,
                             table, f"{B}/runs/{job}", str(CPUS), MEM, str(first), str(last), "inherit"]))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("tables")
    t.add_argument("--job", choices=sorted(JOBS), required=True)
    t.add_argument("--deploy", required=True, help="the deploy root on pscratch the tables will sit in")
    t.add_argument("--pins-sha256", required=True)
    t.add_argument("--out-dir", type=Path, required=True)
    s = sub.add_parser("submit")
    s.add_argument("--job", choices=sorted(JOBS), required=True)
    s.add_argument("--deploy", required=True)
    s.add_argument("--pin", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "submit":
        print("\n".join(submit_lines(a.job, a.deploy, a.pin)))
        return 0
    check_deploy(a.deploy)
    rows = steps(a.job, a.pins_sha256)
    table_dir = f"{a.deploy}/{TABLE_REL}"
    head = f"# 1B job {a.job} ({{}}); FD-1B-DECLARATION.md sections 6-7\n"
    for fn, lines, what in ((f"fd1b-{a.job}-steps.tsv", rows, "steps"), (f"tasks-fd1b-{a.job}.tsv",
                                                                          lanes_table(a.job, table_dir), "lanes")):
        p = a.out_dir / fn
        if p.exists():
            raise SystemExit(f"[FAIL] refusing to overwrite {p}")
        p.write_text(head.format(what) + "".join("\t".join(x) + "\n" for x in lines))
    print(json.dumps({"job": a.job, "steps": len(rows), "unfolds": len(expand(a.job)), "cap_node_h": cap(a.job)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())

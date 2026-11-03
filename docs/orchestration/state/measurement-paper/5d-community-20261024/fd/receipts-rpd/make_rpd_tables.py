#!/usr/bin/env python3
"""Writes the run-period diagnosis's committed step and lane tables (FD-RPD-DECLARATION.md part 1 section 2, part 2
section 2) for its two jobs, each run by sbatch_timing_packed.sh -> s5c_array.sh -> fd_f1_lane.py on one exclusive
CPU node, eight lanes of 32 CPUs and 56 GB (5B's geometry).

* Job A, ``rpd-a``: per playlist nn_dump_inputs.py -> s5p_input_dumps.py lateral -> fd_rpd_inputs.py check, on X's
  staged zero loop with --mcfile X's flux file (always explicit); K2's two unfolds of 5B's staged PC inputs (seed 42
  and replica 3001); and N0's ten partitions (fd_rpd_inputs.py n0-split). Packed longest first by an estimated cost.
* Job B, ``rpd-b`` (submitted only after the controls PASS): each playlist's seed-42 unfold and its 30 replicas
  (seeds 4000 + 100 i + k), and N0's 120 pseudo-playlist unfolds, one unfold per step, packed longest first by
  780 s x e + 10 s (part 1 section 7), each step to the least-loaded lane.

    python3 -I -B make_rpd_tables.py <repo root> <output dir>
"""
import json
import sys
from pathlib import Path

REPO = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(REPO / "nd-unfolding"))
import fd_rpd as rp  # noqa: E402
import fd_rpd_inputs as ri  # noqa: E402

R = "/pscratch/sd/j/josephrb/fd-rpd-20261103"
REL = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-rpd"
N_LANES = 8
# the approximate shares of part 1 section 5, for packing only (the readers use F1's)
E_PACK = {"1A": .0847, "1B": .0176, "1C": .0405, "1D": .1359, "1E": .0972, "1F": .1575, "1G": .1311, "1L": .0127,
          "1M": .1507, "1N": .1001, "1O": .0280, "1P": .0439}
assert sorted(E_PACK) == sorted(ri.PLAYLISTS)
# job A's step costs in s, estimates for packing only: 5B's ALL lane took 3:14 + 7:12 + 7:06 for the whole sample
# (FD-CT-5B-REPORT.md:87) plus about 60 s of start-up a step; an N0 split about 300 s; a K2 unfold 140 s
A_COST = {"playlist": lambda pl: 1050 * E_PACK[pl] + 180, "n0": lambda p: 300.0, "k2": lambda b: 140.0}


def q(X):
    return {k: f"{R}/{v}" for k, v in ri.playlist_paths(X).items()}


def loop(X):
    return f"{R}/staged/zero/runEventLoopOmniFold_5D_{X}_zero.root"


def pack(work):
    load = [0.0] * N_LANES
    rows = []
    for cost, key, steps in sorted(work, key=lambda w: (-w[0], w[1])):
        lane = min(range(N_LANES), key=lambda k: (load[k], k))
        load[lane] += cost
        rows += ["\t".join([str(lane), name, entry, *args]) for name, entry, args in steps]
    return rows, load


work_a = []
for X in ri.PLAYLISTS:
    p = q(X)
    steps = [(f"rpd_nndump_{X}", "nn_dump_inputs.py", ["--omnifile", loop(X), "--mcfile", p["flux"], "--axes",
                                                       "eavail,q3,W", "--out", p["nn"]]),
             (f"rpd_lateral_{X}", "s5p_input_dumps.py", ["lateral", "--omnifile", loop(X), "--cv-npz", p["nn"],
                                                         "--mcfile", p["flux"], "--out", p["lat"], "--out-bkg",
                                                         p["bkg"]]),
             (f"rpd_check_{X}", "fd_rpd_inputs.py", ["check", "--r", R, "--playlist", X])]
    work_a.append((A_COST["playlist"](X), f"a_{X}", steps))
for b in rp.K2_SEEDS:
    tag = "s42" if b is None else f"b{b}"
    work_a.append((A_COST["k2"](b), f"k2_{tag}", [(f"rpd_k2_PC_{tag}", "fd_rpd_inputs.py",
                                                    ["unfold", "--r", R, "--what", "k2",
                                                     f"--pairs={'-' if b is None else b}:-"])]))
for part in range(1, ri.N_PART + 1):
    work_a.append((A_COST["n0"](part), f"n0_{part:02d}", [(f"rpd_n0split_p{part:02d}", "fd_rpd_inputs.py",
                                                           ["n0-split", "--r", R, "--partition", str(part)])]))
rows_a, load_a = pack(work_a)

work_b = []
for X in ri.PLAYLISTS:
    c = 780 * E_PACK[X] + 10
    for b in (None, *rp.REP[X]):
        tag = "s42" if b is None else f"b{b}"
        work_b.append((c, f"{X}_{tag}", [(f"rpd_unfold_{X}_{tag}", "fd_rpd_inputs.py",
                                          ["unfold", "--r", R, "--what", "playlist", "--playlist", X,
                                           f"--pairs={'-' if b is None else b}:-"])]))
for part in range(1, ri.N_PART + 1):
    for k, X in enumerate(ri.PLAYLISTS):
        work_b.append((780 * E_PACK[X] + 10, f"n0_{part:02d}_{k:02d}",
                       [(f"rpd_unfold_n0_p{part:02d}_k{k:02d}", "fd_rpd_inputs.py",
                         ["unfold", "--r", R, "--what", "n0", "--partition", str(part), "--k", str(k), "--pairs=-:-"])]))
rows_b, load_b = pack(work_b)


def tasks(job, steps_name):
    head = (f"# RPD job {job} (lanes), written by make_rpd_tables.py; FD-RPD-DECLARATION.md part 2 section 2. The steps "
            "path is relative to the deploy root, where s5c_array.sh and fd_f1_lane.py run")
    return [head] + ["\t".join([f"rpd_{job.lower()}_lane{k}", "fd_f1_lane.py", "--steps", f"{REL}/{steps_name}",
                                "--lane", str(k)]) for k in range(N_LANES)]


out = Path(sys.argv[2])
head_a = "# RPD job A (steps), written by make_rpd_tables.py; longest first by estimated cost, each work item to the least-loaded lane"
head_b = "# RPD job B (steps), written by make_rpd_tables.py; longest first by 780 s x e + 10 s, each step to the least-loaded lane"
(out / "rpd-a-steps.tsv").write_text("\n".join([head_a, *rows_a]) + "\n")
(out / "tasks-rpd-a.tsv").write_text("\n".join(tasks("A", "rpd-a-steps.tsv")) + "\n")
(out / "rpd-b-steps.tsv").write_text("\n".join([head_b, *rows_b]) + "\n")
(out / "tasks-rpd-b.tsv").write_text("\n".join(tasks("B", "rpd-b-steps.tsv")) + "\n")
(out / "packing.json").write_text(json.dumps({"lane_load_s": {"A": load_a, "B": load_b},
                                              "n_steps": {"A": len(rows_a), "B": len(rows_b)}}, indent=1) + "\n")
print("wrote", len(rows_a), "job A steps and", len(rows_b), "job B steps; fullest lane", round(max(load_a)),
      "s and", round(max(load_b)), "s")

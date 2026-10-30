#!/usr/bin/env python3
"""Writes 5B's committed step and lane tables (FD-CT-5B-DECLARATION.md section 2) for its two jobs, each run by
sbatch_timing_packed.sh -> s5c_array.sh -> fd_f1_lane.py on one exclusive CPU node.

* Job A, ``5b-inputs``: four lanes, one per period (ALL, PA, PB, PC), each running merge -> nn_dump_inputs.py ->
  s5p_input_dumps.py lateral -> check (with the MC truth); the ALL lane then runs the ALL unfold, which the pooled
  control reads.
* Job B, ``5b-periods`` (submitted only after the control PASSes): 33 unfolds, the seed-42 unfold and bootstrap
  replicas 1-10 of each period, one unfold per step, packed into eight lanes longest first (the cost of a step
  taken as its period's share of the twelve zero loops' bytes), each step to the least-loaded lane.

    python3 -I -B make_5b_tables.py <repo root> <output dir>
"""
import sys
from pathlib import Path

REPO = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(REPO / "nd-unfolding"))
import fd_ct_period_inputs as pi  # noqa: E402

P = "/pscratch/sd/j/josephrb"
B = f"{P}/fd-ct-5b-20261030"
LOOPS = f"{P}/measurement-paper/phase1/mp1/s1/evloop/zero"
MP1_LAT = f"{P}/measurement-paper/phase1/mp1/s1/lateral"
REL = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ct/5b"
LANES_A = ("ALL", "PA", "PB", "PC")
N_LANES_B = 8
# bytes of each zero loop (ls -l, login37, 2026-10-30): the step cost model for job B's packing only
LOOP_BYTES = {"1A": 398375296, "1B": 106517598, "1C": 204230889, "1D": 596287802, "1E": 495761736, "1F": 689044069,
              "1G": 581501093, "1L": 56587445, "1M": 862899975, "1N": 499729347, "1O": 150945068, "1P": 199848958}
assert sorted(LOOP_BYTES) == sorted(pi.ZERO_LOOPS)


def paths(per):
    return {"merged": f"{B}/merged/runEventLoopOmniFold_5D_{per}_zero.root", "nn": f"{B}/dumps/nn_{per}.npz",
            "lat": f"{B}/dumps/lat_{per}.npz", "bkg": f"{B}/dumps/lat_{per}_bkg.npz",
            "flux": f"{B}/flux/runEventLoopMC_{per}.root", "truth": f"{B}/truth/truth_{per}.npz",
            "receipt": f"{B}/inputs/check_{per}.json", "unf": f"{B}/unf/{per}"}


def unfold_args(per, b):
    q = paths(per)
    pair = f"{'-' if b is None else b}:-"
    return ["unfold", "--period", per, "--receipt", q["receipt"], f"--pairs={pair}", "--estimator-seed", "42",
            "--tag", f"5b_{per}", "--threads", "32", "--out", q["unf"]]


steps_a = ["# 5B job A (steps), written by make_5b_tables.py; FD-CT-5B-DECLARATION.md section 2"]
for lane, per in enumerate(LANES_A):
    q = paths(per)
    rows = [
        (f"ct5b_merge_{per}", "fd_ct_period_inputs.py", ["merge", "--period", per, "--loops-dir", LOOPS, "--out", q["merged"]]),
        (f"ct5b_nndump_{per}", "nn_dump_inputs.py", ["--omnifile", q["merged"], "--mcfile", q["flux"], "--axes", "eavail,q3,W",
                                                     "--out", q["nn"]]),
        (f"ct5b_lateral_{per}", "s5p_input_dumps.py", ["lateral", "--omnifile", q["merged"], "--cv-npz", q["nn"], "--mcfile",
                                                       q["flux"], "--out", q["lat"], "--out-bkg", q["bkg"]]),
        (f"ct5b_check_{per}", "fd_ct_period_inputs.py",
         ["check", "--period", per, "--merged", q["merged"], "--nn-npz", q["nn"], "--lat-npz", q["lat"], "--lat-bkg", q["bkg"],
          "--flux", q["flux"], "--truth-out", q["truth"], "--out", q["receipt"]]
         + (["--mp1-lat-npz", f"{MP1_LAT}/lat_zero.npz", "--mp1-lat-bkg", f"{MP1_LAT}/lat_zero_bkg.npz"] if per == "ALL" else [])),
    ]
    if per == "ALL":
        rows.append((f"ct5b_unfold_ALL_s42", "fd_ct_period_inputs.py", unfold_args("ALL", None)))
    for name, entry, args in rows:
        steps_a.append("\t".join([str(lane), name, entry, *args]))

cost = {per: sum(LOOP_BYTES[pl] for pl in pi.PERIODS[per]) for per in ("PA", "PB", "PC")}
work = sorted(((cost[per], per, b) for per in ("PA", "PB", "PC") for b in (None, *range(1, 11))),
              key=lambda w: (-w[0], w[1], -1 if w[2] is None else w[2]))
load = [0] * N_LANES_B
steps_b = ["# 5B job B (steps), written by make_5b_tables.py; FD-CT-5B-DECLARATION.md section 2. Longest first, each "
           "step to the least-loaded lane"]
for c, per, b in work:
    lane = min(range(N_LANES_B), key=lambda k: (load[k], k))
    load[lane] += c
    tag = "s42" if b is None else f"b{b:02d}"
    steps_b.append("\t".join([str(lane), f"ct5b_unfold_{per}_{tag}", "fd_ct_period_inputs.py", *unfold_args(per, b)]))


def tasks(job, n, steps_name):
    head = (f"# 5B job {job} (lanes), written by make_5b_tables.py; FD-CT-5B-DECLARATION.md section 2. The steps path is "
            "relative to the deploy root, where s5c_array.sh and fd_f1_lane.py run")
    return [head] + ["\t".join([f"ct5b_{job.lower()}_lane{k}", "fd_f1_lane.py", "--steps", f"{REL}/{steps_name}",
                                "--lane", str(k)]) for k in range(n)]


out = Path(sys.argv[2])
(out / "5b-inputs-steps.tsv").write_text("\n".join(steps_a) + "\n")
(out / "tasks-5b-inputs.tsv").write_text("\n".join(tasks("A", len(LANES_A), "5b-inputs-steps.tsv")) + "\n")
(out / "5b-periods-steps.tsv").write_text("\n".join(steps_b) + "\n")
(out / "tasks-5b-periods.tsv").write_text("\n".join(tasks("B", N_LANES_B, "5b-periods-steps.tsv")) + "\n")
print("wrote", *(out / n for n in ("5b-inputs-steps.tsv", "tasks-5b-inputs.tsv", "5b-periods-steps.tsv",
                                   "tasks-5b-periods.tsv")))

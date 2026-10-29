#!/usr/bin/env python3
"""Writes 3b's committed step and lane tables (FD-CT-3B-DECLARATION.md section 2) from the tool's own pins: 13
noise-free mismatch closures (zero-on-zero first, then MP-1's 10 species variants, then W2b's two), packed into eight
lanes (sbatch_timing_packed.sh -> s5c_array.sh -> fd_f1_lane.py), lane k running steps k and k + 8.

    python3 -I -B make_3b_tables.py <repo root> <output dir>
"""
import sys
from pathlib import Path

REPO = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(REPO / "nd-unfolding"))
import fd_ct_readers as ct  # noqa: E402

P = "/pscratch/sd/j/josephrb"
B = f"{P}/fd-ct-3b-20261029"
DUMP = {"zero": f"{P}/measurement-paper/phase1/mp1/s1/lateral/lat_zero.npz",
        **{f"{s}_{t}": f"{P}/measurement-paper/phase1/mp1/s1/lateral/lat_{s}_{t}.npz" for s in ct.SPECIES
           for t in ("m1", "p1")},
        "w2b_rr0": f"{P}/w2-recoil-20261006/w2b/lateral/lat_w2b_rr0.npz",
        "w2b_rr1": f"{P}/w2-recoil-20261006/w2b/lateral/lat_w2b_rr1.npz"}
pins = ct.closure_pins()
order = ["zero"] + [f"{s}_{t}" for s in ct.SPECIES for t in ("m1", "p1")] + ["w2b_rr0", "w2b_rr1"]
assert sorted(order) == sorted(pins) == sorted(DUMP) and len(order) == 13
REL = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ct/3b/3b-steps.tsv"
steps = ["# 3b (steps), written by make_3b_tables.py from fd_ct_readers.closure_pins(); FD-CT-3B-DECLARATION.md section 2"]
for i, v in enumerate(order):
    lane = i % 8
    args = ["--variant", v, "--response-npz", DUMP["zero"], "--expect-response-sha256", pins["zero"],
            "--pseudo-npz", DUMP[v], "--expect-pseudo-sha256", pins[v], "--estimator-seed", "42", "--threads", "32",
            "--iters", "5", "--out", f"{B}/closures/closure_{v}.npz"]
    steps.append("\t".join([str(lane), f"ct3b_closure_{v}", "fd_ct_closure.py", *args]))
tasks = ["# 3b (lanes), written by make_3b_tables.py; FD-CT-3B-DECLARATION.md section 2. The steps path is relative to "
         "the deploy root, where s5c_array.sh and fd_f1_lane.py run"]
for k in range(8):
    tasks.append("\t".join([f"ct3b_lane{k}", "fd_f1_lane.py", "--steps", REL, "--lane", str(k)]))
out = Path(sys.argv[2])
(out / "3b-steps.tsv").write_text("\n".join(steps) + "\n")
(out / "tasks-3b.tsv").write_text("\n".join(tasks) + "\n")
print("wrote", out / "3b-steps.tsv", out / "tasks-3b.tsv")

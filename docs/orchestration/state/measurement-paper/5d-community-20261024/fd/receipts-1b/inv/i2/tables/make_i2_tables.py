"""I2-0 and I2 bulk task tables (FD-1B-INV-DECLARATION section 6, bound by FD-1B-INV-BINDING): one unfold per step,
the pilot's 8 items on one node's 8 lanes; the bulk's 196 round-robin by mode over 32 lanes, at most 3 mode-A items
and at most 7 items per lane. Run from a checkout at M: python3 make_i2_tables.py <checkout> <out dir>."""
import sys
from pathlib import Path
co, out = Path(sys.argv[1]), Path(sys.argv[2])
sys.path.insert(0, str(co / "nd-unfolding"))
import fd_1b_inv as inv, s1_assemble as sa
P = "/pscratch/sd/j/josephrb"; V = f"{P}/fd-1b-inv-20261101"
COMMON = ["--npz", f"{P}/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz", "--bkg", f"{P}/s5c-20260924/runs/p2/bkg_dump.npz",
          "--bank", f"{P}/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware", "--detector-dir", f"{P}/s5p-20260926/bank_detector",
          "--pins", f"{P}/fd-1b-20261030/pins.json",
          "--expect-pins-sha256", "5adcd576eb46f443fe4133b05044cd315c0eeb0f281e21acee5f2318b4bab248",
          "--threads", "32", "--tag", "fd1b_inv", "--out", f"{V}/i2/unf"]
universes = [f"{b}_{i}" for b in inv.INTERACTION for i in range(sa.EXPECT[b])]
assert len(universes) == 67
items = [(m, u) for u in ["CV"] + universes for m in inv.MODES]
assert len(items) == 204 and len(set(items)) == 204
pilot = list(inv.PILOT)
bulk = [x for x in items if x not in set(pilot)]
assert len(bulk) == 196
def tables(job, lanes_items, nodes):
    steps, tasks = [f"# 1B investigation {job} (steps); FD-1B-INV-DECLARATION.md section 6, FD-1B-INV-BINDING.md"], \
                   [f"# 1B investigation {job} (lanes); FD-1B-INV-DECLARATION.md section 6, FD-1B-INV-BINDING.md"]
    for lane, its in enumerate(lanes_items):
        for mode, u in its:
            steps.append("\t".join([str(lane), f"fd1b_inv_{job}_{mode}_{u}", "fd_1b_inv.py", "unfold", "--mode", mode,
                                    "--universes", u] + COMMON))
        tasks.append("\t".join([f"fd1b_inv_{job}_lane{lane}", "fd_f1_lane.py", "--steps", f"{V}/tables/{job}-steps.tsv",
                                "--lane", str(lane)]))
    (out / f"{job}-steps.tsv").write_text("\n".join(steps) + "\n")
    (out / f"tasks-{job}.tsv").write_text("\n".join(tasks) + "\n")
    return lanes_items
p = tables("i2-0", [[x] for x in pilot], 1)
lanes = [[] for _ in range(32)]
for k, x in enumerate(bulk):
    lanes[k % 32].append(x)
assert max(len(l) for l in lanes) == 7 and max(sum(m == "A" for m, _ in l) for l in lanes) <= 3, \
    (max(len(l) for l in lanes), max(sum(m == "A" for m, _ in l) for l in lanes))
tables("i2", lanes, 4)
print("pilot lanes", len(p), "bulk lanes", len(lanes), "most per lane", max(len(l) for l in lanes),
      "most A per lane", max(sum(m == "A" for m, _ in l) for l in lanes))

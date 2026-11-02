"""Stage 0 (κ, mode D) task tables (FD-1B-STAGED-DECLARATION.md section 2, carrying FD-1B-MODED-DECLARATION.md
sections 7 and 9; bound by FD-1B-STAGED-BINDING-1.md): one unfold per step.
* D-0: the declared PILOT's 8 items, one per lane of one node;
* the bulk: the other 96 of the 104 items (Dnom at CV and the 67 interaction universes; B and C on the three grids
  for the six grid universes), round-robin by mode over 16 lanes on two one-node jobs, at most 6 per lane.
Run from a checkout at M: python3 make_stage0_tables.py <checkout> <out dir>."""
import sys
from pathlib import Path
co, out = Path(sys.argv[1]), Path(sys.argv[2])
sys.path.insert(0, str(co / "nd-unfolding"))
import fd_1b_moded as md, fd_1b_inv as inv, s1_assemble as sa
P = "/pscratch/sd/j/josephrb"; W = f"{P}/fd-1b-staged-20261102"; DD = f"{W}/deploy"
COMMON = ["--npz", f"{P}/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz", "--bkg", f"{P}/s5c-20260924/runs/p2/bkg_dump.npz",
          "--bank", f"{P}/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware", "--detector-dir", f"{P}/s5p-20260926/bank_detector",
          "--pins", f"{P}/fd-1b-20261030/pins.json",
          "--expect-pins-sha256", "5adcd576eb46f443fe4133b05044cd315c0eeb0f281e21acee5f2318b4bab248",
          "--threads", "32", "--tag", "fd1b_d", "--out", f"{W}/stage0/unf"]
DEFINITION = ["--definition", f"{DD}/nd-unfolding/pv-ladder/readouts/h2_definition.json"]
universes = [f"{b}_{i}" for b in inv.INTERACTION for i in range(sa.EXPECT[b])]
assert len(universes) == 67
items = [("Dnom", None, u) for u in ["CV"] + universes]
items += [(m, g, u) for u in md.GRID_UNIVERSES for g in md.GRIDS for m in md.GRID_MODES]
assert len(items) == 104 and len(set(items)) == 104
pilot = list(md.PILOT)
assert set(pilot) <= set(items) and len(pilot) == 8
bulk = [x for x in items if x not in set(pilot)]
assert len(bulk) == 96
def name(job, m, g, u):
    return f"fd1b_d_{job}_{m}_{g}_{u}" if g else f"fd1b_d_{job}_{m}_{u}"
def tables(job, lanes_items):
    head = f"# 1B staged stage 0 {job} ({{}}); FD-1B-STAGED-DECLARATION.md section 2, FD-1B-STAGED-BINDING-1.md"
    steps, tasks = [head.format("steps")], [head.format("lanes")]
    for lane, its in enumerate(lanes_items):
        for m, g, u in its:
            extra = ["--grid", g] + DEFINITION if g else []
            steps.append("\t".join([str(lane), name(job, m, g, u), "fd_1b_moded.py", "unfold", "--mode", m] + extra
                                   + ["--universes", u] + COMMON))
        tasks.append("\t".join([f"fd1b_d_{job}_lane{lane}", "fd_f1_lane.py", "--steps", f"{W}/tables/{job}-steps.tsv",
                                "--lane", str(lane)]))
    (out / f"{job}-steps.tsv").write_text("\n".join(steps) + "\n")
    (out / f"tasks-{job}.tsv").write_text("\n".join(tasks) + "\n")
tables("d0", [[x] for x in pilot])
# round-robin by mode: interleave the Dnom and grid items so each lane holds a mix
dn = [x for x in bulk if x[0] == "Dnom"]; gr = [x for x in bulk if x[0] != "Dnom"]
order, i, j = [], 0, 0
while i < len(dn) or j < len(gr):
    for _ in range(2):
        if i < len(dn):
            order.append(dn[i]); i += 1
    if j < len(gr):
        order.append(gr[j]); j += 1
assert sorted(order, key=str) == sorted(bulk, key=str)
lanes = [[] for _ in range(16)]
for k, x in enumerate(order):
    lanes[k % 16].append(x)
assert max(len(l) for l in lanes) == 6
tables("bulk", lanes)
print("pilot lanes 8; bulk lanes", len(lanes), "most per lane", max(len(l) for l in lanes),
      "fine-grid items per lane max", max(sum(g == "fine" for _, g, _ in l) for l in lanes), "Dnom", len(dn), "grid", len(gr))

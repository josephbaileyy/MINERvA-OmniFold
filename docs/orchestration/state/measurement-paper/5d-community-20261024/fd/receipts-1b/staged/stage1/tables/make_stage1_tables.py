"""Stage 1 task tables (FD-1B-STAGED-DECLARATION.md sections 4.3, 8 and 10; binding 2): one item per step.
* s1-0: the pilot's 8 items (``fd_1b_mc.PILOT[plugin]``), one per lane of one node;
* bulk: every other item, round-robin by role over 8-lane one-node jobs, at most 22 per lane: per truth (G18, AR23,
  and the plug-in if run) its central value, seed check, 175 universe blocks, 50 stat replicas and 300 toys; the
  four procedure controls and the capture run in the pilot.
Run from a checkout at the binding's merge:
  python3 make_stage1_tables.py <checkout> <out dir> <plugin yes|no> <flux table sha256> [<push sha256>]
The bulk table needs the push digest when the plug-in runs, so it is made after S1-0."""
import math
import sys
from pathlib import Path
co, out, plugin, flux_sha = Path(sys.argv[1]), Path(sys.argv[2]).resolve(), sys.argv[3] == "yes", sys.argv[4]
push_sha = sys.argv[5] if len(sys.argv) > 5 else None
sys.path.insert(0, str(co / "nd-unfolding"))
import fd_1b_mc as mc, s1_assemble as sa, fd_1b_toys as toys
P = "/pscratch/sd/j/josephrb"; W = f"{P}/fd-1b-staged-20261102"
COMMON = ["--npz", f"{P}/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz", "--bkg", f"{P}/s5c-20260924/runs/p2/bkg_dump.npz",
          "--bank", f"{P}/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware", "--detector-dir", f"{P}/s5p-20260926/bank_detector",
          "--pins", f"{P}/fd-1b-20261030/pins.json",
          "--expect-pins-sha256", "5adcd576eb46f443fe4133b05044cd315c0eeb0f281e21acee5f2318b4bab248",
          "--flux-constraint", f"{P}/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt",
          "--flux-table", f"{W}/stage1/in/flux_universes.npz", "--expect-flux-table-sha256", flux_sha,
          "--threads", "32", "--tag", "fd1b_mc", "--out", f"{W}/stage1/unf"]
PREP = ["--prep", f"{P}/fd-f1-20261027/f1b3/prep"]   # the toys' F1 prep (stage 2 tables)
PUSH = ["--push", f"{W}/stage1/in/push.npz", "--expect-push-sha256", str(push_sha)]
truths = ["g18", "ar23"] + (["plugin"] if plugin else [])
universes = [f"{b}_{i}" for b in sa.EXPECT for i in range(sa.EXPECT[b])]
assert len(universes) == 175
items = []
for t in truths:
    items += [(t, "central", "T"), (t, "seed", "T")] + [(t, "block", u) for u in universes]
    items += [(t, "stat", str(b)) for b in mc.STAT_REPLICAS] + [(t, "toy", str(s)) for s in mc.TOY_SEEDS[t]]
items += [("data", "control", c) for c in mc.CONTROLS] + ([("data", "capture", "data")] if plugin else [])
assert len(items) == len(set(items)) == 527 * len(truths) + 4 + int(plugin)
def as_item(role, item):
    if role in ("control", "capture"):
        return ("data", role, item)
    t, _, it = item.partition(":")
    return (t, role, "T" if role == "central" else it)
pilot = [as_item(r, i) for r, i in mc.PILOT[plugin]]
assert set(pilot) <= set(items) and len(pilot) == 8
bulk = [x for x in items if x not in set(pilot)]
if plugin and push_sha is None:
    bulk = []        # the bulk table is made after S1-0, with the push digest
def argv(t, role, it):
    extra = PREP if t in ("g18", "ar23") else (PUSH if t == "plugin" else [])
    return ["fd_1b_mc.py", "unfold", "--truth", t, "--role", role, "--items", it] + COMMON + extra
def tables(job, lanes_items):
    head = f"# 1B staged stage 1 {job} ({{}}); FD-1B-STAGED-DECLARATION.md sections 4 and 8, binding 2"
    steps, tasks = [head.format("steps")], [head.format("lanes")]
    for lane, its in enumerate(lanes_items):
        for t, role, it in its:
            steps.append("\t".join([str(lane), f"fd1b_mc_{job}_{t}_{role}_{it}"] + argv(t, role, it)))
        tasks.append("\t".join([f"fd1b_mc_{job}_lane{lane}", "fd_f1_lane.py", "--steps", str(out / f"{job}-steps.tsv"),
                                "--lane", str(lane)]))
    (out / f"{job}-steps.tsv").write_text("\n".join(steps) + "\n")
    (out / f"tasks-{job}.tsv").write_text("\n".join(tasks) + "\n")
tables("s1-0", [[x] for x in pilot])
if bulk:
    nodes = math.ceil(len(bulk) / (8 * 22))
    by_role = {}
    for x in bulk:
        by_role.setdefault(x[1], []).append(x)
    order = []
    while any(by_role.values()):
        for r in ("toy", "block", "stat", "central", "seed"):
            if by_role.get(r):
                order.append(by_role[r].pop(0))
    lanes = [[] for _ in range(8 * nodes)]
    for k, x in enumerate(order):
        lanes[k % len(lanes)].append(x)
    assert max(len(l) for l in lanes) <= 22 and sorted(order) == sorted(bulk)
    tables("s1-bulk", lanes)
    print("bulk items", len(bulk), "nodes", nodes, "most per lane", max(len(l) for l in lanes))
print("pilot", pilot)

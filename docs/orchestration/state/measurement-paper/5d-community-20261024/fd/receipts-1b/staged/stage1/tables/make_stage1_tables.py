"""Stage 1 task tables (FD-1B-STAGED-DECLARATION.md sections 4.3, 8 and 10; binding 2; FD-1B-STAGED-AMENDMENT-2.md;
addendum A2.1's S2 and the director's ruling (A) of 2026-11-04, for binding 3): one item per step.
* receipt (amendment 2): ``fd_1b_mc.py receipt`` as the one step of one lane of a one-node job;
* s1-0: the pilot's 8 items (``fd_1b_mc.PILOT[plugin]``), one per lane of one node, under "data";
* s1-0b (amendment 2, the director's ruling): after S1-0's readout, the clipmean at every truth and the central
  values S1-0 lacks (``fd_1b_mc.pilot_b``), one per lane of one node, under "data";
* bulk, under "nature" only (A2.1 S2): every graded item (``fd_1b_mc.BULK_ROLES``) per truth (G18, AR23, and the
  plug-in if run): its central value, seed check, 175 universe blocks, 50 stat replicas and 300 toys, round-robin by
  role over 8-lane one-node jobs, at most 22 per lane. The graded items S1-0 and S1-0b run under "data" are re-run
  here under "nature" (ruling (A)): their "data" products stay checks and S1-0b's descriptive figure, never graded
  (fd_1b_mc.refuse_mixed_estimator refuses a truth whose products mix rules). The clipmeans and the procedure
  controls and capture are S1-0's and S1-0b's alone.
Every unfold and the receipt carry the CV per-row tdw (A2.1 (e2): a composite refuses without it under either rule).
Every bulk step carries c2check's gate record and its digest, which must be the one binding 3 commits in
``fd_1b_mc.GATE_PIN``, unmodified in the checkout, or no bulk table is written.
Run from a checkout at the binding's merge:
  python3 make_stage1_tables.py <checkout> <out dir> --plugin yes|no --flux-table-sha256 SHA --estimator NAME
      [--push-sha256 SHA --clip-seed SEED --clip-gate PATH --expect-clip-gate-sha256 SHA]
The estimator is a name in ``s5e_candidate.CANDIDATES`` (configuration (e) is "R"). The s1-0b and bulk tables need
the push digest when the plug-in runs and the receipt's N_clip seed, so they are made after S1-0; the bulk also needs
the gate record, so it is made after c2check and binding 3."""
from __future__ import annotations

import argparse
import math
import subprocess
import sys
from pathlib import Path

P = "/pscratch/sd/j/josephrb"
W = f"{P}/fd-1b-staged-20261102"
CV_TDW = f"{P}/fd-1b-a21-cvdenom2-20261103/cvdenom.npy"      # fd_1b_cvdenom's PASS output (A2.1 §6, run 2)
CV_TDW_SHA256 = "0bc70d622ed51f7e6ce3b80e095788f315e52937b6a6c79a0bafedeb4545def8"
LANES, PER_LANE = 8, 22


def as_item(role, item):
    if role in ("control", "capture"):
        return ("data", role, item)
    t, _, it = item.partition(":")
    return (t, role, "T" if role == "central" else it)


def declared_items(mc, sa, truths, plugin, clip_seed):
    universes = [f"{b}_{i}" for b in sa.EXPECT for i in range(sa.EXPECT[b])]
    assert len(universes) == 175
    items = []
    for t in truths:
        items += [(t, "central", "T"), (t, "seed", "T")] + [(t, "block", u) for u in universes]
        items += [(t, "stat", str(b)) for b in mc.STAT_REPLICAS] + [(t, "toy", str(s)) for s in mc.TOY_SEEDS[t]]
        items += [(t, "clipmean", str(clip_seed))]
    items += [("data", "control", c) for c in mc.CONTROLS] + ([("data", "capture", "data")] if plugin else [])
    assert len(items) == len(set(items)) == 528 * len(truths) + 4 + int(plugin)
    return items


def plan(mc, sa, plugin, clip_seed):
    """(pilot, pilot_b, bulk): S1-0's and S1-0b's items under "data", then the graded bulk under "nature", which is
    every declared item in BULK_ROLES, the pilot's and S1-0b's graded items included (ruling (A)). pilot_b and bulk
    are empty before S1-0 (clip_seed None)."""
    truths = ["g18", "ar23"] + (["plugin"] if plugin else [])
    items = declared_items(mc, sa, truths, plugin, clip_seed)
    pilot = [as_item(r, i) for r, i in mc.PILOT[plugin]]
    assert set(pilot) <= set(items) and len(pilot) == 8
    if clip_seed is None:
        return pilot, [], []
    pilot_b = mc.pilot_b(plugin, int(clip_seed))
    assert set(pilot_b) <= set(items) and not set(pilot_b) & set(pilot)
    bulk = [x for x in items if x[1] in mc.BULK_ROLES]
    assert not {x for x in pilot + pilot_b if x[1] not in mc.BULK_ROLES} & set(bulk)
    return pilot, pilot_b, bulk


def committed_gate_sha(mc, co: Path) -> str:
    """The declared c2check record's sha256 from fd_1b_mc.bound_gate_sha256 (which refuses a missing or malformed pins
    file), required to be the checkout's committed GATE_PIN: tracked, and its working bytes HEAD's blob."""
    sha, blob = mc.bound_gate_sha256()
    rel = mc.GATE_PIN.resolve().relative_to(co.resolve()).as_posix()
    head = subprocess.run(["git", "-C", str(co), "rev-parse", f"HEAD:{rel}"], capture_output=True, text=True)
    if head.returncode != 0 or head.stdout.strip() != blob:
        raise SystemExit(f"{rel} is not committed at the checkout's HEAD as it stands on disk: no bulk table")
    return sha


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("checkout", type=Path)
    p.add_argument("out", type=Path)
    p.add_argument("--plugin", choices=("yes", "no"), required=True)
    p.add_argument("--flux-table-sha256", required=True)
    p.add_argument("--estimator", required=True)
    p.add_argument("--push-sha256")
    p.add_argument("--clip-seed")
    p.add_argument("--clip-gate")
    p.add_argument("--expect-clip-gate-sha256")
    a = p.parse_args(argv)
    co, out, plugin = a.checkout, a.out.resolve(), a.plugin == "yes"
    sys.path.insert(0, str(co / "nd-unfolding"))
    import fd_1b_mc as mc
    import s1_assemble as sa
    import s5e_candidate
    assert a.estimator in s5e_candidate.CANDIDATES, f"estimator {a.estimator!r} is not in the registry"
    common = ["--npz", f"{P}/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz", "--bkg", f"{P}/s5c-20260924/runs/p2/bkg_dump.npz",
              "--bank", f"{P}/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware", "--detector-dir", f"{P}/s5p-20260926/bank_detector",
              "--pins", f"{P}/fd-1b-20261030/pins.json",
              "--expect-pins-sha256", "5adcd576eb46f443fe4133b05044cd315c0eeb0f281e21acee5f2318b4bab248",
              "--flux-constraint", f"{P}/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt",
              "--flux-table", f"{W}/stage1/in/flux_universes.npz", "--expect-flux-table-sha256", a.flux_table_sha256,
              "--cv-tdw", CV_TDW, "--expect-cv-tdw-sha256", CV_TDW_SHA256,
              "--threads", "32", "--estimator", a.estimator, "--tag", "fd1b_mc", "--out", f"{W}/stage1/unf"]
    prep = ["--prep", f"{P}/fd-f1-20261027/f1b3/prep"]   # the toys' F1 prep (stage 2 tables)
    receipt = ["fd_1b_mc.py", "receipt"] + common[:common.index("--threads")] + [
        "--staged", f"{P}/fd-1b-inv-20261101/i0/in", "--definition", str(co / "nd-unfolding/pv-ladder/readouts/h2_definition.json"),
        "--out", f"{W}/stage1/a2/receipt.json"]
    push = ["--push", f"{W}/stage1/in/push.npz", "--expect-push-sha256", str(a.push_sha256)]
    later = not ((plugin and a.push_sha256 is None) or a.clip_seed is None)   # after S1-0, with the push and N_clip's seed
    pilot, pilot_b, bulk = plan(mc, sa, plugin, a.clip_seed if later else None)
    gate = None
    if bulk and a.clip_gate:
        if a.expect_clip_gate_sha256 != committed_gate_sha(mc, co):
            raise SystemExit("--expect-clip-gate-sha256 is not the record binding 3 commits in BOUND_GATE.sha256")
        gate = ["--clip-gate", a.clip_gate, "--expect-clip-gate-sha256", a.expect_clip_gate_sha256]

    def argv(t, role, it, rule):
        extra = prep if t in ("g18", "ar23") else (push if t == "plugin" else [])
        return (["fd_1b_mc.py", "unfold", "--truth", t, "--role", role, "--items", it] + common + extra
                + ["--clip-rule", rule] + (gate if rule == "nature" else []))

    def tables(job, lanes_items, rule):
        head = f"# 1B staged stage 1 {job} ({{}}); FD-1B-STAGED-DECLARATION.md sections 4 and 8, A2.1 S2, binding 3"
        steps, tasks = [head.format("steps")], [head.format("lanes")]
        for lane, its in enumerate(lanes_items):
            for t, role, it in its:
                steps.append("\t".join([str(lane), f"fd1b_mc_{job}_{t}_{role}_{it}"] + argv(t, role, it, rule)))
            tasks.append("\t".join([f"fd1b_mc_{job}_lane{lane}", "fd_f1_lane.py", "--steps", str(out / f"{job}-steps.tsv"),
                                    "--lane", str(lane)]))
        (out / f"{job}-steps.tsv").write_text("\n".join(steps) + "\n")
        (out / f"tasks-{job}.tsv").write_text("\n".join(tasks) + "\n")
    tables("s1-0", [[x] for x in pilot], "data")
    if later:
        tables("s1-0b", [[x] for x in pilot_b], "data")
    (out / "receipt-steps.tsv").write_text("# 1B staged stage 1 receipt (steps); FD-1B-STAGED-AMENDMENT-2.md, binding 3\n"
                                           + "\t".join(["0", "fd1b_mc_receipt_a2"] + receipt) + "\n")
    (out / "tasks-receipt.tsv").write_text("# 1B staged stage 1 receipt (lanes); FD-1B-STAGED-AMENDMENT-2.md, binding 3\n"
                                           + "\t".join(["fd1b_mc_receipt_lane0", "fd_f1_lane.py", "--steps",
                                                         str(out / "receipt-steps.tsv"), "--lane", "0"]) + "\n")
    if gate:
        nodes = math.ceil(len(bulk) / (LANES * PER_LANE))
        by_role = {}
        for x in bulk:
            by_role.setdefault(x[1], []).append(x)
        order = []
        while any(by_role.values()):
            for r in ("toy", "block", "stat", "central", "seed"):
                if by_role.get(r):
                    order.append(by_role[r].pop(0))
        lanes = [[] for _ in range(LANES * nodes)]
        for k, x in enumerate(order):
            lanes[k % len(lanes)].append(x)
        assert max(len(l) for l in lanes) <= PER_LANE and sorted(order) == sorted(bulk)
        tables("s1-bulk", lanes, "nature")
        print("bulk items", len(bulk), "nodes", nodes, "slots", LANES * PER_LANE * nodes,
              "most per lane", max(len(l) for l in lanes))
    elif bulk:
        print("no bulk table: it needs --clip-gate and binding 3's committed BOUND_GATE.sha256")
    print("pilot", pilot)
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""End-to-end smoke for the sidecar identity export, on a synthetic G2-shaped ROOT.

Why this exists: `nd-unfolding/tests/test_event_identity.py` covers the pure contract, but the
exporter's PyROOT path -- branch binding, the `UChar_t` pass flags, the retention loop, the
order-hash re-derivation and the block verification -- is only exercised by running it. A
synthetic file is the only way to run it without a compute allocation and a 113 GB read, and a
path that has never executed is not evidence of anything.

The fixture is built to contain the cases that matter rather than random rows:
  * a matched signal row, a NATIVE MISS (sim_pass=0, sentinel reco, valid truth), and an
    out-of-domain row that must be dropped;
  * a `data` gate carrying TWO distinct reconstructed events, so `occurrence` is non-zero and the
    identity is only unique because of it;
  * a dropped row sitting BEFORE a duplicated one, so an occurrence computed after selection
    would differ from one computed before it.

Needs PyROOT. Writes only into a temporary directory.

    python3 smoke_export_event_identity.py
"""
from __future__ import annotations

import os
import sys
import tempfile

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
import event_identity as eid  # noqa: E402

SENTINEL = -9999.0

# (sim, sim_pz, sim_pass, MC, MC_pz, w_truth, w_reco, run, subrun, nth)
SIGNAL_ROWS = [
    (1.0, 4.0, 1, 1.1, 4.1, 1.25, 1.30, 111353, 7, 0),      # matched
    (SENTINEL, SENTINEL, 0, 1.2, 4.2, 0.90, 0.90, 111353, 7, 1),   # NATIVE MISS
    (1e6, 1e6, 1, SENTINEL, SENTINEL, 1.00, 1.00, 111353, 7, 2),   # dropped: no truth, bad reco
    (2.0, 5.0, 1, 2.1, 5.1, 1.75, 1.80, 111353, 8, 0),      # matched
]
# (measured, measured_pz, measured_pass, run, subrun, gate)
DATA_ROWS = [
    (999.0, 999.0, 1, 19168, 2, 100),        # dropped: outside the FPS box
    (1.0, 3.0, 1, 19168, 2, 295),            # gate 295, first reconstructed event
    (1.5, 6.0, 1, 19168, 2, 295),            # gate 295, SECOND -> occurrence 1
    (2.0, 7.0, 0, 19168, 2, 296),            # dropped: not reco-selected
]
# (sim_background, sim_background_pz, sim_background_pass, w_bkg, run, subrun, nth)
BKG_ROWS = [
    (0.5, 2.0, 1, 0.25, 113000, 1, 0),
    (1.5, 3.0, 1, 0.50, 113000, 1, 1),
    (1e6, 1e6, 1, 0.75, 113000, 1, 2),       # dropped: outside the FPS box
]


def _make_root(path):
    """Write a synthetic G2-shaped ROOT with the branches the exporter reads."""
    import ROOT
    from array import array
    ROOT.gROOT.SetBatch(True)
    f = ROOT.TFile.Open(path, "RECREATE")

    def scalars(tree, names, kind="d"):
        bufs = {}
        for nm in names:
            bufs[nm] = array(kind, [0])
            tree.Branch(nm, bufs[nm], f"{nm}/{'D' if kind == 'd' else ('I' if kind == 'i' else 'b')}")
        return bufs

    t = ROOT.TTree("mc_signal_reco", "")
    d = scalars(t, ["sim", "sim_pz", "MC", "MC_pz", "w_truth", "w_reco"])
    b = scalars(t, ["sim_pass"], "B")
    i = scalars(t, ["mc_run", "mc_subrun", "mc_nthEvtInFile"], "i")
    for row in SIGNAL_ROWS:
        (d["sim"][0], d["sim_pz"][0], b["sim_pass"][0], d["MC"][0], d["MC_pz"][0],
         d["w_truth"][0], d["w_reco"][0], i["mc_run"][0], i["mc_subrun"][0],
         i["mc_nthEvtInFile"][0]) = row
        t.Fill()
    t.Write()

    t = ROOT.TTree("data", "")
    d = scalars(t, ["measured", "measured_pz"])
    b = scalars(t, ["measured_pass"], "B")
    i = scalars(t, ["ev_run", "ev_subrun", "ev_gate"], "i")
    for row in DATA_ROWS:
        (d["measured"][0], d["measured_pz"][0], b["measured_pass"][0],
         i["ev_run"][0], i["ev_subrun"][0], i["ev_gate"][0]) = row
        t.Fill()
    t.Write()

    t = ROOT.TTree("mc_background", "")
    d = scalars(t, ["sim_background", "sim_background_pz", "w_bkg"])
    b = scalars(t, ["sim_background_pass"], "B")
    i = scalars(t, ["mc_run", "mc_subrun", "mc_nthEvtInFile"], "i")
    for row in BKG_ROWS:
        (d["sim_background"][0], d["sim_background_pz"][0], b["sim_background_pass"][0],
         d["w_bkg"][0], i["mc_run"][0], i["mc_subrun"][0], i["mc_nthEvtInFile"][0]) = row
        t.Fill()
    t.Write()
    f.Close()


def _make_target_npz(path, order_hash_fn):
    """Write the subset of inventory keys the exporter reads, with the hashes the dump stores."""
    w_truth = np.array([1.25, 0.90, 1.75], np.float32)          # the three retained signal rows
    pass_truth = np.array([True, True, True])
    w_bkg = np.array([0.25, 0.50], np.float32)
    measured_pc = np.zeros((2, 12, 3), np.float32)
    np.savez_compressed(
        path,
        w_truth=w_truth, pass_truth=pass_truth, w_bkg=w_bkg, measured_pc=measured_pc,
        sig_identity_hash=np.asarray(order_hash_fn(w_truth, pass_truth)),
        bkg_identity_hash=np.asarray(order_hash_fn(w_bkg, np.arange(2, dtype=np.int64))),
        data_identity_hash=np.asarray(order_hash_fn(measured_pc)))


class _Args:
    def __init__(self, omnifile, target_npz, source_label):
        self.omnifile = omnifile
        self.target_npz = target_npz
        self.identity_audit = None
        self.source_label = source_label
        self.production_pet_dir = _HERE


def main():
    import export_event_identity as exp
    from fullevent_fps_dataloader import inventory_order_hash

    checks, failures = 0, []

    def ck(name, cond, detail=""):
        nonlocal checks
        checks += 1
        if not cond:
            failures.append(f"{name}: {detail}")
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}{(' -- ' + detail) if detail else ''}")

    with tempfile.TemporaryDirectory() as tmp:
        root = os.path.join(tmp, "smoke_g2.root")
        npz = os.path.join(tmp, "smoke_inventory.npz")
        _make_root(root)
        _make_target_npz(npz, inventory_order_hash)

        arrays, n_target, order_hash_fn = exp.build_sidecar(_Args(root, npz, "1X"))
        ck("target row counts", n_target == {"sig": 3, "data": 2, "bkg": 2}, str(n_target))

        for inv, n in n_target.items():
            eid.verify_identity_block(inv, arrays, n, order_hash_fn)
        ck("every block verifies", True)

        k = eid.export_keys("sig")
        sig_id = arrays[k["values"]]
        ck("native miss retained with its identity",
           sig_id.shape[0] == 3 and list(sig_id[1]) == [111353, 7, 1], str(sig_id.tolist()))
        ck("dropped signal row is absent",
           [111353, 7, 2] not in sig_id.tolist(), str(sig_id.tolist()))

        kd = eid.export_keys("data")
        occ = arrays[kd["occurrence"]]
        data_id = arrays[kd["values"]]
        ck("both events of the shared gate survive",
           data_id.tolist() == [[19168, 2, 295], [19168, 2, 295]], str(data_id.tolist()))
        ck("occurrence separates them", occ.tolist() == [0, 1], str(occ.tolist()))
        ck("data identity is unique only WITH occurrence",
           not eid.uniqueness_report(arrays[kd["key"]])["is_unique"], "control")

        ck("source label recorded",
           list(arrays[eid.SOURCE_LABELS_KEY]) == ["1X"], str(arrays[eid.SOURCE_LABELS_KEY]))
        ck("contract version recorded",
           str(arrays[eid.CONTRACT_VERSION_KEY]) == eid.IDENTITY_CONTRACT_VERSION)

        # Negative control: a target whose signal weights are in the other order must be REFUSED.
        bad = os.path.join(tmp, "bad_inventory.npz")
        w_truth = np.array([1.75, 0.90, 1.25], np.float32)
        np.savez_compressed(
            bad, w_truth=w_truth, pass_truth=np.array([True, True, True]),
            w_bkg=np.array([0.25, 0.50], np.float32),
            measured_pc=np.zeros((2, 12, 3), np.float32),
            sig_identity_hash=np.asarray(
                inventory_order_hash(w_truth, np.array([True, True, True]))),
            bkg_identity_hash=np.asarray(
                inventory_order_hash(np.array([0.25, 0.50], np.float32),
                                     np.arange(2, dtype=np.int64))),
            data_identity_hash=np.asarray(inventory_order_hash(np.zeros((2, 12, 3), np.float32))))
        try:
            exp.build_sidecar(_Args(root, bad, "1X"))
            ck("reordered target is refused", False, "build_sidecar returned instead of raising")
        except SystemExit as e:
            ck("reordered target is refused", "sig_identity_hash" in str(e), str(e)[:90])

        out = os.path.join(tmp, "sidecar.npz")
        exp.write_atomic(out, arrays)
        reread = np.load(out, allow_pickle=False)
        for inv, n in n_target.items():
            eid.verify_identity_block(inv, reread, n, order_hash_fn)
        ck("sidecar survives a write/read round trip", True)

    print(f"\n[smoke] {checks - len(failures)}/{checks} checks passed")
    for fmsg in failures:
        print(f"  FAILED {fmsg}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

"""OI-22 leg (a2): what the no-truth-leakage check can and cannot prove about the real object.

I SCOPED THIS AS "numpy-only, one streaming pass, cheap" AND THAT WAS WRONG. Measured
here rather than argued, because the correction is mine to make.

THE STRUCTURAL PROBLEM. assert_no_truth_leakage(event_reco, ...) takes `event_reco` --
the loader's OUTPUT. That array is not in the NPZ; it is derived. So "run the leakage
check on the real input" has two readings and they differ in what they prove:

  (A) build event_reco here with build_event_features, then assert.
      Statement 2 (PURITY) rebuilds from the same reco blocks with the SAME code and
      demands an exact match -- so if I built the input with that code, it passes BY
      CONSTRUCTION. Statement 2 is VACUOUS under (A). Statements 1 and 3 are not.
  (B) run the production loader build_fullevent_loaders on the real NPZ and check ITS
      output. Non-circular, and the only reading under which statement 2 means anything.
      That is a full loader pass over 49,152,885 events, not a read.

So the honest deliverable here is (A), clearly labelled, PLUS the control the orchestrator
asked for: demonstrate the detector FIRES on real-object data. A detector that has never
fired on this object proves nothing about it.

PREDECLARED:
  L1 leakage assert on a REAL slice, unmodified          expect PASS
  L2 CONTROL: truth injected into event_reco, real slice expect the detector to FIRE
  L3 CONTROL: all-NaN event_reco, real slice             expect FIRE (finiteness guard)
"""
import json
import os
import sys

import numpy as np

REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
NPZ = os.path.join(REPO, "nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz")
sys.path.insert(0, os.path.join(REPO, "nd-unfolding/pet"))
import fullevent_fps_dataloader as fe  # noqa: E402

N = 2_000_000          # contiguous real events; peak RSS is one decompressed member (~1.4 GB)

print("=== OI-22 leg (a2): leakage detector against REAL-OBJECT data ===\n")
z = np.load(NPZ, allow_pickle=False)
sl = {}
for k in ("reco_scalars", "reco_muon", "reco_vertex", "truth_scalars", "pass_reco",
          "measured_scalars", "data_muon", "data_vertex"):
    a = z[k]
    sl[k] = np.array(a[:N])
    print(f"  loaded {k:16s} full={a.shape}  slice={sl[k].shape}  dtype={a.dtype}")
    del a
z.close()

r = fe.evt_blocks(scalars=sl["reco_scalars"], muon=sl["reco_muon"], vertex=sl["reco_vertex"])
t = fe.evt_blocks(scalars=sl["truth_scalars"])
# build_event_features requires the DATA inventory too -- my first call passed None and it
# failed closed at assert_finite_event_scalars, which is the loader being right and me being
# wrong about its signature. The data leg is a separate inventory with its own row count.
d = fe.evt_blocks(scalars=sl["measured_scalars"], muon=sl["data_muon"],
                  vertex=sl["data_vertex"])
pr = sl["pass_reco"].astype(bool)
print(f"\n  pass_reco True: {int(pr.sum())} / {pr.size}")

er, et, ed, meta = fe.build_event_features(r, t, d, pass_reco=pr)
print(f"  event_reco {er.shape} {er.dtype} | event_truth {et.shape}")
print(f"  features: {meta['feature_names']}")


def arm(label, expectation, fn):
    try:
        fn()
        fired, detail = False, "returned without raising"
    except Exception as exc:
        fired, detail = True, f"{type(exc).__name__}: {str(exc)[:150]}"
    ok = (fired is True) if expectation == "FIRE" else (fired is False)
    print(f"  [{label}] expect={expectation:5s} fired={str(fired):5s} "
          f"{'as predeclared' if ok else '*** UNEXPECTED ***'}")
    print(f"      {detail}")
    return ok, fired, detail


print("\n-- arms --")
res = {}
res["L1"] = arm("L1 real slice, unmodified", "PASS",
                lambda: fe.assert_no_truth_leakage(er, r, t, fe.DEFAULT_EVT_FEATURES,
                                                   pass_reco=pr))
leaked = er.copy()
leaked[:, 0] = et[:, 0]          # substitute the truth pT into the reco leg's shared column
res["L2"] = arm("L2 truth injected      ", "FIRE",
                lambda: fe.assert_no_truth_leakage(leaked, r, t, fe.DEFAULT_EVT_FEATURES,
                                                   pass_reco=pr))
nan = np.full_like(er, np.nan)
res["L3"] = arm("L3 all-NaN event_reco  ", "FIRE",
                lambda: fe.assert_no_truth_leakage(nan, r, t, fe.DEFAULT_EVT_FEATURES,
                                                   pass_reco=pr))

allok = all(v[0] for v in res.values())
out = {
    "what": "OI-22 leg (a2): leakage detector exercised on REAL-OBJECT data (contiguous slice)",
    "object": NPZ,
    "slice_events": N,
    "of_total_events": 49152885,
    "arms": {k: {"as_predeclared": v[0], "fired": v[1], "detail": v[2]} for k, v in res.items()},
    "all_arms_as_predeclared": allok,
    "WHAT_THIS_PROVES": [
        "The leakage detector RUNS and FIRES on real-object data, not only on fixtures -- L2 and "
        "L3 are the demonstrated failing directions on this NPZ's own arrays.",
        "Statement 3 (DISSIMILARITY on shared columns) is a real property of the real data and "
        "holds on this slice.",
    ],
    "WHAT_THIS_DOES_NOT_PROVE": [
        "Statement 2 (PURITY) is VACUOUS here: event_reco was built by the same code the assert "
        "rebuilds with, so an exact match is guaranteed by construction. Only the production "
        "loader's output can make statement 2 meaningful.",
        f"This is a {N}-event contiguous slice, not all 49,152,885 events. It is a demonstration "
        "that the detector engages the real object, NOT a whole-object proof.",
        "no-truth-leakage on the real publication input therefore remains NOT PROVED.",
    ],
}
print(f"\n=== arms as predeclared: {sum(v[0] for v in res.values())}/3 ===")
print("\n<<<RECEIPT_JSON>>>")
print(json.dumps(out, indent=1, sort_keys=True))

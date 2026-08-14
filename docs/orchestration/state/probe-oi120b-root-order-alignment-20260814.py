"""OI-22 leg (b) / OI-120(b): event-by-event ORDER proof of the G2 full-event NPZ against its
source ROOT. Lane D. READ-ONLY -- opens the merged ROOT and the NPZ, writes only a receipt.

THE GAP, named by the repo itself. FULL_EVENT_FEATURE_CONTRACT.md:214-215:
    "row-count alignment is enforced; a full event-by-event order proof (as
     build_bkgsub_pointcloud_input.py did against the ROOT) is a P5B hardening item."
And fullevent_dump_contract.py:99-112 checks identity via (w_truth, pass_truth) for signal,
measured_pc for data, (w_bkg, bkg_indices) for background -- so an INDEPENDENTLY PERMUTED
FEATURE BLOCK evades all three. That is the hole this closes.

METHOD, taken from the precedent the contract names rather than invented: re-walk each source
tree in ENTRY ORDER applying the SAME retention gate as dump_pointcloud_inputs.py, rebuild each
per-event row with the SAME production row-builders, and compare element-wise against the NPZ
member in its stored order.

WHY REUSING THE PRODUCTION GATE IS CORRECT AND NOT CIRCULAR. The claim under test is ORDERING:
does stored row k correspond to the k-th retained ROOT entry? Reusing `select_signal_row` and
the `*_row` builders is what isolates that claim -- a reimplemented gate would retain a
different set and the comparison would fail for a reason that has nothing to do with order.
THE LIMIT THIS IMPOSES, stated rather than discovered: this proves ORDER, not gate-correctness.
A bug inside select_signal_row is replicated identically on both sides and cannot be seen here.

CONTROLS, predeclared. A match proves nothing unless a mismatch is demonstrable on this data:
  A1  compare as-is                        expect EXACT
  A2  roll the ROOT-side array by 1 row    expect MISMATCH  (adjacent-shift sensitivity)
  A3  swap two interior rows               expect MISMATCH  (pure permutation, counts identical)
A3 is the one that matters: it is the exact defect the existing identity checks cannot see.
"""
import hashlib
import json
import os
import sys
import time

import numpy as np

REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
ROOT_IN = os.path.join(REPO, "nd-unfolding/g2_fullevent/merged/"
                             "runEventLoopOmniFold_G2_FPS_MEFHC.root")
NPZ = os.path.join(REPO, "nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz")
sys.path.insert(0, os.path.join(REPO, "nd-unfolding/pet"))
sys.path.insert(0, os.path.join(REPO, "nd-unfolding"))

import dump_pointcloud_inputs as DP  # noqa: E402  (production gate + row builders)

LIMIT = int(os.environ.get("LEGB_LIMIT", "0"))       # 0 = all entries; >0 = smoke test


def sha256_file(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def walk_signal(f, limit=0):
    """Re-walk mc_signal_reco in entry order under the production retention gate."""
    from array import array
    t = f.Get("mc_signal_reco")
    if not t:
        raise SystemExit("[legb] missing tree 'mc_signal_reco'")
    n = int(t.GetEntries())
    if limit:
        n = min(n, limit)

    ssc = {b: array("d", [0.0]) for b in DP.SIG_SCALAR_BRANCHES}
    tsc = {b: array("d", [0.0]) for b in DP.TRUTH_SCALAR_BRANCHES}
    mub = {b: array("d", [0.0]) for b in DP.RECO_MUON_BRANCHES if b != "mu_reco_minos_ok"}
    vtb = {b: array("d", [0.0]) for b in DP.RECO_VERTEX_BRANCHES}
    minos = array("B", [0])
    sp, wt, wr = array("B", [0]), array("d", [0.0]), array("d", [0.0])
    for d in (ssc, tsc, mub, vtb):
        for b, a in d.items():
            t.SetBranchAddress(b, a)
    t.SetBranchAddress("sim_pass", sp)
    t.SetBranchAddress("w_truth", wt)
    t.SetBranchAddress("w_reco", wr)
    t.SetBranchAddress("mu_reco_minos_ok", minos)

    out = {"truth_scalars": np.zeros((n, DP.NUM_SCALAR), np.float32),
           "reco_scalars": np.zeros((n, DP.NUM_SCALAR), np.float32),
           "reco_muon": np.zeros((n, DP.NUM_MUON), np.float32),
           "reco_vertex": np.zeros((n, DP.NUM_VTX), np.float32),
           "w_truth": np.zeros(n, np.float32), "w_reco": np.zeros(n, np.float32),
           "pass_reco": np.zeros(n, bool), "pass_truth": np.zeros(n, bool)}
    k, t0 = 0, time.time()
    for i in range(n):
        t.GetEntry(i)
        keep, pr, ptru = DP.select_signal_row(ssc["sim"][0], ssc["sim_pz"][0], sp[0],
                                              tsc["MC"][0], tsc["MC_pz"][0])
        if not keep:
            continue
        # assembled exactly as _reco_row does: non-minos branches in order, minos appended
        muon_vals = [mub[b][0] for b in DP.RECO_MUON_BRANCHES if b != "mu_reco_minos_ok"]
        muon_vals.append(float(minos[0]))
        out["truth_scalars"][k] = tuple(float(tsc[b][0]) for b in DP.TRUTH_SCALAR_BRANCHES)
        out["reco_scalars"][k] = DP.reco_scalar_row(pr, [ssc[b][0]
                                                         for b in DP.SIG_SCALAR_BRANCHES])
        out["reco_muon"][k] = DP.reco_muon_row(pr, muon_vals)
        out["reco_vertex"][k] = DP.reco_vertex_row(pr, [vtb[b][0] for b in DP.RECO_VERTEX_BRANCHES])
        out["w_truth"][k] = float(wt[0]); out["w_reco"][k] = float(wr[0])
        out["pass_reco"][k] = pr; out["pass_truth"][k] = ptru
        k += 1
        if i and i % 2_000_000 == 0:
            print(f"  [legb] signal {i}/{n} kept={k} ({time.time() - t0:.0f}s)", flush=True)
    for key in out:
        out[key] = out[key][:k]
    print(f"[legb] signal walk done: kept {k}/{n} in {time.time() - t0:.0f}s", flush=True)
    return out


def walk_data(f, limit=0):
    """Re-walk the data tree under the production gate (measured_pass != 0 AND in-domain)."""
    from array import array
    t = f.Get("data")
    if not t:
        raise SystemExit("[legb] missing tree 'data'")
    n = int(t.GetEntries())
    if limit:
        n = min(n, limit)
    dsc = {b: array("d", [0.0]) for b in DP.DATA_SCALAR_BRANCHES}
    mub = {b: array("d", [0.0]) for b in DP.RECO_MUON_BRANCHES if b != "mu_reco_minos_ok"}
    vtb = {b: array("d", [0.0]) for b in DP.RECO_VERTEX_BRANCHES}
    minos = array("B", [0])
    dp = array("B", [0])
    for d in (dsc, mub, vtb):
        for b, a in d.items():
            t.SetBranchAddress(b, a)
    t.SetBranchAddress("measured_pass", dp)
    t.SetBranchAddress("mu_reco_minos_ok", minos)
    out = {"measured_scalars": np.zeros((n, DP.NUM_SCALAR), np.float32),
           "data_muon": np.zeros((n, DP.NUM_MUON), np.float32),
           "data_vertex": np.zeros((n, DP.NUM_VTX), np.float32)}
    k, t0 = 0, time.time()
    for i in range(n):
        t.GetEntry(i)
        if dp[0] == 0:
            continue
        if not DP.in_fps_domain(dsc["measured"][0], dsc["measured_pz"][0]):
            continue
        out["measured_scalars"][k] = tuple(float(dsc[b][0]) for b in DP.DATA_SCALAR_BRANCHES)
        # kept data rows are pass_reco=True by construction, as _read_data_inventory does
        mv = [mub[b][0] for b in DP.RECO_MUON_BRANCHES if b != "mu_reco_minos_ok"]
        mv.append(float(minos[0]))
        out["data_muon"][k] = DP.reco_muon_row(True, mv)
        out["data_vertex"][k] = DP.reco_vertex_row(
            True, [vtb[b][0] for b in DP.RECO_VERTEX_BRANCHES])
        k += 1
        if i and i % 2_000_000 == 0:
            print(f"  [legb] data {i}/{n} kept={k} ({time.time() - t0:.0f}s)", flush=True)
    for key in out:
        out[key] = out[key][:k]
    print(f"[legb] data walk done: kept {k}/{n} in {time.time() - t0:.0f}s", flush=True)
    return out


def compare(name, root_arr, npz_arr):
    a, b = np.asarray(root_arr), np.asarray(npz_arr)
    r = {"block": name, "root_shape": list(a.shape), "npz_shape": list(b.shape)}
    if a.shape != b.shape:
        r.update(exact=False, reason="shape mismatch")
        return r
    eq = (a == b) | (np.isnan(a) & np.isnan(b) if a.dtype.kind == "f" else False)
    rowok = eq.all(axis=tuple(range(1, eq.ndim))) if eq.ndim > 1 else eq
    nmis = int((~rowok).sum())
    r.update(exact=bool(nmis == 0), n_mismatch_rows=nmis,
             first_mismatch_rows=[int(i) for i in np.flatnonzero(~rowok)[:10]])
    return r


def controls(name, root_arr, npz_arr):
    """A match is worthless unless a mismatch is demonstrable ON THIS DATA."""
    a = np.asarray(root_arr)
    out = {}
    rolled = np.roll(a, 1, axis=0)
    out["A2_roll_by_1"] = {"changed_array": not np.array_equal(a, rolled),
                           "detected": not compare(name, rolled, npz_arr)["exact"]}
    # A3 must swap rows that actually DIFFER. Swapping two equal rows is not a mutation, and a
    # control that did not mutate reports a pass against nothing (BEN-181). This bit first: on
    # the boolean blocks (pass_reco/pass_truth) the naive indices 17 and n//2 held the same
    # value, so the "permutation" was a no-op and the control silently proved nothing.
    sw = a.copy()
    i = 17 if a.shape[0] > 100 else 0
    ref = a[i]
    diff = np.flatnonzero(~(a == ref).reshape(a.shape[0], -1).all(axis=1))
    if diff.size:
        j = int(diff[diff.size // 2])
        sw[[i, j]] = sw[[j, i]]
        out["A3_swap_two_rows"] = {
            "changed_array": not np.array_equal(a, sw), "swapped": [int(i), j],
            "detected": not compare(name, sw, npz_arr)["exact"]}
    else:
        # every row equals row i: the array is constant and carries NO order information, so no
        # permutation of it is detectable by anyone. Reported as inapplicable, not as a failure.
        out["A3_swap_two_rows"] = {
            "changed_array": False, "detected": None, "applicable": False,
            "why": "array is constant; a permutation of it is undetectable in principle"}
    return out


def main():
    import ROOT  # noqa: F401  (lazy; this script is cluster-only by design)
    print("=== OI-22 leg (b): event-by-event ORDER proof against the source ROOT ===")
    print(f"root : {ROOT_IN}")
    print(f"npz  : {NPZ}")
    if LIMIT:
        print(f"*** SMOKE TEST: LEGB_LIMIT={LIMIT} entries per tree. NOT a proof. ***")

    f = ROOT.TFile.Open(ROOT_IN)
    if not f or f.IsZombie():
        raise SystemExit(f"[legb] cannot open {ROOT_IN}")
    sig = walk_signal(f, LIMIT)
    dat = walk_data(f, LIMIT)
    f.Close()

    z = np.load(NPZ, allow_pickle=False)
    results, ctl = {}, {}
    for name, arr in list(sig.items()) + list(dat.items()):
        if name not in z.files:
            results[name] = {"block": name, "exact": None, "reason": "absent from NPZ"}
            continue
        npz_arr = z[name][:arr.shape[0]] if LIMIT else z[name]
        results[name] = compare(name, arr, npz_arr)
        ctl[name] = controls(name, arr, npz_arr)
        st = results[name]
        print(f"  {name:18s} exact={st.get('exact')}  "
              f"mismatch_rows={st.get('n_mismatch_rows')}  "
              f"A2={ctl[name]['A2_roll_by_1']['detected']} "
              f"A3={ctl[name]['A3_swap_two_rows']['detected']}")
        del npz_arr
    z.close()

    all_exact = all(v.get("exact") for v in results.values() if v.get("exact") is not None)
    # a control marked inapplicable (constant array) is skipped, not counted as a pass
    all_ctl = all(c[k]["detected"] and c[k]["changed_array"]
                  for c in ctl.values() for k in ("A2_roll_by_1", "A3_swap_two_rows")
                  if c[k].get("applicable", True))
    receipt = {
        "what": "OI-22 leg (b): per-block event-by-event ORDER proof, G2 NPZ vs source ROOT",
        "produced_by": "Lane D. Read-only: ROOT and NPZ opened; nothing written but this receipt.",
        "SMOKE_TEST": bool(LIMIT), "entry_limit": LIMIT,
        "root": {"path": ROOT_IN, "sha256": sha256_file(ROOT_IN) if not LIMIT else None},
        "npz": {"path": NPZ, "sha256": sha256_file(NPZ) if not LIMIT else None},
        "blocks": results, "controls": ctl,
        "all_blocks_exact": all_exact, "all_controls_fired": all_ctl,
        "VERDICT": ("ORDER PROVED ON REAL INPUT" if (all_exact and all_ctl and not LIMIT)
                    else "NOT PROVED"),
        "SCOPE_LIMITS": [
            "Proves ORDER, not gate-correctness: the production retention gate "
            "(select_signal_row / measured_pass+in_fps_domain) is REUSED on both sides "
            "deliberately, so a bug inside it is replicated and invisible here.",
            "Covers the SCALAR/muon/vertex blocks. The point-cloud blocks (part_reco, part_gen) "
            "are NOT covered by this run.",
            "Background block not covered by this run.",
        ],
    }
    print(f"\n=== VERDICT: {receipt['VERDICT']} "
          f"(blocks exact={all_exact}, controls fired={all_ctl}) ===")
    print("\n<<<RECEIPT_JSON>>>")
    print(json.dumps(receipt, indent=1, sort_keys=True, default=str))


if __name__ == "__main__":
    main()

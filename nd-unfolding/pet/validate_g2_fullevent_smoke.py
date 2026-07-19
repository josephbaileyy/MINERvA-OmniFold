#!/usr/bin/env python3
"""Fail-closed runtime validator for the G2 full-event extended-FPS smoke ROOT.

Runs under PyROOT (needs the root_6_28 env -> run on the compute node via
alloc_run.sh, NOT the login node). Opens the smoke omnifile produced by
`runEventLoopOmniFold` with MNV101_DUMP_POINTCLOUD=1 + MNV101_FULL_PHASE_SPACE=1
and fails closed on any violated invariant from the G2 dump contract.

Usage:  python3 validate_g2_fullevent_smoke.py <omnifile.root> [receipt.json] [sample]
Exit 0 = PASS, 1 = FAIL, 2 = could not open / structural error.
"""
import json
import sys

import ROOT

REPORT = {"file": None, "status": "UNKNOWN", "checks": [], "counts": {}}
_fail = []


def ck(name, cond, detail=""):
    ok = bool(cond)
    REPORT["checks"].append({"name": name, "ok": ok, "detail": str(detail)})
    if not ok:
        _fail.append(f"{name}: {detail}")
    return ok


def branch_names(tree):
    return {b.GetName() for b in tree.GetListOfBranches()}


def get_param(f, name, kind):
    obj = f.Get(name)
    if obj is None:
        return None
    try:
        return obj.GetVal()
    except AttributeError:
        return obj.GetTitle()  # TNamed


def uchar_value(value):
    """Normalize PyROOT UChar_t proxies across ROOT/Python bindings."""
    if isinstance(value, str):
        if len(value) != 1:
            raise ValueError(f"unexpected UChar_t string representation: {value!r}")
        return ord(value)
    if isinstance(value, (bytes, bytearray)):
        if len(value) != 1:
            raise ValueError(f"unexpected UChar_t byte representation: {value!r}")
        return value[0]
    return int(value)


def main():
    path = sys.argv[1]
    receipt = sys.argv[2] if len(sys.argv) > 2 else None
    sample = int(sys.argv[3]) if len(sys.argv) > 3 else 20000
    REPORT["file"] = path

    f = ROOT.TFile.Open(path)
    if not f or f.IsZombie():
        print(f"FAIL: cannot open {path}")
        REPORT["status"] = "FAIL_OPEN"
        if receipt:
            open(receipt, "w").write(json.dumps(REPORT, indent=2))
        return 2

    # ---- 1. four trees + positive POT ----
    trees = {n: f.Get(n) for n in ("mc_truth_denom", "mc_signal_reco",
                                   "mc_background", "data")}
    for n, t in trees.items():
        ck(f"tree_present:{n}", t is not None and t.InheritsFrom("TTree"))
    if any(t is None for t in trees.values()):
        REPORT["status"] = "FAIL"
        _finish(f, receipt)
        return 1
    n_truth = trees["mc_truth_denom"].GetEntries()
    n_sig = trees["mc_signal_reco"].GetEntries()
    n_bkg = trees["mc_background"].GetEntries()
    n_data = trees["data"].GetEntries()
    REPORT["counts"] = {"mc_truth_denom": n_truth, "mc_signal_reco": n_sig,
                        "mc_background": n_bkg, "data": n_data}
    mcpot = get_param(f, "mcPOTUsed", "d")
    datapot = get_param(f, "dataPOTUsed", "d")
    REPORT["counts"]["mcPOTUsed"] = mcpot
    REPORT["counts"]["dataPOTUsed"] = datapot
    ck("mcPOT_positive", mcpot is not None and mcpot > 0, mcpot)
    ck("dataPOT_positive", datapot is not None and datapot > 0, datapot)
    for n, c in (("mc_truth_denom", n_truth), ("mc_signal_reco", n_sig),
                 ("mc_background", n_bkg), ("data", n_data)):
        ck(f"tree_nonempty:{n}", c > 0, c)

    # ---- 2. exact provenance metadata ----
    ck("petSchemaVersion", get_param(f, "petSchemaVersion", "s") == "g2-fullevent-v1",
       get_param(f, "petSchemaVersion", "s"))
    ck("hasFullEventSchema", get_param(f, "hasFullEventSchema", "i") == 1,
       get_param(f, "hasFullEventSchema", "i"))
    ck("fullPhaseSpace", get_param(f, "fullPhaseSpace", "i") == 1,
       get_param(f, "fullPhaseSpace", "i"))

    # ---- 3. distinct schemas: required present + forbidden absent ----
    b_truth = branch_names(trees["mc_truth_denom"])
    b_sig = branch_names(trees["mc_signal_reco"])
    b_bkg = branch_names(trees["mc_background"])
    b_data = branch_names(trees["data"])
    reco_mu = {"mu_reco_px", "mu_reco_py", "mu_reco_pz", "mu_reco_E", "mu_reco_phi",
               "mu_reco_qp", "mu_reco_minos_ok", "vtx_reco_x", "vtx_reco_y", "vtx_reco_z"}
    true_mu = {"mu_true_px", "mu_true_py", "mu_true_pz", "mu_true_E", "mu_true_phi",
               "vtx_true_x", "vtx_true_y", "vtx_true_z"}
    cloud5 = {"part_reco_E", "part_reco_pos", "part_reco_z", "part_reco_view", "part_reco_time"}
    forbidden = {"mu_true_qp", "mu_true_minos", "mu_true_minos_ok", "mu_true_range",
                 "mu_true_charge", "part_gen_view", "part_gen_time"}

    ck("truth_has_truth_muon", true_mu <= b_truth, sorted(true_mu - b_truth))
    ck("truth_has_mc_id", {"mc_run", "mc_subrun", "mc_nthEvtInFile"} <= b_truth)
    ck("truth_no_reco_muon", not (reco_mu & b_truth), sorted(reco_mu & b_truth))
    ck("truth_no_reco_cloud", not (cloud5 & b_truth), sorted(cloud5 & b_truth))

    ck("sig_has_reco_muon", reco_mu <= b_sig, sorted(reco_mu - b_sig))
    ck("sig_has_truth_muon", true_mu <= b_sig, sorted(true_mu - b_sig))
    ck("sig_has_cloud5", cloud5 <= b_sig, sorted(cloud5 - b_sig))
    ck("sig_has_truthcloud", {"part_gen_E", "part_gen_pdg"} <= b_sig)
    ck("sig_has_mc_id", {"mc_run", "mc_subrun", "mc_nthEvtInFile"} <= b_sig)

    ck("bkg_has_reco_muon", reco_mu <= b_bkg, sorted(reco_mu - b_bkg))
    ck("bkg_has_cloud5", cloud5 <= b_bkg, sorted(cloud5 - b_bkg))
    ck("bkg_has_wbkg", "w_bkg" in b_bkg)
    ck("bkg_no_truth_muon", not (true_mu & b_bkg), sorted(true_mu & b_bkg))
    ck("bkg_has_mc_id", {"mc_run", "mc_subrun", "mc_nthEvtInFile"} <= b_bkg)

    ck("data_has_reco_muon", reco_mu <= b_data, sorted(reco_mu - b_data))
    ck("data_has_cloud5", cloud5 <= b_data, sorted(cloud5 - b_data))
    ck("data_has_real_id", {"ev_run", "ev_subrun", "ev_gate"} <= b_data,
       sorted({"ev_run", "ev_subrun", "ev_gate"} - b_data))
    ck("data_no_truth_side", not (true_mu & b_data), sorted(true_mu & b_data))
    ck("data_no_mc_id", "mc_run" not in b_data)
    ck("data_no_truthcloud", "part_gen_E" not in b_data)

    allb = b_truth | b_sig | b_bkg | b_data
    ck("no_forbidden_counterpart", not (forbidden & allb), sorted(forbidden & allb))

    # ---- 4. reco-schema observable parity (data vs reco-signal) ----
    ck("data_reco_parity", (reco_mu | cloud5) <= (b_data & b_sig & b_bkg))

    # ---- 5. sampled per-row: equal cloud vector lengths + valid reco muon ----
    def cloud_len_ok(tree, n_scan, need_valid_mu):
        seen = 0
        bad = 0
        mu_ok = 0
        for i, ev in enumerate(tree):
            if i >= n_scan:
                break
            le = len(ev.part_reco_E)
            if not (le == len(ev.part_reco_pos) == len(ev.part_reco_z)
                    == len(ev.part_reco_view) == len(ev.part_reco_time)):
                bad += 1
            seen += 1
            if need_valid_mu:
                # data & bkg rows always pass selection -> reco muon finite/non-sentinel
                if ev.mu_reco_E > 0 and abs(ev.mu_reco_px) < 1e8 and ev.mu_reco_px != -9999.0:
                    mu_ok += 1
        return seen, bad, mu_ok

    s_seen, s_bad, _ = cloud_len_ok(trees["mc_signal_reco"], sample, False)
    ck("sig_cloud_lengths_equal", s_bad == 0, f"{s_bad}/{s_seen} rows unequal E/pos/z/view/time")
    b_seen, b_bad, b_mu = cloud_len_ok(trees["mc_background"], sample, True)
    ck("bkg_cloud_lengths_equal", b_bad == 0, f"{b_bad}/{b_seen} rows unequal")
    ck("bkg_reco_muon_valid", b_seen == 0 or b_mu == b_seen, f"{b_mu}/{b_seen} valid reco muon")
    d_seen, d_bad, d_mu = cloud_len_ok(trees["data"], sample, True)
    ck("data_cloud_lengths_equal", d_bad == 0, f"{d_bad}/{d_seen} rows unequal")
    ck("data_reco_muon_valid", d_seen == 0 or d_mu == d_seen, f"{d_mu}/{d_seen} valid reco muon")

    # ev_* identity actually populated (not all zero)
    nz = 0
    for i, ev in enumerate(trees["data"]):
        if i >= min(sample, 5000):
            break
        if ev.ev_run != 0 or ev.ev_gate != 0:
            nz += 1
    ck("data_ev_id_populated", nz > 0, f"{nz} rows with nonzero ev_run/ev_gate")

    # cluster_view/time actually populated on some reco row (values not all zero)
    seen_view_vals = seen_time_vals = 0
    for i, ev in enumerate(trees["data"]):
        if i >= min(sample, 20000) or (seen_view_vals and seen_time_vals):
            break
        if len(ev.part_reco_view) and any(v != 0 for v in ev.part_reco_view):
            seen_view_vals = 1
        if len(ev.part_reco_time) and any(t != 0 for t in ev.part_reco_time):
            seen_time_vals = 1
    ck("cluster_view_populated", seen_view_vals == 1)
    ck("cluster_time_populated", seen_time_vals == 1)

    # ---- 6. native appended misses (last nTruthOnlyMisses rows) ----
    n_miss = get_param(f, "nTruthOnlyMisses", "l")
    has_miss = get_param(f, "hasTruthOnlyMisses", "i")
    REPORT["counts"]["nTruthOnlyMisses"] = n_miss
    ck("hasTruthOnlyMisses_flag", has_miss == 1, has_miss)
    ck("nTruthOnlyMisses_positive", n_miss is not None and n_miss > 0, n_miss)
    if n_miss and n_miss > 0:
        t = trees["mc_signal_reco"]
        start = n_sig - n_miss
        inspect = min(n_miss, 5000)
        bad_pass = bad_sent = bad_reco_empty = bad_truth = 0
        for j in range(inspect):
            t.GetEntry(start + j)
            if uchar_value(t.sim_pass) != 0:
                bad_pass += 1
            if not (t.sim == -9999.0 and t.mu_reco_px == -9999.0 and t.mu_reco_E == -9999.0
                    and t.vtx_reco_x == -9999.0 and uchar_value(t.mu_reco_minos_ok) == 0):
                bad_sent += 1
            if not (len(t.part_reco_E) == 0 and len(t.part_reco_view) == 0
                    and len(t.part_reco_time) == 0):
                bad_reco_empty += 1
            # cached truth identity/muon valid (mc_run set, truth muon not sentinel)
            if not (t.mc_run != 0 and t.mu_true_E != -9999.0 and abs(t.mu_true_E) < 1e8):
                bad_truth += 1
        ck("miss_sim_pass_zero", bad_pass == 0, f"{bad_pass}/{inspect}")
        ck("miss_reco_sentinels", bad_sent == 0, f"{bad_sent}/{inspect}")
        ck("miss_reco_vectors_empty", bad_reco_empty == 0, f"{bad_reco_empty}/{inspect}")
        ck("miss_truth_identity_valid", bad_truth == 0, f"{bad_truth}/{inspect}")

    # ---- 7. Phase-18.2 completeness invariant: |signal| == |truth_denom| ----
    ck("c_global_count_invariant", n_sig == n_truth,
       f"mc_signal_reco={n_sig} vs mc_truth_denom={n_truth}")

    _finish(f, receipt)
    return 0 if not _fail else 1


def _finish(f, receipt):
    REPORT["status"] = "PASS" if not _fail else "FAIL"
    REPORT["n_failed"] = len(_fail)
    REPORT["n_checks"] = len(REPORT["checks"])
    if receipt:
        open(receipt, "w").write(json.dumps(REPORT, indent=2))
    print(json.dumps({"status": REPORT["status"], "n_checks": REPORT["n_checks"],
                      "n_failed": REPORT["n_failed"], "counts": REPORT["counts"]},
                     indent=2))
    if _fail:
        print("FAILURES:")
        for x in _fail:
            print("  -", x)
    try:
        f.Close()
    except Exception:
        pass


if __name__ == "__main__":
    sys.exit(main())

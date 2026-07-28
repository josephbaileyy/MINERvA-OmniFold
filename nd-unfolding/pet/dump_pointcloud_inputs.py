#!/usr/bin/env python3
"""Build padded point-cloud OmniFold inputs from a MNV101_DUMP_POINTCLOUD omnifile.

Phase 3 reader: the event loop (runEventLoopOmniFold.cpp, MNV101_DUMP_POINTCLOUD=1)
writes per-event variable-length vectors part_gen_{E,px,py,pz,pdg} (truth FS hadrons,
muon+nu removed) and part_reco_{E,x,y,z} (reco recoil clusters) on mc_signal_reco, and
part_reco_{E,x,y,z} on data. This loops those trees with the SAME (pt,pz) gating as the
scalar nd driver, truncates/zero-pads each cloud to a fixed num_part (keeping the
highest-energy constituents), and writes of_inputs_pc.npz for minerva_pet_dataloader.py
(pointcloud mode) -> the vendored PET.

  python dump_pointcloud_inputs.py --omnifile runEventLoopOmniFold_PC_MEFHC.root \
      --num-part 12 --out of_inputs_pc.npz
"""
import argparse
import math
import os
import sys
from array import array

import numpy as np
# NOTE: `import ROOT` is deferred into main() (PyROOT is unavailable on the login node and the
# G2 full-event read is RUNTIME-BLOCKED); the pure write/schema contract below imports cleanly.

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
for p in (f"{_REPO}/2d-unfolding", f"{_REPO}/nd-unfolding", f"{_REPO}/nd-unfolding/pet"):
    if p not in sys.path:
        sys.path.insert(0, p)
import fullevent_dump_contract as fdc  # noqa: E402  (login-safe: no ROOT/TF)


def _read_g2_markers(f):
    """Read the G2 full-event schema markers from a ROOT file: TNamed petSchemaVersion,
    TParameter<int> hasFullEventSchema / fullPhaseSpace. Missing markers -> {} -> fail closed."""
    meta = {}
    nm = f.Get("petSchemaVersion")
    if nm:
        meta["petSchemaVersion"] = str(nm.GetTitle())
    for k in ("hasFullEventSchema", "fullPhaseSpace"):
        p = f.Get(k)
        if p:
            meta[k] = int(p.GetVal())
    return meta

GEN_FEATS = ["part_gen_E", "part_gen_px", "part_gen_py", "part_gen_pz", "part_gen_pdg"]
RECO_FEATS = ["part_reco_E", "part_reco_pos", "part_reco_z"]

# ============================================================================================
# G2 full-event schema (publication default). AUTHORITATIVE branch names are Agent-E's C++ dump
# (`MINERvA101/.../runEventLoopOmniFold.cpp`, MNV101_DUMP_POINTCLOUD=1 + MNV101_FULL_PHASE_SPACE=1;
# see pet/G2_FULLEVENT_CPP_DUMP_STATUS.md and the hash-bound pet/validate_g2_fullevent_smoke.py
# that PASSED on all twelve production ROOTs). The four trees are mc_truth_denom / mc_signal_reco
# / mc_background / data; mc_truth_denom is the normalization denominator only (|mc_signal_reco| ==
# |mc_truth_denom| Phase-18.2 c-invariant), so the point-cloud inventory reads mc_signal_reco (reco
# side + appended native truth-only misses + truth cloud), data, and mc_background.
G2_ESTIMATOR_FINGERPRINT = "pet-fullevent-fps-v1"   # FULL schema; reduced cross-check is distinct
SENTINEL = -9999.0
# Retained extended-FPS domain = min/max of the canonical FPS reporting grid. A row whose LIVE
# reco/truth (pT, p_parallel) scalar falls outside this box is EXCLUDED before it can enter
# training (mandatory for the recovered 1D/1E/1F/1P playlists; conditional_use in
# docs/orchestration/state/g2-gate1-all12-validation-20260719.json).
FPS_PT_LO, FPS_PT_HI = 0.0, 30.0        # GeV
FPS_PZ_LO, FPS_PZ_HI = 0.0, 120.0       # GeV

# per-token reco cloud (mc_signal_reco reco side + data + mc_background share these exact names);
# col 0 (E) is the truncation/sort key. view = std::vector<int> (1=X/2=U/3=V), time = vector<double>.
RECO_CLOUD_BRANCHES = ("part_reco_E", "part_reco_pos", "part_reco_z")
RECO_VIEW_BRANCH, RECO_TIME_BRANCH = "part_reco_view", "part_reco_time"
TRUTH_CLOUD_BRANCHES = ("part_gen_E", "part_gen_px", "part_gen_py", "part_gen_pz", "part_gen_pdg")
# distinguished reco muon (7 cols) + reco vertex (3 cols); minos_ok is UChar_t. The truth muon is
# summarized in truth_scalars (pt, p_parallel) per the fullevent_dump_contract (no detector truth
# counterpart is manufactured).
RECO_MUON_BRANCHES = ("mu_reco_px", "mu_reco_py", "mu_reco_pz", "mu_reco_E",
                      "mu_reco_phi", "mu_reco_qp", "mu_reco_minos_ok")
RECO_VERTEX_BRANCHES = ("vtx_reco_x", "vtx_reco_y", "vtx_reco_z")
# scalar (pt, p_parallel, eavail, q3) coordinate branches per inventory (GeV). The FPS domain gate
# reads cols 0,1; eavail/q3 travel for downstream reporting/covariance binning only.
SIG_SCALAR_BRANCHES   = ("sim", "sim_pz", "sim_eavail", "sim_q3")
TRUTH_SCALAR_BRANCHES = ("MC", "MC_pz", "MC_eavail", "MC_q3")
DATA_SCALAR_BRANCHES  = ("measured", "measured_pz", "measured_eavail", "measured_q3")
BKG_SCALAR_BRANCHES   = ("sim_background", "sim_background_pz",
                         "sim_background_eavail", "sim_background_q3")
BKG_AUDIT_BRANCHES = ("bkg_nuPDG", "bkg_current", "bkg_inttype")   # AUDIT metadata; never features
NUM_MUON = len(RECO_MUON_BRANCHES)      # 7
NUM_VTX = 3
NUM_SCALAR = 4
NUM_TRUTH_FEAT = len(TRUTH_CLOUD_BRANCHES)   # 5 (E,px,py,pz,pdg)


def _pad_tokens(cols, num_part):
    """cols: list of equal-length per-feature sequences for ONE event, cols[0] the energy sort key.
    Return (num_part, len(cols)) float32, top-num_part tokens by cols[0] descending, zero-padded.
    Empty (n==0, e.g. a native miss's empty reco cloud) -> all zeros (the PET energy pad sentinel)."""
    nfeat = len(cols)
    n = len(cols[0])
    out = np.zeros((num_part, nfeat), np.float32)
    if n == 0:
        return out
    arr = np.array([list(c) for c in cols], np.float32).T          # (n, nfeat)
    if n > 1:
        arr = arr[np.argsort(-arr[:, 0], kind="stable")]           # stable => reproducible order
    k = min(n, num_part)
    out[:k] = arr[:k]
    return out


def pad_reco_cloud_tokens(part_E, part_pos, part_z, part_view, part_time, num_part):
    """Pad the FIVE aligned per-token reco vectors together (sorted by E desc) so reco_view/reco_time
    follow the SAME token permutation as the (E,pos,z) cloud. Returns (cloud(P,3), view(P,), time(P,))."""
    padded = _pad_tokens([part_E, part_pos, part_z, part_view, part_time], num_part)   # (P,5)
    return padded[:, :3], padded[:, 3], padded[:, 4]


def pad_truth_cloud_tokens(gen_E, gen_px, gen_py, gen_pz, gen_pdg, num_part):
    """part_gen (P,5) = (E,px,py,pz,pdg), sorted by E desc, zero-padded (raw PDG retained)."""
    return _pad_tokens([gen_E, gen_px, gen_py, gen_pz, gen_pdg], num_part)


def _finite(x):
    try:
        return math.isfinite(float(x))
    except (TypeError, ValueError):
        return False


def in_fps_domain(pt, ppar):
    """Retained extended-FPS domain membership: finite AND within [0,30]x[0,120] GeV."""
    return (_finite(pt) and _finite(ppar)
            and FPS_PT_LO <= float(pt) <= FPS_PT_HI and FPS_PZ_LO <= float(ppar) <= FPS_PZ_HI)


def select_signal_row(sim, sim_pz, sim_pass, MC, MC_pz):
    """Row-retention + pass-flags for a mc_signal_reco row over the retained FPS domain.
    Returns (keep, pass_reco, pass_truth):
      * pass_truth = truth (MC, MC_pz) in domain (non-finite / out-of-domain truth excluded);
      * pass_reco  = reco selected (sim_pass!=0) AND reco (sim, sim_pz) in domain;
      * keep       = pass_truth OR pass_reco.
    A native truth-only miss (sim_pass==0, sim=-9999 sentinel) -> pass_reco False, kept via
    pass_truth (native miss PRESERVED). An upstream-corrupt out-of-domain reco muon (e.g. the 1D
    ~2.96e6 GeV row) -> pass_reco False (EXCLUDED from step 1) yet may still enter step 2 through
    an in-domain truth."""
    pass_truth = in_fps_domain(MC, MC_pz)
    pass_reco = (int(sim_pass) != 0) and in_fps_domain(sim, sim_pz)
    return (pass_truth or pass_reco), bool(pass_reco), bool(pass_truth)


def reco_scalar_row(pass_reco, scalar_vals):
    """(pt,p_parallel,eavail,q3) reco scalars, or the -9999 SENTINEL 4-tuple for a !pass_reco row
    (no reconstructed muon) so a step-1 classifier trained on reco_scalars can NEVER read a truth
    quantity off a miss (leakage guard)."""
    if not pass_reco:
        return (SENTINEL,) * NUM_SCALAR
    return tuple(float(v) for v in scalar_vals)


def reco_muon_row(pass_reco, muon_vals):
    """7-col reco muon [px,py,pz,E,phi,qp,minos_ok]; SENTINEL (minos_ok=0) for a !pass_reco row."""
    if not pass_reco:
        return (SENTINEL,) * (NUM_MUON - 1) + (0.0,)
    return tuple(float(v) for v in muon_vals)


def reco_vertex_row(pass_reco, vtx_vals):
    """3-col reco vertex [x,y,z] mm; SENTINEL for a !pass_reco row."""
    if not pass_reco:
        return (SENTINEL,) * NUM_VTX
    return tuple(float(v) for v in vtx_vals)


def finalize_g2_arrays(sig, data, bkg, *, data_pot, mc_pot, pot_scale,
                       edges_pt, edges_pz, num_part):
    """Assemble the final G2 output arrays dict (fullevent_dump_contract.REQUIRED_KEYS + audit +
    POT provenance) from the three already-built, domain-filtered inventories, and compute the
    persisted identity/order hashes. Pure (no ROOT/TensorFlow) -> login-testable.

    `sig` keys: part_reco, reco_scalars, reco_muon, reco_vertex, reco_view, reco_time, part_gen,
                truth_scalars, pass_reco, pass_truth, w_truth, w_reco.
    `data` keys: measured_pc, measured_scalars, data_muon, data_vertex, data_view, data_time.
    `bkg` keys:  bkg_part_reco, bkg_reco_scalars, bkg_muon, bkg_vertex, bkg_view, bkg_time, w_bkg
                (+ bkg_nuPDG/current/inttype audit).

    WEIGHT NORMALIZATION (deliberate, uniform): w_truth / w_reco / w_bkg are the RAW literal ROOT
    per-event MC weights (NOT POT-scaled). Consumers apply pot_scale = data_pot/mc_pot explicitly
    (matches fullevent_fps_dataloader.build_negweight_refined_target's `pot_scale` parameter for the
    Option-A negweight injection -w_bkg*pot_scale, and the extraction normalization). data_pot,
    mc_pot, pot_scale ride along as provenance; step-1 DataLoader(normalize=True) is POT-invariant."""
    import fullevent_fps_dataloader as fed
    a = {}
    # ---- signal reco (RECO_KEYS) + truth cloud (TRUTH_KEYS) + signal globals ----
    a["part_reco"]     = np.asarray(sig["part_reco"], np.float32)
    a["reco_scalars"]  = np.asarray(sig["reco_scalars"], np.float32)
    a["reco_muon"]     = np.asarray(sig["reco_muon"], np.float32)
    a["reco_vertex"]   = np.asarray(sig["reco_vertex"], np.float32)
    a["reco_view"]     = np.asarray(sig["reco_view"], np.float32)
    a["reco_time"]     = np.asarray(sig["reco_time"], np.float32)
    a["part_gen"]      = np.asarray(sig["part_gen"], np.float32)
    a["truth_scalars"] = np.asarray(sig["truth_scalars"], np.float32)
    a["pass_reco"]     = np.asarray(sig["pass_reco"], bool)
    a["pass_truth"]    = np.asarray(sig["pass_truth"], bool)
    a["w_truth"]       = np.asarray(sig["w_truth"], np.float32)      # RAW (see docstring)
    a["w_reco"]        = np.asarray(sig["w_reco"], np.float32)       # RAW
    # ---- data (DATA_KEYS) ----
    a["measured_pc"]      = np.asarray(data["measured_pc"], np.float32)
    a["measured_scalars"] = np.asarray(data["measured_scalars"], np.float32)
    a["data_muon"]        = np.asarray(data["data_muon"], np.float32)
    a["data_vertex"]      = np.asarray(data["data_vertex"], np.float32)
    a["data_view"]        = np.asarray(data["data_view"], np.float32)
    a["data_time"]        = np.asarray(data["data_time"], np.float32)
    # ---- background (BKG_KEYS) — literal aligned Option-A injection inventory ----
    a["bkg_part_reco"]    = np.asarray(bkg["bkg_part_reco"], np.float32)
    a["bkg_reco_scalars"] = np.asarray(bkg["bkg_reco_scalars"], np.float32)
    a["bkg_muon"]         = np.asarray(bkg["bkg_muon"], np.float32)
    a["bkg_vertex"]       = np.asarray(bkg["bkg_vertex"], np.float32)
    a["bkg_view"]         = np.asarray(bkg["bkg_view"], np.float32)
    a["bkg_time"]         = np.asarray(bkg["bkg_time"], np.float32)
    a["w_bkg"]            = np.asarray(bkg["w_bkg"], np.float32)     # RAW MC background weight
    a["bkg_indices"]      = np.arange(a["w_bkg"].shape[0], dtype=np.int64)   # canonical full order
    for k in BKG_AUDIT_BRANCHES:                                    # audit-only, never features
        if k in bkg:
            a[k] = np.asarray(bkg[k], np.int64)
    # ---- globals / schema markers / edges / provenance ----
    a["edges_0"] = np.asarray(edges_pt, float)
    a["edges_1"] = np.asarray(edges_pz, float)
    a["petSchemaVersion"]      = np.asarray(fdc.G2_SCHEMA["petSchemaVersion"])
    a["hasFullEventSchema"]    = np.asarray(fdc.G2_SCHEMA["hasFullEventSchema"])
    a["fullPhaseSpace"]        = np.asarray(fdc.G2_SCHEMA["fullPhaseSpace"])
    a["estimator_fingerprint"] = np.asarray(G2_ESTIMATOR_FINGERPRINT)
    a["data_pot"]  = np.asarray(float(data_pot))
    a["mc_pot"]    = np.asarray(float(mc_pot))         # provenance
    a["pot_scale"] = np.asarray(float(pot_scale))      # provenance: consumers apply to raw weights
    a["num_part"]  = np.asarray(int(num_part))
    # ---- identity/order hashes over the EXACT stored arrays (must equal the contract recompute) ----
    a["sig_identity_hash"]  = np.asarray(fed.inventory_order_hash(a["w_truth"], a["pass_truth"]))
    a["data_identity_hash"] = np.asarray(fed.inventory_order_hash(a["measured_pc"]))
    a["bkg_identity_hash"]  = np.asarray(fed.inventory_order_hash(a["w_bkg"], a["bkg_indices"]))
    return a


# ============================================================================================
# G2 PyROOT inventory readers (RUNTIME — need PyROOT on a COMPUTE node; NOT login-safe). Each reads
# one tree's aligned branches, applies the retained-FPS-domain row gate, and returns a dict whose
# keys are the FINAL contract output names (so finalize_g2_arrays is a thin, pure assembler).
# ============================================================================================
def _require_branches(tree, tname, names):
    missing = [b for b in names if not tree.GetBranch(b)]
    if missing:
        raise SystemExit(f"[G2-FAIL] tree '{tname}' missing required branch(es) {missing} -- the "
                         f"ROOT is not a G2 full-event dump (fail closed).")


def _bind_reco_block(tree):
    """Bind the reco cloud/view/time/muon/vertex/scalar buffers shared by mc_signal_reco (reco
    side), data, and mc_background. Returns a buffers dict for per-row reads."""
    import ROOT
    B = {"cloud": {b: ROOT.std.vector("double")() for b in RECO_CLOUD_BRANCHES},
         "view": ROOT.std.vector("int")(), "time": ROOT.std.vector("double")(),
         "muon": {b: array("d", [0.0]) for b in RECO_MUON_BRANCHES if b != "mu_reco_minos_ok"},
         "minos": array("B", [0]),
         "vtx": {b: array("d", [0.0]) for b in RECO_VERTEX_BRANCHES}}
    for b, v in B["cloud"].items():
        tree.SetBranchAddress(b, v)
    tree.SetBranchAddress(RECO_VIEW_BRANCH, B["view"])
    tree.SetBranchAddress(RECO_TIME_BRANCH, B["time"])
    for b, a in {**B["muon"], **B["vtx"]}.items():
        tree.SetBranchAddress(b, a)
    tree.SetBranchAddress("mu_reco_minos_ok", B["minos"])
    return B


def _reco_row(B, pass_reco, num_part):
    """Assemble (cloud, view, time, muon, vertex) for ONE reco row from bound buffers. A !pass_reco
    row (native miss / out-of-domain reco) gets a zeroed cloud + view/time and SENTINEL muon/vertex
    so no truth/corrupt value can leak into step 1."""
    if pass_reco:
        cloud, view, time = pad_reco_cloud_tokens(
            B["cloud"]["part_reco_E"], B["cloud"]["part_reco_pos"], B["cloud"]["part_reco_z"],
            B["view"], B["time"], num_part)
    else:
        cloud = np.zeros((num_part, 3), np.float32)
        view = np.zeros(num_part, np.float32); time = np.zeros(num_part, np.float32)
    muon_vals = [B["muon"][b][0] for b in RECO_MUON_BRANCHES if b != "mu_reco_minos_ok"]
    muon_vals.append(float(B["minos"][0]))
    muon = reco_muon_row(pass_reco, muon_vals)
    vtx = reco_vertex_row(pass_reco, [B["vtx"][b][0] for b in RECO_VERTEX_BRANCHES])
    return cloud, view, time, muon, vtx


def _read_signal_inventory(f, num_part):
    """mc_signal_reco: reco side + appended native truth-only misses + truth cloud. Enforces the
    retained-FPS domain, preserves native misses (pass_reco=False, empty reco, valid truth), and
    sentinel-guards !pass_reco reco scalars/muon/vertex against step-1 truth leakage."""
    import ROOT
    t = f.Get("mc_signal_reco")
    if not t:
        raise SystemExit("[G2-FAIL] missing tree 'mc_signal_reco'")
    need = (list(RECO_CLOUD_BRANCHES) + [RECO_VIEW_BRANCH, RECO_TIME_BRANCH]
            + list(TRUTH_CLOUD_BRANCHES) + list(RECO_MUON_BRANCHES) + list(RECO_VERTEX_BRANCHES)
            + list(SIG_SCALAR_BRANCHES) + list(TRUTH_SCALAR_BRANCHES)
            + ["sim_pass", "w_truth", "w_reco"])
    _require_branches(t, "mc_signal_reco", need)
    B = _bind_reco_block(t)
    gen = {b: (ROOT.std.vector("int")() if b == "part_gen_pdg" else ROOT.std.vector("double")())
           for b in TRUTH_CLOUD_BRANCHES}
    for b, v in gen.items():
        t.SetBranchAddress(b, v)
    ssc = {b: array("d", [0.0]) for b in SIG_SCALAR_BRANCHES}
    tsc = {b: array("d", [0.0]) for b in TRUTH_SCALAR_BRANCHES}
    sp = array("B", [0]); wt = array("d", [0.0]); wr = array("d", [0.0])
    for b, a in {**ssc, **tsc}.items():
        t.SetBranchAddress(b, a)
    t.SetBranchAddress("sim_pass", sp)
    t.SetBranchAddress("w_truth", wt); t.SetBranchAddress("w_reco", wr)

    n = int(t.GetEntries())
    out = {"part_reco": np.zeros((n, num_part, 3), np.float32),
           "reco_scalars": np.zeros((n, NUM_SCALAR), np.float32),
           "reco_muon": np.zeros((n, NUM_MUON), np.float32),
           "reco_vertex": np.zeros((n, NUM_VTX), np.float32),
           "reco_view": np.zeros((n, num_part), np.float32),
           "reco_time": np.zeros((n, num_part), np.float32),
           "part_gen": np.zeros((n, num_part, NUM_TRUTH_FEAT), np.float32),
           "truth_scalars": np.zeros((n, NUM_SCALAR), np.float32),
           "pass_reco": np.zeros(n, bool), "pass_truth": np.zeros(n, bool),
           "w_truth": np.zeros(n, np.float32), "w_reco": np.zeros(n, np.float32)}
    k = 0
    for i in range(n):
        t.GetEntry(i)
        keep, pr, ptru = select_signal_row(ssc["sim"][0], ssc["sim_pz"][0], sp[0],
                                           tsc["MC"][0], tsc["MC_pz"][0])
        if not keep:
            continue
        cloud, view, time, muon, vtx = _reco_row(B, pr, num_part)
        out["part_reco"][k] = cloud; out["reco_view"][k] = view; out["reco_time"][k] = time
        out["reco_muon"][k] = muon; out["reco_vertex"][k] = vtx
        out["reco_scalars"][k] = reco_scalar_row(pr, [ssc[b][0] for b in SIG_SCALAR_BRANCHES])
        out["part_gen"][k] = pad_truth_cloud_tokens(
            gen["part_gen_E"], gen["part_gen_px"], gen["part_gen_py"], gen["part_gen_pz"],
            gen["part_gen_pdg"], num_part)                     # truth cloud always present
        out["truth_scalars"][k] = tuple(float(tsc[b][0]) for b in TRUTH_SCALAR_BRANCHES)
        out["pass_reco"][k] = pr; out["pass_truth"][k] = ptru
        out["w_truth"][k] = float(wt[0]); out["w_reco"][k] = float(wr[0])   # RAW (see finalize)
        k += 1
        if i and i % 500000 == 0:
            print(f"  [G2] signal {i}/{n} kept {k}", flush=True)
    for key in out:
        out[key] = out[key][:k].copy()
    print(f"[G2] signal kept {k}/{n} (pass_reco={int(out['pass_reco'].sum())} "
          f"pass_truth={int(out['pass_truth'].sum())})", flush=True)
    return out


def _read_data_inventory(f, num_part):
    """data: reco cloud/muon/vertex/view/time + measured scalars + real ev_* identity. All data
    rows are reco-selected (measured_pass!=0); domain-gated on (measured, measured_pz)."""
    t = f.Get("data")
    if not t:
        raise SystemExit("[G2-FAIL] missing tree 'data'")
    _require_branches(t, "data", list(RECO_CLOUD_BRANCHES) + [RECO_VIEW_BRANCH, RECO_TIME_BRANCH]
                      + list(RECO_MUON_BRANCHES) + list(RECO_VERTEX_BRANCHES)
                      + list(DATA_SCALAR_BRANCHES) + ["measured_pass"])
    B = _bind_reco_block(t)
    dsc = {b: array("d", [0.0]) for b in DATA_SCALAR_BRANCHES}
    dp = array("B", [0])
    for b, a in dsc.items():
        t.SetBranchAddress(b, a)
    t.SetBranchAddress("measured_pass", dp)
    n = int(t.GetEntries())
    out = {"measured_pc": np.zeros((n, num_part, 3), np.float32),
           "measured_scalars": np.zeros((n, NUM_SCALAR), np.float32),
           "data_muon": np.zeros((n, NUM_MUON), np.float32),
           "data_vertex": np.zeros((n, NUM_VTX), np.float32),
           "data_view": np.zeros((n, num_part), np.float32),
           "data_time": np.zeros((n, num_part), np.float32)}
    k = 0
    for i in range(n):
        t.GetEntry(i)
        if int(dp[0]) == 0 or not in_fps_domain(dsc["measured"][0], dsc["measured_pz"][0]):
            continue
        cloud, view, time, muon, vtx = _reco_row(B, True, num_part)
        out["measured_pc"][k] = cloud; out["data_view"][k] = view; out["data_time"][k] = time
        out["data_muon"][k] = muon; out["data_vertex"][k] = vtx
        out["measured_scalars"][k] = tuple(float(dsc[b][0]) for b in DATA_SCALAR_BRANCHES)
        k += 1
    for key in out:
        out[key] = out[key][:k].copy()
    print(f"[G2] data kept {k}/{n}", flush=True)
    return out


def _read_background_inventory(f, num_part):
    """mc_background: literal aligned Option-A injection inventory — reco cloud/muon/vertex/view/time
    + background scalars + RAW w_bkg (+ nuPDG/current/inttype AUDIT). Domain-gated on
    (sim_background, sim_background_pz); the upstream-corrupt out-of-domain row is EXCLUDED here."""
    t = f.Get("mc_background")
    if not t:
        raise SystemExit("[G2-FAIL] missing tree 'mc_background'")
    _require_branches(t, "mc_background", list(RECO_CLOUD_BRANCHES)
                      + [RECO_VIEW_BRANCH, RECO_TIME_BRANCH] + list(RECO_MUON_BRANCHES)
                      + list(RECO_VERTEX_BRANCHES) + list(BKG_SCALAR_BRANCHES)
                      + ["sim_background_pass", "w_bkg"])
    B = _bind_reco_block(t)
    bsc = {b: array("d", [0.0]) for b in BKG_SCALAR_BRANCHES}
    bp = array("B", [0]); wb = array("d", [0.0])
    for b, a in bsc.items():
        t.SetBranchAddress(b, a)
    t.SetBranchAddress("sim_background_pass", bp); t.SetBranchAddress("w_bkg", wb)
    have_audit = [b for b in BKG_AUDIT_BRANCHES if t.GetBranch(b)]
    aud = {b: array("i", [0]) for b in have_audit}
    for b, a in aud.items():
        t.SetBranchAddress(b, a)
    n = int(t.GetEntries())
    out = {"bkg_part_reco": np.zeros((n, num_part, 3), np.float32),
           "bkg_reco_scalars": np.zeros((n, NUM_SCALAR), np.float32),
           "bkg_muon": np.zeros((n, NUM_MUON), np.float32),
           "bkg_vertex": np.zeros((n, NUM_VTX), np.float32),
           "bkg_view": np.zeros((n, num_part), np.float32),
           "bkg_time": np.zeros((n, num_part), np.float32),
           "w_bkg": np.zeros(n, np.float32)}
    for b in have_audit:
        out[b] = np.zeros(n, np.int64)
    k = 0
    for i in range(n):
        t.GetEntry(i)
        if int(bp[0]) == 0 or not in_fps_domain(bsc["sim_background"][0], bsc["sim_background_pz"][0]):
            continue
        cloud, view, time, muon, vtx = _reco_row(B, True, num_part)
        out["bkg_part_reco"][k] = cloud; out["bkg_view"][k] = view; out["bkg_time"][k] = time
        out["bkg_muon"][k] = muon; out["bkg_vertex"][k] = vtx
        out["bkg_reco_scalars"][k] = tuple(float(bsc[b][0]) for b in BKG_SCALAR_BRANCHES)
        out["w_bkg"][k] = float(wb[0])                          # RAW MC background weight
        for b in have_audit:
            out[b][k] = int(aud[b][0])
        k += 1
    for key in out:
        out[key] = out[key][:k].copy()
    print(f"[G2] background kept {k}/{n}", flush=True)
    return out


def _run_g2_dump(f, args):
    """RUNTIME G2 full-event read: aligned signal/data/background inventories over the retained
    extended-FPS domain -> the contract NPZ (atomic, no partial, no purity fallback, no legacy).
    Needs PyROOT on a COMPUTE node (root_6_28). NOT executed on the login node."""
    import unfold_2d_omnifold_unbinned as u2d
    import fullevent_fps_dataloader as fed

    P = args.num_part
    edges_pt = np.asarray(fed.CANONICAL_PT_EDGES, float)
    edges_pz = np.asarray(fed.CANONICAL_PPARALLEL_EDGES, float)
    fed.assert_extended_fps_edges(edges_pt, edges_pz)          # belt-and-braces: canonical FPS grid
    data_pot, mc_pot, pot_scale = u2d.get_pot_scales(f)

    sig = _read_signal_inventory(f, P)
    data = _read_data_inventory(f, P)
    bkg = _read_background_inventory(f, P)
    f.Close()

    arrays = finalize_g2_arrays(sig, data, bkg, data_pot=data_pot, mc_pot=mc_pot,
                                pot_scale=pot_scale, edges_pt=edges_pt, edges_pz=edges_pz,
                                num_part=P)
    fdc.write_fullevent_npz_atomic(args.out, arrays, bkg_mode="negweight-refined")
    print(f"[G2] wrote {args.out}: signal {arrays['part_gen'].shape[0]} "
          f"data {arrays['measured_pc'].shape[0]} bkg {arrays['w_bkg'].shape[0]} num_part={P}")


def _pad_cloud(feat_vecs, num_part, sort_by_first_desc=True):
    """feat_vecs: list of equal-length python lists (one per feature) for ONE event.
    Returns (num_part, n_feat) zero-padded, truncated to the top num_part by feature[0]."""
    n_feat = len(feat_vecs)
    n = len(feat_vecs[0])
    out = np.zeros((num_part, n_feat), dtype=np.float32)
    if n == 0:
        return out
    arr = np.array(feat_vecs, dtype=np.float32).T  # (n, n_feat)
    if sort_by_first_desc and n > 1:
        arr = arr[np.argsort(-arr[:, 0])]
    k = min(n, num_part)
    out[:k] = arr[:k]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--omnifile", required=True)
    ap.add_argument("--mcfile", default=f"{_REPO}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root")
    ap.add_argument("--flux-hist", default="pTmu_reweightedflux_integrated")
    ap.add_argument("--num-part", type=int, default=12)
    ap.add_argument("--full-phase-space", action="store_true",
                    help="lift the theta_mu truth gate (mirror the nd driver / nn_dump_inputs.py)")
    ap.add_argument("--pt-edges", default=None,
                    help="comma-separated pT edge override (FPS extended grid)")
    ap.add_argument("--pz-edges", default=None,
                    help="comma-separated p|| edge override (FPS extended grid)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--legacy-recoil-crosscheck", action="store_true",
                    help="OPT-IN: dump the OLD recoil-only cross-check NPZ (purity placeholder, no "
                         "background/muon/vertex/view/time, NOT publication). Default path REQUIRES "
                         "the G2 full-event schema and fails closed on old inputs.")
    args = ap.parse_args()

    import ROOT  # deferred: PyROOT unavailable on the login node
    import unfold_2d_omnifold_unbinned as u2d

    if args.full_phase_space:
        import math
        u2d.MAX_MUON_THETA_RAD = math.pi
        print("[INFO] FULL PHASE SPACE: theta_mu truth gate lifted")

    P = args.num_part
    pt_e = ([float(x) for x in args.pt_edges.split(",")] if args.pt_edges
            else u2d.PT_EDGES)
    pz_e = ([float(x) for x in args.pz_edges.split(",")] if args.pz_edges
            else u2d.PZ_EDGES)
    pt_lo, pt_hi, pz_lo, pz_hi = pt_e[0], pt_e[-1], pz_e[0], pz_e[-1]

    f = ROOT.TFile.Open(args.omnifile)
    if not f or f.IsZombie():
        raise SystemExit(f"[FAIL] cannot open {args.omnifile}")

    # ---- G2 full-event schema gate (publication default) --------------------------------------
    if not args.legacy_recoil_crosscheck:
        fdc.assert_g2_schema(_read_g2_markers(f))   # fail closed on old / recoil-only inputs
        _run_g2_dump(f, args)                        # reads signal/data/background -> contract NPZ
        return
    print("[LEGACY] recoil-only CROSS-CHECK dump — NOT publication (purity placeholder; no "
          "background / muon / vertex / view / time / G2 schema). Quarantined artifact.")

    t = f.Get("mc_signal_reco"); d = f.Get("data")
    if not t.GetBranch("part_gen_E"):
        raise SystemExit("[FAIL] no part_gen_E branch -- re-run the event loop with "
                         "MNV101_DUMP_POINTCLOUD=1")
    data_pot, mc_pot, pot_scale = u2d.get_pot_scales(f)

    # ---- signal (MC): gen + reco clouds, pass flags, weights ----
    import math
    # scalar branches: pt/pz/eavail/q3 (truth + reco) so the PET push weights can be
    # binned into the SAME 4D axes as the GBDT result (PET-vs-GBDT comparison).
    sc = {b: array("d", [0.0]) for b in
          ("MC", "MC_pz", "MC_eavail", "MC_q3", "sim", "sim_pz", "sim_eavail", "sim_q3",
           "w_truth", "w_reco")}
    sp = array("B", [0])
    for b, a in sc.items():
        t.SetBranchAddress(b, a)
    t.SetBranchAddress("sim_pass", sp)
    genv = {b: ROOT.std.vector("double")() if b != "part_gen_pdg" else ROOT.std.vector("int")()
            for b in GEN_FEATS}
    recv = {b: ROOT.std.vector("double")() for b in RECO_FEATS}
    for b, v in {**genv, **recv}.items():
        t.SetBranchAddress(b, v)

    # Preallocate to the upper-bound entry count and fill by index (then truncate).
    # A python list of 32.8M small (P,nfeat) arrays + the np.asarray copy at the end
    # OOM-killed the 48G job (MaxRSS 50G); contiguous arrays cost ~15G total here.
    n = t.GetEntries()
    ng, nr = len(GEN_FEATS), len(RECO_FEATS)
    gen_cl = np.zeros((n, P, ng), np.float32)
    reco_cl = np.zeros((n, P, nr), np.float32)
    pr = np.zeros(n, bool); ptru = np.zeros(n, bool)
    wt = np.zeros(n, np.float64); wr = np.zeros(n, np.float64)
    tru_sc = np.zeros((n, 4), np.float32)   # per-event (pt,pz,eavail,q3) truth scalars
    rec_sc = np.zeros((n, 4), np.float32)   # per-event reco scalars
    k = 0
    for i in range(n):
        t.GetEntry(i)
        a_pt, a_pz = float(sc["MC"][0]), float(sc["MC_pz"][0])
        b_pt, b_pz = float(sc["sim"][0]), float(sc["sim_pz"][0])
        passed = sp[0] != 0
        tru_ok = u2d.in_truth_phase_space(a_pt, a_pz, pt_lo, pt_hi, pz_lo, pz_hi)
        rec_ok = (math.isfinite(b_pt) and math.isfinite(b_pz)
                  and pt_lo <= b_pt <= pt_hi and pz_lo <= b_pz <= pz_hi)
        if not (tru_ok or (passed and rec_ok)):
            continue
        gen_cl[k] = _pad_cloud([list(genv[b]) for b in GEN_FEATS], P)
        reco_cl[k] = _pad_cloud([list(recv[b]) for b in RECO_FEATS], P)
        pr[k] = passed and rec_ok; ptru[k] = tru_ok
        wt[k] = float(sc["w_truth"][0]) * pot_scale
        wr[k] = float(sc["w_reco"][0]) * pot_scale
        tru_sc[k] = (a_pt, a_pz, float(sc["MC_eavail"][0]), float(sc["MC_q3"][0]))
        rec_sc[k] = (b_pt if (passed and rec_ok) else -9999.0,
                     b_pz if (passed and rec_ok) else -9999.0,
                     float(sc["sim_eavail"][0]) if (passed and rec_ok) else -9999.0,
                     float(sc["sim_q3"][0]) if (passed and rec_ok) else -9999.0)
        k += 1
        if i % 200000 == 0:
            print(f"  signal {i}/{n}", flush=True)
    gen_cl = gen_cl[:k]; reco_cl = reco_cl[:k]
    pr = pr[:k]; ptru = ptru[:k]; wt = wt[:k]; wr = wr[:k]
    tru_sc = tru_sc[:k]; rec_sc = rec_sc[:k]
    print(f"  signal kept {k}/{n}", flush=True)

    # ---- data: reco cloud only ----
    dm = {b: array("d", [0.0]) for b in ("measured", "measured_pz")}
    dp = array("B", [0])
    for b, a in dm.items():
        d.SetBranchAddress(b, a)
    d.SetBranchAddress("measured_pass", dp)
    drecv = {b: ROOT.std.vector("double")() for b in RECO_FEATS}
    for b, v in drecv.items():
        d.SetBranchAddress(b, v)
    nd = d.GetEntries()
    meas_buf = np.zeros((nd, P, len(RECO_FEATS)), np.float32)
    km = 0
    for i in range(nd):
        d.GetEntry(i)
        if dp[0] == 0:
            continue
        pt, pz = float(dm["measured"][0]), float(dm["measured_pz"][0])
        if not (pt_lo <= pt <= pt_hi and pz_lo <= pz <= pz_hi):
            continue
        meas_buf[km] = _pad_cloud([list(drecv[b]) for b in RECO_FEATS], P)
        km += 1
    meas_cl = meas_buf[:km]
    f.Close()

    part_gen = np.asarray(gen_cl, np.float32)
    part_reco = np.asarray(reco_cl, np.float32)
    measured_pc = np.asarray(meas_cl, np.float32)
    print(f"[OK] signal clouds: gen {part_gen.shape} reco {part_reco.shape}; "
          f"data {measured_pc.shape}; num_part={P}")
    import unfold_nd_omnifold_unbinned as und
    ea_e = und.EXTRA_AXES["eavail"]["edges"]; q3_e = und.EXTRA_AXES["q3"]["edges"]
    np.savez_compressed(
        args.out, num_part=P,
        petSchemaVersion="recoil-only-crosscheck",  # explicitly NOT G2; fails the G2 schema gate
        hasFullEventSchema=0, fullPhaseSpace=int(bool(args.full_phase_space)),
        part_gen=part_gen, part_reco=part_reco, measured_pc=measured_pc,
        pass_reco=np.asarray(pr, bool), pass_truth=np.asarray(ptru, bool),
        w_truth=np.asarray(wt), w_reco=np.asarray(wr),
        measured_weights=np.ones(len(meas_cl)),
        # per-event (pt,pz,eavail,q3) scalars for binning the PET result vs GBDT
        truth_scalars=np.asarray(tru_sc, np.float32), reco_scalars=np.asarray(rec_sc, np.float32),
        edges_0=np.asarray(pt_e, float), edges_1=np.asarray(pz_e, float),
        edges_2=np.asarray(ea_e, float), edges_3=np.asarray(q3_e, float),
        gen_feats=np.array(GEN_FEATS, dtype=object),
        reco_feats=np.array(RECO_FEATS, dtype=object),
        data_pot=data_pot)
    print(f"[wrote] {args.out}")


if __name__ == "__main__":
    main()

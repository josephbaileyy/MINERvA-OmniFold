#!/usr/bin/env python3
"""MP-5(a) step 1: the analysis-MC (MnvTune v1) truth content per fine cell with the muon angle measured from the
fixed MAT beam axis (the analysis convention) and from the true neutrino direction (the generators' convention).

Population. The analysis truth denominator is the 5D omnifile's ``mc_truth_denom`` (32.8M rows, no event identity).
The G2 full-phase-space production (``g2_fullevent/final/runEventLoopOmniFold_G2_FPS_<pl>.root``) wrote the same
rows with identity (mc_run, mc_subrun, mc_nthEvtInFile) and the MAT-frame muon, plus the events outside the muon
phase space. Each G2 row is joined by identity (``event_identity.pack_identity``) to its MasterAnaDev ``Truth`` entry,
which carries ``mc_incomingPartVec`` (the true neutrino direction).

Per event (MeV, MAT TruthFunctions.h / CVUniverse.h semantics):
  beam axis  theta_b = (RotateX(-0.05887) l).Theta()           [TruthFunctions.h:21-27, PlotUtilsPhysicalConstants.h:44]
  nu axis    theta_n = angle(l, k), k = mc_incomingPartVec[0:3]
  pT = |l|/1000 sin(theta), p_par = |l|/1000 cos(theta)         [CVUniverse.h:71-79]
  W  = sqrt(M^2 + 2 M (E_nu - E_l) - 4 E_nu E_l sin^2(theta/2)) / 1000, M by mc_targetNucleon  [CVUniverse.h:41-44,396-410]
  E_avail, q3: the stored truth (axis-independent).
Contents use the truth-denominator gate of unfold_nd_omnifold_unbinned.collect_truth_denom_nd (finite values,
0 <= w < 1e4, u2d.in_truth_phase_space on (pT, p_par)) with w = w_truth x pot_scale, binned with np.histogramdd as
nn_dump_inputs.py does for denom_nd.

CONTROLS (exit 3, nothing else is read, if any fails): T1 alignment, T2 join, T3 MnvTune truth, T4 recompute
(mp5_declaration.json). Usage: python3 mp5_tune.py OUTDIR POOLDIR NPROC S5C_CONTRACT
"""
import hashlib
import json
import math
import multiprocessing as mp
import os
import resource
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np  # noqa: E402

NS = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
G2_DIR = f"{NS}/nd-unfolding/g2_fullevent/final"
OMNI5D = f"{NS}/nd-unfolding/runEventLoopOmniFold_5D_MEFHC.root"
OMNI5D_SHA = "b6d2651cfdbc52790cc7ed6032f2062a3e0ea50c12d63725beba29098dd5175a"   # M4-W omni_input.sha256
OFIN = f"{NS}/nd-unfolding/of_inputs_5d.npz"
OFIN_SHA = "07fccc1abc7204bc29349b4ba96850986fe91e909e83fc54e8d1a6b3922a649f"     # mnvtune_v1_xsec5d meta npz_sha256
MNV = "/pscratch/sd/j/josephrb/s5p-20260926/gen5d/mnvtune_v1_xsec5d.npz"
MNV_SHA = "bf7bd27873427d4b1ff9864403b895529931f113440acec3daa28479f958466c"      # release manifest 2026-10-06
MANIFESTS = f"{NS}/2d-unfolding/playlist_manifests"
PLAYLISTS = ["1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P"]
A_BEAM = -0.05887                       # MinervaUnits::numi_beam_angle_rad
M_N, M_P = 939.56536, 938.272013        # PlotUtilsPhysicalConstants.h:73-75 (MeV)
M_NUCLEON = (1.5 * M_N + M_P) / 2.5     # CVUniverse.h:41
STORED = ["MC", "MC_pz", "MC_eavail", "MC_q3", "MC_W", "w_truth"]
G2COLS = STORED + ["mu_true_px", "mu_true_py", "mu_true_pz", "mu_true_E", "mc_run", "mc_subrun", "mc_nthEvtInFile"]
MADDEF = {"kx": "mc_incomingPartVec[0]", "ky": "mc_incomingPartVec[1]", "kz": "mc_incomingPartVec[2]",
          "kE": "mc_incomingPartVec[3]", "lx": "mc_primFSLepton[0]", "ly": "mc_primFSLepton[1]",
          "lz": "mc_primFSLepton[2]", "lE": "mc_primFSLepton[3]", "vx": "mc_vtx[0]", "vy": "mc_vtx[1]", "vz": "mc_vtx[2]"}
MADCOLS = ["mc_run", "mc_subrun", "mc_nthEvtInFile", "kx", "ky", "kz", "kE", "lx", "ly", "lz", "lE",
           "mc_incomingE", "mc_Q2", "mc_targetNucleon"]
# loose superset of the truth fiducial (ZRange 5980-8422 mm, hexagon apothem 850 mm, circumradius 981.5 mm);
# the join's coverage check (T2) proves nothing the analysis kept was cut here
MADFILTER = "mc_current==1 && mc_incoming==14 && vz > 5900. && vz < 8500. && vx*vx + vy*vy < 990.*990."
ENU_BINS = [0.0, 3.0, 5.0, 8.0, 15.0, 30.0, np.inf]


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


_ROOT = None


def _root():
    global _ROOT
    if _ROOT is None:
        import ROOT
        ROOT.gErrorIgnoreLevel = ROOT.kError
        _ROOT = ROOT
    return _ROOT


def read_mad(fn):
    """One MasterAnaDev file's Truth entries (nu_mu CC, loose fiducial), in tree order."""
    ROOT = _root()
    f = ROOT.TFile.Open(fn)
    n_all = int(f.Get("Truth").GetEntries())
    f.Close()
    df = ROOT.RDataFrame("Truth", fn)
    for k, v in MADDEF.items():
        df = df.Define(k, v)
    d = df.Filter(MADFILTER).AsNumpy(MADCOLS)
    return fn, n_all, {k: np.asarray(v) for k, v in d.items()}


def rotx(x, y, z, a):
    """TVector3::RotateX(a)."""
    s, c = math.sin(a), math.cos(a)
    return x, c * y - s * z, s * y + c * z


def theta_of(x, y, z):
    """TVector3::Theta() = atan2(Perp, z), Perp = sqrt(x^2 + y^2)."""
    return np.arctan2(np.sqrt(x * x + y * y), z)


def w_cvu(M, enu, el, th):
    """CVUniverse::GetTrueExperimentersW (MeV); NaN where W^2 < 0."""
    q2 = 4.0 * enu * el * np.sin(th / 2.0) ** 2
    with np.errstate(invalid="ignore"):
        return np.sqrt(M * M + 2.0 * (enu - el) * M - q2)


def in_ps(u2d, pt, pz, lo_t, hi_t, lo_z, hi_z):
    """u2d.in_truth_phase_space, vectorized; the theta cut is re-decided with math.atan2 within 1e-12 of 20 deg."""
    fin = np.isfinite(pt) & np.isfinite(pz)
    with np.errstate(invalid="ignore"):
        box = fin & (pt >= lo_t) & (pt <= hi_t) & (pz >= lo_z) & (pz <= hi_z)
        th = np.arctan2(pt, pz)
    ok = box & (th < u2d.MAX_MUON_THETA_RAD)
    near = np.where(box & (np.abs(th - u2d.MAX_MUON_THETA_RAD) < 1e-12))[0]
    for i in near:
        ok[i] = u2d.in_truth_phase_space(float(pt[i]), float(pz[i]), lo_t, hi_t, lo_z, hi_z)
    return ok, int(near.size)


def gate(u2d, cols, w, edges):
    """collect_truth_denom_nd's row gate: finite truth values and weight, 0 <= w < 1e4, in the truth phase space."""
    fin = np.isfinite(w) & (w >= 0) & (w < 1e4)
    for c in cols:
        fin &= np.isfinite(c)
    ps, near = in_ps(u2d, cols[0], cols[1], edges[0][0], edges[0][-1], edges[1][0], edges[1][-1])
    return fin & ps, near


def hist5(cols, w, m, edges):
    return np.histogramdd(np.column_stack([c[m] for c in cols]), bins=edges, weights=w[m])[0]


def maxabs(a, b, m=None):
    d = np.abs(np.asarray(a, float) - np.asarray(b, float))
    if m is not None:
        d = d[m]
    d = d[np.isfinite(d)]
    return float(d.max()) if d.size else 0.0


def q(x):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    if not x.size:
        return {"n": 0}
    p = np.quantile(x, [0.025, 0.16, 0.5, 0.84, 0.975])
    return {"n": int(x.size), "median": float(p[2]), "r68": [float(p[1]), float(p[3])], "r95": [float(p[0]), float(p[4])],
            "max": float(x.max())}


def main():
    out, pooldir, nproc = Path(sys.argv[1]), Path(sys.argv[2]), int(sys.argv[3])
    out.mkdir(parents=True, exist_ok=True)
    pooldir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    ctx = mp.get_context("spawn")
    pool = ctx.Pool(nproc)
    import gen5d_flux_reweight as gfr
    import event_identity as eid
    import s5p_stage1_inspect as s1
    import xsec_nd
    g5 = gfr.load_g5(gfr.DEFAULTS["gen5d_tree"])
    u2d = g5.u3d.u2d
    ROOT = _root()
    res = {"schema": "mp5-tune/1", "argv": sys.argv, "environment": gfr.environment(), "code": {}, "inputs": {},
           "controls": {}, "playlists": {}}
    for m in (sys.modules[__name__], gfr, eid, s1, xsec_nd, g5, u2d):
        p = Path(m.__file__).resolve()
        res["code"][m.__name__] = {"file": str(p), "sha256": sha256(p)}
        print("module", m.__name__, p, flush=True)

    # ---- input digests (G2 ROOTs hashed in parallel, compared with their production receipts)
    g2f = {p: f"{G2_DIR}/runEventLoopOmniFold_G2_FPS_{p}.root" for p in PLAYLISTS}
    big = [OMNI5D, OFIN, MNV] + [g2f[p] for p in PLAYLISTS]
    digests = dict(zip(big, pool.map(sha256, big)))
    want = {OMNI5D: OMNI5D_SHA, OFIN: OFIN_SHA, MNV: MNV_SHA}
    for p in PLAYLISTS:
        rc = json.loads(Path(f"{G2_DIR}/G2_receipt_{p}.json").read_text())
        want[g2f[p]] = rc.get("final_root", {}).get("sha256")
        man = f"{MANIFESTS}/{p}_MC.txt"
        res["inputs"][man] = {"sha256": sha256(man), "receipt_manifest_mc_sha256": rc.get("manifest_mc", {}).get("sha256"),
                              "receipt_schema": rc.get("receipt_schema"), "receipt_status": rc.get("status")}
    for f in big:
        res["inputs"][f] = {"sha256": digests[f], "expected": want[f], "match": digests[f] == want[f]}
    # binding: the 5D omnifile, of_inputs_5d and the MnvTune product; the G2 digests are reported against their
    # production receipts, and T1 (bitwise against the hashed 5D omnifile) is the binding evidence for their rows
    res["controls"]["T0_input_digests"] = {"pass": all(res["inputs"][f]["match"] for f in (OMNI5D, OFIN, MNV)),
                                           "g2_match_receipts": {p: res["inputs"][g2f[p]]["match"] for p in PLAYLISTS}}
    print("T0", res["controls"]["T0_input_digests"], flush=True)

    z = np.load(OFIN, allow_pickle=True)
    edges = [np.asarray(z[f"edges_{i}"], float) for i in range(int(z["nedges"]))]
    if list(z["axes"]) != ["eavail", "q3", "W"]:
        raise SystemExit(f"of_inputs_5d axes {list(z['axes'])}")
    fomni = ROOT.TFile.Open(OMNI5D)
    data_pot, mc_pot, pot_scale = u2d.get_pot_scales(fomni)
    fomni.Close()
    res["pot"] = {"data": data_pot, "mc": mc_pot, "scale": pot_scale}
    if not all(np.array_equal(e, np.asarray(s1.FINE[ax], float)) for e, ax in zip(edges, s1.AXES)):
        raise SystemExit("of_inputs_5d edges differ from s5p_stage1_inspect.FINE")

    acc = {k: [] for k in ("stored_ps", "ptb", "pzb", "Wb", "ptn", "pzn", "Wn", "eav", "q3", "w", "enu", "alpha",
                           "nx", "ny", "nz")}
    t2 = {"n_g2_rows": 0, "n_matched": 0, "n_unmatched": 0, "n_mad_dup_keys": 0, "n_mad_dup_content_differs": 0,
          "mu_true_maxabs_MeV": 0.0, "mu_true_E_maxabs_MeV": 0.0, "Enu_branch_vs_vec_maxabs_MeV": 0.0,
          "nu_vec_mass_maxabs_MeV": 0.0}
    t4 = {"pt_maxabs_GeV": 0.0, "pz_maxabs_GeV": 0.0, "W_maxabs_GeV": 0.0, "q3_maxabs_GeV": 0.0,
          "W_nan_pattern_differs": 0}
    for p in PLAYLISTS:
        tp = time.time()
        g = ROOT.RDataFrame("mc_truth_denom", g2f[p]).AsNumpy(G2COLS)
        g = {k: np.asarray(v) for k, v in g.items()}
        files = [ln.strip() for ln in Path(f"{MANIFESTS}/{p}_MC.txt").read_text().splitlines() if ln.strip()]
        parts = pool.map(read_mad, files)
        n_truth = sum(r[1] for r in parts)
        mad = {k: np.concatenate([r[2][k] for r in parts]) for k in MADCOLS}
        del parts
        gk = eid.pack_identity(g["mc_run"], g["mc_subrun"], g["mc_nthEvtInFile"])
        mk = eid.pack_identity(mad["mc_run"], mad["mc_subrun"], mad["mc_nthEvtInFile"])
        if np.unique(gk).size != gk.size:
            raise SystemExit(f"{p}: G2 identity not unique")
        order = np.argsort(mk, kind="stable")
        ms = mk[order]
        first = np.ones(ms.size, bool)
        first[1:] = ms[1:] != ms[:-1]
        dup_rows = order[~first]
        ndiff = 0
        if dup_rows.size:  # keep the first occurrence (manifest order, tree order), as the event loop's dedupe does
            keep_of = order[np.searchsorted(ms, mk[dup_rows], side="left")]
            for k in MADCOLS:
                a, b = mad[k][dup_rows], mad[k][keep_of]
                ndiff += int(np.sum(~((a == b) | (np.isnan(a) & np.isnan(b))) if a.dtype.kind == "f" else a != b))
        uk, ui = ms[first], order[first]
        pos = np.searchsorted(uk, gk)
        pos = np.clip(pos, 0, uk.size - 1)
        hit = uk[pos] == gk
        t2["n_g2_rows"] += int(gk.size)
        t2["n_matched"] += int(hit.sum())
        t2["n_unmatched"] += int((~hit).sum())
        t2["n_mad_dup_keys"] += int(dup_rows.size)
        t2["n_mad_dup_content_differs"] += ndiff
        if not hit.all():
            t2["failed_playlist"] = p
            break
        j = ui[pos]
        e = {k: mad[k][j] for k in MADCOLS}
        del mad
        lx, ly, lz, el = e["lx"], e["ly"], e["lz"], e["lE"]
        bx, by, bz = rotx(lx, ly, lz, A_BEAM)
        t2["mu_true_maxabs_MeV"] = max(t2["mu_true_maxabs_MeV"], maxabs(bx, g["mu_true_px"]), maxabs(by, g["mu_true_py"]),
                                       maxabs(bz, g["mu_true_pz"]))
        t2["mu_true_E_maxabs_MeV"] = max(t2["mu_true_E_maxabs_MeV"], maxabs(el, g["mu_true_E"]))
        enu = e["mc_incomingE"]
        t2["Enu_branch_vs_vec_maxabs_MeV"] = max(t2["Enu_branch_vs_vec_maxabs_MeV"], maxabs(enu, e["kE"]))
        P = np.sqrt(lx * lx + ly * ly + lz * lz)
        th_b = theta_of(bx, by, bz)
        kx, ky, kz = e["kx"], e["ky"], e["kz"]
        kmag = np.sqrt(kx * kx + ky * ky + kz * kz)
        t2["nu_vec_mass_maxabs_MeV"] = max(t2["nu_vec_mass_maxabs_MeV"], maxabs(kmag, e["kE"]))
        cx, cy, cz = ly * kz - lz * ky, lz * kx - lx * kz, lx * ky - ly * kx
        th_n = np.arctan2(np.sqrt(cx * cx + cy * cy + cz * cz), lx * kx + ly * ky + lz * kz)
        tn = e["mc_targetNucleon"]
        M = np.where(tn == 2112, M_N, np.where(tn == 2212, M_P, M_NUCLEON))
        ptb, pzb = P / 1000. * np.sin(th_b), P / 1000. * np.cos(th_b)
        ptn, pzn = P / 1000. * np.sin(th_n), P / 1000. * np.cos(th_n)
        Wb, Wn = w_cvu(M, enu, el, th_b) / 1000., w_cvu(M, enu, el, th_n) / 1000.
        with np.errstate(invalid="ignore"):
            q3r = np.sqrt(e["mc_Q2"] + (enu - el) ** 2) / 1000.
        t4["pt_maxabs_GeV"] = max(t4["pt_maxabs_GeV"], maxabs(ptb, g["MC"]))
        t4["pz_maxabs_GeV"] = max(t4["pz_maxabs_GeV"], maxabs(pzb, g["MC_pz"]))
        t4["W_maxabs_GeV"] = max(t4["W_maxabs_GeV"], maxabs(Wb, g["MC_W"]))
        t4["q3_maxabs_GeV"] = max(t4["q3_maxabs_GeV"], maxabs(q3r, g["MC_q3"]))
        t4["W_nan_pattern_differs"] += int(np.sum(np.isnan(Wb) != np.isnan(g["MC_W"])))
        nbx, nby, nbz = rotx(kx / kmag, ky / kmag, kz / kmag, A_BEAM)   # nu direction in the MAT beam frame
        ps_kin, _ = in_ps(u2d, g["MC"], g["MC_pz"], edges[0][0], edges[0][-1], edges[1][0], edges[1][-1])
        acc["stored_ps"].append(np.column_stack([g[c][ps_kin].astype(float) for c in STORED]))
        for k, v in (("ptb", ptb), ("pzb", pzb), ("Wb", Wb), ("ptn", ptn), ("pzn", pzn), ("Wn", Wn),
                     ("eav", g["MC_eavail"]), ("q3", g["MC_q3"]), ("w", g["w_truth"]), ("enu", enu / 1000.),
                     ("alpha", theta_of(nbx, nby, nbz)), ("nx", nbx), ("ny", nby), ("nz", nbz)):
            acc[k].append(np.asarray(v, float))
        res["playlists"][p] = {"n_g2_rows": int(gk.size), "n_g2_in_kinematic_ps": int(ps_kin.sum()), "n_mad_files": len(files),
                               "n_mad_truth_entries": int(n_truth), "n_mad_prefiltered": int(mk.size),
                               "n_mad_dup_keys": int(dup_rows.size), "wall_s": time.time() - tp}
        print(p, json.dumps(res["playlists"][p]), flush=True)
        del g, e
    pool.close()
    pool.join()
    t2["pass"] = (t2["n_unmatched"] == 0 and t2["n_matched"] == t2["n_g2_rows"] and t2["mu_true_maxabs_MeV"] <= 1e-6
                  and t2["mu_true_E_maxabs_MeV"] <= 1e-6)
    res["controls"]["T2_join"] = t2
    print("T2", json.dumps(t2), flush=True)
    if not t2["pass"]:
        return finish(res, out, t0, 3)

    # ---- T1: the PS-restricted G2 blocks are the 5D omnifile's rows, bitwise, in some playlist order
    o = ROOT.RDataFrame("mc_truth_denom", OMNI5D).AsNumpy(STORED)
    O = np.column_stack([np.asarray(o[c], float) for c in STORED])
    del o
    blocks = dict(zip(PLAYLISTS, acc["stored_ps"]))

    def same(a, b):
        return bool(np.all((a == b) | (np.isnan(a) & np.isnan(b))))
    off, order_found, left = 0, [], list(PLAYLISTS)
    while left:
        cand = [p for p in left if off + len(blocks[p]) <= len(O) and same(blocks[p][:64], O[off:off + 64])]
        cand = [p for p in cand if same(blocks[p], O[off:off + len(blocks[p])])]
        if len(cand) != 1:
            break
        order_found.append(cand[0])
        off += len(blocks[cand[0]])
        left.remove(cand[0])
    t1 = {"n_5d_rows": int(len(O)), "n_g2_ps_rows": int(sum(len(b) for b in blocks.values())), "order": order_found,
          "unplaced": left, "rows_matched_bitwise": int(off)}
    t1["pass"] = (not left) and off == len(O)
    res["controls"]["T1_alignment"] = t1
    print("T1", json.dumps(t1), flush=True)
    if not t1["pass"]:
        return finish(res, out, t0, 3)
    S = np.concatenate([blocks[p] for p in order_found])
    del O, blocks, acc["stored_ps"]

    # ---- T3: the beam-axis content of the stored analysis truth = denom_nd, and the MnvTune extraction
    cols_s = [S[:, i] for i in range(5)]
    ws = S[:, 5] * pot_scale
    gs, _ = gate(u2d, cols_s, S[:, 5], edges)
    Tb_stored = hist5(cols_s, ws, gs, edges)
    dn = np.asarray(z["denom_nd"], float)
    m = np.asarray(z["pass_truth"], bool)
    MCg = np.asarray(z["MCgen"])
    samp = np.column_stack([MCg[m, i] for i in range(5)]).astype(float)
    del MCg
    wt = np.asarray(z["w_truth"], float)[m]
    unf = np.histogramdd(samp, bins=edges, weights=wt)[0]
    unf2 = np.histogramdd(samp, bins=edges, weights=wt * wt)[0]
    del samp
    flux, dpot, nn = z["flux"], float(z["data_pot"]), float(z["n_nucleons"])

    def mnv_extract(denom):  # s5p_mc_truth_pred.py:47-56, restated (its module imports the OmniFold core)
        comp = np.zeros_like(unf)
        comp[denom > 0] = unf[denom > 0] / denom[denom > 0]
        xs, _ = xsec_nd.extract_cross_section_nd(unf, comp, flux, dpot, nn, edges)
        scale = np.where(unf > 0, xs / np.where(unf > 0, unf, 1), 0.0)
        return xs.ravel(order="C"), (unf2 * scale ** 2).ravel(order="C")
    mz = np.load(MNV, allow_pickle=True)
    fx, fv = np.asarray(mz["xsec_flat"], float), np.asarray(mz["sumw2_flat"], float)
    x0, v0 = mnv_extract(dn)
    x1, v1 = mnv_extract(Tb_stored)
    nz_ = dn > 0
    t3 = {"denom_bitwise": bool(np.array_equal(Tb_stored, dn)),
          "denom_max_rel": float(np.max(np.abs(Tb_stored[nz_] - dn[nz_]) / dn[nz_])),
          "denom_cells_zero_mismatch": int(np.sum((Tb_stored > 0) != nz_)),
          "restated_extraction_with_frozen_denom_bitwise": [bool(np.array_equal(x0, fx)), bool(np.array_equal(v0, fv))],
          "extraction_with_beam_axis_content_bitwise": [bool(np.array_equal(x1, fx)), bool(np.array_equal(v1, fv))],
          "extraction_max_rel": float(np.max(np.abs(x1[fx != 0] - fx[fx != 0]) / np.abs(fx[fx != 0])))}
    t3["pass"] = t3["restated_extraction_with_frozen_denom_bitwise"] == [True, True] and t3["denom_max_rel"] <= 1e-12 \
        and t3["denom_cells_zero_mismatch"] == 0 and t3["extraction_max_rel"] <= 1e-12
    res["controls"]["T3_mnvtune_truth"] = t3
    print("T3", json.dumps(t3), flush=True)
    del z, S
    if not t3["pass"]:
        return finish(res, out, t0, 3)

    # ---- per-event arrays over every G2 row (all playlists, discovered order irrelevant to the sums' meaning)
    a = {k: np.concatenate(v) for k, v in acc.items() if k != "stored_ps"}
    del acc
    w = a["w"] * pot_scale
    gb, near_b = gate(u2d, [a["ptb"], a["pzb"], a["eav"], a["q3"], a["Wb"]], a["w"], edges)
    gn, near_n = gate(u2d, [a["ptn"], a["pzn"], a["eav"], a["q3"], a["Wn"]], a["w"], edges)
    Tb = hist5([a["ptb"], a["pzb"], a["eav"], a["q3"], a["Wb"]], w, gb, edges)
    Tn = hist5([a["ptn"], a["pzn"], a["eav"], a["q3"], a["Wn"]], w, gn, edges)
    Tb2 = hist5([a["ptb"], a["pzb"], a["eav"], a["q3"], a["Wb"]], w * w, gb, edges)
    Tn2 = hist5([a["ptn"], a["pzn"], a["eav"], a["q3"], a["Wn"]], w * w, gn, edges)
    supported = json.loads(Path(sys.argv[4]).read_text())["measurement"]["partition_J"]["supported_cells"]
    cmap, ncell = s1.coarse_map(s1.J_EDGES, supported)

    def jcell(pt, pz, W, g_):
        fi = s1.fine_index(np.column_stack([pt, pz, a["eav"], a["q3"], W]))
        jc = np.where(g_ & (fi >= 0), cmap[np.maximum(fi, 0)], -1)
        return fi, jc
    fib, jb = jcell(a["ptb"], a["pzb"], a["Wb"], gb)
    fin_, jn = jcell(a["ptn"], a["pzn"], a["Wn"], gn)
    mv = jb != jn
    J = {"Tb": np.bincount(jb[jb >= 0], w[jb >= 0], ncell), "Tn": np.bincount(jn[jn >= 0], w[jn >= 0], ncell),
         "w2_out": np.bincount(jb[mv & (jb >= 0)], (w * w)[mv & (jb >= 0)], ncell),
         "w2_in": np.bincount(jn[mv & (jn >= 0)], (w * w)[mv & (jn >= 0)], ncell),
         "n_out": np.bincount(jb[mv & (jb >= 0)], None, ncell), "n_in": np.bincount(jn[mv & (jn >= 0)], None, ncell)}
    Jstored = np.bincount(cmap[cmap >= 0], Tb_stored.ravel()[cmap >= 0], ncell)
    # T4: the recomputed beam axis reproduces the stored analysis truth
    t4.update({"Tb_rec_vs_stored_J_max_rel": float(np.max(np.abs(J["Tb"] - Jstored) / Jstored)),
               "Tb_rec_vs_stored_fine_max_abs_rel_to_total": float(np.max(np.abs(Tb - Tb_stored)) / Tb_stored.sum())})
    t4["pass"] = (t4["pt_maxabs_GeV"] <= 1e-9 and t4["pz_maxabs_GeV"] <= 1e-9 and t4["W_maxabs_GeV"] <= 1e-9
                  and t4["W_nan_pattern_differs"] == 0 and t4["Tb_rec_vs_stored_J_max_rel"] <= 1e-6)
    res["controls"]["T4_recompute"] = t4
    print("T4", json.dumps(t4), flush=True)

    # descriptive migration census (beam -> nu axis)
    b_ps, _ = in_ps(u2d, a["ptb"], a["pzb"], 0.0, 4.5, 1.5, 60.0)
    n_ps, _ = in_ps(u2d, a["ptn"], a["pzn"], 0.0, 4.5, 1.5, 60.0)
    ptbin = lambda x: np.searchsorted(edges[0], x, side="right")  # noqa: E731
    wb = np.where(gb, w, 0.0)
    res["migration"] = {
        "n_rows": int(w.size), "n_gate_beam": int(gb.sum()), "n_gate_nu": int(gn.sum()),
        "near_20deg_rechecked": [near_b, near_n],
        "n_ps_decision_differs": int((b_ps != n_ps).sum()),
        "n_beam_only_ps": int((b_ps & ~n_ps).sum()), "n_nu_only_ps": int((n_ps & ~b_ps).sum()),
        "weighted_frac_J_cell_changes_of_beam_gate": float(w[gb & mv].sum() / w[gb].sum()),
        "weighted_frac_fine_cell_changes_of_beam_gate": float(w[gb & (fib != fin_)].sum() / w[gb].sum()),
        "weighted_frac_fine_pT_bin_changes_of_beam_gate": float(wb[ptbin(a["ptb"]) != ptbin(a["ptn"])].sum() / wb.sum()),
        "pT_beam_minus_nu_MeV_beam_gate": q(1000 * (a["ptb"] - a["ptn"])[gb]),
        "pz_beam_minus_nu_MeV_beam_gate": q(1000 * (a["pzb"] - a["pzn"])[gb]),
        "W_beam_minus_nu_MeV_beam_gate": q(1000 * (a["Wb"] - a["Wn"])[gb]),
        "alpha_nu_vs_MAT_axis_mrad_beam_gate": q(1000 * a["alpha"][gb])}

    # ---- the nu-direction pool for the GENIE check, by E_nu bin (declared)
    pw = np.isfinite(a["w"]) & (a["w"] >= 0) & (a["w"] < 1e4)
    eb = np.digitize(a["enu"], ENU_BINS) - 1
    pool_info = []
    for b in range(len(ENU_BINS) - 1):
        mb = pw & (eb == b)
        np.save(pooldir / f"pool_b{b}.npy", np.column_stack([a["nx"][mb], a["ny"][mb], a["nz"][mb], a["w"][mb]]))
        pool_info.append({"bin_GeV": [ENU_BINS[b], ENU_BINS[b + 1] if np.isfinite(ENU_BINS[b + 1]) else "inf"],
                          "n": int(mb.sum()), "sum_w": float(a["w"][mb].sum()),
                          "alpha_mrad": q(1000 * a["alpha"][mb]),
                          "alpha_mrad_beam_gate": q(1000 * a["alpha"][mb & gb])})
    res["direction_pool"] = {"dir": str(pooldir), "bins": pool_info,
                             "n_rows_without_valid_weight": int((~pw).sum()),
                             "n_rows_outside_bins": int(((eb < 0) | (eb >= len(ENU_BINS) - 1))[pw].sum())}
    for f in sorted(pooldir.glob("pool_b*.npy")):
        res["direction_pool"][f.name] = sha256(f)

    np.savez_compressed(out / "mp5_tune.npz", Tb_stored=Tb_stored.ravel(), Tb=Tb.ravel(), Tn=Tn.ravel(),
                        Tb2=Tb2.ravel(), Tn2=Tn2.ravel(), mnv_xsec_from_beam=x1, mnv_sumw2_from_beam=v1,
                        J_Tb_stored=Jstored, **{f"J_{k}": v for k, v in J.items()})
    ok = all(res["controls"][k]["pass"] for k in ("T0_input_digests", "T1_alignment", "T2_join", "T3_mnvtune_truth",
                                                  "T4_recompute"))
    return finish(res, out, t0, 0 if ok else 3)


def finish(res, out, t0, rc):
    ru = resource.getrusage(resource.RUSAGE_SELF)
    res["cpu_s_parent"], res["maxrss_kb_parent"], res["wall_s"], res["exit"] = ru.ru_utime + ru.ru_stime, ru.ru_maxrss, \
        time.time() - t0, rc
    (out / "mp5_tune.json").write_text(json.dumps(res, indent=1, default=str) + "\n")
    print("TUNE_CONTROLS", {k: v.get("pass") for k, v in res["controls"].items()}, "exit", rc, flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())

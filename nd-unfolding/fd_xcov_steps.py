#!/usr/bin/env python3
"""GENCMP X's cluster steps (FD-GENCMP-X-DECLARATION.md sections 2-4): v0, v1, boot and k, which read the declared
files and call fd_xcov's pure functions. Every pscratch or CFS file is opened O_NOATIME and checked against its pin
(fd_xcov.Inputs); every file this module writes goes under --run-dir.

MEASURES: arithmetic on the declared inputs. CANNOT AUTHORIZE: a reading, a paper edit or a claim.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import fd_gencmp as gc  # noqa: E402
import fd_xcov as X  # noqa: E402
import s1_assemble as sa  # noqa: E402

P = Path("/pscratch/sd/j/josephrb")
RE2 = P / "2d-closeout-re2-20261023"
CV_OMNI = Path("/global/cfs/cdirs/m3246/josephrb/two-d-followup-20261010/xr-input/runEventLoopOmniFold_MEFHC.root")
# RE-2's CV omnifile (re2_env.sh:9-10); part B's pscratch stage of it, the same digest, was removed (deletions.tsv:2)
UNI_OMNI = P / "MINERvA-OmniFold/2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root"
NPZ_5D = P / "MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz"
BKG_5D = P / "s5c-20260924/runs/p2/bkg_dump.npz"
Q_R = RE2 / "partc-r2/combination/s5_plus_playlist.npz"
CPL_R = RE2 / "partc-r2/playlist/playlist_term.npz"
S5_R = RE2 / "partc-r2/s5/production_cov.npz"
X01 = P / "2d-closeout-c04repair-20261012/build/minos_rescaled.npz"
CONSTRAINT = P / "MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt"
S1_NPZ = P / "s1-20261024/s1_assembly.npz"
DET_RECEIPT = P / "s5p-20260926/bank_detector/detector-dump.json"
REPO = _ND.parent
FD = X.FD
S1DIR = FD / "s1/readout/s1_assembly"                                     # committed: S1's universe and lateral products
S1_JSON = FD / "s1/readout/s1_assembly.json"
SF1 = REPO / "docs/orchestration/state/2d-closeout/stageF/methods/sf1/manifest/inputs-sha256.txt"
CR = FD / "fd/gencmp-e/c-r/overlap_refined.json"
CPL_BLOCK = FD / "fd/with-cpl/block/cpl_block.npz"
DP = FD / "fd/with-cpl/data-product/fd_data_product_cpl.json"
CMODEL5 = REPO / "nd-unfolding/pv-ladder/readouts/cmodel_5d.json"
CMODEL2 = REPO / "2d-unfolding/pv2d/cmodel/cmodel_2d.json"
PERIODS5 = FD / "fd/readout/fd_ct_5b_periods.json"
PL_JSON = REPO / "docs/orchestration/state/2d-closeout/stageF/methods/re2/run/partc_r2/partc-r2/playlist/playlist_term.json"
DEFINITION = gc.DEFINITION
LATERAL_BANDS = list(sa.LATERAL_BANDS)                                    # BeamAngleX ... Muon_Energy_MINOS
K_TOL = 1e-10


def committed_sha(path: Path, want: str, what: str) -> bytes:
    raw = Path(path).read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if got != want:
        raise X.Stop("0", f"{what} {path}: sha256 {got} != {want}")
    return raw


def stage(inp, src: Path, run_dir: Path) -> Path:
    """An O_NOATIME, digest-checked copy of a small pscratch file under <run>/inputs/, for a reader that opens its
    path itself (s1_assemble.flux_weights, x01_scale)."""
    dst = run_dir / "inputs" / src.name
    data = inp.bytes(src)
    if dst.exists():
        if dst.read_bytes() != data:
            raise X.Stop("-", f"{dst} exists with other bytes")
        return dst
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(data)
    return dst


def write_json(path: Path, rec: dict) -> None:
    if path.exists():
        raise X.Stop("-", f"refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".partial")
    tmp.write_text(json.dumps(rec, indent=1, default=float, allow_nan=False) + "\n")
    os.replace(tmp, path)
    print(json.dumps({"wrote": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}), flush=True)


def root_tree(data_or_fh, tree: str, branches: list[str]) -> dict:
    import uproot
    f = uproot.open(io.BytesIO(data_or_fh) if isinstance(data_or_fh, (bytes, bytearray)) else data_or_fh)
    return {k: np.asarray(v) for k, v in f[tree].arrays(branches, library="np").items()}


def hist2d_cells(data: bytes, cells2d: np.ndarray) -> np.ndarray:
    v, _ = gc.root_hist(data, "hXSec2D")
    return np.asarray(v, float).ravel(order="C")[cells2d]


# ---------------------------------------------------------------- v0


def cmd_v0(a) -> int:
    out = a.run_dir / "v0"
    if out.exists():
        raise X.Stop("-", f"refusing to overwrite {out}")
    inp = X.Inputs()
    # stage the two 5D inputs (boot reads the copies, so s5p_numerics opens no pscratch original)
    staged = {}
    for src in (NPZ_5D, BKG_5D):
        data = inp.bytes(src)
        dst = a.run_dir / "inputs" / src.name
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            raise X.Stop("-", f"refusing to overwrite {dst}")
        dst.write_bytes(data)
        staged[src.name] = hashlib.sha256(data).hexdigest()
    z = np.load(io.BytesIO((a.run_dir / "inputs" / NPZ_5D.name).read_bytes()), allow_pickle=False)
    edges = [np.asarray(z[f"edges_{i}"], float) for i in range(int(z["nedges"]))]
    import s5n_pseudo
    meas = np.asarray(z["measured"])
    obs = meas[s5n_pseudo.fid_mask(meas, edges)]
    bz = np.load(io.BytesIO((a.run_dir / "inputs" / BKG_5D.name).read_bytes()), allow_pickle=False)
    tmpl = np.asarray(bz["bkg_reco"])[s5n_pseudo.fid_mask(np.asarray(bz["bkg_reco"]), edges)]
    cv = inp.bytes(CV_OMNI)
    dat = root_tree(cv, "data", ["measured", "measured_pz", "measured_pass"])
    sig = root_tree(cv, "mc_signal_reco", ["MC", "MC_pz", "w_truth", "w_reco"])
    bkg = root_tree(cv, "mc_background", ["sim_background", "sim_background_pz"])
    keep = X.mask_2d_data(dat["measured"], dat["measured_pz"], dat["measured_pass"])
    d2 = np.stack([dat["measured"][keep], dat["measured_pz"][keep]], axis=1).astype(np.float32)
    b2 = np.stack([bkg["sim_background"], bkg["sim_background_pz"]], axis=1).astype(np.float32)
    counts = {"2d_data_rows": int(keep.sum()), "2d_bkg_entries": int(b2.shape[0]), "2d_mc_rows": int(sig["MC"].size),
              "5d_obs_rows": int(obs.shape[0]), "5d_tmpl_rows": int(tmpl.shape[0]), "5d_mc_rows": int(z["MCgen"].shape[0])}
    want = {"2d_data_rows": X.N_2D_DATA, "2d_bkg_entries": X.N_2D_BKG, "2d_mc_rows": X.N_MC, "5d_obs_rows": X.N_5D_OBS,
            "5d_tmpl_rows": X.N_5D_TMPL, "5d_mc_rows": X.N_MC}
    rec = {"schema": "fd-xcov-v0/1", "counts": counts, "counts_declared": want, "staged_sha256": staged}
    rec["counts_ok"] = counts == want
    rec["mc"] = X.mc_positional(sig["MC"], sig["MC_pz"], np.asarray(z["MCgen"]), sig["w_truth"], np.asarray(z["w_truth"]))
    joins = {}
    for name, big, small in (("data", d2, obs[:, :2]), ("background", b2, tmpl[:, :2])):
        try:
            m, amb = X.subsequence_join(big, small)
            unmatched = np.setdiff1d(np.arange(big.shape[0]), m)
            ub = big[unmatched]
            edge = (ub[:, 0] == np.float32(edges[0][-1])) | (ub[:, 1] == np.float32(edges[1][-1]))
            joins[name] = {"pass": True, "map": m, "ambiguous_rows": amb, "unmatched_2d": int(unmatched.size),
                           "unmatched_on_5d_upper_pt_or_pz_edge": int(edge.sum()),
                           "unmatched_other": int((~edge).sum())}
        except X.Stop as e:
            joins[name] = {"pass": False, "why": str(e)}
    rec["joins"] = {k: {kk: vv for kk, vv in v.items() if kk != "map"} for k, v in joins.items()}
    # the draw check: the regenerated sums of RE-2's replicas 1-100 are the ones their logs printed
    drawn = {}
    for b_ in X.STAT_REPLICAS:
        log = inp.bytes(RE2 / f"partb/logs/S1_{b_:03d}.log").decode(errors="replace")
        lines = X.draw_sums_line(b_)
        drawn[b_] = all(v in log for v in lines.values())
    rec["draw_check"] = {"replicas": len(drawn), "matching": int(sum(drawn.values())),
                         "first_mismatch": next((b_ for b_, ok in drawn.items() if not ok), None)}
    rec["pass"] = bool(rec["counts_ok"] and rec["mc"]["pass"] and all(v["pass"] for v in joins.values())
                       and rec["draw_check"]["matching"] == len(X.STAT_REPLICAS))
    rec["route"] = "B" if rec["pass"] else "A (the statistical stream falls back to r in [0, 1]; ruling 1)"
    rec["inputs"], rec["atime_deviations"] = inp.record, inp.atime_deviations()
    out.mkdir(parents=True)
    if rec["pass"]:
        np.savez(out / "maps.npz", j=joins["data"]["map"], entry=joins["background"]["map"])
        rec["maps_sha256"] = hashlib.sha256((out / "maps.npz").read_bytes()).hexdigest()
    write_json(out / "v0.json", rec)
    print(f"[V0] counts {rec['counts_ok']} mc {rec['mc']['pass']} joins "
          f"{ {k: v['pass'] for k, v in joins.items()} } -> route {rec['route'][0]}", flush=True)
    return 0


# ---------------------------------------------------------------- v1


def universe_list() -> list[tuple[str, int]]:
    s1 = json.loads(S1_JSON.read_text())
    names = sorted(k[len("S1_"):-len(".npz")] for k in s1["meta"]["inputs_sha256"]
                   if k.startswith("S1_") and k.endswith(".npz") and not k.startswith("S1seed") and k != "S1_CV.npz")
    out = []
    for n in names:
        b, i = n.rsplit("_", 1)
        out.append((b, int(i)))
    if len(out) != 175:
        raise X.Stop("V1", f"{len(out)} universes in S1's readout, 175 expected")
    return out


def weight_files(b: str, i: int, sf1: dict, det: dict) -> dict:
    """The wt and wr files S1's product for b:i read, by the digests its metadata records."""
    meta = json.loads(str(np.load(S1DIR / f"S1_{b}_{i}.npz", allow_pickle=False)["meta"]))
    want = meta["bank_weight_sha256"]
    out = {}
    for k in ("wt", "wr"):
        hits = [p for p, h in {**sf1, **det}.items() if h == want[k] and p.endswith(f"_{k}.npy")]
        if len(hits) != 1:
            raise X.Stop("V1", f"{b}:{i} {k}: {len(hits)} files carry its digest")
        out[k] = (Path(hits[0]), want[k])
    return out


def cmd_v1(a) -> int:
    out = a.run_dir / ("v1-probe" if a.probe else "v1")
    if out.exists():
        raise X.Stop("-", f"refusing to overwrite {out}")
    t0 = time.time()
    inp = X.Inputs()
    z = np.load(io.BytesIO(inp.bytes(NPZ_5D)), allow_pickle=False)
    mcgen, w5t, w5r = np.asarray(z["MCgen"]), np.asarray(z["w_truth"], float), np.asarray(z["w_reco"], float)
    sent = np.any(mcgen < X.SENTINEL, axis=1)
    inp.verify(UNI_OMNI)
    t_hash = time.time() - t0
    import uproot
    fh = inp.fileobj(UNI_OMNI)
    tree = uproot.open(fh)["mc_signal_reco"]
    base = {k: np.asarray(v) for k, v in tree.arrays(["MC", "MC_pz", "w_truth", "w_reco"], library="np").items()}
    v0u = X.mc_positional(base["MC"], base["MC_pz"], mcgen, base["w_truth"], w5t)
    sf1 = {p: h for h, p in (ln.split(None, 1) for ln in SF1.read_text().splitlines() if ln.strip())}
    sf1 = {p.strip(): h for p, h in sf1.items()}
    det = {str(DET_RECEIPT.parent / Path(p).name): h
           for p, h in json.loads(inp.bytes(DET_RECEIPT))["files_sha256"].items()}
    todo = universe_list()
    if a.probe:
        todo = [u for u in todo if u[0] == "MaRES"] + [u for u in todo if u[0] == "Flux" and u[1] < 10]
    res, scales = {}, []
    for b, i in todo:
        t1 = time.time()
        files = weight_files(b, i, sf1, det)
        sb = "".join(c if (c.isalnum() or c == "_") else "_" for c in b)
        br = tree.arrays([f"w_truth_{sb}_{i}", f"w_reco_{sb}_{i}"], library="np")
        r = {}
        for k, w2u, w2c, w5c in (("wt", br[f"w_truth_{sb}_{i}"], base["w_truth"], w5t),
                                  ("wr", br[f"w_reco_{sb}_{i}"], base["w_reco"], w5r)):
            path, h = files[k]
            inp.pins[str(path)] = h                       # pinned by S1's product metadata (and the manifest)
            w5u = np.load(io.BytesIO(inp.bytes(path)), allow_pickle=False).astype(float)
            use = (np.asarray(w2c) != 0) & (w5c != 0) & ~sent
            q = (w5u[use] / w5c[use]) / (np.asarray(w2u, float)[use] / np.asarray(w2c, float)[use])
            fin = np.isfinite(q)
            med = float(np.median(q[fin])) if fin.any() else float("nan")
            r[k] = {"rows": int(use.sum()), "nonfinite": int((~fin).sum()), "scale": med,
                    "max_rel": float(np.max(np.abs(q[fin] / med - 1))) if fin.any() else float("inf")}
            scales.append(med)
        r["pass"] = all(r[k]["max_rel"] <= X.RATIO_TOL and r[k]["nonfinite"] == 0 for k in ("wt", "wr"))
        r["seconds"] = round(time.time() - t1, 1)
        res[f"{b}:{i}"] = r
    bands = {}
    for key, r in res.items():
        bands.setdefault(key.rsplit(":", 1)[0], []).append(r["pass"])
    rec = {"schema": "fd-xcov-v1/1", "probe": bool(a.probe), "universe_omnifile_positional": v0u,
           "universes": res, "bands_pass": {b: all(v) for b, v in bands.items()},
           "scale_spread": float(np.max(np.abs(np.array(scales) / np.median(scales) - 1))) if scales else None,
           "seconds_hash": round(t_hash, 1), "seconds_total": round(time.time() - t0, 1),
           "inputs": inp.record, "atime_deviations": inp.atime_deviations()}
    if a.probe:
        per = np.mean([r["seconds"] for r in res.values()])
        rec["projected_seconds_175"] = round(t_hash + 175 * per, 0)
    write_json(out / "v1.json", rec)
    return 0


# ---------------------------------------------------------------- boot


def cmd_boot(a) -> int:
    import s5n_pseudo
    import s5p_numerics
    first, last = (int(v) for v in a.replicas.split(":"))
    reps = list(range(first, last + 1))
    tag = "native" if a.native else "xcov"
    outd = a.run_dir / "boot" / tag
    lane = outd / f"lane_{first}_{last}.json"
    if lane.exists():
        raise X.Stop("-", f"refusing to overwrite {lane}")
    npz, bkg = a.run_dir / "inputs" / X.NPZ_NAME, a.run_dir / "inputs" / X.BKG_NAME
    rec = {"schema": "fd-xcov-boot/1", "native": bool(a.native), "replicas": reps, "threads": a.threads}
    if not a.native:
        v0 = json.loads((a.run_dir / "v0" / "v0.json").read_text())
        if not v0["pass"]:
            raise X.Stop("B", "V0 did not pass: route B has no maps, and the fallback needs no replicas")
        mp = a.run_dir / "v0" / "maps.npz"
        if hashlib.sha256(mp.read_bytes()).hexdigest() != v0["maps_sha256"]:
            raise X.Stop("B", "maps.npz is not the file V0 recorded")
        m = np.load(mp, allow_pickle=False)
        fn = X.make_mapped_replica(m["j"], m["entry"])
        s5n_pseudo.bootstrap_replica = fn                # s5p_numerics.py:200 resolves it at call time
        rec["maps_sha256"] = v0["maps_sha256"]
    argv = ["--npz", str(npz), "--bkg", str(bkg), "--expect-npz-sha256", sa.INPUT_NPZ_SHA256,
            "--expect-bkg-sha256", sa.BKG_SHA256, "--config", "R", "--construction", "data",
            "--pairs", ",".join(f"{b}:{100 + b}" for b in reps), "--estimator-seed", "42",
            "--threads", str(a.threads), "--tag", tag, "--out", str(outd)]
    rec["argv"] = argv
    rc = s5p_numerics.main(argv)
    rec["rc"] = rc
    rec["products"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                       for b in reps for p in [outd / f"{tag}_b{b}_j{100 + b}.npz"] if p.exists()}
    if a.native and 1 in reps:                            # control B0
        new = np.load(outd / f"{tag}_b1_j101.npz", allow_pickle=False)["xsec_flat"]
        ref = np.load(S1DIR / "data_b1_j101.npz", allow_pickle=False)["xsec_flat"]
        rec["B0_bitwise"] = bool(np.array_equal(new, ref))
    rec["code_sha256"] = {Path(f).name: hashlib.sha256(Path(f).read_bytes()).hexdigest()
                          for f in (X.__file__, __file__, s5p_numerics.__file__, s5n_pseudo.__file__)}
    write_json(lane, rec)
    return 0 if rc == 0 and rec.get("B0_bitwise", True) else 1


# ---------------------------------------------------------------- k


def cmd_k(a) -> int:
    out = a.run_dir / "k"
    if out.exists():
        raise X.Stop("-", f"refusing to overwrite {out}")
    inp = X.Inputs()
    ctrl = {}

    def check(name, ok, detail=""):
        ctrl[name] = bool(ok)
        X.report(name.split()[0], name, ok, str(detail))

    defn = json.loads(DEFINITION.read_text())
    U = gc.cell_matrix()
    qz, pl, s5 = inp.npz(Q_R), inp.npz(CPL_R), inp.npz(S5_R)
    cells2d, area, x = np.asarray(pl["cells"], int), np.asarray(qz["area"], float), np.asarray(qz["cells_x_EU"], float)
    e_pt, e_pz = (np.asarray(sa.s1.FINE[k], float) for k in ("pt", "pz"))
    A, B = X.quadrant_vectors(defn, cells2d, area, e_pt, e_pz)
    blk = np.load(CPL_BLOCK, allow_pickle=False)
    dp = json.loads(DP.read_text())
    f = np.asarray(blk["f"], float)
    s1 = inp.npz(S1_NPZ)
    cr = json.loads(CR.read_text())["quadrants"]
    S16 = np.array([cr[q]["S16"] for q in X.QNAMES])
    S2 = B @ x
    check("C-R S2D: B x reproduces C-R's E_R quadrant sums (1e-12)",
          np.allclose(S2, [cr[q]["2D"]["S"] for q in X.QNAMES], rtol=1e-12, atol=0))
    check("C-R S16: A f plus the unreported boxes reproduce C-R's S16 (1e-12)", np.allclose(
        A @ f + [sum(cr[q]["unreported_boxes_P5"].values()) for q in X.QNAMES], S16, rtol=1e-12, atol=0))
    d = S16 - S2
    box_var = np.diag([sum(v ** 2 for v in cr[q]["unreported_boxes_P5"].values()) for q in X.QNAMES])

    # own matrices at quadrant level
    C16q = A @ np.asarray(blk["C_total_plus_C_resp_plus_C_PL5D"], float) @ A.T + box_var
    Q2q = B @ np.asarray(qz["total_plus_C_PL"], float) @ B.T
    cm2 = json.loads(CMODEL2.read_text())
    check("K0 C_model,2D's cells are Q_R's", list(cm2["cells"]) == cells2d.tolist())
    S2m = np.asarray(cm2["S"], float)
    V2m = [B @ (x * s) for s in S2m]
    M2q = sum(np.outer(v, v) for v in V2m)
    C2q = Q2q + M2q

    def own16(key):
        return A @ np.asarray(s1[key], float) @ A.T

    def own2(key):
        return B @ np.asarray(s5[key], float) @ B.T

    def vec2(path: Path) -> np.ndarray:
        return hist2d_cells(inp.bytes(path), cells2d)

    crosses, bounded = {}, {}
    v1 = json.loads((a.run_dir / "v1" / "v1.json").read_text())
    w = sa.flux_weights(stage(inp, CONSTRAINT, a.run_dir))
    s1meta = json.loads(S1_JSON.read_text())["meta"]["inputs_sha256"]
    by_band = {}
    for b, i in universe_list():
        by_band.setdefault(b, []).append(i)
    for b, idx in sorted(by_band.items()):
        X16 = np.array([A @ (U @ sa.xs(S1DIR / f"S1_{b}_{i}.npz")) for i in sorted(idx)
                        if committed_sha(S1DIR / f"S1_{b}_{i}.npz", s1meta[f"S1_{b}_{i}.npz"], "S1 product")])
        X2 = np.array([B @ vec2(RE2 / f"partb/out/U_{b}_{i}/xsec.root") for i in sorted(idx)])
        ww = w if b == sa.FLUX else None
        check(f"K1 16 band {b}: the products give S1's block (1e-10)",
              np.allclose(X.cross_cov(X16, X16, ww), own16(f"C_band_{b}"), rtol=K_TOL, atol=K_TOL * abs(own16(f"C_band_{b}")).max()))
        check(f"K1 2D band {b}: the products give S5_R's block (1e-10)",
              np.allclose(X.cross_cov(X2, X2, ww), own2(f"band_{b}"), rtol=K_TOL, atol=K_TOL * abs(own2(f"band_{b}")).max()))
        K = X.cross_cov(X16, X2, ww)
        if v1["bands_pass"].get(b):
            crosses[f"band:{b}"] = K
        else:
            bounded[f"band:{b}"] = X.psd_sqrt(own16(f"C_band_{b}")) @ X.psd_sqrt(own2(f"band_{b}"))
    flux5 = np.asarray(np.load(io.BytesIO((a.run_dir / "inputs" / X.NPZ_NAME).read_bytes()), allow_pickle=False)["flux"], float)
    scale = sa.x01_scale(stage(inp, X01, a.run_dir), flux5)
    pti = sa.pt_index()
    ipt2 = cells2d // (len(e_pz) - 1)
    for b in LATERAL_BANDS:
        X16, X2 = [], []
        for i in (0, 1):
            p5 = S1DIR / f"lat_{b}_{i}_b-_j-.npz"
            committed_sha(p5, s1meta[p5.name], "S1 lateral")
            xs5 = sa.xs(p5) * (scale[i][pti] if b == sa.MINOS else 1.0)
            X16.append(A @ (U @ xs5))
            v = vec2(RE2 / f"partb/out/S3_{b.replace('_', '')}{i}/xsec.root")
            X2.append(B @ (v * (scale[i][ipt2] if b == sa.MINOS else 1.0)))
        X16, X2 = np.array(X16), np.array(X2)
        check(f"K1 16 lateral {b} (1e-10)", np.allclose(X.cross_cov(X16, X16), own16(f"C_lat_{b}"), rtol=K_TOL,
                                                        atol=K_TOL * abs(own16(f"C_lat_{b}")).max()))
        check(f"K1 2D lateral {b} (1e-10)", np.allclose(X.cross_cov(X2, X2), own2(f"band_{b}"), rtol=K_TOL,
                                                        atol=K_TOL * abs(own2(f"band_{b}")).max()))
        crosses[f"lat:{b}"] = X.cross_cov(X16, X2)
    n16, n2 = X.NORM * (A @ f), X.NORM * (B @ x)
    check("K1 normalization, both sides (1e-10)", np.allclose(np.outer(n16, n16), own16("C_normalization"), rtol=K_TOL)
          and np.allclose(np.outer(n2, n2), own2("band___Normalization_flat"), rtol=K_TOL))
    crosses["normalization"] = np.outer(n16, n2)
    per = json.loads(PERIODS5.read_text())
    k16, k2 = float(per["constants"]["k"]), float(json.loads(PL_JSON.read_text())["report"]["k_factor"])
    V16p, V2p = [], []
    for X_ in ("PA", "PB", "PC"):
        g16 = np.asarray(per["g_vs_5A"]["periods"][X_]["g_5b"], float)
        e16 = float(per["constants"]["exposure_share"][X_])
        V16p.append(np.sqrt(k16 * e16) * (A @ (f * g16)))
        V2p.append(np.sqrt(k2) * (B @ (np.sqrt(np.asarray(pl[f"e_{X_}"], float)) * x * np.asarray(pl[f"g_{X_}"], float))))
    check("K1 C_PL5D from its periods (1e-10)", np.allclose(sum(np.outer(v, v) for v in V16p),
                                                       A @ np.asarray(blk["C_PL5D"], float) @ A.T, rtol=K_TOL))
    check("K1 C_PL_R from its periods (1e-10)", np.allclose(sum(np.outer(v, v) for v in V2p),
                                                       B @ np.asarray(pl["C_PL"], float) @ B.T, rtol=K_TOL))
    crosses["C_PL (constructed, period-paired)"] = X.outer_pairs(V16p, V2p)
    cm5 = json.loads(CMODEL5.read_text())
    check("K0 the C_model vertices are paired in one order", list(cm5["vertices"]) == list(cm2["vertices"]))
    V16m = [A @ (f * np.asarray(s, float)) for s in cm5["S"]]
    check("K1 C_model_abs from its vertices (1e-10)", np.allclose(
        sum(np.outer(v, v) for v in V16m), A @ np.asarray(dp["matrices"]["C_model_abs"], float) @ A.T, rtol=K_TOL))
    crosses["C_model (vertex-paired)"] = X.outer_pairs(V16m, V2m)

    # the statistical stream: route B if V0 and B0 held and every paired replica exists, else route A
    v0 = json.loads((a.run_dir / "v0" / "v0.json").read_text())
    S16stat, S2stat = own16("C_stat"), own2("stat")
    lanes = sorted((a.run_dir / "boot" / "xcov").glob("lane_*.json")) if v0["pass"] else []
    natives = sorted((a.run_dir / "boot" / "native").glob("lane_*.json"))
    b0 = any(json.loads(p.read_text()).get("B0_bitwise") for p in natives)
    prods = {}
    for p in lanes:
        prods.update(json.loads(p.read_text())["products"])
    want = {f"xcov_b{b}_j{100 + b}.npz" for b in X.STAT_REPLICAS}
    route = "B" if (v0["pass"] and b0 and set(prods) >= want) else "A"
    stat = None
    if route == "B":
        S16r = np.array([A @ (U @ sa.xs(a.run_dir / "boot" / "xcov" / n))
                         for n in sorted(want, key=lambda s: int(s.split("_b")[1].split("_")[0]))
                         if committed_sha(a.run_dir / "boot" / "xcov" / n, prods[n], "paired replica")])
        S2r = np.array([B @ vec2(RE2 / f"partb/out/S1_{b:03d}/xsec.root") for b in X.STAT_REPLICAS])
        stat = X.stat_cross(S16r, S2r, np.sqrt(np.diag(S16stat)), np.sqrt(np.diag(S2stat)))
        crosses["stat (paired replicas)"] = stat["K"]
    K = sum(crosses.values())

    M = sum(bounded.values(), np.zeros((X.N_Q, X.N_Q)))
    if route == "A":
        M = M + X.bound_matrix(S16stat, S2stat)

    def evaluate(C2, Kx, label):
        if not M.any():
            Vd = X.Vd_of(C16q, C2, Kx)
            return {"label": label, "route": "B", **X.verdict(d, Vd), "Vd": Vd.tolist()}
        return {"label": label, "route": "A" if route == "A" else "B, with bands bounded", **X.route_a(d, C16q, C2, Kx, M)}

    primary = evaluate(C2q, K, "primary: the reported sixteen-cell matrix against Q_R + C_model,2D (vertex-paired)")
    alone = evaluate(Q2q, K - crosses["C_model (vertex-paired)"], "printed: against Q_R alone (C_model,16 unpaired)")
    nopl = evaluate(C2q, K - crosses["C_PL (constructed, period-paired)"],
                    "sensitivity: the C_PL pair set to 0")
    blocks16 = {"C_total + C_resp + C_PL,5D": C16q - box_var, "unreported boxes": box_var}
    blocks2 = {"Q_R": Q2q, "C_model,2D": M2q}
    Vd = X.Vd_of(C16q, C2q, K)
    rho = {q: float((K[i, i]) / np.sqrt(C16q[i, i] * C2q[i, i])) for i, q in enumerate(X.QNAMES)}
    rec = {"schema": "fd-xcov-k/1", "route": route, "d": d.tolist(), "S16": S16.tolist(), "S2D": S2.tolist(),
           "rho_q": rho, "primary": primary, "Q_R_alone": alone, "C_PL_pair_zero": nopl,
           "shares_primary": X.shares(blocks16, blocks2, crosses, Vd),
           "crosses": {k: v.tolist() for k, v in crosses.items()}, "bounded": sorted(bounded),
           "own": {"C16q": C16q.tolist(), "C2q": C2q.tolist(), "Q2q": Q2q.tolist(), "M2q": M2q.tolist()},
           "stat": None if stat is None else {k: np.asarray(v).tolist() for k, v in stat.items()},
           "controls": ctrl, "inputs": inp.record, "atime_deviations": inp.atime_deviations(),
           "rule": "agree iff joint chi2_4 p >= 0.05 and every |z| <= 2.50; a quadrant over 2.50 is a named differ, "
                   "and so is a joint p < 0.05 with no quadrant over (the director's ruling 3)"}
    write_json(out / "k.json", rec)
    print(f"[K] route {route}: primary {primary['outcome']}", flush=True)
    return 0

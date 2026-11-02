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
V1_DIR = "v1-a2"   # addendum X-A2: the full V1 rerun; the failed run (60679146) wrote no readout
V0_DIR = "v0-a1"   # addendum X-A1: the amended V0; the first run's v0/v0.json stays as the record
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
COMMITTED = {   # sha256 of each committed input K reads (each also fixed by the bound commit's git blob)
    CR: "f1f2fb7813e7f4904f5a6bcfc897a8f0a8e19b001809ebecb4975ec8bcd3c906",
    CPL_BLOCK: "d9aa32fdb64357760348c9ccbc32fbea81d517f0f0786eedf17ab4946eaca59f",
    DP: "d6752d2c64aad4426375c03a3171a7015f031e2027928cf89aea6cd3bbb84d50",
    CMODEL5: "3cfdc6a5b8c6cea5f99b4678e27f6ca5f7973ee57a79b9d139798f0751cfcd60",
    CMODEL2: "aabc66d106a49484d486fb055bfb4280187898f98ca406e010f153af57702dd0",
    PERIODS5: "a5b17895b1189543d773e94717e14cd9b1409535e366c96788f94bf6f40759db",
    PL_JSON: "a952adda441e1fa7d29eb44e064b11991a09ded3682c2530193222e45164ed26",
    S1_JSON: "81e5ef3fe8e7b055360dc43b8a8240c9b5c39c8aa6e7c507b3211d305b326b21",
}
CMODEL_R = REPO / "docs/orchestration/state/2d-closeout/stageF/methods/re2/run/partc_r2/partc-r2/cmodel/cmodel_R.json"
COMMITTED[CMODEL_R] = "571b1e8bd9fe1de6ebf18d70bd1311aec63d2470a7c8daa01cb2b3303d5c0569"   # partc-r2/SHA256SUMS:15
V1_FULL_CAP_S = 1.75 * 3600                     # the full run's cap in seconds of one node (declaration section 6)
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
    out = a.run_dir / V0_DIR
    if (out / "v0.json").exists():
        raise X.Stop("-", f"refusing to overwrite {out / 'v0.json'}")
    inp = X.Inputs()
    # stage the two 5D inputs (boot reads the copies, so s5p_numerics opens no pscratch original); a copy left by an
    # interrupted V0 is reused only if it is the pinned bytes
    staged = {src.name: hashlib.sha256(stage(inp, src, a.run_dir).read_bytes()).hexdigest() for src in (NPZ_5D, BKG_5D)}
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
    # the draw check: the regenerated data and MC sums of RE-2's replicas 1-100 are the ones their logs printed, and
    # the background stream is the one each replica's p1Streams record states (addendum X-A1)
    drawn, legs, bkg_why = {}, {"data": 0, "mc": 0, "bkg": 0}, {}
    for b_ in X.STAT_REPLICAS:
        log = inp.bytes(RE2 / f"partb/logs/S1_{b_:03d}.log").decode(errors="replace")
        lines = X.draw_sums_line(b_)
        bad = X.bkg_stream_check(X.p1_streams_record(inp.bytes(RE2 / f"partb/out/S1_{b_:03d}/xsec.root")), b_)
        ok = {"data": lines["data"] in log, "mc": lines["mc"] in log, "bkg": not bad}
        for k, v in ok.items():
            legs[k] += int(v)
        if bad:
            bkg_why[b_] = bad
        drawn[b_] = all(ok.values())
    rec["draw_check"] = {"replicas": len(drawn), "matching": int(sum(drawn.values())), "matching_by_leg": legs,
                         "first_mismatch": next((b_ for b_, ok in drawn.items() if not ok), None),
                         "bkg_failures": {str(k): v for k, v in list(bkg_why.items())[:5]}}
    rec["pass"] = bool(rec["counts_ok"] and rec["mc"]["pass"] and all(v["pass"] for v in joins.values())
                       and rec["draw_check"]["matching"] == len(X.STAT_REPLICAS))
    rec["route"] = "B" if rec["pass"] else "A (the statistical stream falls back to r in [0, 1]; ruling 1)"
    rec["inputs"], rec["atime_deviations"] = inp.record, inp.atime_deviations()
    out.mkdir(parents=True, exist_ok=True)
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
    """The wt and wr files S1's product for b:i read, by the digests its metadata records: (path, digest, n_matches).
    Addendum X-A2: several pinned files can carry one digest (byte-identical weights, e.g. a knob that leaves the CC
    weights at CV), and any of them is the file S1 read; the sorted-first is taken, and zero matches stop V1."""
    s1meta = json.loads(S1_JSON.read_text())["meta"]["inputs_sha256"]
    committed_sha(S1DIR / f"S1_{b}_{i}.npz", s1meta[f"S1_{b}_{i}.npz"], "S1 product")
    meta = json.loads(str(np.load(S1DIR / f"S1_{b}_{i}.npz", allow_pickle=False)["meta"]))
    want = meta["bank_weight_sha256"]
    out = {}
    for k in ("wt", "wr"):
        hits = sorted(p for p, h in {**sf1, **det}.items() if h == want[k] and p.endswith(f"_{k}.npy"))
        if not hits:
            raise X.Stop("V1", f"{b}:{i} {k}: no pinned file carries its digest")
        out[k] = (Path(hits[0]), want[k], len(hits))
    return out


def npy_shape(path: Path) -> tuple:
    """The shape in an .npy file's header, read O_NOATIME (the dry V1's array check; no array is read)."""
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOATIME", 0))
    with os.fdopen(fd, "rb") as fh:
        version = np.lib.format.read_magic(fh)
        read = np.lib.format.read_array_header_1_0 if version == (1, 0) else np.lib.format.read_array_header_2_0
        shape, _, _ = read(fh)
    return tuple(shape)


def multi_match_classes(lookups: dict) -> dict:
    """For each digest that several pinned files carry, the universes (and so the bands) whose lookups resolve to it."""
    by = {}
    for key, (digest, n) in lookups.items():
        if n > 1:
            by.setdefault(digest, {"n_files": n, "lookups": []})["lookups"].append(key)
    for c in by.values():
        c["bands"] = sorted({k.split(":")[0] for k in c["lookups"]})
    return by


def cmd_v1(a) -> int:
    out = a.run_dir / ("v1-probe" if a.probe else V1_DIR)
    if out.exists() and not a.dry:
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
    if a.dry:
        return v1_dry(todo, sf1, det, tree, base, mcgen)
    res, scales, lookups = {}, [], {}
    for b, i in todo:
        t1 = time.time()
        files = weight_files(b, i, sf1, det)
        sb = "".join(c if (c.isalnum() or c == "_") else "_" for c in b)
        br = tree.arrays([f"w_truth_{sb}_{i}", f"w_reco_{sb}_{i}"], library="np")
        r = {}
        for k, w2u, w2c, w5c in (("wt", br[f"w_truth_{sb}_{i}"], base["w_truth"], w5t),
                                  ("wr", br[f"w_reco_{sb}_{i}"], base["w_reco"], w5r)):
            path, h, nm = files[k]
            lookups[f"{b}:{i}:{k}"] = (h, nm)
            inp.pins[str(path)] = h                       # pinned by S1's product metadata (and the manifest)
            w5u = np.load(io.BytesIO(inp.bytes(path)), allow_pickle=False).astype(float)
            r[k] = dict(X.ratio_test(w2u, w2c, w5u, w5c, sent), file=str(path), n_matches=nm)
            scales.append(r[k]["scale"])
        r["pass"] = all(r[k]["pass"] for k in ("wt", "wr"))
        r["seconds"] = round(time.time() - t1, 1)
        res[f"{b}:{i}"] = r
    bands = {}
    for key, r in res.items():
        bands.setdefault(key.rsplit(":", 1)[0], []).append(r["pass"])
    rec = {"schema": "fd-xcov-v1/2", "probe": bool(a.probe), "universe_omnifile_positional": v0u,
           "universes": res, "bands_pass": {b: all(v) for b, v in bands.items()},
           "multi_match_classes": multi_match_classes(lookups),
           "scale_spread": float(np.max(np.abs(np.array(scales) / np.median(scales) - 1))) if scales else None,
           "seconds_hash": round(t_hash, 1), "seconds_total": round(time.time() - t0, 1),
           "inputs": inp.record, "atime_deviations": inp.atime_deviations()}
    if a.probe:
        per = np.mean([r["seconds"] for r in res.values()])
        rec["projected_seconds_175"] = round(t_hash + 175 * per, 0)
        rec["within_full_cap"] = bool(rec["projected_seconds_175"] <= V1_FULL_CAP_S)
    write_json(out / "v1.json", rec)
    return 0


def v1_dry(todo, sf1, det, tree, base, mcgen) -> int:
    """Addendum X-A2's sweep: every lookup the full V1 makes, with no weight array read and nothing written. Per
    universe: S1's product against its pin, both weight files by digest (count, the file taken, its .npy shape), and
    both universe-omnifile branches (present, with the tree's entries); the base arrays' lengths once."""
    keys, n_tree = set(tree.keys()), int(tree.num_entries)
    rows, lookups, bad = {}, {}, []
    for b, i in todo:
        files = weight_files(b, i, sf1, det)
        sb = "".join(c if (c.isalnum() or c == "_") else "_" for c in b)
        row = {}
        for k, branch in (("wt", f"w_truth_{sb}_{i}"), ("wr", f"w_reco_{sb}_{i}")):
            path, h, nm = files[k]
            lookups[f"{b}:{i}:{k}"] = (h, nm)
            shape = npy_shape(path) if path.exists() else None
            ok = path.exists() and shape == (X.N_MC,) and branch in keys
            row[k] = {"n_matches": nm, "file": str(path), "exists": path.exists(), "npy_shape": shape,
                      "branch": branch, "branch_present": branch in keys, "pass": ok}
            if not ok:
                bad.append(f"{b}:{i}:{k}")
        rows[f"{b}:{i}"] = row
    n = {k: int(np.asarray(v).shape[0]) for k, v in base.items()}
    ok_base = n_tree == X.N_MC and all(v == X.N_MC for v in n.values()) and mcgen.shape[0] == X.N_MC
    hist = {}
    for _, nm in lookups.values():
        hist[nm] = hist.get(nm, 0) + 1
    rec = {"schema": "fd-xcov-v1-dry/1", "universes": len(rows), "lookups": len(lookups),
           "n_matches_histogram": {str(k): v for k, v in sorted(hist.items())},
           "zero_match_lookups": 0, "failing_lookups": bad, "tree_entries": n_tree, "base_lengths": n,
           "base_pass": ok_base, "multi_match_classes": multi_match_classes(lookups), "rows": rows,
           "pass": not bad and ok_base}
    print(json.dumps(rec, default=str), flush=True)
    return 0 if rec["pass"] else 1


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
        v0 = json.loads((a.run_dir / V0_DIR / "v0.json").read_text())
        if not v0["pass"]:
            raise X.Stop("B", "V0 did not pass: route B has no maps, and the fallback needs no replicas")
        mp = a.run_dir / V0_DIR / "maps.npz"
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
        s1meta = json.loads(S1_JSON.read_text())["meta"]["inputs_sha256"]
        committed_sha(S1DIR / "data_b1_j101.npz", s1meta["data_b1_j101.npz"], "B0 reference")
        ref = np.load(S1DIR / "data_b1_j101.npz", allow_pickle=False)["xsec_flat"]
        rec["B0_bitwise"] = bool(np.array_equal(new, ref))
    rec["code_sha256"] = {Path(f).name: hashlib.sha256(Path(f).read_bytes()).hexdigest()
                          for f in (X.__file__, __file__, s5p_numerics.__file__, s5n_pseudo.__file__)}
    write_json(lane, rec)
    return 0 if rc == 0 and rec.get("B0_bitwise", True) else 1


# ---------------------------------------------------------------- k


def read_committed(path: Path) -> bytes:
    return committed_sha(path, COMMITTED[path], "committed input")


def boot_state(run_dir: Path, v0_pass: bool) -> dict:
    """Ruling A2: K runs once, after BOOT has ended or was never due. BOOT is due iff V0 passed; it has ended when its
    native lane has written its record and, if B0 held, all eight mapped lanes have too."""
    if not v0_pass:
        return {"due": False, "ended": True, "b0": None, "lanes": 0}
    nat = list((run_dir / "boot" / "native").glob("lane_*.json"))
    if not nat:
        return {"due": True, "ended": False, "b0": None, "lanes": 0}
    b0 = bool(json.loads(nat[0].read_text()).get("B0_bitwise"))
    lanes = sorted((run_dir / "boot" / "xcov").glob("lane_*.json"))
    return {"due": True, "ended": (not b0) or len(lanes) == 8, "b0": b0, "lanes": len(lanes)}


def v1_state(run_dir: Path) -> dict:
    """Ruling A1: the full V1 readout, or a probe that projected beyond the full run's cap, in which case every band is
    bounded; anything else stops K."""
    full, probe = run_dir / V1_DIR / "v1.json", run_dir / "v1-probe" / "v1.json"
    if full.exists():
        return {"source": "full", "bands_pass": json.loads(full.read_text())["bands_pass"]}
    if probe.exists() and not json.loads(probe.read_text()).get("within_full_cap", True):
        return {"source": "probe beyond the full run's cap: every band bounded", "bands_pass": {}}
    raise X.Stop("K", "no full V1 readout, and no probe that projected beyond the full run's cap")


def cmd_k(a) -> int:
    if a.own_only:
        return k_own_only(a)
    out = a.run_dir / "k"
    if out.exists():
        raise X.Stop("-", f"refusing to overwrite {out}: K runs once (a stop is final)")
    inp = X.Inputs()
    ctrl = {}

    def check(name, ok, detail=""):
        ctrl[name] = bool(ok)
        X.report(name.split()[0], name, ok, str(detail))

    v0 = json.loads((a.run_dir / V0_DIR / "v0.json").read_text())
    bs = boot_state(a.run_dir, v0["pass"])
    if not bs["ended"]:
        raise X.Stop("K", f"BOOT has not ended ({bs}); K runs once, after it")
    v1 = v1_state(a.run_dir)
    rec = {"schema": "fd-xcov-k/1", "boot": bs, "v1_source": v1["source"]}
    try:
        res = k_compute(a, inp, check, v0, bs, v1)
        rec.update(res)
        rc = 0
    except X.Stop as e:                      # a stop is recorded, so K cannot be rerun on another route (ruling A2)
        rec["stop"], rc = str(e), 1
    rec.update(controls=ctrl, inputs=inp.record, atime_deviations=inp.atime_deviations())
    write_json(out / "k.json", rec)
    print(f"[K] {rec.get('route')}: {rec.get('primary', {}).get('outcome', rec.get('stop'))}", flush=True)
    return rc


def k_own_only(a) -> int:
    """Addendum X-A2's dry run of K: K0, K1 and K2 on each side's own matrices, through k_compute itself with every
    cross block, the statistical cross term, z and chi2 skipped; the small staged files go to a scratch directory and
    nothing is written under the run directory. Prints the controls."""
    import tempfile
    inp, ctrl = X.Inputs(), {}

    def check(name, ok, detail=""):                 # records every control and goes on, so one pass lists them all
        ctrl[name] = bool(ok)
        print(f"[{'PASS' if ok else 'FAIL'} {name.split()[0]}] {name}" + ("" if ok else f": {detail}"), flush=True)

    v0 = json.loads((a.run_dir / V0_DIR / "v0.json").read_text())
    bs = boot_state(a.run_dir, v0["pass"])
    rec = {"schema": "fd-xcov-k-own/1", "boot": bs}
    with tempfile.TemporaryDirectory() as td:
        try:
            rec.update(k_compute(a, inp, check, v0, bs, None, stage_root=Path(td)))
            rc = 0
        except X.Stop as e:
            rec["stop"], rc = str(e), 1
    rec.update(controls=ctrl, n_controls=len(ctrl), failing=[k for k, v in ctrl.items() if not v],
               all_pass=rc == 0 and all(ctrl.values()),
               atime_deviations=inp.atime_deviations())
    print(json.dumps(rec, default=float), flush=True)
    return rc


def k_own_tail(a, check, v0, bs, A, U, C16q, C2q, S16stat, S2stat, vec2) -> dict:
    """The dry run's end: K2 on each side's own matrices (the joint matrix with a zero cross block, which is PSD iff
    each side is), and the route-B inputs' format (each paired replica as BOOT recorded it, read as a 16-cell vector;
    each RE-2 replica as a 2D vector); no cross term is formed."""
    Z = np.zeros((X.N_Q, X.N_Q))
    check("K2 each side's own matrix is PSD (C16q and Q_R + C_model,2D)", X.joint_psd(C16q, C2q, Z))
    check("K2 each side's own statistical matrix is PSD", X.joint_psd(S16stat, S2stat, Z))
    out = {"replicas": None}
    if v0["pass"] and bs["b0"]:
        prods = {}
        for p in sorted((a.run_dir / "boot" / "xcov").glob("lane_*.json")):
            prods.update(json.loads(p.read_text())["products"])
        want = [f"xcov_b{b}_j{100 + b}.npz" for b in X.STAT_REPLICAS]
        check("B all 100 paired replicas are recorded by BOOT's lanes", all(n in prods for n in want),
              str(sorted(set(want) - set(prods))[:5]))
        for n in want:
            committed_sha(a.run_dir / "boot" / "xcov" / n, prods[n], "paired replica")
        sh16 = {np.shape(A @ (U @ sa.xs(a.run_dir / "boot" / "xcov" / n))) for n in want}
        sh2 = {np.shape(vec2(RE2 / f"partb/out/S1_{b:03d}/xsec.root")) for b in X.STAT_REPLICAS}
        check("B every paired replica reads as a 4-quadrant vector, and every RE-2 replica as a 2D vector",
              sh16 == {(X.N_Q,)} and len(sh2) == 1, f"{sh16} {sh2}")
        out["replicas"] = {"n": len(want), "shapes_16": sorted(map(str, sh16)), "shapes_2d": sorted(map(str, sh2))}
    return out


def k_compute(a, inp, check, v0, bs, v1, stage_root: Path | None = None) -> dict:
    """K (declaration sections 3-5). With stage_root given (the dry run, v1 None): the own-side controls only."""
    own_only = stage_root is not None
    sroot = stage_root if own_only else a.run_dir
    defn = json.loads(DEFINITION.read_text())
    U = gc.cell_matrix()
    qz, pl, s5 = inp.npz(Q_R), inp.npz(CPL_R), inp.npz(S5_R)
    cells2d, area, x = np.asarray(pl["cells"], int), np.asarray(qz["area"], float), np.asarray(qz["cells_x_EU"], float)
    _, (e_pt, e_pz) = gc.root_hist(inp.bytes(RE2 / "partb/out/ER/xsec.root"), "hXSec2D")
    A, B = X.quadrant_vectors(defn, cells2d, area, np.asarray(e_pt, float), np.asarray(e_pz, float))
    blk = np.load(io.BytesIO(read_committed(CPL_BLOCK)), allow_pickle=False)
    dp, cr = json.loads(read_committed(DP)), json.loads(read_committed(CR))["quadrants"]
    f = np.asarray(blk["f"], float)
    s1 = inp.npz(S1_NPZ)
    S16 = np.array([cr[q]["S16"] for q in X.QNAMES])
    S2 = B @ x
    boxes = np.array([sum(cr[q]["unreported_boxes_P5"].values()) for q in X.QNAMES])
    box_var = np.diag([sum(v ** 2 for v in cr[q]["unreported_boxes_P5"].values()) for q in X.QNAMES])
    check("K0 C-R's S2D is B x (1e-12)", np.allclose(S2, [cr[q]["2D"]["S"] for q in X.QNAMES], rtol=1e-12, atol=0))
    check("K0 C-R's S16 is A f plus the boxes (1e-12)", np.allclose(A @ f + boxes, S16, rtol=1e-12, atol=0))
    d = S16 - S2
    C16q = A @ np.asarray(blk["C_total_plus_C_resp_plus_C_PL5D"], float) @ A.T + box_var
    Q2q = B @ np.asarray(qz["total_plus_C_PL"], float) @ B.T
    check("K0 C-R's sigma16 and 2D sigma are sqrt(diag) of C16q and B Q_R B^T (1e-12)",
          np.allclose(np.sqrt(np.diag(C16q)), [cr[q]["sigma16_reported"] for q in X.QNAMES], rtol=1e-12, atol=0)
          and np.allclose(np.sqrt(np.diag(Q2q)), [cr[q]["2D"]["sigma"] for q in X.QNAMES], rtol=1e-12, atol=0))
    cm2, cmr = json.loads(read_committed(CMODEL2)), json.loads(read_committed(CMODEL_R))
    check("K0 C_model,2D's cells are C_PL_R's (the 205-cell index C-R used)", list(cm2["cells"]) == cells2d.tolist())
    check("K0 cmodel_R.json was built from this cmodel_2d.json",
          cmr["inputs"]["cmodel_json"]["sha256"] == COMMITTED[CMODEL2])
    S2m = np.asarray(cm2["S"], float)
    Cabs2 = (S2m.T @ S2m) * np.outer(x, x)
    sQ, sQM = (np.asarray(cmr["per_cell"][k], float) for k in ("sigma_Q_R", "sigma_Q_R_plus_C_model"))
    diagQ = np.diag(np.asarray(qz["total_plus_C_PL"], float))
    rel = np.allclose(sQ, np.sqrt(diagQ) / x, rtol=X.K_TOL, atol=0)
    absu = np.allclose(sQ, np.sqrt(diagQ), rtol=X.K_TOL, atol=0)
    want = np.sqrt(diagQ + np.diag(Cabs2)) / (x if rel else 1.0)
    check("K1 C_model,2D from its vertices gives cmodel_R.json's per-cell sigma of Q_R + C_model (1e-10)",
          (rel or absu) and np.allclose(sQM, want, rtol=X.K_TOL, atol=0))
    V2m = [B @ (x * s) for s in S2m]
    M2q = sum(np.outer(v, v) for v in V2m)
    C2q = Q2q + M2q

    def own16(key):
        return A @ np.asarray(s1[key], float) @ A.T

    def own2(key):
        return B @ np.asarray(s5[key], float) @ B.T

    def vec2(path: Path) -> np.ndarray:
        return hist2d_cells(inp.bytes(path), cells2d)

    nulls = []

    def k1(label, p16, c16, p2, c2, name16, name2):
        """K1 on one band's two sides (X.k1_band); a band null on both sides is listed by name, side and ratio."""
        r = X.k1_band(p16, c16, p2, c2, C16q, C2q)
        ratios = f"16 max ratio {r['ratio16']:.3g} of C16q, 2D {r['ratio2']:.3g} of C2q"
        if r["kind"] == "null":
            nulls.extend({"band": label, "side": sd, "max_ratio": r[f"ratio{k}"]} for sd, k in (("16", "16"), ("2D", "2")))
            print(f"[K1 null] {label}: {ratios}", flush=True)
            name16, name2 = (f"K1 {sd} {label}: null on both sides (below 1e-12 of C16q and of C2q)" for sd in ("16", "2D"))
        elif r["kind"] == "mixed":
            name16, name2 = (f"K1 {sd} {label}: null on one side only" for sd in ("16", "2D"))
        check(name16, r["ok16"], ratios)
        check(name2, r["ok2"], ratios)

    crosses, bounded = {}, {}
    w = sa.flux_weights(stage(inp, CONSTRAINT, sroot))
    s1meta = json.loads(read_committed(S1_JSON))["meta"]["inputs_sha256"]
    by_band = {}
    for b, i in universe_list():
        by_band.setdefault(b, []).append(i)
    for b, idx in sorted(by_band.items()):
        for i in idx:
            committed_sha(S1DIR / f"S1_{b}_{i}.npz", s1meta[f"S1_{b}_{i}.npz"], "S1 product")
        X16 = np.array([A @ (U @ sa.xs(S1DIR / f"S1_{b}_{i}.npz")) for i in sorted(idx)])
        X2 = np.array([B @ vec2(RE2 / f"partb/out/U_{b}_{i}/xsec.root") for i in sorted(idx)])
        ww = w if b == sa.FLUX else None
        k1(f"band {b}", X.cross_cov(X16, X16, ww), own16(f"C_band_{b}"), X.cross_cov(X2, X2, ww), own2(f"band_{b}"),
           f"K1 16 band {b}: the products give S1's block (1e-10)", f"K1 2D band {b}: the products give S5_R's block (1e-10)")
        if own_only:
            continue
        if v1["bands_pass"].get(b):
            crosses[f"band:{b}"] = X.cross_cov(X16, X2, ww)
        else:
            bounded[f"band:{b}"] = X.bound_matrix(own16(f"C_band_{b}"), own2(f"band_{b}"))
    flux5 = np.asarray(np.load(io.BytesIO((a.run_dir / "inputs" / X.NPZ_NAME).read_bytes()), allow_pickle=False)["flux"], float)
    scale = sa.x01_scale(stage(inp, X01, sroot), flux5)
    pti, ipt2 = sa.pt_index(), cells2d // (len(e_pz) - 1)
    for b in LATERAL_BANDS:
        X16, X2 = [], []
        for i in (0, 1):
            p5 = S1DIR / f"lat_{b}_{i}_b-_j-.npz"
            committed_sha(p5, s1meta[p5.name], "S1 lateral")
            X16.append(A @ (U @ (sa.xs(p5) * (scale[i][pti] if b == sa.MINOS else 1.0))))
            v = vec2(RE2 / f"partb/out/S3_{b.replace('_', '')}{i}/xsec.root")
            X2.append(B @ (v * (scale[i][ipt2] if b == sa.MINOS else 1.0)))
        X16, X2 = np.array(X16), np.array(X2)
        k1(f"lateral {b}", X.cross_cov(X16, X16), own16(f"C_lat_{b}"), X.cross_cov(X2, X2), own2(f"band_{b}"),
           f"K1 16 lateral {b} (1e-10)", f"K1 2D lateral {b} (1e-10)")
        if not own_only:
            crosses[f"lat:{b}"] = X.cross_cov(X16, X2)
    n16, n2 = X.NORM * (A @ f), X.NORM * (B @ x)
    check("K1 16 normalization (1e-10)", X.same_block(np.outer(n16, n16), own16("C_normalization")))
    check("K1 2D normalization (1e-10)", X.same_block(np.outer(n2, n2), own2("band___Normalization_flat")))
    if not own_only:
        crosses["normalization"] = np.outer(n16, n2)
    per, plj = json.loads(read_committed(PERIODS5)), json.loads(read_committed(PL_JSON))
    k16, k2 = float(per["constants"]["k"]), float(plj["report"]["k_factor"])
    V16p, V2p = [], []
    for P_ in ("PA", "PB", "PC"):
        g16 = np.asarray(per["g_vs_5A"]["periods"][P_]["g_5b"], float)
        V16p.append(np.sqrt(k16 * float(per["constants"]["exposure_share"][P_])) * (A @ (f * g16)))
        V2p.append(np.sqrt(k2) * (B @ (np.sqrt(np.asarray(pl[f"e_{P_}"], float)) * x * np.asarray(pl[f"g_{P_}"], float))))
    check("K1 C_PL5D from its periods (1e-10)", X.same_block(sum(np.outer(v, v) for v in V16p),
                                                        A @ np.asarray(blk["C_PL5D"], float) @ A.T))
    check("K1 C_PL_R from its periods (1e-10)", X.same_block(sum(np.outer(v, v) for v in V2p),
                                                        B @ np.asarray(pl["C_PL"], float) @ B.T))
    if not own_only:
        crosses["C_PL (constructed, period-paired)"] = X.outer_pairs(V16p, V2p)
    cm5 = json.loads(read_committed(CMODEL5))
    check("K0 the C_model vertices are paired in one order", list(cm5["vertices"]) == list(cm2["vertices"]))
    V16m = [A @ (f * np.asarray(s_, float)) for s_ in cm5["S"]]
    check("K1 C_model_abs from its vertices (1e-10)", X.same_block(sum(np.outer(v, v) for v in V16m),
                                                              A @ np.asarray(dp["matrices"]["C_model_abs"], float) @ A.T))
    S16stat, S2stat = own16("C_stat"), own2("stat")
    if own_only:
        return {**k_own_tail(a, check, v0, bs, A, U, C16q, C2q, S16stat, S2stat, vec2), "k1_null_bands": nulls}
    crosses["C_model (vertex-paired)"] = X.outer_pairs(V16m, V2m)
    # the statistical stream (ruling 1): route B iff V0 and B0 held, every paired replica exists, and K2 holds for it
    route, stat, why = "A", None, []
    if v0["pass"] and bs["b0"]:
        prods = {}
        for p in sorted((a.run_dir / "boot" / "xcov").glob("lane_*.json")):
            prods.update(json.loads(p.read_text())["products"])
        want = [f"xcov_b{b}_j{100 + b}.npz" for b in X.STAT_REPLICAS]
        if all(n in prods for n in want):
            for n in want:
                committed_sha(a.run_dir / "boot" / "xcov" / n, prods[n], "paired replica")
            S16r = np.array([A @ (U @ sa.xs(a.run_dir / "boot" / "xcov" / n)) for n in want])
            S2r = np.array([B @ vec2(RE2 / f"partb/out/S1_{b:03d}/xsec.root") for b in X.STAT_REPLICAS])
            stat = X.stat_cross(S16r, S2r, np.sqrt(np.diag(S16stat)), np.sqrt(np.diag(S2stat)))
            if X.joint_psd(S16stat, S2stat, stat["K"]):
                route = "B"
                crosses["stat (paired replicas)"] = stat["K"]
            else:
                why.append("K2 failed for the statistical block: falls back to route A")
        else:
            why.append("paired replicas missing")
    else:
        why.append("V0 failed" if not v0["pass"] else "B0 failed")
    K = sum(crosses.values())
    check("K2 the joint matrix of the paired blocks is PSD", X.joint_psd(C16q, C2q, K))
    M = sum(bounded.values(), np.zeros((X.N_Q, X.N_Q)))
    if route == "A":
        M = M + X.bound_matrix(S16stat, S2stat)
    blocks16 = {"C_total + C_resp + C_PL,5D": C16q - box_var, "unreported boxes": box_var}
    blocks2 = {"Q_R": Q2q, "C_model,2D": M2q}

    def evaluate(C2, Kx, label, primary=False):
        try:
            if not M.any():
                Vd = X.Vd_of(C16q, C2, Kx)
                r = {"label": label, "route": "B", **X.verdict(d, Vd), "Vd": Vd.tolist()}
                if stat is not None and route == "B":
                    r["information_R_plus_minus_SE"] = X.r_band(d, C16q, C2, Kx - stat["K"], stat["R"],
                                                                stat["rho_diag_jackknife_se"], np.sqrt(np.diag(S16stat)),
                                                                np.sqrt(np.diag(S2stat)))
                return r
            return {"label": label, "route": "A" if route == "A" else "B, with bands bounded",
                    **X.route_a(d, C16q, C2, Kx, M)}
        except X.Stop as e:
            if primary:
                raise
            return {"label": label, "stop": str(e)}

    primary = evaluate(C2q, K, "primary: the reported sixteen-cell matrix against Q_R + C_model,2D (vertex-paired)", True)
    alone = evaluate(Q2q, K - crosses["C_model (vertex-paired)"], "printed: against Q_R alone (C_model,16 unpaired)")
    nopl = evaluate(C2q, K - crosses["C_PL (constructed, period-paired)"], "sensitivity: the C_PL pair set to 0")
    sh = {"r0": X.shares(blocks16, blocks2, crosses, X.Vd_of(C16q, C2q, K))}
    if M.any():
        sh["r1"] = X.shares(blocks16, blocks2, {**crosses, "bounded (r = 1)": M}, X.Vd_of(C16q, C2q, K + M))
    rho = {f"r{r_:g}": {q: float((K + r_ * M)[i, i] / np.sqrt(C16q[i, i] * C2q[i, i])) for i, q in enumerate(X.QNAMES)}
           for r_ in ((0.0, 1.0) if M.any() else (0.0,))}
    return {"route": route, "route_reasons": why, "k1_null_bands": nulls, "d": d.tolist(), "S16": S16.tolist(), "S2D": S2.tolist(),
            "rho_q": rho, "primary": primary, "Q_R_alone": alone, "C_PL_pair_zero": nopl, "shares": sh,
            "crosses": {k: v.tolist() for k, v in crosses.items()}, "bounded": sorted(bounded),
            "own": {"C16q": C16q.tolist(), "C2q": C2q.tolist(), "Q2q": Q2q.tolist(), "M2q": M2q.tolist()},
            "stat": None if stat is None else {k: np.asarray(v).tolist() for k, v in stat.items()},
            "rule": "agree iff joint chi2_4 p >= 0.05 and every |z| <= 2.50; a quadrant over 2.50 is a named differ, "
                    "and so is a joint p < 0.05 with no quadrant over (the director's ruling 3)"}

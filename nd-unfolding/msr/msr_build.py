#!/usr/bin/env python3
"""MSR (response measurability), the cluster step: build the binned responses the declaration names, and nothing else.

Declaration: ``docs/orchestration/state/measurability-20261122/DECLARATION.md`` (rev 2, sha256 a3f35ed5...). Every
construction here is committed code called unchanged (pinned in PINS and checked first); this file only captures what
that code builds, before any IBU iteration, and writes it. No data, pseudo-data or unfold enters: the 5D capture stops
where ``ibu1.unfold_ibu`` calls ``did.ibu``; the 2D one bins IBUKT's bank with ``ref_c2c1.binned_problem`` and a dummy
measured array (its y is discarded).

    msr_build.py stat PATH...                      stat (size, mtime, atime, inode) and O_NOATIME sha256, one JSON per line
    msr_build.py did-cons --side {did,ibu1} --npz F --bkg F --out DIR
                                                   C-DID-CONS: the J-cell definitions and occupied reco cells by one side
    msr_build.py probe --npz F --bkg F --bank F --out DIR --fraction 0.02
                                                   a timed build on a row subsample (wall and peak RSS printed by the caller)
    msr_build.py build --npz F --bkg F --bank F --t3-run DIR --t3-stage-json F --out DIR
                                                   the declared products (section 8), one npz each, then SHA256SUMS

MEASURES: binned responses, priors, known terms, background templates and maps. CANNOT AUTHORIZE: a reading
(``msr_project.py`` applies the declared ones, locally) or any claim.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import resource
import sys
import time
from pathlib import Path

import numpy as np
from scipy import sparse

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ND = REPO / "nd-unfolding"
DID_DIR = REPO / "docs/orchestration/state/next-preparation-20261009/d-id"
for _p in (ND / "prior_retention", ND / "ref_g1", ND / "ibu1", ND / "pv-ladder", ND / "tier3", ND, DID_DIR,
           REPO / "2d-unfolding" / "ibukt", REPO / "2d-unfolding" / "ref_c2c1", REPO / "2d-unfolding"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

PINS = {  # declaration section 2, full sha256
    "docs/orchestration/state/next-preparation-20261009/d-id/did.py": "d918c816080a292eecaa0cc182a73906b868bb75189056862cf88d7152c4bbbd",
    "nd-unfolding/prior_retention/prr_ibu.py": "fa91394507c0e6a32486af25fa52f7e162135cf6483519ccf15510e1c9473cb0",
    "nd-unfolding/prior_retention/prr_read.py": "d7c7c2c0d6cbe4a13d445a779335699de3d5275c4bcd3efc9f4e84a166868fbe",
    "nd-unfolding/ibu1/ibu1.py": "f862a953425c006f6c73f2190bd65172eb9295f0f6c181d3d2247d4de881cf12",
    "nd-unfolding/ref_g1/ref_g1.py": "8e34c48552857f5eec55e1067f70f4d26b2a6de0eaae46c57983fd91fbc6e7b1",
    "nd-unfolding/s1_assemble.py": "b157250af21a2ef74e4164db6009a40ac596e225f33ac655475798ef49f613f7",
    "nd-unfolding/tier3/t3p_read.py": "f4c221dda95fbbdf2318f7fcdde57b9e1b7fb265e85b13e1dea15341cf069295",
    "2d-unfolding/ref_c2c1/ref_c2c1.py": "285dd138363d090a4ce5dea3361be81fada8680bd782b918e9d95198d1b5d6ea",
    "2d-unfolding/ibukt/ibukt.py": "ef8590cf6d6d025b6db1fb8fdd100f76114390ac78eded62274b2c077c290789",
    "2d-unfolding/ibukt/run_ibukt.py": "f2b4c017e1a2e84c2cb30b43a8824b95c3f7e022f5fca23b0ceac2a750c33683",
    "2d-unfolding/ibukt/config.json": "60d6c4d747596137423a869ac315c484ef65ad69f3ec209d6fd73d6e573c716c",
}
NPZ_SHA = "07fccc1abc7204bc29349b4ba96850986fe91e909e83fc54e8d1a6b3922a649f"
BANK_SHA = "60416384474d1a3b0644f1e09869cf09371382ecbf3c116b1ed110cd47341e2f"
PRIMARY_SEED = 991000          # FD-PRR's primary split (section 5.3, C-RID)
SPLIT2D_KEY = 20261122         # the 2D halves (section 5.3)
T3_ARMS = ("B0", "MO", "OP")
T3_CELLS = (("A7_gibuu", (991000, 994001, 994002, 994003, 994004)), ("q3", (991000,)))
T3_KS = {"B0": (5, 50), "MO": (5, 50), "OP": (2,)}  # OP runs 2 iterations (t3p_arms.ITERS["OP"]); declaration rev 3


class Refused(RuntimeError):
    pass


# ------------------------------------------------------------------------------------------- reads
def noatime_sha256(path: Path, chunk: int = 1 << 24) -> str:
    """sha256 of a file read with O_NOATIME (the standing read rule); refuses if the flag is unavailable."""
    flag = getattr(os, "O_NOATIME", 0)
    if not flag:
        raise Refused("O_NOATIME is not available on this platform")
    h = hashlib.sha256()
    fd = os.open(path, os.O_RDONLY | flag)
    try:
        while True:
            b = os.read(fd, chunk)
            if not b:
                break
            h.update(b)
    finally:
        os.close(fd)
    return h.hexdigest()


def noatime_bytes(path: Path) -> bytes:
    flag = getattr(os, "O_NOATIME", 0)
    if not flag:
        raise Refused("O_NOATIME is not available on this platform")
    fd = os.open(path, os.O_RDONLY | flag)
    try:
        chunks = []
        while True:
            b = os.read(fd, 1 << 24)
            if not b:
                return b"".join(chunks)
            chunks.append(b)
    finally:
        os.close(fd)


def noatime_copy(src: Path, dest: Path, pin: str) -> Path:
    """Copy an original with O_NOATIME into this build's own stage; refuse unless the copy is at ``pin``."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        raise Refused(f"{dest} exists")
    dest.write_bytes(noatime_bytes(src))
    if plain_sha256(dest) != pin:
        raise Refused(f"C-OPS: the copy of {src} is not at {pin}")
    return dest


def plain_sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check_pins() -> None:
    """C-OPS (code): every reused file at its declared sha256."""
    bad = [p for p, s in PINS.items() if plain_sha256(REPO / p) != s]
    if bad:
        raise Refused(f"C-OPS: not at the declared sha256: {bad}")


def stat_line(path: Path) -> dict:
    st = os.stat(path)
    return {"path": str(path), "size": st.st_size, "mtime": st.st_mtime, "atime": st.st_atime, "inode": st.st_ino,
            "sha256": noatime_sha256(path) if Path(path).is_file() else None}


def peak_rss_bytes() -> int:
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(rss if sys.platform == "darwin" else rss * 1024)


# ------------------------------------------------------------------------------------------- 5D
class _Captured(Exception):
    pass


def capture_problem(did, world, half, b_extra: np.ndarray) -> dict:
    """``ibu1.unfold_ibu``'s own construction, stopped where it calls ``did.ibu``: the response, the summed known term,
    the prior, the grid and the fine truth shape. y is zeros and never used (no iteration runs)."""
    import ibu1
    seen: dict = {}
    real_ibu, real_grid = did.ibu, did.make_grid

    def ibu(r, y, b, prior, n_iter, **kw):
        seen.update(R=r.tocsr(), b=np.asarray(b, float), prior=np.asarray(prior, float))
        raise _Captured()

    def make_grid(name, coarse_of, n_coarse, u_nominal):
        g = real_grid(name, coarse_of, n_coarse, u_nominal)
        seen.update(grid=g, u_fine=np.asarray(u_nominal, float))
        return g

    did.ibu, did.make_grid = ibu, make_grid
    try:
        ibu1.unfold_ibu(world, half, np.zeros(world.n_fine), np.asarray(b_extra, float), [1])
    except _Captured:
        pass
    finally:
        did.ibu, did.make_grid = real_ibu, real_grid
    if "R" not in seen:
        raise Refused("the capture never reached did.ibu")
    seen["b_extra"] = np.asarray(b_extra, float)
    seen["b_known"] = seen["b"] - seen["b_extra"]
    return seen


def reported_map(did, ibu1, world, cap: dict) -> np.ndarray:
    """L (n_functionals x n_cells): column j = ``ibu1.extract`` of cell j's unit count spread by the prior shape
    (declaration 3.1). ``extract`` returns ``world.functionals`` of the cross section, so L is in FD-PRR's units."""
    grid, u = cap["grid"], cap["u_fine"]
    share = did.share_matrix(grid, u).tocsc()
    cols = []
    for j in range(grid.n_cells):
        cols.append(ibu1.extract(world, np.asarray(share[:, j].todense()).ravel(), u))
    return np.column_stack(cols)


def bkg_template(world, s5n, bkg: dict, rows=None, scale: float = 1.0) -> np.ndarray:
    reco = np.asarray(bkg["bkg_reco"])
    w = np.asarray(bkg["bkg_w"], float)
    if rows is not None:
        reco, w = reco[rows], w[rows]
    keep = s5n.fid_mask(reco, world.edges)
    return world.reco_hist(reco[keep], scale * w[keep])


def problem_arrays(prefix: str, cap: dict, L: np.ndarray | None) -> dict:
    R = cap["R"]
    out = {f"{prefix}__R_data": R.data, f"{prefix}__R_indices": R.indices, f"{prefix}__R_indptr": R.indptr,
           f"{prefix}__R_shape": np.array(R.shape), f"{prefix}__b_known": cap["b_known"],
           f"{prefix}__b_extra": cap["b_extra"], f"{prefix}__prior": cap["prior"], f"{prefix}__u_fine": cap["u_fine"],
           f"{prefix}__cell_of_fine": cap["grid"].cell_of_fine, f"{prefix}__n_cells": np.array(cap["grid"].n_cells)}
    if L is not None:
        out[f"{prefix}__L"] = L
        out[f"{prefix}__L_t0"] = L @ cap["prior"]
    return out


MC_KEYS = ("MCgen", "MCreco", "pass_reco", "pass_truth", "w_truth", "w_reco")
DATA_KEYS = ("measured", "measured_weights")  # never loaded (declaration section 0; D-ID's REAL_DATA_KEYS likewise)
OTHER_KEYS = ("denom_nd", "flux", "data_pot", "n_nucleons", "nedges")


def load_inputs_nodata(npz: Path, bkg_path: Path, pins: dict | None) -> tuple[dict, dict]:
    """``ibu1.load_inputs`` with its own digest checks (when ``pins`` is given) and the same keys as
    ``s5c_unfold.load_inputs``, except the two data keys, which are never read. test_msr_build checks that every
    returned array equals the pinned loader's."""
    import ibu1
    if pins is not None:
        if ibu1.sha256(npz) != pins["of_inputs_5d_sha256"]:
            raise Refused("of_inputs_5d.npz digest differs from IBU-1's config.json")
        if ibu1.sha256(bkg_path) != pins["bkg_dump_sha256"]:
            raise Refused("bkg_dump.npz digest differs from IBU-1's config.json")
    d = np.load(npz, allow_pickle=True)
    inputs = {k: d[k] for k in MC_KEYS + OTHER_KEYS}
    inputs["edges"] = [np.asarray(d[f"edges_{i}"], float) for i in range(int(d["nedges"]))]
    bz = np.load(bkg_path, allow_pickle=True)
    if pins is not None and json.loads(str(bz["meta"]))["npz_sha256"] != pins["of_inputs_5d_sha256"]:
        raise Refused("background dump was made against a different npz")
    return inputs, {"bkg_reco": bz["bkg_reco"], "bkg_w": bz["bkg_w"], "bkg_nd": bz["bkg_nd"]}


def setup_5d(npz: Path, bkg_path: Path, probe: bool = False):
    import ref_g1
    import s5n_pseudo
    cfg = json.loads(ref_g1.CONFIG.read_text())
    lib = ref_g1.Lib(cfg)
    icfg = lib.ibu1_cfg
    contract = json.loads((REPO / icfg["contract"]["path"]).read_text())
    # the probe reads a row subsample written by `subsample` (timing only), so it carries no pins
    inputs, bkg = load_inputs_nodata(npz, bkg_path, None if probe else icfg["inputs"])
    jw, gw = ref_g1.worlds(lib, cfg, inputs, contract)
    return lib, inputs, bkg, jw, gw, s5n_pseudo


def build_5d(npz: Path, bkg_path: Path, probe: bool = False) -> tuple[dict, dict]:
    import ibu1
    import ref_g1
    import s5c_pseudo
    lib, inputs, bkg, jw, gw, s5n = setup_5d(npz, bkg_path, probe)
    did = lib.prod.did
    n = inputs["MCgen"].shape[0]
    wt, wr = np.asarray(inputs["w_truth"], float), np.asarray(inputs["w_reco"], float)
    full_bkg = bkg_template(gw, s5n, bkg)
    arrays, rec = {}, {"world_shape": list(gw.shape), "axes": ["pt", "pz", "eavail", "q3", "W"],
                       "edges": [np.asarray(e, float).tolist() for e in gw.edges], "n_rows": int(n)}
    # the reading: the full MC at x1 with the full template (3.1, 3.2)
    cap = capture_problem(did, gw, ref_g1.full_half(n, wt, wr), full_bkg)
    L = reported_map(did, ibu1, gw, cap)
    arrays.update(problem_arrays("h2_full", cap, L))
    lin = ibu1.extract(gw, did.share_matrix(cap["grid"], cap["u_fine"]) @ cap["prior"], cap["u_fine"])
    rec["C-L_linearity_rel"] = float(np.max(np.abs(L @ cap["prior"] - lin) / np.maximum(np.abs(lin), 1e-300)))
    arrays["gw_U"] = np.asarray(gw.U.todense() if sparse.issparse(gw.U) else gw.U)
    # the halves of the signal MC at x2, same full template (5.3)
    split = s5c_pseudo.split_key_for(PRIMARY_SEED)
    is_b = s5c_pseudo.half_mask(n, split)
    for name, rows_h in (("A", np.flatnonzero(~is_b)), ("B", np.flatnonzero(is_b))):
        half = ibu1.Half(rows_h, 2.0 * wt[rows_h], 2.0 * wr[rows_h])
        cap_h = capture_problem(did, gw, half, full_bkg)
        arrays.update(problem_arrays(f"h2_half{name}", cap_h, reported_map(did, ibu1, gw, cap_h)))
    # R-ID's own settings: half A x2 with that experiment's template D x2 (C-RID; FD-PRR section 3.4)
    nb = np.asarray(bkg["bkg_w"]).shape[0]
    is_c = s5c_pseudo.half_mask(nb, s5n.bkg_split_key(split))
    rows_a = np.flatnonzero(~is_b)
    cap_r = capture_problem(did, gw, ibu1.Half(rows_a, 2.0 * wt[rows_a], 2.0 * wr[rows_a]),
                            bkg_template(gw, s5n, bkg, rows=~is_c, scale=2.0))
    import prr_ibu
    rid = prr_ibu.r_id(did, gw.U, [{"grid": cap_r["grid"], "u_fine": cap_r["u_fine"]},
                                   {"R": cap_r["R"], "b": cap_r["b"], "prior": cap_r["prior"]}])
    rec["R-ID_rebuilt"] = rid
    arrays.update(problem_arrays("h2_rid", cap_r, None))
    # D-ID's settings at T1 (C-DID): the J world, full MC x1, known term only, and D-ID's functional maps
    cap_t1 = capture_problem(did, jw, ref_g1.full_half(n, wt, wr), np.zeros(jw.n_fine))
    # kappa (cross section per unit count) as D-ID's build_rows computes it, from this world's own completeness
    dn = np.asarray(inputs["denom_nd"], float).ravel()
    comp = np.zeros(jw.n_fine)
    comp[dn > 0] = cap_t1["u_fine"][dn > 0] / dn[dn > 0]
    kap, _ = lib.prod.xsec_nd.extract_cross_section_nd(np.ones(jw.shape), comp.reshape(jw.shape), inputs["flux"],
                                                       float(inputs["data_pot"]), float(inputs["n_nucleons"]), jw.edges)
    U = sparse.csr_matrix(jw.U)
    maps_t1 = did.functional_matrix((U @ sparse.diags(np.asarray(kap).ravel(order="C"))).tocsr(), cap_t1["grid"],
                                    cap_t1["u_fine"])
    arrays.update(problem_arrays("t1_did", cap_t1, None))
    arrays["t1_did__maps"] = np.asarray(maps_t1)
    rec["t1_names"] = list(jw.names)
    rec["n_cells"] = {"h2": int(cap["grid"].n_cells), "t1": int(cap_t1["grid"].n_cells),
                      "h2_rid": int(cap_r["grid"].n_cells),
                      "h2_nonempty_coarse": int(np.unique(np.asarray(gw.coarse_of)[cap["u_fine"] > 0]).size)}
    return arrays, rec


# ------------------------------------------------------------------------------------------- 2D
def build_2d(bank_path: Path, probe: bool = False) -> tuple[dict, dict]:
    import ibukt as core
    import ref_c2c1
    import s5c_pseudo
    cfg = json.loads((REPO / "2d-unfolding/ibukt/config.json").read_text())
    pt_e, pz_e = cfg["pt_edges"], cfg["pz_edges"]
    with np.load(bank_path, allow_pickle=False) as z:
        bank = {k: z[k] for k in z.files}
    gen, reco, pr, pt = bank["gen"], bank["reco"], bank["pr"].astype(bool), bank["pt"].astype(bool)
    wt, wr = bank["wt"].astype(float), bank["wr"].astype(float)
    if np.any(pr & ~pt):
        raise Refused("C-2D: a signal fake (pr and not pt), as run_ibukt.py:360 refuses")
    n = gen.shape[0]
    sel = np.arange(n)
    bkg, bw = bank["bkg"], bank["bw"].astype(float)
    b_bkg = core.histogram(bkg[:, 0], bkg[:, 1], bw, cfg)
    gi = ref_c2c1.global_index(bkg[:, 0], bkg[:, 1], pt_e, pz_e)
    b_bkg_2 = np.bincount(gi[gi >= 0], weights=bw[gi >= 0], minlength=b_bkg.size)
    # the bank's `selected` is the 205 paper cell ids (run_ibukt.py:237-239, :402), an integer index array
    ids = np.asarray(bank["selected"], np.int64).ravel()
    if ids.size != 205 or ids.min() < 0 or ids.max() >= b_bkg.size or np.unique(ids).size != ids.size:
        raise Refused(f"C-L: the bank's selected is not 205 distinct cell ids in 0..{b_bkg.size - 1}")
    mask = np.zeros(b_bkg.size, bool)
    mask[ids] = True
    arrays, rec = {}, {"pt_edges": pt_e, "pz_edges": pz_e, "factor": np.asarray(bank["factor"]).tolist(),
                       "selected_ids": ids.tolist()}

    def one(name, idx, scale):
        T, M, _y, t = ref_c2c1.binned_problem(gen[idx], reco[idx], bkg, pr[idx], pt[idx], scale * wt[idx],
                                              scale * wr[idx], bw, pt_e, pz_e)
        r = ref_c2c1.global_index(reco[idx][:, 0], reco[idx][:, 1], pt_e, pz_e)
        kn = pt[idx] & pr[idx] & (t < 0) & (r >= 0)
        b_known = np.bincount(r[kn], weights=scale * wr[idx][kn], minlength=T.size)
        # the second construction (C-2D): IBUKT's own cell map on the truth and reco coordinates
        tc = core.cells(gen[idx][:, 0], gen[idx][:, 1], cfg)
        rc = core.cells(reco[idx][:, 0], reco[idx][:, 1], cfg)
        kn2 = pt[idx] & pr[idx] & (tc < 0) & (rc >= 0)
        b_known_2 = np.bincount(rc[kn2], weights=scale * wr[idx][kn2], minlength=T.size)
        arrays.update({f"d2_{name}__T": T, f"d2_{name}__M": M, f"d2_{name}__b_known": b_known,
                       f"d2_{name}__b_known_ibukt": b_known_2})

    one("full", sel, 1.0)
    is_b = s5c_pseudo.half_mask(n, SPLIT2D_KEY)
    one("halfA", np.flatnonzero(~is_b), 2.0)   # also on the probe, so its timing covers the halves
    one("halfB", np.flatnonzero(is_b), 2.0)
    arrays["d2__b_bkg"] = b_bkg
    arrays["d2__b_bkg_globalindex"] = b_bkg_2
    arrays["d2__truth_nominal"] = np.asarray(bank["truth_nominal"], float) if "truth_nominal" in bank else np.full(224, np.nan)
    arrays["d2__factor"] = np.asarray(bank["factor"], float) * np.ones(224)
    arrays["d2__selected_ids"] = ids
    arrays["d2__selected_mask"] = mask
    if not probe:  # a subsample's M cannot match the full bank, so C-2D runs on the full build only
        R = np.divide(arrays["d2_full__M"], arrays["d2_full__T"][None, :],
                      out=np.zeros_like(arrays["d2_full__M"]), where=arrays["d2_full__T"][None, :] > 0)
        bank_R = np.asarray(bank["ibu_response"], float)
        rec["C-2D"] = {"M_vs_bank_ibu_response_max_abs": float(np.max(np.abs(arrays["d2_full__M"] - bank_R))),
                       "R_vs_bank_ibu_response_max_abs": float(np.max(np.abs(R - bank_R))),
                       "T_vs_bank_ibu_prior_max_rel": float(np.max(np.abs(arrays["d2_full__T"] - bank["ibu_prior"])
                                                                   / np.maximum(np.abs(bank["ibu_prior"]), 1e-300))),
                       "sum_b_bkg": float(b_bkg.sum()), "sum_bw_in_window": float(
                           bw[ref_c2c1.global_index(bkg[:, 0], bkg[:, 1], pt_e, pz_e) >= 0].sum())}
        arrays["d2__bank_ibu_response"] = bank_R
        arrays["d2__bank_ibu_prior"] = np.asarray(bank["ibu_prior"], float)
    return arrays, rec


# ------------------------------------------------------------------------------------------- T3 bias vectors
def t3_vectors(run: Path, stage_json: Path, stage: Path) -> tuple[dict, dict]:
    """b_c = (X_hat_k - X)/P at k in T3_KS, exactly as ``t3p_read.quantities`` forms it, for B0, MO and OP. Every
    original under T3's run root is read with O_NOATIME: SHA256SUMS and stage.json directly, and each product and each
    FD-PRR nominal copy through ``noatime_copy`` into ``stage`` (this build's own), which is all that is then loaded."""
    import estimator_stability_analyze as an
    import t3p_probe as T
    import t3p_read as TR
    M16 = an.cell_matrix(str(REPO / "nd-unfolding/pv-ladder/readouts/h2_definition.json"))
    sums = {}
    for line in noatime_bytes(run / "log-floor/SHA256SUMS").decode().splitlines():
        h, p = line.split("  ", 1)
        sums[p] = h
    stage_rec = json.loads(noatime_bytes(stage_json).decode())
    want = {f"prr_B0_{T.PRIOR}_s{s}" for s in (T.PRIMARY_SEED, *T.FLOOR_SEEDS)}
    files = []
    for e in stage_rec["files"]:
        if e["role"] in want:
            e = dict(e, copy=str(noatime_copy(Path(e["copy"]), stage / "fd-prr" / Path(e["copy"]).name, e["sha256"])))
        files.append(e)
    Pr = TR.priors(dict(stage_rec, files=files), M16)
    arrays, rec = {"M16": np.asarray(M16, float)}, {"products": {}}
    for truth, seeds in T3_CELLS:
        for s in seeds:
            arrays[f"t3__P__s{s}"] = Pr[s]
            for arm in T3_ARMS:
                path = T.product_path(run / "runs", arm, truth, s)
                rel = str(path.relative_to(run))
                if rel not in sums:
                    raise Refused(f"C-OPS: {rel} is not in log-floor/SHA256SUMS")
                copy = noatime_copy(path, stage / "t3" / rel, sums[rel])
                got = sums[rel]
                a, _meta = TR.load(copy)
                X = M16 @ a["xtrue_flat"].astype(float)
                for k in T3_KS[arm]:
                    if k > a["X16_push"].shape[0]:
                        raise Refused(f"{rel}: k = {k} beyond its {a['X16_push'].shape[0]} iterations")
                    arrays[f"t3__b__{arm}__{truth}__s{s}__k{k}"] = (a["X16_push"][k - 1] - X) / Pr[s]
                arrays[f"t3__X__{arm}__{truth}__s{s}"] = X
                rec["products"][rel] = {"sha256": got, "iterations": int(a["X16_push"].shape[0])}
    return arrays, rec


# ------------------------------------------------------------------------------------------- C-DID-CONS
def did_cons(side: str, npz: Path, bkg_path: Path, out: Path) -> dict:
    """Four sorted lists (declaration section 1): the J-cell fine memberships and the occupied reco cells, by one side."""
    out.mkdir(parents=True, exist_ok=False)
    if side == "ibu1":
        lib, inputs, bkg, jw, gw, s5n = setup_5d(npz, bkg_path)
        did = lib.prod.did
        u = np.bincount(jw.tflat[jw.tflat >= 0], weights=np.asarray(inputs["w_truth"], float)[jw.tflat >= 0],
                        minlength=jw.n_fine)
        grid = did.make_grid("J", jw.coarse_of, jw.n_coarse, u)
        ok = jw.rflat >= 0
        y = np.bincount(jw.rflat[ok], weights=np.asarray(inputs["w_reco"], float)[ok], minlength=jw.n_fine)
        cell_of_fine, reco = grid.cell_of_fine, np.flatnonzero(y > 0)
    else:
        import did as D
        cfg = json.loads(D.CONFIG.read_text())
        idir = out / "inputs" / "nd-unfolding"
        idir.mkdir(parents=True)
        os.symlink(npz, idir / "of_inputs_5d.npz")
        diag = D.Diagnostic(cfg, out / "inputs", out / "did-out", D.Budget(1e9),
                            D.load_comparator(cfg["code"]["comparator.py"]), D.load_committed(cfg["code"]["nd-unfolding"]))
        # D-ID's own stage-1 steps that build the event geometry and the grids (stage1 without the comparators,
        # whose committed products this connect does not read); an admission failure propagates (non-zero exit)
        diag.load_events()
        diag.build_rows()
        diag.histograms()
        diag.grids()
        cell_of_fine, reco = diag.G["T1"].cell_of_fine, diag.reco_cells
    members = [" ".join(map(str, np.flatnonzero(cell_of_fine == c))) for c in range(int(cell_of_fine.max()) + 1)]
    lists = {"j_cells": "\n".join(sorted(members)) + "\n", "reco_cells": "\n".join(map(str, sorted(reco.tolist()))) + "\n"}
    rec = {"side": side}
    for name, text in lists.items():
        (out / f"{side}_{name}.txt").write_text(text)
        rec[name] = {"sha256": hashlib.sha256(text.encode()).hexdigest(), "n": text.count("\n")}
    return rec


# ------------------------------------------------------------------------------------------- probe inputs
def npz_rows(path: Path, key: str) -> int:
    """The row count of one array in an npz, from its .npy header only (no array is read)."""
    import zipfile
    with zipfile.ZipFile(path) as z, z.open(f"{key}.npy") as f:
        version = np.lib.format.read_magic(f)
        shape, _, _ = np.lib.format._read_array_header(f, version)
    return int(shape[0])


def subsample(part: str, src: Path, fraction: float, out: Path) -> dict:
    """Write a row subsample of the 5D inputs (MC keys only; the data keys are not read) or of the 2D bank, for the
    probe's timing. Run in its own process, so the probe process never holds the full arrays (Grok's read, item 3)."""
    if out.exists():
        raise Refused(f"{out} exists")
    out.parent.mkdir(parents=True, exist_ok=False)
    rng = np.random.default_rng(7)
    if part == "5d":
        n = npz_rows(src, "MCgen")
        keep = np.flatnonzero(rng.random(n) < fraction)
        d = np.load(src, allow_pickle=True)
        arrays = {k: d[k][keep] for k in MC_KEYS}
        arrays.update({k: d[k] for k in OTHER_KEYS})
        arrays.update({f"edges_{i}": d[f"edges_{i}"] for i in range(int(d["nedges"]))})
    else:
        with np.load(src, allow_pickle=False) as z:
            bank = {k: z[k] for k in z.files}
        n = bank["gen"].shape[0]
        keep = np.flatnonzero(rng.random(n) < fraction)
        arrays = {k: (v[keep] if k in ("gen", "reco", "pr", "pt", "wt", "wr") else v) for k, v in bank.items()}
    np.savez(out, **arrays)
    return {"part": part, "rows": int(n), "kept": int(keep.size), "fraction": fraction}


# ------------------------------------------------------------------------------------------- write
def write_npz(path: Path, arrays: dict) -> str:
    if path.exists():
        raise Refused(f"{path} exists")
    np.savez(path, **arrays)
    return plain_sha256(path)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("stat")
    s.add_argument("paths", nargs="+", type=Path)
    ss = sub.add_parser("subsample")
    ss.add_argument("--part", choices=("5d", "2d"), required=True)
    ss.add_argument("--src", type=Path, required=True)
    ss.add_argument("--fraction", type=float, required=True)
    ss.add_argument("--out", type=Path, required=True)
    c = sub.add_parser("did-cons")
    c.add_argument("--side", choices=("did", "ibu1"), required=True)
    for p in (c,):
        p.add_argument("--npz", type=Path, required=True)
        p.add_argument("--bkg", type=Path, required=True)
        p.add_argument("--out", type=Path, required=True)
    for name in ("probe", "build"):
        p = sub.add_parser(name)
        p.add_argument("--npz", type=Path, required=True)
        p.add_argument("--bkg", type=Path, required=True)
        p.add_argument("--bank", type=Path, required=True)
        p.add_argument("--out", type=Path, required=True)
        if name == "probe":
            p.add_argument("--fraction", type=float, required=True)
            p.add_argument("--part", choices=("5d", "2d"), required=True)
        else:
            p.add_argument("--t3-run", type=Path, required=True)
            p.add_argument("--t3-stage-json", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.cmd == "stat":
        for p in a.paths:
            print(json.dumps(stat_line(p)))
        return 0
    check_pins()
    if a.cmd == "subsample":
        print(json.dumps(subsample(a.part, a.src, a.fraction, a.out)))
        return 0
    if a.cmd == "did-cons":
        print(json.dumps(did_cons(a.side, a.npz, a.bkg, a.out)))
        return 0
    a.out.mkdir(parents=True, exist_ok=False)
    t0 = time.time()
    if a.cmd == "probe":  # --npz / --bank are the subsample files `subsample` wrote
        if a.part == "5d":
            arrays, rec = build_5d(a.npz, a.bkg, probe=True)
        else:
            arrays, rec = build_2d(a.bank, probe=True)
        rec.update(part=a.part, fraction=a.fraction, seconds=round(time.time() - t0, 1), peak_rss_bytes=peak_rss_bytes())
        print(json.dumps({k: rec[k] for k in ("part", "fraction", "seconds", "peak_rss_bytes")}))
        return 0
    if noatime_sha256(a.npz) != NPZ_SHA or noatime_sha256(a.bank) != BANK_SHA:
        raise Refused("C-OPS: an input is not at its declared sha256")
    sums, record = [], {"schema": "msr-build/1", "code_pins": PINS}
    for name, fn in (("r5d", lambda: build_5d(a.npz, a.bkg)), ("r2d", lambda: build_2d(a.bank)),
                     ("t3", lambda: t3_vectors(a.t3_run, a.t3_stage_json, a.out / "stage-t3"))):
        ts = time.time()
        arrays, rec = fn()
        h = write_npz(a.out / f"{name}.npz", arrays)
        sums.append(f"{h}  {name}.npz")
        record[name] = {**rec, "seconds": round(time.time() - ts, 1), "sha256": h}
    record["peak_rss_bytes"] = peak_rss_bytes()
    record["environment"] = {k: os.environ.get(k) for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")}
    (a.out / "build.json").write_text(json.dumps(record, indent=1, default=str) + "\n")
    sums.append(f"{plain_sha256(a.out / 'build.json')}  build.json")
    (a.out / "SHA256SUMS").write_text("\n".join(sums) + "\n")
    print(json.dumps({"built": [s.split("  ")[1] for s in sums], "seconds": round(time.time() - t0, 1)}))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Refused as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        sys.exit(9)

#!/usr/bin/env python3
"""GENCMP amendment E, step E2 (FD-GENCMP-AMENDMENT-E-ADDENDUM-E2.md): #651 item 6's caveat measured. C_model's NuWro
and GiBUU vertices are rebuilt with CH shape ratios in place of carbon ones, and Stage G's chi2 of the four "CH,
analysis definitions" predictions is recomputed with that C_model, beside E-1's.

The vertex is the PV ladder's own (pv-ladder/DECLARATION.md D3): a real-data unfold of configuration (e) with the
prior reweighted by the vertex's gated shape ratio to GENIE 2.12 CV (pvl_ratios.py, pvl_unfold.py). Only the vertex's
prediction changes: GENCMP step A's CH combination in the generator definitions, x_CH = (12/13) x_C + (1/13) x_H
(the committed mp3b/mp3c products), so the reference and the definitions stay as C_model's.

Subcommands, each refusing to overwrite what it writes:

* ``stage``      (login node) O_NOATIME copies of every pscratch input into <run>/inputs/ (fd_gencmp_e.cmd_stage).
* ``vertices``   (login node) the two CH vertex files, in the gen5d form pvl_ratios reads, and config_ch.json: the
                 committed config with every pscratch path pointing at its staged copy and the two vertices at the CH
                 files. Control V: the committed step-A carbon arrays are the staged carbon vertex files bitwise, and
                 x_CH is fd_gencmp.combine of carbon and hydrogen bitwise.
* ``ratios``     (login node) pvl_ratios on config_ch.json. Control R1: the tune_v1 and genie_mec ratio files (and the
                 latter's PC fallback) hold the committed prep's numbers (r, k), every number equal.
* ``unfold``     (in the one CPU job, after its three srun steps of pvl_unfold, launched as the PV ladder launched its
                 own: NuWro CH, GiBUU CH and, as control R2, NuWro carbon with the committed prep ratio) the products'
                 digests and R2: the carbon rerun reproduces the committed L-5D-PV_e_nuwro product's xsec_flat bitwise.
* ``chi2``       (login node) S_CH from the CH vertices (GENIE+MEC's row unchanged); control C1: the carbon products
                 give cmodel_5d.json's S bitwise; control C2: diag(f) S^T S diag(f) is the data product's C_model_abs;
                 control C3: with the carbon S, each prediction's chi2 is E-1's (1e-10). Then each chi2 with S_CH and
                 Delta = chi2_CH - chi2_carbon, for the four predictions, both arms and both kinds.

MEASURES: arithmetic and three declared unfolds. CANNOT AUTHORIZE: a change to the reported covariance (binding ruling
4: no covariance changes without Joseph), a reading or paper text.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
_REPO = _ND.parent
for _p in (str(_ND), str(_ND / "pv-ladder")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import fd_cpl_addition as A  # noqa: E402  (compare_numbers, write_atomic)
import fd_g_compare as fg  # noqa: E402  (compare)
import fd_gencmp as gc  # noqa: E402  (combine, load_pins, read_noatime, NUWRO_NPZ, GIBUU_NPZ)
import fd_gencmp_e as E  # noqa: E402  (cmd_stage, write_new, Stop, report)

FD = _REPO / "docs/orchestration/state/measurement-paper/5d-community-20261024"
INPUTS = FD / "fd/gencmp-e2/INPUTS.sha256"
PVL = _ND / "pv-ladder"
CONFIG = PVL / "config.json"
CMODEL5 = PVL / "readouts/cmodel_5d.json"
CMODEL5_SHA256 = "3cfdc6a5b8c6cea5f99b4678e27f6ca5f7973ee57a79b9d139798f0751cfcd60"
SCRATCH = Path("/pscratch/sd/j/josephrb")
PRODUCTS = "pv-ladder-20261024/products"
PREP = "pv-ladder-20261024/prep/ratios/L-5D-PV"
RUNG = "L-5D-PV"
CH_VERTICES = {"nuwro": gc.NUWRO_NPZ, "gibuu": gc.GIBUU_NPZ}       # step A's committed products
E1 = FD / "fd/gencmp-e/rerun1/chain/chdefs"                          # E-1's readouts (#662)
E1_SHA256 = {"with": "a19009e0bd83b9bb8f9ad65fb65804e6f62c8953310103fbfe6fce5f84995875",
             "nopl": "d9a1ce38040b8cd3c2a6deb787f8a7dc90aca5c4d3a5a8d25a60b7f8ab582ed9"}
DP = FD / "fd/with-cpl/data-product/fd_data_product_cpl.json"
DP_SHA256 = "d6752d2c64aad4426375c03a3171a7015f031e2027928cf89aea6cd3bbb84d50"
BLOCK = FD / "fd/with-cpl/block/cpl_block.npz"
BLOCK_SHA256 = "d9aa32fdb64357760348c9ccbc32fbea81d517f0f0786eedf17ab4946eaca59f"
DELTA_FLAG = 2.3                                                     # binding ruling 4 (the disclosed GiBUU rise)
TOL = 1e-10
Stop, report = E.Stop, E.report


def sha256(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def staged(run_dir: Path, path: str | Path) -> Path:
    """The staged copy of a pscratch path."""
    return run_dir / "inputs" / Path(path).relative_to(SCRATCH)


# ---------------------------------------------------------------- vertices


def ch_arrays(carbon_gen5d: dict, stepA: dict) -> dict:
    """The CH vertex file's arrays: the carbon gen5d file's edges, with x and sumw2 replaced by step A's CH ones.
    Control V: step A's frozen carbon arrays are the carbon file's bitwise, and its CH arrays are combine(C, H)."""
    report("V", "step A's carbon xsec and sumw2 are the staged carbon vertex file's, bitwise",
           np.array_equal(stepA["xsec_C12_frozen"], carbon_gen5d["xsec_flat"])
           and np.array_equal(stepA["sumw2_C12_frozen"], carbon_gen5d["sumw2_flat"]))
    x, v = gc.combine(stepA["xsec_C12_frozen"], stepA["sumw2_C12_frozen"], stepA["xsec_H"], stepA["sumw2_H"])
    report("V", "step A's CH arrays are combine(carbon, hydrogen), bitwise",
           np.array_equal(x, stepA["xsec_CH"]) and np.array_equal(v, stepA["sumw2_CH"]))
    out = {k: np.asarray(carbon_gen5d[k]) for k in carbon_gen5d if k.startswith("edges_")}
    out["xsec_flat"], out["sumw2_flat"] = np.asarray(stepA["xsec_CH"], float), np.asarray(stepA["sumw2_CH"], float)
    return out


def config_ch(cfg: dict, run_dir: Path, ch: dict[str, tuple[Path, str]]) -> dict:
    """The committed config with every pscratch path at its staged copy (same digest) and the CH vertices."""
    def repoint(o):
        if isinstance(o, dict):
            return {k: (str(staged(run_dir, v)) if k == "path" and str(v).startswith(str(SCRATCH)) else repoint(v))
                    for k, v in o.items()}
        return o
    out = repoint(cfg)
    for name, (path, h) in ch.items():
        v = dict(out["vertices"][name])
        v.update(path=str(path), sha256=h,
                 label=v["label"] + "; CH = C12 + free proton, 12:1 per nucleon (GENCMP step A), generator definitions")
        out["vertices"][name] = v
    return out


def cmd_vertices(a) -> int:
    out = a.run_dir / "vertices"
    report("V", f"{out} does not exist (no overwrite)", not out.exists())
    cfg = json.loads(CONFIG.read_text())
    ch = {}
    for name, npz in CH_VERTICES.items():
        carbon = staged(a.run_dir, cfg["vertices"][name]["path"])
        report("V", f"{name}: the staged carbon file is the config's", sha256(carbon) == cfg["vertices"][name]["sha256"])
        with np.load(carbon, allow_pickle=True) as zc, np.load(npz, allow_pickle=False) as zs:
            arrays = ch_arrays({k: zc[k] for k in zc.files if k != "meta_json"}, {k: zs[k] for k in zs.files})
        p = out / f"{name}_ch_xsec5d.npz"
        out.mkdir(parents=True, exist_ok=True)
        np.savez(p, **arrays)
        ch[name] = (p, sha256(p))
    cc = config_ch(cfg, a.run_dir, ch)
    E.write_new(out / "config_ch.json", (json.dumps(cc, indent=1) + "\n").encode())
    print(f"[V] {len(ch)} CH vertex files and config_ch.json written", flush=True)
    return 0


# ---------------------------------------------------------------- ratios


def cmd_ratios(a) -> int:
    import pvl_ratios
    cfg = a.run_dir / "vertices" / "config_ch.json"
    rc = pvl_ratios.main(["--config", str(cfg), "--rung", RUNG, "--out", str(a.run_dir / "prep")])
    report("R1", "pvl_ratios ran", rc == 0, f"rc {rc}")
    new, old = a.run_dir / "prep" / RUNG, staged(a.run_dir, SCRATCH / PREP)
    for name in ("tune_v1", "genie_mec", "genie_mec_sq"):
        bad = A.compare_numbers(json.loads((old / f"{name}.json").read_text()),
                                json.loads((new / f"{name}.json").read_text()), ("/source", "/reference"))
        report("R1", f"{name}.json holds the committed prep's numbers", not bad, str(bad[:5]))
    return 0


# ---------------------------------------------------------------- unfold


UNFOLDS = ("nuwro_ch", "gibuu_ch", "nuwro_carbon_R2")


def cmd_unfold(a) -> int:
    """After the job's three srun steps (receipts/x_e2_unfold.sh, launched as the PV ladder launched its own,
    sbatch_pvl.sh:70-83): the products' digests, and control R2."""
    outd = a.run_dir / "unfold"
    report("U", "unfold.json does not exist (no overwrite)", not (outd / "unfold.json").exists())
    rec = {"products": {k: sha256(outd / f"L-5D-PV_e_{k}.npz") for k in UNFOLDS if (outd / f"L-5D-PV_e_{k}.npz").exists()}}
    report("U", "all three products exist", len(rec["products"]) == len(UNFOLDS), str(sorted(rec["products"])))
    new = np.load(outd / "L-5D-PV_e_nuwro_carbon_R2.npz", allow_pickle=True)["xsec_flat"]
    ref = np.load(staged(a.run_dir, SCRATCH / PRODUCTS / "L-5D-PV_e_nuwro.npz"), allow_pickle=True)["xsec_flat"]
    rec["R2_bitwise"] = bool(np.array_equal(new, ref))
    E.write_new(outd / "unfold.json", (json.dumps(rec, indent=1) + "\n").encode())
    report("R2", "the NuWro carbon rerun reproduces the committed L-5D-PV_e_nuwro bitwise", rec["R2_bitwise"])
    return 0


# ---------------------------------------------------------------- chi2


def factor(xs: dict[str, np.ndarray], rmap: np.ndarray, n: int) -> np.ndarray:
    """build_cmodel5d.factor's arithmetic: s_k = rel_shift(integrals(x_k), integrals(x_tune_v1)), k in VERTICES."""
    import build_cmodel5d as BC
    import pv2d_lib as P
    X0 = BC.integrals(xs["tune_v1"], rmap, n)
    return np.array([P.rel_shift(BC.integrals(xs[v], rmap, n), X0) for v in BC.VERTICES])


def model_abs(f: np.ndarray, S: np.ndarray) -> np.ndarray:
    return np.outer(f, f) * (S.T @ S)


def chi2_rows(readout: dict, f: np.ndarray, C_rest: np.ndarray, S: np.ndarray) -> dict:
    """Each corner prediction's total and shape-only chi2 under C_rest + diag(f) S^T S diag(f), from its g and V_g as
    E-1's Stage G readout records them (V_g = (sigma_Vg_over_f f)^2 on its cells)."""
    C = C_rest + model_abs(f, S)
    out = {}
    for p in readout["predictions"]:
        if p["name"] == "mnvtune_v1":
            continue
        cells = [int(c[1:]) for c in p["cells"]]
        g, Vg = np.zeros(f.size), np.zeros(f.size)
        g[cells] = p["g"]
        Vg[cells] = (np.asarray(p["sigma_Vg_over_f"]) * f[cells]) ** 2
        c = fg.compare(f, g, Vg, C, cells, "C_model rebuilt")
        out[p["name"]] = {k: c[k]["chi2"] for k in ("total", "shape_only")}
    return out


def cmd_chi2(a) -> int:
    import build_cmodel5d as BC
    out = a.run_dir / "chi2"
    report("C", f"{out} does not exist (no overwrite)", not out.exists())
    cm = json.loads(A.pinned(CMODEL5, CMODEL5_SHA256, "cmodel_5d.json", "C0"))
    defn_rmap, n, *_ = BC.load_definition(BC._HERE / "readouts" / "h2_definition.json",
                                          _REPO / "docs/orchestration/state/s5p/stage1/stage1_inspect.json", BC.EXPECT)
    prod = lambda name: np.asarray(np.load(staged(a.run_dir, SCRATCH / PRODUCTS / f"{name}.npz"),  # noqa: E731
                                           allow_pickle=True)["xsec_flat"], float)
    xs_c = {"tune_v1": prod("L-5D-PV_e_tune_v1"), **{v: prod(f"L-5D-PV_e_{v}") for v in BC.VERTICES}}
    S_c = factor(xs_c, defn_rmap, n)
    report("C1", "the carbon products give cmodel_5d.json's S bitwise", np.array_equal(S_c, np.asarray(cm["S"], float)))
    uf = a.run_dir / "unfold"
    rec_u = json.loads((uf / "unfold.json").read_text())
    xs_ch = dict(xs_c)
    for v in ("nuwro", "gibuu"):
        p = uf / f"L-5D-PV_e_{v}_ch.npz"
        report("C0", f"{v} CH: the product is the one unfold recorded", sha256(p) == rec_u["products"][f"{v}_ch"])
        xs_ch[v] = np.asarray(np.load(p, allow_pickle=True)["xsec_flat"], float)
    S_ch = factor(xs_ch, defn_rmap, n)
    dp = json.loads(A.pinned(DP, DP_SHA256, "data product", "C0"))
    blk = np.load(BLOCK, allow_pickle=False)
    report("C0", "the with-block npz is its pinned bytes", sha256(BLOCK) == BLOCK_SHA256)
    f = np.asarray(blk["f"], float)
    Ce, Cma = (np.asarray(dp["matrices"][k], float) for k in ("C_e", "C_model_abs"))
    report("C2", "diag(f) S^T S diag(f) from cmodel_5d.json's S is the data product's C_model_abs (1e-12)",
           bool(np.all(np.abs(model_abs(f, S_c) - Cma) <= 1e-12 * np.abs(Cma).max())))
    arms = {"with": Ce + np.asarray(blk["C_resp"], float) + np.asarray(blk["C_PL5D"], float),
            "nopl": Ce + np.asarray(blk["C_resp"], float)}
    res = {}
    for arm, C_rest in arms.items():
        path = E1 / arm / "readout" / "fd_g_readout.json"
        report("C0", f"E-1's {arm} Stage G readout is the committed one",
               sha256(path) == E1_SHA256[arm])
        r1 = json.loads(path.read_text())
        carbon, chm = chi2_rows(r1, f, C_rest, S_c), chi2_rows(r1, f, C_rest, S_ch)
        for p in r1["predictions"]:
            if p["name"] in carbon:
                for k in ("total", "shape_only"):
                    report("C3", f"{arm} {p['name']} {k}: the carbon S reproduces E-1's chi2 (1e-10)",
                           abs(carbon[p["name"]][k] - p[k]["chi2"]) <= TOL * abs(p[k]["chi2"]))
        res[arm] = {name: {k: {"carbon": carbon[name][k], "CH": chm[name][k], "delta": chm[name][k] - carbon[name][k]}
                           for k in ("total", "shape_only")} for name in carbon}
    deltas = [v[k]["delta"] for arm in res.values() for v in arm.values() for k in ("total", "shape_only")]
    dmax = float(max(abs(x) for x in deltas))
    rec = {"schema": "fd-gencmp-e2/1", "S_carbon": S_c.tolist(), "S_CH": S_ch.tolist(),
           "vertices": list(BC.VERTICES), "chi2": res, "delta_max_abs": dmax,
           "delta_flag": {"threshold": DELTA_FLAG, "exceeded": dmax > DELTA_FLAG,
                          "rule": "binding ruling 4: above it, the director also brings Joseph the question of "
                                  "rebuilding the reported C_model on CH; no covariance changes without him"},
           "unfold": rec_u, "label": "C_model with CH shape ratios for NuWro and GiBUU (generator definitions); "
                                     "GENIE+MEC unchanged; a measurement of #651 item 6's caveat, not a new covariance"}
    out.mkdir(parents=True)
    E.write_new(out / "e2.json", (json.dumps(rec, indent=1, default=float) + "\n").encode())
    print(f"[E2] max |Delta chi2| = {dmax:.3f} (flag above {DELTA_FLAG}: {dmax > DELTA_FLAG})", flush=True)
    return 0


# ---------------------------------------------------------------- CLI


def build_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("stage", "vertices", "ratios", "unfold", "chi2"):
        s = sub.add_parser(name)
        s.add_argument("--run-dir", type=Path, required=True)
        if name == "stage":
            s.add_argument("--scratch", type=Path, default=SCRATCH)
    return p.parse_args(argv)


def main(argv=None) -> int:
    a = build_args(argv)
    try:
        if a.cmd == "stage":
            return E.cmd_stage(a, gc.load_pins(INPUTS))
        return {"vertices": cmd_vertices, "ratios": cmd_ratios, "unfold": cmd_unfold, "chi2": cmd_chi2}[a.cmd](a)
    except (Stop, A.Stop, fg.Stop) as e:
        print(f"[STOP] {e}", file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

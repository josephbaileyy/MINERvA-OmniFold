#!/usr/bin/env python3
"""The run-period diagnosis's inputs (state/measurement-paper/5d-community-20261024/FD-RPD-DECLARATION.md, part 1
revision 4, bound by FD-RPD-BINDING-1.md): staging, the per-playlist flux and F1, the per-playlist dumps' check, N0's
pseudo-playlist partitions, and the (e) unfolds.

    fd_rpd_inputs.py stage    --r <R>                                   (login)  stage S: O_NOATIME copies
    fd_rpd_inputs.py flux     --r <R>                                   (login)  stage S: 12 flux files, F1, e
    fd_rpd_inputs.py check    --r <R> --playlist X                      (job A)  receipt and MC truth of X
    fd_rpd_inputs.py n0-split --r <R> --partition p                     (job A)  one N0 partition, its truths
    fd_rpd_inputs.py unfold   --r <R> --what playlist|n0|k2 ...         (jobs A, B)

* ``stage`` copies every pre-existing input into <R>/staged, each read once through an O_NOATIME descriptor and
  required at its pin (part 1 section 1); the atime of each source is recorded before and after. Every later step
  reads only the staged copies or files this campaign made.
* ``flux`` builds X's flux file from the staged baseline files with the pinned production combiner's reader and
  arithmetic (combine_flux_MEFHC.read_playlist, its module global BASE pointed at the staged copies; the pinned file
  is not edited), then decides F1: each period's data-POT-weighted combination of its playlists equals 5B's committed
  period flux file bin by bin to 1e-12 relative, with its POTs, and ALL equals the staged production flux. It records
  each flux file's digest and bin contents, and the exposure shares e_X = POT_X Phi_X / sum (Phi constant over p_T).
* ``check`` (after nn_dump_inputs.py and s5p_input_dumps.py lateral on X's staged loop with --mcfile X's flux) refuses
  unless: the loop is X's pinned zero loop; the flux file is the one F1 recorded for X; the lateral npz is array for
  array the nn_dump npz; the background dump names the lateral npz and the staged loop; the npz's flux key is X's
  recorded bin contents; and the npz's data POT, the loop's dataPOTUsed and the flux file's
  DataPOTUsedForFluxWeighting agree to 1e-12. It records the loop's mcPOTUsed (C1's s_X), then writes X's MC truth.
* ``n0-split`` writes one N0 partition (part 1 section 4): ALL's staged lateral inputs split by a multinomial draw at
  F1's shares into 12 pseudo-playlists, the assignment vectors stored, per-event weights unchanged, data_pot scaled by
  e, flux ALL's, denom_nd ratio-preserving so each pseudo-playlist's completeness is ALL's, bkg_nd each one's own,
  measured_weights carried from ALL's rows (config R does not read it); then each pseudo-npz's MC truth.
* ``unfold`` runs the unchanged s5p_numerics.py (config R, 5 iterations, real data, estimator seed 42) on a playlist
  (its check receipt), an N0 pseudo-playlist (its partition receipt) or K2's staged 5B PC inputs.

Every step refuses to overwrite (exit 3) and refuses a pinned input with another digest (exit 4); a failed check
refuses with exit 5 and writes nothing.

MEASURES: nothing; it re-expresses committed and staged inputs and runs the existing tools. CANNOT AUTHORIZE: any
reading, verdict or covariance; those are fd_rpd.py's.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
DEPLOY = _ND.parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import fd_ct_period_inputs as pi  # noqa: E402  (PLAYLISTS, PERIODS, ZERO_LOOPS, FLUX, FLUX_REL, MP1_ZERO, NPZ_KEYS, ...)

P = "/pscratch/sd/j/josephrb"
PLAYLISTS = pi.PLAYLISTS
PERIODS = {k: v for k, v in pi.PERIODS.items() if k != "ALL"}
N_PART = 10
N0_SEED0 = 20261102            # partition p's multinomial seed is N0_SEED0 + p, p = 1..10
N0_SMALL = 0.03                # N0's small set: the pseudo-playlists with e below this
REL_FLUX = 1e-12
POT_REL = pi.POT_REL
HIST = "pTmu_reweightedflux_integrated"
BASE_FLUX = f"{P}/MINERvA-OmniFold/2d-unfolding/baseline_flux"
COMBINER = ("2d-unfolding/combine_flux_MEFHC.py", "1fc5c1e9fdb15011e5a6209f415e3b184de9e7080944b3548763e0294d117803")
PROD_FLUX = "d40aea69235cdc98644e1bb3e622e579d6b81904c004c83fe50465079989f316"
# the per-playlist baseline flux and data-POT files, as Stage B's verify_c04.json recorded them (2026-10-12)
BASELINE = {
    "runEventLoopData_1A.root": "d7c57e84c5f07a74818f53ae0571366d3f135af3d4059daa6c7f36857bd84fe3",
    "runEventLoopData_1B.root": "b648ee4d4f3eb053a6eeb6564f00d9d54ea1786717b5cc1f9adf30d29c5a45bf",
    "runEventLoopData_1C.root": "1efe76c7196b77e1ba16b83731d3bc585dce1f96292e40b683ece57e49428344",
    "runEventLoopData_1D.root": "d706af08ea3a9c43ef66ffb2d369fd7398bb229c88c9072de5674dd66b46d13a",
    "runEventLoopData_1E.root": "7c7a95f54431a581df4b1b427cba6128974b309e861f23fd6f243aab0f910a4b",
    "runEventLoopData_1F.root": "9991635c593ee16617c793ab59cd6b331b2273bf030b41d05a79e5d14f366923",
    "runEventLoopData_1G.root": "b3ec03e304a3dbe19c2aa7505427bc06fd81e7388afe1f754dbb48b782c2451d",
    "runEventLoopData_1L.root": "c42829d9df2aed7417cb73d1b4060ccce7c55d7ef8acd74624ceb461095a9ae8",
    "runEventLoopData_1M.root": "ed56c3adfe15d6588016194629802599795dbbca11bc67df3025d7eb1668bb55",
    "runEventLoopData_1N.root": "4f369303730eae4a56c4a52e201332b145b284321dd299b11bc336e3eb721bc5",
    "runEventLoopData_1O.root": "e0b93d385d2e63a9b40255674dd8b0f240245772008de09e0d0b1195e6d5433b",
    "runEventLoopData_1P.root": "42c1f6ef7c94e45964eae5ecb096b0d277bd95c1aa9aaa3dea8b16f7677afe8f",
    "runEventLoopMC_1A.root": "d54d2a2c6e0454b035c69d82aff3d3ac2c8cb5e589fea09f2b439804854b1107",
    "runEventLoopMC_1B.root": "b3fe98499fd504c023bc188c6995e0bdfe98a1d8694f6af3413bf08a321f3f1e",
    "runEventLoopMC_1C.root": "199789aaefa34ac7dda5d506f9be638b6caa0b0628f6709890da66b6c2862b1e",
    "runEventLoopMC_1D.root": "69006ab6a730dff0ab88f16e9e02fd5c4af5d74df236e0a75757daf2fa542c77",
    "runEventLoopMC_1E.root": "dc4517b83f33a347f633176f7105a4154b36496138baa2e225ae358e8489f6d1",
    "runEventLoopMC_1F.root": "803e5fb593b6e6c4264f782faef6354ec17f59c0763f5696a203ae672db3915d",
    "runEventLoopMC_1G.root": "379a052a0249dd41755498e7e01a34a2cdad238346c386f5e4cbc471a053c4a8",
    "runEventLoopMC_1L.root": "c65876c847709c44ec56662ac865c003bb4a656ce4091d47eeb4516112d5b670",
    "runEventLoopMC_1M.root": "36879d6bbb0201c8c9d539589c23073b1b3bcb9c7b3c3219e14199756b6533d0",
    "runEventLoopMC_1N.root": "09f9e0f7f9311d63c3503e11ae43934df530ad0c6c0641605c6dfb377bb9207c",
    "runEventLoopMC_1O.root": "0d195e4d94057b2679456fdf9e82f912247c9638f5aae3e757bbfcbdc77a4c4f",
    "runEventLoopMC_1P.root": "3d98169a18adad7132d53aaa2d1abb992294cd0fed05dfef9c533ed224f877f3",
}
REL5 = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ct/5b"
INVENTORY_REL = f"{REL5}/run/preserve/INVENTORY.sha256"
CHECK_PC_REL = f"{REL5}/run/inputs/check_PC.json"
B5 = f"{P}/fd-ct-5b-20261030"
S1_SRC = (f"{P}/s1-20261024/s1_assembly.npz", "db000707780d4d6da65389be9adedfd9a3ba6552a255f6ce81ccbdd0b8eb72a4")
CRESP_SRC = (f"{P}/cresp-20261026/out/cresp.npz", "4d8b579732b79cbbb8e6c9a4f6335c4bda4eae6dd4194241a0d8cd6e7ea8a20a")
LOOPS = f"{P}/measurement-paper/phase1/mp1/s1/evloop/zero"
MP1_LAT = f"{P}/measurement-paper/phase1/mp1/s1/lateral"
EVENT_KEYS = ("MCgen", "MCreco", "measured", "pass_reco", "pass_truth", "w_truth", "w_reco", "measured_weights")
SIGNAL_KEYS = ("MCgen", "MCreco", "pass_reco", "pass_truth", "w_truth", "w_reco")
DATA_KEYS = ("measured", "measured_weights")
GLOBAL_KEYS = ("axes", "flux", "n_nucleons", "edges_0", "edges_1", "edges_2", "edges_3", "edges_4", "nedges")


class Refuse(Exception):
    def __init__(self, code: int, why: str):
        super().__init__(why)
        self.code = code


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 24), b""):
            h.update(block)
    return h.hexdigest()


def require(path: Path, want: str, what: str) -> str:
    got = sha256(path)
    if got != want:
        raise Refuse(4, f"{what} {path}: sha256 {got} != {want}")
    return got


def fresh(*paths: Path) -> None:
    for p in paths:
        if p.exists():
            raise Refuse(3, f"refusing to overwrite {p}")


def write_json(path: Path, obj: dict) -> None:
    tmp = path.with_name(path.name + ".partial")
    tmp.write_text(json.dumps(obj, indent=1) + "\n")
    tmp.replace(path)


def code_sha() -> dict:
    files = {"fd_rpd_inputs.py": Path(__file__).resolve(), "fd_ct_period_inputs.py": Path(pi.__file__).resolve(),
             "nn_dump_inputs.py": _ND / "nn_dump_inputs.py", "s5p_input_dumps.py": _ND / "s5p_input_dumps.py",
             "s5p_mc_truth_pred.py": _ND / "s5p_mc_truth_pred.py", "s5p_numerics.py": _ND / "s5p_numerics.py",
             "combine_flux_MEFHC.py": DEPLOY / COMBINER[0]}
    return {k: sha256(p) for k, p in files.items() if p.is_file()}


# ---------------------------------------------------------------- stage (stage S)


def inventory_pins(deploy: Path = DEPLOY) -> dict[str, str]:
    """5B's preserved products, by their committed INVENTORY rows: absolute path -> sha256."""
    pins = {}
    for line in (deploy / INVENTORY_REL).read_text().splitlines():
        if line.strip():
            sha, path = line.split(None, 1)
            pins[path.strip()] = sha
    return pins


def stage_sources(deploy: Path = DEPLOY) -> dict[str, tuple[str, str]]:
    """Every pre-existing input this campaign reads: staged name -> (source path, pin). Part 1 section 1's table."""
    inv = inventory_pins(deploy)
    pc = json.loads((deploy / CHECK_PC_REL).read_text())["files"]
    src = {}
    for pl in PLAYLISTS:
        src[f"zero/runEventLoopOmniFold_5D_{pl}_zero.root"] = (f"{LOOPS}/runEventLoopOmniFold_5D_{pl}_zero.root",
                                                              pi.ZERO_LOOPS[pl])
    for name, sha in BASELINE.items():
        src[f"baseline/{name}"] = (f"{BASE_FLUX}/{name}", sha)
    src["baseline/runEventLoopMC_MEFHC.root"] = (f"{BASE_FLUX}/runEventLoopMC_MEFHC.root", PROD_FLUX)
    for per in PERIODS:
        for path, sha in inv.items():
            if path.startswith(f"{B5}/unf/{per}/"):
                src[f"5b/unf/{per}/{Path(path).name}"] = (path, sha)
        tpath = f"{B5}/truth/truth_{per}.npz"
        src[f"5b/truth/truth_{per}.npz"] = (tpath, inv[tpath])
    src["5b/dumps/lat_PC.npz"] = tuple(pc["lat_npz"])
    src["5b/dumps/lat_PC_bkg.npz"] = tuple(pc["lat_bkg"])
    src["mp1/lat_zero.npz"] = (f"{MP1_LAT}/lat_zero.npz", pi.MP1_ZERO["lat_npz"])
    src["mp1/lat_zero_bkg.npz"] = (f"{MP1_LAT}/lat_zero_bkg.npz", pi.MP1_ZERO["lat_bkg"])
    src["s1/s1_assembly.npz"] = S1_SRC
    src["cresp/cresp.npz"] = CRESP_SRC
    return src


def noatime_copy(src: Path, dst: Path) -> tuple[str, int]:
    """Copy src to dst through an O_NOATIME descriptor, hashing as it reads. O_NOATIME needs the caller to own src;
    os.open raises otherwise, and the copy refuses."""
    h = hashlib.sha256()
    n = 0
    fd = os.open(src, os.O_RDONLY | getattr(os, "O_NOATIME", 0))
    try:
        with os.fdopen(fd, "rb", closefd=False) as fin, open(dst, "wb") as fout:
            for block in iter(lambda: fin.read(1 << 24), b""):
                h.update(block)
                fout.write(block)
                n += len(block)
    finally:
        os.close(fd)
    return h.hexdigest(), n


def run_stage(a) -> int:
    out = a.r / "staged"
    fresh(out)
    if not hasattr(os, "O_NOATIME") and not a.allow_no_noatime:
        raise Refuse(2, "this platform has no O_NOATIME")
    sources = stage_sources(a.deploy)
    missing = [s for s, _ in sources.values() if not Path(s).is_file()]
    if missing:
        raise Refuse(4, f"missing sources: {missing}")
    out.mkdir(parents=True)
    rows, t0 = {}, time.time()
    for name, (src, pin) in sorted(sources.items()):
        dst = out / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        before = os.stat(src)
        got, n = noatime_copy(Path(src), dst)
        after = os.stat(src)
        if got != pin:
            dst.unlink()
            raise Refuse(4, f"{src}: sha256 {got} != {pin}")
        os.chmod(dst, 0o440)
        rows[name] = {"source": src, "sha256": got, "bytes": n, "source_mtime": int(before.st_mtime),
                      "source_atime_before": int(before.st_atime), "source_atime_after": int(after.st_atime),
                      "atime_unchanged": int(before.st_atime) == int(after.st_atime)}
    rec = {"schema": "fd-rpd-staged/1", "n_files": len(rows), "files": rows,
           "atime_unchanged_all": all(r["atime_unchanged"] for r in rows.values()),
           "code_sha256": code_sha(), "seconds": round(time.time() - t0, 1)}
    write_json(out / "STAGED.json", rec)
    print(json.dumps({"staged": len(rows), "bytes": sum(r["bytes"] for r in rows.values()),
                      "atime_unchanged_all": rec["atime_unchanged_all"]}), flush=True)
    return 0


def staged(r: Path, name: str) -> tuple[Path, str]:
    """A staged copy, at the digest its staging recorded (and its pin, which staging required)."""
    rec = json.loads((r / "staged/STAGED.json").read_text())
    if rec.get("schema") != "fd-rpd-staged/1" or name not in rec["files"]:
        raise Refuse(4, f"{name} is not in the staging record")
    p = r / "staged" / name
    return p, require(p, rec["files"][name]["sha256"], f"staged {name}")


# ---------------------------------------------------------------- flux (stage S, F1)


def load_combiner(deploy: Path, base: Path):
    """The pinned production combiner, imported unchanged, with its module global BASE pointed at the staged copies
    (read_playlist reads f"{BASE}/..." at call time)."""
    path = deploy / COMBINER[0]
    require(path, COMBINER[1], "combine_flux_MEFHC.py")
    spec = importlib.util.spec_from_file_location("combine_flux_MEFHC", path)
    cf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cf)
    cf.BASE = str(base)
    return cf


def combine(per: list[dict]) -> dict:
    """The combiner's arithmetic (combine_flux_MEFHC.main, lines 82-96), on per-playlist reads."""
    w = np.array([p["pot_data"] for p in per])
    tot_d, tot_m = float(sum(p["pot_data"] for p in per)), float(sum(p["pot_mc"] for p in per))
    c = (np.stack([p["contents"] for p in per]).T @ w) / tot_d
    e = np.sqrt((np.stack([p["errors"] for p in per]).T ** 2) @ (w ** 2)) / tot_d
    return {"contents": c, "errors": e, "pot_data": tot_d, "pot_mc": tot_m}


def write_flux(path: Path, edges, comb: dict, playlists) -> None:
    import ROOT
    from array import array

    h = ROOT.TH1D(HIST, "POT-weighted MEFHC flux (m^{-2}/POT)", len(edges) - 1, array("d", edges))
    for i, (c, e) in enumerate(zip(comb["contents"], comb["errors"])):
        h.SetBinContent(i + 1, float(c))
        h.SetBinError(i + 1, float(e))
    h.SetDirectory(0)
    f = ROOT.TFile.Open(str(path), "RECREATE")
    h.Write(HIST)
    ROOT.TParameter("double")("POTUsed", comb["pot_mc"]).Write()
    ROOT.TParameter("double")("DataPOTUsedForFluxWeighting", comb["pot_data"]).Write()
    ROOT.TNamed("fluxSource", f"POT(data)-weighted combination of staged baseline_flux/runEventLoopMC_<"
                f"{','.join(playlists)}>.root:{HIST} (fd_rpd_inputs.py flux)").Write()
    ROOT.TNamed("periodPlaylists", ",".join(playlists)).Write()
    f.Close()


def read_flux(path: Path) -> dict:
    import ROOT

    f = ROOT.TFile.Open(str(path), "READ")
    h = f.Get(HIST)
    n = h.GetNbinsX()
    out = {"edges": [h.GetBinLowEdge(i) for i in range(1, n + 2)],
           "contents": [h.GetBinContent(i) for i in range(1, n + 1)],
           "errors": [h.GetBinError(i) for i in range(1, n + 1)],
           "pot_mc": float(f.Get("POTUsed").GetVal()),
           "pot_data": float(f.Get("DataPOTUsedForFluxWeighting").GetVal())}
    f.Close()
    return out


def rel_max(a, b) -> float:
    a, b = np.asarray(a, float), np.asarray(b, float)
    if a.shape != b.shape:
        return float("inf")
    with np.errstate(divide="ignore", invalid="ignore"):
        d = np.where(b != 0, np.abs(a / b - 1.0), np.where(a == 0, 0.0, np.inf))
    return float(d.max()) if d.size else 0.0


def f1_decide(per_pl: dict, periods: dict, prod: dict) -> dict:
    """F1: the data-POT-weighted combination of each period's playlists against 5B's committed period flux, and of
    all twelve against the production flux, bin by bin (contents and errors) and in both POTs, to REL_FLUX."""
    out = {}
    for name, pls, ref in [*((k, PERIODS[k], v) for k, v in periods.items()), ("ALL", PLAYLISTS, prod)]:
        comb = combine([{**per_pl[pl], "contents": np.asarray(per_pl[pl]["contents"]),
                         "errors": np.asarray(per_pl[pl]["errors"])} for pl in pls])
        dev = {"contents": rel_max(comb["contents"], ref["contents"]), "errors": rel_max(comb["errors"], ref["errors"]),
               "pot_data": abs(comb["pot_data"] / ref["pot_data"] - 1.0),
               "pot_mc": abs(comb["pot_mc"] / ref["pot_mc"] - 1.0),
               "edges": rel_max(per_pl[pls[0]]["edges"], ref["edges"])}
        out[name] = {"max_rel": dev, "pass": all(v <= REL_FLUX for v in dev.values())}
    return out


def exposure_shares(per_pl: dict, loop_pot: dict | None = None) -> tuple[dict, float]:
    """e_X = POT_X Phi_X / sum_Y POT_Y Phi_Y, with Phi_X the (p_T-constant) integrated flux and POT_X the staged loop's
    dataPOTUsed (part 1 section 5; F1 requires it equal to the flux file's data POT to 1e-12); returns e and the largest
    relative spread of Phi over p_T bins."""
    spread = max(float(np.max(np.abs(np.asarray(v["contents"]) / np.mean(v["contents"]) - 1.0))) for v in per_pl.values())
    pot = loop_pot or {pl: v["pot_data"] for pl, v in per_pl.items()}
    raw = {pl: pot[pl] * float(np.mean(v["contents"])) for pl, v in per_pl.items()}
    tot = sum(raw.values())
    return {pl: raw[pl] / tot for pl in PLAYLISTS}, spread


def flux_decision(per_pl: dict, f1: dict, pots: dict) -> dict:
    """Stage S's verdict from F1, the flux's flatness and each staged loop's (data, MC) POT: every loop's data POT must
    equal its flux file's to POT_REL, and e is computed from the loops' data POT (part 1 section 5)."""
    loops = {pl: {"data_pot": d, "mc_pot": m, "over_flux_data_pot_minus_1": d / per_pl[pl]["pot_data"] - 1.0}
             for pl, (d, m) in pots.items()}
    loops_ok = all(abs(v["over_flux_data_pot_minus_1"]) <= POT_REL for v in loops.values())
    e, spread = exposure_shares(per_pl, {pl: v["data_pot"] for pl, v in loops.items()})
    ok = all(v["pass"] for v in f1.values()) and spread <= pi.FLUX_FLAT and loops_ok
    return {"verdict": "PASS" if ok else "FAIL", "F1": f1, "loops": loops,
            "loops_data_pot_equal_flux_data_pot": loops_ok, "flux_rel_spread_over_pt": spread, "exposure_share": e}


def run_flux(a) -> int:
    out = a.r / "flux"
    fresh(out)
    base = a.r / "staged/baseline"
    for name in BASELINE:
        staged(a.r, f"baseline/{name}")
    prod_path, _ = staged(a.r, "baseline/runEventLoopMC_MEFHC.root")
    cf = load_combiner(a.deploy, base)
    out.mkdir(parents=True)
    per_pl, files = {}, {}
    for pl in PLAYLISTS:
        edges, contents, errors, pot_data, pot_mc = cf.read_playlist(pl)
        comb = combine([{"contents": contents, "errors": errors, "pot_data": pot_data, "pot_mc": pot_mc}])
        p = out / f"runEventLoopMC_{pl}.root"
        write_flux(p, list(edges), comb, [pl])
        os.chmod(p, 0o440)
        per_pl[pl] = read_flux(p)
        files[pl] = [str(p), sha256(p)]
    periods = {}
    for per in PERIODS:
        p = a.deploy / pi.FLUX_REL / f"runEventLoopMC_{per}.root"
        require(p, pi.FLUX[per], f"5B {per} flux file")
        periods[per] = read_flux(p)
    f1 = f1_decide(per_pl, periods, read_flux(prod_path))
    pots = {pl: loop_pots(staged(a.r, f"zero/runEventLoopOmniFold_5D_{pl}_zero.root")[0]) for pl in PLAYLISTS}
    rec = {"schema": "fd-rpd-flux/1", **flux_decision(per_pl, f1, pots), "tolerance_rel": REL_FLUX,
           "flux_flat_tolerance": pi.FLUX_FLAT, "files": files, "per_playlist": per_pl, "code_sha256": code_sha()}
    write_json(out / "F1.json", rec)
    e = rec["exposure_share"]
    print(json.dumps({"F1": rec["verdict"], "e_min": min(e.values()), "e_max": max(e.values())}), flush=True)
    return 0 if rec["verdict"] == "PASS" else 1


def flux_record(r: Path) -> dict:
    p = r / "flux/F1.json"
    rec = json.loads(p.read_text()) if p.is_file() else {}
    if (rec.get("schema"), rec.get("verdict")) != ("fd-rpd-flux/1", "PASS"):
        raise Refuse(5, "F1 did not record a PASS")
    return rec


# ---------------------------------------------------------------- check (job A)


def loop_pots(path: Path) -> tuple[float, float]:
    """The loop's dataPOTUsed and mcPOTUsed, as the dumps read them (unfold_2d_omnifold_unbinned.get_pot_scales)."""
    for p in (str(DEPLOY / "2d-unfolding"), str(_ND)):
        if p not in sys.path:
            sys.path.insert(0, p)
    import ROOT
    import unfold_2d_omnifold_unbinned as u2d

    f = ROOT.TFile.Open(str(path), "READ")
    data_pot, mc_pot, _ = u2d.get_pot_scales(f)
    f.Close()
    return float(data_pot), float(mc_pot)


def run_check(a) -> int:
    X = a.playlist
    d = {k: a.r / v for k, v in playlist_paths(X).items()}
    fresh(d["receipt"], d["truth"])
    for k in ("receipt", "truth"):
        d[k].parent.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    loop, loop_sha = staged(a.r, f"zero/runEventLoopOmniFold_5D_{X}_zero.root")
    if loop_sha != pi.ZERO_LOOPS[X]:
        raise Refuse(4, f"{X}'s staged loop is not its pinned zero loop")
    fr = flux_record(a.r)
    fpath, fsha = fr["files"][X]
    if Path(fpath) != d["flux"]:
        raise Refuse(4, f"F1 recorded {fpath} for {X}, not {d['flux']}")
    require(d["flux"], fsha, f"{X} flux file")
    problems = []
    nn_vs_lat = pi.compare(d["nn"], d["lat"], pi.NPZ_KEYS)
    if not all(nn_vs_lat.values()):
        problems.append(f"the lateral npz is not the nn_dump npz: {sorted(k for k, v in nn_vs_lat.items() if not v)}")
    nn_sha, lat_sha, bkg_sha = sha256(d["nn"]), sha256(d["lat"]), sha256(d["bkg"])
    with np.load(d["bkg"], allow_pickle=False) as b:
        bmeta = json.loads(str(b["meta"]))
    if (bmeta.get("npz_sha256"), bmeta.get("omnifile")) != (lat_sha, str(loop)):
        problems.append("the background dump does not name this lateral npz and staged loop")
    with np.load(d["lat"], allow_pickle=True) as z:
        npz_pot = float(z["data_pot"])
        flux = np.asarray(z["flux"], float)
    want_flux = fr["per_playlist"][X]["contents"]
    flux_dev = rel_max(flux, want_flux)
    if flux_dev > REL_FLUX:
        problems.append(f"the npz flux key is not {X}'s flux file's bin contents ({flux_dev:.3e})")
    data_pot, mc_pot = loop_pots(loop)
    f_pot = fr["per_playlist"][X]["pot_data"]
    pot = {"npz_over_loop_minus_1": npz_pot / data_pot - 1.0, "flux_weighting_over_loop_minus_1": f_pot / data_pot - 1.0}
    if max(abs(v) for v in pot.values()) > POT_REL:
        problems.append(f"data POT: {pot}")
    if problems:
        raise Refuse(5, "; ".join(problems))
    rec = {"schema": "fd-rpd-inputs/1", "playlist": X,
           "files": {"loop": [str(loop), loop_sha], "flux": [str(d["flux"]), fsha], "nn_npz": [str(d["nn"]), nn_sha],
                     "lat_npz": [str(d["lat"]), lat_sha], "lat_bkg": [str(d["bkg"]), bkg_sha]},
           "nn_npz_equals_lat_npz": nn_vs_lat, "data_pot": data_pot, "mc_pot": mc_pot, "pot_scale": data_pot / mc_pot,
           "data_pot_checks": pot, "flux_key_max_rel": flux_dev}
    rc = subprocess.run([sys.executable, str(_ND / "s5p_mc_truth_pred.py"), "--npz", str(d["lat"]),
                         "--expect-npz-sha256", lat_sha, "--out", str(d["truth"])]).returncode
    if rc != 0 or not d["truth"].is_file():
        raise Refuse(6, f"s5p_mc_truth_pred.py exited {rc}")
    rec["files"]["truth"] = [str(d["truth"]), sha256(d["truth"])]
    rec.update({"code_sha256": code_sha(), "seconds": round(time.time() - t0, 1)})
    write_json(d["receipt"], rec)
    print(json.dumps({"checked": X, "receipt": str(d["receipt"])}), flush=True)
    return 0


def playlist_paths(X: str) -> dict[str, str]:
    """Each playlist's products under <R> (relative), shared by the steps, the tables and the readers."""
    return {"flux": f"flux/runEventLoopMC_{X}.root", "nn": f"dumps/nn_{X}.npz", "lat": f"dumps/lat_{X}.npz",
            "bkg": f"dumps/lat_{X}_bkg.npz", "truth": f"truth/truth_{X}.npz", "receipt": f"inputs/check_{X}.json",
            "unf": f"unf/{X}"}


# ---------------------------------------------------------------- n0-split (job A)


def histnd_counts(cols, w, edges) -> np.ndarray:
    """unfold_nd_omnifold_unbinned.histnd's counts (np.histogramdd over the dump's edges), without its ROOT import."""
    counts, _ = np.histogramdd(np.column_stack(cols), bins=[np.asarray(e, float) for e in edges], weights=w)
    return counts


def truth_sum(mcgen, pass_truth, w_truth, edges) -> np.ndarray:
    """O: the binned truth-weight sum of the truth-passing signal rows, as s5c_unfold.unfold forms ofin."""
    m = np.asarray(pass_truth, bool)
    samp = np.column_stack([mcgen[m, i] for i in range(mcgen.shape[1])])
    o, _ = np.histogramdd(samp, bins=edges, weights=np.asarray(w_truth)[m])
    return o


def assign(rng: np.random.Generator, n: int, e: np.ndarray) -> np.ndarray:
    return rng.choice(len(e), size=n, p=e).astype(np.int8)


def n0_partition(lat: dict, bkg: dict, e: np.ndarray, seed: int) -> tuple[list[dict], list[dict], dict]:
    """One N0 partition of ALL's lateral inputs into len(e) pseudo-playlists (part 1 section 4). Returns the
    pseudo-npz arrays, the pseudo background arrays, and the assignment vectors (data, signal, background)."""
    rng = np.random.default_rng(seed)
    a = {"data": assign(rng, len(lat["measured"]), e), "signal": assign(rng, len(lat["MCgen"]), e),
         "background": assign(rng, len(bkg["bkg_reco"]), e)}
    edges = [np.asarray(lat[f"edges_{i}"], float) for i in range(int(lat["nedges"]))]
    o_all = truth_sum(lat["MCgen"], lat["pass_truth"], lat["w_truth"], edges)
    dn_all = np.asarray(lat["denom_nd"], float)
    npzs, bkgs = [], []
    for k in range(len(e)):
        sd, ss, sb = a["data"] == k, a["signal"] == k, a["background"] == k
        z = {key: np.asarray(lat[key]) for key in GLOBAL_KEYS}
        z.update({key: np.asarray(lat[key])[ss] for key in SIGNAL_KEYS})
        z.update({key: np.asarray(lat[key])[sd] for key in DATA_KEYS})
        z["data_pot"] = float(lat["data_pot"]) * float(e[k])
        o_k = truth_sum(z["MCgen"], z["pass_truth"], z["w_truth"], edges)
        with np.errstate(divide="ignore", invalid="ignore"):
            z["denom_nd"] = np.where(o_all > 0, dn_all * o_k / o_all, float(e[k]) * dn_all)
        b = {"bkg_reco": np.asarray(bkg["bkg_reco"])[sb], "bkg_w": np.asarray(bkg["bkg_w"])[sb]}
        b["bkg_nd"] = histnd_counts([b["bkg_reco"][:, i] for i in range(b["bkg_reco"].shape[1])], b["bkg_w"], edges)
        npzs.append(z)
        bkgs.append(b)
    return npzs, bkgs, a


def n0_paths(p: int, k: int) -> dict[str, str]:
    return {"npz": f"n0/p{p:02d}/n0_p{p:02d}_k{k:02d}.npz", "bkg": f"n0/p{p:02d}/n0_p{p:02d}_k{k:02d}_bkg.npz",
            "truth": f"n0/p{p:02d}/truth_p{p:02d}_k{k:02d}.npz", "unf": f"unf-n0/p{p:02d}/k{k:02d}",
            "receipt": f"n0/p{p:02d}/N0_p{p:02d}.json", "assign": f"n0/p{p:02d}/assign_p{p:02d}.npz"}


def run_n0_split(a) -> int:
    p = a.partition
    if not 1 <= p <= N_PART:
        raise Refuse(2, f"partition {p} outside 1..{N_PART}")
    paths = {k: [a.r / v for v in (n0_paths(p, j)[k] for j in range(len(PLAYLISTS)))] for k in ("npz", "bkg", "truth")}
    rec_path, asg_path = a.r / n0_paths(p, 0)["receipt"], a.r / n0_paths(p, 0)["assign"]
    fresh(rec_path, asg_path, *paths["npz"], *paths["bkg"], *paths["truth"])
    t0 = time.time()
    fr = flux_record(a.r)
    e = np.array([fr["exposure_share"][pl] for pl in PLAYLISTS], float)
    lat_p, lat_sha = staged(a.r, "mp1/lat_zero.npz")
    bkg_p, bkg_sha = staged(a.r, "mp1/lat_zero_bkg.npz")
    with np.load(lat_p, allow_pickle=True) as z:
        lat = {k: z[k] for k in z.files}
    with np.load(bkg_p, allow_pickle=True) as z:
        bkg = {k: z[k] for k in z.files if k != "meta"}
    npzs, bkgs, asg = n0_partition(lat, bkg, e / e.sum(), N0_SEED0 + p)
    rec_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(asg_path, **asg)
    pseudo = []
    for k, (z, b) in enumerate(zip(npzs, bkgs)):
        np.savez_compressed(paths["npz"][k], **z)
        zsha = sha256(paths["npz"][k])
        np.savez_compressed(paths["bkg"][k], **b, meta=json.dumps({"npz_sha256": zsha,
                                                                    "omnifile": f"n0:p{p:02d}:k{k:02d}"}))
        rc = subprocess.run([sys.executable, str(_ND / "s5p_mc_truth_pred.py"), "--npz", str(paths["npz"][k]),
                             "--expect-npz-sha256", zsha, "--out", str(paths["truth"][k])]).returncode
        if rc != 0 or not paths["truth"][k].is_file():
            raise Refuse(6, f"s5p_mc_truth_pred.py exited {rc} on pseudo-playlist {k}")
        pseudo.append({"k": k, "share": float(e[k] / e.sum()), "analogue": PLAYLISTS[k],
                       "npz": [str(paths["npz"][k]), zsha], "bkg": [str(paths["bkg"][k]), sha256(paths["bkg"][k])],
                       "truth": [str(paths["truth"][k]), sha256(paths["truth"][k])],
                       "rows": {"data": int(np.sum(asg["data"] == k)), "signal": int(np.sum(asg["signal"] == k)),
                                "background": int(np.sum(asg["background"] == k))}})
    write_json(rec_path, {"schema": "fd-rpd-n0/1", "partition": p, "seed": N0_SEED0 + p, "playlists": list(PLAYLISTS),
                          "inputs": {"lat_zero": [str(lat_p), lat_sha], "lat_zero_bkg": [str(bkg_p), bkg_sha],
                                     "flux_record": sha256(a.r / "flux/F1.json")},
                          "assign": [str(asg_path), sha256(asg_path)], "pseudo": pseudo,
                          "code_sha256": code_sha(), "seconds": round(time.time() - t0, 1)})
    print(json.dumps({"n0_partition": p, "receipt": str(rec_path)}), flush=True)
    return 0


# ---------------------------------------------------------------- unfold (jobs A and B)


def unfold_target(a) -> tuple[str, str, str, str, Path, str]:
    """(npz, npz sha, bkg, bkg sha, out dir, tag) for the unfold asked for, from its receipt."""
    if a.what == "playlist":
        X = a.playlist
        rec = json.loads((a.r / playlist_paths(X)["receipt"]).read_text())
        if (rec.get("schema"), rec.get("playlist")) != ("fd-rpd-inputs/1", X):
            raise Refuse(4, f"not {X}'s check receipt")
        (lat, ls), (bkg, bs) = rec["files"]["lat_npz"], rec["files"]["lat_bkg"]
        return lat, ls, bkg, bs, a.r / playlist_paths(X)["unf"], f"rpd_{X}"
    if a.what == "n0":
        rec = json.loads((a.r / n0_paths(a.partition, 0)["receipt"]).read_text())
        if (rec.get("schema"), rec.get("partition")) != ("fd-rpd-n0/1", a.partition):
            raise Refuse(4, f"not partition {a.partition}'s N0 receipt")
        q = rec["pseudo"][a.k]
        if q["k"] != a.k:
            raise Refuse(4, f"N0 receipt row {a.k} is not pseudo-playlist {a.k}")
        (lat, ls), (bkg, bs) = q["npz"], q["bkg"]
        return lat, ls, bkg, bs, a.r / n0_paths(a.partition, a.k)["unf"], f"rpd_n0_p{a.partition:02d}_k{a.k:02d}"
    lat, ls = staged(a.r, "5b/dumps/lat_PC.npz")
    bkg, bs = staged(a.r, "5b/dumps/lat_PC_bkg.npz")
    return str(lat), ls, str(bkg), bs, a.r / "unf-k2", "rpd_k2_PC"


def run_unfold(a) -> int:
    lat, ls, bkg, bs, out, tag = unfold_target(a)
    targets = pi.unfold_products(out, tag, a.pairs)
    fresh(*targets)
    require(Path(lat), ls, "unfold npz")
    require(Path(bkg), bs, "unfold background dump")
    cmd = [sys.executable, str(_ND / "s5p_numerics.py"), "--npz", lat, "--bkg", bkg, "--expect-npz-sha256", ls,
           "--expect-bkg-sha256", bs, "--config", "R", "--iters", "5", "--construction", "data", f"--pairs={a.pairs}",
           "--estimator-seed", "42", "--tag", tag, "--threads", str(a.threads), "--out", str(out)]
    rc = subprocess.run(cmd).returncode
    missing = [str(p) for p in targets if not p.is_file()]
    if rc == 0 and missing:
        raise Refuse(6, f"s5p_numerics.py exited 0 without {missing}")
    return rc


# ---------------------------------------------------------------- main


def build_args(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("stage", "flux", "check", "n0-split", "unfold"):
        s = sub.add_parser(name)
        s.add_argument("--r", type=Path, required=True)
        s.add_argument("--deploy", type=Path, default=DEPLOY)
        if name == "stage":
            s.add_argument("--allow-no-noatime", action="store_true", help=argparse.SUPPRESS)
        if name in ("check",):
            s.add_argument("--playlist", choices=PLAYLISTS, required=True)
        if name == "n0-split":
            s.add_argument("--partition", type=int, required=True)
        if name == "unfold":
            s.add_argument("--what", choices=("playlist", "n0", "k2"), required=True)
            s.add_argument("--playlist", choices=PLAYLISTS)
            s.add_argument("--partition", type=int)
            s.add_argument("--k", type=int)
            s.add_argument("--pairs", required=True)
            s.add_argument("--threads", type=int, default=32)
    a = ap.parse_args(argv)
    if a.cmd == "unfold":
        need = {"playlist": ("playlist",), "n0": ("partition", "k"), "k2": ()}[a.what]
        extra = [k for k in ("playlist", "partition", "k") if getattr(a, k) is not None and k not in need]
        if any(getattr(a, k) is None for k in need) or extra:
            ap.error(f"--what {a.what} takes exactly {need}")
    return a


def main(argv=None) -> int:
    a = build_args(argv)
    try:
        return {"stage": run_stage, "flux": run_flux, "check": run_check, "n0-split": run_n0_split,
                "unfold": run_unfold}[a.cmd](a)
    except Refuse as e:
        print(f"[rpd-inputs] refusing: {e}", file=sys.stderr, flush=True)
        return e.code


if __name__ == "__main__":
    sys.exit(main())

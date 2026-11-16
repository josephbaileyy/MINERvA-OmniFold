#!/usr/bin/env python3
"""Kish effective sample size of configuration (e)'s final unfolded event weights, on the 16 reported cells.

The referee's major issue 7 (interim GPT report; the director's task of 2026-11-10, approved by Joseph). The central
data product of configuration (e), ``data_b-_j-.npz`` (sha256 fb5cc679..., s1_assemble.py:49), stores only the
binned cross section: ``s5c_unfold.unfold`` computes the push weights in memory and discards them (s5c_unfold.py:124,
:138-146 @ abdc88c5). This tool reruns that one unfold through the same functions at the producer's code commit
(abdc88c5, whose ten module digests equal the product's code record), captures the push weights in memory, and:

* BINDING: the re-made ``xsec_flat`` must equal fb5cc679's byte for byte. If it differs at all, no ESS is computed
  or written: STOP.json records the difference and the tool exits 8.
* then computes, per reported cell R00-R15 and globally, the Kish n_eff = (sum w)^2 / sum w^2 and the weight-tail
  summaries of two weight definitions (the director's ruling 2):
  (B) each simulated event's contribution to the reported cell integral f_R = sum_f xsec_f vol_f, i.e.
      c_i = 1e4 wpush_i w_truth_i / (comp_f flux_f N POT) for the event's fine cell f (the printed number);
  (A) the final per-event weight the result histograms, wpush_i w_truth_i (s5c_unfold.py:138), beside it.
  The prior weight w_truth alone is printed as a labelled reference.

Reads: the three shared inputs once each through O_NOATIME, with os.stat before and after, into a node-local
staging directory (/dev/shm) that is removed at exit; every later read is of the copies. A Python audit hook refuses
any other read under /pscratch or /global/cfs outside --out-root. Writes: the re-made product (``--out/product``),
ess.json (or STOP.json / FAILED.json) and nothing else.

MEASURES: the Kish ESS and weight concentration of the reported result's simulated events under (A) and (B).
CANNOT AUTHORIZE: any change to the result or its covariance, an uncertainty, or any coverage reading.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

SCHEMA = "ess-e-central/1"
CODE_PIN = "abdc88c52b909cfc1eb658ae97bd9defc8f640e7"   # the producer's code (RE1-REPORT.md:31; meta code record)
MAIN_PIN = "025459c8f4a92d65239cecc3cc3a09cd5de13c15"   # where the H2 definition and the data product are read
# name: (path, sha256, bytes); the bytes from fd/receipts-ref-g1/preconditions/listing.json
SHARED = {
    "npz": ("/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz",
            "07fccc1abc7204bc29349b4ba96850986fe91e909e83fc54e8d1a6b3922a649f", 1548438020),
    "bkg": ("/pscratch/sd/j/josephrb/s5c-20260924/runs/p2/bkg_dump.npz",
            "2addac8f26055c5ed69862e7afe29e12ac51dbe23a8d6eeed79d71bec9d82955", 16017201),
    "ref": ("/pscratch/sd/j/josephrb/s5p-20260926/runs/s2/num/data/data_b-_j-.npz",
            "fb5cc6798b97b5902ad8f0fecbc49990271f7772f98d3063c1dc8596340e680c", 95564),
}
REPO = {
    "h2": ("nd-unfolding/pv-ladder/readouts/h2_definition.json",
           "b67907615fe2e903e60ae6caa1c141fa007676c0a1b3ae9f42490d331bfdda89"),
    "dp": ("docs/orchestration/state/measurement-paper/5d-community-20261024/fd/with-cpl/data-product/"
           "fd_data_product_cpl.json", "d6752d2c64aad4426375c03a3171a7015f031e2027928cf89aea6cd3bbb84d50"),
}
FINE_MAP_SHA256 = "930326a3a7c0852d4047b5468d8ea3b63d046b896e4a4de1557e29f95102e18c"   # s1_assemble.py:44
# the product's code record (its meta code_sha256), each equal to the file at CODE_PIN; plus the grid module
CODE_SHA = {
    "nd-unfolding/s5n_pseudo.py": "8981f97b96b418cfe46f1e940cb120f174053d7d3429f3b0b01a229c6c02ee6c",
    "nd-unfolding/s5c_pseudo.py": "d81d4f46fb55f25fdf7ce2e4b9a9a63bf876beaf754bdc250eee974579e11f5d",
    "nd-unfolding/s5c_unfold.py": "510d749a2e82fa448de6172753ae2adc9ebd81a89d4f18bf76beb5faa8bb3968",
    "nd-unfolding/omnifold_nn_core.py": "24f87f119073c4f125c2f753310507d4375b6f8a1b7751e59d3615dd50e90582",
    "nd-unfolding/xsec_nd.py": "454001f3c9ac3aa6485d184aadb8aba65dd71dba124816962b9c3b6344920fa5",
    "2d-unfolding/unfold_2d_omnifold_unbinned.py": "8ebe0277ee4c277f6f697712a901b14d6ba24ed5dcadfc3c66b29276acf81b5e",
    "nd-unfolding/s5e_candidate.py": "bda8c48ce2365e173bbba083b18233d6f6b7c2dfbab5179156073860c8281ec7",
    "nd-unfolding/s5e_deform.py": "6726ff99c7787d1ee6dff7fa5d08df88f9df76285d98c4c462f964ac6164779f",
    "nd-unfolding/s5e_trace.py": "c47e9dd3feef9eab323e40f4e0da770ad67e86431a1ce95f99a10007decc66c1",
    "nd-unfolding/s5p_numerics.py": "9d7c12322200dc2dca2944883ad0f51e41e58a70d5ac3d87991c3bb85611630a",
    "nd-unfolding/s5p_stage1_inspect.py": "26569afc0da46f21167e0908014712cd800c1e14ac63a4b245a0b493c76d3d71",
}
MODULES = ("s5p_numerics", "s5c_unfold", "omnifold_nn_core", "xsec_nd", "s5n_pseudo", "s5e_trace", "s5e_candidate",
           "s5c_pseudo", "s5e_deform", "unfold_2d_omnifold_unbinned", "s5p_stage1_inspect")
THREADS = 32
# the meta fields that differ on a perfect rerun (the s5p recovery criterion, PROCEDURE-20261005 section 3)
PER_RUN = ("slurm_job", "slurm_step", "seconds_load", "seconds_unfold")
N_CELLS = 16
PROTECTED = ("/pscratch", "/global/cfs")
RC_STOP, RC_FAILED = 8, 9


class Failed(Exception):
    """A check failed before the binding comparison could be made: FAILED.json, rc 9."""


# --------------------------------------------------------------------------------------------- read discipline

_GUARD = {"active": False, "protected": (), "allowed": ()}


def _under(p: str, roots) -> bool:
    return any(p == r or p.startswith(r.rstrip("/") + "/") for r in roots)


def _audit(event, args):
    if event != "open" or not _GUARD["active"]:
        return
    path, _mode, flags = args
    if not isinstance(path, (str, bytes, os.PathLike)):
        return
    if isinstance(flags, int) and (flags & os.O_ACCMODE) == os.O_WRONLY:
        return
    p = os.path.realpath(os.fsdecode(path))
    if not _under(p, _GUARD["protected"]) or _under(p, _GUARD["allowed"]):
        return
    if isinstance(flags, int) and flags & _GUARD["noatime"]:
        return
    raise PermissionError(f"ess_capture: a plain read of {p} (protected trees are read only through O_NOATIME)")


def install_guard(protected, allowed, noatime: int) -> None:
    sys.addaudithook(_audit)
    _GUARD.update(active=True, noatime=noatime, protected=tuple(os.path.realpath(r) for r in protected),
                  allowed=tuple(os.path.realpath(r) for r in allowed))


def stat_record(path: str) -> dict:
    s = os.stat(path)
    return {"size": s.st_size, "ino": s.st_ino, "mtime_ns": s.st_mtime_ns, "atime_ns": s.st_atime_ns}


def copy_noatime(src: str, dest: Path, noatime: int) -> str:
    """One O_NOATIME pass over ``src`` into ``dest`` (new); the sha256 taken in that pass, and the copy re-hashed."""
    h = hashlib.sha256()
    fd = os.open(src, os.O_RDONLY | noatime)
    with os.fdopen(fd, "rb") as fh, open(dest, "xb") as fo:
        while block := fh.read(1 << 24):
            h.update(block)
            fo.write(block)
    got = h.hexdigest()
    if sha256_file(dest) != got:
        raise Failed(f"the copy {dest} differs from {src}")
    return got


def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while block := fh.read(1 << 24):
            h.update(block)
    return h.hexdigest()


def stage(shared: dict, stage_dir: Path, noatime: int, check_atime: bool) -> tuple[dict, dict]:
    """Each shared input once through O_NOATIME; stat before and after must agree (atime included on the cluster)."""
    copies, records = {}, {}
    for name, (src, pin, nbytes) in shared.items():
        before = stat_record(src)
        dest = stage_dir / f"{name}_{Path(src).name}"
        got = copy_noatime(src, dest, noatime)
        after = stat_record(src)
        records[name] = {"path": src, "before": before, "after": after, "copy_digest": got}
        if got != pin:
            raise Failed(f"{name}: digest {got} is not the pin {pin}")
        if before["size"] != nbytes:
            raise Failed(f"{name}: {before['size']} bytes, pinned {nbytes}")
        keys = ("size", "ino", "mtime_ns") + (("atime_ns",) if check_atime else ())
        if any(before[k] != after[k] for k in keys):
            raise Failed(f"{name}: stat changed across the read: {before} -> {after}")
        copies[name] = dest
    return copies, records


# --------------------------------------------------------------------------------------------------- statistics


def summary(v: np.ndarray) -> dict:
    """Kish n_eff and the weight tail of one event set's weights ``v`` (float64). Percentiles are numpy's default
    (linear interpolation) and are printed relative to the set's mean weight; the max-weight share is max v / sum v."""
    v = np.asarray(v, np.float64)
    n = int(v.size)
    if n == 0:
        return {"n": 0}
    s, s2 = float(v.sum()), float(np.square(v).sum())
    mean = s / n
    p99, p999 = (float(x) for x in np.percentile(v, [99.0, 99.9]))
    return {
        "n": n, "sum": s, "sum_sq": s2,
        "n_eff": s * s / s2 if s2 > 0 else 0.0,
        "n_eff_over_n": (s * s / s2) / n if s2 > 0 else 0.0,
        "mean": mean,
        "p99_over_mean": p99 / mean if mean != 0 else None,
        "p999_over_mean": p999 / mean if mean != 0 else None,
        "max_over_mean": float(v.max()) / mean if mean != 0 else None,
        "max_share": float(v.max()) / s if s != 0 else None,
        "min": float(v.min()), "n_negative": int((v < 0).sum()), "n_zero": int((v == 0).sum()),
    }


def kinds(sel: np.ndarray, wa: np.ndarray, wb: np.ndarray, wt: np.ndarray, noreco: np.ndarray) -> dict:
    a, b = wa[sel], wb[sel]
    nr = noreco[sel]
    return {
        "B_contribution": summary(b), "A_final_weight": summary(a), "prior_w_truth": summary(wt[sel]),
        "no_reco_partner": {"n": int(nr.sum()),
                            "share_of_sum_A": float(a[nr].sum() / a.sum()) if a.size and a.sum() else None,
                            "share_of_sum_B": float(b[nr].sum() / b.sum()) if b.size and b.sum() else None},
    }


# ------------------------------------------------------------------------------------------------------ the run


def git_show(deploy: Path, rev: str, rel: str, pin: str) -> bytes:
    out = subprocess.run(["git", "-C", str(deploy), "show", f"{rev}:{rel}"], capture_output=True, check=False)
    if out.returncode != 0:
        raise Failed(f"git show {rev}:{rel}: rc {out.returncode} {out.stderr.decode()[:200]}")
    got = hashlib.sha256(out.stdout).hexdigest()
    if got != pin:
        raise Failed(f"{rel} at {rev[:9]} has sha256 {got}, pinned {pin}")
    return out.stdout


def load_npz(path: Path) -> tuple[np.ndarray, np.ndarray, dict]:
    with np.load(path, allow_pickle=False) as z:
        return np.array(z["xsec_flat"]), np.array(z["shape"]), json.loads(str(z["meta"]))


def strip_per_run(meta: dict) -> dict:
    m = {k: v for k, v in meta.items() if k not in PER_RUN}
    if isinstance(m.get("refinement"), dict):
        m["refinement"] = {k: v for k, v in m["refinement"].items() if k != "seconds"}
    return m


def run(a, cfg: dict) -> int:
    t_start = time.time()
    deploy, out = a.deploy.resolve(), a.out
    record = {"schema": SCHEMA, "tool_digest": sha256_file(Path(__file__).resolve()), "argv": sys.argv,
              "host": socket.gethostname(), "slurm_job": os.environ.get("SLURM_JOB_ID"),
              "python": platform.python_version(), "code_pin": cfg["code_pin"], "main_pin": cfg["main_pin"]}
    head = subprocess.run(["git", "-C", str(deploy), "rev-parse", "HEAD"], capture_output=True, text=True)
    if head.stdout.strip() != cfg["code_pin"]:
        raise Failed(f"deploy HEAD {head.stdout.strip()} is not {cfg['code_pin']}")
    for rel, pin in cfg["code_sha"].items():
        if sha256_file(deploy / rel) != pin:
            raise Failed(f"{rel} in the deploy is not the pinned file")
    for p in (deploy / "nd-unfolding", deploy / "2d-unfolding"):
        sys.path.insert(0, str(p))
    import lightgbm
    import omnifold_nn_core as onc
    import s5c_unfold
    import s5e_trace
    import s5p_numerics
    import s5p_stage1_inspect as s1
    import xsec_nd
    record["versions"] = {"numpy": np.__version__, "lightgbm": lightgbm.__version__}
    if s5c_unfold.onc is not onc:
        raise Failed("s5c_unfold's omnifold_nn_core is another module object")

    # the two committed operands of the 16 cells, from the main pin
    h2 = json.loads(git_show(deploy, cfg["main_pin"], *cfg["repo"]["h2"]))
    dp = json.loads(git_show(deploy, cfg["main_pin"], *cfg["repo"]["dp"]))

    stage_dir = Path(a.stage_dir)
    stage_dir.mkdir(mode=0o700)          # refuses an existing directory
    try:
        copies, stats = stage(cfg["shared"], stage_dir, cfg["noatime"], cfg["check_atime"])
        record["reads"] = stats

        # ---- capture: pass-through wrappers; the numbers are the producer's own
        loops, unfolds = [], []
        real_loop, real_unfold = onc.omnifold_loop, s5c_unfold.unfold

        def loop(*args, **kw):
            res = real_loop(*args, **kw)
            loops.append(res)
            return res

        def unfold(inputs, config, seed, threads, iters):
            xs, rec = real_unfold(inputs, config, seed, threads, iters)
            unfolds.append((inputs, xs))
            return xs, rec

        onc.omnifold_loop, s5c_unfold.unfold = loop, unfold
        argv = ["--npz", str(copies["npz"]), "--bkg", str(copies["bkg"]),
                "--expect-npz-sha256", cfg["shared"]["npz"][1], "--expect-bkg-sha256", cfg["shared"]["bkg"][1],
                "--config", "R", "--iters", "5", "--construction", "data", "--pairs=-:-", "--tag", "data",
                "--threads", str(cfg["threads"]), "--out", str(out / "product")]
        record["producer_argv"] = argv
        t0 = time.time()
        rc = s5p_numerics.main(argv)
        record["seconds_producer"] = round(time.time() - t0, 3)
        onc.omnifold_loop, s5c_unfold.unfold = real_loop, real_unfold
        if rc != 0:
            raise Failed(f"s5p_numerics.main returned {rc}")
        if len(loops) != 1 or len(unfolds) != 1:
            raise Failed(f"{len(loops)} OmniFold loops and {len(unfolds)} unfolds ran, expected one each")
        # every producer module the run used came from the deploy (checked after the run: the refinement and the
        # R install import theirs lazily)
        for name in cfg["modules"]:
            mod = sys.modules.get(name)
            if mod is None or not Path(mod.__file__).resolve().is_relative_to(deploy):
                raise Failed(f"module {name} is not loaded from the deploy ({getattr(mod, '__file__', None)})")

        # ---- BINDING: the re-made xsec_flat byte for byte against fb5cc679's
        product = out / "product" / "data_b-_j-.npz"
        rx, rshape, rmeta = load_npz(product)
        fx, fshape, fmeta = load_npz(copies["ref"])
        inputs, xs = unfolds[0]
        same = (rx.dtype == fx.dtype and rx.shape == fx.shape and rx.tobytes() == fx.tobytes()
                and np.array_equal(rshape, fshape))
        captured = xs.ravel(order="C")
        binding = {"remade_digest": sha256_file(product), "reference_digest": cfg["shared"]["ref"][1],
                   "xsec_flat_bytes_equal": bool(same),
                   "captured_equals_remade": bool(captured.dtype == rx.dtype and captured.tobytes() == rx.tobytes()),
                   "n_entries": int(fx.size)}
        sm_r, sm_f = strip_per_run(rmeta), strip_per_run(fmeta)
        record["meta_compare"] = {"equal_except_per_run_fields": sm_r == sm_f,
                                  "per_run_fields": list(PER_RUN) + ["refinement.seconds"],
                                  "differing_keys": sorted(k for k in set(sm_r) | set(sm_f) if sm_r.get(k) != sm_f.get(k))}
        record["binding"] = binding
        if not (same and binding["captured_equals_remade"]):
            if rx.shape == fx.shape:
                diff = rx != fx
                binding.update(n_differ=int(diff.sum()),
                               max_abs=float(np.max(np.abs(rx - fx))) if diff.any() else 0.0)
            record["verdict"] = "STOP: the re-made xsec_flat is not byte-identical to fb5cc679's; no ESS is computed"
            write_json(out / "STOP.json", record)
            return RC_STOP

        # ---- the event-level mapping, checked against the producer's own binning (s5c_unfold.py:136-145)
        loop_pull, wpush = loops[0]
        d = inputs
        m = np.asarray(d["pass_truth"], bool)
        edges = d["edges"]
        samp = np.column_stack([d["MCgen"][m, i] for i in range(d["MCgen"].shape[1])])
        wt = np.asarray(d["w_truth"])[m]
        if wpush.shape[0] != int(m.sum()):
            raise Failed("the push weights do not align with the truth-selected events")
        unf, _ = np.histogramdd(samp, bins=edges, weights=wpush * d["w_truth"][m])
        ofin, _ = np.histogramdd(samp, bins=edges, weights=d["w_truth"][m])
        dn = d["denom_nd"]
        comp = np.zeros_like(ofin)
        nz = dn > 0
        comp[nz] = ofin[nz] / dn[nz]
        xs2, good = xsec_nd.extract_cross_section_nd(unf, comp, d["flux"], float(d["data_pot"]),
                                                     float(d["n_nucleons"]), edges)
        checks = {"recomputed_xs_bytes_equal": bool(xs2.tobytes() == xs.tobytes())}
        fine_edges_equal = all(np.array_equal(np.asarray(e, float), np.asarray(s1.FINE[ax], float))
                               for e, ax in zip(edges, s1.AXES))
        checks["edges_equal_fine_grid"] = bool(fine_edges_equal and len(edges) == len(s1.AXES))
        fi = s5e_trace.flat_index(samp, edges)
        nfine = int(np.prod(xs.shape))
        counts, _ = np.histogramdd(samp, bins=edges)
        checks["event_index_counts_equal"] = bool(np.array_equal(
            np.bincount(fi[fi >= 0], minlength=nfine).astype(np.float64), counts.ravel(order="C")))
        cmap, n_boxes = s1.coarse_map(s1.H2_EDGES)
        hm = np.asarray(h2["h2_to_reporting_cell"], int)
        if hm.size != n_boxes or int(h2["n_reporting_cells"]) != N_CELLS:
            raise Failed("the H2 definition does not map its boxes onto 16 cells")
        fm = np.where(cmap >= 0, hm[cmap], -1).astype("<i4")
        checks["fine_map_digest_equal"] = hashlib.sha256(fm.tobytes()).hexdigest() == cfg["fine_map_sha"] \
            == h2["fine_map_sha256_int32le"]
        vol = s1.fine_volume()
        checks["volume_equal"] = bool(np.allclose(vol, xsec_nd._bin_volume(xs.shape, edges).ravel(order="C"),
                                                  rtol=1e-13, atol=0.0))
        if not all(checks.values()):
            record["checks"] = checks
            raise Failed(f"a mapping check failed: {checks}")
        xflat = xs.ravel(order="C")
        f_cells = np.array([float((xflat * vol)[fm == c].sum()) for c in range(N_CELLS)])
        f_dp = np.asarray(dp["f"], float)
        checks["f_vs_data_product_max_rel"] = float(np.max(np.abs(f_cells / f_dp - 1)))

        # ---- (B): each event's contribution to its cell integral; (A): the final weight
        flux_b = xsec_nd._broadcast_along(d["flux"], xs.ndim, 0)
        den = (comp * flux_b * float(d["n_nucleons"]) * float(d["data_pot"])).ravel(order="C")
        goodf = good.ravel(order="C")
        inside = fi >= 0
        fic = np.where(inside, fi, 0)
        used = inside & goodf[fic]
        wa = np.asarray(wpush, np.float64) * np.asarray(wt, np.float64)
        wb = np.zeros_like(wa)
        wb[used] = 1.0e4 * wa[used] / den[fic[used]]
        cell = np.where(used, fm[fic], -1)
        noreco = ~np.asarray(d["pass_reco"], bool)[m]
        sums = np.array([wb[cell == c].sum() for c in range(N_CELLS)])
        checks["cell_sum_vs_f_max_rel"] = float(np.max(np.abs(sums / f_cells - 1)))
        checks["events_in_cells_with_zero_denominator"] = int((inside & ~goodf[fic] & (fm[fic] >= 0)).sum())
        if checks["f_vs_data_product_max_rel"] > 1e-12 or checks["cell_sum_vs_f_max_rel"] > 1e-9:
            record["checks"] = checks
            raise Failed(f"the cell sums do not reproduce the reported f: {checks}")
        record["checks"] = checks

        cells = {}
        for c in range(N_CELLS):
            cells[f"R{c:02d}"] = kinds(cell == c, wa, wb, wt, noreco)
        reported = cell >= 0
        record["cells"] = cells
        record["global"] = {
            "reported_16_cells": kinds(reported, wa, wb, wt, noreco),
            "all_fine_cells_with_nonzero_denominator": kinds(used, wa, wb, wt, noreco),
            "whole_truth_selected_ensemble_A_only": {"A_final_weight": summary(wa), "prior_w_truth": summary(wt),
                                                     "no_reco_partner_n": int(noreco.sum())},
        }
        ref_ref = fmeta.get("refinement", {})
        rem_ref = rmeta.get("refinement", {})
        record["data_side_refinement"] = {
            "label": ("refinement.n_eff_refined from the product meta: the Kish n_eff of the refined DATA-side "
                      "weights that feed step 1 (s5n_pseudo.py:302 @ abdc88c5), global only. It describes the "
                      "measured sample after background subtraction, NOT the unfolded simulated ensemble."),
            "reference_meta": {k: ref_ref.get(k) for k in ("n_eff_refined", "n_eff_signed_abs")},
            "remade_meta": {k: rem_ref.get(k) for k in ("n_eff_refined", "n_eff_signed_abs")},
        }
        record["definitions"] = DEFINITIONS
        record["seconds_total"] = round(time.time() - t_start, 3)
        record["verdict"] = "PASS: the re-made xsec_flat equals fb5cc679's byte for byte; ESS computed"
        write_json(out / "ess.json", record)
        return 0
    finally:
        shutil.rmtree(stage_dir, ignore_errors=True)


DEFINITIONS = {
    "kish": "n_eff = (sum_i w_i)^2 / sum_i w_i^2 over the events of the set; n_eff_over_n = n_eff / n",
    "B_contribution": ("the printed number: w_i = 1e4 wpush_i w_truth_i / (comp_f flux_f N_nucleons POT_data) for "
                       "the event's fine cell f, so that sum_{i in R} w_i = f_R = sum_{f in R} xsec_f vol_f, the "
                       "reported cell integral (xsec_nd.py:77-82, s1_assemble.py:120-122); it carries the per-fine-"
                       "cell completeness and the flux of the event's pT bin"),
    "A_final_weight": "w_i = wpush_i w_truth_i, the weight the result histograms (s5c_unfold.py:138 @ abdc88c5)",
    "prior_w_truth": "w_i = w_truth_i, the simulation's prior weight on the same events (a reference, not asked)",
    "events": ("simulated events passing the truth selection (pass_truth) whose truth coordinates fall in a fine "
               "cell of the reported cell with a nonzero denominator (xsec_nd.py:80 'good'); events in fine cells "
               "with a zero denominator contribute nothing to f and are counted in checks"),
    "regressor": ("every truth-selected event carries a step-2 push weight (omnifold_nn_core.py:266 @ abdc88c5), "
                  "including events with no reconstructed partner, whose step-1 weight was filled by the "
                  "regressor (:260); they are included in A and B, and no_reco_partner gives their number and "
                  "share of each sum"),
    "normalization": ("Kish n_eff is invariant to a constant scale, so the 1e4, N_nucleons, POT_data and any constant "
                      "MC normalization inside w_truth cancel; the per-cell factors of B (completeness, flux by pT "
                      "bin) do not cancel, which is what separates B from A"),
    "tails": ("p99_over_mean and p999_over_mean: numpy.percentile (linear) at 99 and 99.9 of the set's weights, "
              "divided by the set's mean weight; max_share: the largest single weight over the set's sum"),
}


def write_json(path: Path, obj: dict) -> None:
    tmp = path.with_name(path.name + ".partial")
    tmp.write_text(json.dumps(obj, indent=1, sort_keys=False, default=str) + "\n")
    os.replace(tmp, path)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--deploy", type=Path, required=True, help="a clean clone at CODE_PIN")
    ap.add_argument("--out", type=Path, required=True, help="a new directory under --out-root")
    ap.add_argument("--out-root", type=Path, required=True, help="the job's $OUT: the only allowed protected root")
    ap.add_argument("--stage-dir", required=True, help="a new node-local directory, e.g. /dev/shm/ess-<job>")
    ap.add_argument("--fixture", type=Path, default=None, help="TESTS ONLY: pins and paths from a JSON; refused in Slurm")
    a = ap.parse_args(argv)
    cfg = {"code_pin": CODE_PIN, "main_pin": MAIN_PIN, "shared": SHARED, "repo": REPO, "code_sha": CODE_SHA,
           "fine_map_sha": FINE_MAP_SHA256, "modules": MODULES, "threads": THREADS, "protected": PROTECTED,
           "noatime": getattr(os, "O_NOATIME", None), "check_atime": True}
    if a.fixture is not None:
        if os.environ.get("SLURM_JOB_ID"):
            print("ess_capture: --fixture is refused inside a Slurm job", file=sys.stderr)
            return 2
        fx = json.loads(a.fixture.read_text())
        cfg.update({k: v for k, v in fx.items() if k != "shared" and k != "repo"})
        cfg["shared"] = {k: tuple(v) for k, v in fx.get("shared", {}).items()} or SHARED
        cfg["repo"] = {k: tuple(v) for k, v in fx.get("repo", {}).items()} or REPO
    if cfg["noatime"] is None:
        print("ess_capture: O_NOATIME is not available: refusing a plain read", file=sys.stderr)
        return 2
    a.out.mkdir(parents=True)            # refuses an existing --out
    out_root = os.path.realpath(a.out_root)
    if not os.path.realpath(a.out).startswith(out_root.rstrip("/") + "/"):
        print("ess_capture: --out is not under --out-root", file=sys.stderr)
        return 2
    install_guard(cfg["protected"], [out_root], cfg["noatime"])
    try:
        return run(a, cfg)
    except Failed as e:
        write_json(a.out / "FAILED.json", {"schema": SCHEMA, "verdict": f"FAILED: {e}", "argv": sys.argv})
        print(f"ess_capture: FAILED: {e}", file=sys.stderr)
        return RC_FAILED


if __name__ == "__main__":
    sys.exit(main())

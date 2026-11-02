#!/usr/bin/env python3
"""GENCMP amendment E (state/measurement-paper/5d-community-20261024/FD-GENCMP-AMENDMENT-E-DECLARATION.md): Stage G's
diagnostics recomputed on the "CH, analysis definitions" predictions of GENCMP step B (FD-GENCMP-REPORT.md section
2.2, #648), after a control that reproduces the committed ones on the old predictions.

Subcommands, each refusing to overwrite what it writes:

* ``stage``        O_NOATIME copies of every pscratch input into <run>/inputs/, laid out as under $P, each checked
                   against fd/gencmp-e/INPUTS.sha256 with its atime compared before and after. Every later step reads
                   the copies, so no tool opens a pscratch original.
* ``materialize``  the four predictions of the corner "CH, analysis definitions" as fine-grid npz files in
                   <run>/pred/, from step B's rebuilt products by fd_gencmp's own seed_mean and combine (the same
                   functions fd_gencmp.py defs ran), with MnvTune v1's file copied unchanged and one SHA256SUMS over
                   the five. Control E0: each prediction integrates to defs.json's analysis-definitions g, and its
                   two chi2 are defs.json's, to 1e-12 relative.
* ``chain``        for each prediction set (``old``, Stage G's own; then ``chdefs``) and each arm (``nopl``: C_resp;
                   ``with``: C_resp + C_PL5D), Stage G, G-DIAG, G-FOLLOWUP, G-SENS2 and the flux bootstrap, each a
                   subprocess of its bound tool with the upstream readouts' sha256 as its pins
                   (fd_cpl_addition.Chain), then the three figures and their independent check.
                   R0 (old set, each downstream step and the figures on the committed upstream readouts): every
                   readout is the committed one in structure and numbers (and strings, in the with arm), but argv,
                   code_sha256 and the extra block's file; every figure sidecar is the committed one but argv, code and
                   versions, and its PDF the same bytes. The chdefs set runs only once R0 has held in both arms.
                   XC (chdefs set): each prediction's g and its total and shape-only chi2 in Stage G's readout are
                   defs.json's, in both arms.

MEASURES: Stage G's arithmetic on the declared predictions. CANNOT AUTHORIZE: a reading, a Table IV or paper edit, or a
claim (the declaration's section 0).
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import sys
import zipfile
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
_REPO = _ND.parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import fd_cpl_addition as A  # noqa: E402  (Chain, Paths, step_argv, extra, compare_numbers, compare_strings, ...)
import fd_g_compare as fg  # noqa: E402  (PREDICTIONS, PINS, GIBUU_CELLS)
import fd_gencmp as gc  # noqa: E402  (seed_mean, combine, integrate, chi2_pair, read_noatime, load_pins, LABELS)
import fd_gencmp_kin as kin  # noqa: E402  (SEEDS)
import s1_assemble as sa  # noqa: E402  (s1.AXES, s1.FINE)

FD = "docs/orchestration/state/measurement-paper/5d-community-20261024"
INPUTS = _REPO / FD / "fd/gencmp-e/INPUTS.sha256"
DEFS = _REPO / FD / "fd/gencmp/readout/defs.json"
DEFS_SHA256 = "544f4f4343095b5e78b59e0782ac3ce5ef5974b2e24dbb59be3708b5937556f8"
SCRATCH = Path("/pscratch/sd/j/josephrb")
REBUILD = "gencmp-20261101/b/out"            # step B's rebuilt products, relative to $P
TUNE = fg.PREDICTIONS[-1]                     # MnvTune v1: the analysis MC truth, unchanged (declaration section 2)
CH_DEFS = "CH, analysis definitions"
SETS = ("old", "chdefs")
ARMS = ("nopl", "with")
STEPS = ("g", "g_diag", "g_followup", "g_sens2", "flux_boot")
R0_EXCLUDE = ("/argv", "/code_sha256", "/extra_block/file")    # the extra block's path names where it was read
TOL = 1e-12

# The corner's four predictions: Stage G's names, cells and order, so every name-keyed rule of the bound tools holds.
# ``src`` is the step B sample (or the carbon and hydrogen pair combined 12:1 per nucleon); ``qualifiers`` are the
# label's parts the figure legend must draw (fd_g_figures.PREDICTION_SETS["gencmp-chdefs"] carries the same strings).
CHDEFS = (
    dict(name="genie_cv", src=("genie_cv",), cells="all",
         label=f"GENIE 2.12.10 CV, no MEC; {CH_DEFS} (rebuilt, GENCMP step B)"),
    dict(name="genie_mec", src=("genie_mec",), cells="all",
         label=f"GENIE 2.12.10 + Valencia MEC; {CH_DEFS} (rebuilt, GENCMP step B)"),
    dict(name="nuwro", src=("nuwro_C12", "nuwro_H"), cells="all",
         label=f"NuWro 21.09; {CH_DEFS} (rebuilt, GENCMP step B): C12 + free proton, 12:1 per nucleon; "
               f"hydrogen: supplement FLAGGED; {gc.LABELS['nuwro_CH']}"),
    dict(name="gibuu", src=("gibuu_C12", "gibuu_H"), cells="gibuu",
         label=f"GiBUU 2019; {CH_DEFS} (rebuilt, GENCMP step B): C12 + free proton, 12:1 per nucleon; "
               f"hydrogen: closure B3 failed; {gc.LABELS['gibuu_CH']}; no events above E_nu = 20 GeV (KNOWN_ISSUES 82), "
               "so it is compared on the eight p_parallel < 4.5 cells only and not shown above p_parallel 4.5 "
               "(FD-DIRECTOR-RULINGS.md section 5)"),
)
PRED_SCHEMA = "fd-gencmp-e-prediction/1"


class Stop(SystemExit):
    def __init__(self, control: str, why: str):
        super().__init__(f"FAIL control {control}: {why}")


def report(control: str, name: str, ok: bool, why: str = "differs") -> None:
    if not ok:
        raise Stop(control, f"{name}: {why}")
    print(f"[PASS {control}] {name}", flush=True)


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_new(path: Path, data: bytes) -> None:
    if path.exists():
        raise Stop("-", f"refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    A.write_atomic(path, data)


# ---------------------------------------------------------------- stage


def scratch_pins(pins: dict[str, str], scratch: Path = SCRATCH) -> dict[str, str]:
    """The pins under the scratch root, as {path relative to it: sha256}."""
    return {str(Path(p).relative_to(scratch)): h for p, h in pins.items() if Path(p).is_relative_to(scratch)}


def cmd_stage(a, pins: dict[str, str] | None = None) -> int:
    pins = gc.load_pins(INPUTS) if pins is None else pins
    todo = scratch_pins(pins, a.scratch)
    report("S", "the inputs file names at least one scratch input", bool(todo), "none")
    rec = {}
    for rel, want in sorted(todo.items()):
        src, dst = a.scratch / rel, a.run_dir / "inputs" / rel
        data, atime_ok = gc.read_noatime(src)
        got = hashlib.sha256(data).hexdigest()
        report("S", f"{rel} is the pinned bytes", got == want, f"{got} != {want}")
        write_new(dst, data)
        rec[rel] = {"sha256": got, "atime_unchanged": atime_ok}
    moved = sorted(k for k, v in rec.items() if not v["atime_unchanged"])
    write_new(a.run_dir / "inputs" / "STAGE.json",
              (json.dumps({"schema": "fd-gencmp-e-stage/1", "copied": rec, "atime_deviations": moved},
                          indent=1) + "\n").encode())
    print(f"[S] {len(rec)} inputs staged; atime moved on {len(moved)}", flush=True)
    return 0


# ---------------------------------------------------------------- materialize


def rebuilt(d: Path, sample: str, seed: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    with np.load(d / f"{sample}_ana_s{seed}.npz", allow_pickle=False) as z:
        return tuple(np.asarray(z[k], float) for k in ("xsec_flat", "sumw2_flat", "nevt_flat"))


def corner(d: Path, src: tuple) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """xsec and sumw2 exactly as fd_gencmp.py defs formed them (seed_mean; combine for a carbon and hydrogen pair), and
    nevt, the five seeds' mean count per fine cell, summed over the pair (descriptive: Stage G prints it)."""
    parts = []
    for s in src:
        x, v, _ = gc.seed_mean(d, s, kin.SEEDS)
        n = np.mean([rebuilt(d, s, seed)[2] for seed in kin.SEEDS], axis=0)
        parts.append((x, v, n))
    if len(parts) == 1:
        return parts[0]
    (xc, vc, nc), (xh, vh, nh) = parts
    x, v = gc.combine(xc, vc, xh, vh)
    return x, v, nc + nh


def defs_record(defs: dict, name: str) -> dict:
    return defs["generators"][name]["CH"]["analysis_definitions"]


def check_e0(U: np.ndarray, R: dict, defs: dict, name: str, cells: list[int], x, v) -> None:
    """E0: the materialized file is the corner defs.json read: g and its two chi2 equal to 1e-12 relative (defs.json was
    computed on a compute node, and BLAS may sum U x in another order here; the worst difference is printed)."""
    rec = defs_record(defs, name)
    g, Vg = gc.integrate(U, x, v, cells)
    worst = float(np.max(np.abs(g[cells] - np.asarray(rec["g"])) / np.abs(np.asarray(rec["g"]))))
    report("E0", f"{name}: g on its cells is defs.json's to 1e-12 (worst relative {worst:.2e})",
           A.compare_numbers({"g": rec["g"]}, {"g": g[cells].tolist()}, ()) == [], f"worst {worst!r}")
    c = gc.chi2_pair(R, g, Vg, cells)
    for arm in ("reported", "without_C_PL5D"):
        for kind in ("total", "shape_only"):
            ok = A.same_number(c[arm][kind]["chi2"], rec["chi2"][arm][kind]["chi2"])
            report("E0", f"{name}: {arm} {kind} chi2 is defs.json's", ok,
                   f"{c[arm][kind]['chi2']!r} != {rec['chi2'][arm][kind]['chi2']!r}")


def npz_bytes(x, v, n, meta: dict) -> bytes:
    """A prediction file as Stage G reads it (fd_g_compare.prediction_problems): xsec, sumw2 and nevt as float64 on the
    fine grid, the grid's edges and meta_json. Stored with fixed timestamps and attributes as fd_cpl_addition.npz_bytes
    does, so the same arrays give the same bytes; meta_json keeps its string dtype."""
    arrays = {"xsec_flat": np.asarray(x, "<f8"), "sumw2_flat": np.asarray(v, "<f8"), "nevt_flat": np.asarray(n, "<f8"),
              **{f"edges_{ax}": np.asarray(sa.s1.FINE[ax], "<f8") for ax in sa.s1.AXES},
              "meta_json": np.asarray(json.dumps(meta, sort_keys=True))}
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_STORED) as z:
        for k, arr in arrays.items():
            b = io.BytesIO()
            np.lib.format.write_array(b, arr if arr.ndim == 0 else np.ascontiguousarray(arr), version=(1, 0),
                                      allow_pickle=False)     # ascontiguousarray would make meta_json 1-d
            zi = zipfile.ZipInfo(f"{k}.npy", date_time=(1980, 1, 1, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_STORED
            zi.create_system = 3
            zi.external_attr = 0o644 << 16
            z.writestr(zi, b.getvalue())
    return buf.getvalue()


def cmd_materialize(a, R: dict | None = None, defs_sha256: str = DEFS_SHA256) -> int:
    out = a.run_dir / "pred"
    report("M", f"{out} does not exist (no overwrite)", not out.exists())
    raw = a.defs.read_bytes()
    report("M", "defs.json is the pinned readout", hashlib.sha256(raw).hexdigest() == defs_sha256)
    defs = json.loads(raw)
    d = a.run_dir / "inputs" / REBUILD
    rj = d / "rebuild.json"
    report("M", "the rebuild directory is the one defs.json read",
           sha256(rj) == defs["rebuild_json_sha256"], f"{sha256(rj)} != {defs['rebuild_json_sha256']}")
    U = gc.cell_matrix()
    if R is None:
        R = gc.result(gc.Inputs())
    sums, specs = {}, []
    for spec in CHDEFS:
        cells = gc.ALL_CELLS if spec["cells"] == "all" else gc.GIBUU_CELLS
        x, v, n = corner(d, spec["src"])
        check_e0(U, R, defs, spec["name"], cells, x, v)
        rel = f"gencmp_e/{spec['name']}_ch_ana.npz"
        meta = {"schema": PRED_SCHEMA, "prediction": spec["name"], "label": spec["label"],
                "corner": CH_DEFS, "sources": {s: [f"{s}_ana_s{seed}.npz" for seed in kin.SEEDS] for s in spec["src"]},
                "rebuild_json_sha256": defs["rebuild_json_sha256"], "defs_sha256": defs_sha256,
                "nevt": "the five seeds' mean count per fine cell, summed over carbon and hydrogen; descriptive"}
        data = npz_bytes(x, v, n, meta)
        write_new(out / rel, data)
        sums[rel] = hashlib.sha256(data).hexdigest()
        specs.append({"name": spec["name"], "path": rel, "sha256": sums[rel], "meta": ["prediction", spec["name"]],
                      "cells": spec["cells"], "label": spec["label"]})
    tune_src = a.run_dir / "inputs" / "s5p-20260926" / TUNE["path"]
    report("M", "MnvTune v1's staged file is Stage G's", sha256(tune_src) == TUNE["sha256"])
    write_new(out / TUNE["path"], tune_src.read_bytes())
    sums[TUNE["path"]] = TUNE["sha256"]
    specs.append({k: (list(v) if isinstance(v, tuple) else v) for k, v in TUNE.items()})
    write_new(out / "SHA256SUMS", "".join(f"{h}  {p}\n" for p, h in sums.items()).encode())
    write_new(out / "predictions.json", (json.dumps({"schema": "fd-gencmp-e-predictions/1", "set": "chdefs",
                                                     "predictions": specs}, indent=1) + "\n").encode())
    print(f"[M] {len(specs)} predictions written; E0 held for {len(CHDEFS)}", flush=True)
    return 0


def load_chdefs(pred: Path) -> list[dict]:
    """The chdefs set as Stage G's tools take it, from materialize's record, each file re-hashed."""
    specs = json.loads((pred / "predictions.json").read_bytes())["predictions"]
    names = [s["name"] for s in specs]
    report("P", "the chdefs set holds Stage G's five names, in order, on Stage G's cells",
           names == [p["name"] for p in fg.PREDICTIONS]
           and [s["cells"] for s in specs] == [p["cells"] for p in fg.PREDICTIONS])
    for s in specs:
        report("P", f"{s['name']}: the file is the recorded bytes", sha256(pred / s["path"]) == s["sha256"])
    return specs


# ---------------------------------------------------------------- chain


BOOT = """import json, sys
nd, mod, pins_file, preds_file, argv = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], json.loads(sys.argv[5])
sys.path.insert(0, nd)
import importlib
T = importlib.import_module(mod)
pins = json.load(open(pins_file))
kw = {}
if preds_file != "-":
    kw["predictions"] = json.load(open(preds_file))
sys.argv = [T.__file__, *argv]
sys.exit(T.run(T.build_args(argv), pins=pins, **kw))
"""


class Chain(A.Chain):
    """fd_cpl_addition's Chain, with the prediction set passed to each tool beside its pins."""

    def __init__(self, paths, receipt: Path, preds_file: Path | None):
        super().__init__(paths, receipt)
        self.preds_file = preds_file

    def run(self, name, arm, tool, argv, outputs, timeout, pins=None, variant=""):
        if pins is None or variant:
            raise Stop("C", f"{arm} {name}: every amendment-E step runs with explicit pins and no variant")
        import subprocess
        import time
        pf = self.p.BA / "pins" / f"{arm}-{name}.json"
        A.write_atomic(pf, (json.dumps(pins, indent=1) + "\n").encode())
        preds = "-" if self.preds_file is None or tool == "fd_g_figures_check" else str(self.preds_file)
        cmd = [sys.executable, "-I", "-B", "-c", BOOT, str(self.p.nd), tool, str(pf), preds, json.dumps(argv)]
        if tool == "fd_g_figures_check":
            cmd = [sys.executable, "-I", "-B", str(self.p.nd / f"{tool}.py"), *argv]
        log = self.p.BA / "logs" / f"{arm}-{name}"
        t0 = time.time()
        with open(f"{log}.out", "w") as o, open(f"{log}.err", "w") as e:
            try:
                rc = subprocess.run(cmd, stdout=o, stderr=e, timeout=timeout, cwd=self.p.BA,
                                    env={k: v for k, v in os.environ.items() if k != "PYTHONPATH"}).returncode
            except subprocess.TimeoutExpired:
                rc = 124
        rec = {"step": name, "arm": arm, "tool": tool, "argv": argv, "pins": pins,
               "predictions": None if preds == "-" else preds, "rc": rc, "wall_s": round(time.time() - t0, 1),
               "start_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t0)),
               "outputs": {str(q): (sha256(q) if Path(q).exists() else None) for q in outputs}}
        self.steps.append(rec)
        self.save()
        print(f"[chain] {arm} {name}: rc {rc}, {rec['wall_s']} s", flush=True)
        if rc != 0 or any(v is None for v in rec["outputs"].values()):
            raise Stop("C", f"{arm} {name} exited {rc} or wrote no {[k for k, v in rec['outputs'].items() if v is None]}")
        return rec


class Paths(A.Paths):
    """fd_cpl_addition's paths with the scratch root at the staged copies; for the chdefs set the predictions' root and
    manifest are materialize's."""

    def __init__(self, D: Path, BA: Path, run_dir: Path, pset: str):
        super().__init__(D, run_dir / "inputs", BA)
        self.block = self.T / "fd/with-cpl/block/cpl_block.npz"
        if pset == "chdefs":
            self.s5p_root = run_dir / "pred"
            self.s5p_sums = run_dir / "pred" / "SHA256SUMS"


BLOCK_SHA256 = "d9aa32fdb64357760348c9ccbc32fbea81d517f0f0786eedf17ab4946eaca59f"
COMMITTED_WITH = {
    "g": (f"{FD}/fd/with-cpl/readout/fd_g_readout.json", "b55366b3fd2d35a5426351531a9aa002a4d6be4b1048bd27339491e8c400a6fd"),
    "g_diag": (f"{FD}/fd/with-cpl/readout/fd_g_diag_readout.json",
               "bfd529ab67ddf6e9d72de5ddda9d6318fe5b055b008b9af1bbd0af5d45a64de2"),
    "g_followup": (f"{FD}/fd/with-cpl/readout/fd_g_followup_readout.json",
                   "5c95c6d0f43ba0288d293e6b21f97c082f4a090adf22ca97fec1396df30f0633"),
    "g_sens2": (f"{FD}/fd/with-cpl/readout/fd_g_sens2_readout.json",
                "cff60b63a951834df1793e7785da7314bf675696e888c1ff3fda58e5df604c20"),
    "flux_boot": (f"{FD}/fd/with-cpl/readout/fd_flux_boot_readout.json",
                  "7d11751577d4b2dbdac92ec576ee9d1f46d684ccc08fc419196996dcbd175f9d"),
    "f0b": (f"{FD}/fd/with-cpl/readout/fd_f0b_readout.json",
            "5f542830561731b567f2b97d78e5e9677a9802a35ef9c21855828bf184e6f3d6"),
}
COMMITTED = {"nopl": {k: A.COMMITTED[k] for k in (*STEPS, "f0b")}, "with": COMMITTED_WITH}
FIGURES = {"nopl": f"{FD}/fd/figures", "with": f"{FD}/fd/with-cpl/figures"}


def arm_block(p: Paths, arm: str) -> tuple[list, str]:
    """The extra block's flags for an arm, as the committed readouts of that arm were made."""
    if arm == "nopl":
        return A.extra(p.cresp, A.PINS["cresp_npz"], "C_resp", "C_resp"), "C_resp"
    return A.extra(p.block, BLOCK_SHA256, A.XKEY, A.NAME), A.NAME


def step_pins(k: str, H: dict, base: dict) -> dict:
    """A step's bound defaults, with the predictions' manifest and each upstream readout replaced by what was written."""
    import importlib
    if k == "g":
        pins = dict(fg.PINS)
    else:
        mod, attr = A.STEP_PINS[k]
        pins = dict(getattr(importlib.import_module(mod), attr))
        pins.update({f: H[u] for f, u in A.UPSTREAM[k].items()})
    pins.update(base)
    return pins


def run_set(c: Chain, pset: str, arm: str, D: Path) -> dict:
    """The five readouts and the three figures for one set and arm; returns the readouts' paths and sha256.

    The old set runs each downstream step and the figures on the COMMITTED upstream readouts, pinned by their committed
    digests, as fd_cpl_addition's without arm does: each readout records its upstream's digest, so R0 can compare it
    with the committed one only if its upstream is the committed one. The chdefs set chains: each downstream step reads,
    and is pinned to, the readout the step before wrote."""
    p = c.p
    xb, name = arm_block(p, arm)
    base = {} if pset == "old" else {"s5p_sums": sha256(p.s5p_sums)}
    W = p.BA / pset / arm
    out = {k: W / "readout" / Path(A.COMMITTED[k][0]).name for k in STEPS}
    (W / "readout").mkdir(parents=True, exist_ok=True)
    up, H = {}, {}
    if pset == "old":
        src = {k: D / COMMITTED[arm][k][0] for k in STEPS}
        hsrc = {k: COMMITTED[arm][k][1] for k in STEPS}
    else:
        src, hsrc = up, H
    for k in STEPS:
        c.run(k, f"{pset}-{arm}", A.TOOLS[k], A.step_argv(p, k, xb, xb, src, out[k], "with"), [out[k]], A.TIMEOUT[k],
              pins=step_pins(k, hsrc, base))
        H[k], up[k] = sha256(out[k]), out[k]
    f0b_rel, f0b_pin = COMMITTED[arm]["f0b"]
    src = dict(src)
    src["f0b"] = D / f0b_rel
    c.check(f"F {pset}-{arm}: the committed F0b readout is the pinned bytes", sha256(src["f0b"]) == f0b_pin, f0b_rel)
    fig = W / "figures"
    fargv = A.step_argv(p, "figures", xb, xb, src, fig, "with")
    if arm == "nopl":                                   # the committed nopl figures name C_resp by the tool's default
        i = fargv.index("--reported-block-name")
        del fargv[i:i + 2]
    pset_flag = ["--prediction-set", "gencmp-chdefs"] if pset == "chdefs" else []
    import fd_g_figures as FG
    c.run("figures", f"{pset}-{arm}", "fd_g_figures", [*fargv, *pset_flag],
          [fig / f"{n}{e}" for n in A.FIG_NAMES for e in (".pdf", ".json")], 75,
          pins={**FG.PINS, "g_readout": hsrc["g"], "g_diag_readout": hsrc["g_diag"],
                "g_followup_readout": hsrc["g_followup"], "g_sens2_readout": hsrc["g_sens2"], "f0b_readout": f0b_pin})
    c.run("figures_check", f"{pset}-{arm}", "fd_g_figures_check",
          [*A.step_argv(p, "figures_check", xb, xb, src, fig, "with"), *pset_flag], [], 75, pins={})
    return {"out": out, "H": H, "fig": fig, "block_name": name}


def check_r0(c: Chain, arm: str, res: dict, D: Path) -> None:
    for k in STEPS:
        rel, pin = COMMITTED[arm][k]
        c.check(f"R0 {arm} {k}: the committed readout is the pinned bytes", sha256(D / rel) == pin, rel)
        old, new = json.loads((D / rel).read_bytes()), json.loads(res["out"][k].read_bytes())
        # strings in the with arm only: its committed readouts were written by these very tools, while the nopl ones
        # were written by earlier versions of fd_g_diag, fd_g_followup and fd_flux_boot, which fd_cpl_addition's
        # control R reproduced in structure and numbers (FD-CT-5B-ADDITION-REPORT.md:119-125)
        bad = A.compare_numbers(old, new, R0_EXCLUDE) + (A.compare_strings(old, new, R0_EXCLUDE) if arm == "with" else [])
        what = "structure, numbers and strings" if arm == "with" else "structure and numbers"
        c.check(f"R0 {arm} {k}: {what} are the committed readout's but argv, code_sha256 and the block's file",
                not bad, bad[:20])
    cfig = D / FIGURES[arm]
    for n in A.FIG_NAMES:
        old, new = json.loads((cfig / f"{n}.json").read_bytes()), json.loads((res["fig"] / f"{n}.json").read_bytes())
        bad = A.compare_numbers(old, new, A.FIG_EXCLUDE) + A.compare_strings(old, new, A.FIG_EXCLUDE)
        c.check(f"R0 {arm} figure {n}: the sidecar is the committed one but argv, code and versions; the PDF the same "
                "bytes", not bad and (res["fig"] / f"{n}.pdf").read_bytes() == (cfig / f"{n}.pdf").read_bytes(),
                bad[:20])


def check_xc(c: Chain, arm: str, res: dict, defs: dict) -> None:
    """XC: Stage G's g and chi2 on the chdefs set are defs.json's (reported arm against defs' reported matrix, nopl
    against its matrix without C_PL5D)."""
    key = "reported" if arm == "with" else "without_C_PL5D"
    g = json.loads(res["out"]["g"].read_bytes())
    have = {p["name"]: p for p in g["predictions"]}
    c.check(f"XC {arm}: Stage G's readout holds each of the corner's four predictions",
            all(s["name"] in have for s in CHDEFS), sorted(have))
    for s in CHDEFS:
        p, rec = have[s["name"]], defs_record(defs, s["name"])
        ok = A.compare_numbers({"g": rec["g"]}, {"g": p["g"]}, ()) == [] and all(
            A.same_number(p[kind]["chi2"], rec["chi2"][key][kind]["chi2"]) for kind in ("total", "shape_only"))
        c.check(f"XC {arm} {s['name']}: Stage G's g and chi2 on the chdefs set are defs.json's", ok, s["name"])


def cmd_chain(a) -> int:
    D = _REPO
    BA = a.run_dir / "chain"
    report("C", f"{BA} does not exist (no overwrite)", not BA.exists())
    for sub in ("logs", "pins"):
        (BA / sub).mkdir(parents=True, exist_ok=True)
    defs = json.loads(a.defs.read_bytes())
    report("C", "defs.json is the pinned readout", sha256(a.defs) == DEFS_SHA256)
    preds = a.run_dir / "pred"
    specs = load_chdefs(preds)
    pf = BA / "pins" / "predictions-chdefs.json"
    A.write_atomic(pf, (json.dumps(specs, indent=1) + "\n").encode())
    receipt = BA / "chain.json"
    try:
        c = Chain(Paths(D, BA, a.run_dir, "old"), receipt, None)
        for arm in ARMS:                                   # R0 in both arms before any new number
            check_r0(c, arm, run_set(c, "old", arm, D), D)
        steps = c.steps
        c = Chain(Paths(D, BA, a.run_dir, "chdefs"), receipt, pf)
        c.steps = steps
        for arm in ARMS:
            check_xc(c, arm, run_set(c, "chdefs", arm, D), defs)
    except (A.Stop, fg.Stop) as e:
        print(f"[STOP] {e}", file=sys.stderr, flush=True)
        return 1
    print(f"[chain] done: {len(c.steps)} records in {receipt}", flush=True)
    return 0


# ---------------------------------------------------------------- CLI


def build_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("stage")
    s.add_argument("--scratch", type=Path, default=SCRATCH)
    s.add_argument("--run-dir", type=Path, required=True)
    for name in ("materialize", "chain"):
        s = sub.add_parser(name)
        s.add_argument("--run-dir", type=Path, required=True)
        s.add_argument("--defs", type=Path, default=DEFS)
    return p.parse_args(argv)


def main(argv=None) -> int:
    a = build_args(argv)
    try:
        return {"stage": cmd_stage, "materialize": cmd_materialize, "chain": cmd_chain}[a.cmd](a)
    except (Stop, A.Stop, fg.Stop) as e:
        print(f"[STOP] {e}", file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

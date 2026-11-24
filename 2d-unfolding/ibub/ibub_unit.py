#!/usr/bin/env python3
"""IBUB's IBU units (IBUB-DECLARATION.md sections 3, 5 and 8): REF-C2C1's c2 estimator, binned D'Agostini IBU in the
seam of E_R's own driver, run on COV2D's toys through the driver's ``--data-file`` hook.

Every IBU mechanism is ``2d-unfolding/ref_c2c1/ref_c2c1.py``'s, imported and used unchanged: ``run_driver``,
``roounfold_bayes``, ``dagostini``, ``xsec_at_every_k``, ``c_sim``, ``event_factors``, ``th2_vector``, ``own_hxsec`` and
``copy_noatime``. Its unit parser, argv resolver, unit runner, code check and ``main`` are not used: they know only
REF-C2C1's units, and its code check pins the driver blob that COV2D's toys ran. IBUB runs main's blob (route (A),
the director's ruling of 2026-11-23); C-G2R and C-REP stand behind that.

Units (one ``--unit`` each; a lane runs several in one process, as REF-C2C1's replicas did):
  central            E_R's argv on the real data, no --data-file               C-REP against REF-C2C1's c2_central
  central_df         E_R's argv + --data-file <staged copy of $K2A>             C-REP-D against the same reference
  toy:<TUNE>:<SEED>  E_R's argv + --data-file <staged copy of data_<SEED>.root> one per COV2D toy
Each writes ``<name>.root`` (the driver's output), ``<name>.npz`` (xsec per K of the scan, the unfolded vectors, T, y,
meta) and ``<name>.done`` (its control verdict and both products' sha256).

Subcommands:
  stage                 login node: copy $CV, $MC and libRooUnfold.so through O_NOATIME into the staging root, check
                        each against its pin, make it read-only, write stage.json
  preflight             login node: the two references' O_NOATIME sha256 and the 600 toy files' stat (section 8)
  run --unit U ... --out DIR
                        the units, after the code pins, the staged inputs' digests and the CPU/thread gate
  refcheck --out DIR --time central=F --time central_df=F --step-rc central=RC --step-rc central_df=RC
                        the barrier (section 8): both references PASS and this job's, each full srun step (its
                        /usr/bin/time file) exit 0 within the re-price trigger, and central_df equal to central;
                        writes refcheck.json; exit 0 lets the toys start
  complete --out DIR    the job's completion check: the exact 600 toy markers PASS and this job's, no undeclared
                        marker, and the barrier receipt this job's PASS

Every run, refcheck and complete is bound to SLURM_JOB_ID and to IBUB_M, the deploy commit, which must equal the
checkout's HEAD; each destination must resolve under the namespace (config.json "namespace").

MEASURES: one driver run per unit. CANNOT AUTHORIZE: a reading (``ibub_readout.py`` applies the declared ones).
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import stat
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
CONFIG = HERE / "config.json"
for p in (REPO / "2d-unfolding" / "ref_c2c1", REPO / "2d-unfolding" / "cov2d"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
import ref_c2c1 as rc  # noqa: E402  (unchanged; pinned in config.json)
import cov2d as c  # noqa: E402  (TOY_SEEDS)

GateFailure = rc.GateFailure
RC_GATE, RC_CONTROL, RC_STOP = rc.RC_GATE, rc.RC_CONTROL, 3
REFERENCE_UNITS = ("central", "central_df")
# the controls each unit kind must carry (section 5); the readout requires the toy set
CONTROLS = {"central": {"C-G2R", "C-FILL", "C-ROO", "C-SIM", "C-DATA", "C-REP"},
            "central_df": {"C-G2R", "C-FILL", "C-ROO", "C-DATA", "C-REP-D"},
            "toy": {"C-G2R", "C-FILL", "C-ROO", "C-DATA"}}


def load_config(path: Path = CONFIG) -> dict:
    return json.loads(Path(path).read_text())


def check_code(cfg: dict) -> None:
    """Every imported file IBUB depends on equals its pin (the driver at main's blob, ref_c2c1.py, the helper)."""
    for rel, digest in cfg["code_sha256"].items():
        if rc.sha256(REPO / rel) != digest:
            raise GateFailure(f"{rel} digest differs from config.json")


def namespace(cfg: dict) -> Path:
    """The bound namespace $N, which must not itself be a symlink (its path as written is its real path)."""
    n = Path(cfg["namespace"])
    if os.path.realpath(n) != os.path.abspath(n):
        raise GateFailure(f"the namespace {n} is not its own real path (a symlink?)")
    return n


def inside(cfg: dict, path) -> Path:
    """``path`` resolved (every symlink followed) must lie under the namespace: no write or staged read escapes it."""
    n = os.path.realpath(namespace(cfg))
    p = os.path.realpath(path)
    if p != n and not p.startswith(n + os.sep):
        raise GateFailure(f"{path} resolves to {p}, outside the namespace {n}")
    return Path(p)


def write_contained(cfg: dict, path, data: bytes, *, exclusive: bool = True) -> None:
    """Write ``data`` to ``path``, whose directory must resolve under the namespace. The final component is never
    followed if it is a symlink (O_NOFOLLOW). With ``exclusive``, the file must not already exist: a stale file or a
    planted symlink is refused, never replaced or written through."""
    path = Path(path)
    inside(cfg, path.parent)
    flags = os.O_WRONLY | os.O_CREAT | os.O_NOFOLLOW | (os.O_EXCL if exclusive else os.O_TRUNC)
    fd = os.open(path, flags, 0o644)
    try:
        os.write(fd, data)
    finally:
        os.close(fd)


def binding() -> dict:
    """The job and deploy every unit, the barrier and the completion check are bound to: SLURM_JOB_ID, and the
    deploy's HEAD, which must equal IBUB_M (the commit the job was submitted with)."""
    job, want = os.environ.get("SLURM_JOB_ID"), os.environ.get("IBUB_M")
    if not job or not re.fullmatch(r"[0-9]+", job):
        raise GateFailure(f"SLURM_JOB_ID is {job!r}, not a job id")
    if not want or not re.fullmatch(r"[0-9a-f]{40}", want):
        raise GateFailure(f"IBUB_M is {want!r}, not a commit")
    r = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True)
    head = r.stdout.strip()
    if r.returncode != 0 or head != want:
        raise GateFailure(f"the deploy HEAD {head!r} (rc {r.returncode}) is not IBUB_M {want}")
    return {"job": job, "deploy_head": head}


def staging_root(cfg: dict) -> Path:
    return Path(cfg["staging"]["root"]).resolve()


def staged(cfg: dict) -> dict:
    root = staging_root(cfg)
    return {k: root / cfg["staging"][k] for k in ("CV", "MC", "lib")}


def data_dir(cfg: dict) -> Path:
    return staging_root(cfg) / cfg["staging"]["data"]


def check_inputs(cfg: dict) -> dict:
    """The staged copies equal their pins, read through O_NOATIME, before any driver opens them (once per process)."""
    out = {}
    root = staging_root(cfg)
    for key, path in staged(cfg).items():
        if not rc.under(path, root):
            raise GateFailure(f"staged {key} {path} is not under the staging root {root}")
        got = rc.sha256_noatime(path)
        if got != cfg["inputs"][f"{key}_sha256"]:
            raise GateFailure(f"staged {key} digest {got[:12]} differs from config.json")
        out[key] = got
    return out


# ------------------------------------------------------------------------------------------- the toys' records


def toy_shas(cfg: dict, tune: str) -> dict:
    """{seed: sha256} of a tune's 300 toy data files, from COV2D step B's committed pseudo_b.json at its pin."""
    t = cfg["toys"][tune]
    raw = (REPO / t["pseudo_b"]).read_bytes()
    if hashlib.sha256(raw).hexdigest() != t["pseudo_b_sha256"]:
        raise GateFailure(f"{t['pseudo_b']} differs from its pin")
    rec = json.loads(raw)
    if rec.get("verdict") != "PASS":
        raise GateFailure(f"{t['pseudo_b']} verdict is {rec.get('verdict')}")
    files = {int(f["seed"]): f for f in rec["files"]}
    want = list(c.TOY_SEEDS[tune])
    missing = [s for s in want if s not in files or files[s]["role"] != "toy"]
    if missing:
        raise GateFailure(f"{tune}: pseudo_b.json lacks toy seeds {missing[:5]}")
    for s in want:
        if Path(files[s]["path"]).name != f"data_{s}.root" or str(Path(files[s]["path"]).parent) != t["dir"]:
            raise GateFailure(f"{tune}: pseudo_b.json's file for seed {s} is {files[s]['path']}, not under {t['dir']}")
    return {s: files[s]["sha256"] for s in want}


def reported_cells(cfg: dict) -> np.ndarray:
    """E_R's 205 reported cells (rep, on the 224-cell grid) from the committed blocks record at its pin."""
    raw = (REPO / cfg["cells"]["blocks"]).read_bytes()
    if hashlib.sha256(raw).hexdigest() != cfg["cells"]["blocks_sha256"]:
        raise GateFailure("the blocks record differs from its pin")
    rep = np.load(io.BytesIO(raw))["rep"].astype(bool)
    if rep.shape != (224,) or int(rep.sum()) != 205:
        raise GateFailure(f"rep has shape {rep.shape} and {int(rep.sum())} cells, not (224,) and 205")
    return rep


# ------------------------------------------------------------------------------------------- units


def parse_unit(spec: str) -> dict:
    if spec in REFERENCE_UNITS:
        return {"kind": spec, "name": spec, "tune": None, "seed": None}
    parts = spec.split(":")
    if len(parts) == 3 and parts[0] == "toy" and parts[1] in c.TOY_SEEDS and parts[2].isdigit():
        tune, seed = parts[1], int(parts[2])
        if seed not in c.TOY_SEEDS[tune]:
            raise ValueError(f"{seed} is not one of {tune}'s declared toy seeds")
        return {"kind": "toy", "name": f"toy_{tune}_{seed}", "tune": tune, "seed": seed}
    raise ValueError(f"unknown unit {spec!r}")


def g2r_check(cfg: dict, argv: list) -> None:
    """C-G2R: no option COV2D-G2R amendment 1 added reaches the driver, in either spelling (--opt v, --opt=v)."""
    bad = sorted({a.split("=", 1)[0] for a in argv} & set(cfg["g2r_forbidden_options"]))
    if bad:
        raise GateFailure(f"C-G2R: the argv carries {bad}")


def resolve_argv(cfg: dict, data_copy: Path | None) -> list:
    subs = {"$CV": str(staged(cfg)["CV"]), "$MC": str(staged(cfg)["MC"])}
    argv = [subs.get(x, x) for x in cfg["e_r"]["argv"]]
    if any(x.startswith("$") for x in argv):
        raise GateFailure(f"unresolved variable in {argv}")
    if data_copy is not None:
        argv += ["--data-file", str(data_copy)]
    g2r_check(cfg, argv)
    return argv


def gate_env(cfg: dict) -> tuple[int, dict]:
    """Like for like with COV2D's toy lanes: exactly the declared CPUs and all four thread variables."""
    cpus = rc.cpu_count()
    if cpus != int(cfg["e_r"]["cpus"]):
        raise GateFailure(f"needs {cfg['e_r']['cpus']} CPUs, this process has {cpus}")
    threads = {k: os.environ.get(k) for k in cfg["e_r"]["thread_env"]}
    if threads != cfg["e_r"]["thread_env"]:
        raise GateFailure(f"needs the thread environment {cfg['e_r']['thread_env']}, not {threads}")
    return cpus, threads


def data_source(cfg: dict, unit: dict, shas: dict) -> tuple[Path, str]:
    if unit["kind"] == "central_df":
        return Path(cfg["refs"]["k2a"]["path"]), cfg["refs"]["k2a"]["sha256"]
    return Path(cfg["toys"][unit["tune"]]["dir"]) / f"data_{unit['seed']}.root", shas[unit["tune"]][unit["seed"]]


def stage_data(cfg: dict, unit: dict, shas: dict) -> tuple[Path, str]:
    """One O_NOATIME copy of the unit's data file under the staging root (the TFile guard's only readable tree), which
    must equal its pin; a copy off its pin is deleted before the refusal."""
    src, want = data_source(cfg, unit, shas)
    dest = data_dir(cfg) / f"{unit['name']}.root"
    dest.parent.mkdir(parents=True, exist_ok=True)
    inside(cfg, dest.parent)                      # a symlinked stage/data can never take the copy out of $N
    try:
        got = rc.copy_noatime(src, dest)
    except BaseException:
        if dest.exists():            # a partial or unverified copy never stays behind to block a rerun
            dest.unlink()
        raise
    if got != want:
        dest.unlink()
        raise GateFailure(f"C-DATA: {src} sha256 {got[:12]} != {want[:12]}")
    return dest, got


def read_reference(cfg: dict) -> dict:
    """REF-C2C1's c2_central.npz, read once through O_NOATIME and checked against its done-marker's digest."""
    ref = cfg["refs"]["c2_central"]
    with rc.open_noatime(Path(ref["path"])) as fh:
        raw = fh.read()
    if hashlib.sha256(raw).hexdigest() != ref["sha256"]:
        raise GateFailure(f"C-REP's reference {ref['path']} differs from its pin")
    z = np.load(io.BytesIO(raw))
    return {k: np.asarray(z[k]) for k in ("ks", "xsec", "T", "y")}


def max_rel(a: np.ndarray, b: np.ndarray) -> float:
    """max |a/b - 1| over b != 0; inf when a is non-zero where b is zero, when the shapes differ, or when either side
    holds a non-finite value (a NaN never reaches a reduction, where it could be dropped)."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    if a.shape != b.shape or not (np.all(np.isfinite(a)) and np.all(np.isfinite(b))):
        return float("inf")
    nz = b != 0
    if np.any(a[~nz] != 0):
        return float("inf")
    return float(np.max(np.abs(a[nz] / b[nz] - 1))) if nz.any() else 0.0


def compare(a: dict, b: dict, rep: np.ndarray, rtol: float) -> dict:
    """C-REP's comparison: xsec at every K of the scan on the 205 cells, and the binned T and y, to rtol."""
    if list(np.asarray(a["ks"])) != list(np.asarray(b["ks"])):
        return {"pass": False, "why": "the K scans differ"}
    xs = max([max_rel(np.asarray(a["xsec"])[i][rep], np.asarray(b["xsec"])[i][rep]) for i in range(len(a["ks"]))])
    out = {"xsec_max_rel": xs, "T_max_rel": max_rel(a["T"], b["T"]), "y_max_rel": max_rel(a["y"], b["y"]), "rtol": rtol}
    out["pass"] = bool(max(out["xsec_max_rel"], out["T_max_rel"], out["y_max_rel"]) <= rtol)
    return out


def max_abs_rel(a, b) -> float:
    """C-ROO's measure, max |a - b| / max(|b|, 1e-300); inf when either side holds a non-finite value."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    if a.shape != b.shape or not (np.all(np.isfinite(a)) and np.all(np.isfinite(b))):
        return float("inf")
    return float(np.max(np.abs(a - b) / np.maximum(np.abs(b), 1e-300))) if a.size else 0.0


def read_marker(path: Path) -> dict:
    """A done-marker as a dict; an absent, empty or malformed one reads as {} (no verdict, so never PASS)."""
    try:
        m = json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return {}
    return m if isinstance(m, dict) else {}


def marker_ok(out: Path, name: str, bound: dict, kind: str | None = None) -> tuple[bool, str]:
    """A unit is done only if all of these hold:
    - its marker names it;
    - the marker is PASS and was written by this job at this deploy (``bound``);
    - neither product is a symlink;
    - both products are at the marker's digests;
    - the npz's own meta names the same unit, kind, job and deploy.
    Returns (ok, why)."""
    m = read_marker(out / f"{name}.done")
    npz, root = out / f"{name}.npz", out / f"{name}.root"
    if m.get("unit") != name or m.get("verdict") != "PASS":
        return False, f"marker unit {m.get('unit')!r}, verdict {m.get('verdict')!r}"
    if (str(m.get("job")), m.get("deploy_head")) != (bound["job"], bound["deploy_head"]):
        return False, f"marker job/deploy {m.get('job')}/{m.get('deploy_head')}"
    if npz.is_symlink() or root.is_symlink() or not (npz.is_file() and root.is_file()):
        return False, "a product is absent or a symlink"
    if rc.sha256(npz) != m.get("sha256") or rc.sha256(root) != m.get("root_sha256"):
        return False, "a product is not at its marker's digest"
    try:
        meta = json.loads(str(np.load(npz)["meta"]))
    except (ValueError, KeyError, OSError) as e:
        return False, f"its npz meta is not readable ({e})"
    if (meta.get("unit"), str(meta.get("slurm_job")), meta.get("deploy_head")) != (name, bound["job"], bound["deploy_head"]):
        return False, f"its npz meta names {meta.get('unit')}/{meta.get('slurm_job')}/{meta.get('deploy_head')}"
    if kind is not None and meta.get("kind") != kind:
        return False, f"its npz meta kind is {meta.get('kind')}"
    return True, "ok"


def c_sim_finite(driver, cap, ks) -> bool:
    """IBUB's finite check on C-SIM: every covered cell of the simulated extraction, at every K, and of its reference,
    must be finite. ref_c2c1.c_sim, pinned and unchanged, keeps a running Python max that drops a NaN (the codex read,
    round 2, item 4). The extraction here uses the same ref_c2c1 helpers and the driver's recorded arguments."""
    T, M, tin, w_in = cap["T"], cap["M"], cap["tin"], cap["w_in"]
    a, k = cap["extract"]
    h_comp, _, h_den = cap["completeness"]
    nx, ny = len(driver.PT_EDGES) - 1, len(driver.PZ_EDGES) - 1
    unit = h_comp.Clone("ibub_csim_unit")
    for ix in range(1, nx + 1):
        for iy in range(1, ny + 1):
            unit.SetBinContent(ix, iy, 1.0)
    covered = rc.th2_vector(h_comp, nx, ny) > 0
    ref = rc.th2_vector(cap["real_extract"](h_den, unit, *a[1:], **k), nx, ny)
    if not np.all(np.isfinite(ref[covered])):
        return False
    traj = rc.dagostini(M, T, M.sum(axis=1), ks)
    for K in ks:
        h = rc.filled(driver, tin, w_in, rc.event_factors(traj[K], T, tin), f"ibub_csim_K{K}")
        x = rc.th2_vector(cap["real_extract"](h, *a, **k), nx, ny)
        if not np.all(np.isfinite(x[covered])):
            return False
    return True


def provenance(path: Path) -> dict:
    """The driver's TNamed records in its own output."""
    import ROOT
    f = ROOT.TFile.Open(str(path))
    out = {}
    for key in f.GetListOfKeys():
        obj = key.ReadObj()
        if obj.ClassName() == "TNamed":
            out[key.GetName()] = obj.GetTitle()
    f.Close()
    return out


def run_unit(driver, ohf, cfg: dict, unit: dict, out: Path, *, shas: dict, rep: np.ndarray, ref: dict | None,
             bound: dict, inputs_verified: dict | None = None, unfolder=None) -> int:
    """One unit; its done-marker carries its control verdict and the job and deploy it ran under. A unit already
    present is skipped only if its marker is PASS and was written by this job at this deploy; anything else present
    is refused, never overwritten."""
    name = unit["name"]
    root, npz, marker = out / f"{name}.root", out / f"{name}.npz", out / f"{name}.done"
    if any(p.exists() or p.is_symlink() for p in (npz, root, marker)):
        ok, why = marker_ok(out, name, bound, unit["kind"])
        if ok:
            return 0
        print(f"refusing: {name} exists and is not this job's verified PASS ({why})", file=sys.stderr)
        return RC_CONTROL
    try:
        cpus, threads = gate_env(cfg)
    except GateFailure as e:
        print(f"refusing: {name}: {e}", file=sys.stderr)
        return RC_GATE
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    c2 = cfg["c2"]
    ks = list(c2["scan"])
    data_copy = data_sha = None
    try:
        if unit["kind"] != "central":
            data_copy, data_sha = stage_data(cfg, unit, shas)
        argv = resolve_argv(cfg, data_copy)
        lib = str(staged(cfg)["lib"])
        prod = unfolder or (lambda M, T, y, k: rc.roounfold_bayes(M, T, y, k, lib))
        cap = rc.run_driver(driver, ohf, argv, root, ibu={"unfolder": prod, "ks": ks, "primary": c2["primary"]},
                            staging=staging_root(cfg))
        xs = rc.xsec_at_every_k(driver, cap, ks)
        arrays = {"ks": np.array(ks), "xsec": np.array([xs[K] for K in ks]),
                  "unfolded": np.array([cap["traj"][K] for K in ks]), "T": cap["T"], "y": cap["y"]}
        controls = {"C-G2R": {"pass": True, "forbidden": cfg["g2r_forbidden_options"]}}
        own = rc.own_hxsec(driver, root, (out, staging_root(cfg)))
        fill = max_rel(own, xs[c2["primary"]])     # inf on a non-finite value, or on own != 0 where the extraction is 0
        controls["C-FILL"] = {"max_rel": fill, "pass": bool(fill <= c2["c_fill_rtol"])}
        numpy_traj = rc.dagostini(cap["M"], cap["T"], cap["y"], ks)
        roo = max([max_abs_rel(cap["traj"][K], numpy_traj[K]) for K in ks])
        controls["C-ROO"] = {"max_rel": roo, "pass": bool(roo <= c2["c_roo_rtol"])}
        if unit["kind"] == "central":
            sim = rc.c_sim(driver, cap, rc.dagostini, ks, c2["c_sim_rtol"])
            sim["all_finite"] = c_sim_finite(driver, cap, ks)
            sim["pass"] = bool(sim["pass"] and sim["all_finite"] and np.isfinite(sim["max_rel"]))
            controls["C-SIM"] = sim
        prov = provenance(root)
        recorded_argv = json.loads(prov.get("runArgv", "null")) or []
        data = {"argv_equal": list(recorded_argv[1:]) == argv + ["--out", str(root)],
                "dataFileSha256": prov.get("dataFileSha256"), "expected": data_sha}
        data["pass"] = bool(data["argv_equal"] and prov.get("dataFileSha256") == data_sha)
        controls["C-DATA"] = data
        if unit["kind"] in REFERENCE_UNITS:
            key = "C-REP" if unit["kind"] == "central" else "C-REP-D"
            controls[key] = (compare(arrays, ref, rep, c2["c_rep_rtol"]) if ref is not None
                             else {"pass": False, "why": "no reference was read"})
        meta = {"schema": "ibub-unit/1", "unit": name, "kind": unit["kind"], "tune": unit["tune"], "seed": unit["seed"],
                "argv": argv, "runner_sha256": rc.sha256(Path(__file__).resolve()), "config_sha256": rc.sha256(CONFIG),
                "code_sha256": cfg["code_sha256"], "inputs_sha256": inputs_verified, "data_sha256": data_sha,
                "slurm_job": bound["job"], "deploy_head": bound["deploy_head"], "cpus": cpus, "thread_env": threads,
                "measured_weights_sha256": hashlib.sha256(cap["measured_weights"].tobytes()).hexdigest(),
                "controls": controls, "seconds": round(time.time() - t0, 3)}
        if set(controls) != CONTROLS[unit["kind"]]:
            raise GateFailure(f"{name}: controls {sorted(controls)} are not the declared {sorted(CONTROLS[unit['kind']])}")
        passed = all(v["pass"] for v in controls.values())
        if root.is_symlink() or not root.is_file():
            raise GateFailure(f"{name}: the driver's output {root} is not a regular file")
        buf = io.BytesIO()
        np.savez_compressed(buf, **arrays, meta=json.dumps(meta, default=str))
        write_contained(cfg, npz, buf.getvalue())
        write_contained(cfg, marker, (json.dumps({
            "unit": name, "kind": unit["kind"], "tune": unit["tune"], "seed": unit["seed"], "job": bound["job"],
            "deploy_head": bound["deploy_head"], "verdict": "PASS" if passed else "FAIL", "seconds": meta["seconds"],
            "sha256": rc.sha256(npz), "root_sha256": rc.sha256(root), "data_sha256": data_sha}) + "\n").encode())
    except GateFailure as e:
        print(f"refusing: {name}: {e}", file=sys.stderr)
        return RC_GATE
    finally:
        if data_copy is not None and Path(data_copy).exists():
            Path(data_copy).unlink()
    print(json.dumps({"unit": name, "seconds": meta["seconds"], "controls": {k: v["pass"] for k, v in controls.items()}}),
          flush=True)
    return 0 if passed else RC_CONTROL


# ------------------------------------------------------------------------------------------- subcommands


def stage(cfg: dict) -> int:
    """Copy each input once through O_NOATIME into the staging root, check it against its pin, make it read-only."""
    root = staging_root(cfg)
    inside(cfg, root.parent if not root.exists() else root)
    root.mkdir(parents=True, exist_ok=True)
    inside(cfg, root)
    rec, ok = {"schema": "ibub-stage/1", "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "files": {}}, True
    for key, dest in staged(cfg).items():
        src, want = Path(cfg["inputs"][f"{key}_source"]), cfg["inputs"][f"{key}_sha256"]
        got = rc.copy_noatime(src, dest)
        good = got == want
        if good:
            os.chmod(dest, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
        else:
            dest.unlink()
            ok = False
        rec["files"][key] = {"source": str(src), "staged": str(dest), "sha256": got, "pin": want, "pass": good}
    rec["verdict"] = "PASS" if ok else "FAIL"
    write_contained(cfg, root / "stage.json", (json.dumps(rec, indent=1, sort_keys=True) + "\n").encode())
    print(json.dumps(rec, sort_keys=True))
    return 0 if ok else RC_GATE


def preflight(cfg: dict) -> int:
    """Section 8's preflight: both references at their pins (O_NOATIME), and each of the 600 toy files present (stat)."""
    rec, ok = {"schema": "ibub-preflight/1", "refs": {}, "toys": {}}, True
    for k in ("c2_central", "k2a"):
        r = cfg["refs"][k]
        try:
            got = rc.sha256_noatime(Path(r["path"]))
        except OSError as e:
            got = f"unreadable: {e.strerror}"
        rec["refs"][k] = {"path": r["path"], "sha256": got, "pass": got == r["sha256"]}
        ok = ok and rec["refs"][k]["pass"]
    for tune in cfg["toys"]:
        missing = []
        for s in toy_shas(cfg, tune):
            p = Path(cfg["toys"][tune]["dir"]) / f"data_{s}.root"
            try:
                if os.stat(p).st_size <= 0:
                    missing.append(s)
            except OSError:
                missing.append(s)
        rec["toys"][tune] = {"files": len(c.TOY_SEEDS[tune]), "missing": missing}
        ok = ok and not missing
    rec["verdict"] = "PASS" if ok else "STOP"
    print(json.dumps(rec, sort_keys=True))
    return 0 if ok else RC_STOP


def gnu_time(path: Path) -> dict:
    """The full step's wall time and exit status from ``/usr/bin/time -v`` output: "Elapsed (wall clock) time
    (h:mm:ss or m:ss): 3:36.74" and "Exit status: 0". Anything unreadable reads as no wall and no status."""
    try:
        text = Path(path).read_text()
    except OSError:
        return {"wall_s": None, "exit_status": None}
    m = re.search(r"Elapsed \(wall clock\) time \(h:mm:ss or m:ss\):\s*([0-9:.]+)", text)
    e = re.search(r"Exit status:\s*(-?[0-9]+)", text)
    wall = None
    if m:
        parts = [float(x) for x in m.group(1).split(":")]
        wall = sum(v * 60 ** (len(parts) - 1 - i) for i, v in enumerate(parts))
    return {"wall_s": wall, "exit_status": int(e.group(1)) if e else None}


def refcheck(cfg: dict, out: Path, rep: np.ndarray, bound: dict, times: dict, step_rcs: dict) -> int:
    """The barrier. Its checks:
    - both reference units are this job's verified PASS (``marker_ok``: identity, digests, embedded provenance);
    - each full reference srun step exited 0 (``step_rcs``, the job's waited statuses);
    - the step's /usr/bin/time file reads exit status 0 within the re-price trigger (``times``);
    - central_df's cross sections equal central's to C-REP's tolerance.
    It writes refcheck.json once (no stale or planted file is replaced), the barrier receipt, which records both
    references' digests; exit 0 lets the toys start."""
    rec = {"schema": "ibub-refcheck/2", "job": bound["job"], "deploy_head": bound["deploy_head"],
           "runner_sha256": rc.sha256(Path(__file__).resolve()), "units": {}}
    ok = True
    limit = cfg["price"]["reprice_factor"] * cfg["price"]["unit_s"]
    arrays = {}
    for u in REFERENCE_UNITS:
        good, why = marker_ok(out, u, bound, u)
        t = gnu_time(times[u]) if u in times else {"wall_s": None, "exit_status": None}
        srun_rc = step_rcs.get(u)
        fast = isinstance(t["wall_s"], float) and t["wall_s"] <= limit and t["exit_status"] == 0
        unit_ok = bool(good and fast and srun_rc == 0)
        m = read_marker(out / f"{u}.done")
        rec["units"][u] = {"marker": why, "srun_rc": srun_rc, "step_wall_s": t["wall_s"],
                           "step_exit_status": t["exit_status"], "limit_s": limit,
                           "npz_sha256": m.get("sha256") if good else None,
                           "root_sha256": m.get("root_sha256") if good else None, "pass": unit_ok}
        ok = ok and unit_ok
        if good:
            z = np.load(out / f"{u}.npz")
            arrays[u] = {k: z[k] for k in ("ks", "xsec", "T", "y")}
    if len(arrays) == 2:
        rec["central_df_vs_central"] = compare(arrays["central_df"], arrays["central"], rep, cfg["c2"]["c_rep_rtol"])
        ok = ok and rec["central_df_vs_central"]["pass"]
    else:
        rec["central_df_vs_central"] = {"pass": False, "why": "a reference unit is not this job's verified PASS"}
        ok = False
    rec["verdict"] = "PASS" if ok else "STOP"
    write_contained(cfg, out / "refcheck.json", (json.dumps(rec, indent=1, sort_keys=True) + "\n").encode())
    print(json.dumps(rec, sort_keys=True))
    return 0 if ok else RC_STOP


def barrier_ok(out: Path, bound: dict) -> tuple[bool, str, str | None]:
    """refcheck.json is the bound job's PASS at the bound deploy, with both references passing. The digests it
    records must equal the reference products as they are now. Returns (ok, why, its sha256)."""
    p = out / "refcheck.json"
    if p.is_symlink() or not p.is_file():
        return False, "refcheck.json is absent or a symlink", None
    raw = p.read_bytes()
    try:
        b = json.loads(raw)
    except ValueError:
        return False, "refcheck.json is not JSON", None
    if not isinstance(b, dict):
        return False, "refcheck.json is not an object", None
    if (b.get("verdict"), str(b.get("job")), b.get("deploy_head")) != ("PASS", bound["job"], bound["deploy_head"]):
        return False, f"refcheck.json is {b.get('verdict')} for {b.get('job')}/{b.get('deploy_head')}", None
    for u in REFERENCE_UNITS:
        r = (b.get("units") or {}).get(u) or {}
        m = read_marker(out / f"{u}.done")
        good, why = marker_ok(out, u, bound, u)
        if not (r.get("pass") is True and r.get("srun_rc") == 0 and good
                and (r.get("npz_sha256"), r.get("root_sha256")) == (m.get("sha256"), m.get("root_sha256"))):
            return False, f"refcheck.json's {u} is not a passing reference at its products' digests ({why})", None
    return True, "ok", hashlib.sha256(raw).hexdigest()


def complete(cfg: dict, out: Path, bound: dict) -> int:
    """The job's completion check, which the job publishes as IBUB-DONE. Each of these is a failure:
    - any of the 600 declared toy units that is not this job's verified PASS (``marker_ok``);
    - any marker for an undeclared unit;
    - a barrier receipt that is not this job's PASS at its references' current digests (``barrier_ok``).
    It prints one JSON line, which records the barrier's sha256; exit 0 only when every check holds."""
    expected = [f"toy_{t}_{s}" for t in ("G18", "AR23") for s in c.TOY_SEEDS[t]]
    bad, passed = [], 0
    for name in expected:
        ok, why = marker_ok(out, name, bound, "toy")
        passed += ok
        if not ok:
            bad.append(f"{name}: {why}")
    known = set(expected) | set(REFERENCE_UNITS)
    extra = sorted(f[:-5] for f in os.listdir(out) if f.endswith(".done") and f[:-5] not in known)
    barrier, why, bsha = barrier_ok(out, bound)
    rec = {"schema": "ibub-complete/2", "job": bound["job"], "deploy_head": bound["deploy_head"],
           "toy_pass": passed, "toy_expected": len(expected), "not_pass": bad[:50], "not_pass_count": len(bad),
           "undeclared_markers": extra, "barrier_pass": barrier, "barrier_why": why, "barrier_sha256": bsha}
    rec["verdict"] = "PASS" if (passed == len(expected) and not extra and barrier) else "FAIL"
    print(json.dumps(rec, sort_keys=True))
    return 0 if rec["verdict"] == "PASS" else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("stage")
    sub.add_parser("preflight")
    r = sub.add_parser("run")
    r.add_argument("--unit", action="append", required=True)
    r.add_argument("--out", type=Path, required=True)
    b = sub.add_parser("refcheck")
    b.add_argument("--out", type=Path, required=True)
    b.add_argument("--time", action="append", default=[], metavar="UNIT=PATH",
                   help="the /usr/bin/time -v file of each reference unit's srun step")
    b.add_argument("--step-rc", action="append", default=[], metavar="UNIT=RC",
                   help="each reference unit's srun step exit status, as the job waited for it")
    d = sub.add_parser("complete")
    d.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    cfg = load_config()
    try:
        check_code(cfg)
        if a.cmd == "stage":
            return stage(cfg)
        if a.cmd == "preflight":
            return preflight(cfg)
        out = inside(cfg, a.out)                     # every write of run, refcheck and complete stays under $N
        bound = binding()
        rep = reported_cells(cfg)
        if a.cmd == "refcheck":
            times, step_rcs = {}, {}
            for t in a.time:
                u, _, path = t.partition("=")
                if u not in REFERENCE_UNITS or not path:
                    raise ValueError(f"--time {t!r} is not UNIT=PATH for a reference unit")
                times[u] = Path(path)
            for t in a.step_rc:
                u, _, v = t.partition("=")
                if u not in REFERENCE_UNITS or not re.fullmatch(r"-?[0-9]+", v):
                    raise ValueError(f"--step-rc {t!r} is not UNIT=RC for a reference unit")
                step_rcs[u] = int(v)
            return refcheck(cfg, out, rep, bound, times, step_rcs)
        if a.cmd == "complete":
            return complete(cfg, out, bound)
        units = [parse_unit(s) for s in a.unit]
        if len({u["name"] for u in units}) != len(units):
            raise ValueError("a unit is named twice")
        inside(cfg, staging_root(cfg))
        for u in units:                              # C-G2R, before the driver is imported (section 5)
            resolve_argv(cfg, None if u["kind"] == "central" else data_dir(cfg) / f"{u['name']}.root")
        shas = {t: toy_shas(cfg, t) for t in cfg["toys"]}
        verified = check_inputs(cfg)
        ref = read_reference(cfg) if any(u["kind"] in REFERENCE_UNITS for u in units) else None
        driver, ohf = rc.load_driver()
    except (ValueError, GateFailure, OSError) as e:
        print(f"refusing: {e}", file=sys.stderr)
        return RC_GATE
    rc_ = 0
    for u in units:
        rc_ = run_unit(driver, ohf, cfg, u, out, shas=shas, rep=rep, ref=ref, bound=bound,
                       inputs_verified=verified) or rc_
    return rc_


if __name__ == "__main__":
    sys.exit(main())

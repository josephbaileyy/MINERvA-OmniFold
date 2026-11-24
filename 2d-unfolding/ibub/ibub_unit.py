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
  refcheck --out DIR    the barrier (section 8): both references PASS, within the re-price trigger, and central_df
                        equal to central; exit 0 lets the toys start

MEASURES: one driver run per unit. CANNOT AUTHORIZE: a reading (``ibub_readout.py`` applies the declared ones).
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import stat
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
    """max |a/b - 1| over b != 0, and inf when a is non-zero where b is zero."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    if a.shape != b.shape:
        return float("inf")
    nz = b != 0
    if np.any(a[~nz] != 0):
        return float("inf")
    return float(np.max(np.abs(a[nz] / b[nz] - 1))) if nz.any() else 0.0


def compare(a: dict, b: dict, rep: np.ndarray, rtol: float) -> dict:
    """C-REP's comparison: xsec at every K of the scan on the 205 cells, and the binned T and y, to rtol."""
    if list(np.asarray(a["ks"])) != list(np.asarray(b["ks"])):
        return {"pass": False, "why": "the K scans differ"}
    xs = max(max_rel(np.asarray(a["xsec"])[i][rep], np.asarray(b["xsec"])[i][rep]) for i in range(len(a["ks"])))
    out = {"xsec_max_rel": xs, "T_max_rel": max_rel(a["T"], b["T"]), "y_max_rel": max_rel(a["y"], b["y"]), "rtol": rtol}
    out["pass"] = bool(max(out["xsec_max_rel"], out["T_max_rel"], out["y_max_rel"]) <= rtol)
    return out


def read_marker(path: Path) -> dict:
    """A done-marker as a dict; an absent, empty or malformed one reads as {} (no verdict, so never PASS)."""
    try:
        m = json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return {}
    return m if isinstance(m, dict) else {}


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
             inputs_verified: dict | None = None, unfolder=None) -> int:
    """One unit; its done-marker carries its control verdict, and only a PASS unit is skipped on a rerun."""
    name = unit["name"]
    root, npz, marker = out / f"{name}.root", out / f"{name}.npz", out / f"{name}.done"
    if npz.exists() or root.exists():
        verdict = read_marker(marker).get("verdict")
        if verdict == "PASS":
            return 0
        print(f"refusing: {name} exists without a PASS done-marker (verdict {verdict})", file=sys.stderr)
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
        prim = xs[c2["primary"]]
        nz = prim != 0
        fill = float(np.max(np.abs(own[nz] / prim[nz] - 1))) if nz.any() else 0.0
        controls["C-FILL"] = {"max_rel": fill, "pass": bool(fill <= c2["c_fill_rtol"] and np.all(own[~nz] == 0))}
        numpy_traj = rc.dagostini(cap["M"], cap["T"], cap["y"], ks)
        roo = max(float(np.max(np.abs(cap["traj"][K] - numpy_traj[K]) / np.maximum(np.abs(numpy_traj[K]), 1e-300)))
                  for K in ks)
        controls["C-ROO"] = {"max_rel": roo, "pass": bool(roo <= c2["c_roo_rtol"])}
        if unit["kind"] == "central":
            controls["C-SIM"] = rc.c_sim(driver, cap, rc.dagostini, ks, c2["c_sim_rtol"])
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
                "slurm_job": os.environ.get("SLURM_JOB_ID"), "cpus": cpus, "thread_env": threads,
                "measured_weights_sha256": hashlib.sha256(cap["measured_weights"].tobytes()).hexdigest(),
                "controls": controls, "seconds": round(time.time() - t0, 3)}
        if set(controls) != CONTROLS[unit["kind"]]:
            raise GateFailure(f"{name}: controls {sorted(controls)} are not the declared {sorted(CONTROLS[unit['kind']])}")
        passed = all(v["pass"] for v in controls.values())
        np.savez_compressed(npz, **arrays, meta=json.dumps(meta, default=str))
        marker.write_text(json.dumps({"unit": name, "kind": unit["kind"], "tune": unit["tune"], "seed": unit["seed"],
                                      "verdict": "PASS" if passed else "FAIL", "seconds": meta["seconds"],
                                      "sha256": rc.sha256(npz), "root_sha256": rc.sha256(root),
                                      "data_sha256": data_sha}) + "\n")
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
    root.mkdir(parents=True, exist_ok=True)
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
    (root / "stage.json").write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n")
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


def refcheck(cfg: dict, out: Path, rep: np.ndarray) -> int:
    """The barrier: both reference units PASS (C-REP, C-REP-D), each within the re-price trigger, and central_df's
    cross sections equal central's to C-REP's tolerance. Writes refcheck.json; 0 lets the toys start."""
    rec, ok = {"schema": "ibub-refcheck/1", "units": {}}, True
    limit = cfg["price"]["reprice_factor"] * cfg["price"]["unit_s"]
    arrays = {}
    for u in REFERENCE_UNITS:
        marker, npz, root = out / f"{u}.done", out / f"{u}.npz", out / f"{u}.root"
        m = read_marker(marker)
        good = (m.get("verdict") == "PASS" and m.get("unit") == u and npz.exists() and root.exists()
                and rc.sha256(npz) == m.get("sha256") and rc.sha256(root) == m.get("root_sha256"))
        secs = m.get("seconds")
        fast = isinstance(secs, (int, float)) and secs <= limit
        rec["units"][u] = {"verdict": m.get("verdict"), "seconds": secs, "limit_s": limit, "pass": bool(good and fast)}
        ok = ok and good and fast
        if good:
            z = np.load(npz)
            arrays[u] = {k: z[k] for k in ("ks", "xsec", "T", "y")}
    if len(arrays) == 2:
        rec["central_df_vs_central"] = compare(arrays["central_df"], arrays["central"], rep, cfg["c2"]["c_rep_rtol"])
        ok = ok and rec["central_df_vs_central"]["pass"]
    else:
        rec["central_df_vs_central"] = {"pass": False, "why": "a reference unit is missing or not PASS"}
        ok = False
    rec["verdict"] = "PASS" if ok else "STOP"
    (out / "refcheck.json").write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n")
    print(json.dumps(rec, sort_keys=True))
    return 0 if ok else RC_STOP


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
    a = ap.parse_args(argv)
    cfg = load_config()
    try:
        check_code(cfg)
        if a.cmd == "stage":
            return stage(cfg)
        if a.cmd == "preflight":
            return preflight(cfg)
        rep = reported_cells(cfg)
        if a.cmd == "refcheck":
            return refcheck(cfg, a.out, rep)
        units = [parse_unit(s) for s in a.unit]
        if len({u["name"] for u in units}) != len(units):
            raise ValueError("a unit is named twice")
        shas = {t: toy_shas(cfg, t) for t in cfg["toys"]}
        verified = check_inputs(cfg)
        ref = read_reference(cfg) if any(u["kind"] in REFERENCE_UNITS for u in units) else None
        driver, ohf = rc.load_driver()
    except (ValueError, GateFailure, OSError) as e:
        print(f"refusing: {e}", file=sys.stderr)
        return RC_GATE
    rc_ = 0
    for u in units:
        rc_ = run_unit(driver, ohf, cfg, u, a.out, shas=shas, rep=rep, ref=ref, inputs_verified=verified) or rc_
    return rc_


if __name__ == "__main__":
    sys.exit(main())

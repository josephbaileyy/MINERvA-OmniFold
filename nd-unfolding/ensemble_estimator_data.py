#!/usr/bin/env python3
"""E96-DATA (draft): the ensemble-averaged estimator E_96 on the real data, beside configuration (e)'s data result.

Declaration (draft): docs/orchestration/state/measurement-paper/5d-community-20261024/fd/e96-data-20261110/
E96D-DECLARATION.md. Nothing here runs before the LL5D readout and the director's go.

ENS1 (``ensemble_estimator_probe.py``, bound, unchanged) refuses the data by design (its stability and closure
namespaces, and FD-STAB's ``estimator_stability_probe.py:215,481``). This module is the separately declared data role.
It reuses ENS1's internal jitter byte for byte (``eep.internal_jitter``, ``eep.moved_rows``, ``eep.BASE_SEED``) and
calls the bound runner ``s5p_numerics.main`` directly with ``--construction data``:

    ensemble_estimator_data.py control  --runs DIR -- <s5p_numerics args, --pairs=-:->   (e)'s own path (float32),
                                                                                       which must equal fb5cc679's
    ensemble_estimator_data.py base     --runs DIR -- <s5p_numerics args, --pairs=-:0>   F64: float64, no jitter
    ensemble_estimator_data.py ensemble --k K[,K...] --runs DIR -- <..., --pairs=-:0>     F(y + delta_k(y)), k in 1..96
    ensemble_estimator_data.py tasks --out-dir DIR --runs DIR --npz P --bkg P
    ensemble_estimator_data.py expect <a task's argv>
    ensemble_estimator_data.py analyze --runs DIR --e-product P --definition P --data-product P --out P

Rebindings for one runner call, each restored on exit:
* ``s5p_numerics.jittered``: in 'base' and 'ensemble', seed 0 is the float64 copy ``jittered(inputs, bkg, None)``
  (ENS1's rule); in 'ensemble', delta_k is then added; any other jitter seed is refused. In 'control' it refuses,
  because (e)'s path takes no jitter;
* ``s5n_pseudo.write_product``: the meta gains an ``e96_data`` block; nothing is written unless the namespace check
  ran;
* ``argparse.ArgumentParser.parse_args``: the runner's arguments must be exactly the declared data call.

MEASURES: single fits on the data and their average. CANNOT AUTHORIZE: an adoption of E_96, any change to (e), its
uncertainty or any record, or a reading (the director reads the committed record once).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from contextlib import contextmanager
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import ensemble_estimator_probe as eep  # noqa: E402
import rounding_mechanism_probe as rmp  # noqa: E402
import s5n_pseudo  # noqa: E402
import s5p_numerics  # noqa: E402

SCHEMA = "e96-data/1"
FAMILY = "e96data"                       # the job-name family (no repo hits for "e96data" at origin/main 1f37b251)
N_ENS = eep.N_ENS                        # 96
BASE_SEED = eep.BASE_SEED                # 0
MODES = ("control", "base", "ensemble")
PAIR = {"control": (None, None), "base": (None, BASE_SEED), "ensemble": (None, BASE_SEED)}
PAIR_TEXT = {"control": "-:-", "base": f"-:{BASE_SEED}", "ensemble": f"-:{BASE_SEED}"}
def declared() -> dict:
    """The declared data call: (e)'s own inputs and settings (docs/orchestration/state/s5p/s2-num-tasks.tsv:2,
    n1_data_ctrl: of_inputs_5d.npz 07fccc1a, bkg_dump.npz 2addac8f, config R, 5 iterations, 32 threads, estimator
    seed 42), which are FD-STAB's, RS1's and ENS1's inputs and settings too: read from ``rmp.STABILITY`` at call time,
    so there is one source (a test pins its production values to (e)'s argv)."""
    s = rmp.STABILITY
    return {"npz_sha256": s["npz_sha256"], "bkg_sha256": s["bkg_sha256"], "iters": s["iters"],
            "threads": s["threads"], "estimator_seed": s["estimator_seed"], "config": "R"}
E_PRODUCT_SHA256 = "fb5cc6798b97b5902ad8f0fecbc49990271f7772f98d3063c1dc8596340e680c"   # (e)'s data_b-_j-.npz
CHUNK = 2                                # internal seeds per task, as ENS1 (§8)


class Refusal(RuntimeError):
    pass


def sha256_path(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


# ----------------------------------------------------------------------------------------------- the check
def check_data_namespace(ns, mode: str) -> str | None:
    """The declared data call exactly: (e)'s inputs and settings, the data construction, one declared pair."""
    DATA = declared()
    if getattr(ns, "construction", None) != "data":
        return "E96-DATA runs only --construction data"
    if getattr(ns, "expect_npz_sha256", None) != DATA["npz_sha256"] or \
            getattr(ns, "expect_bkg_sha256", None) != DATA["bkg_sha256"]:
        return "the expected input digests are not (e)'s of_inputs_5d.npz and bkg_dump.npz"
    if getattr(ns, "config", None) != DATA["config"]:
        return "--config must be R"
    for key in ("iters", "threads", "estimator_seed"):
        if getattr(ns, key, None) != DATA[key]:
            return f"--{key.replace('_', '-')} must be {DATA[key]}"
    if getattr(ns, "capacity", None) is not None:
        return "--capacity is refused: the estimator is (e)'s"
    for key in ("pseudo_seed", "pseudo_seeds", "fixed_split_seed", "eavail_ratio"):
        if getattr(ns, key, None) is not None:
            return f"--{key.replace('_', '-')} is refused for the data"
    if getattr(ns, "truth", None) != "nominal" or float(getattr(ns, "amplitude", -1)) != 0.0:
        return "--truth and --amplitude stay at the runner's defaults for the data"
    pairs = s5p_numerics.parse_pairs(getattr(ns, "pairs", ""))
    if pairs != [PAIR[mode]]:
        return f"mode {mode} runs the single pair {PAIR_TEXT[mode]}"
    return None


# ------------------------------------------------------------------------------------------------ the install
@contextmanager
def install(mode: str, k: int | None):
    """Rebind for one runner call: 'control' ((e)'s path), 'base' (F64) or 'ensemble' (internal seed k)."""
    if mode not in MODES:
        raise ValueError(f"unknown mode {mode!r}")
    if (mode == "ensemble") != (k is not None):
        raise ValueError("only the ensemble takes an internal seed")
    here, probe = sha256_path(Path(__file__).resolve()), sha256_path(Path(eep.__file__).resolve())
    st = {"checked": False}
    item: dict = {}
    saved = {"jittered": s5p_numerics.jittered, "write_product": s5n_pseudo.write_product,
             "parse_args": argparse.ArgumentParser.parse_args}
    o = dict(saved)

    def jittered(inputs, bkg, seed):
        if mode == "control":
            raise Refusal("the control is (e)'s own path: no jitter, no float64 copy")
        if seed != BASE_SEED:
            raise Refusal(f"jitter seed {seed} is not the declared {BASE_SEED}")
        item["protocol_seed"] = seed
        ji, jb = o["jittered"](inputs, bkg, None)                    # the float64 copy (ENS1's rule for seed 0)
        if k is not None:
            ji, jb, item["coord_sha256"] = eep.internal_jitter(ji, jb, k)
        item["moved_rows"] = eep.moved_rows(inputs, bkg, ji, jb)
        print(f"[e96data] grid membership moved rows {item['moved_rows']}", file=sys.stderr)
        return ji, jb

    def write_product(out, arrays, meta):
        if not st["checked"]:
            raise Refusal("refusing to write: the runner's arguments were never checked by E96-DATA")
        block = {"schema": SCHEMA, "mode": mode, "k": k,
                 "internal_seed": None if k is None else eep.INTERNAL_BASE + k,
                 "protocol_seed": item.get("protocol_seed"), "coord_sha256": item.get("coord_sha256"),
                 "moved_rows": item.get("moved_rows"), "code_sha256": here, "ens1_probe_sha256": probe}
        item.clear()
        return o["write_product"](out, arrays, {**meta, "e96_data": block})

    def parse_args(self, args=None, namespace=None):
        ns = o["parse_args"](self, args, namespace)
        if not (hasattr(ns, "pairs") and hasattr(ns, "construction")):
            return ns
        why = check_data_namespace(ns, mode)
        if why:
            print(f"refusing: {why}", file=sys.stderr)
            raise SystemExit(2)
        st["checked"] = True
        return ns

    s5p_numerics.jittered = jittered
    s5n_pseudo.write_product, argparse.ArgumentParser.parse_args = write_product, parse_args
    try:
        yield item
    finally:
        s5p_numerics.jittered = saved["jittered"]
        s5n_pseudo.write_product = saved["write_product"]
        argparse.ArgumentParser.parse_args = saved["parse_args"]


def _replace(argv: list[str], opt: str, value: str) -> list[str]:
    out = [t for i, t in enumerate(argv) if t != opt and (i == 0 or argv[i - 1] != opt)]
    return out + [opt, value]


def tag_of(mode: str, k: int | None) -> str:
    return {"control": f"{FAMILY}_E", "base": f"{FAMILY}_F64"}.get(mode) or f"{FAMILY}_k{k:03d}"


def run(mode: str, ks: list[int | None], rest: list[str], runs: Path) -> int:
    """One process, one bound-runner call per internal seed; the first non-zero rc stops the task."""
    for k in ks:
        argv = _replace(_replace(rest, "--tag", tag_of(mode, k)), "--out", str(runs / mode))
        try:
            with install(mode, k):
                rc = s5p_numerics.main(argv)
        except Refusal as exc:
            print(f"refusing: {exc}", file=sys.stderr)
            return 5
        if rc:
            return rc
    return 0


# ------------------------------------------------------------------------------------------------- the queue
def data_args(a, mode: str) -> list[str]:
    DATA = declared()
    return ["--npz", str(a.npz), "--bkg", str(a.bkg), "--expect-npz-sha256", DATA["npz_sha256"],
            "--expect-bkg-sha256", DATA["bkg_sha256"], "--config", "R", "--iters", str(DATA["iters"]),
            "--threads", str(DATA["threads"]), "--construction", "data", f"--pairs={PAIR_TEXT[mode]}"]


DRY_KS = (1,)                            # the dry run: the control and k = 1, one unfold each (E96D §Price)


def task_lines(a) -> tuple[list[str], list[str]]:
    """(dry, full); each line: id, unfolds, script, argv. Dry: the control and k = 1. Full: the F64 base, then k = 2..96
    in tasks of CHUNK (the dry run's products carry in, so the full run never repeats them)."""
    common = ["--runs", str(a.runs)]

    def line(tid, n, argv):
        return "\t".join([tid, str(n), "ensemble_estimator_data.py", *argv])

    def ens(grp):
        return line(f"{FAMILY}_k{grp[0]:03d}", len(grp), ["ensemble", "--k", ",".join(map(str, grp)), *common,
                                                          "--", *data_args(a, "ensemble")])
    dry = [line(f"{FAMILY}_E", 1, ["control", *common, "--", *data_args(a, "control")])] + [ens([k]) for k in DRY_KS]
    full = [line(f"{FAMILY}_F64", 1, ["base", *common, "--", *data_args(a, "base")])]
    ks = [k for k in range(1, N_ENS + 1) if k not in DRY_KS]
    for i in range(0, len(ks), CHUNK):
        full.append(ens(ks[i:i + CHUNK]))
    return dry, full


def parse_task(argv: list[str]):
    if argv[:1] not in [[m] for m in MODES] or "--" not in argv:
        raise ValueError("usage: ensemble_estimator_data.py {control | base | ensemble --k LIST} --runs DIR -- <args>")
    mode, cut = argv[0], argv.index("--")
    ap = argparse.ArgumentParser(prog=f"ensemble_estimator_data.py {mode}", allow_abbrev=False)
    ap.add_argument("--runs", type=Path, required=True)
    if mode == "ensemble":
        ap.add_argument("--k", required=True)
    a = ap.parse_args(argv[1:cut])
    ks: list[int | None] = [int(v) for v in a.k.split(",")] if mode == "ensemble" else [None]
    if mode == "ensemble" and (len(set(ks)) != len(ks) or any(k not in range(1, N_ENS + 1) for k in ks)):
        raise ValueError(f"--k must be distinct values in 1-{N_ENS}")
    return mode, ks, argv[cut + 1:], a.runs


def expected_outputs(argv: list[str]) -> list[Path]:
    """Every product a task writes, as ``run`` names them (the job script's teardown guard reads this)."""
    mode, ks, rest, runs = parse_task(argv)
    b, j = PAIR[mode]
    return [runs / mode / s5p_numerics.product_name(tag_of(mode, k), b, j) for k in ks]


# ---------------------------------------------------------------------------------------------- the analysis
def load_product(p: Path) -> tuple[np.ndarray, dict]:
    with np.load(p, allow_pickle=False) as z:
        return np.asarray(z["xsec_flat"], np.float64), json.loads(str(z["meta"]))


def product_problems(meta: dict, mode: str, k: int | None) -> list[str]:
    """Each product must be the declared data call of its mode, from one E96-DATA code."""
    DATA = declared()
    out = []
    blk = meta.get("e96_data") or {}
    want_j = PAIR[mode][1]
    if meta.get("construction") != "data":
        out.append("construction is not data")
    if meta.get("input_npz_sha256") != DATA["npz_sha256"] or meta.get("bkg_dump_sha256") != DATA["bkg_sha256"]:
        out.append("inputs are not (e)'s")
    if meta.get("bootstrap_seed") is not None or meta.get("jitter_seed") != want_j:
        out.append(f"pair is not {PAIR_TEXT[mode]}")
    if meta.get("coords") != ("float32" if mode == "control" else "float64"):
        out.append(f"coords {meta.get('coords')!r} is not the mode's")
    if (meta.get("estimator_seed"), meta.get("threads"), meta.get("iters")) != \
            (DATA["estimator_seed"], DATA["threads"], DATA["iters"]):
        out.append("estimator seed, threads or iterations are not (e)'s")
    if blk.get("schema") != SCHEMA or blk.get("mode") != mode or blk.get("k") != k:
        out.append("the e96_data block is not this mode and k")
    if mode != "control" and any((blk.get("moved_rows") or {"_": 1}).values()):
        out.append("rows moved across the grid")
    return out


def analyze(a, e_sha: str = E_PRODUCT_SHA256) -> int:
    """The controls (A-D0 .. A-D2), then E_96's sixteen cells beside (e)'s and F64's. Exit 8 on a failed control."""
    sys.path.insert(0, str(_ND))
    import s1_assemble as sa
    rec = {"schema": SCHEMA + "/analysis", "controls": {}, "label":
           "descriptive (E96D-DECLARATION.md): a statement about the real data; no adoption, no uncertainty, "
           "no change to (e)"}
    fail = []

    def control(name, ok, detail=None):
        rec["controls"][name] = {"pass": bool(ok), **({"detail": detail} if detail is not None else {})}
        if not ok:
            fail.append(name)

    def finish(rc):
        p = a.out if rc == 0 else a.out.with_name(a.out.stem + ".STOP.json")
        p.write_text(json.dumps(rec, indent=1) + "\n")
        print(f"E96-DATA analysis {'OK' if rc == 0 else 'STOP'} rc={rc}; controls failed: {fail}")
        return rc

    # A-D0: the inputs. (e)'s product and the committed data product
    control("A-D0 (e)'s product is fb5cc679", sha256_path(a.e_product) == e_sha)
    dp = json.loads(a.data_product.read_text())
    if fail:
        return finish(8)
    x_e, _ = load_product(a.e_product)
    U = sa.functional_matrix(sa.fine_map(a.definition))
    f_dp = np.asarray(dp["f"], np.float64)
    f_e = U @ x_e
    control("A-D0 U @ (e)'s xsec_flat equals the data product's f to 1e-12",
            bool(np.allclose(f_e, f_dp, rtol=1e-12, atol=0)), {"max_rel": float(np.max(np.abs(f_e / f_dp - 1)))})

    # A-D1: the control rerun is (e)'s product bitwise (the deploy, threads and runner reproduce (e))
    pc = a.runs / "control" / s5p_numerics.product_name(tag_of("control", None), None, None)
    x_c, m_c = load_product(pc)
    pc_probs = product_problems(m_c, "control", None)
    control("A-D1 the control equals (e)'s xsec_flat bitwise, and is the declared call",
            x_c.tobytes() == x_e.tobytes() and not pc_probs, {"problems": pc_probs})

    # A-D2: F64 and the 96 fits, complete, each the declared call, one code, distinct jitters
    pb = a.runs / "base" / s5p_numerics.product_name(tag_of("base", None), None, BASE_SEED)
    x_b, m_b = load_product(pb)
    probs = product_problems(m_b, "base", None)
    X, codes, digests, missing = [], set(), set(), []
    for k in range(1, N_ENS + 1):
        p = a.runs / "ensemble" / s5p_numerics.product_name(tag_of("ensemble", k), None, BASE_SEED)
        if not p.is_file():
            missing.append(k)
            continue
        x, m = load_product(p)
        probs += [f"k{k}: {q}" for q in product_problems(m, "ensemble", k)]
        blk = m.get("e96_data") or {}
        codes.add((blk.get("code_sha256"), blk.get("ens1_probe_sha256"), json.dumps(m.get("code_sha256"), sort_keys=True)))
        digests.add(json.dumps(blk.get("coord_sha256"), sort_keys=True))
        X.append(x)
    control("A-D2 F64 and 96 fits, each the declared call, one code, 96 distinct jitters",
            not missing and not probs and len(codes) == 1 and len(digests) == N_ENS,
            {"missing": missing, "problems": probs[:20], "codes": len(codes), "distinct_jitters": len(digests)})
    if fail:
        return finish(8)

    # the results
    X = np.stack(X)
    x_E = X.mean(axis=0)
    F = X @ U.T                                     # the 96 fits' sixteen cells
    f_E, f_B = U @ x_E, U @ x_b
    sd_mean = F.std(axis=0, ddof=1) / np.sqrt(N_ENS)
    sig_e = np.asarray(dp["relative_sigma"]["C_e"], np.float64)
    rel = lambda a_, b_: (a_ / b_ - 1.0)            # noqa: E731
    rec["cells"] = dp["cells"]
    rec["sixteen"] = {
        "E96_over_e_minus_1": rel(f_E, f_e).tolist(), "F64_over_e_minus_1": rel(f_B, f_e).tolist(),
        "E96_over_F64_minus_1": rel(f_E, f_B).tolist(),
        "E96_mean_sd_over_e": (sd_mean / f_e).tolist(),
        "E96_minus_e_over_sigma_Ce": (rel(f_E, f_e) / sig_e).tolist(),
        "F64_minus_e_over_sigma_Ce": (rel(f_B, f_e) / sig_e).tolist(),
        "label": "relative to (e)'s f (the committed data product); sigma_Ce is the data product's relative_sigma.C_e; "
                 "the sd of the mean is over the 96 fits / sqrt(96)"}
    rec["inputs_sha256"] = {"e_product": sha256_path(a.e_product), "data_product": sha256_path(a.data_product),
                            "definition": sha256_path(a.definition)}
    return finish(0)


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["tasks"]:
        ap = argparse.ArgumentParser(prog="ensemble_estimator_data.py tasks", allow_abbrev=False)
        for opt in ("--out-dir", "--runs", "--npz", "--bkg"):
            ap.add_argument(opt, type=Path, required=True)
        a = ap.parse_args(argv[1:])
        dry, full = task_lines(a)
        a.out_dir.mkdir(parents=True, exist_ok=True)
        head = "# E96-DATA (E96D-DECLARATION.md); columns: id, unfolds, script, argv"
        for name, lines in (("dry.tsv", dry), ("full.tsv", full)):
            (a.out_dir / name).write_text("\n".join([head, *lines]) + "\n")
        n = lambda ls: sum(int(l.split("\t")[1]) for l in ls)  # noqa: E731
        print(json.dumps({"dry_tasks": len(dry), "dry_unfolds": n(dry), "full_tasks": len(full), "full_unfolds": n(full)}))
        return 0
    if argv[:1] == ["expect"]:
        try:
            print("\n".join(str(p) for p in expected_outputs(argv[1:])))
        except (ValueError, SystemExit) as exc:
            print(f"refusing: {exc}", file=sys.stderr)
            return 2
        return 0
    if argv[:1] == ["analyze"]:
        ap = argparse.ArgumentParser(prog="ensemble_estimator_data.py analyze", allow_abbrev=False)
        for opt in ("--runs", "--e-product", "--definition", "--data-product", "--out"):
            ap.add_argument(opt, type=Path, required=True)
        return analyze(ap.parse_args(argv[1:]))
    try:
        mode, ks, rest, runs = parse_task(argv)
    except ValueError as exc:
        print(f"refusing: {exc}", file=sys.stderr)
        return 2
    return run(mode, ks, rest, runs)


if __name__ == "__main__":
    sys.exit(main())

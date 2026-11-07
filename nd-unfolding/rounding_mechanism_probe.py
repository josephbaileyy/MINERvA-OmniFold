#!/usr/bin/env python3
"""RS1: which channel carries configuration (e)'s rounding spread. One arm through the bound stability path.

Declaration: docs/orchestration/state/measurement-paper/5d-community-20261024/fd/rounding-stability-20261106/
RS1-DECLARATION.md (§3-§4 the arms, §8 this module). Authority: DECISION-20261106-joseph-diagnoses-jinst-corrections.md
item 1.3; DECISION-20261106-joseph-plateau-next-work.md item 1.

    rounding_mechanism_probe.py run --arm ARM [--contract P --h2-definition P] -- <s5p_numerics.py arguments>
    rounding_mechanism_probe.py tasks --out TSV --dry-out TSV --npz P --bkg P --expect-npz-sha256 H
                                      --expect-bkg-sha256 H --runs DIR

``run`` installs ONE arm's rebindings and then calls ``estimator_stability_probe.main`` as FD-STAB's ``control``
stability path, unchanged. It installs first, so the bound probe's own ``install`` captures this module's functions as
its originals and composes over them. Every rebinding is of a name the bound code resolves at call time:

* ``s5p_numerics.jittered``: seed 0 (``UNJITTERED_F64``, never a protocol seed) returns ``jittered(inputs, bkg,
  None)``, the step-free float64 copy (audit E2). The S arms also keep seed 0's arrays for the second experiment;
* ``s5e_trace.jitter_coords``: F_k zeroes the other axes' steps of the protocol's own draws; V is the value-keyed,
  tie- and order-preserving jitter (``value_keyed_jitter``);
* ``s5n_pseudo.build_pseudo`` (S arms): also builds the experiment from the unjittered inputs and requires every
  non-coordinate array to be bitwise equal (row alignment);
* ``s5p_numerics.unfold_one``: S arms hand one consumer the unjittered arrays (S-all none, the identity G4); A0
  traces each unfold with ``s5e_trace.traced_unfold`` and a ``Recorder``, imported unchanged;
* ``s5c_unfold.config_params`` (B arms): adds ``max_bin``, which the OmniFold estimators and the refinement both read;
* ``s5c_unfold.unfold`` (P arms): ``s5c_unfold.permute`` first;
* ``omnifold_nn_core.make_estimators`` and ``s5n_pseudo.recorded_classifier`` (A0, V): record each fit's split table;
* ``s5e_trace.measured_side``: record the refinement's zero-weight rows and the W = 0 counts;
* ``s5n_pseudo.write_product``: every product's meta gains a ``rounding_mechanism`` block, and a sidecar
  ``<product>.trace.json.gz`` carries the readouts;
* ``argparse.ArgumentParser.parse_args``: the runner's parsed arguments must be the declared stability input, with the
  arm's declared pairs only; no product is written unless that check ran.

MEASURES: one arm's products. CANNOT AUTHORIZE: a reading (``rounding_mechanism_analyze.py`` evaluates §5), a
mechanism, or any change to the estimator.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import sys
from contextlib import ExitStack, contextmanager
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import estimator_stability_probe as esp  # noqa: E402
import omnifold_nn_core as onc  # noqa: E402
import s5c_unfold  # noqa: E402
import s5e_trace  # noqa: E402
import s5n_pseudo  # noqa: E402
import s5p_numerics  # noqa: E402

SCHEMA = "rs1-rounding-mechanism/1"
UNJITTERED_F64 = 0          # jitter seed 0: float64 coordinates with no step (FD-STAB's seeds are 1-51)
SEEDS = tuple(range(1, 21))  # 20 jitter seeds (the director's E3 ruling)
AXES = ("pt", "pz", "eavail", "q3", "W")  # s5c_coverage.AXES
W_AXIS = 4
VALUE_KEY = 0x0B51_2026_1106
DUMP_SEEDS = {"A0": (None, UNJITTERED_F64, 1, 2, 3), "V": (1, 2, 3)}
STABILITY = {"truth": "eavail_shape", "amplitude": 1.0, "ratio": esp.STABILITY_TRUTH["ratio"],
             "ratio_sha256": esp.STABILITY_TRUTH["ratio_sha256"], "pseudo_seed": esp.STABILITY_PSEUDO_SEED,
             "iters": 5, "threads": 32, "estimator_seed": 42}


def _arms() -> dict:
    j = [f"-:{s}" for s in SEEDS]
    arms = {"A0": {"jitter": "protocol", "trace": True, "pairs": ["-:-", f"-:{UNJITTERED_F64}"] + j},
            "V": {"jitter": "value", "pairs": j}}
    for k, ax in enumerate(AXES):
        arms[f"F_{ax}"] = {"jitter": "axis", "axis": k, "pairs": j}
    arms["S_ref"] = {"jitter": "protocol", "side": "ref", "pairs": j}
    arms["S_omni"] = {"jitter": "protocol", "side": "omni", "pairs": j}
    arms["S_all"] = {"jitter": "protocol", "side": "all", "pairs": j[:3]}
    for nb in (63, 1023):
        arms[f"B{nb}"] = {"jitter": "protocol", "max_bin": nb, "pairs": [f"-:{UNJITTERED_F64}"] + j}
    for ps in (1, 2):
        arms[f"P{ps}"] = {"jitter": "protocol", "permute": ps, "pairs": [f"-:{UNJITTERED_F64}"]}
    return arms


ARMS = _arms()


class Refusal(RuntimeError):
    pass


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 22), b""):
            h.update(block)
    return h.hexdigest()


# --------------------------------------------------------------------------------------------- jitters

def _splitmix64(z: np.ndarray) -> np.ndarray:
    z = z.astype(np.uint64)
    with np.errstate(over="ignore"):
        z = z + np.uint64(0x9E3779B97F4A7C15)
        z = (z ^ (z >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)
        z = (z ^ (z >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)
        return z ^ (z >> np.uint64(31))


def ulp_toward_zero(x32: np.ndarray) -> np.ndarray:
    """|x| - nextafter(|x|, 0) in float32 (exact by Sterbenz), as float64; 0 for x = 0."""
    a = np.abs(np.asarray(x32, np.float32))
    return (a - np.nextafter(a, np.float32(0))).astype(np.float64)


def value_keyed_jitter(x: np.ndarray, seed: int | None, edges: list | None = None) -> np.ndarray:
    """float64 copy; with a seed, each value moves by u * 1/2 * ulp_toward_zero, u in [-1, 1) a keyed hash of (seed, axis,
    float32 bits). Equal float32 values move identically in every array, and the order of distinct values is kept
    strictly (each moves by less than half the gap to either neighbour). Grid-edge values are not moved."""
    x32 = np.asarray(x, np.float32)
    out = x32.astype(np.float64)
    if seed is None:
        return out
    bits = x32.view(np.uint32).astype(np.uint64)
    step = np.zeros_like(out)
    for k in range(out.shape[1]):
        key = _splitmix64(np.array([(int(seed) << 8) ^ k ^ VALUE_KEY], np.uint64))[0]
        h = _splitmix64(bits[:, k] ^ key)
        u = (h >> np.uint64(11)).astype(np.float64) * 2.0 ** -53 * 2.0 - 1.0
        step[:, k] = u * 0.5 * ulp_toward_zero(x32[:, k])
    if edges is not None:
        for k, e in enumerate(edges):
            step[np.isin(out[:, k], np.asarray(e, np.float32).astype(np.float64)), k] = 0.0
    return out + step


def axis_jitter(orig, axis: int):
    def jitter(x, seed, edges=None):
        full = orig(x, seed, edges)
        out = orig(x, None, edges)
        if seed is not None:
            out[:, axis] = full[:, axis]
        return out
    return jitter


# ------------------------------------------------------------------------------------------ readouts

def split_table(booster) -> list:
    """Per tree, its nodes in preorder: internal (feature, threshold, gain, count), leaf (value, count)."""
    trees = []
    for t in booster.dump_model()["tree_info"]:
        nodes, stack = [], [t["tree_structure"]]
        while stack:
            n = stack.pop()
            if "split_feature" in n:
                nodes.append(["s", int(n["split_feature"]), float(n["threshold"]), float(n.get("split_gain", 0.0)),
                              int(n.get("internal_count", -1))])
                stack.extend([n["right_child"], n["left_child"]])
            else:
                nodes.append(["l", float(n.get("leaf_value", 0.0)), int(n.get("leaf_count", -1))])
        trees.append(nodes)
    return trees


def shared_fraction(X: np.ndarray) -> list:
    """Per axis, the share of rows whose value is shared with another row."""
    out = []
    X = np.asarray(X)
    for k in range(X.shape[1]):
        _, inv, cnt = np.unique(X[:, k], return_inverse=True, return_counts=True)
        out.append(float((cnt[inv] > 1).mean()) if X.shape[0] else 0.0)
    return out


class Recorded:
    """Pass-through estimator; after each fit, the model's split table goes to ``log`` (when ``log`` is not None)."""

    def __init__(self, base, role: str, log: list | None):
        self.base, self.role, self.log = base, role, log

    @property
    def booster_(self):
        """The wrapped model's booster, so the bound probe's ``min_leaf_count`` reads through this wrapper."""
        return getattr(self.base, "booster_", None)

    def get_params(self, deep: bool = True):
        return self.base.get_params(deep)

    def set_params(self, **params):
        self.base.set_params(**params)
        return self

    def fit(self, X, y, sample_weight=None):
        self.base.fit(X, y, sample_weight=sample_weight)
        if self.log is not None and getattr(self.base, "booster_", None) is not None:
            self.log.append({"role": self.role, "trees": split_table(self.base.booster_)})
        return self

    def predict_proba(self, X):
        return self.base.predict_proba(X)

    def predict(self, X):
        return self.base.predict(X)


# ---------------------------------------------------------------------------------------- the install

ALIGNED = ("obs_counts", "tmpl_w", "w_truth", "w_reco", "pass_reco", "pass_truth")
COORDS = ("MCgen", "MCreco", "obs", "tmpl")


def check_aligned(exp_j: dict, exp_u: dict, xt_j, xt_u) -> None:
    for k in ALIGNED:
        if not np.array_equal(np.asarray(exp_j[k]), np.asarray(exp_u[k])):
            raise Refusal(f"the jittered and unjittered experiments differ in {k}: rows are not aligned")
    for k in COORDS:
        if np.shape(exp_j[k]) != np.shape(exp_u[k]):
            raise Refusal(f"the jittered and unjittered experiments differ in the shape of {k}")
    if (xt_j is None) != (xt_u is None) or (xt_j is not None and not np.array_equal(xt_j, xt_u)):
        raise Refusal("the jittered and unjittered experiments differ in their truth")


def check_namespace(ns, arm: str) -> str | None:
    want = STABILITY
    if getattr(ns, "truth", None) != want["truth"] or float(getattr(ns, "amplitude", -1)) != want["amplitude"]:
        return f"RS1 runs only the declared stability truth {want['truth']} at amplitude {want['amplitude']}"
    ratio = getattr(ns, "eavail_ratio", None)
    if ratio is None or sha256_path(Path(ratio)) != want["ratio_sha256"]:
        return "the --eavail-ratio file is not the declared one"
    for key in ("iters", "threads", "estimator_seed"):
        if getattr(ns, key, None) != want[key]:
            return f"--{key.replace('_', '-')} must be {want[key]}"
    if getattr(ns, "fixed_split_seed", None) is not None or getattr(ns, "pseudo_seeds", None) is not None:
        return "--fixed-split-seed and --pseudo-seeds are refused"
    pairs = s5p_numerics.parse_pairs(getattr(ns, "pairs", ""))
    allowed = set(s5p_numerics.parse_pairs(",".join(ARMS[arm]["pairs"])))
    if any(p not in allowed for p in pairs):
        return f"arm {arm} declares only the pairs {','.join(ARMS[arm]['pairs'])}"
    return None


@contextmanager
def install(arm: str, U: np.ndarray | None = None):
    """Rebind this arm's names for one invocation; restore them on exit. Yields the per-product state."""
    if arm not in ARMS:
        raise ValueError(f"unknown arm {arm!r}")
    cfg = ARMS[arm]
    if cfg.get("trace") and U is None:
        raise ValueError("a traced arm needs the functional matrix U")
    here = sha256_path(Path(__file__).resolve())
    st = {"checked": False}
    item: dict = {}
    saved = {
        "jittered": s5p_numerics.jittered, "unfold_one": s5p_numerics.unfold_one,
        "jitter_coords": s5e_trace.jitter_coords, "measured_side": s5e_trace.measured_side,
        "build_pseudo": s5n_pseudo.build_pseudo, "write_product": s5n_pseudo.write_product,
        "recorded_classifier": s5n_pseudo.recorded_classifier, "config_params": s5c_unfold.config_params,
        "unfold": s5c_unfold.unfold, "make_estimators": onc.make_estimators,
        "parse_args": argparse.ArgumentParser.parse_args,
    }
    o = dict(saved)

    def reset():
        item.clear()
        item.update({"seed": None, "fits": [], "refinement_tree": None})

    reset()

    def dumping() -> bool:
        return arm in DUMP_SEEDS and item["seed"] in DUMP_SEEDS[arm]

    def jittered(inputs, bkg, seed):
        item["seed"] = seed
        if seed == UNJITTERED_F64:
            return o["jittered"](inputs, bkg, None)
        if "side" in cfg:
            item["unjittered"] = o["jittered"](inputs, bkg, None)
        return o["jittered"](inputs, bkg, seed)

    if cfg["jitter"] == "value":
        jitter_coords = value_keyed_jitter
    elif cfg["jitter"] == "axis":
        jitter_coords = axis_jitter(o["jitter_coords"], cfg["axis"])
    else:
        jitter_coords = o["jitter_coords"]

    def build_pseudo(inputs, bkg, *args, **kw):
        exp, xt, info = o["build_pseudo"](inputs, bkg, *args, **kw)
        if "side" in cfg and item["seed"] is not None:
            ui, ub = item.pop("unjittered")
            exp_u, xt_u, _ = o["build_pseudo"](ui, ub, *args, **kw)
            check_aligned(exp, exp_u, xt, xt_u)
            item["exp_u"] = exp_u
        return exp, xt, info

    def measured_side(exp, seed, threads, override, coords_dtype=np.float32):
        feat, w_ref, ev = o["measured_side"](exp, seed, threads, override, coords_dtype)
        if "max_bin" in cfg and ev.get("ran") and (ev.get("classifier_params") or {}).get("max_bin") != cfg["max_bin"]:
            raise Refusal(f"the refinement did not receive max_bin {cfg['max_bin']}")
        item.setdefault("measured_sides", []).append({
            "zero_weight_rows": np.flatnonzero(np.asarray(w_ref) == 0).astype(int).tolist(),
            "n_rows": int(len(w_ref)), "w0_measured": int((np.asarray(feat)[:, W_AXIS] == 0).sum()),
            "w0_mc_reco": int((np.asarray(exp["MCreco"])[:, W_AXIS] == 0).sum())})
        if cfg.get("trace") and item["seed"] in (None, UNJITTERED_F64):
            item["ties_measured"] = shared_fraction(feat)
        return feat, w_ref, ev

    def unfold_one(exp, dtype, seed, threads, iters, unfold_fn=None):
        if "side" in cfg:
            exp_u = item.pop("exp_u", None)
            if exp_u is None:
                raise Refusal("an S arm reached the unfold without its unjittered experiment")
            side = cfg["side"]
            ref_exp = exp if side in ("ref", "all") else exp_u
            loop_exp = exp if side in ("omni", "all") else exp_u
            feat_r, w_ref, ev = s5e_trace.measured_side(ref_exp, seed, threads, None, dtype)
            feat_l = feat_r if loop_exp is ref_exp else s5n_pseudo.signed_sample(loop_exp)[0].astype(dtype)
            unf_in = s5e_trace.unf_inputs(loop_exp, feat_l, w_ref)
            xs, params = (unfold_fn or s5c_unfold.unfold)(unf_in, "deterministic", seed, threads, iters)
            return xs, {"refinement": ev, "estimator_params": params}
        if cfg.get("trace"):
            def traced(unf_in, config, eseed, thr, it):
                m = np.asarray(unf_in["pass_truth"], bool)
                rec = s5e_trace.Recorder(unf_in, np.ones(len(unf_in["pass_truth"])), U, it)
                xs, params, _ = s5e_trace.traced_unfold(unf_in, rec, eseed, thr, it)
                item["fn_push"] = rec.out["fn_push"].tolist()
                if item["seed"] in (None, UNJITTERED_F64):
                    pr = np.asarray(unf_in["pass_reco"], bool)[m]
                    item["ties_mc_truth"] = shared_fraction(np.asarray(unf_in["MCgen"])[m])
                    item["ties_mc_reco"] = shared_fraction(np.asarray(unf_in["MCreco"])[m][pr])
                return xs, params
            return o["unfold_one"](exp, dtype, seed, threads, iters, unfold_fn=traced)
        return o["unfold_one"](exp, dtype, seed, threads, iters, unfold_fn)

    def config_params(config, threads):
        out = o["config_params"](config, threads)
        if config == "deterministic":
            out = {**out, "max_bin": int(cfg["max_bin"])}
        return out

    def unfold(inputs, config, seed, threads, iters):
        return o["unfold"](s5c_unfold.permute(inputs, cfg["permute"]), config, seed, threads, iters)

    def make_estimators(kind, nvars, seed=None):
        ests = o["make_estimators"](kind, nvars, seed=seed)
        log = item["fits"] if dumping() else None
        return tuple(Recorded(e, r, log) for e, r in zip(ests, ("clf1", "clf2", "reg")))

    @contextmanager
    def recorded_classifier(u2d, record):
        with o["recorded_classifier"](u2d, record):
            inner = u2d._make_bkg_classifier

            def factory(estimator, params, device):
                clf = inner(estimator, params, device)
                item["refinement_clf"] = clf
                return clf

            u2d._make_bkg_classifier = factory
            try:
                yield
            finally:
                u2d._make_bkg_classifier = inner

    def write_product(out, arrays, meta):
        if not st["checked"]:
            raise Refusal("refusing to write: the runner's arguments were never checked by RS1")
        clf = item.pop("refinement_clf", None)
        if dumping() and clf is not None and getattr(clf, "booster_", None) is not None:
            item["refinement_tree"] = split_table(clf.booster_)
        seed = item["seed"]
        block = {"schema": SCHEMA, "arm": arm, "config": {k: v for k, v in cfg.items() if k != "pairs"},
                 "jitter_seed": seed, "unjittered_float64": seed == UNJITTERED_F64, "code_sha256": here}
        trace = {k: v for k, v in item.items() if k not in ("seed", "unjittered", "exp_u")}
        side = Path(out).with_name(Path(out).name[:-4] + ".trace.json.gz")
        tmp = side.with_name(side.name + f".partial-{os.getpid()}")
        with gzip.open(tmp, "wt") as fh:
            json.dump({**block, **trace}, fh)
        rc = o["write_product"](out, arrays, {**meta, "rounding_mechanism": block})
        if rc == 0:
            os.replace(tmp, side)
        else:
            tmp.unlink()
        reset()
        return rc

    def parse_args(self, args=None, namespace=None):
        ns = o["parse_args"](self, args, namespace)
        if hasattr(ns, "pairs") and hasattr(ns, "construction"):  # the runner's parser, not another
            why = check_namespace(ns, arm)
            if why:
                print(f"refusing: {why}", file=sys.stderr)
                raise SystemExit(2)
            st["checked"] = True
        return ns

    s5p_numerics.jittered, s5e_trace.jitter_coords = jittered, jitter_coords
    s5n_pseudo.build_pseudo, s5e_trace.measured_side, s5p_numerics.unfold_one = build_pseudo, measured_side, unfold_one
    s5n_pseudo.write_product, argparse.ArgumentParser.parse_args = write_product, parse_args
    if "max_bin" in cfg:
        s5c_unfold.config_params = config_params
    if "permute" in cfg:
        s5c_unfold.unfold = unfold
    if arm in DUMP_SEEDS:
        onc.make_estimators, s5n_pseudo.recorded_classifier = make_estimators, recorded_classifier
    try:
        yield item
    finally:
        s5p_numerics.jittered, s5p_numerics.unfold_one = saved["jittered"], saved["unfold_one"]
        s5e_trace.jitter_coords, s5e_trace.measured_side = saved["jitter_coords"], saved["measured_side"]
        s5n_pseudo.build_pseudo, s5n_pseudo.write_product = saved["build_pseudo"], saved["write_product"]
        s5n_pseudo.recorded_classifier, s5c_unfold.config_params = saved["recorded_classifier"], saved["config_params"]
        s5c_unfold.unfold, onc.make_estimators = saved["unfold"], saved["make_estimators"]
        argparse.ArgumentParser.parse_args = saved["parse_args"]


def functional_matrix(contract: Path, h2_definition: Path) -> np.ndarray:
    """The 153 s5e functionals and the 16 reporting cells, stacked, over the fine grid."""
    import estimator_stability_analyze as esa
    U153, _ = esa.functionals(json.loads(Path(contract).read_text()))
    return np.vstack([U153, esa.cell_matrix(str(h2_definition))])


# ------------------------------------------------------------------------------------------- the queue

DRY = (("A0", "-:-"), ("A0", f"-:{UNJITTERED_F64}"), ("A0", "-:1"), ("V", "-:1"), ("B1023", f"-:{UNJITTERED_F64}"),
       ("B63", f"-:{UNJITTERED_F64}"), ("S_ref", "-:1"), ("S_all", "-:1"), ("P1", f"-:{UNJITTERED_F64}"))
CHUNK = 4
CONTRACT = "docs/orchestration/state/s5c/contract.json"
H2_DEFINITION = "nd-unfolding/pv-ladder/readouts/h2_definition.json"


def task_lines(a) -> tuple[list[str], list[str]]:
    lines, dry_ids = ["# id\tunfolds\tscript\targv (RS1-DECLARATION.md §4, §7)"], []
    for arm, cfg in ARMS.items():
        dry_pairs = [p for (a_, p) in DRY if a_ == arm]
        rest = [p for p in cfg["pairs"] if p not in dry_pairs]
        groups = [[p] for p in dry_pairs] + [rest[i:i + CHUNK] for i in range(0, len(rest), CHUNK)]
        for n, g in enumerate(groups):
            tid = f"rs1_{arm}_{n:02d}"
            if n < len(dry_pairs):
                dry_ids.append(tid)
            extra = ["--contract", CONTRACT, "--h2-definition", H2_DEFINITION] if cfg.get("trace") else []
            argv = ["run", "--arm", arm, *extra, "--",
                    "--npz", str(a.npz), "--bkg", str(a.bkg), "--expect-npz-sha256", a.expect_npz_sha256,
                    "--expect-bkg-sha256", a.expect_bkg_sha256, "--config", "R", "--iters", str(STABILITY["iters"]),
                    "--threads", str(STABILITY["threads"]), "--construction", "pseudo", "--truth", STABILITY["truth"],
                    "--amplitude", str(STABILITY["amplitude"]), "--eavail-ratio", STABILITY["ratio"],
                    "--pseudo-seed", str(STABILITY["pseudo_seed"]), f"--pairs={','.join(g)}", "--tag", f"rs1_{arm}",
                    "--out", str(Path(a.runs) / arm)]
            lines.append("\t".join([tid, str(len(g)), "rounding_mechanism_probe.py", *argv]))
    return lines, dry_ids


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["tasks"]:
        ap = argparse.ArgumentParser(prog="rounding_mechanism_probe.py tasks", allow_abbrev=False)
        for opt in ("--out", "--dry-out", "--npz", "--bkg", "--runs"):
            ap.add_argument(opt, type=Path, required=True)
        ap.add_argument("--expect-npz-sha256", required=True)
        ap.add_argument("--expect-bkg-sha256", required=True)
        a = ap.parse_args(argv[1:])
        lines, dry_ids = task_lines(a)
        a.out.write_text("\n".join(lines) + "\n")
        dry = [l for l in lines if l.split("\t")[0] in dry_ids]
        if len(dry) != len(DRY):
            raise SystemExit("a dry-run task is not in the queue")
        a.dry_out.write_text("\n".join(dry) + "\n")
        print(json.dumps({"tasks": len(lines) - 1, "unfolds": sum(int(l.split("\t")[1]) for l in lines[1:]),
                          "dry": len(dry)}))
        return 0
    if argv[:1] != ["run"] or "--" not in argv:
        print("usage: rounding_mechanism_probe.py run --arm ARM [--contract P --h2-definition P] -- <args>", file=sys.stderr)
        return 2
    cut = argv.index("--")
    ap = argparse.ArgumentParser(prog="rounding_mechanism_probe.py run", allow_abbrev=False)
    ap.add_argument("--arm", choices=sorted(ARMS), required=True)
    ap.add_argument("--contract", type=Path)
    ap.add_argument("--h2-definition", type=Path)
    a = ap.parse_args(argv[1:cut])
    U = None
    if ARMS[a.arm].get("trace"):
        if a.contract is None or a.h2_definition is None:
            print("refusing: a traced arm needs --contract and --h2-definition", file=sys.stderr)
            return 2
        U = functional_matrix(a.contract, a.h2_definition)
    try:
        with install(a.arm, U):
            return esp.main(["--candidate", "control", "stability", "--", *argv[cut + 1:]])
    except Refusal as exc:
        print(f"refusing: {exc}", file=sys.stderr)
        return 5


if __name__ == "__main__":
    sys.exit(main())

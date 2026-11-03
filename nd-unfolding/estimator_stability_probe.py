#!/usr/bin/env python3
"""Estimator-stability probe (STAB): run ONE candidate estimator configuration through the production pipelines.

Declaration: docs/orchestration/state/measurement-paper/5d-community-20261024/FD-STAB-DECLARATION.md. Authority:
DECISION-20261102-joseph-bias-and-stabilisation-routes.md ("Probe, 1B waits").

    estimator_stability_probe.py --candidate C stability -- <s5p_numerics.py arguments>
    estimator_stability_probe.py --candidate C closure   -- <s5p_nullexp.py arguments>
    estimator_stability_probe.py tasks --out TSV --npz P --bkg P --bank D --detector-dir D --expect-npz-sha256 H
                                       --expect-bkg-sha256 H --closure-ratio-dir D --runs D

Candidates (declaration §2). Each is configuration (e) -- s5e candidate R, the refinement at 400 trees and 31 leaves,
the three OmniFold estimators at the deterministic F2 parameters -- with one change to the OmniFold estimators only:

* ``control``: nothing changed;
* ``B2``: 2-fold cross-fitting of the two OmniFold classifiers. Each training row gets a fold from a keyed hash of its
  POSITION (never its values, so a rounding-scale perturbation cannot move it); the classifier of fold f is trained
  on the other fold, and every evaluated row is predicted by the model that did not train on it. In step 2 the two
  copies of an event (label 0 and label 1) share a fold. The regressor already predicts rows it did not train on and
  is unchanged; so is the refinement classifier;
* ``B3a``, ``B3b``: ``min_child_samples`` 10,000 and 100,000 on the three OmniFold estimators.

Nothing in a production module is edited. ``install`` rebinds, for the life of one invocation, the three names the
production code resolves at call time: ``s5c_unfold.config_params`` (B3's parameters, which ``s5c_unfold.unfold``
then verifies on every estimator it built), ``omnifold_nn_core.make_estimators`` (every estimator wrapped in
``Recorded``; B2's classifiers in ``CrossFit``) and ``s5n_pseudo.write_product`` (every product's meta gains a
``stability_probe`` block: the candidate, its override, the fold key, the per-fit minimum leaf counts and this file's
sha256). The control runs through the same wrappers, so a wrapper cannot be what separates a candidate from it.

The data are never read: ``stability`` refuses ``--construction data``, and ``closure`` requires ``--expectation``
and ``--no-nuisance``. A candidate fixes the estimator, so ``--capacity`` and any ``--config`` other than R are refused.

MEASURES: one candidate's products. CANNOT AUTHORIZE: a stability or bias verdict by itself
(``estimator_stability_analyze.py`` evaluates the declared criteria), or the adoption of any estimator.
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
import omnifold_nn_core as onc  # noqa: E402
import s5c_unfold  # noqa: E402
import s5n_pseudo  # noqa: E402

SCHEMA = "estimator-stability-probe/1"
CANDIDATES = {
    "control": {},
    "B2": {"crossfit_k": 2},
    "B3a": {"min_child_samples": 10_000},
    "B3b": {"min_child_samples": 100_000},
}
FOLD_KEY = 0x5AB_B4_2026_1102  # declared; the fold of a row depends only on its position and this key
_MASK = (1 << 64) - 1


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 22), b""):
            h.update(block)
    return h.hexdigest()


def fold_ids(n: int, k: int, key: int = FOLD_KEY, period: int | None = None) -> np.ndarray:
    """Fold of each of n rows: splitmix64(position mod period, xor key) mod k. Values never enter."""
    pos = np.arange(n, dtype=np.uint64)
    if period is not None:
        pos = pos % np.uint64(period)
    z = (pos ^ np.uint64(key & _MASK)) + np.uint64(0x9E3779B97F4A7C15)
    with np.errstate(over="ignore"):
        z = (z ^ (z >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)
        z = (z ^ (z >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)
        z = z ^ (z >> np.uint64(31))
    return (z % np.uint64(k)).astype(np.int64)


def min_leaf_count(est) -> int | None:
    """Smallest training-row count of any leaf of a fitted LightGBM model; None for an estimator without one."""
    booster = getattr(est, "booster_", None)
    if booster is None:
        return None
    best = None
    stack = [t["tree_structure"] for t in booster.dump_model()["tree_info"]]
    while stack:
        node = stack.pop()
        if "leaf_count" in node:
            c = int(node["leaf_count"])
            best = c if best is None else min(best, c)
        stack.extend(node[k] for k in ("left_child", "right_child") if k in node)
    return best


class Recorded:
    """A pass-through estimator: fit, predict and parameters go to the wrapped one; each fit's minimum leaf count is
    appended to ``log``. Forwarding is exact, so a recorded estimator gives bitwise the wrapped one's predictions."""

    def __init__(self, base, role: str, log: list):
        self.base, self.role, self.log = base, role, log

    def get_params(self, deep: bool = True) -> dict:
        return self.base.get_params(deep)

    def set_params(self, **params):
        self.base.set_params(**params)
        return self

    def fit(self, X, y, sample_weight=None):
        self.base.fit(X, y, sample_weight=sample_weight)
        self.log.append({"role": self.role, "folds": 1, "min_leaf_count": [min_leaf_count(self.base)]})
        return self

    def predict_proba(self, X):
        return self.base.predict_proba(X)

    def predict(self, X):
        return self.base.predict(X)


class CrossFit(Recorded):
    """K-fold cross-fitted classifier for the OmniFold loop's ``fit(X) ; predict_proba(X[:m])`` pattern.

    ``paired``: the fit set is two copies of the same m events (OmniFold step 2), which must share a fold; the copies
    are checked to be identical. ``predict_proba(E)`` requires E to be the first len(E) rows of the fit set (the loop
    always evaluates there) and refuses anything else."""

    def __init__(self, base, role: str, log: list, k: int, paired: bool, key: int = FOLD_KEY):
        super().__init__(base, role, log)
        self.k, self.paired, self.key = int(k), bool(paired), int(key)
        self.models, self.X_fit, self.folds = [], None, None

    def set_params(self, **params):
        self.base.set_params(**params)
        for m in self.models:
            m.set_params(**params)
        return self

    def fit(self, X, y, sample_weight=None):
        X = np.asarray(X)
        n = X.shape[0]
        period = None
        if self.paired:
            if n % 2 or not np.array_equal(X[: n // 2], X[n // 2:]):
                raise RuntimeError(f"{self.role}: a paired fit set must be two identical copies")
            period = n // 2
        self.folds = fold_ids(n, self.k, self.key, period)
        w = None if sample_weight is None else np.asarray(sample_weight)
        y = np.asarray(y)
        self.models, counts = [], []
        for f in range(self.k):
            keep = self.folds != f
            if not np.any(keep) or len(np.unique(y[keep])) < 2:
                raise RuntimeError(f"{self.role}: fold {f}'s complement lacks a class")
            m = type(self.base)(**self.base.get_params())
            m.fit(X[keep], y[keep], sample_weight=None if w is None else w[keep])
            self.models.append(m)
            counts.append(min_leaf_count(m))
        self.X_fit = X
        self.log.append({"role": self.role, "folds": self.k, "min_leaf_count": counts})
        return self

    def predict_proba(self, X):
        E = np.asarray(X)
        m = E.shape[0]
        if self.X_fit is None or m > self.X_fit.shape[0] or not np.array_equal(E, self.X_fit[:m]):
            raise RuntimeError(f"{self.role}: cross-fitted prediction is defined only on the leading rows of the fit set")
        out = None
        for f, model in enumerate(self.models):
            rows = self.folds[:m] == f
            if not np.any(rows):
                continue
            p = np.asarray(model.predict_proba(E[rows]))
            if out is None:
                out = np.empty((m, p.shape[1]), dtype=p.dtype)
            out[rows] = p
        return out

    def predict(self, X):
        return np.argmax(self.predict_proba(X), axis=1)


@contextmanager
def install(candidate: str):
    """Rebind the three production names for one invocation; restore them on exit. Yields the fit log."""
    if candidate not in CANDIDATES:
        raise ValueError(f"unknown candidate {candidate!r}")
    override = CANDIDATES[candidate]
    est_params = {k: v for k, v in override.items() if k != "crossfit_k"}
    k = override.get("crossfit_k")
    log: list = []
    orig_params, orig_make, orig_write = s5c_unfold.config_params, onc.make_estimators, s5n_pseudo.write_product
    here = sha256_path(Path(__file__).resolve())

    def config_params(config, threads):
        out = orig_params(config, threads)
        if config == "deterministic" and est_params:
            out = {**out, **est_params}
        return out

    def make_estimators(kind, nvars, seed=None):
        clf1, clf2, reg = orig_make(kind, nvars, seed=seed)
        if k:
            return (CrossFit(clf1, "clf1", log, k, paired=False), CrossFit(clf2, "clf2", log, k, paired=True),
                    Recorded(reg, "reg", log))
        return Recorded(clf1, "clf1", log), Recorded(clf2, "clf2", log), Recorded(reg, "reg", log)

    def write_product(out, arrays, meta):
        meta = {**meta, "stability_probe": {"schema": SCHEMA, "candidate": candidate, "override": override,
                                            "fold_key": FOLD_KEY if k else None, "fits": list(log),
                                            "code_sha256": here}}
        log.clear()
        return orig_write(out, arrays, meta)

    s5c_unfold.config_params, onc.make_estimators, s5n_pseudo.write_product = config_params, make_estimators, write_product
    try:
        yield log
    finally:
        s5c_unfold.config_params, onc.make_estimators, s5n_pseudo.write_product = orig_params, orig_make, orig_write


# ------------------------------------------------------------------------------------------------ the declared tasks
STATE = "docs/orchestration/state"
NULL_J_MNVTUNE = f"{STATE}/s5p/ratios/nullsJ/null-mnvtune_v1-J.json"
NULL_F = {g: f"{STATE}/s5p/ratios/nullsF/null-{g}-F.json" for g in ("genie_cv", "genie_mec", "nuwro_cv", "gibuu_cv")}
NO_RATIO = f"{STATE}/measurement-paper/5d-community-20261024/fd/stab/no-ratio.json"
STABILITY_TRUTH = {"truth": "eavail_shape", "amplitude": 1.0,
                   "ratio": f"{STATE}/s5n/eavail-ratio-gibuu-over-genie.json",
                   "ratio_sha256": "45cc3e0abfe0dfae985113137e54b1d3f3961e86f4d29c454e08a0aa9f1f08a2"}
STABILITY_PSEUDO_SEED = 990000
JITTER_SEEDS = tuple(range(1, 52))  # 51 jitters; s5e's design n = 1 + 1/(2 * 0.1**2)
SCHEMA_TRUTH = {"s5e-shape-ratio/1": "ratio_nd", "s5p-cond-ratio/1": "cond_ratio", "s5p-fine-ratio/1": "fine_ratio",
                "s5n-eavail-ratio/1": "eavail_shape"}
# The 18 F0b truths (fd_f0_regrade.TRUTHS), each as s5p_nullexp's noise-free expectation: (name, hypothesis,
# alternative ratio or None, alternative truth, amplitude). "CLUSTER:" marks a file read on the cluster by its pin.
CLOSURES = (
    ("nominal", NULL_J_MNVTUNE, None, None, None),
    ("W1", NULL_J_MNVTUNE, f"{STATE}/s5n/eavail-ratio-nuwro-over-genie.json", "eavail_shape", 1.0),
    ("W2", NULL_J_MNVTUNE, f"{STATE}/s5e/w2-genie-mec-over-cv-eavailW.json", "ratio_nd", 1.0),
    ("W3", NULL_J_MNVTUNE, f"{STATE}/s5e/w3-nuwro-over-genie-pt-pz-eavail.json", "ratio_nd", 1.0),
    ("q3", NULL_J_MNVTUNE, NO_RATIO, "q3_given_eavail_w", 0.3),
    ("stage0c_gibuu", NULL_J_MNVTUNE,
     f"{STATE}/measurement-paper/5d-design-20261023/stage0/receipts-A/eavail-ratio-gibuu-over-genie-fluxfix.json",
     "eavail_shape", 1.0),
    ("closure_nuwro", NULL_J_MNVTUNE, "CLUSTER:prep/ratios/L-5D-PV/nuwro.json", "SCHEMA", 1.0),
    ("A7_mnvtune", NULL_J_MNVTUNE, None, None, None),
    ("A7_genie_cv", NULL_F["genie_cv"], None, None, None),
    ("A7_genie_mec", NULL_F["genie_mec"], None, None, None),
    ("A7_nuwro", NULL_F["nuwro_cv"], None, None, None),
    ("A7_gibuu", NULL_F["gibuu_cv"], None, None, None),
    ("P1r", NULL_J_MNVTUNE, f"{STATE}/s5p/ratios/altR/p1r-w3-nuwro-over-genie-pt-pz-eavail.json", "ratio_nd", 1.0),
    ("P2r", NULL_J_MNVTUNE, f"{STATE}/s5p/ratios/altR/p2r-d5-nuwro-over-genie-q3-given-eavail-w.json", "cond_ratio", 1.0),
    ("P3r", NULL_J_MNVTUNE, f"{STATE}/s5p/ratios/altR/p3r-w2-genie-mec-over-cv-eavailW.json", "ratio_nd", 1.0),
    ("P1g", NULL_F["genie_cv"], f"{STATE}/s5p/ratios/altR/p1r-w3-nuwro-over-genie-pt-pz-eavail.json", "ratio_nd", 1.0),
    ("P2g", NULL_F["genie_cv"], f"{STATE}/s5p/ratios/altR/p2r-d5-nuwro-over-genie-q3-given-eavail-w.json", "cond_ratio", 1.0),
    ("P3g", NULL_F["genie_cv"], f"{STATE}/s5p/ratios/altR/p3r-w2-genie-mec-over-cv-eavailW.json", "ratio_nd", 1.0),
)
CLOSURE_SEED = 991000  # s5p_nullexp's expectation mode draws nothing; the seed only fixes the MC split, as in F4


def closure_truth_kind(alt_path: Path, declared: str) -> str:
    """The truth kind of an alternative file: the declared one, or (``SCHEMA``) the one its schema names."""
    if declared != "SCHEMA":
        return declared
    schema = json.loads(alt_path.read_text()).get("schema")
    if schema not in SCHEMA_TRUTH:
        raise ValueError(f"{alt_path}: schema {schema!r} names no declared truth kind")
    return SCHEMA_TRUTH[schema]


def task_lines(a) -> list[str]:
    common = ["--npz", str(a.npz), "--bkg", str(a.bkg), "--expect-npz-sha256", a.expect_npz_sha256,
              "--expect-bkg-sha256", a.expect_bkg_sha256, "--config", "R", "--iters", "5", "--threads", "32"]
    lines = ["# FD-STAB tasks: per candidate, 1 base + 51 jittered unfolds of one GiBUU-like pseudo-experiment, and 18"
             " noise-free closures at the F0b truths"]
    pairs = ",".join(["-:-"] + [f"-:{j}" for j in JITTER_SEEDS])
    for c in CANDIDATES:
        lines.append("\t".join([f"stab_{c}_stability", "estimator_stability_probe.py", "--candidate", c, "stability", "--",
                                *common, "--construction", "pseudo", "--truth", STABILITY_TRUTH["truth"],
                                "--amplitude", str(STABILITY_TRUTH["amplitude"]), "--eavail-ratio", STABILITY_TRUTH["ratio"],
                                "--pseudo-seed", str(STABILITY_PSEUDO_SEED), "--pairs", pairs, "--tag", f"stab_{c}",
                                "--out", f"{a.runs}/{c}/stability"]))
        for name, hyp, alt, kind, amp in CLOSURES:
            argv = [*common, "--bank", str(a.bank), "--detector-dir", str(a.detector_dir), "--hypothesis", hyp,
                    "--pseudo-seeds", f"{CLOSURE_SEED}:{CLOSURE_SEED}", "--no-nuisance", "--expectation",
                    "--mc-fraction", "half", "--tag", f"stab_{c}_{name}", "--out", f"{a.runs}/{c}/closure/{name}"]
            if alt is not None:
                path = f"{a.closure_ratio_dir}/{alt[len('CLUSTER:'):]}" if alt.startswith("CLUSTER:") else alt
                argv += ["--alternative", path, "--alternative-truth", kind, "--alternative-amplitude", str(amp)]
            lines.append("\t".join([f"stab_{c}_closure_{name}", "estimator_stability_probe.py", "--candidate", c,
                                    "closure", "--", *argv]))
    return lines


def _refuse(rest: list[str], mode: str) -> str | None:
    if "--capacity" in rest:
        return "a candidate fixes the estimator: --capacity is refused"
    if "--config" in rest and rest[rest.index("--config") + 1] != "R":
        return "a candidate is built on configuration (e): --config must be R"
    if mode == "stability":
        if "--construction" not in rest or rest[rest.index("--construction") + 1] != "pseudo":
            return "the probe never reads the data: stability needs --construction pseudo"
    if mode == "closure" and not ({"--expectation", "--no-nuisance"} <= set(rest)):
        return "closures are noise-free: --expectation and --no-nuisance are required"
    return None


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["tasks"]:
        ap = argparse.ArgumentParser(prog="estimator_stability_probe.py tasks")
        for opt in ("--out", "--npz", "--bkg", "--bank", "--detector-dir", "--closure-ratio-dir", "--runs"):
            ap.add_argument(opt, type=Path, required=True)
        ap.add_argument("--expect-npz-sha256", required=True)
        ap.add_argument("--expect-bkg-sha256", required=True)
        a = ap.parse_args(argv[1:])
        a.out.write_text("\n".join(task_lines(a)) + "\n")
        print(json.dumps({"tasks": a.out.read_text().count("\n") - 1, "out": str(a.out)}))
        return 0
    if len(argv) < 4 or argv[0] != "--candidate" or argv[1] not in CANDIDATES or argv[2] not in ("stability", "closure") \
            or argv[3] != "--":
        print(f"usage: estimator_stability_probe.py --candidate {{{','.join(CANDIDATES)}}} {{stability,closure}} -- <args>",
              file=sys.stderr)
        return 2
    candidate, mode, rest = argv[1], argv[2], argv[4:]
    why = _refuse(rest, mode)
    if why:
        print(f"refusing: {why}", file=sys.stderr)
        return 2
    if mode == "closure" and "--alternative-truth" in rest:
        i = rest.index("--alternative-truth") + 1
        try:
            rest[i] = closure_truth_kind(Path(rest[rest.index("--alternative") + 1]), rest[i])
        except (ValueError, OSError) as exc:
            print(f"refusing: {exc}", file=sys.stderr)
            return 2
    with install(candidate):
        if mode == "stability":
            import s5p_numerics
            return s5p_numerics.main(rest)
        import s5p_nullexp
        return s5p_nullexp.main(rest)


if __name__ == "__main__":
    sys.exit(main())

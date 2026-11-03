#!/usr/bin/env python3
"""Estimator-stability probe (STAB): run ONE candidate estimator configuration through the production pipelines.

Declaration: docs/orchestration/state/measurement-paper/5d-community-20261024/FD-STAB-DECLARATION.md. Authority:
DECISION-20261102-joseph-bias-and-stabilisation-routes.md ("Probe, 1B waits").

    estimator_stability_probe.py --candidate C stability -- <s5p_numerics.py arguments>
    estimator_stability_probe.py --candidate C closure   -- <s5p_nullexp.py arguments>
    estimator_stability_probe.py tasks --out TSV --dry-out TSV --npz P --bkg P --bank D --detector-dir D
                                       --expect-npz-sha256 H --expect-bkg-sha256 H --closure-ratio-dir D --runs D

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

The data are loaded by the production loader but never enter a product: the pseudo-experiment's measured side is
built from the simulation and the background dump (``s5n_pseudo.build_pseudo``), and the unfolding's inputs take only
that side (``s5e_trace.unf_inputs``). ``stability`` requires ``--construction pseudo`` at the declared pseudo seed, and
``closure`` requires ``--expectation``, ``--no-nuisance`` and the declared MC split. A candidate fixes the estimator,
so ``--capacity`` and any ``--config`` other than R are refused. The refusal is decided on the runner's own parsed
arguments (``check_namespace``), so a repeated or abbreviated option cannot slip past it, and no product is written
unless that check ran.

    estimator_stability_probe.py gate --task ID --queue TSV --log DIR --t0 EPOCH --cap NODE_H

``gate`` (declaration §7) lets a queued task start only while the node-hours charged so far plus the projected
remainder stay within the cap, and B2 within 2x the control's per-unfold time.

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


def check_namespace(ns, mode: str) -> str | None:
    """The refusal, decided on the runner's own parsed arguments (last value wins, abbreviations resolved)."""
    if getattr(ns, "capacity", None) is not None:
        return "a candidate fixes the estimator: --capacity is refused"
    if getattr(ns, "config", None) != "R":
        return "a candidate is built on configuration (e): --config must be R"
    if mode == "stability":
        if getattr(ns, "construction", None) != "pseudo":
            return "the probe never puts the data in a product: stability needs --construction pseudo"
        if getattr(ns, "pseudo_seed", None) != STABILITY_PSEUDO_SEED or getattr(ns, "pseudo_seeds", None) is not None:
            return f"stability is one pseudo-experiment: --pseudo-seed {STABILITY_PSEUDO_SEED}"
    elif mode == "closure":
        if not (getattr(ns, "expectation", False) and getattr(ns, "no_nuisance", False)):
            return "closures are noise-free: --expectation and --no-nuisance are required"
        if getattr(ns, "mc_fraction", None) != CLOSURE_MC_FRACTION or \
                getattr(ns, "pseudo_seeds", None) != f"{CLOSURE_SEED}:{CLOSURE_SEED}":
            return f"closures use the declared split: --pseudo-seeds {CLOSURE_SEED}:{CLOSURE_SEED} --mc-fraction half"
    else:
        return f"unknown mode {mode!r}"
    return None


@contextmanager
def namespace_guard(mode: str, state: dict):
    """For one runner invocation: check the namespace its parser returns before it does anything with it."""
    orig = argparse.ArgumentParser.parse_args

    def parse_args(self, args=None, namespace=None):
        ns = orig(self, args, namespace)
        why = check_namespace(ns, mode)
        if why:
            print(f"refusing: {why}", file=sys.stderr)
            raise SystemExit(2)
        state["checked"] = True
        return ns

    argparse.ArgumentParser.parse_args = parse_args
    try:
        yield
    finally:
        argparse.ArgumentParser.parse_args = orig


@contextmanager
def install(candidate: str, mode: str | None = None):
    """Rebind the three production names for one invocation; restore them on exit. Yields the fit log.

    With ``mode``, the runner's parsed arguments are checked (``namespace_guard``), and no product is written unless
    that check ran: a runner that stopped calling argparse could not bypass it."""
    if candidate not in CANDIDATES:
        raise ValueError(f"unknown candidate {candidate!r}")
    override = CANDIDATES[candidate]
    est_params = {k: v for k, v in override.items() if k != "crossfit_k"}
    k = override.get("crossfit_k")
    log: list = []
    state = {"checked": False}
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
        if mode is not None and not state["checked"]:
            raise RuntimeError("refusing to write: the runner's arguments were never checked")
        meta = {**meta, "stability_probe": {"schema": SCHEMA, "candidate": candidate, "override": override,
                                            "fold_key": FOLD_KEY if k else None, "fits": list(log),
                                            "code_sha256": here}}
        log.clear()
        return orig_write(out, arrays, meta)

    s5c_unfold.config_params, onc.make_estimators, s5n_pseudo.write_product = config_params, make_estimators, write_product
    try:
        if mode is None:
            yield log
        else:
            with namespace_guard(mode, state):
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
CLOSURE_MC_FRACTION = "half"
STAB_CHUNK = 4  # pairs per stability task: 13 tasks of 4 unfolds per candidate, so the queue balances over the lanes
# Compute (declaration §7): 8 lanes on one node, one task per lane at a time, from one queue; a task starts only if
# the projected total stays within the cap (``gate``); the job's --time is the cap's remainder, so Slurm itself
# bounds the charge.
CAP_NODE_H = 8.0
LANES = 8
UNIT_S = 0.022828 * 3600 * LANES  # 657 s of one lane per unfold (FD-1B-STAGED-DECLARATION.md:530, measured on S1)
ASSUMED_FACTOR = {"B2": 2.0}  # before a candidate has a finished task: B2 at the 2x the cap allows, the others at 1x
B2_STOP_RATIO = 2.0  # B2 is stopped if its measured per-unfold time exceeds 2x the control's
# The dry run (§11): one short job, four lanes. The control pair is also the bitwise determinism check (§3.2: nominal
# and A7_mnvtune are the same closure); B2 and B3b are the candidates whose cost may differ. Their products and
# timings carry into the full job, which skips existing products.
DRY_TASKS = ("stab_control_closure_nominal", "stab_control_closure_A7_mnvtune", "stab_B2_closure_nominal",
             "stab_B3b_closure_nominal")


def closure_truth_kind(alt_path: Path, declared: str) -> str:
    """The truth kind of an alternative file: the declared one, or (``SCHEMA``) the one its schema names."""
    if declared != "SCHEMA":
        return declared
    schema = json.loads(alt_path.read_text()).get("schema")
    if schema not in SCHEMA_TRUTH:
        raise ValueError(f"{alt_path}: schema {schema!r} names no declared truth kind")
    return SCHEMA_TRUTH[schema]


def candidate_tasks(a, c: str) -> list[tuple[str, int, list[str]]]:
    """One candidate's tasks: (id, unfolds, argv after the script name)."""
    common = ["--npz", str(a.npz), "--bkg", str(a.bkg), "--expect-npz-sha256", a.expect_npz_sha256,
              "--expect-bkg-sha256", a.expect_bkg_sha256, "--config", "R", "--iters", "5", "--threads", "32"]
    pairs = ["-:-"] + [f"-:{j}" for j in JITTER_SEEDS]
    out = []
    for i in range(0, len(pairs), STAB_CHUNK):
        chunk = pairs[i:i + STAB_CHUNK]
        out.append((f"stab_{c}_stability_{i // STAB_CHUNK:02d}", len(chunk),
                    ["--candidate", c, "stability", "--", *common, "--construction", "pseudo",
                     "--truth", STABILITY_TRUTH["truth"], "--amplitude", str(STABILITY_TRUTH["amplitude"]),
                     "--eavail-ratio", STABILITY_TRUTH["ratio"], "--pseudo-seed", str(STABILITY_PSEUDO_SEED),
                     "--pairs", ",".join(chunk), "--tag", f"stab_{c}", "--out", f"{a.runs}/{c}/stability"]))
    for name, hyp, alt, kind, amp in CLOSURES:
        argv = [*common, "--bank", str(a.bank), "--detector-dir", str(a.detector_dir), "--hypothesis", hyp,
                "--pseudo-seeds", f"{CLOSURE_SEED}:{CLOSURE_SEED}", "--no-nuisance", "--expectation",
                "--mc-fraction", CLOSURE_MC_FRACTION, "--tag", f"stab_{c}_{name}", "--out", f"{a.runs}/{c}/closure/{name}"]
        if alt is not None:
            path = f"{a.closure_ratio_dir}/{alt[len('CLUSTER:'):]}" if alt.startswith("CLUSTER:") else alt
            argv += ["--alternative", path, "--alternative-truth", kind, "--alternative-amplitude", str(amp)]
        out.append((f"stab_{c}_closure_{name}", 1, ["--candidate", c, "closure", "--", *argv]))
    return out


def task_lines(a) -> list[str]:
    """The queue: tab-separated id, unfolds, script, argv. Candidates interleave, so B2's cost is measured early."""
    per = {c: candidate_tasks(a, c) for c in CANDIDATES}
    lines = ["# FD-STAB queue: per candidate, 1 base + 51 jittered unfolds of one GiBUU-like pseudo-experiment in tasks of"
             f" {STAB_CHUNK}, and 18 noise-free closures at the F0b truths; columns: id, unfolds, script, argv"]
    for i in range(max(len(v) for v in per.values())):
        for c in CANDIDATES:
            if i < len(per[c]):
                tid, n, argv = per[c][i]
                lines.append("\t".join([tid, str(n), "estimator_stability_probe.py", *argv]))
    return lines


PROTECTED = ("--capacity", "--config", "--construction", "--pseudo-seed", "--pseudo-seeds", "--expectation",
             "--no-nuisance", "--mc-fraction")


def _refuse(rest: list[str], mode: str) -> str | None:
    """A first check on argv; the decision is ``check_namespace`` on the runner's own parse (``install``). Here a
    protected option must be spelled in full, once, and without '='."""
    seen = []
    for tok in rest:
        if not tok.startswith("--"):
            continue
        name = tok.split("=", 1)[0]
        if name in PROTECTED:
            if "=" in tok:
                return f"{name} must be given as a separate argument, not with '='"
            if name in seen:
                return f"{name} is given more than once"
            seen.append(name)
        elif any(p.startswith(name) for p in PROTECTED):
            return f"{name} abbreviates a protected option; spell it in full"
    if "--capacity" in rest:
        return "a candidate fixes the estimator: --capacity is refused"
    if "--config" in rest and rest[rest.index("--config") + 1] != "R":
        return "a candidate is built on configuration (e): --config must be R"
    if mode == "stability":
        if "--construction" not in rest or rest[rest.index("--construction") + 1] != "pseudo":
            return "the probe never puts the data in a product: stability needs --construction pseudo"
    if mode == "closure" and not ({"--expectation", "--no-nuisance"} <= set(rest)):
        return "closures are noise-free: --expectation and --no-nuisance are required"
    return None


# ----------------------------------------------------------------------------------------------------- the budget
def read_queue(path: Path) -> list[tuple[str, str, int]]:
    """(id, candidate, unfolds) per queue line."""
    out = []
    for line in path.read_text().splitlines():
        if line and not line.startswith("#"):
            cols = line.split("\t")
            out.append((cols[0], cols[cols.index("--candidate") + 1], int(cols[1])))
    return out


def read_log(log: Path) -> dict[str, dict]:
    """Per task id, its start and (if finished) end epoch, as the job script writes them."""
    rec: dict[str, dict] = {}
    for p in log.glob("*.start"):
        rec.setdefault(p.stem, {})["start"] = float(p.read_text().split()[0])
    for p in log.glob("*.end"):
        rec.setdefault(p.stem, {})["end"] = float(p.read_text().split()[0])
    return rec


def project(now: float, t0: float, queue, rec: dict, lanes: int = LANES, unit_s: float = UNIT_S) -> dict:
    """The node-hours charged so far plus the projected remainder, for one node.

    Per candidate, the per-unfold lane time is the mean over its finished tasks, or, before any, UNIT_S times its
    ASSUMED_FACTOR. The remainder is the unstarted tasks plus what is left of the running ones, spread over the lanes,
    and never less than the longest single remaining task."""
    per = {}
    for tid, c, n in queue:
        r = rec.get(tid, {})
        if "end" in r:
            t, u = per.get(c, (0.0, 0))
            per[c] = (t + r["end"] - r["start"], u + n)
    rate = {c: (per[c][0] / per[c][1] if c in per and per[c][1] else unit_s * ASSUMED_FACTOR.get(c, 1.0))
            for _, c, _ in queue}
    left = []
    for tid, c, n in queue:
        r = rec.get(tid, {})
        if "end" in r:
            continue
        est = n * rate[c]
        left.append(max(0.0, est - (now - r["start"])) if "start" in r else est)
    wall_left = max(sum(left) / lanes, max(left, default=0.0))
    elapsed = max(0.0, now - t0)
    measured = {c: per[c][0] / per[c][1] for c in per if per[c][1]}
    b2_ratio = measured["B2"] / measured["control"] if {"B2", "control"} <= set(measured) else None
    return {"charged_node_h": elapsed / 3600, "projected_node_h": (elapsed + wall_left) / 3600,
            "per_unfold_s": rate, "measured": sorted(measured), "b2_over_control": b2_ratio}


def gate(task: str, queue_path: Path, log: Path, t0: float, cap: float = CAP_NODE_H, now: float | None = None) -> int:
    """0: start the task (its start is recorded). 4: the task already finished (a dry-run task in the full run): skip
    it, keeping its measured timing. 3: stop; nothing further starts (log/STOP holds why)."""
    import time
    now = time.time() if now is None else now
    stop = log / "STOP"
    if stop.exists():
        return 3
    if (log / f"{task}.end").exists():
        return 4
    queue = read_queue(queue_path)
    if task not in {t for t, _, _ in queue}:
        stop.write_text(json.dumps({"reason": f"task {task} is not in the queue"}) + "\n")
        return 3
    p = project(now, t0, queue, read_log(log))
    why = None
    if p["projected_node_h"] > cap:
        why = f"projected {p['projected_node_h']:.2f} node-h exceeds the cap {cap}"
    elif p["b2_over_control"] is not None and p["b2_over_control"] > B2_STOP_RATIO:
        why = f"B2 costs {p['b2_over_control']:.2f}x the control per unfold (stop above {B2_STOP_RATIO})"
    if why:
        stop.write_text(json.dumps({"reason": why, "task": task, **p}, indent=1) + "\n")
        return 3
    tmp = log / f"{task}.start.tmp"
    tmp.write_text(f"{now}\n")
    tmp.replace(log / f"{task}.start")  # atomic: a concurrent gate never reads a half-written start
    return 0


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["tasks"]:
        ap = argparse.ArgumentParser(prog="estimator_stability_probe.py tasks", allow_abbrev=False)
        for opt in ("--out", "--npz", "--bkg", "--bank", "--detector-dir", "--closure-ratio-dir", "--runs"):
            ap.add_argument(opt, type=Path, required=True)
        ap.add_argument("--expect-npz-sha256", required=True)
        ap.add_argument("--expect-bkg-sha256", required=True)
        ap.add_argument("--dry-out", type=Path, required=True, help="the dry run's four queue lines")
        a = ap.parse_args(argv[1:])
        lines = task_lines(a)
        a.out.write_text("\n".join(lines) + "\n")
        dry = [l for l in lines if l.split("\t")[0] in DRY_TASKS]
        if len(dry) != len(DRY_TASKS):
            raise SystemExit("a dry-run task is not in the queue")
        a.dry_out.write_text("\n".join(dry) + "\n")
        print(json.dumps({"tasks": len(lines) - 1, "out": str(a.out), "dry": str(a.dry_out)}))
        return 0
    if argv[:1] == ["gate"]:
        ap = argparse.ArgumentParser(prog="estimator_stability_probe.py gate", allow_abbrev=False)
        ap.add_argument("--task", required=True)
        ap.add_argument("--queue", type=Path, required=True)
        ap.add_argument("--log", type=Path, required=True)
        ap.add_argument("--t0", type=float, required=True, help="the job's start, epoch seconds")
        ap.add_argument("--cap", type=float, required=True, help="node-hours left under the declared cap")
        a = ap.parse_args(argv[1:])
        return gate(a.task, a.queue, a.log, a.t0, a.cap)
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
    with install(candidate, mode):
        if mode == "stability":
            import s5p_numerics
            return s5p_numerics.main(rest)
        import s5p_nullexp
        return s5p_nullexp.main(rest)


if __name__ == "__main__":
    sys.exit(main())

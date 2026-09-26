"""Score one PET final-design run directory on every PROTOCOL-20260925 section-4 endpoint.

Simulation only. A run directory has the predecessor's layout (`confirm/run_replicate.py`):
`replicate_arrays.npz` (prior and pseudodata rows, pass flags, truth scalars `[pt, ppar, eavail,
q3]`, `w_truth`, `pseudo_distortion`, `prior_oracle`, historical region codes) and
`iterations/iterNN.npz` (`pull`, `push` over every prior row; iteration NN is k = NN + 1).

**Like-for-like (section 4 preamble).** For every histogram, over truth-passing rows with finite
true `E_avail` (the predecessor's `keep_a`/`keep_b`):

* unfolded = prior weighted by `w_truth x push`;
* prior = prior weighted by `w_truth`;
* target = the replicate's own pseudodata truth weighted by `w_truth x pseudo_distortion`;

each unit-normalized, and `R = 1 - L1(unfolded - target) / L1(prior - target)`. R is undefined
(`recovery: null`, the absolute residual `residual_l1` is the reported quantity) when the injected
`L1(prior - target) < 3F`, `F = 0.004` (section 4, last paragraph). `recovery_raw` is the
unconditional value, kept for the cross-check.

**Histograms** (all computed for every run; which endpoint a run feeds follows from its case):

| name | bins | used by |
|---|---|---|
| `eavail` | 7 historical `E_avail` bins | E0, E2, E3, E6 (D1/D2/D5/R), E7, B2 |
| `eavail@<region>` | 7 bins within each scoreable historical region | E1 (U2a/U2b), C3 |
| `eavail_x_proton` | 7 x truncated-cloud proton class 0/1/2/3+ | E4, E6 (D4c), E7 |
| `eavail_x_neutron` | 7 x neutron class 0/1/2/3+ | E6 (D4d) |
| `eavail_x_pipm` | 7 x charged-pion class 0/1/2+ | E6 (D4a) |
| `eavail_x_pi0` | 7 x neutral-pion class 0/1+ | E6 (D4b) |
| `eavail_x_q3` | 7 x true-q3 quartile (`Q3_QUARTILE_EDGES`) | E5, E6 (D3) |

Joint histograms are flattened E_avail-major (`e * n_class + class`). Rows whose true q3 is not
finite are left out of the q3 histogram (all three spectra alike). The regions are the historical
(pT, p_par)-cell regions stored per row as `cm.REGION_CODES`, as `score_replicate.py` uses them.

**Cross-check (built in).** Where the run directory holds the predecessor's `scores.json`, the
aggregate and per-region E_avail `recovery_raw` of every common k must equal its
`iterations[*].push.recovery` / `recovery_by_region` to 1e-9 (the scorer refuses otherwise), as
`../diagnostics/posthoc_iterations.py` does.

**Bootstrap members (section 9).** If `replicate_arrays.npz` carries `prior_bootstrap_weight` /
`pseudo_bootstrap_weight` (the member's Poisson(1) weights), the prior and unfolded spectra include
the prior's Poisson weights and the target EXCLUDES the pseudodata's: every member of a coverage
replicate is scored against the replicate's own pseudodata truth.

    python score_design.py --run RUN --k 3 10 --row-features rf.npz --out-dir OUT \
        [--case D1_p0.350] [--population-target pop.json] [--require-cross-check]
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import math
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import numpy as np

HERE = Path(__file__).resolve().parent
CAMPAIGN = HERE.parents[1] / "improvement_campaign"
if str(CAMPAIGN / "phase_e") not in sys.path:
    sys.path.insert(0, str(CAMPAIGN / "phase_e"))

import common as cm  # noqa: E402  (predecessor: ENDPOINT_EDGES, REGION_CODES, SCOREABLE)

SCHEMA = "pet-final-design/run-scores/1"
PROTOCOL = "nd-unfolding/pet/final_design/PROTOCOL-20260925.md"

EAVAIL_EDGES = np.asarray(cm.ENDPOINT_EDGES, dtype=np.float64)
N_EAV = EAVAIL_EDGES.size - 1
SCOREABLE_REGIONS = tuple(cm.SCOREABLE)                    # low_acceptance, moderate, good
REGION_CODES = dict(cm.REGION_CODES)

F_FLOOR = 0.004                                            # section 4: finite-sample L1 floor
UNDEFINED_BELOW = 3.0 * F_FLOOR                            # R undefined when injected L1 < 3F
CROSS_CHECK_TOL = 1e-9

# Truth-side species classes over the stored 12-token cloud (TRUNCATED-CLOUD counts, section 4).
# name -> (row_features column, top class; the top class is ">= top").
SPECIES = {"proton": ("tr_n_p", 3), "neutron": ("tr_n_n", 3),
           "pipm": ("tr_n_pipm", 2), "pi0": ("tr_n_pi0", 1)}

# DEV-bank quartiles of true q3 (unweighted, 45,087,969 truth-passing DEV rows with finite q3),
# adopted by PROTOCOL-20260925 Amendment 1; job 58891701, provenance/q3_quartiles_dev_20260926.json.
# (The provisional all-inventory constant of 2026-09-25 is superseded.)
Q3_QUARTILE_EDGES = (1.2509539127349854, 2.5968730449676514, 4.490950584411621)
Q3_QUARTILE_PROVENANCE = {
    "status": "ADOPTED (DEV bank), PROTOCOL-20260925 Amendment 1",
    "script": "nd-unfolding/pet/final_design/analysis/q3_quartiles.py",
    "inventory_sha256": "fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625",
    "excluded": "FB and RB rows (banks/BANK_MANIFEST.json)", "job": "58891701",
    "n_used": 45087969, "weighting": "unweighted rows", "date": "2026-09-26"}

HISTOGRAM_BINS = {"eavail": N_EAV, "eavail_x_proton": N_EAV * 4, "eavail_x_neutron": N_EAV * 4,
                  "eavail_x_pipm": N_EAV * 3, "eavail_x_pi0": N_EAV * 2,
                  "eavail_x_q3": N_EAV * (len(Q3_QUARTILE_EDGES) + 1)}

# ------------------------------------------------------------------------------------------- #
# Cases: which endpoint a run feeds and its natural histogram (sections 4 and 7)
# ------------------------------------------------------------------------------------------- #
CASE_ALIASES = {"dev": "D1_p0.350"}
NULL_CASES = ("null",)
D4_SPECIES_HISTOGRAM = {"D4a": "eavail_x_pipm", "D4b": "eavail_x_pi0",
                        "D4c": "eavail_x_proton", "D4d": "eavail_x_neutron"}
DESIGNATED = {"D1_p0.350": "E0", "D1_m0.350": "E3", "D4c_p_up": "E4", "D3_p0.35": "E5"}


def refuse_blinded_final_runs(names, protocol=None):
    """Final-bank stages S4*/S5* (and any run whose receipt records a FB/RB pseudodata bank) stay
    unscored until PROTOCOL-20260925 carries an explicit `### Amendment ... UNBLIND` heading
    (Amendment 2c: scoring unlocks on a completeness declaration, not on the large-slot freeze).
    Fails closed."""
    import re as _re
    from pathlib import Path as _P
    protocol = _P(protocol) if protocol else _P(__file__).resolve().parents[1] / "PROTOCOL-20260925.md"
    def _bank(n):
        """The pseudodata bank a run recorded (receipt or inputs receipt), '' if none."""
        import json as _j
        for f in ("receipt.json", "inputs_receipt.json"):
            try:
                sel = _j.loads((_P(str(n)) / f).read_text()).get("selection") or {}
                return str(sel.get("pseudo_bank") or sel.get("record", {}).get("pseudo_bank", ""))
            except (OSError, ValueError, AttributeError):
                continue
        return ""
    blinded = [n for n in names if _re.match(r"^S[45]", _P(str(n)).name)
               or _bank(n) in ("FB", "RB")]
    if blinded and not _re.search(r"^### Amendment \S+ .*\bUNBLIND\b", protocol.read_text(), _re.M):
        raise SystemExit(f"refusing to score final-bank runs before an UNBLIND amendment: {blinded[:3]}")


def canonical_case(case: str) -> str:
    """The distortion id as `phase_e/distortions.py` names it ('dev' is D1 +0.35); a run-directory
    style '_D1_' joiner for a response case is normalized to '+D1_'."""
    case = CASE_ALIASES.get(case, case)
    return re.sub(r"^(R\d_x[0-9.]+)_(D\d)", r"\1+\2", case)


def classify_case(case: str) -> dict[str, Any]:
    """{case, family, natural histogram, endpoint id}. Unknown ids are refused (fail closed)."""
    c = canonical_case(case)
    if c in NULL_CASES:
        return {"case": c, "family": "null", "natural": "eavail", "endpoint": "E7"}
    parts = re.split(r"[+*]", c)   # "+": response + truth; "*": product of truth weights
    fams = [re.match(r"^(D5p|D\d[a-d]?|R\d)_", p) for p in parts]
    if not all(fams):
        raise ValueError(f"unknown case id {case!r}")
    fams = [m.group(1) for m in fams]
    d4 = [f for f in fams if f.startswith("D4")]
    if len(d4) > 1:
        raise ValueError(f"case {case!r} changes more than one species")
    if d4:
        natural = D4_SPECIES_HISTOGRAM[d4[0]]
    elif any(f == "D3" for f in fams):
        natural = "eavail_x_q3"
    else:
        natural = "eavail"                                    # D1, D2, D5, D5p, R + D1
    return {"case": c, "family": "+".join(fams), "natural": natural,
            "endpoint": DESIGNATED.get(c, "E6")}


# ------------------------------------------------------------------------------------------- #
# Histograms and the recovery statistic
# ------------------------------------------------------------------------------------------- #
def eavail_codes(e: np.ndarray) -> np.ndarray:
    """Bin index with `numpy.histogram` semantics (last bin closed); -1 outside or non-finite."""
    e = np.asarray(e, dtype=np.float64)
    idx = np.searchsorted(EAVAIL_EDGES, e, side="right") - 1
    idx[e == EAVAIL_EDGES[-1]] = N_EAV - 1
    bad = ~np.isfinite(e) | (e < EAVAIL_EDGES[0]) | (e > EAVAIL_EDGES[-1])
    idx[bad] = -1
    return idx.astype(np.int64)


def class_codes(n: np.ndarray, top: int) -> np.ndarray:
    return np.minimum(np.asarray(n, dtype=np.int64), top)


def q3_codes(q3: np.ndarray) -> np.ndarray:
    q3 = np.asarray(q3, dtype=np.float64)
    idx = np.searchsorted(np.asarray(Q3_QUARTILE_EDGES), q3, side="right").astype(np.int64)
    idx[~np.isfinite(q3)] = -1
    return idx


def joint(eb: np.ndarray, cls: np.ndarray, n_cls: int) -> np.ndarray:
    out = eb * n_cls + cls
    out[(eb < 0) | (cls < 0)] = -1
    return out


def hist(codes: np.ndarray, w: np.ndarray, n: int) -> np.ndarray:
    ok = codes >= 0
    return np.bincount(codes[ok], weights=np.asarray(w, np.float64)[ok], minlength=n)[:n]


def recovery_stats(prior: np.ndarray, unfolded: np.ndarray, target: np.ndarray,
                   keep_spectra: bool = True) -> dict[str, Any]:
    """The historical recovery (`run_arm_evaluation.recovery`) with the section-4 undefined rule."""
    sums = [float(np.sum(a)) for a in (prior, unfolded, target)]
    if not all(np.isfinite(s) and s > 0 for s in sums):
        return {"recovery": None, "recovery_raw": None, "defined": False,
                "reason": f"a spectrum does not normalize (sums {sums})"}
    p, u, t = (np.asarray(a, np.float64) / s for a, s in zip((prior, unfolded, target), sums))
    inj = float(np.abs(t - p).sum())
    res = float(np.abs(t - u).sum())
    raw = (1.0 - res / inj) if inj > 0 else None
    d = t - p
    dd = float(d @ d)
    # the finite-sample L1 floor grows with the number of bins (~sqrt(nbins/7) for the same events):
    # scaled per histogram (Amendment 2c; statistical review 8d9aaf8d item 11)
    below = UNDEFINED_BELOW * max(1.0, math.sqrt(len(p) / N_EAV))
    out = {"injected_l1": inj, "residual_l1": res, "recovery_raw": raw,
           "defined": bool(inj >= below), "undefined_below": below,
           "recovery": raw if inj >= below else None,
           "overshoot_projection": float(((u - p) @ d) / dd) if dd > 0 else None}
    if keep_spectra:
        out.update({"signed_residual_per_bin": (u - t).tolist(),
                    "injected_per_bin": d.tolist(), "moved_per_bin": (u - p).tolist(),
                    "unfolded_norm": u.tolist(), "target_norm": t.tolist(),
                    "prior_norm": p.tolist()})
    return out


# ------------------------------------------------------------------------------------------- #
# Inputs
# ------------------------------------------------------------------------------------------- #
class RowFeatures:
    """Species counts per inventory row: the full `row_features.npz` (indexed by row) or an
    `extract_row_features.py` extract (with a `rows` column; absent rows are refused)."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        with np.load(self.path) as z:
            self.rows = np.asarray(z["rows"]) if "rows" in z.files else None
            self.cols = {c: np.asarray(z[c]) for c, _ in SPECIES.values()}

    def take(self, column: str, rows: np.ndarray) -> np.ndarray:
        rows = np.asarray(rows, dtype=np.int64)
        if self.rows is None:
            return self.cols[column][rows]
        pos = np.searchsorted(self.rows, rows)
        if (pos >= self.rows.size).any() or not np.array_equal(
                self.rows[np.minimum(pos, self.rows.size - 1)], rows):
            raise ValueError(f"{self.path}: rows missing from the row-feature extract")
        return self.cols[column][pos]


def sha256_file(path: Path | str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def iteration_files(run: Path) -> dict[int, Path]:
    return {int(Path(f).stem[4:]) + 1: Path(f)
            for f in sorted(glob.glob(str(run / "iterations" / "iter[0-9][0-9].npz")))}


@dataclass
class Side:
    """One sample (prior or pseudodata): codes per histogram, base weights, region codes."""
    codes: dict[str, np.ndarray]
    region: np.ndarray
    weight: np.ndarray
    keep: np.ndarray


def build_side(A: Mapping[str, np.ndarray], prefix: str, rf: RowFeatures,
               weight: np.ndarray) -> Side:
    truth = A[f"{prefix}_truth"]
    keep = A[f"{prefix}_pass_truth"].astype(bool) & np.isfinite(truth[:, 2])
    eb = eavail_codes(truth[:, 2])
    eb[~keep] = -1
    codes = {"eavail": eb}
    rows = A[f"{prefix}_rows"]
    for name, (col, top) in SPECIES.items():
        codes[f"eavail_x_{name}"] = joint(eb, class_codes(rf.take(col, rows), top), top + 1)
    codes["eavail_x_q3"] = joint(eb, q3_codes(truth[:, 3]), len(Q3_QUARTILE_EDGES) + 1)
    return Side(codes, np.asarray(A[f"{prefix}_region"]), np.asarray(weight, np.float64), keep)


# ------------------------------------------------------------------------------------------- #
# Scoring
# ------------------------------------------------------------------------------------------- #
class DesignScorer:
    def __init__(self, run: Path | str, rf: RowFeatures, case: str | None = None,
                 population_target: Path | None = None) -> None:
        self.run = Path(run)
        ident_path = self.run / "run_identity.json"
        self.identity = json.loads(ident_path.read_text()) if ident_path.exists() else {}
        case = case or self.identity.get("distortion")
        if case is None:
            raise ValueError(f"{self.run}: no case (run_identity.json has no 'distortion'; "
                             "pass --case)")
        self.case = classify_case(case)
        with np.load(self.run / "replicate_arrays.npz") as z:
            A = {k: np.asarray(z[k]) for k in z.files}
        self.bootstrap = {k: k in A for k in ("prior_bootstrap_weight", "pseudo_bootstrap_weight")}
        # A bootstrap member's `prior_w_truth` is ALREADY the resampled weight (w x k):
        # runner/design_inputs.apply_bootstrap writes w x k there and keeps w as
        # `prior_w_truth_unresampled`. The scorer uses it as is (the prior the engine trained on)
        # and checks the relation instead of multiplying by k again (review ec475e7b, BLOCK).
        wb = A["prior_w_truth"].astype(np.float64)
        if self.bootstrap["prior_bootstrap_weight"]:
            if "prior_w_truth_unresampled" not in A:
                raise ValueError(f"{self.run}: bootstrap member without prior_w_truth_unresampled")
            expect = (A["prior_w_truth_unresampled"].astype(np.float64)
                      * A["prior_bootstrap_weight"].astype(np.float64))
            if not np.allclose(wb, expect, rtol=1e-6, atol=0.0):
                raise ValueError(f"{self.run}: prior_w_truth is not unresampled x bootstrap weight")
        wa = A["pseudo_w_truth"].astype(np.float64) * A["pseudo_distortion"].astype(np.float64)
        self.prior = build_side(A, "prior", rf, wb)
        self.pseudo = build_side(A, "pseudo", rf, wa)
        self.oracle = A["prior_oracle"].astype(np.float64)
        self.w_truth_prior = A["prior_w_truth"].astype(np.float64)
        self.n = {"prior": int(A["prior_rows"].size), "pseudo": int(A["pseudo_rows"].size),
                  "prior_scored": int(self.prior.keep.sum()),
                  "pseudo_scored": int(self.pseudo.keep.sum())}
        self.targets = self._spectra(self.pseudo, np.ones(self.n["pseudo"]))
        self.priors = self._spectra(self.prior, np.ones(self.n["prior"]))
        self.population = self._load_population(population_target) if population_target else None
        self.rf_path = rf.path

    # spectra of one side weighted by base weight x extra, for every histogram and region
    def _spectra(self, side: Side, extra: np.ndarray) -> dict[str, np.ndarray]:
        w = side.weight * np.asarray(extra, np.float64)
        out = {name: hist(side.codes[name], w, n) for name, n in HISTOGRAM_BINS.items()}
        for region in SCOREABLE_REGIONS:
            m = side.region == REGION_CODES[region]
            out[f"eavail@{region}"] = hist(np.where(m, side.codes["eavail"], -1), w, N_EAV)
        return out

    def _load_population(self, path: Path) -> dict[str, Any]:
        doc = json.loads(Path(path).read_text())
        want = self.identity.get("distortion_hash")
        if want is not None and doc.get("distortion_hash") not in (None, want):
            raise ValueError(f"population target {path} is for another distortion")
        t = doc["targets"]
        tg = {"eavail": np.asarray(t["aggregate"], float)}
        tg.update({f"eavail@{k}": np.asarray(v, float) for k, v in t["regions"].items()
                   if k in SCOREABLE_REGIONS})
        return {"path": str(path), "sha256": sha256_file(path), "targets": tg}

    def block(self, weights: np.ndarray, keep_spectra: bool = True) -> dict[str, Any]:
        unf = self._spectra(self.prior, weights)
        return {name: recovery_stats(self.priors[name], unf[name], self.targets[name],
                                     keep_spectra) for name in unf}

    def stability(self, push: np.ndarray, pull: np.ndarray) -> dict[str, Any]:
        """E9: weights over truth-passing prior rows (the predecessor's fields)."""
        kb = self.prior.keep
        w = push[kb]
        fin = np.isfinite(w)
        out: dict[str, Any] = {
            "n_truth_passing": int(kb.sum()),
            "n_nonfinite_push_all_rows": int((~np.isfinite(push)).sum()),
            "n_nonfinite_pull_all_rows": int((~np.isfinite(pull)).sum()),
            "n_nonfinite_truth_passing": int((~fin).sum()),
            "n_negative_truth_passing": int((w[fin] < 0).sum()),
        }
        wf = w[fin]
        if wf.size:
            q = np.percentile(wf, [50, 99, 99.9])
            ok = (wf >= 0).all()
            wt = self.w_truth_prior[kb][fin] * wf
            out.update({"push_max": float(wf.max()), "push_min": float(wf.min()),
                        "push_p50": float(q[0]), "push_p99": float(q[1]),
                        "push_p999": float(q[2]),
                        "push_ess_over_n": _ess(wf) / wf.size if ok else None,
                        "final_truth_weight_ess_over_n": _ess(wt) / wf.size if ok else None,
                        "prior_only_ess_over_n": _ess(self.w_truth_prior[kb]) / kb.sum()})
        return out

    def oracle_anchor(self) -> dict[str, Any]:
        """The exact distortion applied to the prior, scored like a push: the finite-sample
        ceiling of every histogram on this replicate (for the null, the prior residual = the
        null floor)."""
        return self.block(self.oracle, keep_spectra=False)

    def score(self, ks: list[int], require_cross_check: bool = False) -> dict[str, Any]:
        files = iteration_files(self.run)
        missing = [k for k in ks if k not in files]
        if missing:
            raise ValueError(f"{self.run}: k {missing} not written (have {sorted(files)})")
        committed = self._committed()
        if require_cross_check and committed is None:
            raise ValueError(f"{self.run}: --require-cross-check but no usable scores.json")
        records, checks = [], []
        for k in ks:
            with np.load(files[k]) as z:
                push = np.asarray(z["push"], np.float64)
                pull = np.asarray(z["pull"], np.float64)
            stab = self.stability(push, pull)
            rec: dict[str, Any] = {"k": k, "iteration_file": files[k].name,
                                   "iteration_file_sha256": sha256_file(files[k]),
                                   "stability": stab}
            kb = self.prior.keep
            if stab["n_nonfinite_truth_passing"] or stab["n_negative_truth_passing"]:
                rec["histograms"] = None
                rec["not_scored"] = "push has non-finite or negative weights on truth-passing rows"
            else:
                pw = np.where(kb, push, 0.0)
                h = self.block(pw)
                rec["histograms"] = h
                rec["endpoints"] = self.endpoints(h)
                if self.population is not None:
                    unf = self._spectra(self.prior, pw)
                    rec["vs_population"] = {
                        name: recovery_stats(self.priors[name], unf[name], tgt)
                        for name, tgt in self.population["targets"].items()}
                if committed is not None and k in committed:
                    checks.append(self._cross_check(k, h, committed[k]))
            records.append(rec)
        return {"schema": SCHEMA, "protocol": PROTOCOL, "run": str(self.run),
                "run_name": self.run.name, "case": self.case, "identity": self.identity,
                "provenance": self._provenance(),
                "constants": {"F": F_FLOOR, "undefined_below_injected_l1": UNDEFINED_BELOW,
                              "eavail_edges": EAVAIL_EDGES.tolist(),
                              "q3_quartile_edges": list(Q3_QUARTILE_EDGES),
                              "q3_quartile_provenance": Q3_QUARTILE_PROVENANCE,
                              "species": {k: list(v) for k, v in SPECIES.items()},
                              "region_codes": {r: REGION_CODES[r] for r in SCOREABLE_REGIONS},
                              "bootstrap_member": self.bootstrap},
                "n": self.n, "oracle_anchor": self.oracle_anchor(),
                "cross_check": {"performed": bool(checks), "tolerance": CROSS_CHECK_TOL,
                                "iterations": checks,
                                "max_abs_diff": max((c["max_abs_diff"] for c in checks),
                                                    default=None)},
                "iterations": records}

    def endpoints(self, h: Mapping[str, Any]) -> dict[str, Any]:
        """Section-4 endpoint values this run contributes (by its case)."""
        e = self.case["endpoint"]
        agg = h["eavail"]
        out: dict[str, Any] = {"natural_histogram": self.case["natural"],
                               "natural": _brief(h[self.case["natural"]]),
                               "eavail": _brief(agg)}
        if e == "E0":
            out["E0"] = _brief(agg)
            out["E1"] = {r: _brief(h[f"eavail@{r}"]) for r in SCOREABLE_REGIONS}
            out["E2"] = {"signed_residual_per_bin": agg["signed_residual_per_bin"],
                         "injected_per_bin": agg["injected_per_bin"],
                         "moved_per_bin": agg["moved_per_bin"]}
        elif e == "E7":
            out["E7"] = {"eavail_spurious_l1": agg["residual_l1"],
                         "eavail_x_proton_spurious_l1": h["eavail_x_proton"]["residual_l1"],
                         "eavail_prior_l1": agg["injected_l1"],
                         "eavail_x_proton_prior_l1": h["eavail_x_proton"]["injected_l1"]}
        elif e in ("E3", "E4", "E5"):
            out[e] = _brief(h[self.case["natural"]])
        else:
            out["E6"] = _brief(h[self.case["natural"]])
        return out

    def _committed(self) -> dict[int, dict[str, Any]] | None:
        path = self.run / "scores.json"
        if not path.exists() or any(self.bootstrap.values()):
            return None
        doc = json.loads(path.read_text())
        return {it["k"]: {"aggregate": it["push"]["recovery"],
                          "regions": it["push"]["recovery_by_region"]}
                for it in doc["iterations"]}

    def _cross_check(self, k: int, h: Mapping[str, Any], ref: Mapping[str, Any]) -> dict[str, Any]:
        diffs = {"aggregate": abs(h["eavail"]["recovery_raw"] - ref["aggregate"])}
        for r in SCOREABLE_REGIONS:
            diffs[r] = abs(h[f"eavail@{r}"]["recovery_raw"] - ref["regions"][r])
        worst = max(diffs.values())
        if not worst <= CROSS_CHECK_TOL:
            raise AssertionError(f"{self.run.name} k={k}: E_avail recovery differs from the "
                                 f"predecessor's scores.json by {diffs}")
        return {"k": k, "ours": h["eavail"]["recovery_raw"], "committed": ref["aggregate"],
                "abs_diff": diffs, "max_abs_diff": worst}

    def _provenance(self) -> dict[str, Any]:
        rc_path = self.run / "receipt.json"
        rc = json.loads(rc_path.read_text()) if rc_path.exists() else {}
        return {"replicate_arrays_sha256": sha256_file(self.run / "replicate_arrays.npz"),
                "receipt_sha256": sha256_file(rc_path) if rc_path.exists() else None,
                "receipt": {k: rc.get(k) for k in ("config_hash", "code_commit", "complete",
                                                  "step2_miss_mode", "slurm_job_id",
                                                  "seconds")},
                "row_features": str(self.rf_path),
                "row_features_sha256": sha256_file(self.rf_path),
                "population_target": (None if self.population is None else
                                      {k: self.population[k] for k in ("path", "sha256")})}


def _ess(w: np.ndarray) -> float:
    s2 = float((w * w).sum())
    return float(w.sum() ** 2 / s2) if s2 > 0 else 0.0


def _brief(s: Mapping[str, Any]) -> dict[str, Any]:
    return {k: s.get(k) for k in ("recovery", "recovery_raw", "defined", "injected_l1",
                                  "residual_l1", "overshoot_projection")}


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, allow_nan=False, separators=(",", ":")) + "\n")
    tmp.replace(path)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", type=Path, required=True, nargs="+")
    ap.add_argument("--k", type=int, nargs="+", required=True)
    ap.add_argument("--row-features", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--case", default=None, help="override run_identity.json 'distortion'")
    ap.add_argument("--population-target", type=Path, default=None)
    ap.add_argument("--require-cross-check", action="store_true")
    a = ap.parse_args(argv)
    refuse_blinded_final_runs(a.run)
    rf = RowFeatures(a.row_features)
    a.out_dir.mkdir(parents=True, exist_ok=True)
    for run in a.run:
        t0 = time.perf_counter()
        res = DesignScorer(run, rf, a.case, a.population_target).score(a.k, a.require_cross_check)
        res["seconds"] = round(time.perf_counter() - t0, 2)
        write_json(a.out_dir / f"{run.name}.design_scores.json", res)
        cc = res["cross_check"]
        for r in res["iterations"]:
            h = r.get("histograms")
            if h is None:
                print(f"{run.name} k={r['k']}: NOT SCORED ({r['not_scored']})")
                continue
            nat = h[res["case"]["natural"]]
            print(f"{run.name} [{res['case']['case']} -> {res['case']['endpoint']}] k={r['k']}: "
                  f"R_Eavail={h['eavail']['recovery_raw']:.10f} "
                  f"natural({res['case']['natural']}) R={nat['recovery']} "
                  f"inj={nat['injected_l1']:.4f}")
        print(f"{run.name}: cross-check performed={cc['performed']} "
              f"max|diff|={cc['max_abs_diff']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

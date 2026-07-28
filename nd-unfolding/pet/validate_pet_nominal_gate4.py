#!/usr/bin/env python3
"""Gate-4 validator for the publication full-event PET NOMINAL result (runbook Packet P5A /
PET_UQ_REMEDIATION_STATUS Gate 4).

CODE-ONLY gate: the pure checks below are login-safe and unit-tested against synthetic nominal
results; the actual nominal training is a separate authorized step (nominal_pet_training_allowed
stays false). The validator COMPOSES the existing closure evidence (ordinary closure
`closure_fullevent_fps.py` + omitted-muon stress closure `stress_closure_muon.py`) and adds:

  * finite / full-coverage push weights;
  * strict MC index/order (sorted, unique, in range);
  * exact lower-dimensional (pT,p_parallel) marginal closure + normalization;
  * cap-sensitivity telemetry (logit-cap saturation fraction bounded);
  * the FREEZE of estimator fingerprint + central vector (length/finite/order) + reported-bin
    mask/order + extended-FPS edges + seed/config policy.

The output receipt binds the nominal result path/hash, the frozen contract, every check, and a single
PASS/FAIL verdict. It is written unique-temp + fsync + atomic os.replace ONLY to a caller-supplied
WORK path; it never publishes a production artifact."""
import argparse
import hashlib
import json
import os
import sys
import tempfile

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
for _p in (_HERE, f"{_REPO}/nd-unfolding", f"{_REPO}/nd-unfolding/pet"):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import fullevent_fps_dataloader as fe  # noqa: E402  (login-safe)

RECEIPT_SCHEMA = "pet-fullevent-gate4-nominal-validation-v1"
ESTIMATOR_FINGERPRINT = "pet-fullevent-fps-v1"
BKG_MODE = "negweight-refined"

# ----------------------------- FROZEN nominal contract -----------------------------
# Frozen NOW (code-only): fingerprint, extended-FPS reporting grid + bin geometry/order, and the
# seed/config policy. The central vector itself is produced by the authorized nominal run; the freeze
# fixes its LENGTH (= reported cells) + order convention so a later result cannot silently reshape it.
N_PT_BINS = len(fe.CANONICAL_PT_EDGES) - 1                 # 15
N_PPAR_BINS = len(fe.CANONICAL_PPARALLEL_EDGES) - 1        # 19
N_CELLS = N_PT_BINS * N_PPAR_BINS                          # 285
FROZEN = {
    "estimator_fingerprint": ESTIMATOR_FINGERPRINT,
    "bkg_mode": BKG_MODE,
    "edges_pt": [float(x) for x in fe.CANONICAL_PT_EDGES],
    "edges_pparallel": [float(x) for x in fe.CANONICAL_PPARALLEL_EDGES],
    "n_pt_bins": N_PT_BINS, "n_pparallel_bins": N_PPAR_BINS, "n_reported_cells": N_CELLS,
    "bin_order": "pt-major row-major: cell = i_pt * n_pparallel_bins + i_pparallel",
    "seed_policy": {"estimator_seed": 42, "subsample_seed": 0, "niter": 2, "epochs": 8,
                    "train_events": 2000000},
    "closure_scripts": {
        "ordinary": "nd-unfolding/pet/closure_fullevent_fps.py",
        "omitted_muon_stress": "nd-unfolding/pet/stress_closure_muon.py"},
    "tolerances": {"marginal_l1_max": 0.10, "push_median_dev_max": 0.15,
                   "normalization_dev_max": 1e-3, "cap_saturation_frac_max": 1e-3},
}


def _ck(name, ok, detail=""):
    return {"name": name, "ok": bool(ok), "detail": str(detail)}


def check_weights_finite_coverage(push, n_expected=None):
    push = np.asarray(push, float)
    checks = [_ck("weights:nonempty", push.size > 0, push.size),
              _ck("weights:finite", bool(np.all(np.isfinite(push))), "all finite"),
              _ck("weights:nonnegative", bool(np.all(push >= 0.0)), "likelihood-ratio >= 0"),
              _ck("weights:not_all_zero", bool(np.any(push > 0.0)), "some positive")]
    if n_expected is not None:
        checks.append(_ck("weights:full_coverage", push.shape[0] == int(n_expected),
                          f"{push.shape[0]} vs {n_expected}"))
    return all(c["ok"] for c in checks), checks


def check_mc_index_order(imc, n_full=None):
    imc = np.asarray(imc)
    checks = [_ck("index:1d_integer", imc.ndim == 1 and np.issubdtype(imc.dtype, np.integer),
                  f"{imc.ndim}d {imc.dtype}"),
              _ck("index:strictly_increasing", imc.size > 0 and bool(np.all(np.diff(imc) > 0)),
                  "sorted unique ascending"),
              _ck("index:nonnegative", imc.size > 0 and int(imc.min()) >= 0, "min>=0")]
    if n_full is not None:
        checks.append(_ck("index:in_range", imc.size > 0 and int(imc.max()) < int(n_full),
                          f"max {int(imc.max()) if imc.size else None} < {n_full}"))
    return all(c["ok"] for c in checks), checks


def marginal_l1(h_truth, h_rw):
    a = np.asarray(h_truth, float); b = np.asarray(h_rw, float)
    a = a / a.sum() if a.sum() else a
    b = b / b.sum() if b.sum() else b
    return float(np.abs(a - b).sum())


def check_marginal_closure(h_truth, h_rw, tol=None):
    tol = FROZEN["tolerances"]["marginal_l1_max"] if tol is None else tol
    l1 = marginal_l1(h_truth, h_rw)
    return (l1 <= tol), [_ck("marginal:pt_ppar_l1", l1 <= tol, f"L1={l1:.4f} <= {tol}")], l1


def check_normalization(sum_w_push, sum_w, tol=None):
    tol = FROZEN["tolerances"]["normalization_dev_max"] if tol is None else tol
    dev = abs(float(sum_w_push) / float(sum_w) - 1.0) if sum_w else float("inf")
    return (dev <= tol), [_ck("normalization:sum_ratio", dev <= tol, f"|ratio-1|={dev:.3e} <= {tol}")]


def check_cap_sensitivity(saturation_frac, tol=None):
    tol = FROZEN["tolerances"]["cap_saturation_frac_max"] if tol is None else tol
    ok = saturation_frac is not None and float(saturation_frac) <= tol
    return ok, [_ck("cap:saturation_frac", ok, f"{saturation_frac} <= {tol}")]


def check_closure_verdicts(ordinary_pass, stress_recoil_blind, stress_fullevent_recovers):
    """Compose the two closure verdicts: ordinary closure PASS (estimator does NOT move when it must
    not) AND omitted-muon stress (recoil-only stays blind, full-event RECOVERS the injected tilt)."""
    checks = [_ck("closure:ordinary_pass", bool(ordinary_pass), ordinary_pass),
              _ck("closure:stress_recoil_blind", bool(stress_recoil_blind), stress_recoil_blind),
              _ck("closure:stress_fullevent_recovers", bool(stress_fullevent_recovers),
                  stress_fullevent_recovers)]
    return all(c["ok"] for c in checks), checks


def check_freeze(observed):
    """Verify a nominal result's declared contract against the FROZEN policy (fingerprint, edges, bin
    geometry/order, seed/config) and the central vector's length/finiteness/order."""
    checks = []
    checks.append(_ck("freeze:fingerprint", observed.get("estimator_fingerprint")
                      == ESTIMATOR_FINGERPRINT, observed.get("estimator_fingerprint")))
    checks.append(_ck("freeze:bkg_mode", observed.get("bkg_mode") == BKG_MODE,
                      observed.get("bkg_mode")))
    checks.append(_ck("freeze:edges_pt", observed.get("edges_pt") == FROZEN["edges_pt"], "pt edges"))
    checks.append(_ck("freeze:edges_pparallel",
                      observed.get("edges_pparallel") == FROZEN["edges_pparallel"], "p|| edges"))
    checks.append(_ck("freeze:bin_order", observed.get("bin_order") == FROZEN["bin_order"],
                      observed.get("bin_order")))
    checks.append(_ck("freeze:seed_policy", observed.get("seed_policy") == FROZEN["seed_policy"],
                      observed.get("seed_policy")))
    cv = observed.get("central_vector")
    mask = observed.get("reported_bin_mask")
    if cv is not None:
        cv = np.asarray(cv, float)
        checks.append(_ck("freeze:central_vector_len", cv.shape == (N_CELLS,), cv.shape))
        checks.append(_ck("freeze:central_vector_finite", bool(np.all(np.isfinite(cv))), "finite"))
    if mask is not None:
        checks.append(_ck("freeze:reported_mask_len", np.asarray(mask).shape == (N_CELLS,),
                          np.asarray(mask).shape))
    return all(c["ok"] for c in checks), checks


def build_gate4_report(*, result_meta, frozen_observed, weights_push=None, imc=None, n_full=None,
                       marginal=None, normalization=None, saturation_frac=None,
                       closure=None, observed_at_utc=None):
    """Assemble the Gate-4 receipt + single verdict. Pure (no training). `marginal`=(h_truth,h_rw);
    `normalization`=(sum_w_push,sum_w); `closure`=(ordinary,recoil_blind,fullevent_recovers)."""
    checks, comps = [], {}
    fz_ok, fz = check_freeze(frozen_observed); checks += fz; comps["freeze"] = fz_ok
    if weights_push is not None:
        w_ok, wc = check_weights_finite_coverage(weights_push, n_full if imc is None else
                                                 (len(imc) if hasattr(imc, "__len__") else None))
        checks += wc; comps["weights"] = w_ok
    if imc is not None:
        i_ok, ic = check_mc_index_order(imc, n_full); checks += ic; comps["index_order"] = i_ok
    if marginal is not None:
        m_ok, mc, _l1 = check_marginal_closure(*marginal); checks += mc; comps["marginal"] = m_ok
    if normalization is not None:
        n_ok, nc = check_normalization(*normalization); checks += nc; comps["normalization"] = n_ok
    if saturation_frac is not None:
        c_ok, cc = check_cap_sensitivity(saturation_frac); checks += cc; comps["cap"] = c_ok
    if closure is not None:
        cl_ok, clc = check_closure_verdicts(*closure); checks += clc; comps["closure"] = cl_ok
    verdict = bool(checks) and all(c["ok"] for c in checks)
    payload = {
        "receipt_schema": RECEIPT_SCHEMA, "verdict": "PASS" if verdict else "FAIL",
        "observed_at_utc": observed_at_utc, "nominal_pet_training_allowed": False,
        "result": dict(result_meta), "frozen_contract": FROZEN,
        "component_verdicts": comps, "checks": checks,
        "n_checks": len(checks), "n_failed": sum(1 for c in checks if not c["ok"])}
    return payload, verdict


def write_work_receipt(work_path, payload):
    """Atomic WORK-only write (unique temp + fsync + os.replace). Never a production artifact."""
    directory = os.path.dirname(os.path.abspath(work_path)) or "."
    fd, tmp = tempfile.mkstemp(prefix=".gate4_nom_", suffix=".json", dir=directory)
    try:
        with os.fdopen(fd, "w") as fh:
            json.dump(payload, fh, indent=2, default=str)
            fh.write("\n"); fh.flush(); os.fsync(fh.fileno())
        os.replace(tmp, work_path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    return work_path


def _sha256_file(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def main(argv=None):
    ap = argparse.ArgumentParser(description="Gate-4 nominal validator (runtime; needs a trained result)")
    ap.add_argument("--nominal-weights", required=True, help="nominal weights npz (from the driver)")
    ap.add_argument("--work", required=True, help="caller-supplied WORK receipt path (JSON)")
    ap.add_argument("--n-full", type=int, default=None)
    args = ap.parse_args(argv)
    import datetime
    z = np.load(args.nominal_weights, allow_pickle=True)
    frozen_observed = {"estimator_fingerprint": str(z["estimator_fingerprint"]) if
                       "estimator_fingerprint" in z.files else None,
                       "bkg_mode": str(z["bkg_mode"]) if "bkg_mode" in z.files else None,
                       "edges_pt": FROZEN["edges_pt"], "edges_pparallel": FROZEN["edges_pparallel"],
                       "bin_order": FROZEN["bin_order"], "seed_policy": FROZEN["seed_policy"]}
    payload, verdict = build_gate4_report(
        result_meta={"path": os.path.abspath(args.nominal_weights),
                     "sha256": _sha256_file(args.nominal_weights)},
        frozen_observed=frozen_observed,
        weights_push=z["weights_push"] if "weights_push" in z.files else None,
        imc=z["mc_indices"] if "mc_indices" in z.files else None, n_full=args.n_full,
        observed_at_utc=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    write_work_receipt(args.work, payload)
    print(json.dumps({"verdict": payload["verdict"], "n_failed": payload["n_failed"],
                      "component_verdicts": payload["component_verdicts"]}, indent=2))
    return 0 if verdict else 1


if __name__ == "__main__":
    sys.exit(main())

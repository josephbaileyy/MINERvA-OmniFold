"""Post-hoc per-iteration diagnostics of completed PET unfolding runs (simulation only).

For every iteration of a run directory written by the predecessor's `confirm/run_replicate.py`
(`replicate_arrays.npz`, `iterations/iterNN.npz`), measure where a correction is gained or lost:

* **Detector ratio quality (step 1).** The prior's reco-passing events weighted by the PULL,
  against the same events weighted by the ORACLE (the exact distortion function evaluated on the
  prior's truth, `prior_oracle`), in reco observables: reco E_avail (the endpoint bins), the number
  of stored reco clusters, and the stored-cluster energy sum. The oracle-weighted prior is the
  noiseless reco image of the target on the same events, so this isolates the classifier's error
  from pseudodata/prior sampling differences.
* **Truth projection (step 2).** Truth observables over the SELECTED events weighted by the pull
  (what step 1 hands to step 2) and by the push (what step 2 returns), each against the oracle.
* **Missed-event extrapolation.** The same truth observables over the MISSED events (truth-passing,
  reco-failing), where only the push acts.
* Truth observables: the seven E_avail endpoint bins; truncated-cloud species classes (protons
  0/1/2/3+, neutrons 0/1/2/3+, charged pions 0/1/2+, neutral pions 0/1+); the joint E_avail x
  proton class and E_avail x neutron class histograms; weighted mean species counts.
* Weight tails and ESS of the push over all / selected / missed events.

Recovery of an observable is the historical form `1 - L1(norm(h_w) - norm(h_oracle)) /
L1(norm(h_prior) - norm(h_oracle))` over its histogram; mean-count recovery is
`(m_w - m_prior) / (m_oracle - m_prior)`. When the oracle displacement of an observable is below
`SMALL_INJECTION_L1` the recovery is reported as `null` (undefined for a near-zero injection) and
the absolute residual is reported instead.

Species counts come from `row_features.npz` (`build_row_features.py`) and are counts over the stored
12-token truth cloud (truncated), the same counts the predecessor's D4 distortions are defined on.
"""
from __future__ import annotations

import argparse
import glob
import json
import sys
from pathlib import Path

import numpy as np

EAVAIL_EDGES = np.array([0.0, 0.1, 0.2, 0.4, 0.8, 1.5, 3.0, 100.0])
SMALL_INJECTION_L1 = 1e-3
SPECIES_CLASSES = {"p": 3, "n": 3, "pipm": 2, "pi0": 1}  # top class = ">= value"


def _norm(h: np.ndarray) -> np.ndarray:
    s = h.sum()
    return h / s if s > 0 else h


def recovery(h_w: np.ndarray, h_prior: np.ndarray, h_oracle: np.ndarray) -> dict:
    a, p, o = _norm(h_w), _norm(h_prior), _norm(h_oracle)
    inj = float(np.abs(p - o).sum())
    res = float(np.abs(a - o).sum())
    return {"injected_l1": inj, "residual_l1": res,
            "recovery": (1.0 - res / inj) if inj > SMALL_INJECTION_L1 else None,
            "signed_residual": (a - o).round(6).tolist()}


def mean_recovery(x: np.ndarray, w: np.ndarray, w0: np.ndarray, wo: np.ndarray) -> dict:
    m = float(np.average(x, weights=w)) if w.sum() > 0 else float("nan")
    m0 = float(np.average(x, weights=w0))
    mo = float(np.average(x, weights=wo))
    d = mo - m0
    return {"mean": m, "prior": m0, "oracle": mo,
            "recovery": ((m - m0) / d) if abs(d) > 1e-4 * max(abs(m0), 1e-6) else None}


def eavail_bin(e: np.ndarray) -> np.ndarray:
    return np.clip(np.digitize(e, EAVAIL_EDGES) - 1, 0, len(EAVAIL_EDGES) - 2)


def species_class(n: np.ndarray, top: int) -> np.ndarray:
    return np.minimum(n.astype(np.int64), top)


def hist(codes: np.ndarray, w: np.ndarray, n: int) -> np.ndarray:
    return np.bincount(codes, weights=w, minlength=n)[:n]


def tails(w: np.ndarray) -> dict:
    w = w[np.isfinite(w)]
    if w.size == 0:
        return {}
    pos = w[w > 0]
    return {"max": float(w.max()), "p999": float(np.quantile(w, 0.999)),
            "min": float(w.min()), "frac_nonpositive": float((w <= 0).mean()),
            "ess_over_n": float(pos.sum() ** 2 / (pos ** 2).sum() / w.size) if pos.size else 0.0}


def analyze_run(run: Path, rf: dict[str, np.ndarray]) -> dict:
    A = np.load(run / "replicate_arrays.npz")
    rows = A["prior_rows"]
    sel = A["prior_pass_reco"] & A["prior_pass_truth"]
    tru = A["prior_pass_truth"]
    miss = tru & ~A["prior_pass_reco"]
    w0 = A["prior_w_truth"].astype(np.float64)
    wr = A["prior_w_reco"].astype(np.float64)
    orc = A["prior_oracle"].astype(np.float64)
    eav = A["prior_truth"][:, 2]
    rc_eav = A["prior_reco_eavail"]
    counts = {k: rf[f"tr_n_{k}"][rows] for k in SPECIES_CLASSES}
    rc_n = rf["rc_n_valid"][rows].astype(np.int64)
    rc_E = rf["rc_E_sum"][rows]
    eb = eavail_bin(eav)
    nb = len(EAVAIL_EDGES) - 1
    cls = {k: species_class(counts[k], t) for k, t in SPECIES_CLASSES.items()}
    joint = {k: eb * (SPECIES_CLASSES[k] + 1) + cls[k] for k in ("p", "n")}
    # reco observables on selected events
    rc_eb = eavail_bin(np.where(sel, rc_eav, 0.0))
    rc_nb = np.minimum(rc_n, 12)
    q = np.quantile(rc_E[sel], np.linspace(0, 1, 11)[1:-1]) if sel.any() else np.array([])
    rc_Eb = np.digitize(rc_E, q)

    def truth_block(mask: np.ndarray, w: np.ndarray) -> dict:
        ww, pw, ow = (w0 * w * mask), (w0 * mask), (w0 * orc * mask)
        out = {"eavail": recovery(hist(eb, ww, nb), hist(eb, pw, nb), hist(eb, ow, nb))}
        for k, t in SPECIES_CLASSES.items():
            out[f"class_{k}"] = recovery(hist(cls[k], ww, t + 1), hist(cls[k], pw, t + 1),
                                         hist(cls[k], ow, t + 1))
            out[f"mean_{k}"] = mean_recovery(counts[k][mask], ww[mask], pw[mask], ow[mask])
        for k in ("p", "n"):
            m = nb * (SPECIES_CLASSES[k] + 1)
            out[f"joint_eavail_{k}"] = recovery(hist(joint[k], ww, m), hist(joint[k], pw, m),
                                                hist(joint[k], ow, m))
        return out

    def reco_block(w: np.ndarray) -> dict:
        ww, pw, ow = wr * w * sel, wr * sel, wr * orc * sel
        return {"reco_eavail": recovery(hist(rc_eb, ww, nb), hist(rc_eb, pw, nb), hist(rc_eb, ow, nb)),
                "reco_nclusters": recovery(hist(rc_nb, ww, 13), hist(rc_nb, pw, 13), hist(rc_nb, ow, 13)),
                "reco_Esum_decile": recovery(hist(rc_Eb, ww, 10), hist(rc_Eb, pw, 10), hist(rc_Eb, ow, 10))}

    # scorer cross-check: E_avail against the replicate's own pseudodata truth, as the predecessor's
    # score_replicate.py computes it; must reproduce the committed scores.json to 1e-9
    ka = A["pseudo_pass_truth"].astype(bool) & np.isfinite(A["pseudo_truth"][:, 2])
    kb = tru & np.isfinite(eav)
    tgt = hist(eavail_bin(A["pseudo_truth"][ka, 2]), (A["pseudo_w_truth"] * A["pseudo_distortion"])[ka], nb)
    committed = {}
    if (run / "scores.json").exists():
        committed = {it["k"]: it["push"]["aggregate"]["recovery"]
                     for it in json.loads((run / "scores.json").read_text())["iterations"]}
    its = []
    for f in sorted(glob.glob(str(run / "iterations" / "iter[0-9][0-9].npz"))):
        k = int(Path(f).stem[4:]) + 1
        I = np.load(f)
        pull = I["pull"].astype(np.float64)
        push = I["push"].astype(np.float64)
        vs_pseudo = recovery(hist(eb[kb], (w0 * push)[kb], nb), hist(eb[kb], w0[kb], nb), tgt)
        if k in committed and vs_pseudo["recovery"] is not None and \
                abs(min(vs_pseudo["recovery"], 1.0) - committed[k]) > 1e-9:
            raise AssertionError(f"{run.name} k={k}: E_avail recovery {vs_pseudo['recovery']} "
                                 f"!= committed {committed[k]}")
        rec = {"k": k, "eavail_vs_pseudodata": vs_pseudo,
               "step1_detector": reco_block(pull),
               "pull_selected": truth_block(sel, pull),
               "push_selected": truth_block(sel, push),
               "push_missed": truth_block(miss, push),
               "push_all": truth_block(tru, push),
               "tails": {"push_all": tails(push[tru]), "push_selected": tails(push[sel]),
                         "push_missed": tails(push[miss]), "pull_selected": tails(pull[sel])},
               "corr_log_push_oracle": {
                   pop: float(np.corrcoef(np.log(np.clip(push[m], 1e-12, None)),
                                          np.log(orc[m]))[0, 1]) if orc[m].std() > 0 else None
                   for pop, m in (("selected", sel), ("missed", miss))},
               "push_over_oracle_by_np": {
                   pop: [float(np.average(push[m & (cls["p"] == c)] / orc[m & (cls["p"] == c)],
                                          weights=w0[m & (cls["p"] == c)]))
                         if (m & (cls["p"] == c)).any() else None for c in range(4)]
                   for pop, m in (("selected", sel), ("missed", miss))},
               "push_over_oracle_by_nn": {
                   pop: [float(np.average(push[m & (cls["n"] == c)] / orc[m & (cls["n"] == c)],
                                          weights=w0[m & (cls["n"] == c)]))
                         if (m & (cls["n"] == c)).any() else None for c in range(4)]
                   for pop, m in (("selected", sel), ("missed", miss))}}
        its.append(rec)
    oracle_self = truth_block(tru, orc)
    for key, r in oracle_self.items():  # the oracle scored against itself must recover exactly
        if "residual_l1" in r and r["residual_l1"] > 1e-9:
            raise AssertionError(f"{run.name}: oracle self-check failed on {key}: {r['residual_l1']}")
    meta = json.loads((run / "run_identity.json").read_text()) if (run / "run_identity.json").exists() else {}
    return {"run": run.name, "identity": meta,
            "n": {"prior": int(rows.size), "truth": int(tru.sum()), "selected": int(sel.sum()),
                  "missed": int(miss.sum())},
            "oracle_block": truth_block(tru, np.ones_like(orc)), "iterations": its}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--row-features", type=Path, required=True)
    ap.add_argument("--runs", nargs="+", required=True, help="run directories (globs allowed)")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    R = np.load(a.row_features)
    rf = {k: R[k] for k in R.files if k.startswith(("tr_n_", "rc_"))}
    dirs = sorted({Path(p) for g in a.runs for p in glob.glob(g)
                   if (Path(p) / "replicate_arrays.npz").exists()})
    a.out.mkdir(parents=True, exist_ok=True)
    for d in dirs:
        out = a.out / f"{d.name}.posthoc.json"
        if out.exists():
            continue
        res = analyze_run(d, rf)
        tmp = out.with_suffix(".tmp")
        tmp.write_text(json.dumps(res))
        tmp.replace(out)
        print(f"{d.name}: {len(res['iterations'])} iterations", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

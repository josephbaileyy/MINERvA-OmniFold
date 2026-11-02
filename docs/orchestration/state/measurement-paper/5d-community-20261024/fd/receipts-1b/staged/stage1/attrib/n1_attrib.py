"""N1's rows above the bound on the declared draws, attributed (the stage-1 stop report; the director's ruling on
connect 32's STOP, item 2). DESCRIPTIVE ONLY: no verdict and no bound of its own.

For each per-row array it repeats ``fd_1b_mc.composite_n1``'s two passes over the bank: the all-draws bound per row
from each band's largest single ratio, then the exact pass over the 900 declared draws on the rows that bound puts
above ``N1_BOUND``. On top of the receipt it records, per row above on the declared draws: |a_CV|, the worst
composite, the draw (truth and seed) that attains it, and the draw's universes with the largest single ratios r_j
(|a_uj / a_CV|, or |a_uj| where a_CV == 0). It then aggregates which bands supply the largest and second-largest
r_j, each band's largest r_j on those rows, and |a_CV| on those rows against every row with a_CV != 0.

The two passes repeat composite_n1's arithmetic, so the output carries composite_n1's own numbers for comparison:
``check`` refuses unless all_draws_max, all_draws_rows_above, declared max and declared rows_above equal the
committed receipt's exactly (``--receipt``, digest checked). Everything else is read through fd_1b_mc's loaders
(``_load_world``, ``_weights``, ``_single``, ``declared_draws``, ``via_noatime``), unchanged.

Run from a checkout at the binding's merge, with the receipt's arguments:
  python3 n1_attrib.py --npz ... --bkg ... --bank ... --detector-dir ... --pins ... --expect-pins-sha256 ...
      --flux-constraint ... --flux-table ... --expect-flux-table-sha256 ... --receipt <receipt.json>
      --expect-receipt-sha256 ... --out <json>

MEASURES: which bands and CV weights the rows above carry. CANNOT AUTHORIZE: a bound, a verdict or a redesign.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path.cwd() / "nd-unfolding"))
import fd_1b_inv as inv  # noqa: E402
import fd_1b_mc as mc  # noqa: E402
import fd_1b_toys as toys  # noqa: E402

QUANTILES = (0.0, 0.05, 0.5, 0.95, 1.0)
TOP = 4


def band(tag: str) -> str:
    return tag.rpartition("_")[0]


def quantiles(x: np.ndarray) -> dict | None:
    return None if x.size == 0 else {f"q{int(q * 100):02d}": float(np.quantile(x, q)) for q in QUANTILES}


def draw_labels() -> list[tuple[str, int]]:
    """(truth, seed) of each declared draw, in ``declared_draws``' order."""
    return [(t, s) for t in mc.TRUTHS for s in mc.TOY_SEEDS[t]]


def attribute(inputs: dict, bkg: dict, bank_cv, load, flux, draws: list[list[str]]) -> dict:
    """composite_n1's two passes, keeping the rows, the worst draw per row and its largest single ratios."""
    cv = mc._cv_arrays(inputs, bkg)
    nz = {k: v != 0 for k, v in cv.items()}
    scale = {k: np.where(nz[k], np.abs(v), 1.0) for k, v in cv.items()}
    tags_all = toys.s1_universes()
    by_band: dict[str, list[str]] = {}
    for t in tags_all:
        by_band.setdefault(band(t), []).append(t)
    logsum = {k: np.zeros(v.shape) for k, v in cv.items()}
    top = {k: np.zeros(v.shape) for k, v in cv.items()}
    nonzero = {k: np.zeros(v.shape) for k, v in cv.items()}
    for tags in by_band.values():
        R = {k: np.zeros(v.shape) for k, v in cv.items()}
        for t in tags:
            single, _ = mc._single(inputs, bkg, bank_cv, t, load(t), flux)
            for k, a in single.items():
                np.maximum(R[k], np.abs(a) / scale[k], out=R[k])
        for k in cv:
            with np.errstate(divide="ignore"):
                logsum[k] += np.log(R[k])
            np.maximum(top[k], R[k], out=top[k])
            nonzero[k] += R[k] > 0
    rows, out = {}, {}
    for k in cv:
        with np.errstate(divide="ignore", invalid="ignore"):
            sup = np.where(nz[k], np.where(top[k] > 0, np.exp(logsum[k] - np.log(np.where(top[k] > 0, top[k], 1.0))),
                                           0.0), nonzero[k])
        rows[k] = np.flatnonzero(sup > mc.N1_BOUND)
        out[k] = {"all_draws_max": float(sup.max()), "all_draws_rows_above": int(rows[k].size),
                  "a_cv_abs_all_nonzero_rows": quantiles(np.abs(cv[k][nz[k]]))}
    exact = {k: i for k, i in rows.items() if 0 < i.size <= mc.N1_CANDIDATE_CAP}
    col = {t: c for c, t in enumerate(tags_all)}
    V = {k: np.zeros((i.size, len(col))) for k, i in exact.items()}
    for t, c in col.items():
        single, _ = mc._single(inputs, bkg, bank_cv, t, load(t), flux)
        for k, i in exact.items():
            a = single[k][i]
            V[k][:, c] = np.where(nz[k][i], np.abs(a) / scale[k][i], a)
    labels = draw_labels()
    if len(labels) != len(draws):                       # a fixture's draws: label by index only
        labels = [(None, d) for d in range(len(draws))]
    for k in cv:
        i = rows[k]
        if k not in exact:
            out[k].update(declared={"evaluated": i.size == 0, "rows": int(i.size), "max": None,
                                    "rows_above": 0 if i.size == 0 else None})
            continue
        m, worst, arg = nz[k][i], np.zeros(i.size), np.full(i.size, -1)
        for d, tags in enumerate(draws):
            v = V[k][:, [col[t] for t in tags]]
            peak = np.max(np.abs(v), axis=1)
            comp = np.where(m, np.prod(np.abs(v), axis=1), np.abs(v.sum(axis=1)))
            with np.errstate(divide="ignore", invalid="ignore"):
                r = np.where(peak > 0, comp / peak, np.where(comp == 0, 1.0, np.inf))
            arg[r > worst] = d
            np.maximum(worst, r, out=worst)
        above = np.flatnonzero(worst > mc.N1_BOUND)
        out[k]["declared"] = {"evaluated": True, "rows": int(i.size), "max": float(worst.max()),
                              "rows_above": int(above.size)}
        recs, first, second, pairs, truths = [], Counter(), Counter(), Counter(), Counter()
        band_r: dict[str, list[float]] = {}
        for j in above:
            tags = draws[arg[j]]
            rj = sorted(((float(abs(V[k][j, col[t]])), t) for t in tags), reverse=True)
            first[band(rj[0][1])] += 1
            if len(rj) > 1:
                second[band(rj[1][1])] += 1
                pairs[f"{band(rj[0][1])}+{band(rj[1][1])}"] += 1
            truth, seed = labels[arg[j]]
            truths[truth] += 1
            for b, ts in by_band.items():
                band_r.setdefault(b, []).append(float(max(abs(V[k][j, col[t]]) for t in ts)))
            recs.append({"row": int(i[j]), "a_cv": float(cv[k][i[j]]), "cv_zero": bool(not m[j]),
                         "worst": float(worst[j]), "draw_index": int(arg[j]), "truth": truth, "seed": seed,
                         "top": [[t, r] for r, t in rj[:TOP]], "n_universes_r_gt_1": int(sum(r > 1 for r, _ in rj))})
        a_cv = np.abs(cv[k][i[above]])
        out[k].update({
            "rows_above_cv_zero": int(np.sum(~m[above])),
            "a_cv_abs_rows_above": quantiles(a_cv[a_cv > 0]),
            "largest_r_band": dict(first.most_common()), "second_r_band": dict(second.most_common()),
            "top_pairs": dict(pairs.most_common(10)), "worst_truth": dict(truths.most_common()),
            "band_max_r_on_rows_above": {b: {"max": max(x), "rows_gt_10": sum(y > 10 for y in x),
                                             "rows_gt_2": sum(y > 2 for y in x)}
                                         for b, x in sorted(band_r.items()) if max(x) > 1},
            "rows": recs})
    return {"arrays": out, "bound": mc.N1_BOUND, "n_draws": len(draws), "candidate_cap": mc.N1_CANDIDATE_CAP}


def check(res: dict, receipt: dict) -> list[str]:
    """composite_n1's numbers in the committed receipt, against this repetition's; any difference is listed."""
    bad = []
    comp = receipt["composite"]
    for key in ("bound", "n_draws", "candidate_cap"):
        if res[key] != comp[key]:
            bad.append(f"{key}: {res[key]} != {comp[key]}")
    for k, want in comp["arrays"].items():
        got = res["arrays"][k]
        for key in ("all_draws_max", "all_draws_rows_above"):
            if got[key] != want[key]:
                bad.append(f"{k} {key}: {got[key]} != {want[key]}")
        for key in ("evaluated", "rows", "max", "rows_above"):
            if got["declared"][key] != want["declared"][key]:
                bad.append(f"{k} declared {key}: {got['declared'][key]} != {want['declared'][key]}")
    return bad


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    for k in ("npz", "bkg", "bank", "detector-dir", "pins", "flux-constraint", "flux-table", "receipt", "out"):
        ap.add_argument(f"--{k}", type=Path, required=True)
    for k in ("expect-pins-sha256", "expect-flux-table-sha256", "expect-receipt-sha256"):
        ap.add_argument(f"--{k}", required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        print(f"[n1-attrib] refusing to overwrite {a.out}", file=sys.stderr)
        return 4
    raw = a.receipt.read_bytes()
    if hashlib.sha256(raw).hexdigest() != a.expect_receipt_sha256:
        print("[n1-attrib] refusing: the receipt's digest differs", file=sys.stderr)
        return 4
    receipt = json.loads(raw)
    inv.OPENED.clear()
    world = mc._load_world(a)
    flux_p = mc.via_noatime(toys.flux_probabilities, a.flux_constraint)
    res = attribute(world["inputs"], world["bkg"], world["bank_cv"], lambda t: mc._weights(world, a, t),
                    world["flux"], mc.declared_draws(flux_p, world["groups"]))
    res.update(step="n1-attribution", descriptive_only=True, receipt_sha256=a.expect_receipt_sha256,
               mismatches=check(res, receipt), atime=inv.atime_check(),
               code_sha256={**mc.code_digests(), Path(__file__).name: hashlib.sha256(
                   Path(__file__).read_bytes()).hexdigest()})
    a.out.write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps({"out": str(a.out), "mismatches": res["mismatches"], "atime_moved": res["atime"]["moved"]}))
    if res["mismatches"]:
        print("[n1-attrib] refusing: the repetition does not reproduce the receipt", file=sys.stderr)
        return 1
    return 8 if res["atime"]["moved"] else 0


if __name__ == "__main__":
    sys.exit(main())

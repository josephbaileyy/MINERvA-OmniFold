"""Population target of a (bank, distortion) for the study's report-only comparison (PROTOCOL-20260925 sections 3
and 4: every final-stage score targets the replicate's own pseudodata truth and, reported beside it, the FB
population truth under the same distortion).

The target is the normalized seven-bin truth E_avail spectrum over EVERY truth-passing row of the bank with finite
true E_avail, weighted `w_truth x d`, aggregate and per scoreable historical region -- the scorer's like-for-like
target (`score_design.build_side` on the pseudodata: `pseudo_w_truth x pseudo_distortion`, `pass_truth` and finite
E_avail, `eavail_codes`, historical region codes) with the replicate's rows replaced by the whole bank. `d` is the
runner's own distortion (`design_inputs.get_distortion`); its unit-mean normalization cancels in the normalized
spectra. A D4 (species) distortion also gets its natural joint histogram (E_avail x the species class the case
changes, e.g. `eavail_x_proton` for D4c; D3 gets `eavail_x_q3`), and its species counts come from `row_features.npz`, the truncated-cloud
counts the scorer bins on; `--check-run` proves on a run's own rows that they reproduce the runner's stored
distortion weights (`pseudo_distortion`, computed from the truth cloud). The output is the `--population-target`
file `score_design.py` reads (its `distortion_hash` is checked against each run's).

Reads only signal-MC members (`truth_scalars`, `w_truth`, `pass_truth`) through `SignalOnlyNpz`, and the bank codes
checked against the committed `banks/BANK_MANIFEST.json`. No estimator output is read. RB is refused.

    fb_population_target.py --distortion dev --inputs-npz G2_FPS_MEFHC_P12.npz --banks-npz banks.npz \
        --populations <B1 populations.npz> --out fb_population_dev.json
"""
from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
sys.path.insert(0, str(STUDY / "runner"))
sys.path.insert(0, str(HERE))
import design_inputs as di  # noqa: E402
from score_design import (HISTOGRAM_BINS, N_EAV, Q3_QUARTILE_EDGES, REGION_CODES, SCOREABLE_REGIONS,  # noqa: E402
                          SPECIES, RowFeatures, class_codes, classify_case, eavail_codes, hist, joint, q3_codes)

SCHEMA = "pet-final-design/population-target/1"
DATALOADER = STUDY.parent / "fullevent_fps_dataloader.py"
MEMBERS = ("truth_scalars", "w_truth", "pass_truth")


def scalar_cols() -> dict[str, int]:
    """`SCALAR_COLS` of the full-event data loader, read from its source (the module imports TensorFlow)."""
    for node in ast.parse(DATALOADER.read_text()).body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "SCALAR_COLS" for t in node.targets):
            return ast.literal_eval(node.value)
    raise SystemExit(f"no SCALAR_COLS in {DATALOADER}")


def normalized(h: np.ndarray) -> list[float]:
    s = float(h.sum())
    if not (np.isfinite(s) and s > 0):
        raise SystemExit(f"population spectrum does not normalize (sum {s})")
    return (h / s).tolist()


# `distortions.count_species` keys -> the row-feature columns the scorer bins on (`score_design.SPECIES`)
COUNT_KEYS = {"n_p": "proton", "n_n": "neutron", "n_pipm": "pipm", "n_pi0": "pi0"}


def truth_of(ts: np.ndarray, cols: dict[str, int], rf: RowFeatures | None, rows: np.ndarray,
             needs_species: bool) -> dict[str, np.ndarray]:
    """The runner's truth mapping of these rows, with the D4 species counts from `row_features.npz`."""
    truth = di.truth_mapping(SimpleNamespace(SCALAR_COLS=cols), ts, None)
    if needs_species:
        if rf is None:
            raise SystemExit("a species distortion needs --row-features")
        truth.update({k: rf.take(SPECIES[v][0], rows).astype(np.float64) for k, v in COUNT_KEYS.items()})
    return truth


def distortion_weight(spec, truth: dict, pg: np.ndarray) -> np.ndarray:
    dw = np.ones(pg.size, np.float64)
    dw[pg] = di.unit_mean(np.asarray(spec.raw({k: v[pg] for k, v in truth.items()}), np.float64))[0]
    return dw


def check_run(run: Path, spec, rf: RowFeatures | None) -> dict:
    """On one run's own pseudodata rows: the weight rebuilt here equals the runner's `pseudo_distortion`."""
    with np.load(run / "replicate_arrays.npz") as z:
        rows, pg = np.asarray(z["pseudo_rows"]), np.asarray(z["pseudo_pass_truth"]).astype(bool)
        tr, stored = np.asarray(z["pseudo_truth"], np.float64), np.asarray(z["pseudo_distortion"], np.float64)
    ident = json.loads((run / "run_identity.json").read_text())
    if ident.get("distortion_hash") != spec.content_hash():
        raise SystemExit(f"{run}: distortion hash differs from {spec.name}'s")
    # pseudo_truth columns are (pt, pparallel, eavail, q3)
    truth = truth_of(tr, {"pt": 0, "pparallel": 1, "eavail": 2, "q3": 3}, rf, rows, spec.needs_species)
    got = distortion_weight(spec, truth, pg)
    diff = float(np.max(np.abs(got - stored)))
    if diff > 1e-9 * max(1.0, float(np.max(np.abs(stored)))):
        raise SystemExit(f"{run}: rebuilt distortion weight differs from the stored one by {diff}")
    return {"run": str(run), "rows": int(rows.size), "max_abs_diff": diff}


def build(bank: str, distortion: str, inputs_npz: Path, banks_npz: Path, populations: Path,
          rf: RowFeatures | None, check: Path | None) -> dict:
    if bank != "FB":
        raise SystemExit(f"bank {bank}: only the released final bank FB has a population target here")
    codes, bank_record = di.load_bank_codes(banks_npz)
    rows = np.flatnonzero(codes == di.BANK_CODES[bank])
    spec = di.get_distortion(distortion)
    if spec.reco_energy_scale is not None or spec.muon_momentum_scale is not None:
        raise SystemExit(f"{distortion}: response distortions keep the undistorted truth (no population target)")
    checked = check_run(check, spec, rf) if check else None
    raw = np.load(inputs_npz, allow_pickle=False, mmap_mode="r")
    d = di.scope.SignalOnlyNpz(raw)
    ts = np.asarray(d["truth_scalars"])[rows].astype(np.float64)
    w = np.asarray(d["w_truth"])[rows].astype(np.float64)
    pg = np.asarray(d["pass_truth"])[rows].astype(bool)
    truth = truth_of(ts, scalar_cols(), rf, rows, spec.needs_species)
    keep = pg & np.isfinite(truth["eavail"])
    wt = w * distortion_weight(spec, truth, pg)
    eb = eavail_codes(truth["eavail"])
    eb[~keep] = -1
    region = di.region_codes(di.historical_cr(), truth["pt"], truth["ppar"], populations)
    targets = {"aggregate": normalized(hist(eb, wt, N_EAV)), "regions": {}, "histograms": {}}
    for name in SCOREABLE_REGIONS:
        targets["regions"][name] = normalized(hist(np.where(region == REGION_CODES[name], eb, -1), wt, N_EAV))
    natural = classify_case(distortion)["natural"]
    if natural == "eavail_x_q3":                      # E5 (D3): true q3 at the DEV quartiles (Amendment 1)
        jc = joint(eb, q3_codes(truth["q3"]), len(Q3_QUARTILE_EDGES) + 1)
        targets["histograms"][natural] = normalized(hist(jc, wt, HISTOGRAM_BINS[natural]))
    elif natural != "eavail":
        col, top = SPECIES[natural.split("eavail_x_", 1)[1]]
        jc = joint(eb, class_codes(rf.take(col, rows), top), top + 1)
        targets["histograms"][natural] = normalized(hist(jc, wt, HISTOGRAM_BINS[natural]))
    try:
        commit = subprocess.run(["git", "-C", str(STUDY), "rev-parse", "HEAD"], capture_output=True,
                                text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        commit = None
    return {"schema": SCHEMA, "bank": bank, "distortion": spec.name, "distortion_hash": spec.content_hash(),
            "distortion_record": spec.record, "n_bank_rows": int(rows.size), "n_scored_rows": int(keep.sum()),
            "natural_histogram": natural, "targets": targets, "weight_check": checked, "banks": bank_record,
            "inputs_npz": str(inputs_npz), "inputs_npz_members": list(MEMBERS), "populations": str(populations),
            "populations_sha256": di.sha256_file(populations), "row_features": None if rf is None else str(rf.path),
            "scalar_cols": scalar_cols(), "code_commit": commit}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bank", default="FB")
    ap.add_argument("--distortion", nargs="+", required=True)
    ap.add_argument("--inputs-npz", type=Path, required=True)
    ap.add_argument("--banks-npz", type=Path, required=True)
    ap.add_argument("--populations", type=Path, required=True)
    ap.add_argument("--row-features", type=Path, default=None, help="row_features.npz (D4 distortions)")
    ap.add_argument("--check-run", nargs="*", default=[], metavar="DISTORTION=RUN_DIR",
                    help="a run of that distortion whose stored weights the rebuilt ones must equal")
    ap.add_argument("--out-dir", type=Path, required=True)
    a = ap.parse_args(argv)
    rf = RowFeatures(a.row_features) if a.row_features else None
    checks = dict(x.split("=", 1) for x in a.check_run)
    a.out_dir.mkdir(parents=True, exist_ok=True)
    for name in a.distortion:
        doc = build(a.bank, name, a.inputs_npz, a.banks_npz, a.populations, rf,
                    Path(checks[name]) if name in checks else None)
        out = a.out_dir / f"{a.bank.lower()}_population_{name}.json"
        out.write_text(json.dumps(doc, indent=1) + "\n")
        print(f"{out}: {doc['n_scored_rows']} of {doc['n_bank_rows']} rows; aggregate "
              f"{[round(x, 4) for x in doc['targets']['aggregate']]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

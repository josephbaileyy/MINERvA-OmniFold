#!/usr/bin/env python3
"""V_F (C_e^infl) Phase 1 readings, read straight from the Phase 1 readouts (FD-VF BINDING 1's run, #1356).

The per-key \\fvval mapping (vf_readings.py through make_values_fived16.all_values) needs Phase 2's V_F copies first:
make_values_fived16 reads Table IV's four GENCMP chi2 from gdefs (a Phase 2 readout) and checks them against Stage G's
chdefs chain and against GENCMP's 2 x 2 corners, and indexes eav by the arm's matrix name. This tool reads only Phase
1's readouts and products, OLD and V_F, each pinned by sha256 prefix, and writes:
- vf_readings_phase1.json and .md, led by the decision-rule outcome changes (F0/F0b/F1 listings and trigger counts);
- Stage G's chi2 for all four chains; the per-cell sigma (C_e, C_e^infl, C_rep with and without C_PL5D, OLD and V_F);
  the S1/C_resp sigma rows both ways (C_e form and C_e^infl form).
Run: python3 -B phase1_readings.py --out-dir <dir>"""
import argparse
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

ROOT = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                           cwd=Path(__file__).resolve().parent, check=True).stdout.strip())
B = "docs/orchestration/state/measurement-paper/5d-community-20261024"
F, W = f"{B}/fd", f"{B}/fd/with-vf"
CELLS = [f"R{i:02d}" for i in range(16)]
PINS = {   # name: (path, sha256 prefix); OLD from make_values_fived16's READOUTS / NOPL_READOUTS and #1345's OLD_* pins
    "old f0": (f"{F}/readout/fd_f0_readout.json", "6e7d718b"),
    "vf f0": (f"{W}/readout/vf-f0/fd_f0_readout.json", "7d7429d4"),
    "old with/f0b": (f"{F}/with-cpl/readout/fd_f0b_readout.json", "5f542830"),
    "vf with/f0b": (f"{W}/readout/vf-with-S/fd_f0b_readout.json", "432243e1"),
    "old with/f1": (f"{F}/with-cpl/readout/fd_f1_readout.json", "5ccc89e5"),
    "vf with/f1": (f"{W}/readout/vf-with-S/fd_f1_readout.json", "bd36a2aa"),
    "old nopl/f0b": (f"{F}/readout/fd_f0b_readout.json", "b9db935a"),
    "vf nopl/f0b": (f"{W}/readout/vf-nopl-S/fd_f0b_readout.json", "7ed24825"),
    "old nopl/f1": (f"{F}/readout/fd_f1_readout.json", "cbe411a9"),
    "vf nopl/f1": (f"{W}/readout/vf-nopl-S/fd_f1_readout.json", "e473f642"),
    "old S with/g": (f"{F}/with-cpl/readout/fd_g_readout.json", "b55366b3"),
    "vf S with/g": (f"{W}/readout/vf-with-S/fd_g_readout.json", "c9fe9d51"),
    "old S nopl/g": (f"{F}/readout/fd_g_readout.json", "75a9ddee"),
    "vf S nopl/g": (f"{W}/readout/vf-nopl-S/fd_g_readout.json", "a0d000d0"),
    "old E with/g": (f"{F}/gencmp-e/rerun1/chain/chdefs/with/readout/fd_g_readout.json", "a19009e0"),
    "vf E with/g": (f"{W}/readout/vf-with-E/fd_g_readout.json", "7034a08e"),
    "old E nopl/g": (f"{F}/gencmp-e/rerun1/chain/chdefs/nopl/readout/fd_g_readout.json", "d9a1ce38"),
    "vf E nopl/g": (f"{W}/readout/vf-nopl-E/fd_g_readout.json", "eefe1c6d"),
    "old dp": (f"{F}/with-cpl/data-product/fd_data_product_cpl.json", "d6752d2c"),
    "vf dp": (f"{W}/data-product/fd_data_product_vf.json", "1a37b082"),
    "s1": (f"{B}/s1/readout/s1_assembly.json", "81e5ef3f"),
    "cresp": ("docs/orchestration/state/measurement-scoping/assigned-uncertainties/cresp/cresp.json", "19bb2ee1"),
}
LISTING = ["f0", "with/f0b", "with/f1", "nopl/f0b", "nopl/f1"]
STAGEG = ["S with/g", "E with/g", "S nopl/g", "E nopl/g"]


def load():
    d = {}
    for k, (rel, pin) in PINS.items():
        raw = (ROOT / rel).read_bytes()
        h = hashlib.sha256(raw).hexdigest()
        if not h.startswith(pin):
            sys.exit(f"STOP: {rel} has sha256 {h[:12]}, pinned {pin}")
        d[k] = json.loads(raw)
    return d


def per_cell(v):
    return [v[c] for c in CELLS] if isinstance(v, dict) else list(v)


def triggers(r):
    out = {}
    for g, x in r["triggers"]["by_group"].items():
        out[g] = {"cells_abs_z_gt_2": x["cells_abs_z_gt_2"], "truths_p_lt_0.01": x["truths_p_lt_0.01"]}
    return out


def decision_rules(d):
    """Each listing (p < 0.01 or any |z| > 2) and trigger count, OLD -> V_F. A covariance that only grows can only clear
    a flag or lower a count; a new listing or a higher count is a STOP."""
    rows, stops = [], []
    for k in LISTING:
        o, n = d[f"old {k}"], d[f"vf {k}"]
        to, tn = {t["name"]: t for t in o["truths"]}, {t["name"]: t for t in n["truths"]}
        assert list(to) == list(tn), f"{k}: the truths differ"
        for name in to:
            a, b = bool(to[name]["listed"]), bool(tn[name]["listed"])
            ca, cb = to[name]["grade"]["cells_abs_z_gt_2"], tn[name]["grade"]["cells_abs_z_gt_2"]
            if a != b or ca != cb:
                rows.append({"readout": k, "truth": name, "graded": to[name]["graded"], "listed_old": a, "listed_vf": b,
                             "cells_old": ca, "cells_vf": cb, "p_old": to[name]["grade"]["p"],
                             "p_vf": tn[name]["grade"]["p"]})
                if (b and not a) or not set(cb) <= set(ca):
                    stops.append(f"{k} {name}: newly listed or a new |z| > 2 cell")
        go, gn = triggers(o), triggers(n)
        for g in go:
            for c in go[g]:
                if gn[g][c] > go[g][c]:
                    stops.append(f"{k} {g} {c}: {go[g][c]} -> {gn[g][c]}")
    counts = {k: {"old": triggers(d[f"old {k}"]), "vf": triggers(d[f"vf {k}"])} for k in LISTING}
    return rows, counts, stops


def stage_g(d):
    out = []
    for k in STAGEG:
        o = {p["name"]: p for p in d[f"old {k}"]["predictions"]}
        n = {p["name"]: p for p in d[f"vf {k}"]["predictions"]}
        assert list(o) == list(n)
        for name in o:
            for part in ("total", "shape_only"):
                a, b = o[name][part], n[name][part]
                assert a["ndf"] == b["ndf"]
                out.append({"chain": k, "prediction": name, "part": part, "ndf": a["ndf"], "chi2_old": a["chi2"],
                            "p_old": a["p"], "chi2_vf": b["chi2"], "p_vf": b["p"],
                            "crosses_0.01": (a["p"] < 0.01) != (b["p"] < 0.01)})
    return out


def sigma(d):
    o, n = d["old dp"]["relative_sigma"], d["vf dp"]["relative_sigma"]
    assert max(abs(a / b - 1) for a, b in zip(o["C_e"], n["C_e"])) < 1e-12, "the two products' C_e differ"
    f = n["f"] if "f" in n else d["vf dp"]["f"]
    M = d["vf dp"]["matrices"]
    ce_infl_model = [math.sqrt(M["C_e_infl"][i][i] + M["C_model_abs"][i][i]) / f[i] for i in range(16)]
    ce_model = [math.sqrt(M["C_e"][i][i] + M["C_model_abs"][i][i]) / f[i] for i in range(16)]
    s1 = d["s1"]["relative_sigma"]
    assert max(abs(a / b - 1) for a, b in zip(per_cell(s1["C_total"]), ce_model)) < 1e-8, "S1's C_total is not C_e + C_model"
    cols = {"C_e": o["C_e"], "C_e^infl": n["C_e_infl"],
            "C_total (S1)": per_cell(s1["C_total"]), "C_total^infl": ce_infl_model,
            "C_total_resp (cresp)": per_cell(d["cresp"]["relative_sigma"]["C_total_resp"]),
            "C_total_resp^infl": n["C_total_plus_C_resp_plus_DeltaC_e"],
            "C_rep OLD": o["C_total_plus_C_resp_plus_C_PL5D"], "C_rep V_F": n["C_total_plus_C_resp_plus_C_PL5D_plus_DeltaC_e"]}
    return cols


def med(v):
    s = sorted(v)
    return (s[7] + s[8]) / 2


def md(rec):
    L = ["# V_F (C_e^infl) Phase 1 readings, OLD -> C_e^infl", "",
         "From the Phase 1 readouts of FD-VF BINDING 1's run (#1356), read by `phase1_readings.py`. Readings go to the "
         "director first; nothing here is note wording.", "", "## 1. Decision-rule outcome changes (first)", ""]
    if rec["stops"]:
        L += ["**STOP: a flag set or a count raised under a covariance that only grows:**", ""] + [f"- {s}" for s in rec["stops"]] + [""]
    else:
        L += ["No flag is set and no count rises: every change below clears a flag or lowers a count.", ""]
    L += ["Rule: a truth is listed if p < 0.01 or any cell has |z| > 2 against its grade matrix (F0/F0b/F1).", "",
          "| readout | truth | graded | listed OLD | listed V_F | |z|>2 cells OLD | V_F | p OLD | p V_F |",
          "|---|---|---|---|---|---|---|---:|---:|"]
    for r in rec["listing_changes"]:
        L.append(f"| {r['readout']} | {r['truth']} | {r['graded']} | {r['listed_old']} | {r['listed_vf']} | "
                 f"{' '.join(r['cells_old']) or '-'} | {' '.join(r['cells_vf']) or '-'} | {r['p_old']:.3g} | {r['p_vf']:.3g} |")
    L += ["", "Trigger counts by group (cells with |z| > 2; truths with p < 0.01), OLD -> V_F:", "",
          "| readout | group | cells OLD | cells V_F | truths OLD | truths V_F |", "|---|---|---:|---:|---:|---:|"]
    for k, c in rec["trigger_counts"].items():
        for g in c["old"]:
            a, b = c["old"][g], c["vf"][g]
            L.append(f"| {k} | {g} | {a['cells_abs_z_gt_2']} | {b['cells_abs_z_gt_2']} | {a['truths_p_lt_0.01']} | "
                     f"{b['truths_p_lt_0.01']} |")
    L += ["", "**Not yet read (Phase 2):** PRR/RSN listings, V-ATLAS A3 and its validity list, C-R's and gover's labels, "
          "X's agreement, E2's seed-variation rule, the gdefs seed flags.", "",
          "**Bias regrades:** REGRADE (rg16, rg2d) and LL5D grade under truth-specific C_T and do not move (declaration "
          "section 4.3). Phase 2's recomputes run locally with the producers' own functions.", "",
          "## 2. Stage G, all four chains", ""]
    cross = [r for r in rec["stage_g"] if r["crosses_0.01"]]
    L += [f"Rows whose p crosses 0.01: {len(cross)}" + ("" if not cross else ": " + ", ".join(
          f"{r['chain']} {r['prediction']} {r['part']}" for r in cross)), "",
          "| chain | prediction | part | ndf | chi2 OLD | p OLD | chi2 V_F | p V_F |", "|---|---|---|---:|---:|---:|---:|---:|"]
    for r in rec["stage_g"]:
        L.append(f"| {r['chain']} | {r['prediction']} | {r['part']} | {r['ndf']} | {r['chi2_old']:.3f} | {r['p_old']:.3g} | "
                 f"{r['chi2_vf']:.3f} | {r['p_vf']:.3g} |")
    s = rec["sigma"]
    L += ["", "## 3. Per-cell relative sigma (percent), OLD and C_e^infl", "",
          "The C_e and C_e^infl columns are A2's per-cell table's pair; the six source columns are unchanged. The "
          "S1/C_resp rows are given both ways (C_e form, as printed now; C_e^infl form), for Joseph's open question "
          "(declaration section 4.3).", "",
          "| cell | " + " | ".join(s) + " |", "|---|" + "---:|" * len(s)]
    for i, c in enumerate(CELLS):
        L.append(f"| {c} | " + " | ".join(f"{100 * s[k][i]:.2f}" for k in s) + " |")
    L.append("| median | " + " | ".join(f"{100 * med(s[k]):.2f}" for k in s) + " |")
    L += ["", "## 4. Follow-ups for other lanes (after Phase 2 and the director's review)", "",
          "- `make_values_fived16.py`: `READOUTS`, `NOPL_READOUTS`, `ARMS`, `MATRIX_KEYS`; also its literal "
          "`\"C_total_plus_C_resp\"` (:678, :689) and the C_PL5D label it parses from the product (:700-702); "
          "Table IV through gdefs (:282-312) and gencmp_values' 2 x 2 (:314-404) need Phase 2's gdefs copy.",
          "- `make_supplemental.py`, `fived16_headline`, `fived16_genresidual`, the EA2 redraw, `valid_region.py`'s "
          "`COV_KEY` for a bound rerun.", "",
          "NOT CITABLE FOR: a validated size for C_e^infl; a coverage or calibration statement; any note wording."]
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, required=True)
    a = ap.parse_args(argv)
    d = load()
    rows, counts, stops = decision_rules(d)
    rec = {"schema": "fd-vf-readings-phase1/1", "pins": PINS,
           "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           "stops": stops, "listing_changes": rows, "trigger_counts": counts, "stage_g": stage_g(d), "sigma": sigma(d)}
    a.out_dir.mkdir(parents=True, exist_ok=True)
    (a.out_dir / "vf_readings_phase1.json").write_text(json.dumps(rec, indent=1) + "\n")
    (a.out_dir / "vf_readings_phase1.md").write_text(md(rec))
    print(f"stops {len(stops)}; listing changes {len(rows)}; stage G rows crossing 0.01: "
          f"{sum(r['crosses_0.01'] for r in rec['stage_g'])}")
    return 9 if stops else 0


if __name__ == "__main__":
    sys.exit(main())

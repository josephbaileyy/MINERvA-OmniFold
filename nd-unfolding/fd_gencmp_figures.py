#!/usr/bin/env python3
"""The paper's ratio figure (fig:ratio16) for Table IV's predictions as adopted from GENCMP
(DECISION-20261101-joseph-gencmp-paper-adoption.md items 1, 2 and 6): GENIE CV, GENIE + MEC, NuWro and GiBUU in the
corner "CH, analysis definitions" of GENCMP's step B (fd/gencmp/readout/defs.json, FD-GENCMP-REPORT.md sec. 2.2), and
MINERvA Tune v1 unchanged from Stage G.

fd_g_figures.py draws the figure: its inputs, K0 and K1 run unchanged on the with-block Stage G readouts
(FD-CT-5B-ADDITION-REPORT.md sec. 3), and only then are the four rebuilt predictions' g, g/f - 1, pulls and labels
put in place of Stage G's. The data side stays Stage G's record: f and sigma_total_over_f must agree with defs.json's
(1e-12 and 1e-10), and the cells and ndf must be equal. Everything after that is fd_g_figures.py's ratio model,
paint, K2-K8 and read-back, so the figure is drawn and checked exactly as before. The legend names the target and
the definitions; K7 requires each qualifier to stand in the substituted label.

MEASURES: nothing. CANNOT AUTHORIZE: a caption, a reading, a claim or paper text.

usage: fd_gencmp_figures.py --g-readout ... --definition ... --defs defs.json --out-dir DIR
       (the six fd_g_figures.py inputs of the with-block arm, then GENCMP's defs.json)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fd_g_figures as FG  # noqa: E402

BLOCK = "C_resp + C_PL5D"                       # the with-block arm's adopted extra block (its sidecars' option)
PINS = {                                        # the with-block readouts fd/with-cpl/figures/fd_g_fig_ratio.json read
    "g_readout": "b55366b3fd2d35a5426351531a9aa002a4d6be4b1048bd27339491e8c400a6fd",
    "g_diag_readout": "bfd529ab67ddf6e9d72de5ddda9d6318fe5b055b008b9af1bbd0af5d45a64de2",
    "g_followup_readout": "5c95c6d0f43ba0288d293e6b21f97c082f4a090adf22ca97fec1396df30f0633",
    "g_sens2_readout": "cff60b63a951834df1793e7785da7314bf675696e888c1ff3fda58e5df604c20",
    "f0b_readout": "5f542830561731b567f2b97d78e5e9677a9802a35ef9c21855828bf184e6f3d6",
    "definition": "b67907615fe2e903e60ae6caa1c141fa007676c0a1b3ae9f42490d331bfdda89",
}
DEFS_PIN = "544f4f4343095b5e78b59e0782ac3ce5ef5974b2e24dbb59be3708b5937556f8"
REBUILT = ("genie_cv", "genie_mec", "nuwro", "gibuu")
# each rebuilt prediction's legend qualifier, which its substituted label carries (K7)
QUALIFIER = {"genie_cv": "analysis definitions", "genie_mec": "analysis definitions",
             "nuwro": "CH, analysis definitions", "gibuu": "CH, analysis definitions"}
GIBUU_ONLY = "p_parallel < 4.5 cells only"


def substitute(r: dict, defs: dict) -> None:
    """Put defs.json's "CH, analysis definitions" predictions in place of Stage G's four, keeping Stage G's data."""
    FG.report("G0", "defs.json is GENCMP's step B readout, every sample complete and past B0 and B2",
              defs.get("schema") == "fd-gencmp-defs/1" and defs["not_read"] == [] and all(
                  st["B0"] is True and st["complete"] is True and st["B2"] in ("pass", "n/a")
                  for st in defs["status"].values()))
    for p in r["g_readout"]["predictions"]:
        n = p["name"]
        if n not in REBUILT:
            continue
        rec = defs["generators"][n]["CH"]["analysis_definitions"]["chi2"]["reported"]
        FG.report("G1", f"{n}: the rebuilt record is on Stage G's cells, data and reported sigma",
                  rec["cells"] == p["cells"] and FG.rel(rec["f"], p["f"]) <= 1e-12
                  and FG.rel(rec["sigma_total_over_f"], p["sigma_total_over_f"]) <= 1e-10
                  and rec["total"]["ndf"] == p["total"]["ndf"] and rec["shape_only"]["ndf"] == p["shape_only"]["ndf"])
        g = np.asarray(rec["g"], float)
        FG.report("G1", f"{n}: g/f - 1 is the record's on Stage G's f",
                  FG.rel(g / np.asarray(p["f"], float) - 1, rec["g_over_f_minus_1"]) <= 1e-10)
        p.update(g=rec["g"], g_over_f_minus_1=rec["g_over_f_minus_1"], pulls=rec["pulls"],
                 f_minus_g=rec["f_minus_g"], total=rec["total"], shape_only=rec["shape_only"],
                 label=f"{FG.SHORT[n]}; {QUALIFIER[n]}" + (f"; {GIBUU_ONLY}" if n == "gibuu" else ""))
        FG.QUALIFIERS[n] = (QUALIFIER[n],) + ((GIBUU_ONLY,) if n == "gibuu" else ())


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    for k in FG.INPUTS:
        ap.add_argument("--" + k.replace("_", "-"), dest=k, type=Path, required=True)
    ap.add_argument("--defs", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    a = ap.parse_args(argv)
    a.figures, a.ratio_form, a.gibuu_axis, a.reported_block_name = ["ratio"], "data-over-prediction", "separate", BLOCK
    outs = [a.out_dir / f"{FG.NAMES['ratio']}{ext}" for ext in (".pdf", ".json")]
    FG.report("K0", "no output exists (no overwrite)", not any(p.exists() for p in outs))
    FG.MF.style()
    r = FG.load(a, PINS)
    FG.check_chain(r, PINS, name=BLOCK)
    got = hashlib.sha256(a.defs.read_bytes()).hexdigest()
    FG.report("G0", "defs.json's sha256 is the pin", got == DEFS_PIN, f"{got} != {DEFS_PIN}")
    substitute(r, json.loads(a.defs.read_text()))
    model = FG.ratio_model(r, a.ratio_form, a.gibuu_axis, name=BLOCK)
    # the model names Stage G's readout as every value's source; for the four rebuilt predictions, g and the label
    # came from defs.json and from QUALIFIER here, while f and sigma_total_over_f stay Stage G's
    for it in model["items"]:
        for n in REBUILT:
            stage_g = f"fd_g_readout.json predictions[name={n}]"
            it["source"] = [f"defs.json generators[{n}].CH.analysis_definitions.chi2.reported.g" if src == f"{stage_g}.g"
                            else f"{stage_g}.label (substituted by fd_gencmp_figures.py)" if src == f"{stage_g}.label"
                            else src for src in it["source"]]
    FG.check_gibuu(model)
    FG.check_labels(model, r)
    FG.check_panels(model)
    fig = FG.draw("ratio", model)
    FG.readback(fig, model)
    pdf = FG.render(fig)
    FG.plt.close(fig)
    fig2 = FG.draw("ratio", model)
    again = FG.render(fig2)
    FG.plt.close(fig2)
    FG.check_pdf("ratio", pdf, again)
    code = FG.code_record()
    code["sha256"]["fd_gencmp_figures.py"] = hashlib.sha256(Path(__file__).resolve().read_bytes()).hexdigest()
    side = FG.sidecar("ratio", model, pdf, a, PINS, code)
    side.update(schema="fd-gencmp-figure-sidecar/1", controls_passed=side["controls_passed"] + ["G0", "G1"],
                labels={"what": "the paper's ratio figure for Table IV's predictions as adopted from GENCMP (CH, "
                                "analysis definitions); Stage G's data and sigma; drawn by fd_g_figures.py",
                        "not": "no caption, reading, claim or paper text"})
    side["inputs_sha256"]["gencmp_defs"] = DEFS_PIN
    # the model's sources keep Stage G's key names; these fields of these predictions came from defs.json instead
    side["substituted"] = {n: {"from": "defs.json generators[name].CH.analysis_definitions.chi2.reported",
                               "fields": ["g", "g_over_f_minus_1", "pulls", "f_minus_g", "total", "shape_only"],
                               "label": next(p["label"] for p in r["g_readout"]["predictions"] if p["name"] == n)}
                           for n in REBUILT}
    a.out_dir.mkdir(parents=True, exist_ok=True)
    meta = json.dumps(side, indent=1, allow_nan=False) + "\n"
    for out, data in zip(outs, (pdf, meta.encode())):
        tmp = out.with_name(out.name + ".partial")
        tmp.write_bytes(data)
        os.replace(tmp, out)
        print(json.dumps({"wrote": str(out), "sha256": hashlib.sha256(data).hexdigest()}), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

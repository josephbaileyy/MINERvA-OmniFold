#!/usr/bin/env python3
"""Generate values_landed.tex: the printed numbers of the results that landed from 2026-11-01 on, from their records.

usage: make_values_landed.py [--check]     (run from anywhere inside the repository; SKIP where the readouts are absent)

Two kinds of source, and no printed number is typed by hand in the note:
- a committed readout, pinned by sha256 in READOUTS (the digest each OUTCOME record states); a value is read at a key
  path and formatted here at its printed precision;
- an OUTCOME record line, for a number the record states but whose readout is not on main (the 1B receipt lives on
  its campaign branch) or which the record tabulates from the bound code (the 2D cell ranges). The literal must occur
  on that line of the record, or the run stops.
Assertions (ASSERT) pin the classes the prose states in words (for example the verdict UNDER-COVERS), so the words
cannot drift from the record either. --check fails unless the committed values_landed.tex equals a fresh generation.
Each key prints with \\lrval{key}; an unknown key stops the build.
"""
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

_top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, cwd=Path(__file__).parent)
ROOT = Path(_top.stdout.strip()) if _top.returncode == 0 else Path(__file__).resolve().parents[2]
OUT = Path(__file__).with_name("values_landed.tex")
FD = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd"
ST = "docs/orchestration/state/2d-closeout"
OR = "docs/orchestration"
READOUTS = {  # name: (path, sha256 as the OUTCOME record states it)
    "ar23": (f"{FD}/receipts-cov2d/readout/AR23/score_AR23.json",
             "fe5263e904f65892ce26b75fb279441230713c38675c2a3615c59d561c4f5ce1"),
    "g18": (f"{FD}/receipts-cov2d/readout/G18/score_G18.json",
            "849766942b3ecd9e6e72fd5db9d1a59815796b3f917875f8d0122b0c639088ec"),
    "vr": (f"{ST}/valid-region-20261107/receipts/read/readout.json",
           "91bb604e3a62e2654e611750830e225061e5c0b0255b12455a23ac9be4eec84c"),
    "pp": (f"{ST}/per-period-benchmark-20261106/receipts/read/readout.json",
           "4872df322a4e2e49ef009c4fa7eb78f273b8bea75a8a97855fd57451d229dca1"),
    "p1": (f"{FD}/receipts-1b/precheck-fd/p4/records/p4/readout.json",
           "8e05ca9bc2d0f2142b5c8d2bff28f05176c48f27454218390f09658344cea7b0"),
    "rg1": (f"{FD}/receipts-ref-g1/a1-read/readout.json",
            "4db170d36cffa0be2aeb53926e94158ef4e5e2e1d88fa50dd29baeace8ed6fd7"),
    # I2's readout, as its receipt's SHA256SUMS pins it (fd/receipts-1b/inv/i2/SHA256SUMS)
    "i2": (f"{FD}/receipts-1b/inv/i2/i2.json",
           "a9d3dc9c0e331eb635d6598c03b5bf95f6931f88c0cf0a43a1e73e2df9135bdb"),
}
REC = {
    "methods": f"{OR}/DECISION-20261106-joseph-methods-study-and-archive.md",
    "refg1": f"{OR}/OUTCOME-20261106-ref-g1-r1-differ.md",
    "refg1decl": "docs/orchestration/state/measurement-paper/5d-community-20261024/REF-G1-DECLARATION.md",
    "i2report": "docs/orchestration/state/measurement-paper/5d-community-20261024/FD-1B-INV-I2-REPORT.md",
    "keepblock": f"{OR}/DECISION-20261101-joseph-1b-keep-block-redesign-test.md",
    "stop": f"{OR}/OUTCOME-20261106-1b-stage1-receipt-stop.md",
    "cov2d": f"{OR}/OUTCOME-20261108-cov2d-both-tunes-under-cover.md",
    "fpsledger": "docs/orchestration/state/2d-closeout/stageF/methods/note-b8/ledger.md",
}
WORDS = {1: "one", 2: "two", 3: "three", 4: "four"}


def load():
    out = {}
    for name, (rel, sha) in READOUTS.items():
        if not (ROOT / rel).exists():
            return None
        b = (ROOT / rel).read_bytes()
        got = hashlib.sha256(b).hexdigest()
        if got != sha:
            sys.exit(f"FAIL: {rel}: sha256 {got} is not the record's {sha}")
        out[name] = json.loads(b)
    return out


def at(d, path):
    for k in path.split("/"):
        d = d[int(k)] if isinstance(d, list) else d[k]
    return d


def record(key, line, literal):
    text = (ROOT / REC[key]).read_text(encoding="utf-8").splitlines()[line - 1]
    if literal not in text:
        sys.exit(f"FAIL: {REC[key]}:{line} does not contain {literal!r}")
    return literal


def tex_num(x, nd):
    s = f"{x:.{nd}f}"
    return s.replace("-", "$-$") if s.startswith("-") else s


def cells_words(cs):
    cs = list(cs)
    return cs[0] if len(cs) == 1 else ", ".join(cs[:-1]) + " and " + cs[-1]


def build(R):
    V, A = {}, []  # values; assertion failures
    def expect(cond, what):
        if not cond:
            A.append(what)
    # --- COV2D (OUTCOME-20261108-cov2d-both-tunes-under-cover.md, sections 1-4 and CITABLE FOR)
    V["cov2d-ntoys"] = str(at(R["ar23"], "section_9_9/products"))
    expect(at(R["g18"], "section_9_9/products") == at(R["ar23"], "section_9_9/products"), "COV2D toy counts differ")
    for t in ("ar23", "g18"):
        g = R[t]["grade"]
        expect(R[t]["verdict"] == "UNDER-COVERS" and g["verdict"] == "UNDER-COVERS", f"{t} verdict")
        expect(R[t]["stop"] == [] and R[t]["controls_failed"] == [], f"{t} controls")
        V[f"cov2d-{t}-joint"] = str(g["joint_count"])
        V[f"cov2d-{t}-kjoint"] = str(g["k_joint"])
        V[f"cov2d-{t}-ndf"] = str(g["ndf"])
        V[f"cov2d-{t}-chi2ndf"] = tex_num(g["chi2_mean_over_ndf"], 2)
        V[f"cov2d-{t}-chi2ndf-se"] = tex_num(g["chi2_mean_over_ndf_se"], 2)
        V[f"cov2d-{t}-size"] = tex_num(g["size"]["per_truth_union_bound"], 4)
        fl = g["flagged_cells"]
        V[f"cov2d-{t}-flagged"] = cells_words([str(c) for c in fl])
        V[f"cov2d-{t}-nflagged"] = WORDS[len(fl)]
        for c in fl:
            a = g["attribution"][f"R{c}"]
            expect(a["driven_by"] == "bias", f"{t} cell {c} attribution")
            V[f"cov2d-{t}-{c}-count"] = str(g["counts"][c])
            V[f"cov2d-{t}-{c}-kc"] = str(a["k_flag"])
            V[f"cov2d-{t}-{c}-sc"] = tex_num(g["s_c"][c], 3)
            V[f"cov2d-{t}-{c}-pullmean"] = tex_num(a["pull_mean"], 2)
            V[f"cov2d-{t}-{c}-pullsd"] = tex_num(a["pull_sd"], 2)
        oc = g["outlier_cell"]
        expect(oc["cell"] == 216 and oc["flagged"] is False, f"{t} outlier cell")
    V["cov2d-size-max"] = tex_num(max(R[t]["grade"]["size"]["per_truth_union_bound"] for t in ("ar23", "g18")), 3)
    V["cov2d-cell29-range"] = record("cov2d", 52, "0.07–0.15, 15–20").replace("–", "--")
    V["cov2d-cell56-range"] = record("cov2d", 53, "0.25–0.33, 6–7").replace("–", "--")
    V["cov2d-res-cell"] = record("cov2d", 91, "0.10–0.13").replace("–", "--")
    V["cov2d-res-joint"] = record("cov2d", 91, "0.08")
    # --- the 1B stage-1 receipt STOP (OUTCOME-20261106-1b-stage1-receipt-stop.md; the receipt is on its campaign branch)
    V["stop-flagged"] = record("stop", 27, "892")
    V["stop-draws"] = record("stop", 27, "900")
    V["stop-maxcells"] = record("stop", 29, "is 62")[len("is "):]
    # --- valid regions (OUTCOME-20261107-valid-region.md, sections 1-3)
    cells = [f"R{i:02d}" for i in range(16)]
    va, vp = at(R["vr"], "readings/V-ATLAS/valid"), at(R["vr"], "readings/V-PRIOR/valid")
    V["vr-atlas-nvalid"], V["vr-prior-nvalid"] = str(len(va)), str(len(vp))
    V["vr-atlas-not"] = cells_words([c for c in cells if c not in va])
    V["vr-prior-not"] = cells_words([c for c in cells if c not in vp])
    V["vr-both-n"] = str(len([c for c in cells if c in va and c in vp]))
    V["vr-prior-tau"] = str(at(R["vr"], "readings/V-PRIOR/tau"))
    for c in [c for c in cells if c not in va]:
        V[f"vr-{c}-z-gibuu"] = tex_num(at(R["vr"], f"readings/V-ATLAS/cells/{c}/z/A7_gibuu"), 2)
    # --- the per-period 2D benchmark (OUTCOME-20261107-per-period-2d-benchmark.md, sections 2-3)
    pp = R["pp"]["readings"]
    expect(at(pp, "classes/R5") == "no change" and at(pp, "classes/R5bar") == "farther without 1G-1M", "R5 classes")
    V["pp-combined"] = pp["combined_statement"]
    V["pp-nrep"] = str(pp["n_replicas"])
    V["pp-ncells"] = str(pp["n_cells"])
    ck = [c for c in R["pp"]["controls"] if c["id"] == "C-K"][0]
    expect(ck["verdict"] == "PASS" and ck["k_measured"] == ck["k_declared"], "C-K")
    V["pp-nk"] = str(ck["k_measured"])
    V["pp-nkbar"] = str(pp["n_cells"] - ck["k_measured"])
    for m, tag in (("replica", "rep"), ("replica+seed", "seed")):
        V[f"pp-k-z-{tag}"] = tex_num(at(pp, f"by_model/{m}/R5/z"), 2)
        V[f"pp-kbar-z-{tag}"] = tex_num(at(pp, f"by_model/{m}/R5bar/z"), 2)
    V["pp-k-res"] = tex_num(at(pp, "by_model/replica/R5/resolved_3sigma"), 2)
    V["pp-kbar-delta"] = tex_num(-at(pp, "by_model/replica/R5bar/delta"), 2)
    V["pp-kbar-frac"] = tex_num(-at(pp, "by_model/replica/R5bar/fraction"), 2)
    # --- the 1B pre-check, Part 1 (OUTCOME-20261108-1b-precheck-part1.md)
    p1 = R["p1"]
    for grp in ("flux", "detector"):
        expect(at(p1, f"groups/{grp}/rule_S/verdict") == "REPRODUCED", f"group {grp}")
    for b in ("Flux", "GEANT_Pion", "MinosEfficiency"):
        expect(at(p1, f"bands/{b}/rule_K/verdict") == "PASS", f"band {b} rule K")
    for b, tag in (("GEANT_Neutron", "neutron"), ("GEANT_Proton", "proton")):
        expect(at(p1, f"bands/{b}/rule_S/verdict") == "DEPARTS", f"band {b} rule S")
        V[f"p1-{tag}-cells"] = cells_words(at(p1, f"bands/{b}/rule_S/cells_outside"))
    expect(at(p1, "window") == [0.9, 1.1], "pre-check window")
    # --- the response-only sensitivity (DECISION-20261101-joseph-1b-keep-block-redesign-test.md item 1): sqrt(B/M) per
    # cell from I2's committed M and B (FD-1B-INV-I2-REPORT.md sec. 5), its median and range checked against the
    # report's printed arithmetic (:299) and printed at the decision's precision (:38-39)
    i2 = R["i2"]
    expect(i2["cells"] == [f"R{i:02d}" for i in range(16)], "I2 cells")
    r = sorted(math.sqrt(b / m) for b, m in zip(i2["B"], i2["M"]))
    med, lo, hi = (r[7] + r[8]) / 2, r[0], r[-1]
    record("i2report", 299, f"median {med:.3f} and range {lo:.3f}–{hi:.3f}")
    record("keepblock", 38, f"median {med:.2f}×")
    record("keepblock", 39, f"{lo:.2f}–{hi:.2f}")
    V["i2-resp-med"], V["i2-resp-lo"], V["i2-resp-hi"] = f"{med:.2f}", f"{lo:.2f}", f"{hi:.2f}"
    # --- REF-G1, the sixteen-cell binned head-to-head (OUTCOME-20261106-ref-g1-r1-differ.md; a stated limitation,
    # DECISION-20261108-joseph-note-framing-and-estimator-dependence.md item 3)
    g1 = R["rg1"]
    expect(g1["R1"]["reading"] == "differ" and g1["controls_pass"] is True, "REF-G1 R1")
    expect(g1["R2"]["nuwro"]["reading"] == "IBU worse" and g1["R2"]["tune_v1"]["reading"] == "IBU better", "REF-G1 R2")
    V["rg1-T"] = record("refg1", 16, f"T = {g1['R1']['T']:.1f}")[len("T = "):]
    b1, b2 = g1["R1"]["bars"]
    V["rg1-bar1"], V["rg1-lev1"] = record("refg1", 17, f"{b1:.2f} (0.95)").split(" ")[0], "0.95"
    V["rg1-bar2"], V["rg1-lev2"] = record("refg1", 17, f"{b2:.2f} (0.997)").split(" ")[0], "0.997"
    V["rg1-K"] = record("refg1decl", 130, "K = 5")[len("K = "):]
    V["rg1-r2-nuwro"] = tex_num(g1["R2"]["nuwro"]["ratio"], 2)
    r3 = g1["R3"]["sigma_ibu_over_e"]
    expect(len(r3) == 16, "REF-G1 R3 cells")
    V["rg1-r3-med"] = record("refg1", 35, f"{g1['R3']['median']:.2f}")
    V["rg1-r3-lo"] = record("refg1", 35, f"{min(r3):.2f}")
    V["rg1-r3-hi"] = record("refg1", 36, f"{max(r3):.2f}")
    # --- the rounding-level shift, as the methods-study decision states it (:20; FD-STAB's NONE_PASS)
    V["stab-max"] = record("methods", 20, "2.6")
    # --- extended-fiducial tier shares (note-b8/ledger.md row E7)
    V["fps-tier1-pct"] = record("fpsledger", 81, "6")
    V["fps-tier2-pct"] = record("fpsledger", 81, "28")
    if A:
        sys.exit("FAIL: a record no longer says what the prose states: " + "; ".join(A))
    return V


def render(V):
    # one paragraph per line, blank-separated, so reflow_tex.py --note leaves the file as generated
    lines = ["% Generated by make_values_landed.py from the records it pins (readouts by sha256, OUTCOME lines by literal). "
             "Do not edit. Regenerate: python3 docs/analysis-note/make_values_landed.py",
             "\\makeatletter",
             "\\providecommand{\\lrval}[1]{\\@ifundefined{lr@#1}{\\errmessage{values_landed: no value '#1'}}{\\@nameuse{lr@#1}}}"]
    for k in sorted(V):
        lines += ["", f"\\@namedef{{lr@{k}}}{{{V[k]}}}"]
    lines += ["", "\\makeatother"]
    return "\n".join(lines) + "\n"


def main():
    R = load()
    if R is None:  # the standalone note repository carries no readouts (as make_values_fived16.py)
        print(f"SKIP: the pinned readouts are not in this tree; {OUT.name} is used as committed")
        return
    text = render(build(R))
    if "--check" in sys.argv[1:]:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != text:
            sys.exit(f"FAIL: {OUT.name} is not a fresh generation; run make_values_landed.py")
        print(f"OK: {OUT.name} is fresh")
        return
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT.name}: {text.count(chr(92) + '@namedef')} keys")


if __name__ == "__main__":
    main()

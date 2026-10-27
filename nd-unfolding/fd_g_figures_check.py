#!/usr/bin/env python3
"""An independent check of fd_g_figures.py's outputs (FD-G-FIGURES-DECLARATION.md section 2.3): every item of every
sidecar's plotted model is re-derived from the readouts' keys by this file's own code, which imports nothing of the
figure tool, and the sidecar's digests are recomputed from the files.

* ratio: each prediction's points against f/g (or 1 + g_over_f_minus_1), their cells against Stage G's (GiBUU's
  against the definition's p_parallel < 4.5 boxes), the error-bar ends against (f/g)(1 -+ sigma/f), the data band
  against 1 -+ sigma/f, every key interval against the definition's boxes (the full range taken from the boxes'
  union), every name against Stage G's label.
* modes: every bar against top_modes[k].loadings, every printed mode index, fraction, sigma and distance against
  modes_by_chi2[k] to its printed precision, each row label in its own row.
* sens: every curve against the records sorted by alpha, every ndf against Stage G's, every family name against the
  readouts' families, the note against G-SENS's label.
* Every other item (reference lines, separators, ticks, axis labels, headers) against its declared value.

An item no rule visits is a failure. Exit 0 if every check passes, 1 otherwise; it writes nothing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

INPUTS = ("g_readout", "g_diag_readout", "g_followup_readout", "g_sens2_readout", "f0b_readout", "definition")
FIGURES = {"ratio": "fd_g_fig_ratio", "modes": "fd_g_fig_modes", "sens": "fd_g_fig_sens"}
PLAIN = (("$^{12}$C", "C12"), (r"$p_\parallel$", "p_parallel"))
MUST = ("C12 target; no correction to CH applied", "prior (not an independent prediction)",
        "p_parallel < 4.5 cells only")
KEY_AXES = ("pt", "pz", "eavail", "q3", "W")
# the declared layout and wording (FD-G-FIGURES-DECLARATION.md section 4), written out here
OFFSETS = {"genie_cv": -0.3, "genie_mec": -0.15, "nuwro": 0.0, "gibuu": 0.15, "mnvtune_v1": 0.3}
KEY_LABELS = {"pt": "$p_T$ (GeV/$c$)", "pz": "$p_\\parallel$ (GeV/$c$)", "eavail": "$E_{\\mathrm{avail}}$ (GeV)",
              "q3": "$q_3$ (GeV/$c$)", "W": "$W$ (GeV)"}
YLABEL = {"data-over-prediction": "data / prediction", "prediction-over-data": "prediction / data"}
NAMES = {"genie_cv": "GENIE 2.12.10 CV, no MEC", "genie_mec": "GENIE 2.12.10 + Valencia MEC",
         "nuwro": "NuWro 21.09: $^{12}$C target; no correction to CH applied",
         "gibuu": "GiBUU 2019: $^{12}$C target; no correction to CH applied; $p_\\parallel$ < 4.5 cells only",
         "mnvtune_v1": "MINERvA Tune v1: prior (not an independent prediction)"}
ORDER = ("genie_cv", "genie_mec", "nuwro", "gibuu", "mnvtune_v1")
SIXTEEN = ("genie_cv", "genie_mec", "nuwro", "mnvtune_v1")
TOP = 3
TOL = 1e-12


class Checker:
    def __init__(self):
        self.failed, self.n = [], 0

    def __call__(self, what: str, ok: bool) -> bool:
        self.n += 1
        if not ok:
            self.failed.append(what)
            print(f"FAIL {what}", flush=True)
        return ok


def sha256(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def close(a, b, tol=TOL) -> bool:
    a, b = list(map(float, a)), list(map(float, b))
    return len(a) == len(b) and all(abs(x - y) <= tol * max(abs(x), abs(y), 1e-300) for x, y in zip(a, b))


def plain(text: str) -> str:
    for tex, p in PLAIN:
        text = text.replace(tex, p)
    return text


def declared(text: str, n: str) -> bool:
    """The drawn name is the declared one (section 4), with its qualifiers, on one line or broken after its ':'."""
    return text in (NAMES[n], NAMES[n].replace(": ", ":\n", 1))


def name_ok(text: str, label: str) -> bool:
    """The drawn name: the start of Stage G's label, then ": " and qualifiers that stand in it; every qualifier the
    director required that stands in the label is drawn."""
    t = plain(text).replace(":\n", ": ", 1)
    name, _, qual = t.partition(": ")
    quals = qual.split("; ") if qual else []
    joined = "; ".join(quals)
    return (bool(name) and label.startswith(name) and label[len(name):len(name) + 1] in (";", ",", ":", "")
            and all(q in label for q in quals) and all(m in joined for m in MUST if m in label))


def full_range(defn: dict) -> dict:
    cells = defn["reporting_cells"]
    return {ax: (min(c["box"][ax][0] for c in cells), max(c["box"][ax][1] for c in cells)) for ax in KEY_AXES}


def printed(lo: float, hi: float, full: tuple) -> str:
    if (lo, hi) == full:
        return "all"
    if lo == full[0]:
        return f"< {hi:g}"
    if hi == full[1]:
        return f"> {lo:g}"
    return f"{lo:g}–{hi:g}"


def nums(text: str) -> list[float]:
    return [float(x) for x in re.findall(r"[-+]?\d+(?:\.\d+)?", text.replace("$\\chi^2$", ""))]


def check_ratio(m: dict, r: dict, ck: Checker, seen: set, options: dict) -> None:
    g, defn = r["g_readout"], r["definition"]
    P = {p["name"]: p for p in g["predictions"]}
    form = m["form"]
    ck("ratio: the model's form and GiBUU axis are the run's options", form == options["ratio_form"]
       and m["gibuu_axis"] == options["gibuu_axis"] and len(m["axes"]) == (2 if m["gibuu_axis"] == "separate" else 1))
    ck("ratio: the predictions are Stage G's five, in order", [p["name"] for p in g["predictions"]] == list(ORDER))
    gib = [f"R{c['id']:02d}" for c in defn["reporting_cells"] if c["box"]["pz"][1] <= 4.5]
    sig = P[g["predictions"][0]["name"]]["sigma_total_over_f"]
    I = {it["gid"]: it for it in m["items"]}
    for n, p in P.items():
        cells = [int(c[1:]) for c in p["cells"]]
        if n == "gibuu":
            ck("ratio: GiBUU's cells are the definition's p_parallel < 4.5 cells", p["cells"] == gib)
        it = I.get(f"ratio:{n}")
        if not ck(f"ratio:{n} is plotted", it is not None):
            continue
        seen.add(it["gid"])
        ck(f"ratio:{n} sits on its own cells, at its offset", it["cells"] == p["cells"]
           and close(it["x"], [c + OFFSETS[n] for c in cells]))
        ck(f"ratio:{n} is drawn as points", it["style"]["ls"] == "None")
        want_axes = 1 if (n == "gibuu" and m["gibuu_axis"] == "separate") else 0
        ck(f"ratio:{n} is on its declared axes", it["axes"] == want_axes)
        f, gg, s = p["f"], p["g"], p["sigma_total_over_f"]
        if form == "data-over-prediction":
            y = [a / b for a, b in zip(f, gg)]
            ck(f"ratio:{n} is f/g", close(it["y"], y))
            e = I.get(f"ratio:{n}:err")
            if ck(f"ratio:{n}:err is plotted", e is not None):
                seen.add(e["gid"])
                ck(f"ratio:{n}:err is on its series' axes", e["axes"] == it["axes"])
                ck(f"ratio:{n}:err is (f/g)(1 -+ sigma/f) on the same x", e["x"] == it["x"] and close(
                    e["lo"], [q - q * t for q, t in zip(y, s)]) and close(e["hi"], [q + q * t for q, t in zip(y, s)]))
        else:
            ck(f"ratio:{n} is 1 + g_over_f_minus_1", close(it["y"], [1 + q for q in p["g_over_f_minus_1"]]))
            ck(f"ratio:{n} has no error bar", f"ratio:{n}:err" not in I)
        lg = I.get(f"ratio:{n}:legend")
        if ck(f"ratio:{n}:legend is drawn", lg is not None):
            seen.add(lg["gid"])
            ck(f"ratio:{n}:legend names it as Stage G's label does", name_ok(lg["text"], p["label"])
               and lg["series"] == f"ratio:{n}")
            ck(f"ratio:{n}:legend is the declared name", declared(lg["text"], n))
    for gid, it in I.items():
        if gid.startswith("ratio:data:"):
            seen.add(gid)
            ck(f"{gid} is 1 -+ sigma/f on every cell", form == "prediction-over-data" and len(it["rects"]) == 16
               and all(close([q[1], q[1] + q[3]], [1 - t, 1 + t]) and abs(q[0] + q[2] / 2 - i) <= 1e-12
                       for i, (q, t) in enumerate(zip(it["rects"], sig))))
    full = full_range(defn)
    for c in defn["reporting_cells"]:
        for ax in KEY_AXES:
            gid = f"ratio:key:{ax}:R{c['id']:02d}"
            it = I.get(gid)
            if ck(f"{gid} is drawn", it is not None):
                seen.add(gid)
                ck(f"{gid} is the definition's box", it["text"] == printed(*c["box"][ax], full[ax]))
    for gid, it in I.items():
        if it["kind"] == "ref":
            seen.add(gid)
            ck(f"{gid} is the line at 1 or a separator between groups of four",
               (it["orient"] == "h" and it["value"] == 1.0) or (it["orient"] == "v" and it["value"] in (3.5, 7.5, 11.5)))
        elif it["kind"] == "ticks":
            seen.add(gid)
            ck(f"{gid} labels the cells", it["labels"] == g["cells"])
        elif it["kind"] == "ylabel":
            seen.add(gid)
            ck(f"{gid} names the ratio's form", it["text"] == YLABEL[form])
        elif gid.startswith("ratio:keylabel:"):
            seen.add(gid)
            ck(f"{gid} names its axis and unit", it["text"] == KEY_LABELS[gid.rsplit(":", 1)[1]])


def check_modes(m: dict, r: dict, ck: Checker, seen: set, options: dict) -> None:
    g, dg = r["g_readout"], r["g_diag_readout"]
    cells = g["cells"]
    I = {it["gid"]: it for it in m["items"]}
    rows = [p["name"] for p in g["predictions"] if len(p["cells"]) == 16]
    ck("modes: no GiBUU item", not any(gid.startswith("modes:gibuu") for gid in I))
    for i, n in enumerate(rows):
        rec = next(p for p in dg["predictions"] if p["name"] == n)
        rt = next(c for c in rec["comparisons"] if c["comparison"] == "reported")["relative_to_f"]
        ranks = sorted({int(gid.split(":")[2]) for gid in I if re.fullmatch(rf"modes:{n}:\d+", gid)})
        ck(f"modes:{n} draws ranks 1..{TOP}", ranks == list(range(1, TOP + 1)) and rows == list(SIXTEEN))
        for k in ranks:
            b, mk = I[f"modes:{n}:{k}"], rt["modes_by_chi2"][k - 1]
            t = next(x for x in rt["top_modes"] if x["mode"] == mk["mode"])
            seen.add(b["gid"])
            ck(f"modes:{n}:{k} is in row {n}, column rank {k}", b["axes"] == i * TOP + (k - 1))
            ck(f"modes:{n}:{k} bars are the loadings of the rank-{k} mode by chi2",
               b["x"] == list(range(16)) and close(b["heights"], [t["loadings"][c] for c in cells]))
            t0, t1 = I.get(f"modes:{n}:{k}:text0"), I.get(f"modes:{n}:{k}:text1")
            if ck(f"modes:{n}:{k} texts are drawn in its panel", t0 is not None and t1 is not None
                  and t0["axes"] == t1["axes"] == b["axes"]):
                seen |= {t0["gid"], t1["gid"]}
                a, c = nums(t0["text"]), nums(t1["text"])
                z = mk["projection"] / mk["sigma"]
                ck(f"modes:{n}:{k} prints its mode, fraction, sigma and distance",
                   len(a) == 2 and len(c) == 2 and a[0] == mk["mode"] and abs(a[1] - 100 * mk["fraction"]) <= 0.05 + 1e-9
                   and abs(c[0] - 100 * mk["sigma"]) <= 0.005 + 1e-9 and abs(c[1] - z) <= 0.005 + 1e-9
                   and abs(z * z - mk["chi2"]) <= 1e-9 * mk["chi2"])
        lab = I.get(f"modes:{n}:label")
        if ck(f"modes:{n}:label is drawn", lab is not None):
            seen.add(lab["gid"])
            ck(f"modes:{n}:label is the declared name", declared(lab["text"], n))
            ck(f"modes:{n}:label names it as Stage G's label does, over its own rank-1 panel",
               name_ok(lab["text"], next(p for p in g["predictions"] if p["name"] == n)["label"])
               and lab["axes"] == I[f"modes:{n}:1"]["axes"])
    for gid, it in I.items():
        if it["kind"] == "ref":
            seen.add(gid)
            ck(f"{gid} is the zero line or a separator", (it["orient"] == "h" and it["value"] == 0.0)
               or (it["orient"] == "v" and it["value"] in (3.5, 7.5, 11.5)))
        elif it["kind"] == "ticks":
            seen.add(gid)
            ck(f"{gid} labels the cells", it["labels"] == cells)
        elif gid.startswith("modes:header:"):
            seen.add(gid)
            k = int(gid.rsplit(":", 1)[1])
            ck(f"{gid} names its rank over its column", it["text"] == f"rank {k} by $\\chi^2$" and it["axes"] == k - 1)
        elif gid == "modes:ylabel":
            seen.add(gid)
            ck(f"{gid} is 'loading'", it["text"] == "loading")


def check_sens(m: dict, r: dict, ck: Checker, seen: set, options: dict) -> None:
    g, fu, s2 = r["g_readout"], r["g_followup_readout"], r["g_sens2_readout"]
    I = {it["gid"]: it for it in m["items"]}
    fams = {**fu["constants"]["families"], **s2["constants"]["families"]}
    recs = fu["sens"]["records"] + s2["sens"]["records"]
    ck("sens: five families", sorted(fams) == sorted(["interaction", "c_e_systematic", "flux", "detector", "lateral"]))
    for p in g["predictions"]:
        n, axes = p["name"], set()
        for fam in fams:
            it = I.get(f"sens:{n}:{fam}")
            if not ck(f"sens:{n}:{fam} is plotted", it is not None):
                continue
            seen.add(it["gid"])
            axes.add(it["axes"])
            want = sorted((x["alpha"], x["chi2"]) for x in recs if x["family"] == fam and x["prediction"] == n)
            ck(f"sens:{n}:{fam} is the records' chi2 against alpha", close(it["x"], [a for a, _ in want])
               and close(it["y"], [c for _, c in want]))
            ck(f"sens:{n}:{fam} is dashed only for the joint family", it["style"]["ls"] == (
                "--" if len(fams[fam]) > 1 else "-"))
        for suffix in ("label", "ndf"):
            it = I.get(f"sens:{n}:{suffix}")
            if ck(f"sens:{n}:{suffix} is drawn in its panel", it is not None and axes == {it["axes"]}):
                seen.add(it["gid"])
        ck(f"sens:{n}:label names it as Stage G's label does", name_ok(I[f"sens:{n}:label"]["text"], p["label"])
           and declared(I[f"sens:{n}:label"]["text"], n))
        ck(f"sens:{n} has its own panel", axes == {ORDER.index(n)})
        ck(f"sens:{n}:ndf is Stage G's", I[f"sens:{n}:ndf"]["text"] == f"ndf {p['total']['ndf']}")
    for fam, groups in fams.items():
        it = I.get(f"sens:legend:{fam}")
        if ck(f"sens:legend:{fam} is drawn", it is not None):
            seen.add(it["gid"])
            ck(f"sens:legend:{fam} names the family's groups", it["text"] == " + ".join(groups) + (
                " (joint)" if len(groups) > 1 else " alone") and it["series"].endswith(f":{fam}"))
    note = I.get("sens:note")
    if ck("sens:note is drawn", note is not None):
        seen.add(note["gid"])
        ck("sens:note is G-SENS's label", note["text"].replace(",\n", ", ", 1) == fu["sens"]["label"]
           == s2["sens"]["label"])
    for gid, it in I.items():
        if it["kind"] == "ticks":
            seen.add(gid)
            ck(f"{gid} labels the alphas", it["labels"] == [f"{x:g}" for x in fu["constants"]["alphas"]])
        elif it["kind"] in ("xlabel", "ylabel"):
            seen.add(gid)
            ck(f"{gid} names its axis", it["text"] == {"xlabel": r"$\alpha$", "ylabel": r"$\chi^2$"}[it["kind"]])
        elif gid == "sens:legend:title":
            seen.add(gid)


CHECK = {"ratio": check_ratio, "modes": check_modes, "sens": check_sens}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    for k in INPUTS:
        ap.add_argument("--" + k.replace("_", "-"), dest=k, type=Path, required=True)
    ap.add_argument("--figures-dir", type=Path, required=True)
    a = ap.parse_args(argv)
    ck = Checker()
    r = {k: json.loads(getattr(a, k).read_text()) for k in INPUTS}
    digests = {k: sha256(getattr(a, k)) for k in INPUTS}
    found = 0
    for name, stem in FIGURES.items():
        side = a.figures_dir / f"{stem}.json"
        if not side.exists():
            continue
        found += 1
        s = json.loads(side.read_text())
        pdf = a.figures_dir / s["file"]
        ck(f"{name}: the sidecar names its figure and file", s["figure"] == name and s["file"] == f"{stem}.pdf")
        ck(f"{name}: the PDF's sha256 is the sidecar's", pdf.exists() and sha256(pdf) == s["pdf_sha256"])
        ck(f"{name}: the inputs' sha256 are the sidecar's", s["inputs_sha256"] == digests)
        m = s["plotted"]
        seen: set = set()
        CHECK[name](m, r, ck, seen, s["options"])
        unvisited = sorted({it["gid"] for it in m["items"]} - seen)
        ck(f"{name}: every plotted item is checked ({len(m['items'])})", not unvisited)
        if unvisited:
            print(f"     unchecked: {unvisited[:8]}", flush=True)
    ck("at least one sidecar", found > 0)
    print(f"{'OK' if not ck.failed else 'FAILED'}: {ck.n} checks, {len(ck.failed)} failed, {found} sidecars",
          flush=True)
    return 0 if not ck.failed else 1


if __name__ == "__main__":
    raise SystemExit(main())

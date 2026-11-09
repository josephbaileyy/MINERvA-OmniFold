#!/usr/bin/env python3
"""Build the short paper once per pre-written outcome case and print the text each case changes, from the PDF.

usage: build_cases.py <worktree> <out-dir>      (or: build_cases.py --recut <out-dir>, from the saved builds)

Every case gives each key of its group a declared class (make_values_fived16.PENDING) through pending_lines(), the
same path a fill takes; the other groups stay pending. A printed value that does not exist yet (cells, levels) is an
obviously hypothetical stand-in in square brackets. Each build's pdftotext is written to <out-dir>/<case>.txt, and the
changed passages are cut from it between fixed anchors (text that no case changes) and written to
<out-dir>/passages.json. Nothing in the worktree is written.
"""
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

NOTE = "docs/analysis-note"

C1 = "[cells R03, R11, with their coverage fractions]"
C2 = "[cell R06, with its coverage fraction]"


def P(g, a, bg=None, ba=None):
    """The four (tune, reading) classes: primary at G18 and AR23, then with the bands (default: the same)."""
    return {("g18", "minus2"): g, ("ar23", "minus2"): a, ("g18", "all"): bg or g, ("ar23", "all"): ba or a}


c, uc, uj, ujc, i = "covers", "under-cells", "under-joint-only", "under-joint", "invalid"
CELLS = {(t, r): C1 if t == "ar23" else C2 for t in ("g18", "ar23") for r in ("minus2", "all")}
CELLS.update({(t, r, x): C1 if t == "ar23" else C2 for t in ("g18", "ar23") for r in ("minus2", "all")
              for x in ("weak", "over", "clip")})
NUM = {("ar23", "all", "why"): "[the numerical check of the grade that failed]"}
# case -> (campaign, per, route, flags, text) for make_values_fived16.ll5d_case
LL5D_CASES = {
    "cov-all-cover": ("graded", P(c, c), "direct", {}, {}),
    "cov-all-cover-qualified": ("graded", P(c, c), "direct",
                                {("g18", "minus2", "weak"): "some", ("ar23", "minus2", "over"): "some",
                                 ("ar23", "all", "weak"): "some"}, {}),
    "cov-bands-under-one": ("graded", P(c, c, c, uc), "direct", {}, {}),
    "cov-bands-under-both": ("graded", P(c, c, uc, ujc), "direct", {}, {}),
    "cov-bands-invalid-one": ("graded", P(c, c, c, i), "direct", {}, NUM),
    "cov-bands-invalid-both": ("graded", P(c, c, i, i), "direct", {}, {}),
    "cov-primary-under-bands-cover": ("graded", P(c, uc, c, c), "direct", {}, {}),
    "cov-primary-invalid-bands-cover": ("graded", P(i, i, c, c), "direct", {}, {}),
    "cov-one-under-cells": ("graded", P(c, uc), "direct", {}, {}),
    "cov-one-under-clip": ("graded", P(c, uc), "direct", {("ar23", "minus2", "clip"): "some", ("ar23", "all", "clip"): "some"}, {}),
    "cov-one-under-joint-only": ("graded", P(c, uj), "direct", {}, {}),
    "cov-mixed-cell-joint": ("graded", P(uc, uj, ujc, c), "direct", {}, {}),
    "cov-both-under-joint": ("graded", P(ujc, ujc), "direct", {}, {}),
    "cov-invalid-one-covers": ("graded", P(i, c), "direct", {}, {}),
    "cov-invalid-one-under": ("graded", P(i, uc), "direct", {}, {}),
    "cov-invalid-all": ("graded", P(i, i), "direct", {}, {}),
    "cov-proceeded-cover": ("graded", P(c, c), "offset-proceeded", {}, {}),
    "cov-proceeded-under": ("graded", P(c, uc), "offset-proceeded", {}, {}),
    "cov-repaired-cover": ("graded", P(c, c), "repaired", {}, {}),
    "cov-repaired-under": ("graded", P(ujc, ujc), "repaired", {}, {}),
    "cov-gate-failed": ("gate-failed", None, "direct", {}, {}),
    "cov-offset-stopped": ("offset-stopped", None, "direct", {}, {}),
    "cov-stop": ("stop", None, "direct", {}, {}),
}


def prr(g, q, kg, kq):
    """The prior-retention group with PR-2a classes g (GiBUU hybrid) and q (q3 tilt) and PR-2b classes kg, kq. Only the
    labels the IBU classes force are set (FD-PRR §5.4: the implementation-specific share where the IBU retains less)."""
    v = {"prr-pr2a-gibuu": g, "prr-pr2a-q3": q, "prr-pr2b-gibuu": kg, "prr-pr2b-q3": kq, "prr-abs": f"{g}-{q}"}
    for t, a in (("gibuu", g), ("q3", q)):
        for f in ("F1", "F2", "F3", "F4"):
            v[f"prr-pr1-{f}-{t}"] = "undefined" if a == "undefined" else "no-effect"
        for lab in ("fir", "info", "impl", "obs", "stat", "unattr"):
            v[f"prr-label-{lab}-{t}"] = "holds" if (lab == "impl" and a == "less") else "not"
    v.update({"prr-pr3-any": "not", "prr-pr3-ibu": "not", "prr-pr3-levels": "[levels]", "prr-ibu-bar": "[the bar]"})
    return v


PRR_CASES = {"ibu-less": ("less", "less", "falls", "falls"), "ibu-same": ("same", "same", "flat", "flat"),
             "ibu-more": ("more", "more", "rises", "rises"), "ibu-undefined": ("undefined", "undefined", "undefined", "undefined"),
             "ibu-split-less-same": ("less", "same", "falls", "flat"), "ibu-split-same-more": ("same", "more", "flat", "rises")}


def cases(mv):
    out = {}
    for name, (camp, per, route, flags, text) in LL5D_CASES.items():
        out[name] = mv.ll5d_case(camp, per, route, flags, CELLS, text)
    for name, args in PRR_CASES.items():
        out[name] = prr(*args)
    return out


# anchors: fixed text around each changed passage, as pdftotext prints it (whitespace normalized)
PASSAGES = {
    "abstract-coverage": ("intervals is not established.", "The five-observable output on data is therefore", "text"),
    "sec-coverage": ("one of the generators of Cmodel .", "7. DISCUSSION AND CONCLUSIONS", "text"),
    "abstract-ibu": ("fixed before the tests were graded.", "The estimator is reproducible", "text"),
    "sec-ibu": ("At the GiBUU hybrid truth, the IBU at five iterations", "No tested level clears both flagged truths.", "text"),
    # Table 1's row, from pdftotext -raw (content order keeps a table row together)
    "table-coverage": ("Like-for-like five-observable coverage test 5D 6.3", "Run-period consistency", "raw"),
}


def load_mod(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_mv(wt):
    spec = importlib.util.spec_from_file_location("mv", wt / NOTE / "make_values_fived16.py")
    mv = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mv)
    return mv


def norm(txt):
    txt = re.sub(r"\f\s*\d+\s*\n", " ", txt)        # a page break and the next page's number
    # pdftotext's end-of-line hyphenation; a break at a compound's own hyphen keeps it (under-covers, five-observable)
    txt = re.sub(r"\b(under|five|two|pseudo|noise|like|for|run|held|well|non)-\n(?=[a-z])", r"\1-", txt)
    txt = re.sub(r"-\n(?=[a-z])", "", txt)
    # pdftotext also drops the hyphen of a compound it rejoins on one line; the source prints only "under-cover..."
    txt = txt.replace("undercover", "under-cover").replace("runperiod", "run-period")
    txt = re.sub(r"\f", " ", txt)
    return re.sub(r"\s+", " ", txt)


def cut(txt, a, b):
    i = txt.find(a)
    if i < 0:
        return None
    if a.endswith("."):
        i += len(a)
    j = txt.find(b, i + 1)
    return txt[i:j].strip() if j > 0 else None


def recut(out):
    """Re-cut passages.json from the saved <case>.txt builds, without rebuilding."""
    res = {}
    for name in sorted(LL5D_CASES.keys() | PRR_CASES.keys()):
        txt = norm((out / f"{name}.txt").read_text())
        rawt = norm((out / f"{name}.raw.txt").read_text())
        res[name] = {"pending_markers": txt.count("[PENDING"), "unresolved": txt.count("??"), "passages": {}}
        for p, (a, b, src) in PASSAGES.items():
            c = cut(rawt if src == "raw" else txt, a, b)
            if c is not None:
                res[name]["passages"][p] = c
    (out / "passages.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")


def main(argv):
    wt, out = Path(argv[1]).resolve(), Path(argv[2]).resolve()
    out.mkdir(parents=True, exist_ok=True)
    mv = load_mv(wt)
    cr = load_mod(Path(__file__).resolve().parent.parent / "check_round.py", "check_round")
    CASES = cases(mv)
    for name, ver in CASES.items():
        for k, v in ver.items():
            g, cls = mv.PENDING[k]
            assert cls is None or v in cls, (name, k, v)
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / NOTE
        shutil.copytree(wt / NOTE, d, ignore=shutil.ignore_patterns("archive", "main_*.pdf", "*.aux", "*.log", "*.fls",
                                                                     "*.fdb_latexmk"))
        (Path(td) / "docs/orchestration").mkdir(parents=True)
        (Path(td) / "docs/orchestration/state").symlink_to(wt / "docs/orchestration/state")
        r = subprocess.run(["latexmk", "-pdf", "-g", "-interaction=nonstopmode", "-halt-on-error", "main_note.tex"],
                           cwd=d, capture_output=True, text=True, errors="replace")
        if r.returncode:
            sys.exit(f"main_note build failed ({r.returncode})")
        head = (d / "values_fived16.tex").read_text().split("\n")
        base = [l for l in head if not re.match(r"\\@namedef\{fv(g|gd|c)@", l)
                and not any(l.startswith(rf"\@namedef{{fv@{k}}}") for k in mv.PENDING)]
        end = base.index(r"\makeatother")
        for name, ver in CASES.items():
            pl = mv.pending_lines(ver)
            (d / "values_fived16.tex").write_text("\n".join(base[:end] + pl + base[end:]))
            for f in d.glob("main_paper.*"):
                if f.suffix != ".tex":
                    f.unlink()
            r = subprocess.run(["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", "main_paper.tex"],
                               cwd=d, capture_output=True, text=True, errors="replace")
            if r.returncode:
                sys.exit(f"{name}: main_paper build failed")
            log = (d / "main_paper.log").read_text(errors="replace")
            if re.search(r"undefined (references|citations)|Reference .* undefined", log):
                sys.exit(f"{name}: undefined references")
            raw = subprocess.run(["pdftotext", "main_paper.pdf", "-"], cwd=d, capture_output=True, text=True,
                                 errors="replace").stdout
            (out / f"{name}.txt").write_text(raw)
            (out / f"{name}.raw.txt").write_text(subprocess.run(["pdftotext", "-raw", "main_paper.pdf", "-"], cwd=d,
                                                                capture_output=True, text=True, errors="replace").stdout)
            bad = cr.printed_class_names(raw, mv)                 # check_round check 8, on every case build
            if bad:
                sys.exit(f"{name}: a class name prints: {bad}")
            txt = norm(raw)
            print(f"{name}: built; {len(txt.split())} words; {txt.count('[PENDING')} pending markers")
    recut(out)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--recut":
        recut(Path(sys.argv[2]).resolve())
    else:
        main(sys.argv)

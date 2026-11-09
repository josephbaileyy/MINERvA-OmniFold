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

LL5D_TUNES = ("g18", "ar23")
LL5D_READ = ("minus2", "all")


def ll5d(campaign, per, abstract, cells=None):
    """per[(tune, reading)] -> class; cells[(tune, reading)] -> stand-in text."""
    v = {"ll5d-campaign": campaign, "ll5d-abstract": abstract}
    for t in LL5D_TUNES:
        for r in LL5D_READ:
            v[f"ll5d-{t}-{r}"] = per.get((t, r), "na")
            v[f"ll5d-{t}-{r}-cells"] = (cells or {}).get((t, r), "[cells R..]")
    return v


def every(cls):
    return {(t, r): cls for t in LL5D_TUNES for r in LL5D_READ}


C1 = "[cells R03, R11]"
C2 = "[cells R06]"
CASES = {
    "cov-both-cover": ll5d("graded", every("covers"), "both-cover"),
    "cov-one-under-cells": ll5d("graded", {("g18", "minus2"): "covers", ("ar23", "minus2"): "under-cells",
                                           ("g18", "all"): "covers", ("ar23", "all"): "under-cells"},
                                "one-under", {("ar23", "minus2"): C1, ("ar23", "all"): C1}),
    "cov-both-under-joint": ll5d("graded", every("under-joint"), "both-under",
                                 {("g18", "minus2"): C2, ("g18", "all"): C2, ("ar23", "minus2"): C1, ("ar23", "all"): C1}),
    "cov-invalid": ll5d("graded", every("invalid"), "invalid"),
    "cov-mixed-primary-covers": ll5d("graded", {("g18", "minus2"): "covers", ("ar23", "minus2"): "covers",
                                                ("g18", "all"): "covers", ("ar23", "all"): "under-cells"},
                                     "both-cover", {("ar23", "all"): C1}),
    "cov-gate-failed": ll5d("gate-failed", {}, "not-graded"),
    "cov-to-joseph": ll5d("to-joseph", {}, "not-graded"),
    "cov-stop": ll5d("stop", {}, "not-graded"),
}


def prr(ibu):
    v = {}
    for t in ("gibuu", "q3"):
        for f in ("F1", "F2", "F3", "F4"):
            v[f"prr-pr1-{f}-{t}"] = "no-effect"
        v[f"prr-pr2a-{t}"] = ibu
        v[f"prr-pr2b-{t}"] = "flat"          # replaced by a bracketed stand-in in the passage (another reading)
        for lab in ("fir", "info", "impl", "obs", "stat", "unattr"):
            # FD-PRR §5.4: "implementation-specific share" holds when PR-2a = IBU retains less; nothing else follows
            v[f"prr-label-{lab}-{t}"] = "holds" if (lab == "impl" and ibu == "less") else "not"
    v["prr-pr3-any"] = "not"
    v["prr-pr3-ibu"] = "not"
    v["prr-pr3-levels"] = "[levels]"
    return v


for _c in ("less", "same", "more"):
    CASES[f"ibu-{_c}"] = prr(_c)

# anchors: fixed text around each changed passage, as pdftotext prints it (whitespace normalized)
PASSAGES = {
    "abstract-coverage": ("A like-for-like five-observable coverage test at the same tunes", "The five-observable output on data is therefore"),
    "sec-coverage": ("or on the ensemble average.", "7. DISCUSSION AND CONCLUSIONS"),
    "abstract-ibu": ("At the GiBUU-like truth, a binned iterative unfolding", "The estimator is reproducible"),
    "sec-ibu": ("At the GiBUU hybrid truth, the IBU at five iterations", "No tested level clears both flagged truths."),
}


def load_mv(wt):
    spec = importlib.util.spec_from_file_location("mv", wt / NOTE / "make_values_fived16.py")
    mv = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mv)
    return mv


def norm(txt):
    # pdftotext's end-of-line hyphenation; a break at a compound's own hyphen keeps it (under-covers, five-observable)
    txt = re.sub(r"\b(under|five|two|pseudo|noise|like|for|run|held|well|non)-\n(?=[a-z])", r"\1-", txt)
    txt = re.sub(r"-\n(?=[a-z])", "", txt)
    # pdftotext also drops the hyphen of a compound it rejoins on one line; the source prints only "under-cover..."
    txt = txt.replace("undercover", "under-cover")
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
    for name in CASES:
        txt = norm((out / f"{name}.txt").read_text())
        res[name] = {"pending_markers": txt.count("[PENDING"), "unresolved": txt.count("??"), "passages": {}}
        for p, (a, b) in PASSAGES.items():
            c = cut(txt, a, b)
            if c is not None:
                res[name]["passages"][p] = c
    (out / "passages.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")


def main(argv):
    wt, out = Path(argv[1]).resolve(), Path(argv[2]).resolve()
    out.mkdir(parents=True, exist_ok=True)
    mv = load_mv(wt)
    for name, ver in CASES.items():
        for k, v in ver.items():
            g, cls = mv.PENDING[k]
            assert cls is None or v in cls, (name, k, v)
    res = {}
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
            txt = norm(raw)
            res[name] = {"pending_markers": txt.count("[PENDING"), "unresolved": txt.count("??"), "passages": {}}
            for p, (a, b) in PASSAGES.items():
                c = cut(txt, a, b)
                if c is not None:
                    res[name]["passages"][p] = c
            print(f"{name}: built; {len(txt.split())} words; passages {sorted(res[name]['passages'])}")
    (out / "passages.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--recut":
        recut(Path(sys.argv[2]).resolve())
    else:
        main(sys.argv)

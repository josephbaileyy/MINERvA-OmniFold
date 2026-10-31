#!/usr/bin/env python3
"""Self-test of the restyle checks, in the direction each one acts (DECLARATION.md §3 item 7).

usage: python3 -I selftest.py [DEPLOY]      (DEPLOY: a checkout holding technote_style.py; default: this repository)
toy_producer.py is run through capture.py, as a real producer would be, into one run directory per case. compare.py
and raster.py must then:
  stay silent on   an identical rerun; the restyle (sizes, fonts, labels, panel layout, panel labels, text added);
                   a different wall time in the report;
  fire on          a one-ulp value change; one series' RGBA changed, and a line's or a scatter's alone; a series left
                   out; a changed input file (check 5); a report value changed alone (check 4); a figure record that
                   --figures does not name; a one-pixel change to a raster (check 2); a text printed at 3.5 pt
                   under textsize.py's 4.0 pt floor (check 7), which must be named. It stays silent on the same
                   text at 5.0 pt.
Exit 0 and print SELF-TEST :: PASS only if every case behaves."""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
DEPLOY = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else HERE.parents[7]
PY = sys.executable


def run(base, name, data, *flags):
    r = base / name
    cap = r / "capture" / "toy"
    (r / "out").mkdir(parents=True)
    p = subprocess.run([PY, "-I", str(HERE / "capture.py"), str(cap), str(DEPLOY), str(HERE / "toy_producer.py"),
                        str(data), str(r / "out" / "toy"), *flags], capture_output=True, text=True)
    if p.returncode:
        sys.exit(f"selftest: the toy failed in case {name}:\n{p.stderr[-2000:]}")
    return r


def compare(b, a, *extra):
    p = subprocess.run([PY, "-I", str(HERE / "compare.py"), str(b), str(a), "--figures", "toy.png",
                        "--strip", f"{b}=RUN", "--strip", f"{a}=RUN", *extra], capture_output=True, text=True)
    return p.returncode, p.stdout


def textsize(run):
    p = subprocess.run([PY, "-I", str(HERE / "textsize.py"), str(run), str(DEPLOY), "--floor", "4.0",
                        "--width", "toy=6.5"], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def compare_recolour(b, a, *extra):
    return compare(b, a, "--recolour", str(TOYREC), "--palette", str(TOYPAL), *extra)


def overlap(run):
    p = subprocess.run([PY, "-I", str(HERE / "overlap.py"), str(run), "--gate"], capture_output=True, text=True)
    return p.returncode, p.stdout


def raster(*args):
    p = subprocess.run([PY, "-I", str(HERE / "raster.py"), *map(str, args)], capture_output=True, text=True)
    return p.returncode, p.stdout


def main():
    ok = True

    def expect(name, rc, out, want_fail, must=""):
        nonlocal ok
        good = (rc != 0) == want_fail and (not must or must in out)
        ok &= good
        print(f"  {'fires ' if want_fail else 'silent'}  {name}: {'ok' if good else 'WRONG'}")
        if not good:
            print("    " + out.strip().replace("\n", "\n    "))

    with tempfile.TemporaryDirectory() as t:
        base = Path(t)
        rng = np.random.default_rng(7)
        data = base / "in.npy"
        np.save(data, rng.uniform(0.8, 1.2, size=(7, 6)))
        data2 = base / "in2.npy"
        np.save(data2, np.load(data) * 1.0)
        changed = base / "in3.npy"
        a3 = np.load(data)
        a3[5, 2] += 0.25
        np.save(changed, a3)

        old = run(base, "old", data)
        cases = {
            "rerun": run(base, "rerun", data),
            "restyle": run(base, "restyle", data, "--style", "restyle-2026-10"),
            "timing": run(base, "timing", data, "--timing", "9.9"),
            "ulp": run(base, "ulp", data, "--ulp"),
            "rgba": run(base, "rgba", data, "--rgba"),
            "line-rgba": run(base, "line-rgba", data, "--line-rgba"),
            "scatter-rgba": run(base, "scatter-rgba", data, "--scatter-rgba"),
            "report-ulp": run(base, "report-ulp", data, "--report-ulp"),
            "drop": run(base, "drop", data, "--drop"),
            "input": run(base, "input", changed),
            "same-input-copy": run(base, "same-input-copy", data2),
            # the toy's 13 in canvas printed at 6.5 in: 7.0 pt drawn prints at 3.5 pt, 10.0 pt at 5.0 pt
            "label-3.5": run(base, "label-3.5", data, "--label-size", "7.0"),
            "label-5.0": run(base, "label-5.0", data, "--label-size", "10.0"),
        }
        global TOYPAL, TOYREC
        TOYPAL, TOYREC = base / "palette.tsv", base / "recolour.tsv"
        TOYPAL.write_text("identity\thex\nthis_work\t#D55E00\n")
        TOYREC.write_text("figure\tbefore_rgb\tidentity\ntoy\t#4C72B0\tthis_work\n")
        am = {n: run(base, n, data, f) for n, f in (("palette", "--palette"), ("palette-wrong", "--palette-wrong"),
                                                      ("hist-ulp", "--hist-ulp"), ("overlap", "--overlap"))}
        am["rebin"] = run(base, "rebin", data, "--palette", "--rebin")  # recoloured as mapped, so only the bins differ
        am["palette-extra"] = run(base, "palette-extra", data, "--palette", "--palette-extra")
        am["palette-ulp"] = run(base, "palette-ulp", data, "--palette", "--ulp")
        am["rebin-ulp"] = run(base, "rebin-ulp", data, "--palette", "--rebin", "--hist-ulp")
        outs = ("--outputs", "out/toy_report.txt")
        expect("identical rerun", *compare(old, cases["rerun"], *outs), False)
        expect("restyle (layout, fonts, labels, panel labels, text)", *compare(old, cases["restyle"], *outs), False)
        expect("a different wall time in the report", *compare(old, cases["timing"], *outs), False)
        expect("one value moved by one ulp", *compare(old, cases["ulp"]), True, "only before")
        expect("one series' RGBA changed", *compare(old, cases["rgba"]), True, "only before")
        expect("a line's RGBA changed alone", *compare(old, cases["line-rgba"]), True, "only before")
        expect("a scatter's RGBA changed alone", *compare(old, cases["scatter-rgba"]), True, "only before")
        expect("a series left out", *compare(old, cases["drop"]), True, "only before")
        expect("a changed report value alone (check 4)", *compare(old, cases["report-ulp"], *outs), True,
               "FAIL output out/toy_report.txt: differs")
        expect("the figure unchanged when only the report is (check 3)", *compare(old, cases["report-ulp"]), False)
        expect("a changed input file (check 5)", *compare(old, cases["input"]), True, "opened files differ")
        rc, out = compare(old, cases["same-input-copy"])
        expect("the same input under another name (check 5 names paths)", rc, out, True, "opened files differ")

        expect("a text printed at 3.5 pt, floor 4.0 (check 7)", *textsize(cases["label-3.5"]), True,
               "3.50 pt  median")
        rc, out = textsize(cases["label-3.5"])
        expect("  ... and the failing text is named", rc, out, True, "smallest 'tiny label'")
        expect("the same text printed at 5.0 pt (check 7)", *textsize(cases["label-5.0"]), False, "TEXTSIZE :: PASS")

        # RESTYLE AMENDMENT 1: the recolour check, the named binning exception and the overlap gate
        expect("recolour: the series recoloured as the table maps it", *compare_recolour(old, am["palette"]), False)
        expect("recolour: the palette colour wrong by one unit", *compare_recolour(old, am["palette-wrong"]), True,
               "the palette and recolour table give")
        expect("recolour: a series the table does not map recoloured", *compare_recolour(old, am["palette-extra"]),
               True, "the palette and recolour table give")
        expect("recolour: a one-ulp value change still fires", *compare_recolour(old, am["palette-ulp"]), True,
               "only before")
        expect("rebin: zero-aligned bins, the figure named", *compare_recolour(old, am["rebin"], "--rebin", "toy.png"),
               False)
        expect("rebin: the same bins change, the figure not named", *compare_recolour(old, am["rebin"]), True,
               "only before")
        expect("rebin: a hist value moved by one ulp, the figure named",
               *compare_recolour(old, am["rebin-ulp"], "--rebin", "toy.png"), True, "only before")
        expect("rebin: a hist value moved by one ulp, plain check", *compare(old, am["hist-ulp"]), True, "only before")
        expect("overlap: a text on the line", *overlap(am["overlap"]), True, "'on the line'")
        expect("overlap: none", *overlap(old), False, "OVERLAP :: PASS")
        import importlib.util
        spec = importlib.util.spec_from_file_location("rs", DEPLOY / "2d-unfolding" / "restyle_2026_10.py")
        rs = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(rs)
        rows = [l.split("\t") for l in (DEPLOY / "docs/orchestration/state/2d-closeout/stageF/methods/fig-restyle-20261031"
                                         / "palette.tsv").read_text().splitlines()[2:]]
        same = {r[0]: r[1].upper() for r in rows} == {k: v.upper() for k, v in rs.PALETTE.items()}
        expect("palette.tsv equals restyle_2026_10.PALETTE", 0 if same else 1,
               "" if same else f"palette.tsv {rows} vs PALETTE {rs.PALETTE}", False)

        pa, pb = old / "out" / "toy.pdf", cases["rerun"] / "out" / "toy.pdf"
        extra = cases["rerun"] / "capture" / "toy" / "toy.pdf.json"
        shutil.copy(cases["rerun"] / "capture" / "toy" / "toy.png.json", extra)
        expect("a figure record that --figures does not name", *compare(old, cases["rerun"]), True,
               "FAIL figure toy.pdf: not named by --figures")
        extra.unlink()
        expect("raster: an identical rerun's PDF", *raster(pa, pb), False)
        expect("raster: the restyled PDF", *raster(pa, cases["restyle"] / "out" / "toy.pdf"), True)
        keep = base / "png"
        raster(pa, pb, "--keep", keep)
        png = sorted((keep / "a").glob("p-*.png"))[0]
        bad = base / "bad.png"
        shutil.copy(png, bad)
        im = np.asarray(Image.open(bad).convert("RGB")).copy()
        im[10, 10] = (im[10, 10] + 1) % 256
        Image.fromarray(im).save(bad)
        expect("raster: one pixel changed", *raster("--png", png, bad), True, "1 differing pixel")
        expect("raster: the same PNG", *raster("--png", png, png), False)
    print("SELF-TEST ::", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

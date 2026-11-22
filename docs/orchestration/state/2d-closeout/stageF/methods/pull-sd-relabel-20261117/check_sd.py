#!/usr/bin/env python3
"""The checks of the note figure's "rms" -> "SD" relabel (README.md section 3), on the three arms of one run.

usage: python3 -I check_sd.py --before DIR --off DIR --after DIR --installed PDF --installed-sha SHA --deploy DIR
                              [--strip OLD=NEW ...] [--old-label 'rms ='] [--new-label 'SD = ']
Each arm DIR holds out/MEFHC_5iter_pull_full.pdf, capture/pull_full/ (capture.py's and boxes.py's records) and
logs/pull_full.log. "before" is the installed figure's producer (fig-restyle-20261031's bound commit db5276148) with
--style restyle-2026-10; "off" is the package's producer with the same argv; "after" adds --sd-label. --deploy is a tree
holding the package's 2d-unfolding/restyle_2026_10.py (textsize.py reads the printed width from it). The restyle's own
tools (raster.py, compare.py, overlap.py, textsize.py) do checks K2, K3 and K7, unchanged.
  K1  the installed figure is the digest given.
  K2  identity: "before" and "off" rasterize at 300 DPI to the installed figure's pixels (raster.py).
  K3  data and log: compare.py, "before" against "after" and against "off": every data artist bit for bit (colours and
      styles included), the step's log byte for byte after --strip and the wall-time filter, the same inputs and digests.
  K4  drawn text: "off" draws the texts "before" draws; "after" draws them too but one, which is "before"'s with the old
      label replaced, once, by the new. The old label occurs once among "before"'s texts.
  K5  layout: "off"'s boxes are "before"'s; "after"'s are "before"'s too, every axes and every text box, except the
      changed text's own extent, which must lie inside its unchanged bbox patch.
  K6  pixels: "before" and "after" differ, and only inside the changed text's bbox patch (2 px margin at 300 DPI); the
      left half of the page, which make_figures.sh crops for paper_validation_residual.pdf, is pixel-equal.
  K7  the restyle's gates on "after": no in-panel text on data (overlap.py --gate), printed text at least 4.0 pt
      (textsize.py --floor 4.0), no raw "_" or "^" in the PDF's text; the PDF's text has the new label, not the old.
  K8  "after"'s page is 864 x 360 pt (make_figures.sh asserts it before the crop).
Prints one line per check and CHECK_SD :: PASS or FAIL; exit 0 only on PASS."""
import argparse
import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parent / "fig-restyle-20261031" / "tools"
F = "MEFHC_5iter_pull_full"
ap = argparse.ArgumentParser()
for k in ("--before", "--off", "--after", "--installed", "--deploy"):
    ap.add_argument(k, type=Path, required=True)
ap.add_argument("--installed-sha", required=True)
ap.add_argument("--strip", action="append", default=[])
ap.add_argument("--old-label", default="rms =")
ap.add_argument("--new-label", default="SD = ")
a = ap.parse_args()
ok = True


def res(name, good, detail=""):
    global ok
    ok &= bool(good)
    print(f"{'PASS' if good else 'FAIL'} {name}{': ' + detail if detail else ''}")


def tool(script, *args):
    p = subprocess.run([sys.executable, "-I", str(TOOLS / script), *map(str, args)], capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).strip()


def pdf(arm):
    return arm / "out" / f"{F}.pdf"


def cap(arm, ext):
    return arm / "capture" / "pull_full" / f"{F}.png.{ext}"


def rows(path, skip=1):
    return path.read_text().splitlines()[skip:]


def boxes(arm):
    out = []
    for line in rows(cap(arm, "boxes.tsv")):
        kind, n, text, *xy = line.split("\t")
        out.append((kind, n, text, tuple(float(v) for v in xy)))
    return out


def render(p, d):
    subprocess.run(["pdftoppm", "-r", "300", "-png", str(p), str(d / "p")], check=True)
    (png,) = sorted(d.glob("p*.png"))
    return np.asarray(Image.open(png).convert("RGB"))


# K1
got = hashlib.sha256(a.installed.read_bytes()).hexdigest()
res("K1 installed figure", got == a.installed_sha, f"{a.installed.name} {got[:12]} (want {a.installed_sha[:12]})")
# K2
for arm in ("before", "off"):
    rc, out = tool("raster.py", a.installed, pdf(getattr(a, arm)))
    res(f"K2 identity {arm}", rc == 0 and "EQUAL" in out, out.splitlines()[-1] if out else f"rc {rc}")
# K3
strip = [x for s in a.strip for x in ("--strip", s)]
for arm in ("after", "off"):
    rc, out = tool("compare.py", a.before, getattr(a, arm), "--figures", f"{F}.png", "--outputs", "logs/pull_full.log",
                   *strip)
    res(f"K3 data, log and inputs: before vs {arm}", rc == 0 and out.splitlines()[-1] == "COMPARE :: PASS",
        " | ".join(out.splitlines()[-4:]))
# K4
tb, to, ta = (rows(cap(getattr(a, k), "textsizes.tsv")) for k in ("before", "off", "after"))
res("K4 text: off draws before's texts", to == tb, f"{len(tb)} texts")
hits = [i for i, r in enumerate(tb) if a.old_label in r]
diff = [i for i in range(max(len(tb), len(ta))) if i >= len(tb) or i >= len(ta) or tb[i] != ta[i]]
want = tb[hits[0]].replace(a.old_label, a.new_label, 1) if len(hits) == 1 else None
res("K4 text: after changes the label alone", len(hits) == 1 and tb[hits[0]].count(a.old_label) == 1
    and len(ta) == len(tb) and diff == hits and ta[hits[0]] == want,
    f"old label in {len(hits)} text(s); differing rows {diff}; after: {ta[diff[0]] if diff and diff[0] < len(ta) else None!r}")
# K5
bb, bo, ba = (boxes(getattr(a, k)) for k in ("before", "off", "after"))
res("K5 layout: off's boxes are before's", bo == bb, f"{len(bb)} rows")
changed = [i for i, (x, y) in enumerate(zip(bb, ba)) if x != y]
box = None
good = len(ba) == len(bb) and changed != []
for i in changed:  # the changed rows: the label's text and its bbox patch, renamed in place
    kind, n, text, xy = ba[i]
    good &= (bb[i][:2] == (kind, n) and kind in ("text", "textbox")
             and bb[i][2].count(a.old_label) == 1 and text == bb[i][2].replace(a.old_label, a.new_label, 1))
    if kind == "textbox":  # the patch keeps its place and size
        good &= xy == bb[i][3]
        box = xy
for i in changed:  # the text's own extent may change, inside the patch
    kind, n, text, xy = ba[i]
    if kind == "text":
        good &= box is not None and box[0] <= xy[0] and box[1] <= xy[1] and xy[2] <= box[2] and xy[3] <= box[3]
good &= [ba[i][0] for i in changed].count("textbox") == 1
res("K5 layout: after moves nothing but the changed text, inside its box", good,
    f"rows changed {changed}; box {None if box is None else tuple(round(v, 4) for v in box)}")
# K6
with tempfile.TemporaryDirectory() as t:
    t = Path(t)
    (t / "b").mkdir()
    (t / "a").mkdir()
    ib, ia = render(pdf(a.before), t / "b"), render(pdf(a.after), t / "a")
if ib.shape != ia.shape or box is None:
    res("K6 pixels", False, f"shapes {ib.shape} {ia.shape}; box {box}")
else:
    h, w = ib.shape[:2]
    ys, xs = np.nonzero(np.any(ib != ia, axis=2))
    x0, x1 = box[0] * w - 2, box[2] * w + 2
    y0, y1 = (1 - box[3]) * h - 2, (1 - box[1]) * h + 2
    inside = (xs >= x0) & (xs <= x1) & (ys >= y0) & (ys <= y1)
    res("K6 pixels: changed only inside the label's box", xs.size > 0 and bool(inside.all()),
        f"{xs.size} differing pixel(s), {int((~inside).sum())} outside x {x0:.0f}-{x1:.0f}, y {y0:.0f}-{y1:.0f} of {w}x{h}")
    res("K6 pixels: the left half is pixel-equal", not np.any(xs < w // 2), f"{int((xs < w // 2).sum())} in the left half")
# K7
rc, out = tool("overlap.py", a.after, "--figures", f"{F}.png", "--gate")
res("K7 overlap gate (after)", rc == 0, out.splitlines()[-1] if out else f"rc {rc}")
rc, out = tool("textsize.py", a.after, a.deploy, "--floor", "4.0")
res("K7 printed text >= 4.0 pt (after)", rc == 0, " | ".join(out.splitlines()[-2:]))
txt = {k: subprocess.run(["pdftotext", str(pdf(getattr(a, k))), "-"], capture_output=True, text=True, check=True).stdout
       for k in ("before", "after")}
raw = [ln for ln in txt["after"].splitlines() if "_" in ln or "^" in ln]
res("K7 no raw _ or ^ in after's PDF text", raw == [], f"{len(raw)} line(s)")
res("K7 after's PDF text has the new label, not the old", a.new_label.strip() in txt["after"]
    and a.old_label.strip() not in txt["after"] and a.old_label.strip() in txt["before"])
# K8
size = subprocess.run(["pdfinfo", str(pdf(a.after))], capture_output=True, text=True, check=True).stdout
size = next((ln.split()[2] + " x " + ln.split()[4] for ln in size.splitlines() if ln.startswith("Page size:")), None)
res("K8 after's page 864 x 360 pt", size == "864 x 360", str(size))
print(f"CHECK_SD :: {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)

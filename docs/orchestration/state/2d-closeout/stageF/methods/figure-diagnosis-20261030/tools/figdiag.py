#!/usr/bin/env python3
"""Figure and table diagnosis (PLAN.md): the item inventory, the crop boxes, the renders and the measured text sizes.

usage: python3 -I figdiag.py items  <worktree> <anchor-dir> <out-dir>   # items.tsv: ours by rule, anchors by caption
       python3 -I figdiag.py crops  <out-dir>                          # crops.tsv (+ crops-override.tsv applied)
       python3 -I figdiag.py render <out-dir> <png-dir>                # colour, greyscale and CVD PNGs, at 300 DPI
       python3 -I figdiag.py measure <out-dir>                         # text-size.tsv: printed glyph-box heights
       python3 -I figdiag.py control <out-dir> <png-dir>               # the planted degraded figure (PLAN.md section 5)
       python3 -I figdiag.py probe <png-dir>                           # the vision probe image and its key
       python3 -I figdiag.py captions <out-dir> <caption-dir>          # each item's caption text, from its crop

The population (PLAN.md section 1):
  - ours: every figure (\\includegraphics) and table environment of paper_body.tex, and of the note's
    sec_results.tex, sec_eavailw.tex and sec_fived16.tex. Each is found by its \\label, whose number and page come
    from the build's .aux file;
  - anchors: every caption that opens with FIG./Fig./TABLE and a number, found from pdftotext -bbox words on each page.

A crop is the caption's block plus the float body beside it. The body is found on the 300 DPI raster of the caption's
column (or the full text width, for a two-column float): from the caption edge, rows are taken while the gap of
all-white rows stays below GAP_PT. A figure's body sits above its caption; a table's sits above or below, as its
source orders \\caption and the tabular (ours) or below (the anchors, revtex). crops-override.tsv replaces a box that
fails visual inspection; every crop is inspected, and the override records why.

Measured text size: pdftotext -bbox word boxes inside the crop and outside the caption block; the height of a word box
is its printed glyph-box height in pt. It is an instrument, applied alike to ours and the anchors, not a font size:
a raster figure has no words, and is reported as such."""
import csv
import hashlib
import html
import os
import re
import subprocess
import sys
from pathlib import Path

DPI = 300
GAP_PT = 9.0     # an all-white band at least this tall ends a float body (\\textfloatsep and \\abovecaptionskip are larger)
PAD_PT = 3.0
RULE_FRAC = 0.4  # an unbroken dark run this long is a horizontal rule (a tabular may be narrower than its column)
HEAD_PT = 45.0   # words ending above this are a page header, never a float
OURS = {"paper": ("main_paper", ["paper_body.tex"]),
        "note": ("main_note", ["sec_results.tex", "sec_eavailw.tex", "sec_fived16.tex"])}
# a caption's opening tokens: revtex sets "FIG. 3." / "FIG. 3:" / "TABLE II." in capitals, where running text says
# "Fig. 3"; the note (article class) sets "Figure 3:" / "Table 3:"
CAP = re.compile(r"^(FIG\.|TABLE)$|^(Figure|Table)$")
NUM = re.compile(r"^([0-9]+|[IVXL]+)[.:]$")


def is_caption(a, b):
    return bool(CAP.match(a) and NUM.match(b) and (a.isupper() or b.endswith(":")))


def sh(*cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, check=True, **kw).stdout


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def words(pdf, page):
    """pdftotext -bbox words of one page: [(x0, y0, x1, y1, text)] in pt, y downward, and the page size."""
    out = sh("pdftotext", "-bbox", "-f", str(page), "-l", str(page), str(pdf), "-")
    m = re.search(r'<page width="([\d.]+)" height="([\d.]+)"', out)
    ws = [(float(a), float(b), float(c), float(d), html.unescape(t)) for a, b, c, d, t in
          re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>', out)]
    return ws, float(m.group(1)), float(m.group(2))


def npages(pdf):
    return int(re.search(r"Pages:\s+(\d+)", sh("pdfinfo", str(pdf))).group(1))


# ---------------------------------------------------------------- items
def env_items(src, name):
    """(kind, label, caption_first) for each figure/table environment of a source, with caption-before-body order."""
    t = src.read_text()
    out = []
    for m in re.finditer(r"\\begin\{(figure|table)\*?\}(.*?)\\end\{\1\*?\}", t, re.S):
        body = m.group(2)
        labels = re.findall(r"\\label\{((?:fig|tab)[^}]*)\}", body)
        if m.group(1) == "figure" and "\\includegraphics" not in body:
            continue
        cap = body.find("\\caption")
        tab = min([i for i in (body.find("\\begin{tabular"), body.find("\\begin{tabularx"), body.find("\\resizebox"))
                   if i >= 0] or [len(body)])
        out.append((m.group(1), labels[0] if labels else "", cap >= 0 and cap < tab, src.name))
    return out


def aux_labels(aux):
    lab = {}
    for m in re.finditer(r"\\newlabel\{([^}]*)\}\{\{([^}]*)\}\{([^}]*)\}", aux.read_text(errors="replace")):
        lab[m.group(1)] = (m.group(2), m.group(3))
    return lab


def cmd_items(wt, adir, out):
    wt, adir, out = Path(wt), Path(adir), Path(out)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    note = wt / "docs" / "analysis-note"
    for doc, (main, srcs) in OURS.items():
        lab = aux_labels(note / f"{main}.aux")
        pdf = note / f"{main}.pdf"
        for s in srcs:
            for kind, label, capfirst, f in env_items(note / s, s):
                num, page = lab.get(label, ("?", "?"))
                rows.append(dict(id=f"{doc}-{kind[:3]}-{num}", set=f"ours-{doc}", kind=kind, number=num, page=page,
                                 body=("below" if capfirst else "above") if kind == "table" else "above",
                                 source=f"{s}:{label}", pdf=str(pdf), pdf_sha256=sha(pdf)))
    for pdf in sorted(adir.glob("*.pdf")):
        slot = {"2504.06857v2": "A", "2002.12496v2": "B", "2205.05084v2": "C"}.get(pdf.stem, pdf.stem)
        seen = set()
        for p in range(1, npages(pdf) + 1):
            ws, _, _ = words(pdf, p)
            for i in range(len(ws) - 1):
                if is_caption(ws[i][4], ws[i + 1][4]):
                    kind = "table" if ws[i][4].upper().startswith("TAB") else "figure"
                    num = ws[i + 1][4][:-1]
                    if (kind, num) in seen:   # a later mention inside running text, not the caption
                        continue
                    # a caption opens a line: nothing to its left on the same baseline within its column
                    left = [w for w in ws if abs(w[3] - ws[i][3]) < 1 and w[2] <= ws[i][0] and ws[i][0] - w[2] < 8]
                    if left:
                        continue
                    seen.add((kind, num))
                    rows.append(dict(id=f"anchor{slot}-{kind[:3]}-{num}", set=f"anchor-{slot}", kind=kind,
                                     number=num, page=str(p), body="above" if kind == "figure" else "below",
                                     source=f"{pdf.name}:p{p}", pdf=str(pdf), pdf_sha256=sha(pdf)))
    cols = ["id", "set", "kind", "number", "page", "body", "source", "pdf", "pdf_sha256"]
    with open(out / "items.tsv", "w", newline="") as f:
        w = csv.DictWriter(f, cols, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"items: {len(rows)} ({sum(r['set'].startswith('ours') for r in rows)} ours) -> {out / 'items.tsv'}")


# ---------------------------------------------------------------- crops
def raster_rows(pdf, page, box):
    """Per-row 'has ink' flags of a page region at DPI (box in pt: x0, y0, x1, y1)."""
    x0, y0, x1, y1 = box
    s = DPI / 72
    ppm = subprocess.run(["pdftoppm", "-r", str(DPI), "-f", str(page), "-l", str(page), "-gray", "-x", str(int(x0 * s)),
                          "-y", str(int(y0 * s)), "-W", str(max(1, int((x1 - x0) * s))), "-H",
                          str(max(1, int((y1 - y0) * s))), str(pdf)], capture_output=True, check=True).stdout
    hdr = re.match(rb"P5\s+(\d+)\s+(\d+)\s+(\d+)\s", ppm)
    w, h = int(hdr.group(1)), int(hdr.group(2))
    data = ppm[hdr.end():]
    ink = [min(data[r * w:(r + 1) * w]) < 200 for r in range(h)]
    rule = [longest_dark_run(data[r * w:(r + 1) * w]) >= RULE_FRAC * w for r in range(h)]
    return ink, rule


def longest_dark_run(row):
    """The longest run of dark pixels in one raster row: a rule is one unbroken run; a line of text never is."""
    best = cur = 0
    for v in row:
        cur = cur + 1 if v < 128 else 0
        best = max(best, cur)
    return best


def body_line(ws, x0, x1):
    """Baselines (y1) of body-text lines inside [x0, x1]: at least 85 % of the width, 8+ words, mostly words of 3+ letters
    (a row of tick labels or an axis title is not one)."""
    lines = {}
    for w in ws:
        if w[0] >= x0 - 2 and w[2] <= x1 + 2:
            lines.setdefault(round(w[3]), []).append(w)
    out = []
    for y, l in lines.items():
        span = max(w[2] for w in l) - min(w[0] for w in l)
        wordy = sum(1 for w in l if re.match(r"^[A-Za-z][a-z]{2,}", w[4]))
        if span >= 0.85 * (x1 - x0) and len(l) >= 8 and wordy >= 0.5 * len(l):
            out.append((min(w[1] for w in l), max(w[3] for w in l)))
    return sorted(out)


def text_lines(ws, x0, x1, y_from):
    """Words in [x0, x1] at or below y_from, grouped into lines by vertical overlap, so that a sub- or superscript
    joins its line: [(top, bottom, median glyph height of the line's full-size words, words)]."""
    sel = sorted((w for w in ws if w[1] >= y_from - 1 and w[0] >= x0 - 2 and w[2] <= x1 + 2), key=lambda w: w[3])
    lines = []
    for w in sel:
        h = w[3] - w[1]
        if lines and w[1] < lines[-1][1] - 0.3 * h:      # overlaps the current line vertically
            t, b, ww = lines[-1]
            lines[-1] = (min(t, w[1]), max(b, w[3]), ww + [w])
        else:
            lines.append((w[1], w[3], [w]))
    out = []
    for t, b, ww in lines:
        hs = sorted(x[3] - x[1] for x in ww)
        big = [h for h in hs if h >= 0.8 * hs[-1]]
        out.append((t, b, big[len(big) // 2], ww))
    return out


def caption_block(ws, start, x0, x1, stop=None):
    """The caption's lines inside its column [x0, x1]: from its first line down while the gap between lines stays below
    one caption line height and each line's glyph height stays within 0.6 pt of the first line's (a caption is set
    smaller than the text around it), and above `stop` (a table's first rule)."""
    ls = text_lines(ws, x0, x1, start[1])
    if not ls:
        return start[1], start[3]
    t0, b0, h0, _ = ls[0]
    yb = b0
    for t, b, h, ww in ls[1:]:
        if t - yb > h0 or (abs(h - h0) > 0.6 and len(ww) >= 3) or (stop is not None and t > stop):
            break
        yb = max(yb, b)
    return start[1], max(yb, start[3])


def cmd_crops(out):
    out = Path(out)
    items = list(csv.DictReader(open(out / "items.tsv"), delimiter="\t"))
    over = {}
    if (out / "crops-override.tsv").exists():
        over = {r["id"]: r for r in csv.DictReader(open(out / "crops-override.tsv"), delimiter="\t")}
    rows = []
    for it in items:
        if it["page"] == "?":
            rows.append(dict(id=it["id"], page="?", x0="", y0="", x1="", y1="", cap_y0="", cap_y1="", how="NO-PAGE"))
            continue
        pdf, p = it["pdf"], int(it["page"])
        ws, pw, ph = words(pdf, p)
        key = {"figure": ("FIG", "Figure"), "table": ("TABLE", "Table")}[it["kind"]]
        start = None
        for i in range(len(ws) - 1):
            if ws[i][4].rstrip(".") in key and is_caption(ws[i][4], ws[i + 1][4]) \
                    and ws[i + 1][4][:-1] == it["number"]:
                start = ws[i]
                break
        if start is None:
            rows.append(dict(id=it["id"], page=p, x0="", y0="", x1="", y1="", cap_y0="", cap_y1="", how="NO-CAPTION"))
            continue
        tx0 = min(w[0] for w in ws if w[1] > ph * 0.05)
        tx1 = max(w[2] for w in ws if w[1] > ph * 0.05)
        mid = (tx0 + tx1) / 2
        cx0 = start[0]
        # the caption's column: follow its first line rightwards while the word gaps stay below a column gutter
        first = sorted((w for w in ws if abs(w[3] - start[3]) < 1 and w[0] >= cx0 - 1), key=lambda w: w[0])
        run_end = first[0][2]
        for w in first[1:]:
            if w[0] - run_end > 10:
                break
            run_end = w[2]
        if it["set"] == "ours-note" or cx0 < mid - 20 and run_end > mid + 20:   # the note is one-column
            x0, x1 = tx0, tx1
        elif cx0 < mid:
            x0, x1 = tx0, mid - 2
        else:
            x0, x1 = mid + 2, tx1
        s = 72 / DPI
        first_rule = None
        if it["kind"] == "table" and it["body"] == "below":
            _, rule = raster_rows(pdf, p, (x0, start[3], x1, ph))
            first_rule = next((start[3] + y * s for y in range(len(rule)) if rule[y]), None)
        cy0, cy1 = caption_block(ws, start, x0, x1, first_rule)
        if it["body"] == "above":
            above = [ln for ln in body_line(ws, x0, x1) if ln[1] < cy0 - 1]
            head = [w[3] for w in ws if w[3] < HEAD_PT]   # the running head or page number (revtex prints it on top)
            lim = above[-1][1] + 1 if above else (max(head) + 1 if head else 0)
            # another float's caption above, in this column: the body starts below its last line
            for k in range(len(ws) - 1):
                o = ws[k]
                if o is not start and is_caption(o[4], ws[k + 1][4]) and o[3] < cy0 - 1 and o[0] >= x0 - 2 \
                        and o[0] <= x1:
                    lim = max(lim, caption_block(ws, o, x0, x1)[1] + 1)
            # the rest of the paragraph that the last body line belongs to (its short last line)
            lh = start[3] - start[1]
            for ln in sorted({(round(w[1], 1), round(w[3], 1)) for w in ws
                              if w[1] > lim - 0.5 and w[3] < cy0 - 1 and w[0] >= x0 - 2 and w[2] <= x1 + 2}):
                para = [w for w in ws if abs(w[3] - ln[1]) < 0.6 and w[0] < x0 + 3]
                if ln[0] - lim < 1.0 * lh and para:
                    lim = ln[1] + 1
                else:
                    break
            rr, _ = raster_rows(pdf, p, (x0, lim, x1, cy0 - 1))
            top = next((y for y in range(len(rr)) if rr[y]), None)
            y0, y1 = (lim + top * s if top is not None else cy0), cy1
        else:
            nxt = [o[1] for k, o in enumerate(ws[:-1]) if is_caption(o[4], ws[k + 1][4]) and o[1] > cy1 + 1
                   and x0 - 2 <= o[0] <= x1]   # the next float's caption below, in this column, ends this body
            rr, rule = raster_rows(pdf, p, (x0, cy1 + 1, x1, min(nxt) - 1 if nxt else ph))
            gap, bot, y, seen_ink, last_rule = 0, None, 0, False, None
            # take rows until a 2 GAP_PT white band; the body ends at the last rule seen (a tabular's bottom rule),
            # or, for a table without rules, at the last inked row
            while y < len(rr):
                if rr[y]:
                    bot, gap, seen_ink = y, 0, True
                    if rule[y]:
                        last_rule = y
                elif seen_ink:
                    gap += 1
                    if gap * s >= 2 * GAP_PT:
                        break
                y += 1
            end = last_rule if last_rule is not None else bot
            y0, y1 = cy0, cy1 + 1 + (end * s if end is not None else 0)
        how = "auto"
        if it["id"] in over:
            o = over[it["id"]]
            x0, y0, x1, y1 = (float(o[k]) for k in ("x0", "y0", "x1", "y1"))
            how = "override: " + o["why"]
        rows.append(dict(id=it["id"], page=p, x0=f"{max(0, x0 - PAD_PT):.1f}", y0=f"{max(0, y0 - PAD_PT):.1f}",
                         x1=f"{min(pw, x1 + PAD_PT):.1f}", y1=f"{min(ph, y1 + PAD_PT):.1f}", cap_y0=f"{cy0:.1f}",
                         cap_y1=f"{cy1:.1f}", how=how))
    cols = ["id", "page", "x0", "y0", "x1", "y1", "cap_y0", "cap_y1", "how"]
    with open(out / "crops.tsv", "w", newline="") as f:
        w = csv.DictWriter(f, cols, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    bad = [r["id"] for r in rows if r["how"].startswith("NO-")]
    print(f"crops: {len(rows)}, without a box: {len(bad)} {bad}")


# ---------------------------------------------------------------- render
def crop_png(pdf, page, box, dst):
    x0, y0, x1, y1 = box
    s = DPI / 72
    stem = str(dst)[:-4]
    sh("pdftoppm", "-r", str(DPI), "-f", str(page), "-l", str(page), "-x", str(int(x0 * s)), "-y", str(int(y0 * s)),
       "-W", str(int((x1 - x0) * s)), "-H", str(int((y1 - y0) * s)), "-png", "-singlefile", str(pdf), stem)


def cmd_render(out, pngdir):
    out, pngdir = Path(out), Path(pngdir)
    pngdir.mkdir(parents=True, exist_ok=True)
    items = {r["id"]: r for r in csv.DictReader(open(out / "items.tsv"), delimiter="\t")}
    crops = [r for r in csv.DictReader(open(out / "crops.tsv"), delimiter="\t") if r["x0"]]
    cvd = None
    try:
        if os.environ.get("FIGDIAG_PYLIB"):  # a scratch --target install of colorspacious (kept out of git)
            sys.path.insert(0, os.environ["FIGDIAG_PYLIB"])
        from colorspacious import cspace_convert  # Machado et al. (2009) CVD model, as colorspacious implements it
        import numpy as np
        cvd = (cspace_convert, np)
    except ImportError:
        print("  colorspacious not importable: no CVD renders (PLAN.md section 2: a cited implementation or none)")
    rows = []
    for c in crops:
        it = items[c["id"]]
        box = tuple(float(c[k]) for k in ("x0", "y0", "x1", "y1"))
        col = pngdir / f"{c['id']}.png"
        crop_png(it["pdf"], int(c["page"]), box, col)
        grey = pngdir / f"{c['id']}.grey.png"
        sh("magick", str(col), "-colorspace", "Gray", str(grey))
        outs = [col, grey]
        if cvd:
            outs.append(cvd_png(col, pngdir / f"{c['id']}.deuteranopia.png", *cvd))
        for p in outs:
            rows.append(dict(id=c["id"], variant=p.name.split(".")[1] if p.name.count(".") > 1 else "colour",
                             png=p.name, png_sha256=sha(p)))
    with open(out / "renders.tsv", "w", newline="") as f:
        w = csv.DictWriter(f, ["id", "variant", "png", "png_sha256"], delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"renders: {len(rows)} PNGs for {len(crops)} items -> {pngdir}")


def cvd_png(src, dst, cspace_convert, np):
    ppm = subprocess.run(["magick", str(src), "-depth", "8", "rgb:-"], capture_output=True, check=True).stdout
    w, h = (int(v) for v in sh("magick", "identify", "-format", "%w %h", str(src)).split())
    a = np.frombuffer(ppm, dtype=np.uint8).reshape(h, w, 3) / 255.0
    sim = cspace_convert(a, {"name": "sRGB1+CVD", "cvd_type": "deuteranomaly", "severity": 100}, "sRGB1")
    b = (np.clip(sim, 0, 1) * 255).astype(np.uint8).tobytes()
    subprocess.run(["magick", "-size", f"{w}x{h}", "-depth", "8", "rgb:-", str(dst)], input=b, check=True)
    return dst


# ---------------------------------------------------------------- measure
def cmd_measure(out):
    out = Path(out)
    items = {r["id"]: r for r in csv.DictReader(open(out / "items.tsv"), delimiter="\t")}
    rows = []
    for c in csv.DictReader(open(out / "crops.tsv"), delimiter="\t"):
        if not c["x0"]:
            continue
        it = items[c["id"]]
        ws, _, _ = words(it["pdf"], int(c["page"]))
        x0, y0, x1, y1, cy0, cy1 = (float(c[k]) for k in ("x0", "y0", "x1", "y1", "cap_y0", "cap_y1"))
        hs = sorted(round(w[3] - w[1], 2) for w in ws if x0 <= w[0] and w[2] <= x1 and y0 <= w[1] and w[3] <= y1
                    and not (cy0 - 1 <= w[1] and w[3] <= cy1 + 1))
        if not hs:
            rows.append(dict(id=c["id"], words=0, min_pt="", p10_pt="", median_pt="", note="no text words (raster?)"))
            continue
        rows.append(dict(id=c["id"], words=len(hs), min_pt=f"{hs[0]:.2f}", p10_pt=f"{hs[len(hs) // 10]:.2f}",
                         median_pt=f"{hs[len(hs) // 2]:.2f}", note=""))
    with open(out / "text-size.tsv", "w", newline="") as f:
        w = csv.DictWriter(f, ["id", "words", "min_pt", "p10_pt", "median_pt", "note"], delimiter="\t",
                           lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"text sizes: {len(rows)} items -> {out / 'text-size.tsv'}")


# ---------------------------------------------------------------- control and probe
CONTROL_SRC = "paper-fig-3"   # paper_fig_deformation (PLAN.md section 5), checked by name below


def cmd_control(out, pngdir):
    out, pngdir = Path(out), Path(pngdir)
    items = {r["id"]: r for r in csv.DictReader(open(out / "items.tsv"), delimiter="\t")}
    assert items[CONTROL_SRC]["source"].endswith("fig:deformation"), items[CONTROL_SRC]["source"]
    c = next(r for r in csv.DictReader(open(out / "crops.tsv"), delimiter="\t") if r["id"] == CONTROL_SRC)
    s = DPI / 72
    src = pngdir / f"{CONTROL_SRC}.png"
    body_h = int((float(c["cap_y0"]) - float(c["y0"])) * s)
    w = int(sh("magick", "identify", "-format", "%w", str(src)))
    tmp = pngdir / "_ctl_body.png"
    # the body only: scaled to 50 % in the same box (every font and line weight halved), grey levels mapped to a
    # saturated red-to-green ramp; the caption below is left as printed
    sh("magick", str(src), "-crop", f"{w}x{body_h}+0+0", "+repage", "-resize", "50%", "-colorspace", "Gray",
       "(", "-size", "1x256", "gradient:#ff0000-#00ff00", ")", "-clut", "-background", "white", "-gravity", "center",
       "-extent", f"{w}x{body_h}", str(tmp))
    cap = pngdir / "_ctl_cap.png"
    sh("magick", str(src), "-crop", f"{w}x10000+0+{body_h}", "+repage", str(cap))
    dst = pngdir / "ctl-x.png"
    sh("magick", str(tmp), str(cap), "-append", str(dst))
    sh("magick", str(dst), "-colorspace", "Gray", str(pngdir / "ctl-x.grey.png"))
    try:
        if os.environ.get("FIGDIAG_PYLIB"):
            sys.path.insert(0, os.environ["FIGDIAG_PYLIB"])
        from colorspacious import cspace_convert
        import numpy as np
        cvd_png(dst, pngdir / "ctl-x.deuteranopia.png", cspace_convert, np)
    except ImportError:
        pass
    tmp.unlink()
    cap.unlink()
    print(f"control: {dst} sha256 {sha(dst)[:16]}")


def cmd_captions(out, capdir):
    out, capdir = Path(out), Path(capdir)
    capdir.mkdir(parents=True, exist_ok=True)
    items = {r["id"]: r for r in csv.DictReader(open(out / "items.tsv"), delimiter="\t")}
    n = 0
    for c in csv.DictReader(open(out / "crops.tsv"), delimiter="\t"):
        if not c["x0"]:
            continue
        x0, x1, cy0, cy1 = (float(c[k]) for k in ("x0", "x1", "cap_y0", "cap_y1"))
        t = sh("pdftotext", "-f", c["page"], "-l", c["page"], "-x", str(int(x0)), "-y", str(int(cy0) - 1), "-W",
               str(int(x1 - x0)), "-H", str(int(cy1 - cy0) + 2), items[c["id"]]["pdf"], "-")
        (capdir / f"{c['id']}.txt").write_text(re.sub(r"\s+", " ", t).strip() + "\n")
        n += 1
    print(f"captions: {n} -> {capdir}")


def cmd_probe(pngdir):
    import secrets
    pngdir = Path(pngdir)
    pngdir.mkdir(parents=True, exist_ok=True)
    n = f"{secrets.randbelow(90_000_000) + 10_000_000}"
    dst = pngdir / "probe.png"
    sh("magick", "-size", "1200x800", "xc:white", "-stroke", "black", "-strokewidth", "3", "-draw",
       "line 100,700 1150,700", "-draw", "line 100,700 100,80", "-fill", "none", "-stroke", "#1f77b4", "-draw",
       "polyline 100,650 300,520 500,560 700,300 900,350 1100,150", "-stroke", "none", "-fill", "black",
       "-pointsize", "40", "-annotate", "+380+760", "energy (GeV)", "-pointsize", "64", "-annotate", "+520+260", n,
       str(dst))
    (pngdir / "probe.key").write_text(n + "\n")
    print(f"probe: {dst} (key in probe.key, never shown to a rater)")


if __name__ == "__main__":
    c, a = sys.argv[1], sys.argv[2:]
    {"items": cmd_items, "crops": cmd_crops, "render": cmd_render, "measure": cmd_measure, "control": cmd_control,
     "probe": cmd_probe, "captions": cmd_captions}[c](*a)

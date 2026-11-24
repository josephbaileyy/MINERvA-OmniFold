"""Extract cell values of Figs. 3, 4, 5 of arXiv:2106.16210 from the PDF vector graphics.

Usage:  python3 -I extract.py <paper.pdf> <outdir>

Reads the page content streams directly (pdfops.py, stdlib only), so the cell
colours are the exact DeviceRGB operands written by ROOT.  Writes fig3.csv,
fig4.csv, fig5.csv and fig{3,4,5}_overlay.png into <outdir> and prints a summary.
"""
import csv
import math
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pdfops import interpret, page_content  # noqa: E402

PZ = [1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 7, 8, 9, 10, 15, 20, 40, 60]
PT = [0, .07, .15, .25, .33, .40, .47, .55, .70, .85, 1.00, 1.25, 1.50, 2.50, 4.50]

# region = page-space bbox (x0, y0, x1, y1) containing one figure incl. labels
FIGS = {
    'fig3': dict(page=5, region=(320, 545, 560, 745), xedges=PZ, yedges=PZ,
                 cols=('true_bin', 'reco_bin')),
    'fig4': dict(page=5, region=(320, 220, 560, 420), xedges=PT, yedges=PT,
                 cols=('true_bin', 'reco_bin')),
    'fig5': dict(page=6, region=(55, 545, 300, 745), xedges=PZ, yedges=PT,
                 cols=('ipt', 'ipz')),
}
PDFTOPPM = '/opt/homebrew/bin/pdftoppm'
DPI = 1600


def inside(r, box, tol=0.0):
    return (r[0] >= box[0] - tol and r[2] <= box[2] + tol and
            r[1] >= box[1] - tol and r[3] <= box[3] + tol)


def fit_line(pos, val):
    n = len(pos)
    mp, mv = sum(pos) / n, sum(val) / n
    b = sum((p - mp) * (v - mv) for p, v in zip(pos, val)) / sum((p - mp) ** 2 for p in pos)
    a = mv - b * mp
    res = max(abs(a + b * p - v) for p, v in zip(pos, val))
    return a, b, res


def dedupe(vals, tol=0.01):
    out = []
    for v in sorted(vals):
        if not out or abs(v - out[-1]) > tol:
            out.append(v)
    return out


def numeric_labels(texts):
    out = []
    for x, y, s, fs in texts:
        parts = [p.strip() for p in s.split('|')]
        try:
            vals = [float(p) for p in parts]
        except ValueError:
            continue
        out.append((x, y, vals))
    return out


def calibrate(rects, lines, texts, region):
    R = [r for r in rects if inside(r, region)]
    L = [l for l in lines if all(region[0] <= p[0] <= region[2] and region[1] <= p[1] <= region[3]
                                 for p in l[0])]
    T = [t for t in texts if region[0] <= t[0] <= region[2] and region[1] <= t[1] <= region[3]]
    # frame = the white rectangle that is the bounding box of all colour cells
    white = [r for r in R if r[4][1] == (b'1', b'1', b'1')]
    pad = max(white, key=lambda r: (r[2] - r[0]) * (r[3] - r[1]))
    frames = [r for r in white if r is not pad and (r[2] - r[0]) < (pad[2] - pad[0])]
    frame = max(frames, key=lambda r: (r[2] - r[0]) * (r[3] - r[1]))
    fx0, fy0, fx1, fy1 = frame[:4]
    coloured = [r for r in R if r[4][1] != (b'1', b'1', b'1') or
                (inside(r, frame, 1e-3) and abs((r[2] - r[0]) - (fx1 - fx0)) > 1e-3)]
    cells = [r for r in coloured if inside(r, frame, 1e-3)]
    palette = sorted([r for r in coloured if r[0] > fx1 + 0.5], key=lambda r: r[1])
    assert len(cells) + len(palette) == len(coloured), 'unclassified rectangles'
    px1 = max(r[2] for r in palette)
    segs = [l[0] for l in L if len(l[0]) == 2]
    vert = [s for s in segs if abs(s[0][0] - s[1][0]) < 1e-3]
    hor = [s for s in segs if abs(s[0][1] - s[1][1]) < 1e-3]
    vlen = lambda s: abs(s[0][1] - s[1][1])
    hlen = lambda s: abs(s[0][0] - s[1][0])
    # major ticks: the longer of the two tick lengths, starting on the axis line
    xt = [s for s in vert if abs(min(s[0][1], s[1][1]) - fy0) < 1e-3 and vlen(s) < 20]
    xmaj = dedupe([s[0][0] for s in xt if vlen(s) > 0.75 * max(map(vlen, xt))])
    yt = [s for s in hor if abs(min(s[0][0], s[1][0]) - fx0) < 1e-3 and hlen(s) < 20]
    ymaj = dedupe([s[0][1] for s in yt if hlen(s) > 0.75 * max(map(hlen, yt))])
    zt = [s for s in hor if abs(max(s[0][0], s[1][0]) - px1) < 1e-3 and hlen(s) < 20]
    zmaj = dedupe([s[0][1] for s in zt])
    lab = numeric_labels(T)
    xlab = [v for x, y, vs in lab if fy0 - 15 < y < fy0 - 5 and fx0 - 20 < x < fx1 for v in vs]
    ylab = sorted([(y, vs[0]) for x, y, vs in lab if x < fx0 and fy0 - 5 < y < fy1 + 5])
    zlab = sorted([(y, vs[0]) for x, y, vs in lab if x > px1 and fy0 - 10 < y < fy1 + 5])
    ylab = [v for _, v in ylab]
    zlab = [v for _, v in zlab]
    assert len(xlab) == len(xmaj), (xlab, xmaj)
    assert len(ylab) == len(ymaj), (ylab, ymaj)
    assert len(zlab) == len(zmaj), (zlab, zmaj)
    cal = {'x': fit_line(xmaj, xlab), 'y': fit_line(ymaj, ylab), 'z': fit_line(zmaj, zlab)}
    return dict(frame=frame, cells=cells, palette=palette, cal=cal,
                ticks=dict(x=list(zip(xmaj, xlab)), y=list(zip(ymaj, ylab)), z=list(zip(zmaj, zlab))))


def to255(rgb):
    return tuple(float(c) * 255.0 for c in rgb)


def dist(a, b):
    return math.sqrt(sum((p - q) ** 2 for p, q in zip(a, b)))


def nearest_edge(v, edges):
    i = min(range(len(edges)), key=lambda k: abs(edges[k] - v))
    return i, v - edges[i]


def build_palette(cal, palette):
    a, b, _ = cal['z']
    steps = []
    for r in palette:
        v0, v1 = a + b * r[1], a + b * r[3]
        steps.append(dict(rgb=r[4][1], c=to255(r[4][1]), v0=v0, v1=v1, v=(v0 + v1) / 2))
    vbot, vtop = steps[0]['v0'], steps[-1]['v1']
    half = (vtop - vbot) / len(steps) / 2
    return steps, half


def match(rgb, steps, half):
    exact = [k for k, s in enumerate(steps) if s['rgb'] == rgb]
    if exact:
        k = exact[0]
        return steps[k]['v'], half, 0.0, k
    c = to255(rgb)
    k = min(range(len(steps)), key=lambda j: dist(c, steps[j]['c']))
    best = None
    for j in (k - 1, k + 1):
        if not 0 <= j < len(steps):
            continue
        p, q = steps[k]['c'], steps[j]['c']
        d = [qq - pp for pp, qq in zip(p, q)]
        dd = sum(x * x for x in d)
        t = max(0.0, min(1.0, sum((cc - pp) * x for cc, pp, x in zip(c, p, d)) / dd)) if dd else 0.0
        proj = [pp + t * x for pp, x in zip(p, d)]
        resid = dist(c, proj)
        if best is None or resid < best[1]:
            v = steps[k]['v'] + t * (steps[j]['v'] - steps[k]['v'])
            dvdc = abs(steps[j]['v'] - steps[k]['v']) / math.sqrt(dd) if dd else 0.0
            best = (v, resid, dvdc)
    v, resid, dvdc = best
    return v, max(half, resid * dvdc), resid, k


def render(pdf, page, region, dpi, out_png):
    s = dpi / 72.0
    x, y = int(region[0] * s), int((792 - region[3]) * s)
    w, h = int((region[2] - region[0]) * s), int((region[3] - region[1]) * s)
    base = out_png[:-4]
    subprocess.run([PDFTOPPM, '-png', '-r', str(dpi), '-f', str(page), '-l', str(page),
                    '-x', str(x), '-y', str(y), '-W', str(w), '-H', str(h), '-singlefile',
                    pdf, base], check=True)
    return x, y, s


def main(pdf, outdir):
    from PIL import Image, ImageDraw, ImageFont
    os.makedirs(outdir, exist_ok=True)
    cache = {}
    summary = {}
    for name, F in FIGS.items():
        if F['page'] not in cache:
            cache[F['page']] = interpret(page_content(pdf, F['page']))
        rects, lines, texts = cache[F['page']]
        C = calibrate(rects, lines, texts, F['region'])
        steps, half = build_palette(C['cal'], C['palette'])
        ax, bx, rx = C['cal']['x']
        ay, by, ry = C['cal']['y']
        xe, ye = F['xedges'], F['yedges']
        ny, nx = len(ye) - 1, len(xe) - 1
        grid = {}
        edge_res_pt = 0.0
        meas_x = [[] for _ in xe]
        meas_y = [[] for _ in ye]
        for r in C['cells']:
            vals = []
            for v, edges, sl, meas in ((ax + bx * r[0], xe, bx, meas_x), (ax + bx * r[2], xe, bx, meas_x),
                                       (ay + by * r[1], ye, by, meas_y), (ay + by * r[3], ye, by, meas_y)):
                i, d = nearest_edge(v, edges)
                edge_res_pt = max(edge_res_pt, abs(d / sl))
                meas[i].append(v)
                vals.append(i)
            ix0, ix1, iy0, iy1 = vals
            assert ix1 == ix0 + 1 and iy1 == iy0 + 1, ('cell spans != 1 bin', r)
            key = (iy0, ix0)
            assert key not in grid or grid[key][0] == r[4][1], ('conflicting duplicate cell', key)
            v, sig, res, k = match(r[4][1], steps, half)
            grid[key] = (r[4][1], v, sig, res, k, r)
        rows = []
        for iy in range(ny):
            for ix in range(nx):
                if (iy, ix) in grid:
                    rgb, v, sig, res, k, r = grid[(iy, ix)]
                    rows.append((iy, ix, v, sig, ' '.join(c.decode() for c in rgb), res, k))
                else:
                    rows.append((iy, ix, 0.0, 0.0, 'undrawn', None, None))
        with open(os.path.join(outdir, name + '.csv'), 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow([F['cols'][0], F['cols'][1], 'value', 'sigma', 'rgb', 'match_residual'])
            for iy, ix, v, sig, rgb, res, k in rows:
                w.writerow([iy, ix, '%.5f' % v, '%.5f' % sig, rgb, 'NA' if res is None else '%.4f' % res])

        # raster cross-check: pixels inside each bin, located from the axis
        # calibration and nominal bin edges (not from the rectangle), must have the
        # rectangle's colour.  Five probe points.  Black axis lines and tick marks
        # overlay the edge cells, so a probe that lands on pure black is ignored;
        # a cell fails if any probe shows another colour, or no probe matches.
        png = os.path.join(outdir, name + '_overlay.png')
        x0px, y0px, s = render(pdf, F['page'], F['region'], DPI, png)
        img = Image.open(png).convert('RGB')
        pix = img.load()
        topx = lambda X, Y: (X * s - x0px, (792 - Y) * s - y0px)
        raster_bad = []
        probes = ((0.5, 0.5), (0.37, 0.43), (0.63, 0.57), (0.43, 0.63), (0.57, 0.37))
        for iy, ix, v, sig, rgb, res, k in rows:
            want = (255, 255, 255) if rgb == 'undrawn' else tuple(round(c) for c in to255(rgb.split()))
            got = []
            for fx, fy in probes:
                X = (xe[ix] + fx * (xe[ix + 1] - xe[ix]) - ax) / bx
                Y = (ye[iy] + fy * (ye[iy + 1] - ye[iy]) - ay) / by
                got.append(pix[topx(X, Y)])
            ok = [max(abs(a - b) for a, b in zip(p, want)) <= 2 for p in got]
            other = [p for p, o in zip(got, ok) if not o and p != (0, 0, 0)]
            if other or not any(ok):
                raster_bad.append((iy, ix, got, want))
        # overlay: value x1000 as integer text in each cell
        draw = ImageDraw.Draw(img)
        for iy, ix, v, sig, rgb, res, k in rows:
            Xa, Xb = [(e - ax) / bx for e in (xe[ix], xe[ix + 1])]
            Ya, Yb = [(e - ay) / by for e in (ye[iy], ye[iy + 1])]
            pa, pb = topx(Xa, Yb), topx(Xb, Ya)
            wpx, hpx = pb[0] - pa[0], pb[1] - pa[1]
            txt = '-' if rgb == 'undrawn' else '%d' % round(v * 1000)
            fs = max(6, int(min(hpx * 0.7, wpx / max(len(txt), 2) * 1.6, 60)))
            font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', fs)
            bg = (255, 255, 255) if rgb == 'undrawn' else to255(rgb.split())
            lum = 0.299 * bg[0] + 0.587 * bg[1] + 0.114 * bg[2]
            draw.text(((pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2), txt, anchor='mm', font=font,
                      fill=(0, 0, 0) if lum > 128 else (255, 255, 255))
        img.save(png)

        drawn = [r for r in rows if r[4] != 'undrawn']
        sig = sorted(r[3] for r in drawn)
        res_nonzero = [r for r in drawn if r[5] > 0]
        info = dict(ncells_drawn=len(drawn), ngrid=len(rows), nundrawn=len(rows) - len(drawn),
                    npalette=len(steps), half_step=half,
                    sigma_median=sig[len(sig) // 2] if len(sig) % 2 else (sig[len(sig) // 2 - 1] + sig[len(sig) // 2]) / 2,
                    sigma_max=sig[-1], n_inexact=len(res_nonzero),
                    max_residual=max([r[5] for r in drawn] or [0]),
                    cal_res=(rx, ry, C['cal']['z'][2]), edge_res_pt=edge_res_pt,
                    raster_bad=raster_bad,
                    meas_x=[sum(m) / len(m) if m else None for m in meas_x],
                    meas_y=[sum(m) / len(m) if m else None for m in meas_y],
                    pal_range=(steps[0]['v0'], steps[-1]['v1']),
                    pal_vs_index=max(abs(s_['v'] - (k + 0.5) / len(steps)) for k, s_ in enumerate(steps)),
                    nbox0=sum(1 for r in drawn if r[6] == 0),
                    ntop=sum(1 for r in drawn if r[6] == len(steps) - 1))
        if name in ('fig3', 'fig4'):
            sums = []
            for iy in range(ny):
                rr = [r for r in rows if r[0] == iy]
                lo = sum(r[2] - r[3] for r in rr)
                hi = sum(r[2] + r[3] for r in rr)
                sums.append((sum(r[2] for r in rr), lo, hi))
            info['row_sums'] = sums
        summary[name] = info

    for name, I in summary.items():
        print('==', name)
        print('  cells drawn %d of %d grid (undrawn %d); palette steps %d (half-step %.5f)' % (
            I['ncells_drawn'], I['ngrid'], I['nundrawn'], I['npalette'], I['half_step']))
        print('  palette value range %.5f..%.5f; max |box centre - (k+0.5)/N| = %.5f' % (
            I['pal_range'] + (I['pal_vs_index'],)))
        print('  sigma median %.5f max %.5f; inexact colour matches %d, max residual %.4f' % (
            I['sigma_median'], I['sigma_max'], I['n_inexact'], I['max_residual']))
        print('  cells in lowest palette box %d, in top box %d' % (I['nbox0'], I['ntop']))
        print('  axis fit max residual x %.2e y %.2e z %.2e; worst cell-edge offset from nominal edge %.3f pt' % (
            I['cal_res'] + (I['edge_res_pt'],)))
        print('  measured x edges', ['%.4f' % v if v is not None else None for v in I['meas_x']])
        print('  measured y edges', ['%.4f' % v if v is not None else None for v in I['meas_y']])
        print('  raster centre-pixel mismatches: %d' % len(I['raster_bad']), I['raster_bad'][:5])
        if 'row_sums' in I:
            for iy, (s_, lo, hi) in enumerate(I['row_sums']):
                print('  row %2d sum %.4f  [%.4f, %.4f]' % (iy, s_, lo, hi))
            ss = [x[0] for x in I['row_sums']]
            print('  row-sum range %.4f .. %.4f' % (min(ss), max(ss)))
    return summary


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

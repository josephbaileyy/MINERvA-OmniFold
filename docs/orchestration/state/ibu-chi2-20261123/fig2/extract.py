#!/usr/bin/env python3
"""Extract Figure 2 of arXiv 2106.16210 (page 4) from its vector graphics.

Run:  python3 -I extract.py <paper.pdf> <workdir>
Produces in <workdir>: p4.svg, p4bbox.html, p4-04.png (raster), fig2_cells.csv,
fig2_points.csv (per-panel raw measurements), overlay_top.png, overlay_bot.png,
summary.json.

Geometry facts used (all measured from the SVG, see report.md):
- panel frames are the 30 closed black rectangles ~112 x 60 pt;
- y axis per panel: the two major left-axis ticks are 0 and 5;
- data markers are tiny filled black circles at the point centre; the error bar is
  the 1.344-pt-wide black vertical stroke through the centre (caps drawn as
  horizontal strokes of the same width);
- the red line (Tune v1) is a polyline whose vertices sit at bin centres
  (no flat steps exist in this figure); bins with no vertex are absent;
- bin x positions: the union of vertex/marker x offsets (relative to the frame
  left edge) over the panels of a block forms exactly 16 (top) / 14 (bottom)
  clusters, assigned to bins in left-to-right order.
"""
import csv, json, re, subprocess, sys
from collections import defaultdict

PDF, WD = sys.argv[1], sys.argv[2].rstrip('/')
PT = [0, .07, .15, .25, .33, .40, .47, .55, .70, .85, 1.00, 1.25, 1.50, 2.50, 4.50]
PZ = [1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 7, 8, 9, 10, 15, 20, 40, 60]
NPT, NPZ = len(PT) - 1, len(PZ) - 1
BIN = '/opt/homebrew/bin/'

subprocess.run([BIN + 'pdftocairo', '-svg', '-f', '4', '-l', '4', PDF, f'{WD}/p4.svg'], check=True)
subprocess.run([BIN + 'pdftotext', '-f', '4', '-l', '4', '-bbox', PDF, f'{WD}/p4bbox.html'], check=True)
subprocess.run([BIN + 'pdftoppm', '-f', '4', '-l', '4', '-r', '300', '-png', PDF, f'{WD}/p4'], check=True)

svg = re.sub(r'<defs>.*?</defs>', '', open(f'{WD}/p4.svg').read(), flags=re.S)
BLACK, RED = 'rgb(0%, 0%, 0%)', 'rgb(100%, 0%, 0%)'


def pts(d):
    return [(float(a), float(b)) for a, b in re.findall(r'([-\d.]+) ([-\d.]+)', d)]


frames, red, circ, thin, thick = set(), [], [], [], []
for p in re.findall(r'<path ([^>]*)/>', svg):
    a = dict(re.findall(r'([\w-]+)="([^"]*)"', p))
    P = pts(a['d'])
    tr = a.get('transform', '')
    if tr:
        assert tr == 'matrix(0.1, 0, 0, -0.1, 0, 792)', tr
        P = [(x * 0.1, 792 - y * 0.1) for x, y in P]
    st, w = a.get('stroke'), a.get('stroke-width')
    if st == BLACK and w == '6.7209':
        xs, ys = [x for x, _ in P], [y for _, y in P]
        if a['d'].count('L') == 3 and 'Z' in a['d'] and 50 < max(xs) - min(xs) < 200:
            frames.add((round(min(xs), 3), round(min(ys), 3), round(max(xs), 3), round(max(ys), 3)))
        else:
            thin.append(P)
    elif st == BLACK and w == '13.4418':
        thick.append(P)
    elif st == RED:
        red.append(P)
    elif a.get('fill') == BLACK and 'stroke' not in a and len(P) > 4:
        xs, ys = [x for x, _ in P], [y for _, y in P]
        if max(xs) - min(xs) < 1:
            circ.append(((max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2))

frames = sorted(frames, key=lambda f: (f[1], f[0]))
assert len(frames) == 30, len(frames)
TOP, BOT = frames[:14], frames[14:]

# ---- text: panel labels and scale factors -------------------------------
words = [(float(m[0]), float(m[1]), float(m[2]), float(m[3]), m[4]) for m in re.findall(
    r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>',
    open(f'{WD}/p4bbox.html').read())]


def in_frame(f, x, y):
    return f[0] < x < f[2] and f[1] < y < f[3]


def panel_text(f):
    ws = sorted([w for w in words if in_frame(f, (w[0] + w[2]) / 2, (w[1] + w[3]) / 2)],
                key=lambda w: (round(w[1]), w[0]))
    nums = [w for w in ws if re.fullmatch(r'\d+\.\d+', w[4])]
    label = (float(nums[0][4]), float(nums[1][4]))  # first line: lo < p < hi
    times = [w for w in ws if w[4] == '×']
    factor, ftxt = 1.0, None
    if times:
        t = times[0]
        nxt = [w for w in ws if abs(w[1] - t[1]) < 4 and w[0] > t[2] and w[0] - t[2] < 5]
        ftxt = nxt[0][4]
        factor = float(ftxt)
    return label, factor, ftxt


panels = []
for blk, fr, edges in (('top', TOP, PT), ('bot', BOT, PZ)):
    for i, f in enumerate(fr):
        label, factor, ftxt = panel_text(f)
        assert abs(label[0] - edges[i]) < 1e-6 and abs(label[1] - edges[i + 1]) < 1e-6, (blk, i, label)
        panels.append(dict(blk=blk, i=i, f=f, label=label, factor=factor, ftxt=ftxt))

# ---- y calibration from left-axis ticks ---------------------------------
for P in panels:
    f = P['f']
    ticks = sorted({(round(s[0][1], 3), round(abs(s[1][0] - s[0][0]), 3)) for s in thin
                    if len(s) == 2 and abs(s[0][1] - s[1][1]) < 0.01
                    and abs(min(s[0][0], s[1][0]) - f[0]) < 0.3
                    and f[1] + 0.3 < s[0][1] < f[3] + 0.5 and abs(s[1][0] - s[0][0]) < 5})
    lmin = min(l for _, l in ticks)
    major = sorted(y for y, l in ticks if l > 1.5 * lmin)
    minor = sorted(y for y, l in ticks if l <= 1.5 * lmin)
    assert len(major) == 2, (P['blk'], P['i'], ticks)
    y5, y0 = major  # page y grows downward
    P['y0'], P['ppu'] = y0, (y0 - y5) / 5.0
    ally = sorted(y for y, _ in ticks)  # all ticks: one per display unit
    sp = [b - a for a, b in zip(ally, ally[1:])]
    P['tick_spacing_dev'] = max(abs(s - P['ppu']) for s in sp)
    assert P['tick_spacing_dev'] < 0.3  # one 0.224-pt grid step, (P['blk'], P['i'], ticks)
    assert abs(y0 - f[3]) < 0.05, (P['blk'], P['i'], y0, f[3])


def owner(x, y, blk):
    """Panel of block blk whose frame contains (x, y); a point on a shared
    horizontal border belongs to the panel whose bottom edge it sits on."""
    cands = [P for P in panels if P['blk'] == blk and P['f'][0] - 0.5 < x < P['f'][2] + 0.5
             and P['f'][1] - 0.3 < y < P['f'][3] + 0.3]
    if len(cands) > 1:
        cands.sort(key=lambda P: abs(P['f'][3] - y))
    return cands[0] if cands else None


# ---- assign primitives to panels ----------------------------------------
for P in panels:
    P['red'], P['pts'] = [], []
for poly in red:
    xs = [x for x, _ in poly]
    for P in panels:
        f = P['f']
        if f[0] - 0.5 < min(xs) and max(xs) < f[2] + 0.5 and all(f[1] - 0.5 < y < f[3] + 0.5 for _, y in poly):
            assert not P['red'], 'two red lines in one panel'
            P['red'] = poly
seen = set()
for (x, y) in circ:
    key = (round(x, 2), round(y, 2))
    if key in seen:
        continue
    seen.add(key)
    blk = 'top' if y < 340 else 'bot'
    P = owner(x, y, blk)
    if P is not None:
        P['pts'].append((x, y))

# ---- bin x positions by clustering relative x over each block ------------
nb = {'top': NPZ, 'bot': NPT}
centres = {}
for blk in ('top', 'bot'):
    rel = sorted([x - P['f'][0] for P in panels if P['blk'] == blk for x, _ in P['red']]
                 + [x - P['f'][0] for P in panels if P['blk'] == blk for x, _ in P['pts']])
    cl = [[rel[0]]]
    for r in rel[1:]:
        (cl[-1] if r - cl[-1][-1] < 0.8 else cl.append([r]) or cl[-1]).append(r)
    assert len(cl) == nb[blk], (blk, len(cl), [round(c[0], 2) for c in cl])
    centres[blk] = [sum(c) / len(c) for c in cl]
    spread = max(max(c) - min(c) for c in cl)
    print(f'{blk}: {len(cl)} x-clusters, max within-cluster spread {spread:.3f} pt')


def bin_of(P, x):
    r = x - P['f'][0]
    j = min(range(len(centres[P['blk']])), key=lambda k: abs(centres[P['blk']][k] - r))
    assert abs(centres[P['blk']][j] - r) < 0.6, (P['blk'], P['i'], r)
    return j


# ---- error bars ---------------------------------------------------------
def errbar(P, x, y):
    """Return (half_up, half_dn) in pt, plus clipped flag."""
    up = dn = 0.0
    for s in thick:
        if len(s) == 2 and abs(s[0][0] - s[1][0]) < 0.01 and abs(s[0][0] - x) < 0.05:
            ys = [s[0][1], s[1][1]]
            if min(abs(v - y) for v in ys) < 0.02 and max(abs(v - y) for v in ys) < 30:
                far = max(ys, key=lambda v: abs(v - y))
                if far < y:
                    up = max(up, y - far)
                else:
                    dn = max(dn, far - y)
    f = P['f']
    clipped = (y - up <= f[1] + 0.05) or (y + dn >= f[3] - 0.05 and dn > 0)
    return up, dn, clipped


# ---- build per-panel measurements ---------------------------------------
rows = []
for P in panels:
    for x, y in P['red']:
        rows.append(dict(blk=P['blk'], panel=P['i'], kind='mc', bin=bin_of(P, x), x=x, y=y,
                         ydisp=(P['y0'] - y) / P['ppu']))
    for x, y in P['pts']:
        up, dn, clip = errbar(P, x, y)
        rows.append(dict(blk=P['blk'], panel=P['i'], kind='data', bin=bin_of(P, x), x=x, y=y,
                         ydisp=(P['y0'] - y) / P['ppu'], eup=up / P['ppu'], edn=dn / P['ppu'],
                         clipped=clip))
# uniqueness check
cnt = defaultdict(int)
for r in rows:
    cnt[(r['blk'], r['panel'], r['kind'], r['bin'])] += 1
dups = {k: v for k, v in cnt.items() if v > 1}
assert not dups, dups

pan = {(P['blk'], P['i']): P for P in panels}
QUANT = 0.22403  # pt, coordinate grid of the original PDF (see report)
cells = {}
for r in rows:
    P = pan[(r['blk'], r['panel'])]
    ipt, ipz = (r['panel'], r['bin']) if r['blk'] == 'top' else (r['bin'], r['panel'])
    area = (PT[ipt + 1] - PT[ipt]) * (PZ[ipz + 1] - PZ[ipz])
    val = r['ydisp'] / P['factor'] * 1e5 * area
    r.update(ipt=ipt, ipz=ipz, g=ipt * NPZ + ipz, area=area, count=val, factor=P['factor'])
    c = cells.setdefault(r['g'], dict(g=r['g'], ipt=ipt, ipz=ipz))
    tag = r['blk']
    r['quantum_count'] = QUANT / P['ppu'] / P['factor'] * 1e5 * area
    c[f'quant_{tag}'] = r['quantum_count']
    if r['kind'] == 'mc':
        c[f'Q_{tag}'] = val
    else:
        c[f'D_{tag}'] = val
        half = (r['eup'] + r['edn']) / 2
        r['half_disp'] = half
        # resolvable: both halves drawn, not clipped, at least 2 grid steps long
        ok = (r['eup'] > 0 and r['edn'] > 0 and not r['clipped']
              and half * P['ppu'] >= 2 * QUANT - 1e-3 and r['ydisp'] > 0)
        r['err_ok'] = ok
        if ok:
            c[f'Nerr_{tag}'] = (r['ydisp'] / half) ** 2

cols = ['g', 'ipt', 'ipz', 'D_top', 'D_bot', 'Q_top', 'Q_bot', 'Nerr_top', 'Nerr_bot']
with open(f'{WD}/fig2_cells.csv', 'w', newline='') as fh:
    w = csv.writer(fh)
    w.writerow(cols)
    for g in range(NPT * NPZ):
        c = cells.get(g, dict(g=g, ipt=g // NPZ, ipz=g % NPZ))
        w.writerow([c.get(k, '') if k in ('g', 'ipt', 'ipz') else
                    ('' if k not in c else f'{c[k]:.6g}') for k in cols])
with open(f'{WD}/fig2_points.csv', 'w', newline='') as fh:
    keys = ['blk', 'panel', 'kind', 'bin', 'g', 'ipt', 'ipz', 'factor', 'area', 'x', 'y', 'ydisp',
            'count', 'quantum_count', 'eup', 'edn', 'half_disp', 'clipped', 'err_ok']
    w = csv.DictWriter(fh, fieldnames=keys, extrasaction='ignore')
    w.writeheader()
    for r in rows:
        w.writerow(r)

# ---- summary statistics -------------------------------------------------
def med(v):
    v = sorted(v)
    n = len(v)
    return None if not n else (v[n // 2] if n % 2 else 0.5 * (v[n // 2 - 1] + v[n // 2]))


dd = [abs(c['D_top'] / c['D_bot'] - 1) for c in cells.values()
      if 'D_top' in c and 'D_bot' in c and c['D_top'] > 100 and c['D_bot'] > 100]
qq = [abs(c['Q_top'] / c['Q_bot'] - 1) for c in cells.values()
      if 'Q_top' in c and 'Q_bot' in c and c.get('D_top', 0) > 100 and c.get('D_bot', 0) > 100]
nr = [c[f'Nerr_{t}'] / c[f'D_{t}'] for c in cells.values() for t in ('top', 'bot')
      if f'Nerr_{t}' in c and c[f'D_{t}'] > 0]
def both(c, k):
    return f'{k}_top' in c and f'{k}_bot' in c


# resolution-aware subset: both D measurements >= 20 grid steps (<= 2.5 % quantisation)
res = [c for c in cells.values() if both(c, 'D') and c['D_top'] > 100 and c['D_bot'] > 100
       and c['D_top'] >= 20 * c['quant_top'] and c['D_bot'] >= 20 * c['quant_bot']]
dd20 = [abs(c['D_top'] / c['D_bot'] - 1) for c in res]
qq20 = [abs(c['Q_top'] / c['Q_bot'] - 1) for c in res if both(c, 'Q')]
# panels whose factor is not printed (assumed 1): ratio to the other block
unp = {}
for P in panels:
    if P['ftxt'] is None:
        other = 'bot' if P['blk'] == 'top' else 'top'
        rr = [c[f"D_{P['blk']}"] / c[f'D_{other}'] for c in res
              if (c['ipt'] if P['blk'] == 'top' else c['ipz']) == P['i']]
        unp[f"{P['blk']}{P['i']}"] = dict(n=len(rr), median_ratio=med(rr))
nr_strict = [c[f'Nerr_{t}'] / c[f'D_{t}'] for c in cells.values() for t in ('top', 'bot')
             if f'Nerr_{t}' in c and c[f'D_{t}'] > 0 and c[f'D_{t}'] > 0
             and any(r['g'] == c['g'] and r['blk'] == t and r['kind'] == 'data'
                     and r['half_disp'] * pan[(t, r['panel'])]['ppu'] >= 4 * QUANT - 1e-3 for r in rows)]
summ = dict(
    n_res20=len(dd20), med_dD_res20=med(dd20), max_dD_res20=max(dd20),
    n_resQ20=len(qq20), med_dQ_res20=med(qq20), max_dQ_res20=max(qq20),
    unprinted_factor_check=unp,
    n_nerr_4q=len(nr_strict), med_NerrOverD_4q=med(nr_strict),
    min_NerrOverD=min(nr), max_NerrOverD=max(nr),
    n_cells_D_gt100=len(dd), med_dD=med(dd), max_dD=max(dd),
    n_cells_Q=len(qq), med_dQ=med(qq), max_dQ=max(qq),
    n_nerr=len(nr), med_NerrOverD=med(nr),
    sumD_top=sum(c.get('D_top', 0) for c in cells.values()),
    sumD_bot=sum(c.get('D_bot', 0) for c in cells.values()),
    sumQ_top=sum(c.get('Q_top', 0) for c in cells.values()),
    sumQ_bot=sum(c.get('Q_bot', 0) for c in cells.values()),
    panels=[dict(blk=P['blk'], i=P['i'], label=P['label'], factor_text=P['ftxt'],
                 ppu=round(P['ppu'], 4), tick_dev=round(P['tick_spacing_dev'], 4),
                 n_red=len(P['red']), n_pts=len(P['pts'])) for P in panels],
    centres={k: [round(v, 3) for v in vs] for k, vs in centres.items()},
)
json.dump(summ, open(f'{WD}/summary.json', 'w'), indent=1)
for k, v in summ.items():
    if k not in ('panels', 'centres'):
        print(k, v)

# ---- overlay renders ----------------------------------------------------
from PIL import Image, ImageDraw
img = Image.open(f'{WD}/p4-04.png').convert('RGB')
s = img.size[0] / 612.0
dr = ImageDraw.Draw(img)
for r in rows:
    P = pan[(r['blk'], r['panel'])]
    # reconstruct page position from the extracted count (round trip)
    yd = r['count'] * P['factor'] / (1e5 * r['area'])
    X = (P['f'][0] + centres[r['blk']][r['bin']]) * s
    Y = (P['y0'] - yd * P['ppu']) * s
    if r['kind'] == 'mc':
        half = 0.5 * min([abs(c - centres[r['blk']][r['bin']]) for c in centres[r['blk']] if c != centres[r['blk']][r['bin']]])
        dr.line([(X - half * s, Y), (X + half * s, Y)], fill=(0, 200, 255), width=2)
    else:
        rr = 5
        dr.ellipse([X - rr, Y - rr, X + rr, Y + rr], outline=(0, 170, 0), width=2)
        if r.get('err_ok'):
            h = r['half_disp'] * P['ppu'] * s
            dr.line([(X + 7, Y - h), (X + 7, Y + h)], fill=(255, 0, 255), width=2)
for P in panels:
    f = P['f']
    dr.text((f[0] * s + 4, f[1] * s + 40), f"f={P['factor']}", fill=(0, 0, 255))
    for v in (0, 5):
        yy = (P['y0'] - v * P['ppu']) * s
        dr.line([(f[0] * s, yy), (f[0] * s + 25, yy)], fill=(255, 140, 0), width=1)
img.crop((int(95 * s), int(65 * s), int(565 * s), int(330 * s))).save(f'{WD}/overlay_top.png')
img.crop((int(95 * s), int(365 * s), int(565 * s), int(632 * s))).save(f'{WD}/overlay_bot.png')

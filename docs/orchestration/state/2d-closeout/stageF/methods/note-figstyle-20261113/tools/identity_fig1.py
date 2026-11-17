"""Fig. 1 identity test: the extended-display redraw against the committed control_plots.pdf (note figure style, group C,
family 1b; the director's ruling (c) of 2026-11-14).

usage: python3 identity_fig1.py <committed control_plots.pdf> <redrawn control_plots.pdf> <out dir>     (needs PyMuPDF)

Four parts, each printed PASS or FAIL:
  1. text:    the sorted multiset of printed words (PyMuPDF get_text "words") is equal.
  2. values:  every drawn path, grouped by stroke and fill colour, has the same vertices, to TOL_PT page points
              (matplotlib writes coordinates to about 0.01 pt). The bars, outlines, ratio markers and error bars are paths,
              so this compares every plotted value in page units, with the axes' mapping fixed by part 1's tick labels.
  3. catch:   the same comparison restricted to each panel's last bin (the vertices right of the panel's last x tick
              label but one), which holds the compressed catch bin, and the "100" overflow tick labels themselves.
  4. visual:  pdftoppm -r 100 rasters of both; the count of differing pixels is printed, and 0 is PASS.
Exit 0 only if all four pass.
"""
import collections, os, subprocess, sys

import numpy as np
import pymupdf as fitz

TOL_PT = 0.02


def words(page):
    return sorted(w[4] for w in page.get_text("words"))


def paths(page):
    """{(stroke colour, fill colour): sorted list of rounded vertex tuples, one per path}."""
    out = collections.defaultdict(list)
    for p in page.get_drawings():
        key = (tuple(round(c, 3) for c in (p.get("color") or ())), tuple(round(c, 3) for c in (p.get("fill") or ())))
        pts = []
        for it in p["items"]:
            if it[0] == "l":
                pts += [(it[1].x, it[1].y), (it[2].x, it[2].y)]
            elif it[0] == "re":
                r = it[1]
                pts += [(r.x0, r.y0), (r.x1, r.y1)]
            elif it[0] == "c":
                pts += [(q.x, q.y) for q in it[1:5]]
            elif it[0] == "qu":
                q = it[1]
                pts += [(q.ul.x, q.ul.y), (q.lr.x, q.lr.y)]
        out[key].append(np.array(pts, dtype=float))
    for k in out:
        out[k].sort(key=lambda a: (len(a), tuple(a.round(1).ravel()[:8])))
    return out


def compare_paths(a, b, keep=None):
    """Number of colour groups compared, mismatches (list of str), max |delta| in points."""
    bad, dmax, n = [], 0.0, 0
    for k in sorted(set(a) | set(b)):
        pa, pb = a.get(k, []), b.get(k, [])
        if keep is not None:
            pa = [keep(x) for x in pa]
            pb = [keep(x) for x in pb]
            pa = [x for x in pa if len(x)]
            pb = [x for x in pb if len(x)]
        if len(pa) != len(pb):
            bad.append(f"{k}: {len(pa)} paths vs {len(pb)}")
            continue
        n += 1
        for x, y in zip(pa, pb):
            if x.shape != y.shape:
                bad.append(f"{k}: vertex count {len(x)} vs {len(y)}")
                continue
            if len(x):
                d = float(np.abs(x - y).max())
                dmax = max(dmax, d)
                if d > TOL_PT:
                    bad.append(f"{k}: max delta {d:.4f} pt")
    return n, bad, dmax


def main():
    ref, new, out = sys.argv[1:4]
    os.makedirs(out, exist_ok=True)
    pr, pn = fitz.open(ref)[0], fitz.open(new)[0]
    ok = []

    wr, wn = words(pr), words(pn)
    diff = (collections.Counter(wr) - collections.Counter(wn)) + (collections.Counter(wn) - collections.Counter(wr))
    t_ok = not diff
    print(f"1. text: {len(wr)} vs {len(wn)} words; differing multiset entries {sum(diff.values())} -> {'PASS' if t_ok else 'FAIL'}")
    if diff:
        print("   ", dict(list(diff.items())[:20]))
    ok.append(t_ok)

    ar, an = paths(pr), paths(pn)
    n, bad, dmax = compare_paths(ar, an)
    v_ok = not bad
    print(f"2. values: {n} colour groups, {sum(len(v) for v in ar.values())} vs {sum(len(v) for v in an.values())} paths; "
          f"max vertex delta {dmax:.4f} pt (tol {TOL_PT}); mismatches {len(bad)} -> {'PASS' if v_ok else 'FAIL'}")
    for m in bad[:10]:
        print("   ", m)
    ok.append(v_ok)

    # Catch bins: vertices right of each panel's second-to-last x tick label; "100" labels compared as text with position.
    def hundreds(page):
        return sorted((round((w[0] + w[2]) / 2, 1), round(w[1], 1)) for w in page.get_text("words") if w[4] == "100")
    hr, hn = hundreds(pr), hundreds(pn)
    xcut = sorted(x for x, _ in hr)
    def keep_right(arr, cuts=xcut):
        if not len(cuts):
            return arr[:0]
        return arr[arr[:, 0] >= min(cuts) - 40.0]
    n3, bad3, dmax3 = compare_paths(ar, an, keep=keep_right)
    pos_ok = len(hr) == len(hn) and all(abs(a[0] - b[0]) <= 0.1 and abs(a[1] - b[1]) <= 0.1 for a, b in zip(hr, hn))
    c_ok = pos_ok and not bad3
    print(f"3. catch: {len(hr)} vs {len(hn)} '100' labels, positions equal {pos_ok}; vertices near the catch bins: "
          f"max delta {dmax3:.4f} pt, mismatches {len(bad3)} -> {'PASS' if c_ok else 'FAIL'}")
    ok.append(c_ok)

    for tag, f in (("ref", ref), ("new", new)):
        subprocess.run(["pdftoppm", "-r", "100", "-png", "-singlefile", f, os.path.join(out, tag)], check=True)
    from PIL import Image
    ia = np.asarray(Image.open(os.path.join(out, "ref.png")).convert("RGB")).astype(int)
    ib = np.asarray(Image.open(os.path.join(out, "new.png")).convert("RGB")).astype(int)
    if ia.shape != ib.shape:
        print(f"4. visual: raster shapes {ia.shape} vs {ib.shape} -> FAIL")
        ok.append(False)
    else:
        d = np.any(ia != ib, axis=2)
        nd = int(d.sum())
        if nd:
            Image.fromarray((~d * 255).astype(np.uint8)).save(os.path.join(out, "diffmask.png"))
            ys, xs = np.nonzero(d)
            print(f"   differing region x {xs.min()}-{xs.max()} y {ys.min()}-{ys.max()}")
        print(f"4. visual: {ia.shape[1]}x{ia.shape[0]} px at 100 dpi; differing pixels {nd} -> {'PASS' if nd == 0 else 'FAIL'}")
        ok.append(nd == 0)

    print("ALL PASS" if all(ok) else "NOT ALL PASS")
    sys.exit(0 if all(ok) else 1)


if __name__ == "__main__":
    main()

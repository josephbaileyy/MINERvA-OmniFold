#!/usr/bin/env python3
"""The drawn-data identity check for Fig. 1 version B' (DECISION-20261116-joseph-paper-batch.md item 15).

  python -I fig1_identity.py --arrays fig_arrays_q.npz --values uqmedian.tex --old OLD/make_figs.py \\
      --new NEW/make_figs.py --outdir DIR [--old-fig1 SHA] [--new-fig1 SHA] [--fig2 SHA] [--fig3 SHA]

Both producers run their own main() in this interpreter on the same arrays (the --npz that re2c_fig1.py writes, its
tmp/fig_arrays_q.npz), each into DIR/old or DIR/new. At every save the figure's drawn data are dumped with the
fig-restyle campaign's artists.py (every data artist as arrays, hashed with its colours and styles; Axes.hist's input
values as "hist-input" items), with every text per axes, and the canvas is rasterized at 300 dpi. The checks, each a
FAIL:
  F1  each figure's PDF digest equals the one given (--old-fig1, --new-fig1, --fig2, --fig3; both versions for fig2
      and fig3);
  F2  fig2 and fig3: the same items, the same texts and the same PDF bytes in both versions;
  F3  Fig. 1 has 7 axes in both versions, and on the six that are not the bottom-right panel the multiset of item
      hashes is equal (data, colours and styles, bit for bit);
  F4  the texts of those six axes are equal, except the colour bar's: its side label
      "(OmniFold $-$ published)$/\\sigma_{\\mathrm{published}}$" (7.5 pt) must go, leaving no side label, and its
      axes title must become "$r_i$" (8 pt), from none;
  F5  the panel: the old one draws no data item; the new one draws exactly one Axes.hist call, whose values equal,
      bit for bit, r_i = (ours_v - paper_v) / sqrt(diag cov_total) on mask_reported, computed here from the arrays
      (205 values); its bins are 0.25 wide, one is centred on zero, they cover min and max of r_i (no clipping) and
      the counts sum to 205; its only line is the vertical line at zero (no reference curve);
  F6  the panel's printed count, mean and spread equal the old panel's printed ones and f"{r.mean():.3f}",
      f"{r.std():.3f}" of the r_i here; the old label "RMS" becomes "SD";
  F7  every pixel that differs between the two 300-dpi rasters lies inside the panel's box (old or new, tight), the
      colour bar's side label box or its title box (each where non-empty, old or new), each with a 2 px margin.
Writes DIR/identity.json and prints one line per check and FIG1 IDENTITY PASS or FAIL (exit 0 or 1)."""
import argparse
import hashlib
import importlib.util
import io
import json
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[10]
sys.path.insert(0, str(REPO / "docs/orchestration/state/2d-closeout/stageF/methods/fig-restyle-20261031/tools"))
import artists  # noqa: E402

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.axes import Axes  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402
from matplotlib.text import Text  # noqa: E402

OLD_CB = r"(OmniFold $-$ published)$/\sigma_{\mathrm{published}}$"
NEW_CB = r"$r_i$"
DPI = 300


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def axes_texts(fig):
    """Per axes index: sorted (font size, text) of every visible non-empty Text it holds (labels, ticks, ax.texts)."""
    out = []
    for ax in fig.axes:
        ts = []
        for t in ax.findobj(Text):
            s = t.get_text()
            if isinstance(s, str) and s.strip() and t.get_visible():
                ts.append((float(t.get_fontsize()), s))
        out.append(sorted(ts))
    return out


def run(make_figs, arrays, values, outdir):
    """Run make_figs.main into outdir, capturing what each saved figure draws."""
    caps = {}
    real_save, real_hist = Figure.savefig, Axes.hist

    def hist(ax, x, *a, **k):
        r = real_hist(ax, x, *a, **k)
        ax.figure._b_hist = getattr(ax.figure, "_b_hist", []) + [
            (ax.figure.axes.index(ax), np.array(x, dtype=np.float64), np.array(r[0]), np.array(r[1]))]
        return r

    def save(fig, fname, *a, **k):
        real_save(fig, fname, *a, **k)
        name = Path(fname).name
        arrays, index = artists.collect(fig)
        buf = io.BytesIO()
        real_save(fig, buf, format="png", dpi=DPI)
        img = plt.imread(io.BytesIO(buf.getvalue()))
        fig.set_dpi(DPI)
        fig.canvas.draw()
        rend = fig.canvas.get_renderer()
        boxes = {}
        if len(fig.axes) == 7:
            boxes["panel"] = fig.axes[6].get_tightbbox(rend).extents.tolist()
            cb = fig.axes[5]
            for k, t in (("cblabel", cb.yaxis.label), ("cbtitle", cb.title)):
                if t.get_text().strip():
                    boxes[k] = t.get_window_extent(rend).extents.tolist()
        cbt = ({"label": fig.axes[5].get_ylabel(), "title": fig.axes[5].get_title()} if len(fig.axes) == 7 else {})
        caps[name] = {"cb": cbt, "items": index, "arrays": arrays, "texts": axes_texts(fig), "img": img, "boxes": boxes,
                      "hist": getattr(fig, "_b_hist", []), "n_axes": len(fig.axes)}

    spec = importlib.util.spec_from_file_location(f"make_figs_{abs(hash(str(make_figs)))}", make_figs)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    Figure.savefig, Axes.hist = save, hist
    try:
        rc = mod.main(["--npz", str(arrays), "--outdir", str(outdir), "--values", str(values)])
    finally:
        Figure.savefig, Axes.hist = real_save, real_hist
        plt.rcdefaults()
    return rc, caps


def main(argv=None):
    ap = argparse.ArgumentParser()
    for k in ("arrays", "values", "old", "new", "outdir"):
        ap.add_argument("--" + k, type=Path, required=True)
    for k in ("old-fig1", "new-fig1", "fig2", "fig3"):
        ap.add_argument("--" + k)
    a = ap.parse_args(argv)
    res, ok = {}, True

    def check(name, cond, detail=""):
        nonlocal ok
        ok &= bool(cond)
        res[name] = {"pass": bool(cond), "detail": detail}
        print(f"{'PASS' if cond else 'FAIL'} {name}: {detail}")

    rc_o, old = run(a.old, a.arrays, a.values, a.outdir / "old")
    rc_n, new = run(a.new, a.arrays, a.values, a.outdir / "new")
    F1, F2, F3 = "fig1_validation.pdf", "fig2_joint_localization.pdf", "fig3_generator_context.pdf"
    check("F0 both producers ran", rc_o == 0 and rc_n == 0 and set(old) == set(new) == {F1, F2, F3},
          f"rc {rc_o} / {rc_n}; figures {sorted(new)}")
    if not res["F0 both producers ran"]["pass"]:
        print("FIG1 IDENTITY FAIL"); return 1
    dig = {v: {f: sha(a.outdir / v / f) for f in (F1, F2, F3)} for v in ("old", "new")}
    want = [("old", F1, a.old_fig1), ("new", F1, a.new_fig1)] + [(v, f, w) for f, w in ((F2, a.fig2), (F3, a.fig3))
                                                                for v in ("old", "new")]
    bad = [f"{v}/{f} {dig[v][f][:16]} != {w[:16]}" for v, f, w in want if w and dig[v][f] != w]
    check("F1 PDF digests as given", not bad, "; ".join(bad) or ", ".join(f"{v}/{f} {w[:8]}" for v, f, w in want if w))
    for f in (F2, F3):
        same = (Counter(i["hash"] for i in old[f]["items"]) == Counter(i["hash"] for i in new[f]["items"])
                and old[f]["texts"] == new[f]["texts"] and dig["old"][f] == dig["new"][f])
        check(f"F2 {f} unchanged", same, f"{len(new[f]['items'])} items, PDF {dig['new'][f][:16]}")
    o, n = old[F1], new[F1]
    check("F3a seven axes", o["n_axes"] == n["n_axes"] == 7, f"{o['n_axes']} / {n['n_axes']}")
    diff_ax = [k for k in range(6) if Counter(i["hash"] for i in o["items"] if i["axes"] == k)
               != Counter(i["hash"] for i in n["items"] if i["axes"] == k)]
    nk = sum(1 for i in n["items"] if i["axes"] != 6)
    check("F3b the six other axes draw the same items", not diff_ax, f"{nk} items; differing axes {diff_ax}")
    tdiff = [k for k in range(6) if k != 5 and o["texts"][k] != n["texts"][k]]
    cb_o = Counter(o["texts"][5]) - Counter(n["texts"][5]); cb_n = Counter(n["texts"][5]) - Counter(o["texts"][5])
    cbo, cbn = o["cb"], n["cb"]
    check("F4 texts equal except the colour bar label", not tdiff and dict(cb_o) == {(7.5, OLD_CB): 1}
          and dict(cb_n) == {(8.0, NEW_CB): 1} and cbo == {"label": OLD_CB, "title": ""}
          and cbn == {"label": "", "title": NEW_CB},
          f"other axes differing {tdiff}; removed {dict(cb_o)}; added {dict(cb_n)}; colour bar old {cbo}, new {cbn}")
    z = np.load(a.arrays, allow_pickle=False)
    m = z["mask_reported"].astype(bool)
    dd = np.sqrt(np.where(np.diag(z["cov_total"]) > 0, np.diag(z["cov_total"]), np.nan))
    r = ((z["ours_v"] - z["paper_v"]) / dd)[m]
    p_old = [i for i in o["items"] if i["axes"] == 6]
    hs = n["hist"]
    ok5 = not p_old and len(hs) == 1 and hs[0][0] == 6
    det = f"old panel items {len(p_old)}; hist calls {len(hs)}"
    if ok5:
        _, x, cnt, bins = hs[0]
        w = np.diff(bins)
        lines = [i for i in n["items"] if i["axes"] == 6 and i["kind"] == "line"]
        others = {i["kind"] for i in n["items"] if i["axes"] == 6} - {"line", "patch", "hist-input"}
        vxy = n["arrays"][f"i{lines[0]['i']}.xy"] if len(lines) == 1 else np.zeros((0, 2))
        cen = (bins[:-1] + bins[1:]) / 2
        ok5 = (x.shape == (205,) and np.array_equal(x, r) and np.allclose(w, 0.25, rtol=0, atol=1e-12)
               and np.min(np.abs(cen)) < 1e-12 and bins[0] <= r.min() and r.max() <= bins[-1]
               and int(cnt.sum()) == 205 and len(lines) == 1 and not others
               and vxy.shape == (2, 2) and np.all(vxy[:, 0] == 0) and vxy[0, 1] != vxy[1, 1])
        det += (f"; values == r_i: {np.array_equal(x, r)} ({x.size}); width {w.min():.12g}..{w.max():.12g}; "
                f"min |centre| {np.min(np.abs(cen)):.3g}; bins {bins[0]:.3f}..{bins[-1]:.3f} cover r_i {r.min():.3f}..{r.max():.3f}; "
                f"counts {int(cnt.sum())}; "
                f"lines {len(lines)} (x {vxy[:, 0].tolist()}); other kinds {sorted(others)}")
    check("F5 the panel's histogram is of the 205 r_i", ok5, det)
    t_old = " ".join(s for _, s in o["texts"][6]); t_new = " ".join(s for _, s in n["texts"][6])
    mo = re.search(r"mean = (\S+),\s+RMS = (\S+)\s+\((\d+) bins\)", t_old)
    mn = re.search(r"(\d+) bins\nmean (\S+)\nSD (\S+)", t_new)
    want6 = (str(m.sum()), f"{r.mean():.3f}", f"{r.std():.3f}")
    check("F6 printed count, mean and SD", bool(mo and mn) and (mo.group(3), mo.group(1), mo.group(2)) == want6
          == (mn.group(1), mn.group(2), mn.group(3)), f"old {mo.groups() if mo else None}; new {mn.groups() if mn else None}; "
          f"from the arrays {want6}")
    io_, in_ = o["img"], n["img"]
    if io_.shape != in_.shape:
        check("F7 changed pixels inside the panel and the colour bar's label boxes", False, f"shapes {io_.shape} {in_.shape}")
    else:
        H = io_.shape[0]
        chg = np.any(io_ != in_, axis=2)
        allow = np.zeros_like(chg)
        for b in [v for c in (o, n) for v in c["boxes"].values()]:
            x0, y0, x1, y1 = b
            allow[max(0, int(np.floor(H - y1)) - 2):int(np.ceil(H - y0)) + 2, max(0, int(np.floor(x0)) - 2):int(np.ceil(x1)) + 2] = True
        out = chg & ~allow
        ys, xs = np.nonzero(chg)
        bb = f"x {xs.min()}..{xs.max()}, y {ys.min()}..{ys.max()}" if xs.size else "none"
        check("F7 changed pixels inside the panel and the colour bar's label boxes", not out.any(),
              f"{int(chg.sum())} changed pixels ({bb}); {int(out.sum())} outside; image {io_.shape[1]}x{H}")
    rec = {"arrays": {"path": str(a.arrays), "sha256": sha(a.arrays)}, "values_sha256": sha(a.values),
           "old_make_figs": {"path": str(a.old), "sha256": sha(a.old)},
           "new_make_figs": {"path": str(a.new), "sha256": sha(a.new)},
           "pdf_sha256": dig, "boxes_px": {"old": o["boxes"], "new": n["boxes"]}, "checks": res,
           "versions": {"python": sys.version.split()[0], "matplotlib": matplotlib.__version__, "numpy": np.__version__},
           "verdict": "PASS" if ok else "FAIL"}
    (a.outdir / "identity.json").write_text(json.dumps(rec, indent=1) + "\n")
    print("FIG1 IDENTITY PASS" if ok else "FIG1 IDENTITY FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

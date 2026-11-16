"""Family 7's identity test: fig6/7 (MEFHC_fig6_7_uncertainty_pt/pz) drawn by the opt-in --from-projections path of
2d-unfolding/uq/plot_uncertainty_fig6_7_style.py (note figure style; the director's approval of 2026-11-15).

usage: python3 identity_family7.py <base producer .py> <out dir>    (matplotlib 3.10.8, numpy 1.26: the run's versions;
                                                                     PyMuPDF, pdftoppm; PYTHONPATH must hold fakeroot7;
                                                                     DRAW_PY: the interpreter that draws part a)
Inputs: RE-2-shapes run 2's committed fig67/ (fd/receipts-cov2d/g2r/re2shapes/run2/g2r/, main d58d0d18), its
fig67_projections.json and its two PDFs, drawn on the cluster through the ROOT path at deploy 903fb78b
(logs/steps.tsv, row fig67).
Three parts, each PASS or FAIL:
  a. reproduce:  --from-projections with the run's --ml-label and --include-ml, no --print-style, under fakeroot7 (any
                 ROOT use raises), against each committed PDF: the words, every drawn path to 0.02 pt, and the
                 pdftoppm -r 100 raster (0 differing pixels). So the JSON path draws what the ROOT path drew.
  b. default:    the base producer's draw_one and the new one with print_style left False, on the same curves, write
                 byte-identical PDFs (SOURCE_DATE_EPOCH fixed). So the default path is unchanged.
  c. data:       --print-style changes no data artist: every StepPatch's values and edges (exactly), label, colour and
                 line style equal those of the default figure.
Exit 0 only if all pass.
"""
import collections, importlib.util, json, os, subprocess, sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[7]
G = REPO / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d/g2r/re2shapes/run2/g2r"
NEW = REPO / "2d-unfolding/uq/plot_uncertainty_fig6_7_style.py"
sys.path.insert(0, str(HERE))
import identity_fig1 as idf  # noqa: E402  (words, paths, compare_paths)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    for d in (REPO, NEW.parent):         # the base copy may sit outside the repository: resolve its imports here
        if str(d) not in sys.path:
            sys.path.insert(0, str(d))
    spec.loader.exec_module(m)
    return m


def raster_equal(a, b, out, tag):
    from PIL import Image
    for t, f in (("ref", a), ("new", b)):
        subprocess.run(["pdftoppm", "-r", "100", "-png", "-singlefile", f, os.path.join(out, f"{tag}-{t}")], check=True)
    ia = np.asarray(Image.open(os.path.join(out, f"{tag}-ref.png")).convert("RGB")).astype(int)
    ib = np.asarray(Image.open(os.path.join(out, f"{tag}-new.png")).convert("RGB")).astype(int)
    return ia.shape == ib.shape and not np.any(ia != ib), (ia.shape, int(np.any(ia != ib, axis=2).sum()) if ia.shape == ib.shape else -1)


def main():
    base, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    ok = []
    # a. reproduce the committed PDFs from the JSON
    pre = out / "a" / "MEFHC_fig6_7_uncertainty"; pre.parent.mkdir(exist_ok=True)
    env = dict(os.environ)
    r = subprocess.run([os.environ.get("DRAW_PY", sys.executable), str(NEW), "--from-projections", str(G / "fig67/fig67_projections.json"),
                        "--include-ml", "always", "--ml-label", "Training seed", "--out-prefix", str(pre)],
                       env=env, capture_output=True, text=True)
    print(r.stdout.strip()); print(r.stderr.strip()[-400:])
    a_ok = r.returncode == 0
    import pymupdf as fitz
    for suf in ("pt", "pz"):
        ref, new = G / f"fig67/MEFHC_fig6_7_uncertainty_{suf}.pdf", Path(f"{pre}_{suf}.pdf")
        if not new.exists():
            print(f"a. {suf}: no output -> FAIL"); a_ok = False; continue
        pr, pn = fitz.open(ref)[0], fitz.open(new)[0]
        wd = (collections.Counter(idf.words(pr)) - collections.Counter(idf.words(pn))) + \
             (collections.Counter(idf.words(pn)) - collections.Counter(idf.words(pr)))
        n, bad, dmax = idf.compare_paths(idf.paths(pr), idf.paths(pn))
        req, info = raster_equal(ref, new, out, suf)
        this = not wd and not bad and req
        print(f"a. {suf}: words differ {sum(wd.values())}; {n} path groups, mismatches {len(bad)}, max {dmax:.4f} pt; "
              f"raster {info[0]} differing {info[1]} -> {'PASS' if this else 'FAIL'}")
        a_ok &= this
    # a's mutant: one curve of the JSON scaled by 1.01 must make part a fail (the comparison can see a data change)
    mut = json.load(open(G / "fig67/fig67_projections.json"), object_pairs_hook=collections.OrderedDict)
    k0 = next(iter(mut["pt"])); mut["pt"][k0] = [1.01 * v for v in mut["pt"][k0]]
    mj = out / "mutant.json"; mj.write_text(json.dumps(mut))
    mpre = out / "m" / "MEFHC_fig6_7_uncertainty"; mpre.parent.mkdir(exist_ok=True)
    subprocess.run([os.environ.get("DRAW_PY", sys.executable), str(NEW), "--from-projections", str(mj),
                    "--include-ml", "always", "--ml-label", "Training seed", "--out-prefix", str(mpre)],
                   env=env, capture_output=True, text=True)
    pr, pn = fitz.open(G / "fig67/MEFHC_fig6_7_uncertainty_pt.pdf")[0], fitz.open(f"{mpre}_pt.pdf")[0]
    killed = bool(idf.compare_paths(idf.paths(pr), idf.paths(pn))[1])
    print(f"a. mutant ({k0!r} x 1.01 in pt): path mismatches found {killed} -> {'KILLED' if killed else 'SURVIVED'}")
    ok.append(a_ok and killed)
    # b. the default draw_one is unchanged
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    dump = json.load(open(G / "fig67/fig67_projections.json"), object_pairs_hook=collections.OrderedDict)
    mb, mn = load(base, "fig67_base"), load(NEW, "fig67_new")
    b_ok = True
    for suf, edges in (("pt", mn.PT_EDGES), ("pz", mn.PZ_EDGES)):
        curves = collections.OrderedDict((k, np.asarray(v, float)) for k, v in dump[suf].items())
        files = []
        for tag, m in (("base", mb), ("new", mn)):
            os.environ["SOURCE_DATE_EPOCH"] = "0"      # a fixed PDF CreationDate, so the bytes compare
            f = out / f"b-{tag}-{suf}.png"
            m.draw_one(suf, edges, curves, str(f), None, None, "Training seed", ("Run period",))
            files.append(f.with_suffix(".pdf"))
        same = files[0].read_bytes() == files[1].read_bytes()
        print(f"b. {suf}: base and new default PDFs byte-identical {same} -> {'PASS' if same else 'FAIL'}")
        b_ok &= same
    ok.append(b_ok)
    # c. the print style changes no data artist
    c_ok = True
    from matplotlib.patches import StepPatch
    for suf, edges in (("pt", mn.PT_EDGES), ("pz", mn.PZ_EDGES)):
        curves = collections.OrderedDict((k, np.asarray(v, float)) for k, v in dump[suf].items())
        grabbed = []
        orig_close = plt.close
        plt.close = lambda fig=None: grabbed.append(fig)
        try:
            mn.draw_one(suf, edges, curves, str(out / f"c-def-{suf}.png"), None, None, "Training seed", ("Run period",))
            mn.draw_one(suf, edges, curves, str(out / f"c-ps-{suf}.png"), None, None, "Training seed", ("Run period",),
                        print_style=True)
        finally:
            plt.close = orig_close
        def data(fig):
            return [(p.get_label(), tuple(np.asarray(p.get_data().values).tolist()), tuple(np.asarray(p.get_data().edges).tolist()),
                     p.get_edgecolor(), p.get_linestyle()) for p in fig.axes[0].patches if isinstance(p, StepPatch)]
        d0, d1 = data(grabbed[0]), data(grabbed[1])
        same = d0 == d1 and len(d0) == len(curves)
        print(f"c. {suf}: {len(d0)} step artists, data/label/colour/linestyle equal {same} -> {'PASS' if same else 'FAIL'}")
        c_ok &= same
    ok.append(c_ok)
    print("ALL PASS" if all(ok) else "NOT ALL PASS")
    sys.exit(0 if all(ok) else 1)


if __name__ == "__main__":
    main()

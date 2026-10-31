#!/usr/bin/env python3
"""Mutation receipt for the restyle checks: each planted weakness in a checker must make selftest.py fail.

usage: python3 -I mutate.py [DEPLOY] > MUTATION-RECEIPT.txt
For each mutant, the tools are copied to a temporary directory and one exact text replacement (which must occur exactly
once) is applied to one file. Then selftest.py runs on the copy, against DEPLOY (default: this repository). A mutant is
KILLED when the self-test fails, and the cases that went wrong are listed. The unmutated copy must pass first. Exit 0
only if the control passes and every mutant is killed."""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEPLOY = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else HERE.parents[7]
FILES = ("artists.py", "capture.py", "compare.py", "raster.py", "textsize.py", "overlap.py", "selftest.py",
         "toy_producer.py")

MUTANTS = [
    ("a line's colours are not hashed (line, marker face and marker edge)", "artists.py",
     '''"xy": a.get_xydata(), "color": to_rgba(a.get_color(), a.get_alpha()),
                    "mfc": to_rgba(a.get_markerfacecolor()), "mec": to_rgba(a.get_markeredgecolor()),''',
     '''"xy": a.get_xydata(),'''),
    ("values hashed as float32 (a tolerance)", "artists.py",
     "np.ascontiguousarray(np.asarray(x, dtype=np.float64))",
     "np.ascontiguousarray(np.asarray(x, dtype=np.float32).astype(np.float64))"),
    ("patches are not captured", "artists.py",
     "elif isinstance(a, Patch) and _in_data(a, ax):", "elif False:"),
    ("collections' colours are not hashed (face and edge)", "artists.py",
     '''f = {"offsets": a.get_offsets(), "face": to_rgba_array(a.get_facecolors()),
                     "edge": to_rgba_array(a.get_edgecolors()), "cmap": _cmap(a)}''',
     '''f = {"offsets": a.get_offsets(), "cmap": _cmap(a)}'''),
    ("labels are hashed (a restyle of a label fires)", "artists.py",
     "h, dh, colours, arr = _item(kind, fields)", "h, dh, colours, arr = _item(kind + str(label), fields)"),
    ("figures compared by item count only", "compare.py",
     'cb, ca = Counter(x["hash"] for x in ib), Counter(x["hash"] for x in ia)',
     'cb, ca = Counter(len(ib) for x in ib), Counter(len(ia) for x in ia)'),
    ("wall-time lines not dropped", "compare.py",
     'return "\\n".join(l for l in text.splitlines() if not TIMING.search(l))', 'return text'),
    ("outputs not compared", "compare.py",
     "elif norm(pb.read_text(errors=\"replace\"), subs) != norm(pa.read_text(errors=\"replace\"), subs):",
     "elif False:"),
    ("opened inputs not compared", "compare.py",
     "elif rows(pb) != rows(pa):", "elif False:"),
    ("rasters compared by size only", "raster.py",
     "bad += int(np.any(a != b, axis=2).sum())", "bad += 0"),
    ("the size floor's comparison inverted", "textsize.py",
     "fail = floor is not None and lo[0] < floor", "fail = floor is not None and lo[0] > floor"),
    ("the printed-width scaling dropped", "textsize.py",
     "scale = WIDTH_IN[stem] * 72 / page_w", "scale = 1.0"),
    ("amendment 1: series colours not checked against the palette", "compare.py",
     "            if want_c != got_c:", "            if False:"),
    ("amendment 1: the recolour table ignored (every colour must stay)", "compare.py",
     "        return c if ident is None else pal[ident] + c[7:]", "        return c"),
    ("amendment 1: the binning exception applied to every figure", "compare.py",
     """        keep = (lambda x: not (x["kind"] == "patch" and x.get("gid") == "restyle-hist")) if k.name[:-len(".json")] in rebin \\""",
     """        keep = (lambda x: not (x["kind"] == "patch" and x.get("gid") == "restyle-hist")) if True \\"""),
    ("amendment 1: the values given to hist not recorded", "capture.py",
     """    fig.__dict__.setdefault("_restyle_hist_inputs", []).append((n, vals))""", """    pass"""),
    ("amendment 1: the overlap test disabled", "overlap.py",
     """                if any(_hits_box(g, box) for g in _geometry(a, ax)):""", """                if False:"""),
    ("capture wraps savefig before technote_style (the .pdf twin captured too)", "capture.py",
     "import technote_style  # noqa: E402,F401  (installs its .pdf-twin wrapper before ours)\n", ""),
]


def selftest(tools):
    p = subprocess.run([sys.executable, "-I", str(tools / "selftest.py"), str(DEPLOY)], capture_output=True, text=True)
    wrong = [l.strip() for l in p.stdout.splitlines() if l.rstrip().endswith("WRONG")]
    return p.returncode, wrong, p.stdout.strip().splitlines()[-1:] or [p.stderr.strip()[-300:]]


def main():
    import matplotlib
    import numpy
    ok = True
    print(f"python {sys.version.split()[0]}, matplotlib {matplotlib.__version__}, numpy {numpy.__version__}; "
          f"deploy {DEPLOY.name}")
    with tempfile.TemporaryDirectory() as t:
        ctl = Path(t) / "control"
        ctl.mkdir()
        for f in FILES:
            shutil.copy(HERE / f, ctl / f)
        rc, wrong, last = selftest(ctl)
        print(f"control (unmutated copy): {'PASS' if rc == 0 else 'FAIL'} {last}")
        ok &= rc == 0
        for n, (name, f, old, new) in enumerate(MUTANTS, 1):
            d = Path(t) / f"m{n}"
            shutil.copytree(ctl, d)
            src = (d / f).read_text()
            if src.count(old) != 1:
                print(f"M{n} {name}: NOT APPLIED (the text occurs {src.count(old)} times in {f})")
                ok = False
                continue
            (d / f).write_text(src.replace(old, new))
            rc, wrong, last = selftest(d)
            killed = rc != 0
            ok &= killed
            print(f"M{n} {name} ({f}): {'KILLED' if killed else 'SURVIVED'}")
            for w in wrong:
                print(f"     {w}")
            if killed and not wrong:
                print(f"     {last}")
    print("MUTATION ::", "PASS (control passes, every mutant killed)" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

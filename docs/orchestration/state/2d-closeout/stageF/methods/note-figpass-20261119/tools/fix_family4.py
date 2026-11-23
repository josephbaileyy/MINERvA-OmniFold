#!/usr/bin/env python3
"""Family-4 figures with declared label fixes (the figure pass, chunk C: the grader's F4 items on Figs. 19 and 22).

usage: python3 fix_family4.py <note-figstyle-20261113/runs/family4/pickles> <out dir> <figure stem> [...]
       (matplotlib 3.10.8, the version the pickles were written by)

For each figure named: the pinned pickle is loaded only through restyle_family4.load(), which checks its sha256 first
and reads the file; no pickle byte is changed. Then:
1. labels.tsv (figure, axes index, kind, text): kind "ylabel" sets that axes' empty y label (the run stops if it has
   one); kind "above" adds a text centred above the axes. Made before the palette edits, so a y label takes the
   power of ten as the other labels do;
2. the palette pass's edits (note-figstyle-20261117/tools/palette_lib.apply), as for the installed file;
3. texts.tsv's replacements for the figure (layout_lib.fix_texts; each must be found);
4. restyle_family4.restyle(), unchanged, for the fonts and the printed size, as the installed figure was laid out.
Arm 0 is note-figstyle-20261117/tools/palette_family4.py, which reproduces the installed file. Run both under
capture_palette.py: every data item's full hash must be equal (compare.py), and the drawn strings may differ only by
the declared edits.
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[7]
OLD = ROOT / "docs/orchestration/state/2d-closeout/stageF/methods/note-figstyle-20261113/tools"
PAL = ROOT / "docs/orchestration/state/2d-closeout/stageF/methods/note-figstyle-20261117/tools"
sys.path[:0] = [str(OLD), str(PAL), str(HERE), str(ROOT)]
import layout_lib  # noqa: E402
import palette_lib  # noqa: E402
import restyle_family4 as rf4  # noqa: E402

LABELS = {}
for r in layout_lib.table("labels.tsv"):
    LABELS.setdefault(r[0], []).append((int(r[1]), r[2], r[3]))


def label(fig, name):
    for n, kind, text in LABELS.get(name, []):
        ax = fig.axes[n]
        if kind == "ylabel":
            if ax.get_ylabel():
                raise SystemExit(f"labels.tsv: {name} axes {n} already has a y label {ax.get_ylabel()!r}")
            ax.set_ylabel(text)
        elif kind == "above":
            ax.text(0.5, 1.02, text, transform=ax.transAxes, ha="center", va="bottom")
        else:
            raise SystemExit(f"labels.tsv: {name}: unknown kind {kind!r}")


def main():
    pdir, out, names = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3:]
    out.mkdir(parents=True, exist_ok=True)
    for name in names:
        fig = rf4.load(pdir / f"{name}.pdf.figpickle")
        label(fig, name)
        palette_lib.apply(fig, name, check_fit=False)
        layout_lib.fix_texts(fig, name)
        entries = palette_lib.legend_entries(fig)
        fig = rf4.restyle(fig, name)
        if palette_lib.legend_entries(fig) != entries:
            raise SystemExit(f"{name}: legend entries {entries} became {palette_lib.legend_entries(fig)}")
        fig.savefig(out / f"{name}.pdf")
        fig.savefig(out / f"{name}.png", dpi=200)
        plt.close(fig)
        print(f"[fix4] wrote {out / name}.pdf")


if __name__ == "__main__":
    main()

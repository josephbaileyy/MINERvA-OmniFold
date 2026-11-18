#!/usr/bin/env python3
"""Figs. 19-22 in the note palette (arm 1): the family-4 pickles, with the record's edits, then restyled as installed.

usage: python3 palette_family4.py <pickle dir> <out dir>    (matplotlib 3.10.8, the version the pickles were written by)

For each pinned pickle (note-figstyle-20261113/tools/restyle_family4.py's PINNED, loaded only through its load(), which
checks the sha256 before unpickling): palette_lib.apply() (recolour.tsv, restyle.tsv, hatches.tsv, text_fixes.tsv,
the notation, frameless legends, the power of ten in the label), then restyle_family4.restyle(), unchanged, for the
fonts and the printed size, as for the installed figures; a legend entry lost by that restyle stops the recipe.
No datum changes: compare.py checks the arm-1 capture against arm 0 on the colour- and style-free hash.
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[7]
OLD = ROOT / "docs/orchestration/state/2d-closeout/stageF/methods/note-figstyle-20261113/tools"
sys.path[:0] = [str(OLD), str(HERE), str(ROOT)]
import restyle_family4 as rf4  # noqa: E402
import palette_lib  # noqa: E402


def main():
    pdir, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    for fname in rf4.PINNED:
        name = fname[: -len(".pdf.figpickle")]
        fig = rf4.load(pdir / fname)
        palette_lib.apply(fig, name, check_fit=False)   # restyle() lays the figure out again below
        entries = palette_lib.legend_entries(fig)
        fig = rf4.restyle(fig, name)
        if palette_lib.legend_entries(fig) != entries:
            raise SystemExit(f"{name}: legend entries {entries} became {palette_lib.legend_entries(fig)}")
        fig.savefig(out / f"{name}.pdf")
        fig.savefig(out / f"{name}.png", dpi=200)
        plt.close(fig)
        print(f"[palette4] wrote {out / name}.pdf")


if __name__ == "__main__":
    main()

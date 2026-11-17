#!/usr/bin/env python3
"""Family 4's print-style recipe: the four RE-1 central-value redraws, restyled from their figure pickles (note figure
style, group C; the director's method ruling of 2026-11-15: figure pickles for producers that must not change).

usage: python3 restyle_family4.py <pickle dir> <out dir>     (matplotlib 3.10.8, the version the pickles were written by)

Provenance of the pickles (runs/family4/): written on the cluster by tools/capture_pickle.py around
  nd-unfolding/re1/redraw_central_only_p3.py --only generators modedecomp mec, and
  nd-unfolding/re1/redraw_central_only_p4.py --only ascencio,
both unchanged, at the deploy e6f4d7afb74978be4eeb5439995f6c3fc1310eeb, on the nine inputs of RE-1 run 2's F2 job:
  P3 xsec_3d_p3.root c16b622b4970800121b1d92dad91407878e0f4546375bfe27cdd3257d46d8c63,
  P4 xsec_4d_p4.root ece4055e29756eeef81932b93199d507ca69296bbe7a90b2776c0c39a330998e,
  the Ascencio supplement 748afa9235f7e06b6415f213109106011ea6afa70ba8738d30e90c78a2fbde5a,
  Stage-7 genie_cv 8d417234dd33de2b0944d1bb9a75d5f888fa95c5ad0a02d4f71048a5bd410e3c,
  tunev1 2d3b6bedf496b1c213861affdc36fad8288216ebb7f41f72527d80abf1fb0e09,
  nuwro e728f0893cc6d0bf4e8355279fe46b9c6a458cedbbc79877e42cb49a62d26374,
  gibuu a54035aa96b587ad6b04e518138ea48fa0517954c77c317b56d85a4f626c7b24,
  modes 16962b6d0b7c5fc05035507603f941cef6678e3a57adf3cac8aeb35766b2dfcc,
  mec 38552e52ee706e1ee69dfe30de39a4572923e9738dfdd390206e1e45bf1e9f3e.

Loading a pickle runs code, so this recipe unpickles only the files in PINNED, and only when the file's sha256 equals
the pinned one; any other file, or a mismatch, stops it before anything is loaded.

The restyle changes no data artist (data, colours, markers, line styles: checked against the cluster capture by the
caller). It sets the paper's fonts (note_print_style: DejaVu Serif with Computer Modern maths) on every text, sets axis
labels to 9.3 pt, tick labels to 8.3 pt and every other text to 8.5 pt, resizes the canvas to the printed width
(sec_3d.tex's \\includegraphics), and lays the figure out again with tight_layout.
"""
import hashlib
import pickle
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.text import Text  # noqa: E402

PINNED = {  # file name: sha256, from runs/family4/pickles/PICKLES.tsv (matplotlib 3.10.8)
    "generators_vs_unfolded_band_central.pdf.figpickle": "720a350efb64bf57bef15e6337a23783f351ac36a14485614bdf47adfde0d714",
    "mode_decomp_eavail_central.pdf.figpickle": "5c3c6cea96c04a8c9d301129ee999e8a69779123a654ea7104f5e43aefdb5349",
    "compare_mec_eavail_central.pdf.figpickle": "846b3277db722600be9b5aa315b1d6b192584fc5d4c56b91cc8e0017886982e9",
    "ascencio_fullcov_compare_central.pdf.figpickle": "34a6bfb35fa43623f310694ac43629552d2462e6d57bf399c841c2ca1eb0e7cf",
}
# printed width as a fraction of the note's text width (sec_3d.tex), and the canvas aspect (height / width)
LAYOUT = {
    "generators_vs_unfolded_band_central": (0.99, 0.44),
    "mode_decomp_eavail_central": (0.49, 1.3),
    "compare_mec_eavail_central": (0.49, 0.8),
    "ascencio_fullcov_compare_central": (0.85, 0.6),
}
# per figure at the printed size: the largest marker size kept (markersize is not a hashed field), and where the
# legend goes ("below": one figure legend under the panels, in ncol columns; None: left where the producer put it)
MARKER_MAX = {"generators_vs_unfolded_band_central": 3.0, "ascencio_fullcov_compare_central": 4.0}
LEGEND_BELOW = {"generators_vs_unfolded_band_central": 5, "mode_decomp_eavail_central": 1,
                "ascencio_fullcov_compare_central": 2}
SIZE_LABEL, SIZE_TICK, SIZE_TEXT = 9.3, 8.3, 8.5


def load(path):
    path = Path(path)
    want = PINNED.get(path.name)
    if want is None:
        raise SystemExit(f"REFUSE: {path.name} is not a pinned pickle")
    blob = path.read_bytes()
    got = hashlib.sha256(blob).hexdigest()
    if got != want:
        raise SystemExit(f"REFUSE: {path.name} sha256 {got} is not the pinned {want}")
    return pickle.loads(blob)


def restyle(fig, name):
    root = Path(__file__).resolve().parents[8]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    import note_print_style as nps
    nps.apply()
    for ax in fig.axes:
        ax.tick_params(labelsize=SIZE_TICK, labelfontfamily="serif")
        for lab in ax.get_xticklabels() + ax.get_yticklabels():
            lab.set_fontfamily("serif"); lab.set_math_fontfamily("cm")
        for t in (ax.xaxis.label, ax.yaxis.label):
            t.set_fontfamily("serif"); t.set_math_fontfamily("cm"); t.set_fontsize(SIZE_LABEL)
        for t in (ax.xaxis.get_offset_text(), ax.yaxis.get_offset_text()):
            t.set_fontfamily("serif"); t.set_math_fontfamily("cm"); t.set_fontsize(SIZE_TICK)
    done = set()
    for ax in fig.axes:
        done |= {id(x) for x in ax.get_xticklabels() + ax.get_yticklabels() + [ax.xaxis.label, ax.yaxis.label,
                                                                                ax.xaxis.get_offset_text(),
                                                                                ax.yaxis.get_offset_text()]}
    for t in fig.findobj(Text):
        if id(t) in done:
            continue
        t.set_fontfamily("serif"); t.set_math_fontfamily("cm"); t.set_fontsize(SIZE_TEXT)
    cap = MARKER_MAX.get(name)
    if cap is not None:
        from matplotlib.lines import Line2D
        for ln in fig.findobj(Line2D):
            if ln.get_markersize() > cap:
                ln.set_markersize(cap)
    frac, aspect = LAYOUT[name]
    fig.set_size_inches(*nps.figsize(frac, aspect))
    ncol = LEGEND_BELOW.get(name)
    if ncol is None:
        fig.tight_layout()
        return fig
    handles, labels = [], []
    for ax in fig.axes:
        leg = ax.get_legend()
        if leg is not None:   # the axes' own labelled artists (containers included), in the legend's order
            want = [t.get_text() for t in leg.get_texts()]
            h, l = ax.get_legend_handles_labels()
            pick = dict(zip(l, h))
            handles += [pick[x] for x in want if x in pick]; labels += [x for x in want if x in pick]
            leg.remove()
    rows = -(-len(labels) // ncol)
    fig.legend(handles, labels, loc="lower center", ncol=ncol, frameon=False, fontsize=SIZE_TEXT,
               bbox_to_anchor=(0.5, 0.0), handlelength=1.6, columnspacing=1.0)
    height_in = fig.get_size_inches()[1]   # one legend row is about 1.45 x the text size; keep that band free
    fig.tight_layout(rect=(0, (rows * 1.45 * SIZE_TEXT / 72 + 0.06) / height_in, 1, 1))
    return fig


def main():
    pdir, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    for fname in PINNED:
        name = fname[: -len(".pdf.figpickle")]
        fig = restyle(load(pdir / fname), name)
        fig.savefig(out / f"{name}.pdf")
        fig.savefig(out / f"{name}.png", dpi=200)
        plt.close(fig)
        print(f"[restyle4] wrote {out / name}.pdf")


if __name__ == "__main__":
    main()

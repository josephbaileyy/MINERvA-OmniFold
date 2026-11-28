"""C2-CORR's note figure: the eigenvalue spectra of the three statistical covariances on the 205 published bins, drawn
from the committed record only (tier3-design, 2026-11-27; Joseph's "can we try both the sentence and figure?").

usage: python3 -I -B c2_corr_figure.py [--record RECORD.json] [--out PDF]

It reads run-corr/c2_corr.json beside this file and refuses unless the record's sha256 is RECORD_SHA, its status is
OK and every C2-CORR and C2-EFF control passed. It plots record["figure_spectra"] as stored, with no recomputation,
and writes docs/analysis-note/figures/c2_corr_spectra.pdf by default. It refuses an existing output path.

Style: the note's print style (note_print_style.apply(), the paper's rcParams with DejaVu Serif), sized for printing at
0.49 of the text width like tension_spectrum. Series identities follow restyle_2026_10.PALETTE where one exists:
OmniFold ("This work") is red #FF0000 with a solid line, and the published covariance is black with a dashed line.
The note has no IBU series identity, so IBU is Okabe-Ito bluish green #009E73 with a dash-dot line. It is chosen to
be distinct from the red, the black and Tune v1's blue under colour-vision deficiency, and can be changed by the note
lane. Wording beyond the legend and axis labels (the caption) is the note lane's.
"""
import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.environ.get("C2_EFF_REPO") or os.path.abspath(os.path.join(HERE, *[".."] * 7))
RECORD = os.path.join(HERE, "run-corr", "c2_corr.json")
RECORD_SHA = "a084016f876e2faf6dd7064a95c1de8396527c4e401519058fff6f7c9a392a0d"
OUT = os.path.join(REPO, "docs", "analysis-note", "figures", "c2_corr_spectra.pdf")
WIDTH_FRAC, ASPECT = 0.49, 0.78
SERIES = (  # record key, legend, colour, line style, line width
    ("C_IBU_K10", "IBU, ten iterations (same bootstrap draws)", "#009E73", "-.", 1.1),
    ("C_OF", "OmniFold (statistical covariance)", "#FF0000", "-", 1.1),
    ("StatOnly", "MINERvA published statistical covariance", "#000000", "--", 1.0),
)


class Refused(Exception):
    pass


def load(record: str, want_sha: str) -> dict:
    with open(record, "rb") as f:
        b = f.read()
    got = hashlib.sha256(b).hexdigest()
    if got != want_sha:
        raise Refused(f"the record's sha256 is {got}, not {want_sha}")
    rec = json.loads(b.decode())
    if rec.get("status") != "OK":
        raise Refused(f"the record's status is {rec.get('status')!r}")
    ctl = list(rec.get("controls", {}).values()) + list(rec.get("c2_eff_controls", {}).values())
    if not ctl or not all(c.get("pass") is True for c in ctl):
        raise Refused("not every control in the record passed")
    spec = rec.get("figure_spectra", {})
    for key, *_ in SERIES:
        lam = spec.get(key)
        if not isinstance(lam, list) or len(lam) != 205 or not all(isinstance(x, float) for x in lam):
            raise Refused(f"figure_spectra[{key!r}] is not 205 floats")
        if any(b2 > a for a, b2 in zip(lam, lam[1:])):
            raise Refused(f"figure_spectra[{key!r}] is not in descending order")
        if lam[-1] <= 0:
            raise Refused(f"figure_spectra[{key!r}] has a non-positive eigenvalue, which a log axis cannot show")
    return rec


def draw(rec: dict, out: str, keep: bool = False):
    sys.path.insert(0, REPO)
    import note_print_style as nps
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    nps.apply()
    fig, ax = plt.subplots(figsize=nps.figsize(WIDTH_FRAC, ASPECT))
    for key, label, colour, ls, lw in SERIES:
        lam = rec["figure_spectra"][key]
        ax.semilogy(range(1, len(lam) + 1), lam, color=colour, ls=ls, lw=lw, label=label)
    ax.set_xlabel("Eigenvalue rank")
    ax.set_ylabel(r"Eigenvalue [(cm$^2$/(GeV/$c$)$^2$)$^2$]")
    ax.set_xlim(0, 206)
    ax.legend(frameon=False, fontsize=6.5, loc="lower left", bbox_to_anchor=(0.0, 1.01), ncol=1, borderaxespad=0.0,
              handlelength=2.0)
    fig.tight_layout(pad=0.3)
    fig.savefig(out, metadata={"CreationDate": None, "ModDate": None, "Producer": None, "Creator": None})
    if keep:
        return fig
    plt.close(fig)
    return None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--record", default=RECORD)
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args(argv)
    if os.path.lexists(a.out):
        print(f"refusing: {a.out} exists")
        return 2
    try:
        rec = load(a.record, RECORD_SHA)
    except (Refused, OSError, ValueError) as e:
        print(f"C2-CORR FIGURE REFUSED: {type(e).__name__}: {e}")
        return 3
    draw(rec, a.out)
    with open(a.out, "rb") as f:
        print(f"C2-CORR FIGURE OK {hashlib.sha256(f.read()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

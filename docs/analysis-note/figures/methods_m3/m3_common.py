"""Shared inputs, hash checks and journal style for the M3 methods-paper figures.

Every input is a committed receipt under docs/orchestration/state/ of the repository checkout given by
--repo (default: the M3 detached worktree at origin/main c5aa0e90). Each is opened only after its sha256
matches the value recorded here, so a figure cannot be drawn from different bytes than REPORT.md lists.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

DEFAULT_REPO = Path("/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/"
                    "ee772d13-75a3-4217-970c-8badb94dd2ba/scratchpad/wt-m3")

INPUTS = {
    "d1_summary": ("docs/orchestration/state/s5c/d1/d1_summary.json",
                   "f5c802e37bf196ed0c1ecbf2414decb7fa0f2bbc0459ca3422c191c26f4a3c44"),
    "s5n_dev": ("docs/orchestration/state/s5n/stage1/dev_receipt.json",
                "1ef4096c39e2cfb2ded7d7e70c649eebcea09fbd0b31dca97e7b9d16c9878526"),
    "s5n_truth": ("docs/orchestration/state/s5n/stage1/truth_check.json",
                  "14ee280030f326484222da56245507006a1533f4f0e41e778823ab586a95c046"),
    "s5e_assess": ("docs/orchestration/state/s5e/cand/assess_receipt.json",
                   "84266e309d1aae0d2db1db315750b8164413a7d0125fcaa4a6c9b25834261a2c"),
    "tier_s": ("docs/orchestration/state/s5c/tier_s/interim_400.json",
               "aa574c17756ac9cea55306a731728104f7e084621372c8941c91bd9d0aab031f"),
}

# (E_avail, W) projection binning (nd-unfolding/project_cov_nd.py AXIS_EDGES); EW index = 6 * i_Eavail + i_W.
EAVAIL_EDGES = [0.0, 0.1, 0.2, 0.4, 0.8, 1.5, 3.0, 100.0]
W_EDGES = [0.0, 1.1, 1.4, 1.8, 2.2, 3.0, 100.0]
N_W = len(W_EDGES) - 1
N_EW = (len(EAVAIL_EDGES) - 1) * N_W

BLUE, RED, GREEN, PURPLE, GREY = "#2a78d6", "#c0392b", "#1baf7a", "#4a3aa7", "0.55"
PDF_META = {"CreationDate": None}


def parse_args(doc: str, default_out: Path) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=doc.split("\n", 1)[0])
    ap.add_argument("--repo", type=Path, default=DEFAULT_REPO, help="checkout holding the committed receipts")
    ap.add_argument("--outdir", type=Path, default=default_out)
    return ap.parse_args()


def load(repo: Path, key: str) -> dict:
    rel, want = INPUTS[key]
    path = repo / rel
    got = hashlib.sha256(path.read_bytes()).hexdigest()
    if got != want:
        raise SystemExit(f"sha256 mismatch for {path}: {got} != {want}")
    return json.loads(path.read_text())


def style() -> None:
    """The article's figure style (publication/release/figs/make_figs.py style())."""
    plt.rcParams.update({"font.family": "serif", "mathtext.fontset": "cm", "font.size": 8,
                         "axes.labelsize": 8.5, "xtick.labelsize": 7.5, "ytick.labelsize": 7.5,
                         "legend.fontsize": 7.0, "axes.linewidth": 0.6, "pdf.fonttype": 42})


def ew_axis(ax, label_rows: bool = True) -> None:
    """Index axis over the 42 (E_avail, W) cells, grouped by E_avail bin; ticks name the W bin."""
    for k in range(1, len(EAVAIL_EDGES) - 1):
        ax.axvline(k * N_W - 0.5, color="0.8", lw=0.5, zorder=0)
    ax.set_xlim(-0.5, N_EW - 0.5)
    ax.set_xticks(range(N_EW))
    ax.set_xticklabels([str(i % N_W + 1) for i in range(N_EW)], fontsize=5.5)
    if label_rows:
        for k in range(len(EAVAIL_EDGES) - 1):
            lo, hi = EAVAIL_EDGES[k], EAVAIL_EDGES[k + 1]
            txt = f"{lo:g}–{hi:g}" if hi < 100 else rf"$\geq${lo:g}"
            ax.text(k * N_W + (N_W - 1) / 2, 1.0, txt, transform=ax.get_xaxis_transform(), ha="center",
                    va="bottom", fontsize=6.0, color="0.3")


def ew_xlabel() -> str:
    return (r"$(E_{\rm avail},W)$ cell: $W$ bin 1–6 within each $E_{\rm avail}$ bin (GeV, top); "
            r"$W$ edges 0, 1.1, 1.4, 1.8, 2.2, 3, $\infty$ GeV")


def save(fig, outdir: Path, stem: str) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    fig.savefig(outdir / f"{stem}.pdf", metadata=PDF_META)
    fig.savefig(outdir / f"{stem}.png", dpi=200)
    plt.close(fig)


def check(label: str, ok: bool, value) -> dict:
    """Record a reproduced paper number; stop the figure if it does not reproduce."""
    print(f"[{'OK' if ok else 'MISMATCH'}] {label}: {value}")
    if not ok:
        raise SystemExit(f"paper number does not reproduce: {label} = {value}")
    return {"claim": label, "value": value}

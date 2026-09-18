#!/usr/bin/env python3
"""Slide figure: throughput and the verification apparatus, per month, from git.

WHAT THIS PLOTS. Two panels over the same six-month axis:

  (A) commits per month -- the throughput measure, and the one the talk immediately
      disowns as a productivity number (slide 3). It is here because the DISCONTINUITY
      is the subject, not the level.
  (B) verification files ADDED per month, split into test files and guard-named
      executables -- the apparatus built in response.
  (C) verification SHARE of code lines added per month. This panel is the one that
      TESTS the talk's thesis rather than illustrating it: "verification is the binding
      constraint" predicts the share rises. It could have come out flat. It did not.
      The 2026-06 dip to 1.2% breaks monotonicity and is drawn, not smoothed.

WHY TWO PANELS AND NOT TWO LINES ON ONE AXIS. Panel A's August value is 2,177 and
panel B's largest is 95. On a shared axis panel B is invisible; on a dual axis the
reader infers a correlation from an arbitrary scale choice. Two panels, one axis each.

THE 2026-08-12 MARK. Lane A (orchestrator), Lane B (uncertainty), Lane C (PET) and
Lane D (verifier) all make their first commit that day. It is drawn as an annotation,
not a fitted breakpoint -- nothing here tests for a changepoint.

POPULATIONS, STATED BECAUSE THE TALK IS ABOUT GETTING THESE WRONG.
  * Commits: `git log` on the current branch. Not deduplicated across merges.
  * Test files: paths matching `test_*.py` at ADD time (`--diff-filter=A`), tracked
    only. A `find` walk over the working tree instead returns 494 rather than the 128
    tracked today, because it sweeps `__pycache__`, vendored code and untracked
    scratch -- and `.claude/worktrees/` triplicates every lane checkout.
  * Guard files: `.py`/`.sh` paths whose name contains "guard", case-insensitive, at
    ADD time. This UNDERCOUNTS the apparatus: guards that live inside a larger module
    have no such path. It is a lower bound and the caption says so.

THE SELF-CHECK IS AN IDENTITY ON CLOSED MONTHS AND AN OBSERVATION ON THE CURRENT ONE.
Closed months are asserted byte-for-byte against RECORDED below; a mismatch is a hard
exit 3 telling you to update the table and name the reason in the same commit. The
CURRENT month is printed but NOT asserted, because the repository deliberately changes
it every day -- asserting equality across a boundary the system deliberately moves is
the exact defect on slide 5's fourth row. An empty git result is CANNOT CHECK (exit 2),
never agreement: a tally of zero may mean the command could not look.
"""
import re
import subprocess
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "verification_apparatus.png"

MONTHS = ("2026-04", "2026-05", "2026-06", "2026-07", "2026-08", "2026-09")
CURRENT_MONTH = "2026-09"          # printed, never asserted -- see the docstring

# RECORDED 2026-09-08 on this checkout. Closed months are an IDENTITY, not a floor:
# a change here is a real change and must be re-derived and named, not absorbed.
RECORDED = {
    "commits": {"2026-04": 9, "2026-05": 50, "2026-06": 92,
                "2026-07": 272, "2026-08": 2177, "2026-09": 239},
    "tests":   {"2026-04": 0, "2026-05": 0, "2026-06": 4,
                "2026-07": 31, "2026-08": 95, "2026-09": 10},
    "guards":  {"2026-04": 0, "2026-05": 0, "2026-06": 0,
                "2026-07": 2, "2026-08": 12, "2026-09": 5},
    # tenths of a percent, so the identity check stays on integers
    "share":   {"2026-04": 0, "2026-05": 41, "2026-06": 12,
                "2026-07": 204, "2026-08": 448, "2026-09": 618},
}
CODE = (".py", ".sh", ".C", ".cc", ".h")
VERIF_TOKENS = ("test_", "probe-", "guard", "ratchet", "verify_", "_check", "preflight")

# --- design tokens (dataviz reference palette, light surface; validated) -----------
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#e4e3df"
BLUE = "#2a78d6"      # categorical slot 1 -- panel A, single series
ORANGE = "#eb6834"    # slot 2 -- test files
AQUA = "#1baf7a"      # slot 3 -- guard files (2.74:1 on this surface, so the relief
                      # rule applies: every bar carries a visible direct label)
VIOLET = "#4a3aa7"    # slot 7 -- panel C is a DIFFERENT measure (a share, not a count),
                      # so it does not reuse a count panel's hue


def _git(*args):
    out = subprocess.run(("git",) + args, cwd=REPO, capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(f"CANNOT CHECK :: git {' '.join(args)} exited {out.returncode}\n{out.stderr}")
    return out.stdout


def measure_commits():
    rows = [l for l in _git("log", "--format=%as").splitlines() if l.strip()]
    if not rows:
        sys.exit("CANNOT CHECK :: git log returned no rows. A tally of zero here means "
                 "the command could not look, not that there are no commits.")
    counts = {m: 0 for m in MONTHS}
    for line in rows:
        counts[line[:7]] = counts.get(line[:7], 0) + 1
    return counts


def measure_added(pattern, exts=None):
    """Count paths matching `pattern` at the commit that ADDED them, per month."""
    raw = _git("log", "--diff-filter=A", "--format=COMMIT %as", "--name-only")
    if not raw.strip():
        sys.exit("CANNOT CHECK :: no add-history returned.")
    counts = {m: 0 for m in MONTHS}
    month = None
    for line in raw.splitlines():
        if line.startswith("COMMIT "):
            month = line.split()[1][:7]
            continue
        p = line.strip()
        if not p or month is None:
            continue
        if exts and not p.endswith(exts):
            continue
        if pattern.search(p):
            counts[month] = counts.get(month, 0) + 1
    return counts


def measure_share():
    """Verification share of code lines added, in TENTHS OF A PERCENT (integer, so the
    identity check does not hinge on float formatting)."""
    raw = _git("log", "--format=COMMIT %as", "--numstat")
    if not raw.strip():
        sys.exit("CANNOT CHECK :: no numstat history returned.")
    acc = {m: [0, 0] for m in MONTHS}
    month = None
    for line in raw.splitlines():
        if line.startswith("COMMIT "):
            month = line.split()[1][:7]
            continue
        cols = line.split("\t")
        if len(cols) != 3 or cols[0] == "-" or month is None:
            continue
        path = cols[2]
        if not path.endswith(CODE):
            continue
        base = path.rsplit("/", 1)[-1].lower()
        verif = any(t in base for t in VERIF_TOKENS) or "guard" in path.lower()
        acc.setdefault(month, [0, 0])[0 if verif else 1] += int(cols[0])
    out = {}
    for m in MONTHS:
        v, sci = acc[m]
        out[m] = round(1000 * v / (v + sci)) if v + sci else 0
    return out


def self_check():
    live = {"commits": measure_commits(),
            "tests": measure_added(re.compile(r"(^|/)test_[^/]*\.py$")),
            "guards": measure_added(re.compile(r"guard", re.I), exts=(".py", ".sh")),
            "share": measure_share()}
    closed = [m for m in MONTHS if m != CURRENT_MONTH]
    bad = []
    for key, rec in RECORDED.items():
        for m in closed:
            if live[key].get(m, 0) != rec[m]:
                bad.append(f"  {key} {m}: recorded {rec[m]}, measured {live[key].get(m, 0)}")
    if bad:
        sys.exit("THE RECORDED TABLE MOVED on a CLOSED month.\n" + "\n".join(bad) +
                 "\nUpdate RECORDED and name the cause in the same commit. Do not "
                 "widen this into a floor.")
    print("SELF-CHECK :: closed months 2026-04..2026-08 reproduce RECORDED exactly")
    for key in ("commits", "tests", "guards", "share"):
        print(f"  {key:<8} {CURRENT_MONTH} live = {live[key].get(CURRENT_MONTH, 0):>5}"
              f"   (recorded {RECORDED[key][CURRENT_MONTH]}; OBSERVED, not asserted)")
    return live


def bars(ax, x, vals, color, label=None, width=0.38, offset=0.0):
    b = ax.bar(x + offset, vals, width=width, color=color, label=label,
               linewidth=1.6, edgecolor=SURFACE, zorder=3)
    for rect, v in zip(b, vals):
        if v == 0:
            continue
        ax.annotate(f"{v:,}", (rect.get_x() + rect.get_width() / 2, v),
                    textcoords="offset points", xytext=(0, 4), ha="center",
                    fontsize=13, color=INK, zorder=4)
    return b


def main():
    live = self_check()
    x = np.arange(len(MONTHS))
    labels = [m[5:] for m in MONTHS]
    labels[-1] += "\n(8 days)"

    fig, (a, b, c) = plt.subplots(1, 3, figsize=(18.4, 5.1), dpi=200)
    fig.patch.set_facecolor(SURFACE)

    for ax in (a, b, c):
        ax.set_facecolor(SURFACE)
        ax.yaxis.grid(True, color=GRID, linewidth=1.0, zorder=0)
        ax.set_axisbelow(True)
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)
        ax.spines["bottom"].set_color(GRID)
        ax.tick_params(axis="both", length=0, labelsize=13, colors=INK_2)
        ax.set_xticks(x)
        ax.set_xticklabels(labels)

    # --- panel A: throughput, single series, no legend (the title names it) --------
    bars(a, x, [live["commits"][m] for m in MONTHS], BLUE, width=0.62)
    a.set_title("Commits per month", fontsize=16, color=INK, pad=32, loc="left")
    a.set_ylim(0, 2620)
    # point at the bar's LEFT FLANK, not its top: the top carries the value label
    a.annotate("parallel agent lanes\nfirst commit 2026-08-12",
               xy=(3.70, 1430), xytext=(1.05, 1760), fontsize=12.5, color=INK_2,
               ha="left", va="center",
               arrowprops=dict(arrowstyle="-", color=INK_2, linewidth=1.2,
                               shrinkA=6, shrinkB=3))

    # --- panel B: apparatus, two series -> legend AND direct labels ----------------
    bars(b, x, [live["tests"][m] for m in MONTHS], ORANGE,
         label="test files added", offset=-0.20)
    bars(b, x, [live["guards"][m] for m in MONTHS], AQUA,
         label="guard files added", offset=+0.20)
    b.set_title("Verification files added per month", fontsize=16, color=INK,
                pad=32, loc="left")
    b.set_ylim(0, 118)
    leg = b.legend(frameon=False, fontsize=13, loc="upper left", handlelength=1.1)
    for t in leg.get_texts():
        t.set_color(INK_2)

    # --- panel C: the thesis test ------------------------------------------------
    share = [live["share"][m] / 10 for m in MONTHS]
    cb = c.bar(x, share, width=0.62, color=VIOLET, linewidth=1.6,
               edgecolor=SURFACE, zorder=3)
    for rect, v in zip(cb, share):
        c.annotate(f"{v:.1f}%", (rect.get_x() + rect.get_width() / 2, v),
                   textcoords="offset points", xytext=(0, 4), ha="center",
                   fontsize=13, color=INK, zorder=4)
    c.set_title("Verification share of code lines added", fontsize=16, color=INK,
                pad=32, loc="left")
    c.set_ylim(0, 78)
    c.annotate("the thesis predicts this rises.\nit could have come out flat",
               xy=(0.235, 1.0), xycoords="axes fraction", fontsize=12.5,
               color=INK_2, ha="left", va="top")

    fig.text(0.008, 0.012,
             "Commits: git log, current branch. Test files: test_*.py at add time, tracked only.\n"
             "Guard files: .py/.sh whose path contains \"guard\" -- a LOWER BOUND, since a guard "
             "inside a larger module has no such path.\n"
             "Verification share: numerator is code paths whose BASENAME matches "
             "test_/probe-/guard/ratchet/verify_/_check/preflight -- a proxy that errs BOTH ways, "
             "and the .md governance work is excluded entirely.\n"
             "September is 8 days, plotted as observed and not asserted. Re-derived from git at "
             "plot time; closed months are pinned as an identity. Nothing here tests for a changepoint.",
             fontsize=10.0, color=INK_2, va="bottom", linespacing=1.45)

    fig.tight_layout(rect=(0, 0.125, 1, 1))
    fig.savefig(OUT, facecolor=SURFACE)
    print(f"WROTE {OUT}  ({OUT.stat().st_size / 1024:.0f} KiB)")


if __name__ == "__main__":
    main()

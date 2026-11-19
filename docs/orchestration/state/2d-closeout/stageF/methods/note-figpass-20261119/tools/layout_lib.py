"""The note figure pass's layout edits (cov2d, 2026-11-19): presentation only, on a drawn figure.

apply(fig, name) makes, after the palette pass's own edits (note-figstyle-20261117/tools/palette_lib.apply), every
layout edit this record's tables declare for the figure named by its saved file's stem, in order:
0. every axis keeps the ticks and tick labels it drew (freeze_ticks);
0b. texts.tsv (figure, old, new): each replacement in any drawn text of the figure (titles, labels, texts, legend
   entries, tick labels); each must be found at least once, or the run stops. A wording fix, declared row by row;
1. layout.tsv (figure, width in, height in, text scale, text floor pt): every text's size is multiplied by the scale
   and then raised to the floor if it is below it (tick labels through their axis, so new ticks keep the size); the
   canvas is set to the printed size. A size in points then prints at that size when the PDF is included at its
   natural width (the class widths in widths.tsv).
2. ticks.tsv (figure, axes index, axis x|y, rotation, ha): a tick-label rotation and alignment.
3. boxes.tsv (figure, axes index, x0, y0, width, height; inches from the canvas's lower left; optionally a title pad
   in points): each named axes is placed in that box, and its titles are drawn that far above it. A figure with no
   boxes row is laid out again with tight_layout(). A row with axes index -1 keeps every axes where the producer put it.
4. moves.tsv (figure, text prefix, dx, dy; data units): each drawn text (an annotation's text included) that starts
   with the prefix is moved by (dx, dy); each prefix must match exactly one text. Position only.
Nothing else changes: no datum, colour, style or string. The arms check this: the capture's item hashes (data, colours
and styles) and the multiset of drawn strings must equal the palette arm's (tools/arms_layout.sh).
"""
from pathlib import Path

from matplotlib.text import Text

HERE = Path(__file__).resolve().parent
REC = HERE.parent


def table(name):
    p = REC / name
    if not p.exists():
        return []
    rows = [ln.split("\t") for ln in p.read_text().splitlines() if ln.strip() and not ln.startswith("#")]
    return rows[1:]


LAYOUT = {r[0]: (float(r[1]), float(r[2]), float(r[3]), float(r[4])) for r in table("layout.tsv")}
TEXTS = {}
for r in table("texts.tsv"):
    TEXTS.setdefault(r[0], []).append((r[1].replace("\\n", "\n"), r[2].replace("\\n", "\n")))
MOVES = {}
for r in table("moves.tsv"):
    MOVES.setdefault(r[0], []).append((r[1], float(r[2]), float(r[3])))
TICKS = {}
for r in table("ticks.tsv"):
    TICKS.setdefault(r[0], []).append((int(r[1]), r[2], float(r[3]), r[4]))
BOXES = {}
for r in table("boxes.tsv"):
    BOXES.setdefault(r[0], []).append((int(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5]),
                                       float(r[6]) if len(r) > 6 and r[6].strip() else None))
for name in set(TICKS) | set(BOXES):
    if name not in LAYOUT:
        raise SystemExit(f"ticks.tsv / boxes.tsv name {name}, which layout.tsv does not")


def sizes(fig, scale, floor):
    ticks = {}   # each axis's tick-label size, read before anything is scaled
    for ax in fig.axes:
        for which, axis in (("x", ax.xaxis), ("y", ax.yaxis)):
            major = axis.get_major_ticks()
            if major:
                ticks[(id(ax), which)] = major[0].label1.get_fontsize()
    for t, size in [(t, t.get_fontsize()) for t in fig.findobj(Text)]:
        t.set_fontsize(max(size * scale, floor))
    for ax in fig.axes:
        for which in ("x", "y"):
            if (id(ax), which) in ticks:
                ax.tick_params(axis=which, which="both", labelsize=max(ticks[(id(ax), which)] * scale, floor))


def freeze_ticks(fig):
    """Each axis keeps the major ticks and tick labels it drew (a FixedLocator and FixedFormatter of what the drawn
    figure shows), so a new size cannot re-choose them. An axis showing an offset text ("1e-38") is left as it is,
    since a fixed formatter would drop the offset; the string check then sees any change."""
    from matplotlib.ticker import FixedFormatter, FixedLocator
    fig.canvas.draw()
    for ax in fig.axes:
        for axis in (ax.xaxis, ax.yaxis):
            if axis.get_offset_text().get_text().strip():
                continue
            locs = list(axis.get_majorticklocs())
            labels = [t.get_text() for t in axis.get_majorticklabels()]
            axis.set_major_locator(FixedLocator(locs))
            axis.set_major_formatter(FixedFormatter(labels))


def fix_texts(fig, name):
    """texts.tsv's replacements for this figure, in every drawn text; each must be found."""
    rows = TEXTS.get(name, [])
    used = set()
    for t in fig.findobj(Text):
        s = t.get_text()
        for i, (old, new) in enumerate(rows):
            if old in s:
                s = s.replace(old, new)
                used.add(i)
        if s != t.get_text():
            t.set_text(s)
    missing = [rows[i] for i in range(len(rows)) if i not in used]
    if missing:
        raise SystemExit(f"texts.tsv: {name}: not found in the figure: {missing}")


def apply(fig, name):
    if name not in LAYOUT:
        return False
    w, h, scale, floor = LAYOUT[name]
    freeze_ticks(fig)
    fix_texts(fig, name)
    sizes(fig, scale, floor)
    for n, which, rot, ha in TICKS.get(name, []):
        ax = fig.axes[n]
        labels = ax.get_xticklabels() if which == "x" else ax.get_yticklabels()
        for t in labels:
            t.set_rotation(rot)
            t.set_ha(ha)
    fig.set_size_inches(w, h)
    if name in BOXES and any(b[0] == -1 for b in BOXES[name]):
        pass   # keep the producer's axes positions
    elif name in BOXES:
        names = {b[0] for b in BOXES[name]}
        if len(names) != len(BOXES[name]) or max(names) >= len(fig.axes):
            raise SystemExit(f"boxes.tsv: {name}: axes {sorted(names)} against {len(fig.axes)} axes")
        for n, x0, y0, bw, bh, pad in BOXES[name]:
            fig.axes[n].set_position([x0 / w, y0 / h, bw / w, bh / h])
            if pad is not None:   # the axes' title offset (points), as set_title(pad=) sets it; the title texts stay
                fig.axes[n]._set_title_offset_trans(pad)
    else:
        fig.tight_layout()
    for prefix, dx, dy in MOVES.get(name, []):
        hit = [t for t in fig.findobj(Text) if t.get_text().startswith(prefix)]
        if len(hit) != 1:
            raise SystemExit(f"moves.tsv: {name}: {len(hit)} texts start with {prefix!r}")
        x, y = hit[0].get_position()
        hit[0].set_position((x + dx, y + dy))
    return True

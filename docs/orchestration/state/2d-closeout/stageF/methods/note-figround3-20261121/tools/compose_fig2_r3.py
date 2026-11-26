#!/usr/bin/env python3
"""Fig. 2 (fig:xsec: MEFHC_5iter_xsec_proj_pt, _proj_pz): round 3 of 2026-11-21 (Joseph and the rewrite helper).

usage (as compose_fig2_round.py: under remap_anc.py, optionally capture_palette.py, in figenv/rootmpl3108):
  FIG2_R3_JSON=<record.json> FIG2_ROUND_JSON=<r2 record> python3 remap_anc.py <anc> compose_fig2_r3.py <xsec> <anc> <out>

Runs note-figround-20261121/tools/compose_fig2_round.py (the installed recipe) with one more wrapper under it. At
each projection's save, after the earlier edits:
- the published prediction ("Tune v1: published prediction", a dashed line on the projection's edges) is drawn black,
  above the prior's solid blue histogram (z-order), as before the restyle; it was blue dashed and hard to see on the
  prior. Its data, dashes and width are kept;
- the legend (p_par panel only) reads "MINERvA Tune v1 prior" for "Tune v1: our simulation (the prior)" and
  "MINERvA Tune v1 published prediction" for "Tune v1: published prediction"; it is rebuilt in place (same location, size and
  order) so that its handles show the new line colour.
Checks (each failure stops the run): every datum unchanged; the legend covers no plotted vertex; no text overlap at
the final draw.
"""
import json
import os
import runpy
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
METHODS = HERE.parents[1]
sys.path.insert(0, str(METHODS / "note-figpass-20261119/tools"))
import compose_tier2 as ct  # noqa: E402
from matplotlib.patches import StepPatch  # noqa: E402
from matplotlib.text import Text  # noqa: E402

PROJ = ("MEFHC_5iter_xsec_proj_pt", "MEFHC_5iter_xsec_proj_pz")
R2 = METHODS / "note-figround-20261121/tools/compose_fig2_round.py"
RENAME = {
    ct.PRIOR_NEW: "MINERvA Tune v1 prior",
    ct.ANC_NEW: "MINERvA Tune v1\npublished prediction",
}
DONE = {}


def data_state(fig):
    out = []
    for ax in fig.axes:
        for a in ax.get_children():
            if hasattr(a, "get_xydata"):
                out.append(np.asarray(a.get_xydata(), float).tobytes())
            elif isinstance(a, StepPatch):
                out.append(np.asarray(a.get_data().values, float).tobytes())
            elif hasattr(a, "get_segments"):
                out.append(b"".join(np.asarray(s, float).tobytes() for s in a.get_segments()))
    return out


def fix(fig, stem):
    top = fig.axes[0]
    before = data_state(fig)
    anc = [ln for ln in top.lines if ln.get_label() == ct.ANC_NEW]
    prior = [p for p in top.patches if isinstance(p, StepPatch) and p.get_label() == ct.TUNE]
    if len(anc) != 1 or len(prior) != 1:
        raise SystemExit(f"r3: {stem}: {len(anc)} published-prediction lines, {len(prior)} priors")
    ln = anc[0]
    style_before = {"color": ln.get_color(), "ls": ln.get_linestyle(), "lw": ln.get_linewidth(), "z": ln.get_zorder()}
    ln.set_color("black")
    ln.set_zorder(max(ln.get_zorder(), prior[0].get_zorder() + 0.1))
    leg = top.get_legend()
    rec = {"published_prediction_before": style_before,
           "published_prediction_after": {"color": "black", "ls": ln.get_linestyle(), "lw": ln.get_linewidth(), "z": ln.get_zorder()}}
    if leg is not None:
        labels = [t.get_text() for t in leg.get_texts()]
        if not set(RENAME) <= set(labels):
            raise SystemExit(f"r3: {stem}: legend {labels} lacks {list(RENAME)}")
        handles = leg.legend_handles
        fs = leg.get_texts()[0].get_fontsize()
        kw = {"loc": leg._loc, "frameon": leg.get_frame_on(), "ncol": leg._ncols, "fontsize": fs}
        bb = leg.get_bbox_to_anchor()
        leg.remove()
        # the original artists as handles, so the rebuilt legend shows the new colour (handles copy style at creation)
        # compose_tier2's relegend showed the prior's artist (label ct.TUNE) as ct.PRIOR_NEW; map back to artist labels
        back = {ct.PRIOR_NEW: ct.TUNE}
        h, lab_art = top.get_legend_handles_labels()
        pick = dict(zip(lab_art, h))
        hs = [pick.get(back.get(lab, lab)) for lab in labels]
        if any(h is None for h in hs):
            raise SystemExit(f"r3: {stem}: legend artists not found for {labels}")
        top.legend(hs, [RENAME.get(l, l) for l in labels], **kw)
        rec["legend"] = [RENAME.get(l, l) for l in labels]
    fig.canvas.draw(); rend = fig.canvas.get_renderer()
    if top.get_legend() is not None:
        lb = top.get_legend().get_window_extent(rend); pts = []
        for a in top.get_children():
            if hasattr(a, "get_xydata") and a.get_visible() and a.get_transform().contains_branch_seperately(top.transData)[0]:
                pts.append(a.get_transform().transform(np.asarray(a.get_xydata(), float)))
            elif isinstance(a, StepPatch):
                d = a.get_data(); e, v = np.asarray(d.edges, float), np.asarray(d.values, float)
                pts.append(top.transData.transform(np.column_stack([np.repeat(e, 2)[1:-1], np.repeat(v, 2)])))
        hit = sum(int(((p[:, 0] >= lb.x0) & (p[:, 0] <= lb.x1) & (p[:, 1] >= lb.y0) & (p[:, 1] <= lb.y1)).sum()) for p in pts)
        if hit:
            raise SystemExit(f"r3: {stem}: the legend covers {hit} plotted vertices")
    tl, dr = set(), set()
    for ax in fig.axes:
        for axis in (ax.xaxis, ax.yaxis):
            for tk in axis.get_major_ticks() + axis.get_minor_ticks():
                tl.update((id(tk.label1), id(tk.label2)))
            for tk in axis._update_ticks():
                dr.update(id(l) for l in (tk.label1, tk.label2) if l.get_visible())
    ts = [t for t in fig.findobj(Text) if t.get_visible() and t.get_text() and (id(t) not in tl or id(t) in dr)]
    lg = top.get_legend(); legt = set(id(t) for t in lg.get_texts()) if lg else set()
    bbs = [(t, t.get_window_extent(rend)) for t in ts]
    ov = [(a.get_text(), b.get_text()) for i, (a, ba) in enumerate(bbs) for b, bb in bbs[i + 1:]
          if ba.overlaps(bb) and not (id(a) in legt and id(b) in legt)]
    if ov:
        raise SystemExit(f"r3: {stem}: texts overlap: {ov}")
    if data_state(fig) != before:
        raise SystemExit(f"r3: {stem}: a datum changed")
    DONE[stem] = rec


def wrapped(self, fname, *a, **k):
    stem = Path(str(fname)).name.split(".")[0]
    if stem in PROJ and stem not in DONE:
        fix(self, stem)
    return _save(self, fname, *a, **k)


_save = ct._inner
ct._inner = wrapped
argv = sys.argv[1:]
sys.argv = [str(R2), *argv]
runpy.run_path(str(R2), run_name="__main__")
if set(DONE) != set(PROJ):
    raise SystemExit(f"r3: fixed {sorted(DONE)}, not both projections")
if os.environ.get("FIG2_R3_JSON"):
    Path(os.environ["FIG2_R3_JSON"]).write_text(json.dumps(DONE, indent=1) + "\n")
print(f"[compose_fig2_r3] {len(DONE)} projections: published prediction black dashed above the prior; legend renamed")

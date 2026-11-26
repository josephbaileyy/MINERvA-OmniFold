"""Check the read's section-B weight correction to the 365.3 bound and its Valencia-flux point.

Runs ../inputs/replay/replay.py in-process (its own assertions included) and reuses its
arrays; no input is modified.
"""

import contextlib
import io
import json
import runpy
from pathlib import Path

import numpy as np

REPLAY = Path(__file__).resolve().parent.parent / "inputs" / "replay"
with contextlib.redirect_stdout(io.StringIO()):
    s = runpy.run_path(str(REPLAY / "replay.py"))
bands, scale = s["_bands"], s["scale"]
rows = [json.loads(line) for line in (REPLAY / "full-phase-generated.jsonl").open()]
stats = [[b for b in r["stats"]] for r in rows]  # [playlist][true 60-80, >=80]


def total(f):
    return scale * np.sum([[f(b) for b in r] for r in stats], axis=0)


gen_t = total(lambda b: b["truth_w"])
gen_w2 = total(lambda b: b["truth_w2"]) * scale  # scale applies squared
sel_t = total(lambda b: b["selected"][1])
sel_r = total(lambda b: b["selected"][2])
dest_t = total(lambda b: np.array(b["reco"])[:, 1])  # destinations <40, 40-60, 60-80, >=80, outside
dest_r = total(lambda b: np.array(b["reco"])[:, 2])
np.testing.assert_allclose(dest_r[:, 1:4], s["dest"][:, 1:4, 2], rtol=1e-11)
np.testing.assert_allclose(gen_t, s["den"], rtol=1e-11)
np.testing.assert_allclose(dest_r.sum(1), sel_r, rtol=1e-11)

G, St, Sr = gen_t.sum(), sel_t.sum(), sel_r.sum()
in40_t, in40_r = dest_t[:, 1:4].sum(), dest_r[:, 1:4].sum()
print("## B. The 365.3 headroom (true >= 60 rows, all truth pT, data POT)")
print(f"generated (truth weights) {G:.3f} = {gen_t.round(3).tolist()}; MC stat +- {np.sqrt(gen_w2.sum()):.1f}")
print(f"selected anywhere: truth weights {St:.3f}, reco weights {Sr:.3f}, reco/truth {Sr / St:.5f}")
print(f"reco >= 40 destinations: truth weights {in40_t:.3f}, reco weights {in40_r:.3f}")
print(f"as coded, generated(truth w) - reco>=40(reco w)            {G - in40_r:.3f}")
print(f"  of which unselected (truth w)                            {G - St:.3f}")
print(f"  truth - reco weight on selected tracks                   {St - Sr:.3f}")
print(f"  selected, reco < 40 (reco w)                             {dest_r[:, 0].sum():.3f}")
print(f"  selected, outside reco acceptance (reco w)               {dest_r[:, 4].sum():.3f}")
print(f"truth weights on both sides                                {G - in40_t:.3f}")
print(f"reco weights on both sides, generated x (reco/truth on selected) {G * Sr / St - in40_r:.3f}")

print("\n## Valencia flux: in-domain reweighting only (flux.npz has no true >= 60 or background rows)")
names = ["20-40", "40-60", "60-80", ">=80"]
raw_nom = bands(s["m"].sum(1) + s["b"])
raw_val = bands(s["mf"].sum(1) + s["b"])
fold_nom, fold_val = bands(s["fold"]), bands(s["flux_fold"])
for i, n in enumerate(names):
    print(f"reco {n:>5}: raw MC nominal {raw_nom[i]:10.1f} Valencia {raw_val[i]:10.1f} diff {raw_val[i] - raw_nom[i]:+8.1f}"
          f" | in-grid fold nominal {fold_nom[i]:10.1f} Valencia {fold_val[i]:10.1f} diff {fold_val[i] - fold_nom[i]:+6.1f}")
fig2 = s["fig2"]["mc"]
print(f"Fig. 2 fine-copy Tune v1 MC at reco 40-60: {fig2:.1f}; nominal gap {fig2 - raw_nom[1]:.1f};"
      f" closed by Valencia {raw_val[1] - raw_nom[1]:.1f} ({(raw_val[1] - raw_nom[1]) / (fig2 - raw_nom[1]):.1%});"
      f" remaining {fig2 - raw_val[1]:.1f} ({(fig2 - raw_val[1]) / fig2:.1%} of Fig. 2)")
print(f"nominal true >= 60 feed held fixed inside b: {bands(s['g']['feed']).round(1).tolist()}")

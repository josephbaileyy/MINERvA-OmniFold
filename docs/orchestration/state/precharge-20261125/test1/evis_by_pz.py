"""Data/fold of good-curvature negative tracks on the (reco p_parallel, E_vis) plane.

All 12 playlists, merged-POT scaling. If the excess were a function of E_vis alone, the
ratio at fixed E_vis would not depend on the p_parallel band (up to migration).
"""

import numpy as np
import pandas as pd

from events import load

x = load()
g = x[(x.sign == "-") & (x.precision == "good")].copy()
g["w"] = np.where(g.is_data, 1.0, g.fold * g.merged_scale)
g["pzb"] = pd.cut(g.pz, [20, 40, 50, 60, 80, np.inf], right=False)
g["evb"] = pd.cut(g.evis, [20, 40, 45, 50, 55, 60, 70, 80, 100, np.inf], right=False)
d = g[g.is_data].pivot_table(index="pzb", columns="evb", values="w", aggfunc="sum", observed=False)
m = g[~g.is_data].pivot_table(index="pzb", columns="evb", values="w", aggfunc="sum", observed=False)
pd.set_option("display.width", 200)
print("data counts\n", d.fillna(0).astype(int).to_string())
print("\nfold\n", m.round(1).to_string())
print("\ndata/fold (cells with fold >= 5)\n", (d / m).where(m >= 5).round(2).to_string())

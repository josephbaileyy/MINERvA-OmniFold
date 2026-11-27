"""Remove changes of reconstructed momentum composition within each coarse band."""

import contextlib
import io
import runpy
from pathlib import Path
import json
import numpy as np

here = Path(__file__).resolve().parent
with contextlib.redirect_stdout(io.StringIO()):
    state = runpy.run_path(str(here / "score.py"))
fine = np.load(here / "fine.npz")
low = np.array([20, 30, 40, 50, 60, 65, 70, 75, 80, 90, 100, 120])
band = np.searchsorted([40, 60, 80], low, side="right")


def coarse(x):
    return np.stack([x[band == j].sum(0) for j in range(4)])


def submodels(train, test):
    _, _, factors = state["fit_and_predict"](train, test)
    mc = np.zeros((len(low), 3, 3, 226))
    data = np.zeros(mc.shape[:-1])
    for p in test:
        h = fine[p]
        np.testing.assert_allclose(coarse(h), state["events"][p], rtol=1e-11, atol=1e-7)
        dp, mp = state["archive"][p + "_pot"]
        mc += h[..., :226] * (dp / mp)
        data += h[..., 226]
    signal = mc[..., :224] * state["weight"]
    base = signal.sum(-1) + mc[..., 224:].sum(-1)
    response = np.zeros_like(data)
    for i, j in enumerate(band):
        use = (state["iz"] == 14) if j == 1 else (state["iz"] >= 14)
        if j > 0:
            response[i] = signal[i][..., use].sum(-1)
    return data, [
        base,
        base + (factors[0][band, None, None] - 1) * mc[..., 225],
        base + (factors[1][band, None, None] - 1) * response,
    ]


obs, models = submodels(state["training"], state["validation"])
report = {}
for c in ("curvature", "recoil"):
    k, n = state["selected_values"](obs, c)
    report[c] = {
        "observed": coarse(k).tolist(),
        "denominator": coarse(n).tolist(),
        "predicted": [],
    }
    for m in models:
        a, b = state["selected_values"](m, c)
        assert np.all(b[n > 0] > 0)
        report[c]["predicted"].append(coarse(n * state["ratio"](a, b)).tolist())
print(json.dumps(report, indent=2))

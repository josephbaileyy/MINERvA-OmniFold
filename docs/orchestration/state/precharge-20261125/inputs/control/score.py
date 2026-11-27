"""Compare held-out control distributions for two sources of excess counts."""

from pathlib import Path
import json
import numpy as np

here = Path(__file__).resolve().parent
previous = here.parent / "replay"
events = np.load(here / "quality.npz")
archive = np.load(previous / "playlists.npz")
feed = np.load(previous / "feed.npz")
ref = np.genfromtxt(previous / "cross-section.csv", delimiter=",", names=True)
prev = np.genfromtxt(previous / "reco-bands.csv", delimiter=",", names=True)
reported = ref["reported"] == 1


def ratio(n, d):
    return np.divide(n, d, out=np.zeros_like(n, dtype=float), where=d > 0)


weight = ratio(ref["unfolded_signed_K10"], ref["truth_generated"])
weight[reported] *= ratio(
    ref["published_xsec"], ref["xsec_cm2_per_nucleon_per_GeVc_squared"]
)[reported]
weight[reported] *= ratio(ref["selected_anywhere"], ref["selected_in_grid"])[reported]
periods = sorted(events.files)
training = periods[::2]
validation = periods[1::2]
iz = np.arange(224) % 16


def project(x):
    return np.r_[x[:224][iz == 14].sum(), x[:224][iz == 15].sum(), x[224:]]


def totals(names, individual=True):
    pot = np.array([archive[p + "_pot"] for p in names])
    mc = np.zeros_like(events[names[0]][..., :226])
    data = np.zeros(mc.shape[:3])
    for i, p in enumerate(names):
        hist = events[p]
        for columns, reference in [
            (slice(0, 224), archive[p + "_M"].sum(1)),
            (slice(224, 226), archive[p + "_B"]),
            (225, feed[p]),
            (226, archive[p + "_N"]),
        ]:
            x = hist[..., columns].reshape((4, -1)).sum(1)
            np.testing.assert_allclose(x, project(reference), rtol=1e-11, atol=1e-7)
        dp, mp = pot[i] if individual else pot.sum(0)
        mc += hist[..., :226] * (dp / mp)
        data += hist[..., 226]
    signal = mc[..., :224] * weight
    baseline = signal.sum(-1) + mc[..., 224:].sum(-1)
    response = np.zeros_like(data)
    response[1] = signal[1][..., iz == 14].sum(-1)
    response[2:] = signal[2:][..., iz >= 14].sum(-1)
    return data, baseline, mc[..., 225], response


def fit_and_predict(train_names, test_names):
    d, base, *sources = totals(train_names)
    obs, nom, *test_sources = totals(test_names)
    excess = (d - base).sum((1, 2))
    models = [nom]
    factors = []
    for source, test in zip(sources, test_sources):
        alpha = ratio(excess, source.sum((1, 2)))
        alpha[0] = 0
        factors.append(1 + alpha)
        models.append(nom + alpha[:, None, None] * test)
    return obs, models, factors


def selected_values(x, control):
    if control == "curvature":
        return x[:, 0, :].sum(1), x[:, :2, :].sum((1, 2))
    return x[:, :, 0].sum(1), x[:, :, :2].sum((1, 2))


def control_scores(obs, models):
    report = {}
    for control in ["curvature", "recoil"]:
        k, n = selected_values(obs, control)
        fractions = [ratio(*selected_values(model, control)) for model in models]
        pp = np.array(fractions)
        dev = 2 * (
            k * np.log(np.maximum(k / n, 1e-20) / pp)
            + (n - k) * np.log(np.maximum(1 - k / n, 1e-20) / (1 - pp))
        )
        report[control] = {
            "count": k.tolist(),
            "valid": n.tolist(),
            "pred_fraction": pp.tolist(),
            "binomial_deviance": dev.tolist(),
        }
    return report


_, base, _, _ = totals(periods, False)
np.testing.assert_allclose(base.sum((1, 2)), prev["fold_all_selected"], rtol=1e-10)
obs, models, factors = fit_and_predict(training, validation)
report = {
    "training": training,
    "validation": validation,
    "excess_factors": [x.tolist() for x in factors],
    "data_totals": obs.sum((1, 2)).tolist(),
    "raw_prediction_totals": [m.sum((1, 2)).tolist() for m in models],
    "controls": control_scores(obs, models),
}
# Sensitivity to one pair of run periods. The conditional likelihoods treat predicted shapes as fixed.
report["drop_one_pair"] = []
for i in range(6):
    observed, predicted, _ = fit_and_predict(
        training[:i] + training[i + 1 :], validation[:i] + validation[i + 1 :]
    )
    table = control_scores(observed, predicted)
    report["drop_one_pair"].append(
        {
            c: np.diff(np.array(r["binomial_deviance"])[1:, 2:].sum(1)).item()
            for c, r in table.items()
        }
    )
print(json.dumps(report, indent=2))

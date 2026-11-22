"""Synthetic checks of the signed-data readout on a common covariance."""

from types import SimpleNamespace

import numpy as np
import pytest

import signed_data


def test_signed_data_reads_both_iterations_and_the_fixed_control_subset():
    selected = np.arange(205)
    mask = np.arange(224) < len(selected)
    covariance = np.diag(mask.astype(float))

    published = np.zeros(224)
    er = np.full(224, np.sqrt(465.41527219152636 / 205))
    refined = {k: np.full(224, np.sqrt(value)) for k, value in ((5, 0.83), (10, 1.03))}
    signed = {k: refined[k].copy() for k in signed_data.KS}
    signed[5][15] -= 0.5
    signed[10][15] += 0.25
    readings = signed_data._readings(
        covariance, published, er, selected, refined, signed
    )

    assert readings["E_R"]["chi2"] == pytest.approx(465.41527219152636)
    for k, shift in ((5, -0.5), (10, 0.25)):
        result = readings[str(k)]
        assert result["signed_minus_refined"][15] == pytest.approx(shift)
        assert result["historical_control_cells"]["max_index"] == 15
        assert result["historical_control_cells"]["max_absolute"] == pytest.approx(
            abs(shift)
        )
        assert result["er_vs_signed"]["ndf"] == result["er_vs_refined"]["ndf"] == 205
        assert result["er_minus_refined"][15] - result["er_minus_signed"][
            15
        ] == pytest.approx(shift)


def test_signed_histogram_checks_actual_data_minus_background(monkeypatch, tmp_path):
    import sys
    from contextlib import nullcontext

    data = np.full((16, 18), 5.0)
    background = np.full((16, 18), 2.0)
    signed = data - background

    def histogram(values):
        return SimpleNamespace(
            GetNbinsX=lambda: 14,
            GetNbinsY=lambda: 16,
            GetBinContent=lambda i, j: values[i, j],
        )

    source = SimpleNamespace(
        Get={
            "hMeasSub2D": histogram(signed),
            "hDataReco2D": histogram(data),
            "hBkgReco2D": histogram(background),
        }.__getitem__
    )
    monkeypatch.setitem(
        sys.modules,
        "ROOT",
        SimpleNamespace(
            TFile=SimpleNamespace(Open=lambda *args: nullcontext(source)),
        ),
    )
    target, flow = signed_data._signed_histogram(tmp_path / "er.root")
    assert len(target) == 224 and np.all(target == 3)
    assert len(flow) == 64 and flow[0]["signed_count"] == 3
    signed[9, 10] += 1
    with pytest.raises(ValueError, match="data minus background"):
        signed_data._signed_histogram(tmp_path / "er.root")


@pytest.mark.parametrize(
    "defect", ["negative", "unsupported reco", "unsupported truth", "archive"]
)
def test_measure_replays_archived_target_and_stops_before_signed_unfold(
    monkeypatch, tmp_path, defect
):
    selected = np.arange(205)
    prior = np.ones(224)
    matrix = np.eye(224)
    target = np.ones(224)
    if defect == "negative":
        target[1] = -0.25
    if defect == "unsupported reco":
        matrix[223] = 0
    if defect == "unsupported truth":
        matrix[:, 1] = 0
        target[1] = 0
    archived_target = np.full(224, 2.0)
    archived_xsec = np.ones((2, 224))
    if defect == "archive":
        archived_xsec[1, 3] = 1.01
    calls = []

    def bayes(response, true, measured, ks, library):
        calls.append(measured)
        assert measured is archived_target
        return {k: prior.copy() for k in ks}

    def drive(driver, helper, argv, out, *, ibu, staging):
        assert comparison.recording_lightgbm({}, None) == []
        weights, _, _ = driver.refine_stay_positive(None, target)
        assert weights is target
        traj = ibu["unfolder"](matrix, prior, target, ibu["ks"])
        return {"M": matrix, "T": prior, "traj": traj}

    monkeypatch.setattr(signed_data, "_signed_histogram", lambda _: (target, []))
    monkeypatch.setattr(
        signed_data, "_publication", lambda _: (prior, matrix, selected)
    )
    monkeypatch.setattr(
        signed_data.runner,
        "read_npz",
        lambda _: {
            "T": prior,
            "y": archived_target,
            "ks": [5, 10],
            "xsec": archived_xsec,
        },
    )
    comparison = SimpleNamespace(
        roounfold_bayes=bayes,
        recording_lightgbm=lambda *_: pytest.fail("unnecessary LightGBM import"),
        run_driver=drive,
        xsec_at_every_k=lambda _driver, capture, _ks: capture["traj"],
    )
    driver = SimpleNamespace(refine_stay_positive=None)
    expected = "archived K=10" if defect == "archive" else "inadmissible signed"
    with pytest.raises(ValueError, match=expected):
        signed_data._measure(tmp_path, tmp_path, {"argv": []}, comparison, driver, None)
    assert len(calls) == 1
    assert not (tmp_path / "readout.json").exists()
    if defect != "archive":
        assert (tmp_path / "STOP.json").is_file()


def test_study_imports_no_matplotlib_closure():
    import subprocess
    import sys

    root = signed_data.runner.REPO
    script = """
import importlib.abc
import sys
class RejectPlotting(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.partition('.')[0] in {'matplotlib', 'technote_style', 'compare_to_paper_fullcov'}:
            raise AssertionError(fullname)
sys.meta_path.insert(0, RejectPlotting())
import signed_data
import ref_c2c1
from pathlib import Path
import inspect
assert 'compare_to_paper_fullcov' not in inspect.getsource(signed_data.run)
"""
    subprocess.run(
        [sys.executable, "-c", script],
        cwd=root / "2d-unfolding/ibukt",
        env={
            **__import__("os").environ,
            "PYTHONPATH": str(root / "2d-unfolding/ref_c2c1"),
        },
        check=True,
    )


@pytest.mark.parametrize(("seconds", "expected"), [(0, 0), (5, 124)])
def test_launcher_measures_and_times_out_child(tmp_path, seconds, expected):
    import os
    import sys

    import launch_signed_data

    status, rss = launch_signed_data._run_measured_child(
        [sys.executable, "-c", f"import time; time.sleep({seconds})"],
        tmp_path,
        os.environ.copy(),
        0.5,
    )
    assert status == expected
    assert rss > 0


def test_signed_data_launcher_pins_match_the_checkout():
    from hashlib import file_digest

    import launch_signed_data

    for name, pin in launch_signed_data.PINS.items():
        with launch_signed_data.SCRIPT.with_name(name).open("rb") as stream:
            assert file_digest(stream, "sha256").hexdigest() == pin

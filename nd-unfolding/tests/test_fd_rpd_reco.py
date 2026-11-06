"""Local real-format fixtures and contract tests for RPD-RECO; no cluster inputs."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import numpy as np
import pytest
import uproot

REPO = Path(__file__).resolve().parents[2]
SOURCE = Path(
    os.environ.get("FD_RPD_RECO_MODULE", str(REPO / "nd-unfolding/fd_rpd_reco.py"))
)
SPEC = importlib.util.spec_from_file_location("fd_rpd_reco_under_test", SOURCE)
assert SPEC is not None and SPEC.loader is not None
R = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = R
SPEC.loader.exec_module(R)


def _git(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "-c",
            "core.hooksPath=/dev/null",
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            *arguments,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return completed.stdout.strip()


def _truth(count: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    pt = rng.uniform(0.1, 0.55, count)
    pz = np.resize(np.array([2.0, 5.0, 10.0, 20.0, 30.0]), count)
    mass = 0.5 * (R.M_PROTON + R.M_NEUTRON)
    invariant = rng.uniform(1.1, 2.3, count)
    muon = np.sqrt(pt * pt + pz * pz + R.M_MUON**2)
    theta = np.arctan2(pt, pz)
    energy = (invariant**2 - mass**2 + 2 * muon * mass) / (
        2 * mass - 4 * muon * np.sin(theta / 2) ** 2
    )
    q3 = np.sqrt(4 * energy * muon * np.sin(theta / 2) ** 2 + (energy - muon) ** 2)
    return np.column_stack([pt, pz, rng.uniform(0, 1, count), q3, invariant])


def _reco(count: int, rng: np.random.Generator) -> np.ndarray:
    return np.column_stack(
        [
            rng.uniform(0.001, 4.499, count),
            rng.choice([1.7, 2.5, 3.5, 4.7, 5.5, 6.5, 9.0, 12.0, 17.0, 30.0], count),
            rng.uniform(0.001, 1.6, count),
            rng.uniform(0.001, 4, count),
            rng.uniform(0.8, 3, count),
        ]
    )


class Fixture:
    """Twelve real NPZ pairs, three real ROOT spectra and pinned source stand-ins."""

    def __init__(
        self, root: Path, *, seed: int = 17, rows: int = 64, plant_step: bool = False
    ):
        self.root = root
        self.dump = root / "dumps"
        self.dump.mkdir(parents=True)
        self.run = root / "run"
        self.flux = root / "flux"
        self.flux.mkdir()
        self.source = root / "mat-source"
        self.source.mkdir()
        _git(self.source, "init", "-q")
        text = "selected_CV_spectrum_is_numerator\ncommon_generator_histogram_is_denominator\nplaylist_mapping_is_1D_1M_1N\nall_spectra_are_per_POT_per_GeV\n"
        source = self.source / "FluxReweighter.cxx"
        source.write_text(text)
        _git(self.source, "add", "FluxReweighter.cxx")
        _git(self.source, "commit", "-q", "-m", "fixture source")
        self.prediction_repo = root / "prediction-repo"
        self.prediction_repo.mkdir()
        _git(self.prediction_repo, "init", "-q")
        pins = []
        for index, playlist in enumerate(R.PLAYLISTS):
            rng = np.random.default_rng(np.random.SeedSequence([seed, index + 1]))
            reco = _reco(rows, rng)
            passed = np.ones(rows, dtype=bool)
            passed[:2] = False
            reco[:2] = -9999
            signal = self.dump / f"lat_{playlist}.npz"
            measured = _reco(rows + index, rng)
            if plant_step and playlist in R.GROUPS["PB"]:
                measured = np.concatenate(
                    [measured, measured[(measured[:, 1] >= 8) & (measured[:, 1] < 15)]]
                )
            np.savez(
                signal,
                MCreco=reco,
                MCgen=_truth(rows, seed + index),
                w_reco=np.ones(rows),
                pass_reco=passed,
                pass_truth=np.ones(rows, dtype=bool),
                measured=measured,
                data_pot=np.array(1e19 * (index + 1)),
                axes=np.array(
                    [{"name": name} for name in ("pt", "pz", "eavail", "q3", "W")],
                    dtype=object,
                ),
            )
            background = self.dump / f"lat_{playlist}_bkg.npz"
            n_background = max(16, rows // 10)
            np.savez(
                background,
                bkg_reco=_reco(n_background, rng),
                bkg_w=np.full(n_background, 0.2),
            )
            pins.extend(f"{R.digest(path)}  {path}\n" for path in (signal, background))
        self.pins = root / "INPUTS.sha256"
        self.pins.write_text("".join(pins))
        inventory = root / "candidates.tsv"
        table = ["playlist_label\trelative_path\tsha256\tbytes\truntime_status\n"]
        edges = np.array([0, 1, 2, 4, 8, 16, 32, 64, 128], dtype=float)
        selections = {}
        for index, group in enumerate(("1D", "1M", "1N")):
            path = self.flux / f"{group}.root"
            values = np.ones(8) if index == 0 else 1 + index * 0.002 * np.arange(8)
            with uproot.recreate(path) as output:
                output["CV"] = values, edges
            table.append(
                f"{group}\t{path.name}\t{R.digest(path)}\t{path.stat().st_size}\tCANDIDATE_NOT_RUNTIME_SELECTED\n"
            )
            selections[group] = {
                "relative_path": path.name,
                "histogram": "CV",
                "retention": "local disposable fixture",
            }
        inventory.write_text("".join(table))
        h2 = REPO / "nd-unfolding/pv-ladder/readouts/h2_definition.json"
        constants = REPO / "MINERvA101/MINERvA-101-Cross-Section/event/CVUniverse.h"
        pin = lambda path: {"path": str(path), "sha256": R.digest(path)}
        self.config: dict[str, Any] = {
            "run_class": "local_fixture",
            "dump_root": str(self.dump),
            "pins": pin(self.pins),
            "h2": pin(h2),
            "inventory": pin(inventory),
            "constants": pin(constants),
            "flux_source": pin(source)
            | {"git_sha": _git(self.source, "rev-parse", "HEAD")},
            "flux_root": str(self.flux),
            "flux_selection": selections,
            "data_rows_estimate": rows * 12 + 66,
            "premise": {
                "cv_numerator_is_selected_spectrum": True,
                "generation_denominator_is_common": True,
                "spectra_are_per_pot_density": True,
                "evidence": {
                    role: {
                        "lines": [index, index],
                        "sha256": hashlib.sha256(line.encode()).hexdigest(),
                    }
                    for index, (role, line) in enumerate(
                        zip(
                            (
                                "cv_numerator",
                                "common_generation_denominator",
                                "playlist_mapping",
                                "per_pot_units",
                            ),
                            text.splitlines(),
                        ),
                        start=1,
                    )
                },
            },
        }
        self.config_path = root / "config.json"
        self.save_config()

    def save_config(self) -> None:
        self.config_path.write_text(json.dumps(self.config))
        self.config_sha = R.digest(self.config_path)

    def inputs(self) -> Any:
        inputs = R.Inputs(self.config_path, self.config_sha, self.run)
        inputs.load_pins()
        return inputs

    def execute(self, step: str, **kwargs: Any) -> dict[str, Any]:
        return R.run_stage(self.config_path, self.config_sha, self.run, step, **kwargs)

    def prepare_prediction(self) -> tuple[Path, str]:
        for step in ("pins", "p0", "d2-predict"):
            self.execute(step)
        target = self.prediction_repo / "prediction.json"
        shutil.copyfile(self.run / "d2-predict.json", target)
        _git(self.prediction_repo, "add", "prediction.json")
        _git(self.prediction_repo, "commit", "-q", "-m", "fixture pre-data prediction")
        return target, R.digest(target)


@pytest.fixture
def standin_noatime(monkeypatch: pytest.MonkeyPatch) -> None:
    """A real distinguishable descriptor flag on local stand-ins, never production."""
    if not hasattr(os, "O_NOATIME"):
        monkeypatch.setattr(os, "O_NOATIME", os.O_NONBLOCK, raising=False)


@pytest.fixture
def fixture(tmp_path: Path, standin_noatime: None) -> Fixture:
    return Fixture(tmp_path)


def test_native_noatime_absence_refuses(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delattr(os, "O_NOATIME", raising=False)
    with pytest.raises(R.Refused, match="NOATIME"):
        R.noatime_flag()


def test_plain_open_refused_and_staging_allowed(fixture: Fixture) -> None:
    source = fixture.pins
    with R.read_guards([source]):
        with pytest.raises(R.Refused, match="PLAIN_OPEN"):
            source.read_bytes()
        copied = R.stage_copy(
            source, fixture.root / "copy", fixture.config["pins"]["sha256"]
        )
    assert copied.read_bytes() == source.read_bytes()


@pytest.mark.parametrize("defect", ["missing", "extra", "digest"])
def test_pins_bad_and_good(fixture: Fixture, defect: str) -> None:
    assert fixture.execute("pins")["result"]["n_files"] == 24
    second_run = fixture.root / "bad-run"
    fixture.run = second_run
    source = fixture.dump / "lat_1A.npz"
    if defect == "missing":
        source.unlink()
    elif defect == "extra":
        (fixture.dump / "extra.npz").write_bytes(b"extra")
    else:
        source.write_bytes(b"changed")
    with pytest.raises(R.Refused, match="PIN_SET|INPUT_DIGEST"):
        fixture.execute("pins")


def test_staging_guards(fixture: Fixture) -> None:
    copied = fixture.root / "staged-copy"
    R.stage_copy(fixture.pins, copied, R.digest(fixture.pins))
    copied.write_bytes(b"modified")
    with pytest.raises(R.Refused, match="STAGED_DIGEST"):
        R.stage_copy(fixture.pins, copied, R.digest(fixture.pins))
    with pytest.raises(R.Refused, match="INPUT_EXISTS"):
        R.stage_copy(fixture.root / "missing", fixture.root / "absent-copy", "a" * 64)
    with pytest.raises(R.Refused, match="DIGEST_FORMAT"):
        R.stage_copy(fixture.pins, fixture.root / "bad-sha", "short")
    with pytest.raises(R.Refused, match="STAGE_LOCATION"):
        R.stage_copy(fixture.pins, fixture.pins, R.digest(fixture.pins))


@pytest.mark.parametrize("step", R.STEPS[1:])
def test_every_step_refuses_missing_predecessor(fixture: Fixture, step: str) -> None:
    with pytest.raises(R.Refused, match="PREDECESSOR"):
        fixture.execute(step)


def test_predecessor_pass_identity_and_chain(fixture: Fixture) -> None:
    fixture.execute("pins")
    inputs = fixture.inputs()
    assert (
        R.require_predecessors(inputs, "p0", dry_run=False)["pins"]["status"] == "PASS"
    )
    path = fixture.run / "pins.json"
    original = json.loads(path.read_text())
    for key, value, guard in (
        ("status", "STOP", "PREDECESSOR"),
        ("code_sha256", "wrong", "PREDECESSOR_IDENTITY"),
        ("predecessor_sha256", "wrong", "PREDECESSOR_SHA"),
    ):
        path.write_text(json.dumps(original | {key: value}))
        with pytest.raises(R.Refused, match=guard):
            R.require_predecessors(inputs, "p0", dry_run=False)
    path.write_text(json.dumps(original))


def test_prediction_required_committed_and_exact(fixture: Fixture) -> None:
    prediction, sha = fixture.prepare_prediction()
    inputs = fixture.inputs()
    with pytest.raises(R.Refused, match="PREDICTION_COMMITTED"):
        inputs.key("lat_1A.npz", "measured")
    inputs.prediction = prediction, sha
    assert inputs.key("lat_1A.npz", "measured").shape[1] == 5
    prediction.write_text(prediction.read_text() + " ")
    with pytest.raises(R.Refused, match="PREDICTION_SHA"):
        inputs.key("lat_1A.npz", "measured")
    another_command = fixture.inputs()
    another_command.prediction = prediction, sha
    with pytest.raises(R.Refused, match="PREDICTION_SHA"):
        another_command.key("lat_1A.npz", "measured")
    shutil.copyfile(fixture.run / "d2-predict.json", prediction)
    uncommitted = fixture.prediction_repo / "not-committed.json"
    shutil.copyfile(prediction, uncommitted)
    inputs.prediction = uncommitted, sha
    with pytest.raises(R.Refused, match="PREDICTION_COMMITTED"):
        inputs.key("lat_1A.npz", "measured")


def test_key_allowlist_and_object_array(fixture: Fixture) -> None:
    inputs = fixture.inputs()
    assert inputs.key("lat_1A.npz", "axes").dtype == object
    with pytest.raises(R.Refused, match="KEY_ALLOWLIST"):
        inputs.key("lat_1A.npz", "measured_weights")


def test_committed_prediction_is_staged_before_read(fixture: Fixture) -> None:
    path, sha = fixture.prepare_prediction()
    inputs = fixture.inputs()
    inputs.prediction = path, sha
    with R.read_guards([path]):
        inputs.require_prediction()
    assert len(list(inputs.staged.glob("prediction-*.json"))) == 1


@pytest.mark.parametrize(
    "defect,guard",
    [
        ("truth", "PASS_TRUTH"),
        ("finite", "FINITE_MC"),
        ("weights", "WEIGHTS"),
        ("shape", "ARRAY_SHAPE"),
        ("key", "KEY_EXISTS"),
    ],
)
def test_signal_guards(fixture: Fixture, defect: str, guard: str) -> None:
    path = fixture.dump / "lat_1A.npz"
    with np.load(path, allow_pickle=True) as archive:
        contents = {key: archive[key] for key in archive.files}
    if defect == "truth":
        contents["pass_truth"][3] = False
    elif defect == "finite":
        contents["MCreco"][3, 0] = np.nan
    elif defect == "weights":
        contents["w_reco"][3] = -1
    elif defect == "shape":
        contents["MCgen"] = contents["MCgen"][:-1]
    else:
        del contents["MCgen"]
    np.savez(path, **contents)
    fixture.pins.write_text(
        "".join(
            f"{R.digest(source)}  {source}\n"
            for source in sorted(fixture.dump.glob("*.npz"))
        )
    )
    fixture.config["pins"]["sha256"] = R.digest(fixture.pins)
    fixture.save_config()
    inputs = fixture.inputs()
    with pytest.raises(R.Refused, match=guard):
        next(inputs.samples(data=False))


def test_finite_data_refusal(fixture: Fixture) -> None:
    path = fixture.dump / "lat_1A.npz"
    with np.load(path, allow_pickle=True) as archive:
        contents = {key: archive[key] for key in archive.files}
    contents["measured"][0, 0] = np.nan
    np.savez(path, **contents)
    fixture.pins.write_text(
        "".join(
            f"{R.digest(source)}  {source}\n"
            for source in sorted(fixture.dump.glob("*.npz"))
        )
    )
    fixture.config["pins"]["sha256"] = R.digest(fixture.pins)
    fixture.save_config()
    prediction, sha = fixture.prepare_prediction()
    inputs = fixture.inputs()
    inputs.prediction = prediction, sha
    with pytest.raises(R.Refused, match="FINITE_DATA"):
        list(inputs.samples(data=True))


def test_p0_real_root_inputs_and_no_data(fixture: Fixture) -> None:
    fixture.execute("pins")
    record = fixture.execute("p0")
    assert {row["key"] for row in record["keys_read"]} <= R.MC_KEYS | R.BKG_KEYS
    assert set(record["result"]["spectra"]) == {"1D", "1M", "1N"}
    assert record["result"]["constants_GeV"] == {"M_p": 0.938272013, "M_n": 0.93956536}
    assert record["result"]["P-F"]["pass"] is True
    assert (
        record["result"]["runtime_estimate"]["data_rows_estimate_not_read"]
        == 64 * 12 + 66
    )
    assert len(record["result"]["spectra"]["1M"]["edges"]) == 9


@pytest.mark.parametrize(
    "defect", ["premise", "evidence", "selection", "source", "histogram"]
)
def test_p0_refusals(fixture: Fixture, defect: str) -> None:
    if defect == "premise":
        fixture.config["premise"]["generation_denominator_is_common"] = False
    elif defect == "evidence":
        fixture.config["premise"]["evidence"]["cv_numerator"]["sha256"] = "0" * 64
    elif defect == "selection":
        fixture.config["flux_selection"]["1M"]["relative_path"] = "not-selected.root"
    elif defect == "source":
        fixture.config["flux_source"]["git_sha"] = "0" * 40
    else:
        fixture.config["flux_selection"]["1D"]["histogram"] = "missing"
    fixture.save_config()
    fixture.execute("pins")
    with pytest.raises(
        R.Refused, match="P_F|FLUX_SELECTION|SOURCE_COMMIT|FLUX_HISTOGRAM"
    ):
        fixture.execute("p0")


def test_energy_algebra_only_and_controls() -> None:
    truth = _truth(600, 29)
    for mass in (R.M_PROTON, R.M_NEUTRON):
        energy, _denominator, muon = R.reconstructed_energy(truth, mass)
        theta = np.arctan2(truth[:, 0], truth[:, 1])
        squared_mass = (
            mass**2
            + 2 * (energy - muon) * mass
            - 4 * energy * muon * np.sin(theta / 2) ** 2
        )
        np.testing.assert_allclose(squared_mass, truth[:, 4] ** 2, rtol=0, atol=1e-9)
    assert len(R.energy_controls(truth, np.ones(600))) == 3
    with pytest.raises(R.Refused, match="C_E3"):
        R.energy_controls(truth, np.ones(600), scale=1.01)
    bad = truth.copy()
    bad[:, 0] = 10
    with pytest.raises(R.Refused, match="C_E1"):
        R.energy_controls(bad, np.ones(600))


def test_energy_controls_each_stratum_and_bars() -> None:
    truth = _truth(900, 51)
    for low, high in ((1.5, 8), (8, 15), (15, 60)):
        bad = truth.copy()
        selected = (truth[:, 1] >= low) & (truth[:, 1] < high)
        bad[selected, 3] *= 1.01
        with pytest.raises(R.Refused, match="C_E3"):
            R.energy_controls(bad, np.ones(900))
    part = R.energy_statistics(truth, np.ones(900), truth[:, 1])
    part["strata"]["1.5:8"]["error"][:] = 0.0021
    with pytest.raises(R.Refused, match="C_E3"):
        R.evaluate_energy_controls([part])
    part = R.energy_statistics(truth, np.ones(900), truth[:, 1])
    error = part["strata"]["1.5:8"]["error"]
    error[: max(2, len(error) // 20)] = 0.031
    with pytest.raises(R.Refused, match="C_E3"):
        R.evaluate_energy_controls([part])


def test_flux_range_step_function_and_gate() -> None:
    own = {"edges": [0, 2, 4], "values": [1, 2]}
    target = {"edges": [1, 2, 3], "values": [3, 4]}
    factors, outside = R.spectrum_ratio(np.array([0.5, 1.0, 2.0, 3.0]), own, target)
    np.testing.assert_array_equal(factors, [1, 3, 2, 1])
    np.testing.assert_array_equal(outside, [True, False, False, True])
    truth = _truth(1000, 13)
    part = R.energy_statistics(truth, np.ones(1000), truth[:, 1])
    controls = {"energy_parts": [part], "pb_weight": 1000.0, "outside_weight": 1.0}
    assert R.prediction_controls(controls)["outside_fraction"] == 0.001
    controls["outside_weight"] = 1.1
    with pytest.raises(R.Refused, match="OUTSIDE_RANGE"):
        R.prediction_controls(controls)


def test_bins_deciles_and_reporting_cells() -> None:
    np.testing.assert_array_equal(
        R.bin_indices(np.array([-1, 0, 1, 2, 3]), np.array([0.0, 1.0, 2.0])),
        [2, 0, 1, 2, 2],
    )
    np.testing.assert_array_equal(
        R.bin_indices(np.array([-100, 0, 1, 100]), np.array([-np.inf, 1.0, np.inf])),
        [0, 0, 1, 1],
    )
    quantiles = R.weighted_quantiles(
        np.array([1.0, 1.0, 2.0]), np.ones(3), np.arange(1, 10) / 10
    )
    assert len(np.unique(quantiles)) == 2
    definition = json.loads(
        (REPO / "nd-unfolding/pv-ladder/readouts/h2_definition.json").read_text()
    )
    rows = np.array(
        [
            [0.2, 2.0, 0.2, 0.2, 1.2],
            [0.2, 2.0, 0.2, 3.0, 1.2],
            [5.0, 2.0, 0.2, 0.2, 1.2],
        ]
    )
    np.testing.assert_array_equal(R.reporting_cells(rows, definition), [0, -1, -2])


def test_leave_one_out_and_bootstrap_sigma_hand_calculation() -> None:
    counts = np.array([[10.0, 20.0], [30.0, 40.0], [5.0, 10.0]])
    prediction = np.array([[5.0, 10.0], [10.0, 20.0], [5.0, 5.0]])
    offset = R.leave_one_out(counts, prediction)
    assert offset[0, 0] == pytest.approx((10 / 5) / ((30 + 5) / (10 + 5)) - 1)
    replicas = np.stack(
        [
            offset,
            R.leave_one_out(counts * 1.01, prediction),
            R.leave_one_out(counts * 0.99, prediction),
        ]
    )
    np.testing.assert_allclose(R._sigma(replicas), np.std(replicas[1:], axis=0, ddof=1))
    score = R.shape_score(
        np.array([0.0, 0.1, 50.0]),
        np.array([0.1, 0.1, 0.001]),
        np.array([25.0, 25.0, 24.99]),
    )
    assert score["ndf"] == 1
    assert score["chi2"] == pytest.approx(0.5)
    assert score["excluded"] == [2]
    with pytest.raises(R.Refused, match="BOOTSTRAP_VARIANCE"):
        R.shape_score(
            np.array([0.0, 0.1]), np.array([0.0, 0.1]), np.array([25.0, 25.0])
        )


def _null_pvalues() -> np.ndarray:
    return ((np.arange(1920) + 0.5) / 1920).reshape(20, 8, 12)


def test_c0_calibration_both_sigma_directions_and_offset() -> None:
    from scipy.stats import chi2

    pvalues = _null_pvalues()
    assert R.calibration_gate(pvalues)["p_lt_005"] == 0.05
    statistics = chi2.isf(pvalues, 10)
    for scale in (0.5, 2.0):
        with pytest.raises(R.Refused, match="C0_CALIBRATION"):
            R.calibration_gate(chi2.sf(statistics / scale**2, 10))
    # Independent Poisson count-level fixture: a 5% shape offset in one
    # pseudo-playlist is resolvable; this is not a physics measurement.
    rng = np.random.default_rng(71)
    counts = np.full((201, 12, 10), 1_000_000.0)
    predictions = np.full_like(counts, 1_000_000.0)
    counts[1:] = rng.poisson(counts[1:])
    predictions[1:] = rng.poisson(predictions[1:])
    counts[:, 0, 0] *= 1.05
    offset = R.leave_one_out(counts, predictions)
    planted = R.shape_score(offset[0, 0], R._sigma(offset)[0], predictions[0, 0])["p"]
    pvalues[0, 0, 0] = planted
    with pytest.raises(R.Refused, match="C0_FAMILY"):
        R.calibration_gate(pvalues)


def test_c0_tail_count_and_family_guards() -> None:
    with pytest.raises(R.Refused, match="C0_COUNT"):
        R.calibration_gate(np.ones((1, 8, 12)))
    pvalues = _null_pvalues()
    pvalues.flat[:10] = 0.0005
    with pytest.raises(R.Refused, match="C0_TAIL"):
        R.calibration_gate(pvalues)
    pvalues = _null_pvalues()
    pvalues.flat[0] = 1e-8
    with pytest.raises(R.Refused, match="C0_FAMILY"):
        R.calibration_gate(pvalues)


@pytest.mark.parametrize(
    "fraction,sigma,predicted,probability,outcome",
    [
        (1.0, 0.05, 0.1, 0.5, "TRACKS"),
        (0.8, 0.01, 0.1, 0.5, "TRACKS"),
        (0.4, 0.01, 0.1, 0.5, "PARTIAL"),
        (0.1, 0.01, 0.1, 0.5, "DOES-NOT-TRACK"),
        (0.6, 0.2, 0.1, 0.5, "INCONCLUSIVE"),
        (0.8, 0.01, -0.1, 0.5, "DOES-NOT-TRACK"),
        (0.8, 0.01, 0.1, 0.009, "PARTIAL"),
    ],
)
def test_d2_outcomes_and_revision_one_gap(
    fraction: float, sigma: float, predicted: float, probability: float, outcome: str
) -> None:
    assert (
        R.classify_flux_swap(
            observed=0.1,
            sigma_observed=0.005,
            fraction=fraction,
            sigma_fraction=sigma,
            predicted=predicted,
            sigma_predicted=0.01,
            prediction_p=probability,
        )
        == outcome
    )


def test_d2_negative_zero_and_bracket() -> None:
    assert R.step_reading(-0.1, 0.01) == "SEEN"
    assert R.step_reading(0.03, 0.01) == "SEEN"
    assert R.step_reading(0.0299, 0.01) == "NOT-SEEN-AT-3σ"
    assert (
        R.classify_flux_swap(
            observed=-0.1,
            sigma_observed=0.01,
            fraction=0.8,
            sigma_fraction=0.01,
            predicted=-0.1,
            sigma_predicted=0.01,
            prediction_p=0.1,
        )
        == "TRACKS"
    )
    assert (
        R.classify_flux_swap(
            observed=0,
            sigma_observed=0.01,
            fraction=np.nan,
            sigma_fraction=np.nan,
            predicted=0,
            sigma_predicted=0,
            prediction_p=0,
        )
        == "NOT-SEEN"
    )
    assert (
        R.classify_flux_swap(
            observed=0.029,
            sigma_observed=0.01,
            fraction=0.8,
            sigma_fraction=0.01,
            predicted=0.1,
            sigma_predicted=0.01,
            prediction_p=0.1,
        )
        == "NOT-SEEN"
    )
    assert R.bracket_outcome("TRACKS", "PARTIAL") == "INCONCLUSIVE"
    assert R.bracket_outcome("TRACKS", "TRACKS") == "TRACKS"


def test_d2_boundaries_and_signed_prediction_bar() -> None:
    def classify(**changes: float) -> str:
        arguments = {
            "observed": 0.1,
            "sigma_observed": 0.01,
            "fraction": 0.75,
            "sigma_fraction": 0.125,
            "predicted": 0.1,
            "sigma_predicted": 0.01,
            "prediction_p": 0.01,
        }
        return R.classify_flux_swap(**(arguments | changes))

    assert classify() == "TRACKS"
    assert classify(fraction=0.749, sigma_fraction=0.01) == "PARTIAL"
    assert classify(fraction=0.75, sigma_fraction=0.126) == "PARTIAL"
    assert classify(fraction=0.27, sigma_fraction=0.01) == "PARTIAL"
    assert classify(fraction=0.269, sigma_fraction=0.01) == "INCONCLUSIVE"
    assert classify(fraction=0.23, sigma_fraction=0.01) == "INCONCLUSIVE"
    assert classify(fraction=0.229, sigma_fraction=0.01) == "DOES-NOT-TRACK"
    assert classify(predicted=-0.019, sigma_predicted=0.01) == "PARTIAL"
    assert classify(predicted=-0.02, sigma_predicted=0.01) == "DOES-NOT-TRACK"


def test_hadronic_firing_bars() -> None:
    scores = {
        f"{axis}{suffix}": [
            {"playlist": playlist, "p": 0.5} for playlist in R.PLAYLISTS
        ]
        for axis in ("eavail", "q3", "W")
        for suffix in ("", "@0", "@1", "@2", "@3")
    }
    assert R.hadronic_reading(scores)["outcome"] == "HADRONIC-NOT-DETECTED"
    scores["q3"][0]["p"] = 0.001 / 12 - 1e-10
    assert R.hadronic_reading(scores)["outcome"] == "HADRONIC-VIA-MUON"
    scores["q3@1"][0]["p"] = 0.001 / 48
    assert R.hadronic_reading(scores)["outcome"] == "HADRONIC-VIA-MUON"
    scores["q3@1"][0]["p"] -= 1e-10
    assert R.hadronic_reading(scores)["outcome"] == "HADRONIC-CONDITIONAL"


@pytest.mark.parametrize("seed", [17, 43])
def test_real_format_prediction_bins_readback_and_two_bootstrap_seeds(
    tmp_path: Path, standin_noatime: None, seed: int
) -> None:
    fixture = Fixture(tmp_path, seed=seed, rows=128)
    prediction, sha = fixture.prepare_prediction()
    record = fixture.execute("step0", prediction=prediction, prediction_sha=sha)
    assert not any(row["key"] == "measured" for row in record["keys_read"])
    inputs = fixture.inputs()
    inputs.prediction = prediction, sha
    p0_record = json.loads((fixture.run / "p0.json").read_text())["result"]
    histograms, _controls = R.aggregate(inputs, p0_record, record["result"], data=True)
    for replica in (0, 1):
        rng = np.random.default_rng(np.random.SeedSequence([20261104, 11, replica + 1]))
        manual = np.zeros((12, 3))
        manual_pz = np.zeros((12, len(R.PZ_EDGES)))
        for sample in inputs.samples(data=True):
            draws = rng.poisson(1, len(sample.values))
            if sample.kind == "data":
                bins, _size = R.axis_assignments(sample.values, None)["step"]
                manual[R.PLAYLISTS.index(sample.playlist)] = np.bincount(
                    bins, weights=draws, minlength=3
                )
                pz_bins = R.bin_indices(sample.values[:, 1], R.PZ_EDGES)
                manual_pz[R.PLAYLISTS.index(sample.playlist)] = np.bincount(
                    pz_bins, weights=draws, minlength=len(R.PZ_EDGES)
                )
        np.testing.assert_array_equal(histograms["step"]["N"][replica + 1], manual)
        np.testing.assert_array_equal(histograms["pz"]["N"][replica + 1], manual_pz)
    product = R._save_histograms(fixture.run, "readback", histograms)
    readback = R._load_histograms(fixture.run, product)
    np.testing.assert_array_equal(readback["step"]["N"], histograms["step"]["N"])
    steps = R.observed_steps(readback["step"]["N"], readback["step"]["P"])
    assert steps.shape == (201, 12)
    assert np.all(np.isfinite(steps))


def test_step_output_and_dry_run_guards(fixture: Fixture) -> None:
    fixture.execute("pins")
    with pytest.raises(R.Refused, match="OUTPUT_EXISTS"):
        fixture.execute("pins")
    with pytest.raises(R.Refused, match="STEP_NAME"):
        fixture.execute("not-a-step")
    with pytest.raises(R.Refused, match="DRY_RUN_SCOPE"):
        fixture.execute("d1", dry_run=True)


def test_input_changed_guard(fixture: Fixture, monkeypatch: pytest.MonkeyPatch) -> None:
    original = os.fstat
    calls = 0

    def changed(descriptor: int) -> Any:
        nonlocal calls
        calls += 1
        info = original(descriptor)
        return SimpleNamespace(
            st_ino=info.st_ino,
            st_size=info.st_size,
            st_mtime_ns=info.st_mtime_ns + calls,
        )

    monkeypatch.setattr(os, "fstat", changed)
    with pytest.raises(R.Refused, match="INPUT_CHANGED"):
        R.stage_copy(
            fixture.pins, fixture.root / "changed", fixture.config["pins"]["sha256"]
        )


@pytest.mark.parametrize(
    "defect,guard", [("format", "PIN_FORMAT"), ("root", "PIN_ROOT")]
)
def test_pin_manifest_guards(fixture: Fixture, defect: str, guard: str) -> None:
    text = fixture.pins.read_text()
    if defect == "format":
        text = "invalid\n" + text
    else:
        text = text.replace(
            str(fixture.dump / "lat_1A.npz"), str(fixture.root / "lat_1A.npz")
        )
    fixture.pins.write_text(text)
    fixture.config["pins"]["sha256"] = R.digest(fixture.pins)
    fixture.save_config()
    with pytest.raises(R.Refused, match=guard):
        fixture.inputs()


def test_mass_and_flux_size_guards(fixture: Fixture) -> None:
    constants = fixture.root / "bad-constants.h"
    constants.write_text("double M_n = 939.56536; double M_p = 938.0;\n")
    fixture.config["constants"] = {
        "path": str(constants),
        "sha256": R.digest(constants),
    }
    fixture.save_config()
    inputs = fixture.inputs()
    with pytest.raises(R.Refused, match="MASS_CONSTANTS"):
        R.p0(inputs)
    fixture.run = fixture.root / "bad-size-run"
    constants.write_text("double M_n = 939.56536; double M_p = 938.272013;\n")
    fixture.config["constants"]["sha256"] = R.digest(constants)
    inventory = Path(fixture.config["inventory"]["path"])
    lines = inventory.read_text().splitlines()
    fields = lines[1].split("\t")
    fields[3] = str(int(fields[3]) + 1)
    lines[1] = "\t".join(fields)
    inventory.write_text("\n".join(lines) + "\n")
    fixture.config["inventory"]["sha256"] = R.digest(inventory)
    fixture.save_config()
    with pytest.raises(R.Refused, match="FLUX_SIZE"):
        R.p0(fixture.inputs())


def test_empty_support_flux_layout_and_cells(fixture: Fixture) -> None:
    with pytest.raises(R.Refused, match="MC_SUPPORT"):
        R.weighted_quantiles(np.ones(2), np.zeros(2), np.array([0.5]))
    truth = _truth(20, 12)
    truth[:, 1] = 2.0
    proton, _denominator, muon = R.reconstructed_energy(truth, R.M_PROTON)
    neutron, _denominator, _muon = R.reconstructed_energy(truth, R.M_NEUTRON)
    energy = (proton + neutron) / 2
    truth[:, 3] = np.sqrt(
        4 * energy * muon * np.sin(np.arctan2(truth[:, 0], truth[:, 1]) / 2) ** 2
        + (energy - muon) ** 2
    )
    with pytest.raises(R.Refused, match="CE_SUPPORT"):
        R.energy_controls(truth, np.ones(20))
    own = {"edges": [0.0, 1.0], "values": [0.0]}
    with pytest.raises(R.Refused, match="FLUX_SUPPORT"):
        R.spectrum_ratio(np.array([0.5]), own, {"edges": [0.0, 1.0], "values": [1.0]})
    path = fixture.root / "bad-flux.root"
    with uproot.recreate(path) as root:
        root["CV"] = np.array([-1.0, 2.0]), np.array([0.0, 1.0, 2.0])
    with pytest.raises(R.Refused, match="FLUX_LAYOUT"):
        R.read_flux_histogram(path, "CV")
    definition = json.loads(
        (REPO / "nd-unfolding/pv-ladder/readouts/h2_definition.json").read_text()
    )
    definition["h2_to_reporting_cell"][0] = -1
    with pytest.raises(R.Refused, match="CELL_IDENTITY"):
        R.reporting_cells(np.array([[0.2, 2.0, 0.2, 0.2, 1.2]]), definition)


def test_swap_support_and_d2_finite_guards() -> None:
    truth = _truth(100, 32)
    with pytest.raises(R.Refused, match="SWAP_SUPPORT"):
        R.prediction_controls(
            {
                "energy_parts": [R.energy_statistics(truth, np.ones(100), truth[:, 1])],
                "pb_weight": 0,
                "outside_weight": 0,
            }
        )
    with pytest.raises(R.Refused, match="D2_FINITE"):
        R.classify_flux_swap(
            observed=0.1,
            sigma_observed=0.01,
            fraction=np.nan,
            sigma_fraction=0.1,
            predicted=0.1,
            sigma_predicted=0.01,
            prediction_p=0.5,
        )


def test_product_digest_guard(fixture: Fixture) -> None:
    fixture.run.mkdir()
    product = R._save_histograms(
        fixture.run,
        "product",
        {"step": {"N": np.ones((201, 12, 3)), "P": np.ones((201, 5, 12, 3))}},
    )
    assert R._load_histograms(fixture.run, product)["step"]["N"].shape == (201, 12, 3)
    (fixture.run / product["path"]).write_bytes(b"modified")
    with pytest.raises(R.Refused, match="PRODUCT_DIGEST"):
        R._load_histograms(fixture.run, product)


def test_prediction_content_guard(fixture: Fixture) -> None:
    path, _sha = fixture.prepare_prediction()
    record = json.loads(path.read_text())
    record["result"]["simulation_only"] = False
    for target in (path, fixture.run / "d2-predict.json"):
        target.write_text(json.dumps(record))
    _git(fixture.prediction_repo, "add", "prediction.json")
    _git(fixture.prediction_repo, "commit", "-q", "-m", "fixture invalid prediction")
    inputs = fixture.inputs()
    inputs.prediction = path, R.digest(path)
    with pytest.raises(R.Refused, match="PREDICTION_CONTENT"):
        inputs.key("lat_1A.npz", "measured")


def test_data_partition_exact_and_independent(fixture: Fixture) -> None:
    path, sha = fixture.prepare_prediction()
    inputs = fixture.inputs()
    inputs.prediction = path, sha
    p0_record = json.loads((fixture.run / "p0.json").read_text())["result"]
    target = np.arange(64, 76)
    config = p0_record | {
        "partition_fractions": {
            "signal": np.full(12, 1 / 12),
            "background": np.full(12, 1 / 12),
        },
        "data_counts": target,
    }
    histograms, controls = R.aggregate(inputs, config, None, data=True, partition=0)
    np.testing.assert_array_equal(controls["kind_totals"]["data"], target)
    assert not np.allclose(
        controls["kind_totals"]["signal"], controls["kind_totals"]["background"]
    )
    assert histograms["step"]["N"].shape == (201, 12, 3)
    config["data_counts"] = target + 1
    with pytest.raises(R.Refused, match="DATA_PARTITION"):
        R.aggregate(inputs, config, None, data=True, partition=1)


def test_runtime_estimate_and_resource_guards(
    fixture: Fixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    inputs = fixture.inputs()
    times = iter((0.0, 1000.0))
    monkeypatch.setattr(R.time, "perf_counter", lambda: next(times))
    estimate = R.runtime_estimate(inputs)
    assert estimate["exceeds_two_hours"] and estimate["needs_director_price"]
    assert not any(row["key"] == "measured" for row in inputs.keys_read)
    monkeypatch.setenv("OMP_NUM_THREADS", "2")
    arguments = [
        "pins",
        "--config",
        str(fixture.config_path),
        "--config-sha256",
        fixture.config_sha,
        "--run",
        str(fixture.root / "thread-refusal"),
    ]
    assert R.main(arguments) == 4
    assert (
        json.loads((fixture.root / "thread-refusal/pins.STOP.json").read_text())[
            "guard"
        ]
        == "THREADS"
    )
    for key in R.THREAD_KEYS:
        monkeypatch.setenv(key, "1")
    monkeypatch.setattr(os, "getpriority", lambda *_args: 0)
    monkeypatch.setattr(os, "nice", lambda *_args: 0)
    arguments[-1] = str(fixture.root / "nice-refusal")
    assert R.main(arguments) == 4
    assert (
        json.loads((fixture.root / "nice-refusal/pins.STOP.json").read_text())["guard"]
        == "NICE"
    )


@pytest.mark.parametrize("seed,expected_pass", [(17, True), (43, False)])
def test_real_format_c0_pass_and_stop(
    tmp_path: Path, standin_noatime: None, seed: int, expected_pass: bool
) -> None:
    fixture = Fixture(tmp_path, seed=seed, rows=1024)
    prediction, sha = fixture.prepare_prediction()
    fixture.execute("step0")
    if not expected_pass:
        with pytest.raises(R.Refused, match="C0_FAMILY") as refused:
            fixture.execute("c0", prediction=prediction, prediction_sha=sha)
        assert refused.value.details["readings"] is None
        with pytest.raises(R.Refused, match="PREDECESSOR"):
            fixture.execute("d1", prediction=prediction, prediction_sha=sha)
        return
    fixture.execute("c0", prediction=prediction, prediction_sha=sha)
    c0 = json.loads((fixture.run / "c0.json").read_text())
    assert c0["status"] == "PASS"
    assert len(c0["result"]["calibration"]["pvalues"]) == 20
    for partition in c0["result"]["partition_disclosures"]:
        assert partition["actual_data_counts"] == partition["target_data_counts"]
        assert partition["read_by_scoring"] is False


@pytest.mark.parametrize("seed", [17, 43])
def test_downstream_scoring_two_seeds(
    tmp_path: Path, standin_noatime: None, seed: int
) -> None:
    """Exercise d1/d2 on real-format data, with an explicit unit C-0 predecessor.

    This is a scoring test, not a claim that the planted-step fixture passed
    C-0. Actual C-0 pass and STOP behavior is tested separately above.
    """
    fixture = Fixture(tmp_path, seed=seed, rows=512, plant_step=True)
    prediction, sha = fixture.prepare_prediction()
    fixture.execute("step0")
    inputs = fixture.inputs()
    inputs.prediction = prediction, sha
    records = R.require_predecessors(inputs, "c0", dry_run=False)
    histograms, _controls = R.aggregate(
        inputs, records["p0"]["result"], records["step0"]["result"], data=True
    )
    product = R._save_histograms(fixture.run, "c0", histograms)
    fixture_control = {
        "step": "c0",
        "status": "PASS",
        "code_sha256": R.digest(SOURCE),
        "config_sha256": fixture.config_sha,
        "predecessor_sha256": R.digest(fixture.run / "step0.json"),
        "dry_run": False,
        "result": {
            "product": product,
            "unit_test_predecessor_only": True,
            "calibration": R.calibration_gate(_null_pvalues()),
        },
    }
    R.write_json(fixture.run / "c0.json", fixture_control)
    for step in ("d1", "d2"):
        fixture.execute(step, prediction=prediction, prediction_sha=sha)
    c0 = json.loads((fixture.run / "c0.json").read_text())
    d1 = json.loads((fixture.run / "d1.json").read_text())["result"]
    assert set(d1["R-d1.0"]) == {"PB", "PC"}
    assert len(d1["axes"]["pz"]) == 12
    assert d1["R-d1.2"]["overall"]["1A"]["data_sigma"] > 0
    d2 = json.loads((fixture.run / "d2.json").read_text())["result"]
    assert d2["outcome"] in {
        "NOT-SEEN",
        "DOES-NOT-TRACK",
        "TRACKS",
        "PARTIAL",
        "INCONCLUSIVE",
    }
    assert d1["R-d1.0"]["PB"]["reading"] == "SEEN"
    histograms = R._load_histograms(fixture.run, c0["result"]["product"])["step"]
    observed = R.observed_steps(histograms["N"], histograms["P"])
    for label, variant in (
        ("unswapped_background", 1),
        ("integral_scaled_background", 2),
    ):
        predicted = R.predicted_steps(histograms["P"], variant)
        np.testing.assert_allclose(
            d2["brackets"][label]["sigma_residual"],
            np.std((observed - predicted)[1:], axis=0, ddof=1),
            rtol=1e-13,
        )
        assert d2["brackets"][label]["ndf"] == 12


def test_rate_per_pot_guard_and_arithmetic(fixture: Fixture) -> None:
    counts = np.ones((201, 12, 3))
    prediction = np.ones((201, 5, 12, 3)) * 2
    histograms = {
        "step": {"N": counts, "P": prediction},
        "rate@0": {"N": counts[..., :2], "P": prediction[..., :2]},
        "rate@1": {"N": counts[..., :2], "P": prediction[..., :2]},
    }
    inputs = SimpleNamespace(key=lambda name, _key: R.PLAYLISTS.index(name[4:6]) + 1)
    result = R._rate_summary(histograms, inputs)
    assert result["overall"]["PA"]["data_per_POT"] == pytest.approx(18 / 21)
    assert result["pz<8"]["1B"]["prediction_per_POT"] == 1
    inputs.key = lambda *_args: 0
    with pytest.raises(R.Refused, match="POT"):
        R._rate_summary(histograms, inputs)


def test_step_and_d2_variance_guards(
    fixture: Fixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    fixture.run.mkdir()
    histograms = {"step": {"N": np.ones((201, 12, 3)), "P": np.ones((201, 5, 12, 3))}}
    product = R._save_histograms(fixture.run, "c0", histograms)
    inputs = SimpleNamespace(require_prediction=lambda: None, run=fixture.run)
    records = {
        "c0": {"result": {"product": product}},
        "d1": {"result": {"R-d1.0": {"PB": {"reading": "SEEN"}}}},
    }
    monkeypatch.setattr(R, "score_axes", lambda *_args: {})
    with pytest.raises(R.Refused, match="STEP_VARIANCE"):
        R._d1(inputs, records)
    with pytest.raises(R.Refused, match="D2_VARIANCE"):
        R._d2(inputs, records)


def test_prediction_reproduction_guard(
    fixture: Fixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    prediction, sha = fixture.prepare_prediction()
    fixture.execute("step0")
    inputs = fixture.inputs()
    inputs.prediction = prediction, sha
    records = R.require_predecessors(inputs, "c0", dry_run=False)
    histograms = R._load_histograms(
        fixture.run, records["d2-predict"]["result"]["product"]
    )
    histograms["step"]["P"][0, 0, 0, 0] += 1
    monkeypatch.setattr(R, "aggregate", lambda *_args, **_kwargs: (histograms, {}))
    with pytest.raises(R.Refused, match="PREDICTION_REPRODUCED"):
        R._c0(inputs, records)


def test_wall_clock_and_price_guards(
    fixture: Fixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    inputs = fixture.inputs()
    p0_record = R.p0(inputs)
    inputs.started -= 7201
    with pytest.raises(R.Refused, match="WALL_CLOCK"):
        R.aggregate(inputs, p0_record, None, data=False)
    fixture.run = fixture.root / "expensive-run"
    fixture.execute("pins")
    times = iter((0.0, 1000.0))
    monkeypatch.setattr(R.time, "perf_counter", lambda: next(times))
    fixture.execute("p0")
    with pytest.raises(R.Refused, match="PRICE_REVIEW"):
        fixture.execute("d2-predict")

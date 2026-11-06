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


class FluxHistogramDouble:
    """Small ROOT protocol double; this does not certify a MAT histogram."""

    def __init__(self, edges: Any, values: Any):
        self.edges = np.asarray(edges, dtype=float)
        self.values = np.asarray(values, dtype=float)
        self.calls: list[tuple[str, float]] = []

    def GetXaxis(self) -> Any:
        return SimpleNamespace(
            GetTitle=lambda: "E_nu (GeV)",
            GetXmin=lambda: self.edges[0],
            GetXmax=lambda: self.edges[-1],
            GetBinLowEdge=lambda i: self.edges[i - 1],
        )

    def GetTitle(self) -> str:
        return "constrained flux"

    def GetYaxis(self) -> Any:
        return SimpleNamespace(GetTitle=lambda: "flux convention shared by fixture")

    def Interpolate(self, value: float) -> float:
        self.calls.append(("interpolate", value))
        centers = (self.edges[:-1] + self.edges[1:]) / 2
        return float(np.interp(value, centers, self.values))

    def FindBin(self, value: float) -> int:
        self.calls.append(("bin", value))
        return int(np.searchsorted(self.edges, value, side="right"))

    def GetBinContent(self, index: int) -> float:
        return float(self.values[index - 1]) if 1 <= index <= len(self.values) else 0.0

    def GetBinError(self, index: int) -> float:
        return self.GetBinContent(index) / 10

    def GetNbinsX(self) -> int:
        return len(self.values)

    def InheritsFrom(self, name: str) -> bool:
        return name == "PlotUtils::MnvH1D"

    def ClassName(self) -> str:
        return "PlotUtils::MnvH1D"


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
        text = "selected_CV_spectrum_is_numerator\ncommon_generator_histogram_is_denominator\nplaylist_mapping_is_1D_1M_1N\nall_spectra_share_one_convention\n"
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
                                "common_units_convention",
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
        if not hasattr(self, "fixture_flux_spectra"):
            self.fixture_flux_spectra = {}
            for group in ("1D", "1M", "1N"):
                path = self.flux / f"{group}.root"
                with uproot.open(path) as root_file:
                    values, edges = root_file["CV"].to_numpy(flow=False)
                    errors = root_file["CV"].errors(flow=False)
                self.fixture_flux_spectra[group] = {
                    "histogram": "CV",
                    "class_name": "PlotUtils::MnvH1D",
                    "original_path": str(path),
                    "sha256": R.digest(path),
                    "bytes": path.stat().st_size,
                    "path_opened": "$FIXTURE/staged-root",
                    "opened_by": "synthetic extract fixture; no PyROOT class claim",
                    "retention": "local disposable fixture",
                    "values": values.tolist(),
                    "edges": edges.tolist(),
                    "errors": errors.tolist(),
                    "title": "constrained flux",
                    "axis_titles": {"x": "E_nu (GeV)", "y": "fixture density"},
                    "file_units_metadata": {},
                    "generated_spectrum": {"edges": edges.tolist()},
                }
        extracted = self.root / "flux-extract-fixture.json"
        if not hasattr(self, "fixture_factor_products"):
            self.fixture_factor_products = {}
            histograms = {
                group: FluxHistogramDouble(spec["edges"], spec["values"])
                for group, spec in self.fixture_flux_spectra.items()
            }
            for playlist in R.PLAYLISTS:
                with np.load(self.dump / f"lat_{playlist}.npz") as archive:
                    truth, passed, weights = (
                        archive["MCgen"],
                        archive["pass_reco"],
                        archive["w_reco"],
                    )
                proton, _, _ = R.reconstructed_energy(truth, R.M_PROTON)
                neutron, _, _ = R.reconstructed_energy(truth, R.M_NEUTRON)
                energy = np.where(passed, (proton + neutron) / 2, np.nan)
                arrays, counts = {}, {}
                for target in ("1D", "1M"):
                    factor, outside, patterns = R.mat_flux_swap(
                        energy,
                        histograms[R.OWN_FLUX[playlist]],
                        histograms[target],
                        FluxHistogramDouble([0, 128], [1]),
                    )
                    arrays[f"factor_{target}"], arrays[f"outside_{target}"] = (
                        factor,
                        outside,
                    )
                    counts[target] = R.zero_pattern_counts(patterns, passed, weights)
                product = self.root / f"fixture-factors-{playlist}.npz"
                np.savez(product, **arrays)
                self.fixture_factor_products[playlist] = {
                    "path": str(product),
                    "sha256": R.digest(product),
                    "rows": len(energy),
                    "zero_patterns": counts,
                }
        for playlist, product in self.fixture_factor_products.items():
            product["signal_sha256"] = R.digest(self.dump / f"lat_{playlist}.npz")
        record = {
            "schema": "fd-rpd-reco-flux-extract/2",
            "step": "flux-extract",
            "status": "PASS",
            "run_class": "local_fixture",
            "fixture_only": True,
            "code_sha256": R.digest(Path(R.__file__)),
            "selection_sha256": R.flux_selection_digest(self.config),
            "mat_environment": {
                "plotutils_mnvh1d_dictionary": True,
                "instrument_sha256": R.digest(REPO / "nd-unfolding/fd_rpd_inputs.py"),
                "scope": "synthetic handoff fixture; not a MAT environment verification",
            },
            "spectra": self.fixture_flux_spectra,
            "factor_products": self.fixture_factor_products,
        }
        extracted.write_text(json.dumps(record))
        self.config["flux_extract"] = {
            "path": str(extracted),
            "sha256": R.digest(extracted),
        }
        custody = self.root / "flux-custody-fixture.json"
        custody.write_text(
            json.dumps(
                {
                    "schema": "fd-rpd-reco-flux-custody/1",
                    "custody_code_sha256": R.digest(
                        REPO / "nd-unfolding/fd_rpd_reco_custody.py"
                    ),
                    "status": "PASS",
                    "extract_sha256": R.digest(extracted),
                    "code_sha256": R.digest(Path(R.__file__)),
                    "trace_sha256": "f" * 64,
                    "fixture_only": True,
                    "scope": "synthetic custody fixture; no runtime trace claim",
                }
            )
        )
        self.config["flux_custody"] = {
            "path": str(custody),
            "sha256": R.digest(custody),
        }
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
    inputs.prediction = fixture.prediction_repo / "missing.json", sha
    with pytest.raises(R.Refused, match="PREDICTION_SHA"):
        inputs.key("lat_1A.npz", "measured")
    inputs.prediction = prediction, sha
    local = fixture.run / "d2-predict.json"
    original_local = local.read_bytes()
    local.write_bytes(original_local + b" ")
    with pytest.raises(R.Refused, match="PREDICTION_SHA"):
        inputs.key("lat_1A.npz", "measured")
    local.write_bytes(original_local)
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


def test_p0_pinned_extract_and_no_data(fixture: Fixture) -> None:
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
    own = FluxHistogramDouble([0, 2, 4], [1, 2])
    target = FluxHistogramDouble([1, 2, 3], [3, 4])
    factors, outside, _ = R.mat_flux_swap(
        np.array([0.5, 1.0, 2.0, 3.0]), own, target, FluxHistogramDouble([0, 4], [1])
    )
    np.testing.assert_array_equal(factors, [1, 3, 3.5 / 1.5, 1])
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
    own = FluxHistogramDouble([0, 1], [-1])
    with pytest.raises(R.Refused, match="FLUX_SUPPORT"):
        R.mat_flux_swap(np.array([0.5]), own, own, FluxHistogramDouble([0, 1], [1]))
    with pytest.raises(R.Refused, match="FLUX_LAYOUT"):
        R.validate_flux_spectrum(
            {"values": [-1.0, 2.0], "edges": [0.0, 1.0, 2.0], "errors": [0.0, 0.0]}
        )
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


def test_output_location_before_any_write(
    fixture: Fixture,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    forbidden = Path("/global/cfs/cdirs/fixture/rpd-output")
    real_mkdir = Path.mkdir

    def checked_mkdir(path: Path, *args: Any, **kwargs: Any) -> None:
        assert Path("/global/cfs") not in path.resolve().parents
        real_mkdir(path, *args, **kwargs)

    monkeypatch.setattr(Path, "mkdir", checked_mkdir)
    R.require_output_root(fixture.run)
    with pytest.raises(R.Refused, match="OUTPUT_LOCATION"):
        R.Inputs(fixture.config_path, fixture.config_sha, forbidden)
    assert (
        R.main(
            [
                "pins",
                "--config",
                str(fixture.config_path),
                "--config-sha256",
                fixture.config_sha,
                "--run",
                str(forbidden),
            ]
        )
        == 4
    )
    assert "STOP OUTPUT_LOCATION" in capsys.readouterr().err


@pytest.mark.parametrize("seed", [17, 43])
@pytest.mark.parametrize("extra", ["extra.npz", "nn_2A.npz"])
def test_known_siblings_are_stat_only(
    tmp_path: Path, standin_noatime: None, seed: int, extra: str
) -> None:
    fixture = Fixture(tmp_path, seed=seed)
    siblings = {}
    for playlist in R.PLAYLISTS:
        path = fixture.dump / f"nn_{playlist}.npz"
        path.write_bytes(f"not an NPZ; never open {playlist}".encode())
        info = path.stat()
        siblings[path.name] = {
            "name": path.name,
            "bytes": info.st_size,
            "mtime_ns": info.st_mtime_ns,
        }
    active = [True]

    def forbid_sibling_open(event: str, arguments: tuple[Any, ...]) -> None:
        if (
            active[0]
            and event == "open"
            and isinstance(arguments[0], (str, bytes, os.PathLike))
        ):
            path = Path(os.fsdecode(arguments[0]))
            assert not (
                path.parent == fixture.dump and path.name in siblings
            ), "known sibling was opened"

    sys.addaudithook(forbid_sibling_open)
    try:
        result = fixture.execute("pins")["result"]
        assert result["n_files"] == 24
        assert result["known_siblings_stat_only"] == [
            siblings[name] for name in sorted(siblings)
        ]
        inputs = fixture.inputs()
        assert set(inputs.pins) == {
            f"lat_{playlist}{suffix}.npz"
            for playlist in R.PLAYLISTS
            for suffix in ("", "_bkg")
        }
        (fixture.dump / extra).write_bytes(b"unknown sibling")
        fixture.run = fixture.root / "refused-extra"
        with pytest.raises(R.Refused, match="PIN_SET"):
            fixture.execute("pins")
    finally:
        active[0] = False


def _intercept_cfs_writes(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    writes: list[str] = []
    real_mkdir, real_open = Path.mkdir, Path.open

    def on_cfs(path: Path) -> bool:
        return path == Path("/global/cfs") or Path("/global/cfs") in path.parents

    def checked_mkdir(path: Path, *args: Any, **kwargs: Any) -> None:
        if on_cfs(path):
            writes.append("mkdir")
            raise AssertionError("CFS mkdir attempted")
        real_mkdir(path, *args, **kwargs)

    def checked_open(path: Path, *args: Any, **kwargs: Any) -> Any:
        if on_cfs(path):
            writes.append("open")
            raise AssertionError("CFS file open attempted")
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, "mkdir", checked_mkdir)
    monkeypatch.setattr(Path, "open", checked_open)
    return writes


@pytest.mark.parametrize("failure", ["threads", "nice", "dry-run", "output-exists"])
def test_cfs_precedes_other_refusals(
    fixture: Fixture,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    failure: str,
) -> None:
    writes = _intercept_cfs_writes(monkeypatch)
    guards: list[str] = []
    original_require = R.require

    def track_require(condition: bool, guard: str, message: str) -> None:
        guards.append(guard)
        original_require(condition, guard, message)

    monkeypatch.setattr(R, "require", track_require)
    for key in R.THREAD_KEYS:
        monkeypatch.setenv(key, "1")
    if failure == "threads":
        monkeypatch.setenv("OMP_NUM_THREADS", "4")
    if failure == "nice":
        monkeypatch.setattr(os, "getpriority", lambda *_args: 0)
        monkeypatch.setattr(os, "nice", lambda *_args: 0)
    forbidden = Path("/global/cfs/cdirs/fixture/rpd-output")
    arguments = [
        "d1" if failure == "dry-run" else "pins",
        "--config",
        str(fixture.config_path),
        "--config-sha256",
        fixture.config_sha,
        "--run",
        str(forbidden),
    ]
    if failure == "dry-run":
        arguments += ["--dry-run"]
    if failure == "output-exists":
        original_exists = Path.exists
        monkeypatch.setattr(
            Path,
            "exists",
            lambda path: path == forbidden / "pins.json" or original_exists(path),
        )
    assert R.main(arguments) == 4
    assert guards[0] == "OUTPUT_LOCATION"
    assert "STOP OUTPUT_LOCATION" in capsys.readouterr().err
    assert writes == []
    with pytest.raises(R.Refused, match="OUTPUT_LOCATION"):
        R.run_stage(
            fixture.config_path, fixture.config_sha, forbidden, "d1", dry_run=True
        )
    assert writes == []


def test_cfs_handler_rechecks_before_stop_write(
    fixture: Fixture,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    writes = _intercept_cfs_writes(monkeypatch)
    original_guard = R.require_output_root
    calls = []

    def entry_then_handler(path: Path) -> None:
        calls.append(path)
        if len(calls) > 1:
            original_guard(path)

    monkeypatch.setattr(R, "require_output_root", entry_then_handler)
    monkeypatch.setenv("OMP_NUM_THREADS", "4")
    forbidden = Path("/global/cfs/cdirs/fixture/changed-output")
    assert (
        R.main(
            [
                "pins",
                "--config",
                str(fixture.config_path),
                "--config-sha256",
                fixture.config_sha,
                "--run",
                str(forbidden),
            ]
        )
        == 4
    )
    assert len(calls) == 2
    assert writes == []
    assert "STOP OUTPUT_LOCATION" in capsys.readouterr().err


@pytest.mark.parametrize("invalid", [-1, 0, 165601])
def test_priced_wall_budget_limits(
    fixture: Fixture,
    monkeypatch: pytest.MonkeyPatch,
    invalid: int,
) -> None:
    assert R.wall_budget_seconds(None) == 7200
    assert R.wall_budget_seconds(1, 0.026) == 1
    assert R.wall_budget_seconds(165600, 0.026) == 165600
    with pytest.raises(R.Refused, match="WALL_BUDGET"):
        R.wall_budget_seconds(invalid, 0.026)
    destination = fixture.root / f"invalid-budget-{invalid}"
    assert (
        R.main(
            [
                "pins",
                "--config",
                str(fixture.config_path),
                "--config-sha256",
                fixture.config_sha,
                "--run",
                str(destination),
                "--priced-wall-seconds",
                str(invalid),
                "--measured-seconds-per-draw",
                "0.026",
            ]
        )
        == 4
    )
    stop = json.loads((destination / "pins.STOP.json").read_text())
    assert stop["guard"] == "WALL_BUDGET"
    assert stop["priced_wall_seconds"] == invalid
    assert stop["wall_budget_seconds"] == invalid
    assert stop["readings"] is None


def test_priced_wall_budget_admission_and_elapsed(
    fixture: Fixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture.execute("pins")
    clock = iter((0.0, 1000.0))
    monkeypatch.setattr(R.time, "perf_counter", lambda: next(clock))
    p0 = fixture.execute("p0")
    price = p0["result"]["runtime_estimate"]
    assert price["needs_director_price"]
    own_price = price["steps"]["d2-predict"]["planning_seconds_with_factor_10"]
    assert 7200 < own_price < 8000
    assert price["steps"]["c0"]["planning_seconds_with_factor_10"] > 165600
    with pytest.raises(R.Refused, match="PRICE_REVIEW"):
        fixture.execute("d2-predict")
    with pytest.raises(R.Refused, match="PRICE_REVIEW"):
        fixture.execute(
            "d2-predict", priced_wall_seconds=7000, **_timing_options(fixture, 0.026)
        )
    prediction = fixture.execute(
        "d2-predict", priced_wall_seconds=8000, **_timing_options(fixture, 0.026)
    )
    assert prediction["wall_budget_seconds"] == 8000
    assert prediction["priced_wall_seconds"] == 8000
    assert p0["wall_budget_seconds"] == 7200 and p0["priced_wall_seconds"] is None
    assert (
        sum(step["poisson_draws"] for step in price["steps"].values())
        == price["poisson_draws"]
    )
    inputs = R.Inputs(
        fixture.config_path,
        fixture.config_sha,
        fixture.run,
        priced_wall_seconds=8000,
        **_timing_options(fixture, 0.026),
    )
    inputs.started -= 7201
    inputs.check_wall_clock()
    inputs.started -= 800
    with pytest.raises(R.Refused, match="WALL_CLOCK"):
        inputs.check_wall_clock()


@pytest.mark.parametrize("seed", [17, 43])
def test_p0_records_actual_environment(
    tmp_path: Path,
    standin_noatime: None,
    seed: int,
) -> None:
    import scipy

    fixture = Fixture(tmp_path, seed=seed)
    pins = fixture.execute("pins")
    p0 = fixture.execute(
        "p0", priced_wall_seconds=8000, **_timing_options(fixture, 0.026)
    )
    environment = p0["result"]["environment"]
    assert environment["interpreter"] == sys.executable
    assert environment["resolved_interpreter"] == str(Path(sys.executable).resolve())
    assert environment["python"] == sys.version.split()[0]
    assert environment["numpy"] == np.__version__
    assert environment["scipy"] == scipy.__version__
    assert environment["uproot"] == uproot.__version__
    assert pins["wall_budget_seconds"] == 7200
    assert p0["wall_budget_seconds"] == 8000
    assert p0["priced_wall_seconds"] == 8000


def _timing_options(fixture: Fixture, rate: float) -> dict[str, Any]:
    record = {
        "seconds_per_draw": rate,
        "chunk_shape": {
            "rows": R.CHUNK_ROWS,
            "bootstrap_replicas": R.BOOTSTRAPS,
            "weight_variants": 5,
            "axes": list(R.TIMING_AXES),
            "pass": "real-signal",
        },
        "environment": R.runtime_environment(),
        "scope": "synthetic timing provenance for local guard tests only",
    }
    path = fixture.root / "timing-record.json"
    path.write_text(json.dumps(record))
    return {
        "measured_seconds_per_draw": rate,
        "timing_record": path,
        "timing_record_sha256": R.digest(path),
    }


@pytest.mark.parametrize("priced,measured", [(8000, None), (None, 0.026)])
def test_priced_timing_pair_refuses(
    fixture: Fixture,
    capsys: pytest.CaptureFixture[str],
    priced: int | None,
    measured: float | None,
) -> None:
    with pytest.raises(R.Refused, match="PRICED_TIMING_PAIR"):
        R.wall_budget_seconds(priced, measured)
    destination = fixture.root / "pair-stop"
    arguments = [
        "pins",
        "--config",
        str(fixture.config_path),
        "--config-sha256",
        fixture.config_sha,
        "--run",
        str(destination),
    ]
    if priced is not None:
        arguments += ["--priced-wall-seconds", str(priced)]
    if measured is not None:
        arguments += ["--measured-seconds-per-draw", str(measured)]
    assert R.main(arguments) == 4
    stop = json.loads((destination / "pins.STOP.json").read_text())
    assert stop["guard"] == "PRICED_TIMING_PAIR"
    assert stop["priced_wall_seconds"] == priced
    assert stop["measured_seconds_per_draw"] == measured
    assert stop["planned_seconds"] is None
    assert stop["estimate_status"] == "unavailable_before_input_metadata"
    assert stop["readings"] is None


@pytest.mark.parametrize("invalid", [0.0, -0.1, float("nan"), float("inf")])
def test_measured_rate_refuses(invalid: float) -> None:
    assert R.wall_budget_seconds(8000, 0.026) == 8000
    with pytest.raises(R.Refused, match="MEASURED_RATE"):
        R.wall_budget_seconds(8000, invalid)


@pytest.mark.parametrize(
    "defect,guard",
    [
        ("missing", "TIMING_SOURCE"),
        ("sha", "INPUT_DIGEST"),
        ("rate", "TIMING_SHAPE"),
        ("shape", "TIMING_SHAPE"),
        ("environment", "TIMING_ENVIRONMENT"),
    ],
)
def test_timing_record_guards(fixture: Fixture, defect: str, guard: str) -> None:
    options = _timing_options(fixture, 0.026)
    inputs = R.Inputs(
        fixture.config_path,
        fixture.config_sha,
        fixture.run,
        priced_wall_seconds=8000,
        **options,
    )
    assert inputs.timing_source["sha256"] == options["timing_record_sha256"]
    assert inputs.timing_source["record"]["chunk_shape"]["weight_variants"] == 5
    assert str(options["timing_record"]) in inputs.hashes
    fixture.run = fixture.root / "bad-timing-run"
    if defect == "missing":
        options.pop("timing_record")
    elif defect == "sha":
        options["timing_record_sha256"] = "a" * 64
    else:
        record = json.loads(options["timing_record"].read_text())
        if defect == "rate":
            record["seconds_per_draw"] *= 2
        elif defect == "shape":
            record["chunk_shape"]["weight_variants"] = 1
        else:
            record["environment"]["numpy"] = "wrong-version"
        options["timing_record"].write_text(json.dumps(record))
        options["timing_record_sha256"] = R.digest(options["timing_record"])
    with pytest.raises(R.Refused, match=guard):
        R.Inputs(
            fixture.config_path,
            fixture.config_sha,
            fixture.run,
            priced_wall_seconds=8000,
            **options,
        )


def test_measured_plan_and_price_stop_receipt(fixture: Fixture) -> None:
    fixture.execute("pins")
    p0 = fixture.execute("p0")
    options = _timing_options(fixture, 0.026)
    inputs = R.Inputs(
        fixture.config_path,
        fixture.config_sha,
        fixture.run,
        priced_wall_seconds=8000,
        **options,
    )
    estimate = p0["result"]["runtime_estimate"]
    inputs.plan_step("d2-predict", estimate)
    draws = estimate["steps"]["d2-predict"]["poisson_draws"]
    assert inputs.step_estimate["planned_seconds"] == draws * 0.026 * 1.5
    assert inputs.execution()["planning_factor"] == 1.5
    assert inputs.execution()["timing_chunk_shape"]["axes"] == list(R.TIMING_AXES)
    inputs.plan_step("c0", estimate)
    assert inputs.step_estimate["planned_seconds"] > 165600
    arguments = [
        "d2-predict",
        "--config",
        str(fixture.config_path),
        "--config-sha256",
        fixture.config_sha,
        "--run",
        str(fixture.run),
        "--priced-wall-seconds",
        "7000",
        "--measured-seconds-per-draw",
        "0.026",
        "--timing-record",
        str(options["timing_record"]),
        "--timing-record-sha256",
        options["timing_record_sha256"],
    ]
    assert R.main(arguments) == 4
    stop = json.loads((fixture.run / "d2-predict.STOP.json").read_text())
    assert stop["guard"] == "PRICE_REVIEW"
    assert stop["planned_seconds"] == draws * 0.026 * 1.5
    assert stop["planning_factor"] == 1.5
    assert stop["priced_wall_seconds"] == 7000
    assert stop["measured_seconds_per_draw"] == 0.026
    assert stop["timing_source"]["sha256"] == options["timing_record_sha256"]
    assert stop["readings"] is None


def test_draft_configuration_refuses(fixture: Fixture) -> None:
    assert fixture.execute("pins")["result"]["n_files"] == 24
    fixture.config["configuration_status"] = "DRAFT_UNRESOLVED_RUNTIME"
    fixture.save_config()
    fixture.run = fixture.root / "draft-config"
    with pytest.raises(R.Refused, match="CONFIG_READY"):
        fixture.execute("pins")


def test_timing_shape_matches_actual_aggregate_axes(fixture: Fixture) -> None:
    inputs = fixture.inputs()
    bins = R.step0(inputs)
    values = inputs.key("lat_1A.npz", "MCreco")
    assignments = R.axis_assignments(values, bins)
    assert sorted(assignments) == list(R.TIMING_AXES)
    assert len(assignments) == 23


class _RootDouble:
    """Mechanical TFile/MnvH1D protocol double; never a real MAT class test."""

    def __init__(
        self,
        *,
        missing: bool = False,
        wrong_class: bool = False,
        zombie: bool = False,
        no_file: bool = False,
    ):
        owner = self
        self.opened: list[str] = []
        self.closed = 0
        self.gROOT = SimpleNamespace(GetVersion=lambda: "fixture-root")

        class Hist:
            def InheritsFrom(self, name: str) -> bool:
                return name == "PlotUtils::MnvH1D" and not wrong_class

            def ClassName(self) -> str:
                return "TH1D" if wrong_class else "PlotUtils::MnvH1D"

            def GetNbinsX(self) -> int:
                return 2

            def GetXaxis(self) -> Any:
                return SimpleNamespace(GetBinLowEdge=lambda i: float(i - 1))

            def GetBinContent(self, i: int) -> float:
                return float(i)

            def GetBinError(self, i: int) -> float:
                return float(i) / 10

        class File:
            def GetListOfKeys(self) -> list[Any]:
                return []

            def IsZombie(self) -> bool:
                return zombie

            def Get(self, name: str) -> Any:
                return None if missing or name != "CV" else Hist()

            def Close(self) -> None:
                owner.closed += 1

        class TFile:
            @staticmethod
            def Open(path: str, mode: str) -> Any:
                owner.opened.append(path)
                assert mode == "READ"
                return None if no_file else File()

        self.TFile = TFile


def _mock_mat_checks(
    monkeypatch: pytest.MonkeyPatch, root: Any, *, dictionary: bool = True
) -> list[str]:
    calls: list[str] = []

    def setup(_unused: Any) -> int:
        calls.append("setup")
        return 0

    def environment() -> dict[str, Any]:
        calls.append("environment")
        return {
            "plotutils_mnvh1d_dictionary": dictionary,
            "scope": "local protocol double only",
        }

    instrument = SimpleNamespace(
        __file__=str(REPO / "nd-unfolding/fd_rpd_inputs.py"),
        run_check_mat_setup=setup,
        mat_environment=environment,
    )
    monkeypatch.setattr(R, "load_mat_instrument", lambda: instrument)
    monkeypatch.setitem(sys.modules, "ROOT", root)
    return calls


def test_tfile_guard_both_entries(fixture: Fixture) -> None:
    source = fixture.flux / "1D.root"
    staged = fixture.root / "checked.root"
    R.stage_copy(source, staged, R.digest(source))
    root = _RootDouble()
    original = root.TFile
    with R.guarded_tfile(root, [staged]):
        assert root.TFile.Open(str(staged), "READ") is not None
        for open_file in (root.TFile.Open, root.TFile):
            with pytest.raises(R.Refused, match="MAT_TFILE_STAGE"):
                open_file(str(source), "READ")
            with pytest.raises(R.Refused, match="MAT_TFILE_STAGE"):
                open_file(str(staged), "RECREATE")
    assert root.TFile is original
    assert root.opened == [str(staged)]


@pytest.mark.parametrize(
    "defect,guard",
    [
        ("missing", "FLUX_HISTOGRAM"),
        ("wrong_class", "MAT_MNVH1D"),
        ("zombie", "MAT_ROOT_FILE"),
        ("no_file", "MAT_ROOT_FILE"),
    ],
)
def test_pyroot_reader_protocol_guards(
    fixture: Fixture, defect: str, guard: str
) -> None:
    source = fixture.flux / "1D.root"
    staged = fixture.root / "checked.root"
    R.stage_copy(source, staged, R.digest(source))
    valid = _RootDouble()
    result = R.read_flux_histogram(staged, "CV", root=valid)
    assert result["class_name"] == "PlotUtils::MnvH1D"
    np.testing.assert_array_equal(result["edges"], [0, 1, 2])
    np.testing.assert_array_equal(result["values"], [1, 2])
    np.testing.assert_array_equal(result["errors"], [0.1, 0.2])
    assert valid.closed == 1
    with pytest.raises(R.Refused, match=guard):
        R.read_flux_histogram(staged, "CV", root=_RootDouble(**{defect: True}))


@pytest.mark.parametrize("dictionary", [True, False])
def test_mat_environment_reuses_instrument(
    fixture: Fixture, monkeypatch: pytest.MonkeyPatch, dictionary: bool
) -> None:
    root = _RootDouble()
    calls = _mock_mat_checks(monkeypatch, root, dictionary=dictionary)
    if dictionary:
        observed, environment = R.checked_mat_environment()
        assert observed is root
        assert environment["instrument_sha256"] == R.digest(
            REPO / "nd-unfolding/fd_rpd_inputs.py"
        )
    else:
        with pytest.raises(R.Refused, match="MAT_ENVIRONMENT"):
            R.checked_mat_environment()
    assert calls == ["setup", "environment"]
    assert root.opened == []


@pytest.mark.parametrize(
    "defect,guard",
    [
        ("missing", "FLUX_EXTRACT"),
        ("status", "FLUX_EXTRACT"),
        ("code", "FLUX_EXTRACT"),
        ("selection_digest", "FLUX_EXTRACT_IDENTITY"),
        ("sha", "INPUT_DIGEST"),
    ],
)
def test_flux_extract_identity_guards(
    fixture: Fixture, defect: str, guard: str
) -> None:
    if defect == "missing":
        fixture.config.pop("flux_extract")
    elif defect == "sha":
        fixture.config["flux_extract"]["sha256"] = "a" * 64
    else:
        spec = fixture.config["flux_extract"]
        path = Path(spec["path"])
        record = json.loads(path.read_text())
        if defect == "status":
            record["status"] = "STOP"
        elif defect == "code":
            record["code_sha256"] = "a" * 64
        else:
            record["selection_sha256"] = "a" * 64
        path.write_text(json.dumps(record))
        spec["sha256"] = R.digest(path)
        custody_path = Path(fixture.config["flux_custody"]["path"])
        custody = json.loads(custody_path.read_text())
        custody["extract_sha256"] = R.digest(path)
        custody_path.write_text(json.dumps(custody))
        fixture.config["flux_custody"]["sha256"] = R.digest(custody_path)
    fixture.config_path.write_text(json.dumps(fixture.config))
    fixture.config_sha = R.digest(fixture.config_path)
    fixture.execute("pins")
    with pytest.raises(R.Refused, match=guard):
        fixture.execute("p0")


def test_mat_environment_failure_exit_code(
    fixture: Fixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    def unavailable() -> Any:
        raise RuntimeError("controlled pinned setup refusal")

    monkeypatch.setattr(R, "load_mat_instrument", unavailable)
    original_check = R.checked_mat_environment
    monkeypatch.setattr(
        R, "checked_mat_environment", lambda _inputs=None: original_check()
    )
    assert (
        R.main(
            [
                "flux-extract",
                "--config",
                str(fixture.config_path),
                "--config-sha256",
                fixture.config_sha,
                "--run",
                str(fixture.run),
            ]
        )
        == 7
    )
    stop = json.loads((fixture.run / "flux-extract.STOP.json").read_text())
    assert stop["guard"] == "MAT_ENVIRONMENT"
    assert stop["readings"] is None


def test_a1_root_interpolation_and_boundary() -> None:
    energy = np.array([74.999, 75.0, 75.001])
    own = FluxHistogramDouble([0, 50, 100], [2, 4])
    target = FluxHistogramDouble([0, 50, 100], [6, 8])
    generated = FluxHistogramDouble([0, 100], [3])
    factors, outside, _ = R.mat_flux_swap(energy, own, target, generated)
    expected = np.array(
        [target.Interpolate(float(e)) / own.Interpolate(float(e)) for e in energy[:2]]
        + [8 / 4]
    )
    np.testing.assert_allclose(factors, expected, rtol=1e-14)
    assert not outside.any()
    assert own.calls[:3] == [
        ("interpolate", 74.999),
        ("interpolate", 75.0),
        ("bin", 75.001),
    ]
    # A point well away from the centers discriminates interpolation from bins.
    factor, _, _ = R.mat_flux_swap(np.array([50.0]), own, target, generated)
    assert factor[0] == pytest.approx(7 / 3)
    assert factor[0] != 8 / 4


@pytest.mark.parametrize("pattern", range(8))
def test_a1_every_zero_pattern(pattern: int) -> None:
    values = [
        0.0 if pattern & (1 << i) else value for i, value in enumerate((2.0, 6.0, 4.0))
    ]
    own, target, generated = [FluxHistogramDouble([0, 100], [v]) for v in values]
    factors, outside, codes = R.mat_flux_swap(
        np.array([50.0, 50.0]), own, target, generated
    )
    w_own = 1 if values[0] == 0 or values[2] == 0 else values[0] / values[2]
    w_target = 1 if values[1] == 0 or values[2] == 0 else values[1] / values[2]
    np.testing.assert_array_equal(factors, [w_target / w_own] * 2)
    np.testing.assert_array_equal(codes, [pattern] * 2)
    assert not outside.any()
    counts = R.zero_pattern_counts(codes, np.array([True, True]), np.array([2.0, 0.0]))
    assert counts[str(pattern)]["count"] == 2
    assert counts[str(pattern)]["pass_reco_weight_share"] == 1
    assert sum(record["count"] for record in counts.values()) == 2


def test_flux_custody_and_factor_guards(fixture: Fixture) -> None:
    inputs = fixture.inputs()
    products = fixture.fixture_factor_products
    assert R.pinned_flux_factors(inputs, products, "1A", 64)["factor_1D"].shape == (64,)
    for defect in ("rows", "signal_sha256"):
        wrong = json.loads(json.dumps(products))
        wrong["1A"][defect] = 65 if defect == "rows" else "a" * 64
        with pytest.raises(R.Refused, match="FLUX_FACTORS"):
            R.pinned_flux_factors(inputs, wrong, "1A", 64)
    fixture.config.pop("flux_custody")
    fixture.config_path.write_text(json.dumps(fixture.config))
    fixture.config_sha = R.digest(fixture.config_path)
    fixture.run = fixture.root / "custody-refusal"
    fixture.execute("pins")
    with pytest.raises(R.Refused, match="FLUX_CUSTODY"):
        fixture.execute("p0")


def _custody_module() -> Any:
    path = Path(
        os.environ.get(
            "FD_RPD_CUSTODY_MODULE", REPO / "nd-unfolding/fd_rpd_reco_custody.py"
        )
    )
    spec = importlib.util.spec_from_file_location("rpd_custody_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_custody_trace_directions() -> None:
    custody = _custody_module()
    policy = {
        "cwd": "/run/extract",
        "protected_roots": [
            "/original/data",
            "/constraint.txt",
            "/mat/FluxReweighter.cxx",
        ],
        "allowed": {
            "staged_data": ["/run/extract/mat-data"],
            "run": ["/run/extract"],
            "system": ["/etc", "/usr", "/proc"],
            "environment": ["/env"],
            "pinned_mat_libs": ["/mat/libMAT.so"],
        },
        "failed_prefixes": ["/optional/lib"],
    }
    lines = [
        '13 openat(AT_FDCWD, "/etc/ld.so.cache", O_RDONLY|O_CLOEXEC) = 3</etc/ld.so.cache>',
        '13 openat(AT_FDCWD, "/optional/lib/not-here.so", O_RDONLY) = -1 ENOENT (No such file or directory)',
        '13 openat(4</run/extract/mat-data>, "flux.root", O_RDONLY) = 5</run/extract/mat-data/flux.root>',
    ]
    result = custody.classify_trace(lines, policy)
    assert result["successful_open_counts"] == {"system": 1, "staged_data": 1}
    assert result["failed_nonprotected_counts"] == {"/optional/lib": 1}
    bad_lines = [
        '13 openat(AT_FDCWD, "/mat/FluxReweighter.cxx", O_RDONLY) = 3</mat/FluxReweighter.cxx>',
        '13 openat(AT_FDCWD, "/original/data/not-here", O_RDONLY) = -1 ENOENT (No such file or directory)',
        '13 openat(AT_FDCWD, "/constraint.txt", O_RDONLY) = 3</constraint.txt>',
        '13 openat(AT_FDCWD, "/unknown/other.root", O_RDONLY) = 3</unknown/other.root>',
        '13 openat(4, "relative.root", O_RDONLY) = 3',
        '13 openat(AT_FDCWD, "/run/extract/link", O_RDONLY) = 3</original/data/a.root>',
    ]
    for line in bad_lines:
        with pytest.raises(custody.CustodyRefused):
            custody.classify_trace(lines + [line], policy)


def test_cov2d_fence_both_directions(monkeypatch: pytest.MonkeyPatch) -> None:
    custody = _custody_module()
    responses = []

    def run(command: list[str], **_kwargs: Any) -> Any:
        responses.append(command[0])
        return SimpleNamespace(
            returncode=0,
            stdout=(
                ""
                if command[0] == "squeue"
                else "60909280|COMPLETED|\n60911676|FAILED|\n"
            ),
            stderr="",
        )

    monkeypatch.setattr(custody.subprocess, "run", run)
    assert custody.cov2d_fence()["exit_code"] == 0
    assert responses == ["squeue", "sacct"]
    for queue, accounting, code in (
        ("60909280|cov2d-test|RUNNING|0|2h\n", "", 0),
        ("", "60909280|COMPLETED|\n60911676|RUNNING|\n", 0),
        ("", "60909280|COMPLETED|\n", 0),
        ("", "", 1),
    ):
        monkeypatch.setattr(
            custody.subprocess,
            "run",
            lambda command, **kw: SimpleNamespace(
                returncode=code,
                stdout=queue if command[0] == "squeue" else accounting,
                stderr="",
            ),
        )
        with pytest.raises(custody.CustodyRefused) as caught:
            custody.cov2d_fence()
        assert caught.value.details["exit_code"] == 3
        assert caught.value.details["queue_stdout"] == queue


def test_staged_prefix_restore_and_missing(
    fixture: Fixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    prefixes = {
        key: str(fixture.root / key) for key in ("PLOTUTILSROOT", "MPARAMFILES")
    }
    for key, value in prefixes.items():
        Path(value).mkdir()
        monkeypatch.setenv(key, "original-" + key)
    with pytest.raises(RuntimeError):
        with R.staged_mat_prefixes(prefixes):
            assert {key: os.environ[key] for key in prefixes} == prefixes
            raise RuntimeError("controlled failure")
    assert os.environ["PLOTUTILSROOT"] == "original-PLOTUTILSROOT"
    assert os.environ["MPARAMFILES"] == "original-MPARAMFILES"
    Path(prefixes["MPARAMFILES"]).rmdir()
    with pytest.raises(R.Refused, match="MAT_DATA_STAGE"):
        with R.staged_mat_prefixes(prefixes):
            pass


def test_constrained_common_integral_bracket() -> None:
    own = {"edges": [0, 2, 4], "values": [10, 20]}
    target = {"edges": [1, 2, 3], "values": [60, 80]}
    assert R.common_flux_integral_ratio(own, target) == pytest.approx(140 / 30)
    with pytest.raises(R.Refused, match="FLUX_SUPPORT"):
        R.common_flux_integral_ratio(
            {"edges": [0, 1], "values": [0]}, {"edges": [0, 1], "values": [1]}
        )


def test_same_connect_prepare_receipt(
    fixture: Fixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    import time

    root = _RootDouble()
    root.TClass = SimpleNamespace(
        GetClass=lambda _name: SimpleNamespace(HasDictionary=lambda: True)
    )
    monkeypatch.setitem(sys.modules, "ROOT", root)
    monkeypatch.setenv("FD_RPD_RECO_CONNECT_ID", "unit-connect")
    instrument = SimpleNamespace(
        mapped_files=lambda: set(), mat_env_problems=lambda *args: []
    )
    monkeypatch.setattr(R, "load_mat_instrument", lambda: instrument)
    custody = _custody_module()
    prepared = {
        "run": str(fixture.run.resolve()),
        "connect_id": "unit-connect",
        "prepare_time_ns": time.time_ns(),
        "environment_after_setup": custody.environment_record(),
        "mapped_mat_stats": {},
        "instrument_files": [],
        "mat_environment": {
            "setup_sha256": {},
            "mat_sha256": {},
            "symlink": {"link": "target"},
        },
    }
    inputs = fixture.inputs()
    inputs.prestage = prepared
    assert R.checked_prepared_mat(inputs)[0] is root
    for key, bad in (
        ("run", "/foreign"),
        ("connect_id", "foreign"),
        ("prepare_time_ns", 0),
        ("environment_after_setup", {}),
    ):
        inputs.prestage = prepared | {key: bad}
        with pytest.raises(R.Refused, match="MAT_PREPARE"):
            R.checked_prepared_mat(inputs)
    inputs.prestage = prepared
    instrument.mat_env_problems = lambda *args: ["controlled mismatch"]
    with pytest.raises(R.Refused, match="MAT_ENVIRONMENT"):
        R.checked_prepared_mat(inputs)


def test_extract_missing_dependency_before_constructor(
    fixture: Fixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _RootDouble()
    monkeypatch.setattr(R, "checked_mat_environment", lambda _inputs=None: (root, {}))
    inputs = fixture.inputs()
    inputs.prestage = {
        "mat_prefixes": {},
        "mat_dependencies": [
            {"staged": str(fixture.root / "absent.root"), "sha256": "a" * 64}
        ],
    }
    # Resolve selections before assigning a strict manifest (the files are mechanical stand-ins).
    selected = R.selected_flux_files(fixture.inputs())
    monkeypatch.setattr(R, "selected_flux_files", lambda _inputs: selected)
    with pytest.raises(R.Refused, match="MAT_DATA_STAGE"):
        R.flux_extract(inputs, [])
    assert root.opened == []


def test_constrained_extract_protocol_roundtrip(
    fixture: Fixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Mechanical double checks constructor arguments and row custody, not MAT validity."""
    inputs = fixture.inputs()
    selected = R.selected_flux_files(inputs)
    sources = {
        Path(fixture.config[key]["path"]): fixture.config[key]["sha256"]
        for key in ("pins", "h2", "inventory", "constants", "flux_source")
    }
    sources.update({path: checksum for path, checksum in inputs.pins.values()})
    sources.update(
        {Path(item["original_path"]): item["sha256"] for item in selected.values()}
    )
    copies = {
        str(path.resolve()): {
            "staged": str(inputs.copy(path, checksum)),
            "sha256": checksum,
        }
        for path, checksum in sources.items()
    }
    prefixes = {key: str(fixture.run / key) for key in ("PLOTUTILSROOT", "MPARAMFILES")}
    for path in prefixes.values():
        Path(path).mkdir(parents=True)
    dependencies = [
        {
            "playlist_group": group,
            "pdg": 14,
            "role": "constrained-numerator-input",
            "environment_key": "PLOTUTILSROOT",
            "relative_path": f"data/flux/flux-gen2thin-pdg14-minervame{group}_rearrangedUniverses.root",
            "staged": copies[str(Path(item["original_path"]).resolve())]["staged"],
            "sha256": item["sha256"],
        }
        for group, item in selected.items()
    ]
    listing = {
        path.name: {
            "name": path.name,
            "bytes": path.stat().st_size,
            "mtime_ns": path.stat().st_mtime_ns,
        }
        for path in fixture.dump.iterdir()
    }
    inputs.prestage = {
        "files": copies,
        "dump_listing": listing,
        "mat_prefixes": prefixes,
        "mat_dependencies": dependencies,
    }
    inputs.config["prestage"] = {"sha256": "a" * 64}
    calls = []
    spectra = {
        group: FluxHistogramDouble([0, 2, 4], [2 + i, 4 + i])
        for i, group in enumerate(("1D", "1M", "1N"))
    }

    class Reweighter:
        gen2thin = 2
        g4numiv6 = 1

        def __init__(self, *args: Any):
            calls.append(args)
            self.group = str(args[2])[-2:]

        def GetFluxReweighted(self, pdg: int) -> Any:
            assert pdg == 14
            return spectra[self.group]

        def GetFluxGenerated(self, pdg: int) -> Any:
            assert pdg == 14
            return FluxHistogramDouble([0, 2, 4], [1, 1])

    root = _RootDouble()
    root.PlotUtils = SimpleNamespace(FluxReweighter=Reweighter)
    root.std = SimpleNamespace(string=str)
    monkeypatch.setattr(
        R,
        "checked_mat_environment",
        lambda _inputs=None: (
            root,
            {
                "plotutils_mnvh1d_dictionary": True,
                "instrument_sha256": R.digest(REPO / "nd-unfolding/fd_rpd_inputs.py"),
            },
        ),
    )
    result = R.flux_extract(inputs, ["unit protocol"])
    assert calls == [
        (14, True, "minervame" + group, 2, 1, 100) for group in ("1D", "1M", "1N")
    ]
    assert all(row["key"] != "measured" for row in result["keys_read"])
    assert len(result["factor_products"]) == 12
    assert result["spectra"]["1D"]["integral"] == 12
    assert result["spectra"]["1D"]["raw_file_integral_descriptive_only"] == 3
    assert len(root.opened) == 6 and all(
        Path(p).is_relative_to(fixture.run / "staged") for p in root.opened
    )
    extract = fixture.run / "flux-extract.json"
    fixture.config["flux_extract"] = {"path": str(extract), "sha256": R.digest(extract)}
    receipt = fixture.root / "protocol-custody.json"
    receipt.write_text(
        json.dumps(
            {
                "schema": "fd-rpd-reco-flux-custody/1",
                "custody_code_sha256": R.digest(
                    REPO / "nd-unfolding/fd_rpd_reco_custody.py"
                ),
                "status": "PASS",
                "extract_sha256": R.digest(extract),
                "trace_sha256": "f" * 64,
                "code_sha256": R.digest(Path(R.__file__)),
                "fixture_only": True,
            }
        )
    )
    fixture.config["flux_custody"] = {"path": str(receipt), "sha256": R.digest(receipt)}
    fixture.config_path.write_text(json.dumps(fixture.config))
    fixture.config_sha = R.digest(fixture.config_path)
    fixture.run = fixture.root / "numeric-protocol"
    fixture.execute("pins")
    p0 = fixture.execute("p0")["result"]
    assert len(root.opened) == 6
    assert p0["spectra"]["1D"]["integral"] == 12
    assert p0["background_scale"]["1M"]["1D"] == pytest.approx(12 / 16)


def test_fresh_prepare_stages_closed_inventory(
    fixture: Fixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    custody = _custody_module()
    inventory = (
        REPO
        / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/rpd-reco/code-audit-fix-20261106/MAT-DATA-DEPENDENCIES.json"
    )
    entries = json.loads(inventory.read_text())["entries"]
    roots = {key: fixture.root / key for key in ("PLOTUTILSROOT", "MPARAMFILES")}
    for key, path in roots.items():
        path.mkdir()
        monkeypatch.setenv(key, str(path))
    for item in entries:
        path = roots[item["environment_key"]] / item["relative_path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        if item.get("role") == "constrained-numerator-input" and item.get("pdg") == 14:
            shutil.copyfile(fixture.flux / f'{item["playlist_group"]}.root', path)
        else:
            path.write_text("disposable native dependency stand-in\n")
    library = fixture.root / "libMAT.so"
    library.write_text("disposable instrument stand-in\n")
    instrument = SimpleNamespace(
        MAT_SETUP={}, MAT_FILES={str(library): R.digest(library)}
    )
    environment = {
        "mapped_mat_files": [str(library)],
        "mat_sha256": instrument.MAT_FILES,
        "setup_sha256": {},
        "plotutils_mnvh1d_dictionary": True,
    }
    monkeypatch.setattr(R, "load_mat_instrument", lambda: instrument)
    monkeypatch.setattr(R, "checked_mat_environment", lambda: (None, environment))
    monkeypatch.setattr(
        custody, "cov2d_fence", lambda: {"status": "PASS", "exit_code": 0}
    )
    # This test exercises stat comparisons; native O_NOATIME is a separate run-lane gate.
    stat = custody.source_stat
    monkeypatch.setattr(custody, "source_stat", lambda p: stat(p) | {"atime_ns": 0})
    monkeypatch.setenv("FD_RPD_RECO_CONNECT_ID", "fixture-prepare")
    fixture.config.update(
        {
            "configuration_status": "READY",
            "mat_dependencies": {"path": str(inventory), "sha256": R.digest(inventory)},
            "trace_environment_roots": ["/synthetic/env"],
            "cov2d_protected_paths": ["/synthetic/cov2d-input"],
        }
    )
    fixture.save_config()
    run = fixture.root / "fresh-prepare"
    prepared = custody.prepare(R, fixture.config_path, fixture.config_sha, run)
    assert len(prepared["mat_dependencies"]) == 15
    constraint = next(
        item
        for item in prepared["mat_dependencies"]
        if item["environment_key"] == "MPARAMFILES"
    )
    assert constraint["stat_before"] == constraint["stat_after"]
    assert (
        Path(constraint["staged"]).read_text()
        == "disposable native dependency stand-in\n"
    )
    policy = json.loads((run / "trace-policy.json").read_text())
    assert str(roots["MPARAMFILES"]) in policy["protected_roots"]
    config = run / "extract-config.json"
    protected = [Path(item["original"]) for item in prepared["files"].values()]
    with R.read_guards(protected):
        inputs = R.Inputs(config, R.digest(config), run)
        inputs.load_pins()
        assert len(inputs.key("lat_1A.npz", "MCgen")) == 64
    assert inputs.keys_read == [{"file": "lat_1A.npz", "key": "MCgen"}]
    with pytest.raises(custody.CustodyRefused, match="fresh prestage"):
        custody.prepare(R, fixture.config_path, fixture.config_sha, run)


def test_pf_common_binning_silent_and_firing(fixture: Fixture) -> None:
    spectra = json.loads(json.dumps(fixture.fixture_flux_spectra))
    assert R.common_flux_units(spectra)["identical_binning"] is True
    spectra["1M"]["generated_spectrum"]["edges"][2] += 0.5e-12
    assert R.common_flux_units(spectra)["identical_binning"] is True
    spectra["1M"]["generated_spectrum"]["edges"][2] += 1.5e-12
    with pytest.raises(R.Refused, match="P_F_BINNING") as caught:
        R.common_flux_units(spectra)
    assert caught.value.details["bin_edges"]["1M"]["g"] != spectra["1D"]["edges"]
    spectra["1M"]["generated_spectrum"]["edges"] = spectra["1D"]["edges"]
    spectra["1N"]["edges"] = spectra["1N"]["edges"][:-1]
    with pytest.raises(R.Refused, match="P_F_BINNING"):
        R.common_flux_units(spectra)


@pytest.mark.parametrize("field", ["title", "axis_titles", "file_units_metadata"])
def test_pf_common_units_silent_and_firing(fixture: Fixture, field: str) -> None:
    spectra = json.loads(json.dumps(fixture.fixture_flux_spectra))
    assert R.common_flux_units(spectra)["declared_units_byte_equal"] is True
    spectra["1M"][field] = (
        {"x": "different", "y": "units"}
        if field == "axis_titles"
        else (
            {"units": {"class_name": "TNamed", "text": "different"}}
            if field == "file_units_metadata"
            else "different title"
        )
    )
    with pytest.raises(R.Refused, match="P_F_UNITS") as caught:
        R.common_flux_units(spectra)
    assert (
        caught.value.details["shared_units_observed"]["1M"][field]
        == spectra["1M"][field]
    )
    assert (
        caught.value.details["shared_units_observed"]["1D"][field]
        == spectra["1D"][field]
    )


def test_environment_receipt_preserves_setup_and_redacts_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    custody = _custody_module()
    monkeypatch.setenv("OPENAI_API_KEY", "fixture-private-key")
    monkeypatch.setenv("SERVICE_ACCOUNT", "fixture-credential-json")
    monkeypatch.setenv("PROXY_URL", "https://name:password@proxy.invalid")
    monkeypatch.setenv("LD_LIBRARY_PATH", "/pinned/MAT/lib:/pinned/ROOT/lib")
    record = custody.environment_record()
    assert record["LD_LIBRARY_PATH"] == "/pinned/MAT/lib:/pinned/ROOT/lib"
    assert record["OPENAI_API_KEY"] == "<redacted credential field>"
    assert record["SERVICE_ACCOUNT"] == "<redacted credential field>"
    assert record["PROXY_URL"] == "https://<redacted>@proxy.invalid"


def test_flux_file_units_metadata_protocol(fixture: Fixture) -> None:
    read_keys = []

    class Key:
        def __init__(self, name: str, kind: str, text: str):
            self.name, self.kind, self.text = name, kind, text

        def GetName(self) -> str:
            return self.name

        def GetClassName(self) -> str:
            return self.kind

        def ReadObj(self) -> Any:
            read_keys.append(self.name)
            return SimpleNamespace(
                GetString=lambda: self.text, GetTitle=lambda: self.text
            )

    class File:
        def IsZombie(self) -> bool:
            return False

        def GetListOfKeys(self) -> list[Any]:
            return [
                Key("units", "TNamed", "shared units"),
                Key("POT", "TObjString", "shared exposure convention"),
                Key("flux_E_cvweighted", "PlotUtils::MnvH1D", "not metadata"),
                Key("units_hist", "TH1D", "not text"),
            ]

        def Close(self) -> None:
            pass

    root = SimpleNamespace(TFile=SimpleNamespace(Open=lambda *args: File()))
    path = fixture.root / "staged-units.root"
    result = R.flux_units_metadata(path, root=root)
    assert result == {
        "units": {"class_name": "TNamed", "text": "shared units"},
        "POT": {"class_name": "TObjString", "text": "shared exposure convention"},
    }
    assert read_keys == ["units", "POT"]


def test_trace_failure_writes_stop_without_pass(fixture: Fixture) -> None:
    custody = _custody_module()
    run = fixture.root / "failed-trace"
    run.mkdir()
    policy = run / "policy.json"
    policy.write_text(
        json.dumps(
            {
                "protected_roots": ["/original/data"],
                "allowed": {"run": [str(run)]},
                "cwd": str(run),
            }
        )
    )
    trace = run / "raw.strace"
    trace.write_text(
        'openat(AT_FDCWD, "/original/data/missing", O_RDONLY) = -1 ENOENT (No such file or directory)\n'
    )
    with pytest.raises(custody.CustodyRefused):
        custody.check_trace(R, run, trace, policy, R.digest(policy))
    stop = json.loads((run / "flux-custody.STOP.json").read_text())
    assert stop["status"] == "STOP" and stop["readings"] is None
    assert stop["violations"][0]["request"] == "/original/data/missing"
    assert not (run / "flux-custody.json").exists()

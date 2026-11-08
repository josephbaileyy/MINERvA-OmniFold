"""Local real-format fixtures and contract tests for RPD-RECO; no cluster inputs."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shlex
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
                        Path(R.__file__).with_name("fd_rpd_reco_custody.py")
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

            def SetDirectory(self, _directory: int) -> None:
                pass

            def GetTitle(self) -> str:
                return "protocol flux"

            def GetYaxis(self) -> Any:
                return SimpleNamespace(GetTitle=lambda: "protocol density")

            def GetNbinsX(self) -> int:
                return 2

            def GetXaxis(self) -> Any:
                return SimpleNamespace(
                    GetBinLowEdge=lambda i: float(i - 1), GetTitle=lambda: "energy"
                )

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
        self.TH1 = SimpleNamespace(
            AddDirectoryStatus=lambda: True, AddDirectory=lambda _value: None
        )
        self.SetOwnership = lambda _object, _owned: None


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
            "FD_RPD_CUSTODY_MODULE",
            Path(R.__file__).with_name("fd_rpd_reco_custody.py"),
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
        "class_exclusions": {"run": ["/run/extract/mat-data"]},
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
    inputs, _state, root, _lib = _prepared_mat_fixture(fixture, monkeypatch)
    prepared = inputs.prestage
    instrument = R.load_mat_instrument()
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


def test_legacy_prepare_presence_and_policy_guards(
    fixture: Fixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    inputs, _state, _root, _lib = _prepared_mat_fixture(fixture, monkeypatch)
    prepared = inputs.prestage
    assert R.checked_prepared_mat(inputs)
    inputs.prestage = None
    with pytest.raises(R.Refused) as caught:
        R.checked_mat_environment(inputs)
    assert caught.value.guard == "MAT_PREPARE"
    inputs.prestage = prepared
    (inputs.run / "trace-policy.json").write_text("{}")
    with pytest.raises(R.Refused) as caught:
        R.checked_prepared_mat(inputs)
    assert caught.value.guard == "MAT_PREPARE"


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
                    Path(R.__file__).with_name("fd_rpd_reco_custody.py")
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


def _prepare_fixture(
    fixture: Fixture, monkeypatch: pytest.MonkeyPatch
) -> tuple[Any, Path, dict[str, Path]]:
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
        MAT_SETUP={},
        MAT_FILES={str(library): R.digest(library)},
        mapped_files=lambda: {str(library)},
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
    monkeypatch.setattr(custody, "executable_mapped_files", lambda: {})
    fixture.config.update(
        {
            "configuration_status": "READY",
            "mat_dependencies": {"path": str(inventory), "sha256": R.digest(inventory)},
            "trace_environment_roots": ["/synthetic/env"],
            "trace_instrument_directories": [str(library.parent / "instrument")],
            "cov2d_protected_paths": ["/synthetic/cov2d-input"],
            "trace_platform_library_digest": "ordinary_instrument_code_only",
            "trace_platform_roots": [
                {
                    "role": role,
                    "path": str(fixture.root / "platform" / role),
                    "reason": "disposable platform policy fixture",
                }
                for role in sorted(custody.PLATFORM_ROLES)
            ],
        }
    )
    ovis = Path(
        next(
            item["path"]
            for item in fixture.config["trace_platform_roots"]
            if item["role"] == "ovis_ldms"
        )
    )
    for relative in custody.OVIS_EXIT_LIBRARIES:
        path = ovis / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"\x7fELF synthetic exit-hook code")
    fixture.save_config()
    run = fixture.root / "fresh-prepare"
    return custody, run, roots


def _add_prepare_platform_mapping(
    custody: Any, fixture: Fixture, monkeypatch: pytest.MonkeyPatch
) -> Path:
    library = Path(fixture.config["trace_platform_roots"][0]["path"]) / "instrument.so"
    library.parent.mkdir(parents=True)
    library.write_bytes(b"mapped platform prepare fixture")
    info = library.stat()
    instrument = R.load_mat_instrument()
    previous = instrument.mapped_files
    instrument.mapped_files = lambda: previous() | {str(library)}
    monkeypatch.setattr(
        custody,
        "executable_mapped_files",
        lambda: {str(library): {"device": info.st_dev, "inode": info.st_ino}},
    )
    return library


def test_fresh_prepare_stages_closed_inventory(
    fixture: Fixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TEST_API_KEY", "private-full-prepare-fixture")
    custody, run, roots = _prepare_fixture(fixture, monkeypatch)
    platform_library = _add_prepare_platform_mapping(custody, fixture, monkeypatch)
    prepared = custody.prepare(R, fixture.config_path, fixture.config_sha, run)
    assert {
        name: pin
        for name, pin in prepared["platform_libraries"].items()
        if name in prepared["platform_mapped"]
    } == {
        str(platform_library): {
            **custody.platform_identity(platform_library),
            "sha256": R.digest(platform_library),
        }
    }
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
    private = Path(prepared["private_prepare_path"])
    assert private.is_file() and not private.is_relative_to(run)
    assert inputs.prestage == prepared
    assert (run / "staged/prestage-reference.json").is_file()
    assert not (run / "staged/prestage.json").exists()
    fingerprint = hashlib.sha256(b"private-full-prepare-fixture").hexdigest().encode()
    assert fingerprint in private.read_bytes()
    assert all(
        fingerprint not in path.read_bytes()
        for path in run.rglob("*")
        if path.is_file()
    )
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

    root = SimpleNamespace(
        TFile=SimpleNamespace(Open=lambda *args: File()),
        TH1=SimpleNamespace(
            AddDirectoryStatus=lambda: True, AddDirectory=lambda value: None
        ),
    )
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


def _prepared_mat_fixture(
    fixture: Fixture, monkeypatch: pytest.MonkeyPatch
) -> tuple[Any, Any, Any, Path]:
    """Real instrument verifier plus real local stats; lazy dictionary/map protocol."""
    import time

    # The checked instrument is code-only; no environment/data checks are invoked here.
    instrument = R.load_mat_instrument()
    opt = fixture.root / "opt"
    lib = opt / "lib/libMAT.so"
    lib.parent.mkdir(parents=True)
    lib.write_bytes(b"original mapped code")
    setup = fixture.root / "setup.sh"
    setup.write_text("fixture setup")
    instrument.MAT_PREFIX = str(opt)
    instrument.MAT_LIB = str(lib.parent)
    instrument.MAT_SETUP = {str(setup): R.digest(setup)}
    instrument.MAT_FILES = {str(lib): R.digest(lib)}
    instrument.MAT_LINK = (str(lib.parent / "libMATDict.so"), str(lib))
    instrument.MAT_MAPPED = {str(lib)}
    monkeypatch.setenv("PLOTUTILSROOT", str(lib.parent))
    monkeypatch.setenv("MINERVA_PREFIX", str(opt))
    monkeypatch.setenv("FD_RPD_RECO_CONNECT_ID", "lazy-map-test")
    custody = R.load_custody_instrument()
    native_reader = custody.native_environment
    monkeypatch.setattr(custody, "native_environment", lambda: dict(os.environ))
    monkeypatch.setattr(R, "load_custody_instrument", lambda: custody)
    state = SimpleNamespace(
        loaded=False, calls=[], native_environment=native_reader, custody=custody
    )

    def get_class(name: str) -> Any:
        assert name == "PlotUtils::MnvH1D"
        state.calls.append("dictionary")
        state.loaded = True
        return SimpleNamespace(HasDictionary=lambda: True)

    def mapped_files() -> set[str]:
        state.calls.append("maps")
        return {str(lib)} if state.loaded else set()

    instrument.mapped_files = mapped_files
    monkeypatch.setattr(R, "load_mat_instrument", lambda: instrument)
    root = SimpleNamespace(TClass=SimpleNamespace(GetClass=get_class))
    monkeypatch.setitem(sys.modules, "ROOT", root)
    root_prefix = fixture.root / "root-runtime"
    root_prefix.mkdir()
    if "ROOTSYS" not in os.environ:
        monkeypatch.setenv("ROOTSYS", str(root_prefix))
    for key, value in {
        "CLING_STANDARD_PCH": "none",
        "CPPYY_API_PATH": "none",
        "CPPYY_NO_ROOT_FILTER": "1",
    }.items():
        monkeypatch.setenv(key, value)
    inputs = fixture.inputs()
    policy = inputs.run / "trace-policy.json"
    policy.write_text(
        json.dumps(
            {
                "allowed": {
                    "pinned_mat_libs": [str(lib)],
                    "platform_system": [],
                    "pinned_platform_libs": [],
                },
                "protected_roots": [],
                "instrument_directories": [str(lib.parent)],
            }
        )
    )
    staged_code = fixture.root / "staged-checked.py"
    staged_code.write_text("checked instrument")
    info = lib.stat()
    inputs.prestage = {
        "run": str(inputs.run),
        "connect_id": "lazy-map-test",
        "prepare_time_ns": time.time_ns(),
        "environment_after_setup": _custody_module().environment_record(),
        "environment_snapshot": _custody_module().environment_snapshot(),
        "trace_policy_sha256": R.digest(policy),
        "platform_libraries": {},
        "platform_mapped": {},
        "mapped_mat_stats": {str(lib): [info.st_dev, info.st_ino, info.st_size]},
        "instrument_files": [
            {"staged": str(staged_code), "sha256": R.digest(staged_code)}
        ],
        "mat_environment": {
            "setup_sha256": instrument.MAT_SETUP,
            "mat_sha256": instrument.MAT_FILES,
            "symlink": {instrument.MAT_LINK[0]: str(lib)},
        },
    }
    return inputs, state, root, lib


def test_lazy_dictionary_before_maps(
    fixture: Fixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    inputs, state, root, _lib = _prepared_mat_fixture(fixture, monkeypatch)
    assert R.checked_prepared_mat(inputs)[0] is root
    assert state.calls == ["dictionary", "maps"]
    state.calls.clear()
    assert R.checked_prepared_mat(inputs)[0] is root
    assert state.calls == ["dictionary", "maps"]


@pytest.mark.parametrize("defect", ["size", "inode", "staged_digest"])
def test_prepared_mapped_stats_and_staged_digest(
    fixture: Fixture, monkeypatch: pytest.MonkeyPatch, defect: str
) -> None:
    inputs, _state, _root, lib = _prepared_mat_fixture(fixture, monkeypatch)
    R.checked_prepared_mat(inputs)
    if defect == "size":
        lib.write_bytes(b"changed mapped library length")
    elif defect == "inode":
        replacement = lib.with_name("replacement.so")
        replacement.write_bytes(lib.read_bytes())
        replacement.replace(lib)
        assert lib.stat().st_ino != inputs.prestage["mapped_mat_stats"][str(lib)][1]
    else:
        Path(inputs.prestage["instrument_files"][0]["staged"]).write_text("changed")
    guard = "MAT_INSTRUMENT_DIGEST" if defect == "staged_digest" else "MAT_MAPPED_STAT"
    with pytest.raises(R.Refused, match=guard):
        R.checked_prepared_mat(inputs)


@pytest.mark.parametrize(
    "defect,guard",
    [
        ("inventory", "MAT_INVENTORY"),
        ("atime", "STAGE_SOURCE_STAT"),
        ("native", "NATIVE_SELECTION"),
        ("fence_call", "PREPARE_FENCE"),
        ("fence_status", "PREPARE_FENCE"),
    ],
)
def test_prepare_firing_guards(
    fixture: Fixture, monkeypatch: pytest.MonkeyPatch, defect: str, guard: str
) -> None:
    custody, run, roots = _prepare_fixture(fixture, monkeypatch)
    if defect == "inventory":
        original = Path(fixture.config["mat_dependencies"]["path"])
        record = json.loads(original.read_text())
        record["entries"] = record["entries"][:-1]
        wrong = fixture.root / "wrong-inventory.json"
        wrong.write_text(json.dumps(record))
        fixture.config["mat_dependencies"] = {
            "path": str(wrong),
            "sha256": R.digest(wrong),
        }
        fixture.save_config()
    elif defect == "atime":
        stat = custody.source_stat
        seen = {}

        def moving(path: Path) -> Any:
            info = stat(path)
            seen[str(path)] = seen.get(str(path), 0) + 1
            if seen[str(path)] > 1:
                info["atime_ns"] += 1
            return info

        monkeypatch.setattr(custody, "source_stat", moving)
    elif defect == "native":
        path = (
            roots["PLOTUTILSROOT"]
            / "data/flux/flux-gen2thin-pdg14-minervame1D_rearrangedUniverses.root"
        )
        path.write_bytes(b"different native source")
    elif defect == "fence_call":

        def refused() -> Any:
            raise custody.CustodyRefused("fence refused", {"guard": guard})

        monkeypatch.setattr(custody, "cov2d_fence", refused)
    else:
        monkeypatch.setattr(
            custody, "cov2d_fence", lambda: {"status": "STOP", "exit_code": 3}
        )
    with pytest.raises(custody.CustodyRefused) as caught:
        custody.prepare(R, fixture.config_path, fixture.config_sha, run)
    assert caught.value.details["guard"] == guard
    if defect.startswith("fence"):
        assert not (run / "original-inputs").exists()
        assert not (run / "mat-data").exists()


def test_run_overlaps_protected_guard(
    fixture: Fixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    custody, run, _roots = _prepare_fixture(fixture, monkeypatch)
    prepared = custody.prepare(R, fixture.config_path, fixture.config_sha, run)
    prepared["files"][str(run)] = {"original": str(run)}
    with pytest.raises(custody.CustodyRefused) as caught:
        custody.build_trace_policy(fixture.config, prepared, run)
    assert caught.value.details["guard"] == "RUN_PROTECTED_OVERLAP"


def test_trace_extract_identity_guard(fixture: Fixture) -> None:
    custody = _custody_module()
    run = fixture.root / "identity-trace"
    run.mkdir()
    policy = run / "policy.json"
    policy.write_text(
        json.dumps(
            {"cwd": str(run), "protected_roots": [], "allowed": {"system": ["/etc"]}}
        )
    )
    trace = run / "trace.txt"
    trace.write_text(
        'openat(AT_FDCWD, "/etc/ld.so.cache", O_RDONLY) = 3</etc/ld.so.cache>\n'
    )
    extract = run / "flux-extract.json"
    extract.write_text(
        json.dumps({"status": "PASS", "code_sha256": R.digest(Path(R.__file__))})
    )
    assert (
        custody.check_trace(R, run, trace, policy, R.digest(policy))["status"] == "PASS"
    )
    (run / "flux-custody.json").unlink()
    for wrong in (
        {"status": "STOP", "code_sha256": R.digest(Path(R.__file__))},
        {"status": "PASS", "code_sha256": "0" * 64},
    ):
        extract.write_text(json.dumps(wrong))
        with pytest.raises(custody.CustodyRefused) as caught:
            custody.check_trace(R, run, trace, policy, R.digest(policy))
        assert caught.value.details["guard"] == "TRACE_EXTRACT_IDENTITY"


def test_negative_expected_guard(
    fixture: Fixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    custody = _custody_module()
    run = fixture.run.resolve()
    run.mkdir()
    dependency = run / "constraint.txt"
    dependency.write_text("own staged input")
    custody.write_private_prepare(
        R,
        run,
        "prestage",
        {
            "run": str(run),
            "connect_id": "negative-check",
            "mat_dependencies": [
                {"environment_key": "MPARAMFILES", "staged": str(dependency)}
            ],
        },
        protected_roots=[],
    )

    policy = run / "trace-policy.json"
    policy.write_text(
        json.dumps(
            {
                "cwd": str(Path(custody.__file__).resolve().parents[1]),
                "clone_root": str(Path(custody.__file__).resolve().parents[1]),
            }
        )
    )

    def stopped(_command: Any, **kwargs: Any) -> Any:
        assert not dependency.exists()
        (run / "flux-extract.STOP.json").write_text(
            json.dumps({"guard": "OTHER_GUARD"})
        )
        return SimpleNamespace(returncode=4, stdout="", stderr="")

    monkeypatch.setattr(custody.subprocess, "run", stopped)
    with pytest.raises(custody.CustodyRefused) as caught:
        custody.missing_dependency_check(
            R, fixture.config_path, fixture.config_sha, run, R.digest(policy)
        )
    assert caught.value.details["guard"] == "NEGATIVE_EXPECTED_GUARD"
    assert dependency.read_text() == "own staged input"


def test_extract_selection_guard(
    fixture: Fixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    inputs = fixture.inputs()
    source = fixture.flux / "1D.root"
    inputs.prestage = {
        "mat_prefixes": {},
        "mat_dependencies": [
            {
                "staged": str(source),
                "sha256": R.digest(source),
                "playlist_group": "1D",
                "pdg": 14,
                "role": "constrained-numerator-input",
            }
        ],
    }
    monkeypatch.setattr(
        R, "checked_mat_environment", lambda _inputs=None: (_RootDouble(), {})
    )
    monkeypatch.setattr(
        R, "selected_flux_files", lambda _inputs: {"1D": {"sha256": "0" * 64}}
    )
    with pytest.raises(R.Refused, match="FLUX_CONSTRUCTOR_SELECTION"):
        R.flux_extract(inputs, [])


def test_instrument_directory_scan_and_mapping() -> None:
    custody = _custody_module()
    policy = {
        "cwd": "/code",
        "protected_roots": ["/mat/lib/data"],
        "instrument_directories": ["/mat/lib", "/mat/include"],
        "python_directories": ["/code", "/user/site"],
        "allowed": {
            "pinned_mat_libs": ["/mat/lib/libMAT.so", "/mat/lib/MATDict.rootmap"],
            "environment": ["/mat/lib", "/env"],
            "system": ["/etc"],
        },
    }
    lines = [
        'openat(AT_FDCWD, "/mat/lib", O_RDONLY|O_DIRECTORY) = 3</mat/lib>',
        'openat(AT_FDCWD, "/mat/lib/MATDict.rootmap", O_RDONLY) = 4</mat/lib/MATDict.rootmap>',
        'openat(AT_FDCWD, "/mat/lib/MAT-MINERvADict.rootmap", O_RDONLY) = 4</mat/lib/MAT-MINERvADict.rootmap>',
        'openat(AT_FDCWD, "/mat/lib/libMATDict.so", O_RDONLY) = 4</mat/lib/libMAT.so>',
        'openat(AT_FDCWD, "/code", O_RDONLY|O_DIRECTORY) = 5</code>',
        'openat(AT_FDCWD, "/mat/include/PlotUtils/MnvH1D.h", O_RDONLY) = 5</mat/include/PlotUtils/MnvH1D.h>',
    ]
    result = custody.classify_trace(lines, policy)
    assert result["successful_open_counts"] == {
        "instrument_directory": 3,
        "pinned_mat_libs": 2,
        "python_directory": 1,
    }
    assert custody.mapped_instrument_violations({"/mat/lib/libMAT.so"}, policy) == []
    assert custody.mapped_instrument_violations(
        {"/mat/lib/libMAT.so", "/mat/lib/libUnfoldUtils.so"}, policy
    ) == ["/mat/lib/libUnfoldUtils.so"]
    with pytest.raises(custody.CustodyRefused):
        custody.classify_trace(
            lines
            + ['openat(AT_FDCWD, "/mat/lib/data/fallback.root", O_RDONLY) = -1 ENOENT'],
            policy,
        )


def test_instrument_directories_required() -> None:
    custody = _custody_module()
    with pytest.raises(custody.CustodyRefused) as caught:
        custody.build_trace_policy(
            {"trace_environment_roots": ["/env"], "trace_instrument_directories": []},
            {},
            Path("/run"),
        )
    assert caught.value.details["guard"] == "INSTRUMENT_DIRECTORIES"


def test_nonpinned_mapped_library_refuses(
    fixture: Fixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    inputs, state, _root, library = _prepared_mat_fixture(fixture, monkeypatch)
    instrument = R.load_mat_instrument()
    foreign = fixture.root / "other-instrument/libUnpinned.so"
    foreign.parent.mkdir()
    foreign.write_bytes(b"unapproved library")
    policy = inputs.run / "trace-policy.json"
    value = json.loads(policy.read_text())
    value["instrument_directories"].append(str(foreign.parent))
    policy.write_text(json.dumps(value))
    inputs.prestage["trace_policy_sha256"] = R.digest(policy)
    instrument.mapped_files = lambda: (
        {str(library), str(foreign)} if state.loaded else set()
    )
    with pytest.raises(R.Refused, match="MAT_MAPPED_SET"):
        R.checked_prepared_mat(inputs)


def test_root_reader_releases_before_close(fixture: Fixture) -> None:
    import weakref

    events = []
    automatic = [True]

    class Histogram(FluxHistogramDouble):
        def SetDirectory(self, value: int) -> None:
            assert value == 0
            events.append("detach")

    references = []

    class File:
        def IsZombie(self) -> bool:
            return False

        def Get(self, name: str) -> Any:
            assert automatic[0] is False
            hist = Histogram([0, 1, 2], [2, 4])
            references.append(weakref.ref(hist))
            return hist

        def Close(self) -> None:
            assert automatic[0] is False
            assert references[0]() is None, "histogram proxy survived into Close"
            events.append("close")

    root = SimpleNamespace(
        TFile=SimpleNamespace(Open=lambda *args: File()),
        TH1=SimpleNamespace(
            AddDirectoryStatus=lambda: automatic[0],
            AddDirectory=lambda v: automatic.__setitem__(0, v),
        ),
        SetOwnership=lambda obj, value: events.append("own"),
    )
    result = R.read_flux_histogram(fixture.root / "staged.root", "CV", root=root)
    np.testing.assert_array_equal(result["values"], [2, 4])
    assert events == ["detach", "own", "close"]
    assert automatic == [True]


def test_real_mnv_worker_crash_cannot_publish_pass(
    fixture: Fixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    spec = importlib.util.spec_from_file_location(
        "real_mnv_supervisor",
        Path(
            os.environ.get(
                "FD_RPD_MAT_CHECK_MODULE",
                REPO / "nd-unfolding/tests/fd_rpd_reco_mat_check.py",
            )
        ),
    )
    assert spec is not None and spec.loader is not None
    check = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(check)
    check.r = R
    run = fixture.root / "segfault-protocol"
    monkeypatch.setattr(
        sys,
        "argv",
        ["check", "--probe", str(fixture.flux / "1D.root"), "--run", str(run)],
    )

    def crash(_command: Any, **kwargs: Any) -> Any:
        (run / "real-mnv-worker.json").write_text(
            json.dumps({"status": "PASS", "class_name": "PlotUtils::MnvH1D"})
        )
        return SimpleNamespace(
            returncode=-11, stdout="reader before close", stderr="segfault"
        )

    monkeypatch.setattr(check.subprocess, "run", crash)
    assert check.main() == 4
    assert not (run / "real-mnv-check.json").exists()


def test_prologue_prepare_opens_no_declared_data(
    fixture: Fixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TEST_API_KEY", "private-prologue-prepare-fixture")
    custody, _run, _roots = _prepare_fixture(fixture, monkeypatch)
    platform_library = _add_prepare_platform_mapping(custody, fixture, monkeypatch)
    spec = importlib.util.spec_from_file_location(
        "rpd_prologue_test",
        Path(
            os.environ.get(
                "FD_RPD_PROLOGUE_MODULE", REPO / "nd-unfolding/fd_rpd_reco_prologue.py"
            )
        ),
    )
    assert spec is not None and spec.loader is not None
    prologue = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "fd_rpd_reco", R)
    monkeypatch.setitem(sys.modules, "fd_rpd_reco_custody", custody)
    spec.loader.exec_module(prologue)
    prologue.r, prologue.custody = R, custody
    active = [True]
    protected = [
        fixture.dump.resolve(),
        fixture.flux.resolve(),
        fixture.source.resolve(),
    ]

    def forbid(event: str, args: Any) -> None:
        if (
            active[0]
            and event == "open"
            and isinstance(args[0], (str, bytes, os.PathLike))
        ):
            path = Path(os.fsdecode(args[0])).resolve()
            assert not any(
                path == root or root in path.parents for root in protected
            ), "prologue opened declared data"

    sys.addaudithook(forbid)
    run = fixture.root / "data-free-prepare"
    try:
        digest = prologue.prepare(fixture.config_path, fixture.config_sha, run)
    finally:
        active[0] = False
    assert digest == R.digest(run / "prologue-prepare-reference.json")
    prepared = custody.read_private_prepare(
        R, run / "prologue-prepare-reference.json", digest, run
    )
    assert {
        name: pin
        for name, pin in prepared["platform_libraries"].items()
        if name in prepared["platform_mapped"]
    } == {
        str(platform_library): {
            **custody.platform_identity(platform_library),
            "sha256": R.digest(platform_library),
        }
    }
    private = Path(prepared["private_prepare_path"])
    fingerprint = (
        hashlib.sha256(b"private-prologue-prepare-fixture").hexdigest().encode()
    )
    assert private.is_file() and not private.is_relative_to(run)
    assert fingerprint in private.read_bytes()
    assert all(
        fingerprint not in path.read_bytes()
        for path in run.rglob("*")
        if path.is_file()
    )
    assert not (run / "original-inputs").exists()
    assert not (run / "mat-data").exists()


def _diagnostic_prepare_context(
    monkeypatch: pytest.MonkeyPatch, environment: dict[str, str] | None = None
) -> tuple[Any, SimpleNamespace]:
    custody = _custody_module()
    monkeypatch.setattr(
        os,
        "environ",
        {
            "FD_RPD_RECO_CONNECT_ID": "observed-connect",
            "HOME": "/fixture/home",
            **(environment or {}),
        },
    )
    monkeypatch.setattr(R.time, "time_ns", lambda: 20_000_000_000_000)
    prepared = {
        "status": "PASS",
        "run": "/fixture/run",
        "connect_id": "observed-connect",
        "prepare_time_ns": 19_999_999_999_900,
        "environment_after_setup": custody.environment_record(),
        "environment_snapshot": custody.environment_snapshot(),
        "mat_environment": {},
        "mapped_mat_stats": {},
        "instrument_files": [],
        "original_mat_prefixes": {},
        "mat_prefixes": {},
        "files": {},
        "module_paths": {},
        "trace_policy_sha256": "0" * 64,
    }
    return custody, SimpleNamespace(run=Path("/fixture/run"), prestage=prepared)


@pytest.mark.parametrize(
    "case",
    ["missing", "legacy", "run", "connect_presence", "connect", "age", "environment"],
)
def test_prepare_receipt_named_guards(
    monkeypatch: pytest.MonkeyPatch, case: str
) -> None:
    custody, context = _diagnostic_prepare_context(monkeypatch)
    assert R.check_prepare_receipt(context, custody) is context.prestage
    required = [
        "connect_id",
        "environment_after_setup",
        "environment_snapshot",
        "prepare_time_ns",
        "run",
    ]
    fields = [
        "connect_id",
        "environment_after_setup",
        "environment_snapshot",
        "files",
        "instrument_files",
        "mapped_mat_stats",
        "mat_environment",
        "mat_prefixes",
        "module_paths",
        "original_mat_prefixes",
        "prepare_time_ns",
        "run",
        "status",
        "trace_policy_sha256",
    ]
    if case == "missing":
        context.prestage = None
        guard = "MAT_PREPARE_PRESENT"
        expected = {"presence": {"required": required, "observed": []}}
    elif case == "legacy":
        # Legacy prepare layout predating the environment snapshot field.
        del context.prestage["environment_snapshot"]
        guard = "MAT_PREPARE_PRESENT"
        expected = {
            "presence": {
                "required": required,
                "observed": [
                    field for field in fields if field != "environment_snapshot"
                ],
            }
        }
    else:
        diff = {"added": {}, "removed": {}, "changed": {}}
        prepared_run, prepared_connect = "/fixture/run", "observed-connect"
        observed_connect: str | None = "observed-connect"
        stamp, age = 19_999_999_999_900, 100
        if case == "run":
            context.prestage["run"] = prepared_run = "/fixture/foreign"
            guard = "MAT_PREPARE_RUN"
        elif case == "connect_presence":
            del os.environ["FD_RPD_RECO_CONNECT_ID"]
            observed_connect = None
            diff["removed"] = {"FD_RPD_RECO_CONNECT_ID": "observed-connect"}
            guard = "MAT_PREPARE_CONNECT_PRESENT"
        elif case == "connect":
            context.prestage["connect_id"] = prepared_connect = "prepared-connect"
            guard = "MAT_PREPARE_CONNECT"
        elif case == "age":
            context.prestage["prepare_time_ns"] = stamp = 12_799_999_999_999
            age = 7_200_000_000_001
            guard = "MAT_PREPARE_AGE"
        else:
            os.environ["HOME"] = "/fixture/new-home"
            diff["changed"] = {
                "HOME": {"prepared": "/fixture/home", "observed": "/fixture/new-home"}
            }
            guard = "MAT_PREPARE_ENVIRONMENT"
        expected = {
            "presence": {"required": required, "observed": fields},
            "run": {"prepared": prepared_run, "observed": "/fixture/run"},
            "connect_presence": {
                "required": True,
                "observed": observed_connect is not None,
            },
            "connect_id": {"prepared": prepared_connect, "observed": observed_connect},
            "age": {
                "prepare_time_ns": stamp,
                "now_ns": 20_000_000_000_000,
                "observed_age_ns": age,
                "exclusive_bounds_ns": [0, 7_200_000_000_000],
            },
            "environment": {
                "excluded": {
                    "_": "shell-maintained last-command value",
                    "NERSC_PYMON_UUID": "per-interpreter pymon UUID; inherited value is replaced",
                },
                "diff": diff,
                "record_display_diff": {},
            },
        }
    with pytest.raises(R.Refused) as caught:
        R.check_prepare_receipt(context, custody)
    assert caught.value.guard == guard
    assert caught.value.details == expected


@pytest.mark.parametrize("change", ["changed", "added", "removed", "credential"])
def test_prepare_environment_whole_comparison(
    monkeypatch: pytest.MonkeyPatch, change: str
) -> None:
    import time

    custody = _custody_module()
    monkeypatch.setattr(
        os,
        "environ",
        {
            "FD_RPD_RECO_CONNECT_ID": "env-test",
            "LD_LIBRARY_PATH": "/pinned/lib",
            "PLOTUTILSROOT": "/pinned/mat",
            "TEST_API_KEY": "first-private-value",
        },
    )
    prepared = {
        "run": "/fixture/run",
        "connect_id": "env-test",
        "prepare_time_ns": time.time_ns(),
        "environment_after_setup": custody.environment_record(),
        "environment_snapshot": custody.environment_snapshot(),
    }
    context = SimpleNamespace(run=Path("/fixture/run"), prestage=prepared)
    monkeypatch.setenv("_", "different-shell-command")
    assert R.check_prepare_receipt(context, custody) is prepared
    if change == "changed":
        monkeypatch.setenv("LD_LIBRARY_PATH", "/foreign/lib")
    elif change == "added":
        monkeypatch.setenv("LD_PRELOAD", "/foreign/libextra.so")
    elif change == "removed":
        monkeypatch.delenv("PLOTUTILSROOT")
    else:
        monkeypatch.setenv("TEST_API_KEY", "second-private-value")
    with pytest.raises(R.Refused) as caught:
        R.check_prepare_receipt(context, custody)
    assert caught.value.guard == "MAT_PREPARE_ENVIRONMENT"
    diff = caught.value.details["environment"]["diff"]
    expected = {"added": {}, "removed": {}, "changed": {}}
    if change == "changed":
        expected["changed"] = {
            "LD_LIBRARY_PATH": {"prepared": "/pinned/lib", "observed": "/foreign/lib"}
        }
    elif change == "added":
        expected["added"] = {"LD_PRELOAD": "/foreign/libextra.so"}
    elif change == "removed":
        expected["removed"] = {"PLOTUTILSROOT": "/pinned/mat"}
    else:
        expected["changed"] = {
            "TEST_API_KEY": {
                "prepared": "<redacted credential field>",
                "observed": "<redacted credential field>",
            }
        }
    assert diff == expected
    rendered = json.dumps(caught.value.details)
    assert "first-private-value" not in rendered
    assert "second-private-value" not in rendered


@pytest.mark.parametrize("key", ["HOME", "NERSC_TEST_UNLISTED", "UNLISTED_ENV_KEY"])
@pytest.mark.parametrize("operation", ["added", "removed", "changed"])
def test_prepare_environment_nonprotected_keys(
    monkeypatch: pytest.MonkeyPatch, key: str, operation: str
) -> None:
    custody, context = _diagnostic_prepare_context(monkeypatch)
    os.environ.pop(key, None)
    if operation != "added":
        os.environ[key] = "prepared-value"
    os.environ["_"] = "prepared-shell-command"
    context.prestage["environment_after_setup"] = custody.environment_record()
    context.prestage["environment_snapshot"] = custody.environment_snapshot()
    os.environ["_"] = "observed-shell-command"
    assert R.check_prepare_receipt(context, custody) is context.prestage
    if operation == "removed":
        del os.environ[key]
    else:
        os.environ[key] = "observed-value"
    expected = {"added": {}, "removed": {}, "changed": {}}
    if operation == "added":
        expected["added"] = {key: "observed-value"}
    elif operation == "removed":
        expected["removed"] = {key: "prepared-value"}
    else:
        expected["changed"] = {
            key: {"prepared": "prepared-value", "observed": "observed-value"}
        }
    with pytest.raises(R.Refused) as caught:
        R.check_prepare_receipt(context, custody)
    assert caught.value.guard == "MAT_PREPARE_ENVIRONMENT"
    assert caught.value.details["environment"]["diff"] == expected


@pytest.mark.parametrize(
    "key",
    [
        "LD_PRELOAD",
        "PYTHONPATH",
        "ROOT_INCLUDE_PATH",
        "CLING_TEST",
        "ROOTSYS",
        "CLING_PREBUILT_MODULE_PATH",
    ],
)
def test_environment_exclusions_reject_interpreter_keys(
    monkeypatch: pytest.MonkeyPatch, key: str
) -> None:
    custody = _custody_module()
    snapshot = custody.environment_snapshot()
    monkeypatch.setitem(custody.ENVIRONMENT_EXCLUSIONS, key, "forbidden")
    with pytest.raises(custody.CustodyRefused) as caught:
        custody.environment_diff(snapshot, snapshot)
    assert caught.value.details["guard"] == "ENVIRONMENT_EXCLUSIONS"


def test_environment_exclusions_are_reviewed() -> None:
    assert _custody_module().ENVIRONMENT_EXCLUSIONS == {
        "_": "shell-maintained last-command value",
        "NERSC_PYMON_UUID": "per-interpreter pymon UUID; inherited value is replaced",
    }


def test_prologue_worker_stop_records_values_and_cfs_guard(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    spec = importlib.util.spec_from_file_location(
        "rpd_prologue_stop_test",
        Path(
            os.environ.get(
                "FD_RPD_PROLOGUE_MODULE", REPO / "nd-unfolding/fd_rpd_reco_prologue.py"
            )
        ),
    )
    assert spec is not None and spec.loader is not None
    prologue = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "fd_rpd_reco", R)
    monkeypatch.setitem(sys.modules, "fd_rpd_reco_custody", _custody_module())
    spec.loader.exec_module(prologue)
    prologue.r = R
    receipt = prologue.custody.write_private_prepare(
        R,
        tmp_path,
        "prologue-prepare",
        {
            "run": str(tmp_path),
            "connect_id": "stop-record",
        },
        protected_roots=[],
    )
    error = R.Refused("MAT_PREPARE_RUN", "controlled mismatch")
    error.details = {"run": {"prepared": "/foreign", "observed": str(tmp_path)}}

    def refuse(_inputs: Any) -> Any:
        raise error

    monkeypatch.setattr(R, "checked_prepared_mat", refuse)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "prologue",
            "--worker",
            "--run",
            str(tmp_path),
            "--prepare-sha256",
            R.digest(receipt),
        ],
    )
    assert prologue.main() == 4
    stop = json.loads((tmp_path / "prologue-worker.STOP.json").read_text())
    assert stop["guard"] == error.guard
    assert stop["details"] == error.details

    def forbid_write(*_args: Any, **_kwargs: Any) -> None:
        pytest.fail("CFS-refused worker must not write a STOP receipt")

    monkeypatch.setattr(R, "write_json", forbid_write)
    monkeypatch.setattr(
        sys, "argv", ["prologue", "--worker", "--run", "/global/cfs/forbidden-run"]
    )
    assert prologue.main() == 4


def test_connect_mat_setup_disables_nounset() -> None:
    """Every live MAT connect suspends nounset during setup sourcing."""
    sources = 0
    for path in (REPO / "nd-unfolding").rglob("*_connect.sh"):
        nounset = False
        for line in path.read_text().splitlines():
            if not line.lstrip().startswith(("set ", "source ", ". ")):
                continue
            words = shlex.split(line, comments=True)
            if not words:
                continue
            if words[0] == "set":
                for option in words[1:]:
                    if option.startswith("-") and "u" in option:
                        nounset = True
                    elif option.startswith("+") and "u" in option:
                        nounset = False
            if (
                words[0] in {"source", "."}
                and len(words) > 1
                and Path(words[1]).name == "setup_salloc_env.sh"
            ):
                sources += 1
                assert not nounset, f"{path}: MAT setup sourced under nounset"
    assert sources == 2


@pytest.mark.parametrize(
    "wrapper", ["fd_rpd_reco_prologue_connect.sh", "fd_rpd_reco_flux_connect.sh"]
)
@pytest.mark.parametrize("setup_rc", [0, 7])
def test_connect_mat_activation_preserves_shell_options(
    tmp_path: Path, wrapper: str, setup_rc: int
) -> None:
    """Activation may use unset variables and return nonzero before postchecks."""
    setup = tmp_path / "setup_salloc_env.sh"
    setup.write_text(
        'printf "activation stderr: %s\\n" "$RPD_UNSET_ACTIVATION_TEST" >&2\n'
        f"return {setup_rc}\n"
    )
    script = (REPO / "nd-unfolding" / wrapper).read_text()
    start = script.index("set +u\n")
    stop = script.index("# The setup changes TMPDIR", start)
    block = script[start:stop]
    source = next(
        shlex.split(line)[1]
        for line in block.splitlines()
        if line.startswith("source ")
    )
    block = block.replace(source, shlex.quote(str(setup)))
    program = (
        "set -euo pipefail\nunset RPD_UNSET_ACTIVATION_TEST\n"
        + block
        + '[[ "$-" == *u* && "$-" == *e* ]]\n'
        + '[[ "$(set -o pipefail)" == *on ]]\n'
        + 'printf "postcondition reached: %s\\n" "$reco_setup_rc"\n'
        + "false\nprintf 'unreachable\\n'\n"
    )
    completed = subprocess.run(
        ["bash", "-c", program], capture_output=True, text=True, check=False
    )
    assert completed.returncode == 1
    assert completed.stdout == f"postcondition reached: {setup_rc}\n"
    assert "activation stderr:" in completed.stderr
    assert f"MAT setup exit status: {setup_rc}" in completed.stderr
    assert "unbound variable" not in completed.stderr


@pytest.mark.parametrize("mode", ["equal", "changed", "added", "removed"])
def test_private_prepare_public_outputs(
    fixture: Fixture,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    mode: str,
) -> None:
    """Exercise the actual worker and scan every committable output for leaks."""
    custody = _custody_module()
    # Mutation failures must never serialize host credential fingerprints.
    module_override = os.environ.get("FD_RPD_CUSTODY_MODULE")
    monkeypatch.setattr(os, "environ", {"PATH": os.defpath})
    if module_override:
        monkeypatch.setenv("FD_RPD_CUSTODY_MODULE", module_override)
    secret = "disposable-private-credential-value"
    replacement = "changed-disposable-credential-value"
    url = "https://user:disposable-password@example.invalid"
    changed = mode != "equal"
    monkeypatch.setenv("TEST_API_KEY", secret)
    if mode == "added":
        monkeypatch.delenv("TEST_API_KEY")
    monkeypatch.setenv("TEST_DATABASE_URL", url)
    inputs, _state, _root, _lib = _prepared_mat_fixture(fixture, monkeypatch)
    prepared = inputs.prestage
    reference = custody.write_private_prepare(
        R, inputs.run, "prologue-prepare", prepared, protected_roots=[]
    )
    private = Path(prepared["private_prepare_path"])
    assert not private.is_relative_to(inputs.run)
    assert private.stat().st_mode & 0o777 == 0o600
    assert private.parent.stat().st_mode & 0o777 == 0o700
    assert json.loads(reference.read_text())["private_prepare"]["sha256"] == R.digest(
        private
    )
    assert (
        custody.read_private_prepare(R, reference, R.digest(reference), inputs.run)
        == prepared
    )
    spec = importlib.util.spec_from_file_location(
        "privacy_prologue",
        Path(
            os.environ.get(
                "FD_RPD_PROLOGUE_MODULE", REPO / "nd-unfolding/fd_rpd_reco_prologue.py"
            )
        ),
    )
    assert spec is not None and spec.loader is not None
    prologue = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "fd_rpd_reco", R)
    monkeypatch.setitem(sys.modules, "fd_rpd_reco_custody", custody)
    spec.loader.exec_module(prologue)
    if mode == "removed":
        monkeypatch.delenv("TEST_API_KEY")
    elif changed:
        monkeypatch.setenv("TEST_API_KEY", replacement)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "prologue",
            "--worker",
            "--run",
            str(inputs.run),
            "--prepare-sha256",
            R.digest(reference),
        ],
    )
    assert prologue.main() == (4 if changed else 0)
    exported = custody.public_record(
        prepared, prepared["environment_snapshot"], custody.environment_snapshot()
    )
    output = capsys.readouterr()
    texts = [output.out, output.err, json.dumps(exported)]
    texts += [path.read_text() for path in inputs.run.rglob("*") if path.is_file()]
    for text in texts:
        assert '"fingerprints"' not in text
        for value in (secret, replacement, url, "disposable-password"):
            assert value not in text
            assert hashlib.sha256(value.encode()).hexdigest() not in text
    summary = {
        "prepared_present": mode != "added",
        "observed_present": mode != "removed",
        "state": "changed" if changed else "equal",
    }
    view = json.loads(
        (
            inputs.run
            / ("prologue-prepare.STOP.json" if changed else "prologue-prepare.json")
        ).read_text()
    )
    assert view["redacted_environment"]["TEST_API_KEY"] == summary
    if mode != "added":
        assert view["environment_snapshot"]["values"]["TEST_API_KEY"] == summary
        assert view["environment_after_setup"]["TEST_API_KEY"] == summary
    assert view["private_prepare_sha256"] == R.digest(private)
    if changed:
        stop = json.loads((inputs.run / "prologue-worker.STOP.json").read_text())
        assert stop["guard"] == "MAT_PREPARE_ENVIRONMENT"
        section = mode if mode in {"added", "removed"} else "changed"
        assert (
            stop["details"]["environment"]["diff"][section]["TEST_API_KEY"] == summary
        )
        assert (
            json.loads(output.err.splitlines()[-1])["environment"]["diff"][section][
                "TEST_API_KEY"
            ]
            == summary
        )
    else:
        worker = json.loads((inputs.run / "prologue-worker.json").read_text())
        assert (
            worker["environment"]["environment_after_setup"]["TEST_API_KEY"] == summary
        )


@pytest.mark.parametrize(
    "defect",
    ["sha", "raw_sha", "location", "permissions", "directory_permissions", "identity"],
)
def test_private_prepare_refuses(tmp_path: Path, defect: str) -> None:
    custody = _custody_module()
    run = tmp_path / "run"
    run.mkdir(mode=0o700)
    prepared = {"run": str(run), "connect_id": "private-fixture"}
    reference = custody.write_private_prepare(
        R, run, "prestage", prepared, protected_roots=[]
    )
    assert (
        custody.read_private_prepare(R, reference, R.digest(reference), run) == prepared
    )
    private = Path(prepared["private_prepare_path"])
    record = json.loads(reference.read_text())
    if defect == "raw_sha":
        private.write_text(private.read_text() + " ")
    elif defect == "location":
        leaked = run / "private.json"
        leaked.write_bytes(private.read_bytes())
        leaked.chmod(0o600)
        record["private_prepare"]["path"] = str(leaked)
    elif defect == "permissions":
        private.chmod(0o644)
    elif defect == "directory_permissions":
        private.parent.chmod(0o755)
    elif defect == "identity":
        record["run"] = str(tmp_path / "other")
    reference.write_text(json.dumps(record))
    with pytest.raises(custody.CustodyRefused) as caught:
        custody.read_private_prepare(
            R, reference, "0" * 64 if defect == "sha" else R.digest(reference), run
        )
    assert caught.value.details["guard"] == "PRIVATE_PREPARE"


def test_private_prepare_trace_exact_path() -> None:
    custody = _custody_module()
    private = "/private-metadata/run/prestage.json"
    policy = {
        "cwd": "/run",
        "protected_roots": ["/original"],
        "private_prepare_files": [private],
        "allowed": {},
    }
    line = lambda path: f'openat(AT_FDCWD, "{path}", O_RDONLY) = 3<{path}>'
    result = custody.classify_trace([line(private)], policy)
    assert result["status"] == "PASS"
    for path in (private + ".other", private + "/child", "/original/source.cxx"):
        with pytest.raises(custody.CustodyRefused):
            custody.classify_trace(
                [line(path)],
                {**policy, "private_prepare_files": [private, "/original/source.cxx"]},
            )


@pytest.mark.parametrize("defect", ["cfs", "protected", "permissions"])
def test_private_prepare_write_boundary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, defect: str
) -> None:
    custody = _custody_module()
    run = tmp_path / "run"
    run.mkdir()
    path = (
        Path("/global/cfs/private-record.json")
        if defect == "cfs"
        else tmp_path / "private" / "prestage.json"
    )
    monkeypatch.setattr(custody, "private_prepare_path", lambda *_args: path)
    if defect == "permissions":
        path.parent.mkdir(mode=0o755)
        path.parent.chmod(0o755)
    touched = []
    mkdir = Path.mkdir

    def tracked_mkdir(target: Path, *args: Any, **kwargs: Any) -> Any:
        touched.append(target)
        return mkdir(target, *args, **kwargs)

    monkeypatch.setattr(Path, "mkdir", tracked_mkdir)
    expected = R.Refused if defect == "cfs" else custody.CustodyRefused
    with pytest.raises(expected) as caught:
        custody.write_private_prepare(
            R,
            run,
            "prestage",
            {"run": str(run), "connect_id": "boundary"},
            protected_roots=[str(path.parent)] if defect == "protected" else [],
        )
    if defect == "cfs":
        assert caught.value.guard == "OUTPUT_LOCATION"
    else:
        assert caught.value.details["guard"] == "PRIVATE_PREPARE"
    assert not path.exists()
    assert not (run / "prestage-reference.json").exists()
    if defect != "permissions":
        assert touched == []


@pytest.mark.parametrize("protected", [None, "ROOTSYS", "CLING_PREBUILT_MODULE_PATH"])
def test_pymon_exclusion_keeps_root_guards(
    monkeypatch: pytest.MonkeyPatch, protected: str | None
) -> None:
    custody, context = _diagnostic_prepare_context(monkeypatch)
    monkeypatch.setenv("NERSC_PYMON_UUID", "parent-process-id")
    monkeypatch.setenv("ROOTSYS", "/prepared/root")
    context.prestage["environment_after_setup"] = custody.environment_record()
    context.prestage["environment_snapshot"] = custody.environment_snapshot()
    monkeypatch.setenv("NERSC_PYMON_UUID", "child-process-id")
    assert R.check_prepare_receipt(context, custody) is context.prestage
    if protected is not None:
        monkeypatch.setenv(protected, "/unexpected/root/lib:")
        with pytest.raises(R.Refused) as caught:
            R.check_prepare_receipt(context, custody)
        assert caught.value.guard == "MAT_PREPARE_ENVIRONMENT"
        diff = caught.value.details["environment"]["diff"]
        assert protected in (
            diff["changed"] if protected == "ROOTSYS" else diff["added"]
        )
        assert "NERSC_PYMON_UUID" not in diff["changed"]


@pytest.mark.parametrize("entry", ["custody", "prologue"])
def test_prepare_snapshot_before_root(
    fixture: Fixture, monkeypatch: pytest.MonkeyPatch, entry: str
) -> None:
    custody, run, _roots = _prepare_fixture(fixture, monkeypatch)
    monkeypatch.setenv("ROOTSYS", "/before/root")
    monkeypatch.delenv("CLING_PREBUILT_MODULE_PATH", raising=False)
    check = R.checked_mat_environment

    def importing_root() -> Any:
        result = check()
        os.environ["ROOTSYS"] = "/after/root"
        os.environ["CLING_PREBUILT_MODULE_PATH"] = "/after/root/lib:"
        return result

    monkeypatch.setattr(R, "checked_mat_environment", importing_root)
    if entry == "custody":
        prepared = custody.prepare(R, fixture.config_path, fixture.config_sha, run)
    else:
        spec = importlib.util.spec_from_file_location(
            "boundary_prologue",
            Path(
                os.environ.get(
                    "FD_RPD_PROLOGUE_MODULE",
                    REPO / "nd-unfolding/fd_rpd_reco_prologue.py",
                )
            ),
        )
        assert spec is not None and spec.loader is not None
        prologue = importlib.util.module_from_spec(spec)
        monkeypatch.setitem(sys.modules, "fd_rpd_reco", R)
        monkeypatch.setitem(sys.modules, "fd_rpd_reco_custody", custody)
        spec.loader.exec_module(prologue)
        checksum = prologue.prepare(fixture.config_path, fixture.config_sha, run)
        prepared = custody.read_private_prepare(
            R, run / "prologue-prepare-reference.json", checksum, run
        )
    assert prepared["environment_snapshot"]["values"]["ROOTSYS"] == "/before/root"
    assert (
        "CLING_PREBUILT_MODULE_PATH" not in prepared["environment_snapshot"]["values"]
    )
    assert (
        prepared["environment_after_setup"]
        == prepared["environment_snapshot"]["values"]
    )


@pytest.mark.parametrize(
    "perturb", [None, "ROOTSYS", "CLING_PREBUILT_MODULE_PATH", "HOME"]
)
def test_worker_snapshot_before_root_and_runtime_recheck(
    fixture: Fixture, monkeypatch: pytest.MonkeyPatch, perturb: str | None
) -> None:
    import builtins

    module_override = os.environ.get("FD_RPD_CUSTODY_MODULE")
    real_root = fixture.root / "real-root"
    real_root.mkdir()
    alias_root = fixture.root / "root-alias"
    alias_root.symlink_to(real_root, target_is_directory=True)
    monkeypatch.setattr(os, "environ", {"PATH": os.defpath, "ROOTSYS": str(alias_root)})
    if module_override:
        monkeypatch.setenv("FD_RPD_CUSTODY_MODULE", module_override)
    inputs, _state, root, _lib = _prepared_mat_fixture(fixture, monkeypatch)
    importer = builtins.__import__
    imports = []

    def mutating_import(name: str, *args: Any, **kwargs: Any) -> Any:
        if name == "ROOT":
            imports.append(name)
            os.environ["ROOTSYS"] = str(real_root)
            os.environ["CLING_PREBUILT_MODULE_PATH"] = str(real_root / "lib") + ":"
            return root
        return importer(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", mutating_import)
    environment = R.checked_prepared_mat(inputs)[1]
    assert imports == ["ROOT"]
    assert environment["environment_after_setup"]["ROOTSYS"] == str(alias_root)
    assert "CLING_PREBUILT_MODULE_PATH" not in environment["environment_after_setup"]
    if perturb is None:
        assert R.checked_prepared_mat(inputs)[0] is root
    else:
        monkeypatch.setenv(perturb, "/unexpected")
        with pytest.raises(R.Refused) as caught:
            R.checked_prepared_mat(inputs)
        assert caught.value.guard == "MAT_RUNTIME_ENVIRONMENT"
        section = "added" if perturb == "HOME" else "changed"
        assert caught.value.details["environment"]["diff"][section][perturb] == (
            "/unexpected"
            if section == "added"
            else {
                "prepared": (
                    str(real_root)
                    if perturb == "ROOTSYS"
                    else str(real_root / "lib") + ":"
                ),
                "observed": "/unexpected",
            }
        )
        assert imports == ["ROOT"]


def test_prologue_child_environment_boundary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Native putenv must not change which environment the child is promised."""
    custody = _custody_module()
    path = Path(
        os.environ.get(
            "FD_RPD_PROLOGUE_MODULE", REPO / "nd-unfolding/fd_rpd_reco_prologue.py"
        )
    )
    spec = importlib.util.spec_from_file_location("launch_boundary_prologue", path)
    assert spec is not None and spec.loader is not None
    prologue = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "fd_rpd_reco", R)
    monkeypatch.setitem(sys.modules, "fd_rpd_reco_custody", custody)
    spec.loader.exec_module(prologue)
    key = "RPD_NATIVE_ENV_BOUNDARY_TEST"
    monkeypatch.setenv(key, "before-native-setter")
    baseline = dict(os.environ)
    run = tmp_path / "run"

    def prepare(_config: Any, _sha: Any, target: Path) -> str:
        assert target == run
        target.mkdir()
        (target / "trace-policy.json").write_text(
            json.dumps(
                {
                    "cwd": str(Path(custody.__file__).resolve().parents[1]),
                    "clone_root": str(Path(custody.__file__).resolve().parents[1]),
                }
            )
        )
        (target / "prologue-worker.json").write_text(
            json.dumps({"status": "PASS", "data_keys_read": []})
        )
        os.putenv(key, "after-native-setter")
        assert os.environ[key] == "before-native-setter"
        return "a" * 64

    subprocess_run = subprocess.run

    def child(_command: Any, **kwargs: Any) -> Any:
        assert kwargs.get("env") == baseline
        assert kwargs.get("cwd") == str(Path(custody.__file__).resolve().parents[1])
        process = subprocess_run(
            [
                sys.executable,
                "-c",
                'import os; print(os.environ["RPD_NATIVE_ENV_BOUNDARY_TEST"])',
            ],
            **kwargs,
        )
        assert process.stdout.strip() == "before-native-setter"
        (run / "prologue.strace").write_text("")
        return process

    monkeypatch.setattr(prologue, "prepare", prepare)
    monkeypatch.setattr(prologue.subprocess, "run", child)
    monkeypatch.setattr(
        custody,
        "classify_trace",
        lambda *_args: {"status": "PASS", "events": [], "violations": []},
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "prologue",
            "--config",
            str(tmp_path / "config.json"),
            "--config-sha256",
            "b" * 64,
            "--run",
            str(run),
        ],
    )
    try:
        assert prologue.main() == 0
        assert (
            json.loads((run / "data-free-trace.json").read_text())["status"] == "PASS"
        )
    finally:
        # Restore native state too; Python's mapping never saw the native setter.
        os.putenv(key, baseline[key])


@pytest.mark.parametrize(
    "key",
    [
        "RPD_NATIVE_RUNTIME_TEST",
        "NERSC_PYMON_UUID",
        "ROOTSYS",
        "CLING_PREBUILT_MODULE_PATH",
    ],
)
def test_native_runtime_changes_refuse(
    fixture: Fixture, monkeypatch: pytest.MonkeyPatch, key: str
) -> None:
    import ctypes

    inputs, state, _root, _lib = _prepared_mat_fixture(fixture, monkeypatch)
    monkeypatch.setattr(state.custody, "native_environment", state.native_environment)
    R.checked_prepared_mat(inputs)
    native_before = state.native_environment()
    python_before = os.environ.get(key)
    library = ctypes.CDLL(None)
    library.setenv.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
    library.setenv.restype = ctypes.c_int
    assert library.setenv(key.encode(), b"native-only-change", 1) == 0
    try:
        assert os.environ.get(key) == python_before
        with pytest.raises(R.Refused) as caught:
            R.checked_prepared_mat(inputs)
        assert caught.value.guard == "MAT_RUNTIME_ENVIRONMENT"
        assert caught.value.details["environment"]["excluded"] == {}
        section = "changed" if key in native_before else "added"
        item = caught.value.details["environment"]["diff"][section][key]
        assert item == (
            {"prepared": native_before[key], "observed": "native-only-change"}
            if section == "changed"
            else "native-only-change"
        )
    finally:
        if key in native_before:
            os.putenv(key, native_before[key])
        else:
            os.unsetenv(key)


@pytest.mark.parametrize(
    "third_key", [None, "RPD_UNEXPECTED_IMPORT_KEY", "NERSC_PYMON_UUID"]
)
def test_import_diff_is_bounded(
    fixture: Fixture, monkeypatch: pytest.MonkeyPatch, third_key: str | None
) -> None:
    import builtins

    override = os.environ.get("FD_RPD_CUSTODY_MODULE")
    real_root = fixture.root / "real-root"
    real_root.mkdir()
    alias_root = fixture.root / "root-alias"
    alias_root.symlink_to(real_root, target_is_directory=True)
    monkeypatch.setattr(os, "environ", {"PATH": os.defpath, "ROOTSYS": str(alias_root)})
    if override:
        monkeypatch.setenv("FD_RPD_CUSTODY_MODULE", override)
    inputs, _state, root, _lib = _prepared_mat_fixture(fixture, monkeypatch)
    importer = builtins.__import__

    def initialize(name: str, *args: Any, **kwargs: Any) -> Any:
        if name == "ROOT":
            os.environ["ROOTSYS"] = str(real_root)
            os.environ["CLING_PREBUILT_MODULE_PATH"] = str(real_root / "lib") + ":"
            if third_key:
                os.environ[third_key] = "unreviewed-import-value"
            return root
        return importer(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", initialize)
    diff = {
        "added": {"CLING_PREBUILT_MODULE_PATH": str(real_root / "lib") + ":"},
        "removed": {},
        "changed": {
            "ROOTSYS": {"prepared": str(alias_root), "observed": str(real_root)}
        },
    }
    if third_key:
        with pytest.raises(R.Refused) as caught:
            R.checked_prepared_mat(inputs)
        assert caught.value.guard == "MAT_IMPORT_ENVIRONMENT"
        diff["added"][third_key] = "unreviewed-import-value"
        assert caught.value.details["environment"]["diff"] == diff
        assert caught.value.details["environment"]["unexpected"] == {
            "added": {third_key: "unreviewed-import-value"},
            "removed": {},
            "changed": {},
        }
    else:
        record = R.checked_prepared_mat(inputs)[1]
        assert record["root_import_environment_diff"] == diff
        assert record["root_import_allowed_keys"] == [
            "CLING_PREBUILT_MODULE_PATH",
            "CLING_STANDARD_PCH",
            "CPPYY_API_PATH",
            "CPPYY_NO_ROOT_FILTER",
            "ROOTSYS",
        ]
        assert record["runtime_environment_exclusions"] == {}


@pytest.mark.parametrize(
    "defect",
    [
        "CLING_STANDARD_PCH",
        "CPPYY_API_PATH",
        "CPPYY_NO_ROOT_FILTER",
        "ROOTSYS",
        "unset_valid",
        "unset_missing",
    ],
)
def test_import_values_are_pinned(
    fixture: Fixture, monkeypatch: pytest.MonkeyPatch, defect: str
) -> None:
    import builtins

    inputs, _state, root, _lib = _prepared_mat_fixture(fixture, monkeypatch)
    custody = R.load_custody_instrument()
    if defect.startswith("unset_"):
        monkeypatch.delenv("ROOTSYS", raising=False)
        inputs.prestage["environment_snapshot"] = custody.environment_snapshot()
        inputs.prestage["environment_after_setup"] = custody.environment_record()
    importer = builtins.__import__

    def initialize(name: str, *args: Any, **kwargs: Any) -> Any:
        if name == "ROOT":
            if defect == "unset_valid":
                os.environ["ROOTSYS"] = str(fixture.root)
            else:
                os.environ["ROOTSYS" if defect == "unset_missing" else defect] = (
                    "/unexpected-import-value"
                )
            return root
        return importer(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", initialize)
    if defect == "unset_valid":
        record = R.checked_prepared_mat(inputs)[1]
        assert record["root_import_validation"]["rootsys"] == {
            "prepared_present": False,
            "prepared": None,
            "observed": str(fixture.root),
            "expected_realpath": None,
            "valid": True,
        }
    else:
        with pytest.raises(R.Refused) as caught:
            R.checked_prepared_mat(inputs)
        assert caught.value.guard == "MAT_IMPORT_ENVIRONMENT"
        validation = caught.value.details["environment"]
        if defect in {"ROOTSYS", "unset_missing"}:
            assert validation["rootsys"]["valid"] is False
        else:
            assert validation["invalid_pinned_values"][defect] == {
                "expected": {
                    "CLING_STANDARD_PCH": "none",
                    "CPPYY_API_PATH": "none",
                    "CPPYY_NO_ROOT_FILTER": "1",
                }[defect],
                "observed": "/unexpected-import-value",
            }


def test_import_prebuilt_removal_refuses(
    fixture: Fixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    import builtins

    inputs, _state, root, _lib = _prepared_mat_fixture(fixture, monkeypatch)
    custody = R.load_custody_instrument()
    monkeypatch.setenv("CLING_PREBUILT_MODULE_PATH", "/prepared/lib:")
    inputs.prestage["environment_snapshot"] = custody.environment_snapshot()
    inputs.prestage["environment_after_setup"] = custody.environment_record()
    importer = builtins.__import__

    def removing(name: str, *args: Any, **kwargs: Any) -> Any:
        if name == "ROOT":
            os.environ.pop("CLING_PREBUILT_MODULE_PATH")
            return root
        return importer(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", removing)
    with pytest.raises(R.Refused) as caught:
        R.checked_prepared_mat(inputs)
    assert caught.value.guard == "MAT_IMPORT_ENVIRONMENT"
    assert caught.value.details["environment"]["unexpected"]["removed"] == {
        "CLING_PREBUILT_MODULE_PATH": "/prepared/lib:"
    }


def test_public_module_names_are_not_artifacts() -> None:
    custody = _custody_module()
    spec = importlib.util.spec_from_file_location(
        "receipt_artifacts_for_module_names",
        REPO / "docs/orchestration/verify_receipt_artifacts.py",
    )
    assert spec is not None and spec.loader is not None
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    modules = {
        "nersc_pymon.log": "/instrument/nersc_pymon/log.py",
        "package.root": "/environment/package/root.py",
        "plain_module": "/environment/plain_module.py",
    }
    exported = custody.public_record({"module_paths": modules}, {}, {})
    rebuilt = {
        ".".join(item["module_name_components"]): item["source_path"]
        for item in exported["module_paths"]
    }
    assert rebuilt == modules
    assert not checker.bare_citations(json.dumps(exported))
    assert checker.bare_citations(json.dumps({"module_paths": modules})) == {
        "nersc_pymon.log",
        "package.root",
    }


@pytest.mark.parametrize(
    "key", ["CLING_STANDARD_PCH", "CPPYY_API_PATH", "CPPYY_NO_ROOT_FILTER"]
)
@pytest.mark.parametrize(
    "case", ["added_wrong", "never_set", "unchanged_wrong", "added_correct"]
)
def test_import_pin_added_missing_and_unchanged(
    fixture: Fixture, monkeypatch: pytest.MonkeyPatch, key: str, case: str
) -> None:
    """Exercise pin validation when startup adds a key or leaves it untouched."""
    import builtins

    expected_values = {
        "CLING_STANDARD_PCH": "none",
        "CPPYY_API_PATH": "none",
        "CPPYY_NO_ROOT_FILTER": "1",
    }
    inputs, _state, root, _lib = _prepared_mat_fixture(fixture, monkeypatch)
    custody = R.load_custody_instrument()
    for name in expected_values:
        monkeypatch.delenv(name, raising=False)
    if case == "unchanged_wrong":
        monkeypatch.setenv(key, "/wrong-pre-import-value")
    prepared_snapshot = custody.environment_snapshot(native=True)
    inputs.prestage["environment_snapshot"] = prepared_snapshot
    inputs.prestage["environment_after_setup"] = prepared_snapshot["values"]
    importer = builtins.__import__

    def initialize(name: str, *args: Any, **kwargs: Any) -> Any:
        if name == "ROOT":
            for pin, value in expected_values.items():
                if pin == key and case in {"never_set", "unchanged_wrong"}:
                    continue
                os.environ[pin] = (
                    "/wrong-added-value"
                    if pin == key and case == "added_wrong"
                    else value
                )
            return root
        return importer(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", initialize)
    added = dict(expected_values)
    if case in {"never_set", "unchanged_wrong"}:
        del added[key]
    elif case == "added_wrong":
        added[key] = "/wrong-added-value"
    expected_diff = {"added": added, "removed": {}, "changed": {}}
    if case == "added_correct":
        record = R.checked_prepared_mat(inputs)[1]
        validation = record["root_import_validation"]
        assert validation["pass"] is True
        assert validation["invalid_pinned_values"] == {}
        assert (
            record["native_environment_after_mat"] | expected_values
            == record["native_environment_after_mat"]
        )
    else:
        with pytest.raises(R.Refused) as caught:
            R.checked_prepared_mat(inputs)
        assert caught.value.guard == "MAT_IMPORT_ENVIRONMENT"
        validation = caught.value.details["environment"]
        observed = (
            None
            if case == "never_set"
            else (
                "/wrong-pre-import-value"
                if case == "unchanged_wrong"
                else "/wrong-added-value"
            )
        )
        assert validation["invalid_pinned_values"] == {
            key: {"expected": expected_values[key], "observed": observed}
        }
        assert validation["pass"] is False
    assert validation["diff"] == expected_diff
    assert validation["unexpected"] == {"added": {}, "removed": {}, "changed": {}}


def _trace_fixture(name: str) -> list[str]:
    directory = REPO / "nd-unfolding/tests/fixtures/fd_rpd_reco_trace/prologue4"
    return (directory / f"{name}.strace.txt").read_text().splitlines()


def _round3_trace_policy() -> dict[str, Any]:
    clone = "/dev/shm/limres-rpd-prologue4-20261108/repo"
    return {
        "cwd": clone,
        "clone_root": clone,
        "protected_roots": [],
        "allowed": {"system": ["/etc"]},
    }


def test_real_trace_fixture_provenance() -> None:
    directory = REPO / "nd-unfolding/tests/fixtures/fd_rpd_reco_trace/prologue4"
    manifest = json.loads((directory / "manifest.json").read_text())
    source = subprocess.run(
        ["git", "show", manifest["source_commit"] + ":" + manifest["source_file"]],
        cwd=REPO,
        capture_output=True,
        check=True,
    ).stdout
    assert len(source) == manifest["source_bytes"]
    assert hashlib.sha256(source).hexdigest() == manifest["source_sha256"]
    lines = source.decode().splitlines()
    for item in manifest["fixtures"].values():
        actual = (directory / item["file"]).read_bytes()
        assert (
            actual
            == ("\n".join(lines[n - 1] for n in item["source_lines"]) + "\n").encode()
        )
        assert hashlib.sha256(actual).hexdigest() == item["sha256"]


def test_trace_interleaving_keeps_pid_and_every_line() -> None:
    custody = _custody_module()
    lines = _trace_fixture("interleaved_failures")
    calls, violations, retained = custody.complete_trace_calls(lines)
    assert violations == retained == []
    assert [call["pid"] for call in calls] == [1600512, 1600533, 1600532]
    assert [call["line_numbers"] for call in calls] == [[1], [2, 4], [3, 5]]
    assert [call["raw_lines"] for call in calls] == [
        [lines[0]],
        [lines[1], lines[3]],
        [lines[2], lines[4]],
    ]
    checked = custody.classify_trace(lines, _round3_trace_policy())
    assert checked["status"] == "PASS"
    assert checked["trace_line_count"] == len(lines)
    assert [event["success"] for event in checked["events"]] == [True, False, False]
    success = custody.classify_trace(
        _trace_fixture("split_success"), _round3_trace_policy()
    )
    assert success["successful_open_counts"] == {"system": 2}
    assert success["events"][1]["pid"] == 1600533
    assert success["events"][1]["line_numbers"] == [2, 3]


@pytest.mark.parametrize(
    "defect", ["unfinished", "orphan", "wrong_pid", "wrong_name", "duplicate"]
)
def test_trace_unpaired_calls_refuse(defect: str) -> None:
    custody = _custody_module()
    lines = _trace_fixture("split_success")
    if defect == "unfinished":
        lines = lines[:2]
    elif defect == "orphan":
        lines = [lines[0], lines[2]]
    elif defect == "wrong_pid":
        lines[2] = lines[2].replace("1600533", "1600532")
    elif defect == "wrong_name":
        lines[2] = lines[2].replace("openat resumed", "open resumed")
    else:
        lines.insert(2, lines[1])
    with pytest.raises(custody.CustodyRefused) as caught:
        custody.classify_trace(lines, _round3_trace_policy())
    details = caught.value.details
    assert details["status"] == "STOP"
    assert any(item["class"] == "parse" for item in details["violations"])
    retained = [
        *details["events"],
        *details["violations"],
        *details["retained_noncall_lines"],
    ]
    assert {n for item in retained for n in item["line_numbers"]} == set(
        range(1, len(lines) + 1)
    )
    for item in details["violations"]:
        assert {"class", "path", "pid", "raw_line", "raw_lines"} <= item.keys()


def test_trace_exact_clone_chdir_and_other_refusal() -> None:
    custody = _custody_module()
    lines = _trace_fixture("exact_clone_chdir")
    result = custody.classify_trace(lines, _round3_trace_policy())
    assert [event["category"] for event in result["events"]] == [
        "system",
        "declared_clone_cwd",
        "declared_clone_cwd",
    ]
    for changed in (
        lines[:1] + [lines[1].replace('/repo"', '/elsewhere"')],
        lines[:1] + ["1600512 fchdir(9) = 0"],
    ):
        with pytest.raises(custody.CustodyRefused) as caught:
            custody.classify_trace(changed, _round3_trace_policy())
        assert caught.value.details["violations"][0]["class"] == "cwd"
        assert caught.value.details["violations"][0]["pid"] == 1600512


def _platform_fixture(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[Any, Path, dict[str, Any], dict[str, Any]]:
    custody = _custody_module()
    library = tmp_path / "platform/libinstrument.so"
    library.parent.mkdir(parents=True)
    library.write_bytes(b"mapped platform instrument")
    identity = custody.platform_identity(library)
    mappings = {str(library): {key: identity[key] for key in ("device", "inode")}}
    monkeypatch.setattr(custody, "executable_mapped_files", lambda: mappings)
    policy = {
        "allowed": {"platform_system": [str(library.parent)]},
        "protected_roots": [],
    }
    return custody, library, mappings, policy


def test_platform_config_closed_roles_and_reasons(
    fixture: Fixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    custody, _run, _roots = _prepare_fixture(fixture, monkeypatch)
    config = fixture.config
    assert len(custody.platform_settings(config)) == 8
    for change in ("missing", "duplicate", "reason", "relative", "glob", "digest"):
        wrong = json.loads(json.dumps(config))
        if change == "missing":
            wrong["trace_platform_roots"].pop()
        elif change == "duplicate":
            wrong["trace_platform_roots"][0] = wrong["trace_platform_roots"][1]
        elif change == "reason":
            wrong["trace_platform_roots"][0]["reason"] = ""
        elif change in {"relative", "glob"}:
            wrong["trace_platform_roots"][0]["path"] = (
                "relative" if change == "relative" else "/opt/*"
            )
        else:
            wrong["trace_platform_library_digest"] = "ordinary_all_inputs"
        with pytest.raises(custody.CustodyRefused) as caught:
            custody.platform_settings(wrong)
        assert caught.value.details["guard"] == "PLATFORM_CONFIG"


def test_platform_executable_maps_identity() -> None:
    custody = _custody_module()
    lines = [
        "1000-2000 r-xp 0000 08:01 42 /opt/platform/suffixless",
        "2000-3000 r--p 0000 08:01 99 /var/lib/sss/mc/passwd",
        "3000-4000 r--p 0000 08:01 43 /opt/platform/cache.pcm",
        "4000-5000 rwxp 0000 00:00 0 [anonymous]",
    ]
    assert custody.parse_executable_maps(lines) == {
        "/opt/platform/suffixless": {"device": os.makedev(8, 1), "inode": 42}
    }
    with pytest.raises(custody.CustodyRefused) as caught:
        custody.parse_executable_maps(lines + [lines[0].replace(" 42 ", " 44 ")])
    assert caught.value.details["guard"] == "PLATFORM_MAP_IDENTITY"


@pytest.mark.parametrize("defect", ["none", "set", "protected", "inode", "unstable"])
def test_platform_prepare_pins_and_protected_first(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, defect: str
) -> None:
    custody, library, mappings, policy = _platform_fixture(tmp_path, monkeypatch)
    calls = []

    def digest(path: Path) -> str:
        calls.append(str(path))
        checksum = R.digest(path)
        if defect == "unstable":
            path.write_bytes(b"changed while hashing")
        return checksum

    reader = SimpleNamespace(digest=digest)
    mapped = {str(library)}
    if defect == "set":
        mapped = set()
    elif defect == "protected":
        policy["protected_roots"] = [str(library.parent)]
    elif defect == "inode":
        mappings[str(library)]["inode"] += 1
    if defect == "none":
        pins = custody.pin_platform_libraries(reader, mapped, policy)
        assert pins == {
            str(library): {
                **custody.platform_identity(library),
                "sha256": R.digest(library),
            }
        }
        assert calls == [str(library)]
    else:
        guard = {
            "set": "PLATFORM_MAP_SET",
            "protected": "PLATFORM_PROTECTED",
            "inode": "PLATFORM_MAP_FILE",
            "unstable": "PLATFORM_PIN_CHANGED",
        }[defect]
        with pytest.raises(custody.CustodyRefused) as caught:
            custody.pin_platform_libraries(reader, mapped, policy)
        assert caught.value.details["guard"] == guard
        assert calls == ([str(library)] if defect == "unstable" else [])


@pytest.mark.parametrize(
    "defect",
    [
        "none",
        "added",
        "removed",
        "sha256",
        "inode",
        "bytes",
        "mtime_ns",
        "mapping",
        "protected",
        "absent_pins",
    ],
)
def test_platform_worker_exact_pins(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, defect: str
) -> None:
    custody, library, mappings, policy = _platform_fixture(tmp_path, monkeypatch)
    mapped = {str(library)}
    pins = custody.pin_platform_libraries(R, mapped, policy)
    prepared = {
        "platform_libraries": pins,
        "platform_mapped": json.loads(json.dumps(mappings)),
    }
    if defect == "added":
        pins.clear()
    elif defect == "removed":
        mappings.clear()
        mapped.clear()
    elif defect in {"sha256", "inode", "bytes", "mtime_ns"}:
        pins[str(library)][defect] = "0" * 64 if defect == "sha256" else -1
    elif defect == "mapping":
        mappings[str(library)]["inode"] += 1
    elif defect == "protected":
        policy["protected_roots"] = [str(library)]
    elif defect == "absent_pins":
        prepared = {}
    calls = []

    def digest(path: Path) -> str:
        calls.append(path)
        return R.digest(path)

    record = custody.platform_library_record(
        SimpleNamespace(digest=digest), prepared, mapped, policy
    )
    assert record["status"] == ("PASS" if defect == "none" else "STOP")
    if defect in {"added", "removed", "protected", "absent_pins"}:
        assert calls == []
    if defect in {"sha256", "inode", "bytes", "mtime_ns", "mapping"}:
        assert record["libraries"][str(library)]["prepared"] == pins[str(library)]
        assert record["libraries"][str(library)]["observed"] == {
            **custody.platform_identity(library),
            "sha256": R.digest(library),
        }


def test_platform_guard_on_production_path(
    fixture: Fixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    inputs, state, _root, lib = _prepared_mat_fixture(fixture, monkeypatch)
    custody = state.custody
    library = fixture.root / "platform/libnative.so"
    library.parent.mkdir()
    library.write_bytes(b"real local mapped identity")
    identity = custody.platform_identity(library)
    monkeypatch.setattr(
        custody,
        "executable_mapped_files",
        lambda: {str(library): {key: identity[key] for key in ("device", "inode")}},
    )
    instrument = R.load_mat_instrument()
    instrument.mapped_files = lambda: {str(lib), str(library)}
    policy_path = inputs.run / "trace-policy.json"
    policy = json.loads(policy_path.read_text())
    policy["allowed"]["platform_system"] = [str(library.parent)]
    policy_path.write_text(json.dumps(policy))
    inputs.prestage["trace_policy_sha256"] = R.digest(policy_path)
    inputs.prestage["platform_libraries"] = custody.pin_platform_libraries(
        R, {str(library)}, policy
    )
    inputs.prestage["platform_mapped"] = custody.platform_prepared_mappings(
        {str(library)}, policy
    )
    assert R.checked_prepared_mat(inputs)[1]["platform_libraries"]["status"] == "PASS"
    library.write_bytes(b"tampered platform instrument")
    with pytest.raises(R.Refused) as caught:
        R.checked_prepared_mat(inputs)
    assert caught.value.guard == "MAT_PLATFORM_LIBRARIES"
    assert caught.value.details["platform_libraries"]["status"] == "STOP"
    assert (
        caught.value.details["platform_libraries"]["libraries"][str(library)][
            "prepared"
        ]
        != caught.value.details["platform_libraries"]["libraries"][str(library)][
            "observed"
        ]
    )


def test_trace_policy_disjoint_under_system_run(
    fixture: Fixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    custody, run, _roots = _prepare_fixture(fixture, monkeypatch)
    prepared = custody.prepare(R, fixture.config_path, fixture.config_sha, run)
    clone = Path("/dev/shm/trace-policy-fixture/repo")
    monkeypatch.setattr(
        custody, "__file__", str(clone / "nd-unfolding/fd_rpd_reco_custody.py")
    )
    native_run = Path("/dev/shm/trace-policy-fixture/run")
    prepared["mat_prefixes"] = {"PLOTUTILSROOT": str(native_run / "stage")}
    policy = custody.build_trace_policy(fixture.config, prepared, native_run)
    assert custody.trace_cwd(policy) == str(clone)
    for path, expected in (
        (native_run / "reference.json", "run"),
        (native_run / "instrument/0-setup.sh", "run"),
        (native_run / "stage/flux.root", "staged_data"),
        (clone / "nd-unfolding/fd_rpd_reco.py", "environment"),
        (clone / "nd-unfolding/__pycache__/fd_rpd_reco.cpython-311.pyc", "environment"),
    ):
        assert custody.classify_successful_open({str(path)}, "O_RDONLY", policy) == [
            expected
        ]
    assert (
        custody.classify_successful_open(
            {str(clone / "unknown.dat")}, "O_RDONLY", policy
        )
        == []
    )
    bad = json.loads(json.dumps(policy))
    bad["class_exclusions"]["system"] = []
    line = f'22 openat(AT_FDCWD, "{native_run}/reference.json", O_RDONLY) = 3'
    with pytest.raises(custody.CustodyRefused) as caught:
        custody.classify_trace([line], bad)
    assert caught.value.details["violations"][0]["categories"] == ["system", "run"]
    for key in ("cwd", "clone_root"):
        wrong = {**policy, key: "/elsewhere"}
        with pytest.raises(custody.CustodyRefused) as caught:
            custody.trace_cwd(wrong)
        assert caught.value.details["guard"] == "TRACE_CWD"


def test_platform_nonlibrary_opens_are_recorded() -> None:
    custody = _custody_module()
    roots = [
        "/opt/cray/pe",
        "/opt/ovis-ldms",
        "/opt/nvidia/hpc_sdk",
        "/opt/nersc/pymon",
        "/opt/nersc/etc/nerscjson_client",
        "/var/lib/sss/mc",
        "/platform/darshan",
        "/platform/libfabric",
    ]
    policy = {
        "cwd": "/code",
        "protected_roots": [],
        "allowed": {"platform_system": roots},
    }
    lines = [f'10 openat(AT_FDCWD, "{root}/metadata", O_RDONLY) = 3' for root in roots]
    result = custody.classify_trace(lines, policy)
    assert result["successful_open_counts"] == {"platform_system": 8}
    assert [event["path"] for event in result["events"]] == [
        root + "/metadata" for root in roots
    ]


def test_trace_stop_record_is_complete_public_and_cfs_first(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    custody = _custody_module()
    run = tmp_path / "run"
    run.mkdir()
    policy = _round3_trace_policy()
    policy["protected_roots"] = ["/protected/source"]
    lines = _trace_fixture("split_success")[:1] + [
        '41 openat(AT_FDCWD, "/protected/source", O_RDONLY) = -1 ENOENT (No such file or directory)'
    ]
    secret = "fixture-redacted-value-24998"
    provenance = {
        "trace_sha256": "a" * 64,
        "fingerprints": {"TOKEN": hashlib.sha256(secret.encode()).hexdigest()},
    }
    with pytest.raises(custody.CustodyRefused) as caught:
        custody.classify_trace_with_stop(
            R, run, "data-free-trace", lines, policy, provenance
        )
    path = run / "data-free-trace.STOP.json"
    record = json.loads(path.read_text())
    assert record["status"] == "STOP"
    assert record["trace_sha256"] == "a" * 64
    assert record["violations"] == caught.value.details["violations"]
    item = record["violations"][0]
    assert (
        item["class"] == "protected_root"
        and item["path"] == "/protected/source"
        and item["pid"] == 41
    )
    assert item["raw_lines"] == [lines[1]] and item["raw_line"] == lines[1]
    assert secret not in path.read_text()
    assert hashlib.sha256(secret.encode()).hexdigest() not in path.read_text()
    with pytest.raises(custody.CustodyRefused) as caught:
        custody.write_trace_record(R, run, "unknown-stage", {"status": "STOP"})
    assert caught.value.details["guard"] == "TRACE_RECORD_NAME"
    writes = []
    monkeypatch.setattr(R, "write_json", lambda *args: writes.append(args))
    with pytest.raises(R.Refused, match="OUTPUT_LOCATION"):
        custody.write_trace_record(
            R, Path("/global/cfs/custody-run"), "data-free-trace", record
        )
    assert writes == []


def test_prologue_persists_classifier_stop(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    custody = _custody_module()
    path = Path(
        os.environ.get(
            "FD_RPD_PROLOGUE_MODULE", REPO / "nd-unfolding/fd_rpd_reco_prologue.py"
        )
    )
    spec = importlib.util.spec_from_file_location("trace_stop_prologue", path)
    assert spec is not None and spec.loader is not None
    prologue = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "fd_rpd_reco", R)
    monkeypatch.setitem(sys.modules, "fd_rpd_reco_custody", custody)
    spec.loader.exec_module(prologue)
    run = tmp_path / "run"
    clone = str(Path(custody.__file__).resolve().parents[1])
    policy = {
        "cwd": clone,
        "clone_root": clone,
        "protected_roots": ["/protected/source"],
        "allowed": {"system": ["/etc"]},
    }
    lines = _trace_fixture("split_success")[:2] + [
        '72 openat(AT_FDCWD, "/protected/source", O_RDONLY) = -1 ENOENT (missing)'
    ]

    def prepare(_config: Any, _sha: Any, target: Path) -> str:
        target.mkdir()
        (target / "trace-policy.json").write_text(json.dumps(policy))
        return "a" * 64

    def child(_command: Any, **kwargs: Any) -> Any:
        assert kwargs["cwd"] == clone
        (run / "prologue.strace").write_text("\n".join(lines) + "\n")
        (run / "prologue-worker.json").write_text(
            json.dumps({"status": "PASS", "data_keys_read": []})
        )
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(prologue, "prepare", prepare)
    monkeypatch.setattr(prologue.subprocess, "run", child)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "prologue",
            "--config",
            str(tmp_path / "config.json"),
            "--config-sha256",
            "b" * 64,
            "--run",
            str(run),
        ],
    )
    assert prologue.main() == 4
    record = json.loads((run / "data-free-trace.STOP.json").read_text())
    assert record["status"] == "STOP" and record["worker_exit_code"] == 0
    assert record["trace_sha256"] == R.digest(run / "prologue.strace")
    assert record["policy_sha256"] == R.digest(run / "trace-policy.json")
    assert record["prepare_sha256"] == "a" * 64
    assert {item["class"] for item in record["violations"]} == {
        "parse",
        "protected_root",
    }
    assert {item["pid"] for item in record["violations"]} == {1600533, 72}
    assert all(
        item["raw_line"] and item["raw_lines"] and "path" in item
        for item in record["violations"]
    )
    assert "fingerprints" not in json.dumps(record)
    assert "STOP DATA_FREE_TRACE: syscall custody violations" in capsys.readouterr().err
    assert not (run / "data-free-trace.json").exists()


def test_platform_worker_stat_stability(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    custody, library, _mappings, policy = _platform_fixture(tmp_path, monkeypatch)
    pins = custody.pin_platform_libraries(R, {str(library)}, policy)

    def digest(path: Path) -> str:
        checksum = R.digest(path)
        path.write_bytes(b"changed during worker digest")
        return checksum

    record = custody.platform_library_record(
        SimpleNamespace(digest=digest),
        {
            "platform_libraries": pins,
            "platform_mapped": {
                name: {key: pin[key] for key in ("device", "inode")}
                for name, pin in pins.items()
            },
        },
        {str(library)},
        policy,
    )
    assert record["status"] == "STOP"
    assert record["libraries"][str(library)]["stable"] is False


def test_full_prologue4_trace_offline_with_built_policy(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Replay committed syscalls; this cannot establish native library pin identity."""
    custody = _custody_module()
    directory = REPO / "nd-unfolding/tests/fixtures/fd_rpd_reco_trace/prologue4"
    manifest = json.loads((directory / "manifest.json").read_text())
    prefix = str(Path(manifest["source_file"]).parents[1]) + "/"

    def source(name: str) -> bytes:
        return subprocess.run(
            ["git", "show", manifest["source_commit"] + ":" + prefix + name],
            cwd=REPO,
            capture_output=True,
            check=True,
        ).stdout

    config = json.loads(source("policy-config.json"))
    prepared = json.loads(source("run/prologue-prepare.json"))
    old_policy = json.loads(source("run/trace-policy.json"))
    draft = json.loads(
        (
            REPO
            / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/rpd-reco/trace-classifier-repair-20261108/production-config.draft.json"
        ).read_text()
    )
    for key in ("trace_platform_roots", "trace_platform_library_digest"):
        config[key] = draft[key]
    config["trace_instrument_directories"].append(
        "/pscratch/sd/j/josephrb/MINERvA-OmniFold/unbinned_unfolding/build"
    )
    prepared["module_paths"] = {
        ".".join(item["module_name_components"]): item["source_path"]
        for item in prepared["module_paths"]
    }
    clone = Path(prepared["run"]).parent / "repo"
    monkeypatch.setattr(
        custody, "__file__", str(clone / "nd-unfolding/fd_rpd_reco_custody.py")
    )
    monkeypatch.setattr(sys, "path", old_policy["python_directories"])
    prepared["platform_libraries"] = {
        line.split(" = ", 1)[1]
        .split("<", 1)[1]
        .split(">", 1)[0]: {"fixture_only": True}
        for line in _trace_fixture("late_ovis_loads")
        if "/opt/ovis-ldms/" in line
    }
    policy = custody.build_trace_policy(config, prepared, Path(prepared["run"]))
    # The local machine cannot resolve this platform symlink. Its target is
    # the successful descriptor annotation at committed trace line 1625.
    policy["allowed"]["platform_system"].append(
        "/global/common/software/nersc9/darshan/3.4.6-gcc-13.2.1/lib"
    )
    trace = source("run/prologue.strace")
    assert hashlib.sha256(trace).hexdigest() == manifest["source_sha256"]
    result = custody.classify_trace(trace.decode().splitlines(), policy)
    assert result["status"] == "PASS" and result["violations"] == []
    assert result["trace_line_count"] == 2709
    assert sum(len(event["raw_lines"]) == 2 for event in result["events"]) == 67
    assert (
        sum(event.get("category") == "declared_clone_cwd" for event in result["events"])
        == 2
    )
    assert result["successful_open_counts"] == {
        "system": 296,
        "instrument_directory": 7,
        "python_directory": 9,
        "environment": 552,
        "platform_system": 44,
        "pinned_platform_libs": 13,
        "run": 16,
        "private_prepare": 2,
        "pinned_mat_libs": 6,
    }


def _late_library_policy(root: Path, pins: dict[str, Any]) -> dict[str, Any]:
    return {
        "cwd": str(root),
        "protected_roots": [],
        "platform_library_pins": pins,
        "allowed": {"platform_system": [str(root)], "pinned_platform_libs": list(pins)},
    }


def test_ovis_inventory_covers_committed_exit_loads(
    fixture: Fixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    custody, run, _roots = _prepare_fixture(fixture, monkeypatch)
    ovis = Path(
        next(
            item["path"]
            for item in fixture.config["trace_platform_roots"]
            if item["role"] == "ovis_ldms"
        )
    )
    lines = _trace_fixture("late_ovis_loads")
    for line in lines:
        if "/opt/ovis-ldms/" not in line:
            continue
        requested = line.split('"', 2)[1]
        resolved = line.split(" = ", 1)[1].split("<", 1)[1].split(">", 1)[0]
        source = ovis / Path(requested).relative_to("/opt/ovis-ldms")
        target = ovis / Path(resolved).relative_to("/opt/ovis-ldms")
        target.parent.mkdir(parents=True, exist_ok=True)
        content = source.read_bytes()
        source.unlink()
        target.write_bytes(content)
        source.symlink_to(target.name)
    prepared = custody.prepare(R, fixture.config_path, fixture.config_sha, run)
    pins = {
        "/opt/ovis-ldms/" + str(Path(name).relative_to(ovis)): pin
        for name, pin in prepared["platform_libraries"].items()
    }
    policy = _late_library_policy(Path("/opt/ovis-ldms"), pins)
    policy["allowed"].update(
        system=["/proc"], run=["/dev/shm/limres-rpd-prologue4-20261108/run"]
    )
    result = custody.classify_trace(lines, policy)
    assert result["successful_open_counts"]["pinned_platform_libs"] == 13
    assert prepared["platform_mapped"] == {}
    assert len(prepared["platform_libraries"]) == 13
    assert [event["pid"] for event in result["events"]] == [1600512] * 15
    assert all(
        event["category"] == "pinned_platform_libs" for event in result["events"][2:]
    )
    for missing in pins:
        wrong = {
            **policy,
            "platform_library_pins": {
                name: pin for name, pin in pins.items() if name != missing
            },
        }
        with pytest.raises(custody.CustodyRefused) as caught:
            custody.classify_trace(lines, wrong)
        violations = caught.value.details["violations"]
        assert len(violations) == 1
        assert violations[0]["class"] == "platform_library"
        assert violations[0]["resolved"] == missing
        assert violations[0]["pid"] == 1600512
        assert violations[0]["raw_line"] in lines[2:]


@pytest.mark.parametrize("defect", ["missing", "protected", "escape"])
def test_exit_inventory_refuses_before_plain_read(tmp_path: Path, defect: str) -> None:
    custody = _custody_module()
    root = tmp_path / "ovis"
    root.mkdir()
    policy = {
        "platform_root_reasons": [{"role": "ovis_ldms", "path": str(root)}],
        "protected_roots": [],
    }
    first = root / custody.OVIS_EXIT_LIBRARIES[0]
    for relative in custody.OVIS_EXIT_LIBRARIES:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"code")
    if defect == "missing":
        first.unlink()
    if defect == "protected":
        policy["protected_roots"] = [str(first)]
    elif defect == "escape":
        target = tmp_path / "outside.so"
        target.write_bytes(b"code")
        first.unlink()
        first.symlink_to(target)
    with pytest.raises(custody.CustodyRefused) as caught:
        custody.platform_late_library_paths(policy)
    assert caught.value.details["guard"] == (
        "PLATFORM_LATE_PRESENT" if defect == "missing" else "PLATFORM_LATE_ROOT"
    )


def test_prepare_mapped_subset_refuses(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    custody, library, _mappings, policy = _platform_fixture(tmp_path, monkeypatch)
    assert str(library) in custody.platform_prepared_mappings({str(library)}, policy)
    with pytest.raises(custody.CustodyRefused) as caught:
        custody.platform_prepared_mappings(set(), policy)
    assert caught.value.details["guard"] == "PLATFORM_PREPARE_SUBSET"


@pytest.mark.parametrize(
    "defect",
    ["none", "digest", "inode", "bytes", "mtime_ns", "suffixless", "protected"],
)
def test_post_exit_library_verification(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, defect: str
) -> None:
    custody = _custody_module()
    root = tmp_path / "platform"
    root.mkdir()
    library = root / ("suffixless" if defect == "suffixless" else "late.so")
    library.write_bytes(b"\x7fELF fixture code")
    pin = {**custody.platform_identity(library), "sha256": R.digest(library)}
    pins = {str(library): pin} if defect != "suffixless" else {}
    policy = _late_library_policy(root, pins)
    lines = [f'72 openat(AT_FDCWD, "{library}", O_RDONLY) = 3<{library}>']
    if defect == "digest":
        pin["sha256"] = "0" * 64
    elif defect in {"inode", "bytes", "mtime_ns"}:
        pin[defect] = -1
    elif defect == "protected":
        policy["protected_roots"] = [str(library)]
        observed = {
            "status": "PASS",
            "events": [
                {
                    "request": str(library),
                    "resolved": str(library),
                    "path": str(library),
                    "success": True,
                    "pid": 72,
                    "raw_lines": lines,
                    "raw_line": lines[0],
                }
            ],
            "violations": [],
        }
        reads = []
        monkeypatch.setattr(R, "digest", lambda path: reads.append(path))
        with pytest.raises(custody.CustodyRefused) as caught:
            custody.check_trace_libraries(R, observed, policy)
        assert reads == []
        assert "protected" in caught.value.details["violations"][0]["reason"]
        return
    run = tmp_path / "run"
    run.mkdir()
    if defect == "none":
        checked = custody.classify_trace_with_stop(
            R, run, "data-free-trace", lines, policy, {}
        )
        assert checked["library_open_checks"][str(library)]["observed"] == pin
    else:
        with pytest.raises(custody.CustodyRefused) as caught:
            custody.classify_trace_with_stop(
                R, run, "data-free-trace", lines, policy, {}
            )
        record = json.loads((run / "data-free-trace.STOP.json").read_text())
        assert record["violations"] == caught.value.details["violations"]
        violation = record["violations"][0]
        assert violation["pid"] == 72 and violation["path"] == str(library)
        assert violation["class"] == "platform_library"
        if defect != "suffixless":
            assert violation["comparison"]["prepared"] == pin
            assert violation["comparison"]["observed"] != pin


@pytest.mark.parametrize("category", ["environment", "system", "instrument"])
def test_other_classes_cover_late_library_opens(category: str, tmp_path: Path) -> None:
    custody = _custody_module()
    root = tmp_path / category
    root.mkdir()
    library = root / "late.so"
    library.write_bytes(b"\x7fELF fixture code")
    policy = {
        "cwd": str(root),
        "protected_roots": [],
        "allowed": {"run": [str(tmp_path / "run")]},
    }
    if category == "instrument":
        policy["instrument_directories"] = [str(root)]
        policy["allowed"]["pinned_mat_libs"] = [str(library)]
        policy["mat_library_sha256"] = {str(library): R.digest(library)}
    else:
        policy["allowed"][category] = [str(root)]
    lines = [
        f'81 openat(AT_FDCWD, "{tmp_path}/run/worker.json", O_WRONLY|O_CREAT) = 3',
        f'81 openat(AT_FDCWD, "{library}", O_RDONLY) = 4<{library}>',
    ]
    checked = custody.classify_trace(lines, policy)
    assert checked["status"] == "PASS" and checked["events"][-1]["category"] == (
        "pinned_mat_libs" if category == "instrument" else category
    )
    if category == "instrument":
        assert custody.check_trace_libraries(R, checked, policy)["library_open_checks"][
            str(library)
        ]["observed"]["sha256"] == R.digest(library)
        policy["allowed"]["pinned_mat_libs"] = []
    else:
        policy["allowed"][category] = [str(root / "other-prefix")]
    with pytest.raises(custody.CustodyRefused):
        custody.classify_trace(lines, policy)


def test_real_atexit_library_load_is_checked_after_worker(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Load real local code at exit; replay its audited read after the checkpoint."""
    custody = _custody_module()
    compiler = shutil.which("cc")
    assert compiler is not None, "a C compiler is required for the exit-load fixture"
    library = tmp_path / "late.so"
    built = subprocess.run(
        [
            compiler,
            "-dynamiclib" if sys.platform == "darwin" else "-shared",
            "-fPIC",
            "-x",
            "c",
            "-",
            "-o",
            str(library),
        ],
        input="int fixture_answer(void) { return 42; }\n",
        text=True,
        capture_output=True,
        check=False,
    )
    assert built.returncode == 0, built.stderr
    pin = {**custody.platform_identity(library), "sha256": R.digest(library)}
    pins = {str(library): pin}
    policy = _late_library_policy(tmp_path, pins)
    monkeypatch.setattr(custody, "executable_mapped_files", lambda: {})
    middle = custody.platform_library_record(
        R, {"platform_libraries": pins, "platform_mapped": {}}, set(), policy
    )
    assert middle["status"] == "PASS" and middle["observed_mapped"] == []
    events = tmp_path / "child-events.json"
    checkpoint = tmp_path / "worker.json"
    script = """import atexit, ctypes, json, os, pathlib, sys
library, checkpoint, events = map(pathlib.Path, sys.argv[1:])
observed = []
def audit(name, args):
    if name == "open" and args[0] in (str(library), str(checkpoint)):
        observed.append(str(args[0]))
sys.addaudithook(audit)
def save():
    events.write_text(json.dumps(observed))
def late():
    loaded = ctypes.CDLL(str(library))
    assert loaded.fixture_answer() == 42
    assert library.read_bytes()
atexit.register(save)
atexit.register(late)
checkpoint.write_text(json.dumps({"library_loaded": False}))
"""
    child = subprocess.run(
        [sys.executable, "-c", script, str(library), str(checkpoint), str(events)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert (
        child.returncode == 0 and "Exception ignored" not in child.stderr
    ), child.stderr
    assert json.loads(events.read_text()) == [str(checkpoint), str(library)]
    lines = [
        f'91 openat(AT_FDCWD, "{checkpoint}", O_WRONLY|O_CREAT) = 3',
        f'91 openat(AT_FDCWD, "{library}", O_RDONLY) = 4<{library}>',
    ]
    checked = custody.classify_trace_with_stop(
        R, tmp_path, "data-free-trace", lines, policy, {}
    )
    assert checked["events"][-1]["category"] == "pinned_platform_libs"
    assert checked["library_open_checks"][str(library)]["observed"] == pin
    wrong = {**policy, "platform_library_pins": {}}
    with pytest.raises(custody.CustodyRefused) as caught:
        custody.classify_trace(lines, wrong)
    assert caught.value.details["violations"][0]["path"] == str(library)
    library.write_bytes(library.read_bytes() + b"changed after snapshot and exit")
    with pytest.raises(custody.CustodyRefused) as caught:
        custody.classify_trace_with_stop(
            R, tmp_path, "data-free-trace", lines, policy, {}
        )
    assert (
        caught.value.details["violations"][0]["reason"]
        == "opened library differs from prepare pin"
    )


def test_instrument_post_exit_digest_refuses(tmp_path: Path) -> None:
    custody = _custody_module()
    library = tmp_path / "instrument.so"
    library.write_bytes(b"\x7fELF instrument fixture")
    policy = {
        "cwd": str(tmp_path),
        "protected_roots": [],
        "instrument_directories": [str(tmp_path)],
        "allowed": {"pinned_mat_libs": [str(library)]},
        "mat_library_sha256": {str(library): R.digest(library)},
    }
    lines = [f'75 openat(AT_FDCWD, "{library}", O_RDONLY) = 3<{library}>']
    assert (
        custody.classify_trace_with_stop(
            R, tmp_path, "data-free-trace", lines, policy, {}
        )["status"]
        == "PASS"
    )
    library.write_bytes(b"\x7fELF changed after worker")
    with pytest.raises(custody.CustodyRefused) as caught:
        custody.classify_trace_with_stop(
            R, tmp_path, "data-free-trace", lines, policy, {}
        )
    violation = caught.value.details["violations"][0]
    assert violation["class"] == "instrument_library"
    assert (
        violation["comparison"]["prepared"]
        == policy["mat_library_sha256"][str(library)]
    )
    assert violation["comparison"]["observed"]["sha256"] == R.digest(library)


def test_prepared_mapping_identity_refuses(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    custody, library, mappings, policy = _platform_fixture(tmp_path, monkeypatch)
    prepared = {
        "platform_libraries": custody.pin_platform_libraries(R, {str(library)}, policy),
        "platform_mapped": json.loads(json.dumps(mappings)),
    }
    assert (
        custody.platform_library_record(R, prepared, {str(library)}, policy)["status"]
        == "PASS"
    )
    prepared["platform_mapped"][str(library)]["inode"] += 1
    record = custody.platform_library_record(R, prepared, {str(library)}, policy)
    assert record["status"] == "STOP"
    assert (
        record["libraries"][str(library)]["mapped_identity"] == mappings[str(library)]
    )
    assert (
        record["libraries"][str(library)]["prepared_mapped_identity"]
        != mappings[str(library)]
    )


@pytest.mark.parametrize("pinned", [False, True], ids=["unpinned", "pinned"])
def test_negative_check_after_exit_library_custody(
    fixture: Fixture, monkeypatch: pytest.MonkeyPatch, pinned: bool
) -> None:
    """The negative-check path must verify late code and publish its refusal."""
    custody = _custody_module()
    run = fixture.run.resolve()
    run.mkdir()
    dependency = run / "constraint.txt"
    dependency.write_text("own staged dependency")
    custody.write_private_prepare(
        R,
        run,
        "prestage",
        {
            "run": str(run),
            "connect_id": "negative-late-library",
            "mat_dependencies": [
                {"environment_key": "MPARAMFILES", "staged": str(dependency)}
            ],
        },
        protected_roots=[],
    )
    platform = fixture.root / "platform"
    platform.mkdir()
    library = platform / "suffixless"
    library.write_bytes(b"\x7fELF disposable late library")
    pin = {**custody.platform_identity(library), "sha256": R.digest(library)}
    pins = {str(library): pin} if pinned else {}
    clone = str(Path(custody.__file__).resolve().parents[1])
    policy = {**_late_library_policy(platform, pins), "cwd": clone, "clone_root": clone}
    policy_path = run / "trace-policy.json"
    policy_path.write_text(json.dumps(policy))
    policy_sha = R.digest(policy_path)
    raw = f'817 openat(AT_FDCWD, "{library}", O_RDONLY|O_CLOEXEC) = 4<{library}>'
    # Both inputs pass path classification. Only after-exit inspection distinguishes
    # the unpinned, suffixless ELF from ordinary platform metadata.
    assert custody.classify_trace([raw], policy)["status"] == "PASS"
    calls = []

    def stopped(command: Any, **kwargs: Any) -> Any:
        calls.append(command)
        assert not dependency.exists()
        assert (
            dependency.with_name(dependency.name + ".negative-check-held").read_text()
            == "own staged dependency"
        )
        assert kwargs["cwd"] == clone
        (run / "flux-extract.STOP.json").write_text(
            json.dumps({"status": "STOP", "guard": "MAT_DATA_STAGE"})
        )
        (run / "missing-dependency.strace").write_text(raw + "\n")
        return SimpleNamespace(returncode=4, stdout="", stderr="STOP MAT_DATA_STAGE")

    monkeypatch.setattr(custody.subprocess, "run", stopped)
    if pinned:
        receipt = custody.missing_dependency_check(
            R, fixture.config_path, fixture.config_sha, run, policy_sha
        )
        assert (
            receipt["status"] == "PASS"
            and receipt["expected_guard"] == "MAT_DATA_STAGE"
        )
        assert (
            receipt["trace_check"]["library_open_checks"][str(library)]["observed"]
            == pin
        )
        assert (run / "missing-dependency-check.json").is_file()
        assert (run / "missing-dependency.STOP.json").is_file()
        assert not (run / "missing-dependency-trace.STOP.json").exists()
    else:
        with pytest.raises(custody.CustodyRefused) as caught:
            custody.missing_dependency_check(
                R, fixture.config_path, fixture.config_sha, run, policy_sha
            )
        assert str(caught.value) == "library custody violations"
        record = json.loads((run / "missing-dependency-trace.STOP.json").read_text())
        assert record["status"] == "STOP"
        assert record["policy_sha256"] == policy_sha
        assert record["trace_sha256"] == R.digest(run / "missing-dependency.strace")
        assert record["violations"] == caught.value.details["violations"]
        assert len(record["violations"]) == 1
        violation = record["violations"][0]
        assert violation["class"] == "platform_library"
        assert violation["path"] == violation["resolved"] == str(library)
        assert violation["pid"] == 817
        assert violation["raw_line"] == raw and violation["raw_lines"] == [raw]
        assert violation["reason"] == "library open has no prepare pin"
        assert violation["comparison"] == {
            "prepared": None,
            "kind": "library",
            "stat": custody.platform_identity(library),
        }
        assert "fingerprints" not in json.dumps(record)
        assert not (run / "missing-dependency-check.json").exists()
        assert (run / "flux-extract.STOP.json").is_file()
    assert len(calls) == 1 and "/usr/bin/strace" == calls[0][0]
    assert dependency.read_text() == "own staged dependency"
    assert not dependency.with_name(dependency.name + ".negative-check-held").exists()

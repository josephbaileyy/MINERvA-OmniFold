#!/usr/bin/env python3
"""Reconstruction-level playlist diagnostics under FD-RPD-RECO revision 2.

The execution order is pins, p0, d2-predict, step0, c0, d1, d2. A committed
simulation prediction is mandatory before data access. These diagnostics cannot
change an estimator, covariance, publication scope, or the unknown-cause clause.
"""

from __future__ import annotations

import argparse
import contextlib
import contextvars
import csv
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import time
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

THREAD_KEYS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
)
if __name__ == "__main__":
    for _thread_key in THREAD_KEYS:
        os.environ.setdefault(_thread_key, "1")

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]
Json = dict[str, Any]
PLAYLISTS = ("1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P")
GROUPS = {"PA": PLAYLISTS[:6], "PB": PLAYLISTS[6:9], "PC": PLAYLISTS[9:]}
OWN_FLUX = {
    playlist: flux
    for group, flux in (("PA", "1D"), ("PB", "1M"), ("PC", "1N"))
    for playlist in GROUPS[group]
}
STEPS = ("pins", "p0", "d2-predict", "step0", "c0", "d1", "d2")
MC_KEYS = frozenset(
    {"MCreco", "MCgen", "w_reco", "pass_reco", "pass_truth", "data_pot", "axes"}
)
BKG_KEYS = frozenset({"bkg_reco", "bkg_w"})
BOOTSTRAPS = 200
PARTITIONS = 20
CHUNK_ROWS = 65_536
DEFAULT_WALL_SECONDS = 7_200
MAX_PRICED_WALL_SECONDS = 39_600
MEASURED_MARGIN = 1.5
DEFAULT_PLANNING_FACTOR = 10.0
TIMING_AXES = tuple(
    sorted(
        ["step", "pz", "pmu", "theta", "pt", "eavail", "q3", "W", "cells"]
        + [
            f"{axis}@{stratum}"
            for axis in ("eavail", "q3", "W")
            for stratum in range(4)
        ]
    )
)
PZ_EDGES = np.array([1.5, 2, 3, 4, 5, 6, 8, 10, 15, 20, 60], dtype=float)
PT_EDGES = np.array(
    [0, 0.15, 0.25, 0.4, 0.55, 0.7, 0.85, 1, 1.25, 1.5, 2.5, 4.5], dtype=float
)
M_PROTON = 0.938272013
M_NEUTRON = 0.93956536
M_MUON = 0.1056583755
MIN_PREDICTION = 25.0
STEP_SIGMA = 3.0
FAMILY_ALPHA = 0.001 / 12
CONDITIONAL_ALPHA = 0.001 / 48
C0_LOW = 0.03
C0_HIGH = 0.075
C0_TAIL = 0.004
CE1_MIN = 0.999
CE3_MEDIAN = 0.002
CE3_Q99 = 0.03
OUTSIDE_MAX = 0.001
NO_TRACK_MAX = 0.25
TRACK_LOWER = 0.5
TRACK_POINT = 0.75
PARTIAL_LOWER = 0.25
PREDICTION_P_MIN = 0.01
CONFIDENCE_SIGMA = 2.0


class Refused(RuntimeError):
    """A named contract guard failed; no diagnostic reading is admissible."""

    def __init__(self, guard: str, message: str):
        self.guard = guard
        self.details: Json | None = None
        super().__init__(f"{guard}: {message}")


def require(condition: bool, guard: str, message: str) -> None:
    """Refuse a failed contract predicate, retaining its declared guard name."""
    if not condition:
        raise Refused(guard, message)


def require_output_root(run: Path) -> None:
    """Refuse CFS output before creating any file or directory."""
    resolved = run.resolve()
    forbidden = Path("/global/cfs")
    require(
        resolved != forbidden and forbidden not in resolved.parents,
        "OUTPUT_LOCATION",
        "outputs must not be written to CFS",
    )


def wall_budget_seconds(
    priced_wall_seconds: int | None, measured_seconds_per_draw: float | None = None
) -> int:
    """Validate a director-priced step budget, or retain the login default."""
    require(
        (priced_wall_seconds is None) == (measured_seconds_per_draw is None),
        "PRICED_TIMING_PAIR",
        "priced wall seconds and measured seconds per draw must be supplied together",
    )
    require(
        measured_seconds_per_draw is None
        or (
            bool(np.isfinite(measured_seconds_per_draw))
            and measured_seconds_per_draw > 0
        ),
        "MEASURED_RATE",
        "measured seconds per draw must be finite and positive",
    )
    budget = (
        DEFAULT_WALL_SECONDS if priced_wall_seconds is None else priced_wall_seconds
    )
    require(
        isinstance(budget, int)
        and not isinstance(budget, bool)
        and 0 < budget <= MAX_PRICED_WALL_SECONDS,
        "WALL_BUDGET",
        "priced wall seconds must be positive and at most 39600",
    )
    return budget


def execution_fields(
    priced_wall_seconds: int | None,
    measured_seconds_per_draw: float | None,
    *,
    timing_source: Json | None = None,
    estimate: Json | None = None,
) -> Json:
    """Retain requested price, timing provenance and available step estimate."""
    return {
        "priced_wall_seconds": priced_wall_seconds,
        "wall_budget_seconds": (
            DEFAULT_WALL_SECONDS if priced_wall_seconds is None else priced_wall_seconds
        ),
        "measured_seconds_per_draw": measured_seconds_per_draw,
        "planning_factor": (
            DEFAULT_PLANNING_FACTOR
            if measured_seconds_per_draw is None
            else MEASURED_MARGIN
        ),
        "planned_seconds": None if estimate is None else estimate["planned_seconds"],
        "step_estimate": estimate,
        "estimate_status": (
            "unavailable_before_input_metadata" if estimate is None else "available"
        ),
        "timing_source": timing_source,
        "timing_chunk_shape": (
            None
            if timing_source is None
            else timing_source.get("record", {}).get("chunk_shape")
        ),
    }


def runtime_environment() -> Json:
    """Identify the actual interpreter and numerical readers used by P0."""
    import scipy
    import uproot

    return {
        "interpreter": sys.executable,
        "resolved_interpreter": str(Path(sys.executable).resolve()),
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "uproot": uproot.__version__,
    }


def digest(path: Path) -> str:
    """Return the SHA256 of a local copy or a generated product."""
    checksum = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            checksum.update(block)
    return checksum.hexdigest()


def noatime_flag() -> int:
    """Require the platform's O_NOATIME; never substitute a plain read."""
    require(hasattr(os, "O_NOATIME"), "NOATIME", "O_NOATIME is unavailable")
    return int(os.O_NOATIME)  # type: ignore[attr-defined]


_PROTECTED: contextvars.ContextVar[tuple[Path, ...]] = contextvars.ContextVar(
    "rpd_reco_inputs", default=()
)


def _audit_open(event: str, arguments: tuple[Any, ...]) -> None:
    if event != "open" or not _PROTECTED.get():
        return
    path, _mode, flags = arguments
    if isinstance(path, int) or flags & os.O_ACCMODE == os.O_WRONLY:
        return
    resolved = Path(os.fsdecode(path)).resolve()
    if any(resolved == root or root in resolved.parents for root in _PROTECTED.get()):
        require(
            bool(flags & noatime_flag()), "PLAIN_OPEN", f"plain input read: {resolved}"
        )


sys.addaudithook(_audit_open)


@contextlib.contextmanager
def read_guards(roots: Sequence[Path]) -> Iterator[None]:
    """Refuse Python-level plain reads below the declared input roots.

    ROOT is deliberately not imported: ROOT files are read by uproot, from
    staged copies only, so there is no TFile entry point in the import closure.
    """
    token = _PROTECTED.set(tuple(path.resolve() for path in roots))
    try:
        yield
    finally:
        _PROTECTED.reset(token)


def stage_copy(source: Path, destination: Path, expected: str) -> Path:
    """Copy an input through O_NOATIME and check both source and copy digests.

    Parameters
    ----------
    source, destination : Path
        Declared input and a distinct local staging path.
    expected : str
        Full, predeclared SHA256 digest.
    """
    require(
        bool(re.fullmatch(r"[0-9a-f]{64}", expected)),
        "DIGEST_FORMAT",
        "a full SHA256 is required",
    )
    require(
        source.resolve() != destination.resolve(),
        "STAGE_LOCATION",
        "source equals staged copy",
    )
    require(source.is_file(), "INPUT_EXISTS", f"missing input {source}")
    if destination.exists():
        require(
            digest(destination) == expected,
            "STAGED_DIGEST",
            f"changed staged copy {destination}",
        )
        return destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    checksum = hashlib.sha256()
    descriptor = os.open(source, os.O_RDONLY | noatime_flag())
    with os.fdopen(descriptor, "rb") as incoming, destination.open("xb") as outgoing:
        before = os.fstat(incoming.fileno())
        for block in iter(lambda: incoming.read(1 << 20), b""):
            checksum.update(block)
            outgoing.write(block)
        after = os.fstat(incoming.fileno())
    require(
        (before.st_ino, before.st_size, before.st_mtime_ns)
        == (after.st_ino, after.st_size, after.st_mtime_ns),
        "INPUT_CHANGED",
        f"input changed while copying {source}",
    )
    require(
        checksum.hexdigest() == expected, "INPUT_DIGEST", f"digest mismatch {source}"
    )
    require(
        digest(destination) == expected, "STAGED_DIGEST", f"copy differs {destination}"
    )
    return destination


def _json_value(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return _json_value(value.tolist())
    if isinstance(value, np.generic):
        return _json_value(value.item())
    if isinstance(value, float) and not np.isfinite(value):
        return "Infinity" if value > 0 else ("-Infinity" if value < 0 else None)
    if isinstance(value, dict):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    return value


def write_json(path: Path, record: Json) -> None:
    """Write a new JSON record, refusing overwrites and nonstandard numbers."""
    with path.open("x") as stream:
        json.dump(
            _json_value(record), stream, indent=2, allow_nan=False, sort_keys=True
        )
        stream.write("\n")


@dataclass(frozen=True)
class Sample:
    """Event rows and their nominal weights, without data-dependent cuts."""

    playlist: str
    kind: str
    values: FloatArray
    weights: FloatArray
    truth: FloatArray | None = None


class Inputs:
    """Digest-checked staged inputs and the gate before any measured key.

    Parameters
    ----------
    config_path : Path
        JSON configuration whose input identities will be bound at binding 2.
    config_sha : str
        Expected SHA256 of that configuration.
    run : Path
        Exclusive output directory, separate from declared source roots.
    """

    def __init__(
        self,
        config_path: Path,
        config_sha: str,
        run: Path,
        *,
        priced_wall_seconds: int | None = None,
        measured_seconds_per_draw: float | None = None,
        timing_record: Path | None = None,
        timing_record_sha256: str | None = None,
    ):
        require_output_root(run)
        self.wall_seconds = wall_budget_seconds(
            priced_wall_seconds, measured_seconds_per_draw
        )
        self.priced_wall_seconds = priced_wall_seconds
        self.measured_seconds_per_draw = measured_seconds_per_draw
        self.timing_source: Json | None = None
        self.step_estimate: Json | None = None
        self.run = run.resolve()
        self.started = time.monotonic()
        self.run.mkdir(parents=True, exist_ok=True)
        self.staged = self.run / "staged"
        with read_guards([config_path]):
            copy = stage_copy(config_path, self.staged / "config.json", config_sha)
        self.config: Json = json.loads(copy.read_text())
        require(
            self.config.get("configuration_status", "READY") == "READY",
            "CONFIG_READY",
            "draft configuration has unresolved runtime fields",
        )
        self.hashes: dict[str, str] = {str(config_path.resolve()): config_sha}
        self.roots = [config_path.resolve(), Path(self.config["dump_root"]).resolve()]
        for key in ("pins", "h2", "inventory", "constants", "flux_source"):
            self.roots.append(Path(self.config[key]["path"]).resolve())
        self.roots.append(Path(self.config["flux_root"]).resolve())
        require(
            not any(
                self.staged == root or root in self.staged.parents
                for root in self.roots
            ),
            "STAGE_LOCATION",
            "staging is inside an input root",
        )
        self.keys_read: list[dict[str, str]] = []
        self.prediction: tuple[Path, str] | None = None
        self.prediction_checks = 0
        self.prediction_prefix = f"prediction-{time.time_ns()}"
        self.pins: dict[str, tuple[Path, str]] = {}
        self.known_siblings: list[Json] = []
        self.copies: dict[tuple[Path, str], Path] = {}
        require(
            (
                measured_seconds_per_draw is None
                and timing_record is None
                and timing_record_sha256 is None
            )
            or (
                measured_seconds_per_draw is not None
                and timing_record is not None
                and timing_record_sha256 is not None
            ),
            "TIMING_SOURCE",
            "measured pricing requires a pinned timing record, and unpriced runs cannot carry one",
        )
        if timing_record is not None and timing_record_sha256 is not None:
            self.roots.append(timing_record.resolve())
            copied = self.copy(timing_record, timing_record_sha256)
            record = json.loads(copied.read_text())
            require(
                isinstance(record, dict),
                "TIMING_SHAPE",
                "timing record must be an object",
            )
            shape = record.get("chunk_shape", {})
            require(
                isinstance(shape, dict)
                and isinstance(shape.get("axes"), list)
                and record.get("seconds_per_draw") == measured_seconds_per_draw
                and shape.get("rows") == CHUNK_ROWS
                and shape.get("bootstrap_replicas") == BOOTSTRAPS
                and shape.get("weight_variants") == 5
                and shape.get("pass") == "real-signal"
                and sorted(shape.get("axes", [])) == list(TIMING_AXES),
                "TIMING_SHAPE",
                "timing record must match S and a full real-pass signal chunk",
            )
            require(
                record.get("environment") == runtime_environment(),
                "TIMING_ENVIRONMENT",
                "timing environment differs from the current interpreter/readers",
            )
            self.timing_source = {
                "path": str(timing_record.resolve()),
                "sha256": timing_record_sha256,
                "record": record,
            }

    def execution(self) -> Json:
        """Return price and timing metadata for this invocation's record."""
        return execution_fields(
            self.priced_wall_seconds,
            self.measured_seconds_per_draw,
            timing_source=self.timing_source,
            estimate=self.step_estimate,
        )

    def plan_step(self, step: str, estimate: Json | None) -> None:
        """Apply this invocation's measured rate or P0's Poisson-only fallback."""
        draws = 0 if estimate is None else int(estimate["steps"][step]["poisson_draws"])
        rate = self.measured_seconds_per_draw
        if rate is None:
            rate = (
                0.0
                if estimate is None
                else float(estimate["timing_seconds"])
                / int(estimate["timing_sample_draws"])
            )
        factor = (
            DEFAULT_PLANNING_FACTOR
            if self.measured_seconds_per_draw is None
            else MEASURED_MARGIN
        )
        self.step_estimate = {
            "step": step,
            "poisson_draws": draws,
            "seconds_per_draw": rate,
            "factor": factor,
            "planned_seconds": draws * rate * factor,
            "unmeasured_costs": [
                "input staging and decompression",
                "weighted-quantile sorting",
                "output writing",
            ],
        }

    def check_wall_clock(self) -> None:
        """Refuse elapsed time beyond this invocation's recorded budget."""
        require(
            time.monotonic() - self.started <= self.wall_seconds,
            "WALL_CLOCK",
            f"step wall budget of {self.wall_seconds} seconds exhausted",
        )

    def copy(self, source: Path, expected: str) -> Path:
        """Stage one declared source and retain its actual identity."""
        identity = source.resolve(), expected
        if identity in self.copies:
            return self.copies[identity]
        label = hashlib.sha256(str(source.resolve()).encode()).hexdigest()[:16]
        with read_guards(self.roots):
            copied = stage_copy(
                source, self.staged / f"{label}-{source.name}", expected
            )
        self.hashes[str(source.resolve())] = expected
        self.copies[identity] = copied
        return copied

    def declared(self, name: str) -> Path:
        """Return a staged named configuration input."""
        spec = self.config[name]
        return self.copy(Path(spec["path"]), spec["sha256"])

    def load_pins(self) -> None:
        """Require exactly the declared twelve signal/background pairs."""
        lines = self.declared("pins").read_text().splitlines()
        entries: dict[str, tuple[Path, str]] = {}
        for line in lines:
            match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
            require(match is not None, "PIN_FORMAT", "invalid sha256sum line")
            assert match is not None
            source = Path(match[2])
            require(
                source.parent.resolve() == Path(self.config["dump_root"]).resolve(),
                "PIN_ROOT",
                "pin outside dump root",
            )
            require(source.name not in entries, "PIN_SET", "duplicate pin")
            entries[source.name] = (source, match[1])
        expected = {
            f"lat_{playlist}{suffix}.npz"
            for playlist in PLAYLISTS
            for suffix in ("", "_bkg")
        }
        require(
            set(entries) == expected,
            "PIN_SET",
            "pin set differs from 24 declared dumps",
        )
        actual = {
            path.name
            for path in Path(self.config["dump_root"]).iterdir()
            if path.is_file()
        }
        known_sibling_names = {f"nn_{playlist}.npz" for playlist in PLAYLISTS}
        require(
            expected <= actual and actual <= expected | known_sibling_names,
            "PIN_SET",
            f"missing {sorted(expected - actual)}, "
            f"extra {sorted(actual - expected - known_sibling_names)}",
        )
        self.known_siblings = []
        for sibling_name in sorted(actual & known_sibling_names):
            sibling_path = Path(self.config["dump_root"]) / sibling_name
            info = sibling_path.stat()
            self.known_siblings.append(
                {
                    "name": sibling_name,
                    "bytes": info.st_size,
                    "mtime_ns": info.st_mtime_ns,
                }
            )
        self.pins = entries

    def key(self, name: str, key: str) -> NDArray[Any]:
        """Read exactly one permitted NPZ key, from a checked copy only."""
        allowed = BKG_KEYS if name.endswith("_bkg.npz") else MC_KEYS | {"measured"}
        require(key in allowed, "KEY_ALLOWLIST", f"undeclared key {key}")
        if key == "measured":
            self.require_prediction()
        source, expected = self.pins[name]
        copied = self.copy(source, expected)
        with read_guards(self.roots), np.load(copied, allow_pickle=True) as archive:
            require(key in archive.files, "KEY_EXISTS", f"missing {key} in {name}")
            result = np.asarray(archive[key])
        self.keys_read.append({"file": name, "key": key})
        return result

    def require_prediction(self) -> None:
        """Require byte identity with the committed pre-data prediction record."""
        require(
            self.prediction is not None,
            "PREDICTION_COMMITTED",
            "no committed d2-predict record supplied",
        )
        assert self.prediction is not None
        path, expected = self.prediction
        require(
            path.is_file(),
            "PREDICTION_SHA",
            "prediction record is missing",
        )
        if path.resolve() not in self.roots:
            self.roots.append(path.resolve())
        self.prediction_checks += 1
        try:
            with read_guards(self.roots):
                committed_copy = stage_copy(
                    path,
                    self.staged
                    / f"{self.prediction_prefix}-{self.prediction_checks:05d}.json",
                    expected,
                )
        except Refused as error:
            if error.guard in {"INPUT_DIGEST", "STAGED_DIGEST"}:
                raise Refused(
                    "PREDICTION_SHA", "prediction record digest differs"
                ) from error
            raise
        self.hashes[str(path.resolve())] = expected
        local = self.run / "d2-predict.json"
        require(
            local.is_file() and digest(local) == expected,
            "PREDICTION_SHA",
            "committed prediction differs from this run",
        )
        record = json.loads(committed_copy.read_text())
        require(
            record.get("status") == "PASS"
            and record.get("step") == "d2-predict"
            and not record.get("dry_run", True)
            and record.get("result", {}).get("simulation_only") is True
            and record.get("code_sha256") == digest(Path(__file__))
            and record.get("config_sha256") == next(iter(self.hashes.values()))
            and not any(
                row.get("key") == "measured" for row in record.get("keys_read", [])
            ),
            "PREDICTION_CONTENT",
            "prediction is not this code/configuration's passing MC-only record",
        )
        product = record["result"]["product"]
        require(
            digest(self.run / product["path"]) == product["sha256"],
            "PRODUCT_DIGEST",
            "pre-data prediction product changed",
        )
        root = subprocess.run(
            ["git", "-C", str(path.parent), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=False,
        )
        require(
            root.returncode == 0,
            "PREDICTION_COMMITTED",
            "prediction record is not in a git worktree",
        )
        repository = Path(root.stdout.strip())
        relative = path.resolve().relative_to(repository.resolve())
        committed = subprocess.run(
            ["git", "-C", str(repository), "show", f"HEAD:{relative.as_posix()}"],
            capture_output=True,
            check=False,
        )
        require(
            committed.returncode == 0
            and hashlib.sha256(committed.stdout).hexdigest() == expected,
            "PREDICTION_COMMITTED",
            "prediction bytes are not committed at HEAD",
        )

    def samples(self, *, data: bool) -> Iterator[Sample]:
        """Stream signal, background, then data, in the fixed playlist order."""
        for kind in (
            ("signal", "background", "data") if data else ("signal", "background")
        ):
            for playlist in PLAYLISTS:
                name = f"lat_{playlist}.npz"
                if kind == "signal":
                    values = np.asarray(self.key(name, "MCreco"), dtype=float)
                    truth = np.asarray(self.key(name, "MCgen"), dtype=float)
                    weights = np.asarray(self.key(name, "w_reco"), dtype=float)
                    reco = np.asarray(self.key(name, "pass_reco"), dtype=bool)
                    passed_truth = np.asarray(self.key(name, "pass_truth"), dtype=bool)
                    require(
                        values.ndim == 2
                        and values.shape[1] == 5
                        and truth.shape == values.shape
                        and weights.shape
                        == reco.shape
                        == passed_truth.shape
                        == (len(values),),
                        "ARRAY_SHAPE",
                        f"invalid signal layout {playlist}",
                    )
                    require(
                        bool(np.all(~reco | passed_truth)),
                        "PASS_TRUTH",
                        f"reco without truth {playlist}",
                    )
                    require(
                        bool(
                            np.all(np.isfinite(values[reco]))
                            and np.all(np.isfinite(truth[reco]))
                        ),
                        "FINITE_MC",
                        f"nonfinite selected MC {playlist}",
                    )
                    weights = weights * reco
                elif kind == "background":
                    name = f"lat_{playlist}_bkg.npz"
                    values = np.asarray(self.key(name, "bkg_reco"), dtype=float)
                    weights = np.asarray(self.key(name, "bkg_w"), dtype=float)
                    truth = None
                    require(
                        values.ndim == 2
                        and values.shape[1] == 5
                        and weights.shape == (len(values),),
                        "ARRAY_SHAPE",
                        f"invalid background layout {playlist}",
                    )
                    require(
                        bool(np.all(np.isfinite(values))),
                        "FINITE_MC",
                        f"nonfinite background {playlist}",
                    )
                else:
                    values = np.asarray(self.key(name, "measured"), dtype=float)
                    require(
                        values.ndim == 2 and values.shape[1] == 5,
                        "ARRAY_SHAPE",
                        f"invalid data layout {playlist}",
                    )
                    require(
                        bool(np.all(np.isfinite(values))),
                        "FINITE_DATA",
                        f"nonfinite measured row {playlist}",
                    )
                    weights = np.ones(len(values))
                    truth = None
                require(
                    bool(np.all(np.isfinite(weights)) and np.all(weights >= 0)),
                    "WEIGHTS",
                    f"invalid weights {playlist}",
                )
                yield Sample(playlist, kind, values, weights, truth)


def weighted_quantiles(
    values: FloatArray, weights: FloatArray, fractions: FloatArray
) -> FloatArray:
    """Return weighted empirical quantiles using the first reaching each CDF value."""
    order = np.argsort(values, kind="stable")
    cumulative = np.cumsum(weights[order])
    require(
        bool(len(cumulative) and cumulative[-1] > 0),
        "MC_SUPPORT",
        "empty weighted distribution",
    )
    indices = np.searchsorted(cumulative, fractions * cumulative[-1], side="left")
    return np.asarray(values[order[np.minimum(indices, len(order) - 1)]], dtype=float)


def bin_indices(values: FloatArray, edges: FloatArray) -> NDArray[np.int64]:
    """Assign [lo, hi) bins, retaining one combined under/overflow bin."""
    indices = np.searchsorted(edges, values, side="right") - 1
    overflow = (indices < 0) | (indices >= len(edges) - 1)
    return np.where(overflow, len(edges) - 1, indices).astype(np.int64)


def reconstructed_energy(
    truth: FloatArray, mass: float
) -> tuple[FloatArray, FloatArray, FloatArray]:
    """Invert truth W in GeV and return neutrino energy, denominator and muon energy."""
    pt, pz, _recoil, _q3, invariant_mass = truth.T
    theta = np.arctan2(pt, pz)
    muon_energy = np.sqrt(pt * pt + pz * pz + M_MUON * M_MUON)
    denominator = 2 * mass - 4 * muon_energy * np.sin(theta / 2) ** 2
    with np.errstate(divide="ignore", invalid="ignore"):
        energy = (
            invariant_mass * invariant_mass - mass * mass + 2 * muon_energy * mass
        ) / denominator
    return energy, denominator, muon_energy


def energy_statistics(
    truth: FloatArray, weights: FloatArray, reco_pz: FloatArray, *, scale: float = 1.0
) -> Json:
    """Collect additive controls and quantile operands in reco p_parallel strata."""
    proton, denominator_p, muon = reconstructed_energy(truth, M_PROTON)
    neutron, denominator_n, _ = reconstructed_energy(truth, M_NEUTRON)
    energy = 0.5 * (proton + neutron) * scale
    theta = np.arctan2(truth[:, 0], truth[:, 1])
    with np.errstate(invalid="ignore", divide="ignore"):
        q3 = np.sqrt(4 * energy * muon * np.sin(theta / 2) ** 2 + (energy - muon) ** 2)
        error = np.abs(q3 / truth[:, 3] - 1)
        spread = np.abs(neutron / proton - 1)
    results: Json = {}
    for low, high in ((1.5, 8), (8, 15), (15, 60)):
        selected = (
            (reco_pz >= low)
            & ((reco_pz <= high) if high == 60 else (reco_pz < high))
            & (weights > 0)
        )
        total = float(weights[selected].sum())
        valid = (
            np.isfinite(energy)
            & (denominator_p > 0)
            & (denominator_n > 0)
            & (energy >= muon)
        )
        controlled = selected & valid
        results[f"{low}:{high}"] = {
            "total": total,
            "valid_weight": float(weights[controlled].sum()),
            "error": error[controlled],
            "weight": weights[controlled],
            "spread": spread[controlled],
        }
    return {"strata": results, "energy": energy}


def evaluate_energy_controls(parts: Sequence[Json]) -> Json:
    """Apply the frozen C-E gates to pooled operands, never playlist-wise gates."""
    results: Json = {}
    for stratum in ("1.5:8", "8:15", "15:60"):
        rows = [part["strata"][stratum] for part in parts]
        total = sum(row["total"] for row in rows)
        require(total > 0, "CE_SUPPORT", f"empty energy-control stratum {stratum}")
        fraction = sum(row["valid_weight"] for row in rows) / total
        require(
            fraction >= CE1_MIN, "C_E1", f"kinematic fraction {fraction} in {stratum}"
        )
        error = np.concatenate([row["error"] for row in rows])
        weight = np.concatenate([row["weight"] for row in rows])
        spread = np.concatenate([row["spread"] for row in rows])
        require(bool(np.all(np.isfinite(error))), "C_E3", "nonfinite q3 comparison")
        median, q99 = weighted_quantiles(error, weight, np.array([0.5, 0.99]))
        require(
            bool(median <= CE3_MEDIAN and q99 <= CE3_Q99),
            "C_E3",
            f"q3 discrepancy {median}, {q99} in {stratum}",
        )
        results[stratum] = {
            "C-E1": fraction,
            "C-E3_median": median,
            "C-E3_q99": q99,
            "C-E2_median_spread": weighted_quantiles(spread, weight, np.array([0.5]))[
                0
            ],
            "C-E2_q99_spread": weighted_quantiles(spread, weight, np.array([0.99]))[0],
            "C-E2_max_spread": float(spread.max()),
        }
    return results


def energy_controls(
    truth: FloatArray, weights: FloatArray, *, scale: float = 1.0
) -> Json:
    """Evaluate the C-E controls on a single pooled test sample."""
    parts = energy_statistics(truth, weights, truth[:, 1], scale=scale)
    return evaluate_energy_controls([parts])


def shape_score(offset: FloatArray, sigma: FloatArray, prediction: FloatArray) -> Json:
    """Evaluate the declared diagonal shape statistic with simulation-only sparsity."""
    from scipy.stats import chi2

    used = prediction >= MIN_PREDICTION
    require(
        bool(
            np.all(np.isfinite(offset[used]))
            and np.all(np.isfinite(sigma[used]))
            and np.all(sigma[used] > 0)
        ),
        "BOOTSTRAP_VARIANCE",
        "undefined offset or bootstrap variance in an included bin",
    )
    ndf = int(used.sum()) - 1
    if ndf < 1:
        return {
            "chi2": None,
            "ndf": ndf,
            "p": None,
            "excluded": np.flatnonzero(~used).tolist(),
        }
    inverse_variance = 1 / sigma[used] ** 2
    mean = float(np.sum(offset[used] * inverse_variance) / inverse_variance.sum())
    statistic = float(np.sum((offset[used] - mean) ** 2 * inverse_variance))
    return {
        "chi2": statistic,
        "ndf": ndf,
        "p": float(chi2.sf(statistic, ndf)),
        "weighted_mean": mean,
        "excluded": np.flatnonzero(~used).tolist(),
    }


def leave_one_out(counts: FloatArray, predictions: FloatArray) -> FloatArray:
    """Return playlist offsets against the pooled leave-one-out ratio."""
    with np.errstate(divide="ignore", invalid="ignore"):
        reference = (counts.sum(axis=-2, keepdims=True) - counts) / (
            predictions.sum(axis=-2, keepdims=True) - predictions
        )
        return np.asarray(counts / predictions / reference - 1, dtype=float)


def calibration_gate(pvalues: FloatArray) -> Json:
    """Apply C-0's two calibration tails and its per-partition family rule."""
    require(
        pvalues.shape == (PARTITIONS, 8, 12) and bool(np.all(np.isfinite(pvalues))),
        "C0_COUNT",
        "C-0 requires all 1,920 p-values",
    )
    fraction = float(np.mean(pvalues < 0.05))
    tail = float(np.mean(pvalues < 0.001))
    family = bool(np.any(pvalues < FAMILY_ALPHA))
    require(
        C0_LOW <= fraction <= C0_HIGH, "C0_CALIBRATION", f"p<.05 fraction {fraction}"
    )
    require(tail <= C0_TAIL, "C0_TAIL", f"p<.001 fraction {tail}")
    require(not family, "C0_FAMILY", "a null partition fires the family-wise rule")
    return {
        "p_lt_005": fraction,
        "p_lt_0001": tail,
        "family_fires": family,
        "pvalues": pvalues,
    }


def classify_flux_swap(
    *,
    observed: float,
    sigma_observed: float,
    fraction: float,
    sigma_fraction: float,
    predicted: float,
    sigma_predicted: float,
    prediction_p: float,
) -> str:
    """Apply the ordered, exhaustive d2 outcome table, including negative steps."""
    if step_reading(observed, sigma_observed) != "SEEN":
        return "NOT-SEEN"
    require(
        bool(
            np.all(
                np.isfinite(
                    [fraction, sigma_fraction, predicted, sigma_predicted, prediction_p]
                )
            )
        )
        and sigma_fraction >= 0
        and sigma_predicted >= 0,
        "D2_FINITE",
        "undefined d2 statistic after a seen step",
    )
    same_sign = np.sign(predicted) == np.sign(observed)
    lower = fraction - CONFIDENCE_SIGMA * sigma_fraction
    if fraction + CONFIDENCE_SIGMA * sigma_fraction < NO_TRACK_MAX or (
        not same_sign and abs(predicted) >= CONFIDENCE_SIGMA * sigma_predicted
    ):
        return "DOES-NOT-TRACK"
    if (
        lower >= TRACK_LOWER
        and fraction >= TRACK_POINT
        and same_sign
        and prediction_p >= PREDICTION_P_MIN
    ):
        return "TRACKS"
    if lower >= PARTIAL_LOWER:
        return "PARTIAL"
    return "INCONCLUSIVE"


def step_reading(observed: float, uncertainty: float) -> str:
    """Read the reconstructed step two-sided at the declared three-sigma bar."""
    return (
        "SEEN"
        if observed != 0 and abs(observed) >= STEP_SIGMA * uncertainty
        else "NOT-SEEN-AT-3σ"
    )


def bracket_outcome(primary: str, bracket: str) -> str:
    """Retain a classification only when the background bracket agrees."""
    return primary if primary == bracket else "INCONCLUSIVE"


def read_flux_histogram(path: Path, histogram: str) -> Json:
    """Read one actual ROOT histogram from a staged file using uproot."""
    import uproot

    with uproot.open(path) as root_file:
        require(
            histogram in root_file, "FLUX_HISTOGRAM", f"missing histogram {histogram}"
        )
        values, edges = root_file[histogram].to_numpy(flow=False)
    require(
        values.ndim == 1
        and len(edges) == len(values) + 1
        and bool(np.all(np.diff(edges) > 0))
        and bool(np.all(np.isfinite(values)) and np.all(values >= 0)),
        "FLUX_LAYOUT",
        "invalid flux histogram",
    )
    return {
        "histogram": histogram,
        "edges": edges,
        "values": values,
        "integral": float(np.sum(values * np.diff(edges))),
    }


def p0(inputs: Inputs) -> Json:
    """Record explicit runtime flux selections, constants and the source-pinned P-F premise."""
    rows = list(
        csv.DictReader(
            io.StringIO(inputs.declared("inventory").read_text()), delimiter="\t"
        )
    )
    selection = inputs.config["flux_selection"]
    require(
        set(selection) == {"1D", "1M", "1N"},
        "FLUX_SELECTION",
        "P0 requires three explicit file selections",
    )
    spectra: Json = {}
    for group, spec in selection.items():
        matches = [
            row
            for row in rows
            if row["playlist_label"] == group
            and row["relative_path"] == spec["relative_path"]
        ]
        require(
            len(matches) == 1,
            "FLUX_SELECTION",
            f"selection {group} is absent or ambiguous in C-N inventory",
        )
        row = matches[0]
        source = Path(inputs.config["flux_root"]) / row["relative_path"]
        require(
            source.resolve().is_relative_to(Path(inputs.config["flux_root"]).resolve()),
            "FLUX_SELECTION",
            "flux path escapes declared root",
        )
        copy = inputs.copy(source, row["sha256"])
        require(
            copy.stat().st_size == int(row["bytes"]),
            "FLUX_SIZE",
            "flux size differs from C-N",
        )
        with read_guards(inputs.roots):
            spectrum = read_flux_histogram(copy, spec["histogram"])
        spectra[group] = {
            **spectrum,
            "path_opened": str(copy),
            "original_path": str(source),
            "sha256": row["sha256"],
            "retention": spec["retention"],
        }
    constants = inputs.declared("constants").read_text()
    parsed = {}
    for mass in ("M_p", "M_n"):
        match = re.search(rf"\b{mass}\s*=\s*([\d.]+)", constants)
        require(match is not None, "MASS_CONSTANTS", f"missing {mass} in CVUniverse")
        assert match is not None
        parsed[mass] = float(match[1]) / 1000
    require(
        parsed == {"M_p": M_PROTON, "M_n": M_NEUTRON},
        "MASS_CONSTANTS",
        "CVUniverse constants differ",
    )
    source_path = inputs.declared("flux_source")
    lines = source_path.read_text().splitlines()
    evidence: Json = {}
    premise = inputs.config["premise"]
    for role in (
        "cv_numerator",
        "common_generation_denominator",
        "playlist_mapping",
        "per_pot_units",
    ):
        spec = premise["evidence"][role]
        first, last = spec["lines"]
        excerpt = "\n".join(lines[first - 1 : last])
        require(
            1 <= first <= last <= len(lines)
            and bool(excerpt.strip())
            and hashlib.sha256(excerpt.encode()).hexdigest() == spec["sha256"],
            "P_F",
            f"source evidence differs for {role}",
        )
        evidence[role] = {
            "lines": [first, last],
            "text": excerpt,
            "sha256": spec["sha256"],
        }
    require(
        premise["cv_numerator_is_selected_spectrum"] is True
        and premise["generation_denominator_is_common"] is True
        and premise["spectra_are_per_pot_density"] is True,
        "P_F",
        "bound source premise does not permit the flux ratio",
    )
    source_commit = subprocess.run(
        [
            "git",
            "-C",
            str(Path(inputs.config["flux_source"]["path"]).parent),
            "rev-parse",
            "HEAD",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    require(
        source_commit.returncode == 0
        and source_commit.stdout.strip() == inputs.config["flux_source"]["git_sha"],
        "SOURCE_COMMIT",
        "MAT checkout differs from source pin",
    )
    return {
        "spectra": spectra,
        "environment": runtime_environment(),
        "P-F": {
            "pass": True,
            "source_sha256": inputs.config["flux_source"]["sha256"],
            "git_sha": source_commit.stdout.strip(),
            "evidence": evidence,
        },
        "constants_GeV": parsed,
        "keys_read": [],
    }


def spectrum_ratio(
    energy: FloatArray, own: Json, target: Json
) -> tuple[FloatArray, NDArray[np.bool_]]:
    """Use piecewise-constant flux ratios and retain unity outside the common range."""
    own_edges = np.asarray(own["edges"], dtype=float)
    target_edges = np.asarray(target["edges"], dtype=float)
    low, high = max(own_edges[0], target_edges[0]), min(own_edges[-1], target_edges[-1])
    inside = np.isfinite(energy) & (energy >= low) & (energy < high)
    ratio = np.ones(len(energy))
    own_bin = np.searchsorted(own_edges, energy[inside], side="right") - 1
    target_bin = np.searchsorted(target_edges, energy[inside], side="right") - 1
    denominator = np.asarray(own["values"], dtype=float)[own_bin]
    require(
        bool(np.all(denominator > 0)),
        "FLUX_SUPPORT",
        "zero own flux on supported MC energy",
    )
    ratio[inside] = np.asarray(target["values"], dtype=float)[target_bin] / denominator
    return ratio, ~inside


def reporting_cells(values: FloatArray, definition: Json) -> NDArray[np.int64]:
    """Apply both the declared reporting boxes and the H2 lookup, counting exclusions."""
    names = ("pt", "pz", "eavail", "q3", "W")
    base_edges = (
        np.array([0, 0.7, 4.5]),
        np.array([1.5, 4.5, 60]),
        np.array([0, 0.8, 100]),
        np.array([0, 2, 100]),
        np.array([0, 1.8, 100]),
    )
    indices = np.stack(
        [
            np.searchsorted(edge, values[:, axis], side="right") - 1
            for axis, edge in enumerate(base_edges)
        ],
        axis=1,
    )
    valid = np.all((indices >= 0) & (indices < 2), axis=1)
    fine = np.clip(indices, 0, 1) @ np.array([16, 8, 4, 2, 1])
    lookup = np.asarray(definition["h2_to_reporting_cell"], dtype=np.int64)
    require(
        lookup.shape == (32,) and bool(np.all((lookup >= -1) & (lookup < 16))),
        "CELL_IDENTITY",
        "invalid H2 lookup",
    )
    result = np.where(valid, lookup[fine], -2)
    for cell in definition["reporting_cells"]:
        inside = np.ones(len(values), dtype=bool)
        for axis, name in enumerate(names):
            low, high = cell["box"][name]
            inside &= (values[:, axis] >= low) & (values[:, axis] < high)
        require(
            bool(np.all((result == cell["id"]) == inside)),
            "CELL_IDENTITY",
            "reporting boxes disagree with H2 lookup",
        )
    excluded = {index for box in definition["unreported_boxes"] for index in box}
    require(
        excluded == set(np.flatnonzero(lookup < 0)),
        "CELL_IDENTITY",
        "unreported boxes disagree with H2 lookup",
    )
    return result


def step0(inputs: Inputs) -> Json:
    """Freeze MC-only axes and muon strata; never open a measured key."""
    variables: dict[str, list[FloatArray]] = {
        key: [] for key in ("theta", "eavail", "q3", "W", "weight")
    }
    for sample in inputs.samples(data=False):
        if sample.kind != "signal":
            continue
        used = sample.weights > 0
        variables["weight"].append(sample.weights[used])
        variables["theta"].append(
            np.arctan2(sample.values[used, 0], sample.values[used, 1])
        )
        for name, column in (("eavail", 2), ("q3", 3), ("W", 4)):
            variables[name].append(sample.values[used, column])
    weights = np.concatenate(variables.pop("weight"))
    axes: Json = {"pz": PZ_EDGES, "pmu": PZ_EDGES, "pt": PT_EDGES}
    merged: Json = {}
    for name, pieces in variables.items():
        quantiles = weighted_quantiles(
            np.concatenate(pieces), weights, np.arange(1, 10) / 10
        )
        unique = np.unique(quantiles)
        axes[name] = np.r_[-np.inf, unique, np.inf]
        merged[name] = {
            "duplicate_edges_merged": 9 - len(unique),
            "original_deciles": quantiles,
        }
    median = weighted_quantiles(
        np.concatenate(variables["theta"]), weights, np.array([0.5])
    )[0]
    definition = json.loads(inputs.declared("h2").read_text())
    return {
        "axes": axes,
        "theta_median": median,
        "deciles": merged,
        "h2": definition,
        "simulation_only": True,
    }


def axis_assignments(
    values: FloatArray, bins: Json | None
) -> dict[str, tuple[NDArray[np.int64], int]]:
    """Map rows to common axes, retained overflows and the fixed step regions."""
    pz = values[:, 1]
    assignments = {
        "step": (
            np.where(
                (pz >= 1.5) & (pz < 8), 0, np.where((pz >= 8) & (pz < 15), 1, 2)
            ).astype(np.int64),
            3,
        )
    }
    if bins is None:
        return assignments
    theta = np.arctan2(values[:, 0], pz)
    coordinates = {
        "pz": pz,
        "pmu": np.hypot(values[:, 0], pz),
        "theta": theta,
        "pt": values[:, 0],
        "eavail": values[:, 2],
        "q3": values[:, 3],
        "W": values[:, 4],
    }
    for name, coordinate in coordinates.items():
        edges = np.asarray(bins["axes"][name], dtype=float)
        assignments[name] = bin_indices(coordinate, edges), len(edges)
    cells = reporting_cells(values, bins["h2"])
    assignments["cells"] = np.where(cells == -1, 16, np.where(cells < 0, 17, cells)), 18
    strata = (pz >= 8).astype(np.int64) * 2 + (theta >= bins["theta_median"]).astype(
        np.int64
    )
    for name in ("eavail", "q3", "W"):
        index, size = assignments[name]
        for stratum in range(4):
            assignments[f"{name}@{stratum}"] = (
                np.where(strata == stratum, index, size),
                size + 1,
            )
    for stratum in range(2):
        assignments[f"rate@{stratum}"] = np.where((pz >= 8) == bool(stratum), 0, 1), 2
    return assignments


def aggregate(
    inputs: Inputs,
    p0_record: Json,
    bins: Json | None,
    *,
    data: bool,
    partition: int | None = None,
) -> tuple[Json, Json]:
    """Stream paired per-row Poisson draws once across every axis and both swaps.

    Arrays have replica, variant, playlist, bin order. Replica zero is nominal;
    replicas 1..200 use the frozen SeedSequence words. C-0 independently assigns
    data, signal and background rows before running precisely the same scorer.
    """
    inputs.check_wall_clock()
    generators = [
        np.random.default_rng(np.random.SeedSequence([20261104, 11, replica + 1]))
        for replica in range(BOOTSTRAPS)
    ]
    allocation = (
        np.random.default_rng(np.random.SeedSequence([20261104, 13, partition + 1]))
        if partition is not None
        else None
    )
    fractions = p0_record.get("partition_fractions")
    data_assignment = (
        np.repeat(np.arange(12), p0_record["data_counts"])
        if allocation is not None
        else None
    )
    if allocation is not None:
        assert data_assignment is not None
        allocation.shuffle(data_assignment)
    data_position = 0
    accumulated: Json = {}
    controls: Json = {
        "energy_parts": [],
        "outside_weight": 0.0,
        "pb_weight": 0.0,
        "kind_totals": {
            kind: np.zeros(12) for kind in ("signal", "background", "data")
        },
    }
    spectra = p0_record["spectra"]
    for sample in inputs.samples(data=data):
        assignments = axis_assignments(sample.values, bins)
        if partition is not None:
            assignments = {
                name: assignment
                for name, assignment in assignments.items()
                if "@" not in name
            }
        count = len(sample.values)
        playlist_index = PLAYLISTS.index(sample.playlist)
        if allocation is None:
            allocated = np.full(count, playlist_index)
        elif sample.kind == "data":
            assert data_assignment is not None
            allocated = data_assignment[data_position : data_position + count]
            data_position += count
            require(
                len(allocated) == count,
                "DATA_PARTITION",
                "fixed-size data allocation is too short",
            )
        else:
            assert fractions is not None
            allocated = allocation.choice(12, count, p=fractions[sample.kind])
        controls["kind_totals"][sample.kind] += np.bincount(
            allocated, weights=sample.weights, minlength=12
        )
        factors = np.ones((5, count))
        own = spectra[OWN_FLUX[sample.playlist]]
        if sample.kind == "signal":
            assert sample.truth is not None
            energy_part = energy_statistics(
                sample.truth, sample.weights, sample.values[:, 1]
            )
            energy = energy_part.pop("energy")
            controls["energy_parts"].append(energy_part)
            for target, variant_slots in (("1D", (1, 2)), ("1M", (3, 4))):
                factor, outside = spectrum_ratio(
                    np.where(sample.weights > 0, energy, np.nan), own, spectra[target]
                )
                factors[list(variant_slots)] = factor
                if target == "1D" and sample.playlist in GROUPS["PB"]:
                    selected = (sample.values[:, 1] >= 1.5) & (sample.values[:, 1] < 15)
                    controls["pb_weight"] += float(sample.weights[selected].sum())
                    controls["outside_weight"] += float(
                        sample.weights[selected & outside].sum()
                    )
        elif sample.kind == "background":
            factors[2] = spectra["1D"]["integral"] / own["integral"]
            factors[4] = spectra["1M"]["integral"] / own["integral"]
        for name, (_indices, size) in assignments.items():
            if name not in accumulated:
                accumulated[name] = {
                    "N": np.zeros((BOOTSTRAPS + 1, 12, size)),
                    "P": np.zeros((BOOTSTRAPS + 1, 5, 12, size)),
                }
        for start in range(0, count, CHUNK_ROWS):
            inputs.check_wall_clock()
            stop = min(start + CHUNK_ROWS, count)
            for replica in range(BOOTSTRAPS + 1):
                draw = (
                    np.ones(stop - start)
                    if replica == 0
                    else generators[replica - 1].poisson(1, stop - start)
                )
                weights = sample.weights[start:stop] * draw
                for name, (indices, size) in assignments.items():
                    flat = allocated[start:stop] * size + indices[start:stop]
                    if sample.kind == "data":
                        accumulated[name]["N"][replica] += np.bincount(
                            flat, weights=weights, minlength=12 * size
                        ).reshape(12, size)
                    else:
                        for variant in ((0,) if partition is not None else range(5)):
                            accumulated[name]["P"][replica, variant] += np.bincount(
                                flat,
                                weights=weights * factors[variant, start:stop],
                                minlength=12 * size,
                            ).reshape(12, size)
    if data_assignment is not None:
        require(
            data_position == len(data_assignment)
            and bool(
                np.array_equal(
                    controls["kind_totals"]["data"], p0_record["data_counts"]
                )
            ),
            "DATA_PARTITION",
            "C-0 data allocation did not preserve exact playlist counts",
        )
    return accumulated, controls


def prediction_controls(controls: Json) -> Json:
    """Refuse an invalid inversion or excessive primary-swap energy overflow."""
    energy = evaluate_energy_controls(controls["energy_parts"])
    require(
        controls["pb_weight"] > 0,
        "SWAP_SUPPORT",
        "PB has no weight in the step regions",
    )
    fraction = controls["outside_weight"] / controls["pb_weight"]
    require(
        fraction <= OUTSIDE_MAX,
        "OUTSIDE_RANGE",
        f"primary-swap out-of-range weight fraction {fraction}",
    )
    return {"energy": energy, "outside_fraction": fraction}


def _double_step(counts: FloatArray, prediction: FloatArray) -> FloatArray:
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.asarray(
            (counts[..., 1] / prediction[..., 1])
            / (counts[..., 0] / prediction[..., 0]),
            dtype=float,
        )


def predicted_steps(prediction: FloatArray, variant: int = 1) -> FloatArray:
    """Return each playlist's simulation-only change when moved to the target flux."""
    return _double_step(prediction[:, variant], prediction[:, 0]) - 1


def observed_steps(
    counts: FloatArray, prediction: FloatArray, variant: int = 0
) -> FloatArray:
    """Return playlist steps against PA, leaving each PA playlist out of its reference."""
    pa = [PLAYLISTS.index(playlist) for playlist in GROUPS["PA"]]
    observed = _double_step(counts, prediction[:, variant])
    reference = np.broadcast_to(
        _double_step(counts[:, pa].sum(axis=1), prediction[:, variant, pa].sum(axis=1))[
            :, None
        ],
        observed.shape,
    ).copy()
    for index in pa:
        others = [item for item in pa if item != index]
        reference[:, index] = _double_step(
            counts[:, others].sum(axis=1), prediction[:, variant, others].sum(axis=1)
        )
    return observed / reference - 1


def group_step(
    counts: FloatArray, prediction: FloatArray, group: str, variant: int = 0
) -> FloatArray:
    """Return a group's step against the PA pooled reference."""
    members = [PLAYLISTS.index(playlist) for playlist in GROUPS[group]]
    pa = [PLAYLISTS.index(playlist) for playlist in GROUPS["PA"]]
    return (
        _double_step(
            counts[:, members].sum(axis=1), prediction[:, variant, members].sum(axis=1)
        )
        / _double_step(counts[:, pa].sum(axis=1), prediction[:, 0, pa].sum(axis=1))
        - 1
    )


def _sigma(replicas: FloatArray) -> FloatArray:
    with np.errstate(invalid="ignore"):
        return np.asarray(np.std(replicas[1:], axis=0, ddof=1), dtype=float)


def score_axes(histograms: Json, *, sigma_scale: float = 1.0) -> Json:
    """Score all axes with the same paired bootstrap, retaining fixed excluded bins."""
    results: Json = {}
    for axis, counts in histograms.items():
        if axis == "step" or axis.startswith("rate@"):
            continue
        observed = counts["N"]
        prediction = counts["P"][:, 0]
        # The final bin on a conditional axis is the other strata, never a cut
        # within the selected stratum. The cells' final bin records unreported rows.
        if axis == "cells":
            observed, prediction = observed[..., :16], prediction[..., :16]
        elif "@" in axis:
            observed, prediction = observed[..., :-1], prediction[..., :-1]
        offsets = leave_one_out(observed, prediction)
        uncertainty = _sigma(offsets) * sigma_scale
        results[axis] = [
            shape_score(offsets[0, index], uncertainty[index], prediction[0, index])
            | {
                "playlist": playlist,
                "offset": offsets[0, index],
                "sigma": uncertainty[index],
                "N": observed[0, index],
                "P": prediction[0, index],
            }
            for index, playlist in enumerate(PLAYLISTS)
        ]
    return results


def hadronic_reading(scores: Json) -> Json:
    """Classify hadronic differences using the frozen unconditional/conditional bars."""
    unconditional = {
        axis: [
            row["playlist"]
            for row in scores[axis]
            if row["p"] is not None and row["p"] < FAMILY_ALPHA
        ]
        for axis in ("eavail", "q3", "W")
    }
    conditional = {
        f"{axis}@{stratum}": [
            row["playlist"]
            for row in scores[f"{axis}@{stratum}"]
            if row["p"] is not None and row["p"] < CONDITIONAL_ALPHA
        ]
        for axis in ("eavail", "q3", "W")
        for stratum in range(4)
    }
    outcome = (
        "HADRONIC-CONDITIONAL"
        if any(conditional.values())
        else (
            "HADRONIC-VIA-MUON"
            if any(unconditional.values())
            else "HADRONIC-NOT-DETECTED"
        )
    )
    return {
        "outcome": outcome,
        "unconditional": unconditional,
        "conditional": conditional,
    }


def _save_histograms(run: Path, step: str, histograms: Json) -> Json:
    path = run / f"{step}.npz"
    require(not path.exists(), "OUTPUT_EXISTS", f"refusing overwrite {path}")
    with path.open("xb") as stream:
        np.savez(
            stream,
            **{
                f"{axis}__{kind}": values
                for axis, record in histograms.items()
                for kind, values in record.items()
            },
        )
    return {"path": path.name, "sha256": digest(path)}


def _load_histograms(run: Path, product: Json) -> Json:
    path = run / product["path"]
    require(
        digest(path) == product["sha256"], "PRODUCT_DIGEST", f"changed product {path}"
    )
    result: Json = {}
    with np.load(path, allow_pickle=False) as archive:
        for key in archive.files:
            axis, kind = key.split("__")
            result.setdefault(axis, {})[kind] = np.asarray(archive[key], dtype=float)
    return result


def _read_record(run: Path, step: str) -> Json:
    path = run / f"{step}.json"
    require(path.is_file(), "PREDECESSOR", f"missing passing {step} record")
    record: Json = json.loads(path.read_text())
    require(
        record.get("status") == "PASS" and record.get("step") == step,
        "PREDECESSOR",
        f"{step} did not pass",
    )
    return record


def require_predecessors(
    inputs: Inputs, step: str, *, dry_run: bool
) -> dict[str, Json]:
    """Validate the complete predecessor chain, code identity and input configuration."""
    records: dict[str, Json] = {}
    current_code = digest(Path(__file__))
    previous: str | None = None
    for name in STEPS[: STEPS.index(step)]:
        record = _read_record(inputs.run, name)
        require(
            record["code_sha256"] == current_code
            and record["config_sha256"] == next(iter(inputs.hashes.values()))
            and record["dry_run"] == dry_run,
            "PREDECESSOR_IDENTITY",
            "code, configuration or run class changed",
        )
        require(
            record["predecessor_sha256"] == previous,
            "PREDECESSOR_SHA",
            f"broken chain at {name}",
        )
        records[name] = record
        previous = digest(inputs.run / f"{name}.json")
    return records


def runtime_estimate(inputs: Inputs) -> Json:
    """Price Poisson sampling on a bounded MC-independent local timing sample.

    This is an estimate, never authorization to run. It includes the real pass,
    prediction pass and all twenty C-0 partitions, and states the unmeasured I/O
    and histogramming cost explicitly.
    """
    mc_rows = 0
    for playlist in PLAYLISTS:
        mc_rows += len(inputs.key(f"lat_{playlist}.npz", "w_reco"))
        mc_rows += len(inputs.key(f"lat_{playlist}_bkg.npz", "bkg_w"))
    generator = np.random.default_rng(20261104)
    start = time.perf_counter()
    generator.poisson(1, 262_144)
    elapsed = time.perf_counter() - start
    data_estimate = int(inputs.config.get("data_rows_estimate", 4_091_707))
    draws = BOOTSTRAPS * (mc_rows + (PARTITIONS + 1) * (mc_rows + data_estimate))
    poisson_seconds = elapsed * draws / 262_144
    # Binning, five weight variants and repeated I/O are not timed by this probe.
    conservative_seconds = poisson_seconds * DEFAULT_PLANNING_FACTOR
    step_draws = {
        "pins": 0,
        "p0": 0,
        "d2-predict": BOOTSTRAPS * mc_rows,
        "step0": 0,
        "c0": BOOTSTRAPS * (PARTITIONS + 1) * (mc_rows + data_estimate),
        "d1": 0,
        "d2": 0,
    }
    steps = {
        step: {
            "poisson_draws": count,
            "poisson_only_seconds": elapsed * count / 262_144,
            "planning_seconds_with_factor_10": elapsed
            * count
            / 262_144
            * DEFAULT_PLANNING_FACTOR,
        }
        for step, count in step_draws.items()
    }
    return {
        "mc_background_rows": mc_rows,
        "data_rows_estimate_not_read": data_estimate,
        "poisson_draws": draws,
        "timing_sample_draws": 262_144,
        "timing_seconds": elapsed,
        "poisson_only_seconds": poisson_seconds,
        "planning_seconds_with_factor_10": conservative_seconds,
        "exceeds_two_hours": conservative_seconds > DEFAULT_WALL_SECONDS,
        "needs_director_price": conservative_seconds > inputs.wall_seconds,
        "summary_only": "campaign total; admission compares each step's own estimate",
        "steps": steps,
        "wall_budget_seconds": inputs.wall_seconds,
        "unmeasured_costs": [
            "NPZ decompression",
            "histogramming",
            "sorting weighted quantiles",
        ],
        "node_hours_authorized": 0,
    }


def _c0(inputs: Inputs, records: dict[str, Json]) -> Json:
    inputs.require_prediction()
    p0_result = records["p0"]["result"]
    bins = records["step0"]["result"]
    actual, actual_controls = aggregate(inputs, p0_result, bins, data=True)
    predicted = _load_histograms(inputs.run, records["d2-predict"]["result"]["product"])
    require(
        bool(np.array_equal(actual["step"]["P"], predicted["step"]["P"])),
        "PREDICTION_REPRODUCED",
        "MC prediction changed after data access",
    )
    totals = actual_controls["kind_totals"]
    fractions = {
        kind: (
            weights / weights.sum()
            if weights.sum() > 0
            else totals["signal"] / totals["signal"].sum()
        )
        for kind, weights in totals.items()
    }
    null_config = {
        **p0_result,
        "partition_fractions": fractions,
        "data_counts": totals["data"].astype(np.int64),
    }
    pvalues = np.empty((PARTITIONS, 8, 12))
    axes = ("pz", "pmu", "theta", "pt", "eavail", "q3", "W", "cells")
    partition_disclosures = []
    for partition in range(PARTITIONS):
        histograms, controls = aggregate(
            inputs, null_config, bins, data=True, partition=partition
        )
        partition_disclosures.append(
            {
                "partition": partition,
                "target_data_counts": null_config["data_counts"],
                "actual_data_counts": controls["kind_totals"]["data"],
                "target_weight_fractions": fractions,
                "realized_weight_fractions": {
                    kind: weights / weights.sum() if weights.sum() > 0 else np.zeros(12)
                    for kind, weights in controls["kind_totals"].items()
                    if kind != "data"
                },
                "read_by_scoring": False,
            }
        )
        scores = score_axes(histograms)
        for axis_index, name in enumerate(axes):
            require(
                all(row["p"] is not None for row in scores[name]),
                "C0_COUNT",
                f"unscorable null axis {name}",
            )
            pvalues[partition, axis_index] = [row["p"] for row in scores[name]]
    try:
        calibration = calibration_gate(pvalues)
    except Refused as error:
        error.details = {
            "pvalues": pvalues,
            "partition_disclosures": partition_disclosures,
            "input_sha256": inputs.hashes,
            "keys_read": inputs.keys_read,
            "readings": None,
        }
        raise
    return {
        "calibration": calibration,
        "partition_fractions": null_config["partition_fractions"],
        "partition_disclosures": partition_disclosures,
        "product": _save_histograms(inputs.run, "c0", actual),
    }


def _rate_summary(histograms: Json, inputs: Inputs) -> Json:
    pots = np.array(
        [float(inputs.key(f"lat_{playlist}.npz", "data_pot")) for playlist in PLAYLISTS]
    )
    require(
        bool(np.all(np.isfinite(pots)) and np.all(pots > 0)), "POT", "invalid data POT"
    )
    rows: Json = {}
    for stratum, axis, selected_bin in (
        ("overall", "step", None),
        ("pz<8", "rate@0", 0),
        ("pz>=8", "rate@1", 0),
    ):
        counts = histograms[axis]["N"]
        predictions = histograms[axis]["P"][:, 0]
        if selected_bin is None:
            counts, predictions = counts.sum(axis=-1), predictions.sum(axis=-1)
        else:
            counts, predictions = (
                counts[..., selected_bin],
                predictions[..., selected_bin],
            )
        rows[stratum] = {}
        populations = {
            playlist: [index] for index, playlist in enumerate(PLAYLISTS)
        } | {
            group: [PLAYLISTS.index(playlist) for playlist in members]
            for group, members in GROUPS.items()
        }
        for name, members in populations.items():
            exposure = pots[members].sum()
            rate_data = counts[:, members].sum(axis=1) / exposure
            rate_mc = predictions[:, members].sum(axis=1) / exposure
            rows[stratum][name] = {
                "data_per_POT": rate_data[0],
                "data_sigma": _sigma(rate_data),
                "prediction_per_POT": rate_mc[0],
                "prediction_sigma": _sigma(rate_mc),
                "data_pot": exposure,
            }
    return rows


def _d1(inputs: Inputs, records: dict[str, Json]) -> Json:
    inputs.require_prediction()
    histograms = _load_histograms(inputs.run, records["c0"]["result"]["product"])
    scores = score_axes(histograms)
    step = histograms["step"]
    groups: Json = {}
    for group in ("PB", "PC"):
        replicas = group_step(step["N"], step["P"], group)
        uncertainty = float(_sigma(replicas))
        require(
            bool(np.all(np.isfinite(replicas))) and uncertainty > 0,
            "STEP_VARIANCE",
            "undefined step bootstrap",
        )
        groups[group] = {
            "s": replicas[0],
            "sigma": uncertainty,
            "sign": int(np.sign(replicas[0])),
            "reading": step_reading(float(replicas[0]), uncertainty),
        }
    firing = {
        axis: [
            row["playlist"]
            for row in scores[axis]
            if row["p"] is not None and row["p"] < FAMILY_ALPHA
        ]
        for axis in ("pz", "pmu", "theta", "pt")
    }
    carriers = {
        axis: {
            "carries": [
                row["playlist"]
                for row in rows
                if row["p"] is not None
                and row["p"] < (CONDITIONAL_ALPHA if "@" in axis else FAMILY_ALPHA)
                and row["playlist"] in {"1L", "1M"}
            ],
            "rest": [
                row["playlist"]
                for row in rows
                if row["p"] is not None
                and row["p"] < (CONDITIONAL_ALPHA if "@" in axis else FAMILY_ALPHA)
                and row["playlist"] not in {"1L", "1M"}
            ],
        }
        for axis, rows in scores.items()
    }
    return {
        "R-d1.0": groups,
        "R-d1.1": {
            "firing": firing,
            "p_lt_0001": {
                axis: [
                    row["playlist"]
                    for row in scores[axis]
                    if row["p"] is not None and row["p"] < 0.001
                ]
                for axis in firing
            },
        },
        "R-d1.2": _rate_summary(histograms, inputs),
        "R-d1.3": hadronic_reading(scores),
        "R-d1.4": carriers,
        "axes": scores,
        "unreported_rows": histograms["cells"]["N"][0, :, 16],
        "unreported_prediction": histograms["cells"]["P"][0, 0, :, 16],
        "overflow_rows": histograms["cells"]["N"][0, :, 17],
        "overflow_prediction": histograms["cells"]["P"][0, 0, :, 17],
    }


def _d2(inputs: Inputs, records: dict[str, Json]) -> Json:
    from scipy.stats import chi2

    inputs.require_prediction()
    if records["d1"]["result"]["R-d1.0"]["PB"]["reading"] != "SEEN":
        return {"outcome": "NOT-SEEN", "f": None, "reading_stopped_after_R-d1.0": True}
    histogram = _load_histograms(inputs.run, records["c0"]["result"]["product"])["step"]
    counts, predictions = histogram["N"], histogram["P"]
    observed = group_step(counts, predictions, "PB")
    by_playlist = observed_steps(counts, predictions)
    results: Json = {}
    for label, variant in (
        ("unswapped_background", 1),
        ("integral_scaled_background", 2),
    ):
        swapped = group_step(counts, predictions, "PB", variant)
        with np.errstate(divide="ignore", invalid="ignore"):
            fraction = 1 - swapped / observed
        predicted = predicted_steps(predictions, variant)
        pb = [PLAYLISTS.index(playlist) for playlist in GROUPS["PB"]]
        predicted_pb = (
            _double_step(
                predictions[:, variant, pb].sum(axis=1),
                predictions[:, 0, pb].sum(axis=1),
            )
            - 1
        )
        residual = by_playlist - predicted
        uncertainty = _sigma(residual)
        require(
            bool(np.all(np.isfinite(residual))) and bool(np.all(uncertainty > 0)),
            "D2_VARIANCE",
            "undefined predicted-step size test",
        )
        statistic = float(np.sum((residual[0] / uncertainty) ** 2))
        probability = float(chi2.sf(statistic, 12))
        outcome = classify_flux_swap(
            observed=float(observed[0]),
            sigma_observed=float(_sigma(observed)),
            fraction=float(fraction[0]),
            sigma_fraction=float(_sigma(fraction)),
            predicted=float(predicted_pb[0]),
            sigma_predicted=float(_sigma(predicted_pb)),
            prediction_p=probability,
        )
        results[label] = {
            "outcome": outcome,
            "s_obs": observed[0],
            "sigma_obs": _sigma(observed),
            "s_swap": swapped[0],
            "sigma_swap": _sigma(swapped),
            "f": fraction[0],
            "sigma_f": _sigma(fraction),
            "s_pred_PB": predicted_pb[0],
            "sigma_pred_PB": _sigma(predicted_pb),
            "chi2_pred": statistic,
            "ndf": 12,
            "p_pred": probability,
            "playlist_s_obs": by_playlist[0],
            "playlist_s_pred": predicted[0],
            "sigma_residual": uncertainty,
        }
    mirror_counts = predictions[:, 0].copy()
    pa = [PLAYLISTS.index(playlist) for playlist in GROUPS["PA"]]
    mirror_counts[:, pa] = predictions[:, 3, pa]
    pb = [PLAYLISTS.index(playlist) for playlist in GROUPS["PB"]]
    mirror = (
        _double_step(counts[:, pb].sum(axis=1), mirror_counts[:, pb].sum(axis=1))
        / _double_step(counts[:, pa].sum(axis=1), mirror_counts[:, pa].sum(axis=1))
        - 1
    )
    pc = group_step(counts, predictions, "PC", 1)
    return {
        "outcome": bracket_outcome(
            results["unswapped_background"]["outcome"],
            results["integral_scaled_background"]["outcome"],
        ),
        "brackets": results,
        "descriptive_only": {
            "PA_to_1M_step_PB_vs_PA": mirror[0],
            "PA_to_1M_sigma": _sigma(mirror),
            "PC_to_1D_step": pc[0],
            "PC_to_1D_sigma": _sigma(pc),
        },
        "cause_is_not_known_unchanged": True,
    }


def run_stage(
    config_path: Path,
    config_sha: str,
    run: Path,
    step: str,
    *,
    prediction: Path | None = None,
    prediction_sha: str | None = None,
    dry_run: bool = False,
    priced_wall_seconds: int | None = None,
    measured_seconds_per_draw: float | None = None,
    timing_record: Path | None = None,
    timing_record_sha256: str | None = None,
    argv: Sequence[str] = (),
) -> Json:
    """Execute one bound step, retaining its input identities and predecessor digest.

    Data-bearing steps require a committed pre-data prediction. No step is a
    publication adoption or permission for a subsequent cluster run.
    """
    require_output_root(run)
    require(step in STEPS, "STEP_NAME", f"unknown step {step}")
    require(
        not (run / f"{step}.json").exists(),
        "OUTPUT_EXISTS",
        f"step {step} already recorded",
    )
    require(
        not dry_run or step in {"pins", "p0"},
        "DRY_RUN_SCOPE",
        "dry runs are limited to pins and p0",
    )
    inputs = Inputs(
        config_path,
        config_sha,
        run,
        priced_wall_seconds=priced_wall_seconds,
        measured_seconds_per_draw=measured_seconds_per_draw,
        timing_record=timing_record,
        timing_record_sha256=timing_record_sha256,
    )
    try:
        if prediction is not None and prediction_sha is not None:
            inputs.prediction = prediction, prediction_sha
        records = require_predecessors(inputs, step, dry_run=dry_run)
        inputs.plan_step(
            step,
            records["p0"]["result"]["runtime_estimate"] if "p0" in records else None,
        )
        if step in {"d2-predict", "c0"}:
            assert inputs.step_estimate is not None
            require(
                inputs.step_estimate["planned_seconds"] <= inputs.wall_seconds,
                "PRICE_REVIEW",
                "step estimate exceeds its wall budget; director pricing required before bootstrap",
            )
        inputs.load_pins()
        previous = STEPS[STEPS.index(step) - 1] if step != "pins" else None
        result: Json
        if step == "pins":
            result = {
                "files": {
                    name: {
                        "sha256": expected,
                        "staged": str(inputs.copy(source, expected)),
                    }
                    for name, (source, expected) in inputs.pins.items()
                },
                "n_files": len(inputs.pins),
                "known_siblings_stat_only": inputs.known_siblings,
            }
        elif step == "p0":
            result = p0(inputs)
            result["runtime_estimate"] = runtime_estimate(inputs)
        elif step == "d2-predict":
            histograms, controls = aggregate(
                inputs, records["p0"]["result"], None, data=False
            )
            checked = prediction_controls(controls)
            predicted = predicted_steps(histograms["step"]["P"])
            groups = {}
            for group, members in GROUPS.items():
                indices = [PLAYLISTS.index(playlist) for playlist in members]
                group_prediction = (
                    _double_step(
                        histograms["step"]["P"][:, 1, indices].sum(axis=1),
                        histograms["step"]["P"][:, 0, indices].sum(axis=1),
                    )
                    - 1
                )
                groups[group] = {
                    "s_pred": group_prediction[0],
                    "sigma": _sigma(group_prediction),
                }
            result = {
                "controls": checked,
                "playlist_s_pred": predicted[0],
                "playlist_sigma_pred": _sigma(predicted),
                "groups": groups,
                "product": _save_histograms(inputs.run, step, histograms),
                "simulation_only": True,
            }
        elif step == "step0":
            result = step0(inputs)
        elif step == "c0":
            result = _c0(inputs, records)
        elif step == "d1":
            result = _d1(inputs, records)
        else:
            result = _d2(inputs, records)
        inputs.check_wall_clock()
        record = {
            "schema": "fd-rpd-reco-step/1",
            "step": step,
            "status": "PASS",
            "dry_run": dry_run,
            "run_class": inputs.config.get("run_class", "diagnostic"),
            **inputs.execution(),
            "code_sha256": digest(Path(__file__)),
            "config_sha256": config_sha,
            "input_sha256": inputs.hashes,
            "keys_read": inputs.keys_read,
            "predecessor_sha256": (
                digest(inputs.run / f"{previous}.json") if previous else None
            ),
            "argv": list(argv),
            "result": result,
            "does_not_license": [
                "which period or flux is correct",
                "correction or exclusion",
                "change to estimator or covariance",
                "validation or coverage",
                "removing the unknown-cause clause",
                "paper use without Joseph's decision",
            ],
        }
        write_json(inputs.run / f"{step}.json", record)
        return record
    except Refused as error:
        error.details = {**(error.details or {}), "execution": inputs.execution()}
        raise


def main(argv: Sequence[str] | None = None) -> int:
    """Run the local diagnostic CLI; stop explicitly when a guard refuses."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("step", choices=STEPS)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--config-sha256", required=True)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--prediction", type=Path)
    parser.add_argument("--prediction-sha256")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--priced-wall-seconds", type=int)
    parser.add_argument("--measured-seconds-per-draw", type=float)
    parser.add_argument("--timing-record", type=Path)
    parser.add_argument("--timing-record-sha256")
    arguments = parser.parse_args(argv)
    command = list(argv) if argv is not None else sys.argv[1:]
    try:
        require_output_root(arguments.run)
        wall_budget_seconds(
            arguments.priced_wall_seconds, arguments.measured_seconds_per_draw
        )
        for key in THREAD_KEYS:
            os.environ.setdefault(key, "1")
        require(
            all(os.environ[key] == "1" for key in THREAD_KEYS),
            "THREADS",
            "all numerical thread limits must be one",
        )
        current_nice = os.getpriority(os.PRIO_PROCESS, 0)
        if current_nice < 19:
            os.nice(19 - current_nice)
        require(
            os.getpriority(os.PRIO_PROCESS, 0) == 19, "NICE", "nice level must be 19"
        )
        record = run_stage(
            arguments.config,
            arguments.config_sha256,
            arguments.run,
            arguments.step,
            prediction=arguments.prediction,
            prediction_sha=arguments.prediction_sha256,
            dry_run=arguments.dry_run,
            priced_wall_seconds=arguments.priced_wall_seconds,
            measured_seconds_per_draw=arguments.measured_seconds_per_draw,
            timing_record=arguments.timing_record,
            timing_record_sha256=arguments.timing_record_sha256,
            argv=command,
        )
    except (Refused, OSError, ValueError, KeyError, ImportError) as error:
        guard = error.guard if isinstance(error, Refused) else type(error).__name__
        try:
            require_output_root(arguments.run)
        except (Refused, OSError, ValueError) as output_error:
            print(f"STOP OUTPUT_LOCATION: {output_error}", file=sys.stderr)
            return 4
        arguments.run.mkdir(parents=True, exist_ok=True)
        stop = arguments.run / f"{arguments.step}.STOP.json"
        if not stop.exists():
            details = error.details if isinstance(error, Refused) else None
            write_json(
                stop,
                {
                    "schema": "fd-rpd-reco-stop/1",
                    "step": arguments.step,
                    "status": "STOP",
                    "guard": guard,
                    "message": str(error),
                    "argv": command,
                    "code_sha256": digest(Path(__file__)),
                    "config_sha256": arguments.config_sha256,
                    **execution_fields(
                        arguments.priced_wall_seconds,
                        arguments.measured_seconds_per_draw,
                        timing_source=(
                            None
                            if arguments.timing_record is None
                            else {
                                "path": str(arguments.timing_record),
                                "sha256": arguments.timing_record_sha256,
                            }
                        ),
                    ),
                    **(details.get("execution", {}) if details else {}),
                    "input_sha256": details.get("input_sha256", {}) if details else {},
                    "details": details,
                    "readings": None,
                },
            )
        print(f"STOP {guard}: {error}", file=sys.stderr)
        return 4
    print(
        json.dumps(
            {
                "step": record["step"],
                "status": record["status"],
                "dry_run": record["dry_run"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

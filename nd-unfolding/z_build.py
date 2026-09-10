#!/usr/bin/env python3
"""Build and read back both Z variants from digest-bound local inputs.

This entry point checks construction, not scientific adoption. See Z_BUILD.md
for the manifest contract and the unresolved real-input requirements.
"""

from __future__ import annotations

import argparse
from contextlib import ExitStack
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, NoReturn, cast
from zipfile import BadZipFile

import numpy as np

import p4_lib as p4
import z_assembly as assembly
import z_contract as contract
import z_receipt as receipt
import z_statistics as statistics
import z_validator as validator
from unified_throw_cov import _atomic_savez

JSONDict = dict[str, Any]

SCHEMA_VERSION = 1
SUPPORT_PREFIX = "hCov_universe5d_"
TOTAL_KEY = "hCov_combined5d_total_uthrow"
REPO = Path(__file__).resolve().parents[1]
REQUIREMENTS = {
    "parent_lineage": "Bind G, its actual combined_source, and its production-CV input; "
    "independently establish that the declared files are those inputs.",
    "component_footing": "Verify each component's estimator, normalization, full-grid mask, "
    "row order, background treatment and provenance on the same fixed central value.",
    "cause1": "Supply the endpoint-interpolation counterfactual and its scope and magnitude.",
    "cause2": "Supply the F7 operands, k and its source for both centering variants.",
    "cause3": "Predeclare K, both-leg estimator/draw seeds, the complete binding leg set, "
    "and approved aggregate, per-bin/coverage and correlation-use criteria; build all members.",
    "cause4": "Supply the scalar jitter add-back print value, seed and both operand digests.",
    "cause5": "Independently trace all consumed inputs for PET provenance and apply the "
    "artifact-specific ruling; construction alone does not dispose of this cause.",
    "cause6": "Supply the statistical projection operator and both coverage censuses.",
    "cause7": "Verify the five active bands, ten endpoint identities, migration censuses "
    "and declared policies, the support-scope check and the measured counterfactual.",
    "null": "Persist both internal same-run fixed-seed CVs and predicate at throw creation; "
    "approve B, S, B <= S and epsilon in [B, S] before production.",
    "code_and_run": "Pin the complete producing code, measured executable imports and run/step; "
    "independently verify the real-input construction and environment.",
    "endpoint_completeness": "Resolve the committed ROOT inspection's endpoint "
    "globalCompleteness readings above one without normalization or an invented criterion.",
    "runtime": "Verify the real PyROOT environment and assess production-scale memory/runtime "
    "for dense component sums, both variants and exact eigenvalue checks.",
    "authorization": "Obtain the named production/resource authorization and independent "
    "scientific decisions before production, adoption, projection or publication use.",
}


def _require_keys(value: Any, required: set[str], where: str) -> JSONDict:
    contract.require(isinstance(value, dict), f"{where}: expected an object")
    contract.require(
        set(value) == required, f"{where}: expected keys {sorted(required)}"
    )
    return cast(JSONDict, value)


def _text(value: Any, where: str) -> str:
    contract.require(
        isinstance(value, str) and bool(value.strip()), f"{where}: blank text"
    )
    return cast(str, value)


def _digest(value: Any, where: str) -> str:
    contract.require(
        isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value),
        f"{where}: expected a full lowercase SHA-256",
    )
    return cast(str, value)


def _unique_pairs(pairs: list[tuple[str, Any]]) -> JSONDict:
    result = {}
    for key, value in pairs:
        contract.require(key not in result, f"JSON: duplicate key {key!r}")
        result[key] = value
    return result


def _decode_json(text: str) -> JSONDict:
    def reject_constant(value: str) -> None:
        raise contract.ZContractError(f"JSON: non-finite constant {value}")

    decoded = json.loads(
        text,
        object_pairs_hook=_unique_pairs,
        parse_constant=reject_constant,
    )
    contract.require(isinstance(decoded, dict), "JSON: expected an object")
    return cast(JSONDict, decoded)


def _read_json(path: Path) -> JSONDict:
    return _decode_json(path.read_text())


class Source:
    """Read numeric NPZ or ROOT objects while binding the file's bytes.

    Parameters
    ----------
    declaration : JSONDict
        Explicit path, format (npz, root or opaque), and SHA-256.
    base : Path
        Directory relative input paths are resolved against.
    """

    def __init__(self, declaration: JSONDict, base: Path) -> None:
        _require_keys(declaration, {"path", "format", "sha256"}, "source")
        self.path = (base / _text(declaration["path"], "source path")).resolve()
        self.format = declaration["format"]
        contract.require(
            self.format in ("npz", "root", "opaque"), "source: unknown format"
        )
        self.stamp = receipt.stamp_file(self.path)
        contract.require(
            self.stamp["sha256"] == _digest(declaration["sha256"], "source"),
            f"source digest mismatch: {self.path}",
        )
        self.store: Any = None
        self.reads: dict[str, JSONDict] = {}
        self._handles = ExitStack()

    def __enter__(self) -> Source:
        try:
            if self.format == "npz":
                handle = self._handles.enter_context(self.path.open("rb"))
                self.store = np.load(handle, allow_pickle=False)
                contract.require(
                    isinstance(self.store, np.lib.npyio.NpzFile), "source: expected NPZ"
                )
                self._handles.enter_context(self.store)
                contract.require(
                    len(self.store.files) == len(set(self.store.files)),
                    "source: duplicate archive keys",
                )
            elif self.format == "root":
                import ROOT

                self.store = ROOT.TFile.Open(str(self.path), "READ")
                if self.store:
                    self._handles.callback(self.store.Close)
                contract.require(
                    self.store and not self.store.IsZombie(), f"cannot open {self.path}"
                )
        except BaseException:
            self._handles.close()
            raise
        return self

    def __exit__(self, *args: Any) -> None:
        self._handles.close()

    def keys(self) -> set[str]:
        """Return the actual stored object inventory."""
        if self.format == "npz":
            return set(self.store.files)
        contract.require(
            self.format == "root", "opaque sources have no array inventory"
        )
        return {key.GetName() for key in self.store.GetListOfKeys()}

    def read(self, key: str, shape: tuple[int, ...] | None = None) -> np.ndarray:
        """Read a real finite array and record its content digest."""
        contract.require(key in self.keys(), f"source {self.path}: missing {key}")
        if self.format == "npz":
            values = np.asarray(self.store[key])
        else:
            hist = self.store.Get(key)
            contract.require(hist.InheritsFrom("TH1"), f"{key}: expected a histogram")
            dim = hist.GetDimension()
            contract.require(dim in (1, 2), f"{key}: expected TH1 or TH2")
            if dim == 1:
                values = np.array(
                    [hist.GetBinContent(i + 1) for i in range(hist.GetNbinsX())]
                )
            else:
                contract.require(hist.ClassName() == "TH2D", f"{key}: expected TH2D")
                nx, ny = hist.GetNbinsX(), hist.GetNbinsY()
                raw = np.frombuffer(
                    hist.GetArray(), dtype=np.float64, count=(nx + 2) * (ny + 2)
                )
                values = raw.reshape(ny + 2, nx + 2)[1:-1, 1:-1].T.copy()
            # Release the source histogram after copying instead of accumulating
            # every support-band matrix in the open TFile's object cache.
            import ROOT

            hist.SetDirectory(0)
            ROOT.SetOwnership(hist, True)
        contract.require(
            values.dtype.kind in "fiu", f"{key}: expected a real numeric array"
        )
        contract.require(
            values.ndim in (1, 2) and values.size > 0, f"{key}: malformed shape"
        )
        contract.require(np.all(np.isfinite(values)), f"{key}: non-finite values")
        if shape is not None:
            contract.require(
                values.shape == shape, f"{key}: shape {values.shape} != {shape}"
            )
        values = np.asarray(values, dtype=np.float64)
        self.reads[key] = {
            "sha256": receipt.sha256_array(values),
            "shape": list(values.shape),
        }
        return cast(np.ndarray, values)

    def diagonal(self, key: str, n: int) -> np.ndarray:
        """Read only a throw covariance's diagonal from ROOT; never use it as a budget block."""
        if self.format == "npz":
            values = np.diag(self.read(key, (n, n))).copy()
        else:
            contract.require(key in self.keys(), f"source {self.path}: missing {key}")
            hist = self.store.Get(key)
            contract.require(
                hist.InheritsFrom("TH2")
                and (hist.GetNbinsX(), hist.GetNbinsY()) == (n, n),
                f"{key}: expected a {n} by {n} histogram",
            )
            values = np.array([hist.GetBinContent(i + 1, i + 1) for i in range(n)])
            import ROOT

            hist.SetDirectory(0)
            ROOT.SetOwnership(hist, True)
        contract.require(np.all(np.isfinite(values)), f"{key}: non-finite diagonal")
        self.reads[key + ":diagonal"] = {
            "sha256": receipt.sha256_array(values),
            "shape": [n],
        }
        return cast(np.ndarray, values)

    def verify_unchanged(self) -> None:
        """Refuse replacement or modification during the build."""
        current = receipt.stamp_file(self.path)
        contract.require(
            all(
                current[k] == self.stamp[k]
                for k in ("sha256", "size", "inode", "device", "mtime_ns")
            ),
            f"source changed during build: {self.path}",
        )


def _code_identity(revision: str) -> JSONDict:
    head = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=REPO, text=True
    ).strip()
    contract.require(
        revision == head, "producing_revision must equal the executing checkout's HEAD"
    )
    modules = {Path(__file__).resolve()}
    for module in tuple(sys.modules.values()):
        path = getattr(module, "__file__", None)
        if path and Path(path).resolve().is_relative_to(REPO):
            modules.add(Path(path).resolve())
    digests = {
        str(path.relative_to(REPO)): receipt.sha256_file(path)
        for path in sorted(modules)
    }
    dirty = []
    for path, digest in digests.items():
        blob = subprocess.run(
            ["git", "show", f"{head}:{path}"], cwd=REPO, capture_output=True
        )
        if blob.returncode or hashlib.sha256(blob.stdout).hexdigest() != digest:
            dirty.append(path)
    return {
        "revision": head,
        "import_closure_digests": digests,
        "worktree_files_differing_from_revision": dirty,
    }


def _sum_bands(
    source: Source, names: tuple[str, ...], prefix: str, n: int
) -> np.ndarray:
    total = np.zeros((n, n))
    for band in names:
        total += source.read(prefix + band, (n, n))
    return total


def _write_product(
    path: Path, arrays: dict[str, np.ndarray], metadata: JSONDict
) -> None:
    if path.suffix == ".npz":
        _atomic_savez(
            str(path), **arrays, metadata_json=np.asarray(json.dumps(metadata))
        )
        return
    import ROOT
    from adopt_unified_5d import _write_th2

    output = ROOT.TFile.Open(str(path), "RECREATE")
    contract.require(output and not output.IsZombie(), f"cannot create {path}")
    try:
        output.cd()
        for key, values in arrays.items():
            if values.ndim == 2:
                hist = _write_th2(key, key, values)
            else:
                hist = ROOT.TH1D(key, key, values.size, 0, values.size)
                for index, value in enumerate(values):
                    hist.SetBinContent(index + 1, float(value))
            contract.require(hist.Write() > 0, f"failed to write {key}")
        contract.require(
            ROOT.TObjString(json.dumps(metadata)).Write("metadata_json") > 0,
            "failed to write product metadata",
        )
    finally:
        output.Close()


def _product_metadata(source: Source) -> JSONDict:
    contract.require("metadata_json" in source.keys(), "product: missing metadata")
    if source.format == "npz":
        raw = source.store["metadata_json"]
        contract.require(
            raw.shape == () and raw.dtype.kind == "U", "product: malformed metadata"
        )
        return _decode_json(str(raw.item()))
    obj = source.store.Get("metadata_json")
    contract.require(
        obj.InheritsFrom("TObjString"), "product: expected TObjString metadata"
    )
    return _decode_json(str(obj.GetString().Data()))


def _verify_products(
    paths: dict[str, Path],
    expected: JSONDict,
    operands: JSONDict,
    parts: JSONDict,
    bands: JSONDict,
    metadata: JSONDict,
) -> tuple[JSONDict, JSONDict]:
    recorded_g, closures, stamps = {}, {}, {}
    for variant in assembly.CENTERING_VARIANTS:
        path = paths[variant]
        stamp = receipt.stamp_file(path)
        with Source(
            {"path": str(path), "sha256": stamp["sha256"], "format": path.suffix[1:]},
            path.parent,
        ) as source:
            contract.require(
                _product_metadata(source) == metadata[variant],
                "product: metadata differs from this build",
            )
            arrays = {
                key: source.read(key, values.shape)
                for key, values in expected[variant].items()
            }
            for key in ("hXSecND_flat", "hSupportMask", "hRowIndex5D", "hPinnedMask"):
                contract.require(
                    np.array_equal(arrays[key], expected[variant][key]),
                    f"product: {key} differs from declared footing",
                )
            recorded_g[variant] = arrays["hInflation_g"]
            closures[variant] = assembly.run_inflation_gates(
                C_Z=arrays[TOTAL_KEY],
                g=recorded_g[variant],
                pinned_mask=arrays["hPinnedMask"].astype(bool),
                v_uni=operands[f"v_uni_{variant}"],
                v_blk=operands["v_blk"],
                **parts,
                **bands,
            )
            source.verify_unchanged()
        stamps[variant] = stamp
    pair = assembly.run_pair_gates(g_recorded=recorded_g, **operands["raw"])
    return {variant: {**closures[variant], **pair} for variant in closures}, stamps


def build_z(
    manifest_path: Path,
    *,
    out_cv: Path,
    out_mean: Path,
    receipt_cv: Path,
    receipt_mean: Path,
    out_null: Path,
) -> JSONDict:
    """Construct both variants, verify closed artifacts, and write receipts last.

    Parameters
    ----------
    manifest_path : Path
        Versioned input declaration documented in Z_BUILD.md.
    out_cv, out_mean : Path
        Distinct new .npz or .root product paths.
    receipt_cv, receipt_mean : Path
        Distinct new JSON receipt paths.
    out_null : Path
        New .npz path for the versioned null-operand copy.

    Returns
    -------
    dict
        Product/receipt identities and an explicitly non-passing science status.

    Raises
    ------
    ZContractError
        A declaration, input, construction gate or closed-file check fails.
    """
    reserved: list[Path] = []
    try:
        manifest_path = Path(manifest_path).resolve()
        manifest_stamp = receipt.stamp_file(manifest_path)
        manifest = _read_json(manifest_path)
        _require_keys(
            manifest,
            {
                "schema_version",
                "input_kind",
                "run",
                "producing_revision",
                "sources",
                "stat_key",
                "ml_key",
                "footing",
            },
            "manifest",
        )
        contract.require(
            type(manifest["schema_version"]) is int
            and manifest["schema_version"] == SCHEMA_VERSION,
            "unsupported manifest schema",
        )
        contract.require(
            manifest["input_kind"] in ("synthetic", "real"), "unknown input kind"
        )
        run = _require_keys(manifest["run"], {"id", "step"}, "run")
        for key, value in run.items():
            _text(value, f"run {key}")
        _text(manifest["stat_key"], "stat_key")
        _text(manifest["ml_key"], "ml_key")
        for key in (manifest["stat_key"], manifest["ml_key"]):
            contract.require(
                key not in ("C_unified", "C_seed"), f"{key} cannot be a budget block"
            )
        sources_decl = _require_keys(
            manifest["sources"],
            {"parent", "central", "support", "active", "stat", "ml", "throw", "null"},
            "sources",
        )
        footing = _require_keys(
            manifest["footing"], {"mask_sha256", "row_order_sha256"}, "footing"
        )
        code = _code_identity(manifest["producing_revision"])
        paths = {"cv": Path(out_cv).resolve(), "mean": Path(out_mean).resolve()}
        receipts = {
            "cv": Path(receipt_cv).resolve(),
            "mean": Path(receipt_mean).resolve(),
        }
        out_null = Path(out_null).resolve()
        destinations = [*paths.values(), *receipts.values(), out_null]
        contract.require(
            len(set(destinations)) == len(destinations), "output paths must be distinct"
        )
        contract.require(
            all(p.suffix in (".npz", ".root") for p in paths.values()),
            "products must be .npz or .root",
        )
        contract.require(out_null.suffix == ".npz", "null output must be .npz")
        contract.require(
            all(p.suffix == ".json" for p in receipts.values()), "receipts must be JSON"
        )

        with ExitStack() as stack:
            sources = {
                role: stack.enter_context(Source(decl, manifest_path.parent))
                for role, decl in sources_decl.items()
            }
            input_paths = {source.path for source in sources.values()} | {manifest_path}
            contract.require(
                not input_paths.intersection(destinations), "output aliases an input"
            )
            contract.require(
                sources["null"].format == "npz", "null source must be versioned NPZ"
            )
            central = sources["central"].read("hXSecND_flat")
            mask = statistics.support_mask(central)
            rows: np.ndarray = np.flatnonzero(mask).astype(np.int64)
            n = rows.size
            contract.require(n > 0, "central: empty support")
            for key, values in (("mask_sha256", mask), ("row_order_sha256", rows)):
                contract.require(
                    receipt.sha256_array(values) == _digest(footing[key], key),
                    f"central: {key} mismatch",
                )
            x1, x2, null_mask = receipt.load_null_operands(sources["null"].path)
            contract.require(
                np.all(np.isfinite(x1)) and np.all(np.isfinite(x2)),
                "null: non-finite full-grid operands",
            )
            null_measurement = statistics.reconstruct_null_ratio(x1, x2, null_mask)
            contract.require(
                all(np.isfinite(value) for value in null_measurement.values()),
                "null: non-finite reconstructed measurement",
            )
            contract.require(
                np.array_equal(mask, null_mask), "null and production support differ"
            )
            null_outcome = validator.assess_null(null_measurement["r_null"])

            inventory = sorted(
                key[len(SUPPORT_PREFIX) :]
                for key in sources["support"].keys()
                if key.startswith(SUPPORT_PREFIX) and key != SUPPORT_PREFIX + "total"
            )
            residual = tuple(
                sorted(
                    set(inventory)
                    - set(contract.VERT_BANDS)
                    - set(contract.LATERAL_BANDS)
                )
            )
            partition = contract.check_band_partition(
                contract.VERT_BANDS, residual, contract.LATERAL_BANDS, inventory
            )
            bands = {
                "bands_vert": contract.VERT_BANDS,
                "bands_residual": residual,
                "bands_lateral": contract.LATERAL_BANDS,
                "band_inventory": inventory,
            }
            active = {
                band: sources["active"].read(p4.candidate_band_key(band), (n, n))
                for band in contract.LATERAL_BANDS
            }
            active_total = sources["active"].read(p4.CANDIDATE_ACTIVE_TOTAL_KEY, (n, n))
            active_residual = p4.check_component_sum(active_total, active)
            parts = {
                "cov_vert_sum": _sum_bands(
                    sources["support"], contract.VERT_BANDS, SUPPORT_PREFIX, n
                ),
                "cov_residual_sum": _sum_bands(
                    sources["support"], residual, SUPPORT_PREFIX, n
                ),
                "cov_lateral_sum": sum(active.values()),
                "cov_stat": sources["stat"].read(manifest["stat_key"], (n, n)),
                "cov_ml": sources["ml"].read(manifest["ml_key"], (n, n)),
            }
            blocksum = sum(parts.values())
            blocksum_psd = assembly.gate_symmetry_psd(blocksum)
            raw = {
                "diag_c_unified_mean": sources["throw"].diagonal("C_unified", n),
                "diag_c_blocksum": sources["throw"].diagonal("C_blocksum", n),
                "joint_mean_shift": sources["throw"].read("hJointMeanShift", (n,)),
            }
            operands = assembly.derive_variant_diagonals(**raw)
            operands["raw"] = raw
            expected, metadata = {}, {}
            for variant in assembly.CENTERING_VARIANTS:
                g, pinned = assembly.compute_g(
                    operands[f"v_uni_{variant}"], operands["v_blk"]
                )
                covariance = assembly.assemble(g, **parts)
                assembly.run_inflation_gates(
                    C_Z=covariance,
                    g=g,
                    pinned_mask=pinned,
                    v_uni=operands[f"v_uni_{variant}"],
                    v_blk=operands["v_blk"],
                    **parts,
                    **bands,
                )
                expected[variant] = {
                    TOTAL_KEY: covariance,
                    "hInflation_g": g,
                    "hPinnedMask": pinned.astype(float),
                    "hXSecND_flat": central,
                    "hSupportMask": mask.astype(float),
                    "hRowIndex5D": rows,
                }
                metadata[variant] = {
                    "schema_version": SCHEMA_VERSION,
                    "variant": variant,
                    "input_kind": manifest["input_kind"],
                    "run": run,
                    "scientific_acceptance": "NON-PASSING",
                    "adoptable": False,
                    "manifest_sha256": manifest_stamp["sha256"],
                    "code_identity": code,
                }
            assembly.run_pair_gates(
                g_recorded={v: expected[v]["hInflation_g"] for v in paths}, **raw
            )
            for path in destinations:
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open("xb"):
                    pass
                reserved.append(path)
            for variant in paths:
                _write_product(paths[variant], expected[variant], metadata[variant])
            closure, product_stamps = _verify_products(
                paths, expected, operands, parts, bands, metadata
            )
            null_copy = receipt.persist_null_operands(
                out_null, x1, x2, null_mask, code_identity=code
            )
            copied = receipt.load_null_operands(out_null)
            contract.require(
                all(np.array_equal(a, b) for a, b in zip(copied, (x1, x2, null_mask))),
                "null output changed its operands",
            )
            rebuilt_null = statistics.reconstruct_null_ratio(*copied)
            contract.require(
                rebuilt_null == null_measurement, "null output ratio changed"
            )
            for source in sources.values():
                source.verify_unchanged()
            contract.require(
                receipt.sha256_file(manifest_path) == manifest_stamp["sha256"],
                "manifest changed during build",
            )
            contract.require(
                _code_identity(manifest["producing_revision"]) == code,
                "executing code changed during build",
            )
            bindings = {
                role: {"stamp": source.stamp, "objects": source.reads}
                for role, source in sources.items()
            }
            science = {
                "assessable": False,
                "branch": None,
                "branch_label": None,
                "reject_conditions": ["4c"],
                "reason": "Scientific criteria and real-input evidence remain unresolved.",
            }
            null_block = {
                **rebuilt_null,
                "assessment": null_outcome,
                "persisted": null_copy,
                "source": sources["null"].stamp,
                #: REVIEWER FINDING F4, and BOTH reviewers reached it independently. This
                #: was `external_cv_crosscheck`, a bare verdict string. Two things were
                #: wrong with that and they are different. (1) SS1.5 requires a reported
                #: cross-check to carry the compared object's path, sha256 and key, and it
                #: carried none -- the identity lived in `notes.inputs`, far from the
                #: verdict a reader acts on. (2) The word "external" was false: the operand
                #: is this build's OWN declared `central` input, so with a synthetic
                #: manifest both sides can be synthetic and `ELEMENTWISE_EQUAL` is
                #: guaranteed by construction. A verdict that cannot fail is not evidence.
                #: It is renamed rather than repaired in place, because the honest field is
                #: a different field: this compares against a DECLARED input and SS1.5's
                #: external cross-check remains UNPERFORMED. Both facts travel with the
                #: verdict now instead of being recoverable from elsewhere in the receipt.
                "declared_cv_crosscheck": {
                    "verdict": (
                        "ELEMENTWISE_EQUAL" if np.array_equal(x1, central)
                        else "UNRESOLVED"
                    ),
                    "compared_against": {
                        "role": "central",
                        "key": "hXSecND_flat",
                        "path": sources["central"].stamp["path"],
                        "sha256": sources["central"].stamp["sha256"],
                    },
                    "independence": (
                        "NOT INDEPENDENT. The compared object is this build's own declared "
                        "`central` source, not an external production ROOT. Under "
                        "`input_kind: synthetic` both operands can be synthetic and agreement "
                        "is guaranteed by construction."
                    ),
                    "external_crosscheck_status": "UNPERFORMED",
                },
            }
            relative_null = np.abs(x2[null_mask] - x1[null_mask]) / np.abs(
                x1[null_mask]
            )
            contract.require(
                np.all(np.isfinite(relative_null)),
                "null: non-finite per-bin diagnostic",
            )
            worst_null = int(np.argmax(relative_null))
            null_block["per_bin_diagnostic"] = {
                "maximum_relative_difference": float(relative_null[worst_null]),
                "argmax_grid_index": int(rows[worst_null]),
                "grades_nothing": True,
            }
            receipts_written = {}
            for variant in paths:
                cov = expected[variant][TOTAL_KEY]
                inflation = {
                    **closure[variant],
                    "partition": partition,
                    "membership": {key: list(value) for key, value in bands.items()},
                    "raw_operands": {
                        key: receipt.sha256_array(value) for key, value in raw.items()
                    },
                    "sqrt_tr_before": float(np.sqrt(np.trace(blocksum))),
                    "sqrt_tr_after": float(np.sqrt(np.trace(cov))),
                }
                causes = {
                    str(i): {
                        "status": "UNRESOLVED",
                        "requirement": REQUIREMENTS[f"cause{i}"],
                    }
                    for i in range(1, 8)
                }
                causes["2"]["joint_mean_shift_sha256"] = receipt.sha256_array(
                    raw["joint_mean_shift"]
                )
                z_stamp = {
                    **product_stamps[variant],
                    "n_reported": int(n),
                    **footing,
                    "run": run,
                    "row_order_basis": "C-order flat indices reconstructed from declared production CV; NOT read_from_G",
                }
                built = receipt.build_receipt(
                    z_stamp=z_stamp,
                    variant=variant,
                    parent={
                        "parent_candidate": sources["parent"].stamp,
                        "combined_source": sources["support"].stamp,
                        "lineage_status": "UNVERIFIED",
                    },
                    code_identity=code,
                    inflation=inflation,
                    null_block=null_block,
                    cause_blocks=causes,
                    closure={
                        **closure[variant],
                        "active_total_eq_sum5": active_residual,
                        "blocksum_symmetry_psd": blocksum_psd,
                    },
                    outcome=science,
                    notes={
                        "input_kind": manifest["input_kind"],
                        "adoptable": False,
                        "construction_status": "CHECKED",
                        "inputs": bindings,
                        "manifest": manifest_stamp,
                        "paired_products": product_stamps,
                        "remaining_requirements": REQUIREMENTS,
                    },
                )
                receipts_written[variant] = receipt.write_receipt(
                    receipts[variant], built
                )
                contract.require(
                    _read_json(receipts[variant]) == built,
                    "receipt readback differs from this build",
                )
            return {
                "construction_status": "CHECKED",
                "scientific_acceptance": "NON-PASSING",
                "adoptable": False,
                "products": product_stamps,
                "receipts": receipts_written,
                "remaining_requirements": REQUIREMENTS,
            }
    except BaseException as exc:
        for path in reserved:
            path.unlink(missing_ok=True)
        if isinstance(
            exc,
            (
                OSError,
                EOFError,
                BadZipFile,
                ValueError,
                TypeError,
                KeyError,
                ImportError,
                p4.P4GateError,
            ),
        ):
            raise contract.ZContractError(f"Z build refused: {exc}") from exc
        raise


class _RefusingParser(argparse.ArgumentParser):
    """A usage error is a CONSTRUCTION FAILURE and must not share the completion code.

    REVIEWER FINDING F2. argparse exits 2 on a usage error, and 2 is also this command's
    "the build ran and its science is non-passing" code. Measured before the change: a
    single mistyped flag, and no arguments at all, both produced exit 2 having written no
    artifact. An automation reading `rc == 2` as "two products and two receipts exist,
    science non-passing" was therefore wrong on any launcher typo -- and unlike an exit-0
    hazard this one is reachable by accident rather than by malice.

    1 already means construction failure and a malformed invocation is one, so the codes
    do not need widening. The stderr envelope is emitted here too, so a caller parsing
    stderr JSON gets the same shape from a usage error as from a refused build.
    """

    def error(self, message: str) -> NoReturn:  # type: ignore[override]
        print(
            json.dumps({"construction_status": "FAILED", "reason": f"usage: {message}"}),
            file=sys.stderr,
        )
        raise SystemExit(1)


def main(argv: list[str] | None = None) -> int:
    """Run a local build.

    EXIT CODES, and 2 does not mean success. 2 = the build RAN TO COMPLETION and its
    science is NON-PASSING, which is the only outcome this command can produce; two
    products, two receipts and one null slab exist. 1 = construction failed or the
    invocation was malformed, with a `{"construction_status": "FAILED"}` envelope on
    stderr. 0 is reachable only from `--help`, which writes nothing.

    A CALLER MUST NOT TREAT 2 AS PROOF THE ARTIFACTS EXIST WITHOUT ALSO CHECKING THEM.
    An uncaught non-`ZContractError` still exits 1, but through the interpreter's own
    traceback rather than the envelope, so stderr-JSON parsing is not total.
    """
    parser = _RefusingParser(description=__doc__)
    for name in (
        "manifest",
        "out-cv",
        "out-mean",
        "receipt-cv",
        "receipt-mean",
        "out-null",
    ):
        parser.add_argument(f"--{name}", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = build_z(
            args.manifest,
            out_cv=args.out_cv,
            out_mean=args.out_mean,
            receipt_cv=args.receipt_cv,
            receipt_mean=args.receipt_mean,
            out_null=args.out_null,
        )
    except contract.ZContractError as exc:
        print(
            json.dumps({"construction_status": "FAILED", "reason": str(exc)}),
            file=sys.stderr,
        )
        return 1
    print(json.dumps(result, indent=2))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

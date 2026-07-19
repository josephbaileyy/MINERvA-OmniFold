#!/usr/bin/env python3
"""Independent, fail-closed validation of the G2 MEFHC full-schema NPZ receipt."""

from __future__ import annotations

import argparse
import datetime as dt
import gc
import hashlib
import json
import os
from pathlib import Path
import tempfile
import zipfile

import numpy as np

import fullevent_dump_contract as contract
import fullevent_fps_dataloader as loader


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(16 << 20), b""):
            h.update(block)
    return h.hexdigest()


def npy_header(archive: zipfile.ZipFile, key: str) -> dict:
    with archive.open(key + ".npy") as stream:
        version = np.lib.format.read_magic(stream)
        shape, fortran, dtype = np.lib.format._read_array_header(stream, version)
    return {"shape": list(shape), "dtype": str(dtype), "fortran_order": bool(fortran)}


def scalar(npz: np.lib.npyio.NpzFile, key: str):
    return np.asarray(npz[key]).item()


def in_domain(values: np.ndarray) -> np.ndarray:
    return (np.isfinite(values[:, 0]) & np.isfinite(values[:, 1])
            & (values[:, 0] >= 0.0) & (values[:, 0] <= 30.0)
            & (values[:, 1] >= 0.0) & (values[:, 1] <= 120.0))


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as stream:
            json.dump(value, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--npz", required=True, type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    receipt_bytes = args.receipt.read_bytes()
    receipt = json.loads(receipt_bytes)
    failures: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    require(receipt.get("status") == "PASS", "producer receipt status is not PASS")
    require(receipt.get("receipt_schema") == "g2-mefhc-fullschema-npz-v1",
            "wrong producer receipt schema")
    require(receipt.get("slurm_job_id") == "56120687", "wrong Slurm job binding")
    require(Path(receipt["npz"]["path"]).resolve() == args.npz.resolve(), "NPZ path mismatch")
    require(receipt["npz"]["size_bytes"] == args.npz.stat().st_size, "NPZ size mismatch")
    npz_sha = sha256(args.npz)
    require(receipt["npz"]["sha256"] == npz_sha, "NPZ SHA-256 mismatch")

    for label in ("dumper", "contract", "merge_receipt"):
        bound = receipt[label]
        require(sha256(Path(bound["path"])) == bound["sha256"], f"{label} SHA-256 mismatch")
    merge = json.loads(Path(receipt["merge_receipt"]["path"]).read_text())
    require(merge.get("status") == "PASS", "merge receipt not PASS")
    require(merge["merged_root"]["path"] == receipt["source_root"]["path"],
            "source ROOT path is not the committed merge product")
    require(merge["merged_root"]["sha256"] == receipt["source_root"]["sha256"],
            "source ROOT hash is not the committed merge hash")
    require(merge["domain_validation"]["status"] == "PASS", "merge domain validation not PASS")
    require(not merge["domain_validation"]["non_superseded_failures"],
            "merge receipt has non-superseded domain failures")

    with zipfile.ZipFile(args.npz) as archive:
        keys = sorted(name[:-4] for name in archive.namelist() if name.endswith(".npy"))
        headers = {key: npy_header(archive, key) for key in keys}
    require(not sorted(set(contract.REQUIRED_KEYS) - set(keys)), "required NPZ members missing")
    require(headers == receipt["member_headers"], "member headers differ from producer receipt")

    evidence: dict = {}
    with np.load(args.npz, allow_pickle=False) as npz:
        markers = {key: scalar(npz, key) for key in contract.G2_SCHEMA}
        try:
            contract.assert_g2_schema(markers)
        except Exception as exc:
            failures.append(f"schema marker failure: {exc}")
        require(markers == receipt["schema_markers"], "schema markers differ from receipt")
        require(int(scalar(npz, "num_part")) == 12, "num_part is not 12")
        require(str(scalar(npz, "estimator_fingerprint")) == "pet-fullevent-fps-v1",
                "wrong estimator fingerprint")
        try:
            loader.assert_extended_fps_edges(npz["edges_0"], npz["edges_1"])
        except Exception as exc:
            failures.append(f"extended-edge failure: {exc}")
        data_pot = float(scalar(npz, "data_pot"))
        mc_pot = float(scalar(npz, "mc_pot"))
        pot_scale = float(scalar(npz, "pot_scale"))
        require(np.isfinite([data_pot, mc_pot, pot_scale]).all() and data_pot > 0 and mc_pot > 0,
                "invalid POT metadata")
        require(np.isclose(data_pot / mc_pot, pot_scale, rtol=1e-12, atol=0),
                "pot_scale != data_pot/mc_pot")

        pass_reco = npz["pass_reco"]
        pass_truth = npz["pass_truth"]
        reco = npz["reco_scalars"]
        truth = npz["truth_scalars"]
        require(np.all(pass_reco | pass_truth), "signal inventory contains row outside both domains")
        require(np.all(in_domain(reco[pass_reco])), "pass_reco row outside retained domain")
        require(np.all(in_domain(truth[pass_truth])), "pass_truth row outside retained domain")
        require(np.all(reco[~pass_reco] == -9999.0), "non-reco signal scalar is not sentinel guarded")
        evidence["signal"] = {
            "rows": int(pass_reco.size), "pass_reco": int(pass_reco.sum()),
            "pass_truth": int(pass_truth.sum()),
            "identity_sha256": loader.inventory_order_hash(npz["w_truth"], pass_truth),
        }
        require(evidence["signal"]["identity_sha256"] == str(scalar(npz, "sig_identity_hash")),
                "signal identity hash mismatch")
        del reco, truth, pass_reco, pass_truth
        gc.collect()

        measured = npz["measured_scalars"]
        require(np.all(in_domain(measured)), "data row outside retained domain")
        data_hash = loader.inventory_order_hash(npz["measured_pc"])
        require(data_hash == str(scalar(npz, "data_identity_hash")), "data identity hash mismatch")
        evidence["data"] = {"rows": int(measured.shape[0]), "identity_sha256": data_hash}
        del measured
        gc.collect()

        background = npz["bkg_reco_scalars"]
        weights = npz["w_bkg"]
        indices = npz["bkg_indices"]
        require(np.all(in_domain(background)), "background row outside retained domain")
        require(np.isfinite(weights).all(), "background weights are non-finite")
        require(np.array_equal(indices, np.arange(indices.size, dtype=indices.dtype)),
                "background indices are not canonical order")
        bkg_hash = loader.inventory_order_hash(weights, indices)
        require(bkg_hash == str(scalar(npz, "bkg_identity_hash")), "background identity mismatch")
        evidence["background"] = {
            "rows": int(weights.size), "identity_sha256": bkg_hash,
            "raw_weight_sum": float(weights.sum(dtype=np.float64)),
        }

    expected_rows = receipt["inventory_rows"]
    require({key: value["rows"] for key, value in evidence.items()} == expected_rows,
            "inventory row counts differ from receipt")
    result = {
        "schema_version": 1,
        "validation_schema": "g2-mefhc-fullschema-npz-independent-v1",
        "status": "PASS" if not failures else "FAIL",
        "validated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "npz": {"path": str(args.npz.resolve()), "size_bytes": args.npz.stat().st_size,
                "sha256": npz_sha},
        "producer_receipt": {"path": str(args.receipt.resolve()),
                             "sha256": hashlib.sha256(receipt_bytes).hexdigest()},
        "source_root": receipt["source_root"],
        "merge_receipt": receipt["merge_receipt"],
        "schema_markers": receipt["schema_markers"],
        "member_count": len(headers),
        "inventory_evidence": evidence,
        "retained_domain_gev": {"pt": [0.0, 30.0], "pparallel": [0.0, 120.0]},
        "failures": failures,
    }
    atomic_json(args.output, result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())

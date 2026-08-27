#!/usr/bin/env python3
"""Changed-retry-3 target: reuse the frozen weighted target and fit literal only.

Retry 2 established that the historical sklearn Stay-Positive target is not
bit-reproducible in a fresh process.  This wrapper therefore consumes the exact
hash-bound Gate-5 seed-50000 weighted target and uses the unchanged canonical
refiner only for the literal delete/duplicate representation.  The original
paired-target implementation remains byte-identical and supplies every other
construction and validation step.
"""

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from pet_v2_equivalence_root_remap import install as install_root_remap  # noqa: E402
from pet_v2_target_package_bypass_retry2 import install_target_dataloader  # noqa: E402


ORIGINAL = HERE / "materialize_pet_v2_equivalence_target.py"
ORIGINAL_SHA256 = "6ae2ee6eaec3c4fc247b54115a8427cfae8e211dbda179d7cc69f2359ddd7fb6"
WEIGHTED_SHA256 = "13d46574b8f8e904aee0d544b33ce0f4fcd3fd5a119b0a2fd64071c70c650c03"
WEIGHTED_SIZE = 18723004
RECEIPT_SHA256 = "ff081d44aad16971a2b812b493c78cbeef25254f497ec5533dec4698c7246fc4"
SIGNED_TARGET_HASH = "446a392e898b8b1816151a6d8f3b90d2144bce75af6540ec8d984ebba751b44a"
INPUT_SHA256 = "fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625"


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(16 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def assert_regular(path, expected_sha, expected_size=None):
    path = Path(path).resolve()
    if not path.is_file() or path.is_symlink():
        raise SystemExit(f"[pet-v2-retry3][FAIL] missing/non-regular/symlink supplier {path}")
    if expected_size is not None and path.stat().st_size != expected_size:
        raise SystemExit(f"[pet-v2-retry3][FAIL] supplier size drift {path}")
    observed = sha256_file(path)
    if observed != expected_sha:
        raise SystemExit(
            f"[pet-v2-retry3][FAIL] supplier hash {observed} != {expected_sha}: {path}"
        )
    return path


def load_original():
    assert_regular(ORIGINAL, ORIGINAL_SHA256)
    expected_head = os.environ.get("PETV2_EXPECTED_HEAD")
    observed_head = subprocess.check_output(
        ["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True
    ).strip()
    if not expected_head or observed_head != expected_head:
        raise SystemExit(
            f"[pet-v2-retry3][FAIL] checkout HEAD {observed_head} != {expected_head}"
        )
    spec = importlib.util.spec_from_file_location("pet_v2_retry3_original", ORIGINAL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_archive(target, receipt):
    target = assert_regular(target, WEIGHTED_SHA256, WEIGHTED_SIZE)
    receipt = assert_regular(receipt, RECEIPT_SHA256)
    payload = json.loads(receipt.read_text(encoding="utf-8"))
    checks = {
        "status": payload.get("status") == "PASS",
        "bootstrap_seed": payload.get("bootstrap_seed") == 50000,
        "input": payload.get("input_preflight", {}).get("sha256") == INPUT_SHA256,
        "signed_target_hash": (
            payload.get("runtime_target", {}).get("signed_target_hash") == SIGNED_TARGET_HASH
        ),
        "target_hash": (
            payload.get("step1_feed", {}).get("weights", {}).get("sha256")
            == WEIGHTED_SHA256
        ),
        "target_size": (
            payload.get("step1_feed", {}).get("weights", {}).get("size_bytes")
            == WEIGHTED_SIZE
        ),
    }
    failed = [key for key, value in checks.items() if not value]
    if failed:
        raise SystemExit(
            "[pet-v2-retry3][FAIL] archived target receipt mismatch: " + ", ".join(failed)
        )
    values = np.load(target, mmap_mode="r", allow_pickle=False)
    if values.shape != (4680719,) or values.dtype != np.float32:
        raise SystemExit("[pet-v2-retry3][FAIL] archived target shape/dtype drift")
    if not np.all(np.isfinite(values)) or np.any(values < 0):
        raise SystemExit("[pet-v2-retry3][FAIL] archived target is non-finite or negative")
    return target, receipt, values


def make_archive_then_literal(fe_module, archive, canonical_literal):
    """Return the exact two-call refiner used by the unchanged paired-target driver."""
    calls = {"count": 0}

    def refiner(feat, signed_w, **kwargs):
        calls["count"] += 1
        if calls["count"] == 1:
            observed = fe_module.inventory_order_hash(np.asarray(signed_w, float))
            if observed != SIGNED_TARGET_HASH:
                raise SystemExit(
                    f"[pet-v2-retry3][FAIL] signed inventory {observed} "
                    f"!= {SIGNED_TARGET_HASH}"
                )
            if len(signed_w) != len(archive):
                raise SystemExit("[pet-v2-retry3][FAIL] archived target row alignment drift")
            print(
                "[pet-v2-retry3] PASS archived weighted target and signed-inventory binding; "
                "skipping non-bit-reproducible weighted refit",
                file=sys.stderr,
                flush=True,
            )
            return np.asarray(archive, dtype=np.float64)
        if calls["count"] == 2:
            return canonical_literal(feat, signed_w, **kwargs)
        raise SystemExit("[pet-v2-retry3][FAIL] unexpected third refinement call")

    refiner.calls = calls
    return refiner


def main():
    install_target_dataloader()
    adapted = install_root_remap()
    original = load_original()
    if "--help" in sys.argv or "-h" in sys.argv:
        return original.main()

    target_env = os.environ.get("PETV2_EXISTING_WEIGHTED_TARGET")
    receipt_env = os.environ.get("PETV2_EXISTING_WEIGHTED_RECEIPT")
    if not target_env or not receipt_env:
        raise SystemExit("[pet-v2-retry3][FAIL] archived target/receipt operands are mandatory")
    target, receipt, archive = validate_archive(target_env, receipt_env)

    canonical_factory = original.fe.learned_stay_positive_refiner
    canonical_literal = canonical_factory()

    def archive_then_literal():
        return make_archive_then_literal(original.fe, archive, canonical_literal)

    original.fe.learned_stay_positive_refiner = archive_then_literal
    original_write_npy = original._write_npy
    original_write_json = original._write_json

    def write_npy(path, value, note):
        path = Path(path)
        if path.name != "PETV2_WEIGHTED_TARGET.npy":
            return original_write_npy(path, value, note)

        def writer(tmp):
            with open(target, "rb") as source, open(tmp, "wb") as destination:
                shutil.copyfileobj(source, destination, length=16 << 20)

        original.atomic_write(str(path), writer, suffix=".npy", overwrite=False, fsync=True)
        original.mark_complete(str(path), note="PET-v2 archived weighted seed-50000 target")

    def write_json(path, payload):
        if Path(path).name == "PETV2_TARGET_RECEIPT.json":
            prior_refinement = dict(payload.get("refinement") or {})
            payload["weighted"].update({
                "sum": float(np.asarray(archive).sum(dtype=np.float64)),
                "zeros": int(np.count_nonzero(np.asarray(archive) == 0.0)),
                "source_path": str(target),
                "source_receipt": str(receipt),
                "source_receipt_sha256": RECEIPT_SHA256,
                "construction": "byte-identical reuse of frozen Gate-5 seed-50000 target",
            })
            payload["refinement"] = {
                "weighted_reused": True,
                "weighted_refit_performed": False,
                "weighted_sha256": WEIGHTED_SHA256,
                "signed_target_hash_verified": SIGNED_TARGET_HASH,
                "literal_fit_performed": True,
                "literal_estimator": "GradientBoostingClassifier exact",
                "literal_random_state": original.REFINEMENT_SEED,
                "literal_raw_sha256": prior_refinement.get("literal_raw_sha256"),
                "note": (
                    "retry 2 measured that a fresh weighted GBDT fit is not byte-reproducible; "
                    "the frozen historical weighted target is consumed exactly while the "
                    "literal representation is fit independently"
                ),
            }
        return original_write_json(path, payload)

    # The base stores `captured` locally, so retain its already-computed literal hash from the
    # payload and replace only the inaccurate weighted-fit description after construction.
    original._write_npy = write_npy
    original._write_json = write_json
    try:
        result = original.main()
    finally:
        original.fe.learned_stay_positive_refiner = canonical_factory
    if not adapted.redirects:
        raise SystemExit("[pet-v2-retry3][FAIL] no canonical-root insertion was remapped")
    return result


if __name__ == "__main__":
    raise SystemExit(main())

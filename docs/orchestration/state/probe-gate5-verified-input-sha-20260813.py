"""Positive-control probe for train_fullevent_replica.py:105-112.

Read-only w.r.t. the repo: builds the SAME fixture the committed acceptance test builds
(test_gate5_replica_driver.py::target_receipt), in a scratch dir, and asks one question:

  can read_replica_target_receipt() be made to FAIL by substituting the source NPZ
  with a DIFFERENT file of the SAME SIZE?

If it cannot, the check the field `_verified_input_sha256` names does not exist.
Arm 2 (different size) is the control that proves the probe is wired up at all.
"""
import json
import sys
import tempfile
from pathlib import Path

import numpy as np

# docs/orchestration/state/<this file>  ->  repo root
REPO = Path(__file__).resolve().parents[3]
PET = REPO / "nd-unfolding/pet"
sys.path.insert(0, str(PET))

import fullevent_fps_dataloader as fe  # noqa: E402
import train_fullevent_nominal as nominal  # noqa: E402
import train_fullevent_replica as replica  # noqa: E402
from atomic_write import mark_complete  # noqa: E402


def build_fixture(tmp_path, seed=50000, index=0):
    """Byte-for-byte the committed test's fixture (test_gate5_replica_driver.py:22-64)."""
    source = tmp_path / "source.npz"
    source.write_bytes(b"immutable-source-fixture")
    target = tmp_path / "target.npy"
    with target.open("wb") as stream:
        np.save(stream, np.asarray([1.0, 2.0], dtype=np.float32), allow_pickle=False)
    mark_complete(str(target), note="probe")
    receipt_path = tmp_path / "target-receipt.json"
    data_factor, sig_factor, bkg_factor = fe.coherent_bootstrap_factors(3, 5, 2, seed)
    payload = {
        "status": "PASS",
        "replica_index": index,
        "bootstrap_seed": seed,
        "seed_policy": replica.SEED_POLICY,
        "runtime_target": {
            "target_mode": nominal.BKG_MODE,
            "bootstrap_seed": seed,
            "refinement_is_learned_production": True,
            "input_identity_hashes": {"sig": "s", "data": "d", "bkg": "b"},
        },
        "step1_feed": {"weights": {
            "path": str(target.resolve()),
            "sha256": replica.sha256_file(target),
            "size_bytes": target.stat().st_size,
        }},
        "input_preflight": {
            "path": str(source.resolve()),
            "sha256": replica.sha256_file(source),
            "size_bytes": source.stat().st_size,
        },
        "bootstrap": {
            "n_data_full": 3, "n_sig_full": 5, "n_bkg_full": 2,
            "data_factor_sha256": replica.hash_array(data_factor),
            "signal_factor_sha256": replica.hash_array(sig_factor),
            "background_factor_sha256": replica.hash_array(bkg_factor),
        },
    }
    receipt_path.write_text(json.dumps(payload))
    return source, target, receipt_path, payload


def call(target, receipt_path, source):
    # .resolve() everywhere: on macOS tempfile hands back /var/... while Path.resolve()
    # yields /private/var/..., and the receipt stores the resolved form. The committed
    # test passes the UNRESOLVED path, so on this platform every arm would die at the
    # path check before reaching the subject -- a vacuous pass. Caught by arm A0.
    return replica.read_replica_target_receipt(
        str(target.resolve()), str(receipt_path.resolve()), str(source.resolve()), 50000, 0)


def arm(label, mutate, expect):
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        source, target, receipt_path, payload = build_fixture(tmp)
        note = mutate(source, target, receipt_path) or ""
        try:
            rec = call(target, receipt_path, source)
            got = "PASSED"
            detail = (f"_verified_input_sha256={rec['_verified_input_sha256'][:16]}  "
                      f"actual file sha={replica.sha256_file(source)[:16]}  "
                      f"equal={rec['_verified_input_sha256'] == replica.sha256_file(source)}")
        except SystemExit as exc:
            got = "FAILED-CLOSED"
            detail = str(exc)
        verdict = "as expected" if got == expect else "*** UNEXPECTED ***"
        print(f"[{label}]\n  mutation : {note}\n  expected : {expect}\n  observed : "
              f"{got}   ({verdict})\n  detail   : {detail}\n")
        return got == expect


def m_none(s, t, r):
    return "none (baseline)"


def m_same_size(s, t, r):
    old = s.read_bytes()
    new = b"SUBSTITUTED-source-file!"          # 24 bytes, same as the fixture's 24
    assert len(new) == len(old), (len(new), len(old))
    s.write_bytes(new)
    return f"source replaced, SAME size ({len(new)} B), different content"


def m_diff_size(s, t, r):
    s.write_bytes(s.read_bytes() + b"tamper")
    return "source appended, size changes (control: proves the probe is wired up)"


def m_target_same_size(s, t, r):
    """The committed test tampers the TARGET by appending. This is the target's
    same-size arm, for symmetry: it must fail closed, because :99 hashes."""
    old = t.read_bytes()
    new = bytearray(old)
    new[-1] ^= 0xFF
    t.write_bytes(bytes(new))
    mark_complete(str(t), note="probe")
    return f"target flipped one bit, SAME size ({len(new)} B)"


ok = []
ok.append(arm("A0 baseline, nothing touched", m_none, "PASSED"))
ok.append(arm("A1 SOURCE substituted, same size", m_same_size, "FAILED-CLOSED"))
ok.append(arm("A2 SOURCE substituted, different size (control)", m_diff_size, "FAILED-CLOSED"))
ok.append(arm("A3 TARGET one bit flipped, same size (contrast)", m_target_same_size,
              "FAILED-CLOSED"))
print("probe arms behaving as the field name promises:",
      f"{sum(ok)}/{len(ok)}")

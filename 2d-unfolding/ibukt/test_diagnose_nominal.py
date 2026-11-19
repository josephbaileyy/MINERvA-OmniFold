"""Local checks for the read-only nominal edge diagnostic."""

import hashlib
import json
import os
from pathlib import Path

import numpy as np
import pytest

import diagnose_nominal as diagnose
import ibukt


def synthetic_bank():
    """A nominal sample with separate truth and reco endpoint effects."""
    return {
        "gen": np.array(
            [
                [0.03, 40.0],
                [0.03, 60.0],
                [0.03, 40.0],
                [4.5, 40.0],
                [0.03, np.nextafter(60.0, 0.0)],
                [0.03, 60.0],
            ]
        ),
        "reco": np.array(
            [
                [0.03, 40.0],
                [0.03, 50.0],
                [0.03, 60.0],
                [0.03, 40.0],
                [0.03, 50.0],
                [0.03, 40.0],
            ]
        ),
        "pt": np.ones(6, dtype=bool),
        "pr": np.array([True, True, True, True, True, False]),
        "wr": np.array([10.0, 3.0, 5.0, 2.0, 1.0, 99.0]),
        "selected": np.arange(205),
    }


def test_decomposition_pins_exact_boundaries_and_response_terms():
    result = diagnose.measure(synthetic_bank(), ibukt.configuration())
    last = result["selected_cells"][15]
    assert (last["ipt"], last["ipz"]) == (0, 15)
    assert (last["y_signed"], last["response_row_sum"]) == (16.0, 11.0)
    assert (last["y_signed_minus_response"], last["outside_truth_wr_sum"]) == (5.0, 5.0)
    assert last["outside_truth_count"] == 2
    assert last["roundoff"] == 0.0
    assert result["sample"]["reco_outside"] == 1
    assert result["refinement"]["y_refined_minus_y_signed"] is None
    truth_pz = result["truth_boundaries"]["pz"]
    assert (truth_pz["maximum"], truth_pz["maximum_count"]) == (60.0, 1)
    boundary = next(row for row in truth_pz["values"] if row["value"] == 60.0)
    assert boundary["by_bin"] == [[0, 16, 1, 3.0]]
    assert boundary["by_reported_reco_cell"] == [[15, 1, 3.0]]
    truth_pt = result["truth_boundaries"]["pt"]
    upper_pt = next(row for row in truth_pt["values"] if row["value"] == 4.5)
    assert upper_pt["by_bin"] == [[14, 15, 1, 2.0]]
    reco_pz = result["reco_boundaries"]["pz"]
    upper_pz = next(row for row in reco_pz["values"] if row["value"] == 60.0)
    assert upper_pz["by_bin"] == [[0, 16, 1, 5.0]]
    assert upper_pz["by_reported_reco_cell"] == []


def test_diagnostic_refuses_fakes():
    bank = synthetic_bank()
    bank["pt"][0] = False
    with pytest.raises(ValueError, match="unexpected signal fakes"):
        diagnose.measure(bank, ibukt.configuration())


def test_verified_input_refuses_wrong_hash_and_symlink(tmp_path, monkeypatch):
    monkeypatch.setattr(os, "O_NOATIME", getattr(os, "O_NOATIME", 0), raising=False)
    source = tmp_path.resolve() / "input"
    source.write_bytes(b"input")
    with pytest.raises(ValueError, match="digest differs"):
        with diagnose.verified_input(source, "0" * 64):
            pytest.fail("wrong input was accepted")
    link = source.with_name("link")
    link.symlink_to(source)
    with pytest.raises(ValueError, match="cannot follow symlinks"):
        with diagnose.verified_input(link, "0" * 64):
            pytest.fail("symlink was accepted")


def test_run_verifies_receipts_and_writes_only_to_fresh_scratch(tmp_path, monkeypatch):
    scratch = tmp_path.resolve() / "pscratch" / "user"
    campaign = scratch / diagnose.RUN_NAME
    bank = campaign / diagnose.BANK_PATH
    bank.parent.mkdir(parents=True)
    np.savez(bank, **synthetic_bank())
    config = campaign / "deploy/2d-unfolding/ibukt/config.json"
    config.parent.mkdir(parents=True)
    config.write_bytes(ibukt.CONFIG.read_bytes())
    bank_sha = hashlib.sha256(bank.read_bytes()).hexdigest()
    identity = campaign / diagnose.IDENTITY_PATH
    identity.write_text(
        json.dumps(
            dict(status="PASS", bank_sha256=bank_sha, config_sha256=diagnose.CONFIG_SHA)
        )
    )
    receipt = campaign / "prepare/PASS.json"
    receipt.write_text(
        json.dumps(
            dict(
                status="PASS",
                action="prepare",
                script_sha256=diagnose.CONNECT_SHA,
                bound_commit=diagnose.BOUND_COMMIT,
                run_root=str(campaign),
                artifacts={
                    diagnose.BANK_PATH: bank_sha,
                    diagnose.IDENTITY_PATH: hashlib.sha256(
                        identity.read_bytes()
                    ).hexdigest(),
                },
            )
        )
    )
    monkeypatch.setattr(
        diagnose, "PREPARE_SHA", hashlib.sha256(receipt.read_bytes()).hexdigest()
    )
    monkeypatch.setattr(diagnose, "SCRATCH_ROOT", scratch.parent)
    monkeypatch.setattr(os, "O_NOATIME", getattr(os, "O_NOATIME", 0), raising=False)
    monkeypatch.setattr(os, "umask", lambda mode: mode)
    monkeypatch.setenv("SCRATCH", str(scratch))
    monkeypatch.delenv("SLURM_JOB_ID", raising=False)
    script = Path(diagnose.__file__)
    pin = hashlib.sha256(script.read_bytes()).hexdigest()
    result = diagnose.run(pin)
    output = Path(result["report"])
    assert output.parent.parent == scratch
    assert output.parent.name.startswith("ibukt-nominal-diagnostic-")
    assert hashlib.sha256(output.read_bytes()).hexdigest() == result["sha256"]
    assert json.loads(output.read_bytes())["bank_sha256"] == bank_sha
    bank.write_bytes(b"tampered")
    with pytest.raises(ValueError, match="input digest differs"):
        diagnose.run(pin)
    assert len(list(scratch.glob("ibukt-nominal-diagnostic-*"))) == 1

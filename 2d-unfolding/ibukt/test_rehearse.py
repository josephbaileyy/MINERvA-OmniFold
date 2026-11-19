"""Local checks for rehearsal workspace confinement and evidence handling."""

import json
import os
import sys
import time

import pytest

import rehearse


@pytest.mark.parametrize("location", ["cfs", "outside", "symlink"])
def test_probe_refuses_before_creating_anything(tmp_path, monkeypatch, location):
    scratch = tmp_path / "pscratch"
    home = scratch / "user"
    parent = home / "ibukt-rehearsal-test"
    parent.mkdir(mode=0o700, parents=True)
    target = tmp_path / location
    target.mkdir()
    workspace = target
    if location == "symlink":
        workspace = parent / "paper-mask"
        workspace.symlink_to(target, target_is_directory=True)
    monkeypatch.setenv("SCRATCH", str(home))
    monkeypatch.setenv("IBUKT_REHEARSAL_ROOT", str(parent))
    monkeypatch.setattr(rehearse, "SCRATCH_ROOT", scratch)
    monkeypatch.setattr(
        rehearse,
        "run_probe",
        lambda *args: pytest.fail("invalid workspace reached the probe"),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "rehearse.py",
            "--probe",
            "paper-mask",
            "--workspace",
            str(workspace),
        ],
    )
    monkeypatch.chdir(workspace)
    with pytest.raises(SystemExit) as caught:
        rehearse.main()
    assert caught.value.code == 2
    assert not list(target.iterdir())


def test_probe_accepts_the_private_working_directory(tmp_path, monkeypatch):
    parent = tmp_path / "user" / "ibukt-rehearsal-test"
    parent.mkdir(mode=0o700, parents=True)
    workspace = parent / "score"
    workspace.mkdir(mode=0o700)
    (workspace / "stage").mkdir(mode=0o700)
    monkeypatch.setattr(rehearse, "SCRATCH_ROOT", tmp_path)
    monkeypatch.setenv("SCRATCH", str(parent.parent))
    monkeypatch.setenv("IBUKT_REHEARSAL_ROOT", str(parent))
    monkeypatch.chdir(workspace)
    for variable, suffix in (
        ("TMPDIR", "tmp"),
        ("MPLCONFIGDIR", "mpl"),
        ("XDG_CACHE_HOME", "cache"),
    ):
        directory = workspace / suffix
        directory.mkdir(mode=0o700)
        monkeypatch.setenv(variable, str(directory))
    assert rehearse.validated_workspace("score", workspace) == workspace


def test_inventory_preserves_rows_across_missing_and_malformed_evidence(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(os, "O_NOATIME", getattr(os, "O_NOATIME", 0), raising=False)
    inventory = tmp_path / "imports.jsonl"
    assert not rehearse.probe_result(inventory, 0)["complete"]
    passed = dict(outcome="ok", verdict="ok", launch_refusal=None, offending_argv=None)
    lines = [json.dumps(passed), json.dumps(passed)]
    inventory.write_text("\n".join(lines))
    assert rehearse.probe_result(inventory, 0)["complete"]
    refused = dict(
        outcome="refused:launch",
        verdict="refused",
        launch_refusal="blocked",
        offending_argv=["lscpu"],
    )
    inventory.write_text("\n".join([*lines, "{", json.dumps(refused)]))
    result = rehearse.probe_result(inventory, 3)
    assert result["outcomes"] == ["ok", "ok", "refused:launch"]
    assert result["refusals"][0]["argv"] == ["lscpu"]
    assert len(result["inventory_errors"]) == 1
    assert not result["complete"]


def test_probe_timeout_kills_descendants(tmp_path):
    program = (
        "import subprocess, sys; "
        "subprocess.Popen([sys.executable, '-c', "
        '\'import time; time.sleep(1); open("late", "w").close()\']); '
        "print('spawned', flush=True); "
        "import time; time.sleep(10)"
    )
    result = rehearse.run_child(
        [sys.executable, "-c", program], tmp_path, dict(os.environ), 0.5
    )
    assert result == 124
    assert "spawned" in (tmp_path / "probe.log").read_text()
    time.sleep(0.75)
    assert not (tmp_path / "late").exists()

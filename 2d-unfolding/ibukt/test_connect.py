"""Local checks of the IBUKT SSH launcher without a live connection."""

import base64
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shlex
import subprocess
import sys

import pytest

import connect


def test_envstage_activation_and_campaign(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Check the command passed to SSH and the corresponding approval packet."""
    pin = hashlib.sha256(Path(connect.__file__).read_bytes()).hexdigest()
    identity = {"action": "envstage", "script_sha256": pin}
    go = {**identity, "reference": "local test"}
    fence = {
        **identity,
        "notice_id": "test-notice",
        "ack_id": "test-ack",
        "time_unix": datetime.now(timezone.utc).timestamp(),
    }
    approval = tmp_path / "approval.json"
    approval.write_text(
        json.dumps(
            {
                **identity,
                "host": "example.invalid",
                "run_name": "ibukt-20261119-c",
                "director_go": go,
                "joseph_go": go,
                "fences": {"cov2d": fence, "tier3-design": fence},
            }
        )
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["connect.py", "envstage", "--approval", str(approval), "--sha256", pin],
    )
    syntax_check = subprocess.run
    calls = []

    def capture(argv: list[str], *, input: str, text: bool, check: bool) -> None:
        calls.append(argv)
        assert check and text
        assert argv[:5] == ["ssh", "-T", "-o", "BatchMode=yes", "example.invalid"]
        bash, flag, shell = shlex.split(argv[5])
        assert (bash, flag) == ("bash", "-c")
        syntax_check(["bash", "-n"], input=shell, text=True, check=True)
        assert shell.index("conda shell.bash hook") < shell.index("conda activate")
        assert shell.index(
            'conda activate "$HOME/.conda/envs/root_6_28"'
        ) < shell.index('exec "$HOME/.conda/envs/root_6_28/bin/python3"')
        _, _, _, _, bootstrap, name = shlex.split(shell[shell.index("exec ") :])
        compile(bootstrap, "<remote-bootstrap>", "exec")
        packet = json.loads(base64.b64decode(input))
        assert packet["action"] == "envstage"
        assert packet["approval"]["run_name"] == name == "ibukt-20261119-c"
        assert hashlib.sha256(base64.b64decode(packet["source"])).hexdigest() == pin

    monkeypatch.setattr(connect.subprocess, "run", capture)
    connect.main()
    assert len(calls) == 1

    record = json.loads(approval.read_text())
    record["run_name"] = "ibukt-20261118-b"
    approval.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="must name campaign ibukt-20261119-c"):
        connect.main()
    assert len(calls) == 1


def test_sacct_snapshot_reports_exact_digest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The original connection returns the saved snapshot even on fence refusal."""
    rows = "123|cov2d-test|RUNNING|10|1\n"
    monkeypatch.setattr(connect, "command", lambda _: rows)
    monkeypatch.setattr(
        connect, "digest", lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    )
    with pytest.raises(ValueError, match="protected allocation is unended"):
        connect.sacct(tmp_path, "before", report=True)
    result = json.loads(capsys.readouterr().out)
    saved = (tmp_path / result["path"]).read_bytes()
    assert saved == result["sacct"].encode() == rows.encode()
    assert result["sha256"] == hashlib.sha256(saved).hexdigest()


def test_rerun_budget_carries_exact_spend(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Count the stopped run's actual charge before reserving a new job."""
    from ibukt import budget

    screen = tmp_path / "screen"
    screen.mkdir()
    prepare = tmp_path / "prepare"
    prepare.mkdir()
    (prepare / "submit-intent.json").touch()
    (prepare / "submission.json").write_text(json.dumps({"job_id": "62222222"}))
    monkeypatch.setattr(connect, "read_json", lambda path: json.loads(path.read_text()))
    monkeypatch.setattr(
        connect,
        "command",
        lambda _argv, **_kw: json.dumps(
            budget(
                (screen / "accounting.sacct.txt").read_text(),
                json.loads((screen / "reservations.json").read_text()),
                5.35,
            )
        ),
    )
    rows = "62222222|ibukt-prepare|COMPLETED|660|1\n"
    for prior in ("", "61556304|ibukt-prepare|FAILED|639|1\n"):
        with pytest.raises(ValueError, match="previous prepare allocation"):
            connect.accounting(tmp_path, "screen", prior + rows)
    receipt = connect.accounting(
        tmp_path, "screen", connect.PRIOR_PREPARE_SACCT + "\n" + rows
    )
    assert json.loads(receipt.read_text())["spent_or_reserved"] == pytest.approx(
        (638 + 660) / 3600
    )

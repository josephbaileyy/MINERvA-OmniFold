"""Tests of tools/p0_checks.py (the P0 connect's in-place input check and fresh stat). Local files only.

usage: python3 -B -m pytest -q tests/test_p0_checks.py
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parents[1] / "tools"


def load():
    spec = importlib.util.spec_from_file_location("p0_checks_test", TOOLS / "p0_checks.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def files(tmp_path: Path) -> dict[str, Path]:
    out = {}
    for name, body in (("extract.json", b"{}\n"), ("factors-1A.npz", b"\x00" * 3000)):
        path = tmp_path / name
        path.write_bytes(body)
        out[name] = path
    return out


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_inputs_pass_diff_missing_and_no_flag(
    files: dict[str, Path], monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    checks = load()
    monkeypatch.setattr(checks.os, "O_NOATIME", 0, raising=False)
    expected = {str(p): digest(p) for p in files.values()}
    assert checks.check_inputs(expected) == 0
    assert "P0 INPUTS: PASS (2 files, 0 bad)" in capsys.readouterr().out
    one = str(files["extract.json"])
    assert checks.check_inputs({**expected, one: "0" * 64}) == 3
    out = capsys.readouterr().out
    assert "DIFF sha256" in out and "P0 INPUTS: STOP (2 files, 1 bad)" in out
    assert checks.check_inputs({**expected, str(files["extract.json"]) + ".gone": "0" * 64}) == 3
    assert "MISSING" in capsys.readouterr().out
    monkeypatch.delattr(checks.os, "O_NOATIME", raising=False)
    assert checks.check_inputs(expected) == 3
    assert "no O_NOATIME" in capsys.readouterr().out


def test_inputs_reads_with_the_noatime_flag(files: dict[str, Path], monkeypatch: pytest.MonkeyPatch) -> None:
    checks = load()
    monkeypatch.setattr(checks.os, "O_NOATIME", 0o1000000, raising=False)
    seen = []
    real_open = os.open

    def spy(path: str, flags: int, *args: object) -> int:
        seen.append(flags)
        return real_open(path, flags & ~0o1000000, *args)

    monkeypatch.setattr(checks.os, "open", spy)
    assert checks.check_inputs({str(p): digest(p) for p in files.values()}) == 0
    assert seen and all(flag & 0o1000000 for flag in seen)


def test_stat_pass_missing_bytes_and_inode(files: dict[str, Path], capsys: pytest.CaptureFixture[str]) -> None:
    checks = load()
    table = {str(p): {"bytes": p.stat().st_size, "inode": p.stat().st_ino} for p in files.values()}
    assert checks.check_stat(table) == 0
    out = capsys.readouterr().out
    assert "P0 STAT: PASS (2 files, 0 missing or different)" in out
    assert "earliest purge exposure " in out and out.count("same as S1") == 2
    one = str(files["factors-1A.npz"])
    for change in ({"bytes": table[one]["bytes"] + 1}, {"inode": table[one]["inode"] + 1}):
        assert checks.check_stat({**table, one: {**table[one], **change}}) == 3
        assert "DIFFERS from S1" in capsys.readouterr().out
    assert checks.check_stat({**table, one + ".gone": table[one]}) == 3
    assert "MISSING" in capsys.readouterr().out


def test_stat_purge_exposure_is_the_oldest_atime_plus_56_days(
    files: dict[str, Path], capsys: pytest.CaptureFixture[str]
) -> None:
    checks = load()
    old, new = files["extract.json"], files["factors-1A.npz"]
    os.utime(old, (1_790_000_000, 1_790_000_000))
    os.utime(new, (1_795_000_000, 1_795_000_000))
    table = {str(p): {"bytes": p.stat().st_size, "inode": p.stat().st_ino} for p in (old, new)}
    assert checks.check_stat(table) == 0
    out = capsys.readouterr().out
    assert f"earliest purge exposure {checks.utc(1_790_000_000 + 56 * 86400)} ({old}," in out


def test_main_reads_the_expected_file(tmp_path: Path, files: dict[str, Path], monkeypatch: pytest.MonkeyPatch) -> None:
    checks = load()
    monkeypatch.setattr(checks.os, "O_NOATIME", 0, raising=False)
    spec = tmp_path / "expected.json"
    spec.write_text(
        json.dumps(
            {
                "inputs": {str(p): digest(p) for p in files.values()},
                "stat": {str(p): {"bytes": p.stat().st_size, "inode": p.stat().st_ino} for p in files.values()},
            }
        )
    )
    assert checks.main(["p0_checks.py", "inputs", str(spec)]) == 0
    assert checks.main(["p0_checks.py", "stat", str(spec)]) == 0
    assert checks.main(["p0_checks.py", "bogus", str(spec)]) == 2


def test_the_committed_expected_values() -> None:
    expected = json.loads((TOOLS / "p0_expected.json").read_text())
    assert len(expected["inputs"]) == 14 and len(expected["stat"]) == 27
    assert sum("/dumps/lat_" in path for path in expected["stat"]) == 24
    assert sum("flux-gen2thin-pdg14-" in path for path in expected["stat"]) == 3
    root = "/pscratch/sd/j/josephrb/rpd-reco-flux3-20261123/run/"
    assert all(path.startswith(root) for path in expected["inputs"])
    # Every expected sha256 equals flux3's committed records (run-61861637): the two record files' own digests and
    # the 12 factor products' digests as the extract records them.
    records = TOOLS.parent.parent / "flux3-20261123" / "run-61861637" / "records" / "run"
    want = {root + name: digest(records / name) for name in ("flux-extract.json", "flux-custody.json")}
    for playlist, product in json.loads((records / "flux-extract.json").read_text())["factor_products"].items():
        assert product["path"] == f"{root}flux-factors-{playlist}.npz"
        want[product["path"]] = product["sha256"]
    assert expected["inputs"] == want

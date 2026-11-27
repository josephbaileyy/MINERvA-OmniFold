"""Tests of tools/d2s0_checks.py (e1) (P0's checks plus the stage mode for P0's two records). Local files only.

usage: python3 -I -B -m pytest -q -p no:cacheprovider tests/test_d2s0_checks.py
"""

from __future__ import annotations

import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parents[1] / "tools"


def load():
    spec = importlib.util.spec_from_file_location("d2s0_checks_test", TOOLS / "d2s0_checks.py")
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
    assert "INPUTS: PASS (2 files, 0 bad)" in capsys.readouterr().out
    one = str(files["extract.json"])
    assert checks.check_inputs({**expected, one: "0" * 64}) == 3
    out = capsys.readouterr().out
    assert "DIFF sha256" in out and "INPUTS: STOP (2 files, 1 bad)" in out
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
    assert "STAT: PASS (2 files, 0 missing or different)" in out
    assert "earliest purge exposure " in out and out.count("same as recorded") == 2
    one = str(files["factors-1A.npz"])
    for change in ({"bytes": table[one]["bytes"] + 1}, {"inode": table[one]["inode"] + 1}):
        assert checks.check_stat({**table, one: {**table[one], **change}}) == 3
        assert "DIFFERS from the record" in capsys.readouterr().out
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
    expected = json.loads((TOOLS / "d2s0_expected.json").read_text())
    assert len(expected["inputs"]) == 16 and len(expected["stat"]) == 40
    assert sum("/dumps/lat_" in path for path in expected["stat"]) == 24
    assert sum("flux-gen2thin-pdg14-" in path for path in expected["stat"]) == 3
    root = "/pscratch/sd/j/josephrb/rpd-reco-flux4-20261126/run/"
    p0_root = "/pscratch/sd/j/josephrb/rpd-reco-p0e1-20261126/run/"
    assert all(path.startswith(root) or path.startswith(p0_root) for path in expected["inputs"])
    # Every expected sha256 equals flux4's committed records (run-62051670): the two record files' own digests and
    # the 12 factor products' digests as the extract records them.
    records = TOOLS.parent.parent / "flux4-20261126" / "run-62051670" / "records" / "run"
    want = {root + name: digest(records / name) for name in ("flux-extract.json", "flux-custody.json")}
    for playlist, product in json.loads((records / "flux-extract.json").read_text())["factor_products"].items():
        assert product["path"] == f"{root}flux-factors-{playlist}.npz"
        want[product["path"]] = product["sha256"]
    # p0e1's two run records, from the committed p0e1 records (run-20261127): p0.json as committed, pins.json from its
    # byte-exact gzip; p0.json names pins.json's sha256 as its predecessor.
    p0_records = TOOLS.parent.parent / "p0e1-20261126" / "run-20261127" / "records" / "run"
    pins = gzip.decompress((p0_records / "pins.json.gz").read_bytes())
    want[p0_root + "p0.json"] = digest(p0_records / "p0.json")
    want[p0_root + "pins.json"] = hashlib.sha256(pins).hexdigest()
    assert json.loads((p0_records / "p0.json").read_text())["predecessor_sha256"] == want[p0_root + "pins.json"]
    assert expected["inputs"] == want


def test_stage_copies_byte_for_byte_and_refuses_the_rest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    checks = load()
    monkeypatch.setattr(checks.os, "O_NOATIME", 0, raising=False)
    source = tmp_path / "pins.json"
    source.write_bytes(b'{"step": "pins"}\n')
    want = digest(source)
    dest = tmp_path / "run" / "pins.json"
    dest.parent.mkdir()
    assert checks.stage(str(source), want, str(dest)) == 0
    assert dest.read_bytes() == source.read_bytes() and (dest.stat().st_mode & 0o777) == 0o600
    assert "STAGE: PASS" in capsys.readouterr().out
    assert checks.stage(str(source), want, str(dest)) == 3  # never overwrites
    assert "cannot create" in capsys.readouterr().out
    other = tmp_path / "run" / "other.json"
    assert checks.stage(str(source), "0" * 64, str(other)) == 3 and not other.exists()  # wrong sha: nothing written
    assert "expected" in capsys.readouterr().out
    assert checks.stage(str(source) + ".gone", want, str(other)) == 3 and not other.exists()
    assert "cannot read" in capsys.readouterr().out
    monkeypatch.delattr(checks.os, "O_NOATIME", raising=False)
    assert checks.stage(str(source), want, str(other)) == 3 and not other.exists()
    assert "no O_NOATIME" in capsys.readouterr().out


def test_stage_reads_with_the_noatime_flag(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    checks = load()
    monkeypatch.setattr(checks.os, "O_NOATIME", 0o1000000, raising=False)
    seen = []
    real_open = os.open

    def spy(path, flags, *args):
        seen.append((str(path), flags))
        return real_open(path, flags & ~0o1000000, *args)

    monkeypatch.setattr(checks.os, "open", spy)
    source = tmp_path / "p0.json"
    source.write_bytes(b"{}\n")
    assert checks.stage(str(source), digest(source), str(tmp_path / "copy.json")) == 0
    assert any(path == str(source) and flags & 0o1000000 for path, flags in seen)


def test_stage_through_main(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    checks = load()
    monkeypatch.setattr(checks.os, "O_NOATIME", 0, raising=False)
    source = tmp_path / "a.json"
    source.write_bytes(b"[]\n")
    assert checks.main(["d2s0_checks.py", "stage", str(source), digest(source), str(tmp_path / "b.json")]) == 0
    assert checks.main(["d2s0_checks.py", "stage", str(source)]) == 2


def test_the_stat_table_is_p0e1s() -> None:
    """The retention stat is p0e1's 40 entries exactly (S1's 27 plus the probe's 13)."""
    stat = json.loads((TOOLS / "d2s0_expected.json").read_text())["stat"]
    p0e1 = json.loads((TOOLS.parent.parent / "p0e1-20261126" / "tools" / "p0_expected.json").read_text())["stat"]
    assert stat == p0e1 and len(stat) == 40


def test_the_p0e1_records_are_a_passing_chain_for_this_config() -> None:
    """require_predecessors at S compares code, config and dry_run: p0e1's run records must carry this package's config."""
    reco = TOOLS.parent.parent
    p0_records = reco / "p0e1-20261126" / "run-20261127" / "records" / "run"
    p0 = json.loads((p0_records / "p0.json").read_text())
    pins = json.loads(gzip.decompress((p0_records / "pins.json.gz").read_bytes()))
    config = digest(TOOLS.parent / "production-config.ready.json")
    for record, step in ((pins, "pins"), (p0, "p0")):
        assert record["step"] == step and record["status"] == "PASS" and record["dry_run"] is False
        assert record["config_sha256"] == config
        assert record["code_sha256"] == "12f68102d38ec042d791b9edeb59ba96bdcda74c54dc37e5880c0922b0fbb9ec"
    assert p0["result"]["C-JOIN"]["part2"]["status"] == "PASS"

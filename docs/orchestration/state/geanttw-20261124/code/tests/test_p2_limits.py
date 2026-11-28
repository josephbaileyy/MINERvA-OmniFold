"""p2_limits.py: the committed limits are the formula's, and every refusal."""
import importlib.util
import subprocess
import sys
import os
from pathlib import Path

import pytest

CODE = Path(__file__).resolve().parents[1]
REPO = Path(os.environ.get("GEANTTW_REPO") or CODE.parents[4])   # a copy of code/ is told the repo
assert (REPO / "2d-unfolding").is_dir(), f"no repository at {REPO}: set GEANTTW_REPO"
_s = importlib.util.spec_from_file_location("p2l", CODE / "p2_limits.py")
L = importlib.util.module_from_spec(_s)
_s.loader.exec_module(L)


def run(*args):
    return subprocess.run([sys.executable, str(CODE / "p2_limits.py"), *map(str, args)], capture_output=True, text=True)


def test_the_committed_limits_are_the_formulas():
    p = run("--repo", REPO, "--check", CODE / "p2_limits.txt")
    assert p.returncode == 0, p.stdout + p.stderr


def test_a_changed_limits_file_refuses(tmp_path):
    t = tmp_path / "l.txt"
    t.write_text((CODE / "p2_limits.txt").read_text().replace("1M 05:36:00", "1M 06:00:00"))
    assert run("--repo", REPO, "--check", t).returncode == 1


def fake_repo(tmp, mc_bytes, missing=False, empty=False):
    (tmp / "2d-unfolding" / "playlist_manifests").mkdir(parents=True)
    t = tmp / L.TSV
    t.parent.mkdir(parents=True)
    rows = []
    for pl in L.PLAYLISTS:
        rel = f"MC/{pl}/a.root"
        (tmp / "2d-unfolding" / "playlist_manifests" / f"{pl}_MC.txt").write_text("" if empty and pl == "1A" else L.ROOT + rel + "\n")
        if not (missing and pl == "1B"):
            rows.append(f"{'0' * 64}\t{mc_bytes.get(pl, 100)}\t2025-01-01T00:00:00Z\t{rel}")
    t.write_text("sha256\tbytes\tmtime\tpath\n" + "\n".join(rows) + "\n")
    return tmp


def test_the_formula_floor_and_scale(tmp_path):
    r = fake_repo(tmp_path, {"1L": 100, "1A": 100, "1B": 300})
    text = L.limits_text(r)
    lines = dict(ln.split() for ln in text.splitlines())
    assert "1L" not in lines
    assert lines["1A"] == "00:30:00"                       # 3 x 435 s = 21:45 -> the 30 min floor
    assert lines["1B"] == "01:06:00"                       # 3 x 435 s x 3 = 65:15 -> rounded up to the minute
    assert len(lines) == 11


def test_a_manifest_path_without_a_row_refuses(tmp_path):
    with pytest.raises(SystemExit, match="no ANATUPLE row"):
        L.limits_text(fake_repo(tmp_path, {}, missing=True))


def test_an_empty_manifest_refuses(tmp_path):
    with pytest.raises(SystemExit, match="is empty"):
        L.limits_text(fake_repo(tmp_path, {}, empty=True))


def test_it_prints_the_limits(tmp_path):
    p = run("--repo", fake_repo(tmp_path, {}))
    assert p.returncode == 0 and p.stdout.count("\n") == 11


def test_repo_is_required(capsys):
    with pytest.raises(SystemExit) as e:
        L.main([])
    assert e.value.code == 2 and "--repo" in capsys.readouterr().err

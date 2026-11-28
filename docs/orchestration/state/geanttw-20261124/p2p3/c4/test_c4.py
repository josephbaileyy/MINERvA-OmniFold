"""c4_header.py, nue_grep.sh and run_c4.sh on fixtures: each result, and each fail-closed STOP."""
import hashlib
import re
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
import uproot

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import c4_header as C   # noqa: E402

PLS = C.PLAYLISTS
SIZES = {pl: 3 + i for i, pl in enumerate(PLS)}   # entries per playlist, per tree


def tree_cols(t, n, drop=None):
    cols = {b: np.zeros(n) for b in C.SLIM[t] if b != drop}
    cols["extra_branch"] = np.zeros(n)
    return cols


def write(path, n, drop=None):
    with uproot.recreate(path) as f:
        for t in C.TREES:
            f[t] = tree_cols(t, n, drop)
    st = os.stat(path)   # a future atime, so a non-O_NOATIME test read leaves it in place
    os.utime(path, ns=(st.st_mtime_ns + 3600 * 10**9, st.st_mtime_ns))


def make_d2(tmp, drop=None, missing=()):
    d2 = tmp / "d2"
    d2.mkdir()
    write(d2 / "runEventLoopOmniFold_MEFHC_universes_full.root", sum(SIZES.values()), drop)
    for pl in PLS:
        if pl not in missing:
            write(d2 / f"runEventLoopOmniFold_{pl}_universes_full.root", SIZES[pl])
    return d2


def run_c4(d2, size=None, door=True):
    env = {k: v for k, v in os.environ.items() if not k.startswith(("C4_TEST_", "NUE_TEST_"))}
    if door:
        u = d2 / "runEventLoopOmniFold_MEFHC_universes_full.root"
        env.update(C4_TEST_D2=str(d2), C4_TEST_UOMNI_SIZE=str(size if size is not None else u.stat().st_size))
    p = subprocess.run([sys.executable, "-I", str(HERE / "c4_header.py")], capture_output=True, text=True, env=env)
    js = [ln[5:] for ln in p.stdout.splitlines() if ln.startswith("JSON ")]
    return p, (json.loads(js[0]) if js else None)


def test_slim_list_is_the_37():
    assert [len(C.SLIM[t]) for t in C.TREES] == [3, 9, 8, 17]
    assert sum(len(v) for v in C.SLIM.values()) == 37


def test_all_present_gives_sizes_and_a_settled_offset(tmp_path):
    p, r = run_c4(make_d2(tmp_path))
    assert p.returncode == 0, p.stdout + p.stderr
    assert len(r["i"]["branches"]) == 37 and "STOP" not in p.stdout
    pre = sum(SIZES[pl] for pl in PLS[:PLS.index("1L")])
    assert r["ii"]["offset_1L"] == {t: pre for t in C.TREES} and r["ii"]["count_1L"] == {t: SIZES["1L"] for t in C.TREES}
    assert r["ii"]["offset_settled"] is True


def test_a_missing_slim_branch_stops_part_i_and_part_ii_still_reports(tmp_path):
    p, r = run_c4(make_d2(tmp_path, drop="w_truth_GEANT_Pion_0"))
    assert p.returncode == 2 and "STOP: (i) mc_truth_denom:w_truth_GEANT_Pion_0 is not in UOMNI" in p.stdout
    assert r["i"] is None and r["ii"]["offset_settled"] is False and "offset_1L" in r["ii"]


def test_a_size_mismatch_stops_part_i(tmp_path):
    p, r = run_c4(make_d2(tmp_path), size=1)
    assert p.returncode == 2 and "is not Stage C's" not in p.stdout and "!= Stage C's 1" in p.stdout


def test_missing_per_playlist_files_leave_the_offset_unsettled(tmp_path):
    p, r = run_c4(make_d2(tmp_path, missing=("1C",)))
    assert p.returncode == 0 and r["ii"]["missing"] == ["1C"] and r["ii"]["offset_settled"] is False
    assert "C3 waits" in p.stdout


@pytest.mark.skipif(hasattr(os, "O_NOATIME"), reason="this OS has O_NOATIME")
def test_outside_the_tests_no_noatime_stops_both_parts(tmp_path):
    p, r = run_c4(make_d2(tmp_path), door=False)
    assert p.returncode == 2 and "STOP: (i) this Python has no O_NOATIME" in p.stdout


def test_the_real_paths_are_pinned():
    s = (HERE / "c4_header.py").read_text()
    assert 'D2 = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding"' in s
    assert "UOMNI_SIZE = 171117087867\n" in s and "import glob" not in s and "glob(" not in s


# ---- nue_grep.sh
@pytest.fixture
def shim(tmp_path):
    """sha256sum for macOS, as a PATH shim over shasum -a 256."""
    b = tmp_path / "bin"
    b.mkdir()
    (b / "sha256sum").write_text('#!/bin/bash\nshasum -a 256 "$@"\n')
    (b / "sha256sum").chmod(0o755)
    return f"{b}:{os.environ['PATH']}"


def src_trees(tmp):
    root = tmp / "src"
    for t in ("evloop", "MAT", "MAT-MINERvA-pin", "MAT-MINERvA-pat"):
        (root / t).mkdir(parents=True)
    (root / "evloop" / "runEventLoopOmniFold.cpp").write_text("x;\n  PlotUtils::MinervaUniverse::SetNuEConstraint(true);\n")
    (root / "evloop" / "notes.txt").write_text("SetNuEConstraint in prose\n")
    (root / "MAT-MINERvA-pin" / "Flux.h").write_text("static void SetNuEConstraint(bool);\n")
    return root


def grep(root, path):
    env = {**{k: v for k, v in os.environ.items() if not k.startswith("NUE_TEST_")}, "PATH": path}
    return subprocess.run(["bash", str(HERE / "nue_grep.sh"), str(root)], capture_output=True, text=True, env=env)


def test_grep_reports_source_hits_with_shas_only(tmp_path, shim):
    root = src_trees(tmp_path)
    (root / "MAT" / "inside").symlink_to(root / "MAT-MINERvA-pin" / "Flux.h")
    p = grep(root, shim)
    assert p.returncode == 0, p.stdout + p.stderr
    assert "runEventLoopOmniFold.cpp:2:" in p.stdout and "Flux.h:1:" in p.stdout and "notes.txt" not in p.stdout
    assert p.stdout.count("sha256 ") == 2 and "== nue_grep done" in p.stdout


def test_a_symlink_out_of_src_stops_before_any_grep(tmp_path, shim):
    root = src_trees(tmp_path)
    (tmp_path / "outside.h").write_text("SetNuEConstraint\n")
    (root / "MAT" / "escape.h").symlink_to(tmp_path / "outside.h")
    p = grep(root, shim)
    assert p.returncode == 2 and "STOP: a symlink resolves outside" in p.stdout and "== tree" not in p.stdout


def test_a_missing_tree_stops(tmp_path, shim):
    root = src_trees(tmp_path)
    shutil.rmtree(root / "MAT")
    p = grep(root, shim)
    assert p.returncode == 2 and "STOP: no tree" in p.stdout


# ---- run_c4.sh
def test_runner_refuses_a_wrong_sha():
    p = subprocess.run(["bash", str(HERE / "run_c4.sh"), "0" * 64, "0" * 64], capture_output=True, text=True)
    assert p.returncode == 9 and "REFUSED: c4_header.py is" in p.stdout


def test_runner_parts_report_independently(tmp_path, shim):
    """The assembled remote script, run locally: part 1 STOPs, part 2 still runs and reports."""
    d2 = make_d2(tmp_path, drop="measured")
    root = src_trees(tmp_path)
    work = tmp_path / "w"
    work.mkdir()
    for f in ("c4_header.py", "nue_grep.sh"):
        shutil.copy(HERE / f, work / f)
    r = (HERE / "run_c4.sh").read_text()
    r = re.sub(r'^SSH=.*$', 'SSH=""', r, flags=re.M).replace("PY=/global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python3",
                                                         f"PY={sys.executable}")
    r = r.split("VALID=$(ssh-keygen")[0] + "{" + r.split("\n{", 1)[1]   # no cert gate in the test copy
    (work / "run_c4.sh").write_text(r)
    shas = [hashlib.sha256((work / f).read_bytes()).hexdigest() for f in ("c4_header.py", "nue_grep.sh")]
    env = {**os.environ, "PATH": shim, "C4_TEST_D2": str(d2),
           "C4_TEST_UOMNI_SIZE": str((d2 / "runEventLoopOmniFold_MEFHC_universes_full.root").stat().st_size),
           "NUE_TEST_SRC": str(root)}
    p = subprocess.run(["bash", str(work / "run_c4.sh"), *shas], capture_output=True, text=True, env=env)
    assert "== part1 rc=2" in p.stdout and "== part2 rc=0" in p.stdout, p.stdout + p.stderr
    assert "runEventLoopOmniFold.cpp:2:" in p.stdout

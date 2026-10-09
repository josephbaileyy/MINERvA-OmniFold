"""Tests for the release packaging and correction calculations added on 2026-10-08 (PRD release audit ea939701).

  python3 -m pytest publication/release/test_release_tools.py
"""
from __future__ import annotations

import gzip
import importlib.util
import io
import sys
import tarfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


build_rc = load("build_rc", HERE / "build_rc.py")
m1f2 = load("m1_f2_norm_ratio", ROOT / "docs/publication/corrections-20261008/m1_f2_norm_ratio.py")
seed = load("seed_effect_exponent", ROOT / "docs/publication/corrections-20261008/seed_effect_exponent.py")


def test_build_is_byte_reproducible_and_normalized():
    files = {"README.md": b"x\n", "code/a.py": b"print(1)\n", "data/b/c.npz": b"\x00\x01"}
    one, two = build_rc.build(dict(files), "pkg"), build_rc.build(dict(files), "pkg")
    assert one == two
    raw = gzip.decompress(one)
    with tarfile.open(fileobj=io.BytesIO(raw)) as tar:
        members = tar.getmembers()
        names = [m.name for m in members]
        assert names == sorted(names)
        for m in members:
            assert (m.mtime, m.uid, m.gid, m.uname, m.gname) == (build_rc.EPOCH, 0, 0, "", "")
        modes = {m.name: m.mode for m in members}
        assert modes["pkg/code/a.py"] == 0o755 and modes["pkg/README.md"] == 0o644
        assert tar.extractfile("pkg/data/b/c.npz").read() == b"\x00\x01"


def test_build_changes_when_a_file_changes():
    a = build_rc.build({"f": b"1"}, "pkg")
    b = build_rc.build({"f": b"2"}, "pkg")
    assert a != b


def test_m1_f2_ratio_is_relative_not_raw(tmp_path):
    f_mid, f_coarse = np.array([1.0, 100.0]), np.array([1.0, 100.0])
    d_m1, d_f2 = np.array([0.1, 0.0]), np.array([0.0, 10.0])  # equal relative size, raw sizes 100x apart
    for g in m1f2.GENERATORS:
        np.savez(tmp_path / f"fine-minus-mid-{g}.npz", D_J=d_m1, f_B_mean=f_mid)
        np.savez(tmp_path / f"delta-{g}.npz", D_J=d_f2, f_B_mean=f_coarse)
    r = m1f2.ratios(tmp_path)
    for v in r.values():
        assert abs(v["relative_L2"] - 1.0) < 1e-12
        assert abs(v["raw_L2"] - 0.01) < 1e-12


def test_seed_exponent_recovers_a_known_power_law():
    pts = [(n, 3.0 * n ** -0.5) for n in (40, 80, 160)]
    assert abs(seed.lsq_exponent(pts) - 0.5) < 1e-12
    flat = [(40, 6.0), (80, 6.0), (160, 6.0)]
    assert abs(seed.lsq_exponent(flat)) < 1e-12


def test_seed_exponent_on_the_committed_receipt():
    out = io.StringIO()
    old, sys.stdout = sys.stdout, out
    try:
        seed.main([str(ROOT / "docs/orchestration/state/SEED-EFFECT-20260920.json")])
    finally:
        sys.stdout = old
    text = out.getvalue()
    assert '"lsq_exponent_three_means": -0.0144' in text
    assert '"two_point_exponent_40_to_80": 0.0003' in text


def test_readme_follows_the_candidate_name():
    assert build_rc.readme_for("minerva-omnifold-article-release-rc6") == "docs/publication/release/RC6-README.md"
    try:
        build_rc.readme_for("minerva-omnifold-article-release")
    except SystemExit:
        pass
    else:
        raise AssertionError("a name without -rc<N> must be refused")

"""c2_check.py on fixtures: PASS on bitwise-equal rows, FAIL on any one changed value, and each unusable input."""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
import uproot

CODE = Path(__file__).resolve().parents[1]
_s = importlib.util.spec_from_file_location("c2", CODE / "c2_check.py")
C2 = importlib.util.module_from_spec(_s)
_s.loader.exec_module(C2)
PLS = ("1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P")
N = {pl: 2 + i % 3 for i, pl in enumerate(PLS)}   # rows per playlist, every tree


def cols(t, n, seed, patched):
    rng = np.random.default_rng(seed)
    out = {}
    for b in C2.SLIM[t] + ["extra"]:
        dt = np.uint8 if b.endswith("_pass") else np.float64
        out[b] = rng.integers(0, 2, n).astype(dt) if dt == np.uint8 else rng.uniform(0, 2, n)
        if patched and b in C2.TARGETS.get(t, []):
            out[b] = out[b] * 1.5   # P2's patched truth weights differ from UOMNI's pinned ones
    return out


def write(path, per_tree):
    with uproot.recreate(path) as f:
        for t, c in per_tree.items():
            f[t] = c


@pytest.fixture
def ws(tmp_path):
    parts = {pl: {t: cols(t, N[pl], 100 * i + j, False) for j, t in enumerate(C2.TREES)} for i, pl in enumerate(PLS)}
    uomni = {t: {b: np.concatenate([parts[pl][t][b] for pl in PLS]) for b in C2.SLIM[t] + ["extra"]} for t in C2.TREES}
    write(tmp_path / "uomni.root", uomni)
    dumps = []
    for i, pl in enumerate(PLS):
        d = tmp_path / f"pat_{pl}.root"
        write(d, {t: {b: (v * 1.5 if b in C2.TARGETS.get(t, []) else v) for b, v in parts[pl][t].items()}
                  for t in C2.TREES})
        dumps.append(d)
    off = {t: sum(N[pl] for pl in PLS[:PLS.index("1L")]) for t in C2.TREES}
    write(tmp_path / "pin_1L.root", parts["1L"])
    return {"tmp": tmp_path, "parts": parts, "dumps": dumps, "off": off}


def run(ws, *args, door=True):
    env = {k: v for k, v in os.environ.items() if not k.startswith("C2_TEST")}
    if door:
        env.update(C2_TEST="1", C2_TEST_OFFSET=json.dumps(ws["off"]), C2_TEST_N=json.dumps({t: N["1L"] for t in C2.TREES}))
    out = ws["tmp"] / "c2.json"
    p = subprocess.run([sys.executable, "-I", str(CODE / "c2_check.py"), *args, "--uomni", str(ws["tmp"] / "uomni.root"),
                        "--json", str(out)], capture_output=True, text=True, env=env)
    return p, (json.loads(out.read_text()) if out.exists() else None)


def test_branch_lists_are_the_grant():
    assert sum(len(v) for v in C2.SLIM.values()) == 37 and sum(len(v) for v in C2.NON_TARGET.values()) == 25


def test_pre_passes_on_the_1L_slice(ws):
    p, r = run(ws, "pre", "--dump", str(ws["tmp"] / "pin_1L.root"))
    assert p.returncode == 0, p.stdout + p.stderr
    assert "C2-PRE PASS: 37/37" in p.stdout and r["differ"] == []


def test_pre_fails_on_one_changed_value_including_a_target(ws):
    ws["parts"]["1L"]["mc_truth_denom"]["w_truth_GEANT_Pion_0"][1] += 1e-12
    write(ws["tmp"] / "pin_1L.root", ws["parts"]["1L"])
    p, r = run(ws, "pre", "--dump", str(ws["tmp"] / "pin_1L.root"))
    assert p.returncode == 1 and r["differ"] == ["mc_truth_denom:w_truth_GEANT_Pion_0"]
    assert r["verdict"] == "FAIL" and "C2-PRE FAIL: 36/37" in p.stdout
    text = (ws["tmp"] / "c2.json").read_text()
    assert text == json.dumps(json.loads(text), indent=1, sort_keys=True)   # the record's keys are sorted


def test_pre_fails_on_a_wrong_offset(ws):
    ws["off"] = {t: v + 1 for t, v in ws["off"].items()}
    p, r = run(ws, "pre", "--dump", str(ws["tmp"] / "pin_1L.root"))
    assert p.returncode == 1   # every float branch differs; a 0/1 *_pass branch may match a shifted slice by chance
    assert {"mc_signal_reco:MC", "mc_truth_denom:MC_pz", "data:measured"} <= set(r["differ"])














def test_full_is_no_longer_a_mode(ws):
    p, _ = run(ws, "full", "--dump", str(ws["tmp"] / "pin_1L.root"))
    assert p.returncode == 2 and "invalid choice" in p.stderr


def test_pre_needs_a_dump(ws):
    p, _ = run(ws, "pre")
    assert p.returncode == 2 and "pre takes --dump" in p.stdout


def test_uomni_is_required(ws):
    p = subprocess.run([sys.executable, "-I", str(CODE / "c2_check.py"), "pre", "--dump", "x"],
                       capture_output=True, text=True)
    assert p.returncode == 2 and "--uomni" in p.stderr


@pytest.mark.parametrize("b", [np.zeros(4, dtype=np.int64), np.zeros((2, 2))])
def test_same_bits_needs_the_same_dtype_and_shape(b):
    assert C2.same_bits(np.zeros(4), np.zeros(4)) is True
    assert C2.same_bits(np.zeros(4), b) is False   # the same bytes, another dtype or shape


def test_a_dump_missing_a_branch_is_unusable(ws):
    c = {t: dict(v) for t, v in ws["parts"]["1L"].items()}
    del c["mc_signal_reco"]["sim_pass"]
    write(ws["tmp"] / "pin_1L.root", c)
    p, _ = run(ws, "pre", "--dump", str(ws["tmp"] / "pin_1L.root"))
    assert p.returncode == 2 and "lacks ['sim_pass']" in p.stdout


@pytest.mark.skipif(hasattr(os, "O_NOATIME"), reason="this OS has O_NOATIME")
def test_outside_the_tests_no_noatime_is_unusable(ws):
    p, _ = run(ws, "pre", "--dump", str(ws["tmp"] / "pin_1L.root"), door=False)
    assert p.returncode == 2 and "no O_NOATIME" in p.stdout


def test_the_pinned_offset_is_c4s():
    s = (CODE / "c2_check.py").read_text()
    assert 'OFFSET_1L = {"data": 2778489, "mc_background": 407731, "mc_truth_denom": 20716792, "mc_signal_reco": 20716792}' in s



@pytest.mark.parametrize("cut", [1, -1])
def test_pre_refuses_a_dump_that_is_not_1ls_size(ws, cut):
    """An oversized dump would read past the granted 1L slice; a truncated one could pass on a matching prefix."""
    part = ws["parts"]["1L"]
    if cut > 0:
        part = {t: {b: np.r_[v, v[:1]] for b, v in c.items()} for t, c in part.items()}
    else:
        part = {t: {b: v[:-1] for b, v in c.items()} for t, c in part.items()}
    write(ws["tmp"] / "pin_1L.root", part)
    p, _ = run(ws, "pre", "--dump", str(ws["tmp"] / "pin_1L.root"))
    assert p.returncode == 2 and "not C4's 1L count" in p.stdout


def test_the_real_1l_counts_are_c4s():
    assert C2.N_1L == {"data": 49872, "mc_background": 7820, "mc_truth_denom": 383848, "mc_signal_reco": 383848}

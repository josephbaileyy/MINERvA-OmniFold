"""dumpcmp.py: every rule passes on equal inputs and fails on one planted difference."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import awkward as ak
import numpy as np
import pytest
import uproot

CODE = Path(__file__).resolve().parents[1]
_s = importlib.util.spec_from_file_location("dumpcmp", CODE / "dumpcmp.py")
dc = importlib.util.module_from_spec(_s)
_s.loader.exec_module(dc)

N = 6


def base():
    rng = np.random.default_rng(1)
    w = rng.uniform(0.5, 2.0, N)
    return {
        "mc_signal_reco": {"w_truth": w.copy(), "w_reco": w * 1.1, "pt": rng.uniform(0, 2, N),
                           "w_truth_GEANT_Pion_0": w.copy(), "w_reco_GEANT_Pion_0": w * 1.1},
        "data": {"pt": rng.uniform(0, 2, N), "n": np.arange(N, dtype=np.int32)},
    }


def write(path, trees):
    with uproot.recreate(path) as f:
        for t, cols in trees.items():
            f[t] = cols
    return path


def ulp(x):
    return np.nextafter(x, np.inf)


def run(tmp_path, a, b, **kw):
    return dc.compare(write(tmp_path / "a.root", a), write(tmp_path / "b.root", b), **kw)


def test_identical_pass(tmp_path):
    r = run(tmp_path, base(), base())
    assert r["verdict"] == "PASS" and r["problems"] == []
    assert r["trees"]["data"]["branches"]["n"] == {"judged": True, "n_diff": 0, "first_diff": None}


def test_one_ulp_fails_with_index(tmp_path):
    b = base()
    b["mc_signal_reco"]["pt"][3] = ulp(b["mc_signal_reco"]["pt"][3])
    r = run(tmp_path, base(), b)
    assert r["verdict"] == "FAIL"
    assert r["trees"]["mc_signal_reco"]["branches"]["pt"] == {"judged": True, "n_diff": 1, "first_diff": 3}


def test_last_entry_and_int_branch(tmp_path):
    b = base()
    b["data"]["n"][N - 1] += 1
    r = run(tmp_path, base(), b)
    assert r["verdict"] == "FAIL" and r["trees"]["data"]["branches"]["n"]["first_diff"] == N - 1


def test_exempt_reported_not_judged(tmp_path):
    b = base()
    b["mc_signal_reco"]["w_truth_GEANT_Pion_0"][:2] *= 1.5
    r = run(tmp_path, base(), b, exempt=r"w_truth_GEANT_Pion_0")
    assert r["verdict"] == "PASS"
    assert r["trees"]["mc_signal_reco"]["branches"]["w_truth_GEANT_Pion_0"] == {"judged": False, "n_diff": 2,
                                                                                  "first_diff": 0}


def test_exempt_is_a_full_match(tmp_path):
    b = base()
    b["mc_signal_reco"]["w_truth_GEANT_Pion_0"][0] *= 2
    r = run(tmp_path, base(), b, exempt=r"w_truth_GEANT_Pion")
    assert r["verdict"] == "FAIL"


def test_negative_zero_differs_and_nan_payload_equal(tmp_path):
    a, b = base(), base()
    a["data"]["pt"][0], b["data"]["pt"][0] = 0.0, -0.0
    assert run(tmp_path, a, b)["verdict"] == "FAIL"
    a, b = base(), base()
    a["data"]["pt"][1] = b["data"]["pt"][1] = np.nan
    assert run(tmp_path, a, b)["verdict"] == "PASS"


def test_dtype_mismatch_fails(tmp_path):
    b = base()
    b["data"]["pt"] = b["data"]["pt"].astype(np.float32)
    r = run(tmp_path, base(), b)
    assert r["verdict"] == "FAIL" and any("dtype" in p for p in r["problems"])


def test_shape_mismatch_fails(tmp_path):
    a, b = base(), base()
    a["data"]["v"] = np.zeros((N, 3))
    b["data"]["v"] = np.zeros((N, 2))
    r = run(tmp_path, a, b)
    assert r["verdict"] == "FAIL" and any("shape" in p for p in r["problems"])


def test_entry_count_and_tree_set(tmp_path):
    b = base()
    b["data"] = {k: v[:-1] for k, v in b["data"].items()}
    r = run(tmp_path, base(), b)
    assert r["verdict"] == "FAIL" and any("entries" in p for p in r["problems"])
    b = base()
    b["extra_tree"] = {"x": np.ones(N)}
    r = run(tmp_path, base(), b)
    assert r["verdict"] == "FAIL" and any("tree sets" in p for p in r["problems"])
    a = base()
    a["only_a"] = {"x": np.ones(N)}
    assert run(tmp_path, a, base())["verdict"] == "FAIL"


def test_missing_and_extra_branches(tmp_path):
    b = base()
    del b["data"]["n"]
    r = run(tmp_path, base(), b)
    assert r["verdict"] == "FAIL" and any("missing from B" in p for p in r["problems"])
    b = base()
    b["data"]["w_truth_GEANT_Neutron_1"] = np.ones(N)
    assert run(tmp_path, base(), b)["verdict"] == "FAIL"
    assert run(tmp_path, base(), b, allow_extra=dc_re())["verdict"] == "PASS"
    b["data"]["w_truth_GEANT_Neutron_2"] = np.ones(N)          # not a full match of the pattern
    assert run(tmp_path, base(), b, allow_extra=dc_re())["verdict"] == "FAIL"


def dc_re():
    return r"w_(truth|reco|bkg)_GEANT_(Neutron|Pion|Proton)_[01]"


def test_fixed_size_2d_branch(tmp_path):
    a, b = base(), base()
    a["data"]["v3"] = np.arange(N * 3, dtype=np.float64).reshape(N, 3)
    b["data"]["v3"] = a["data"]["v3"].copy()
    assert run(tmp_path, a, b)["verdict"] == "PASS"
    b["data"]["v3"][4, 2] = ulp(b["data"]["v3"][4, 2])
    r = run(tmp_path, a, b)
    assert r["trees"]["data"]["branches"]["v3"]["n_diff"] == 1 and r["trees"]["data"]["branches"]["v3"]["first_diff"] == 4


def jag(rows):
    return ak.Array(rows)


@pytest.mark.parametrize("rows_b,ok", [
    ([[1.0, 2.0], [], [3.0], [4.0], [5.0, 6.0], [7.0]], True),
    ([[1.0, 2.0], [], [3.0], [4.0], [5.0, 6.5], [7.0]], False),
    ([[1.0, 2.0], [], [3.0], [4.0, 9.0], [5.0, 6.0], [7.0]], False),
])
def test_jagged(tmp_path, rows_b, ok):
    rows_a = [[1.0, 2.0], [], [3.0], [4.0], [5.0, 6.0], [7.0]]
    a, b = base(), base()
    a["data"]["j"], b["data"]["j"] = jag(rows_a), jag(rows_b)
    r = run(tmp_path, a, b)
    assert (r["verdict"] == "PASS") is ok


def test_jagged_against_flat_fails(tmp_path):
    a, b = base(), base()
    a["data"]["j"] = jag([[1.0]] * N)
    b["data"]["j"] = np.ones(N)
    assert run(tmp_path, a, b)["verdict"] == "FAIL"


def test_cli_exit_codes_and_json(tmp_path):
    a = write(tmp_path / "a.root", base())
    b2 = base()
    b2["data"]["pt"][0] = ulp(b2["data"]["pt"][0])
    b = write(tmp_path / "b.root", b2)
    out = tmp_path / "r.json"
    p = subprocess.run([sys.executable, "-I", str(CODE / "dumpcmp.py"), str(a), str(a), "--json", str(out)],
                       capture_output=True, text=True)
    assert p.returncode == 0 and json.loads(out.read_text())["verdict"] == "PASS"
    p = subprocess.run([sys.executable, "-I", str(CODE / "dumpcmp.py"), str(a), str(b)], capture_output=True, text=True)
    assert p.returncode == 1 and "dumpcmp FAIL" in p.stdout and "pt differs" in p.stdout
    p = subprocess.run([sys.executable, "-I", str(CODE / "dumpcmp.py"), str(a), str(b), "--exempt", "pt"],
                       capture_output=True, text=True)
    assert p.returncode == 0
    p = subprocess.run([sys.executable, "-I", str(CODE / "dumpcmp.py"), str(a), str(write(tmp_path / "c.root", {
        **base(), "data": {**base()["data"], "w_reco_GEANT_Pion_1": np.ones(N)}})), "--allow-extra", dc_re()],
        capture_output=True, text=True)
    assert p.returncode == 0


def test_highest_cycle_is_compared(tmp_path):
    """A file whose tree has a stale cycle 1 and a current cycle 2 compares by cycle 2 only."""
    a = write(tmp_path / "a.root", {"data": {"pt": np.zeros(N)}})
    with uproot.update(a) as f:
        f["data"] = {"pt": np.ones(N)}
    with uproot.open(a) as f:
        assert sorted(f.keys()) == ["data;1", "data;2"]
    b = write(tmp_path / "b.root", {"data": {"pt": np.ones(N)}})
    assert dc.compare(a, b)["verdict"] == "PASS"
    assert dc.compare(b, a)["verdict"] == "PASS"


def test_jagged_entry_dtype_mismatch(tmp_path):
    a, b = base(), base()
    a["data"]["j"] = jag([[1.0]] * N)
    b["data"]["j"] = jag([[1]] * N)
    assert run(tmp_path, a, b)["verdict"] == "FAIL"

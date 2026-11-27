"""same_events.py on synthetic fixtures: each verdict, and each fail-closed stop before any comparison."""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

SCRIPT = Path(__file__).resolve().parent / "same_events.py"
N = 50


class WS:
    def __init__(self, tmp):
        self.root = tmp
        rng = np.random.default_rng(3)
        self.pt = rng.uniform(0, 4.5, N).astype(np.float32)
        self.pz = rng.uniform(1.5, 60, N).astype(np.float32)
        self.w5 = {"entry": np.arange(0, 2 * N, 2, dtype=np.uint32), "truth_pt": self.pt.copy(),
                   "truth_pz": self.pz.copy(), "w_unfolded": np.ones(N)}
        self.w2 = {"entry": np.arange(N, dtype=np.uint32), "truth_pt": self.pt.astype(np.float64),
                   "truth_pz": self.pz.astype(np.float64), "w_unfolded": np.ones(N)}
        self.c5 = {"key": "(input npz sha256, entry)", "n_rows": N}
        self.c2 = {"key": {"column": "entry"}, "rows": N}

    def write(self):
        names = {"evw5d_weights": "evw5d-weights.npz", "evw5d_constants": "evw5d-constants.json",
                 "evw2d_weights": "out-weights.npz", "evw2d_constants": "out-constants.json"}
        np.savez(self.root / names["evw5d_weights"], **self.w5)
        np.savez(self.root / names["evw2d_weights"], **self.w2)
        (self.root / names["evw5d_constants"]).write_text(json.dumps(self.c5))
        (self.root / names["evw2d_constants"]).write_text(json.dumps(self.c2))
        return {k: hashlib.sha256((self.root / v).read_bytes()).hexdigest() for k, v in names.items()}

    def run(self, shas=None, door=True):
        got = self.write()
        env = {k: v for k, v in os.environ.items() if not k.startswith("SAME_EVENTS_")}
        if door:
            env.update(SAME_EVENTS_TEST_ROOT=str(self.root), SAME_EVENTS_TEST_N=str(N))
            for k, v in {**got, **(shas or {})}.items():
                env["SAME_EVENTS_TEST_SHA_" + k.upper()] = v
        p = subprocess.run([sys.executable, "-I", str(SCRIPT)], capture_output=True, text=True, env=env)
        js = [ln[5:] for ln in p.stdout.splitlines() if ln.startswith("JSON ")]
        return p, (json.loads(js[0]) if js else None)


@pytest.fixture
def ws(tmp_path):
    return WS(tmp_path)


def test_identical_rows_in_the_same_order(ws):
    p, r = ws.run()
    assert p.returncode == 0, p.stdout + p.stderr
    assert r["verdict"] == "SAME-ROWS-SAME-ORDER" and r["T5"] == "not run (T4 exact on every row)"
    for c in ("truth_pt", "truth_pz"):
        assert r["T4"][c]["exact_equal_float32"] == N and r["T4"][c]["max_abs_delta_float64"] == 0.0
    assert r["T3"]["entries_equal"] is False and r["T3"]["first_differing_row"] == 1   # keys differ; not the test


def test_float64_detail_below_float32_is_exact_after_the_cast_and_reported(ws):
    ws.w2["truth_pt"] = ws.w2["truth_pt"] + np.spacing(ws.w2["truth_pt"].astype(np.float32)).astype(np.float64) * 1e-3
    p, r = ws.run()
    assert r["verdict"] == "SAME-ROWS-SAME-ORDER"
    assert r["T4"]["truth_pt"]["max_abs_delta_float64"] > 0 and r["T4"]["truth_pt"]["max_abs_delta_float32"] == 0


def test_a_shifted_row_is_not_exact_and_its_delta_is_reported(ws):
    ws.w2["truth_pz"][7] = np.float64(np.nextafter(np.float32(ws.pz[7]), np.float32(100))) + 0.5
    p, r = ws.run()
    assert p.returncode == 0 and r["verdict"] == "NOT-EXACT"
    d = r["T4"]["truth_pz"]
    assert d["exact_equal_float32"] == N - 1 and d["rows_over_1_ulp"] == 1
    assert d["nonzero_delta_distribution"]["n_nonzero"] == 1 and d["max_abs_delta_float32"] > 0.5
    assert r["T5"] == {"same_multiset_float32": False}


def test_permuted_rows_are_the_same_set_in_a_different_order(ws):
    perm = np.random.default_rng(9).permutation(N)
    for c in ("truth_pt", "truth_pz"):
        ws.w2[c] = ws.w2[c][perm]
    p, r = ws.run()
    assert r["verdict"] == "SAME-SET-DIFFERENT-ORDER" and r["T5"] == {"same_multiset_float32": True}


@pytest.mark.parametrize("which", ["evw5d_weights", "evw5d_constants", "evw2d_weights", "evw2d_constants"])
def test_a_sha_mismatch_stops_before_any_comparison(ws, which):
    p, r = ws.run(shas={which: "0" * 64})
    assert p.returncode == 2 and "STOP:" in p.stdout and r is None
    assert not any(ln.startswith(("T2", "T3", "T4")) for ln in p.stdout.splitlines())


def test_a_wrong_dtype_stops(ws):
    ws.w5["truth_pt"] = ws.w5["truth_pt"].astype(np.float64)
    p, r = ws.run()
    assert p.returncode == 2 and "is float64 (50,), not float32 1-D" in p.stdout and r is None


def test_a_missing_column_stops(ws):
    del ws.w2["truth_pz"]
    p, r = ws.run()
    assert p.returncode == 2 and "lacks ['truth_pz']" in p.stdout and r is None


def test_a_row_count_mismatch_stops(ws):
    for c in ws.w2:
        ws.w2[c] = ws.w2[c][:-1]
    p, r = ws.run()
    assert p.returncode == 2 and "T2 rows evw5d 50 evw2d 49" in p.stdout and r is None


def test_a_declared_count_mismatch_stops(ws):
    ws.c2["rows"] = N + 1
    p, r = ws.run()
    assert p.returncode == 2 and "declares 51 rows" in p.stdout and r is None


@pytest.mark.skipif(hasattr(os, "O_NOATIME"), reason="this OS has O_NOATIME")
def test_outside_the_tests_a_python_without_noatime_refuses(ws):
    p, r = ws.run(door=False)
    assert p.returncode == 2 and "STOP: this Python has no O_NOATIME" in p.stdout and r is None


def test_the_real_paths_and_shas_are_pinned():
    s = SCRIPT.read_text()
    for path, sha in (("/pscratch/sd/j/josephrb/evw5d-20261125-r2/evw5d/weights.npz",
                       "0fceefcdcfcd5c48070453707b55f40e55787909f98481dadcdc82dd0897aba6"),
                      ("/pscratch/sd/j/josephrb/evw5d-20261125-r2/evw5d/constants.json",
                       "8f009d828163161418e94997428c80a8c723fa3a015fcb63165861aa3312c3aa"),
                      ("/pscratch/sd/j/josephrb/evw2d-20261126/out/weights.npz",
                       "bf452352da52f12a2788f76c4caf9e8402600ba06d352fc99e9344d87367b108"),
                      ("/pscratch/sd/j/josephrb/evw2d-20261126/out/constants.json",
                       "1fe4449ee7ec34067f5d2a20aa841f2c97fd2f678eaa7f554ab583ad75daf2ba")):
        assert f'("{path}", "{sha}")' in s
    assert "N_DECLARED = 32849103\n" in s

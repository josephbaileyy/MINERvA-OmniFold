"""Tests for compare_sufficient.py: each verdict fires on the case it names and on nothing weaker (G12 review, MINOR 1)."""
from __future__ import annotations

import copy
import io
import json
import tempfile
import zipfile
from contextlib import redirect_stdout
from pathlib import Path

import numpy as np
import pytest

import importlib.util

spec = importlib.util.spec_from_file_location("compare_sufficient", Path(__file__).resolve().parent / "compare_sufficient.py")
cmp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cmp)

BASE = {"f": np.linspace(0.1, 1.0, 10), "seeds": np.arange(5, dtype=np.int64), "dom": np.array([True, False, True])}
MANIFEST = {"npz_sha256": "x", "code_root": "/a", "inputs": {"path": "/a/in"},
            "nulls": {"M": {"B": 1000, "shift": {"a": 0.0123456789, "se": 0.04}}}}


def verdict(new_arrays, new_manifest, *, old_compressed=False):
    """Write a preserved and a regenerated npz (+ manifest) and return (exit code, VERDICT line)."""
    with tempfile.TemporaryDirectory() as tmp:
        old, new = Path(tmp) / "old.npz", Path(tmp) / "new.npz"
        (np.savez_compressed if old_compressed else np.savez)(old, **BASE)
        np.savez(new, **new_arrays)
        Path(str(old) + ".manifest.json").write_text(json.dumps(MANIFEST))
        Path(str(new) + ".manifest.json").write_text(json.dumps(new_manifest))
        cmp.DIFFS.clear()
        out = io.StringIO()
        with redirect_stdout(out):
            rc = cmp.main([str(new), str(old)])
    line = [x for x in out.getvalue().splitlines() if x.startswith("VERDICT")][0]
    return rc, line


def manifest(**shift):
    m = copy.deepcopy(MANIFEST)
    m["nulls"]["M"]["shift"].update(shift)
    return m


def arrays(**changes):
    a = {k: v.copy() for k, v in BASE.items()}
    a.update(changes)
    return a


def test_identical_is_byte_identical():
    rc, v = verdict(arrays(), copy.deepcopy(MANIFEST))
    assert rc == 0 and "npz byte-identical" in v


def test_equal_arrays_in_a_different_container_are_serialization_only():
    rc, v = verdict(arrays(), copy.deepcopy(MANIFEST), old_compressed=True)
    assert rc == 0 and "serialization only" in v


def test_last_bit_float_differences_are_not_bit_identical():
    f = BASE["f"].copy()
    f[3] = np.nextafter(f[3], 2.0)
    rc, v = verdict(arrays(f=f), manifest(a=0.0123456789 * (1 + 1e-14)))
    assert rc == 1 and "NOT BIT-IDENTICAL" in v


@pytest.mark.parametrize("case", ["int_seeds", "shape", "bool_flip", "large_float"])
def test_a_real_array_difference_is_not_called_last_bits(case):
    changes = {
        "int_seeds": {"seeds": BASE["seeds"][::-1].copy()},
        "shape": {"f": np.linspace(0.1, 1.0, 9)},
        "bool_flip": {"dom": ~BASE["dom"]},
        "large_float": {"f": BASE["f"] * (1 + 1e-6)},
    }[case]
    rc, v = verdict(arrays(**changes), copy.deepcopy(MANIFEST))
    assert rc == 1 and "NOT REPRODUCED" in v, v


@pytest.mark.parametrize("field,value", [("B", 1365), ("prediction_sha256", "y")])
def test_a_changed_count_or_digest_under_nulls_is_not_called_last_bits(field, value):
    f = BASE["f"].copy()
    f[3] = np.nextafter(f[3], 2.0)
    m = copy.deepcopy(MANIFEST)
    m["nulls"]["M"][field] = value
    rc, v = verdict(arrays(f=f), m)
    assert rc == 1 and "NOT REPRODUCED" in v, v


def test_a_large_shift_statistic_change_is_not_called_last_bits():
    f = BASE["f"].copy()
    f[3] = np.nextafter(f[3], 2.0)
    rc, v = verdict(arrays(f=f), manifest(a=0.0124))
    assert rc == 1 and "NOT REPRODUCED" in v, v


def test_the_container_really_differs_in_the_serialization_case():
    """Guard the fixture: savez and savez_compressed must give different bytes, or the test above proves nothing."""
    with tempfile.TemporaryDirectory() as tmp:
        a, b = Path(tmp) / "a.npz", Path(tmp) / "b.npz"
        np.savez(a, **BASE)
        np.savez_compressed(b, **BASE)
        assert a.read_bytes() != b.read_bytes()
        assert zipfile.ZipFile(b).infolist()[0].compress_type == zipfile.ZIP_DEFLATED


def test_a_large_change_in_one_small_element_is_not_called_last_bits():
    """Review cycle 2: relative to the array maximum this is 2.5e-13, but the element itself moved by 50 %."""
    f = BASE["f"].copy()
    f[0] = 1e-12
    old = arrays(f=f)
    g = f.copy()
    g[0] = 1.5e-12
    with tempfile.TemporaryDirectory() as tmp:
        o, n = Path(tmp) / "old.npz", Path(tmp) / "new.npz"
        np.savez(o, **old)
        np.savez(n, **arrays(f=g))
        for p in (o, n):
            Path(str(p) + ".manifest.json").write_text(json.dumps(MANIFEST))
        cmp.DIFFS.clear()  # as verdict() does, so a tool that keeps state cannot pass on an earlier test's leftovers
        out = io.StringIO()
        with redirect_stdout(out):
            rc = cmp.main([str(n), str(o)])
    assert rc == 1 and "VERDICT: NOT REPRODUCED" in out.getvalue(), out.getvalue()


def test_a_path_key_present_in_only_one_manifest_is_not_a_location_difference():
    f = BASE["f"].copy()
    f[3] = np.nextafter(f[3], 2.0)
    m = copy.deepcopy(MANIFEST)
    m["nulls"]["M"]["shift"]["path"] = "/somewhere"
    rc, v = verdict(arrays(f=f), m)
    assert rc == 1 and "NOT REPRODUCED" in v, v

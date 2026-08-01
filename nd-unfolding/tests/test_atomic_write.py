"""Pin the J10 fix: the publication nominal write is transactional, not a bare savez.

`np.savez_compressed(out, ...)` streams into `out`. Kill it partway and what survives is
a nonempty, plausible, incomplete npz -- which every `[[ -s ]]` resume guard in the tree
read as finished, and which the Gate-4 validator would have read as a result.

These tests assert the property that matters: after an interrupted write, `out` is either
the previous file or absent, never a partial. They also cover the completion marker, which
is what makes a Python producer's output legible to lib/resume_guard.sh.
"""
import json
import os
import sys

import numpy as np
import pytest

_PET = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pet")
if _PET not in sys.path:
    sys.path.insert(0, _PET)

import atomic_write as aw  # noqa: E402


class Boom(Exception):
    pass


class TestAtomicity:
    def test_writes_and_reads_back(self, tmp_path):
        p = str(tmp_path / "x.npz")
        got = aw.atomic_savez_compressed(p, {"a": np.arange(5)})
        assert got == p
        with np.load(p) as d:
            assert list(d["a"]) == [0, 1, 2, 3, 4]

    def test_interrupted_write_leaves_no_file_at_the_destination(self, tmp_path):
        p = str(tmp_path / "x.npz")

        def boom(_tmp):
            raise Boom("killed mid-write")

        with pytest.raises(Boom):
            aw.atomic_write(p, boom)
        assert not os.path.exists(p)
        assert not list(tmp_path.glob(".atomic_*")), "temp must be cleaned up"

    def test_interrupted_rewrite_leaves_the_previous_file_intact(self, tmp_path):
        """The case that matters for a publication artifact: a failed re-run must not
        destroy the good result that was already there."""
        p = str(tmp_path / "x.npz")
        aw.atomic_savez_compressed(p, {"a": np.arange(3)})

        def boom(_tmp):
            raise Boom("killed mid-rewrite")

        with pytest.raises(Boom):
            aw.atomic_write(p, boom)
        with np.load(p) as d:
            assert list(d["a"]) == [0, 1, 2], "the old file must survive a failed rewrite"

    def test_partial_numpy_write_does_not_reach_the_destination(self, tmp_path):
        """Simulate the real failure: savez dies partway through serializing."""
        p = str(tmp_path / "x.npz")

        def half(tmp):
            with open(tmp, "wb") as f:
                f.write(b"PK\x03\x04truncated-npz-header")
            raise Boom("walltime")

        with pytest.raises(Boom):
            aw.atomic_write(p, half)
        assert not os.path.exists(p)

    def test_temp_is_a_sibling_so_the_rename_is_atomic(self, tmp_path):
        """A cross-filesystem mv is a copy, which is not atomic. Assert the temp lands
        in the destination directory rather than $TMPDIR."""
        seen = {}
        p = str(tmp_path / "sub" / "x.npz")

        def w(tmp):
            seen["dir"] = os.path.dirname(tmp)
            np.savez_compressed(tmp, a=np.arange(2))

        aw.atomic_write(p, w, suffix=".npz")
        assert seen["dir"] == os.path.dirname(os.path.abspath(p))


class TestNoClobber:
    def test_overwrite_false_refuses_an_existing_output(self, tmp_path):
        p = str(tmp_path / "x.npz")
        aw.atomic_savez_compressed(p, {"a": np.arange(2)})
        with pytest.raises(FileExistsError):
            aw.atomic_savez_compressed(p, {"a": np.arange(9)}, overwrite=False)
        with np.load(p) as d:
            assert len(d["a"]) == 2

    def test_overwrite_true_is_the_default(self, tmp_path):
        p = str(tmp_path / "x.npz")
        aw.atomic_savez_compressed(p, {"a": np.arange(2)})
        aw.atomic_savez_compressed(p, {"a": np.arange(9)})
        with np.load(p) as d:
            assert len(d["a"]) == 9


class TestSuffixNormalization:
    def test_npz_suffix_is_appended_like_numpy_does(self, tmp_path):
        """numpy appends '.npz' to a name that lacks it. The helper does the same and
        RETURNS the real path, so a caller cannot report a file that does not exist."""
        got = aw.atomic_savez_compressed(str(tmp_path / "bare"), {"a": np.arange(2)})
        assert got.endswith("bare.npz") and os.path.exists(got)
        assert not os.path.exists(str(tmp_path / "bare"))

    def test_atomic_write_itself_does_not_normalize(self, tmp_path):
        """The G2 dump contract writes to exactly the path it was given; that behaviour
        predates this helper and must not change."""
        p = str(tmp_path / "exact.dat")
        aw.atomic_write(p, lambda t: open(t, "w").write("x"))
        assert os.path.exists(p)


class TestCompletionMarker:
    def test_mark_and_is_complete(self, tmp_path):
        p = str(tmp_path / "x.npz")
        aw.atomic_savez_compressed(p, {"a": np.arange(2)}, mark=True, note="unit test")
        assert aw.is_complete(p)
        m = json.load(open(aw.completion_marker_path(p)))
        assert m["note"] == "unit test" and m["size"] == os.path.getsize(p)

    def test_unmarked_output_is_not_complete(self, tmp_path):
        p = str(tmp_path / "x.npz")
        aw.atomic_savez_compressed(p, {"a": np.arange(2)})
        assert not aw.is_complete(p)

    def test_marker_is_invalidated_by_a_later_rewrite(self, tmp_path):
        p = str(tmp_path / "x.npz")
        aw.atomic_savez_compressed(p, {"a": np.arange(2)}, mark=True)
        with open(p, "wb") as f:
            f.write(b"truncated")
        assert not aw.is_complete(p)

    def test_marker_format_matches_the_shell_library(self, tmp_path):
        """rg_is_complete parses these fields out of the JSON by hand."""
        p = str(tmp_path / "x.npz")
        aw.atomic_savez_compressed(p, {"a": np.arange(2)}, mark=True)
        m = json.load(open(aw.completion_marker_path(p)))
        assert {"output", "size", "mtime", "marked_at"} <= set(m)

    def test_python_marker_is_readable_by_the_shell_guard(self, tmp_path):
        import subprocess
        lib = os.path.join(os.path.dirname(_PET), "..", "lib", "resume_guard.sh")
        lib = os.path.normpath(lib)
        if not os.path.exists(lib):
            pytest.skip("resume_guard.sh not present")
        p = str(tmp_path / "x.npz")
        aw.atomic_savez_compressed(p, {"a": np.arange(2)}, mark=True)
        r = subprocess.run(["bash", "-c", f'source "{lib}"; rg_is_complete "{p}"'],
                           capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr


class TestContractStillGatesFirst:
    def test_gates_run_before_any_write(self, tmp_path):
        """write_fullevent_npz_atomic delegates its transaction here, but its schema and
        manifest gates must still fire first and leave nothing behind."""
        import fullevent_dump_contract as fdc
        p = str(tmp_path / "g2.npz")
        with pytest.raises(ValueError):
            fdc.write_fullevent_npz_atomic(p, {"petSchemaVersion": "wrong"})
        assert not os.path.exists(p)
        assert not list(tmp_path.iterdir())

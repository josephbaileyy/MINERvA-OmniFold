#!/usr/bin/env python3
"""Transactional file writes, and the completion markers shell resume guards read.

WHY THIS EXISTS (AUDIT-FINDINGS-20260731 J10, same defect class as J35 / BEN-023).
A bare `np.savez_compressed(out, ...)` writes incrementally straight to `out`.  Kill
it partway -- preemption, a walltime cut, a node failure -- and what is left at `out`
is a nonempty, plausible-looking, WRONG file.  Every resume guard in the tree that
asked `test -s` then skipped it forever.  For the publication nominal that is worse
than a crash, because the artifact survives to be read by the Gate-4 validator.

The transaction is: write a temp file in the SAME directory, fsync it, then
`os.replace()` it over the destination.  `os.replace` is atomic within a filesystem,
so a reader sees either the old file or the complete new one and never a half-written
one; an interruption leaves the temp behind and `out` untouched.  Same directory
matters -- a cross-filesystem move is a copy, which is not atomic.

This generalizes the pattern `fullevent_dump_contract.write_fullevent_npz_atomic`
already had -- that function is the correct in-repo precedent, named as such by J10 --
and adds an fsync and a no-clobber option.  Callers whose product is not a G2 dump
(the Gate-4 nominal weights, for one) use `atomic_savez_compressed` directly rather
than borrowing a schema that does not describe them.

WHY THE CONTRACT DOES NOT DELEGATE HERE.  It should, and the delegation was written and
then deliberately reverted: `fullevent_dump_contract.py` is frozen by
`docs/orchestration/state/g2-dump-submit-20260719.json`, the receipt attesting which code
produced `G2_FPS_MEFHC_P12.npz` -- the only `g2-fullevent-v1` input in existence.  That is
a data-provenance receipt, not a code gate, so re-issuing it would rewrite the record of
what ran at submit time, which is precisely what `verify_hash_bindings.py` refuses to do.
Deduplicating six lines is not worth falsifying that record.  Fold the contract onto this
module the next time that receipt is legitimately re-issued, i.e. when the dump is rebuilt.
"""
import json
import os
import socket
import tempfile
import time

import numpy as np


def completion_marker_path(path):
    """The marker lib/resume_guard.sh looks for. Kept identical to that convention
    (and to run_p4_unfold_std.sh's receipts) so a Python producer's output is visible
    to a shell resume guard."""
    return f"{path}.done"


def mark_complete(path, note=""):
    """Stamp `path` complete, binding the marker to the file's current size+mtime so a
    later truncation or partial rewrite invalidates it instead of keeping a stale pass.

    Written temp-then-rename for the same reason the payload is: a marker truncated
    mid-write must not parse as a pass."""
    st = os.stat(path)
    marker = completion_marker_path(path)
    payload = {"output": path, "size": st.st_size, "mtime": int(st.st_mtime),
               "marked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "host": socket.gethostname(),
               "job": os.environ.get("SLURM_JOB_ID", ""), "note": note}
    tmp = f"{marker}.tmp"
    with open(tmp, "w") as f:
        f.write(json.dumps(payload) + "\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, marker)
    return marker


def is_complete(path):
    """True iff `path` exists and its marker still describes it. Mirrors
    lib/resume_guard.sh rg_is_complete, including the tolerance for the older
    run_p4_unfold_std.sh receipts that predate the size/mtime binding."""
    marker = completion_marker_path(path)
    if not (os.path.exists(path) and os.path.exists(marker)):
        return False
    try:
        with open(marker) as f:
            m = json.load(f)
    except (json.JSONDecodeError, OSError):
        return False
    if "size" not in m and "mtime" not in m:
        return True
    st = os.stat(path)
    return m.get("size") == st.st_size and m.get("mtime") == int(st.st_mtime)


def _fsync_dir(dpath):
    """Persist the rename itself. Without this the directory entry can still be in
    flight after os.replace returns, so a node crash could lose a file whose data
    was already durable. Best-effort: not every filesystem permits opening a
    directory (and none of the correctness above depends on it)."""
    try:
        fd = os.open(dpath, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(fd)
    except OSError:
        pass
    finally:
        os.close(fd)


def atomic_write(path, writer, suffix="", overwrite=True, fsync=True, mark=False,
                 note=""):
    """Run `writer(tmp_path)` then atomically move the result onto `path`.

    writer     callable taking the temp path; must write exactly one file there.
    overwrite  False refuses to clobber an existing `path` (J10 asks for the
               no-clobber guard; a publication artifact should not be silently
               replaced by a re-run that was meant to go somewhere else).
    mark       also stamp the completion marker, LAST, so a marker always implies a
               fully renamed output and never the reverse.

    Returns the path actually written.
    """
    if not overwrite and os.path.exists(path):
        raise FileExistsError(
            f"[atomic_write] refusing to overwrite existing output: {path} "
            f"(pass overwrite=True if replacing it is intended)")
    dpath = os.path.dirname(os.path.abspath(path)) or "."
    os.makedirs(dpath, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".atomic_", suffix=suffix, dir=dpath)
    os.close(fd)
    try:
        writer(tmp)
        if fsync:
            with open(tmp, "rb") as f:
                os.fsync(f.fileno())
        os.replace(tmp, path)              # atomic within the filesystem
        if fsync:
            _fsync_dir(dpath)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)                 # interrupted: no partial survives at `path`
    if mark:
        mark_complete(path, note)
    return path


def atomic_savez_compressed(path, arrays, overwrite=True, fsync=True, mark=False,
                            note=""):
    """`np.savez_compressed` with the write made transactional.

    `arrays` is a dict, not **kwargs, so a key named `path`/`overwrite`/`mark` cannot
    collide with a parameter.

    numpy appends '.npz' to a filename that lacks it, and callers depend on that
    (launchers pass --out ending in .npz, but not universally). The suffix is
    normalized HERE, once, and the real destination returned, so the caller can
    report where the file actually landed instead of guessing.
    """
    if not path.endswith(".npz"):
        path = path + ".npz"

    def _write(tmp):
        # mkstemp gave us a '.npz'-suffixed temp, so numpy will not append again and
        # the name it writes is exactly the name we rename from.
        np.savez_compressed(tmp, **arrays)

    return atomic_write(path, _write, suffix=".npz", overwrite=overwrite, fsync=fsync,
                        mark=mark, note=note)

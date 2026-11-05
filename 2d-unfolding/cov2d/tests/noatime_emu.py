"""O_NOATIME for COV2D's own reads on a platform without it (macOS), so a clean run's guards can be tested silent there.

On Linux (os.O_NOATIME exists) nothing is patched: the kernel flag does the work, as on the cluster. Elsewhere each of
COV2D's O_NOATIME read helpers (``cov2d.stage_copy``, ``cov2d_receipt.read_noatime`` and ``open_noatime``,
``cov2d_pseudo_write.copy_noatime``) restores the file's atime when it is done, which is what the flag leaves. A plain
read (builtins.open, ROOT) is not emulated, so it moves atime as on the cluster's filesystems: the guards' fire tests
use exactly such a read. Both filesystems update atime on a fresh file's first plain read (relatime).
"""
from __future__ import annotations

import contextlib
import os
from unittest import mock

REAL = bool(getattr(os, "O_NOATIME", 0))


def _restore(path, atime_ns):
    os.utime(path, ns=(atime_ns, os.stat(path).st_mtime_ns))


def _restoring(fn):
    def wrapped(path, *a, **k):
        t = os.stat(path).st_atime_ns
        try:
            return fn(path, *a, **k)
        finally:
            _restore(path, t)
    return wrapped


class _File:
    """A file object that restores its file's atime when closed."""
    def __init__(self, fh, path, atime_ns):
        self._fh, self._path, self._t = fh, path, atime_ns

    def __getattr__(self, name):
        return getattr(self._fh, name)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def close(self):
        if not self._fh.closed:
            self._fh.close()
            _restore(self._path, self._t)


@contextlib.contextmanager
def emulated(*modules):
    """Patch the read helpers found in ``modules`` (cov2d, cov2d_receipt, cov2d_pseudo_write) unless O_NOATIME is real."""
    if REAL:
        yield
        return
    with contextlib.ExitStack() as st:
        for m in modules:
            for name in ("stage_copy", "read_noatime", "copy_noatime"):
                if hasattr(m, name):
                    st.enter_context(mock.patch.object(m, name, _restoring(getattr(m, name))))
            if hasattr(m, "open_noatime"):
                real = m.open_noatime
                st.enter_context(mock.patch.object(
                    m, "open_noatime", lambda p, _r=real: _File(_r(p), p, os.stat(p).st_atime_ns)))
        yield

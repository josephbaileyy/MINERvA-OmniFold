"""Prove which code a producer executed, and refuse before any output when that cannot be shown.

A digest of a file taken when the output is written says what is on disk then, not what ran. This
module therefore loads each repository module from bytes it has already hashed: the bytes that are
hashed are the bytes that are compiled and executed, so neither a later edit nor a stale ``.pyc``
can separate the record from the code. Every check raises ``ProvenanceRefusal``; callers run them
before reading inputs or opening an output.

A module is accepted only from inside ``root``, the checkout derived from the producer's own
``__file__``. A module of the same name that is already imported and was not loaded here (a
conflicting checkout on ``sys.path``, a ``sitecustomize``, an earlier import) is refused rather
than reused, because which bytes it executed is unknowable after the fact.

Residual, stated rather than hidden: the entry script itself is read by the interpreter before any
of this runs. Callers hash it as their first statement, which leaves the window between the
interpreter's read and that statement.
"""

import hashlib
import importlib.machinery
import json
import os
import platform
import subprocess
import sys
import types
from pathlib import Path

#: Exit status for a refusal, matching ``nd-unfolding/mnv_guarded_run.py``'s violation exit.
REFUSAL_EXIT = 3

#: Thread-count variables recorded with every run: thread count is part of the estimator.
THREAD_ENV = ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS",
              "SLURM_CPUS_PER_TASK")

#: Distributions whose versions identify the estimator backend. Read from metadata, never imported.
PACKAGES = ("numpy", "scikit-learn", "lightgbm", "xgboost", "scipy")

_MARK = "__mnv_verified__"


class ProvenanceRefusal(RuntimeError):
    """The executed code, the guard or an input could not be identified as required."""


def sha256_hex(data):
    return hashlib.sha256(data).hexdigest()


def git_blob_sha1(data):
    """The object id ``git hash-object`` gives these bytes."""
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def _inside(path, root):
    try:
        Path(path).resolve().relative_to(Path(root).resolve())
        return True
    except ValueError:
        return False


def file_record(path, data, root):
    path = Path(path).resolve()
    return {"path": str(path), "relpath": path.relative_to(Path(root).resolve()).as_posix(),
            "sha256": sha256_hex(data), "git_blob": git_blob_sha1(data)}


def self_record(path, root):
    """Hash the calling entry script; call it as the script's first statement."""
    return file_record(path, Path(path).read_bytes(), root)


def load_verified(name, path, root, expect_sha256=None):
    """Execute module ``name`` from the bytes of ``path`` and register it in ``sys.modules``.

    Returns ``(module, record)``. Refuses when ``path`` is outside ``root``, when the digest differs
    from ``expect_sha256``, or when ``name`` is already imported from anything but this loader.
    """
    path = Path(path).resolve()
    if not _inside(path, root):
        raise ProvenanceRefusal(f"{name}: {path} is outside the admitted checkout {root}")
    existing = sys.modules.get(name)
    if existing is not None:
        mark = getattr(existing, _MARK, None)
        if mark is not None and mark["path"] == str(path) and \
                (expect_sha256 is None or mark["sha256"] == expect_sha256):
            return existing, dict(mark)
        origin = getattr(existing, "__file__", None)
        raise ProvenanceRefusal(
            f"{name} was already imported from {origin!r} before this producer could load "
            f"{path}; which bytes it executed cannot be established")
    data = path.read_bytes()
    record = file_record(path, data, root)
    if expect_sha256 is not None and record["sha256"] != expect_sha256:
        raise ProvenanceRefusal(f"{name}: {path} has sha256 {record['sha256']}, "
                                f"expected {expect_sha256}")
    module = types.ModuleType(name)
    module.__file__ = str(path)
    module.__spec__ = importlib.machinery.ModuleSpec(name, None, origin=str(path))
    module.__loader__ = None
    code = compile(data, str(path), "exec", dont_inherit=True)
    sys.modules[name] = module
    try:
        exec(code, module.__dict__)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    setattr(module, _MARK, dict(record))
    return module, record


def require_inside(root, modules):
    """Refuse unless every module in ``{name: module}`` was loaded from a file inside ``root``."""
    for name, module in modules.items():
        origin = getattr(module, "__file__", None)
        if not origin or not _inside(origin, root):
            raise ProvenanceRefusal(f"{name} resolved to {origin!r}, outside {root}")


def bootstrap_record(module, root):
    """Record a module that had to be imported normally (this one, before it could verify)."""
    require_inside(root, {module.__name__: module})
    return file_record(module.__file__, Path(module.__file__).read_bytes(), root)


def guard_state():
    """The ``mnv_guarded_run.py`` finder installed in this interpreter, if any.

    Matched by type name, as the guard matches itself: its propagated half loads a second copy of
    the module, so ``isinstance`` would answer False across that boundary.
    """
    for finder in sys.meta_path:
        if type(finder).__name__ == "GuardedPathFinder":
            return {"installed": True, "expect_root": getattr(finder, "expect_root", None),
                    "allowed": sorted(getattr(finder, "allowed", ())),
                    "depth": getattr(finder, "depth", None),
                    "propagation": getattr(finder, "propagation", None)}
    return {"installed": False, "expect_root": None, "allowed": [], "depth": None,
            "propagation": None}


def require_guard(root, state=None):
    """Refuse unless the guard enforces exactly ``root``, with no ``--allow`` tree."""
    state = guard_state() if state is None else state
    want = str(Path(root).resolve())
    if not state["installed"]:
        raise ProvenanceRefusal("not running under nd-unfolding/mnv_guarded_run.py")
    if state["expect_root"] != want:
        raise ProvenanceRefusal(f"the guard enforces {state['expect_root']}, not {want}")
    if state["allowed"] != [want]:
        raise ProvenanceRefusal(f"the guard also allows {sorted(set(state['allowed']) - {want})}")
    return state


def git_identity(root, records):
    """HEAD of ``root`` and whether each executed file's bytes are HEAD's blob at its path.

    ``git`` runs with every ``GIT_*`` variable removed: ``GIT_DIR`` or ``GIT_WORK_TREE`` would answer
    for another repository than ``-C`` names, and the program-running ones (``GIT_EDITOR``,
    ``GIT_EXTERNAL_DIFF``, ...) are refused by the guard and needed by neither command.
    """
    root = str(Path(root).resolve())
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    try:
        head = subprocess.run(["git", "-C", root, "rev-parse", "HEAD"], capture_output=True,
                              text=True, check=True, env=env).stdout.strip()
        listing = subprocess.run(["git", "-C", root, "ls-tree", "-z", "HEAD", "--"] +
                                 [r["relpath"] for r in records],
                                 capture_output=True, text=True, check=True,
                                 env=env).stdout if records else ""
    except (OSError, subprocess.CalledProcessError) as exc:
        return {"status": f"unavailable: {exc}", "commit": None, "mismatched": None}
    at_head = {}
    for entry in filter(None, listing.split("\0")):
        meta, rel = entry.split("\t", 1)
        at_head[rel] = meta.split()[2]
    mismatched = sorted(r["relpath"] for r in records if at_head.get(r["relpath"]) != r["git_blob"])
    return {"status": "ok", "commit": head, "mismatched": mismatched}


def input_record(path, expect_sha256=None, hash_bytes=False):
    """Path, size and mtime of an input; its sha256 when asked or when a digest is expected."""
    path = Path(path).resolve()
    st = path.stat()
    rec = {"path": str(path), "size": st.st_size, "mtime_ns": st.st_mtime_ns, "sha256": None}
    if hash_bytes or expect_sha256 is not None:
        h = hashlib.sha256()
        with open(path, "rb") as fh:
            for block in iter(lambda: fh.read(1 << 22), b""):
                h.update(block)
        rec["sha256"] = h.hexdigest()
        if expect_sha256 is not None and rec["sha256"] != expect_sha256:
            raise ProvenanceRefusal(f"input {path} has sha256 {rec['sha256']}, "
                                    f"expected {expect_sha256}")
    return rec


def environment_record():
    from importlib import metadata
    versions = {}
    for name in PACKAGES:
        try:
            versions[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            versions[name] = None
    root_mod = sys.modules.get("ROOT")
    return {"python": sys.version.split()[0], "executable": sys.executable,
            "host": platform.node(), "argv": list(sys.argv),
            "threads": {k: os.environ.get(k) for k in THREAD_ENV}, "packages": versions,
            "root_version": root_mod.gROOT.GetVersion() if root_mod is not None else None}


def refuse_existing(path):
    """Refuse to write over an existing output."""
    if os.path.lexists(path):
        raise ProvenanceRefusal(f"output {path} already exists; refusing to overwrite it")


def load_expectations(path):
    """An expectation file: ``{"commit", "modules": {relpath: sha256}, "inputs": {key: sha256}}``."""
    if path is None:
        return {"commit": None, "modules": {}, "inputs": {}}
    exp = json.loads(Path(path).read_text())
    unknown = set(exp) - {"commit", "modules", "inputs", "note"}
    if unknown:
        raise ProvenanceRefusal(f"expectation file {path} has unknown keys {sorted(unknown)}")
    return {"commit": exp.get("commit"), "modules": dict(exp.get("modules", {})),
            "inputs": dict(exp.get("inputs", {}))}


def finalize(root, records, expectations, strict):
    """Check executed files against HEAD and the expectations; return the identity record.

    Always refuses on a contradiction (a stated commit or digest that does not match). In
    ``strict`` mode it also refuses when something is merely unknown: no guard, git unavailable,
    an executed file that is not HEAD's blob, or an executed module with no stated digest.
    """
    ident = git_identity(root, records)
    by_rel = {r["relpath"]: r for r in records}
    for rel, want in expectations["modules"].items():
        if rel not in by_rel:
            raise ProvenanceRefusal(f"expected module {rel} was not executed")
        if by_rel[rel]["sha256"] != want:
            raise ProvenanceRefusal(f"{rel} executed with sha256 {by_rel[rel]['sha256']}, "
                                    f"expected {want}")
    if expectations["commit"] is not None and ident["commit"] != expectations["commit"]:
        raise ProvenanceRefusal(f"checkout is at {ident['commit']}, expected "
                                f"{expectations['commit']}")
    guard = guard_state()
    if strict:
        require_guard(root, guard)
        if ident["status"] != "ok":
            raise ProvenanceRefusal(f"implementation commit unavailable: {ident['status']}")
        if ident["mismatched"]:
            raise ProvenanceRefusal(f"executed bytes differ from HEAD {ident['commit']}: "
                                    f"{ident['mismatched']}")
        missing = sorted(set(by_rel) - set(expectations["modules"]))
        if expectations["commit"] is None or missing:
            raise ProvenanceRefusal("strict provenance needs a stated commit and a digest for "
                                    f"every executed module; missing {missing or ['commit']}")
    return {"guard": guard, "git": ident, "executed": records, "strict": bool(strict)}

"""Install the OI-136 import guard in inheriting Python child processes."""
from __future__ import annotations

import atexit
import hashlib
import importlib.util
import os
import pathlib
import sys


def _load_guard(module_path: str):
    """Load the guard from its parent-recorded absolute path."""
    module_name = f"_mnv_guarded_run_propagated_{os.getpid()}"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load OI-136 guard module at {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _sha256(path: pathlib.Path) -> str:
    """Return the digest of the shim bytes that installed this child guard."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _verify_guard_location(module_path: str, expect_root: str) -> pathlib.Path:
    """Refuse a propagated guard module outside the expected checkout."""
    module = pathlib.Path(module_path).resolve()
    root = pathlib.Path(expect_root).resolve()
    try:
        module.relative_to(root)
    except ValueError:
        print(
            "[oi136 child] GUARD MODULE OUTSIDE EXPECTED ROOT -- REFUSING STARTUP.\n"
            f"[oi136 child]   module        {module}\n"
            f"[oi136 child]   expected      {root}",
            file=sys.stderr,
            flush=True,
        )
        os._exit(3)
    if not module.is_file():
        raise RuntimeError(f"cannot read OI-136 guard module at {module}")
    return module


def _script_path() -> str | None:
    """Return the child script path when this interpreter is running a file."""
    if not sys.argv or not sys.argv[0] or sys.argv[0].startswith("-"):
        return None
    script = pathlib.Path(sys.argv[0])
    return str(script.resolve()) if script.is_file() else None


def _path_without_shim(shim_dir: pathlib.Path) -> list[str]:
    """Return sys.path without entries resolving to this shim directory."""
    remaining = []
    for entry in sys.path:
        try:
            resolved = pathlib.Path(entry or os.curdir).resolve()
        except OSError:
            resolved = None
        if resolved != shim_dir:
            remaining.append(entry)
    return remaining


def _run_existing_sitecustomize(guard, shim_dir: pathlib.Path) -> None:
    """Execute the next importable sitecustomize after the guard is installed."""
    spec = guard.find_spec("sitecustomize", _path_without_shim(shim_dir))
    if spec is None or spec.loader is None:
        return
    origin = getattr(spec, "origin", None)
    guard.chained_sitecustomize.update(found=True, origin=origin)

    current = sys.modules.get("sitecustomize")
    module = importlib.util.module_from_spec(spec)
    sys.modules["sitecustomize"] = module
    try:
        spec.loader.exec_module(module)
        guard.chained_sitecustomize["executed"] = True
    finally:
        if current is None:
            sys.modules.pop("sitecustomize", None)
        else:
            sys.modules["sitecustomize"] = current


def _install() -> None:
    """Install propagation when the parent supplied the complete environment contract."""
    module_path = os.environ.get("MNV_GUARD_MODULE")
    expect_root = os.environ.get("MNV_GUARD_EXPECT_ROOT")
    if not module_path or not expect_root:
        return

    verified_module = _verify_guard_location(module_path, expect_root)
    guard_module = _load_guard(str(verified_module))
    allow_text = os.environ.get("MNV_GUARD_ALLOW", "")
    allow = [path for path in allow_text.split(os.pathsep) if path]
    inventory = os.environ.get("MNV_GUARD_INVENTORY") or None
    script = _script_path()
    guard = guard_module.install(expect_root, allow)
    guard.shim_sha256 = _sha256(pathlib.Path(__file__).resolve())
    emitted = False

    def emit_child_inventory() -> None:
        nonlocal emitted
        if emitted:
            return
        emitted = True
        violation = guard.violation
        if guard.launch_refusal is not None:
            outcome = "refused:launch-python-startup-flags"
            site = guard_module.SITE_LAUNCH
        elif violation is not None:
            outcome = "refused:import-tree-violation"
            site = guard_module.SITE_IMPORT_RESOLUTION
        else:
            outcome = "propagated-child-exit-unobserved"
            site = guard_module.SITE_NONE
        guard_module._safe_inventory(
            inventory,
            guard,
            script,
            expect_root,
            allow,
            outcome,
            violation,
            site=site,
        )
        guard_module._emit_inventory(expect_root, violation)

    atexit.register(emit_child_inventory)
    guard.on_violation = emit_child_inventory
    _run_existing_sitecustomize(guard, pathlib.Path(__file__).resolve().parent)


try:
    _install()
except SystemExit:
    raise
except BaseException as exc:
    print(
        f"[oi136 child] COULD NOT INSTALL SUBPROCESS GUARD: {exc!r}",
        file=sys.stderr,
        flush=True,
    )
    os._exit(2)

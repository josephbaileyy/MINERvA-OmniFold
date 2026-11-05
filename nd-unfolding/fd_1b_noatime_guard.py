#!/usr/bin/env python3
"""1B's guarded launcher (the director's ruling of 2026-11-05, after REF-G1's plain reads moved 419 of 1B's input
atimes): an audit hook that refuses any open of a path under a declared input root unless it carries O_NOATIME, and
a launcher that installs it before running a job's entry script.

    python3 -B fd_1b_noatime_guard.py --declared [--root R ...] -- ENTRY.py [ARGS ...]

``--declared`` means ROOTS below, so every job line names the one list (and a bash job script, which cannot import
it, still passes it statically); ``--root R`` adds a root. At least one root is required.

The hook (``sys.addaudithook`` on the "open" event, which builtins.open, io.open, os.open, np.load and np.memmap all
raise) is permanent for the process: nothing the entry script imports can remove it. A plain read under a root
raises PermissionError, which the entry scripts' own handlers report as a refusal. Paths are compared after
os.path.realpath on both sides, so a symlink or a relative path cannot step around a root.

It lives outside fd_1b_c2.gate_code_digests() on purpose: putting it in fd_1b_mc or fd_1b_c2 would change the code
the calibration and c2check are bound to. Binding 3 binds it by sha256, and the scan in tests/test_fd_1b_guard.py
requires every binding-3 job line that runs fd_1b_mc, fd_1b_c2 or fd_1b_binning to come through it.

ROOTS below are 1B's declared pscratch inputs. They are the defaults the stage 1 generator and binding 3's job
scripts pass, and one list for the scan and the tests.
"""
from __future__ import annotations

import os
import runpy
import sys

P = "/pscratch/sd/j/josephrb"
ROOTS = (f"{P}/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware",        # the bank
         f"{P}/s5p-20260926/bank_detector",                                   # the detector dump
         f"{P}/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz",               # the inputs
         f"{P}/s5c-20260924/runs/p2/bkg_dump.npz",                            # the background
         f"{P}/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints",   # the flux constraint
         f"{P}/fd-1b-inv-20261101/i0/in",                                     # S1 staged
         f"{P}/fd-1b-staged-20261102/stage1/in",                              # the staged flux-universe arrays
         f"{P}/fd-1b-20261030/pins.json", f"{P}/fd-f1-20261027/f1b3/prep",
         f"{P}/fd-1b-a21-cvdenom2-20261103")
MARK = "fd_1b_noatime_guard"


def refuses(path, flags: int, roots: tuple, noatime: int) -> bool:
    """Whether an open of ``path`` with ``flags`` is refused: it resolves under a root and lacks the noatime bit."""
    if isinstance(path, int) or path is None:                 # an existing descriptor: its open was judged already
        return False
    p = os.path.realpath(os.fsdecode(path))
    under = any(p == r or p.startswith(r.rstrip(os.sep) + os.sep) for r in roots)
    return under and not (flags & noatime)


def install(roots, noatime: int | None = None) -> None:
    """Add the hook over ``roots``. ``noatime`` is os.O_NOATIME; it may be given only where that flag does not exist
    (the tests on macOS pass a harmless stand-in bit). Refuses to install without a flag, as fd_1b_inv refuses a
    plain read, and refuses an empty root list."""
    flag = getattr(os, "O_NOATIME", None) if noatime is None else noatime
    if not flag:
        raise SystemExit(f"{MARK}: O_NOATIME is not available here: refusing to run unguarded")
    rs = tuple(os.path.realpath(r) for r in roots)
    if not rs:
        raise SystemExit(f"{MARK}: no declared roots: refusing to run unguarded")

    def hook(event, args):
        if event == "open" and refuses(args[0], args[2] if len(args) > 2 and args[2] is not None else 0, rs, flag):
            raise PermissionError(f"{MARK}: a plain open of a declared input refused: {os.fsdecode(args[0])} "
                                  f"(read it through O_NOATIME)")
    sys.addaudithook(hook)


def main(argv: list[str]) -> None:
    if "--" not in argv:
        raise SystemExit(f"usage: {MARK}.py --declared [--root R ...] -- ENTRY.py [ARGS ...]")
    cut = argv.index("--")
    opts, rest = argv[:cut], argv[cut + 1:]
    roots, i = [], 0
    while i < len(opts):
        if opts[i] == "--declared":
            roots += list(ROOTS)
            i += 1
        elif opts[i] == "--root" and i + 1 < len(opts):
            roots.append(opts[i + 1])
            i += 2
        else:
            raise SystemExit(f"{MARK}: unknown or incomplete option {opts[i]!r}")
    if not rest:
        raise SystemExit(f"{MARK}: no entry script after --")
    install(roots)
    print(f"{MARK}: installed over {len(roots)} roots; running {rest[0]}", file=sys.stderr, flush=True)
    sys.argv = rest
    sys.path[0] = os.path.dirname(os.path.realpath(rest[0]))
    runpy.run_path(rest[0], run_name="__main__")


if __name__ == "__main__":
    main(sys.argv[1:])

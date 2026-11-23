#!/usr/bin/env python3
"""Line tracer for msr_project.py: run test_msr under sys.settrace and list every executable line that never ran.

    python3 nd-unfolding/msr/trace_msr_project.py        (exit 0 only if every executable line ran and the tests pass)
"""
from __future__ import annotations

import sys
import types
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = str((HERE / "msr_project.py").resolve())
sys.path.insert(0, str(HERE))


def executable_lines(path: str) -> set[int]:
    code = compile(Path(path).read_text(), path, "exec")
    lines: set[int] = set()

    def walk(co: types.CodeType):
        lines.update(ln for _, _, ln in co.co_lines() if ln is not None)
        for c in co.co_consts:
            if isinstance(c, types.CodeType):
                walk(c)
    walk(code)
    return lines


def main() -> int:
    hit: set[int] = set()

    def tracer(frame, event, arg):
        if frame.f_code.co_filename == TARGET:
            if event == "line":
                hit.add(frame.f_lineno)
            return tracer
        return tracer if event == "call" and frame.f_code.co_filename == TARGET else None

    def global_tracer(frame, event, arg):
        if frame.f_code.co_filename == TARGET:
            hit.add(frame.f_lineno)
            return tracer
        return None

    sys.modules.pop("msr_project", None)
    sys.settrace(global_tracer)
    import msr_project  # noqa: F401  (module-level lines are traced here)
    import test_msr
    suite = unittest.defaultTestLoader.loadTestsFromModule(test_msr)
    result = unittest.TextTestRunner(verbosity=0).run(suite)
    sys.settrace(None)
    allx = executable_lines(TARGET)
    src = Path(TARGET).read_text().splitlines()
    missed = sorted(ln for ln in allx - hit if src[ln - 1].strip() and not src[ln - 1].strip().startswith(("#", '"""')))
    print(f"executable lines {len(allx)}; executed {len(allx & hit)}; not executed {len(missed)}")
    for ln in missed:
        print(f"  {ln}: {src[ln - 1].strip()}")
    return 0 if (not missed and result.wasSuccessful()) else 1


if __name__ == "__main__":
    sys.exit(main())

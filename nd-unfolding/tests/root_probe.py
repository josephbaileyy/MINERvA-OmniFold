"""One definition of "is PyROOT actually available", because there were two and both were wrong.

**Why this exists.** Several suites install a minimal `sys.modules["ROOT"]` stub so that a module
importing ROOT can be loaded without PyROOT. Two of them do it at MODULE IMPORT time -- i.e. during
pytest collection -- and never remove it, so in a whole-directory run **whichever test module loads
first decides what every later module sees**. The stubs carry two attributes; real PyROOT has
thousands.

Every ROOT-gated test then asked the wrong question, in two different wrong ways:

    test_z_pilot.py    try: import ROOT ... HAVE_ROOT = True     # a stub satisfies this
    test_z_build.py    skipUnless(importlib.util.find_spec("ROOT"), ...)   # and this

Measured on 2026-09-21, on a host with no PyROOT at all:

| run | result |
|---|---|
| `pytest tests/test_z_pilot.py` | 53 passed, **4 skipped** |
| `pytest tests/test_nd_branch_binding_fails_closed.py tests/test_z_pilot.py` | **4 failed** |
| `pytest tests/test_z_build.py` | 22 passed, **2 skipped** |
| the same file after any stub installer | **2 failed** |

In each case the tests that failed are exactly the ones that had skipped: the guard let them run
against a two-attribute fake. **The failure is order-dependent, so per-file runs are green and the
whole-directory run is red** -- the shape where a suite is green in the way people check it and red
in the way CI would.

**The predicate.** A stub is MARKED with `__mnv_stub__`, and this asks for a module that is present
and unmarked. An UNMARKED stub therefore reads as real, which is the deliberate direction: a new
stub that forgets the marker makes the gated tests RUN and fail loudly, rather than skip silently.
A guard whose failure mode is a silent skip cannot be trusted to be measuring anything.
"""
import importlib.util
import sys


def have_real_pyroot() -> bool:
    """True only for genuine PyROOT. See the module docstring for why `import ROOT` is not enough."""
    if "ROOT" in sys.modules:
        module = sys.modules["ROOT"]
        # A teardown that restores an absent entry writes None, and `import ROOT` then raises
        # rather than yielding a module. Present-but-None is not availability.
        if module is None:
            return False
        return not getattr(module, "__mnv_stub__", False)
    try:
        return importlib.util.find_spec("ROOT") is not None
    except (ImportError, ValueError):
        # ValueError is the `__spec__ is None` case -- a stub installed without a spec, which is
        # the defect this module's docstring opens with.
        return False

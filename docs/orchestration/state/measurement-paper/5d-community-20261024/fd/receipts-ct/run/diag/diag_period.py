#!/usr/bin/env python3
"""5A leak-guard diagnostic, authorized once by the director's ruling of 2026-10-29 (option (a)): import the deployed
pinned fd_ct_readers in-process (no edit, no copy), build the period readout in memory with the bound inputs, and run
the guard. Print ONLY: the JSON key paths of offending numbers, the forbidden-table entry each matched BY ROLE, and the
cells where |X_sup/f - 1| < LEAK_REL. No numeric value is printed and no readout is written.

    env -u PYTHONPATH <root_6_28 python3> -I -B diag_period.py <deploy dir> <period argv ...>
"""
import contextlib
import io
import sys
from pathlib import Path

D = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(D / "nd-unfolding"))
import numpy as np  # noqa: E402
import fd_ct_readers as ct  # noqa: E402
import fd_f0_regrade as f0  # noqa: E402

ARGV = sys.argv[2:]
out = Path(ARGV[ARGV.index("--out-json") + 1])
assert not out.exists(), "the diagnostic's --out-json must not exist"
print(f"module {Path(ct.__file__).resolve()}  sha256 {ct.sa.sha256(Path(ct.__file__).resolve())}")
X_NAMES = ("prior integral X_p", "central X_sup", "prior X_sup")   # run_period's LeakGuard(f, [U @ xp, *partial]) order
state = {}
orig_init = f0.LeakGuard.__init__


def init(self, f, integrals):
    orig_init(self, f, integrals)
    f = np.asarray(f, float)
    X = [np.asarray(a, float) for a in integrals]
    assert len(X) == 3, f"expected 3 integral rows, got {len(X)}"
    rows = [("f", f)]
    with np.errstate(divide="ignore", invalid="ignore"):
        for n, x in zip(X_NAMES, X):
            rows += [(n, x), (f"f - {n}", f - x), (f"f/{n}", f / x), (f"{n}/f", x / f), (f"f/{n} - 1", f / x - 1),
                     (f"{n}/f - 1", x / f - 1)]
    self._roles = [(name, c, abs(float(v[c]))) for name, v in rows for c in range(len(f))
                   if np.isfinite(v[c]) and v[c] != 0]
    state["f"], state["X"] = f, X


def roles(self, a, cell):
    a = abs(float(a))
    if not np.isfinite(a) or a == 0:
        return []
    hits = [f"{n} cell R{c:02d}" for n, c, t in self._roles
            if (cell is None or c == cell) and abs(a - t) <= f0.LEAK_REL * t]
    if a < f0.LEAK_FLOOR:
        hits.append("below the 1e-30 floor")
    return hits


def walk(self, obj, path, found):
    """Mirrors LeakGuard.count's traversal, recording path and matched roles instead of a count."""
    if isinstance(obj, str):
        for k, tok in enumerate(f0._NUM.findall(obj)):
            h = roles(self, float(tok), None)
            if h:
                found.append((f"{path} (string, number token #{k})", h))
        return
    if isinstance(obj, bool) or obj is None:
        return
    if isinstance(obj, (int, float, np.floating, np.integer)):
        h = roles(self, obj, None)
        if h:
            found.append((path, h))
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            walk(self, k, f"{path}.<key {k}>", found)
            walk(self, v, f"{path}.{k}", found)
        return
    if isinstance(obj, (list, tuple)) and not all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in obj):
        for i, x in enumerate(obj):
            walk(self, x, f"{path}[{i}]", found)
        return
    a = np.asarray(obj, float)
    if a.ndim >= 1 and a.shape[-1] == f0.N_CELLS:
        for idx in np.ndindex(a.shape):
            h = roles(self, a[idx], idx[-1])
            if h:
                found.append((f"{path}{list(idx)}", h))
    else:
        for idx in np.ndindex(a.shape):
            h = roles(self, a[idx], None)
            if h:
                found.append((f"{path}{list(idx)}", h))


def P(*a):
    print(*a, file=sys.__stdout__, flush=True)


def check(self, what, obj):
    found = []
    walk(self, obj, what, found)
    P(f"guard check of '{what}': {len(found)} offending number(s); tool's own count {self.count(obj)}")
    for p, h in found:
        P(f"  OFFENDING {p}: matches {sorted(set(h))}")
    f, X = state["f"], state["X"]
    with np.errstate(divide="ignore", invalid="ignore"):
        for n, x in zip(X_NAMES, X):
            near = [f"R{c:02d}" for c in range(len(f)) if np.isfinite(x[c]) and abs(x[c] / f[c] - 1) < f0.LEAK_REL]
            masked = [f"R{c:02d}" for c in range(len(f)) if not np.isfinite(x[c])]
            P(f"  {n}: cells with |X/f - 1| < LEAK_REL: {near}; cells masked (NaN): {masked}")
    P("diagnostic ends here: no readout written")
    raise SystemExit(3)


f0.LeakGuard.__init__ = init
f0.LeakGuard.check = check
tool_out, tool_err = io.StringIO(), io.StringIO()
try:
    with contextlib.redirect_stdout(tool_out), contextlib.redirect_stderr(tool_err):
        rc = ct.main(ARGV)
except SystemExit as e:
    rc = e.code
print(f"tool exit {rc}; controls that printed PASS: {sum(1 for l in tool_out.getvalue().splitlines() if l.startswith('PASS'))}; "
      f"tool stderr lines: {len(tool_err.getvalue().splitlines())}")
print(f"--out-json exists after: {out.exists()}")

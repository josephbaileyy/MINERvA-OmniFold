#!/usr/bin/env python3
"""Reviewer: exact-reciprocal sensitivity and N2 reserve, reusing my rc_assurance functions."""
import importlib.util, sys
spec = importlib.util.spec_from_file_location("rca", sys.argv[1]); m = importlib.util.module_from_spec(spec)
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    spec.loader.exec_module(m)
for x in (1.15, 1.20, 1.25, 4 / 3, 1.33, 1.5):
    e = m.edges_for((1 / x, x), ["I68", "I95"])
    print(round(x, 4), m.req_n(["I68", "I95"], e, m.ALPHA_COV, 0.10), m.req_n(["I68"], {"I68": e["I68"]}, 0.04 / 206, 0.10))
n2 = 100 * 7.075833333 / 100 * 1.05
print("N2", n2, (n2 + 0.4), (n2 + 2.3), (n2 + 0.4) / 0.8, (n2 + 2.3) / 0.8)

#!/usr/bin/env python3
"""Reviewer re-derivation of C's E_C branch (repair 1) from C's stated operands; own code.
Operands: c_cv (exact) 0.68 / 69523/3600; universe rate 0.132419 (opt, = 0.059147*2.2388) / 0.5 (cons);
overhead 1.0/1.5; extraction 0.01/0.05; retry 0.02/0.10; verification 0.05/0.10; reserve 0.20; dev 6.
S-a dropped (exact sweep replaces it)."""
import json
io = 0.5 / (804 / 3600)
out = {"io_ratio": io}
for name, cv, uni, ovh, ext, rr, vf, cons in (
        ("optimistic", 0.68, 0.059147 * io, 1.0, 0.01, 0.02, 0.05, False),
        ("conservative", 69523 / 3600, 0.5, 1.5, 0.05, 0.10, 0.10, True)):
    setup = {"S-r": 12 * (24 if cons else 2.5) * 24 / 256, "S-a": 0.0,
             "S-b": (120 * 5 * 8 / 256 if cons else 0) + 10 * uni, "S-d": 20 if cons else 2,
             "S-e": 300 * cv if cons else 0, "S-f": 200 * cv, "S-j": 3 * 202 * cv * ovh}
    S = sum(setup.values())
    prod = 5000 * (cv * ovh + ext)
    sub = S + 6 + prod + vf * (prod + S) + rr * (prod + S + 6)
    rebuild = 187 * cv * io + 11 * cv
    out[name] = dict(setup=setup, setup_sum=S, production=prod, p2_admitted=sub / 0.8,
                     rebuild=rebuild, total=sub / 0.8 + rebuild / 0.8)
print(json.dumps(out, indent=1))

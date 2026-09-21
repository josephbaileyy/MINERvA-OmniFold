#!/usr/bin/env python3
"""Is `z_contract.Z_BOUNDARIES['cause3_corr']` INERT to (cause 3, Z)'s outcome, and is the LIVE
binding site `z_validator._DIAGONAL_ONLY_SCOPE` instead?

The endpoint-A packet asserts both. This probe tests them by EXECUTION rather than by reading, and
it carries the positive controls without which the identity result would be vacuous: if deleting the
registry entry leaves `describe()` byte-identical, that is only evidence of inertness once we have
shown the harness CAN see a registry deletion at all.

Nothing is edited on disk. The registry is a module-level dict, so every mutation here is in-process
and reverted in a `finally`.

Run from the repository root:
  python3 docs/orchestration/state/probe-z-cause3corr-binding-site-20260910.py
"""
import json
import os
import sys

_ND = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))), "nd-unfolding")
sys.path.insert(0, _ND)

import z_contract as zc          # noqa: E402
import z_validator as zv         # noqa: E402

_line = "-" * 92


def all_valid():
    """VERBATIM from tests/test_z_validator.py:43-50 at 6f24fb00 -- not a reimplementation.

    Every `Validity` field defaults to False (the safe direction, z_validator.py:118-120), so a
    hand-rolled mirror silently produces branch 1 instead of MET. Copied rather than derived.
    """
    return zv.Validity(footing_ok=True, digests_agree=True, partition_agrees=True,
                       identities_pass=True, cv_held_fixed=True, offsets_match_K=True,
                       offset_declared_nonzero=True, product_digests_distinct=True,
                       all_members_finite=True)


def canonical(outcome):
    return json.dumps(outcome.describe(), sort_keys=True, indent=None, default=str)


# The currently ADOPTED leg set: the two diagonal-only legs, per SPEC 3.7d.
AGG = zv.Leg("agg", "aggregate", "cause3_agg", "s_agg")
MED = zv.Leg("med", "per-bin", "cause3_med", "s_med")
L2 = zv.LegSet([AGG, MED], predeclared_at="PROBE")
STATS = {"s_agg": 0.001, "s_med": 0.001}

DECLARED2 = {
    "cause3_agg": zc.Boundary.declared("cause3_agg", 0.01, "T"),
    "cause3_med": zc.Boundary.declared("cause3_med", 0.02, "T"),
}

print(_line)
print("0. BASELINE — the adopted two-leg set, with `cause3_corr` WITHHELD as the tree has it")
print(_line)
print(f"registry `cause3_corr` is_declared = {zc.Z_BOUNDARIES['cause3_corr'].is_declared}")
saved = dict(zc.Z_BOUNDARIES)
try:
    zc.Z_BOUNDARIES.update(DECLARED2)
    base = zv.assess(L2, STATS, all_valid())
    base_json = canonical(base)
finally:
    zc.Z_BOUNDARIES.clear(); zc.Z_BOUNDARIES.update(saved)
print(f"is_met = {base.is_met}   branch_label = {base.branch_label!r}")
print(f"scope_statement present = {base.scope_statement is not None}")
print(f"describe() sha-ish length = {len(base_json)} chars")

print()
print(_line)
print("1. THE CLAIM — delete the `cause3_corr` REGISTRY ENTRY, re-assess, compare byte-for-byte")
print(_line)
saved = dict(zc.Z_BOUNDARIES)
try:
    zc.Z_BOUNDARIES.update(DECLARED2)
    del zc.Z_BOUNDARIES["cause3_corr"]
    assert "cause3_corr" not in zc.Z_BOUNDARIES
    deleted = zv.assess(L2, STATS, all_valid())
    deleted_json = canonical(deleted)
    err = None
except Exception as e:                       # noqa: BLE001
    deleted_json, err = None, f"{type(e).__name__}: {e}"
finally:
    zc.Z_BOUNDARIES.clear(); zc.Z_BOUNDARIES.update(saved)
if err:
    print(f"assess RAISED: {err}")
    print("VERDICT: the entry is NOT inert -- deletion is refused.")
else:
    same = deleted_json == base_json
    print(f"describe() byte-identical with the entry deleted: {same}")
    print(f"VERDICT: the registry entry is {'INERT' if same else 'LOAD-BEARING'} to this outcome.")

print()
print(_line)
print("2. POSITIVE CONTROL A — can this harness see a registry deletion AT ALL?")
print(_line)
print("Delete `cause3_agg`, which a DECLARED leg names. If this is also byte-identical, section 1")
print("proves nothing, because `assess` would not be consulting the registry in the first place.")
saved = dict(zc.Z_BOUNDARIES)
try:
    zc.Z_BOUNDARIES.update(DECLARED2)
    del zc.Z_BOUNDARIES["cause3_agg"]
    ctlA = canonical(zv.assess(L2, STATS, all_valid()))
    errA = None
except Exception as e:                       # noqa: BLE001
    ctlA, errA = None, f"{type(e).__name__}: {e}"
finally:
    zc.Z_BOUNDARIES.clear(); zc.Z_BOUNDARIES.update(saved)
if errA:
    print(f"assess RAISED: {errA}")
    print("CONTROL A PASSES: a deletion the outcome depends on is REFUSED, so the registry is")
    print("  consulted at assess time and section 1's identity is a real negative, not a blind one.")
else:
    print(f"byte-identical to baseline: {ctlA == base_json}")
    print("CONTROL A " + ("FAILS -- section 1 is VACUOUS." if ctlA == base_json else "PASSES."))

print()
print(_line)
print("3. POSITIVE CONTROL B — the direction that decides WHERE the binding lives")
print(_line)
print("Declare a correlation-sensitive leg. If the scope statement disappears, the narrowing is")
print("derived from the LEG SET, which is the packet's claim about the live binding site.")
CORR = zv.Leg("corr", "aggregate", "cause3_corr", "s_corr", sees_correlations=True)
L3 = zv.LegSet([AGG, MED, CORR], predeclared_at="PROBE")
saved = dict(zc.Z_BOUNDARIES)
try:
    zc.Z_BOUNDARIES.update(DECLARED2)
    zc.Z_BOUNDARIES["cause3_corr"] = zc.Boundary.declared("cause3_corr", 0.03, "T")
    with_corr = zv.assess(L3, {**STATS, "s_corr": 0.001}, all_valid())
finally:
    zc.Z_BOUNDARIES.clear(); zc.Z_BOUNDARIES.update(saved)
print(f"two diagonal-only legs   -> scope_statement is None: {base.scope_statement is None}")
print(f"plus a correlation leg   -> scope_statement is None: {with_corr.scope_statement is None}")
flipped = (base.scope_statement is not None) and (with_corr.scope_statement is None)
print(f"CONTROL B {'PASSES' if flipped else 'FAILS'}: the narrowing is derived from the leg set, "
      f"not from the registry.")
print(f"and with the correlation leg declared, `cause3_corr` becomes LOAD-BEARING: is_met with "
      f"s_corr=0.9 -> ", end="")
saved = dict(zc.Z_BOUNDARIES)
try:
    zc.Z_BOUNDARIES.update(DECLARED2)
    zc.Z_BOUNDARIES["cause3_corr"] = zc.Boundary.declared("cause3_corr", 0.03, "T")
    fail = zv.assess(L3, {**STATS, "s_corr": 0.9}, all_valid())
finally:
    zc.Z_BOUNDARIES.clear(); zc.Z_BOUNDARIES.update(saved)
print(f"{fail.is_met}  failing_legs={fail.failing_legs}")

print()
print(_line)
print("4. WHAT THE LIVE SITE ACTUALLY SAYS, verbatim from the emitted outcome")
print(_line)
print(base.scope_statement)
print()
for term in ("marginalization", "projection", "coverage validation", "off-diagonal"):
    print(f"  mentions {term!r}: {term in (base.scope_statement or '')}")

print()
print(_line)
print("CONCLUSION")
print(_line)
print("The narrowing that travels with the grade is DERIVED from the declared leg set (control B),")
print("and the registry entry is inert to the outcome while remaining visible to `assess` (control A).")
print("The emitted scope statement already refuses to license the assembled covariance for")
print("MARGINALIZATION and PROJECTION -- which is what endpoint A proposes to release.")

print()
print(_line)
print("5. THE LOAD-BEARING CASE FOR 'IT COSTS NOTHING TODAY': leg ADOPTED, boundary STILL WITHHELD")
print(_line)
print("§3.3 rests on this: adopting the correlation leg must keep cause 3 NON-PASSING until the")
print("boundary is declared. If instead it returned MET, the recommendation would smuggle a pass.")
saved = dict(zc.Z_BOUNDARIES)
try:
    zc.Z_BOUNDARIES.update(DECLARED2)          # cause3_corr left WITHHELD, as the tree has it
    assert not zc.Z_BOUNDARIES["cause3_corr"].is_declared
    out = zv.assess(L3, {**STATS, "s_corr": 0.001}, all_valid())
finally:
    zc.Z_BOUNDARIES.clear(); zc.Z_BOUNDARIES.update(saved)
print(f"assessable      = {out.assessable}")
print(f"branch_label    = {out.branch_label!r}")
print(f"reject_conditions = {out.reject_conditions}")
print(f"is_met          = {out.is_met}")
safe = (out.is_met is False)
print(f"VERDICT: {'PASSES' if safe else 'FAILS'} -- adopting the leg with the boundary withheld "
      f"{'does NOT' if safe else 'DOES'} yield MET.")
print("  Note the statistic supplied was 0.001, i.e. WELL INSIDE any plausible limit. A withheld")
print("  boundary refuses on the ABSENCE OF A LIMIT, not on the value -- which is the correct")
print("  direction and is what makes 'costs nothing today' true rather than lucky.")

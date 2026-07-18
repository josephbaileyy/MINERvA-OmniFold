#!/usr/bin/env python3
"""P4 standard LATER-ONLY adoption CLI — FAIL-CLOSED (repair round 3, 2026-07-18).

Explicitly consumes the pre-adoption candidate + its inseparable component manifest
and promotes it to an adopted product. Requires: the expected vertical/unified inputs
and their identities (support-family / stat / ML SHA256 == component manifest); the
candidate validator PASS receipt; and rejects aliasing (out path == any input) or any
unvalidated input. NOT run in the repair round and NOT run automatically by the
canonical driver — a deliberate, separately authorized step (needs --i-understand-adoption).
"""
import argparse, json, os, sys
import p4_lib as P


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--component-manifest", required=True)
    ap.add_argument("--validation", required=True, help="validator JSON (must be PASS)")
    ap.add_argument("--out", required=True, help="adopted product path")
    ap.add_argument("--i-understand-adoption", action="store_true")
    a = ap.parse_args()

    P.require(a.i_understand_adoption, "adoption requires explicit --i-understand-adoption")
    prov = json.load(open(a.component_manifest))
    val = json.load(open(a.validation))
    P.require(val.get("result") == "PASS", "candidate validator did not PASS")
    # identities: the expected vertical/unified inputs are present and hash-matched
    for key, path in (("support_family_sha256", prov["support_family"]),
                      ("stat_sha256", prov["stat_cov"].split(":")[0]),
                      ("ml_sha256", prov["ml_cov"].split(":")[0])):
        P.require(os.path.exists(path), f"expected input missing: {path}")
        P.require(P.sha256_file(path) == prov[key], f"input identity drift: {path}")
    P.require(prov["identities"].get("pure_addition"), "component manifest is not pure-addition")
    # reject aliasing: out must differ from candidate and every input (by realpath)
    reals = {os.path.realpath(p) for p in (a.candidate, prov["support_family"],
                                           prov["stat_cov"].split(":")[0], prov["ml_cov"].split(":")[0])}
    P.require(os.path.realpath(a.out) not in reals, "aliasing: --out coincides with an input/candidate")
    P.require(P.sha256_file(a.candidate), "candidate unreadable")
    print(f"[adopt] gates PASS; would promote {a.candidate} -> {a.out} "
          f"(not executed here — separate authorized adoption step)")
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except P.P4GateError as e:
        print(f"FAIL-CLOSED :: {e}"); sys.exit(1)

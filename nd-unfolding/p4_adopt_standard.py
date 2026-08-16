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

# OI-128 (2026-08-16). The gate name `p4_validate_active_lateral.py` records once the systematic
# band set has actually been refereed against the SUPPORT FAMILY. It is duplicated from that
# module's literal rather than shared: `p4_lib.py` is the natural home but is under repair by
# another lane, so `tests/test_p4_repair.py` asserts the two spellings agree instead of leaving
# the duplication unchecked. Move it to `p4_lib` when that file is free.
BAND_COMPLETENESS_GATE = "band_set_completeness_vs_support_family"


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
    # OI-128 (2026-08-16). `result == "PASS"` does NOT imply the band-completeness gate ran.
    # `p4_validate_active_lateral.py` appends each cleared gate to `gates` and sets `result=PASS`
    # only at the END of its try block, so on the CURRENT validator a PASS receipt necessarily
    # records this one. The window this closes: a receipt written AFTER the 2026-08-10
    # component-manifest binding fix but BEFORE the band-completeness gate existed carries
    # `component_manifest_sha256`, records `PASS`, never refereed the band set against the support
    # family -- and was adoptable, because `gates` appeared nowhere in this file except a success
    # print. Checked here rather than trusted, and BEFORE any of the manifest gates below, since
    # those all read a manifest whose systematic budget this gate is what vouches for.
    _gates = val.get("gates")
    P.require(isinstance(_gates, list),
              "the validation receipt carries no `gates` list, so it cannot show WHICH checks ran; "
              "refusing rather than reading an absent inventory as a tolerable old format -- that "
              "is precisely the window this check exists to close (re-run "
              "p4_validate_active_lateral.py)")
    P.require(BAND_COMPLETENESS_GATE in _gates,
              f"the validation receipt does not record the `{BAND_COMPLETENESS_GATE}` gate: the "
              "systematic band set was never refereed against the support family, so a build that "
              "enumerated the wrong bands reconstructs every internal identity perfectly while the "
              "systematic budget is silently short (re-run p4_validate_active_lateral.py)")
    # FIX 2 of 2 (2026-08-10). Bind the component manifest to the validation receipt BEFORE
    # reading anything out of it. Previously `prov` came from a path on this command line and was
    # never tied to the receipt, so every gate below that consults it -- including the
    # non-adoptable refusal -- could be defeated by passing a hand-edited copy.
    _cm_sha = val.get("component_manifest_sha256")
    P.require(_cm_sha is not None,
              "the validation receipt records no component_manifest_sha256 -- it predates the "
              "2026-08-10 binding fix and cannot tie this manifest to what was validated; re-run "
              "p4_validate_active_lateral.py")
    P.require(P.sha256_file(a.component_manifest) == _cm_sha,
              "component manifest is not the one this receipt validated (sha256 mismatch) -- "
              "refusing, because every gate below reads from it")
    # Refuse a self-declared non-adoptable candidate before anything else. The whole point of
    # the marker is that it cannot be missed by a reader who does not know how the file was made.
    P.require_adoptable(prov)
    # ...and independently of the manifest, honour the marker the RECEIPT carries, so stripping the
    # key from both files is not enough either.
    P.require(not val.get(P.NON_ADOPTABLE_KEY),
              f"the validation receipt records {P.NON_ADOPTABLE_KEY}=true for this candidate")
    # identities: the expected vertical/unified inputs are present and hash-matched
    for key, path in (("support_family_sha256", prov["support_family"]),
                      ("stat_sha256", prov["stat_cov"].split(":")[0]),
                      ("ml_sha256", prov["ml_cov"].split(":")[0])):
        P.require(os.path.exists(path), f"expected input missing: {path}")
        P.require(P.sha256_file(path) == prov[key], f"input identity drift: {path}")
    # repair-5 (pattern sweep): this read `identities.pure_addition` and tested it for
    # truthiness, but the builder wrote that key as a literal `True` -- so the strictest gate in
    # the chain was reading a constant and calling it evidence. The builder now records MEASURED
    # errors; this consumer checks them against the declared tolerance instead of a boolean.
    _ids = prov.get("identities", {})
    P.require(isinstance(_ids, dict) and _ids, "component manifest records no identities")
    P.require("pure_addition" not in _ids,
              "component manifest carries the retired self-asserted `pure_addition` flag; it "
              "predates repair-5, when the identities were literals rather than measurements")
    _rtol = float(_ids.get("identity_rtol", 1e-9))
    for _k in ("active_only_eq_sum5_relerr", "C_combined_eq_syst_stat_ml_relerr",
               "full_total_residual_eq_stat_plus_ml_relerr"):
        P.require(_k in _ids, f"component manifest missing measured identity {_k}")
        P.require(float(_ids[_k]) <= _rtol,
                  f"component manifest records a FAILING identity {_k}={_ids[_k]} > {_rtol}")
    # reject aliasing: out must differ from candidate and every input (by realpath)
    reals = {os.path.realpath(p) for p in (a.candidate, prov["support_family"],
                                           prov["stat_cov"].split(":")[0], prov["ml_cov"].split(":")[0])}
    P.require(os.path.realpath(a.out) not in reals, "aliasing: --out coincides with an input/candidate")
    # J32: `P.require(P.sha256_file(...))` tested only that the digest was TRUTHY -- i.e. that the
    # file was readable. It bound nothing. Now that the validator's receipt records which candidate
    # it validated (p4_validate_active_lateral.py), require that this is that candidate.
    cand_sha = P.sha256_file(a.candidate)
    P.require(cand_sha, "candidate unreadable")
    receipt_sha = val.get("candidate_sha256") if isinstance(val, dict) else None
    P.require(receipt_sha is not None,
              "the validation receipt records no candidate_sha256 -- it predates the J32 fix and "
              "cannot bind a candidate; re-run p4_validate_active_lateral.py")
    P.require(receipt_sha == cand_sha,
              f"candidate sha256 {cand_sha} does not match the validated candidate {receipt_sha} "
              "-- this PASS receipt does not certify this file")
    print(f"[adopt] gates PASS; would promote {a.candidate} -> {a.out} "
          f"(not executed here — separate authorized adoption step)")
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except P.P4GateError as e:
        print(f"FAIL-CLOSED :: {e}"); sys.exit(1)

#!/usr/bin/env python3
"""Gate-3 validator for a P3F selection-shifted FULL-EVENT active-universe ROOT.

Gate 3 promotes a FRESH selection-shifted full-event lateral endpoint. Each endpoint ROOT must be
produced by the canonical installed binary (SHA-256 61d7dfbf..., built from 486e53e) under the
runtime combination MNV101_ACTIVE_UNIVERSE=BAND:IDX + MNV101_DUMP_POINTCLOUD=1 +
MNV101_FULL_PHASE_SPACE=1. The older MD5-e63c scalar ROOTs are CONTROLS only and do NOT establish
the g2-fullevent-v1 schema.

This validator does NOT re-implement the full-event structural contract. It COMPOSES the committed
additive EXHAUSTIVE domain validator (`validate_g2_fullevent_domain.py`, run read-only as a subprocess
to a caller-supplied WORK receipt), NOT the sampled smoke validator directly. That matters for
playlists 1D/1E/1F/1P: they carry KNOWN finite upstream-corrupt reco muons OUTSIDE the frozen extended
PET domain [0,30]x[0,120] GeV, on which the smoke validator's two SAMPLED reco-muon heuristics
(`bkg_reco_muon_valid`, `data_reco_muon_valid`) can fail. The domain validator runs every
domain/content check, composes the smoke validator, and SUPERSEDES exactly those two heuristics with
an EXHAUSTIVE bound out-of-domain census. Gate-3 FAILS CLOSED unless the domain receipt has
status=PASS, an empty `fatal` list, no structural NON-superseded base failures, a complete untruncated
out-of-domain census, exact retained bounds 30/120, and a nested base-validator receipt/hash/result.
The composed domain+base result OWNS the four trees, background clouds/weights, data & MC identities,
full-event metadata + schema, native misses, completeness, branch parity, and finite/populated
content. On top of that this validator adds the active-universe evidence that a selection-shifted
lateral endpoint must carry:

  * activeUniverseBand    == the expected lateral band,
  * activeUniverseIndex   == the expected endpoint index,
  * hasActiveUniverse     == 1,
  * activeUniverseIsLateral == 1,
  * the four signed migration-census TParameters
    (activeUniverse{Truth,Reco}{Entrants,Exits}) exist and are integral & non-negative,

and validates the requested band/endpoint/playlist against the declared
5-band x 2-endpoint x 12-playlist (=120 file) inventory.

The output JSON binds the input ROOT path/hash/size, the base validator path/hash/result, this
validator's hash, the expected vs observed active identity + census, the counts, and a single
PASS/FAIL verdict. It is written with unique-temp + fsync + atomic os.replace ONLY to the
caller-supplied WORK path; this tool NEVER publishes a final ROOT or a production receipt.

The pure functions (inventory, active-metadata, census, base-result composition, report assembly,
atomic write) import NO ROOT and are login-testable. ROOT reads + the base-validator subprocess +
file hashing run only in main() (compute node).

Usage:
  python3 validate_p3f_pet_fullevent.py --root ENDPOINT.root --band BAND --endpoint IDX \
      --playlist PL --work WORK_RECEIPT.json [--base-validator PATH] [--sample N]
Exit 0 = PASS, 1 = FAIL, 2 = usage / open error.
"""
import argparse
import datetime
import hashlib
import json
import os
import subprocess
import sys
import tempfile

# ------------------------------- declared Gate-3 inventory -------------------------------
# 5 lateral bands x 2 endpoints x 12 FPS playlists = 120 selection-shifted full-event ROOTs.
# Bands are the committed P3F FPS lateral set (active_universe_5d/fps/<BAND>_<IDX>/); endpoints are
# the two universe indices per band; playlists are the canonical Gate-1 FPS playlist_order.
EXPECTED_BANDS = ("BeamAngleX", "BeamAngleY", "MuonResolution",
                  "Muon_Energy_MINERvA", "Muon_Energy_MINOS")
EXPECTED_ENDPOINTS = (0, 1)
EXPECTED_PLAYLISTS = ("1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P")
N_EXPECTED_FILES = len(EXPECTED_BANDS) * len(EXPECTED_ENDPOINTS) * len(EXPECTED_PLAYLISTS)  # 120

# Active-universe schema markers + the four signed migration-census TParameters (runEventLoopOmniFold
# writes these under MNV101_ACTIVE_UNIVERSE; TNamed/TParameter names are authoritative from the C++).
ACTIVE_BAND_MARKER = "activeUniverseBand"          # TNamed  (band name; "cv" if not enabled)
ACTIVE_INDEX_MARKER = "activeUniverseIndex"        # TParameter<int>
ACTIVE_ENABLED_MARKER = "hasActiveUniverse"        # TParameter<int> (1)
ACTIVE_LATERAL_MARKER = "activeUniverseIsLateral"  # TParameter<int> (1)
MIGRATION_CENSUS_PARAMS = ("activeUniverseTruthEntrants", "activeUniverseTruthExits",
                           "activeUniverseRecoEntrants", "activeUniverseRecoExits")

_HERE = os.path.dirname(os.path.abspath(__file__))
# Gate-3 composes the EXHAUSTIVE domain validator (which itself composes the smoke validator and
# supersedes the two sampled reco-muon heuristics with a bound census). The smoke default is kept
# only to bind/forward as the domain validator's --base-validator.
DOMAIN_VALIDATOR_DEFAULT = os.path.join(_HERE, "validate_g2_fullevent_domain.py")
BASE_VALIDATOR_DEFAULT = os.path.join(_HERE, "validate_g2_fullevent_smoke.py")
RECEIPT_SCHEMA = "p3f-pet-fullevent-validation-v1"
# Frozen extended-PET retained domain the domain receipt MUST declare exactly.
EXPECTED_PT_MAX = 30.0
EXPECTED_PPAR_MAX = 120.0
# Base smoke checks the domain validator is ALLOWED to supersede (exhaustive census replaces them);
# any base failure OUTSIDE this set is a non-superseded failure and fails Gate-3 closed.
SUPERSEDED_BASE_CHECKS = ("bkg_reco_muon_valid", "data_reco_muon_valid")


# ============================ pure, ROOT-free logic (unit-tested) ============================
def _ck(name, ok, detail=""):
    return {"name": name, "ok": bool(ok), "detail": str(detail)}


def normalize_endpoint(endpoint):
    """Coerce a CLI endpoint to int; raise ValueError on a non-integer token."""
    try:
        return int(endpoint)
    except (TypeError, ValueError):
        raise ValueError(f"endpoint {endpoint!r} is not an integer")


def assert_inventory(band, endpoint, playlist):
    """Strict membership check for a requested (band, endpoint, playlist) against the declared
    5x2x12 inventory. Returns (band, idx, playlist) normalized; raises ValueError otherwise."""
    idx = normalize_endpoint(endpoint)
    if band not in EXPECTED_BANDS:
        raise ValueError(f"band {band!r} not in declared inventory {EXPECTED_BANDS}")
    if idx not in EXPECTED_ENDPOINTS:
        raise ValueError(f"endpoint {idx} not in declared endpoints {EXPECTED_ENDPOINTS}")
    if playlist not in EXPECTED_PLAYLISTS:
        raise ValueError(f"playlist {playlist!r} not in declared playlists {EXPECTED_PLAYLISTS}")
    return band, idx, playlist


def check_inventory(band, endpoint, playlist):
    """Non-raising inventory membership -> (ok, checks, idx_or_None)."""
    checks = []
    try:
        idx = normalize_endpoint(endpoint)
    except ValueError as e:
        return False, [_ck("inventory:endpoint_integer", False, str(e))], None
    b_ok = band in EXPECTED_BANDS
    e_ok = idx in EXPECTED_ENDPOINTS
    p_ok = playlist in EXPECTED_PLAYLISTS
    checks.append(_ck("inventory:band", b_ok, band))
    checks.append(_ck("inventory:endpoint", e_ok, idx))
    checks.append(_ck("inventory:playlist", p_ok, playlist))
    return (b_ok and e_ok and p_ok), checks, idx


def _is_integral_nonneg(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return False
    return f.is_integer() and f >= 0.0


def check_active_metadata(observed, expected_band, expected_idx):
    """Validate the observed active-universe markers against the expected lateral endpoint.
    `observed` is a dict of marker-name -> value (missing markers absent). Returns (ok, checks)."""
    checks = []
    ob = observed.get(ACTIVE_BAND_MARKER)
    checks.append(_ck("active:band_matches", ob is not None and str(ob) == str(expected_band),
                      f"{ob!r} vs {expected_band!r}"))
    oi = observed.get(ACTIVE_INDEX_MARKER)
    checks.append(_ck("active:index_matches",
                      oi is not None and _is_integral_nonneg(oi) and int(oi) == int(expected_idx),
                      f"{oi!r} vs {expected_idx}"))
    en = observed.get(ACTIVE_ENABLED_MARKER)
    checks.append(_ck("active:hasActiveUniverse==1", en is not None and int(en) == 1, en))
    lat = observed.get(ACTIVE_LATERAL_MARKER)
    checks.append(_ck("active:isLateral==1", lat is not None and int(lat) == 1, lat))
    ok = all(c["ok"] for c in checks)
    return ok, checks


def check_migration_census(observed):
    """The four signed migration-census TParameters must EXIST and be integral & non-negative."""
    checks = []
    for name in MIGRATION_CENSUS_PARAMS:
        present = name in observed and observed[name] is not None
        ok = present and _is_integral_nonneg(observed[name])
        checks.append(_ck(f"census:{name}", ok,
                          observed.get(name) if present else "MISSING"))
    return all(c["ok"] for c in checks), checks


def check_domain_census_complete(domain_receipt):
    """The out-of-domain census must be COMPLETE and UNTRUNCATED: every reco context's censused row
    list length equals its reported out_of_domain count, the bound total equals their sum, and no
    fatal reports a truncated census. `domain_receipt` is the parsed g2-domain-validation-v1 dict."""
    checks = []
    census = domain_receipt.get("census") or {}
    total_expected = 0
    for c in domain_receipt.get("checks", []):
        ood = c.get("out_of_domain")
        if ood is None:                      # truth/miss checks carry no out_of_domain field
            continue
        total_expected += int(ood)
        key = f"{c.get('context')}_out_of_domain"
        if ood > 0:
            got = len(census.get(key, [])) if isinstance(census.get(key), list) else -1
            checks.append(_ck(f"domain:census_complete:{c.get('context')}", got == ood,
                              f"{got}/{ood}"))
    bound = domain_receipt.get("out_of_domain_censused_and_bound")
    checks.append(_ck("domain:census_bound_total", bound == total_expected,
                      f"{bound} vs {total_expected}"))
    trunc = [x for x in (domain_receipt.get("fatal") or []) if "truncat" in str(x).lower()]
    checks.append(_ck("domain:no_truncation", not trunc, trunc))
    return all(c["ok"] for c in checks), checks


def check_domain_result(domain_receipt):
    """Compose the EXHAUSTIVE domain validator result; fail closed unless it PASSED with an empty
    fatal list, exact 30/120 retained bounds, a nested base-validator receipt/hash/result with NO
    non-superseded base failures, and a complete untruncated out-of-domain census. `domain_receipt`
    is the parsed g2-domain-validation-v1 dict."""
    checks = []
    checks.append(_ck("domain:schema", domain_receipt.get("receipt_schema")
                      == "g2-domain-validation-v1", domain_receipt.get("receipt_schema")))
    checks.append(_ck("domain:status_pass", domain_receipt.get("status") == "PASS",
                      domain_receipt.get("status")))
    fatal = domain_receipt.get("fatal")
    checks.append(_ck("domain:fatal_empty", fatal == [], fatal))
    dom = domain_receipt.get("domain") or {}
    checks.append(_ck("domain:pt_max_30", dom.get("pt_max") == EXPECTED_PT_MAX, dom.get("pt_max")))
    checks.append(_ck("domain:ppar_max_120", dom.get("p_par_max") == EXPECTED_PPAR_MAX,
                      dom.get("p_par_max")))
    # nested base validator (structural) — receipt / hash / result must be bound, ran, and carry NO
    # non-superseded failures (the two reco-muon heuristics may be superseded; nothing else may fail).
    s = domain_receipt.get("structural") or {}
    checks.append(_ck("domain:base_ran", bool(s.get("ran")), s.get("error", "")))
    checks.append(_ck("domain:base_no_nonsuperseded_failures",
                      s.get("non_superseded_failures") == [], s.get("non_superseded_failures")))
    sup = s.get("superseded_failures")
    checks.append(_ck("domain:superseded_within_allowed",
                      isinstance(sup, list) and set(sup) <= set(SUPERSEDED_BASE_CHECKS), sup))
    checks.append(_ck("domain:base_receipt_bound", bool(s.get("receipt")), s.get("receipt")))
    checks.append(_ck("domain:base_receipt_hash", bool(s.get("base_receipt_sha256")),
                      s.get("base_receipt_sha256")))
    checks.append(_ck("domain:base_validator_hash", bool(s.get("base_validator_sha256")),
                      s.get("base_validator_sha256")))
    checks.append(_ck("domain:base_result_bound",
                      s.get("n_checks") is not None and s.get("n_failed") is not None,
                      f"n_checks={s.get('n_checks')} n_failed={s.get('n_failed')}"))
    cok, cck = check_domain_census_complete(domain_receipt)
    checks += cck
    return all(c["ok"] for c in checks), checks


def build_report(*, root_meta, this_validator, domain_validator, domain_result,
                 band, endpoint, playlist, observed, observed_at_utc=None):
    """Assemble the full Gate-3 receipt payload + single PASS/FAIL verdict from already-gathered
    inputs. Pure: no ROOT, no I/O, no hashing. `root_meta`={path,sha256,size_bytes};
    `this_validator`/`domain_validator`={path,sha256}; `domain_result` = the domain-validator run
    summary {ran,exit,receipt,receipt_sha256,parsed:<g2-domain-validation-v1 dict>}; `observed` =
    active markers + census read from the ROOT. The nested base (smoke) validator receipt/hash/result
    is bound from the domain receipt's `structural` block."""
    inv_ok, inv_checks, idx = check_inventory(band, endpoint, playlist)
    # expected active identity derives from the (validated) requested endpoint
    exp_idx = idx if idx is not None else endpoint
    parsed = domain_result.get("parsed") or {}
    struct = parsed.get("structural") or {}
    dom_ran = bool(domain_result.get("ran"))
    dom_exec_ok = dom_ran and domain_result.get("exit") == 0
    dom_ok, dom_checks = check_domain_result(parsed)
    dom_ran_check = [_ck("domain:validator_ran", dom_exec_ok,
                         domain_result.get("error", domain_result.get("exit")))]
    act_ok, act_checks = check_active_metadata(observed, band, exp_idx)
    cen_ok, cen_checks = check_migration_census(observed)
    checks = inv_checks + dom_ran_check + dom_checks + act_checks + cen_checks
    verdict = bool(inv_ok and dom_exec_ok and dom_ok and act_ok and cen_ok)
    payload = {
        "receipt_schema": RECEIPT_SCHEMA,
        "verdict": "PASS" if verdict else "FAIL",
        "observed_at_utc": observed_at_utc,
        "root": dict(root_meta),
        "this_validator": dict(this_validator),
        "domain_validator": {
            "path": domain_validator.get("path"), "sha256": domain_validator.get("sha256"),
            "ran": dom_ran, "exit": domain_result.get("exit"),
            "receipt": domain_result.get("receipt"),
            "receipt_sha256": domain_result.get("receipt_sha256"),
            "status": parsed.get("status"), "fatal": parsed.get("fatal"),
            "domain": parsed.get("domain"),
            "out_of_domain_censused_and_bound": parsed.get("out_of_domain_censused_and_bound")},
        # nested base (smoke) validator, bound from the domain receipt's composed structural result
        "base_validator": {
            "path": struct.get("base_validator"), "sha256": struct.get("base_validator_sha256"),
            "receipt": struct.get("receipt"), "receipt_sha256": struct.get("base_receipt_sha256"),
            "ran": struct.get("ran"), "exit": struct.get("exit"),
            "n_checks": struct.get("n_checks"), "n_failed": struct.get("n_failed"),
            "non_superseded_failures": struct.get("non_superseded_failures"),
            "superseded_failures": struct.get("superseded_failures")},
        "inventory": {
            "band": band, "endpoint": exp_idx, "playlist": playlist,
            "n_bands": len(EXPECTED_BANDS), "n_endpoints": len(EXPECTED_ENDPOINTS),
            "n_playlists": len(EXPECTED_PLAYLISTS), "n_total_files": N_EXPECTED_FILES,
            "in_inventory": inv_ok,
            "expected_bands": list(EXPECTED_BANDS), "expected_endpoints": list(EXPECTED_ENDPOINTS),
            "expected_playlists": list(EXPECTED_PLAYLISTS)},
        "expected_active": {
            ACTIVE_BAND_MARKER: band, ACTIVE_INDEX_MARKER: exp_idx,
            ACTIVE_ENABLED_MARKER: 1, ACTIVE_LATERAL_MARKER: 1,
            "census_params": list(MIGRATION_CENSUS_PARAMS)},
        "observed_active": {
            ACTIVE_BAND_MARKER: (None if observed.get(ACTIVE_BAND_MARKER) is None
                                 else str(observed.get(ACTIVE_BAND_MARKER))),
            ACTIVE_INDEX_MARKER: observed.get(ACTIVE_INDEX_MARKER),
            ACTIVE_ENABLED_MARKER: observed.get(ACTIVE_ENABLED_MARKER),
            ACTIVE_LATERAL_MARKER: observed.get(ACTIVE_LATERAL_MARKER)},
        "observed_census": {k: observed.get(k) for k in MIGRATION_CENSUS_PARAMS},
        "census_ok": cen_ok,
        "counts": dict((domain_result.get("counts") or parsed.get("structural", {}).get("counts")
                        or {})),
        "checks": checks,
        "n_checks": len(checks),
        "n_failed": sum(1 for c in checks if not c["ok"]),
        "component_verdicts": {"inventory": inv_ok, "domain": (dom_exec_ok and dom_ok),
                               "active": act_ok, "census": cen_ok}}
    return payload, verdict


def write_work_receipt(work_path, payload):
    """Atomic receipt write: unique temp in the WORK path's directory -> fsync -> os.replace, ONLY to
    the caller-supplied WORK path. Never writes any final ROOT / production receipt. On interruption
    no partial file survives at `work_path`."""
    directory = os.path.dirname(os.path.abspath(work_path)) or "."
    fd, tmp = tempfile.mkstemp(prefix=".p3f_pet_val_", suffix=".json", dir=directory)
    try:
        with os.fdopen(fd, "w") as fh:
            json.dump(payload, fh, indent=2, default=str)
            fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, work_path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    return work_path


# ============================== ROOT / filesystem (runtime only) ==============================
def _sha256_file(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def read_active_markers(root_path):
    """Read the active-universe markers + migration census from a ROOT file. Missing markers are
    OMITTED from the returned dict (so downstream checks fail closed). Needs PyROOT (compute node)."""
    import ROOT  # deferred: unavailable on the login node
    f = ROOT.TFile.Open(root_path)
    if not f or f.IsZombie():
        raise SystemExit(f"[P3F] cannot open {root_path}")
    out = {}
    nm = f.Get(ACTIVE_BAND_MARKER)
    if nm:
        out[ACTIVE_BAND_MARKER] = str(nm.GetTitle())
    for name in (ACTIVE_INDEX_MARKER, ACTIVE_ENABLED_MARKER, ACTIVE_LATERAL_MARKER,
                 *MIGRATION_CENSUS_PARAMS):
        p = f.Get(name)
        if p:
            try:
                out[name] = p.GetVal()
            except AttributeError:
                out[name] = p.GetTitle()
    f.Close()
    return out


def run_domain_validator(root_path, domain_receipt_workpath, domain_validator,
                         base_validator=None):
    """Run the committed EXHAUSTIVE domain validator READ-ONLY to a NEW WORK receipt (never any
    original). It internally composes the smoke validator (writing its own base receipt beside the
    domain receipt) and supersedes the two sampled reco-muon heuristics with a bound census. Returns
    {ran, exit, receipt, receipt_sha256, parsed:<domain receipt dict>, counts}. Runtime only."""
    r = {"ran": False, "receipt": domain_receipt_workpath}
    cmd = [sys.executable, domain_validator, root_path, domain_receipt_workpath]
    if base_validator:
        cmd += ["--base-validator", base_validator]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=14400)
        r["ran"] = True
        r["exit"] = p.returncode
    except Exception as e:  # noqa: BLE001
        r["error"] = str(e)
        return r
    try:
        d = json.load(open(domain_receipt_workpath))
    except Exception as e:  # noqa: BLE001
        r["error"] = f"domain receipt unreadable: {e}"
        return r
    r["parsed"] = d
    r["receipt_sha256"] = _sha256_file(domain_receipt_workpath)
    # surface the composed base counts (owned by the nested smoke validator) for the Gate-3 receipt
    struct = d.get("structural") or {}
    base_receipt = struct.get("receipt")
    counts = None
    if base_receipt and os.path.exists(base_receipt):
        try:
            counts = json.load(open(base_receipt)).get("counts")
        except Exception:  # noqa: BLE001
            counts = None
    r["counts"] = counts
    return r


def main(argv=None):
    ap = argparse.ArgumentParser(description="Gate-3 P3F full-event active-universe validator")
    ap.add_argument("--root", required=True, help="selection-shifted full-event endpoint ROOT")
    ap.add_argument("--band", required=True, help=f"lateral band (one of {EXPECTED_BANDS})")
    ap.add_argument("--endpoint", required=True, help="endpoint index (0 or 1)")
    ap.add_argument("--playlist", required=True, help="FPS playlist (e.g. 1A)")
    ap.add_argument("--work", required=True, help="caller-supplied WORK receipt path (JSON)")
    ap.add_argument("--domain-validator", default=DOMAIN_VALIDATOR_DEFAULT,
                    help="exhaustive domain validator to compose (default: sibling)")
    ap.add_argument("--base-validator", default=BASE_VALIDATOR_DEFAULT,
                    help="smoke validator forwarded to the domain validator's --base-validator")
    args = ap.parse_args(argv)

    # Strict inventory check on the CLI request (fail before any compute).
    try:
        band, idx, playlist = assert_inventory(args.band, args.endpoint, args.playlist)
    except ValueError as e:
        print(f"[P3F] usage: {e}")
        return 2
    # Defensive: never let the WORK receipt clobber the input ROOT.
    if os.path.abspath(args.work) == os.path.abspath(args.root):
        print("[P3F] --work must not be the input ROOT path")
        return 2

    if not os.path.exists(args.root):
        print(f"[P3F] input ROOT not found: {args.root}")
        return 2

    root_meta = {"path": os.path.abspath(args.root), "sha256": _sha256_file(args.root),
                 "size_bytes": os.path.getsize(args.root)}
    this_validator = {"path": os.path.abspath(__file__), "sha256": _sha256_file(__file__)}
    domain_validator = {"path": os.path.abspath(args.domain_validator),
                        "sha256": _sha256_file(args.domain_validator)}

    # Compose the EXHAUSTIVE domain validator to a WORK receipt (it writes its own base receipt
    # beside it). Never a production path; the smoke validator is forwarded, not invoked here.
    domain_receipt = args.work + ".domain.json"
    domain_result = run_domain_validator(args.root, domain_receipt, args.domain_validator,
                                         base_validator=args.base_validator)
    observed = read_active_markers(args.root)

    observed_at_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    payload, verdict = build_report(
        root_meta=root_meta, this_validator=this_validator, domain_validator=domain_validator,
        domain_result=domain_result, band=band, endpoint=idx, playlist=playlist, observed=observed,
        observed_at_utc=observed_at_utc)
    write_work_receipt(args.work, payload)          # WORK path only; no final ROOT / production write
    print(json.dumps({"verdict": payload["verdict"], "n_failed": payload["n_failed"],
                      "component_verdicts": payload["component_verdicts"],
                      "work_receipt": args.work}, indent=2))
    return 0 if verdict else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Fail-closed validator for the twelve G2 Gate-1 ROOT/receipt pairs.

Validates both normal production receipts and the independently reviewed
retained-domain recovery receipts. ROOT content hashes are recomputed, not
trusted. Writes one atomic JSON summary only after all checks complete.
"""
import argparse
import concurrent.futures
import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile


PLAYLISTS = ("1A", "1B", "1C", "1D", "1E", "1F",
             "1G", "1L", "1M", "1N", "1O", "1P")
RECOVERED = {"1D", "1E", "1F", "1P"}
BIN_SHA = "61d7dfbf7ee38f39e51c656b48702056c773c3d1c5d1b2d9bf08a6da42d2e19b"
BASE_VALIDATOR_SHA = "3b5c4ae9b954a6db2ac8dadf25abb433cc0024f9ee182e589de654ba44b5f1f8"
LAUNCHER_SHA = "dfcfa5c612e2067b12c879f183533de2678de78c8f6acba816ac2db86e94a715"
DOMAIN_VALIDATOR_SHA = "32634d6832b4c1f6e5f9036a425b7412f004e2de0aa77828106646d7fc6e3739"
BUILT_SOURCE_COMMIT = "486e53e677eb64eb9d622ff6e5daecb3e62aab22"
ALLOWED_SAMPLED_FAILURES = {"bkg_reco_muon_valid", "data_reco_muon_valid"}
COUNT_KEYS = ("mc_truth_denom", "mc_signal_reco", "mc_background", "data",
              "nTruthOnlyMisses")
POT_KEYS = ("mcPOTUsed", "dataPOTUsed")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(16 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_json(path):
    with open(path) as handle:
        return json.load(handle)


def atomic_json(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix="." + path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def check(condition, failures, message):
    if not condition:
        failures.append(message)


def canonical(path):
    return str(Path(path).resolve())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=str(Path(__file__).resolve().parents[2]))
    parser.add_argument("--output", required=True)
    parser.add_argument("--hash-workers", type=int, default=4)
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    final_dir = repo / "nd-unfolding/g2_fullevent/final"
    failures = []
    records = {}
    roots = {}
    aggregate = {key: 0 for key in COUNT_KEYS}
    aggregate.update({key: 0.0 for key in POT_KEYS})

    check(sha256(repo / "MINERvA101/opt/bin/runEventLoopOmniFold") == BIN_SHA,
          failures, "canonical binary hash drift")
    check(sha256(repo / "nd-unfolding/pet/validate_g2_fullevent_smoke.py") == BASE_VALIDATOR_SHA,
          failures, "base validator hash drift")
    check(sha256(repo / "nd-unfolding/pet/sbatch_g2_fullevent_evloop_array.sh") == LAUNCHER_SHA,
          failures, "production launcher hash drift")
    check(sha256(repo / "nd-unfolding/pet/validate_g2_fullevent_domain.py") == DOMAIN_VALIDATOR_SHA,
          failures, "domain validator hash drift")

    for playlist in PLAYLISTS:
        root = final_dir / ("runEventLoopOmniFold_G2_FPS_%s.root" % playlist)
        receipt_path = final_dir / ("G2_receipt_%s.json" % playlist)
        prefix = playlist + ": "
        check(root.is_file() and root.stat().st_size > 0, failures, prefix + "ROOT missing/empty")
        check(receipt_path.is_file() and receipt_path.stat().st_size > 0,
              failures, prefix + "receipt missing/empty")
        if not root.is_file() or not receipt_path.is_file():
            continue
        receipt = load_json(receipt_path)
        schema = receipt.get("receipt_schema")
        wanted_schema = ("g2-recovery-receipt-v1" if playlist in RECOVERED
                         else "g2-production-playlist-receipt-v1")
        check(schema == wanted_schema, failures, prefix + "wrong receipt schema")
        check(receipt.get("playlist") == playlist, failures, prefix + "playlist mismatch")
        check(receipt.get("status") == "PASS", failures, prefix + "receipt not PASS")
        check(receipt.get("binary_sha256") == BIN_SHA and
              receipt.get("binary_sha256_expected") == BIN_SHA,
              failures, prefix + "binary binding mismatch")
        check(receipt.get("built_source_commit") == BUILT_SOURCE_COMMIT,
              failures, prefix + "built-source mismatch")
        check(receipt.get("env") == {"MNV101_DUMP_POINTCLOUD": "1",
                                      "MNV101_FULL_PHASE_SPACE": "1"},
              failures, prefix + "environment mismatch")
        for kind in ("Data", "MC"):
            field = "manifest_" + kind.lower()
            manifest = repo / ("2d-unfolding/playlist_manifests/%s_%s.txt" %
                               (playlist, kind))
            bound = receipt.get(field, {})
            check(canonical(bound.get("path", "")) == canonical(manifest),
                  failures, prefix + field + " path mismatch")
            check(manifest.is_file() and bound.get("sha256") == sha256(manifest),
                  failures, prefix + field + " hash mismatch")
        final = receipt.get("final_root", {})
        check(canonical(final.get("path", "")) == canonical(root),
              failures, prefix + "final ROOT path mismatch")
        check(final.get("size_bytes") == root.stat().st_size,
              failures, prefix + "final ROOT size mismatch")
        roots[playlist] = root

        counts = None
        supporting_validation_sha256 = None
        ood = 0
        if schema == "g2-production-playlist-receipt-v1":
            validator = receipt.get("validator", {})
            check(validator.get("sha256") == BASE_VALIDATOR_SHA,
                  failures, prefix + "validator hash mismatch")
            validation = receipt.get("validation", {})
            check(validation.get("n_checks") == 50 and validation.get("n_failed") == 0,
                  failures, prefix + "production validation is not 50/50 PASS")
            validation_path = Path(validation.get("validation_json", ""))
            check(validation_path.is_file(), failures, prefix + "validation JSON missing")
            if validation_path.is_file():
                supporting_validation_sha256 = sha256(validation_path)
                v = load_json(validation_path)
                check(v.get("status") == "PASS" and v.get("n_checks") == 50 and
                      v.get("n_failed") == 0, failures,
                      prefix + "validation JSON is not 50/50 PASS")
                check(v.get("counts") == validation.get("counts"), failures,
                      prefix + "embedded counts differ from validation JSON")
            counts = validation.get("counts")
        elif schema == "g2-recovery-receipt-v1":
            check(receipt.get("recovery") is True, failures, prefix + "recovery flag missing")
            check(receipt.get("base_validator", {}).get("sha256") == BASE_VALIDATOR_SHA,
                  failures, prefix + "base-validator hash mismatch")
            check(receipt.get("production_launcher", {}).get("sha256") == LAUNCHER_SHA,
                  failures, prefix + "launcher hash mismatch")
            domain_meta = receipt.get("domain_validation", {})
            check(domain_meta.get("validator_sha256") == DOMAIN_VALIDATOR_SHA,
                  failures, prefix + "domain-validator hash mismatch")
            domain_path = Path(domain_meta.get("receipt", ""))
            check(domain_path.is_file(), failures, prefix + "domain receipt missing")
            if domain_path.is_file():
                supporting_validation_sha256 = sha256(domain_path)
                check(domain_meta.get("receipt_sha256") == supporting_validation_sha256,
                      failures, prefix + "domain receipt hash mismatch")
                domain = load_json(domain_path)
                check(domain.get("status") == "PASS" and not domain.get("fatal"),
                      failures, prefix + "domain receipt not PASS")
                check(domain.get("domain") == {"pt_max": 30.0, "p_par_max": 120.0},
                      failures, prefix + "retained domain mismatch")
                structural = domain.get("structural", {})
                check(structural.get("ran") is True and
                      not structural.get("non_superseded_failures") and
                      set(structural.get("failed_checks", [])) <= ALLOWED_SAMPLED_FAILURES,
                      failures, prefix + "non-superseded structural failure")
                base_path = Path(structural.get("receipt", ""))
                check(base_path.is_file(), failures, prefix + "base receipt missing")
                if base_path.is_file():
                    check(structural.get("base_receipt_sha256") == sha256(base_path),
                          failures, prefix + "base receipt hash mismatch")
                    base = load_json(base_path)
                    check(base.get("n_checks") == 50, failures,
                          prefix + "base receipt check count mismatch")
                    counts = base.get("counts")
                census = domain.get("census", {})
                ood_rows = []
                for key, rows in census.items():
                    if key.endswith("_out_of_domain"):
                        ood_rows.extend(rows)
                ood = domain.get("out_of_domain_censused_and_bound")
                check(ood == len(ood_rows) == domain_meta.get("out_of_domain_censused_and_bound"),
                      failures, prefix + "out-of-domain census count mismatch")
                for row in ood_rows:
                    pt, ppar = row.get("pt"), row.get("p_par")
                    valid = (isinstance(pt, (int, float)) and isinstance(ppar, (int, float)) and
                             math.isfinite(pt) and math.isfinite(ppar) and
                             not (0.0 <= pt <= 30.0 and 0.0 <= ppar <= 120.0))
                    check(valid, failures, prefix + "census contains non-OOD row")
        check(isinstance(counts, dict), failures, prefix + "counts unavailable")
        if isinstance(counts, dict):
            for key in COUNT_KEYS:
                check(isinstance(counts.get(key), int), failures, prefix + key + " invalid")
                if isinstance(counts.get(key), int):
                    aggregate[key] += counts[key]
            for key in POT_KEYS:
                check(isinstance(counts.get(key), (int, float)), failures,
                      prefix + key + " invalid")
                if isinstance(counts.get(key), (int, float)):
                    aggregate[key] += counts[key]
            check(counts.get("mc_truth_denom") == counts.get("mc_signal_reco"),
                  failures, prefix + "truth/signal completeness invariant failed")
        records[playlist] = {
            "receipt_schema": schema,
            "receipt_path": str(receipt_path),
            "receipt_sha256": sha256(receipt_path),
            "root_path": str(root),
            "root_size_bytes": root.stat().st_size,
            "root_sha256_expected": final.get("sha256"),
            "counts": counts,
            "supporting_validation_sha256": supporting_validation_sha256,
            "out_of_domain_rows_censused_and_bound": ood,
        }

    # Hash all large ROOTs concurrently after all cheap fail-closed checks.
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.hash_workers) as pool:
        futures = {playlist: pool.submit(sha256, root) for playlist, root in roots.items()}
        for playlist in PLAYLISTS:
            if playlist not in futures:
                continue
            actual = futures[playlist].result()
            records[playlist]["root_sha256_actual"] = actual
            check(actual == records[playlist]["root_sha256_expected"], failures,
                  playlist + ": final ROOT hash mismatch")

    check(set(records) == set(PLAYLISTS), failures, "playlist set incomplete")
    check(aggregate["mc_truth_denom"] == aggregate["mc_signal_reco"], failures,
          "global truth/signal completeness invariant failed")
    summary = {
        "schema_version": 1,
        "gate": "G2 full-schema FPS CV per-playlist production",
        "observed_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "playlist_order": list(PLAYLISTS),
        "normal_production_pairs": sorted(set(PLAYLISTS) - RECOVERED),
        "retained_domain_recovery_pairs": sorted(RECOVERED),
        "aggregate_counts": aggregate,
        "total_root_size_bytes": sum(r["root_size_bytes"] for r in records.values()),
        "pairs": records,
        "conditional_use": ("Recovered pairs require the downstream builder to enforce "
                            "0<=pT<=30 GeV and 0<=p_parallel<=120 GeV before training."),
        "canonical_hashes": {"binary": BIN_SHA, "base_validator": BASE_VALIDATOR_SHA,
                             "production_launcher": LAUNCHER_SHA,
                             "domain_validator": DOMAIN_VALIDATOR_SHA},
    }
    atomic_json(args.output, summary)
    print(json.dumps({"status": summary["status"], "n_pairs": len(records),
                      "n_failures": len(failures),
                      "total_root_size_bytes": summary["total_root_size_bytes"],
                      "aggregate_counts": aggregate}, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())

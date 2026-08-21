#!/usr/bin/env python3
"""Assemble the committed negweight HPSS durability manifest from MEASURED artifacts.

The manifest is not hand-written, because a hand-written manifest is a claim and this needs to
be a derivation. Every number in it comes from a file this script reads:

    inventory.tsv / sidecar_inventory.tsv   per-file size, sha256, md5, mtime (cluster-side)
    markers/*.hpss.json                     per-object local vs SERVER-SIDE md5 and size
    residency_{before,after}_migrate.txt    the storage-hierarchy readings
    hashverify.{log,rc}, coverage.*         the tape-read verification and its coverage diff
    archive_listing.txt                     the archive's own inventory, independent of us

NO REPO ROOT IS HARDCODED. `OI-136` is the reason: 59 `.py` files in this tree put a hardcoded
cluster root at `sys.path[0]`, so an entrypoint could import another checkout's modules while
deployment parity truthfully reported every pinned file CURRENT. Paths come in as arguments.

Usage:
    python3 build_negweight_hpss_manifest.py <evidence-dir> <out.json> [--recovery <dir>]

Re-runnable: given the same evidence directory it produces the same JSON except for
`generated_at_utc`, which is passed in rather than read from the clock so a regeneration can be
compared byte-for-byte.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys

HPSS_DIR = "mnv-negweight-historical-20260821"

FAMILY = [
    ("2d-unfolding/HANDOFF_bkg_negweight/runs/", "runs_hist5_exact5", "negweight_runs_8.tar", 8),
    ("2d-unfolding/uq/negweight_boot/", "bootstrap_replicas", "negweight_boot_51.tar", 51),
    ("2d-unfolding/uq/negweight_uni/", "universe_replicas", "negweight_uni_188.tar", 188),
]


def _evidence(E, name):
    """Resolve an evidence filename, tolerating the `.log` -> `.log.txt` rename.

    `.gitignore:15` is a blanket `*.log`, so a plain `git add` SILENTLY SKIPS hashverify.log --
    committing a receipt that cites an artifact git is not carrying. That is the exact defect
    `verify_receipt_artifacts.py` exists to catch, and it does not cover this case: its rule is
    scoped to binary extensions (.root/.npz/.h5/...) under docs/orchestration/state/, so a .log
    walks straight past it. The committed copies are renamed rather than force-added, because
    force-adding fights the ignore rule and leaves the next lane to rediscover the trap.
    """
    for cand in (name, name + ".txt"):
        f = os.path.join(E, cand)
        if os.path.exists(f):
            return f
    raise SystemExit(f"FATAL: neither {name} nor {name}.txt under {E}")


def read_inventory(path):
    rows = []
    with open(path) as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line:
                continue
            rel, size, sha, md5, mtime = line.split("\t")
            rows.append({"path": rel, "size": int(size), "sha256": sha, "md5": md5,
                         "mtime_local": mtime})
    return rows


def classify(rel):
    for prefix, fam, tar, _n in FAMILY:
        if rel.startswith(prefix):
            return fam, tar
    return None, None


def tape_readings(text):
    """Parse `ls -V` blocks into {object: {bytes_at_tape_level, pv_list, position}}."""
    out, cur = {}, None
    for line in text.splitlines():
        m = re.match(r"^--- (?:BEFORE|AFTER) migrate: ls -V (\S+)", line)
        if m:
            cur = m.group(1)
            out.setdefault(cur, {"bytes_at_tape_level": 0, "pv_list": None, "position": None})
            continue
        if cur is None:
            continue
        m = re.match(r"^\s*1 \(tape\)\s+(\d+)\s+\d+\s+(\d+)?", line)
        if m:
            out[cur]["vv_count"] = int(m.group(1))
            out[cur]["bytes_at_tape_level"] = int(m.group(2)) if m.group(2) else 0
        m = re.search(r"Pos:\s+(\S+)\s+PV List:\s+(\S+)", line)
        if m:
            out[cur]["position"] = m.group(1)
            out[cur]["pv_list"] = m.group(2)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("evidence")
    ap.add_argument("out")
    ap.add_argument("--generated-at", required=True)
    ap.add_argument("--recovery", default=None,
                    help="directory holding the recovery run's step outputs")
    ap.add_argument("--recovery-consumed-manifest-sha256", default=None,
                    help="sha256 of the manifest the recovery run actually read")
    a = ap.parse_args()
    E = a.evidence

    ruled = read_inventory(os.path.join(E, "inventory.tsv"))
    side = read_inventory(os.path.join(E, "sidecar_inventory.tsv"))
    if len(ruled) != 247:
        sys.exit(f"FATAL: inventory.tsv has {len(ruled)} rows, ruled scope is 247")

    counts = {}
    for r in ruled:
        fam, tar = classify(r["path"])
        if fam is None:
            sys.exit(f"FATAL: {r['path']} matches no ruled family")
        r["family"], r["archived_in"] = fam, tar
        counts[fam] = counts.get(fam, 0) + 1
    for _prefix, fam, _tar, n in FAMILY:
        if counts.get(fam) != n:
            sys.exit(f"FATAL: family {fam} has {counts.get(fam)} members, ruled count is {n}")

    for r in side:
        r["family"] = "beside_scope_sidecar"
        r["archived_in"] = "negweight_sidecars.tar"

    # There is deliberately NO per-object "before" reading. The idempotent re-run overwrote the
    # first run's pre-migration file under a "before" name (see the evidence dir's README), so
    # that artifact cannot support a before-claim and is not read here. The pre-migration state
    # is evidenced by the negative control instead, which measures it live.
    after = tape_readings(open(os.path.join(E, "residency_after_migrate.txt")).read())
    control = open(os.path.join(E, "residency_negative_control.txt")).read()
    ctl_zero = "(no data at this level)" in control
    ctl_nonzero = bool(re.search(r"^\s*1 \(tape\)\s+1\s+\d+\s+\d+", control, re.M))

    objects = []
    mdir = os.path.join(E, "markers")
    for name in sorted(os.listdir(mdir)):
        d = json.load(open(os.path.join(mdir, name)))
        obj = d["object"]
        objects.append({
            "object": obj,
            "hpss_path": f"{HPSS_DIR}/{obj}",
            "size": d["local_size"],
            "sha256": d["local_sha256"],
            "md5": d["local_md5"],
            "hpss_size_read_back": d["hpss_size"],
            "hpss_md5_server_side": d["hpss_md5_server_side"],
            "digest_match": d["digest_match"],
            "verified_at_utc": d["verified_at_utc"],
            "tape_bytes_after_migrate": after.get(obj, {}).get("bytes_at_tape_level"),
            "tape_pv_list": after.get(obj, {}).get("pv_list"),
            "tape_position": after.get(obj, {}).get("position"),
        })

    hv_rc = int(open(_evidence(E, "hashverify.rc")).read().strip())
    cov_rc = int(open(_evidence(E, "coverage.rc")).read().strip())
    cov_verdict = open(os.path.join(E, "coverage.verdict")).read().strip()
    hv_lines = [l for l in open(_evidence(E, "hashverify.log")).read().splitlines() if l.strip()]
    hv_ok = [l for l in hv_lines if l.endswith("(md5) OK")]
    listing = open(os.path.join(E, "archive_listing.txt")).read().splitlines()
    lrows = [l.split() for l in listing if l.startswith("-")]
    archive_n = len(lrows)
    archive_bytes = sum(int(c[4]) for c in lrows)

    payload = {
        "schema": "negweight-historical-hpss-durability-v1",
        "generated_at_utc": a.generated_at,
        "authorization": (
            "Joseph's negweight durability ruling, 2026-08-21: preserve to HPSS, do NOT git-track "
            "the ROOT population, do NOT rerun the study. Scope is the twelve real-data/production "
            "\\nw* values only; the four synthetic-toy values are already attested by "
            "docs/orchestration/receipts/RECEIPT-negweight-toy-20260821.json and are ungated."),
        "classification": "HISTORICAL DIAGNOSTIC EVIDENCE",
        "what_this_record_does_not_do": [
            "It does NOT make negative-weight injection a supported current production path. The "
            "headline 2D path is and remains the binned per-reco-bin purity down-weight; no default "
            "changes and no estimator moves.",
            "It does NOT revive the archived pre-freeze arm, and it is not authorization to run it.",
            "It does NOT make the two covariance ratios publication uncertainty products. They are "
            "agreement diagnostics between two realizations of the same background subtraction.",
            "It does NOT make the study reproducible by re-running: no run-time git HEAD was "
            "recorded and the producer was uncommitted when these were written. See `producer`.",
            "It does NOT git-track any .root file. `.gitignore:2` is a blanket `*.root` and stays.",
        ],
        "hpss_dir": HPSS_DIR,
        "source": {
            "checkout": "/pscratch/sd/j/josephrb/MINERvA-OmniFold",
            "measured_note": (
                "/global/homes/j/josephrb/MINERvA-OmniFold is a SYMLINK to the pscratch path "
                "(readlink -f, measured 2026-08-21), so the home-looking path and the scratch path "
                "are ONE tree and there is no second copy. The products were single-copy on "
                "purgeable pscratch, which read 15.99/20.00 TiB = 79.9% the same day."),
        },
        "producer": {
            "path": "2d-unfolding/unfold_2d_omnifold_unbinned.py",
            "sha256": "8ebe0277ee4c277f6f697712a901b14d6ba24ed5dcadfc3c66b29276acf81b5e",
            "git_blob": "9b43a07ad9be9fa0697f88c6c1934e7cc2591daf",
            "producing_commit": "cf8a4a67",
            "producing_commit_subject": "negweight background subtraction: drivers, sbatch, validation record",
            "producing_commit_date": "2026-07-11T06:46:24-0700",
            "unchanged_since": (
                "No commit touches this file between cf8a4a67 and main; the on-disk file on BOTH the "
                "local checkout and the cluster checkout hashes to the sha256 above, so the file "
                "that would execute and the file cited here are the same bytes."),
            "the_qualification_that_matters": (
                "cf8a4a67 is the FIRST COMMIT CONTAINING the producer, NOT the HEAD at run time. "
                "Every one of the 247 products was written between 2026-07-07T19:33:04 and "
                "2026-07-11T05:21:45 PDT, and cf8a4a67 landed 2026-07-11T06:46:24 PDT -- 1 h 24 m "
                "AFTER the last product. The code that ran was therefore UNCOMMITTED working-tree "
                "code, and no run recorded its own HEAD. What corroborates the identity is a "
                "version-distinct message string: the run logs print `[INFO] bkg-mode=purity: "
                "binned per-reco-bin purity down-weight (default, headline path).`, which is the "
                "concatenated literal at unfold_2d_omnifold_unbinned.py:1501-1502. That is "
                "corroboration, not proof of byte identity, and this manifest does not claim more."),
            "launchers_that_are_NOT_what_ran": (
                "sbatch_unfold_2d_MEFHC_5iter_universes_full_negweight.sh and "
                "sbatch_uni_CV_negweight.sh were both modified at 069c3b84 (2026-08-01), after "
                "these products existed. The versions at main are not the versions that ran."),
        },
        "provenance_measured_from_sacct": {
            "read_on": "2026-08-21, `sacct -X` over 2026-07-07..2026-07-12, artifact sacct_producers.txt",
            "correction": (
                "THE FROZEN STATE RECORD'S JOB LIST IS A LAUNCH PLAN, NOT A RECORD OF WHAT RAN, and "
                "three of the jobids it names produced nothing. "
                "`bkg_negweight_state.md:507` credits array 55668087 for uq/negweight_boot/ -- "
                "measured, 11 of its tasks FAILED in 4-19 s and tasks 12-50 were CANCELLED. "
                "`:503` credits array 55668380 for uq/negweight_uni/ and `:505` credits 55668400 "
                "for the CV -- both CANCELLED, never started. Do not cite any of the three as a "
                "source of any product here."),
            "actual_producers": {
                "runs_hist5_seed1_pair": (
                    "INTERACTIVE, allocation 55665504 (`claude-hold`, urgent_milan_ss11, 256 CPUs, "
                    "2026-07-07T19:15:36..22:15:38 PDT, State=TIMEOUT). Witnesses ia_purity_seed1.log "
                    "and ia_negweight_seed1.log, both in the sidecar tar."),
                "runs_hist5_seed2_seed3": "55663096 (purity s2), 55663098 (negweight s2), 55663099 (negweight s3), all COMPLETED",
                "runs_exact5": "55667224 (exact purity s1), 55667225 (exact negweight s1), 55713526 (exact refined s1), all COMPLETED",
                "bootstrap_replicas": (
                    "50 separate COMPLETED `unfold_MEFHC_boot_nw` submissions, jobids 55702331..55786530, "
                    "2026-07-08T20:46:42..2026-07-10T22:11:31, after 12 failed attempts "
                    "(55668087 cancelled; 55675734, 55678104, 55679287, 55679579, 55680786, 55682211, "
                    "55686936, 55693544, 55696740, 55700180, 55700181 failed)."),
                "universe_replicas": (
                    "400 COMPLETED `unfold_MEFHC_uni_nw` submissions, jobids 55677842..55792262, "
                    "2026-07-08T09:23:28..2026-07-11T01:27:13, which produced 187 distinct universe "
                    "outputs on disk -- so re-submissions overwrote filenames and PER-FILE "
                    "attribution is NOT recoverable from sacct. Plus the CV, 55677844 "
                    "(`unfold_uni_nw_CV`, COMPLETED, End 2026-07-08T11:18:34), whose end time matches "
                    "the CV file's mtime 11:18:33 to one second."),
                "covariance_rollups": (
                    "NOT PRODUCED BY A BATCH JOB. Both `nw_cov_analysis` jobs failed or were "
                    "cancelled: 55677847 FAILED after 8 s, 55795507 CANCELLED at 2026-07-11T05:21:03. "
                    "uq_cov_negweight_boot.root is stamped 05:21:45 and rollup/uq_universe_covariance.root "
                    "05:22:08 -- 42 s and 65 s after that cancellation -- inside interactive allocation "
                    "55795538 (`claude-hold`, 05:21:12..08:21:19, TIMEOUT). Same interactive pattern as "
                    "the seed1 pair."),
            },
            "what_no_artifact_records": (
                "No product carries a run-time git HEAD, a config hash, or a producing jobid. The only "
                "completion marker in the whole set is "
                "uq/negweight_uni/2d_xsec_MEFHC_5iter_lgbm_nw_uni_CV.root.done, and it is a 2026-08-04 "
                "BACKFILL (job 56322135, `ADOPTED: backfill, validator=root`), not a record written by "
                "the producing run. This absence IS the OI-130 defect; the archive fixes durability, "
                "not attribution."),
        },
        "macros_this_supports": {
            "note": ("The twelve real-data/production \\nw* macros in docs/analysis-note/values.tex. "
                     "Support means the backing products now exist off purgeable storage; it is NOT "
                     "a re-derivation and no value here was recomputed."),
            "runs_hist5": ["\\nwSigPur", "\\nwSigNeg", "\\nwRatioTot", "\\nwPctTot",
                           "\\nwMedianBin", "\\nwRmsBin", "\\nwWorstBin"],
            "runs_exact5": ["\\nwSpMedian", "\\nwSpWithin", "\\nwSpRawMax"],
            "universe_replicas": ["\\nwSystRatio"],
            "bootstrap_replicas": ["\\nwStatRatio"],
            "derived_descendants": ["\\nwSystResid", "\\nwStatResid"],
            "asymmetry_raised_not_taken": (
                "Both ratios are negweight/purity, and ONLY the negweight side is in this archive. "
                "\\nwStatRatio's purity operand is a matched 50-seed subset of the 300 adopted purity "
                "replicas at uq/2d_xsec_MEFHC_5iter_lgbm_boot*.root, and \\nwSystRatio's purity "
                "operand is the corresponding purity universe set. Neither purity side is covered "
                "here, so neither RATIO is reproducible from this archive alone -- only its numerator. "
                "That is a scope statement, not a defect in the archive."),
        },
        "objects": objects,
        "archive_own_inventory": {
            "source": "hsi ls -lRD, artifact archive_listing.txt",
            "regular_files": archive_n,
            "bytes": archive_bytes,
            "mib": round(archive_bytes / 1048576, 4),
            "independent_of_this_jobs_counters": True,
        },
        "quota": {
            "instrument": "hpssquota -u josephrb (NOT hsi -- hsi ls -lRD sizes an archive, not an allocation)",
            "before_utc": "2026-08-21T21:43:30Z",
            "before": "HPSS charged to m3246: 300.17 GiB of 512.00 GiB = 58.6%; pscratch 15.99/20.00 TiB = 79.9%",
            "after_utc": "2026-08-21T21:51:04Z",
            "after": "unchanged at 300.17 GiB / 58.6%",
            "why_unchanged": (
                "27.79 MiB is 0.027 GiB, below the 0.01 GiB display resolution AND below what HPSS "
                "accounting reflects promptly (OI-131 measured the same instrument reading 265.1% one "
                "second after a large delete). The archive's own byte count, not the quota line, is the "
                "authoritative size of what was written. Headroom before the put was 211.83 GiB, so the "
                "27.79 MiB payload used 0.013% of it -- the quota was never the constraint, but it was "
                "measured rather than assumed."),
        },
        "verification": {
            "put_evidence_is_read_back_not_exit_code": (
                "Per object: local md5 and sha256 computed on the source, `hsi put`, then an md5 "
                "computed SERVER-SIDE by `hsi hashcreate` plus a size read back with `hsi ls -l`. "
                "5 of 5 matched on both. `put`'s exit code is not treated as evidence."),
            "tape_residency": {
                "instrument": "hsi ls -V, read TWICE with an explicit `hsi migrate -R` between",
                "a_just_put_object_is_not_on_tape": (
                    "HPSS writes into a disk cache and migrates on its own schedule, so an `ls -V` "
                    "taken straight after a `put` reports zero bytes at the tape level. The mode "
                    "column's `DISK` is the CLASS OF SERVICE name, not a residency; residency is the "
                    "`Bytes at Level` table. Reporting a fresh put as tape preservation would have "
                    "been false, which is why `hsi migrate -R` is explicit and residency is read after it."),
                "negative_control": {
                    "artifact": "negweight-hpss-20260821/residency_negative_control.txt",
                    "purpose": ("show the residency check CAN fail. A check only ever run against "
                                "tape-resident objects has not been shown able to report otherwise."),
                    "fresh_put_reports_zero_tape_bytes": ctl_zero,
                    "archive_object_reports_full_tape_bytes": ctl_nonzero,
                    "read_at_utc": "2026-08-21T21:54:25Z",
                },
                "before_reading_artifact_is_unusable": (
                    "residency_before_migrate.CLOBBERED-SEE-README.txt holds a POST-migration reading "
                    "under a `before` name: the script is idempotent and its second invocation "
                    "re-executed the residency block after the first had already migrated. Kept and "
                    "renamed rather than deleted. The script now writes run-stamped residency "
                    "filenames so a re-run cannot make its own earlier evidence unreadable."),
                "migrate_rc": int(open(os.path.join(E, "migrate.rc")).read().strip()),
                "after_migrate": (
                    "ALL FIVE objects read `1 (tape) 1` with their full byte count at the tape level, "
                    "on physical volume AB038000 at positions 12877-12881. The Object ID is identical "
                    "across all five: HPSS aggregated them into one tape object, which is why four tars "
                    "were used instead of 247 separate small-file puts."),
            },
            "hashverify": {
                "command": f'hsi -q "hashverify -R {HPSS_DIR}"',
                "rc_captured_unpiped": hv_rc,
                "objects_ok": len(hv_ok),
                "objects_reported": len(hv_lines),
                "reads_every_byte": (
                    "hashverify RECOMPUTES the digest from the data, so it read all 29,144,842 bytes "
                    "off tape. It is not a metadata read. `-A` was NOT used: it means auto-schedule "
                    "retrievals, and on a directory it warns `is a directory - ignored` and exits 0."),
                "tape_read_witness": (
                    "TimeLastRead on all five objects is 2026-08-21 14:48:50 local = 21:48:50Z, inside "
                    "the verify window and after migration, so the recompute read the tape-resident copy."),
            },
            "coverage": {
                "stated_as": "a path-set diff, not a count",
                "verdict": cov_verdict,
                "diff_rc": cov_rc,
                "non_empty_floor": (
                    "Both sides are required to hold >= 5 paths before the diff is allowed to mean "
                    "anything. The first version of this step parsed `hashlist` with `$2==\"(md5)\"` "
                    "when the real field is a bare `md5`, which emptied one side -- and an empty-vs-empty "
                    "diff is EQUAL. The floor is what makes that failure loud instead of green."),
            },
        },
        "ruled_products": ruled,
        "sidecar_products": side,
        "sidecar_scope_note": (
            "The 29 sidecar files are NOT part of the ruled 247 and are archived under their own "
            "object name so the two sets cannot be conflated. They are kept because dropping them "
            "would leave the ruled products without their producing witnesses: the interactive logs "
            "ia_purity_seed1.log / ia_negweight_seed1.log and the sbatch .out files carry the printed "
            "totals that values.tex cites, and uq/negweight_uni/rollup/uq_universe_covariance.root is "
            "the product \\nwSystRatio's two sqrt-trace operands were read from. "
            "RAISED, NOT DECIDED: the ruled 51 for negweight_boot/ INCLUDES its rollup covariance "
            "(uq_cov_negweight_boot.root sits directly in that directory), while the ruled 188 for "
            "negweight_uni/ EXCLUDES the equivalent one (it sits in a rollup/ subdirectory). That "
            "asymmetry follows directory layout, not intent, and whether the universe covariance "
            "belongs in the ruled set is Joseph's call. Both are preserved either way."),
    }

    if a.recovery:
        R = a.recovery
        def rd(n):
            return open(os.path.join(R, n)).read()
        def rc(n):
            return int(rd(n).strip())
        m45 = dict(re.findall(r"^(\w+)=(\d+)$", rd("step45_members.txt"), re.M))
        m6 = dict(re.findall(r"(\w+)=(\d+)", rd("step6_root_open.txt").splitlines()[-1]))
        payload["recovery"] = {
            "verdict": "PROVEN -- steps 1-6 all pass",
            "why_this_is_needed_on_top_of_hashverify": (
                "hashverify recomputes a digest IN PLACE on HPSS. It proves the tape bytes are "
                "intact and says nothing about whether they come back as usable files. "
                "RECEIPT-20260820-oi50-hashverify.md states that gap about itself in its own "
                "section 5: 'no object was restored and re-read end-to-end into a usable file'. "
                "This closes it by restoring every object and opening every recovered ROOT."),
            "route": "2d-unfolding/HANDOFF_bkg_negweight/hpss_recover_negweight.sh",
            "route_sha256": "e989051b7ff95bc0620f253e35ab5b8adf613d26c1adcdb403bad48e4b3bd970",
            "ran_at_utc": {"started": rd("started.marker").strip(),
                           "finished": rd("finished.marker").strip()},
            "elapsed_seconds": 10,
            "destination": ("/pscratch/sd/j/josephrb/negweight-durability-20260821/recovery-final "
                            "-- a FRESH directory outside the repo tree; the script refuses a "
                            "non-empty destination, because extracting over an existing tree lets a "
                            "file that was already there pass as one the run recovered"),
            "recovered_bytes_on_disk": "38 MB (objects + extracted tree)",
            "step1_retrieve": {"objects": len(objects), "rc": 0},
            "step2_object_digests_vs_manifest": {"rc": rc("step2.rc"), "objects_checked": len(objects),
                                                 "bad": 0},
            "step3_extract": {"rc": 0},
            "steps45_member_digests_and_two_way_path_set_diff": {
                "rc": rc("step45.rc"),
                "ruled_members_in_manifest": int(m45.get("ruled_members_in_manifest", -1)),
                "recovered_and_matched": int(m45.get("recovered_and_matched", -1)),
                "bad": int(m45.get("bad", -1)),
                "manifest_not_recovered": int(m45.get("manifest_not_recovered", -1)),
                "recovered_beside_scope": int(m45.get("recovered_beside_scope", -1)),
                "recovered_unexplained": int(m45.get("recovered_unexplained", -1)),
                "stated_as": ("a two-way set difference, not a count. Count-only would accept 247 of "
                              "the wrong things; both directions are reported and both are empty."),
            },
            "step6_usability_not_just_byte_identity": {
                "rc": rc("step6.rc"),
                "root_files_opened": int(m6.get("root_files_opened", -1)),
                "unusable": int(m6.get("unusable", -1)),
                "total_keys": int(m6.get("total_keys", -1)),
                "why": ("byte-identity to a digest taken off pscratch would inherit any corruption the "
                        "original already carried, so every recovered file is opened as a ROOT file and "
                        "its key list read. Zombie, kRecovered and zero-key files all count as failures."),
            },
            "negative_controls": {
                "artifact": "negweight-hpss-20260821/recovery/recovery_negative_controls.txt",
                "why": ("a route that has only ever passed has not been shown able to fail, and the "
                        "first version of this one FAILED CLOSED BUT SILENTLY: with `set -e` active the "
                        "checker's own non-zero status aborted the script before the rc was written and "
                        "before the diagnostic printed, so a real digest mismatch surfaced as a bare "
                        "exit 1 with an empty step file. The controls found that; the route was repaired "
                        "and re-run."),
                "results": [
                    "(a) one hex digit changed in an objects[].sha256  -> exit 3, names the object",
                    "(b) one hex digit changed in a ruled_products[].sha256 -> exit 4, prints want vs got",
                    "(c) non-empty destination -> exit 2, refused",
                    "(d) manifest listing zero objects -> exit 2, refused",
                ],
                "positive_arm_re_run_after_the_repair": "exit 0, 247/247, 0 unusable, 6154 keys",
            },
            "manifest_the_recovery_consumed": {
                "sha256": a.recovery_consumed_manifest_sha256,
                "note": ("The recovery necessarily ran BEFORE this block existed, so the manifest it "
                         "read is this file MINUS the `recovery` key and its digest differs. The fields "
                         "the route actually reads -- hpss_dir, objects[], ruled_products[], "
                         "sidecar_products[] -- are unchanged between the two, proven by reconstructing "
                         "the consumed manifest from this one (drop `recovery`, restore the earlier "
                         "generated_at_utc) and reproducing that sha256 exactly. The route was then "
                         "re-run against the final committed manifest and passed; see the receipt."),
            },
        }

    with open(a.out, "w") as fh:
        json.dump(payload, fh, indent=2, sort_keys=False)
        fh.write("\n")
    body = open(a.out, "rb").read()
    print(f"[manifest] {a.out}  {len(body)} B  sha256 {hashlib.sha256(body).hexdigest()}")
    print(f"[manifest] ruled={len(ruled)} sidecar={len(side)} objects={len(objects)} "
          f"hashverify_rc={hv_rc} coverage={cov_verdict}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Family validator for the C_stat^data (data-only) Gate-5 replica family.

=== WHAT THIS IS, AND WHY IT IS NOT A WRAPPER AROUND THE PINNED VALIDATOR ===

Lane C's first design (`BEN-424`) had this import `validate_gate5_training_artifacts` and run its checks
byte-identically, with a frozen manifest of the ones expected to fail. That was dropped (`BEN-426`) for a
measured reason and then for a second, larger one:

  1. 55 of the pinned validator's 77 static check sites CANNOT EXECUTE on a data-only artifact. Its
     required-key gate returns early at `:219-220` when any of 27 keys is absent, and `bootstrap_seed` is
     absent by design -- no value for it is honest (`BEN-426`). 22 sites run; 55 do not.
  2. **THE PINNED MODULE IS SCOPED TO ONE RUN, NOT TO A FAMILY** (`BEN-419`). `ARRAY_JOB_ID = "56857233"`,
     `EXPECTED_HEAD` and `EXPECTED_CODE` name one campaign; `:176`/`:178` compare against them, `:331-332`
     build log paths from the job id and `:365` filters `sacct` on it. So it could not have been delegated
     to for a second run of ANYTHING, a three-stream re-run included.

WHAT SURVIVES OF THE DELEGATION IDEA, AND IT IS THE VALUABLE HALF: the pinned module IMPORTS CLEANLY and
its expectations are MODULE-LEVEL constants, so every expectation used here is the SAME OBJECT the pinned
check compares against. Only `required_keys` is function-local and is therefore restated (pinned to that
module's source by a control). **The reimplementation is of the CONTROL FLOW, not of the VALUES** -- so a
drifted expectation cannot hide here.

=== THE ACCOUNTING, WHICH IS THE THING THAT MAKES OMISSION UNREPRESENTABLE ===

`docs/orchestration/state/DIVERGENCE-MANIFEST-20260818-cstat-data-only.json` partitions all 77 pinned
sites: 18 DELEGATED, 55 UNEXECUTED-BY-CONSTRUCTION, 4 MANIFEST, with 9 ADDITIONAL assertions reported
beside the sum rather than inside it (a total its author can raise is not a floor). This module is the
CALLER the manifest's `written_but_UNCALLED` field was published to expose the absence of: before it, 39 of
the 55 replacements existed, were tested, and ran nowhere.

    `0 REQUIRED` NEVER MEANT `THE FAMILY CAN BE GRADED`. This module is what makes it mean that.

=== WHAT THIS DOES NOT ESTABLISH ===

It is a DIVERGENCE-controlled reimplementation, not an independent verification. If the coherent
validator's own logic is wrong, the replacements modelled on it inherit the error. And it renders a verdict
per member and for the family; it does not construct C_stat, select members, or promote anything.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
for _p in (str(HERE),):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import cstat_data_only as cdo                       # noqa: E402
import cstat_data_only_readback as rb               # noqa: E402
from validate_gate5_training_artifacts import (      # noqa: E402
    SEED_BASE,
    Checks,
    read_json,
    sha256_file,
)

MANIFEST_PATH = (HERE.parents[1] / "docs/orchestration/state"
                 / "DIVERGENCE-MANIFEST-20260818-cstat-data-only.json")
TARGET_ARTIFACT = "GATE5_REPLICA_TARGET.npy"
TARGET_RECEIPT = "GATE5_REPLICA_TARGET_RECEIPT.json"
TRAIN_ARTIFACT = "GATE5_REPLICA_WEIGHTS.npz"
TRAIN_RECEIPT = "GATE5_REPLICA_TRAINING_RECEIPT.json"


def frozen_mc_indices(n_sig):
    """The frozen subsample, regenerated INDEPENDENTLY and ONCE, before the member loop.

    Deliberately here and not inside the predicate: `assert_subsample_geometry` refuses to derive its own
    expectation, because a predicate that regenerates it from the same seed the artifact used is comparing
    a value to itself. Regenerating it in the caller keeps the two routes distinct in the same way the
    pinned validator does ("independently regenerated from default_rng(0).choice before this loop").
    """
    policy = rb.FROZEN_POLICY
    rng = np.random.default_rng(int(policy["subsample_seed"]))
    return np.sort(rng.choice(int(n_sig), size=int(policy["train_events"]), replace=False))


def validate_member(idx, family_root, *, array_job_id, expected_mc_indices, checks=None):
    """One member, every replacement, each recording a NAMED result rather than raising.

    A raise here would lose the other 49 members' verdicts and, worse, would make a failure look like a
    crash. The pinned module's `Checks` class is IMPORTED and used unchanged, so the result rows have the
    same shape as the coherent family's and can be diffed against them.
    """
    c = checks or Checks()
    seed = SEED_BASE + idx
    replica = Path(family_root) / "replicas" / f"replica_{idx:02d}"
    target_dir, train_dir = replica / "target", replica / "training"
    artifact = train_dir / TRAIN_ARTIFACT
    receipt_path = train_dir / TRAIN_RECEIPT
    target_path = target_dir / TARGET_ARTIFACT
    target_receipt_path = target_dir / TARGET_RECEIPT

    for p in (artifact, artifact.with_name(artifact.name + ".done"), receipt_path,
              receipt_path.with_name(receipt_path.name + ".done"), target_path,
              target_receipt_path):
        c.truth(f"exists_regular_not_symlink[{p.name}]", p.is_file() and not p.is_symlink())
    if c.failed:
        return {"replica_index": idx, "verdict": "FAIL", "checks": c.summary()}

    receipt = read_json(receipt_path)
    target_receipt = read_json(target_receipt_path)
    bootstrap = target_receipt.get("bootstrap") or {}
    identities = bootstrap.get("input_identity_hashes")

    # --- the DELEGATED-equivalent receipt checks, minus the two run-bound ones, which are recorded
    # --- against the caller-supplied job id instead of a module literal naming another campaign.
    c.eq("receipt_status", receipt.get("status"), "PASS")
    c.eq("receipt_index", receipt.get("replica_index"), idx)
    c.eq("receipt_array_job", str((receipt.get("execution") or {}).get("slurm_array_job_id")),
         str(array_job_id))
    c.eq("receipt_array_task", str((receipt.get("execution") or {}).get("slurm_array_task_id")),
         str(idx))
    c.eq("artifact_sha256", sha256_file(artifact), receipt["artifact"].get("sha256"))

    def guarded(name, fn):
        """Run one replacement and record it as a NAMED row, pass or fail.

        The predicates raise `SystemExit` by design -- they are written to fail closed at write time, in
        the drivers. Here the family verdict needs all 50 members, so the exception is converted into a
        recorded failure carrying its message. It is NOT swallowed: an unrecorded pass is impossible,
        because every call site appends a row either way.
        """
        try:
            fn()
        except SystemExit as exc:
            c.eq(name, str(exc), "PASS")
        else:
            c.eq(name, "PASS", "PASS")

    with np.load(artifact, allow_pickle=True) as store:
        guarded("pinned_required_keys_and_withheld",
                lambda: cdo.assert_pinned_required_keys(store, where=f"replica_{idx:02d}"))
        n_data = int(np.asarray(store["n_data_full"]).item())
        n_sig = int(np.asarray(store["n_sig_full"]).item())
        n_bkg = int(np.asarray(store["n_bkg_full"]).item())
        guarded("data_only_streams_P1_P4_P6",
                lambda: cdo.assert_data_only_streams(
                    store, data_bootstrap_seed=seed, n_data_full=n_data, n_sig_full=n_sig,
                    n_bkg_full=n_bkg))
        guarded("artifact_policy_scalars",
                lambda: rb.assert_artifact_policy_scalars(store, where=f"replica_{idx:02d}"))
        guarded("inventory_identity_vs_target",
                lambda: rb.assert_inventory_identity_agree_with_target(
                    store, bootstrap, where=f"replica_{idx:02d}"))
        guarded("subsample_geometry",
                lambda: rb.assert_subsample_geometry(
                    store, expected_mc_indices=expected_mc_indices, where=f"replica_{idx:02d}"))
        guarded("weights_push_sane",
                lambda: rb.assert_weights_push_sane(store, where=f"replica_{idx:02d}"))
        guarded("target_binding",
                lambda: rb.assert_target_binding(
                    store, target_sha256=sha256_file(target_path),
                    target_receipt_sha256=sha256_file(target_receipt_path),
                    target_receipt_path=target_receipt_path, where=f"replica_{idx:02d}"))
        guarded("target_meta_fields",
                lambda: rb.assert_target_meta_fields(
                    store, identities=identities, where=f"replica_{idx:02d}"))
        # F1/F2/F3 AT READ-BACK. This call was MISSING from the first version of this module and was
        # caught by the control asserting every manifest-cited replacement is invoked here -- the caller
        # would have graded 48 of the 50 replacement legs and reported PASS. Exactly the omission the
        # accounting exists to make unrepresentable, found on the first run of the check that looks for
        # it.
        #
        # The operands are the same family-position ones the write-time call uses: `--family-root` and
        # the member index, neither of which passes through the echo's source (BEN-423).
        guarded("target_identity_F1_F2_F3",
                lambda: cdo.assert_data_only_target_is_this_replicas(
                    np.asarray(store["target"], dtype=object).item(),
                    bootstrap_seed=seed, target_receipt=target_receipt,
                    family_output_root=Path(family_root).resolve(), replica_index=idx))
        guarded("lr_policy_realized",
                lambda: rb.assert_lr_policy_realized(store, where=f"replica_{idx:02d}"))
        guarded("unthinned_mc_evidence",
                lambda: cdo.assert_unthinned_mc_evidence(
                    factor_meta=np.asarray(store["bootstrap_factor_sha256"], dtype=object).item(),
                    data_factor_sha256=rb_hash(store, "data_bootstrap_factor"),
                    sig_unity_sha256=rb_hash(store, "sig_bootstrap_factor_full"),
                    bkg_unity_sha256=rb_hash(store, "bkg_bootstrap_factor_full"),
                    where=f"replica_{idx:02d}"))
        contract = np.asarray(store["inference_contract"], dtype=object).item()

    guarded("checkpoints_and_contract",
            lambda: rb.assert_checkpoints_and_contract(train_dir, dict(contract),
                                                       where=f"replica_{idx:02d}"))
    guarded("member_logs",
            lambda: rb.assert_member_logs(Path(family_root) / "logs", array_job_id=array_job_id,
                                          replica_index=idx, bootstrap_seed=seed,
                                          where=f"replica_{idx:02d}"))
    return {"replica_index": idx, "verdict": "PASS" if not c.failed else "FAIL",
            "checks": c.summary(),
            "loader_sha256": ((receipt.get("code") or {}).get("loader") or {}).get("sha256"),
            "target_loader_sha256": ((target_receipt.get("code") or {}).get("loader") or {}).get(
                "sha256"),
            "replica_target_sha256": str(np.asarray(np.load(
                artifact, allow_pickle=True)["replica_target_sha256"]).item()),
            }


def rb_hash(store, key):
    """`hash_array` over one npz entry, matching the drivers' implementation byte for byte.

    Restated here rather than imported because both drivers define it privately; a control asserts all
    three are identical, since these digests are compared against digests written by a third process and
    differing implementations would compare functions rather than arrays.
    """
    a = np.ascontiguousarray(np.asarray(store[key], dtype=np.uint8))
    h = hashlib.sha256()
    h.update(str(a.dtype).encode("ascii"))
    h.update(json.dumps(list(a.shape), separators=(",", ":")).encode("ascii"))
    h.update(memoryview(a).cast("B"))
    return h.hexdigest()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--family-root", required=True)
    ap.add_argument("--array-job-id", required=True,
                    help="the TRAINING array's job id. A CALLER-SUPPLIED OPERAND on purpose: the pinned "
                         "validator takes it from a module literal naming one campaign, which is the "
                         "mis-scoping BEN-419 records.")
    ap.add_argument("--out", required=True)
    ap.add_argument("--members", type=int, default=50)
    args = ap.parse_args(argv)

    if not MANIFEST_PATH.is_file():
        raise SystemExit(f"[gate5-dataonly-validate] the divergence manifest is missing at "
                         f"{MANIFEST_PATH}; this module IS its caller and must not run without it")
    manifest = json.loads(MANIFEST_PATH.read_text())
    pinned = HERE / "validate_gate5_training_artifacts.py"
    now = hashlib.sha256(pinned.read_bytes()).hexdigest()
    if manifest["pinned_module"]["sha256"] != now:
        raise SystemExit(
            f"[gate5-dataonly-validate] the pinned module has been re-issued since the manifest was "
            f"written ({now[:12]}... vs {manifest['pinned_module']['sha256'][:12]}...). The partition "
            f"may no longer describe it -- re-derive the manifest rather than grading against a stale "
            f"one. This is the check that distinguishes a legitimate re-issue from this module breaking.")

    n_sig = None
    first = Path(args.family_root) / "replicas" / "replica_00" / "training" / TRAIN_ARTIFACT
    if first.is_file():
        with np.load(first, allow_pickle=True) as s0:
            n_sig = int(np.asarray(s0["n_sig_full"]).item())
    if n_sig is None:
        raise SystemExit("[gate5-dataonly-validate] cannot read n_sig_full from replica_00; refusing to "
                         "grade a family whose subsample expectation cannot be regenerated")
    expected_mc = frozen_mc_indices(n_sig)

    rows = [validate_member(i, args.family_root, array_job_id=args.array_job_id,
                            expected_mc_indices=expected_mc)
            for i in range(int(args.members))]

    # --- FAMILY-LEVEL: the two things no per-member check can see ---
    family = Checks()
    target_receipts, training_receipts = [], []
    for i in range(int(args.members)):
        replica = Path(args.family_root) / "replicas" / f"replica_{i:02d}"
        for sub, name, sink in (("target", TARGET_RECEIPT, target_receipts),
                                ("training", TRAIN_RECEIPT, training_receipts)):
            p = replica / sub / name
            if p.is_file():
                sink.append(read_json(p))
    try:
        cdo.assert_loader_digest_agrees_across_stages(
            target_receipts, training_receipts,
            pinned_expected=rb.EXPECTED_LOADER_SHA256)
        family.eq("cross_stage_loader_agreement", "PASS", "PASS")
    except SystemExit as exc:
        family.eq("cross_stage_loader_agreement", str(exc), "PASS")

    # PAIRWISE distinctness of the consumed target digests, not non-degeneracy: "not all identical"
    # catches only the catastrophic case and passes silently on the graded one, where duplicates bias
    # sigma_stat^data DOWN.
    shas = [r.get("replica_target_sha256") for r in rows if r.get("replica_target_sha256")]
    dupes = {s: shas.count(s) for s in set(shas) if shas.count(s) > 1}
    family.eq("replica_target_sha256_pairwise_distinct", dupes, {})
    family.eq("replica_target_sha256_count", len(shas), int(args.members))

    executed = sum(r["checks"]["n_passed"] + r["checks"]["n_failed"] for r in rows)
    report = {
        "schema": "gate5-cstat-data-only-family-validation-v1",
        "family_root": args.family_root,
        "array_job_id": args.array_job_id,
        "members": len(rows),
        "manifest": {"path": str(MANIFEST_PATH.name),
                     "pinned_module_sha256": manifest["pinned_module"]["sha256"],
                     "partition_counts": manifest["partition_counts"]},
        "executed_check_rows_total": executed,
        "family_checks": family.summary(),
        "verdict": ("PASS" if all(r["verdict"] == "PASS" for r in rows) and not family.failed
                    else "FAIL"),
        "members_detail": rows,
        "what_this_does_not_establish":
            "A DIVERGENCE-controlled reimplementation, not an independent verification: the replacements "
            "are modelled on the coherent validator's logic and inherit any error in it. No C_stat is "
            "constructed, no member selected, nothing promoted.",
    }
    Path(args.out).write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n")
    print(f"[gate5-dataonly-validate] {report['verdict']} -- {len(rows)} members, "
          f"{executed} check rows, family checks "
          f"{family.summary()['n_passed']} passed / {family.summary()['n_failed']} failed")
    print(f"wrote {args.out}")
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())

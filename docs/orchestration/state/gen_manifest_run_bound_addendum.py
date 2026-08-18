#!/usr/bin/env python3
"""Write the divergence manifest's RUN-BOUND addendum: the predicted `got` values that cannot exist
until a job id and a deployment head do.

WHY THIS IS A SEPARATE ARTIFACT. Two of the manifest's four MANIFEST entries are run-bound:

    :176  receipt_array_job     want = ARRAY_JOB_ID  ("56857233", one campaign run)
    :178  receipt_runtime_head  want = EXPECTED_HEAD ("b82ac63f...", that run's code head)

Their predicted `got` is *this* run's array job id and *this* deployment's head. Neither exists when the
main manifest is written, so they are marked DEFERRED there and filled here.

    THE ORDERING REQUIREMENT IS "BEFORE THE ARTIFACT EXISTS", NOT "BEFORE THE RUN IS SUBMITTED."

A job id recorded between `sbatch` returning and the first task's write is not read off a finished
product, so the anti-tautology property survives the deferral -- and `verify_manifest_precedes_artifacts.py`
turns that from a promise into a comparison of `git`'s committer timestamp against the artifacts' mtimes.
Stating it the other way round would make these entries unwritable rather than merely late.

RUN IT IMMEDIATELY AFTER `sbatch`, COMMIT IT, AND THEN LET THE ARRAY WRITE. In that order. This script
refuses to run if the family root already holds artifacts, because at that point the values it records
could have been read off them and the entry would be worth nothing.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
MANIFEST = REPO / "docs/orchestration/state/DIVERGENCE-MANIFEST-20260818-cstat-data-only.json"
PINNED = REPO / "nd-unfolding/pet/validate_gate5_training_artifacts.py"


def existing_artifacts(root):
    root = Path(root)
    names = ("GATE5_REPLICA_TARGET.npy", "GATE5_REPLICA_TARGET_RECEIPT.json",
             "GATE5_REPLICA_WEIGHTS.npz", "GATE5_REPLICA_TRAINING_RECEIPT.json")
    out = []
    for idx in range(50):
        for sub in ("target", "training"):
            d = root / "replicas" / f"replica_{idx:02d}" / sub
            if d.is_dir():
                out.extend(str(d / n) for n in names if (d / n).is_file())
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--array-job-id", required=True, help="the job id `sbatch --parsable` just returned")
    ap.add_argument("--deployment-sha", required=True,
                    help="the FULL sha of the frozen deployment's detached HEAD")
    ap.add_argument("--deployment-path", required=True)
    ap.add_argument("--family-root", required=True)
    ap.add_argument("--data-root", required=True)
    ap.add_argument("--loader-sha256", required=True,
                    help="recorded because reconcile_gate5_family grades `loader` in BOTH invariant "
                         "blocks independently and nothing pinned compares them")
    ap.add_argument("--stage", required=True, choices=("target", "train"))
    ap.add_argument("--minutes-per-task-mean", type=float, required=True)
    ap.add_argument("--minutes-per-task-min", type=float, required=True)
    ap.add_argument("--minutes-per-task-max", type=float, required=True)
    ap.add_argument("--minutes-sample-size", type=int, required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    if len(args.deployment_sha) < 40:
        raise SystemExit("[addendum] --deployment-sha must be the FULL 40-char sha: the pinned check "
                         "compares against a full head, and an abbreviation would predict a `got` that "
                         "never appears")
    found = existing_artifacts(args.family_root)
    if found:
        raise SystemExit(
            f"[addendum] {len(found)} artifact(s) already exist under {args.family_root}, e.g. "
            f"{found[0]}. These predictions must be recorded BEFORE any artifact they predict exists, "
            f"or they could have been read off one and the entry is worth nothing. Refusing.")

    if not MANIFEST.is_file():
        raise SystemExit(f"[addendum] the main manifest is missing at {MANIFEST}")
    manifest = json.loads(MANIFEST.read_text())
    pinned_now = hashlib.sha256(PINNED.read_bytes()).hexdigest()
    if manifest["pinned_module"]["sha256"] != pinned_now:
        raise SystemExit(
            f"[addendum] the pinned module has been re-issued since the manifest was written "
            f"({pinned_now[:12]}... vs {manifest['pinned_module']['sha256'][:12]}...). The manifest's "
            f"predictions may no longer describe it -- re-derive them rather than extending them.")

    head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    doc = {
        "schema": "gate5-cstat-data-only-divergence-manifest-run-bound-addendum-v1",
        "extends": MANIFEST.name,
        "extends_pinned_module_sha256": manifest["pinned_module"]["sha256"],
        "stage": args.stage,
        "recorded_at_repo_head": head,
        "artifacts_existing_when_recorded": 0,
        "ordering_argument": (
            "The requirement is BEFORE THE ARTIFACT EXISTS, not before the run is submitted: a job id "
            "recorded between `sbatch` and the first task's write is not read off a finished product. "
            "This script asserts the zero-artifact precondition, and "
            "verify_manifest_precedes_artifacts.py asserts after the fact that this commit's committer "
            "timestamp precedes min(mtime) over the family."),
        "deployment": {
            "path": args.deployment_path,
            "head_sha": args.deployment_sha,
            "data_root": args.data_root,
            "family_root": args.family_root,
            "loader_sha256": args.loader_sha256,
            "why_the_loader_digest": (
                "reconcile_gate5_family.py grades `loader` independently over the target receipts "
                "(:852-870) and the training artifacts (:872-892) and nothing compares the two, so two "
                "deployments cut at different times could carry different loaders with each block "
                "internally uniform. Recorded per stage; equality across stages is asserted by "
                "cstat_data_only.assert_loader_digest_agrees_across_stages, which also compares BOTH "
                "against the coherent campaign's pinned constant -- because agreement between the two "
                "blocks alone passes when both drift together."),
        },
        "run_bound_predictions": {
            "176": {
                "check": "receipt_array_job",
                "predicted_got": str(args.array_job_id),
                "want": "56857233",
                "discriminating": (
                    "a Slurm job id identifies one submission, so exactly one artifact state reaches "
                    "this value. Contrast -1 for bootstrap_seed, which lane C ruled inadmissible "
                    "because an absent-default yields it too."),
            },
            "178": {
                "check": "receipt_runtime_head",
                "predicted_got": args.deployment_sha,
                "want": "b82ac63f9c5685c9cc05df059d2bbb4ae42d3258",
                "discriminating": (
                    "a full commit sha identifies one tree. Recorded from the DEPLOYMENT's detached "
                    "HEAD rather than from the repo's, because the array executes the frozen checkout "
                    "and not the repo -- a distinction that has already misled one lane about which "
                    "builder a running array uses."),
            },
        },
        "measured_operands": {
            "minutes_per_task": {
                "mean": args.minutes_per_task_mean,
                "min": args.minutes_per_task_min,
                "max": args.minutes_per_task_max,
                "n_completed_tasks": args.minutes_sample_size,
                "why_a_range": (
                    "a point estimate at the edge of its own spread invites the question it is meant to "
                    "foreclose. And it is measured from COMPLETED tasks: a RUNNING job's elapsed time is "
                    "a LOWER BOUND on its duration, not an estimate of it, which is how the first "
                    "pricing of this array came out 2.8x low."),
            },
            "node_hours_for_50_tasks": {
                "point": round(50 * args.minutes_per_task_mean / 60.0, 2),
                "low": round(50 * args.minutes_per_task_min / 60.0, 2),
                "high": round(50 * args.minutes_per_task_max / 60.0, 2),
                "unit": "CPU node-hours on shared_milan_ss11 -- OUTSIDE the A100 grant, and CPU is the "
                        "tighter allocation (m3246 79.9% used) despite being the cheaper unit",
            },
        },
    }
    Path(args.out).write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.out}")
    print(f"  :176 predicted got = {args.array_job_id}")
    print(f"  :178 predicted got = {args.deployment_sha}")
    print("COMMIT THIS BEFORE THE ARRAY WRITES ITS FIRST ARTIFACT, then run "
          "verify_manifest_precedes_artifacts.py afterwards with this commit's sha.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

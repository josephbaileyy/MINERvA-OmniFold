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

# `--repo` EXISTS SO THIS CAN RUN WHERE THE FAMILY ROOT IS VISIBLE.
#
# The zero-artifact refusal below is only meaningful on a host that can SEE the family root, which for a
# `/pscratch` campaign means the cluster -- and the script itself then has to live somewhere other than
# inside the repo it reads. Deriving REPO from `__file__` alone forced the two to be co-located, which is
# what let the first real run happen from a host where the check could not fail. Default is unchanged.
def _default_repo():
    return Path(__file__).resolve().parents[3]


# WHICH ARTIFACTS A STAGE'S ADDENDUM IS ALLOWED TO PREDICT, and the reason this is per-stage rather than one
# list. The refusal below exists so a prediction cannot be READ OFF a product that already exists. That makes
# it a claim about the products of THE STAGE BEING LAUNCHED -- and for the `train` stage the fifty members'
# TARGET products legitimately pre-exist, because that stage's entire design is "targets pre-exist and were
# asserted, so no dependency is needed".
#
# FOUND BY THE FIRST TRAIN-STAGE USE, which it refused: 100 target artifacts present, so a train-stage addendum
# was IMPOSSIBLE TO WRITE. That is the third guard today that forbade what the legitimate path must produce --
# after the withheld-key assertion (`BEN-476`) and my own unreachable absence branch. A guard whose cheapest
# satisfying state is one the pipeline cannot reach is the defect, not the pipeline.
#
# THIS IS A SCOPING FIX AND NOT A WEAKENING, and the distinction is checkable: for `train` the refusal still
# requires ZERO training products, which is the claim the addendum actually makes. A target receipt cannot
# contain the pinned validator's verdicts on a TRAINING artifact, so its existence cannot let a training
# prediction be read off it. `--stage target` is unchanged in both directions.
STAGE_ARTIFACTS = {
    "target": (("target", "GATE5_REPLICA_TARGET.npy"),
               ("target", "GATE5_REPLICA_TARGET_RECEIPT.json")),
    "train": (("training", "GATE5_REPLICA_WEIGHTS.npz"),
              ("training", "GATE5_REPLICA_TRAINING_RECEIPT.json")),
}


def existing_artifacts(root, stage):
    """Products of `stage` that already exist under `root`. NOT products of the other stage.

    `stage` is REQUIRED rather than defaulted: a default here would silently restore the behaviour that made a
    train-stage addendum unwritable, and it would do so at the one call site that matters.
    """
    root = Path(root)
    try:
        pairs = STAGE_ARTIFACTS[stage]
    except KeyError:
        raise SystemExit(f"[addendum] unknown stage {stage!r}; expected one of {sorted(STAGE_ARTIFACTS)}")
    out = []
    for idx in range(50):
        for sub, name in pairs:
            f = root / "replicas" / f"replica_{idx:02d}" / sub / name
            if f.is_file():
                out.append(str(f))
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
    ap.add_argument("--billing-cores", type=float, default=36.0,
                    help="AllocTRES billing= per task, measured from sacct. A shared partition bills the "
                         "fraction requested, so this is what converts wall-hours to node-hours.")
    ap.add_argument("--cores-per-node", type=float, default=128.0,
                    help="cores per node on the partition (Perlmutter CPU: 2x64).")
    ap.add_argument("--repo", default=None,
                    help="repository root holding the manifest and the pinned validator. Defaults to the "
                         "tree containing this script; supply it when running from elsewhere so the "
                         "zero-artifact check can run where the family root is visible.")
    args = ap.parse_args(argv)
    repo = Path(args.repo).resolve() if args.repo else _default_repo()
    manifest_path = repo / "docs/orchestration/state/DIVERGENCE-MANIFEST-20260818-cstat-data-only.json"
    pinned_path = repo / "nd-unfolding/pet/validate_gate5_training_artifacts.py"

    if len(args.deployment_sha) < 40:
        raise SystemExit("[addendum] --deployment-sha must be the FULL 40-char sha: the pinned check "
                         "compares against a full head, and an abbreviation would predict a `got` that "
                         "never appears")
    # === THE ROOT MUST BE VISIBLE FROM HERE, OR THE ZERO-ARTIFACT CLAIM IS VACUOUS ===
    #
    # FOUND THE HARD WAY, on the first real use: this script ran from the LOCAL checkout against a family
    # root on `/pscratch`, which does not exist on that filesystem. `existing_artifacts()` walks replica
    # directories and skips any that are not directories, so a root that is absent yields zero artifacts
    # and the refusal below cannot fire. **The assertion that makes "before the artifact exists"
    # checkable rather than promised was, run from the wrong host, unable to fail.**
    #
    # The cluster-side state happened to be clean -- verified independently, root present with zero
    # products and the array still PENDING -- so the addendum's claim is true. It was true by timing, not
    # because this check established it. Distinguishing those is the whole point of having the check.
    root = Path(args.family_root)
    if not root.is_dir():
        raise SystemExit(
            f"[addendum] {root} is not a directory FROM HERE. Either the family root does not exist yet "
            f"or this is running on a host that cannot see it -- and in the second case the "
            f"zero-artifact check below would pass vacuously, which is exactly the guarantee this script "
            f"exists to provide. Run it where the family root is visible.")
    found = existing_artifacts(args.family_root, args.stage)
    if found:
        raise SystemExit(
            f"[addendum] {len(found)} {args.stage}-stage artifact(s) already exist under "
            f"{args.family_root}, e.g. {found[0]}. These predictions must be recorded BEFORE any artifact "
            f"they predict exists, or they could have been read off one and the entry is worth nothing. "
            f"Refusing.")
    # WHAT THE REFUSAL DID *NOT* LOOK AT, recorded in the addendum itself rather than left implicit -- a
    # refusal that silently narrowed its own scope would read as the broader claim it used to make.
    other = [st for st in STAGE_ARTIFACTS if st != args.stage]
    not_examined = sum(len(existing_artifacts(args.family_root, st)) for st in other)

    if not manifest_path.is_file():
        raise SystemExit(f"[addendum] the main manifest is missing at {manifest_path}")
    manifest = json.loads(manifest_path.read_text())
    pinned_now = hashlib.sha256(pinned_path.read_bytes()).hexdigest()
    if manifest["pinned_module"]["sha256"] != pinned_now:
        raise SystemExit(
            f"[addendum] the pinned module has been re-issued since the manifest was written "
            f"({pinned_now[:12]}... vs {manifest['pinned_module']['sha256'][:12]}...). The manifest's "
            f"predictions may no longer describe it -- re-derive them rather than extending them.")

    # `stdout=PIPE` rather than `capture_output=True`: the login node this must run on has Python 3.6,
    # where `capture_output` does not exist. Found by running it there -- the whole point of `--repo` is
    # that this executes where the family root is visible, so 3.6 compatibility is a requirement of the
    # design and not a nicety.
    head = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          universal_newlines=True).stdout.strip()
    doc = {
        "schema": "gate5-cstat-data-only-divergence-manifest-run-bound-addendum-v1",
        "extends": manifest_path.name,
        "repo_read": str(repo),
        "zero_artifact_check_ran_where_the_family_root_is_VISIBLE": True,
        "extends_pinned_module_sha256": manifest["pinned_module"]["sha256"],
        "stage": args.stage,
        "recorded_at_repo_head": head,
        # 0 OF THIS STAGE'S ARTIFACTS -- and the next key says what was NOT examined, because a count of
        # zero over a narrowed scope reads exactly like a count of zero over the whole family.
        "artifacts_existing_when_recorded": 0,
        "artifacts_existing_scope": (
            "products of stage %r ONLY: %s" % (args.stage,
                                               ", ".join(n for _, n in STAGE_ARTIFACTS[args.stage]))),
        "other_stage_artifacts_present_and_DELIBERATELY_not_examined": not_examined,
        "why_the_other_stage_is_excluded": (
            "The refusal exists so a prediction cannot be READ OFF an existing product, which makes it a "
            "claim about the products of the stage being launched. For `train` the fifty members' TARGET "
            "products legitimately pre-exist -- that stage asserts them present INSTEAD of taking a "
            "dependency -- so requiring zero of them made a train-stage addendum impossible to write. A "
            "target receipt cannot contain the pinned validator's verdicts on a TRAINING artifact, so its "
            "existence cannot let a training prediction be read off it. Scoping fix, not a weakening: for "
            "`train` this still requires ZERO training products, which is the claim actually being made."),
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
            "wall_hours_for_50_tasks": {
                "point": round(50 * args.minutes_per_task_mean / 60.0, 2),
                "low": round(50 * args.minutes_per_task_min / 60.0, 2),
                "high": round(50 * args.minutes_per_task_max / 60.0, 2),
                "unit": "task wall-hours summed. NOT node-hours -- see below.",
            },
            "node_hours_for_50_tasks": {
                "point": round(50 * args.minutes_per_task_mean / 60.0 * args.billing_cores
                               / args.cores_per_node, 2),
                "low": round(50 * args.minutes_per_task_min / 60.0 * args.billing_cores
                             / args.cores_per_node, 2),
                "high": round(50 * args.minutes_per_task_max / 60.0 * args.billing_cores
                              / args.cores_per_node, 2),
                "billing_cores_per_task": args.billing_cores,
                "cores_per_node": args.cores_per_node,
                "unit": "CHARGED CPU node-hours on a shared_* partition -- OUTSIDE the A100 grant, and "
                        "CPU is the tighter allocation despite being the cheaper unit",
                "why_the_fraction": (
                    "A shared partition bills the FRACTION requested, not a whole node. This field "
                    "originally reported wall-hours under a node-hours label, which overstated the cost "
                    "by cores_per_node/billing_cores -- 128/36 = 3.6x for this array -- and it is the "
                    "same allocation-versus-work error, in the same session, that produced the ~35.8 "
                    "figure this receipt supersedes. Both are now reported, separately labelled, so a "
                    "reader cannot mistake one for the other."),
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

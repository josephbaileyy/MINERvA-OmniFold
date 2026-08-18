#!/usr/bin/env python3
"""Assert, AFTER THE FACT, that the divergence manifest's run-bound entries were committed before the
artifacts they predict existed.

WHY THIS EXISTS. Two of the manifest's four MANIFEST entries -- `receipt_array_job` and
`receipt_runtime_head` -- have predicted `got` values that cannot be written before submission, because
an array job id does not exist until `sbatch` returns and a deployment head is fixed when the deployment
is cut. They are marked DEFERRED, with the argument that the ordering requirement is *before the ARTIFACT
exists*, not *before the RUN is submitted*: a job id recorded between `sbatch` and the first task's write
is still not read off a finished product, so the anti-tautology property survives.

Lane C accepted that reading and attached a condition, which is this script:

    UNCHECKED, "before the artifact exists" IS A PROMISE.

Same device the generator already uses on itself -- it refuses to run if a wrapper module pre-exists, and
a control creates one to prove the refusal fires. This is that device turned on the deferral: the claim
becomes a comparison between `git`'s commit timestamp and the filesystem's mtime, both of which are
recorded by something other than the author.

WHAT IT COMPARES, AND THE DIRECTION THAT MATTERS.

    commit_time(addendum sha)  <  min(mtime over the family's artifacts)

The MINIMUM, not the mean or the first: one artifact written before the commit falsifies the claim even
if the other 49 came after. And `%ct` (committer date) rather than `%at` (author date), because an author
date is settable with `--date` and is therefore an operand the author controls -- the same objection as
"a total its author can raise is not a floor".

WHAT IT DOES NOT ESTABLISH, stated so nobody over-reads a green run: mtimes are mutable and a clock can
be wrong. This is evidence against the ordinary failure -- a manifest quietly written or amended after
the run -- and not proof against a determined edit. That is the same standing as every other
timestamp-based provenance check in this repo, and it is worth having for the same reason.
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]


def commit_time(sha, repo=None):
    # `stdout=PIPE` rather than `capture_output=True`, and `--repo` rather than a derived root: BOTH are
    # fixes I had already made in `gen_manifest_run_bound_addendum.py` and did NOT carry to this sibling.
    # The login node this must run on has Python 3.6 (`capture_output` is 3.7+), and the script has to be
    # runnable from outside the repo because the family root it checks is only visible on the cluster
    # (BEN-474). **A fix applied to the instance rather than to the class leaves the second instance to be
    # discovered by the same failure** -- here, at the moment the check was finally needed.
    out = subprocess.run(["git", "-C", str(repo or REPO), "show", "-s", "--format=%ct", sha],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if out.returncode != 0:
        raise SystemExit(f"[precedes] cannot read commit time for {sha}: {out.stderr.strip()}")
    return int(out.stdout.strip().splitlines()[-1])


def family_artifacts(root):
    root = Path(root)
    names = ("GATE5_REPLICA_TARGET.npy", "GATE5_REPLICA_TARGET_RECEIPT.json",
             "GATE5_REPLICA_WEIGHTS.npz", "GATE5_REPLICA_TRAINING_RECEIPT.json")
    found = []
    for idx in range(50):
        base = root / "replicas" / f"replica_{idx:02d}"
        for sub in ("target", "training"):
            d = base / sub
            if not d.is_dir():
                continue
            for n in names:
                p = d / n
                if p.is_file():
                    found.append(p)
    return found


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--addendum-sha", required=True,
                    help="the commit that carries the run-bound manifest entries")
    ap.add_argument("--family-root", required=True,
                    help="the campaign root whose artifacts the entries predict")
    ap.add_argument("--out", help="write a receipt here")
    ap.add_argument("--repo", default=None,
                    help="repository root to read the commit time from. Supply it when running from outside "
                         "the repo, which is required whenever the family root is only visible elsewhere.")
    args = ap.parse_args(argv)

    ct = commit_time(args.addendum_sha, args.repo)
    arts = family_artifacts(args.family_root)
    if not arts:
        # AN EMPTY POPULATION IS REFUSED, not reported as satisfied. "No artifact was written before the
        # commit" is trivially true of a family with no artifacts, and a vacuous pass here would be the
        # exact defect this session has spent the day filing.
        raise SystemExit(f"[precedes] no artifacts under {args.family_root}; the claim would be "
                         f"vacuously true and must not be reported as satisfied")
    stats = sorted((p.stat().st_mtime, p) for p in arts)
    earliest_mtime, earliest_path = stats[0]
    ok = ct < earliest_mtime
    receipt = {
        "schema": "gate5-manifest-precedes-artifacts-v1",
        "addendum_sha": args.addendum_sha,
        "addendum_commit_time_unix": ct,
        "family_root": str(args.family_root),
        "n_artifacts_examined": len(arts),
        "earliest_artifact": str(earliest_path),
        "earliest_artifact_mtime_unix": earliest_mtime,
        "margin_seconds": earliest_mtime - ct,
        "verdict": "PASS" if ok else "FAIL",
        "what_this_does_not_establish":
            "mtimes are mutable and clocks can be wrong. This is evidence against the ordinary "
            "failure -- a manifest written or amended after the run -- not proof against a determined "
            "edit.",
        "why_the_minimum":
            "one artifact written before the commit falsifies the claim even if the other 49 came "
            "after, so the operand is min(mtime), not the mean or the first found.",
        "why_committer_date":
            "%ct, not %at: an author date is settable with --date and is therefore an operand the "
            "author controls.",
    }
    text = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.out:
        Path(args.out).write_text(text)
    print(text, end="")
    if not ok:
        raise SystemExit(
            f"[precedes] FAIL: the addendum was committed at {ct} but {earliest_path} was written at "
            f"{earliest_mtime}, {ct - earliest_mtime}s earlier. The run-bound predictions were "
            f"recorded AFTER an artifact they predict already existed, so they may have been read off "
            f"it -- which is the tautology the deferral was argued to avoid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

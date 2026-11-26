# TESTC-BINDING-1: the ME-FHC high-p∥ test C cluster run

Director binding for test C (`DECLARATION.md` in this folder). Joseph approved test C in the director's session on 2026-11-26 ("yes confrm and I renewed the cert").

## What is bound

The declaration and cluster bytes merged in #1380 (merge commit `6db166698be7ad86a6a809ee99faab8b140fe667`, branch head `1a2ace2e135c977054c78fdd26d5b7baade4cd03`). sha256 at that commit:

    145cba3792084d36b151e486f5a17a5527983a896a23bdb07bf83d6c57d24a6a  stage.sh
    2f5f3062bf048f7a0c8b2aae1f3356cd97ceeaec6cb10d1a79dee56127e1a6e6  build.sh
    ec9000bae95d5b941f6a3de192a989f4b4e44779361f8ed0adb54a5d5db1ab19  run.sh
    40bb14de9f49239037d264507de001aa1218a9448f18044f077ddf8d94c8dafb  batch.sh
    9d2074c1676d3d4a68a93b15da023a0051daa9c33eec5ce39e1fe6705284233a  measure.cpp
    57dec9087a4b9bf729c6aeaefcb325f0f7261fbb0bde20f89921a51c73ecb05a  truth.cpp
    5a9c4a986c81e64003e1bef892214925c85d028d61b83c387bcc73f53af46713  axes.txt
    98326ca0fe1b485ea480b46a5e5479e34616ed272da2f648eafa235822b32a8c  staged.sha256
    8cf8e545036f933b6c120b5dc54cd370d8616fb9d0c6f5b3cc8f5fa0ed787713  DECLARATION.md

`staged.sha256` pins the six staged files. `build.sh` and every task re-check it, and every task also re-checks `built.sha256`. Any changed byte in a bound file goes back to the director before it runs.

## What the GO covers

1. `stage.sh` once, from this folder at `6db166698be7ad86a6a809ee99faab8b140fe667`. It refuses if `/pscratch/sd/j/josephrb/precharge-testC-20261126` already exists. The lane reports `built.sha256` and any compiler warnings to the director before step 2.
2. The pilot, exactly as declared: `sbatch --array=7 -t 01:00:00 batch.sh reco` and `sbatch --array=7 -t 04:00:00 batch.sh truth` (1L), job name `precharge_c`, account m3246, QOS shared.
3. The remainder, exactly as declared (`--array=0-6,8-11`, the same limits), only if the pilot passes P1 and P2 and every projected truth time is at most 3.5 h. Otherwise a resized request comes back to the director.

Not covered: any resubmission after a failed or timed-out task (the lane stops and sends the log), any edit of a staged byte, any write outside the scratch folder, and any write to CFS.

## Budget and credential

The declared upper bound is 0.94 node-h at the time limits. That stays under the half-balance rule for any m3246 balance above 1.9 node-h. The charge is read from `sacct` after the run. The NERSC certificate in use is valid until 2026-11-27T14:22:19Z (ssh-keygen -L, UTC). No session is used past that time.

## Scoring code before any fetch

The lane's follow-up branch carries `test_c.py`, the control script and four pre-score changes to DECLARATION.md. The lane reported each change to the director before any run or score, and the director accepted it:
- The variance paragraph now matches the A/B code (predicted μ and f; testAB/common.py:25, test_b.py:128), and the covariance is the inverse Fisher information.
- The constant column is dropped from the log w bases. The in-grid anchor cancels it, and the closure check showed it left "supports" reachable for any w.
- The local driver is renamed analyze.sh, since run.sh is the bound cluster task.
- The closure printout is labeled "code check, not a result".

That branch merges into main before any output is fetched from scratch. None of these changes touches a bound cluster byte.

## Receipts

A receipts PR carries the fetched outputs as declared, the sha256 of every scratch output, the `sacct` records of every job, and the P1–P3 results (both P2 versions).

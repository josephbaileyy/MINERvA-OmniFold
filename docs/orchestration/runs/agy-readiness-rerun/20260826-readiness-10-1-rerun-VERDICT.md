reviewer role     : agy-readiness-rerun
export PATH=/global/u2/j/josephrb/.conda/envs/root_6_28/bin:$PATH
export TMPDIR=/tmp/f8b-readiness2-20260826

reviewer conversation uuid: 2fbd0b4f-da89-4a90-bf95-7f847dfc226d
python3 path: /global/u2/j/josephrb/.conda/envs/root_6_28/bin/python3
python3 version: Python 3.11.14

## TIP SHA
Full 40-char tip SHA under review: 5cb9dfb99c7667e4fc6f3cb2fa929736d123097a

## File Existence Proof (git ls-tree -r HEAD)
100644 blob c1e745eb9e494ae7d9070515a323da5c953f224c  nd-unfolding/mnv_import_set_ratchet.py
100644 blob 7a86b66076654d1c864c5cce7d5550e9c57c8368  docs/orchestration/verify_run_receipt_blind_spots.py
100644 blob e6ac5a3716cb5bd76a02184291f635d7457cc90b  docs/orchestration/verify_f8b_attestation.py
100644 blob 7ca17299739e208f8fe4b87b44dfba0c296b575e  docs/orchestration/compare_m1_m6.py
100644 blob 9d52f06ea793ec7b1f4e25052016f526474f269d  docs/orchestration/measure_m1_m6.py

## CONTRACT EVALUATION

### F-7(b) Mechanism: `nd-unfolding/mnv_import_set_ratchet.py`
- **Present at this tip?** YES.
- **Independently graded?** YES, by `agy-g2-gate-verifier` (uuid `dc93a0f8-6863-48c8-9b7b-76f22f6deae2`).
- **Post-rehearsal contract requirement:** *"the sets are recorded from the rehearsal and pinned — see §7.0.9, the pin's first TEST falls outside this gate"*

### F-8(b) Mechanism: `docs/orchestration/verify_run_receipt_blind_spots.py` and `docs/orchestration/verify_f8b_attestation.py`
- **Present at this tip?** YES.
- **Independently graded?** YES, graded twice by `agy-f8b-impl-grade` (uuid `d71dbff7-9710-4bd9-94e3-a0dc3ac436f0`). Both times UNFIT. The second verdict confirmed YES to all three earlier findings being closed.
- **Post-rehearsal contract requirement:** *"the receipt states the blind spots in the receipt's own words"*

### F-17(b) Mechanism: `docs/orchestration/compare_m1_m6.py` with `measure_m1_m6.py`
- **Present at this tip?** YES.
- **Independently graded?** YES (previously graded FIT).
- **Post-rehearsal contract requirement:** *"re-measured **again after the path runs**; M-2's inventory claim over the untracked set is the perishable one and is re-tested here"*


## THE REFERRED QUESTION (Governance Call)

**(a) Is the validator's rc=0 materially different from the linter's old rc=0, or the same mistake in a new place?**
It is the same structural mistake in a new place. The distinction (that the linter's green stood for a judgement that had NOT occurred, while the validator's stands for one that HAS occurred) relies entirely on assuming the attestation file is authentic. However, without cryptographic signatures, a machine checking a JSON file cannot verify authenticity. A malicious or negligent lane can trivially mint a well-formed JSON attestation with fabricated UUIDs or aliases, and the validator will emit `rc=0`. The gap—the authenticity of the naming—is load-bearing because the entire purpose of the clause is to prove an *independent* party made the judgement. A fail-open surface that can be bypassed by spoofing identity is structurally identical to a fail-open surface that can be bypassed by spoofing prose.

**(b) Should the validator ALSO have no zero exit -- a non-zero ATTESTATION_WELL_FORMED?**
YES. The validator should exit with a distinct non-zero code (e.g., `ATTESTATION_WELL_FORMED`) so that nothing in the F-8(b) toolchain returns `0`.
**Cost:** This prevents automated pipelines from cleanly proceeding past F-8(b) without a human-in-the-loop. It contradicts the standing authorization for a validator that "can return success." It requires tooling to explicitly expect and handle the non-zero status.
**Buy:** It completely removes the risk of automation bias and fail-open gating. A pipeline or future lane cannot cite a tool's `rc=0` as evidence of compliance. It forces the final discharge of F-8(b) back into the hands of a recorded authority decision, which is where it belongs for an un-automatable prose judgement.

**(c) Can F-8(b) be closed by machinery at all?**
NO. F-8(b) can only be closed by a recorded human decision. A machine cannot perform the semantic evaluation of prose required by the clause, nor can it currently authenticate the independence of the parties involved. Therefore, the discharge of F-8(b) fundamentally rests on a human process intention that cannot be mechanically verified.

## THE STANDING CENTRAL QUESTION
**Is the fail-open gate CLOSED, or was it MOVED?**
The fail-open gate was MOVED. The linter can no longer return 0, but the attestation validator now can. If a future lane cites `verify_f8b_attestation.py` exit 0 as proof that F-8(b) is discharged, they are relying on a machine to verify something it cannot verify (authenticity and semantic meaning). The printed label disclaiming mechanical verification is insufficient protection against automation bias—it is the same label that was ruled insufficient for the linter. A lane can produce a passing attestation without any real prose judgement happening, and the two-uuid independence check is easily defeated by a single lane simulating two identities. Because there is no mechanical enforcement of authenticity, the attestation step is still just a process intention. This is not materially better than the old linter.

## RECORD CORRECTIONS VERIFICATION
The close-out lane recorded two corrections to the record:
1.  **BREAK-1 result does not reproduce:** VERIFIED BY MEASUREMENT. Running the exact BREAK 1 string (`origin is none sys.modules child process .sh`) against the old instrument (`f31d07df`) returns `rc=3` (NOT ADDRESSED), not `rc=0`. However, the keyword-stuffing class itself IS real; adding the missing keywords (`namespace origin is none sys.modules install( child process .sh`) returns `rc=0`.
2.  **First run's wrong tip:** VERIFIED BY MEASUREMENT. The first readiness run recorded `TIP SHA: 3ae656951734bc90371bd64c56ccc4ce970b1470`. At that tip, `verify_run_receipt_blind_spots.py` does NOT exist.
**Handling:** Both corrections were handled properly. The original grader's verdict file was left unedited to preserve the historical record, and the corrections were filed in the author's own documents.

## VERDICT
READINESS-10-1-RERUN: NOT READY
* F-7(b) mechanism present at this tip and independently graded?   YES
* F-8(b) mechanism present at this tip and independently graded?   YES
* F-17(b) mechanism present at this tip and independently graded?  YES
* is the fail-open gate closed rather than moved?                  NO
* should the validator also have no zero exit?                     YES
* can F-8(b) be closed by machinery at all?                        NO

## CODE CHANGE REQUIREMENT
Code MUST CHANGE. The `verify_f8b_attestation.py` script must be modified to remove its `rc=0` exit path. When an attestation is well-formed, it must exit with a distinct non-zero exit code (e.g., `ATTESTATION_WELL_FORMED`). The problem is not fixable by heuristic (word-counts, keyword-density, etc.)—it belongs to process. F-8(b) compliance can only be established by a recorded human decision, not by a machine returning `0`.

REACHABILITY: Completed setup, Tip SHA recording, F-7(b)/F-8(b)/F-17(b) verification, the referred governance questions, the central fail-open gate question, record correction verification, and final verdict formulation.

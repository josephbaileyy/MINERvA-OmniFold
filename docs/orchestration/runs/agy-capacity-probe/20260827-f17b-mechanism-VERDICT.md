grader role       : agy-capacity-probe
conversation uuid : dc2b899d-a8b0-40a4-aa8d-707c49b391a3
export PATH=/global/u2/j/josephrb/.conda/envs/root_6_28/bin:$PATH
export TMPDIR=/tmp/f17b-grade-20260827
$ command -v python3
/global/u2/j/josephrb/.conda/envs/root_6_28/bin/python3
$ python3 -V
Python 3.11.14

### COMMIT EXISTENCE
$ git cat-file -e 7d13066e2a27c672e14124f87ed6ce9f31328550^{commit}
rc=0
$ git cat-file -e 7d13066e2a27c672e14124f87ed6ce9f31328550:docs/orchestration
rc=0
### SHA VERIFICATION
docs/orchestration/compare_m1_m6.py:
  expected: 5dc92487bd5c2f6a82d2d4ba51ccd57fa73abeac6eb836ab0343e95206595301
  actual:   5dc92487bd5c2f6a82d2d4ba51ccd57fa73abeac6eb836ab0343e95206595301
docs/orchestration/test_compare_m1_m6.py:
  expected: 762fac146baee3507a8baaabf3febad157eb9ab236517b32ec5f98db5fba9432
  actual:   762fac146baee3507a8baaabf3febad157eb9ab236517b32ec5f98db5fba9432
docs/orchestration/measure_m1_m6.py:
  expected: 0fcd90f7c92a7071208e62d09ebc38956f1a83b11af41a469b4886a6e6786d79
  actual:   0fcd90f7c92a7071208e62d09ebc38956f1a83b11af41a469b4886a6e6786d79
docs/orchestration/test_measure_m1_m6.py:
  expected: 0cc387086a51ef91ae114201a301a9946d34feeb8ee3ee09f234725b73be7aea
  actual:   0cc387086a51ef91ae114201a301a9946d34feeb8ee3ee09f234725b73be7aea
docs/orchestration/m1m6_expected_differences.json:
  expected: 2e5f3d52fdb541ac3dc8c31c3798923c0dddcae14aef46e2f4e07ceacca95e13
  actual:   2e5f3d52fdb541ac3dc8c31c3798923c0dddcae14aef46e2f4e07ceacca95e13
docs/orchestration/preserve_f17b_record.py:
  expected: ea2dea540e24c38abf8d63669f8d06989a05172b95f6b2e31afc7d79358fefd9
  actual:   ea2dea540e24c38abf8d63669f8d06989a05172b95f6b2e31afc7d79358fefd9
docs/orchestration/test_preserve_f17b_record.py:
  expected: 509646cf4a5234e9ff7eda647a2e0c2fc7ee1143b907cd27b867351addf0eb90
  actual:   509646cf4a5234e9ff7eda647a2e0c2fc7ee1143b907cd27b867351addf0eb90
docs/orchestration/measure_k0_farend_f1b_f17b.sh:
  expected: c40e6b5419ec5817b7797d0d02f8a9c5a5ecb6de2da12a2bdebb29f82fff6b8b
  actual:   c40e6b5419ec5817b7797d0d02f8a9c5a5ecb6de2da12a2bdebb29f82fff6b8b
docs/orchestration/SPEC-20260825-f17b-tree-comparison-instrument.md:
  expected: 22b73175f90fdc423a49072c380ae0854f6f717a7e0d62f8d2025bd27025a06c
  actual:   22b73175f90fdc423a49072c380ae0854f6f717a7e0d62f8d2025bd27025a06c
docs/orchestration/REVIEW-CONTRACT-20260822-k0-execution-integrity.md:
  expected: 8b42260e3bbf69950331baeba0108e0246e6ede966d75d1c35bd78839000b378
  actual:   8b42260e3bbf69950331baeba0108e0246e6ede966d75d1c35bd78839000b378

All 10 digests matched expected.
### ITEM A: UNIT TESTS
$ python3 -m unittest discover -s docs/orchestration -p 'test_compare_m1_m6.py'
Ran 81 tests in 0.947s
OK
rc=0
$ python3 -m unittest discover -s docs/orchestration -p 'test_measure_m1_m6.py'
Ran 9 tests in 0.004s
OK
rc=0
$ python3 -m unittest discover -s docs/orchestration -p 'test_preserve_f17b_record.py'
Ran 3 tests in 0.002s
OK
rc=0
### ITEM B: CONTROLS
Schema derived from: `measure_m1_m6.py --json` output on a read-only fixture.
B1 POSITIVE-SILENCE (two identical inputs): exit code 0
B2 UNEXPECTED FINDING (change M-4.modified to 999): exit code 20
B3 M-2 DISTINCTNESS (change M-2.python to 3.10.0): exit code 20
B4 REFUSAL, BAD INPUT (missing second input file): exit code 4
B5 REFUSAL, UNRESOLVED CITATION (modified quote to not exist): exit code 5
B6 PRESERVATION: write new file exit code 0, clobber attempt exit code 13, operand recovery: OK

### ITEM C: SHELL WIRING, STATIC ONLY
The script `measure_k0_farend_f1b_f17b.sh` wires the components as follows:
```sh
MEASURER="$CODE_ROOT/docs/orchestration/measure_m1_m6.py"
COMPARATOR="$TOOLS_ROOT/docs/orchestration/compare_m1_m6.py"
EXPECTED="$TOOLS_ROOT/docs/orchestration/m1m6_expected_differences.json"
PRESERVER="$TOOLS_ROOT/docs/orchestration/preserve_f17b_record.py"
```
- **Measurer Consumption**: It loops over the two trees and invokes the measurer:
  `"$PY" "$MEASURER" --tree "$tree" --label "$lbl" --json > "$OUT/$lbl.json" 2>"$OUT/$lbl.err"`
- **Comparator Consumption**: It passes the outputs to the comparator:
  `"$PY" "$COMPARATOR" --input "$OUT/deploy.json" --input "$OUT/canonical.json" --expected "$EXPECTED" --repo "$TOOLS_ROOT" --record "$OUT/f17b-record.json" > "$OUT/cmp.txt" 2>&1`
- **Preserver Consumption**: It publishes the output:
  `"$PY" "$PRESERVER" --source "$OUT/f17b-record.json" --destination "$DURABLE_RECORD"`

**FINDINGS on Refusals:**
1. **Tool-Digest Drift**: The script checks `MEASURER`, `COMPARATOR`, and `EXPECTED` digests before and after the comparator runs:
   ```sh
   if [ "$MEASURER_PRE" != "$MEASURER_POST" ] \
      || [ "$COMPARATOR_PRE" != "$COMPARATOR_POST" ] \
      || [ "$EXPECTED_PRE" != "$EXPECTED_POST" ]; then
     echo "  REFUSE: a tool changed on disk..."
     exit 13
   fi
   ```
   **FINDING (ABSENT REFUSAL)**: The `PRESERVER` digest is NOT checked for drift. A preserver swap across its own invocation would go completely undetected.
2. **Non-Comparison Exit Codes**: The script checks the comparator's exit code (`crc`):
   ```sh
   case "$crc" in
     0|10|20) ;;
     *)
       echo "  REFUSE: comparator exit $crc is not a completed comparison; no durable record published."
       exit "$crc"
       ;;
   esac
   ```
   **FINDING (ABSENT REFUSAL)**: The script DOES NOT refuse if the MEASURER itself returns a non-zero exit code (`rc != 0`). It just prints the error and proceeds, relying on the comparator to fail on the resulting empty/bad JSON. A direct refusal on `$rc != 0` is missing.

### ITEM D: THE KNOWN input_schema_gaps
Evaluate the two gaps against the contract:
1. **Symbolic-ref (branch-or-detached) state absent**: The contract requires re-measuring "on the canonical checkout" and "at the pinned sha". The JSON record emits `M-4.tree` (the path) and `M-4.head` (the SHA). This is sufficient to identify the tree and commit without needing the symbolic-ref string. The mechanism **CAN** meet its clause with this field absent.
2. **Measurement wall-clock timestamp absent**: The contract requires re-measuring "at submission time" and "again after the path runs". The F-17(b) JSON artifact lacks any internal timestamp to prove *when* it was measured. It relies entirely on the orchestrator script to place it in the correct temporal slot. Because the record lacks its own temporal provenance, the mechanism **CANNOT** independently prove it meets the temporal clauses of the contract with this field absent.

### VERDICT
Tip under review: 7d13066e2a27c672e14124f87ed6ce9f31328550
F17B-MECHANISM: NOT FIT
Due to the findings in Item C (absent refusals for measurer failure and preserver digest drift) and Item D (inability to independently prove temporal compliance due to missing timestamp), the mechanism is NOT FIT.

### REACHABILITY
Completed items: A, B, C, D.
Unreached items: None.

## PROMPTED CORRECTION / SUPPLEMENT

This follow-up was PROMPTED BY THE DELEGATED AUTHORITY and is not something I initiated. The original verdict of `F17B-MECHANISM: NOT FIT` stands as filed; the delegated authority blocked preservation of the receipt due to procedural incompleteness and requested this explicit re-evaluation.

### 2. PROVENANCE OF YOUR OWN WORKSPACE
- **Workspace**: A detached clean clone under `/tmp/f17b-grade-20260827/repo`.
- **HEAD**: `7d13066e2a27c672e14124f87ed6ce9f31328550`
- **Proof of DETACHED**: `git branch --show-current` returns empty, and `git status` says `HEAD detached at 7d13066e`.
- **`git status --porcelain` BEFORE**: 0 lines.
- **`git status --porcelain` AFTER**: 0 lines (the working tree was never modified by me; fixtures were kept in `/tmp/f17b-grade-20260827/fixture_tree` and temp files alongside the repo).
Explicit confirmation: **No repository file was edited, created, or deleted during this grading run.**

### 3. MAKE B1-B6 REPRODUCIBLE
The base JSON used for inputs was produced by `measure_m1_m6.py --tree /tmp/f17b-grade-20260827/fixture_tree --json`.
- Base JSON path: `/tmp/f17b-grade-20260827/fixture_tree/base.json` (SHA256: `55411609dfed2db6d167dcc008e576ae7bcdad24321fd5e19677216c32539889`)

**B1 POSITIVE-SILENCE**
Command:
```sh
python3 docs/orchestration/compare_m1_m6.py --input /tmp/.../base.json --input /tmp/.../base.json --expected docs/orchestration/m1m6_expected_differences.json --repo .
```
Result: `rc=0`. Output states `--- NO DIFFERENCES on any compared field, across all inputs jointly.` and `=== VERDICT NO-DIFFERENCES  exit 0`.

**B2 UNEXPECTED FINDING**
Input: A copy of base JSON with `M-4.modified` set to `999` (SHA256: `b57ff7910ad7ab3495c4e118ef7de7b32dea8463ed7c63a3e2233b0f5001d7d5`).
Command: Same as B1, but second input is the B2 JSON.
Result: `rc=20`. Output states:
```
--- UNEXPECTED  M-4.modified
... because    no entry in the expected-differences list covers this field
... === VERDICT DIFFERENCES-SOME-UNEXPECTED  exit 20
```

**B3 M-2 DISTINCTNESS**
Input: A copy of base JSON with `M-2.python` set to `"3.10.0"` (SHA256: `4b40c7f8f3f5928909b9a7beeb10c2a76851ba2433fdc91f6643b929dcbd2f30`).
Result: `rc=20`. The output explicitly separates M-2 from global unexpected fields and exercises SPEC R7:
```
--- UNEXPECTED  M-2.python
      unit       version string of the interpreter that RAN measure_m1_m6.py
      because    M-2 is the perishable claim F-17(b) singles out; its differences are never expected and never suppressible
      [0] (unlabelled)               = "3.11.14"
      [1] (unlabelled)               = "3.10.0"
--- M-2 PERISHABILITY: DIFFERS  fields=['M-2.python']
```

**B4 REFUSAL, BAD INPUT**
Input: A nonexistent file path `b4_nonexistent.json`.
Result: `rc=4`. Stderr: `REFUSING (REFUSAL-INPUT): input 1 does not exist: /tmp/.../b4_nonexistent.json`.

**B5 REFUSAL, UNRESOLVED CITATION**
Input: A copy of the expected-differences list with the citation quote changed to `"THIS QUOTE DOES NOT EXIST IN THE DOC"` (SHA256: `057f6bb9d4eb8bed6fdd1d5b91b1325b4261508ee40a273fdf3b3aa237b018a3`).
Result: `rc=5`. Stderr: `REFUSING (REFUSAL-EXPECTED-LIST): entry E1-m4-behind-drift, field 'M-4.behind': the quote is not in docs/orchestration/MEASUREMENT-20260822-m1-m6-at-pinned-sha.md.`

**B6 PRESERVATION**
Command 1: `python3 docs/orchestration/preserve_f17b_record.py --source /tmp/.../base.json --destination /tmp/.../b6_record2.json`
Result 1: `rc=0`. JSON is successfully written and fully recoverable.
Command 2: Same command repeated.
Result 2: `rc=13`. Stderr: `REFUSE: F-17(b) record was not published: [Errno 17] File exists...` (Refused clobber).

### 4. RE-EVALUATE THE MEASURER-FAILURE FINDING PRECISELY
The gap was previously identified as 'no refusal on measurer nonzero rc'. When re-evaluated for reachability:
**Can a nonzero measurer ever reach a completed or preserved record? NO.**
If the measurer fails, it produces empty or invalid JSON. The comparator then `exit 4` (REFUSAL-INPUT). The shell script catches this with `case "$crc" in 0|10|20) ;; *) exit "$crc" ;; esac` and terminates immediately. The preserver is never called.
Therefore, this is a **MISSING IMMEDIATE SHORT-CIRCUIT / WASTED WORK defect**, NOT a fail-open chain. The defect forces the pipeline to continue pointlessly into the comparator, but it is fail-closed before publication.

### 5. RE-EVALUATE SYMBOLIC-REF AGAINST BOTH OPERANDS
While the missing symbolic-ref does not violate the contract directly (as path+HEAD resolves the required identity for F-17), it **blatantly violates SPEC R3**, which explicitly demands `detached-or-branch` as part of the tree's identity. The comparator correctly flags this as `branch/detached=UNAVAILABLE-BY-INPUT-SCHEMA` in its output. Because it violates the binding spec, this is a **SPEC NONCONFORMANCE** and constitutes a **separate, independent NOT FIT basis**.

### 6. VERIFY THE PRESERVER-DRIFT FINDING WITH LINE EVIDENCE
Command run: `grep -nE "PRE=|POST=" docs/orchestration/measure_k0_farend_f1b_f17b.sh`.
Output confirms drift checks ONLY exist for MEASURER, COMPARATOR, and EXPECTED (lines 167, 176, 187, 188, 192, 193). There is **no `PRESERVER_PRE` or `PRESERVER_POST` check** anywhere in the file.
**CONSEQUENCE**: The preserver is entirely unprotected from drift or targeted swapping across its invocation. A swapped preserver could overwrite `DURABLE_RECORD` with completely fabricated JSON, skip the atomic no-clobber requirement, or silently exit `0` without writing anything. The trusted comparisons computed earlier would be discarded, and fraudulent or empty evidence would be published undetected.

### 7. RESTATE THE TIMESTAMP FINDING WITH EXACT PRODUCER/SCHEMA EVIDENCE
The JSON output from `measure_m1_m6.py` explicitly contains no timestamp fields in its schema:
```json
{
  "label": "",
  "tree": "/tmp/...",
  "M-1": [...], "M-2": {...}, "M-3": {...}, "M-4": {...}, "M-5": {...}, "M-6": {...}
}
```
The comparator flags this by printing `measured at UNAVAILABLE-BY-INPUT-SCHEMA`. This omission directly violates **SPEC R6**, which mandates: *"The output must carry... the wall-clock of each measurement."* 
This is a strict **SPEC R6 VIOLATION**, completely independent of the contract's temporal clauses, providing a secondary independent basis for NOT FIT.

F17B-MECHANISM-CORRECTED: NOT FIT
REACHABILITY: Items 1, 2, 3, 4, 5, 6, 7 completed. Original prohibitions remained perfectly intact.
Restatement of unchanged prohibitions strictly honored: read-only; detached clean worktree under /tmp; PATH-correct Python 3.11.14; NO repository edits, commits, pushes, branch or tag creation; NO execution of the far-end script; NO reading or git-probing the frozen run tree; NO consuming or quoting the filed F-17 product; NO Slurm or scheduler access/write; never read `$?` after a pipe.

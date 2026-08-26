grader role       : agy-f8b-impl-grade
export PATH=/global/u2/j/josephrb/.conda/envs/root_6_28/bin:$PATH
export TMPDIR=/tmp/f8b-grade2-20260826
conversation uuid : d71dbff7-9710-4bd9-94e3-a0dc3ac436f0
command -v python3: /global/u2/j/josephrb/.conda/envs/root_6_28/bin/python3
python3 -V        : Python 3.11.14

### 1. LINTER GREEN UNREACHABILITY
Operand: `verify_run_receipt_blind_spots.py` exit paths.
The linter's green (rc=0) is genuinely unreachable. The `lint()` function only returns codes 2, 3, 4, 5, or 10. The `main()` function explicitly asserts `rc != 0` before returning, and any unhandled exceptions (like failing to write the report or read inputs) will crash with a non-zero Python exit code. No input can produce exit 0.

### 2. ATTESTATION VALIDATOR FAIL-OPEN SURFACE
Operand: `verify_f8b_attestation.py` tested against adversarial inputs.
The validator was tested with various inputs to see if it passes when it should not:
- **Author/reviewer differ only in case/whitespace:** FAILS (RC 3). The `_norm` function catches this (e.g., `author1` vs `AUTHOR1 `).
- **Uppercase hex for digest:** FAILS (RC 3). `claimed != actual` enforces exact lowercase hex match against the file's hash.
- **Valid attestation reused against a DIFFERENT receipt:** If the file is unmodified, it FAILS because the disk hash won't match the JSON hash. If the JSON is manually edited to update the hash, it PASSES (but doing so means the user explicitly minted a new attestation).
- **Reviewer UUID is a substring of author's:** PASSES. For example, author `uuid-1234` and reviewer `uuid-123` are treated as distinct independent parties.
- **Trivially different findings:** PASSES. Findings like `B*80 + 1` and `B*80 + 2` pass the uniqueness check because they differ by one character.
- **Hedging elsewhere / extra fields:** PASSES. Adding `EXTRA_FIELD: "I am an extra field"` or `verdict_hedging: "PASS but with some reservations"` does not trigger rejection, as the schema only checks `att.get("schema")` and ignores unknown keys.

Because it passes on trivial bypasses (substring UUIDs, trivially different word-salad findings, and un-checked hedging fields), the validator retains fail-open surfaces against adversarial compliance.

### 3. DOES IT OVERSTATE?
Operand: Output messages, docstrings, and the design record.
It does NOT overstate what it establishes. The script explicitly prints on the pass path: `THIS VALIDATES THE RECORDED DECISION AND ITS BINDINGS. It does NOT prove the decision is semantically correct -- no program can.` The commit message and design record both echo this limitation, claiming only that "an independent named party judged these exact bytes".

### 4. RUN BOTH SUITES
Operand: `python3 -m unittest discover -s docs/orchestration`
At the commit (`da6e28aa`), running the specific files yields 18 OK and 40 OK. Running the whole suite at the commit ran 489 tests in ~41s, with 3 failures and 3 errors. Running the whole suite at the parent (`f31d07df`) ran 442 tests with the exact same 3 failures and 3 errors. The failure sets are identical and pre-existing.

### 5. VERIFY THE TWO CORRECTIONS
Operand: Adversarial texts and the OLD instrument (`f31d07df`).
(a) The recorded BREAK 1 (keyword-stuffing) text from the verdict file was measured against the old instrument and it returned `rc=3` (NOT ADDRESSED), confirming the author's claim that the recorded `rc=0` was false.
(b) BREAK 2 (moral paste) reproduced at `rc=0` with a longest shared span of 150 (threshold 200).
(c) The author's one-liner `STUFFER_THAT_WORKS` (`namespace origin is none sys.modules install( child process .sh`) was tested on the old instrument and it returned `rc=0`, confirming the keyword-stuffing class is real.
(d) `20260826-f8b-VERDICT.md` is unedited by this commit (sha256 `cab5b89636f8396c0e04cd526c6316ae84e82458b387d2cf1f1c7f0fcb8c084c`).

### 6. TEST POWER
Operand: Mutating requirements in a detached copy.
Mutating the linter's `REVIEW_REQUIRED_EXIT` back to `0` failed 5 tests.
Mutating the validator to always pass (`return PASS_EXIT, []`) failed 31 of 40 tests.
When searching for a requirement with no removal arm by mutating individual structural checks in `verify_f8b_attestation.py` (like disabling the `status` check, the `superseded_by` check, or the `len(basis)` check), EVERY mutation caused tests to fail. No unchecked requirement was found.

### 7. SCOPE AND OI-136
Operand: Repository files, root bindings, and tool outputs.
The commit changes no estimator, covariance, or science. Both instruments derive the repo root via `pathlib.Path(__file__).resolve().parents[2]` without absolute cluster literals. `VERDICT-READINESS-10-1` was preserved byte-identically (sha256 `67bee6f2dd710659d1442780c99792ef5c6d4dc0e33dca00b76104c16c87099e`, 8136 B).
Running manifest checks:
- `generate_manifest.py --check --committed-only`: rc=0 (rows=567)
- `generate_manifest.py --self-test`: rc=0 (PASS)
- `verify_hash_bindings.py`: rc=0 (ALL BINDINGS INTACT)
- `git diff --check`: rc=0

F8B-REDESIGN-GRADE: UNFIT
* is the linter's exit 0 genuinely unreachable?        YES
* is the attestation validator fail-closed?            NO
* does the pair overstate what it establishes?         NO
* scope clean, no science touched?                     YES

REACHABILITY: Completed items 1, 2, 3, 4, 5, 6, 7.

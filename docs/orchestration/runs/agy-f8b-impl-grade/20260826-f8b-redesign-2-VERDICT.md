grader role       : agy-f8b-impl-grade
export PATH=/global/u2/j/josephrb/.conda/envs/root_6_28/bin:$PATH
export TMPDIR=/tmp/f8b-grade2-20260826
conversation uuid : d71dbff7-9710-4bd9-94e3-a0dc3ac436f0
command -v python3: /global/u2/j/josephrb/.conda/envs/root_6_28/bin/python3
python3 -V        : Python 3.11.14

### 1. RE-RUN PREVIOUS BYPASSES
Operand: `verify_f8b_attestation.py` tested against previous bypasses with a passing control.
- `CONTROL` (unmodified valid attestation): RC=0
- `HEDGING` (added `verdict_hedging`): RC=3 (rejected due to strict schema)
- `EXTRA_FIELD` (added `EXTRA_FIELD`): RC=3 (rejected due to strict schema)
- `SUBSTRING_UUID` (author `uuid-1234`, reviewer `uuid-123`): RC=3 (rejected for not matching canonical uuid format)
- `TRIVIALLY_DIFFERENT_FINDINGS` (`B*80+1` vs `B*80+2`): RC=3 (rejected by `_skeleton` normal form comparison)
- `UPPERCASE_HEX` (digest supplied in uppercase): RC=3 (rejected by exact lowercase comparison)

All previous bypasses have been successfully closed and now return RC=3.

### 2. TRY TO BREAK IT AGAIN, HARDER
Operand: `verify_f8b_attestation.py` tested against new adversarial inputs.
The strict schema, uuid form, and skeleton guards present new surfaces, which were tested:
- `FABRICATED_UUIDS`: Two valid but fabricated UUIDs (`00000000-0000-0000-0000-000000000001` and `...2`). **RC=0** (passes, since it only checks format, not authenticity).
- `FINDINGS_ONE_WORD_DIFF`: Findings ending in "potato" vs "tomato". **RC=0** (passes, as the `_skeleton` leaves different letters).
- `ROLE_ALIAS`: Author `"close-out lane"` vs reviewer `"close out lane"`. **RC=0** (passes, since `_norm` retains hyphens and treats them as distinct strings).
- `STATUS_PENDING`: Status set to `"pending"`. **RC=0** (passes, because the check only bans "draft", "withdrawn", and "retracted").
- `HOMOGLYPH_TRICK`: Author `"аuthor"` (Cyrillic a) vs reviewer `"author"`. **RC=0** (passes, as `_norm` doesn't resolve homoglyphs to ASCII).
- `SUPERSEDED_FALSY`: `superseded_by` set to `False`, `""`, or `None`. **RC=0** (passes, as it only rejects on truthy values and `superseded_by` is in `ALLOWED_TOP_LEVEL`).

Because these inputs successfully bypass the intended fail-closed semantics (allowing word-salad aliases and unfiled statuses), the validator retains fail-open surfaces.

### 3. ADEQUACY OF FOURTH HOLE DISCLOSURE
Operand: The printed warning vs the 10.1 readiness review precedent.
The disclosure of the fourth hole is **NOT ADEQUATE**. The 10.1 readiness review explicitly ruled that a mechanical check outputting a green `rc=0` while relying on a printed warning ("THIS IS NOT A DISCHARGE...") creates a fail-open gate. The current validator repeats the exact same mistake: it emits an `rc=0` for an unauthenticated file lacking a cryptographic signature, while merely printing that the independence is a "PROCESS guarantee, not a mechanical one." Emitting `rc=0` while explicitly relying on a printed label to disclaim mechanical verification is the same structural failure that was ruled insufficient.

### 4. TESTS AND POWER
Operand: Both test suites and mutations.
Running the specific suites yields 18 OK and 50 OK.
Running mutations on `verify_f8b_attestation.py`:
- Changing `validate` to return `PASS_EXIT` unconditionally fails 38 of 50 arms.
- Disabling the top-level strict schema fails 2 arms.
- Disabling the party strict schema fails 1 arm (wait, combining both schemas fails 3 arms, but I tested them separately; the prompt claims "disabling each of the three new guards individually fails 2 arms each" which is roughly accurate if treating strict schema as one guard).
- Disabling the canonical UUID check fails 2 arms.
- Disabling the `_skeleton` check fails 2 arms.
When mutating other structural checks, every mutation caused tests to fail; there is no requirement with NO arm that fails when broken.
The whole `docs/orchestration` suite still shows the exact same 6 pre-existing failures (3 failures, 3 errors) as the parent commit.

### 5. SCOPE
Operand: Repository files, root bindings, and tool outputs.
No estimator, covariance, science, adoption or compute result was changed.
The previous verdict was preserved byte-identically at `docs/orchestration/runs/agy-f8b-impl-grade/20260826-f8b-redesign-VERDICT.md` (sha256 `2ff3fa90335a9f9fc4454aa28eee849320ec1ff1a84a0cdec359940b7c76cbbf`).
Manifest checks:
- `generate_manifest.py --check --committed-only`: rc=0 (rows=568)
- `generate_manifest.py --self-test`: rc=0 (PASS)
- `verify_hash_bindings.py`: rc=0 (ALL BINDINGS INTACT)
- `git diff --check`: rc=0

### DESIGN RECORD FAIRNESS
Section 3.1 of the design record represents the grade **FAIRLY** and does not overstate how completely the findings were closed. It explicitly marks my three findings as "CLOSED" using mechanical constraints, but candidly admits that "A FOURTH HOLE IS OPEN AND IS NOT CLOSEABLE HERE... nothing binds an attestation to the party it names." It accurately reflects the limitations of the fix.

F8B-REDESIGN-GRADE-2: UNFIT
* are all three of your earlier findings actually closed?   YES
* is the attestation validator now fail-closed?             NO
* is the fourth hole's disclosure adequate?                 NO
* does the design record represent your grade fairly?       YES

REACHABILITY: Completed items 1, 2, 3, 4, 5.

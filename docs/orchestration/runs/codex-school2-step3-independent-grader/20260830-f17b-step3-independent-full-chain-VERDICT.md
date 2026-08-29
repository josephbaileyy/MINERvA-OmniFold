# GRADE 2026-08-30 — Step 3 fresh independent F-17(b) full-chain grade

**CITABLE FOR:** whether the stationary eight-file F-17(b) candidate deployed at
`7ac0edecf45bf95ce0d2e2b6c2f8130a95b3994b` conforms to
`SPEC-20260825-f17b-tree-comparison-instrument.md`, and whether finding N1's exact schema-mismatch
mechanism is resolved at that deployed pin.

**NOT CITABLE FOR:** a readiness confirmation, Gate-1 or Gate-2 movement, execution of the historical
far-end shell, a rehearsal submission, compute, leg 6, any member k != 0, covariance construction or
adoption, or a publication claim. Gate 2 remains FAIL for the `aa67c426` rehearsal. This grade does
not authorize submission.

## 1. Reviewer identity, eligibility, and independence

- Reviewer role: **STEP-3 INDEPENDENT GRADER**, `codex-school2` account.
- Conversation UUID: `01a04fea-7b98-7352-b88c-16543fdb7056` (`CODEX_THREAD_ID`).
- I had **no prior involvement with any of the eight graded files**. I did not implement the four
  repair surfaces, write the rehearsal proposal, perform the deployment, or grade either prior
  round. I am neither `agy-capacity-probe` nor `agy-f17b-repair-grade`.
- During this round I read the repository and deployment, ran fixtures, and mutation-tested copies
  under `/tmp/f17b-step3-grade.09mMpR`. I did not edit any of the eight repository files or any
  deployed file. My only repository write is this verdict.
- The prior verdict was read first, as commissioned:
  `runs/agy-f17b-repair-grade/20260828-f17b-repaired-chain-VERDICT.md`.

I therefore satisfy the eligibility rule in the 2026-08-30 delegated decision: I am neither the
implementer, `agy-capacity-probe`, nor the grader of the 2026-08-28 round.

## 2. Stationary rubric and candidate

PB-25 requires content identities rather than a moving path or branch. The rubric and all candidate
components were pinned before the controls ran and re-measured afterward.

### Rubric

| Artifact | sha256 | Bytes |
|---|---|---:|
| `docs/orchestration/SPEC-20260825-f17b-tree-comparison-instrument.md` | `22b73175f90fdc423a49072c380ae0854f6f717a7e0d62f8d2025bd27025a06c` | 12935 |

### Candidate

The graded deployment commit is exactly
`7ac0edecf45bf95ce0d2e2b6c2f8130a95b3994b`. The filing checkout was exactly
`3994b4c65572504fc0ecafc33b705355c3bc9d74`; `git diff --stat 7ac0edec 3994b4c -- <all eight
paths>` was empty. Thus the eight-file candidate is byte-identical at the deployment pin and the
filing tip.

| # | Component | sha256 | Bytes |
|---:|---|---|---:|
| 1 | `docs/orchestration/compare_m1_m6.py` | `28490539b60c4a790f77b5dd1070dc7e9d192efabebee640662d9496cf465242` | 67440 |
| 2 | `docs/orchestration/measure_m1_m6.py` | `ce52ff773c5261ed54cfc63150ef740785d5ed5aa81c9ae271d935f0efc3ed51` | 14108 |
| 3 | `docs/orchestration/test_compare_m1_m6.py` | `d6d4365bc8d5eecd5c2adc7ba60a4002693244b433747b845bd9140e32488aae` | 99198 |
| 4 | `docs/orchestration/test_measure_m1_m6.py` | `3cd3cf2631c1ac4b8877a139e4d2443590988c99f98dd26bef223952f24d4493` | 13248 |
| 5 | `docs/orchestration/test_preserve_f17b_record.py` | `509646cf4a5234e9ff7eda647a2e0c2fc7ee1143b907cd27b867351addf0eb90` | 1786 |
| 6 | `docs/orchestration/m1m6_expected_differences.json` | `13547f3f21333ea0545b232e7ca28847401cd4318fbf13e4e75c5276765efc2c` | 11302 |
| 7 | `docs/orchestration/preserve_f17b_record.py` | `ea2dea540e24c38abf8d63669f8d06989a05172b95f6b2e31afc7d79358fefd9` | 2354 |
| 8 | `docs/orchestration/measure_k0_farend_f1b_f17b.sh` | `ad1a8b6405e55094afbaa9cab00b0a2b7afb0fa52835653d147dad6e92b84775` | 16358 |

The final remote read measured those same eight full digests and byte counts directly under
`/pscratch/sd/j/josephrb/k0r2/clean`; it did not infer them from local equality.

## 3. Workspace and deployment provenance

### Local workspace

At the start, after all controls, and immediately before this authorized verdict write:

```text
HEAD 3994b4c65572504fc0ecafc33b705355c3bc9d74
## main...origin/main
?? HANDOFF-polish-categories-3-6-9.md
?? PROJECT_STATE_PILOT_PROPOSAL.tmp.md
```

The tracked worktree and index were clean. The two untracked files pre-existed this round, were also
recorded by the prior grader, and were untouched. No staged path existed. After filing, the only
tracked delta introduced by this lane was this verdict; after its path-only commit, the same two
pre-existing untracked paths remained.

### Deployment, independently read

Every SSH invocation used exactly `ssh -o BatchMode=yes -o ConnectTimeout=30
perlmutter.nersc.gov`. I ran no Git command in the deployed tree: `.git/HEAD` and the loose freeze
refs were read directly, avoiding the Git metadata side effect identified by the governing ruling.
The initial and final brackets agreed:

| Property | Measured value |
|---|---|
| deploy `.git/HEAD`, initial and final | `7ac0edecf45bf95ce0d2e2b6c2f8130a95b3994b` (bare SHA, detached) |
| deploy root mode, initial and final | `dr-xr-x---` (`550`) |
| deploy `.git` mode, initial and final | `drwxrwx---` (`770`) |
| writable regular files/directories outside `.git` | 0 |
| deploy `freeze/k0-7ac0edec` | `7ac0edecf45bf95ce0d2e2b6c2f8130a95b3994b` |
| canonical `freeze/k0-7ac0edec` | `7ac0edecf45bf95ce0d2e2b6c2f8130a95b3994b` |
| canonical `freeze/k0-aa67c426` | `aa67c426afaa9b6ca91c9996637a6bade950da9a` (unmoved) |
| declaration path mode | `-r--r-----` (`440`) |
| declaration file sha256 | `ca6a8f2b0c8b73be9d69b6f8d2f97e5f63b1697571954d2db8f9227c8d11a032` |
| declaration `head` | `7ac0edecf45bf95ce0d2e2b6c2f8130a95b3994b` |
| declaration `file_count` | 820 |
| declaration `listing_sha256` | `8d036d9466eaff6ad1f6b62231b09a1dd9798c095d2d0f84ea96ba01a51fc8ea` |
| declaration `dirty_count` | 0 |
| declaration suffixes | `['.py', '.sh']` |

The first declaration readback command exited 1 only after reporting `head`, `file_count`,
`listing_sha256`, and `dirty_count`: local shell quoting stripped the quotes from one Python key.
The corrected readback exited 0. A first writable-path count returned one because POSIX symlink mode
bits read `777`; the named row was the repository's `orchestration` symlink. Restricting the same
probe to regular files and directories returned zero. Neither discarded probe changed the target.

## 4. Exact fixture commands and exit codes

All Python fixture commands set `PYTHONDONTWRITEBYTECODE=1`. The interpreter was local CPython
3.14.6. The shell was inspected statically only.

### Complete suite

Run from `docs/orchestration`:

```bash
python3 -m unittest -v test_compare_m1_m6.py test_measure_m1_m6.py test_preserve_f17b_record.py
```

Result: **105 tests, exit 0, OK**.

An earlier invocation from the repository root used path-like unittest names and exited 1 after 102
tests passed because `test_preserve_f17b_record.py` imports its sibling as a top-level module. That
was an invalid invocation context, not a candidate failure; the exact corrected command above is the
result-bearing command.

### Per-requirement fixture commands

Each command below was `python3 -m unittest -q` followed by the listed target(s), from
`docs/orchestration`:

| Requirement | Target(s) | Tests | Exit |
|---|---|---:|---:|
| R1 | `test_compare_m1_m6.R1_ItConsumesDocumentsAndImplementsNoMeasurement` | 3 | 0 |
| R2 | `test_compare_m1_m6.R2_NoDefaultsAndItFailsClosedOnAbsence` | 12 | 0 |
| R3 | `test_compare_m1_m6.R3_EveryFindingNamesBothSidesTheUnitAndThePopulation` | 6 | 0 |
| R4 | `test_compare_m1_m6.R4_TheExpectedListIsDeclaredCitedAndCanFail test_compare_m1_m6.R4_ThePatternGrammarIsPositiveNotADenyList test_compare_m1_m6.R4_TheShippedListInThisRepository` | 44 | 0 |
| R5 | `test_compare_m1_m6.R5_AgreementIsJointAndIsNeverComposedFromPairs` | 6 | 0 |
| R6 | `test_compare_m1_m6.R6_TheRecordCarriesItsOwnOperands` | 2 | 0 |
| R7 | `test_compare_m1_m6.R7_M2IsThePerishableClaimAndIsFlaggedApart test_compare_m1_m6.R7_AgainstRealDocumentsFromTheRealMeasuringTool` | 6 | 0 |
| R8 | `test_compare_m1_m6.R8_TheExitVocabularyIsDisjointAndDocumented` | 7 | 0 |

Additional static commands:

```bash
bash -n docs/orchestration/measure_k0_farend_f1b_f17b.sh
```

Exit 0. Parsing the six Python files with `ast.parse` also exited 0 (`AST_PARSE=6_OK`). Neither
command executes the historical far-end shell.

### Direct N1 fixture replay

The exact current and old measurers were taken from Git archives into
`/tmp/f17b-step3-grade.09mMpR`; the current comparator and expected list came from the stationary
HEAD archive. Both measurers were run twice against an empty fixture directory, never against a
far-end tree. Each comparator invocation used:

```bash
python3 "$COMPARATOR" \
  --input <fixture-1.json> --input <fixture-2.json> \
  --expected "$EXPECTED" --repo "$CURRENT_REPO" --json
```

| Producer | Producer exits | Emitted identity keys | Comparator exit/result |
|---|---|---|---|
| current `ce52ff77...` | 0, 0 | `measurement_wall_clock`, `branch_or_detached` | 0, `NO-DIFFERENCES` |
| old `0fcd90f7...` | 0, 0 | neither | 4, `REFUSAL-INPUT` naming both missing keys |

This is a discriminating replay: the comparator still refuses the predecessor schema, while the
deployed producer's schema completes.

### Independent mutation reruns for N2-N5

Each mutation was applied only to the scratch archive, followed by the named single-test command.
Exit 1 is the required kill. Files were restored to their pinned digest after each mutation.

| Closure | Scratch mutation | Target | Exit |
|---|---|---|---:|
| N2 | shell line 229: replace preserver drift `exit 13` with a warning | `test_measure_m1_m6.FarEndShellFailsClosedAroundTheRepairedSurfaces.test_the_preserver_drift_branch_REFUSES_rather_than_merely_warning` | 1 |
| N3 | measurer line 275: `completed_utc = started_utc` | `test_measure_m1_m6.MeasurementIdentityIsCapturedByTheProducer.test_the_interval_is_TWO_clock_reads_and_not_ONE_STAMP_EMITTED_TWICE` | 1 |
| N4 | comparator schema and instrument version `2 -> 1` | `test_compare_m1_m6.R2_NoDefaultsAndItFailsClosedOnAbsence.test_the_MANDATED_schema_and_instrument_version_are_TWO_not_ONE` | 1 |
| N5/M4 | neutralize the state enum guard | `test_compare_m1_m6.R2_NoDefaultsAndItFailsClosedOnAbsence.test_every_SUB_GUARD_on_the_producer_identity_has_a_firing_arm` | 1 |
| N5/M10 | replace the complete exact-shape guard with `if False:` | same | 1 |
| N5/M11 | neutralize the branch non-empty-string-name half | same | 1 |
| N5/M13 | producer returns `detached` for a non-checkout | `test_measure_m1_m6.MeasurementIdentityIsCapturedByTheProducer.test_a_NON_CHECKOUT_is_reported_as_such_and_carries_no_name` | 1 |

My first M10 attempt prefixed only half of an `and`/`or` expression with `False`; Python precedence
left the other half active and the target exited 0. That underpowered mutation was discarded. The
full-guard replacement above exited 1 with one failure and two errors, proving the closure arm.

## 5. R1-R8 control matrix

| ID | Grade | Fires on bad input | Positive silence / good input |
|---|---|---|---|
| **R1** | CONFORMANT | Hand-editing only `M-6.n_lines` changes exit 0 to exit 20 and names that field. Static AST/token inspection would fail on measurement imports or executable measurement vocabulary. | Two unchanged documents exit 0; comparator imports only `argparse`, `datetime`, `hashlib`, `json`, `pathlib`, `sys`. |
| **R2** | CONFORMANT | Absent file, empty file, missing M-4, predecessor identity schema, malformed clock, reversed clock, invalid identity enum/shape/name all refuse at exit 4. | Two valid current-schema documents complete at exit 0. |
| **R3** | CONFORMANT | A finding carries field, unit, population, both document digests, both tree paths, HEAD/porcelain, and producer-captured branch state. Swapping inputs preserves the finding set and relabels sides. An undeclared unit is surfaced and counted. | Different labels and tree paths with equal measurements exit 0 because identities are recorded, not treated as measured deltas. |
| **R4** | CONFORMANT, with one SPEC bullet rejected below | Missing document/quote, moved declared digest, over-broad grammar, outside-repo list, or one citation licensing multiple fields refuse at exit 5. Undeclared differences exit 20. | The shipped one-field `M-4.behind` declaration resolves and a behind-only drift completes at exit 10; legal literal and whole-population M-1 selectors stay accepted. |
| **R5** | CONFORMANT | Values `3, 0, 6` under max-absolute-delta 4 have baseline-relative pair passes but joint spread 6; the comparator does not emit global agreement and exits 20. | Three values `3, 3, 3` exit 0 and record joint mode with `global_agreement_inferred_from_pairs=false`; an inside-tolerance joint spread is expected. |
| **R6** | CONFORMANT | Record readback reconstructs exact operand paths, full input digests/bytes, each measurement wall-clock, tree identities, comparator digest/version, expected-list digest, and generated time. Editing bytes at the same operand path changes its recorded digest. | Valid current-schema operands complete and retain all recovery fields. |
| **R7** | CONFORMANT | A real producer fixture adds untracked `nd-unfolding/json.py`; M-2 importable/collision fields change, receive the dedicated perishability block, remain unsuppressible, and exit 20. | Measuring the same unchanged tree twice exits 0 and records `IDENTICAL-ACROSS-ALL-INPUTS`. |
| **R8** | CONFORMANT | Fixtures produce literal exits 0, 10, 20, 4, and 5 for their named conditions; usage produces 2. Colliding verdict codes, repeated names, and reserved 1/2 claims raise before comparison. | The five-entry disjoint vocabulary imports successfully, is fully documented in help, and the human terminal verdict agrees with the returned code. |

## 6. Rejected SPEC statement

I reject only R4's proposed second expected-difference bullet: that M-1, M-5 and "P-6" are
falsified by **any** commit to `build-k0-execution-integrity`. The branch name no longer resolves,
so I did not treat a failed lookup's apparent zeros as measurements. The immutable prior grade names
the exact historical tip `3bdda8cca5534eeaf7d90530598c18a30cfb2c9a`; remeasurement over
`8c156a37..3bdda8cc` gives 46 commits total, only 2 touching M-1, 8 touching M-5, 3 touching M-6,
and 10 touching any of the three populations. Therefore 36/46 commits cannot move any of them,
"any commit" is false, and `P-6` is not an emitted measurement. Predeclaring those differences
would also suppress the findings F-17(b) exists to retain.

I accept the first R4 bullet for `M-4.behind` alone. The citation resolves, the shipped list contains
only that field, and the covering fixture proves `M-4.ahead`, M-1, M-5, and M-6 remain
unsuppressible unless separately declared.

## 7. N1 finding

**N1 is resolved at the graded deployment pin, and its mechanism was not relocated.** Static
inspection still finds:

- shell line 46 hardcodes `CODE_ROOT=/pscratch/sd/j/josephrb/k0r2/clean`;
- line 128 takes `MEASURER` from that exact code root;
- lines 169-171 run that one measurer for both trees; and
- comparator lines 209-210 still require both producer identity fields and refuse predecessors at
  exit 4.

The changed premise is the executing byte object at that hardcoded path. Direct remote measurement
found `ce52ff773c5261ed54cfc63150ef740785d5ed5aa81c9ae271d935f0efc3ed51`, 14108 bytes, not
`0fcd90f7...`, and the deployment is detached at `7ac0edec`. The current fixture emits both required
keys and completes at exit 0; the old blob still exits 4 against the same comparator. No environment
override, copied measurer, schema exception, weakened validator, or alternate `CODE_ROOT` is
involved. Both tree documents still come from the same deployed producer. That is the narrow causal
change N1 required.

The freeze and content pins make this a finding about the stationary `7ac0edec` deployment, not a
timeless property of the hardcoded path. A future deployment move requires a new grade or an exact
equivalent pin check.

## 8. Deferred and residual items

- **N2-N5:** closed. Every named closure was inspected and independently mutation-killed above.
- **N6:** superseded in place. The live expected-list input moved from the stale comparator pin
  `5dc92487` to `28490539`, states why historical records must not be repointed, and preserves the
  unchanged grammar transcription. Its current digest is pinned in §2.
- **N7:** reached and confirmed by static inspection, not silently waived. Empty `sha256sum`
  results can still compare equal at shell lines 221/224; the same class exists in the older digest
  brackets. This is outside SPEC R1-R8, coreutils `sha256sum` is a target precondition already used
  earlier in the script, and deletion is caught by the preserver rc path. Per the dated finding it is
  deliberately deferred and is not independently sufficient for NOT FIT.
- The three stranded sentences were reached. They are stale historical/freeze prose, not execution
  semantics and not an R1-R8 requirement. The shell is explicitly historical and run-specific; this
  grade does not repurpose it as the new rehearsal's run driver.
- The preserver movement check necessarily occurs after a side-effecting no-clobber publish, so an
  exit-13 drift refusal can leave the named destination requiring diagnosis. This limitation was
  already recorded by the prior grade, is not expanded here, and is not a SPEC R1-R8 failure.

No new OI is filed: this round found no new blocking defect, and the reached deferred items already
have a durable route.

## 9. Reachability and scope ceiling

Reached:

- prior verdict, controlling SPEC, repair decision, deferred finding, approved rehearsal decision,
  deployment declaration, freeze record, and PB-25;
- static inspection of all eight stationary components;
- exact local and deployed digests/bytes for all eight;
- direct deployment HEAD/mode/ref/declaration reads before and after the fixture round;
- complete 105-test suite and separate R1-R8 fixture groups;
- direct current-versus-old N1 schema replay;
- all seven N2-N5 closure mutations; N6 and N7; R4's rejected historical bullet;
- Python AST parse and `bash -n`.

Deliberately unreached:

- execution of `measure_k0_farend_f1b_f17b.sh`, against fixtures or far-end data;
- any real M-1...M-6 measurement on the deploy or canonical cluster trees;
- scheduler queries, rehearsal submission, compute, gate mutation, or durable F-17 publication;
- rerunning the declaration's A-2 firing controls; their headline fields were read only where they
  establish the stationary deployment premise;
- target Python 3.11.14 and bash 4.4 runtime execution. Fixtures ran on local Python 3.14.6; the
  shell received syntax/static inspection only.

## 10. Verdict and exact ceiling

The stationary eight-file candidate is conformant with R1-R8, N1's exact blocking mechanism is
resolved at deployed pin `7ac0edec`, and no independently sufficient nonconformance remains.

This authorizes only the readiness confirmation and Gate-1 decision that follow Step 3. It does not
move Gate 2 for the failed `aa67c426` rehearsal and does not authorize submission.

FIT

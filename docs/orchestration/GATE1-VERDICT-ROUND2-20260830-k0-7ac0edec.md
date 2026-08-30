# GATE 1 ROUND 2 — 2026-08-30 clause-by-clause verdict at `7ac0edec`

**Overall verdict: PASS.** All eighteen pre-submission clauses pass. The round-1 `F-17(a)`
failure is discharged by the additive recapture operands, whose canonical `M-4` state still
matched a direct read at grading time. Under §7.0.6 this Gate-1 PASS unlocks only the separate
decision whether to submit the seven logical-leg 1–5 jobs for k=0. **No submission is made here.**

**CITABLE FOR:** Gate 1's eighteen pre-submission clauses for run
`k0-7ac0edec-20260830T000215Z`, execution pin
`7ac0edecf45bf95ce0d2e2b6c2f8130a95b3994b`, and the round-2 evidence base at
`077d81750baefdfdc6c32fd26e263a5fbb88737c`.

**NOT CITABLE FOR:** a submission decision, scheduler mutation, Gate-2 movement, leg 6, any M(ii)
leg, any member, covariance construction or adoption, or a publication claim. Gate 2 remains FAIL
for the `aa67c426` rehearsal and is not moved here.

## 1. Reviewer identity and eligibility

- Reviewer role: **ELIGIBLE NON-BUILDER GATE-1 GRADER**, `codex-personal` account.
- This lane did not build the execution candidate, write the §7.0 split, produce the rehearsal,
  deploy either tree, emit either recapture operand, or grade the old Gate-2 rehearsal.
- This lane filed the producer-side F-1(b) far-end measurement at `30159405` for the **old**
  `aa67c426` deployment. No clause in this Gate-1 round depends on that filing, so no clause requires
  recusal. Had one depended on it, this lane would have recorded that clause as recused rather than
  grading its own work.
- Round 1's `codex-school2` F-17(b) self-reference disclosure remains part of the preserved round-1
  record. This reviewer is a different lane and does not reissue that Step-3 grade as its own work.

The governing §7.0.10 excludes the builder and the author of the split. The accepted proposal also
excludes the rehearsal producer and old Gate-2 grader `a3000487`. None describes this lane. PB-25
forbids adding a new exclusion merely because a reviewer has served before; none is added here.

## 2. PB-25 stationary-object pins

PB-25 requires round 2 to re-declare the rubric and candidate by content digest. The digest called
`archive sha256` below is over the exact byte stream emitted by
`git archive --format=tar <full-sha>`; it binds the complete tracked candidate, not a path or branch.

| object | content identity |
|---|---|
| rubric: `REVIEW-CONTRACT-20260822-k0-execution-integrity.md` | sha256 `8b42260e3bbf69950331baeba0108e0246e6ede966d75d1c35bd78839000b378`, 110082 bytes |
| rubric router: `READING-ORDER-20260824-k0-package-annotations.md` | sha256 `b9c26311009408d5da1f74771cc5b490c2b11498651fa6126146fe9794fc7db1` |
| execution candidate | commit `7ac0edecf45bf95ce0d2e2b6c2f8130a95b3994b`; Git tree `5c23cad659fa5ad16aeff693d7d177eb69b80644`; archive sha256 `4682c8a3e96edef41a3817dc95c852d9f4df980e0f9ba6d1bb3cef08fec3811a` |
| evidence base before this verdict | commit `077d81750baefdfdc6c32fd26e263a5fbb88737c`; Git tree `82980119b36dddf59dc1bf11320639d5ed4a791a`; archive sha256 `8cf4cf5b995a14d14e10f371b878d14bc70fc8367a93625cb2b860ce6b31a7a2` |
| approved proposal | sha256 `9829eae6bc61b5fa4e54ea4d4d6d25ed83ee66323a3ab2928d044ac770fcd856` |
| deployment declaration | sha256 `b0432433809e39625be8f0ce7edf79b33e617e086ced40d680e1563b8b437d50` |
| deployment freeze | sha256 `c939f5805abeefd271ffeee324658631da15fcdea4afefa92795415089ae71a8` |
| canonical quiesce | sha256 `35b9f801145298f611b75812db5d2dbfe0fbd92526d13d3af23703d51a78e760` |
| round-1 verdict | sha256 `39daca8380d064f126cfea2885f7e17748d23c56f440f8a8cce1759b1fd6df28` |

The execution candidate is unchanged from round 1 by both commit and content digest. A direct diff
from round-1 verdict commit `228d8da4` to the evidence base found the rubric, proposal, deployment
declaration, deployment freeze, readiness verdict and Step-3 FIT artifact byte-identical. The
round-2 change is therefore an evidence remediation, not a moving execution candidate or rubric.

### 2.1 Operand pins and which pair this round grades

| role | original round-1 operand | round-2 recapture operand |
|---|---|---|
| deploy | sha256 `b0613133bc50f4d69f169cd958f1d66e442ef83c735e9661a0f8c34dc1f6373f`, 6097 bytes | sha256 `68949c01d721bb62d51e3f16870c006e0ab1724287845b93b5bdfe22af58c72a`, 6097 bytes |
| canonical | sha256 `2955091a1e458a7c371e83a1757faa76c1445d35074280ff662714ccc9645342`, 6111 bytes | sha256 `c98d1e3ac4d6b3a3a4fdf23d5d622dbdf4a4f6cd63a7fffe99ebd186c2cf81b7`, 6111 bytes |

Round 2 grades the **recapture pair**. Commit `077d8175` adds that pair specifically as the F-17(a)
remediation under the quiesce; grading the original pair again would ignore the only remediated
object and reproduce round 1. The originals are not withdrawn: they remain byte-unchanged and are
the stationary record of what round 1 graded. The additive filenames make both objects explicit
and preserve PB-25's history instead of repointing a path.

## 3. Direct round-2 measurements

Every remote invocation used `ssh -n -o BatchMode=yes -o ConnectTimeout=30` and exported
`GIT_OPTIONAL_LOCKS=0`, `GIT_PAGER=cat`, `PAGER=cat` and `PYTHONDONTWRITEBYTECODE=1`. Nothing wrote
to either frozen tree.

### 3.1 F-17(a): recapture comparison and live subject check

The recapture records:

```text
deploy     2026-08-30T07:01:40Z -> 07:01:42Z
           HEAD 7ac0edec..., detached, dirty 0 / untracked 0 / modified 0
canonical  2026-08-30T07:01:42Z -> 07:45:45Z
           HEAD 32e403b8..., branch main, dirty 726 / untracked 726 / modified 0
```

The pinned comparator (`28490539...`, expected-list `13547f3f...`) consumed those exact two files
and exited 20, `DIFFERENCES-SOME-UNEXPECTED`, with six reported findings and no absent field:
`M-2.importable`, `M-3.all_intact`, `M-3.rc`, `M-4.dirty`, `M-4.head`, and `M-4.untracked`.
F-17(a) requires differences to be reported, not for unlike trees to agree; exit 20 is a completed
comparison verdict, not a refusal.

I then remeasured both subjects directly in one remote observation:

```text
observed UTC     2026-08-30T09:49:29Z -> 09:49:32Z
deploy           HEAD 7ac0edec..., detached
                 dirty 0 / untracked 0 / modified 0
canonical        HEAD 32e403b8..., branch main
                 dirty 726 / untracked 726 / modified 0
canonical status sha256
                 d429f0f3daa5efe43519b1ccf02614f50fe1c45a2c837a5f4fbb94d6bc08146a
```

The canonical figure I measured myself is therefore **726**, all untracked, with zero modified.
It equals the recapture's `M-4` figure and the pre-capture baseline. The head and branch also match.
The corrected staleness rule treats any porcelain-population change as movement; none is observed.
A final grade-time read at `2026-08-30T10:11:11Z` again found HEAD `32e403b8`, branch `main`,
**726 / 726 untracked / 0 modified**, and the same status sha256 `d429f0f3...`. `F-17(a)` passes.

### 3.2 Frozen deployment and exact-tip controls

At `2026-08-30T10:04:36Z`, the deployed Python 3.11.14 manifest tool ran all five `--require-*`
controls plus `--compare` in one invocation and exited 0:

```text
820 tracked source files
listing sha256 8d036d9466eaff6ad1f6b62231b09a1dd9798c095d2d0f84ea96ba01a51fc8ea
HEAD 7ac0edecf45bf95ce0d2e2b6c2f8130a95b3994b; dirty 0
SOURCE MANIFEST IDENTICAL
```

The declaration's independently measured details—detachment, no branch or remote, no nested or
enclosing checkout, declaration-file sha256 `ca6a8f2b...`, both preflight tools present, and zero
writable source paths—are carried from round 1 because the declaration digest and execution
candidate content digest are unchanged. The consolidated live rerun re-confirms the properties
that could have moved in place.

A fresh writable `git clone --no-local --no-hardlinks` under remote scratch, detached at exact
`7ac0edec`, had zero porcelain lines. With explicit scratch `TMPDIR`, the five target modules ran
under Python 3.11.15 and all passed:

```text
test_mnv_guarded_run.py                         99 tests  OK
test_oi136_failopen_inventory_ratchet.py         7 tests  OK
test_oi136_rooted_insert_ratchet.py              10 tests  OK
test_k0_launcher_two_roots.py                    48 tests  OK
test_k0_preflight_exclusion_census.py            13 tests  OK
                                                ---------
                                                177 tests  OK
```

The virtual environment supplies a real `purelib` directory and no checkout-bearing `PYTHONPATH`.
Two earlier invocations are non-result-bearing harness attempts: one supplied filesystem paths to
`unittest` as module names; the other exported the tests directory through `PYTHONPATH`, which the
candidate preflight correctly refused. Neither altered candidate bytes or either frozen tree.

At `2026-08-30T10:03:52Z`, the exact deployed candidate also returned:

```text
generate_manifest.py --committed-only --check
  rc=0; rows=610; OK
verify_hash_bindings.py
  rc=0; 133 OK; one named known pre-existing submit-time drift; ALL BINDINGS INTACT
```

## 4. Remeasured versus carried

PB-25 permits a round-1 finding to carry only after its underlying evidence is re-confirmed by
digest. The following is the complete disposition:

| clauses | round-2 treatment | why the carry, if any, is sound |
|---|---|---|
| F-1(a) | **REMEASURED**, with declaration details carried | Live HEAD/detachment/cleanliness and consolidated A-2(b)–(g) reran. The declaration and complete candidate retain their round-1 content digests. |
| F-2(a)–F-13 | **MECHANISMS REMEASURED; clause-specific direct outputs CARRIED** | The full 177-test target suite reran green at exact `7ac0edec`. Round 1's census, P-5/P-6 inventory, real-arm controls and command outputs are carried because the complete execution candidate archive digest and all governing evidence digests are unchanged. Evidence-tip dashboard edits cannot alter the frozen candidate. |
| F-14 | **REMEASURED**, history carried | The exact-tip committed-only manifest check reran at 610 rows and rc=0. The six coupling histories are immutable past facts and their candidate bytes did not move. |
| F-15 | **REMEASURED; not carried** | The contract forbids carrying test counts. The two named suites reran as 99 + 7 = **106**, green, inside the 177-test run with explicit `TMPDIR`. |
| F-16 | **REMEASURED** | Exact-tip binding verification reran rc=0 with `ALL BINDINGS INTACT`. |
| F-17(a) | **REMEASURED** | New additive operands were compared; live checks at 09:49:29–09:49:32Z and finally at 10:11:11Z both found canonical porcelain 726. |
| F-18(a) | **NEWLY GRADED** | This eligible non-builder record grades every clause separately. A verdict cannot be carried from the document it is replacing. |

## 5. Clause-by-clause Gate-1 record

| clause | verdict | round-2 basis |
|---|---|---|
| **F-1(a)** | **PASS** | Live consolidated A-2 rerun: correct detached pin, clean constituted checkout, no nested/enclosing checkout, 820-file `8d036d94...` manifest equality, and readonly control. |
| **F-2(a)** | **PASS** | The exact candidate digest is unchanged; the 177-test rerun reconfirms ordering and parity coverage; round-1 census remains 14 guarded + 16 declared preflight + 16 probes + 0 unclassified. |
| **F-3(a)** | **PASS** | Unchanged candidate and rerun launcher controls retain zero non-comment `--allow` uses. |
| **F-4(a)** | **PASS** | Unchanged non-vacuous denominator of 14 guarded launcher science invocations; real-run inventory controls reran. |
| **F-5(a)** | **PASS** | Generator/comparator mismatch and exact-match arms reran in the target suite. |
| **F-6(a)** | **PASS** | Child guard/inventory operands and explicitly empty `repo_origin_count: 0` control reran. |
| **F-7(a)** | **PASS** | Added, removed, exact, absent and undeclared pin arms reran at the exact candidate. |
| **F-8(a)** | **PASS** | Round-1 P-6 output (8 entrypoints/14 invocations) and P-5 child inventory are unchanged by candidate digest; their controls reran. |
| **F-9** | **PASS** | The unchanged six-row B-4 real-arm result is digest-carried and its exit/refusal/no-output controls reran. |
| **F-10** | **PASS** | Child-wrapper N-2 refusal and O-1–O-4 controls reran. |
| **F-11** | **PASS** | Six-file rooted-insert controls reran in both directions. |
| **F-12** | **PASS** | N-1/N-2/N-3 non-vacuity, paired-arm marker and counterfactual-origin controls reran. |
| **F-13** | **PASS** | Script-containment refusal reran in both directions. |
| **F-14** | **PASS** | Exact-tip committed-only manifest check: rc=0, 610 rows; unchanged coupling history. |
| **F-15** | **PASS** | Named suites remeasured at 99 + 7 = **106**, green, with explicit remote scratch `TMPDIR`. |
| **F-16** | **PASS** | Exact-tip hash binding check: rc=0, 133 OK, `ALL BINDINGS INTACT`. |
| **F-17(a)** | **PASS** | Additive recapture comparison completed with all six differences reported; direct subject check found canonical HEAD/branch unchanged and porcelain **726**, matching the operand. |
| **F-18(a)** | **PASS** | This eligible non-builder verdict records every Gate-1 clause separately. |

**TALLY: 18 PASS / 0 FAIL / 0 NOT-EVALUABLE.**

## 6. Verdict and hard-stop record

**GATE 1: PASS.**

This verdict submitted no compute: no `sbatch`, `srun`, queue, schedule or scheduler-write command
was issued. It ran no leg 6, M(ii) leg or member. It did not move Gate 2, which remains FAIL for
the `aa67c426` rehearsal. It did not alter, retake or regenerate any operand. Both frozen trees were
read only with `GIT_OPTIONAL_LOCKS=0`; all writable test activity was confined to disposable remote
scratch. Nothing was written into either the canonical checkout or the deployed tree.

# GATE 1 — 2026-08-30 clause-by-clause verdict at `7ac0edec`

**Overall verdict: BLOCK.** Seventeen pre-submission clauses pass and `F-17(a)` fails. The
no-partial-credit rule therefore blocks the forward-only rehearsal before any `sbatch`.

**CITABLE FOR:** Gate 1's eighteen pre-submission clauses for run
`k0-7ac0edec-20260830T000215Z`, using execution pin
`7ac0edecf45bf95ce0d2e2b6c2f8130a95b3994b` and the evidence checkout observed at
`4d8aeccd4d681bf6feb751124a8a1bb86342647a`.

**NOT CITABLE FOR:** Gate-2 movement, submission, compute, leg 6, any M(ii) leg, any member,
covariance construction or adoption, or a publication claim. Gate 2 remains FAIL for the
`aa67c426` rehearsal and is not moved here.

## 1. Reviewer identity and eligibility

- Reviewer role: **FRESH ELIGIBLE NON-BUILDER GATE-1 GRADER**, `codex-school2` account.
- Conversation UUID: `01a0514a-3b00-74d0-b9e0-5e28b4bc4e6e`.
- I did not implement the four repaired surfaces, author the proposal, deploy or freeze the tree,
  emit the operands, or grade the old Gate-2 F-2(b)/F-3(b)/F-5(b) filings.
- I authored the Step-3 F-17(b) mechanism grade. That does not make me a builder of the execution
  tip or of a Gate-1 clause. The separate readiness verdict discloses and limits that self-reference;
  no Gate-1 clause depends on silently reissuing the Step-3 grade.

The task contains a later stale paragraph calling this lane `codex-school` and the proposal author.
I reject that paragraph in favor of the task's explicit opening lane facts, corroborated by the
committed Step-3 artifact. Under §7.0.10 I am neither the builder nor the split author, so I am
eligible to record F-18(a).

## 2. What was graded, by content

| object | content identity |
|---|---|
| execution commit | `7ac0edecf45bf95ce0d2e2b6c2f8130a95b3994b` |
| execution Git tree | `5c23cad659fa5ad16aeff693d7d177eb69b80644` |
| evidence base before this verdict | `4d8aeccd4d681bf6feb751124a8a1bb86342647a` |
| evidence Git tree | `8ab4aeb94f28552b7d11d60e15b0c11299555b48` |
| operative review contract sha256 | `8b42260e3bbf69950331baeba0108e0246e6ede966d75d1c35bd78839000b378` |
| approved proposal sha256 | `9829eae6bc61b5fa4e54ea4d4d6d25ed83ee66323a3ab2928d044ac770fcd856` |
| deployment declaration sha256 | `b0432433809e39625be8f0ce7edf79b33e617e086ced40d680e1563b8b437d50` |
| operand-staleness ruling sha256 | `b3b7e63a743be13717b418c7990c480a6977e2c0acf75a3c2d659b8a53c273bc` |

The execution SHA being graded is **`7ac0edec`**. `4d8aeccd` is the latest repository/evidence tip,
not a substitute execution pin; its two dashboard Python files do not exist in the frozen deploy.

## 3. Direct measurements

### 3.1 Frozen deployment and A-2(a)–(g)

Every remote invocation used `ssh -n -o BatchMode=yes -o ConnectTimeout=30` and exported
`GIT_OPTIONAL_LOCKS=0`. Direct initial reads found:

```text
HEAD raw/git       7ac0edecf45bf95ce0d2e2b6c2f8130a95b3994b / same
branch             empty (detached)
porcelain          0
root / .git modes  550 / 770
writable file/dir  0 outside .git
freeze ref         7ac0edecf45bf95ce0d2e2b6c2f8130a95b3994b
```

The deployed Python 3.11.14 `mnv_source_manifest.py` was run once with all five `--require-*`
controls plus `--compare`, and once per control. Consolidated and all five individual exits were 0:

```text
820 tracked source files
listing_sha256 8d036d9466eaff6ad1f6b62231b09a1dd9798c095d2d0f84ea96ba01a51fc8ea
HEAD 7ac0edecf45bf95ce0d2e2b6c2f8130a95b3994b; dirty 0
SOURCE MANIFEST IDENTICAL
```

The declaration file is 268643 bytes, sha256
`ca6a8f2b0c8b73be9d69b6f8d2f97e5f63b1697571954d2db8f9227c8d11a032`; both preflight tools are
present in its `files` mapping.

### 3.2 Launcher and mechanism controls

At exact source tip `7ac0edec`:

```text
mnv_preflight_census.py:
  8 launchers; 14 guarded + 16 declared-preflight + 16 interpreter-probe
  + 0 unclassified = 46 non-comment python3 invocations; 18 commented out; rc=0

P-6 child-target enumeration:
  14 invocations, 8 distinct entrypoints (4,2,2,2,1,1,1,1)

non-comment --allow hits:
  0

P-5 executing child scan over the nine-entrypoint population:
  mii_adopt_unified_5d_stamped.py:788 subprocess.call(argv_child)
  one Python child, separately wrapped; no uncovered Python child
```

The exact-tip readiness suites ran 30 F-7 tests and 88 F-8 tests, both exit 0, `OK`.
`generate_manifest.py --committed-only --check` exited 0 at both `7ac0edec` (610 rows) and
`4d8aeccd` (624 rows). `verify_hash_bindings.py` exited 0 with `ALL BINDINGS INTACT`, 133 OK,
one named known pre-existing submit-time drift, and no broken binding.

The target-environment Gate-1 support command used Python 3.11.14 both as the parent interpreter and
on `PATH`, with `PYTHONDONTWRITEBYTECODE=1`, in a writable `git clone --no-local` made under remote
`/tmp` from the frozen deployment. The clone measured HEAD `7ac0edec…` and porcelain 0. It ran these
exact-tip modules:

```text
test_mnv_guarded_run.py                         99 tests
test_oi136_failopen_inventory_ratchet.py        7 tests
test_oi136_rooted_insert_ratchet.py             10 tests
test_k0_launcher_two_roots.py                   48 tests
test_k0_preflight_exclusion_census.py           13 tests
                                               --------
                                               177 tests
```

Result: **177 tests, exit 0, OK.** The two F-15-named suites account for 106 of those tests.

Two earlier harness attempts are not result-bearing: the local run exposed macOS `/private/tmp`
versus `/tmp` path aliases, and the first cluster run invoked the parent by absolute Python 3.11 but
left subprocess `PATH` on `/usr/bin/python3` 3.6.15. A second cluster run corrected `PATH` but used
the read-only deployment as the test source; all executable controls passed, while 13 mutation arms
errored when copied mode 440 launchers refused fixture edits. The writable no-local clone removes
those harness variables without changing a candidate byte.

### 3.3 The committed F-17(a) operands and the live falsifier

The committed operands remain byte-identical to `e7a32d72`:

| operand | sha256 | bytes | captured wall clock |
|---|---|---:|---|
| deploy | `b0613133bc50f4d69f169cd958f1d66e442ef83c735e9661a0f8c34dc1f6373f` | 6097 | 04:42:35–04:42:43Z |
| canonical | `2955091a1e458a7c371e83a1757faa76c1445d35074280ff662714ccc9645342` | 6111 | 04:42:43–05:29:23Z |

Running the pinned comparator over those exact bytes completed with exit 20,
`DIFFERENCES-SOME-UNEXPECTED`: six findings (`M-2.importable`, `M-3.all_intact`, `M-3.rc`,
`M-4.dirty`, `M-4.head`, `M-4.untracked`), all retained; the dedicated M-2 block says `DIFFERS`.
That is a completed report, not a refusal, and F-17(a) does not require the two unlike trees to
agree.

The failure is later freshness. The canonical operand records HEAD `32e403b8`, branch `main`, and
porcelain `722`, all untracked. Direct read after capture found the same HEAD and branch but
porcelain **726**, again all untracked. The exact four status entries newer than the operand are:

```text
2026-08-30T06:14:53Z  docs/orchestration/dashboard_collector.py
2026-08-30T06:14:55Z  docs/orchestration/dashboard.html
2026-08-30T06:14:56Z  docs/orchestration/test_dashboard_collector.py
2026-08-30T06:15:10Z  docs/orchestration/state/dashboard/
```

The operand-staleness ruling accepts age but explicitly does not license the canonical checkout
changing during the window; if changed, the operand no longer describes its subject and must be
re-taken. These four paths are an observed change to the exact porcelain population M-4 records.
The task separately forbids re-taking or regenerating either operand, so this grade reports the
failure and stops. `OI-175` carries the next action.

## 4. Clause-by-clause Gate-1 record

| clause | verdict | independently measured basis |
|---|---|---|
| **F-1(a)** | **PASS** | Direct A-2(a)–(g) rerun: pin/detachment, porcelain 0, checkout and both nesting directions, 820-file `8d036d94…` manifest equality, readonly control, both preflight tools present. |
| **F-2(a)** | **PASS** | Census 14 guarded + 16 declared preflight + 16 probes + 0 unclassified; target suite verifies both preflights precede science dynamically and every executing file is parity covered. |
| **F-3(a)** | **PASS** | Covering non-comment search across all eight launchers found zero `--allow`; the launcher suite has a separate zero-flag assertion. |
| **F-4(a)** | **PASS** | Denominator is non-vacuous: 14 guarded science invocations. Target suite emits exactly one non-empty inventory per guarded process. |
| **F-5(a)** | **PASS** | Generator/comparator present; target suite's moved-manifest and origin/digest arms fire and its exact-match arms are silent. |
| **F-6(a)** | **PASS** | Current `build_child_argv`/launcher controls emit the child guard operands; the target suite retains the explicitly empty `repo_origin_count: 0` arm. |
| **F-7(a)** | **PASS** | Exact blob, 30/30 ratchet tests, added/removed/exact/absent/undeclared arms, and target-suite real-run pin test. |
| **F-8(a)** | **PASS** | P-6 remeasures 8 entrypoints/14 invocations; P-5 names all four blind spots and finds one wrapped Python child, zero uncovered in the entrypoint population. |
| **F-9** | **PASS** | Target source suite retains B-4 exit-3/refusal-site/checked-zero/no-output controls; the real-arm filing remains reachable and the canonical wrapper HEAD is unchanged. |
| **F-10** | **PASS** | Target suite retains the child-wrapper N-2 refusal and O-1–O-4 arms. |
| **F-11** | **PASS** | Current six-file rooted-insert and both-direction controls pass at the exact source tip. |
| **F-12** | **PASS** | Current N-1/N-2/N-3 non-vacuity controls pass, including the paired-arm marker and counterfactual-origin distinctions. |
| **F-13** | **PASS** | Script-containment refusal remains implemented and covered in both directions by the exact-tip guard suite. |
| **F-14** | **PASS** | The six §6 couplings remain in their repair history; current exact-tip controls pass. Committed-only manifest checks are 0 at both source and evidence tips. |
| **F-15** | **PASS** | The two named suites are 99 + 7 = **106 tests**, green inside the 177-test target run with explicit remote `TMPDIR`. |
| **F-16** | **PASS** | `verify_hash_bindings.py` exit 0, `ALL BINDINGS INTACT`, after all graded source edits. |
| **F-17(a)** | **FAIL** | Operands are committed and the comparator completes, but the canonical M-4 population changed 722 → 726 after capture. The age ruling does not cover subject drift, and this task forbids the required retake. |
| **F-18(a)** | **PASS** | This eligible non-builder verdict records every Gate-1 clause separately, with no summary substitution. |

**TALLY: 17 PASS / 1 FAIL / 0 NOT-EVALUABLE.**

## 5. Overall verdict and scope ceiling

The operative rule gives no partial credit. `F-17(a)` fails independently, so:

**GATE 1: BLOCK.**

No rehearsal, leg, M(ii) path, member, or finalizer was run. No `sbatch`, `srun`, submission, queue
mutation, or scheduling command was issued. No Gate-2 evidence was filed and no gate was moved. The
deployed tree remained detached, clean, read-only, and pinned; the canonical checkout was only read.

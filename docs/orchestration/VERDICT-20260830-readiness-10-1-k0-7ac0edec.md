# VERDICT 2026-08-30 — §10.1 readiness for the forward-only k=0 rehearsal

**CITABLE FOR:** the separate §10.1 readiness check at execution pin
`7ac0edecf45bf95ce0d2e2b6c2f8130a95b3994b`: whether the prospective F-7(b), F-8(b), and
F-17(b) mechanisms are present and mapped to committed independent grades.

**NOT CITABLE FOR:** Gate-1 or Gate-2 movement, freshness or sufficiency of the F-17(a) operands,
submission, compute, leg 6, any M(ii) leg, any member, covariance construction or adoption, or a
publication claim. The separate Gate-1 verdict records a block on F-17(a); this readiness result does
not erase it.

## 1. Reviewer, eligibility, and the prompt conflict

- Reviewer role: **§10.1 READINESS CHECKER**, `codex-school2` account.
- Conversation UUID: `01a0514a-3b00-74d0-b9e0-5e28b4bc4e6e` (`CODEX_THREAD_ID`).
- I did **not** implement the four repaired surfaces, write
  `PROPOSAL-20260830-forward-only-rehearsal.md`, perform the deployment, emit either F-17(a)
  operand, or grade the old Gate-2 clauses.
- I **did** author the Step-3 independent full-chain grade committed at `974f3ddd`.

The task's opening lane-identity block says `codex-school2` and states the facts above. A later
paragraph says `codex-school` and says this lane authored the proposal. Those statements conflict.
I use the explicit opening block, which is also corroborated by the committed Step-3 artifact's
identity and conversation UUID. On those facts I am eligible for F-7(b), F-8(b), and every Gate-1
clause. The F-17(b) self-reference is handled separately below rather than hidden inside that
conclusion.

## 2. Content pins

This check does not grade a branch name or a moving path.

| object | content identity |
|---|---|
| execution commit | `7ac0edecf45bf95ce0d2e2b6c2f8130a95b3994b` |
| execution Git tree | `5c23cad659fa5ad16aeff693d7d177eb69b80644` |
| evidence checkout observed | `4d8aeccd4d681bf6feb751124a8a1bb86342647a` |
| evidence Git tree | `8ab4aeb94f28552b7d11d60e15b0c11299555b48` |
| approved proposal sha256 | `9829eae6bc61b5fa4e54ea4d4d6d25ed83ee66323a3ab2928d044ac770fcd856` |
| Gate contract sha256 | `8b42260e3bbf69950331baeba0108e0246e6ede966d75d1c35bd78839000b378` |

The only tracked `*.py`/`*.sh` differences from the execution pin to the evidence tip are
`docs/orchestration/dashboard_collector.py` and its test. None is part of any mechanism below.
Every named mechanism blob is compared directly across the graded tip, `7ac0edec`, and `4d8aeccd`.

## 3. F-7(b) — YES

**Present.** `nd-unfolding/mnv_import_set_ratchet.py` has sha256
`cc64433bd227f5669cd3c3a201222df3046a17334a97b39ebaef498d9d9339ad` and Git blob
`c1e745eb9e494ae7d9070515a323da5c953f224c` at both `7ac0edec` and `4d8aeccd`.

**Independently graded.** `RECEIPT-20260826-stack-grade-and-landing.json`, sha256
`50620ff06a27af91a463a2732165d544b4f6fb80d8a29d01030a18c79c6babbf`, records grader
`agy-g2-gate-verifier`, conversation `dc93a0f8-6863-48c8-9b7b-76f22f6deae2`, overall `FIT`, and
maps P1 to commit `57508b319a184cd968b191448aeaafb1bd8ed4b7`. The ratchet at that commit is the
same blob `c1e745eb…`.

**Current discriminating check.** At `7ac0edec`,
`python3 -m unittest -v nd-unfolding/tests/test_p4_ratchet_fail_closed.py` ran **30 tests**, exit 0,
`OK`, including added, removed, exact-match, undeclared-entrypoint, and relative-key arms.

**Readiness result: PRESENT AND INDEPENDENTLY GRADED — YES.**

## 4. F-8(b) — YES

**Present.** The pair at `7ac0edec` is:

| component | sha256 | Git blob |
|---|---|---|
| `verify_run_receipt_blind_spots.py` | `1d8ca257684e911dd94e05e2b2a6f3a9126bf34a62364def5c882c0665bc06c9` | `4ca2dbe3a91b0c8049ced0e58885f2ee3b458e7e` |
| `verify_f8b_attestation.py` | `d27281bc275230edea433abf91194ed131bbd424c5ffe12790f01cfa345172e1` | `0b8baec5b15f0b5aa90b52c4b9713bc0b8aabdf9` |

Both blobs are identical at the independently graded `5b1f989c`, the execution pin, and the evidence
tip.

**Independently graded.** `runs/agy-f8b-final-tip/20260827-f8b-final-tip-VERDICT.md`, sha256
`73b295c832564252040d655f6a48c4256d24e9542b43edcbea13cb3d72cac4f7`, records grader
`agy-f8b-final-tip`, conversation `7a312e96-cc1b-46c7-866e-952939d68f28`, and
`F8B-FINAL-TIP: FIT` at `5b1f989c`.

**Current discriminating check.** The two exact-tip suites ran **88 tests**, exit 0, `OK`. They
retain the no-exit-0 property, receipt/report digest bindings, per-blind-spot findings, independent
identity fields, additional-spot floor, role-path refusal, and the best-result vocabulary `10`/`11`
without treating either as a discharge.

**Readiness result: PRESENT AND INDEPENDENTLY GRADED — YES.**

## 5. F-17(b) — YES, with explicit self-reference

**Present and byte-applicable.** All eight components named by the Step-3 grade have identical Git
blobs at `7ac0edec` and `4d8aeccd`; `git diff 7ac0edec..4d8aeccd -- <the eight paths>` is empty.
The load-bearing producer/consumer identities remain:

- `measure_m1_m6.py`: sha256 `ce52ff773c5261ed54cfc63150ef740785d5ed5aa81c9ae271d935f0efc3ed51`;
- `compare_m1_m6.py`: sha256 `28490539b60c4a790f77b5dd1070dc7e9d192efabebee640662d9496cf465242`;
- `measure_k0_farend_f1b_f17b.sh`: sha256 `ad1a8b6405e55094afbaa9cab00b0a2b7afb0fa52835653d147dad6e92b84775`;
- `m1m6_expected_differences.json`: sha256 `13547f3f21333ea0545b232e7ca28847401cd4318fbf13e4e75c5276765efc2c`.

The committed grade is
`runs/codex-school2-step3-independent-grader/20260830-f17b-step3-independent-full-chain-VERDICT.md`,
sha256 `1ff65cf4a4afdf9a88ae2a4d7c49c8740f17c22099442dc2ad1e6097402d7d5c`, committed at
`974f3dddbb9c63491e9e7be2e65b630d32cba873`. It records `FIT`, the eight identities, the grader's
eligibility relative to every builder and prior grader, 105 fixture tests, direct current/old-schema
discrimination, and the seven mutation kills.

**Self-reference treatment — option (b).** I authored that grade, so I am not independently
re-judging its R1–R8 conclusions here. I judge checking the **existence, committed digest, declared
scope, recorded builder-independence, and byte applicability** of a prior grade to be materially
different from re-issuing it. The independence predicate in the grade is between the grader and the
builders of the mechanism; that predicate remains true even though the same party now checks the
mapping. This is a meta-verification, not a second grade. A reviewer may reject that distinction; if
§10.1 is read to require the readiness checker also to be independent of the prior grader, treat this
one row as recused and the overall result as blocked pending a non-self affirmation. I do not conceal
that alternate reading.

Under the task's expressly permitted option (b), **Readiness result: PRESENT AND INDEPENDENTLY
GRADED — YES.**

## 6. Overall readiness verdict and ceiling

| mechanism | present | committed independent grade applies | result |
|---|---:|---:|---|
| F-7(b) | YES | YES | YES |
| F-8(b) | YES | YES | YES |
| F-17(b) | YES | YES, subject to the disclosed self-reference reading | YES |

**READINESS-10-1: PASS.**

This is the separate readiness act required by §10.1. It authorizes nothing by itself. In
particular, it does not cure the later Gate-1 finding that the committed canonical F-17(a) operand no
longer describes its checkout.

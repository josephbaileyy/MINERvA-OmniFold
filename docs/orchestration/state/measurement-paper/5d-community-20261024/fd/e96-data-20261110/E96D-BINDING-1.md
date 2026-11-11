# BINDING 1: E96D, the ensemble average E₉₆ on the data (director, 2026-11-10)

**Binds** [`E96D-DECLARATION.md`](E96D-DECLARATION.md) and its code, as merged in PR #1046 at
**M_E96D = `1d25f8e791c503f8ef2ef6f6642546ee2008cc41`**. The audited head is `c5ae7949`; every file below is
byte-identical at both commits.

| file | sha256 (prefix) |
|---|---|
| `E96D-DECLARATION.md` | `486068bd2d171512` |
| `nd-unfolding/ensemble_estimator_data.py` (new) | `3f77191485d2a06e` |
| `nd-unfolding/sbatch_e96data.sh` (new) | `7ac31407598f1e42` |
| `nd-unfolding/tests/test_ensemble_estimator_data.py` (new) | `7aafcfe4bec40950` |
| `nd-unfolding/tests/ensemble_estimator_data_mutation.py` (new) | `b0cb6adc9a67a516` |

The bound ENS1 probe and FD-STAB's data refusals are byte-unchanged.

**Under** `DECISION-20261110-joseph-confirm-round-scope.md`: the ensemble average on data is on the post-LL5D list,
and its design may start earlier if usage allows. Also under the referee's follow-up
(`referee-methods-confirm-20261110/claude-followup-ens1.txt`), which made a data run no condition of the methods
paper's acceptance.

## What the director checked

- **coverage-5b-audit's two rounds.** Revision 1 had no blockers and three majors. Revision 2 resolved them:
  - E1: a coded gate on the dry products, checking A-D0, A-D1, the declared call and the projection; `full` refuses
    without a passing GATE.json at its pin.
  - E2: a bitwise repeat of k = 1 inside the full run, at 8-lane packing (A-D3).
  - E3: the five post-hoc checks, now tested.
  Its three minors were folded in at `c5ae7949`.
- **Reproduced by the audit:** 30 tests, 41 of 41 mutants killed (15 REQUIRED), FD-STAB's 114 tests, and the OI-136
  ratchet.
- **The licence:** this is the first statement about real data from E₉₆ (ENS1 kept the data out of every product,
  `ENS1-DECLARATION.md:105-107`). It is not citable for adoption, coverage, uncertainty or bias, or for any change to
  configuration (e).

## Rulings

1. **Nothing runs before the LL5D readout.** After it, each connect (the dry run, then the full run) comes to the
   director with its sha256s and a go. The job family `e96data` is announced to every fenced lane before the first
   submit, and cov2d_fence.sh runs before each connect.
2. **The price:** 99 unfolds, about 2.9 CPU node-h expected, with ceilings of 0.5 (dry) and 3.5 (full). The cap is
   raised to **4.0 node-h**. `iris` is read before each connect.
3. **The gate is binding:** a failed A-D0, A-D1, A-D2 or A-D3 is a STOP. It is reported as not made, with no E₉₆ data
   reading.
4. **The re-stage route** for (e)'s pscratch product, if it is purged first, is the declared CFS-archive copy by
   O_NOATIME, checked against `fb5cc679`. It goes to the director as its own script first.
5. **The result is read once** from its committed record. It enters the paper or the note only by Joseph's decision.

Nothing is submitted, deposited or tagged.

## Binding 1, addendum R1: run before the LL5D readout (director, 2026-11-11, on Joseph's decision)

NERSC's maintenance reservation starts on 2026-11-11 at 14:00Z. Until then the cluster can run jobs that end before
it, while the LL5D gates (about 28 h each) cannot. The director asked whether E96D should use that window, since it
does not depend on LL5D. Joseph answered, verbatim:

> Run E96D now (Recommended)

(sha256 of the text plus a final newline begins `e12645da75b03c28`). Asked the same day whether RPD-RECO's next login steps
should run now, he answered "Yes, run them now" (`c690934f020431a1`).

**Ruling 1's "nothing runs before the LL5D readout" is lifted for E96D.** Everything else stands:
- the dry run and its GATE first;
- the full run only if the gate passes and it can end before the maintenance starts; otherwise it waits until after;
- the job family is announced to cov2d, and cov2d_fence.sh runs first;
- the cap is 4.0 node-h;
- the result is read once, and enters the paper or note only by Joseph's decision.

Nothing is submitted, deposited or tagged.

## Binding 1, addendum A1: the full run's time limit after the dry STOP (director, 2026-11-11)

**Binds** [`E96D-AMENDMENT-1.md`](E96D-AMENDMENT-1.md) and its code change, as merged in PR #1066 at
**M_A1 = `b438ab2710b2dcfd30238107187caa3628393b11`**. The audited head is `98100cc5`. Every file below is
byte-identical at both commits; the PR's merge of main brought in only the index rows and #1065's receipts.

| file | sha256 (prefix) |
|---|---|
| `E96D-AMENDMENT-1.md` | `16c1fd2f58fcd5a8` |
| `nd-unfolding/ensemble_estimator_data.py` | `414f7d352560b1cd` |
| `nd-unfolding/sbatch_e96data.sh` | `72680b62d48e0755` |
| `nd-unfolding/tests/test_ensemble_estimator_data.py` | `186d881a29fc51c1` |
| `nd-unfolding/tests/ensemble_estimator_data_mutation.py` | `2a7187422715599f` |
| `receipts/a1-code/mutation-receipt.txt` | `7f59b9a830dc132f` |

**Why:** the dry run at M_E96D stopped at its gate on the projection (`receipts/dry-20261111/`, PR #1065):
lane_max 14 × t 907.572 s + 300 s = 13,006 s against 0.9 × 12,600 s. Every other gate control passed.

**What the director checked:**
- **coverage-5b-audit's GO** at `98100cc5`, with no blocking or major findings. The change is exactly
  FULL_TIME_S 3.5 → 4.25 h, the job script's header comment, one REQUIRED boundary test and two mutants.
- **The audit's reruns:** 31 tests OK on numpy 1.26 (seeds 0 and 1) and on numpy 2; MUTATION CHECK PASS (43),
  line-identical to the receipt.
- **The bound:** (0.9 × 15,300 − 300) / 14 = 962.14 s. The REQUIRED test passes 907.572 s and 962 s and STOPs 963 s
  with rc 8; the mutant restoring 3:30:00 is killed.
- **The price,** re-derived by the audit from the dry receipt's `full.tsv`: 3.36–3.61 node-h expected at
  t = 907.572 s; ceiling 4.75 node-h, plus the 0.26 already spent = 5.01, within the cap.

**Rulings:**
1. **Amendment 1's §"The director's rulings" binds as written:** option (a); the cap is raised to **5.1 node-h**
   for the study, the 0.26 spent included; the 11-11 dry products stay the STOP record; a new dry run at M_A1 is
   required; a t above 962.1 s STOPs again, and a second time-STOP comes to the director as a decision; the cause
   stays unmeasured; E96D waits for LL5D's gate jobs 61078463 and 61078506 to end and for their atime readings.
   <!-- absence-ok: the director's ruling on this study's scope; no cause measurement is declared or run -->
2. **The submit's limit (the audit's minor a1).** Nothing in code ties FULL_TIME_S to the full submit's TLIMIT, so:
   - the full submit is regenerated at M_A1 with `TLIMIT_ARG=4:15:00` and `TLIMIT=04:15:00`, equal to
     FULL_TIME_S = 15,300 s;
   - the 2026-11-11 `e96d_full_submit.sh` (TLIMIT 03:30:00) is not reused;
   - at the full connect's go, the director checks the literal against the constant.
3. **Each new connect** (the dry run at M_A1, then the full run) comes to the director with its sha256s before it
   runs. Any `--deadline` is stated in the connect and read in the cluster's local time. Base ruling 5 stands: the
   result is read once and enters the paper or note only by Joseph's decision.

Nothing is submitted, deposited or tagged.

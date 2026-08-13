# HANDOFF — Gate 5 replica driver, Session A → Session C, 2026-08-13 ~06:00Z at `ae6e600`

**Why now, measured rather than felt:** Session A's transcript is **11.43 MB / 1,846 assistant messages** after
seventeen hours. The mediator is 4.13 MB and was itself advised to stop making substantive judgments at that
size. **And A's own `state.json` detail still read "Gate 6 running (5 members, 08:44–38:35 elapsed)" while the
members were past 1:03** — the transition-written status field A filed `BEN-192` about, now describing A.

**To Session C, because the replica driver is PET engine code and C found the guard defect below itself.**

## WHAT IS AUTHORIZED — you do not need to ask anyone

**N=50 is authorized** (Joseph: *"sounds good, get N=50 up and running"*). The predeclaration is committed at
**`6bd3707`**. **You have standing authority to SUBMIT the moment the driver passes its tests — do not wait
for Joseph and do not wait for the mediator.** The standing grant is in force: anything needing only a
go-ahead has one.

**Surface only:** a genuine choice turning on his judgment, an irreversible act on incomplete evidence,
something foreclosing an option he might want, or work outside publication scope.

## THE FIVE THINGS NOT INFERABLE FROM THE TREE

**1. The estimator is now a factory — import it, never copy it.**
```python
from annealed_estimator import make_annealed_multifold      # nd-unfolding/pet/
cls = make_annealed_multifold(MultiFold, tf, records)
```
All three arguments were closures from `train_fullevent_nominal.py`'s `main()`. **`MultiFold` is the base
class and is imported inside `main()` (`:374`) — do NOT hoist that import to module scope**, or the module
becomes unimportable without TensorFlow and a `main()` failure becomes an import-time failure for everything.
Array `56832077` died at 51 s on exactly that `ModuleNotFoundError`.

**2. `records` is the RECEIPT'S EVIDENCE CHANNEL, and this is the one that can produce a false result.**
`main()` fails closed if it is empty (*"the anneal interception never fired"*), validates every entry against
`base_lr`/`annealed_lr`, and builds `lr_policy_realized`'s `n_fits_base_lr` / `n_fits_annealed` from it — the
`2 base + 4 annealed` that `56563761`'s receipt reports. **Rebinding or sharing that list yields a run that
anneals CORRECTLY and reports the anneal FALSELY.** Identical estimator, false receipt. **Pass a fresh list
per replica.** `tests/test_annealed_estimator.py` already asserts two factory calls do not share one — that is
the failure a 50-replica campaign surfaces and a single-call test cannot see.

**3. `train_fullevent_nominal.py:252` is NOT a replica guard. Do not "fix" it into one.** `rt` there is the
**target receipt's** block, so it keeps a replica's *target* out of the nominal — it fires in the opposite
direction. Deleting it removes a nominal protection and adds no replica capability. **The real reason the
driver cannot draw a replica is an ABSENCE:** no `--bootstrap-seed` argument, and `bootstrap_seed=` is never
passed to `build_fullevent_loaders`. The loader side is largely done — `bootstrap_seed` is in the signature
(`:1077`), `validate_coherent_bootstrap` exists (`:750`), and D1's coherent dual-leg draw has a real power
test (`test_d1_dual_leg_weights.py:178` asserts *"the draw must actually zero some rows"*).

**4. `assert_refined_target_is_replica` (`fullevent_fps_dataloader.py:736`) has ZERO PRODUCTION CALLERS.**
All five call sites are in `tests/test_fullevent_gate2.py`. **The per-replica-target rule is specified,
implemented, tested — and enforced by nothing. Gate 5 is the path that must call it.** If you build the path
without wiring it, **the suite still passes and the rule silently does not exist**, because the tests invoke
the function directly rather than through the code that should use it. **Wiring it is one line; knowing to is
the finding** (Session C's own, from earlier tonight).

**5. TWO JOBS PER REPLICA, necessarily.** The per-replica negweight-refined target build imports ROOT via
`u2d.refine_stay_positive`; the training needs TF; **no Perlmutter interpreter carries both.** So: ROOT target
build, then TF training consuming the precomputed target. Measured cost from `sacct`: target build `00:55:32`
(256 CPU, no GPU, job `56344268`), training `06:00:36` (32 CPU + 1×A100, job `56563761`). **Per replica 0.93
CPU + 6.01 GPU node-hours; at N=50, 46.3 CPU + 300.5 GPU node-hours, ≈35 h wall at 10 concurrent.**

## DO NOT

- **Do not edit `train_fullevent_nominal.py`, its launcher, or their tests.** They are live pins in
  `p3f-pet-gate4-launch-code-gate-20260813.json` (**19 pins**, re-issued at `ce03f2c`). Editing one costs a
  gate re-issue. **Write a separate replica driver and launcher** — the precedent is
  `sbatch_pet_fullevent_nominal_annealed.sh`, and the factory exists precisely so you can do this without
  copying the estimator.
- **Do not use `--allow-overwrite` anywhere.** It destroys finished publication artifacts; job `56563092` was
  correctly refused for trying.
- **Do not fix `wakerctl.py` on the cluster** — that edits the 114-commit fork Joseph forbade reconciling
  during closeout.
- **Do not run a cluster P4 job** — `p4_evidence.py:25` still hardcodes `REPO` and Joseph's hold names it.

## THE OVERNIGHT RISK IS THAT NOTHING WAKES ANYONE — read this part twice

We are background agents; we run only when woken. **`wakerctl` is DEAD** — crashing every tick since
2026-07-20 on a multi-row `sacct` result parsed as one row (`:464`/`:484`), verified from its own log. **Session
wakeups die with the fleet, which already died once tonight at `22:10:48Z` on a binary-upgrade `EACCES`.** The
mediator's hourly cron dies if its session dies.

**So: ARM A SESSION WAKEUP YOURSELF, immediately, as a second independent path.** Three shots — A's, yours,
the mediator's cron — at the same problem. Tonight's evidence: **cron wakeup is 3-for-3; every other
mechanism has failed at least once.**

**When you wake:**
- **driver done but unsubmitted → SUBMIT IT.** That is the standing authority above.
- **jobs failed → report, and do NOT retry blindly.** The first Gate-6 array died at 51 s on a missing
  `module load tensorflow/2.15.0`; a blind retry would have burned five slots again.
- **Never read silence as success.** Re-measure with `sacct` **and** `squeue` — they disagreed twice tonight
  and `squeue` is the live one.

## STATE AT HANDOFF, all measured at ~05:57Z

| item | state |
|---|---|
| Gate 2 | **fully promoted**, both requirements, no link resting on the promoting lane |
| Gate 4 estimator disposition | **annealed**, recorded; artifact `56563761` **promoted** at `6b68d12` |
| Gate 4 code gate | re-issued `…-20260813.json`, 19 pins, `PASS_CODE_ONLY`, training allowed |
| Gate 6 | array `56834281_[1-5]` **all RUNNING** — 1:21:06, 1:21:06, 1:13:30, 1:11:15, 0:51:15; ~6 h each, so finishing ≈07:00–08:00 EDT |
| Gate 5 | predeclared `6bd3707`, **driver not written** — this handoff |
| pre-commit hook | **enabled**, `core.hooksPath .githooks`, 4 checks, fired on `ce03f2c` |
| HPSS | closed; deletion **cancelled on evidence** (open data is a reprocessed 24%-larger set, so the 240 are not regenerable from it) |
| entry path | 39,969 → ~27,448 tok |

**Gate 6's criterion, for whoever reads its output:** PASS requires the member-to-member spread to **exceed**
the measured same-path scatter `1.26775e-4`. At or below it the branch is **UNRESOLVED** and is reported as
*below the reproducibility floor* — **not** as a small component. Read the **realized** `seed_policy` each
member persisted off `argv`, not the launch command.

## THE ONE RULE THIS SESSION WOULD PASS ON

**Existence and operation are separate facts, and we kept verifying only the first.** Four mechanisms in one
night looked like protection and were not: `.git-blame-ignore-revs` (inert without per-clone config), the
pre-commit hook (inert until enabled), a "300 B cap" (a rule-shaped object that was never written anywhere),
and `wakerctl` (installed, documented, crashing for three weeks). **Every real advance tonight came from
reading an artifact directly; every wasted hour came from acting on a status field, a relayed number, or a
summary of one.**

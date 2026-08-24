# FINDING 2026-08-24 — five process defects from the OI-126 R5 night, and the rules they change

**Evidence home for `BEN-530` … `BEN-534`.** Filed by the OI-126 free-reads lane. Every defect below
is mine or was found in my own lane's work; three of the five are errors I made and reported as
results before catching them.

**CITABLE FOR:** the five defects, their measured operands, and the three playbook amendments they
justify.
**NOT CITABLE FOR:** any statement about OI-126's scientific status, PET's suitability as an
uncertainty product, or the R5 sweep's physics conclusions. The R5 receipt owns those and this file
does not touch them. `BEN-530`'s scope note about the sweep's threshold is a statement about a
THRESHOLD's calibration, not about a verdict.

**Why these are amendments and not new rules.** `PLAYBOOK.md` caps active rules at 25 and there are
exactly 25 (`PB-01`…`PB-25`), so a new row requires retiring one in the same change. `PB-20` already
prefers the amendment path — *"amend or cross-reference an existing mechanism unless the new row
changes a check, rule, or scope."* All five defects are instances of rules that already exist and
were not specific enough to fire, so amendment is the correct taxonomy here and not a workaround for
the cap. Nothing is retired.

---

## BEN-530 — a bar calibrated against one noise source is SILENT about a second, not conservative about it

Amends **`PB-12`**.

`r5_sweep.py`'s docstring declares its thresholds *"against the epoch-to-epoch val_loss scatter"*.
That is one noise source: variation **between epochs within one training run**. Three separate
errors followed from never writing down which source the bar covered.

1. **I judged a between-run quantity with a within-run statistic.** I built a "noise floor" from the
   member's `own_epoch_scatter` (`val_successive_diff_sd = 4.986350220533611e-04`) and used it to
   assess a difference measured **between two runs**, whose measured value was **D = 0**. Those are
   different populations. Retracted at `7da3b3d6`; my prediction that a favourable verdict was
   "probably unattainable" was refuted by the data.
2. **The justification I wrote for framing (b) was false.** It read *"the relevant noise … is that
   member's own evaluation noise."* Evaluating fixed weights on a fixed row set is deterministic, so
   there is no evaluation noise to be the relevant one. Struck at `74cee642`.
3. **The source that actually moves `dL` was omitted from the calibration entirely: which rows you
   summed over.** Measured from the R5 receipt (`sha256 ca5759d7…`), `dL_rowset_max_dev` as a
   multiple of the 2.4e-3 CONFIRM bar:

   | member | multiple of the bar | receipt's cell |
   |---|---|---|
   | `replica_43` | 0.38x | ROW-SET IMMATERIAL |
   | `replica_49` | 0.75x | ROW-SET IMMATERIAL |
   | `replica_29` | 0.82x | ROW-SET IMMATERIAL |
   | `replica_00` | 0.96x | ROW-SET IMMATERIAL |
   | `replica_26` | 3.74x | THRESHOLD-INDETERMINATE |
   | `replica_45` | 4.40x | THRESHOLD-INDETERMINATE |

   Two members are already over the bar on this omitted source. Three more sit at 0.75–0.96 of it on
   a **max over two alternatives**, which understates the population it stands for.

**The rule.** A threshold names the noise statistic it is calibrated against, that statistic's unit,
and the population it was measured over — and states which sources it does **not** cover. "Not
calibrated against X" is not "conservative with respect to X."

---

## BEN-531 — a discriminating test publishes its separation and its size BEFORE it runs

Amends **`PB-12`**.

`r5_c2_discriminator.py`, job `57507676`, was built to decide whether `replica_29`'s row-set
shortfall was sampling noise or a split error. It could not have done so, and every operand needed to
know that was available before submission.

- Its two endpoints were `A = 2.6588668915084046e-02` and `B = 2.6414423654711385e-02`, so the
  interpolation's **entire dynamic range** was `|B-A| = 1.7425e-04` = **0.66% of A**.
- The gap it had to explain was the residual: `-3.19728470785198e-03` = **12.03% of A**, i.e.
  **18.3x** the whole range available to the mixing weight. `C_pred` was therefore effectively a
  constant and the interpolation contributed nothing.
- Its declared criterion was `same_sign` over two draws. Under the symmetric sampling null it names,
  `P(two draws share a sign) = 1/2`. So the test's **size** — its false-positive rate against exactly
  the hypothesis it was testing — is **one half**. (The receipt words this as "50% power"; the number
  is right and the word is loose. Size is the correct term.)
- One of the "two draws" was not a draw: `C1` equals the sweep's already-published
  `C_independent_perm` (`2.4619673097196985e-02`). Effective new n was **one**.

**The rule.** Before a discriminating test runs, publish the separation between its endpoints, the
scale of the residual it must resolve, and its size or power under its own stated null. If the
separation cannot resolve the residual, report **NO POWER** with the achieved leverage. Do not report
a direction as though it were a discrimination, and do not report a reproduced sign as a settled
mechanism. The 18.35 leverage figure in the receipt is `residual / |B-A|` — its denominator is an
interpolation span, not a sampling scale, so it is not a significance and must not be read as sigma.

---

## BEN-532 — ssh connection multiplexing makes a node-local instrument look like a cluster instrument

Sharpens **`PB-11`**, which already says to query the scheduler. This records *why the wrong
instrument looked adequate*, which is the part that let the rule be violated without noticing.

`~/.ssh/config` sets `ControlMaster auto` with `ControlPersist 12h`. Repeated `ssh saul.nersc.gov`
calls therefore reuse **one connection on one login node**. Measured:

- default: `login29`, `login29`, `login29`
- with `-o ControlPath=none`: `login37`, `login37`, `login28`

So every `pgrep`/`ps` result obtained over that session was one login node's, while the job in
question was running on `nid001104`. The repetition read as corroboration and was a single
observation. Compounding it: `squeue -u <name>` exits **0 with 0 rows** for a nonexistent user, so a
mistyped or wrong-scoped query is indistinguishable from an empty queue.

**The rule.** A cluster-wide liveness question is answered by `squeue`/`sacct`, never by a process
list — a process list is one node's even when the connection count suggests otherwise. Use `--me`
rather than `-u <name>` so the no-such-user branch is unreachable rather than merely unchecked.

---

## BEN-533 — another lane's scheduler state is not yours to act on, and `--me` is not "my jobs"

Amends **`PB-18`**.

I concluded a peer lane's chain was dead and submitted a duplicate job, `57506433`. Two independent
errors, either of which alone was enough:

- **Wrong scope.** The condition I tested was whether the peer *session* was running a process. The
  owner session was alive; `idle` in a session listing means *between turns*, not dead.
- **Wrong instrument.** Half the evidence was `BEN-532`.

I cancelled mine by job ID rather than `pkill -f`, which is the one thing that went right.

**The mechanical reason this needs a rule and not just care.** `squeue --me` returns every job under
the shared account, across all lanes. Measured today: `57275989`, QOS `cron`, held with *"user env
retrieval failed requeued held"*, appears in my own `--me` output and is **not my job**. So "my
queue" and "my jobs" are different sets, and nothing in the tooling distinguishes them.

**The rule.** Never cancel, resubmit, or kill a job you did not submit without that lane's own word,
however dead it looks. The cost asymmetry settles it: waiting costs a delay, acting costs a
double-spent allocation of the scarce resource. Ruled by Joseph on 2026-08-24.

---

## BEN-534 — a hold is a property of the BRANCH, not of anyone's restraint

Amends **`PB-18`**.

I told Joseph that a set of commits was "held pending your publishing call." Publication on shared
`main` is not something a lane can withhold. Measured:

- My lane's commits at 08-23 **20:48, 20:50, 20:53, 20:54, 20:56** — `9a881c03`, `82cac45f`,
  `87310615`, `bc76ac6c`, `0e53f962` — are all ancestors of `origin/main`, carried out by the
  close-out lane's push containing `dfef7871` (21:51) and `8f230444` (22:54). I did not push any of
  them.
- **That is five commits. I reported it as four, twice, in the session that followed.** I had not
  re-derived the count, and the correct figure is five.
- The consequential half is not the mechanism but the relay: I put that assurance into four status
  reports to the decision-maker without asking what enforced it.
- **Live instance right now:** `HEAD` is 10 commits ahead of `origin/main` (`8f230444`) and every one
  of them publishes with the next lane's push.

**The rule.** Work that must wait for a decision gets its own branch or no commit. Never describe a
commit on shared `main` as held, and never relay such a description onward.

---

## What none of this authorizes

No scientific conclusion, no adoption, no promotion, and nothing about OI-126. Three playbook
amendments and five casebook rows.

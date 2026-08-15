# AUTHORIZATION 2026-08-15 — run standard-P4 stages 4–6 (the 5D→4D projection) **IF** the verifier returns PASS

**Granted by Joseph Bailey, 2026-08-15.** Recorded before use, per `BEN-201`. **This authorization is
CONDITIONAL and does not take effect unless and until its condition is met.**

## The grant, verbatim and complete

Context — the mediator explained that the 5D→4D projection is stage 6 of `run_p4_standard.sh`, that the
script is fail-closed on a verifier token, and that the live verdict sets
`authorizes_covariance_stages_4_6: false`. Joseph then said:

> "okay yes if it comes back pass, run it"

## The condition

**A freshly issued `standard-p4-verifier` verdict that:**

1. records `verdict: PASS`, and
2. records `authorizes_covariance_stages_4_6: true`, and
3. **passes `p4_check_verifier_token.py` on its own terms** — the digest matches a committed, tracked
   receipt identical to its committed blob; the reviewed commit is an ancestor of `HEAD`; and **every
   file that verdict reviewed is byte-identical between the reviewed commit and `HEAD`.**

**Condition 3 is not decorative.** The previous verdict would have been refused for staleness alone
(`25 / 43` reviewed files changed) even had it said PASS. **If the gate refuses the new verdict for any
reason, the condition is NOT met and this authorization does not fire.**

**If the verdict returns BLOCK, or PASS with `authorizes_covariance_stages_4_6: false`, nothing runs**
and the outstanding defects go back to Joseph as a list.

## SEPARATION OF DUTIES — added by the mediator, not by Joseph, and binding

**The lane that issues the verdict MUST NOT be the lane that consumes the token and runs the chain.**

This campaign already carries one case of a single agent occupying both roles: `VL132` records that
`C_stat` was built by **one** builder against an authorization scoped to two blind builders, and the
receipt is forbidden from claiming independent verification as a result. **The same shape here would be
worse**, because the verdict is not merely a check on the chain — it is the *permission* to run it. An
agent that writes its own permission slip and then acts on it has performed no verification at all.

`run_p4_standard.sh`'s own comment concedes the gate cannot stop a falsified verdict; what it does is
*"move the act from setting an invisible variable to committing a false receipt into the ledger under
their own name — the difference between an accident and a decision."* **The separation is what keeps
that guarantee meaningful.**

**Therefore:**
- The verifier lane issues the verdict and **stops**. It does not run the chain, does not set
  `P4_VERIFIER_PASS`, and does not adopt.
- A **different** lane, dispatched after the verdict lands, computes the token from the committed
  verdict and runs the chain.
- **Setting `P4_VERIFIER_PASS` by hand to any value not derived from a committed verdict is
  prohibited absolutely** and is not covered by any grant on record. `KNOWN_ISSUES #21`.

## What is authorized

**Stages 4–6 of the canonical standard chain**, culminating in the 5D→4D marginal projection
(`p4_project_4d.py`), consistent with Joseph's standing 2026-08-07 decision: *adopt the exact 5D→4D
marginal and label the independent 4D estimator a cross-check.* **No separate 4D physics, no 4D lateral
work.** Per the close-out runbook this lane needs **no GPU**.

## What is NOT authorized

1. **ADOPTION IS NOT INCLUDED.** Running the chain produces a **candidate**. Designating any product
   quotable, adopting the 5D or 4D covariance, or promoting anything remains **Joseph's alone** —
   `AUTHORIZATION-20260815-consensus-grant.md` §3, *"promotion is not compute and is not covered."*
   The chain may run; its output stays a candidate until he says otherwise.
2. **No re-running of stage 3 or any physics unfold.** The projection consumes the existing products.
3. **No editing of `p4_*` sources to make the gate pass**, and **no repinning** of any receipt-bound
   launcher (`OI-123`).
4. **The five Gate-6 prohibitions at `19585b7` stay live** — `do_not_select_passing_subset`,
   `do_not_construct_C_ML`, `do_not_move_central`, `do_not_start_leg_2`, `do_not_retry_unchanged`.
5. **Nothing into `docs/analysis-note/`.** `values.tex`'s superseded `5.81e-38` / `6.24e-38` /
   `1.65e-38` are **downstream of adoption**, not of this run, and stay untouched.
6. **`/pscratch/sd/j/josephrb/gate6traj-reconcile-56847059` stays frozen.**

## Open questions this authorization does NOT resolve

- **The 2026-08-08 stage-3 run.** `P4_STANDARD_STATUS.md:4` records a standing hold from Joseph — *"no
  cluster P4 run"* — and ten `mode=produced` receipts dated 2026-08-08 exist on the cluster. **Whether
  that run was authorized has been put to Joseph twice and is unanswered.** The projection consumes
  those products. **This is recorded as a known, unresolved dependency of the run, not as an objection
  to it** — and it is a further reason adoption stays separate from execution.
- **The ten stage-3 products are untracked** and live only on purgeable scratch.

## Related

- `AUTHORIZATION-20260815-consensus-grant.md` — cost grant; promotion explicitly excluded.
- `DECISION-20260815-joseph-oi6-oi8-oi126.md` — `OI-6` closed on purity; `OI-8` in force with a
  corrected basis.
- `KNOWN_ISSUES #21` — why an arbitrary `P4_VERIFIER_PASS` does not work and must not be attempted.

# DECISION 2026-11-06 — Joseph: the 12-hour job limit is relaxed to the scheduler's own maximum

**Recorded by** the paper-tighten lane, as director.

## What led to it

**The rule.** `DECISION-20261101-joseph-reopen-1b-and-compute-for-limitations.md:55` (item 2) states the director's
reading of Joseph's compute approval, "which Joseph may override": "CPU only, jobs under 12 h, regular QOS, nothing
written to CFS."

**Where it bound.** RPD-RECO's step c0 (PR #848, `fd_rpd_reco.py` at `10731ed3`) runs its real pass and 20 partitions
in one invocation. The director's B2 ruling capped a step's priced wall-clock at 39,600 s (11 h) and sent any c0 above
that back as a design question. The login timing receipt (PR #849, `timing.json` sha256 `303850f7…`) plans c0 at about
25.1 h, at draws × S × 1.5 with S = 3.879e-7 s per draw. So c0 refused under the cap.

## Joseph's message, verbatim

> listen the 12 hour job limit isn't strict, we can relax this rule. why did work pause? also, can we get a prd referee on the methods paper and see if it scores way better?

sha256 of the text plus a final newline begins `c0e22726eaa2d9b5`. The first sentence is the decision. The other two
are a question and a request, which the director answers and carries out separately.

## What is decided

1. **The per-job wall-time limit is the scheduler's own maximum**, not 12 h. The director measured it on 2026-11-06
   with `sacctmgr -nP show qos format=name,maxwall` from a Perlmutter login node: `regular_0`, `regular_1`, `shared`,
   `preempt` and `overrun` each have MaxWall `2-00:00:00` (48 h).
2. **The director's operational reading of it:**
   - a step's priced wall-clock may be at most 165,600 s (46 h), which leaves 2 h of the 48 h for setup, staging and
     the receipt;
   - a single-threaded step may use the `shared` QOS, which bills only the fraction it requests, in place of a full
     regular node.
3. **Unchanged:**
   - CPU only;
   - nothing written to CFS from a job;
   - each campaign is declared, priced and bound before it runs, and its report gives the cost measured;
   - a single campaign priced above half of the group's remaining balance goes back to Joseph with its price first;
   - "a set" is priced as a whole: many long jobs together are a campaign price, not a per-job one.

## What follows

- **RPD-RECO B2:** the refusal `N > 39,600` becomes `N > 165,600`. c0 runs as one invocation with no split, as the
  ruling already required. Everything else in B2 stands.
- Earlier records that state "under 12 h" as a rule now read as this record says. They are not edited.

## Not decided here

- Any claim, wording or framing.
- Any campaign's price. Each is still priced and bound on its own.

Nothing is submitted, deposited or tagged.

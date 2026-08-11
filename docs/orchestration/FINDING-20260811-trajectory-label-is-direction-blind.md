# The trajectory harness's fallback label says "under-achieves" for an overshoot — found by running it on a configuration that fails the other way

**Found 2026-08-11 by Session C (PET), in its own lane's harness, on job `56691812`.** BEN id **PENDING
BLOCK ASSIGNMENT** (see `FINDING-20260811-gate4-prerequisite-points-at-a-deleted-blocker.md` §6 — the PET
range is exhausted and `max+1` is BEN-105's documented failure).

## 1. The defect

`nd-unfolding/pet/step1_increment_trajectory.py:296-300`, the third branch of the verdict selector:

```python
else:
    verdict = "UNDER_ACHIEVES_AT_ITER0_SAME_SIGN"
    reading = ("step 1 under-achieves at iteration 0 but with the CORRECT sign, so the sign "
               "inversion is an iteration effect layered on a step-1 capacity/convergence "
               "shortfall present from the start.")
```

The branch is selected by elimination: not `end_to_end_sign_is_wrong`, and not
`abs(it0["end_to_end_achieved_over_required"] - 1.0) <= 0.10`. That condition is on the **magnitude** of
the deviation and says nothing about its **direction**, so the branch fires for `ach/req = 0.85` *and* for
`ach/req = 1.15` and asserts *"under-achieves"* either way.

Measured on the annealed arm of `56691812`: iteration 0 has `end_to_end_achieved_over_required = 1.1101`.
The correction **over**-achieves by 11.01%, and the harness reported `UNDER_ACHIEVES_AT_ITER0_SAME_SIGN`.

## 2. Why it was invisible until now, which is the reusable part

Every configuration this harness had ever been run on **under**-shot at iteration 0. The pre-anneal
artifact gives `0.9721`; the whole diagnostic programme (BEN-043, the step-1 under-achievement finding,
the `32%` open blocker in the Gate-4 receipt) is about a *deficit*. The label was written by someone who
had only ever seen deficits, and its wording encodes that assumption as a fact.

**So the tell is not in the code, it is in the coverage:** a fallback branch whose *message* is more
specific than its *condition*. The condition tests `|dev| > 0.10`; the message claims a direction. That
gap is invisible while the data only ever arrives from one side, and the first run from the other side
prints a confident falsehood.

This is the same family as the retired `recovery >= 0.80` bar and the `-1e-30` covariance floor —
**a predicate and its human-readable claim drifting apart** — but with the drift in the *message* rather
than the threshold. Mechanical sweep it suggests: for any `if/elif/else` chain that assigns a verdict
string, check whether the string asserts anything the condition does not test. Directional words
(`under`, `over`, `above`, `below`, `rises`, `falls`) in a branch selected by an absolute-value test are
the specific smell.

## 3. What is and is not affected

**Unaffected:** every number. The trajectory table, the reproduction gates, `end_to_end_sign_is_wrong`,
`r1_required_mean`, the cap-saturation telemetry and all six iterations across both arms are computed
independently of the label. The ledger row for `56691812` reads the branch from the **numbers** against
the predeclared criteria, not from this label, and its conclusion (predeclared branch **REPAIRED**) does
not depend on it.

**Affected:** the string `UNDER_ACHIEVES_AT_ITER0_SAME_SIGN` and its `reading` in
`STEP1_TRAJECTORY.slurm-56691812.json`. **Do not quote either for that arm.** The honest label for an
annealed iteration 0 would be `OVER_ACHIEVES_AT_ITER0_SAME_SIGN`, and the accompanying reasoning
("a step-1 capacity/convergence shortfall present from the start") is precisely backwards for it — the
annealed arm's iteration 0 does not fall short, it exceeds.

## 4. Disposition: NOT patched in this commit, and the reason is not caution

Two reasons, in order of weight:

1. **Editing the harness would move a sha that the run just produced results under.** `56691812`'s
   receipts bind `step1_increment_trajectory.py` at `1acb1869c57f9772…`, printed by the run's own
   preflight. A same-day edit would leave four committed receipts citing a file whose bytes no longer
   exist at that digest — the exact condition that made `wakerctl_sha256` unverifiable for three weeks.
   The fix belongs in a commit that also re-runs or explicitly re-pins, not squeezed in beside the
   result.
2. **The label is not a gate.** Nothing consumes it; the campaign's branch determinations are made from
   `end_to_end_achieved_over_required` and `end_to_end_sign_is_wrong`. So the cost of leaving it one more
   commit is a misleading string in one receipt, which this file now annotates, against the cost of
   invalidating a provenance chain.

**The fix, specified so whoever takes it does not have to re-derive it:** split the third branch on the
sign of `it0["end_to_end_achieved_over_required"] - 1.0` into
`OVER_ACHIEVES_AT_ITER0_SAME_SIGN` / `UNDER_ACHIEVES_AT_ITER0_SAME_SIGN`, add both to
`verdict_label_history` so the retired single label stays readable, and **power-test both directions** —
construct an iteration-0 record at `ach/req = 1.15` and one at `0.85` and assert the two labels differ.
A test that only ever feeds it a deficit is what let this ship.

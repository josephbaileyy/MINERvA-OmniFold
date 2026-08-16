# FINDING 2026-08-16 — a hash pin cannot detect a stale checkout, because both sides of the comparison go stale together

**`BEN-301`.** Filed by the mediator. Found while performing the independent digest confirmation that
was supposed to be the *last* step before launching the authorized arm-1 resubmit. **The launch did not
happen, and the gate is not what stopped it.**

## The gate, and what it actually proves

`sbatch_foldforward_instrumented_closure.sh` carries a `G0` pin block: a literal sha256 for the
**wrapper** (`closure_foldforward_instrumented.py`), checked at launch, fail-closed, and **printed** so
the log records the digest the task really ran. It has been maintained exactly as designed — four
documented moves in two days:

```
ee269b09  →  b24cfefe   MOVE 1  2026-08-15  report-annotation fixes
b24cfefe  →  0e1471ba   MOVE 2  2026-08-16  anneal attestation (BEN-317)
0e1471ba  →  7499814e   MOVE 3  2026-08-16  end-of-run recording (67c94df)
7499814e  →  e284cdbc   MOVE 4  2026-08-16  BEN-342 fixture + the ~105 correction
```

**Verified here independently** — `hashlib`, not the `sha256sum` the reporting lane used — that the
working tree's wrapper is `e284cdbc…` and the pin literal is the same string. Exactly one pin line
changed in `8ed164a`; DRIVER, ANNEALED and ENGINE are byte-identical, so the receipt-bound driver was
not repinned (`BEN-270`). **The pin is correct, maintained, and fit for its stated purpose.**

## What the cluster holds

```
cluster HEAD            683bdcc   — an ANCESTOR of local HEAD, 663 commits behind it
                                    and "behind 487" its own `github/main`
wrapper on cluster      ee269b09  — the ORIGINAL digest, pre-MOVE-1
pin literal on cluster  ee269b09  — MATCHES
tracked dirty / staged  19 files      untracked  735
```

**So `G0` would PASS.** The wrapper and the literal that authenticates it are stale **together**, and
they agree with each other perfectly. A gate that compares a file to a constant stored beside that file
is measuring *internal consistency*, and internal consistency is exactly the property a stale checkout
preserves.

**Had the run gone out, it would have executed the pre-MOVE-1 wrapper** — no end-of-run recorder
(MOVE 3), no anneal attestation (MOVE 2), none of `BEN-342` — and reported `G0 PASS`.

## Why this is not the same as "someone forgot to deploy"

Three separate lanes and the mediator spent this session establishing, by measurement, that:

- the successor instrument records the **right** quantity, not the neighbour (`BEN-342`);
- the fixture is no longer degenerate on the weight-leg axis, proven by mutation;
- the headline amplitude `~105 draw-sd` derives from nothing and is really `75.8` (`BEN-361`, on its
  own author);
- the proposed `OI-125` re-run was already denied inside the launcher being proposed (`BEN-334`).

**Every one of those checks was performed against the local tree. None of them was a claim about the
machine the code runs on**, and no gate in the chain distinguishes those two things. The verification
was sound and would have authorized a run that contained none of it.

## The specific asymmetry that makes this durable

A pin **detects tampering** and **records provenance**. It is *strong* against "someone edited the
wrapper without saying so" and **structurally blind** to "this whole checkout is 663 commits old",
because the second failure moves the checked object and its expectation by the same amount.

`MOVE 1`'s own maintenance note is evidence the design was understood: it observes that
`logs/ff_57038937_{3,4,5}.out` carry `ee269b09` as the wrapper those tasks ran, so provenance is
recoverable **after the fact from the logs**. That is true, and it is the mitigation — **but it is a
forensic property, not a gate.** It tells you what ran once you go looking; it does not decline to run.

Note also that `train_fullevent_nominal.py` — the artifact whose `:576-577` is *the definition* the new
instrument was verified against — is itself **modified on the cluster** (9 insertions, 26 deletions
against `683bdcc`). The reduction lines themselves still read the reco leg with the same quotient, so
the definition survives; but the file the verification treated as fixed ground is not fixed there.

## THE RULE

> **A digest pin authenticates content against an expectation stored in the same tree. It cannot
> authenticate the tree. Before a launch, check the deployment's REVISION against the revision you
> verified — a separate question from any pin, and one no pin will ever answer.**

Corollary, and the cheaper half: **`G0 PASS` in a log is not evidence that current code ran.** Read the
printed digest against the digest you expect, rather than reading the verdict.

## Disposition

**No run was launched.** Making the cluster current is not a mechanical fix: the checkout is 487
commits behind its own remote with 19 tracked files dirty (including evidence JSONs and
`train_fullevent_nominal.py`) and 735 untracked paths, its remote is named `github` rather than
`origin`, and a second worktree `fe-fps-campaign` shares the area. **Escalated to Joseph** — it is a
potentially destructive action on shared state, under the standing "do not pull the cluster science
repo" prohibition, and it is not the mediator's to take.

Related: `BEN-270` (the driver is receipt-bound), `BEN-317`, `BEN-332` (a check whose result depends on
local git state), `BEN-342`, `BEN-334`.

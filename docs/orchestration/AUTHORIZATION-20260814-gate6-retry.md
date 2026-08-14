# AUTHORIZATION RECORD — the Gate-6 member-family retry (2026-08-14)

**Why this file exists, given the standing instruction to stop producing artifacts.** Joseph's redirect was
*"no new receipts, findings, or convention documents unless a gate requires the artifact."* **Gate 6 requires
exactly this one.** `ND_OMNIFOLD_STATUS.md:40` reads *"A retry design is written and **awaits Joseph's
decision**"* — this record **is** that decision, so writing it is gate work rather than beside it. Structure
follows `AUTHORIZATION-20260813-gate4-estimator-disposition.md`, including its `DO_NOT_RECORD_AS` discipline.

## The authorization, verbatim and complete

> Also yes I authorize the gate 6 retry

**That is the entire authorization.** Ten words. Everything below is scope, and none of it is his.

## Transcription provenance

Transcribed by `personal-orchestrator` (peer session `minerva-omnifold-58`, socket
`uds:/tmp/cc-socks/65811.sock`) from Joseph's typed message immediately preceding its dispatch — no
intermediate storage, no paraphrase step. **Lane A copy-pasted the block and cannot see the original; it
attests only that the text above matches the message it received.** Same chain and the same division of
attestation as the 2026-08-12 and 2026-08-13 records.

Written per `HANDOFF-20260812-1145Z.md:126` — *"write any `[JOSEPH-VERBATIM]` authorization into a committed
receipt BEFORE acting on it"* — and **nothing in it has been acted on by lane A.**

## WHAT IT AUTHORIZES — and what remains, in the same sentence, because `BEN-244` was filed tonight about exactly this

**`BEN-244`'s mechanism:** a stale blocker citation *"produced no error and no symptom for 36 hours — only work
that never started."* Its inverse is equally cheap to cause, so the unblocking and the residue are stated
together and never apart:

> **This authorizes the *changed* retry that `PLAN-20260813-gate6-cml-retry-design.md` proposes, and it
> leaves the Gate-6 family blocked**, at `19585b7`, `family_verdict BLOCK_GATE6_ML_ENSEMBLE`,
> `passing_members [1]`, `failing_members [2, 3, 4, 5]` — all verified in this turn from
> `state/gate6-member-trajectories-result-56847059.json:109-111`.

### ALL FIVE PROHIBITIONS REMAIN LIVE. THIS AUTHORIZATION CLEARS NONE OF THEM.

The natural misreading is that a retry authorization discharges `do_not_retry_unchanged`. **It does not, and
the distinction is not pedantic.** Verified verbatim at `:112-118`:

| prohibition | status after this record |
|---|---|
| `do_not_select_passing_subset` | **LIVE, untouched** |
| `do_not_construct_C_ML` | **LIVE, untouched** |
| `do_not_move_central` | **LIVE, untouched** |
| `do_not_start_leg_2` | **LIVE, untouched** |
| `do_not_retry_unchanged` | **LIVE, and satisfied by construction rather than lifted** |

**`do_not_retry_unchanged` forbids an *unchanged* retry. A changed retry was never inside its scope**, so
there was never anything for this authorization to remove. What Joseph supplied is the **user go to spend
compute on the changed retry** — the thing `STATUS:41` said was missing. The prohibition set is unchanged at
five, and any future record showing four has expanded scope without authority.

## WHAT IT DOES NOT AUTHORIZE — written in, because a bare "yes" invites expansion

Each of these was named by the mediator in the dispatch and each is verified below rather than relayed.

- **NOT Leg X.** Held on two lanes' independent recommendation and Joseph has not reversed that; its 2×2
  stays unsubmitted. **Stated precisely, because `STATUS:59` says Leg X *"is authorized"* and that is also
  true:** Leg X holds a *readout* authorization (`state/gate6-legx-readout-authorization-20260813.json`) and
  is nonetheless **deliberately not submitted**. This record changes neither half — Leg X remains
  authorized-in-readout, held, and unsubmitted.
- **NOT skipping Leg 0.** `PLAN-20260813-gate6-cml-retry-design.md:144-146` makes the ordering *"forced, not
  stylistic"*: Leg X *"measures two main effects with one degree of freedom each and **no replication**, so it
  has no internal error scale; Leg F is what supplies that scale"*, and **Leg 0 comes first because it is free
  and may retire one of the four failures before either training leg is costed.** Leg 0 was authorized
  separately by the mediator and still comes first. Leg 0 is inference-only, changes
  `step1_increment_trajectory.py` only (**not** in the Gate-4 code gate's 19 pinned paths, so no gate
  re-issue), and **does not promote, select or remove member 3** even if it retires member 3's margin.
- **NOT `C_ML` construction.** The retry clears a *measurement* blocker. `C_ML` additionally needs a nominal
  extraction product — `combine_cml_bkgsub.py:75` defaults `--cv` to
  `products/pet/bkgsub/pet_nominal_bkgsub_5d_xsec.npz` and `:81-82` takes **both its reference and its
  positivity mask** from it (`cv = np.asarray(np.load(args.cv)["xsec_flat"], float)`, `rep = cv > 0`) — and
  faces `--expect 12` against Leg 1's five.
  **`do_not_construct_C_ML` is now enforced in code as well as by the prohibition, and was not when this
  record was drafted.** At `c29e3522` the `--expect` mismatch was a `[cml][WARN]` that built anyway; lane A
  filed that as `OI-72` believing it new. **Both halves of that were wrong by the time this was pushed, and
  the record is corrected rather than quietly adjusted:** the defect was already documented as part of
  `BEN-244` (`FINDING-20260814-a-decision…:96`), and lane B **fixed it at `4d04ceb`, 2026-08-14 19:45:25** —
  fail-closed by default, an explicit `--allow-incomplete-family` escape that rewrites the output to a
  `NONQUOTABLE-DIAGNOSTIC.` path, plus a regression test. `OI-72` is **withdrawn**, and the correction is kept
  visible because *"a claim true when measured and false in the commit carrying it"* is `BEN-225`, whose own
  remedy — re-verify after `git pull --rebase` — is the only reason this was caught.
  **The consequence for this authorization is unchanged and slightly strengthened:** `C_ML` still needs a
  nominal extraction product and a complete family, and the family-completeness half now refuses rather than
  warns.
- **NOT member selection.** `do_not_select_passing_subset` stands. **No member is promoted, excluded, or
  quoted by this record** — including member 1, the only passing member, which is precisely the one a
  convenient reading would take.
- **NOT the VL100 quotability question**, separately with Joseph and unresolved. Now tracked as **`OI-71`**;
  before tonight it was tracked under no id at all.

## DO_NOT_RECORD_AS

- **DO NOT RECORD AS:** *"Joseph unblocked Gate 6."* He did not. Gate 6 is blocked at `19585b7` and stays
  blocked; he authorized **one retry attempt** whose purpose is to produce the evidence that could later
  justify unblocking it. A retry is an experiment, not a verdict.
- **DO NOT RECORD AS:** *"the retry is authorized, therefore the legs may run in any order."* The ordering is
  predeclared and forced, and Leg 0 is first.
- **DO NOT RECORD AS:** *"Joseph endorsed the PLAN's reasoning."* This is **approval by reference**, the same
  status as *"Okay do the annealed"*. The PLAN's physics and cost argument is `[CLAUDE]`-class and the
  mediator's. **If it contains an error, the error is the mediator's, and the disposition routes back through
  the mediator to Joseph rather than being re-decided by a lane.**
- **DO NOT RECORD AS:** *"four prohibitions remain."* Five do. See the table above.

## Not authorized by this, and not touched by lane A

No `scancel`, no resubmit, no `scontrol update`, no job submission.
**`/pscratch/sd/j/josephrb/gate6traj-reconcile-56847059` was not touched** — the mediator is sequencing the
retry, not lane A, and Leg 0 comes first. **Nothing in this dispatch went near the cluster**, so no live job
state is reported here: every number above is quoted from a committed receipt or a tracked source file read in
this turn, never from `sstat` or `squeue` (`CLAUDE.md`'s same-turn rule cuts both ways — a live count I cannot
take is a count I must not print).

## Related

`PLAN-20260813-gate6-cml-retry-design.md` (the design this authorizes),
`state/gate6-member-trajectories-result-56847059.json` (the block being retried),
`AUTHORIZATION-20260813-gate4-estimator-disposition.md` (the model, and the `OI-23` residue),
`BEN-244` / `FINDING-20260814-a-decision-that-reached-its-own-record-and-nowhere-else.md` (why the unblocking
and the residue are written in one sentence), `OI-71` (VL100 quotability), `OI-72` (the `--expect` warn).

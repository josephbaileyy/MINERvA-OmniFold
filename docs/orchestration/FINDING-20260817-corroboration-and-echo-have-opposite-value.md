# Corroboration and echo have opposite evidential value — `BEN-312` running in reverse

**Lane B, 2026-08-17. Read-only: code reads, `git show`, `ListAgents`. Nothing submitted.**
Filed in lane B's own block (`248`) **at lane A's insistence and on its reasoning**, which is better than the
argument I opened with — see §5.

---

## THE ONE PARAGRAPH

`BEN-312` records three parties deriving one number from one source, where **agreement read as
corroboration** — an *inflation* failure. **This is the same mechanism inverted: genuine independent
corroboration reading as an echo** — a *deflation* failure. In both directions the defect is identical: **the
ROUTE is not carried with the fact.** And because corroboration and echo have **opposite** evidential value,
a relay that omits the route **destroys** the difference rather than degrading it. Most missing-context
defects lose precision; this one inverts a sign.

**The check is one clause and needs no tooling: when relaying a claim, say where it came from.**

---

## 1. The instance

A peer lane independently derived this lane's gate-1 conclusion — that `bootstrap_nd.py:28-29` already routes
`--seed` to the estimator when `--fixed-data-seed` is set, that `seedscan_split.py:36` exposes
`--estimator-seed`, and that gate 1 is therefore two modules rather than four legs — **by reading the code,
not this lane's document.**

**The independence is evidenced, not assumed.** That lane stated, unprompted and *before* producing the
finding:

> *"`EXTENT-20260817-…md` exists on main and names this launcher; **I HAVE NOT READ IT**, and it may already
> carry some of §1."*

**It was then relayed to me as new information**, framed as *"gate 1 is smaller than your own report said, in
your favour."* I flagged it back as my own conclusion returning to me — **correct on the facts I had, and
wrong on the merits.** The mediator self-reported the transport error: *"the fact was corroboration; my
framing made it look like novelty. Those have opposite value and I collapsed them."*

**There was no reading of the relay that preserved the fact, because the relay did not contain it.** Both
available readings lose the same thing:

| my reading | the relay's framing |
|---|---|
| "this is my own finding echoed back" → discard a second derivation | "this is new information" → record a peer's independent confirmation as my own restatement |

**Same loss, opposite routes.** That is the diagnostic signature of a missing dimension rather than a wrong
value: no amount of care on the receiving end recovers it.

## 2. Why a separate row rather than an annotation on `BEN-312`

**Lane A's argument, which is decisive and is not about this instance's cost:**

> A row that records only the **inflation** direction teaches a reader to **discount agreement**, which makes
> the **deflation** failure MORE likely. So the two directions are not two instances of one lesson — **they
> are a lesson and its own iatrogenic side effect.**

An annotation inside `BEN-312` would be read by exactly the audience `BEN-312` has already primed to distrust
agreement. **The remedy for one direction is not a widening of the other**, which distinguishes this from
`BEN-386`'s category error, where no widening helps at all. On lane A's taxonomy (`BEN-391`), the
inflation/deflation pair are **coverage** failures with an unrestricted-control remedy; `BEN-386` is the
category error where that remedy does not apply.

**My original argument — that it cost me a near-discarded finding — is weaker and is recorded as the
subordinate reason.**

## 3. What it composes with

**`BEN-247`'s stopping condition.** *"I got rows"* satisfies a search; *"a peer told me X"* satisfies a
belief. In both, the signal arrives **without the dimension that would let you evaluate it**, and in both the
remedy is to demand the missing dimension explicitly rather than to distrust the signal.

**Lane A's addition, which makes this the worse of the two:** *a search you can re-run; a relay you cannot,
because the route is gone once the message is sent.* A stale `sacct` query can be reissued against the same
scheduler. A message's provenance exists only in the sender's context, and that context is destroyed by the
next compaction or session death.

## 4. Two further instances, same day, same channel

**(a) The route matters for a claim's DEPENDENCIES, not only its ORIGIN.** The same relay later carried a
**true** capability claim — `--fixed-data-seed` exists and works — **without the specification it depended
on.** When lane C conceded spec **(B)** (that `M(ii)` is a *joint* measurement on the composite), the
capability stopped helping: a joint variation across four legs at seed `42` needs **all four seed-variable at
once**, so partial capability buys nothing and `sweep_bank_5d.py:252` became the **blocking dependency**
rather than one of two parallel edits. **The capability claim never changed truth value; its usefulness
inverted.** Carried in `EXTENT-20260817-2850-a100h-scope-and-missing-legs.md` §4's inversion note, with §7
item 4 withdrawn there.

**(b) The attribution itself.** The crediting name *"Assistant"* has been used for **at least two distinct
live sessions**. `ListAgents` at the time of writing showed `Assistant [28640e]` and `A [84e2e8]` as separate
peers. **Lane A had to DECLINE a credit** to prevent a misattribution in the flattering direction
(`BEN-214`): it has no record of touching `bootstrap_nd.py`, `seedscan_split.py` or gate 1's leg structure.
**A misattribution toward a lane's own credit has no natural discoverer except the party declining it** — that
check has exactly one possible caller, and it fired. Recorded rather than silently corrected, because the
ambiguity is in the *name* and will recur.

## 5. Provenance of this row, which is load-bearing given its subject

**Filed in lane B's block `248`, not lane A's `390-399`, on lane A's three reasons:**

1. **A did not derive the gate-1 conclusion** and cannot confirm that *"Assistant"* refers to it.
2. **A cannot verify the relay** — the events happened in channels A had no access to. Every row in
   `390-399` was held to *"I measured this or I read the source."*
3. **Decisive:** if A filed it, the row's own provenance becomes *"a lane that was not party to the relay,
   filing about a derivation it may be confused with"* — **the defect the row describes, instantiated by the
   act of recording it.**

**`248` freeness derived tracked AND untracked immediately before taking it** —
`git grep -ohE 'BEN-24[7-9]'` → `247` only, and `grep -rhoE 'BEN-24[7-9]' --exclude-dir=.git .` → `247` only.
**Lane A derived the same freeness independently.**

**What lane A verified and what it did not, stated so no false completeness is inherited.** A read the tree
before reading this lane's document and confirmed both flags exist and route as described — a **third**
derivation of the premises. A **did not** verify *"gate 1 is therefore two modules rather than four legs"*,
which depends on what the four legs were, a document A has not read. **Premises thrice-derived; conclusion
not.** And per §4(a) the conclusion is now qualified anyway, so what stands thrice-derived is the
**capability** — precisely the half that turned out not to help.

**A's upgrade to my own citation, which is the reason its pass was worth running: HELP TEXT IS
DOCUMENTATION.** A help string describing seed routing is a claim about what the author *intended*; the
**behaviour** is two lines below it:

    bootstrap_nd.py:28   _data_base = a.fixed_data_seed if a.fixed_data_seed is not None else a.seed
    bootstrap_nd.py:29   _est_seed  = a.seed             if a.fixed_data_seed is not None else a.estimator_seed

`EXTENT` §3 already cites both (`:28`, `:29`, `:37`, and `:54` for the ML leg), so nothing rested on
documentation alone — **but the agreement between help text and implementation is a finding, not an
assumption**, and stating it explicitly is `BEN-391`'s instance 2 in miniature, where *"no committed DOCUMENT
records X"* was true and got read as settling a question about **code**.

## 6. The general statement, which is this row's most portable claim

**SHIP WHAT WOULD LET A READER FALSIFY THIS.**

The receipt-ingredients principle (`CONVENTION-receipt-ingredients.md`, `BEN-077`) has been useful in **four
registers in one day**:

| register | the thing shipped | where |
|---|---|---|
| operands of a **number** | the ingredients a derived figure is computed from | `BEN-077`, the original |
| scope of a **grade** | what the trace covered, and the **named falsifier** | `VL66`'s cause-5 declaration |
| units of a **ratio** | both sides' **unit and member count** | `BEN-152`'s 2026-08-17 extension |
| provenance of a **claim** | the **route** — who derived it, from what, independently or not | this row |

**So the rule was never about numbers.** Lane A's assessment, which is why this is promoted here rather than
left as a remark: *that is a better statement of `BEN-077` than `BEN-077` makes*, and `BEN-392`/`BEN-393` are
both instances of it without saying it. **This is lane B's claim with lane B's evidence; lane A has not
audited all four registers and did not second it.**

**Predicted next register, offered so it can be checked rather than assumed:** the provenance of a
**capability** — *"this can be done today"* needs the specification under which it would count, which is
exactly how §4(a) failed. Not yet an instance; recorded as a prediction.

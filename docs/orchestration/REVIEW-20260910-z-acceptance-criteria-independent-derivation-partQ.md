# PART Q — A-6(b): the two exclusion grounds point opposite ways, and §2.1a(ii)'s unit decides it

**Owner:** independent-assessment lane. **Code base:** `6f24fb00`. **No grade assigned.**
**Scope:** A-6(b) and §2.1a(ii) only. §3–§3.3 and §2.1's block population were routed to the
mathematical reviewer, correctly — see §Q.5.

---

## Q.1 — THE OPERAND QUESTION RESOLVES: THE LOGGED AND STORED QUANTITIES ARE THE SAME OBJECT

The coordinator's fingerprint compares a logged `sqrt-trace` against `sqrt(Σ_i h(i,i))` read from the
stored `TH2D`, and flagged as pending whether those are the same quantity. **Measured, they are.**

`combine_cov_nd.py`:

- `:20` computes `C=(Z.T@Z)/(Xr.shape[0]-1)` in memory, over the reported mask `rep = cv>0`.
- `:22` prints `sqrt-trace={np.sqrt(max(C.trace(),0)):.3e}` — i.e. `sqrt(Σ_i C[i,i])`.
- `:23-26` writes **that same `C`** via `hh.SetBinContent(i+1,j+1,float(C[i,j]))`.

So the stored diagonal *is* `C`'s diagonal, and `sqrt(Σ_i h(i,i))` equals the printed `sqrt-trace` up
to a `float64 → TH2D → float64` round trip. `TH2D` stores doubles, so that round trip is exact.

**Neither artifact can explain the reported gaps.** Formatting is `.3e` — four significant figures, so
at most ~0.03%; the reported gaps are **3.6%** and **4.6%**, more than a hundredfold larger. ROOT's
under/overflow bins are never set, so summing `1..n` or `0..n+1` gives the same value.

**But this closes the operand question, not the reader question, and the distinction is the whole of
their caveat.** Showing the two *quantities* coincide does not show the *reader* works: a wrong
histogram name, file, or axis would produce a mismatch indistinguishable from a real one. Their
stated weakness — no case where the fingerprint is known to **match**, so no demonstration that the
instrument can return `True` — **stands, and my analysis does not substitute for it.**

**A positive control is available in the same log line, and I am naming it rather than running it.**
The log carries a second quantity: `reported 10694 bins`. The stored `TH2D` is `n × n` with
`n = C.shape[0]` (`:23`), so reading back `n` and comparing to `10694` tests whether the reader is
opening the right object and reading the right axis — **without needing a known-matching trace.** If
`n` matches and the trace still does not, the mismatch is in the **values**, not the **addressing**,
which decomposes the instrument's two failure modes.

**I am not running it, deliberately.** Supplying a control and then assessing its result would spend
this lane's verdict on the fingerprint — Part E's trade, priced in advance for once. It should be the
reviewer's, who already holds the attack.

## Q.2 — THE TWO EXCLUSION GROUNDS POINT IN OPPOSITE DIRECTIONS, AND ONLY ONE OF THEM EXCLUDES

The relay gives two observations about `budget5d_55233707`: a **fingerprint mismatch**, and a
**job-level `TIMEOUT`**. **These are not two supports for one conclusion.**

- **The fingerprint excludes** — subject to §Q.1's reader question.
- **The `TIMEOUT` does not exclude, and on the step-level reading it positively supports the
  opposite.** The `--expected-ids` enforcement lives in `replica_manifest.load_replica_manifest:44-48`,
  called at `combine_cov_nd.py:18` — **before** the print at `:22` and the write at `:23-26`. So the
  log lines *"100 replicas … [wrote] uq_cov_stat_5d.root"* are themselves evidence that
  `load_replica_manifest` did **not** raise, that the declared id set was present in full, and that
  the product was written. **A job-level timeout that kills later stages cannot retroactively falsify
  a step that already completed and printed.**

**So the exclusion is singly supported, not doubly.** Presenting the `TIMEOUT` alongside the
fingerprint would make it look corroborated when the second observation is either neutral or
contrary. If the fingerprint falls to the reviewer's attack, **nothing else excludes this execution.**

## Q.3 — §2.1a(ii)'s CRITERION IS UNDERSPECIFIED AT THE WORD "SUCCESSFUL", AND THE UNIT DECIDES THE OUTCOME

§2.1a(ii) reads: *"a **SUCCESSFUL execution** of that command line is itself proof that exactly the
declared id set was present."*

Applied to the only candidate execution, the two available units give **opposite** answers:

| unit | verdict on `55233707` | basis |
|---|---|---|
| **job**-level success | **FAILS** — `sacct -X` State `TIMEOUT` | the scheduler's exit state |
| **step**-level success | **HOLDS** — both combines printed their counts and `[wrote]` lines | the enforcement runs at `:18`, before `:22`/`:23-26` |

The sentence names **neither**, and there is exactly one candidate execution, so the unit is not a
refinement — **it is the answer.** This is the launch-plan-versus-record shape (`OI-17`'s family)
arriving at the level of a single word: *"successful"* reads as a property of the run, and the
property the criterion actually needs is a property of **the step that performed the check**.

**What would settle it, named and not authored:** the criterion must say which exit state it means,
and for a step-level reading it must say what evidence counts — the log lines, a step exit code, or
`sacct -j <job>.<step>` rather than `sacct -X`. **I am not choosing**; `F9` already reserves the
adjacent "what does *verified* mean" question to Joseph, and this is the same question one level down.

## Q.4 — MY EQUAL-`N` FINDING IS STRONGER THAN WHEN FILED, AND JOSEPH'S DECLARATION ENTAILS `F1` RATHER THAN SATISFYING IT

**Equal-`N`.** Part I §I.3 said A-6 part (a) cannot substitute for part (b) because a count cannot
identify a population. The search result strengthens it: `N` for the **released bytes** is now
established by **no surviving execution record at all** — part (b) has not merely been skipped, its
only candidate evidence is under exclusion. **And the arm ambiguity closes** in the direction Part I
left open: the captured job is `budget5d`, the top-level unscoped globs, and the member-scoped
replicas post-date the products, so both candidates resolve to top-level. Part I §I.3's caveat that
content discriminates the *inputs* and not the *product* is unaffected.

**Joseph's declaration.** Its phrase *"the fixed scalar-5D central measurement and its **explicitly
named projections**"* is `F1` in his own words — but it **requires** the enumeration rather than
supplying it. The names must exist somewhere for the declaration to be true of anything, and `F1`
remains unmet until they do.

`F3` is **largely** met by *"not presented as calibrated confidence intervals, generator-exclusion
significances, or evidence of validated frequentist coverage"* — that disclaims significances and
coverage. It does not name `χ²`, `ndf`, `rcond` or retained rank, which `F3` also listed; those follow
from no χ² being quoted rather than from the declaration, so the entailment holds but is indirect.

## Q.5 — THE ROUTING AWAY FROM ME IS CORRECT AND I AM NOT CONTESTING IT

§3–§3.3 and §2.1's block population were sent to the mathematical reviewer rather than to me, on the
ground that §3.1's inertness paragraph contains my sentence and the three-block population is my
finding. **That is the principle this lane asked for, applied without being asked again, and it is
right.** A first reading is worth more than my confirmation on both.

I note one thing for whoever reads §3.1: the sentence of mine it contains is **withdrawn** (Part N),
so that paragraph needs both facts in one breath — it carries a strengthening of mine *and* that
strengthening is false as stated.

**Not assessed here:** the fingerprint's reader question (§Q.1), anything in §4.x, clause (d)/A-4,
§1/§1.1, §2.1a's equal-`N` content, and the `2`-vs-`4` residue deliberately left unresolved.

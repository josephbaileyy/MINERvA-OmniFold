# ASSESSMENT 2026-09-18 — the causes 1, 2 and 4 acceptance criteria

**Owner:** `z-independent-assessor` (`owners.tsv:15`). **Subject:**
`PACKET-20260918-causes-1-2-4-acceptance-criteria.md` at `230aecf77f7599123b67c6ae153c86f07a48f3ed`,
author `owners.tsv:14` `[91eaa2]`.

## CITABLE FOR / NOT CITABLE FOR

**CITABLE FOR:** the per-cause verdicts and findings `Z1`–`Z7`.

**NOT CITABLE FOR:** approval of any criterion — **approval is Joseph's act**; any grade; any
adoption. Nothing here unblocks `cause3_agg` or `δ_bin`, and nothing reopens `OI-126`.

## Evidence classes

**SOURCE only.** Every finding below is a committed blob read at `230aecf7`. **No payload read and no
compute for this assessment.** Where the packet relies on a relayed sweep I say so and do not
launder it.

---

# VERDICT

**The organizing claim holds for causes 1 and 4 and its WORDING FAILS for cause 2 — while cause 2's
conclusion survives, on better ground than the packet gives it.** Recommend approving §1 and §3 as
written; approve §2 with `Z3`'s correction made and `Z4`'s addition attached. Both routed items are
correctly routed, and one of them is worse than the packet says (`Z6`).

| cause | tolerance-free? | verdict |
|---|---|---|
| **1** | **YES**, and its clause says so in its own title | approve as written (`Z1`) |
| **2** | **NOT AS ARGUED.** The parameter exists and the code says it was **chosen** | approve the criterion, correct the wording, attach the margin (`Z3`, `Z4`) |
| **4** | **YES**, all four conditions binary | approve, with the mutation's **discriminator** specified (`Z5`) |

---

## `Z1` (SOURCE) — cause 1's tolerance-free claim HOLDS, verified against the clause not the paraphrase

`SPEC` §6.2 is titled, verbatim, *"`(cause 1, Z)` — measure-and-disclose closure, **irrespective of
magnitude**"* (`:3509`), and the adopted recommendation at `:3515-3520` is quoted correctly by the
packet. **So magnitude is excluded by the ruling itself, and the packet's inference — that adding a
tolerance would ADD a criterion the ruling removed — is sound.** The criterion that remains is a
four-part conjunction of completeness, disclosure, independent verification and four binary refusals.
**Nothing here can be blocked by the closed question.** Approve.

## `Z2` (SOURCE) — cause 4's tolerance-free claim HOLDS

`SPEC:1005-1019`, read directly: condition 2 *"its operands are the new build's own"*; condition 3
*"adding it **does not change the covariance content**"*; condition 4 *"the print is print-only, never
subtracted."* All binary. The five refusals at `:1237` are binary. **No magnitude appears anywhere**,
and the packet is right that a *"bound"* would presuppose a permitted change and weaken the
specification. Approve.

## `Z3` (SOURCE) — cause 2's WORDING IS REFUTED BY ITS OWN GOVERNING ARTIFACT, and the conclusion survives on different ground

The packet, §0 and §2.2: *"its floor multiple is **already fixed in code, not chosen**. There is no
free parameter to justify."*

**`uq_math.py:129-137` says the opposite, in its own capitals:**

> *"**THE THRESHOLD BELOW IS A CODIFICATION, NOT A REPO DECISION, AND IS FLAGGED AS SUCH.** The
> predeclared rule is qualitative (`~floor` vs `>> floor`) and **no number was ever recorded for
> it.** `2.0` is **chosen** … still recorded as **SET by this lane** rather than inherited: the
> predeclared rule never carried a value, so this is **a codification with an owner and a date, not a
> fact recovered from the record.**"*

**So a free parameter exists, it was chosen, and "fixed in code" describes where it lives rather than
whether it is justified.** That is the same conflation `θ` was closed for, and the packet's headline —
that cause 2 carries *"no number that could be contaminated by a favourable result"* — is not
supportable as written.

⚠ **But the conclusion survives, and the packet has a better argument available than the one it
made.** The same comment supplies `k`'s derivation, and it is **statistical, not formatting**:

> *"`2.0` is chosen so that a shift **AT the sampling floor** (`1.0x`, i.e. **consistent with being a
> finite-N fluctuation**) is unambiguously below it … **It is deliberately not tuned to sit just under
> `4.69x` — a threshold placed to make today's answer come out right is not a criterion.**"*

**That is a noise-versus-signal separation**, which is a legitimate basis for a binary branch, and it
is categorically different from `θ`'s defect — `θ` took a *resolution* figure and used it as an
*acceptance cap*. `k` is not a cap on acceptable movement; it separates "consistent with a finite-`N`
fluctuation" from "not". **And the comment carries its own anti-tuning disclaimer**, which is the
discipline three withdrawn cause-3 numbers lacked.

**So: refute the wording, endorse the criterion, and use this ground instead.** *"No new tolerance is
introduced; cause 2 inherits one, and the inherited one has a stated statistical derivation and an
owner"* is both true and strong. *"Not chosen"* is neither.

## `Z4` (SOURCE) — the L4 composition: NO overlap, but the MARGIN falls between them

The packet's split is correct and I confirm it: **cause 2 is the branch's VALUE on Z's own operands;
L4 is that outcome's STABILITY across the member set.** Different scopes, neither substituting.

**What falls between them is the margin to the branch point.** Suppose Z's ratio comes back at
`2.01` against `k = 2.0`. Then `f7_cv_centered_required` returns `True`, cause 2's (a)–(d) are all
satisfied, **and** L4 returns "identical across the member set" if every member lands above `2.0` —
so **both criteria PASS while the verdict is one perturbation from flipping.** Neither is sensitive to
how close it came.

§2.2(c) makes the margin **recoverable** — it requires the receipt to record the ratio, the floor and
`F7_FLOOR_MULTIPLE` — **but recoverable is not the same as gating**, and no criterion fires on a small
one. And by `Z3` the threshold is a chosen codification, so **a verdict at a small margin is a verdict
determined by the choice** — precisely the outcome the codification comment disclaims wanting.

⚠ **This is the same gap I recorded from the other side.** At `8df3b173` `C5` I required L4 to report
the margin, because as written it cannot distinguish *"tested and stable"* from *"no member came near
the branch point."* **The identical gap appears here from cause 2's side, found independently**, which
is a reason to treat it as a property of the composition rather than of either criterion.
**Requirement: the margin must qualify the verdict in both.** I name it; I do not set a value, and no
value is needed — it is a reporting requirement, not a tolerance.

## `Z5` (SOURCE) — cause 4's mutation is concrete in its TARGET and not in its DISCRIMINATOR

`SPEC:1010-1012` is the right standard and the packet quotes it correctly: the condition *"must be
enforced by a **guard that fails** … **not by a one-time comparison**"*, with *"a quantity in scope is
one edit from being subtracted."* And §4's falsifier — *"the guard **fails to fire** under a deliberate
mutation that routes `jit_trace` into the stored covariance"*, with *"a guard that has never been made
to fire is untested, not proven"* — names the target concretely enough to execute.

⚠ **What it does not specify is how the guard's refusal will be told apart from another mechanism's,
and this packet is unusually exposed to that because it specifies both.** §3.3 refusal 3 is *"covariance
content changes"*, enforced as *"a digest comparison on the stored object"*. **A mutation that routes
`jit_trace` into the stored covariance changes the stored object — so the digest comparison will also
react to it, possibly first.** A run that ends in a refusal therefore does not establish **which**
mechanism refused, and *"the guard fired"* would be unverified.

**That is the catalogued shape — a mutation refused before it reaches the guard it targets — and it
would reproduce exactly the defect  `SPEC:1010-1011` exists to prevent.** **Requirement: the mutation must
distinguish the guard's refusal from the digest check's** — by asserting on the guard's own message, or
by invoking the guard directly on the mutated input. **I name the requirement and not its
implementation.**

## `Z6` (SOURCE) — the guard-condition ambiguity is NOT a packet defect; it is a SPEC-INTERNAL CONTRADICTION

The packet flags it and routes it, which is right. **It is worse than the packet says.** Both texts are
`SPEC`'s own:

| | |
|---|---|
|  `SPEC:1010-1011` | *"**Condition 3** must be enforced by a guard that fails if the computed value ever reaches the stored covariance"* |
| `SPEC:1237`, row `(4, Z)` | *"§2.4's four conditions met, **condition 4** enforced by a **guard**"* |

The packet says *"the two conditions are near-identical in content, so nothing material turns on it."*
**True of the content; not true of the attribution.** An implementer cannot resolve a specification's
self-contradiction by picking, and a receipt that cites the wrong condition number is a receipt whose
row cannot be checked against its clause.

**On the merits, without deciding it:** `:1010` is the operative sentence that *defines* the guard,
while `:1237` is a receipt-row summary — and a summary is the likelier place for a loose reference. So
`:1010` is the more defensible reading. **But this is a specification defect and the disposition is the
spec owner's, not a reviewer's.** The packet's instinct to route rather than choose is correct; the
routing should say *"`SPEC` contradicts itself"* rather than *"the packet is ambiguous."*

## `Z7` (SOURCE) — the packet carries a superseded count in two places

§0 and residue 1 both say *"**twenty** note/primer/paper sources."* The routing lane has since measured
**24**, and has stated that the grep glob covered all 24 — so **the sweep's coverage was complete and
only its description was truncated**. That distinction matters and should travel with the correction:
a *description* defect leaves the conclusion standing, whereas a *coverage* defect would not. **The
packet's own text is what a reader will meet, and it still says twenty.**

⚠ **And I did not run that sweep.** It is the stated ground for §0's *"one claim, one map"*, it is
load-bearing for all three causes' populations, and the packet's own common falsifier names it. **It
is relayed in my record as it is in the packet's, and I do not launder it by repetition.**

---

## Recommendation

- **Approve §1 (cause 1) as written.** Its clause excludes magnitude by ruling.
- **Approve §3 (cause 4) as written, with `Z5`'s discriminator requirement attached** to the mutation.
- **Approve §2 (cause 2) with `Z3`'s wording corrected** — *"inherits a chosen parameter that has a
  stated statistical derivation"*, not *"not chosen"* — **and `Z4`'s margin requirement attached**,
  which also binds L4.
- **Both routed items stand as routed**, with `Z6`'s sharpening: the guard-condition ambiguity is a
  `SPEC` self-contradiction rather than a packet ambiguity.

**The packet's headline — that all three are approvable today on form, population and value — survives
for causes 1 and 4 and needs one qualification for cause 2.** That is still the first real unblocking
in this package, and I say so plainly.

## What this assessment does not do

- Approves nothing; approval is Joseph's. Grades no cell. Sets no value and needs none.
- Does not resolve the `SPEC:1010`/`:1237` contradiction, verify `OI-186/188`, or run the corpus sweep.
- Read no payload and ran no compute.

# DETERMINATION — the anchor's confound: **KEEP `k = 0`, DECLARE IT, and the disposition is CONDITIONAL ON THE VERDICT'S DIRECTION**

**By:** lane C (PET), as `(B)`'s owner, on B's `j = 0` result. **There is a fourth option and it is the one
ruled.** Nothing spent, nothing submitted, `seed_offset_policy.py` untouched.

---

## 0. First, a correction to the premise — **it was flagged, in the ruling B is reproducing**

The dispatch says the predicate *"returned a result you did not flag."* `RULING-20260818` §1c, verbatim:

> *"**`k = 0` is EXEMPT and must be: it is dirty on two of the three ranges, and that is a property of the
> PUBLISHED ARCHIVE, not of the scan.** The exemption is the honest shape — the anchor differs structurally
> from every other member, this cannot be fixed without abandoning the anchor, and **it is a limitation of
> `M(ii)` to declare rather than a defect to repair.**"

**Both coincidences, the same two reasons, and the same conclusion.** Recorded because a determination built on
*"C missed this"* would route the next reader to the wrong document.

**What B genuinely added, and both are real:** *(1)* the **implementation** question — whether `build_plan`
enforces the predicate and how the exemption is expressed — which my §1c left as prose and which is a decision
rather than a default; and *(2)* **the sharper framing**, *is a spread measured against a confounded anchor
attributable?*, which my §1c answered by fiat (*"declare rather than repair"*) **without giving a reason.**
**§2 supplies the reason, and it is a better one than the fiat.** B was right not to set it as a default.

## 1. THE FOURTH OPTION EXISTS BECAUSE **THE SECOND ONE DOES NOT** — *"anchor differently"* is not available

> **A CLEAN ANCHOR IS NOT AN ANCHOR.** The anchor's entire function is that it reproduces the published product
> **exactly**. The published product HAS the two coincidences — production ran `--estimator-seed 1000` while
> throw 0's draw RNG is `default_rng(1000 + 0)`, and replica 42 draws Poisson weights from seed 42 with its
> estimator at 42. **So a run that lacks the coincidences is not the archive, and a run that reproduces the
> archive has them.** The confound and the anchoring are the same fact.

**Option 2 therefore does not cost a member — it costs the ANCHOR.** It yields a 49-member scan with no tie to
any published value, and `M(ii)` asks a question *about a published value*. **That is the one thing the design
cannot give up**, and it is why `(ii)` beat `(i)` in the first place: `(i)` was refused partly because
`S = 42` is not the archive. **Dropping `j = 0` re-imports the defect that ruling rejected.**

**Option 3 — *"rule the confound immaterial"* — is refused as stated**, because immateriality is a magnitude
claim and the magnitude is unmeasured. **§3 gives what is available instead: a bound, and a direction.**

## 2. THE RULING — **the DIRECTION is known even though the magnitude is not, and the direction decides it**

**Contaminating one member of an ensemble inflates the expected sample variance.** With `x_0 → x_0 + δ`, `δ`
independent of the offset structure and of variance `σ_δ²`:

```
E[s^2]  =  sigma^2  +  sigma_d^2 * (1 - 1/n) / (n - 1)      >=  sigma^2
```

> **So the anchor confound biases the measured `f` UPWARD — toward `UNMET`, AGAINST the negligibility claim
> the bar exists to test.** And that settles the disposition, because it is the opposite of the other bias in
> this measurement: **`c4(n)` biases the sd DOWNWARD, toward PASS, which is why §6 of the ruling requires it be
> corrected rather than declared.**
>
> **THE ASYMMETRY IS THE RULE: a bias toward the CONSERVATIVE verdict is DECLARABLE; a bias toward PASS must be
> CORRECTED.** A declared conservative bias cannot manufacture the answer anyone wants; an uncorrected
> pass-ward bias can. **This is the same asymmetry as `INCONCLUSIVE → NOT MET` in the ruling's §5, applied to a
> nuisance term instead of to a bound.**

**RULED, and the conditional is the substance of it:**

| verdict | disposition | why |
|---|---|---|
| **MET** | **STANDS**, with the confound declared and §3's bound quoted | The confound pushes `f` UP. A verdict of *small* reached **despite** an upward bias cannot have been manufactured by it. |
| **UNMET** | **NOT DECLARABLE until §3's two-step check is run** | Here the confound points the same way as the verdict, so it is a live alternative explanation. |
| **INCONCLUSIVE** | same as UNMET | Under §5 it resolves to NOT MET, so it inherits UNMET's burden. |

**Cost of the conditional: ZERO in the MET branch, and §3's check is zero-new-compute in the other two.** That
strictly dominates option 2 (which pays unconditionally *and* destroys the anchor) and option 3 (which is
indefensible in exactly the branch where it matters).

## 3. THE MAGNITUDE — a bound now, and a two-step check on products that ALREADY EXIST

**Bound, from §2's formula.** Percentage inflation of the measured sd:

| `σ_δ / σ` | `n = 6` | `n = 20` | **`n = 50`** | `n = 100` |
|---|---|---|---|---|
| **1.00** *(pessimistic: anchor displaced by the FULL per-member scatter)* | **8.01 %** | 2.47 % | **1.00 %** | 0.50 % |
| 0.50 | 2.06 % | 0.62 % | 0.25 % | 0.12 % |
| 0.25 | 0.52 % | 0.16 % | 0.06 % | 0.03 % |

> **At `n = 50`, even the pessimistic case inflates the measured sd by `1.00 %` — twice `c4`'s `0.51 %`
> correction and in the safe direction.** *(And a fourth independent reason `n = 6` is the wrong grid: there the
> same confound is worth `8.01 %`, which would move a verdict on its own.)*

### 3a. ⚠ A CORRECTION TO MY OWN FIRST FRAMING OF THIS, CAUGHT BEFORE PUBLISHING — two different `σ`s

**My first draft closed the gap by pairing the bound above with an outlier test on the archive** (*is replica 42
unusual among the 100?*) and concluded *"the two arguments cover complementary regimes and leave no gap."*
**That was an asymmetric comparison — this lane's own most-repeated failure, and it nearly shipped inside a
document arguing about attributability:**

- the outlier test's `σ` is the **per-REPLICA scatter of one replica's contribution**;
- the inflation formula's `σ` is the **per-SCAN-MEMBER scatter of the block sum**.

**These differ by the LEVERAGE of one replica on the block sum — roughly `1/100` of `C_stat`'s share of a sum
that `C_syst` dominates.** Chaining them as if they were one quantity is the error, and the ratio is not a
detail: it is the whole conversion.

### 3b. So the check is TWO steps, and both are reads of existing products — **zero new compute**

1. **DISPLACEMENT, in replica units.** Rank replica 42's block contribution among the 100 in `boot_nd_5d`, and
   throw 0's among the 160 throw slabs. **Family-wise thresholds, so the test cannot fire on ordinary
   scatter:** flag at `|z| > 3.48` (100 draws, `α = 0.05`) / `|z| > 3.60` (160 draws). **The expected maximum
   `|z|` of `m` clean draws is `2.58` / `2.73`, which is the floor on what a one-member test can see** — stated
   because a test whose threshold sits below the clean maximum would flag something every time.
2. **LEVERAGE, converting step 1's units into scan-member units.** The sensitivity of the block sum to one
   replica and to one throw — `∂(block_sum)/∂(replica_i)`, computable from the same archived slabs.

**Only the PRODUCT of the two enters §3's table.** If step 1 finds replica 42 and throw 0 unremarkable, the
displacement is below the test's own resolution and step 2's leverage shrinks it further — **and the confound is
empirically immaterial for the price of reading files.** If step 1 flags either, we have learned the coincidence
matters, and that is worth knowing whatever the verdict.

**Both steps are cluster-side reads** (the products are on scratch — see §5), so they belong with `P-ANCHOR`
rather than being a second trip.

## 4. `build_plan` — **WIRE THE PREDICATE, and express the exemption as a COINCIDENCE ALLOWLIST, not as `j != 0`**

**Wire it.** B is right that wiring it un-exempted would make the driver refuse the ruled grid, and right not
to choose. **The choice is:**

> **The exemption names the TWO KNOWN COINCIDENCES — `(g1, bootstrap[1,100])` and `(g2, uthrow[1000,1159])`,
> each with where it was measured — and permits those two and nothing else. It does NOT skip member `0`.**

**The difference is the only thing that makes the guard worth wiring.** A `j != 0` skip passes *any* coincidence
at the anchor, including one introduced later by widening an array or adding a leg. **An allowlist of two
FAILS the moment a third appears** — and a third appearing is exactly the event nobody would otherwise notice,
because the anchor is the member everyone has already agreed is special.

> **This is *a filter needs a test in the direction it acts*: the exemption is a NARROWING, so it gets a test
> that it does NOT fire — a fixture with a third coincidence at `j = 0` that the predicate must still reject.**
> Without that test, widening the exemption later looks free.

## 5. B's implementation notes, and its sharpening — **accepted, one of them against my own text**

- **Range table with per-entry provenance, never a threshold: ADOPTED.** And the test that a caller-supplied
  range changes the answer is the right guard — it is what stops the table being decorative.
- **The PET-family band ABSENT AND NAMED AS ABSENT is the correct call and I withdraw any implication
  otherwise.** My ruling checked `[50000, 50049]` and said so; **B has not measured it, and an unmeasured range
  in a provenance-carrying table is worse than a named hole.** *(Consequence worth stating: `k = 2000`'s failure
  is therefore currently un-caught. It is not the ruled grid, so nothing is exposed — but a later lane widening
  the step needs the band measured first, and that is a task, not a caveat.)*
- **B's sharpening, accepted verbatim: *"the anchor is free" and "the anchor is clean" are different claims and
  only the first was established.*** Both appear in my ruling — freeness in §3, dirtiness in §1c — **separately,
  with neither leaning on the other**, so no argument of mine used the conflation. **But the distinction is
  worth being explicit and B is right that the `(ii)`-over-`(i)` cost argument rests on freeness alone**, which
  is all cost needs. **And per `P-ANCHOR`, freeness is not established either yet.**

## 6. `P-ANCHOR` — **unanswered, and the consequence of failure is worse than one member**

**B refuses to report it as a pass, correctly.** All six archived product paths are absent from the checkout and
untracked (scratch), and of the tracked receipt evidence only `receipt_construction_contract_5d.json` covers a
leg (`uq_5d/unified_throw_cov_5d.root`) — **`boot_nd_5d`, `seedscan_split_5d` and `universe_sweep` are named by
no tracked receipt. One leg of four.**

> **And the failure mode is not *"the anchor costs a member."* By §1, THERE IS NO CLEAN ANCHOR TO BUY.** If the
> archive's products cannot be read, the anchor must be **re-produced** — which reproduces its coincidences,
> because they are the archive's — **so a failed `P-ANCHOR` costs a member AND leaves the confound exactly where
> it was.** The conditional in §2 is unaffected; the pricing is not. **Every figure in the ruling's §3 moves up
> one member, as stated there.**

## 7. Ceiling versus allocation — **they bind on DIFFERENT AXES, both readings are true, and neither supersedes**

| `n` | GPU node-h | % of remaining GPU | CPU node-h | % of remaining CPU |
|---|---|---|---|---|
| 6 | 49.1 | 0.08 % | 108.1 | 2.70 % |
| 20 | 186.4 | 0.29 % | 410.8 | 10.25 % |
| **50** | **480.7** | **0.75 %** | **1,059.4** | **26.42 %** |

*(B's fresh figures: 9.81 GPU node-h and 21.62 CPU node-h per member; 64,119.5 GPU and 4,009.1 CPU node-hours
remaining.)*

> **Joseph's CEILING binds on GPU** — `200 / 39.223` → 6 members — **and the REMAINING ALLOCATION binds on
> CPU**, where `n = 50` is `26.4 %` against `0.75 %` on GPU. **A ceiling and an allocation are different
> objects.** My ruling's §3 framed GPU as binding because **that is the axis Joseph's number is denominated in
> and he is the one deciding**; B's framing is the right one for what the campaign can absorb. **Both belong in
> what goes to him: he is approving a ceiling, and the thing being consumed is CPU.**

## 8. Scope

- **RULED: `k = 0` stays in the grid; the confound is DECLARED; the disposition is CONDITIONAL on the verdict's
  direction** (§2). MET stands; UNMET/INCONCLUSIVE requires §3b first.
- **RULED: `build_plan` wires the predicate with a two-entry coincidence ALLOWLIST**, plus the narrowing test
  that it does not fire (§4). **B implements — its module.**
- **REFUSED: option 2** (no clean anchor exists) **and option 3 as stated** (immateriality is a magnitude claim;
  §3 gives a bound and a direction instead).
- **CORRECTED, mine, before publishing: §3a's two `σ`s.** The outlier test and the inflation bound are in
  different units and the leverage between them is the whole conversion.
- **NOT RULED: `P-ANCHOR`.** A cluster-side read, B's to report, and §6 states what a failure costs.
- **AUTHORIZED: nothing.** §3b is a read of existing products and needs no grant; everything else is still
  Joseph's.

*Second sought: B on §4's allowlist and on whether §3b's two steps are readable from the archived slabs as they
stand; A on §2's direction argument, which is the load-bearing claim here and is one line of algebra that either
holds or does not.*

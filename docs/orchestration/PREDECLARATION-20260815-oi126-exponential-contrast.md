# PREDECLARATION — the `OI-126` (a)/(b) contrast: variance-matched, zero-free perturbation

> # RETIRED 2026-08-15 — consensus 4-0 at `410af7a`. THIS EXPERIMENT WILL NOT RUN.
>
> **Reason, in one line: `Poisson(1)` is the sampling distribution, not a proxy — so the contrast could
> not have undermined the object it tested.** Independent `Poisson(1)` row multiplicities reproduce the
> *exact* sampling distribution of every aggregate; `Exponential(1)` matches only the first two moments
> and is wrong precisely in the atom at zero. §7 of this document argued the opposite and was wrong.
> Consequence: **both outcomes support `C_stat`'s validity**, so no result could have been actionable.
>
> **THE BODY IS LEFT INTACT DELIBERATELY.** §5b, §7 and the superseded half-width rows are the
> reasoning trail, and they are the evidence that the design was genuinely open when it was written —
> the same principle this document applies to §4. **A retired predeclaration is a record; a removed one
> is a gap.** Nothing below is in force. Do not resurrect it: see
> `PROPOSAL-20260815-oi126-fixed-network-propagation.md`, which keeps the correct noise model and
> removes the confound structurally instead.
>
> Retired by its own author. The pattern that produced §7's error is `BEN-315`.

**STATUS: RETIRED (see above). NEVER IN FORCE. NO CODE WAS WRITTEN, NOTHING WAS SUBMITTED.**
**Landed as a DRAFT so it can be reviewed as a document** — lane B could review only a relay of its
arithmetic while it existed solely in a working tree, and correctly marked every claim about the text
as UNVERIFIABLE. Landing it unsigned fixes that; it does not advance it.
Authored by the executor (`Assistant`) lane 2026-08-15. To be co-signed by the mediator
(`personal-orchestrator`) and landed **before** any code exists. Spend authorized by Joseph at
`ae70c3f` (*"Yes I authorize both"*).

**CONDITIONAL ON A RULING THIS DOCUMENT DOES NOT SUBSTITUTE FOR.** Lane C (PET), author of the
`C_stat` spec, has not ruled on whether a reduced-n diagnostic is coherent under the contract.
Joseph authorized the *spend*, not a spec interpretation. **If lane C rules it incoherent, this stops
regardless of cost or co-signature.**

---

## 1. The question, and why it is not already answered

Poisson(1) resampling of the **measured** leg moves the band fit by a factor of ~5 in
`p_par 6-20 GeV`. Two readings with opposite publication consequences:

- **(a)** the estimator is genuinely that unstable there → `C_stat`'s band entries are right and the
  published uncertainties are enormous.
- **(b)** a Poisson bootstrap of the measured leg is not a valid statistical-uncertainty proxy for
  this estimator → `C_stat` needs a different construction; `OI-121`/`OI-122` reopen.

**The contrast.** `Poisson(1)` and `Exponential(1)` **both have mean 1 and variance 1**. They differ
in exactly one property: `P(X = 0)` is `e^-1 = 0.36787944117144233` versus **`0`**. So an
`Exponential(1)` arm holds the injected variance fixed and removes the zero atom.

- band statistic **stays high** → the response is *variance*-driven → **(a)**
- band statistic **collapses** → the response is *zero-support*-driven → **(b)**

## 2. The decision statistic, fixed here so it cannot be chosen later

**Per replica: the MEDIAN over the 84 band cells of `R_push`, in `p_par 6-20 GeV`.**
**Per arm: the mean of those per-replica medians, with a two-sided 95% Student-t interval.**

This is *deliberately* the same object B measured (`probe-oi126-band-Rpush-sigma-20260815.json`,
`per_replica_band_R_push_MEDIAN_over_cells`), because the sizing below uses that array's `sd`. **A
mean-over-cells statistic would have a different spread and would invalidate the sizing.** Any
substitution of the statistic voids this predeclaration.

## 3. The boundary — numeric, two-sided, and applied IN CODE

```
arm mean of per-replica band medians, 95% t-interval entirely ABOVE  2.3042  ->  (a)
arm mean of per-replica band medians, 95% t-interval entirely BELOW  2.3042  ->  (b)
interval CONTAINS 2.3042                                                    ->  UNRESOLVED
```

`2.3042` is the midpoint of the measured (a) truth `3.59690668865833` and the **measured** (b) null
`1.0114` (the control region's median `R_push`; see §5a, which supersedes the earlier assumed `1.0`). The threshold is written as a constant in the evaluation script **before** the arm is run, and
the verdict is emitted by that code, not by a reader.

> **THE `4.0` BOUNDARY IS RETIRED, and the reason is recorded so it cannot be reinstated.** It sat
> `0.403` from the measured (a) truth — **under a quarter of one sigma** — so the Poisson arm itself
> crosses it on a large fraction of draws. It was proposed when the (a) hypothesis was anchored on
> `replica_00`'s `5.0467`, which B has since measured to be a **high draw**: `z = +0.90`, with 35 of
> 50 replicas below it.

## 4. `UNRESOLVED` is a real outcome and does NOT default to (a)

An `UNRESOLVED` verdict is reported as `UNRESOLVED`, feeds Track B (publish with the fork stated),
and **does not license the (a) reading.** Specifically prohibited after the fact: re-centring the
boundary, widening the intervals, dropping draws, switching the statistic, or reporting a one-sided
interval. **The failure mode this clause exists to prevent is a partial collapse read favourably.**

## 5. Sizing — **the n = 9 derivation is WITHDRAWN. It was a 50%-power condition.**

**The defect, found by lane B inside a narrow scope the mediator set, and reproduced independently
here.** The earlier criterion `t*s/sqrt(n) < d` was evaluated by substituting the *true* sd for the
*realized* one. That is approximately a **median-behaviour** condition — it asks whether the interval
is short enough *on average* — not a power calculation. At n=9 the sample sd carries ~25% relative
uncertainty, so a realized `s` one sigma high overruns the boundary by itself.

Correct calculation: the event "95% t-interval entirely on one side of the boundary" is a non-central
t test, power `P(T'(df=n-1, nc=sqrt(n)*d/sd) > t_0.975,n-1)`. Reproduced here to three digits against
B's table:

```
 n     power if (a) is exactly true     both-arms cost
 6     0.361                              39.1 GPU-h
 9     0.566                              58.6 GPU-h   <- the withdrawn sizing: a coin flip
15     0.828                              97.6 GPU-h
19     0.914                             123.7 GPU-h
25     0.972                             162.8 GPU-h
```

**ADOPTED: n = 15 per arm, `97.6` GPU-h both arms, power `0.824` at the measured boundary** — the
§5a condition has been discharged and the sizing is now unconditional.

Marginal reasoning, stated so it can be checked: `9 -> 15` buys **+26** points of power for 39 GPU-h;
`15 -> 19` buys **+8.6** for a further 26. The curve turns at 15. `n = 9` is rejected outright — with
no cost ceiling, spending 59 GPU-h for a coin flip is the worst of the options, because it most likely
returns exactly what Track B yields for free.

### 5a. RESOLVED 2026-08-15: the (b) null is NOT an assumption. **My own §5a premise was malformed.**

I asked for a free measurement of "the nominal's band statistic" to replace the assumed `1.0`. **That
request was ill-formed and I withdraw it.** Reading B's probe rather than reasoning about it
(`probe-oi126-band-Rpush-sigma-20260815.py:75`):

```python
r = T_n[bc] / T_k[bc]        # NOMINAL / REPLICA, per band cell; then median over cells
```

**`R_push` is the ratio of the nominal to the replica.** So a replica that reproduces the nominal
gives **exactly `1.0`** — the (b) null is the **definitional fixed point of the statistic**, not an
assumed value. There is nothing to measure: the nominal against itself is `1` by construction.

What *is* a genuine open quantity is how far the Exponential arm's own **legitimate** variance
response moves it off unity — `Exponential(1)` still injects variance `1`, so under (b) the arm lands
*near* `1`, not *at* it. Best available anchors, all measured:

```
(b) null anchor                              value    boundary   distance   power n=15
definitional fixed point                     1.0000   2.2985     1.2985     0.828
control-region median R_push (replica_00)     1.0114   2.3042     1.2928     0.824
band family MINIMUM over all 50 replicas      1.0859   2.3414     1.2555     0.802
```

**ADOPTED (b) null: `1.0114`** — the control region's measured median `R_push` (`p_par < 6`, 128
cells), i.e. the empirical value of "the estimator responds to measured-leg resampling *benignly*",
which is exactly what (b) predicts for the band. It is preferred to the definitional `1.0` because it
is measured rather than idealised, and to the family minimum because that is an extremum rather than a
central value.

**BOUNDARY: `2.3042`. DISTANCE: `1.2928`.**

**Consequence for the sizing: the boundary moves `0.0057` and power at n=15 changes by `0.0033`.**
Even the pessimistic family-minimum anchor gives `0.802`. **So the conditional in this lane's vote —
"switch to n=19 if the re-derived distance falls below ~1.25" — CANNOT TRIGGER**, and the vote resolves
to **unconditional n = 15**. The `1.30` case that would have forced n≥23 is not reachable from any
measured anchor.

**Recorded because it is the useful part:** the earlier claim that "the (a) hypothesis was anchored on
a high draw; the (b) hypothesis is anchored on nothing" was **half wrong**. The (a) half was right and
B corrected it. The (b) half was wrong — (b) was anchored on the definition all along, and I did not
see it because I reasoned about the statistic instead of reading the four lines that compute it.

### 5b. Which branch the money actually buys, stated because it bears on "best option"

The two branches are **not symmetric in consequence**. If **(a)** is confirmed, the action is
"publish with the large uncertainties as they stand" — which is what **Track B does for free**. If
**(b)** is found, `C_stat` needs reconstruction and `OI-121`/`OI-122` reopen — a materially different
action. **So the decision-relevant outcome is (b), and the expensive upper half of the power curve
buys confirmation of the branch that changes nothing.**

That is *not* an argument for not running. The run tests whether a **published statistical
uncertainty is valid**, and publishing an invalid `C_stat` is a real error rather than a change of
plan. It is an argument against paying for `n = 25+` to tighten the (a) side.

### 5c. A second channel, free, and it does NOT reduce n

Under **(b)**, removing the alleged cause should also *stabilise* the estimator, so the arm's **sd**
should fall as well as its mean. An F test of `s_b^2/s_a^2` against the 50-replica reference (df 49)
gives, at `sd_b/sd_a = 0.5`: power `0.746` at n=9, `0.931` at n=15. Under **(a)** it correctly does
not fire (`0.050`, nominal).

**It is therefore a second route to detecting (b) and adds nothing to confirming (a), so it does not
reduce the required n.** Recorded as **co-secondary**: reported always, never substituted for §3's
verdict, and `sd_b` is a first-class output because it is the assumption the whole sizing rests on.

## 6. The two anchoring caveats, stated not buried

**(i) The sizing borrows the untested arm's spread, and `n ∝ sd²`.** The n-values below are from the
WITHDRAWN half-width criterion and are retained only to show the scaling; the governing numbers are
the power table in §5. Declared response, fixed now:

```
sd_exp = 1.6091 (assumed)  ->  n >=  9
sd_exp = 2.0               ->  n >= 12
sd_exp = 2.5               ->  n >= 17
sd_exp = 3.0               ->  n >= 23
```

**If the Exponential arm's own measured `sd` exceeds `1.6091` such that `n = 9` no longer satisfies
the half-width requirement, the verdict is `UNRESOLVED — UNDERPOWERED`, computed by the same code
from the arm's own `sd`.** It is *not* rescued by re-deriving a boundary, and any extension to larger
n is a new authorization with a new predeclaration.

**(ii) The boundary is the midpoint of one MEASURED mean and one ASSUMED null.** `3.5969` is measured
over 50 replicas. `1.0` is the *assumed* value under (b) — **nobody has measured the Exponential
arm.** The (a) hypothesis was anchored on a high draw; **the (b) hypothesis is anchored on nothing.**
Consequence, computed in advance:

```
(b) truly at 1.0  ->  boundary 2.2985, distance 1.2984  ->  n >=  9   [SUPERSEDED by 5a: the
                     null is measured at 1.0114, boundary 2.3042; these rows are the withdrawn
                     half-width criterion and are kept only to show the sd/null scaling]
(b) truly at 1.5  ->  boundary 2.5485, distance 1.0485  ->  n >= 12
(b) truly at 2.0  ->  boundary 2.7985, distance 0.7985  ->  n >= 19
```

**So if the Exponential arm lands near `2.0`, this run is underpowered by more than a factor of two
and its correct output is `UNRESOLVED`.** Recorded here so that outcome cannot later be presented as
a weak (a).

**(iii) The band's spread is p_par-column-structured and the aggregate hides it.** B's
`sd_by_column` = `[1.0847, 3.0524, 3.7154, 3.5151, 1.9001, 0.3342]` — an **11x range** in absolute
sd across the band's columns (rel_sd `0.302`–`0.565`). **The band-aggregate statistic in §2 is the
predeclared decision object; no per-column verdict is authorized by this document**, because a
per-column decision in the high-sd columns would need several times `n = 9`.

## 7. The continuous-null assumption, with its counterargument beside it

**Assumed:** a variance-matched *continuous* perturbation is the right null for "genuine statistical
response," so that a collapse under `Exponential(1)` isolates the zero atom as the cause.

**Counterargument, which is not settled:** real measured fluctuations are integer-valued, and a bin
genuinely observing zero events is physical. On that view `Exponential(1)` is the wrong null and a
collapse would be an artifact of the *replacement*, not evidence about Poisson.

**Our position, and it is an argument rather than a result:** the object being replaced is a
**per-row** weight over 49,152,885 signal rows, and `36.8%` of *rows* carrying zero weight is not the
same object as a *bin* observing zero counts. **This is recorded as contested. A reader who rejects
it should read the outcome as bounding the zero atom's role under a continuous null, not as settling
(a) versus (b).**

## 8. What the diagnostic arm is NOT

- **No family membership.** It claims none, and must not be keyed as a `C_stat` member.
- **Nothing quotable is constructed.** No `C_ML`, no central move, no subset selection.
- All products carry the `NONQUOTABLE-DIAGNOSTIC.` prefix.
- **The reconciler is not invoked**, and this document does not assert it would pass.

## 9. Self-description: the override's identity goes in the receipt

Applying the `lr_proof` lesson **in advance**. Every product records:

- `perturbation_distribution`: `"exponential(1.0)"`, and the mean/variance identity to `Poisson(1)`
- `perturbation_module_sha256`: digest of the module that drew it
- `realized_data_factor_sha256`: hash of the **realized float array**, uncast
- `data_factor_dtype`: the actual dtype, asserted `float64`
- `predeclaration_sha256`: digest of *this file as landed*

**Why:** `data_factor_sha256` is written on both the build side and the extract side, where the
extractor re-draws and re-hashes — a two-sided replay check. **An override installed on both sides
makes that check self-consistent and therefore vacuous as evidence about which draw was used.** These
five fields are what make the arm self-describing in its place.

## 10. Build order, and a scope correction I owe

1. **Re-issue the dataloader binding** — record the move. Per the `verify_hash_bindings.py`
   convention a **rebuild is not required**: the existing receipts record what ran and that stays
   true; rewriting their hashes would falsify history.
2. **Widen the diagnostic namespace — in THREE files, not one.**
   `build_fullevent_replica_target.py:150`, `train_fullevent_replica.py:320`,
   `extract_fullevent_replica.py:443`. **I previously reported one file. That was wrong**, and it was
   wrong because my `grep` was truncated by `head -8` — the matches in the other two drivers sat
   below the cut. The mediator's correction to two was closer; the measured answer is three.
3. **Inject at the real seam inside `fullevent_fps_dataloader.py`** — not a monkeypatch, for the
   reason in §9. `build_fullevent_loaders` has no `data_factor` parameter, so the seam must be added
   as an explicit optional argument with `Poisson` as the default, leaving every existing caller
   bit-identical.

**Leg F is terminal and there is nothing to sequence around** — `56863958` tasks all `COMPLETED`,
last ending `2026-08-14T09:02:08`. **My earlier "wait for Leg F" recommendation was built on
`LIVE-STATE.md:29` rendering `UNKNOWN=4` as `ACTIVE`, and I should have checked `sacct` before
recommending a schedule around it.**

## 11. Failure modes declared uninformative in advance

1. **The Poisson control arm fails to reproduce `3.5969 ± ` its own interval** → the harness is
   wrong; the Exponential arm is **not read**, whatever it printed.
2. **`n = 9` inadequate against the arm's own measured `sd`** → `UNRESOLVED — UNDERPOWERED` (§6i).
3. **Interval contains the §3 boundary `2.3042`** → `UNRESOLVED`, feeds Track B (§4).
4. **Any task exiting other than 0** → not a result.
5. **The realized `data_factor` is not `float64`, or contains an exact zero** → the arm did not test
   what it claims; fail closed.

---

**Signatures required before any code is written:**

- [ ] `Assistant` (executor) — author
- [ ] `personal-orchestrator` (mediator) — co-signature
- [ ] Lane C (PET) — ruling that a reduced-n diagnostic is coherent under the `C_stat` contract
- [ ] Joseph — confirmation at **~59 GPU-h**, since the derived `n = 9` exceeds the size the
      authorization was discussed against

# RULING — `R` MUST VARY. Option **(i) is refused**, and the reason is a ruling already on this record

**By:** lane C (PET), owner of `SPEC-20260814-gate5-cstat-construction-v1.md` and the product ruling this
follows. **Second blocking item for the data-only ensemble.** E found the sixth site, **stopped before
writing a line, and sent the number rather than absorbing it.** Nothing was run; every leg below read from
the tree this turn.

---

## 0. RULING: `R` MUST VARY with the data draw. **(i) REFUSED on the merits. (ii) ADOPTED — it exists, is
costed, and its two traps RESOLVE rather than trade (§3b). (iii) stays blocked.**

**And the argument is not a preference of mine — it is consistency with a ruling I made this afternoon.**

## 1. The mechanism is worse than "one omitted term". `normalize=True` makes `R` the ONLY route

`:1552`:

```
data = DataLoader(reco=meas_cloud_all, weight=w_refined.astype(np.float32), normalize=True,
                  normalization_factor=STEP1_MC_NORMALIZATION * R, reco_evt=event_meas_all)
```

**And the vendored `normalize` DIVIDES OUT whatever the weights summed to.**
`omnifold_nn/omnifold/dataloader.py:149-153`:

```
_src = self.weight if self.weight_reco is None else self.weight_reco
sumw = np.sum(_src[_pr])
_c = (normalization_factor/sumw).astype(np.float32)
self.weight *= _c
```

**So the measured block's total weight after normalization is EXACTLY `1e6 · R`, whatever `w_refined`
summed to.** The precomputed refined target *does* carry the data draw (`build_negweight_refined_target`
takes `data_factor`) — **and that fluctuation is then exactly cancelled by the renormalization.**

> **Therefore `R` is not one contribution among several. With `normalize=True`, `R` is the ONLY route by
> which the data-count fluctuation reaches the measured normalization.** Freeze `R` and the measured leg's
> total weight becomes **identical across all fifty replicas** — the rate term is removed by exact
> cancellation, not merely reduced.

**So the mediator's conclusion is right and stronger than the argument given for it.** It is not that
`σ_stat^data` would be *biased low*. It is that it would be **a different quantity.**

## 2. Why that is decided by a ruling already on the record, not by a fresh judgement

A cross-section `σ_stat` is dominated by the **rate** fluctuation of the data sample. A data-only `C_stat`
whose measured normalization is frozen across replicas measures **shape statistical fluctuation only.**

**This campaign already has a name for that failure, and I ruled on it this afternoon.** `VL130` is
**shape-only** because `central_vector` sums to 1 by construction; `BEN-400` disqualified a published ratio
for pairing a shape-constrained spread against an absolute one, on the ground that a `rel_sd` of a different
quantity is not comparable however carefully the statistic is matched.

> **Option (i) would reproduce that exact defect inside the published `σ_stat`** — a shape-only statistical
> uncertainty presented under a name the field reads as total-rate statistical uncertainty. **And unlike this
> afternoon's ratio, this one is quoted to other experiments.**

**And it defeats the authorization's own justification.** Joseph authorized 151 A100-h **for external
comparability**. A frozen-normalization `σ_stat` is not comparable to MINERvA's own, T2K's, MicroBooNE's or
NOvA's — it is systematically smaller by the term those all include. **The mediator's point that a reader
comparing against T2K will not read our predeclaration is exactly right: documenting a bias is not
correcting it.**

**So (i) is refused on the merits and not merely deprioritised.** Its positive assertion that `R` equals the
nominal `R` is still *required* — but as a **falsifier for the three-stream product's own receipts**, not as
a licence for this one.

## 3. What I found while ruling, and it improves (ii)'s prospects — WITHOUT prescribing a route

**The loader's single switch is at the DRAW site, not at the APPLICATION sites, and the application sites
are already per-stream.** `:1545-1549`:

```
R, r_telem = step1_class_ratio_from_dump(
    d, pot_scale=pot_scale, n_data=M, w_truth_full=..., w_reco_full=..., w_bkg_full=...,
    data_factor=data_factor, bkg_factor=bkg_factor,
    sig_factor=(sig_factor if bootstrap_seed is not None else None))
```

**`R`'s computation ALREADY takes three independent factor arguments, and `sig_factor` ALREADY has its own
conditional.** So *"data factor applied, signal factor not"* is **not** unreachable in the normalization
path — it is exactly the shape that path is written in. **What is single-switched is the DRAW at `:1321`,
inside the same branch that performs the `w_truth *= sig_factor` multiply.**

> **So E's structural claim is right about `bootstrap_seed` and should not be generalised to
> "unreachable".** The plumbing downstream of the draw is already per-stream; the coupling is one branch.

**AND I AM NOT PRESCRIBING THE ROUTE.** I did that once on this item — condition (i) of the second-product
ruling, *"put the override in the driver"* — and it was **silently wrong** because I read a mention as an
operation (`BEN-403(ii)`). **E establishes whether (ii) exists by attempting it, and the finding above is
input to that, not an answer.**

## 3b. **(ii) EXISTS AND IS COSTED — so §4 below is moot, and the two traps resolve rather than trade**

E looked before claiming, and the route is driver-side editing nothing pinned. **Trap 1 is real and it does
NOT collide with `P5`. Here is why, and the resolution is a specification rather than a trade-off.**

### Trap 1 — which arrays must be bit-exact, ruled explicitly so the next lane finds no conflict

**`P5`'s domain is the MC leg; (ii)'s non-bit-exactness is on the MEASURED leg. They are disjoint arrays.**
`P5` compares `w_truth`/`w_reco` against `w_truth_full[imc]`/`w_reco_full[imc]`; the rescale acts on the
measured `DataLoader`'s `weight` (`w_refined`). **There is no array that both requirements touch.**

> **THE RULE, and it is general: assert BIT-EXACTNESS where the claim is that NOTHING HAPPENED, and assert a
> TOLERANCED CLOSURE where the claim is that a specific COMPUTATION happened.** An absence has no rounding,
> so bit-exactness is the natural and complete predicate for it. An arithmetic result does have rounding, so
> bit-exactness there is not a stronger check — **it is a check of the implementation path rather than of the
> claim**, and it fails for reasons with no physics content.

**Specified, so it cannot be read two ways:**

| array | predicate | why |
|---|---|---|
| `w_truth`, `w_reco` | **BIT-EXACT** to `w_truth_full[imc]`, `w_reco_full[imc]` (`P5`) | the claim is *no draw was applied* — an absence |
| measured `weight` after the rescale | **TOLERANCED CLOSURE**: `sum(weight[pass_reco])` vs `1e6 · R_dataonly`, tolerance declared, `≤ 4·float32 eps` relative | the claim is *this computation happened* |
| measured `weight` vs any one-shot canonical construction | **NO REQUIREMENT — explicitly WAIVED here** | one-shot is not reachable driver-side, and identity to an unreachable construction is not a property of the product |

**And the physical size, stated so nobody re-litigates it from the word "non-bit-exact":** two sequential
`float32` rescales differ from one by `≲ 2·eps = 2.38e-7` relative, **common-mode within a replica** (a
single scalar). Against a family total spread of `5.167%` that is **`2.3e-6` of the quantity being
measured** — negligible by six orders, and it perturbs a common scale rather than adding structure to the
covariance.

**The mediator's *"bit-exactness is the property your whole verification scheme rests on"* is right about the
scheme and wrong about this array.** The scheme rests on bit-exactness where it is asserting an identity;
here it would be asserting a construction path.

### Trap 2 — both `R` values stamped, and the loader's own stamp is NOT rewritten

The loader stamps `meta["target"]["step1_class_ratio"] = R` at `:1554-1558`, computed **before** any
driver-side rescale. **Left alone the receipt asserts a number the weights no longer embody — the
receipt-vs-reality class, `Route A`'s defect at a different site.**

> **`P7` (train): the data-only block must carry ALL THREE of `step1_class_ratio_loader_stamped`
> (`= R_nominal`), `step1_class_ratio_applied` (`= R_dataonly`), and an explicit
> `weights_embody = "step1_class_ratio_applied"`. Absence of any one raises.**
>
> **`P8` (train): the loader's `meta["target"]["step1_class_ratio"]` must be left EXACTLY as the loader wrote
> it.** Overwriting it would make a loader-stamped field assert something the loader did not do — the same
> prohibition as rewriting a submit-time hash (`BEN-406` §3). **The correction is ADDITIVE, never in place.**

This is `CONVENTION-receipt-ingredients.md` / `BEN-077`: ship both operands so the numbers *can* contradict
each other. A receipt carrying one `R` is unfalsifiable about which one the weights embody.

### The aliasing is respected, not tripped over

`:152-156`'s comment — *"`self.weight` is a view of the caller's array, and callers rely on seeing the
rescale"* — makes a driver-side in-place rescale **consistent with the design rather than a violation of
it.** The live constraint is ordering: **anything that reads the measured weights before the rescale sees
pre-rescale numbers**, so `P7`'s closure check must run **after**, and no hash of the measured weights may be
taken before.

## 4. If (ii) had not existed, this would have been JOSEPH'S decision — recorded because the reasoning still binds

**Say it plainly rather than letting it emerge as a slip:** if no unpinned route supplies a varying data
factor to `R`, then the only remaining option is **(iii)**, an edit to a file pinned 25 ways, which
`OI-60`/`BEN-384` block.

> **In that case `C_stat^data` is NOT BUILDABLE UNDER THE CURRENT PIN REGIME, and the choice — spend a
> Gate-2-class re-attestation, or not have the product — is a scope decision for Joseph.** It is not
> available to me, not to E, and **not to a two-session quorum**, because it trades a publication deliverable
> against a code gate rather than deciding a fact.
>
> **What must NOT happen is (i) becoming the answer by default because (ii) is hard and (iii) is blocked.**
> That is the shape this ruling exists to prevent.

## 5. Two things taken from the dispatch

**(a) `P5` guards a hazard I did not know about, and that raises its status rather than confirming it.**
`omnifold_nn/omnifold/dataloader.py:101-107` carries its own **unseeded** `np.random.poisson(1, ...)` on
`self.weight` behind a `bootstrap` flag — dormant, default `False`, never passed by
`build_fullevent_loaders`, **and one keyword from silently thinning MC with a draw no receipt could hash
against a canonical form.** `P5` compares `w_truth` to `w_truth_full[imc]` **bit-exactly**, so it catches
that for free. **A predicate that catches an unenumerated hazard is evidence the predicate is at the right
level of abstraction** — and it is why `P5` is mandatory at train rather than advisory.

**(b) `n_data_effective` is load-bearing in both directions, and that is worth recording.** It was the field
E narrowed `OI-90` to this morning — *"data-factor APPLICATION evidenced by `n_data_effective`, NOT by array
identity"* — i.e. the evidence the factor **was** applied. **At `:945-951` it is the mechanism by which the
factor silently would **not** be: `data_factor is None → n_data_eff = float(n_data_rows)`, the raw row
count, no error.** **The same field that evidences application is the field that fabricates it on absence** —
which is `BEN-405`'s class (`ABSENT` silently becoming a legal value) in the quantity a σ_stat depends on.

## 6. Disposition

- **`R` must vary. (i) refused on the merits.** Its positive assertion is retained as a falsifier for the
  three-stream receipts, not as a licence here.
- **(ii) ADOPTED.** It exists, E costed it at **~20 min on top of ~2.5 h**, and it edits nothing pinned.
- **`P7` and `P8` are added** to the six predicates of
  `RULING-20260817-lanec-data-only-coherence-predicate.md`, bringing the required negative controls from
  **11 to 13** (`P7`, `P8` at train only).
- **The bit-exactness split of §3b is normative**: MC leg bit-exact, measured leg toleranced closure,
  identity-to-one-shot explicitly waived. **A future lane finding these two requirements together must not
  pick one — they apply to disjoint arrays.**
- **(iii) remains blocked** by `OI-60`/`BEN-384`, and §4 stands as the recorded reasoning for the branch that
  did not fire.
- **E's ~2.5 h + ~20 min is the number**, and it starts now.
- **Nothing built, nothing submitted. 151 A100-h authorized and unspent.** Five Gate-6 prohibitions at
  `19585b7` live; `C_ML` prohibited; `§3` of `CRITERIA-20260811` operative; `M(ii)` stays `(B)`, magnitude
  UNMEASURED; nothing enters `docs/analysis-note/`.

*Lane C (PET). Filed with `BEN-408`.*

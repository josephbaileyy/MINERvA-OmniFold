# A validation that does not exercise the failure mode; and a restatement that read as a second measurement

**Filed 2026-08-15 by the executor lane** (a peer Claude session, block `310-319`), on the mediator's
authorization, **beside `f4267b4` and not over it.** Rows: `BEN-310`, `BEN-311`. Receipt-chain hole:
`OI-125`. Subject item: `OI-71`, which **stays OPEN**.

**Nothing in lane D's finding text is edited or retracted here.** D is not running, the row is D's, and
**D's arithmetic is not in question — it reproduces exactly.** What is corrected is the *target* of that
arithmetic. That distinction is the whole of this document's relationship to `f4267b4`: a scope
correction, not a discredit.

---

## 1. THE RESULT THAT MATTERS, AND IT IS NOT THE MARGIN

**VL100's own run does not exhibit the fold-forward deficit at all.**

| quantity | nominal run | VL100's own run (`56552326`) |
|---|---:|---:|
| fold-forward ratio over `pass_reco` | `0.736746250130697` | **`1.011418`** |
| `R` (`step1_class_ratio`) | `1.1240802949941018` | **not recorded anywhere** |
| `dev = \|ratio/R - 1\|` | `0.3445786271570904` | **not formable** |

The 34% deficit is a property of the **nominal** run. The closure that certifies the annealed arm
reproduces it **not at all** — its pushed weights conserve the reco-leg sum to about 1%.

**This is worse news than "the margin survives," and it is the thing Joseph needs.** A validation that
does not reproduce the fold-forward behaviour of the run that produces the physics is **silent** about
that failure mode, not reassuring about it. `VL100` was asked to validate the annealed estimator
*configuration*; if the fold-forward deficit is a defect, `VL100` never exercised it and therefore
cannot certify against it. **That question is upstream of whether the recovery margin clears**, and
nothing in this document or in `f4267b4` answers it.

It is not answerable read-only, either. See §5.

## 2. THE RECEIPT-CHAIN HOLE (`OI-125`)

The closure recorded **no `step1_class_ratio` and no fold-forward scalars** — not in
`NONQUOTABLE-DIAGNOSTIC.POWERED_CLOSURE_ANNEALED.slurm-56552326.json`, not in
`NONQUOTABLE-DIAGNOSTIC.PREFLIGHT.slurm-56552326.json`, and not in the 47/47
`NONQUOTABLE-DIAGNOSTIC.INDEPENDENT_VALIDATION.slurm-56562169.json`.

So **no `dev` can be formed for `VL100`'s run from the record at all.** The `1.011418` in §1 is a
measurement made by this session from the artifact's per-event pieces — **not a recorded value.** The
nominal run's weights npz carries `fold_forward_sum_w_push_reco`, `fold_forward_sum_w_reco`,
`fold_forward_n_pass_reco` and `step1_class_ratio`; the closure's carries none of them, so the
diagnostic that the whole quarantine is about **cannot be evaluated on the run whose number the arm
choice rests on.** Filed as `OI-125`.

## 3. THE SCOPE ERRORS: A DIFFERENT RUN, AND A DIFFERENT ARM

> **ATTRIBUTION CORRECTED 2026-08-15, later the same day, by the lane that wrote this section.**
> This section originally read as though lane D chose the wrong file. **D did not.** The closure's own
> quarantine manifest names `fullevent_nominal/pet_fullevent_nominal_weights.npz` as `weights_path` and
> computes its entire fold-forward rejection from it, and the CPU finalizer's `hash:nominal-weights`
> check pins that same file. **D decomposed the quantity the quarantine actually uses, which is the
> correct target for the question D asked.** The run/arm mismatch originates in the manifest, upstream
> of the probe, and it was independently re-derived by the finalizer before D ever ran. Read §1 and §2
> of `FINDING-20260815-the-quarantine-measured-a-different-run.md` before reading the two subsections
> below as a criticism of the probe — they are a description of the record the probe followed.


`probe-vl100-foldforward-shape-20260814.py:46` reads
`nd-unfolding/pet/fullevent_nominal/pet_fullevent_nominal_weights.npz`.

**Different run.** `VL100` comes from job `56552326` — different subsample, different loader
population, an injected truth tilt. D's `n_pass_reco` is `837671`; the closure records
`n_step1_a = 837494` and `n_step1_b = 836975`, and this session measures `837034` `pass_reco` rows in
half B. **It matches none of them.** The *grid* is `VL100`'s; the *weights* are another run's.

**Different arm — found by the mediator, re-measured independently here rather than relayed:**

| | path | sha256 | `seed_policy.lr_policy` |
|---|---|---|---|
| pre-anneal | `fullevent_nominal/…weights.npz` | `58f664cd…f2f51084` | **key ABSENT** |
| promoted | `fullevent_nominal_annealed/…weights.npz` | `559a1020…5ef6eb3e` | `schedule = fit-time-anneal-after-iteration-0` |

**`VL100` is the ANNEALED arm's recovery, and the falsification of it was computed from the retired
arm's weights.**

And the two runs' fields are **nearly uncorrelated** — Pearson `0.141`, Spearman `0.195`. A shared
fold-forward *defect* would make them agree; each field being dominated by its own learned reweighting
would not.

### 3a. Fifth instance of one trap, whose remedy already exists

`fullevent_nominal/` and `fullevent_nominal_annealed/` are **sibling directories holding
identically-named files.** Prior instances: `sbatch_fullevent_diagnostic_extract.sh:42`,
`leg_mismatch.py:30`, the P5A extraction launcher, and now this probe.

**Lane C's guard is the one-line remedy and it is already in the repo** —
`nd-unfolding/pet/sbatch_p5a_fullevent_nominal_extract.sh:153-182` (`G1`): assert
`seed_policy.lr_policy.schedule == "fit-time-anneal-after-iteration-0"`. The reason it is the right
form is in C's own comment: **the pre-anneal artifact has no `lr_policy` key at all, so it fails
loudly rather than comparing two unequal values** — and it discriminates by *schema*, so it catches a
wrong arm whatever the path and survives a legitimate digest change, which a sha pin does not.

> **TIMELINE CORRECTED, because the convenient version was wrong.** The dispatch that authorized this
> filing described C's guard as *"written hours before this probe ran."* Measured: the guard landed at
> `d184f95`, **2026-08-14 19:56:51 -0400**; D's falsification is `f4267b4`, **19:50:07 -0400**. The
> guard is **`+404 s` LATER**, so it was **not available to D.** It *was* available to every reader
> afterward, including the propagation of the finding into three places. The remedy's value is
> prospective, and overstating its availability would have made this document an instance of the
> carelessness it is about.
>
> **AND THE CORRECTED FACT IS THE MORE USEFUL ONE.** *"D missed an available remedy"* is an accusation
> and it is false. What actually happened is that **two lanes reached the same hazard independently
> inside seven minutes** — one building a guard against it, one falling into it — with neither able to
> see the other's work. **Two independent arrivals are evidence the hazard is structural, not evidence
> of a lapse.** That is why this finding names the directory layout, and why the remedy is a schema
> assertion in every reader rather than more care by any author.

## 4. WHY THE MEASUREMENT WAS NOT A SECOND MEASUREMENT (`BEN-310`)

**Lane D's per-cell field is the unfolding's own per-cell output.** By D's own definition,
`ratio[c]` is the `w_reco`-weighted mean of `push` inside cell `c`. The unfolding's per-cell
correction, `h_unfolded[c]/h_prior[c]`, is the `w_truth`-weighted mean of the **same `push`** inside
the **same cell**. They differ only by weight leg (`w_reco` vs `w_truth`) and population (`pass_reco`
vs `pass_truth`) — so they are **one statement, not two.**

Measured, not argued:

| | Pearson | Spearman | `rel_sd` of D's field | `rel_sd` of `h_unfolded/h_prior` | ratio of the two |
|---|---:|---:|---:|---:|---|
| the run D decomposed | **`0.99973`** | `0.99937` | `0.47021238590619524` | `0.4658785086788078` | `0.933 → 1.020` |
| `VL100`'s own run | **`0.99987`** | `0.99978` | `0.34818` | `0.34672` | `0.993 → 1.060` |

**The consequence: dividing that field out is a de-unfolding, not a shape correction.** Applying
`alpha = -1` with the field measured on `VL100`'s own run gives recovery **`-0.000808`**, and lands at
`L1 = 0.00313` from `h_prior` against the unfolding's own distance of `0.13156` — **2.4% of the way.**
Recovery of `h_prior` is **0 by construction** (residual ≡ gap). The operation returns the unfolded
spectrum to the prior.

**Why the `68×` framing persuaded, and this is the transferable part:** the null it tests is **"`push`
is flat across the grid," which is the negation of unfolding working at all.** *Any* real reweighting
beats sampling noise by a large factor, so the comparison **cannot discriminate a contaminating
deficit from the answer.** The dispersion was real, the noise model was honest, the global-scale
control was a genuine test — and the quantity still could not bear the inference, because the recorded
fold-forward scalar has **no per-cell reference** against which a per-cell *deficit* could be defined.
`ratio[c]` compared against a constant assumes flatness; there is no `R_c`.

This is `BEN-300`'s form one level down: **consensus among restatements of one source is not
corroboration** — here, two weighted means of one `push` array, one of them presented as a contaminant
of the other.

### 4a. How it survived to three places

The propagation into the P5A `NOT_CANONICAL.json` output contract, into `OI-71`, and to Joseph is the
**mediator's**, and the mediator has said so and is correcting it. The mechanism worth recording is
narrower: `OI-71`'s cell states the falsification was *"Re-verified from the object by lane A rather
than relayed."* **That re-verification was of D's receipt object** — the per-cell arrays, the
`observed_over_noise`, the global-scale control — **all of which are correct.** What it did not check
is **which artifact the probe opened**, which is one `grep` of line 46 of the probe committed beside
it. **Re-deriving a receipt's numbers from the receipt cannot detect that the receipt describes the
wrong object**, and that is exactly the gap a schema guard like C's `G1` closes and a numeric
re-derivation does not.

## 5. THE ANSWER TO THE QUESTION ASKED, AND ITS LIMIT

**Question:** how far does `VL100` move under a shape-corrected fold-forward?

Reproduced first, from the persisted 285-cell spectra using the producer's own definitions
(`closure_powered_truth_reweight.py:339-345`):

```
gap      = L1(h_prior,   h_target)  = 0.23427036251295683
floor    = L1(h_prior,   h_untilted)= 0.010747273613151719
residual = L1(h_unfolded,h_target)  = 0.11418260718355933
recovery = 1 - residual/gap         = 0.5126032761517403   (published: identical, d = 0.000e+00)
adopted  = 0.80 x 0.618228          = 0.49458240000000003
margin                              = 0.01802087615174025
```

**"Shape-corrected" is not a determined operation**, because the record has no per-cell reference. It
is a one-parameter family, `h_corr[c] ∝ h_unfolded[c] · (q[c]/⟨q⟩)^α`, re-unit-normalized. The field
`q` is **not** `ratio[c]` — §4 shows that choice is a de-unfolding. It is
`q[c] = ratio[c] / (h_unfolded[c]/h_prior[c])`: the only content of `ratio[c]` that `h_unfolded` does
not already carry, i.e. the weight-leg / population (acceptance-side) part.

| field | `q` amplitude | `α = -1` | `α = 0` | `α = +1` | worst margin | criterion lost at |
|---|---:|---:|---:|---:|---:|---|
| `VL100`'s own run | `0.52%` | `0.511140` | `0.512603` | `0.513984` | **`+0.016557`** | `11×` / `22×` amplitude |
| nominal run (**adversarial**, `2.8×` amplitude, from the run where the deficit lives) | `1.44%` | `0.515176` | `0.512603` | `0.509074` | **`+0.014491`** | **`2.8×`** / `4.6×` amplitude |

**The arm still clears.** Sensitivity to the choice is enormous *between* families (the rejected one
spans `-0.0008` to `+0.535` and crosses the criterion at `|α| ≈ 0.05–0.09`) and negligible *within*
the defensible one. **The whole question was which family, and that is settled by an identity, not a
preference.**

**Alignment control, without which none of the above counts.** `weights_push` is aligned to half B,
whose global row ids are `dump_rows_b`; `deterministic_halves` returns **sorted** index sets and
`mc_indices` is sorted, so `push[j] ↔ dump_rows_b[j]` is determined rather than guessed. Rebuilding
the spectra from the artifact reproduces the published recovery: **`0.5126032762844603`** vs
`0.5126032761517403`, `d = 1.3e-10`; max relative deviation over cells with mass `5.8e-8`. That
residual is the loader's float32 in-place rescale not cancelling elementwise under unit normalization.
**A wrong pairing would move `h_unfolded` by of order its own bin values (`1e-3`), not `1e-10`.**
Corroboration that this session computed D's quantity at all: the global ratio reproduces D's recorded
`0.736746250130697` to `1.5e-13`, and D's `rel_sd` to the last printed digit.

### What is NOT established

1. **`OI-71` is not closed, and this is the load-bearing limit.** Every correction computable from
   disk is **post-hoc and multiplicative on `h_unfolded`.** The fold-forward acts in iterations 2 and
   3 of 3, so a defect that mis-delivered weight **during training** is baked into `push` itself and
   **no reweighting of `h_unfolded` can probe it.** Only a retrained closure answers it. **None was
   submitted, and none should be without Joseph.**
2. **The nominal run's 34% deficit is untouched and still real.** What §4 explains is its per-cell
   *structure*; its *magnitude* is not explained here.
3. **Three hygiene quotability grounds remain unexamined** — by D, by the mediator, and here.
4. **The margin is genuinely thin in absolute terms.** An adversarially-aligned shape distortion of
   ~2.5–3.3% of `h_unfolded` consumes `0.018` entirely. The measured residual field is `0.52%`–`1.44%`.
   The factor is `2.8`–`11`, not `100`.
5. **Verified by whom.** The mediator independently verified **the arm error only**. The Pearson
   coefficients, the reproduction to `1.3e-10`, the alignment control, and the `1.011418` are
   **measurements made by this session** and are shipped with their operands
   (`RECEIPT-vl100-shape-corrected-foldforward-20260815.json`, plus the two per-cell operand JSONs) so
   they can be contradicted rather than taken on trust.

## 6. Artifacts

| file | what |
|---|---|
| `state/RECEIPT-vl100-shape-corrected-foldforward-20260815.json` | the receipt: both scans, all crossings, ingredients, hashes |
| `state/probe-vl100-shape-correction-scan-20260815.py` | regenerates the receipt from committed operands; **no cluster access needed** |
| `state/probe-vl100-own-run-foldforward-20260815.py` | read-only cluster probe: per-cell fold-forward ratio for `VL100`'s own run + the alignment control |
| `state/vl100-own-run-foldforward-20260815.json` | its output (285-cell operands) |
| `state/probe-vl100-nominal-residual-field-20260815.py` | read-only cluster probe: the nominal run's residual field |
| `state/vl100-nominal-residual-field-20260815.json` | its output (285-cell operands) |

Read-only throughout: two python reads on a Perlmutter login node. No `sbatch`, no `scancel`, no
`scontrol`; `gate6traj-reconcile-56847059` untouched; the cluster repo neither pulled nor written;
array `56993778` untouched.

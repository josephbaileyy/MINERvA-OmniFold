# The quarantine that rejects `VL100` measured a different run, and three parties agreed because they read the same file

**Filed 2026-08-15 by the executor lane** (block `310-319`), read-only, on the mediator's standing
authorization to examine the remaining quotability grounds. Rows: `BEN-312`, `BEN-313`. Extends
`OI-125`; supplies the grounds determination `OI-71` was waiting on for three of its four grounds.

**This document corrects my own finding of earlier today.**
`FINDING-20260815-a-restatement-is-not-a-second-measurement.md` said lane D "decomposed the wrong
run." That is true as to *fact* and **wrong as to attribution**: D read the artifact the closure's own
quarantine manifest names as the source of its fold-forward rejection. **D followed the record.** The
mismatch is in the manifest, upstream of the probe.

---

## 1. THE CHAIN, MEASURED

`NONQUOTABLE-DIAGNOSTIC.manifest.slurm-56552326.json` — the quarantine manifest for the closure that
produced `VL100` — carries:

```
job_id        56552326                                  the ANNEALED powered closure
push_path     …/annealed_shape_validation/….slurm-56552326.npz
push_sha256   1c5a8fef…780202                           == closure report artifact.sha256  (correct)
xsec_path     …POWERED_CLOSURE_ANNEALED.slurm-56552326.json
xsec_sha256   f7f76459…e9c015                           == that file, recomputed here     (correct)

weights_path  …/pet/fullevent_nominal/pet_fullevent_nominal_weights.npz
weights_sha256 58f664cd…f2f51084                        <-- the PRE-ANNEAL nominal run

fold_forward  sum_w_push_reco 736746.2709517315
              sum_w_reco      1000000.0282607947
              reco_weighted_mean_push 0.736746250130697
              R               1.1240802949941018
              deviation       0.3445786271570904   tolerance 0.05   exceeds by 6.891572543141808
              recomputed_from "the weights artifact, not from any report or summary"

rejection_reason  "...NOT QUOTABLE on the physics alone, independent of how this manifest is labelled."
publication_gate_rejects_this                  true
publication_gate_rejects_this_on_physics_alone true
```

**Every hash in that manifest is correct for the file it names.** The defect is not a broken pin. It is
that **`weights_path` names a different run and a different arm than `job_id` does** — and the
`fold_forward` block, the `rejection_reason`, and the physics-alone publication rejection are all
computed from `weights_path`.

**The closure's own push weights do not show that deficit.** Measured from `push_path` — the same
artifact from which the 47/47 validation re-derives every one of the four spectra:

| | reco-weighted mean of `push` over `pass_reco` |
|---|---:|
| `weights_path` (pre-anneal nominal, what the manifest measured) | `0.736746250130697` |
| `push_path` (the closure's own artifact, what `VL100` is computed from) | **`1.011418`** |

So **`NOT QUOTABLE on the physics alone` is a true statement about a run that is not this one**, and it
is attached to `VL100` by the manifest's own file pointers.

### 1a. Two objects under one job id

The manifest's `purpose` describes a **cross-section extraction**: *"first exercise of the full-event
extractor on real input. Diagnostic only: the fold-forward deficit is unrepaired, so this cross section
is knowingly low by ~34%."* On that reading the `fold_forward` block is about the right object — the
extraction, which was built from the nominal weights.

But `xsec_path` and `xsec_summary_path` point at the **closure report** and the **preflight gate
receipt**, and *neither contains a cross section*: grepped for `xsec`, `cross_section`, `d2sigma` —
**zero keys in either file.** So the manifest describes an extraction, names the closure's artifacts as
that extraction's products, and its physics rejection transfers to `VL100` in consequence.

**Both readings converge on the same operative fact**, which is the one that matters and is not
disputable: the measurement behind `VL100`'s physics rejection was taken on another run's weights.

## 2. WHY IT LOOKED CORROBORATED (`BEN-312`)

Three parties, on three days, produced the same `0.3445786271570904`:

| who | what they did | which file |
|---|---|---|
| manifest author | recorded `fold_forward`, *"recomputed from the weights artifact"* | `58f664cd…` |
| CPU finalizer `56562169` | check `quarantine:dual_publication_rejection` → `recomputed_deviation 0.3445786271570904`, `fold_values_match true`; pinned by check `hash:nominal-weights` → `58f664cd… == 58f664cd…` | `58f664cd…` |
| lane D `f4267b4` | decomposed those scalars per cell | `58f664cd…` |

**All three agree, all three are arithmetically right, and all three read the same file.** The
finalizer's re-derivation is exactly the kind of independent check the campaign relies on — and it
**cannot** detect this class of error, because what it pins is *that the file it read is the file the
manifest named*. `hash:nominal-weights` passing is the defect being confirmed, not caught.

**This is `BEN-300`'s mechanism at the level of a shared source rather than a shared restatement.**
Consensus among readers of one artifact is not corroboration that the artifact is the right one. The
transferable check is the one `BEN-311` already names: **assert the ARM by schema at the point of
read** — `seed_policy.lr_policy.schedule`, which is absent on the pre-anneal artifact — rather than
verifying that a path matches a recorded path.

## 3. THE "FOUR QUOTABILITY GROUNDS" WAS A COUNT WITH NO MEMBERS (`BEN-313`)

I was asked to determine the three hygiene grounds. **They are not written down anywhere.**

Derived, not assumed: the phrase originates in **`f4267b4` itself** — lane D's own limitation sentence,
*"It says nothing about the other three quotability grounds, which are hygiene rather than physics and
were not examined here."* `git log -S` over all branches returns that one commit. It now appears in
**five** places (D's receipt, `OI-71`, `ND_OMNIFOLD_RUN_LOG.md:7705`, and twice in my own artifacts of
this morning). **Not one of them enumerates the four.** No `CONVENTION-*.md` defines quotability at
all.

So the count propagated as a fact for a day, and every downstream statement of the form *"three grounds
remain unexamined"* — including my own, twice — asserted the existence of a set nobody had listed. **A
count is the cheapest thing to relay and the hardest to falsify**: it survives every restatement
because it names nothing that can be checked.

### The enumeration the record actually supports

Reconstructed from the artifacts rather than from the phrase. **There are three grounds, not four, and
two of them are the same ground.**

| # | ground | source | determination |
|---|---|---|---|
| **G1** | the fold-forward deficit makes the product non-quotable on physics alone | manifest `rejection_reason`, `publication_gate_rejects_this_on_physics_alone` | **DETERMINED — does not describe this closure.** §1: measured on `58f664cd…`; the closure's own artifact gives `1.011418`. |
| **G2** | the `NONQUOTABLE-DIAGNOSTIC.` prefix and `quotable: False` | closure report `annealed_lr_arm.note`; manifest `authorizes_engine_change: false` | **DETERMINED, and NOT INDEPENDENT OF G1.** The note scopes itself to *"does NOT authorize editing `omnifold.py` — that promotion is separate and Joseph's"*, i.e. to engine edits and promotion, **not** to quoting a value — as `AUTHORIZATION-20260813…:496-500` already says. The only publication-level content in the label is the manifest's two booleans, and those are computed from G1. |
| **G3** | provenance hygiene of the value itself | 47/47 finalizer; 14 hash pins; the Slurm `3:0`; the renamed retired self-check | **DETERMINED CLEAN, with one inherited residual.** All 14 pins pass; the `3:0` is a post-training launcher artifact of the driver's retired absolute-`0.80` self-check, and `closure_powered_annealed_lr.py:199-207` renames that field rather than letting it read as the verdict. Two independent reproductions of the recovery were added this morning. **Residual:** `hash:nominal-weights` pins the pre-anneal file, so G3's re-derivation of G1 inherits G1's target. |
| **G4** | recovery has never been evaluated at the promoted configuration | promotion receipt `explicitly_not_claimed[2]`: *"recovery_evaluated remains False"* | **NOT DETERMINABLE READ-ONLY — structurally.** See §4. |

**Checked and found NOT to be a defect, recorded so nobody re-files it:** the manifest's publication
booleans are read only for truthiness and have **no executable consumer** — `git grep` finds them in
markdown only. That is the `BEN-228` shape, **and it is already analysed and correctly dispositioned**
at `REPAIR6-RECORDED-NOT-CHECKED-INVENTORY.md:51-65`: a literal that can only ever cause a *refusal* is
**fail-closed**, its real failure mode is the key going **absent**, and its guard is the
both-directions test `tests/test_p4_repair.py::NonAdoptableMarker`. **Do not re-file this.** I went
looking for it as a finding and the repo had already answered it.

## 4. G4 IS THE ONE THAT NEEDS THE INSTRUMENT

`recovery_evaluated: False` at the promoted artifact
(`fullevent_nominal_annealed/pet_fullevent_nominal_weights.npz`, job `56563761`, `559a1020…`) is
**not closable by any read.** Recovery is defined against an **injected truth reweight** — the closure
tilts half A and asks how much of the induced gap the estimator recovers. The promoted nominal has no
injected tilt and no A/B split, so there is no recovery to compute from its weights, at any effort.

`OI-23` established *configuration equivalence* between the closure and the promoted run — 12 shared
dimensions plus the LR policy across a float32 boundary — which is an argument that the two would score
alike, **not a measurement that they do.**

**And G4 shares its instrument with `OI-71`'s remaining physics question.** My own limitation stands:
every correction computable from disk is post-hoc and multiplicative on `h_unfolded`, so a fold-forward
defect that mis-delivered weight *during* iterations 2–3 is baked into `push` and unreachable by
reweighting. **One retrained, instrumented closure answers both.** Costed and predeclared in
`PROPOSAL-20260815-instrumented-and-corrected-foldforward-closure.md`. **Not submitted** — the
promotion receipt's own `scope_PROMOTED_IS_NOT_PROCEED.NOT_authorized` lists *"any recovery run"* and
requires *"A FRESH authorization from Joseph."*

## 5. `OI-125` IS SHARPER THAN FILED

`OI-125` recorded that the closure's three receipts persist no `step1_class_ratio` and no fold-forward
scalars. Measured since: **`git grep -n 'fold_forward'` over `closure_powered_truth_reweight.py` and
`closure_powered_annealed_lr.py` returns ZERO hits.**

So it is not a persistence omission — **the closure driver has no fold-forward computation at all.**
`train_fullevent_nominal.py:576-577` computes it in eight lines; the closure driver never did. That is
why the quarantine had to reach for another run's weights to state a fold-forward rejection: **for this
closure there was no such number to state.** The fix is to add the computation, not to persist an
existing one.

## 6. What this does and does not change

**Does not change:** `VL100 = 0.512603276` stands, reproduced twice. It still clears under both
corrections. The nominal extraction's ~34% deficit is real and unexplained. The three hygiene grounds
turn out to be two, and both are determined, so **`OI-71`'s remaining content is G4 alone** — which is
narrower than the row implied and needs GPU time, not more reading.

**Does change:** the *physics* ground against `VL100` was never about `VL100`'s run. Anyone reading the
`NONQUOTABLE-DIAGNOSTIC.` prefix as a physics verdict on the recovery number is reading a measurement
of the pre-anneal nominal extraction. **The label is correct about the extraction and does not transfer,
and until §5's computation exists, this closure has no fold-forward number of its own to be judged on.**

Read-only: four `ssh` reads (two python, two `sacct`) plus local greps. No `sbatch`, no `scancel`, no
`scontrol`, no submission of any kind.

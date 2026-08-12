# Promoting a PET nominal by MOVING it silently re-points the superseded artifact at the new estimator's weights — and it already happened

**Found 2026-08-11 by Session C (PET) while preparing an authorized promotion, BEFORE performing it.**
`BEN-133`. This is a live corruption in a committed artifact set, not a hypothetical.

## 1. The mechanism

Every full-event PET weights artifact embeds an **absolute** `inference_contract["weights_folder"]`, and
consumers resolve checkpoints from it — `step1_increment_trajectory.py` (`wf = contract["weights_folder"]`),
`gate_ab_push_provenance.py`, `step1_pull_push_decomposition.py`, and
`extract_fullevent_fps.py:253` (`inference_contract["step2_checkpoint"]`).

The established promotion mechanism is move-and-archive: the outgoing artifact set is moved into
`fullevent_nominal/superseded-<date>/` and the incoming set installed at `fullevent_nominal/`. The
artifact's embedded path does **not** move with it.

## 2. It has already fired, and it fails in the dangerous direction

Measured on the cluster, 2026-08-11:

```
SUPERSEDED-20260806:
   file lives in : fullevent_nominal/superseded-20260806
   contract says : .../nd-unfolding/pet/fullevent_nominal/w_nominal
   folder exists : True
   step2 ckpt    : EXISTS  .../fullevent_nominal/w_nominal/OmniFold_fe_nominal_nominal_iter2_step2.weights.h5
```

The 2026-08-06 artifact was moved on 2026-08-07. Its contract still names `fullevent_nominal/w_nominal`
— **and that folder exists, and the checkpoint exists.** But those are the **2026-08-08** artifact's
networks. So loading the superseded 08-06 npz and following its own contract pairs **08-06 push weights
with 08-08 model weights**, and nothing errors.

**This is the worst available failure shape and the campaign has a name for it:** it fails *silently*
and leaves *an artifact asserting a state it cannot have* (BEN-084's asymmetry). A dangling path would
have raised `FileNotFoundError` on first use. A path that resolves to a *different estimator* returns a
number.

## 3. Why it would have bitten tonight, which is why this is filed before the promotion and not after

Promoting `56563761` by the same mechanism means moving the 2026-08-08 artifact into
`superseded-20260811/`. Its contract says `fullevent_nominal/w_nominal`, which would then hold the
**annealed** checkpoints. The 08-08 artifact would silently resolve to the annealed network.

That artifact is not incidental. It is:

- the **control arm** of job `56691812`, run hours earlier, whose whole purpose was to be the
  pre-anneal comparison — the control would start returning treatment weights;
- the baseline `58f664cdef266d09` the ledger asserts unchanged (`VALIDATION_LEDGER.md:1580`);
- the artifact BEN-043, CLM-012's numeric basis, and the frozen `fold_forward_ratio_dev_max` are
  measured against.

So the obvious mechanism would corrupt the reference point of the measurement that justified the
promotion, on the same night, and every downstream read would keep succeeding.

## 4. Recommended mechanism: promote by DESIGNATION, not by moving bytes

Leave every artifact where it is and change what *canonical* names — registry, ledger, and the
consumers' defaults. Properties, none of which the move has:

- **no digest changes**, so every committed receipt binding
  `pet_fullevent_nominal_weights.npz` stays true — including the four from `56691812` and the
  Gate-A/B chain;
- **no artifact's self-description is falsified**; each contract keeps pointing at its own checkpoints;
- **reversible** — it is a pointer change, not a data migration;
- it does not require editing the contract *inside* an npz, which would change the artifact's digest and
  invalidate the receipts that bind it (the only other way to make a move coherent).

**§4 CORRECTED 2026-08-12 — this list was wrong twice and the document contradicted itself.**
As first written it named "six hardcoded references" and **omitted the two class-2
`os.path.join` sites** — `gate_ab_push_provenance.py` and `step1_pull_push_decomposition.py` — which
**§1 above lists by name as consumers that resolve checkpoints from the embedded `weights_folder`**.
So the section that made the recommendation falsifiable dropped two of the sites the section above it
had already identified, and it dropped exactly the two that a literal-path grep cannot see. The count
was then wrong a second time in the other direction: a full enumeration over ALL tracked files (not
just `*.py`/`*.sh`) finds **51 files / 105 occurrences**, of which only **two were retargets**. The
rest are diagnostics of the 08-08 artifact, producer/output paths, or historical records — see
`nd-unfolding/pet/check_canonical_designation.py`, which now enforces that every one carries an
explicit disposition.

Cost, stated so the recommendation is falsifiable: `canonical` stops being "whatever is at
`fullevent_nominal/`" and becomes a named pointer, so **two defaults were retargeted and every other
reference was deliberately left** — `leg_mismatch.py:30`, `inversion_screen.py:33`, `push_vs_acceptance.py:34`,
`sbatch_fullevent_diagnostic_extract.sh:42`, `sbatch_fullevent_diagnostic_xsec_resume.sh:27`,
`sbatch_designA_diagnostic_reproduction.sh:51` (plus `sbatch_step1_trajectory.sh:42`). **And they must
not be retargeted uniformly:** several are diagnostics *of the 08-08 artifact specifically* (the
Design-A reproduction, the leg-mismatch and inversion screens), and silently repointing those at the
annealed artifact would reproduce this very defect one level up — a diagnostic whose target changed
under it while its name stayed the same.

## 5. Status: PROMOTION PERFORMED 2026-08-12 by designation — this section is kept as the record of the pause

> **UPDATED 2026-08-12. The promotion has now LANDED**, by designation, at `461ba00`: two defaults
> retargeted, 105 occurrences across 51 files each carrying an explicit disposition, enforced by
> `nd-unfolding/pet/check_canonical_designation.py`. The text below is the state *before* that, and is
> kept rather than rewritten because the pause is the part worth reading — a section reading "NOT
> performed" after it was performed is the stale-status defect this campaign keeps paying for, so it is
> banner-corrected here rather than silently edited.
>
> What released it: the mechanism concern was **corroborated by a session trying to refute it** — a
> consumer handed an artifact resolves *that artifact's* own contract, so designation-without-moving is
> safe and never rested on the reference count being complete. And a class-5 **runtime identity guard**
> now backs it where no checker can reach: the three 08-08 diagnostics assert fold-forward
> `0.7367462501305516` from the artifact's own contents before use, power-tested to refuse both the
> annealed (`1.084053`) and the 08-06 superseded (`0.746483`) artifacts.

## 5(historical). Status at filing: the promotion is NOT performed, and this is a surfaced blocker rather than a substitute

The promotion is authorized (`AUTHORIZATION-20260811-annealed-promotion-and-hpss.md`, verbatim
*"promote it and launch the HPSS archive"*, first-hand, informed). The orchestrator's instruction with
that authorization was explicit: *"If either turns out to be blocked for a reason we have not seen, tell
me before improvising — he has authorized these two actions, not a substitute for them."*

Promotion-by-designation **is** a substitute for promotion-by-move: different files change, different
things can break, and the resulting tree looks different to the next reader. So it is routed rather than
performed. What is done instead is this file, the recommendation above, and the pre-existing corruption
in §2 recorded so it is fixed on its own merits regardless of which mechanism is chosen.

**The 08-06 corruption needs repair either way**, and it is independent of tonight's decision. The
cheapest correct repair is a `NOTE.md` in `superseded-20260806/` recording that the artifact's embedded
`weights_folder` is stale and naming the checkpoints it was actually trained with — the Gate-2
supersessions already write exactly such a `NOTE.md` and the PET one did not, which is the whole
difference. Rewriting the npz to fix the path is the wrong repair: it would change a superseded
artifact's digest.

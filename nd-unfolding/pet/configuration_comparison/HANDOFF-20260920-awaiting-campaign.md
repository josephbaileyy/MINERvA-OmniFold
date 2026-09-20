# Blocked on one thing: scheduler time. Everything else is done and verified.

**The comparison is NOT complete.** No arm has trained at campaign scale, no
recovery is measured, and the only PDF that exists is a plumbing check marked
NOT A RESULT.

## The exact missing artifact

`/pscratch/sd/j/josephrb/campaign-20260920/final/*/weights_*.npz` — 16 files,
eight seeds × two arms. Nothing else is outstanding.

## The continuation command

When `final` (job 58606605) completes:

```bash
python3 nd-unfolding/pet/configuration_comparison/report_campaign.py \
  --campaign /pscratch/sd/j/josephrb/campaign-20260920 \
  --closure-npz /global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/g2_input/G2_FPS_MEFHC_P12.npz \
  --reference 0.6949731568655361 \
  --output /pscratch/sd/j/josephrb/campaign-20260920/campaign_report.json

python3 nd-unfolding/pet/configuration_comparison/make_final_deck.py \
  --report /pscratch/sd/j/josephrb/campaign-20260920/campaign_report.json \
  --outdir nd-unfolding/pet/configuration_comparison/slides \
  --stem final_comparison
```

Both have been run end to end on real weights, real receipts and the real
closure file; the second produced a rendered 395 kB PDF. **There is no open
input.** `--reference` is `frozen_design.REFERENCE["aggregate"]`, computed
2026-09-20 from the frozen endpoint at the frozen `niter=3` and pinned BEFORE
any comparative result existed:

| | |
|---|---:|
| aggregate reference, k=3 | 0.694973 |
| adequacy floor, 0.80 x | **0.555979** |
| regional floors, 0.60 x each region's own | low_acceptance 0.0084, poor 0.2199, moderate 0.4659, good 0.5853 |

Quoted with its iteration count on purpose: the same ceiling is 0.5104 at k=1
and 0.7146 at k=4, so a reference without its `k` is ambiguous by a third.

## What is queued, at commit `5507ed8f`

| job | stage | state |
|---|---|---|
| 58607250 | gather, one per stage | PENDING (Priority) |
| 58607251 | tuning, **32** — 4 rates x 4 seeds x 2 arms | `afterok` gather |
| 58607253 | select the learning rate, per arm | `afterok` tuning |
| 58607254 | pilot, 8 | `afterok` select |
| 58607255 | final, 16 | `afterok` pilot |
| 58607256 | **report, deck, PDF, claim index** | `afterok` final |

**The chain ends by producing the deliverable.** Nobody has to run anything:
every input is pinned, and `sbatch_report_and_deck.sh` writes the report, the
deck and the PDF, commits them in the cluster checkout and leaves a git
bundle. It sends nothing, by design and by test.

**Priority decision, Joseph, 2026-09-20: wait.** The chain sits behind roughly
200 pending tasks from this account's 5D unfolding lane, which holds the
fairshare. Holding those was offered and declined; the 5D lane keeps its
priority and this one waits its turn. The gather's request was cut from 120 GB
to 48 GB after sizing it from the arrays it actually holds (~4 GiB peak) --
the only lever this lane had, and it is pulled.

Cost, re-derived for the closure: **58.5 GPU-hours, 73.1 with retries**,
against a 1,000-hour ceiling. The 366-hour figure was built on the real-data
nominal's row counts and does not describe this campaign.

## Do not read the plumbing PDF as a result

`PIPELINE_VERIFIED-20260920.md` records his 0.1484 against our 0.0197 from a
40,000-event smoke at one OmniFold iteration. Both arms are far below the 0.76
adequacy floor there, which is why the report correctly returns
`NEITHER_ELIGIBLE / NO_SELECTION`. His arm starts from his checkpoint and ours
from scratch, which is the point of the pretrained arm and also why a
one-iteration number flatters it.

## What changed today, for whoever picks this up

Sixteen defects, every one of which would have produced a completed campaign
rather than a failed one. The ones that would have produced a WRONG ANSWER
rather than a crash:

* the driver unfolded **real data** and never applied the injection, while its
  docstring said the opposite;
* the injection existed twice, and the reference ceilings were built with one
  form and would have been scored with the other;
* his arm received the pre-conversion feature representation, not the
  `eta, phi, log pT, log E` his model reads;
* the dE/dx sentinel `-999` went into the network raw;
* his arm was **not pretrained** — and after that was fixed, the engine's
  `clone_model` discarded the weights, while the receipt recorded an exact
  load;
* our arm ran a bare `MultiFold` rather than the annealed incumbent;
* `epochs` defaulted to 50 against the frozen 8;
* the stage splits were frozen and unimplemented, so tuning, pilot and final
  shared their events.

Three of those were frozen fields describing something nobody had implemented.
Two were caught by a number that should have moved and didn't.

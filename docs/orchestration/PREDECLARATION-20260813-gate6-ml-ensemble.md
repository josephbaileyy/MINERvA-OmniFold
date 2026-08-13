# PREDECLARATION 2026-08-13 — Gate 6, PET-specific ML ensemble at N=5

**Written before any member is submitted.** Nothing in this file was chosen after seeing a spread.

## Authority and how N was chosen

Joseph asked whether the literature gives a precedent for the member count and seed set. **It does, and it
is narrow.** The **neutrino** OmniFold measurement — the closest precedent to this analysis — used **5
trials**, with the stated justification that the resulting standard error is negligible against the
systematic and statistical uncertainties. HERA jet-substructure OmniFold used **10 models per step**.
**5 is the neutrino-specific precedent with a reason attached; 10 is the broader HEP convention.**

**`N = 5`.** The reasoning is the mediator's (`[CLAUDE]`-class), endorsed by Joseph, **not authored by him**.
Recorded that way so a later reader does not attribute the choice of 5 to him.

**No literature prescribes a seed SET.** Members differ by initialization and subsample draw; the values
are an implementation detail. **That is precisely why persisting the realized policy matters more than the
values** — and `train_fullevent_nominal.py:602` already persists `seed_policy` read off `argv` rather than
the module default, so a varied-seed run records what it actually did rather than what it was supposed to.

## THE MEMBERS, fixed here

Five members. Each varies **both** seed axes together:

| member | `--estimator-seed` | `--subsample-seed` |
|---|---|---|
| 1 | 42 | 0 |
| 2 | 43 | 1 |
| 3 | 44 | 2 |
| 4 | 45 | 3 |
| 5 | 46 | 4 |

**Member 1 is the promoted nominal's own policy** (`estimator_seed 42`, `subsample_seed 0`), so the ensemble
contains the adopted estimator rather than five neighbours of it.

**"Crossed" here means five independent members varying initialization and subsample TOGETHER, not a
factorial scan.** A factorial cross of five values on two axes is 25 members, which is not what `N = 5`
means and is not authorized. Stated because "crossed" admits both readings and the ambiguity would be
resolved after the fact otherwise.

**Everything else is held at the promoted configuration:** `niter 3`, `epochs 8`, `batch_size 512`,
`train_events 2,000,000`, the annealed LR policy, and the **promoted Gate-2 target** — no Poisson
fluctuation, per Gate 6's own text. Each member writes to its own output directory; the driver refuses to
overwrite a finished artifact and that guard is not to be bypassed.

## THE CRITERION — predeclared, with a measured floor

The deliverable is the ML-ensemble covariance component, centred on the **ensemble mean**, compared against
the GPU floor as Gate 6 requires.

**The floor is measured, not assumed.** The annealed run's matched same-seed repeat gives a production
same-path scatter of **`1.26775e-4`** in fold-forward deviation (`56563761`, nominal `1.0840529523112135`
against matched floor `1.0841954572741048`). That is the reproducibility floor of this configuration.

**Branch PASS** — all 5 members complete; all realized seeds persisted; and the member-to-member spread
**exceeds** `1.26775e-4`, so the ensemble is resolving estimator variation rather than repeat noise. The
component is then computed centred on the ensemble mean.

**Branch UNRESOLVED — and this is a real outcome, not a failure to be re-read as PASS.** The spread is at or
below `1.26775e-4`. Then the ensemble has **not** measured an ML component; it has measured the floor, and
the honest statement is *"below the reproducibility floor of this configuration at N=5"* rather than
*"the ML component is zero"*. **A component reported as small because the instrument cannot resolve it is
not a small component.**

**Branch BLOCK** — any member fails, any member's persisted `seed_policy` disagrees with the argv it was
launched with, or any member consumes a target other than the promoted Gate-2 target. Then the ensemble
manifest is invalid and no component is reported.

**Materiality floor:** no difference below `1.26775e-4` is claimed as an effect, whichever branch fires.

**Read on the realized `seed_policy` persisted by each member, not on the launch command.** The two can
differ, and only the persisted record is evidence — the same discipline that made `56818470`'s reading
depend on `end_to_end_*` rather than the field a ledger row happened to quote.

## Cost, measured

One member is one full-event training: **6:00:36** wall, 32 CPU + 1×A100, 1 node (`sacct` on `56563761`).
**Five members ≈ 30 GPU node-hours**, no CPU target builds — Gate 6 uses the existing promoted target and
therefore needs no per-replica ROOT job, which is what distinguishes it from Gate 5.

## HELD, not launched

**No member is submitted until Session C reports on input integrity.** The scratch inputs are ~24% smaller
than the current open-data files of the same name (three of three checked, ratio 1.243–1.244), and the
download path does a straight `xrdcp` with no skim step — so either the scratch copies are a valid older
production or they are truncated. **Gate 6 trains on those same inputs.** 30 GPU node-hours is a smaller
bill than Gate 5's ~300, but it is the same category of waste, and the mediator's own instruction is that
Gate 6 stops too if C returns "truncated". Predeclaring now costs nothing and is unavailable later; the
launch waits.

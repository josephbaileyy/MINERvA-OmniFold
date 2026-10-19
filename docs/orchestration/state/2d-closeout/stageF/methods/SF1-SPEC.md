# SF-1: does the null distribution depend on the unfolding-simulation size? (specification and grant, frozen before any run)

**Owner:** the paper-tighten lane, as director (Stage F), 2026-10-19. This is methods-paper item M2 (calibration
fidelity, referee comment 6), under
[`DECISION-20261019-joseph-methods-first-and-measurement-compute`](../../../../DECISION-20261019-joseph-methods-first-and-measurement-compute.md)
§1, which approves compute for "the methods-paper items that need computation".
The audit that motivates it is [`M2-AUDIT.md`](M2-AUDIT.md) Q4.

**CITABLE FOR:** what SF-1 measures, its acceptance rule and failure branch, and its compute grant.
**NOT CITABLE FOR:**
- any result before its report exists;
- a test of the data process itself (that needs an independent simulation sample, which is not available);
- any change to the s5p decisions or to amendment 7. SF-1 is a separate, report-level study; any change to a claim
  is Joseph's.

## 1. Question

The calibration pseudo-experiments unfold with half the simulation, while the data unfold with all of it. Only the
mean of that difference has been measured, in a noise-free process without nuisances (amendment 6, F4: 0–0.068
null SD along each null's bias direction). Does the whole null distribution of the test statistics change with the
unfolding-simulation size, in location, scale or tail, by enough to move any of the three shape decisions with the
smallest margins?

Those three decisions are NuWro shape (2.8 null SD), GENIE CV shape (4.5) and GENIE+MEC shape (4.9). The other
seven decisions have margins of 5.7–207 null SD.

## 2. Design

- **Runs.** For each null N ∈ {NuWro 21.09, GENIE CV, GENIE+MEC}: rerun `nd-unfolding/s5p_nullexp.py` with
  `--mc-fraction quarter` and nuisances on, for the first 200 seeds of N's production calibration ensemble.
  - The code and inputs are those of the production products.
  - Same seed, so the same split key, pseudo-data and nuisance draws.
  - The only change is that the unfolding uses half of half A (`s5c_pseudo.half_mask` at key split + 7777).
- **Pairing.** Each quarter product is paired with the production (half) product of the same seed.
- **Statistics.** T_tot and T_shape are computed by the production code path (`s5p_joint.py` `statistics`), with
  the same frozen V, the same additive draws (same `surrogate_seed0` and seed indices) and the same domain, on the
  variant c = 0.

## 3. What is measured (per null, per statistic)

From the 200 pairs, with 95% intervals from a paired bootstrap over seeds (10,000 resamples, fixed RNG seed 20261019):
- the median shift, Δ = (median_q − median_h)/SD_h;
- the scale ratio, s = SD_q/SD_h;
- the ratio of the 95th and 99th percentiles, quarter over half;
- the paired-difference distribution of T_q − T_h.

## 4. Acceptance rule and failure branch (frozen)

**Extrapolation (assumed, and stated as such).** Going from half to full simulation is taken to change the null
distribution by at most the measured half-to-quarter change, applied in the direction opposite to the step:
location −Δ, scale 1/s.

Under a 1/n law the half-to-full change would be half the half-to-quarter change, so this is conservative by a factor
of about 2 under that law. No law is assumed beyond that.

**Adjusted ensemble.** For each of the three shape tests, the production claim ensemble (all variants, B as
reached) is transformed: each null draw's T becomes median_h + (T − median_h)/s_lo − Δ_lo·SD_h. Here s_lo and Δ_lo
are the lower ends of the 95% intervals of s and Δ. These are the ends that make the adjusted null higher and wider,
which is the direction adverse to a rejection. The test's claim
p and its Holm/Clopper–Pearson decision are then recomputed with the production rule, the observed statistic
unchanged.

**Outcomes:**
- **PASS** for a test if its decision (reject) is unchanged under the adjusted ensemble. The methods paper may then
  say that the decision is robust to the unfolding-simulation size within the measured half-to-quarter change.
- **FAIL** if the decision becomes undetermined or not rejected. The methods paper must then say that the decision is
  not robust to calibration fidelity at that level. Whether the claim is narrowed is Joseph's decision; SF-1 itself
  changes no claim.
- **Reported in every case**, with no further pass/fail: Δ, s and the percentile ratios for both statistics, and the
  same numbers for the total tests of the three nulls.

**No re-runs.** If more than 10% of a null's 200 runs fail to produce products, the shortfall is reported and the
statistics use the products that exist. There is no second set of seeds.

## 5. Grant

- At most **25 charged CPU node-h** on `m3246`, regular QOS, never premium. Recorded cost is 0.024–0.031 node-h per
  pseudo-experiment, so 600 runs are 15–19 node-h.
- Each job under 12 h.
- Outputs under `/pscratch/sd/j/josephrb/methods-paper/sf1-20261019/`, and nothing written to CFS.
- Every job id with its `sacct` charge is ledgered in the SF-1 report.
- If the charge reaches 25 node-h, the study stops and reports what it has.

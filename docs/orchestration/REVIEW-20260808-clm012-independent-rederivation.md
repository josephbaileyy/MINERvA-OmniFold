# Independent re-derivation of CLM-012: arithmetic confirmed, reasoning corrected in five places

**Date:** 2026-08-08 · **Condition (d)** of Joseph's CLM-012 instruction: *"Get one independent
re-derivation before promoting past VERIFIED-NUMERIC. It's single-source and your own rule says worker
agreement isn't verification."* · Reviewer: independent read-only delegate, given the committed report and
acceptance map and asked to reproduce four numbers with its own arithmetic and to attack the prose.

## Verdict up front

**The arithmetic is confirmed — all four numbers to display rounding (≤6e-7).** The 285-cell alignment is
sound, both `bin_order` strings are byte-identical, both artifacts pin the same input sha, and the headline
finding is not void.

**The reasoning had two real defects and three overstatements. I accept all five and partially contest one
further objection.** CLM-012 stays `VERIFIED-NUMERIC` — this review does not promote it, and two of the
corrections below weaken the grounds on which I had called it decision-grade.

| # | objection | my disposition |
|---|---|---|
| B | §2's "algebraic identity" claim is **false** and double-counts against §4 | **ACCEPT — real defect** |
| i | "predicts to 0.19 pp" is budget-contingent; the ladder is the counterexample | **ACCEPT — real defect** |
| ii | per-cell bands show transport gain is large and measured, not absent | **ACCEPT — strengthens caveat (i)** |
| iv | the "28.2% estimator" bucket is ~98% scatter penalty, not response deficit | **ACCEPT — material refinement** |
| v | "reads as a round number" is unsupported and probably wrong | **ACCEPT — and it improves the finding** |
| vi | the ceiling is a property of (detector × injection), not the detector | **ACCEPT — governance issue for the re-specification** |
| iii | the 72% picks the favourable bracket end | **PARTIALLY CONTEST — see §3** |

---

## 1. The two real defects

### B. I claimed an algebraic identity that is not one, and it double-counts

I wrote, in `FINDING-20260807-d2-acceptance-limited-oracle.md` §2:

> *"This is why `d2_response_decomposition.py`'s 'zero dispersion' column (0.6313) and BEN-038's dilution
> ideal (0.63321) agreed — not a coincidence, an algebraic identity."*

**That is false.** Verified in the code: `rec_if_zero_dispersion = 1.0 - coherent` with
`coherent = abs(1.0 - E_r)`, and `E_r` is the **estimator's** mean response. So that column is
`1 − |1 − 0.631286| = 0.631286` — the estimator's own `E_w[r]`. The dilution ideal is `0.633208`. They are
different objects and their agreement is the **empirical −0.001922 bias**, not an identity.

The genuine identity is narrower: *within a single construction*, zero-dispersion recovery equals that
construction's own `E_w[r]`. That explains why my spectrum-space oracle equals the dilution mean response
(same construction). It says nothing about the estimator matching the model.

**And the reviewer's sharper point is the one that matters: this is a double-count.** §2 declared the
0.6313 ≈ 0.63321 agreement trivially algebraic, while §4 and CLM-012's caveat (iii) rested the entire
decision-grade status on *that same agreement* being a meaningful empirical bridge, and caveat (ii) called
it "one confirmed non-trivial prediction." It cannot be both. The sentence is removed.

The reviewer also notes the equality needs **two** steps and I named one: (i) spectrum-space recovery
`= 1 − E_w[|1−r|]` for *any* per-cell response, by L1 factorisation through `w_b`; (ii) one-sidedness then
collapses that to `E_w[r]`. Correct, and it also makes clear that "an identity fell out" oversells what is,
for `r_dil = 1 − (1−a_b)^k` with `a_b ∈ [0,1]`, algebraically guaranteed.

### i. "Confirmed to 0.19 pp" is budget-contingent, and my own ladder is the counterexample

I called the dilution model "an assumed model with one confirmed non-trivial prediction" on the strength of
`E_w[r] = 0.631286` versus the curve's `0.633208`. But from the same finding's own table:

    ep8  (gate)  0.63129     ep8 (ctl8)  0.63250     ep16  0.56324     ep32  ~0.5235

So the estimator's mean response moves **6.9 pp** on doubling the budget and ~**11 pp** at 4×. The honest
statement is: *the estimator happens to sit at its dilution ceiling at ep8, and sits well below it at ep16
and ep32.* That is not a confirmation of the model — the model predicts a **ceiling**, and the agreement is
between that ceiling and a **contingent** estimator value. I used the ladder to kill the under-training
hypothesis and then, in the same document, used the ep8 agreement as model validation without noticing the
ladder refutes its stability.

**Consequence:** CLM-012 caveat (ii) is downgraded from "one confirmed non-trivial prediction" to "agrees at
one point of a curve whose shape it does not predict," and caveat (iii)'s "the curve is where this estimator
actually operates" is narrowed to "at ep8/seed42/k=3 only."

---

## 2. Three overstatements, all accepted

### ii. Transport gain is large and measured — "no net gain" is true and empty

The reviewer's per-cell band table (independently reproduced, and consistent with BEN-038's):

| `a_b` band | weight share | `E_w[r_est]` | `E_w[r_dil]` | bias |
|---|---|---|---|---|
| [0.00, 0.01) | 0.2316 | 0.1525 | 0.0082 | **+0.1443** |
| [0.01, 0.10) | 0.0636 | 0.2840 | 0.0981 | **+0.1859** |
| [0.10, 0.30) | 0.0746 | 0.3603 | 0.4933 | −0.1330 |
| [0.30, 0.50) | 0.1252 | 0.5340 | 0.7845 | −0.2505 |
| [0.50, 0.70) | 0.1922 | 0.8376 | 0.9378 | −0.1002 |
| [0.70, 1.01) | 0.3127 | 1.0333 | 0.9905 | **+0.0428** |

The two lowest bands carry **29.5% of the displacement weight** and beat their own dilution ceiling by +0.14
and +0.19 — the lowest by a factor of **18.6×**. Weighted `E_w|r_est − r_dil| = 0.1949` against a signed mean
difference of `0.0019`: the aggregate agreement is **100× smaller than the typical per-cell deviation**.

So cross-cell transport is not hypothetical, it is large; it is cancelled by a −0.25/−0.10 undershoot in the
mid-acceptance bands. **"No net transport gain" is literally true and analytically empty.** The correct
statement is that gain and undershoot cancel at ep8 in this weighting, via a cancellation with no reason to
be stable — which is exactly objection (i) again. This *strengthens* caveat (i): the curve is not merely
"not a bound," it is **demonstrably violated on 30% of the weight**.

BEN-038 already recorded the top band at 1.0333 and low-acceptance cells beating their ceiling 19×. I cited
that as a caveat and then leaned on the aggregate bridge anyway. That is under-using evidence already in the
ledger.

### iv. The "28.2% estimator" bucket is ~98% scatter penalty, not response quality

Verified: `ceiling − measured = 0.086355`, of which the scatter penalty is `0.084433` = **97.8%**, leaving a
response deficit of `0.001922` = 2.2%.

So the shortfall I have been calling "the estimator's own deficiency" and "unexplained" is, specifically,
**the criterion's per-cell absolute value charging deterministic per-cell dispersion**. It is *located*, not
unexplained: the signed response is essentially at ceiling and the loss is dispersion. What remains genuinely
unexplained is why the dispersion is that large — and my earlier work already showed it is not reducible by
budget, seed, or iteration count.

**This matters for Joseph's instruction** that re-specifying must not make the 28.2% invisible. It makes it
*more* specific, not less: the open item should read "per-cell dispersion charged by the L1, signed response
at ceiling," not "unexplained." BEN-038's own rule is to split signed response from scatter **before**
diagnosing; §1 of my finding did not, and it is the section a reader quotes.

### v. "Reads as a round number" is unsupported — and the truth is better for the finding

From the acceptance map's own global value: `1 − (1 − 0.42351622)^3 = 0.808415`, i.e. **0.0084 above the
0.80 bar**. That is too close to be coincidence. The likely history is that 0.80 **was** derived from an
achievability argument — the **scalar-scope** one, using global acceptance, which the map itself flags as
overstating differential recovery by +19.9 pp (`recovery_field_scope_note`, and CLM-011's Jensen finding).

So my rhetoric was wrong in a way that *improves* the substance: the defect is not "nobody derived the bar,"
it is **"the bar was derived with a Jensen error."** And the reviewer's corollary is the sharpest line in the
review: *under the scalar reading the bar sits below the ceiling and CLM-012 is false.* The claim therefore
hinges entirely on the per-cell/Jensen correction — which is exactly what makes the correction the finding's
real contribution rather than an aside.

### vi. The ceiling depends on the injection, which is a governance problem for the re-specification

The same 285 cells give, at k=3: truth-mass `0.609475`, prior-mass `0.609523`, untilted-mass `0.609625`,
**tilt-displacement `0.633208`**, uniform-over-live `0.776110`. And under synthetic re-injections from the
report's own block: amplitude −0.35 → `0.611760`, +0.35 → `0.628361`, +0.70 → `0.642253`.

So the ceiling moves ±2 pp with the injected shape. My §5 phrased `0.633` as a detector fact. **It is a
property of (detector × injection × weighting).** For the re-specification Joseph is deciding, this is not a
footnote: a criterion whose bar is computed from the probe must recompute the ceiling per injection, and pin
the injection alongside `k` and the acceptances. Added to the predeclaration's adoption conditions.

---

## 3. The one objection I partially contest

**iii. "The 72% picks the favourable bracket end."** The reviewer is right that I advertised a bracket
`[0.618228, 0.633208]` and then decomposed using only the lower end, which maximises the specification share
(71.8% vs 65.9%).

**But the choice is defensible on matching grounds, and I failed to say so.** The criterion computes
`recovery` with the A/B sampling difference *in it* — `h_unfolded` from half B against `h_target` from half
A. My per-event oracle is built the same way, so `0.618228` is the **matched** ceiling and `0.633208` is a
sampling-free idealisation. Comparing a sampling-charged measurement against a sampling-free ceiling would
understate the specification share, not overstate it.

**What I accept:** advertising a bracket and silently using one end is the pattern an auditor should flag,
and the fix is to justify the end rather than to average. The finding now states the matching argument and
carries **66% as the sampling-free alternative**. I do not accept relabelling the headline "66–72%", because
that presents an unmatched comparison as equally valid.

The reviewer also notes that "the 0.014980 difference **is** the sampling term" is asserted rather than
demonstrated — the per-k offsets are 0.0144, 0.0117, 0.0150, 0.0188, 0.0216, 0.0238, roughly stable but not
constant. **Accepted as stated too strongly**; "is consistent with" replaces "is".

---

## 4. Provenance gaps the reviewer could not close, recorded so they are known

- **`0.618228` — the load-bearing number — is not verifiable from committed files.** It needs
  `POWERED_CLOSURE_ARTIFACT.slurm-56381674.npz` and the 9.9 GB dump, both on purgeable `/pscratch`. Of the
  five numbers, it is the one no offline reader can check, and the 71.8% headline rests on it. Same for the
  per-event k-curve and for `d2_oracle.py`'s `0.954204`.
- **Gate 1's "≤2.2e-9"** is an observed value; the code's tolerance is `TOL = 1e-7` and nothing committed
  records the 2.2e-9. The reviewer verified the weaker but real statement that the report's metrics are
  internally consistent with its own committed histograms to ~1e-16.
- **ep32's "+29.7%"** has no committed artifact — the probe products live on scratch. It is stated as
  measured fact in §5 and the "not more epochs" recommendation leans on it.
- **`R = 1.1240802949941018`** does not appear in the report JSON; for this run it is sourced from the
  artifact's target metadata and hardcoded in three of my scripts.
- **Gate 2's tolerances are loose:** `5e-4` absolute on `0.63` is ≈0.08% relative, which would pass a value
  0.0005 wrong — **2.6× the entire 0.19 pp signal the gate exists to protect.** Not vacuous, but not tight
  either, and worth tightening if that comparison is ever load-bearing again.
- **Two support inconsistencies**, immaterial but undocumented: cell 228 has `a_b = 0` yet `w_b > 0`; cells
  251/252/253/284 carry truth mass in the map but are identically empty in all four report spectra.
- **`w_b` is not pure injection displacement** — `h_prior` is half B while `h_target` is half A, so `gap`
  carries the 4.59% A/B sampling difference. Re-deriving with the sampling-cancelled weight
  `|h_target − h_untilted|` gives `0.632655` versus `0.633208`: a −0.055 pp shift that **strengthens** the
  number. Worth one sentence so a reader who notices the contamination does not assume the weights inherit it.
- **`a_b` is a reco *efficiency*** (the map says so, and KNOWN_ISSUES records the extractor wrongly dividing
  by it) while the dilution model reads it as "the visible fraction of a truth cell." The reviewer
  cross-checked and they agree to **+0.054%** (`837494/1999920 = 0.418764` vs the map's `0.418539`), so the
  reading is right — but nobody had checked.

## 5. What this changes

- `FINDING-20260807-d2-acceptance-limited-oracle.md` — §2's false identity sentence removed; the two-step
  derivation stated; §3 carries the Jensen-derivation account instead of "round number"; §1 carries the
  bracket-matching argument and the 66% alternative; §5's ceiling described as (detector × injection ×
  weighting).
- `CLAIMS.md` CLM-012 — caveats (ii) and (iii) downgraded per §1; new caveat on injection-dependence; the
  28.2% re-characterised as ~98% scatter penalty.
- `PREDECLARATION-20260808-…` — the injection must be pinned alongside `k` and the acceptances; the
  "unexplained" wording in the criterion text corrected.
- `docs/OPEN_ITEMS.md` item (d) — same re-characterisation.
- **CLM-012 remains `VERIFIED-NUMERIC`.** One independent re-derivation confirms the arithmetic; it does not
  promote a claim whose reasoning it corrected in five places.

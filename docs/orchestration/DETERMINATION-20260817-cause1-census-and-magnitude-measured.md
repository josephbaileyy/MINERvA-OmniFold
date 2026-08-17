# DETERMINATION — cause 1: the census is complete and the magnitude now exists. All four legs have content; the discharge is ROUTED, not declared.

**Lane E, 2026-08-17.** Predeclared at `a2a3a8a`
([`PREDECLARE-20260817-cause1-endpoint-census-and-magnitude.md`](PREDECLARE-20260817-cause1-endpoint-census-and-magnitude.md)),
measured against that commit, written after. **Branch C1.** **Adopts nothing.** `docs/analysis-note/`
untouched, not one character; `values.tex` untouched; no ROOT modified; no covariance rebuilt.

---

## THE ONE PARAGRAPH

`CRITERIA` §2 cause 1's `M` leg says of the one-sided-vs-mean-centered magnitude: ***"This number does
not exist anywhere."*** **It exists now.** Rebuilding X's systematic budget from its own 188 universe
vectors — and reproducing all eight committed summary numbers first, as a positive control — the retired
one-sided CV-centered construction would have given **√Tr `4.610136e-38` (×1.0594) or `4.487828e-38`
(×1.0313)** depending on which endpoint is taken, against the as-built **`4.351483e-38`**, and would have
moved the per-bin median from **13.2346%** to **14.8405%** or **15.7383%** — **+1.6 to +2.5 percentage
points, i.e. +12% to +19% relative.** The per-band census is complete: **42 ± pairs, every one with both
endpoints, `Flux` exactly 100 contiguous.**

**So `P` is MET and `M` is measured on X's own inputs, reported as a distribution.** With `C` and `T`
already MET and both re-derived here, **cause 1 now reads four METs, which by `CRITERIA` §0 is the
discharge condition.** **I am not declaring it.** That is the same posture Session B took on cause 2 and
for the same reason: declaring a discharge of the 2026-07-12 quarantine has publication consequences and
is not the measuring lane's call. **Routed.**

---

## 1. The positive control, which is what makes the rest readable

The reconstruction **imports production's own `load_flat`, `UNI_RE` and `category_for_band` from
`analyze_universes_5d`** rather than reimplementing them, so a discrepancy cannot be my parsing. It then
had to reproduce eight committed numbers from
`nd-unfolding/uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_summary.txt` before any counterfactual was
allowed to mean anything (branch **C2** was declared to void the comparison on any failure):

| quantity | committed | reconstructed | |
|---|---|---|---|
| reported bins | `10694` of `65856` | `10694` of `65856` | ✓ |
| total syst √Tr | `4.3515e-38` | `4.351483e-38` | ✓ |
| total syst median rel | `13.235%` | `13.23461%` | ✓ |
| `Flux` sum √Tr | `3.993e-39` | `3.992673e-39` | ✓ |
| `Models` sum √Tr | `8.964e-38` | `8.963974e-38` | ✓ |
| `Normalization` sum √Tr | `4.507e-39` | `4.507039e-39` | ✓ |
| `Hadronic response` sum √Tr | `4.017e-38` | `4.016568e-38` | ✓ |
| `Muon reconstruction` sum √Tr | `2.789e-38` | `2.789261e-38` | ✓ |

Tolerance `5e-4` relative, **stated with its derivation**: the summary prints 4 significant figures and
`5e-4` is half a unit in the last printed place. Not a fitted tolerance.

Run on Perlmutter `login08`, `rc=0`, **no batch job**; whole stream to
`/pscratch/sd/j/josephrb/lane-e/c1.out` and filtered on read (BEN-026). Reader
`nd-unfolding/receipt_cause1_endpoint_census_5d.py` sha256
`0bb03405f7db839a1bd4e26d3bc767c8e9c6c8d62fd6a28f1e947adee5cec704`, **verified equal on both sides of the
copy.** Receipt: `nd-unfolding/uq_5d/receipt_cause1_endpoint_census_5d.json`.

## 2. `P` — the per-band endpoint census, which did not exist

44 bands over 188 files. **Every one of the 42 ± pair bands has both endpoints present** (indices `[0,1]`),
and **`Flux` has exactly 100 at indices `0…99`, contiguous.** Two entries are not pairs and are recorded
as such rather than smoothed over:

* **`2p2h` has N=3** (indices `0,1,2`). It is **not** a ±pair. Declared as an unknown *before* measuring
  (predeclaration §4) and **excluded from the counterfactual**, carried unchanged in both totals.
* **one `…_uni_full_CV.root`** carries no numeric index, so production's `UNI_RE` does not match it and
  it contributes to no band. It is reported in the receipt as `skipped_files_not_matching_UNI_RE`, because
  a file the instrument ignores is exactly the thing a census must name.

**The `P` leg's criterion — *"both ± endpoints present for every band and an exact contiguous
100-universe flux bank"* — is satisfied, and now by a committed artifact rather than by a passing check
nobody kept.**

## 3. `M` — the magnitude, as a distribution and not a max (BEN-064)

Diagonal-only **by sufficiency**: trace and per-bin σ depend only on the diagonal, so no 10,694² matrix
was formed. **This says nothing about off-diagonal structure and no such claim is made anywhere.**

| construction | √Tr | ratio to as-built | per-bin median rel |
|---|---|---|---|
| **as-built** (mean-centered, biased `1/N`) | **`4.351483e-38`** | 1 | **`13.2346%`** |
| one-sided CV-centered, endpoint `0` | `4.610136e-38` | **`1.059440`** | `14.8405%` (**+1.61 pp, +12.1% rel**) |
| one-sided CV-centered, endpoint `1` | `4.487828e-38` | **`1.031333`** | `15.7383%` (**+2.50 pp, +18.9% rel**) |

**Both endpoints were computed rather than trusting a comment.** `unified_throw_cov.py:52-53` says
`idx 0 = −1σ, idx 1 = +1σ`, but that is a comment in a different module, so the predeclaration required
both. They disagree — and interestingly **not in the same direction**: endpoint `0` gives the larger
√Tr while endpoint `1` gives the larger per-bin median. **The choice of endpoint is itself worth ~2.7% of
√Tr**, which is a second reason the one-sided form is objectionable and one no single-endpoint calculation
would have shown.

**Per-band trace-ratio distribution over the 40 pair bands with a non-degenerate denominator:**

| | min | p25 | median | p75 | p90 | max | >1 | <1 |
|---|---|---|---|---|---|---|---|---|
| endpoint `0` | `0.6377` | `1.2338` | **`2.0261`** | `2.6318` | `4.3256` | `5.8024` | **35** | 5 |
| endpoint `1` | `0.6111` | `1.0610` | **`1.6797`** | `2.8224` | `3.9487` | `8.6838` | **34** | 6 |

**So *"one-sided overstates"* is true in aggregate and NOT universally** — the median band is inflated
~1.7–2.0×, but 5–6 bands of 40 are *understated* (`MaCCQE` ep0 `0.6377`, `MaRES` ep1 `0.6111`,
`LowQ2` ep0 `0.8012`). A per-band bound taken from the aggregate direction would be wrong for those.

### 3a. The two bands excluded from the distribution, and why excluding them is not a convenience

`EtaNCEL` and `NormDISCC` have as-built √Tr of `4.187e-45` and `8.043e-51` — **five and eleven orders
below the smallest real band** (`FrPiProd_N`, `6.354e-40`). The gap is unambiguous, so the `1e-42` cut is
a statement about the data and not a tuned threshold. Their ratios are `9.3e10` and `2.5e22`; **reporting
a max of `2.5e22` would be a true number that means nothing**, and it is why BEN-064's *"distribution not
a max"* needs a companion rule: **a ratio is the wrong statistic when the denominator is a measured zero,
and the distribution must disclose its denominators.**

**They are the cleanest demonstration of the defect in the whole measurement, and it is absolute rather
than relative.** Both knobs have genuinely **no** systematic effect — their ± unfolds agree to numerical
zero. The one-sided form assigns each of them **`1.279e-39` of variance, fabricated out of nothing.**

### 3b. Why one-sided inflates, measured rather than asserted

`EtaNCEL_0/1` and `NormDISCC_0/1` all sit at **exactly the same distance `1.2793e-39`** from the CV used
for centering, which is not a coincidence:

```
||sweep CV unfold  −  products/5d CV||            = 1.7054569831625e-39
max| sweep CV − products CV | / max CV            = 0.9055 %
control: MaCCQE_0 is NOT the sweep CV             ||MaCCQE_0 − CV|| = 7.920e-39
```

**There is a ~0.9% common baseline offset between the sweep's unfolds and the CV file used to centre
them.** Mean-centering cancels it exactly — it is common to both endpoints of every pair, and to all 100
flux universes. **CV-centering does not: it converts that common offset into a spurious rank-1 term in
every band.** That is precisely the mechanism `CRITERIA` §2 names (*"the CV-centered form adds a spurious
rank-1 term that mean-centering correctly kills"*), now measured on X's own bank with its source
identified.

**Consequence, stated so it is not over-read: X AS BUILT IS UNAFFECTED.** The offset cancels in the
construction that was actually used. It matters only to the counterfactual. **Whether a 0.9% baseline
offset between the sweep unfolds and the CV file is itself worth investigating is a separate question
about the sweep, it is not cause 1, and it is not mine — flagged for the owning lane.**

## 4. `C` and `T`, re-derived rather than inherited

**`C`.** `CRITERIA` §3 grades it MET citing **`(§4.8)` — a section that does not exist**; §4 of that
document runs 4.1 through 4.7. **The audit is nonetheless real**, and better than the criterion asked
for: it is committed as executable tests (`Cause1PathAuditTests`), not prose. **This is a citation defect,
not a missing audit**, and the distinction only survived because the search was covering. It is the second
dangling pointer in this document class — §4.4 is *itself* the finding that *"the only predeclared
discharge criterion any of these five causes has is cited by a line number that no longer contains it."*

**`T`.** Four mutations in an isolated worktree, restored and `git diff HEAD` verified empty after each:

| # | mutation | result |
|---|---|---|
| **M1** | drop mean-centering at `analyze_universes_5d.py:97`, the site that actually built X | `test_analyze_universes_5d_band_covariance_is_mean_centered_and_biased` **FAILS** — criterion (i) |
| **M2** | rename `uq_math.mat_covariance` | **two** tests FAIL, one with *"uq_math.mat_covariance has disappeared"* — **fails rather than skipping vacuously**, criterion (ii) |
| **M3** | `import pet_systematics_5d` into `analyze_universes_5d` | `test_no_pet_module_is_on_X_build_path` **FAILS**, and the outer-product guard fires too, surfacing `pet_systematics_5d`'s one-sided sites |
| **M4** | **one comment line, zero semantic change** | `test_the_only_outer_product_on_X_path_is_the_documented_norm_band` **FAILS** — see §5 |

**Both directions the criterion requires are verified, so `T` is MET.** M4 is a *robustness* defect, not a
power defect, and I am deliberately not letting it weaken the leg — overstating it would wrongly block a
discharge. Full suite **35/35** with the tree restored.

## 5. The one new defect found, and why I am not fixing it

`test_the_only_outer_product_on_X_path_is_the_documented_norm_band` asserts

    self.assertEqual(found, ["analyze_universes_5d.py:109"])

— an allow-list keyed on **`file:line`**. **M4 shows a single added comment line, with no semantic change
of any kind, turns it red** (`['analyze_universes_5d.py:110'] != ['analyze_universes_5d.py:109']`).

**This is a false-positive generator on a guard whose true positives matter**, and the damage is the
familiar one: a check that goes red on innocent edits trains its reader to wave it through, and the next
red might be a real one-sided `np.outer`. It also fails the pre-commit dispatcher's own admitting rule —
*"a check belongs here iff a committer who did nothing wrong can always make it pass"* — so it could
never be promoted into the hook as written.

**Proposed one-line fix, not applied:** key the allow-list on the enclosing construct rather than the
line, e.g. match the source segment `np.outer(v, v)` inside the `add_norm` block, or compare
`(module, normalized_source_line)` instead of `(module, lineno)`.

**Why I am not applying it: I should not both grade a leg and modify the instrument that grades it.**
That is the separation `personal` invoked in routing cause 3's and cause 4's `M` judgements to a peer,
and it applies with more force here, because the guard I would be editing is the `T`-leg evidence for the
cause I am reporting on. Routed. `BEN-381`.

## 6. Where cause 1 stands — the arithmetic, and the thing I am not doing with it

| leg | before | now |
|---|---|---|
| **C** code | MET *(pointer dangling)* | **MET** — re-derived by M1 and M3; pointer corrected to where the audit lives |
| **P** provenance | **PARTIAL** — *"no committed per-band endpoint census"* | **MET** — the census exists and is committed |
| **M** magnitude | **OPEN** — *"this number does not exist anywhere"* | **MEASURED on X's own inputs, as a distribution** |
| **T** test | MET | **MET** — both required directions re-verified (M1, M2); a robustness defect filed separately |

**`CRITERIA` §0 is explicit that a measured large difference discharges `M` as well as a measured small
one — *"what is forbidden is an unmeasured one"*. On the letter of §0, cause 1 now reads four METs, which
is §0's discharge condition.**

**I am not declaring it, for one reason and it is not hedging.** Session B reached exactly this position
on cause 2 — four METs — and routed rather than declared, writing that *"declaring the first discharge of
the 2026-07-12 quarantine is a decision with publication consequences and is not a session's call to make
at the end of its own work."* **That reasoning does not weaken because the lane changed.** The specific
question a decider needs to answer, stated so it can be answered without re-reading this document:

> **Does a `+3.1%`/`+5.9%` √Tr difference with a `1.7–2.0×` median per-band ratio constitute `M` MET
> under §0's *"measured, not necessarily small"* rule — or does a difference this size mean the
> construction choice is material enough to need its own statement in the note?**

**That is a physics-presentation judgement. I measured the number; I am not deciding what it licenses.**

## 7. Limits

* **No cause is declared discharged here.** `P` moved; `M` moved from OPEN to MEASURED.
* **Diagonal-only.** Trace and per-bin σ are exact; **off-diagonal structure was not compared** and no
  claim about correlation structure is made.
* **The counterfactual excludes `Flux` (N=100), `2p2h` (N=3) and `__Normalization_flat`**, all carried
  unchanged in both totals, so the totals differ only through the 42 pair bands. `2p2h`'s exclusion was
  declared before measuring; its as-built √Tr is `3.361e-38`, the largest single contribution in the
  budget, so **if a decider wants the counterfactual to include it, that is a substantive re-run and not
  a footnote** — flagged rather than quietly absorbed.
* **This is about X only** — the July background-aware product the note quotes. It says nothing about the
  stamped candidate, about causes 2–7, or about adoption.
* **`CRITERIA`'s dangling `§4.8` and the line-pinned guard are other lanes' artifacts.** I added a pointer
  beside §3's table and filed `BEN-381`; **I did not rewrite their row text or their test.**

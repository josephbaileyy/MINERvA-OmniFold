# FINDING — a fraction must name **which index** its denominator is, and three parties got it wrong in a row

**Filed by:** lane C (PET), 2026-08-18. **Row:** `BEN-466`. **Cross-stream:** `OI-121`.
**Subject:** stage 0 of the `M(ii)` estimator-seed scan; two numbers of my own in
`DETERMINATION-20260818-lanec-anchor-recompute-and-lateral-in-g1.md`; and **my own correction of the first
defect, which committed the same defect a third time.**

**The stage-0 verdict is not disputed and nothing here weakens it.** Three offset pairs `(0,1200)`,
`(0,2400)`, `(1200,2400)`, all **DISTINCT**, exit 0, no `INCOMPARABLE`, estimator delta equal to the offset
delta on every row, data draw held identical. **The negative branch is closed and `M(ii)` is measurable.**

---

## 1. Three readings of one measurement, in order, and only the last is right

| # | reported by | fraction | denominator used | verdict |
|---|---|---|---|---|
| 1 | mediator | **`~16 %`** | `65,856` — the **full grid** | **WRONG.** ~84 % of the grid is empty; **a bin zero in both members cannot change**, so this measures the sparsity of the binning, not the effect. |
| 2 | **me** | **`98.25 %`** | `10,694` — the **advisory's** reported-bin count | **ALSO WRONG.** `10,694` is a *different product's* mask. |
| 3 | mediator + B, **measured** | **`100.00 %`** | **each product's OWN support** | **CORRECT.** `10510/10510`, `10507/10507`, `10508/10508` — identically on all three pairs, all nine comparisons. |

> **EVERY BIN THAT CAN MOVE, MOVED.** Not `~16 %`, not the `~98 %` I inferred — **`100.00 %`, measured**, after
> B fixed the reporter and the nine products were re-run.

**And the tell was inside the sentence I was reading.** The original report said *"changed 10,507-10,510 of
65,856 bins — remarkably stable across all nine comparisons."* **`10,507-10,510` IS THE SUPPORT SIZE.** A
"changed" count that barely varies across nine independent comparisons is not a reproducible effect size — **it
is a population count wearing the label of a measurement.** I quoted that stability approvingly and inferred a
percentage from it instead of asking why a *changed* count would be near-constant.

**A second number of the mediator's, also corrected by it:** *"`~0.6-1.2 %` relative"* was `max|delta|` **over
the peak bin**, not a per-bin relative change. **The median per-bin relative change on the support is
`5.10e-03` to `6.27e-03`** — about `0.51-0.63 %` — and it now ships beside the peak ratio so the two cannot be
confused. **I repeated the `0.6-1.2 %` figure in my own amendment without asking what statistic it was.**

## 2. The indices, and why there are at least four

| count | what it is | authority |
|---|---|---|
| **`65,856`** | the **FULL 5D grid**, `14*16*7*7*6` over `(pt, pz, eavail, q3, W)`. **Most entries EMPTY.** | `nd-unfolding/p4_lib.py:22` |
| **`10,694`** | the **GBDT full reported set** | `docs/orchestration/ADVISORY-20260813-oi30-eavail-residuals.md:286-288` |
| **`10,550`** | the **PET-COMMON subset**, and `10,550 + 144 = 10,694` exactly | `docs/orchestration/ADVISORY-20260813-oi30-eavail-residuals.md:317-321` |
| **`10,507` / `10,508` / `10,510`** | **the support of each stage-0 product** — *per product*, not a constant | measured, stage 0 |

**The mask is a predicate, not a constant, and that is the whole point.** `adopt_unified_5d.py` reads
`hXSecND_flat` — which genuinely *does* have `65,856` bins — then reduces it:

```python
xfull = np.array([h.GetBinContent(i + 1) for i in range(h.GetNbinsX())])   # 65,856
x = xfull[xfull > 0]                                                       # -> this product's support
assert x.size == n, f"reported CV ({x.size}) != throw dim ({n})"           # n = vu.size
```

> **So `vu`, `vb`, `diag_comb` and `g` are all on the support, the stored covariance is `n x n`, and `n` IS
> PRODUCT-DEPENDENT.** Any fixed literal — including the `10,694` I used — **is a claim about which product you
> meant.** That is why reading #2 failed even though its denominator was a real, citable, correct number.

## 3. Why this is its own shape, not `BEN-400` / `BEN-415` / `BEN-425`

Those are about a denominator that is unknown, unbounded, or silently smaller. **Here nothing was missing:**

- **Every index involved is correct** — as a count of the thing it counts.
- **They are already published TOGETHER, as a pair.** Production receipts carry
  **`reported_bins (10694, 65856)`** — quoted inside `BEN-429`, *this lane's own row*.
- **The warning is already written, verbatim.** `ADVISORY-20260813-oi30-eavail-residuals.md:289`:
  *"Both numbers are right; they index different things."*
- The same advisory (`:299-301`) records a scout inferring `10,550²` from a file size and being wrong — **a
  previously documented instance of this exact confusion.**

> **The pair was shipped. The warning was written. Three parties in sequence still took a numerator from one
> set and a denominator from another** — and the second of them (me) was *correcting the first*. **It is a
> reporting-form defect, not an information deficit, which is why the rule attaches to the fraction and not to
> the artifact.**

## 4. The same error twice more in my own determination

| where | claim | status |
|---|---|---|
| `§14` | R4's arrays are *"three arrays of ~285 floats"* (~2 KB) | **WRONG** — `285` is the extended-FPS `15x19` grid, a different product |
| `§14a` | *"the 5D flat length is `65,856`, so each array is `0.527 MB` — wrong by 230x"* | **ALSO WRONG**, by ~`6.2x` the other way |
| now | **the support, ~`10,510` doubles ≈ `82 KiB`** | correct, and **BETWEEN** my two figures |

**Knock-on, ruling direction unchanged and strengthened:**

```
§11h diagonal write   3 x ~10,510 x 8 B  ~=  252 KB   ~=  246 KiB     (ruled with 1.58 MB)
trade vs the released 41.44 GB intermediate  ~=  164,000 : 1           (ruled with 26,219 : 1)
```

*(Stated as an approximation on purpose: the exact figure is `3 * n * 8` for **that member's own** `n`, and
writing a literal here would repeat the defect this finding is about.)*

> **THE MECHANISM IS THE ONE `§14a` ITSELF NAMES, AND I COMMITTED IT WHILE NAMING IT:** *"a quantity true at
> its own scope quoted at another."*
>
> **I asked *"what is the 5D flat length?"* instead of *"WHICH INDEX DOES THIS ARRAY USE?"*** `65,856` is
> genuinely, checkably true of `hXSecND_flat` — **which is exactly why it survived being checked.** **A
> correction that substitutes a different wrong index is indistinguishable, from the outside, from a correction
> that worked** — and reading #2 in §1 is that failure a second time, in the act of repairing the first.

## 5. The consequence that is not bookkeeping — leg B's support was never specified

`PREDECLARATION-20260817-mii-seed-scan-cause-3.md:80-86` defines the bar's leg B as

```
f_med = median over bins of sd_i(sigma_i) / sigma_i   <=  2.74 %
```

***"over bins"* names none of the counts in §2.** Not academic: **over the full grid ~84 % of entries have
`sigma_i = 0` and `x = 0`, so the per-bin ratio is `0/0`.** The median is then either `NaN` or — if `NaN`s are
dropped anywhere in the chain — **silently the median over the support: a different statistic reached by
accident rather than by specification.**

> **RULED (before any `f_med` exists, the only legitimate moment — `BEN-403`): leg B's support is the PREDICATE
> `xfull > 0` evaluated on the MEMBER'S OWN `hXSecND_flat`, exactly as `adopt_unified_5d.py:120` does it. The
> specification names the PREDICATE, NOT A COUNT.**
>
> **1. CALIBRATION.** Leg B's `2.74 %` derives from `\gbdtFiveBlockMedian`'s 4 s.f., and that published
> `13.359 %` **is** `adopt_unified_5d.py:161`'s `100*np.median(do)` with `do = sqrt(diag_comb)/x` on the
> *masked* `x`. **A threshold calibrated to a published quantity transfers only to the same statistic.**
>
> **2. A COUNT WOULD RE-POINT** — between `10,694`, `10,550`, and each member's own `n`. **The predicate is
> checkable per member; a literal is a claim about which product you meant** (`BEN-380`). **§1 reading #2 is
> the proof that this failure mode is live and not hypothetical.**

**AND IT SETTLES A BRANCH OF MY PREDECLARATION IN THE STRICTER DIRECTION, MORE DECISIVELY THAN AT `98 %`.**
The predeclaration offers an escape: *"if the contribution is concentrated, leg B is small and leg A binds; if
it is uniform, both move together."* **At `100.00 %` of the support responding, the concentrated branch is
definitively not operative.** Leg B is fully supported and **genuinely binds**. **The bar is harder to clear
than that clause allowed** — recorded before any `f_med` exists.

## 6. What is NOT claimed

> **`0.51-0.63 %` median per-bin relative change between two offsets is NOT `f_med`,** and neither is the peak
> ratio. Those are replica-level differences between **two** members; `f_med` is the median over bins of the
> spread of `sigma_i` across **fifty** — a different object and a different estimator. **No stage-0 number
> licenses a prediction about the bar.** `n = 3` is a floor on the effect's *existence*. **Stage 1 prices it.**

Nothing here touches `C_syst`, `C_ML`, the ROOT legs, adoption, or the archive comparison.

## 7. The transferable rules

> **(i) A FRACTION SHIPS THE DEFINITION OF ITS DENOMINATOR, NOT ONLY ITS VALUE.**
>
> **(ii) Where an artifact already carries an index PAIR, quoting a percentage without naming which element it
> used is not imprecision — it is an unfalsifiable claim**, because the reader cannot reconstruct `100 %` from
> `16 %` without independently re-deriving the mask. **The pair being published is what makes the omission
> unrecoverable rather than merely terse:** with one index a reader would ask; with two, the number looks
> complete.
>
> **(iii) DERIVE THE DENOMINATOR FROM THE SAME ARTIFACT AS THE NUMERATOR.** Reading #2 failed on exactly this
> and no other axis — a correct count, honestly cited, belonging to a different product.
>
> **(iv) A COUNT THAT BARELY VARIES ACROSS INDEPENDENT COMPARISONS IS A POPULATION, NOT AN EFFECT.** The
> stability was reported as reassuring and was the diagnostic.

**Cheap executable form:** the receipts already carry `reported_bins (n, 65856)`. **A per-bin fraction quotes
against the first element and prints both.** A report that prints the pair cannot express this defect — which
is why the repair belongs in the reporter, where B put it, and not in a convention document.

## 8. `BEN-467` — the third instance, **in code this time**, and the fix for the first instance is its carrier

**Filed 2026-08-19, after lane D read the real artifacts on `origin/lane-b-member-axis-wip`.**

```python
# origin/lane-b-member-axis-wip:nd-unfolding/mii_root_payload_classes.py:37-39
#: The 5D flat length. RECORDED EXPLICITLY because C sized a per-bin array off the extended-FPS
#: 285-bin grid and was wrong by 230x; the mediator caught it. A per-bin float64 array is 0.527 MB.
FLAT_NBINS = 65856

# origin/lane-b-member-axis-wip:nd-unfolding/mii_anchor_comparator.py:171
#   "...avoids materializing a 34.7 GB matrix."       <- 65856^2 x 8 B = 34.70 GB; real size 0.915 GB
```

> **THE CONSTANT WRITTEN TO PREVENT §4's FIRST INSTANCE ENCODES ITS SECOND, VERBATIM, INCLUDING MY PROSE.** The
> comment cites the `230x` correction — **which was itself wrong** — and states *"a per-bin float64 array is
> `0.527 MB`"*, the exact figure §4 corrects. **And `FLAT_NBINS = 65856` is the GRID, while every array these
> payload classes describe is on the ~`10,694` SUPPORT** (`nd-unfolding/adopt_unified_5d.py:120-121`).

**THE RULE, and it is the one transferable thing here:**

> **A COMMENT THAT RECORDS A CORRECTED *VALUE* INHERITS THE NEXT ERROR. ONE THAT RECORDS THE *DERIVATION*
> CANNOT.**
>
> Had `:37-38` read *"derive `n` from `xfull > 0`; never from the grid — see `adopt_unified_5d.py:120-121`"*, **it
> would have been right without knowing the number.** It recorded the answer to the first question instead of the
> method, **so it was defenceless against the second** — and a comment whose stated purpose is *"recorded
> explicitly to prevent this defect"* is the last place anyone re-checks.

**AND THE PROCEDURAL HALF IS MINE.** §4 corrected the figure in the document that **originated** it. **The
executing copies are the two modules above, and those are what a future reader acts on.**

> **A NUMBER CORRECTED ONLY IN THE DOCUMENT THAT FIRST STATED IT HAS NOT BEEN CORRECTED.** *What EXECUTES versus
> what is CITED — and the unit is the callee.* **Applied to my own arithmetic one day after I wrote the rule
> down.**

### 8a. A second-order instance, caught by the check this campaign built

**My first draft of the ruling section citing those two modules used BARE repo-relative paths — and they exist
only on `origin/lane-b-member-axis-wip`.** So the citations were **unresolvable from `main`, the branch the
citing document lives on**, and `docs/orchestration/lanec_citation_resolution_check.py` failed on four of them.

> **Repaired by making each citation CARRY ITS REF**, and the checker now resolves a `<ref>:<path>` citation
> against that ref's tree, **failing closed on a ref nobody can fetch.** **An allowlist entry would have hidden
> it: the citation needed the ref, not an exemption.** *(The check's second real outing, and it caught its author
> rather than anyone else — which is the only kind of evidence that it is not merely tuned to what it already
> found.)*

# s5p Stage-6 recompute lane: independent assessment of ambiguities A6 and A8 from the governing records (2026-09-29)

**CITABLE FOR:** the recomputation lane's reading of the frozen text on A6 (how the process-shift and the sub-fine
residual variants combine in the claim rule) and A8 (the interval on which the sequential rule's T7 precision is
measured), with citations at `4f5a613f`. **NOT CITABLE FOR:** a ruling (the owner has ruled on neither), any
p-value or decision, or a change of the recomputation's primary readings, which were already the union and the
99.5% interval and are unchanged. The alternatives stay computed as labelled diagnostics
(`HANDOFF-20260928-s5p-recompute.md` §3, §3.1).

Requested by the specification owner through the s5p campaign session (relayed 2026-09-29): assess the campaign's
clarification (`CLARIFICATION-20260928-s5p-recompute-A6-A8.md`, origin/main `4a1d931c`) **from the governing
records**, not from the campaign's reasoning, and do not recommend a reading from observed p-values or from which
reading gives agreement.

## Operand state and disclosures (what I had seen when writing §1–§2)

- **No observed p-value was inspected.** My batch-0 smoke outputs on the cluster contain p-values at B = 27–47. I
  have never opened those fields, and none is quoted anywhere.
- **Production state, measured at 2026-09-29T01:27:55Z:** only the five `-B0.json` statuses exist (no statistic),
  and there is no `stage7/joint/`.
- I read the campaign's **conclusions** as summarized in the relay message ("A6 resolved by text to the UNION …;
  A8 … to precision on the 99.5% look interval …; T7's 95% is met a fortiori by nesting") before re-reading the
  governing records. §1–§2 were drafted **before** I opened the clarification document; §3 compares them
  afterwards. The assessment is therefore not blind to the campaign's position, only to its argument.
- **One line of a production evaluator body was seen, unintentionally.** While extracting docstring line numbers
  with `grep -A`, `s5p_inference.py:98` (`lo, hi = cp_interval(k, B, look_level)`) printed. It bears on A8. It is
  not used as an argument below (it shows that an interval at `look_level` is computed, not what the precision is
  measured on). No other body line of `s5p_joint`, `s5p_inference` or `s5p_seqstop` has been read.
- **Revision of my own earlier table.** `HANDOFF-20260928-s5p-recompute.md` §3 recorded A6 and A8's precision level
  as "resolved by an authoritative record? no".
  - For A8 that was an under-reading. The docstring grammar in §2 (2) was in front of me when I wrote the table.
  - For A6 the textual case is assembled here for the first time, from clauses I had cited only separately.
  - Neither revision comes from data or from agreement with production.

## 1. A6 — the claim rule's variant set: **AGREE, the text suffices for the UNION** (with a stated residual)

1. **The claim rule names two variant families, and writes the M1 members without a process-shift term.**
   Amendment 7 `claims.rejection`: *"the CLAIM p-values: the largest p over the process-shift variants
   (bias-aligned upper-bound D, c in 0, 1/2, 1) AND the sub-fine-residual variants F +- 2 delta_M1"*.
   - The maximum is taken over the members of two lists.
   - The second list's members are the calibration ensemble F shifted by ±2δ_M1, and carry no c·S term.
   - "F" is **not defined explicitly** in any governing record; this is an inference. The frozen production set
     names each external null's calibration hypothesis `ratios/nullsF/null-<g>-F.json` (`state/s5p/prod/spec.json`,
     the fine-null construction of amendment 6 F2). The confirmation review uses F ± κ·δ_M1 beside "rejected
     conditional on the fine-grid null" (`REVIEW-20260927-s5p-admission-confirmation.md:62`). Both point to F as
     the fine-null calibration ensemble itself, not the ensemble already carrying its process-shift variants.
   - A combined member F + c·S ± 2δ_M1 is written nowhere in the frozen records.
2. **The admission adopted the reviewer's variant form verbatim.** Confirmation review, required change 5
   (`REVIEW-20260927-s5p-admission-confirmation.md:62`): *"Recommended: an M1 variant F ± κ·δ_M1 inside the claim
   rule, with κ declared."* Amendment 7 then declares κ in `calibration.m1_shift` (*"kappa 2 (claim), kappa_robust 3
   (report)"*) beside the process shift's own list (`calibration.process_shift`: *"variants c in (0, 1/2, 1)"*),
   as separate lists.
3. **The size committed before the first look is that of the uncombined variant.**
   - Amendment 7 `claims.conditions_stated_with_every_claim[0]`: *"its effect enters the claim rule as the kappa = 2
     variants and its size in null-T units (with the frozen V) is committed before the first look"*.
   - The committed producer's docstring (`nd-unfolding/s5p_prefreeze.py` at `4f5a613f`, `units`) reports the sizes
     *"for delta = F2 …, M1 …, 2 M1 (the claim variant), 3 M1 (the robustness variant) and the D16 bias-aligned
     upper bound"*.
   - Amendment 7 `prefreeze_measurements.summary` lists `M1_claim_variant_in_null_sd` and `D16_in_null_sd` as
     separate entries.
   - "The claim variant" is 2δ_M1 alone. Under a cross product the claim rule would contain members whose size was
     never committed.
   - This is supportive rather than decisive: one could call 2δ "the M1 effect's size" even inside combined
     members. Reading 1 carries the conclusion.
4. **The process-shift family is defined on c·S alone.** Amendment 8 M2: *"variants c in (0, 1/2, 1) of S; the
   claim p is the largest over them"*. Amendment 7 appended the M1 family to that list; it did not redefine the c
   members.

**Residual.** The text never says in words that combinations are excluded, and it never defines "F" (point 1).
- Amendment 6 F3's rationale, *"a rejection must hold under every variant"*, could motivate combined perturbations
  as a stricter **design**, but that is an argument about what the rule should have been, not a reading of it.
- Its numerical reach is bounded. The process shift is 0.024–0.068 null SD (amendment 7 `D16_in_null_sd`) beside
  0.55–2.0 null SD for the κ = 2 variants (`M1_claim_variant_in_null_sd`). So the cross product can move a decision
  only when a claim interval lies within about that margin of a Holm threshold.
- It stays computed as the labelled diagnostic `product_reading` / `holm_product_variant_reading`, and a decision it
  would change is reported by `decisions_changed_by_product_reading`.

## 2. A8 — the interval of the sequential rule's T7 precision: **AGREE, the text suffices for the 99.5% look interval**; the closed/open boundary is **not** settled by text but is **immaterial**

1. **The admission attaches the 99.5% look interval to every condition of the stop.** Amendment 7
   `calibration.sequential_rule`: *"stops the null when s5p_inference.sequential_decision stops both (99.5%
   Clopper-Pearson look interval: no decision threshold straddled, T7 precision at the point estimate, or an upper
   end below every threshold)"*. The parenthesis names one interval, and the list after its colon gives the
   properties that interval must have. "T7 precision at the point estimate" is one of them.
2. **The function the admission names makes the same interval the subject of both conditions.** The
   `s5p_inference.sequential_decision` docstring (`s5p_inference.py:92–96` at `4f5a613f`) reads: *"stop only when the
   exact Clopper-Pearson interval of the tail probability at ``look_level`` (Bonferroni over at most ten looks:
   0.995) (a) contains no decision threshold … and (b) meets the T7 precision at the point estimate p = (k + 1) /
   (B + 1): half-width <= 0.05 …"*. Clauses (a) and (b) share one grammatical subject, so the half-width in (b) is
   that of the interval at `look_level`.
3. **T7 does not require the stop to be measured at 95%.** Amendment 1 T7 sets the reported precision on exact 95%
   intervals and allows *"a valid sequential stopping rule (Besag-Clifford) … if frozen at Stage 3"*. The frozen
   rule is amendment 7's.
   - Equal-tailed Clopper-Pearson intervals are nested in the confidence level: the 95% interval lies inside the
     99.5% one at every (k, B). I checked all 11,009 points (B = 200, 400, …, 1800, 1999; every k) and found no
     violation.
   - So a stop under the primary reading always meets T7 at 95% as well. The 95% reading can stop where the 99.5%
     interval misses the bound, which is exactly what (1) and (2) exclude. The 99.5% level is also the admission's
     stated Bonferroni protection over at most ten looks.
4. **Closed versus open containment** (*"straddled"*, *"contains"*) is not fixed by the text. It changes the stop at
   **no** attainable (k, B): the recompute's `a8-map` found zero differing k at every look size (handoff §3.1). The
   text is insufficient on this point, and the point is immaterial.

What remains computed as labelled diagnostics: `A8_alt_precision_95`, `A8_alt_open_boundaries` and
`A8_alt_precision_95_open`, with verdicts per reading (`sequential.a8_sensitivity`). A8 can bind only for a GENIE
MEC, NuWro or GiBUU stop at B ≤ 800 (handoff §3.1).

## 3. Comparison with the campaign's clarification (read after §1–§2 were written)

Read at `4a1d931c` after §1–§2 were written; §1–§2 were not revised on its account, except for the closure scan
below, which I re-ran myself.

- **Conclusions agree** on both items: A6 is resolved by text to the union, A8's level by text to the 99.5% look
  interval, and closure is not resolved by text.
- **Arguments agree in substance** on the colon reading of amendment 7, T7's nesting, the review's F ± κ·δ_M1 form,
  and the committed uncombined size.
- **Points in this assessment the clarification does not make:**
  - the docstring's shared grammatical subject of (a) and (b) (§2 (2));
  - that "F" is never defined and is identified only by inference (§1 (1));
  - the numerical bound on the cross product's reach (§1, residual).
- **Points it makes that this assessment did not:**
  - the committed size computed "as max over ±2δ_M1 alone" (`s5p_prefreeze.py:51`, a code line I did not read);
  - the frozen implementation facts (`s5p_joint.py` builds the union; the straddle test is `lo < th <= hi`). I
    record these as the campaign's statements. They are not inputs to this assessment, and **the recompute's
    primary closure stays closed [lo, hi]**; it is not changed to match.
- **Scope of my earlier closure claim, corrected.** Handoff §3.1 said open containment "differs nowhere on the
  attainable grid", but `a8-map` covered only B = 200, 400, …, 1800, 1999. A look can fall between these when seeds
  are lost. The clarification scanned B = 1..1999. I re-ran that scan myself (every k, every B = 1..1999, the twelve
  thresholds):
  - closed vs open containment changes the stop at **no** (k, B);
  - the one exact equality, B = 2, k = 2 (lo = 0.05), fails the T7 precision either way;
  - the closest endpoint-to-threshold approach for B ≥ 100 is 4.5e-9 at (B, k) = (1507, 24), the same as the
    clarification's.
  - So closure is immaterial at every B, and no ruling on it is needed.
- **A7 — CORRECTED 2026-09-29, later the same day.** The first version of this bullet said that R7(a)'s text fixes
  the κ = 3 variant set as "claim variants ∪ F ± 3δ_M1" (the ±2δ members kept), and made that set the reported one.
  That is **withdrawn**. The owner states that the ruling selected the full Holm re-run and the labels, **not** the
  variant set. No governing record at `4f5a613f` fixes it either (search and citations in
  `HANDOFF-20260928-s5p-recompute.md` §3.2). The set is open question **A7-VS**, flagged for a ruling before final
  verification. Both sets ("retain" and "replace") are computed, and a test on which they differ is reported
  UNRESOLVED.
- **A8 deadline arithmetic.** The clarification estimates the earliest first look with B > 0 near 2026-09-29T11Z
  (MEC), as a lower bound. It is not re-measured here.

**Summary: AGREE on A6 (union) and A8 (the 99.5% level), each resolved by the frozen text; the closure is not
resolved by text and is immaterial at every B.** Neither has an owner ruling. The recompute keeps its primary
readings, which already were these, and keeps the cross product and the 95% and open readings as labelled
diagnostics.

# Queued fixes from journal-editor's read of e3b99c82b (2026-11-09)

**Status:** round 6 is back, and the hold is lifted. **Applied** at this commit: A2, B1, B2, B3, B4, B5 (with D2), B6, B8,
B9 (only "partial evidence"), B10, B11 (not the 204 against 205), B12, B13, B14 (captions only), B15, C1, C2, C3, C4,
D1, D4 and D6.

**Not applied, with reasons:**
- **B9's C_total narration:** make_values LISTED_CLAIMS anchors that sentence (kind "ctotal"). Removing it means
  retiring the anchor, which I'll propose rather than do in a presentation pass.
- **B11's 204 against 205 degrees of freedom:** the COV2D outcome gives the two values (`:41`) but not why one tune
  has 204, and I didn't invent a reason.
- **B14's figure-key "exp.":** that is in the figure file. The caption now explains it.
- **Fig. 1's legend citation:** that is in the figure file too.
- **B15, in Data availability:** it is Joseph's protected text. The rater script refuses a changed first sentence, so
  the "(AnaTuples)" gloss and "Supplemental Material" go with W-19.
- **B7's C_e:** this is now W-23.

The editor's item ids are kept.

## Presentation: mine to apply after the hold
- **A2.** §7 ¶1 "agrees with it in each muon-kinematic quadrant" becomes "agrees with the two-dimensional result in
  each muon-kinematic quadrant". This corrects my own pronoun. The record (r5:208) is the comparison with this
  analysis's 2D result, not with the published one.
- **B1.** Table 1 moves to the end of §3.3, as a test map. Its Result cells are cut to the verdict plus one number
  (D1, about 250 words). "Equivalent, by 4 %" and "Step does not account …" are defined or replaced.
- **B2.** "Reconstruction stability" (the migration-diagonal fraction) is renamed and defined in §2, next to purity.
  §5.2's "low-stability cells" and Limitation 2 change to match.
- **B3.** The IBU distance ratio gets a symbol other than ρ. b and d are defined as symbols in §5.3.
- **B4.** One sentence on what differs between the two estimators. The "reproducible central value" sentence is
  rewritten.
- **B5 and D2.** The 2D covariance's construction moves to §3.2 ("The reported covariances"). §6.2 keeps only the
  calibration tests.
- **B6.**
  - How the 224 muon-momentum bins become 205 reported.
  - The cell arithmetic gets a pointer to table S2.
  - The three run-period groups are defined once, in §2.
  - "real neutrino data" becomes "neutrino data".
- **B7.** What the 8 × 8 is. C_e is either named in §3.2 or dropped by the result package; that is for
  limitation-resolver.
- **B8.** Percentile wording for the IBU bars. S8 says what the 90 % interval is, and that the point is on the data.
- **B9 and D3.**
  - §5.2's text gives the reported-covariance flags plus the one addition without C_PL,5D (R06). The C_total
    enumeration is left to table 2. **Constraint:** make_values LISTED_CLAIMS anchors the "Under C_total alone" sentence,
    so the anchor list must change with it.
  - "partial evidence" gets its object.
- **B10.** §6.1 gives the median (0.8) beside the maximum, checked against the r5:40 source. The jargon is rewritten
  in plain terms, outside the approved B0 sentences. Those stay verbatim (W-8).
- **B11.**
  - The joint region, and the direction of the threshold, are defined.
  - 204 against 205 degrees of freedom is explained, from COV2D's record.
  - "null's law" becomes "null distribution", and "fail-closed rules" becomes "stopping rules".
  - The lateral/normalization surrogate clause is clarified.
- **B12.** "two readings" becomes "two variants of the test, fixed in advance", which is presentation. The editor's
  "it tests coverage at each of the two truths; it does not estimate a rate over truths" was checked against
  `LL5D-DECLARATION.md`:
  - `:88`: "Grading is per tune and per reading. With two truths there is no coverage rate."
  - §6, `:473-475`: COVERS and UNDER-COVERS "at (T, reading)".

  It says neither more nor less than those lines, so it is applied as presentation, with that citation in its source
  comment. If the director reads it otherwise, it becomes a W-item.

  **The sentence as queued:** "it tests coverage at each of the two truths, for each variant; it does not estimate a
  rate over truths". This is the editor's follow-up of 2026-11-09, matching `:88`'s "per tune and per reading".
- **B13.** The Limitations preamble is cut. "Demonstration" becomes "illustration".
- **B14.**
  - Fig. 2 caption: C⁺, and the bin indices.
  - Fig. 3 caption: why panel (a) is the lower-capacity variant. The legend's "exp." is in the figure file, so it is
    a figure-code change, noted here.
  - Fig. 1's legend citation form.
- **B15.** One spelling: US, the majority. "Supplemental Material" becomes "supplementary material" in Data
  availability. The timing phrases are unified only after D5's ruling.
- **C1.** Each abstract variant is made grammatical on its own; the pending marker gets its own clause.
- **C2.** §5.3 prints the bar: max(0.05, 9.03 s), from FD-PRR §5.1 `:281-286`.
- **C3.** Every outcome is checked to leave the intro sentence, §7 ¶1 and Limitation 1 true. A COVERS variant
  sentence is added to §7 if needed. variants.md records the check.
- **C4.** The PENDING_GROUPS descriptions become descriptive names, with no internal labels. check_round's GONE
  check is extended to values_fived16.tex's `fvgd@` lines, which the paper prints. **This is a defect in e3b99c82b.**
- **D4.** The instability is stated once in §6.1.
- **D6.** The roadmap shrinks to one sentence.

## For the director, as W-items (claim-level, or marked [J])

<!-- absence-ok: this section quotes draft wording options for the director's decision; it states no finding that a result does not exist -->

| new W | editor | the item | my recommendation |
|---|---|---|---|
| W-11 | A1 | the abstract's "The uncertainties are not calibrated" overgeneralizes from the 2D covariance at two tunes. It goes beyond COV2D's NOT CITABLE FOR ("coverage of the reported intervals at the data's point"), and it contradicts §1 ("not established") and Limitation 1 | **a defect I introduced; fix it** to the editor's wording, "The calibration of the uncertainties is not established: the two-dimensional covariance under-covers at two held-out generator tunes, and no five-observable coverage test has run to a result" | <!-- absence-ok: quoted draft wording for the director's decision -->
| W-12 | A3 | §7 ¶2, "tracks the same bias" and "show the same bias toward the prior" (r5:319), rest on evidence the paper doesn't present | weaken to "is consistent with", after checking the records' CITABLE FOR |
| W-13 | A4 | "does not yet provide … run-period consistency" (r5:316) attributes a data property to the method | the editor's fix |
| W-14 | A5 | "applying the thresholds of ref. [5]" implies all of them; the record says one item is not met | "implementing … of the thresholds", with the record's count |
| W-15 | A6 | the residual compared with an earlier covariance that failed acceptance (r5:218), and Fig. 3(b)'s band | for the director: drop it, or keep it with a stated reason |
| W-16 | A7 | the abstract's "bitwise independent of its training seed" lacks §6.1's "in the unfolds we ran" | restore the qualifier |
| W-17 | A8 | "Multidifferential … reach three dimensions", next to the scope sentence, reads as a priority claim (r5:13) | move it into the context paragraph |
| W-18 | A9 | Limitation 3 and §7's sentence on the note's calibrated tests describe tests the paper never presents; rename "joint-test estimator" to "five-observable estimator" | move Limitation 3 to the Supplement. The rename touches the registry aliases and the result package's glossary, so it needs limitation-resolver |
| W-19 | B16 | Data availability: the deposit DOI, and the CC0 terms | for Joseph (with W-9 and W-10) |
| W-20 | D5 | compress the first coverage test's gate detail, and one timing statement in §3.3 | the director checks every test the timing statement covers; the §4.1 background-treatment exception stays explicit |
| W-21 | D7 | move the earlier estimator's miscoverage (0.06) to the Supplement | for Joseph: it is a reported coverage failure; I recommend keeping it |
| — | E | the package's "chi2_over_205" against the paper's "χ²/ndf, ndf = 205" | one name in both pieces; for limitation-resolver |

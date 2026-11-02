# The GENCMP addendum E2 paper round: the independent two-direction review, with dispositions

**The reviewer:** a fresh general-purpose subagent, read-only. It was given:
- the diff `63493acdc..8bcea1714`, with both builds;
- the director's work order, verbatim;
- the authorities:
  - DECISION-20261102 (#680) and DECISION-20261101 item 1;
  - E2's report (§3, §4, §5, §7) and addendum (§0);
  - `e2.json`, `x_e2_sens.out.txt` and the GENCMP readouts.

It was not given the writer's conclusions. It re-derived every new key with its own script. It mutation-tested the
generator in a copy outside the worktree, because `--self-test` rewrites a figure file in place.

**The two directions:**
- truth: each changed sentence, caption, cell and value against its source;
- loss: no required fact dropped, and no sentence elsewhere left false.

**The result:** nothing false, and no decision violated.
- All 124 new keys equal the sources (0 mismatches).
- There is no seed clause and no `reading.sentence`.
- Nothing calls Δ significant or insignificant, or says the rise is "not a GiBUU property".
- The kept hydrogen-sample clause is true under the reported C_model (44.19 < 45.25 < 47.55). DECISION-20261101 item 1
  still requires it, and the new "With the reported C_model" scope makes it consistent with #680.
- Its four plants of its own were each refused by the intended assertion.

| # | sev. | finding | disposition |
|---|---|---|---|
| 1 | Medium | `primer_body.tex:305` ("it raises GiBUU's overall mismatch slightly") and `sec_joint.tex:309` ("rises with the correction") still state the rise as an effect of the correction, against #680 item 3 | FIXED in `ad9403f5d` (ledger E2-6). Both now attribute it to C_model's carbon shape ratios. The primer clause is the same length as before ("on broader cells GiBUU's mismatch rises slightly, from an uncertainty built partly on carbon"): a longer one moved the primer's last reference onto a 16th page |
| 2 | Medium | the paper cites only the doubled readout as the scale, the direction in which χ² is least sensitive. Removing C_model raises the totals by 14.6, 32.5, 12.6 and 119.0 | FIXED: the paper also gives the removal changes (+14.57, +32.45, +12.55, +119.05), keys `e2-with-*-total-dx0` |
| 3 | Low | "most of that rise": the pairing accounts for 2.68 of the 2.29 rise (117 %). "Most" leaves part of the rise to GiBUU, and none is left | FIXED: "That rise comes from pairing …; with those ratios also from CH, GiBUU's total falls instead, to 45.1". The note's two places now read "because" and "comes from". The guard asserts that GiBUU's CH total with CH ratios lies below carbon, which is the same as the pairing's share exceeding the rise. The decision record says "mostly"; this goes to the director as a wording choice |
| 4 | Low | mixed precision in adjacent sentences ("45 to 48", "45.1 against 45.5", "45.3 on carbon" in the generators' definitions) | NOT CHANGED. The integers are Table IV's printed form. The one-decimal pair is needed to show 45.1 < 45.5. The 45.3 sits inside the clause marked "all in the generators' own definitions" |
| 5 | Low | Table 22's Δ_CH is 0.01 off the difference of the printed columns in three rows | FIXED: the caption says "from unrounded values" |
| 6 | Low | "Every χ² falls as C_model grows, GiBUU's most" is true from ×0, but not from ×1 to ×2 | FIXED: "Every χ² falls as C_model grows. Removing C_model raises GiBUU's total most, to 166.83 from 47.78" (asserted for totals in both arms) |
| 7 | Low | Sec. 10.6's three tables floated past the Sec. 11 heading | FIXED: a `\clearpage` ends `sec_fived16.tex`. Tables 21–23 are on pp. 78–79 and Sec. 11 starts on p. 80. The note is 133 pp |
| 8 | Low | the paper's source comment (`:234`) still called the target effect "not measured" | FIXED: it now cites E2 §3 and §5 and the `e2`/`e2sens` pins, with the arithmetic of the attribution |
| 9 | Low | stated facts not guarded: (a) the without-C_PL,5D σ fall's cell; (b) NuWro's and GiBUU's rows of S actually change; (c) "GiBUU's most" for shape-only; (d) "where it is small" at R12; (e) "every prediction's χ² moves" | FIXED: (a), (b), (d) and (e) are now asserted. (b) and (e) also have self-test plants, each refused by its own message. (c): the sentence now names the total only, which is asserted |
| 10 | Low | the limits sentence omits E2 §4's point that the data's statistical uncertainty on the vertex unfolds is not measured | FIXED in the note only: "The changes are those of these data; their statistical uncertainty, from the data entering the unfolds that build C_model, is not measured." There is no seed clause. It is waived as a scoping statement, as in E2's report |
<!-- absence-ok: scoping statement about what E2 measures (FD-GENCMP-AMENDMENT-E-ADDENDUM-E2-REPORT.md sec. 4: no addendum declared input resampling), quoted from the note, not a claim that a result does not exist -->

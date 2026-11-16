# An independent referee's accuracy items: the meaning read (2026-11-16)

**What changed:** commit 92c485079, which applies the director's selection of an independent referee read of d30df1ce
(relay-only: the report is not committed or quoted). The items are A1, B3, B4, B6, B7, D1, D2, D4, D5, D10 and E1.
That commit's message gives each item's record.

**The read:** an independent read-only subagent, of HEAD 92c485079 against each record.

**Verdict: MINOR.** Nothing is false against its record.

**Two defects, fixed in the follow-up commit:**
- §5.3: "IBU overshoots the truth" had lost "along the prior-to-truth direction" and "at the two flagged truths"
  (paper :440 and the Table 6 caption). Both are restored.
- §5.2: after the split, "They are not independent …" lost its subject. It now reads "The held-out-tune tests are not
  independent …".

**Notes applied:**
- D2: "that the replicas support" was replaced by "a quarter of the replica count by the comparison's rule", since
  ⌊N/4⌋ is a fixed rule (Supplement :756).
- D5: the inversion sentence now reads "the cells compared, 16×16 in this paper", because the Supplement inverts 8×8
  at :585 and :896.
- B6: "in central value" is added, and "a level offset" becomes "an excess", since the excess rises from 0.5 % to 8.4 %
  and its lowest unfolded bin lies inside the noise.
- B7: the shares are "of the prior weight in the region cells" (the tab:tune-gate caption).
- The publication.bib comment that described the entry as a misc entry is updated.

**Notes for others:**
- **Joseph (protected text):** the Data availability section (main_paper.tex) still says the whole "analysis used an
  earlier production of that release", which now contradicts §2.
- **journal-editor:** Supplement Table S1 (:43) says "the same exposure" (RECORD-20261008 D02: the publication quotes
  10.61×10²⁰), and Supplement :334 names "Stay Positive", a title the published version drops.
- **A caveat on §2:** "than the other playlists" rests on q2-opendata REPORT §1's download dates. Its §4 compared
  only 1A and 1P directly.

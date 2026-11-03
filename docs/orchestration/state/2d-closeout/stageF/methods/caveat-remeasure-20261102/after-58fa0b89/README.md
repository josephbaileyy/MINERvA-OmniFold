# Caveat density after #695: the paper at main `58fa0b89` (2026-11-02)

**Asked for by** the director: the after point of #695 (the Section IV consolidation and the quadrant sentence),
measured against the before point at `108040f8` (`../README.md`).

**CITABLE FOR:**
- the paper's caveat measures at `58fa0b89`, by the 10-25 caveat study's procedure;
- which caveats' wording #695 changed.

**NOT CITABLE FOR:**
- a change smaller than the coder spread, which is about ±25% (`../../caveat-study/REPORT.md` §2.4);
- the note, which was not re-coded. The director ruled that the note's run at `108040f8` stands.

## Result

| paper at | words | distinct caveats | distinct /1k | statements per caveat | statements /1k |
|---|---|---|---|---|---|
| `108040f8` (before; coder 1) | 7,982 | 84 | 10.52 | 1.76 | 18.54 |
| `58fa0b89` (after; coder 2) | 8,080 | 77 | **9.53** | 1.88 | 17.95 |
| *P range* | | | 1.38–4.54 | 1.60–2.29 | 2.38–7.76 |

By kind, before and after, distinct caveats:
- (a) 4 and 4;
- (b) 3 and 3;
- (c) 43 and 44;
- (d) 30 and 22;
- (e) 4 and 4.

**How much of the −9% #695 caused.** The two inventories come from two coders, so caveats are matched by text: a
caveat persists if any of its statements still prints verbatim.
- **Wording that left.** Of the 84 before caveats, **7** lost every statement:
  - C_model coverage at held-out truths;
  - the earlier calibrated-model-term route;
  - two learner-choice statements;
  - two 2D covariance statements;
  - the normalization check that covered only the three-observable marginal.
- **Wording that arrived.** **6** after caveats have no statement in the before text:
  - the reworded learner choice;
  - the run-period block's self-consistency check;
  - the bounded correlations of the quadrant sentence;
  - the narrowed four-observable check;
  - the reworded 2D covariance statement;
  - the earlier 2D band's fixed-truth failure, which #690 item 2 required.
- **Net text change.** Almost all of these are rewordings of the same issues. On the before coder's labels, the after
  text holds about 77 + 6 = 83 distinct caveats: **≈ 10.3 per 1k, −2%**.
- **The rest is coder variation.** The remaining drop, from 83 to 77, is mostly in how the two coders grouped (d)
  scope statements (30 → 22).
- **Conclusion.** #695 left distinct-caveat density essentially unchanged. Its effect is inside the coder spread on
  either reading.

**Reproduce:**

    python3 -I ../remeasure.py --repo <checkout at 58fa0b89> --work <scratch> --inv after-58fa0b89/inv

This gives exit 0. The blinded text is pinned in `inv/CODED-ON.sha256`, and a rebuild at `58fa0b89` reproduces it
byte for byte. The analysis-note sources are unchanged from #695's head `cc02b2eb` through `c95b6d3c`, so the coding
holds for all three commits.

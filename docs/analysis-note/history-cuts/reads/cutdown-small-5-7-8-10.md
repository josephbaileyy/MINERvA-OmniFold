# Cutdown meaning read: §5.2 (sec_validation K1), §7.8 (sec_3d K1), §8.5 (sec_eavailw K1), §10.3 (sec_fived16 K1)

Reader: the editor (Claude Fable 5.2), new text against the base `8342963c1`. The editor's own read, not an
independent model's. (a) does the sentence still say exactly what it said, or less? (b) does every remaining
sentence's antecedent and pointer still hold?

| row | (a) | (b) |
|---|---|---|
| sec_validation K1 | One whole paragraph removed; no remaining sentence is reworded. | The next paragraph opens "Unlike the band's replicas, the central value has completeness exactly 1", which follows the positive-control paragraph as well as it followed the removed one. Its last sentence ("in the replica form, the p_∥ 40–60 GeV/c column still undercovers") stands on its own. Nothing later refers to the per-bin counts. The values.tex macros the paragraph used are defined and now unused; the build does not require their use. |
| sec_3d K1 | Three whole sentences removed; the first sentence of the paragraph is word for word. | The paragraph is now one sentence under its heading "No 4D uncertainty.", and its search comment still follows it. §4's opening ("no 4D uncertainty magnitude is reported (§…4d)") points here and finds the statement. |
| sec_eavailw K1 | One whole sentence removed. | The paragraph now ends "A later significance for a region chosen from the central-value map must account for that selection.", which is complete. §7.8 keeps the comparison. |
| sec_fived16 K1 | The first sentence loses its parenthesis and gains "(App. I)"; its claim is word for word. Everything after it in the passage is removed. | The parenthesis defined J, H2 and R for the removed sentences only. App. I's row says "Stage 0 failed its first part on both sets of cells and stopped; the reconstruction-information test, which remains incomplete, had no configuration meeting its residual requirement. C_model was then adopted unscaled", so the new pointer supports "did not pass its first two tests". App. I's row points back to §10.3, where the kept sentence is. The next paragraph ("For C_resp, …") is independent. The keys s0-cfam-min, s0-pooled-min, s0-h2-*, s0-j-* and r10-nconfig are no longer printed; they were deleted only with their sentences. |

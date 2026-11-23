# Cutdown, §7 (sec_3d.tex): cut log

**Under** Joseph's go for the cutdown (DECISION-20261116-joseph-paper-batch.md at main `99aefd3f0`, sixth answer,
items 29 and 34) and the editor's brief of the same day. **The rule (2026-11-13):** history or detail stays in the
note only if removing it would change a reader's understanding of the reported object, its reproducibility, its
evidential independence or its limitations; everything else goes to the ledger or the records document.

**Base:** `sec_3d.tex` at `8342963c16d74bc10d740e5637d602300557e53a`. Line numbers are the base's; removed text stays at that sha and line.

| id | base line | words cut | disposition | old text | new text | home of the content | why not NEEDED |
|---|---|---|---|---|---|---|---|
| K1 | :206, sentences 2–4 | 67 | cut to ledger | "A corrected 4D covariance would use the actual minus and plus variation endpoints; MAT's mean-centered covariance blocks, normalized by 1/N; one fixed estimator seed; and mean-centered joint throws, with the mean shift reported separately. It would not subtract a scalar jitter floor. Because the single-pass shifted observables exist only for events selected at the central value, re-selected event loops (§…uq-higherdim) would be needed to bound migration effects." | cut; the paragraph keeps "Neither a 4D uncertainty nor a ratio … is reported." | 8342963c1:sec_3d.tex:206. The same construction rules are stated for the covariances that exist, in §4.5 and §4.7. | A specification of a covariance that was not built. The statement a reader needs, that no 4D uncertainty is reported, stays. |

**Kept, though the cutdown table proposed shortening §7.6–§7.8 to about 1,100 words.** Each passage was checked and
kept for a reason of the rule or of a pin:
- the flux-repair paragraph: three of its sentences are pinned by records probes, and it states which studies keep
  unrepaired samples;
- the pion-FSI paragraph: §8's opening relies on its result ("change the prediction by less than one percent");
- the two 2p2h paragraphs: they say how the printed 52% and 63% are normalized (a records probe pins that sentence),
  which is the reproducibility of printed numbers;
- the two-body-current sentences: a caveat on reading the 2p2h comparison;
- the comparison with the published low-recoil measurement: it carries the definition difference that limits it.

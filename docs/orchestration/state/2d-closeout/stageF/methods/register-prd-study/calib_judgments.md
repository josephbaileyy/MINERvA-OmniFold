# Hand calibration of tools/qcount.py (2026-10-23)

Gold standard (one rater: the study agent). A **qualifier** is a word or phrase that restricts the scope of one of the
paper's own claims, makes it conditional, disclaims or limits its evidential status (not validated, not measured,
post hoc, descriptive), hedges it, or concedes a limitation of the paper's method or result. A negation that reports a
physics finding ("the model does not describe the data") or describes a model ("the spectator nucleon is not
simulated") is NOT a qualifier; a negation that limits the paper's own claim ("its size is not validated") is. <!-- absence-ok: quotes or discusses absence wording in the corpus or our paper; not a claim that a result does not exist -->

## Set 1: 30 random sentences (calib_sample.txt; seed 20261023; 15 ours, 15 corpus)

| id | detected | judgment | missed (FN) |
|---|---|---|---|
| S01-S04, S07, S10, S12, S13 (ours) | none | correct negatives | - |
| S05 ours | has not been measured; cannot; could; unmeasured | 4 TP | "rests on one seed pair" (scope) | <!-- absence-ok: quotes or discusses absence wording in the corpus or our paper; not a claim that a result does not exist -->
| S06 ours | none | - | "rather than an independent validation" (status) |
| S08 ours | descriptive | 1 TP | - |
| S09 ours | none | - | "a significance ... would also require their cross-covariance" (status) |
| S11 ours | is not validated; cannot | 2 TP | - | <!-- absence-ok: quotes or discusses absence wording in the corpus or our paper; not a claim that a result does not exist -->
| S14 ours | is not known; cannot establish | 2 TP | - |
| S15 ours | Within | 1 FP (locative definition) | - |
| S16 2004.05434 | within; not | 2 FP (tolerance; a finding) | "usually" (hedge); "Whilst" (concession) |
| S17-S23, S25-S28, S30 (corpus) | none | correct negatives, except S18 | S18: "Other methods ... are needed to investigate these complex regions" (implicit limitation) |
| S24 1705.03568 | depend on | 1 TP (model dependence of a method) | - |
| S29 2110.13372 | but | 1 FP (model contrast) | - |

Set 1 totals: ours TP 9, FP 1, FN 3; corpus TP 1, FP 3, FN 3 (S16 x2, S18).

## Set 2: 30 further random corpus sentences (calib_sample_corpus_extra.txt; seed 99)

TP 4 (S02 suggesting; S03 without [the most forward bin]; S07 only; S21 only), FP 16 (S03 assumptions; S05
partially; S09 not; S15 However, not, not; S17 In simulation[-based]; S20 conditioned; S21 not; S22 not; S23 in this
analysis; S27 not; S29 only, depend on, whereas, depend on), FN 4 (S02 "when a full TMD uncertainty breakdown is
available"; S03 "generally"; S19 "potential"; S28 "This comes with a cost of modest model biases").

## Set 3: 40 random marker instances (calib_markers.txt; seed 7; 20 ours, 20 corpus) -- precision only

Ours: TP 17, FP 3 (M04 "needs no convergence"; M05 "possible"; M20 "a specified deformation" in a definition).
Corpus: TP 5 (M21, M31, M33, M36, M39), FP 15.

## Result

| population | sentences / instances | precision | recall |
|---|---|---|---|
| ours, set 1 sentences | 15 sentences, 12 gold qualifiers | 9/10 = 0.90 | 9/12 = 0.75 |
| ours, set 3 instances | 20 instances | 17/20 = 0.85 | - |
| corpus, sets 1+2 sentences | 45 sentences, 12 gold qualifiers | 5/24 = 0.21 | 5/12 = 0.42 |
| corpus, set 3 instances | 20 instances | 5/20 = 0.25 | - |
| pooled, all sentences (sets 1+2) | 60 sentences | 14/34 = 0.41 | 14/24 = 0.58 |
| sentence-level (>=1 qualifier), set 1 | 30 sentences | 6/8 = 0.75 | 6/9 = 0.67 |

Arithmetic: ours set 1 gold = 9 TP + 3 FN = 12; corpus sets 1+2: TP 1+4 = 5, FP 3+16 = 19, FN 3+4 = 7, so precision
5/24 and recall 5/12; pooled TP 14, FP 20, FN 10.

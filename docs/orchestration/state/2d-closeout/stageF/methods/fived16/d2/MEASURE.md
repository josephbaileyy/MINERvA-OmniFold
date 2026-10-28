# d2: what is typical, measured (2026-10-28)

**Under:**
- `DECISION-20261028-joseph-final-draft-d.md`, items 2 and 6. Joseph's words: "typical lengths", no "metatext", no
  "more qualifications/limitations than typical", and "do what is typical for these types of papers first as a
  draft".
- The director's work order of 2026-10-28.

**Measured by** the paper rewrite lane, with register-prd-study's own tools: `tools/abstract_stats.py`, which uses
`tex2prose.convert` and `qcount.markers`. The sources are the corpus's arXiv sources, as downloaded in
`be6e903d…/scratchpad/corpus-dl/` at the versions of `register-prd-study/REPORT.md` §1. The study's own `src/` was
emptied by the tmp sweep.

## 1. The paper abstract

| doc | words | sentences | sentences with a SCOPE, COND or STATUS marker |
|---|---:|---:|---|
| 2002.12496v2 (MINERvA) | 119 | 5 | 1 of 5 |
| 2004.05434v2 (T2K) | 141 | 5 | 0 of 5 |
| 2102.03346v1 (T2K) | 98 | 4 | 0 of 4 |
| 2106.16210v4 (MINERvA) | 120 | 7 | 0 of 7 |
| 2110.13372v2 (MINERvA) | 122 | 5 | 0 of 5 |
| 2301.03700v4 (MicroBooNE) | 113 | 5 | 0 of 5 |
| 2310.06082v4 (MicroBooNE) | 141 | 6 | 0 of 6 |
| 2504.06857v2 (OmniFold/T2K methods) | 121 | 4 | 0 of 4 |
| **ours, at d (`0be5f0ff`)** | **238** | **8** | **5 of 8** |

These agree with the director's count from the sources, which gave 97, 113, 117, 120, 120, 121, 141 and 141 words,
within the tokenizer's ±3.

**The caps for the paper abstract:**
- **Words:** median about 120, maximum 141, so 120–150.
- **Markers:** at most one marked sentence, carrying at most one marker. The corpus maximum is one marked sentence,
  and no corpus sentence carries two markers (`register-prd-study/REPORT.md` §2.2).

## 2. The note abstract

The anchors are the long technical documents of the rater calibration (`rater-calibration/NOTE-BASELINE.md`). Their
abstracts come from the arXiv abstract pages saved by the caveat study (`796e7ecc…/scratchpad/caveat/abs/`; sha256
`69bfa90b…` and `86b2e675…`), measured with the same converter and markers.

| doc | words | sentences | marked sentences |
|---|---:|---:|---|
| T2K, PRD 91, 072010 (arXiv 1502.01550) | 184 | 7 | 0 of 7 |
| ProtoDUNE-SP, JINST 15, P12004 (arXiv 2007.06722) | 190 | 8 | 0 of 8 |
| **ours, at d** | **382** | **9** | **5 of 9** |

**The caps for the note abstract:**
- **Words:** at most 190, the anchors' maximum. The floor is 110: the candidates below are whole-sentence subsets,
  and the longest one that meets the marker cap is 136 words.
- **Markers:** the corpus cap, at most one marked sentence carrying at most one marker.

## 3. Why only these candidates

`make_candidates.py` builds each candidate from whole sentences of the printed abstract. That is the guardrail:
reduce by removing whole sentences, never by weakening one that stays. The one wording change is the note's "Its
principal result is" → "The principal result of the analysis is", because the metatext sentence that gave "Its" its
antecedent leaves.

Under the caps:
- **The paper** has three candidates, each keeping the result sentence, the χ² sentence and the fake-data sentence (which
  carries no marker):
  - PA adds the coverage and bias-test sentence (134 words, one STATUS marker);
  - PB adds the reproduction (120, one SCOPE);
  - PC adds the validation findings (129, one SCOPE).
- **The note** has only two: NA (coverage and bias test, 136 words) and ND (flux, 117). Each other remaining note
  sentence carries two or more markers.

## 4. Data and release (item 6)

`DA-SURVEY.md` holds the seven corpus measurement papers' release text, quoted from source. In brief:
- all seven release their cross sections, a covariance and the binning;
- four say where in the text;
- three use the Supplemental Material;
- two cite a collaboration web page;
- none has a Data Availability section, because all predate the PRD requirement of 2024-09-04;
- none cites a DOI or HEPData.

The typical draft is `options.py` `DA_TYPICAL`.
<!-- absence-ok: reports measured counts of the corpus's abstracts and release text; not a claim that a result is absent -->

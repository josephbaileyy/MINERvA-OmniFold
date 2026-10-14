# DECISION 2026-10-14 — Joseph adopts the narrower 2D publication endpoint, and rules on six open items

**Recorded by** the paper-tighten lane, as director. On 2026-10-14 the director put seven open items to Joseph, in
his session. Each came with an explanation and a recommendation. Joseph answered all seven in one message, quoted
verbatim here:

> "1. yes lets adopt the narrower endpoint 2. defer it 3. keep the decision 4. agreed with your recommendation 5.
> okay do your recommendation 6. agreed with your recommendation 7. okay agreed"

Each answer's sha256 is taken over the answer text plus a final newline; the first 16 hex digits are shown.

**CITABLE FOR:**
- the publication endpoint the 2D closeout now aims at;
- what each of the other six rulings starts, or leaves held.

**NOT CITABLE FOR:**
- adopting any product, central value, uncertainty or claim wording. Stage F adoption stays Joseph's, made on the
  reviewed products;
- a KI-85 lift;
- a compute grant;
- any message to NERSC, MINERvA, a coauthor or anyone else. Sending stays Joseph's act;
- a statement that the full scientific closeout was achieved. It was not.

## 1. Rulings

| # | item | the director's recommendation, in short | Joseph's answer | sha256 (16) |
|---|---|---|---|---|
| 1 | **Q7: the publication endpoint** ([`PLAN-20261011-2d-closeout.md`](PLAN-20261011-2d-closeout.md) §6; the Stage D REPORT §1, overall UNAVAILABLE) | Adopt the narrower endpoint for this publication. Keep the full endpoint as future work and disclose it as not achieved | "yes lets adopt the narrower endpoint" | `5058efa154074ff2` |
| 2 | the response-mismatch closure settings: the amplitude ε and the decision statistic (`docs/analysis-note/app_response_mismatch.tex`; 5D (E_avail, W), not 2D) | Defer. Nothing waits on it, since the 2026-10-06 ruling that Fig. 2 "Stands as written" | "defer it" | `7642221ed33a8afc` |
| 3 | `NormDISCC` (G3, [`../publication/DECISION-20261012-joseph-2d-closeout-recipe.md`](../publication/DECISION-20261012-joseph-2d-closeout-recipe.md)) | Keep the 2026-10-12 decision: null, disclosed as zero and unconfirmed. Raise the collaboration question with Ben | "keep the decision" | `187e97b4211793b0` |
| 4 | the review with Ben | Schedule it. Topics: the endpoint (item 1); the playlist spread and J36; who holds the Q3 key; `NormDISCC` | "agreed with your recommendation" | `2cb626c5242d95da` |
| 5 | drafts A and B (`docs/publication/corrections-20261008/DRAFT-20261008-anatuple-preservation-requests.md`) | Revise A down from about 11 TiB to about 1 TiB, covering only the 41 Playlist 1A MC files (0.707 TB). Before that, verify the 448 1B–1P MC files against the public release by checksum, read-only. Drop B. The director prepares the final A text; sending it is Joseph's act | "okay do your recommendation" | `5614a13c2885695c` |
| 6 | the 1A re-download (about 0.96 TB) | Not now. Preserving our 1A copy through A keeps exact reproducibility. A re-download, if wanted, comes after the closeout | "agreed with your recommendation" | `2cb626c5242d95da` |
| 7 | the GENIE v3 throughput pilot (≤ 0.2 core-h; Q4's limited route) | Hold. It belongs to Stage D. Under the narrower endpoint it is at most a later cross-check | "okay agreed" | `12437dd98a6c60c1` |

## 2. What the narrower endpoint means (item 1)

The plan defines three milestones (§1): engineering complete, construction complete, and scientific closeout. It
also says the narrower endpoint "is a different publication endpoint. It is not 'all issues closed'" (§6).

**This publication aims at construction complete.** That is a matched uncertainty construction under declared
assumptions:
- one reproducible central estimator, LightGBM seed 42, already adopted for the central value on 2026-10-11;
- every required source propagated once, with correlations and approximation errors accounted for;
- the MAT systematic universe law as a declared convention (Q5, 2026-10-14);
- the remaining construction limits disclosed. These are KI 85, 88 and 90–94, `NormDISCC` (G3), C07′ omitted,
  G2 as Joseph rules after K2, the J36 mix error, and the playlist spread (below).

**Full scientific closeout is NOT ACHIEVED, and the package must say so.** That would be independent validation that
supports the interval, bias and covariance claims. Its inputs do not exist:
- no independent production-size MC;
- no validated continuous nuisance generator;
- only truth-level, already-inspected independent-generator samples.

The open-data release is a reprocessing, not a new production (Q2). Full closeout stays open as future work, and no
coverage claim is made.

**What follows:**
- **Stages C and F proceed.** Stage C is the pilot, then production under the director's grants. Stage F is
  adoption, deliverables and recovery, with Joseph adopting the products and the claim wording.
- **Stages D and E are not executed for this publication.** The Q3 design
  ([`PROPOSAL-20261014-q3-custodian-key-design.md`](PROPOSAL-20261014-q3-custodian-key-design.md)) stays an
  unadopted proposal for that future work. So does the GENIE v3 pilot (item 7).
- **KI-85 is not lifted.**
- **Claim wording must stay inside the narrower endpoint.** It may say: a reproducible central value with a matched
  uncertainty construction under stated conventions. It may not say: validated coverage, calibrated intervals or
  goodness-of-fit significance beyond what the construction supports. The director drafts the wording at Stage F for
  Joseph's adoption.
- **The playlist spread is a disclosure item.** Its coverage by the existing bands is being checked read-only; the
  result is recorded when it lands. If it is not covered, it goes to Joseph as a construction question before Stage F.
  ([`state/2d-closeout/playlist-spread-20261014/REPORT.md`](state/2d-closeout/playlist-spread-20261014/REPORT.md))

## 3. Item 5, as started

The director runs the read-only checksum comparison of the 1B–1P MC files. It re-measures the HPSS quota and the CFS
usage, then revises draft A in its file. The comparison and the revised text are recorded separately. Nothing is sent.

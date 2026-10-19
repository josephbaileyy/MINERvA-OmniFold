# Agenda: Joseph's review of the 2D closeout with Ben (DRAFT, 2026-10-16; updated 2026-10-17 after J1/J2, and 2026-10-18 after the provisional J3–J5)

**Prepared by** the paper-tighten lane, as director, for Joseph. The review is Joseph's. Scheduling it, inviting Ben
and sending anything to him are Joseph's acts. Nothing here has been sent.

**CITABLE FOR:** the topics Joseph asked to bring to Ben, with the record behind each one.
**NOT CITABLE FOR:** any outcome of the review, or any adoption.

The review was agreed on 2026-10-14
([`DECISION-20261014`](../../../DECISION-20261014-joseph-2d-endpoint-and-open-items.md), item 4). The playlist-term
decision added the per-period test to it
([`DECISION-20261015-joseph-playlist-consistency-term.md`](../../../DECISION-20261015-joseph-playlist-consistency-term.md) §2).

**Timing.** Joseph decided on 2026-10-17 to adopt before the review (J1), and adopted S5 + C_PL (J2)
([`DECISION-20261017-joseph-2d-adopt-s5-plus-playlist.md`](../../../DECISION-20261017-joseph-2d-adopt-s5-plus-playlist.md)).
The review therefore scrutinizes an adopted construction; Joseph can still revise it afterwards. Parts 1 and 2 are
both ready: the production REPORT, its verification and the combination are on `main`.

## Part 1 — decisions already taken, for Ben's scrutiny (ready now)

| # | topic | question for Ben | record |
|---|---|---|---|
| 1 | **The endpoint.** Construction complete under declared conventions; full scientific closeout NOT ACHIEVED; Stages D and E not executed | Is the narrower endpoint publishable as framed? Is the disclosure strong enough? Is "construction complete" earned when G2 (unmeasured), the learner dependence (0.98% median) and C09/C10 (unfolding model, regularization, response; Stage D) are outside every block? | DECISION-20261014 §2; draft disclosure D1 |
| 2 | **Central value.** LightGBM seed 42 (`E_U`), adopted after the comparisons were known, so that it matches its covariance's estimator | Is the post-hoc switch disclosed clearly enough? | [`DECISION-20261011`](../../../../publication/DECISION-20261011-joseph-2d-central-lightgbm-seed42.md); paper §`sec:repro2d` |
| 3 | **The recipe.** Three independent bootstrap streams (R5); C04+X01 flux repair (VL175); KI-92 Rvn1pi counted once; laterals from active files; the seed main effect C08 | Is any source missing or double-counted? | [`DECISION-20261012-joseph-2d-closeout-recipe.md`](../../../../publication/DECISION-20261012-joseph-2d-closeout-recipe.md); Stage B REPORT; production DESIGN §8 |
| 4 | **`NormDISCC` (G3)**: kept as a null band, disclosed as zero and unconfirmed | Is it intentionally null in the MINERvA products? Would Ben ask the collaboration? (Asking is Joseph's or Ben's act) | recipe decision G3 |
| 5 | **C07′ data-POT counting**: omitted, because the flux prediction carries a 2% POT-counting term by convention | Is the two-inferred-links argument acceptable? | Stage B diagnostics §6.2 |
| 6 | **G2**: carried as a disclosed approximation; 2 of 187 universes tested, neither resolved above trainer noise | Is 2 of 187 enough, or is the 43–129 node-h repair worth it? | [`DECISION-20261015-joseph-g2-carry.md`](../../../DECISION-20261015-joseph-g2-carry.md) |
| 7 | **C03 shared draw not applied**: the background stream is independent of the signal stream; the overlap was never measured | Acceptable as a disclosure? | production DESIGN §8 |
| 8 | **The playlist spread and J36.** 1G–1M low by about 3%, 1N–1P high by about 5% at reco level. The per-period unfold shows a 1G–1M p_∥ step of +6.94% ± 0.41 that VL175 does not cover: diluted into the combined result, the raw shift has χ² p_∥ 33.8 against a noise expectation of 1.8 (the double-ratio shift gives 33.1, with no noise reference). J36 is −0.084% | Is the cause known within MINERvA (intensity, detector or beam changes between periods)? Which period, if any, should be the reference? | [`period-unfold REPORT`](../period-unfold-20261014/REPORT.md); [`playlist-spread REPORT`](../playlist-spread-20261014/REPORT.md) |
| 9 | **KI-85**: statistical calibration deferred until after the publication package; no coverage claim is made | Is publishing with untested coverage acceptable if it is stated plainly? | KNOWN_ISSUES 85 |
| 10 | **Flux block smaller than published** (4.01% published median against ours); the reason is not established by the release | Does Ben know why? | paper §`sec:uq2d` |

## Part 2 — products for review (after Stage C and the playlist block)

| # | item | what Joseph and Ben see |
|---|---|---|
| 11 | The production covariance: per-block medians, rank, PSD, ensemble errors (≈4% per-cell σ; C08 with 4 dof, 71% relative SE of variance). Retraining noise inside the universe block (X03): in `2p2h:0` and `MaCCQE:0` it is as large as the shift; X03 and the band-centring numbers were not independently recomputed | production REPORT and `s5.json` summary |
| 12 | The playlist-consistency block: its design (reference-free double ratio, 1F in group A, each period's own MC response) against its sensitivities (1A–1F reference, raw ratios); exchangeability, grouping, noise overlap and possible shrinkage; its size with and without it in the budget. The block, its independent recompute and the combination with S5 exist ([`../playlist-term/REPORT.md`](../playlist-term/REPORT.md), [`../playlist-term/COMBINATION-REPORT.md`](../playlist-term/COMBINATION-REPORT.md)). Containment of the observed differences is algebraic, not a coverage test: the block's own double-ratio check is passed by construction. Is a run-period difference covariance the right object? | the block REPORT, its [`recompute/`](../playlist-term/recompute/) outputs, and the F9 combination |
| 13 | The budget against VL175 and against the published analysis | [`rebuild/REPORT.md`](rebuild/REPORT.md) §3–§4; paper §IV B as built |
| 14 | The disclosure set with final numbers, as written into the four documents | [`DRAFT-disclosures.md`](DRAFT-disclosures.md) revision 4; the built PDFs (below) |
| 15 | The claim wording, inside the narrower endpoint: Joseph's provisional J3–J5 (all as recommended) | [`DECISION-PACKET-J3-J6.md`](DECISION-PACKET-J3-J6.md); [`DECISION-20261018`](../../../DECISION-20261018-joseph-2d-j3-j5-provisional.md); [`J3-J5-WORDING-IMPLEMENTATION.md`](J3-J5-WORDING-IMPLEMENTATION.md) |
| 16 | The plain-language pass (2026-10-18), with content unchanged. Its decisions left to Joseph: A, state the numbers the hedges stand in for; B, move history and repeated caveats from the paper and primer to the note; C, claim-strength wording; D, items outside the pass (bibliography titles, figure legends, the result-status table) | [`PLAIN-LANGUAGE-IMPLEMENTATION.md`](PLAIN-LANGUAGE-IMPLEMENTATION.md) §7–§8; [`DECISION-20261018-joseph-plain-language-pass`](../../../DECISION-20261018-joseph-plain-language-pass.md) |
| 17 | Plain-language pass 2 (2026-10-19): themes A–D as decided; the paper's abstract 233 → 163 words; the 5D uncertainty status now precedes the results; two outside models (Gemini 3.8 Flash, GPT-6.1-sol) critiqued and rewrote; both still read the paper as audit-like. The physics points they raised, triaged: calorimetric response (high); W fixed by (pT, p∥, q3); the sequential p-value sentence; carbon vs hydrocarbon targets; the null's hadron composition; the background treatment in the figures. Framing as a methods paper is the lever left | [`PLAIN-LANGUAGE-PASS2-IMPLEMENTATION.md`](PLAIN-LANGUAGE-PASS2-IMPLEMENTATION.md) §3, §5, §7 |

**The built PDFs** (note, paper, primer, PET note) are built locally from the plain-language pass-2 branch, and their sha256
are in `PLAIN-LANGUAGE-PASS2-IMPLEMENTATION.md` §6. They supersede the earlier builds. They are not committed and have not been sent anywhere. Joseph decides whether and how Ben receives them (J6).

**Points for Joseph to confirm at the review** (raised by the independent review of the wording):

| # | point | where |
|---|---|---|
| 15a | **A director's factual correction to approved wording.** The ~7% run-period step belongs to the double ratio: each period group's unfolded distribution taken relative to its own simulation. The unfolded distributions themselves step by 10.29%. The disclosure's meaning is unchanged. | paper §IV B; note §uq-combine; DRAFT D5 revision 4 |
| 15b | **Readability of the decided register W1(c).** "Full scientific closeout", "population or simultaneous interval coverage" and "calibrated covariance-based generator significance" are not defined for an outside reader. **Addressed by the plain-language pass:** paper and note now say "The result's intervals, bias and covariance have not been independently validated", with the coverage cases spelled out. Joseph to confirm. | paper §IV B; note §sec:uq-2d-scope |
| 15c | **The endpoint statement carries more than W1(c)'s sentences:** the three missing inputs and "no coverage claim is made" (D1's required content, DECISION-20261014 §2), and the note's "goodness-of-fit values are indicative" clause. | paper §IV B; note §sec:uq-2d-scope |
| 15d | **The primer says nothing about the run-period inconsistency.** The decision placed D0–D5 in the paper and the note, not the primer. | primer |
| 15e | **To keep the paper at 11 pages**, one parenthetical moved to the note: the post hoc diagnostic pointing to under-scatter of the closure pseudo-experiments. Restoring it made the paper 12 pages; after the plain-language pass the paper is 12 pages anyway (page 12 is references), and the space cost of restoring it is unmeasured. | paper §IV B; note §sec:coverage |

## Part 3 — housekeeping that needs Ben

| # | topic | record |
|---|---|---|
| 16 | **PET folders on CFS**: `mnv-p3f-pet-fullevent-final/` (1,134,999,732,224 B, the only copy) and `pet-studies-20261006/` (422,878,122,496 B). Joseph's CFS area is about 3.947 TB, against his 3 TB rule | [`cfs-copy-1A-mc REPORT`](../preservation-20261014/cfs-copy-1A-mc/REPORT.md) §2 |
| 17 | **Who holds the Q3 custodian key.** This belongs to the future full closeout (Stage D), not to this publication | [`PROPOSAL-20261014-q3-custodian-key-design.md`](../../../PROPOSAL-20261014-q3-custodian-key-design.md) |
| 18 | **Future work for the full endpoint**: independent production-size MC, a validated nuisance generator, untouched truth departures, GENIE v3 | PLAN §4 Stage D |

## Not on the agenda

Submission, deposit, tagging, coauthor or collaboration contact, and NERSC requests stay separately authorized acts of
Joseph's.

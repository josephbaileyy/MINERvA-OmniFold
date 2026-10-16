# Agenda: Joseph's review of the 2D closeout with Ben (DRAFT, 2026-10-16)

**Prepared by** the paper-tighten lane, as director, for Joseph. The review is Joseph's. Scheduling it, inviting Ben
and sending anything to him are Joseph's acts. Nothing here has been sent.

**CITABLE FOR:** the topics Joseph asked to bring to Ben, with the record behind each one.
**NOT CITABLE FOR:** any outcome of the review, or any adoption.

The review was agreed on 2026-10-14
([`DECISION-20261014`](../../../DECISION-20261014-joseph-2d-endpoint-and-open-items.md), item 4). The playlist-term
decision added the per-period test to it
([`DECISION-20261015-joseph-playlist-consistency-term.md`](../../../DECISION-20261015-joseph-playlist-consistency-term.md) §2).

**Timing.** Part 1 can be reviewed now. Part 2 needs the Stage C production REPORT and the playlist block. Joseph
chooses one meeting after both are ready, or two meetings.

## Part 1 — decisions already taken, for Ben's scrutiny (ready now)

| # | topic | question for Ben | record |
|---|---|---|---|
| 1 | **The endpoint.** Construction complete under declared conventions; full scientific closeout NOT ACHIEVED; Stages D and E not executed | Is the narrower endpoint publishable as framed? Is the disclosure strong enough? | DECISION-20261014 §2; draft disclosure D1 |
| 2 | **Central value.** LightGBM seed 42 (`E_U`), adopted after the comparisons were known, so that it matches its covariance's estimator | Is the post-hoc switch disclosed clearly enough? | [`DECISION-20261011`](../../../../publication/DECISION-20261011-joseph-2d-central-lightgbm-seed42.md); paper §`sec:repro2d` |
| 3 | **The recipe.** Three independent bootstrap streams (R5); C04+X01 flux repair (VL175); KI-92 Rvn1pi counted once; laterals from active files; the seed main effect C08 | Is any source missing or double-counted? | [`DECISION-20261012-joseph-2d-closeout-recipe.md`](../../../../publication/DECISION-20261012-joseph-2d-closeout-recipe.md); Stage B REPORT; production DESIGN §8 |
| 4 | **`NormDISCC` (G3)**: kept as a null band, disclosed as zero and unconfirmed | Is it intentionally null in the MINERvA products? Would Ben ask the collaboration? (Asking is Joseph's or Ben's act) | recipe decision G3 |
| 5 | **C07′ data-POT counting**: omitted, because the flux prediction carries a 2% POT-counting term by convention | Is the two-inferred-links argument acceptable? | Stage B diagnostics §6.2 |
| 6 | **G2**: carried as a disclosed approximation; 2 of 187 universes tested, neither resolved above trainer noise | Is 2 of 187 enough, or is the 43–129 node-h repair worth it? | [`DECISION-20261015-joseph-g2-carry.md`](../../../DECISION-20261015-joseph-g2-carry.md) |
| 7 | **C03 shared draw not applied**: the background stream is independent of the signal stream; the overlap was never measured | Acceptable as a disclosure? | production DESIGN §8 |
| 8 | **The playlist spread and J36.** 1G–1M low by about 3%, 1N–1P high by about 5% at reco level. The per-period unfold shows a 1G–1M p_∥ step of +6.94% ± 0.41 that VL175 does not cover (χ² 33.8 against a noise expectation of 1.8). J36 is −0.084% | Is the cause known within MINERvA (intensity, detector or beam changes between periods)? Which period, if any, should be the reference? | [`period-unfold REPORT`](../period-unfold-20261014/REPORT.md); [`playlist-spread REPORT`](../playlist-spread-20261014/REPORT.md) |
| 9 | **KI-85**: statistical calibration deferred until after the publication package; no coverage claim is made | Is publishing with untested coverage acceptable if it is stated plainly? | KNOWN_ISSUES 85 |
| 10 | **Flux block smaller than published** (4.01% published median against ours); the reason is not established by the release | Does Ben know why? | paper §`sec:uq2d` |

## Part 2 — products for review (after Stage C and the playlist block)

| # | item | what Joseph and Ben see |
|---|---|---|
| 11 | The production covariance: per-block medians, rank, PSD, ensemble errors (≈4% per-cell σ; C08 with 4 dof, 71% relative SE of variance) | production REPORT and `s5.json` summary |
| 12 | The playlist-consistency block: its design (construction, reference period, ratio type, 1F, MC responses), and its size with and without it in the budget | the block record and its verifier report |
| 13 | The budget against VL175 and against the published analysis | one comparison table |
| 14 | The disclosure set with final numbers | [`DRAFT-disclosures.md`](DRAFT-disclosures.md) revision 2 |
| 15 | The claim wording, inside the narrower endpoint | a claims draft (after J2) |

## Part 3 — housekeeping that needs Ben

| # | topic | record |
|---|---|---|
| 16 | **PET folders on CFS**: `mnv-p3f-pet-fullevent-final/` (1,134,999,732,224 B, the only copy) and `pet-studies-20261006/` (422,878,122,496 B). Joseph's CFS area is about 3.947 TB, against his 3 TB rule | [`cfs-copy-1A-mc REPORT`](../preservation-20261014/cfs-copy-1A-mc/REPORT.md) §2 |
| 17 | **Who holds the Q3 custodian key.** This belongs to the future full closeout (Stage D), not to this publication | [`PROPOSAL-20261014-q3-custodian-key-design.md`](../../../PROPOSAL-20261014-q3-custodian-key-design.md) |
| 18 | **Future work for the full endpoint**: independent production-size MC, a validated nuisance generator, untouched truth departures, GENIE v3 | PLAN §4 Stage D |

## Not on the agenda

Submission, deposit, tagging, coauthor or collaboration contact, and NERSC requests stay separately authorized acts of
Joseph's.

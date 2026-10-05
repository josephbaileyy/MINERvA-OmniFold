# Independent review of the publication decision packet (2026-10-05/06)

**CITABLE FOR:** the review's target, its verdicts, each finding, and the owner's resolution.
**NOT CITABLE FOR:** any physics result. This is the owner's checked restatement of the reviewer's report, not a
verbatim transcript. Reviewer agreement is not independent evidence for any number that the reviewer and the
owner both took from the same original calculation (PLAN §1).

| | |
|---|---|
| reviewer | a fresh read-only Opus 5.5 subagent with no prior context. It worked in a detached worktree `MINERvA-OmniFold-pub-review-20261005` and printed a clean `git status` afterward. No Astra session was available in this session. |
| cycle 1 target | `d9a75393` (the packet, claims table, literature, outline, release inventory and handoff) |
| cycle 1 verdict | **ACCEPT WITH CHANGES**: 1 blocking (affecting approval item (4) only), 6 should-fix, 12 notes |
| what the reviewer reproduced | all four s5p output digests, the design and the plan; every row of the claims-table §C proxy distances, from `joint-evaluate.json`; every k, B, p, threshold and interval against the terminal record and recompute report; the ledger quotes VL149/157/160; the 2D status lines; C2 and the coverage window; six arXiv abstracts verbatim; the full-text response passages of 2110.13372 and 1511.05944; the open-data page terms; the `app_release.tex` and `technote.bib` findings; the fallback poll (rc 0) |
| what the reviewer could not verify | `/pscratch` products and digests; Ascencio's χ² values; the MicroBooNE and CMS quotes; the APS length rules; the arXiv-versus-journal version identity; the cluster `seed-states.json` digest |

## Cycle 1 findings and resolutions

| id | severity | finding (short) | resolution, and the operand the owner re-checked |
|---|---|---|---|
| B1 | BLOCKING (item 4) | W2's δ "as read from" Ascencio is impossible, because that paper states no input value. Leaving the lane to pick one would invent a shift (PM-1). | Re-checked: the Ascencio text gives the input only as "determined from hadron calorimetry data taken with a test beam detector". δ is now **0.04**, from the verified Aliaga abstract ("agreements better than 4%"). It is labelled as a single coherent-scale simplification of a test-beam data/simulation agreement bound, not MINERvA's per-particle prescription. Item (4) asks Joseph to accept or replace it. |
| S1 | SHOULD-FIX | Pending outputs were stated as results ("rejects five", "every null is rejected", "universal rejection"). | Reworded to "the pending, unrecorded outputs read `rejected` for all 10 tests; none is certified" in packet §1 and claims §C. "Comparer verdict INCOMPLETE" was added beside 712/712. |
| S2 | SHOULD-FIX | The common-response argument overclaimed: a shift can lower T; Table I of 2106.16210 is independent evidence. | Re-checked by the owner in the full text. Table I standard χ² over 205 bins: Tune v1 6786, GENIE 2.12.6 8241, GiBUU v2019 5800, NuWro 3789–5151. "Would" became "could", with ΔT ≈ 2dᵀW⁻¹(F−μ) + dᵀW⁻¹d. Table I is cited as partial counter-evidence. The concern is rescoped to the 5D **shape** content along the hadronic axes (packet §1, §5.4; claims §C). |
| S3 | SHOULD-FIX | Joint-information value is not on offer against published 2D results, and W1 shows value only relative to coarse projections. | W1 is renamed and scoped to "matched coarse projections". Route A now says W1 and W2 are necessary but not sufficient, and reopening it is Joseph's call. §5.1 adds the other families' 2D failure. This **strengthens** route B. |
| S4 | SHOULD-FIX | W1 was underspecified: the projected shift variants, the missing-seed state, the "as matched" ambiguity. | Each 109-dimensional variant vector (S(c) from the frozen `shift_vector`, ±2 δ_M1) is projected, with no rebuild. Total is matched to total and shape to shape, and both projections must give p ≥ 0.05. W1 runs after D1 **and D2**, and the criterion must hold under both D2 readings (a) and (b). |
| S5 | SHOULD-FIX | W2's mechanism and cost basis were wrong: no recoil universe exists, the npz has no q0, E_avail is primary, and the determinism criterion does not apply. | Re-checked: `s5p_input_dumps.py` `AXES = ("eavail", "q3", "W")`, with no q0. W2 is split into **W2a** (a new event-loop recoil universe, one independent review, a one-playlist cost measurement, ≤ 1 node-hour) and **W2b** (separately approved at the measured cost; 8 node-hour ceiling for W2a and W2b together). The control criterion is now bitwise reproduction of `data_b-_j-.npz`, or failing that the 20-jitter envelope. Holm is re-run on the shifted p's. The data-side approximation for non-central nulls is stated as unmeasured. W2 runs after D2. |
| S6 | SHOULD-FIX | Approval item (1) conflated NOT ADMITTED with NOT READY and ignored the 09-26 completion clause. | Item (1) is reworded: the measurement branch stays NOT ADMITTED; s5p's `publication_readiness` stays NOT READY as recorded; the 09-26 clause governs s5p's own completion; this article's readiness is a separate record. |
| N1 | NOTE | "its review is running" was not in a committed source. | D1 now quotes the committed message of `02df81e6` ("review pending … NOT REVIEWED: do not deploy") and marks the running review as relayed. |
| N2 | NOTE | The calibration's nuisance list was incomplete. | It now lists flux, 34 model bands, the three GEANT bands, MinosEfficiency and the five lateral bands, "none of these a recoil or calorimetric response band". |
| N3 | NOTE | 33.0 is our recomputation, not the published value. | Attributed as "our recomputation 33.04", with Table I 6786/205 for the published figure. |
| N4 | NOTE | The 2D χ² is not a low-recoil result. | Split into low recoil (Ascencio) and the full muon-kinematics plane (Table I). |
| N5 | NOTE | The coverage failure covers the VL162 statistical band, not the 6.87% construction, so "STALE" was too strong. | Now "INCOMPLETE": combined coverage is untested and the statistical band failed. |
| N6 | NOTE | VL156–VL158 do not cover the MnvTune excess (L8). | L8 now cites the figure producers (`make_figures.sh:178–180`, `gen_to_xsec_eavailW.py`, `overlay_eavailW_band.py`) and records that no ledger row was identified. |
| N7 | NOTE | The shifted-variant null medians and SDs were not verified by the recompute. | Stated in claims §C. |
| N8 | NOTE | Approval item (2) omitted D4 and D5. | Added. |
| N9 | NOTE | Outline: §9 should be §5; the 2,151 is a raw `wc -w`; F2 does not exist either. | All three fixed. |
| N10 | NOTE | "24% smaller" is arithmetically "~20% smaller" (the current files are 1.243× larger). | Fixed, keeping OI-55's own wording as quoted. |
| N11 | NOTE | The recompute lane's notification commitment is relayed only, and the review file did not exist yet. | The handoff states "only as a relayed message". This file now exists. |
| N12 | NOTE | Main had moved to `51648245`. | Re-measured at 2026-10-05T23:42Z: `origin/main` `87256e75` (Phase 0 PASS at `15a32b0e`; the determinism array was submitted). D2 is updated. |

**Owner's assessment:** every finding was accepted. None changes the recommendation, and S2, S3 and the reviewer's
answer to question 3 strengthen it. The physics argument now rests on independent published evidence (Table I)
rather than on the pattern of pending outputs alone.

## Cycle 2

[Recorded after the focused re-check.]

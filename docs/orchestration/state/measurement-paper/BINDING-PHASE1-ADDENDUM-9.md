# Binding addendum 9: MP-2 feature-contract amendments from the S2 preflight (2026-10-20)

**By** the paper-tighten lane, as director, under [`BINDING-PHASE1-ADDENDUM-8.md`](BINDING-PHASE1-ADDENDUM-8.md).

**Source:** the session's S2 preflight report, `phase1/mp2/PREFLIGHT-S2.md`, with receipt `preflight_s2.json`
(`882d5657…`). It is report-only and cost 0 node-h. It lands with the session's next PR.

**Timing.** These amendments come before any S2 output exists, as addendum 8 requires.

**CITABLE FOR:** the amendments.
**NOT CITABLE FOR:** any result.

## Amendments to the frozen contract (`feature_contract_draft.json` `98141c2f…`)

1. **GiBUU ID 902 (μ) maps to PDG 13 and is excluded**, like every muon. Read literally, the frozen map would have
   put the muon into E_other in every GiBUU event.
2. **GiBUU ID 1 with charge −1 maps to the antiproton, −2212.** GiBUU codes antiprotons that way, not with negative
   IDs. The other unmapped IDs (Ξ, Λ_c, Σ_c, D, D_s) stay in "other", as declared.
3. **The struck-nucleon mass for multinucleon events.** The default (1.5 M_n + M_p)/2.5 is assigned, as the analysis
   convention assigns it to non-single-nucleon events (`CVUniverse.h:39-44, 397-404`):
   - **GiBUU:** for events with `production_ID` ∈ {35, 36} (2p2h). Ruling (g) of addendum 8 was keyed on the number of
     initial-nucleon rows, which is always one in GiBUU, so it never fired.
   - **NuWro:** for MEC events with two struck nucleons, consistent with GENIE MEC's pair codes and with Tune v1.
   - Every single-nucleon event keeps that nucleon's mass, as frozen.

## Recorded for the record, with no contract change

4. **GiBUU deep-inelastic events on hydrogen** (`production_ID` 34, 46% of the GiBUU-H sample) **do not conserve
   energy.** They lose a median 45 MeV, with a median p_T imbalance of 31 MeV. Non-DIS hydrogen events balance
   exactly. The cause is not identified; GiBUU writing no photons is one candidate. Carbon cannot be checked this way.
   - This is a caveat on the MP3-C GiBUU-on-CH replay, and possibly on the frozen GiBUU product: E_avail of those
     events may be low.
   - It is reported with the replay, in the session's report and in the analysis note's CH subsection. Diagnosing it
     is a later item.
5. **GENIE gst final-state lists omit the primary muon.** S2 reads the muon from `El`/`pxl`/`pyl`/`pzl`. This is an
   implementation note.

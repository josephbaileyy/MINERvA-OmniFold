# Binding addendum 14: size-controlled MP-2 closure rules, the GiBUU charm convention, and the D2 row (2026-10-22)

**By** the paper-tighten lane, as director, from an independent read-only draft that the director reviewed and amended (KNOWN_ISSUES numbering; §7 updated to the steps already run), under
[`BINDING-PHASE1-ADDENDUM-13.md`](BINDING-PHASE1-ADDENDUM-13.md) and Joseph's decision
[`DECISION-20261022-joseph-mp2-gate-rules.md`](../../DECISION-20261022-joseph-mp2-gate-rules.md).

**Timing.**
- The V2/V3 statistics for GENIE CV and GENIE MEC were computed and sealed by jobs 60107470 and 60107471 (ended 07:44
  and 07:45 PDT). Their sha256 are `5f390342…` and `d0a4f9df…`, recorded in the gates files.
- Joseph's decision was recorded at 09:03 PDT, and this addendum after it. **No V2 or V3 statistic has been read.**
- No NuWro or GiBUU V2/V3 statistic exists.
- These rules are therefore fixed before any V2/V3 outcome is known.

**CITABLE FOR:** the V2 and V3 rules, the R12 ruling, the D2 record, and the conditions below.
**NOT CITABLE FOR:** any result, or any claim.

**[Joseph]** items are flagged to him.

## 1. What Joseph decided

DEC:16-19, verbatim: "Size-controlled (Recommended)": a p-value per distribution with a Holm correction across the
family for V3, and a maximum-pull bar corrected for 109 cells for V2. And "Keep 3000 (Recommended)" for the tree cap.

## 2. The MP-2 S2 closure rules

These replace the frozen ones named below, for every G and both feature sets. α = 0.05 per replica and per gate.
Φ̄ is the standard normal upper tail.

| rule | replaces | the rule |
|---|---|---|
| **V2-fine** | nothing (kept) | χ²/ndf ≤ 1.5 over the fine cells with ≥ 20 entries on both sides, as frozen. Its chance failure is about 0 at its ndf. ndf_fine depends on raw counts only and is computed blind; if it is < 200 for any G, the director is told before any verdict is read |
| **V2-J** | "no J cell beyond 3σ" | max over the 109 supported J cells of \|pull_c\| ≤ **3.4970** (Šidák: (1 − 2Φ̄(z))¹⁰⁹ = 0.95). The count of pulls is asserted to be 109 |
| **V3** | χ²/ndf ≤ 1.5 per distribution, and R5b's "no bin beyond 3σ" | Per distribution d: p_χ,d = P(χ²_ndf ≥ χ²_d), with ndf = bins used − 1; p_z,d = 1 − (1 − 2Φ̄(z_max,d))^{n_d} over its n_d used bins; p_d = min(1, 2 min(p_χ,d, p_z,d)). V3 passes iff Holm at 0.05 over the four p_d rejects none, i.e. iff min p_d > 0.0125. Holm-adjusted p's are reported. A distribution with ndf < 1 fails closed |
| **V3-n** | the per-neutron sumw2 | The per-neutron KE distribution uses the event-clustered variance Σ_e (n_e,b w_e)² on both sides |

- **Unchanged:** the 20-entry minimum, R5b's population, the bins (A13 R5), R6's shape closure and s, the
  excluded-bin and support-gap reports, V1, V4, and every other frozen element.
- **Replicas (R3, unchanged).** Every gate must pass on all five replicas.
- **The chance of a statistics-only failure, stated.** Under exact closure the replicas' statistics coincide. Per G it
  is then:
  - 5% for V2-J and 5% for V3;
  - ≤ 9.75% for either;
  - about 0 for V2-fine;
  - about 5e-4 for V1.

  If replica model noise were as large as sampling noise and independent, the bound would be 22.6% per gate and 40.1%
  for both. At release, the across-replica correlation of the J pulls is reported, descriptively.
- **Power, stated.** These are looser per-test bars than the frozen ones (3.50 against 3.0; χ²/ndf of about 2.5–3.2
  against 1.5 at V3's ndf). Every verdict quotes its bar.
- **Release.**
  1. This addendum is merged.
  2. A verdict script (`mp2_s2_verdict.py`; no refit; 0 node-h) is committed with its sha256.
  3. The session records `stat` of each sealed file.
  4. The script verifies each sealed sha256 against its gates file, recomputes V3-n from the stored weights and
     harmonized arrays, applies §2, and writes `verdict_v2v3_<G>_<fset>.json`.

  The sealed files are not modified. The same script serves every G.
- **V5 [Joseph].** V5 is a per-J-cell bar over 109 cells with SD from five replicas, and its chance failure rate is
  likewise uncontrolled. It is not covered by Joseph's decision, and is put to him before any S3 output.

## 3. The tree cap

n_estimators = 3000 stays, by Joseph's decision, with A13's checkpoints and the descriptive 10,000-tree V1 when
V1's best iteration is ≥ 2800.

## 4. R12: GiBUU's undecayed charm

- **Reported** (`s2-receipts/r12_d2_counts.json`): 4,470 GiBUU in-grid events, 7.90e-3 of its in-grid rate, carry
  undecayed Λ_c, Σ_c, D or D_s. Tune C+H, GENIE and NuWro have 0.
- **The contract.** It puts every generator event in the analysis convention before any feature is computed
  (JSON:75), but names no decay convention. The analysis's final-state lists, and MINERvA's response, carry charm's
  decay products.
- **Ruling: harmonize.** GiBUU's charmed hadrons are decayed before any feature or product is computed, and
  addendum 9 item 2 is amended for them. The specification:
  - PYTHIA6 decay tables, as GENIE's decayer uses; otherwise ROOT `TDatabasePDG` channels with `TGenPhaseSpace`,
    declared as a phase-space approximation. The table's sha256 is recorded;
  - decay recursively until every product is a species found in Tune's lists;
  - `default_rng([2026102134, 0x4348])`, in the declared event order, in the generator frame, before the rotation.
- **Fail-closed checks:**
  - four-momentum conservation per decay to 1e-9 relative;
  - no charm remains;
  - branching ratios sum to 1 per parent to 1e-6.

  The species mix, and the shifts of E_avail, of the species sums and of the product per J cell, are reported.
- **Fallback, if a check fails:** the charm events are excluded from GiBUU's training, V1 and V3 samples, as R13. The
  S2 report states which branch applied. **This choice depends only on the checks, never on any gate.**
- **Before the GiBUU fit** (0 node-h): the GENIE CV and MEC gst `charm` rate share in the grid, so the record can say
  whether Tune's generator decays charm or makes none.
- **Order and cost.** A new read-only snapshot (code-v8; code-v7 is the step-memory fix); GiBUU re-harmonized (about 0.03 CPU node-h, debug, within
  tranche A); controls N, H0, A and Z; H_CH,an rebuilt; then the GiBUU `modgates` job on code-v8.
- **[Joseph, informed]** The frozen GiBUU product used by A7 and MP3-C counts no visible energy from undecayed charm
  (`gen_to_xsec5d.py:287-290`), so its E_avail is low in those events.
  - A7's decisions stand (D6).
  - KNOWN_ISSUES row 102 records it.
  - A descriptive readout (0 node-h) of the per-J-cell shift Δμ_c/σ_c, frozen against charm-decayed, is reported
    beside A7, never as a re-grade.

## 5. D2: NuWro's three-muon events

The session's check (`r12_d2_counts.json`, `D2`):
- in all 52 events, `post[0]` is the primary μ⁻;
- the frozen converter's muon is never `post[0]`: it is the μ⁺ in 34 events and a secondary μ⁻ in 18;
- 9 are in the grid, 4.4e-6 of NuWro's in-grid rate, below A13's 1e-4.

No re-run. The harmonized events keep the frozen convention, for consistency with the products A7 used. KNOWN_ISSUES
row 101 records it.

## 6. KNOWN_ISSUES rows (landed by the director)

| # | severity | status / owner | issue | where | opened |
|---|---|---|---|---|---|
| 101 | LOW | **OPEN 2026-10-22** (MP-2 S2, D2; binding addendum 14 §5); owner: the measurement session. No re-run at this size | **The NuWro flat converter (`3d-unfolding/genie/nuwro_to_flat_5d.C:53-62`, "last muon wins") takes a non-primary muon in CC events that carry a μ⁺μ⁻ pair.** There are 52 of 2,374,491 CC events in the frozen NuWro C12 and the MP3-B H samples. The primary is always `post[0]`. The selected muon is the μ⁺ in 34 events and a secondary μ⁻ in 18. Nine are in the grid, 4.4e-6 of the in-grid rate. It affects the frozen NuWro product and MP-2's harmonized NuWro events equally | [S2-IMPLEMENTATION D2](docs/orchestration/state/measurement-paper/phase1/mp2/S2-IMPLEMENTATION.md); `s2-receipts/r12_d2_counts.json` | 2026-10-22 |
| 102 | LOW | **OPEN 2026-10-22** (MP-2 S2, R12; binding addendum 14 §4); owner: the measurement session | **The frozen GiBUU 2019 prediction leaves charmed hadrons (Λ_c, Σ_c, D, D_s) undecayed and counts no visible energy from them** (`3d-unfolding/genie/gen_to_xsec5d.py:287-290`). That covers 4,470 in-grid events, 7.90e-3 of GiBUU's in-grid rate. The analysis convention (Tune's final-state lists) and MINERvA's response carry their decay products, so the frozen GiBUU E_avail is low in those events. MP-2 decays them under addendum 14 §4. A7's decisions stand. The per-J-cell size is reported beside A7 | [binding addendum 14](docs/orchestration/state/measurement-paper/BINDING-PHASE1-ADDENDUM-14.md); `s2-receipts/r12_d2_counts.json` | 2026-10-22 |

## 7. Tranche A after the stop rule

- **Charged:** 1.224 of 3.5, after step 0. Phase 1 stands at 9.109 of 35, as the session reports it.
- **What the stop rule caught.** The NuWro overrun was step-memory serialization: 4 × 120 GiB against a 476 GiB
  allocation. The models were not slow, so this was a launcher defect. It is fixed in code-v7, which reads the memory
  from AllocTRES when SLURM_MEM_PER_NODE is unset.
- **Done, or approved earlier by the director:**
  - step 0, the concurrency test: PASS on code-v7, job 60112509;
  - step 1, NuWro's missing model `k4h1f2` and its gates, on code-v7: job 60112561.
- **Approved here, in order, each after the previous one passes:**
  1. the code-v8 snapshot implementing §4, with its sha list in a PR;
  2. GiBUU's re-harmonization with the §4 checks (about 0.03, debug);
  3. GiBUU `modgates` (about 0.87). Its stop rule is 1.25× the projected wall time.
- **The V2/V3 verdict script** (§2, Release) runs after this addendum is merged, for GENIE CV, GENIE MEC and NuWro,
  and for GiBUU when it exists.
- **Projected total:** about 2.5, within tranche A's 3.5. The stop rule of A13 applies to every job.

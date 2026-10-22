# Analysis behind binding addendum 14 (MP-2 size-controlled gates, R12, D2; 2026-10-22): the independent draft, kept as the reasoning record

**Note (director):** the binding (BINDING-PHASE1-ADDENDUM-14.md) renumbers this draft's KNOWN_ISSUES rows 100/101 to 101/102 (row 100 was already the RC7 release row) and updates its §7 to the steps already run.

Drafted read-only on 2026-10-22 for the director. Nothing here is a ruling until the director commits it.

## How it was read

- **No worktree was created and nothing was fetched.** Commits `2179f869` (main, addendum 13), `2f09d47f` (PR #233
  head) and `d30a2495` (current `origin/main`) were already present in the local object store, so every file was read
  with `git show <sha>:<path>`.
- Nothing was edited, committed or sent.

### No V2 or V3 statistic was read

- The sealed files (`fit/sealed_v2v3_<G>_primary.json`) are cluster-only, and I did not open them.
- From the two open GENIE gates files I read only their key names and the `V2_V3` block, which holds a path and a
  sha256:
  - genie_cv: `5f390342…`
  - genie_mec: `d0a4f9df…`
- The job logs contain one line mentioning V2/V3, the `VERDICT` line "V2_V3: held for Joseph".
- I read `S2-IMPLEMENTATION.md` at `2f09d47f`. It reports V1 and V4 only.

**Sources.** `A13` = `MP/BINDING-PHASE1-ADDENDUM-13.md`, where `MP/` = `docs/orchestration/state/measurement-paper/`.
`DEC` = `docs/orchestration/DECISION-20261022-joseph-mp2-gate-rules.md` (main `d30a2495`). `FIT` = `mp2_s2_fit.py` at
`2f09d47f`, whose sha256 `91c2a64b…` equals the `mp2_s2_fit.py` line of both `code-v5.sha256` and `code-v6.sha256`;
v6 differs from v5 only in `mp2_s2_job.sh`. `S2I` = `MP/phase1/mp2/S2-IMPLEMENTATION.md` at `2f09d47f`.

### Joseph's ruling, as recorded

DEC:16-19 quotes Joseph's answers verbatim. The director wrote the option text; the hash prefix of the answer lines is
`3432fa9cc8b3532b`.

> Gate rules: "Size-controlled (Recommended)" — Replace them now, before any gate output: a p-value per distribution
> with a Holm correction across the family for V3, and a maximum-pull bar corrected for 109 cells for V2.
> Tree cap: "Keep 3000 (Recommended)"

**One fact the addendum must state.** "Before any gate output" is not literally true. The GENIE CV and MEC V2/V3
statistics were computed and sealed by jobs 60107470 and 60107471, which ended at 07:44 and 07:45 PDT. DEC was recorded
at 09:03 PDT. What holds is the decision's own wording, "before any V2 or V3 statistic had been read" (DEC:3-4), and
that is what preserves the ruling's meaning. §2 gives a cheap way to evidence it.

---

## 1. The replacement rules

### 1.1 Every frozen V2/V3 criterion, and its false-fail rate under exact closure

These are false-fail rates for **one replica** under Gaussian pulls, computed with `scipy.stats`.

| criterion (frozen text) | source | false-fail under exact closure | disposition |
|---|---|---:|---|
| V2 fine grid: χ²/ndf ≤ 1.5 over the cells with ≥ 20 entries on both sides | JSON:142; PLAN:223-224 | 2.7e-12 at ndf 500; 6e-6 at ndf 200; about 0 at the expected ndf of thousands | **stays frozen.** Replacing it with a 5% p-value would be a large tightening (about χ²/ndf ≤ 1.04 at ndf 3000) |
| V2 J cells: "no J cell beyond 3σ" (all 109 supported cells; no entry minimum) | JSON:142 | 25.5% | **replaced** (rule V2-J) |
| V3: χ²/ndf ≤ 1.5 per distribution | A8:26 (b) | 13–19% per distribution at ndf 5–10, about 45% over the four | **replaced** (rule V3) |
| V3: "no bin beyond 3σ", over the χ² bins (R5b) | A8:26 (b); A13 R5b | 1.3–2.9% per distribution at 5–11 bins, about 9% over the four | **replaced, inside rule V3** |
| V3 per-neutron sumw2 treats one event's neutrons as independent | S2I R5; A13 R5 | it understates the variance, so p is biased low and the size is **not** controlled for that distribution | **corrected** (rule V3-n) |
| V1: AUC ≤ AUC(G vs G) + 0.005 | JSON:141 | about 5e-4. The difference SE is about 1.5e-3 at GENIE's fold-0 sizes, so the margin is about 3.3 SE | **stays frozen.** Not a per-bin bar, and small |
| V4: ESS/N ≥ 0.3 and max w/⟨w⟩ ≤ 50 | JSON:144 | not a significance test | **stays frozen** |
| V5 (S3): per J cell, SD_k(Δ_hyb) ≤ 0.2 \|mean\| or ≤ 0.1 δ_fine | JSON:145 | a per-cell bar over 109 cells, with SD from K = 5 (4 dof). Its chance failure rate is not controlled either | **not in Joseph's ruling.** Flagged: put it to Joseph before any S3 output |

The frozen V3 rule's total of about 54% per replica, from the χ² and pull parts together, is slightly above A13's
"about 45%", which counted only the χ² part.

### 1.2 Rule V2-J, replacing "no J cell beyond 3σ"

- **Family.** The 109 supported J-cell pulls of one replica, pull_c = (s·T_c − G_c) / √(s²σ²_T,c + σ²_G,c), as
  `FIT:329` computes them with R6's s. α = 0.05 per replica.
- **Method: Šidák.** Šidák's inequality holds for two-sided tests on a multivariate normal under any correlation, so
  the weak coupling of the cells through the common s does not break the bound.
- **The rule.** V2-J passes in replica k iff max_c |pull_c| ≤ **z*₁₀₉ = 3.4970**, where
  (1 − 2Φ̄(z*))¹⁰⁹ = 0.95. The per-cell two-sided p is 4.705e-4; Bonferroni would give 3.5038.
- **Guard.** The code asserts exactly 109 stored pulls (`len(J.pulls) == 109`). Any other count is a stop, not a
  verdict.
- **V2 as a whole** passes in replica k iff the frozen fine-grid rule passes **and** V2-J passes.
- **Fine-grid guard.** The frozen fine-grid rule stands only if ndf_fine ≥ 200.
  - ndf_fine depends on the raw Tune and G entry counts only (`use = (tn ≥ 20) & (gn ≥ 20)`, `FIT:220`), not on
    any weight. It can be computed blind from the harmonized inputs, and is identical across replicas.
  - If ndf_fine < 200 for any G, the director is told before any verdict is read.

### 1.3 Rule V3, replacing V3's χ²/ndf ≤ 1.5 and R5b's per-bin 3σ bar

For each of the four distributions d of one replica (neutron multiplicity at KE > 10 MeV, proton multiplicity at
KE > 20 MeV, π⁰ count, per-neutron KE):

- **The χ² component.** p_χ,d = P(χ²_ndf ≥ χ²_d), with ndf_d = bins used − 1. This is the `p_value` that `FIT:229`
  already stores, except for the per-neutron distribution (rule V3-n).
- **The pull component.** This is R5b, kept rather than dropped: dropping it would loosen more than Joseph ruled.
  p_z,d = 1 − (1 − 2Φ̄(z_max,d))^{n_d}, Šidák over the n_d used bins, from the stored `max_abs_pull_used` and
  `n_bins_used`.
- **The per-distribution p-value** (Joseph's "a p-value per distribution"): p_d = min(1, 2·min(p_χ,d, p_z,d)), a
  Bonferroni combination of the two components.
- **The family.** The four p_d of the replica, with Holm at α = 0.05.
  - V3 passes in replica k iff Holm rejects none of the four, which is iff min_d p_d > 0.05/4 = 0.0125.
  - **Stated plainly:** the pass/fail verdict of Holm equals Bonferroni's. Holm's step-down only identifies *which*
    distributions fail. Holm-adjusted p-values are reported for all four.
- **The rule as bars**, for reading:
  - a distribution fails if p_χ ≤ 0.00625, which is χ²/ndf above about 3.24 at ndf 5, 2.67 at ndf 8 and 2.46 at
    ndf 10;
  - or if its max pull exceeds the Šidák bar at 0.00625: 3.227 (5 bins), 3.359 (8), 3.420 (10), 3.446 (11).
- **Untestable distributions.** If ndf_d < 1, the distribution is "not testable". V3 then fails closed for that
  replica, and the reason is reported.
- **Unchanged:** the 20-entry minimum, R5b's population, the bins (A13 R5), and the reporting of excluded and
  support-gap bins.

### 1.4 Rule V3-n: the per-neutron variance

Under a p-value rule, the per-neutron sumw2 (each neutron independent) makes p_χ too small. The variance is replaced
by the **event-clustered** one, on both sides:
- per bin b: σ²_b = Σ_events (n_e,b · w_e)², where n_e,b is event e's number of neutrons in bin b;
- the pulls and χ² of the per-neutron distribution use σ²_b.

The other three distributions have one entry per event and are unchanged.

### 1.5 How replicas combine (R3), and the overall false-fail rate, honestly

- **R3 stands.** Each gate must pass on all five replicas. α = 0.05 is per replica and per gate, as the director
  proposed. The contract implies nothing else: R3 makes each replica a null that must be valid.
- **Under exact closure** (each replica's w_G equal to the true ratio), the five replicas carry the same weights, so
  their statistics are identical. The sumw2 in every pull is common sampling noise of the same G events and Tune rows.
  The five-replica false-fail is therefore the single-replica one:
  - **5% for V2-J**, and **5% for V3**;
  - **≤ 9.75% for "V2-J or V3"** (1 − 0.95²; the two are not independent);
  - **about 0 for V2's fine grid**;
  - **about 5e-4 for V1**.

  For a G, the overall chance of a statistics-only "not established" is about 10%.
- **The upper bound.** If replica-to-replica model noise were as large as the sampling noise and independent, the
  rates would be 1 − 0.95⁵ = 22.6% per gate and 1 − 0.9025⁵ = 40.1% for both.
  - That noise is not in sumw2. Where it is large, a failure reflects finite-classifier spread, which is a genuine
    property of the null as used, not chance.
  - The true value lies between the two bounds.
- **Descriptive, at release.** The across-replica correlation of the 109 J pulls, and the spread of each V3 p_d,
  locate the true rate between the bounds. Neither is a gate.
- **Power, stated.** Both replacements are **loosenings** of the per-test bars: 3.50 instead of 3.0 for J pulls, and
  χ²/ndf of about 2.5–3.2 instead of 1.5 at V3's ndf. They trade power against small mis-closures for size control.
  The S2 report quotes the bars beside every verdict.

### 1.6 Release protocol

1. Addendum 14 is committed (merged to main).
2. The verdict code is a new script, `mp2_s2_verdict.py`. It refits nothing and costs 0 node-h; it runs on a login
   node or in a debug step. Its sha256 is committed before it runs.
   - For each sealed file: verify its sha256 against the gates file; apply §1.2–1.4; write
     `verdict_v2v3_<G>_<fset>.json` with every component, bar and Holm-adjusted p.
   - V3-n is recomputed from stored arrays (§2).
3. **Before step 2,** the session records `stat` (mtime and atime) of each sealed file. With pscratch's relatime, a
   read after the write would advance atime past mtime. This is evidence, not proof, that no one opened them.
4. NuWro and GiBUU get the same script as their sealed files appear. No rule changes between generators.

---

## 2. Do the code-v5/v6 sealed files hold what the rules need?

Checked against `FIT` (`91c2a64b…`, the code that wrote them) at `2f09d47f`: `chi2_shape` at :213-237, and the sealed
assembly at :331-346.

| needed | stored? | where |
|---|---|---|
| V2 fine: χ² and ndf | yes | `V2.fine.chi2`, `.ndf`, also `.p_value` (:224-229) |
| V2 fine: ndf, blind | yes, and recomputable from raw counts | `.n_bins_used` |
| V2-J: all 109 pulls | yes | `V2.J.pulls`, the full list, and `max_abs_pull` (:345-346) |
| V3: χ², ndf, p per distribution | yes | `V3.<d>.chi2`, `.ndf`, `.p_value` |
| V3: max pull and bins used | yes | `.max_abs_pull_used`, `.n_bins_used` (:230) |
| V3: per-bin pulls | yes | `.pulls_used` is stored when ≤ 200 bins (:231); V3 has ≤ 11. For V2 fine it is `None`, but no rule needs fine-cell pulls |
| **V3-n: event-clustered variance** | **no.** The stored sumw2 is per neutron (:333-337) | recompute, below |

**What must be recomputed.** Only V3-n, at **0 node-h, with no refit**. It needs:
- the per-replica w_G from `weights_<G>_<fset>.npz` (:427; written by the gates job beside the sealed file);
- w_truth, `nKE_val`, `nKE_ev` and `in_support` from the harmonized `tune_CH.npz`;
- `c`, `nKE_val`, `nKE_ev` and the R13 mask from `events_<G>.npz`.

All of these are on pscratch. The recomputed per-neutron χ², pulls and p are written into the verdict file, not the
sealed file, so the sealed sha stays valid.

- **GENIE CV and MEC:** the sealed files exist. The verdict script handles V3-n.
- **NuWro and GiBUU:** no sealed file yet. NuWro's gates did not run (stop rule), and GiBUU waits for R12. They can
  run on the unchanged code-v6, with V3-n applied by the verdict script, so one implementation serves all four.
  Adding V3-n to the gates code would mean a new snapshot and two implementations. Not recommended.

---

## 3. R12: GiBUU's undecayed charm

### Facts

From `s2-receipts/r12_d2_counts.json` (`2f09d47f`):
- **GiBUU-CH:** 4,470 of 1,580,042 in-grid events carry a charmed hadron (Λ_c, Σ_c, D, D_s: GiBUU IDs 56–61 and
  114–121). That is **7.90e-3 of the in-grid rate**, against 0.28% by count, so these events are weighted toward high
  E_ν.
- **Tune C+H (31,658,399), GENIE CV, GENIE MEC, NuWro:** 0.
- Addendum 13 R12's bar was 1e-3, so this is above it.

### What the contract says

- **The governing rule.** JSON:75: "every generator event is put in the analysis convention before any feature is
  computed". FCD:103: "the analysis convention for every generator event, as MP-5 did".
  - The list that follows names the axis, W and NaN-W. It does **not** name a decay convention, so the contract is
    **silent** on stable particles.
- **The particle rules** (JSON:90-95; FCD:127-132) cover exclusions, the ID map, thresholds and de-excitation. They
  say nothing on decays.
- **A9:17-18** put Λ_c, Σ_c, D and D_s in "other", "as declared". That ruling was made before anyone knew Tune has
  none.

### What Tune does with charm

- **What is verified.** No undecayed charm in 31.7M Tune C+H rows. Tune's lists carry K±, K⁰/K̄⁰, K_L, Λ and Σ
  undecayed (`PREFLIGHT-S2.md:79`), and π⁰ stable.
- **Not verified:** that Tune *produces and decays* charm, rather than producing none.
  - GENIE 2.12's decayer decays charmed hadrons, and the same-version GENIE gst samples also show 0 undecayed.
  - The gst `charm` flag would settle it. Condition C1 below counts it (0 node-h).
- **Either way,** MINERvA's response acts on the decay products. Charm decays within cτ ≈ 60–300 µm, long before any
  detector element. Tune's lists are therefore the detector-relevant convention.

### The frozen GiBUU product has the same defect, in a measurement coordinate

- The frozen GiBUU E_avail (`3d-unfolding/genie/gen_to_xsec5d.py:287-290`) counts only ID 1 (charge +1) as proton,
  ID 101 as π, and ID 999.
- An undecayed Λ_c or D therefore adds **nothing** to E_avail. In the analysis convention its products (p, π±, π⁰, γ)
  would add their visible energy.
- So the frozen GiBUU prediction used by A7 and MP3-C has E_avail too low in charm events, for about 0.8% of its
  in-grid rate.
- The S2-harmonized product inherits the same convention under options (a) and (c).

### The options

**(a) Exclude the charm events from GiBUU's training, V1 and V3 samples, as R13.**
- **What the reweighting learns:** GiBUU without its charm production. Tune's own charm-decay events, if any, are
  weighted toward GiBUU's non-charm density.
- **Rate:** the 0.79% is not modelled event by event. c pins the in-support total to H_CH,an, which includes the charm
  events, so that rate is spread over all events.
- **What is left alone:** the product, H_CH,an and V2's comparator keep GiBUU's undecayed convention, with E_avail low
  in those events.
- **Honesty:** a small, stated omission plus a convention mismatch left in the coordinates.
- **Why R13 is not a precedent here.** R13 removed a target Tune's training rows do not have. Charm is physics both
  sides have; only its representation differs.

**(b) Harmonize: decay GiBUU's charm hadrons into the analysis convention before any feature or product.**
- **What the reweighting learns:** like is compared with like. Any remaining difference is physics: GiBUU's charm rate
  and kinematics against Tune's.
- **The product:** the harmonized GiBUU product and H_CH,an change for those events, with E_avail gaining the decay
  products' visible energy. That is the contract's own rule applied to a convention it did not list, exactly as MP-5
  and A9 harmonized others.
- **The cost of honesty:**
  - a decay model GiBUU did not run is introduced, so it must be declared and stated;
  - a phase-space decay is an approximation, though one that matters only through which species carry the energy;
  - the frozen GiBUU product's convention defect becomes visible and must be recorded.
- **"Removing the rest mass from E_other"** is not a harmonization. Tune puts the decay products' energy into p, π±,
  EM and kaon "other" features and into E_avail, not into a rest-mass-free E_other. It would trade one mismatch for
  another. Not recommended.

**(c) Keep and report.**
- **What the reweighting learns:** GiBUU's charm events carry E_other ≥ 1.87–2.29 GeV of rest mass and lack the
  decay products. That is a nearly separable class with no Tune counterpart.
- **V1:** at 0.79% of rate, a perfectly separable class could raise the rate-weighted AUC by up to about
  ½ × 0.0079 ≈ **0.004**, almost the whole 0.005 margin.
- **V4 and the null:** w_G would push weight onto Tune's high-E_other rows (strange production) to fill a region Tune
  cannot reach. V4's tail suffers, and the null's detector-level content for those events reflects a final state the
  detector never sees.
- **Honesty:** any "not established" or tail behaviour would be partly a convention artifact.

### Recommendation: (b), with (a) as the declared fallback, chosen on implementation checks only and never on a gate result

**Specification**, declared in addendum 14 before any GiBUU output:
- **Decay tables:**
  - preferably PYTHIA6's, which GENIE 2.12's decayer uses;
  - if PYTHIA6 is unavailable in `root_6_28`, ROOT `TDatabasePDG`'s decay channels with `TGenPhaseSpace`, declared as
    a phase-space approximation.

  The table file's sha256 is recorded.
- **Recursion:** decay until every product is a species that appears in Tune's final-state lists (p, n, π±, π⁰, γ,
  K±, K⁰/K̄⁰, K_L, Λ, Σ, leptons, ν). Leptons and ν are then excluded as the contract excludes them.
- **Random numbers:** `default_rng([seed_gibuu_ch, 0x4348])`, one stream, events in the declared order j.
- **Frame:** decays done in the generator frame, before the whole-event rotation.

**Checks, fail-closed**, before any fit:
1. Four-momentum conservation per decay, to ≤ 1e-9 relative.
2. Zero charmed hadrons remain.
3. The table's branching ratios sum to 1 per parent, to 1e-6.
4. Report the product species mix, the shift in E_avail and in each species sum for the 4,470 events, and the shift
   of the harmonized product per J cell.

If a check fails, (a) applies. The S2 report says which applied and why.

**Cost and order:**
- Re-harmonize GiBUU on a new read-only snapshot (code-v7; about 0.03 CPU node-h on debug, as harm B took 115 s),
  within tranche A.
- Controls N and H0 use the frozen native readers and frozen numerators, so they are unaffected. A and Z re-run as
  before.
- H_CH,an is rebuilt. Then comes the GiBUU `modgates` job.

**Whose call.**
- The amendment is the **director's**: a harmonization amendment before any GiBUU S2 output exists, as A9 was.
- **[Joseph, informed]:** the finding that the **frozen** GiBUU prediction (A7, MP3-C) counts no visible energy from
  undecayed charm is a convention defect in a published-comparison input. A7's decisions stand (D6).
  - Recommended: a KNOWN_ISSUES row, and a descriptive readout at 0 node-h, beside A7 and never a re-grade, of the J-cell
    shift Δμ_c/σ_c between the frozen GiBUU product and the charm-decayed one.
  - Whether the methods paper mentions it is Joseph's call, through Stage F.

**Condition C1** (0 node-h, login node, before the GiBUU fit). Count the gst `charm == 1` events in the GENIE CV and
MEC in-grid samples, which use Tune's generator version, and report their rate share beside GiBUU's 7.9e-3. This tells
"Tune decays charm" from "Tune makes none". The recommendation is the same either way; the record's wording is not.

---

## 4. DRAFT ADDENDUM 14

```markdown
# Binding addendum 14: size-controlled MP-2 closure rules, the GiBUU charm convention, and the D2 row (2026-10-22)

**By** the paper-tighten lane, as director, from an independent read-only draft that the director reviewed, under
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
- **Order and cost.** A code-v7 read-only snapshot; GiBUU re-harmonized (about 0.03 CPU node-h, debug, within
  tranche A); controls N, H0, A and Z; H_CH,an rebuilt; then the GiBUU `modgates` job on the code-v6 job script.
- **[Joseph, informed]** The frozen GiBUU product used by A7 and MP3-C counts no visible energy from undecayed charm
  (`gen_to_xsec5d.py:287-290`), so its E_avail is low in those events.
  - A7's decisions stand (D6).
  - KNOWN_ISSUES row 101 records it.
  - A descriptive readout (0 node-h) of the per-J-cell shift Δμ_c/σ_c, frozen against charm-decayed, is reported
    beside A7, never as a re-grade.

## 5. D2: NuWro's three-muon events

The session's check (`r12_d2_counts.json`, `D2`):
- in all 52 events, `post[0]` is the primary μ⁻;
- the frozen converter's muon is never `post[0]`: it is the μ⁺ in 34 events and a secondary μ⁻ in 18;
- 9 are in the grid, 4.4e-6 of NuWro's in-grid rate, below A13's 1e-4.

No re-run. The harmonized events keep the frozen convention, for consistency with the products A7 used. KNOWN_ISSUES
row 100 records it.

## 6. KNOWN_ISSUES rows (landed by the director)

| # | severity | status / owner | issue | where | opened |
|---|---|---|---|---|---|
| 100 | LOW | **OPEN 2026-10-22** (MP-2 S2, D2; binding addendum 14 §5); owner: the measurement session. No re-run at this size | **The NuWro flat converter (`3d-unfolding/genie/nuwro_to_flat_5d.C:53-62`, "last muon wins") takes a non-primary muon in CC events that carry a μ⁺μ⁻ pair.** There are 52 of 2,374,491 CC events in the frozen NuWro C12 and the MP3-B H samples. The primary is always `post[0]`. The selected muon is the μ⁺ in 34 events and a secondary μ⁻ in 18. Nine are in the grid, 4.4e-6 of the in-grid rate. It affects the frozen NuWro product and MP-2's harmonized NuWro events equally | [S2-IMPLEMENTATION D2](docs/orchestration/state/measurement-paper/phase1/mp2/S2-IMPLEMENTATION.md); `s2-receipts/r12_d2_counts.json` | 2026-10-22 |
| 101 | LOW | **OPEN 2026-10-22** (MP-2 S2, R12; binding addendum 14 §4); owner: the measurement session | **The frozen GiBUU 2019 prediction leaves charmed hadrons (Λ_c, Σ_c, D, D_s) undecayed and counts no visible energy from them** (`3d-unfolding/genie/gen_to_xsec5d.py:287-290`). That covers 4,470 in-grid events, 7.90e-3 of GiBUU's in-grid rate. The analysis convention (Tune's final-state lists) and MINERvA's response carry their decay products, so the frozen GiBUU E_avail is low in those events. MP-2 decays them under addendum 14 §4. A7's decisions stand. The per-J-cell size is reported beside A7 | [binding addendum 14](docs/orchestration/state/measurement-paper/BINDING-PHASE1-ADDENDUM-14.md); `s2-receipts/r12_d2_counts.json` | 2026-10-22 |

## 7. Tranche A after the stop rule (for the director's decision)

- **Charged:** 1.204 of 3.5 (S2I, tranche A table). Phase 1 stands at 9.089 of 35 (`LEDGER.tsv`, re-summed).
- **What the stop rule caught.** The NuWro overrun was step-memory serialization: 4 × 120 GiB against a 476 GiB
  allocation. The models were not slow, so this was a launcher defect.
- **Approved, in order:**
  1. the debug concurrency test of code-v6 (≤ 0.04);
  2. NuWro's missing model `k4h1f2` and its gates (about 0.35);
  3. GiBUU's re-harmonization (about 0.03);
  4. GiBUU `modgates` (about 0.87).
- **Gates on each step:** each needs the previous one to pass. Steps 3 and 4 come after code-v7 and §4's checks.
- **Projected total:** about 2.5, within tranche A's 3.5. The stop rule of A13 applies to every job.
```

---

## 5. Notes for the director

1. **KNOWN_ISSUES numbering.** Rows 100 and 101 assume the highest row on `d30a2495` is 99, which is what I measured.
   Re-measure before landing.
2. **"Before any gate output" is not literally met** for GENIE (sealed at 07:44/07:45; DEC at 09:03). The draft
   states this in Timing and rests on "not read". The `stat` atime evidence (§1.6) is cheap and worth requiring.
3. **The V3 rule embeds R5b** as a second component of each distribution's p-value. If the director prefers Joseph's
   words read narrowly (the χ² p only), R5b's pull bar must still be either size-controlled or explicitly withdrawn.
   Dropping it silently would be a loosening beyond his ruling.
4. **R12 (b) changes the GiBUU harmonized product and H_CH,an.** That is intended: it is the contract's own rule. It
   also makes the frozen GiBUU product's defect visible, which is why Joseph is informed.
5. **I have not verified** that `root_6_28` has PYTHIA6 or `TDatabasePDG` decay channels for every charm parent. The
   fallback (a) exists for exactly that case.

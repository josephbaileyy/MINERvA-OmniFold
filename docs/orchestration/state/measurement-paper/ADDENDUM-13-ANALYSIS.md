# Analysis behind binding addendum 13 (MP-2 S2 rulings, 2026-10-22): the independent draft, kept as the reasoning record

Drafted read-only on 2026-10-22 for the director. Nothing here is a ruling until the director commits it.
It was read through a scratch worktree of `pr231` (`dac42a09`). No file in any worktree was edited, nothing was
committed, and no one was contacted.

Path abbreviations:
- `MP/` = `docs/orchestration/state/measurement-paper/`
- `S2I` = `MP/phase1/mp2/S2-IMPLEMENTATION.md`
- `FCD` = `MP/phase1/mp2/FEATURE-CONTRACT-DRAFT.md`
- `JSON` = `measurement-paper/phase1/mp2/feature_contract_draft.json` (the frozen form)
- `FIT` = `measurement-paper/phase1/mp2/mp2_s2_fit.py`
- `HARM` = `measurement-paper/phase1/mp2/mp2_s2_harmonize.py`
- `A8`, `A9` = `MP/BINDING-PHASE1-ADDENDUM-8.md`, `-9.md`; `BIND` = `MP/BINDING-PHASE1-20261019.md`

**Items marked [JOSEPH] need Joseph's decision, or need him told before the director acts.**

---

## 0. What I verified, and what I did not

**Verified, in the PR #231 tree:**
- **The frozen contract.** `shasum -a 256 JSON` = `98141c2f22f4…6630cd`. That is A8's frozen sha, and the one `FIT:36`
  asserts.
- **The ledger.** The `charged_cpu_node_h` column of `MP/phase1/LEDGER.tsv` sums to **7.88466**. The 8 S2 jobs
  (60101975–60102387) sum to **0.28223**. Both match the PR.
- **The code that produced the outputs.** `mp2_s2_harmonize.py` at head is `3e1ad6e2…`, the same in `code-v3` and
  `code-v4` (`s2-receipts/code-v3.sha256`, `code-v4.sha256`). `code-v2` has `e663d2d3…`. `mp2_s2_fit.py` is
  `e0819fb7…` at head and in v2, v3 and v4. The probe log prints the v4 list (`logs/mp2s2-s2probe-60102387.out`).
- **Every number in the S2I harmonization and control tables** checks against `harm_a/` and
  `harm_b/s2_harmonize.controls.json`. That covers N, A, Z, H0, the counts, the rates and the H shares.
- **The probe** (`logs/mp2s2-s2probe-60102387.out`).
  - Best iterations: 3000, 2973, 2970 and 2997.
  - fit_s: 120.0–123.9. predict_s: 20.0–23.5. wall_s: 152.1–160.8.
  - n_train: 3.60M Tune and 1.14M GiBUU.
  - Job elapsed 353 s (ledger), so about 190 s of load and teardown.
- **The code paths behind each reading.** Cited with file:line in §1.
- **MAT's E_avail.** `CVUniverse::GetEAvailableTrue` has no threshold (`MINERvA101/MINERvA-101-Cross-Section/event/CVUniverse.h:361-372`).
- **The frozen NuWro converter.** It takes the **last** particle with `pdg == ±13` in `e->post` as the muon
  (`3d-unfolding/genie/nuwro_to_flat_5d.C:53-62`, comment "last muon wins").
- **The GiBUU H jobcard.** It differs from the frozen C12 card only in `target_Z`, `target_A`, `include2p2hQE` and
  `numEnsembles` (`measurement-paper/phase1/mp3c/mp3c_card.py:6-8, :17-20`; checked by MP3-C C0).

**Not verified:**
- Anything only on the cluster: the pool files, the model files, `fit_probe/`, `preflight_s2.json`.
- Whether NuWro writes the primary lepton first in `post`. See D2.
- Whether Perlmutter's `maintenance_20261021` ended early. See §5, item 6.
- The contents of `mp2_s2_harmonize.py` `0c92db3b…` and `9dbcde93…`. Neither is in the repository.

---

## 1. Rulings R0–R13

### R0. E_avail: MAT's function with no threshold

- **Question.** Does the 10 MeV photon drop apply to E_avail?
- **Sources.**
  - FCD:122-123: "E_avail is MAT's `GetEAvailableTrue` … over the harmonized list, on both sides. S1's control C3
    shows that it reproduces `MC_eavail` bitwise for Tune v1."
  - JSON:95 (`de_excitation`): "photons below 10 MeV are dropped from every feature".
  - FCD:130 gives the species thresholds.
  - Addenda 8 and 9 are silent.
- **Options.**
  - (a) MAT's function as written, on the unthresholded list. This is the session's reading.
  - (b) MAT's function on the thresholded list.
- **Recommended: (a).**
- **Reason.**
  - E_avail is one of the five measurement coordinates. It must be the analysis definition: the grid, r_h, ρ and every
    frozen product are binned in it.
  - Under (b), Tune's E_avail would no longer equal `MC_eavail`, which the contract itself certifies bitwise (S1 C3).
    The contract's two sentences can only be reconciled by reading "every feature" as "every feature other than the
    measurement coordinates".
  - Only E_avail is affected: pT, p∥, q3 and W do not depend on photons.
- **Consequence.** Immaterial in size.
  - Below 10 MeV there are 116 photons in 2,451,873 Tune C rows of 1A, and 5 on H (`PREFLIGHT-S2.md:59-62`).
  - Generators have 0–9 per roughly 100k events.
  - Tune's oxygen de-excitation lines stay in `MC_eavail` on the O rows, which keep r_h and are not trained.
- **Record.** E_avail is the analysis coordinate. The γ < 10 MeV drop and the species thresholds apply to the species
  sums, the multiplicities and the leading-particle features.

### R1. The validation draw and its seed

- **Question.** How are the 10% validation rows drawn, and with what seed?
- **Sources.**
  - JSON:111: "10% of each fold's training rows (seeded), weighted binary logloss".
  - FCD:177.
  - No validation seed appears in JSON:123-133.
- **Options.**
  - (a) A per-class Bernoulli(0.1) draw on the model's training rows (after the ≤ 4M Tune subsample), with
    `default_rng([lgbm_random_state_k, h, f])`, and `[v1_split_seed, 1]` / `[gvg_split_seed, 1]` for V1 and its
    control. This is the session's reading (`FIT:125-131`).
  - (b) A pooled draw over both classes.
  - (c) A new seed constant.
- **Recommended: (a).**
- **Reason.** It is a deterministic function of declared seeds, recorded before any production output, and it keeps
  both classes in every validation set. Option (c) adds nothing. Option (b) could leave a class thin in validation.
- **Consequence.** None for physics. It fixes the determinism of early stopping.
- **Also record.** The V1 and control classifiers use `random_state = v1_split_seed` and `gvg_split_seed`
  (`FIT:305, :316`). The contract is silent there; this is reading **R1b**, accepted.

### R2. The domain of c

- **Question.** Over which rows is "the in-grid C+H content Σ w_truth w_G" equated to H_CH,an's?
- **Sources.**
  - JSON:116: "c fixed so that the in-grid C+H content sum(w_truth w_G) equals that under the reference hybrid
    H_CH,an".
  - FCD:186-187.
  - JSON:135 and FCD:156-160: Tune rows outside G's E_ν support keep r_h.
- **Options.**
  - (a) The Tune C+H in-grid rows inside G's support, the rows that carry w_G, with one c per (G, replica). This is the
    session's reading (`FIT:246`).
  - (b) All in-grid C+H rows, with the out-of-support rows entering at r_h on the event side and at r_an on the
    reference side.
- **Recommended: (a).**
- **Reason.** Under (b), c would absorb Σ w (r_an − r_h) over rows the classifier never weights. That is a
  reference-versus-A7 difference, not anything w_G does. Option (a) normalizes exactly the population w_G applies to.
- **Consequence.** It is exact for GENIE and NuWro, whose support runs to 100 GeV. For GiBUU (0–20 GeV), the
  E_ν > 20 GeV rows (about 5% of σ_CC, KNOWN_ISSUES 82) are outside c and keep r_h.
- **Condition carried to S3.** The rows outside w_G's domain (other nuclei and out-of-support rows) carry r_h in
  J_event but r_an in the primary reference J_hyb(H_CH,an). So the primary Δ_hyb would contain Σ (r_h − r_an) over
  those rows, which is not a hybridization effect. That contradicts the stated purpose of the primary reference
  (FCD:254-255: "isolates the effect of hybridization from the target and convention effects").
  - Before any S3 output, the session commits an S3 reading. Either J_event's non-domain rows carry the weight of the
    reference each Δ_hyb is taken against, or the residual is computed and reported as its own term.
  - [JOSEPH, informed] This bears on what the primary Δ_hyb means. It is not ruled here.

### R3. V2–V4 on every replica

- **Question.** Which replicas do V2–V4 apply to?
- **Sources.** FCD:241-246 (order) and JSON:146 name no replica. Each replica's weights feed its own S3 unfold
  (FCD:250-253).
- **Options.**
  - (a) All five, and the gate passes only if all five pass. This is the session's reading.
  - (b) Replica k = 0.
  - (c) The replica-mean weight.
- **Recommended: (a).**
- **Reason.** Every replica's w_G is used as a null in S3, so every one must be a valid null. Option (c) tests a
  weight no unfold uses.
- **Consequence.** It is the strictest reading. With the false-fail rates in §1a, it raises the chance that a G is
  "not established" on statistics alone. That is disclosed, not offset.

### R4. V1 on replica k = 0

- **Question.** V1 is declared as one classifier per G ("8 V1 classifiers", FCD:275; JSON:160) but names no replica.
- **Options.**
  - (a) k = 0 by position, chosen before any result. This is the session's reading.
  - (b) All five, at 5× the V1 cost.
- **Recommended: (a).**
- **Reason.** It matches the declared count, and the choice is positional and made before any result. V5 covers
  the spread across replicas at S3.
- **Consequence.** V1 certifies replica 0 only. The S2 report says so.

### R5. The V3 bins, and an unrecorded pull reading (R5b)

- **Sources.**
  - FCD:149-153 and JSON:103 name the four held-out distributions.
  - A8:26 ruling (b): "χ²/ndf ≤ 1.5 over the bins with at least 20 entries on both sides, and no bin beyond 3σ".
  - No bins are declared anywhere.
- **R5, the bins.** Accept the session's bins (S2I:73; `FIT:59-61`), now declared before any fit:
  - neutron multiplicity (KE > 10 MeV) and proton multiplicity (KE > 20 MeV): 0…9 and ≥ 10;
  - π⁰ count: 0…5 and ≥ 6;
  - per-neutron KE edges: 0, 10, 20, 50, 100, 200, 500, 1000, 2000 and ∞ MeV.

  The per-neutron sumw2 treats the neutrons of one event as independent. That **understates** the variance, so it
  inflates χ², which errs toward failing. Accept, stated.
- **R5b, the 3σ rule's population. This reading is not in S2I.**
  - `FIT:291` applies "no bin beyond 3σ" only over the bins used for χ² (≥ 20 entries on both sides).
  - A8(b) can be read either way.
  - **Recommended: accept the restriction.** A Gaussian pull is no more valid than a Gaussian χ² below 20 entries.
    This also matches V2's fine-cell rule.
  - **Condition.** Every excluded bin is reported with each side's content share. A bin where one side has ≥ 20 and the
    other < 20 is reported as a support gap.
  - The session adds R5b to S2I before the gates run.

### R6. Shape closure for V2 and V3 [JOSEPH]

- **Question.** V2 says "closure … within the summed sumw2" (JSON:142). Tune's C+H content and G's CH product are in
  different normalizations. Is V2 an absolute or a shape test?
- **Sources.**
  - JSON:142.
  - PLAN:223-224: "closure of the fine 5D and J marginals against `gen5d` within the products' `sumw2`".
  - JSON:116: c pins the rate to H_CH,an's.
  - FCD:167-168: there is only one global constant.
- **Options.**
  - (a) **Shape closure.** Scale s = ΣG / ΣT over the fine grid; ndf = cells − 1; the same s on the J cells. This is
    the session's reading (`FIT:194-206`).
  - (b) Absolute closure. This needs Tune's C+H nucleon count and flux normalization, which are not in the S2 inputs.
- **Recommended: (a).**
- **Why (a) costs the classifier test nothing.**
  - `FIT:246` gives c_k Σ w_truth odds_k = Σ w_truth r_an over the same rows. So ΣT = Σ w_truth r_an for every replica,
    and s = ΣG / Σ w_truth r_an.
  - s therefore **does not depend on the classifier**. It is fixed by H_CH,an and G alone.
  - The rate of the event-level null is H_CH,an's by construction (contract §4). An absolute V2 would test H_CH,an's
    normalization chain, not w_G.
  - The "unknown nucleon-share constant" is the rate itself, which the contract already assigns to the hybrid. It is
    absorbed by s and nothing else.
- **Conditions.** Both are report-only and cost 0 node-h.
  1. The gates assert that s is equal across the five replicas, to ≤ 1e-12 relative. This is an internal check that
     the R2 normalization is what it claims to be.
  2. The S2 report gives s, ΣG, the G-only fine-cell share g0, and a consistency identity: s × k_T × f_CH,an = 1, where:
     - k_T is Tune's counts-to-cross-section factor (Σ in-grid w_truth over all rows, divided by Σ D·dV from
       `mnvtune_v1_xsec5d.npz`);
     - f_CH,an = Σ_C+H, in-support w_truth r_an / Σ_all in-grid w_truth r_an.

     Agreement to about 1e-3 (net of cells outside the only-cells) shows that the constant is fully explained. A
     disagreement is reported before S3.
- **Consequence for the measurement.**
  - V2 and V3 certify the **shape** of the event-level null, at the hybrid's rate.
  - Because ΣT is fixed to the hybrid's content, which already contains G's G-only-cell rate redistributed by
    `fine_ratio`'s fallback, the G-only rate appears in V2 as a uniform excess of g0 in the shared cells. That is the
    null as S3 will use it, and so the right object to test.
  - No decision changes.
- **Why Joseph.**
  - The paper and note must describe V2 as "shape closure at the hybrid's rate", not "closure".
  - If Joseph wants an absolute-rate test of the event-level null, it needs a contract change and the analysis's C+H
    nucleon count. That is his call.

### R7. The V1 control protocol (see also R10)

- **Sources.**
  - JSON:141: "the control trained on G halves of the same sizes with n_estimators FIXED to the V1 classifier's best
    iteration".
  - FCD:221-222.
- **Session's reading.** G is split into halves A and B with `gvg_split_seed`. The protocol is V1's (50/50, 10%
  validation), with n_estimators fixed to V1's best iteration (`FIT:312-320`).
- **Recommended: accept the protocol and the capacity matching, and adjust the sizes as in R10.**
  - Under R10's fold-matched V1, V1's G sample is G-fold 0 (n_G0 events). The control then takes **two disjoint random
    subsets of all G events, each of n_G0 events**, drawn with `gvg_split_seed`.
  - That is possible because n_G ≈ 5 n_G0. It meets "G halves of the same sizes" on the G side exactly, which the
    pooled reading cannot.
  - The control involves no w_G, so drawing it from all folds leaks nothing.
  - The Tune side (≤ 4M rows) cannot be size-matched with G under any reading. Stated.
- **Consequence.** The control's AUC noise is about 1.5e-3 at n_G0/2 test events per side, against a 0.005 margin.

### R8. The G-fold index j and the G-fold formula

- **Sources.**
  - JSON:120: "G-fold = splitmix64(j XOR (fold_key_k + 1)) mod 5 over the generator event index j".
  - FCD:201: "keyed by fold_key_k + 1".
  - JSON:80: the rotation draw is "one uniform per generator event in the declared file order (C12 main, C12
    supplement, H main, H supplement; entries in file order, CC or not)".
- **Session's reading.**
  - j is the entry index in that order, the same index the ν draw uses.
  - The JSON formula is taken literally, with no `>> 1` (`FIT:94-95`).
  - Checked: `HARM:204` sets `j = np.nonzero(keep)[0]` over the concatenated entries. The GiBUU tasks are read in
    numeric order, 1..80 then 1001..1080 (`HARM:412-413`).
- **Recommended: accept.** The JSON is the sha-frozen form. G has no half structure, so the parity bit is harmless.
  The ν draw (an RNG stream) and the fold (a hash) share j but cannot correlate.
- **Consequence.** None.

### R9. The V4 domain

- **Sources.** JSON:144: "Kish ESS of w_truth x w_G over the Tune C+H in-grid rows >= 0.3 N, N = the row count";
  A8:27, ruling (c).
- **Options.**
  - (a) The in-support rows that carry w_G, with N their count. This is the session's reading.
  - (b) All in-grid C+H rows, with r_h outside the support.
- **Recommended: (a).**
- **Reason.** V4 tests w_G, and w_G is undefined outside the support. Option (b) would grade A7's r_h inside an
  MP-2 gate.
- **Condition.** The S2 report gives the out-of-support row count and its w_truth share per J cell. FCD:160 already
  requires that share.
- **Consequence.** It matters only for GiBUU.

### R10. V1's held-out property

- **Question.** What are "G's held-out events" (JSON:141)?
- **The problem with the session's reading.**
  - The session uses all of G's events against a 4M pooled sample of Tune rows (`FIT:299-304`).
  - Each Tune row of fold f was weighted by a model trained on G-folds ≠ f, so 4/5 of the G events V1 compares against
    trained that row's weight.
  - If w_G has learned any feature of its own G training sample, V1 is biased toward **passing**.
- **Options.**
  - (a) Pooled, with the limitation stated. This is the session's reading.
  - (b) **Fold-matched**, one fresh classifier, which keeps the contract's "a fresh classifier" and the 8-classifier
    count. The sample is the Tune rows of replica 0's fold f = 0 (both halves; ≤ 4M by `v1_split_seed`), weighted
    w_truth·w_G, against the G events of G-fold 0 (k = 0 key). Both sides are held out from the models that weight
    those Tune rows (models (0, 0, 0) and (0, 1, 0)).
  - (c) Five fold-matched classifiers, with the AUCs averaged. That is 5× the cost, and it departs from "a fresh
    classifier".
- **Recommended: (b) as the gate, with (a) run beside it as descriptive.**
- **Reason.**
  - (b) meets every word of JSON:141: pooled held-out Tune rows, at most 4M, G's held-out events, one fresh
    classifier. (a) does not meet "held-out" on the G side.
  - (b) trades statistics for the absence of leakage. The test AUC SE is about 8e-4 at roughly 1.3e5 G test events,
    which is 6 SE inside the 0.005 margin.
  - Running (a) beside it shows how much the leakage moves the AUC. That is useful for S4.
- **Consequence.** It is stricter than (a). It costs 2 extra fits per G for the descriptive (a), about 0.1–0.15
  CPU node-h in all.
- **Note for the director.** This is a judgement, leakage against power. It is the director's reading, not Joseph's.
  No result exists.

### R11. The struck nucleon

- **Sources.**
  - FCD:116-120, the W mass rule.
  - JSON:35, 44, 53, 60.
  - A8:31, ruling (g).
  - A9:19-24, amendment 3: the default mass for GiBUU `production_ID` ∈ {35, 36} and for NuWro two-nucleon MEC.
- **Session's reading.**
  - GENIE: `hitnuc` (2112/2212, else default).
  - NuWro: `in[1].pdg` when n_in = 2; default for n_in = 3 or 1 (`HARM:341-342`).
  - GiBUU: the unique perweight-0 ID-1 row by charge; default for 35/36 or a non-unique row (`HARM:391-393`).
- **Recommended: accept.** It is A9 amendment 3 as implemented.
  - NuWro's n_in = 1 events (15,340 C12-main CC) are coherent-type events with no struck nucleon. The default mass
    matches GENIE's coherent `hitnuc = 0` and the analysis.
  - GiBUU's 321,667 default-mass CC events agree with the preflight's 16.6% 2p2h share of C12.
- **Consequence.** None beyond A9.

### R12. Unmapped GiBUU IDs

- **Sources.**
  - JSON:92: "anything else -> 'other'".
  - A9:17-18: "The other unmapped IDs (Ξ, Λ_c, Σ_c, D, D_s) stay in 'other', as declared".
- **Session's reading.**
  - Each unmapped (ID, charge) gets a code below 1e9 that is outside p, n, π±, π⁰ and γ, so it enters E_other.
  - IDs 901 and 903, and negative IDs, stop the job (`HARM:396-398`).
  - Seen in the full samples (`harm_b/…controls.json`): 53, 56, 57, 59, 114 and 118, with (56, +1) Λ_c at 4,794 (C12)
    and 5,796 (H).
- **Recommended: accept.** It is fail-closed on anything undeclared. The contract's "negative ID → antiparticle"
  clause never fires (`PREFLIGHT-S2.md:106`).
- **Condition, before submission (login node, 0 node-h, report only).** Count the undecayed charmed hadrons
  (|pdg| 411, 421, 431, 4122, 4112/4212/4222, 4132/4232, 4332) in the Tune C+H final-state lists, the GENIE gst lists
  and the NuWro `post` lists, and give the GiBUU rate beside them.
  - GiBUU leaves Λ_c and D undecayed, and their E_other carries ≥ 1.87–2.29 GeV of rest mass.
  - If Tune decays charm while GiBUU does not, that is a **convention** difference the classifier can learn, about
    0.3% of GiBUU events. It must be known before V1 is read.
  - If the count shows a mismatch above 1e-3 of in-grid rate, the director rules on it before the GiBUU fit. Otherwise
    it is a stated caveat.

### R13. GENIE atomic-electron targets: rule differently from the session

- **Sources.**
  - JSON:33: "C12 rows tgt == 1000060120, H rows tgt == 2212".
  - JSON:70 and FCD:89: "**train only on C and H rows on both sides** … The target is never a feature."
  - JSON:72: "any such row is a target-identity signal the classifier can learn".
  - Precedent, `MP/phase1/mp3a/REPORT.md:159`: "The code-11 (ν–e) events are excluded from C-only, as the spec reads,
    and are kept in μ_CH, as frozen."
- **Session's reading.** `tgt == 11` events stay in G's events (labelled target 0) and in the harmonized product
  (`HARM:258, :263`).
- **Options.**
  - (a) Keep them everywhere. This is the session's reading.
  - (b) **Keep them in the harmonized product** (V2's comparator, H_CH,an, control N), as frozen, but **exclude them
    from G's training, V1 and V3 samples**.
  - (c) Drop them everywhere. That breaks the frozen product that N reproduces.
- **Recommended: (b).**
- **Reason.**
  - The contract's target rule is explicit, and it excludes non-C/H rows on the Tune side (the 174 Z = 0 rows keep
    r_h).
  - A G-side electron-target event is a pure target-identity signal with no Tune C+H counterpart.
  - (b) is MP3-A's precedent applied to S2.
- **Consequence.** Immaterial in size.
  - In phase space: CV 1 + 8 and MEC 0 + 16 (`mp3a/REPORT.md:53`).
  - Zero weight in all 109 J cells.
  - It needs a one-line filter in `FIT` `load()` (`ev["tgt"] != 0` for the training, V1 and V3 samples) and a new
    immutable snapshot.
- **Record correction.** S2I:81 gives "CV main: 35 of 2,000,000 entries; supplement 11; MEC main 17". These are entry
  counts that no receipt carries. The receipts count **CC** events with `tgt == 11`: CV main 1, CV supplement 8, MEC
  main 0, MEC supplement 17 (`harm_a/s2_harmonize.controls.json`, `targets_*`). S2I should cite the receipt, and its
  "MEC main 17" reads as a supplement count.

### 1a. A property of the frozen V2 and V3 thresholds [JOSEPH]

This is not a reading, so it is not ruled here, but it governs how a FAIL must be read. These are false-fail rates
under **exact** closure (Gaussian pulls; computed with `scipy.stats.chi2.sf`):
- **V3, χ²/ndf ≤ 1.5.**
  - At ndf 5, 9 and 10, it fails 18.6%, 14.1% and 13.2% of the time. The V3 distributions have ndf of about 5–10.
  - Over four roughly independent distributions, that is about 45% per replica.
  - At V2's fine-grid ndf (thousands), it is about 0.
- **V2, "no J cell beyond 3σ" over 109 J cells.** 1 − 0.9973¹⁰⁹ ≈ **26%** per replica.
- **Across replicas.** The five replicas share G's and Tune's events, so they are highly correlated and add only a
  little to these rates.

So an S2 "not established" can arise from statistics alone with probability well above a half.
- The rules are frozen (BIND:46-49; A8:26). Loosening them because of this would be a contract change, and a
  loosening.
- **The draft does not change them.**
- **Condition.** The gates report each χ²'s p-value and each J cell's pull, so that a statistical FAIL can be told
  from a gross one.
- **[JOSEPH]** Whether to replace them, before any gate output, with size-controlled rules (for example, a p-value
  per distribution with Holm over the family, and a J-cell max-pull bar corrected for 109 cells) is a methods
  decision. It changes what "established" can mean. If it is to change, it must be committed before the gates job
  runs.

---

## 2. The four disclosures

### D1. The GiBUU Z control, redefined twice: accept the current definition as a corrected control, recorded as post hoc

**What the contract says.** "the generator ν is along +z; asserted per event, GiBUU included" (JSON:82). For GiBUU
this cannot be implemented as written:
- FinalEvents carries no ν vector and no remnant (`PREFLIGHT-S2.md:132`).
- An unbalanced event cannot tell a tilt from a missing particle.

The session's Z is its own diagnostic, not a contract gate (S2I:31).

**Each step, judged.**
1. **First definition** (non-DIS H, |ΔpT| ≤ 1 MeV) failed on 337 events, at most 91 MeV.
   - Every one is short 0.940–0.943 GeV of energy (0.1/0.5/0.9 quantiles).
   - That is a nucleon of a few MeV of kinetic energy, not written. A 91 MeV/c nucleon has KE ≈ 4.4 MeV.
   - A ν tilt balances energy, so these events cannot test the tilt. **This was a correction.**
2. **Second definition** (energy-balanced, any channel) failed on 3,074 DIS events.
   - A9:28-34 already records that GiBUU DIS final states do not conserve energy or momentum (median pT imbalance
     31 MeV).
   - Dropping the non-DIS restriction of the first definition was the error. **This was a correction.**
3. **Current definition** (non-DIS **and** energy-balanced) is the intersection of the two earlier populations.
   - The 1 MeV tolerance never moved.
   - Both exclusions use properties that do not depend on the ν direction: energy is a scalar, and production_ID is
     the channel.
   - The passing population is 822,359 events with max |ΔpT| = 1.26e-6 GeV (`harm_b/…controls.json` `Z_h`), about
     800× inside the tolerance.

**Why this is not goalpost-moving.**
- Moving the goalposts would mean loosening the tolerance, or excluding events *because* they fail.
- Here each excluded class was identified by an independent signature, and both signatures were anticipated in the
  record: MP3-C's B1 saw the missing nucleon (6 of 19,148), and A9 item 4 records DIS.
- The failing numbers are kept.

**What it establishes.**
- ν ∥ +z for GiBUU, measured on complete non-DIS H events.
- It carries to GiBUU C12 **by configuration, not by measurement**: the H card differs from the frozen C12 card only
  in target_Z, target_A, include2p2hQE and numEnsembles (`mp3c_card.py:6-8`; MP3-C C0).
- GiBUU C12 and DIS events stay **unmeasured** for direction.

**Recommended additions.** Report only, login node, 0 node-h. Not blocking.
- **Azimuthal-mean test.** The mean vector (⟨Σp_x⟩, ⟨Σp_y⟩) of the final-minus-initial transverse momentum over:
  - the GiBUU H DIS events (706,827), with an expected SE of about 0.04 MeV;
  - the 337 missing-nucleon events;
  - the GiBUU C12 events, with an SE of about 0.15 MeV from Fermi motion.

  Missing particles, DIS non-conservation and the unwritten remnant are azimuthally symmetric. A tilt θ gives a mean of
  E_ν θ along a fixed azimuth. This would turn "C12 and DIS unchecked" into a measured bound of order 1e-5 rad.
- `pt_balance` is stored only as a hypot (`HARM` `gibuu_file`), so the components need a separate script. The
  `n_energy_balanced > 0` population floor in `HARM:475` should be read alongside the reported 822,359 in the record.

**What the record should say.**
- "Z for GiBUU, as finally defined, was redefined twice after failures. Each redefinition corrected a mis-specified
  population; tolerance unchanged; failing counts kept."
- "Established: ν ∥ +z on 822,359 complete non-DIS H events (max 1.3e-6 GeV). C12 inherits it by jobcard identity."
- "The contract's per-event assertion is not implementable for GiBUU and is recorded as such, not as passed."
- "New caveat beside A9 item 4: about 0.04% of non-DIS GiBUU-H events lack a low-KE final nucleon. The effect on the
  features is below the thresholds; on E_avail it is ≤ a few MeV for a missing proton."

**Accept: yes.**

### D2. NuWro's three-muon events: accept the handling, after a 0 node-h check of which muon it is

**Facts.**
- CC events with 3 muons: 42 (C12 main), 5 (C12 supplement), 5 (H main) and 0 (H supplement), against
  1,999,725 / 99,895 / 249,895 / 24,924 single-muon events (`harm_a/…controls.json`).
- The harmonized muon is the **last |pdg| = 13** in `post` (`HARM:324-326`). That is exactly the frozen converter's
  rule (`nuwro_to_flat_5d.C:53-62`), and control A matches it bitwise.

**The open point.** If NuWro writes the primary lepton first in `post` (I believe it does, but have not verified it),
then in these events the "last muon" is a muon from the μ⁺μ⁻ pair, possibly the μ⁺, not the primary.
- The frozen NuWro product, which A7 and MP3-B use, carries the same choice.
- The handling therefore reproduces a possible defect of the frozen product consistently.

**Recommended.**
- Accept "at least one muon", the frozen converter's muon, and every extra muon excluded (|pdg| 13 is excluded in
  every feature, `HARM:126`).
- **Condition.** It runs before the record lands: login node, 0 node-h. For the 52 events, report:
  - the sign of the selected muon and its position in `post`;
  - whether `post[0]` is a μ⁻;
  - each muon's energy;
  - the events' share of NuWro's in-grid rate.
- If the selected muon is not the primary:
  - the record states that the frozen NuWro product takes a non-primary muon in N events, with a KNOWN_ISSUES row
    (LOW, director-landed);
  - the harmonized product keeps the frozen convention, for consistency with the products A7 used, provided the share
    is ≤ 1e-4 of in-grid rate. The bound by count is ≤ 52 / 1.54M in phase space ≈ 3.4e-5.
- No re-run. This is a record item, not a measurement item.

### D3. GENIE atomic-electron targets: see R13

The handling is right for the **product** (kept, as frozen, and reproduced by N). It is **not** right for training.
Exclude them from G's training, V1 and V3 samples, per the contract's target rule and MP3-A's precedent. Correct the
counts in S2I to the receipt's.

### D4. Job 60101976: no re-run; accept with the record corrected

**Facts.**
- The wrapper hashed `mp2_s2_harmonize.py` = `0c92db3b…` at 11:18:07Z (`logs/mp2s2-s2harmA-60101976.out:1, :7`).
- The file was re-copied about 28 s later.
- 60101977, which started later, recorded `9dbcde93…` for its own `__main__`
  (`harm_b.failed-60101977.s2_harmonize.json:34`).
- 60101976 failed with exit 1 at the two-target assertion ("a target other than C12 and H") after 84 s. It wrote no
  JSON receipt; the PR carries only its log.

**Usability.** Its output is **a failure message only**. Nothing downstream reads anything from it:
- the products, controls and harmonized events in use come from 60102311 and 60102312 under the read-only `code-v3`
  (`3e1ad6e2…`, equal to head);
- the R13 finding it raised was reproduced independently under immutable code by 60102168 (`code-v2`) and 60102311
  (`code-v3`), with `targets_*` counts in the receipts.

So there is nothing to re-run.

**What the record must correct.**
- S2I:102 says the job "ran sha256 `0c92db3b…`". That is **not established**. The hash was taken by the wrapper at
  job start. When the interpreter read the file is not recorded, so it may have run `9dbcde93…`.
- The record should read: "the wrapper hashed `0c92db3b…`; the file changed about 28 s later; which version the
  interpreter read is unrecorded and immaterial, since the job produced only a failure whose finding was reproduced
  under immutable snapshots."
- The claim "the change touched only the GiBUU reader" cannot be checked from the repository, because neither version
  is in it. Drop the claim or show the diff.
- S2I:95 says the first-run outputs are "kept as `harm_a.failed-60101976`". No such receipt is in the PR. Say there is
  none, or give its cluster path.
- The immutable-snapshot practice adopted afterward (`s2/code-v<n>/`, read-only, passed as `CODE`) is the right
  remedy. It is accepted as standing practice for every remaining MP-2 job.

---

## 3. Compute

### Is about 2.6 node-h consistent with the probe?

It is slightly low against the session's own job layout. **Expect about 2.8–3.1 for the requested work, and about
3.0–3.4 with R10's descriptive V1.**

| piece | basis (measured) | CPU node-h |
|---|---|---:|
| models | 50 per G; 4 concurrent streams of 13, 13, 12 and 12 models; 152–161 s per model, so 13 × ~157 s ≈ 34 min per job; plus about 3 min of load (probe: 353 s elapsed − 161 s), giving about 37 min × 4 jobs | ≈ 2.5 |
| gates | V1 and control (2 fits, about 120 s each at 128 threads, per S2I), plus 5 replicas × V2–V4 and the loading of 50 model files: about 6–8 min per G | ≈ 0.4–0.5 |
| R10 descriptive pooled V1 and its control | 2 more fits per G | ≈ 0.15 |
| **total** | | **≈ 3.0–3.2** |

- The session's 2.3 + 0.3 = 2.6 does not match its own "4 jobs of 1 node each, about 45 min per job", which is
  3.0 node-h.
- The difference is the 13th wave per stream (50/4 is 12.5) and the gate time.
- The draft's original 0.7–1.2 (FCD:274) was an arithmetic slip: 200 × 150 s ÷ 4 = 2.08 node-h. S2I:85-88 says so
  correctly.
- The GENIE samples have fewer G training rows (about 0.72M against GiBUU's 1.14M). The cap binds on time per tree,
  so GiBUU and NuWro (about 1.1M) set the per-job wall time and GENIE runs about 10% faster.

### Recommended S2+S3 sub-budget

The ceiling is phase 1's 35. It replaces A8:37's "about 2–3.5".

| tranche | released | CPU node-h |
|---|---|---:|
| spent (8 S2 jobs) | n/a | 0.28 |
| **A: F_primary models and gates** (4 regular jobs, 1 node each, `--time` ≤ 1:30) | on this addendum, after the conditions in §4 | ≤ 3.5 |
| B: F_fallback (11 features: about 0.6× the histogram cost per tree, so about 95 s per model) | only after a reported F_primary failure (BIND:60-61) | ≤ 2.3 |
| C: S3 (28 Asimov unfolds at 0.03–0.06 each, plus the replay, FCD:277; plus any unfolds the S3 reading of R2 adds) | only after the S2 gate report and the committed S3 readings | ≤ 2.4 |
| **S2+S3 sub-budget** | | **≤ 8.5** |

- Phase 1 would then stand at ≤ 7.885 + 8.2 ≈ **16.1 of 35**.
- That is well inside the ceiling and inside Joseph's "half the CPU pool remaining" rule
  (`DECISION-20261019…:52-53`). This is a sub-allocation within an existing grant, not a new grant, so no fresh pool
  measurement is needed.
- **Stop rule.** If any tranche-A job exceeds 1.25× its projected wall time, or tranche A's total exceeds 3.5, the
  session stops and reports before submitting more.

### The iteration cap that binds at 3000 [JOSEPH]

**What the contract says.**
- `n_estimators: 3000` with `early_stopping_rounds: 200` (JSON:107, :110).
- The cost basis assumed about 1,500 iterations (JSON:159).
- "Frozen before fitting: … hyperparameters" (PLAN:216-217).
- Changes need "a committed record before the affected output exists" (A8:35-36).
- "No tuning after any S3 or S4 output" (JSON:146).

So a change now is permitted procedurally, but it would be informed by a fit's validation curve.

**What the probe shows.** In 4 of 4 models, the validation minimum is within the last 30 trees. The models are not
converged by the early-stopping criterion. How flat the curve is at 3000 is **unknown**, because the probe saved no
`evals_result_`.

**Is it a problem?**
- **The reweighting models.** Under-fitting leaves w_G between Tune and G. The gates exist to catch that: V1 sees the
  residual separability, and V2 and V3 see non-closure. The failure direction is conservative ("not established").
  Not a problem of honesty.
- **V1's own classifier** uses the same capped settings. If it also hits the cap, its AUC is a **lower bound** on the
  separability achievable, so a V1 PASS is weaker evidence. That is the non-conservative direction, and it should be
  visible.

**Recommended.**
- Keep 3000. It is frozen, and changing it after seeing a fit's validation curve is the kind of adjustment
  predeclaration exists to prevent.
- **Condition.** Every model and V1 fit records validation logloss at 500, 1000, 2000, 2500, 2800 and 3000 trees,
  from `evals_result_`. This is free, and it changes no output.
- **Condition.** If V1's best iteration is ≥ 2800 (early stopping did not fire), V1's verdict is reported as "PASS
  (or FAIL) at the frozen capacity; early stopping did not fire". A descriptive V1 at `n_estimators = 10000`, with the
  same early stopping, is run beside it in the same job (about 0.05 node-h per G).
- **[JOSEPH]** Whether to raise the cap for all models before production is his methods call. It costs about 2× the
  model time, about +2.5 node-h at 6000 trees. The director should not do it unasked.

---

## 4. DRAFT ADDENDUM

```markdown
# Binding addendum 13: MP-2 S2 readings R0–R13, the disclosures, and the S2+S3 compute (2026-10-22)

**By** the paper-tighten lane, as director, under [`BINDING-PHASE1-ADDENDUM-8.md`](BINDING-PHASE1-ADDENDUM-8.md) and
[`BINDING-PHASE1-ADDENDUM-9.md`](BINDING-PHASE1-ADDENDUM-9.md).

**The request:** `phase1/mp2/S2-IMPLEMENTATION.md`, PR #231, head `dac42a09`. The frozen contract is
`feature_contract_draft.json` `98141c2f…`, re-hashed by the director.

**Timing.** These rulings come before any production model, gate or S3 output exists, as addendum 8 requires. The
four timing-probe models in `fit_probe/` are never read.

**CITABLE FOR:** the readings, the dispositions and the grant below.
**NOT CITABLE FOR:** any result, or any claim (claims are Joseph's).

Items marked **[Joseph]** are flagged to him. He may override any ruling here.

## What the session reported

- All four generators and the Tune v1 C+H table are harmonized under `code-v3` (`3e1ad6e2…`, read-only).
- Every control passed:
  - H0 bitwise;
  - N to ≤ 7.6e-13 relative, with nevt exact;
  - A bitwise;
  - Z: GENIE and NuWro zero; GiBUU as below.
- The S2 charge is 0.282 CPU node-h over 8 jobs. Phase 1 stands at 7.885 of 35.
- The probe measured 152–161 s per model at 4 per node. The best iterations were 2970–3000 of the cap of 3000.

## Rulings on the readings

| # | ruling |
|---|---|
| R0 | **Accepted.** E_avail is MAT's `GetEAvailableTrue`, unthresholded, the analysis coordinate (S1 C3 bitwise). The γ < 10 MeV drop and the species thresholds apply to the species sums, the multiplicities and the leading-particle features. JSON `de_excitation`'s "every feature" is read as excluding the five measurement coordinates |
| R1 | **Accepted.** A per-class 10% draw with `default_rng([lgbm_random_state_k, h, f])`; `[v1_split_seed, 1]` and `[gvg_split_seed, 1]` for V1 and its control. **R1b:** the V1 and control `random_state` are `v1_split_seed` and `gvg_split_seed` |
| R2 | **Accepted.** One c per (G, replica), over the Tune C+H in-grid rows inside G's support. **Carried to S3:** before any S3 output, a committed reading of what J_event's non-domain rows (other nuclei, out of support) carry against each reference, or the computed residual, so that the primary Δ_hyb contains no r_h − r_an term. **[Joseph, informed]** |
| R3 | **Accepted.** V2–V4 on all five replicas; a gate passes only if all five pass |
| R4 | **Accepted.** V1 on replica k = 0 by position |
| R5 | **Accepted.** The bins in `S2-IMPLEMENTATION.md` R5. **R5b (new):** the "no bin beyond 3σ" check of addendum 8 (b) runs over the bins used for χ². Every excluded bin is reported with each side's share, and one-sided bins are reported as support gaps |
| R6 | **Accepted: shape closure.** s = ΣG / ΣT is classifier-independent, because c fixes ΣT to Σ w_truth r_an. The gates assert s equal across the replicas to ≤ 1e-12 relative. The S2 report gives s, g0, and the identity s · k_T · f_CH,an = 1. V2 and V3 are described everywhere as "shape closure at the hybrid's rate". **[Joseph]** For the wording, and for any wish for an absolute-rate test (a contract change) |
| R7 | **Accepted, with sizes as in R10.** The control is two disjoint random subsets of all of G's events, each the size of V1's G sample, drawn with `gvg_split_seed`; V1's protocol; n_estimators fixed to V1's best iteration |
| R8 | **Accepted.** j is the entry index in the declared file order. The JSON's G-fold formula is taken literally |
| R9 | **Accepted.** V4 over the in-support rows, with N their count. The out-of-support count and its w_truth share per J cell are reported |
| R10 | **Ruled differently.** V1's gate sample is replica 0's Tune rows of fold 0 (both halves; ≤ 4M by `v1_split_seed`), weighted w_truth·w_G, against G's events of G-fold 0. The session's pooled V1 is run beside it as **descriptive** |
| R11 | **Accepted.** As addendum 9 amendment 3 |
| R12 | **Accepted.** Before submission, a login-node count (0 node-h) of undecayed charmed hadrons in Tune C+H, GENIE and NuWro against GiBUU. A mismatch above 1e-3 of in-grid rate comes to the director before the GiBUU fit |
| R13 | **Ruled differently.** `tgt == 11` events stay in the harmonized products, H_CH,an and N, as frozen. They are **excluded** from G's training, V1 and V3 samples, under the contract's target rule (MP3-A's precedent). The `S2-IMPLEMENTATION.md` counts are corrected to the receipt's CC counts (CV 1 + 8, MEC 0 + 17) |

## The frozen V2 and V3 thresholds [Joseph]

- Under exact closure, χ²/ndf ≤ 1.5 fails 13–19% of the time at V3's ndf of 5–10, about 45% per replica over the four
  distributions. "No J cell beyond 3σ" fails about 26% over 109 cells.
- The thresholds stay as frozen. The gates report every p-value and every pull.
- Whether to replace them with size-controlled rules is Joseph's decision. It must be committed before the gates job
  runs, or it cannot apply.

## Disclosures

1. **GiBUU Z: accepted as corrected, recorded as post hoc.**
   - Two redefinitions after failures. Each corrected a mis-specified population: a missing final nucleon (an energy
     deficit of 0.94 GeV), and DIS non-conservation (addendum 9 item 4). The 1 MeV tolerance never changed, and the
     failing counts are kept.
   - Established: ν ∥ +z on 822,359 complete non-DIS H events (max 1.3e-6 GeV). C12 inherits it by jobcard identity
     (MP3-C C0). C12 and DIS are unmeasured.
   - The contract's per-event assertion is recorded as not implementable for GiBUU, not as passed.
   - A report-only azimuthal-mean test over the DIS, missing-nucleon and C12 events is invited (0 node-h).
   - New caveat beside addendum 9 item 4: about 0.04% of non-DIS GiBUU-H events lack a low-KE final nucleon.
2. **NuWro three-muon events (52 CC): accepted.**
   - The frozen converter's muon (the last ±13 in `post`), with the extra muons excluded.
   - Before this record lands, a login-node check (0 node-h) reports, for the 52 events, the selected muon's sign and
     position, whether `post[0]` is μ⁻, the muon energies, and their in-grid rate share.
   - If the selected muon is not the primary, a KNOWN_ISSUES row (LOW) records it for the frozen NuWro product. No
     re-run while the share is ≤ 1e-4.
3. **GENIE atomic-electron targets:** as R13.
4. **Job 60101976: no re-run.**
   - It produced only a failure. Its finding (R13) was reproduced under the immutable `code-v2` and `code-v3`, and
     nothing reads its output.
   - `S2-IMPLEMENTATION.md` is corrected:
     - the wrapper hashed `0c92db3b…`; which version the interpreter read is unrecorded;
     - the claim "only the GiBUU reader changed" is shown by a diff or withdrawn;
     - the non-existent `harm_a.failed-60101976` receipt is not cited.
   - Immutable, read-only snapshots are standing practice for every remaining MP-2 job.

## The iteration cap [Joseph]

- n_estimators = 3000 stays as frozen.
- Every fit records validation logloss at 500, 1000, 2000, 2500, 2800 and 3000 trees.
- If V1's best iteration is ≥ 2800, V1 is reported "at the frozen capacity", with a descriptive V1 at 10000 trees
  beside it.
- Raising the cap for all models (about +2.5 node-h) is Joseph's methods call. It is not made here.

## Grant

- **The S2+S3 sub-budget is ≤ 8.5 CPU node-h** (0.28 spent), within the phase-1 ceiling of 35. It replaces addendum 8's
  "about 2–3.5".
- **Tranche A, ≤ 3.5: granted on this record.** The 200 F_primary models and the gates, as 4 jobs of 1 node each on
  QOS regular, `--time` ≤ 1:30. Before submission:
  1. the code implementing R10, R7, R13, R5b and R6's s assertion, and the logloss checkpoints, lands in a new
     read-only snapshot with its sha256 list, committed or hashed in the PR;
  2. the R12 and D2 login-node counts are reported;
  3. the production `--out` is not `fit_probe/`.
- **Tranche B, ≤ 2.3 (F_fallback):** only after a reported F_primary failure for that G.
- **Tranche C, ≤ 2.4 (S3):** only after the S2 gate report and the committed S3 reading carried from R2.
- **Stop rule.** Any job beyond 1.25× its projected wall time, or tranche A beyond 3.5: stop and report.
- The ledger, storage and order rules of the binding (§3) apply. Phase 1 would stand at ≤ 16.1 of 35.

## Records

- **The maintenance window.** The S2 jobs ran on 2026-10-22, inside the announced `maintenance_20261021` window
  (10-21 06:00 to 10-27 23:00 PDT). The session records Perlmutter's actual return time with its source, so that
  addendum 8's "after the maintenance window" is evidenced.
- **The probe.** It ran 4 models where 2 were announced, within the stated ≤ 0.1 node-h (0.098). Recorded, no action.
```

---

## 5. Other findings for the director (not R0–R13)

1. **S2I:81, the R13 counts.** These are entry counts that no receipt carries, and "MEC main 17" matches the receipt's
   *supplement* CC count. Fix: see R13.
2. **S2I:95.** It names a `harm_a.failed-60101976` output that is not in the PR.
3. **S2I:102.** "it ran sha256 `0c92db3b…`" is an inference from the wrapper's hash, not a record. See D4.
4. **S2I:90.** It announced a 2-model probe; 4 ran, at 0.098 node-h.
5. **Two readings implemented in code but missing from S2I:** R1b (the V1 and control random_state) and R5b (the 3σ
   population). Both are accepted above.
6. **The jobs ran 2026-10-22 04:15–04:41 PDT**, inside the window A3:8 and A8:38 announced. No record in `MP/`
   says the window ended early. The return time should be recorded.
7. **S2I:162, the cost table.** "about 2.6" against "4 jobs … about 45 min per job", which is 3.0. See §3.
8. **The S3 consequence of R2** (the non-domain rows' weight in J_event against each reference) is the most
   consequential item not on the session's list. It should be the first item of the S3 readings record.

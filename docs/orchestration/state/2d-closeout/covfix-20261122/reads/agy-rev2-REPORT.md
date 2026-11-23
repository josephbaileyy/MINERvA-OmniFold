<!-- absence-ok: verbatim third-party read report -->
NO-GO

**Document Reviewed:** [inputs/COVFIX-DECLARATION.md](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md) (DRAFT rev 2, 2026-11-22)  
**Baseline Inputs:** [inputs/INVENTORY.md](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/INVENTORY.md) (`7d5a98361`), [inputs/grok-rev1-REPORT.md](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/grok-rev1-REPORT.md), [inputs/agy-rev1-REPORT.md](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/agy-rev1-REPORT.md), [inputs/b1-DECLARATION.md](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/b1-DECLARATION.md), [inputs/b1-REPORT.md](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/b1-REPORT.md), [inputs/REGRADE-AMENDMENT-1.md](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/REGRADE-AMENDMENT-1.md), and cited project records.  
**Review Mandate:** Technical audit of DRAFT rev 2 against external review Fix 1 ($E[ee^T] = C_{\text{fluct}} + b b^T$, testing the case matrix along $V$'s eigenmodes; acceptable outcomes A, B, C; rejection of scaling the covariance until tunes pass).  
**Verdict:** **NO-GO.** While rev 2 successfully resolves all 11 BLOCKING defects and all 20 MAJOR findings from rev 1, binding must be withheld because **three prerequisites in §9 remain open (uncommitted balance receipt, unexecuted KI 85 waiver, and unallocated PG session)**, and rev 2 introduces **two new MAJOR architectural/statistical vulnerabilities** (an execution-environment gap for `/dev/shm` custody under Slurm batch processing and bias dilution by $1/|F_{\text{bias}}|$) alongside minor statistical typos.

---

## 1. Audit of Rev-1 Findings in Rev 2

Every BLOCKING and MAJOR finding from both rev-1 reports was checked against [COVFIX-DECLARATION.md](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md) (rev 2).

### 1.1 BLOCKING Findings from Rev-1 Reports

| ID | Origin | Finding Summary | Status in Rev 2 | Exact Line(s) and Remediation Details |
|---|---|---|---|---|
| **Grok B1** | Grok rev 1 | Validation set contains G18_10b (FSI twin of spent G18); spent tunes enter §5.4 selection bars. | **CLOSED** | [Lines 22–25, 248–252, 315–317, 367–377](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L22-L25): G18_10b removed; validation set fixed to `G21_11b_00_000` and `G18_02b_02_11b` (CCQE/2p2h distinct from spent tunes). G18 and AR23 are strictly descriptive and barred from selecting or admitting candidates. |
| **Grok B2** | Grok rev 1 | Custody leaky: unnamed generator, optional HPSS, physics counts in F1 logs, uncommitted seeds. | **CLOSED** | [Lines 37–39, 275–295](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L37-L39): Mandates fresh session that has read no cov2d records; seeds pre-committed (`8_310_000 + 10_000·u + idx`); logs restricted to boolean pass/fail; AES-256 encryption under director's key; HPSS copy required; purge stops study. |
| **Grok S-ST1** | Grok rev 1 | ST1 skips N5 on "covers" (where 0.44 same-event factor masks under-coverage); N5 contradicts KI 85 deferral. | **CLOSED** | [Lines 34–36, 169, 184–204, 498–500](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L34-L36): Skip rule deleted; N5 always runs in P1 W1; ST1 uses spread only ($v_i, F$) with written block subtractions; N1 is never a construction error; KI 85 deferral explicitly flagged for Joseph's ruling in §9.1. |
| **Grok D2** | Grok rev 1 | Candidate B3 is an ad-hoc eigenvalue tail scaling ($\phi \in \{1,\dots,100\}$) rejected by outside review. | **CLOSED** | [Lines 26, 326–353](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L26): Candidate B3 deleted completely. Candidate $K_B$ rebuilt with separate fluctuation ($V_F$) and bias ($C_b$) components. |
| **Grok D1** | Grok rev 1 | $K_B$ fluctuation rule ($\max(\lambda_i, \hat{s}_i)$ + Ledoit–Wolf) is upward-biased and distorts eigenbasis; PV draw list does not match N4. | **CLOSED** | [Lines 27–29, 32–33, 158–163, 227–234, 328–338](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L27-L29): Per-mode max and Ledoit–Wolf deleted; fluctuation corrected by pooled per-band factor $\hat{f}_R$ past a 3-SE guard; PV, N4, and A1p share the exact same source list (data Poisson + 38 bands + lateral + norm + sim). |
| **agy B1** | agy rev 1 | Candidate B3 is an ad-hoc tail scaling rejected by outside review (identical to Grok D2). | **CLOSED** | [Lines 26, 326–353](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L26): Candidate B3 deleted completely. |
| **agy B2** | agy rev 1 | $K_B$ fluctuation rule defective for $p=205, N=200$ (Jensen bias, noise floor, cell-diagonal distortion; identical to Grok D1). | **CLOSED** | [Lines 27–29, 328–338](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L27-L29): Replaced with unbiased band-spread estimator $\hat{f}_R$ across R1, R2, R3 with 3-SE significance guard, preserving internal relative eigenspectrum. |
| **agy B3** | agy rev 1 | Debiased outer product $\hat{b}\hat{b}^T - S_t/N_t$ is negative definite along at least 199 dimensions, causing fatal C-PSD failure. | **CLOSED** | [Lines 29, 341–344, 347](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L29): $C_b = [ \frac{1}{\|F_{\text{bias}}\|} \sum_t (\hat{b}_t\hat{b}_t^T - S_t/(N_t-1)) ]_+$ applies spectral clipping (positive-part projection $[\cdot]_+$), bounding rank to at most 5 and guaranteeing positive semi-definiteness. |
| **agy B4** | agy rev 1 | Logical inversion in ST1: skipping N5 on "covers" hides true under-coverage under KI 85 under-scattering (identical to Grok S-ST1). | **CLOSED** | [Lines 34–35, 169, 184–204](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L34-L35): N5 runs unconditionally in Wave 1; N1/N2 cannot trigger construction error alone; spread-only block subtractions implemented. |
| **agy B5a** | agy rev 1 | Filesystem `atime` bypassed by `O_NOATIME` reads; unencrypted pscratch ratio files allow covert inspection. | **CLOSED** | [Lines 37–39, 284–295](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L37-L39): Cryptographic custody enforced via AES-256 encryption (`gpg`/`openssl`) with director-held key; plaintext wiped; plaintext hashes committed in `PG-SEAL.sha256` prior to P1. |
| **agy B5b** | agy rev 1 | Validation tune #2 (`G18_10b`) shares CCQE and 2p2h physics models with spent build tune `G18_10a` (identical to Grok B1). | **CLOSED** | [Lines 22–23, 248–252, 268–270](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L22-L23): `G18_10b` removed; validation set restricted to tunes with distinct CCQE or 2p2h classes; exclusion rule bars any tune sharing both classes with a spent tune. |
| **agy B6** | agy rev 1 | Allocation balance 725.6 node-h unsupported by committed records; monolithic P1 allows silent cluster overruns. | **PARTLY CLOSED** | [Lines 45–46, 121–123, 132–140, 503](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L45-L46): P1 split into Waves 1 and 2; ST6 cumulative sacct ceiling added. However, **the balance receipt remains uncommitted** and is explicitly left as an open prerequisite for binding in §3 (line 133) and §9.3 (line 503). |

---

### 1.2 MAJOR Findings from Rev-1 Reports

| ID | Origin | Finding Summary | Status in Rev 2 | Exact Line(s) and Remediation Details |
|---|---|---|---|---|
| **F1** | Grok rev 1 | AR23 already uses SuSAv2 2p2h; distinctness claim for G21 was false. | **CLOSED** | [Lines 48, 258–260](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L48): Overlap explicitly stated: G21_11b shares AR23's `SuSAv2MECPXSec` 2p2h model; CCQE (SuSAv2) differs from both spent tunes. |
| **F2** | Grok rev 1 | G18_02a is not the tune nearest C_model's GENIE 2.12. | **CLOSED** | [Lines 49, 261–263](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L49): Nearest-neighbour claim struck; G18_02* described accurately as adiabatic evolution with RS$\to$BS resonance/coherent update. |
| **F3** | Grok rev 1 | "0.661 in data-dominated cells" misplaces KI 85 (0.661 is all-bin $\sigma$ ratio). | **CLOSED** | [Lines 50, 196–197](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L50): Erroneous attribution removed; KI 85 cited with its exact same-event caveat, reporting N1/N5 as same-event factor. |
| **F4** | Grok rev 1 | `tune_v1` and `_sq` maps are not C_model members in cited records. | **CLOSED** | [Lines 51, 172–173, 340](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L51): `tune_v1` and `_sq` dropped completely; A1 and $F_{\text{bias}}$ restricted strictly to the 3 confirmed PV2D vertices (`genie_mec`, `nuwro`, `gibuu`). |
| **F5** | Grok rev 1 | Inventory states b1 was already run, contradicting scoping. | **CLOSED** | [Lines 54–55, 101–103](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L54-L55): Resolved with exact citation to merged PR #1242 and committed b1 REPORT. |
| **F6** | Grok rev 1 | Claim that $\tau = 0.0098$ "cannot move any reading" contradicts G18 cut block (142 modes moved). | **CLOSED** | [Lines 52, 78–80, 347–353](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L52): Claim deleted; text discloses that small trace coexists with subspace movement; cut diagnostics required for all candidate matrices. |
| **F7** | Grok rev 1 | Allocation balance of 725.6 node-h is uncited in packet. | **PARTLY CLOSED** | [Lines 46, 132–134, 503](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L46): Source cited (director's message from login23 S1 survey); text establishes that **binding requires a committed iris receipt**. Still open pending commitment of the receipt. |
| **Grok B3** | Grok rev 1 | "Spent once" unenforceable: no definition of a read, no lock on intermediate residuals, pre-PV amendment loophole. | **CLOSED** | [Lines 40–41, 209–219](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L40-L41): Defined as single invocation of bound binary writing one summary JSON; per-toy residuals stay in memory; lock file guards second run; §5–§7 frozen against post-binding amendments. |
| **D3** | Grok rev 1 | Nominal N4 cannot see fluctuation excess seen at G18/AR23; candidates lack truth-dependent spread. | **CLOSED** | [Lines 30–31, 173, 177–179, 329–331](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L30-L31): Cell A1p measures perturbed-response spread at 3 alternative truths; pooled spread factor $\hat{f}_R$ pools across N4 and all three A1p ensembles. |
| **D4** | Grok rev 1 | N4 and PV omit lateral surrogate and 1.4% normalisation from explicit draw list. | **CLOSED** | [Lines 32–33, 158–163, 227–234](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L32-L33): Full source list defined identically across N4, A1p, and PV: 38 bands + lateral surrogate + norm (1.4%) + sim redraws. |
| **D5** | Grok rev 1 | Inflation checks missing on bands, modes, and build bars; P-2/P-4 asymmetric. | **CLOSED** | [Lines 42–44, 370–373, 399–402, 409–422](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L42-L44): Full symmetry enforced: P-2 and §5.4 refuse band "over"; P-3 and §5.4 refuse joint "over"; P-4 allows 0 under-flagged modes; INFLATED verdict catches over-coverage. |
| **D6** | Grok rev 1 | A1 does not add alternative truths outside C_model's inputs. | **CLOSED** | [Lines 177–179, 451–453](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L177-L179): Explicitly disclosed that A1 is in-sample; held-out alternative truths reserved strictly for PV; licensed sentences disclose in-sample construction. |
| **D7** | Grok rev 1 | Band label "covers" used by ST1 skip rule is undefined; M vs band edge mismatch. | **CLOSED** | [Lines 104–113](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L104-L113): Unified label table across all metrics: over $<0.8$, covers $[0.8, 1.25]$, under $>1.25$; guarded interval $[X-h, X+h]$ must lie wholly within interval; no separate band convention. |
| **S2** | Grok rev 1 | False-FAIL excursion calculation for $K_C$ wrong; no floor on $k$; empty bands undefined. | **CLOSED** | [Lines 43–44, 98–99, 360–363, 437–438](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L43-L44): Floor $k \ge 10$ enforced; bands with $<10$ modes dropped and named; excursion re-derived for $k=10$ (though with low/high label swap; see §2.3). |
| **S3** | Grok rev 1 | Fixed Gaussian 0.6827 null invalid for clipped/un-centred draws; recolouring check blind to draw distortions. | **CLOSED** | [Lines 43, 381–386, 394–400, 439–441](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L43): Joint null replaced with COV2D draw-matched null run on frozen draw lists; false-FAIL rates computed blind prior to PV; union bound adopted. |
| **P2** | Grok rev 1 | Phase can pass quoted price without hitting cap; sum of phases un-gated; N5 not withheld until N1/N2 read. | **CLOSED** | [Lines 45–46, 121–123, 137–140, 170](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L45-L46): ST6 cumulative sacct ceiling pins approved total across all phases; P1 split into Wave 1 and Wave 2; N3 priced exactly at 9.5 node-h. |
| **agy M1** | agy rev 1 | Guard $h(M)$ collapses acceptance window for small $k$ ($1.5\sigma$ at $k=2$, $0.48\sigma$ at $k=1$). | **CLOSED** | [Lines 360–363, 437–438](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L360-L363): Subspace dimension floored at $k \ge 10$, guaranteeing $h(M) \le 0.051$ and maintaining excursion $>5.7\sigma$. |
| **agy M2** | agy rev 1 | Empty bands ($|R|=0$) for $k \le 73$ cause NaN/vacuous pass; P-4 allows 100% mode failure at small $k$. | **CLOSED** | [Lines 98–99, 362–363, 373, 411](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L98-L99): Bands with $<10$ modes dropped; P-4 tightened to allow 0 under-flagged modes. |
| **agy M3** | agy rev 1 | N4 unconditionally includes simulation statistics while PV includes them conditionally on R1 test. | **CLOSED** | [Lines 32–33, 158–163, 227–234](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L32-L33): Contradiction removed; sim redraws included unconditionally across N4, A1p, and PV. |
| **agy M4** | agy rev 1 | §5.4 build-set admission bars omit over-coverage checks, admitting inflated matrices into PV. | **CLOSED** | [Lines 42, 370–372](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L42): §5.4 requires that no band read "over" and that the draw-matched joint rule flag neither "under" nor "over". |
| **agy M5** | agy rev 1 | Generating 3 validation tunes in PG exhausts Perlmutter's GENIE v3 product, breaking ST4. | **CLOSED** | [Lines 217–219, 248–251](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L217-L219): Validation truths fixed to 2 tunes permanently (`G21_11b_00_000` and `G18_02b_02_11b`); catalog exhaustion limitation explicitly disclosed. |

---

## 2. Technical Audit of Rev 2: Fidelity, Logic, Statistics, Prices, and Custody

### 2.1 Fidelity Against Inputs and Records
1. **Model Overlaps (§4.1, [lines 258–263](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L258-L263)):** Rev 2 faithfully reflects [FD-F1-REPORT.md](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/FD-F1-REPORT.md) §1.3. AR23 shares SuSAv2 MEC with G21_11b, while CCQE differs. G18_02b is correctly characterized from the official GENIE tune page.
2. **b1 Project Record (§2, [lines 101–103](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L101-L103)):** Rev 2 accurately incorporates the execution and merge of b1 ([inputs/b1-REPORT.md](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/b1-REPORT.md), PR #1242), adopting its student-$t$ guard.
3. **C-PUB Tolerance (§8, [lines 492–494](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L492-L494)):** Cites [REGRADE-AMENDMENT-1.md](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/REGRADE-AMENDMENT-1.md) and T2-BINDING-1 Addendum 1, using $\max(10^{-9}, 10 \kappa_2 \varepsilon)$. Matches the packet.

### 2.2 Mathematical and Statistical Verification

#### 1. Every Number in Section 6.4 (§6.4, [lines 424–445](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L424-L445))
- **Standard Error of $M$:** For $\text{ndf} = 204$ and $N = 300$:
  $$\text{SE}(M) = \sqrt{\frac{2}{N \cdot \text{ndf}}} = \sqrt{\frac{2}{300 \times 204}} = \sqrt{\frac{2}{61200}} \approx 0.005717 \approx 0.006 \quad \text{([Line 427](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L427): Exact).}$$
- **P-3 Discrete Size:** False "under" at count $\le k_J$ has binomial tail prob $\le 0.025$; false "over" at $\ge k_J^+$ has prob $\le 0.025$. Total P-3 size $\le 0.050$ ([Line 433](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L433): Exact).
- **P-4 Linearity and Markov Bound:** Per-mode critical threshold is $\alpha_i = 0.025/\text{ndf}$. By linearity of expectation, $E[\sum_{i=1}^{\text{ndf}} I_i] \le \text{ndf} \times (0.025/\text{ndf}) = 0.025$. Because P-4 forbids any flagged mode, $P(\text{False FAIL from P-4}) = P(\sum I_i \ge 1) \le E[\sum I_i] \le 0.025$ ([Line 435](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L435): Rigorous and exact).
- **Per-Truth and Two-Truth Union Bounds:**
  - $P(\text{not PASS per truth}) \le P(\text{P-3 under}) + P(\text{P-3 over}) + P(\text{P-4 under}) \le 0.025 + 0.025 + 0.025 = 0.075$ ([Line 439](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L439)).
  - $P(\text{FAILS per truth}) \le P(\text{P-3 under}) + P(\text{P-4 under}) \le 0.025 + 0.025 = 0.050$ (P-3 over routes to INFLATED, not FAILS; [Line 439](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L439)).
  - Over two truths: $P(\text{not VALIDATED}) \le 2 \times 0.075 = \mathbf{0.15}$; $P(\text{FAILS}) \le 2 \times 0.050 = \mathbf{0.10}$ ([Line 440](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L440): Exact).

#### 2. The $k \ge 10$ Floor Arithmetic and Excursion Defect ([Lines 362, 437–438](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L362))
- For $k = 10, N = 300$: $\text{SE}(M) = \sqrt{2 / (300 \times 10)} = \sqrt{2/3000} \approx 0.025820$.
- $t_{0.975, 299} \approx 1.96793 \implies h(M) = 1.96793 \times 0.025820 \approx \mathbf{0.05081} \approx 0.051$.
- To remain inside "covers" $[0.8, 1.25]$, the guarded interval $[M - h, M + h]$ must satisfy $M + h \le 1.25$ and $M - h \ge 0.8$.
  - **High Side Boundary:** $M \le 1.25 - 0.05081 = 1.19919$. Deviation from nominal null ($M=1.0$):
    $$\Delta_{\text{high}} = 1.19919 - 1.0 = 0.19919 \implies \frac{0.19919}{0.025820} = \mathbf{7.71\sigma}.$$
  - **Low Side Boundary:** $M \ge 0.8 + 0.05081 = 0.85081$. Deviation from nominal null ($M=1.0$):
    $$\Delta_{\text{low}} = 1.0 - 0.85081 = 0.14919 \implies \frac{0.14919}{0.025820} = \mathbf{5.78\sigma}.$$
- **Defect in [Line 438](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L438):** The text states: *"about 5.7σ on the high side and 7.7σ on the low side."* **This is an exact typographical transposition.** $5.7\sigma$ is on the *low side* and $7.7\sigma$ is on the *high side*.

#### 3. Pooled Band Factor $\hat{f}_R$ and 3-SE Guard (§5.2, [lines 329–333](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L329-L333))
- $\hat{f}_R = \frac{1}{4} [ F_R(\text{N4}) + F_R(\text{A1p}_{\text{genie}}) + F_R(\text{A1p}_{\text{nuwro}}) + F_R(\text{A1p}_{\text{gibuu}}) ]$.
- Applied only if $\hat{f}_R - 1 > 3 \cdot \text{SE}(\hat{f}_R)$.
- **Defect (Ambiguity):** Section 2 ([lines 101–103](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L101-L103)) specifies SE propagation for a difference of two independent ensembles ($\text{SE}^2 = \text{SE}_1^2 + \text{SE}_2^2$), but **fails to define the SE formula for an unweighted average of 4 ensembles**. It must be explicitly defined as $\text{SE}^2(\hat{f}_R) = \frac{1}{16} \sum_{k=1}^4 \text{SE}^2(F_R(E_k))$.

#### 4. Positive Semi-Definiteness (PSD) Projection (§5.2, [lines 342–344](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L342-L344))
- $C_b = [ \frac{1}{|F_{\text{bias}}|} \sum_t (\hat{b}_t \hat{b}_t^T - S_t/(N_t-1)) ]_+$.
- Let $A = \frac{1}{|F|} \sum_{t=1}^5 \hat{b}_t \hat{b}_t^T$ (rank $\le 5$) and $B = \frac{1}{|F|} \sum_{t=1}^5 \frac{S_t}{N_t-1}$ (positive semi-definite, rank $\le 205$).
- By Weyl's inequality, $\lambda_k(A - B) \le \lambda_k(A) - \lambda_{\min}(B) \le \lambda_k(A)$.
- Since $\text{rank}(A) \le 5$, $\lambda_k(A) = 0$ for all $k \ge 6$. Because $B$ is PSD ($\lambda_{\min}(B) \ge 0$), $\lambda_k(A - B) \le 0$ for all $k \ge 6$.
- Consequently, $A - B$ has at most 5 positive eigenvalues. Spectral truncation $[ \cdot ]_+$ clamps all non-positive eigenvalues to zero, guaranteeing that $C_b$ is positive semi-definite with $\text{rank}(C_b) \le 5$. The claim in line 344 is mathematically proven.

#### 5. Exactness of the Split Identity (§2, [lines 96–97](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L96-L97); §6.1, [line 403](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L403))
- With sample divisor $1/N$:
  $$v_i = \frac{1}{N} \sum_{s=1}^N (z_{s,i} - m_i)^2 = \frac{1}{N} \sum_{s=1}^N z_{s,i}^2 - m_i^2 = q_i - m_i^2 \implies q_i = m_i^2 + v_i \quad \text{exactly.}$$
- Averaging over modes: $M = \frac{1}{\text{ndf}} \sum q_i = \frac{1}{\text{ndf}} \sum m_i^2 + \frac{1}{\text{ndf}} \sum v_i = \frac{1}{\text{ndf}} \sum m_i^2 + F$. Exact.

---

### 2.3 Verification of Node-Hour Pricing and Accounting

Every product $n \times 0.19$, subtotal, wave total, and grand total was verified.

| Line Item | Formula | Full (node-h) | Lean (node-h) | Exact Arithmetic | Status |
|---|---|---|---|---|---|
| **N1** | $200 / 150 \times 0.19$ | 38.0 | 28.5 | $200 \times 0.19 = 38.0$; $150 \times 0.19 = 28.5$ | Exact |
| **N2** | $200 / 150 \times 0.19$ | 38.0 | 28.5 | $200 \times 0.19 = 38.0$; $150 \times 0.19 = 28.5$ | Exact |
| **N5** | $(200+200) / (150+150) \times 0.19$ | 76.0 | 57.0 | $400 \times 0.19 = 76.0$; $300 \times 0.19 = 57.0$ | Exact |
| **N3** | $50 \times 0.19$ | 9.5 | 9.5 | $50 \times 0.19 = 9.5$ | Exact |
| **N4** | $200 / 150 \times 0.19$ | 38.0 | 28.5 | $200 \times 0.19 = 38.0$; $150 \times 0.19 = 28.5$ | Exact |
| **A1f** | $3 \times 60 / 0 \times 0.19$ | 34.2 | 0.0 | $180 \times 0.19 = 34.2$; $0 \times 0.19 = 0.0$ | Exact |
| **A1p** | $3 \times 100 / 3 \times 100 \times 0.19$ | 57.0 | 57.0 | $300 \times 0.19 = 57.0$ | Exact |
| **P1 Wave 1** | $\text{N1} + \text{N2} + \text{N5} + \text{N3}$ | **161.5** | **123.5** | $38+38+76+9.5 = 161.5$; $28.5+28.5+57+9.5 = 123.5$ | Exact |
| **P1 Wave 2** | $\text{N4} + \text{A1f} + \text{A1p}$ | **129.2** | **85.5** | $38+34.2+57 = 129.2$; $28.5+0+57 = 85.5$ | Exact |
| **P1 Total** | $\text{Wave 1} + \text{Wave 2}$ | **290.7** | **209.0** | $161.5+129.2 = 290.7$; $123.5+85.5 = 209.0$ | Exact |
| **PV** | $2 \times 300 \times 0.19$ | **114.0** | **114.0** | $600 \times 0.19 = 114.0$ | Exact |
| **PG Range** | 2 tunes generation | **1.3–2.0** | **1.3–2.0** | Based on F1 actuals ($2 \times 0.6638 = 1.3275$) | Exact |
| **Full Total** | $\text{PG} + \text{P1} + \text{PV}$ | **406.0–406.7** | — | $1.3/2.0 + 290.7 + 114.0 = 406.0 / 406.7$ | Exact |
| **Lean Total** | $\text{PG} + \text{P1} + \text{PV}$ | — | **324.3–325.0** | $1.3/2.0 + 209.0 + 114.0 = 324.3 / 325.0$ | Exact |

- **Allocation Half-Balance Compliance ([Lines 132–136](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L132-L136)):** Stated balance is 725.6 node-h; half-balance threshold is 362.8 node-h.
  - Phase caps: PG cap (3.0), P1 cap (330 full / 240 lean), and PV cap (135) are all strictly below 362.8 node-h.
  - Lean grand total ($325.0 < 362.8$) satisfies the half-balance rule for the entire campaign. Full grand total ($406.7 > 362.8$) requires Joseph's explicit authorization.

---

### 2.4 Enforceability of Custody and Spent-Once Protocols

While rev 2 eliminates file access-time (`atime`) dependence and establishes cryptographic sealing, two operational enforceability vulnerabilities exist:

1. **The Login Node `/dev/shm` vs Slurm Compute Node Access Gap (§4.2, [line 298](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L298)):**
   - Line 298 mandates: *"Decryption goes to /dev/shm only, and every decrypted sha256 must equal the seal."*
   - `/dev/shm` is a local RAM-disk private to the specific host. A file decrypted to `/dev/shm` on a NERSC login node is **physically inaccessible to batch worker jobs executing across Perlmutter compute nodes**.
   - Phase PV requires 114 node-h (600 unfolding toys, each running neural network unfolding via Slurm batch arrays). If the 600 worker jobs execute `s5e_deform.ratio_weight` ([line 228](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L228)), they cannot read the ratio from login-node `/dev/shm`.
   - If worker jobs decrypt the file locally on each compute node, the director's secret passphrase must be distributed across Slurm environment variables or batch scripts, violating key custody.
   - *Fix:* Specify that the bound PV connect precomputes the deformed pseudo-data and weights inside `/dev/shm` on the connect node and stages them securely, or define a secure shared staging mechanism on `/dev/shm` within a single allocated multi-GPU node.

2. **Visibility of Intermediate Unfolded Toy Outputs Prior to Single-Invocation Readout (§3.3, [lines 209–214](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L209-L214)):**
   - ST4 restricts the *readout binary* to a single invocation writing summary statistics only.
   - However, during PV, 600 unfolding jobs execute and write intermediate unfolded cross-section arrays ($\hat{\sigma}_s$) to pscratch.
   - Under shared POSIX permissions (`josephrb:wheel`), any session or script could inspect these intermediate files, compute unofficial residuals, and pre-evaluate coverage before triggering the official single-invocation readout binary.
   - *Fix:* Mandate that PV batch scripts write intermediate toy cross sections directly into a restricted, temporary directory accessible only to the bound readout runner, and wipe them upon completion.

---

## 3. Acceptability of the Pooled Per-Band Fluctuation Factor

**Question:** *Is the pooled per-band fluctuation factor in §5.2 acceptable under the review's "no scaling until the two tunes pass", given that it is measured on fluctuation ensembles at nominal and at three non-spent truths and never reads G18 or AR23?*

### Direct Answer: **YES, it is acceptable.**

### Technical Justification and Reasons:
1. **Not Tuned to Achieve a Pass:**
   The external review specifically forbade *"scaling the covariance until the two tunes pass"*. In rev 1, candidate B3 swept an arbitrary eigenvalue multiplier $\phi \in \{1,\dots,100\}$ on tail modes, selecting the smallest $\phi$ that forced G18 and AR23 to meet §5.4's admission bars. In contrast, $\hat{f}_R$ is an empirical forward estimator derived directly from the matrix of cases required by Fix 1 (nominal N4 and alternative perturbed-response A1p). It evaluates no test statistics on G18 or AR23.
2. **Complete Separation of Fluctuation from Bias:**
   Each ensemble component $F_R(E) = \frac{1}{|R|} \sum_{i \in R} v_i$ measures the sample variance $v_i = \frac{1}{N} \sum_s (z_{s,i} - m_i)^2$. Because the ensemble mean shift $m_i$ is subtracted, $\hat{f}_R$ measures pure fluctuation spread around the shifted truth, entirely decoupled from truth-model bias $b b^T$.
3. **Rigorous Significance Guard (3-SE):**
   The factor is not a free parameter. It is applied only if empirical spread exceeds the baseline covariance by more than 3 standard errors ($\hat{f}_R - 1 > 3 \cdot \text{SE}(\hat{f}_R)$), preventing upward fitting to sampling noise. Furthermore, eigenvalues are never lowered, preserving conservative detector modeling.
4. **Adoption of External Reviewer Guidance:**
   This exact formulation was recommended by reviewer 2 ([agy-rev1-REPORT.md:269–272](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/agy-rev1-REPORT.md#L269-L272)) as the mathematically valid replacement for cell-space Ledoit–Wolf shrinkage.

---

## 4. Soundness of Replacing $C_{\text{model}}$ with $C_b$

**Question:** *Is removing $C_{\text{model}}$ from the fluctuation part and replacing it with $C_b$ (built from the three $C_{\text{model}}$ vertices plus G18 and AR23) sound, or does it double-count or drop anything?*

### 4.1 Structural Soundness and Absence of Double-Counting
- **Clean Decoupling:** In the baseline covariance, $C_{\text{model}}$ was an ad-hoc covariance block representing generator model differences, improperly added into the Gaussian fluctuation matrix without a generative toy law. Subtracting $C_{\text{model}}$ ($F_A = K_A - C_{\text{model}}$) isolates genuine detector/statistical fluctuations ($C_{\text{fluct}}$).
- **No Double-Counting:** 
  - $V_F$ scales $F_A$ by $\hat{f}_R$, which is derived strictly from spread $v_i$ (bias subtracted).
  - $C_b$ is built strictly from the outer products of ensemble mean biases $\hat{b}_t$, debiased by the sampling covariance of the mean $S_t/(N_t-1)$.
  - Because $C_{\text{model}}$ is completely removed from $F_A$, the three PV2D vertices are not counted in the baseline and then counted again in $C_b$. Fluctuation and bias occupy orthogonal statistical representations.

### 4.2 What It Drops: Two Critical Vulnerabilities
While structurally sound, the specific mathematical definition of $C_b$ introduces two significant omissions:

1. **Bias Dilution by $1/|F_{\text{bias}}| = 1/5$ (MAJOR Vulnerability):**
   - The formula averages the debiased outer products over 5 truths:
     $$C_b = \left[ \frac{1}{5} \sum_{t=1}^5 \left( \hat{b}_t \hat{b}_t^T - \frac{S_t}{N_t - 1} \right) \right]_+$$
   - When candidate $K_B$ is evaluated against a specific held-out truth $u$ (such as `G21_11b`), the physical error distribution has a fixed, non-random bias dyad $b_u b_u^T$ of unit weight.
   - If $b_u$ is aligned with one of the vertices (e.g. SuSAv2 MEC in AR23), $C_b$ provides only **$\frac{1}{5} = 20\%$ of the required variance** along that model-specific direction.
   - Averaging outer products treats the true model as if it were drawn from an empirical mixture prior across the 5 models, severely diluting model-specific excursions. At any single fixed truth, $K_B$ will be prone to under-covering along model-specific directions.
2. **Omission of Nominal Estimator Closure Bias (MINOR Vulnerability):**
   - $F_{\text{bias}}$ contains only the 5 alternative tunes; nominal truth ($t = \text{nominal}$) is excluded.
   - Nominal closure bias (which IBUKT A2 measured up to 1.708% noise-free) is excluded from ST1 and excluded from $V_F$ (spread only).
   - Consequently, neither $V_F$ nor $C_b$ allocates variance to nominal unfolding closure bias.

---

## 5. Categorized Findings and Required Remediations

### BLOCKING Findings (Must be resolved before binding)

1. **[BLOCKING-1] Uncommitted Allocation Balance Receipt (§3, [line 133](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L133); §9.3, [line 503](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L503))**
   - *Defect:* The campaign relies on an allocation balance of 725.6 node-h. Lines 133 and 503 explicitly identify a committed iris balance receipt as a mandatory prerequisite for binding. Binding cannot proceed on an uncommitted receipt.
   - *Concrete Fix:* Execute an iris balance survey on a Perlmutter connect and commit `BALANCE-RECEIPT.txt` before binding.

2. **[BLOCKING-2] Joseph's Decision Required to Supersede KI 85 Deferral (§3.3, [line 202](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L202); §9.1, [lines 498–500](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L498-L500))**
   - *Defect:* Known Issue 85 established a standing directive deferring the held-out-MC re-test until after the publication package. Cell N5 constitutes that re-test. Section 9.1 explicitly notes that binding N5 requires Joseph's formal decision superseding the deferral.
   - *Concrete Fix:* Obtain and commit Joseph's written authorization superseding the KI 85 deferral for Phase P1, or formally drop N5 and outcome A as specified in line 500.

3. **[BLOCKING-3] Unnamed Generating Session and Uncommitted PG Key (§4.2, [line 277](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L277); §9.3, [lines 504–505](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L504-L505))**
   - *Defect:* Custody mandates that PG be executed by a fresh session that has read no project records. Section 9.3 leaves the generating session unnamed and the director's passphrase uncommitted.
   - *Concrete Fix:* The director must formally name the PG session ID and generate the encryption passphrase prior to binding.

---

### MAJOR Findings (Design and procedural flaws requiring revision)

1. **[MAJOR-1] Execution Environment Disconnect for `/dev/shm` Custody in PV (§4.2, [line 298](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L298))**
   - *Defect:* Line 298 requires decryption to `/dev/shm` only. Slurm batch jobs running across Perlmutter compute nodes cannot read login-node `/dev/shm`.
   - *Concrete Fix:* Update §4.2 to specify the execution architecture: either the bound PV connect generates the deformed pseudo-data and weights inside `/dev/shm` on the login node and stages them securely, or specify a dedicated Slurm job script structure that manages RAM-disk decryption securely.

2. **[MAJOR-2] Bias Under-Coverage via $1/|F_{\text{bias}}|$ Dilution in $C_b$ (§5.2, [line 342](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L342))**
   - *Defect:* Averaging 5 outer products divides the variance along any single model's bias direction by 5, diluting coverage against model-specific departures.
   - *Concrete Fix:* Disclose this dilution in §5.2 and §7 (outcome B), or modify $C_b$ to incorporate an envelope/subspace projection that scales with the maximum projection across the 5 models.

3. **[MAJOR-3] Pre-Readout Visibility of Intermediate Unfolded Toy Arrays (§3.3, [lines 209–214](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L209-L214))**
   - *Defect:* While the readout binary is restricted to one invocation, intermediate unfolded cross sections written to pscratch by the 600 worker jobs can be evaluated out-of-band before invoking the readout.
   - *Concrete Fix:* Mandate that PV batch scripts write intermediate toy outputs into a restricted directory accessible only to the bound readout runner, with automated deletion upon completion.

---

### MINOR Findings (Typographical and notation cleanups)

1. **[MINOR-1] Inverted High/Low Excursion Labels in §6.4 (§6.4, [line 438](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L438))**
   - *Defect:* Text states "about 5.7σ on the high side and 7.7σ on the low side." At $k=10$ with $h=0.051$, $1.25 - h$ is $7.71\sigma$ from 1.0 (high side), and $0.8 + h$ is $5.78\sigma$ from 1.0 (low side).
   - *Concrete Fix:* Change to: *"about 7.7σ on the high side and 5.8σ on the low side."*

2. **[MINOR-2] Missing Analytical Definition for $\text{SE}(\hat{f}_R)$ (§5.2, [line 332](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L332))**
   - *Defect:* The standard error formula for the pooled average of 4 ensembles is omitted.
   - *Concrete Fix:* Add explicit definition: $\text{SE}^2(\hat{f}_R) = \frac{1}{16} \sum_{k=1}^4 \text{SE}^2(F_R(E_k))$.

3. **[MINOR-3] Omission of Nominal Closure Bias Disclosure (§5.2, [line 340](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix2/inputs/COVFIX-DECLARATION.md#L340))**
   - *Defect:* $F_{\text{bias}}$ omits nominal truth, leaving nominal closure bias unallocated in both $V_F$ and $C_b$.
   - *Concrete Fix:* Add a disclosure note stating that nominal closure bias (IBUKT A2: $\le 1.708\%$) is neglected relative to detector systematics and is not modeled in $C_b$.

---

## 6. Summary Recommendation

Draft rev 2 represents a comprehensive, highly rigorous remediation of the structural flaws in rev 1. It successfully eliminates eigenvalue tail scaling (B3), repairs the mathematical instability of the fluctuation estimator, enforces positive semi-definiteness via spectral truncation, and closes all major fidelity gaps.

However, because **open policy prerequisites remain unresolved in §9** (the iris balance receipt, the KI 85 waiver, and session assignment), and because **the cluster execution architecture for `/dev/shm` custody under Slurm batch processing must be clarified**, the formal verdict remains **NO-GO**. 

Upon commitment of `BALANCE-RECEIPT.txt`, execution of Joseph's KI 85 ruling, and resolution of findings MAJOR-1 and MINOR-1, COVFIX rev 2 will be fully eligible for binding.

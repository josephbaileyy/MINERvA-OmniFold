# COVFIX declaration, DRAFT rev 12: the 2D covariance fix (2026-11-24)
<!-- absence-ok: a draft declaration of studies not yet run; every existing study is routed to INVENTORY.md -->

<!-- absence-ok: status line of an unrun draft -->
**Status: rev 11.4 is bound** (COVFIX-BINDING-1, at M_C1 `90b29087`; sha256 `464ce635…`). **This rev 12 is a DRAFT
amendment and binds nothing** until Joseph approves its text and the director writes its binding. Until then rev 11.4
governs every phase. Rev 12 is drafted before any sealed truth exists and before any PV toy is drawn.

**By** the `cov2d` session, at the director's request of 2026-11-22 (`reads/director-rev0-items.md` quotes its items on
rev 0). Joseph authorized starting the design phase, via the director, after an outside review of the note asked for
its "Fix 1". The inventory is `INVENTORY.md` in this directory, read at origin/main `7d5a98361`.

**CITABLE FOR:** nothing yet. Once bound and run: the readings in §6 and only the sentences §7 licenses for them.

**NOT CITABLE FOR:**
- any note or paper wording;
- adopting any covariance (adoption is Joseph's);
- a cause of the under-coverage;
- coverage at the data's own point, or for generators outside the validation family (§4.3);
- a p-value.

**Revision history.**
- **Rev 1** answered the director's seven items on rev 0.
- **Rev 2** answered Grok's and agy's NO-GO reads of rev 1 (`reads/*-rev1-REPORT.md`).
- **Rev 3** answers their NO-GO reads of rev 2 (`reads/*-rev2-REPORT.md`):
  - **Grok N-1, the block structure.** K0 is now named by its blocks: Q_rep, the adopted G2R covariance, which equals
    s5_total + C_PL exactly, plus C_model_abs beside it. The carry is an explicit formula, and every candidate is the sum
    of a fluctuation block and a bias block. The carried-versus-remade difference is measured at G18 and AR23 in P0.
    §2, §3.1, §5.1.
  - **Grok N-2, the ST1 amendment.** It is a single named exception, confined to the generator of the firing block and
    written before P2. §3.3.
  - **Grok N-3, agy MINOR-2.** SE(f̂_R) is defined, with the N/(N−1) correction. §5.2.
  - **Grok N-4.** "C_b can only add" is gone, replaced by a residual stop. §5.2.
  - **Grok N-5.** Any band with at least 10 modes can fire ST1. §3.3.
  - **Grok N-6.** The draw-matched null and its 0.20 check run inside the PV binary, after decryption and with the
    candidates frozen. §5.5, §6.1.
  - **Grok N-7.** The false b1 attribution of the guard is removed. §2.
  - **Grok N-8.** The lean campaign's cell 4 covers genie_mec and nuwro only. §3.
  - **Grok N-9, agy MAJOR-1 and MAJOR-3.** The passphrase is piped, never written to a file. Decryption and the toy
    writer run on the login node in /dev/shm, which is wiped. Graded truths are encrypted, and the job ends with a
    plaintext scan. §3.4, §4.2.
  - **agy MAJOR-2, agy MINOR-3.** C_b is the sum, not the mean, of the family's debiased outer products, so it is not
    diluted, and the family includes nominal closure bias. §5.2.
  - **A design consequence both reads point to.** A bias block necessarily over-covers truths whose bias is smaller than
    the family's. The bars are now two-sided on the fluctuation part and one-sided ("not under") on the total. That is
    Fix 1's decomposition: the bias block is a stated model-class bound, and the fluctuation must match. §5.4, §6.2.
  - **Minor:** N-10's σ sides; M-11, which asks that KI 85's no-change rule be superseded explicitly; M-12 (G18_02);
    M-13 (the PG floor and a per-job walltime ceiling); M-14 (the k floor in the measurability case); M-15 (cap sums);
    M-16 (a descriptive held-out bias comparison); M-17 (the 20 % mark, now cited to a committed quote).
  - agy's three BLOCKINGs are binding prerequisites, already listed in §9, not defects of the text.
- **Rev 4** answers their NO-GO reads of rev 3 (`reads/*-rev3-REPORT.md`):
  - **The residual stop** (Grok N3-1, agy Defect 1):
    - the cut is referenced to each candidate's own λ₁(V_F);
    - the residual rule checks only well-determined modes (λ ≥ 1e-6·λ₁);
    - an ndf change is printed, not a stop;
    - the rule does not apply to K_C;
    - P0 calibrates it on the committed C_T vs C_T + C_run pair.
    §2, §3.1, §5.2.
  - **C_b's frame** (N3-2b). Each bias is mapped to x_R by D_t⁻¹ before the sum. §5.2.
  - **Outcome B** (N3-3):
    - G18 and AR23 are out of C_b, which now sums nominal and the three C_model vertices;
    - rows A, B and C say "matches (two-sided)" for the fluctuation block and "does not under-cover (one-sided)" for the
      total;
    - B carries the held-out bias statistics.
    §5.2, §7.
  - **KI 85** (N3-4b). Without both sentences superseded, no block is regenerated and outcome A is not licensed. §3.3.
  - **The null** (N3-2). It is written out: carried G2R band shifts plus a Gaussian remainder, with controls and a
    labelled Gaussian fallback. §6.1.
  - **The ST1 exception** (N3-4, agy Defects 2 and 4):
    - it changes code only;
    - it is bound before the f̂_R and C_b ensembles are drawn, and those are redrawn under it;
    - the regeneration is priced;
    - it can name more than one block.
    §3.3.
  - **Custody** (N3-5):
    - the writer and the readout run on exclusive compute nodes, through `srun` stdin pipes;
    - the scan is by content, and covers /dev/shm, /tmp and the campaign directory;
    - the readout gets its own pipe;
    - the lock file's limit is stated.
    §3.4.
  - **x̂_t** (N3-6). It is defined as the unfold of round(λ⁺). P0 carries with both vectors. §2, §3.1.
  - **§6.4's false-PASS boundary** (N3-7). Corrected. §6.4.
  - **The band factor's basis** (N3-8). Stated. §5.2.
  - **Minor:**
    - K_C's floor is k ≥ 25, for 5σ at N = 100 (N3-9);
    - the G18_02 wording (N3-10);
    - `--time` at 1.5× the price, with chunked submission (N3-11);
    - the price sentences and the no-N5 totals (N3-12);
    - the C_PL τ_F clause (N3-13);
    - a fixed bootstrap basis, and the glosses as v3.2.0 descriptions (N3-14);
    - agy Defects 3 and 5.
- **Rev 4.1** answers agy's read of rev 4 (`reads/agy-rev4-REPORT.md`). Grok could not read rev 4: its usage balance was
  exhausted (HTTP 402, `reads/grok-rev4-ERROR.txt`). agy closed every rev 3 BLOCKING and MAJOR finding and raised five:
  - §8 now names the exclusive-node writer (Defect 1);
  - §6.4 separates the far and near false-PASS boundaries and states the near one's 0.07 (Defect 2);
  - the per-mode binomial parameter is renamed p_i (Defect 3);
  - row "A, partial" carries the KI 85 condition (Defect 4);
  - P-3's count K_J is written (Defect 5).
- **Rev 5** answers codex-school2's read of rev 4.1 (`reads/codex2-rev4.1-REPORT.md`; NO-GO). codex-school2 is the
  second reader named in `DECISION-20261123-joseph-covfix-ki85-size-reader.md`, which is now cited in §3, §3.3, §7 and
  §9.
  - **Outcome licences** (its BLOCKINGs on A and B, and MAJORs on C and none):
    - A needs code-level evidence;
    - "A, partial" reports the actual verdict;
    - B and C license only the observed affirmative readings at the two named tunes under the declared toy law, not a
      model class;
    - a baseline challenge (K0 FAILS somewhere) is required for B and C;
    - "inconclusive" becomes "no challenge". §7.
  - **Affirmative bars.**
    - The total is barred by its upper guarded bound, M + h ≤ 1.25.
    - The fluctuation is barred by F̃ "covers", with every band affirmative.
    - P2 uses PV's bars exactly.
    - False PASS is about 0.025 at the boundary, at either truth, by construction, and calibrated. §6.3–§6.5.
  - **The null** (BLOCKING): a written calibration law with fixed bias alternatives and centred drawn-only
    fluctuation; a whole-rule ensemble simulation (200 ensembles × grid, bootstraps included) with Clopper–Pearson
    bounds; conservative cutoffs; analytic Gaussian fallback; sentinels. §6.1–§6.2.
  - **F̃ normalizes** the spread by its expected (N − 1)/N and its undrawn share (C_PL, C08). §6.1.
  - **Custody and spent-once** (BLOCKING):
    - director-run writer, readout and PG, through the wrapper;
    - director-held seeds, committed by digest;
    - authenticated encryption only, with manifests verified before decrypt;
    - scans after both roles, with trap cleanup;
    - a director-controlled atomic consumption record, with crash semantics;
    - a synthetic-seal wrapper test;
    - the cooperative assumption stated. §3.3, §3.4, §4.2.
  - **ST1 and the exception** (BLOCKING): ST1 is a diagnostic trigger; the exception needs code-level evidence; one
    exception only; its branch stops as its own priced phase PX outside P1's cap. §3.3.
  - **Majors:**
    - where each source acts (§3.2);
    - ST2 eligibility and precedence (§3.3, §6.4);
    - the reservation ledger (§3.3);
    - missing toys (§3.3);
    - the C-PSD fallback scope (§6.2);
    - C_b as a fitted allowance, with the held-out quadratic and outside-span metric (§5.2, §6.1);
    - f̂_R edge cases (§5.2);
    - K_C's fixed combinations and rank check, and measurability eligibility frozen before the seal (§5.3);
    - a span-level residual rule (§5.2);
    - the carry's finiteness and rounding checks (§2);
    - P0's go/no-go control matrices (§3.1);
    - the novelty test (§4.1).
  - **Fidelity:** the 142-eigenvector wording; F1's 1.3275 context; the RE-2 part C citation; PV vs COV2D differences;
    A0's tolerance origin.
- **Rev 6** answers agy's delta read of rev 5 (`reads/agy-rev5-REPORT.md`; NO-GO):
  - the bias grid uses each candidate's own bias block, so it is defined for K0 and K_A (BLOCKING 1);
  - the 20,000-replicate budget, seed and b = 0 setting for q̂ and p̂_i are restored (BLOCKING 2);
  - F_exp is per band (u_R) and defined for K_C (MAJOR 3);
  - the k ≥ 25 SE formula is the normalized one (MAJOR 4);
  - the simulation's inner bootstrap is cut to 200 resamples, with its cost and place stated (MAJOR 5);
  - the stale "inconclusive" in §5.1 and "Grok" in §8 are fixed, and the seed block is named c08 throughout (MINOR).
- **Rev 7** answers codex-school2's confirming read of rev 6 (`reads/codex2-rev6-REPORT.md`; NO-GO, 11 bind-readiness
  fixes; agy's delta read of rev 6 was GO, `reads/agy-rev6-REPORT.md`). Following the director's convergence rule, it
  removes machinery where it can rather than defend it:
  - **Fix 1:** one drawn-covariance decomposition through the spectral map L, used in V_F, u, u_R, F_exp and the law;
    δ is defined as independently drawn, probability-centred shifts; a non-positive F_exp is a refusal (§5.2, §6.1–§6.2).
  - **Fix 2:** q and p_i always come from the 20,000-draw bank, the fallback included (no analytic 0.6827); 0.6827 is
    named a content target; the size statement is conditional on the Clopper–Pearson endpoint event; zero-bias cutoffs
    are a reference, gated over the bias grid; sentinels are reported (§6.1).
  - **Fix 3:**
    - analytic delta-method guards, identical in grading and calibration, replace the bootstrap guard, so no inner
      bootstrap exists;
    - 400 ensembles;
    - per-truth gates of 0.10 (not-PASS) and 0.05 (deficit pass), one-sided Clopper–Pearson, allocated so that a
      candidate stays at or below 0.20 false-FAIL;
    - explicit deficit scenarios D1–D3, with the P-2 pass rate recorded separately;
    - no 0.025/0.075 guarantees;
    - every rate conditional on the surrogate (§2, §6.2, §6.5).
  - **Fix 4:** K_C's k comes from the fixed grid {25, 50, 73}, with the cheap bars evaluated first; a benchmark gates P2
    (§5.3, §6.2).
  - **Fix 5:**
    - a seed‖salt sha256 commitment, per the director;
    - seed-bearing job scripts and logs captured into the encrypted seal;
    - a writer manifest, encrypted and verified before readout decryption, together with the frozen digests;
    - gpg only (age is interactive);
    - cleanup limited to campaign-owned paths (§3.4, §4.2).
  - **Fix 6:** consumption keyed by seal and role; the freeze digest bound at first acquisition; the transition
    persisted before plaintext; any post-decrypt crash is terminal (§3.3).
  - **Fix 7:** ST1 denominators, guards and sequences for a W1 trigger, a W2 trigger, an unexplained firing and a later
    firing; the post-fix acceptance check; PX items; a reprice before any new paid work (§3.3).
  - **Fix 8:** prefix polling removed; the 409.22 ceiling pinned; intents persisted before submission; lost IDs
    reconciled; terminal incompleteness after same-seed retries, for P1 arms and PV (§3, §3.3).
  - **Fix 9:** §4.3 licenses the two named deformations only; §7 is exhaustive in three parts (construction finding,
    baseline challenge, selected candidate); the 02a fallback is for absence only (§4.1, §4.3, §7).
  - **Fix 10:** lateral and norm act on the unfolded output, as in COV2D; the sim stream is pinned; A1f and A1p are
    reported in a common basis; a non-cancelling rounding measure; the A1 map digests, with the C_model lineage named
    as RE-2's statement (§2, §3.2).
  - **Fix 11:** a directed residual; one cutoff rule; degenerate edges assigned to the lower-rank band or included
    whole; measurability inputs and provenance; the C_b⁰ symbol; the frame identity restricted; the outside-span
    fraction in whitened retained coordinates (§5.2, §5.3, §6.1).
  - **Fix 12:** the 142-eigenvector wording (rank fell by one), and the illustration's equal-variance qualifier.
- **Rev 8** applies the director's scope ruling on the rev 7 reads (`reads/*-rev7-REPORT.md`; agy NO-GO on majors only,
  codex-school2 NO-GO with 5 blocking). It takes codex-school2's simpler cuts in full:
  - **ST1:** if PX has no funded path, the branch ends at the construction finding and K_A is omitted. The N5 and
    N4 − N2 guards use band-level influence scores (§3.3).
  - **One Gaussian reference law,** N(0, V_drawn). The band bank, the remainder and the fallback are dropped. V_drawn has
    a C-PSD control and a sampled-covariance control (§6.2).
  - **The testability veto and every rate claim are removed.** The surrogate runs are descriptive stress tests, printed
    and read by nothing. PASS rests only on the fixed affirmative bars applied to the real toys. K0's verdict is reported
    as observed (§6.2–§6.5).
  - **K_C and outcome C are dropped.** The outcomes are A, B or none, plus the construction finding. The measurability
    study stays separate (§5.3, §7). The director informs Joseph of this scope change.
  - **Fixed as written:** codex's PV toy-law sentence (§3.4); agy's three MAJOR (the §9 bars, the N5 guard, D2's
    formula) and three minor (F̃_R's SE, the PX scale note, D3's signs); the outcome rows "PV never ran" and
    "no challenge" (§7).
  - **Custody, in codex's simpler form:**
    - one durable spend record, fsynced and committed before any decryption;
    - one authenticated writer manifest, with every unfold output chained to it;
    - ciphertext hashes only published;
    - pinned gpg flags;
    - terminal rules;
    - the cooperative assumption stated (§3.3, §3.4, §4.2).
  - **The price is unchanged:** 408.55–409.22 node-h. K_C and the testability simulation were laptop-only work, and PV's
    readout gets lighter.
- **Rev 9** makes the rev 8 reads' targeted fixes inside the rev 8 scope (`reads/*-rev8-REPORT.md`), with the
  director's go:
  - **A refusal cannot erase a valid observed deficit.** Readings are graded per truth, FAILS is read before REFUSED,
    and the challenge comes from any valid K0 deficit. Phase-terminal integrity failures are separated from
    candidate-level refusals (§6.4, §7).
  - **Jobs hash what they actually unfold:**
    - each unfold records the sha256 of its actual input and complete output, its expected ID and its invocation;
    - the readout rehashes and requires exactly one product per ID, the central unfolds included;
    - the PG seal is pinned at PG's close and the freeze at P2's (§3.4).
  - **K_B's reference** is the accepted corrected matrix, else Q_rep, so the unfunded branch is defined. Part 1 has its
    own unfunded sentence (§5.2, §7).
  - **The Gaussian control** runs C-PSD on the full matrix and checks that the sampling factor reconstructs it. V₊ is
    used throughout (§6.2).
  - **L** is the full-space map I + Σ(√φ − 1)P_R. The separate rank-wise "Applied" text is deleted. The pool targets
    F_R/F_exp,R (§5.2).
  - **Smaller items:**
    - the PX acceptance inputs per firing row, with W2 out of PX's costs;
    - the band-mean-of-ratios notation;
    - the stdin-to-fd-3 handoff and the integrity gate;
    - the seed‖salt encoding;
    - one amendment deadline, the first spend;
    - a unique ledger intent, and one product per ID;
    - pinned lateral inputs and a rounding preflight;
    - the full A1 digests;
    - one tie convention and a deterministic basis;
    - D1's and D3's guards;
    - stale references removed.
  - **The price is unchanged.** By phase: P0 0; PG 1.33–2.00; P1 291.84 (W1 162.07, W2 129.77); P2 0; PV 115.38. Total
    408.55–409.22 node-h, or 332.55–333.22 without N5. PV's 1.0 node-h for the writer and readout is re-priced from the
    synthetic-seal test before PV.
- **Rev 10** makes the rev 9 reads' targeted fixes (`reads/*-rev9-REPORT.md`; agy NO-GO, 1 MAJOR; codex-school2 NO-GO,
  4 BLOCKING):
  - **K_B's reference** is K_ref = F_A + C_model_abs(x_R), the accepted corrected matrix or else K0. The cut diagnostic
    and residual rule use K_ref, so every branch is executable. Both readers raised this (§5.2).
  - **V₊ is the sole reference covariance:** the law, F_exp (now Σ u_iᵀV₊u_i/λ_i^F), the fit denominators, the cutoffs
    and D2. A zero V₊ is handled before any division (§6.1, §6.2).
  - **The invocation actually launched** (executable sha256 and resolved argv) is hashed and compared with the freeze's
    expected invocation; only accepted attempts count in the chain (§3.4).
  - **A refusal reaches only the readings it affects.** A carry failure refuses all readings at that truth; a reference
    failure refuses F̃, its bands and the flags; an SE or F_exp failure refuses only its own reading. A valid total
    deficit still triggers FAILS (§6.2, §6.4).
  - **Majors and minors:**
    - a fixed 2.0 node-h reservation for the synthetic test, with the production re-price reserved before PV;
    - grades persisted before the stress runs;
    - a canonical Gram–Schmidt basis for tied eigenspaces;
    - every terminal stop before complete grades routes to "ungraded", in the row now named "none, PV ungraded";
    - stale wording removed.
  - **The price includes the synthetic test's 2.0 node-h:** full 410.55–411.22 at PG's priced range (334.55–335.22
    without N5). PV is 117.38, inside its cap of 135. By the director's ruling the ceiling stays 409.22, with ST6 as the
    hard stop (§3).
- **Rev 11** makes the rev 10 reads' fixes (`reads/*-rev10-REPORT.md`; agy NO-GO on 1 MAJOR and 3 MINOR, all textual;
  codex-school2 NO-GO with 2 BLOCKING):
  - **K_B's construction refusal is explicit:** every ensemble in a fitted band needs a carry, a PSD projection to V₊
    and a positive F_exp,R, or K_B is omitted (§5.2).
  - **The secret-bearing readout ends at publication of the grades.** The stress runs are a separate, seal-free job
    whose failure cannot touch the published grades (§3.4).
  - **Majors:**
    - chain records keyed by allocation job ID, with the checks on accepted records;
    - basis rotation only for exact ties, with the 1e-9 convention for band assignment only;
    - ST6 is the ledger's gate at 409.22 alone;
    - §9's stale price is replaced by a pointer to §3.
  - **Minors:** the undefined u and u_R removed; a uses V₊; a grammar fix.
  - The price and the ceiling are unchanged.
- **Rev 11.1.** Both reads of rev 11 were **GO**, with no blocking change (`reads/*-rev11-REPORT.md`). This folds in their
  non-blocking items only:
  - the stress job runs locally at 0 node-h, with its inputs (D_u and V₊) reconstructed from verified central outputs
    and frozen arrays, and pinned in the published grade record (§3.4);
  - the readout selects accepted records before the chain checks (§3.4);
  - the whitening sentence uses W V₊ Wᵀ (§6.1).
  - The price and the ceiling are unchanged.
- **Rev 11.2:** one §3 edit. The binding ceiling is 411.22 node-h, by Joseph's answer "Raise to 411.22 (Recommended)"
  (2026-11-23, via the director; sha256 prefix `8fb26c62f91e7b20`). Earlier entries that mention 409.22 are history.
- **Rev 11.3** answers the director's full read, text only:
  - the passphrase, seed base and salt are kept durably in the director's macOS login Keychain, read only by the wrapper
    into stdin;
  - the consumption record and a secret-free README live in ~/director-tools/covfix/, not a scratchpad (§3.3, §4.2);
  - the stale "about 409" ceiling sentence in §3 is fixed;
  - outcome A's reach within the ceiling is stated: unavailable for `universe`, and for the W1 blocks only if measured
    spend leaves room for PX (§7, §9);
  - the PG roles are stated: the PG session prepares and tests, and the director's wrapper invokes the bound connect
    (§4.2).
- **Rev 11.4:**
  - the ceiling is 541.50 node-h, from Joseph's "Raise to about 540" (sha256 prefix `2edd5a1690819494`) and his direct
    confirmation of the exact figure, "541.5 is perfectly fine" (`adc1262352d73d91`);
  - §3 prints each ST1 branch's priced worst case, with the N5 method now including `stat`;
  - outcome A is reachable for every single-block firing; only a W1 exception plus `universe` is unfunded, by design;
  - binding needs an iris receipt of at least 541.50 node-h;
  - the wrapper's stdin framing and the seed range are written into §4.2;
  - the expected no-firing price is unchanged;
  - a citation fix accepted by the director without a read (2026-11-23): the seed range now cites F1's amendment 2 (7
    tasks per tune, one wave), with the task index still capped at 63. No rule changes.
- **Rev 12 (DRAFT, 2026-11-24):** Joseph's decisions, relayed by the rewrite helper and the director: "lets do the blind
  correlation truth and the three smaller items", and "we can raise the ceiling too". The director writes the governing
  DECISION (`DECISION-<date>-joseph-covfix-rev12`, cited below by that placeholder name).
  - **A third sealed truth, u = 2,** joins the held-out validation family and decides (§4.1, §4.3, §6.4, §7): a
    correlation deformation of p(q3, W | p_T, p∥, E_avail) on the 5D FINE grid, applied by `s5e_deform.ratio_weight`, with
    300 PV toys at seed base 9_820_000 and one central unfold. It leaves the graded 2D truth at nominal, so it tests
    hidden-variable dependence through the response, not a truth shift. **Its definition and custody are a placeholder**
    (§4.2): Joseph is choosing between a human definer and a declared family drawn by a committed seed.
    - **The alternative Joseph may choose instead:** u = 2 graded with every §6 reading but **descriptive**, deciding
      nothing, with the verdict and §7 left at u = 0, 1. That form changes nothing deciding in §5–§7. The director's
      ruling of 2026-11-24 drafts the deciding form, because Joseph's words were "add it to §4's held-out validation
      family", and that family decides.
  - **The price:** the expected no-firing base becomes 468.74–469.41 node-h (PV 175.57, up 58.19 = 300 × 0.19 + 0.19 + the u2-draw's 1.0).
    PV's cap becomes 202. The ceiling becomes 600.00 node-h, funding every single-block ST1 branch (§3's table, recomputed).
    Binding needs a committed iris receipt of at least 600.00 node-h.
  - **Descriptive readings, deciding nothing** (§6.6): the two off-diagonal corners of the factorial between K0 and K_B
    ("fluctuation block only" = V_F + C_model_abs; "bias block only" = F_A + C_b), graded on the same PV toys; the lower
    95 % Clopper–Pearson bound on joint coverage beside P-3; M with its bands both with and without the undrawn
    components, always; and, beside P-2, the undrawn share tr(V⁺U)/ndf and the zero-bias a = tr(V⁺V₊)/ndf, overall and
    per band. P-2 itself stays on the full V.
  - **The amendment rule:** the DECISION supersedes §3.3's "ST1's named exception, the only post-binding amendment to
    §5–§7" for these changes only: the descriptive readings of §6.6, and u = 2's place in §6.4 and §7. Every other
    deciding rule in §5–§7 is unchanged.
  - **u = 2's custody (§4.2), Joseph's choice:** a declared family, drawn by a committed seed, with a reco floor:
    - a tilt of q3–W correlation shapes, calibrated from the public build truths, clipped and raked;
    - attempts derived from the director-held secrets through the wrapper, the first passing one taken, with a 64-attempt
      cap and a STOP;
    - four checks: invariance on the graded weights of all 300 natures, non-triviality, bounds, and a reco floor
      Δᵀ S⁻¹ Δ ≥ 1 on the reco muon (p_T, p∥) histogram that is E_R's complete reco input;
    - unsealed draws reported before sealing, and full disclosure after PV.
  - **The per-phase balance check (§3, ST6):** a committed iris read before each paid phase, against that phase's cap
    plus the expected price of later phases.

<!-- absence-ok: rule statement -->
**Rules are fixed before computation.** Every reading, bar, candidate rule, seed and stop rule below is fixed at
binding, before P0. After binding, §5–§7 may not be amended except by ST1's named exception, or by an executability fix
(a crash or a typo) that changes no number, bar, family, seed or choice rule (§3.3). The executability fix is allowed
only before the first spend of the real PV seal (ST4), and needs the director's ruling. Any other amendment names every
output already seen.
- **Rev 12's amendment** (DRAFT) is made under `DECISION-<date>-joseph-covfix-rev12`, which supersedes the clause above
  for rev 12's changes only: §6.6's descriptive readings, and the third sealed truth's place in §6.4 and §7. It is made
  before any sealed truth exists or any PV toy is drawn, so it is still pre-registration. No output of PG or PV has been
  seen. P0's committed record (the spent tunes) has been seen; rev 12 changes no bar or rule that P0 informed.

## 1. What the review asked, and what the inventory already settles

The review's Fix 1 separates bias from fluctuation:
E[(σ̂ − σ)(σ̂ − σ)ᵀ] = C_fluct + b bᵀ.

Its acceptable outcomes:
- **(A)** a construction error, found and fixed;
- **(B)** the covariance holds for a stated model class, with the truth-model bias quantified separately;
- **(C)** reported uncertainties for coarser or selected combinations only.

It rejects scaling the covariance until the two tunes pass.

The inventory settles four points:
1. **The fluctuation is under-described, not only the bias** (T2A, against COV2D's remade C_T). At the spent tunes the
   spread per component is 1.6 / 3.0 / 4.4 (AR23) and 1.5 / 3.6 / 4.7 (G18) over ranks 1–73 / 74–139 / ≥ 140. So every
   candidate has a fluctuation part, and P1 measures whether that excess exists at nominal (N4) and at other truths
   (A1p).
2. **C_run's trace is small in 2D:** τ = 0.0098 per ndf at both tunes (REGRADE 2D). In the G18 regrade, 142 of C_T's kept
   eigenvectors had a component outside the new kept span, with maximum residual near 1, and the rank fell by one, from
   205 to 204. The trace reading is a separate diagnostic. So every candidate prints the cut diagnostic.
3. **G18 and AR23 are spent.** COVFIX uses them only to calibrate (P0) and to describe. They enter no candidate block,
   no bar and no choice.
4. **Never-read truths are cheap.** F1's whole recorded charge was 1.3275 node-h for both GENIE v3 tunes. That
   includes failed attempts and 0.609167 node-h of downstream closure and pseudo-experiment jobs, so it is historical
   context for PG's estimate, not its price.

## 2. The covariances, the carry, and notation

**The reported matrices.**
- **Q_rep** is the adopted 2D covariance, COV2D-G2R's rebuild (DECISION-20261114-joseph-d1-g2r-adopted.md). Its file is
  key `Q` of #1167's run2 `g2r/outA/cov2d_Q_205.npz`, sha256
  `ff66b91d6d2c574a1786b057ce7566e8ed7184700a45b989fa41ae0eb8cb0295`
  (`fd/receipts-cov2d/g2r/re2shapes/run2/NODE-SHA256.txt:222`). cov2d holds a sha-verified laptop copy.
- **Its blocks:** `Q` = `s5_total` + `C_PL`, and `s5_total` = `universe` + `stat` + `c08`. Both identities were
  measured exact (maximum relative difference 0) on that copy on 2026-11-22. P0 re-checks them as a control.
- **C_model** is RE-2 part C's relative matrix: "C_model = sum_k s_k s_k^T (M2), kappa = 1, fractional", sha256
  `11fe68188bd31a35103f5eb4708bd6a7cdab8965164680caa6671c509dcd3470`
  (`state/2d-closeout/stageF/methods/re2/RE2-PARTC-REPORT.md` §7; `cmodel_R.json`), reported beside
  Q_rep. Absolute at a central value x: C_model_abs(x) = diag(x) C_model diag(x).

**K0, the matrix under test.** COV2D graded C_T = (remade S5 blocks) + C_model_abs at each tune, without C_PL. COVFIX's
reported-procedure analogue at the data's point is:

K0_R = V_F,0 + V_b,0, with V_F,0 = Q_rep (the fluctuation block) and V_b,0 = C_model_abs(x_R) (the model block).

**The carry to a truth t.** All of COVFIX's blocks are absolute at x_R, and they are carried by one formula:

V(t) = D_t V D_t, with D_t = diag(x̂_t / x_R).

- x̂_t is the central unfold, with E_R's argv, of t's expected pseudo-data rounded to integers: round(λ⁺) on every
  signal and background row, with λ⁺ as in §3.4 and round-half-to-even. The data tree holds integer counts only, so a
  fractional Asimov file is not constructible. This costs one unfold per truth.
- x̂_t uses t's CV nature: no band draw and no sim, with r_t applied.
- **Rounding check:** per reco cell with Σλ⁺ > 0, the non-cancelling measure Σ_rows |round(λ⁺) − λ⁺| / Σ_rows λ⁺ is
  reported. A cell above 1e-3 is a refusal. Cells with Σλ⁺ = 0 are excluded and counted.
- **D_t must be finite and nonzero** on all 205 aligned cells, or the carry refuses at that truth.
- The formula has the shape REGRADE §2 used for C_run and COV2D §4.4 used for the seed block c08. Its reference vector is §2's x̂_t,
  not REGRADE's x_T or COV2D's realization-based x̂_T.
- **The carry is not COV2D's remake.** COV2D remade the blocks at each tune with 486 unfolds per truth. COVFIX tests the
  reported covariance carried in relative form, which is the object a user applies. P0 measures the difference at
  G18 and AR23 (§3.1).

**Every candidate** is V = V_F + V_b, a fluctuation block plus a bias block, carried by the formula above.

**Notation.**
- **Truth and toys.** For a truth t and a toy s = 1…N, the error is e_s = σ̂_s − σ_t on the 205 reported cells.
- **One divisor.** b̂_t = (1/N) Σ_s e_s, and S_t = (1/N) Σ_s (e_s − b̂_t)(e_s − b̂_t)ᵀ.
- **The eigenbasis and the cut.** V(t) = Σ λ_i u_i u_iᵀ, with rank 1 the largest. For every candidate, total or
  fluctuation, the kept modes are those with λ_i > 1e-12·λ₁(V_F(t)), referenced to the candidate's own fluctuation block.
  A large bias block therefore cannot shift the truncation of the fluctuation modes. The number kept is ndf. Every
  bootstrap holds the eigenbasis fixed at the full-sample matrix.
- **Per mode and toy:** z_{s,i} = u_iᵀ e_s / √λ_i.
- **Per mode:**
  - m_i = mean_s z_{s,i};
  - v_i = (1/N) Σ_s (z_{s,i} − m_i)²;
  - q_i = mean_s z²_{s,i}.
  - Then q_i = m_i² + v_i exactly.
- **The fluctuation readings use V_F's own eigenbasis.** Writing λ_i^F and u_i^F, the per-mode spread is v_i^F, and
  F^F = (1/ndf_F) Σ v_i^F.
- **Bands:** R1 = ranks 1–73, R2 = 74–139, R3 = ≥ 140. A band is used only if it holds at least 10 kept modes;
  otherwise it is dropped and named as dropped. Q_R, F_R and B_R are the band means of q_i, v_i and m_i².
- **The mean ratios:** M = (1/ndf) Σ q_i, the mean χ²/ndf.
- **The guard** (COVFIX's own rule) is analytic, and the same in every reading and in §6.2's stress runs: h(X) =
  t_{0.975, N−1} · SE(X), where SE(X) = sd_s(ψ_s)/√N and ψ_s is X's per-toy influence term:
  - for M or a total band mean, ψ_s = χ²_s/ndf, or its band analogue. M is a mean of independent per-toy terms, so this
    is exact;
  - for a spread F or a band F_R, ψ_s = (1/ndf_R) Σ_{i∈R} [(z_{s,i} − m_i)² − v_i], the delta-method influence function
    of the sum of 1/N variances;
  - for F̃, SE(F^F)/F_exp, and for a band F̃_R, SE(F_R^F)/F_exp,R;
  - sd_s is the sample SD (divisor N − 1). A zero or non-finite SE refuses that reading;
  - it is a fixed rule with approximate coverage for quadratic toy scores, and is described as such.
  - For a difference of two independent ensembles (ST1), SE² is the sum.
  - Bootstrap SEs are used only for the construction quantity f̂_R and the descriptive bias statistics (§5.2, §6.1).
- **Labels** for any ratio X:

  | label | X |
  |---|---|
  | over | < 0.8 |
  | covers | [0.8, 1.25] |
  | under | > 1.25 |

  A label is read only if [X − h, X + h] lies inside one label's interval. Otherwise the reading is "unresolved across
  <labels>". Bands use the same rule and edges.
- **The total's affirmative bar** is X + h ≤ 1.25: the upper guarded bound lies at or below the tolerance.

## 3. Phases, in order

<!-- absence-ok: reading rule, scoping statement or verbatim review text about studies not yet run -->
| phase | what | price, full (node-h) | price, lean | cap, full / lean |
|---|---|---|---|---|
| **P0** | re-analysis of committed records (§3.1) | 0 (local) | 0 | 0 |
| **PG** | generate, encrypt and seal the two GENIE validation truths, u = 0, 1 (§4) | 1.33–2.0 | 1.33–2.0 | 3.0 |
| **P1 W1** | N1, N2, N5, N3, plus the nominal central unfold and the §2-vector unfolds at G18 and AR23 (§3.2) | 162.07 | 124.07 | — |
| **P1 W2** | N4, A1f, A1p, plus three A1 central unfolds, after ST1 is read on W1 | 129.77 | 86.07 | — |
| **P1** | total | 291.84 | 210.14 | 330 / 240 |
| **P2** | build and freeze the candidates (§5) | 0 (local) | 0 | 0 |
| **PV** | 900 validation toys (300 at each of three sealed truths), 3 central unfolds, the synthetic-seal test (a fixed 2.0 reservation, §3.3), the exclusive-node writer and readout (about 1.0, an unmeasured estimate), and the u2-draw role (about 1.0, an unmeasured estimate, §4.2) (§3.4, §6) | 175.57 | 175.57 | 202 |

- **Totals:** full 468.74–469.41; lean 387.04–387.71, including the synthetic test's 2.0 added in rev 10, at PG's priced
  range of 1.33–2.00.
  - **Rev 12's PV arithmetic:** 900 toys × 0.19 = 171.00, plus 3 central unfolds × 0.19 = 0.57, plus the synthetic
    test's 2.0, the writer and readout's 1.0 and the u2-draw's 1.0, is 175.57 (rev 11.4: 600 × 0.19 + 2 × 0.19 + 2.0 + 1.0 = 117.38; the
    difference is 58.19). PV's cap keeps rev 11.4's proportion, 135 / 117.38: 175.57 × 135 / 117.38 = 201.92, set at
    202.
  - **The u2-draw's 1.0 is expected spend, not contingency,** like the synthetic test's 2.0 (director, 2026-11-24). It is
    re-measured in the synthetic rehearsal, with the writer and readout.
  - These are the expected no-firing prices. The 600.00 ceiling below is headroom for PX only.
  - The ranges come from PG's range only. The printed range starts at 1.33, above F1's measured 1.3275 node-h for two
    tunes.
  - Without N5 (§9.1): full 392.74–393.41; lean 330.04–330.71.
- **Every cell is priced at n × 0.19** node-h per unfold, with no rounding. That is the director's planning figure:
  COV2D's 112.74 node-h over 600 toys is 0.188, including pilots and retries.
- **Lean** sets N1, N2 and N4 to 150 toys each and N5 to 150 + 150, and drops A1f. Cell 4 then rests on IBUKT A2's
  committed 5-draw means at genie_mec and nuwro only. **gibuu has no fixed-response ensemble in the lean campaign.**
- **The balance.** The director's message of 2026-11-22 gives 725.6 node-h, from the iris row read at limitation-
  resolver's S1 survey (login23, 2026-11-22T22:01:53Z). That row is not committed. **Binding requires a committed iris
  receipt.** Half of 725.6 is 362.8. The director has asked limitation-resolver for a fresh committed receipt for rev 12.
- **Against half the balance** (rev 12):
  - every phase price and every phase cap is below 362.8;
  - the caps' sums (full 535, lean 445) are not, and neither is the full total, with or without N5, nor the lean total;
  - only the lean total without N5 (330.04–330.71) is below it;
  - **Joseph chose full** (`DECISION-20261123-joseph-covfix-ki85-size-reader.md`, his governing re-confirmation: "Full, as designed"), with N5, under a ceiling of 541.50 node-h at rev 11.4, raised to 600.00 at rev 12 (below). ST6 keeps the campaign inside that ceiling. The lean columns are kept as the record of the alternative he did not choose.
- **ST6, the cumulative ceiling** (§3.3).
  - Joseph's approved total is pinned in every connect.
  - Each submission's charge ceiling is its nodes × its `--time`. Each toy job's `--time` is 1.5 × its priced per-toy
    time (0.19 node-h is a mean), so a slow job is not killed, and a stalled one cannot charge more than its ceiling.
  - A phase is submitted in chunks small enough that ended charges plus unended ceilings stay within its cap (ST3).
  - The admission check is ST3/ST6's reservation ledger (§3.3), not a prefix poll of sacct.
  - **The ceiling is pinned in the binding at 541.50 node-h (rev 11.4); rev 12 raises it to 600.00 node-h.**
    - **History.** Joseph approved about 409, then raised it to 411.22 for the synthetic test ("Raise to 411.22
      (Recommended)", sha256 prefix `8fb26c62f91e7b20`).
    - **The headroom.** He then raised it again for PX headroom: "Raise to about 540" (the sha256 of the text plus a
      newline begins `2edd5a1690819494`). That option read: "Also funds the systematic-universe rebuild. Close to the
      whole remaining balance in the worst case."
    - **The exact figure.** The director proposed 541.50: inside "about 540" (+0.3 %), and funding every single-block
      branch, including `universe` with laterals rebuilt (541.37). Joseph confirmed it directly: "541.5 is perfectly
      fine" (the sha256 of the text plus a newline begins `adc1262352d73d91`). 541.50 is therefore Joseph's approved
      ceiling.
    - The director records all three in the binding document (`DECISION-20261123-joseph-covfix-ki85-size-reader.md`
      holds the first decisions).
    - **Rev 12's ceiling.** Joseph: "we can raise the ceiling too" (relayed by the rewrite helper and the director,
      2026-11-24), and "Raise the ceiling to about 600" (relayed by the director, 2026-11-24). The director first set
      599; with the u2-draw priced in PV it set 600.00, which funds every single-block ST1 branch on rev 12's base,
      including `universe` with laterals rebuilt (599.56). Joseph sees the final figure when he approves
      rev 12's text and the DECISION, which records it.
    - **The expected no-firing price** is 468.74–469.41 at rev 12 (392.74–393.41 without N5). The ceiling beyond it is
      headroom for PX only.
    - **ST6 is the hard stop:** the ledger's atomic gate (§3.3) at the pinned ceiling (600.00 node-h at rev 12). A submission
      it refuses stops the run, and that goes to the director, not to Joseph as a re-approval. The price table above is
      an estimate, not a trigger; PX keeps its own repricing rule.
    - **Balance:** binding needs the committed iris receipt to show at least the pinned ceiling remaining (600.00 node-h at
      rev 12). If it does not, the binding goes back to Joseph.
    - The ceiling is separate from the expected price and from the 535 sum of caps.
  - **The per-phase balance check (rev 12).** The m3246 pool is shared with other users, so the binding-time receipt
    does not protect later phases. Before each paid phase (PG, W1, PX, W2, PV), a committed iris read must show the
    pool's remaining node-h ≥ that phase's cap plus the expected price of every phase after it. Otherwise the phase
    stops and goes to the director.
    - "That phase's cap" is PG's 3.0, PV's 202, PX's bound price, and, for W1 and for W2, the P1 cap (330) less P1's
      reconciled charges.
    - The expected prices after a phase are those of §3's table (and PX's, only once bound).
    - **At rev 12's figures**, before any spend:

      | before | requirement |
      |---|---|
      | PG | 3.0 + (162.07 + 129.77 + 175.57) = 470.41 |
      | W1 | 330 + 175.57 = 505.57 |
      | PV | 202 |

    - Binding at 600.00 is satisfied today: iris showed 630.4 node-h remaining for the whole m3246 pool at 06:55Z on
      2026-11-24 (PR #1276, merged `62be2eff`).
  - **The priced worst case for each ST1 branch,** with PG at its 2.0 top, on rev 12's no-firing base
    2.00 + 162.07 + 129.77 + 175.57 = 469.41:

    | ST1 branch | PX | total | at 600.00 |
    |---|---|---|---|
    | none | 0 | 469.41 | fits |
    | `c08` (W1) | 15.20 | 484.61 | fits |
    | `stat` (W1) | 57.00 | 526.41 | fits |
    | N5 data-stream method (W1), which also regenerates `stat` | 95.00 | 564.41 | fits |
    | `c08` + `stat` (W1) | 72.20 | 541.61 | fits |
    | `c08` + N5 method + `stat` (W1) | 110.20 | 579.61 | fits |
    | `universe` after W2, laterals reused | 128.25 | 597.66 | fits |
    | `universe` after W2, laterals rebuilt (+10 unfolds) | 130.15 | 599.56 | fits |
    | any W1 exception + `universe` | ≥ 145.35 | ≥ 614.76 | **unfunded by design** |

    - Rev 11.4's table, on its base of 411.22 against 541.50, is the same less 58.19 in every total.

    - The last row is unfunded whatever the ceiling: under §3.3's sole-exception rule, a row firing after the exception
      has been bound stops the campaign.
    - PX for `universe` includes its redraw of N4 and A1p (95.00). PX for the N5 method includes 200 replicas (38.00)
      and `stat` (57.00).

### 3.1 P0: what the committed records give (0 node-h, local, descriptive)

- **Controls:** Q_rep's two block identities, its sha256, C_model's sha256, and C-PSD on every block:
  λ_min ≥ −1e-12·λ_max. **A failure stops at P0.**
- **The carry check.** At G18 and AR23, K0 carried by §2's formula is compared with COV2D's remade C_T.
  - The carry is done twice: with COV2D's committed realization-based x̂_T from `blocks_<T>.npz`, and with §2's round(λ⁺)
    vector, whose two unfolds run in W1. The P0 readings that need the second vector are completed after W1.
  - The readings are COV2D's committed errors `E_<T>.npz` under each, the eigenvalue ratio per band, and the principal
    angles between the kept spans.
  - This is descriptive. It states the size of the carry approximation and of the difference between the two vectors.
- **The residual rule's go/no-go control on spent data.** §5.2's residual rule is applied to the committed regrade
  pair at G18 and AR23:
  - "old" is COV2D's C_T from `blocks_<T>.npz`, with its fluctuation reference C_T − C_model_abs(T);
  - "new" is C_T + C_run(T), with C_run carried from Q_rep's `C_PL` exactly as REGRADE carried it;
  - both are evaluated at the tune's frame, with C_T's own x̂_T.
  The rule's maximum principal angle between the well-determined spans is printed. If the rule fires there, P0 stops
  and goes to the director: a rule that rejects that pair would reject K_B for no reason.
- The per-mode profiles (m_i, v_i, q_i) of COV2D's committed errors under the carried K0, under C_T, and under G2R's
  C_T′.
- IBUKT A2's mean residuals (`state/2d-closeout/ibukt-a2/readout.json`), times E_R, in K0's modes: m_i only.
- c2 as scoped: T2A's mean error projected on C_PL's two directions.

These validate nothing.

### 3.2 P1: the construction measurements

Each cell is a toy ensemble unfolded by the production procedure (re2_driver.py, E_R's argv). The seeds are
pre-committed and disjoint from every committed ensemble; a test checks them against COV2D's, c08's and S1's seed lists.

**The full source list** is "data Poisson + bands + lateral + norm + sim", where:
- the bands are COV2D's 38: Flux (one of 100 universes, constraint-weighted), 2p2h (1 of 3), and the 36 others (one
  endpoint each), composed first-order on `w_reco`, `w_truth` and `w_bkg` by `cov2d.draw` (COV2D §4.2);
- lateral is COV2D's surrogate over 5 bands;
- norm is x̂ × (1 + 0.014 z);
- sim is S1's signal and background simulation-weight Poisson redraws at fresh seeds.

**Where each source acts.** COV2D's `--data-file` replaces the data tree and leaves the unfolding simulation in
`--omnifile`.
- **Data Poisson** acts on the pseudo-data only.
- **The 38 weight bands and the truth deformation r_t** act on the toy's nature: its pseudo-data and its graded truth,
  as COV2D §4.2 composes them. The unfolding uses the CV simulation, so a band draw makes the nature differ from the
  unfolding model. That is the sense of "perturbed response" here; the unfolding response itself is not redrawn by a
  band.
- **Lateral and norm act on the unfolded output,** as COV2D §4.2 applies them, after the unfold: x̂ += Σ_b s_b Δ_b(t)/2,
  then x̂ × (1 + 0.014 z). They do not touch the graded truth.
- **Sim** acts on the unfolding side only. It redraws the simulation weights the unfold uses, as S1's three-stream
  bootstrap does, multiplying the CV simulation weights, independently of the nature's band draws. It changes neither
  the pseudo-data nor the graded truth.
  - Toy s's sim stream is `numpy.random.default_rng([seed_s, DRAW_SALT, 2])`. That is the third stream beside COV2D's
    draw stream `[seed_s, DRAW_SALT]` and count stream `[seed_s, DRAW_SALT, 1]`.
  - The redrawn weights reach the unfold through the bootstrap-weight hook S1's code already uses.
- **N4 − N2** is the incremental change in scatter from the nature-side sources. It is read as additive only under the
  blocks' own additive model, which is disclosed, not verified.

| cell | truth | what each toy draws | toys full / lean | seed base | node-h full / lean |
|---|---|---|---|---|---|
| **N1** data stream, same-event | nominal | Poisson pseudo-data at data size from the MC reco weights | 200 / 150 | 9_100_000 | 38 / 28.5 |
| **N2** + simulation statistics | nominal | N1 + sim | 200 / 150 | 9_200_000 | 38 / 28.5 |
| **N5** data stream, held-out | nominal, MC half A | pseudo-data from half A, unfolded with half B's response; plus half-B data-stream bootstrap replicas (`--bootstrap-streams data`) for that configuration's own data-stream block S1_B | 200+200 / 150+150 | 9_500_000 (toys), 9_510_000 (replicas), 9_520_000 (split) | 76 / 57 |
| **N3** estimator seed | nominal | one fixed N1 pseudo-dataset (seed 9_300_100); estimator seeds 9_300_000–9_300_049 | 50 / 50 | — | 9.5 / 9.5 |
| **N4** all sources at nominal | nominal | the full source list, with r ≡ 1 | 200 / 150 | 9_400_000 | 38 / 28.5 |
| **A1f** alternative truth, fixed response | genie_mec, nuwro, gibuu (the three named PV2D deformations) | N1 only, response nominal, truth deformed by the vertex's 2D map | 3 × 60 / 0 | 9_600_000 + 10_000·j | 34.2 / 0 |
| **A1p** alternative truth, perturbed response | the same three | the full source list at the deformed truth | 3 × 100 / 3 × 100 | 9_700_000 + 10_000·j | 57 / 57 |
| **central unfolds** | nominal; the three vertices; G18 and AR23 | round(λ⁺) pseudo-data (§2), one unfold each, for D_t | 1 + 3 + 2 | — | 1.14 / 1.14 |
| **existing** | G18, AR23 | COV2D's toys (data Poisson + bands + lateral + norm; no sim) | 300 + 300 | committed | 0 |

- j = 0, 1, 2 for genie_mec, nuwro, gibuu.
- **The named deformations** are PV2D's ratio files `2d-unfolding/pv2d/ratios/{genie_mec,nuwro,gibuu}.json`, sha256
  `cfaaf4d663a392ce7283c1427ef25845a76663f9d218b906613de72ee5a79143`,
  `785180dd9dba80a0dfd24ce2e3b9fc1973f31e3df4678f21f4003cf3c1c0d804` and
  `b62c224ac4321f385a2b7892a8d24aa788a8a8c7bc65331f3ea335a43135d10a`, each matching `projections.json`
  (`8241807f4dddf678a5b1473112f6f36b614d43cc5a4b3e932bb2d3f7d32f05c3`).
  - That these are the shifts behind C_model ("C_model = sum_k s_k s_k^T") is RE-2 part C §7's statement, and is not
    re-verified here. The text calls them the named deformations.
- **A1f and A1p are in-sample.** A1f measures the estimator's bias at those truths (the review's cell 4, in-sample), and
  A1p the truth-dependent spread. Both are reported in one common basis, K0's fluctuation block carried to each truth,
  as bias (m_i) and centred scatter (v_i) side by side. The held-out alternative truths are PV's.
- **C_PL and C_run are not drawn,** because they have no generative law (SCOPING a3). They enter V_F as covariance.

### 3.3 Stop rules

**ST1, a diagnostic trigger for a construction-defect investigation.** It is read on W1 (N2, N3, N5) before W2 is
submitted, and on W2 for N4. A firing row flags a discrepancy; it does not by itself identify a defect.
- Each reading uses the spread only, never q, because nominal closure bias (IBUKT A2: up to 1.708 % noise-free) would
  otherwise enter. Nominal bias is reported separately (m_i, B_R).
- **The common basis** is K0's fluctuation block Q_rep, carried to x̂_MC and diagonalized there.
- **The ratio:** each row's per-mode ratio is ŝ_i over the row's denominator, projected in that basis, with
  ŝ_i = λ_i v_i. Only modes whose projected denominator exceeds 1e-12 × its maximum over modes are used.
- **The guard is §2's analytic SE.**
  - **Band-level influence scores.** Each row's guarded quantity is the band mean of per-mode ratios,
    (1/ndf_R) Σ_{i∈R} Â_i/B̂_i, with Â_i from toys and B̂_i from a block or, for N5, from replicas. By the delta method
    on that mean, there is one influence score per toy and, where B̂ is estimated, one per replica. The modes share toys
    and replicas, so the scores are computed for the band as a whole.
  - N4 − N2 is computed this way on each side, and the two independent variances add.
  - For N5, the toy-side and replica-side variances add, under conditional independence of the two ensembles. The
    replica-side term uses the derivative −Â_i/B̂_i² of each ratio with respect to its denominator.
- Every band with at least 10 modes can fire.

| block | reading (band mean of the per-mode ratio, guarded) | ST1 fires if any band reads |
|---|---|---|
| `stat`'s data-stream part, through its bootstrap method | N5: ŝ_i / u_iᵀ S1_B u_i, with S1_B from N5's own 200 replicas | "under" or "over" |
| `stat` (three streams) | N2: ŝ_i / u_iᵀ stat u_i | "under" only. An N2 "over" is recorded and does not fire, because KI 85's earlier-band finding allows same-event under-scatter; that is a possibility, not a guarantee of direction. |
| `c08` (the seed block) | N3: ŝ_i / u_iᵀ c08 u_i. One pseudo-dataset with the seed varied, against the production seed block. | "under" or "over" |
| `universe` | (ŝ_i^{N4} − ŝ_i^{N2}) / u_iᵀ universe u_i. This includes interactions between draws, clipping and the response, disclosed. | "under" or "over" |

N1 is never a construction-error reading. N1/N5 is reported as the same-event factor.

**The ST1 sequences,** fixed now. In every branch, no new paid work starts before the director's ruling.
1. **A W1 row fires.** W2 is not submitted. cov2d investigates the firing blocks' builders and reports.
   - **With code-level evidence,** the named exception below is written, and PX is priced. PX covers:
     - the regeneration;
     - the post-fix acceptance check.
     The whole remaining campaign (PX + W2 + PV, with W2 counted once) is repriced against the ceiling.
   - **Without code-level evidence,** the firing is "unexplained". The campaign continues without K_A only if the
     director rules so.
2. **The W2 row (`universe`) fires.** P2 does not start. The same investigation follows.
   - With evidence, PX covers the regeneration, the redraw of N4 and A1p (95.00), and the acceptance check, and the rest
     of the campaign is repriced.
   - Without evidence, the firing is "unexplained", as in 1.
3. **Repricing.** If the repriced remainder fits the ceiling, the director binds PX.
   - If it does not, PX has **no funded path**, and the ST1 branch ends at the construction finding, reported as a
     finding (§7, Part 1). K_A is omitted for this run, and the campaign continues with K0 and K_B.
   - W2's first-time work is counted once in the remainder, never as part of PX.
   - Every single-block branch fits the ceiling on the priced figures (§3's table: 541.50 at rev 11.4, 600.00 at rev 12),
     and so does every W1 combination. A W1 exception followed by a `universe` firing is unfunded by design (item 4).
4. **A row fires after the sole exception has been bound.** The campaign stops and goes to the director.

**ST1's named exception, the only post-binding amendment to §5–§7.**
- **It needs code-level evidence:**
  - a reproducing unit test that fails on the old builder and passes on the corrected one;
  - the named bug;
  - the post-fix acceptance check: the firing row's reading recomputed with the regenerated block, in the same common
    basis. Its inputs, fixed now:
    - for the N5 row, the same N5 toys against the half-B block rebuilt by the corrected method (200 new replicas);
    - for the N2 row, the same N2 toys against the regenerated `stat`;
    - for the N3 row, the same N3 toys against the regenerated `c08`;
    - for the `universe` row, a redrawn N4 (the redraw PX already prices) minus the reused N2, against the regenerated
      `universe`.
    It needs at least one band with at least 10 modes, and "covers" in every such band.
- **If the bug reproduces but acceptance fails,** the finding is "defect found; correction did not resolve the
  discrepancy". K_A is not formed, and the branch ends.
- **It may change** only the code that generates the firing blocks, never a substituted matrix. It may not change any
  bar, seed, the validation family, the §5.2 factor rule, C_b's rule, or §7's order. One exception covers
  every row that fired by then.
- **PX's itemized regeneration:**
  - `universe`: 175 unfolds (33.25), plus 10 lateral (1.90) if laterals are rebuilt;
  - `stat`: 300 replicas (57.00);
  - `c08`: 80 unfolds (15.20);
  - if the data-stream method is corrected: the N5 replicas, 200 (38.00), and `stat`, which that method builds (57.00).
  The amendment states which constituents are reused. PX is outside P1's cap and inside the ledger.
- K_A is Q_rep with the corrected blocks, plus C_model_abs.

**KI 85.** Joseph superseded **both** of KI 85's sentences for COVFIX
(`DECISION-20261123-joseph-covfix-ki85-size-reader.md`). So N5 runs, and outcome A may change the 2D covariance; a change
enters the journal paper or a later Zenodo version, not the first release. Had he not superseded them, ST1 would record
and regenerate nothing, and N5 would not run. That gate is kept for the record.

**ST2, eligibility for PV.**
- The eligible candidates are K_A (if formed and PX was funded) and K_B, each only if it meets §5.3 at P2.
- K0 always runs as the baseline.
- A K_A that fails P2, or one omitted because PX had no funded path, is recorded in §7's construction finding.
- If no candidate is eligible, PV does not run. The baseline is then ungraded (§7).
- **If PX has no funded path,** the ST1 branch ends at the construction finding, reported as a finding, and K_A is
  omitted for this run.

**ST3 and ST6, one reservation ledger.**
- The ledger is serialized under flock in the campaign directory, and keyed by allocation job ID.
- **Before any submission,** an intent entry with a unique intent ID (a random 128-bit hex string), the phase and the
  reservation is persisted. The intent ID is embedded in the job name, `covfix_<phase>_<intent>`. After submission, the
  job ID is recorded.
- **Lost IDs.** If a connect dies between submitting and recording, the next connect first reconciles every open intent
  from sacct, matching the intent ID in the job name against active and terminal jobs. Until that is done, no
  submission proceeds.
- **Uncertainty keeps the reservation open,** whether about acceptance or about the final charge.
- **Each expected toy ID** in a P1 arm, PX or PV is accepted exactly once, with one verified complete product.
- **The synthetic-seal test** gets a fixed advance reservation of 2.0 node-h under the PV cap.
- Its measurements, scaled to the 900-toy workload (rev 12; 600 at rev 11.4), re-price the production writer and readout. That price is reserved
  before PV is submitted.
- A descriptive stress run's failure never blocks a completed grade.
- **Reservations:** nodes × `--time` (1.5 × the priced per-toy time), including exclusive allocations, with
  allocation-level walltime rounding. Jobs run with `--no-requeue`.
- **Accounting lag.** A reservation stays open until sacct shows the job terminal, and its charge is then reconciled
  once.
- **The gate,** atomic under the flock: reconciled charges plus open reservations plus the new reservation must stay
  within both the phase cap and the pinned ceiling (§3).

**ST4, validation is spent once.**
- **The consumption record** is controlled by the director: append-only, in **~/director-tools/covfix/** (mode 700, not
  a scratchpad), mirrored in a commit, and keyed by **seal digest and role** (PV writer, PV readout).
- **The freeze digest is bound** to the seal at its first acquisition. A later freeze digest never resets consumption.
- **The spend is durable before any plaintext exists.** Under one lock, the wrapper appends "spent" for the original
  seal and role, fsyncs the record, and commits its mirror. Only then does it start decryption.
- **Terminal rules:**
  - an uncertain spend, from a lock or write failure, is terminal;
  - restoring a copy of the record, or changing the freeze, cannot create a fresh role;
  - a crash after decryption is a terminal stop for that role, with no retries;
  - same-seed retries apply only to the ordinary unfold jobs, never to the two secret-bearing roles;
  - any break in the seal, the manifest or the chain is terminal.
- An executability fix never permits a grading change after exposure.
- PV's readout writes one JSON of summary statistics; per-toy residuals and z arrays stay inside the process.
- §5–§7 cannot be amended after binding, except by ST1's exception, or by an executability fix that changes no number,
  bar, family, seed or choice rule. That fix is allowed only before the first spend of the real PV seal, the same
  deadline as in the rules paragraph above.
- **The limit:** a later construction needs new sealed truths, and the catalog may not supply a third distinct family.

**ST5, guard refusals are terminal** for their phase: fences, atime, provenance, the A0 controls, the seal and
decryption checks, the manifest and chain checks, the scans, and C-PSD on the input blocks and candidates. §6.2's
controls refuse a candidate at a truth (§6.4) rather than stop the phase.
- **Completeness:** every P1 arm (including N5's replicas and PX's diagnostics) and every PV truth needs all of its toys.
- A job that ends other than COMPLETED may be resubmitted with identical seeds, at most twice, decided before any
  reading of that arm.
- If any toy is still missing after that, the phase is **incomplete and terminal**, and goes to the director. There is
  no grading on a subset; a failure can depend on a toy's input even when no residual has been read.

### 3.4 What a PV toy draws, and where

PV draws the full source list of §3.2, the same as N4 and A1p, at a sealed truth u.

- **The truth deformation.** For u = 0, 1, r_u is u's own bridged ratio, applied per row by
  `s5e_deform.ratio_weight(gen, FINE, w_truth, ratio, 1.0)`, computed once with the CV `w_truth` and its rescale constant
  from `mc_truth_denom`'s rows (COV2D §4.1). The same per-row factor applies to every `mc_signal_reco` row. Rows outside
  the 5D grid and background rows get r = 1.
- **For u = 2** (rev 12), r_2 is §4.1's correlation deformation on the 5D FINE grid (pt, pz, eavail, q3, W), applied by the
  same `s5e_deform.ratio_weight` call and the same rules for rows outside the grid and background rows. It leaves the
  graded (p_T, p∥) truth at nominal (§4.3). Its definition and custody are §4.2's placeholder.
- **The toy law is §3.2's single recipe:** the 38 bands composed on the nature's reco and truth; lateral and norm on
  the unfolded output; sim on the unfolding side; Poisson on the pseudo-data.
  - **The lateral Δ_b(t)** are carried in relative form from part B's lateral products, Δ_b ∘ (x̂_t / x_R), as COV2D §4.4's
    fallback carries them, so no remake is priced.
    - The five endpoint differences Δ_b are pinned by sha256 at binding, from part B's lateral product list.
    - Their orientation and the X01 treatment for Muon_Energy_MINOS are as `re2c_rollup.py:235-253` defines them.
  - **A rounding preflight:** before any paid toy submission, §2's rounding check runs on the nominal inputs, on a login
    node at 0 node-h. A refusal there stops the campaign.
  - **The draw order** is `cov2d.draw`'s: Flux, then the other 37 bands sorted, then the lateral signs, then norm. Sim
    and counts use their own streams.
- **The pseudo-data** are Poisson at λ⁺ = max(·, 0), on a count stream separate from the draw stream.
- **The graded truth** is each toy's own clipped composite truth, normalized with the drawn Flux universe's integral and
  completeness ≡ 1 (COV2D §4.2).
- **The estimator seed** is fixed at 42, and the seed block c08 is in every candidate.
- **Count:** 300 toys per sealed truth, seed base 9_800_000 + 10_000·u (u = 0, 1, 2), plus one central unfold per truth.
  u = 2's base, 9_820_000, follows the same formula; its toys' seeds 9_820_000–9_820_299 are disjoint from u = 0's and
  u = 1's (9_800_000–9_800_299, 9_810_000–9_810_299), from every P1 seed (9_100_000–9_720_099, §3.2; A1p's last arm, j = 2, ends at 9_720_099), and from the
  bootstrap and stress seeds (9_991_000–9_994_000).

**Who runs it, and where, in order.** cov2d writes and tests the bound PV code; it does not run the secret-bearing
roles. The **writer** and the **readout** are run by the director, or a session the director controls, through the
director's wrapper. The wrapper acquires ST4's consumption record, verifies every ciphertext's sha256 against
`PG-SEAL.sha256` before decrypting, and pipes the passphrase on stdin.
1. **The writer** runs on an exclusive compute node (`salloc --exclusive -N 1`, then `srun --exclusive -N 1 <writer>`,
   which forwards stdin to the task). The decrypted r_u lives only in that node's /dev/shm.
2. In that one process it writes, for all 900 toys (600 at rev 11.4), the pseudo-data files (reco-level counts, which the
   compute jobs need) and the graded truths, plus the three round(λ⁺) files for D_u. The graded truths are encrypted (§4.2) before they
   touch disk.
   - It also writes **one authenticated manifest**, encrypted with the same flags. The manifest binds the graded
     ciphertexts, the toy IDs, the hash of each pseudo-data file, and the central inputs, to the original PG manifest's
     digest and to the director-authorized freeze digest. Both digests are pinned in the binding.
3. Before exiting, and through a trap on failure, it removes its enumerated campaign-owned temporary paths on that node
   (in /dev/shm and /tmp). It then scans those paths and the campaign directory **by content**: every file's sha256 is
   compared against the plaintext hashes in the PG manifest, and every file is checked for an unencrypted graded-truth
   array. A hit stops the study. An exact-hash scan detects exact copies only, not repacked or partial plaintext, and
   that is disclosed.
4. The compute jobs unfold the pseudo-data only.
   - **The chain:** each job hashes the **actual input file it unfolds**, its **complete output**, and the **invocation
     it actually launched**: the executable's sha256 and the resolved argument vector. It appends a chain record of
     (allocation job ID from the ledger, expected truth and toy ID, input sha256, output sha256, invocation sha256), all
     as computed.
   - **The readout** first selects the accepted records by ledger allocation ID; the ledger marks a failed attempt's job
     ID as excluded. On that set it compares each record with the authenticated manifest and with the freeze's expected
     invocation for that ID, rehashes each output it consumes, and runs the missing, extra and mismatch checks. Exactly
     one verified product per expected ID must come from the accepted set.
   - A missing, extra or mismatched record is a break, and terminal.
   - The same applies to the three central unfolds that determine D_u.
   - The original PG seal is pinned at PG's close, and the freeze at P2's, so both are in PV's binding.
5. **The readout** runs on its own exclusive node, from a fresh pipe. Before decrypting any graded truth, it verifies:
   - the writer's manifest;
   - the frozen code and arrays against `P2-FREEZE.sha256`.
   - the chain from the writer's manifest to every unfold output.
   It then decrypts the graded truths in-process, runs §6.2's controls, grades, persists the verified grades, cleans up,
   scans, and publishes the grades. Then it ends. Cleanup and scans cover enumerated campaign-owned paths only.
6. **The descriptive stress runs** are a separate job, after publication, with no seal access. They run on this laptop,
   at 0 node-h, outside the ledger.
   - **Inputs:** they reconstruct D_u from the verified central-unfold outputs and V₊ from the frozen candidate arrays.
     Both are pinned by sha256 in the published grade record.
   - A scenario whose inputs are unavailable is reported as omitted.
   - Their failure, timeout or crash leaves the published grades untouched, and failed scenarios are reported as
     omitted.

<!-- absence-ok: reading rule, scoping statement or verbatim review text about studies not yet run -->
**The wrapper is tested** before PV on a synthetic seal: a dummy truth, encrypted and sealed the same way, run end to
end. That test also measures the writer and readout allocation time, which replaces PV's unmeasured 1.0 node-h estimate
in a re-price before PV is submitted.

**After the freeze,** the unfolded outputs alone are not graded errors, and nothing they reveal can change a frozen
candidate (ST4).

**PV differs from COV2D's G18 and AR23 toys in more than sim:**
- different tunes;
- a different grading matrix (the carried K0 or a candidate, not COV2D's remade C_T);
- a different central-vector convention (round(λ⁺) and its unfold, not one Poisson realization);
- a different null (§6.2) and decision rule (§6.3).

The shared toy ingredients are the nature draws (`cov2d.draw`), the Poisson pseudo-data, the graded-truth construction
and the estimator. N2 probes sim's increment at nominal truth; it cannot establish sim's share at the alternative truths.

## 4. The validation truths

### 4.1 Which, and how many

- **Two never-read GENIE v3 tunes,** each with a CCQE or 2p2h model that the spent tunes do not use:
  1. `G21_11b_00_000`;
  2. `G18_02b_02_11b`, or `G18_02a_02_11b` only if 02b is absent: the same G18_02 construction, with a different
     intranuclear transport.
- **Both are required.** If either family is absent from the genie_xsec `v3_04_00` product on Perlmutter, PG stops and
  goes to the director. No FSI twin of a spent tune may replace it.
- **A third sealed truth, u = 2** (rev 12): a blind correlation deformation of p(q3, W | p_T, p∥, E_avail) on the 5D FINE
  grid (pt, pz, eavail, q3, W), applied by `s5e_deform.ratio_weight`. It is not a GENIE tune and is not generated by PG;
  it reweights the nominal simulation. It keeps p(p_T, p∥, E_avail), so the graded 2D truth is the nominal's (§4.3). It
  joins the held-out validation family, and it decides (§6.4). Its definition and custody: §4.2, placeholder.
- **What the names mean,** as v3.2.0 descriptions pending PG's probe of v3_04_00, from GENIE's "Global Fits and Physics Tunes" page (https://genie-mc.github.io/tunes.html,
  read 2026-11-22; it covers v3.0.0–v3.2.0):
  - In the CMC token (`11b`, `02b`), the letter selects the intranuclear transport: a = INTRANUKE/hA,
    b = INTRANUKE/hN, c = Liège/INCL, d = Geant4 Bertini. The trailing `_02_11b` is GENIE's "final 2020 free-nucleon
    x-section retune".
  - G21_11* "uses the SuSAv2 QE and 2p2h model". **Overlap, disclosed:** spent AR23_20i_00_000's 2p2h is
    `SuSAv2MECPXSec` (FD-F1-REPORT.md §1.3), so G21_11b shares AR23's 2p2h. Its CCQE (SuSAv2) differs from both spent
    tunes' `NievesQELCCPXSec`.
  - G18_02* is "similar to G18_01* CMCs, but upgrade[s] the resonance and coherent pion production models (RS → BS)".
    The page says G18_10* adds to it "a consistent theory-based model of interactions around the quasi-elastic peak (NAV
    QE and NSV 2p2h model)", so G18_02 does not carry spent G18_10a's NAV QE and NSV 2p2h. The page does not name
    G18_02's own QE and 2p2h models.
- **PG's stat-only probe,** before any generation:
  - it lists the product's tune qualifiers;
  - it prints, for each chosen tune, the CCQE and 2p2h model class names from GENIE's own tune configuration (public
    configuration, not generated content);
  - it confirms an encryption tool (§4.2).
- **The novelty test,** applied to the probe's output: a chosen tune qualifies only if at least one of its CCQE class
  and its 2p2h class is used by **neither** spent tune. A tune whose two classes both appear among the spent tunes'
  classes is excluded, even in a new pairing. The 02a fallback substitutes only for 02b's **absence** from the product.
  02a shares 02b's CCQE and 2p2h classes, so a novelty exclusion of 02b excludes 02a too. If no qualifying tune
  remains for a slot, PG stops.
- The probe's output, the fallback taken and the overlap record are committed before generation. Partial overlaps are
  disclosed in §4.3.
- FD-F1-DECLARATION.md:76 is cited only for the product, path and qualifier convention.

### 4.2 Custody

**Who generates.** A session that is not cov2d and has read none of COV2D, T2A, G2R, REGRADE or this declaration's
§5–§7: a fresh session Joseph opens, which the director names at binding. **Binding requires it.** That session runs
F1's bound pipeline (`gen5d_v3.py`, `run_gevgen_v3.sh`, the pv-ladder ratios and the bridge), unchanged except for the
tune names and the seeds.
- **The seeds are director-held,** so a builder cannot regenerate the truths from public tune names and public seeds.
  - The director draws PG's seed base and a random salt.
  - Before generation, the director publishes sha256(seed base ‖ salt), and reveals both after PV's readout. The
    encoding is the seed base in ASCII decimal, one ':', then the salt as 64 lowercase hex characters (32 random bytes),
    with no newline.
  - Tune u's task seed = base + 10_000·u + task index.
  - **Range:** the seed base is uniform in [1e9, 2e9), and F1's pipeline as run takes 7 tasks per tune in a single wave
    (FD-F1-DECLARATION-AMENDMENT-2.md, superseding FD-F1-DECLARATION.md §F1b's 64). The task index is capped at a
    ceiling of 63, below 10,000, so the seed bound holds a fortiori. The largest task seed is 2,000,010,062, below
    2³¹ − 1, as `run_gevgen_v3.sh` passes it to both `--seed` and `-r`. PG's binary refuses a computed seed at or above
    2³¹ − 1.
  - F1's generator takes the seed in its command arguments. PG's job scripts and logs therefore stay in the PG
    session's directory and are captured into the encrypted sealed set, under the cooperative assumption below.
- **Roles.** The PG session prepares and tests its run directory. The **director's wrapper invokes the bound PG
  connect**, with the passphrase piped in, so the PG session never holds the passphrase. The PG session's working
  directories are private to it by convention, and that privacy rests on the one-account limit below.

**What it sees.** Its connect captures every stdout, stderr, log and meta file into the sealed set. The session sees
only a final summary of booleans (each step's pass/fail) and file counts. Physics outputs, such as f_MEC, process
fractions, CC counts and the ratio normalization k, are in the sealed meta only.

**The director-held secrets, and their durability.** PV comes weeks after PG, and a scratchpad does not survive that
long: it is wiped by a crash, and macOS cleans /private/tmp after about 3 days. Losing the passphrase would make the
ciphertext unrecoverable, with no regeneration allowed. Losing the seed base or salt would break the commitment reveal.
So:
- **Storage.** The passphrase, the seed base and the salt are stored in the director's macOS login Keychain, as
  `security add-generic-password -s covfix-<item> -a director -w`, with the items passphrase, seed-base and salt.
- **Reading.** The wrapper alone reads them back, through `security find-generic-password -s covfix-<item> -a director
  -w`, piped straight into the bound binary's stdin (over ssh, into `srun`'s forwarded stdin).
- They are never in a file, an argument or the environment, so they never enter shell history or the Slurm spool.
- **The stdin framing,** fixed:
  - PG's binary reads `<passphrase as 64 hex>\n<seed base in decimal>\n`, then EOF;
  - the PV writer and the PV readout read `<passphrase>\n` only;
  - the salt never leaves the laptop, because the commitment is computed and revealed there;
  - each binary refuses any other framing.
- **A secret-free README** in ~/director-tools/covfix/ (mode 700) names the Keychain service names and states the
  procedure, so that a later director session can continue PV. It holds no secret.

**Seal and encryption.**
1. The plaintext sha256 of every product is computed with O_NOATIME reads. **The plaintext hashes are never
   published.** A plaintext hash of a seed-bearing product, such as a predictable job script, would let anyone check
   seed guesses. They go only into an encrypted PG manifest.
2. Each product is encrypted with pinned flags. The passphrase reaches the bound binary on its stdin: the director's
   wrapper pipes it into `srun`, which forwards stdin to the task. The binary hands it to gpg on fd 3 through an internal
   pipe, and streams the payload on gpg's stdin and stdout. srun does not forward other file descriptors.
   - encrypt: `gpg --batch --yes --pinentry-mode loopback --passphrase-fd 3 --no-symkey-cache --symmetric --cipher-algo AES256 --s2k-digest-algo SHA512 --force-mdc`;
   - decrypt: `gpg --batch --pinentry-mode loopback --passphrase-fd 3 --no-symkey-cache --decrypt`.
   gpg's non-zero exit on an integrity (MDC) failure is a refusal, and no decrypted product is used before gpg has
   exited 0. PG stops if the probe does not find gpg, or if a synthetic round trip with these flags fails.
3. A decrypt-and-hash round trip must reproduce each plaintext sha256.
4. The plaintext is deleted.
5. A content scan, of enumerated PG-owned paths only, against the plaintext hash list must come back empty, with
   cleanup through a trap on failure.
6. `PG-SEAL.sha256` (**ciphertext** sha256 per product, plus the encrypted PG manifest's ciphertext sha256) is committed
   **before P1's first connect**.

**Copies.** The ciphertext sits on pscratch and, **required**, on HPSS (htar from a login node, then hashverify). The
ratio files are not committed to the repo until PV's readout is. A missing or altered ciphertext stops the study. There
is no regeneration.

**Limits, disclosed.**
- All sessions share one Unix account. An exclusive node limits scheduling; it does not isolate a shared identity,
  filesystem, logs or process access.
- Before PV, the barriers against cov2d are the director's key and the director-held seeds, not file permissions.
  Beyond those, the design rests on a cooperative assumption: no builder reads another session's private directories
  or processes. That assumption is stated, not enforced.
- Atime does not detect O_NOATIME reads, so it is housekeeping only.
- The generating session saw the plaintext and is retired after PG.

**The third truth (u = 2): definition and custody (rev 12 DRAFT).** Joseph chose a **declared family drawn by a committed
seed, with a reco floor** (relayed by the director, 2026-11-24).

*The family.* On the 5D FINE grid (`pvl_lib.FINE`: 14 p_T × 16 p∥ × 7 E_avail × 7 q3 × 6 W = 65,856 cells), with w the
CV `w_truth` of `mc_truth_denom`'s rows binned on that grid:
- In each (p_T, p∥, E_avail) cell, ξ and η are q3's and W's bin centres, standardized within the cell under w (mean 0,
  variance 1). Cells with fewer than two populated (q3, W) bins get r = 1.
- **The basis φ:** φ₁ = ξη, φ₂ = (ξ² − ⟨ξ²⟩)η and φ₃ = ξ(η² − ⟨η²⟩), with ⟨·⟩ the cell's w-mean: a small basis of q3–W
  correlation shapes, which leave each cell's q3 and W means unchanged to first order.
- **The tilt:** r⁰ = exp(c₁φ₁ + c₂φ₂ + c₃φ₃), with |c₁| ∈ [a_lo, a_hi], |c₂|, |c₃| ≤ |c₁| / 2, and all three signs drawn.
- **Clip, then rake:** r⁰ is clipped to [0.5, 2]. Then iterative proportional fitting on w·r restores, to 1e-9
  relative, the joint (p_T, p∥, E_avail) distribution and the global q3 and W marginals of w, within 200 iterations.
  Non-convergence is an attempt failure. The raked r is applied per row by `s5e_deform.ratio_weight(gen, FINE, w_truth,
  ratio, 1.0)`. Its in-grid renormalization is then 1 to within the raking tolerance.
- **The calibration of [a_lo, a_hi],** fixed now as a rule and computed before any draw. For each public build truth
  g ∈ {genie_mec, nuwro, gibuu}, D_g is the w-weighted mean over (p_T, p∥, E_avail) cells of |ρ_g − ρ_ref|. Here ρ is the
  within-cell q3–W correlation of the bin centres under the generator's 5D density, and ref is untuned GENIE 2.12 CV.
  These are the same pinned predictions PV2D's ratio files cite:
  - `genie_cv_xsec5d_full.npz` `cfa42210dfe9cadc8e9460333316a639bd719c9ae52ab1144be900372a9adcc2`;
  - `genie_mec_xsec5d_full.npz` `c179855df6e42a5b8bab1f839aae675c53a5150f132649c855356ad75f26790f`;
  - `nuwro_cv_xsec5d_full.npz` `475a2871304db23efedbd5ab42a32d91c7f1d295b6dd0c907c46aa6d81c48070`;
  - `gibuu_cv_xsec5d_fluxfix.npz` `48917692ee1295902db3bec34d6c80e368f020ae7924dabbda7e996c461cca18`.
  [a_lo, a_hi] is set so that φ₁ alone at |c₁| = a_lo and a_hi gives, after clipping and raking, a w-weighted mean
  within-cell |Δρ| equal to min_g D_g and max_g D_g. **The numerical values are not yet computed.** The four files are
  on pscratch only, and their fetch (a login-node read by sha) needs the director's go. The script, its output and
  [a_lo, a_hi] are committed before any draw, sealed or unsealed.
  <!-- absence-ok: scoping statement about this declaration's own method parameter, defined here and computed later -->

*The draw.* Attempt k = 1, 2, … takes its parameters from SHA-256(domain tag ‖ seed base ‖ salt ‖ k):
- The domain tag is "covfix-u2-correlation-draw/1". The seed base and salt are the director-held secrets of §4.2, whose
  commitment is already published, so the draw is replayable after their reveal.
- The 32 digest bytes give four 64-bit unsigned integers, U_i = n_i / 2⁶⁴. |c₁| = a_lo + (a_hi − a_lo)·U₁; |c₂| =
  (|c₁| / 2)·U₂; |c₃| = (|c₁| / 2)·U₃; the three signs are bits 0–2 of n₄.
- **It runs only through the director's wrapper,** as a secret-bearing role ("u2-draw") on one exclusive node (about 1.0 node-h in PV's price, §3), with the
  §4.2 stdin framing and JE's round-3 contract. Its binary is cov2d's to write and goes through §8's chain.
- **The first passing attempt is taken.** The attempt cap is K_max = 64. If no attempt passes by k = 64, the role ends
  without a map, and that is a STOP to the director. u = 2 is then not formed, and PV does not run until the director
  and Joseph rule.
- **Sealing:** the taken map r_2 is encrypted and sealed as PG's products are (§4.2), with its manifest and seal file.
  Every attempt's parameters and check results, the count and the timing are sealed with it. They are revealed in full
  after PV's readout, so the selection can be replayed.

*The checks inside custody.* Each prints pass or fail only; nothing else leaves the role.
1. **Invariance, on the weights the toys grade.** Two parts:
   - (a) at CV: the raked w·r reproduces w's joint (p_T, p∥, E_avail) and its q3 and W marginals to 1e-9 relative;
   - (b) for each of u = 2's 300 toy natures (drawn by `cov2d.draw` at their public seeds, §3.4), the graded 2D truth
     (the clipped, band-varied composite truth of §3.4, normalized as there) with r_2 and without it differs by at most
     0.05·σ_c on every reported cell. σ_c is the data-statistical standard deviation, √(stat_cc) from Q_rep's `stat`
     block at x_R.
   - Band variation is handled by checking every nature, not only CV. `ratio_weight` restores only the in-grid CV total,
     and r_2 is fixed per row, so a band's reweighting of q3 and W within a cell can move the graded truth slightly;
     (b) bounds that motion at 5 % of the data's statistical error.
2. **Truth-level non-triviality:** the w-weighted mean within-cell |Δρ(q3, W)| of the raked map is at least
   0.5·min_g D_g.
3. **The bounds:** the raked r lies in [0.4, 2.5] on every FINE cell whose CV support meets `pvl_lib.SUPPORT_MIN`, and
   is finite and positive everywhere.
4. **The reco floor:** Δᵀ S⁻¹ Δ ≥ 1.
   - Δ = μ(r_2) − μ₀ and S = diag(μ₀), where μ₀ is the expected reco summary at nominal and μ(r_2) the same under r_2.
     Both are at one dataset's exposure (data POT), signal plus background. Cells with μ₀ = 0 are excluded and counted.
   - **The reco summary, frozen now:** the joint histogram of the reco muon (p_T, p∥) of every passing event, on FINE's
     (p_T, p∥) edges (224 cells, 14 × 16).
   - **Why this summary.** It is the complete set of reco features E_R's OmniFold uses. `re2_driver.py:2336-2338`
     builds MCreco and the measured array from (reco_pt, reco_pz) only, and the data tree carries `measured`,
     `measured_pz` and `measured_pass` and nothing else (`re2_driver.py:1096`). A summary built on other variables
     would test reco differences the unfold cannot see, and a floor on them would mean nothing. The director accepted
     this summary on 2026-11-24, with a separate read agreeing that `re2_driver.py:2336` stacks only reco p_T and p∥ for
     the 2D unfold.
   - In 2D, a muon-only histogram is therefore the right object, not a coarse stand-in. The advisory's concern about a
     muon-only histogram applies where the unfold has more inputs. The joint 224-cell binning keeps the p_T–p∥
     correlations the unfold learns from, and the total rate is inside it.
   - A score of 1 is roughly a one-standard-deviation separation along the shift, in the local Gaussian approximation
     with Poisson statistics. It is a modest floor, and it guarantees no unfolded bias and no coverage power.

*Before sealing, on unsealed draws.* The same family and checks are run with a public domain tag,
"covfix-u2-correlation-unsealed/1", and a public seed published in the same commit, never the committed secrets. Over
200 unsealed attempts it reports:
- how often each check rejects, and the floor in particular;
- for draws within 20 % of the floor, how often a map crosses it under 50 bootstrap resamplings of the simulation (finite
  simulation noise);
- which (φ₁, φ₂, φ₃) directions survive raking and the cuts.
This report is committed before the sealed draw. It is a description, and changes no cut after the fact.

*After PV, published:* the cut, the reco summary, the taken map's achieved score Δᵀ S⁻¹ Δ, the redraw count, and every
sealed attempt's record.

### 4.3 What the validation family can and cannot show

u = 0 and u = 1 are GENIE v3 configurations. G21_11b shares AR23's 2p2h class, and G18_02's models will be named by the
probe. A pass licenses readings at the **three named deformations under the fixed toy law** only (rev 12; two at rev
11.4), with those overlaps stated beside it. It does not license a GENIE v3 model family, or any other generator. A
non-GENIE generator truth would need a sample this project does not have; that is disclosed, not tested.

**u = 2 leaves the graded 2D truth at nominal** (rev 12). Its deformation changes only p(q3, W | p_T, p∥, E_avail), so the
graded (p_T, p∥) cross section, a marginal over q3 and W at fixed E_avail, is the nominal's. What changes is the response:
the reconstruction's efficiency and migration depend on q3 and W, so the unfold sees a different hidden-variable mix at
the same 2D truth. u = 2 therefore **tests hidden-variable dependence through the response, not a truth shift.**
- C_b, fitted from truth shifts (§5.2), is **not what u = 2 tests**. A u = 2 deficit speaks to the fluctuation block and
  the response model, not to the bias allowance.
- u = 2 is a reweighting of the nominal simulation. It is not a generator sample, and it shares the nominal's physics
  outside the deformed conditional.
- **A PASS at u = 2 applies to one sealed draw from the declared family**, conditional on the declared cuts (invariance,
  non-triviality, the bounds and the reco floor), under the fixed toy law. **Weakly visible maps, below the reco floor,
  are outside the claim.** At u = 2 the 2D unfold can respond only through the hadronic dependence of the muon-side
  efficiency and smearing: that is the mechanism u = 2 tests. The floor selects a subset of the family, favouring changes the reco summary measures well;
  its effect on the difficulty of passing the bars can go either way, and that is disclosed beside any u = 2 reading.

## 5. Candidate constructions, built from P0 and P1, frozen at P2

**The build data** are N1–N5, A1f and A1p. COV2D's G18 and AR23 toys are descriptive only. **The selection data**, the
only data any P2 bar or choice reads, are N4 and A1p. G18 and AR23 never enter a bar or a choice; their readings under each candidate
are printed descriptively. Nothing in PG's seal is read.

### 5.1 K0, the control, and K_A

- **K0** = Q_rep + C_model_abs(x_R), carried (§2): fluctuation block Q_rep, model block C_model_abs. Its expected PV
  reading is "under". **If K0 is VALIDATED at every sealed truth (§6.4; three at rev 12),** the comparison showed no
  need for a change at those truths ("no deficit shown", §7).
- **K_A** is Q_rep with ST1's firing block regenerated (ST1's named exception), plus C_model_abs. **If ST1 does not fire,
  K_A = K0, and K_A is not read separately.** Outcome A is then unavailable.

### 5.2 K_B: the fluctuation block and the bias block

**Fluctuation block.** The reference F_A is defined without K_A:
- if ST1's exception was applied and its acceptance check passed, F_A is that corrected matrix's fluctuation block,
  whether or not K_A later passes P2;
- otherwise (no firing, unexplained, unfunded, or acceptance failed), F_A = Q_rep.
F_A is absolute at x_R, and it is the reference throughout §5.2.

- **Measured.** For each ensemble E with truth t_E, F_A is carried to t_E (§2) and diagonalized there. F̃_R(E) is E's
  normalized band spread in that carried basis: F_R(E) / F_exp,R(E), with F_exp,R as in §6.1, using F_A's own undrawn
  part C_PL + c08. The finite-N factor (N − 1)/N is applied once, inside F_exp,R.
- **The pooled spread ratio,** which targets the same normalized spread that P2 and PV grade:

  f̂_R = (1/4) Σ_{E ∈ {N4, A1p(genie_mec), A1p(nuwro), A1p(gibuu)}} F̃_R(E)
- **SE(f̂_R)** is the standard deviation of f̂_R over 2,000 joint bootstrap replicates, each resampling every ensemble
  inside itself at seed 9_991_000, with every eigenbasis held fixed at its full-sample matrix.
  - No independence between modes is assumed.
  - The disjoint seeds give independent random streams **conditional on the one shared simulation bank**; independence
    over alternative banks is not claimed.
  - The 3·SE trigger is a construction rule, with no stated error-rate guarantee.
- **Edge cases, fixed:**
  - **construction inputs:** every ensemble that enters a fitted band needs a successful carry, a successful PSD
    projection of F_A − U (with L = I) to its V₊, and a finite, positive F_exp,R. If any of those fails for an
    ensemble the band needs, K_B is omitted, and that is reported;
  - an ensemble whose carried band holds fewer than 10 kept modes is left out of that band's mean, and the equal
    weights go to the rest;
  - if none remain, the band's factor is 1;
  - ranks are by eigenvalue, and only kept modes count;
  - **degenerate edges:** if eigenvalues within 1e-9 relative of each other straddle a band edge, the whole cluster is
    assigned to the lower-rank (higher-variance) band. This one convention applies to construction, admission and
    grading alike.
  - **A deterministic basis:** numpy `eigh`, with each eigenvector's sign fixed so its largest-magnitude component is
    positive.
  - **For an exactly tied eigenspace** (equal eigenvalues to floating-point equality, in a grading eigensystem), the
    basis is canonical: the ordered cell axes e_1, e_2, … are projected into the eigenspace and orthonormalized in that
    order by Gram–Schmidt, skipping null projections. The per-mode flags then do not depend on the solver.
  - The 1e-9 near-tie convention above is used **only** for band assignment, never for basis rotation.
- **One decomposition, through the spectral map L,** on the full space. With P_R the projector onto F_A's band-R kept
  eigenspace at x_R (degenerate clusters assigned whole, as above):
  - L = I + Σ_{R active} (√φ_R − 1) P_R;
  - a band is active where f̂_R − 1 > 3·SE(f̂_R), and then φ_R = f̂_R; factors are never below 1;
  - L = I on every direction outside the active bands, including the cut complement;
  - for K0 and K_A, L = I, each with its own constituent blocks.
  - V_F = L F_A Lᵀ.
  - Every constituent block is mapped the same way: L·universe·Lᵀ, L·stat·Lᵀ, L·c08·Lᵀ and L·C_PL·Lᵀ. So the undrawn part
    is U = L(C_PL + c08)Lᵀ, and the drawn part is V_F − U.
  - Both are carried by the same formula.
  - §6.1's F_exp and §6.2's law use this drawn part, through its PSD-handled form V₊.
- **The post-carry fit** of V_F is reported per ensemble truth and per band.
- f̂_R is a rank-band summary transferred across bases. It is not a mode-matched estimate, and that is disclosed.
- **Why this is not the rejected scaling:**
  - f̂_R is measured on fluctuation ensembles at nominal and at three non-spent truths;
  - G18 and AR23 do not enter it;
  - it is one pre-registered factor per band, never searched until a bar passes.
  This is disclosed beside any result.

**The fitted bias allowance C_b, in the reference frame.** F_bias = {nominal (N4's mean), genie_mec, nuwro, gibuu (A1p means)}: the
non-spent build truths only. Each member is mapped to x_R before the sum:

β_t = D_t⁻¹ b̂_t, Σ_t = D_t⁻¹ S_t D_t⁻¹, and C_b = [ Σ_{t ∈ F_bias} (β_t β_tᵀ − Σ_t/(N_t − 1)) ]₊

- [·]₊ is the positive part: the eigen-decomposition with negative eigenvalues set to 0. Its rank is at most 4.
- **It is the sum, not the mean,** so no member is diluted. Writing C_b⁰ = Σ_t β_t β_tᵀ for the undebiased sum,
  β_tᵀ (C_b⁰)⁺ β_t ≤ 1 for each member. C_b itself, debiased and projected, need not keep that bound.
- **The frame identity** b̂_tᵀ V(t)⁻¹ b̂_t = β_tᵀ V⁻¹ β_t holds for ordinary inverses with D_t nonsingular. The grading
  pseudoinverses, with their own cuts, are computed directly in the truth's frame.
- **G18 and AR23 are not in C_b.** Their biases are large; T2A's mean-error parts against C_T are 13.61 and 20.97 per
  ndf. In the sum they would set the bias block's width in exactly the directions a GENIE tune's bias is expected to
  lie, and the one-sided total bar would then pass by their size. Their mapped biases β_G18 and β_AR23 are printed
  against C_b descriptively: β ᵀC_b⁺β, the fraction outside C_b's span, and M under K_B.
- **What C_b is, and is not.** C_b is a fitted bias allowance.
  - The positive-part projection changes its expectation, and it can lose the undebiased sum's member-wise bound.
  - It is not claimed to bound any model class, nor to over-cover every smaller bias.
  - The total is barred by an affirmative upper bound (§6.3). The fluctuation is barred two-sided and separately.

**K_B = V_F + C_b** at x_R, carried by §2's formula.
- **Its reference total** is K_ref = F_A + C_model_abs(x_R), with F_A as defined above: the accepted corrected matrix
  if one exists, else Q_rep, so K_ref = K0 in that case. K_ref exists on every branch, including the unfunded one, and
  stays the reference even if an accepted K_A later fails P2.
- K_B must pass C-PSD and print its cut diagnostic against K_ref's:
  - the kept sets under §2's cut, each referenced to its own λ₁ of the fluctuation block (F_A for K_ref, V_F for K_B);
  - K_ref's kept modes outside K_B's kept span, and their maximum residual;
  - the smallest kept and the largest dropped eigenvalue.

**Residual rule (K_B against K_ref only):**
- Only K_ref's well-determined modes are checked, those with λ_i ≥ 1e-6·λ₁(F_A), evaluated at x_R.
- With U_ref,well their orthonormal basis and P_B,kept the orthogonal projector onto K_B's kept span, K_B is not
  admissible if the directed residual ‖(I − P_B,kept) U_ref,well‖₂ exceeds 0.1. It is directed, so a smaller new span
  lying inside the old one cannot pass by dropping an old direction.
- An ndf difference alone is printed, not a stop; tail modes below 1e-6·λ₁(F_A) are printed, not stopped on.
- P0 calibrates this rule on the committed regrade pair (§3.1).

### 5.3 Admission bars (P2, on the selection data only)

A candidate V = V_F + V_b is admissible only if, at N4 and at each A1p truth, it passes **the same bars as PV** (§6.3,
P-1 to P-4):
- F̃ and every band with at least 10 modes read "covers";
- M + h ≤ 1.25, and the same for every total band;
- no joint or per-mode under-flag;
- §6.2's controls pass.

It must also pass C-PSD, and, for K_B, §5.2's residual rule. These bars are in-sample, so they admit a candidate; they
never pass one. G18's and AR23's readings under every candidate are printed and decide nothing.

There is no reduced-reporting candidate. The measurability study is a separate study, and no COVFIX reading depends on
it.

### 5.4 Freeze

At P2's end, the code and arrays defining K0, K_A (if any) and K_B are committed with sha256 in `P2-FREEZE.sha256`, and
bound by the director before PV's first connect.

## 6. Readings and bars, fixed now

### 6.1 Per ensemble and per truth

<!-- absence-ok: reading rules for future measurements -->
**Fluctuation readings,** against V_F in V_F's carried basis (u_i^F, λ_i^F).
- **The undrawn part** is U = L(C_PL + c08)Lᵀ carried (§5.2). C_PL is not drawn, and c08 is not drawn because the seed
  is fixed at 42.
- **For a correct V_F,** the expected 1/N spread ratios use V₊, the covariance actually sampled (§6.2):
  - total: F_exp = ((N − 1)/N) · (1/ndf_F) Σ_i u_iᵀ V₊ u_i / λ_i^F;
  - band R: F_exp,R = ((N − 1)/N) · (1/ndf_R) Σ_{i∈R} u_iᵀ V₊ u_i / λ_i^F.
  - The same formulas give §5.2's fit denominators.
  - A denominator at or below zero refuses the readings that need it: F̃ or that band's F̃_R. In the fit, it refuses
    K_B's construction.
- **What is labelled** is F̃ = F^F / F_exp, and per band F̃_R = F_R^F / F_exp,R. F_exp and each F_exp,R are printed.

**Total readings,** against V = V_F + V_b:
- M and its bands;
- the split M = (1/ndf)Σm_i² + (1/ndf)Σv_i, exact under §2's divisor. The m_i² part includes the noise of the
  estimated mean;
- §5.2's cut diagnostic.
- Every reading is stated separately for each sealed truth and each band with at least 10 modes.

**The held-out bias against the fitted allowance** (descriptive, K_B only). With β̂_u = D_u⁻¹ b̂_u and
Σ_u = D_u⁻¹ S_u D_u⁻¹:
- **Q_u** = β̂_uᵀ C_b⁺ β̂_u − tr(C_b⁺ Σ_u)/(N_u − 1), with C_b⁺ the pseudoinverse at cutoff 1e-12 × C_b's largest
  eigenvalue.
- **The outside-span fraction.** y = W_F β̂_u, with W_F whitening V_F's kept modes at x_R. The fraction is
  ‖(I − P)y‖² / ‖y‖², with P the projector onto the range of W_F C_b W_Fᵀ, whose rank is set by the 1e-12 cutoff. Both are
  in that one frame. A zero denominator is reported as undefined.
- Both carry toy-bootstrap SEs (seed 9_993_000). They enter §7's sentences, and decide nothing.

**Joint and per-mode readings.**
- **The joint reading** is the count K_J = #{s : χ²_s ≤ F⁻¹_{χ²(ndf)}(0.6827)} against V(t). Here 0.6827 is a fixed
  content target.
- **The per-mode reading** is #{s : |z_{s,i}| ≤ 1}.
- **The reference probabilities** q (joint) and p_i (per mode) are estimated from 20,000 draws of §6.2's Gaussian law at
  zero bias, at seed 9_992_000, per candidate and truth. The whitened covariance W V₊ Wᵀ is not the identity, so no
  analytic 0.6827 is assumed.
- **The cutoffs:**
  - "under" at a count ≤ k_J, the largest k with P(Bin(N, q) ≤ k) < 0.025; per mode, the largest k with
    P(Bin(N, p_i) ≤ k) < 0.025/ndf;
  - "over" symmetrically;
  - each uses the conservative end of its 95 % Clopper–Pearson interval: the lower end for "under" and the upper end
    for "over";
  - a cutoff no k satisfies has a sentinel, −1 or N + 1, which never flags. P-3 and P-4 then report "no under-flag
    (flag impossible at this N)".
- A nonzero bias changes the reference probabilities. The cutoffs are a fixed recipe against the zero-bias reference,
  and no flag-size claim is made beyond that recipe.

### 6.2 The reference law and its controls

**The law,** for a candidate V at truth t: e ~ N(0, V₊(t)), where V₊ is V_drawn = V_F − U (§5.2), carried and then
PSD-handled as below. There is no band bank, no remainder and no fallback. V₊ is the sole reference covariance: for
F_exp, for §5.2's fit, for the cutoff draws and for the stress runs.

**Controls:**
- **C-PSD on the full carried V_drawn(t):** λ_min ≥ −1e-12·λ_max over all 205 eigenvalues. Eigenvalues within
  ±1e-12·λ_max are set to 0, which gives V₊.
- **A zero V₊** (every eigenvalue set to 0) refuses the readings that need the reference, before any check divides by
  its norm.
- **The sampling factor** is A = U₊ diag(√λ₊), and it must reconstruct V₊: ‖AAᵀ − V₊‖_F / ‖V₊‖_F ≤ 1e-10.
- **The marginal sampling check:** the 20,000 draws' sample covariance Ŝ must satisfy max_i |u_iᵀŜu_i / λ_i − 1| ≤ 0.05
  over V₊'s nonzero modes. That is five times the per-mode sampling SD √(2/20000) = 0.01.
- **A failure of any of these controls is a reference failure.** It refuses the readings that need the reference at that
  truth (§6.4), not the whole candidate.

**Descriptive stress runs,** printed and read by nothing. For each candidate and truth, 400 ensembles of N errors per
scenario (seed 9_994_000) are graded by §6.3's rule, and the pass fractions are printed:
- zero bias;
- b = ±√κ_j w_j for each eigenpair of the candidate's own bias block, with eigenvalues above 1e-12 × the largest and each
  sign fixed so the largest-magnitude component is positive;
- three deficit scenarios, with φ the drawn fluctuation and a = tr(V⁺V₊)/ndf:
  - **D1:** at zero bias, φ scaled by √(1.25/a), if a > 0;
  - **D2:** for each total band R with at least 10 modes, with P_R = Σ_{i∈R} u_i u_iᵀ in V's basis,
    φ → (I − P_R)φ + √(1.25/a_R) P_R φ at zero bias, where a_R = (1/ndf_R) Σ_{i∈R} u_iᵀ V₊ u_i / λ_i; defined if
    a_R > 0;
  - **D3:** for each bias direction w_j, b = ±β w_j with β² = (1.25 − a)·ndf / (w_jᵀV⁺w_j), if a < 1.25 and w_jᵀV⁺w_j > 0;
  - an undefined scenario is printed as omitted.
- They veto nothing, and no rate is claimed from them.

### 6.3 PASS at a sealed truth (PV)

Every check is affirmative, applied to the real toys:
- **P-1, fluctuation:** F̃ reads "covers", and every band F̃_R with at least 10 modes reads "covers". An unresolved band
  fails.
- **P-2, total:** M + h ≤ 1.25, and the same for every total band with at least 10 modes.
- **P-3:** no joint under-flag, reported as in §6.1 when a sentinel applies.
- **P-4:** no per-mode under-flag, reported the same way.

### 6.4 The PV verdict per candidate, and precedence

**Per truth first.** At each sealed truth, each reading is either valid or refused, and a refusal reaches only the
readings it affects:
- **a carry failure** (§2) refuses every reading at that truth, because every reading needs V(t);
- **a reference failure** (§6.2's checks on V₊) refuses the readings that need the reference: F̃ and its bands, which use
  F_exp, and the joint and per-mode flags, which use q and p_i. M and the total bands need only V(t), so they stay
  valid;
- **a zero or non-finite SE, or a non-positive F_exp,** refuses only its own reading.
- A refused reading is printed as refused, and every valid reading at that truth is still graded. §6.2's controls are
  required for VALIDATED, and an independently valid total deficit triggers FAILS and the challenge.
- **Phase-terminal integrity failures are different:** a seal, manifest or chain break, or a failed scan (ST5). They stop
  PV for every candidate, and the baseline is then ungraded (§7).

**Then the verdict,** read in this order; the first condition that holds is it:

| verdict | condition |
|---|---|
| **FAILS** | at any sealed truth, a valid reading shows: M − h > 1.25, or a total band does so; P-3 or P-4 flags "under"; or F̃ or a band reads "under" |
| **REFUSED** | no FAILS, and a required reading is refused at any sealed truth |
| **INFLATED** | no FAILS and no refusal, and F̃ or a band reads "over" at any sealed truth |
| **VALIDATED** | P-1 to P-4 hold, with every required reading valid, at every sealed truth (u = 0, 1, 2 at rev 12) |
| **UNRESOLVED** | otherwise, for example a band unresolved across labels, or M + h > 1.25 with M − h ≤ 1.25 |

K0's verdict is reported as observed. A refusal cannot hide a valid observed deficit, because FAILS is read first, and
every refusal is printed beside it.

**Rev 12:** "any" and "every" range over the three sealed truths u = 0, 1, 2. At rev 11.4 they were "either" and "both"
over u = 0, 1. The order of the conditions and every bar are unchanged. The alternative Joseph may choose instead is in
the change log: u = 2 descriptive, with this table over u = 0, 1 only.

### 6.5 No operating rates are claimed

PASS rests on the fixed affirmative bars applied to the real toys. §6.1's cutoffs are a fixed recipe against the
zero-bias Gaussian reference. §6.2's stress runs are descriptive. COVFIX claims no false-PASS or false-FAIL operating
rate.

### 6.6 Descriptive readings added in rev 12 (decide nothing)

<!-- absence-ok: descriptive reading rules for future measurements -->
Each reading below is printed at every sealed truth, on the same PV toys, and labelled "descriptive". None enters §6.3,
§6.4, §5.3 or §7, and none is read by any rule. They are added under `DECISION-<date>-joseph-covfix-rev12` (the rules
paragraph before §1).

**The factorial's off-diagonal corners.** With K0 = F_A + C_model_abs (F_A = Q_rep unless an accepted K_A exists, §5.2)
and K_B = V_F + C_b, the two changes from K0 to K_B are the fluctuation block (F_A → V_F) and the bias block
(C_model_abs → C_b). The other two corners isolate each:
- **"fluctuation block only"** = V_F + C_model_abs(x_R): K_B's fluctuation block with K0's bias block;
- **"bias block only"** = F_A + C_b: K0's fluctuation block with K_B's bias block.
- Each is carried by §2's formula and graded with every §6.1 and §6.2 reading, as a candidate is. Its kept modes are
  referenced to its own fluctuation block's λ₁ (V_F, F_A). Its drawn part is its fluctuation block less the undrawn part
  under the same map (V_F − L(C_PL + c08)Lᵀ, F_A − (C_PL + c08)), handled to V₊ as §6.2 does.
- **The alternative not taken:** a stacked form F_A + C_model_abs + C_b, which adds K_B's bias block on top of K0's.
  It is off the factorial (it changes no single block of K0), so it isolates neither change.
- They are graded only if K_B was formed (§5.2). They inherit K_B's omission otherwise.

**The lower 95 % Clopper–Pearson bound on joint coverage,** beside P-3, for each candidate and truth: the lower end of the
two-sided 95 % Clopper–Pearson interval for K_J / N (§6.1), printed with q, the reference probability. It is a
description of the observed joint count, not a bar.

**M and its bands, with and without the undrawn components,** always, for each candidate (and the two corners above) at
each truth:
- **(i) against V − L·C_PL·Lᵀ:** V(t) with the run-period block removed (C_PL, carried by D_t as C_run is; L = I for K0
  and K_A). This is the reported covariance without C_PL;
- **(ii) against V − U (all undrawn width):** V(t) less the whole undrawn part U = L(C_PL + c08)Lᵀ of §6.1, carried.
  **(ii) is not the P-2 bar.** P-2 is read against V(t) as §6.3 states.
- Each is printed beside M and its bands against V(t), with the same guards.

**Beside P-2: the undrawn share and the zero-bias expectation,** for every candidate (and the two corners above) at every
sealed truth, overall and for every total band with at least 10 modes, in V(t)'s basis (u_i, λ_i) and kept set:
- **the undrawn share** tr(V⁺U)/ndf = (1/ndf) Σ_i u_iᵀ U u_i / λ_i, and per band (1/ndf_R) Σ_{i∈R} u_iᵀ U u_i / λ_i;
- **the zero-bias a** = tr(V⁺V₊)/ndf = (1/ndf) Σ_i u_iᵀ V₊ u_i / λ_i, and per band a_R (the a and a_R of §6.2's stress
  scenarios), the mean χ²/ndf the toys would give with no bias and the candidate's own drawn width.
- Both decide nothing. **P-2 stays on the full V(t)** (§6.3).

## 7. What each outcome licenses (adoption and wording remain Joseph's and the director's)

The result has three independent parts, each reported.

**Part 1: the construction finding** (ST1 and its exception), licensed by its own evidence, whatever PV finds:
- "ST1 did not fire."
- "ST1 fired at <rows>; unexplained."
- "A construction defect in <block>'s builder was found (a reproducing test fails on the old builder and passes on the
  corrected one); the corrected block passed the acceptance check." Then whether K_A was eligible at P2.
- "A construction defect in <block>'s builder was reproduced (reproducing test as above); PX had no funded path, so the
  correction and its acceptance check did not run, and K_A was omitted for this run."
- "A defect in <block>'s builder was found; the correction did not resolve the discrepancy."

**Outcome A within the ceiling** (§3's table: 541.50 at rev 11.4, 600.00 at rev 12):
- Outcome A is reachable for **every single-block firing**: `c08`, `stat` or the N5 data-stream method on W1, or
  `universe` after W2, laterals included.
- It is also reachable for every combination of W1 blocks.
- **Unfunded:** a W1 exception followed by a `universe` firing. That stops the campaign under §3.3's sole-exception rule,
  and the result is the construction finding for the W1 blocks.
- ST6 still enforces the ceiling against measured spend at the time of each submission.

Any covariance change from Part 1 enters the journal paper or a later Zenodo version, not the first release
(`DECISION-20261123-joseph-covfix-ki85-size-reader.md`).

**Part 2: the baseline** (K0's PV verdict, as observed):
- **challenge:** at one sealed truth at least, a valid K0 reading shows a FAILS condition, whatever K0's other readings
  are. Any refusal is printed beside it;
- **no deficit shown:** K0 is VALIDATED at every sealed truth. "At the three named sealed truths (two GENIE v3 tunes,
  and a hidden-variable response test with the 2D truth at nominal), the reported covariance showed no deficit under
  these bars."
- **unchallenged:** K0 is INFLATED, UNRESOLVED or REFUSED;
- **ungraded:** PV did not produce complete grades. That covers ST2 leaving no eligible candidate, and every stop or
  terminal rule before complete grades: integrity failures, and ST5's terminal incompleteness after retries.

**Part 3: the selected candidate:** the first VALIDATED, in the fixed order K_A, K_B, among the eligible candidates.
**A or B licenses its sentence only with a challenge.** That is policy. Without a challenge, Part 1's finding still
stands alone, and each candidate's PV verdict is reported descriptively.

<!-- absence-ok: outcome licensing table for a future result -->
| outcome | condition | licensed sentence (substance, not wording) | not licensed |
|---|---|---|---|
| **A** | challenge; K_A selected | "With the corrected <block>, at each of the three named sealed truths (two GENIE v3 tunes, and a hidden-variable response test with the 2D truth at nominal) under the declared toy law, the fluctuation block's mean ratio <F̃ ± h> and every band read 'covers', and the total's guarded upper bound is <M + h> ≤ 1.25 (and per band), with no joint or mode under-flag." | a model-class claim; coverage at the data; that the total is tight |
| **B** | challenge; K_B selected | "At each of the three named sealed truths (two GENIE v3 tunes, and a hidden-variable response test with the 2D truth at nominal) under the declared toy law: the fluctuation block, measured on nominal and alternative-truth ensembles, has mean ratio <F̃ ± h> and every band reads 'covers'; with a fitted bias allowance from nominal and the three named PV2D deformations, reported separately, the total's guarded upper bound is <M + h> ≤ 1.25 (and per band), with no joint or mode under-flag. The held-out biases against the allowance: Q_u = <value ± SE>, outside-span fraction <value ± SE>." The factors f̂_R and C_b's rank and trace are printed with it. | coverage of any model family; "covers" for the total beyond the printed bound; a cause of the bias; that the allowance bounds a model class |
| **none, with a challenge** | challenge; no candidate VALIDATED | Nothing new. "Coverage remains unvalidated" stands, with P1's readings and every candidate's verdict as description. | any covariance change |
| **descriptive only** | no deficit shown, or unchallenged | Part 2's sentence, if any, and each candidate's verdict as description. A VALIDATED candidate is reported as such, but licenses no A or B sentence. | any covariance change; an A or B sentence |
| **none, PV ungraded** | ungraded | Part 1's finding, and P1's readings as description. | any statement about the sealed truths |

- **In-sample disclosure.** An A sentence states its corrected block. A B sentence states that C_b was fitted from
  nominal and the three named deformations (not G18 or AR23), and that the factors f̂_R came from N4 and A1p. Both name
  the three sealed truths and their overlaps (§4.3), say that u = 2 tests hidden-variable dependence through the
  response with its 2D truth at nominal (so C_b is not what it tests), and say that the covariance is the reported one
  carried in relative form (§2).
- **Rev 12's descriptive readings** (§6.6) may be printed beside any outcome, labelled descriptive. They license no
  sentence of their own.
- **Coexistence.** Part 1's finding and Part 3's outcome are reported together.
- **INFLATED** is reported as "the fluctuation block is wider than the held-out scatter by <F̃, bands>".
- **UNRESOLVED** is explained as sampling ambiguity only when a band or the total is unresolved across labels. Resolving
  it needs a newly authorized test, with an amendment and a price, never a re-read of the same toys under a changed
  rule.

## 8. Code, tests and audit before any compute

- **Reused unchanged where possible:** re2_driver.py `--data-file`, cov2d_writer, `cov2d.draw` (with r ≡ 1 for N4),
  S1's three-stream bootstrap code (for sim, and with `--bootstrap-streams data` for N5's replicas), F1's pipeline (PG),
  and `cov2d.draw`'s composition law for the toys.
- **New code:**
  - the N-cell and A1 toy writers, with a fixed-response mode and the 2D-map truth deformation;
  - the N3 seed arm;
  - the N5 half split;
  - the §2 carry;
  - the §3.3 ST1 readings;
  - the §5 builders and the residual stop;
  - the §6 readout, summary-only, with §2's analytic guards and §6.2's Gaussian reference law and its controls;
  - the descriptive stress runs, as a separate job with no seal access (§3.4);
  - PG's probe (with the novelty test), capture wrapper, authenticated encryption, seal checker and content scans;
  - PV's exclusive-compute-node writer (§3.4) with encrypted graded truths;
  - the director's wrapper, with ST4's consumption record, manifest verification before decrypt, and the synthetic-seal
    end-to-end test;
  - the ST3/ST6 reservation ledger;
  - ST1's reproducing-test harness for the named exception.
- **Each needs** unit tests, a line trace of every new line, hand mutants (all killed), a codex-school2 and an agy read (`DECISION-20261123-joseph-covfix-ki85-size-reader.md`), the
  director's binding, and per-connect fences.
- **A0-type controls in every readout:**
  - the readout reproduces COV2D's committed mean χ² at G18 and AR23 from E_<T>.npz against C_T, to the κ-scaled
    tolerance max(1e-9, 10 κ₂ ε), with κ₂ on the actual non-null grading subspace and ε = float64 epsilon. The
    tolerance's origin is COV2D addendum A5; REGRADE-AMENDMENT-1 is its retained-subspace variant;
  - numpy against scipy `evr` mode agreement, as in T2A.

## 9. Open items, for the director, and for Joseph where marked

1. **KI 85: decided.** Joseph superseded both of KI 85's sentences for COVFIX (`DECISION-20261123-joseph-covfix-ki85-size-reader.md`).
   - N5 is bound and runs unconditionally.
   - Outcome A may change the 2D covariance. Any change enters the journal paper or a later Zenodo version, not the
     first release. Adoption and wording remain Joseph's.
   - When N5 is bound, KI 85's row in `KNOWN_ISSUES.md` is updated to point to that decision. Until then the row is
     left unchanged.
2. **Size: decided.** Full, as designed (`DECISION-20261123-joseph-covfix-ki85-size-reader.md`, Joseph's governing re-confirmation): two sealed tunes, full P1 toy
   counts, and N5 always, at an expected no-firing price of 410.55–411.22 node-h. Joseph later raised the ceiling,
   first to 411.22 for the synthetic test, then to "about 540" for PX headroom, and confirmed the exact 541.50 (§3).
   Rev 12 (DRAFT) adds a third sealed truth (468.74–469.41 node-h) and raises the ceiling to 600.00. ST6 enforces the ceiling. That is above half the balance, and Joseph approved it. Each phase is still capped from
   sacct. The second reader is
   codex-school2, alongside agy, by the same decision.
3. **Outcome A's reach** (§7, Part 1). Within the ceiling it is reachable for every single-block firing, including
   `universe` with laterals rebuilt (541.37 at rev 11.4; 599.56 at rev 12, under 600.00), and for every W1 combination. Only a W1 exception followed by a `universe`
   firing is unfunded, by the sole-exception rule.
4. **Binding prerequisites:**
   - a committed iris receipt showing at least the pinned ceiling remaining (541.50 at rev 11.4; 600.00 for rev 12), or the
     binding goes back to Joseph;
   - the fresh PG session named;
   - the director's passphrase generated, with the director's piping wrapper, and never shown to cov2d.
5. **The bars:**
   - the fluctuation affirmative and two-sided (F̃ and every band "covers");
   - the total affirmative (M + h ≤ 1.25);
   - no under-flag;
   - §6.2's sampled-covariance check at 0.05;
   - the residual rule at 0.1 on modes with λ ≥ 1e-6·λ₁.
   These are policy choices, open to challenge.
6. **Truth-dependent spread.** If A1p's band ratios differ strongly between truths, pooling makes V_F over-cover at some
   truths and under-cover at others. §5.3's two-sided fluctuation bar will then refuse K_B, and "none" follows. That is
   intended.
7. **The carry.** COVFIX tests the reported covariance carried in relative form, not remade at each truth. P0 measures
   the difference at G18 and AR23. If the director wants the remade object instead, that is 486 unfolds per truth (about
   92 node-h each), and it changes the price.
8. **Rev 12's open items:**
   - **for Joseph:** u = 2's role, deciding (as drafted) or descriptive (the change log's alternative); and the
     DECISION's text superseding §3.3's clause for rev 12's changes;
   - **for the director:**
     - the go for a login-node fetch, by sha, of the four 5D predictions the calibration of [a_lo, a_hi] reads (§4.2):
       GIVEN 2026-11-24; the values are committed before any draw;
     - the u2-draw role's node-h: RULED 2026-11-24, priced at about 1.0 in PV's expected price, re-measured in the
       synthetic rehearsal, with the ceiling at 600.00;
       <!-- absence-ok: price of a role this draft declares and has not yet written -->
   - the receipt: binding at 600.00 is satisfied by PR #1276 (630.4 node-h at 06:55Z); the per-phase check then applies
     before each paid phase.

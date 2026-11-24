# Ben's (b): an inventory, a draft rule with blanks, and costs (2026-11-24, tier3-design, for the director)

**What this is.** An inventory and a draft only. **No rule is applied, nothing is computed, and nothing is declared.**
No data, no sealed product and no COVFIX §5–§7 PV output was opened; no note wording is proposed. The document goes to
the director first, then to Joseph. Every choice in §2 is **OPEN** for Joseph and Ben.
<!-- absence-ok: the document's own scope (what this draft does and does not do), not a claim that a result is absent -->

**Ben's request (b), as the director relayed it (2026-11-24):** report only bins whose method bias is below the MC–MC
generator differences. The rule is declared from simulation only, before it is applied, and is disclosed as post-data.

**Snapshot and method.**
- Repository snapshot: main `380684d95` for every path, commit and sha256 below, unless another is given. Commits come
  from `git log -1 --format=%h -- PATH`, and sha256 from the committed bytes. A read-only codex-school sweep
  (`codex-school-sweep.md`, beside this file) found the candidates. I spot-checked its paths, shas and the cited lines
  I rely on, and they matched.
- **UNVERIFIED** marks an availability (usually of a scratch file on pscratch) that is pinned in a committed record but
  not checked.

**The candidate cell sets** (the director's list; the variables are not yet chosen):
- **S3:** (pT, p∥, E_avail), with q3 as an optional fourth axis;
- **S4:** (pT, p∥, E_avail, q3), with W derived;
- **S5:** the note's 16 illustrative 5D cells R00–R15. Their map is `nd-unfolding/pv-ladder/readouts/h2_definition.json`
  (`5c440914d`, sha256 `b6790761…`).

The existing 2D (pT, p∥) products appear in §1.4 for context. COV2D, IBUB and PV are 2D.

## 0. Points the director should see first

1. **COVFIX declares two sealed validation truths, not three.** They are u = 0, 1: `G21_11b_00_000` and
   `G18_02b_02_11b` (fallback `G18_02a_02_11b`), with 300 toys plus one central unfold per truth
   (`COVFIX-DECLARATION.md:724–728`, `:790–799`; declaration sha256 `464ce635…`). The brief's "u = 0, 1, 2", and its
   ~26 GPU node-h, matches three truths:
   - with three truths: (3 × 300 + 3) × 0.028559 = **25.8 GPU node-h**;
   - with the declared two: (2 × 300 + 2) × 0.028559 = **17.2 GPU node-h**.
   The unit is the measured 5D unit, 0.028559 GPU node-h per unfold (`state/gpu-timing-20261023/REPORT.md:21–23`).
   - **Per the director (2026-11-24):** a DRAFT rev 12 on branch `cov2d/covfix-rev12-20261124` (head `13344558`), not
     yet approved by Joseph, adds a third sealed truth, u = 2, which is a sealed correlation-deformation reweighting.
     So the figure is **17.2 GPU node-h at u = 0, 1 (rev 11.4 as bound), and 25.8 if rev 12 is approved.**
   - **The sealed set itself is still open.** Slot 1's tune, G21_11b, is absent from CVMFS: PR #1281, "GENIE spline
     listing on CVMFS", merged at `9c657843`. Its replacement is pending Joseph's choice.
2. **A held-out clause at COVFIX's seals conflicts with COVFIX as bound.** COVFIX is bound at M_C1 `90b29087`
   (`COVFIX-BINDING-1.md:1–9`).
   - Its validation "is spent once", with consumption keyed by seal digest **and role**. The roles are the PV writer
     and the PV readout (`COVFIX-DECLARATION.md:678–682`).
   - PV's readout "writes one JSON of summary statistics; per-toy residuals and z arrays stay inside the process"
     (`:691`).
   - §5–§7 change only by ST1's named exception or by an executability fix (`:692–694`; `COVFIX-BINDING-1.md:6–9`).
   - "A later construction needs new sealed truths, and the catalog may not supply a third distinct family" (`:695`).
   - A per-cell coverage readout of 3D, 4D or 5D unfolds of PV's pseudo-data is a new construction and a new role.
     Under the binding as written it is not available. **Options (the choice stays OPEN for Joseph and Ben):**
     - **(i), the director's recommended option (2026-11-24).** Fold a "(b) readout" provision into rev 12 while it is
       still an unbound draft, before ST4's first spend. The provision would cover:
       - the 16-cell 5D unfolds of PV's pseudo-data, which are not secret and can run on GPU nodes;
       - grading the 16 cells against the sealed truths inside the director's readout, as an added role;
       - (b)'s per-cell test and threshold, frozen in that amendment.
     - (ii) new sealed truths through a fresh PG. The director judges this likely impossible: the catalog has no
       further families on CVMFS (`:695`; #1281).
     - (iii) validation only at truths already read (F1's G18 and AR23). These are not held out.
   - **Technically**, PV's pseudo-data are 5D-capable: each event is reweighted by u's bridged ratio on the 5D FINE grid
     (`:710–713`). So a 3D, 4D or 16-cell unfold of the same toys is possible, if the custody question is settled.
3. **The closest committed precedents for such a rule** are V-PRIOR and V-HALF, both diagnostic, on R00–R15:
   - **V-PRIOR:** the RMS truth-relative bias against the RMS generator departure from the Tune v1 prior, with
     S_b/S_g < 0.5 under four noise treatments (`2d-closeout/valid-region-20261107/DECLARATION.md:199–265`);
   - **V-HALF:** |b_{c,t}| ≤ 0.5 |d_{c,t}|, prior-relative, applied where |d| ≥ 0.01
     (`DECISION-20261109-joseph-bias-half-rule.md:30–36`).
   A (b) rule could reuse their definitions. Whether it does is open (§2).
4. **IBU at the held-out tunes exists in 2D only, and only once IBUB runs.** IBUB is declared on COV2D's 600 toys on
   E_R's 14 × 16 grid (`IBUB-DECLARATION.md:42–67`); it has no GO yet. No committed IBU product gives held-out-tune
   bias on S3, S4 or S5.

## 1. What exists, per cell set

### 1.1 S5: the 16 cells R00–R15

**Method bias, OmniFold:**

| Product | What it gives | Truths | Path | Commit | sha256 | Exists? | To get more |
|---|---|---|---|---|---|---|---|
| F1 | Per-cell b = X̂/X − 1 (ensemble mean of 20 Poisson pseudo-experiments) and the noise-free closure (`FD-F1-REPORT.md:11–18`, `:30–43`) | the held-out ("spent") GENIE v3 tunes G18_10a_02_11b and AR23_20i_00_000 | `measurement-paper/5d-community-20261024/fd/readout/fd_f1_readout.json` | `eeff25b58` | `cbe411a9…` | **yes** | per-experiment table on pscratch (`FD-F1-REPORT.md:15–18`), UNVERIFIED |
| F0b | Per-truth cell bias X̂/X − 1 and the noise of its mean (`FD-F0-REPORT.md:187–205`) | nominal; W1–W3; q3; Stage 0c GiBUU; NuWro closure; A7 Tune v1, CV, MEC, NuWro, GiBUU | `…/fd/with-cpl/readout/fd_f0b_readout.json` | `32d3f6e36` | `5f542830…` | **yes**, means | per-experiment residuals on pscratch (pinned `7384c651…`), UNVERIFIED |
| FD-PRR route 1 | Cell vectors b and d (prior-relative) and r (truth-relative) (`nd-unfolding/prior_retention/prr_read.py:276–285`) | F0b's 12 graded truths; primary split 991000; four extra splits for the A7 GiBUU arms and the nominal prior | `…/fd/receipts-prr/read/cluster/readout.json` | `3163dfba1` | `9238f22b…` | **yes** | — |
| T3 | Per-iteration summaries. The cell vectors are extractable from pscratch arrays (`nd-unfolding/tier3/t3p_read.py:232–248`) | six arms at A7 GiBUU and the q3 tilt; four extra GiBUU splits | `…/fd/tier3-20261110/run-20261121/cluster/read/readout.json` | `5d610d7d1` | `b0362c38…` | summaries yes; vectors UNVERIFIED | login-node extraction, 0 node-h, if the pscratch arrays survive |

**Method bias, IBU:**

| Product | What it gives | Truths | Path | Commit | sha256 | Exists? | To get more |
|---|---|---|---|---|---|---|---|
| FD-PRR route 2 | IBU estimates at K = 1, 2, 3, 4, 5, 10, 20, 50, 200 on H2 truth bins, 20 noise-free experiments (`FD-PRR-DECLARATION.md:188–200`) | the same 12 truths; extra splits | `…/fd/receipts-prr/ibu/attempt3/cluster/log-ibu/SHA256SUMS` | `487192f2b` | `49782595…` | summaries committed; `route2.npz` on pscratch (pinned `759be4ab…`), UNVERIFIED | login extraction at 0 node-h if retained; otherwise rerun (0.1517 CPU node-h, `…/attempt3/README.md:9–11`) |
| IBU at G18/AR23 on R00–R15 | — | — | — | — | — | **no** | IBU on F1's pseudo-data, if those survive: about 0.15–0.3 CPU node-h at FD-PRR's IBU job size. The survival is UNVERIFIED. |

**MC–MC generator differences (truth level):**

| Product | What it gives | Generators | Path | Commit | sha256 | Exists? | To get more |
|---|---|---|---|---|---|---|---|
| FD-G (CH) | Per-cell truth-level vectors g in the analysis definitions; any pairwise difference is arithmetic (`valid-region-20261107/DECLARATION.md:118–122`, `:217–229`) | GENIE CV, GENIE+MEC, NuWro CH, GiBUU CH (on the eight p∥ < 4.5 cells), Tune v1 | `…/fd/gencmp-e/rerun1/chain/chdefs/with/readout/fd_g_readout.json` | `e7feb3317` | `a19009e0…` | **yes** | laptop, 0 node-h |
| GENCMP (carbon) | Carbon truth vectors, as the note's main comparison uses them (`2d-closeout/stageF/methods/note-genresid-20261120/README.md:26–42`) | NuWro and GiBUU carbon | `…/fd/gencmp/readout/defs.json` | `e87dbda54` | `544f4f43…` | **yes** | laptop, 0 node-h |

### 1.2 S4: (pT, p∥, E_avail, q3), with W derived

- **OmniFold method bias: no native product.**
  - RE-1's 4D table (`2d-closeout/stageF/methods/re1/run2/readouts/movement_4d.tsv`, `2af68accc`, `214278a6…`)
    compares background treatments on data. It is **not a bias**.
  - The historical 4D closure gives only a q3 marginal under one injected shape.
  - Two routes: (a) native 4D fake-data unfolds at chosen truths; (b) a projection of 5D OmniFold outputs, which needs
    fine-level 5D outputs at those truths (UNVERIFIED). A projection estimates the 5D estimator's bias, not a 4D
    estimator's.
- **IBU method bias: no product.** It would need an S4 response binned on the chosen truth grid, and IBU on matched
  pseudo-data.
- **MC–MC generator differences: the inputs exist.** MP2's harmonized particle-level 5D predictions:
  - GENIE CV `…/phase1/mp2/s2-receipts/harm_a/harmonized_genie_cv.npz` (`dac42a094`, `62a49f4f…`);
  - GENIE+MEC `harmonized_genie_mec.npz` (`0c7b11a7…`);
  - NuWro CH `harmonized_nuwro_ch.npz` (`4cd94b0d…`);
  - GiBUU CH `harm_b/harmonized_gibuu_ch.npz` (`9dd761dd…`; the earlier harmonization; a later re-harmonization has its
    own receipt).

  These integrate to any 4D grid whose edges are fine edges, at 0 node-h (`…/mp2/S2-IMPLEMENTATION.md:122–142`). MnvTune
  v1's fine input is pinned in `FD-G-DECLARATION.md:67–76`, with local availability UNVERIFIED. **A derived W** needs a
  fixed truth-W definition and bin map. If W must be computed per event, that is a login-node extraction, as for the q0
  study. The q0 study shows that reco W is an exact function of (pT, p∥, reco q3) (`M4-W-RECORD.md:104–110`).

### 1.3 S3: (pT, p∥, E_avail), and +q3

- **OmniFold and IBU method bias:** as for S4, there is no native product. The historical 3D closure gives a
  truth-relative E_avail marginal and joint-bin scatter under one injected E_avail bump
  (`3d-unfolding/3D_OMNIFOLD_STATUS.md:67–69`, `:119–123`), not held-out-tune bias.
- **MC–MC generator differences:**
  - MP2's harmonized inputs (above) project to 3D at 0 node-h.
  - Stage 7's 3D truth predictions (GENIE CV, GENIE+MEC, NuWro, GiBUU) have a receipt at
    `state/s5p/stage7/generator-context/generator-context-receipt.json` (`f5ed4704c`, `106ecfcb…`). The histogram bytes
    are UNVERIFIED locally.
  - A shape-only NuWro/GENIE CV ratio on the 3D analysis grid: `state/s5e/w3-nuwro-over-genie-pt-pz-eavail.json`
    (`0998742b2`, `3455daf3…`).

### 1.4 Context: the existing 2D (pT, p∥)

| Product | What it gives | Truths | Path | Commit | sha256 | Status |
|---|---|---|---|---|---|---|
| COV2D / T2A | 300 signed unfolded-minus-truth error vectors per tune, 205 cells | G18, AR23 | `…/fd/tier2-20261110/t2a/{G18/E_G18,AR23/E_AR23}.npz` | `9140d8a4e` | `846b9d85…`, `ccda9c50…` | exists |
| IBUKT A2 | Truth-relative residuals, OmniFold K = 5 and IBU K = 5/10, five draws | nominal, GENIE+MEC, NuWro, bump, tilt, within-bin tilts | `2d-closeout/ibukt-a2/readout.json` | `ed6ee7d01` | `dfae50f5…` | exists |
| IBUB | IBU K = 5/10 on COV2D's 600 toys | G18, AR23 | `…/IBUB-DECLARATION.md` | `734a7e540` | `3aaf07f1…` | declared; about 9.2 CPU node-h (`:313–327`); no GO |
| PV2D projections | Truth projections g and gated shape ratios | GENIE+MEC, NuWro, GiBUU against GENIE 2.12 CV | `2d-unfolding/pv2d/ratios/projections.json` | `8315aa1d8` | `8241807f…` | exists |

## 2. A draft rule, with blanks (every item OPEN for Joseph and Ben)

*Written as text, to be declared later from simulation only, before it is applied, and disclosed as post-data.*

**(b)-1. The population.** For the cell set ⟨S3 / S4 / S5⟩:
- the bias is evaluated at the truths ⟨T_bias: e.g. F1's held-out G18 and AR23; and/or F0b's graded truths; and/or
  FD-PRR's 12⟩;
- in the units ⟨truth-relative, b = X̂/X − 1 / prior-relative, FD-PRR's b⟩;
- the generator differences are taken over ⟨G: GENIE CV, GENIE+MEC, NuWro, GiBUU (its domain ⟨p∥ < 4.5 only / all
  cells⟩), Tune v1⟩;
- at the level ⟨truth, particle-level CH-harmonized / carbon⟩.

**(b)-2. The comparison statistic, per cell c.** Choose one:
- ⟨A: max over t ∈ T_bias of |b_{c,t}|, against the generator spread S_g,c = ⟨max pairwise |g_i/g_j − 1| / RMS of
  (g_G/g_ref − 1) over G / half the range over G⟩⟩;
- ⟨B: a band, the cell reportable while |b_{c,t}| sits inside ⟨the generators' envelope / a fixed fraction of it⟩⟩;
- ⟨C: V-PRIOR's or V-HALF's construction, reused as written⟩.

**(b)-3. The threshold.** The cell is reportable if ⟨statistic⟩ ≤ κ · S_g,c, with κ = ⟨__⟩. The precedents are κ = 0.5
(V-PRIOR's S_b/S_g < 0.5; V-HALF's |b| ≤ 0.5|d|). The cut where S_g,c is itself small is ⟨__: e.g. V-HALF's
|d| ≥ 0.01 floor, or "not assessable" reported as such⟩.

**(b)-4. How the bias uncertainty enters.** Use ⟨the point estimate / the upper bound |b| + z·σ_b, with z = ⟨__⟩⟩.
- σ_b comes from ⟨F0b's noise of the mean / the spread across FD-PRR's or T3's extra splits / F1's 20-experiment
  ensemble⟩.
- MC-statistical noise enters via ⟨splits⟩.
- A cell whose decision flips within σ_b is ⟨not reportable / flagged⟩.

**(b)-5. Cells where the methods disagree** (OmniFold against IBU, where both exist at the same truths). Choose one:
- ⟨the cell must pass under both⟩;
- ⟨it must pass under the reported method only, with the disagreement printed⟩;
- ⟨a disagreement beyond the two biases' combined uncertainty makes the cell not reportable⟩.

**(b)-6. The held-out validation clause, frozen before PV.**
- (b)-1 to (b)-5 and the resulting reportable set are frozen and committed before any PV seal is spent.
- At each sealed truth u ∈ ⟨0, 1 (rev 11.4 as bound) / 0, 1, 2 (if draft rev 12 is approved)⟩ (§0.1), for each
  reportable cell, the per-cell coverage is
  ⟨the fraction of PV toys with |z_{c}| ≤ 1 against the carried covariance / the interval covers the truth⟩.
- The cell's coverage must be ≥ ⟨__: e.g. 0.6827 minus a declared binomial tolerance at N = 300⟩.
- If it fails: ⟨the cell is dropped / the rule is declared failed and nothing is quoted on it / it is reported with a
  label⟩.
- **Blocked as COVFIX is bound (§0.2).** This clause needs one of §0.2's options first. The director recommends (i),
  folding it into draft rev 12 before ST4's first spend; the choice is OPEN.

**(b)-7. Disclosure.** The rule, its date and its simulation-only basis are recorded before it is applied, and the
fact that it was fixed after data is disclosed. Where it is disclosed is Joseph's call; no wording is proposed here.

## 3. Cost and timeline per cell set (estimates; each from a cited unit)

| | Inventory and freeze (no rule applied) | Bias at held-out tunes | IBU beside OmniFold | Generator differences | Held-out PV clause |
|---|---|---|---|---|---|
| **S5** | days; every OmniFold input exists (§1.1) | **exists** (F1) | 0.15–0.3 CPU node-h, if F1's pseudo-data survive (UNVERIFIED); otherwise regenerate at F1's cost (1.3275 CPU node-h total, of which the 42-unfold batch was 0.609; `FD-F1-REPORT.md:128–143`) | exists, 0 node-h | 16-cell 5D unfolds of PV's toys: **17.2 GPU node-h** at u = 0, 1 (rev 11.4), 25.8 if rev 12 adds u = 2; needs §0.2's option (i), as the director recommends |
| **S4** | days, plus a fixed truth-W definition | new native 4D fake-data unfolds: about 42 unfolds (F1's 2 × (20 + 1)) at roughly 0.04 CPU node-h each. That is RE-1's mixed 3D/4D/5D batch throughput of 0.0423 (`RE1-REPORT-2.md:356–368`) and is only a rough unit; a pilot would re-measure. So about 2 CPU node-h, plus input preparation (0.12) | S4 response plus IBU: about 0.2–0.5 CPU node-h | 0 node-h if the cells align with fine edges; a login extraction if W is derived per event | 4D unfolds of PV's toys: about 602 × 0.04 ≈ 25 CPU node-h (rough unit); blocked by §0.2 |
| **S3** | days | as S4, in 3D: about 2 CPU node-h | as S4 | 0 node-h (projection) | as S4, in 3D: about 25 CPU node-h (rough); blocked by §0.2 |

**The order of work**, whichever set is chosen:
1. Joseph and Ben pick the cell set and fill §2's blanks.
2. A declaration fixes them, from simulation only. A binding follows for any run.
3. The missing products are made (§3's middle columns).
4. The rule is applied, once.
5. The held-out clause follows COVFIX's PV schedule and the §0.2 decision.

S5 can be tabulated soonest, because its OmniFold bias at the held-out tunes and its generator vectors already exist.
S3 and S4 each need a small new fake-data production first.
<!-- absence-ok: an inventory; "no product" rows state what the snapshot's committed records hold for each cell set, from the cited search (codex-school-sweep.md) and my checks -->

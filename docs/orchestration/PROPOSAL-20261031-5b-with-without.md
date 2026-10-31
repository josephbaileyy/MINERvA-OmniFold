# PROPOSAL: how the paper and note present the 16-cell result with and without the run-period block (2026-10-31)

**By** the paper rewrite lane, for the director, for Joseph. This is a proposal, not text. Nothing in the paper, the
note or any product is changed.

**Status** (the director, 2026-10-31):
- **Accepted:** item 0 (#542 decided the headline matrix; the interim "Now" sentence never printed and is moot), item 3's
  generated listed-truth macros with their two-way assert, to be built before any text, and, for raters, no P2 and one
  P1 ×3 non-regression only (mean and min ≥ 3.0).
- **To Joseph:** J1 and J2 (§4). The director puts them to him.
- **Held:** all paper and note text, until Joseph answers J1 and J2.

**Sources** (origin/main `0f7fe4ee3`):
- [`DECISION-20261030-joseph-4b-not-now-5b-audit-then-add.md`](DECISION-20261030-joseph-4b-not-now-5b-audit-then-add.md)
  (#542), item 2;
- [`FD-CT-5B-ADDITION-BINDING.md`](state/measurement-paper/5d-community-20261024/FD-CT-5B-ADDITION-BINDING.md), ruling 2;
- [`FD-CT-5B-ADDITION-REPORT.md`](state/measurement-paper/5d-community-20261024/FD-CT-5B-ADDITION-REPORT.md) and
  [`fd_cpl_table.json`](state/measurement-paper/5d-community-20261024/fd/with-cpl/table/fd_cpl_table.json) (`eb786bcf…`). Every number below is from
  that table, from the with and without F0b and F1 readouts, or computed from the table's `sigma_over_f` by me (marked
  "computed");
- the paper `paper_body.tex` and the note's `sec_fived16.tex` and `sec_systematics.tex`, at the same commit.

## 0. What is already decided

- **The headline matrix is the with-block one, C_total + C_resp + C_PL,5D.** #542 item 2: the block is "audited, then added
  to the 16-cell reported covariance", and "The revised covariance flows through every downstream product: the result
  table, the generator χ², and the F1 and flux-bootstrap readouts where they use the matrix". So this is not proposed but read from the decision.
- **The 2D precedent agrees.** The paper's 2D covariance includes its run-period block (paper §IV C `sec:uq2d`, "run period
  (three period groups)"). The note gives the block's effect separately, in `tab:pl-added` (the increase in σ and the
  block's share).
- **1B keeps `b79556f0…`, the without-block matrix** (binding ruling 3). When 1B reports, the paper names that matrix.
- **The decision's interim "Now" sentence never printed.** That sentence said the reported uncertainties "do not yet
  include a dedicated run-period component". `git grep` on main finds no such sentence in `docs/analysis-note/*.tex`.
  It is now moot. I propose the record says that, rather than printing it. The director accepted this, and this
  record says it.
<!-- absence-ok: `git grep -n -i -E "dedicated run|run-period component" origin/main -- docs/analysis-note/*.tex` printed nothing at 0f7fe4ee3, and nothing again at d1c7b80d1 -->

**Open:** where the without-block numbers print, the wording, two items for Joseph (§4), and how the rule is enforced
(§3).

## 1. What the block changes (from the table)

| quantity | without | with | change |
|---|---:|---:|---|
| median σ/f per cell (computed) | 7.29 % (the printed `sigmed-C_total_resp`) | 7.86 % | ×1.048 at the median |
| largest σ widening | — | — | ×1.141, R04 (4.20 → 4.80 %) |
| the block alone, per cell (computed) | — | median 2.34 %, max 3.16 % (R05) | its share of the with-block variance: median 9.0 %, max 23.2 % |
| χ², GENIE CV (16) | 109.35 | 105.42 | −3.6 % |
| χ², GENIE + MEC (16) | 272.12 | 223.55 | −17.8 % |
| χ², NuWro (16) | 188.03 | 130.68 | −30.5 % |
| χ², Tune v1 (16) | 329.72 | 262.06 | −20.5 % |
| χ², GiBUU (8) | 58.46 | 45.25 | −22.6 % |
| shape-only χ², NuWro (15) | 188.00 | 113.73 | −39.5 %, the largest fall |
| abstract range, the three external generators, as integers | 109–272 | 105–224 | — |
| F0b listed truths | q3; GiBUU E_avail shape (R06); GiBUU hybrid (R02, R06, R07) | q3; GiBUU hybrid (R02, R06) | **the GiBUU E_avail shape leaves the list** (R06 z = 2.010 → 1.762) |
| F1, G18 / AR23 | 11.84 / 16.86 | 9.26 / 14.06 | both pass either way |

**What follows from this:**
- **The χ² move far more than the uncertainties do.** The σ widens about 5 % at the median, while the χ² fall by up to
  40 %. The block has rank two and lies along the directions the predictions' residuals take.
- **The order of the predictions is unchanged:** GENIE CV < NuWro < GENIE + MEC < Tune v1, with and without the block.
- **Every χ² stays far beyond its ndf.**
- **One fake-data verdict changes.** That is the one place where the block changes a claim (§4, J1).

## 2. Where each number goes

**The principle:** the paper prints the with-block matrix everywhere it says "reported covariance", plus the without
numbers wherever the block changes a printed conclusion or moves a headline number materially. The note prints both
for every product #542 names: the result, the generator χ², the fake-data tests, F1 and the flux bootstrap. The
diagnostics print the with-block numbers only, with their captions saying so.

### Paper

| place | with | without |
|---|---|---|
| §IV A `sec:cov16`, the reported-covariance paragraph | names C_PL, and adds a short run-period paragraph (§2.1) | one clause on the existing "and X % without C_resp" pattern: "The median … is 7.86 %, 7.29 % without C_PL, and 6.74 % without C_PL or C_resp" |
| Table III `tab:result16` | the one σ column (the director's Q5 stands), with the caption naming C_total + C_resp + C_PL | per cell in the note (below) |
| **Table IV `tab:gen16`** | the reported χ² | **recommended: one more column pair, "without C_PL", χ² and shape-only χ²** (ndf unchanged, so not repeated). This needs Joseph (§4, J2) |
| Table II `tab:fd16` | its first block becomes the with-block values. The second block (C_total alone) is unchanged, because no C_total-only readout depends on the block | in the note's table |
| the listed-truths sentence after Table II | the with list | **states the without list in the same sentence** (§4, J1) |
| the F1 paragraph | with-block χ² and p | in the note |
| the sensitivity and flux-bootstrap sentences | with-block values (G-SENS2 and the flux bootstrap, with arm) | in the note |
| Fig. `fig:ratio16` | install `fd/with-cpl/figures/fd_g_fig_ratio.pdf` (`b57cbb2c…`), with the caption naming the matrix | — |

### Note (`sec_fived16.tex`)

| table | change |
|---|---|
| `tab:fived16-cells` | add the columns "C_PL,5D alone" and "reported C_total + C_resp + C_PL,5D". The existing C_total + C_resp column then reads as "without the block", so the per-cell with and without sit side by side |
| `tab:fived16-groups` | add a C_PL,5D column |
| `tab:fived16-gen` | it already has a "without C_resp" pair, so add a "without C_PL,5D" pair |
| `tab:fived16-fd` | three blocks: reported (with), without C_PL,5D, and C_total alone |
| `tab:fived16-corr` | the reported (with) matrix. The without correlation is the committed data product's (`838f1661…`), cited by name |
| `tab:fived16-sens`, `fig:fived16-modes`, `tab:fived16-diag`, `tab:fived16-pulls` | with-block only. Each caption names the matrix, and the without versions are cited as the committed readouts by digest |
| the F1 and flux-bootstrap text | both, in one sentence each |
| **new `sec:fived16-pl`** in `sec:fived16-cov` | the block's construction, the audit and its stop condition fixed in advance (`stop` = false), a with/without table in the form of `tab:pl-added` (the σ increase, median 4.8 % and max 14.1 % at R04; the share, median 9.0 % and max 23.2 %), the table label's caveats, and the sentence that the addition followed the data. The caveats are: three periods, so the 68 % interval on σ_true/σ_hat is [0.73, 2.56]; R00 and R08 are noise-dominated; rank 2, undebiased |

**Deposit.** `fd/with-cpl/deposit-candidate/` carries only the with matrix as `covariance.csv`. For the deposit to be
"with and without", it should also carry C_total + C_resp (or C_PL,5D) as a named second file. That is a builder
change and its own step. Not now.

### 2.1 Proposed paper wording (for the truth and register checks, not final)

> **Proposed paper wording, after the C_resp sentence of §IV A:**
>
> "The run-period block $C_{\mathrm{PL}}$ accounts for an inconsistency among the three run-period groups, whose
> unfolded results, each relative to its own simulation, differ by more than their resampling scatter. The cause is not
> known. As for the two-dimensional result, the block is built from the double ratios among the groups, with no
> reference period; it has rank two, and with three groups its size is poorly determined. It was added after these
> differences were seen, following an audit whose stopping criterion was fixed in advance. Because it is built from the
> observed differences, its size is not validated."
<!-- absence-ok: proposed wording, not a claim of this record; it restates the addition report's and the table label's NOT CITABLE FOR "a validated size for C_PL,5D: a block built from the observed differences contains them by construction" -->

**Sources for each fact:**
- "differ … beyond the bootstrap noise": #542 "What led to it", citing `FD-CT-5B-REPORT.md`;
- the double ratio and no reference: `FD-CT-5B-REPORT.md` (periods "against each other (not against ALL)",
  with exposure shares e_X); rank two: the audit report, A4 and A5. "Beyond the noise" is #542's reading. 5B itself
  declares no consistency threshold;
- "after … seen" and the audit: the addition report's lead and the table's `labels.decision`;
- "not validated": NOT CITABLE FOR.

The note carries the audit's clauses O, N and R, and the label's interval.

## 3. Enforcing it in code (before any text)

1. **`make_values_fived16.py`:**
   - the headline keys keep their names and re-pin to the with-cpl readouts by sha256 (`b55366b3` G, `5f542830` F0b,
     `5ccc89e5` F1, `bfd529ab` G-DIAG, `5c95c6d0` G-FOLLOWUP, `cff60b63` G-SENS2, `7d117515` flux bootstrap,
     `d6752d2c` data product);
   - the without values get a `-nopl` suffix, mirroring `-nocresp`, pinned to the committed readouts.
2. **The hazard a re-pin creates:**
   - The listed truths' names and cell lists are typed by hand in the paper (the sentence after Table II) and in the
     note, beside a `\fvval` z and p.
   - Re-pinning the keys silently would compile a false sentence: it would print "GiBUU E_avail shape (cell R06,
     z = 1.76)" as listed.
   - So **generate the list as macros** (`f0b-listed-names`, `f0b-listed-names-nopl`), and have the generator assert
     that every listed truth named in the prose equals the readout's `triggers.listed`. The assertion needs a two-way
     test.
3. **A probe in `check_table_macros.py`** for Table IV's new columns, if J2 is taken.
4. **The ledger, `check_held`, agy's "list every difference" read** and local CI, as for every truth fix.
5. **A rater pass.** The register rounds stopped, so I propose no P2 iteration on this text. I propose one P1 ×3
   non-regression only (mean and min ≥ 3.0), because the change is required content, not a register attempt. This is
   the director's call.

## 4. For Joseph

- **J1, a claim changes with the matrix.**
  - **The fact.** Under the without-block matrix, the reported uncertainty fails to cover the bias at two GiBUU-like
    truths. Under the with-block matrix it fails at one, the hybrid. The E_avail shape falls from z = 2.01 to 1.76 in
    R06, so it sat at the threshold.
  - **The risk.** The block was built from data, not from these truths. Printing only the with list would read as a
    validation gain, which the block cannot give (NOT CITABLE FOR a coverage or calibration statement).
  - **Proposed body.** "Under the reported covariance, the listed truths are the GiBUU hybrid truth (…; cells R02, R06)
    and the synthetic q3 tilt; without $C_{\mathrm{PL}}$ the GiBUU E_avail shape is also listed (R06, z = 2.01)."
  - **The abstract** (Joseph's wording) says "at GiBUU-like truths". Under the reported matrix that now names one
    truth. Proposed: "at a GiBUU-like truth or at a synthetic $q_3$ tilt". The note's abstract and executive summary
    match.
  - **The abstract's numbers** move through their macros (7.29 → 7.86 %; 109–272 → 105–224; GiBUU 58 → 45).
- **J2: Table IV's without columns.**
  - **Recommended:** add them. The block moves the paper's main comparison by up to 40 %, more than it moves any
    uncertainty, and it was added after the data. A reader who doubts it needs both sets of numbers on the page.
  - **What it costs:** an amended caption for Option B (#581, Joseph's caption). The two-block layout and the separate
    χ² and ndf columns stay.
  - **The alternative:** Table IV unchanged, with one sentence after it giving the falls (4–40 %, order unchanged) and
    pointing to the note's table.

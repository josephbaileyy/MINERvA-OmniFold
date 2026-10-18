# Stage F rebuilds R1–R4, phase 2: the deliverable text changes (record, frozen before implementation)

**Owner:** the paper-tighten lane, as director (Stage F), 2026-10-18. Follows phase 1 ([`REPORT.md`](REPORT.md),
merged `ae198cc1`) under Joseph's adoption of Q = S5 total + C_PL
([`DECISION-20261017`](../../../../DECISION-20261017-joseph-2d-adopt-s5-plus-playlist.md)).

**CITABLE FOR:** the rules phase 2 applies to the deliverable sources, and the director's rulings on the open questions
of the site inventory. **NOT CITABLE FOR:** any claim (J3/R5), disclosure wording (J4), KI-85 row text (J5), a built or
pushed PDF (B1–B5, J6), or any number not in a phase-1 receipt.

## 1. Scope

- **Sources:** `docs/analysis-note/` (the four builds of `build_all.sh`: note, paper, primer, PET note), its figures and
  `make_figures.sh`, and the build gates `check_sec4_receipts.py` / `check_dead_containment.py` with their tests.
- **The site map** is [`PHASE2-INVENTORY.md`](PHASE2-INVENTORY.md) (read-only inventory at `ae198cc1`, about 190 rows,
  committed with this record). Every row is either changed by its status rule (§2) or recorded as unchanged with a
  reason in the implementation report.
- **Out of scope:** records outside the deliverables (AGENTS.md, the 2D status file, the claim tables; K1–K4), the
  standalone `MINERvA-OmniFold-Analysis-Note` repository and any push (J6), committed PDFs (B1–B5), any new
  computation, and `publication/release/figs/make_figs.py` (pinned `9c4dbf24…` by `make_fig1_q.py`; its stale
  "VL170/VL172" docstring is left and recorded here).

## 2. Rules, by inventory status

| status | rule |
|---|---|
| **NUM** | Replace with the receipt value at the printed precision of the sentence; the macro or a LaTeX comment names the receipt (`rebuild/outputs/...` path and field). A number derived from two receipt fields is not printed (Q5). |
| **NR** | Not recomputed. In the body: remove the number, or keep it only where the sentence states the historical object it belongs to (e.g. "the superseded VL162 band", "the seed-scan floor in force when this test was graded"). Superseded construction material moves to `app_history` (Q6, Q7). |
| **FACT** | The sentence states a construction fact that is false of Q. Replace it with the minimal true statement of what Q is (blocks, seed, sweep, streams), from the receipts or the production DESIGN / s5.json, with no new evaluative, claim or caveat language; add `% J4 pending (DRAFT-disclosures Dn)` beside it. |
| **J** | Claim or disclosure wording. Leave the words unless they are false of Q (then FACT applies); add `% J3 pending` or `% J4 pending (Dn)`. Do not import DRAFT-disclosures text. |
| **FIG** | Install the phase-1 figure file (§4); captions describe what the producer draws (memory rule: a caption's only authority is its producer). |
| **TOOL** | §5. |

A factual qualifier that makes a sentence true (naming which band or block a number belongs to) is FACT, not J.

## 3. Rulings on the inventory's open questions (§5 there)

| Q | ruling |
|---|---|
| Q1 universe count | No rollup universe count is printed (no receipt field). State the receipted facts: the July sweep has 44 bands and 187 universes (`s5.json` check `july_44_bands_187_universes`); the rollup drops Rvp1pi (KI-92) and holds 43 bands plus the flat normalization (`universe_bands_43_plus_norm`). |
| Q2 error bars | Fix now. `sec_results.tex:5–7` must say what `fig:xsec` draws (`hXSec2D` bin errors, as the producers `plot_2d_threeway_fig13.py` / `plot_2d_cross_section.py` read them) and point to the uncertainty figures for Q; the implementer states the error's meaning only as far as the producer code shows it. |
| Q3 combined max pull | The sentence "no reported bin has \|pull\|>3" (combined form) is removed; the mean / RMS from `chi2_Q_std.txt` stay. The receipts do not give the maximum. |
| Q4 conditioning | Quote `budget_Q.ranks` with the threshold named (t = 1e-12 primary; 1e-10 where the text compares). The old 8.7e8 and "rank 140" go to history. |
| Q5 learner vs seed block | The "five times the seed block" comparison is removed (its operand, the ten-seed block, is retired); no derived 17× is printed. The learner-dependence sentence is J4 (D3). |
| Q6 seed scan | `§sec:seedscan`'s body text and `fig:seedscan` leave the systematics section; `app_history` gains a short labelled paragraph with the VL175-era values (10 seeds, 0.166%, 1.24×, n = 4 → 10), no figure. A closure or threshold that was graded against 0.166% keeps the number, stated as the floor in force when it was graded. The training-seed block of Q is c08 (`budget_Q.c08`, rank 4 over 5 seed triplets). |
| Q7 earlier bootstrap | The VL170 split-bootstrap numbers (1.07, 77/23, 0.95, 0.356, 0.108, 0.46, 76.7, 252, 50 → 300, 1A 1.46%) move to `app_history` as "the earlier (VL170) bootstrap". The body describes S1 with receipted numbers only (0.684%, √Tr ratio 0.428, ensemble error 4.1%, centring per `s5_copied`). |
| Q8 history clauses | Body "an earlier version quoted 6.87%" sentences stay as written (true) and get `% J4 pending`; `app_history`'s errata table gains the VL175 → Q rows (6.09 → 6.45, 3.65 → 3.75, 0.994/1.014/5.80 → 0.964/0.987/6.01, 4.23 → 4.75, 0.048/0.406 → 0.042/0.398), with the containment gate kept green. |
| Q9 Sec. IV gate | Fix now: `check_sec4_receipts.py` reads `.json.gz` (by suffix), its `\uqMedian` and statistical-block bindings point at `budget_Q.json.gz` (`Q.median_pct`, `stat.median_pct`), and its self-test and `test_check_sec4_receipts.py` gain a gzip case and the Q values (0.674 → 0.684). Reviewed with the rest. |
| Q10 logs | The phase-1 `.log` files are `*.log`-ignored and were never committed. Committed with this record by explicit path (`git add -f`): the ten listed in `SHA256SUMS.cfs` (`logs/` ×3, `eq/a{1,2}/f67_*.log` ×6, `runner.log`), each measured equal to its CFS digest on 2026-10-18, and the local `fig1/fig1_run.log` (Fig. 1 ran locally; no CFS entry). REPORT §1's link then resolves. |
| Q11 `make_figs.py` | Left (above). |
| Q12 flux | The direction sentence keeps `\fluxBand` against the published value; "4.99% without the constraint weights" leaves the body (VL-era, no S5 counterpart) for history. |
| Q13 records | K1–K4, not phase 2. |

**The log-normal χ² definition** (REPORT §5) is added as a definition beside `\chiCombinedLog` where it is first
quoted (`app_statmethods.tex` worked example): δ = ln E_U − ln p, C_ln = (Total + Q)/(p_i p_j). Stating a definition
is FACT; whether and how the paper discusses its definition dependence is J4.

## 4. Figures

| deliverable file | source (committed, phase 1) |
|---|---|
| `figures/paper_fig1_validation.pdf` | `rebuild/outputs/fig1/fig1_validation.pdf` `82665808…` |
| note Figs. 6/7 (`fig:uqbands` p_T and p_∥ files) | `rebuild/outputs/fig67/MEFHC_fig6_7_uncertainty_{pt,pz}.pdf` |
| `fig:bootstrap` (`uq_spread_2d`, `uq_corr_2d`) | `rebuild/outputs/stat/uq_{spread,corr}_2d.pdf`; caption: "std/mean" is σ/`E_U` |
| `fig:seedscan` | none (Q6) |

Each install is a byte copy checked against `SHA256SUMS.cfs`. Legend labels "Training seed" / "Run period" are
provisional (J4).

## 5. Tooling

- `make_figures.sh` lines 54 and 57 (VL170/VL172 recipe) are replaced by an explicit, digest-checked copy of the §4
  files from `rebuild/outputs/`, with a comment naming `rebuild/scripts/run_rebuild.sh` as the regeneration recipe,
  so a rerun cannot reinstall VL170 figures.
- `check_sec4_receipts.py` per Q9. `check_dead_containment.py` is not changed; new errata rows must pass it.

## 6. Acceptance

1. `build_all.sh` (all four targets) rc 0 in a scratch copy, no undefined references, both gates pass (self-tests and
   real runs); page counts reported.
2. A grep over the four builds' `\input` closures for the VL175 values at every precision in the inventory (§0
   there) finds each hit either changed, in `app_history`, or listed in the report with its status.
3. Every PHASE2-INVENTORY row has a disposition in the implementation report.
4. Independent review (fresh context, no producer-side authorship) of the diff against this record and the receipts,
   findings fixed before merge.
5. Pre-commit (13 checks), `generate_manifest.py --check --at-sha HEAD`, `verify_hash_bindings.py`.

**Same-model caveat:** director, implementer and reviewer are Claude Opus 5.5 on claude-school.

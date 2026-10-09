# Release-reproducibility and evidence-preservation audit of the PRD article (2026-10-08)

**CITABLE FOR:**
- whether RC4 reproduces its outputs from an empty directory, and how those outputs compare with the article
  sources at the baseline;
- for every numerical claim in the article: its canonical receipt, underlying artifact, independent check and
  preservation route, as this audit measured them;
- the gaps that would stop a reader or maintainer from reproducing or recovering a claim, with proposed fixes.

**NOT CITABLE FOR:**
- any physics number (the routed receipts remain the authority);
- a release, deposit, tag or submission;
- a change to any scientific decision, gate or claim wording;
- authorization to copy, move or delete any product.

This is a read-only audit on an isolated report branch, and it is not to be merged. It ran no cluster job and wrote
nothing to the cluster. It changed no scientific source or product, and it did not modify the RC4 package.

| | |
|---|---|
| baseline | `origin/main` **`fec438db5d6e313f110879a749381bb189b2a384`**, fetched 2026-10-08 ≈ 07:40Z; isolated worktree `../MINERvA-OmniFold-prd-audit-20261008` on branch `audit/prd-release-repro-20261008` |
| article sources | unchanged since `0e7d9b1b`; the last change is `bf4f1a29`; `git diff 0e7d9b1b fec438db -- docs/analysis-note publication` is empty |
| documents read first | `AGENTS.md`; `docs/publication/submission/PACKAGE-MANIFEST-20261006.md` §1b; `docs/publication/release/RC4-README.md`; `docs/publication/CLAIMS-20261005-claim-to-evidence.md`; `docs/publication/ARTICLE-READINESS-20261006.md`; `docs/publication/RELEASE-INVENTORY-20261005.md`; `VALIDATION_LEDGER.md` (the "Quote a number" route) |
| claim table | `CLAIM-TABLE-20261008.tsv` (this directory), 97 rows |
| campaign review | `docs/orchestration/CAMPAIGN-REVIEW-20260929.md` was **not** read before the audit work, contrary to `AGENTS.md` and an earlier revision of this table, which listed it as read first. It was read after the first commit (`37825e61`); its consequences are recorded in §0. |
| owner / reviewer | one audit session (this one) plus three read-only mapping agents, one per article-section group (rows labelled `A`, `B`, `C` in `mapped_by`). The lead re-measured every consequential finding before adopting it (§4.3). No producing lane reviewed its own work. There is no independent reviewer (§0). |

## 0. Campaign-review choice (CAMPAIGN-REVIEW-20260929 §1), recorded after the fact

**Decision answered.** Can a reader reproduce the article's numbers from RC4, and can a maintainer recover the
evidence behind every other number? A useful terminal outcome is a classified inventory with explicit gaps. A
finding of "not reproducible" or "not preserved" counts as a successful result, not a failure of the audit.

**Ownership and review.**
- One owner: this Opus 5.5 session.
- Three read-only mapping agents, also Opus 5.5, each covering a separable section group. They are helpers, not
  independent reviewers. The review warns that "more participants do not create independence" and that agents of the
  same model are not automatically independent origins.
- The owner re-measured every consequential agent finding (§4.3). That is a check by the owner, not an independent
  review.
- The review's recommended independent reviewer, Astra High in a fresh read-only session, was **not used**. It was
  not available in this session's tools, and the goal grants no external delegation. **This audit is therefore not
  independently reviewed.** A fresh read-only review of the RC4 replay (§2–3) and of the six ME rows would be the
  appropriate next step if the findings are to drive article changes.

**Budget and stop.**
- No cluster compute was used: only login-node reads, about 10 minutes of local CPU for the replays, and the agents'
  inference.
- The audit made one pass and no repair loop, in line with the goal's "no review-until-perfect loop" and the
  review's §4. It stops when the inventory and the feasible checks are complete. This revision only corrects the
  record of what was read.

**Practices the review names, as applied here.**
- Cheap discriminating checks came first: the empty-directory replay with only the documented dependencies, before
  any deeper work.
- The review's warning that a hash establishes identity, not validity, is why the claim table separates the receipt,
  the independent check and preservation, rather than treating digest matches as validation.

## 1. Verdict

1. **RC4 reproduces from an empty directory, but not with the dependencies it documents.**
   - With exactly numpy 1.26.4 and scipy 1.15.2, as the README and the article's "standard numerical libraries
     only" state, `verify_rc.py` gives **`VERIFY: FAIL`**. Both figure steps need matplotlib.
   - With matplotlib added, it gives **`VERIFY: PASS`**: 0 differences in every replay, W1 equal, all quoted figure
     numbers within half a unit of the printed digit, and all four figures regenerated. The package tree is unchanged
     afterwards (§2).
2. **The RC4 outputs agree with the current article.**
   - `values.tex` is byte-identical to RC4's `expected/values.tex`.
   - All seven RC4 scripts are byte-identical to `main`.
   - Table I matches the replay in every field.
   - Further checks made only by this audit also reproduce from RC4's inputs: the recovery margins (4.6 / 868.6 /
     49.8), the κ-scan brackets, the lost-draw counts, the power figures and the W1 claims (§3).
3. **Inventory:** 97 claim rows.

   | class | meaning | rows |
   |---|---|---:|
   | **RR** | recomputed from the RC4 package; verified by this audit's replay, or by `fig_numbers.py` in it | 37 |
   | **SO** | supported outside the release by a committed receipt and an independent check | 34 |
   | **SO-NOINDEP** | committed receipt, but no independent check found | 20 |
   | **ME** | missing evidence, or the printed value is not reproduced | 6 |

   In addition, 64 rows carry **UP**: the preservation of their underlying artifact is unverified, or rests on
   purgeable or volatile storage. Every RR row is UP, because the RC4 tarball and its three data files have no
   durable copy.
4. **No printed physics number was found to disagree with its receipt, with one exception: U03.** The article calls
   the seed-effect exponent `0.000` a "fitted exponent" over N = 40/80/160. A least-squares fit to those points gives
   −0.014; `0.000` is the two-point 40→80 value.

   The other five ME rows are:
   - D03: ⟨E_ν⟩ ≈ 6 GeV has no receipt and no citation;
   - J10: the proxy convergence rate 0.45–0.76 cannot be recomputed from any recorded number;
   - R05: the "~11 %" statistic shift is in no committed record;
   - DA2: the dependency statement;
   - DA6: "file identities recorded with the release" is not true of RC4.
5. **The most consequential preservation gap is the release itself.**
   - The RC4 tarball, whose digest `46f801bf…` the manifest pins, exists only in another session's macOS
     `/private/tmp` scratchpad.
   - Its three data files exist on `/pscratch` (purgeable) and in that scratchpad.
   - No commit or durable store holds them, and no committed script rebuilds the tarball byte for byte.
   - Behind the release, the inputs of most SO rows are pscratch-only, so their earliest purge eligibility is around
     **2026-11-20**: the s5c/s5n/s5e/s5p stage-2 runs, the VL170 2D band products, the W2 shifted unfolds, the F2
     shifts, the seed-effect ensembles and the 4D product.
   - The 11 TB of analysed older-production AnaTuples are pscratch-only, and a fresh download does not reproduce
     them (OI-55).

   The proposed fixes are in §6. None was applied: this audit is read-only.

## 2. RC4 from an empty directory

### 2.1 Locating the package

| item | measured |
|---|---|
| tarball path | `<publication-session /private/tmp scratchpad>/rc4/minerva-omnifold-article-release-rc4.tar.gz` (another session's macOS temporary scratchpad), mtime 2026-10-06 21:08:50 |
| sha256 | `46f801bf05bbd18d1fcfe8c8bf5b0e361cd8e352211de641b434547be1680e88`, equal to PACKAGE-MANIFEST §1 |
| size | 15,696,060 B |
| other copies searched | `find /` on this Mac (only that scratchpad, plus RC2/RC3 tarballs in the same scratchpad); on Perlmutter, `find -maxdepth 6` under `/global/cfs/cdirs/m3246/josephrb`, `$PSCRATCH` and `$HOME` for `*article-release*` and `*rc4*`: **no tarball**. The payload files (not the tarball) are at `/pscratch/sd/j/josephrb/pub-release-20261006/{frozen,union,figs}/` with digests equal to `RC4-SHA256SUMS.txt`. Git holds `RC4-README.md` and `RC4-SHA256SUMS.txt` only; `git rev-list --all --objects` finds no `inference_sufficient.npz` or `fig_arrays.npz`. |

### 2.2 Commands

```
S=<this session's scratchpad>
cp <tarball> $S/rc4-tarball.tar.gz && shasum -a 256 $S/rc4-tarball.tar.gz        # 46f801bf…
mkdir $S/rc4-empty && cd $S/rc4-empty && ls -A | wc -l                            # 0
tar -xzf ../rc4-tarball.tar.gz && cd minerva-omnifold-article-release-rc4
shasum -a 256 -c SHA256SUMS                                                      # 18/18 OK
diff <(sort -k2 SHA256SUMS) <(sort -k2 $W/docs/publication/release/RC4-SHA256SUMS.txt)   # identical
cmp README.md $W/docs/publication/release/RC4-README.md                          # identical

# (a) documented dependencies only
python3.11 -m venv venv-doc && venv-doc/bin/pip install numpy==1.26.4 scipy==1.15.2
mkdir $S/run-doc && cd $S/run-doc && tar -xzf ../rc4-tarball.tar.gz && cd minerva-omnifold-article-release-rc4
env -i HOME=$HOME PATH=/usr/bin:/bin TMPDIR=$S/tmp-doc /usr/bin/time -p $S/venv-doc/bin/python -I code/verify_rc.py

# (b) documented dependencies + matplotlib
python3.11 -m venv venv-mpl && venv-mpl/bin/pip install numpy==1.26.4 scipy==1.15.2 matplotlib
mkdir $S/run-mpl && … (fresh extraction) …
env -i HOME=$HOME PATH=/usr/bin:/bin TMPDIR=$S/tmp-mpl MPLCONFIGDIR=$S/tmp-mpl/mpl /usr/bin/time -p $S/venv-mpl/bin/python -I code/verify_rc.py
shasum -a 256 -c SHA256SUMS ; find . -type f | wc -l                              # still 18/18 OK, 20 files
```

Environment: macOS 26.6.2 arm64, Python 3.11.15 (`~/.local/bin/python3.11`), fresh venvs.
(a) `pip freeze` = `numpy==1.26.4 scipy==1.15.2`.
(b) adds `matplotlib==3.11.2` and its dependencies (contourpy 1.3.3, cycler 0.12.1, fonttools 4.66.1, kiwisolver 1.5.1, packaging 26.3, pillow 12.3.0, pyparsing 3.3.3, python-dateutil 2.9.0.post0, six 1.17.0).

### 2.3 Results

| step | (a) numpy + scipy only (the README's stated dependencies) | (b) + matplotlib |
|---|---|---|
| joint tests, frozen, vs `expected/joint-evaluate.json` | ok, `COMPARE: AGREE (0 differences)` | ok, AGREE (0) |
| recovery union, reading (a), vs `expected/resolved-evaluate.json` | ok, AGREE (0) | ok, AGREE (0) |
| W1, readings (a) and (b), vs `expected/W1-RESULT-20261006.json` | ok, 0 claim and 0 criterion differences, qualifying `[]` | ok, same |
| Figs. 1–3 quoted numbers vs `expected/values.tex` | ok, `FIG NUMBERS: PASS` | ok, PASS |
| Figs. 1–3 regenerated | **FAIL**, `ModuleNotFoundError: No module named 'matplotlib'` | ok, 3 PDFs |
| Fig. 4 regenerated | **FAIL**, same cause | ok |
| **verdict** | **`VERIFY: FAIL`, rc 1**, 138 s wall time | **`VERIFY: PASS`, rc 0**, 199 s wall time |
| package tree after the run | 18/18 checksums OK | 18/18 OK |

Logs: `verify-doc.txt` sha256 `f66e00a6…`, `verify-mpl.txt` sha256 `6d2a9438…` (appendix B).

**Reading.** RC4 reproduces every replayed value from an empty directory once matplotlib is present. Its README says
"with numpy and scipy only" and lists only numpy and scipy under "Tested with". `code/figs/make_figs.py:17` and
`code/figs/plot_joint_null_distributions.py:27` import matplotlib. The article's Data availability section says
"with standard numerical libraries only … regenerate Figs. 1–4". A reader who installs exactly what the README
names gets `VERIFY: FAIL`. This is a documentation defect, not a numerical one, but it is the first thing an outside
reader would hit.

## 3. RC4 outputs against the current article

The article sources at the baseline (`fec438db`; the last change to them is `bf4f1a29`, merged at `0e7d9b1b`;
`git diff 0e7d9b1b fec438db -- docs/analysis-note publication` is empty):

| article source | sha256 |
|---|---|
| `main_paper.tex` | `1a63bffa…` |
| `paper_body.tex` | `9595eca2…` |
| `values.tex` | `46640a8f177768b47d3cabf46d272ad2c3daa8b1799f55fa04dd69a25fba026a` |
| `values_inference.tex` | `7a786528…` |
| `publication.bib` | `13084b6c…` |

| comparison | method | result |
|---|---|---|
| `values.tex` | `diff` of RC4's `expected/values.tex` against the current `docs/analysis-note/values.tex` | **byte-identical** (both `46640a8f…`). RC4 was built before three paper commits (`352f156a`, `dc19ce17`, `bf4f1a29`), but none of them touched `values.tex`. |
| RC4 code vs main | `cmp` of every RC4 script with its source in `publication/` | all 7 byte-identical (`replay_inference.py`, `verify_rc.py`, `make_reading_b.py`, `w1_projected_tests.py`, `figs/fig_numbers.py`, `figs/make_figs.py`, `figures/plot_joint_null_distributions.py`) |
| `expected/joint-evaluate.json` vs main | `cmp` against `docs/orchestration/state/s5p/stage7/joint/joint-evaluate.json` | byte-identical (`b9604502…`) |
| Table I (10 rows × B, k, p, Holm threshold, CP interval) | Table I parsed from `paper_body.tex:529-538`, compared with this audit's replay output `replay-frozen.json` | **0 mismatches**; p numerators and denominators exact; thresholds and CP endpoints equal at printed precision |
| the article's literal ratios (`$1.07$--$1.39$`, `$1.11$--$1.13$`, `$1.07$--$1.15$`, `$1.14$--$1.16$`, `1.61`, `1.39`, 7 %, `\SIrange{12}{30}`, `\SIrange{23}{31}`) | `grep -cF` in `paper_body.tex`, and against `fig_numbers.py`'s built-in table | all present exactly once in the forms checked, and equal to the built-in table |
| the verbal shares ("two thirds", "most", "a fifth") | `fig_numbers.py` | 67.2 %, 83.2 %, 21.9 %, inside the script's declared intervals |
| Fig. 3 | regenerated (`make_figs.py`) and rendered beside `figures/paper_eavailW_generators_ratio.pdf` at 100 dpi | same curves, points, ratios and legend; only line weights differ (matplotlib version) |
| Fig. 4 | regenerated beside `figures/paper_joint_nulls.pdf` | same panels, histogram shapes, observed lines and k/B labels |
| Fig. 2 | regenerated beside `figures/paper_joint_localization.pdf` | same cell colours on both panels; axis labels differ; the article's PDF comes from an older producer (`0a4ab263`, 2026-08-25) |
| Fig. 1 | regenerated beside `figures/model_comp_projections.pdf` and `figures/paper_validation_residual.pdf` | same quantities; the article's PDFs come from older producers (`1e7c2868`, 2026-07-15; `0a4ab263`); the pull colour scale differs (±3 vs ±5). **Defect:** the regenerated Fig. 1 text panel says "This work: pending VL170" (`make_figs.py:57`), where the article prints 6.87 %. Equality of the article's Fig. 1 and Fig. 2 PDFs with the release arrays is visual only. |

### 3.1 Further checks from the RC4 inputs (beyond `verify_rc.py`)

| article claim | check | result |
|---|---|---|
| 224 lost calibration and 53 lost power pseudo-experiments (`paper_body.tex:576-578`) | 7400 submitted − Σ B (RC4) = 224. 1200 − Σ n of the six power sets = 53. The interrupted/never-started split is summed from the committed `missing-sensitivity.json` (`f48e16ef…`). | 224 ✓; 53 ✓; 111 + 113 ✓ (power 26 + 27) |
| 1400 submitted per null (1800 NuWro) (Table I caption) | B in the RC4 union reading | 1400 ×4, 1800 ✓ |
| the recovered experiments are the lost ones | RC4 union seeds minus frozen seeds, compared with the committed `missing_seeds` lists | equal sets for all 5 nulls (34/57/49/35/49) ✓ |
| closest approach 4.6 below 868.6 (GENIE + MEC shape, κ = 3 robust); next 49.8 (GENIE CV shape) (`:589-591`) | new script `recovery_margins.py` (sha256 `68d6d37c…`): T of the 224 recovered draws for every claim and robustness variant | 0 of 62 (test, variant) cells reach T_obs. Gap 4.62 (T_obs 868.59, max 863.97); next 49.82 ✓ |
| power 1.0 / 1.0 / 0.23; 172–199 retained; GENIE-null shape power 0.74 / 0.02 / 0.00 (`:565-569`) | replay `power` block | 1.0, 1.0, 0.2308; n = 193, 195, 195, 199, 193, 172; 0.7387, 0.0207, 0.0 ✓ |
| W1: p < 0.05 in at least one projection for every test; GENIE CV (p_T,p∥) p = 0.48 / 0.63 (`:550-552`, `:624-625`) | `make_reading_b.py` + `w1_projected_tests.py` rerun (`w1-replay.json` `d3c8c199…`) | for every test, the smaller of the two projection p-values is at most 0.0014 (the largest such value over the ten tests), in both readings. GENIE CV (p_T,p∥): 0.4832 (676/1400) and 0.6288 (880/1400) ✓. These are recovery-union readings (B = 1400/1800), not the frozen B. |
| κ-scan: determinate rejections up to 5.25; first loss in (5.2547, 5.2563] (frozen) and (5.1688, 5.1703] (union) (`:481-488`) | new script `kappa_brackets.py` (`c119c17d…`): the committed `Scan` class with RC4's `replay_inference.py` (digest checked), family A at the five bracket endpoints | frozen: κ = 5.25 and 5.2546875 all rejected; κ = 5.25625 → GENIE + MEC shape undetermined (own, k = 23) and GENIE CV shape undetermined (inherited, own below, k = 27). Union: 5.16875 all rejected; 5.1703125 → the same two (k = 24 / 26) ✓ |
| robustness labels (all ten at κ = 3) | replay `decisions_robust_kappa` | 10/10 rejected, frozen and union ✓ |

## 4. Claim inventory

### 4.1 Method

**Scope.**
- Every number in `main_paper.tex` (abstract) and `paper_body.tex` (Secs. I–VIII, figure captions and Table I).
- The data-availability statements, because they make checkable reproduction claims.
- Generator and estimator configuration numbers, as one row each.
- Literature numbers, with the internal record that supports each transcription.
- Purely definitional numbers, such as grid edges, are folded into the row of the result that uses them.

**Fields per row** (`CLAIM-TABLE-20261008.tsv`):
- the printed value;
- the canonical receipt (path, introducing commit, ledger row), with the printed value checked against it;
- the underlying artifact (path, sha256, location);
- the independent check;
- the preservation route, and whether a durable copy was observed;
- the class and the UP flag;
- the gap and the proposed fix.

The `primary_class` of a row that mixes classes is its weakest component.

**Instruments.**
- Read-only `git` in the worktree.
- `python3 -I` on committed JSON receipts.
- The RC4 replay environment of §2.
- Read-only `ssh saul.nersc.gov`: `ls`, `stat`, `find` with a bounded depth, `sha256sum` on files under 2 GB,
  `hsi -q ls`, and `scp` of 8 small shift files to a local scratchpad.

**Side effect.** Hashing pscratch files moved their access times to 2026-10-08. The mapping notes record the earlier
atimes. Atime is therefore no longer evidence that anyone needs a file, and the purge dates below use the earliest
pre-audit atimes.

### 4.2 Counts by section

| section | RR | SO | SO-NOINDEP | ME | UP |
|---|---:|---:|---:|---:|---:|
| Abstract | 1 | 1 | – | – | 2 |
| I Introduction (literature) | – | 1 | 1 | – | – |
| II Data | – | 4 | 1 | 1 | – |
| III Method | – | 2 | 1 | – | 1 |
| IV.A 2D reproduction | 7 | – | – | – | 7 |
| IV.B 2D uncertainty | 1 | 2 | 4 | – | 3 |
| IV.C higher-dimensional validation | – | 5 | 2 | – | 7 |
| V Central values | 10 | – | 4 | – | 13 |
| VI.A–B Joint-test design and conditions | 3 | 6 | 4 | 1 | 8 |
| VI.C Results, Table I, κ-scan, W1, power | 9 | – | – | – | 9 |
| VI.D Lost pseudo-experiments | 2 | 3 | 1 | – | 3 |
| VI.E Detector response (W1 p, W2) | 1 | 4 | – | 1 | 4 |
| VII Uncertainty status | – | 5 | 2 | 1 | 3 |
| VIII Data availability | 3 | 1 | – | 2 | 4 |
| **total** | **37** | **34** | **20** | **6** | **64** |

**SO-NOINDEP rows** (committed receipt, no independent check found): L02, D06, M01, V08, V12, V13, V14, V15, V20,
C02, C03, C04, C12, J01, J04 (in part), J09, J14, J24 (the 111/113 split), U04, U06.

Some of them were recomputed by this audit from committed inputs. That is a first independent recomputation, not yet
committed as a receipt:
- V11, V12 and V13 (91.2 % / 0.679, 0.674 %, 97.7 % / 78.1 %), by `checks/recheck_coverage.py`;
- C02 (0.824 % and 0.745 % maxima, from the committed FSI summaries);
- J09 (§4.3).

### 4.3 Findings the lead re-measured before adopting

| row | finding | lead's own re-measurement |
|---|---|---|
| U03 | The article prints "fitted exponent 0.000" (`paper_body.tex:672-673`, `\seedEffectExponent`) after the three seed-effect values at N = 40, 80, 160. No committed code fits it. The source table (`EVIDENCE-20260920-sproj-resolution-floor-and-seed-effect.md:22`) prints `0.000` without a derivation. | Least squares of log s on log N: **p = −0.0144** over the three means (6.0243, 6.0232, 6.1454) and −0.0130 over all seven points. The two-point 40→80 exponent is **0.0003 → 0.000**. "Did not fall" still holds (p ≤ 0); the printed value of the stated fit does not. |
| J09 | The 0.50–0.86 is described as an "unweighted (L2) norm" (`paper_body.tex:427-429`). | From `stage3/f2/delta-*.npz` and `stage3/m1/fine-minus-mid-*.npz` (scp'd; their digests match the committed receipts; `D_J` of the latter is bitwise equal to RC4's `d1__`): the relative per-cell L2, ‖d1/f‖/‖D_F2/f‖, gives **0.750 / 0.856 / 0.505 / 0.528**, which reproduces the range. The raw L2 gives 0.784 / 0.576 / 0.496 / 0.346, which does not. Agent C's per-generator values differ in the second decimal (0.759 / 0.857 / 0.542 / 0.504); the formula is unrecorded. No committed producer exists. |
| J28 | B = 1200 early stop for four nulls | 99.5 % CP upper bound at k = 0: B = 1200 → 0.004980 < 0.005 (stop); B = 1000 → 0.005974 (continue) |
| V13 | The rescored C2 interval lies above its 2σ window | `rescore_vl169_toys_vl170.json`: C2 0.9769, interval [0.9737, 0.9800], window [0.9281, 0.9722]. The article says only that the 1σ fraction is above its window. |
| C04 | "within 10 %" of Ascencio *et al.* omits an open caveat | `VALIDATION_LEDGER.md:1667-1697`: ratios 1.092 and 1.063. Its fourth caveat (OI-59, open) says the two E_avail truth axes are defined differently, with a measured ≈ 11 % migration in those cells. The article does not state it. |
| R05 | "statistics move by up to about 11 %" is in no committed record | Agent C: 10.95 % (MnvTune total at +4 %, against the frozen observation), 9.70 % against the δ = 0 control. The lead confirmed by `grep` that `W2B-REPORT-20261006.md` contains no 11 % statement. |
| fig-array sources | Five `fig_arrays.npz` source files are absent from the s5p CFS archive | Lead: `ours_2d` 142a45b0, `paper_cov` 6c6dce72 and `excess_eavail_W` 751bb859 re-hashed on CFS in `minerva-shutdown-stage/fig_products/`. `xsec_5d` 630306e2 re-hashed in the global-home evidence epoch `preparation-2026-09-24-bf34a12c/trunk-baseline/`. The Tune v1 text file is git-tracked (22231752). |
| products behind the joint tests | Is the CFS archive complete for the release inputs? | Lead: every product digest in the RC4 manifests is in the archive's SHA256SUMS (`1a72cb43…`, re-measured): **8,333 / 8,333** (frozen) and **8,611 / 8,611** (union). The only digests not found are the code, the design (git-tracked at `docs/orchestration/state/s5p/prod/design.json`, sha256 `404446eb…`) and the npz itself. |

### 4.4 Wording and citation defects (no number changes)

- **Mis-routed source comments:**
  - `paper_body.tex:253` attributes the pion-FSI "< 1 %" and "within 10 %" to VL159/VL160, which contain neither.
    The receipts are `3d-unfolding/genie/genie_fsi_{FrAbs,FrInel}_pi_xsec3d_summary.txt` and the Ascencio ledger
    entry.
  - `RC4-README.md:123,127` routes the covariance-status numbers to VL142–VL144. They live in
    `GRADE-20260920-cause3-two-member.json`, `SEED-EFFECT-20260920.json`, the FLOOR JSONs and
    `CENTRAL-VALUE-VS-SIGMA-20260920.json`; VL146 is the control for 6.145 %.
  - `paper_body.tex:776` (Data availability) still cites RC3 (`7999d094…`), not RC4.
  - The source comment at `:655` places `9ffc4ddd` on branch `s5p-parallel-recompute-20260928`.
    It is an ancestor of `main` now, as are every other commit the article's comments cite (`466b427b`, `00009056`,
    `22a004e7`, `09718448`, `940d84aa`, `538739ff`, `b354cdf7`; checked with `git merge-base --is-ancestor`).
- **Stale claim map.** `CLAIMS-20261005-claim-to-evidence.md` §E still says the tolerance beyond κ = 3 "is not
  evaluated". The κ-scan sentence (`bf4f1a29`) has no claim-map row.
- **Retyped literals that no build check binds:**
  - Sec. V prints 1.07–1.39, 1.11–1.13, 1.07–1.15, 1.14–1.16, 1.61, 1.39, 7 %, 12–30 % and 23–31 % as literals.
    `fig_numbers.py:92-112` checks them against its own hard-coded copy, not against `paper_body.tex` (which is not
    in the release).
  - Sec. IV prints 0.674, 97.7, 78.1, 4, 0.3, 1, 1.4, 74 and 16–31 % as literals with no macro.
  - All match today (§3, §4.3).
- **Minor:**
  - **D03:** ⟨E_ν⟩ ≈ 6 GeV needs a citation.
  - **M03:** "about fifteen-fold" is the low end of per-cell ratios 14.9–36.8, and no receipt states it.
  - **V14:** "its cause is untested" predates the KI-85 diagnostic `8eb40e5f`, which is descriptive.
  - **V19:** 16–31 % holds for (E_avail,W) cells only (33.6 % in one joint cell), with a different estimator than the 74 %.
  - **C14:** "slightly above" means 9.4 % and 11.7 %.
  - **W1 operand:** W1 is computed on the recovery-union readings (B = 1400/1800); the article does not say so.
  - **Fig. 1 label:** RC4's regenerated Fig. 1 prints "This work: pending VL170" (`make_figs.py:57`).
  - **A7 inconsistencies:** amendment 7 is internally inconsistent in two places that the article does not inherit:
    `calibration.metric` "exactly 200 products" vs `metric_frozen.n` = 194; condition 4 "~0.05 null SD" vs the
    pre-freeze 0.068.
- **DA3.** The outside-reader empty-directory replay on record (`RC1-REPLAY-RECEIPT-20261006.md`) is of RC1, which had
  no figure numbers. This audit's replay is the first empty-directory replay of RC4 on record.

## 5. Preservation map

The durability classes used below:
- **git** — committed on `main` (public origin);
- **CFS** — `/global/cfs/cdirs/m3246/josephrb/…`, durable project storage; the user's directory measured 1.5 TB on
  2026-10-08, against Joseph's 3 TB rule;
- **home epoch** — `/global/homes/j/josephrb/evidence/repository-epochs/…`, durable and backed up, but the home
  filesystem is 93 % full;
- **HPSS** — tape, 54 files / 373.6 GB;
- **pscratch** — purged after 8 weeks without access;
- **/tmp** — a local macOS temporary directory.

| artifact (claims) | identity | observed locations | durable? |
|---|---|---|---|
| **RC4 tarball** (all RR rows; DA1–DA4) | `46f801bf…`, 15,696,060 B | /tmp of another session only | **NO** |
| RC4 `inference_sufficient.npz` frozen / union (J15–J29, A01) | `7bd019c6…` / `6ffed091…` | pscratch `pub-release-20261006/{frozen,union}`; inside the tarball | **NO** (regenerable from CFS products + git code; regeneration untested, the extractor reads pscratch paths from `design.json`) |
| RC4 `fig_arrays.npz` (V01–V09, C05–C14) | `72394a2b…` | pscratch `pub-release-20261006/figs`; inside the tarball | **NO** (all sources durable, see next row; regeneration untested) |
| fig-array sources | 142a45b0, 6c6dce72, 751bb859, 630306e2, 22231752, 4 generator ROOTs, mnvtune 5D | CFS shutdown-stage (3), home epoch (1), git (1), CFS s5p archive (5) | YES, re-hashed. The receipts name only the pscratch paths. |
| RC4 code | 7 scripts | git `main`, byte-identical | YES |
| s5p calibration, power and recovery products (Table I, J24–J29) | 10,612 files, SHA256SUMS `1a72cb43…` | CFS `s5p-archive-20261006` | YES, a single copy; no HPSS copy |
| s5p V, M1 shifts, data vector, design | 35979ef7, d1 files, fb5cc679, 404446eb | CFS archive / git | YES |
| s5p F2 shifts, `runs/s3r/f2` asimovs, 20 jitter re-unfolds, lateral endpoint unfolds, V pilot ensemble (194) (J06, J09, J11, J13) | per agent C notes | pscratch `s5p-20260926` only | **NO**; pre-audit atime ≈ 2026-10-06 |
| W2 shifted data unfolds rr0 / rr1 / rrzero (R04, R05, A02) | df11bfd8 / 36313201 / ec5dc97d | pscratch `w2-recoil-20261006` only | **NO** |
| s5c `runs/d1`, `runs/s_valid`; s5n `runs`; s5e `runs/cand`; s5p `runs/s2` (V16–V21, M03) | 30 / 1,849 / 649 / 726 / 923 files | pscratch only | **NO**; earliest pre-audit atime 2026-09-25 → **purge-eligible ≈ 2026-11-20** |
| VL170 2D band: bootstrap covariance, universe rollup, 600 replicas (V08, V12) | 71a75821, 077912e3 | pscratch only (HPSS holds only the VL162-era files) | **NO** |
| VL169 coverage toys (V10, V11) | 200 files | pscratch only | NO (the committed scores reproduce from git-tracked inputs) |
| adopted trunk `z-cv.npz`; projection (U01, VII) | 3d7465f6… (890,500,272 B); 835828bf | pscratch + home epoch (both re-hashed) | YES (home epoch only; no CFS/HPSS copy; the HPSS "solecopy" holds `z-mean.npz`, not `z-cv.npz`) |
| member throw roots, `mii/member_k000000`, `_k001200` (U02) | 2.67 GB each | pscratch only | **NO** |
| seed-effect / floor ensembles `z2m-floor-20260920{,-k1200}` (U03, U04) | 15 GB each | pscratch only; pre-audit atime 2026-09-20 → **≈ 2026-11-15** | **NO** (the committed JSONs are byte-identical to the cluster copies) |
| 4D product `xsec_4d_MEFHC_5iter_lgbm.root` (C04, V15) | 1fb82508 | pscratch only | **NO** |
| `of_inputs_5d.npz` (5D unfolding input) | 1.55 GB | pscratch only | **NO** |
| merged 5D omnifile | 169,974,191,800 B | pscratch + HPSS (md5 hashverify PASS 2026-08-20, `RECEIPT-20260820-oi50-hashverify.md`) | YES |
| analysed older-production AnaTuples (D01–D05; all event-level reproduction) | 1,818 data + 489 MC + 53 flux/reweight + 9 param files ≈ 2,369; 11 TB; names in `2d-unfolding/playlist_manifests/` (paths only) | pscratch `minerva/minerva_large_files` only | **NO**. A fresh download gives a different production (OI-55), and no per-file sizes or checksums are committed. |

## 6. Consequential gaps and proposed fixes (ranked)

None of these was applied. Items marked **(Joseph)** change article wording, scope or storage commitments, or need
an external act, so they are his decision. The rest are maintenance any lane could do under a normal authorization.

| # | gap | consequence | proposed fix |
|---|---|---|---|
| G1 | The RC4 tarball (`46f801bf…`) and its three data files have no durable copy, and no committed script rebuilds the tarball byte for byte (tar/gzip metadata would change the digest even with identical contents) | The package the manifest pins, which coauthor review and any deposit would reference, is lost at the next `/tmp` cleanup or reboot of one Mac, or at pscratch purge | (a) Copy `minerva-omnifold-article-release-rc4.tar.gz` and `pub-release-20261006/{frozen,union,figs}` to CFS (e.g. `/global/cfs/cdirs/m3246/josephrb/article-release-rc4/` with a SHA256SUMS), and record the path in PACKAGE-MANIFEST §1b. (b) Commit `publication/release/build_rc.sh` with deterministic tar flags (`--sort=name --mtime=@0 --owner=0 --group=0 --numeric-owner`, `gzip -n`), so any future RC is rebuildable to its digest. |
| G2 | `RC4-README.md` and the article (`paper_body.tex:752-753`, "standard numerical libraries only") omit matplotlib, which the figure steps import | An outside reader who installs what is documented gets `VERIFY: FAIL` | Add matplotlib (tested 3.11.2) to the README's dependency and "Tested with" lines and ship a pinned `requirements.txt`. Article: "with numpy, scipy and matplotlib" **(Joseph, article wording)**. RC5 or a README-only revision. |
| G3 | Pscratch-only inputs behind SO claims: the s5c/s5n/s5e/s5p stage-2 runs, the VL170 2D band products, the W2 unfolds, the F2 shifts and asimovs, the jitter and lateral unfolds, the V pilot ensemble, the seed-effect ensembles, the member throw roots, the 4D product and `of_inputs_5d.npz` | Purge-eligible from ≈ 2026-11-15/20. After that, V08, V12, V16–V21, M03, J06, J09, J11, J13, R04, R05, U02–U04 and C04 can no longer be re-derived from products; only their committed summary JSONs would remain | Copy them to CFS with a SHA256SUMS. Measured with `du --apparent-size` on 2026-10-08: the stage-2 runs, the 2D band products, the toys, replicas, F2, s3r, s3v, s3 and W2 directories together ≈ 0.7 GiB; the floor ensembles 2 × 14.9 GiB; the two member throw roots 2 × 2.67 GB (not the whole 86 GiB `mii/` tree); `of_inputs_5d.npz` 1.55 GB. The total is ≈ 38 GB, inside the 3 TB rule (1.5 TB used). Then add the durable path to each receipt. **(Joseph: storage decision under the 3 TB rule.)** |
| G4 | The analysed AnaTuples (11 TB, older production) are pscratch-only, and their identities are names only. The article says the "file identities are recorded with the release" (DA6), which is not true of RC4. | Event-level reproduction of every non-release number depends on files that a re-download does not reproduce | (a) Commit a manifest of name, size and checksum for the ≈ 2,369 files; sizes cost one `find -printf`, checksums a login-node pass, or use the remote's adler32 where available. Ship it in the release. (b) Decide on durable storage: an HPSS quota increase, or ask MINERvA/Fermilab whether the older production is preserved under a version tag **(Joseph; external contact)**. (c) Until then, reword DA6 **(Joseph)**. |
| G5 | U03: "fitted exponent 0.000" is not the fit over the points it follows (fit −0.014) | A printed three-decimal value that a reader cannot reproduce | Print "fitted exponent −0.01" or "two-point (40→80) exponent 0.000", and commit the fit code beside `SEED-EFFECT-20260920.json` **(Joseph, wording)**. The same value appears in note `sec_eavailw.tex:276` and in the correction records. |
| G6 | J09/J10: the "unweighted (L2) norm" description is wrong (the range reproduces with a relative per-cell L2), no producer is committed, and the proxy rate 0.45–0.76 is reproducible from no record | Condition (i)'s quantitative basis cannot be re-derived, and the norm is misnamed | Commit a producer for the M1/F2 ratios with an explicit norm, and record the proxy-rate inputs or mark 0.45–0.76 as an unrecomputable design-review figure. Reword to "relative (per-cell fractional) L2" **(Joseph, wording)**. Add D_F2 and f_B_mean to the next RC so J09 becomes RR. |
| G7 | R05: "~11 %" is in no record | An unreceipted number in the response section | Add the max \|ΔT/T\| and its baseline (frozen observation, 10.95 %; or the δ = 0 control, 9.70 %) to `W2B-REPORT-20261006.md` as a dated addendum. |
| G8 | C04: the open OI-59 truth-definition caveat (≈ 11 % migration in the compared cells) is not disclosed beside "within 10 %" | An omitted qualifier on a comparison claim | A clause or note in Sec. V, or drop the comparison **(Joseph, scientific wording)**. |
| G9 | The adopted trunk `z-cv.npz` is durable in the home epoch only; the CFS s5p archive is the only copy of the joint-test products (no tape copy) | A single durable copy of each | Optional HPSS copy of `z-cv.npz` (0.9 GB) and of the s5p archive (2.3 GB), with `hsi hashverify`. HPSS headroom was not re-measured (`hpssquota`). |
| G10 | Citation routing: `paper_body.tex:253` (VL159/VL160), `:776` (RC3), `:655` ("on branch"); `RC4-README.md:123,127` (VL142–VL144); CLAIMS §E stale on κ | A reader following the route reaches the wrong record | Correct the source comments (no output change) and add a CLAIMS §F row for the κ-scan sentence. |
| G11 | Retyped literals (§4.4) are not checked against `paper_body.tex` | A future prose edit passes `verify_rc.py` | Move the Sec. IV/V literals into `values.tex` macros, so that `fig_numbers.py --values` binds them, or have `fig_numbers.py` read `paper_body.tex`. |
| G12 | Regeneration of RC4's data files from durable storage is untested: `extract_inference_sufficient.py` reads product paths from `design.json` (pscratch), and `export_fig_arrays.py` defaults to pscratch roots | "Regenerable from the archive" is a claim with no test | Add a root-remap option to the extractor and run one login-node regeneration from the CFS archive into a scratch directory. Compare against `7bd019c6…`. The exporter already has `--analysis-root` and similar options. |
| G13 | Small items: D03 citation; V13 2σ wording; V14 "untested" vs KI-85; M03 receipt for "fifteen-fold"; V19 scope; W1 operand; Fig. 1 "pending VL170" label; A7 inconsistencies; L02/R03 literature quotes stored only as agent-reported text | Minor | Batch them into the next paper pass and the next RC. Store verbatim quotes for the literature numbers. |

## 7. Unresolved, not done, and blockers

- **Not done by design (read-only audit and the goal's exclusions):**
  - no copy, archive or deletion (G1, G3, G4, G9);
  - no cluster job;
  - no regeneration run on the cluster (G12);
  - no κ full-grid rerun (the record's independent reproduction already AGREEs; this audit checked only the five
    article bracket points);
  - no tag, deposit, submission or external message.
- **Byte-level verification gaps:**
  - The CFS archive's 10,612 files were checked by manifest digest against its SHA256SUMS. The files themselves were
    not re-hashed (2.3 GB), apart from the samples the agents hashed.
  - The HPSS copies were checked by size only (`hsi hashverify` reads every byte and was not run).
- **Unverifiable from here:**
  - the literature transcriptions (L01, L02, R01, R03a) against the papers; there was no web fetch, and only the
    internal records were checked;
  - whether macOS will clear the other session's `/private/tmp` scratchpad, and when.
- **Atime-based purge dates are approximate.** This audit's reads reset the atimes it touched. The dates use the
  earliest pre-audit atimes recorded in the mapping notes.
- **No independent review of this audit** (§0). The mapping agents and the owner are the same model family. A fresh
  read-only reviewer has not checked the findings.
- **Figure equality.** Figs. 1 and 2 in the article come from older producers. Their equality with the release arrays
  was checked visually, not numerically.

## 8. Reproducing this audit

```
W=<worktree at fec438db>; S=<empty scratch dir>; RC=<path to minerva-omnifold-article-release-rc4.tar.gz>
shasum -a 256 $RC                                       # 46f801bf05bbd18d1fcfe8c8bf5b0e361cd8e352211de641b434547be1680e88
python3.11 -m venv $S/venv-doc && $S/venv-doc/bin/pip install numpy==1.26.4 scipy==1.15.2
python3.11 -m venv $S/venv-mpl && $S/venv-mpl/bin/pip install numpy==1.26.4 scipy==1.15.2 matplotlib==3.11.2
for v in doc mpl; do mkdir $S/run-$v && tar -xzf $RC -C $S/run-$v
  (cd $S/run-$v/minerva-omnifold-article-release-rc4 && env -i HOME=$HOME PATH=/usr/bin:/bin \
     MPLCONFIGDIR=$S/mpl $S/venv-$v/bin/python -I code/verify_rc.py; echo rc=$?); done
R=$S/run-mpl/minerva-omnifold-article-release-rc4
diff $R/expected/values.tex $W/docs/analysis-note/values.tex
$S/venv-mpl/bin/python -I $R/code/replay_inference.py --npz $R/data/frozen/inference_sufficient.npz \
    --compare $R/expected/joint-evaluate.json --out $S/replay-frozen.json
$S/venv-mpl/bin/python -I checks/recovery_margins.py $R
$S/venv-mpl/bin/python -I checks/kappa_brackets.py $R $W/publication/kappa/kappa_breakdown.py
mkdir $S/m && cp notes/*.tsv $S/m && python3 checks/merge_claims.py $S/m && diff $S/m/CLAIM-TABLE.tsv CLAIM-TABLE-20261008.tsv   # identical
ssh saul.nersc.gov 'cat /global/cfs/cdirs/m3246/josephrb/s5p-archive-20261006/SHA256SUMS' | shasum -a 256   # 1a72cb43…
```

## Appendix A. Files in this directory

| file | what it is |
|---|---|
| `REPORT-20261008-release-reproducibility-audit.md` | this report |
| `CLAIM-TABLE-20261008.tsv` | the 97-row claim-to-artifact table (tab-separated; 16 columns) |
| `checks/recovery_margins.py`, `checks/kappa_brackets.py` | the lead's new RC4-input checks (§3.1) |
| `checks/recheck_coverage.py`, `checks/agentC_checks.py` | the mapping agents' recomputations (V11–V13; J13, J28) |
| `checks/merge_claims.py` | builds the table from the skeleton and the four row files |
| `logs/verify-doc.txt`, `logs/verify-mpl.txt` | the two `verify_rc.py` runs (stdout+stderr; renamed from .log, contents unchanged) |
| `logs/fig_numbers.txt`, `logs/kappa_brackets.txt` | figure-number and κ-bracket outputs |
| `logs/replay-frozen.json`, `logs/replay-union.json`, `logs/w1-replay.json` | replay outputs from the RC4 inputs |
| `notes/mapping-notes-{A,B,C}.md` | the mapping agents' command logs (local paths abbreviated) |
| `notes/claims-skeleton.tsv`, `notes/{lead,agent-A,agent-B,agent-C}-rows.tsv` | the inputs from which `merge_claims.py` rebuilds the table |

## Appendix B. Digests

| object | sha256 |
|---|---|
| RC4 tarball | `46f801bf05bbd18d1fcfe8c8bf5b0e361cd8e352211de641b434547be1680e88` |
| RC4 `SHA256SUMS` contents | identical to `docs/publication/release/RC4-SHA256SUMS.txt` at `fec438db` |
| CFS archive `SHA256SUMS` | `1a72cb439120d910ee509fa0be7915924eb36b6a42fda8bda8006a0a92609935` (10,612 lines) |
| `values.tex` (article = RC4 expected) | `46640a8f177768b47d3cabf46d272ad2c3daa8b1799f55fa04dd69a25fba026a` |
| `joint-evaluate.json` (main = RC4 expected) | `b9604502b1aa263508ba46f0be91846d7a2106f6f2fd0ba5c172b87ee256dd11` |
| `missing-sensitivity.json` | `f48e16ef351ea78c59b7e75f5bf653dc5742857457786e3d8fd1a067be8e2293` |
| `robust-labels.json` | `206655f906bdffac636676f39ed86267f31eb9600ed9d45a335905fdaf7fde2a` |
| `verify-doc.txt` / `verify-mpl.txt` | `f66e00a6d0021436ae6900358ea426eba9c7af24babc6d2bb11786f639b05d79` / `6d2a943817df7fc0e7f90b802ad6f47e4ebbaff30aa8210328b483ff849b5956` |
| `replay-frozen.json` / `replay-union.json` | `780840d3…` / `148436eb…` |
| `w1-replay.json` | `d3c8c199…` as produced; `87537d7f…` as committed (local npz paths abbreviated) |
| `CLAIM-TABLE-20261008.tsv` | `56e48b31742736e98d0a2c1f2c143f4d5746ed84b0320e585310dbeeef177b2e` |
| `recovery_margins.py` / `kappa_brackets.py` | `68d6d37c…` / `c119c17d…` |
| regenerated Figs. 1–4 (not committed) | `b2a91450…`, `35eb41da…`, `0c33c63b…`, `19b9c8f2…` |

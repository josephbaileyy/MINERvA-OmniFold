# Publication correction — keep and disclose (2D estimator pairing)

| field | content |
|---|---|
| `Lane` | publication correction (assigned by Joseph 2026-10-09 after Session 1's §11 ruling) |
| `Decision` | Are the paper, note and primer factually consistent about the frozen central estimator, the uncertainty estimators, seed provenance and unmeasured transfer, without claiming that disclosure has established publication readiness? |
| `Branch` / `Base` / `Head` | `prep/next-publication-20261009` / `5ac9706a21e8a5ac8863a65fd7623d8ab8d22269` (merge of PR #61; equal to `origin/main` at 2026-10-09T19:58Z) / source head `11c753b7f84cdc1112a4586e7bf42a94ff23641d`; this report and the regenerated `MANIFEST.tsv` are in the commit after it |
| `Owned files` | §0 (claimed before editing) |
| `Pinned inputs` | §1 |
| `Resources` | §7: about 0.6 h active, about 0.12 local core-h, peak RSS about 0.13 GB, about 0.86 GB scratch, about 24 KiB tracked evidence; cluster 0, GPU 0, no training, no toys |
| `Review` | one fresh read-only subagent; initial review of `2b4dc8ff` PASS WITH CHANGES (0 material, 5 minor, 6 notes); one repair batch `b7f4c065`; focused re-review PASS (10 resolved, F6 declined, 1 new note N1, applied after review in `11c753b7` and not re-reviewed); §5 |
| `Model / effort` | owner and reviewer: Claude Opus 5.5 (`claude-opus-5-5`), Claude Code; effort not observable to the session |
| `Disposition` | correction **PASS** (§6); publication-ready objective **not achieved** |
| `Next action` | Joseph: review and merge decision for this PR and the standalone branch; the scientific pairing stays open (§8) |

`Q` = `docs/orchestration/state/next-preparation-20261009`.

## 0. Claimed files (recorded before editing)

Ownership observed at 2026-10-09T20:00Z: no worktree had uncommitted changes to any path below
(`git status --porcelain` in all 20 worktrees; the guard lane's new worktree was mid-checkout and owns
none of them); no local or `origin` branch ahead of the base touches `docs/analysis-note/`,
`KNOWN_ISSUES.md`, `docs/publication/`, `CATALOG.md` or `MANIFEST-overrides.tsv` except branches last
touched on or before 2026-10-05, which are not live claims; no open PR. The standalone repository's
`origin/main` `ad3fb80` is blob-identical to the base's `docs/analysis-note/` in every tracked file
except its own `.gitignore` and `AGENTS.md`.

Canonical repository, this branch:

- `docs/analysis-note/paper_body.tex`
- `docs/analysis-note/primer_body.tex`
- `docs/analysis-note/sec_method.tex`
- `docs/analysis-note/sec_systematics.tex`
- `docs/analysis-note/sec_results.tex`
- `docs/analysis-note/sec_validation.tex`
- `docs/analysis-note/sec_execsummary.tex`
- `docs/analysis-note/sec_intro.tex`
- `docs/analysis-note/sec_summary.tex`
- `docs/analysis-note/app_statmethods.tex`
- `docs/analysis-note/main_note.tex` (abstract only; added for review finding F1 about 20:22Z, written by the same command that made the edit, immediately before it, so not a separate prior commit)
- `KNOWN_ISSUES.md`, row 88 only
- `docs/publication/CLAIMS-20261005-claim-to-evidence.md` (a dated status section only)
- `docs/publication/submission/PACKAGE-MANIFEST-20261006.md` (a dated status note only)
- `Q/publication/` (this report and its minimal evidence)
- `docs/orchestration/CATALOG.md` (one route row), `docs/orchestration/MANIFEST-overrides.tsv` (one
  row), `docs/orchestration/MANIFEST.tsv` (regenerated from source only)

Standalone `MINERvA-OmniFold-Analysis-Note`: the same `docs/analysis-note/` files, on a new branch
`sync-publication-correction-20261009` in a new isolated worktree.

Not touched: frozen audits, receipts, `publication/release/preservation/`, other lanes' `Q/` subtrees
and reports, scientific registers other than KI-88.

## 1. Pinned inputs

| input | identity |
|---|---|
| ruling | `Q/closeout/REPORT.md` §11 (Joseph, 2026-10-09), at base `5ac9706a` |
| proposed wording | `Q/closeout/REPORT.md` §4 |
| estimator identity, seeds, comparisons | `docs/orchestration/ASSESSMENT-20261008-2d-estimator-pairing.md` §§1–3, 5, 8; `state/uncertainty-preparation-20261008/a/pairings.tsv` (`P01`, `P02`, `P04`, `P07`, `P09a`, `P09b`, `P14`); `a/verification.md` central-value table |
| independent recomputation of those numbers | `state/uncertainty-preparation-20261008/e/recompute/rc_pairing.json.txt` (`seed1 vs exact` 0.966 % / 1.2995; `seedmean vs exact` 0.987 % / 5.147; `blocksum_median_rel_pct_den_exact_central` 6.8269) |
| scope limits | `docs/orchestration/DELIVERY-20261008-uncertainty-preparation.md` §§1, 6; `KNOWN_ISSUES.md` 84, 85; `VALIDATION_LEDGER.md` VL169, VL170, VL172 |
| standalone base | `MINERvA-OmniFold-Analysis-Note` `origin/main` `ad3fb8000a8d373a796856bdbc4c050b9970fc30` |

## 2. What changed, by passage

Commits: `fbabeead` (correction), `2b4dc8ff` (restores a sentence a new source comment had absorbed;
found by reading the rendered note), `b7f4c065` (review repair batch), `11c753b7` (re-review N1 and the
preserved review).

| ruling item | where | change |
|---|---|---|
| 1. estimators distinct; transfer unmeasured; not shown wrong | paper estimator list and §IV.B; paper conclusions; note `sec_method` backend paragraph, `sec_systematics` intro, `sec_results` budget, `app_statmethods` (variance-source table, block sum, combined χ², summary table); exec summary; note abstract; `sec_intro`; `sec_summary`; primer trust check | §4's two passages applied in substance. "matched-central-value systematic universes" (paper), "backend-matched to production" and the universes' "central estimator seed" (note) read as statements about the quoted central value; they are replaced. The note says the transfer is "not a demonstration that the quoted uncertainty is wrong" |
| 2. "pinned seeds" | `sec_method.tex` (§3.2) | Replaced by `P01`'s provenance: no seed passed, no seed option at `d1bc8813`, `random_state=None`, inferred from launcher and revision (the run log was not found); exact-split seed noise unmeasured. The paper's 2D central item says "with an unpinned seed" |
| 3. the 0.97 % / 1.3 comparison | paper §IV.B; note §3.2; `app_statmethods` methodological paragraph; primer ("about one percent") | Identified as LightGBM seed 1 vs exact; σ is the per-bin standard deviation of the `VL170` statistical block. Not paired with the seed-42 systematics. No integrated ratio is quoted (it is lane A's only, not reviewed). Added numbers: 12.5 % maximum; 0.99 % and "about five" σ_ML (ten-seed mean vs exact); 6.827 % (block sum over the exact central). Each is in A's evidence and the 2026-10-08 reviewer's recomputation |
| 4. consistency sweep | coverage section (`sec_validation`), its scope list, paper KI-85 sentence, primer coverage paragraph, `app_statmethods` "little central-value change" and block-sum independence | The coverage toys used "the statistical band's estimator", not "the production estimator"; the fixed-truth test "tests the LightGBM statistical estimator". The KI-85 diagnostic is "on pseudo-data drawn from the same simulated events … neither an independent-population coverage test nor a real-data calibration". The primer now says the failed coverage test was of the band as first built and the quoted rebuilt band is not re-tested. The seed-1 / seed-42 block sum is unmeasured at the covariance level (`P07`). The unsourced "seed-ensemble mean … agrees with the production single-run CV to 0.28 %" is replaced by the measured 0.99 % (5.1 σ_ML) |
| 5. KI-88 | `KNOWN_ISSUES.md` row 88 | Interim disposition, Joseph's endpoint quoted verbatim, the actions not authorized, route to closeout §11. Status stays **OPEN**. The row now names the seed-1 central and the `VL170` denominator |
| records | `CLAIMS-20261005` §H; `PACKAGE-MANIFEST-20261006` 2026-10-09 note and §5 | L2/L4 statuses and a "not publication-ready" row. The manifest's §2 "No scientific or provenance item remains open" is marked superseded |

Preserved: every number, band, adoption, figure, `values.tex`, receipt, audit and
`publication/release/preservation/`. The abstract of the paper is unchanged (it already names
statistical-coverage limitations; the disclosure is in the body and conclusions). Not applied: the
closeout's optional 6.83 % denominator in the paper (reviewer F6, DECLINED-OK); it is in the note.

## 3. Builds and synchronization

| check | result |
|---|---|
| canonical `build_all.sh` at `11c753b7`, clean tree | rc 0; `RESULT :: PASS … head=11c753b7 tree=clean`; containment self-test PASS (17 perturbations rejected); `SEC4-RECEIPTS :: PASS (14/14)`; note 123 pp, primer 9 pp, paper 11 pp (base: 123 / 9 / 11) |
| unresolved references | none in any log; no `??` in `pdftotext` of any PDF |
| PDF sha256 (include build date; not reproducible byte for byte) | note `1c1e36ae…`, primer `467cfb4a…`, paper `9c8f96e8…` |
| rendered inspection | word-level `pdftotext` diff of each PDF against the base build: only the intended passages and reflow change. It found the absorbed "third backend" sentence in `fbabeead`, repaired in `2b4dc8ff`. An intermediate paper build ran to 12 pp (two references); the paper additions were compacted to 11 pp without dropping content required by the ruling |
| standalone | branch `sync-publication-correction-20261009`, commit `6a7fa2f20c3404695623a77279ca1ab3c5867003`, from `origin/main` `ad3fb800`, in its own worktree; eleven files copied from `11c753b7`. Blob comparison after the copy: every tracked file equals canonical `11c753b7:docs/analysis-note/` except the standalone's own `.gitignore` and `AGENTS.md`. `build_all.sh` rc 0, PASS (`head=unknown` and the SEC4 skip are the documented standalone fallbacks), 123 / 9 / 11 pp; `pdftotext` of all three PDFs identical to the canonical build. Overleaf target `latexmk -jobname=output main_paper.tex`: rc 0, 11 pp, 0 undefined (products removed) |
| remote heads (`git ls-remote`, 2026-10-09T20:31Z) | `MINERvA-OmniFold-Analysis-Note`: `sync-publication-correction-20261009` = `6a7fa2f2…`; `main` = `ad3fb800…` (unchanged, because the canonical PR is unmerged). `MINERvA-OmniFold`: this branch = the commit carrying this report; `main` = `5ac9706a…` |

## 4. Other checks

| check | result |
|---|---|
| pre-commit hook (13 checks) on each of the five commits | 13 passed each time; `Checks` trailer present |
| `verify_hash_bindings.py` | `ALL BINDINGS INTACT` |
| `generate_manifest.py --check` | OK after regeneration from source in the report commit |
| note tests `test_build_all.py`, `test_check_sec4_receipts.py` | 53 passed |
| links (`Q/closeout/checks/linkcheck.py`) on KNOWN_ISSUES, CLAIMS, PACKAGE-MANIFEST, CATALOG and this report | 65 unresolved, all pre-existing (the same 65 at the base); 0 new |
| diff scope | `git diff --stat 5ac9706a` lists only the claimed files, `Q/publication/` and the generated manifest |

Pre-existing and not touched here: the `OI-136` ratchets (KNOWN_ISSUES 89; no `.py` changed); the 65
unresolved catalog/register links.

## 5. Independent review

- **Reviewer.** One fresh Claude Code general-purpose subagent, with no authorship of this correction or of A–E. Its model is inherited (Opus 5.5) and its effort is not observable. CAMPAIGN-REVIEW §5 suggests Astra High, which this session cannot reach.
- **Setup.** A detached worktree in scratch. Its own code was used for every number. The status was empty at start and end, and the worktree was removed. Nothing was edited or messaged.
- **Preserved verbatim.** [`review/review.md`](review/review.md) sha256 `e26dae9b…`; [`review/review-cycle1.md`](review/review-cycle1.md) `3b25f4c6…`; the reviewer's script [`review/check_numbers.py.txt`](review/check_numbers.py.txt) `a62ae474…`.

| cycle | fixed commit | verdict | findings |
|---|---|---|---|
| initial | `2b4dc8ff` | PASS WITH CHANGES | 0 material. F1–F5 minor (note abstract unqualified; 6.83 % beside 6.830 %; √Tr is not a ratio; "little central-value change"; the paper lacked the unpinned seed and CLAIMS said "complete"). F6–F11 notes |
| focused re-review | `b7f4c065` | **PASS** | F1–F5 and F7–F11 RESOLVED; F6 DECLINED-OK; new N1 NOTE ("vary that seed") |

**After the final review**, N1 was applied as a one-line edit in `11c753b7`. **It is not independently reviewed.** No further cycle is permitted.

## 6. Disposition

| decision | disposition | reason |
|---|---|---|
| paper, note and primer factually consistent about the frozen central estimator, the uncertainty estimators, seed provenance and unmeasured transfer, without a readiness claim | **PASS** | §2 corrections; reviewed PASS on re-review; three builds and the standalone synchronization pass (§3) |
| KI-88 records the interim disposition and stays open | **PASS** | §2 row 5 |
| publication-ready measurement | **NOT ACHIEVED** | The disclosure leaves the transfer unmeasured (`P03`, `P05`, `P07`, `P09b` UNRESOLVED). `VL170` coverage is not re-tested (KI-85 deferred). Joseph's endpoint (§11) is not met. This PASS does not authorize submission, adoption, a LightGBM re-quote, transfer experiments, N2, a KI-85 lift, changed gates or reopening terminal campaigns |

## 7. Resources

| item | measured |
|---|---|
| active time | about 0.6 h (about 19:56Z to 20:35Z), including review; cap 6 h |
| local CPU | about 0.12 core-h: ten full builds at about 35 s user each (one base, six branch, three standalone), about six single-paper builds, tests (32 s), hash bindings (7 s); reviewer under 0.02 core-h. At most 2 threads per command (two builds once ran concurrently); cap 4 core-h |
| peak RAM | about 0.13 GB (build maxRSS); cap 8 GiB |
| scratch | about 0.86 GB: a 415 MB detached base worktree for the comparison build, the reviewer's worktrees (removed), and text extracts; the standalone worktree is 14 MB; cap 3 GiB |
| tracked evidence | about 24 KiB (`review/`) plus this report; cap 10 MiB |
| cluster / GPU / training / event loops / toys | 0 / 0 / none / none / none |

## 8. Remaining scientific blockers and next decisions (Joseph's)

1. **Merge.** Whether to merge this PR. The standalone branch should follow it to standalone `main` on merge, and whichever branch merges second regenerates `MANIFEST.tsv`.
2. **The pairing itself stays open** (KI-88). The ways to the stated endpoint are the ones in DELIVERY §6:
   - measure the transfer: `P03` about 34–39 node-h at N = 50, and all three about 170–350 or 330–510 node-h, after a design with declared observables and tolerances;
   - or change the quoted central estimator.
   Neither is authorized.
3. **`VL170` coverage** is not re-tested; the KI-85 held-out re-test is deferred until after the publication package.
4. **Other open items** unchanged by this correction: the OI-136 ratchets (KI-89), the PPFX identity receipt (KI-91), the ordinal mask alignment (KI-90), and the article's own author inputs (PACKAGE-MANIFEST §4).

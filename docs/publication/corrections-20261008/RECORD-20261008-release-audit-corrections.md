# Corrections to the PRD article and its release, from the release audit (2026-10-08)

**CITABLE FOR:**
- what this pass changed in the article, the note and the release, and why;
- the RC5 identity and how it is built and verified;
- the CFS preservation of RC4 and of the audit's supporting products;
- the AnaTuple inventory and its costed plan;
- the disposition of each audit gap, G1–G13.

**NOT CITABLE FOR:**
- any change to a frozen decision, gate, label or physics number (none was made);
- a release, deposit, tag or submission;
- closing `OI-130`, whose broader inventory this article pass does not cover.

| | |
|---|---|
| authority | Joseph, 2026-10-08 (goal "Resolve the actionable findings in the PRD release audit…"): preserve RC4 and about 38 GB of supporting products on CFS within the 3 TB rule; correct substantiated documentation, citation, dependency, figure-label and wording errors; prepare a new RC with documented dependencies and a reproducible packaging command; commits, pushes, a reviewable PR (unmerged) and the standalone-note sync; one fresh read-only independent reviewer, at most two review/repair cycles |
| baseline | `origin/main` `fec438db5d6e313f110879a749381bb189b2a384` (fetched 2026-10-08), worktree `MINERvA-OmniFold-prd-fix-20261008`, branch `fix/prd-release-audit-corrections-20261008` |
| findings inventory | the audit at `ea939701` (branch `audit/prd-release-repro-20261008`, `docs/publication/audit-20261008/`). Each finding was rechecked against its canonical source before acting (§3). |

## 1. Campaign-review choice (`CAMPAIGN-REVIEW-20260929.md` §1)

**Decision answered.** Which audit findings are real, and for each real one: is it fixed and verified, or what
exactly blocks it? A finding that is disproved, or blocked with a concrete cause, is a valid terminal outcome.

**Ownership and review.**
- The owner is this session (Opus 5.5): it implements and records.
- The independent reviewer is one fresh session that Joseph started ("minerva-omnifold-f9"). It is read-only, works
  in a detached worktree at a fixed implementation commit, reproduces the consequential checks, and verifies the
  preservation receipts.
- The review campaign's recommended Astra High reviewer is not available here. Joseph supplied the reviewer.

**Budget and stop.**
- No cluster jobs. The CFS copy and hashing ran on a data-transfer node; the builds and replays ran locally.
- At most two review/repair cycles, then stop.
- Proxy-rate provenance and AnaTuple preservation are not fixable within this authority. They end as decision
  requests (§6), not as further work.

## 2. Preservation (G1, G3, G9)

**Directory:** `/global/cfs/cdirs/m3246/josephrb/prd-release-preservation-20261008/`. Its README, committed at
`publication/release/preservation/README-prd-release-preservation-20261008.md`, lists the contents, the exclusions and
the recovery commands.

| step | measured |
|---|---|
| capacity before | `du -s --block-size=1G /global/cfs/cdirs/m3246/josephrb` = **1,522 GiB** (1.63 TB, decimal; 2026-10-08 15:15 UTC), against the 3 TB rule; the copy adds 42.4 GB |
| RC4 | `rc4/minerva-omnifold-article-release-rc4.tar.gz`, copied by `scp -p` from the publication session's scratchpad; `sha256sum -c` gives **`46f801bf05bbd18d1fcfe8c8bf5b0e361cd8e352211de641b434547be1680e88` OK**. RC4 is unchanged; its original also remains where it was. |
| RC5 | `rc5/minerva-omnifold-article-release-rc5.tar.gz`, `67847088…` OK (§7) |
| inventory (source) | `preserve_prd_evidence_20261008.sh inventory` on `dtn01.nersc.gov`: **16,239 files, 42,395,379,463 bytes**, each hashed at the source. `SOURCE-INVENTORY.tsv` sha256 `9139cb1e…` (committed gzipped as `publication/release/preservation/SOURCE-INVENTORY.tsv.gz`); per-source counts in `SOURCE-SUMMARY.tsv` |
| symlinks | 161 source symlinks, recorded in `SYMLINKS.tsv` (`903433b0…`) and not copied. 160 are the floor ensembles' slab links into `mii/member_k00{0000,1200}/uq_5d/uthrow_slabs_5d_sb/`, whose 80 targets are preserved; one is the relative `figs/repo/orchestration -> docs/orchestration`. The inventory refuses if any resolved target is not preserved. |
| copy | `rsync -a --files-from=… /global/ $DEST/`, rc 0. Sources were only read. The first attempt used `/` as the transfer root; rsync's sender refused the symlinked `/pscratch` component for every file, and no data was transferred. The script now uses `/global/`. |
| verify (destination) | `sha256sum --quiet -c SHA256SUMS` over the destination: **all 16,239 files match the source inventory** (`VERIFY-RECEIPT.txt` `7538ba0c…`, finished before 2026-10-08 15:47:52 UTC; script sha256 `36102352…`) |
| spot identities in the inventory | z-cv `3d7465f6…`, projection `835828bf…`, figure arrays `72394a2b…`, frozen and union sufficient inputs `7bd019c6…` / `6ffed091…`, W2 unfolds `df11bfd8…` / `36313201…` / `ec5dc97d…`, VL170 band `71a75821…` / `077912e3…`, 4D product `1fb82508…`, F2 delta `4fed1dc6…`: all present |
| capacity after | the same `du` = **1,561 GiB** (1.68 TB, decimal) at 15:53 UTC, after the copy (the 15.7 MB RC5 tarball, added at about the same time, is within the rounding); under the 3 TB rule |

**Excluded** (see the README):
- the W2 shifted event-loop, lateral and merged outputs (about 32 GB);
- code snapshots already in git;
- the s5p products, already on CFS in `s5p-archive-20261006`;
- the AnaTuples (§6).

No HPSS copy was made: Joseph authorized CFS only. The trunk `z-cv.npz` now has two durable copies, the CFS
directory and the home epoch. The s5p archive still has one, on CFS.

## 3. Findings rechecked against their canonical sources

| finding | recheck | outcome |
|---|---|---|
| U03 "fitted exponent 0.000" | `seed_effect_exponent.py`, on the committed `SEED-EFFECT-20260920.json`: least squares over the three means gives **−0.0144**, and over all seven points −0.0130. The two-point 40→80 exponent is 0.0003. | Confirmed. The exponent was redundant with the three printed values, so it was **removed** from the paper and the note. The macro stays defined, marked retired. |
| J09 "unweighted (L2) norm" | `m1_f2_norm_ratio.py`, on the eight pair-difference products. Their digests match the committed receipts `state/s5p/stage3/{m1,f2}/*.json`. The relative L2, ‖D_M1/f_mid‖/‖D_F2/f_coarse‖, gives 0.759 / 0.857 / 0.542 / 0.504, which matches the recorded `campaign-state.json` m1 row (0.76 / 0.86 / 0.54 / 0.50). The raw L2 gives 0.784 / 0.576 / 0.346 / 0.496. | Confirmed. The text now reads "the L2 norm of the per-cell relative changes", and RC5 recomputes the range. |
| J10 0.45–0.76 proxy rate | Its only sources are the A7 `claims.rejection` text and `REVIEW-20260927` item 4, whose own printed proxy numbers give 0.52, 0.875, ≈ 0 and 0.45–0.73. No recorded operand reproduces it. | Confirmed **unresolved provenance**. The article now calls it "a design-review value whose calculation is not recorded". No derivation was invented, and the κ scan is not presented as validating convergence. |
| R05 "about 11%" | `publication/w2/w2b_statistic_shift.py`, on the committed evaluations: **0.1095**, MnvTune total at +4 %, T 2852.305 → 2539.914, baseline the frozen observed statistic. Against the unscaled re-unfold it is 0.0970. | Confirmed. The baseline is now recorded (W2B addendum), and the article says "from their frozen values". |
| C04 Ascencio caveat | `VALIDATION_LEDGER.md` Ascencio entry (fourth caveat, OI-59 open); `docs/EAVAIL_DEFINITION.md` §2 (−10.99 % out of truth bin 1) and §4; our definition read from `CVUniverse.h:361-374`; Ascencio's Eq. 1 read in arXiv:2110.13372 | Confirmed. The disclosure was added to Sec. V. |
| V13 2σ window | `rescore_vl169_toys_vl170.json`: C2 0.9769 [0.9737, 0.9800], window [0.9281, 0.9722] | Confirmed. The text now says both fractions are above their windows. |
| V14 "cause is untested" | `KNOWN_ISSUES.md` row 85: the 2026-10-07 diagnostic is descriptive, consistent with closure-toy under-scatter, and the held-out re-test is deferred | Partly confirmed. The text now says the cause is not established and names both the diagnostic and the missing test. |
| V19 16–31 % scope | VL154 A4: candidate R (the joint-test estimator), the maximum over the 42 (E_avail,W) cells for the withheld shapes (16.4 % and 31.3 %), 20 of 42 cells within σ | Confirmed. The estimator and the cell set are now named. |
| C14 "slightly above" | From the RC4 figure arrays: GENIE CV +9.4 %, GENIE+MEC +11.8 % at 1.4 ≤ W < 1.8 GeV | Confirmed. The text now reads "9–12 % above", bound to macros that `fig_numbers.py` checks. |
| M03 "about fifteen-fold" | `negweight_bias_ratio.py`, on `d1_summary.json` and `dev_receipt.json`: the largest biases give 4.11 % → 0.241 % (**17.0×**); the per-cell ratios are 6.9–36.8 (the 6.9 is the catch cell, EW41) | Wording kept: it states the ratio of the maxima conservatively. The calculation is now committed. |
| D03 ⟨E_ν⟩ ≈ 6 GeV | arXiv:2106.16210, title "at ⟨E_ν⟩∼6 GeV" | Confirmed. The citation was added. |
| D02 1.057e21 POT (not an audit finding; checked while reading 2106.16210) | Published: 10.61×10²⁰. This analysis: 1.057394e21, from the analysed files' summed `dataPOTUsed`, with an independent hadd POT check (`AUDIT-FINDINGS-20260820`) | No change. The article quotes the exposure of the files it analysed (an earlier production). The 0.35 % difference is recorded here only. |
| DA2 dependencies | RC4 replayed with exactly numpy + scipy: `VERIFY: FAIL` (no matplotlib) | Confirmed. Fixed in RC5 and in the article. |
| DA3 outside-reader replay | `RC1-REPLAY-RECEIPT-20261006.md` covers RC1 only | Confirmed. The article now says a replay from an empty directory reproduces every value, and that an *earlier candidate* was replayed by an independent reader. |
| DA6 "file identities recorded with the release" | RC4 contains no AnaTuple identities | Confirmed. RC5 ships names, sizes and mtimes, and the article now says "names and sizes, but not checksums". |
| L01, L02, R01, R03a literature | §5 | Confirmed verbatim against the original publications. |
| A7 internal inconsistencies (200 vs 194; ~0.05 vs 0.068) | `contract-amendment-7-production-admission.json` `calibration.metric` vs `metric_frozen.n`; condition 4 vs the pre-freeze summary | Confirmed. The contract is frozen and is not edited. The article follows the measured values (194; 0.07, from 0.068). Recorded here. |

## 4. What changed

**Article** (`docs/analysis-note/paper_body.tex`, `values.tex`):
- **Sec. II:** a citation for ⟨E_ν⟩ ≈ 6 GeV.
- **Sec. IV.B:** the rescored C1/C2 are both above their windows; the cause of the excess width is "not established",
  with the diagnostic and the missing held-out test named.
- **Sec. IV.C:** the 16–31 % names the joint-test estimator and the (E_avail,W) cells.
- **Sec. V:**
  - the Ascencio truth-definition disclosure;
  - the generator-context and Fig. 2 ratios are now `values.tex` macros;
  - Fig. 3's "slightly above" becomes "9–12 % above".
- **Sec. VI.B:**
  - the norm is described as the L2 norm of per-cell relative changes;
  - the proxy rate is "a design-review value whose calculation is not recorded".
- **Sec. VI.C:** W1 uses the ensembles with the recovered pseudo-experiments included.
- **Sec. VI.E:** "about 11 % from their frozen values".
- **Sec. VII:** the redundant fitted exponent is removed.
- **Sec. VIII:**
  - the dependencies are numpy, scipy and matplotlib;
  - the AnaTuple names and sizes, but not checksums, are recorded with the release;
  - the L2 ratios of condition (i) are now recomputable;
  - the empty-directory and outside-reader statements are corrected;
  - the source comment points to RC5 and to the preserved RC4.
- **Source comments:**
  - the pion-FSI and Ascencio routes (they were cited as VL159/VL160);
  - the W2 and κ routes;
  - "on branch" corrected to "on main".

**Note** (`sec_eavailw.tex`): the same redundant fitted exponent is removed. No other note or primer text changed.

**Records:**
- the W2B report addendum (R05);
- `CLAIMS-20261005-claim-to-evidence.md` §F;
- `PACKAGE-MANIFEST-20261006.md` §1c;
- the calculations in this directory: `seed_effect_exponent.py`, `m1_f2_norm_ratio.py`, `negweight_bias_ratio.py`,
  and `publication/w2/w2b_statistic_shift.py`.

**Release:**
- `build_rc.py`, a byte-reproducible packager;
- `requirements.txt`;
- `verify_rc.py`: condition-(i) ratios, M1-shift identity, figure-step error output;
- `fig_numbers.py`: printed values bound to macros, including the new 9–12 % check;
- `make_figs.py`: the Fig. 1 label;
- `RC5-README.md`, with corrected citation routes (the covariance-status JSONs, VL146, the FSI summaries);
- `test_release_tools.py`.

## 5. Literature claims checked against the original publications

The arXiv API records and the two full texts were fetched on 2026-10-08. The PDFs were read with `pdftotext`.

| claim | publication | verbatim support |
|---|---|---|
| H1: eight observables (L01) | arXiv:2108.12376 abstract | "…OmniFold, which considers eight observables simultaneously in this first application" |
| ATLAS: twenty-four Z+jets observables (L01) | arXiv:2405.20041 | title: "A simultaneous unbinned differential cross section measurement of twenty-four $Z$+jets kinematic observables…" |
| three-dimensional data measurements (L02) | arXiv:2203.08022; 2307.06413; 2603.06718; 2606.00745 | "the first measurement of the triple-differential cross section"; "unfolding to a three-dimensional measurement"; "the first measurement of the triple-differential … cross section"; title "Comparisons of triple-differential cross sections…" |
| ⟨E_ν⟩ ≈ 6 GeV (D03) | arXiv:2106.16210 | title "… at $<E_ν>\sim6~GeV$ on hydrocarbon"; abstract "peak neutrino energy of approximately 6 GeV" |
| hadronic-energy uncertainty rises to 10 % at 0.9 < q3 < 1.2 GeV (R01) | arXiv:2110.13372 (PRD 106, 032001), Sec. VI | "The hadronic energy uncertainty varies throughout the distribution and rises to 10% at high 0.9 < q3 < 1.2 GeV. The input uncertainty is determined from hadron calorimetry data taken with a test beam detector" |
| Ascencio E_avail definition (C04) | arXiv:2110.13372, Eq. 1 | "Eavail = Σ Tproton + Σ Tπ± + Σ Eparticle … Eparticle is the total energy of any other final state particles except neutrons. The definition excludes a nucleon mass from strange baryons." |
| test beam: p, π, e at 0.35–2.0 GeV/c; agreement better than 4 % (R03a) | arXiv:1501.06431 (NIM A 789, 28) abstract | "samples of protons, pions, and electrons from 0.35 to 2.0 GeV/c momentum … agreements better than 4% for the calorimetric response" |

The PDF digests are `d50f142a…` (2110.13372) and `1914c811…` (1501.06431).

## 6. AnaTuple inventory and identity/preservation plan (G4)

**Exact inventory** (metadata only, no reads of file contents): `anatuple-inventory-20261008.tsv` in this directory,
also shipped in RC5 as `data/anatuple-inventory.tsv`.

| part | files | bytes |
|---|---:|---:|
| `Data/Playlist1{A–G,L–P}` | 1,818 | 989,532,713,730 (0.99 TB) |
| `MC/StandardMC` | 489 | 10,533,960,141,421 (10.53 TB) |
| `MATFluxAndReweightFiles`, `MParamFiles` | 67 | 163,363,441 (0.16 GB) |
| **total** | **2,374** | **11,523,656,218,592** |

- Every one of the 2,307 AnaTuples that the analysis's committed playlist manifests reference
  (`2d-unfolding/playlist_manifests/MEFHC_{Data,MC}.txt`) is present. The 67 others are the flux, reweight and
  parameter files.
- The 2026-08-13 integrity receipts (`opendata-input-integrity-*.json`, 2,365 files structurally complete) predate
  this list; they record completeness, not per-file identities.
- No symlinks.
- mtimes are UTC from `TZ=UTC find -printf`.

**Measured costs** (`dtn01.nersc.gov`, 2026-10-08):
- single-stream `sha256sum` read 531,036,017 B (one data file) in 0.63 s, and the first 4 GiB of one MC file in 4.0 s:
  about 0.85–1.1 GB/s;
- HPSS: 347.90 GiB used of 512.00 GiB (`hpssquota`, 15:33 UTC), so about 164 GiB free;
- CFS: 1,561 GiB (1.68 TB) of the 3 TB rule after this pass.

**Plan and decision request** (not executed, beyond the inventory: none of it is within the existing authority as a
storage commitment):

| option | scope | cost | what it buys | blocker |
|---|---|---|---|---|
| A. checksum identity | sha256 of all 2,374 files on a DTN, committed as a manifest | about 3.2 h single-stream at the measured rate, or about 1 h with 4 parallel streams; DTN time, no allocation charge; it reads 11.5 TB, which also resets the files' access times | per-file identity of the analysed production (what DA6 lacks) | Joseph's go-ahead for the full 11.5 TB read (the goal forbade an uncosted sweep; this costs it). A data-only subset (0.99 TB, about 17 min) is the cheap first step. |
| B. durable copy of Data + auxiliary | 1,885 files, 0.99 TB, to CFS | CFS goes from 1.68 TB to about 2.67 TB (decimal), under the 3 TB rule but tight | the data side of the event-level reproduction survives a pscratch purge | a storage commitment of about 1 TB: Joseph's decision |
| C. durable copy of MC | 489 files, 10.53 TB | exceeds the CFS rule; needs about 10 TiB more HPSS than the 164 GiB free (an allocation request to NERSC) | the full event-level reproduction chain | an external allocation request (Joseph) |
| D. upstream retention | ask MINERvA/Fermilab whether this older production is retained under a version tag | none on our side | could replace B and C | an external contact (Joseph) |

**Recommendation:** A (data-only first, then full) and B now; then C or D, depending on the answer to D.

## 7. RC5

| | |
|---|---|
| identity | **`minerva-omnifold-article-release-rc5.tar.gz`**, sha256 **`6784708827e8337c7d3f7774e0fb727c24613ed7eb0db4cadf101fc6413124be`**, 15,741,965 B, 32 files (`docs/publication/release/RC5-SHA256SUMS.txt`, `RC5-README.md`) |
| relation to RC4 | RC4 (`46f801bf…`) is unchanged and preserved on CFS. RC5 has a new identity. Its three data files are byte-identical to RC4's (checked against `RC4-SHA256SUMS.txt` by the builder); the code, README, requirements and expected macro files differ; `data/m1f2/` and `data/anatuple-inventory.tsv` are new. |
| packaging command | `python3 publication/release/build_rc.py --payload <extracted RC4> --payload-sums docs/publication/release/RC4-SHA256SUMS.txt --name minerva-omnifold-article-release-rc5 --out <dir>`, run at this record's commit |
| reproducibility | two independent builds gave the same sha256, `67847088…` (`cmp` identical) |
| empty-directory verification | fresh `python3.11 -m venv` and `pip install -r requirements.txt` (numpy 1.26.4, scipy 1.15.2, matplotlib 3.11.2 and their pinned dependencies); `env -i … python -I code/verify_rc.py` from an empty directory: **`VERIFY: PASS`, rc 0, 177 s**. Every replay AGREE (0 differences); W1 0/0; FIG NUMBERS PASS; Figs. 1–4 regenerated (Fig. 1 prints "This work: 6.87%"); condition (i) ratios 0.504–0.857 against the printed 0.50–0.86; M1 shifts identical to the frozen d1, 4/4. Afterwards all 32 checksums are OK (the run adds only `code/__pycache__`). |
| durable copy | `/global/cfs/cdirs/m3246/josephrb/prd-release-preservation-20261008/rc5/` (`sha256sum -c` OK) |
| tests | `publication/release/test_release_tools.py` (byte-reproducibility and normalization; relative vs raw norm; exponent fit) plus the existing replay and W1 tests: 12 passed |
| a defect caught by this verification | the first RC5 build failed its Fig. 1–3 step, because a `\uqMedian` in `make_figs.py`'s docstring was read as a `\u` escape. It was fixed, and `verify_rc.py` now prints a failing figure step's error. |

## 8. Disposition of G1–G13

| gap | disposition | evidence |
|---|---|---|
| G1 RC4 not durable; no reproducible packager | **Fixed and verified.** RC4 is on CFS with its original digest. A byte-reproducible packager now exists and was demonstrated by two identical builds. RC5 is on CFS. RC4 itself cannot be rebuilt byte for byte (it predates the packager); its exact bytes are preserved instead. | §2, §7 |
| G2 undocumented matplotlib | **Fixed and verified.** RC5 README and `requirements.txt`; the article says "numpy, scipy and matplotlib"; RC5 passes from an empty directory with exactly `requirements.txt`. | §7; `paper_body.tex` Sec. VIII |
| G3 pscratch-only supporting products | **Fixed and verified** for the audit's identified set: 16,239 files, 42.4 GB, every destination file matched against its source hash. Excluded, and recorded in the README: the 32 GB of W2 shifted event-loop and lateral outputs. The receipts that name pscratch paths are not rewritten; the preservation README maps every source path to its CFS copy. | §2 |
| G4 AnaTuples: no identities; pscratch-only | **Unresolved; blocked on Joseph's decision.** Done: the exact inventory (2,374 files, 11,523,656,218,592 B; names, sizes, UTC mtimes), shipped in RC5; the article now says "names and sizes, but not checksums"; costs measured. Blocked: the checksum sweep (about 3.2 h DTN, a full 11.5 TB read) and any durable copy (0.99 TB within the CFS rule, or 10.5 TB beyond both the rule and HPSS headroom) need Joseph's storage decision and, for C/D, an external request. | §6 |
| G5 "fitted exponent 0.000" | **Fixed and verified.** Removed from the paper and the note; the calculation is committed (−0.0144) and tested. | §3; `seed_effect_exponent.py` |
| G6a norm description | **Fixed and verified.** "The L2 norm of the per-cell relative changes"; the producer is committed; RC5 recomputes 0.504–0.857 and checks the printed range. | §3, §7 |
| G6b 0.45–0.76 proxy rate | **Unresolved: provenance.** No recorded operand reproduces it; the reviewer's own printed proxy numbers do not match it. The article now discloses that its calculation is not recorded, and the κ scan is not presented as testing it. Blocker: the design review's computation was never committed and cannot be reconstructed from the record. Only its author, or a new pre-registered measurement (a new study, not authorized here), could resolve it. | §3 |
| G7 "about 11%" unreceipted | **Fixed and verified.** W2B addendum and `w2b_statistic_shift.py`: 0.1095 against the frozen observed statistic (MnvTune total, +4 %, 2852.305 → 2539.914). | §3 |
| G8 Ascencio caveat | **Fixed.** The disclosure is in Sec. V, checked against `EAVAIL_DEFINITION.md`, the code, and arXiv:2110.13372 Eq. 1. The underlying OI-59 question (what the definitions do to the comparison) stays open, as before. | §3, §5 |
| G9 single durable copies | **Partly fixed.** `z-cv.npz` (`3d7465f6…`) now has a CFS copy as well as the home epoch. **Unresolved:** the s5p archive (2.3 GB) still has one durable copy (CFS). An HPSS copy fits the 164 GiB free, but HPSS was not authorized; this is Joseph's decision. | §2 |
| G10 citation routing | **Fixed.** Paper source comments (FSI and Ascencio routes, W2 and κ routes, "on main", RC5/RC4); RC5 README routes the covariance-status numbers to their JSON receipts and VL146; CLAIMS §F replaces §E's stale κ statement. `RC4-README.md` is left unchanged, because RC4 is preserved as it was. | §4 |
| G11 retyped literals | **Partly fixed and verified.** Sec. V's generator and Fig. 2/3 ratios are `values.tex` macros that `fig_numbers.py --values` checks; a tamper test makes it fail. **Unresolved:** Sec. IV's literals (0.674, 97.7, 78.1, 4, 0.3, 1, 1.4, 74, 16–31). Blocker: their producers are not in the release, so no release check can bind them. A build-time check against the committed receipts would be new tooling beyond this correction pass (proposed). | §4 |
| G12 regeneration from durable storage untested | **Unresolved.** Blocker: the frozen extractor takes product paths from `design.json` and from receipts nested in the frozen code, across several `/pscratch` roots. Regenerating from CFS needs a path-remap layer in that frozen read path, which is a code change outside the authorized correction categories, plus a login-node run over about 7,000 products. What changed: every input it needs now exists durably (the s5p archive, plus the jitter, lateral and asimov inputs preserved in §2). | §2 |
| G13 small items | **Fixed:** D03 citation; V13 both windows; V14 cause "not established", with diagnostic and missing test named; V19 estimator and cell set; C14 "9–12 % above" (bound and checked); W1 operand; Fig. 1 label; literature quotes verified verbatim (§5). **Receipt added, wording kept:** M03 (17.0× ratio of maxima). **Documented, not editable:** the two A7 internal inconsistencies (frozen contract; the article follows the measured values). | §3–§5 |

This pass does **not** close `OI-130`. That item is the class of untracked artifacts behind published macros, repository-wide; only the article's evidence was preserved here.

## 9. Builds, standalone sync and remote heads

| | |
|---|---|
| canonical build at `f82e6db7` (clean tree) | `build_all.sh` rc 0, `RESULT :: PASS … head=f82e6db76f20119450e7364ec2d9919c23c67db7 tree=clean`; note 123, primer 9, paper 10 pp. Overleaf target `latexmk -pdf -jobname=output main_paper.tex` rc 0, 10 pp, 0 undefined references. The PDF digests include the build date. |
| standalone before the copy | a fresh worktree of `MINERvA-OmniFold-Analysis-Note` at `origin/main` `2357c6ca4c3d5804dd22d409652128926abfa25d` equals canonical `fec438db` in all 117 tracked files except its own `.gitignore` and `AGENTS.md` (`cmp`, file by file) |
| standalone sync | the three changed files (`paper_body.tex`, `sec_eavailw.tex`, `values.tex`) were copied from `f82e6db7` to the standalone branch **`sync-prd-release-corrections-20261008`**, commit **`43c07039cdbeff47d8124f51671cd1fb4e091750`**. Standalone `build_all.sh` rc 0 at 123/9/10 pp (`head=unknown` is the documented fallback); Overleaf target rc 0, 10 pp, 0 undefined; `pdftotext` of all three PDFs identical to the canonical build. |
| why a branch, not standalone `main` | the canonical PR stays unmerged by instruction. Standalone `main` therefore stays at `2357c6ca`, equal to canonical `main`; the branch should merge together with the canonical PR. |
| remote heads (`git ls-remote`, 2026-10-08) | `MINERvA-OmniFold`: main = `fec438db5d6e313f110879a749381bb189b2a384`, `fix/prd-release-audit-corrections-20261008` = {{CANON_HEAD}}. `MINERvA-OmniFold-Analysis-Note`: main = `2357c6ca4c3d5804dd22d409652128926abfa25d`, `sync-prd-release-corrections-20261008` = `43c07039cdbeff47d8124f51671cd1fb4e091750`. |
| RC5 from a clean checkout | a detached checkout of `f82e6db7` rebuilds RC5 to `6784708827e8337c7d3f7774e0fb727c24613ed7eb0db4cadf101fc6413124be` exactly |

## 10. Independent review

{{REVIEW}}

## 11. Decisions that remain Joseph's

1. **AnaTuple identity and preservation (G4):**
   - (a) Run the checksum sweep? Data only (0.99 TB, about 17 min DTN) and then all 2,374 files (about 3.2 h);
     DTN time, no allocation charge.
   - (b) Copy Data + auxiliary (0.99 TB) to CFS? That takes CFS from 1.68 TB to about 2.67 TB of the 3 TB rule.
   - (c) For the 10.53 TB of MC: request HPSS allocation, or ask MINERvA/Fermilab whether the older production is
     retained. Both are external acts.
2. **An HPSS second copy of the s5p archive (2.3 GB) and of `z-cv.npz` (0.9 GB)?** It fits the 164 GiB free (G9).
3. **The W2 shifted event-loop and lateral outputs (about 32 GB)?** They were excluded from the CFS copy; the
   article's W2 numbers do not need them, but regenerating the shifted unfolds would.
4. **The 0.45–0.76 proxy rate (G6b):** accept it as disclosed ("a design-review value whose calculation is not
   recorded"), or authorize a new pre-registered measurement of the refinement rate. That would be a new study.
5. **Release acts** (unchanged): coauthor review of a PDF built from this commit; the deposit, which RC5 now
   supersedes RC4 for; the tag; submission.

# Agent B notes: rows C01-C14, U01-U08, L01-L02, R01, R03 (literature part)

Worktree W = $W at fec438db (git status clean, not modified).
Cluster: login32, 2026-10-08 ~07:53 UTC. Only ls/stat/find/sha256sum (<2 GB)/hsi -q ls were run. Nothing was written to the cluster.
Side effect: my sha256sum reads moved pscratch atimes to 2026-10-08 for: adopted z-cv.npz (it was 2026-09-24 before the read), PROJ/cov_5d_to_eavailW_publication.root (was 2026-09-25), z2m-floor-20260920/SEED_EFFECT.json (was 2026-09-20), products/4d/xsec_4d_MEFHC_5iter_lgbm.root (was 2026-10-03). Treat atime as a weak signal in any case.

## Consequential findings

1. **U03 exponent "0.000" is not reproduced as a fit over N=40/80/160.** SEED-EFFECT-20260920.json gives subset means 6.0243% (N40), 6.0232% (N80), and 6.1454% (N160). A least-squares fit of s ~ N^-p gives p = -0.014 on the 3 means and -0.013 on all 7 points. Only the two-point 40->80 exponent gives 0.0003, which rounds to 0.000. No committed code computes the exponent: probes/probe-20260920-seed-effect-at-matched-N.py and -sproj-resolution-floor.py contain no fit. EVIDENCE-20260920...md:22 prints `0.000` without derivation. The paper calls it a "fitted exponent" right after listing the N=160 point. The "flat" conclusion stands, but the printed 3-decimal value is wrong. Fix: print p = -0.01, or call it the 40->80 two-point exponent.
   - The nesting caution is handled correctly at paper_body.tex:676-677 ("single seed pair ... nested subsets of the same 160 throws").
2. **C04 (within 10% of Ascencio) carries an undisclosed caveat.** The ledger entry VALIDATION_LEDGER.md:1667-1697 (2026-06-10, no VL id) records ratios 1.092 and 1.063. Its fourth caveat (OI-59, still OPEN per docs/OPEN_ITEMS.md:188) says the two E_avail truth axes are defined differently: ours is the closed 4-species definition, Ascencio's is the open list. This produces a measured -10.99% migration out of truth bin 1, in exactly those cells. The paper does not mention it.
   - The 4D product behind C04 (products/4d/xsec_4d_MEFHC_5iter_lgbm.root, sha256 1fb82508…, 198,403 B) exists only on pscratch. HPSS mnv-quoted-products-20260812 holds only xsec_4d_MEFHC_ascencio_fine.root, and no copy turned up in the home epochs or on CFS.
3. **Mis-routed citations.** paper_body.tex:252 ("Sources: VL159, VL160") and RC4-README.md:123 attribute "under 1% for pion FSI" and "within 10% of Ascencio" to VL159/VL160. Neither row contains them.
   - The FSI receipts are 3d-unfolding/genie/genie_fsi_{FrAbs,FrInel}_pi_xsec3d_summary.txt. Recomputed maxima are 0.824% and 0.745%, so MATCH.
   - Similarly, RC4-README:127 cites VL142-VL144 as the authority for 6.145/6.02/20.91/7.57/26.0/1.06. Those rows hold only the digest, the projection and cause 7. The numbers live in the GRADE/SEED-EFFECT/FLOOR/CENTRAL-VALUE JSONs and the EVIDENCE docs. The control for 6.145% is VL146.
4. **Retyped literals.** paper_body.tex prints 1.07--1.39, 1.11--1.13, 1.07--1.15, 1.14--1.16, 1.61/1.39, 12--30, 23--31 as literals. fig_numbers.py:92-112 holds its own hardcoded copies and does not read paper_body. A later edit to paper_body would therefore pass verification unnoticed.
5. **U06 operand.** The movement is of each member's own CV execution (z-null.npz). It is not the adopted product's hXSecND_flat, which is a fixed archive central, identical across members by construction. VL146's "CV shift 0" refers to that other operand and does not contradict U06.
6. **C14 wording.** "Slightly above" corresponds to predictions 9.4% (GENIE-CV) and 11.7% (GENIE+MEC) above the data at 1.4<=W<1.8.
7. **C12 pairing.** The printed "1.37 against 1.29" matches the GENIE+MEC-share case (1.3746/1.2918). Across the three shares the values are 1.369-1.377 and 1.283-1.292.

## Preservation map (observed)

| artifact | where observed | verified |
|---|---|---|
| adopted z-cv.npz 3d7465f6 (890,500,272 B) | pscratch z_pilot_20260916_a5 (sha256sum = 3d7465f6…918c5; mtime 09-17, atime 09-24) **and** /global/homes/j/josephrb/evidence/repository-epochs/preparation-2026-09-24-bf34a12c/trunk-baseline/.../z-cv.npz (sha256sum = 3d7465f6) | YES, global HOME (not CFS/HPSS) |
| projection 835828bf (17,101 B) | pscratch z2m-products/PROJ (sha256sum match) + same home epoch (sha256sum match) | YES, home |
| **HPSS solecopy archive does NOT contain the adopted z-cv.npz** | `hsi -q ls -lR /home/j/josephrb/mnv-scalar5d-solecopy-20260925` lists z_pilot_20260916_a5/z-mean.npz only, plus member z-cv/z-mean, std_final5_candidate.root, z_precursor throw root, uq_cov_{mlsplit,stat}_5d.root | by design: RECOVERY-MANIFEST-20260924 marks z-cv.npz PRESERVED via the home copy; no tape or CFS copy of the adopted trunk exists |
| member z-cv.npz 361090f9 / 7e4636a3 | HPSS solecopy (sizes 887254200 / 887228520 match) + pscratch | YES (listing; restore-verified per RECEIPT-20260925-d3 @1957326e) |
| member z-null.npz ff0d8ec0 / 74444bb0 | home epoch (sha256sum match) + pscratch | YES |
| member throw roots mii/member_k00{0000,1200}/uq_5d/unified_throw_cov_5d.root (2.67 GB each) | pscratch only (mtime 09-19/09-20, atime 09-22) | NO, not inventoried |
| z2m-floor-20260920 and -k1200 (15 GB each; U03/U04 inputs) | pscratch only; committed JSONs byte-identical to the cluster copies | NO |
| std_final5_candidate.root (42.3 GB) | HPSS solecopy (size match) + pscratch (atime 09-24) | YES (listing) |
| gen5d_fluxfix npz (C08-C13 inputs) | CFS s5p-archive-20261006/gen5d_fluxfix (sha256sum of 4 files = cfa42210, c179855d, 475a2871, 48917692) | YES, CFS |
| stage7 genfig gen roots | CFS s5p-archive-20261006/stage7/genfig (genie_cv_xsec_eavailW.root re-hashed debaf83e; others in SHA256SUMS) | YES, CFS |
| xsec_5d_MEFHC_5iter_lgbm.root 630306e2 | home epoch (manifest PRESERVED; not re-hashed by me) | listing only |
| excess_eavail_W.root 751bb859 | pscratch + HPSS mnv-quoted-products-20260812 (size 6166 only) | partial |
| fig_arrays.npz 72394a2b | pscratch pub-release-20261006/figs + RC4 tarball (local). Nothing found on CFS/home-epoch (find maxdepth 4) | NO |
| 4D product 1fb82508 (C04) | pscratch only | NO |
| s5p stage-2 runs (U07) | CFS s5p-archive-20261006/runs/{prod,s2} exist (ls). pscratch s5p-20260926/stage2 does not exist | partial |

## Commands bearing on conclusions

Local (W = worktree):
- `cat $S/claims-skeleton.tsv`; `sed -n` on paper_body.tex 15-40, 236-330, 600-716; `values.tex` 340-430
- `git log -1 --format=%h -- <receipt>`: GRADE 4057bd07, SEED-EFFECT 128a5e7a, CENTRAL-VALUE-VS-SIGMA 9f85830f, EVIDENCE-20260920 15edf148, EVIDENCE-20260919 00161bf7, generator-context b1e6e3b9, note-capgap aa64878f, f1_member_check c29dde25, RECOVERY-MANIFEST d9efdf8d, RECEIPT-d3 1957326e, PREREG 44e09fd8, stage2-exit 690ff304, REVIEW s5p round1 5201eebc, PET decision bc356b0c, PET-GBDT report 1464d97c, LITERATURE/CLAIMS 82cea368, FSI summaries 971fdb55/121f88a1, fig_numbers/RC4-README f5787b32
- python recompute from SEED-EFFECT json: N40 mean 6.02428, N80 6.02323, N160 6.14539, 7-pt mean 6.0413 sd 0.388; slopes +0.0130 (7-pt) and +0.0144 (3 means), so p = -slope
- python recompute from FLOOR-*.json: N40 20.795/21.029 (6 pairs each), N80 7.661/7.473; floor exponent 1.4658
- `shasum -a 256` on committed SEED-EFFECT/FLOOR/CENTRAL-VALUE JSONs: dbc7eb2e, 78280f92, 25b40ffc, 2da97bfc (all equal to the cluster copies)
- python on GRADE json: s_proj 0.06145388143592225, limit 0.05, branch 5 NOT MET - PER-BIN; members on pscratch z2m-products
- python on CENTRAL-VALUE-VS-SIGMA: movement_over_uncertainty max 0.06022, median 0.010591
- EVIDENCE-20260919:71-78: 1.474286/5.674201 = 0.25982 (sq 0.06751)
- python on FSI summaries: FrAbs max 0.824%, FrInel max 0.745%
- python on cap_share.json: GiBUU+share corner 1.369-1.377, total 1.283-1.292
- RC4 fig arrays (`$S/run-mpl/.../data/figs/fig_arrays.npz`, sha256 72394a2b, venv-mpl python -I): edges match C07; E_avail/W marginal ratios (C01, C14) as in TSV
- read the parent's `$S/out/fig_numbers.log` (FIG NUMBERS: PASS, values quoted in TSV)
- `git grep` for exponent derivation ('exponent.{0,40}0\.000' etc.): only prose sites, no computation
- `git grep` 1fb8250820c0: only manifests/scripts, no durable-copy record

Cluster (`ssh -o BatchMode=yes -o ConnectTimeout=20 saul.nersc.gov '...'`):
1. `stat` on the adopted z-cv.npz, member z-cv/z-null/z-receipt, mii throw roots, and std_final5_candidate.root: all exist. Sizes, mtimes and atimes are in the table above. `ls -la` of z_pilot_20260916_a5 lists z-cv.npz (890500272), z-mean.npz, z-null.npz, and the receipts.
2. `sha256sum` PROJ/cov_5d_to_eavailW_publication.root = 835828bf…a54e. `sha256sum` adopted z-cv.npz = 3d7465f6…918c5 (4.8 s).
3. `ls -la /global/cfs/cdirs/m3246/josephrb`; `find ... -maxdepth 4 -name z-cv*/z_pilot*/...`: no covariance on CFS (only z_pilot*.py code). Home evidence epochs are listed.
4. `ls` s5p-archive-20261006; `hsi -q ls -l` home: mnv-scalar5d-solecopy-20260925 is present.
5. `hsi -q "ls -lR /home/j/josephrb/mnv-scalar5d-solecopy-20260925"`: no adopted z-cv.npz (see map).
6. `sha256sum` on the cluster copies of SEED_EFFECT.json, FLOOR.json (x2) and CV_VS_SIGMA.json: identical to the committed copies. `sha256sum` on home-epoch z-cv.npz (3d7465f6), PROJ (835828bf) and z-null.npz x2 (ff0d8ec0, 74444bb0).
7. `ls` z2m-floor-20260920{,-k1200}: out/{HA,HB,Q1..Q4}, 15G each. SEED_EFFECT.json atime 09-20.
8. CFS SHA256SUMS grep: gen5d_fluxfix and stage7/genfig digests are present. `sha256sum` of 4 gen5d_fluxfix npz and genie_cv_xsec_eavailW.root on CFS: match.
9. `stat` of stage7/genfig roots/logs (atime 10-06), excess_eavail_W.root, pub-release fig_arrays.npz and note-capgap cap_share.json (pscratch atime 10-03).
10. `hsi -q ls -lR mnv-quoted-products-20260812 | grep`: excess_eavail_W.root 6166 B present. products/4d holds only xsec_4d_MEFHC_ascencio_fine.root.
11. `ls` products/4d on pscratch. `stat` + `sha256sum` xsec_4d_MEFHC_5iter_lgbm.root = 1fb82508… `find` home epochs + CFS (maxdepth 7): no copy.
12. `find` CFS/home for *release-rc*/fig_arrays*: none. `ls` pub-release-20261006: figs, frozen, union, tools.
13. `ls` s5p-20260926: there is no stage2 dir. `ls` CFS s5p-archive runs: prod, s2.

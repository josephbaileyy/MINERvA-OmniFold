# Agent C notes: Sec. VI rows J01–J14, J21, J25, J26, J28, J29, R02, R03 (±4% only), R04, R05

Worktree: $W at fec438db (status clean before and after).
RC4: scratchpad/run-doc/minerva-omnifold-article-release-rc4 (SHA256SUMS still all OK after my runs; the
`code/__pycache__` there dates from 00:38, before my first run at 00:53, and I ran with `-B`).
Everything I wrote is under scratchpad: scripts/agentC_checks.py, scripts/write_agentC_rows.py,
out/agentC_checks.json, cluster-copy/m1f2/ (8 small npz copied read-only by scp), agent-C-rows.tsv, this file.
Cluster: read-only commands only (stat, ls, sha256sum, grep of the archive's files.txt/SHA256SUMS, hsi -q ls, scp read).
scp and sha256sum updated the atime of the files they read (stage3/f2, stage3/m1, a few others). No writes on the cluster.

## Commands and results

1. `sed -n 329,660p paper_body.tex`; `cat -n values_inference.tex`: printed values and macro sources.
2. A7 JSON (4f5a613f, sha 448f5764…), printed claims/calibration/metric_frozen/prefreeze_measurements:
   - claims.family (l.9): 109 / 72. MATCH.
   - claims.rejection (l.10): κ=2, "0.45-0.76 per halving … ~1-3 times", κ_robust 3. MATCH.
   - conditions (l.13–18): 0.50-0.86 L2; 5 lateral bands; 34 bands, LowQ2_1/HighQ2_1 clipped; D16 "at most ~0.05
     null SD" (the summary says 0.068, which is the source of the article's 0.07); GiBUU >20 GeV; >100 GeV negligible.
   - calibration.process (l.22): 1 of 100 PPFX universes, 34 bands, 1.4%, 20 jitters. sequential_rule (l.23): 200, 1999, 99.5% look interval.
   - calibration.metric (l.25) says "200-experiment … exactly 200 products", but metric_frozen.n (l.59) = 194 and its note
     explains the 6 lost seeds. This is an internal inconsistency; the article follows metric_frozen.
   - prefreeze summary (l.76–102): λ 450.2/317.7/6344/1711.6; M1 claim 1.65/2.0/0.55/1.65; robust 3.34/3.6/1.07/2.77; D16 0.056/0.068/0.0/0.024. All MATCH the article.
3. units.json (4f5a613f, sha 2bafa908…) has the unrounded values. Its code_sha256 1fa1ee42 equals the current s5p_prefreeze.py.
   Its inputs are runs/s3r/f2 asimovs on pscratch.
4. RC4 arrays (`np.load`, venv-doc python -I): supported_cells 109; dom__GiBUU 72 == (pz_index<=1); jitters (20,109); U (109,65856).
   Frozen B 1365/1366/1343/1751/1351; union B 1400/1400/1400/1800/1400 (seed offsets 0..1399, NuWro 0..1799).
5. scripts/agentC_checks.py on RC4 (out/agentC_checks.json):
   - J13: observed_jitter_p was recomputed for all 10 tests and equals expected/joint-evaluate.json (rtol 1e-12).
     NuWro shape has k∈{1,2} of 1751; all other tests are constant.
   - J28: union with seed offset <1200, claim k over variants, sequential_decision restated. The four nulls have k=0 and
     look-upper 0.00498 < 0.005, so the rule stops at B=1200. At B=1000 the upper end is 0.00597, so it continues.
     NuWro shape has k=1 and does not stop. Holm at 1200: all rejected.
6. Worst-interrupted scenario (J25): I used k+n_int and B+n_int with RC4 holm_determined and the interrupted counts
   22/17/25/27/20 from missing-sensitivity.json. The result is identical to the recorded scenario: all 10 not rejected, p 0.0130–0.0190.
   The sensitivity was committed (0afd9ef5) at 2026-10-05T20:43Z, before the Phase A submission at 23:37Z.
7. J09/J10: I scp'd stage3/f2/delta-<g>.npz and stage3/m1/fine-minus-mid-<g>.npz. Their shas match the committed receipts,
   and fine-minus-mid D_J is bitwise equal to RC4 d1__.
   - L2 of the fractional difference D/f_B_mean gives 0.759/0.857/0.542/0.504, which reproduces 0.76/0.86/0.54/0.50.
   - The raw L2 gives 0.784/0.576/0.346/0.496.
   - So the article's "unweighted (L2) norm" is an imprecise description.
   - The frozen-V W-norm ratios ‖d1‖/‖D_F2‖ are 0.87/0.67/0.42/0.33.
   - The reviewer's own printed proxy shifts (REVIEW-20260927:47-48) give M1/F2 = 0.52, 0.875, ~0, 0.45–0.73.
   - So 0.45–0.76 is not reproducible from any recorded number.
   - No committed producer exists for either ratio (545b2a54 added only JSON).
8. CFS archive /global/cfs/cdirs/m3246/josephrb/s5p-archive-20261006: SHA256SUMS sha 1a72cb43… re-measured; 10,612 lines.
   - Contains: runs/prod/cal 7176, pow 1147, status 47; recovery/recovery cal 224 + pow 53; recovery/determinism 16 products
     + determinism.json (66036819); recovery/stopping.json (c956beb7); stage7/joint/{joint-evaluate b9604502,
     missing-sensitivity f48e16ef, robust-labels 206655f9, seed-states}; stage3/V/V-s3v.npz (35979ef7, MATCH A7);
     stage3/m1/*, stage3/f4/*; runs/s2/num/data/data_b-_j-.npz (fb5cc679); gen5d/mnvtune_v1_xsec5d.npz;
     gen5d_fluxfix/* generator 5D histograms.
   - Absent (grep count 0): stage3/f2 (F2 deltas), runs/s3r/f2 asimovs, the 20 jitter re-unfolds data_b-_j{1..20},
     runs/s3/latunf lateral endpoints, the V pilot ensemble runs/s3v/pilot, prefreeze units/devpower, all W2 products, and the deploy.
9. pscratch stat (atime): every absent item still exists. Most were last accessed 2026-10-06; s3r/f2 and stage3/f2 at
   02:31, jitters and W2 unf at 07:1x. pilot_null has 194 files; jitters 20; latunf 12.
   W2 unf shas re-measured: rr0 df11bfd8, rr1 36313201, rrzero ec5dc97d (all MATCH the W2B report).
   The 8-week no-access purge would first hit these around 2026-12-01 if they are not read again.
10. HPSS (`hsi -q ls`): no s5p entry. "No matching names located for 's5p*'".
11. Reproduction harness reports/fresh-3a80aa74/report.json (2d3b40e0), tier B, all REPRODUCED with the same producers
    re-executed on preserved inputs: prefreeze:units, prefreeze:devpower, V:build-v (arrays V, n, names, shrinkage),
    and 17 pairdiff F2/F4/M1 arrays.
12. Independent records, all reachable from fec438db:
    - final-ext compare.json (466b427b): AGREE 1379/1379, including observed_jitter_p rows.
    - recovery crosscheck (00009056): 856/856; 16/16 determinism; does not recompute the union reading; no stopping check.
    - w2-check (9ffc4ddd): AGREE 1379/1379 ×3; 150/150.
    The article and values comments still describe these as "on branch s5p-parallel-recompute-20260928".
13. W2: committed w2b-results joint-evaluate shas match the W2B manifest.
    - rr0/rr1: 10/10 rejected, 9 with k=0; NuWro shape is k=1 (−4%) and k=3, p=0.002283 (+4%), threshold 0.05.
    - Max |ΔT/T| is 10.95% (MnvTune total at +4%, measured against the frozen data). Against the δ=0 control it is 9.70%.
      No receipt states "11%".
14. W1 (R02): W1-RECORD:31-32 and RC4 expected/W1-RESULT give 0.48323 (676/1400) and 0.62884 (880/1400). These are union-reading B values.
    The lead's verify log shows W1 with 0 differences.

## Counts by class (23 rows)
- RR: J02, J05, J13, J21, J28, R02, plus the RR part of J04 (20), J07 (α, CP) and J29 (union).
- SO: J03, J06, J08, J11, J12, J25, J26, J29 (frozen-S), R03, R04, R05.
- SO-NOINDEP: J01, J09, J14, plus part of J04.
- ME: J10.
- UP flags: J03, J04, J06, J09, J11, R03, R04, R05.

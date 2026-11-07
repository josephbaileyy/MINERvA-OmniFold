Per-period 2D benchmark, CONNECT 1: the environment receipt. Verdict: PASS (2026-11-07T06:42Z, login36).

Bound by BINDING-1.md (PR #874, on origin/main), ruling 3. Code at M = a7af2e614f2d65ca10d169e6d73582e83f9ecf1d.
connect1.sh sha256 fbf2e847a34980fee199be4999015c9ca090d54a0ae89a087d6e34dc72d6444b; the director gave GO for it.
Deploy: `git archive M` of 8 paths from a fresh clone at M (empty porcelain), sha256
bb1e00e4ed9c8ef27b9681a9daf47078b9d89d5559937104f778afd5c06c716e (4,505,600 bytes).

What it shows, with the file that holds each result:
- pins.check: the archive digest and the four BINDING-1 pins are equal on the cluster (remote1.out).
- squeue.txt: the cov2d fence held. There were 0 rows for josephrb, so no cov2d-* job was queued or running.
- env.txt: root_6_28, Python 3.11.14, numpy 1.26.4, matplotlib 3.10.8, ROOT 6.28/12.
- suite.log: "Ran 51 tests in 0.994s", OK. This is under real PyROOT, so no ROOT stub was used. The run was at nice 19,
  ionice idle, with BLAS at 1 thread.
- smoke.json: the load_all smoke test on O_NOATIME copies of the published ROOT and of ONE product (pu_PA_b01).
  - Both copies' sha256 equal INPUTS.sha256, and both source atimes are unchanged.
  - The published object has 224 bins and 205 reported cells.
  - The product is finite, and its 205 positive cells equal the published set (C-IN-cells PASS).
  - The ROOT cross section is within 3.5e-3 relative of the 3-figure text release.
  - The published TotalCovariance is not exactly symmetric (max |V - V^T| = 2.9e-98). This was printed only, as declared.
  - The first line of smoke.json is a stdout print from compare_to_paper_fullcov.flatten_th2d, not JSON.

CITABLE FOR: the read's environment, its suite pass, and load_all on real files.
NOT CITABLE FOR: any reading. No per-group comparison was computed.
0 node-h. No sbatch. Nothing written outside /pscratch/sd/j/josephrb/per-period-benchmark-20261106/connect1.

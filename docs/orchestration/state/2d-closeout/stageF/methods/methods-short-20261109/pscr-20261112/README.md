# #977 read-only pscratch session: receipt

**What ran.** One session on login27, 2026-11-12T00:08:59Z, under the director's go for exactly
`code/pscr_remote.sh` (9513d080…), `code/pscr_fetch.sh` (9401337b…) and `code/w_inventory.sha256`
(a08ae0eb…; the 100 assess-product lines of
`docs/orchestration/state/measurement-paper/5d-design-20261023/stage0/INVENTORY.sha256` at origin/main 950656d5c).
0 node-h. Command: `bash pscr_fetch.sh <new empty dir> login27 w_inventory.sha256`; fetch rc 0, ssh rc 0,
script rc 0 (`session/fetch.out.txt`).

**Fence.** Inline, as written: squeue showed only `ll5d_gate_G18` and `ll5d_gate_AR23` (RUNNING); sacct had 28
cov2d/t2a rows in 14 days, none unended; FENCE CLEAR.

**Reads.** 102 inputs, each opened by explicit path with O_NOATIME, stat (size, mtime, atime) unchanged and
read whole (`members/manifest.json`; one `FILE` line each in `session/fetch.out.txt`). Mac-side verifier:
work_proxy.npz = coverage.json:9's sha 42ce788b…; the 100 assess products equal INVENTORY.sha256 by path and
sha; OF5D = inputs-sha256.txt:1's 07fccc1a…; PSCR-977 OK.

**Members** (`SHA256SUMS`):

| member | rows | content |
|---|---|---|
| `members/work_proxy.npz` | 4.2/F4.3, 4.3 | per-playlist 2D reco templates D, S, S2, B, B2 on the 14×16 analysis grid and the proxy grid (proxy_hists.py); copied whole |
| `members/w_truth_z.npz` | m5/Fm7 | `xtrue_flat` (65856 = 14×16×7×7×6 cells) and `shape` of all 100 s5e assess products (nominal 40, W1/W2/W3 20 each), with the seeds |
| `members/w_truth_meta.json` | m5/Fm7 | each set's first product's keys and `meta` |
| `members/f53.json` | F5.3 | weighted and unweighted fractions of pass_reco rows outside the reco window and the gen grid (r4_migration.py's masks) |
| `members/manifest.json` | all | the 102 input records |

`w_truth_z.npz` is the fetched `w_truth.npz` (52.7 MB, sha 5fd98d61…, not committed) rewritten with
`np.savez_compressed`; `code/recompress_w_truth.py` re-reads it and checks all 12 arrays bitwise
(`session/recompress.out.txt`). The fetched tar (fc445ee3…) is not committed.

**Force-added.** `members/w_truth_z.npz` and `members/work_proxy.npz` are tracked by `git add -f` (`*.npz` is
gitignored; .gitignore's exception covers only `docs/analysis-note/release-package-*/*.npz`). They are receipt
members, not part of #981's release package, and must not be picked up by it.

**Control.** The unweighted pair reproduces `docs/orchestration/state/s5n/stage1/review1/r4_migration.json`
exactly (0.9999790240210246 / 0.9999139886843416); the session fails otherwise.

**Readings recorded with the fetch, not repaired:**

1. *Truth differs by seed only where half B is empty.* Within one set, `xtrue_flat` differs across seeds in
   1026-1161 fine cells, and only there: each is zero in some seeds. Every cell nonzero in all of a set's seeds
   agrees across them to 4x10^-14. `s5n_pseudo.true_xsec` divides half B's r-weighted truth by half B's
   completeness (ofin_B / denom_nd), so per fine cell x = const * denom_nd * (sum_B w r / sum_B w), independent
   of the split wherever half B populates the cell and r is constant in it. The EW-projected sums of single
   seeds therefore differ (up to 4.3% in EW1 for nominal, 5.9% for W3; 2.6% in EW14), but the full-sample truth
   is recoverable exactly: `code/m5_injected.py` takes each cell's value from any seed that populates it, checks
   that every cell of the 100-product support (10,694 cells) is populated in at least one seed of every set
   (0 missing), and gives the lower-capacity panel's definition (s5n_truth_check.py: M1 @ x(W) / M1 @ x(nom) - 1)
   in `derived/m5_injected.json`. Controls, both passing to 8x10^-15: W1 (E_avail-bin reweight) gives
   (1 + injected)/rho_k one constant over all 42 cells; W2 ((E_avail, W)-cell reweight) gives (1 + injected)/rho
   one constant. Not checkable from these products: a fine cell populated in the full MC but empty in every one
   of the 100 halves.
2. *Out-of-window weight: resolved, no correction.* The 428 pass_reco rows reconstructed outside the window carry
   w_reco 72.41 in total (none with zero w_reco). OUTCOME-20260925-s5c-purity-background-bias-at-high-W.md:37's
   "428 of 20.4 M, zero weight" is the s5c construction's MEASURED weight, and the code bears it out: in
   `nd-unfolding/s5c_pseudo.py` (origin/main 50402c0a3; file sha256 d81d4f46…, the `code_sha256` the assess products
   record) `purity_weights` :104-112 sets `inside` from `np.digitize` over [first, last) on every axis and gives
   every pseudo-data entry outside it `w = 0`. On the MC side the same rows are not masked: `s5c_unfold.unfold`
   (`nd-unfolding/s5c_unfold.py` :124-127, sha256 510d749a…) passes `MCreco` with `MCreco_weights=w_reco` to
   `omnifold_loop`. So the OUTCOME line is right for what it describes; the paper must not call those rows
   "zero weight" without naming the measured side.
3. *Gen outside the grid* counts 1755 pass_reco rows (w_reco 389.26), including the -9999 truth sentinels in
   q3 and W (r4_migration.json gen_min_per_col).

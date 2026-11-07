# COV2D addendum A4: the bulk readout driver, in two phases (declaration, before any code reads a bulk output)

**By** the `cov2d` session, 2026-11-07. **Authorized by** the director's ruling 1 of 2026-11-07, after the stage-5
finding that M holds no driver from the bulk's outputs to C_T, the null, the score and the readouts.
**Status:** DRAFT. Nothing in it has run, and no code has read a bulk output.

**M** (the code A4 imports, unchanged) = `a60547692df5f963e428cdfe4661fc51ab785b7b`. Every file:line below is at M,
unless it names `main` (`03f9b5cb`) for the declaration's text.

**MEASURES, when run:** for each truth T ∈ {G18, AR23}, C_T, its null, the graded reading and §6's readouts, from the
1,572 bulk products whose completeness is committed (#866).
**CANNOT AUTHORIZE:** anything beyond its own readings. A verdict goes to the director, and through the director to
Joseph (COV2D-DECLARATION.md §10 item 7, main).

## 1. What A4 is, and is not

- **Glue only.** A4 adds one module, `2d-unfolding/cov2d/cov2d_readout.py`. It imports `cov2d_blocks`, `cov2d_null`,
  `cov2d_score` and `cov2d_readouts` at M, unchanged. No bound function is edited, copied or re-implemented. If one would
  have to change, A4 stops and goes to the director (ruling 1).
- **§9.9 implemented here (not glue)** (the director's ruling of 2026-11-07): §9.9 (COV2D-DECLARATION.md:523-525, main)
  has no implementation at M. `git grep` for `dataFileSha256` finds only the writer, `re2_driver.py:2238`, and an re2
  test. A4 adds check logic for that already-declared control: a read of each product's provenance (§3.3, §4.3).
  - It reads only the products' `TNamed` provenance.
  - It refuses before any toy error is used.
  - It has tests in both directions and REQUIRED mutants (§8).
  It is the only part of A4 that is not glue.
- **Two phases, ordered structurally (ruling 1; §9.7, COV2D-DECLARATION.md:521, main):** "the null: check_matched at
  10⁻¹², computed and committed before the scorer opens any toy product".
  - Phase N reads no toy product.
  - Its null record reaches main through a receipt PR the director merges.
  - Phase S refuses to open any toy product until it has verified that committed record against a digest given on its
    command line.

## 2. The record paths

Under `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d/readout/<T>/`:

| file | written by | content |
|---|---|---|
| `null_<T>.json` | phase N | the null (`fd_1b_null.null_contents`' dict, arrays as lists), `thresholds`, `size`, `null_minus`; C_T's digest and §9.8; the input inventory (§3.4); §9.9 for the non-toy products; `M`; `pins_checked`; `verdict` (PASS or STOP) |
| `blocks_<T>.npz` | phase N | `C_T`, `C_T_minus`, `C_univ`, `C_lat`, `C_norm`, `C_stat`, `C08`, `C_model_abs`, `x_T`, `x_R`, `rep`, `minos_x`, `w_flux`, and the per-band arrays phase S's readouts need (`bands_<b>`). Force-added (`*.npz` is gitignored, `.gitignore:30`); its sha256 is in `null_<T>.json` |
| `score_<T>.json` | phase S | `fd_1b_mc.grade`'s dict via `cov2d_score.score`, the readouts (§5), §9.9 for the toys, `M`, `pins_checked`, `null_digest` (as verified), `verdict` (§6) |

Each phase's log, connect and removal records sit beside them, as in every earlier receipt.

## 3. Phase N: `python cov2d_readout.py null --truth T --out DIR`

Login node, root_6_28 with the pinned MAT environment, the same environment and template as control95. Its main
(cov2d_blocks.py:336-433) has been run and receipted at M (#869).

### 3.1 Reads (each through O_NOATIME into a private copy, with its digest checked before ROOT opens the copy)

- **Bulk products of T** (`$O/out/<label>/xsec.root`): `X_<T>`, the 175 `U_<T>_<band>_<idx>`, the 10
  `L_<T>_<band>_<i>` and the 300 `B_<T>_<NNN>`. Each one's sha256 must equal its row in #866's `completeness.tsv`. A
  missing product, or one off its digest, refuses (INVALID, §9.13).
- **Part B's E_R** (`ro.NS_R/out/ER/xsec.root`), against `ro.partb_sums()`, as control95 checks it.
- **The rollup's own inputs**, through `cov2d_blocks.noatime_inputs` (:160) exactly as control95 calls it (:371):
  the constraint, the VL175 build JSON and MINOS npz, the MEFHC flux file, and the per-playlist flux and POT files.
- **C08_R:** `cov2d_blocks.C08_R_FILE` (:52, sha256 `7153b194…`), key `c08`.
- **C_model and C_model⁻:** `cov2d_blocks.c_model()` (:76; JSON `aabc66d1…` :48, matrix `11fe6818…` :50).
- **No toy product, no toy truth, no step-A/B array is parsed in phase N** (§3.4 hashes three files, unparsed).

### 3.2 Computation (each call to a bound function at M)

1. The open audit is installed before the rollup is imported, as in control95 (`OpenAudit`; `pinned_mat_environment`).
2. `cells = ro.Cells(E_R copy)`: E_R's 205-cell mask, with `x_R = cells.x`.
3. `x_T = cells.vec(X_<T> copy)`. The bands are `{b: stack(cells.vec(U_<T>_<b>_<i>) for i)}` for the 38 universe
   bands, and the 5 lateral bands from `L_<T>_<b>_<0,1>`.
4. `(w_flux, phi_minos) = ro.flux_weights()`. Then
   `minos_x = ro.x01(cells, [L_<T>_Muon_Energy_MINOS_0, _1], phi_minos, "cov2d_<T>")`. `x01` uses only `cells.rep`
   and `cells.full` (re2c_rollup.py:235-254), so E_R's mask is the cells object R6 names. Any `ro.CHECKS` failure x01
   adds is a STOP.
5. `X_rep = stack(cells.vec(B_<T>_<NNN>))` for the 300 replicas.
6. `blocks = cov2d_blocks.assemble(x_T, cells.rep, bands, minos_x, w_flux, X_rep, x_R, C08_R, C_model, C_model_minus)`
   (:119). §9.8 is `blocks["section_9_8"]`.
7. `null = cov2d_null.null_at_T(blocks, bands, minos_x, w_flux)` (:50), at `n_mc = 2,000,000` and seed 5,742,000. It
   gives the null, the thresholds, the size and `null_minus`. `check_matched` ≤ 10⁻¹² is enforced inside
   `fd_1b_null.null_contents`, which refuses otherwise.

### 3.3 §9.9 for the non-toy products (§9.9 implemented here, not glue)

For each product read in §3.1, its `TNamed` provenance is read (`driverSha256`, `runArgv`, `runConfig`,
`dataFileSha256`), as `test_re2_data_file.records` reads it (:101-111).

**Required:**
- one `driverSha256` across all of them;
- `dataFileSha256` equal to the realization file's sha256 in the committed `pseudo_b.json` of T. The universes,
  laterals, replicas and central run all unfold d̃_T (declaration §4.4);
- `runArgv` equal to the product's `runs_<T>.tsv` row with its variables expanded;
- the estimator seed equal to the `--seed` in that same row.

Any difference is INVALID at T.

### 3.4 The input inventory, which phase S will check

Phase N hashes, **without parsing**, through O_NOATIME, and records sha256, size and mtime for:
- step A's `cells.npz` and `pseudo_a.json` for T;
- step B's `truth_xsec.npz` for T;
- the 300 toy products `T_<T>_<seed>/xsec.root`. Their digests are taken from #866's `completeness.tsv`; they are not
  opened.

**What this proves:** phase N and phase S read the same bytes. **What it does not prove:** that those bytes are the
ones step A or step B wrote. A search for earlier evidence of their identity (§7) found the following, and phase N
checks each item:

| file | earlier evidence on main | check in phase N |
|---|---|---|
| G18 `cells.npz` | size 4,321,842 B, mtime 2026-11-05 03:52 PST (`fd/receipts-cov2d/pseudo/G18/end_state.txt:43`), listed after job 60848251 ended | size equal; mtime minute equal; mtime within the job's sacct window, 02:42:18–05:06:52 PST (same file) |
| AR23 `cells.npz` | its name only (`pseudo/AR23/end_state.txt:20`); job 60889690, 2026-11-05T22:19:09 to 2026-11-06T00:50:53 PST | mtime within the job's window |
| G18, AR23 `truth_xsec.npz` | none (only step B's file counts, 303 and 304) | mtime within its job's window |
| G18, AR23 `pseudo_a.json` | sha256 `163cf1aa…` and `bdb7a57d…` (`pseudo/<T>/remote_sha256.txt`), with a committed copy | sha256 equal |

No earlier digest of either `cells.npz` or `truth_xsec.npz` exists in any job log or record. That limit is
disclosed here, and it is not a STOP (the director's ruling of 2026-11-07).

### 3.5 Phase N's PASS condition

PASS, with `verdict: "PASS"`, when:
- every read in §3.1 matched its pin;
- the open audit refused nothing, and no input's atime moved;
- the rollup's checks all held;
- §9.8 holds;
- `null_at_T` returned (so `check_matched` ≤ 10⁻¹²);
- §9.9 holds for the non-toy products;
- §3.4's checks hold.

Otherwise STOP or INVALID, as the bound code classes it. The record says which, and it goes to the director
unrepaired.

**The gate:**
- The null record and `blocks_<T>.npz` are committed through a receipt PR, which the director merges.
- The digest phase S takes is the sha256 of `null_<T>.json` as merged on main.

## 4. Phase S: `python cov2d_readout.py score --truth T --null-digest SHA --out DIR`

### 4.1 Refusals, before any toy product is opened (both directions are tested, §8)

1. `git show origin/main:<path>/null_<T>.json` must exist, and its sha256 must equal `--null-digest`. An absent record
   or another digest refuses.
2. The record's `M` must equal the deploy's HEAD, and its `verdict` must be `PASS`.
3. `blocks_<T>.npz` from origin/main must match the digest the record holds.
4. The input inventory (§3.4) is re-hashed through O_NOATIME and must equal the record, file by file.

### 4.2 Reads, after §4.1

- the 300 toy products, in `cov2d.TOY_SEEDS[T]` order;
- `truth_xsec.npz` (x_true per nature, masked to E_R's 205 cells);
- `pseudo_a.json`'s `natures` (from the committed copy, whose sha256 equals the inventory's);
- `cells.npz` for R_c.

### 4.3 Checks and computation (bound functions at M)

1. **§9.9 for the 300 toys** (implemented here, not glue), as in §3.3, before `errors` uses any toy error. For toy seed s, `dataFileSha256` must equal `pseudo_b.json`'s `files[seed=s]`
   sha256. The seeds must be exactly `cov2d.TOY_SEEDS[T]` (declaration §9.9: "the toys' seeds are exactly the declared
   ranges").
2. `deltas = cov2d_score.lateral_deltas(bands, minos_x)` (:35).
3. `(E, cross) = cov2d_score.errors(x_hat, x_true, natures, deltas, C_T)` (:52), with the natures' `lateral_signs` and
   `norm_z`.
4. `g = cov2d_score.score(E, C_T, null, T, cells, weakened_ratio, controls_failed)` (:70), with `weakened_ratio` from
   C2's `variance_ratio.option_1_clipped` (`R/clip/c2-clip2.json`, sha256 `39e333c5…`). `controls_failed` lists any
   failed §9 control for T.
5. **Readouts** (`cov2d_readouts` at M):
   - `spread_alone` (:43);
   - `bias` (:51);
   - `predicted_offset(bands, w_flux, x_T)` (:56);
   - `leave_out_mec(E, blocks, null_minus, g, cells)` (:67);
   - `realization_check(x_T, x_true_realization, σ)` (:82);
   - `clipping_residual(cells_npz, toy_index, rep, x_true, σ, C_T, g["flagged_cells"], T)` (:87), which refuses unless
     the rows are the toys in seed order (:96-99).

### 4.4 Phase S's PASS condition

PASS (the record is complete) when §4.1–§4.3 ran to the end and `score_<T>.json` was written. PASS is not the reading;
the reading is §6.

## 5. The readings, verbatim

### 5.1 The rule

COV2D-DECLARATION.md:269-273 (main):
- **cell c under-covers:** #{t : |e_tc| ≤ σ_c} ≤ k_c(T), the largest k with P(Bin(300, p_c(T)) ≤ k) < 0.025/205;
- **joint under-coverage:** #{χ²_t in region} ≤ k_J(T), the largest k with P(Bin(300, q(T)) ≤ k) < 0.025;
- **COVERS at T:** no cell under-covers and no joint under-coverage;
- **UNDER-COVERS at T:** otherwise; the report names each cell and whether the joint fraction is under too;
- **INVALID at T:** any §9 control fails for T; reported unrepaired.

### 5.2 The labels

- **The weakened pass** (:279): an unflagged cell in `cov2d.weakened_cells` at T "passes, weakened by clipping". A flag
  there is read as any other flag. The share of weakened cells is given beside the joint reading.
- **The outlier cell 216** (:300): reported by name, "whatever it is".
- **One-sided** (:307): over-coverage is reported, not failed.

### 5.3 The readouts (§6, :326-350)

- the spread alone;
- the bias;
- the predicted offset;
- the leave-out-MEC variant, in 1B's three texts (COV2D-AMENDMENT-1.md:159-160; fd_1b_mc.py:805-809):
  - "covers without the GENIE + MEC shift";
  - "its coverage in cells […] (and jointly) rests on the GENIE + MEC shift";
  - "printed; no reading (the tune under-covers under C_T)";
- the realization check;
- (ii) R_c: a flagged cell whose median |R_c| exceeds 0.5 σ_c "the clipping may explain this cell's flag" (:350); the
  verdict is unchanged.

Readout (i) is receipted separately (#873).

## 6. What each record may say

- `score_<T>.json`'s `verdict` is exactly one of COVERS, UNDER-COVERS or INVALID (§5.1), as `cov2d_score.score` sets
  it.
- No other verdict word is written. Every number is beside its reading.

## 7. The identity search

Recorded per the director's requirement of 2026-11-07.

- **What was searched:** `git grep -E 'cells\.npz|truth_xsec'` over `fd/receipts-cov2d/pseudo/` on main, covering
  every receipt for G18, AR23 and AR23-attempt1: the end states, the job logs, the connect logs, `pseudo_a.json`,
  `pseudo_b.json` and `remote_sha256.txt`.
- **What it found:** three hits, all in the end states (§3.4's table).
- **Partial content evidence:** `pseudo_a.json`'s per-toy `truth_lambda` sums lam_plus over all truth rows, while
  `cells.npz` bins only the rows in the truth phase space (cov2d_pseudo.py:130-139). So the two give an inequality, not
  an identity: Σ_c m_all[k] ≤ −sum_lambda_neg[k]. Phase S records it, as a consistency check that is not decisive.

## 8. Tests and mutants

- **The fixture:** a synthetic end-to-end fixture with two truths, run through the real `null` and `score` mains on a
  tmp tree. The open audit's guarded prefix points at the tree. MAT, `TFile.Open` and part B's arithmetic are stubbed,
  as REQUIRED-12.md's control95 test does.
- **Both directions** for every guard:
  - an absent null record, a wrong digest, a wrong `M`, a STOP verdict;
  - a `blocks` digest off;
  - each inventory file changed;
  - a toy product opened before the gate;
  - a wrong toy seed set, and the seeds out of order for R_c;
  - §9.9: a wrong `driverSha256`, a wrong `dataFileSha256`, a wrong `runArgv` and a wrong seed each refuse, and a
    correct product passes;
  - a product off its #866 digest;
  - an atime moved.
- **The mutation harness:** in `mutation_amendment.py`'s style. Its REQUIRED mutants:
  - the null gate removed;
  - the digest compare removed;
  - the inventory re-hash removed;
  - §9.9 skipped, and each of its four field compares removed;
  - the toy order changed;
  - the open audit off;
  - `noatime_inputs` dropped.
- **Then** coverage-5b-audit audits A4, and the director binds it with a new M line.

## 9. Price and schedule

- **Both phases** run on a login node, at 0 node-h.
- **Phase N** reads 486 products per truth plus the rollup's inputs, as control95 did (5.5 s of compute there). The
  null's 2,000,000 draws dominate.
- **Phase S** reads 300 products per truth.
- **The readout is due 2026-12-18** (§10, main).

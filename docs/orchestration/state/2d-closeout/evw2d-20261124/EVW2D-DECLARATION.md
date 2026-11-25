# EVW2D declaration: E_R's per-event unfolded weights, written beside its histograms (2026-11-24, revision 4)

**By** limitation-resolver, at the director's request. **Status: a draft for the reads and the director's binding.
Nothing has run on NERSC.** It runs only under a binding and the director's GO. Publication is Joseph's call, after Ben.

**Revision 2 (2026-11-25)** takes codex-school's first read: NO-GO, 4 BLOCKING and 8 other findings, all taken. The
changes are summarized in §11.

**Revision 3 (2026-11-25)** takes the second reads: codex-school NO-GO (5 BLOCKING) and agy `gemini-4-hydrogen-xhigh`
NO-GO (2 BLOCKING). All findings are taken, with the director's condition on C-CMAP (§3). The changes are summarized in
§12.

**Revision 4 (2026-11-25)** takes codex-school's third read (NO-GO, 8 BLOCKING) and then the re-read on its head by
codex-school `gpt-6.2-sol` (NO-GO, 2 BLOCKING, both about what the exactness gates compare) and claude-personal
`claude-sonnet-5-5` (GO WITH CHANGES). All BLOCKING findings and the cheap others are taken; the rest are the package's
follow-ups. agy and Grok could not run (quota). The director accepted §8's threat model and made this the last full
round. The changes are summarized in §13.

The code is in [`2d-unfolding/evw2d/`](../../../../../2d-unfolding/evw2d/): `evw2d.py`, `config.json`,
`references.npz` (built by `make_references.py`), `test_evw2d.py` and `evw2d_mutation.py`.

## 1. Why

- **No 2D driver stores per-event weights.** Every driver writes only histograms on `PT_EDGES`, so any change of binning
  needs a rerun (`ibu-chi2-20261123/grid-price/README.md`, "a cheap fix that pays back either way").
- **Production training does not see the interior pT edges.** Tier 1's C-COL showed that the unfolded counts in each
  p∥ column agree to 2.3e-13 on two grids (`ibu-chi2-20261123/tier1/README.md`). That is a statement about p∥ marginals
  on two grids. This run tests it cell by cell on the paper's grid (C-EXACT-PAPER). For any other grid, a re-histogram
  of the weights equals a rerun only if the training also ignores those edges, which is expected but not tested here.
- **Publication.** Joseph may publish the central-value weights as the unbinned result.

## 2. What runs

**One run of E_R's driver, unchanged:** E_R's argv, its 64 CPUs and thread environment, and its two inputs. No byte of
`2d-unfolding/re2/re2_driver.py`, `2d-unfolding/ref_c2c1/ref_c2c1.py` or `2d-unfolding/ref_c2c1/config.json` changes.
COV2D, G2R and COVFIX pin them.

- **The driver tree.** A clean, cache-free clone at `77d76cfc2d621f8faa010b75006811868494652a`: REF-C2C1's deploy, and
  Tier 1's M. `evw2d.py` imports `ref_c2c1.py` from that tree, and through its `load_driver` the driver and the OmniFold
  helper. It refuses in these cases, all before the import except the last:
  - the tree is not the top level of a git checkout whose HEAD is that commit, or `git status --porcelain --ignored`
    shows anything. git runs with no inherited `GIT_*` variable, so `GIT_DIR` or `GIT_WORK_TREE` cannot point the
    checks at another checkout;
  - `config.json` does not pin exactly these four files, any of them is reached through a link or is not a plain file
    inside the tree, or any of them differs from its pin (C-PINS):

    | file | sha256 |
    |---|---|
    | `re2_driver.py` | `938c53c5…` |
    | `omnifold.py` | `e9623412…` |
    | `ref_c2c1.py` | `285dd138…` |
    | `ref_c2c1/config.json` | `9127b45a…` |

  - a `__pycache__` sits beside them;
  - the process does not run with `python -B`, or a redirected cache is set (`PYTHONPYCACHEPREFIX` or
    `-X pycache_prefix`);
  - a module named `re2_driver`, `ref_c2c1` or `omnifold` is already loaded;
  - a loaded module's file is not the tree's.

  It re-hashes the four files after the run, and checks again that no cache appeared. At that commit the driver equals REF-C2C1's pin, and Tier 1's C-REF-OLD
  reproduced E_R's hXSec2D from it to 7.9e-12. Main's driver (`e226daf3…`) differs only by G2R's inert `--miss-map`.
  EVW2D still pins M, so it runs exactly the code Tier 1 checked.
- **The runner.** `ref_c2c1.run_driver`, unchanged: E_R's driver `main()` in-process, with its own output `xsec.root`,
  and ROOT `TFile.Open` reads limited to the staging root.
- **Three pass-through recorders.** They wrap `OmniFold_helper_functions.omnifold`, the driver's
  `collect_truth_denom_arrays` and its `get_pot_scales`.
  - Each calls the real function once, forwarding the very argument objects it received, and returns the very object
    the real call returned.
  - It keeps references to the arguments and the result. It also keeps digests: arrays by dtype, shape and bytes,
    floats by their bits, containers in order, and ROOT files and trees by type only.
  - The run refuses if a seam is never reached, or is reached twice.
  - C-REC re-takes the digests at the end.
  - The recorders are stacked under REF-C2C1's own observer of the OmniFold call. A test puts spies on both sides of
    each recorder in a real run. It shows that each seam was called once on each side, that every positional and
    keyword argument reached the real call as the same object, and that each caller received the identical object the
    real call made. "Unmodified" means the digests: the arguments' digest is the same on entry, on return and at the
    end of the run, and the result's at return and at the end. A change made and undone inside the call is not seen.
- **The inputs.** `evw2d.py stage` makes O_NOATIME copies, into the staging root, of:
  - the CV omnifile `43f8cc16…` (CFS `two-d-followup-20261010/xr-input/`);
  - the flux file `d40aea69…`.

  These are REF-C2C1's inputs, `ref_c2c1/config.json` `inputs`. The steps for each copy:
  1. It goes to a partial name unique to the invocation (host, process and a random token). Only a partial this
     invocation created is ever removed; one that another invocation made stays.
  2. It is checked against its pin and set read-only.
  3. It is published under its final name by a hard link, which never replaces an existing file.

  A failed copy leaves no file of its own. A stale partial, an existing name or a symlink refuses, and stays for a
  person to remove. The staging root is then made read-only (0555), so no name in it can be replaced by an ordinary
  write. Before it starts, the run opens each copy through O_NOATIME and holds it open for the whole run. The held file
  must be the one the name names (identity: device, inode, size, mtime, mode; a name that is a link refuses), and its
  bytes, hashed through the
  handle, must equal the pin. The independent read of `mc_signal_reco` (C-KEY) opens the held file itself
  (`/proc/self/fd/N`), not the name, so a name swapped and restored cannot feed it other bytes. At the end, C-STAGE
  checks that the name still names that file, with the same digest. The run reads only these copies.
  - **ROOT and RDataFrame reads of the verified staged copies are authorized here explicitly.** ROOT cannot take
    O_NOATIME. The copies are this lane's own, and their atime does not matter.
  - Any Python read under `/pscratch` or `/global/cfs` outside the allowed roots must carry O_NOATIME (REF-C2C1's
    `read_guards`).
  - The binding confirms that the cluster's interpreter has a real `os.O_NOATIME`. The tests substitute it, as
    REF-C2C1's do.

## 3. What is written

**The key.** The CV omnifile carries no event identity. Its trees are listed in `stageD-inputs/REPORT.md` §4.3:
- `mc_signal_reco`: {sim, sim_pz, sim_pass, w_reco, MC, MC_pz, w_truth};
- `mc_truth_denom`: {MC, MC_pz, w_truth};
- `mc_background` and `data`.

The event loop writes `mc_run`/`mc_subrun`/`mc_nthEvtInFile` only under `MNV101_DUMP_POINTCLOUD`. The key is therefore
**(omnifile sha256 `43f8cc16…`, ROOT entry number in `mc_signal_reco`)**, which is unique by construction (C-KEY).
It identifies a tree entry in one content-addressed file, not a physical event. Physical ids (run, subrun, gate) are
out of this item; if publication needs them, that is a separate, priced item (the director's ruling).

**`weights.npz`** has one row per truth-passing `mc_signal_reco` row: the rows whose step-2 weights fill `hUnfold2D`.
That is about 33 M rows, about 1.2 GB, plain `np.savez`.

| column | dtype | meaning |
|---|---|---|
| `entry` | uint32 | ROOT entry number in `mc_signal_reco` |
| `truth_pt`, `truth_pz` | float64 | truth pT and p∥ (GeV/c), the driver's arrays |
| `w_prior` | float64 | the driver's `w_truth`, POT-scaled (fills `hTruth2D`) |
| `w_unfolded` | float64 | `float(step-2 ratio) × float(w_truth)`, the driver's `hUnfold2D` fill weight |

Notes on the layout:
- The weights are float64. In float32 the rounding of a cell's sum is bounded only by 2⁻²⁴ ≈ 6e-8, and E_R's sparsest
  cell has N_eff 28.9. So float32 could fail the 1e-8 gate on rounding alone (the director's ruling (2)).
- Rows with truth pT = 4.5 or p∥ = 60 pass the truth gate but fall into ROOT's overflow, in no cell. They are kept, and
  C-FLOW checks them.

**The constants** sit in the npz's `meta` and in `constants.json`. They are the driver's own `extract_cross_section_2d`
arguments, captured, not recomputed:
- the 14 `flux_bins` (m⁻²/POT);
- the data POT;
- the MC POT and the POT scale, from the recorded `get_pot_scales`;
- `n_nucleons`;
- the 1e4 m²→cm² factor.

On the flux:
- Both validated grids apply the 14 values by pT-bin index.
- **Only when C-FLUX passes**, the file also gives `phi_m2_per_POT`: one of the 14 values, which agree to one ulp. A
  binning other than these 14 bins applies it to every pT bin.
- The values agreeing makes them interchangeable. That each is the integrated flux Φ comes from the input's provenance
  (`stageA/REPORT.md` §3.5).
- The file's `fluxIntegral_m2_per_POT` parameter is the sum of the 14 copies, about 14 Φ, and is not a flux.

The formula: d²σ/dpT dp∥ = Σ w_unfolded / (c Φ N POT ΔpT Δp∥) × 1e4, zero where c, Φ, N or POT is not positive, and
cells take their lower edge but not their upper edge.

**The weights are the central value, validated only for observables of (pT, p∥) and only on the two grids tested
(§1).**

**The completeness c.** In Phase 17, `mc_signal_reco` holds every truth-passing denominator event. Tier 1's er.root
gives c = 1 to 1.6e-14 on both grids.
- **If C-COMPLETE passes,** the truth-passing signal rows and the kept denominator rows are the same multiset of
  (pT, p∥, w) values. Then on any binning both completeness histograms hold the same sum of the same values per cell.
  So c is 1, up to summation rounding, wherever the denominator is positive. Where it is zero, both cross sections
  are zero. C-CMAP checks this on the driver's own map.
- **The declared fallback:** if C-COMPLETE fails, `denominator.npz` (the driver's kept `mc_truth_denom` rows: truth_pt,
  truth_pz, w_truth; float64) is written beside the weights. c is then event-level per cell, Σ w_prior / Σ w_truth(den).
  The run completes, prints `FINDING: C-COMPLETE`, and records the finding in `run.json` and `evw2d.done`. **The failure
  is reported to the director as a finding.** The fallback adds about 0.8 GB.
- **C-CMAP, under the director's condition (2026-11-25).** When C-COMPLETE passes, C-CMAP judges the driver's own map:
  - **pass:** within 1e-12 of 1 wherever the denominator is positive, and 0 elsewhere.
  - **rounding:** every zero cell is 0, the largest miss is above 1e-12 but at most 1e-9, **and the map is the
    driver's own summation.** The driver's two fills are refilled from the recorded rows, in the driver's order:
    its truth-passing signal rows, and its kept denominator rows. They must equal `hOFInputTruth2D` and
    `hOFTruthDenom2D` bit for bit over every global bin, and their ratio must equal `hOFCompleteness2D` bit for bit,
    also over every global bin.
    Equal multisets summed in two orders can make such a miss; a changed map, or rows the driver did not fill,
    cannot pass this. The run takes the same declared fallback: `denominator.npz`, with dσ from
    event-level completeness. It records `C-CMAP` as a finding, with the size of the miss in `finding_sizes` in
    `run.json` and `evw2d.done`, and prints it. With the fallback, C-CMAP-EVENT requires the event-level map rebuilt
    from the saved rows to equal the driver's `hOFCompleteness2D`, zero cells included, to 1e-12.
  - **stop:** anything else: a zero cell that is not 0, no positive cell, a miss above 1e-9, or a map the recorded
    rows do not make. The run FAILs.

Also written:
- `xsec.root`, the driver's own output;
- `run.json`: the controls and their verdict (`controls_verdict`), the findings and their sizes, digests, argv, pins,
  LightGBM parameters, the staged inputs' identities, each phase's duration, peak RSS, and a custody record (each
  product's atime, mtime and size, with the scratch purge rule the binding confirms);
- `SHA256SUMS` over every product;
- **`evw2d.done`, published last, by write-then-rename.** A crash leaves either no marker or a whole one. It holds the
  run's verdict, the findings and their sizes, the acceptance checks and the digest of `SHA256SUMS`. The verdict is
  PASS only when the controls pass and the acceptance holds:
  - the products are exactly the expected set: the four products, `denominator.npz` exactly when the fallback is
    taken, and `SHA256SUMS`;
  - `SHA256SUMS` parses to exactly the expected digest map;
  - every product re-hashes equal.

  **A product without a PASS `evw2d.done` is not a result.** A consumer checks it with `accepted()`, which re-runs the
  acceptance and also requires `denominator.npz` exactly when the run recorded findings. An interrupted run leaves no done marker, and the next attempt needs a new `--out`.

## 4. Controls

Each control is computed in the run. Any failure makes the verdict FAIL and the exit code 6, except the two declared
fallbacks: C-COMPLETE, and C-CMAP's rounding outcome. The files are still written, for diagnosis, under a FAIL
`evw2d.done`.

A C-KEY failure is the exception. Without a valid key no weights are written. The run writes a FAIL `run.json` and
`evw2d.done` and stops, instead of crashing.

| control | what it checks | gate |
|---|---|---|
| **C-BIND** (before anything is created) | `config.json` is read once; the sha256 of the very bytes parsed equals the one given on the command line (`--config-sha256`, recorded by the binding), and that digest is the one recorded in the products. It carries the reviewed values, held as constants in `evw2d.py` so the config cannot loosen them: E_R's argv, 64 CPUs and thread environment, the 1e-8 tolerance, the input digests (`43f8cc16…`, `d40aea69…`), the references digest (`1b214582…`), the paper's pT edges and exactly the four pins. `declaration_sha256` is bound and equals this file's digest. The lane root is bound and strictly under `/pscratch/sd/j/josephrb`. The driver tree, the staging root, this checkout (`deploy_C`) and `--out` lie strictly inside it, and `--out` is new. The staged names are plain file names. | refuse |
| **interpreter, checkout, allocation** (before anything is created) | As §2: `-B`, no redirected cache, no preloaded driver modules; the driver tree is a clean checkout at M. `run` needs a numbered srun step (`SLURM_STEP_ID` all digits and below Slurm's reserved ids from `0xfffffff0`: not the `batch`, `extern` or another special step) of a 1-node job (`SLURM_JOB_NUM_NODES` = 1) on a compute node (host `nid…`). The time cap is the launcher's `#SBATCH -t`, which the binding fixes; `evw2d.py` does not query the scheduler, which the lane's rules limit to sacct. | refuse |
| **C-PINS** | The four pinned files are plain files inside the tree, reached through no link, and equal their digests before the import and after the run, and no cache appeared. The loaded modules are the tree's. | all |
| **C-KEY** | An independent read of `mc_signal_reco` from the held, verified file (RDataFrame, single-threaded; the loader's float64 and one-byte `sim_pass` types required) carries each row's ROOT entry number (`rdfentry_`, required 0…n−1 in order). It is passed through the loader's keep rule: weights finite and in [0, 1e4); truth by the driver's own `in_truth_phase_space` (rectangle plus θ < 20°); reco on the rectangle, needing `sim_pass`; −9999 sentinels; the POT scale. The kept rows must reproduce, bit for bit, the eight arrays the driver passed to OmniFold: truth and reco pT/p∥, both pass flags, `w_truth` and `w_reco`. The kept entry numbers must strictly increase and fit uint32. The pinned loader reads the tree sequentially and appends each kept row, so its k-th row is the k-th kept entry; the alignment rests on that traversal. | all equal |
| **C-REC** | Each recorder was called exactly once. Its arguments' digest did not change across the call or by the end, and its result's digest did not change by the end. | all |
| **C-FLUX** | The 14 flux values are finite, positive, and agree to one ulp of the largest. | ≤ 1 ulp |
| **C-COMPLETE** | The two multisets (§3) are equal, sorted by bit pattern. | equal; on failure, the fallback |
| **C-CMAP** (when C-COMPLETE passes) | The driver's `hOFCompleteness2D` against 1 where `hOFTruthDenom2D` > 0 and 0 elsewhere: pass, rounding (the declared fallback, recorded with its size; only when the driver's two fills, refilled from the recorded rows in its order, reproduce `hOFInputTruth2D`, `hOFTruthDenom2D` and the map bit for bit) or stop (§3). | ≤ 1e-12; ≤ 1e-9 with the fallback and the refill |
| **C-CMAP-EVENT** (with the fallback) | The event-level completeness rebuilt from `weights.npz` and `denominator.npz` equals the driver's `hOFCompleteness2D`, zero cells included. | ≤ 1e-12 relative |
| **C-FILE** | The products read back, against their sources and independently of the table that was written. The saved meta and `constants.json` both equal the meta written, and the dtypes are the declared ones. The saved entries equal the independently derived truth-passing entry numbers. Each indexes the independently read tree to the saved truth pT, p∥ and POT-scaled `w_truth`, bit for bit. The saved weights equal the driver's own rows, recomputed from the recorded OmniFold call. The fallback file is present exactly when it is declared; its three columns are float64 and equal the driver's denominator bit for bit, and its meta is the declared one. Every bit-for-bit comparison also requires equal dtypes. | all equal |
| **C-FLOW** | The saved weights are filled over every global bin of the driver's grid, under- and overflow included. They are compared with the run's own `hUnfold2D` (`w_unfolded`) and `hTruth2D` (`w_prior`), after the saved axes are checked. | ≤ 1e-12 relative |
| **C-SELF** | The file is histogrammed on the grid saved in the file and extracted by the formula, **with the constants and the completeness selector saved in the file**. It is compared with this run's own hXSec2D as the driver made it, kept in memory at the extraction (every global bin of the first `extract_cross_section_2d` result). The hXSec2D in `xsec.root` must equal that in-memory histogram bit for bit. | ≤ 1e-8 relative; the file bit for bit |
| **C-EXACT-ER** | The same histogram is compared with E_R's committed hXSec2D (`references.npz` `er`, from E_R's `xsec.root` `a5c13fc3…`). | ≤ 1e-8 relative |
| **C-EXACT-PAPER** | The file is histogrammed on the paper's pT edges (0.075/0.325/0.475) and compared with Tier 1's hXSec2D there (`references.npz` `paper`, from the committed `tier1/units/e/er.root`, `5171c7b8…`). | ≤ 1e-8 relative |
| **C-STAGE** | After the run, each staged name still names the held, verified file (device, inode, size, mtime, mode) with the same digest read again through O_NOATIME, and the staging root admits no ordinary write. | all |

Further rules:
- Each exactness test needs at least one nonzero reference cell, and exact zeros where the reference is zero.
- Before the driver runs, `references.npz` must match its pin, read once (the digest and the arrays come from one
  buffer), and both of its grids must equal the bound ones: E_R's
  on the driver's pT and p∥ edges, and Tier 1's on `config.json` `paper_pt_edges` and the driver's p∥ edges.
  `make_references.py` enforces the same axes when it builds the file.
- The two exactness tests against E_R and Tier 1 are the end-to-end proof that the cell sums are the result. C-FILE
  and C-FLOW prove the rows, the keys, the overflow rows and the saved constants.
- The run also refuses, before creating its output, if the CPU count or thread environment is not E_R's.
- The manifest's digests of `constants.json` and `xsec.root` are taken from the bytes the controls judge, before any
  control reads them: `constants.json` is parsed from the very bytes hashed, and `xsec.root` is hashed the moment the
  driver returns, before the independent read and before C-FLOW and C-SELF open it. `weights.npz` and `denominator.npz` are hashed as they are written. The acceptance re-hashes
  every product, so a product changed after its checks fails the acceptance.

`references.npz` (sha256 `1b214582…`) holds the two 224-cell vectors and their axis edges, and records the source
digests. Rebuilt with the axis checks, it is byte-identical. Its `er` vector agrees with Tier 1's committed C-REF-OLD
reproduction (`tier1/units/old/er.root`) to ≤ 1e-8, and its `paper` vector and both axes equal Tier 1's `e` product
bit for bit. Both are tests.

## 5. Tests and mutants

`test_evw2d.py` runs E_R's real driver from the pinned tree, in-process, on a synthetic omnifile shaped like RE-2's
fixture. The fixture adds rows that reach every branch of the keep rule: bad weights, θ > 20°, truth outside, reco
outside, a non-finite truth, values on the top edges, values on both grids' interior edges, and two identical rows. Its
references come from the same driver, unrecorded, on our edges and with `PT_EDGES` set to the paper's, as E_R and
Tier 1 ran.

The tests cover:
- **zero changed bytes:** the tree files equal their pins and the commit's blobs; a full run leaves them unchanged and
  C-PINS sees it; one changed byte, or a bytecode cache, refuses;
- **each caller receives the identical object, unmodified:** spies on both sides of every recorder in the real run;
- C-REC firing on a changed output or a changed argument, on a missing seam and on a second call;
- the key sequence equal to a scalar re-statement of the loader, row by row, including the identical rows and the
  sentinel rows;
- each of the eight C-KEY comparisons firing on a one-ulp change, and the branch types required;
- C-FILE firing on a shifted key, two weights swapped within one cell on both grids, an overflow row's weight, a
  truth value nudged one ulp inside its cell, a wrong dtype and wrong saved constants. The exactness tests stay silent
  on all of these but the last, which is why C-FILE exists;
- C-FLOW firing on a flow row's `w_unfolded` or `w_prior`;
- the extraction and the flow fill bit for bit against the driver's own TH2D fill and `extract_cross_section_2d`, and
  event-level completeness against the driver's own;
- C-FLUX both ways and on the real 14 values (Tier 1's committed `hFlux_pt`), and the scalar Φ only on a pass;
- C-COMPLETE both ways (signed zeros in either order; 2 × weight 1 ≠ 1 × weight 2), C-CMAP both ways, and the fallback
  end to end;
- every C-BIND gap with its own message, including each reviewed value, the command-line digest and this checkout's
  place;
- the interpreter, checkout and allocation checks;
- staging through unique partial names and links, with a stale partial or a symlink refusing and staying;
- C-STAGE on a name replaced by a same-bytes copy, and on a writable root;
- a cache appearing during the run failing C-PINS;
- C-CMAP's three outcomes, the rounding fallback end to end with its recorded size, and a stop failing the run;
- C-FILE on a tampered `constants.json` and on a denominator overflow row that no cell sum sees;
- the clean FAIL on a C-KEY mismatch, whether a value or a row count;
- the acceptance: a missing, extra or unlisted product, and a manifest missing one line;
- the done marker, published whole or not at all;
- `main()` end to end, in-process, each command with the driver tree's modules loaded afresh; its refusal of an
  existing `--out` and of a driver tree off the pinned commit; cleanup with its ledger row, and its refusals: an
  unaccepted product, a run bound to another config, a staged name that is a link or another file with the same
  bytes, and a ledger that is a link (nothing deleted, the link's target unchanged);
- the revision-4 hardening: the config digest of the bytes parsed; a lane root equal to the prefix; the `batch` and
  `extern` steps; `GIT_DIR`/`GIT_WORK_TREE` pointing at a clean checkout; a tree that is not its checkout's top level;
  a pin reached through a link; a handle that is not the named file; a name swapped for another omnifile around the
  driver and restored before any check (C-KEY fails on the held read); another invocation's partial left in place;
  `same_bits` refusing a dtype change; C-CMAP on real ROOT fills in two orders (a fill-order miss is the fallback; the
  same miss with rows the driver did not fill, or an injected map error of rounding size, stops); a wrong
  denominator meta; the exactness tests following the saved grid and the saved completeness selector; products
  changed after their checks failing the acceptance;
- the reference builder refusing NERSC paths for either source, and references with a missing key or a wrong dtype.

`evw2d_mutation.py` applies one-span mutants of `evw2d.py`. Each must make the suite fail with a named failing test,
and the control must pass.
- Each worker has its own sparse git worktree of the driver tree at M, so no case can taint another's.
- Every tree must be clean after every case.
- A kill whose first error is an import or syntax error is not counted.
- Each case records its failing tests, its kind (an assertion or refusal inside a test, or an error in a test's
  setup), its first error line and the mutant's sha256.

The results are in the code receipt.

## 6. Price

| item | estimate |
|---|---|
| Tier 1's E_R rerun on one node (`er_e` 9:33, `er_old` 9:44 by sacct; Tier 1's six steps ran concurrently in a 10:33 allocation) | 9:33–9:44 |
| the independent C-KEY read and keep rule (about 33 M rows, a per-row Python predicate) | about 1–3 min |
| the C-COMPLETE sort, C-FILE, C-FLOW, C-STAGE's second hash of about 2.2 GB of inputs, digests, writing and reading back about 1.2 GB (2 GB with the fallback) | about 3–6 min |
| **total** | **about 0.2–0.3 CPU node-h expected; cap 0.5** |

Peak memory is unmeasured.<!-- absence-ok: this run has not been made yet; run.json records its peak RSS --> It is expected under 40 GB: about 33 M rows × about 20 columns of float64 at peak, plus
the driver's own. A CPU node has 512 GB. `run.json` records each phase's duration and the peak RSS: preflight (from
the command's start: binding, checkout, pins, import, allocation and the staged inputs' verification), driver, key,
write, controls and final verification. `evw2d.done` adds the acceptance's duration.

It runs on one node, CPU only, in E_R's thread environment, under an sbatch time limit that is the cap. Staging is two
O_NOATIME copies on a login node, in the root_6_28 environment (`evw2d.py` imports ROOT through the driver tree), at
0 node-h. There is no GPU and no move between CPU and GPU, so no repro test
is needed.

## 7. Custody

**The lane root,** bound at the binding: `$SCRATCH/evw2d-<date>/`, enforced under `/pscratch/sd/j/josephrb`. It holds:
- `deploy_M`, the clean clone at M;
- `deploy_C`, the clone at the commit that carries `evw2d/` and this declaration;
- `stage/`;
- `out/`;
- the launcher's logs.

Rules:
- Nothing goes to CFS.
- The staged copies are deleted after the run, as REF-C2C1's were, by `evw2d.py cleanup --out DIR`. It acts only on an
  accepted product whose `run.json` was bound to the same config digest. Before deleting anything it requires each
  staged name to be a plain file that is the file the run verified (inode, size, mtime and mode; not the device
  number, which a network filesystem may number differently on the login node), with the run's and the pin's digest.
  It opens `<lane_root>/deletions.tsv` for appending without following a link, requires the opened file to be a
  singly linked regular file, and only then deletes, appending a row per file: UTC time, path, sha256, size and
  reason.
- `out/` stays on `$SCRATCH` until Joseph decides on publication. `run.json` records each product's atime, mtime and
  size, and the purge rule. The binding confirms the rule (files unread for 8 weeks), so the exposure is the atime plus
  56 days.
- The launcher's logs and any temporary files stay inside the lane root.
- Status is checked by sacct only.

## 8. What it cannot claim

- It measures one driver run and its weights.
- It cannot authorize a reading, a claim, publication, or physical event ids.
- The weights are validated for observables of (pT, p∥) only, on the two grids tested. Nothing here shows they are
  valid for any other observable.
- **What the controls defend against (accepted by the director, 2026-11-25).** They are built against mistakes and
  against lasting changes by any writer: the wrong file, a stale or concurrent copy, a changed pin, a changed product.
  They are not a defence against a hostile process under the same account, which could change any file, or the
  process itself, between two checks.
  - The class this leaves open: the driver opens all its inputs (the omnifile and the flux file) and its source files
    by name. A name swapped and restored around one of those reads alone is not seen by identity or digest.
  - What still sees part of it: the independent read uses the held, verified omnifile, so a swap that changes any
    `mc_signal_reco` array the driver passes to OmniFold fails C-KEY. The exactness tests compare cell sums with E_R's
    and Tier 1's committed hXSec2D at 1e-8, so a swap that moves those sums beyond that fails them.
  - What can pass: a swap that changes neither. Examples are a zero-weight row added to the denominator tree (it can
    trigger the fallback and change `denominator.npz` and the saved selector), or a data POT that scales `w_prior`,
    `w_unfolded` and `data_pot` together. Each needs a hostile same-account process, which this model places out of
    scope.

## 9. Risks

| risk | consequence |
|---|---|
| LightGBM's multi-threaded fit could differ from E_R's run beyond 1e-8 | C-EXACT-ER and C-EXACT-PAPER FAIL. RE-2's 1e-8 rule has held each time: Tier 1 got 7.9e-12. A failure is a STOP and goes to the director. |
| Tier 1's paper-edge run and this run are separate fits | C-EXACT-PAPER tests the same rule across them. |
| The independent read's keep rule is a re-statement of the loader | C-KEY's bitwise equality on all eight arrays, plus C-FILE's per-row cross-check against the independently read tree, is what makes it safe. Rows that are bitwise identical in every loader column are indistinguishable to the unfold, and the entry numbers still key them uniquely. |
| The purge of the CFS originals | This does not apply (CFS). Only the staged copies are on pscratch, and only for the run. |

## 10. Order

1. This declaration and the code, with tests and mutants.
2. Reads:
   - codex-school: round 1 and round 2 NO-GO, both taken;
   - agy `gemini-4-hydrogen-xhigh`: round 2 NO-GO, taken;
   - round 3: one delta pass by each on a single head, by the director's ruling. agy (weekly quota 0 until
     2026-12-01) and Grok (HTTP 402, balance exhausted) could not run. The director ruled codex-school the only
     round-3 reader, with the director's own review of the full delta before binding as the second look.
     codex-school returned NO-GO, with 8 BLOCKING, 2 SHOULD-FIX and 1 MINOR, taken in revision 4 (§13). The
     director's rulings (2026-11-25): §8's threat model is accepted (the PG replay's D2); revision 4 is the last full
     round; one codex-school re-read on its head runs in parallel with its campaign; after that, only a finding that
     could change the published weights, the constants or the exactness gates blocks, and anything else goes to a
     follow-ups list in the package.
3. To the director, with shas computed by command.
4. The binding. It fixes `declaration_sha256`, `lane_root`, `driver_tree.root` and the staging root in `config.json`,
   and records the bound `config.json` sha256 that the launcher passes. It fixes the launcher, its `#SBATCH -t` (the cap)
   and its digest. It confirms O_NOATIME and the purge rule on the cluster. The diff of `config.json` must show only
   those four fields changed.
5. GO.
6. Stage, then run.
7. The records PR.

## 11. Revision 2: codex-school's round 1 (NO-GO) and what changed

| # | finding | change |
|---|---|---|
| 1 (BLOCKING) | the gates did not validate rows, keys or saved constants | C-FILE (per row, against the driver and the independent read); exactness rebuilt from the saved constants; tamper tests |
| 2 | C-KEY inferred row identity from traversal | ROOT entry numbers carried through the read; branch types required; the exact key sequence tested; the traversal dependence stated |
| 3 | the identity test stopped inside the recorder | spies on the caller's side; a dict-copy mutant; the digest's scope stated |
| 4 (BLOCKING) | `references.npz` not in the package; grids trusted | the file supplied to the reads; both grids enforced in the run and in the builder; p∥ axes tested |
| 5 (BLOCKING) | the mutation receipts conflicted | REC_IDENTITY's first form (`type(out)(out)`) was an equivalent mutant: a tuple copy is the same object in CPython. It was replaced by a real copy, which explains the different receipts. The new campaign records every case's failing tests, error line and mutant digest, and counts only named test failures |
| 6 | C-COMPLETE overstated | qualified to positive support and rounding; bit-pattern sort; C-CMAP on the driver's map |
| 7 | cell agreement cannot validate flow rows | C-FLOW over every global bin against `hUnfold2D` and `hTruth2D`; saved axes checked |
| 8 (MINOR) | the scalar-flux note was unconditional | the scalar given only on a C-FLUX pass; parameter called the sum of the 14 copies |
| 9 (BLOCKING) | the binding and SCRATCH boundary were unenforced | C-BIND before anything is created; the allocation check |
| 10 | pins, cache and staging custody | cache refusal, `-B`, the loaded-module check, post-run re-hash; staging through partial names; ROOT reads of staged copies authorized; O_NOATIME confirmed at binding |
| 11 | exceptions could leave ambiguous products | the seam-presence gate; both refusal classes caught; `evw2d.done` written last |
| 12 | narrow the claims | §1 and §8 narrowed; the price reconciled with Tier 1's concurrent steps; phase times and peak RSS recorded |

## 12. Revision 3: the second reads (codex-school and agy, both NO-GO) and what changed

| finding | change |
|---|---|
| no clean mutation receipt (both, BLOCKING) | a fresh campaign on the revision-3 bytes, with per-worker sparse worktrees, per-case cleanliness, kinds, and environment errors not counted |
| C-BIND checked only the config's own consistency (codex, BLOCKING; agy) | config.json's digest passed from the binding; the reviewed values held as constants in the code; this checkout and every root strictly inside the lane; an srun step on a compute node; the cap is the bound launcher's `#SBATCH -t` |
| C-PINS could pass with other code running (codex, BLOCKING) | exactly four pins; a clean checkout at the pinned HEAD; redirected caches and preloaded modules refused; caches checked again after the run |
| staged bytes could change after verification (codex, BLOCKING) | publication by no-clobber links from unique partial names; a read-only staging root; C-STAGE (identity and digest after the run); the reference builder refuses NERSC paths |
| the fallback table and `constants.json` were unvalidated (codex, BLOCKING; agy) | C-FILE compares `denominator.npz` with the driver's denominator bit for bit, and `constants.json` with the meta; the fallback must be present exactly when declared; the conversion factor is taken from the saved constants and checked |
| a C-KEY mismatch crashed the run (agy, BLOCKING) | a clean FAIL record and done marker with no weights, exit 6 |
| the row mapping was not proven independently (codex) | C-FILE's entries come from the independent read and its weights from the recorded call, not from the written table; `UChar_t`/`Double_t` branch types required; a table-swap mutant |
| argument forwarding was untested (codex) | the spies compare every argument's identity across the recorder, and count the calls <!-- absence-ok: a reviewer's finding quoted with its fix, not a claim that a result does not exist --> |
| C-CMAP could reject on rounding (codex) | the three outcomes, under the director's condition (§3); C-CMAP-EVENT with the fallback |
| acceptance was not atomic or fixed (codex; agy) | the exact product set, the parsed manifest and re-hashes; the marker by write-then-rename; `run.json` holds `controls_verdict` and `evw2d.done` the verdict; `accepted()` for consumers |
| cost and custody accounting (codex) | each phase's duration; the custody record; `cleanup` with its ledger |
| C-FLUX at the largest float (codex, MINOR) | a finite ulp and shape (14,) required |
| weak tests and small hardening (agy) | the allocation test stages first; `.`, `..` and empty names; reference keys and dtypes; `e.min()`/`e.max()` in C-KEY; symlinks refused in staging. Staging runs in the root_6_28 environment on a login node, where ROOT is present, rather than on a DTN |

The first full campaign on these bytes (117 mutants; control passed; trees clean) left two alive. MAIN_CHECKOUT
(main skipping the checkout gate) was a missing test; a main-level test now refuses a driver tree off the pinned commit
before anything is staged. STAGE_SYMLINK was equivalent: the staging root's listing already names a symlink at the
staged name, dangling or not, so the separate symlink check was removed and the refusal is unchanged (its test stays).
The receipt is a fresh campaign on the final bytes.

## 13. Revision 4: codex-school's round 3 (NO-GO) and what changed

| finding | change |
|---|---|
| 1. C-BIND could judge one config and run another (BLOCKING) | `load_config` parses and hashes one buffer; that digest is checked against the command line and recorded in the products; a lane root equal to the prefix refuses |
| 2. the batch step passed the allocation gate (BLOCKING) | `SLURM_STEP_ID` and `SLURM_JOB_ID` must be all digits; the 30-minute cap stays the bound launcher's `#SBATCH -t` (§10.4) |
| 3. git checks could follow inherited variables; pins could resolve through links (BLOCKING) | git runs with no `GIT_*` variable; the tree must be its checkout's top level; each pin must be a plain file inside the tree, reached through no link |
| 4. the staging directory could be swapped and restored around both reads (BLOCKING) | the staged copies are held open from their verification to the end; the digest is taken through the handle; the independent read opens the held file itself; the residual (a swap around the driver's read alone) and why it cannot pass unseen are stated in §8 |
| 5. a float32 denominator with false meta could pass (BLOCKING) | `same_bits` requires equal dtypes everywhere; C-FILE checks the denominator's meta |
| 6. acceptance could seal bytes no control checked (BLOCKING) | the digests of `constants.json` and `xsec.root` are taken from the judged bytes, before any control reads them; a product changed afterwards fails the acceptance |
| 7. C-CMAP could soften a non-rounding error (BLOCKING) | rounding needs the driver's two fills, refilled from the recorded rows in its order, to reproduce `hOFInputTruth2D`, `hOFTruthDenom2D` and the map bit for bit; tested on real ROOT fills in two orders, an injected map error, and rows the driver did not fill |
| 8. cleanup could append through a link, and deleted without checking against the run (BLOCKING) | the ledger opens with `O_NOFOLLOW` before anything is deleted; the run's config digest, and each staged file's identity and digest against `run.json` and the pin, are checked first; a staged name that is a link refuses |
| 9. staging could remove another invocation's partial (SHOULD-FIX) | partial names carry the host, the process and a random token; a partial another invocation created stays |
| 10. the reference builder screened one source (SHOULD-FIX) | both sources are screened, and the bytes hashed are the bytes read (`uproot` on the same buffer); the rebuilt `references.npz` is byte-identical (`1b214582…`) |
| 11. test and timing claims (MINOR) | `main()` is described as in-process; "unmodified" is defined by the digests; `run.json` records a preflight phase, and `evw2d.done` the acceptance's |
| round-2 PARTLY items | the exactness tests use the grids and the completeness selector saved in the file; the price section names login-node staging; the uncovered error branches are listed in the receipt |

Two additions in revision 4 were dropped as equivalent before the campaign: a second identity check through the held
handle, and a second digest through it, in C-STAGE. Any change they could see, the name's identity and digest already
show.

**The re-read on the revision-4 head** (codex-school `gpt-6.2-sol`, NO-GO; claude-personal `claude-sonnet-5-5`, GO WITH
CHANGES), taken before the campaign:

| finding | change |
|---|---|
| C-SELF could judge a replaced `xsec.root` hashed after the independent read (codex, BLOCKING) | `xsec.root` is hashed the moment the driver returns; that digest is the manifest's, and the acceptance re-hashes it. codex-school's confirmation found a remaining window (between the driver's close of the file and its return), so C-SELF now compares with the driver's hXSec2D kept in memory at the extraction, and requires the file's hXSec2D to equal it bit for bit |
| `references.npz` was pin-checked, then loaded in a second read (codex, BLOCKING; Sonnet) | hashed and loaded from one buffer |
| C-CMAP's ratio compared on the grid cells only (codex) | the ratio is compared over every global bin |
| cleanup compared the device number, which Lustre may number differently on the login node (Sonnet) | cleanup compares inode, size, mtime and mode; C-STAGE, on the run's node, keeps the full identity |
| a hard-linked ledger (both) | the opened ledger must be a singly linked regular file before anything is deleted |
| a staged name that is a link passed verification (codex) | refused at verification |
| Slurm's reserved step ids are numeric (Sonnet) | ids from `0xfffffff0` refuse |
| `accepted()` did not tie the fallback to the findings (Sonnet) | it requires `denominator.npz` exactly when the run recorded findings |
| §8 named one residual where there is a class (both) | §8 states the class, what still sees part of it, and what can pass |
| the declaration's title and §2's "before any import" (Sonnet) | corrected |

The remaining findings of both reads are in the package's follow-ups list.

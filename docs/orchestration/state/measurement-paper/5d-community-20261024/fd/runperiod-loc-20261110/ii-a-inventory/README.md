# RPL (ii-a) inventory: the zero loops carry no event key, so (ii-a) is NOT MADE (2026-11-11)

**By** the valid-region lane (director-helper-2), for the director, under
[`RPL-BINDING-1.md`](../RPL-BINDING-1.md) ruling 1 (the inventory, 0 node-h, with `rpl_inventory.sh` `b8a9058c`,
`rpl_launch.sh` `0e473dc8` and `cov2d_fence.sh` `16a2a5cd` verified) and the director's go for this connect.

**The outcome, by ruling 3** (`RPL-BINDING-1.md`: "If the keys are absent or not unique, (ii-a) is reported as not
made"): **the keys are absent.** (ii-a) is reported as not made. The join, its dry run and the method partition do
not run. A new event-loop pass that carries the MINOS-method flag is outside RPL
(`RPL-DECLARATION.md` row "(ii-a) without a unique key") and needs its own decision.

## What ran

- **The fence**, `connect/cov2d_fence.sh` (sha256 `16a2a5cd…`), on login27 at 2026-11-11T02:15:20Z: no cov2d or t2a job
  queued; 28 cov2d/t2a sacct rows in 14 days, none unended; `FENCE CLEAR` (`connect/fence.session.txt`).
- **The inventory**, `connect/rpl_inventory.sh` (sha256
  `b8a9058ce9da0d807ea1317e58bcb97f760982bd01da63b4427b34e6f31c2299`), launched by `connect/rpl_launch.sh` (`0e473dc8…`)
  on login27, foreground on the login node, nice 19, threads 1, 0 node-h.
  - Login node chosen by the survey at 2026-11-11T02:14:53Z (`connect/login-survey.txt`): login27, loadavg 18.13, with
    320 G free in /dev/shm.
  - Run 2026-11-11T02:15:32Z to 02:15:51Z (`cluster/inventory.log.txt:1,33`), `INVENTORY OK []`
    (`cluster/inventory.log.txt:28`), rc 0, and the /dev/shm work directory removed (`cluster/inventory.log.txt:32`).
  - The script's own copy on the cluster, `cluster/rpl_inventory.cluster-copy.sh`, is byte-identical to the approved
    script (`cmp`; both sha256 `b8a9058c…`), and the log records the same sha256 (`cluster/inventory.log.txt:2`).
  - The log's nine `Warning in <TInterpreter::ReadRootmapFile>` lines (RooUnfold classes present in two dictionaries)
    come from the environment's ROOT setup and are not from the inputs.
- **The fetch:** `post.tar.gz` sha256 `1ca0074b152d486263d09b1edecae69fb7ba1dad9feadf0656bb43343e71d24d` and
  `inventory.log` `401b9e11…` (`connect/fetch.sha256.txt`). They were unpacked into an empty directory and read with
  `python3 -I`. `cluster/inventory.json` (sha256 `c4945f9e8012419e435d589a0f41f84d0bb23bbf617e76bf4610487d98b7e29e`) is
  the file from the archive.

## What it found (`cluster/inventory.json`)

- **All 12 zero loops match their pins** (`nd-unfolding/fd_ct_period_inputs.py` `ZERO_LOOPS`, :58), read by an
  O_NOATIME copy; size, mtime and atime are unchanged by the read (`pin_ok` and `stat_unchanged` true for 1A–1P).
- **Each file holds the same four trees with the same branch lists** in all 12 playlists:

| tree | branches | the branch list |
|---|---:|---|
| `data` | 6 | `measured`, `measured_pz`, `measured_eavail`, `measured_q3`, `measured_W`, `measured_pass` |
| `mc_signal_reco` | 16 | `sim`, `sim_pz`, `sim_eavail`, `sim_q3`, `sim_W`, `sim_pass`, `w_reco`, `MC`, `MC_pz`, `MC_eavail`, `MC_q3`, `MC_W`, `MC_nproton`, `MC_npip`, `MC_hadangle`, `w_truth` |
| `mc_background` | 13 | `sim_background`, `sim_background_pz`, `sim_background_eavail`, `sim_background_q3`, `sim_background_W`, `sim_background_pass`, `w_bkg`, `bkg_nuPDG`, `bkg_current`, `bkg_inttype`, `bkg_vtx_x`, `bkg_vtx_y`, `bkg_vtx_z` |
| `mc_truth_denom` | 9 | `MC`, `MC_pz`, `MC_eavail`, `MC_q3`, `MC_W`, `MC_nproton`, `MC_npip`, `MC_hadangle`, `w_truth` |

- **No tree carries the data key** (`ev_run`, `ev_subrun`, `ev_gate`), **the MC key** (`mc_run`, `mc_subrun`,
  `mc_nthEvtInFile`), or any of the declared index branches (`physEvtNum`, `slice_numbers`, `n_slices`, `ev_slice`,
  `slice`, `mc_nthEvtInSpill`). No `key_*` record and no `index_branches` entry was written for any tree.
  - Search: the full branch lists above, as recorded in `cluster/inventory.json` for every tree of every playlist, were
    matched against `run|subrun|gate|evt|event|slice|entry|idx|index|id$` (case-insensitive) with `python3 -I`:
    no hits.
- **Entries, descriptive:** the `data` trees hold 4,119,797 rows over the 12 playlists; per-tree entries are in
  `cluster/inventory.json`.

## What was not read

- **No AnaTuple was read in this connect.** The declaration's inventory row also names one data and one MC AnaTuple.
  The bound script reads only the zero loops. A join needs the key on both sides, and the zero loops carry none, so the
  AnaTuple side cannot change the outcome.
- **The universe files encode the method split only in MC.** MAT adds the MINOS curvature term to the shift only when
  `<AnaTool>_minos_used_curvature` is true (`i-bandsize/matsrc/MuonSystematics.cxx.numbered.txt:130-147`, sha256
  `85780aee…`), so the MC's shifted branches carry the split implicitly. The data have no shifted branches, so this
  cannot partition the data and does not make (ii-a).
- **No physics column was read**, and no data/MC quantity was formed (ruling 5).

## Licence

**CITABLE FOR:** MP-1's 12 zero loops (at their `ZERO_LOOPS` pins) carry no run, subrun, gate, event or slice key
branch, so check (ii-a) of `RPL-DECLARATION.md` is not made; the zero loops' tree and branch lists as above.

**NOT CITABLE FOR:**
- any statement about the MINOS range/curvature method split, in data or MC, or about whether it moves the step;
- any data/MC comparison;
- the AnaTuples' branches (not read here);
- RPL's other checks, (i) and (ii-b), or any cause of the step.

Nothing is submitted, deposited or tagged.

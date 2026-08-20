# Audit findings — can the non-background-aware 5D files be removed? (2026-08-20)

> **Scope.** The scientific-removability question for the non-background-aware 5D event-loop files on
> pscratch, i.e. the `bkgaware` pair set — **not** the tracked `nd-unfolding/products/pet/bkgsub/`
> product JSONs, which is a different tree that the near-homophone suffix makes easy to substitute.
> One test remains in flight: Slurm **57285260**, see §5. Its result does not change §2 or §6.

**Read-only audit. Nothing was deleted, moved, or archived. No `hsi` mutating call was issued; every
cluster command was `ls`/`find`/`sacct`/`squeue`/`hpssquota`/`hsi -q ls`.** Written 2026-08-20.

**Verdict in one line: NO for the merged file and NO-FOR-NOW for the 12 per-playlist intermediates —
and the arm actually at risk is the background-aware one, whose 13 source files have no second copy
anywhere (its derived products do; §1).**

---

## 0. Scope, and the correction that defines it

The subject is **`bkgaware`** — untracked, gitignored event-loop ROOT files on pscratch — **not `bkgsub`**,
the tracked product JSONs under `nd-unfolding/products/pet/bkgsub/`. Different suffix, different tree.
The `main`-removal machinery in `CLAUDE.md` (pushed evidence tag, tested recovery, removal-family
authorization, surviving discovery route) **does not apply**: these files were never in `main`.

**Enumeration instrument, stated so it can be falsified:**

```
find /pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding -maxdepth 1 -name "*.root" \
     -printf "%s\t%TY-%Tm-%Td %TH:%TM\t%f\n"        # run on login30, 2026-08-20, rc=0
```

**`-maxdepth 1` — subdirectories are NOT covered.** `uq_5d/`, `uq_4d/`, `bank_*`, `products/` and
`p3f_pet_fullevent/` may hold further 5D objects that this audit did not enumerate. Treat the set below
as complete *for the top level of `nd-unfolding` only*.

The pair set is **13 pairs**, not the 5+3 in the seed I was handed. Every plain
`5D_*_universes_full.root` has a `_bkgaware` counterpart and vice versa — the pairing is exact.

| playlist | plain (bytes) | mtime | bkgaware (bytes) | mtime |
|---|---|---|---|---|
| 1A | 13,876,099,699 | 06-29 22:47 | 13,967,366,108 | 07-13 21:23 |
| 1B | 3,730,146,505 | 06-29 20:52 | 3,754,803,912 | 07-13 20:24 |
| 1C | 7,122,873,471 | 06-29 22:08 | 7,169,599,337 | 07-13 20:43 |
| 1D | 20,714,442,298 | 06-30 00:38 | 20,851,460,255 | 07-13 22:10 |
| 1E | 17,326,591,276 | 06-30 00:13 | 17,441,205,238 | 07-13 21:42 |
| 1F | 24,083,419,846 | 06-30 01:40 | 24,243,323,810 | 07-13 22:24 |
| 1G | 20,382,839,130 | 06-30 00:55 | 20,516,264,281 | 07-13 22:05 |
| 1L | 1,991,359,285 | 06-29 21:06 | 2,004,993,044 | 07-13 20:12 |
| 1M | 30,691,822,531 | 06-30 02:46 | 30,899,506,609 | 07-13 23:01 |
| 1N | 17,630,734,012 | 06-30 00:20 | 17,753,617,857 | 07-13 21:48 |
| 1O | 5,370,028,860 | 06-29 21:47 | 5,408,395,011 | 07-13 20:32 |
| 1P | 7,075,099,792 | 06-29 22:10 | 7,125,869,263 | 07-13 22:10 |
| **per-playlist subtotal (12)** | **169,995,456,705 = 158.32 GiB** | | **171,136,404,725 = 159.38 GiB** | |
| MEFHC (merged) | 169,974,191,800 = 158.30 GiB | 06-30 03:18 | 171,117,093,365 = 159.37 GiB | 07-13 23:08 |
| **ARM TOTAL (13)** | **339,969,648,505 = 316.62 GiB** | | **342,253,498,090 = 318.75 GiB** | |

**The space prize is smaller than the framing suggests.** pscratch measured today
(`hpssquota`, `lfs quota`, `myquota` — three instruments, same answer) is **15.99 TiB / 20.00 TiB =
79.9%**. Deleting the *entire* plain arm recovers 0.3092 TiB → **78.4%, a 1.5 pp gain**. That is the
whole upside, and §2–§4 are the cost.

---

## 1. THE FINDING THAT INVERTS THE QUESTION: only the plain arm is archived

`hsi -q "ls -lR"` over `/home/j/josephrb`, grepped for `universes_full`, returns **exactly one** of the
26 files:

```
-rw-r-----  josephrb  169974191800  Aug 12 07:04  runEventLoopOmniFold_5D_MEFHC_universes_full.root
```

in `mnv-quoted-products-20260812`. Byte-exact match to the scratch copy (169,974,191,800).

**Not on HPSS:** all 12 plain per-playlist files, and **all 13 background-aware files, including the
merged `..._MEFHC_universes_full_bkgaware.root` (159.37 GiB).**
**Not on CFS either:** `find /global/cfs/cdirs/m3246/josephrb -maxdepth 3 -name
"runEventLoopOmniFold_5D_*universes_full*.root"` returns nothing (rc=0 — a real null, not a failed query).

So on the storage axis the naive framing ("we moved to background-aware, retire the old") is backwards
for the **sources**: of the 26 pair files, the only one with a second copy anywhere is the
non-background-aware merged omnifile.

**Stated precisely, because the stronger version is not what is measured.** The background-aware
*sources* are sole-copy (318.75 GiB on purgeable scratch), but its *derived products* are archived.
`hsi -q "ls -lR" | grep -i bkgaware` returns three objects in `mnv-quoted-products-20260812`:

| bytes | object |
|---|---|
| 41,436,632,945 | `uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware.root` |
| 892,170,881 | `stamped_bkgaware_meancentered_20260812.root` |
| (dir) | `uq_5d/universe_stage2_5d_bkgaware/` |

None is in the pair set, so the enumeration in §0 is intact. What it changes is the **consequence**:
losing the 13 background-aware omnifiles would **not** lose the background-aware covariance results — it
would lose the ability to **rebuild** them. That is a real exposure and a weaker one than "sole-copy"
unqualified, and the distinction should not be blurred: the quoted numbers survive on tape, the capacity
to re-derive or re-quote them from source does not.

### 1b. The HPSS copy is not a verified recovery path

`docs/OPEN_ITEMS.md` **OI-50** (still OPEN, narrowed 2026-08-18): *"`mnv-quoted-products-20260812`
(300.17 GiB) remains on tape and remains **unverified**, and it is the archive the paper cites."*
The sibling archive `mnv-p3f-pet-fullevent-final` was read off tape and matched 240/240 md5s, then
deleted from tape — the quoted archive got no such treatment.

Deleting the scratch copy of the merged plain omnifile would therefore make an **unverified tape copy
the sole surviving copy of a paper-cited artifact.** That is not a recovery path; it is a hope.

Cheap discharge, already specified in OI-50: `hsi hashverify` over `mnv-quoted-products-20260812` —
digests are already stored, so it reads metadata and moves zero bytes. Chunk path arguments at 6
(`hsi` segfaults above ~36) and use `ssh -n` in any driving loop.

### 1c. "Archive rather than delete" does not fit — measured

HPSS today: **300.17 / 512.00 GiB = 58.6%**, i.e. **211.83 GiB free**. (The 2026-08-12 audit's 1.4573 TB
/ 265.1% is **stale**: ~1.16 TB left tape when the P3F archive migrated to CFS on 08-18. Both readings
are correct for their date; only today's is actionable.)

- Archiving the **background-aware arm** (318.75 GiB) to HPSS **does not fit** in 211.83 GiB free.
- Archiving the **12 plain per-playlist** files (158.32 GiB) *would* fit, with 53.5 GiB to spare.

CFS is the only destination with plausible room, but **I could not measure the m3246 CFS project quota**:
`showquota` reports only home and pscratch, and `df -h /global/cfs` returns the shared 151 P filesystem
(104 P used), which is **not evidence about our allocation**. That number must come from Iris or a
project-quota instrument before any move is planned.

---

## 2. The merged plain omnifile is LIVE, not superseded — RETAIN

`runEventLoopOmniFold_5D_MEFHC_universes_full.root` is load-bearing on four independent axes. Any one
of them blocks deletion.

**(a) It is the row-alignment reference for the PET point cloud.**
`nd-unfolding/pet/pointcloud_projection.py:44` — `OMNI = os.environ.get("PCPROJ_OMNI", f"{_REPO}/nd-unfolding/runEventLoopOmniFold_5D_MEFHC_universes_full.root")`,
with the comment at `:40-41`: *"OMNI must be the omnifile the npz was built from (row-aligned for the
MC_W assert)."* `nd-unfolding/pet/POINTCLOUD_PROJECTION.md:160-162` records that the
`MC == truth_scalars[:,0]` assertion **passes on all 32,849,103 rows**. Delete the file and that
assertion can never be re-run: the point cloud's row alignment becomes unfalsifiable. This is exactly
the hazard that a superseded arm can still be load-bearing as a control.

**(b) It is a hardcoded module-level constant in a driver the closing procedure still names.**
`nd-unfolding/sweep_bank_5d.py:40` — `OMNIFILE_5D = f"{_REPO}/nd-unfolding/runEventLoopOmniFold_5D_MEFHC_universes_full.root"`,
not env-overridable. Eight further live call sites default to it:
`eavailW_covariance.py:136`, `pet_lateral_band.py:79`, `pet_lateral_band_5d.py:54`,
`sbatch_nn_dump_5d.sh:14`, `sbatch_uthrow_dump_5d.sh:15`, `sbatch_uthrow_dump_rebank.sh:17`,
`sbatch_unfold_5d_detector.sh:32`, `sbatch_eavailW_cov_wlat.sh:35`, `sbatch_unfold_ascencio_fine.sh:25`.
Note `_REPO` is hardcoded to `/pscratch/sd/j/josephrb/MINERvA-OmniFold` — the tree I enumerated **is**
the tree that runs, so these defaults resolve to the files in §0.

**(c) It is digest-bound in a committed receipt.**
`docs/orchestration/state/quoted-products-digests-56760314.json` records
`sha256 afaaedaf745145acc29f792fcfc158e572ae27f87bfd74044c8c12a5b219c608`, `bytes 169974191800`,
`named_by: ["VALIDATION_LEDGER.md"]`. Also carried in
`docs/orchestration/state/cluster-ignored-set-walk-20260812.json` and
`docs/orchestration/RECEIPT-20260812-hpss-space-audit.md:69`.
Mechanical side-effect worth pricing separately: `verify_hash_bindings.py` computes its binding
inventory over the **filesystem** (`RECEIPT_BINDING_COUNT = 117`), so *deleting* a receipt-bound
gitignored path can move that count the same way an extra one does. Never resolve that by bumping
the constant.

**(d) It is the archive the paper cites,** per OI-50 — see §1b.

---

## 3. The 12 plain per-playlist files — the real candidates, not yet dischargeable

These are hadd intermediates of (2)(a)'s merge product, and they are the only part of the question with
a genuinely clean dependency story.

**Covering search for references, so the null means something.** `grep` for `5D_1[A-P]_universes_full`
over **every** tracked file (`git ls-files`) returns **zero hits** — no code, no sbatch script, no
receipt, no manifest, no doc names any per-playlist 5D file. Contrast: the merged plain name appears on
26 tracked lines, the merged bkgaware name on 9. (My first pass at this grep was wrong and I caught it:
searching bare `universes_full` returned 273 lines, but they were overwhelmingly the **2D** file
`runEventLoopOmniFold_MEFHC_universes_full.root` — a different file in `2d-unfolding/`. The 5D-restricted
pattern is the one that answers the question.)

**Why that is still not enough to say "delete":**

1. **Sole copy.** Not on HPSS (§1), not on CFS (§1). There is no recovery path at all.
2. **Regeneration is an event loop, not a download** — 12 playlists over the 9.6 TiB MC input.
3. **No merge-completeness receipt located.** The merged file (169,974,191,800 B) is
   **21,264,905 B smaller** than the sum of its 12 parts (169,995,456,705 B). A ~21 MB deficit across
   12 files is the right order for per-file TTree headers/metadata not duplicated in a merge, and the
   mtimes are consistent (parts 06-29→06-30 02:46, merge 06-30 03:18) — but **a size relation is not a
   completeness proof.** The test that settles it is specified, authorized, and running: see §5.

**If those three are discharged — hashverify or a CFS copy for recovery, plus an entry-count merge
proof — the 12 plain per-playlist files (158.32 GiB) are scientifically removable.** They carry no
citation, no digest binding, no code reference, and no control role. That is 158.32 GiB, or roughly
0.8 pp of pscratch.

---

## 4. Gate and control interactions — checked, not assumed

**Gate 6 does not reach this tree.** The five keys in
`docs/orchestration/state/gate6-member-trajectories-result-56847059.json`, verbatim:
`do_not_select_passing_subset`, `do_not_construct_C_ML`, `do_not_move_central`, `do_not_start_leg_2`,
`do_not_retry_unchanged`. None concerns files, storage, or this tree. The receipt's
`campaign_node` is *"Gate 6 PET ML ensemble Leg 1 member trajectories"* and it names **no ROOT file at
all**. `do_not_retry_unchanged` anticipates a *changed* retry, so I checked whether such a retry would
need these inputs — it would not: see below.

**The PET full-event / `C_stat` chain is not downstream of these files — measured, not assumed.**
`nd-unfolding/products/pet/bkgsub/of_inputs_pc_fullcloud_bkgsub_5d.provenance.json` names
`source_root: runEventLoopOmniFold_PC_MEFHC_fullcloud.root`, with `fullcloud_npz` and `ref5d_npz`.
No 5D `universes_full` file appears in any tracked `*provenance.json`. So the prior I was given
("GBDT-side, not upstream of `C_stat`") is now a finding, on the provenance of what **executed**.

**The footing controls do not bind the target set — but they bind one level below it.**
`docs/orchestration/PREDECLARE-20260811-bkgaware-footing-readopt.md` designs a 2×2 in
(footing × J28) whose arms **C1/C2 are non-background-aware reproduction controls that must return
`5.2600e-38` / `5.6609e-38`**, and states why: *"The controls are the point of running four instead of
two: they make the footing difference a measured quantity on one throw ensemble."* Naming both sides
honestly: those four arms consume **one unchanged input**, the throw ROOT
`uq_5d/unified_throw_cov_5d_fluxfix_20260806_full160.root`, plus the
`uq_5d/universe_stage2_5d/` block-sum products — *"no re-combine, no re-throw, nothing recomputed
upstream."* So the 2×2 does **not** read the event-loop omnifiles.
The dependency is one step removed and weaker than it first looks, because **the controls' operands are
themselves archived**: `hsi -q "ls -lR"` shows `unified_throw_cov_5d_fluxfix_20260806_full160.root`
(2,668,021,041 B) on tape, alongside both the `uq_5d/universe_stage2_5d/` and
`uq_5d/universe_stage2_5d_bkgaware/` directories. So C1/C2 can be re-run from tape without any omnifile.
What the omnifiles uniquely provide is the ability to **rebuild those products from source** if the
control values themselves are ever challenged. The plain footing is quoted
live in the note as the `+0.2839%` block-sum figure behind `sec_systematics.tex:170-173`.

**Quarantine means retained, not dead.** `AGENTS.md:27` puts *"Corrected scalar 5D covariance
candidates"* at `QUARANTINED` — background-aware block-sum and unified-throw candidates exist and
**neither is a publication uncertainty product**; `AGENTS.md:26` adds that validated 5D central values
*"do not revive superseded unified covariance products."* Neither arm is adopted. "Superseded" therefore
does not license deletion of either.

---

## 5. The test that is running, and the test that would not have helped

**Redirected before launch, and the reason is in this report.** The obvious experiment — does the
background-aware omnifile reproduce the plain one's row alignment, so `PCPROJ_OMNI` and
`sweep_bank_5d.py:40` could be repointed? — **cannot change the verdict it targets.** Even a clean pass
collapses only §2(a) and §2(b); §2(c) (the `sha256 afaaedaf74…` binding) and §2(d) (the paper citation)
survive untouched, and the merged plain file stays RETAIN either way. So it was not run.

The blocker that *is* dischargeable is the one gating the 12 per-playlist files: **no merge-completeness
receipt exists.** That test is running as Slurm job **57285260** (`--qos=shared -C cpu`, 8 CPUs, 64 GB,
6 h limit — inside the standing under-12 h approval), script
`/pscratch/sd/j/josephrb/mnv-5d-merge-completeness/merge_completeness_5d.py`, writing its JSON to that
same work dir, **outside** the `MINERvA-OmniFold` tree so it does not perturb the inventory it measures.
Every file is opened `TFile::Open(..., "READ")`.

**Four checks, and the structure that forced two of them.** A probe of `1L` first showed that "the entry
count of the tree" is not well defined in these files:

```
mcPOTUsed;1        TParameter<double>  5.822833555494932e+19
dataPOTUsed;1      TParameter<double>  1.3370718209243894e+19
mc_truth_denom;20  TTree  383848        mc_truth_denom;19  TTree  378765
mc_signal_reco;33  TTree  383848        mc_signal_reco;32  TTree  382752
mc_background;1    TTree    7820        data;1             TTree   49872
```

Two trees carry **multiple cycles with different entry counts** — AutoSave snapshots, where the highest
cycle is the complete one. So:

1. **Entry count of the highest-cycle key**, per tree, **reported per playlist** so a shortfall localizes
   instead of merely failing.
2. **Cycle census on the merge.** A `TFileMerger` that merges every key rather than the highest cycle
   would **double-count**; check 1 alone would report that as an unexplained surplus. The job records
   both the highest-cycle entries and the all-cycles sum for each side.
3. **Order-independent column aggregates** — `Min`, `Max` and `Count` (exact) plus `Sum` (float,
   compared at a stated 1e-12 relative tolerance) on the first present column of
   `w_truth, MC_W, MC, MC_pz, MC_eavail`, with the column used recorded. Entry-count equality shows no
   events were *lost*; it does not show none were *altered or duplicated*, and for an irreversible
   deletion decision that gap is the whole question. RDataFrame runs single-threaded on purpose so the
   summation order is stable.
4. **`mcPOTUsed` / `dataPOTUsed`.** `hadd` does **not** sum `TParameter<double>`. The job reports whether
   the merge carries the 12-playlist sum, or instead equals some single playlist's value. This one is not
   about deletability at all: if the merged file's POT is not the sum, the **normalisation of a live,
   paper-cited product is wrong**, and that outranks everything else in this memo.

**What a PASS does and does not authorize.** A pass discharges the **merge-completeness blocker only**
— blocker (iii) of the three in §3. Blockers (i) *no second copy anywhere* and (ii) *no verified recovery
path* (§1b, OI-50) are untouched by it. **A passing completeness test is not a deletion authorization.
Deletion is Joseph's call, and nothing in this audit licenses it.** A FAIL is the more informative
outcome: it would mean the merged plain omnifile — live in PET point-cloud projection and nine other
drivers — does not faithfully represent its inputs, which is a defect in a quoted product rather than a
storage finding.

---

## 6. Recommendation

1. **Do not delete anything today.** Nothing in the target set has both a verified recovery path and a
   clean dependency story.
2. **The exposure runs opposite to the question asked, on the source axis.** The background-aware
   *sources* are 318.75 GiB, sole-copy, on purgeable scratch, and **too large for HPSS's 211.83 GiB of
   free space**. Its *derived products* are on tape (§1), so what is at risk is the ability to rebuild,
   not the quoted results. Still a real exposure, and it wants a decision on its own.
3. **Run `hsi hashverify` on `mnv-quoted-products-20260812` (OI-50).** Zero bytes moved, and it is the
   precondition for every later sentence about the merged plain file.
4. **Then, and only then, the 12 plain per-playlist files (158.32 GiB) are the defensible candidates** —
   after the §5 completeness proof passes *and* a recovery copy exists. Both, not either.
5. **Re-measure the m3246 CFS project quota** before any archive plan; `df` on `/global/cfs` is not it.
6. **Do not treat pscratch relief as urgent on atime grounds.** Every large path reports atime within a
   minute of 2026-08-20 02:00–02:01 because something walked the tree, so NERSC's purge timer has been
   reset across the board and "last accessed" carries no disuse information right now.

## 7. Separately flagged — outside the pair set, and bigger

`runEventLoopOmniFold_5D_FPS_MEFHC_universes_full.root` is **192,868,793,175 B (179.62 GiB, mtime
06-10 11:23)** — larger than either merged file, the biggest single object in the tree, **non-background-
aware, and with no `_bkgaware` counterpart and no HPSS copy.** It is not part of the 13 pairs and must
not be swept in by a `*_universes_full.root`-minus-`*_bkgaware` glob: for the pairs, deleting the plain
arm removes a superseded duplicate; for FPS it removes the **only** copy. Same trap applies to
`runEventLoopOmniFold_PC_FPS_MEFHC.root` (72,651,640,496 B). If pscratch relief is the actual goal,
these are where the bytes are — and they need their own audit, not this one's conclusion.

## 8. Operational note, measured after I was warned about it

Job `57266000_0` (`g5dotrain`, WorkDir `/pscratch/sd/j/josephrb/gate5-data-only-frozen-377c713`) was
reported to me as running. `sacct` now returns **State=FAILED, Elapsed 03:08:52, End
2026-08-20T02:17:00** (batch step FAILED; only `.extern` COMPLETED). `squeue -u josephrb` shows no
running job — one PENDING cron entry (`57275989`, BeginTime). So the "do not touch" hazard on those two
trees has expired, and **a Gate-5 job failed** — unrelated to this audit, but it should not sit unnoticed.

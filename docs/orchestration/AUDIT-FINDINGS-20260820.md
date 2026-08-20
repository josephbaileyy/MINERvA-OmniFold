# Audit findings — can the non-background-aware 5D files be removed? (2026-08-20)

> **Scope.** The scientific-removability question for the non-background-aware 5D event-loop files on
> pscratch, i.e. the `bkgaware` pair set — **not** the tracked `nd-unfolding/products/pet/bkgsub/`
> product JSONs, which is a different tree that the near-homophone suffix makes easy to substitute.
> The one test this audit ran has landed: Slurm **57285260** + **57285779**, §5 — the merge-completeness
> blocker is **discharged**. It does not change §2, and it changes §6 only by retiring one of three
> blockers on the 12 per-playlist files.

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
3. ~~**No merge-completeness receipt.**~~ **DISCHARGED 2026-08-20 by §5.** The merged file
   (169,974,191,800 B) is **21,264,905 B smaller** than the sum of its 12 parts (169,995,456,705 B),
   and a size relation is not a completeness proof — so it was measured instead. It passes on every
   axis. The size deficit is explained: the parts carry AutoSave leftover tree cycles that the merge
   does not (§5).

**One of the three is now discharged (blocker 3, §5). The other two are not, and they are the ones that
matter for an irreversible action:** there is no second copy of these 12 files anywhere, and no verified
recovery path exists even for the merged file that supersedes them (§1b). **If those two are discharged —
`hsi hashverify` or a CFS copy — the 12 plain per-playlist files (158.32 GiB) are scientifically
removable.** They carry no citation, no digest binding, no code reference, and no control role. That is
158.32 GiB, or roughly 0.8 pp of pscratch.

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

## 5. The merge-completeness test — RESULT: PASS (blocker 3 only)

**Slurm `57285260`** (COMPLETED, 46.8 s) and follow-up **`57285779`** (COMPLETED), both
`--qos=shared -C cpu`, inside the standing under-12 h approval. Script and JSON in
`/pscratch/sd/j/josephrb/mnv-5d-merge-completeness/`, **outside** the `MINERvA-OmniFold` tree so the
probe does not perturb the inventory it measures. Every open is `TFile::Open(..., "READ")`.

**Redirected before launch, and the redirect mattered.** The obvious experiment — can the
background-aware omnifile stand in as the row-alignment reference, so `PCPROJ_OMNI` and
`sweep_bank_5d.py:40` could be repointed? — **cannot change the verdict it targets**: even a clean pass
leaves §2(c) (the `sha256 afaaedaf74…` binding) and §2(d) (the paper citation) untouched, so the merged
plain file stays RETAIN either way. It was not run. The dischargeable blocker was merge completeness.

### What the structure forced

A probe of `1L` showed that "the entry count of the tree" is not well defined in these files:

```
mc_truth_denom;20  383848   |  mc_truth_denom;19  378765
mc_signal_reco;33  383848   |  mc_signal_reco;32  382752
mc_background;1      7820   |  data;1              49872
mcPOTUsed;1  5.822833555494932e+19   dataPOTUsed;1  1.3370718209243894e+19
```

Two trees carry **multiple cycles with different entry counts** — AutoSave snapshots, highest cycle
complete. A `TFileMerger` that merged every key rather than the highest would **double-count**, and a bare
entry-count check would have reported that as an unexplained surplus (for `1L` alone, ~5,083 entries high).

### Results

**Entry counts — exact on all four trees, delta 0.** Per-playlist counts are recorded in the JSON so a
shortfall would localize; they sum to the merged total exactly.

| tree | Σ 12 parts | merged | delta | merged cycles |
|---|---|---|---|---|
| `mc_truth_denom` | 32,849,103 | 32,849,103 | 0 | `[1]` |
| `mc_signal_reco` | 32,849,103 | 32,849,103 | 0 | `[1]` |
| `mc_background` | 658,227 | 658,227 | 0 | `[1]` |
| `data` | 4,119,797 | 4,119,797 | 0 | `[1]` |

**The multi-cycle risk resolved in the good direction, and only measurement could say so.** The merge
reports a single cycle on every tree while the parts retain their AutoSave leftovers — the merger took the
highest cycle. This also **explains the 21 MB size deficit** of §3: the parts carry bytes the merge
correctly does not.

**Column aggregates — `Min`/`Max`/`Count` exact, `Sum` at float precision.**

| tree | column | count | min | max | Sum rel. diff |
|---|---|---|---|---|---|
| `mc_truth_denom` | `w_truth` | exact | 0.0012975226026944284 | 18.338888775570414 | 1.37e-16 |
| `mc_signal_reco` | `w_truth` | exact | 0.0012975226026944284 | 18.338888775570414 | 1.37e-16 |
| `mc_background` | `w_bkg` | exact | 0.0042967455694679435 | 11.354676060364943 | 1.97e-16 |
| `data` | `measured_W` | exact | 0.0 | 20.750233409290523 | 1.16e-16 |

Min/Max/Count are exact and order-independent, so they catch alteration and duplication, not only loss.
The Sum differences are pure float reassociation — four orders inside a 1e-12 tolerance and twelve inside
double precision. RDataFrame ran single-threaded so summation order was stable.

**POT — the check that outranked the rest, and it is clean.** `hadd` does **not** sum
`TParameter<double>`, so the merged file's normalisation was an open question about a **live, paper-cited
product**, not a storage question.

| parameter | Σ 12 parts | merged | equals sum | equals any single playlist |
|---|---|---|---|---|
| `mcPOTUsed` | 4.978198462880827e+21 | 4.978198462880827e+21 | yes | no |
| `dataPOTUsed` | 1.057394261158926e+21 | 1.057394261158926e+21 | yes | no |

`hadd_universes_full.py` does sum them. **No normalisation defect.** The "equals no single playlist" column
is what makes this a positive result rather than a coincidence.

**One instrument gap, recorded rather than buried.** The first job printed `overall: NOT_PASS`. That was
**my column-preference list, not the merge**: `mc_background` carries `sim_background*`/`w_bkg` and `data`
carries `measured*`, and none of `w_truth, MC_W, MC, MC_pz, MC_eavail` exists in either, so both returned
`NO_AGG_COLUMN` while their entry counts already matched exactly. A null from a search that could not have
matched is evidence about the search. `57285779` re-ran those two with `w_bkg` and `measured_W`: both PASS.

**An independent corroboration, and it cuts toward retaining.** 32,849,103 is exactly the row count
`POINTCLOUD_PROJECTION.md:160-162` cites for the `MC == truth_scalars[:,0]` assertion. Two unrelated
records agree on the merged file's size, which **strengthens §2(a)'s retain case** — it does not support
deletion.

### What this PASS does and does not authorize

It discharges **blocker 3 of §3, merge completeness, and nothing else.** Blockers (i) *no second copy
anywhere* and (ii) *no verified recovery path* (§1b, OI-50, still open) are untouched by it. **A passing
completeness test is not a deletion authorization. Deletion is Joseph's call, and nothing in this audit
licenses it.** A FAIL would have been the more consequential outcome — it would have meant the merged
plain omnifile, live in PET point-cloud projection and nine other drivers, does not faithfully represent
its inputs. It does.

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
4. **The 12 plain per-playlist files (158.32 GiB) are the defensible candidates, and one of their three
   blockers is now discharged** (§5 passed). What remains is a **recovery path**, not a completeness
   question. Neither a `hashverify` nor a CFS copy has been done, so the answer today is still no.
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

## 9. Process appendix — three notes for whoever regenerates `MANIFEST.tsv` next

Not scientific findings; kept separate so they do not dilute §1–§8. All measured at `ee52b08a`.

**(a) Stage the new file BEFORE regenerating, or the generated row is stale on arrival.**
`generate_manifest.py` inventories the **git index** (`:70` `git ls-files`, `:71`
`git ls-files --others --exclude-standard`), not `HEAD`. Add a doc and regenerate, and its row reads
`tracking=intended` — which becomes wrong the instant the commit lands and the file turns tracked
(observed here: `tracking=...,intended:1`). `git add` the doc **first**, then regenerate, then add the
manifest: the row reads `tracked`, and `--check` exits 0 *after* the commit rather than immediately
before it. The manifest cannot be hand-edited either — it has a byte-count fixed point that raises if it
does not converge (`:350-360`).

**(b) `MANIFEST.tsv` was already out of date on `main`, and this commit repairs five rows that are not
this audit's.** A bare `--check` in a detached worktree at `ee52b08a`, with nothing added, exits **1**
(`OUT OF DATE`, rows=319). The drifting rows are `docs/orchestration/.gitignore`, `LIVE-STATE.md`,
`MANIFEST.tsv`'s own self-size, `state/live-state.json` and `verify_hash_bindings.py`. The `.gitignore`
and `verify_hash_bindings.py` rows belong to `18d6b43d`, which landed a code change without regenerating
the manifest; its author has confirmed that. The generator emits the whole file, so those rows could not
be excluded from this commit — they are attributed here and in the commit message rather than left to
read as this audit's work.

**(c) OI-70's row describing this generator is stale on four counts, and the row still reads as current
instructions.** Measured, not relayed:

- The **mechanism claim is false.** The row says the generator "walks the filesystem (`:83`) rather than
  the git index and `.gitignore` is not consulted". Inventory is git-defined at `:69-71`, the docstring
  at `:4-5` states ignored files are excluded, and `--self-test` (`:376-394`) creates a file under an
  ignored directory and asserts its absence from the rows — it **passes**.
- **Both line citations have drifted.** `:83` is now inside `load_overrides()`, reading
  `MANIFEST-overrides.tsv` — nothing to do with inventory. The `states[rel] = "intended"` computation the
  row cites at `:103` is now at `:77`. A citation that has drifted is worse than a vague one: it looks
  falsifiable and is not.
- **The remedy it asks for has landed.** The row asks to "Add a `tracking` column, or exclude `intended`
  paths from the table". The committed header is `path  tracking  class  kind  …`.
- **Its blocker is retired, which makes its acceptance criterion vacuous.** The row records that two
  lanes declined to regenerate because doing so from a worktree "drops every `__pycache__`, `.DS_Store`
  and `.pytest_cache` row… measured at 30 rows dropped" (`BEN-183`), and sets the criterion "check that
  the ROW COUNT DOES NOT FALL". The committed manifest contains **0** `__pycache__`/`.pyc` rows and **0**
  `.DS_Store`/`.pytest_cache` rows, so that drop can no longer occur and the criterion now guards a
  retired failure mode.

**Stated explicitly to forestall a wrong inference — including one this audit initially drew.** The row's
instruction "Run `generate_manifest.py` IN THE MAIN CHECKOUT" is **unnecessary, not dangerous.**
`inventory()` is **pathspec-scoped**: both calls carry `-- docs/orchestration`, so untracked files at the
repository root cannot enter the table. Measured by running `inventory()` in the main checkout: 319 rows,
**0 `intended`**, no row outside `docs/orchestration`; the repo-wide `git ls-files` at `:264` feeds
`reference_sources()` for inbound counts, not rows. The real sweeping hazard is narrower and genuine —
an *uncommitted file inside `docs/orchestration`* is inventoried, which OI-70 itself records happening to
a peer's predeclaration. A detached worktree remains correct hygiene for keeping a regeneration off a
shared checkout; it is not a defence against a repo-root sweep.

The row is not amended here: `docs/OPEN_ITEMS.md` rows are digest-coupled to
`control-plane/source-record-inventory.tsv`, so editing one alone is unsatisfiable, and the row belongs to
another lane. It is routed rather than rewritten.

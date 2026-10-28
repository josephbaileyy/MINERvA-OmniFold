# The cheap tier's first step: are its inputs retained? (2026-10-28)

**By** the measurement session (fresh, `coverage` in ListAgents), for the director.

**Under** [`DECISION-20261028-joseph-d2-approved-and-cheap-tier.md`](../../../DECISION-20261028-joseph-d2-approved-and-cheap-tier.md)
item 2: "Its first step checks that the dumps items 3b and 5B depend on are retained, before the 2026-11-20 purge
window." The items are those of [`LIMITATION-PLAN-ADDENDUM-20261028.md`](LIMITATION-PLAN-ADDENDUM-20261028.md).

**MEASURES:** names, sizes, modification and access times on pscratch; HPSS path names, archive inventories and
quota; CFS directory names. On login08, 2026-10-28 21:43–21:46 UTC, by `ls`, `stat`, `du`, `hsi ls`, `hsi get -` of
inventory files, `htar -t` and `hpssquota`.
- No file's contents were read, no job ran, and nothing was written on the cluster.
- Nothing was read under `fd-f1-20261027/`.

**CANNOT AUTHORIZE:** an HPSS copy, a deletion, a retention request to NERSC (that contact is Joseph's), or a
declaration.

**CITABLE FOR:** where the cheap tier's inputs are, their access ages, which have an HPSS or CFS copy, and the HPSS
space left.

**NOT CITABLE FOR:** whether NERSC will purge a given file on a given date; any file's integrity (no sha256 was taken
here); which per-playlist inputs 5B will use.

**Receipts:** [`fd/receipts-ct/retention/`](fd/receipts-ct/retention/), probes `ret1.sh`–`ret6.sh` and their outputs.
`$P` = `/pscratch/sd/j/josephrb`.

## 1. The rule used for exposure

- NERSC: "assume that any file not accessed within 8 weeks may be purged at any time"
  (`state/2d-closeout/preservation-20261014/REPORT.md:87-88`). Purges have happened (`:89`).
- **Exposed from** = oldest access time in the group + 8 weeks **(arithmetic)**. Purging runs on a fullness
  threshold (`:87`). pscratch is at 17.01 of 20.00 TiB, 85.0 % (`ret2.out:99`).
- `ls` and `stat` do not change access times. This record does not propose reading files only to reset them.

## 2. The inputs, by item

| item | input | size | oldest access | exposed from | HPSS | CFS |
|---|---|---:|---|---|---|---|
| 3a, 3b | W2b data unfolds `$P/w2-recoil-20261006/w2b/unf/` (3 npz) | 285 K | 2026-10-20 (`ret3.out:11`) | 2026-12-15 | **no** | **no** |
| 3b | W2b lateral dumps `w2b/lateral/` (6 npz, with `_bkg`) | 4.5 G | 2026-10-08 (`ret3.out:10`) | 2026-12-03 | **no** | **no** |
| 3b | W2b merged and per-playlist event loops `w2b/{merged,evloop}/` (3 + 36 ROOT) | 14 G + 14 G | 2026-10-08 (`ret3.out:8-9`) | 2026-12-03 | **no** | **no** |
| 3b | MP-1 S1 lateral dumps `$P/measurement-paper/phase1/mp1/s1/lateral/` (22 npz: 11 variants and their `_bkg`) | 17 G | 2026-10-20 (`ret3.out:6`) | 2026-12-15 | **no** | **no** |
| 3b | MP-1 S1 data unfolds `mp1/s1/unf/` (11 npz) | 1.1 M | 2026-10-26 (`ret3.out:7`) | 2026-12-21 | **no** | **no** |
| 3b, 5B | MP-1 S1 per-playlist event loops `mp1/s1/evloop/<variant>/` (11 × 12 ROOT), and `merged/` (11 ROOT) | 50 G + 50 G | 2026-10-20 (`ret3.out:4-5`) | 2026-12-15 | **no** | **no** |
| 5B | per-playlist universe loops `$P/MINERvA-OmniFold/nd-unfolding/runEventLoopOmniFold_5D_<PL>_universes_full_bkgaware.root` (12) | 159.4 GiB **(arithmetic, `ret4.out:2-13`)** | **2026-09-14** for 11 of 12; 1A 2026-10-20 (`ret4.out:2-13`) | **2026-11-09** | **no** | **no** |
| 5B | their merge, `…_5D_MEFHC_universes_full_bkgaware.root` | 159.4 GiB | 2026-09-27 (`ret4.out:14`) | **2026-11-22** | **no**; only the non-bkgaware `…_MEFHC_universes_full.root` is in `mnv-quoted-products-20260812/nd-unfolding/` (`ret3.out:39-40`) | **no** |
| 4C | A7 calibration products `$P/s5p-20260926/runs/prod/cal/` | — | 2026-10-27, directory (`ret3.out:13`) | — | **yes**, `prd-release-preservation-20261008/s5p-archive-20261006.tar` (`ret5.out`) | **yes**, `s5p-archive-20261006/` (`ret4.out:36`) |
| 5A | `playlist_term.npz` `c1723cb5…` (`state/2d-closeout/playlist-term/REPORT.md:30`) | 1.4 M | 2026-10-16 (`ret3.out:12`) | 2026-12-11 | not this digest | **yes**, `2d-closeout-playlist-term-20261016/` (`ret4.out`) |

<!-- absence-ok: every "no" in the HPSS and CFS columns is scoped to the Search line below -->
Search: HPSS path names by `hsi ls -R /home/j/josephrb` filtered for mp1, w2b, w2-, universes, playlist, lat_ and zero
(`ret3.out:24-83`); the member lists of every HPSS archive directory (the `INVENTORY.sha256`, `members.sha256` and
`*-INVENTORY.sha256` files, read with `hsi get -`) filtered for mp1, w2b, lat_, universes and playlist_term
(`ret6.out`); `htar -t` on the one archive with an htar index, s5p (10,688 lines, `ret6.out`); CFS by
`ls /global/cfs/cdirs/m3246/josephrb/` and a glob for `*bkgaware*` two levels down (`ret4.out:15-41`).
- **What the Search cannot see:** `htar -t` failed on the other tars, which have no `.idx` (`ret6.out`, rc 72); their
  inventory files stand in for them. The inventory matches are unrelated (`ret6.out`): an S1 log named
  `G3-all.universes`, two NuWro converter sources, and RE-2's `partc-r2/playlist/playlist_term.npz` `dbb067aa…`.
  That is not 5A's `c1723cb5…`.

## 3. HPSS space

422.79 of 512.00 GiB is used, so **89.2 GiB is free** (`ret2.out:100`) **(arithmetic)**. That equals the 2026-10-28
reading in `HANDOFF-20261028-measurement-session.md` §4.
- The 5B universe loops (159.4 GiB) and their merge (159.4 GiB) do not fit.
- 3b's dumps and unfolds (MP-1 17 G + 1.1 M, W2b 4.5 G + 285 K, about 21.5 G) do fit **(arithmetic)**.
- All the ROOT event loops above (MP-1 100 G, W2b 28 G) together do not fit beside them.

## 4. For the director

1. **The first exposure is 2026-11-09, before the decision's 2026-11-20.** It covers 11 of the 12 per-playlist
   bkgaware universe loops, which have no copy elsewhere and no room on HPSS.
   - Whether 5B needs them is open. The addendum names two candidate per-period sources and leaves the choice to a
     pooled control (`LIMITATION-PLAN-ADDENDUM-20261028.md:380-387`). The other source is MP-1's `zero` per-playlist
     loops, exposed 2026-12-15.
   - The options are: Joseph frees HPSS space or decides; the risk is accepted because the files are regenerable event
     loops, at a cost this record does not measure; or 5B's development reads them before 2026-11-09 as real work.
2. **Proposed under the standing grant, if the director agrees:** an HPSS copy of 3b's npz inputs (about 21.5 G),
   with `hashcreate`/`hashverify` and an inventory, before 3b's declaration is bound. The ROOT event loops would stay on
   pscratch only. MP-1's 132 event-loop passes cost 3.913 node-h
   (`measurement-paper/phase1/mp1/S1-REPORT.md:102`); merges and dumps would add to a rebuild.
3. **For the pscratch list** (`pv-ladder-retention-reraise-20261120.md`): add `$P/measurement-paper/phase1/mp1/s1/`
   and `$P/w2-recoil-20261006/w2b/`, and the universe loops above, while the cheap tier runs.

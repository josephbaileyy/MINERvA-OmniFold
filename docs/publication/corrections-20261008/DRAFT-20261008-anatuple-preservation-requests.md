# DRAFTS for Joseph's review: requests about preserving the analysed AnaTuples (NOT SENT)

**Status: drafts only. Nothing here has been sent, filed or requested.** Sending any draft is an external act that
needs Joseph's explicit decision (goal 2026-10-08: "Do not send it or request a quota increase"). The figures come from
`RECORD-20261008-followups-g11-g12-preservation.md` §3 and §7; re-measure them before sending.

## A. To NERSC (HPSS allocation request, via the ERCAP allocation-change process or a help ticket)

> **Subject:** HPSS storage increase for project m3246 (user josephrb): archival copy of analysed MINERvA open-data
> files
>
> We request an increase of about **11 TiB** in HPSS storage for user josephrb under project m3246. It is for a
> one-time archival copy of the MINERvA open-data AnaTuples that our published analysis read: 2,374 files,
> 11,523,656,218,592 bytes (1,818 data files, 0.99 TB; 489 simulation files, 10.53 TB; 67 flux and parameter files,
> 0.16 GB).
>
> The files now sit only on Perlmutter scratch. They are an earlier production of the public MINERvA release, and the
> current public files of the same names differ, so a fresh download would not reproduce the analysis inputs. We have
> sha256 checksums for all 2,374 files (computed 2026-10-08/10) and would verify the archive against them after
> transfer.
>
> Current use: 350.9 GiB of a 512 GiB quota (2026-10-09). The copy would be written once with htar, then left untouched.

## B. To the MINERvA collaboration (open-data contact)

> **Subject:** Is the earlier ME FHC open-data production still retained?
>
> Our analysis of the MINERvA open data (medium-energy FHC, 12 playlists) used files downloaded before the current
> release. They are an earlier production: the current files of the same names are about 24% larger. To make our
> published analysis reproducible, we would like to know whether that earlier production is retained, and under what
> version tag or path, so that we can cite it rather than archive our own copy.
>
> We can supply a list of the 2,374 file names and sizes we used, with a sha256 checksum for each.

## C. To NERSC (help ticket: unreadable files on pscratch OST 61)

**Withdrawn 2026-10-10: not needed, never sent.** The hung reads all completed on 2026-10-09 at about 18:31 UTC, and
on 2026-10-10 all 7 files hashed normally (`RECORD-20261010-ost61-hashed-and-data-addition.md`). The text is kept as
drafted.

> **Subject:** Reads hang on pscratch files whose first stripe is on OST 61 (user josephrb)
>
> Seven files under `/pscratch/sd/j/josephrb/minerva/minerva_large_files/` cannot be read. `stat` or the first read
> blocks in uninterruptible I/O (D state, wait channel `cl_sync_io_wait`), and the process cannot be killed. The
> same seven files hung from `dtn01` and from `login05` between 2026-10-09 00:08 and 05:53 UTC. Every one has
> its first stripe on OST 61 (`lfs getstripe -i`), and they are the only files of this dataset that start there. The
> other 2,367 files, whose first stripes are on 365 other OSTs, read normally; OST 60 also hung on 2026-10-09 but
> recovered within hours. The files:
>
> - `Data/Playlist1E/MasterAnaDev_data_AnaTuple_run00016140_Playlist.root`
> - `Data/Playlist1F/MasterAnaDev_data_AnaTuple_run00016588_Playlist.root`
> - `Data/Playlist1F/MasterAnaDev_data_AnaTuple_run00016758_Playlist.root`
> - `Data/Playlist1G/MasterAnaDev_data_AnaTuple_run00018720_Playlist.root`
> - `Data/Playlist1G/MasterAnaDev_data_AnaTuple_run00019158_Playlist.root`
> - `Data/Playlist1M/MasterAnaDev_data_AnaTuple_run00019215_Playlist.root`
> - `MC/StandardMC/Playlist1O/MasterAnaDev_mc_AnaTuple_run00113376_Playlist.root`
>
> Could you check OST 61? We need only to read these files, once, to checksum them.

## What each answer would mean

- **A granted:** copy the MC (10.53 TB) and, if not already done, the data to HPSS with htar; verify against
  `ANATUPLE-SHA256.tsv`.
- **B answers yes, with a stable location:** cite it, and keep only the checksum manifest. A and the CFS data copy
  become optional.
- **Neither:** the event-level reproduction chain depends on purgeable scratch. Record that as a known limitation.
- **C fixed:** re-run the sweep script (it resumes, hashing only the missing files) to complete the manifest. (Done
  2026-10-10 without a ticket: the storage recovered on its own.)

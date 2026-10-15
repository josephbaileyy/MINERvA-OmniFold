# DRAFTS for Joseph's review: requests about preserving the analysed AnaTuples (NOT SENT)

**Status: drafts only. Nothing here has been sent, filed or requested.** Sending any draft is an external act that
needs Joseph's explicit decision (goal 2026-10-08: "Do not send it or request a quota increase"). The figures come from
`RECORD-20261008-followups-g11-g12-preservation.md` §3 and §7; re-measure them before sending.

> **Correction 2026-10-14, before any send:** only Playlist 1A (41 MC files and 253 Data files) differs from the
> current public release. 1B–1P match it, so "a fresh download would not reproduce the analysis inputs" holds for
> 1A only (`docs/orchestration/state/2d-closeout/stageD-inputs/q2-opendata-20261014/REPORT.md`). Revise A and B
> accordingly.
> **Done 2026-10-14:** A is revised to the 41 1A MC files, and B is dropped (below). Neither is sent.

## A. To NERSC (HPSS allocation request, via the ERCAP allocation-change process or a help ticket)

**Revised 2026-10-14, at Joseph's direction** ([`DECISION-20261014-joseph-2d-endpoint-and-open-items.md`](../../orchestration/DECISION-20261014-joseph-2d-endpoint-and-open-items.md)
item 5). The request now covers only the 41 Playlist 1A MC files. The figures are from
[`state/2d-closeout/preservation-20261014/REPORT.md`](../../orchestration/state/2d-closeout/preservation-20261014/REPORT.md),
measured 2026-10-14/15. Re-measure the HPSS line before sending. The 2026-10-08 text (about 11 TiB) is in git history.
**Not sent.**

> **Subject:** HPSS storage increase for project m3246 (user josephrb): archival copy of 0.71 TB of MINERvA
> open-data files that are no longer public
>
> We request an increase of **1 TiB** in HPSS storage for user josephrb under project m3246, from 512 GiB to
> 1.5 TiB. It is for a one-time archival copy of 41 MINERvA open-data simulation files that our analysis read:
> 706,929,079,280 bytes (658 GiB). They are the medium-energy FHC Playlist 1A simulation as released before January
> 2026. MINERvA has since replaced them with a reprocessing, and the current public files of the same names differ
> (checked by checksum). So these files can no longer be downloaded, and a fresh download would not reproduce our
> inputs.
>
> The rest of our inputs are covered without HPSS:
> - the other 448 simulation files are byte-identical to the current public release (adler32, checked
>   2026-10-14);
> - our data files are already preserved on project storage.
>
> The 41 files now sit only on Perlmutter scratch, where they become purge-eligible from December 2026. We hold a
> sha256 checksum for each and would verify the archive against them after transfer. Current use is 350.9 GiB of a
> 512 GiB quota (2026-10-14), so the copy does not fit today. It would be written once with htar and then left
> untouched.

## B. To the MINERvA collaboration (open-data contact)

**Dropped 2026-10-14, at Joseph's direction** (same decision, item 5). Q2 answered its question: the current release
is a reprocessing, and only our 1A files are the earlier one
([`q2-opendata-20261014/REPORT.md`](../../orchestration/state/2d-closeout/stageD-inputs/q2-opendata-20261014/REPORT.md)).
The 2026-10-08 text is in git history. **Not sent.**

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

- **A granted:** copy the 41 1A MC files (0.707 TB) to HPSS with htar, and verify them against `ANATUPLE-SHA256.tsv`.
- **A refused:** exact reproduction of the 1A MC depends on purgeable scratch. Record that as a known limitation. The
  fallback is to re-download the current 1A release and re-run the 1A event loop. The measured effect on the 2D
  result is of order 10⁻⁶ (`state/2d-closeout/stageD-inputs/q2-opendata-20261014/triage/REPORT.md`).
- **C:** withdrawn; see above.

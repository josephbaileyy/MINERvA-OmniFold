REF-G1 atime check (the director's request of 2026-11-05, after coverage-5b-audit reported atimes moved in REF-G1's
batch and timing windows). By limitation-resolver: a metadata-only stat (`stat -c "%X %Y %s %n"`, no file read) of the
734 bank and detector-dump files of the preconditions listing (../preconditions/listing.json, #775), taken from
saul.nersc.gov at 2026-11-05T15:34:02Z (stat-20261105T153402Z.txt: its first line is that time, then one line per file:
atime, mtime, bytes, path). atime_check.py compares it with the listing and with the batch receipts (../batch/); its
output is atime_check.txt (`python3 atime_check.py ../preconditions/listing.json stat-20261105T153402Z.txt ../batch`).

Finding (accepted by the director): REF-G1's universe units moved the atimes, by plain reads. ref_g1.py at M 609d8f24:
Run.universe calls s5p_universe.weights (np.load of each weight file, mmap_mode="r"; s5p_universe.py:89-100, blob
ee0a1e17 at M) and takes sha256 digests of the same files (ref_g1.py:236-238); Run.bank_cv np.loads cv.npz
(ref_g1.py:202-206). Detector bands read the detector dump; every other band reads the bank.
- Bank, 701 files: 669 moved, 2026-11-05T14:45-14:49Z (20, 165, 207, 198, 79 per minute): 167 universe tags x 4 weight
  files, and cv.npz (14:49:40Z). Unmoved: the bank's own 32 files of the 8 detector-band tags.
- Detector dump, 33 files: 32 moved, 14:48-14:49Z (8 tags x 4). Unmoved: detector-dump.json.
- Every one of the 175 non-CV universe units has its weight files' atimes inside its own predicted window (+-60 s),
  rebuilt from the job's start (14:42:06Z), each lane's GNU-time elapsed and the units' seconds; universe_CV reads no
  bank file.
- The timing job's one unit (universe_Flux_0, 11:11:03-11:12:14Z) reads cv.npz and Flux_0's four weight files: five
  by the code above. The batch re-read them, so their 11:11Z atimes are overwritten and cannot be re-measured.
- Counts, both stated, neither fitted to the other: coverage-5b-audit reported 412 files at 14:47-14:49Z and 7 at
  11:11Z (its stat time and population are not known to this lane); this stat (15:34:02Z) counts 516 in 14:47-14:49Z
  (484 bank, 32 detector) and 701 in 14:45-14:49Z.
- Exposed-from (oldest atime + 56 days) is unchanged, since each set's oldest atime is a file REF-G1 never read: bank
  2026-12-20T00:47Z (oldest 2026-10-25T00:47:00Z), detector dump 2026-12-26T19:01Z (oldest 2026-10-31T19:01:19Z), as
  in the listing. The files REF-G1 read are exposed from 2026-12-31T14:45Z on.

All 971 files of the listing (added by this lane, beyond the request): a second metadata-only stat of every listed file
at 2026-11-05T15:42:45Z (stat-all-20261105T154245Z.txt), compared per group by atime_groups.py (output
atime_groups.txt; `python3 atime_groups.py ../preconditions/listing.json stat-all-20261105T154245Z.txt`). Every file of
the other six groups also moved, by REF-G1's own runs:
- the batch (14:42-14:46Z): of_inputs_5d.npz and bkg_dump.npz at 14:42:21Z; the three L-5D-PV ratio files at
  14:45:22-14:45:41Z;
- the read (15:18:14-15:18:16Z, the minute of STOP.json's written_utc 15:18:16Z): all 50 (e) replicas, 175 (e)
  universes, the central, the 3 ladder unfolds and the 2 F0b closures, and IBU-1's D_N.npz (G-IBU1's plain np.load and
  sha256, ref_g1_read.py:399-404 at M).
- So D_N.npz, the set's earliest at the listing (exposed from 2026-12-18T15:04Z), is now exposed from 2026-12-31T15:18Z;
  the earliest exposed-from over all 971 files is now the bank's, 2026-12-20T00:47Z (32 detector-band copies REF-G1
  never reads). Each group's dates, at the listing and now, are in atime_groups.txt.

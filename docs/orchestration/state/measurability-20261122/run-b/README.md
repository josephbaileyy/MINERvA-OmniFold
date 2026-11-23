# MSR connect B: the build, rc 0 (2026-11-23, tier3-design)

The run had the director's GO for connect B (Joseph via the director, 2026-11-22), at package head `b8a2b4d9`: connect
`msr_build_connect.sh` 2a5c1c92, launcher 2620ae7a, M `68b9f96b`. cov2d's fence rev 3 (7e81a721) was embedded.
Declaration rev 4 with Amendment B.

- **Acks** (`lane/acks.tsv`, times from `date -u`): director-helper-3 07:54:20Z, cov2d 07:54:26Z, limitation-resolver
  07:55:10Z. The window ended at the oldest plus 900 s, 08:09:20Z (`lane/wend.txt`). limitation-resolver was told before
  the connect.
- **The session** ran on login38 and ended 07:58:45Z. ssh rc 0 and script rc 0. The tar `fetch-build.tar` (sha256
  a2e32880…, the log's) was fetched, and `RECORDS.SHA256SUMS` checked 16 files (`lane/launcher.out.txt`,
  `lane/records-check.txt`).
- **Fences and overlap:** cov2d's rev 3 was CLEAR, this lane's sacct fence was clear, and the overlap was CLEAR (1,596
  pairs).
- **Staged copies:** the probe's three copies (`msr-p-20261122/stage`) were re-checked by O_NOATIME sha256 at their pins
  (`cluster/logs/stage-recheck.jsonl`): of_inputs_5d.npz 07fccc1a…, bkg_dump.npz 2addac8f…, bank.npz 60416384….
- **Build**, one part per process (`cluster/logs/build-*.json`, `cluster/build/*.json`):

  | part | rc | wall | peak RSS | product sha256 |
  |---|---|---|---|---|
  | r5d | 0 | 41.2 s | 4,813,246,464 B | b54689e375e68590ccaae2e92ab2cc25567c8c35b71f4ed42c5d74f8ca168d10 |
  | r2d | 0 | 54.7 s | 5,602,426,880 B | 34275a665cc04ef72c2364d6c5f454ad26d0821c725299b0fb6a56e3c8cd36e4 |
  | t3 | 0 | 0.8 s | 52,428,800 B | 5eaca6fadf4b6eefe5814c279db0cc11a8a23fa8c4146fea0b7247262c2ca7db |

  Every part is under the 8e9 B cap. The probe had estimated 19.3 s (5D) and 56.5 s (2D), so the 5D wall time ran about
  twice the estimate, which is the probe's known limit. Peak RSS was close.
- **Products** (`cluster/build/`, with `SHA256SUMS` checked locally): r5d.npz, r2d.npz and t3.npz, with their json
  records. The H2 grid has 29 cells in the full build and in half A, and 28 in half B: one H2 cell has no truth in
  half B. The 2D known term is empty: no reco-passing signal row has truth outside the grid. The products are committed
  here under declaration §7 (the director's ruling of 2026-11-23). They are force-added past the repository's `*.npz`
  and `build/` ignore rules, as the other state records under `docs/orchestration/state/` are.
- **Deploy:** 0 porcelain lines after. Nothing was written to CFS. The IBUKT bank was read only as the staged copy. The
  probe's `$OUT` (`msr-p-20261122`) and B's `$OUT` (`msr-b-20261123`) stay on pscratch. Removing them is Joseph's call,
  after this record merges.

No reading has been computed. The local step (`msr_project.py`) gets its own GO.

Renamed records (git ignores `.err`, `.log` and `.out`) are listed in `RENAMES.tsv` with their sha256.
<!-- absence-ok: a build receipt; "no reading has been computed" states this study's own order of work -->

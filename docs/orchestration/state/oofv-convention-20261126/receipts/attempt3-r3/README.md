# OOFVC attempt 3 (r3): the run and its score

Run under OOFVC-BINDING-3 (#1411, `ea9a60393c135a5350ddc9df36bbb97618df398c`) with tool commit
`b8077dfc73a47823e1e9235020dab28953941f11`. The namespace was `/pscratch/sd/j/josephrb/oofvc-20261126-r3/`. Each step
had its own director GO, a cert check, and fresh cov2d and limitation-resolver acks. The bound shas were checked by
`shasum` before each launch, and the staged copy was checked on the node: `oofvc_dump.sh` 185c8b17, `oofvc_units.sh`
f67bd737, `oofvc_post.sh` 567938b9, `oofvc_launch.sh` 8f09ec2d.

## Steps

| step | job | result | files |
|---|---|---|---|
| dump-pilot (1L) | 62067464_7 | COMPLETED 0:0, 38 s | `pilot-launcher.txt`, `pilot-watch.txt`, `pilot-readout.txt` |
| dump-rest (11 playlists) | 62067601 | 11/11 COMPLETED 0:0, 42–323 s | `rest-launcher.txt`, `rest-watch.txt`, `rest-readout.txt` |
| units (join, then 4 units) | 62068236 | COMPLETED 0:0, 756 s | `units-launcher.txt`, `units-watch.txt`, `units-readout.txt`, `units-controls.txt` |
| post, fetch | none (login node) | rc 0. `post.tar.gz` sha256 `7e4fd78bc98c4d83a5283bed934cbf815683f3357a73e1e01cbdd69f14b70bc6` on both ends | `post-launcher.txt`, `fetch-launcher.txt` |

- **Dumps.** Every playlist's counts equal r2's. The totals are 91,390,364 entries and 21,156,240 selected, with to_bkg
  658,227 (equal to 43f8cc16's mc_background rows) and to_sig 20,498,013. dup_sig is 0, and routing_disagree is 0 in
  all twelve. The binary was 1579a71a, as in r2. The dump ROOT digests differ from r2's although every count is equal;
  the scorer depends on the join, not on dump bytes. Taken from the two readouts: 1L is f753ced1 in r3 against
  8c437178 in r2.
- **NuE (§2.7).** All twelve brackets are complete, with mtime_ns 1630424966000000000 and size 25403 unchanged. Each
  bracket shows that task's own read, not a global order. Lustre atime is not monotonic across clients: the r3
  pilot's "before" atime (1795740833000000000, 00:53:53Z) is earlier than r2 dump-rest's largest reported one
  (1795740848000000000, 00:54:08Z). cov2d raised this, and the two readouts confirm it.
- **CV omnifile.** It was staged by `dd iflag=noatime`, with atime unchanged before and after. The staged sha256s are
  43f8cc16 and d40aea69, as pinned.
- **Join (`units-controls.txt`).** C-READ, C-ROUTE, C-JOIN, C-SIGW and C-LAB all pass. C-JOIN matched 658,227 rows
  one to one with no ties, so the tie rule was never exercised and route B was not needed. 544,162 rows moved.
  rows_sha256 is `cbf34bd8cad0f4978dc1aea22713eb5057bf521118dc7ce8d10b93b30defcb03`.
- **Charge (`post/charge.txt` inside the archive).** dump 0.0078, units 0.2100, r3 total 0.2178 node-h. With attempts
  1 and 2 (about 0.042, BINDING-3), OOFVC used about 0.26 of its 2.0 cap.

`r3-records.tar.gz` is `post.tar.gz` repacked without `join/oofvc_rows.npz` (30,474,810 B). That file's sha256 is the
rows_sha256 above, and it remains in r3 on the cluster.

## Score

The scorer ran on the laptop: `oofvc_score.py` at ea9a6039 (its directory differs from b8077dfc only in
`launch/bound/`), in ew2d-env with ROOT 6.40. The arguments were `--tool-commit b8077dfc…` and `--tree`, a
`make_tree.sh archive` of 77d76cfc whose six shas equal the cluster deploy's (`make_tree.txt`). rc was 0.
`score.json.txt` (the scorer's stdout, sha256 `2933116671235cb989279c3d38468410a3e8df69189c0053539fb08414e135cb`)
records `controls_pass` true and `reading` "READ". Every control passes: C-IN, C-JOIN-RECORD, C-UNITS, C-PINS, C-KS,
C-BASE, C-FIX and C-MOVE. The N controls (C-NID, C-NSUM, C-NMOVED) pass in both c2 units, per each
`units/*/c2_central.oofvc.json` in the archive.

| ratio | value | band (§2.4) |
|---|---|---|
| r_IBU = D_IBU^R / D_IBU^0 = 0.19545 / 0.53805 | 0.3633 | LOWER |
| r_ER = D_ER^R / D_ER^0 = 2.21241 / 2.12144 | 1.0429 | LITTLE CHANGE |
| r_N = D_IBU^N / D_IBU^0 = 0.36577 / 0.53805 | 0.6798 | LOWER |
| r_RN = D_IBU^RN / D_IBU^0 = 0.20530 / 0.53805 | 0.3816 | LOWER |

These are the declaration's statements for these bands.
- **Primary:** "The reclassification moves the binned IBU's distance; at this scale it does not move the OmniFold
  central value's."
- **Secondary:** "Counting selected events in the efficiency numerator wherever they reconstruct moves the binned
  IBU's distance down."
- **E_R under N:** not applicable.

**Descriptive, read by no rule.**
- True 40–60 column ratio (ours / published): IBU_0 1.1303, IBU_R 1.0954, IBU_N 1.0558, IBU_RN 1.0176, ER_0 0.9345,
  ER_R 0.9212.
- Completeness above 1: none under off, and 205 cells (max 1.8643) under R.
- `score.json.txt` also holds D at every K and the class weights.

No reading names a cause (§2.4).

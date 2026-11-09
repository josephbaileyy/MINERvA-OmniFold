# s5e candidate R, A3: the 153 per-quantity rounding shifts (receipt)

The valid-region lane ran this on 2026-11-09, at the director's request and on the director's go for
`s5e_a3_extract.sh` at sha256 7c843f2950e3cc7cd5fa74a2d03a588ad0b5fa91d458414996b67dcdac1f2cf0. The ruling was
route (b): recompute with the receipt's own producer, not from review2's r2_cache.npz.

`../assess_receipt.json` (84266e30…) keeps only three summary values of A3's data-rounding probe: median
0.7829505732456221, max 2.5837789197284393 and argmax J145. Those are §6.1's "median 0.8, up to 2.6". This receipt
records all 153 values behind them, for the figures lane's rounding-instability figure:
`cluster/a3_rounding_shifts.csv`, sha256 9ac8f7d8b74f090c28efc9023a21729ef5505090864ee1459fd998667e2c3987.

**Pinned here for the first time.** No earlier committed record carries the sha256 of the 103 inputs or of review2's
r2_cache.npz. The search was `git grep -n -I "r2_cache"` over origin/main @ 65875111. It finds only the review2 scripts
that write or read the cache, none with a digest; no tracked JSON, TSV or MD file names it.
- The inputs' sha256 are recorded here, in `cluster/a3_rounding_shifts.json`, for the first time.
- The check that these are the same computation and the same bytes is an identity: the 153 values' median, max and
  argmax equal the receipt's three values exactly.

Search: git grep -n -I "r2_cache" origin/main (all file types) gives 5 lines in review2/r2_chaos.py, r2_load.py and r2_recompute.py, none a digest @ 65875111b9c913cc1b1c3696b3f896139a4abe51

CITABLE FOR: the 153 values, as s5e_analyze_candidate.py:147-151 @ 2f958652 computes them on the 103 inputs recorded
here; each value is max over the two jitteredge perturbations of |U f − U f_upcast| / σ_data, where σ_data is the SD over
the 100 data-bootstrap replicas. Also: their bitwise identity with the receipt's median, max and argmax; the inputs'
sha256, sizes and stats.
NOT CITABLE FOR: a digest of these inputs before 2026-11-09 (none was committed); r2_cache.npz, which was not read; any
wording.
<!-- absence-ok: the search above covers r2_cache; for the 103 product files, no committed jitteredge, upcast or boot digest was found by git grep -E "jitteredge|data_R_upcast|boot_b" with a 40+ hex digest on the same line @ 65875111 -->

## What ran

The producer computes the shifts inline in `main()`. `cluster/a3_extract.py` (15f9b923…) executes four of its lines
verbatim, `s5e_analyze_candidate.py:147, 148, 150 and 151` @ 2f958652, whose text has sha256 01aee82c…:

```
        dsig = np.array([load_fn(f, U)["f"] for f in sorted(glob.glob(str(A / "data" / "boot" / "boot_b*.npz")))]).std(0, ddof=1)
        up = load_fn(A / "data" / "data_R_upcast.npz", U)["f"]  # float64 handling, same values: the probe's baseline
        jit = [np.abs(load_fn(f, U)["f"] - up) / dsig for f in sorted(glob.glob(str(A / "data" / "data_R_jitteredge*.npz")))]
        jmax = np.max(np.array(jit), axis=0)
```

- **What was supplied.** Two names the lines use, and nothing else:
  - `load_fn` reads each file once through O_NOATIME, records its sha256 and its stat before and after (a change is a
    STOP), and hands the bytes to the producer's own `s5e_analyze_candidate.load_fn`, unchanged.
  - `glob.glob` returns the committed file list (`../review2/r2_integrity.json`: assess/data holds data_R,
    data_R_upcast, data_R_jitteredge1 and 2, and boot_b1 to boot_b100). So no directory was listed, and the
    producer's own `sorted()` sets the order.
- **U and names** come from the producer module's `s5c_coverage.reported_functionals` on the frozen s5c contract
  (d54fd7c9…, unchanged since c29dde25), as its `main()` does at :101. The 153 names equal the receipt's
  `functional_names`.
- **The summary** uses the expression of :153-154, `{"median": float(np.median(jmax)), "max": float(jmax.max()),
  "argmax": names[int(jmax.argmax())]}`, which the script asserts is present in the file.
- **The gate.** The summary must equal the receipt's three values exactly (float ==, and the name); otherwise a STOP
  with only STOP.json. It passed: `"match": {"median": true, "max": true, "argmax": true}`. Read back from the
  committed CSV alone, the median, max and argmax are again 0.7829505732456221, 2.5837789197284393 and J145.

## The session (`lane/extract-session.txt`; the connect's log is `cluster/extract.log.txt`)

- **The session.** One foreground ssh session on login09, from 2026-11-09T23:38:29Z to 23:39:21Z, with ssh rc 0 read
  unpiped.
  - The connect was staged in /dev/shm and checked at its sha256, then removed.
  - iris's m3246 row was printed. `squeue --me` lists only the two ll5d_gate jobs (log lines 4-6).
  - No process on the node named s5e-20260925 (line 7). <!-- absence-ok: the connect's own pgrep listing, line 7 -->
- **The deploy.** A fresh clone at 2f958652 into the run's own directory `/pscratch/sd/j/josephrb/s5e-a3-extract-20261109`,
  with 0 porcelain --ignored lines before (line 8) and after (line 23).
  - The producer cc00829e… (line 9) and the contract d54fd7c9… (line 10).
  - assess_receipt.json from 843fc99e at 84266e30… (line 11).
  - a3_extract.py at its pin (line 12).
- **The run.** root_6_28's python 3.11.14 and numpy 1.26.4, with -I -B, threads 1, nice 19, ionice idle, and the local
  test override unset (lines 13-15). The JSON records `"o_noatime": true` and `"local_test": false`.
  - All 103 inputs were read once, each stat unchanged across its read.
- **What was written.** Only the run's own directory; nothing in s5e's tree. `out/` holds the CSV and the JSON (lines
  19-22). The connect ended rc 0 (line 24).
- **The fetch.** scp into a new empty directory. Every sha256 matches the log.

## Files

- `cluster/a3_rounding_shifts.csv`: index, name, shift_over_data_sigma; 153 rows in the receipt's functional order;
  floats as Python repr.
- `cluster/a3_rounding_shifts.json` (93f5f2e1…). It holds:
  - the producer's sha, its lines and their text's sha;
  - the contract and the receipt, with their shas;
  - the computed summary and the match;
  - numpy, python and the threads;
  - each of the 103 inputs' sha256, bytes and stat before and after;
  - the CSV's sha.
- `cluster/s5e_a3_extract.sh` (the connect, 7c843f29…), `cluster/a3_extract.py`, `cluster/extract.log.txt`,
  `cluster/extract.done` and `cluster/clone.log.txt` (empty).
- `lane/extract-session.txt` holds the session.
- `lane/make_fixture.py` is the local check at 0 node-h, in a clean clone of 2f958652. It builds a synthetic 103-file
  tree and a receipt from the producer's lines run the plain way (np.load and a real glob).
  - On that tree, a3_extract.py's 153 values were bitwise equal to the plain run's.
  - With one jitteredge file perturbed, it stopped with only STOP.json.
  - A wrong lines sha was refused.
- **Renames.** The two names git ignores carry ".txt" (`RENAMES.tsv`). Their contents are unchanged.
- **The binding inventory.** The JSON's `"producer": {"path", "sha256"}` pair is one new receipt binding,
  nd-unfolding/s5e_analyze_candidate.py at cc00829e.
  - Following the director's ruling (a) and the 107233af precedent, this PR moves `verify_hash_bindings.py`'s
    RECEIPT_BINDING_COUNT from 166 to 167, and its digest from 6a2ac974 to 18818a17.
  - The delta and the power test are in `binding-delta.txt`, with outputs in `lane/power-test-flipped.txt` and
    `lane/power-test-restored.txt`, from `lane/binding_delta.py`.

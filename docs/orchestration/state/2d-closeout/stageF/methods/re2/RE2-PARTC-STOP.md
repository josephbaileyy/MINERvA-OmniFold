# RE-2 part C: the bound run's stop at C13, and the fix for amendment 1 (2026-10-24, re-1 lane)

**Status.** The run of part C bound by `RE2-BINDING-C.md` (`e079ff05`) stopped at C13, the values table, with exit
3. Under the binding's strict rule it stopped and was reported to the director, and nothing was repaired in place.
- The director accepted the fix design on 2026-10-24, with four conditions.
- The director writes `RE2-BINDING-C-AMENDMENT-1` binding this fix's commit.
- Nothing refined runs again until that amendment is on `main`.

**MEASURES:** the stop, its cause, and the fix's tests. **CANNOT AUTHORIZE:** the rerun, which is the amendment's.

## 1. The stopped run

**Preflight.** On login12 at 2026-10-24T14:32:21Z, the deploy `deploy-e079ff05` was at
`e079ff05447cd36e754654f94b166a6481d3005a`, clean. `sha256sum -c` of the declaration's §12 gave **25 of 25 OK**
([`run/partc_stopped/partc_preflight/preflight.log`](run/partc_stopped/partc_preflight/preflight.log)).

**The steps.** `bash re2c_run.sh refined <deploy> $B/partc` ran **35 steps at rc 0**, C1 to C12, in about 2 minutes:
- analyze ×5, rollup, export_cov, the four period steps, playlist, combine, build_q;
- χ² ×3, ours_only ×3, Figs. 6/7, the stat figures, check_rebuild;
- the five receipts and four figure producers;
- reduce, numbers, cmodel.

So every in-chain control passed:
- the May control, the block-sum control and the period control;
- CB-18;
- the VL175 budget and group-median controls;
- CR-02/03;
- C_model's two controls.

**C13 then exited 3** ([`run/partc_stopped/partc/logs/steps.tsv`](run/partc_stopped/partc/logs/steps.tsv),
[`values.log`](run/partc_stopped/partc/logs/values.log)):

```
{"rows": 251, "unexpected": 1, "control_pass": 242, "new_products": 8, "changes": 199, "refined": true, "declared_fails": 1}
UNEXPECTED s2-bkg-share N/sec_systematics.tex:101 control PASS 0.26  "no key 'sigma_bkg_over_sigma_stat_median' in path 'numbers.bkg_separable.sigma_bkg_over_sigma_stat_median'"
```

`chain.json` and `SHA256SUMS` were not written, because they follow C13. The run's files are listed with their
digests in [`run/partc_stopped/partc_preflight/partc_stopped.SHA256SUMS`](run/partc_stopped/partc_preflight/partc_stopped.SHA256SUMS)
(128 files; sha256 `f2e517c40ef48b93…`). The file was written beside the run, so `$B/partc` itself is unchanged.

**The records committed here:**
- [`run/partc_stopped/partc_preflight/`](run/partc_stopped/partc_preflight/): the preflight log, the run's stdout,
  and the §12 check file;
- [`run/partc_stopped/partc/logs/`](run/partc_stopped/partc/logs/): every step's log, `steps.tsv` and `run.txt`;
- [`run/partc_stopped/partc/values_table.tsv`](run/partc_stopped/partc/values_table.tsv) and `.json`: the stopped
  table, with the failed row.

## 2. The cause

**Which row.** Row `s2-bkg-share` regenerates `sec_systematics.tex:101`'s "0.26", S2's σ_bkg/σ_stat median, from
`s5.json`'s `numbers.bkg_separable`.
- S2 (J5) is not bound.
- So the refined rollup records `bkg_separable` as "not computed: S2 (J5) was not run in the refined arm (S5-22)". <!-- absence-ok: quotes the refined s5.json's own field, and J5's status is RE2-BINDING-B's (not bound) -->
- The row has no refined value. The engine counts that as an error.

**Why the declaration's test missed it.** Its stand-in refined tree copied the purity `s5.json`, which has the key.
A fixture built from the purity records cannot know which keys the refined arm leaves out.

**The other 250 rows** all resolved against the real refined records.

## 3. The fix (the director's conditions 1 and 4)

**Spec.** `s2-bkg-share` moves from `re2c_values_spec.tsv` to `re2c_values_unmatched.tsv`, with this reason: "S2
(J5) not run in RE-2, so the refined rollup does not compute the bkg-only separable term (S5-22); a purity-only
diagnostic; integration rewords it as purity history."
- The spec has 250 rows.
- The unmatched list has 25: the 22 sites integration handles by hand, and the 3 exact-split sites classified as
  unchanged.

**The test is now built from the world** (condition 1):
- **The fixture.** `re2c_refined_schema.py` reads the stopped run's real refined records, the 18 sources the spec
  reads, and writes `fixtures/refined_schema.json`.
  - For JSON: every key path, each leaf's type, each list's length, and verbatim any value that says something was
    "not computed" or "not run".
  - For printouts: the text with every decimal number masked to 1.0.
  - It records each source file's sha256 from the stopped run.
  - Integers and integer-mantissa labels such as `1e-04` are kept, because the spec's regexes anchor on them.
- **The stand-in.** `test_re2c.py` builds its stand-in refined tree from the fixture and asserts that the tree's
  schema equals the fixture's. Every spec row must then resolve.
- **The mutation.** Restoring `s2-bkg-share`, as its exact original line, must fail. It does.

**The test on the old spec and the new one:**

```
old spec (e079ff05): (3, ['s2-bkg-share'])     # rc 3, the one unresolved row
new spec:            (0, [])
```

The first version of the fixture masked `1e-04` and `1e-12` as values and failed three rows on the new spec as
well: `rank-paperV`, `tens-73-chi2` and `tens-73-modes`. Those rows resolve on the real records, so the mask was
fixed, not the spec.

**Determinism is a stop** (condition 2). `re2c_determinism.py` compares every file the rerun shares with the stopped
run, byte for byte. Before comparing, it maps the rerun's own namespace and deploy path in its bytes to the stopped
run's.
- It excludes, each named in its output:
  - `logs/`, `mpl/`, and any path with a `tmp` component. The period selftest writes into a `mkdtemp` directory with
    a random name (`periods_ns/tmp/tmp8lbdy9iq/` in the stopped run), and its verdict is in `periods/selftest.json`,
    which is compared. (The director found this one at `d57da592`.)
  - ROOT files, which carry the TFile time. Each is compared through the npz written from the same arrays:
    - `s5/uq_production_covariance.root` through `s5/production_cov.npz`. build_q's A2 checks
      (`re2c_build_q.py:387-393`) stop unless its total, universe and every band equal the npz's to 1e-12 of the
      matrix maximum. This is not exact equality.
    - `outA/uq_adopted_covariance.root` through `outA/cov2d_Q_205.npz`'s `Q`.
    - `outA/block_stat.root`, `block_c08.root` and `block_playlist.root` through `cov2d_Q_205.npz`'s `stat`, `c08`
      and `C_PL`. They are written from those arrays at `re2c_build_q.py:704-706`, and the npz at `:713-715`.
      build_q's read-back (A4, `:678-692`, `:710`) stops unless each ROOT matrix equals its array exactly.
      `block_stat.root`'s `hRel2D` is √diag(stat)/x of the same arrays.
  - PDFs, which carry a creation date, are compared through their PNG twins. All 22 have one.
  - The values table, whose spec is what changed.
  - Four named JSON fields that record when, where and from which commit a receipt ran:
    - `receipt_model_chi2.json`'s `generated_utc` and `host`;
    - `RECEIPT-agreement-windows.json`'s `hostname` and `git_head_at_run`.

    The rest of each of those two files is compared exactly, as parsed JSON.
- **The sweep for other run-specific names** in the stopped tree covered hostnames, ISO times, `nid` names, pids,
  the mkdtemp name and the deploy commit, in every file outside logs, ROOT and PDF.
  - It found only those four fields and the `mkdtemp` directory.
  - The deploy path (`deploy-e079ff05`, in 7 records) and the output namespace are handled by the path pairs.
- Only `chain.json` and `SHA256SUMS` may be present in the rerun alone.
- Any other difference stops the run before C10.

**Tests:** `python3 -m unittest test_re2c` passes 20 of 20. The new ones are the schema stand-in, the mutation, the
moved row's listing, and three determinism cases:
- runs that differ only in their `mkdtemp` name and run-context fields PASS, and a changed value beside those fields
  FAILs;
- a changed byte FAILs;
- a one-sided product FAILs.

## 4. Digests

**The changed files.** Exactly 3 of the declaration's 25 files changed. The other 22 are byte-identical to §12
(`sha256sum -c`: 22 OK).

| file | status | sha256 |
|---|---|---|
| `2d-unfolding/re2/partc/re2c_values_spec.tsv` | changed | `51319f678ca409c874519d6c677bc5b15cf3cc06d6d957075153b88998aa742b` |
| `2d-unfolding/re2/partc/re2c_values_unmatched.tsv` | changed | `afb20e38190275b4c0c3c92035b9a36d772906edf1e10dc7b929b51f812c8149` |
| `2d-unfolding/re2/partc/test_re2c.py` | changed | `20ef0ba7223bc68127e724ed30abd1ab8a1a59a136699e4fbd27c76fe4c3b599` |
| `2d-unfolding/re2/partc/re2c_refined_schema.py` | new | `f37b87bb0c95f129aab89cfa06c517075ba2c39f0a892ed4e37160971ea12da9` |
| `2d-unfolding/re2/partc/re2c_determinism.py` | new | `fe950d2bd9240f404a76222aabfb0463f68a7e8406d41587a27688cac816d729` |
| `2d-unfolding/re2/partc/re2c_tracked.py` | new | `571fc4e0f0d3160953ba2b705c316a56743aa5304b31eca28f1702905a3eee66` |
| `2d-unfolding/re2/partc/fixtures/refined_schema.json` | new | `d47d65dd278253ab4b354b786a4572f7fadedca33d10c7f7b0380169146873c1` |

**The rerun, as proposed for the amendment:**
1. A clean deploy of this commit.
2. The same preflight, against the declaration's §12 with the rows above replacing it.
3. `re2c_run.sh refined` into `$B/partc-r2`.
4. `re2c_determinism.py --stopped $B/partc --rerun $B/partc-r2` with the namespace and deploy path pairs; a FAIL
   stops before C10.
5. C10, C14 and the report, as bound.

## 5. Every `run/` path named here is tracked

`python3 -I 2d-unfolding/re2/partc/re2c_tracked.py RE2-PARTC-STOP.md` (output at commit):

```
docs/orchestration/state/2d-closeout/stageF/methods/re2/RE2-PARTC-STOP.md: 8 run/ paths
  tracked  run/
  tracked  run/partc_stopped/partc/logs/
  tracked  run/partc_stopped/partc/logs/steps.tsv
  tracked  run/partc_stopped/partc/logs/values.log
  tracked  run/partc_stopped/partc/values_table.tsv
  tracked  run/partc_stopped/partc_preflight/
  tracked  run/partc_stopped/partc_preflight/partc_stopped.SHA256SUMS
  tracked  run/partc_stopped/partc_preflight/preflight.log
all tracked
```

## 6. The rerun's determinism stop, and the fix for amendment 2 (2026-10-24)

**The rerun, under amendment 1.**
- **Preflight:** on login12 at 16:17:32Z, the deploy was `903fb78b941a2f889bfcc5092e41ce27f5add898`, clean.
  `sha256sum -c` over the amendment's 29 rows gave **29 of 29 OK**
  ([`run/partc_r2/partc-r2_preflight/preflight.log`](run/partc_r2/partc-r2_preflight/preflight.log)).
- **The chain:** `re2c_run.sh refined` into `$B/partc-r2` ran **36 steps at rc 0**.
  - C13 read 250 rows: 241 controls PASS, 8 new products, 1 declared failure and 0 unexpected.
  - It wrote `chain.json` and `SHA256SUMS`.
  - `$B/partc` is untouched ([`run.out`](run/partc_r2/partc-r2_preflight/run.out)).

**The determinism stop: FAIL, rc 1** ([`determinism.json`](run/partc_r2/partc-r2_preflight/determinism.json), sha256
`b7085a8b…`; argv in [`determinism.argv`](run/partc_r2/partc-r2_preflight/determinism.argv)).
- It compared 66 files: 60 equal, 6 differ, 0 one-sided.
- The run stopped before C10 and was reported to the director, with nothing repaired.

**The 6 differences.** A field-by-field diff shows that every differing value is a recorded sha256 of another file:

| file | the differing fields |
|---|---|
| `s5/s5.json` | the S5 ROOT's own digest |
| `pins_q.json` | the s5_root, s5_json and combination_json digests |
| `outA/budget_Q.json` | 7 input-pin and provenance digests of the same three |
| `playlist/playlist_term.json` | `inputs.analysis_json.sha256` |
| `combination/combination.json` | `inputs.analysis_json.sha256` |
| `outA/SHA256SUMS` | the 4 outA ROOT files, `budget_Q.json` and `cov2d_Q_205.json` |

**Why.** Each digested file is one of two kinds:
- a ROOT file, which carries the TFile time;
- a record that is equal after the path pairs, but whose raw bytes name the run's namespace.

The path pairs cannot reach the digest of a path-bearing file. No measured value differed, and every npz is
byte-equal. The director's review had not caught this cascade either.

**The fix (amendment 2, the director's conditions 1–5).** Only `re2c_determinism.py` changes, plus its tests in
`test_re2c.py`.
1. **Learned digest pairs.** A pair (rerun digest → stopped digest) is learned only from a file proven equal: by
   exact bytes after the path pairs and the pairs already learned, or by the declared JSON-field rule.
   - It is applied only to a whole 64-hex token.
   - Learning iterates to a fixpoint. Any digest still differing there leaves its file differing, which is a FAIL.
2. **ROOT pairs come only from the fixed `ROOT_TWINS` table:**
   - `s5/uq_production_covariance.root` → `s5/production_cov.npz`;
   - `outA/uq_adopted_covariance.root`, `block_stat.root`, `block_c08.root` and `block_playlist.root` →
     `outA/cov2d_Q_205.npz`.

   A ROOT pair is learned only when its twin is byte-equal. A ROOT file missing from the table fails the run.
3. **The record.** Every pair is listed in `determinism.json` with the file it was learned from and its reason
   (`equal`, `json-rule` or `root-twin <twin>`), and the fixpoint iteration count is given.
4. **Tests,** each in the direction it acts. `python3 -m unittest test_re2c` passes 25 of 25:
   - (a) a path-bearing record whose digest a second record holds PASSES;
   - (b) a ROOT digest FAILS when its twin differs by one byte;
   - (c) a changed value in a record that also holds learned digests FAILS;
   - (d) a 64-hex digest that matches nothing learned FAILS;
   - (e) a ROOT file not in the table FAILS.

**A pre-binding dry check, disclosed.** The new comparator was run once over the two existing trees. It read
`$B/partc` and `$B/partc-r2` and wrote only `$B/review/det-dry/determinism.json`
([`run/partc_r2/determinism_dry_amend2.json`](run/partc_r2/determinism_dry_amend2.json)).
- It gave **PASS**: 66 of 66 equal, 27 learned pairs in 4 fixpoint iterations, none untabled.
- The pairs: 5 `root-twin`, 2 `json-rule` (the two receipts), and 20 `equal`.
- It is not the bound verdict. The bound one comes from a clean deploy of the amendment-2 commit, after
  `sha256sum -c` of `$B/partc-r2`'s own `SHA256SUMS` (the director's condition 6).

**Scope and digests (condition 5).** Of the 29 files bound by amendment 1, only these two change. The other 27 are
byte-identical.

| file | sha256 |
|---|---|
| `2d-unfolding/re2/partc/re2c_determinism.py` | `84951a8f75a650104bbfa1ff6a23e0739559b974305b16412144b5f28ff01739` |
| `2d-unfolding/re2/partc/test_re2c.py` | `87ac367fcb64af49ff6d88db72a223e27d8df9a967a15ba99330ae467c781507` |

**The proposed determinism rerun, for the amendment:**
1. `sha256sum -c` of `$B/partc-r2/SHA256SUMS`, logged and required all OK.
2. A clean deploy of the amendment-2 commit, in a separate directory.
3. `re2c_determinism.py` with the same two path pairs, writing `$B/partc-r2_preflight/determinism-amend2.json` beside
   the first verdict, which is kept. Nothing is written into `$B/partc-r2`.
4. On PASS, C10, C14 and the report.

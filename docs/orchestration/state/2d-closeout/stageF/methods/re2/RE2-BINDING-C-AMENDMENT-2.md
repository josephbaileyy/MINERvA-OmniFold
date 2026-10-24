# RE-2 part C binding, amendment 2: the determinism comparator learns digest pairs (2026-10-24)

**By** the paper-tighten lane, as director. **Amends** [`RE2-BINDING-C.md`](RE2-BINDING-C.md) and
[`RE2-BINDING-C-AMENDMENT-1.md`](RE2-BINDING-C-AMENDMENT-1.md) (PR #323).

**What happened.** The bound rerun (deploy `903fb78b`, preflight 29 of 29 OK) completed into `$B/partc-r2`: 36 steps,
all rc 0. C13 gave 250 rows: 241 controls PASS, 8 new, 1 declared failure and 0 unexpected. The determinism stop then
returned FAIL, with 60 of 66 files equal and 6 differing, and the run stopped before C10, as bound.
- **Every differing field is a recorded sha256 of another file.** Each digested file is either a ROOT product, whose
  TFile time differs, or a record that compares equal after the path pairs but holds the namespace path in its raw
  bytes. No numerical value differs, and every npz product is byte-equal. The field-by-field diff is in
  `RE2-PARTC-STOP.md` §6, and the failed verdict is in `run/partc_r2/` (`b7085a8b…`).
- **The defect was in the comparator's design, and the director's review of #322 missed it.** Path pairs change raw
  bytes, so any digest of a path-bearing record cannot match.

**The fix**, PR #324, head `d108286c43091b06f5c8321265041c9460c4c27a`, merged at `8c5ce1ff`. Only `re2c_determinism.py`
and `test_re2c.py` change among the 29 bound files.
- A digest pair is learned only from a file proven equal: by exact bytes after the path pairs and the pairs already
  learned, or by the declared JSON-field rule.
- It is applied only to whole 64-hex tokens, and learning iterates to a fixpoint. A digest still differing at the
  fixpoint leaves its file differing, which is a FAIL.
- ROOT pairs come only from the fixed `ROOT_TWINS` table, and only when the twin npz is byte-equal:
  - `s5/uq_production_covariance.root` → `s5/production_cov.npz`;
  - the four `outA` ROOT files → `outA/cov2d_Q_205.npz`.
- An untabled ROOT file is a FAIL.
- Every pair is listed in `determinism.json`, with its source file, its reason and the iteration count.

**The director's checks, at `d108286c`:**
- 25 of 25 tests pass, including tests (a)–(e), each in the direction it acts.
- The other 27 bound files are unchanged against amendment 1's table.
- The learning loop: pairs come only from compared-equal files or the twin table, and the substitution applies to
  whole 64-hex tokens only.
- Manifest `--check`: OK. Hash bindings: intact. CI: success.

**The disclosed pre-binding dry check** (`run/partc_r2/determinism_dry_amend2.json`) is accepted as a record, not as
the verdict. It was read-only over the two trees and wrote only under `$B/review/det-dry/`. It gave PASS: 66 of 66
files equal, with 27 learned pairs in 4 iterations (20 equal, 5 root-twin, 2 json-rule) and no untabled ROOT file.

## Amendment

**No product is regenerated.** `$B/partc-r2` was produced by the bound code at `903fb78b`, and no chain step reads the
comparator. Only the determinism step reruns, under the new comparator.

**The bound files** are the 29 below. The director re-hashed all 29 at `d108286c`: 29 of 29 OK. They are amendment
1's table with `re2c_determinism.py` and `test_re2c.py` replaced.

**The order:**
1. Run `sha256sum -c` of `$B/partc-r2/SHA256SUMS`, written by the run, and log its output. Every entry must be OK,
   or the run stops.
2. Make a clean deploy of `d108286c` in a separate directory. Run `sha256sum -c` over the 29 rows below, and log its
   output, `git rev-parse HEAD` and the argv.
3. Run `re2c_determinism.py` with the same two path pairs, writing `$B/partc-r2_preflight/determinism-amend2.json`
   beside the failed first verdict. Nothing is written into `$B/partc-r2`.
   - A FAIL stops the run before C10. Report it to the director.
4. On PASS, run C10, C14 and the report as amendment 1 binds them. C10's `re2c_fig1_local.sh` is unchanged. The report
   must:
   - state that the determinism verdict came from the amendment-2 comparator, over the products of `903fb78b`;
   - include the failed first verdict and its 6 differences;
   - include the dry check.

**Everything else in RE2-BINDING-C and amendment 1 stands.**

## The bound files (29)

| file | sha256 |
|---|---|
| `2d-unfolding/re2/partc/fixtures/refined_schema.json` | `d47d65dd278253ab4b354b786a4572f7fadedca33d10c7f7b0380169146873c1` |
| `2d-unfolding/re2/partc/make_diffs.sh` | `9a3cb6839111b9988042a357b52dda6c64f273b0915682c02950515655f65a6b` |
| `2d-unfolding/re2/partc/pin_siblings.py` | `9679d4db21365b63210a27f95022be5031a6efa3ef83b6a6ca05c3bcf3f7f68b` |
| `2d-unfolding/re2/partc/re2c_analyze_periods.py` | `708cfc2fec29b80019bebbf84cc3a354aff02031f1669904fae680ede21c8a59` |
| `2d-unfolding/re2/partc/re2c_analyze.py` | `4789b36d9c6d1d9979e272544f0a6d4bd46e675779b699983f59d1ba88c587f0` |
| `2d-unfolding/re2/partc/re2c_audit.py` | `280ee00742e7b89912e6cb2b1e01558f94ffe675762081c3abe37bdbdddc5605` |
| `2d-unfolding/re2/partc/re2c_build_q.py` | `45fafddb6e44e88386d6b10b605b635315ef09e3d31ef1da5e8a71a913d1fe97` |
| `2d-unfolding/re2/partc/re2c_check_rebuild.py` | `f7feca72a17ce43ba740162e380320a6e62eae57926116e85e1476eb4b1c9246` |
| `2d-unfolding/re2/partc/re2c_cmodel.py` | `cd8fbf09635c2854d2e68f6f1274add500d722aa21552e9fd665403f836b3072` |
| `2d-unfolding/re2/partc/re2c_combine.py` | `2f5d2ea3161d7f5c3a389fb697e5aa5a745b6565334e2bba1a10d0f5ceb15301` |
| `2d-unfolding/re2/partc/re2c_determinism.py` | `84951a8f75a650104bbfa1ff6a23e0739559b974305b16412144b5f28ff01739` |
| `2d-unfolding/re2/partc/re2c_dryrun.sh` | `3c6084c5c64d7f9fd79b780da059dcfa2602506753e8157e21e37ec078a917e0` |
| `2d-unfolding/re2/partc/re2c_export_cov.py` | `524ef62e79947dbc16c5a59e860e166a05a03f27cc60ad80ac07709e1d947a3f` |
| `2d-unfolding/re2/partc/re2c_fig1_local.sh` | `02c3090f22790ca50f9d762b2d766bd07918dd2e7cdec12cc33099b9adc20e9a` |
| `2d-unfolding/re2/partc/re2c_fig1.py` | `9d7eb17700d33fd77696c3d7af49e22dd943d4bb8495eda974d7bba119873b99` |
| `2d-unfolding/re2/partc/re2c_k1roll.py` | `166d5c09da3c95e8e949dacb5a3f78832c5366ed2ad18e99048e25eb6c2d186c` |
| `2d-unfolding/re2/partc/re2c_numbers.py` | `8d5f06a86ee25e087ffa46745cf2c24d568c9cb43a937c2f23cc14b058123787` |
| `2d-unfolding/re2/partc/re2c_periods.py` | `19f2c3934f93a34cc7d20202f83152421bdb0db044380bd8601216bcdb95dd9f` |
| `2d-unfolding/re2/partc/re2c_playlist_term.py` | `24ac48d86a76cc00c9dbf175f460baa1239947941fffdf57cad8c98b804383e8` |
| `2d-unfolding/re2/partc/re2c_reduce.py` | `e03df3f88a7e609d8787bd0ee8e22fbe319d2afa7dcaf97f67b006073c05e381` |
| `2d-unfolding/re2/partc/re2c_refined_schema.py` | `f37b87bb0c95f129aab89cfa06c517075ba2c39f0a892ed4e37160971ea12da9` |
| `2d-unfolding/re2/partc/re2c_rollup.py` | `53840b0bc687511995466b74bef185412f0b4db3244f170e6204629b516b74d8` |
| `2d-unfolding/re2/partc/re2c_run.sh` | `ff66c7a9faa3529f1a84582fc3df2cfaea43a20016c01523077bbb7880fcf589` |
| `2d-unfolding/re2/partc/re2c_tracked.py` | `571fc4e0f0d3160953ba2b705c316a56743aa5304b31eca28f1702905a3eee66` |
| `2d-unfolding/re2/partc/re2c_values_spec.tsv` | `51319f678ca409c874519d6c677bc5b15cf3cc06d6d957075153b88998aa742b` |
| `2d-unfolding/re2/partc/re2c_values_unmatched.tsv` | `afb20e38190275b4c0c3c92035b9a36d772906edf1e10dc7b929b51f812c8149` |
| `2d-unfolding/re2/partc/re2c_values.py` | `b5d645021e3d876c852794a5d1a14d12aed1375f75c08ad0be0c80350a8c0e3e` |
| `2d-unfolding/re2/partc/test_re2c.py` | `87ac367fcb64af49ff6d88db72a223e27d8df9a967a15ba99330ae467c781507` |
| `docs/orchestration/state/2d-closeout/stageF/methods/re2/run/launch/re2_hpss.sh` | `3db768d559958ef02984fdd1096fee3270705f70be912f91cde2c4be9404b0ce` |

The determinism step may rerun once this record is on `main`.

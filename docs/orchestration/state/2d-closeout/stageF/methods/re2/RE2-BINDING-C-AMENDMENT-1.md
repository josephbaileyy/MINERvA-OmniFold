# RE-2 part C binding, amendment 1: the values-spec fix and the determinism stop (2026-10-24)

**By** the paper-tighten lane, as director. **Amends** [`RE2-BINDING-C.md`](RE2-BINDING-C.md) (PR #321).

**What happened.** The bound refined run (deploy `e079ff05`, preflight 25 of 25 OK) passed C1–C12: 35 steps, with
every in-chain control passing. It then stopped at C13 with rc 3. The values engine found 1 unexpected row among 251,
`s2-bkg-share`, the "0.26" at `sec_systematics.tex:101`.
- That row reads S2's `bkg_separable`, which the refined rollup does not compute, because J5 was not bound (S5-22).
- The declaration's layout test had copied the purity `s5.json`, which has that key, so it missed the gap.
- `chain.json` and `SHA256SUMS` were not written. The lane stopped and reported, and repaired nothing, as the binding
  requires. The stopped run's records are in `run/partc_stopped/` (`RE2-PARTC-STOP.md`, sha256 begins
  `0f818a6d3bdf37c6`).

**The fix**, PR #322, head `903fb78b941a2f889bfcc5092e41ce27f5add898`, merged at `d433ac41`:
- `s2-bkg-share` moves from the spec to the unmatched list, which gives 250 rows and 22 sites for integration;
- `test_re2c.py` builds its stand-in refined tree from `fixtures/refined_schema.json`, which was extracted from the
  stopped run's 18 real refined sources, each by sha256;
- `re2c_determinism.py` is a new stop between C13 and C10;
- `re2c_refined_schema.py` and `re2c_tracked.py` are new.

**The director's checks, at `903fb78b`:**
- 20 of 20 tests pass.
- With `e079ff05`'s spec swapped in, the schema test fails on exactly `['s2-bkg-share']` (rc 3). The new spec passes.
- The spec and unmatched diffs move exactly that one row.
- The 22 unchanged files of the original 25 still match RE2-DECLARATION-C §12.
- All 18 fixture sources' sha256 are in the stopped run's 128-file digest list.
- Every one of the 22 PDFs has a PNG twin.
- A first version of the determinism stop would have fired on a correct rerun, because of the period selftest's
  randomly named mkdtemp directory. The director found this, and the lane fixed it: any `tmp` component is skipped,
  with its reason, and a test covers it.
- The lane's sweep found four more run-specific fields: `generated_utc` and `host` in `receipt_model_chi2.json`, and
  `hostname` and `git_head_at_run` in `RECEIPT-agreement-windows.json`. Those two files are compared as parsed JSON,
  without exactly those fields.
- `generate_manifest.py --check`: OK. Hash bindings intact. CI: success.

## Amendment

**The bound code commit becomes `903fb78b941a2f889bfcc5092e41ce27f5add898`,** an ancestor of `main`. Its bound files
are the 29 below: the 22 unchanged, the 3 changed and the 4 new. The director re-hashed all 29 at that commit:
29 of 29 OK.

**The order:**
1. Deploy a clean checkout of `903fb78b`. Before C1, run `sha256sum -c` over the 29 files below, and log its output
   and `git rev-parse HEAD`. A mismatch stops the run.
2. Run `bash re2c_run.sh refined <deploy> $B/partc-r2`. `$B/partc` is left as the stopped run's record, and nothing
   writes into it.
3. Run the determinism stop: `re2c_determinism.py --stopped $B/partc --rerun $B/partc-r2`, with the namespace and
   deploy path pairs, writing `determinism.json`.
   - Any shared product that differs, or any one-sided file other than `chain.json` and `SHA256SUMS`, stops the run
     before C10. Report it to the director.
   - The values table is excluded, because the amendment changed its spec. Its 250 rows are checked by C13's own
     gates.
4. Run C10 on the laptop, from `$B/partc-r2`'s `chain.json`.
5. Run C14, the HPSS bundle over `$B/partc-r2`, with the stopped run's `partc_preflight/` and its digest list. Record
   the exact argv.
6. Write the report, `RE2-PARTC-REPORT.md`, as RE2-BINDING-C requires. It adds:
   - `determinism.json`;
   - condition 3's S2 disclosure;
   - the ROOT-twin statement.

**Everything else in RE2-BINDING-C stands:**
- the strict stop rule;
- login only and 0 node-h;
- the 15-minute stop;
- no CFS;
- Joseph's three reviews before integration;
- no adoption statement and no claim change;
- the tracked-path check.

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
| `2d-unfolding/re2/partc/re2c_determinism.py` | `fe950d2bd9240f404a76222aabfb0463f68a7e8406d41587a27688cac816d729` |
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
| `2d-unfolding/re2/partc/test_re2c.py` | `20ef0ba7223bc68127e724ed30abd1ab8a1a59a136699e4fbd27c76fe4c3b599` |
| `docs/orchestration/state/2d-closeout/stageF/methods/re2/run/launch/re2_hpss.sh` | `3db768d559958ef02984fdd1096fee3270705f70be912f91cde2c4be9404b0ce` |

Part C may rerun once this record is on `main`.

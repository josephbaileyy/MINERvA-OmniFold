# F6: `driver_p1.py` reaches `2d-unfolding/` on `main` (identity record)

**Owner:** 2D closeout executor (2d closer), directed by the paper-tighten lane under
AUTHORIZATION-20261012-2d-closeout-delegation.md.

This closes the condition carried by the 2026-10-15 production binding, ruling 1
([`AUTHORIZATION-20261015-2d-closeout-stageC-production-binding.md`](../../../../AUTHORIZATION-20261015-2d-closeout-stageC-production-binding.md)),
and kept by the packing binding §4: `driver_p1.py` reaches `2d-unfolding/` on `main` through its own reviewed PR
before Stage F adoption ([`../CHECKLIST.md`](../CHECKLIST.md) F6).

**CITABLE FOR:** the identity of `2d-unfolding/driver_p1.py` on `main` with the bytes and import resolution that
produced the Stage C production outputs listed below.
**NOT CITABLE FOR:** any result, adoption or claim; any change to the production driver
`unfold_2d_omnifold_unbinned.py`; the environment at job time beyond what is stated here.

## 1. What changes

One file is added: `2d-unfolding/driver_p1.py`, a byte copy of
[`../../stageC/pilot/p1/driver_p1.py`](../../stageC/pilot/p1/driver_p1.py):
- sha256 `3056e625a22f2ee79621e515aa5a76a4685662ac6fc10ee7e832680dde087578`, 125,698 bytes, mode 100644;
- `cmp` against the pilot copy: identical.

Nothing else in `2d-unfolding/` changes. The pilot copy stays where it is (the pilot and production packages, their
manifests and `p1/SHA256SUMS` cite it there).

## 2. Which production outputs these bytes produced

`sbatch_prod.sh` runs `cd $REPO/2d-unfolding` and then `python3 driver_p1.py …` for these rows only (lines 85–124),
after `p1_check` verifies `3056e625…` at `$REPO/2d-unfolding/driver_p1.py` (line 79):

| item | jobs | the analysis check that records `3056e625` |
|---|---|---|
| C0 `2dc_P_C0_unit` | 1 | `analyze_prod.py` `c0`, `prov(u, P1_SHA, …)` (line 142): PASS |
| S1 | 300 | `replicas("S1")`, `prov(p, P1_SHA, …)` (line 258): 300/300 |
| S2 | 100 | the same: 100/100 |
| S4(i) (`S4B`) | 80 | the same: 80/80 |

That is 481 of the 531 jobs, the number binding ruling 1 accepted. 480 of them ran as members of regular-QOS packs
(including `S1_001`–`004` in the smoke pack). The other 50 jobs, including the 35 G2 members (S4U, S4CV), ran the
production driver `unfold_2d_omnifold_unbinned.py` (`74a4ed69…`), which is already on `main` and is not touched
here. The production REPORT is [`../../stageC/production/REPORT.md`](../../stageC/production/REPORT.md) (PR #150,
merge `55e6f44d`).

## 3. Identity check performed

**Kind: byte and import-graph identity.** No unfold was re-run. A re-run would need a job submission, which this
lane's grants do not cover without a new request.

### 3.1 The whole directory is byte-identical

Production ran the driver from two deployed trees, `$NS/repo/2d-unfolding/` (`git archive 4139548b`) and
`$NS/repo_k/2d-unfolding/` (`git archive c873cc22`), each with `driver_p1.py` copied in
(`NS=/pscratch/sd/j/josephrb/2d-closeout-stageC-production-20261015`).
- `git diff 4139548b origin/main -- 2d-unfolding/` and `git diff c873cc22 origin/main -- 2d-unfolding/` are empty
  at `main` `c2be4ae0`.
- Every file of `main`'s `2d-unfolding/` plus this `driver_p1.py` (197 files,
  [`main_plus_driver_2d-unfolding.sha256`](main_plus_driver_2d-unfolding.sha256)) equals every file found on disk
  in each deployed directory (`find -type f`, 197 files each:
  [`deployed_repo_2d-unfolding.sha256`](deployed_repo_2d-unfolding.sha256),
  [`deployed_repo_k_2d-unfolding.sha256`](deployed_repo_k_2d-unfolding.sha256)): `diff` empty for both. Neither
  deployed directory has a `__pycache__` or any other extra file.

So `sys.path[0]` (the script's directory) has the same contents when the driver runs from `main` as it had in
production.

### 3.2 Import resolution

The driver's imports (`grep` of `driver_p1.py`): `argparse`, `contextlib`, `inspect`, `io`, `math`, `array`,
`hashlib`, `json`, `os`, `sys`, `numpy`, `ROOT`; inside functions `sklearn`, `xgboost`, `lightgbm` (estimator
choice); and `omnifold`, after `main()` inserts the absolute path
`/pscratch/sd/j/josephrb/MINERvA-OmniFold/unbinned_unfolding/python` at `sys.path[0]` (lines 2161–2165).

Resolved with `importlib.util.find_spec` on a saul login node (login04, 2026-10-17T23:25:12Z), in the jobs'
environment (`setup_salloc_env.sh`; `root_6_28`, Python 3.11.14), with `sys.path[0]` set to each deployed
`2d-unfolding/` ([`import_resolution.txt`](import_resolution.txt)). No module code was executed:
- every standard-library and third-party module resolves inside the `root_6_28` environment, and none inside
  `2d-unfolding/`, for both trees;
- `omnifold` resolves to `…/unbinned_unfolding/python/omnifold.py`, sha256
  `e96234124a31edd7a8dd61fdb16cb48a5b28cbd1b90202f59b0095868378227a`, which is `HELPER_SHA` in `sbatch_prod.sh`
  (line 26), checked by every production job (line 71).

The helper's own imports ([`omnifold_helper_imports.txt`](omnifold_helper_imports.txt)): `ROOT`, `numpy`,
`sklearn`, `pickle`, `os`, `sys`, `array`, and conditionally `xgboost`, `lightgbm`, `omnifold_nn_core`. No file or
directory in `2d-unfolding/` has any of these names, nor `omnifold`, nor any name the driver imports, so nothing in
the directory can shadow them. `pickle` resolves to the environment. `omnifold_nn_core` does not resolve; it is
imported only for the neural-network estimator, and every production row ran `--estimator lgbm`.

### 3.3 Path differences

- **`driverFile` provenance string.** `run_provenance` records `os.path.abspath(__file__)` (line 1386). Run from a
  `main` checkout, that string names the checkout's path instead of `$NS/repo{,_k}/2d-unfolding/driver_p1.py`. It is
  a record, not an input: no computation reads it. `driverSha256` (line 1397) is unchanged.
- **The helper path** is absolute in the driver, so it is the same from any checkout.
- No other path in the driver depends on its own location (`grep` for `__file__`, `dirname`, `Path(`, relative
  `../`: only lines 1382–1397, the provenance records).

## 4. Limits

- **Same model.** This record's verifier is the same model as its executor (§5).
- **No re-run.** Identity is shown by bytes and import resolution, not by reproducing an output.
- **Environment measured now.** The import resolution was measured on 2026-10-17 in the current `root_6_28`
  environment, not recorded at job time. The jobs ran 2026-10-15 to 2026-10-17 in the same named environment; the
  helper's digest was checked in every job, the third-party package versions were not.
- **pscratch paths.** The helper lives on pscratch, outside the repository, as it did for production.

## 5. Independent review

Pending: the executor's fresh read-only verifier, then the director's review on the PR.

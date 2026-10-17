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
(including `S1_001`–`004` in the smoke pack). The other 50 jobs (C0_cv 1, S3 10, and the 39 G2 rows: 35 S4U and
4 S4CV) ran the production driver `unfold_2d_omnifold_unbinned.py` (`74a4ed69…`), which is already on `main` and
is not touched here. Of those 39 G2 rows, 35 ran as pack members from `repo_k` and 4 S4U rows on the shared QOS
from `repo`. The production REPORT is [`../../stageC/production/REPORT.md`](../../stageC/production/REPORT.md) (PR #150,
merge `55e6f44d`).

## 3. Identity check performed

**Kind: byte and import-graph identity.** No unfold was re-run. A re-run would need a job submission, which this
lane's grants do not cover without a new request.

### 3.1 The whole directory is byte-identical

Production ran the driver from three deployed trees, each a `git archive` with `driver_p1.py` copied in
(`NS=/pscratch/sd/j/josephrb/2d-closeout-stageC-production-20261015`):
- `$NS/repo/2d-unfolding/` (`4139548b`): C0_unit;
- `$NS/repo_k/2d-unfolding/` while at `8ea086eb`: the smoke pack 59860260 (`S1_001`–`004`, 2026-10-16
  19:03–19:13Z; `stageC/production/evidence/smoke_pack/smoke_pack_59860260.txt` line 1). That tree was moved aside
  when `c873cc22` was deployed at 20:37:10Z and survives at `$NS/tmp/repo_k.8ea086eb.retired.20261016T203710Z/`
  (its `.deployed_commit` reads `8ea086eb…`);
- `$NS/repo_k/2d-unfolding/` at `c873cc22`: the other 476 pack members.

`git diff <commit> origin/main -- 2d-unfolding/` is empty for each of `4139548b`, `8ea086eb` and `c873cc22`, at
`main` `c2be4ae0`.
- Every file of `main`'s `2d-unfolding/` plus this `driver_p1.py` (197 files,
  [`main_plus_driver_2d-unfolding.sha256`](main_plus_driver_2d-unfolding.sha256)) equals every file found on disk
  in each deployed directory (`find -type f`, 197 files each:
  [`deployed_repo_2d-unfolding.sha256`](deployed_repo_2d-unfolding.sha256),
  [`deployed_repo_k_2d-unfolding.sha256`](deployed_repo_k_2d-unfolding.sha256),
  [`deployed_repo_k_8ea086eb_retired_2d-unfolding.sha256`](deployed_repo_k_8ea086eb_retired_2d-unfolding.sha256)):
  `diff` empty for all three. None has a `__pycache__` or any other extra file.
- "Identical to `main`" means a clean checkout of `main`. The live cluster checkout
  `/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding` (not used by production) also holds `__pycache__/` and
  untracked data directories; the verifier found no untracked `.py` file and no name that could shadow an import
  there.

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
  `2d-unfolding/`, for both trees measured (`repo`, `repo_k`; the retired `8ea086eb` tree is byte-identical to them,
  §3.1);
- `omnifold` resolves to `…/unbinned_unfolding/python/omnifold.py`, sha256
  `e96234124a31edd7a8dd61fdb16cb48a5b28cbd1b90202f59b0095868378227a`, which is `HELPER_SHA` in `sbatch_prod.sh`
  (line 26), checked by every production job (line 71).

The helper's own imports ([`omnifold_helper_imports.txt`](omnifold_helper_imports.txt)): `ROOT`, `numpy`,
`sklearn`, `pickle`, `os`, `sys`, `array`, and conditionally `xgboost`, `lightgbm`, `omnifold_nn_core`. No file or
directory in `2d-unfolding/` has any of these names, nor `omnifold`, nor any name the driver imports, so nothing in
the directory can shadow them. `pickle` resolves to the environment. `omnifold_nn_core` is imported only in the
helper's neural-network branch, after the helper's own lines 227–231 insert `<helper>/../../nd-unfolding` into
`sys.path` (it then resolves to `/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/omnifold_nn_core.py`); it
does not resolve before that insert. That branch never ran: every production row passed `--estimator lgbm`
(`sbatch_prod.sh:83`).

### 3.3 Path differences

- **`driverFile` provenance string.** `run_provenance` records `os.path.abspath(__file__)` (line 1386). Run from a
  `main` checkout, that string names the checkout's path instead of `$NS/repo{,_k}/2d-unfolding/driver_p1.py`. It is
  a record, not an input: no computation reads it. `driverSha256` (line 1397) is unchanged.
- **The helper path** is absolute in the driver, so it is the same from any checkout.
- No other path in the driver depends on its own location (`grep` for `__file__`, `dirname`, `Path(`, relative
  `../`: only lines 1382–1397, the provenance records).
- **cwd-relative defaults.** Four argparse defaults are relative to the working directory: `--omnifile
  runEventLoopOmniFold.root` (line 1400), `--out 2d_crossSection_omnifold.root` (1422), `--mcfile
  runEventLoopMC.root` (1424), and `--flux-universe-file baseline_flux/flux_integral_universes_MEFHC.root` (1429;
  read only with `--universe Flux:N`, lines 1774–1776). None applied in production: every `driver_p1` row passed
  absolute `--omnifile`, `--mcfile` and `--out` (`sbatch_prod.sh:83, 88, 120, 124`) and none passed `--universe`.
  A future run from a `main` checkout that relies on these defaults reads from its own cwd.
- **Scratch files.** Measuring this record left `$NS/tmp/f6_repo_2du.sha` and `$NS/tmp/f6_repo_k_2du.sha` in the
  production namespace's `tmp/`, identical to the committed `deployed_repo*.sha256`.

## 4. Limits

- **Same model.** This record's verifier is the same model as its executor (§5).
- **No re-run.** Identity is shown by bytes and import resolution, not by reproducing an output.
- **Environment measured now.** The import resolution was measured on 2026-10-17 in the current `root_6_28`
  environment, not recorded at job time. The jobs ran 2026-10-15 to 2026-10-17 in the same named environment; the
  helper's digest was checked in every job, the third-party package versions were not.
- **pscratch paths.** The helper lives on pscratch, outside the repository, as it did for production.

## 5. Independent review

**Executor's verifier** (fresh, read-only, detached worktree at `fa11e3fd`, git-dir ≠ git-common-dir; same model as
the executor). **Verdict: APPROVE WITH CHANGES, 1 MATERIAL, 5 MINOR**; the code change itself was confirmed.

It confirmed, by its own measurement:
- the diff: the only `2d-unfolding/` change is the new file; same blob `18d08daa`, mode 100644, 125,698 bytes;
- every line citation; the 481/531 split from `jobs.tsv`;
- an empty `2d-unfolding/` diff from `4139548b`, `c873cc22` and `8ea086eb` to `c2be4ae0`; its own streamed hashes
  of `repo`, `repo_k` and both retired `repo_k` copies (197 files, 18 directories each, no `__pycache__`, no
  symlinks), all equal to `fa11e3fd`'s tree;
- imports from its own AST walk of the driver and helper, resolved with `find_spec` in the jobs' environment (none
  inside `2d-unfolding/`; helper `e9623412…`); importing the libraries (not the driver) with `repo_k` as
  `sys.path[0]` loaded 1,325 modules, none from the tree (numpy 1.26.4, sklearn 1.8.0, lightgbm 4.6.0, xgboost
  3.2.0, ROOT 6.28/12; versions today, not at job time);
- the provenance of all 481 `driver_p1` outputs: `driverSha256` `3056e625…` and helper `e9623412…` in every one;
  `driverFile` is `$NS/repo/2d-unfolding/driver_p1.py` for C0_unit and `$NS/repo_k/2d-unfolding/driver_p1.py` for
  the 480 members;
- `generate_manifest.py --at-sha fa11e3fd --check`: OK.

| finding | disposition |
|---|---|
| M1 §3.1 omits the third tree, `repo_k` at `8ea086eb`, which ran the smoke pack (4 outputs) | §3.1 names all three trees; the retired tree's hash list is committed and equals `main` + driver |
| m2 cwd-relative argparse defaults not mentioned | listed in §3.3, with why none applied in production |
| m3 `omnifold_nn_core` "does not resolve" holds only before the helper's own `sys.path` insert | §3.2 corrected |
| m4 "the 35 G2 members" wording | §2: 39 G2 rows, 35 pack members from `repo_k`, 4 shared from `repo` |
| m5 two scratch hash files left in `$NS/tmp/` | named in §3.3 |
| m6 "identical to `main`" means a clean checkout; the live cluster checkout has extra untracked files | scoped in §3.1 |

**Director's review:** on the PR.

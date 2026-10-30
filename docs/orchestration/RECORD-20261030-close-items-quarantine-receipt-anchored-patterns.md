# RECORD — a correction beside the k=0 quarantine receipt: "Both anchored patterns" are at least eight (2026-10-30)

**By** the close-items session, on the director's order of 2026-10-30 (backlog candidate 2, read-only). Measured at
`064496cd6` (`main` when the receipt was written) and at `origin/main` `c3acf1616`.

**Corrects, beside it:** [`state/RECEIPT-20260822-quarantine-member-k000000-stale-replicas.json`](state/RECEIPT-20260822-quarantine-member-k000000-stale-replicas.json),
`destination.justification[2]`. **The receipt is not edited.** It stays the record of what was written on 2026-08-22.

**From:** the second finding in OI-160's row, carried to the director when OI-160 retired
([`RECORD-20261030-close-items-oi160-closed.md`](RECORD-20261030-close-items-oi160-closed.md)).

**MEASURES:** nothing on the cluster. Repository reads only.
<!-- absence-ok: a scoping statement about this record's own method -->

**CITABLE FOR:** the population of code sites that read 5D bootstrap replica paths at both revisions, and whether
each can name the quarantine destination.

**NOT CITABLE FOR:**
- the receipt's other justifications: the recursive-walker bullet, the `mii/` bullet and the filesystem bullet;
- the quarantined files' integrity or durability, which ruling 16 (`c4cfbe811`) recorded;
- any change to a launcher.

## 1. The sentence, and what is wrong with it

The receipt, `destination.justification[2]`, verbatim:

> NO path component equals boot_nd_5d. Both anchored patterns -- sbatch_finalize_5d_bkgaware_gpu.sh:167 and
> mii_stage0_distinctness.py:103 -- require a literal boot_nd_5d directory component.

**"Both" is a universal over an incomplete list.** At the receipt's own `main`, `064496cd6`, eight code sites read a
5D bootstrap replica path through a literal `boot_nd_5d` component, not two (§2). The receipt names two of them.

**The conclusion survives.** The destination is `/pscratch/sd/j/josephrb/quarantine/20260822-member-k000000-stale-replicas`.
It is absolute, outside the repository root, and has no `boot_nd_5d` component. Every one of the eight joins
`boot_nd_5d` onto the working directory `nd-unfolding/`, onto a `mii/member_kNNNNNN/` prefix, or onto a `member_root`.
None of them can resolve to the destination. OI-160's row reached the same judgement.

## 2. The population

Search: `git grep -n -E "boot_nd_5d|res_boot_" <rev> -- '*.sh' '*.py'` at `064496cd6` (64 lines, 27 files) and at
`c3acf1616` (83 lines, 36 files). Each hit was classified as a writer (`--out`, `OUT=`, `mkdir`), a reader, a test or a
comment. The readers of 5D bootstrap replicas are below. The 4D, FPS and `boot_nd_5d_ai1` readers name other
directories, so they are left out.

**Anchored on a literal `boot_nd_5d` component**: eight sites at `064496cd6`, each still present at `c3acf1616`:

| # | site at `064496cd6` | at `c3acf1616` | what it does | base it joins onto |
|---:|---|---|---|---|
| 1 | `sbatch_finalize_5d_bkgaware_gpu.sh:167` | `:422` | `combine_cov_nd.py --glob "$(mr_prefix boot_nd_5d)/res_boot_*.npz"` | the member prefix (`lib_member_resume.sh:138-142`) |
| 2 | `mii_stage0_distinctness.py:103` | `:103` | `glob(os.path.join(member_root, "boot_nd_5d", "res_boot_*.npz"))` | `member_root` |
| 3 | `run_budget_5d.sh:15` | `:15` | `combine_cov_nd.py --glob 'boot_nd_5d/res_boot_*.npz'` | `$REPO/nd-unfolding` |
| 4 | `sbatch_combine_5d_budget.sh:14` | `:14` | the same glob | `${REPO}/nd-unfolding` |
| 5 | `sbatch_bootstrap_5d.sh:12` | `:12` | `rg_skip_if_complete "boot_nd_5d/res_boot_${ID}.npz"`, the resume skip | `${REPO}/nd-unfolding` |
| 6 | `sbatch_bootstrap_5d_gpu.sh:74-75` | `:313-314` | `mr_skip_if_complete "$(mr_prefix "boot_nd_5d/res_boot_${ID}.npz")"`, the resume skip the receipt's hazard is about | the member prefix |
| 7 | `boot5d_packed_loop.sh:20`, `:30` | `:20`, `:30` | `ls boot_nd_5d/res_boot_*.npz \| wc -l`, a progress count in a log line | `$REPO/nd-unfolding` |
| 8 | `sbatch_boot5d_gpu_interactive.sh:44` | `:44` | the same progress count | `$REPO/nd-unfolding` |

- **Sites 1, 3 and 4** are the three `combine_cov_nd.py` population validators. The receipt named only site 1.
- **Sites 5 and 6** are resume skips, the mechanism the quarantine was made to defeat.
- **Sites 7 and 8** only count files for a log line.

**Parameterized: the directory is an argument, so no literal component anchors them.**
- `anchor_coincidence_displacement.py:63` globs `os.path.join(d, "res_boot_*.npz")`, with `--boot-dir` defaulting to
  `boot_nd_5d` (`:134`). It is present at both revisions.
- `s5c_assemble.py:137` globs `f"{a.boot_dir}/res_boot_*.npz"`. It is present at `c3acf1616` only.
- `combine_cov_nd.py:46` globs whatever `--glob` it is given. Sites 1, 3 and 4 above are its callers.

These three reach the destination only if someone passes its absolute path. Their defaults and their committed callers
do not.

**Hits that name the namespace but open no replica file:**
- `seed_offset_policy.py:398`, a scope regex;
- `seed_offset_policy.py:609`, a write guard's list of archive namespaces a member must not write under;
- `z_build_path.py:113-141`, declared populations;
- the tests under `nd-unfolding/tests/`, which build their own fixtures.

**Fixed paths in the OI-160 run tools:** `state/oi160-reproduction-20261029/run_job.sh:57` and
`state/oi160-tolerance-20261029/run_array.sh:49`. These name `$N/boot_nd_5d/…` under the canonical checkout's
`nd-unfolding`, and ran read-only once each in 2026-10.

## 3. Addresses carried with the finding

- **OI-160's row cited the two extra sites as** *"`run_budget_5d.sh:15`, `sbatch_combine_5d_budget.sh:16`"*. The first
  address is right. The second is wrong: `sbatch_combine_5d_budget.sh:16` is the `seedscan_split_5d` glob, and the
  `boot_nd_5d` glob is `:14`, at both revisions.
- **`RECORD-20261030-close-items-oi160-closed.md:45-46`** repeats the row's `:16`. That record is ARCHIVAL, and this one
  carries the correction.
- **`QUESTION-20261028-trunk-stat-ml-replica-provenance.md:29`** cites the pair as `:14,16`. That is correct: one line
  for `C_stat`, one for `C_ML`.

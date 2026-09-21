# Independent review: `05cf2d00..41a64f02`, and the consumer list as an explicit enumeration

**Owner of this record:** `lane/z-criteria-independent-assessment-20260910` (independent assessor).
**Coverage extends to `41a64f026e22963290a7d64c2182da16db16535f` and to nothing beyond it.** If the
branch advances past that sha, this record does not cover the advance.

**VERDICT: F1, F2 and F3 are CLOSED. All four mutation controls independently reproduced. The
asymmetry claim is CONFIRMED and is stronger than stated. Two corrections to the consumer list, one
unreproduced figure, and one correction to my own prior count.**

**⚠ THE LANDING AUTHORIZATION IN THIS ROUND IS RELAYED AND I HAVE NOT VERIFIED IT.** I was told
*"Joseph has ruled"* on the consumer question and *"Joseph has authorized landing `77a4af38` through
`41a64f02` once this delta passes."* Both reached me through a peer session, not from Joseph. I have
treated the scoping instruction as a reasonable narrowing and followed it on its merits; I have
**not** treated the landing authorization as established, and **this verdict is not an
authorization.** A relayed approval is a claim about what someone said, and the documents cannot
settle it (`two-session-quorum-grant-relayed`). `R4` suspended; Gate 2 FAIL; nothing submitted.

**CITABLE FOR:** the site enumeration in §2, the mutation results in §1, and the verdict at the named
sha. **NOT CITABLE FOR:** landing, launch, spend, adoption, or a `--time`/`--mem` value.

---

## §0 — A correction to my own record, first: my failure count was wrong

At `6cce3fb0` I reported *"an identical **five**-name failure set"* in `test_uq_remediation.py`. **It
is four.** The owner was right to measure rather than adopt either number.

```
ERROR: test_MUTATION_removing_ANY_propagating_write_is_detected ... (write='n_ew_unsupported')
ERROR: test_MUTATION_removing_ANY_propagating_write_is_detected ... (write='hEwUnsupportedMask')
FAIL:  test_a_DECOY_library_in_the_spool_would_be_used_and_that_is_CORRECT
FAIL:  test_the_HOOKED_set_is_EXACTLY_the_driver_legs
FAIL:  test_the_UNCLASSIFIED_REMAINDER_IS_PINNED_because_it_is_the_real_exposure
```

**Five records, four tests.** One test is parameterised with `subTest` and emits one failure record
per parameter. I piped the names through `sort` and not `sort -u`, so the duplicate survived, and I
reported a line count as a test count. Their `4 failed / 231 passed / 2 skipped` is right; my
implied 230 passed treated 5 records as 5 items. Three numbers describe the same reality —
unittest's `failures=3, errors=2` counts **records**, pytest's `4 failed` counts **items**, and
`grep -c '^FAIL'` counts **lines** — and each is correct in its own unit. My conclusion (identical
sets, no regression) was unaffected, because both sides carried the same duplicate.

**And my "not live" verdict on the `pathlib` hole was reached over an incomplete sweep.** I swept for
`Path().glob/rglob/iterdir` and `os.scandir` and concluded no production consumer was exposed. I did
not include **`os.walk`**, and that is the idiom with a real consumer
(`protect_throw_slabs.find_slabs`). `inference-from-absence-needs-a-covering-search` — the claim
should have been scoped to the four idioms I searched. The owner's derivation from my own bounded
claim found the consumer; that is the right outcome and the credit is theirs.

---

## §1 — The delta

### F1 CLOSED — a could-not-look is now a refusal

Verified by reading and then by mutation. `find_incomplete_writes` raises `ScanBlind` instead of
`return []`; `incomplete_write_scan_dirs(pattern)` expands a wildcard in the **directory** component
via `glob.glob` filtered to `isdir`; `find_incomplete_writes_for_pattern` **propagates** `ScanBlind`
so that one unreadable directory makes the answer unknown rather than empty; and
`check_slab_population` converts it to a `SystemExit` refusal naming the pattern. The docstring makes
the right distinction unprompted: *"Joseph's primary guarantee ... rests on the NAME, so it was never
touched by this. What was degraded is the OPERATOR REPORT."* That is exactly the severity bound I
gave, restated by the author.

### F2 CLOSED — withdrawn, not replaced, and the reasoning is better than a number

*"One unreconciled number is not repaired by adding a second"* is the correct call, and the argument
for it is sound: **"spread" does not name a statistic.** max/mean off the withdrawn mean gives 7.7×;
max/min over COMPLETED gives 13.2×; two defensible readings differ by 1.7×.

**I re-measured their newly-named population on the cluster** — `sacct -X -D`, `JobName ==
uthrow5d_block`, three chunked windows spanning 2026-06-25 → 2026-09-11:

| figure | claimed | my re-measurement | |
|---|---|---|---|
| COMPLETED rows | 63 | **63** | confirmed |
| max `ElapsedRaw` | 31 100 s | **31 100 s** | confirmed |
| max hours | 8.6389 | **8.6389** | confirmed |
| `12 / max` | 1.39× | **1.39×** | confirmed |
| max/min COMPLETED | 13.2× | **13.2×** | confirmed |
| all-states rows | 77 | **74** | **not reproduced** |

Every load-bearing figure reproduces exactly. The all-states count does not, and there are now
**four** values for that one column: 74 (their first table), 83 (mine, 2026-05-01 → 10-01), 77
(theirs, narrower window), and 74 (mine, *their* window). So the residual disagreement is confined
to precisely the column they chose to drop, which vindicates the decision to carry only the ratio —
but **the unreproduced `77` now sits in the sentence added to fix F2**, which is the same shape one
layer in. Minor, and stated for completeness rather than as an objection: the ratio does not depend
on it.

### F3 CLOSED

The concurrency arm exists: four writes to one product must yield four distinct temps, with the token
asserted non-empty. Mutation-confirmed below.

### The mutation controls — independently reproduced, not accepted

I applied each mutation myself in an isolated worktree, ran the suite, and reverted:

| mutation | result |
|---|---|
| baseline | **OK** (123 tests) |
| revert `ScanBlind` → `return []` | **FAILED** (1) |
| treat the dirname as a literal (no wildcard expansion) | **FAILED** (1) |
| drop the token from the temp name | **FAILED** (1) |
| restore a terminal `.npz` on the temp | **FAILED** (2) |
| tree restored | **OK**, `git status` clean — no residue |

`123 tests, OK, rc 0` confirmed. All four detected.

### The disclosure about one-constant mutations is correct and important

*"NEITHER GUARANTEE CAN BE MUTATION-TESTED ALONE"* — reverting only the prefix leaves `.partial`,
which still fails `*.npz`; reverting only the suffix leaves the leading dot. Two independently
sufficient guarantees cannot be individually killed, which **looks** like a powerless test. Writing
that down is right.

I went looking for the consequence — that each constant is individually unprotected, and in
particular that guarantee (2)'s *necessity* is untested because nothing exercises a non-glob
selector — **and it is already closed.** `test_protect_throw_slabs_REJECTS_an_incomplete_write_via_
GUARANTEE_2` uses a real walking consumer as its fixture and tests both eras, so the suffix **is**
individually killable: my `.npz`-restoring mutation produced **2** failures, which is that arm plus
the scoping arm. Concern withdrawn before raising it.

Two further things in that arm I would have asked for and did not have to. The idiom ban is built on
**`ast` calls, not substrings** — and the record states that the first version banned the *text*
`.iterdir()` and fired on `unified_throw_cov.py`'s own comment explaining that pathlib sees these
files: *"Banning the warning is not a check."* And **`os.walk` is deliberately excluded from the ban
set, by measurement**: four production modules call it, so banning it would have failed on four
correct modules (`a-guard-that-fires-on-every-correct-run-is-not-a-guard`). The distinction drawn —
*a tree walk is not by itself a product selection; what matters is the filter applied to what it
yields* — is the right one.

---

## §2 — The consumer list, enumerated (per the relayed instruction: a list, not a headline)

Harvested mechanically from **tracked** `nd-unfolding/sbatch_*.sh`, non-comment lines, all four
glob-bearing flags. **33 selection sites** in total. Of those, **18 select products written by
`_atomic_savez`**, across **8 launchers** and **3 flags**:

| launcher | flag | pattern | stem |
|---|---|---|---|
| `sbatch_uthrow_combine_5d_fast.sh` | `--block-slabs` | `"${BLOCK_DIR_SB}/block5d_*.npz"` | `block5d_` |
| `sbatch_uthrow_combine_5d_fast.sh` | `--combine` | `"${THROW_DIR}/uthrow5d_slab_*.npz"` | `uthrow5d_slab_` |
| `sbatch_uthrow_combine_5d.sh` | `--block-slabs` | `'uq_5d/block_slabs_5d/block5d_*.npz'` | `block5d_` |
| `sbatch_uthrow_combine_5d.sh` | `--combine` | `'uq_5d/uthrow_slabs_5d/uthrow5d_slab_*.npz'` | `uthrow5d_slab_` |
| **`sbatch_j28_adopt_5d.sh`** | **`--block-slabs`** | `'uq_5d/block_slabs_5d_sb/block5d_*.npz'` | `block5d_` |
| **`sbatch_j28_adopt_5d.sh`** | **`--block-slabs`** | `"${RESCALED}/block5d_*.npz"` | `block5d_` |
| **`sbatch_j28_adopt_5d.sh`** | **`--combine`** | `"${UNION}/uthrow5d_slab_*.npz"` | `uthrow5d_slab_` |
| **`sbatch_j28_adopt_5d.sh`** | **`--throw-slabs`** | `"${STAGE_OLD}/uthrow5d_slab_*.npz"` | `uthrow5d_slab_` |
| `sbatch_uthrow_combine_4d.sh` | `--block-slabs`, `--combine` | `uq_4d/uthrow_slabs_4d/…` | `block4d_`, `uthrow4d_slab_` |
| `sbatch_uthrow_combine_4d_corrected_gpu.sh` | `--block-slabs`, `--combine` | `uq_4d/corrected/uthrow_slabs_4d/…` | same 4D stems |
| `sbatch_uthrow_combine_fps.sh` | `--block-slabs`, `--combine` | `uq_fps/uthrow_slabs_fps/…` | `blockfps_`, `uthrowfps_slab_` |
| `sbatch_uthrow_combine_fps_corrected_cpu.sh` | `--block-slabs`, `--combine` | `uq_fps/corrected/uthrow_slabs_fps_neutral/…` | same fps stems |
| `sbatch_uthrow_combine_fps_corrected_gpu.sh` | `--block-slabs`, `--combine` | same as above | same fps stems |

**Two corrections to the list I was given (7 launchers × 2 flags = 14 sites):**

1. **`sbatch_j28_adopt_5d.sh` is absent from it** — four sites, bolded above.
2. **`--throw-slabs` is a third flag, and it belongs to a *second consumer program*.** Measured:
   `--combine` and `--block-slabs` are declared in `unified_throw_cov.py:1250-1251`, while
   `--throw-slabs` (with its own `--block-slabs`) is declared in
   `rescale_flux_universes.py:200-201`. So the products of the repaired producer are selected by
   **two** programs, not one — and `rescale_flux_universes.py` is the program `protect_throw_slabs`'
   own docstring names as rebuilding `C_blocksum` from the block slabs.

The delta's **own code comment already carries the right figure** — *"all 18 launcher patterns across
the three glob-bearing flags"* — so this is a correction to the message, not to the repair.

**Selection behaviour**, confirmed: single-quoted patterns pass through to Python `glob.glob`;
`"${VAR}/…"` forms shell-expand first and then glob. All 18 have **fixed** directory components
(which is why F1's wildcard case was latent). All 18 require a **literal terminal `.npz`**.

**The other 15 sites are `--glob`**, consumed by `combine_cov_nd.py` and friends, selecting
`res_boot_*.npz` / `res_split_*.npz` and `*_uni_full_*.root`. Those products are **not** written by
`_atomic_savez` — `bootstrap_nd.py` and `seedscan_split.py` use a bare
`np.savez_compressed(args.out, …)` with no temp and no rename — so they are correctly outside this
repair's effect. The owner's own classification of that as *strictly worse than the defect just
repaired*, needing atomic publication **added** rather than a temp renamed, is right, and it is
recorded in their test rather than only in prose.

**Promised scope = 2 sites** (`sbatch_uthrow_combine_5d_fast.sh`, both flags). Reviewed. The other
three precursor arms carry no selection flag — they produce — and the observation that "4 arms" was
the wrong unit because three of four are producers is correct.

---

## §3 — The asymmetry claim: CONFIRMED, and stronger than stated

The claim: *scope of review is 2 sites; scope of effect is every site, for free, because the
guarantee is a property of the name.*

Tested mechanically at **every** slab-selection site — for each, a real directory with the real
product, a real post-repair temp from `U.incomplete_name(...)`, and a real pre-repair temp, selected
with real `glob.glob` (not `fnmatch`, which does **not** special-case the leading dot):

```
slab-selection sites                                  18   (8 launchers, 3 flags)
sites where the POST-repair temp is SELECTED           0   of 18
sites where the PRE-repair temp IS selected           18   of 18
patterns not requiring a terminal '.npz'               0
patterns beginning with a dot                          0
consumers passing glob(include_hidden=True)            0
```

**Confirmed.** And the correction *strengthens* it: the effect covers 18 sites across 8 launchers
rather than 14 across 7, and the pre-repair defect was live at **every one of the 18**, not only at
the precursor's two.

**The falsifiers, named, because a universal claim is only as good as its stated failure modes.**
The asymmetry breaks if any of these appears, and each is currently absent or covered:

1. a selection pattern that **begins with a dot** — none;
2. a pattern **without a terminal `.npz`** (e.g. `block5d_*`) — none; this is the one a future author
   is most likely to write;
3. `glob.glob(..., include_hidden=True)` (Python 3.11+) — absent, and it defeats guarantee (1)
   entirely;
4. a **non-glob** selector without an `.npz` filter — `os.walk`/`iterdir`; covered by guarantee (2),
   which is why (2) is load-bearing and not belt-and-braces.

Items 3 and 4 are the ones no current test would catch if introduced, since the idiom-ban arm checks
for `iterdir`/`rglob`/`scandir` calls and not for the `include_hidden` keyword.

---

## §4 — Recorded as out of scope

**`protect_throw_slabs.py`'s own defect is OUT OF SCOPE for this review**, per the relayed
instruction, and I agree with the narrowing on its merits: it is an archival tool, not a precursor
dependency, and folding it in would expand a bounded review into every tool that touches a slab.

I confirmed the finding before setting it aside, by execution rather than reading —
`find_slabs` collects the pre-repair temp `block5d_knobs.npz.abc123.tmp.npz` and rejects the
post-repair `.mnv-incomplete.….partial`, and the tool `np.load`s what it collects and records a
per-file `readable` flag, so a pre-repair temp would have been archived as an unreadable "protected
slab." **It needs its own record and its own owner.**

**One distinction, so both statements stay true:** the *tool's* defect is out of scope, but the
delta's **arm** that uses the tool as a fixture is in scope and is load-bearing — it is what makes
guarantee (2) individually mutation-killable. I reviewed the arm, not the tool.

**Also out of scope and noted:** the probe's R5 accounting. I agree it should be computed by its own
instrument at submission rather than pre-computed. **One factual note: the cluster is reachable from
this session** — `ssh saul.nersc.gov` answered on `login18` and I ran `sacct` against it for §1 — so
the `ssh` 255 is local to that session, not a site outage. Nothing here depends on it.

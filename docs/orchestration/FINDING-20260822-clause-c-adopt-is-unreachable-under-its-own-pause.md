# FINDING 2026-08-22 — clause (c) of the B1 member pause cannot be satisfied through the real launcher path: it is circular as written

**Question posed.** Clause (c) of the B1 steps (4)/(5) pause — quoted verbatim in
`nd-unfolding/sbatch_finalize_5d_bkgaware_gpu.sh:270-300` — requires that "a FRESH NON-BUILDER has
verified the REAL steps (4)/(5) path on a PRESENT-SEED artifact, INCLUDING A NEGATIVE CONTROL," and
excludes "invoking the wrapper directly." The lane that discharged it ran the *extracted* adopt
segment under `srun`. So: **can a real `sbatch` of that launcher reach the adopt calls at
`:347`/`:352` while the pause holds?**

**Answer: no. There is no environment variable and no argument combination that does it.** Clause (c)
as written is circular, on three independent grounds, two of them structural and one of them a fact
about the artifacts that exist today. This is a finding about the *condition's satisfiability*, not
about anyone's code quality: every branch involved is doing what its own comment says it does.

This document changes no code and no `nd-unfolding/` file. It edits nothing under
`docs/OPEN_ITEMS.md` either — see **Scope and limits**.

---

## 1. The control flow, as measured

The launcher takes **no positional arguments** (verified: no `$1`, `$@`, `$*`, `getopts`, or `shift`
on any uncommented line — the only grep hits are prose). Its behaviour is therefore a pure function
of the environment. A covering enumeration of every `${VAR}` reference on uncommented lines gives the
complete externally-settable set:

| variable | effect on reaching `:347` |
|---|---|
| `MNV_EST_SEED_OFFSET` | **the only lever on `:256`** |
| `MNV_LAUNCHER_DIR` | locates `lib_member_resume.sh`; no effect on the branch |
| `RESUME_ADOPT_LEGACY` | `=1` → `exit 5` at `:194`, both regimes |
| `RESUME_FORCE` | `=1` → `exit 5` at `:214` undeclared; declared, it only forces regeneration and still meets the pause |
| `MII_CONTAINER` | renames the member root only (`lib_member_resume.sh:84,88`) |
| `SLURM_JOB_ID`, `BASH_SOURCE` | library resolution only |
| `REPO` | **hardcoded at `:15`, not env-overridable** |

`:256` is literally `if mr_declared; then`, and `mr_declared` (`lib_member_resume.sh:230`) is:

```bash
mr_declared() { [[ -n "${MNV_EST_SEED_OFFSET:-}" ]]; }
```

So exactly two regimes exist, and they partition:

* **Declared** (`MNV_EST_SEED_OFFSET` non-empty, canonical integer — *including `0`*): member
  namespace; the pause block runs; **`exit 0` at `:330`**, above the adopt calls.
* **Undeclared** (unset *or* empty string): archive literal paths; falls through `:331`; adopt runs
  at `:347`/`:352`.

**Measured, not read.** I copied the launcher, `lib_member_resume.sh` and `lib/resume_guard.sh` into
a sandbox, applied **one** patch — line 15, `REPO="/pscratch/…"` → `REPO="${SB_REPO}"`, confirmed by
`diff` to be the sole hunk — stubbed `setup_salloc_env.sh`, and put a `python3` on `PATH` that records
its argv and creates whatever `--out` / `--outdir`+`--out-root` names, so no real adoption occurs.
Four arms, all of which reach `:256`:

| arm | `MNV_EST_SEED_OFFSET` | outcome | adopt invoked? |
|---|---|---|---|
| A | unset | archive paths, falls through | **yes**, both calls |
| B | `0` | `MEMBER PAUSE` fired, rc=0 | no |
| C | `1200` | `MEMBER PAUSE` fired, rc=0 | no |
| D | `""` (empty) | archive paths, falls through | **yes**, both calls |

Arms B and C reached the pause *having produced the member intermediate*, so "adopt not reached" there
is caused by the pause and not by a missing input — my first harness pass got this wrong (the stub
only understood `--out`, so the declared arms died earlier at `mr_run`, which would have made the
comparison unsound) and was corrected before the arms above were run.

Arm D is worth recording: `mr_declared` tests `-n "${…:-}"` while `lib_substitution_fence.sh:33`
tests `+x` (declared-at-all). That asymmetry is real, but it buys nothing — an empty value routes to
the **archive** paths, identically to unset, because `mr_member_dir` (`:73`) and
`seed_offset_policy.declared_offset()` both treat empty as undeclared too. It is not a way in.

**So adopt is reachable in exactly one regime: undeclared, over the archive's own legs.**

---

## 2. First circularity — the reachable regime cannot carry a present seed

"Present-seed" is a property of the two **input legs**, not of the environment. The wrapper reads
`estimator_seed` from `--uthrow` (g2) and `--combined` (g1) and stamps
`upstream_estimator_seed_{g1,g2}_checked = 0 if seed is None else 1`
(`mii_adopt_unified_5d_stamped.py:390-394`). The producers write that key **unconditionally**
(`sweep_bank_5d.py:285`, `unified_throw_cov.py:545`, propagated by `analyze_universes_5d.py:276-277`),
so seed-presence is not env-gated — it is *path*-gated, because which files the launcher passes is.

Undeclared means the archive literals. **Re-measured on the cluster today, 2026-08-22** (login34,
`source setup_salloc_env.sh`, ROOT 6.28, keys read directly):

| leg | size | mtime | keys | `LEG_IDENTITY_KEYS` present | `TParameter<int>` keys |
|---|---|---|---|---|---|
| `nd-unfolding/uq_5d/unified_throw_cov_5d.root` (g2) | 2,677,168,123 | Jul 13 02:15 | 9 | **none** | `n_throws` |
| `…/universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware.root` (g1) | 41,436,632,945 | Jul 14 13:59 | 47 | **none** | *(none)* |

This reproduces the 2026-08-20 figures (9 and 47) exactly. Both legs predate remedy (A) by five
weeks, and neither carries a seed. So the one reachable regime is seed-**absent** by construction.

Could the undeclared route be handed present-seed archive legs? Only by re-producing those files in
place. That is (i) refused by the launcher itself — the undeclared route "may only REUSE `${COMB}`,
never produce it" (`:243`), with `RESUME_ADOPT_LEGACY=1` and `RESUME_FORCE=1` both `exit 5` — and
(ii) an overwrite of frozen provenance on the 41.44 GB intermediate (2.087 TiB to regenerate) that
nobody has authorized. **That is not an env or argument combination; it is a separate destructive act.**

Meanwhile present-seed legs would land in a **member** namespace, which requires declared, which is
`exit 0` at `:330`. The artifact clause (c) demands and the path clause (c) demands are in disjoint
regimes.

---

## 3. Second circularity — the check clause (c) exists to exercise is itself gated on `declared`

This one is stronger, because it does not depend on any file's bytes.

The OI-140 recompute — the thing "verified the real path on a present-seed artifact" is *for* — is
`assert_seeds_match_their_baselines` (`mii_adopt_unified_5d_stamped.py:355`). Its first statement is:

```python
if not off_declared:
    return False
```

and `off_declared` has exactly one source: `seed_offset_policy.declared_offset()`
(`mii_adopt_unified_5d_stamped.py:708`), which reads **`MNV_EST_SEED_OFFSET`** and returns
`(0, 0)` when it is unset or empty. There is no CLI override — the wrapper's only arguments are
`--uthrow`, `--combined`, `--out`, and `passthrough` (`:489-492`).

So `off_declared == 1` ⟺ `MNV_EST_SEED_OFFSET` non-empty ⟺ `mr_declared` true ⟺ **`exit 0` at `:330`
before the wrapper is ever invoked.**

**Measured, with a negative control** (pure functions, executed locally with a minimal `ROOT`
stand-in; nothing ROOT-dependent called):

* Leg baselines re-derived from the module: `g1 = 42`, `g2 = 1000`.
* **Arm 1** — `off_declared=0`, both legs carrying seeds that are *deliberately wrong* for `k=1200`
  (each carries its own baseline): returns `False`, **no refusal, nothing compared.**
* **Arm 2 (negative control)** — identical seeds, `off_declared=1`, `k=1200`: raises
  `SystemExit: [FAIL] g1 leg's estimator_seed is 42 but this process declares offset 1200 against
  baseline 42, i.e. 1242.` The check has power; the fixture can fire.

Arm 1 is the finding: **even if you handed the undeclared route perfect present-seed legs, the
identity check would still compare nothing.** The undeclared route cannot exercise it at any price.
`stamp_pairs` on seed-absent legs confirms what such a run would record —
`[('est_seed_offset_declared', 0), ('est_seed_offset', 0), ('upstream_estimator_seed_g1_checked', 0),
('upstream_estimator_seed_g2_checked', 0)]` — i.e. absence, which the pause text itself already calls
"ABSENCE, not a pass."

---

## 4. Third ground — today, adopt is reachable by *no* configuration at all

Arm A/D reached adopt only because my harness **fabricated** the `.done` marker the undeclared route
requires. On the real tree that marker does not exist:

```
$ ls  …/uq_5d/universe_stage2_5d_bkgaware/
uq_universe_5d_covariance_combined_bkgaware.root                 41436632945  Jul 14 13:59
uq_universe_5d_covariance_combined_bkgaware_uthrow.root            892195314  Jul 14 14:02
uq_universe_5d_covariance_combined_bkgaware_uthrow_cvcentered.root 892241032  Jul 14 14:04
uq_universe_5d_summary.txt                                               487  Aug 20 14:49
$ cat  …/uq_universe_5d_covariance_combined_bkgaware.root.done
cat: … No such file or directory
```

No marker ⇒ the undeclared route takes `:242`'s else-branch and **`exit 5`** at `:253`. And the member
tree holds only bootstrap replicas — 18 files, `res_boot_{1,2,3}.npz` plus markers across
`member_k000000`, `member_k001200`, `member_k002400`; **no member `COMB`, no member sweep leg, no
member uthrow.**

So as of 2026-08-22 a real `sbatch` of this launcher terminates before `:347` in **both** regimes:
`exit 0` at `:330` declared, `exit 5` at `:253` undeclared. There is no present-seed g1 or g2 leg
anywhere on the cluster — archive or member.

---

## 5. What this forces

Clause (c) requires the conjunction of two properties that the code places in mutually exclusive
branches. It is unsatisfiable *as written*, and — this is the part worth naming — it is unsatisfiable
for the same structural reason the previous wording was: the earlier version named lane C, a party
that had ceased to exist, and was rewritten as a **property** to fix that. The rewrite fixed the
addressing and introduced a different impossibility, this time in the *code* rather than in the roster.
A property-shaped condition is checkable by whoever is here only if some reachable execution can
exhibit the property.

The option set is therefore closed, and I state it without recommending one — the choice is Joseph's:

1. **Rule clause (c) discharged on the extracted-segment evidence already filed** (`2b6bf689`),
   accepting explicitly that "REAL path" cannot mean "through the launcher" while the pause holds.
   This is the only option that requires no code change, and it requires saying out loud that the
   exclusion of "invoking the wrapper directly" cannot be honoured.
2. **Amend clause (c)** to name what is actually checkable — e.g. the wrapper invoked on stamped legs
   with `MNV_EST_SEED_OFFSET` declared, which exercises `assert_seeds_match_their_baselines` for real
   (Arm 2 above shows it fires) but is by construction not a launcher run.
3. **Lift the pause first, then verify** — i.e. accept that clause (c) is a post-condition of lifting
   rather than a pre-condition of it. This inverts the dependency the pause was written to create.
4. **Add a dry-run path to the launcher** that reaches `:347`/`:352` without adopting, so a declared
   member can exercise steps (4)/(5) under the pause. This is a code change to a frozen-provenance
   launcher and needs its own authorization; it is the only option that makes clause (c) literally
   satisfiable as worded.

Options 1–3 are rulings. Option 4 is a build. Nothing here is self-clearing, and nothing in this
document lifts anything.

---

## Scope and limits

* **Read-only on `nd-unfolding/`.** No file under it was modified. The sandbox ran *copies*, with the
  single line-15 `REPO` patch recorded above and verified by `diff`.
* **No real adoption occurred.** `python3` was a stub that recorded argv; the two 892 MB products
  were never built. The cluster work was three read-only `ls`/`find`/key-listing commands.
* **Local shell is bash 3.2.57**, Perlmutter is 4.4. The constructs on this path (`[[ -n ]]`, `if`,
  `exit`, `=~`) are version-insensitive, but the arms were not run on 4.4 and I am not claiming they
  were. The `set -eo pipefail` at `:11` was preserved in the copies.
* **`--diff`-free claim about `off_declared`:** I did not re-derive `seed_offset_policy.OFFSET_ENV`
  from anywhere but `seed_offset_policy.py:193`, where it is `"MNV_EST_SEED_OFFSET"`.
* **Out of scope and deliberately not concluded:** where the present-seed k=0 product used by the
  clause (c) discharge run came from. No production present-seed leg exists (§2, §4), so it was not a
  production leg — but I did not locate or audit that lane's scratch products, and I am not
  characterising them. That is a question for whoever reviews `2b6bf689`, not an assertion here.
* **No `docs/OPEN_ITEMS.md` row was edited.** Those rows are digest-bound to
  `source-record-inventory.tsv`, so touching one is a coupled multi-file change outside the brief I
  was given ("file your finding under `docs/orchestration/`"). If this finding should carry an OI row,
  that is a separate, bounded change.

## Reproduction

The harness and probe live outside the repo (job scratch), and both are short enough to rebuild from
this document: the launcher copy plus the line-15 patch, a stub `python3` honouring `--out` and
`--outdir`/`--out-root`, and the four arms of §1; the `off_declared` probe of §3 is four calls to
`assert_seeds_match_their_baselines` / `stamp_pairs` with a stand-in `sys.modules["ROOT"]`. The
cluster measurements are three commands over
`/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/`.

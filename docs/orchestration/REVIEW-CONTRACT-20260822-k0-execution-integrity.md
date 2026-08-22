# REVIEW CONTRACT 2026-08-22 — execution integrity for the k=0 M(ii) member

**Status: this is a CONTRACT, agreed BEFORE implementation, not a review of anything.** Joseph
required the controls be fixed in advance *"so the builder cannot select the evidence afterwards"*
([`PLAN-20260822-oneMember-mii-staged.md`](PLAN-20260822-oneMember-mii-staged.md) Amendment 2,
"Review contract status"). Nothing here authorizes a submission. Nothing here is a PASS.

**Author eligibility.** Written by a fresh reviewer who has authored no code in this repository and
no part of the k=0 plan. Everything below was produced read-only: no Slurm job was submitted, no
scientific artifact was opened, moved or deleted, and the 41.44 GB combined intermediate was not
touched. The only files this lane writes are this document and the three index/manifest artifacts
that a new `LIVE` document is required to move with it.

**Governing rulings.** [`DECISION-20260822-joseph-b1-lift-and-clause-c.md`](DECISION-20260822-joseph-b1-lift-and-clause-c.md)
rulings 12, 13 and 14; the plan's Amendment 1 §D and Amendment 2 §§1–3.

---

## 0. The claim this contract exists to prevent

`mnv_guarded_run.py` fires when an import **resolves** inside a checkout other than `--expect-root`.
It does not fire on a `sys.path.insert()` occurring. So a green production arm may be **vacuous**:
if the adopter inserts the canonical root but imports no repository module through it, the guard
refuses nothing and exits 0, and that zero is indistinguishable from a clean run.

**This contract holds that the vacuity is not a risk on this path. It is the measured fact.** See
M-1. The consequence runs in the opposite direction from the builder's Amendment 1 §D: the adopter's
subprocess boundary is the place where the wrapper can do the *least*, and legs 1–5's entrypoints —
which Amendment 1 §D does not analyse — are where the real OI-136 exposure lives.

---

## 1. Measurements this contract rests on

Read-only, 2026-08-22, from local `main` `064496cd` (`git rev-parse HEAD`; `origin/main` is the same
sha) and from the cluster over `ssh saul.nersc.gov`. Each is stated with its command so it can be
falsified, and each is **perishable** — §7 requires every one of them to be re-run at submission
time rather than quoted from here.

### M-1 — what each k=0 Python entrypoint imports, and whether it imports it AFTER a rooted insert

Method: AST parse of each entrypoint; locate the lowest-numbered `sys.path…insert(...)` call; collect
every `import`/`from … import` at any depth with its line number; intersect the top-level module
names against the set of importable top-level names in `nd-unfolding/` and `2d-unfolding/`
(`.py` stems plus directories carrying `__init__.py`). Run from `nd-unfolding/`.

| entrypoint | carries the root literal | first `sys.path` insert | repository modules imported AFTER that insert |
|---|---|---|---|
| `bootstrap_nd.py` | yes | :11 | `omnifold_nn_core`, `seed_offset_policy`, `xsec_nd` |
| `seedscan_split.py` | yes | :23 | `omnifold_nn_core`, `seed_offset_policy`, `xsec_nd` |
| `unfold_nd_omnifold_unbinned.py` | yes | :52 | `flux_universe`, `seed_offset_policy`, `unfold_2d_omnifold_unbinned`, `xsec_nd` |
| `sweep_bank_5d.py` | yes | :35 | `flux_universe`, `omnifold_nn_core`, `unfold_2d_omnifold_unbinned`, `unfold_nd_omnifold_unbinned`, `xsec_nd` |
| `unified_throw_cov_5d.py` | yes | :27 | `omnifold_nn_core`, `unified_throw_cov`, `xsec_nd` |
| `unified_throw_cov.py` (imported, not an entrypoint) | yes | :45 | `compare_unified_throw`, `flux_universe`, `seed_offset_policy`, `unfold_2d_omnifold_unbinned`, `uq_math` |
| `combine_cov_nd.py` | **no** | none | `replica_manifest` (via the script's own directory) |
| `analyze_universes_5d.py` | **no** | none | `fps_unfold_complete` (via the script's own directory) |
| `mii_adopt_unified_5d_stamped.py` | **no** | :149, derived from `__file__` | `seed_offset_policy` |
| **`adopt_unified_5d.py`** | **yes**, `:35` | **:38** | **NONE — the empty set** |

`adopt_unified_5d.py`'s complete import list is `argparse, gc, os, sys` (`:28-31`), `numpy` (`:33`) —
all **before** the rooted insert at `:35-38` — and `ROOT` (`:60`, `:73`), which is the only import in
the file that the insert can reach. Nothing repository-local is imported at all.

### M-2 — could the insert shadow a non-repository name?

The only way `adopt_unified_5d.py`'s insert can bite is by shadowing: a file in the canonical
checkout's `nd-unfolding/` or `2d-unfolding/` whose top-level name collides with something imported
for the first time after `:38` (i.e. `ROOT` and whatever `ROOT`'s own import pulls in).

Measured **on the canonical checkout itself**, because that is the tree the literal names:

```
ssh saul.nersc.gov 'python3 - <<PY … iterate /pscratch/sd/j/josephrb/MINERvA-OmniFold/{2d,nd}-unfolding … PY'
```

→ **125** importable top-level names (123 on `main`; the two extra are the untracked
`nd-unfolding/plot_nn_vs_gbdt_full.py` and `nd-unfolding/validate_adopted_4d.py`). Intersected
against `sys.stdlib_module_names` on CPython 3.12.2 and against a hand-listed third-party set:
**zero collisions in both directions.**

**State plainly what this instrument cannot say.** The stdlib set is *this Mac's* 3.12.2, not the
`root_6_28` interpreter's; the third-party list was hand-written and is therefore **not a covering
search**. A name intersection is a weaker instrument than the runtime origin inventory §4 requires,
and it is offered as a prediction the builder must confirm, never as the evidence.

### M-3 — which of these files are hash-bound

Method that does not depend on a path/digest conjunction (a receipt splits `path` and `sha256`
across lines, so grepping for both at once cannot work): compute each file's live sha256 and search
for **that digest string** across `docs/`, `nd-unfolding/`, `2d-unfolding/` over `*.json *.sh *.py
*.md`, excluding `.claude/worktrees/`.

| file | digest found in |
|---|---|
| `adopt_unified_5d.py` (`e1260e8d…`) | `state/ben106-stamp-verify-active-56695424.json`, `state/ben106-stamp-verify-complete-56695424.json`, `state/cluster-local-fork-freeze-20260812.json`, `VERDICT-20260821-expiry-c-real-path-present-seed.md` |
| `seed_offset_policy.py` (`dffa622e…`) | `VERDICT-20260821-expiry-c-real-path-present-seed.md` |
| all eight others in M-1 | **none** |

Corroborated by `python3 docs/orchestration/verify_hash_bindings.py` → exit 0, `ALL BINDINGS
INTACT`, `133 OK`. A *stale* pin would already be red there, so "no live digest match and the
verifier is green" is close to covering. It is not perfectly covering: a pin held outside those
directories, in a non-text form, or under a different hash algorithm would be invisible to it.

**A separate instrument of mine returned zero and I am discarding it, not reporting it.** An attempt
to drive `verify_hash_bindings.collect()` directly returned `collected 0 binding keys` — that is
evidence about my harness, not about the repository, and no count in this document comes from it.

### M-4 — the canonical checkout's actual state

`ssh saul.nersc.gov 'cd /pscratch/sd/j/josephrb/MINERvA-OmniFold && git rev-parse HEAD && git status
--porcelain | wc -l'` → `b2d7d4ca24707344cf12f99c0aa51381b81dd445`, **721**. Split by
`awk '{print $1}' | sort | uniq -c`: **717 `??`, 4 ` M`**. The four modified files are
`docs/orchestration/state/sessions.json` and three
`nd-unfolding/active_universe_5d/standard/evidence/p4_*.json` — **no tracked `.py` on the k=0 path is
modified there.** `git merge-base --is-ancestor b2d7d4ca HEAD` exits 0; `rev-list --count` gives
**36 behind, 0 ahead** of `main`.

`sha256sum` on the cluster for `adopt_unified_5d.py`, `mii_adopt_unified_5d_stamped.py`,
`mnv_guarded_run.py`, `seed_offset_policy.py` returns digests **identical** to `main`'s.

**Do not read this as "the dirty checkout is fine to run from."** It says the hazard is *latent
today*, which is exactly what OI-136's own row says about the 2026-08-20 fast-forward, and exactly
the reasoning that preceded run `57266000_0`. 717 untracked files are 717 opportunities for a
shadowing name to appear between this measurement and the submission.

### M-5 — the `.sh` half is unrepaired on all eight launchers

`grep -nE '^\s*(export\s+)?REPO=' <launcher>` on the seven submitted launchers plus
`sbatch_finalize_5d_bkgaware_gpu.sh`: **all eight** assign
`REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"` unconditionally, and all but
`sbatch_unfold_5d_detector_bkgaware_gpu.sh` then `cd "${REPO}/nd-unfolding"`. Five of them also
`source "${REPO}/setup_salloc_env.sh"`. No Python guard reaches this: it is decided before any
interpreter starts.

### M-6 — the guard emits no evidence that it looked

`GuardedPathFinder.checked` is incremented at `mnv_guarded_run.py:189` and **read nowhere in
`main()`** (`grep -n checked nd-unfolding/mnv_guarded_run.py` → `:178`, `:189` and three prose
lines). It is read only from inside a test fixture
(`test_mnv_guarded_run.py::test_the_guard_actually_inspected_something`). **A production guarded run
therefore emits no artifact distinguishing "checked many imports, all clean" from "checked nothing."**
That is the vacuity Amendment 2 §2 names, made concrete: today the wrapper *cannot* produce the
positive evidence Joseph asks for.

### M-7 — the guard does not check that the SCRIPT is in the expected tree

`main()` validates `--expect-root` is a checkout (`:252-257`) and that the script exists
(`:259-262`). It never asks whether the script itself lies under `--expect-root`. For an entrypoint
with repository imports this fails closed anyway, by accident, at the first import. **For
`adopt_unified_5d.py`, which has none, running the canonical checkout's copy with
`--expect-root <clean tree>` would exit 0.** The guard would not notice that the executing file came
from the forbidden tree. This is the single largest hole in the builder's proposed design.

### M-8 — the suite's own count is dated

The plan and `OI-136` say the guard carries **21** tests. `grep -c "def test_"` returns **24**. Cite
the count you measure, not the count the prose carries.

---

## 2. §A — what counts as "the approved clean execution tree"

`--allow` naming `/pscratch/sd/j/josephrb/MINERvA-OmniFold` is **FORBIDDEN** (Amendment 2 §3). This
contract adds: `--allow` naming *any* path is forbidden on the production arm, for every leg. An
`--allow` on a production arm is a declaration that the guard's answer was inconvenient.

**A-1. TWO ROOTS, NOT ONE. This is a defect in the plan as written and it must be fixed before
anything is built.** Amendment 2 §3 says the submission commands must name the clean tree instead of
`/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding`. Taken literally that is unbuildable and
unsafe:

- every launcher does `cd "${REPO}/nd-unfolding"` and then reads inputs (`of_inputs_5d.npz`) and
  writes outputs (`boot_nd_5d/`, `seedscan_split_5d/`, `uq_5d/`, `mii/member_k000000/`) **relative to
  that directory**;
- those inputs are large, gitignored, and **absent from a fresh clone**, so a clean tree cannot serve
  as the working directory at all;
- and ≈47.7 GB of member products landing inside the clean tree would destroy the immutability the
  clean tree exists to provide — `git status --porcelain` would stop being empty on the first leg.

So the contract requires the launchers be parameterised on **two** roots:

- `MNV_CODE_ROOT` — the approved clean execution tree. Every `.py` and `.sh` that executes, and
  every module that is imported, must resolve under it. Immutable for the duration.
- `MNV_DATA_ROOT` — the working directory for inputs and products. `/pscratch/sd/j/josephrb/MINERvA-OmniFold`
  is acceptable **as a data root only**. Nothing is executed or imported from it.

Both must be **mandatory with no default** (`: "${MNV_CODE_ROOT:?}"`), not `${VAR:-<hardcoded>}`. A
default is the hardcode wearing a flag, and a defaulted variable that is silently empty makes the
command answer about a different subject without erroring. The precedent named in `OI-136`'s own
remedy cell is `sbatch_gate6_leg0_tier_calibration_array.sh`'s mandatory `G6_LEG0_CODE_REPO`.

**A-2. Constitution of `MNV_CODE_ROOT`.** Created by `git clone` or `git worktree add` at a **named
commit sha**, recorded in the run receipt. All of the following must be recorded before the first
`sbatch` and re-verified after the last:

| # | requirement | instrument |
|---|---|---|
| a | `git rev-parse HEAD` equals the declared sha | quote the sha, never "main" |
| b | `git status --porcelain` emits **zero lines** | count lines; do not read `$?` after a pipe |
| c | it is a checkout by the guard's own definition — `VALIDATION_LEDGER.md` **and** `nd-unfolding/` both present | otherwise the guard exits **2**, and 2 is "we could not look", never "clean" |
| d | it contains **no nested MINERvA-OmniFold checkout** anywhere beneath it — in particular no `.claude/worktrees/` content | `checkout_root_of` returns the *innermost* match, so a nested checkout inside the code root resolves to itself and is refused; and the OI-136 ratchet has already been made to read 369-instead-of-58 by exactly this |
| e | it is **not** nested inside another checkout | same reason, opposite direction |
| f | a full source manifest: `sha256` of every tracked `*.py` and `*.sh`, sorted, plus one digest over that list | re-verified after every leg; any difference aborts |
| g | write protection applied (`chmod -R a-w` over the source, or a read-only bind) | (f) detects a change; (g) prevents it |

**A-3. Binding what EXECUTES.** For every `.py` and `.sh` on the path, plus `mnv_guarded_run.py`
itself, the launcher must call `verify_executing_copy_is_committed.py --repo "${MNV_CODE_ROOT}"` with
one `--pair` per file, in the shape the two Gate-5 launchers already use. This answers "are the files
at these paths the committed ones". It is **not** redundant with the guard and it is **not**
sufficient: run 4 printed `5 of 5 CURRENT` honestly while the modules loaded came from elsewhere.

**A-4. Binding what is IMPORTED.** §4's origin inventory, which is the other half and the half that
run 4 was missing.

**A-5. `BASH_SOURCE` is the spool path under `sbatch`.** `MNV_LAUNCHER_DIR` must be exported to
`${MNV_CODE_ROOT}/nd-unfolding` in the submitting shell. `$0`, `${BASH_SOURCE[0]}` and
`SLURM_SUBMIT_DIR` are all unusable for this. Under ruling 14 this is one of the three things the
rehearsal exists to test, so it must be **reported whether or not it fails**.

---

## 3. §B — wrapper or scoped source repair, decided per entrypoint

Joseph's criterion (Amendment 2 §3): a scoped source repair is authorized *"for entrypoints whose
hardcoded insert would actually resolve repository imports from the canonical checkout"*. Applying
that criterion to M-1 gives a partition, and it is not the partition Amendment 1 §D assumes.

### B-1. SOURCE REPAIR REQUIRED — five entrypoints plus one imported module

`bootstrap_nd.py`, `seedscan_split.py`, `unfold_nd_omnifold_unbinned.py`, `sweep_bank_5d.py`,
`unified_throw_cov_5d.py`, and `unified_throw_cov.py` (imported by the last of these, and itself
rooted-and-importing).

These meet Joseph's criterion exactly: each has an absolute rooted `insert(0, …)` **and** imports
repository modules after it. **A wrapper cannot help them and would block the run.** With
`--expect-root ${MNV_CODE_ROOT}`, `bootstrap_nd.py`'s `import xsec_nd` resolves under
`/pscratch/sd/j/josephrb/MINERvA-OmniFold` and the guard **correctly exits 3**. There is no
configuration of the wrapper that makes them run cleanly, because `PYTHONPATH` cannot outrank
position 0 — and the one configuration that would make them green, `--allow`, is forbidden.

Repair form: derive the root from `pathlib.Path(__file__).resolve().parents[N]`, with **no absolute
fallback**, matching the pilot repair at `nd-unfolding/uq_fps/corrected/test_fps_corrected_uq.py` and
the idiom at `tests/test_p4_repair.py:14`. Per M-3, none of these six carries a live digest binding,
so the repair costs no receipt re-issue. The coupled artifacts it *does* move are in §6.

### B-2. NO SOURCE REPAIR — `adopt_unified_5d.py`

**This contract declines the source repair on the pinned adopter, and contradicts the framing in
Amendment 1 §D that treats it as the site of the problem.** Three reasons, in order of weight:

1. **It does not meet Joseph's criterion.** M-1: it imports no repository module at all, before or
   after the insert. Its insert cannot "actually resolve repository imports from the canonical
   checkout" because there is no repository import to resolve. The criterion is not satisfied, so the
   authorization does not extend to it.
2. **It is the most expensive file on the path to touch.** M-3: it is the only entrypoint with a live
   digest binding, in four places, including the BEN-106 receipt that
   `assert_pinned_writer_is_intact()` reads **every run** and the `cluster-local-fork-freeze` record.
3. **It is a declared positive control of the OI-136 probe** (`probe-oi136-sys-path-hijack-20260820.py:52`).
   Repairing it makes the probe print `CANNOT CHECK :: positive control(s) absent from the fail-open
   set` and exit 2, taking the ratchet test with it.

**What replaces the repair is a disclosure, not a green tick.** The wrapper on the child is to be
applied — for the reason in B-3 — and the run receipt must state, in these terms: *the OI-136 guard
on `adopt_unified_5d.py` refused nothing because that module imports no repository code; its exit 0
is a structural fact about the file, not a measurement of the tree.*

### B-3. WRAPPER SUFFICES, AND IS NON-VACUOUS — `mii_adopt_unified_5d_stamped.py`,
`combine_cov_nd.py`, `analyze_universes_5d.py`

Each imports at least one repository module (`seed_offset_policy`, `replica_manifest`,
`fps_unfold_complete`) resolved from the script's own directory. Guarding them is meaningful: the
guard has something to inspect and §4's inventory will be non-empty.

### B-4. REQUIRED REPAIR TO `mnv_guarded_run.py` ITSELF — the script-containment check

Per M-7 the guard never asks whether the *script it is running* lies under `--expect-root`. Add:
after the `--expect-root` and `script.is_file()` checks, refuse with exit **3** when
`checkout_root_of(str(script.resolve()))` is a checkout other than `--expect-root`. Without it, the
guarded adopter run from the canonical checkout exits 0 and Joseph's correction 3 has no executable
enforcement anywhere.

`mnv_guarded_run.py` carries no live digest (M-3) and is unpinned, so this is a free change — but it
**is** parity-checked as a `--pair` by the two Gate-5 launchers, so the file and its deployed copy
must move together, and `test_oi136_failopen_inventory_ratchet.py:145,157` asserts both launchers
still name it.

**One trap on this edit:** the probe counts `mnv_guarded_run.py` as a *candidate* only because its
docstring carries the root literal. Do not add a new occurrence of that literal, and do not add a
`sys.path.insert` under a rooted constant, or the guard joins the population it measures.

### B-5. THE `.sh` HALF IS IN SCOPE AND IS NOT COVERED BY ANY PYTHON GUARD

Per M-5 all eight launchers hardcode `REPO` and most `cd` into it. Correction 3 is not satisfied by
any amount of Python work. Each launcher must take `MNV_CODE_ROOT`/`MNV_DATA_ROOT` per A-1, source
`setup_salloc_env.sh` from the code root, and invoke each entrypoint by absolute path under the code
root.

---

## 4. §C — the POSITIVE arm: what establishes that no repository code came from outside the clean tree

**An exit code of 0 is not admissible as any part of this.** Neither is a refusal count of zero.

**P-1. A resolved-origin inventory, emitted by the guard, per process.** `mnv_guarded_run.py` must
write a machine-readable record (append-mode JSONL under a run-scoped directory, path passed by
flag or env) containing, for the whole process:

- the interpreter (`sys.executable`, `sys.version`), `--expect-root`, the `--allow` list (which must
  be empty), the script path and **its** resolved checkout root;
- `checked` — the total number of absolute-origin specs the guard resolved (M-6: currently
  unreported);
- **every** module whose resolved origin lies inside **any** checkout — including `--expect-root` —
  as `{fullname, origin, checkout_root, sha256}`. Not only the refused ones. The allowed ones are
  the positive evidence;
- the final `sys.path`, verbatim.

**P-2. The verdict is read off the inventory, not off the exit code.** For each guarded process:

- every entry's `checkout_root` equals `MNV_CODE_ROOT`; and
- every entry's `sha256` matches that path's entry in the A-2(f) source manifest; and
- `checked > 0`.

**P-3. `repo_origin_count == 0` is a REPORTABLE STATE, never a pass.** Where the set of
repository-origin modules is empty — which M-1 predicts for `adopt_unified_5d.py` and for that file
alone — the inventory must say so explicitly and the receipt must carry the B-2 disclosure sentence.
An absent key cannot distinguish "no repository import occurred" from "the inventory did not run",
which is the same reasoning `adopt_unified_5d.py:200-206` already uses for its `*_checked` flags.
Write the flag unconditionally.

**P-4. An expected-import ratchet, per entrypoint.** For each guarded entrypoint, record the sorted
set of repository-origin module names from the first clean run and pin it as an **identity, not a
floor** — the discipline `test_oi136_failopen_inventory_ratchet.py` already applies to the fail-open
set, and for the stated reason: a floor catches collapse but permits erosion. A run whose set differs
in either direction aborts and is reported.

**P-5. Blind spots that must be stated in the receipt rather than closed.** The inventory does not
see:

- **namespace packages** — `spec.origin` is `None` for them, and `find_spec` returns early at
  `mnv_guarded_run.py:185` before `checkout_root_of` is called. `nd-unfolding/` and `2d-unfolding/`
  contain directories without `__init__.py` whose names are ordinary words (`tests`, `products`,
  `mii`, `pet`, `uq`, `seedscan`), and a namespace portion resolving from the wrong checkout is
  **not refused**. A regular module or package in any later `sys.path` entry outranks a namespace
  portion, so this is a narrow hole, not a wide one — but it is a hole and it is not measured;
- **modules already in `sys.modules`** before `install()` runs (the wrapper's own `argparse`, `os`,
  `pathlib`, `runpy`, `sys`);
- **anything in a further subprocess.** `mii_adopt_unified_5d_stamped.py` → `adopt_unified_5d.py` is
  covered only because the child is *separately* wrapped; any other `subprocess` on the path is not.
  Enumerate them (`grep -n "subprocess\.\(run\|call\|Popen\)\|os\.system\|os\.exec" ` over the
  entrypoint set) and either wrap each child or record it as uncovered;
- **the `.sh` route** entirely (B-5).

**P-6. Completeness of the entrypoint set is itself a claim that must be falsifiable.** State the
search that produced it. This contract's set came from
`grep -nE 'python[0-9]*\s|\.py' <each of the eight launchers>` filtered of comments, giving nine
distinct Python files. The builder must re-run that search on `MNV_CODE_ROOT` at the pinned sha,
publish the command and its full output, and reconcile any difference. **A null result from that grep
is evidence about the grep.**

---

## 5. §D — the NEGATIVE controls, and the ordering evidence

Three controls. **N-1 is mandatory and takes no fixture.** N-2 is mandatory and is the only one that
speaks to the subprocess boundary. N-3 is mandatory once per repaired file.

### N-1 — a genuine repository-local import resolving from the wrong checkout, in real production code

**Selected, not introduced.** Run the **real, unmodified** `mii_adopt_unified_5d_stamped.py` from
`/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding` under
`mnv_guarded_run.py --expect-root ${MNV_CODE_ROOT}`, with `--uthrow/--combined/--out` all pointed at
throwaway paths in a scratch directory (**never** the defaults — the defaults name real archive
products).

Why this is the right control and not a contrivance:

- `seed_offset_policy` is a real repository module, imported by real production code at
  `mii_adopt_unified_5d_stamped.py:250` (via `leg_groups()`), reached from `main()` at `:706`;
- run from the canonical checkout it resolves under `/pscratch/sd/j/josephrb/MINERvA-OmniFold`, which
  is a checkout and is not `--expect-root` → **exit 3**;
- **the configuration under test is precisely the one Joseph's correction 3 forbids**, so the control
  demonstrates that the forbidden configuration is refused rather than merely deprecated;
- it requires no fixture, no copy, no edit, and no ROOT.

**This is the exit-3 arm. Its ordering evidence is in §5.4.**

### N-2 — the child boundary is genuinely armed

N-1 refuses in the parent, which proves nothing about the child. Because `adopt_unified_5d.py` has no
repository import (M-1), the only way to demonstrate that the *child* wrapper would fire is a
declared fixture:

- build a **disposable third checkout** (both markers, on scratch, outside `MNV_CODE_ROOT` and
  outside the canonical checkout) containing `nd-unfolding/<victim>.py`;
- take a **copy** of `adopt_unified_5d.py`, record the copy's sha256 and the one-hunk `diff` against
  the pinned original, and add exactly one line — `import <victim>` — immediately after the rooted
  insert and before `import ROOT`. Record that the copy is a fixture and is never executed on the
  production arm;
- run it through the **same argv template** `build_child_argv` will emit
  (`[python, mnv_guarded_run.py, --expect-root, <clean>, --, <copy>, --uthrow …]`), differing only in
  the writer path;
- `--allow` naming the fixture checkout is permitted **in N-2 only**, and only to build the positive
  half of §5.3. It is forbidden on every production arm and on the canonical checkout always.

### N-3 — one per source-repaired file (B-1)

For each of the six: with the **pre-repair** bytes, from a scratch checkout carrying its own copy of
the victim module, the entrypoint imports the canonical checkout's copy — and still does with
`PYTHONPATH` pointed at the scratch tree, because position 0 cannot be outranked. With the
**post-repair** bytes, the same fixture resolves to its own tree. This is the shape the OI-136 pilot
repair already used and it is the only thing that shows the repair repaired something. A filter needs
a test in the direction it acts **and** a test that it is silent in the other direction.

### 5.4 Ordering evidence — an exit code alone is refused

For every exit-3 arm, all four:

**O-1. A monotone progress marker, measured across two arms of the same binary.** Name a stdout
string that is emitted strictly after the guarded import and strictly before any output file is
opened. For N-1 that string is `[remedyA] running the PINNED writer as a subprocess:`
(`mii_adopt_unified_5d_stamped.py:711`), which is after `leg_groups()` at `:706` and before
`subprocess.call` at `:712`. The evidence is: the refused arm's stdout **does not contain** it, and a
paired arm of the same file with `--expect-root` set to the tree it was launched from **does**. One
binary, one marker, two outcomes — that is an ordering measurement. An absence on its own is not.

**O-2. A filesystem witness over a directory that starts empty.** Put `--out` (and any scratch
target) inside a directory created empty for the control. After the refused arm: the directory
listing is byte-for-byte the empty set, and the `--out` path fails `test -e`. Record the listing and
the `stat` of the directory before and after. `[adopt5d]` must appear nowhere in stdout — the writer
emits its first `[adopt5d]` line only after all three input files have been read.

**O-3. Refusal-before-work must be shown in the process's own log order.** The `[oi136] IMPORT TREE
VIOLATION` banner and the last line of stdout must be captured to the **same** stream with
timestamps, or to two files whose interleaving is reconstructable. Do not compare a stdout file to a
stderr file and call it ordering.

**O-4. Never read `$?` after a pipe.** Capture the exit status of the guarded process itself,
unpiped, into a variable before any `| tee`, `| grep` or `| wc`. Several counts in this campaign have
been reported from a command that failed onto a redirected stderr.

### 5.5 The fixture rule — YES, IT APPLIES, AND IT IS THE FIRST ASSERTION

`test_mnv_guarded_run.py` opens with `TheFixtureReallyHijacks`, whose docstring is *"The control. If
this passes cleanly the guard has nothing to prove."* **That rule is inherited in full here.**

For N-1: run the same command **without** the wrapper — `python3 mii_adopt_unified_5d_stamped.py …`
from the canonical checkout — and show it loads `seed_offset_policy` from
`/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding` (print `seed_offset_policy.__file__`, or read
it from an unguarded inventory run) and proceeds **past** the O-1 marker. If the unguarded arm does
not reach the marker, the control is measuring something else and N-1 does not count.

For N-2: unguarded, the copy must load the **fixture** checkout's `<victim>` and exit 0. Assert the
loaded module's `__file__`, not merely that the process succeeded.

For N-3: the pre-repair arm must load the canonical checkout's copy, asserted by `__file__`.

**A control whose fixture does not hijack passes vacuously, and this whole contract exists because
the production arm may pass vacuously too.**

---

## 6. §E — coupled artifacts that must move in the same commit as the B-1 repairs

Not optional, and each is a gate that will go red if it is skipped.

| artifact | why it moves | rule |
|---|---|---|
| `nd-unfolding/tests/test_oi136_failopen_inventory_ratchet.py` — `FAILOPEN_COUNT = 58`, `FAILOPEN_SHA256 = 21828143…` | six repairs remove six files from the fail-open set | take both new values **from the test's own printed output**, never by hand. **58 is not a target**; record which six paths left and why each was authorized |
| `docs/orchestration/state/probe-oi136-sys-path-hijack-20260820.py:52` — `POSITIVE_CONTROLS` | `unfold_nd_omnifold_unbinned.py` is a declared positive control **and** is in the B-1 repair set; after the repair the probe exits **2** (`CANNOT CHECK :: positive control(s) absent`) and the ratchet fails with it | replace it with a file **chosen from the probe's own fail-open output**, not guessed. `adopt_unified_5d.py` survives as the other control precisely because B-2 declines to repair it |
| `nd-unfolding/tests/test_oi136_failopen_inventory_ratchet.py:157` — the `--pair "${GUARD}=…"` assertion | B-4 edits the guard | both Gate-5 launchers must still name it |
| `nd-unfolding/tests/test_mnv_guarded_run.py` | B-4 adds a refusal mode and P-1 adds an output | new arms: script-outside-expect-root refused **3**; script-inside not refused; inventory written and non-empty for a repo import; inventory written and explicitly empty-with-flag for an entrypoint with none |
| `docs/orchestration/verify_hash_bindings.py` result | any digest that moves | must still print `ALL BINDINGS INTACT`, exit 0, re-run **after** the edits — a binding check is a postcondition |
| `docs/orchestration/RUNBOOK-20260822-b1-lift-preflight.md` and `PLAN-…-oneMember-mii-staged.md` §C | Amendment 1 §C's paths are superseded by A-1 | rewrite with `MNV_CODE_ROOT`/`MNV_DATA_ROOT`; do not leave the canonical path as the working directory |

**Scope fence.** Correction 4 limits this to *this path's launchers and entrypoints and their
necessary hash bindings*. The repo-wide 59-file OI-136 migration is **not** authorized, no
scientific-model change is authorized, and the six B-1 repairs are six individually named sites, not
a sweep. Anything outside the M-1 table and the eight launchers of M-5 is out of scope.

---

## 7. §F — PASS / FAIL

A **PASS** requires every one of the following, each with the command and its output filed. Any
single miss is a **FAIL**; there is no partial credit and no waiver by caveat.

> **READ §7.0 FIRST.** As of 2026-08-22 these eighteen criteria are graded at **two** gates, not
> one. The criteria themselves are unchanged and keep their numbers; §7.0 says which gate each
> belongs to and gives the one-question test that reproduces the partition.

### 7.0 AMENDMENT, 2026-08-22 — §F IS TWO GATES, NOT ONE

**Authority.** Joseph, 2026-08-22, verbatim:

> "The contract is to distinguish pre-submission readiness from post-rehearsal completion; no
> submission occurs until the former passes, and no rehearsal product or further member is
> authorized until the latter passes."

**What this amendment changes, stated precisely.** §7.0 as first written changed **nothing** about
what any criterion requires; it only said when each is settled. **That is no longer the whole
truth: Joseph's ruling 20 of 2026-08-22 RESTATES F-9 and, consequentially, F-12** (§7.0.11,
§7.0.12). Every criterion keeps its number and its original wording — F-9 and F-12 carry an added
superseded-by pointer above the preserved original text, and nothing else in the eighteen is
touched. Measured: with the added pointer blocks removed, the criteria text is byte-identical to
`main` at `115c73bb`. So every existing citation of them — including
[`VERIFICATION-20260822-k0-execution-integrity.md`](VERIFICATION-20260822-k0-execution-integrity.md)
and Joseph's rulings — still resolves. Apart from that one restatement, this amendment says only
**when** each criterion is settled and **which of two verdicts** it belongs to.

**Where the split came from.** It was not asserted. The first review of
`build-k0-execution-integrity` graded all eighteen and returned four NOT-EVALUABLE — F-1, F-2, F-3
and F-17 — and the reason recorded for every one of them was the same: *the criterion requires a
production run that does not exist*. That common reason is the boundary, discovered by measurement.
What follows generalises it and makes it re-derivable.

#### 7.0.1 The classification test — one question, and anyone can re-run it

> **Does settling this criterion require an artifact or an observation that ONLY A PRODUCTION RUN of
> the k=0 path can produce?**
>
> **No → PRE-SUBMISSION.  Yes → POST-REHEARSAL.**

"A production run" means the seven submitted jobs of logical legs 1–5. Nothing else counts as one.

#### 7.0.2 "Needs the cluster" is NOT "needs a run" — and F-9 is the worked example

The test asks about a *production run*, not about *locality*. A read-only `ssh`, a `sha256sum` taken
on `pscratch`, a `git status --porcelain` on the canonical checkout, and a **negative control run by
hand with throwaway paths** are all **PRE-SUBMISSION**: they are observations a bench can make, and
the bench merely happens to be a login node.

**F-9 (N-1) is the case that will be misfiled if this is not said.** N-1 runs the real
`mii_adopt_unified_5d_stamped.py` from the canonical checkout under the guard with `--uthrow`,
`--combined` and `--out` pointed at throwaway scratch paths. It touches the cluster. It is **not a
production run**: no `sbatch`, no scientific workload, no archive product, no member output. It
needs no fixture, no copy, no edit and no ROOT — §5 says so. **F-9 is PRE-SUBMISSION and it is
performable today.** A lane that files it under post-rehearsal has deferred the one negative control
that speaks to the configuration correction 3 forbids.

> **CORRECTION, 2026-08-22 — this worked example was half wrong, and the half that was wrong is
> instructive.** The *classification* above survives: F-9 is pre-submission, and "needs the cluster"
> still is not "needs a run". What was wrong is the implicit claim that F-9 was merely **unperformed**.
> When the round-2 builder actually performed it, F-9 turned out to be **unsatisfiable as originally
> written** — B-4 containment refuses the canonical-checkout wrapper before the import guard is ever
> installed. See §7.0.11. I used F-9 as the clean example of a control that could be run today, and
> it was the one control in §F that could not be run *as specified* at all. **A control that has not
> been attempted cannot be distinguished from one that is impossible**, which is exactly why a
> pre-submission NOT-EVALUABLE is graded as a FAIL (§7.0.8) rather than parked.

#### 7.0.3 A criterion with both halves SPLITS; it is never filed whole under the later gate

Most of §F's criteria carry an obligation to *read an instrument* and, implicitly, an obligation to
*have armed that instrument*. Reading is post-rehearsal. **Arming is always pre-submission**, because
an unarmed instrument is a bench-visible fact. Such a criterion is marked **SPLIT** and is written as
`F-n(a)` — the pre-submission half — and `F-n(b)` — the post-rehearsal half. Both must pass, each at
its own gate.

Where an arming half is not literally spelled out in the criterion's original wording, it is marked
**derived** in the table. It is derived by entailment, not invented: an obligation to read an
inventory entails an obligation to emit one, and F-4's own text — *"a missing inventory is a FAIL,
not a gap"* — already says the contract treats it that way.

#### 7.0.4 F-2 IS NOT DEFERRED. Its arming half is pre-submission and it is SATISFIABLE

Recorded explicitly because this is the criterion most likely to be mishandled, and because the
first review found it **unsatisfiable as specified** — F-2 names two instruments, P-2's inventories
and A-3's `--pair` set, and at `ae42ae8d` *neither existed on the path* (0 of 8 launchers invoked
`mnv_guarded_run.py`; 0 of 8 called `verify_executing_copy_is_committed.py --pair`).

Joseph has since authorized both the guard invocations and the executing-file parity calls. **That
authorization must not be read as permission to postpone F-2.** It converts F-2's arming half from
*unsatisfiable* to *satisfiable and due now*:

**F-2(a), PRE-SUBMISSION, and it is a counting test with no judgement in it.** Across the eight
launchers of M-5, both counts must be **zero**:
- the number of production `python3` invocations **not** routed through `mnv_guarded_run.py` with
  `--expect-root "${MNV_CODE_ROOT}"` and a **mandatory** (not defaulted, not optional) inventory
  destination; and
- the number of `.py` and `.sh` files that will execute on the path, plus `mnv_guarded_run.py`
  itself, **not** covered by an A-3 `--pair`.

**F-2(b), POST-REHEARSAL.** P-2 holds across every emitted inventory and every `--pair` reported
CURRENT.

**The honest residual, stated rather than smoothed over.** F-2(a) cannot be promoted to the whole of
F-2. No bench check establishes that no production process imported a file from the canonical
checkout — only the run's own inventories can, and claiming otherwise would be exactly the vacuous
green arm §0 of this contract exists to forbid. The correct disposition is therefore: **the defect is
closed at Gate 1, the measurement is taken at Gate 2, and neither substitutes for the other.**

#### 7.0.5 The partition

Read the class column, then settle the half named in the column for the gate you are grading.

| # | class | PRE-SUBMISSION half — what settles it on the bench | POST-REHEARSAL half — what settles it |
|---|---|---|---|
| F-1 | SPLIT | code root constituted at a **named sha**; A-2(a)–(g) all measured and filed, including the A-2(f) source-manifest digest — and **(d), (e), (g) as executable FAIL-CLOSED checks, not documentation** (ruling 22, §7.0.14); both preflight tools present in the manifest (§7.0.13) | the same measurements repeated after the last leg; porcelain zero and the manifest digest identical at both ends |
| F-2 | SPLIT — see **7.0.4** | both counts zero: unguarded production invocations **other than the enumerated 16-call preflight set**, and executing files not covered by a `--pair` *(derived)*; **plus the ordering criterion — both preflight tools run BEFORE any science invocation in every launcher, settled by RUNNING it under stubs** (ruling 21, §7.0.13) | P-2 holds across every inventory; every `--pair` CURRENT |
| F-3 | SPLIT | grep the eight launchers and every guard invocation → zero `--allow`; publish the command | grep the job stdout → zero `--allow`; publish the command |
| F-4 | SPLIT | the **denominator** is fixed on the bench: guarded production invocations == production Python invocations **less the enumerated preflight set**, and **> 0** — the accepted figure is **14 launcher-level science invocations plus the pinned-writer child**, re-derived in §7.0.13 *(derived — see 7.0.8)* | count of inventories == count of guarded processes |
| F-5 | SPLIT | the source-manifest generator and the inventory-vs-manifest comparator exist, and each carries a test that **fires on a mismatch** and is **silent on a match** *(derived)* | P-2 holds for every real inventory: origins under the code root, sha256 matching the manifest, `checked > 0` |
| F-6 | SPLIT | `build_child_argv` emits the guard and an inventory for the pinned-writer child; a test asserts an explicitly flagged `repo_origin_count: 0` record for that argv shape *(derived)* | the child's record is present in the run's inventory and the run receipt carries the B-2 disclosure sentence in the contract's own terms |
| F-7 | SPLIT — **confirmed by ruling 22**, §7.0.15 | the P-4 mechanism exists: a per-entrypoint expected-set pin, a comparator aborting on a difference in **either** direction, tests for added / removed / exact-match, and an **absent or undeclared pin failing closed**; the §7.0.13 exclusion pinned with it *(derived — see 7.0.9)* | the sets are recorded from the rehearsal and pinned — see §7.0.9, the pin's first TEST falls outside this gate |
| F-8 | SPLIT | P-6's enumeration re-run on `MNV_CODE_ROOT` at the pinned sha, published with its command and its **full** output and reconciled; P-5's blind-spot inventory produced, including the subprocess enumeration with each child either wrapped or recorded as uncovered | the receipt states the blind spots in the receipt's own words |
| F-9 | **PRE-SUBMISSION** | **RESTATED — grade §7.0.11's six-row table, not the original bullet.** N-1 performed: exit 3 *through B-4*, `outcome = refused:script-outside-expect-root`, never an empty/green verdict, both roots and the script named, `checked == 0` **and** `guard_installed == false`, O-1…O-4 with no child marker or output, and `seed_offset_policy` **not** named on the refused arm. Still needs the cluster, still not a run (§7.0.2) | — |
| F-10 | **PRE-SUBMISSION** | N-2 (as replaced by ruling 19) exits 3 through the child wrapper on the `build_child_argv` template, O-1…O-4 | — |
| F-11 | **PRE-SUBMISSION** | N-3 holds for each of the six B-1 files, both directions | — |
| F-12 | **PRE-SUBMISSION** | N-2 and N-3 unchanged — `__file__`. **N-1 RESTATED (§7.0.12):** `script_checkout_root` is the canonical root and is not `expect_root`; the O-1 paired arm reaches the marker, proving the arm could have succeeded; the U/U' arm retained and **required to name `seed_offset_policy`** as counterfactual origin evidence, never as mechanism | — |
| F-13 | **PRE-SUBMISSION** | B-4's script-containment refusal implemented and covered in both directions | — |
| F-14 | **PRE-SUBMISSION** | every row of §6 discharged in the same commit as the repair that moves it — **and see 7.0.7** | — |
| F-15 | **PRE-SUBMISSION** | the two named suites green under `python3 -m unittest`, counts quoted **as measured at the graded sha**, explicit `TMPDIR` | — |
| F-16 | **PRE-SUBMISSION** | `verify_hash_bindings.py` exits 0 with `ALL BINDINGS INTACT` after all edits | — |
| F-17 | SPLIT | M-1…M-6 re-measured on `MNV_CODE_ROOT` at the pinned sha **and** on the canonical checkout, at submission time; differences reported as findings | re-measured **again after the path runs**; M-2's inventory claim over the untracked set is the perishable one and is re-tested here |
| F-18 | SPLIT | a fresh non-builder records the **PRE-SUBMISSION** verdict clause by clause | a fresh non-builder records the **POST-REHEARSAL** verdict clause by clause |

**Count: 8 criteria pure PRE-SUBMISSION, 10 SPLIT, 0 pure POST-REHEARSAL.** That last number is a
finding, not a tidy result — see 7.0.8.

#### 7.0.6 The two gates, and what each one unlocks

**GATE 1 — PRE-SUBMISSION READINESS.** Passes when every pre-submission half in the table above
passes, each with its command and output filed. **A PASS unlocks exactly one thing: submission of
the seven jobs of logical legs 1–5 for k=0.** It unlocks nothing else. Leg 6 stays separately gated
by Amendment 1 §C, no member k≠0 is authorized, and §G is unchanged.

**GATE 2 — POST-REHEARSAL COMPLETION.** Passes when every post-rehearsal half passes, **plus** the
re-measurements the perishable pre-submission halves require at the far end (F-1(b), F-17(b)).
**Until Gate 2 passes, the rehearsal's products stay where they land: not adopted, not consumed by
anything outside the seven rehearsal jobs, not quoted, and no further member is authorized.**
Consumption *within* the rehearsal is the rehearsal — leg 4 depending on leg 3 is the dependency
graph, not an adoption — and is not what this restricts.

§F's no-partial-credit rule applies **within each gate**: any single miss at a gate is a FAIL of
that gate.

#### 7.0.7 Two additions, marked so a reader may strike them

These go beyond partitioning and are flagged rather than folded in silently. **Striking either
leaves the split intact.**

1. **F-14 pre-submission also requires the repository's coupled generated artifacts to be
   consistent at the graded sha** — concretely, `generate_manifest.py --check` exiting 0, measured
   in a clean worktree. Grounds: at `ae42ae8d` it exited **1** while the commit message asserted 0,
   and `MANIFEST.tsv` is a generated file coupled to the very test files §6 moves. §6's six rows do
   not name it, which is why this is an addition and not a reading.
2. **F-15's counts are bound to the graded sha and must be re-measured, never carried forward.**
   The suite has already moved 21 → 24 → 41. Grounds: M-8.

#### 7.0.8 Finding — no criterion is purely post-rehearsal, and that is why round 1 could stall

Applying 7.0.1 honestly to all eighteen yields **zero** criteria that are settled only by a run.
Every post-rehearsal obligation turns out to sit on top of a bench-visible arming obligation. That is
the structural reason the first round produced four NOT-EVALUABLE verdicts and six FAILs that all
had the same shape: **the instruments were absent, and their absence was able to present itself as
"we cannot evaluate that yet."**

The operational consequence, and it is the point of the whole split:

> **A NOT-EVALUABLE in the PRE-SUBMISSION column is a FAIL of Gate 1.** There is nothing a
> pre-submission half can legitimately be waiting on. If it cannot be evaluated, the instrument is
> missing, and a missing instrument is the defect — not a reason to defer.

**Anti-vacuity, stated because F-4 invites the mistake.** At `ae42ae8d` the number of guarded
production processes was zero, so F-4's "count of inventories == count of guarded processes" read
`0 == 0`. **Do not grade that as a pass.** F-4(a) exists to fix the denominator on the bench first:
the count of guarded production invocations must equal the count of production Python invocations
and must be greater than zero. The same reasoning is why P-3 writes its flag unconditionally and why
the ratchet asserts non-vacuity independently of the probe's exit code.

**CARVE-OUT, added 2026-08-22 with ruling 20 — F-9 inverts this rule and is the only criterion that
does.** On F-9's refused arm the guard is *intentionally never installed*, so `checked == 0` is the
**required** value and a non-zero `checked` is the failure. Do not apply the paragraph above to F-9.
The pair to read there is `guard_installed == false` **and** `checked == 0` **and**
`outcome == refused:script-outside-expect-root`; see the state table in §7.0.11. Everywhere else in
§F the anti-vacuity rule stands unchanged.

#### 7.0.9 Finding — F-7's post-rehearsal half cannot be TESTED by the rehearsal

P-4 pins the per-entrypoint import set as an **identity** taken from the first clean run. The k=0
rehearsal is that first clean run, so it can only **establish** the pin; the first run that the pin
can **fail** is a later one. Since §G and Gate 1 authorize no further member, **F-7's ratchet is
never exercised inside this contract's scope.**

This is a finding about the criterion, not something to force. Disposition: F-7(b) is discharged by
*recording and committing* the sets, and the reviewer must say in those words that the pin is
recorded and untested. Whoever proposes the first k≠0 member inherits F-7's first real test, and
should be told so.

#### 7.0.10 Who may grade, and a disclosure

F-18's eligibility rule applies to **each** gate independently, and is tightened here so it is
enforceable from the document rather than from memory:

- the lane that **built** the work under review may not record either verdict;
- the lane that **wrote this split** may not record the verdict graded against it;
- a summary attesting "all controls passed" is a FAIL of F-18 at either gate, unchanged.

**Disclosure.** §7.0 was written by the same fresh non-builder who recorded the round-1 verdict in
`VERIFICATION-20260822-k0-execution-integrity.md`. That reviewer reshaped this rubric and is
therefore **not eligible** to grade Gate 1 against it; a separate lane takes that verdict. The
round-1 verdict itself predates this amendment, graded §F as a single undifferentiated gate, and is
not restated or revised by it.

#### 7.0.11 F-9 RESTATED — B-4 is preserved, the criterion moves

**Authority: Joseph's ruling 20**, `DECISION-20260822-joseph-b1-lift-and-clause-c.md`, fourth set,
quoted there verbatim and not re-quoted in full here. Its operative sentence: F-9 now passes when the
real canonical-checkout wrapper is run with the clean tree as `--expect-root` and exits 3 through
B-4, records `refused:script-outside-expect-root` and never an empty/green verdict, names the script
and both roots, records `checked=0` **as expected**, and satisfies O-1…O-4 with no child marker or
output — and **must not name `seed_offset_policy`**, because the import guard is intentionally never
reached. *"No B-4 bypass flag or production exception is authorized."*

This subsection transcribes that ruling into gradable form. It is written by the author of §7.0 at
the coordinator's instruction; it is **not this lane's judgement and confers no eligibility to
grade** (§7.0.10 stands, and ruling 23 restates it).

**Why the original F-9 became unsatisfiable — the part worth carrying away.** B-4's containment check
sits above `guard = install(...)`, deliberately, *"so the refusal precedes not just the work but the
first import."* N-1 runs the real `mii_adopt_unified_5d_stamped.py` **from the canonical checkout**,
so its script is outside `--expect-root`, containment fires first, and the import guard is never
installed. `seed_offset_policy` therefore cannot be named and `checked` cannot rise above zero.
**F-9 was not failed by a defect. It was invalidated by B-4 working exactly as specified.**

> **THE TRANSFERABLE SHAPE, and it has now happened twice.** *A protection can invalidate the control
> written to test a different protection — and the control then presents as merely UNPERFORMED rather
> than as IMPOSSIBLE.* Ruling 19 found it in N-2; ruling 20 finds the identical shape in N-1. Both
> times the invalidating check is deliberately ordered *first*, so the interaction is predictable
> rather than unlucky. It survived a fresh non-builder's clause-by-clause verdict — which recorded
> F-9 only as "not performed" — and it survived §7.0.2 of this amendment, which used F-9 as its
> worked example. **"Not performed" and "cannot be performed" look identical from the outside, and
> nothing in a verdict distinguishes them unless someone tries to run the control.**

##### F-9, as it is now graded

The refused arm: the **real, unmodified** `mii_adopt_unified_5d_stamped.py`, run from
`/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding`, under `mnv_guarded_run.py` with
`--expect-root ${MNV_CODE_ROOT}` and an `--inventory` destination, with `--uthrow/--combined/--out`
pointed at throwaway scratch paths (**never** the defaults — the defaults name real archive
products). No `--allow` on any arm. All six must hold.

| # | requirement | how it is settled |
|---|---|---|
| 9.1 | exit **3**, through B-4 | the process's own status, captured unpiped (O-4). **Exit 3 alone does not discriminate** — B-4 and an import-tree violation share `VIOLATION_EXIT`. 9.2 is what tells them apart |
| 9.2 | `outcome` is exactly `refused:script-outside-expect-root`, and the verdict is **never** an empty or green one | read from the inventory record, not from stdout |
| 9.3 | names the script, the canonical root and the expected clean root | the B-4 banner prints all three; the record carries `script`, `script_checkout_root`, `expect_root` |
| 9.4 | `checked == 0` **and `guard_installed == false`**, together | see the inversion note — neither field alone is evidence |
| 9.5 | O-1…O-4, with **no child marker and no output** | `[remedyA] running the PINNED writer as a subprocess:` absent; `[adopt5d]` absent; `--out` fails `test -e`; the witness directory that started empty is still the empty set |
| 9.6 | `seed_offset_policy` is **neither required nor expected** on the refused arm — a CONSEQUENCE of 9.1–9.4, **not a string prohibition** | **do not grep the arm for the token.** Read 9.4's triple: the property is that no import was resolved. See the 9.6 subsection |

##### THE `checked=0` INVERSION — read this before applying §7.0.8

**In F-9, and only in F-9, `checked == 0` is the EXPECTED and REQUIRED value.** Everywhere else an
empty inspection set is the vacuity trap §0 exists to catch, and §7.0.8 says so in those words. Here
the guard is *intentionally never installed*, so a **non-zero** `checked` would mean containment did
not fire first and the arm is measuring something else. A grader carrying §7.0.8 forward unmodified
will fail F-9 incorrectly. §7.0.8 carries an explicit carve-out.

A bare zero cannot say which of two worlds produced it: `write_inventory` emits
`"checked": guard.checked if guard is not None else 0`, so the zero on the containment path is a
**default, not a measurement**, and is indistinguishable on its own from a guard that installed and
inspected nothing. `guard_installed` is the discriminator. Read the **pair**:

| state | `guard_installed` | `checked` | `outcome` | means |
|---|---|---|---|---|
| **F-9's required state** | `false` | `0` | `refused:script-outside-expect-root` | containment refused before install |
| import refusal — N-2's state | `true` | `> 0` | `refused:import-tree-violation`, `violation` non-null | the import guard refused |
| genuine empty-but-green — F-6's state | `true` | `> 0` | `ok`, verdict `EMPTY-REPOSITORY-ORIGIN-SET` | it looked and found nothing repository-local |
| **not evidence** | — | — | no record at all | the run establishes nothing |

This is P-3's own reasoning — *an absent key cannot distinguish "no repository import occurred" from
"the inventory did not run"* — applied to a **defaulted** key rather than an absent one.

##### 9.6 is a CONSEQUENCE, not a prohibition — Joseph's clarification of 2026-08-22

Ruling 20 said F-9 *"must not name `seed_offset_policy`"*. Asked to resolve the ambiguity that
created against the retained U/U' arm, **Joseph clarified, and the clarification is weaker than the
rule — deliberately so:**

> "In the refused F-9 arm, `seed_offset_policy` is neither required nor expected to appear, because
> B-4 refuses before imports begin. The separate U/U' comparison must retain and name
> `seed_offset_policy` as counterfactual origin evidence showing what would load without that
> containment. U/U' does not establish the mechanism of the F-9 refusal."

**"Neither required nor expected to appear" is not "must not appear", and the difference is
gradeable.** A prohibition makes the *string* a fail condition. **9.6 is not a string test.** The
absence is a **consequence** of 9.1–9.4: B-4 refuses before imports begin, so no import is resolved,
so there is nothing for the guard to name. **The gradeable property is that no import was resolved,
and 9.4's `guard_installed` / `checked` / `outcome` triple already establishes it positively.**

**How to grade 9.6, and it is a one-line rule:** *do not search the refused arm for a string.* Read
the triple. A rubric that forbids a token is testing a proxy for the property, and the proxy fails in
both directions — it can fail an arm that is correct, and it cannot catch an arm that is wrong.

- **What must NOT fail F-9:** an incidental occurrence of the token anywhere in or around the record
  — in a `sys_path_final` entry whose directory happens to contain the module, in surrounding receipt
  prose, in an error path, or in a capture that also holds another arm. **None of those is the guard
  naming a resolved import.**
- **What DOES fail F-9, and this is the positive falsifier:** `checked > 0`, or
  `guard_installed == true`, or a non-null `violation` naming a resolved import. Each of those says
  the import guard ran, which contradicts 9.1 — the refusal did not come from B-4, and the arm is
  measuring something other than containment.

**Measured, so the expectation is calibrated rather than assumed.** On a two-checkout fixture
reproducing F-9's shape against the build branch's guard — a wrapper in the canonical tree importing
a module genuinely named `seed_offset_policy`, run with the clean tree as `--expect-root` — the
refused arm produced **zero** occurrences of the token: none in the merged log, none anywhere in the
inventory record, and `sys_path_final` held directory paths only. So in practice the token simply is
not there. **That is a reason to stop testing for it, not a reason to keep testing for it**: a check
that always passes on correct input and is not tied to the property is decoration, and this contract
already refuses decoration elsewhere.

##### What the U/U' arm IS, and what it is NOT

Both halves must be stated together. A later reader who finds U/U' naming `seed_offset_policy`
beside an F-9 arm that does not will otherwise read a contradiction where there is a division of
labour.

- **IT IS:** *counterfactual origin evidence showing what would load without that containment*
  (Joseph, above). It answers "if B-4 were not there, which tree's `seed_offset_policy` would this
  wrapper have imported?" — and the answer, asserted on the loaded module's `__file__`, is the
  canonical checkout's copy. **It must retain and name `seed_offset_policy`; that is the whole point
  of the arm, and removing the name would empty it.**
- **IT IS NOT:** the mechanism of the F-9 refusal. F-9 refuses through B-4, before any import. U/U'
  contributes **no** part of 9.1–9.5 and cannot be cited for them. It discharges F-12(N-1)(iii) and
  nothing else.

Both statements are load-bearing. The first stops a later lane from "tidying" the name out of U/U'
on the strength of ruling 20's original wording; the second stops anyone citing U/U' as evidence
that containment fired.

##### THE THREE ARMS, AND HOW A GRADER TELLS THEM APART

They differ in `--expect-root` and in outcome, and two of them legitimately involve the canonical
checkout, so **the distinction must be carried by the record rather than by the reader's care.**

| arm | `--expect-root` | inventory record | exit | names `seed_offset_policy`? | what it establishes |
|---|---|---|---|---|---|
| **F-9 refused** | the **clean tree** (`MNV_CODE_ROOT`) | `script_checkout_root` = canonical, **≠** `expect_root`; `guard_installed=false`; `checked=0`; `outcome=refused:script-outside-expect-root` | **3** | not expected; not graded either way | containment refused before imports began |
| **O-1 paired** | the **canonical checkout** — the tree it was launched from | `script_checkout_root` **=** `expect_root`; `guard_installed=true`; `checked>0`; `outcome=ok` | **0** | may; not graded | the arm could have succeeded, so the refusal was not breakage |
| **U/U' unguarded** | **none** — the guard is not invoked at all | **no record exists** | 0 | **must**, on `__file__` | counterfactual origin: what would load without containment |

**`expect_root` is the arm's identity.** In the F-9 arm it is the clean tree and differs from
`script_checkout_root`; in the paired arm the two are equal; the U/U' arm has no record at all,
because no guard ran. A grader who cannot tell which arm a capture belongs to should read
`expect_root` first and everything else second.

**Each arm writes to its own inventory path and its own capture file.** This is a requirement, not
advice, and it is how the conflation is prevented structurally instead of by care. **O-3's "same
stream" rule is WITHIN an arm** — it exists so the refusal banner and the last stdout line can be
interleaved for one process — **and must not be read as one file for the whole control.** A single
combined capture would put U/U''s naming of `seed_offset_policy` into the same file as the F-9 arm,
which is the one way the token realistically appears near a refused arm at all.

##### O-1 for the restated F-9, and why the paired arm is permitted

O-1 still requires one binary and two outcomes. The paired arm is **the same real wrapper, same
launch directory, with `--expect-root` naming the canonical checkout it was launched from**:
containment then passes, the import guard installs, `seed_offset_policy` resolves *inside*
`--expect-root` and is allowed, and the process proceeds past
`[remedyA] running the PINNED writer as a subprocess:` (`mii_adopt_unified_5d_stamped.py:711`).
Refused arm: marker absent. Paired arm: marker present.

**That paired arm is permitted and a grader must not refuse it.** §2 forbids `--allow` on any
production arm. It says nothing against `--expect-root`, which is not `--allow`, and this is a
control rather than a production arm.

##### 9.2's dependency, and its state as measured

9.2 was **unsatisfiable** when ruling 20 was made. On a B-4 refusal the guard called
`_safe_inventory(..., violation=None, guard=None)`, and `write_inventory` fell through
`VERDICT_REFUSED if violation is not None else (VERDICT_INSPECTED if origins else VERDICT_EMPTY)` to
`EMPTY-REPOSITORY-ORIGIN-SET -- THE GUARD REFUSED NOTHING BECAUSE IT SAW NOTHING`. **Both clauses of
that string are false on a containment refusal**: the guard did refuse, and it refused before it
could see anything. The same false string was echoed to stderr, so a reader of a Slurm `.out` saw
"THE GUARD REFUSED NOTHING" on a run that refused.

**That is now fixed on the build branch, and the fix is verified here rather than taken on report.**
A third verdict constant `VERDICT_REFUSED_SCRIPT` was added at
`build-k0-execution-integrity` `a902b781`. Re-measured on a two-checkout fixture against
`nd-unfolding/mnv_guarded_run.py` as of `e39ab74f`, three arms:

| arm | exit | `guard_installed` | `checked` | `outcome` / verdict |
|---|---|---|---|---|
| script outside `--expect-root` (**F-9**) | 3 | `false` | 0 | `refused:script-outside-expect-root` / `REFUSED -- THE SCRIPT ITSELF LIES IN A CHECKOUT THAT IS NOT --expect-root` |
| paired, `--expect-root` = launch tree (**O-1**) | 0 | `true` | 7 | `ok` / `REPOSITORY-ORIGINS-INSPECTED`; marker present |
| stdlib-only entrypoint inside `--expect-root` (**F-6**) | 0 | `true` | 6 | `ok` / `EMPTY-REPOSITORY-ORIGIN-SET` |

**The third arm is the one that mattered and it is clear.** A fix that made every empty inventory
read as a refusal would have broken F-6, whose whole subject is the genuinely-empty-but-green record
for the pinned-writer child. `VERDICT_EMPTY` remains reachable and correct. **A grader must still
require both directions to be covered by a test in the suite, not only by this one-off fixture** — a
guard that fires on bad input and is silent on good input needs both arms pinned.

**Grade F-9 against the tree that carries B-4, and say which one.** `main` at `115c73bb` has neither
the containment check nor the inventory (`grep -c 'SCRIPT OUTSIDE THE EXPECTED TREE'` → 0,
`grep -c 'write_inventory'` → 0). F-9 is not gradable against `main`; it is gradable against the
build branch at the sha the Gate-1 submission declares.

#### 7.0.12 F-12 RESTATED for N-1 — the non-vacuity anchor moves, it does not disappear

N-2 and N-3 are **unchanged**: their hijack arms still assert the loaded module's `__file__`, and
they remain the import-resolution negative controls (ruling 20).

For N-1 the mechanism is no longer an import hijack, so `__file__` can no longer be the anchor —
**but F-12 must not quietly lose its teeth for N-1.** §5.5's rule is that a control whose fixture does
not genuinely hijack passes vacuously. The equivalent question here is *"was this arm capable of
succeeding at all, and is the refusal attributable to containment rather than to breakage?"* Three
things settle it:

- **F-12(N-1)(i) — the fixture really is misplaced.** From the refused arm's own inventory record:
  `script_checkout_root` equals the canonical checkout and is **not** `expect_root`. Asserted on the
  resolved path the guard actually computed, never on the command line as typed.
- **F-12(N-1)(ii) — the arm can succeed.** The O-1 paired arm reaches the `[remedyA]` marker and does
  not refuse. **Without this, a wrapper that was simply broken would produce the same silent,
  output-free refusal and F-9 would pass vacuously.** This is the direct analogue of N-2's
  `assertIn(STARTED, …)`, and it is the clause that would have caught the original F-9 collision.
- **F-12(N-1)(iii) — retained, and it MUST name `seed_offset_policy`.** The U/U' arm asserts
  `seed_offset_policy.__file__` under the canonical checkout: *counterfactual origin evidence
  showing what would load without that containment* (Joseph, 2026-08-22). Removing the name would
  empty the arm. It is **not** the mechanism of the F-9 refusal and cannot be cited for 9.1–9.5.
  See the two-halves statement and the three-arm table in §7.0.11.

#### 7.0.13 Ruling 21 — the 14/30 guarding boundary, and the ordering clause as a criterion

**Authority: Joseph's ruling 21.** Guard all **14** launcher-level science invocations and the
pinned-writer child. The **16** calls to the two preflight integrity tools are excluded from the
guard **and** from P-4, because guarding the tools *before they have validated the guard* is a
**trust-order inversion**, and their intentionally empty import sets would weaken P-4 with standing
exceptions. *"Both preflight tools must remain covered by the source manifest and executing-file
parity set and must run before any science invocation."*

**This boundary REPAIRS criteria written earlier in §7.0; it is not merely being given a home.**
F-2(a) and F-4(a) are counting tests of the form *"zero production `python3` invocations not routed
through the guard."* The 16 preflight calls **are** production `python3` invocations, so without this
boundary both criteria are unsatisfiable by construction — a defect this lane introduced in §7.0 and
ruling 21 removes. **F-2(a) and F-4(a) are to be read as: zero unguarded production invocations
*other than the enumerated preflight set*.** The partition table rows say so.

Three requirements follow. All are **PRE-SUBMISSION** and bench-checkable.

1. **The excluded set is enumerated and pinned, not open-ended** *(derived — from Joseph's own stated
   reason that standing exceptions weaken P-4)*. Exactly those 16 call sites are listed, and a test
   must **fail** when a production invocation appears that is neither guarded nor on the list. An
   exclusion that can grow silently is the standing exception the ruling exists to prevent.
2. **Both preflight tools remain covered by the A-2(f) source manifest and the A-3 parity set.**
   Excluded from the guard is not excluded from binding. Graded in **F-1(a)** (manifest membership)
   and **F-2(a)** (parity coverage).
3. **Both preflight tools run BEFORE any science invocation, in every launcher. A criterion, not a
   convention** — *"if a launcher can reach a science invocation without the preflight having run,
   that is a finding."* Graded in **F-2(a)**, and it must be settled by **running** each launcher
   under stubs and observing the order of the emitted argv, **not** by reading the file. A launcher
   is a sequence; `bash -n` has already passed over a hook-truncated command in this repository, and
   `tests/test_k0_launcher_two_roots.py` already establishes the run-it-under-stubs idiom.

##### The counts, re-derived here, and the instrument trap in re-deriving them

Ruling 21's enumeration — *"finalize 5, detector 2, uthrow-block 2, one each elsewhere"* — was
re-counted independently against `build-k0-execution-integrity` `80f44084` and **reproduces exactly:
14**, and the two preflight tools give **2 × 8 = 16**, totalling the 30.

> **Trap, recorded because the obvious command gets it wrong.**
> `grep -c -- '--expect-root' <the eight>` returns **22**, not 14. The extra eight are one **comment**
> per launcher that mentions the flag while explaining the nesting hazard. Filter comments first:
> `grep -v '^[[:space:]]*#' <launcher> | grep -c -- '--expect-root'` → 1, 1, 2, 1, 1, 2, 1, 5 = **14**.
> A grader who quotes 22 has counted an adjacent subject without erroring.

#### 7.0.14 Ruling 22 — A-2(d), (e), (g) become fail-closed checks; F-1(a) amended

**Authority: Joseph's ruling 22.** These *"may not remain merely documented."* **F-1(a) now requires
executable, fail-closed checks run before Gate 1**, each **refusing** rather than reporting:

- **(d)** no nested MINERvA-OmniFold checkout anywhere beneath the code root, in particular no
  `.claude/worktrees/` content;
- **(e)** the code root is not nested inside another checkout;
- **(g)** write protection **applied and verified** — not "applied".

(d) and (e) are the two directions of one nesting hazard. `checkout_root_of` returns the **innermost**
match, which is why a nested checkout inside the code root resolves to itself — the same mechanism
that once made the OI-136 ratchet read 369 instead of 58.

**Grade A-2(a)–(g) entire, not only the three the ruling names.** The round-3 builder's own commit is
titled *"A-2(c)(d)(e)(g) become fail-closed checks"* — (c), the both-markers checkout test, is
included beyond the ruling's list. That is a superset of what was ordered and is welcome, but F-1's
text has always said (a)–(g), so a grader should not narrow to the three that were singled out.

##### Verifying (g), and its honest residual

**"Verified" means an attempted write, as the job's own user, fails.** A `chmod` that was *issued* is
not evidence that a write is *refused*; that is the difference between a filter and a test of the
filter.

The residual, stated so nobody reads (g) as immutability: **every leg runs as the same user, and that
user can `chmod` the protection back off.** (g) is a barrier against accident and against a stray
process, not against the account. **(f) — the source manifest re-verified after every leg — is what
detects the case (g) cannot prevent.** That is the division A-2 already draws between them, and it is
the reason both exist rather than either alone.

#### 7.0.15 Ruling 22, second half — the P-4 pin is post-rehearsal, the mechanism is Gate-1

**Authority: Joseph's ruling 22.** *"Production P-4 pins are correctly a post-rehearsal artifact, but
the mechanism and its fail-closed behavior remain Gate-1 requirements."*

This confirms the line §7.0.5's F-7 row already draws, which is therefore unchanged:

- **F-7(a), Gate 1 — the mechanism.** A per-entrypoint expected-set pin; a comparator that aborts on
  a difference in **either** direction; tests for an added module, a removed module and an exact
  match; and **an absent or undeclared pin failing closed**. In the ruling's words, *"what must be
  provable now is that an undeclared or mismatched import set is refused, not that the real pins
  exist."*
- **F-7(b), Gate 2 — the pins.** Recorded from the rehearsal and committed.

§7.0.9 stands and is worth re-reading beside this: the rehearsal **establishes** the pin and cannot
**test** it, so F-7(b) is discharged by recording the sets and saying in those words that the pin is
recorded and untested. The preflight tools' exclusion from P-4 (§7.0.13) is part of the mechanism's
declared configuration and must be pinned **with** it, so that the exclusion cannot widen unnoticed.

#### 7.0.16 What this lane thinks is still ambiguous or needs care

Recorded so it can be attacked directly rather than rediscovered.

**(a) Both ambiguities in ruling 20 are now ANSWERED, not merely resolved by this lane.** Joseph
clarified on 2026-08-22 that in the refused F-9 arm `seed_offset_policy` is *"neither required nor
expected to appear"* and that U/U' *"must retain and name"* it as counterfactual origin evidence.
The scoping this lane had applied held, **but his formulation is weaker than ruling 20's and the
difference is gradeable**: a prohibition makes the token a fail condition, whereas an absence of
expectation makes it a consequence of B-4 refusing first. §7.0.11 now carries his formulation, and
9.6 is graded on 9.4's triple rather than on a string search. The second ambiguity — whether O-1's
paired arm may name the canonical checkout as `--expect-root` — is answered affirmatively in the
same section. **The lesson is worth keeping: when a rule and its rationale disagree, the rationale
is the thing to encode. A rubric that forbids a token is testing a proxy, and the proxy can fail a
correct arm while missing a wrong one.**

**(b) 9.2's dependency was real and is discharged**, verified in three directions in §7.0.11 —
including the silent direction, because a fix that turned every empty inventory into a refusal would
have broken F-6. The suite must still pin both directions; a one-off fixture is not a test.

**(c) `checked = 0` alone is not evidence**, because on the containment path it is a *default* rather
than a measurement. §7.0.11 requires the `guard_installed` / `checked` / `outcome` triple.

**(d) Ruling 21 repairs F-2(a) and F-4(a)** rather than merely finding them a home (§7.0.13). Two
criteria this lane wrote would otherwise have been unsatisfiable by construction.

**(e) A standing rule, because one shape has now recurred twice.**

> Every refusal site in `mnv_guarded_run.py` returns the same `VIOLATION_EXIT`, so **exit 3 never
> identifies which protection fired.** Therefore: **(i)** every exit-3 control must assert the
> `outcome` field — the stable machine-readable discriminator — and not merely the status; and
> **(ii)** whenever a fail-closed check is added *ahead of* an existing one, **every negative control
> downstream of it must be re-derived**, naming which refusal site it intends to fire. A control that
> does not name its intended site cannot notice when an earlier site begins short-circuiting it.

Ruling 19 found this in N-2 and ruling 20 found it in N-1. In both cases the control did not fail
loudly — **it presented as merely unperformed**, which is why it survived a clause-by-clause verdict.

**(f) No part of this weakens B-4, and no bypass is authorized.** Ruling 20 is explicit and it is
repeated here so a later reader cannot mistake a restatement for an exemption: *"No B-4 bypass flag
or production exception is authorized."* **What moved is the criterion, not the protection.**


---

**Tree**

- F-1 `MNV_CODE_ROOT` satisfies A-2(a)–(g), measured **immediately before** the first `sbatch` and
  again **after** the last leg. `git status --porcelain` emits zero lines at both ends and the
  A-2(f) manifest digest is identical at both ends.
- F-2 No production process executes or imports any file under
  `/pscratch/sd/j/josephrb/MINERvA-OmniFold`. Established by P-2 across every guarded process plus
  A-3's `--pair` set, not by inspection of the commands.
- F-3 `--allow` appears in **no** production invocation. Grep the submitted scripts and the job
  stdout; publish the command.

**Positive arm**

- F-4 Every guarded process emitted a P-1 inventory. Count of inventories == count of guarded
  processes; a missing inventory is a FAIL, not a gap.
- F-5 P-2 holds for every inventory: all repository origins under `MNV_CODE_ROOT`, all sha256 match
  the manifest, `checked > 0`.
- F-6 P-3's disclosure is present for `adopt_unified_5d.py`, and its `repo_origin_count` is recorded
  as an explicit `0` rather than an absent key.
- F-7 P-4's per-entrypoint import-set identity holds.
- F-8 P-5's blind spots are stated in the receipt in the receipt's own words, and P-6's entrypoint
  enumeration is published with its command.

**Negative controls**

- F-9 N-1 exits **3**, names `seed_offset_policy`, names both roots, and satisfies O-1…O-4.
  > **RESTATED 2026-08-22 by Joseph's ruling 20 — §7.0.11 supersedes this bullet.** The original
  > wording is preserved rather than edited: it is the pre-implementation agreement, and the reason
  > it had to change is itself evidence. B-4 script containment runs *before* `install()`, so the
  > real wrapper launched from the canonical checkout is refused by containment before any import
  > fires. **F-9 no longer requires `seed_offset_policy` to be named on the refused arm — it
  > forbids it — and `checked=0` is now the EXPECTED value.**
- F-10 N-2 exits **3** through the child wrapper on the `build_child_argv` template, and satisfies
  O-1…O-4.
- F-11 N-3 holds for each of the six B-1 files, both directions.
- F-12 §5.5's hijack arm is demonstrated for N-1, N-2 and each N-3, by asserting the loaded module's
  `__file__` — not by asserting exit 0.
  > **RESTATED 2026-08-22 for N-1 ONLY — §7.0.12 supersedes this bullet for N-1.** N-2 and N-3 are
  > unchanged and still turn on `__file__`. N-1's non-vacuity is re-anchored, because its mechanism
  > is no longer an import hijack.

**Repairs and couplings**

- F-13 B-4's script-containment refusal is implemented and covered in both directions.
- F-14 Every row of §6 is discharged in the same commit as the repair that moves it.
- F-15 `python3 -m unittest` over `nd-unfolding/tests/test_mnv_guarded_run.py` and
  `test_oi136_failopen_inventory_ratchet.py` is green, with the test counts quoted as measured
  (M-8: 24, not 21) and an explicit `TMPDIR`.
- F-16 `verify_hash_bindings.py` exits 0 with `ALL BINDINGS INTACT` **after** all edits.

**Freshness**

- F-17 M-1 through M-6 are **re-measured on `MNV_CODE_ROOT` at the pinned sha and on the canonical
  checkout as it stands at submission time**, and any difference from this document is reported as a
  finding. M-2 in particular is an inventory claim about 717 untracked files and is the most
  perishable statement here; the authorized work is exactly what can falsify it, so it is re-measured
  **after** the path runs as well as before.

**Reviewer**

- F-18 The PASS is recorded by a fresh non-builder against this document clause by clause, citing the
  artifact for each F-number. A summary attesting "all controls passed" is a FAIL of F-18.

---

## 8. §G — what a PASS here does and does not mean

A PASS discharges corrections 2–4 for the k=0 arm and nothing else. It is **not** a statement that
OI-136 is closed (52-odd fail-open files remain, and the 284 other `.sh` launchers), **not** an
authorization to submit leg 6 (staged separately under Amendment 1 §C), **not** an authorization for
any member k≠0, and **not** a scientific verdict of any kind. §5 of the plan's list of what a
one-member pass cannot authorize is unchanged by this contract.

---

## 9. §H — the decisions in here I think are most likely to be wrong

Recorded so a later reader can attack them directly rather than reconstruct them.

1. **B-2, declining the source repair on `adopt_unified_5d.py`.** It rests on M-1 (no repository
   import) plus M-2 (no shadowing name). M-2 is the weak leg: it is a name intersection against one
   interpreter's stdlib list and a hand-written third-party list, over a tree with 717 untracked
   files that can change tomorrow. If a colliding name appears, the file's insert becomes live and
   the repair becomes required. P-1's runtime inventory is what would catch it, which is why P-1 is
   mandatory rather than nice-to-have.
2. **A-1's two-root split.** It is the largest change this contract asks for and it is my own
   inference from the launchers' `cd`-and-write-relative structure, not something Joseph ruled. If
   there is an existing convention for separating code root from data root on this path I have not
   found it, and my `MNV_CODE_ROOT`/`MNV_DATA_ROOT` names would then be a second vocabulary for an
   existing one.
3. **N-2's fixture copy of the pinned writer.** Copying and editing a hash-pinned file, even as a
   declared fixture never executed on the production arm, is close to the move `OI-123` forbids.
   The alternative — accepting that the child boundary is simply untested on this path — may be the
   more honest disposition, and Joseph may prefer it.
4. **Treating `unified_throw_cov.py` as in scope.** It is a module, not an entrypoint; it is in the
   repair set only because `unified_throw_cov_5d.py` imports it after its own rooted insert and it
   carries a rooted insert of its own. Whether that counts as "this path's entrypoints" under
   correction 4's scope fence is a judgement, and a narrower reading would exclude it.

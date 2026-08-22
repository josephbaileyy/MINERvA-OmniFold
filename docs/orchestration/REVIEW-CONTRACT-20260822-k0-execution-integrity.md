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

**Nothing in this amendment changes what any criterion REQUIRES.** F-1 through F-18 below are
unedited and keep their numbers, so every existing citation of them — including
[`VERIFICATION-20260822-k0-execution-integrity.md`](VERIFICATION-20260822-k0-execution-integrity.md)
and Joseph's rulings — still resolves. This amendment says only **when** each criterion is settled
and **which of two verdicts** it belongs to.

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
| F-1 | SPLIT | code root constituted at a **named sha**; A-2(a)–(g) all measured and filed, including the A-2(f) source-manifest digest | the same measurements repeated after the last leg; porcelain zero and the manifest digest identical at both ends |
| F-2 | SPLIT — see **7.0.4** | both counts zero: unguarded production invocations, and executing files not covered by a `--pair` *(derived)* | P-2 holds across every inventory; every `--pair` CURRENT |
| F-3 | SPLIT | grep the eight launchers and every guard invocation → zero `--allow`; publish the command | grep the job stdout → zero `--allow`; publish the command |
| F-4 | SPLIT | the **denominator** is fixed on the bench: guarded production invocations == production Python invocations, and **> 0** *(derived — see 7.0.8)* | count of inventories == count of guarded processes |
| F-5 | SPLIT | the source-manifest generator and the inventory-vs-manifest comparator exist, and each carries a test that **fires on a mismatch** and is **silent on a match** *(derived)* | P-2 holds for every real inventory: origins under the code root, sha256 matching the manifest, `checked > 0` |
| F-6 | SPLIT | `build_child_argv` emits the guard and an inventory for the pinned-writer child; a test asserts an explicitly flagged `repo_origin_count: 0` record for that argv shape *(derived)* | the child's record is present in the run's inventory and the run receipt carries the B-2 disclosure sentence in the contract's own terms |
| F-7 | SPLIT | the P-4 mechanism exists: a per-entrypoint expected-set pin, a comparator aborting on a difference in **either** direction, tests for added / removed / exact-match, and an **absent pin failing closed** *(derived — see 7.0.9)* | the sets are recorded from the rehearsal and pinned |
| F-8 | SPLIT | P-6's enumeration re-run on `MNV_CODE_ROOT` at the pinned sha, published with its command and its **full** output and reconciled; P-5's blind-spot inventory produced, including the subprocess enumeration with each child either wrapped or recorded as uncovered | the receipt states the blind spots in the receipt's own words |
| F-9 | **PRE-SUBMISSION** | N-1 performed — exit 3, names `seed_offset_policy`, names both roots, satisfies O-1…O-4. **See 7.0.2: this needs the cluster, not a run** | — |
| F-10 | **PRE-SUBMISSION** | N-2 (as replaced by ruling 19) exits 3 through the child wrapper on the `build_child_argv` template, O-1…O-4 | — |
| F-11 | **PRE-SUBMISSION** | N-3 holds for each of the six B-1 files, both directions | — |
| F-12 | **PRE-SUBMISSION** | §5.5's hijack arm demonstrated for N-1, N-2 and each N-3, asserted on the loaded module's `__file__` | — |
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
- F-10 N-2 exits **3** through the child wrapper on the `build_child_argv` template, and satisfies
  O-1…O-4.
- F-11 N-3 holds for each of the six B-1 files, both directions.
- F-12 §5.5's hijack arm is demonstrated for N-1, N-2 and each N-3, by asserting the loaded module's
  `__file__` — not by asserting exit 0.

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

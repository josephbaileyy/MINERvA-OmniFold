# GATE-1 VERDICT (ROUND 4) 2026-08-23 — pre-submission readiness for the k=0 M(ii) member

**GATE 1 DOES NOT PASS.**

Stated in the words §7.0.6 requires: **Gate 1 DOES NOT PASS.** Sixteen of the eighteen
pre-submission halves pass; **two fail** — `F-2(a)` and `F-17(a)`. No criterion is recorded
NOT-EVALUABLE. Under §F's no-partial-credit rule as scoped by §7.0.6, any single miss at a gate is a
FAIL of that gate.

**What this blocks.** The seven jobs of logical legs 1–5 for k=0 are **not** authorized for
submission. `PR-J1` does not become operative. Gate 2 is not graded and legitimately cannot be.

**The decisive finding is not a filing gap.** The transitive environment trust boundary is not
merely *unbound* — it is **unsatisfied**. Every repo-relative shell file below `setup_salloc_env.sh`
is **absent from the declared code root**, and every launcher therefore **aborts at
`source "${CODE_ROOT}/setup_salloc_env.sh"` with exit 1**, before any preflight tool, any guard, or
any science invocation. Measured, not inferred: §2 below. The construction as built **cannot earn a
PASS**, and cannot be made to by disclosure or by first-hop binding, because A-2's own constitution
rule guarantees the absence. §4 gives the minimal repair.

**What this verdict does not say.** It does not say the package is bad work. Sixteen criteria pass,
most of them on mechanisms that are built, adversarially tested, and correct — the guard suite alone
carries 50 arms that pin both directions of every refusal site. The defect is at the one seam nobody
put a fixture on.

---

## 0. Eligibility, the object graded, and hygiene

**Eligibility (F-18, §7.0.10, ruling 23).** I am a fresh non-builder. I authored no code in this
repository, no part of the k=0 plan, no part of the review contract, no part of the §7.0 split, and
neither the round-1 nor the round-3 verdict. I did not build `PR-01`…`PR-06`.

**RUBRIC.** `main` @ `f04ac5cd36218a2e587e41793aee0ccb25a9edaa`,
`docs/orchestration/REVIEW-CONTRACT-20260822-k0-execution-integrity.md` — **1160 lines**, sha256
prefix `e0fb342b6466`. Verified this is the operative copy and not the branch's:

```
$ for r in f04ac5cd 6113a34d; do git show $r:docs/orchestration/REVIEW-CONTRACT-...md | wc -l; done
    1160        # main   -> carries §7.0, rulings 20-22 amendments
     575        # branch -> SUPERSEDED, pre-§7.0
```

The build branch carries the **superseded** contract. A verdict graded against the branch's copy
would be void. (Same conclusion the round-3 verdict reached, re-derived here rather than inherited.)

**CODE.** `origin/build-k0-execution-integrity` @ `6113a34d860ad9bcd643923d51170f228c80d894`.
**FILINGS.** `main` @ `f04ac5cd` — `DECLARATION-20260822-k0-submission-sha.md`,
`P5-P6-20260822-entrypoint-set-and-blind-spots.md`,
`MEASUREMENT-20260822-m1-m6-at-pinned-sha.md`.
**EXECUTING TREE.** `/pscratch/sd/j/josephrb/k0r2/clean` @ `6113a34d`.

**The two are DIVERGED, and the verdict must say so.** `git rev-list --left-right --count
f04ac5cd...6113a34d` → **24 16**; merge-base `8c156a37`; neither is an ancestor of the other. `main`
carries **none** of the mechanism — `MNV_CODE_ROOT` appears 0 times in
`sbatch_bootstrap_5d_gpu.sh`, `mnv_preflight_census.py` does not exist, and main's
`mnv_guarded_run.py` (281 lines, sha256 `57ba33f80124977c…`) has **zero** occurrences of
`SCRIPT OUTSIDE THE EXPECTED TREE`, `write_inventory`, or `guard_installed`. This is a legitimate
pre-merge state, not a defect; it is recorded so nobody grades the wrong tree.

**Digest claim, verified first.** The negative-control arms were run at code roots `de040d9b` /
`a902b781`; the graded sha is `6113a34d`. All five load-bearing files are **byte-identical** across
`de040d9b`, `48170de9` and `6113a34d`:

```
mnv_guarded_run.py               bd2ccce19181b075  (all three)
mnv_source_manifest.py           7779a6f977b2f02b
mnv_import_set_ratchet.py        75b07573aede8e6b
mii_adopt_unified_5d_stamped.py  e5bc51a4d482fcd2
adopt_unified_5d.py              e1260e8dec2d39cb
```

`git diff --stat 48170de9 6113a34d` is 12 files: the census tool, the exclusions JSON, the eight
launchers, and two test modules. **No guard and no entrypoint moved.** The earlier arms are about the
graded bytes.

**Hygiene.** Read-only throughout, in two detached worktrees outside `.claude/worktrees/`
(`scratchpad/grade-k0` @ `6113a34d`, `scratchpad/grade-main` @ `f04ac5cd`), both `git status
--porcelain` = 0 lines after all work. Cluster access read-only over `ssh saul.nersc.gov`. **No
Slurm job submitted. No `--allow` run. Nothing written to `/pscratch`. No scientific artifact
opened, moved or deleted.** Primary checkout unchanged: HEAD still `f04ac5cd`, the same two
pre-existing untracked files and nothing else.

**Shell notes, because two of them changed a number.** `/usr/bin/grep` throughout (the tool shell's
`grep` is a wrapper). Multi-file greps run under `/bin/bash -c`: **my first attempt in zsh silently
passed eight filenames as one argument and returned `--allow=0`, `--expect-root TOTAL=0` — both
false.** `TMPDIR=/private/tmp` on every suite. No `$?` read after a pipe; `git status --porcelain`
counted with `wc -l` on a redirected file.

---

## 1. The Gate-1 column, criterion by criterion

| # | verdict | one-line basis |
|---|---|---|
| F-1(a) | PASS | A-2(a)–(g) all MET, re-measured by me on the code root; declared digest reproduces |
| F-2(a) | **FAIL** | the environment chain is ABSENT from the code root — the path aborts before anything runs; plus bind-after-use on `lib_member_resume.sh` in all eight; plus PYTHONPATH injection of the canonical checkout |
| F-3(a) | PASS | 0 non-comment `--allow` in all eight; command published |
| F-4(a) | PASS | bench denominator 14 + child, >0, reproduced three independent ways |
| F-5(a) | PASS | generator + comparator exist, with fires-on-mismatch and silent-on-match arms |
| F-6(a) | PASS | `build_child_argv` emits guard + inventory, fail-closed twice; `repo_origin_count: 0` written unconditionally and asserted |
| F-7(a) | PASS | P-4 identity mechanism + fail-closed on an undeclared pin; §7.0.13 exclusion pinned and enforced |
| F-8(a) | PASS | P-6 re-run by me on the code root, output reproduces exactly; P-5 four blind spots + subprocess enumeration |
| F-9 | PASS | B-4 precedes `install()`; the six-row table discharged on the triple; digest claim verified |
| F-10 | PASS | ruling 19's replacement shape covered; suite green at the graded sha |
| F-11 | PASS | `test_n3_rooted_import_repair.py`, 8 arms, both directions + power/silence |
| F-12 | PASS | `__file__` anchors for N-2/N-3; N-1's three restated clauses discharged |
| F-13 | PASS | refusal implemented; refused-outside and NOT-refused-inside both covered |
| F-14 | PASS | every §6 row lands in `ae42ae8d` with its repair, verified by `git log -S`; `generate_manifest --check` rc=0 |
| F-15 | PASS | 57 tests OK, rc=0; counts as measured **50 and 7** |
| F-16 | PASS | `ALL BINDINGS INTACT`, rc=0, on branch and on main |
| F-17(a) | **FAIL** | M-5's re-measurement answers about `REPO=` and reads as if the `.sh` half is repaired; the difference that decides Gate 1 is unreported |
| F-18(a) | PASS | this document |

**TALLY: 16 PASS / 2 FAIL / 0 NOT-EVALUABLE.**

**A grading discipline I applied on purpose, stated so it is not read as softening.** The §2 defect
would let me fail F-1(a) (A-2 is green on a tree that cannot execute), F-4(a) (the realized guarded
count at run time is 0, not 14) and F-8(a) (P-5 does not name the largest uncovered item). I graded
each of those **as written** and PASS, and carried the defect once, at F-2(a), where it substantively
belongs. Stacking one defect into four rows inflates a tally and hides which mechanism is broken. The
flags are recorded in each row's section below.

---

## 2. THE TRANSITIVE ENVIRONMENT TRUST BOUNDARY — settled, and it settles adversely

Joseph's instruction: *"Do not call Gate 1 closed until the transitive environment trust boundary is
explicitly settled and a fresh non-builder passes it."* It is settled. **It does not pass**, and it
fails harder than "unbound".

### 2.1 The boundary, enumerated to its floor

`setup_salloc_env.sh` is 24 tracked lines. It resolves **three** paths against
`SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"` (`:2`) — not two:

```
:18  source "${SCRIPT_DIR}/unbinned_unfolding/build/setup.sh"
:20  export MINERVA_PREFIX="${SCRIPT_DIR}/MINERvA101/opt"
:21  source "${SCRIPT_DIR}/MINERvA101/opt/bin/setup.sh"
```

The closure below it, measured on the canonical checkout (the only tree that has it):

| hop | file | sha256 | tracked? |
|---|---|---|---|
| 1 | `unbinned_unfolding/build/setup.sh` | `40ff3a3d0c0308a82d90fd6cb4858696931fa00563277e5865141f8ebdc84598` | no |
| 1 | `MINERvA101/opt/bin/setup.sh` | `e22a5b93d327111bf6ffc80f15ef36b908fab642072a6ef296e8bb9cd3719ba6` | no |
| 2 | `MINERvA101/opt/bin/setup_MAT.sh` | `733e9cd839a0f75186d109eaab3dfe746a921d6d7b0347fbd6662b6f1ced3c0e` | no |
| 2 | `MINERvA101/opt/bin/setup_MAT-MINERvA.sh` | `c259101619ac365dcc57043d8ac4926908e51a8a87dad08f601394c9b418c3ac` | no |
| 2 | `MINERvA101/opt/bin/setup_UnfoldUtils.sh` | `bd305c17ddcd507f88ab49cbfcf5fe5a14075e0c1a173e631addcb3423212cd9` | no |
| 3 | — | *none; the hop-2 files source nothing* | — |

Plus a second, wider limb the ruling does not mention: `:13` `eval "$("$ROOT628_CONDA" shell.bash
hook)"` and `:14` `conda activate`, which execute **12** `activate.d` scripts in
`$HOME/.conda/envs/root_6_28/etc/conda/activate.d/`, outside the repository entirely. Both
`ROOT628_PREFIX` and `ROOT628_CONDA` are `${VAR:-default}` — **environment-overridable**, so
verifying the activator's bytes does not constrain which conda it invokes.

```
$ git -C <code root> ls-files -- unbinned_unfolding/build/setup.sh MINERvA101/opt/bin/setup.sh
(empty)
$ git -C <code root> check-ignore -v unbinned_unfolding/build/setup.sh MINERvA101/opt/bin/setup.sh
.gitignore:71:unbinned_unfolding/**    unbinned_unfolding/build/setup.sh
.gitignore:48:MINERvA101/**            MINERvA101/opt/bin/setup.sh
```

They are not merely untracked — they are **ignored by two wildcard rules**. That is what makes the
next subsection structural rather than an accident of this deploy.

### 2.2 They are ABSENT from the declared code root, and the path aborts

```
$ C=/pscratch/sd/j/josephrb/k0r2/clean
$ for r in unbinned_unfolding/build/setup.sh MINERvA101/opt/bin/setup.sh \
           MINERvA101/opt/bin/setup_MAT.sh MINERvA101/opt/bin/setup_MAT-MINERvA.sh \
           MINERvA101/opt/bin/setup_UnfoldUtils.sh; do
    [ -e "$C/$r" ] && echo "PRESENT $r" || echo "ABSENT  $r"; done
ABSENT  unbinned_unfolding/build/setup.sh
ABSENT  MINERvA101/opt/bin/setup.sh
ABSENT  MINERvA101/opt/bin/setup_MAT.sh
ABSENT  MINERvA101/opt/bin/setup_MAT-MINERvA.sh
ABSENT  MINERvA101/opt/bin/setup_UnfoldUtils.sh
```

`$C/unbinned_unfolding/` contains only `python/`; `$C/MINERvA101/` contains only
`MINERvA-101-Cross-Section/`. There is no `build/` and no `opt/`.

**The decisive arm — the launcher preamble replicated exactly, in a child shell, read-only.** All
eight launchers carry `set -eo pipefail` before an unguarded
`source "${CODE_ROOT}/setup_salloc_env.sh"` (`bootstrap:21/81`, `seedscan:8/68`,
`unfold:16/223`, `sweep:14/76`, `uthrow_run:15/75`, `uthrow_block:11/71`,
`uthrow_combine:12/72`, `finalize:12/74`):

```
$ bash <<'EOF'
set -eo pipefail
CODE_ROOT=/pscratch/sd/j/josephrb/k0r2/clean
for _p in setup_salloc_env.sh lib/resume_guard.sh; do          # PR-02's pure-git gate, verbatim
  h="$(git -C "$CODE_ROOT" rev-parse "HEAD:${_p}")"; w="$(git -C "$CODE_ROOT" hash-object "${CODE_ROOT}/${_p}")"
  [ "$h" = "$w" ] || exit 3
done
echo "[repro] parity gate PASSED"
source "${CODE_ROOT}/setup_salloc_env.sh"
echo "[repro] REACHED_LINE_AFTER_SOURCE"
EOF
[repro]   setup_salloc_env.sh: HEAD=b4a9c3f6bb766d8488cbab98878cbac1262cc1bb work=b4a9c3f6bb766d8488cbab98878cbac1262cc1bb
[repro]   lib/resume_guard.sh: HEAD=a89f72d3e3c2717f70d3086eb2cb86e95f0eb165 work=a89f72d3e3c2717f70d3086eb2cb86e95f0eb165
[repro] parity gate PASSED -- both files match HEAD
.../setup_salloc_env.sh: line 18: .../k0r2/clean/unbinned_unfolding/build/setup.sh: No such file or directory
REPRO_EXIT=1
```

`REACHED_LINE_AFTER_SOURCE` **never printed.** Confirmed on the target interpreter (bash 4.4.23 on
`saul`, vs bash 3.2 locally): `source` of a missing file under `set -eo pipefail` exits 1.

**So on the declared submission sha and the declared code root, every k=0 leg dies at the activator.**
No preflight tool runs. No guard runs. No science invocation runs. `PR-02`'s gate passes — and it is
the last thing that happens.

Independently: **both preflight tools also require the conda interpreter, which only the activator
provides.** With `/usr/bin/python3` (3.6.15, measured pre-conda) on the code root:

```
$ python3 mnv_source_manifest.py ...   -> SyntaxError: future feature annotations is not defined
$ python3 mnv_preflight_census.py ...  -> TypeError: 'type' object is not subscriptable
```

Both run clean under `~/.conda/envs/root_6_28/bin/python3` (3.11.14). So the dependency is circular
in exactly the direction `PR-02` identified — and `PR-02` fixed the *checker's* toolchain dependency
while the *checked object* remained unreachable.

### 2.3 Even if the files were materialized, the content is adverse

```
$ cat unbinned_unfolding/build/setup.sh
#!/bin/bash
# this is an auto-generated setup script
export PATH=/pscratch/sd/j/josephrb/MINERvA-OmniFold/unbinned_unfolding/build:${PATH}
export PYTHONPATH=/pscratch/sd/j/josephrb/MINERvA-OmniFold/unbinned_unfolding/build:${PYTHONPATH}
export LD_LIBRARY_PATH=/pscratch/sd/j/josephrb/MINERvA-OmniFold/unbinned_unfolding/build:${LD_LIBRARY_PATH}
```

It **hardcodes the canonical checkout** onto `PATH`, `PYTHONPATH` **and** `LD_LIBRARY_PATH`. Sourcing
it puts `/pscratch/sd/j/josephrb/MINERvA-OmniFold` on the executable and import search paths of every
production process — which is F-2's substantive prohibition (*"No production process executes or
imports any file under /pscratch/sd/j/josephrb/MINERvA-OmniFold"*), violated **by content**, not by a
command line. The OI-136 import guard would refuse a Python import resolving there (fail-closed, and
correct), but it is blind to `PATH` and to `LD_LIBRARY_PATH` entirely. And the file is
*auto-generated*, so it hardcodes wherever it was built — copying it forward carries the forbidden
path with it.

### 2.4 The repository already contains this diagnosis, committed and unreferenced

`nd-unfolding/pet/g2_data_root_setup_salloc_env.template.sh` — present on **both** `6113a34d` and
`f04ac5cd`, referenced by nothing (`grep -rln` → empty). Verbatim, `:15-24`:

> *"AND BOTH TREES ARE UNTRACKED: `git ls-files unbinned_unfolding/build/setup.sh
> MINERvA101/opt/bin/setup.sh` returns 0, so **NO git worktree or frozen deployment will ever contain
> them**. Sourcing the activator from the deployment instead of the data root is therefore not an
> option either — **it is unavailable by construction**. … THE REAL DEFECT IS A CONFLATION:
> `GATE5_DATA_ROOT` names both WHERE THE DATA IS and WHERE THE SOFTWARE ENVIRONMENT IS. … the right
> long-term fix is a separate `GATE5_ENV_ROOT` in both launchers."*

It also records the same measurement I took, on the same shape, and a trap for the repair (`:25-37`):
adding `set -u` to anything sourced into the launcher shell **killed job `57235710` in 10 seconds**,
because conda's `activate-binutils_linux-64.sh` references `ADDR2LINE` unbound.

**A-1's two-root split reproduced, one level deeper, the exact conflation this template was written
to fix.** It separated *code* from *data* and left the *environment* bound to the code root through
`SCRIPT_DIR`. Contract §H.2 flagged the risk in the right words — *"If there is an existing
convention for separating code root from data root on this path I have not found it"* — and the
convention existed, in the repository, unreferenced.

### 2.5 Why disclosure and first-hop binding cannot close it, structurally

A-2 requires the code root to be constituted by `git clone` or `git worktree add` **at a named sha**,
with `git status --porcelain` emitting **zero lines**, and A-2(f)'s manifest to cover *tracked*
`*.py`/`*.sh`. Against a closure that is gitignored by `.gitignore:48` and `:71`:

1. **Any tree satisfying A-2(a)/(f) necessarily lacks the closure** → the path aborts. This is not
   about `k0r2/clean`; it is about the constitution rule.
2. **Copying the closure in does not repair the instruments.** The files stay *ignored*, so A-2(b)
   still emits zero lines and A-2(f) still excludes them. The code root's own integrity checks remain
   structurally blind to the bytes that set up the executing environment — a green A-2 over an
   unmeasured environment.
3. **`git add -f` would bind them and break them.** `unbinned_unfolding/build/setup.sh` is
   auto-generated with an absolute path; committing it pins the canonical checkout into the tree.

So the answer to the assigned question is: **no, the existing construction cannot earn PASS**, and
the failure is at the level of A-2's design, not at the level of what was filed about it.

### 2.6 Why 29 green launcher arms are silent about all of this

`nd-unfolding/tests/test_k0_launcher_two_roots.py` `LauncherFixture.setUp` writes:

```python
(self.code / "setup_salloc_env.sh").write_text(
    'echo "[stub] setup_salloc_env sourced from $BASH_SOURCE"\n')
```

**The fixture replaces the one file whose real content is the entire blocker with a one-line stub
that sources nothing.** Every arm in `EveryInvocationIsGuarded`,
`ThePreflightRunsBeforeAnyScience`, `TheP4RatchetReadsWhatTheRunProduced` and
`SourcedFilesAreVerifiedBEFORETheyAreSourced` runs against a code root with no transitive
dependencies at all. The fixture agrees with the code, not with the world.

And `test_the_disclosure_is_TRUE_those_two_scripts_really_are_untracked` pins *untrackedness* — a
property of the repository, true, and one that will stay true forever — while never asserting the
property that decides the gate: that the closure is **reachable from `MNV_CODE_ROOT` at run time**.
It is a one-directional guard that cannot fire on the actual defect.

---

## 3. The two FAILs, and the PASSes with flags

### F-2(a) — FAIL. Three independent grounds.

**(i) The count is not zero, and the criterion's subject never executes.** F-2(a) requires *"the
number of `.py` and `.sh` files that will execute on the path, plus `mnv_guarded_run.py` itself, not
covered by an A-3 `--pair`"* to be **zero**. Enumerated:

| file | status |
|---|---|
| `setup_salloc_env.sh` | tracked; not `--pair`ed **by design** — `PR-02`'s pure-git gate instead. Accepted under ruling 25. |
| `lib/resume_guard.sh` | same; accepted |
| `unbinned_unfolding/build/setup.sh` | untracked **and absent** → unpairable |
| `MINERvA101/opt/bin/setup.sh` | untracked **and absent** → unpairable |
| `MINERvA101/opt/bin/setup_MAT.sh` | untracked **and absent** → unpairable |
| `MINERvA101/opt/bin/setup_MAT-MINERvA.sh` | untracked **and absent** → unpairable |
| `MINERvA101/opt/bin/setup_UnfoldUtils.sh` | untracked **and absent** → unpairable |
| 12 conda `activate.d/*.sh` | outside the repository → unpairable |

**Count ≥ 5 (17 counting the conda limb), not zero.** The first count — unguarded production
invocations other than the 16 preflight — is **undefined at run time**, because the abort in §2.2
precedes the first invocation.

**(ii) `lib_member_resume.sh` is bind-after-use in all eight launchers.** It is sourced from
`${_mr_lib}`, a path **discovered by a search loop**, and the check that `_mr_lib` *is*
`${CODE_ROOT}/nd-unfolding` runs **after** the source:

| launcher | `source "${_mr_lib}/lib_member_resume.sh"` | containment check | `--pair` |
|---|---|---|---|
| bootstrap | :202 | :218 | :145 |
| seedscan | :189 | :206 | :132 |
| unfold_detector | :201 | :218 | :145 |
| sweep_bank | :197 | :214 | :141 |
| uthrow_run | :198 | :215 | :142 |
| uthrow_block | :192 | :209 | :136 |
| uthrow_combine | :208 | :225 | :152 |
| **finalize** | **:116** | :132 | **:259** |

This is ruling 25's prohibition verbatim — *"do not redefine an after-the-fact check as preflight"* —
and it is the **identical shape `PR-02` itself found and fixed for `_mr_rg`**, whose own commit
message states the principle: *"the file verified at preflight and the file actually sourced can be
two different objects."* `finalize` is the worse case: `lib_member_resume.sh` executes at `:116`
with **neither** byte verification **nor** path containment beforehand, and it defines `mr_run`,
which wraps every subsequent science invocation.

**(iii) The `PYTHONPATH`/`PATH`/`LD_LIBRARY_PATH` injection of the canonical checkout** — §2.3. F-2's
substantive prohibition is violated by the content of a file no `--pair` and no Python guard can
reach.

**Not counted against F-2(a), and recorded so it is not lost:** `ROOT628_PREFIX` and `ROOT628_CONDA`
are `${VAR:-default}`, so the activator's verified bytes do not determine which conda executes.

### F-17(a) — FAIL. The difference that decided the gate was not reported.

F-17(a) requires M-1…M-6 re-measured on both trees *"and any difference from this document is
reported as a finding."* Four differences were reported and two were honestly flagged as stale in the
builder's favour — that part is good work. The failure is **M-5's subject**.

M-5 is *"the `.sh` half is unrepaired on all eight launchers."* The re-measurement answers a narrower
question — `grep -nE '^\s*(export\s+)?REPO=' → 0 assignments` — and concludes *"the contract's
finding is now FALSE there."* That is true of `REPO=` and false of the `.sh` half. On the same tree,
at the same sha, the `.sh` half still contains: an environment chain that is unrepaired, unbindable
and **absent** (§2.2), and a bind-after-use source in all eight (above). As filed, `M-5` reads as
though the shell route is repaired, which is the class of error `F-17(a)` exists to catch —
**measurability chose the specification**: the cheap, greppable half was re-measured and reported as
the whole.

M-4 I re-measured and it holds exactly: `b2d7d4ca24707344cf12f99c0aa51381b81dd445`, `721` dirty =
`717 ??` + `4 M`.

### PASSes carrying a flag

- **F-1(a) PASS.** Re-measured by me on the code root, unpiped, with the conda interpreter:
  `A2_CHECK_EXIT=0` for `--require-clean --require-checkout --require-no-nested-checkout
  --require-not-nested --require-readonly`; `775 tracked source files, listing sha256
  cc00489464b0e803247eeb7cd90afa2f59f010340f6db64123e12b20eafc2239, HEAD 6113a34d…, dirty 0` —
  **identical to the declared digest**; independent `find . -path ./.git -prune -o -type f -writable
  -print | wc -l` → **0**; `nd-unfolding` is `dr-xr-x---`, `setup_salloc_env.sh` is `-r--r-----`.
  **Flag 1:** §7.0.14 says *"verified means an attempted write, as the job's own user, fails."* I did
  not attempt a write — that is a write. I have mode bits plus two independent read instruments;
  the attempted-write arm is still owed by someone with authorization to make it.
  **Flag 2:** every one of these seven is green on a tree that cannot execute the path. A-2 as
  written cannot see that, which is the §2.5 finding.
- **F-4(a) PASS on the bench denominator**, reproduced three independent ways: non-comment
  `--expect-root` = **14** (raw 22 — the eight extras are one comment per launcher, the trap §7.0.13
  names, and I reproduced the wrong 22 first); P-6's `--` target pattern = 14 (`4+2+2+2+1+1+1+1`);
  census = `14 guarded + 16 declared-preflight + 0 unclassified = 30`, `rc=0`, on the local tree and
  again on the code root. **Flag:** the *realized* count at run time is **0**, not 14.
- **F-8(a) PASS.** P-6 re-run by me on `MNV_CODE_ROOT` at the pinned sha; output reproduces the filed
  table exactly. **Flag:** P-5's blind-spot inventory names four items and does **not** name the
  transitive environment closure or the `PYTHONPATH` injection — the two largest uncovered items on
  the path. Graded under F-2(a); a repair to P-5 must not be forgotten because F-8(a) passed.
- **F-9 / F-10 / F-12 PASS, with provenance stated.** I verified the mechanism at the graded bytes
  (`mnv_guarded_run.py:510-524` containment precedes `guard = install(...)` at `:526`;
  `VERDICT_REFUSED_SCRIPT`, `outcome`, `guard_installed`, `checked_provenance`, `refusal_site` all
  present), the byte-identity of those bytes with the shas the arms ran at, and that the suite pins
  both directions of every refusal site. **I did not re-run N-1 myself.** These three rest on
  `RECEIPT-20260822-k0-n1-and-guarded-arms.md` as independently verified in the round-3 verdict, plus
  my digest and mechanism checks. Stated plainly rather than presented as first-hand.

### PASSes, measured

- **F-3(a)** — `--allow` non-comment count = **0** in all eight (one raw hit,
  `sbatch_sweep_bank_5d_run_bkgaware_gpu.sh:11`, is a comment about the unrelated
  `--allow-cv-background`). Arm `test_no_allow_FLAG_appears_on_any_command_line_in_any_launcher` green.
- **F-5(a)** — `mnv_source_manifest.py` + `mnv_import_set_ratchet.py`;
  `test_source_manifest_constitution` (28) and `test_p4_ratchet_fail_closed` (30) green, including
  `test_a_source_manifest_that_has_MOVED_stops_the_launcher_before_any_python` and
  `test_SILENT_on_an_unmutated_tree` — fires-on-bad and silent-on-good, both pinned.
- **F-6(a)** — `build_child_argv` (`mii_adopt_unified_5d_stamped.py:291-343`) emits
  `[python, guard, --expect-root, R, --inventory, I, --, writer, …]`, fail-closed at `:333` (guard
  absent) and `:337`/`:781` (no inventory). `repo_origin_count` written unconditionally
  (`mnv_guarded_run.py:379`); asserted PRESENT-and-zero at `tests/test_mnv_guarded_run.py:443-445`.
- **F-7(a)** — identity-not-floor comparator, malformed line raises rather than skips
  (`mnv_import_set_ratchet.py:54`), undeclared empty set is a failure (`:13-14`); 30 fail-closed arms
  green. Exclusion pinned in `mnv_preflight_exclusions.json` (`mnv_preflight_exclusions/1`) with
  counts derived by instrument; 13 census arms green.
- **F-11** — `tests/test_n3_rooted_import_repair.py`, `Ran 8 tests OK`: pre-repair loads the other
  tree's copy, `PYTHONPATH` cannot outrank position 0, post-repair resolves to its own tree,
  prologues derive from `__file__` with **no absolute fallback**, plus a power arm and a
  silent-on-legitimate arm on the offender checker.
- **F-13** — `test_a_script_in_another_checkout_is_refused_3` **and**
  `test_the_SAME_script_inside_expect_root_is_NOT_refused`, plus
  `test_allow_does_NOT_launder_a_script_from_another_checkout` and
  `test_a_script_outside_EVERY_checkout_is_not_refused_and_is_recorded_as_such`. Both directions.
- **F-14** — coupling verified by search, not by report:
  `git log --oneline -S"FAILOPEN_COUNT = 52"` → `ae42ae8d`, and
  `git log --oneline -S"parents[1]" -- nd-unfolding/unified_throw_cov.py` → `ae42ae8d`. Same commit.
  `FAILOPEN_COUNT` 58 → **52** (six repairs, six departures). `POSITIVE_CONTROLS` replaced from the
  probe's own output → `adopt_unified_5d.py`, `3d-unfolding/unfold_3d_omnifold_unbinned.py`;
  `unfold_nd_omnifold_unbinned.py` correctly removed. `--pair "${GUARD}=…"` assertion retained at
  `test_oi136_failopen_inventory_ratchet.py:192`. §7.0.7(1): `generate_manifest.py --check` **rc=0**
  on the branch (425 rows) and on main (431 rows), both in clean detached worktrees.
- **F-15** — `TMPDIR=/private/tmp python3 -m unittest test_mnv_guarded_run
  test_oi136_failopen_inventory_ratchet` → **`Ran 57 tests … OK`, rc=0.** Counts as measured at the
  graded sha: **50 and 7** — not 21 (the plan), not 24 (M-8), not 41. Broader: **157** across six
  coupled modules (50/7/29/13/30/28), rc=0.
- **F-16** — `verify_hash_bindings.py` → **rc=0, `ALL BINDINGS INTACT`**, 24 bindings in 12
  self-declared fixtures held out, fixture-set digest `36355204b4b8…`. Re-run on **main** as well,
  since `0f1b7b8d` edited that file: also rc=0.

**One claim of `PR-02` I checked because everything rests on it, and it holds.** On a bare login
shell: `git 2.51.0` at `/usr/bin/git`, `/usr/bin/python3` = **Python 3.6.15**. Ruling 25's
feasibility note (*"standard library plus git, so an earlier invocation appears practical"*) is
indeed falsified by the **interpreter**, not the imports, and pure git was the right substitution.

---

## 4. THE MINIMAL REQUIRED REPAIR — and then stop

Five parts. Parts 1–3 are the boundary; part 4 is the independent ruling-25 violation; part 5 is what
makes any of it falsifiable. **No submission, no rehearsal, and no downstream work is authorized by
this verdict.**

1. **A third root: `MNV_ENV_ROOT`, mandatory with no default** (`: "${MNV_ENV_ROOT:?}"`), distinct
   from `MNV_CODE_ROOT` and `MNV_DATA_ROOT`. Launchers source
   `${MNV_ENV_ROOT}/setup_salloc_env.sh`, so `BASH_SOURCE[0]` makes `SCRIPT_DIR` the env root and
   **all three** references (`:18`, `:20`, `:21`) resolve where they live. **Not a symlink** —
   `BASH_SOURCE[0]` is the path *as sourced* (`g2_data_root_setup_salloc_env.template.sh:11-13`).
   That template is the shape; generalize it instead of inventing a fourth vocabulary.
2. **A digest-bound environment manifest, verified BEFORE the source.** Git cannot bind these bytes,
   so substitute the mechanism rather than relocating it — the same move `PR-02` made for the
   interpreter. Pin `sha256` for the full closure: the 2 hop-1 files, the 3 hop-2 files, and the 12
   `activate.d` scripts. Digests as of 2026-08-23 are in §2.1. Also pin `ROOT628_PREFIX` and
   `ROOT628_CONDA` to declared values instead of `${VAR:-default}`, or the manifest describes a
   conda the run need not use.
3. **Remove the canonical checkout from `PATH`/`PYTHONPATH`/`LD_LIBRARY_PATH`.** Regenerate
   `unbinned_unfolding/build/setup.sh` against `MNV_ENV_ROOT`, or make the env root a tree that is
   not the canonical checkout. Then add a fail-closed check, after the source and before the first
   science invocation, that none of the three variables contains
   `/pscratch/sd/j/josephrb/MINERvA-OmniFold`. Without it, F-2's substantive prohibition has no
   enforcement on the shell route at all.
4. **Verify-before-source for `lib_member_resume.sh` in all eight.** Move the `_mr_lib` containment
   check **above** the `source`, exactly as `PR-02` did for `_mr_rg` (`finalize:183-192`); in
   `finalize`, above `:116`.
5. **Three test arms, and the fixture must stop stubbing the activator.**
   `LauncherFixture` must give the fixture code root an activator with a **real** transitive
   `source`. Then: **(a)** a closure member absent → the launcher **refuses**, naming the missing
   path, *before* any science invocation — not `set -e` death 40 lines later; **(b)** **SILENT** when
   the env manifest matches; **(c)** **fires** when any closure member's digest moves.
   **Do not add `set -u`** to anything sourced into the launcher shell:
   `activate-binutils_linux-64.sh` references `ADDR2LINE` unbound and this already killed job
   `57235710` in 10 seconds (`g2_data_root_setup_salloc_env.template.sh:25-37`).

**Then re-declare and re-grade.** `PR-01` expires on *"any commit to
`build-k0-execution-integrity`; any change to `k0r2/clean`; any `.py`/`.sh` add or delete"* — parts
1–5 trip all three. `PR-05` must be re-run immediately before the next grading, and its `M-5` must be
restated against the `.sh` half rather than against `REPO=`. `PR-04`'s P-5 must add the two blind
spots in §2.3 and §2.1. The next grader must be a fresh non-builder who is not me.

---

## 5. What this verdict does and does not authorize

Nothing. §G is unchanged. **The k=0 rehearsal is not launched and no downstream work is authorized.**
Gate 2 is not graded. `OI-136` is not closed. No member `k≠0`, no leg 6, no scientific verdict of any
kind. The two-gate split, the 14/30 boundary, and rulings 12–25 are untouched by this document.

## 6. The parts of this verdict most likely to be wrong

Recorded so they can be attacked directly.

1. **That the boundary is unfixable within A-2 as written (§2.5).** It rests on the two `.gitignore`
   wildcards and on the constitution rule. If Joseph rules the env root out of A-2's scope entirely
   — a declared, digest-bound tree that is *not* required to be a git checkout — then part 1 of the
   repair changes shape and my "structural" framing is too strong. The measurement in §2.2 stands
   either way.
2. **Grading F-1(a), F-4(a) and F-8(a) as PASS.** A stricter grader would fail all three on the §2
   defect and report 13/5/0. I think carrying one defect once is right, but the tally is sensitive to
   that choice and the choice is mine, not the contract's.
3. **F-9, F-10 and F-12 are not first-hand.** I verified the bytes, the mechanism and the digest
   chain; I did not re-run N-1. If the receipt's arms were mis-transcribed, my checks would not
   catch it — only re-running would.
4. **A-2(g) has no attempted-write arm from me**, because that is a write. The mode bits and two read
   instruments agree, which is weaker than §7.0.14 asks for.

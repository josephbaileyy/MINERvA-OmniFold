# RECEIPT 2026-08-22 — N-1, the paired hijack arm, and the first guarded production arm

**Status: EVIDENCE, not a verdict.** Recorded by the k=0 builder lane. Nothing here is a PASS, no
Slurm job was submitted, no scientific workload ran, and the 41.44 GB combined intermediate was
neither opened nor named as an input. The fresh non-builder's verdict is what closes these clauses
and it is not recorded here.

**Governing authority.** [`DECISION-20260822-joseph-b1-lift-and-clause-c.md`](DECISION-20260822-joseph-b1-lift-and-clause-c.md)
rulings 17–19 and Joseph's round-2 authorization of 2026-08-22, against
[`REVIEW-CONTRACT-20260822-k0-execution-integrity.md`](REVIEW-CONTRACT-20260822-k0-execution-integrity.md)
§5 (N-1), §5.4 (ordering evidence), §5.5 (the fixture rule) and §4 (P-1…P-4).

---

## 0. What was measured, where, and on which bytes

| | value |
|---|---|
| host | `saul.nersc.gov` (login34), over `ssh` |
| interpreter | `/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3`, **3.11.14**, after `source setup_salloc_env.sh` |
| `MNV_DATA_ROOT` / canonical checkout | `/pscratch/sd/j/josephrb/MINERvA-OmniFold` @ `b2d7d4ca`, **721** dirty entries |
| `MNV_CODE_ROOT` / clean tree | `/pscratch/sd/j/josephrb/k0r2/clean` @ `a902b781`, `git status --porcelain` = **0 lines**, both markers present |
| throwaway inputs | `$SCRATCH/k0r2/n1/{u,c}.root`, zero-byte files. **Never the defaults, which name real archive products.** |

**The clean tree was constituted without writing to the canonical checkout.** `git clone --bare
--local <canonical> bare.git` (reads the source, hardlinks objects), then this branch was pushed
into `bare.git` over ssh, then `git clone --local bare.git clean`. The canonical checkout's HEAD and
its 721-entry `git status --porcelain` were re-measured afterwards and are unchanged. No
`git worktree add` and no `git fetch` was run inside the canonical tree.

**A default-interpreter trap, recorded because it cost the first attempt.** On a bare login shell
`python3` is old enough that `from __future__ import annotations` is a `SyntaxError`, and the first
arm died at `mii_adopt_unified_5d_stamped.py:137` looking exactly like a source defect. It is the
environment. `source setup_salloc_env.sh` first, and never pipe that source.

---

## 1. §5.5 — U / U′: COUNTERFACTUAL ORIGIN EVIDENCE

**What this arm is, in ruling 20's words: it shows what *would* load without containment. It does
NOT establish the mechanism of the F-9 refusal.** Both halves must be said together. A later reader
who finds U′ naming `seed_offset_policy` beside an F-9 arm that does not will read a contradiction
unless the labels are on the artifacts, which they now are (§7.3).

Two arms of the **same real unmodified binary**, from the canonical checkout, no fixture, no copy,
no edit, and **no `--allow` anywhere**.

### Arm U — plain, unguarded

```
cd /pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding
python3 mii_adopt_unified_5d_stamped.py --uthrow $D/u.root --combined $D/c.root --out $D/witness_U/o.root
```

`rc=1`, and **it reached the O-1 marker** at log line 21:

```
[remedyA] running the PINNED writer as a subprocess: .../python3
  /pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/adopt_unified_5d.py --uthrow ... --out ...
```

The `rc=1` is the CHILD failing on the zero-byte throwaway `u.root` (`TFile::ReadBuffer`, then
`OSError: Failed to open file`), which is downstream of everything this arm is about.
`grep -c "\[adopt5d\]"` = **0**: the writer opened no output.

### Arm U′ — the same binary with the guard installed and `--expect-root` set to the tree it was launched from

This is the contract's "read it from an unguarded inventory run": the guard refuses nothing here,
and its record carries the resolved origin. **No `--allow`.**

```
  expect_root        /pscratch/sd/j/josephrb/MINERvA-OmniFold
  script_checkout    /pscratch/sd/j/josephrb/MINERvA-OmniFold
  checked            9
  repo_origin_count  1
  allow              []
  verdict            REPOSITORY-ORIGINS-INSPECTED
     ORIGIN seed_offset_policy -> /pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/seed_offset_policy.py
```

**The counterfactual is real and it is asserted on the loaded module's origin, not on an exit
code.** Run from the canonical checkout with containment not in play, real production code imports
the canonical checkout's `seed_offset_policy` and proceeds past the O-1 marker. Compare §3, where
the same module resolves under the code root instead.

**`--expect-root` here names the canonical checkout, and that is permitted.** `--expect-root` is not
`--allow`: it declares which tree the run is *expected* to be in, so pointing it at the tree the
binary was launched from is what makes this arm refuse nothing and record origins. `--allow` is
empty on **both** arms and is forbidden on every production arm.

**This arm must RETAIN and NAME `seed_offset_policy` (ruling 20).** It is the only place the module's
origin is on the record, and the F-9 arm cannot supply it — by construction, since B-4 refuses before
imports begin.

---

## 2. N-1 — the forbidden configuration is refused, and it is refused EARLIER than the contract predicted

```
python3 $CLEAN/nd-unfolding/mnv_guarded_run.py --expect-root $CLEAN \
  --inventory $D/inv/armN1.jsonl -- \
  /pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/mii_adopt_unified_5d_stamped.py \
  --uthrow $D/u.root --combined $D/c.root --out $D/witness_N1/o.root
```

**`rc=3`**, captured unpiped into a variable before anything read it (O-4). Full merged stream (O-3
— one stream, so the interleaving is real):

```
[oi136] SCRIPT OUTSIDE THE EXPECTED TREE -- REFUSING BEFORE THE FIRST IMPORT.
[oi136]   script        /pscratch/.../MINERvA-OmniFold/nd-unfolding/mii_adopt_unified_5d_stamped.py
[oi136]   which is in   /pscratch/sd/j/josephrb/MINERvA-OmniFold
[oi136]   expected      /pscratch/sd/j/josephrb/k0r2/clean
```

| ordering evidence | required by | result |
|---|---|---|
| O-1 monotone marker across two arms of the same binary | §5.4 | `[remedyA] running the PINNED writer` present in arm U, **absent** here |
| O-2 filesystem witness over a directory created empty | §5.4 | `witness_N1` listing `[]` before **and** after; `--out` fails `test -e`; `[adopt5d]` count **0** |
| O-3 single-stream log order | §5.4 | one merged stream; the banner is the only content |
| O-4 status captured unpiped | §5.4 | `RC=$?` immediately, before any `grep`/`wc` |

### F-9 WAS RESTATED BY JOSEPH RATHER THAN WORKED AROUND — ruling 20

**The finding, recorded because the resolution only makes sense beside it.** F-9 originally required
N-1 to "exit 3, **name `seed_offset_policy`**". It exits 3 and does not name it, because **B-4
script containment refuses strictly earlier than the import guard can fire** — the script lies in a
checkout that is not `--expect-root`, so the run is refused before the first import. That is the
same defect shape ruling 19 found in N-2, appearing in N-1: a control passing for the wrong reason.
It could not be repaired by reconfiguring the arm; the only alternatives were to disable B-4 on a
production arm or to change the criterion.

**Joseph's ruling 20, verbatim in the operative part:** *"Do not disable or exempt B-4. F-9 is
restated because its original import-specific expectation is incompatible with the earlier
script-containment protection."* The refusal now passes on the record below, and *"N-2 and N-3 remain
the import-resolution negative controls."*

**Measured at code root `de040d9b`, read off the record and not off the exit code:**

| clause | result |
|---|---|
| exits 3 through B-4 | `rc=3`, captured unpiped |
| `outcome` | `refused:script-outside-expect-root` |
| `refusal_site` | `b4-script-containment` — see §7.2; exit 3 alone cannot say which protection fired |
| verdict is never empty/green | `REFUSED -- THE SCRIPT ITSELF LIES IN A CHECKOUT THAT IS NOT --expect-root…` |
| names the script | `…/MINERvA-OmniFold/nd-unfolding/mii_adopt_unified_5d_stamped.py` |
| names the canonical root | `/pscratch/sd/j/josephrb/MINERvA-OmniFold` |
| names the expected clean root | `/pscratch/sd/j/josephrb/k0r2/clean` |
| `checked = 0` **as expected** | `checked=0`, `checked_provenance=not-measured-no-guard-was-installed`, `guard_installed=false` |
| `--allow` empty | `[]` |
| O-1…O-4, no child marker, no output | marker count 0, `[adopt5d]` count 0, witness `[]`, `--out` absent |

**`seed_offset_policy` appears 0 times in the record, and that is an OBSERVATION, not a
requirement.** Ruling 20 as refined: it is *neither required nor expected* to appear, because the
import guard is intentionally never reached. Its absence is a **consequence** of B-4 refusing first,
not a property imposed on the record — so nothing here scrubs the string, and what carries the claim
is the **triple** `guard_installed` / `checked_provenance` / `outcome`, never a missing substring.

## 3. The first guarded PRODUCTION arm — green, and NON-VACUOUS

The configuration the eight launchers now emit: script from the code root, cwd in the data root,
child guarded, both records required.

```
cd /pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding          # the DATA root
python3 $CLEAN/nd-unfolding/mnv_guarded_run.py --expect-root $CLEAN --inventory $D/invP/parent.jsonl -- \
  $CLEAN/nd-unfolding/mii_adopt_unified_5d_stamped.py --uthrow $D/u.root --combined $D/c.root \
  --out $D/witness_P/o.root --guard-expect-root $CLEAN --guard-inventory $D/invP/child.jsonl
```

| record | `checked` | `repo_origin_count` | verdict | origins |
|---|---|---|---|---|
| parent `mii_adopt_unified_5d_stamped.py` | **9** | **1** | `REPOSITORY-ORIGINS-INSPECTED` | `seed_offset_policy -> $CLEAN/nd-unfolding/seed_offset_policy.py` |
| child `adopt_unified_5d.py` | **213** | **0** | `EMPTY-REPOSITORY-ORIGIN-SET — THE GUARD REFUSED NOTHING BECAUSE IT SAW NOTHING` | — |

Three things this establishes and one it does not:

1. **The wrapper is non-vacuous on this path.** The contract's B-1 held that a wrapper "cannot help
   them and would block the run"; that was true of the pre-repair bytes. Post-repair the parent
   resolves `seed_offset_policy` from the **code root** — the same module that resolved from the
   **canonical checkout** in §1, same binary, two trees, two answers.
2. **`checked = 213` on the child is the point of P-3.** The child looked at 213 absolute origins
   and found no repository module among them. A bare exit 0 cannot distinguish that from a guard
   that never ran; the flagged empty record can, and does.
3. **M-1's empty import set for `adopt_unified_5d.py` is now MEASURED at runtime**, on the real
   pinned writer, rather than inferred by AST. The contract offered it as a prediction; it holds.
4. **It does NOT establish that guarding the child protects it from an import.** It cannot: the
   child makes no repository import. The child guard buys the flagged empty record and §H.1
   insurance, and nothing else. Do not report it as import protection.

`rc=1` on this arm is the child failing on the zero-byte throwaway `u.root`, as in §1.

## 4. A-2(f) and P-2/P-3/P-4 exercised end to end on the clean tree

```
[srcman] $CLEAN: 771 tracked source files, listing sha256
         4ab22f9326810f758796d9403320fe2a31243e46af9b5344e44c2fe6f902f6ae,
         HEAD a902b78120e2b28eba8eb53f3680f61afa286b7e, dirty 0            rc=0
[p4] wrote 2 pinned import set(s) from 2 inventory record(s)
[p4]   nd-unfolding/adopt_unified_5d.py: 0 module(s) []  [DECLARED EMPTY]
[p4]   nd-unfolding/mii_adopt_unified_5d_stamped.py: 1 module(s) ['seed_offset_policy']
[p4] 2 inventory record(s) over 2 entrypoint(s); source manifest IN USE
[p4] P-2, P-3 and P-4 HOLD for every inventory record read.                rc=0
```

The B-2 disclosure sentence is carried in the pins as the declared-empty entrypoint's `disclosure`
field, so it travels with the artifact instead of living only in prose.

**These pins are NOT the production pins.** They were written from a two-process arm with throwaway
inputs. The production pins must be written from the first clean k=0 run and reviewed then.

## 5. A defect in this package, found by running this arm rather than by a test

The first N-1 run recorded its own refusal as
`verdict = EMPTY-REPOSITORY-ORIGIN-SET — THE GUARD REFUSED NOTHING BECAUSE IT SAW NOTHING`. Both
clauses were false: the guard refused, and it saw nothing only because nothing ran. A B-4 refusal
raises no `ImportTreeViolation`, so the verdict fell through to the empty-green string — **the exact
conflation P-3 exists to prevent, reintroduced inside the field written to prevent it.** Fixed at
`a902b781`; the verdict is now derived from the outcome as well as the exception, a refusal outranks
emptiness, and both directions are pinned in `test_mnv_guarded_run.py`. The P-4 ratchet additionally
refuses any refusal record found in a production inventory set, checking `outcome` **and** `verdict`
because those two fields disagreed once already.

## 7. ROUND 3, 2026-08-22 — A-2(c)(d)(e)(g) applied and verified, and three guard defects

### 7.1 Write protection APPLIED and VERIFIED, on the real tree, three independent ways

Joseph: *"apply and verify write protection"* — not assert it. Measured on
`/pscratch/sd/j/josephrb/k0r2/clean` at `de040d9b`:

| step | result |
|---|---|
| POWER ARM, before applying | `rc=2`, `A-2(g): 814 tracked source path(s) still carry a write bit` |
| apply + verify, ONE command | `rc=0`, `applied A-2(g) write protection: 922 of 922 protected path(s) changed mode, plus 794 non-tracked writable file(s)` |
| re-verify as a SEPARATE observation | `rc=0` |
| filesystem witness, tracked source | `Permission denied`, mode `-r--r-----` |
| filesystem witness, new file in `nd-unfolding/` | create refused, mode `dr-xr-x---` |
| after a full guarded production arm | still clean **and** still protected, `rc=0`; **0** stray `.pyc` |

**"Writable" has two testable definitions and only one is enforced.** `mode_writable` — any write
bit on a tracked source, on any directory under the root, or on any non-tracked file — is ENFORCED,
because it is what `chmod -R a-w over the source` produces and it is a property of the TREE.
`uid_writable` — `os.access(W_OK)` for the asking process — is RECORDED but NOT enforced, because it
is a property of who is asking: false for a peer's unprotected tree, true for root regardless of any
bit. Enforcing the uid form alone would pass a tree any other account can rewrite mid-run, and the
hazard A-2(g) guards is mutation DURING the run. Neither form stops the owner from `chmod`-ing back
or stops root; this prevents ACCIDENTAL mutation and makes deliberate mutation leave a trace in
A-2(f). `.git` is excluded throughout — git must keep writing there, and a protection that breaks
the tools which verify it protects nothing.

### 7.2 Three defects in my own package, each found by running it rather than by a test

1. **The remedy string I shipped was wrong.** The A-2(g) refusal message told the reader to run
   `git ls-files -z | xargs -0 -n1 dirname | sort -zu | xargs -0 chmod a-w`. `dirname` emits
   NEWLINE-separated output into a `sort -z`, so the directory pass collapsed into one bogus
   argument and silently did nothing while the file pass succeeded. Visible only because apply and
   verify were two instruments and they disagreed. Replaced by `--apply-readonly` on the tool, which
   chmods exactly the set `--require-readonly` checks: one definition, so the protected set cannot
   drift from the verified set.
2. **`__pycache__` was outside the protected set.** After protection was applied and verified, a
   guarded production arm still wrote
   `nd-unfolding/__pycache__/seed_offset_policy.cpython-311.pyc` into a `drwxrwx---` directory, and
   `git status` stayed clean because `__pycache__/` is gitignored. Cause: the protected set was
   built by walking UP from tracked files, so a directory holding no tracked source was never in it.
   Both instruments that should have caught it are blind by construction — `--require-clean` because
   the path is gitignored, the A-2(f) manifest because it covers tracked `.py`/`.sh` only. **A local
   fixture could not have found this**; it took the real tree. Fixed in both directions: every
   directory under the root is protected, and non-tracked writable files are refused separately.
3. **`checked = 0` was a DEFAULT on the containment path.** See §7.3.

### 7.3 What ruling 20 changed in the guard, not in the rubric

Ruling 20 makes `checked = 0` the EXPECTED value for F-9 — which is exactly when a defaulted zero
passes unnoticed. `write_inventory` wrote `guard.checked if guard is not None else 0`, so the
containment path recorded a zero indistinguishable, on its own, from a guard that installed and
inspected nothing. Two new fields, both written unconditionally:

- **`checked_provenance`** — `measured-by-installed-guard` or `not-measured-no-guard-was-installed`.
  F-9 is read off the triple with `guard_installed` and `outcome`, never off `checked` alone.
- **`refusal_site`** — `b4-script-containment`, `import-tree-violation`, or null. **Every refusal
  returns the same exit 3**, which is precisely how B-4 took over F-9's exit 3 the day it landed
  with nothing in the artifact to show it. A test asserts the two refusals are indistinguishable by
  exit code and distinguishable by site.
- **`--label`** — so an artifact says which ARM produced it.

**The two arms are separated by the artifact, not by the reader:**

| field | N-1 (refused) | U′ (counterfactual) |
|---|---|---|
| `expect_root` | the clean tree | the canonical checkout |
| `outcome` | `refused:script-outside-expect-root` | `child-systemexit:…` |
| `refusal_site` | `b4-script-containment` | `null` |
| `checked_provenance` | `not-measured-no-guard-was-installed` | `measured-by-installed-guard` |
| `checked` / `repo_origin_count` | 0 / 0 | 9 / 1 |
| `seed_offset_policy` | absent — a consequence of B-4 | **NAMED**, origin under the canonical checkout |
| `allow` | `[]` | `[]` |

### 7.4 The rule that would have caught B-4 invalidating F-9, made executable

*"Any check added ahead of an existing one requires re-deriving every downstream control."* That is a
memory exercise unless something enumerates the sites and demands a control for each.
`EveryRefusalSiteHasAControlThatNamesItsOutcome` enumerates every `refused:` / `cannot-check:` /
`child-` outcome string **from the source** and requires each to be named by a control in the test
corpus, with a power arm so an empty enumeration cannot pass forever. **It went red on its first run**
and named three uncontrolled `cannot-check:` outcomes; those arms now assert their `outcome`.

## 6. What this receipt does not cover

- No leg of the k=0 path was run. The entrypoints exercised here are the adopter pair only.
- Nothing was measured under `sbatch`. `BASH_SOURCE`-under-spool remains ruling 14's business.
- M-1…M-6 are **not** re-measured here beyond the two facts above; F-17 is still open.
- **The A-2(g) protection is applied to the k0r2 scratch clean tree, not to whatever tree the real
  submission uses.** It must be applied and verified again on that tree, and re-verified after the
  last leg. `--undo-readonly` is how the tree is refreshed; a protection nobody can lift is one
  people work around.
- The canonical checkout's 721 untracked entries are the most perishable statement in §0 and must be
  re-measured at submission time, and again after the path runs.

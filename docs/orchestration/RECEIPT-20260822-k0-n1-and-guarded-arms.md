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

## 1. §5.5 — the fixture rule: the hijack is genuine, asserted on the module's origin

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

**The hijack is real and it is asserted on the loaded module's origin, not on an exit code.** Run
from the canonical checkout, real production code imports the canonical checkout's
`seed_offset_policy`, and the process proceeds past the O-1 marker. Compare §3, where the same
module resolves elsewhere.

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

### F-9 IS NOT SATISFIABLE AS WRITTEN, AND THAT IS THIS PACKAGE'S OWN DOING

F-9 requires N-1 to "exit 3, **name `seed_offset_policy`**". It exits 3 and it does **not** name
`seed_offset_policy`, because **B-4 script containment refuses strictly earlier than the import
guard can fire**. The script lies in a checkout that is not `--expect-root`, so the run is refused
before the first import — `checked = 0`.

**This is the same defect shape ruling 19 found in N-2, now appearing in N-1**: a control that
passes for the wrong reason. Ruling 19 rejected N-2 because "a copied writer placed outside
`MNV_CODE_ROOT` would be refused by the contract's own planned script-containment rule BEFORE its
injected import ever executes". N-1 places the *real* writer outside `MNV_CODE_ROOT`, so it meets
exactly that description. **The verifier's round-2 prediction that this arm "already refuses on
`seed_offset_policy`" was measured against pre-B-4 behaviour and is now wrong.**

**It cannot be repaired by re-configuring the arm.** For the import half to fire on this file, the
script must be in the canonical checkout while `--expect-root` names another tree — which is
precisely the configuration B-4 refuses first. The only ways to see the import refusal on *this*
file are to disable B-4 on a production arm, which is not something this lane will do, or to accept
the substitute evidence below. **This is Joseph's and the reviewer's to rule on, not the builder's.**

Substitute evidence that the import half is armed, both on real repository modules:

- `nd-unfolding/tests/test_n2_child_boundary.py` — a fixture writer INSIDE the expected checkout (so
  B-4 passes) importing the **real** `seed_offset_policy` from a **second real checkout**: `rc=3`,
  banner names `seed_offset_policy`, witness directory empty, refusal before the O-1 marker.
- `nd-unfolding/tests/test_n3_rooted_import_repair.py` — the pre-repair bytes of all six repaired
  files, both directions, asserted on `__file__`.

---

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

## 6. What this receipt does not cover

- No leg of the k=0 path was run. The entrypoints exercised here are the adopter pair only.
- Nothing was measured under `sbatch`. `BASH_SOURCE`-under-spool remains ruling 14's business.
- M-1…M-6 are **not** re-measured here beyond the two facts above; F-17 is still open.
- The canonical checkout's 721 untracked entries are the most perishable statement in §0 and must be
  re-measured at submission time, and again after the path runs.

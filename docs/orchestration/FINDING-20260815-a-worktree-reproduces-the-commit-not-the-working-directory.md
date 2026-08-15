# A worktree reproduces the commit, not the working directory

**Date:** 2026-08-15 · **Lane:** OI-124 disposition lane (peer session `C`) · **Row:** `BEN-332`
**Trigger:** an instruction to regenerate `docs/orchestration/MANIFEST.tsv` from a `git worktree`,
whose reasoning was correct and whose conclusion was the one place the script must not be run.

---

## The instruction, and why it was right

Regenerating a repo-wide generated file while another lane holds uncommitted tracked files bakes that
lane's in-flight state into your commit. That is a real hazard, it is why
`CONVENTION-lane-worktrees.md` exists, and the reasoning transfers to almost every generator in this
repo. The instruction to run it from an isolated worktree followed from it correctly.

## What it missed

`generate_manifest.py` does not read the git index. It `os.walk`s `docs/orchestration` and, by its own
docstring, **inventories gitignored artifacts** alongside tracked ones — `__pycache__/*.pyc`,
`.DS_Store`, `.pytest_cache/*`, `runs/*.log`, `state/locks/*.lock`.

A fresh worktree has none of those. So regenerating at the **same commit** in a clean worktree does not
reproduce the manifest — it produces a manifest missing every ignored artifact.

**Measured, at commit `519e918`, both runs identical except for the directory:**

| where | generator's own summary | diff vs committed |
|---|---|---|
| clean `git worktree` | `rows=768 tracking=tracked:768` | **40 rows DELETED**, 49+/64− |
| main checkout | `rows=813 tracking=ignored:45,tracked:768` | **0 rows deleted**, 57+/27− |

All 40 "removed" paths were then verified **present in the main checkout** and
**`git check-ignore`-positive** — 40/40 on both counts. The worktree was not detecting drift. It was
**causing** it, and committing that output would have been a 40-row deletion under a narrow message.

> **A worktree reproduces the COMMIT. It does not reproduce the WORKING DIRECTORY.** Any generator that
> walks the filesystem rather than the index sees the difference. Before isolating one in a worktree,
> ask what it reads that a worktree does not have.

## What actually bounds the main-checkout run

Narrower than the instruction assumed, and checkable in one command: the generator reads **only
`docs/orchestration`**. Other lanes' uncommitted files elsewhere in the tree — `VALIDATION_LEDGER.md`,
`nd-unfolding/pet/*.sh`, the run logs — cannot reach it. The exposure is exactly

    git status --short -- docs/orchestration

which was verified empty immediately before the run. **The safe-condition is a subdirectory being
clean, not the tree being clean** — and the isolation mechanism was reached for because nobody had
established which of the two it was.

## The underlying defect: a tracked file that is a function of untracked local caches

The committed `MANIFEST.tsv` carries **45 rows describing one machine's transient state**. That makes
`generate_manifest.py --check`, which "exits nonzero when MANIFEST.tsv differs from generated output",
**unable to be green on two machines at once**. A checkout that has never run `pytest` disagrees with
one that has; a checkout on Linux disagrees with one that has `.DS_Store`; `cpython-312` and
`cpython-314` rows disagree with any machine running neither.

**Second-order, and the reason this is not cosmetic.** Running `BEN-330`'s own test suite created five
new `.pyc` files, all five of which are now rows in this commit. **An agent's act of verification
mutated a tracked artifact.** `--check` cannot distinguish that from real staleness — so a `--check`
gate here would fail closed on every machine that has ever run the tests, and would then be switched
off. That is `BEN-228`'s measured pattern (a gate that punishes the convention gets disabled), arrived
at from a different direction.

## Not fixed, deliberately

Excluding ignored artifacts means changing another lane's script and removing 45 existing rows. This
lane was asked for a **regeneration, not a redesign**, and a 45-row deletion is not a thing to do as a
side effect of someone else's errand.

The regeneration was committed **as generated**. Hand-editing generated output so the diff looks
tidier is strictly worse than a manifest that says what the generator actually produced.

**Cheap fix if anyone takes it:** skip `git check-ignore`-positive paths in the walk, or record them in
a sidecar that `--check` does not compare. Either makes `--check` a gate that can be armed.

## The ordering trap this exposed, which has no clean solution

`CLAUDE.md` requires a change's ledger row to land in the same commit as the change. But
`MANIFEST.tsv` records `FINDINGS.md`'s line count — so **the manifest cannot be simultaneously current
with the ledger entry that documents it**. Writing `BEN-332` after the regeneration left the manifest
one line behind (`462` recorded, `463` actual); regenerating again to catch it would have inventoried
lane B's uncommitted `state/RECEIPT-20260815-cstat-tail-geometry-and-weighting-correction.json`, which
appeared in `docs/orchestration` mid-task — the exact hazard the worktree instruction existed to
prevent.

**A one-line staleness in a generated file was taken as the cheaper of the two**, verified absent
(`grep -c` → 0 for B's path) and stated in the commit body rather than hidden. `MANIFEST.tsv` also
records **its own** line count, so it is structurally one step behind itself regardless; that is
pre-existing and not introduced here.

## Scope

* One script, `generate_manifest.py`. Whether other generators in this repo walk the filesystem rather
  than the index was **not** surveyed — the transferable claim is the question to ask, not a count of
  affected scripts.
* The 40/40 present-and-ignored verification was done on **this machine's** main checkout. A different
  machine has a different 45.

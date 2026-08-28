# FINDING 2026-08-28 — provenance of the `OI-136` import guard

Governing row: `docs/OPEN_ITEMS.md` `OI-136`. Code: `nd-unfolding/mnv_guarded_run.py`.

This holds the dated record that `mnv_guarded_run.py`'s module docstring used to carry: the incident
that caused the guard, the rules that were tried and rejected, and the order the two receipts were
built in. The docstring keeps what a reader must know to use the wrapper correctly and points here
for the rest. Nothing in it is a contract; deleting the docstring's *cause* sentences would change
what a maintainer knows, deleting these paragraphs would not.

## The incident that caused it

Run `57266000_0` (2026-08-19/20, 3 h 08 m of A100) printed
`deployment parity CURRENT for all pinned executing copies` and `5 of 5 CURRENT` against the frozen
tree `gate5-data-only-frozen-377c713`, then failed on a guard that the frozen tree's
`cstat_data_only.py` **cannot raise**: its `DATA_ONLY_WITHHELD_REQUIRED_KEYS` is empty. The message
it actually printed carries the suffix ``; the seed lives under `data_bootstrap_seed` (P6)``, which
exists only in the pre-fix blob at `1f6aa9c6^`. The import had resolved to the hardcoded main
checkout, 211 commits behind.

That run is why the guard exists, and it is also the measurement behind the docstring's statement
that the parity check and this guard answer different questions. The parity check passed honestly,
five for five, while the interpreter was loading another tree.

## Rules that were tried and rejected

**`AGENTS.md` as the checkout marker.** It was the obvious choice and it is wrong. `AGENTS.md` was
rewritten as the thin front door on 2026-08-20, so a tree frozen on 2026-08-18 is still a real
checkout that a fresh marker would fail to recognise, and the guard would wave it through. The
surviving rule — markers must predate every frozen tree on scratch — is in the docstring; this is the
attempt that produced it.

**Editing the 59 fail-open files instead of adding a wrapper.** Deriving the root from `__file__` in
each of the 59 is the correct end state. It was not done here because those are hash-pinned science
files inside frozen provenance, so a 59-file sweep needs its own per-site authorization and would be
a larger change than the incident it repairs. The difference `OI-136` records between itself and
`OI-123` is direction: `OI-123` dies at exit 3 before any GPU work, while this family runs to
completion and produces numbers.

**A file-based inventory receipt.** Rejected in favour of stderr: a file would need a path, a flag, a
default and a failure mode for an unwritable directory, and would make the receipt absent exactly
where nobody passed the flag. The surviving rule — stderr, because consumers parse the child's
stdout — is in the docstring.

## Build order of the two receipts

The stderr `[oi136-inv]` walk of `sys.modules` and the `--inventory` json record were developed on
two lines in parallel and merged 2026-08-26. Neither replaces the other and both are emitted from the
same `finally`; that fact is in the docstring, this is only the order it happened in.

## Behaviour added after the first version

Both were added 2026-08-22 and are stated positively in the docstring. What is recorded here is what
the wrapper did *before* them, which is the part no longer true of any current code path.

- **B-4, script-tree refusal.** Until then the file checked only what was *imported*, never what was
  *run*. For an entrypoint with repository imports that failed closed by accident at the first
  import; for one with none it did not fail at all, and running the forbidden checkout's own copy of
  such an entrypoint with `--expect-root <clean tree>` exited 0.
- **P-1, resolved-origin inventory.** Before it, `checked` was incremented and read nowhere, so a
  production run emitted nothing that could distinguish "checked many imports, all clean" from
  "checked nothing", and an exit 0 was not evidence.

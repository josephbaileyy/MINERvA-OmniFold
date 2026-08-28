# FINDING 2026-08-28 — 101 of 122 source BEN citations resolve only at the evidence tag, and nothing checked any of them

**Filed while auditing the tree against a vendored external code-polishing standard**
(`.agents/skills/code-polishing/SKILL.md`), whose Category 2 orders issue references stripped from
source. The carve-out written against it (`.agents/skills/README.md`, Carve-out 3) argues that
`BEN-*` is exempt because it *resolves in-repo*. That claim was asserted before it was measured. This
finding is the measurement, and it is narrower than the claim.

**Nothing is stranded today.** The remedy here pins a green invariant rather than repairing a red one.
That is deliberate and is the only reason it can be wired at all: `.githooks/pre-commit`'s admitting
rule requires that a committer who did nothing wrong can always make a check pass, and a check first
written when it is already red is parked forever — the state `check_canonical_designation.py` has been
in since 2026-08-13.

## Half 1 — the claim was true, but for a reason the claim did not name

Measured 2026-08-28 on a clean tree:

| quantity | value |
|---|---|
| distinct `BEN-\d{3}` cited in tracked `*.py` / `*.sh` outside `docs/`, plus `.githooks/*` | 122 |
| files in that scope | 696 |
| registry rows in `FINDINGS.md`, working tree | 48 |
| registry rows in `FINDINGS.md` at `evidence/prepublication-2026-08-20-0b329e8a` | 391 |
| union | 398 |
| cited ids with **no** row in either | **0** |
| cited ids resolving **only** at the tag | **101** |

A first pass over the working tree alone found 22 apparently unregistered ids and was **wrong**: it
measured against `KNOWN_ISSUES.md`, `VALIDATION_LEDGER.md` and `docs/OPEN_ITEMS.md`, none of which is
the registry. `FINDINGS.md` is, and its own header says where the rest of it went. The error is worth
recording because it is the reader's error, not the tree's: an auditor who does not open the header
concludes the pointers are broken. That is the same failure a stranded citation causes, arrived at by
a different route.

## Half 2 — the asymmetry, which is the actual finding

83 percent of source citations resolve only while `evidence/prepublication-2026-08-20-0b329e8a` is
fetched and intact. Twenty-one resolve from the working tree; seven working-tree rows postdate the
freeze and have no counterpart at the tag.

The 2026-08-20 prepublication freeze pruned `FINDINGS.md` from 391 BEN rows to the handful the active
playbook uses. **That prune is exactly the event that strands a citation, and it ran with no check
over any citing file.** It happened not to strand one. Nothing about the procedure made that outcome
more likely than the other one.

The failure mode is silent in the direction that matters. A `--no-tags` or shallow clone, a deleted or
moved tag, or a re-freeze under a new tag name converts 101 working pointers into dead ends with no
diagnostic anywhere — the reader simply finds nothing and moves on. And a pointer that *might* be dead
is worse than no pointer: the next author who cannot cash one out inlines the whole argument instead,
which is a plausible part of why `.githooks/pre-commit` carries roughly 210 lines of header before its
first line of executable dispatch.

## Remedy

[`verify_ben_citations.py`](verify_ben_citations.py). Three-sided per BEN-162's form set: a cited id
with no registry row fails; zero citations or zero registry rows is CANNOT CHECK, never a pass; a
waiver that is no longer needed fails. The tag name is parsed out of `FINDINGS.md`'s own header rather
than restated, because a hardcoded tag here would be BEN-163 inside the instrument — retag the freeze
and the file still names the old one, correct-looking and wrong. The TAG-ONLY count prints on every
run, so the asymmetry above stays visible instead of being rediscovered.

`--self-test` power-tests fourteen cases in both directions, including a stranded citation, a waived
strand, and both stale-waiver arms, via injected citation sets so that no bad citation is planted in
the tree to exercise them.

An unresolvable tag exits 2 (CANNOT CHECK) and prints `git fetch origin --tags`, so the abnormal state
is loud and the committer is told the one-line fix rather than being blocked by it.

**Wiring, not yet done, and Joseph's call:** two `run` lines in `.githooks/pre-commit` following the
`whose_row self-test` precedent already there —

```
run "BEN citations resolve"        python3 docs/orchestration/verify_ben_citations.py
run "BEN-citation self-test"       python3 docs/orchestration/verify_ben_citations.py --self-test
```

`generate_manifest.py` must be re-run so this file and the script carry manifest rows before either is
quoted as evidence.

## What this does not close

- **Existence, not agreement.** A row that exists but says something other than what the citing comment
  claims passes here. No mechanism closes that; it is what review is for.
- **`docs/` is out of scope on purpose.** Receipts and verdicts cite ids by the hundred and are the
  auditor's own layer; including them would make this a whole-corpus link checker whose failures are
  mostly not about source.
- **The dependency itself is unchanged.** The check makes the 101 visible and makes their loss loud. It
  does not reduce the number. Reducing it means restoring rows to the working tree, which is a freeze
  decision and not a lint's to make.

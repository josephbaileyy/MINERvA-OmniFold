# Vendored skills

Source: `https://github.com/AlkaidCheng/grimoire`, commit `b97aad5be82b10720f397b3eeb2dc7ea68ea9804`
(recorded in `.upstream-sha`). MIT, upstream license copied to `LICENSE.grimoire`.
Vendored 2026-08-28. `cpp-code-review` and `annotated-diff-html` were not taken: no C++ in the tree,
and diff-rendering is already covered by the receipt/manifest machinery.

| Skill | What it governs | Where it fires here |
|---|---|---|
| `code-polishing` | Language-agnostic structural cleanup: iteration artifacts, dead code, stale docs, encapsulation, naming | Analysis scripts under `nd-unfolding/`, `2d-unfolding/`, `3d-unfolding/`, `omnifold_nn/` |
| `python-code-review` | PEP 8, naming, type hints, NumPy docstrings, performance, safety | Same, plus new code as it is written |
| `code-delivery` | Branch names, commit messages, PR text, delivery mechanics | Subordinate to `AGENTS.md` and `.githooks/`; see Precedence |
| `software-design` | Decomposition, interfaces, coupling, whether to refactor first | New modules and consolidations |
| `session-handoff` | Cold-start handoff documents | Subordinate to the evidence routes in `AGENTS.md`; see Carve-out 7 |
| `_shared/` | Cross-skill reference files the above link to | Not a skill; no `SKILL.md` |

## Loading

`.agents/` is tracked; `.claude/` is ignored (`.gitignore:87`), so an agent that discovers skills under
`.claude/skills/` will not see these. Per clone, link them:

```bash
mkdir -p .claude && ln -sfn ../.agents/skills .claude/skills
```

The link is local-only, like `core.hooksPath` and `.git-blame-ignore-revs`: it must be made per clone
and nothing in the tree depends on it existing.

## Precedence

`AGENTS.md` > `.githooks/` > these skills. The skills are general engineering standards written for any
repository; they carry no knowledge of evidence tags, receipts, the ledger, or the freeze discipline.
Where a skill and a routed canonical artifact disagree, the artifact wins and the disagreement is a
carve-out below rather than a judgement call at the point of use.

## Carve-outs

These are the places where following the upstream text literally would destroy something this repository
built on purpose. Each names the upstream rule, why it does not transfer, and what to do instead.

### 1. "Treat removed code as if it never existed" does not apply to the orchestration tree

`code-polishing` Category 1 rules that once an API or default is removed, nothing in the source may be
organized around its absence, and that the removal narrative lives only in the commit, the changelog,
and the PR.

That rule assumes the removal narrative is recoverable from those three places. Here it frequently is
not, and the repository is explicit about why: `KNOWN_ISSUES.md` carries a section titled "Resolved traps
that WILL bite again if forgotten", and `.githooks/pre-commit` and `.githooks/commit-msg` open with long
headers recording exactly which wrong rule was tried, which incident it caused, and why the current rule
replaced it. `commit-msg` exists because two commits landed with nine checks silently skipped; deleting
its "WHY THIS EXISTS" header as edit-history narration would delete the only durable record of that.

Apply Category 1 to the analysis and plotting code. Do not apply it to `.githooks/`, `AGENTS.md`,
`KNOWN_ISSUES.md`, `VALIDATION_LEDGER.md`, `docs/orchestration/`, or to any header whose subject is a
control that exists because a specific failure occurred.

### 2. History-defensive tests are load-bearing here

`code-polishing` calls a test asserting an absence (`not hasattr`, a `raises` on a deleted option, a
sweep proving formerly-reserved names are ordinary now) an artifact a fresh author would never write,
and says to delete it.

In `nd-unfolding/tests/` those tests are the regression surface for quarantined traps: `AGENTS.md`
carries a "Quarantined and superseded traps" section, and the tests that pin a trap as gone are what
keep it gone. `test_p4_guard_mutations.py` reconstructs a superseded gate specifically to demonstrate it
accepted anything; that is a mutation test, not a relic.

Do not delete an absence test. If one is genuinely stale, it is retired through the ledger like any other
finding, not through a `[polish]` commit.

### 3. `BEN-*`, `OI-*`, `VL-*` and `Gate-N` are in-repo references, not PR numbers

`code-polishing` Category 2 removes issue and PR references from source because "see PR #142" is opaque
to a reader in five years.

The identifiers used here are not opaque. `BEN-*` resolves to a row in
`docs/orchestration/FINDINGS.md`: 48 rows in the working tree and 391 more at the evidence tag that
file's own header names, which together cover all 122 ids cited in source (measured 2026-08-28,
`verify_ben_citations.py`). `OI-*` resolves in `docs/OPEN_ITEMS.md` and ledger ids in
`VALIDATION_LEDGER.md`, both linted by the pre-commit run list. They pass the skill's own new-teammate
test, with one caveat recorded in
`docs/orchestration/FINDING-20260828-ben-citations-resolve-only-at-the-evidence-tag.md`: 101 of the 122
resolve only while that tag is fetched, so the test is passed by the repository plus one ref, not by
the working tree alone.

Note that `KNOWN_ISSUES.md`, `VALIDATION_LEDGER.md` and `docs/OPEN_ITEMS.md` are **not** the `BEN-*`
registry, though each cites ids freely. Measuring resolution against them reports false strandings.

Category 2 still applies to anything that resolves only outside the tree: a GitHub issue number, a
reviewer's name, a Slack or thread reference, an agent session id.

### 4. Provenance snapshots are evidence, not dead code

A file that looks like a pre-change copy may be a hash-bound producer.
`docs/orchestration/state/producers-oi126-r5/c_perm_ensemble.PRE-5MEMBER.py` is registered in
`docs/orchestration/MANIFEST.tsv`, described in that directory's `INDEX.json`, and its sha256 is the
`run_provenance.producer_sha256` of a receipt. `unbinned_unfolding/python/omnifold_old.py` is un-ignored
by name in `.gitignore:76` and documented in `README.md` as a pre-edit snapshot kept for diff.

Before proposing any file removal, check `MANIFEST.tsv`, the enclosing `INDEX.json`, and `.gitignore` for
an explicit un-ignore. A path that appears in any of the three is not a polishing target.

**Removal is not the only edit that destroys a binding, and this rule was learned the expensive way.**
Before editing ANY tracked file, check whether its sha256 is pinned:

```bash
git grep -qF "$(shasum -a 256 <path> | cut -d' ' -f1)" -- . && echo PINNED
```

A pinned file may not be touched at all — not to delete an unused import, not to drop a dead `f`
prefix, not to add `__all__`. Its recorded hash is the claim that *these exact bytes ran*, and any
edit makes that claim false. 292 tracked files are pinned, 80 of them `.py`.

The 2026-08-28 pass checked this carve-out as written, edited only files it was not removing, and
voided twelve bindings across seven receipts, four `sbatch` `CODE_SHA` guards and a Gate-6 launcher
that would have died at its own hash check. Eight were caught by `verify_hash_bindings.py`; the other
four were invisible to it, because 1,951 receipt hash keys carry a role name with no sibling path key
and so resolve to no file (`BEN-312`). Do not rely on the checker alone — take the hash of the file
you are about to edit and grep for it.

### 5. `code-delivery` does not own the commit object here

`.githooks/commit-msg` writes the `Checks: N passed` trailer and `AGENTS.md` sets what makes a result
live (evidence plus ledger, RUN_LOG and STATUS records in a commit). Take from `code-delivery` its
prose-level conventions: imperative subject, no assistant co-author trailer, no process leaks in
human-facing text, file list when more than two files change. Do not take its branch, gate, or
merge-mechanics guidance over `AGENTS.md`, and do not let a `[polish]` subject prefix displace the
scope prefix a commit would otherwise carry.

The `code-polishing` rule that audit work is read-only and runs in an isolated worktree already matches
`AGENTS.md`; that one transfers unchanged.

### 6. The verification gate is the hook list, not a test suite

`code-polishing` says to run the full test suite, lint, and type-check after every commit. There is no
lint, formatter, or type-checker configured in this tree, and `nd-unfolding/tests/` is not a fast
whole-repo suite.

The available gate is `git config core.hooksPath .githooks` plus the twelve checks in
`.githooks/pre-commit`, and the `Checks:` trailer is the durable evidence they ran. For a change scoped
to analysis code, add `python3 -m pytest nd-unfolding/tests/ -k <area>` and say in the commit body what
was actually run. Do not write "the suite passes" when what ran was the hook list.

Adopting a formatter or a ruff config across 483 tracked Python files is itself a change with blast
radius, and would need `.git-blame-ignore-revs` maintenance; it is not a `[polish]` commit.

### 7. A handoff routes; it does not restate

`session-handoff` assumes the repository has no standing orientation document. This one does:
`AGENTS.md` is the front door and `CLAUDE.md` the bootstrap, and both warn that generated state is a
view rather than evidence. A handoff written here points at the routed artifact and records what was
measured and where the evidence landed. It does not paraphrase `AGENTS.md`, and it does not copy a
volatile field a reader is required to re-measure.

The skill's core discipline, reference only durable state and never the session filesystem, transfers
unchanged and is worth more here than usual: a committed probe script under
`docs/orchestration/state/` still points at an agent session scratchpad that no longer exists, which is
the exact failure the skill names.

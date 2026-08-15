# `git add` succeeded and staged nothing — and the check built for that stayed green

**Filed** 2026-08-14 · **BEN-260** · repair lane · episode `EP-2026-08-14-receipt-artifacts`

Every number below comes from a command run in the repair turn, at `701b6c9` on `main`.

## 1. The reported state and the measured state

`701b6c9` ("Precondition 3 MET") was reported by its author as committing verbatim stdout for four
scripts as `*_n50.out`. Measured:

```
$ git ls-files | grep -c '_n50.out'
0
```

`git show --stat 701b6c9` lists **7 files, none of them a `.out`**. The cause is `.gitignore:13`
(`*.out`). `git add` on an ignored path **exits 0 and stages nothing**; without `-f` there is no
warning on the happy path, so the author's belief was consistent with everything they saw.

## 2. The gap was wider than reported

The scope handed to this lane was the four `*_n50.out`. The receipt that cites them —
`state/gate5-cstat-spec-measurements-20260814.json`, `evidence` block — names **nine** `.out` files,
and the five non-`n50` siblings (`centring.out`, `flicker.out`, `measure_bins.out`,
`measure_family.out`, `spread_and_nominal.out`) were dropped by the **same** `.gitignore:13` at an
earlier commit and had been missing longer:

```
$ git ls-files docs/orchestration/state/gate5-cstat-spec-measurements-20260814/
... 7 rows, all *.py, no *.out
```

One `git add -f` fixes nine citations or four. Repairing four would have left five identically-broken
citations behind a commit message saying the receipt's provenance was restored.

## 3. Recovery, and why it is recovery rather than regeneration

The brief's expectation was that the files were produced on a cluster worktree and were probably
unrecoverable. **They were recoverable**, and not from the cluster: `.claude/worktrees/lane-c` is a
local `git worktree` sitting at the same sha as `main` (`701b6c9`), and the author's working copies
were still there, ignored (`git status --porcelain --ignored` shows all nine as `!!`).

The distinction that makes this provenance and not fabrication is that the receipt records a `sha256`
per file, so recovery is **checkable rather than asserted**. All nine staged blobs match:

```
$ for f in $DST/*.out; do git cat-file blob :"$f" | shasum -a 256; done
```

| file | receipt `sha256` (first 12) | staged blob | bytes |
|---|---|---|---|
| `centring.out` | `fb4dec3a1abd` | match | 797 |
| `centring_n50.out` | `eb87a6447ddb` | match | 797 |
| `flicker.out` | `d573af6a5962` | match | 1216 |
| `flicker_n50.out` | `d39ac1e223dc` | match | 1278 |
| `measure_bins.out` | `2c20cefdf0bf` | match | 3625 |
| `measure_family.out` | `afc53b84f204` | match | 1710 |
| `measure_family_n50.out` | `d2a019cab4c6` | match | 1854 |
| `spread_and_nominal.out` | `f82bc6154b07` | match | 3997 |
| `spread_and_nominal_n50.out` | `e3969cdcb6e2` | match | 5869 |

`MANIFEST.tsv`'s independently-generated `lines`/`bytes` columns for these nine rows also match the
recovered files. Two independent records agree, so the amend-the-receipt-to-admit-a-gap branch of the
brief was **not** taken: there is no gap to admit.

**Generalisable:** a receipt that ships a per-file digest converts "is this the artifact?" from a
judgement call into a command. Ship the digest — it is what made a 20-minute recovery legitimate
instead of a plausible-looking reconstruction. (`CONVENTION-receipt-ingredients.md`, `BEN-077`.)

## 4. The check that exists for this class, and why it was green

`docs/orchestration/verify_receipt_artifacts.py` (added `a5f8506`) exists to fail when a receipt names
an artifact git is not carrying. On the tree carrying nine such artifacts it reported:

```
RECEIPT-ARTIFACTS :: 203 receipts scanned at working tree, 3 deliverable-area artifact path(s), 0 missing
EXIT=0
```

**Two independent reasons, both measured, and this matters because fixing either one alone is not
enough:**

1. **`.out` is not in `EXT` (`:39`).** The tuple is `.npz/.npy/.h5/.hdf5/.root/.pkl/.parquet`, so the
   paths are never extracted.
2. **The receipt cites bare filenames.** `evidence` keys are `"centring_n50.out"`, with no directory
   component, while `named_artifacts()` (`:66`) keeps a path only if it `startswith("docs/orchestration/state/")`.
   Probed directly: `named_artifacts(<the receipt's text>)` returns `[]`. **So adding `.out` to `EXT`
   would still not catch this receipt.**

A third face of the same narrowness explains the script's own `--historical` output, which self-reports
case 2 (`849b70f^`) as *does NOT fire*. Cause, measured rather than assumed: the needle
`LANED_CSTAT_CROSSCHECK.npz` is named by
`docs/orchestration/METHOD-DECLARATION-20260814-lane-d-cstat-crosscheck.md`, and `scan()` (`:77`,`:83`)
reads only `state/*.json` —
`git grep -l 'LANED_CSTAT_CROSSCHECK' 849b70f -- 'docs/orchestration/state/*.json'` returns nothing at
that rev **or** at `849b70f` itself.

**This is not a wrong check.** Its docstring (`:19-23`) argues the narrow scope from measurement: of
351 artifact-like paths named across those receipts, 349 point at cluster or scratch products that are
not supposed to be in git, so widening the rule fires on all 349 and gets turned off within a day. The
defect is not the scope; it is that **the name and the hook line invite an inference the scope does not
support.** Recorded as `KNOWN_ISSUES` **48** and deliberately left unpatched — widening someone else's
check so that it catches my case is a scope decision for its owner, and per `.githooks/pre-commit:43`
making a check pass by editing its input is worse than not having the check. The inverse holds too:
making a check *cover* your case by editing its scope in the turn you needed coverage is how a
measured trade-off gets silently reversed.

## 5. The dispatcher gap (Task 2)

`verify_receipt_artifacts.py` was in **neither** the run list nor the declined list of
`.githooks/pre-commit` — the third instance of the exact silence that dispatcher's own header
paragraph (`:51-56`) was written about, after `verify_hash_bindings.py` and
`check_canonical_designation.py` (`BEN-244`). It measured **exit 0 on a clean tree**, with its positive
control firing, so it clears the admitting rule at `:11` (*a check belongs here iff a committer who did
nothing wrong can always make it pass*) on the same grounds as `verify_hash_bindings.py`: a whole-tree
invariant, unscoped on purpose. Wired as **check 7**; `6 checks passed` → `7 checks passed`.

Because `run()` discards a passing check's output (`BEN-226`), a hook has only two channels — silence
and failure — so the coverage gap could not be wired as a warning. It is stated at the call site
instead, and in the header, precisely so that a future lane reading `7 checks passed` does not conclude
that a receipt's `.out` evidence is tracked.

**The canonical-designation block's unlock trigger says "move this to the run list as check 7"; that
slot is now taken, so its unlock makes it check 8.** Its decision was left untouched (OI-81, another
lane's).

## 6. What this cost and what generalises

- **`git add`'s exit code is not evidence that anything was staged.** Verify against `git ls-files`.
  This is `BEN-251`'s family (*an operation that reports nothing has told you nothing*) reaching `add`
  after `push` and `scontrol update`. Three tools, three evenings, one shape.
- **A check's name is not its contract.** `verify_receipt_artifacts` sounds total and is deliberately
  narrow. Before relying on a green check to license a claim, read what it extracts — one probe of
  `named_artifacts()` settled in seconds what the name implied for hours.
- **The unrecoverability of an artifact is a measurement, not an inference from where it was produced.**
  The brief and this lane both initially assumed a cluster origin; four `find` and `git worktree list`
  invocations found the content locally, hash-identical.
- **The long-form rule caught this document's own row.** `BEN-260` was first filed as a 1902 B table
  row with no pointer; `findings_row_lint.py --longform` failed the commit and this file exists because
  of it — a check admitted to the dispatcher firing on the lane that was wiring a different check into
  the same dispatcher.

## Cross-references

- `KNOWN_ISSUES` **48** — the checker's coverage gap, OPEN, owner's call.
- `BEN-251` — absence of an error is not a result (`git push`, `scontrol update`).
- `BEN-244` — the check that was in neither list; this dispatcher's prior instance.
- `BEN-226` — `run()` discards passing output, so "wire it but only warn" does not exist here.
- `BEN-077` / `CONVENTION-receipt-ingredients.md` — the per-file digests that made recovery checkable.

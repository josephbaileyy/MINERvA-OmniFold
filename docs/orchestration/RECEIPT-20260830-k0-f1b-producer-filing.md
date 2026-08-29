# RECEIPT — F-1(b) far-end measurement at `aa67c426`, filed by the producer

**CITABLE FOR:** the F-1(b) far-end A-2(a)–(g) measurement taken on
2026-08-29T22:08:01Z (2026-08-30 Europe/Paris) against the deployed tree
`/pscratch/sd/j/josephrb/k0r2/clean`, and for the comparison of those values with the independent
grader's 2026-08-25 values.

**NOT CITABLE FOR:** a new grade, a changed Gate-2 disposition, any other clause's discharge, a
fitness finding for the F-17(b) chain, authorization to modify or reposition the deploy tree, a
rehearsal, compute, covariance construction or adoption, or any publication claim.

**Producer and author:** Codex, the primary `/root` lane working from canonical `main`. **This is a
PRODUCER filing.** I took and file the measurement; I do not grade it.

## 1. Requirement and subject

Review-contract §7.0.5 defines the F-1(b) post-rehearsal half exactly as:

> *"the same measurements repeated after the last leg; porcelain zero and the manifest digest
> identical at both ends"*

The subject is the deploy tree frozen by §7.0.19 at the declared sha
`aa67c426afaa9b6ca91c9996637a6bade950da9a`. The last rehearsal leg had already ended before this
measurement; the independent verdict records combine job `57527875` ending at
`2026-08-25T16:24:42`.

## 2. Producer measurement — all seven A-2 values

The pinned interpreter was
`/global/u2/j/josephrb/.conda/envs/root_6_28/bin/python3`. The instrument was the copy inside the
subject tree, `nd-unfolding/mnv_source_manifest.py` at `aa67c426`. It ran once with all five
fail-closed `--require-*` flags, `--compare`, and a temporary `--write` destination outside the
deploy tree. It returned **rc=0**.

| A-2 | producer measurement | value |
|---|---|---|
| a | declared sha and detached state | `aa67c426afaa9b6ca91c9996637a6bade950da9a`; direct `.git/HEAD` content was that sha and not a `ref:`, therefore **DETACHED** |
| b | `dirty_count` from `git status --porcelain` | **0** |
| c | `constitution.is_checkout` / `markers` | `true` / `["VALIDATION_LEDGER.md", "nd-unfolding"]` |
| d | `constitution.nested_checkouts` | `[]` |
| e | `constitution.enclosing_checkout` | `null` |
| f | `--compare --require-clean` | **rc=0**; `SOURCE MANIFEST IDENTICAL (782 files, fa3489e22168954bebcc9a602338d924582fd231643bfa285b3a9225e7535420)` |
| g | `constitution.mode_writable` / `uid_writable` / `other_writable` | `[]` / `[]` / `[]` |

The baseline was
`/pscratch/sd/j/josephrb/k0r2/declarations/aa67c426/source-manifest.json`:

| object | sha256 / value |
|---|---|
| baseline **file bytes** | `622ddc0ada33234d5b420130cd6e60e17ead8b2669b6e77436f0f57a89e2a405` |
| baseline `listing_sha256` **field** | `fa3489e22168954bebcc9a602338d924582fd231643bfa285b3a9225e7535420` |
| baseline `file_count` field | `782` |
| live `listing_sha256` field | `fa3489e22168954bebcc9a602338d924582fd231643bfa285b3a9225e7535420` |
| live `file_count` field | `782` |

The baseline file sha256 and the `listing_sha256` field are different objects and are not
interchangeable. The first hashes the JSON file bytes; the second is the recorded digest over the
sorted source listing.

## 3. Comparison with the grader

**Measured comparison:** all seven producer A-2 values agree exactly with the values in
`VERDICT-20260825-gate2-k0-rehearsal-nine-clauses.md:77-85`. The full baseline file sha256 agrees
with the grader's published `622ddc0ada33234d…` prefix and with the full value in
`DECLARATION-20260823-k0-candidate-aa67c426.md:62-63`. The producer measurement found **no
disagreement**, so no reconciliation was attempted.

This comparison is not a grade. It states equality between the values I measured and the values the
grader filed.

## 4. Read-only discipline and exact command record

Decision §11.1 states exactly:

> **"The consequence worth carrying: inspecting the frozen deploy with `git` is not a read-only
> act."**

The measurement therefore set `GIT_OPTIONAL_LOCKS=0` for the pinned instrument's four internal Git
reads and set `PYTHONDONTWRITEBYTECODE=1`. Its output JSON was written to the exact `mktemp` path
`/tmp/f1b-producer-aa67c426.9A1yAV.json`, outside the deploy tree, and removed by the exit trap.

These were every command that read or measured the deploy tree, including the Git subprocesses the
instrument itself issued:

```bash
/usr/bin/stat --format='pre_git_metadata=%n|mode=%a|size=%s|mtime=%y' \
  "$CODE_ROOT/.git" "$CODE_ROOT/.git/index" "$CODE_ROOT/.git/HEAD"
IFS= read -r HEAD_CONTENT < "$CODE_ROOT/.git/HEAD"
GIT_OPTIONAL_LOCKS=0 PYTHONDONTWRITEBYTECODE=1 "$PYTHON" "$TOOL" \
  --repo "$CODE_ROOT" \
  --compare "$BASELINE" \
  --write "$MEASUREMENT_JSON" \
  --require-clean \
  --require-checkout \
  --require-no-nested-checkout \
  --require-not-nested \
  --require-readonly \
  --label 'F-1(b) producer far-end measurement 2026-08-30'
# Internal to mnv_source_manifest.py, all inheriting GIT_OPTIONAL_LOCKS=0:
git -C "$CODE_ROOT" rev-parse --git-dir
git -C "$CODE_ROOT" ls-files -z
git -C "$CODE_ROOT" rev-parse HEAD
git -C "$CODE_ROOT" status --porcelain
/usr/bin/stat --format='post_git_metadata=%n|mode=%a|size=%s|mtime=%y' \
  "$CODE_ROOT/.git" "$CODE_ROOT/.git/index" "$CODE_ROOT/.git/HEAD"
```

For completeness, the same consolidated remote shell also ran `/usr/bin/date --utc`,
`/usr/bin/sha256sum "$BASELINE"`, a Python readback of the baseline and temporary output JSON, and
the exit trap's `rm -f "$MEASUREMENT_JSON"`. Those commands did not address the deploy tree.

The deploy `.git` metadata was identical before and after:

| path | mode | size | mtime before | mtime after |
|---|---:|---:|---|---|
| `.git` | `770` | 4096 | `2026-08-26 01:09:29.000000000 -0700` | same |
| `.git/index` | `660` | 193386 | `2026-08-24 04:36:13.000000000 -0700` | same |
| `.git/HEAD` | `660` | 41 | `2026-08-24 04:34:10.000000000 -0700` | same |

**Measured postcondition:** no change to those three `.git` objects was observed. No `checkout`,
`reset`, `fetch`, ref update, branch operation, chmod, source write, Slurm command, or M(ii) leg was
run.

## 5. Scope — what this filing does not move

The delegated decision records the current disposition exactly:

> **"GATE 2 REMAINS FAIL"** on the six independently sufficient clauses of the delegated
> re-evaluation at `327bc105`. **"Readiness remains NOT READY. No rehearsal is authorized."**

It also records the surviving F-17(b) grade line exactly as
`F17B-MECHANISM-CORRECTED: NOT FIT`.

**Inference from scope:** this record files only F-1(b), which the governing clause table already
records as PASS. It provides no evidence for F-2(b), F-3(b), F-5(b), F-7(b), F-8(b), or F-17(b), so
it changes none of them and does not move Gate 2. In particular, it does not make F-17(b)'s missing
pre-submission half exist and does not backfill it.

The historical §7.0.19 no-move sentence was:

> "No `checkout`, no `reset`, no `fetch`-and-merge, no re-declaration, no branch repoint in that
> directory."

Its expiry condition had already fired, as recorded beside OI-162. This filing neither revives that
freeze nor authorizes any modification or repositioning of the deploy tree; moving the tree belongs
to a separate deployment decision.

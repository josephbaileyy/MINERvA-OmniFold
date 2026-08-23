# DECLARATION — the k=0 submission sha, and A-2(a)–(g) filed against it

**CITABLE FOR:** the single commit the k=0 execution tree is constituted at, and the seven A-2
results measured **on that tree**. This is the referent that `F-1(a)` said did not exist.

**NOT CITABLE FOR:** any authorization to submit. Gate 1 does **not** pass; see §4. This document
declares a sha; it does not clear a gate, and no `sbatch` is authorized by it.

**Closes `PR-01` / `F-1(a)`.** The Gate-1 verdict recorded *"no document declares the submission
sha"*, and a covering search confirmed every hit was the requirement, a reviewer recording the
absence, or the literal placeholder `<the approved clean tree at the declared sha>`
(`PLAN-20260822-oneMember-mii-staged.md:434`, `RUNBOOK-20260822-b1-lift-preflight.md:409`,
`VERIFICATION-20260822-k0-execution-integrity.md:155`). It now has a referent.

---

## 1. THE DECLARED SHA

```
MNV_CODE_ROOT = /pscratch/sd/j/josephrb/k0r2/clean
sha           = 6113a34d860ad9bcd643923d51170f228c80d894
branch        = build-k0-execution-integrity
```

**Why this sha and not `de040d9b`, which the tree carried until today.** The deploy was four commits
behind the build branch, and two of those commits are the Gate-1 repairs `PR-03` (`b49bc360`) and
`PR-02` (`6113a34d`). Declaring before refreshing would have pinned a tree the repairs then
invalidated — `PR-01`'s own expiry clause says *"falsified by … any change to `k0r2/clean`; any
`.py`/`.sh` add or delete (moves `file_count`)"*. **The declaration is therefore taken LAST, after
the repairs and after the refresh**, which is the ordering correction recorded in
`WALKDOWN-20260822-one-pass.md`.

### The refresh, with its receipt

```
$ cd /pscratch/sd/j/josephrb/k0r2/bare.git
  before: de040d9b0ccd594240b0a617298c533f2f249a65
$ git fetch https://github.com/josephbaileyy/MINERvA-OmniFold \
      build-k0-execution-integrity:build-k0-execution-integrity
   de040d9b..6113a34d  build-k0-execution-integrity -> build-k0-execution-integrity   # fast-forward
  after:  6113a34d860ad9bcd643923d51170f228c80d894

$ cd /pscratch/sd/j/josephrb/k0r2/clean
  PRE  : HEAD=de040d9b  porcelain=0  --require-readonly rc=0   (protection was ON)
  PRE  : 773 tracked source files, listing sha256 afc572b0277b063a6d23a701ccbacd0ad516545e9fc0201baa14553940ca206b
$ mnv_source_manifest.py --repo $C --write undo.json --undo-readonly
  undid A-2(g) write protection: 922 of 922 protected path(s) changed mode
$ git fetch origin build-k0-execution-integrity && git merge --ff-only FETCH_HEAD
  rc=0, rc=0;  HEAD now 6113a34d;  porcelain 0
$ mnv_source_manifest.py --repo $C --write applied.json --apply-readonly
  applied A-2(g) write protection: 924 of 924 protected path(s) changed mode
```

**The file count moved 773 → 775, exactly the +2 predicted** by `PR-03` adding
`mnv_preflight_census.py` and `tests/test_k0_preflight_exclusion_census.py`. A number that moved by
the amount its cause predicts is worth more than one that merely looks right, so it is recorded here
with both endpoints.

**An instrument note, because it nearly became a false record.** The first `--undo-readonly` attempt
printed `COULD NOT LOOK: give --write and/or --compare` and I read `rc=0` from a **piped** command —
the pipe's status, not the tool's. The tool had measured nothing. Re-run unpiped with `--write`, it
worked. `--require-readonly` alone likewise returns `2` — *could not look* — without `--write`, and
`2` must never be read as clean.

---

## 2. A-2(a)–(g), EACH MEASURED SEPARATELY

Seven clauses, seven observations — not one combined invocation, so that no clause is carried by
another's pass. Measured **2026-08-22, after the refresh**, on `MNV_CODE_ROOT` itself.

| # | requirement (`REVIEW-CONTRACT…:198-205`) | result | evidence |
|---|---|---|---|
| **a** | `git rev-parse HEAD` equals the declared sha | **MET** | `6113a34d860ad9bcd643923d51170f228c80d894` |
| **b** | `git status --porcelain` emits **zero lines** | **MET** | `0` — counted by `wc -l` on a redirected file, **not** by reading `$?` after a pipe, as the clause itself instructs |
| **c** | a checkout by the guard's own definition | **MET** | `VALIDATION_LEDGER.md` present, `nd-unfolding/` present; `--require-checkout` **rc=0** |
| **d** | no nested MINERvA-OmniFold checkout beneath it | **MET** | `--require-no-nested-checkout` **rc=0** |
| **e** | not nested inside another checkout | **MET** | `--require-not-nested` **rc=0** |
| **f** | full source manifest over tracked `*.py`/`*.sh` | **MET** | **775** files, listing sha256 `cc00489464b0e803247eeb7cd90afa2f59f010340f6db64123e12b20eafc2239` |
| **g** | write protection applied | **MET** | `--require-readonly` **rc=0**, and **independently**: `find . -path ./.git -prune -o -type f -writable -print \| wc -l` → **0** |

**(g) is given two instruments on purpose.** The tool's own verdict and a filesystem walk that does
not share its code. The tool additionally reported *"plus 5 non-tracked writable file(s)"* during the
apply; `git status --porcelain --ignored`, `git ls-files -o`, and `git ls-files -o --exclude-standard`
all return **0**, and the independent walk finds **0** writable files. So the tree is clean and
protected on every instrument, and **the "5" is a count of paths the apply CHANGED, not a residual** —
recorded here rather than smoothed over, because I have not traced which five.

---

## 3. WHAT THIS DECLARATION DOES NOT COVER

- **`f` covers tracked `.py` and `.sh` only.** A gitignored file at an executing path is invisible to
  it. That is the manifest's declared scope, not a defect, and it is why `A-2(g)` exists.
- **This is the `k0r2/clean` tree, not "whatever tree the real submission uses."** If the submission
  is made from a different root, every row above must be re-measured there. The receipt already
  carries this caveat and it is not discharged by this document.
- **Re-verification after the last leg is still owed.** `A-2` requires the manifest digest to be
  identical at both ends; this is the *before* end only.
- **Expiry.** Any commit to `build-k0-execution-integrity`, any change to `k0r2/clean`, any `.py`/`.sh`
  add or delete. This item is falsified by exactly the work it enables.

---

## 4. GATE 1 STILL DOES NOT PASS

`F-1(a)` is closed by this document. **`F-2(a)` is repaired in its FIRST HOP ONLY** — the transitive
environment trust boundary is open by Joseph's explicit instruction, and Gate 1 may not be recorded
closed until it is settled **and a fresh non-builder passes it**
(`DECISION-20260822-joseph-b1-lift-and-clause-c.md`, "THE TRANSITIVE ENVIRONMENT TRUST BOUNDARY").
`F-8(a)` and `F-17(a)` are addressed in the companion artifacts filed the same day.

**The grader must be a fresh non-builder.** This lane built `PR-01`, `PR-02` and `PR-03` and is
disqualified from grading any of them.

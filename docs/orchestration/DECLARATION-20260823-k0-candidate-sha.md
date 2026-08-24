# DECLARATION — the k=0 candidate sha, and A-2(a)–(g) filed against it

> ## ⚠ SUPERSEDED 2026-08-23 — the candidate is now `aa67c426`
> **Everything below was true of `a54038b2` when measured and remains historically valid.** It is
> superseded because that tree **cannot execute legs 5a/5b**: `compare_unified_throw.py` hardcoded
> the canonical root into `sys.path.insert(0, …)` and the OI-136 guard refused before any work ran.
> Round 9's 18/0/0 at this sha is likewise historically valid and **does not carry forward** —
> see [`PACKET-20260823-round10-oi136-runtime-violation-repair.md`](PACKET-20260823-round10-oi136-runtime-violation-repair.md).
> The replacement is [`DECLARATION-20260823-k0-candidate-aa67c426.md`](DECLARATION-20260823-k0-candidate-aa67c426.md).
> **Do not cite the numbers below for the current candidate.**

**CITABLE FOR:** the constitution of the execution tree at the declared sha, measured 2026-08-23.

**NOT CITABLE FOR:** a Gate-1 pass, and not for an `sbatch` authorization. **This declares a sha; it
clears no gate.** Gate 1 does **not** pass — round 8 returned 17 PASS / 1 FAIL, and this document is
the repair of that one failure, not a verdict on it.

**Closes the round-8 `F-1(a)` failure**, whose two limbs were: the A-2(f) digest was never filed at
the candidate sha (the filed figure was 778 / `70fb59d4…` at `f3c27870`, three shas stale), and the
packet's `DEPLOYED AT` row named `e93364d1` while the deployed `HEAD` was `a54038b2` — *"not a
missing declaration but a present and false one."* Both re-measured here rather than argued.

---

## 1. THE DECLARED SHA

```
sha      = a54038b21fdebfc975bec452a05866ffa571a36c
branch   = build-k0-execution-integrity
tree     = /pscratch/sd/j/josephrb/k0r2/clean
```

**WHY THIS DOCUMENT DOES NOT NAME ITS OWN COMMIT, AND WHY THAT IS NOT A DODGE.** A file cannot
contain the sha of the commit that adds it. The convention here resolves it the same way the
round-5 declaration did: **a declaration is paperwork *about* an execution tree, and it lives where
the paperwork lives.** `DECLARATION-20260822-k0-submission-sha.md` declares `6113a34d`, was added at
`b2b96730`, and `6113a34d` is not even an ancestor of that commit.

**Consequently this commit does NOT move the deployment.** The deployed tree stays at
`a54038b2` — the sha declared above — so A-2(a) holds **exactly**, not approximately. Two commands
falsify the whole arrangement:

```bash
git -C /pscratch/sd/j/josephrb/k0r2/clean rev-parse HEAD     # must be a54038b2…
git diff --name-only a54038b2..HEAD                          # must list ONLY docs/orchestration/
```

If the second ever lists an `.sh` or a `.py`, the executable bytes have diverged from the declared
tree and **every measurement below is void.** `nd-unfolding/**` is byte-identical across the two.

**This is a judgement call and I am flagging it rather than burying it.** The alternative — deploy
this commit and declare *its* sha — is impossible without a second commit, and a definite
description (*"whatever `rev-parse` returns"*) is what round 8 correctly rejected: it re-points every
commit and nothing can falsify it.

## 2. A-2(a)–(g), EACH MEASURED SEPARATELY

Measured in the deployed tree, post-conda `python3` 3.11.14, `MNV_ENV_ROOT` and `MNV_CONDA_PREFIX`
exported.

| # | requirement | result | evidence |
|---|---|---|---|
| **a** | `git rev-parse HEAD` equals the declared sha | **MET** | `a54038b21fdebfc975bec452a05866ffa571a36c` |
| **b** | `git status --porcelain` emits zero lines | **MET** | `0` — counted with `wc -l` on a redirected file, never by reading `$?` after a pipe |
| **c** | a checkout by the guard's own definition | **MET** | `--require-checkout` **rc=0** |
| **d** | no nested MINERvA-OmniFold checkout beneath it | **MET** | `--require-no-nested-checkout` **rc=0** |
| **e** | not nested inside another checkout | **MET** | `--require-not-nested` **rc=0** |
| **f** | full source manifest over tracked `*.py`/`*.sh` | **MET** | **780** files, listing sha256 `1b45da558929b0ec6eedbc56504a440252e39a9270e6d8f9796c02eb3d2895ad` |
| **g** | write protection applied | **MET** | `--require-readonly` **rc=0**, and independently `find . -path ./.git -prune -o -type f -writable -print \| wc -l` → **0** |

**EVERY rc ABOVE WAS TAKEN WITH `--write` OR `--compare`.** Run bare, `mnv_source_manifest.py`
returns **rc=2 — "COULD NOT LOOK"**, which is never "clean". My first pass at this table did exactly
that and recorded five spurious `rc=2`s; the round-8 grader reported the same trap against itself.
A clause measured by an instrument that could not run is not a clause that passed.

**(g) is given two instruments on purpose** — the tool's verdict and a filesystem walk that does not
share its code.

**A-2(f) as a GATE, not just a record:**

```
$ mnv_source_manifest.py --repo <tree> --compare <manifest> --require-clean     rc=0
[srcman] SOURCE MANIFEST IDENTICAL (780 files, 1b45da558929b0ec6eedbc56504a440252e39a9270e6d8f9796c02eb3d2895ad)
```

**Both preflight tools are present in the manifest** (§7.0.13), checked by key lookup over its 780
entries rather than by substring: `nd-unfolding/lib_mnv_env_preflight.sh` **present**,
`nd-unfolding/lib_mnv_env_pathcheck.sh` **present**.

## 3. WHY 780, AND THE EXPIRY CLAUSE

The count moved with its cause, exactly as the round-8 verdict traced it:
`f3c27870` → 778, `60cf728d`/`0b556379`/`14980486` → 779, `1d2b795d`/`a54038b2` → **780**. The two
additions since the filed figure are **`docs/orchestration/measure_m1_m6.py` and
`docs/orchestration/test_measure_m1_m6.py`** — the M-1…M-6 instrument and its test. Zero deletions.

> **⚠ CORRECTED 2026-08-23, after the round-9 PASS; the graded version of this file said otherwise.**
> It read *"the round-7 parity libraries and the round-8 instrument test."* That is **false**: the
> parity libraries were **RENAMED**, not added — `git diff --name-status -M f3c27870..a54038b2`
> gives `R100 nd-unfolding/mnv_env_pathcheck.sh -> lib_mnv_env_pathcheck.sh` and the same for
> preflight — so they were already inside the 778, and a rename is **count-neutral**. The round-9
> grader flagged it without failing on it, and its diagnosis of why the error is tempting is worth
> keeping: the commit that moved the count to 779 is also the commit that renamed them, so *"what
> else that commit did"* got substituted for *"what moved the count."* Third instance in this
> campaign of **state the class you counted alongside the number.** The count, digest, falsifier and
> all seven clauses were and remain correct; only this gloss was wrong.

**THIS DECLARATION IS FALSIFIED BY ANY ADD OR REMOVAL OF A TRACKED `*.py` OR `*.sh`, AND BY NOTHING
ELSE.** A-2(f) covers only those two suffixes, so a Markdown-only commit **cannot** move the listing
— which is why 780 and `1b45da55…` were declarable inside a doc-only commit at all, and why the
self-reference excuse the round-5 declaration could have claimed does not apply here either.

Re-run before the first `sbatch` and again after the last leg; the digest must be identical at both
ends. **Do not inherit these numbers.**

## 4. WHAT THIS DOES NOT DO

- It does **not** pass Gate 1, and does not assert `F-1(a)` is closed — that is the grader's call.
- It authorizes **no** Slurm submission, science run, covariance work, or deployment change.
- It does not touch an executable byte; `nd-unfolding/**` is unchanged since `60cf728d`.

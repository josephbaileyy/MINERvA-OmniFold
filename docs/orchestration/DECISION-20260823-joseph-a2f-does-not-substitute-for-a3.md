# DECISION 2026-08-23 — Joseph: A-2(f) does not substitute for A-3 executing-file parity

**Recorded by the publication close-out lane on 2026-08-23, from Joseph directly in session.**

**Why this file exists.** The ruling arrived as a chat message. A relayed result is not quotable
(`AGENTS.md`), and this ruling decides a Gate-1 criterion, so it needs a citable home before anything
rests on it. Cite this path; do not cite a relay of it.

**Disclosure of interest.** I am the builder of the code this ruling fails. The gate block that
F-2(a) now stands on is mine. Nothing below is my reading of a close call — the ruling is quoted
verbatim and the measurements are re-run, not carried forward.

---

## Ruling — A-2(f) is not a substitute for A-3

> "A-2(f) does not substitute for A-3 executing-file parity. The two tracked environment libraries
> execute before the later source-manifest comparison and therefore require pre-use git parity.
> F-2(a) stands.
>
> F-17(a) also stands until the canonical M-1…M-6 filing is corrected and re-measured at the
> eventual candidate SHA."

**Scope.** This settles the *principle*, not one launcher. The test is now: does a tracked file
execute before the instrument that binds its bytes? If yes, it needs pre-use git parity, and a
later source-manifest comparison does not discharge that.

**What the ruling makes true, measured at `fabeedc2` on `build-k0-execution-integrity`.**
`nd-unfolding/lib_mnv_env_preflight.sh` and `nd-unfolding/lib_mnv_env_pathcheck.sh` are sourced from
`${CODE_ROOT}` by all eight k=0 launchers with no git-parity gate of their own. In
`sbatch_uthrow_block_5d.sh` the parity gate at `:57-:70` names only `lib/resume_guard.sh`; the two
libraries are sourced at `:74` and `:76`; `lib/resume_guard.sh` is not sourced until `:101`. Both
libraries are **tracked**, so git can bind them — which is why the three accepted substitutions for
the untracked closure files do not reach them.

**This ruling authorizes no repair.** Joseph's instruction with it was explicit: *"Land only the
verdict, regenerate required state/manifest views, and stop. Do not repair anything yet."* The
obvious fix — extending the existing parity block to the two libraries — is **not** authorized by
this document.

---

## Gate 1 status after this ruling

**GATE 1 DOES NOT PASS.** Round 6: **16 PASS / 2 FAIL / 0 NOT-EVALUABLE**, failing `F-2(a)` and
`F-17(a)`. The round-6 grader recorded that F-2(a) would fall if A-2(f) were ruled sufficient;
Joseph ruled it is not, so the tally stands as graded.

`F-17(a)` stands unrepaired and is out of round-6 scope. The defect is on `main`:
`docs/orchestration/MEASUREMENT-20260822-m1-m6-at-pinned-sha.md:52` reads "the three that remain"
where there are four, and the M-1 filing drops `unified_throw_cov.py`, one of the six B-1 files.
Per the ruling it is not closed by an edit alone — it requires re-measurement at the eventual
candidate sha.

---

## The landed verdict

| field | value |
|---|---|
| path | [`GATE1-VERDICT-ROUND6-20260823-k0-execution-integrity.md`](GATE1-VERDICT-ROUND6-20260823-k0-execution-integrity.md) |
| sha256 | `bf2ad6e1415391bb5eba3e15b9e818fb10a6ee65ce4e7ca1b8b08dd57c3d0125` |
| lines | 415 |
| bytes | 29173 |
| origin | `/Users/josephbailey/local-research/` (outside the repo, uncommitted at any ref until now) |

Landed **byte-identically**: `cmp` against the origin file is clean and the digest above was
recomputed on the committed path, not carried from the handoff message. The operative rubric was
confirmed by the grader to be byte-identical to round 5 (1160 lines, `e0fb342b6466…`) — no criterion
was added.

**Two round-5-era corrections the grader made against its own interest**, recorded here so they are
not lost with the verdict: its round-5 statement that files not covered by a `--pair` numbered "0
among files under the code root" was **false**, and false at `f3c27870` for the same two files under
their former names; and F-14 ground (i) was withdrawn in the round-5 document itself at `:585`.
Neither changed a verdict.

## Joseph's dispositions on the round-6 FUTURE FINDINGS (2026-08-23)

Recorded verbatim from Joseph in session, and **authorized by him to be recorded as his direct
rulings** rather than as a relay. The round-6 grader raised three items it explicitly declined to
fail Gate 1 on, recording them as future findings for Joseph to ratify. He has ratified them:

> "The 16 pinned interpreter-capability probes are accepted as a distinct, enumerated category
> outside the guard/P-4 boundary."

> "ROOT628_CONDA's declared system default is accepted for this k=0 rehearsal as a recorded residual,
> not a Gate-1 blocker."

> "The unreadable-member diagnostic wording is nonblocking and must not expand Gate 1."

**None of the three expands Gate 1, and none is a repair authorization.** Ruling 21's guarding
boundary stays at 14 guarded + 16 declared-preflight, with the 16 interpreter probes as a **visible
third category** rather than folded into either — the census prints all three and totals them, so the
boundary cannot drift silently. The `ROOT628_CONDA` default is a **recorded residual**: it is accepted
for this rehearsal only, and accepting it is not a finding that it is correct.

**The third disposition carries an instruction, not just a permission** — *"must not expand Gate 1."*
A wording defect in a diagnostic is repairable, and a repairable defect does not belong in a
disclosure register; but it is also not a Gate-1 criterion, and it may not be made one.

## The authorized round-7 repair

Issued with the dispositions above. Three items, no unrelated changes:

1. **Extend the pure-git parity gate**, before either environment library is sourced, to bind
   `nd-unfolding/lib_mnv_env_preflight.sh`, `nd-unfolding/lib_mnv_env_pathcheck.sh` and
   `lib/resume_guard.sh`, with positive-parity and mutation-refusal controls proving refusal occurs
   **before** the source, and **no** new helper or trust layer.
2. **Re-run and correct the complete M-1…M-6 filing** at the final candidate sha and the current
   canonical checkout, restoring `unified_throw_cov.py` as the tenth M-1 row, **reporting both tree
   states explicitly and not pre-answering the result.**
3. **Update the operative runbook and plan §C** to export the mandatory `MNV_ENV_ROOT` and
   `MNV_CONDA_PREFIX` values.

**Explicitly withheld:** Slurm submission, any science run, any further repair round, and any claim
that Gate 1 passed. *"The same round-6 grader will perform the terminal regrade. Whether PASS or FAIL,
return the verdict to me and stop."*

**A correction Joseph made to the builder, recorded because it changed the work.** The builder
measured `unified_throw_cov.py` on **`main`**, found an active hardcoded `_REPO` feeding a
`sys.path.insert(0, …)`, and reported it as the *candidate's* state — arguing on that basis that
instruction 2 pre-specified a wrong answer. Joseph re-measured the candidate directly
(`git show fabeedc2:nd-unfolding/unified_throw_cov.py`) and established that it carries the B-1
repair, with `_DATA_ROOT` as its only absolute canonical literal. **His expected split — three
`_DATA_ROOT` and one inert `_REPO` — is what the candidate actually measures.** The hardcoded `_REPO`
is real and is on the canonical checkout, where it is one of five. Both are true of different trees;
only one is true of what executes.

## Process note

This is a **terminal handoff**. The round-6 grader requested no further grader, and the freeze on
rubric and candidate holds. The two open findings are a repair and a re-measurement, not grading
questions. See [`DECISION-20260822-joseph-b1-lift-and-clause-c.md`](DECISION-20260822-joseph-b1-lift-and-clause-c.md)
for the preceding ruling set.

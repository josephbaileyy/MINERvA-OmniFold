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

## Process note

This is a **terminal handoff**. The round-6 grader requested no further grader, and the freeze on
rubric and candidate holds. The two open findings are a repair and a re-measurement, not grading
questions. See [`DECISION-20260822-joseph-b1-lift-and-clause-c.md`](DECISION-20260822-joseph-b1-lift-and-clause-c.md)
for the preceding ruling set.

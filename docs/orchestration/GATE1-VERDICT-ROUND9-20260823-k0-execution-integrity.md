# GATE 1 — ROUND-9 TERMINAL REGRADE, k=0 EXECUTION INTEGRITY

**Grader:** independent non-builder session (`minerva-omnifold-6d`). **Read-only throughout.**
**Date:** 2026-08-23. **Host:** `login02` (`saul.nersc.gov`) + local. **Window:** ~16:1xZ – 16:4xZ.

---

## 1. ELIGIBILITY

I built no commit in the `build-k0-execution-integrity` history, authored no part of the §7.0 split,
and authored neither the round-8 repair `bafe2557` nor the declaration it adds. §7.0.10's
disqualification is about authorship; prior service as the round-5, -6, -7 and -8 grader does not
disqualify me. I inherit no PASS. Where this verdict corrects one of my own earlier statements I say
so (§8).

**Not done:** no repository edit, commit, push, merge, deployment or repair; **no Slurm submission**;
no rehearsal, science or covariance work; no `set -u`; no new acceptance criterion; no further grader
requested. I did not move the deployment, and I did not accept the builder's offer to move it (§3).

---

## 2. FROZEN OBJECTS

| object | declared | measured | verdict |
|---|---|---|---|
| declared / deployed | `a54038b21fdebfc975bec452a05866ffa571a36c` | `rev-parse HEAD` → `a54038b2…` | **CONFIRMED** |
| filings | `bafe2557ecae9a9b52a15964ee806f42e91a37fe` | branch tip, 1 commit ahead of the deploy | **CONFIRMED** |
| `main` | `8a5c2f0517244df1be7b8b8939e3e956c6230406` | local HEAD `8a5c2f05…` | **CONFIRMED** |
| rubric **by digest** | 1160 lines, `e0fb342b6466…` | identical at `8a5c2f05` **and** at `f1e2f10e`, `main`'s head when I closed | **CONFIRMED** |
| deploy hygiene | porcelain 0, 0 writable | **0** and **0**, before and after | **CONFIRMED** |

The branch at `bafe2557` still carries the **575-line** superseded rubric (`80402f75057aa58c…`). I
graded the rubric from `main`, by digest, as instructed.

### 2.1 The arrangement's own falsifiers, both run by me

```
git diff --name-status a54038b2..bafe2557
    M docs/orchestration/CATALOG.md
    A docs/orchestration/DECLARATION-20260823-k0-candidate-sha.md
    M docs/orchestration/MANIFEST-overrides.tsv
    M docs/orchestration/MANIFEST.tsv
    M docs/orchestration/PACKET-20260823-round7-f2a-parity-and-f17a-filing.md
  non-docs paths: 0        .py/.sh paths: 0
git diff --name-only 60cf728d..bafe2557 -- 'nd-unfolding/**'    ->  0 lines
tracked *.py/*.sh at bafe2557                                   ->  780   (unchanged from a54038b2)
```

**The consequence that decides the arrangement question: the filing commit changed zero `.py`/`.sh`,
so the A-2(f) listing is `780` / `1b45da55…` at *both* shas.** Nothing perishable rides on which of
the two trees is deployed. The only difference between them is Markdown.

---

## 3. RULING ON THE ARRANGEMENT — UPHELD; DO NOT MOVE THE DEPLOYMENT

The builder asked to be overruled if I judged that the graded tree must be self-consistent. **I do
not, and I decline the offer.** The arrangement is correct, and moving the deploy to `bafe2557` would
make things worse. Four reasons, in order of weight:

1. **A-2(a) is a literal equality and only this arrangement satisfies it.** *"`git rev-parse HEAD`
   equals the declared sha."* Deploy `a54038b2`, declare `a54038b2` → holds exactly. Deploy
   `bafe2557`, declare `a54038b2` → **false by one commit**. Declare `bafe2557` inside `bafe2557` →
   impossible. There is no third option, and the proposed "fix" would trade a true constitutional
   clause for a documentation cosmetic. Round 8 failed this criterion for a *false sha row*; I am not
   going to reward the repair by inducing a false sha *measurement*.
2. **Nothing perishable depends on the choice** (§2.1). A-2(f) covers only tracked `*.py`/`*.sh`, the
   filing commit touched none, and I verified the count and digest are identical at both shas. The
   one number that would have made this a real dilemma is arrangement-invariant.
3. **The precedent is real, and I verified it rather than accepting it.**
   `DECLARATION-20260822-k0-submission-sha.md` was added at `b2b96730`, declares `6113a34d`, and
   `git merge-base --is-ancestor 6113a34d b2b96730` returns **non-zero — not an ancestor.** The
   campaign has already filed a declaration from outside the tree it declares.
4. **A-2 governs the execution tree; a declaration is paperwork about it.** A-2's own preamble says
   the constitution is *"recorded in the run receipt"* — a record *about* a tree, not a member of it.
   A tree that had to contain a true statement of its own identity could never be constituted at all.

**The residual cost, stated rather than smoothed over.** The deployed tree carries the *pre-repair*
packet, whose `DEPLOYED AT` row still reads `HEAD e93364d1…` — false about the tree it sits in. I
confirmed this directly in the deployed bytes, and confirmed the declaration is **absent** there.
A-2(g) write protection plus porcelain-0 mean it **cannot be corrected in place** without breaking
the constitution, so arrangement A structurally guarantees one stale document inside the execution
tree until the deploy next moves. That is the same class as the 575-line branch rubric: a superseded
copy sitting where a reader may open it. It is **not** an A-2 violation — A-2 constrains identity,
cleanliness, protection and the `.py`/`.sh` manifest, and says nothing about Markdown currency.
Recorded as a future finding (§9.1).

**One thing the builder got right that is worth naming, because it breaks the recursion.** The packet
at `bafe2557` names **no sha at all** in that row and defers to the declaration. So on any future
deploy refresh the row cannot go stale again. The trap is one-shot, not structural.

---

## 4. F-1(a) … F-18(a)

| # | verdict | basis |
|---|---|---|
| **F-1(a)** | **PASS** | §5 — all seven A-2 clauses re-measured by me at the declared sha and filed; both limbs of the round-8 failure repaired |
| **F-2(a)** | **PASS** | one gate digest `480faeb9…` across all eight, gate ends before first source in all eight; census rc=0, `14+16+16+0 = 46` |
| **F-3(a)** | **PASS** | non-comment `--allow` across the eight: **0** |
| **F-4(a)** | **PASS** | denominator **14**, `> 0`, 0 unclassified |
| **F-5(a)** | **PASS** | generator + comparator present with matched FIRES/SILENT arms (round-8 measurement; bytes byte-identical) |
| **F-6(a)** | **PASS** | `repo_origin_count` asserted present-and-0 for the child argv shape |
| **F-7(a)** | **PASS** | P-4 pin, both-direction comparator, fail-closed on an absent pin, anti-vacuity arm |
| **F-8(a)** | **PASS** (flagged) | P-6 reproduces 8 entrypoints / 14 invocations; P-5 inventory produced; fifth blind spot still only in a banner and the round-5 packet |
| **F-9 – F-12** | **PASS** | N-1 receipt carries `outcome`, `refusal_site`, `checked=0` with `checked_provenance` and `guard_installed=false`, and `seed_offset_policy` absent-as-observation |
| **F-13** | **PASS** | `VERDICT_REFUSED_SCRIPT` / `b4-script-containment`, both directions |
| **F-14** | **PASS** | §6 rows discharged; `generate_manifest --check` **rc=0**, rows 429 → **430**, in the same commit as the new doc |
| **F-15** | **PASS** | the two named suites, **57 tests OK**, explicit `TMPDIR`, count quoted as measured |
| **F-16** | **PASS** | `verify_hash_bindings.py` **rc=0**, `ALL BINDINGS INTACT`, re-run at the deployed tree |
| **F-17(a)** | **PASS** | filing, instrument and test **byte-identical** to the round-8 PASS (`19412d70…`, `0fcd90f7…`, `0cc38708…`) |
| **F-18(a)** | **PASS** | this document, clause by clause, by a fresh non-builder |

**TALLY: 18 PASS / 0 FAIL / 0 NOT-EVALUABLE.**

---

## 5. F-1(a) — THE REPAIR, RE-MEASURED

`docs/orchestration/DECLARATION-20260823-k0-candidate-sha.md` at `bafe2557`, 99 lines, sha256
`72047925f93f8d3eaa5193bc0bc4d2d3376558f8db2533cb00237de348b05aad`. **Byte-identical on `main` at
`8a5c2f05`** — I checked, because two copies of a filing is exactly how this campaign has been bitten
before. The packet is likewise byte-identical on both (`0ef95f2ed7ef2ed821fd…`).

**Every clause re-measured by me, in the deployed tree, not read off the table:**

```
a)  git rev-parse HEAD                     a54038b21fdebfc975bec452a05866ffa571a36c   == declared
b)  git status --porcelain | wc -l          0        (redirected file, never $? after a pipe)
c)  --require-checkout                      rc=0
d)  --require-no-nested-checkout            rc=0
e)  --require-not-nested                    rc=0
f)  780 tracked source files, listing sha256
      1b45da558929b0ec6eedbc56504a440252e39a9270e6d8f9796c02eb3d2895ad
    --compare                               rc=0   [srcman] SOURCE MANIFEST IDENTICAL (780 files, 1b45da55…)
g)  --require-readonly                      rc=0
    independent filesystem walk             0 writable files
    both preflight tools, by KEY LOOKUP over the manifest's 799 keys:
      nd-unfolding/lib_mnv_env_preflight.sh   PRESENT
      nd-unfolding/lib_mnv_env_pathcheck.sh   PRESENT
```

Every rc above was taken with `--write` or `--compare`. Bare, the tool returns **rc=2 "COULD NOT
LOOK"**, which is never "clean" — the builder hit this on its first pass, logged five spurious
`rc=2`s, caught it, and recorded it in the declaration. That is the seventh of my own round-8 harness
errors reproducing on someone else the same day, and recording it rather than quietly re-running is
the right disposition.

**Limb 1 — the A-2(f) digest is now filed at the candidate sha.** `780` / `1b45da55…`, matching my
independent measurement exactly. The count trace in §3 of the declaration reproduces mine:
`f3c27870`→778, `60cf728d`/`0b556379`/`14980486`→779, `1d2b795d`/`a54038b2`→**780**. The expiry
clause names its own falsifier and nothing else: any add or removal of a tracked `*.py`/`*.sh`.

**Limb 2 — the false row is gone, and the seam was handled.** The `DEPLOYED AT` row now names no sha
and defers to the declaration. `"whatever rev-parse returns"` is deleted, with the reason recorded.
Critically, the **superseded post-commit block is labelled, not edited to look current**: *"Taken at
`e93364d1`, superseded by the round-8 re-measurement at `a54038b2`"*, and the sha inside the code
fence is annotated `# HEAD AT THE TIME OF THIS BLOCK, not now`. Relabelling rather than back-dating is
the correct treatment of a superseded measurement.

### 5.1 A false sentence in the declaration — flagged, not failed, and here is why

Declaration §3 states:

> *"The two additions since the filed figure are the round-7 parity libraries and the round-8
> instrument test."*

**This is false, and I measured it three ways.** The two additions are:

```
git diff --diff-filter=A --name-only f3c27870..a54038b2 | grep -E '\.(py|sh)$'
    docs/orchestration/measure_m1_m6.py
    docs/orchestration/test_measure_m1_m6.py
git diff --diff-filter=D  (same range)   ->  none
```

The parity libraries were **not added** — they were **renamed**, and were already inside the 778:

```
git diff --name-status -M f3c27870..a54038b2
    R100  nd-unfolding/mnv_env_pathcheck.sh   ->  nd-unfolding/lib_mnv_env_pathcheck.sh
    R100  nd-unfolding/mnv_env_preflight.sh   ->  nd-unfolding/lib_mnv_env_preflight.sh
```

**A rename is count-neutral, and that is exactly why the mistake is tempting.** The commit that moved
the count to 779 is also the commit that renamed the parity libraries, so "what else that commit did"
got substituted for "what moved the count." The correct gloss is *"the M-1…M-6 instrument and its
test"*.

**Why this does not fail F-1(a).** F-1(a) enumerates: a named sha, clauses (a)–(g) measured and filed
including the A-2(f) digest, (d)/(e)/(g) as fail-closed checks, and both preflight tools in the
manifest. **Every one of those is present and correct, and I verified each independently.** The false
sentence is a provenance gloss in a section whose numeric content — the count trace and the expiry
clause — is right, and which is self-contradicting: the trace two lines above places the adds at
`60cf728d` and `1d2b795d`, not at a parity-library commit. Failing Gate 1 and blocking the rehearsal
over a misattributed aside, when the declared quantity, the digest, the falsifier and all seven
clauses are correct, would be grading prose rather than the criterion — and inventing a limb for it is
the "no new acceptance criteria" violation I have been instructed against three times.

**It still needs correcting**, and it is the third instance in this campaign of the same lesson:
*state the class you counted alongside the number.* Had the error been in the count, the digest or a
clause, this would be a FAIL, and I want that boundary on the record so this disposition is not read
as leniency.

---

## 6. WHAT I RE-MEASURED RATHER THAN INHERITED

Executable bytes are unchanged since `60cf728d` and no `.py`/`.sh` changed since `a54038b2`, so the
round-8 measurements apply to the same bytes. I still re-ran the load-bearing ones at the deployed
tree:

```
verify_hash_bindings.py                rc=0   ALL BINDINGS INTACT
mnv_preflight_census.py                rc=0   14 guarded + 16 declared-preflight
                                              + 16 interpreter-probe + 0 unclassified = 46
parity gate, all eight                 ONE digest 480faeb987cb2352…, gate end < first source in each
                                              68-84/89  71-87/92  72-88/93  74-90/95
                                              75-91/96  76-92/97  81-97/102 82-98/103
non-comment `--allow`, all eight       0
```

And at the filings sha, the doc-coupled postconditions:

```
generate_manifest.py --check           rc=0   rows=430 (429 -> 430, the one new doc) overrides=67
live_doc_indexed.py                    rc=0   (the 13 pre-existing unindexed LIVE docs are the
                                              known, NOT-enforced backlog, unchanged)
MANIFEST-overrides.tsv:68              docs/.../DECLARATION-20260823-k0-candidate-sha.md  LIVE  open
CATALOG.md:8                           entry present
```

The override row matters: a new doc without one is born ARCHIVAL and invisible to the router. This
one is `LIVE`/`open` and catalogued, in the same commit — F-14's coupling, discharged.

---

## 7. WHAT REMAINS OPEN AT GATE 2, AND WHAT THIS PASS DOES NOT DO

Per **§7.0.6**: a Gate-1 PASS *"unlocks exactly one thing: submission of the seven jobs of logical
legs 1–5 for k=0. It unlocks nothing else."* Leg 6 stays gated by Amendment 1 §C. **No member k≠0 is
authorized.** §G is unchanged, and per §8 a PASS *"discharges corrections 2–4 for the k=0 arm and
nothing else."*

**I am not authorizing a submission.** I am recording that the pre-submission halves pass. The
decision to submit is Joseph's, and I have submitted nothing.

Still owed at Gate 2, unchanged by this verdict: F-1(b) porcelain and manifest digest identical after
the last leg; F-2(b) P-2 across every inventory and every `--pair` CURRENT; F-4(b)–F-7(b); F-8(b) the
receipt in its own words; **F-17(b)** M-1…M-6 re-measured *after* the path runs, M-2's 718-untracked
inventory claim being the perishable one; F-18(b). And the M-6 vacuity hole remains open — its
`checked > 0` half is F-5's post-rehearsal clause, which is where it is now due.

---

## 8. WHERE THIS VERDICT CORRECTS ME

**My round-8 wording on the gate digest was too strong and I withdraw it.** I wrote that
`3e211fe6831aeb8d93522c6cbd2d72375a09a42ad5440eb9bac2e32e839a4142` *"cannot be reproduced by any
extent"*. It reproduces:

```
lines 66-98 of sbatch_bootstrap_5d_gpu.sh   ->  3e211fe6831aeb8d…   MATCH
  i.e. from `# (1) EVERY TRACKED FILE` through `unset _mnv_rel _mnv_head _mnv_work` INCLUSIVE
lines 66-97 (the same span, unset EXCLUSIVE) ->  fdc87463b68ea00e…   the repository test's extent
```

I had tested eight extents anchored on the `for` line plus the test's exact slice, and never the
comment-header-through-`unset`-inclusive span. That was an incomplete search reported as a universal
negative — the exact error I have flagged in others twice in this campaign, committed by me.

Two notes for accuracy, neither of which rescues the number. The builder's correction described the
extent as *"the `awk` line-range inclusive of the `unset` line"*; that alone still does not reproduce
it (`awk NR>=81 && NR<=98` → `9d60c839…`), because the span also has to **start at the comment
header**, which their description omits. And the finding itself stands exactly as they concede it:
**two artifacts in one package compute different digests for the same named "gate block", differing
by one line, and the packet states no extent.** An unstated extent is the defect; the number's
reproducibility was never the point. Recorded as unusable, by agreement.

---

## 9. FUTURE FINDINGS — recorded, none folded into the tally

1. **The deployed tree carries a stale packet copy** whose `DEPLOYED AT` row reads `HEAD e93364d1…`
   while that tree is `a54038b2`, and the declaration is absent there. A-2(g) makes it uncorrectable
   in place. Same class as the 575-line branch rubric. Not an A-2 violation (§3).
2. **The packet's `main` row is now false.** It reads *"`c76fdbfac67d39f86bc0ea633e815c926de04add` —
   carries the ruling record and the same filing bytes."* `main` is `8a5c2f05`, and I verified the
   declaration is **PRESENT at `8a5c2f05` and ABSENT at `c76fdbfa`** — so `c76fdbfa` does not carry
   the same filing bytes. This is the **same defect shape, one row above the one just repaired**: the
   rows either side of it were edited in `bafe2557` and this one was not. A grader routed to
   `c76fdbfa` would grade a tree with no declaration and fail F-1(a) again. Cheapest fix: stop naming
   a `main` sha there too, for the same reason the `DEPLOYED AT` row stopped.
3. **Declaration §3's misattribution** of the two `.py` additions (§5.1). Correction: *"the M-1…M-6
   instrument and its test"*.
4. **`lib_member_resume.sh` is sourced before its `--pair` in `finalize` alone** (`:181` vs `:303`);
   containment-bound before use, not parity-bound. Count 2 stays 0 on the rubric's letter. Unrepaired
   by explicit choice, correctly flagged to Joseph rather than closed on a criterion nobody set.
5. **`test_measure_m1_m6.py` is in no declared suite list** and no `testpaths`; nothing runs it by
   default, and it protects the committed M-1…M-6 mechanism.
6. **`test_k0_preflight_exclusion_census.py` cannot run against an A-2(g)-protected tree** (13
   `PermissionError`s; 71/71 from a writable clone of identical bytes).
7. **The P-5 blind-spot table still lists four**, with the fifth only in a banner and the round-5
   packet.
8. **Canonical M-3's co-reported inventory delta** (`expected 118 / observed 120`) is still
   unmentioned in the filing; conceded, unrepaired, immaterial to any gate.
9. **The branch still carries the 575-line superseded rubric.** Grade by digest. Live trap for any
   future grader who reads from the branch.

---

## 10. HYGIENE

**Primary checkout** `/Users/josephbailey/local-research/MINERvA-OmniFold`: HEAD `8a5c2f05` at open,
`f1e2f10e` at close — `main` moved under me again from peer lanes, and I re-verified the rubric digest
at the new head (`e0fb342b6466…`, unchanged) so the grading basis is unaffected. Porcelain **2 lines**
before and after — `?? PROJECT_STATE_PILOT_PROPOSAL.tmp.md` and
`?? log_test.txt`, both pre-existing and untouched. No edit, stage, commit, push, fetch or checkout in
this repository. I worked `bafe2557` from a **throwaway clone** under the session scratchpad
precisely so the graded checkout's refs and index stayed untouched.

**Deployed tree** `/pscratch/sd/j/josephrb/k0r2/clean`: `a54038b2`, porcelain **0**, **0** writable,
before and after. **I did not move it**, and I explicitly declined the offer to (§3).

**Canonical checkout**: `b2d7d4ca…`, 722 dirty, not touched this round.

**Slurm:** no submission. Only pre-existing job `57275989`, PENDING, submitted **2026-08-20T15:02:55**.
No science, no covariance, no artifact adopted, quoted or deleted. Temporary artifacts: `/tmp/r9_*`
and the scratchpad clone, all outside every checkout.

---

## 11. CONCLUSION

Every pre-submission half of the operative rubric's eighteen criteria passes, each with its command
and output filed. The round-8 `F-1(a)` failure is repaired on both limbs and re-measured by me at the
declared sha. The two-tree arrangement is **upheld**: it is the only configuration in which A-2(a)
holds literally, and the one number that could have made it a real dilemma is invariant across both
trees.

Three defects are recorded as findings rather than failures — a false provenance sentence in the
declaration, a now-false `main` row in the packet, and a stale packet copy inside the execution tree.
None touches a clause any criterion enumerates; all three are one documentation commit away from
closed, and I have said what the boundary would have been.

**GATE 1 PASSES.**

Terminal handoff to Joseph. I have implemented no repair, initiated none, requested no further
grader, and submitted nothing. Per §7.0.6 this unlocks exactly the seven jobs of legs 1–5 for k=0 and
nothing else; the decision to submit is his.

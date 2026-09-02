- **The canonical quiesce window is CLOSED, 2026-08-30:**
  [`CLOSE-20260830-canonical-quiesce-window-k0-7ac0edec.md`](CLOSE-20260830-canonical-quiesce-window-k0-7ac0edec.md)
  — the freeze expired **on its own terms** (*"when submission is authorized or the rehearsal is
  abandoned"*), so **no new authorization is claimed**. Records this lane's *independent* remeasure of
  the sbatch-time property `F-17(a)` actually tests: HEAD `32e403b8`, porcelain **726**, status digest
  `d429f0f3…` — matching the operand without relying on the producer's report. Reconciles the two byte
  figures (a 4,096 difference = one wrapper directory inode) and the three quarantine generations
  (517 + 415 + 6 = 938). Reads the seven arms' array specs **untruncated** and confirms the arms run
  from a tree at `7ac0edec`, detached, porcelain 0. **Corrects** the producer's walltime envelope
  maximum from 253.5 to **300** (`boot5dG`, 100 × 3:00), which does not change the under-500 verdict.
  **Releases the dashboard lane** (`OI-175`, porcelain 726 → 725); does **not** release the deployment
  tree, move any gate, or decide the post-path `F-17(b)` capture, which is routed as `OI-178`.
# Orchestration router

This is a pointer-only active-tree router. It contains no scientific evidence or authorization.

## Current work

### ✅ §10.1 READY; GATE 1 PASSED ROUND 2, 2026-08-30 — submission remains a separate decision

- [`GATE1-VERDICT-ROUND2-20260830-k0-7ac0edec.md`](GATE1-VERDICT-ROUND2-20260830-k0-7ac0edec.md)
  — **GATE 1: PASS, 18 PASS / 0 FAIL / 0 NOT-EVALUABLE.** PB-25 pins the rubric and complete
  execution candidate by content digest. The additive recapture recorded the canonical checkout at
  726 untracked entries; independent grade-time remeasurement found the same HEAD, branch and
  **726 / 726 untracked / 0 modified**. The original pair remains the round-1 historical object.
  No compute was submitted, Gate 2 was not moved, and submission remains a separate decision.

- [`VERDICT-20260830-readiness-10-1-k0-7ac0edec.md`](VERDICT-20260830-readiness-10-1-k0-7ac0edec.md)
  — **READINESS-10-1: PASS.** F-7(b), F-8(b), and F-17(b) are present at `7ac0edec` and mapped by
  exact content identity to committed independent grades. The F-17 mapping carries an explicit
  self-reference disclosure: the readiness checker authored the prior Step-3 grade and verifies its
  existence/applicability rather than reissuing it.
- [`GATE1-VERDICT-20260830-k0-7ac0edec.md`](GATE1-VERDICT-20260830-k0-7ac0edec.md)
  — **ROUND 1 HISTORICAL BLOCK, 17 PASS / 1 FAIL / 0 NOT-EVALUABLE.** `F-17(a)` failed because the canonical
  operand records 722 untracked entries and the checkout now has 726; the four additions are the
  dashboard deployment after the operand completed. `OI-175` routes the replacement. No operand was
  retaken, no compute submitted, and Gate 2 remains unchanged.

### 🔒 DEPLOYED AND RE-FROZEN AT `7ac0edec`, 2026-08-30 — steps 1–2 historical filing; later grade above

- [`FREEZE-20260830-k0-deployment-7ac0edec.md`](FREEZE-20260830-k0-deployment-7ac0edec.md)
  — **THE DEPLOYED TREE `/pscratch/sd/j/josephrb/k0r2/clean` IS NOW FROZEN DETACHED AT
  `7ac0edecf45bf95ce0d2e2b6c2f8130a95b3994b` UNTIL THE NEW REHEARSAL'S F-1(b) IS PRODUCER-FILED.** No
  `checkout`, `reset`, `fetch`-and-merge, re-declaration or branch repoint in that directory, by any
  lane. **It expires when that F-1(b) filing is COMMITTED — not when jobs merely look terminal**, and
  it **cannot yet expire**: the rehearsal has not been submitted, so a zero-length job list is not a
  far end. Carries the **superseded-pin row** required by `OI-123` — old `aa67c426…`, new
  `7ac0edec…`, reason and authority — and records that the predecessor §7.0.19 freeze had **already
  expired** (`FINDING-20260829`, plus the landed producer F-1(b) at `aa67c426`), so this replaced a
  spent hold rather than breaking a live one. A **prose** hold: preventive by convention, detective by
  A-2(a) **and** A-2(f), **not** a mechanical guarantee — `.git` is `drwxrwx---` **by ruling**
  (§11.1.1), and ten `refs/tags/evidence/*` at non-pin commits leave `checkout <tag>` a live,
  never-exercised route. **Authorizes nothing.**

- [`DECLARATION-20260830-k0-deployment-7ac0edec.md`](DECLARATION-20260830-k0-deployment-7ac0edec.md)
  — **A-2(a)–(g) all MET at the new pin, each clause in its own invocation.** `820` tracked `.py`/`.sh`,
  listing sha256 `8d036d9466eaff6ad1f6b62231b09a1dd9798c095d2d0f84ea96ba01a51fc8ea`, declaration file
  `ca6a8f2b…` at `/pscratch/sd/j/josephrb/k0r2/declarations/7ac0edec/source-manifest.json`, porcelain
  **0** (and `--ignored` also 0), detached with **`refs/heads` empty and no remote**, `820 of 820`
  executing copies **CURRENT**. `782 → 820` is arithmetic: `aa67c426 → 7ac0edec` adds 221 tracked
  paths, deletes none, 38 of them `.py`/`.sh`. **The digest was predicted off-cluster from git objects
  BEFORE the deployment and its predictor has a positive control at `aa67c426` (782 / `fa3489e2…`)**,
  then confirmed by the deployed tree and again by the clone recovered from the new bundle — three
  object stores. Firing controls recorded for **(b)(c)(d)(e)(f)(g)**, including `--compare` against the
  superseded `aa67c426` declaration at **rc=3**. **Does NOT pass Gate 1, does NOT move Gate 2, and does
  NOT convert `F17B-REPAIRED-CHAIN: NOT FIT` into FIT** — it removes N1's *mechanism*; the verdict is
  step 3's, and the producing lane is ineligible to give it.

- [`state/RECEIPT-20260830-k0-deployment-and-freeze-bundle-7ac0edec.json`](state/RECEIPT-20260830-k0-deployment-and-freeze-bundle-7ac0edec.json)
  — the machine record: the six-part sequence with every command, new freeze ref
  `refs/tags/freeze/k0-7ac0edec` **in two repositories**, bundle
  `k0-clean-7ac0edec-20260829T233037Z.bundle` (82 761 577 B, sha256 `514bd46e…`), **exact-row**
  `list-heads` assertion, recovery **TESTED** by `clone --no-local` → `fsck` → detached checkout
  (porcelain 0, 1804 tracked, recovered clone re-measures 820 / `8d036d94…`), the mode round-trip, and
  the `.git` delta **partitioned rather than summarised** (23 → 24 writable files; the +1 is *named*:
  the new loose ref, with 0 writable files under `objects/`). Records that **no `.py`/`.sh` byte was
  touched** and that no in-place edit, copied file, `PYTHONPATH` substitution, `MNV_MEASURER` override
  or schema exception was used.

- [`state/RECEIPT-20260830-aa67c426-preservation-remeasurement.json`](state/RECEIPT-20260830-aa67c426-preservation-remeasurement.json)
  — **the precondition, and it PASSED before anything was made writable.** All six items of the
  2026-08-26 receipt's `reverification_recipe` re-run and MATCHED: bundle `8ce58391…` / 79 140 251 B,
  HEAD `aa67c426…`, ref set **exactly ten rows**, modes `dr-xr-x---` / `drwxrwx---`, pin in
  `list-heads`, recovery clone/fsck/checkout rc=0 with tree `60120bfb…` and porcelain 0. **AND ONE
  FINDING:** the receipt's `bundle.generated_from` path `/global/u2/j/josephrb/mnv-work/MINERvA-OmniFold`
  **no longer exists**, so the local-only tag `refs/tags/freeze/k0-aa67c426` was present in **no live
  cluster repository** — recoverability survived only because the recipe reads that ref out of the
  **bundle**. Re-created at the same commit in the canonical checkout (a restoration, **not** a
  repoint), and the generalisation is why the new freeze ref exists in two places.

### ✅ GATE 1 PASSES — round 9, 2026-08-23, 18 PASS / 0 FAIL / 0 NOT-EVALUABLE

- [`DECISION-20260824-joseph-deployment-freeze-until-f1b.md`](DECISION-20260824-joseph-deployment-freeze-until-f1b.md)
  — **⚠ SUPERSEDED 2026-08-30, AND IT HAD ALREADY EXPIRED BEFORE THAT. Everything below was true
  when written; do not read it as governing the deploy tree now.** Its expiry condition fired when
  the producer F-1(b) at `aa67c426` was filed, and the tree is now held by
  [`FREEZE-20260830-k0-deployment-7ac0edec.md`](FREEZE-20260830-k0-deployment-7ac0edec.md) at
  `7ac0edec…` instead — see that document's superseded-pin row for old value, new value, reason and
  authority (`OI-123`). Retained verbatim because it is the authority §7.0.19 was held against and
  because annotating in place is this router's convention. **The historical statement follows.**
  **THE DEPLOYED TREE IS FROZEN AT `aa67c426` UNTIL F-1(b) IS FILED.** No `checkout`, `reset`,
  `fetch`-and-merge, re-declaration or branch repoint in `/pscratch/sd/j/josephrb/k0r2/clean`, by any
  lane. **It expires when F-1(b) is TAKEN, not when the rehearsal "looks done"** — `combine`'s
  conjunctive `afterok` can read as queued while terminal. Contract **§7.0.19**. A **prose** hold:
  preventive by convention, detective by A-2(a), **not** a mechanical guarantee. Residual measured —
  10 `refs/tags/evidence/*` in that tree, none at the candidate, so `checkout <tag>` is still a live
  route. **Authorizes nothing.**

- [`DECISION-20260824-joseph-f6b-scoped-out-of-gate2.md`](DECISION-20260824-joseph-f6b-scoped-out-of-gate2.md)
  — **Joseph's ruling, and the authority §7.0.18 was held against. GATE 2 IS NINE CLAUSES:** F-1(b),
  F-2(b), F-3(b), F-4(b), F-5(b), F-7(b), F-8(b), F-17(b), F-18(b). **`F-6(b)` is NOT waived — it is
  mandatory under the separate leg-6 completion gate.** The ruling **authorizes nothing**: no leg 6, no
  adoption, no consumption, no member k≠0, no other clause relaxed. **A verdict recorded before
  2026-08-24 correctly grades ten; after, nine — say which.**

- [`DECISION-20260825-joseph-gate2-fail-and-four-rulings.md`](DECISION-20260825-joseph-gate2-fail-and-four-rulings.md)
  — **Joseph's ruling on run `k0-aa67c426-20260824T145751Z`: GATE 2 IS RECORDED FAIL, no partial
  credit.** Three clauses PASS (`F-1(b)`, `F-4(b)`, `F-18(b)`), **six are NOT DISCHARGED.** Strict
  §7.0.10 moves `F-2(b)`, `F-3(b)` and `F-5(b)` to NOT DISCHARGED because the grader measured what it
  graded — its measurements are **retained as verification evidence but cannot substitute for a
  missing producer filing.** `F-17(b)`'s `:1471` half is **impossible, not pending and not
  deferred**, and back-filling the pre-submission column is refused outright. `b2d7d4ca` is the
  **immutable** historical referent and must not be rewritten to make the rehearsal pass;
  `mnv-work/` is canonical **forward-only.** The prior instrument GRADE is **EXPIRED** (all three
  pinned digests moved), so the comparator that produced the filed record has never been graded, and
  the repaired one needs a new independent grade before it can support another Gate-2 filing —
  repairer, grader and spec author must be three different parties. **The ruling authorizes NO
  compute**, and confers no Gate-2 credit, no uncertainty adoption and no publication claim. **Scope
  is GBDT uncertainty, not PET** — an earlier PET framing was withdrawn by Joseph and survives only
  in the immutable message of `109bb130`; §0 of the document governs. Carries the defect ledger for the far-end path: two
  defects corrected in `38a7b16b` whose **old explanations are retracted, not preserved**, one
  irreparable unanchored "233 behind main" in `a3ed8631`, and the bounded dotless-pattern fail-open
  that leaves the filed record unaffected. `MANIFEST.tsv` drift is routed **out** of this verdict to
  F-14 / §7.0.7. **Three further rulings, 2026-08-25.** §11.1.1: **do NOT `chmod` the frozen
  deploy's `.git`** — verified not applied — because it is an accident guard the tree owner undoes in
  one command AND it breaks `git worktree add`, this repo's mandated audit mechanism; a **`git bundle`
  plus a recorded `sha256`** is ordered instead, since the property the freeze lacks is
  **detectability**, not resistance — **LANDED 2026-08-26** at
  `state/RECEIPT-20260826-k0-freeze-bundle-detectability.json` (bundle 79 140 251 B, sha256
  `8ce58391…`, recovery TESTED by `clone --no-local` → `fsck` → checkout, porcelain 0), and the
  postcondition earned its keep: a `--all` bundle would have verified, hashed, and **contained
  nothing to recover**, because that clone has no branch refs and none of its ten evidence tags
  contains the pin. §12.4: **the dead literal stays, NO CHANGE** — a typo'd
  whitelist row is **fail-closed UNDER-coverage, the direction OPPOSITE to D-3**, and suppresses
  nothing (measured: still exit **20 UNEXPECTED**); the proposed "unused entry ⇒ non-zero exit"
  middle option is **STRUCK as unsatisfiable**, because a correct entry is unused whenever the two
  documents agree, and the figure **"517 of the 773"** is **STRUCK as a population conflation**.
  §10.2: the register is **CLOSED for this pass**; the third independent origin against which Gate 2
  will be re-evaluated is the `codex-school` dispatch — **UNCLAIMED**, so not yet an origin — and
  there is **no compute until it lands on its own evidence.** **CLAIMED in writing 2026-08-26** by
  that Codex session; the UNCLAIMED reading is kept as the state as ruled on 08-25 and is not
  rewritten. A claim is not a delivery, not a grade, and not Gate-2 credit. **Next route, per Joseph 2026-08-26:**
  the assignment remains **publication close-out**; after the Gate-2 freeze receipt, re-read a fresh
  `LIVE-STATE.md` and the governing `OI-*` and resume the **routed** node, continuing the adopted
  scalar-5D covariance **adoption gate** if that is still critical path — not an assumed workstream,
  and not a reopening of completed or broadly scoped 5D work. The `MANIFEST` classification finding
  stays an **open referral, non-blocking** unless the routed gate explicitly depends on it.

- [`DECISION-20260828-joseph-f17b-four-surface-repair.md`](DECISION-20260828-joseph-f17b-four-surface-repair.md)
  — **Joseph approved the bounded four-surface F-17(b) repair.** The measurer now emits a real
  wall-clock interval and branch-or-detached identity, the comparator requires and carries both,
  the preserver is digest-bracketed across its own invocation, and a failed measurer short-circuits
  immediately. It records dated successors for both historical shell-script pins without editing
  either old value. **This authorizes the repair and fresh independent fixture-only grade only:** no
  far-end run, rehearsal, compute, covariance adoption, Gate-2 movement or publication claim.

- [`DISCIPLINE-20260825-f14-coupling-comparator-repair-lane.md`](DISCIPLINE-20260825-f14-coupling-comparator-repair-lane.md)
  — **One F-14 / §7.0.7 manifest-coupling omission by the independent comparator-repair lane,
  filed against itself.** `c8a29082` changed `compare_m1_m6.py` and `test_compare_m1_m6.py` without
  regenerating `MANIFEST.tsv` in the same commit; `generate_manifest.py --check` returns **rc=1 at
  `c8a29082`** in a clean detached worktree, porcelain 0, and rc=0 at `65f95600` — the shape that
  makes this class invisible, since the endpoint complies and the intermediate sha does not.
  **The excuse is removed by measurement:** the coupled single commit reaches rc=0 **in one pass**
  (unpushed probe `3ae2c6ba`), so committing sources first "so the counts describe a commit" was an
  error and not a trade-off — when all paths go in together the working tree *is* the commit.
  Two transferable findings: `generate_manifest.py`'s DIRTY warning **fires identically on correct
  procedure and on the hazard**, steering a reader into the violation; and the same-commit coupling
  for the manifest is a **composition** of F-14 with §7.0.7, stated in the sibling record's §1 and
  **not in §7.0.7's own text**, so a lane reading only the contract can satisfy its letter at the
  graded sha while breaking the coupling at every commit before it. The composition is **accepted,
  not rebutted.** **§5.1 records a SECOND omission by the same lane, `3dbca981`, committed while
  filing this very document** — rc=1 at that sha in a clean worktree — and it is the **same kind**
  of failure as the first. **§5.2 retracts this lane's own defence that the `intended`->`tracked`
  flip is irreducible for a new path: it is false.** `generate_manifest.py:92` reads the **INDEX**
  via `git ls-files`, so staging the new path before regenerating gives `tracked` in one pass —
  unpushed probe `435de9d3`, rc=0 in a clean worktree. **The two-commit shape is a convention, not
  a constraint**, and the cited precedent `109bb130` is itself **rc=1 at its own sha** though
  published as compliant. The defence was reached **without ever opening the code**, inferring
  necessity from convention and writing it in the grammar of a measurement. Both this lane's
  "irreducible" and the close-out lane's "compliant pair" are the **same unmeasured belief held
  from opposite sides**, each exonerating its own commits, untested until one lane was accused.
  Also corrected: a claim that nothing had absorbed this lane's instance, **false within minutes,
  replaced not softened** — both retractions share the tell that the claim was *comfortable*. **NOT** citable for any Gate-2 clause, nor for the D-3 repair, which stands as
  filed and remains **UNGRADED** under ruling 3.

- [`DISCIPLINE-20260825-f14-manifest-coupling-omissions.md`](DISCIPLINE-20260825-f14-manifest-coupling-omissions.md)
  — **Three F-14 / §7.0.7 manifest-coupling omissions by the publication close-out lane, filed
  against itself.** `30ede740`, `a3ed8631` and `38a7b16b` each moved a tracked path without
  regenerating `MANIFEST.tsv` in the same commit; `generate_manifest.py --check` returns **rc=1 at
  `38a7b16b`** in a clean detached worktree. **`a3ed8631` left an entire row absent, not a stale
  count** — the record it filed was invisible to the router at that commit. **Joseph named one
  commit; the measurement found three**, and all three are recorded so the enumeration is not
  partial. The keeper: the missing row was silently absorbed by the *independent grader's*
  regeneration in `a3000487`, so **a later "the manifest is current" says nothing about whether any
  particular commit complied** — compliance is measurable only at the commit, in a clean worktree,
  and only until someone else regenerates. Regeneration in `109bb130`/`dce8e8cc` **repairs the
  manifest state but does not erase the gap.** **NOT** citable for any Gate-2 clause, and explicitly
  does **not** account for the separate unattributed 23-row drift measured at `e428a645`.

- [`FINDING-20260824-gate2-preparation-and-four-open-rulings.md`](FINDING-20260824-gate2-preparation-and-four-open-rulings.md)
  — **Gate 2 is PREPARED and needs FOUR RULINGS before it can be graded.** Clause list derived
  independently as **ten** (F-1(b)…F-8(b), F-17(b), F-18(b)), agreeing with §7.0.5's arithmetic and
  confirming `F-3(b)` was missing from this router. **`F-6(b)` is structurally unsatisfiable inside the
  scope a Gate-1 PASS unlocks**, so Gate 2 cannot pass as written; F-4(b)'s population is undefined;
  F-7(b)'s exclusion half has no instrument (a §7.0.8 FAIL surface, not a pending input); F-1(b) must
  name `listing_sha256`, not a file digest. Instruments all verified non-vacuous, so Gate 2 is **not**
  tooling-blocked. **No clause is graded.**
- [`READING-ORDER-20260824-k0-package-annotations.md`](READING-ORDER-20260824-k0-package-annotations.md)
  — **READ FIRST if you are grading either gate.** The k=0 package was corrected by annotating in
  place, so its correctness depended on a reader finding all nine annotations across five files. This
  lists them in one reading order, marks the **4 BINDING** (they change what a clause requires) apart
  from the **5 HISTORICAL**, and names the four places a withdrawn sentence is printed *after* its own
  retraction — so a grep cannot tell asserted from withdrawn. **Router only; cite the artifact.**
  Records two live conditions: the contract's `main` and build-branch copies have **diverged again**
  (§7.0.17 is on `main` only, where `b2075558` had made them byte-identical), and the `[remedyA]`
  marker is `:711` in the canonical checkout and on `main` but `:787` on the build branch.

> **⚠ THIS HEADING IS A DATED SNAPSHOT, 2026-08-24.** Round 9's 18/0/0 was graded at `a54038b2` and
> **does not carry forward**: the OI-136 guard refused legs 5a/5b, the repaired candidate is
> `aa67c426`, and rounds 10–12 have since run (round 10 FAILED `F-1(a)` on a deployment excursion;
> round 11 stood at 16/2). **Gate 1 is not currently claimed passed on this branch's record**, and
> this section is behind `build-k0-execution-integrity`'s copy of this router. Read the round-10 packet
> and the 2026-08-24 receipt on that branch before treating any count here as current.
>
> **AND THE Gate-2 LIST BELOW IS INCOMPLETE — `F-3(b)` IS MISSING.** §7.0.5 makes **F-3 SPLIT**, with a
> post-rehearsal half: *"grep the job stdout → zero `--allow`; publish the command."* The enumeration
> below jumps `F-2(b)` to `F-4(b)`. §7.0.5's own arithmetic — **10 SPLIT criteria** — is the check:
> F-1…F-8, F-17, F-18. **A Gate-2 lane that inherits the list below grades nine clauses and misses
> one, and §F's no-partial-credit rule means the miss is silent.** Derive the list from §7.0.5's
> POST-REHEARSAL column, never from this router.

- [`GATE1-VERDICT-ROUND9-20260823-k0-execution-integrity.md`](GATE1-VERDICT-ROUND9-20260823-k0-execution-integrity.md)
  — **the terminal verdict.** sha256 `d5bfb863…`, 350 lines, landed byte-identical. Declared and
  deployed candidate `a54038b21fdebfc975bec452a05866ffa571a36c`.
  **IT UNLOCKS THE SEVEN JOBS OF LOGICAL LEGS 1–5 FOR k=0 AND NOTHING ELSE.** It is **not** a
  submission authorization — the grader states the decision to submit is Joseph's. Leg 6 stays gated
  by Amendment 1 §C, no member k≠0 is authorized, and Gate 2 still owes `F-1(b)`, `F-2(b)`,
  `F-4(b)`–`F-8(b)`, `F-17(b)`, `F-18(b)`.
- [`GATE1-VERDICT-ROUND8-…md`](GATE1-VERDICT-ROUND8-20260823-k0-execution-integrity.md) — 17/1,
  `F-2(a)` and `F-17(a)` closed here; failed `F-1(a)`.
- [`GATE1-VERDICT-ROUND7-…md`](GATE1-VERDICT-ROUND7-20260823-k0-execution-integrity.md) — 17/1,
  failed `F-17(a)`. **Landed now rather than earlier**: rounds 7 and 8 were outside the repo, so the
  passing verdict cited artifacts a reader could not reach.
- [`DECLARATION-20260823-k0-candidate-sha.md`](DECLARATION-20260823-k0-candidate-sha.md) — the
  A-2(a)–(g) filing the pass rests on. **780** tracked source files, listing sha256 `1b45da55…`.

- [`DEFECT-20260825-generate-manifest-dirty-warning-nondiscriminating.md`](DEFECT-20260825-generate-manifest-dirty-warning-nondiscriminating.md)
  — **`generate_manifest.py`'s DIRTY warning fires identically on correct procedure and on the
  hazard, and its advice is FALSE in the one case F-14 requires.** Controls, only staged-ness
  varying: clean tree **silent** (so the instrument is not always-on), staged edit and unstaged edit
  give **byte-identical warning text and equal rc**. A lane cannot use this output to tell whether it
  is about to break the F-14 coupling. Measured consequence: six coupling omissions across two lanes
  in one day, one of them with the warning's own sentence recorded as the reasoning. The
  discriminating fact **already exists and is discarded** at `generate_manifest.py:328`, where the
  porcelain `XY` code is dropped in the same expression that builds the dirty set. A repair must add
  an arm that FIRES on `' M'`, stays SILENT on `'M '`, and covers the opposite direction on `'MM'` —
  **corrected 2026-08-25**: the third arm previously demanded "staged but not committed", a **future
  fact no implementation inside the tool can observe**, and was therefore unsatisfiable. **In scope,
  same family:** default-mode `--check` silently absorbs another lane's untracked files (rc=1, 537
  rows) while `--committed-only` gives rc=0, 533 — that rc=1 is the instrument reporting and must not
  be "repaired". **Distinguish it from a real one:** hours later `e30dbd45` *committed* those four
  paths without regenerating, so `main` went rc=1 in **both** modes for a genuinely different reason
  (a third lane's F-14 omission, measured at
  `DISCIPLINE-20260825-f14-manifest-coupling-omissions.md` §4.2 and regenerated here). The two are
  indistinguishable from the exit status alone. **Re-measured at the tip 2026-08-26: `fd58e71b` is
  rc=0 in BOTH modes, rows=537, porcelain 0** — `aaed392d` was rc=1 *when it was the tip*, and any
  precondition citing the older green `17b79fca` result is **stale across the failing interval**.
  **§6 was UNCLAIMED** as ruled on 08-25: a handoff, not a delivery, and not citable as coverage or
  as an independent origin until an implementer acknowledged it. **It was CLAIMED in writing on
  2026-08-26** by the `codex-school` Codex session, so that condition is now met and the historical
  clause is retained rather than rewritten. **It was then DELIVERED by that implementer on
  2026-08-26 and remains UNGRADED**; §7 carries the baseline re-measurement, implementation, and
  controls. Delivery is not a grade and supplies no Gate-2 credit. **§6 DISPATCH (Joseph,
  2026-08-25): the independent implementer is `codex-school`**,
  re-deriving from this record and the artifacts and **not** from the close-out lane's reasoning or
  the advisory lane's analysis; the grader must be a third party. **The publication close-out lane is
  disqualified from BOTH** — it authored §4, and §4 is a *specification*, which is the prong ruling 3
  turns on (an earlier version of that section wrongly cleared itself on the tool-authorship prong).
  **NOT** citable for any Gate-2 clause, **does not alter Gate 2's FAIL**, is not part of the D-3
  repair, and excuses no omission.
### ⚠ ROUND 11 — Gate 1 at **16 PASS / 2 FAIL**; F-1(a), F-9, F-12 CLOSED; F-8(a) and F-17(a) filed and awaiting grade

- [`PACKET-20260823-round10-oi136-runtime-violation-repair.md`](PACKET-20260823-round10-oi136-runtime-violation-repair.md)
  — **round 9's 18/0/0 at `a54038b2` is historically valid and does NOT carry forward.** The OI-136
  guard refused legs 5a/5b before any work ran. Repaired candidate **`aa67c426`**, deployed,
  `porcelain 0`, 0 writable. Census **52 / 2 / 1** (53 is the PRE-repair figure). **Gate 1 is NOT claimed passed.**
- [`DECLARATION-20260823-k0-candidate-aa67c426.md`](DECLARATION-20260823-k0-candidate-aa67c426.md)
  — A-2(a)–(g) all MET at the new sha; 782 files, listing `fa3489e2…`. **§6 records the deployment
  excursion**: the declaration commit was deployed on top of the candidate, round 10 failed `F-1(a)`
  on it, and the deployment was reset to the declared sha on 2026-08-24. §6.3's branch-ref sentence is
  annotated as since-falsified; §6.8 transcribes the tree's reflog (18 advances in two days) because it
  expires; §6.9 records the hardening and what it does **not** close.
- [`RECEIPT-20260824-k0-f8a-f9-f12-f17a-filings.md`](RECEIPT-20260824-k0-f8a-f9-f12-f17a-filings.md)
  — **F-8(a), F-9, F-12 and F-17(a) measured at `aa67c426`.** P-6's launcher grep with its full output
  raw and collapsed (171/114; 101/27/**12**, reconciling to the contract's nine plus three apparatus
  tools); P-5's blind spots; the import closure **18 module-level / 20 any-depth / 2 hazards** with
  both index scopes named, replacing an unpublished "15"; N-1's three arms with exit statuses filed;
  M-1…M-6 on **both** trees with one identified difference. **Ten findings, four against this lane's
  own work.** Builder-produced evidence — **it grades nothing**.



- **ROUND 2 COMPLETED 374 OF 374 WITH ZERO FAILURES, 2026-09-01:**
  [`RECORD-20260901-k0r2-round2-outcome.md`](RECORD-20260901-k0r2-round2-outcome.md) — queue empty at
  `08:57:51Z` after ~36 h. **374 distinct task identities COMPLETED, 0 FAILED, 0 CANCELLED**, all seven
  arms at full declared population. Round 1 of the same run died with six tasks in 8–15 s on `OI-179`;
  the only change was one exported variable. **Products verified READABLE, not merely marked**: 143
  `.done`, and 185 `.npz` opened with every member read, 0 unreadable — though the first read reported
  two failures and **the reader was wrong, not the files** (`allow_pickle=False` is a numpy default;
  all 61 `uq_5d` products carry object arrays). **The canonical operand never moved for the entire
  run** — porcelain 726 / digest `d429f0f3` at submission and identically 36 h later — and the deploy
  tree stayed frozen at `7ac0edec`, porcelain 0. **§5 says outright that a completed run is not a
  passed gate:** Gate 2 remains **FAIL** on six clauses, no cause is discharged, nothing is adopted,
  counts stay CAND `1 of 7` / QUOTED `0 of 7`. Supplies the n=2 complete populations that make
  `OI-177` ratifiable — and kills the 40 CPU-h figure the amendment first proposed, since arm 5
  measured **49.11**.
- **CAUSE 3's `M(ii)` PREDECLARED — THRESHOLD FIXED FROM PUBLICATION PRECISION, BEFORE ANY NUMBER EXISTS, 2026-09-01:**
  [`PREDECLARE-20260901-cause3-mii-estimator-seed-magnitude.md`](PREDECLARE-20260901-cause3-mii-estimator-seed-magnitude.md)
  — `CRITERIA` flags cause 3's `M(ii)` UNRESOLVED and rules `\gbdtAiEstTrace` CANNOT SERVE on footing (`:194`), so the
  magnitude needs its own measurement on the candidate's bkgaware, post-J28 footing. **`M(i)` is NOT re-opened: it is
  already satisfied**, the candidate's `upstream_fixed_seed_null_norm` `5.8223488501140625e-50` against `tol 1e-12`.
  **THE ACCEPTANCE THRESHOLD IS SET, AND IT IS PRINCIPLED RATHER THAN TUNED:** `f_agg ≤ 4.15%` and `f_med ≤ 2.74%`,
  derived from the precision at which the affected quantities are already PRINTED — an omitted independent contribution
  `S` enters in quadrature, and requiring `U' − U` to stay under half the last printed unit gives
  `S/U ≤ sqrt(2δ + δ²)`. **Re-derived independently at review: `5.81` at 3 s.f. → `4.1496%`, `13.36` at 4 s.f. →
  `2.7361%`, reproducing both.** The boundary is a property of how the numbers are printed, not of what the measurement
  will return, which is what makes it non-tuned. **It also argues F7's floor rule does NOT transfer** — under a true zero
  seed response `C_seed` is zero, so `sqrt(Tr C)/sqrt(12)` is no noise floor for it and would import systematic
  covariance into an estimator-noise test. Six exhaustive branches including `NOT MET — BOTH`. Cost re-derived:
  `0.667` GPU + `0.050` CPU task-hours, inside the ratified arm-1 (20 GPU) and arm-7 (5 CPU) envelopes under
  `DECISION-20260901-joseph-delegated-ceiling-unit-is-task-hours.md`. **Declares only; measures nothing, and the scan
  had not run when this landed.**
- **CAUSE 7 FINALLY HAS DISCHARGE CRITERIA — DRAFTED, NOTHING GRADED, 2026-09-01:**
  [`PREDECLARE-20260901-cause7-discharge-criteria.md`](PREDECLARE-20260901-cause7-discharge-criteria.md)
  — `CRITERIA-20260811` is titled for causes 1, 2, 3, 4 and 6; **cause 7 had none at all**, appearing only in its §4.1 as
  a finding that its recorded discharge is for a DIFFERENT PRODUCT. Drafted under Joseph's 2026-09-01 authorization
  (*"I authorize you spend the hours and drafting to investigate and fix the causes"*). **Four legs, every one OPEN;
  the word MET does not appear in the document.** §0 separates FOUR artifact names so the FPS object cause 7 was
  discharged against (266 bins, job `56431823`, `OI-5` resolving it FPS-only) cannot be substituted for the 5D
  candidate. **The defect IS on the candidate's path** — `adopt_unified_5d.py:17-20` states the nine detector-lateral
  bands *"are left untouched — the throw does not cover them"*, so the laterals ride through inside
  `hCov_combined5d_total`. **THE M THRESHOLD IS DELIBERATELY LEFT OPEN FOR JOSEPH**, in the form
  `nd-unfolding/uq_math.py:128-137` uses for `F7_FLOOR_MULTIPLE`: no pre-observation materiality rule exists and the
  ratio is diagnostic and unbounded, so *any* cutoff written now would be tuned to already-visible data. He must either
  rule a principled threshold before M is graded or rule M measurement-only. Grades nothing, discharges nothing,
  adopts nothing, moves no gate.
- **THE SCALAR-5D COVARIANCE IS A CLAIM UPGRADE — AND THE DEPENDENCY IS KEPT BY CHOICE, 2026-09-01:**
  [`DECISION-20260901-joseph-oi187-upgrade-not-blocker.md`](DECISION-20260901-joseph-oi187-upgrade-not-blocker.md)
  — Joseph, his own turn: ***"Yes it's an upgrade, keep the covariance work going. The intention is to be done with the
  uncertainties before publication"***. **(a)** The quarantine gates ONE CLAIM UPGRADE — the joint high-`E_avail`/high-`W`
  generator deficit from central value to significance — **not the Letter as scoped**: `paper_body.tex:145-148` says
  *"Every non-two-dimensional result in this Letter is a central value… no superseded or historical covariance is used
  here."* **(b)** The dependency is nevertheless RETAINED; the covariance work is not stood down. **Both halves travel
  together** — "upgrade" naturally misreads as "can slip", and it cannot slip by default. What changes is the KIND of
  dependency: **elective, not structural**. The gap that would have collapsed (a): the Letter DOES quote a covariance at
  `paper_body.tex:53-55`, and it is `AGENTS.md:25`'s **VALIDATED** 2D standalone construction — every object the Letter
  quotes is VALIDATED, every quarantined object is one it declines to use. Found by the `claude-school` lane, re-read
  here. **Deliberately does NOT settle** whether `OI-172`'s note obligation reaches the Letter — that is ruled separately
  in `OI-187`'s row on a CODE-PATH argument, because this lane's artifact-scope reasoning was true but not sufficient.
- **PSCRATCH READ STALLS MAKE `A-2(b)` UNMEASURABLE — THE REDEPLOY IS BLOCKED BY A FILESYSTEM, NOT A DECISION, 2026-09-01:**
  [`FINDING-20260901-pscratch-read-stalls-block-a2b.md`](FINDING-20260901-pscratch-read-stalls-block-a2b.md)
  — `git status --porcelain` **does not return** on either cluster checkout, while `find` (1803 files), `git ls-files`
  (1804), `rev-parse`, `cat-file` and all metadata are **instant**. A complete per-file sweep — **1803 attempts,
  terminal marker written, so NOT a blind result** — found **10 files (0.55%)** whose content reads time out, ordinary
  small text files across four unrelated directories. **INTERMITTENT, and an earlier reading of it as a dead Lustre
  target is CORRECTED here:** two of the ten later read clean twice. **And it is worsening** — the sweep got `rc=124`
  where the retest gets no return at all, i.e. **uninterruptible sleep, where `timeout` cannot interrupt its own
  child**; that is also what has held another lane's processes for **2 h 30 m+**. **THE CONSEQUENCE:** `A-2(b)` is
  `dirty_count` from exactly that command, so round-2 `F-1(b)` cannot be filed by the precedent route, so
  `FREEZE-20260830-k0-deployment-7ac0edec.md` §1 cannot expire, so the authorized redeploy cannot proceed. **No
  substitute measurement is offered and none should be improvised.** §5: three of the ten are executable science
  inputs, so the tree is **unsafe to launch from** independently of the freeze. §6 carries the method caution both
  lanes nearly fell for — **an empty sweep result is not a negative result** — with the two rules that follow. Already
  banked and not to be redone: A-2(a) is taken (raw sha in `.git/HEAD`, DETACHED), and bundle-alone recovery of
  `7ac0edec` passes **all six** declared checks. Authorizes nothing; **Gate 2 remains FAIL**.
- **THE REDEPLOY'S PRECONDITION DELTA, AND A CORRECTION ON WHEN THE OTHER EIGHT ARMS BREAK, 2026-09-01:**
  [`FINDING-20260901-k0r2-redeploy-precondition-delta.md`](FINDING-20260901-k0r2-redeploy-precondition-delta.md)
  — the measurement `DECISION-20260901-joseph-authorizes-k0r2-redeploy.md` §2's *"and reconcile the other issues"*
  obliges. **All eight k=0 launchers gained one fail-closed requirement at `865b42d7`** — `MNV_ENV_PROVENANCE`, refusing
  both unset AND set-but-empty (`:?`), needing a baseline emitted by `mnv_env_provenance.py --emit` **before** the first
  `sbatch`, with no default by design. Per-launcher line numbers in §2; **`sbatch_finalize_5d_bkgaware_gpu.sh` is in the
  set, so leg 6's preconditions move too.** **THE CORRECTION:** this lane had reported a **submit-time** refusal. Wrong,
  and wrong in the direction that UNDERSTATES the hazard — `sbatch` does not evaluate the body, so a launcher with the
  variable unset **submits cleanly and every task then dies on the node**, `OI-179` round 1's exact shape. §3's residual
  gap is stated rather than left implied: **no submit-time gate exists**, confirmed with the enforcing lane; *"defect 3
  is enforced"* must not be read as "caught before jobs queue". §4 resolves eight of the ninth launcher's nine `MNV_*`
  values from `submission-environment-round2.txt` — the values the 374/374 run actually used, not proposals — and flags
  that **the same file's `MNV_EST_SEED_OFFSET=0` line is a TRAP**: the estimator-seed launcher refuses at `:154-157` if
  that variable is set at all. §5 keeps three items genuinely OPEN as rulings, not lookups: the `RUN_ID` and its two
  run-scoped paths; what `MNV_ENV_PROVENANCE` points at, since round 2 used a hand-written file and `--emit` did not yet
  exist; and whether a ninth arm may share the completed run's `RUN_ID` at all. §6 is marked SECOND-HAND — recovered
  from a credit-exhausted delegate's log, re-measure before citing. Authorizes no submission; **Gate 2 remains FAIL**.
- **JOSEPH AUTHORIZES THE k=0 REDEPLOY `7ac0edec` → `main`, AND THE ORDER IS PART OF THE RULING, 2026-09-01:**
  [`DECISION-20260901-joseph-authorizes-k0r2-redeploy.md`](DECISION-20260901-joseph-authorizes-k0r2-redeploy.md)
  — Joseph, his own turn: ***"Yes redeploy it and reconcile the other issues"***. **The deployed tree
  `/pscratch/sd/j/josephrb/k0r2/clean` may advance from `7ac0edec` to ONE NAMED COMMIT** — a sha, never the definite
  description *"current `main`"*, which re-points the moment `main` moves (it moved `83666a09`→`050dbb72` inside one
  peer session). **THE ORDERING CONSTRAINT IS PART OF THE RULING AND MUST TRAVEL WITH IT:**
  `FREEZE-20260830-k0-deployment-7ac0edec.md` §1 is **LIVE** — its expiry is *"when that rehearsal's F-1(b) producer
  filing is committed — not when its jobs merely look terminal"*, and **no round-2 filing exists**
  (`RECEIPT-20260830-k0-f1b-producer-filing.md` is scoped by its own box to `aa67c426`). So the round-2 F-1(b) is filed
  FIRST, the freeze expires on its own terms, and only then does the authorization take effect. **This record must NOT
  be cited to cut a live hold short**, nor to refuse a future Joseph-level `OI-123` supersession — the independently
  checked limb is *"no COMMITTED route existed at the time of the check"*, deliberately narrower than "nothing else can
  expire it". Rationale: moving first destroys the far end of a completed **374/374, zero-failure, ~36 h** run,
  recoverable only by re-running everything. §5a carries the preservation prerequisites MEASURED read-only before the
  move — freeze ref present in BOTH repos, bundle `82,761,577 B` / `514bd46e…`, `list-heads` exact-row count 1 — and the
  terminality measurement with its covering control (374 measured reconciles with 374 declared, closing the `sacct -X`
  promoted-task hazard). §7 states plainly that **this record goes back in front of him**, because a lane that receives
  an authorization and rewrites its timing has ratified its own drafting. Authorizes NO submission, no leg 6, no M(ii),
  no adoption; **Gate 2 remains FAIL**.
- **JOSEPH RULES THE TWO MAGNITUDE LEGS — `OI-172` AND `OI-173`, 2026-09-01:**
  [`DECISION-20260901-joseph-oi172-oi173-magnitude-legs.md`](DECISION-20260901-joseph-oi172-oi173-magnitude-legs.md)
  — Joseph in his own turn, directly, not relayed: ***"Okay I agree with your recommendations, I authorize you spend the
  hours and drafting to investigate and fix the causes"***. **Ruling 1 (`OI-172`, cause 1's `M`): MATERIAL ENOUGH TO NEED
  ITS OWN STATEMENT IN THE NOTE — so CAUSE 1 DOES NOT CLOSE and the note acquires a new obligation.** The unfavourable
  branch, which the row named first. Grounds: the trace moves `3.1%`/`5.9%` while per-band ratios run median `2.0261`,
  p90 `4.3256`, max `5.8024`; the effect CHANGES SIGN (`MaCCQE` ep0 `0.6377`, `MaRES` ep1 `0.6111` are understated, so a
  consumer assuming conservatism is wrong on those bands); and the supporting measurement is diagonal-only with `Flux`,
  `2p2h` and `__Normalization_flat` excluded. **Ruling 2 (`OI-173`, cause 4's `M`): specify `M` against the class of
  object the defect actually REACHED — the reported ratio, not the stored covariance — and if the printed `jit_trace` is
  unrecoverable then `M` is NOT MET (unmeasured), NOT `N/A`.** Follows `SCOREBOARD` §2c's rule *"do not let measurability
  choose the specification"*, and explicitly REFUSES the available `N/A`-on-the-merits shortcut, whose payoff would be its
  own premise. **The recommendations are this lane's and are restated verbatim in the record so nobody mistakes them for
  his reasoning; he adopted the conclusions.** Discharges nothing, adopts nothing, moves no gate; cause 4's `M` becomes
  SPECIFIED, not satisfied, and may yet grade NOT MET.
- **JOSEPH RE-ISSUES `OI-173` — THE `M` REFERENT IS THE STAMPED CANDIDATE, 2026-09-02:**
  [`DECISION-20260902-joseph-rules-oi173-referent-is-the-candidate.md`](DECISION-20260902-joseph-rules-oi173-referent-is-the-candidate.md)
  — Joseph in his own turn, directly, not relayed: ***"okay do c"***, where `(c)` is the `5d` lane's *"`M` is specified
  against the reported ratio of the STAMPED CANDIDATE"*. **Supersedes the referent of Ruling 2 above and NOTHING ELSE of
  it** — the class is still the reported ratio, the `N/A` shortcut is still REFUSED, no recomputation is authorized.
  **He authorized a different branch first and it is recorded rather than omitted:** *"Can you do (a)?"* aimed `M` at the
  ADOPTED artifact; implementation halted on the `5d` objection and nothing under `(a)` was ever committed. **Why `(a)`
  was wrong — TWO CORRECT RULINGS COMPOSING INTO A DEFECT:** `DECISION-20260831` §1 fixes the SUBJECT (the stamped
  candidate), Ruling 2 fixes the REFERENT CLASS, and the pair left `M` pointed at an object the framework does not grade.
  Three objects existed and the choice put to him had two. **The measurement, replacing a refuted one:** no committed
  revision of `unified_throw_cov.py` holds BOTH the jitter print and the J28 flux fix — `081ae4ac` modifies that file
  itself with `grep -c` `0`, and `merge-base --is-ancestor 07c18aee 081ae4ac` is TRUE — so a tree old enough to print the
  floor cannot produce the candidate's input. The earlier stamp-based route is REFUTED because `git log -S` dates the
  oldest COMMIT, not the oldest EXISTENCE (`VALIDATION_LEDGER.md:484`). **THE GRADE IS DERIVED AND ROUTED, NOT APPLIED:**
  the chain yields `NOT MET (unmeasured)`, but this lane took the measurement so `BEN-381` routes the regrade; the cell
  stays `OPEN`, counts hold at CAND `1 of 7` / QUOTED `0 of 7`, **Gate 2 remains FAIL**, and Reading B is left undisposed.
  **A covering log sweep must NOT be launched for this.**
- **THE SUPPORTING ANALYSIS FOR THE `OI-173` RE-ISSUE — the `5d` lane's, adopted unchanged, 2026-09-02:**
  [`PROPOSAL-20260902-oi173-reissue-cause4-M-referent.md`](PROPOSAL-20260902-oi173-reissue-cause4-M-referent.md)
  — filed under its own lane's authorship because it reached the third-object problem independently and first, and
  because its **drafting history is the useful artifact**: §3a retracts that lane's stamp inference on the other lane's
  counterexample, §3b restores the conclusion on the flux-fix route with that lane's same-file strengthening, and the
  chain paragraph retracts a universal on the near-miss at `adopt_unified_5d.py:158-160,177-178` (a sqrt-trace ratio IS
  printed and persisted downstream — a different quantity, adopted-combined across inflation, with no `jit_trace` in its
  path). Three corrections across two lanes, each retracted in place rather than deleted. §5 records BOTH live readings
  at their real strength, including the one neither lane could refute. **Grades nothing and moves no cell.**
- **JOSEPH OVERRIDES THE INDEPENDENCE OBJECTION; THE CAND `M` CELL IS ANNOTATED, 2026-09-02:**
  [`DECISION-20260902-joseph-applies-oi173-cause4-m.md`](DECISION-20260902-joseph-applies-oi173-cause4-m.md)
  — Joseph, directly to the `5d` lane with the two-lane consensus and its objection in front of him: ***"apply it"***.
  **The lanes had declined on INDEPENDENCE, NOT authority** — `BEN-381` is a property of who measured, and being named
  by the authority does not confer it; it names the two parties who lack it. **The disclosure is on the record rather
  than left to be discovered:** the applying lane verified the same-file dependency the argument turns on, so the grade
  is weaker for who applied it and a reader should discount it on that ground. **WHAT MOVED — one annotation, at
  `SCOREBOARD-20260817-quarantine-seven-causes.md:78`, CAND column only.** The token stays **`OPEN`**:
  `CRITERIA-20260811:246` defines `MET`/`OPEN`/`UNRESOLVED`, Joseph's *"`NOT MET` (unmeasured)"* is not among them, and
  a fourth token is a `§0` change and his call. Discharge needs four `MET`s either way, so nothing rides on the token
  but meaning — and `OPEN` refuses `N/A` exactly as `NOT MET` would. **What the cell gains is the PERMANENCE and its
  ground:** no **committed** revision of `unified_throw_cov.py` holds both the jitter print and the flux fix, so no
  revision able to produce CAND's fluxfix input could print the unified/block ratio. **A VOCABULARY GAP IS FLAGGED, NOT
  PAPERED OVER** — `OPEN` normally means *awaiting work* and is here annotated to mean *permanently unmeetable*.
  **THIS SUPERSEDES A CONSIDERED REFUSAL, not an empty cell:** `SCOREBOARD` §3 (`:568`) declined this exact cell at
  `:670` — *"the cell stays `OPEN` and I am declining to move it in either direction"* — on a SEARCH-BASED null
  (`:606`/`:609`). What changed is the GROUND, from an empty search to committed bytes with a positive control, so the
  refusal is superseded on evidence rather than overruled on authority. **A NEAR-MISS CAUGHT BY THE `-38` LANE:** `5d`
  had claimed `CRITERIA-20260811:257` in writing, but `:244` reads *"Honest state per cause, **for X**"* and `:341`
  carves out only the `P` legs — that cell is X's, and editing it would have been the
  adopted-artifact-versus-candidate error one layer down, the same error the `OI-173` re-issue existed to correct.
  **AND THE TWO CONTROL DOCUMENTS DISAGREE ABOUT THIS LEG:** `CRITERIA:257` grades it `UNRESOLVED`, `SCOREBOARD:78`
  grades it `OPEN`, and `:246` makes those distinct. **Left standing**, filed as a finding owned by neither lane.
  **Counts unchanged:** CAND `1 of 7`, QUOTED `0 of 7`; **Gate 2 FAIL**; cause 4's verdict untouched and still jointly
  gated on the provenance residual; the historical-ratio reading still undisposed; nothing adopted, `values.tex`
  untouched.

- **THE TWO-LANE CONSENSUS ON CAUSE 4's `M`, AND ITS SUPERSESSION WITHIN THE HOUR, 2026-09-02:**
  [`DECISION-20260902-two-lane-consensus-cause4-M-and-its-supersession.md`](DECISION-20260902-two-lane-consensus-cause4-M-and-its-supersession.md)
  — filed under Joseph's **PROSPECTIVE** approval, *"I want you guys to come to a consensus and I approve that
  resolution"*, which is flagged at the top of the record because **he approved content that did not exist when he
  approved it**: every word is the two lanes' and none of it is his reasoning. **§3.1 IS SUPERSEDED IN FACT** — the
  consensus was that the cell does not move, he overrode within the hour, and the record is filed with the reversal
  visible rather than rewritten. **On `BEN-381`:** he HAD the authority and this record must not be cited for saying
  otherwise; the lanes declined on **independence**, which is a property of who measured and cannot be conferred
  retroactively — *he MAY, and the lanes said he SHOULD NOT*. He then overrode it knowingly, so the grade is weaker for
  having been applied by a measuring lane. **Carries the four binding constraints on any future application** — the
  vocabulary limit; that `CRITERIA` §3's table is **X's** (`:244`, `:341`) so the candidate cell is `SCOREBOARD:78`;
  that the verdict is jointly gated and does not clear on `M`; and the `5d` lane's artifact-bound-versus-artifact-free
  argument **recorded and deliberately not applied**. **§5 is a FINDING owned by neither lane:** the grading scheme is
  declared at three tokens (`CRITERIA:246`) and is running six — `PARTIAL` (5 uses) was never declared and `N/A` appears
  in three spellings — while **no code parses any of them**, so the scheme is purely communicative and the
  `CRITERIA:257`-versus-`SCOREBOARD:78` split on one leg stands unresolved. Discharges nothing, moves no cell, changes
  no count; **Gate 2 remains FAIL**.
- **THE `P` LEG IS ALREADY SATISFIED AND `M` IS THE BLOCKER — §4.2 DISSOLVED, 2026-09-01:**
  [`FINDING-20260901-p-leg-status-measured-against-the-candidate.md`](FINDING-20260901-p-leg-status-measured-against-the-candidate.md)
  — `CRITERIA-20260811` §4.2 says the `P` leg of causes 1–4 is *"currently unsatisfiable from the repository"* and
  proposes its own remedy: *"the cheap fix is a receipt, not a re-run."* **That receipt was written 2026-08-17 and is
  committed; nobody marked §4.2 satisfied.** Measured off three tracked, predeclared receipts: cause 1 `P` **MET**
  (branch `C1`, per-band census, `Flux` exactly 100 contiguous); causes 3 and 4 `P` **MET FOR THE CANDIDATE**
  (branch `S1`, both arms carrying all six self-checked stamps and all three `upstream_*` values, zero mismatches)
  **while both July negative controls returned every stamp ABSENT** — `(cause × artifact)` scoping working as §0
  describes. **Neither receipt discharges anything, and both say the blocker is `M` in their own words.** So
  `OI-172` and `OI-173` are not parallel blockers but the `M` leg itself, confirming the `claude-school` lane's
  ordering over this lane's. Remaining: cause 1 → `OI-172` (free); cause 3 → `M(ii)` needs its own measurement,
  **~1 GPU-node-hour**; cause 4 → `OI-173` (free); **cause 7 has NO criteria at all** and needs them written.
- **THE F7 PREDECLARED TEST, MEASURED ON THE CANDIDATE — MEAN-CENTERING ALONE IS DISQUALIFIED THERE TOO, 2026-09-01:**
  [`FINDING-20260901-f7-floor-ratio-and-seed-pull-measured.md`](FINDING-20260901-f7-floor-ratio-and-seed-pull-measured.md)
  — Run to settle whether [`BRIEF-20260901-greif-fps-thesis-implications-for-gbdt5d.md`](BRIEF-20260901-greif-fps-thesis-implications-for-gbdt5d.md)
  §4 opens a route to redefining the 5D central value as an ensemble mean. **It does not.** `uq_math.py:119-138`
  carries the F7 rule PREDECLARED in `CORRECTED_UQ_PRODUCTION_STATUS.md` before the data: `||mean_shift||` against
  the sampling floor `sqrt(Tr C)/sqrt(N)`, threshold `F7_FLOOR_MULTIPLE = 2.0`. **Measured on
  `stamped_bkgaware_meancentered_20260812.root`'s stamps: `4.510x` the floor, `f7_cv_centered_required` = `True`**
  — *corrected same day by the `claude-school` lane: `4.510x` pairs the UPSTREAM shift with the candidate's
  `sqrt_tr_new`, so it is not like-for-like; the adopted-ensemble ratio is `VALIDATION_LEDGER.md:390` VL33's
  **`5.3478x`**, and the candidate carries no mean shift of its own. Verdict unchanged: `5.3478 > 4.8288 > 4.510 > 2.0`*
  — so the disqualification covers the CANDIDATE, not only the July artifact, which independently supports cause 2's
  2026-08-12 discharge having REQUIRED the CV-centered variant. **The Greif analogy fails at the ensembles:** he centers
  over a bootstrap/seed family, our shift is against the joint **systematic throw** family
  (`unified_throw_cov.py:288`), and averaging systematic throws into a central value is not what the thesis does.
  A 24-member seed-ensemble pull (median `0.588` vs the 3D reference `0.63`, on a `cv>0` support of exactly `10694`)
  **removes ML stochasticity as the offset's cause rather than supporting the redefinition.** Scope limits stated:
  `ssplit5d` varies the train/test split ONLY (`estimator_seed=42` throughout), so no scan anywhere varies both; these
  are REHEARSAL products, measurable but not quotable. **Records a statistic deliberately NOT computed** — an ad-hoc
  per-bin throw pull — because a predeclared test governs and choosing a statistic after seeing the data is the
  failure mode this campaign files against others. **Corrects this lane's own withdrawn `28%`-of-`sqrt(Tr C)` heuristic,
  which used the wrong denominator and pointed the opposite way.** Discharges nothing, moves no gate; `OI-186` files a
  `7%` gap between `uq_math`'s comment and the artifact's stamps.
- **THE DELEGATED COMPUTE CEILING IS DENOMINATED IN TASK-HOURS, 2026-09-01:**
  [`DECISION-20260901-joseph-delegated-ceiling-unit-is-task-hours.md`](DECISION-20260901-joseph-delegated-ceiling-unit-is-task-hours.md)
  — Joseph, in his own turn, asked directly which unit the standing per-arm ceiling uses: ***"It is task
  hours"***. The `500 GPU-h / 500 CPU-h` delegation was written unqualified, and arm 5 of the k=0 round-2
  rehearsal reconciles **only under one reading**: `49.11` task-hours (elapsed summed over 40 tasks) versus
  `2455.51` core-hours at `AllocCPUS=50`. **Under task-hours every one of the seven arms is far inside 500,
  the largest being 49.11**; under core-hours `uthrow5d_runF` and `uthrow5d_block` would each have breached
  the CPU delegation, by ~4.9× and ~2.7×. **They did not — the ruling resolves the wording in the direction
  the campaign's own arithmetic already assumed.** The distinction was known and simply never reached the
  delegation sentence: `SCOREBOARD-20260817:223` writes *"`55.182` CPU task-hours (`2759.1` CPU-core-hours)"*
  explicitly. **RATIFIES NOTHING** — `OI-177` stays OPEN and unsigned (§3's 40 CPU-h for arm 5 is dead on the
  49.11 actual; §3b's 60 awaits his signature), no gate moves, nothing is adopted, counts hold at CAND
  `1 of 7` / QUOTED `0 of 7`. **Carries one caveat forward:** `DEFECT-20260825:172-176` records the 500
  threshold as a Codex session's claim about its own authority and NOT Joseph speaking — this decision fixes
  its UNIT, not its provenance.
- **✅ `OI-179` DEFECT 3 ENFORCED ACROSS THE EIGHT k=0 LAUNCHERS, 2026-09-01 — `OI-179` DISCHARGED:**
  [`RECORD-20260901-oi179-defect3-enforced.md`](RECORD-20260901-oi179-defect3-enforced.md)
  — Joseph: ***"go ahead with defect-3 enforcement"***. `MNV_ENV_PROVENANCE` is now **mandatory with no
  default** in all eight launchers, each task **records its own environment** (even when the check then
  fails), and every `MNV_*` the submission baseline DECLARES must have reached the task. Exit codes
  **propagated, not collapsed**: 2 could-not-look, 3 measured-drift. **The cost the 2026-08-31 shape was
  avoiding does not exist and this was measured before acting:** the pre-source loop compares against
  `HEAD` not a hardcoded digest, `verify_hash_bindings.py` reports ALL BINDINGS INTACT with **none of the
  eight bound by an active run receipt**, and each `--pair` set already includes itself — **no `OI-123`
  supersession**. **THREE ASSERTIONS WERE WRITTEN AND REMOVED, each on a measurement rather than because a
  test was inconvenient:** search paths cannot be asserted (probe job `57819105` measured a compute node's
  pre-activation environment byte-identical to the login node's, but its `/usr/bin/python3` is **3.6.15**
  and the tool needs 3.7+, so the check cannot run where the comparison would be exact); **HOME** cannot be
  asserted (six launchers set `--export=ALL,HOME=…` and three re-export it, so asserting it would have made
  three **refuse themselves** on every correct run); and an **added `MNV_*` is what activation does**. All
  three are reported as observations. ~~**64/64** in `test_k0_launcher_two_roots.py`~~ **— CORRECTED 2026-09-01: that run collected
  33.** `unittest.main()` sat at line 853 of 1325 with three classes after it, so direct execution
  skipped 31 tests and still printed `OK`; 64 was a count of `def test_` lines, not of the runner's
  report. Placement fixed; the file now genuinely reports **Ran 64 … OK** and all 31 pass. Census
  suite **25/25** (was 13/13, extended under `OI-185`), **25** self-test arms in the tool. All eight parse under the **real target interpreter, bash
  4.4.23 on saul**. **⚠ ONE CONSEQUENCE IS ROUTED TO JOSEPH AS `OI-185` RATHER THAN ABSORBED:** ruling 21's
  guarding boundary moves **14/30 → 14/38** (guarded unchanged at 14, unclassified at 0). The census
  **fired** rather than absorbing it, which is `F-7(a)`'s complaint answered. **MOVES NO GATE:** Gate 2
  remains FAIL, leg 6 prohibited, nothing adopted, nothing submitted, CAND `1 of 7` / QUOTED `0 of 7`.
- **🔎 CAUSE 4's JITTER FLOOR RECOVERED, 2026-09-01 — AND THE LEDGER'S `1.539` DESCRIBES A DELETED
  PRODUCT:**
  [`FINDING-20260901-cause4-jitter-floor-recovered.md`](FINDING-20260901-cause4-jitter-floor-recovered.md)
  — Joseph authorized the measurement he had left unowned (***"You can take it"***). **`jit_trace =
  3.731e-78`**, with the full print block `raw ratio=1.541` / `corrected ratio=1.539`, so **the
  magnitude of cause 4's defect on the reported ratio is −0.11%**. Every printed number re-derives from
  its printed operands, four for four. Recovered from the one surviving scratch log Lane D found at
  `8a6cf176` and warned was perishable; it survived 15 more days and is now durable at
  `state/RECEIPT-20260901-cause4-jitter-floor-recovered.json`, whose transcript **re-hashes to the
  cluster-measured sha256**. **⚠ THE LARGER FINDING: the recovered numbers belong to a product that no
  longer exists.** That run wrote `uq_5d/unified_throw_cov_5d.root`; the path's current occupant is
  2.68 GB at `2026-07-13`, twelve days later. The adopted ROOT's own committed operands give a **raw**
  sqrt-trace ratio of **1.3107**, and a corrected ratio can never exceed its raw one — so
  `VALIDATION_LEDGER.md:1192` prints a superseded occupant's number under the adopted product's name.
  **A CONVENIENT ALTERNATIVE READING WAS REFUTED BY THE MEASUREMENT** and is recorded as such: the only
  arithmetically-possible reading beforehand was a *trace* ratio, under which the value inverted
  cleanly — the log shows it is a *sqrt-trace* ratio, and adopting the other would have been
  measurability choosing the specification. **GRADES NOTHING:** the `M` cell is not moved, Gate 2
  remains FAIL, CAND `1 of 7` / QUOTED `0 of 7`. Read-only throughout — isolated worktree exited clean,
  three read-only cluster reads, nothing on the cluster mutated.
- **✅ JOSEPH RATIFIES `OI-185`, 2026-09-01 — `OI-185` DISCHARGED, THE BOUNDARY STANDS AT 14/38 AND THE
  AUTHORED TOTALS ARE GONE:**
  [`DECISION-20260901-joseph-ratifies-oi185-invariants.md`](DECISION-20260901-joseph-ratifies-oi185-invariants.md)
  — Joseph, in his own turn: ***"Okay I like your recommendation for OI-185, do it"***. **The record
  reproduces the accepted recommendation VERBATIM**, because a ruling of that form takes 100% of its content
  from the recommendation and a later summary would let the producing lane set the scope of his ruling after
  the fact. **BOTH HALVES SHIPPED. (1)** ruling 21's boundary is ratified at **14 guarded / 38**. **(2)** the
  four authored totals — `excluded_preflight` 24, `non_comment_python3_invocations` 54,
  `inline_interpreter_probes` 16, `launchers` 8 — are **REMOVED, NOT BUMPED**; the census derives and prints
  them. **THREE PINS SURVIVE:** `guarded == 14` (ruling 21's actual subject), `unclassified == 0`, and
  `commented_out_python3_lines == 18` — the last a TRIPWIRE deliberately left pinned, since the ruling
  authorized de-pinning the BOUNDARY totals and nothing else. Schema `mnv_preflight_exclusions/1 → /2`, and a
  v1 declaration is now **refused as could-not-look** rather than read under v2 semantics. **NEW ENFORCEMENT:**
  every declared exclusion must be structurally complete, resolve to its declared path, appear exactly
  `per_launcher` times, and be **A-3 `--pair` bound in every launcher** — the last was true of all three tools
  and asserted by nobody, which is `F-7(a)`'s complaint about the exclusion itself. **✅ THE ONE DEPARTURE FROM THE
  RATIFIED WORDS IS RESOLVED (§4) — Joseph, 2026-09-01: *"I don't think I meant it literally"*, so the
  shipped criterion stands and no code changed. AS DISCLOSED BEFORE HE RULED:** the recommendation gave the ground as *"imports only the
  standard library"*, and **implemented literally that is unsatisfiable by the set ruling 21 already
  accepted** — measured, `mnv_source_manifest.py` has `repo_origin_count` **1**, importing `MARKERS,
  is_checkout` from `mnv_guarded_run` itself. A stdlib-only rule would have fired on a ratified entry **on
  every correct tree**. The rule was **not relaxed to fit**; the question was restated to the CIRCULARITY
  ground the declaration always gave, made falsifiable as *repository imports ⊆ {`mnv_guarded_run`}* — broader
  than the ratified words **by exactly one module** — disclosed before the ruling, and ratified by it. **THE PROMISE IS NOW TWO TESTS:** a
  principled fourth preflight tool passes with no ruling (boundary 46, `guarded` still 14) and the same
  launcher bytes without the declaration entry still fail. Census suite **25/25**, up from 13. **NO LAUNCHER
  WAS EDITED** — no `F-14`/§7.0.7 coupling, no `OI-123` supersession. **MOVES NO GATE:** Gate 2 remains FAIL,
  nothing adopted, CAND `1 of 7` / QUOTED `0 of 7`.
- **✅ JOSEPH RATIFIES THE `OI-177` PER-ARM CEILINGS, 2026-09-01 — `OI-177` DISCHARGED:**
  [`DECISION-20260901-joseph-ratifies-oi177-per-arm-ceilings.md`](DECISION-20260901-joseph-ratifies-oi177-per-arm-ceilings.md)
  — Joseph, in his own turn: ***"I sign"***. **RATIFIED, in task-hours:** arm 2 seed split **8 CPU** (+3),
  arm 5 uthrow run **60 CPU** (+30), arm 6 uthrow block **40 CPU** (+10); arms 1, 3, 4 and 7 unchanged at
  20 GPU / 20 GPU / 30 GPU / 5 CPU. **Sums 70 GPU / 113 CPU**, up from `PROPOSAL-20260830` §6's 70/70.
  **Every ratified ceiling exceeds BOTH observed actuals on its own arm** — checked per arm, not on the
  sums, since a sum can hold while a member is breached. Basis is **n=2 complete populations**:
  `aa67c426` (2026-08-24) and round 2 (374/374, zero failures, finished 2026-09-01T08:57:51Z), summed over
  DISTINCT task identities. **`PROPOSAL-20260830-forward-only-rehearsal.md` IS NOT EDITED** — `ARCHIVAL`,
  `terminal`, `immutable:yes`, 14 inbound refs; it stands as the 2026-08-30 record and is superseded by
  reference. **Three disclosures made BEFORE signature and carried into the discharge rather than dropped:**
  arm 6's `40` is the least well-supported of the three (its `+3.3%` round-over-round is two unlike
  distributions whose sums coincide — R1 `39.4/52.2/518.3` min against R2 `40.5/81.9/289.0`, R1's mean
  carried by one 8.6-hour outlier); arm 4 holds at 30 on the thinnest margin and was deliberately not
  proposed for change; and **a denominator correction** — arm 4's headroom was quoted as `12.4%` over the
  *ceiling* while the amendment's other headroom figures are over the *actual*, where it is `14.2%`.
  **The ceilings are set from the WORST OBSERVED REGIME, not a forecast:** §3c/§3e measure that
  CPU-partition arms reproduce in neither elapsed nor `TotalCPU` (arm 5 moved +58.7% and +50.4%), so a
  third run may exceed them — that would be a new `OI-*`, not a defect in this signature. **MOVES NO
  GATE:** Gate 2 remains FAIL, leg 6 stays prohibited, nothing is adopted, no compute is authorized,
  counts hold at CAND `1 of 7` / QUOTED `0 of 7`. Largest ceiling `60` against a `500` delegation
  threshold whose provenance caveat (`DEFECT-20260825:172-176`, not Joseph's words) still stands.
- **THE QUARANTINE IS GRADED AGAINST THE CANDIDATE, NOT THE JULY ARTIFACT, 2026-08-31:**
  [`DECISION-20260831-joseph-quarantine-graded-against-the-candidate.md`](DECISION-20260831-joseph-quarantine-graded-against-the-candidate.md)
  — Joseph: *"Okay it sounds like the correct ruling"*, *"Okay do that"*, and **confirmed directly to the
  recording lane as *"yes its my ruling"*** before the record was written. The seven causes are graded
  against `stamped_bkgaware_meancentered_20260812.root` (sha `4f168e83…`, CV `dbcd5359…`, job
  `56720356`). **`CRITERIA §0` already makes discharge a (cause × artifact) property** — *"a class has no
  construction… discharge for **which** matrix?"* — so choosing the subject is sanctioned, not a
  workaround. **Against X the provenance leg is unsatisfiable IN PRINCIPLE**, verified by measurement:
  the g2 input's mtime AND ctime are both `2026-07-13 02:15:41 −0700`, while `fixed_seed_null_norm`
  first enters git at `07c18aee` `2026-07-14 14:43:19 −0700` — the artifact predates its own stamping
  code by ~36.5 h and equal ctime rules out a restore, so no stamp for X can ever exist. **X IS
  RETAINED**: `adopt_unified_5d.py` opens the July product `RECREATE`, so deletion would do what that
  guard exists to prevent; X also backs `values.tex` today and is the only baseline against which the
  candidate's "flux fix alone" claim is checkable. Demotion only AFTER adoption and re-pointing.
  **ADOPTS NOTHING, discharges no cause, changes no count** — CAND `1 of 7`, QUOTED `0 of 7`; Gate 2
  remains **FAIL**. §6 corrects a withdrawn framing: `07c18aee` shows X was DELIBERATELY adopted, so
  nobody erred.
- **`OI-177` PER-ARM CEILINGS, AMENDMENT PREPARED FOR SIGNATURE, 2026-08-31:**
  [`AMENDMENT-20260831-oi177-per-arm-ceilings.md`](AMENDMENT-20260831-oi177-per-arm-ceilings.md)
  — **PREPARED, NOT RATIFIED; `OI-177` stays OPEN.** §6's estimate column is inherited verbatim from
  `PLAN-20260822-oneMember-mii-staged.md:220-224`, a 2026-08-22 prior, and §6's own detector row admits
  it is *"from the older 24-task population"* while declaring **19** tasks — an asymmetric comparison,
  not a slipped number. Measured `aa67c426` actuals over DISTINCT task identities, all seven
  populations complete: bootstrap **15.38** A100-h, seed split **5.43** CPU-h, detector **13.88**,
  sweep **25.54**, uthrow run **30.94**, uthrow block **30.01**, combine **0.42** — **total overrun
  1.38 CPU task-h**, reconciling with the row. Arm 5's prior underestimated by **45%**. Proposes
  minimal change: measured actuals into the estimate column, and raise only the **three** breached
  ceilings (2 → 8, 5 → 40, 6 → 40 CPU-h). Sums 70 GPU / 93 CPU, far under the strictly-under-500
  delegated thresholds. **Flags that ratifying on ONE run repeats the shape of the defect at lower
  severity** — round 2 will supply a second independent measurement of the identical arms, and holding
  costs nothing because the row blocks no gate. Moves no gate; Gate 2 remains **FAIL**.
- **THE GATE-THAT-CANNOT-FAIL AUDITOR IS BLIND ON 15 FILES, 2026-08-31 (`OI-180`):**
  [`FINDING-20260831-strip-noncode-inverts-on-a-closing-triple-quote.md`](FINDING-20260831-strip-noncode-inverts-on-a-closing-triple-quote.md)
  — `audit_gates_that_cannot_fail.py:59` reads a **closing** triple quote at line start as an
  **opening** docstring, so the terminator of an assigned multi-line string inverts the state machine
  for the rest of the file. Measured over 473 Python files: **15 lose more than half their code, 3,730
  non-blank lines invisible**, worst `test_k0_launcher_two_roots.py` at **5.0%** (978 → 49). **Not
  confined to fixtures** — `mii_adopt_unified_5d_stamped.py` 48.6% (an adoption path),
  `mii_root_payload_classes.py` 48.8%, `pet/cstat_data_only.py` 49.2%, `conftest.py` 41.6%. **So any
  0-hits over an affected file is unfounded.** CORRECTS the sibling finding's §1, which attributed the
  sweep's zero to the detector binding alone. **An authorized detector was written, passed 8-of-8
  power, and was deliberately NOT SHIPPED**: it returns 0 on the real file because the stripper already
  blanked its subject, and 170 REVIEW hits elsewhere — its power arm passed only because `run_power`
  feeds RAW lines, making fixture and reality different objects. Shipping it would have added a gate
  that cannot fail inside the instrument built to find them. Moves no gate; Gate 2 remains **FAIL**.
- **THE BEN-039 DETECTOR IS TRIPLE-BOUND, 2026-08-31:**
  [`FINDING-20260831-ben039-detector-is-triple-bound.md`](FINDING-20260831-ben039-detector-is-triple-bound.md)
  — `audit_gates_that_cannot_fail.py` is HEALTHY (`--power-only` rc 0, all seven detectors fire) and
  **blind to `OI-179` defect 2** (sweep grep returns 0). Bound on **three** axes, not one: span, left-hand
  vocabulary, and right-hand call shape. **Row 3 of its table is the proof** — supplying BEN-039's own
  `measured` vocabulary is STILL silent, because `self._ambient_prefixes()` is a method call and the
  pattern requires `.get(`. Positive control fires, so the nulls are evidence. **FOLDED INTO `OI-179`
  rather than filed as a new class**, on Joseph's delegation: the row's remaining open content already
  IS this, the class was named in 2026-08-07 as BEN-039, and a new `OI-*` or `BEN-*` ten-block costs the
  same freeness ceremony for a row that belongs to an open one. **The `mkdir` half is unreachable by any
  source-line detector**, so defect 3 becomes the only mechanism that can detect the class at all —
  load-bearing for two failures now. Supplies the acceptance criterion: any new detector must FIRE in
  `--power-only` on a reconstruction of pre-`b512760d` `good_env()`, or it is itself a gate that cannot
  fail inside the instrument built to find them. Moves no gate; Gate 2 remains **FAIL**.
- **THE `OI-179` REMEDIATION IS CONFIRMED IN A REAL SCHEDULED JOB, 2026-08-30:**
  [`RECORD-20260830-oi179-remediation-confirmed.md`](RECORD-20260830-oi179-remediation-confirmed.md)
  — `[env-pathcheck] OK`, **47 entries, 0 violations**, in all four round-2 `.out` files, on **both**
  partitions that produced round 1's identical refusals (`shared_gpu_ss11`, `shared_milan_ss11`). The
  four tasks then **COMPLETED** `0:0` (8:45–17:18) and wrote products: `member_k000000/` went from 0
  entries to `boot_nd_5d/` + `seedscan_split_5d/` with **4 `.done` markers**. So the diagnosis is
  confirmed by successful remediation, a falsifiable prediction that held — declare the allowlist,
  change nothing else. **The 46 → 47 entry step is recorded as UNEXPLAINED** (consistent across
  partitions, benign). **§3 says outright this is NOT a run result: 4 of 374 tasks.** `OI-179` stays
  **OPEN on defect 1** — `PACKET:122` still measures rc 3 on `$HOME/bin`. No gate moves; `OI-177`
  unratified; Gate 2 remains **FAIL**.
- **ROUND 2 OF THE SEVEN k=0 ARMS IS SUBMITTED, 2026-08-30:**
  [`RECORD-20260830-k0r2-round2-submission.md`](RECORD-20260830-k0r2-round2-submission.md) — job ids
  `57753239`, `57753243`, `57753244`, `57753245`, `57753246`, `57753247`, `57753248`, run id
  **REUSED** (`k0-7ac0edec-20260830T000215Z`) because round 1's arms produced nothing and `%A` keys
  the logs by job id. **The positive control ran this time, in the ACTIVATED environment:**
  `[env-pathcheck] OK: 46 search-path entr(ies) checked`, `PREAMBLE_EXIT=0` — the in-job proof the
  proposal lacked; 46 rather than 37 because the earlier read was unactivated. Environment provenance
  written to disk BEFORE the first `sbatch`, closing `OI-179` defect 3 for this run. Abort arm armed
  and read three times, porcelain **726** / digest `d429f0f3` each time, never fired. **§6 says
  outright that this record does NOT say the run worked** — no task had started, and round 1 queued
  healthily for 22 minutes before failing in 12 seconds. Closed by
  [`CLOSE-20260830-canonical-requiesce-k0r2-window.md`](CLOSE-20260830-canonical-requiesce-k0r2-window.md),
  which records that the prose hold was treated as UNPROTECTED throughout — no dashboard lane was live
  to acknowledge it — and that **what actually held was the abort arm, not the prose.** Releases the
  dashboard lane's `OI-175` fix (726 → 725), safe because `OI-178` already ruled that drift a filed
  finding. Deployment tree NOT released. **`OI-177` unratified; Gate 2 remains FAIL.**
- **THE CANONICAL CHECKOUT IS RE-QUIESCED FOR THE RE-SUBMISSION WINDOW, 2026-08-30:**
  [`FREEZE-20260830-canonical-requiesce-k0r2-resubmission.md`](FREEZE-20260830-canonical-requiesce-k0r2-resubmission.md)
  — a SECOND window, because the first expired by its own terms at submission authorization and
  `CLOSE-20260830` **released the dashboard lane** to land the `OI-175` fix, which takes porcelain
  **726 → 725**. **Nothing has drifted:** HEAD `32e403b8`, porcelain **726**, digest `d429f0f3…`
  unchanged across a five-hour hold re-measured at `20:43:52Z`, and `mii/member_k000000` still empty.
  So this closes a window that is open rather than repairing a violation, and the risk is **permitted
  future drift** — deliberately the weaker claim. Prose hold, preventive by convention and detective
  by `F-17(a)`; pushed before any operand read, and the dashboard lane asked directly, because a hold
  peers cannot see is not a hold. A `CLOSE-*` record is owed whether the re-submission is issued or
  abandoned.
- **RE-SUBMISSION OF THE SEVEN k=0 ARMS, AUTHORIZED 2026-08-30:**
  [`PROPOSAL-20260830-k0r2-resubmission.md`](PROPOSAL-20260830-k0r2-resubmission.md) — Joseph: *"do
  all of it, can you continue on the runs too?"* **One added `export` line and no repository file
  changes**, so none of the `F-14` / §7.0.7 or `OI-123` pin ceremony applies. **Measured on the
  DEPLOYED library against the real login PATH:** `PACKET-20260823:122` as documented gives **rc 3**
  with one `VIOLATION` on `$HOME/bin`, and the corrected **three-entry** widening gives
  `[env-pathcheck] OK: 37 search-path entr(ies) checked` — so **this document is the operative recipe
  and the packet is not**, until `OI-179` defect 1 is settled. Preconditions measured: canonical HEAD
  `32e403b8`, porcelain **726**, digest `d429f0f3…` all UNCHANGED since submission, and
  `mii/member_k000000` still empty — so the `F-17(a)` operands still describe their subject and the
  live risk is **permitted future drift**, the dashboard lane having been released to land the OI-175
  fix (726 → 725). Carries the residual shadowing risk the widening accepts, and the narrower
  launcher-edit alternative it rejects. **`OI-177` ceilings stay unratified; Gate 2 remains FAIL.**
- **THE SEVEN k=0 ARMS DIED ON `env-pathcheck`, AND THE GUARD WAS RIGHT, 2026-08-30:**
  [`FINDING-20260830-k0r2-env-pathcheck-submitter-declaration-omitted.md`](FINDING-20260830-k0r2-env-pathcheck-submitter-declaration-omitted.md)
  — six tasks of `k0-7ac0edec-20260830T000215Z` failed in 8–15 s, exit `3:0`, byte-identical stderr
  (1453 B, `md5 9fc5fa4d…24df6`); the rest cancelled at 16:35:21Z on Joseph's instruction; **~1 minute
  of compute burned.** Cause is a **procedure omission, not a code defect**:
  `lib_mnv_env_pathcheck.sh:37-41` specifies that home-directory PATH entries are refused until the
  submitter predeclares them, `PACKET-20260823:122` gives the export line and `:218` calls it *"a
  submitter-declared allowlist"*, and **`RECORD-20260830` §5 records the submission as eight `export`
  lines with `MNV_ENV_SYSTEM_PREFIXES` absent.** **Three defects filed as `OI-179`:** `PACKET:122`
  omits `$HOME/bin` so the documented recipe still fails; **branch (b) of the guard has no test in the
  direction it acts** — `tests/test_k0_launcher_two_roots.py:738` asserts `[env-pathcheck] OK:` but
  `good_env()` feeds it an allowlist derived from the running host by `_ambient_prefixes()`, so the
  arm cannot fail, which is why Gate 1 passed 18-of-18 while the launcher could not start; and the run
  records no environment provenance at all while pinning its tree to the byte. **NO code, launcher or
  `MANIFEST` pin must change to re-submit.** Corrects the producer session's first diagnosis, which is
  recorded in §4 and withdrawn by its author. Moves no gate; Gate 2 remains **FAIL**.
- **Canonical drift during the run is a FILED FINDING, 2026-08-30:**
  [`DECISION-20260830-joseph-f17b-post-path-drift-is-a-filed-finding.md`](DECISION-20260830-joseph-f17b-post-path-drift-is-a-filed-finding.md)
  — Joseph chose option 1 of four: *"Yes do option 1, filing the correction and settling OI-178"*,
  declining a multi-day re-freeze, a repoint at a quiescent stand-in, and adding `M-4.dirty` to the
  expected-differences file. **Rests on three artifacts read directly**: `compare_m1_m6.py:141-145`
  (exit 20 is a finding, 4/5 are refusals), `PROPOSAL` §3 (`F-17(b)` is not-discharged only on a
  missing `M-2` result, a schema gap, or a refusal), and `m1m6_expected_differences.json`, which says
  a difference in `M-4.dirty` *"is the finding `F-17(b)` asks for"*. So canonical **726 → 725**
  yields exit 20 with a retained finding and `F-17(b)` still discharges. **CORRECTS TWO OF THIS
  LANE'S OWN RECORDS:** the close record's claim that the freeze preamble sets out the options'
  trade-offs (it names them in one sentence with none), and `OI-178`'s framing of the collision as
  BLOCK-shaped when it is finding-shaped. `OI-178` **DISCHARGED**. Moves no gate; Gate 2 remains
  **FAIL**; the grader still weighs the finding.
- **THE DECLARED CANDIDATE SHA, with A-2(a)–(g) filed against it:**
  [`DECLARATION-20260823-k0-candidate-sha.md`](DECLARATION-20260823-k0-candidate-sha.md) —
  `a54038b21fdebfc975bec452a05866ffa571a36c`, **780** tracked source files, listing sha256
  `1b45da55…`, all seven clauses MET. Repairs the round-8 `F-1(a)` failure. **Declares a sha; clears
  no gate.** Re-run before the first `sbatch`; do not inherit the numbers.


- **ROUND-7 REPAIR PACKET (2026-08-23), awaiting the terminal regrade:**
  [`PACKET-20260823-round7-f2a-parity-and-f17a-filing.md`](PACKET-20260823-round7-f2a-parity-and-f17a-filing.md)
  — final candidate `e93364d1…`, deployed, `porcelain=0`, 0 writable. **Gate 1 is NOT claimed passed.**


- **M-1…M-6, re-measured 2026-08-23 on BOTH trees:**
  [`MEASUREMENT-20260823-m1-m6-at-the-candidate-and-canonical.md`](MEASUREMENT-20260823-m1-m6-at-the-candidate-and-canonical.md)
  — the `F-17(a)` filing repair. Ten M-1 rows (the previous filing had nine and dropped
  `unified_throw_cov.py`), **four** surviving literals on the candidate, **five** on the canonical
  checkout. Re-run it with `docs/orchestration/measure_m1_m6.py --tree <TREE>`; do not inherit a number.


- Live snapshot: [`LIVE-STATE.md`](LIVE-STATE.md); run its freshness check before use.
- Bounded queue: [`../CURRENT_WORK.md`](../CURRENT_WORK.md); sources live in
  [`control-plane/`](control-plane/).
- Queue overflow: [`../CURRENT_WORK_OVERFLOW.md`](../CURRENT_WORK_OVERFLOW.md).
- Unpromoted active records: [`../CURRENT_WORK_BACKLOG.md`](../CURRENT_WORK_BACKLOG.md).
- Active process rules: [`PLAYBOOK.md`](PLAYBOOK.md).
- Open/deferred source records: [`../OPEN_ITEMS.md`](../OPEN_ITEMS.md).
- Joseph-only decisions: [`USER-DECISIONS.md`](USER-DECISIONS.md).
- **The whole remaining publication path, ordered by dependency:**
  [`PUBLICATION-READINESS-20260822.md`](PUBLICATION-READINESS-20260822.md) — every item with its
  measured state and command, split into Joseph decisions / lane work / gated / done. It answers two
  questions no other document settles: **the `M(ii)` member family IS on the critical path**, via the
  seven-cause quarantine named as *the binding gate* in `../INTEGRATION_CHECKLIST.md` rather than via
  any runbook packet; and the **P3S lateral is BUILT and validated but not committed and not
  adopted**, which makes `VALIDATION_LEDGER.md` `VL68` and
  [`RUNBOOK-20260807-gbdt-closeout.md`](RUNBOOK-20260807-gbdt-closeout.md)`:38` stale.
  **A view, never evidence** — re-measure any field before deciding a gate on it.

## Evidence and claims

- Verified numbers: [`../../VALIDATION_LEDGER.md`](../../VALIDATION_LEDGER.md).
- Physics claims: [`CLAIMS.md`](CLAIMS.md).
- Active BEN identifiers: [`FINDINGS.md`](FINDINGS.md); full evidence is at the frozen tag.
- Bugs and traps: [`../../KNOWN_ISSUES.md`](../../KNOWN_ISSUES.md).
- Retracted values: [`INDEX-retracted-and-superseded-values.md`](INDEX-retracted-and-superseded-values.md).
- Why the B1 pause's clause (c) cannot be met through the launcher:
  [`FINDING-20260822-clause-c-adopt-is-unreachable-under-its-own-pause.md`](FINDING-20260822-clause-c-adopt-is-unreachable-under-its-own-pause.md)
  — measured: `sbatch_finalize_5d_bkgaware_gpu.sh:347/:352` is unreachable in both regimes, so the
  condition is circular as written and the disposition is a forced choice, not a judgement call.
- The 2026-07-12 quarantine's three no-compute legs, re-measured at HEAD `32e403b8`:
  [`FINDING-20260830-quarantine-nocompute-legs-measured.md`](FINDING-20260830-quarantine-nocompute-legs-measured.md)
  — cause 3's `P-ii` premise is **false** (four write sites landed 08-18…08-20, and two 08-22 records
  restated it as live afterwards); the *"one edit closes 2, 3 and 4"* multiplier **does not hold**, and
  cause 3's `P-i` is **no longer a no-compute leg**; cause 1 has content on all four legs **for the
  quoted artifact**, needing only the routed `DETERMINATION §6` judgement; and cause 4's `M` is neither
  recoverable from bytes nor closed by a run, because the deflation never entered a stored object on X's
  path. **Regrades nothing** (`BEN-381`) — four decisions routed as `OI-170`–`OI-173`. Counts unchanged:
  CAND `1 of 7`, QUOTED `0 of 7`.
- Why the accepted forward-only k=0 rehearsal's seven arms were not submitted on 2026-08-30:
  [`FINDING-20260830-k0-member-namespace-blocks-submission.md`](FINDING-20260830-k0-member-namespace-blocks-submission.md)
  — all three step-3 conditions pass and the preflight re-verifies clean, including canonical porcelain
  **726** with a status digest byte-identical to the Gate-1 round-2 grader's reads, so the quiesce held.
  The blocker is in the **data root**, which no Gate-1 clause and neither F-17 operand measures:
  `mii/member_k000000` still holds the `aa67c426` rehearsal's complete products, every marker reading
  `note:"est_seed_offset=0"`, so `mr_skip_if_complete` **adopts**. Arms 1-3 would skip all 143 of their
  tasks (cross-run, mixed-pin — a §7 abort condition); arms 4-6 carry **no resume guard** and would
  overwrite a Gate-2-FAIL rehearsal's products in place. **Moves no gate and grades nothing**; the
  disposition decision is routed as `OI-176`. No `sbatch` was issued.
- **The `aa67c426` products were quarantined and the seven arms WERE submitted, 2026-08-30:**
  [`RECORD-20260830-k0-quarantine-and-seven-arm-submission.md`](RECORD-20260830-k0-quarantine-and-seven-arm-submission.md)
  — Joseph ruled *"do option 1"* (`DECISION-20260830-joseph-quarantine-k0-member-namespace.md`,
  `deef0e48`), a **per-instance** authorization naming an exact file set. **517 files /
  2 733 087 821 regular-file bytes moved, never deleted**, to
  `/pscratch/sd/j/josephrb/quarantine/20260830-k0-aa67c426-failed-rehearsal/`, with a 0-line diff on
  both the per-file `sha256` set and the `(relpath, bytes, mtime, inode)` ledger. Canonical porcelain
  **726** and status digest `d429f0f3…` held across **five** reads including immediately before each
  `sbatch`. Seven job ids `57742557`, `57742558`, `57742559`, `57742560`, `57742561`, `57742633`
  (`afterok` detector), `57742635` (conjunctive `afterok` over both uthrow arrays) — 374 tasks.
  **Moves no gate, adopts nothing, files no Gate-2 evidence, and leg 6 was not submitted; Gate 2
  remains FAIL.** `OI-176` is DISCHARGED; a §6 per-arm CPU-ceiling discrepancy of 1.38 CPU task-h is
  routed as `OI-177`.

### Documents that open items route to but this router did not list

Added 2026-08-20. `live_doc_indexed.py --check` reports LIVE docs absent from this catalog and
**does NOT enforce it**, so an item's own governing document could be unreachable from the router.
The count was written as **19** on 2026-08-20; re-derived from the same command on 2026-08-22 it is
**13**, so the figure is stated with its date and its command rather than left to drift. These five are the subset that `docs/OPEN_ITEMS.md` rows
actually cite; the other fourteen are not routed to by any open item and are left out
deliberately, because this file is a pointer-only router and not an exhaustive index.

- [`PROVENANCE-DEBT-20260810-standard-p4.md`](PROVENANCE-DEBT-20260810-standard-p4.md) — **`OI-7`'s
  own blocker**: its §3e is the sentence that row is open on. Cited 4× in `OPEN_ITEMS.md` and
  reachable from no router until now.
- [`SPEC-20260814-gate5-cstat-construction-v1.md`](SPEC-20260814-gate5-cstat-construction-v1.md) —
  the ruled `C_stat` construction spec; cited 6×, including by `OI-93`, whose row is stale against
  it.
- [`RANK-AND-INVERSION-20260810.md`](RANK-AND-INVERSION-20260810.md) — the rank and pseudo-inverse
  measurements behind the N-D χ² protocol; routed to by `OI-137`.
- [`RECONCILIATION-20260817-gbdtfive-macros-vs-rebuilt-candidate.md`](RECONCILIATION-20260817-gbdtfive-macros-vs-rebuilt-candidate.md)
  — traces the `\gbdtFive*` note macros to their artifacts; one of them had been destroyed.
- [`DETERMINATION-20260811-cause5-binding-half.md`](DETERMINATION-20260811-cause5-binding-half.md),
  [`CONVENTION-verifying-a-check-is-deployed.md`](CONVENTION-verifying-a-check-is-deployed.md) —
  each cited once.
- [`FINDING-20260822-a-hold-that-instructed-its-own-deletion.md`](FINDING-20260822-a-hold-that-instructed-its-own-deletion.md)
  — added 2026-08-22, routed to by `OI-70`. **Read it before acting on
  [`HOLD-20260821-clause-c-verification.md`](HOLD-20260821-clause-c-verification.md), whose own text
  instructs its deletion.** That instruction is wrong, the hold's bytes are preserved on Joseph's
  ruling, and this route is the only thing that disarms it.

- [`BRIEF-20260822-oi137-finite-N-precision-bias-exposure.md`](BRIEF-20260822-oi137-finite-N-precision-bias-exposure.md)
  — `OI-137`'s measured exposure and **the recommendation Joseph's ruling 7 requires before any
  uncertainty-model change: disclose, do not correct.** Routed to by `OI-137` and `OI-93`. Re-runnable
  covering search beside it at [`state/oi137-covering-search-20260822.sh`](state/oi137-covering-search-20260822.sh).
  **Do not carry "0.2% of the headline trace" forward as the reason the exposure is small** — a trace
  weights eigenvalues by `lambda` and a precision matrix by `1/lambda`; the brief gives the real reason.
- [`PROVENANCE-20260822-declaration-v-scalar5d-blocks.md`](PROVENANCE-20260822-declaration-v-scalar5d-blocks.md)
  — added 2026-08-22 on Joseph's ruling 10. **Declaration (v) of the N-D χ² protocol, recorded per 5D
  block**: ensemble size, normalization convention, effective inversion dimension and finite-ensemble
  treatment, each with a citation. Routed to by `OI-137`. **It CORRECTS the gap statement carried by
  that row and by the brief above** — `N=160` is recounted and stamped on the throw roots
  (`unified_throw_cov.py:388,540`) and propagated to the adopted product as `upstream_n_throws` since
  2026-08-11, so it is *not* only a hardcoded constant; the surviving gap is `C_stat`/`C_ML`, which
  carry no ensemble-size key on any artifact. **Records/provenance only — it adopts nothing and
  changes no uncertainty model.** Re-runnable covering search beside it at
  [`state/declaration-v-5d-covering-search-20260822.sh`](state/declaration-v-5d-covering-search-20260822.sh).

- [`BRIEF-20260901-greif-fps-thesis-implications-for-pet.md`](BRIEF-20260901-greif-fps-thesis-implications-for-pet.md)
  and [`BRIEF-20260901-greif-fps-thesis-implications-for-gbdt5d.md`](BRIEF-20260901-greif-fps-thesis-implications-for-gbdt5d.md)
  — added 2026-09-01, the two lane extractions of **`arXiv:2608.28449`** (Greif, ATLAS full-phase-space
  Z+jets, 843 dimensions), routed to by `OI-183` and `OI-184`. **Read the citability box first: the
  measurement is in ATLAS review and its thesis figures are ATLAS Internal, so the METHOD is citable
  and the NUMBERS are not.** Between them they carry: the ATLAS `C_ML` construction (ensemble mean as
  the central value, so the nominal cannot sit outside its own family); pretraining as the lever that
  took their seed ensemble from 100 members to 10; the closure instrument (full-covariance χ² in 26
  projections, with the rule that a systematic held at nominal in the pseudodata must be EXCLUDED from
  Σ); and the finding that **the high-dimensional hidden-variable advantage was tested and did not
  hold**. **Neither bears on `OI-126`** — that thesis mentions the bootstrap five times in 313 pages
  and carries no centering diagnostic — and **neither is evidence that any coverage gap here is a gap
  relative to the field**: `coverag` appears once in it, about detector acceptance.

### START HERE for the remaining publication work

- [`WALKDOWN-20260822-one-pass.md`](WALKDOWN-20260822-one-pass.md) — **the ORDER of everything left
  before publication, and which step blocks which.** Deliberately thin: it is a route, not a second
  source of state, and every factual field it points at lives in the readiness list below. Two
  independent tracks — execution integrity (five Gate-1 repairs, then the k=0 rehearsal) and one
  scope ruling that decides whether the 50-member M(ii) family exists at all. **Read this first.**
- [`PUBLICATION-READINESS-20260822.md`](PUBLICATION-READINESS-20260822.md) — the measured INVENTORY
  behind that route: every remaining item with the command that measured it, plus `AMENDMENT 1`
  recording an independent peer review whose four objections were all accepted. **Where this and a
  canonical artifact disagree, the canonical artifact wins.**

- [`MEASUREMENT-20260823-m1-m6-at-the-candidate-and-canonical.md`](MEASUREMENT-20260823-m1-m6-at-the-candidate-and-canonical.md)
  — the `F-17(a)` filing repair, 2026-08-23. **Ten** M-1 rows and **four** surviving literals on the
  candidate (three `_DATA_ROOT`, one inert `_REPO`); **five**, all `_REPO`, on the canonical checkout,
  one of them active. The 2026-08-22 filing it replaces had nine rows and said "three". Re-run it —
  `python3 docs/orchestration/measure_m1_m6.py --tree <TREE>` — and do not inherit a number.

### Gate-1 round 8 — F-2(a) AND F-17(a) PASS; F-1(a) failed and is repaired

- [`DECLARATION-20260823-k0-candidate-sha.md`](DECLARATION-20260823-k0-candidate-sha.md)
  — the declared candidate `a54038b21fdebfc975bec452a05866ffa571a36c`, **780** tracked source files,
  listing sha256 `1b45da55…`, **A-2(a)–(g) all MET and each measured separately**. Repairs the
  round-8 `F-1(a)` failure: the digest was three shas stale and the packet named a sha that was not
  `HEAD`. **Declares a sha; clears no gate. Gate 1 does NOT pass.**

### Round-7 repair — BUILT AND DEPLOYED, awaiting the terminal regrade

- [`PACKET-20260823-round7-f2a-parity-and-f17a-filing.md`](PACKET-20260823-round7-f2a-parity-and-f17a-filing.md)
  — Joseph's three authorized items: the parity gate extended to all three tracked files the preamble
  sources (one block digest across all eight launchers, ten new arms in four directions, power
  checked), the M-1…M-6 filing corrected to ten rows on both trees, and the runbook/plan §C exports.
  Final candidate `c35bed58…`, deployed, `porcelain=0`, 0 writable. **Gate 1 is NOT claimed passed.**

### Gate-1 round 6 — GRADED, TERMINAL, and it DOES NOT PASS

- [`GATE1-VERDICT-ROUND6-20260823-k0-execution-integrity.md`](GATE1-VERDICT-ROUND6-20260823-k0-execution-integrity.md)
  — **16 PASS / 2 FAIL / 0 NOT-EVALUABLE** (`F-2(a)`, `F-17(a)`), graded at `fabeedc2`. Landed
  **byte-identical**, sha256 `bf2ad6e1415391bb5eba3e15b9e818fb10a6ee65ce4e7ca1b8b08dd57c3d0125`,
  415 lines. The operative rubric was confirmed byte-identical to round 5 (1160 lines,
  `e0fb342b6466…`) — **no criterion was added.** Round 6's two targets are genuinely fixed and the
  grader could not break either; **both `F-14` grounds are closed.** `F-2(a)` fails on a **new
  ground**: `lib_mnv_env_preflight.sh` and `lib_mnv_env_pathcheck.sh` are **tracked** and sourced
  from the code root by all eight launchers with **zero git-parity gate**, executing 77–193 lines
  before the only instrument covering their bytes — while the pure-git gate sits 17 lines above,
  naming only `lib/resume_guard.sh`. `F-17(a)` is unrepaired and outside round-6 scope.
  **This is a terminal handoff: no further grader was requested.**

- [`DECISION-20260823-joseph-a2f-does-not-substitute-for-a3.md`](DECISION-20260823-joseph-a2f-does-not-substitute-for-a3.md)
  — Joseph's ruling of 2026-08-23: **A-2(f) does not substitute for A-3 executing-file parity.** A
  tracked file that executes before the later source-manifest comparison requires **pre-use git
  parity**, so `F-2(a)` **stands**; `F-17(a)` stands until the canonical M-1…M-6 filing is corrected
  **and re-measured at the eventual candidate sha**. **No repair is authorized by it.** The ruling
  is authorized here and nowhere else; a relay of it is not quotable.

### Gate-1 round 5 — GRADED BY A THIRD PARTY, and it DOES NOT PASS

- [`GATE1-VERDICT-ROUND5-20260823-k0-execution-integrity.md`](GATE1-VERDICT-ROUND5-20260823-k0-execution-integrity.md)
  — **15 PASS / 3 FAIL / 0 NOT-EVALUABLE** (`F-2(a)`, `F-14`, `F-17(a)`), regraded first-hand at
  `f3c27870` inheriting nothing. Landed **byte-identical**, sha256 `c2143e2e…`. **The decisive
  finding:** `sbatch_unfold_5d_detector_bkgaware_gpu.sh` invoked both Python preflight tools at
  `:139`/`:148` and sourced its activator at `:227` — a **SyntaxError on the un-activated 3.6.15
  interpreter**, surfacing as *"the execution tree is not the tree that was approved"*, a **wrong
  diagnosis of a right refusal**. It survived 34 green arms because `good_env()` inherited the
  runner's PATH, so the fixture supplied the interpreter the activator exists to supply.
  **Two of the builder's packet claims were also contradicted by measurement** — the suite count and
  a `--check` run made in the wrong tree.

### Gate-1 round 5 — the repair as built (superseded by the grade above)

- [`PACKET-20260823-round5-f2a-f17a-repair.md`](PACKET-20260823-round5-f2a-f17a-repair.md) —
  **the repair packet for `F-2(a)` and `F-17(a)`, and the read-only commands a grader runs.**
  Three roots (`MNV_ENV_ROOT` mandatory, no default), a **14-member digest manifest over the full
  transitive closure** verified before any source, the activator regenerated so no checkout reaches
  `PATH`/`PYTHONPATH`/`LD_LIBRARY_PATH`, `_mr_lib` bound before use in all eight, and the Gate-5
  template routed rather than duplicated. **Re-declared sha `f3c27870`, 778 files, `70fb59d4…`.**
  **GATE 1 IS NOT CLOSED — the verdict stands at 16/2** until a grader who is neither this builder
  nor the round-4 verifier re-grades. **All criteria are re-opened by the sha move.**

### Gate-1 round 4 — GRADED 2026-08-23, and it DOES NOT PASS

- [`GATE1-VERDICT-ROUND4-20260823-k0-execution-integrity.md`](GATE1-VERDICT-ROUND4-20260823-k0-execution-integrity.md)
  — **the independent grade: GATE 1 DOES NOT PASS, 16 PASS / 2 FAIL / 0 NOT-EVALUABLE** (`F-2(a)`,
  `F-17(a)`), by a fresh non-builder. **The decisive finding is not a filing gap:** every
  repo-relative shell file below `setup_salloc_env.sh` is **ABSENT from the declared code root**, so
  every launcher aborts at the activator with exit 1 before any preflight tool, guard or science
  invocation runs. **The k=0 rehearsal is NOT launched and `PR-J1` does not become operative.**
- [`CONFIRMATION-20260823-builder-response-to-gate1-round4.md`](CONFIRMATION-20260823-builder-response-to-gate1-round4.md)
  — the builder lane's independent re-measurement of the decisive claims. **All reproduced; nothing
  contradicted.** Records what the builder got wrong, and argues that one criterion (`F-8(a)`, the
  builder's own `P-5`) was graded **too leniently**.

### Gate-1 round 4 — the k=0 execution-integrity repairs and their evidence

Added 2026-08-22. **Gate 1 DOES NOT PASS and none of these close it.** `F-2(a)` is repaired in its
first hop only; the **transitive environment trust boundary** must be settled and passed by a **fresh
non-builder** first (Joseph, `DECISION-20260822-joseph-b1-lift-and-clause-c.md`). The close-out lane
built all of these and is disqualified from grading them.

- [`DECLARATION-20260822-k0-submission-sha.md`](DECLARATION-20260822-k0-submission-sha.md) —
  **`PR-01` / `F-1(a)`: the submission sha, which previously had no referent anywhere.**
  `MNV_CODE_ROOT = /pscratch/sd/j/josephrb/k0r2/clean` @ `6113a34d`, 775 tracked source files,
  listing sha256 `cc004894…`, with all seven **A-2(a)–(g)** clauses measured separately against it.
  Read this before quoting any "pinned sha" phrase.
- [`P5-P6-20260822-entrypoint-set-and-blind-spots.md`](P5-P6-20260822-entrypoint-set-and-blind-spots.md)
  — **`PR-04` / `F-8(a)`: the two artifacts that did not exist and were undisclosed.** `P-6` is the
  entrypoint-set search with its command and full output (8 entrypoints, 14 invocations — an
  independent cross-check of ruling 21's boundary). `P-5` is the blind-spot inventory, including the
  subprocess enumeration: **one child on the whole k=0 path, and it is WRAPPED.**
- [`MEASUREMENT-20260822-m1-m6-at-pinned-sha.md`](MEASUREMENT-20260822-m1-m6-at-pinned-sha.md) —
  **`PR-05` / `F-17(a)`: M-1…M-6 re-measured, and FOUR MOVED.** Two are stale **in the builder's
  favour** (`M-1`'s literal table, `M-5`'s `8 of 8` → `0 of 8`). **The fastest-expiring document in
  the package** — re-run all six immediately before the first `sbatch`.
- [`SPEC-20260825-f17b-tree-comparison-instrument.md`](SPEC-20260825-f17b-tree-comparison-instrument.md) —
  **what a third lane must build so `F-17(b)`'s "differences reported as findings" is a machine
  statement, not two column sets diffed by eye.** `measure_m1_m6.py` measures one tree per
  invocation and has **no comparison surface at all**; `F-17(a)` was discharged by hand at
  `30ec0707`. Also records **DO NOT build an `F-7(b)` exclusion instrument** — §7.0.9 rules it
  untestable at k=0 and the widening detector already exists at `b49bc360`. Authored by the
  evidence-producing lane per Joseph's 2026-08-25 ruling, so **every clause is rejectable**.
  **BUILT, by the third lane, 2026-08-25:** `compare_m1_m6.py` (the instrument),
  `test_compare_m1_m6.py` (46 arms, both directions per requirement) and
  `m1m6_expected_differences.json` (the reviewable whitelist, deliberately ONE entry). Exit codes
  `0 / 10 / 20 / 4 / 5`. **Two of the spec's clauses were REJECTED and one requirement is partial:**
  its `M-1, M-5, M-6 are falsified by ANY commit to build-k0-execution-integrity` is false as
  measured — 10 of the 46 commits ahead of `8c156a37` touch those populations, not 46 — and as a
  whitelist entry it would have suppressed the `F-17(a)` findings themselves; R5's stated fixture
  cannot exist under exact equality; and R3's `detached-or-branch` and R6's
  `wall-clock of each measurement` are **not in `measure_m1_m6.py --json` at all**, so the record
  names them `UNAVAILABLE-BY-INPUT-SCHEMA` rather than deriving them from the tree as it is now.
  **It grades nothing:** F-17(b) is the F-18(b) reviewer's, who must be a fresh non-builder.
- [`GRADE-20260825-d3-comparator-repair-fitness.md`](GRADE-20260825-d3-comparator-repair-fitness.md) —
  **the independent grade of the D-3 repair (`c8a29082`) required by ruling 3**, at
  `compare_m1_m6.py` `68b4af12` and `test_compare_m1_m6.py` `b355ecdc`. **Verdict: FIT to support a
  future Gate-2 filing, conditionally** — D-3 is closed (all five fail-open spellings, including the
  four the implementer newly found, refused; negative control restoring the pristine guard reddens
  **16 arms**; producer-derived fixture 721/96/**0 accepted**). **The condition is mechanical**: the
  expected list at filing time must contain no *partial* `M-1` selector — satisfied today, the
  shipped list has one entry and no selector. **Partial wildcards are RULED (c), an ambiguity
  requiring a specification decision, and ESCALATE to Joseph**: measured, the pre-repair guard
  accepted them identically (so not an enlargement), but it accepted them through the very clause
  that is D-3 (so not an admitted contract), and two negative controls FIRE — on the real
  population `M-1[nd-unfolding/unified_throw_cov*].first_insert` silently suppresses **two** files
  including the one whose omission was the F-17(a) failure, and a partial selector's reach is not
  stable as the file population grows. **Three figures in the implementer's mutation matrix do NOT
  reproduce** (5 methods, "reddens 4", "reddens 97"; measured 6, 1, 121). **Grades no F-number,
  discharges no clause, authorizes no compute and no filing; Gate 2 stays FAIL and open.** Expires
  mechanically when any of three pinned digests moves.
- [`GRADE-20260825-selector-narrowing-fitness.md`](GRADE-20260825-selector-narrowing-fitness.md) —
  **the independent grade of the §12.2.1 selector narrowing (`63262a3a`) required by ruling 3**, at
  `compare_m1_m6.py` `5dc92487` and `test_compare_m1_m6.py` `762fac14`. **It REPLACES
  `GRADE-20260825-d3-comparator-repair-fitness.md`, whose mechanical expiry TRIPPED** — two of its
  three pinned digests moved in `63262a3a`, verified not assumed, so the instrument had no live
  grade. **Verdict: FIT to support a future Gate-2 filing, with NO condition** — the prior grade's
  standing precondition ("no partial `M-1` selector in the list at filing time") is now
  unnecessary, because the guard makes one unrepresentable. **`NEWLY ACCEPTED = 0`**, measured over
  **115160** grader-built patterns: the ONLY verdict transition anywhere is
  `ACCEPT -> refused-as-partial-selector` (42224), every other refusal check keeps an
  identically-sized population, and the 50270 rewordings fall in exactly two cosmetic classes with
  no third. Both negative controls re-run and reproduce EXACTLY (revert-the-guard 5 distinct red /
  134 subTests / 0 errors / 0 pre-existing red; over-tighten-to-refuse-literals 6 red including the
  silent-on-good arm and two pre-existing). Producer-derived fixture re-run: **4060 / 210 / 3850 /
  0 escaped**, and the graded **721 / 96 / 0** did not move. **Claim 8's LAST placement: CORRECT**,
  proved by check-identity fingerprinting rather than by reading. **Claim 9: measurement
  reproduced (`M-1[nd-*]` reaches 10 of 10, so the ruling is genuinely syntactic) but the honesty
  claim is OVERSTATED** — the code nowhere records it, and the new invariant arm's docstring frames
  the point AS a reach property that `M-1[nd-*]` satisfies; coverage survives via the 4060-candidate
  sweep, so this is a prose defect, reported and deliberately NOT repaired. **Four claims overstated**
  (the `4840` denominator is unrecoverable — cite `4060`; `field_matches`'s stated ground is wrong
  though the decision is right; four prose sites not three), Its §9 claim that the pre-existing
  "265 of 721" docstring figure does not reproduce is **RETRACTED — see DECISION §13.2**: 265
  reproduces exactly as *refused ∧ one field name ∧ touching no `M-2`*, the D-3 grade had already
  graded and affirmed it, and `accepted` also being 265 is a coincidence (456+265=721). The
  docstring needs a missing qualifier, not a retraction. **Its §8's ratio "517 of the 773" is STRUCK
  by DECISION §12.4** — a property of a generator emitting every path prefix, not of anything a
  reviewer types — so this grade is **NOT CITABLE for that figure**; the rest of §8 stands. §8 is the accepted/rejected shape table the `m1m6_expected_differences.json`
  prose note is to be transcribed from under §12.1. **Grades no F-number, discharges no clause,
  authorizes no rehearsal, no filing and no compute; Gate 2 stays FAIL and open**, and per §10.1 a
  separate readiness check still gates step 4. Expires mechanically when any of three pinned digests
  moves.
- [`GRADE-20260825-f17b-comparison-instrument-fitness.md`](GRADE-20260825-f17b-comparison-instrument-fitness.md) —
  **an independent non-builder's fitness grade of that instrument against the F-17(b) CLAUSE, not
  against the spec.** Graded at `2790ba90` by digest; **records no F-number verdict and no gate
  verdict.** Confirms the builder's rejections by re-derivation — the "any commit" bullet is false at
  **10 of 46** commits by per-commit enumeration, R5's fixture is unbuildable under exact equality,
  and §7.0.9 independently settles the refusal to build an F-7(b) instrument. **34 mutations, 27
  caught behaviourally with the arm named, 6 survivors.** Three demonstrated defects still let an
  obliged difference report as `DIFFERENCES-ALL-EXPECTED` with all 53 arms green: the shipped-list
  guard arm uses `fnmatch`, so it is **blind to `M-1[*]` patterns**; a **one-character** citation
  licenses a suppression; and a **MISSING** measurement is suppressible because `field_set_differs`
  is not a finding — that last one is live in the shipped file today. Also: at that sha the far-end
  script never invokes the instrument, and the filed pre-submission column is **markdown, not
  `--json`**, so it is not consumable by it. **Authorizes nothing.**
- [`VERDICT-20260825-gate2-k0-rehearsal-nine-clauses.md`](VERDICT-20260825-gate2-k0-rehearsal-nine-clauses.md) —
  **the Gate-2 verdict for run `k0-aa67c426-20260824T145751Z`, by an independent non-builder, over the
  NINE clauses of §7.0.18. GATE 2 DOES NOT PASS.** `F-7(b)` and `F-8(b)` have **no evidence of any
  kind** — no rehearsal pin is recorded and no run receipt has been authored — and `F-17(b)`'s
  `:1471` half is **impossible, not pending**, because the pre-submission column is prose and the
  comparator consumes `--json`. `F-1(b)` and `F-4(b)` PASS, re-derived: A-2(a)–(g) all hold at the far
  end, and 374 inventories == 374 guarded processes with the inventory filenames in **bijection** with
  `sacct`'s 374 `JobIDRaw`. `F-2(b)`/`F-5(b)` PASS on measurements this verdict files first (P-2 over
  **all 374** records, 0 sha mismatches against the 782-entry baseline, `checked` min 974).
  **`F-3(b)`'s own instrument is VACUOUS** — these launchers never echo argv, so a stdout grep for
  `--allow` cannot answer it; the guard's `allow_is_empty` field does. **Three producing-lane claims
  did not reproduce**, including a FALSE counterfactual: the excluded sibling's 298 records live under
  `guard-inventories/`, so the `runs/*/inv` glob it was said to protect against yields **374, zero of
  them from siblings**. **New repairable defect:** `bad_pattern` admits `M-1[*` (unbalanced bracket),
  which suppressed **all 19** M-1 findings as `EXPECTED-BY-RULING` with the suite green — the prior
  GRADE has **self-expired** (all three digests moved) and never examined that guard. **Authorizes
  nothing; it is NOT CITABLE FOR any Gate-2 PASS.**

### B1 steps 4-5: the lift, and the preflight that gates the first submission

- [`PLAN-20260822-oneMember-mii-staged.md`](PLAN-20260822-oneMember-mii-staged.md) — **the staged
  one-member request required by ruling 12, and it is a REQUEST, not an authorization.** Read it
  before any M(ii) submission. Carries the measured per-leg costs, the k=0 choice, and two blockers
  that need Joseph: three stale 08-18 replicas inside the chosen member, and family SIZING under the
  pscratch line. **Its "17.8x discrepancy" section is WITHDRAWN** -- 151 and 2 680 count different
  populations, never one quantity; see `PUBLICATION-READINESS-20260822.md` PR-J4.

Added 2026-08-22. The B1 pause is **LIFTED**; read both of these before any submission touching
`nd-unfolding/sbatch_finalize_5d_bkgaware_gpu.sh`.

- [`DECISION-20260822-joseph-b1-lift-and-clause-c.md`](DECISION-20260822-joseph-b1-lift-and-clause-c.md)
  — Joseph's eight rulings of 2026-08-22, including the lift itself and the ruling that the `srun`
  execution satisfies expiry clause (c). **The lift is authorized here and nowhere else**; a relay of
  it is not quotable.
- [`RUNBOOK-20260822-b1-lift-preflight.md`](RUNBOOK-20260822-b1-lift-preflight.md) — required by
  ruling 4. **Its headline is that the launcher must NOT be submitted yet**: both routes refuse today
  for reasons unrelated to the pause, measured on the cluster.
- [`RECEIPT-20260822-k0-n1-and-guarded-arms.md`](RECEIPT-20260822-k0-n1-and-guarded-arms.md) — the
  measured N-1 arm, its paired unguarded hijack control, and the first guarded production arm, run
  on `saul.nersc.gov` against the real canonical checkout. **Read it before quoting F-9 as
  satisfiable**: B-4 script containment now refuses strictly earlier than the import guard can fire,
  so N-1 exits 3 without naming `seed_offset_policy`, and that is a question for Joseph rather than a
  builder's judgement. Also records the one runtime confirmation of M-1 — `adopt_unified_5d.py`
  resolved **213** absolute origins and **zero** repository modules.
- [`REVIEW-CONTRACT-20260822-k0-execution-integrity.md`](REVIEW-CONTRACT-20260822-k0-execution-integrity.md)
  **AMENDED 2026-08-22 (§7.0): §F is now TWO GATES.** Joseph ruled that the contract must separate
  pre-submission readiness from post-rehearsal completion. The eighteen criteria are unedited and
  keep their numbers; §7.0 adds the one-question test that reproduces the partition (8 criteria are
  pre-submission, 10 split, **none** is purely post-rehearsal), the two gates and what each unlocks,
  and the eligibility rule. **If you are grading this contract, read §7.0 before §F.** Two traps it
  names: a NOT-EVALUABLE in the pre-submission column is a FAIL of Gate 1, and "needs the cluster"
  is not "needs a run" — F-9's negative control is pre-submission. **FURTHER AMENDED 2026-08-22 by
  rulings 20-22 (§7.0.11-§7.0.16): F-9 and F-12 are RESTATED.** B-4 containment refuses the
  canonical-checkout wrapper before the import guard installs, so F-9 no longer requires
  `seed_offset_policy` to be named — it forbids it — and **`checked=0` is the EXPECTED value there,
  inverting the anti-vacuity rule that applies everywhere else.** Also lands ruling 21's 14/30
  guarding boundary with the preflight ORDERING requirement graded as a criterion, and ruling 22's
  A-2(d)/(e)/(g) fail-closed checks and P-4 pin-vs-mechanism split. The transferable lesson, and it
  has now recurred twice: **a protection can invalidate the control written to test a different
  protection, and the control then presents as merely unperformed rather than as impossible.**
- [`VERIFICATION-20260822-k0-execution-integrity.md`](VERIFICATION-20260822-k0-execution-integrity.md)
  — the round-1 verdict against that contract: **NOT A PASS**, 7/7/4. It predates the §7.0 split and
  is not revised; it grades build `ae42ae8d`, which is **NOT on main**.
  — **the controls for corrections 2-4, agreed by a fresh non-builder BEFORE the builder implements**,
  on Joseph's instruction that the evidence cannot be selected afterwards. Read it before writing any
  OI-136 wrapper, guard or negative control on the k=0 path. Its headline correction to the plan: the
  pinned adopter `adopt_unified_5d.py` imports **no repository module at all**, so guarding its
  subprocess is vacuous **by construction** and no source repair is authorized there — while
  **five other entrypoints plus one imported module** on legs 1-5 do carry a rooted insert *and*
  import repository code through it, and those are where the scoped source repair belongs. Also:
  the clean tree must be split into a code root and a data root, and `mnv_guarded_run.py` never
  checks that the script it runs is inside `--expect-root`.
- [`GATE1-VERDICT-20260822-k0-execution-integrity.md`](GATE1-VERDICT-20260822-k0-execution-integrity.md)
  — **the GATE-1 verdict against the amended contract: GATE 1 DOES NOT PASS.** Recorded by an
  independent lane that neither built the package nor wrote the §7.0 split, as ruling 23 and §7.0.10
  require. Grades **only** the pre-submission column, against `main` `7165ea5c` — *the build branch
  carries a superseded contract with a different F-9, and a verdict graded against it would be void.*
  Thirteen pass, **five fail** — F-1(a), F-2(a), F-7(a), F-8(a), F-17(a) — and none is recorded
  NOT-EVALUABLE. **F-9 PASSES**, verified on the live cluster records including ruling 20's
  `checked=0` inversion, so the criterion that forced the restatement is closed. What is not closed:
  two executing `.sh` files bound by no `--pair`, the 16-call preflight exclusion enumerated nowhere
  and pinned to nothing, **P-5 and P-6 absent from the package entirely and absent from the builder's
  own gap list**, an A-2(f) digest filed at a superseded sha, and F-17 freshness open. **No
  submission is authorized.** Read §5 for the shortest list that would close the gate, and §2 for
  three builder claims that reproduce differently.

## Task routes

| Task | Route |
|---|---|
| Change code | `KNOWN_ISSUES.md`, relevant status/reference, callers, tests, and hash bindings |
| Quote a result | `VALIDATION_LEDGER.md`, then the exact product or live receipt |
| Run or monitor compute | fresh `LIVE-STATE.md`, direct scheduler observation, then the exact launcher receipt |
| Work on 2D/3D/N-D/PET | relevant workstream status; PET also `PET_UQ_REMEDIATION_STATUS.md` |
| Maintain queue/playbook | [`control-plane/policy.json`](control-plane/policy.json), [`control-plane/source-record-inventory.tsv`](control-plane/source-record-inventory.tsv), then `control_plane_lint.py` |
| Maintain classifications | `MANIFEST-overrides.tsv`, then `generate_manifest.py` |
| Operate continuation | `WAKER.md`, `wakerctl.py`, `waker-config.json`, and `profiles.json` |
| Glance at campaign status | [`RUNBOOK-status-dashboard.md`](RUNBOOK-status-dashboard.md), then `dashboard_collector.py --print-scrontab`; the page is a view, so re-measure before deciding |
| Build deliverables | `docs/analysis-note/build_all.sh` for note, primer, and paper |

## Frozen pre-compaction evidence

Complete history, terminal receipts, long-form findings, audits, determinations, prompts, and old paths
live at:

`evidence/prepublication-2026-08-20-0b329e8a`

Recover a known path without changing the current checkout:

```bash
git show evidence/prepublication-2026-08-20-0b329e8a:<old-path>
```

Search the complete frozen tree:

```bash
git grep '<identifier>' evidence/prepublication-2026-08-20-0b329e8a --
```

The independently stored bundle and recovery proof are recorded in
[`../POST_PUBLICATION_REORG_PLAN.md`](../POST_PUBLICATION_REORG_PLAN.md).

### Anchored-but-unreachable commits — `git fetch github` will NEVER bring these down

Several commits cited in the record are reachable from **no branch**; that is exactly why they were
anchored by `evidence/*` tags. **Git only auto-follows tags that point at objects it is already
downloading**, and `remote.github.fetch` is branches-only
(`+refs/heads/*:refs/remotes/github/*`) with `remote.github.tagOpt` unset — so a tag on a commit
unreachable from `refs/heads/*` can never arrive from an ordinary fetch. **Measured 2026-08-20: six
of the ten `evidence/*` tags on the remote were absent from the main checkout, and `git cat-file -t`
failed outright on all six anchored commits — including `ecee9ff1`, the one carrying
`array_equal True across all 114,361,636 elements`.** Preservation had succeeded; discovery had not,
and a session here would reasonably have concluded the evidence was lost.

Fetch them explicitly — once per checkout:

```bash
git fetch github 'refs/tags/evidence/*:refs/tags/evidence/*'
```

Or make an ordinary `git fetch github` do it permanently, per checkout:

```bash
git config --add remote.github.fetch '+refs/tags/evidence/*:refs/tags/evidence/*'
```

**THE REMOTE NAME IS CHECKOUT-LOCAL — do not hardcode it, and do not trust either name from this
file.** This paragraph read *"The remote is `github`. There is no remote named `origin` —
`git rev-parse origin/main` is fatal"* until 2026-08-21. That is true on the Perlmutter checkout and
**exactly inverted in the local clone**, where `git remote -v` lists only `origin`,
`git rev-parse origin/main` resolves, and `git rev-parse github/main` is the fatal one. A witness
phrased against *either* name is unfollowable in the other tree. Resolve it first and substitute:

```bash
# NAME the remote. Do NOT use `git remote | head -1`.
git remote -v                       # look, then substitute the right name below
git fetch github 'refs/tags/evidence/*:refs/tags/evidence/*'   # on Perlmutter
git fetch origin 'refs/tags/evidence/*:refs/tags/evidence/*'   # in the local clone
```

**`git remote | head -1` IS ITSELF A DEFINITE DESCRIPTION AND IT IS WRONG HERE.** This file recommended
it until 2026-08-21, and it failed the same day it was written: the Perlmutter checkout has TWO
remotes, `analysis-note` and `github`, and `head -1` returns **`analysis-note`** on alphabetical
order. Every downstream number was then computed against the wrong repository -- it reported the
checkout as *"9 behind"* only once the remote was named, having first reported *"behind 94, ahead
2069"*, which was a true measurement of the distance to the ANALYSIS-NOTE repo and meaningless as an
answer to the question asked. **A command that silently answers about a different subject is the
failure mode this campaign keeps paying for; substituting one guess for another is not a fix.**

**The generalisation, and it has now cost this campaign four separate errors:** a remote name, an
interpreter version, a hook's liveness and a file's dirtiness are **properties of a checkout, not of
`main`**. `HANDOFF-20260820-2154Z-publication-closeout.md` §2.1 (a dirty `state/sessions.json` at
51,542 B blocking `MANIFEST.tsv`), §2.2 (`build_all.sh` cannot exit 0) and §2.12 (the pre-commit hook
is inert, 7 of 12 checks `SyntaxError`) are all `login19` facts. Measured in the local clone at
`80eeb441`: `sessions.json` is **clean at its committed 46,746 B**, `core.hooksPath` **is** set, and
the hook reports **12 checks passed** under python 3.12.2. Re-measure with an explicit `-C <path>`
and say which tree you are in.

**Test reachability with `git for-each-ref --contains <sha>`, never `git branch -a --contains`,**
which cannot see tags and will declare an anchored commit disposable.

### The four removed artifacts with no routed citation

`84607aa3` removed 734 tracked files, all under `docs/orchestration`. Most are covered by the generic
route above. **These four were cited by nothing live**, so a reader had no way to learn they exist;
`HANDOFF-20260820-2154Z-publication-closeout.md` §2.11 identified them. They are **recoverable, and
were never lost** — this section is the missing *route*, not a recovery. Restoring the paths into the
live tree is a separate freeze-scope question and is **not** what this section does.

All four resolve at `evidence/prepublication-2026-08-20-0b329e8a`, verified 2026-08-21:

| artifact (under `docs/orchestration/`) | why it matters |
|---|---|
| `runs/standard-p4-verifier/20260811T132822Z-packetB-final-pass.md` | `OI-7`'s PB3/PB4 evidence |
| `runs/standard-p4-verifier/20260817T045149Z-repair12-verdict.json` | supersedes repair-11, which *is* on `main` |
| `AUDIT-20260819-analysis-note-vs-record.md` (1,375 lines) | the only prior enumeration of the 70; bears on `OI-130`, which is 22% enumerated |
| `state/hpss-residency-inventory-20260812.json` | preservation state behind `OI-131` |

```bash
git fetch github 'refs/tags/evidence/*:refs/tags/evidence/*'   # `origin` in the local clone; NAME it
git show evidence/prepublication-2026-08-20-0b329e8a:docs/orchestration/<path-above>
```

**Note the self-contamination, because it recurs in this campaign:** before this section existed, the
`AUDIT` file's *only* live citation was the document reporting that it had none. A write moves the
population it measures — so "cited nowhere" needs a timestamp and a tree, like any other measurement.

**Resolve citations by SHA, not by path.** A path can resolve at HEAD and read a *different* file
with no error. Measured: `nd-unfolding/mii_anchor_comparator.py` is blob `a7cb2d9b…` at both
`ecee9ff1` and `f7ab02ff`, and `cbeac61d…` at HEAD.

## Regenerate

```bash
python3 docs/orchestration/control_plane_lint.py
python3 docs/orchestration/generate_manifest.py
python3 docs/orchestration/generate_manifest.py --check
```

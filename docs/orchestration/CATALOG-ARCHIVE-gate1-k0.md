# CATALOG — archive: the k=0 / Gate-1 rehearsal rounds

**This is a CONTINUATION of [`CATALOG.md`](CATALOG.md), not a document in its own right.** It is
declared there by a `CATALOG-CONTINUES` marker, and `live_doc_indexed.py` reads the two together —
so a pointer row here indexes its document exactly as one in the router does.

**Why it exists.** `CATALOG.md` reached ~4,280 lines, and a reader needs about 500 of them. A
reading guide reduces what you read; it does not reduce what you load. These sections are the
round-by-round history of a rehearsal campaign **closed in August**, each round superseded by the
next, and they were interleaved with live routing.

⚠ **WHAT IS NOT HERE, AND THE OMISSIONS ARE DELIBERATE.**

- **ROUND 11 stayed in `CATALOG.md`.** Its own title records `F-8(a)` and `F-17(a)` as *"filed and
  awaiting grade"*, and this move did not verify that resolved. A section that may still be open is
  not history.
- **`B1 steps 4-5` stayed in `CATALOG.md`.** It reads *"read both of these before any submission
  touching `sbatch_finalize_5d_bkgaware_gpu.sh`"* — standing guidance, not a record of a closed
  round.
- **No live verdict is here.** The surviving Gate-2 disposition lives in
  [`LIVE-STATE.md`](LIVE-STATE.md) and `docs/OPEN_ITEMS.md`. Nothing in this file authorizes,
  grades, or reopens anything.

**Not one character of the moved sections is edited.** They appear below exactly as they stood in
the router, in router order.

---

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

### 🔒 DEPLOYED AND RE-FROZEN AT `7ac0edec`, 2026-08-30

> ⚠ **THIS BULLET WAS THE FIRST TWELVE LINES OF THE FILE, ABOVE THE `#` TITLE, until
> 2026-09-21.** An append landed before the header, so the router opened on a closed
> August quiesce window instead of on its own title. Moved here, beside the deployment
> it is about; not one word of it is changed.

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
 — steps 1–2 historical filing; later grade above

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

---

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

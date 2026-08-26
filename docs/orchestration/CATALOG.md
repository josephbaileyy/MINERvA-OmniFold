# Orchestration router

This is a pointer-only active-tree router. It contains no scientific evidence or authorization.

## Current work

### ✅ GATE 1 PASSES — round 9, 2026-08-23, 18 PASS / 0 FAIL / 0 NOT-EVALUABLE

- [`DECISION-20260824-joseph-deployment-freeze-until-f1b.md`](DECISION-20260824-joseph-deployment-freeze-until-f1b.md)
  — **THE DEPLOYED TREE IS FROZEN AT `aa67c426` UNTIL F-1(b) IS FILED.** No `checkout`, `reset`,
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
  F-14 / §7.0.7.

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
  in one day, one of them with the warning's own sentence recorded as the reasoning. **Owned defect
  with an unassigned owner** — a repair must add an arm that FIRES on dirty-and-not-staged, stays
  SILENT on dirty-and-fully-staged, and covers the opposite direction (staged but not committed),
  which an obvious implementation will miss. **NOT** citable for any Gate-2 clause, **does not alter
  Gate 2's FAIL**, is not part of the D-3 repair, and excuses no omission.


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
  docstring needs a missing qualifier, not a retraction. §8 is the accepted/rejected shape table the `m1m6_expected_differences.json`
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

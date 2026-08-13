# FINDINGS ledger — benchmarking / orchestration findings

Each finding has a `cross_stream` pointer to the physics claim(s) it produced (in `CLAIMS.md`). Long-form
detail lives in sibling `FINDING-<YYYYMMDD>-<slug>.md` files **in this directory** — indexed below.

> Corrected 2026-08-06: this header previously pointed detail at `../benchmarking/findings/`, a directory
> that does not exist. An agent following that pointer hit a dead end, which is one reason findings written
> here were not reaching the agents that needed them.

> **BEN id allocation — take the next id from YOUR LANE'S BLOCK. Never `max(existing)+1`.**
>
> | lane | block |
> |---|---|
> | D — verifier | `090-099` (exhausted) |
> | B — uncertainty construction | `100-129` |
> | C — PET | `130-159` |
> | D — verifier, successor | `160-189` |
> | A — orchestrator | `190-199` |
> | repo infrastructure (ledgers, read path, dispatch machinery) | `200+` |
>
> The highest id allocated per block is **derived, not narrated** — the table that used to state it
> here was wrong in three of five rows within a day of being written. Recompute before allocating:
>
> ```
> grep -oE '^\| BEN-[0-9]+' FINDINGS.md | grep -oE '[0-9]+' | sort -n | tail -1
> ```
>
> **Enforced by attentiveness, not by an allocator — and attentiveness has failed four times, twice
> while the failing agent was reading this rule.** BEN-080 records the exposure as *"known and
> accepted, not fixed"*; BEN-105 counts the instances. Re-read your block *at the moment of
> allocation*, which is exactly when `max(existing)+1` feels right.
>
> Old commit messages cite pre-renumber ids (BEN-077→061, 078→062, 079→063, 080→064). That mapping
> and the full policy history: [`FINDINGS-POLICY-HISTORY.md`](FINDINGS-POLICY-HISTORY.md).

> **BEFORE QUOTING ANY NUMBER: `INDEX-retracted-and-superseded-values.md`** (added 2026-08-11). Retracted values stay
> readable and are presented with the same confidence as live ones — the `188.4x` and the *"code paths disagree"* verdict
> sat in `VALIDATION_LEDGER.md`, the canonical home for technote-quoted numbers, until they were bannered. The index's
> load-bearing column is **where each dead value still appears**, because the corrections already existed; the map to the
> stale copies did not.

## Long-form findings index

Every `FINDING-*.md` in this directory must appear here. A finding that is not indexed is a finding nobody
will read.

| file | subject |
|---|---|
| `FINDING-20260730-event-feature-nonfinite.md` | `build_event_features` has no non-finite guard; a single NaN kills step 2 |
| `FINDING-20260802-estimator-definition-vs-driver.md` | The contract defines the nominal estimator with a batch size the driver does not use |
| `FINDING-20260802-extractor-pass-truth-mask.md` | The full-event extractor omits the `pass_truth` mask, and its own guard blesses it |
| `FINDING-20260802-orchestration-tests-never-run.md` | 99 control-plane tests exist, are never collected, and 20 are red |
| `FINDING-20260804-b4-is-active-gate2-cannot-be-reissued.md` | B-4 is ACTIVE; the first real post-restore Gate-2 run answered it |
| `FINDING-20260804-gate2-units-resolved-gev.md` | RESTORE Step 2 resolved: the dump is GeV, Gate-2's independent check holds |
| `FINDING-20260804-step3-closure-needs-root-and-tf-in-one-interpreter.md` | Step 3 closure needs ROOT *and* TF 2.15 in one interpreter |
| `FINDING-20260804-step7b-corr-cosphi-pt-measured.md` | RESTORE Step 7b measured: corr(cos φ, pT) ≈ +0.002 to +0.006 |
| `FINDING-20260804-wakerctl-tick-correction.md` | CORRECTION: the waker tick is not broken; it runs clean |
| `FINDING-20260806-campaign-pin-inverted-on-insignificant-variance.md` | A campaign pin was inverted on a variance estimate that was never significant (BEN-025) |
| `FINDING-20260806-j28-reroll-exact.md` | The exact J28 re-roll: the Flux block was *understated* ~4.2x, and it covered 122 of 160 adopted throws (BEN-033) |
| `FINDING-20260806-niter4-decision.md` | `niter=4` measured: bias falls 1.535x at flat variance, but the 0.80 bar is unreachable at any k<=39, so k=3 stands (discharges CLM-010 (ii)) |
| `FINDING-20260807-d2-underfitting-probe.md` | The D2 shortfall is **97.8% per-bin scatter, not bias**; 0.6332 is a reference curve, not a bound (BEN-037, BEN-038) |
| `FINDING-20260807-d2-response-reference-point.md` | The D2 miss is **81.4% coherent under-application of the tilt**, 18.6% dispersion; seed-ensembling caps at 0.6313 for any N |
| `FINDING-20260807-checkpoint-is-not-the-trained-model.md` | **The saved step-2 checkpoint is not the model that produced `weights_push`**, and last-epoch weights were never written to disk |
| `FINDING-20260807-step1-under-achieves.md` | **Step 1 is correct at iteration 0 and degrades later** — the failure is iteration dynamics after feedback, not a defect at push=1 |
| `FINDING-20260807-d2-acceptance-limited-oracle.md` | **72% of D2's shortfall is SPECIFICATION, 28% the estimator**: acceptance-limited ceiling 0.618228 against a 0.80 bar (BEN-045) |
| `FINDING-20260807-gates-that-cannot-fail-sweep.md` | Repo-wide sweep for gates that cannot fail: one new instance in 624 files (`p4_lib.py:219`, absolute floor 2.6e+55x too large) |
| `CONVENTION-receipt-ingredients.md` | **CONVENTION (2026-08-10): every derived quantity in a receipt ships the ingredients that let a reader recompute it** — enough that reported numbers CAN contradict each other (BEN-077) |
| `SCOPING-20260810-engine-rebaseline-cost.md` | **What a change to `omnifold.py` would cost — SCOPING ONLY, not a recommendation.** The cost is the re-verification chain, not GPU-hours; `omnifold.py` is NOT among the live Gate-4 gate's 17 pins |
| `FINDING-20260810-criteria-that-answer-a-different-question.md` | **Four criteria in four days answered a subtly different question than the one asked** — none an arithmetic error |
| `VALIDATOR-TOLERANCE-UNITS-20260808.md` | Validator tolerance-units audit: absolute tolerances compared against quantities whose scale makes them unfailable |
| `FINDING-20260809-tparameter-merge-semantics.md` | `hadd`/`TParameter`: summing is correct for an **extensive** quantity and wrong for an intensive one, a constant, or a flag; 15 of 62 fields transit a `hadd` |
| `FINDING-20260809-derived-from-merged-extensives.md` | **J36 is EIGHT sites, not one** — the derived-from-merged-extensives class, sized for the first time (3 are production unfolders) |
| `FINDING-20260809-stage6-central-gate-cannot-pass.md` | **Stage 6 cannot pass as specified**: 5D->4D marginal vs independent 4D disagree at median 4.43% against a 3% per-bin gate, while integrals agree to 0.56% |
| `FINDING-20260809-what-the-fifth-axis-buys.md` | **W is ~69% redundant with (E_avail,q3)** — and the residual sits exactly where the excess claim lives |
| `FINDING-20260812-orchestrator-instrument-defects.md` | **Orchestrator instrument defects**: a settings edit to the wrong config dir verified only by its contents; a staleness detector made honest about a condition it cannot escape; three disagreeing status sources; coverage invisible by construction (7 instances); a containment refusal misread as permissions; a deferred item whose payload was never written; a denominator that certified the emptiness it guarded — plus a third `BEN-069` timezone instance routed to its owner (BEN-190…196) |
| `FINDING-20260812-retraction-reached-the-peer-not-the-decider.md` | **A concession reasoned through and never uttered**; filed first with the wrong mechanism (the BEN-112 shape) |
| `FINDING-20260811-gate4-prerequisite-points-at-a-deleted-blocker.md` | **The live Gate-4 receipt asserts a Gate-2 re-issue is pending that landed five days earlier**, citing a key deleted nine receipts ago |
| `FINDING-20260811-trajectory-label-is-direction-blind.md` | **A fallback verdict branch whose MESSAGE is more specific than its CONDITION** — the trajectory label is direction-blind |
| `FINDING-20260811-promotion-by-move-silently-repoints-artifacts.md` | **Promoting a PET nominal by MOVING it re-points the superseded artifact at the NEW estimator's weights**; already fired 2026-08-07 |
| `FINDING-20260811-dead-containment-evadable.md` | **`check_dead_containment.py` returns PASS while a struck retracted value renders in `main_paper.pdf`** — `\dead {x}` with one space evades the regex |
| `FINDING-20260812-gate-passes-on-empty-lane.md` | **`whose_row.py --lane ""` exited 0 on a foreign row** — the predicate was right and was never consulted; a unit check cannot see a short-circuit that skips it (BEN-117) |
| `FINDING-20260812-nested-conflict-markers-false-pass.md` | **NESTED conflict markers false-passed a foreign row** — boolean scoping, so rows after an inner close escaped attribution; the battery was rebuilt for the function that had failed and not for the one beside it (BEN-162) |
| `FINDING-20260812-session-health-metric-counts-its-own-subject.md` | **The session-health metric counted the word `compact`, not compactions** — all four lanes have exactly 2, and three were about to be retired on a 2.8x spread in a quantity that is identical (BEN-165) |
| `FINDING-20260812-exit-contract-drifted-into-prose.md` | **The gate learned exit 2 and its published contract did not** — the code was fixed and the only document an operator reads was not, so CANNOT CHECK reads as success at the caller (BEN-163) |
| `FINDING-20260812-power-test-axis-selection.md` | **A power test covered the inputs and not the evidence class the conclusion rested on**: 20 checks green, 5 mutations caught, and every one left the verdict's own checks green. Third axis after BEN-162 and BEN-117; none implies the others (BEN-119) |

| `CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md` | Discharge criteria for quarantine causes 1/2/3/4/6 — what each cause requires before it can be closed |


> **This is the ACTIVE ledger: one line per finding.** The full text of every row —
> unchanged, byte for byte — lives in [`FINDINGS-ARCHIVE-2026-08.md`](FINDINGS-ARCHIVE-2026-08.md). To read a
> finding in full, `grep -n 'BEN-0XX' docs/orchestration/FINDINGS-ARCHIVE-2026-08.md`.
> **Add new findings here as one line (≤240 chars) and put the long form in a
> `FINDING-<date>-<slug>.md`.** A row that outgrows one line is a row that belongs in
> its own file — this ledger reached 330 KB (≈78k tokens, 73% of a context window when
> combined with the rest of the prescribed read path) because that rule had no enforcement.

| id | finding | cross_stream | episode |
|----|---------|--------------|---------|
| BEN-120 | **The duplicate-id gate covers 1 of the 4 id-bearing ledgers — and today's collision was in another.** `--check-ledger-ids` runs on VALIDATION_LEDGER.md alone; OI-48 was allocated 3x in an hour. Density is VL-only, duplicates are universal. | — | EP-2026-08-12-closeout |
| BEN-119 | **20 checks green, 5 mutations caught, and none touched the conclusion.** A check carrying the verdict reads as a restatement and goes untested. Name the AXIS a battery covers. [Detail](FINDING-20260812-power-test-axis-selection.md) | — | EP-2026-08-12-closeout |
| BEN-118 | **An overage notice fired 49 s into a 322 GB copy that did not cause it**: an archive 14 h older held 77.9%. Dedup frees 12 kB of 1.46 TB — a digest-verified archive has no slack. [Receipt](state/hpss-residency-inventory-20260812.json) | — | EP-2026-08-12-closeout |
| BEN-204 | **A format rule given to a delegate became a licence to delete another session's committed content.** Told "pipe tables only" for `OPEN_ITEMS.md`, it deleted a peer's nine-line handoff blockquote committed minutes earlier. Scope rules must name what may be **edited** — a path allow-list — not only what the output must look like. [full](FINDINGS-ARCHIVE-2026-08.md) | — | EP-2026-08-12-readpath-audit |
| BEN-203 | `git status` is not an attribution instrument: **six live `claude` processes share this one checkout**, so the tree shows the union of everyone's work. Acting on the standing rule, I nearly reverted a peer's legitimate fix as delegate overreach. Stage and commit with explicit pathspecs. [full](FINDINGS-ARCHIVE-2026-08.md) | — | EP-2026-08-12-readpath-audit |
| BEN-202 | The cheapest orientation in the repo was reachable only by agents who already knew about it: `LIVE-STATE.md` is regenerated every turn and self-describes as "the normal-turn control-plane entrypoint", and 19 files cited it — but **neither `CLAUDE.md` nor `AGENTS.md`**, the two entry points a fresh session is guaranteed to read. Inbound-reference count is not reachability; what matters is whether a *guaranteed-read* file names it. | — | EP-2026-08-12-readpath-audit |
| BEN-201 | A retraction that lands in the index but not at the point of use is not a retraction. `recovery >= 0.80` was retired 2026-08-09 and correctly indexed, yet on 08-12 `docs/OPEN_ITEMS.md` still stated it as the live Gate-4 blocker: **two read-path files disagreed on a gate criterion, and the stale one was phrased as the blocker.** [full](FINDINGS-ARCHIVE-2026-08.md) | CLM-012 | EP-2026-08-12-readpath-audit |
| BEN-117 | **`whose_row.py --lane ""` printed `OTHER` for a foreign row and exited 0** — the falsy lane short-circuited both guards. **The predicate was correct and a self-test asserted it; the answer was never consulted** — a unit check cannot see a short-circuit that skips it, so test a gate's exit code as an exit code. [Detail](FINDING-20260812-gate-passes-on-empty-lane.md). | — | EP-2026-08-12-closeout |
| BEN-144 | **I told a peer "it is your file" about a gate neither of us wrote, in the same message where I was careful not to edit it.** [full](FINDINGS-ARCHIVE-2026-08.md) | — | EP-2026-08-12-closeout |
| BEN-143 | **Git worktrees share `refs/remotes/*` while `FETCH_HEAD` is private, so a peer's fetch silently moves YOUR `origin/main` and your own fetch record cannot tell you.** [full](FINDINGS-ARCHIVE-2026-08.md) | — | EP-2026-08-12-closeout |
| BEN-142 | **THREE lanes independently allocated `OI-48` for the same topic within one hour — A, B and C — and prefixing did not help because the collision was in ALLOCATION, not in NAMESPACE.** [full](FINDINGS-ARCHIVE-2026-08.md) | — | EP-2026-08-12-closeout |
| BEN-141 | **The answer was on the login node in a differently-named SIBLING of the tool I ran, and my negative result was reported as a property of the machine.** [full](FINDINGS-ARCHIVE-2026-08.md) | — | EP-2026-08-12-closeout |
| BEN-140 | **`hsi hashlist <directory>` returns EMPTY and exits 1, and I read that as "the 1.135 TB archive carries no stored digests, so it cannot be verified without re-reading a terabyte."** [full](FINDINGS-ARCHIVE-2026-08.md) | — | EP-2026-08-12-closeout |
| BEN-200 | A ledger too expensive to read is not read: the prescribed read path measured ~146k tokens — 73% of a 200k window — before any work, and FINDINGS.md was cited in 0 of 83 dispatch prompts, so its findings kept recurring. | — | EP-2026-08-12-ledger-read-cost |
| BEN-116 | I filed "a print is not a check" at 21:00 and then made the same claim in prose three times before dawn — because BEN-112's rule was scoped to the MEDIUM of its first instance, and the medium changed. | — | EP-2026-08-11-closeout |
| BEN-115 | The git INDEX is shared mutable state, so `git diff --cached --stat` is a TOCTOU read and not a guard — three lanes scrambled three commits inside one four-minute window while all three were correctly applying the published remedy. | — | EP-2026-08-11-closeout |
| BEN-114 | "The suite is green except the 7 known failures" was a claim about a SUBTREE, and I made it four times without ever naming the subtree. | — | EP-2026-08-11-closeout |
| BEN-113 | `git add -A` on a shared four-session checkout swept NINE files I never authored into a commit whose message describes none of them — and the message is the only thing anyone reads. | — | EP-2026-08-11-closeout |
| BEN-171 | **The convention's *"only technique that ever caught an absorption"* sentence is SUPERSEDED, and it is the sentence that justifies the remedy.** C's declare-the-set guard caught one prospectively and two-sided, which the sentence says is impossible. True when written, so supersession, not error. [full](FINDINGS-ARCHIVE-2026-08.md) | — | EP-2026-08-12-worktree-migration |
| BEN-170 | **BEN-166's repair prescribes the instrument that caused BEN-166.** The banner prescribes `awk '{print length($0)}'` — bytes on BSD awk, characters on GNU — the same command that caused the defect, answering by platform. [full](FINDINGS-ARCHIVE-2026-08.md) | — | EP-2026-08-12-worktree-migration |
| BEN-169 | **The merge gate prints `examined 0 file(s), 0 attributable row(s)` and in the same breath asserts `you are not the author of every contested row`** Both variants reproduced. The absent-file one regresses my own BEN-162(a) repair, 0→1 past the code meant for it. Fail-safe in direction, wrong in diagnosis. [full](FINDINGS-ARCHIVE-2026-08.md) | — | EP-2026-08-12-worktree-migration |
| BEN-168 | **An absence of the answer in the tools you thought of is not an absence of the tool.** Two lanes probed four wrong command names and called the HPSS quota unreadable; it is `hpssquota`. A negative result needs its candidate set stated. [full](FINDINGS-ARCHIVE-2026-08.md) | — | EP-2026-08-12-worktree-migration |
| BEN-167 | **A LIVE BEN id collision, and the documented allocator cannot see it.** The prescribed allocator greps ROWS, so an id cited in prose and CODE but never filed is invisible to it. Resolved by A at `17698cd`; my remedy was wrong. [full](FINDINGS-ARCHIVE-2026-08.md) | — | EP-2026-08-12-worktree-migration |
| BEN-166 | **`CONVENTION-lane-worktrees.md` states its row-length threshold in CHARACTERS and quotes BYTES** `1032` is 1028 chars / 1032 bytes. The one figure that agrees is pure ASCII — the example a reader spot-checks cannot show the discrepancy. [full](FINDINGS-ARCHIVE-2026-08.md) | — | EP-2026-08-12-worktree-migration |
| BEN-165 | **The session-health metric counted DISCUSSION of compaction, and all four lanes have the same true count.** From `isCompactSummary`, every lane has exactly 2; the spread tracks lines containing the word. A substring metric penalises the lanes doing the verifying. [full](FINDINGS-ARCHIVE-2026-08.md) | — | EP-2026-08-12-worktree-migration |
| BEN-164 | **A backtick in a `git commit -m` string silently DELETED a clause from the commit body** A backticked id ran as a command and the clause vanished; the amend then orphaned the sha I had cited. `-F <file>`, never `-m`; re-resolve shas after an amend. [full](FINDINGS-ARCHIVE-2026-08.md) | — | EP-2026-08-12-worktree-migration |
| BEN-163 | **The gate learned exit 2 and the document that teaches its contract did not.** The script returned 0/1/2 while the convention said "exit 1" and "42 checks", so a faithful wrapper reads CANNOT CHECK as success. Moved into prose, which has no self-test. [full](FINDINGS-ARCHIVE-2026-08.md) | — | EP-2026-08-12-worktree-migration |
| BEN-162 | **`whose_row.py` false-passed a contested FOREIGN row when conflict markers NEST.** Boolean scoping, so rows after an inner close escaped attribution and lane D passed on lane C's row. The battery was rebuilt for the function beside it, not this one. [full](FINDINGS-ARCHIVE-2026-08.md) | — | EP-2026-08-12-worktree-migration |
| BEN-161 | "No self-applied instrument closed a gap tonight" is FALSE — I wrote it, a peer adopted it into the ledger as superseding their own version, and the true partition is sharper than the claim it replaced. | — | EP-2026-08-11-four-session-closeout |
| BEN-160 | In a shared checkout where every lane commits under ONE git identity, no git command attributes a commit to a lane — so an agent auditing *"did I absorb a peer's work?"* cannot tell its own commits from anyone else's, and resolving that by… | — | EP-2026-08-11-four-session-closeout |
| BEN-099 | A claim that ANOTHER artifact contains something is never checked — five instances in one night, including one of mine, and every one of them was one `grep` from being caught. | — | EP-2026-08-11-four-session-closeout |
| BEN-097 | BEN-084(B)'s remedy — *put the literal command in the header* — WAS IMPLEMENTED, complete with a named warning about this exact mistake, and the mistake recurred anyway. The remedy is refuted as sufficient. | — | EP-2026-08-11-four-session-closeout |
| BEN-098 | A status file's STALE sections are exactly the ones that were true when written, so nothing — no reader, no test — can tell them from current ones. "In flight" does not self-expire. | — | EP-2026-08-11-four-session-closeout |
| BEN-096 | An OCCURRENCE-COUNT pin is not a CONTENT pin — and I said it was, in a justification another lane adopted verbatim into a commit body. | — | EP-2026-08-11-four-session-closeout |
| BEN-095 | A completeness checker whose docstring says "every occurrence in the tree" searches `.py` and `.sh` only — 74 occurrences in 33 other tracked files are outside it — and there is a FIFTH spelling class it cannot see from any corpus, because… | — | EP-2026-08-11-four-session-closeout |
| BEN-094 | `git add` is not a private act in a shared working tree: another session's commit swept my staged rows into itself, and the content landed under a subject that describes something else. | — | EP-2026-08-11-four-session-closeout |
| BEN-092 | The orchestrator's "which completed jobs are unfiled" step greps COMMIT MESSAGES, so a job filed in a tracked ARTIFACT reports as unfiled — and the cheap fix for it fails in the opposite, work-losing direction. | — | EP-2026-08-11-four-session-closeout |
| BEN-093 | A declared blind spot that happens to exclude the known instance is not a limitation — it is a detector that cannot find the thing it was built to hunt, and it reports CLEAN. | — | EP-2026-08-11-four-session-closeout |
| BEN-112 | My fix for "the product cannot prove its own provenance" printed *"provenance stamped"* while all nine stamps silently failed to be written — caught only by reading them back out of the product, which is the same check the fix exists to en… | — | EP-2026-08-11-closeout |
| BEN-111 | A pre-registered VALUE decided a question that my own pre-registered PROSE would have decided wrongly — and the prose failed by containing the exact conflation the run was testing for. | — | EP-2026-08-11-closeout |
| BEN-110 | A repair that names its defect class fixed one projector and left the identical construction unguarded in another — and the second one is the projector quarantine cause 6 is about. | — | EP-2026-08-11-closeout |
| BEN-109 | A before/after pair computed on two different ensembles, for the THIRD time in one session — and this instance sits inside the evidence for the one quarantine cause whose criterion was predeclared. | — | EP-2026-08-11-closeout |
| BEN-108 | A power test is only as good as its FIXTURE, its ORDERING and its PRESENCE assertion — measured, with the mutation counts, on the `wakerctl.scan()` guard. | — | EP-2026-08-11-closeout |
| BEN-091 | Three receipt pins name content that exists in NO revision of the repository — dangling, not stale — and the live gate is clean, which is why the raw count would have misled. | — | EP-2026-08-11-four-session-closeout |
| BEN-090 | A text-matching gate over a LANGUAGE is only as strong as its agreement with that language's parser — and this one was written to close a gates-that-cannot-fail exposure. | — | EP-2026-08-11-four-session-closeout |
| BEN-107 | A predeclared branch set protects you only over the object you scoped it to — and mine was scoped to one artifact where the chain has two hops. | — | EP-2026-08-11-closeout |
| BEN-106 | The adopted covariance carries no record of how it was constructed: every contract stamp stops one hop upstream, at a file no receipt names. | — | EP-2026-08-11-closeout |
| BEN-100 | A cause list without a per-artifact column reports another product's progress as your own — and it was one edit from deleting a live publication gate. | — | EP-2026-08-11-closeout |
| BEN-101 | The construction contract of the campaign's headline covariance is provable only from a file that is not in the repository, so four of seven quarantine causes have a provenance leg that cannot currently be satisfied at all. | — | EP-2026-08-11-closeout |
| BEN-102 | Two numbers proposed for the paper differ from the ones they would replace in TWO inputs, one of them a silent argparse default — and it was caught by a macro failing to derive from a ledger operand. | — | EP-2026-08-11-closeout |
| BEN-103 | Four documents cite the only predeclared discharge criterion in the campaign by a line number that no longer contains it, and the file guarantees that outcome because it is prepend-ordered. | — | EP-2026-08-11-closeout |
| BEN-104 | The launcher that produced the two numbers proposed for the paper truncated its own log at write time. | — | EP-2026-08-11-closeout |
| BEN-105 | The BEN namespace is exhausted inside its own documented ranges, and the next allocation by either rule is a collision. | — | EP-2026-08-11-closeout |
| BEN-089 | A polling loop with no priority between channels starves the low-volume one — and the low-volume channel is the human. | — | EP-2026-08-11-four-session-closeout |
| BEN-130 | The live Gate-4 receipt asserts a Gate-2 re-issue is pending that landed five days earlier, and cites it with a pointer to an `open_blockers` key deleted nine receipts ago. | — | EP-2026-08-11-closeout |
| BEN-131 | A fallback verdict branch whose MESSAGE is more specific than its CONDITION: it tests `\|dev\|> 0.10` and asserts a direction, so it printed *"step 1 under-achieves at iteration 0"* for a measured 11.01% OVERSHOOT. | — | EP-2026-08-11-closeout |
| BEN-135 | A test-driven fix applied to the WRONG SIDE of a test can break a hash binding, and nothing in the failure message says which side is pinned. | — | EP-2026-08-11-closeout |
| BEN-136 | In this tree, artifact and launcher names are systematically PREFIXES of one another, so every name-based exclusion is a SUBSTRING exclusion unless anchored — three instances in one night, the third hiding a load-bearing site from every in… | — | EP-2026-08-11-closeout |
| BEN-137 | A predeclared branch set is a SCOPE, and the quantity it scopes out can become the caveat on its own verdict — here the excluded iteration was a de facto NULL CONTROL for the treatment, and it FAILED. | — | EP-2026-08-11-closeout |
| BEN-138 | A predeclared provenance requirement was PRINTED and not PERSISTED, and the lane that wrote the requirement then cited the receipts as if they carried it. | — | EP-2026-08-11-closeout |
| BEN-139 | A concession you only REASONED THROUGH was never delivered to anyone [detail](FINDING-20260812-retraction-reached-the-peer-not-the-decider.md) · [full](FINDINGS-ARCHIVE-2026-08.md) | — | EP-2026-08-11-closeout |
| BEN-134 | BEN-094's remedy does not cover a NEW file, and the gap it leaves is exactly the window the collision lands in — measured by it happening to me, within the hour, while I was applying the remedy. | — | EP-2026-08-11-closeout |
| BEN-133 | A promotion that MOVES the outgoing artifact silently re-points it at the incoming estimator's weights, because the artifact embeds an ABSOLUTE checkpoint path that does not move with it — and the previous promotion already did this. | — | EP-2026-08-11-closeout |
| BEN-132 | A guard that scans every line including comments cannot be satisfied by a launcher that DOCUMENTS the anti-pattern it avoids — the prose explaining why we do not do the bad thing fails the test for not doing it. | — | EP-2026-08-11-closeout |
| BEN-088 | A count taken from a non-converged multi-pass build is a transient, not a property of the document — and it reads as a defect list. | — | EP-2026-08-10-annealed-reproduction |
| BEN-087 | Updating a value inside a sentence that NAMES ITS SOURCE silently re-points the source claim — a true sentence becomes false with nobody editing it into falsehood. | — | EP-2026-08-10-annealed-reproduction |
| BEN-086 | An `UNSOURCEABLE` verdict is a statement about the SEARCH, not about the value — and treating it as a defect manufactures one. | — | EP-2026-08-10-annealed-reproduction |
| BEN-085 | The `BLOCKED-ON-USER` file re-pages the user on ANY touch, because its notification key is the file's mtime — so a tree operation can re-send a superseded decision request, and one nearly did. | — | EP-2026-08-10-annealed-reproduction |
| BEN-084 | A fired watch records that a job finished; nothing records that nobody has looked. "Fired" and "read" were indistinguishable from outside the session, and that is what let a completed result sit 2.5 h. | — | EP-2026-08-10-annealed-reproduction |
| BEN-083 | Prove the artifact under test is the artifact you LOADED — hash the resolved `__file__` after import, not the path you set. | — | EP-2026-08-10-annealed-reproduction |
| BEN-082 | Ask of any claim, your own or a received one: "what would be false if this were wrong?" An observation consistent with both a claim and its negation is not evidence for it, however cleanly it fired. | — | EP-2026-08-10-annealed-reproduction |
| BEN-080 | "B1" names two different things in two lanes, and one lane's "B1 closed" commit reads as unblocking the other lane's only remaining gate item. | — | EP-2026-08-10-annealed-reproduction |
| BEN-079 | A bare count is not an announcement. | — | EP-2026-08-10-annealed-reproduction |
| BEN-081 | Hash-pinning a package file does not make its package importable; launchers must preflight the import path they actually execute. | — | EP-2026-08-09-step1-dynamics |
| BEN-001 | Interpretation personas localize a hidden assumption but converge uselessly on a physics crux; use physics-split personas for that. | CLM-007 | EP-2026-07-08-interpretations |
| BEN-002 | Adversarial structure (falsifiable concessions, sign-able verdicts) is required; free discussion yields premature/false consensus. | — | EP-2026-07-08-freeturn |
| BEN-003 | Novelty limit is set by question depth, not round count; stop on saturation signals (concede / same-residual / propose-the-theorem). | CLM-004 | EP-2026-07-08-extended-rounds |
| BEN-004 | Hallucination-as-signal works with verification; the same pass caught 3 fabricated citations. | CLM-004, CLM-005 | multiple |
| BEN-005 | For a theorem-shaped residual, use N independent METHODS not personas; a locatable disagreement is the insight. | CLM-005 | EP-2026-07-09-marginal-floor |
| BEN-006 | Parallel dual-panel + flat topology scales cleanly; panels reinforce each other; flat control preserves citation verification. | CLM-005, CLM-009 | EP-2026-07-09-* |
| BEN-007 | Contrarian concession forced by "produce X or concede" + a cross-panel verified referee constraint = strongest clean-convergence signal. | CLM-009 | EP-2026-07-09-edge-modes |
| BEN-008 | MAX reasoning is load-bearing for frontier insights (affine-weight, center-label, thermal-noise floor appeared only at xhigh/opus-max). | CLM-004, CLM-005 | EP-2026-07-08/09 |
| BEN-009 | Naive-expert/fresh-eyes format (generalists, no subtopic background) is highly productive: validates results by translating them into an unrelated field's language and surfaces edge cases specialists gloss (found the marginal p=2 case + th… | CLM-005, CLM-009 | EP-2026-07-09-conference-etaR |
| BEN-010 | Conference-style (broadcast talks, N lenses, moderator synthesizes) gives fast parallel breadth/synthesis; complementary to routed debate (adversarial depth on one crux). | CLM-009, CLM-011 | EP-2026-07-09-conference-etaR |
| BEN-011 | Usage-limit probe: no account hit a hard server rate-limit up to codex ×32 / gemini ×16 concurrent. | — | campaign-2026-07-09 |
| BEN-012 | Blind idea-rate benchmark (4 arms × n=8, dual graders, orchestrator verification): gpt-5.6-sol one-shot survivor rate ≈ 2× gpt-5.5 (6/8 vs 3/8); grader means DON'T discriminate (7.75 vs 7.69) — verification-surviving novelty does. | — | EP-2026-07-09-idea-rate-study |
| BEN-013 | New-generation codex models: ZERO fabricated citations and zero anchor-arithmetic errors across 32 cards / 44 resolved IDs (prior generation: 3 fabrications in this project). | — | EP-2026-07-09-idea-rate-study |
| BEN-014 | Self-audit is real work: gpt-5.6-sol's revision pass caught 4 genuine flaws in its own cards — including a scoop (Faulkner–Hollands 2006.08002) that the orchestrator's verification missed — and replaced 4/8 own cards (gpt-5.5: 1/8). | — | EP-2026-07-09-idea-rate-study |
| BEN-015 | Dual cross-model graders are a reliable fatal-filter (34/34 fatal agreement; 4/4 calibration plants caught) but an unreliable ranker (Spearman 0.12; gemini ceiling: 19/34 tens). | — | EP-2026-07-09-idea-rate-study |
| BEN-016 | Quota planning number: ≈16–20 codex xhigh+web-search generation calls fit one 5-h usage window per account (16 jobs + 6 probes tripped the cap; the next window absorbed 16 jobs comfortably). | — | EP-2026-07-09-idea-rate-study |
| BEN-017 | Account-capacity numbers (measured to the actual caps): claude-school session limit FOUND — error "You've hit your session limit · resets 11:40am" after 42 successful opus+search -p jobs in one 5-h window from a 6% start (3 heavy derivatio… | — | EP-2026-07-10-lead-vetting |
| BEN-018 | Vetting methodology: single-card audits all passed a kernel that was inconsistent ACROSS cards — only a cross-card unification dispatch surfaced it, and only a ground-truth computation (not adjudication-by-argument) resolved it (outcome: b… | — | EP-2026-07-10-lead-vetting |
| BEN-020 | Verifying a COMMITTED self-validated milestone with 4-family redundancy: each family caught a class the others missed — codex code-audit found the only real BLOCKER (silent input fallback) + design flaws in both closures; claude-school arc… | CLM-001..008 | EP-2026-07-16-p5a-verify |
| BEN-021 | The orchestrator's own derivations need the same verification routing as worker claims: the CLM-009 "emergent max(0,·) floor" overclaim survived the orchestrator's self-check and was refuted by a delegate prior-art pass that recomputed the… | CLM-009 | EP-2026-07-16-sieve-reduction |
| BEN-022 | Shared-dirty-repo mechanics for concurrent-agent campaigns: (1) `git subtree push` works from a dirty tree (split reads committed history) but `git subtree pull` hard-fails — plan pulls via a clean temp worktree, or verify the remote hasn'… | — | EP-2026-07-16-fe-campaign-setup |
| BEN-023 | Resume-skip must validate completeness, not existence: a `[[ -s $OUT ]] && skip` guard let 7 partial slab files (atomic per-throw saves from an interrupted interactive run) permanently block their own repair — 40/40 array tasks "COMPLETED"… | CLM-006 (D-chain repair) | EP-2026-07-17-coordination-takeover |
| BEN-024 | Delegate-session watchers are the weakest link in multi-hour chains: four independent deaths in one day (C's 120/120 monitor bounced in a usage-cap window; B's two salloc-based validations died at session teardown; both agents' post-comple… | CLM-006 campaign ops | EP-2026-07-17-coordination-takeover |
| BEN-025 | Small-sample spread estimates must not overturn decisions: a 16-seed measurement reading "sd GREW 56%" (0.7477%→1.1703%) inverted an advisor's ranking, discarded its correct Rank 1, and produced a tolerance-RAISE recommendation the user ap… | — | EP-2026-08-05-gate4-reissue |
| BEN-029 | Converting a launcher to the BEN-023 content-validated guard has two traps the size-only test does not catch, both hit while repairing the last three offenders on 2026-08-06. | — | EP-2026-08-06-ben023-final-three |
| BEN-031 | Never `git stash -u` on the shared cluster tree. | — | EP-2026-08-06-shared-tree |
| BEN-032 | A filename-substring filter over a set defined by its DIRECTORIES silently under-protects, and reports the shortfall as success. | — | EP-2026-08-06-niter3-budget |
| BEN-033 | Read an ensemble's size from the PRODUCT, never from the launcher that built it — a launcher's globs say what it *would* consume, the product records what it *did*. | — | EP-2026-08-06-niter3-budget |
| BEN-034 | `ControlPersist` masks NERSC certificate expiry, so cluster access dies silently mid-session hours after the credential lapsed — and the only outbound comms path dies with it. | — | EP-2026-08-06-niter3-budget |
| BEN-035 | `rc=$?` after a pipeline reports the LAST stage's status, so a diagnostic that pipes its command through `tail`/`grep` cannot detect that command failing. | — | EP-2026-08-06-niter3-budget |
| BEN-036 | A gate stated as missing *coverage* was actually a *footing* mismatch, and the expensive campaign its wording implied was already finished. | CLM-006 | EP-2026-08-07-five-band-laterals |
| BEN-039 | A stored INPUT named like a MEASUREMENT produced a false exoneration on the campaign's headline product. | — | EP-2026-08-07-nominal-normalization |
| BEN-040 | A fixture shaped like the consumer instead of like the producer makes a fail-closed gate untestable, and it fails 100% of the time on real input while the test stays green. | CLM-006 | EP-2026-08-07-five-band-laterals |
| BEN-041 | A provenance chain with no FIELD for a property cannot be read as asserting that property is fine — and the sibling lane's gate had trained me to expect one. | CLM-006 | EP-2026-08-07-gbdt-closeout |
| BEN-019 | Repeated-measures grading (8 cards; gemini ×30 passes = 240 scores, opus ×4–6 passes): both graders are HIGHLY repeatable (within-card SD gemini 0.24 over 30 passes, opus 0.27; re-grade vs day-before mean\|Δ\|≤ 0.85 with +0.4 mild drift) — s… | — | EP-2026-07-10-lead-vetting |
| BEN-026 | Diagnostic output must never be piped through `tail`/`head`. | — | EP-2026-08-05-gate4-reissue |
| BEN-027 | Identifiers and counts are read from the system, never recalled or eyeballed. | — | EP-2026-08-05-gate4-reissue |
| BEN-028 | A quiet log does not mean a dead job: on this Lustre filesystem Python block-buffers redirected stdout at 4 MiB. | — | EP-2026-08-05-gate4-reissue |
| BEN-030 | A multi-seed scan split across jobs is CHECKPOINTING, not housekeeping — do not consolidate it. | — | EP-2026-08-06-niter3-budget |
| BEN-037 | The handoff a fresh session is routed to said a hypothesis was untested; the canonical open-items doc had already measured it false — and the handoff is the file the session actually reads. | CLM-010 (i) | EP-2026-08-07-d2-underfitting |
| BEN-038 | An L1 criterion turns per-cell VARIANCE into what reads as bias, and a predeclared rule phrased on the aggregate will confirm the wrong cause. | CLM-010 (i) | EP-2026-08-07-d2-underfitting |
| BEN-042 | A decomposition's "scatter penalty" is not what removing the bias would cost, and quoting it against the criterion's headroom inverts the answer twice. | CLM-010 (i) | EP-2026-08-07-d2-underfitting |
| BEN-043 | A `save_best_only` checkpoint plus an `EarlyStopping` that cannot fire means the model you reweight with is never the model you save — and the weights that produced the published artifact may not exist on disk at all. | CLM-010 (i) | EP-2026-08-07-nominal-normalization |
| BEN-044 | An absolute tolerance inherited into a problem whose natural scale is ~1e-80 makes a gate that cannot fail — and a covariance gate is where it hides best. | — | EP-2026-08-07-cstat-100rep-review |
| BEN-045 | A published weighted mean is meaningless to compare against until you know its WEIGHTING — and the same product can ship two. | CLM-012 | EP-2026-08-07-d2-acceptance-oracle |
| BEN-046 | A runbook can describe a gate as a checkpoint to pass when it is actually an open BLOCK with enumerated, never-repaired defects — and the state table it ships with will not say so. | CLM-006 | EP-2026-08-07-gbdt-closeout |
| BEN-060 | A prediction that fails for a reason unrelated to its hypothesis is the shape that gets misread as confirmation — and I produced one, then defended it with a statistic I had eyeballed. | CLM-006 | EP-2026-08-07-gbdt-closeout |
| BEN-070 | A guard written in different units from its neighbours is the signature of this whole family — and one such guard was 55 orders of magnitude too loose to ever fire. | — | EP-2026-08-07-cannot-fail-sweep |
| BEN-071 | Read a validator's checks against each other before reading any of them against the physics — and mechanise it, because the inconsistency is far easier to see than either check's correctness. | CLM-012 | EP-2026-08-08-validator-units |
| BEN-072 | A gate that reproduces a computation must match that computation's CONFIGURATION; any parameter it defaults differently is a floor on its own resolution — and mine was mis-specified against a number it had itself measured. | — | EP-2026-08-08-rerun-gate-ab |
| BEN-073 | When a document moves, the brief that cites it does not move with it — and the stale citation fails silently, because a log that ends two days ago looks like a log, not like an error. | — | EP-2026-08-08-standdown, EP-2026-08-09-artifact-backup |
| BEN-074 | `git stash` is SHARED MUTABLE STATE across concurrent agents in one checkout -- never use it for a reproduce-on-a-clean-tree check. Use a throwaway WIP commit or a detached worktree. | -- | EP-2026-08-09-clm012-bugfix |
| BEN-075 | A launcher must not turn a documented multi-environment pipeline into one process by selecting `--stage all`. | — | EP-2026-08-09-diagnostic-extraction, EP-2026-08-09-diagnostic-extract |
| BEN-076 | BEN-028 inverted: a quiet log does not prove a job is DEAD, and it does not prove a SUBMITTER is ALIVE either. For anything whose job is to create a job, the liveness probe is 'did a Slurm record appear', not 'is the log growing'. | -- | EP-2026-08-09-step1-trajectory |
| BEN-077 | Check that ACHIEVED and REQUIRED are the same quantity — four criteria in four days compared a correct number against a requirement belonging to a different number, and none was an arithmetic error. | CLM-012 | EP-2026-08-10-annealed-shape |
| BEN-078 | Verify a claim about REPO STATE before converting it into a directive — especially a directive that modifies a frozen artifact. Recorded by Joseph as HIS failure, at his instruction. | -- | EP-2026-08-10-annealed-shape |
| BEN-061 | Editing another lane's file to fix MY collection problem silently voided a gate hash binding — and the right fix was available in a file I already owned. | — | EP-2026-08-07-gbdt-closeout |
| BEN-062 | A rule stated one notch too broadly gets ignored after its third false alarm — and the sharp version of trap #8 also explains the OPEN item that the blunt version had been walking past for a week. | — | EP-2026-08-07-gbdt-closeout |
| BEN-063 | A defect filed against one file is a hypothesis about the codebase, and nobody tested it for eight days: J36 is not one site, it is eight. | — | EP-2026-08-07-gbdt-closeout |
| BEN-064 | A `max`-shaped guard lets its worst bin choose the headline, and five numerically irrelevant bins hid a 62% failure. | — | EP-2026-08-07-gbdt-closeout |
| BEN-065 | A spread in a per-component SCALE produces shape error only in proportion to how much the components differ in SHAPE — asserting the first and skipping that step is how a 38.90% number came to look like a threat to a 1–2% claim. | — | EP-2026-08-07-gbdt-closeout |
| BEN-066 | A test fixture that references anything the repository moves has a SHELF LIFE, and its decay is silent: it keeps failing, for the wrong reason, having stopped isolating the defect it was written for. | -- | EP-2026-08-07-gbdt-closeout |
| BEN-067 | The notification channel contains a gate that cannot fire: `notify()` is silent on a reused id, and it is silent ASYMMETRICALLY — a transport failure is ledgered, a duplicate key is not. | -- | EP-2026-08-07-gbdt-closeout |
| BEN-068 | "A decision read before the thing that determines it has finished happening" is a DEFAULT, not a slip — two lanes produced it independently, in different files, on the same night. | -- | EP-2026-08-07-gbdt-closeout |
| BEN-069 | A timestamp is not a measurement unless the command that produced it was pinned to a timezone — two lanes made this error independently on the same day, and both were caught by luck rather than by process. | -- | EP-2026-08-07-gbdt-closeout |
| BEN-190 | **I edited the config directory this session does not read, then reported the setting applied.** A settings edit has two correctness conditions — contents, and read-path membership — and I tested one. [full](FINDINGS-ARCHIVE-2026-08.md) | — | EP-2026-08-12-closeout |
| BEN-191 | **We fixed the staleness detector and `LIVE-STATE.md` is still always stale.** The file conflates a generated view with authored prose; `--check-freshness` can only test the first. Split it. [full](FINDINGS-ARCHIVE-2026-08.md) | — | EP-2026-08-12-closeout |
| BEN-192 | **Three status sources disagree about the same sessions at the same instant, and the two calling themselves *status* disagree most.** Only transcript mtime is an artifact. Recurred: `squeue` vs `sacct` on one array. [full](FINDINGS-ARCHIVE-2026-08.md) | — | EP-2026-08-12-closeout |
| BEN-193 | **Coverage is invisible by construction — a set you cannot see does not announce that you cannot see it.** Eight instances, four parties, all in enumerations; the eighth authorised an irreversible act on 0.87% coverage. [full](FINDINGS-ARCHIVE-2026-08.md) | — | EP-2026-08-12-closeout |
| BEN-194 | **A path-verification refusal reads as a permissions problem.** *"Too complex to verify it stays inside the worktree"* means the guard cannot PROVE containment, not that the lane lacks rights — opposite remedies. [full](FINDINGS-ARCHIVE-2026-08.md) | — | EP-2026-08-12-closeout |
| BEN-195 | **A deferred item whose payload was never written looks exactly like a trigger nobody fired.** `OI-47`'s respawn DID fire and wrote the default, because the value existed in no settings file. Check the payload exists. [full](FINDINGS-ARCHIVE-2026-08.md) | — | EP-2026-08-12-closeout |
| BEN-196 | **A denominator printed to prevent a vacuous negative was computed by the same broken parser, so it certified the emptiness it guarded.** A check's denominator must come from a different instrument than its numerator. [full](FINDINGS-ARCHIVE-2026-08.md) | — | EP-2026-08-12-closeout |
| BEN-197 | **An expired NERSC sshproxy certificate partitions every session from the cluster while all other signals look normal.** Dead 11h49m; `ssh -v` names it in one line. Certs last 24 h — check validity first. [full](FINDINGS-ARCHIVE-2026-08.md) | — | EP-2026-08-12-closeout |
| BEN-198 | **Two of my own counts of one set disagreed; I quoted one without reconciling, and a peer built a false finding on the other.** A `cat` artifact fabricated a path. **A bigger denominator is not a better one.** [full](FINDINGS-ARCHIVE-2026-08.md) | — | EP-2026-08-12-closeout |
| BEN-199 | **A freshness rule with no passing state, cited in CODE for hours with no `FINDINGS.md` row.** `Git:` was required to equal `HEAD`, which is impossible by construction. A citation is not a registration. [full](FINDINGS-ARCHIVE-2026-08.md) | — | EP-2026-08-12-closeout |

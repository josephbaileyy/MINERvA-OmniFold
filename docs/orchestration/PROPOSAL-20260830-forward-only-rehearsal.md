# PROPOSAL 2026-08-30 — a new forward-only k=0 rehearsal

## Status, authority boundary, and decision requested

This document proposes one new k=0 rehearsal. It does not deploy a tree, run either M(ii) leg,
write a scheduler, file Gate-2 evidence, change a gate, or adopt a product. It asks for a separate
decision on the staged sequence below.

The current authority boundary is quoted rather than summarized. Ruling 12 of
`DECISION-20260822-joseph-b1-lift-and-clause-c.md` says:

> "The scientific target is option (a), the M(ii) member scan—not stamped re-adoption of the archive
> products. Marker backfill remains unauthorized. This selects the target but does not authorize the
> 151 A100-hour family, C_ML production, or a full member scan."

The repair decision says:

> "It does **not** authorize a far-end run, a new rehearsal, scientific compute, scheduler mutation,
> covariance construction or adoption, a Gate-2 status change, or a publication claim."

The latest independent full-chain grade says exactly:

> `F17B-REPAIRED-CHAIN: NOT FIT`

and:

> "Had I returned FIT, that list would read identically except that a proposal for a new
> forward-only rehearsal would have become writable."

This proposal being writable does not convert that grade into FIT. Before any rehearsal submission,
all of the following must be true:

1. a separate decision approves this proposal and names its deployment-only and rehearsal phases;
2. the new deployment described below exists at the exact pin and its own A-2(a)–(g) declaration is
   filed;
3. a fresh independent reviewer grades the whole prospective F-17(b) chain at that deployed pin and
   records **FIT**; the reviewer is neither the repair implementer nor either prior grader;
4. the separate readiness check required by decision §10.1 confirms the prospective F-7(b), F-8(b),
   and F-17(b) mechanisms at the exact rehearsal tip; and
5. a fresh eligible non-builder records Gate 1 **PASS** clause by clause at that tip.

The operative §10.1 prohibition is:

> "**Do not start a rehearsal, file Gate-2 evidence, or launch compute without a separate readiness
> check confirming that ALL prospective F-7(b), F-8(b) and F-17(b) mechanisms are present AND
> independently graded.**"

The proposal therefore has a deployment-and-grade phase before its scheduler phase. A deployment
decision is not a submission decision. Any non-FIT full-chain grade, non-PASS readiness result, or
non-PASS Gate-1 verdict stops the sequence before `sbatch`.

## 1. Deployment at the repaired pin

### Exact pin and why it removes N1

Deploy exact commit:

`32e403b84e9e8f9d9bc435028749f896653c7a43`

This is canonical `main` as observed for this proposal. It carries the approved repaired measurer
and comparator with these content identities, measured from the git objects rather than from a
working copy:

| artifact | sha256 | bytes |
|---|---:|---:|
| `docs/orchestration/measure_m1_m6.py` | `ce52ff773c5261ed54cfc63150ef740785d5ed5aa81c9ae271d935f0efc3ed51` | 14108 |
| `docs/orchestration/compare_m1_m6.py` | `28490539b60c4a790f77b5dd1070dc7e9d192efabebee640662d9496cf465242` | 67440 |
| `docs/orchestration/measure_k0_farend_f1b_f17b.sh` | `ad1a8b6405e55094afbaa9cab00b0a2b7afb0fa52835653d147dad6e92b84775` | 16358 |
| `docs/orchestration/m1m6_expected_differences.json` | `13547f3f21333ea0545b232e7ca28847401cd4318fbf13e4e75c5276765efc2c` | 11302 |

The first two identities are the repaired schema pair: the measurer emits
`measurement_wall_clock` and `branch_or_detached`, and the comparator requires them. At the present
deployment, `measure_k0_farend_f1b_f17b.sh` takes `MEASURER` from its hardcoded `CODE_ROOT`, whose
old `aa67c426` measurer predates those keys. Deploying `32e403b8` at that same code root means the
hardcoded path resolves to the repaired measurer. Both tree documents are then produced by the same
schema revision the comparator consumes. That removes N1 without an override, without weakening the
schema, and without editing any of the three pin-bound paths.

The historical run-specific shell remains unchanged and is not repurposed as the new run driver:
its old sha, run directory, and seven job ids identify the old rehearsal. A separately implemented,
new-dated run driver must bind the new sha, declaration, run directory, seven job ids, and durable
record paths while retaining `MEASURER="$CODE_ROOT/docs/orchestration/measure_m1_m6.py"`. That is how
the new deployment dissolves N1: the unchanged wiring now resolves the repaired measurer. The new
driver is a new prospective-chain surface, not an edit or supersession of the historical script, and
the fresh independent full-chain grade required above includes it before use.

### Preserve `aa67c426` before the deployment moves

The old deployment evidence already has a tested recovery source:
`state/RECEIPT-20260826-k0-freeze-bundle-detectability.json` records bundle
`k0-clean-aa67c426-20260826T075536Z.bundle`, 79140251 bytes, sha256
`8ce5839114f4ba6b9b6d231ae343988134cc752b172e5f1b521a9869555022c0`, containing
`refs/tags/freeze/k0-aa67c426`. Recovery from that bundle alone was tested through clone, `fsck`,
detached checkout, and a zero-line porcelain result.

Before any permission or checkout change, the deployment producer must:

1. re-run the receipt's exact reverification recipe, including the bundle sha256, `list-heads`
   inclusion of `refs/tags/freeze/k0-aa67c426`, exact old HEAD/ref set/modes, and tested recovery in
   fresh scratch;
2. file that remeasurement as a new dated receipt; a mismatch is a stop condition, not a repair;
3. leave the existing bundle, receipt, local freeze tag, declaration
   `declarations/aa67c426/source-manifest.json`, and old run directory unchanged; and
4. never repoint `refs/tags/freeze/k0-aa67c426`. It identifies the bytes it originally named.

This preserves the already-tested recovery route before the deployed working tree moves. It does
not pretend the bundle is a byte-image of the old clone; the receipt's own limitation remains that it
recovers the pinned commit and ref set.

### Make writable, deploy, and re-freeze

The current source modes are `dr-xr-x---` for directories and `-r--r-----` for regular source files.
The old ruling deliberately left `.git` at `drwxrwx---`; decision §11.1.1 says:

> "Ruling: do not `chmod` `.git` read-only, and revert it if it was applied."

After the preservation precondition passes, the deployment producer performs this bounded sequence:

1. add owner write permission to the working tree only, pruning `.git` from the recursive mode
   change;
2. fetch the already named object if it is absent, verify its full sha, and checkout
   `32e403b84e9e8f9d9bc435028749f896653c7a43` detached—never a branch name;
3. require zero porcelain lines; verify the guard's checkout constitution, absence of nested and
   enclosing checkouts, and the committed identity of every executable copy;
4. create the new declaration under `declarations/32e403b8/`, recording every tracked `*.py` and
   `*.sh`, the full listing digest, file count, declaration-file sha256, and exact deployment pin;
5. remove write permission from the working tree while again pruning `.git`; verify source
   directories and regular files return to `dr-xr-x---` and `-r--r-----`, and verify `.git` remains
   `drwxrwx---`; and
6. run and file every A-2(a)–(g) check against the new declaration, with mismatch controls where the
   contract requires them.

No in-place edit, copied file, `PYTHONPATH` substitution, `MNV_MEASURER` override, or schema
exception is part of this deployment.

## 2. A new freeze, scoped to the new pin and its own F-1(b)

The expired `aa67c426` freeze is not reused. Approval must instantiate this new dated rule:

> **The deployed tree `/pscratch/sd/j/josephrb/k0r2/clean` stays detached at
> `32e403b84e9e8f9d9bc435028749f896653c7a43` from the filed near-end A-2(a)–(g) declaration until
> F-1(b)'s far-end A-2(a)–(g) measurement for the new rehearsal is producer-filed. No checkout,
> reset, fetch-and-merge, re-declaration, or branch repoint may occur in that directory during this
> interval. It expires when that rehearsal's F-1(b) producer filing is committed—not when its jobs
> merely look terminal.**

Record the new deployment pin on a new local freeze ref whose name includes `32e403b8` and include it
explicitly in a new recovery bundle. Assert the ref is present in `git bundle list-heads`, test
recovery, and commit the receipt before submission. The old `freeze/k0-aa67c426` ref remains
historical and unmoved.

The new rule is preventive prose plus A-2(a) detection, not a mechanical guarantee. Terminality is
measured with complete per-task scheduler accounting for all seven arms, including dependency reason
codes; an empty queue is not the expiry condition.

## 3. F-17(b) with real near-end and far-end operands

Mint `<RUN_ID>` and its run directory before Gate 1 is measured. The **pre-submission operand** is
not a later reconstruction: it is the exact pair of producer-emitted JSON documents

- `docs/orchestration/state/f17a-<RUN_ID>-deploy.json`, measuring the frozen deployment at
  `32e403b8`; and
- `docs/orchestration/state/f17a-<RUN_ID>-canonical.json`, measuring the canonical cluster checkout
  as it actually stands immediately before submission.

The producer creates each with the pinned `measure_m1_m6.py --json`, records its sha256/bytes and
measurement wall-clock, and commits both files before the first `sbatch`. Exact copies also land at
`<RUN>/measurements/pre/deploy.json` and `<RUN>/measurements/pre/canonical.json`; the committed files,
not the run-directory copies, are the durable pre-submission operand.

The producer then runs the pinned `compare_m1_m6.py` over those two documents with the declared
expected-difference file and commits
`docs/orchestration/state/f17a-<RUN_ID>-tree-comparison.json`. Exit 0, 10, or 20 is a completed
comparison with its findings retained; any refusal exit stops before submission. Tool digests are
tightly bracketed around their own invocations.

After all seven arms are proved terminal, repeat the same process from both trees into:

- `docs/orchestration/state/f17b-<RUN_ID>-deploy.json`;
- `docs/orchestration/state/f17b-<RUN_ID>-canonical.json`; and
- `docs/orchestration/state/f17b-<RUN_ID>-tree-comparison.json`.

Use the same comparator for three additional records: deploy pre versus deploy post, canonical pre
versus canonical post, and all four documents together. No pair is compared by eye and no markdown
table substitutes for JSON.

M-2 is retested explicitly. Each near/far and time comparison must quote the comparator record's
dedicated `m2_perishable.status`, fields, and finding count separately from the general finding
summary. A missing dedicated M-2 result, an input-schema gap, or any comparator refusal is F-17(b)
not discharged. Findings are filed as findings; they are not converted to expected differences
after observation.

## 4. Producer filings and independent grading

One named rehearsal producer owns the deployment, submission, run-bound evidence, and the filings
below. That producer files; it does not grade. A fresh non-builder grades each filed clause from the
producer's exact operands. The old Gate-2 grader at `a3000487` is ineligible to grade the new
F-2(b), F-3(b), or F-5(b) producer filings because it measured those propositions itself in the old
rehearsal.

| filing | producer files | covering evidence |
|---|---|---|
| **F-2(b)** | `PRODUCER-FILING-<date>-<RUN_ID>-f2b.md` | Every inventory record, not a sample; the exact inventory population and scheduler job/task population; `mnv_import_set_ratchet.py --source-manifest <new declaration>` output; every executing-file `--pair` result CURRENT; non-vacuous record and `checked` counts. |
| **F-3(b)** | `PRODUCER-FILING-<date>-<RUN_ID>-f3b.md` | The contract's complete job-stdout search and full command/output, plus the stronger covering check over every inventory's parsed `allow=[]` and `allow_is_empty=true`; a positive control showing the search population is non-empty. |
| **F-5(b)** | `PRODUCER-FILING-<date>-<RUN_ID>-f5b.md` | Every real inventory checked against the new source manifest: every script and repository origin under the new code root, every sha256 equal to the manifest, no absent path, `checked > 0` for every guarded process, and the full distributions rather than minima alone. |

Each filing records its producer identity, rehearsal id, deployment pin, seven job ids, input path
population, commands, raw output route, artifact digests, measured result, and limits. The grader
recomputes from those operands and files a separate clause-by-clause verdict. Verification evidence
does not substitute for the producer filing.

## 5. F-7(b) and F-8(b)

### F-7(b): commit the rehearsal pin and put it on a ref

After the terminal inventory population is complete, the producer runs
`mnv_import_set_ratchet.py --write-pins` over exactly that run, with the new source manifest and the
preflight-exclusion digest. Commit the resulting per-entrypoint import-set file with the producer
filings. The filing must say, in the contract's terms, that the pin is **recorded and untested**: this
rehearsal establishes it and cannot be its first test.

Create and push a new annotated evidence ref
`refs/tags/evidence/k0-forward-rehearsal-<RUN_ID>` pointing to the commit that contains the import-set
pin, F-17 records, producer filings, and run receipt. The tag message records those artifact digests
and the deployment sha. A working-tree file without the ref does not satisfy this proposal's F-7(b).

### F-8(b): a receipt whose blind spots are its own prose

The producer authors `RECEIPT-<date>-<RUN_ID>-forward-rehearsal.md` after the far end. It binds the
deployment declaration, near/far F-17 operands, job/task accounting, inventories, log corpus,
import-set pin, producer filings, terminal conditions, aborts, outputs, and every digest used by the
grade.

Its blind-spots section explains in the receipt's own words, with run-specific consequences, at
least the four currently required concepts: namespace packages with absent/no origin; modules
already present in `sys.modules` before the guard; further subprocess or child-interpreter routes;
and shell (`.sh`/B-5) routes. It also states any blind spot observed during this run.

Run `verify_run_receipt_blind_spots.py` and retain its report. Its best outcome is exactly
`10 REVIEW_REQUIRED`, not a pass. A different independent reviewer writes a digest-bound prose
attestation with a distinct finding for every blind spot. `verify_f8b_attestation.py` may return
`11 ATTESTATION_WELL_FORMED`; that is still not a discharge. The design's exact rule is:

> "**THE GATE IS A RECORDED AUTHORITY DECISION, NOT A PROGRAM.** No exit code discharges F-8(b)."

The Gate-2 authority records the F-8(b) decision only after reading that attestation.

## 6. The seven arms and their decision budgets

These are the seven rehearsal submissions of logical legs 1–5. Leg 6/finalization is outside this
proposal and remains separately gated.

The estimate column reproduces the plan's accounting convention: GPU-partition work is counted in
A100-hours and CPU-partition work in CPU task-hours; auxiliary CPU cores on a GPU allocation are not
double-counted as a second budget. The decision ceilings are deliberately above the recorded
estimates and every arm is strictly below both delegated thresholds.

| arm | launcher / population | measured or bounded estimate | GPU-hour ceiling | CPU-hour ceiling |
|---|---|---:|---:|---:|
| 1 bootstrap | `sbatch_bootstrap_5d_gpu.sh`, `1-100` | 14.00 A100-h | **20** | **0** |
| 2 seed split | `sbatch_seedscan_split_5d.sh`, `1-24` | 3.72 CPU-h | **0** | **5** |
| 3 detector | `sbatch_unfold_5d_detector_bkgaware_gpu.sh`, `0-18` | 14.23 A100-h (conservative prior from the older 24-task population) | **20** | **0** |
| 4 sweep | `sbatch_sweep_bank_5d_run_bkgaware_gpu.sh`, `1-169` | 23.84 A100-h | **30** | **0** |
| 5 uthrow run | `sbatch_uthrow_run_5d_fast.sh`, `0-39` | 21.38 CPU-h | **0** | **30** |
| 6 uthrow block | `sbatch_uthrow_block_5d.sh`, `0-20` | 22.02 CPU-h | **0** | **30** |
| 7 uthrow combine | `sbatch_uthrow_combine_5d_fast.sh`, single, dependent on arms 5 and 6 | unmeasured; scheduler-request ceiling 3 CPU-h | **0** | **5** |
| **sum of decision ceilings** | seven arms | — | **70** | **70** |

The delegated authority may decide PASS/BLOCK and these per-arm ceilings because each arm is
strictly under 500 GPU-hours and strictly under 500 CPU-hours. Any requested increase reaching 500
or more in either column, any extra arm, any retry not already bounded by a separately approved
retry rule, and leg 6 go to Joseph before submission.

The dependency order is bootstrap and seed split before consumers; detector, sweep, uthrow run and
uthrow block only when their prerequisites exist; combine uses conjunctive `afterok` on both uthrow
arrays. Exact success populations are taken from the launchers at the approved sha and filed before
Gate 1; a later launcher change requires a new estimate and gate evidence.

## 7. Terminal conditions, aborts, and the authorization ceiling

Terminal success requires all seven job/task populations complete with `COMPLETED 0:0`, all expected
outputs and `.done` markers bound to this run and pin, one non-empty guard inventory per guarded
process, no cross-run inventory, A-2(a)–(g) identical at the far end, completed F-17 comparisons,
producer-filed F-2(b)/F-3(b)/F-5(b), an F-7(b) evidence ref, the F-8(b) receipt and attestation path,
and an eligible clause-by-clause Gate-2 grade. Any failed, cancelled, timed-out, node-failed, short,
duplicate, mixed-pin, missing-inventory, manifest-mismatch, comparator-refusal, or write-protection
condition aborts. No marker is backfilled and no expected population is relaxed.

The contract states the product boundary exactly:

> "**Until Gate 2 passes, the rehearsal's products stay where they land: not adopted, not consumed by
> anything outside the seven rehearsal jobs, not quoted, and no further member is authorized.**"

A terminal success, including Gate-2 PASS, cannot authorize anything beyond the single k=0
rehearsal. The plan's own list is retained verbatim:

> - **Not the remaining 49 members**, and not the family's cost (§6 shows why that is a separate call).
> - **Not `C_ML` production**, which ruling 12 excludes by name.
> - **Not the 151 A100-hour family**, which ruling 12 also excludes by name — and see §6.
> - **Not marker backfill**, and not the undeclared re-adoption route. Still unauthorized.
> - **Not deletion of the 41.44 GB intermediate.** `MVFINAL_j` has no implementation.
> - **Not removal of the launcher's pause branch** — ruling 13 defers that until a member is runnable,
>   and one member being runnable is not the same as the branch being safe to delete.
> - **Nothing about members k≠0.** k=0 is the anchor and the only member with an archive comparand; a
>   pass there says nothing about a member whose products cannot be compared to anything.

It also cannot authorize leg 6, a covariance construction or adoption, a publication claim, or a
Gate-2 result for the failed `aa67c426` rehearsal. Those remain separate decisions.

## 8. Cost question: physics legs or paperwork only?

**Measured record:** nobody previously filed a decision answering this question. The governing
contract nevertheless requires run-bound objects: F-2(b) and F-5(b) read every emitted inventory;
F-7(b) records import sets *from the rehearsal*; F-17 takes JSON from both trees before submission
and again *after the path runs*; and Gate 1 says its PASS unlocks exactly the seven rehearsal jobs.

**Inference from those requirements:** this cannot be a producer-filings-only exercise. A new pin
plus old inventories would be a mixed-revision record, and paperwork written around the old seven
jobs would be backfill rather than a new forward-only rehearsal. The seven physics submissions must
therefore run again to create the new run-bound operands. The three missing producer filings are
written from that new run; they do not replace it.

**Cost estimate:** the seven-arm subset is approximately **52.07 A100-h** plus **47.12 measured
CPU-h**, with the combine arm unmeasured but bounded by a 3 CPU-h scheduler request. The older
plan's approximately **53.6 A100-h** full-member figure includes the separately gated finalizer
ceiling of 1.5 A100-h; it is a conservative envelope, not the exact cost of the seven arms proposed
here. This proposal's decision envelopes are 70 GPU-h and 70 CPU-h in total, with no individual arm
at or above 500 in either resource.

If the decision authority rejects the inference and intends a paperwork-only object, this proposal
must not be partially executed: Joseph must first rule how an old-run inventory can satisfy the new
pin, near/far F-17, and F-7-from-the-rehearsal clauses without backfill. No such route is present in
the record reviewed for this proposal.

## 9. Requested decision

Approve or reject the sequence as a unit:

1. reverify and preserve the `aa67c426` recovery evidence;
2. deploy and re-freeze exact `32e403b8` under a new dated pin;
3. obtain a fresh independent full-chain FIT and the required readiness and Gate-1 decisions;
4. if and only if all three pass, submit the seven bounded arms;
5. file the machine-readable near/far F-17 chain, the three producer filings, F-7 ref, F-8 receipt,
   and an independent Gate-2 grade; and
6. stop at the single-rehearsal authorization ceiling regardless of terminal outcome.

Approval changes no present gate and authorizes no action not named in its recorded decision.

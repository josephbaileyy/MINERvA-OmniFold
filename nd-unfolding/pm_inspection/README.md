# `pm_inspection` — the executable packaging of a predeclared read-only inspection

**STATUS: FOR REVIEW. NOT SUBMITTED, NOT APPROVED, NOT EXECUTED.** Nothing here has been run
against the real inputs. Admission is blocked on prerequisites recorded below.

These files package the fixed reads already declared in
`docs/orchestration/PREDECLARATION-20260906-pm-root-inspection.md` §3–§4. They add no
scientific scope: every path opened and every object read was declared before this code
existed.

| file | role |
|---|---|
| `INPUT-BINDINGS-20260908.json` | the thirteen inputs, with digests and their provenance |
| `pm_root_inspect.py` | producer — opens each input `READ`, performs the declared reads |
| `pm_root_validate.py` | terminal validator — classifies capture, selects one branch |
| `fake_root.py` | test support: the slice of the PyROOT surface the producer touches |
| `test_pm_root_inspection.py` | classification and predeclaration-conformance tests |
| `test_pm_producer_driven.py` | the REAL producer against a controllable temporary tree |
| `test_pm_validator_output.py` | the validator's `main`, end to end, including its write path |

161 tests at the fifth repair round, none of them needing ROOT or any real input.

The contract lives at `docs/orchestration/contracts/CONTRACT-20260908-pm-root-inspection.json`.

## What COMPLETE means, and the three things it does not mean

`COMPLETE` means **the declared measurements were captured**. It is not a scientific grade,
it does not discharge PM-1, PM-3, PM-4 or PM-5, and it does not make anything citable for a
gate movement. The validator has no acceptance threshold because none was authorized, and
inventing one here would be inventing a scientific criterion.

## The distinction the validator exists to keep

**An expected absence is a measurement. A missing required input is a fault.**
`hRowIndex5D` absent from G is the *answer* to a declared question — G's committed inventory
is 13 keys and contains neither `hRowIndex5D` nor `hXSecND_flat` — so absence is `COMPLETE`.
A required input that is missing, wrong-sized or digest-mismatched is `ERROR`. Collapsing
those two would turn a real measurement into a fault, or a fault into a measurement.

## The PM-4 provenance gap is preserved, not closed

Digests for the central CV and the ten endpoints were measured **2026-09-08 by ordinary
read-only access**. They bind the bytes those files hold **now**. They are **not** evidence
that these bytes were G's historical production input: G's own hash receipt does not bind the
central CV. Every digest this producer computes is labelled
`reconstructed_through_producer_input_route` and never `read_from_G`.

CS's digest is the **historical** `support_family_sha256` from
`nd-unfolding/active_universe_5d/standard/candidate/std_component_manifest.json`. **CS is not
re-hashed** — it is 41.4 GB; size is checked and bytes are not. That limitation is stated,
carried in the bindings, and asserted by a test.

## Runtime output never lands inside a checkout

`--out` must be **absolute** and outside every git working tree; the producer refuses
otherwise, and two tests hold it to that. `docs/orchestration/state/pm-root-inspection-20260908/`
is the **later, deliberate, committed evidence destination** — not the runtime directory.

## Environment yes, analysis code no

The deployed tree at `/pscratch/sd/j/josephrb/MINERvA-OmniFold` supplies the **installed and
built environment** only (`setup_salloc_env.sh`; its conda prefix and build setups are not in
any fresh clone). No analysis code is imported from it. That is measured rather than asserted:
`module_provenance()` records every loaded module's file and lists any resolving under that
root, so an accidental import shows up in the report instead of passing silently.

That tree is 235 commits behind `main` and carries dirty paths, so it **cannot be pinned by
commit**. Input identity is therefore by digest, never by commit reference.

## Known prerequisites, none of them resolved here

1. **TTY approval.** `campaignctl.py:3540-3541` refuses approval without an interactive
   terminal, and requires the staged proposal digest pasted back. No agent session can supply
   this. It is a human act, by design.
2. **The admission ref cannot be written from any available host** under campaignctl's
   sanitised environment. Perlmutter has no HTTPS credential; the Mac has two and can show
   neither to the tool, because both live in scopes campaignctl disables.
3. **Attendance.** Attended means the executing session stays present through completion and
   cleanup. An initial approval alone is not attendance.
4. **PyROOT on a compute node is unmeasured.** It works on a login node under this
   environment; the compute-node case is a declared unknown and must fail as `ERROR`, not hang.

## Repairs made after review BLOCK on `a2214f0e`

Independent review found eight real defects. Every one is now pinned by a test that fails if
it returns.

| defect in `a2214f0e` | repair |
|---|---|
| validator returned `COMPLETE` for an empty capture | empty capture is `ERROR` |
| unknown `status` passed silently | any status outside `{read, absent, unreadable}` is a fault |
| an *unreadable* optional counted as the declared absence | unreadable optional is a fault; only `absent` is the measurement |
| validator took `declared_read_ids` from the producer | obligations recomputed from the committed bindings; a shrunken declaration is `INCOMPLETE` and flagged |
| a stale report at the fixed path satisfied the read | producer and validator share `--attempt-id`; a mismatch is `ERROR`. **This repair is partial and the row overstated it — see "The fixed attempt id" below.** |
| mask digest invented (`!= 0`, JSON booleans) | the predeclared algorithm: `central > 0`, `sha256(idx.tobytes())` and `sha256(idx.tobytes() + b"\|C")`, compared to S's committed values |
| `row_index_sha256` and G's before/after digest absent | both captured; G read-onlyness is now measured, CS's stays asserted |
| declared `grid_nbins` reported as measured | `GetNbinsX()` recorded separately, with `nbins_conforms` |
| scalars read with `GetTitle` only | typed `GetVal()` for `TParameter<double>` such as `sqrt_tr_old`; null is a fault |
| `hRowIndex5D` present branch recorded only `GetEntries` | records row **contents** and their index digest |
| output guard fooled by `link -> repo/subdir` | both guards resolve the path before the ancestor walk; the validator now has the guard too |
| contract argv skipped the guard | both route through `nd-unfolding/mnv_guarded_run.py` |

## `--expect-root` is checkout-path-dependent, and that is a real constraint

`command_bindings(..., require_guard=True)` refuses unless the guarded argv's
`--expect-root` equals the repository root campaignctl is running from. The committed value
is `/pscratch/sd/j/josephrb/exec-20260907`, so **this contract is only stageable from a
checkout at exactly that path.** Verified two ways: the argv is refused when `--expect-root`
disagrees with the repo root, and it passes — binding all sixteen guard-shim files plus
`mnv_guarded_run.py` and the validator — when they agree.

That the guard exists is also what makes "environment yes, analysis code no" enforceable
rather than merely asserted: `mnv_guarded_run.py` refuses imports from another checkout
(OI-136), and `module_provenance()` records what actually loaded.

## Second review round — four more real holes, and how they were closed

| defect in `28a65747` | repair |
|---|---|
| a record's own `kind` was authoritative, so relabelling `input:G` as expected-optional and marking it absent returned COMPLETE | `obligation_kinds()` derives every id's kind from the committed bindings; a record whose kind contradicts them is itself a fault |
| `bindings_sha256: "wrong"` still returned COMPLETE | the validator hashes the bindings file it was handed and refuses a report produced against different bytes |
| `hInflation_g` listed but null still emitted `status=read, nbins=None` | a listed key that will not load is `unreadable` |
| the fixed attempt id could be reused over an existing report | the producer refuses to overwrite an existing report; a new attempt needs a new id and a new run directory |
| fixtures were hand-written status records | `test_pm_producer_driven.py` runs the **real producer** against a fake ROOT and a real temporary tree, then mutates that |

## Which interpreter runs the tests, exactly

**`/Users/josephbailey/miniconda3/bin/python3`, Python 3.12.2, numpy 1.26.4.** Recorded with
its probe output in `docs/orchestration/state/pm-inspection-test-evidence-20260908/`.

`/usr/bin/python3` on this machine is 3.9.6 and **cannot import numpy**, so four tests error
there rather than fail. That is not a defect in them: `mask_digests` is a numpy algorithm
because the predeclaration specifies it as one, and a skip guard would hide the very
comparison PM-4 depends on. Run them under an interpreter that has numpy — on Perlmutter that
is the `root_6_28` prefix, numpy 1.26.4, little-endian, which is what makes `idx.tobytes()`
reproducible on both machines.

## The fake ROOT is test support, not a ROOT substitute

`fake_root.py` implements only what the producer touches. Its point is that hand-written
records prove only that the validator classifies what the test author already believed —
running the real producer against a controllable tree proves the payloads being classified
are the ones the producer actually emits. It also makes `TParameter<double>` behave the way
the real class does, with the value in `GetVal()` and a decoy string in `GetTitle()`, so the
typed-read repair is tested rather than asserted.

## Third review round — a capture with no measurements in it

Review stripped every `reads` entry to `read_id`/`status`/`kind`, deleted the top-level `G`,
`CS`, `CV_central`, `endpoints` and `G_read_onlyness` sections, and the validator still said
`COMPLETE`. It had been checking that records **existed**, never that they **carried
anything**.

Two rules close it, and neither is an acceptance threshold — both ask whether the number is
*there*, never whether it is right:

- **`payload_fields_for()`** names what a `status="read"` record must carry, by what that read
  measures: `key_count` for a listing, `row_index_sha256`/`reported_mask_hash`/`count`/
  `measured_nbins`/`content_sha256` for a flat histogram, `nbins`/`first_edge`/`last_edge` for
  an axis, `sha256_before`/`sha256_after`/`unchanged` for G's read-onlyness, `value` for a
  scalar. A null in any of them is a fault. An `absent` optional carries nothing and is
  exempt, because there is nothing for it to carry.
- **`REQUIRED_REPORT_SECTIONS`** must all be present, so deleting the payload sections cannot
  leave a well-formed shell.

**Malformed shapes now produce a verdict, not a traceback.** A report that is not an object, a
`reads` array holding non-records, unreadable bindings, or any unexpected exception inside
`classify` all end as `ERROR` with a written verdict. An uncaught exception would leave the
terminal branch unselected — the one outcome the contract has no consequence for.

## Fourth review round — the same class again, and why the tests could not see it

Two independent reviewers returned BLOCK on `da8179f0`. The through-line both found is the
one this package has now failed four times: **the validator believing a record's summary of
a measurement over the measurement sitting next to it in the same record.** Round 1 took the
obligations from the producer's account; round 2 treated a self-declared `kind` as
authoritative; round 3 carried a `status` with the payload absent; round 4 found `status`,
`unchanged`, `present` and `nbins_conforms` still believed over the digests and counts beside
them.

| defect in `da8179f0` | repair |
|---|---|
| the presence rule tested for `None`, so every digest `""`, every count `0` and all seven sections `{}` returned `COMPLETE` | a payload field must be non-empty **and of the kind its read produces**; a section must be a non-empty mapping, or for `root_version` a non-empty string |
| `sha256_before`, `sha256_after` and `unchanged` were never compared, so a record saying **G changed** was `COMPLETE` | `unchanged` must equal `sha256_before == sha256_after`; either of the report's two statements of it saying G changed is a fault, and the two disagreeing is a fault |
| `G:hRowIndex5D`'s payload rule was `("present",)`, so an object that loaded and could not be digested was a measurement | `contents_readable` is a payload field, the digest is required when contents are readable, and the producer records the undigestible case as `unreadable` |
| the validator imported the producer's `obligation_kinds()`, so producer/validator skew was invisible | the table is restated in the validator; the tests hold both copies to a third restatement of the predeclaration, and a subprocess test fails if the import returns |
| `producer_declaration_disagrees_with_bindings` was computed and then excluded from `faults` | it is a fault |
| a listed-but-null `hXSecND_flat` or axis histogram aborted the capture with `AttributeError`, costing 21 of 38 reads | one bad object costs one `unreadable` record and the capture continues |
| `bindings["data_root"]` was committed and read by nobody, and `module_provenance`'s `forbidden_root` took the same argv value that chose the tree | the producer aims the contamination measurement at the **declared** root; the validator compares all three, and a populated offender list is a fault |
| the validator's write path sat outside every guard | classification and writing are separate; a write failure reports the classification it could not file and returns `ERROR` |
| the verdict was silently overwritten | `preserve-first`: a second classification needs a fresh run directory |
| an unreadable **optional** object was stamped `kind: required`, so an honest producer was additionally accused of reclassifying its own obligation | `status` carries the fault, `kind` carries the obligation |
| an empty `TNamed` title was reported as `status=read, value=""` | an empty title is `unreadable`; a typed `0.0` is still a measurement |

**The reason three rounds each found this class is the fixtures.** `payloaded()` built every
record by calling `validator.payload_fields_for()` — the rule under test — so fixture and rule
moved together and no test could detect a gap in either. Review measured the cost: sixteen
mutations applied one at a time, and **fifteen left all 44 tests green**, including hardcoding
read-onlyness, reporting the declared grid size as the measured one, and emptying seven of the
eight payload branches. The paragraph this replaced claimed that building fixtures through the
payload rule was the *repair*; it was the defect.

The obligation table, each obligation's kind, the payload branch each read falls in and the
payload values are now spelled out in `test_pm_root_inspection.py` from the predeclaration,
independently of both halves. There is one test per payload branch and one per required section
that fails when that single branch or section is dropped. All sixteen of review's mutations are
now caught, as are sixteen reverts of the repairs above.

**That claim was true and too narrow, and round 5 shows how.** The fixture stopped being built
by calling the payload rule, but its report SECTIONS stayed four hand-written stubs —
`{"key_count": 13}`, one endpoint out of ten, no TKey listing, no axis edges and no digest
anywhere in them. So the repair reached the records and stopped one layer short of the
sections, and a rule requiring a listing or an edge still could not fail against this suite.
See the next section.

## Fifth review round — the same class one layer up, and the repair is structural

Review returned BLOCK on `cd35c26e` with four reproduced classes, every one COMPLETE against a
report the REAL producer wrote. Round 3 required a payload; round 4 required it non-empty and
each section to be a non-empty mapping. `{"lost": true}` is a non-empty mapping.

**The asymmetry that kept the class alive for five rounds was structural, not local.** The
obligation side was a flat id-presence set — `set(obligations) - seen` at
`pm_root_validate.py:440-441` — while every content rule iterated `reads`. So PRESENCE
satisfied an obligation and CONTENT was only ever examined from the record side, and anything
an obligation required that no record happened to mention was invisible by construction.

`classify` is now **requirement-driven end to end**. It walks the obligations the committed
bindings impose, and for each one demands a record, that record's status, the record payload
that read produces, and the **nested capture** the read is declared to preserve. The record
side is used for exactly two things: a record nobody asked for, and a read recorded twice.

| defect in `cd35c26e` | repair |
|---|---|
| deleting `CS.key_listing`, deleting an axis's `edges`, or replacing `G`/`CS`/`CV_central`/`endpoints` with `{"lost": true}` each returned COMPLETE | every obligation carries the report path its product occupies. A listing must be TKey **names, classes and cycles** (PREDECLARATION §4) and as many of them as the record counted; an axis must carry the edges **including the final upper edge**, so nbins+1 of them; a digest mapping must restate the record's measurement and agree with it |
| `input:G` with a wrong `path`, `size_bytes: -7`, `sha256` of all zeros, or `digest_verified: false` was COMPLETE, and removing either digest field was too | each input is matched against **its own committed binding** and that binding's digest policy. **CS's no-rehash branch is preserved**: the bindings exclude it at 41.4 GB, so its record carries the historical digest as `sha256_bound_not_verified` with `digest_verified: false` and that is a complete capture — while a record *claiming* a verification the bindings exclude is a fault |
| a module loaded from the bound tree with an EMPTY offender summary was COMPLETE | the offenders are **recomputed** from `module_provenance.modules` against the bound root. The map is the measurement, the list is the producer's account of it, and the two must agree; a report with no map cannot be audited at all |
| a second `G:sqrt_tr_old` record with a different value was COMPLETE | read ids are unique. Two records for one declared read is two answers to one question, and nothing downstream says which one the verdict was reached on |

**The fixture was the reason the tests could not see any of this, and review named it exactly:
the synthetic positive fixture omitted the listings and the edges, so a rule requiring them
could not fail against it.** `report()` now builds all five nested sections from the records,
carrying a thirteen-entry TKey listing with names, classes and cycles (two entries share a name
and differ in cycle), the complete `nbins+1` edge list, the digest mappings, and every one of
the ten endpoints. Those literals are restated in the test file from PREDECLARATION §4 and §7 —
what each read produces, and that the listings and every computed digest are preserved outputs
— and `pm_root_validate` is never asked what they should contain. `section_path()` is restated
there too and a test compares it to the validator's table, which is the same
two-independent-statements cross-check the obligation table already had.

**Confirmed by reverting, not by assertion.** Seventeen reverts of the repairs above were
applied one at a time to a copy of the validator; every one fails at least one test, and each
fine-grained revert — TKey names, classes, cycles, the listing length, the edge count, the
record/section comparison, the conditional read's answer, the bound path, the bound size, the
bound digest, the verification policy, CS's exclusion, the offender recomputation, the module
map, the duplicate rule — fails exactly the test written for it.

**Still not crossed:** `nbins_conforms: false`, `all_finite: false`, `row_index_matches_S:
false`, `count_matches_S: false`, any scalar's value, and the expected optional absences are
each COMPLETE against the real producer, with a test holding each one there.

## What is a completeness check here, and what would be an acceptance threshold

The line the validator does not cross: **is the number there, and does it contradict another
number in the same record** is capture completeness. **Is the number right, big enough or close
enough** is an acceptance threshold, and there is deliberately none, because inventing one would
be inventing a scientific criterion nobody authorized.

So `unchanged` is compared to the two digests that define it, `nbins_conforms` to the two bin
counts that define it, and a count to the bins it was counted over — every one of them an exact
comparison of fields the producer already wrote. But a measured grid **non-conformance** is a
`COMPLETE` capture carrying `nbins_conforms: false`, a non-finite bin is a `COMPLETE` capture
carrying `all_finite: false`, and `row_index_matches_S: false` is a measurement and not a
failure. Each of those has a test asserting `COMPLETE`, because a validator that refuses
everything is not correct either.

Zero and `false` are not emptiness. A `count` of 0 is a real answer, `first_edge` is 0.0 in the
fixtures on purpose, and `unchanged: false` is the measurement itself. An empty digest never is,
which is why the two are typed separately rather than both tested for truthiness.

## The fixed attempt id — SURFACED, NOT FIXED. It needs a ruling, not a patch

`CONTRACT-20260908-pm-root-inspection.json:96` hardcodes
`--attempt-id pm-root-inspection-20260908-attempt-1`. Both reviewers independently reproduced
what follows from that, and **it is not repaired here**:

1. attempt 1 runs and writes `pm-inspection-report.json` at the fixed `output_namespace`;
2. attempt 2 runs, and the producer **correctly** refuses to overwrite that report;
3. the validator reads the report **from attempt 1**, whose `attempt_id` matches the contract's
   literal, and returns `COMPLETE`, granting `unlocks: preserve-capture-as-measurement` for a
   capture this attempt never performed.

The overwrite refusal makes the stale case the *default* outcome of a re-run rather than an edge
case. `test_stale_report_from_another_attempt_is_refused` tests a *different* attempt id, which
is a different hazard from the fixed-path one.

**Why no code change fixes it.** The producer and the validator already agree on the id; the
defect is that the id is a constant in a committed file, so it cannot distinguish "the producer
just wrote this" from "this has been sitting here since attempt 1". Any per-run value the
producer invents and the validator reads back is a value the validator learns *from the report
it is validating*, which is the class of defect this whole package keeps failing. The id has to
come from **outside both halves**.

**Proposal, for the contract and launcher owners.**

- **Where the nonce comes from.** The launcher generates it once per invocation, as
  `pm-root-inspection-20260908-<utc-timestamp>-<8 hex>`, from `secrets.token_hex(4)` and the UTC
  clock. Not from a git sha (a re-run at the same sha is exactly the case that must be
  distinguishable), and not from the scheduler's job id alone (a requeued array task can repeat
  it), though including `SLURM_JOB_ID` alongside the random part is harmless and useful for
  cross-referencing.
- **Who injects it.** Whatever launches *both* halves — the same process that runs the producer
  and then the validator. It passes the identical string to `--attempt-id` on both, and derives
  `--out` for both from it, so each attempt gets a fresh run directory and the producer's
  overwrite refusal stops being reachable in the normal case.
- **What the contract says instead.** The `terminal_validator.argv` entry for `--attempt-id`,
  and the `--out` path that embeds it, become declared **substitutions** rather than literals —
  e.g. `"--attempt-id", "${ATTEMPT_ID}"` with an `attempt_id` block stating who generates it,
  the format, and that it must be identical across the two halves and unique per invocation.
  That requires `campaignctl`'s argv binder to permit and record a substitution, which is why
  this is a contract-and-launcher change and not a code change.
- **A second, independent belt.** The validator could additionally require that the report's
  `finished_at_utc` be no older than the validator's own start minus a bound. That is a
  *freshness* check, it is not free of judgement (someone has to choose the bound), and it is
  weaker than a nonce, so it is recorded here as an option and not implemented.

**Related, and worth a ruling in the same pass:** the contract commits **no producer argv at
all** — `"producer"` is a free-text field — so nothing committed pins the producer's
`--attempt-id`, `--out` or `--data-root`. The validator now refuses a report whose `data_root`
disagrees with the bindings, which closes the consequence of a wrong `--data-root` but does not
pin the argv.

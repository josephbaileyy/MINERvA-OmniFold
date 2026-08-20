# Provenance debt: what the standard-P4 chain does NOT establish (2026-08-10)

**Status of this document.** A deliverable, not a footnote. It exists because the covariance product
is being validated under a **reduced standard** — as a fixed object, by direct audit — rather than
by a passing provenance pipeline. That is a deliberate change of approach, and the price of it is
that the gap has to be written down completely and in advance. **Declared debt is defensible; debt
discovered later is not.**

**Nothing here authorizes adoption.** The candidate carries `publication_gate_rejects_this: true`
throughout and `p4_adopt_standard.py` refuses it.

---

## 0. THE LARGEST GAP: there is no CI in this repository

Stated first because it conditions every other claim in this document and every test count in the
repo.

**Verified 2026-08-09 by `git ls-files`:** no `.github/workflows`, no `.gitlab-ci.yml`, no
pre-commit config, no Makefile target. Every guard described anywhere in this lane —
fail-closed gates, snapshot regeneration, hash bindings, mutation harnesses — **binds an author who
happens to run `pytest`. None binds a commit.**

**Therefore: "the suite is green" is a statement about a machine, not about the repository, and
every citation of a test count should carry that qualifier.** A green count means *someone ran it
somewhere*, not that the tree is in that state.

**Three incidents this plausibly underlies**, all from this campaign and all caught late or by
accident rather than by a gate:

1. **The ledger id collision risk.** BEN ids 077–080 were allocated from the shared maximum into
   the PET lane's range while the header paragraph forbidding exactly that was on screen. Caught
   during a manual merge, not by anything automatic; the PET lane took 077 two commits later.
2. **The hash-pinned file drift.** A five-line guard added to `test_p3f_pet_fullevent_launcher.py`
   silently voided a sha256 frozen into `p3f-pet-gate3-launch-code-gate-20260720.json`. The binding
   test that should have caught it *was itself red for a full working session*, invisible because
   nobody's `pytest` run was authoritative.
3. **The collection abort that masked seven failures.** A module-scope `open()` on a hardcoded
   `/pscratch` path aborted collection of the entire `tests/` directory off-cluster. Seven real
   PET-lane failures were hidden behind it for an unknown period — a directory that cannot collect
   reports nothing, and nothing reads like fine.

Each is the same shape: a check existed, was correct, and was not binding on anyone.

**One guard is already doing CI's job, and it should be kept when CI lands.** The sweep-snapshot
test (`tests/test_p4_sweep_snapshots.py`) has now caught **three** corpus changes made entirely by
the *other* lane — new shell launchers moving the pipeline corpus 330 → 332 → 333 → 334 — none of
which this lane wrote or would have noticed. In a two-lane repo with no CI, a committed snapshot
plus a regenerating test is the only thing detecting cross-lane drift at all. That is an argument
*for* the post-freeze CI item, and equally an argument for **keeping this guard when CI arrives**
rather than retiring it as scaffolding: CI would run it, not replace it.

**This is recorded, not scheduled.** Adding CI now is the add-surface reflex this freeze exists to
stop, and it is post-publication infrastructure rather than a repair-round item. The correct
disposition is: record it, qualify the claims that depend on it, move on.

## 1. Why the standard was reduced

Five `standard-p4-verifier` passes on the provenance pipeline returned outstanding-defect counts of
**6 → 4 → 6 → 9 → 14**. In the last round, **three of six new defects were in guards written during
that same round to close other defects**. The audit target was code under active development, so the
surface grew every round and the process could not converge — it was generating work faster than it
consumed it.

The decision (Joseph, 2026-08-10) is to stop auditing the *pipeline* and audit the *product*:

> *Given this covariance and these ten endpoint ROOTs, is the covariance correct?*

That question is bounded, is about a fixed object, and is answerable. The pipeline question is
neither bounded nor converging. **The trade is explicit: we gain a decidable audit and we give up
the claim that the machinery which produced the object is itself verified.** This document is that
give-up, itemised.

## 2. What the product audit DOES establish

Properties checkable on the covariance and the ten endpoint ROOTs as they stand, independent of how
they were made:

- symmetry, positive semi-definiteness, eigenvalue diagnostics;
- exact block reconstruction — the total equals the sum of its recorded components;
- mask and bin-ordering consistency against the frozen central products;
- marginal identities (5D → 4D) and projection validity as recomputation identities;
- agreement of derived quantities with the same quantities computed by an independent route;
- endpoint content reproduction against the 2026-07-18 reference at a declared tolerance
  (per-bin 1e-9, integral 1e-11), 10/10, worst 1.83e-11 / 2.87e-12.

## 2b. PRODUCT AUDIT RESULT — 4D leg: **CORRECT** (2026-08-10)

Independent audit of the projected 4D covariance, performed by the `codex-school` delegate
**directly on the object** from a raw-array numpy dump — no execution step of mine in this leg.
Receipt: `runs/standard-p4-verifier/20260810T0530Z-product-audit-4d-verdict.json`.

**Verdict: CORRECT.** All eleven checks pass:

| check | computed |
|---|---|
| symmetry | relative `1.878e-16` |
| PSD | λ_min `-7.85e-92` against λ_max `1.50e-76` — negativity at round-off, ratio ~5e-16 |
| finite | 23 280 625 / 23 280 625 entries finite; diagonal strictly positive |
| mask / reachable support | `n5=10694`, `n4=4830`, `n4_reachable=4825` = covariance dimension |
| unreachable bins | the same five indices, independently rederived, carrying 0.0000 % |
| row-order consistency | `corr(log sqrt(diag C), log W-marginal central) = 0.9923` |
| W-marginal identity | two routes agree to `8.07e-17` |
| trace, Frobenius | two routes agree to `1.36e-15` |
| **Cauchy–Schwarz** | **0 of 23 280 625 entries violate `|C_ij| ≤ sqrt(C_ii C_jj)`** |
| scale sanity | relative uncertainty median 11.5 %, no unphysical bins |

Eleven manifest claims were recomputed rather than believed; nine reproduce exactly, and the two
that do not are informational: the minimum eigenvalue (`-3.71e-92` stated vs `-7.85e-92`, both at
round-off, different eigensolver paths) and `projection_identity_relerr` (`9.39e-17` vs `8.07e-17`,
a different norm convention).

**One LOW finding, recorded not fixed** (the freeze): the report-only field `integral_ratio` is an
unweighted sum of differential bin contents, **not a phase-space integral** — the bins are
densities and the sum omits bin volumes. The number is a legitimate comparison statistic; its
*name* overclaims. Same shape as the "direct block sum" naming defect. It affects no gate.

### What the 4D audit explicitly does NOT cover

Copied verbatim from the delegate's receipt, because this is the boundary of what has been checked:

- The identity C4_projected = M C5 M^T, because the 5D covariance C5 was not supplied or accessed in this pass.
- The 5D component decomposition, active-band traces, stat/ML reconstruction identities, or 5D PSD; those remain unaudited until the supplied script's raw output is returned and judged.
- An exact binding between each covariance row and its physical 4D bin label, because the NPZ carries no covariance-row index vector; alignment was tested indirectly through support dimension and covariance-to-central scale structure.
- The source ROOT-file digests claimed for the central products, component files, or 5D candidate, because those source files were not supplied locally.
- Provenance machinery, adoption state, manifests as software, guards, tests, launchers, or any pipeline code that produced the fixed arrays.
- Whether the uncertainty ensemble includes every physically required systematic source; this audit tests the supplied covariance object's numerical and central-product consistency, not the completeness of the uncertainty model.

The third bullet is a defect in **my dump**, not in the product: the npz carried no covariance-row
index vector, so row-to-physical-bin alignment could only be tested indirectly, through support
dimension and covariance-to-central scale structure. A future dump should ship the index vector.

**5D leg: UNAUDITED as of this pass.** The delegate authored a self-identifying audit script
(`runs/standard-p4-verifier/20260810T0530Z-product-audit-5d-script.py`) which hashes every input
against a claimed digest, prints all shapes and independently derived counts, and computes
deliberately redundant quantities that must agree. It is being executed and its raw output returned
for the delegate's judgement.

## 2c. PRODUCT AUDIT RESULT — 5D leg: **CORRECT** (2026-08-10)

The delegate authored the audit script, I executed it verbatim, the delegate judged the raw output.
Receipt: `runs/standard-p4-verifier/20260810T0600Z-product-audit-5d-verdict.json`; the executed
script, the raw output and the judgement transcript are all committed beside it.

**It checked the output's integrity BEFORE the physics**, which was the point of the ingredients
requirement — `output_trustworthy: true`, on six grounds: exactly one BEGIN and one END with END the
final record at `status=COMPLETE`; 209/209 records parse with no timestamp inversion; every declared
input `claim_holds=true` with `size_begin = size_end = bytes_read`; the derived grid
`14·16·7·7·6 = 65856` matching the central array and `10694` reported bins recomputed rather than
accepted; and its own redundant quantities agreeing with each other.

**Verdict: CORRECT.** Twelve checks pass. The reconstruction results are the load-bearing ones:

| check | computed |
|---|---|
| inventory | exactly 48 cycle-1 TH2D keys: 40 retained + 5 active + 3 totals |
| active-systematic reconstruction | stored active total = sum of five active components **bit-for-bit** |
| full systematic reconstruction | 40 retained + 5 active reproduce `C_syst`, max_abs `3.8e-93`-scale |
| **full total reconstruction** | **`C_total = C_syst + C_stat + C_ML`, max_abs `6.76e-93`** |
| symmetry / finiteness | 114 361 636 / 114 361 636 finite; symmetry at round-off |
| PSD | λ_min `-4.23e-91` vs λ_max `1.21e-75` — round-off |
| **Cauchy–Schwarz** | **0 of 114 361 636 entries violate the inequality** |
| scale sanity | central total `3.070e-38`, consistent |

### Two informational findings, and the first one matters downstream

**(a) The combined covariance is numerically rank-deficient:** effective positive rank **263** out
of 10 694, with 10 431 numerical nulls (the 4D leg saw the same thing — numerical condition number
infinite). This is not a defect in the object; it is what a covariance built from ~45 two-endpoint
MAT bands plus stat and ML *is*. But it is a property any consumer must know: **this matrix cannot
be inverted**, and any χ² or likelihood built on it needs a pseudo-inverse or an explicit
regularisation whose choice is a physics decision, not a numerical detail. Recorded here because a
future reader who inverts it naively will get nonsense with no warning.

**(b) Exact covariance-row to physical-bin binding is not encoded in the product** — the same gap the
4D leg reported. Row order is inferred from the reported-support ordering rather than carried as an
explicit index vector. Both audits tested alignment indirectly (support dimension, covariance-to-
central scale correlation) and both said so.

## 2d. WHAT THE TWO LEGS TOGETHER DO NOT ESTABLISH

Verbatim from the delegate:

> Together, the 4D and 5D legs establish that the fixed 5D candidate and fixed projected 4D
> covariance are each numerically correct and internally and centrally consistent, and that the 5D
> recorded blocks reconstruct, but they do not establish the cross-object identity
> `C4_projected = M C5 Mᵀ`, exact row-to-bin labels, uncertainty-model completeness, or pipeline
> provenance.

**The cross-object identity is the largest remaining gap and it is cheaply closable.** Each object
was audited alone: the 4D leg had no access to `C5`, and the 5D leg was not asked to project. The
pipeline records `projection_identity_relerr = 9.39e-17` for exactly this identity, but that is the
pipeline's own claim and both audits correctly declined to credit it. Closing it needs one
recomputation of `M C5 Mᵀ` on the cluster compared against the stored `C4`, judged by the delegate.
**Not done under the current freeze; flagged as the first thing worth doing if the freeze lifts.**

## 2e. CLOSED 2026-08-10 — Packet B1: `C_syst` band-set completeness (verifier defect #6)

**Closed.** The referee is the **support family**, not the manifest and not the candidate: a build
that enumerated the wrong band set produces a manifest whose stored `C_syst` equals the sum of the
bands it lists, so every identity reconstructs perfectly while the systematic budget is short. The
candidate is downstream of that build and inherits the omission, so it cannot referee. The support
family is upstream, `p4_build_components.py` enumerates from it, and the manifest pins its sha256.

Both halves of the verdict's "band-set equality **or** component identity" are implemented and
**both are demonstrated**, plus the over-rejection direction.

**Eleven adversarial manifests, authored blind by the oversight session** independently of the
check (Packet B constraint 3; BEN-040 and repair-7's self-guard are why the constraint exists),
key withheld until after the run. Ten must-reject, one accept-control not identified in advance.
**Eleven correct calls.** Pre-fix code accepts all ten must-reject variants — demonstrated, not
asserted. Record: `tests/test_p4_repair.py::PacketB1BandSetCompleteness`, fixtures under
`tests/fixtures/packet_b1_adversarial/`.

Two variants are worth keeping visible because they would defeat the obvious implementations:
`B1_E` omits a **lateral**, leaving `retained_bands` at the correct 40; and `B1_H`'s perturbed hash
**matches the real one in its first 12 characters**, which this repo prints almost everywhere, so a
prefix comparison is the natural thing to write.

### 2e-i. An authority that is not pinned is not an authority (found by asking for the case that would break my own check)

**This is the generalisable finding of B1 and it is not really about band sets.**

The completeness check compares the manifest against an inventory taken from a support-family ROOT
supplied by the caller (`--support`). Nothing required that ROOT to be the one the build actually
enumerated from. `p4_validate_active_lateral.py` **never checked `support_family_sha256` at all**,
and the adopter's check is a different thing — it hashes the file at the path the *manifest*
records, which cannot detect a validator refereeing against a different object. So the check would
have compared a manifest against the wrong inventory and reported a clean set match.

**Generalise past B1: any check that names its own referee has this exposure.** The referee must be
pinned by the same evidence chain as the thing being judged, or the judgement is about an unrelated
object. Now bound before any set comparison runs.

**How it was found, which is the part worth propagating.** Not by review, and not by the fixture
author. After batch 1 came back clean I asked the oversight session for *the case that would break
my own check* — naming `support_family_sha256` as a field I had trusted without verifying. It built
it (`B1_J`), and the hole was real. **The habit is: after your check passes everything, ask
someone else to attack the assumption you did not test, and name the assumption yourself.** A
fixture author cannot guess which assumption you left implicit; only you know where you did not
look.

### 2e-ii. Cost, measured not estimated

The validator now recomputes content hashes for all 45 support-family bands, i.e. reads the full
support family on every stage-5 run. **This is the right trade** — B1 is the only debt item that
can produce a *confidently wrong* number rather than an unverifiable one, and stage 5 runs rarely.
The added wall-time is to be **measured on the next cluster run and recorded in the receipt**, not
estimated: this project sizes run windows from measurements, and the next person to size a stage-5
window would otherwise guess. *(Pending as of this writing.)*

## 3. What it does NOT establish — the debt

### 3a. Open verifier defects, carried deliberately

From the repair-7 verdict (`20260810T012645Z-repair7-verdict.json`, BLOCK, 14 outstanding). Two
were fixed; the rest are debt.

| # | status | what remains unestablished |
|---|---|---|
| 1 | PARTIAL | Endpoint evidence: content comparison is real and discriminating, but verifier-crosscheck blockers are applied *after* consumable evidence is written, so a consumer can read evidence that a later check would have rejected. |
| **2** | **OPEN, deferred** | **Resume provenance binds only the unfold driver's blob.** Changes to `omnifold.py` or `xsec_nd.py` do not invalidate a resume, so a skipped endpoint may have been produced by different code than the manifest implies. |
| 3 | CLOSED | — |
| 4 | PARTIAL | The verifier's declared `review_scope` is trusted verbatim, and the fallback import graph omits executed shell dependencies. A narrow scope is not detected. |
| **5** | **OPEN, deferred** | **The token gate accepts symbolic revisions** (e.g. `HEAD`) and does not compare reviewed files against their working-tree bytes — only against the committed blob. |
| **6** | **OPEN, deferred** | **`C_syst` recomputation trusts the manifest's `candidate_keys`** and never verifies exact band-set equality or component identity. A manifest that omits a band yields a total that reconstructs perfectly from the bands it admits to. |
| **7** | **OPEN, deferred** | **The mutation harness is incomplete** — it retains detached/textual guards and lacks live positive and negative mutants. |
| 8 | PARTIAL | Sweep corpora omit `p4_check_verifier_token.py`; snapshots are count-and-name only. No CI exists to enforce regeneration (see §3d). |
| 9 | PARTIAL | The co-located P4 status file remains false, and no committed machine-readable products summary exists for job 56495756. |

Plus four unfixed new defects from the same verdict:

- the report-only cross-check emits NaN summaries on non-finite input beside zero threshold counts;
- a **projected** artifact does not inherit the self-declaring rejection marker — the projection
  manifest does not propagate it (the ROOT and its component manifest do carry it);
- `check_projection_validity`'s second leg is named "direct block sum" but recomputes by the same
  route (`M@C` then `@Mᵀ`) and shares `M`. **Verified independently: it is not a gate that cannot
  fire** — injecting a 50 %-wrong `project()` is caught at rel 3.3e-01 — so it catches an error in
  `project()` but not an error in `M` or a conceptual error about the projection. The *name*
  overclaims; the check is narrower than it sounds. Pattern B, not Pattern C.
- `TmpdirGuardItself` does not detect helper-mediated `TemporaryDirectory` use.

### 3b. The two things fixed, and precisely what they buy

- **Reachable 4D support.** Stage 6 can now execute. The projected product is defined on the 4825
  reported 4D bins the 5D support reaches; 5 bins (0.0000 % of the 4D total) are excluded and are
  recorded by global index in the projection manifest. **This does not establish that 4825 is the
  right support** — it establishes that the support is derived, recorded, and no longer silently
  asserted.
- **Manifest–receipt binding.** The non-adoptable marker can no longer be removed by handing the
  adopter an edited manifest. **This does not establish that the adopter is otherwise sound**; it
  closes one bypass of one safety property.

### 3c. Structural limits the audit cannot reach

- **The endpoints are not bit-reproducible** (KNOWN_ISSUES #24). Every provenance statement about
  them is a content statement at a tolerance, never an identity. A re-run that agrees to 1.8e-11 is
  the strongest available claim.
- **The integral leg of that tolerance is a discriminator with ~103× total dynamic range**, already
  sitting at 54.6 % of its coherent ceiling. It cannot be widened again without ceasing to
  discriminate. Breach response is pre-specified at `p4_lib.REPRO_RTOL_INTEGRAL`.
- **`hasTruthOnlyMisses` is misnamed at the writer** — a per-playlist flag summed by `hadd`. The
  reader is correct; the artifact is misleading to anyone who has not read the finding.
- **J36 is nine sites, not one**, and unrepaired. Its shape effect on the 2D analysis is **measured
  and bounded at ≤ 0.15 %** (VALIDATION_LEDGER 2026-08-09), so no 2D shape statement is at risk —
  but the defect is bounded, not corrected, and the bound is pre-unfolding, MC-signal-reco, and
  covers pT and p∥ only.
- **The 5D→4D marginal and the independent 4D unfold differ by a median 4.4 %** in shape (integrals
  agree to 0.56 %), with four candidate mechanisms excluded and none established. This is reported
  as an unexplained estimator dependence, not attributed.

### 3c-bis. The product auditor cannot touch the product

Recorded here because it is a limit on the *new* approach, discovered while setting it up, and it
would be dishonest to describe the product audit without it.

The covariance is **42.3 GB on NERSC scratch**. The `standard-p4-verifier` delegate runs in a
read-only sandbox on a laptop and has no access to that filesystem. So the audit cannot be
"delegate opens the product and checks it". The workable arrangement is:

1. the delegate **authors** the audit script, without my input on what it should compute;
2. I **execute it verbatim** on the cluster and capture the raw output;
3. the delegate **judges** the output.

**What this preserves:** the specification of the audit and the interpretation of its results are
independent of the implementing agent. That is the part that matters most, and it is the part the
pipeline audits were failing to protect.

**What this does NOT preserve:** I am in the execution path. A mis-run, a silently truncated output,
or a substituted input would not be visible to the delegate except through the output it is handed.
Mitigations, all partial: the script is authored by the delegate so I cannot shape what it looks
for; the delegate is instructed to require enough raw material in the output to detect an
inconsistent run (per `CONVENTION-receipt-ingredients.md`, a verdict-only output is unfalsifiable);
and the script and its stdout are both committed, so the pairing is auditable after the fact by
anyone who can reach the cluster.

**Residual risk, stated plainly: the product audit is independent in specification and judgement,
and NOT independent in execution.** Closing that would need either a delegate with cluster access
or a product small enough to transfer, and neither is available today.

### 3d. Enforcement debt

See **§0** — no CI exists, so no guard in this document binds a commit. Listed here only so the
debt inventory is complete; the discussion and the incidents it underlies are at the top.

## 3e. SUPERSEDING DECISION 2026-08-10 — five of these items are being closed under Packet B

Joseph chose standard **B** (no debt that can affect a *quoted* number) over both leaving the debt as
declared and attempting standard C (no pipeline debt at all).

**In scope and being closed** — see
[`PACKET-20260810-B-no-quoted-number-debt.md`](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/0b329e8ae8482e6334a68faf947fc80ae7265ac9/docs/orchestration/PACKET-20260810-B-no-quoted-number-debt.md "evidence/prepublication-2026-08-20-0b329e8a:docs/orchestration/PACKET-20260810-B-no-quoted-number-debt.md"):
defect **#6** (band-set completeness — the only item here that can yield a *confidently wrong* number
rather than an unverifiable one), defect **#2** (resume binds one blob), defect **#1** (consumable
evidence written before blockers), the **projected artifact not inheriting the rejection marker**, and
**J36's C++ site** at `build_1d_ibu_inputs.py` → `ExtractCrossSection`, which reaches the quoted
OmniFold-vs-IBU cross-check.

**Remaining declared debt, unchanged:** #4, #5, #7, #8, #9, the NaN summaries, the
`check_projection_validity` naming overclaim, `TmpdirGuardItself`, CI (§0), surface reduction, and the
5D artifact's derivable-not-self-contained row order.

**Standard C is deferred post-publication, on measured grounds.** Across four repair rounds the lane
closed 9 defects while outstanding went 6 → 14 — introduction ran about **1.9× closure**, and three of
repair-7's six new defects were in guards written that same session. C is therefore not schedulable as
a pre-publication gate, and it would certify a chain that will not be re-run before the paper. It
remains the right eventual target; §0 is its precondition.

**Do not read B as C.** When Packet B closes, this document must say that B is met and C is not.

## 4. The reduced standard, stated for the record

The covariance product is offered as: **an object whose internal consistency, mask/order
consistency, reconstruction identities and reproduction-against-reference have been checked
directly, produced by a pipeline whose provenance guarantees are incompletely verified and whose
open defects are enumerated in §3a.**

It is *not* offered as: a product of a verified chain.

Anyone quoting a number derived from it should cite this document alongside it. If that is not an
acceptable standard for publication, the correct response is to close §3a's open items — not to
restate the product's status more favourably.

## 5. Provenance of this document

Every claim above is either a direct quotation from a committed verifier verdict, a committed ledger
entry, or a measurement recorded in a committed finding. Per
`docs/orchestration/CONVENTION-receipt-ingredients.md`, the numbers here ship with their sources:

| claim | source |
|---|---|
| defect counts 6/4/6/9/14 | the five verdicts under `runs/standard-p4-verifier/` |
| 10/10 reproduction, 1.83e-11 / 2.87e-12 | `VALIDATION_LEDGER.md` 2026-08-09, evidence job 56532439 |
| integral leg 103.4× range, 54.6 % of ceiling | `p4_lib.py` `REPRO_RTOL_INTEGRAL` derivation |
| J36 ≤ 0.15 % shape | `VALIDATION_LEDGER.md` 2026-08-09, 12 per-playlist event-loop outputs |
| 4.4 % median estimator dependence | `FINDING-20260809-stage6-central-gate-cannot-pass.md` |
| 5 unreachable 4D bins, 0.0000 % | this round's projection manifest |
| no CI | `git ls-files`, 2026-08-09 |

# PACKET B — close every debt item that could move a quoted number (2026-08-10)

**Decision.** Joseph, 2026-08-10, chose standard **B** over the alternatives:

| standard | requires | disposition |
|---|---|---|
| A — no *undeclared* debt | the debt document | **already met** (`PROVENANCE-DEBT-20260810-standard-p4.md`) |
| **B — no debt that can affect a quoted number** | the five items below | **THIS PACKET** |
| C — no pipeline debt at all | CI, then the 14, then surface reduction | **deferred post-publication** |

**Why not C.** Measured across four repair rounds the lane closed 9 defects while outstanding went
6 → 14, so ~17 were introduced or newly surfaced — introduction running about **1.9× closure**. That
is divergence, not slow convergence, and repair-7 showed the mechanism: three of six new defects were
in guards written that same session to close other defects. C is therefore not schedulable as a
pre-publication gate, and it would certify a chain that will not be re-run before the paper. It stays
the right eventual target (see the debt document §0 on CI) and is out of scope here.

**The distinction this packet rests on.** The product audit already closed most correctness-bearing
debt *for the artifact in hand* — it verified the inventory at exactly 48 keys = 40+5+3, which is
item 1's hazard below, and content comparison passing 10/10 covers most of item 2's. What remains is
overwhelmingly about **repeatability of future runs**. This packet closes the subset that could move a
*quoted* number, and does not attempt the rest.

---

## ID DISAMBIGUATION — read this before citing an item (BEN-080)

**`B1` was already taken when this packet was written, and that is an authoring error in this
document.** It already denoted the **rate-injection closure** in the PET lane (`CLM-010`, jobs
`56358196` / `56358288` / `56358954` / `56360955` / `56363377`), which is one of the items Gate-4 is
blocked on. This packet then named its own items `B1`–`B5`.

The collision is not cosmetic. A status line reading *"B1 closed"* is true of this packet's band-set
completeness item and **false** of the rate-injection closure — and read at face value it would
support a "Gate-4 unblocked" claim that is not the case. It was caught only because the commit *body*
named its scope.

**Going forward, cite these items as `PB1` … `PB5`.** `PB1 == B1` in this document's original
numbering, and existing references in commits and in the provenance-debt document remain valid.
Anything referring to the closure means `CLM-010 B1` and should say so. Same discipline as the BEN
per-lane id blocks: a shared id space needs a prefix, and this document did not give it one.

## Scope: five items, in priority order

### B1 — `C_syst` band-set completeness (verifier defect #6) — **highest priority**

**The defect.** `C_syst` recomputation trusts the manifest's `candidate_keys` and never verifies exact
band-set equality or component identity. Per the verdict: *a manifest that omits a band yields a total
that reconstructs perfectly.*

**Why it ranks first.** It is the only item on this list that can produce a **confidently wrong
number** rather than an unverifiable one. Every reconstruction check passes on a silently
under-counted systematic budget, because the check tests that listed components sum to the total, not
that the listed set is the required set.

**Acceptance.** Exact band-set equality and component identity verified against a declared required
inventory, not against the manifest's own list. Both directions demonstrated: a manifest with one band
omitted must **FAIL**, and the current 40-band artifact must still **PASS**.

### B2 — resume provenance binds only the unfold driver's blob (verifier defect #2)

**The defect.** Changes to `omnifold.py` or `xsec_nd.py` do not invalidate a resume, so a skipped
endpoint may have been produced by different code than the receipt implies.

**Acceptance.** Resume validity binds the full executed set, not one blob — the execution-derived
scope from repair-7 item 2 already exists and should be reused rather than re-derived. Demonstrate
that a change to `omnifold.py` invalidates a resume.

**Trap, and it has fired twice in this lane.** A new check demanding a field or value that correct
existing artifacts do not carry blocks correct data — `code_rev == HEAD` and `verifier_crosscheck`
both did exactly that (`KNOWN_ISSUES #24`). **Decide the legacy rule in the same commit as the
check**: either backfill with provenance recording the backfill, or grandfather explicitly with a
stated reason. Not silently, and not by letting the check fail on correct data.

### B3 — consumable evidence written before blockers apply (verifier defect #1)

**The defect.** Verifier-crosscheck blockers are applied *after* consumable evidence is written, so a
consumer can read evidence that a later check would have rejected.

**Acceptance.** Evidence is not readable as consumable until every blocker has passed —
write-to-temp + rename-on-complete, or a `.PENDING` name until validated. The `.FAILED.json`
pattern already in this chain is the precedent. Demonstrate that a run failing a blocker leaves no
consumable evidence.

### B4 — a projected artifact does not inherit the rejection marker

**The defect.** The projection manifest does not propagate `publication_gate_rejects_this`, so a
projected product descended from a marked parent does not itself refuse. The ROOT and its component
manifest do carry it.

**Why it is in scope.** It is a *misreading* hazard on a publication-path object, the same class as
the line-105 stale-bar field in the PET lane: an artifact that reads as adoptable when its parent is
not.

**Acceptance.** Propagation implemented; a projected artifact from a marked parent refuses, and the
adopter refuses it. Both directions demonstrated.

### B5 — J36's C++ site, which reaches a quoted cross-check

**The defect.** `build_1d_ibu_inputs.py` reads `hadd`-summed POT from the merged omnifile, rewrites it
as `POTUsed`, and `sbatch_ibu_1d_projection.sh:51` runs `ExtractCrossSection` on that — the same
per-playlist mixture defect, one step removed through an intermediate file. Its output is the quoted
OmniFold-vs-IBU cross-check.

**What is already measured.** The 2D shape effect is bounded at **≤0.15%** (shape max abs 0.073% pT /
0.143% p∥; low-pT ridge 0.032%; normalisation +0.119%), and `app_statmethods.tex:983`'s 1–2% claim
survives with 14–30× margin. The scale also cancels between the OF and IBU arms.

**Acceptance — this one may be prose.** Either fix the per-playlist scaling and re-run the
comparison, or document the ≤0.15% bound **at the point of quotation** so the claim carries its own
error budget. Choose on effort; the measurement exists, so documenting is defensible. State which was
chosen and why.

---

## Explicitly NOT in scope

Carried as declared debt, unchanged, and **not to be opportunistically fixed**:

- verifier defects **#4** (review_scope trusted verbatim), **#5** (token gate accepts symbolic
  revisions), **#7** (mutation harness incomplete), **#8** (sweep corpora / count-and-name snapshots),
  **#9** (co-located status file, missing products summary);
- the report-only cross-check's NaN summaries on non-finite input;
- `check_projection_validity`'s naming overclaim — independently verified as Pattern B, not a gate
  that cannot fire (a 50%-wrong `project()` is caught at rel 3.3e-01);
- `TmpdirGuardItself`'s helper-mediated `TemporaryDirectory` gap;
- CI (debt document §0), surface reduction, and the 5D artifact's self-contained row index — the row
  order stays derivable and hash-pinned, and the audited 42.3 GB digest is not to be broken for it.

---

## Process constraints

These are what keep the packet from becoming repair-8.

1. **The freeze holds for everything else.** No new sweeps, no new guards, no new tests-for-guards
   beyond the acceptance demonstrations for these five items. A defect found outside the five is
   *recorded*, not fixed.
2. **Every acceptance demonstration must fail against the pre-fix code, and that failure must be
   shown.** This is the rule whose absence produced repair-7's findings 1 and 3 — a self-guard that
   shares an assumption with the code it guards cannot see the defect.
3. **The adversarial cases are authored independently of whoever writes the fix.** This lane has the
   documented blind spot twice over: BEN-040 (a fixture shaped like the consumer rather than the
   producer) and repair-7's self-guard stubbing the live blob to equal its fixture. For B1
   especially — where the whole hazard is a manifest that reconstructs perfectly — the omitted-band
   case must not be built by the same agent that writes the completeness check.
4. **Legacy rules land in the same commit as any new check** (B2 above, `KNOWN_ISSUES #24`).
5. **No adoption, no token, no threshold change, no engine edit.** The candidate keeps its
   non-adoptable marker throughout this packet.

---

## Verification

**One verifier pass, scoped to these five items only.** This is a design decision, not an
economy: a general audit returns 14+ again and re-enters the loop this packet exists to leave. The
commission asks whether B1–B5 are closed, with both directions demonstrated, and explicitly does not
re-audit the pipeline.

Delegate read-only per `CLAUDE.md`; verdict receipt committed under
`docs/orchestration/runs/standard-p4-verifier/`; `git status` after it finishes and preserve any diff
before reverting.

---

## Definition of done

1. B1–B5 closed, each with a demonstrated failure against pre-fix code and a demonstrated pass on
   current correct data.
2. B5's disposition stated — fixed, or bounded-and-documented at the point of quotation.
3. One scoped verifier pass returns PASS on B1–B5.
4. `PROVENANCE-DEBT-20260810-standard-p4.md` updated: these five move from open to closed, the
   residual is restated in full, and the document says plainly that standard **B** is met and **C** is
   not.
5. The debt document's own framing updated so a reader cannot mistake B for C.

**What this packet does not do.** It does not make the chain re-runnable with confidence, it does not
add CI, and it does not authorize adoption. It makes the claim *"nothing outstanding can move a
published number"* true and checkable. Adoption remains a separate decision on the reduced standard.

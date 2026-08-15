# DECISION 2026-08-15 — Joseph rules `OI-6`, `OI-8` and `OI-126`

**All three had sat `WAITING-USER` since 2026-08-12.** Recorded before any of it is acted on, per
`BEN-201`. Transcribed by the personal-orchestrator (mediator); the lanes cannot see the original and
this document is the authority they should read rather than any relay of it.

## The grants, verbatim and complete

> **OI-6:** "Okay keep purity, but make sure this distinction and reasoning is obvious in the note. Go
> forward with the rest of the GBDT"

> **OI-8:** "Okay your recommendation sounds good, go ahead with it if anyone else agrees with you."

> **OI-126:** "just go with the consensus"

---

## `OI-6` — CLOSED. Purity is the footing, and the distinction must be visible.

**Reading (A) is adopted:** the standard 5D chain stays purity-footed, consistently labeled, and the
lateral is built from the **existing** ten unfolds. Reading (B) — that "N-D production uses
`negweight-refined`" reaches the standard chain — is **rejected**. It would have required re-running the
central, 169 vertical, 18 detector and 10 lateral unfolds, **and it would have invalidated the
J28-corrected covariance that was just adopted.** That last consequence, not the cost, is the decisive
one.

### The measured basis (from `RUNBOOK-20260807-gbdt-closeout.md` §2.1, not re-derived here)

| comparison | result |
|---|---|
| SYST covariance, 187 universes, both modes | negweight `2.9828e-39` vs purity `3.0242e-39` → **0.9863** |
| STAT covariance, matched first-50 seeds | `1.7260e-40` vs `1.7576e-40` → **0.982** |
| real-data totals | agree to **−0.13%**, per-bin median 1.000, 1.4% RMS |

**Why it generalises rather than being luck:** a systematic covariance is the *spread across* universes,
and each universe shifts by ~0.1% in **both** modes, so the two covariances agree by construction.

### THE DISTINCTION JOSEPH IS ORDERING INTO THE NOTE

This is the operative half of his ruling and it is a boundary, not a summary:

- **SAY:** the standard 5D chain is purity-footed; this is a recorded choice; the measured footing
  impact is ~1–2%; the FPS lane carries the `negweight-refined` measurement, so the pair is a
  consistent measurement plus a matched control at a different footing.
- **DO NOT SAY, and do not let a later edit drift into saying:** that the footing is *proven irrelevant
  in 5D*. **There is NO full 5D 187-universe both-mode comparison at the publication 5-iter `lgbm`
  config.** The 5D evidence is a two-universe spot check at 1 iter / `hist`, plus the structural
  identity, plus the full-statistics 2D result. That is ample for the first statement and **not** ample
  for the second.

**This ruling opens `docs/analysis-note/` for this text only.** That gate is otherwise Joseph's alone
and every other prohibition on it stands.

### "Go forward with the rest of the GBDT" — what it does and does NOT clear

**It clears the footing decision, which was blocking by decision.** It does **not** clear the
`standard-p4-verifier`, and no reader of this document should infer that it does. The live verdict
(`runs/standard-p4-verifier/20260810T012645Z-repair7-verdict.json`, `code_rev 5c25333`) is:

```
verdict :: BLOCK
defects_outstanding :: 14
self_guards_adequate :: NO
authorizes_covariance_stages_4_6 :: False
```

**So the standard 5D lateral is still "NOT BUILT, AND NOT ONE RUN AWAY".** Joseph's grant authorises
*proceeding with the lane*; the verifier decides when the covariance stages may run. Those are different
gates and conflating them is the `BEN-082` shape.

~~**The lane's own preconditions survive untouched:** stage 3 must not run on pre-G-1 code, and G-1 is
code-only and not on the cluster checkout.~~ See `OI-8`.

> **CORRECTED 2026-08-15 (`BEN-352`) — superseded text retained above per this repo's convention, as
> `c179a35` did.** **Neither half of that sentence is true, and there is no surviving precondition on the
> run.** G-1 (`5a4009f`, 2026-08-07) **is** on the cluster checkout — measured, cluster `HEAD` is
> `683bdcc` and `git merge-base --is-ancestor 5a4009f HEAD` returns true there — and **stage 3 already
> ran on it**, on 2026-08-08, producing ten ROOTs and ten `mode=produced` receipts stamped
> `bkg_mode=purity`, `code_rev=42268b6`. The "unfixable provenance regression" rested on a claim about
> the launcher that is **refuted in code**: the resume gate skips only on a *passing*
> `p4_check_receipt.py`, not on receipt existence. See `OI-8` below for the full basis.

---

## `OI-8` — IN FORCE 2026-08-15. Corroboration MET; corroborator **AGREED-WITH-CORRECTION**.

~~## `OI-8` — RULED, **CONDITIONALLY**, and the condition is not yet met~~

~~Joseph's grant is explicitly conditional: *"go ahead with it if anyone else agrees with you."* **He is
requiring corroboration, and a mediator's own confidence does not satisfy it** (`BEN-300`: consensus
among restatements of one source is not corroboration). **This section is therefore NOT YET IN FORCE.**~~

> **Superseded text retained per this repo's convention (`c179a35`). Read the correction before the
> stricken material, because the stricken material's *disposition* survives and its *reason* does not.**

**THE CONDITION IS MET.** Joseph required *"if anyone else agrees with you"*; a lane that did not author
the ruling checked the load-bearing claim **in code** and returned **AGREED-WITH-CORRECTION** —
**agreeing with the disposition** (the G-1 cluster-landing request is dead) while **REFUTING its stated
basis**. Corroboration on a disposition is not corroboration of the reasoning that reached it, and here
the two came apart. **The disposition stands; the basis is replaced.**

### The corrected reason

**The G-1 cluster-landing request is DEAD, and NOTHING SURVIVES AS A PRECONDITION ON THE RUN.**

Not because there is nothing left to land, but because **there is nothing left to protect**:

1. **G-1 is already on the cluster.** `5a4009f` (2026-08-07, *"the standard lane can finally express a
   background footing, and it says purity"*). Cluster `HEAD` measured 2026-08-15 = `683bdcc`;
   `git merge-base --is-ancestor 5a4009f HEAD` in `/pscratch/sd/j/josephrb/MINERvA-OmniFold` → **true**.
   The cluster working tree carries the wiring: **at cluster `HEAD` `683bdcc`**,
   `run_p4_unfold_std.sh:37` reads `bkg_mode` from `P4Config` and `:90` passes `--bkg-mode` to the
   driver. **Those two coordinates are the CLUSTER tree's; the same statements are `:41` and `:111` at
   local `HEAD`** — the trees are forked (`OI-74`) and the file has grown since. Cited both ways
   deliberately, because a line number without its tree is the `BEN-066` decay.
2. **Stage 3 already ran, post-G-1, on 2026-08-08.** Ten ROOTs and ten `.done` receipts in
   `active_universe_5d/standard/unfolds/`, each `mode=produced`, `bkg_mode=purity`,
   `code_rev=42268b6dfa2e60a0e4bd491b11ad9b11d0228273`. `42268b6` **contains** `5a4009f` (G-1),
   `febb9a1` (the resume-gate repair) and `2654731` (the legacy-attest deletion) — all three verified by
   `git merge-base --is-ancestor`.

**So the precondition is not merely unnecessary — it is unsatisfiable as a constraint on a run that has
already happened, on code that already contains what the precondition demanded.**

The ancestry measurement the stricken ruling rested on is unaffected and still correct; it was simply
answering a smaller question than the one that mattered.

```
cluster_head_is_strict_ancestor_of_origin_main : true
commits_cluster_ahead_of_origin_main           : 0
```

### THE REFUTATION, in code — the claim was TRUE WHEN WRITTEN and had been FIXED HOURS LATER

**THE CLAIM:** *"stage 3 writes ten receipts with no `bkg_mode`, the launcher skips endpoints that
already have one, and deletions are frozen, so a pre-G-1 stage 3 creates a provenance regression that
cannot be repaired."*

**WHAT THE CODE DOES** — `nd-unfolding/run_p4_unfold_std.sh:77-84`:

```bash
if [[ -s "${OUT}" && -s "${REC}" ]] && valid_root "${OUT}"; then
  if RCHK=$(python3 p4_check_receipt.py --receipt "${REC}" --tag "${tag}" \
              --root "${OUT}" --merged "${MERGED}" 2>&1); then
    echo "[unfold] SKIP ${tag} (receipt validated)"; return 0
  fi
  echo "[unfold] STALE ${tag} -> re-running: ${RCHK}"
  rm -f "${REC}"                       # D2: never leave a stale ROOT/receipt pair behind
fi
```

**The skip requires `p4_check_receipt.py` to PASS. Receipt existence is necessary and not sufficient.**
On failure the launcher prints `STALE ... -> re-running`, `rm -f`s the receipt, and falls through to a
transactional re-run. And `bkg_mode` is exactly what the gate checks:

- `p4_lib.py:796-797` — `bkg_mode` is in `RECEIPT_REQUIRED_KEYS`; `:949-950` fails closed on any missing
  required key (*"incomplete legacy format"*).
- `p4_lib.py:961-962` — `bkg_mode` is **COMPARED** against the declared value, not merely present.

**A pre-G-1 receipt has no `bkg_mode`, therefore FAILS the gate, therefore is DELETED AND RE-RUN. The
gate cast as the trap is the repair mechanism.** The cost of a pre-G-1 stage 3 is **compute, not
irreversibility** — and the freeze on deletions never applied, because the `rm -f` is the launcher's own
and operates on scratch, not on tracked files.

**ORIGIN — and this is the part worth carrying forward.** The claim described the **pre-repair-4** skip
and **was TRUE when written on 2026-08-07**: the gate then was `[[ -s ROOT && -s RECEIPT ]]` plus a
ROOT-key check, and `p4_lib.py:784-787` documents that form and its removal. It was fixed by `febb9a1`
**the same day**, then copied forward into three more documents and into this ruling without recheck.
Filed as **`BEN-352`**.

**Two collateral claims fall with it**, both in `P4_STANDARD_STATUS.md`:
`legacy-attest` is not a path stage 3 can take — it was **DELETED** in `2654731`
(`run_p4_unfold_std.sh:85`: *"the LEGACY-ATTEST path is DELETED, not repaired"*), and the measured
receipts say `mode=produced`, so the ten ROOTs were **re-unfolded**, not attested.

### WHAT THIS RULING DOES NOT SETTLE — two items escalated, not adjudicated here

1. **`P4_STANDARD_STATUS.md:4` records a standing hold from Joseph — *"no cluster P4 run"* — and there
   is no record of the 2026-08-08 run anywhere in the repo.** Whether it was authorized is **Joseph's
   question** and it is already put to him, unanswered. **Recorded as a discrepancy, deliberately not
   adjudicated. The artifacts looking correct is not evidence that the run was authorized.** `OI-75`.
2. **The ten products are UNTRACKED and live only on purgeable scratch** — `git ls-files` over that
   directory returns 0 on both checkouts, and `git status --ignored` reports them `!!`. By this repo's
   own rule *a result does not exist until its commit lands*, **which is precisely why five documents
   say stage 3 never ran.** `OI-75`.

**Nothing in this correction authorizes a run, a promotion, or an adoption.** The
`standard-p4-verifier` `BLOCK` recorded in the `OI-6` section above is untouched and still governs
stages 4–6.

### ~~THE SPECIFIC CLAIM THAT MUST BE CHECKED IN CODE BEFORE THIS TAKES EFFECT~~ — CHECKED, AND REFUTED

**The check was correctly demanded and correctly scoped.** It named the right claim, called it
unverified, and assigned it to a non-author. **That is the mechanism that caught this**, and it is worth
noting that the mechanism was the *principal's* condition rather than any lane's initiative.

### ~~The ruling put to him~~ — SUPERSEDED TEXT, retained verbatim below

~~**The G-1 cluster-landing request is DEAD AS SUPERSEDED, and the constraint it protected survives as a
precondition on the run rather than as a landing action.**~~

~~Measured basis, from `state/cluster-local-fork-freeze-20260812.json`:~~

```
cluster_head_is_strict_ancestor_of_origin_main : true
commits_cluster_ahead_of_origin_main           : 0
```

~~**There are zero unique cluster commits.** Joseph's own item-7 decision — *"use a clean canonical-based
worktree for new cluster work"* — already governs how G-1 reaches any future run, so there is nothing
left to "land" and no conflict with the cluster P4 hold.~~ *(This paragraph is still correct on its own
terms and is stricken only because it is no longer the operative reason.)*

~~**What survives, restated as a precondition:** *no standard-P4 stage-3 run from a tree that does not
contain G-1.* The hazard is real and unfixable if hit — stage 3 writes ten receipts with no `bkg_mode`,
the launcher **skips endpoints that already have one**, and deletions are frozen, so a pre-G-1 stage 3
creates a provenance regression that cannot be repaired.~~ **← REFUTED. This is the false claim.
`run_p4_unfold_std.sh:77-84` skips only on a PASSING `p4_check_receipt.py`; a receipt with no `bkg_mode`
fails `p4_lib.py:949-950`/`961-962`, is `rm -f`'d, and is re-run. Nothing survives as a precondition.**

### ~~THE SPECIFIC CLAIM THAT MUST BE CHECKED IN CODE BEFORE THIS TAKES EFFECT~~ — the demand, retained

~~**That the launcher skips endpoints that already carry a `bkg_mode` receipt.** The whole
irreversibility argument rests on it, the mediator has **not** verified it, and it is asymmetric: cheap
to be wrong about in the direction of re-opening, expensive in the direction of a silent regression.
**Assigned to a lane that did not author the ruling.**~~

**Retained because it is the part of this document that worked.** The claim was named, flagged unverified,
and assigned to a non-author; the check ran and refuted it. The asymmetry call was right in structure and
inverted in outcome — the expensive direction turned out to be *over*-constraint, not silent regression.

---

## `OI-126` — CLOSED as "go with the consensus"

The consensus is on the record and is **4-0**, reached across lanes that disagreed on the way in:

- `DECISION-20260815-oi126-contrast-not-run.md` — do not run the `Exponential(1)` contrast, because
  `Poisson(1)` **is** the sampling distribution and both outcomes support `C_stat`'s validity.
- The fixed-network arm was **retired by its own author** the same day, on a code trace:
  `extract_xsec` has no measured-weight parameter, so a fixed-net arm's spread under measured
  resampling is **identically zero**. Information loss and refit sensitivity are not separable for this
  estimator.
- The limitation statement is already in the note at `92b2873` (`\label{app:cstatlimit}`), note build
  only, all three builds pass.

**So: `C_stat` publishes with the (a)/(b) fork explicitly stated, and the `67%` described as the spread
of a refit estimator under correct measured-statistics resampling — an upper bound on how poorly the
data constrain the cross-section there.**

**What this does NOT do.** It does not ratify the branch-(b) narrowing. Lane C declined that on one
day's tenure and `VL132` records one builder; ratification still rests with the estimator's owner and
the construction reviewer. **Publishing the fork is exactly the move that does not require it.**

---

## Related

- `AUTHORIZATION-20260815-consensus-grant.md` — the standing grant. **None of the above is a spend.**
- `RUNBOOK-20260807-gbdt-closeout.md` §2.1, §2.2 — the purity backing data and reading (A)/(B).
- `state/cluster-local-fork-freeze-20260812.json` — the ancestry measurement `OI-8` rests on.
- `VL132`, `OI-71`, `OI-125` — untouched by any of this.

# PUBLICATION READINESS — 2026-08-22

**CITABLE FOR:** the *shape* of the remaining publication path — what exists, what is ordered before
what, and who must act. Every item carries the command that measured it, so every claim here is
falsifiable at the item level.

**NOT CITABLE FOR:** any physics number, any adoption, any authorization. This document adopts
nothing, authorizes nothing, and lifts no hold. It is a **view assembled by measurement**; where the
canonical artifact and this list disagree, the canonical artifact wins and this row is the defect.

**Built:** 2026-08-22 by the readiness lane, from `main` @ `e2a4409c`, in a worktree outside
`.claude/worktrees/`. **Built from routed artifacts by measurement, not from any lane's summary** —
including `docs/orchestration/LIVE-STATE.md`, which was **STALE** while this was written:

```
$ python3 docs/orchestration/generate_live_state.py --check-freshness   # unpiped; status read directly
STALE :: Git: c4cfbe81, HEAD e2a4409c, HEAD^ 7165ea5c. Regenerate before quoting any field.
  NOTE: regeneration fixes the sha and timestamp; it does NOT revalidate `Declared state`,
        which is authored prose the generator carries forward.
exit status 1
```
`c4cfbe81` is neither `HEAD` nor `HEAD^`, so this is genuinely stale rather than the born-one-commit-
stale state the generator's own rule permits.

## AMENDMENT 1 — 2026-08-22, peer review by an independent LLM session, ALL FOUR OBJECTIONS ACCEPTED

**Recorded here rather than applied silently, because three of the four objections were to the
CLOSE-OUT LANE'S CHAT SUMMARY of this document rather than to the document's own rows, and that
distinction is the useful part.** A measured document can be compressed into a false headline by the
same lane that measured it, and no check in this repo catches that.

| # | objection | verdict | where it landed |
|---|---|---|---|
| 1 | The cause-5 precedent is **weak support for waiving cause 3**; `VL66` turned on a construction-path trace showing PET weights are not inputs to `X`, whereas cause 3 concerns estimator-seed variation in `X`'s **own** estimator. "Nothing enforces the gate in code" is an **enforcement defect**, not evidence the cause is irrelevant. | **ACCEPTED, and the repo's own record backs the objector over this lane** — `SCOREBOARD:670-676`. The precedent's *reasoning runs adverse*; only the *route* transfers. | §0 falsifier (a), rewritten |
| 2 | **12 `PR-J*` headings ≠ 12 open decisions**; `PR-J4` needs no decision, `PR-J11` is closed, `PR-J1` is conditionally granted, `PR-J9` bundles several. | **ACCEPTED.** §10 already decomposed to "9 live asks"; the **chat summary said "12 Joseph decisions"** and that is the number that would have sized the work. | §10 `JOSEPH DECISIONS` row |
| 3 | *"Fifty do not fit"* means fifty cross a **lane-authored ~90% operational line on a soft quota**, not that the filesystem cannot hold them (soft 20 TiB, hard 30 TiB). | **ACCEPTED.** `PR-J3`'s bullets already disclosed soft/hard and the unsourced threshold; the **row's title and the chat summary both asserted a physical impossibility.** | `PR-J3` framing correction |
| 4 | The control plane **still propagates the old error**: freshness fails and `LIVE-STATE.md` still calls 151 vs 2 680 a 17.8× discrepancy, so the front door can recreate the mistake. | **ACCEPTED AND FIXED — and the objector was right about the mechanism, not just the symptom.** `LIVE-STATE.md` is a **generated view**; the error lives in the hand-authored `state/live-state.json` `next_authorized_action`, and the generator prints that regeneration *"does NOT revalidate `Declared state`, which is authored prose the generator carries forward."* Regenerating alone would have preserved it. | `state/live-state.json` corrected → view regenerated; `CATALOG.md:87` and `PLAN-…-mii-staged.md:165` withdrawn |

**One objection is only partly accepted, and the difference is now measured rather than argued.**
The peer's decision procedure — *"first decide the publication scope"* — is right, but it treats the
scope of the **paper** as an open decision. **It is not: it is already the state at HEAD**, and §0
falsifier (c) now carries the build-graph measurement (`sec_systematics.tex` is reachable from
`main_note.tex` only; `paper_body.tex` has zero `\input` and zero 5D magnitudes). **What that
measurement also surfaced is `PR-X3`** — the paper *does* publish an **ML training-seed-variation**
covariance for the finalized **2D** result, and **cause 3's scope over the 2D artifact has never been
written down by anyone.** That, not the 5D magnitudes, is the live scope question.

**Nothing in this amendment authorizes, adopts or lifts anything.** The `NOT CITABLE FOR` block above
applies unchanged.

---

Every decision-bearing field below was re-measured from source. Where a figure could not be measured
from this host the item says so and its basis reads **UNMEASURED** or **RELAYED**.

**Method rules honoured, stated so they can be checked:** `/usr/bin/grep` throughout (the shell's
`grep` is a ugrep wrapper that mis-detects logs as binary); no `$?` read after a pipe; every null
search reports its exact pattern set and paths; narrow `sacct` windows only; no Slurm job submitted;
no `*combined_bkgaware.root` opened, moved or deleted; read-only on code, note and covariance.

---

## 0. THE TWO QUESTIONS THAT DECIDE WHETHER A WHOLE BRANCH EXISTS

### Q1 — Is the `M(ii)` member family on the publication critical path?

**YES. It is on the critical path — but by a route the runbook never names, and one member is the
only thing authorized.**

**The runbook null is real and it is not the answer.** Search set, run on
`docs/PUBLICATION_COMPLETION_RUNBOOK.md` with `/usr/bin/grep -ciF`:

| pattern | hits |
|---|---|
| `M(ii)` | 0 |
| `member scan` | 0 |
| `member_k` | 0 |
| `seed scan` | 0 |
| `seedscan` | 0 |
| `50 member` | 0 |
| `cause 3` | 0 |
| `estimator seed` | 1 (`:110`, P3F-scalar manifest contents) |
| `quarantine` | 1 (`:102`, purity FPS controls) |

So the runbook genuinely does not route the member family. **That is a fact about the runbook, not
about publication.** The link runs through a *different* governing document.

**The chain, each link measured:**

1. **The binding publication gate is the 2026-07-12 quarantine, and it is named as such —
   in `docs/INTEGRATION_CHECKLIST.md`, not in the runbook.**
   `docs/INTEGRATION_CHECKLIST.md:55-64`, under "Claims GATED on unfinished computation":
   > "**THE BINDING GATE, and it was absent from this list until 2026-08-11: the 2026-07-12
   > uncertainty-remediation quarantine** … seven construction causes, of which **zero are
   > discharged for the 5D GBDT covariance** … It gates the four `\gbdtFive*` macros … **and every
   > covariance-dependent claim in the note.**"
   `docs/orchestration/CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md §4.6` records that this row
   was once proposed for striking as stale and that striking it "would have removed a live
   publication gate."

2. **Cause 3 is one of the seven, and it is OPEN for the artifact publication needs.**
   `VALIDATION_LEDGER.md:729` (`VL64`): *"3 | varying estimator seeds | **OPEN** for the same
   artifact"* — the artifact being the adopted 5D GBDT covariance on 10,694 reported bins.

3. **Discharge is four legs (C code, P provenance, M magnitude, T test) and all four must hold.**
   `CRITERIA-20260811 §0`. Cause 3's `M` splits into `M(i)` the fixed-seed null (measured) and
   `M(ii)` *"the magnitude of what varying seeds would have contributed"*, which §2 itself calls
   *"what the criterion is about"*.

4. **`M(ii)` is OPEN in both columns and its only proposed substitute was disqualified on footing.**
   `docs/orchestration/SCOREBOARD-20260817-quarantine-seven-causes.md` board row 3:
   `M | OPEN and NOT CURRENTLY MEASURABLE | OPEN, same`. The candidate substitute `\gbdtAiEstTrace`
   (12 seeds, 2026-07-14) was ruled *not the same quantity* — pre-J28, one fixed data/MC draw, no
   flux universes — and the ledger already holds it *"an auxiliary robustness check and is not part
   of this candidate budget"*, **at `VALIDATION_LEDGER.md:1088`, not the `:347-348` that
   `CRITERIA-20260811 §2` cites.** The ledger is append-only, so every line-number citation into it
   decays by construction; `:347-348` today holds an unrelated retraction about arm stability. Cite
   the sentence, or the nearest immutable VL id, never the line.

5. **Joseph selected it, today.** `docs/orchestration/DECISION-20260822-joseph-b1-lift-and-clause-c.md`
   ruling 12, verbatim: *"The scientific target is option (a), the M(ii) member scan—not stamped
   re-adoption of the archive products."*

**What this does NOT mean, stated in the negative because "on the critical path" reads as broader
than it is:**

- The **family** (50 members, ~2,680 A100-h, 2.17 TiB) is **NOT authorized**. Ruling 12 excludes it
  by name. Only **one member, k=0**, is conditionally authorized, and not yet operative.
- Running `M(ii)` **does not discharge cause 3**. The authorization says so itself
  (`evidence/prepublication-2026-08-20-0b329e8a:docs/orchestration/AUTHORIZATION-20260818-mii-seed-scan-and-cause6-rebuild.md`):
  *"It buys the magnitude recorded UNRESOLVED. It does not discharge the leg … **measured is not
  acceptable**. This authorization funds an operand, not a conclusion."*
- The k=0 execution-integrity work is **both** infrastructure hardening **and** the first step of a
  publication step. It is not one or the other.

**What would falsify Q1's YES.** Any one of these, and the branch collapses:
(a) a ruling declaring cause 3 `N/A` for the adopted artifact **on the merits — and note the cause-5
precedent's REASONING RUNS AGAINST THIS, not for it** (peer review, 2026-08-22, and this lane
accepts it). `VL66` declared cause 5 `N/A` for `X` on 2026-08-17 by a **construction-path trace
showing ABSENCE of an input route** — *"the recoil-PET budget is a DOWNSTREAM CONSUMER of the shared
bkgaware bank rather than an input to it"*, recoil being *"a different estimator"*
(`SCOREBOARD-20260817-quarantine-seven-causes.md:670-676`). **Cause 3 is estimator-seed variation in
`X`'s OWN estimator** (`lgbm` on every leg), so the same trace runs the *other* way: the thing cause
3 concerns **is** an input to `X`'s construction. What `VL66` establishes is that the *route* exists
for a per-(cause × artifact) `N/A` ruling — **it supplies no argument that cause 3 is such a case,
and "nothing enforces the gate in code" is an ENFORCEMENT DEFECT, not evidence the cause is
inapplicable.** Anyone reaching for (a) must produce a fresh construction-path argument;
(b) a ruling that `M(ii)` may be discharged `UNRESOLVED-BY-DECISION` rather than measured;
(c) publication choosing to quote no 5D covariance magnitude at all — **and this is now MEASURED
against the build graph rather than assumed** (2026-08-22, added on peer review). Three builds exist:
`main_note.tex`, `main_paper.tex`, `main_primer.tex`. **`sec_systematics.tex` is `\input` by
`main_note.tex` ONLY** (`grep -rln sec_systematics *.tex` → one file), and **`paper_body.tex`
contains no `\input` at all**, so the four `\gbdtFive*` magnitudes are **unreachable from the paper
build** — they are defined in `values.tex:112-115` and used only at `sec_systematics.tex:165,167,168,170`,
each already wrapped in `\dead{}`. Confirming counts on `paper_body.tex`: `gbdtFive` **0**, `sqrt`
**0**, `e-38` **0**. **The external paper therefore already quotes NO 5D covariance magnitude**, and
at `paper_body.tex:200-203` it says so in its own voice — the corrected 5D joint throws are described
as built *"with … a fixed estimator seed"* and *"Those uncertainty products remain candidates until
the selection-complete lateral replacement lands."* **So for the PAPER, falsifier (c) is not a
decision to be taken — it is already the state at HEAD.**
  **SCOPE THIS CLAIM TO WHAT WAS SEARCHED, because the temptation to over-read it is the whole
  point of this row.** It says the paper quotes no 5D covariance *magnitude*. It does **not** say the
  paper is free of covariance-dependent claims: `grep -ciE covarian paper_body.tex` → **12**, `GBDT`
  → **5**. What remains genuinely open is therefore **(i) the NOTE**, where `sec_systematics.tex`
  still *discusses* the four magnitudes as struck text rather than removing them, and **(ii) a
  question nobody has written down — see `PR-X3`.**
(d) a smaller-than-50 grid being ruled sufficient.

### Q2 — Is the P3S lateral replacement done?

**PARTIALLY. The physics is BUILT and PASSED validation; the packet the runbook defines as its
output — "a *committed* standard lateral-component packet" — does not exist, and the adoption step
has never run.**

**Built and validated (2026-08-16, Slurm `57128458`, under the repair-11 PASS token):**
`nd-unfolding/active_universe_5d/standard/P4_STANDARD_STATUS.md:3-15` and
`docs/orchestration/state/RECEIPT-20260816-p4-standard-stages456.json`:
`stage4_components.candidate_sha256 = 950f8cb15c5a0bd785d65e7f85f4cb40fa86e27383973f82ef15c7ef525c1263`;
`stage5_validation.result = PASS`, 11 gates, `support_ratio = 1.0`, including
`band_set_completeness_vs_support_family`; `stage6_projection.n_effective_4d = 4825`,
`projection_identity_relerr = 3.76e-16`. The five replaced bands are `BeamAngleX`, `BeamAngleY`,
`MuonResolution`, `Muon_Energy_MINERvA`, `Muon_Energy_MINOS`.

**Not done:**

```
$ git ls-files nd-unfolding/active_universe_5d/standard/
nd-unfolding/active_universe_5d/standard/P4_STANDARD_STATUS.md
nd-unfolding/active_universe_5d/standard/evidence/p4_endpoint_evidence.json
nd-unfolding/active_universe_5d/standard/evidence/p4_merged_audit.json
nd-unfolding/active_universe_5d/standard/evidence/p4_standard_manifest.json
```
Four files, all documentation/evidence — and the three committed evidence JSONs are **stale against
the cluster copies the Aug-16 run wrote** (local `8ca55e46…`/`cd092d23…`/`98e8454c…` vs cluster
`71aace38…`/`1317d0d3…`/`2e3fac26…`). The FPS analogue, which *is* a completed packet of this kind,
carries 21 tracked files including three `receipt_*.json`. `p4_adopt_standard.py` has never run and
`p4_lib.py:659` records it is *"on no surface"*.

**Two canonical rows are STALE and must not be requoted:**
- `VALIDATION_LEDGER.md:733` (`VL68`): *"whose **P4-5D lateral has not been built**"* — **false since
  2026-08-16**. Its own citation `docs/OPEN_ITEMS.md:92-101` has also decayed (those lines now hold
  `OI-71`…`OI-5`).
- `docs/orchestration/RUNBOOK-20260807-gbdt-closeout.md:38`, row *"Standard (5D) lateral component —
  **NOT BUILT, AND NOT ONE RUN AWAY**"* — same. Its `find … *activelat*` test was namespace-specific;
  the standard product is `hCov_active5d_*` inside `std_final5_candidate.root`, invisible to it.

**The physics, worth one line because it changes how urgent the ordering is:** the standard lateral
replacement moves the lateral block by **−0.03%** (`sqrt_tr_active 1.4742855e-38` vs
`sqrt_tr_support 1.4747098e-38`, ratio `0.99971`, from the Aug-16 validation JSON) — not the FPS
analogue's `+10.96%`.

**What would falsify Q2.** Everything decisive is on purgeable `/pscratch` at 79.9% of 20 TiB: the
120 event-loop ROOTs, the ten 74.8 GB merged omnifiles, the ten unfolds, and the 42.3 GB candidate.
A purge destroys the "built" half without touching a single document. Also: the candidate digest is
**not reproducible** — a rebuild of identical content gave `950f8cb1…` where the Aug-9 product was
`602bbcf2…`, so re-measure `sha256`, never carry it forward.

---
## 1. THE CRITICAL PATH, AS ONE ORDERED CHAIN

Read this as the spine. Everything in §4 hangs off it; everything in §6 runs beside it.

```
[A] Gate-1 round-4 repairs        F-1(a) F-2(a) F-7(a) F-8(a) F-17(a)   (bench + 1 cluster read)
      |                            grading lane != builder != rubric author (ruling 23, §7.0.10)
      v
[B] GATE 1 PASS                    18 pre-submission halves, no partial credit
      |
      v
[C] k=0 rehearsal, legs 1-5        seven sbatch jobs, MNV_EST_SEED_OFFSET=0, ~53.6 A100-h/47.1 CPU-h/47.7 GB
      |                            (regenerate replica ids 1-3 first; the six stale files are quarantined)
      v
[D] stage-1 gate on the k=0 member [b2] VERDICT: PASS, coverage 114361636 = 10694^2
      |
      v
[E] pause-branch removal in code   sbatch_finalize_5d_bkgaware_gpu.sh  mr_declared early-exit
      |                            + a FRESH NON-BUILDER review OF THAT REMOVAL (ruling 13)
      v
[F] leg 6 (fin5dBKG) -> MVFINAL_j  the two adopted roots; MVFINAL_j has no implementation today
      |
      v
[G] GATE 2                         post-rehearsal (b) halves + F-1(b) manifest digest at both ends
      |                            + F-17(b) M-1..M-6 re-measured after the path ran
      v
[H] JOSEPH: authorize the family?  the 151-vs-2,680 A100-h discrepancy is settled by [C]'s receipt;
      |                            2.17 TiB puts pscratch at 90.8% > the ~90% abort threshold;
      |                            MVFINAL_j must exist first or the intermediates cannot be released
      v
[I] M(ii) family, n=50, k_j=1200j  j=0 is the anchor; j=1..49 clean
      |
      v
[J] cause-3 discharge JUDGEMENT    "measured is not acceptable" - Joseph, not a lane
      |
      +----> runs BESIDE [A]..[J], not after:
      |      [P] P3S packet: commit the standard lateral evidence + resolve OI-75 + wire the adopter
      |
      v
[K] P4-5D ADOPTION PACKET          six requirements, runbook :160-175
      |
      v
[L] P4-4D                          BY DECISION = the exact 5D->4D marginal; independent 4D = cross-check
      |                            (stage 6 already produced a projection candidate, n=4825)
      v
[M] P6 projections + significances  rebuild 2D/3D/4D/(Eavail,W) marginals; recompute generator comparisons
      |
      v
[N] P7 note / primer / paper       un-strike the four \dead{} 5D magnitudes; all three PDFs clean
      |
      v
[O] INDEPENDENT FINAL AUDIT        six bullets, runbook tail
      |
      v
[P] COLLABORATION REVIEW           OI-29 endorsement; blinded/full-author review
      |
      v
[Q] RELEASE TAG                    immutable publication-results tree
```

**The single most important structural fact about this chain:** steps [A] through [J] are the
*quarantine-discharge* branch and steps [P], [K] onward are the *packet* branch. **The runbook
describes only the second.** A reader who plans from `PUBLICATION_COMPLETION_RUNBOOK.md` alone will
not see [A]-[J] at all, and a reader who plans from the Gate-1/k=0 documents alone will not see [P].
Both branches must land before [K].

---
## 2. JOSEPH DECISIONS — his alone, nobody else can supply them

Ordered by how much they unblock. **Three of these are cheap to answer and unblock the most.**

### PR-J1 — authorize the k=0 one-member run, once Gate 1 passes
- **What is being asked.** Submit seven jobs for `MNV_EST_SEED_OFFSET=0`: 53.6 A100-h, 47.1 CPU-h,
  47.7 GB. It is a **production submission, not a stub test** (ruling 14).
- **Already conditionally granted, and not yet operative.** The grant becomes operative *without a
  further permission round* on a fresh non-builder's clean PASS
  (`PLAN-20260822-oneMember-mii-staged.md`, amendment 2 tail). Gate 1 does not pass, so it is not
  operative. **Storage is not the obstacle here:** `15.98844 + 0.0434 = 16.03185 TiB = 80.16%`.
- **Actor.** Joseph, but only after PR-01..PR-05. **Path.** CRITICAL.

### PR-J2 — `OI-75`: was the 2026-08-08 standard-P4 stage-3 run authorized?
- **What is being asked.** A stage-3 run exists on the cluster that this repo had no record of — ten
  ROOTs and ten `.done` receipts dated 2026-08-08, `mode=produced`, `bkg_mode=purity`,
  `code_rev=42268b6d…`, holder allocation `56495756` — against a standing hold whose scope was
  *"code/tests/receipts only — **no cluster P4 run**"*.
- **Why it is on the critical path.** Item (1) is Joseph's and **blocks item (2)**, which is whether
  those products may land. Those products are the input to the P3S packet (PR-06), which is the input
  to P4-5D. Nothing downstream can be committed cleanly while the authorization question is open.
- **Two things the row insists on.** *"A correct receipt attests to provenance, never to
  authorization."* And: **do not commit the ROOTs on storage grounds alone** — but note scratch is
  purgeable, so the window on item (2) is not open indefinitely (4.8 MB, regenerable in ~2 h 40 m CPU).
- **Expires.** A `/pscratch` purge closes the option without closing the question.
- **Path.** CRITICAL.

### PR-J3 — authorize (or resize) the M(ii) family: **46 members clear the operational line, 50 do not**

> **FRAMING CORRECTION (peer review, 2026-08-22, accepted).** *"Fifty do not fit"* is the wrong
> sentence and this row previously invited it. **Fifty members do not cross a PHYSICAL limit; they
> cross a lane-authored ~90% OPERATIONAL ABORT LINE on a SOFT quota.** Measured: soft **20.00 TiB**,
> hard **30.00 TiB** (`lfs quota -u josephrb /pscratch` → `21474836480 / 32212254720` KiB). The
> projected 18.16 TiB is **60.6% of the hard limit** and would not be blocked by the filesystem.
> The ~90% line is **unsourced, single-lane, same-day, and enforced by nothing in code** (evidenced
> in the bullets below). It remains a **serious operational warning** — Lustre performance and purge
> exposure degrade well before a hard limit, and nothing reserves the headroom — but the decision
> Joseph is being asked for is a **policy** one, not an acknowledgement of impossibility.
- **What is being asked.** 50 members at 2.17 TiB do **not** fit. Measured live
  **2026-08-22T20:56:31Z** (this is the freshest number in this document and it expires fastest):
  ```
  $ ssh saul.nersc.gov 'myquota'
    pscratch  15.99TiB / 20.00TiB  79.9%      (exit 0)
  $ ssh saul.nersc.gov 'lfs quota -u josephrb /pscratch'
    17167454504 KiB used / 21474836480 soft / 32212254720 hard
  ```
  Unrounded `15.98844 / 20.00000 = 79.9422%`. Family projection re-derived from its operands:
  `9.8+2.4+27.0+2677.0+891.7+892.1+41437.0+1784.0 = 47,721.0 MB/member`; `×50 = 2.17010 TiB`;
  `15.98844 + 2.17010 = 18.15854 = **90.7927%**` — **over the ~90% abort line.** If the `du -sh`
  rows were binary the family is 2.27551 TiB → **91.32%**, so 90.8% is the *low* reading and both
  abort.
- **Stated as a sizing instruction rather than a percentage.** 90% line = 18.00 TiB; headroom
  **2.01156 TiB**; shortfall **174.3 GB**. `2.01156 TiB ÷ 47.721 GB = 46.35` → **46 members fit, 50
  do not.**
- **Both escape routes are closed, measured.** (i) *Archive to HPSS as members complete:*
  `hpssquota -u josephrb` (20:59:33Z, exit 0) → `300.20 GiB / 512.00 GiB = 58.6%`, headroom
  **211.80 GiB**, one member all-in is 44.443 GiB → **HPSS holds four more members, not fifty.**
  (ii) *Release the intermediate per member:* `MVFINAL_j` **has no producer, reader or deleter**
  (PR-G4). The mechanism does not exist.
- **The only lever that scales** is funding `MVFINAL_j`: the 41.44 GB intermediate is **86.8% of the
  per-member footprint**, and releasing it collapses the family to ~0.29 TiB. That part is
  taskable to a lane; the sizing call is not.
- **One lever exists and was already declined:** deleting the plain (non-`bkgaware`) arm frees
  0.30920 TiB → `17.84934 TiB = 89.25%`, under the line. `AUDIT-FINDINGS-20260820.md:12-14` verdicts
  it **NO / NO-FOR-NOW**. Reopening it is Joseph's.
- **The threshold itself is thin, and he should know that.** The `~90%` abort exists at
  `RUNBOOK-20260822-b1-lift-preflight.md:376` and `PLAN-20260822-oneMember-mii-staged.md:126`, both
  dated 2026-08-22, both by the same lane, and the runbook states it with **no source**. Nulls, with
  their patterns: no WARN threshold anywhere (`(8[05] ?%|warn).{0,60}(pscratch|scratch|quota)` over
  `docs/` → 0); no front-door policy (`pscratch|scratch|quota` over `AGENTS.md CLAUDE.md` → only
  "quotable"). And **nothing enforces it**: `myquota|lfs quota|SPACE_PCT|hpssquota` over `*.sh`/`*.py`
  → 4 hits, all `hpssquota`, none checking pscratch. **The abort is a human reading a table.** Also
  new and in no repo document: the 20 TiB is a **soft** quota; the hard block limit is 30.00 TiB.
- **Expires in hours, not days.** The margin is 0.159 TiB, so **163 GiB** of unrelated scratch churn
  flips the "46 members" answer. Re-run `myquota` immediately before sizing and do not inherit 15.99.
- **Path.** CRITICAL.

### PR-J4 — **THE 17.8× DISCREPANCY IS NOT A DISCREPANCY, and he should be told before it is used**
- **This corrects the framing this document was commissioned with, and it is the single most
  load-bearing correction here.** `151 A100-h` and `2,680 A100-h` are **two right measurements of
  different populations**:

  | figure | what it counts | per unit | where |
  |---|---|---|---|
  | **151.175 A100-h** | **50 Gate-5 PET `C_stat` TRAINING REPLICAS** (array `56857233`; one leg, one product) | 3.0235 A100-h/replica | on `main`, `docs/OPEN_ITEMS.md` `OI-60` |
  | **1,961.2 GPU-h** | **50 M(ii) MEMBERS** at 08-18 leg prices | 39.223 A100-h/member | on `main`, `DETERMINATION-20260818-lanec-anchor-recompute-and-lateral-in-g1.md` §0 |
  | **2,680 A100-h** | **50 M(ii) MEMBERS** at 08-22 leg prices | 53.6 A100-h/member | on `main`, `PLAN-20260822-oneMember-mii-staged.md` §6 |
  | ~~2,850~~ | **does not exist** — the filename slug for a retracted `28.50` | — | — |

- **The tell that they are different populations.** `2680 / 151.175 = 17.728` and
  `53.6 / 3.0235 = 17.728` — **identical, because the 50 cancels on both sides.** A genuine
  population-size mismatch would leave a residue. It does not. The mismatch is in what one unit of
  work *is*: a full six-leg 5D member versus a single-leg PET training replica.
- **The real in-family gap is 1.37×, and it is one leg.** `2,680 − 1,961.2 = 718.8` against
  `(14.0 − 0.1458) × 50 = 692.7` — leg 1 re-priced. PLAN §1 defends the new price with nine
  `COMPLETED` tasks from the 08-18 member run (`57252337–9`, 8:17–8:51). The 08-18 leg price of
  `0.1458` is ~18× below even the July archive mean, so **the old operand looks like the defective
  one** — a hypothesis, and the k=0 run settles it.
- **All three re-derive.** `50 × 3.0235 = 151.175` ✓. `14.000 + 14.240 + 23.942 + 1.500 = 53.57 ≈
  53.6`, `× 50 = 2680` ✓. `39.078 + 0.1458 = 39.2238`, `× 50 = 1961.15` ✓.
- **Why the wrong prior was reached for, which is the fixable part.**
  `/usr/bin/grep -cE "1,?961|39\.223" docs/orchestration/PLAN-20260822-oneMember-mii-staged.md` → **0**.
  `DETERMINATION-20260818…` is on `main` and carries `1,961` four times but has **no CATALOG row**, so
  the router cannot reach it; the ruling carrying the `39.223` headline was retired from `main` on
  2026-08-20. The mislabel first appears at `RULING-20260819-lanec-issue54-frozen-deployment.md:207`
  — *"the 151 A100-h M(ii) family"* — in a ruling whose subject is the **data-only `C_stat` smoke**,
  and propagates to `CATALOG.md:79` and `PLAN-20260822:165`.
- **Ruling 12 is not the source of the error** — it lists *"the 151 A100-hour family, `C_ML`
  production, or a full member scan"* as **three separate** unauthorized items.
- **Method note for anyone re-checking:** `2,?680` is the wrong pattern; the on-`main` sites write
  `2 680` with a narrow space. Use `2[^0-9]?680`.
- **Actor.** Joseph needs **no decision** here — he needs to be *told*, before the 17.8× is used to
  argue for or against the one-member run. The repair is lane work: PLAN §6 should compare against
  1,961.2 and attribute the delta to leg 1; CATALOG needs a row for `DETERMINATION-20260818` and a
  fix at `:79`.
- **Path.** CRITICAL as an input to PR-J3; zero cost.

### PR-J5 — F-2(a): can a file sourced BEFORE the preflight be bound at all?
- **What is being asked.** At 15 of 16 sites `setup_salloc_env.sh` and `lib/resume_guard.sh` execute
  before the parity check runs. Either a `--pair` entry is accepted as binding-after-the-fact, or the
  `source` lines must move ahead of the preflight — which changes eight launchers identically.
- **Actor.** Joseph. **Blocks.** PR-02, therefore Gate 1. **Path.** CRITICAL, and cheap.

### PR-J6 — the cause-3 discharge judgement (see PR-G7)
- **Not reachable yet**, but flagged here so it is not discovered late: **a measured M(ii) magnitude
  does not discharge cause 3.** *"Measured is not acceptable"* — the same class of judgement as the
  endpoint census.

### PR-J7 — `OI-29`: the collaboration endorsement (see PR-G13)
- **Long external latency; start it now.** One plain question closes it.

### PR-J8 — `OI-31`: the 1.17 reconstructed-`E_avail` scale
- Confirm a rationale and a covering systematic, **or** authorize and quantify a sensitivity study.
  The row's own words: *"publication requires confirmation or a quantified assumption."*

### PR-J9 — `OI-71`, `OI-131(a)`, `OI-13`, `OI-63`, and the three live `\gk{}` items
- Standing, unanswered, and each is his: `OI-71` (may recovery evidence be quoted without a
  measurement at the promoted configuration); `OI-131(a)` (does an irreplaceable subset of the
  CFS-only P3F objects warrant a second copy); `OI-13` (re-issue Gate 4 against the adopted
  criterion — **PET, so off the path**); `OI-63` (two `\gk{}` note-organisation items, deferred by
  him until the publication reorganisation); and the third live `\gk{}` at `sec_results.tex:5`.

### PR-J10 — `OI-148` residual: renumber the `OI-*` ids, or waive the check
- `docs/open-items/verify_open_items_restructure.py` exits 1 on an assertion demanding contiguous
  `OI-1..OI-113`. The script's own comment at `:212-215` calls that *"unsatisfiable without
  renumbering ids cited in pushed commits."* It is invoked from nowhere, so it gates nothing today —
  which is exactly why it will still be red at release time.

### PR-J11 — NOT A DECISION ANY MORE: `OI-137` was RULED, and the row still says otherwise
- **`OI-137`'s apply-or-disclose call is CLOSED.** `DECISION-20260822-joseph-b1-lift-and-clause-c.md`
  **ruling 11**, commit `0309204a`, **2026-08-22 01:14:09 −0500**, verbatim: *"I accept the
  recommendation to disclose and not correct. Apply no blanket Hartlap factor to the summed
  covariance and make no covariance change."* The recommendation it accepts is filed at
  `docs/orchestration/BRIEF-20260822-oi137-finite-N-precision-bias-exposure.md` §8, landed
  `0aa13221`/`409fc245`/`5889b257`, all ancestors of HEAD.
- **The row is STALE by 45 minutes and has been edited twice since without being fixed.**
  `docs/OPEN_ITEMS.md:190` still reads *"The apply-or-disclose call remains Joseph's."*
  ```
  $ git log -S "The apply-or-disclose call remains Joseph" --format='%H %ai %s' -- docs/OPEN_ITEMS.md
  41053bc3 2026-08-22 00:29:19 -0500  OI-137: point at the fuller record...
  ```
  Written 00:29:19; ruling 11 landed 01:14:09; the row was edited again at 10:02:46 (`ae085a79`) and
  the sentence survived. **A reader of that row today is told a decision is pending that was made.**
- **What genuinely remains for him, and it is small:** (i) the `6.5` vs his `~6.4` trace ratio — the
  ruling-11 amendment says *"the deviation is deliberate and is flagged for him to overrule"*;
  (ii) the variance-scale wording at `app_statmethods.tex:899`; (iii) the **new** mixed-normalization
  defect in PR-J12.
- **A FIFTH backwards record, named in no enumeration.** The "bias direction backwards in four
  records" claim verifies — and undercounts. Covering search
  `/usr/bin/grep -rn -I -E "flatter(s|ing)|too SMALL" --include='*.md' --include='*.json' --include='*.tex' --include='*.py' --include='*.sh' .`
  excluding `.claude/worktrees`:
  1. `docs/OPEN_ITEMS.md:166` (`OI-93`) — **corrected in place**, wrong sentence retained under an
     explicit *"THE SENTENCE IMMEDIATELY ABOVE IS BACKWARDS"* annotation (`8a8d3926`);
  2. `docs/OPEN_ITEMS.md:190` — still present, corrected by its own state cell;
  3. `nd-unfolding/pet/gate5_cstat_contract.json:298` — **still wrong, deliberately** (ruling 9 pins it);
  4. `docs/orchestration/state/gate5-cstat-spec-measurements-20260814.json:258` — same;
  5. **`docs/orchestration/SPEC-20260814-gate5-cstat-construction-v1.md:669`** — *"the bias makes χ²
     too small, i.e. it flatters the fit"* — **still wrong and in NO enumeration.** The erratum
     (`nd-unfolding/PET_UQ_REMEDIATION_STATUS.md:579-596`) cites only the two JSONs, and
     `/usr/bin/grep -n -i -E "erratum|inflat|overstat|opposite way|backwards"` over that SPEC returns
     three hits, **all about centring, none about the bias direction.** `OI-93`'s own evidence column
     points a reader at that SPEC.
  The note itself is right: `app_statmethods.tex:667-670` — *"a χ² evaluated on a fixed residual is
  inflated, not flattered."*
- **And the covering-search harness has re-contaminated itself, a third time.**
  `bash docs/orchestration/state/oi137-covering-search-20260822.sh` → `kaufman hits=2 |
  sellentin/heavens hits=2 | percival hits=2 | wishart hits=2`, where its own comment asserts *"The
  true count for all six is 0."* All eight hits are term-list mentions inside two **new** documents
  about a sibling search; its `SELF_REFERENCE_SET` at `:43-44` has two members and does not cover
  them. **The world is unchanged; the instrument now reports false positives.**
- **Actor.** A records lane for four cheap edits (retire the stale sentence; add `SPEC:669` to the
  erratum's enumeration; extend the harness's self-reference set; carry the 6.5-vs-6.4 flag).
  **Path.** PARALLEL — nothing runnable is blocked.

### PR-J12 — declaration (v): the 5D blocks MIX normalization conventions
- **Declaration (v) landed 2026-08-21**, `docs/analysis-note/app_statmethods.tex:645-657`, commit
  `4fb0e3d4` (author-date 2026-08-21 12:52:15 −0500), byte-unchanged since.
- **The "no ensemble-size key on any artifact" claim is CONFIRMED, and the dynamic-key trap was
  checked rather than assumed.** The writer `nd-unfolding/combine_cov_nd.py` is 27 lines and its only
  emission is `hh.Write()` at `:26` — no `np.savez`, no `json.dump`, no `TParameter`, no `TNamed`.
  An 18-spelling sweep (`n_ensemble`, `N_ens`, `ensemble_size`, `n_members`, `n_replicas`, `n_boot`,
  `n_throws`, `TParameter`, …) finds nothing. Read on the cluster:
  ```
  $ ssh saul.nersc.gov 'sha256sum nd-unfolding/uq_cov_{stat,mlsplit}_5d.root'
  6580016f…  uq_cov_stat_5d.root      27b2e456…  uq_cov_mlsplit_5d.root
      (both match the committed REFERENCE_real_manifest.json bindings)
  GetListOfKeys(): NKEYS 1 each -- 'hCov_stat5d_reported' / 'hCov_mlsplit5d_reported', TH2D
  StreamerInfo:    no TParameter at all -- the files structurally cannot hold a scalar
  GetEntries:      114361636.0 = 10694^2   <- a trap: looks like a count, is the bin count
  ```
  N=100 and N=24 exist only as `--expected-ids 1-100` / `1-24` at
  `sbatch_finalize_5d_bkgaware_gpu.sh:167,168` — enforced (`replica_manifest.py:44-48` raises on
  mismatch) but **launcher constants, not stamps.**
- **DO NOT confuse this with `VL132`.** `docs/orchestration/state/gate5-cstat-n50/GATE5_CSTAT_N50.npz`
  (`shasum -a 256` → `6c3b4e00…`, matching) **does** carry `n_members = 50` and
  `normalization = '1/(N-1)'` among 30 keys. That is the **PET Gate-5** object. A third family
  (`pet_cstat_bkgsub_5d.summary.json`) carries `n_replicas = 20`. **Three distinct object families
  share the names `C_stat`/`C_ML`** — the exact collision `OI-137` warns about.
- **NEW DEFECT, and it is what declaration (v) exists to catch.** `app_statmethods.tex:663-665`
  describes the analysis as uniformly *"biased `1/N`"*. Measured: `C_syst` is biased `1/N`
  (`analyze_universes_5d.py:220`) and the joint throws are (`uq_math.py:104`), but **`C_stat` and
  `C_ML` are unbiased `1/(N−1)`** (`combine_cov_nd.py:20`). **The 5D sum mixes conventions**, and (v)
  is the clause requiring the convention be stated per block. Numerically inert today — 1.0% at
  N=100, 4.3% at N=24, and no 5D number is quoted.
- **On the field `p` (truncation rank):** it is not merely unrecorded — **no 5D χ² exists, so no
  truncation has ever been chosen**, and (v) is satisfied for that field by saying so.
- **Actor.** (a) the analysis-note statistics lane, for the mixed-convention sentence — a real
  unclosed defect; (b) the owner of `combine_cov_nd.py`, for a two-line forward fix stamping a
  recounted `n_replicas` on **future products only** (the 2026-07-13 bytes cannot gain a key without
  a rewrite). **No cluster run. No new Joseph decision** — rulings 7/10/11 already scoped this to the
  standard-P4 lane, records-only.
- **Expires if** either root's digest changes; if any commit edits `app_statmethods.tex:645-657` (two
  lanes are editing that file concurrently); when a member run creates member-local copies under
  `nd-unfolding/mii/member_k*/`; or the moment a 5D χ² is specified, at which point `p` becomes a
  real unrecorded operand.
- **Path.** PARALLEL.

---
## 3. LANE WORK — dispatchable now, nothing else is waiting on a decision

Every item below can be started today by a lane. Each carries: what it is; MEASURED state with the
command; what it blocks and what blocks it; the actor; the expiry/falsifier; and critical vs parallel.

> **Read `PR-01`…`PR-05` against the right tree.** The Gate-1 package lives on
> `origin/build-k0-execution-integrity` @ **`48170de9`** (base `8c156a37`, 14 commits, **not merged**:
> `git merge-base --is-ancestor 48170de9 e2a4409c` → exit 1). **None of it is on `main`** —
> `git grep -l 'mnv_source_manifest.py' e2a4409c -- '*.sh'` → **0 files**, and
> `nd-unfolding/tests/test_k0_launcher_two_roots.py` does not exist in the working tree at all.
> Anything measured "on `main`" about this package is measuring the unrepaired world. **Zero repair
> commits exist for any of the five FAILs** as of `e2a4409c`.
>
> **And the executing tree is a third tree.** `k0r2/clean` on Perlmutter is at `de040d9b`; the graded
> tip is `48170de9`; they differ in exactly one file
> (`nd-unfolding/tests/test_p4_ratchet_fail_closed.py`). The evidence is about the graded bytes — the
> *declaration* that makes that statable is what `PR-01` says is missing.

### PR-01 — F-1(a): declare the submission sha, and file A-2(a)-(g) against it
- **What.** Name, in one document, the single commit the k=0 execution tree is constituted at, and
  publish the A-2 seven-check results — including the source-manifest file count and listing digest
  **of that tree**.
- **MEASURED — the sha is nowhere.** Covering search over both trees:
  `git grep -n -i -F -e 'submission sha' -e 'pinned sha' -e 'declared sha' -e 'declares the sha' 48170de9`
  → 15 lines; same at `e2a4409c` → 24 lines. **Every hit is the requirement, a reviewer recording the
  absence, or a literal placeholder** — `PLAN-20260822-oneMember-mii-staged.md:434`,
  `RUNBOOK-20260822-b1-lift-preflight.md:409` and `VERIFICATION-20260822-k0-execution-integrity.md:155`
  all read `<the approved clean tree at the declared sha>`.
- **MEASURED — three trees, three file counts, and the filed one is the oldest.**
  ```
  $ for S in a902b781 de040d9b 48170de9 e2a4409c; do
      echo "$S: $(git ls-tree -r --name-only $S | /usr/bin/grep -cE '\.(py|sh)$')"; done
  a902b781: 771   de040d9b: 773   48170de9: 773   e2a4409c: 766
  ```
  The filed value (`RECEIPT-20260822-k0-n1-and-guarded-arms.md:196-197`) is `771 tracked source files,
  listing sha256 4ab22f93…` at `a902b781` — **neither live tree**. The tree that would actually execute:
  ```
  $ ssh saul.nersc.gov 'cd /pscratch/sd/j/josephrb/k0r2/clean; git rev-parse HEAD; git status --porcelain|wc -l; stat -c %A nd-unfolding'
  de040d9b0ccd594240b0a617298c533f2f249a65
  0
  dr-xr-x---
  ```
  So the A-2 *mechanism* holds (porcelain 0, write protection live). What fails is the **declaration
  and the filing**, not the mechanism.
- **Blocks / blocked by.** Blocks F-8(a) and F-17(a) — both say "at the pinned sha" and the phrase has
  no referent. Blocks F-1(b) at Gate 2, which compares the manifest digest at both ends. Blocked by
  nothing.
- **Actor.** Builder lane, bench. One read-only `mnv_source_manifest.py` run on the chosen tree.
- **Expires / falsified by.** Any commit to `build-k0-execution-integrity` (moves the tip); any change
  to `k0r2/clean`; any `.py`/`.sh` add or delete (moves `file_count`). **This is the archetype of the
  campaign's own rule: the item is falsified by exactly the work it authorizes.**
- **Path.** CRITICAL.

### PR-02 — F-2(a): bind `setup_salloc_env.sh` and `lib/resume_guard.sh` in the `--pair` sets
- **What.** Two shell files execute on the k=0 path (they are `source`d) and no parity check binds
  them, so the eight launchers can execute unreviewed bytes.
- **MEASURED — the eight launchers are the preflight set, not the naive `--expect-root` set.**
  ```
  $ git grep -l -- '--expect-root' 48170de9 -- '*.sh'        -> 10 files
  $ git grep -l 'mnv_source_manifest.py' 48170de9 -- '*.sh'  ->  8 files
  ```
  The two extras (`nd-unfolding/pet/sbatch_gate5_data_only_{target,train}_array.sh`) pre-date this
  package and are present at `e2a4409c` too — **a different population, not a miscount.** The eight,
  all under `nd-unfolding/` on `build-k0-execution-integrity`: `sbatch_bootstrap_5d_gpu.sh`,
  `sbatch_seedscan_split_5d.sh`, `sbatch_unfold_5d_detector_bkgaware_gpu.sh`,
  `sbatch_sweep_bank_5d_run_bkgaware_gpu.sh`, `sbatch_uthrow_run_5d_fast.sh`,
  `sbatch_uthrow_block_5d.sh`, `sbatch_uthrow_combine_5d_fast.sh`,
  `sbatch_finalize_5d_bkgaware_gpu.sh`.
- **MEASURED — count 1 SATISFIED, count 2 is exactly 2.** Comment-filtered, on the eight:
  14 guarded `--expect-root` invocations + 16 preflight calls = **30 `python3` invocations**, which
  reproduces ruling 21's 14/30 boundary on a third independent measurement.
  ```
  $ /usr/bin/grep -n -- '--pair.*\(setup_salloc_env\|resume_guard\)' *.sh    # (no output, exit 1)
  ```
  Both files are `source`d in all eight and paired in none. `lib_member_resume.sh` **is** paired in
  all eight, so this is a gap in an otherwise-complete mechanism.
- **MEASURED — no test can catch it.** `nd-unfolding/tests/test_k0_launcher_two_roots.py:405`
  asserts exactly three hardcoded relative paths. **Nothing enumerates the executing `.sh` set.**
- **A refinement to the verdict's own framing, measured per site.** The verdict says both files are
  sourced at `~41-42`, before the preflight at `~93/102`, so they "cannot be retroactively bound".
  True at 15 of 16 sites — but `sbatch_unfold_5d_detector_bkgaware_gpu.sh:183` sources
  `setup_salloc_env.sh` **after** its parity block ends at `:111`, so there a `--pair` genuinely does
  bind it before execution.
- **Blocks / blocked by.** Blocks Gate 1. Also contradicts `RUNBOOK-20260822-b1-lift-preflight.md`
  §0b-0, which claims the parity call covers "the files it executes". Blocked by nothing.
- **Actor.** Builder lane (bench) **plus one Joseph decision**: whether a file sourced *before* the
  preflight can be bound at all, or whether the sourcing must move. Filed as **PR-J5** below.
- **Expires / falsified by.** A ninth launcher joining the set, or any new `source` line. Note the
  blast radius: `test_the_preflight_block_is_BYTE_IDENTICAL_across_all_eight_except_its_pair_list`
  (`:482`) hashes the preamble with `--pair` lines stripped — adding pairs is safe, adding any other
  line is not unless it lands identically in all eight.
- **Path.** CRITICAL.

### PR-03 — F-7(a): pin the §7.0.13 preflight exclusion to something
- **What.** Sixteen preflight `python3` calls are deliberately excluded from the import guard. The
  exclusion is implicit — nothing names the sixteen, and nothing fails if a seventeenth appears.
- **MEASURED — no field exists to pin into.** The pins schema is `mnv_import_set_pins/1` with
  `entrypoints{modules, declared_empty, disclosure}` (`nd-unfolding/mnv_import_set_ratchet.py:47,169,231-237`).
  ```
  $ git grep -n -iE 'excluded_call_sites|exclusion_set|preflight_exclusion|declared_exclusions|allowlist' \
      48170de9 -- 'nd-unfolding/*.py' 'nd-unfolding/*.sh' 'nd-unfolding/tests/*.py'
  -> 24 hits, ALL unrelated (seed_offset_policy.COINCIDENCE_ALLOWLIST, p4_lib allow/denylist, the
     mii_seed_offset_driver substitution fence)
  ```
- **MEASURED — the widening test does not exist.** The only `python3` regex in the launcher suite is
  `test_k0_launcher_two_roots.py:389`, `re.search(r'python3 "\$GUARD" --expect-root', l)` — it
  *selects guarded calls*, so an added `python3 whatever.py` matches nothing.
  ```
  $ git grep -n -F -e "count('python3" -e 'count("python3' -e "findall(r'python3" -e 'findall(r"python3' \
      48170de9 -- 'nd-unfolding/tests/*.py'   -> 0 lines
  ```
  No test asserts 14, 30 or 16. **A fifteenth unguarded invocation is invisible to the whole suite** —
  exactly the failure ruling 21 named.
- **Blocks / blocked by.** Blocks Gate 1; silently weakens F-3(a) and F-4(a), both of which PASS on a
  hand read with no test behind them (the verdict grades its own confidence there "Moderate").
- **Actor.** Builder lane, bench. Needs a schema field plus a **three-arm** mutation test: fires on a
  15th unguarded call, **silent on the current 14**, fires on removing a guard.
- **Expires / falsified by.** Any change in the preflight call count — `16` is a derived
  two-per-launcher figure and appears as a constant nowhere in code.
- **Path.** CRITICAL.

### PR-04 — F-8(a): produce P-5 and P-6
- **What.** Two publication artifacts. **P-6** = re-run the entrypoint-set search on `MNV_CODE_ROOT`
  at the pinned sha and publish the command with its full output. **P-5** = a blind-spot inventory
  including the subprocess enumeration, each child marked **wrapped** or **uncovered**.
- **MEASURED — neither exists anywhere on either tree.**
  ```
  $ git grep -n -F -e 'P-5' -e 'P-6' 48170de9   -> 4 lines (3 in the superseded contract copy,
                                                   1 false positive at docs/orchestration/RUNS.tsv:342)
  $ git grep -n -F -e 'P-5' -e 'P-6' e2a4409c   -> 20 lines (10 verdict, 4 verification, 4 contract,
                                                   CATALOG.md:128 "absent from the package entirely",
                                                   1 RUNS.tsv false positive)
  ```
  *(Instrument note carried from the measurement: `git grep -E '\bP-5\b'` returns 0 on a tree where
  `/usr/bin/grep -c 'P-5'` returns 3 — `git grep -E` does not honour `\b` here. Use `-F`.)*
  Partial credit that does exist: `mnv_import_set_ratchet.py`'s docstring names the four blind spots,
  and `test_mnv_guarded_run.TheSubprocessBoundaryIsNotCovered` proves the subprocess hole in both
  directions. **The enumeration over the entrypoint set was never produced.**
- **Blocks / blocked by.** Blocks Gate 1 and **is the verdict's stated reason for refusing a PASS** —
  §3 records F-8 as the one criterion absent from the builder's own gap list, the same shape as
  round 1's undisclosed P-4. Blocked by PR-01 ("at the pinned sha" has no referent).
- **Actor.** Builder lane, bench. Two greps and a table.
- **Expires / falsified by.** Any change to the launcher set or the entrypoint set. **It blocks
  nothing mechanically downstream — it is pure publication, which is precisely why it went missing
  twice.**
- **Path.** CRITICAL.

### PR-05 — F-17(a): re-measure M-1..M-6 at the pinned sha and on the canonical checkout
- **What.** Re-take the six measurements the whole review contract rests on
  (`REVIEW-CONTRACT-20260822-k0-execution-integrity.md` §1, `:40-140`), on both trees, at submission
  time, and report every difference as a finding.
- **MEASURED — open by the builder's own words** (`PLAN-20260822-oneMember-mii-staged.md:505`, branch
  copy; RECEIPT §6). Under §7.0.8 an open pre-submission half is a FAIL.
- **MEASURED — two of the six spot-checked, and they diverge in opposite directions.**
  ```
  $ ssh saul.nersc.gov 'cd /pscratch/sd/j/josephrb/MINERvA-OmniFold; git rev-parse HEAD; git status --porcelain|wc -l'
  b2d7d4ca24707344cf12f99c0aa51381b81dd445
  721
  $ git rev-list --count b2d7d4ca..e2a4409c   -> 55     # the contract recorded 36 behind
  $ git rev-list --count e2a4409c..b2d7d4ca   -> 0
  ```
  **M-4 holds** (same HEAD, same 721) but its behind-count moved 36 → 55 since the contract was
  written. **M-5 is stale in the builder's favour and must be RESTATED, not merely re-run:**
  ```
  $ /usr/bin/grep -nE '^[[:space:]]*(export[[:space:]]+)?REPO=' <the eight at 48170de9>  # no output, exit 1
  $ git show e2a4409c:nd-unfolding/sbatch_finalize_5d_bkgaware_gpu.sh | /usr/bin/grep -n 'REPO='
  15:REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
  ```
  All eight now take `MNV_CODE_ROOT`/`MNV_DATA_ROOT` with `:?` fail-closed messages on the branch.
  M-5's finding is **repaired on the branch and unrepaired on main** — which is exactly the class of
  difference F-17(a) exists to surface.
- **Blocks / blocked by.** Blocks Gate 1. Blocked by PR-01.
- **Actor.** Builder lane; **the only one of the five that needs the cluster** (read-only `ssh`, no
  Slurm job).
- **Expires / falsified by.** **Fastest-expiring item in this document.** M-2 is a name intersection
  over 717 untracked files that can change between measurement and submission; contract §H.1 says so
  explicitly.
- **Path.** CRITICAL.

### PR-06 — commit the P3S standard lateral packet
- **What.** The standard lateral component is built and validated on `/pscratch` and essentially
  nothing about it is in git. Land the packet the runbook asks for.
- **MEASURED.** `git ls-files nd-unfolding/active_universe_5d/standard/` → 4 files (one STATUS, three
  evidence JSONs). The three evidence JSONs are **stale** against the cluster copies the Aug-16 run
  wrote (`8ca55e46…`/`cd092d23…`/`98e8454c…` local vs `71aace38…`/`1317d0d3…`/`2e3fac26…` cluster).
  `find . -path ./.git -prune -o -name 'receipt_*' -print | /usr/bin/grep standard` → empty; all three
  `receipt_*` files live under `.../fps/covariance/`. `git log --all --oneline -- '*p3s_standard_manifest*'`
  → empty.
- **Blocks / blocked by.** Blocks [K] P4-5D, because the runbook's P3S output is *"a **committed**
  standard lateral-component packet"* and by `CLAUDE.md`'s own rule an uncommitted result does not
  exist. **Blocked by PR-J2 (OI-75)** for anything that would commit or rely on the 2026-08-08
  stage-3 products — that authorization question is Joseph's and unanswered.
- **Actor.** Standard-P4 lane, for the parts not gated by OI-75 (the small JSONs: 1.6 KB + 9.2 KB +
  141 KB). Do **not** commit the ROOTs on storage grounds alone — OI-75's own instruction.
- **Expires / falsified by.** `/pscratch` purge. Everything decisive is ignored (`!!`) on both
  checkouts and sits on a filesystem at 79.9% of 20 TiB. Also: the candidate sha256 is **not
  reproducible across rebuilds** — `950f8cb1…` vs the Aug-9 `602bbcf2…` for the same content.
- **Path.** CRITICAL, and it is the item most likely to be lost to a purge rather than to a decision.

---
## 4. GATED — real work, waiting on something specific

### PR-G1 — k=0 rehearsal, logical legs 1-5 (seven sbatch jobs)
- **What.** Produce one complete M(ii) member at `MNV_EST_SEED_OFFSET=0` — the anchor, the only member
  with an archive comparand. Ruling 14: **this IS the real Slurm rehearsal, a production submission,
  not a stub test.**
- **State.** CONDITIONALLY AUTHORIZED and **NOT operative.** Two independent things hold it: Gate 1
  does not pass, and the conditional authorization requires *"a fresh non-builder records a clean
  PASS on the execution-integrity corrections."*
- **Cost, measured, not estimated.** 53.6 A100-h + 47.1 CPU-h ≈ 31.4 node-h; 47.7 GB
  (pscratch 15.99 → 16.03 TiB = 80.2%). Every leg is individually under 12 h, so each falls inside
  the standing walltime grant — **but the grant is about walltime and does not authorize this scan.**
  One cost is a real null: `uthrow5d_combF` has no `COMPLETED` record in the July archive window; its
  3 h walltime request bounds it at 3 CPU-h and the real figure comes out of this run.
- **Blocked by.** PR-01..PR-05 (Gate 1). **Blocks.** Everything from [D] onward, and the settlement of
  the 151-vs-2,680 discrepancy.
- **Actor.** A cluster run, after a fresh non-builder PASS. Submission environment must name the
  **approved clean tree**, not `/pscratch/sd/j/josephrb/MINERvA-OmniFold` (721 dirty entries);
  `--allow` for the dirty canonical checkout is FORBIDDEN (amendment 2 §3).
- **Expires / falsified by.** A `/pscratch` purge of the inputs; any commit that changes an executing
  file after the digests are taken; the arrival of a 9th launcher.
- **Path.** CRITICAL.

### PR-G2 — regenerate bootstrap replica ids 1-3 under one revision
- **What.** `member_k000000/boot_nd_5d/` held 3 stale replicas from 2026-08-18 with matching `.done`
  markers; the resume guard would have SKIPPED them and `--expected-ids 1-100` would have PASSED over
  a two-revision ensemble.
- **State.** The hazard is **REMOVED** — the six files are quarantined (see PR-D3) and the directory
  now holds 0. The **regeneration** is part of PR-G1's leg 1 and has not happened.
- **Blocked by / blocks.** Same as PR-G1. **Actor.** Cluster run.
- **Expires.** N/A once leg 1 runs. **Path.** CRITICAL (inside PR-G1).

### PR-G3 — remove the finalize launcher's pause branch, then have a fresh non-builder review it
- **What.** `nd-unfolding/sbatch_finalize_5d_bkgaware_gpu.sh` — a declared member enters
  `if mr_declared; then … echo "[fin-bkg] MEMBER PAUSE (not a boundary)" … exit 0` and exits **before**
  the two adopt calls. Deleting that branch is what makes leg 6 reachable.
- **Cite the string, not the line — the line differs by revision and a relayed number was wrong.**
  Measured here:
  ```
  $ /usr/bin/grep -n 'MEMBER PAUSE' nd-unfolding/sbatch_finalize_5d_bkgaware_gpu.sh          # e2a4409c
  314:  echo "[fin-bkg] MEMBER PAUSE (not a boundary): intermediate built at ${COMB}" >&2
  $ git show origin/build-k0-execution-integrity:nd-unfolding/sbatch_finalize_5d_bkgaware_gpu.sh \
      | /usr/bin/grep -n 'MEMBER PAUSE'                                                       # 48170de9
  426:  echo "[fin-bkg] MEMBER PAUSE (not a boundary): intermediate built at ${COMB}" >&2
  ```
  One occurrence on each tree; **`:314` on `main`, `:426` on the build branch.**
- **MEASURED — still present at both shas**, one occurrence each (see the commands above). Pinned by
  `nd-unfolding/tests/test_k0_launcher_two_roots.py:323`
  `test_the_two_adopt_invocations_are_UNREACHABLE_while_the_pause_branch_stands`.
- **The authorization is partly granted and is NOT sufficient.** Ruling 3 **LIFTED** the B1 steps 4-5
  pause (clauses (a)/(b)/(c) discharged at `3cb46337`, `3cb46337`, `81905bba`) and states explicitly
  *"The launcher's own text is not edited by this and still says what it says."* Ruling 13 then
  **deferred** the branch removal *"until a member is actually runnable."*
- **"Fresh non-builder" is a PROPERTY, not a party** — defined in the launcher's own comment at
  `:398-402`: not the author of the code under review, not the author of the governing ruling. §7.0.10
  adds the Gate-1 form (not the author of the rubric being graded), which is why the round-1 reviewer
  wrote 7/7/4 and a separate lane wrote 13/5/0. A summary attesting "all controls passed" is itself a
  FAIL of F-18.
- **Blocked by.** PR-G1 validating. **Blocks.** Leg 6, `MVFINAL_j`, and therefore any release of the
  41.44 GB per-member intermediate.
- **Expires / falsified by.** A change to the launcher that moves `:368`; a reviewer who turns out to
  have authored part of the package.
- **Path.** CRITICAL.

### PR-G4 — leg 6 (`fin5dBKG`) and the production of `MVFINAL_j`
- **What.** The finalize launcher: prints `100 replicas` and `24 replicas`, reaches `[fin-bkg] done`,
  writes the two adopted roots (~892 MB each) and `MVFINAL_j`.
- **State.** BLOCKED behind PR-G3, and **`MVFINAL_j` has no implementation.** Measured independently:
  ```
  $ /usr/bin/grep -rn 'MVFINAL' . --exclude-dir=.git --exclude-dir=.claude
  -> 13 files; every occurrence in a `.py`/`.sh` is PROSE
     (nd-unfolding/sbatch_finalize_5d_bkgaware_gpu.sh:311,313,324 are comments/echoes;
      nd-unfolding/tests/test_uq_remediation.py:3993,3998 assert that prose is present)
  ```
  **Nothing writes an `MVFINAL_j`, nothing reads one, nothing deletes a member intermediate on one.**
  `DETERMINATION-20260818-lanec-anchor-recompute-and-lateral-in-g1.md` §13 rules it is a digest-bound
  RECEIPT; the ruling exists, the code does not.
- **Blocks.** The disposition of the 41.44 GB per-member intermediate — which is the prerequisite for
  the 50-member family fitting on pscratch at all.
- **Actor.** A lane must implement `MVFINAL_j`; a cluster run must produce it.
- **Expires / falsified by.** Anyone reading "deletion is gated on `MVFINAL_j`" as an active
  protection. It is **procedural only**: today the gate is satisfied vacuously because neither the
  producer nor the deleter exists.
- **Path.** CRITICAL.

### PR-G5 — Gate 2 (post-rehearsal completion)
- **What.** Every post-rehearsal `(b)` half, **plus** re-measurement of the perishable pre-submission
  halves at the far end: **F-1(b)** (porcelain zero and the manifest digest identical at both ends)
  and **F-17(b)** (M-1..M-6 again after the path has run; M-2's untracked-file inventory is the one
  that is re-tested here).
- **State.** Not graded, and **legitimately cannot be** — it needs a run that has not happened. The
  production P-4 pins are correctly Gate-2 business (ruling 22, §7.0.15); no pins file is committed on
  the branch.
- **Contract text.** *"Until Gate 2 passes, the rehearsal's products stay where they land: not
  adopted, not consumed by anything outside the seven rehearsal jobs, not quoted, and no further
  member is authorized."*
- **Path.** CRITICAL.

### PR-G6 — the M(ii) family: 49 more members
- **What.** `k_j = 1200j`, `n = 50` (BEN-462's ruled grid). Each member rebuilds the full 5D
  covariance at a different estimator-seed offset; the spread across members **is** M(ii).
- **State.** **NOT AUTHORIZED.** Ruling 12 excludes it by name. Joseph's 2026-08-18 amendment 2 did
  fund `n = 50` — *"Okay yes, because we have so many hours available, I approve all these hours"* —
  but ruling 12 (2026-08-22) supersedes for scope: *"This selects the target but does not authorize
  the 151 A100-hour family, C_ML production, or a full member scan."*
- **Two hard prerequisites, not details.** (1) `MVFINAL_j` must exist and validate, or the
  intermediates cannot be released per member. (2) The 2.17 TiB does not fit — see PR-J3.
- **Actor.** Joseph, after the k=0 receipt.
- **Expires / falsified by.** Any change to the grid; any change to the construction footing (see
  **PR-X1**, the ordering coupling nobody has recorded).
- **Path.** CRITICAL.

### PR-G7 — the cause-3 discharge judgement
- **What.** Decide whether the measured M(ii) magnitude leaves the published values standing.
- **State.** Cannot be reached until PR-G6 produces a number, and **the number does not decide it.**
  The authorization says so: *"It buys the magnitude recorded UNRESOLVED. It does not discharge the
  leg … **measured is not acceptable**. This authorization funds an operand, not a conclusion."*
- **Actor.** **Joseph.** A physics-presentation judgement of the same class as the endpoint census.
- **Path.** CRITICAL. This is the last gate on the quarantine branch.

### PR-G8 — P4-5D adoption packet
- **What.** Assemble and adopt the final scalar 5D covariance. The packet must contain, verbatim from
  `docs/PUBLICATION_COMPLETION_RUNBOOK.md:164-175`:
  1. common central, reported-bin mask/order, estimator/background fingerprint, component inventory;
  2. pre/post hashes proving no frozen component changed;
  3. exact block-sum/reconstruction checks, symmetry, PSD/eigen diagnostics, finite diagonal,
     mean-shift records;
  4. tracked product summary **plus ledger, RUN_LOG and STATUS updates in the same commit**.
  (Four bullets in the runbook; the commonly-quoted "six requirements" counts the sub-clauses of
  bullet 3 — **stated here because two right counts of different populations read as one error.**)
- **Blocked by.** PR-06 (a committed P3S packet), PR-G7 (cause 3), and the remaining open causes 1, 4,
  6 and 7 for this artifact (`VALIDATION_LEDGER.md:727-733`, `VL62`/`VL65`/`VL67`/`VL68`).
- **A code gate that IS satisfied.** `nd-unfolding/p4_adopt_standard.py:48-57` requires
  `band_set_completeness_vs_support_family` in the validation receipt; the Aug-16 receipt is the first
  ever to carry it.
- **A code gate widely believed to be firing and MEASURED ABSENT.** `p4_lib.py:665,693-701`
  `require_adoptable()` refuses `publication_gate_rejects_this=true`; on the Aug-16 candidate that key
  is **`None` on both `std_component_manifest.json` and `p4_standard_validation.json`**. So
  `RECONCILIATION-20260817-…:293-295` ("which `std_component_manifest.json` marks
  `publication_gate_rejects_this: true`") is **false of the Aug-16 candidate** — that document's own
  §6 admits it was a relay, not a measurement. **Do not requote it.**
- **Gates that DO still block adoption.** The five Gate-6 prohibitions at `19585b7`; the un-wired
  adopter (`p4_lib.py:659` — *"`p4_adopt_standard.py` is on no surface"*); `self_guards_adequate: NO`
  in the Aug-16 receipt; and the note's own prose gate at `sec_systematics.tex:178`,
  `sec_execsummary.tex:31`, `sec_summary.tex:31` (*"until the selection-complete lateral replacement
  lands"*).
- **Path.** CRITICAL.

### PR-G9 — P4-4D
- **What.** Largely settled by decision, not by work. Joseph, 2026-08-07
  (`RUNBOOK-20260807-gbdt-closeout.md` §2): *"4D: adopt the exact 5D→4D marginal and label the
  independent 4D estimator a cross-check. No separate 4D lateral work."* `p4_project_4d.py` (stage 6)
  implements it and **already produced a candidate**: `n_effective_4d = 4825`,
  `projection_identity_relerr = 3.76e-16`, `M_shape [4825, 10694]`,
  `M_content_sha256 = 2f042f76…` (`RECEIPT-20260816-p4-standard-stages456.json`).
- **Carry this cross-check forward, it is not a pass/fail and reads like one.** Marginal vs
  independent 4D: **3009 of 4825 bins differ by more than 3%**, median 4.4%, p90 20.8%, max 72.9%,
  integral ratio 1.005578.
- **Explicitly forbidden.** Do **not** rerun the corrected R1 4D throws.
- **Blocked by.** PR-G8. **Path.** CRITICAL.

### PR-G10 — P6 projections and covariance-dependent analysis
- **What.** Rebuild exact 2D, 3D, 4D, `(E_avail,W)` and declared FPS marginals with explicit
  projection matrices; validate `M C Mᵀ` against direct block sums; recompute generator comparisons
  and significances **only** from the governing adopted covariance.
- **Blocked by.** PR-G8. **Note the DAG is stale here:** `docs/RESULT_DEPENDENCY_AND_RERUN_MAP.md:52`
  still draws `APET --> PROJ`, an edge OI-126 removed on 2026-08-20. That map needs a correction pass.
- **A named open issue lands here.** `KNOWN_ISSUES` #36 (HIGH, OPEN): *"The E_avail-W covariance has
  not been rebuilt after fixing its per-universe flux normalization."* This is also quarantine cause 6
  (`VL67`, *"OPEN, and furthest — no `(E_avail,W)` product has been rebuilt at all"*).
- **Path.** CRITICAL.

---
### PR-G11 — P7: the three documents
- **What.** Update note, primer, paper, figures, tables and release manifests **only from committed
  summaries and the ledger**; build all three; run link/reference/provenance checks; complete
  blinded/full-author review; then tag.
- **MEASURED — the build works on this host, and the standing claim that it cannot is node-scoped.**
  `docs/analysis-note/build_all.sh:37` — `targets=(main_note main_primer main_paper)`, all three.
  ```
  $ cd docs/analysis-note && python3 check_dead_containment.py --self-test   -> SELF-TEST :: PASS, exit 0
  $ python3 check_dead_containment.py                                        -> RESULT :: PASS,   exit 0
      note: 31 \dead{} uses; paper 0; primer 0; note.pdf carries 18/18 struck literals (positive
      control OK); paper.pdf 0/18; primer.pdf 0/18
  $ python3 -m unittest test_build_all -v                                    -> Ran 25 tests ... OK
  ```
  **`HANDOFF-20260820-2154Z-publication-closeout.md` §2.2's "`build_all.sh` cannot exit 0 on this
  host" is TRUE OF `login19` ONLY** — its two stated causes are `python3` = 3.6.15 there and
  `pdftotext` unreachable there. Both are node facts. Corroboration of a real green run:
  `DECISION-20260822-…:303,397` records `build_all.sh` exit 0 read unpiped, 4 engine starts, 4
  `Output written on`; all three PDFs are `Aug 22 10:25`, newer than the newest `.tex` at `10:24`.
  Page counts: note 89 pp, primer 5 pp, paper 7 pp; no `LaTeX Error`/`Emergency stop`/`Fatal error`
  in any of the three logs. **That §2.2 sentence should be re-scoped; left as written it reads as a
  repo-wide blocker and is not one.**
- **MEASURED — what actually blocks the documents is the physics, not markers.**
  `/usr/bin/grep -rn -E "TODO|FIXME|XXX|\bTBD\b|PLACEHOLDER|placeholder|BLOCKER|blocker" --include='*.tex' docs/analysis-note/`
  → **1 hit, and it is the macro definition** `preamble.tex:59`. Zero `\TODO{}` usages. The real
  incompleteness is prose that is waiting on P6: `sec_systematics.tex:178-193` (all four 5D magnitudes
  struck, *"No replacement magnitude is quoted, and none is authorized"*), `:201` (4D and
  extended-fiducial have no covariances constructed with this procedure), `sec_3d.tex:219,278`,
  `sec_summary.tex:35` (*"no significance is quoted without a corrected projected covariance"*).
- **MEASURED — three live reviewer items.** `\gk{}` appears 6 times; one is the definition, three are
  answered with `\jrb{Fixed!}` (`app_statmethods.tex:14`, `sec_systematics.tex:122`, `:129`), and
  **three are live and unanswered**: `sec_experiment.tex:46`, `sec_experiment.tex:104`,
  `sec_results.tex:5`. Two of the three are structural reorganizations of the note — **Joseph's**
  (and `OI-63` defers them until the publication reorganisation).
- **MEASURED — the `\dead{}` checker has exactly one caller, and it is not a hook.**
  `/usr/bin/grep -rn "check_dead_containment" .githooks/` → no output, exit 1. Its only caller is
  `build_all.sh:110-111`. So a violating commit lands with the hook printing `12 checks passed` and
  the failure surfaces at the next build.
- **MEASURED — figures predate every August covariance correction.** 52 PDFs under
  `docs/analysis-note/figures/`; `git log -1 --format=%cd --date=iso -- docs/analysis-note/figures/`
  → **2026-07-20**. (Their mtimes are all `Jul 22 23:03` = clone time, so mtime is not evidence.)
  `make_figures.sh` hardcodes `REPO=/pscratch/…`, so regeneration is **cluster-only**.
- **MEASURED — value provenance is 0/71.** `python3 docs/orchestration/oi130_quoted_value_inventory.py`
  → exit 0, 71 macros in `values.tex` (65 note / 5 primer / 11 paper / 6 inert), and **0 of 71 name a
  backing artifact in their own trailing comment.** The tool has no recorded run in any `.md`
  (`/usr/bin/grep -rn "oi130_quoted_value_inventory" --include='*.md' .` → 0 hits). This is `OI-130`.
- **Blocked by.** PR-G10. **Blocks.** PR-G13, PR-G14.
- **Actor.** Lane for the mechanical rebuild; **Joseph** for the three `\gk{}` items and for the
  `sec_systematics.tex:169-170` sentence, which must be **deleted or rewritten, not updated**, because
  its antecedent has half-changed (`MAP-20260817-gbdt-note-section-blockers.md` §6).
- **Expires / falsified by.** Any commit touching `docs/analysis-note/*.tex` (re-run both containment
  stages and re-count `\gk{}` and the struck literals); any figure regeneration; any adoption commit.
- **Path.** CRITICAL.

### PR-G12 — the independent final audit
- **What.** Before publication synthesis an independent verifier must confirm the runbook's
  requirements. **There are SEVEN bullets, not six** — `sed -n '279,290p' docs/PUBLICATION_COMPLETION_RUNBOOK.md | /usr/bin/grep -c '^- '` → `7`.
- **MEASURED — the composite audit has never been run.**
  `/usr/bin/grep -rn -i "independent final audit|final audit|independent verifier must"` over `*.md`,
  `*.py`, `*.tsv`, `*.json` excluding `.git` and worktrees → **exactly 2 hits, both inside the runbook
  itself** (`:277`, `:279`). No receipt, state JSON or ledger row claims it was performed. The
  "publication-plan verifier" of PG0 is **an LLM session, not a script** (`RUNS.tsv` rows
  `MIG-V3`…`MIG-V3R3`, 2026-07-18) and it audited the **plan text**, not the artifacts.
- **Per-bullet instrument state.** 4 of 7 have a real instrument with a real run, and each of those
  four is qualified: (a) FPS negweight footing — PASS 2026-08-07
  (`…/fps/covariance/fps_publication_pass_receipt.json`) but **scoped to the 10 lateral endpoints
  only**; the five non-lateral checkers contain zero occurrences of `negweight|purity|bkg_mode`.
  (c) joint-vs-additive retraining — **RAN AND IS ADVERSE**: additive overstates joint by **1.786×**
  (`VALIDATION_LEDGER.md:549-570`), and its JSON operand is untracked, so the number lives only as
  prose. (f) skip/atomicity — swept **once**, 624 files, 2026-08-07, `890c086e`; not in the
  pre-commit list, so it is a snapshot not a guarantee. (g) claim-with-evidence — the hook's
  `Checks: 12 passed` trailer is present at HEAD, but **none of the 12 binds a scientific claim to
  the ledger/RUN_LOG/STATUS triple**. (b) PET — instrument exists, never run on a real nominal, and
  **is off the path anyway**. (d) 4D-not-rerun and (e) four-adoption-packets-exist have **no
  instrument at all**.
- **Actor.** A verifier lane, not the builders. Cheapest first: (d) is a re-digest against
  `docs/orchestration/state/quoted-products-digests-56760314.json` (36/36 sha256+mtime, 2026-08-12,
  never re-verified, no consumer) — no compute.
- **Expires / falsified by.** Any of those instruments landing; the `Checks: N passed` trailer
  changing.
- **Path.** CRITICAL.

### PR-G13 — collaboration review
- **What.** Endorsement for publishing the full **1431-bin** 3D+ covariance (rank 247) and its
  **rank-deficient GoF** treatment, plus blinded/full-author review.
- **MEASURED — three collaborator questions were sent; two are answered, one is not, and the
  unanswered one IS `OI-29`.** From `docs/COLLABORATOR_QUESTIONS.md` (181 lines): (1) FrInel_pi
  exclusion **CONFIRMED** 2026-08-02, *"and for a different reason than the source comment gives"* —
  a degeneracy among overlapping dials, not a broken knob; App. A item 2 closes. (2) ours-only
  truncated-spectral χ² **CONFIRMED** as practice (a citation is a follow-up ask); App. A item 4
  closes. (3) the 3D+ novelty question **STILL OPEN and narrowed** — the reply answered a different
  question, and **no view was given on publishing the full 1431-bin covariance or its rank-deficient
  GoF.** That is App. A item 5, and it is OI-29.
- **MEASURED — there is no blinded/full-author review process artifact in this repo.**
  `/usr/bin/grep -rn -iE "blinded review|full-author|author review|internal review|conveners|speakers committee" docs/ --include='*.md'`
  → **2 hits, both the runbook line and the COLLABORATOR_QUESTIONS preamble.**
- **Actor.** **Joseph.** One clarifying question closes item 5: *"would the collaboration endorse
  publishing the full 1431-bin covariance and its rank-deficient GoF?"* No lane can supply it.
- **Expires / falsified by.** A written reply from the conveners/MAT maintainers, or Joseph recording
  a verbal one.
- **Path.** CRITICAL, and it has a long external latency — **start it early; it does not depend on
  the covariance landing.**

### PR-G14 — the release tag and the release manifest
- **What.** Tag the immutable publication-results tree only after every cited artifact is reachable
  from a commit and a release manifest.
- **MEASURED — no release tag exists, and no release manifest exists.**
  ```
  $ git tag --list | wc -l   -> 10   (all under evidence/)
  ```
  All ten are evidence tags. `evidence/prepublication-2026-08-20-0b329e8a` is an **annotated tag on
  commit `0b329e8a`** whose own message says *"complete committed record before active-tree
  compaction; **not a publication-results freeze**"* — it is the permalink anchor the 08-20
  compaction's rewritten links resolve through (`OI-145`), **a discovery-route preservation tag, not
  a release tag.**
  `find . -not -path './.git/*' -not -path './.claude/worktrees/*' -iname '*release*'` → one hit, and
  it is MINERvA's published `data_release`, not ours. `/usr/bin/grep -rn -i "hepdata" docs/` → **0**.
- **A structural hazard worth naming here.** Six of the ten `evidence/*` tags on the remote are
  ABSENT from this checkout, because `remote.github.fetch` is `+refs/heads/*:refs/remotes/github/*`
  with `tagOpt` unset — git only auto-follows tags pointing at objects it is already downloading, so
  a tag on a commit unreachable from `refs/heads/*` (which is *why* it was tagged) can never arrive
  via a plain `git fetch github`. It takes
  `git fetch github 'refs/tags/evidence/*:refs/tags/evidence/*'`. **Preservation succeeded;
  discovery did not.** A release tag inherits this exposure.
- **Blocked by.** Everything. **Actor.** Joseph + a lane. **Path.** CRITICAL, last.

### PR-G15 — quarantine causes 1, 4, 6 and 7 for the adopted artifact
- **What.** Cause 3 is not alone. For the adopted 5D GBDT covariance the ledger records, at
  `VALIDATION_LEDGER.md:727-733`: `VL62` cause 1 **OPEN**; `VL63` cause 2 **DISCHARGED for the
  stamp-verified candidate only**; `VL64` cause 3 **OPEN**; `VL65` cause 4 **OPEN**; `VL66` cause 5
  **N/A for X on the merits**; `VL67` cause 6 **OPEN and furthest**; `VL68` cause 7 **discharged for
  FPS only** (266 bins ≠ 10,694).
- **Cheapest ordering, already costed** (`MAP-20260817-gbdt-note-section-blockers.md`):
  **2 → 4 → 3 → 1 → 6**, with 2 done and **four of the six remaining needing no cluster time.** One
  stamp-propagation edit closes the provenance halves of 2, 3 and 4 together. **Cause 6 is the only
  one needing compute**, and it gates both the `(E_avail,W)` rebuild and the generator ratios.
- **Do not read the tally flat.** `MAP-20260817`'s headline: *"Neither one nor six — for the artifact
  `values.tex` actually quotes it is SEVEN."* Two artifacts, two counts: the quoted July product is
  **0 of 7**, the footing-matched J28 candidate is **1 of 7**.
- **Path.** CRITICAL, and **the cheapest real progress available today** — cause 1's `M` is a static
  audit plus one per-band census, no compute, and it is entirely independent of the k=0 branch.

---
## 5. DONE — with the evidence that closed it

### PR-D1 — 2D central value and 2D standalone uncertainty
- σ_total `3.073e-38 cm²/nucleon`, 1.11% above the paper total; MAT-conformant flux-fixed 187-universe
  construction giving a **6.87%** median relative budget against the paper's 6.86%. Closure,
  completeness and iteration controls pass. Evidence: `2d-unfolding/2D_OMNIFOLD_STUDY_STATUS.md`,
  `2d-unfolding/2D_OMNIFOLD_REFERENCE.md`, `VALIDATION_LEDGER.md`.
- **Falsifier:** quoting a predecessor covariance rollup, or the paper+ours combined-covariance χ²,
  which double-counts shared systematics and is **not** the standalone validation claim.

### PR-D2 — 3D, 4D and 5D central values, anchors and closures
- All VALIDATED; their **covariances stay QUARANTINED** pending the adopted 5D trunk. Evidence:
  `3d-unfolding/3D_OMNIFOLD_STATUS.md`, `nd-unfolding/ND_OMNIFOLD_STATUS.md`, ledger.

### PR-D3 — quarantine of the six stale k=0 replicas, and its durability copy
- **Authorized, executed and durable.** `docs/orchestration/state/RECEIPT-20260822-quarantine-member-k000000-stale-replicas.json`:
  `kind = physical-file-quarantine`, `action = MOVE (same-filesystem rename). NOTHING WAS DELETED AND
  NOTHING WAS COPIED.`, `totals.file_count = 6` (3 `.npz` + 3 `.done`, `payload_bytes = 278611`,
  operands `[92696, 190, 92664, 190, 92681, 190]`), destination
  `/pscratch/sd/j/josephrb/quarantine/20260822-member-k000000-stale-replicas`, all six sha256
  **recomputed at the destination**. Ruling 16's durability copy to
  `/global/homes/j/josephrb/evidence/` is recorded in the same receipt, originals retained.
- **What it does NOT establish, in the receipt's own words:** nothing here evaluates the replicas'
  contents; they are quarantined because their **provenance** cannot be paired with the current
  revision.

### PR-D4 — the B1 steps 4-5 pause is LIFTED
- Joseph, ruling 3, 2026-08-22. Clauses (a) `OI-141` → `3cb46337`; (b) `OI-140` → `3cb46337`;
  (c) fresh non-builder on the real steps (4)/(5) path with a negative control → `81905bba`, ruled
  satisfied by ruling 1.
- **AND IT UNBLOCKS NOTHING BY ITSELF.** Both launcher routes still refuse, for unrelated reasons:
  the declared route dies at the first `mr_run` (100 bootstrap replicas wanted, `member_k000000` now
  holds 0 after the authorized quarantine) and again at the second (24 seedscan splits wanted,
  `seedscan_split_5d/` absent entirely) — **two independent refusals, and clearing the first does not
  clear the second**; the undeclared route exits 5 for want of a marker.

### PR-D5 — OI-147 (eight configuration keys) and OI-140/OI-141
- `OI-147` **COMPLETE 2026-08-21**: seven keys at `aa989794`, the eighth (`hDiagCombinedOld`, via the
  raw diagonal) at `fdc0792a`, Joseph ruling OPTION 1 — both diagonals ship. A sweep over every
  archive-absent key on both adopted artifacts now returns none uncovered, so the stage-1 gate can
  pass a correct product for the first time. `OI-140` verification landed `3cb46337`; `OI-141` fixed
  `3cb46337`; `OI-149` fixed and landed `89e0c62f`.

### PR-D6 — the P3S standard lateral is BUILT AND VALIDATED (not committed, not adopted)
- See Q2. `RECEIPT-20260816-p4-standard-stages456.json`: stage 5 `result = PASS`, 11 gates,
  `support_ratio = 1.0`; stage 6 `n_effective_4d = 4825`, `projection_identity_relerr = 3.76e-16`.
  The lateral block moves by **−0.03%**.

### PR-D7 — the FPS five-band active lateral is ADOPTED
- 2026-08-07, job `56431823`, gate chain PASSED: lateral `7.30356e-39 → 8.10399e-39` (**+10.96%**),
  combined FPS `8.040779e-39 → 8.774217e-39` (+9.1215%), 266 reported bins.
  `VL68` discharges cause 7 **for this artifact only**. **266 ≠ 10,694 is the whole check** — this
  does not touch the 5D GBDT covariance.

### PR-D8 — PET is OFF the publication critical path
- `docs/OPEN_ITEMS.md:179`, `OI-126`, Joseph 2026-08-20, verbatim: *"No PET total covariance is
  adopted for publication. PET remains a diagnostic/method-development result and may be reconsidered
  only after estimator-equivalence and coverage evidence."*
- `docs/analysis-note/sec_summary.tex:46`: *"The whole track is diagnostic and method development: no
  PET covariance is adopted as a publication uncertainty product, and the full-event
  central/statistical pairing was declined rather than resolved."*
- **Consequences to carry, not re-litigate:** Gate 5, Gate 6, `C_stat` and `C_ML` are off the path.
  The reconsideration gate is **estimator-equivalence PLUS coverage** — a different object from
  independent verification of the construction. And one over-quoting trap: the phrase
  *"bootstrap-centering/bias"* IS Joseph's, but the row's own measurements **refute** that mechanism;
  the operative content is *a large, spatially coherent anomaly whose coverage has not been validated*.

### PR-D9 — the MANIFEST / discovery-route check is now GREEN
- This **discharges `HANDOFF-20260820-2154Z` §2.1**, which recorded `OUT OF DATE: rows=324`, 49
  excluded untracked paths, and a warning on a dirty `sessions.json`.
  ```
  $ python3 docs/orchestration/generate_manifest.py --check --committed-only   -> exit 0
    OK: docs/orchestration/MANIFEST.tsv; rows=426 ARCHIVAL=102 DEAD=1 LIVE=44 MACHINE=279
    committed-only: 0 nonignored untracked path(s) EXCLUDED
  $ python3 docs/orchestration/generate_manifest.py --check                    -> exit 0  (same 426 rows)
  ```

### PR-D10 — the twelve pre-commit gates are green at HEAD in a clean worktree
Each of the twelve `run` lines of `.githooks/pre-commit` was invoked individually and unpiped in a
clean worktree checked out at `e2a4409c`, and each returned **rc=0**: `findings_row_lint.py
--longform`; `whose_row.py` with `--check-ledger-ids`, `--check-owners`, `--self-test`,
`--check-oi-ids`; `verify_hash_bindings.py`; `verify_receipt_artifacts.py`; `live_doc_indexed.py`
with `--check` and `--self-test`; `control_plane_lint.py` with and without `--self-test`;
`generate_manifest.py --self-test`.
Recorded because a gate that fails on *your* tree and not on `main` is a known trap here: re-run in a
detached worktree before blaming `main`, and never bump a binding constant.

---
## 6. PARALLEL — real publication work that does NOT sit on the chain

Everything here can be worked today without waiting for Gate 1, the k=0 member, or the adoption.
**Two of them (PR-P1 and PR-P5) have long external latency and should be started first.**

| id | item | state, measured | actor | path |
|---|---|---|---|---|
| **PR-P1** | `OI-29` / collaborator App. A item 5 — endorse the 1431-bin covariance and rank-deficient GoF | OPEN; two of three collaborator questions answered, this one not | **Joseph** | parallel, long latency |
| **PR-P2** | `OI-31` / `KNOWN_ISSUES` #26 — the inherited **1.17** reconstructed-`E_avail` scale has recorded lineage and no justification; the row's own words: *"publication requires confirmation or a quantified assumption"* | OPEN, WAITING-USER since 2026-08-12 | **Joseph** (obtain a rationale, or authorize and quantify a sensitivity study) | parallel |
| **PR-P3** | `OI-130` — 0 of 71 `values.tex` macros name a backing artifact; `\gbdtAiEstTrace`'s evidence `uq_cov_ai1est_5d.root` is untracked | measured this turn: `oi130_quoted_value_inventory.py` exit 0, 71 macros, 0/71 | lane D (read-only audit) then a remediating lane | parallel |
| **PR-P4** | `KNOWN_ISSUES` #57 — the note describes `C_stat` as a Poisson bootstrap of the **measured leg** and a determination on `main` rules that description **wrong**; remedy is a publication-text change | OPEN, **needs its own owner** | a note lane | parallel (but it is a note correctness defect, so it must land before PR-G11 closes) |
| **PR-P5** | `OI-51` — the email to Ben Nachman accepting the HPSS increase, re-scoped 2026-08-18 | WAITING-USER; now sendable | **Joseph** (do not quote a quota percentage: `hpssquota` still reads 265.1%) | parallel |
| **PR-P6** | `OI-148` residual — `docs/open-items/verify_open_items_restructure.py` exits 1 | measured: repin PASS, conservation PASS, seven-column PASS; the residual assertion at `:245` demands contiguous `OI-1..OI-113`, which the script's own comment at `:212-215` calls *"unsatisfiable without renumbering ids cited in pushed commits"* | **Joseph** (renumber or waive); the script is invoked from nowhere, so it gates nothing today | parallel |
| **PR-P7** | `KNOWN_ISSUES` #50 — `build_all.sh` exits 0 on a **cold** tree while leaving undefined references, because `latexmk` runs once per target and the reference pass is short by one | OPEN | a note/tooling lane | parallel; it makes a green P7 build untrustworthy on a fresh clone |
| **PR-P8** | `KNOWN_ISSUES` J36 — global POT scaling discards per-playlist Data/MC ratios at **eight live sites** | HIGH, OPEN | an event-loop lane | parallel |
| **PR-P9** | `KNOWN_ISSUES` J — the 2026-07-31 four-account audit retains unresolved publication and provenance findings | HIGH, OPEN | an audit lane | parallel |
| **PR-P10** | `OI-42` — 715 untracked cluster paths counted but unclassified until after the freeze | BLOCKED, UNOWNED | a cluster-freeze owner | parallel; feeds PR-G14 |
| **PR-P11** | `OI-44` — `hsi hashverify` on all 240 archived files *"once before publication"* | trigger may be moot: the HPSS duplicates were **deleted** on the advisor's judgement after the CFS move (`AUTHORIZATION-20260818…`, `OI-131`). **UNMEASURED whether an object remains to verify.** | PET/storage owner | parallel; **verify the premise before scheduling the work** |

### Off the path, confirmed, do not work

`Gate 5`, `Gate 6`, `C_stat`, `C_ML`, `P5A`, `P5B`, `G2`, `P3F-PET`, and the whole recoil-PET legacy
boundary. All descend from PET, which `OI-126` demoted on 2026-08-20 (PR-D8). **Note that
`docs/RESULT_DEPENDENCY_AND_RERUN_MAP.md:52` still draws the edge `APET --> PROJ`** — the DAG has not
been updated for that ruling and will mislead anyone who plans from it.

---

## 7. THREE COUPLINGS THIS DOCUMENT FOUND AND NOBODY HAS RECORDED

These are **this lane's inferences from measurement, not rulings.** They are stated with their
falsifiers so they can be killed cheaply.

### PR-X1 — the M(ii) family rebuilds the very lateral bands that P3S replaces
- **Measured.** M(ii) leg 3 is `sbatch_unfold_5d_detector_bkgaware_gpu.sh`, whose header names it the
  *"KNOWN_ISSUES #13 LATERAL leg"*, driving `nd-unfolding/uq_5d/detector_universes.txt`:
  ```
  $ cat nd-unfolding/uq_5d/detector_universes.txt | wc -l   -> 18
  BeamAngleX:{0,1}  BeamAngleY:{0,1}  MinosEfficiency:{0,1}  MuonResolution:{0,1}
  Muon_Energy_MINERvA:{0,1}  Muon_Energy_MINOS:{0,1}  GEANT_{Neutron,Pion,Proton}:{0,1}
  ```
  The P3S replacement covers exactly `BeamAngleX`, `BeamAngleY`, `MuonResolution`,
  `Muon_Energy_MINERvA`, `Muon_Energy_MINOS` — **five of the nine bands leg 3 produces, in their
  support-limited form.**
- **Why it matters.** If the M(ii) family runs before the P3S lateral is adopted, it measures the
  estimator-seed sensitivity of a construction that P4-5D will then replace. This campaign has a
  standing precedent for treating that as disqualifying: `FOOTING-20260817-gbdtaiesttrace-12-seeds.md`
  rejected `\gbdtAiEstTrace` as M(ii) **on footing**, not on method.
- **Why it is probably small anyway, and this is the measured half.** The standard lateral
  replacement moves the block by **−0.03%** (`0.99971`), not FPS's `+10.96%`. So the footing argument
  that killed AI1 (pre-J28, different input, different construction) is far weaker here.
- **Covering search behind "nobody has recorded it".** Over `docs/`, `nd-unfolding/` and
  `VALIDATION_LEDGER.md`, excluding `.claude/worktrees`: files matching **both**
  `M\(ii\)|member_k|lib_member_resume` **and** `selection-complete lateral|lateral replacement|P3S`
  are `docs/OPEN_ITEMS.md`, `docs/orchestration/MANIFEST.tsv`, `docs/orchestration/RUNS.tsv`,
  `docs/orchestration/SCOREBOARD-20260817-quarantine-seven-causes.md`, `VALIDATION_LEDGER.md` — all
  five are large index/board files where the two topics co-occur by size, not by argument. **If a
  document states this coupling under other vocabulary, that search misses it.**
- **What to do.** Not a decision for this document. **Put it to Joseph together with PR-J3** — it is
  an ordering question with a cost attached, and the cheap resolution is to record the −0.03% as the
  reason the ordering does not matter, rather than to leave it unaddressed.

### PR-X2 — the M(ii) governing documents are NOT on `main`
- **Measured.** The authorization, cost derivation, spec, predeclaration, grid ruling, proposal and
  footing disqualification for M(ii) are all **absent from the working tree**:
  ```
  $ for f in AUTHORIZATION-20260818-mii-seed-scan-and-cause6-rebuild.md \
             COST-20260817-mii-seed-scan-derivation.md PROPOSAL-20260817-mii-bar-for-cause-3.md \
             FOOTING-20260817-gbdtaiesttrace-12-seeds.md RULING-20260818-lanec-mii-offset-grid-and-member-count.md \
             SPEC-20260818-mii-submission-topology.md EXTENT-20260817-2850-a100h-scope-and-missing-legs.md \
             PREDECLARATION-20260817-mii-seed-scan-cause-3.md; do
      [ -f "docs/orchestration/$f" ] && echo "PRESENT $f" || echo "ABSENT  $f"; done
  ABSENT  (all eight)
  $ git cat-file -s evidence/prepublication-2026-08-20-0b329e8a:docs/orchestration/<each>
  9947 / 14574 / 10141 / 6331 / 24439 / 8799 / 49068 / 21374   (all eight PRESENT in the tag)
  ```
- **Why it matters.** They are preserved at the frozen tag and reachable — but **six of the ten
  `evidence/*` tags are missing from a fresh checkout by construction** (see PR-G14). So the
  authorization that funds `n = 50`, the ruled grid, and the document that disqualified the cheap
  substitute are all one un-followed tag away from being invisible to a new session. This is a
  **discovery** problem, not a preservation one.
- **What to do.** A lane can add a CATALOG route to the tag paths for these eight. Cheap, no
  decision needed. (It cannot be a relative link — the files are not in the tree.)

---
### PR-X3 — the PAPER publishes a training-seed-variation covariance, and cause 3's scope over it has never been written down

**Found 2026-08-22 while measuring falsifier (c); this is a question, not a finding, and it is
stated as a question deliberately.**

`paper_body.tex:58-60` says the finalized **2D** budget *"combines systematic (MAT universe),
statistical (Poisson bootstrap) and **ML (training-seed variation)** covariances."* **Training-seed
variation is precisely cause 3's subject matter.** But the seven causes are graded per
**(cause × artifact)** and every existing cause-3 record is scoped to **`X`, the scalar-5D GBDT
covariance** — not to the 2D budget.

**Two things this is NOT, both checked, so nobody re-raises them as alarms:**
- **It is not an unbuilt-component claim.** The prohibited `do_not_construct_C_ML`
  (Gate-6 receipt, `19585b7`) is the **recoil-PET** `C_ML`. The 2D one is built and complete —
  `LIVE-STATE.md:7`, 2D COMPLETE on central value *and* uncertainty, 6.87% median relative budget
  vs paper 6.86%. **The two share a NAME and not an artifact**, which is the `OI-137` collision this
  document already flags at `PR-J12`.
- **It is not a claim that cause 3 applies to 2D.** Nobody has said it does, and this lane is not
  saying it either. **Asserting `N/A` here without an artifact-side statement would be exactly the
  error `SCOREBOARD §4` caught** — reading a true statement about one artifact as settled for another.

**Why it matters to the plan.** If cause 3 is scoped to `X` only, then falsifier (c) plus the
measured build graph means the *paper* branch is already clear and only the *note* is gated. If
cause 3 reaches any training-seed-variation covariance the collaboration publishes, then **the 2D
result is inside the quarantine and the branch does not collapse by scoping at all** — which would
be the single largest change to this document.

- **Actor.** A ruling, informed by whoever owns cause 3's scope statement. **Not this lane.**
- **Cost to answer.** One artifact-side sentence, of the same form `VL66` wrote for cause 5.
- **Path.** Decides whether `PR-G7`/`PR-J6` is note-only or paper-wide.

## 8. UNMEASURED — stated as such rather than estimated

Each of these is a field a reader will want and this document does **not** supply. Filling one in is
cheap; guessing one is the failure this campaign keeps filing.

| item | why it is unmeasured | what would measure it |
|---|---|---|
| `uthrow5d_combF`'s cost | **A real null, not a failed query** — the identical `sacct` query form returned data for the other four job names in the same July window. Bounded only by its 3 h walltime request. | the k=0 run |
| The per-member footprint (47.721 GB) | A **linear extrapolation from the archive's equivalents**, not a measured member. It is the operand under PR-J3's 90.8%. | the k=0 run |
| Whether leg 1's price is 14.0 or 0.1458 A100-h | Two measurements, 18× apart, from different runs. PLAN §1 argues for the new one; that is an argument, not a settlement. | the k=0 run |
| Whether `OI-44`'s HPSS objects still exist to hashverify | The 240 objects were verified and then the **HPSS duplicates were deleted** on the advisor's judgement. Whether anything remains for the "once before publication" check is not measured here. | one `hsi ls` |
| Whether cause 3's `M(ii)` would need re-running after the P3S lateral is adopted | **PR-X1.** This lane's inference from the leg-3 band list; no ruling exists either way. | a ruling, informed by the measured −0.03% |
| Whether the 24-vs-19 detector array count is a defect | `sbatch_unfold_5d_detector_bkgaware_gpu.sh` is `--array=0-18%8` (**19 tasks**) at HEAD, while `PLAN-20260822` amendment 1 row 3 lists **24**. Two right counts of different things, or one error — **not determined here.** | read the launcher's own expected-population assertion |
| Whether the collaboration will endorse the 1431-bin covariance | External. No lane can supply it. | `PR-J7` |
| Everything about the *content* of the quarantined k=0 replicas | The quarantine receipt says so itself: they are held on **provenance**, and *"nothing here evaluates their contents."* | out of scope |

## 9. CANONICAL RECORDS THIS DOCUMENT MEASURED AS STALE

Recorded here rather than silently worked around, because each is currently teaching a reader
something false. **None of them is repaired by this commit** — this is a read-only lane.

1. **`VALIDATION_LEDGER.md:733` (`VL68`)** — *"whose **P4-5D lateral has not been built**"*. False
   since 2026-08-16. Its own citation `docs/OPEN_ITEMS.md:92-101` has also decayed.
2. **`docs/orchestration/RUNBOOK-20260807-gbdt-closeout.md:38`** — *"Standard (5D) lateral component:
   **NOT BUILT, AND NOT ONE RUN AWAY**"*. Same cause. Its `find … *activelat*` test was
   namespace-specific and cannot see `hCov_active5d_*` inside `std_final5_candidate.root`.
3. **`docs/OPEN_ITEMS.md:190` (`OI-137`)** — *"The apply-or-disclose call remains Joseph's."*
   Superseded by ruling 11 forty-five minutes after it was written, and the row has been edited twice
   since without the sentence being fixed.
4. **`docs/orchestration/RECONCILIATION-20260817-…md:293-295`** — *"which `std_component_manifest.json`
   marks `publication_gate_rejects_this: true`"*. Measured **`None`** on both the Aug-16 component
   manifest and the validation JSON. That document's own §6 admits the claim was a relay.
5. **`HANDOFF-20260820-2154Z-publication-closeout.md` §2.2** — *"`build_all.sh` cannot exit 0 on this
   host"*. True of `login19`; false on this Mac, where the script's own contract suite is 25/25 and
   both containment stages exit 0.
6. **`HANDOFF-20260820-2154Z-publication-closeout.md` §2.1** — the MANIFEST staleness. Discharged:
   `generate_manifest.py --check` and `--check --committed-only` both exit 0 at 426 rows.
7. **`docs/RESULT_DEPENDENCY_AND_RERUN_MAP.md:52`** — still draws `APET --> PROJ`, an edge `OI-126`
   removed on 2026-08-20.
8. **`docs/orchestration/CATALOG.md:79` and `PLAN-20260822-oneMember-mii-staged.md:165`** — *"the
   151 A100-h M(ii) family"* and the `17.8×` derived from it. A category error (PR-J4) that entered
   at `RULING-20260819-lanec-issue54-frozen-deployment.md:207`.
9. **`docs/orchestration/SPEC-20260814-gate5-cstat-construction-v1.md:669`** — the fifth
   backwards-bias-direction record, in no enumeration and pointed at by `OI-93`'s evidence column.
10. **`docs/orchestration/state/oi137-covering-search-20260822.sh`** — its own comment asserts *"The
    true count for all six is 0"*; it now reports 8 hits, all self-reference from two new sibling
    documents its two-member `SELF_REFERENCE_SET` does not cover.
11. **`docs/ESTIMATOR_REGISTRY.md`** — last committed 2026-07-16; its FPS `GATED` row is contradicted
    by the 2026-08-07 FPS adoption receipt. Do not cite it as current.
12. **`docs/orchestration/LIVE-STATE.md`** — STALE at the time of writing (see the header).

## 10. COUNTS

| category | items |
|---|---|
| **JOSEPH DECISIONS** (§2) | **12 HEADINGS, and the heading count is NOT the ask count — do not size work from it** (peer review, 2026-08-22). **PR-J4 and PR-J11 need him TOLD, not asked**; **PR-J12** needs no decision from him at all; **PR-J1 is CONDITIONALLY GRANTED ALREADY** by ruling 12 and needs only confirmation once Gate 1 passes, not a fresh authorization; and **PR-J9 BUNDLES several distinct questions** under one heading, so it is >1 ask. Net: **8 fresh asks + 1 confirmation, and PR-J9 expands.** |
| **LANE WORK, dispatchable now** (§3) | **6** — `PR-01`…`PR-06`. Five are the Gate-1 round-4 repairs; the sixth is the P3S packet commit. **Plus 11 parallel items in §6 (`PR-P1`…`PR-P11`), of which 4 are Joseph's and already counted above** — so **13 distinct lane-dispatchable items.** |
| **GATED** (§4) | **15** — `PR-G1`…`PR-G15`. |
| **DONE** (§5) | **10** — `PR-D1`…`PR-D10`. |
| **New couplings found here** (§7) | **3** — `PR-X1`, `PR-X2`, `PR-X3` (added on peer review). |
| **Canonical records measured STALE** (§9) | **12**. |

*(Stated with what each number counts, because two right counts of different populations are the
recurring error in this campaign — see PR-J4.)*

## 11. WHAT FALSIFIES THIS DOCUMENT AS A WHOLE

- **Any commit.** Every sha, digest, file count and line number here is bound to `e2a4409c` and to a
  cluster read at **2026-08-22T20:56-20:59Z**.
- **A `/pscratch` purge.** It would move `PR-06` from "not committed" to "lost", `PR-J3`'s sizing, and
  `Q2`'s "built" half — without touching a single document in this repo.
- **163 GiB of unrelated scratch churn.** It flips `PR-J3`'s "46 members fit".
- **Any of the ten evidence tags being fetched or not fetched.** `PR-X2`'s eight M(ii) documents are
  reachable only through `evidence/prepublication-2026-08-20-0b329e8a`, and six of the ten
  `evidence/*` tags cannot arrive via a plain `git fetch github`.
- **A ruling.** Q1's YES dies on any of the four falsifiers in §0; `PR-J11`'s "closed" dies if
  ruling 11 is amended.
- **The obvious one, and it is this campaign's own signature failure mode:** several items here are
  falsified by exactly the work they authorize. `PR-05`'s M-2 is a name intersection over 717
  untracked files that the authorized run itself perturbs; `PR-J3`'s footprint is the number the k=0
  run exists to measure. **Re-measure before quoting; do not inherit a field from this table.**

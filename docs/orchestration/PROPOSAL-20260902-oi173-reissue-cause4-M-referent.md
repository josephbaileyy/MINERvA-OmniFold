# PROPOSAL 2026-09-02 — re-issue `OI-173`: Ruling 2's referent does not attach to the graded subject

Drafted `2026-09-01T23:07Z` (`2026-09-02 01:07 +0200`; the record is dated local, as the sibling
`DECISION-20260901-*` records are).

**CITABLE FOR:** the timeline measurement in §3 and the referent gap in §2. **NOT CITABLE FOR:**
grading cause 4's `M` cell; discharge of cause 4 or any cause; a change to the quarantine counts; a
Gate-1 or Gate-2 clause; adoption of any covariance; a change to `values.tex`; or any publication
claim. **Gate 2 remains FAIL. CAND `1 of 7`, QUOTED `0 of 7`.** This record asks a question and
grades nothing. **The `M` cell stays `OPEN` and this lane does not move it.**

## 1. Why this exists

Joseph, 2026-09-01, on picking the k=0 work back up:

> *"OI-173 needs re-issuing — it named 1.539 as its referent, and that number can't describe the
> adopted artifact."*

**Those are his words; everything below is this lane's drafting**, in the ratified-drafting shape of
`DECISION-20260901-joseph-authorizes-k0r2-redeploy.md` §2. He named the problem. What this record
adds is that the gap is one step wider than "not the adopted artifact", and that the ruling's own
decision procedure now has no branch that fires.

**Nothing here was re-measured on the cluster.** Perlmutter's scratch filesystem is degraded
(NERSC status, `2026-09-01T05:58`, unrecovered), and every claim below is read from committed bytes
in this repository or from `git` metadata on the local checkout. Where this lane relies on another
lane's measurement rather than its own, it says so.

## 2. THE REFERENT GAP — the recovered value describes a THIRD object

`OI-173`'s Ruling 2 (Joseph, 2026-09-01) is a conditional with two branches:

> ***`M` IS SPECIFIED AGAINST THE CLASS OF OBJECT THE DEFECT REACHED, the reported ratio, NOT the
> stored covariance**; and if the printed `jit_trace` is unrecoverable from committed bytes then `M`
> is **NOT MET (unmeasured), not `N/A`**. The `N/A`-on-the-merits shortcut is explicitly REFUSED.*

**Branch (ii) did not fire: `jit_trace` WAS recovered**, the same day, and is durable at
`state/RECEIPT-20260901-cause4-jitter-floor-recovered.json` — `jit_trace = 3.731e-78`, raw ratio
`1.541`, corrected `1.539`, a −0.11% effect (`FINDING-20260901-cause4-jitter-floor-recovered.md`
§§2–4; that lane's measurement, not this one's).

**But branch (i) delivered a value that does not attach to the subject being graded.** Three distinct
objects are in play, and the ruling was written as though there were two:

| # | object | what it is | does `1.539` describe it? |
|---|---|---|---|
| 1 | the 2026-07-01 occupant of `uq_5d/unified_throw_cov_5d.root` | overwritten 2026-07-13; **no longer exists** | **yes** — this is what the recovered log measured |
| 2 | **X**, the adopted July artifact | retained, not deleted | **no** — its own operands give a *raw* sqrt-trace ratio `1.3107`, and a corrected ratio can never exceed its raw one |
| 3 | **`stamped_bkgaware_meancentered_20260812.root`** — **the graded subject** | the stamped candidate, sha `4f168e83…`, job `56720356` | **no**, and see §3 |

Object 3 is the subject, per `DECISION-20260831-joseph-quarantine-graded-against-the-candidate.md`
§1: *"The seven quarantine causes are graded against `stamped_bkgaware_meancentered_20260812.root` …
NOT against the adopted July artifact X."*

**So Joseph's own framing understates it.** `1.539` does not describe the adopted artifact — and the
adopted artifact is not the thing cause 4 is graded against either. The recovered ratio belongs to a
predecessor of a product that is itself not the grading subject.

## 3. THE TIMELINE, and it makes the gap structural rather than accidental

Measured on the local checkout by this lane, `git show -s`:

| commit | date | what it did |
|---|---|---|
| `a0cdc019` | **2026-06-08** 16:24:23 −0700 | introduced the `jit_trace` deflation in `nd-unfolding/unified_throw_cov.py` |
| `07c18aee` | **2026-07-14** 14:43:19 −0700 | **retired it** |

The graded subject is dated **2026-08-12** in its own filename — **about four weeks after the
deflation was retired** — and `jit_trace` occurs **0 times at HEAD** (that count is the
`OI-173` row's measurement, not this lane's).

**So there is no jitter-corrected reported ratio for the candidate — not lost, but never generated,
the defect having been retired weeks before the subject was built.** **On its own this dates the
COMMIT rather than the producing revision**, and §3a records a measured case in this codebase of
production from a tree ahead of its own commit. **§3b closes that gap by a route that does not
depend on dates at all**, and the conclusion rests on §3b, not on this section. This lane also grepped `VALIDATION_LEDGER.md` and
every `docs/orchestration/*.md` for a sqrt-trace or trace ratio attached to
`stamped_bkgaware_meancentered_20260812.root` and found none — the hits are its size, its sha, and
its `4.510x` **floor** ratio, which is a different quantity.

**Stated as a limit rather than buried:** this is a null result over committed records. Its covering
control is that the same search finds real ratio values for the other objects (`1.539`, `1.3107`,
4D's `2.01`), so the search can find the thing it is looking for.

### 3a. RETRACTED — a stamp-based argument this lane made and the peer lane REFUTED

**This section previously claimed the null did not rest on any search, because the artifact's own
stamps dated its producing code. THAT INFERENCE IS WRONG. It is recorded rather than deleted,
because it was transmitted to the `minerva-omnifold-38` lane and acted on before it was refuted.**

**What was claimed:** that `07c18aee` retires the deflation and introduces the `fixed_seed_null_norm`
stamp in the same commit, therefore *any artifact carrying that stamp was produced by code at or
after `07c18aee`* — code from which the corrected-ratio print had already been deleted — therefore no
log can ever have printed a jitter-corrected ratio for the stamped candidate, **with no search
needed**.

**The commit fact is true and re-verified.** `git show 07c18aee -- nd-unfolding/unified_throw_cov.py`
does both of the following in one commit, at 2026-07-14 14:43:19 −0700.

| | |
|---|---|
| **REMOVES** | `jit_trace = None`; `jit_trace = float(np.sum((x_cv2 - base) ** 2))`; `tr_uni_corr = max(tr_uni - jit_trace, 0.0)`; `st_uni_corr = float(np.sqrt(tr_uni_corr))`; and both prints — the `[null] jitter floor …` line and the `jitter-corrected unified sqrt-trace=… corrected ratio=…` line |
| **ADDS** | `ROOT.TParameter("double")("fixed_seed_null_norm", null_norm).Write()`, and the same key into the emitted dict |

**The retirement of the deflation and the introduction of the stamp key are the SAME EVENT.** That
much stands.

**WHAT REFUTES THE INFERENCE BUILT ON IT — a counterexample from committed bytes, found by the
`minerva-omnifold-38` lane and re-verified here against the cited lines:**

| line | content |
|---|---|
| `VALIDATION_LEDGER.md:484` (VL40) | `fixed_seed_null_norm`, pre-J28 throw ROOT: **present**, `1.9706093906025077e-50` |
| `VALIDATION_LEDGER.md:488` (VL44) | same column: `4.4607819710748654e-38` / `3.4032639007214586e-38` — X's g2 operands, identifying the artifact |
| `nd-unfolding/CORRECTED_UQ_PRODUCTION_STATUS.md:491` | *"02:20 PDT 07-13 HEADLINE LANDED+VALIDATED: uq_5d/unified_throw_cov_5d.root (2.68GB) … Keys: …,`fixed_seed_null_norm`,…"* |

**An artifact written 2026-07-13 carries the stamp, 36.5 hours BEFORE `07c18aee` committed that key.**
The stamping code ran from a working tree before it was committed. `git log -S` dates the oldest
**commit**, never the oldest **existence** — so carrying the stamp does not date the producing code
at or after `07c18aee`, and the claimed conclusion does not follow. **The covering search this
section declared unnecessary is not unnecessary on this argument.**

**ONE THING THE COUNTEREXAMPLE DOES NOT DO, recorded because it slightly favours the retracted
conclusion and must not be mistaken for a rescue of the rule.** The refuted rule needed *stamp ⇒ no
deflation*. In the single inspectable case, that pairing did hold in the working tree: the 07-13
combine ran `--null` and emits the **9-key** inventory that `OI-173`'s row attributes to the
**post-retirement** writer (`a0cdc019`'s emits 6), and the log prints the new `null 1.97e-50` norm
with **no jitter-floor and no corrected-ratio line**. So the stamp and the removal travelled together
there. **But that is production from a tree AHEAD of its commit, and the risk to §3's conclusion is
production from a STALE tree — the opposite direction, on which this case is silent.** One case is
not a rule, which is exactly the error being retracted.

**WHAT WOULD CLOSE IT** is a way to date the **producing** revision that does not run through
`git log -S`. The peer lane holds only a partial on the direct route — the stamps receipt records
`git.head = 5fb7e38b`, verified a descendant of `07c18aee`, but that is the **stamping** tree and is
not established to be the **producing** tree. **§3b closes it by a different route.**

### 3b. THE REPAIR — mutual exclusion between the print and the flux fix

Proposed by the `minerva-omnifold-38` lane after §3a, and **re-verified independently here, including
one dependency that lane did not state and on which the whole argument turns.**

| # | measurement | result |
|---|---|---|
| 1 | `git log --all -S "jitter floor" -- nd-unfolding/unified_throw_cov.py` | **exactly two** commits: `a0cdc019` (introduces), `07c18aee` (removes). `grep -c` at HEAD = **0** |
| 2 | the candidate's unified-throw **input**, `CRITERIA-20260811-…md:365` | `nd-unfolding/uq_5d/unified_throw_cov_5d_fluxfix_20260806_full160.root`, sha256 `4cb02ae7…` — a **fluxfix** product; receipt present at `nd-unfolding/uq_5d/readopt_20260811_footing/STAMPED_HASH_RECEIPT.slurm-56720356.json` |
| 3 | the flux fix `081ae4ac`, 2026-07-31 23:53:54 −0400 | `git merge-base --is-ancestor 07c18aee 081ae4ac` → **TRUE**, verified ancestry rather than a later date |

Measurement 1 is a **reachable null with its own positive control**: the search returned two hits, so
pattern and path are both live.

**THE DEPENDENCY THE ARGUMENT TURNS ON, WHICH WAS NOT STATED WHEN IT WAS PROPOSED.** If the flux fix
lived only *upstream* of the throw-cov producer, a stale `unified_throw_cov.py` could consume
fluxfix inputs and still print the jitter floor, and the argument would collapse. **It does not.**
`git show --stat 081ae4ac` modifies **`nd-unfolding/unified_throw_cov.py` itself**, 83 lines, with
hunks distributed through `do_throws`, `do_blockunits` and `do_combine` — and
`git show 081ae4ac:nd-unfolding/unified_throw_cov.py | grep -c "jitter floor"` = **0**.

**So the mutual exclusion holds WITHIN A SINGLE FILE, not merely within a repository**, which is
materially stronger than as proposed. Across the entire committed history of
`unified_throw_cov.py`, **no version contains both the jitter-floor print and the flux fix.** A tree
old enough to still print the jitter floor cannot produce a fluxfix throw ROOT.

**Note what this does NOT use: the stamp.** The refuted §3a inference ran *stamp ⇒ code date*. This
runs *artifact feature ⇒ code date*, and the feature is in the filename, in the receipt, and in the
sha256. It closes the stale-tree escape in the direction §3a's counterexample left open.

**THE CHAIN, stated so the object is not mistaken.** This dates the producing tree of the candidate's
**input**, not of the candidate's own stamping run — and that is the correct object, because the
jitter print lives in `unified_throw_cov.py`, the producer of the input.

**AND THE DOWNSTREAM STEP MUST BE STATED AS TWO CLAIMS, NOT AS A UNIVERSAL.** An earlier draft of
this record asserted that nothing downstream prints a sqrt-trace ratio for the candidate and that
`adopt_unified_5d.py` *"never"* touches `sqrt_tr_*`. **That is false, and the same file refutes it in
ten seconds** — the `minerva-omnifold-38` lane caught it and both halves below are re-verified here:

1. **The unified-vs-block-sum comparison — cause 4's actual referent — is printed only by
   `unified_throw_cov.py`**, and per §3b no committed revision of that file carries both the print
   and the flux fix.
2. **The adopt step DOES print a sqrt-trace ratio, and it is a different quantity.**
   `adopt_unified_5d.py:127` and `:154` compute `sqrt_tr_comb` and `sqrt_tr_new` as
   `sqrt(trace(C_new))` before and after per-bin inflation; `:158-160` print both and the ratio
   `(x{sqrt_tr_new/sqrt_tr_comb:.3f})`; `:177-178` write `sqrt_tr_old` / `sqrt_tr_new` as
   `TParameter`s. **It compares the adopted COMBINED covariance to itself across inflation, not
   unified against block-sum**, and `grep -c jit_trace nd-unfolding/adopt_unified_5d.py` = **0**, so
   there is nothing in that path to correct it with. The `g` feed at `:88-90` does read only
   `_diag(C_unified)` / `_diag(C_blocksum)`, which is what the earlier draft was reaching for.

**Naming the near-miss is a stronger record than the universal was**, because the near-miss is what a
later reader will actually find. **This is the asymmetric-comparison shape the ledger already has one
instance of** — the peer lane's observation — where a PET `5.711` was set against *"the GBDT-side 5D
ratio (1.539)"*: same units, different vintage. Two sqrt-trace ratios that are not the same quantity
is exactly how that happened.

**TWO RESIDUAL LIMITS, both real.** First, `--all` covers the repository's refs; **a tree never
committed anywhere is outside the search, and §3a proves such trees exist and get run.** To defeat
this someone would have had to hand-merge the flux fix into a pre-`07c18aee` file still carrying the
print — a deliberate reconstruction rather than an accident, given both commits edit the same file in
the same functions, but not zero. Second, §3a's case should make both lanes slower to say
*impossible*: what is established is that no **committed** revision can do it.

**AND THIS LANDS SOMEWHERE ELSE, FLAGGED NOT FILED.** `DECISION-20260831` §2(b) reaches *"no stamp
for X can ever be produced … permanent for X, not a gap awaiting work"* through the **same
`git log -S` step**, and VL40 shows a throw ROOT stamped before that commit. **Its stated 36.5-hour
mechanism is refuted even if its conclusion survives** — the peer lane's reading, which this lane
finds plausible and has not independently swept, is that VL3–VL8 record `fixed_seed_null_norm_checked`
and `upstream_fixed_seed_null_norm` **absent** on X's adopted ROOTs, and those propagated contract
keys are a different family from VL40's raw stamp. **That is a ruling Joseph confirmed directly
(*"yes its my ruling"*), so cite its conclusion and not its 36.5-hour reason until someone owns the
correction.** Neither lane has swept for other consumers of that step.

## 4. WHY THIS IS NOT THE `N/A` SHORTCUT HE REFUSED — the distinction is real but it is his to weigh

The refused argument was: *"the subtraction never touched X's stored inputs, so cause 4 is `N/A` for
X on the merits."* `OI-173` names it and resists it, because it rests on a claim about **how the
artifact was built** whose payoff is its own premise.

**§3 is a different claim in kind: it is about WHEN the defect was in force relative to when the
subject was produced.** That is an external, dated fact about the code history, not a claim about the
artifact's internals.

**This lane does not assert that the difference is sufficient to license `N/A`, and it should not be
read as doing so.** He refused that disposition once; whether a differently-grounded route reaches it
is exactly the thing being put back to him. Under his own rule — *do not let measurability choose the
specification* — the fact that §3 makes `M` convenient to close is a reason for suspicion, not a
reason to close it.

## 5. THE TWO LIVE READINGS

**Reading A — `NOT MET (unmeasured)` against the candidate.** Branch (ii)'s outcome, reached by a
different route: there is no reported ratio for the subject, so the magnitude leg is unsatisfied.
Preserves both his refusal of `N/A` and the against-the-candidate ruling. **Consequence to state
plainly: cause 4 would then be undischargeable for as long as the referent stays unmeasured** — the
cell sits `OPEN` and cause 4 cannot contribute to the CAND count.

**The permanence is supported by §3b, subject to its two stated limits.** No committed revision of
`unified_throw_cov.py` can both print the jitter floor and produce the candidate's fluxfix input, so
the measurement cannot be taken for this subject and the cell should say so on its face:
`NOT MET (unmeasured — and unmeasurable for this subject)`, so no later lane spends compute trying to
close it. **A covering log sweep is not the way to establish this and should not be launched for it**
— it would be the weaker foundation under
`FINDING-20260901-pscratch-read-stalls-block-a2b.md` §6 (*"an empty result from a sweep is not a
negative result"*), and while Perlmutter's scratch is degraded such a sweep will hang and its silence
will be indistinguishable from a null.

**Drafting history, kept rather than tidied:** this section first asserted the permanence on the
stamp argument retracted in §3a, then withdrew it to *"undischargeable for as long as the referent
stays unmeasured"*, and now restores it on §3b's independent route. The claim is the same; only its
third support survives scrutiny.

**Reading B — the referent is the ratio the defect actually reached, historically.** The specified
class is *reported prose ratios*; the one the defect reached is `1.541 → 1.539`. Under this reading
`M` is **MET** at −0.11%, and the later overwriting of that ratio's product is irrelevant, because
`M` asks the *magnitude of the defect*, not the state of the artifact. **Cost: it grades cause 4
against an object the 2026-08-31 ruling excluded as a grading subject** — though arguably that ruling
governs *which artifact* is graded, while `M` under Ruling 2 is a property of the defect rather than
of an artifact, in which case the two rulings do not actually collide.

**This lane's recommendation: Reading A, written with its permanence on its face.** It is the
conservative disposition, it is continuous with his refusal of the shortcut, and it costs nothing.
Reading B is not unreasonable and is recorded at its real strength rather than as a straw option —
its best argument, the one in the clause above, is genuinely available and this lane could not refute
it. **He may take either; the recommendation is drafting, not a finding.**

## 6. What is already done, so it is not redone

`VALIDATION_LEDGER.md`'s misattribution is **corrected and committed** at `1df84dfc`, as a marked
block beside the original sentences rather than a rewrite. `FINDING-20260901-…-recovered.md` §8's
recommended next step is therefore discharged. **This proposal is what remains**, and it is the part
that needs him rather than a lane.

## 7. What this record does NOT do

It does not grade `M`, move the cell, discharge cause 4, change the counts, touch `values.tex`, move
any gate, or authorize any compute. It does not re-open `DECISION-20260831`. It does not depend on
the k=0 redeploy or on `FREEZE-20260830-k0-deployment-7ac0edec.md`, and it is not blocked by the
scratch outage — it is free, on paper, and answerable at any time.

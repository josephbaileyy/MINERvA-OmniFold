# MAP — what blocks the note's GBDT section, one row per quarantine cause

**Lane A, 2026-08-17, at `388abd8`. READ-ONLY: `docs/analysis-note/` untouched, not one character.**
**Nothing here adjudicates any cause.** Each row says what the cause is, its state derived from
artifacts, what would discharge it, and who can. Decisions are Joseph's.

---

## THE ONE SENTENCE

**Neither one nor six — the question has no artifact-free answer, and for the artifact `values.tex`
actually quotes it is SEVEN.**

| artifact | causes discharged | remaining |
|---|---|---|
| the July `…_bkgaware_uthrow.root` **the note quotes today** | **0 of 7** | **7** |
| the footing-matched, stamp-verified J28 candidate that would **replace** it | **1 of 7** (cause 2, Joseph 2026-08-12) | **6** |

**So `PROCEDURE`'s *"exactly one is discharged"* is true of neither artifact.** It counted cause 7,
whose discharge is the **FPS** covariance (266 bins) and not the 5D GBDT object (10,694 of 65,856) —
`CRITERIA` §4.1, `BEN-100`. Read as a flat list it says *"one down, six to go"* about whichever product
the reader had in mind.

**Consequence for Joseph's actual question:** this is not one-cause-from-done under any reading. It needs
dedicated effort, and the cheapest path is already costed by `CRITERIA`: **2 → 4 → 3 → 1 → 6**, with
cause 2 done. **Four of the six remaining need no cluster time at all** (§2). Cause 6 alone needs a run.

---

## 1. The has-this-been-done check

Mine, with terms the dispatch had not used, at `388abd8`:

```
git ls-tree -r --name-only origin/main | grep -iE 'MAP-|STATUS-MAP|quarantine'
git grep -il 'discharg' origin/main -- 'docs/*'
grep -n '2026-07-12\|quarantin' VALIDATION_LEDGER.md
grep -rn 'cause 1|cause 2|cause 6|cause 7|seven construction' VALIDATION_LEDGER.md
```

**No status map exists.** The causes are scoped across `VALIDATION_LEDGER.md`,
`CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md` (§2 criteria, §3 per-cause legs),
`DETERMINATION-20260811-cause5-binding-half.md` and `nd-unfolding/CORRECTED_UQ_PRODUCTION_STATUS.md`.
This is the first single map. **One correction to the dispatch's own premise:** it cites the quarantine
at `VALIDATION_LEDGER.md:60-88`; that range now holds Gate-6 trajectory rows. The ledger has grown since
2026-08-11 and the quarantine must be found by content. `CRITERIA` §4.4 already recorded this class —
*"the only predeclared discharge criterion any of these five causes has is cited by a line number that no
longer contains it."*

---

## 2. The seven causes

Legs are `C` construction / `P` provenance / `M` magnitude / `T` test, per `CRITERIA` §0; a cause
discharges only on four METs. States below are `CRITERIA` §3 as of 2026-08-12, **re-derived at HEAD** and
annotated where anything moved.

| # | cause | state at HEAD | what would discharge it | who |
|---|---|---|---|---|
| **1** | one-sided endpoint interpolation | **OPEN — C and M.** `C` MET (path enumerated: 11 modules, no `pet_*`/`unified_throw`, so both unfixed one-sided sites are provably **off** X's path). `P` PARTIAL — no committed per-band endpoint census. `M` OPEN for the adopted product. `T` MET, mutation-verified N1/N2. | A **static audit** of X's path plus **one measurement** (the per-band endpoint census). No cluster time. | a lane |
| **2** | CV centering | **DISCHARGED 2026-08-12 — for the candidate only**, by Joseph, naming the artifact by path and sha256 (`stamped_bkgaware_meancentered_20260812.root` `4f168e83…`, CV variant `dbcd5359…`, job `56720356`). **Still OPEN for the July product the note quotes**, whose nine stamp keys read `ABSENT`. | Nothing, for the candidate. For X: it cannot be discharged on X — X predates the stamping. **X gets replaced, not repaired.** | done |
| **3** | varying estimator seeds | **OPEN — provenance only.** `C` MET, `P` MET (one seed `1000` across 40 throw + 36 block slabs; `upstream_n_throws=160` read back from the adopted product), `M` MET (null read off **both** products, `1.9706e-50` pre-J28 / `5.8223e-50` J28, tol `1e-12`), `T` MET both directions. | **Provenance in the adopted product** — `BEN-106`'s stamp propagation, **one edit, which closes this leg for 2, 3 and 4 at once**. Already done for the candidate. | a lane |
| **4** | scalar jitter subtraction | **OPEN — M and provenance.** `C`/`P`/`T` MET (`fixed_seed_null_norm_checked=1`, `upstream_fixed_seed_null_norm=5.8223488501140625e-50`; `T` MET and **N6 caught a defect nothing else did**). `M` **UNRESOLVED** — the recorded `1.539` is a different ensemble. | The same stamp propagation, **plus its magnitude on the right ensemble.** No cluster time. | a lane |
| **5** | the binding half | **NOT THIS LANE'S AND NOT RE-DERIVED HERE.** `DETERMINATION-20260811-cause5-binding-half.md` establishes which half binds; the note states the requirement algebraically at `sec_pet.tex:117-127`, and the determination records *"the cross term is negative in every single universe"*, i.e. a correctness defect, not only a bookkeeping one. | Stated in the `DETERMINATION`. **I did not re-derive it and do not summarise its verdict** — reading a state off another lane's document is the failure this map exists to correct. | Session C |
| **6** | incomplete statistical projection | **OPEN, and still furthest.** `C` PARTIAL (the `(E_avail,W)` projector's unguarded all-zero rows are now detected and reported, `BEN-110`; the ensemble leg and corrected upstream input untouched). `P` **OPEN — no product rebuilt at all.** `M` OPEN. `T` MET for the coverage guard. | **A cluster rebuild it has never had**, a corrected upstream input, and a code repair to the coverage guard. **The only cause needing compute.** Also gates the generator ratios, so it is on two deliverables' critical path. | a lane + compute authorization |
| **7** | selection-complete lateral replacement | **MATERIALLY CHANGED SINCE 2026-08-11 — see §4.** Discharged 2026-08-07 for the **FPS** covariance (266 bins, job `56431823`). For X it was *"the lateral replacement does not exist"*; **it now exists** and is projected — but is marked `publication_gate_rejects_this: true` and `p4_adopt_standard.py` refuses it outright. | **Adoption of a selection-complete 5D lateral replacement for X**, which requires the non-adoptable marker to be resolvable — not an arithmetic step. | Joseph (adoption is his call) |

**Four of the six remaining causes (1, 3, 4, and 7's arithmetic part) need no cluster time.** Causes 3
and 4 share one edit. That is the actionable shape of this gate.

> **POINTER, added 2026-08-30 by the stale blocker sweep lane — the "one edit" multiplier in cause 3's
> and cause 4's remedy cells above, and the sentence immediately preceding this block, DO NOT HOLD.
> Row text left as written; nothing is regraded here (`BEN-381` — this lane measured it).**
>
> The claim is *"`BEN-106`'s stamp propagation, **one edit, which closes this leg for 2, 3 and 4 at
> once**"*. It fails three ways, each independently:
>
> 1. **`BEN-106`'s propagation is a HOP** — `adopt_unified_5d.py:198-210` re-writes keys it read out of
>    the throw root, so it can only carry what a producer already wrote. Causes 2 and 4 needed
>    `joint_mean_shift_norm` and `fixed_seed_null_norm`, **already written** by `unified_throw_cov.py`;
>    cause 3 needed a **seed value, which no producer wrote on either leg.** The measured cost of that
>    difference is **four producer/wrapper edits across three days** — `3dd5e66e`, `214acdbb` (08-18),
>    `5afb7947` (08-19), `bd72112b` (08-20) — plus `nd-unfolding/seed_offset_policy.py`, 38,048 B, which
>    did not exist when this cell was written.
> 2. **On CAND there were no other halves to close.** `SCOREBOARD`'s board already had cause 2's `P`
>    MET (job `56720356`) and cause 4's `P` MET (`receipt_candidate_stamps_5d.json`, S1) on the day this
>    was written.
> 3. **On QUOTED no edit closes any of the three** — X predates the stamping (`SCOREBOARD` §1).
>
> **AND CAUSE 3's `P-i` IS NO LONGER A NO-COMPUTE ITEM.** Its remedy landed, which is what moved it: the
> stamp exists, so the only thing left is a **product carrying a value**, and that is a producing run.
> It cannot close on CAND or QUOTED at all — both predate the producers — so it is carried by whatever
> run builds the next 5D product and is not a separate leg.
>
> Measurements and the routed decisions:
> [`FINDING-20260830-quarantine-nocompute-legs-measured.md`](FINDING-20260830-quarantine-nocompute-legs-measured.md)
> §1–§3, `OI-170`/`OI-171`.

---

## 3. `FINDING-20260815-the-quarantine-measured-a-different-run.md`: it does **neither**

Asked whether it retires a cause, weakens one, or neither. **Neither — and the reason is that it is a
different quarantine.** Measured:

```
grep -c '2026-07-12' FINDING-20260815-the-quarantine-measured-a-different-run.md   -> 0
grep -oE 'cause [1-7]'  (same file)                                               -> no matches
grep -oE 'quarantine[: ][a-z_]*'                                                  -> quarantine:dual_publication_rejection,
                                                                                     "quarantine manifest" x2
```

It concerns the **PET fold-forward / dual-publication** quarantine manifest
(`NONQUOTABLE-DIAGNOSTIC.manifest.slurm-56552326.json`, closure `56552326`), not the 2026-07-12
uncertainty-remediation quarantine with seven construction causes. **The word "quarantine" is overloaded
across two campaigns** — the same shape as `BEN-080` (`B1` meaning two things) and `BEN-100` (one tally,
two products), and the third time tonight that an overloaded name nearly moved a conclusion between
objects. Its findings stand on their own; they touch nothing in §2.

---

## 4. What moved since `PROCEDURE` was written, and it is one row

`CRITERIA` §4.1 grounded X's *zero of seven* partly on X's lateral replacement **not existing**
(`OPEN_ITEMS.md:92-101`: *"its P4-5D lateral has not been built"*). **That is no longer true.**

* `std_final5_candidate.root` exists — 45 bands, 40 retained, `sqrt_tr_syst 4.3513e-38`,
  `sqrt_tr_full 4.3576e-38`, first recorded `FINDING-20260809-stage6-central-gate-cannot-pass.md:312`.
* The authorized stages-4-6 run (`57128458`, rc 0, 2026-08-16) **rewrote it**: 49 keys where the audited
  object had 47, the addition being `hRowIndex5D`, +23,969 bytes (`cb522f3`). The covariance **content**
  is bit-identical — `f26b3bfe…` (5D total), `c1fe11b1…` (4D stored) — so the audits' scientific
  conclusions transfer; only their whole-file digest bindings went stale, and that is indexed rather than
  corrected in place. Stage 6 produced `std_proj4d_candidate.root`.

**What this does NOT do:** it does not discharge cause 7 for X. The candidate carries
`publication_gate_rejects_this: true`, `p4_adopt_standard.py` refuses it, and
`FINDING-20260809` states it plainly — *"not adoptable and not quotable."* **The state change is
"does not exist" → "exists, non-adoptable", which is progress on the path and not a discharge.** Stating
it as a discharge would be exactly the tally error §4.1 was written about.

---

## 5. J28 is RESOLVED-PENDING-THE-GATE, not an unresolved choice — correcting my own document

**`RECONCILIATION-20260817-gbdtfive-macros-vs-rebuilt-candidate.md` §4b called the footing choice
UNRESOLVED. That is superseded.** The footing-matched re-adoption was already run on 2026-08-11
(`PREDECLARE-20260811-bkgaware-footing-readopt.md`, job `56720356`), and both arms are in the ledger.
Verified in the repo rather than taken from the relay — `VALIDATION_LEDGER.md:187-190`:

| arm | `--combined` | `sqrt_tr_old` | `sqrt_tr_new` | × | median frac/bin | PSD most-neg/max |
|---|---|---|---|---|---|---|
| **A1** bkgaware, mean-centered | bkgaware | `4.3578e-38` | **`5.2696e-38`** | 1.209 | 13.36% → 13.57% | `−3.19e-16` |
| **A2** bkgaware, CV-centered | bkgaware | `4.3578e-38` | **`5.6743e-38`** | 1.302 | 13.36% → 14.02% | `−3.23e-16` |
| C1 control, non-bkgaware | non-bkgaware | `4.3455e-38` | `5.2600e-38` | 1.210 | 13.43% → 13.61% | `−4.87e-16` |
| C2 control, non-bkgaware | non-bkgaware | `4.3455e-38` | `5.6609e-38` | 1.303 | 13.43% → 14.09% | `−3.92e-16` |

**A1/A2 are the footing-matched pair; C1/C2 are the controls, and both controls reproduce the original
run digit for digit.** So my reconciliation reported C1/C2 — the controls — as "the replacement pair",
and they are the *non*-bkgaware arm. **A1/A2 are the ones that match the note's "background-aware" prose.**

### 5a. And `\gbdtFiveBlockMedian` does NOT change under the footing-matched path

**This corrects a misread of that table, including the one in the dispatch to me** (*"block median
13.36 → 13.57"*). The `median frac/bin` column is an **arrow from the block-sum median to the ADOPTED
median**, not a new block median:

* `13.36%` is the **block sum** (`= \gbdtFiveBlockMedian`, the bkgaware combined `median rel 13.359%`),
  and it is **identical on the left of all four rows for a given footing** — 13.36 bkgaware, 13.43
  non-bkgaware.
* `13.57%` / `14.02%` are the **adopted** medians, and they differ **by arm**.

**So under the footing-matched (bkgaware) path `\gbdtFiveBlockMedian` stays `13.36` and only
`\gbdtFiveAdoptTrace` and `\gbdtFiveCVTrace` move.** The block median moves only if the *footing*
changes. That materially simplifies the eventual edit — one fewer macro — and it is the block-sum-vs-
adopted conflation this whole reconciliation has had to keep separating.

**The predeclaration's own condition is the gate this map describes:** the values are **not quotable
while the quarantine stands.** So J28 supplies magnitudes and waits on §2, rather than being a decision
anyone still owes.

---

## 6. The two rows arithmetic cannot discharge — carried separately, per instruction

From `PROCEDURE` §3. **Not cause-shaped; a map that folded them in would mislead.**

**(a) `sec_systematics.tex:169` — *"Both are positive semidefinite."*** The `PROCEDURE` says this
*"must be re-established from the new products; it does not survive by inheritance."* **Evidence now
exists and I did not expect to find it:** `VL16`/`VL17` record most-negative-eigenvalue-over-max of
`−3.19e-16` and `−3.23e-16` for A1/A2 (controls `−4.87e-16`, `−3.92e-16`). **Whether a ratio of
`−3e-16` is reported as "positive semidefinite" is a physics-presentation judgement and I am not making
it** — but the measurement is not missing, which is a different state from what the `PROCEDURE` records.
**Owner: the GBDT/close-out lane.**

**(b) `sec_systematics.tex:169-170` — *"neither is adopted for publication until the selection-complete
lateral replacement lands."*** `PROCEDURE` §3: this sentence **must be DELETED OR REWRITTEN, not
"updated"**. §4 above is why it is now delicate rather than simply false: the replacement **exists** and
is **non-adoptable**, so the sentence's antecedent has half-changed. **Whoever rewrites it needs §4's
distinction in hand or they will write something true of neither state.** Joseph's call.

---

## 7. Limits, stated rather than left to be found

* **I adjudicated nothing.** No cause is declared discharged, weakened, or retired here.
* **Cause 5 is not re-derived** — it is Session C's, and reading its state off another lane's document is
  the error this map corrects elsewhere. Its row says where to look, not what it says.
* **No cluster measurement.** Every state above is from committed artifacts and the ledger; the
  `/pscratch` products are unreadable from this checkout. Where a number came from a relay I said so.
* **Two counts in §0, deliberately**, because a single number is the defect `CRITERIA` §4.1 records.
* **`values.tex` and the note are untouched.** `PROCEDURE`'s own header: nothing in it authorizes an edit,
  and nothing here does either.

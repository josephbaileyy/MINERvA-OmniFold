# SPEC — the `M(ii)` seed scan's submission topology

**Authored by the Codex session (a different provider, no shared context with any lane on this
campaign), read-only, at `origin/main` `8640f561`. Committed by the mediator because a specification
that lives only in a message does not exist. Codex made no repo edits, submitted nothing, and
cancelled nothing; the working tree carried only a pre-existing untracked file throughout, which it
disclosed before starting rather than after.**

**Why it was commissioned.** Five Claude lanes reviewed the driver, two of them by explicit mutation
review, and none found the launch blocker. The lane that built it had a probe that **forces the resume
guard false** — configured into the one regime where the defect is invisible. An independent reviewer
without that assumption found it in under an hour.

**Read the DERIVED/JUDGMENT split as load-bearing.** Codex separated what the current producers and
consumers force from what needs an owner's ruling, and did not blur them. Items 6 and 7 are judgments
and are **lane C's**; nothing in this document decides them.

---

## 1. NAMESPACE INVARIANT (DERIVED)

**Each member gets one immutable root keyed by BOTH member and offset** — `mii/member_00_k_00000/`,
`member_01_k_01200/`. Every producer, log, combine, receipt and done-marker stays below it. Shared
inputs (banks, `of_inputs_5d.npz`, CV, omnifile, flux) are **read-only**.

**A preflight must reject any member output path equal to, under, or glob-overlapping the six canonical
archive namespaces.** No member writes `boot_nd_5d/`, `seedscan_split_5d/`,
`uq_5d/universe_sweep_bkgaware/`, `uq_5d/{uthrow,block}_slabs_5d{,_sb}/`,
`uq_5d/unified_throw_cov_5d.root`, `uq_cov_{stat,mlsplit}_5d.root`, or the canonical finalizer outputs.

**Resume becomes IDENTITY-AWARE: skip only if the product is structurally complete AND stamps the
desired member `j`, `k`, estimator seed, draw seed, input digests and code digest. A complete file from
another `k` is a HARD FAILURE — never a skip, never an overwrite.** Fresh member roots start
absent/empty. Atomic writes remain required.

## 2. PER-MEMBER PRODUCERS (DERIVED)

| leg | population | seed | destination |
|---|---|---|---|
| `V_j` vertical sweep | exactly 169 universes | estimator `42+k` | `member/vertical/` |
| `L_j` detector direct | 18 laterals + matched CV = **19** | estimator `42+k` | `member/lateral/` |
| `B_j` bootstrap | ids `1..100` | estimator `42+k`, draw ids unchanged | `member/bootstrap/` |
| `M_j` split | ids `1..24` | estimator `42+k`, split ids unchanged | `member/split/` |
| `T_j` throws | content covers ids `0..159` | estimator `1000+k`, **draw fixed `1000`** | `member/uthrow/throws/` |
| `K_j` blocks | 12 knob endpoint pairs + 100 flux units (124 logical) | estimator `1000+k`, draw `1000` | `member/uthrow/blocks/` |

**`L_j` IS CURRENTLY MISSING FROM THE SIX-LAUNCHER PLAN AND IS HARDCODED AT `--seed 42`.** See item 7.

**Do not specify `K_j`'s correctness by FILE COUNT** — historical layouts pack units differently.

## 3. VALIDATOR BARRIERS, NOT RAW `afterok` EDGES (DERIVED, plus this campaign's failure history)

**Each array flows to a member-local validator, submitted `afterany` or otherwise guaranteed to run.**
It asserts exact ID/population, readability, no duplicates or extras, and every product stamp; it exits
success **only** on the complete desired population.

> **Downstream combines depend `afterok` on the VALIDATORS, not on the arrays — because an array can
> return rows, or exit 0, with an incomplete or misrouted population.**

`V_j→VV_j`, `L_j→LV_j`, `B_j→BV_j`, `M_j→MV_j`, `T_j→TV_j`, `K_j→KV_j`.

**Mandatory stamp equalities:** every `V`/`L`/`B`/`M` product carries `declared=1`, `offset=k`,
`estimator=42+k`; every `T`/`K` product carries `declared=1`, `offset=k`, `estimator=1000+k`,
`draw=1000`; and all products bind the same fixed input and code basis declared for the scan.

## 4. COMPONENT COMBINES (DERIVED)

- `BV_j → STAT_j` — exact bootstrap manifest → `member/uq_cov_stat.root`
- `MV_j → ML_j` — exact split manifest → `member/uq_cov_ml.root`
- `TV_j + KV_j → U_j` — unified combine reads **only member throw/block globs** → `member/unified.root`.
  **This is what fixes the `block_slabs_5d` vs `block_slabs_5d_sb` disconnect.**
- `VV_j + LV_j + STAT_j + ML_j → SWEEP_j` — analyze the exact **188**-product union → member-local
  bkgaware combined covariance. **`combine_cov_nd` checks ids but not offset metadata, and
  `analyze_universes` merely globs — so the pre-combine validators are load-bearing.**
- `SWEEP_j + U_j → ADOPT_j` — member-local unified adoption. **`sbatch_finalize_5d_bkgaware_gpu.sh`
  cannot serve unchanged: it reuses canonical stat/ML/unified roots and canonical paths.**
- `ADOPT_j → MVFINAL_j` — read back component and final stamps/digests, recompute the claimed component
  relationship, write **one** member receipt. **No member is admitted without this terminal receipt.**

**The global ENSEMBLE combine waits `afterok` on all 50 `MVFINAL_j`.** It asserts exactly offsets
`1200j` for `j = 0..49`; exactly one receipt per member; **cross-member product digests DISTINCT wherever
stochastic outputs should differ**; all fixed inputs and draw seeds identical; all estimator seeds
correct — and only then computes the predeclared spread metrics.

## 5. SLURM SHAPE (DERIVED)

```
  [V -> VV] --\
  [L -> LV] ----> SWEEP ----\
  [B -> BV -> STAT] --------> ADOPT -> FINAL-VALIDATE
  [M -> MV -> ML] ----------> /
  [T -> TV] --\              /
  [K -> KV] ----> U ----------/
```
**Cross-member edges are unnecessary because namespaces are disjoint**; concurrency is a resource
choice. Every dependency and job id must be recorded. **A flat list of `sbatch` strings is not this DAG.**

## 6. THE ANCHOR `j = 0` — derivation, then JUDGMENT (lane C's)

**DERIVED:** the canonical archive already occupies every current path; the existing bootstrap/split
resume guards will skip it; old artifacts lack the new offset-declared stamp; **fresh files necessarily
differ in bytes because writers add metadata**; and the historical bootstrap/split argv **omitted the
explicit estimator flag**. **Therefore in-place resume cannot establish a scan anchor, and the existing
`k0` literal parser establishes only seed SEMANTICS.**

**JUDGMENT REQUIRED — choose one and name it before launch:**

- **(A), Codex's recommendation:** recompute `k = 0` in `member_00` isolation under the exact scan code,
  then compare the **scientific payload** against archived products under a **predeclared** equality
  rule — bitwise where reproducible, otherwise named tolerances; metadata bytes excluded and separately
  audited. **This costs a full member and retires the free-anchor cost premise.**
- **(B):** reuse archive objects read-only via digest-bound sidecar receipts referenced into
  `member_00`, with **no claim that they carry offset stamps**. Saves compute; needs evidence that each
  archived component has the exact inputs, code and configuration, and an owner ruling that **semantic
  rather than byte identity** suffices. **Presence alone is inadequate.**
- **(C):** exclude the archive from the 50 and run 50 fresh non-zero members, using the archive only as
  an external reference. **Changes `n` and the anchor's interpretation; needs a statistical ruling.**

**Never run `j = 0` in canonical paths. Whichever option wins, the global reconciler must distinguish
REUSED ARCHIVE evidence from FRESHLY COMPUTED scan-member evidence.**

## 7. THE LATERAL BOUNDARY — JUDGMENT (lane C's)

The predeclaration prices **sweep + the 19-task lateral + finalize** as `C_syst`, and the finalizer
consumes the 188 union — **so `L_j` is derived above as part of the full composite.** But the settled
four-leg baseline table names only `sweep_bank`'s 169 verticals.

**The owner must either (a) add the direct lateral/CV launcher to `g1` at `42+k`, or (b) explicitly hold
it fixed and state that the measured object differs from the priced full `C_syst` composite. Topology
cannot decide that physics scope.**

## 8. REQUIRED DRY-RUN POWER TESTS (DERIVED FROM LIVE FAILURES)

Run real Bash for at least `k = 0` and `k = 1200` with command **and resume behaviour** stubbed. Assert:
inputs identical; **output roots different and member-keyed**; observed seeds exactly `baseline + k`;
draw exactly `1000`; **a complete wrong-`k` product causes FAIL, not SKIP**; exact manifests reach the
validators; and the dependency graph has `U` after `TV+KV`, `SWEEP` after `VV+LV+STAT+ML`, `ADOPT` after
`U+SWEEP`.

> **The shipped probe's forced no-resume regime is insufficient by itself — that regime is why the
> launch blocker survived five reviews.**

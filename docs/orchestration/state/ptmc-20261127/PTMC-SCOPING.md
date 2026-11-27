# PTMC scoping: REF-C2C1's paired IBU-versus-OmniFold test under MINERvA's counting convention (2026-11-27)

**Asked for by** Joseph, through the director (2026-11-27). The job is to redo the note's paired-bootstrap test,
REF-C2C1's C2-R1, with both methods under MINERvA's convention, i.e. OOFVC's R reclassification. Both methods run on
the same paired three-stream draws, on the analysis grid.

**Drafted by** ibu-chi-squared-issue. Read-only on origin/main `e726cb876`. No cluster contact, no data read and no
numbers. The DRAFT declaration is `PTMC-DECLARATION.md`, beside this file.

## 1. The answer on the calendar

**Can it land before 2026-12-01 with full tests and reads? Not reliably. I recommend planning it for v2 and running it
at full rigour anyway.**
- **Best case:** the receipt merges on 11-30, with no slack. That needs every read to clear in one round and the queue
  to be quick.
- **What OOFVC took:** two or three read rounds on its declaration and code, which is the realistic expectation here.
  That puts the merged result at 12-01 or later.
- **The note text** would then still need writing. JE drafts it, and Joseph reads and owns the wording.
- **If the release slips,** or Joseph decides v1 can carry a "result to follow" line, this can join v1. That is
  Joseph's call.

| day | step | depends on |
|---|---|---|
| 11-27 | this scoping and DRAFT declaration; declaration reads (Grok, codex-school, Sonnet); revision | the director's answers to §3 |
| 11-28 | code: driver diff (~30 lines), paired runner (new file), scorer (imports REF-C2C1's reader); tests; mutation campaign; code reads | the declaration's audit |
| 11-29 | binding; fence round; a 0 node-h stat connect (§3, D4); pilot (4 units); then 199 replicas, ~2–3 h wall on 5 nodes plus queue | the GO; cov2d acks |
| 11-30 | score on the laptop; receipts PR; CI; merge; the director reads it; it goes to Joseph | — |
| 12-01 | the note text, if Joseph wants it in v1 | Joseph |

## 2. The price

| item | units | node-h |
|---|---|---|
| pilot: the R central, the off central, the off replica b = 1, the R replica b = 1 | 4, one node, 4 lanes | ≈ 0.2 (OOFVC's four-unit job: 756 s on one node, 0.21) |
| R replicas b = 2..200 | 199 | 199 × 0.0489 ≈ 9.7 |
| the matched-baseline read and the score | login node and laptop | 0 |
| **total** | | **≈ 9.9; cap 12.5** |

- **0.0489 node-h** is SCOPE §4's E_R replica cost, which REF-C2C1's declaration also uses.
- **Cross-check against REF-C2C1's actual spend.** Its 350 replica units took about 10.6 node-h:
  - four 2.5 h jobs that timed out, plus a 0.61 h completion job (`fd/receipts-ref-c2c1/step2/units-replicas/*/sacct.txt`);
  - about 0.03 node-h per unit, mixing 300 c2 units (refinement plus IBU) with 50 c1 units (refinement plus OmniFold).
- **The cost holds only with the paired unit (§3, D3).** One driver run does one refinement and feeds both methods.
  Separate IBU and E_R units would cost about 200 × (0.049 + 0.027) ≈ 15 node-h, over the cap.
- **STOP rule:** if the pilot's measured per-replica cost × 200 exceeds 11.5 node-h, the replicas do not launch, and it
  goes back to the director.

## 3. Decisions the draft makes, each with a recommendation; the director's call

- **D1. Seeds 1..200,** the first 200 of Q_R's set. The alternative is 301..500, REF-C2C1's "new" option.
  - With D2, every R replica b is Q_R's replica b, and the original c2's replica b, with only the reclassification
    changed. That makes the matched baseline (D4) possible.
  - The seeds are fixed here, before any number.
- **D2. A moved row keeps its own draw.** Its signal-stream factor is its mc_background entry's background-stream
  factor, b_bkg[entry].
  - The original signal rows' factors are drawn as now: Poisson(1) over exactly the off-convention rows. So every MC
    event's factor is the same under both conventions, and each event's factor is used exactly once.
  - The alternative is to extend the signal-stream draw over the appended rows. It is equally valid as a bootstrap,
    but it breaks D4's pairing for those rows.
- **D3. A paired unit.** One in-process driver run (E_R's argv, `--signal-convention minerva`, the bootstrap flags)
  hands the same refined w̃ to both methods:
  - the driver's own OmniFold, whose hXSec2D is E_R's;
  - IBU, on the identical binned problem, with REF-C2C1's `binned_problem`, `roounfold_bayes` and `xsec_at_every_k`.
  - **The code stays as it is.** It lives in a new runner. `ref_c2c1.py` (285dd138) and `ref_c2c1_read.py` (0412401b)
    are imported, not edited. The scorer calls the reader's own `t_and_null`, `rank_for` and `classify_t`.
  - **The pairing is tighter than the original's.** REF-C2C1 refitted the refinement separately for its IBU and E_R
    replicas (LightGBM is not deterministic at 64 threads). Here both methods share one w̃.
- **D4. A matched baseline at no node-h cost.** T_off is computed at N = 200 and rank 50 on seeds 1..200 from
  REF-C2C1's own products:
  - the IBU replicas, `ref-c2c1-20261106/units/c2_replica_b{1..200}.npz`;
  - Q_R's staged copies, `ref-c2c1-20261106/read-2/inputs/`.
  - **Why it matters:** the original read N = 300 at rank 75. Without the baseline, an "agree" under R could just be
    lower power at N = 200, so the change of reading could not be laid on the convention.
  - **Where those products stand:**
    - Stage 4 deleted only the staging root (`stage4-delete/README.txt`).
    - Nothing on main says the units or read-2 were removed, and they were last read through O_NOATIME. The purge
      window from 11-06 runs to about 2027-01-01.
    - Their presence needs a 0 node-h stat connect after the GO.
  - **If they are gone,** the baseline clause drops and the reading is reported as measured (declaration §5).
- **D5. The analysis grid,** E_R's edges: 0.07 / 0.33 / 0.47 GeV/c on p_T, at M's driver 938c53c5. It is not
  OOFVC's paper-edge grid.
  - OOFVC's rows file (r3, `cbf34bd8`) is reused as it is. Its "true muon in the grid" test depends only on the outer
    extents (p_T 0–4.5, p∥ 1.5–60 GeV/c), which the two grids share.
  - A control asserts this (C-GRID).
  - The R central's append counts must equal r3's: 536,518 appended and 7,644 outside (C-MOVE).

## 4. What I need from limitation-resolver (one short question)

Is anything of LR's, planned or running, going to remove `/pscratch/sd/j/josephrb/ref-c2c1-20261106/units` or
`.../read-2/inputs` before about 12-05? I would read them through O_NOATIME only, at the read step. Nothing else is
needed: REF-C2C1's code and records are on main.

## 5. What this does not touch

- Joseph's EVW5D deposit directory and scratch r2.
- r3 is read only: the rows file, plus a staging copy made through O_NOATIME at the binding.
- cov2d's protected paths: the fence round gets the usual acks, and the Mac tests run light (nice, one thread).

# REF-C2C1 BINDING 1, step one: the 2D binned cross-check (c2) and the joint-test estimator in 2D (c1) (director, 2026-11-05)

**Binds** [`REF-C2C1-DECLARATION.md`](REF-C2C1-DECLARATION.md), sha256
`63a1efa33fa4e1e3d3e15997b47232b7092dde21096c26f3e629729d14183c3b`, as merged in PR #767 at
**M = `e1a2cf85abd22f8674465307d6d2b4c111b1287d`** (PR head `b8d28cb7`).

**Commissioned by** `DECISION-20261104-joseph-referee-analysis-commission.md` (c2 with c1). B-C's hold was released
on #769 (`f1a33555`).

## What the director checked

- **The digest.** The declaration's sha256 at M is the one above. Two merges of main into the branch (`aa801c57`,
  `b8d28cb7`) left it unchanged against `c2ec419a`.
- **The audit** (coverage-5b-audit, #767, then its delta to `8b235170`):
  - the leave-one-out null is calibrated: differ 0.017–0.022 at N = 50 against a nominal 0.020, and 0.003 at N = 200
    against 0.005;
  - M1, M2 and M3 are upheld and answered;
  - B-C's operands and guard are folded in;
  - nothing blocks.

  The text from `8b235170` to `c2ec419a` states only the replica set and N, as ruled.
- **K = 10** is cited to arXiv:2106.16210v4 p. 5, with the sentence verbatim and the PDF's sha256 (§1.1). The
  director has not re-read the PDF. Step two's code binding checks the citation against the committed PDF digest.
- **A grid defect,** caught by the lane in its own draft. c2 was first cited to an unrun script whose p_T edges
  differ from the paper's. It is now bound to E_R's grid, which equals the paper's on all 224 bins.

## Rulings

1. **Step one is bound: the design at M.** Nothing runs before step two binds the code.
2. **No universe pass.** The cap is **12.5 CPU node-h**: c2 with the replicas reused or 200 new ones, plus c1.
   - The referee's request is a binned cross-check that locates the 2D shape difference. C2-R1 and C2-R2 answer it
     on the paired replicas.
   - The universe pass would add 21.4 node-h. It would also read `$UNI` in the window that the 2D coverage bulk
     needs before 2026-12-19.
   - Decided now, it is not an outcome-dependent choice. **It is not added after any c2 output is read.**
   - Joseph may override this before the run. The director reports it to him with this binding.
   - `$UNI` is therefore not read by REF-C2C1, and no preservation is needed for it.
3. **The code lane is `limitations-catalog`,** after REF-G1's code. REF-G1 has the earlier hard date, since D_N.npz
   is exposed from 2026-12-18.
   - The code is as §4 lists it, with tests and a mutation harness, then coverage-5b-audit, then step two.
   - If Joseph gives c2/c1's code to his Codex lane for parallel work, the declaration moves with it (§4's last
     line). The director routes the audit and binds as above.
4. **The cluster lane is `limitation-resolver`** for §4's preconditions 3–6:
   - the `libRooUnfold.so` listing and import;
   - E_R's inputs, central product, refinement evidence and Q_R's replica products, listed with sha256 and atime;
   - C-DRAW on one replica.

   Each connect's sha256 comes to the director first. Preconditions 3 and 4 are at 0 node-h. C-DRAW's one replica
   counts against the cap.
5. **Every job** is CPU only and under 12 h, with `--time` written as `HH:MM:SS`. Each connect prints `scontrol`
   TimeLimit after submission and cancels on a mismatch.
6. **The paper and the note.** §1.5's and §2.4's licences bind, and so does §5's "does not license" column, which
   excludes any statement that the inputs or intermediate stages equal the publication's. Any sentence goes
   through the paper lane, a PRD-referee read of the exact wording, and Joseph.

Nothing is submitted, deposited or tagged.

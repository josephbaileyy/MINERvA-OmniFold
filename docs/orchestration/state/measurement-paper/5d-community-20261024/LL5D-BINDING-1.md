# BINDING 1: LL5D, the like-for-like 5D coverage test, its design (director, 2026-11-08)

**Binds the design** [`LL5D-DECLARATION.md`](LL5D-DECLARATION.md), as merged in PR #936 at
**M = `1acdee665ea162b2b5a2026ab620990a116c6092`**. The declaration's sha256 is `6748d41891eff7bb…`, byte-identical
to the audited head `7c7da892`. No code is bound here: nothing runs under this binding.

**Under:**
- `DECISION-20261106-joseph-plateau-next-work.md`, item 2: Joseph's override of 1B's rule (iii)
  (`DECISION-20261102-joseph-1b-redesign.md:78`) for a coverage test built like-for-like;
- `DECISION-20261108-joseph-5d-coverage-and-parallel-studies.md` (#934): read with and without GEANT_Neutron and
  GEANT_Proton, the reading without them primary, fixed before any draw;
- `DECISION-20261108-joseph-ll5d-stop-rule.md` (#939): no stop rule fixed in advance; each STOP goes to Joseph
  unrepaired, and he decides then.

## What the director checked

coverage-5b-audit's NO-GO at `94b0fb3e`/`662224be` on three items, then its GO at `7c7da892`
(https://github.com/josephbaileyy/MINERvA-OmniFold/pull/936#issuecomment-6724498395):
- **C1, the minus2 gate:** new drivers call fd_1b_c2's building blocks unchanged, with layout_minus2, drop2 and
  restrict as named departures and REQUIRED tests m2-a to m2-f;
- **C2, the gate's price:** at THREADS=1 from job 60870880, G(N) recomputed by the auditor;
- **C3:** the bank's 6 GEANT tdw arrays and the dump's 8 universes named apart.

What holds unchanged from the first read: the per-row clip gives every fine-cell denominator ≥ 0 by construction; the
removal of the two bands from C_T is exact; the four-evaluation mapping of the 11-03/11-04 gate carries those rules.
The branch's two later merge commits (`8ff733cb`, `697529cf`) changed only CATALOG, MANIFEST-overrides and MANIFEST.

## Rulings

1. **The design is bound as declared at M:** truths G18 and AR23; the natures and per-row composition; the denominator
   composed and clipped per row (the director's ruling D); C_T rebuilt at each truth; paired readings with and without
   the two bands at the same seeds, the reading without them primary; the receipt, the clipping gate and clipcheck;
   grading by fd_1b_null on the 16 cells; §13's licences.
2. **The director's readings, which Joseph may override:** §8's R8, the joint 1 % false-stop budget over the four
   evaluations (2 tunes × 2 readings) with the 11-04 materiality per evaluation; and the exclusion of the plug-in
   truth, which `FD-1B-STAGED-BINDING-3.md:52` defers to the publication-scope decision (OI-205).
3. **STOPs:** under #939. Each goes to the director and to Joseph unrepaired, nothing relaunches, and no repair is
   declared until Joseph decides; a repair after a STOP is disclosed as chosen after it. An INVALID may be rerun
   unchanged under the director's authority.
4. **The code comes in two amendments,** the director's choice of 2026-11-08:
   - **A1a → binding 2:** calib, gate (the receipt with D1–D3, N1 and T ≤ 0, the gate, the cross terms), m2-a to m2-f,
     and the auditor's RSS low. Audited and bound before §11's steps 3–4.
   - **A1b → binding 3:** unfold, walls, clipcheck, null and readout. Audited and bound before the rebuild, the toys and
     the grading.
   - **A1b implements the declaration as bound at M.** It may not change in response to anything A1a's jobs produce.
     A gate PASS licenses only A1b running as declared; A1b's audit checks that it refers to no A1a output beyond the
     gate's PASS or STOP.
   - fd_1b_c2.py is copied verbatim from `342c0ce5` (branch `decl/1b-staged-a2-1-20261103`, untouched), with a
     blob-digest test and its provenance recorded. ll5d.py's own input builders are a named departure beside
     layout_minus2, drop2 and restrict, with a REQUIRED all-path equality test against `342c0ce5`'s path.
5. **The estimator** is configuration (e), the reported procedure. An ENS1 estimator, if Joseph adopts one, is
   re-pinned by an amendment priced then, reusing none of (e)'s bulk products. LL5D is not citable for the coverage of
   any ENS1 estimator.
6. **The price.** The cap is **148.0 CPU node-h** (§9), with about 60 expected at N = 3,000 and 96 at N = 9,000, under
   half the balance at the last reading (1,698.3 node-h, half 849.1, 2026-11-08 17:10Z). `iris` is re-read at each
   connect, and a cap above half the remaining balance comes back to the director.
7. **The job-name family `ll5d_*`** (ll5d_calib, ll5d_gate_G18, ll5d_gate_AR23, ll5d_pilot, ll5d_bulk_01–10) is new.
   The director names it to every lane with a live fence before the first ll5d_ go, and checks its inputs for overlap by
   real path against the campaigns then running; shared inputs are sequenced, not fenced open.
8. **Each connect** sends its sha256 and path to the director before launch, from a fresh clone at the bound commit
   with empty porcelain. ssh's rc is read unpiped, every `--time` is HH:MM:SS with scontrol's TimeLimit checked, and
   each receipt goes in as a PR.
9. **Wording:** §8 R5, the wording of the two readings and the note's text on the clip, waits for the result, then the
   PRD-referee read, then Joseph. No coverage claim is licensed by this binding.

Nothing is submitted, deposited or tagged.

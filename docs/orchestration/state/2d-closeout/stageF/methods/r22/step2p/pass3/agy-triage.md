# Paper pass 3: agy's agreement read, triaged

`agy/` is agy's read of pass 3's text: each changed passage as a BEFORE/AFTER pair, with a planted control
(`make_agy_pairs.py --paper`). paper-g-03 changes no sentence, only their order, so it has no pair.
- **Control:** 3 of 3 planted negations caught (Q1, Q3, Q4).
- **Silent direction:** the identity filler (Q4) reads SAME in the real file.

| pair | change | flag | disposition |
|---|---|---|---|
| Q1 (PB90) | paper-g-02 | drops "10, 15, or 20 iterations" for "the larger counts tested" | The narrowed form asks for exactly this. The counts print in the note's model-dependence section (ledger P3-2, `N:` probe). F109's reason and scope stay in the paper (`P::`). |
| Q2 (PB98–PB103) | paper-g-06 | drops the precision target, its failure and the cell-by-cell breakdown | The narrowed form limits the cut to this discussion, and each fact prints in `sec_5d.tex` (ledger P3-3, `N:` probes). The envelope's size and meaning stay, with a pointer that names the targets (P3-4). |
| Q3 (PB246) | Option B | GiBUU in an "8-cell subset" block; the caption's "indicated comparison region" | Joseph's decision (#581), not judged. agy reads the base caption, "against the sixteen-cell result", as putting GiBUU on all 16 cells. That reading risk is what Option B removes: GiBUU's ndf of 8 printed already, and the paper's text says "compared on the 8 cells". |

## agy2: the read that counts, on the final text (after the review's five fixes)

**Control:** 3 of 3 planted negations caught (Q4, Q6, Q7). The two identity fillers (Q6, Q7) read SAME in the real file.

| pair | change | flag | disposition |
|---|---|---|---|
| Q1 (PB90) | paper-g-02, with R3-3 | "none of the larger counts" for the three counts, and no "its values" | The narrowed form, tied to the cited comparison, which covers 10, 15 and 20 and gives one bound, not a value per count (review R3-3). The counts print in the note (P3-2, `N:`). |
| Q2 (PB96) | R3-2 | the heading drops "the precision target" | The subsection no longer discusses the target, which moved to the note under paper-g-06 (P3-5). agy itself names the move. |
| Q3 (PB98–PB103) | paper-g-06 | the target, its failure and the cell breakdown dropped | As in `agy/`: the narrowed cut, with each fact homed in `sec_5d.tex` (P3-3, `N:`). |
| Q4 (PB246) | Option B | GiBUU in an "unsupported" 8-cell block | Not unsupported: the paper prints "GiBUU is compared on the 8 cells with $\pPar<\fvval{h2-mid-pz}$~GeV/$c$ only" (`paper_body.tex:233`, `:238`). Joseph's decision (#581), not judged. |
| Q5 (PB260) | R3-1 | "of \nsec{sec:gbdt-model-dependence}" added to "the precision target" | The target is now defined only in that note section (P3-3, P3-6, `N:`). The paper's own definition left under paper-g-06, so the pointer is what keeps the sentence true. |

<!-- absence-ok: quotes printed paper sentences and agy's flags; not a claim that something has not been run -->

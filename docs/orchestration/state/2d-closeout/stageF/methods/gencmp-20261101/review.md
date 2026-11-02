# The GENCMP paper round: the independent two-direction review, with dispositions

**The reviewer:** a fresh general-purpose subagent, read-only. It was given:
- the diff `dfa137370..647977f67`;
- the decision record (#651), FD-GENCMP-REPORT.md, the declaration, the consult and the readouts;
- the director's three rulings.

It was not given the writer's conclusions. It re-derived every new number from the readout JSON with its own script.

**The two directions:**
- truth: each new or changed statement against its source;
- loss: no true fact dropped, and no sentence elsewhere left false.

It also checked completeness against the decision's items 1–4 and 6.

**The result:**
- No High finding. Every printed number matches its readout. That covers Table IV in both column groups, the carbon values, GiBUU's rise and fall, 44.2 against 45.3, native NuWro on both routes, 0.063 and 0.07, the seed spread, +2.1 %, the 3D 0.2–0.8 % and 0.17, the 1.1e-7 share, the falls with the block (3.6–29.3 % and 7.4–40.4 %), the abstracts' 107–229 and GiBUU's 48.
- The redrawn figure plots f/g from `defs.json` for the four rebuilt predictions, and Stage G's for Tune v1.
- Three Medium and six Low findings, all fixed in `4b5ec82ed`. Item 6 was partial and is now done (finding 3).

| # | sev. | finding | disposition |
|---|---|---|---|
| 1 | Medium | the paper's scoping sentence named "the sensitivities", but the flux bootstrap in the same paragraph is described there as not a sensitivity, so its "each 16-cell χ²" read as Table IV's | FIXED: "The sensitivities and the flux bootstrap that follow were computed for the predictions in their generator definitions …". It is still one sentence in one place, as the director's ruling 1 asks |
| 2 | Medium | GiBUU's table note used σ_c without defining it for a paper reader | FIXED: "with σ_c a cell's standard deviation under the null distribution of the note's joint tests". That is sec_joint.tex:327's definition (NuWro's B = 1751 null) |
| 3 | Medium | "All predictions are per nucleon of their target" was unchanged, though decision item 6 lists it. After "generated on carbon", "their target" reads as carbon | FIXED: "… per nucleon of their target: CH, or carbon for NuWro and GiBUU outside the sixteen-cell comparison". Scoped rather than replaced with "of CH", because the comparisons of sec:central still use carbon (ruling 3) |
| 4 | Low | the GENIE-hydrogen clause lacked its label (a thin sample, so the spread is largely its noise; declaration §2). It also set 44.2 beside 45 → 48 (analysis definitions) without GiBUU's own-hydrogen value in the generators' definitions | FIXED: "against 45.3 on carbon and 47.5 with its own hydrogen (all in the generators' own definitions; GENIE's hydrogen sample is thin, so this spread is largely its noise)" |
| 5 | Low | "on the sixteen (reported) cells, GiBUU's total χ² rises": GiBUU is compared on 8 cells | FIXED in sec_joint.tex, sec_fived16.tex ("in the sixteen-cell comparison … on its eight cells") and the primer ("on broader cells") |
| 6 | Low | "an average nucleon mass where the generator records none": declaration §3 also applies it to GENIE 2p2h, whose hitnuc is a cluster code | FIXED in the paper and the note: "where the generator records no single struck nucleon" |
| 7 | Low | the probe diagnostic called its hydrogen chunk a production sample's; it is MP3-B's | FIXED: "from one chunk each of the production carbon sample and the free-proton sample" |
| 8 | Low | the figure sidecar's per-item `source` fields named Stage G's readout for the substituted g and labels | FIXED in fd_gencmp_figures.py. The redrawn PDF is byte-identical (`32a7557c`), and the sidecar now names `defs.json` for g and the wrapper for the label |
| 9 | Low | `g-ch-hweight` prints in GiBUU's table note, but only NuWro's label is asserted; no GiBUU readout states the weight. Separately, table4's docstring said every sample "passed B0 and B2", while B2 is "n/a" for 4 of 6 | KEPT, documented. No GiBUU readout states the weight, so nothing can assert it; the comment now cites FD-GENCMP-DECLARATION.md §2, the construction for both. The docstring now says "B2 where it applies" |

**Checks the reviewer ran that passed:**
- **Values:** every g-, gs-, gdef-, gnat- and g3d- value against the readouts.
- **The C_model clause:** the config sha `078df3b6` and the samples `475a2871` and `48917692` (declaration A1).
- **Scoping:** every use of gs-, sens-, fb- and diag- in the note is scoped. g- keys print only where the new predictions are meant.
- **Loss:** no leftover "on carbon, no correction" or neutron-mass sentence about the sixteen-cell comparison in the seven files.
- **Byte identity:** the abstracts' wording unchanged, and `paper_body.tex`'s 2D-quadrant sentence untouched (item 5).
- **Builds:** no "??" and no "[PENDING" in either PDF.

**Added after the review:** six self-test plants in `make_values_fived16.py`, one for each new assertion:
- a sample that failed B0;
- a Table IV χ² that is not its corner;
- a 0.08σ move;
- GiBUU's GENIE-hydrogen total above carbon;
- native NuWro disagreeing;
- a quadrant above the 3D value.

Each is refused, and a traceback check confirmed that its own guard refuses it, not an earlier one.

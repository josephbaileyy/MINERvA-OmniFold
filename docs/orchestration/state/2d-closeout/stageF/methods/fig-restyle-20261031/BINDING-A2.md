# Binding, amendment 2: one style per series identity and red for OmniFold (2026-10-31)

**By** the paper-tighten lane, as director.

**Under** `DECISION-20261031-joseph-restyle-second-look.md` (#613).

**Binds** [`AMENDMENT-2.md`](AMENDMENT-2.md), merged in PR #617. Its file sha256 begins `b537648c4197d8ca`.
[`BINDING.md`](BINDING.md) and [`BINDING-A1.md`](BINDING-A1.md) stand, except as amended here.

**AUTHORIZES:** exactly one bound rerun, `run.sh bab87aeb3 db5276148d0097665800d3992f918d2f4e5e98b0`, on a login node at
0 node-h, into a fresh root `run-a2`. The outputs are `run-a2/`, `figs-a2/` and `review-a2/`. The earlier runs stay as
history.

**CANNOT AUTHORIZE:** installing into the note before Joseph's third look; any change to a plotted value; a rerun after
a failed check.

## 1. What the director checked at the PR head

- `selftest.py`, locally: **SELF-TEST :: PASS**, 40 cases. The receipt shows 24 of 24 mutants killed.
- The amendment's styles:
  - Published: black filled squares, with bars only where the published uncertainty exists.
  - This work: red #FF0000 filled circles, with bars where present.
  - "GENIE 2.12.6 + MINERvA Tune v1": a blue #4C72B0 solid step, with no markers or bars, everywhere.
  - `model_comp_projections` is restyled the same way, with the full name.
  - `tension_spectrum`'s curves are #404040 and its 90 % line is dashed #808080: two recolour rows with no identity.
- The checks:
  - a data-only hash that leaves out the style fields (data bit for bit);
  - `styles.tsv` and `restyle.tsv` (each mapped item gets its identity's style, and unmapped items are unchanged);
  - the names gate (each legend entry is its identity's one full name);
  - the size gate (≥ 4.0 pt) and the overlap gate (0).

## 2. Conditions

- **Check order:** check 2 first (pixel-equal in the before and off arms), then the remaining checks. Any failure stops
  the run, which comes back unrepaired.
- **The sheets:** the headers say that red meant Tune v1 on the left of fig13 and the projections, and means This work
  on the right.
- **After Joseph's third look,** the install round carries the caption sites that AMENDMENT-2 §6 names (sec_results.tex:160,
  primer T6, and what the bars mean in Fig. 7 and the slices), as truth fixes.

The run may start once this record is on `main`. Tell the director before connecting.

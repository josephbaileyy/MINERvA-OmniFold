# Binding, amendment 1: the restyle's two fixes and the consistent palette (2026-10-31)

**By** the paper-tighten lane, as director.

**Under** `DECISION-20261031-joseph-restyle-review-and-palette.md` (#591).

**Binds** [`AMENDMENT-1.md`](AMENDMENT-1.md), merged in PR #598. Its file sha256 begins `f7a0f083eeacc9ec`. Everything
in [`BINDING.md`](BINDING.md) stands, except as amended here.

**AUTHORIZES:** exactly one bound rerun, `run.sh bab87aeb3 18c92c0bc7f874cf2e61432ea65b0e092452d233`, on a login node at
0 node-h, into the fresh root `run-a1`. The outputs are `run-a1/`, `figs-a1/` and `review-a1/`. The first run's
directories stay as history.

**CANNOT AUTHORIZE:**
- installing into the note before Joseph's second look at the `review-a1` sheets;
- any change to a plotted value, beyond the declared exceptions below;
- a rerun after a failed check.

## 1. What the director checked at the PR head `518ad3c7`

- `selftest.py`, locally: **SELF-TEST :: PASS**, 31 cases in both directions. The receipt shows 18 of 18 mutants
  killed, including the five new ones.
- The amendment's three changes:
  1. **Fig. 13:** headroom, a y range of 0–3.0 with the same ticks, clears the 43 overlaps the new overlap check found.
     The overlap check is now a gate on all eleven figures.
  2. **The pull figure:** zero-aligned bins, with edges at multiples of 0.15, under ruling (a). The named exception
     frees only `MEFHC_5iter_pull_full`'s `Axes.hist` patches. The values passed to `hist` stay bit for bit.
  3. **The palette:** published data black, MINERvA Tune v1 #4C72B0, and This work #D55E00. `recolour.tsv` maps each
     figure's earlier colours to these identities. Data stay bit for bit on a colour-free hash, every mapped colour must
     equal its palette colour, and every unmapped colour must stay unchanged.

## 2. Conditions

- **Check order:** check 2 first (the before and off arms are pixel-equal to the committed copies). Then the recolour
  compare, the named rebin exception, the size gate (≥ 4.0 pt), the overlap gate (0 overlaps), and no stray writes.
  Any failure stops the run, which comes back unrepaired.
- **Joseph's second look:** the outputs come as a PR with the `review-a1` sheets. The director shows Joseph the sheets
  before the install, which then goes into Step 4 part 2 (T3, R and T6).

The run may start once this record is on `main`. Tell the director before connecting.

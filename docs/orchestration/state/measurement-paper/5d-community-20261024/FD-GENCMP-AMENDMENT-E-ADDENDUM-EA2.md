# ADDENDUM E-A2 to GENCMP amendment E: the two hydrogen flags leave the corner figures' legend, and the figures are redrawn from E-1's committed bytes (2026-11-02)

**By** the limitation-resolver lane (Claude), for the director to bind by addendum to
[`FD-GENCMP-AMENDMENT-E-BINDING.md`](FD-GENCMP-AMENDMENT-E-BINDING.md).

**Under:** `DECISION-20261102-joseph-caveat-cut-list.md` item 1, move MV07F, and the director's message of 2026-11-02
that scoped this addendum. The decision record is merging separately, and this addendum cites it by name.

**Supersedes:**
- §4's legend-qualifier list for `gencmp-chdefs`, and the same list in §12 (addendum E-A1);
- review row A6 ("hydrogen: supplement FLAGGED" added to NuWro's legend and to the checker's declared name).

**MEASURES:** nothing new. The figures redraw amendment E's committed E-1 with-arm readouts. Every plotted number is
unchanged, and control D checks it.

**CANNOT AUTHORIZE:**
- a readout, covariance or claim change;
- a paper or caption edit. Re-pinning `FIGURES` in `make_values`, dropping the caption sentences, and writing Table III's
  footnote and the note's text are the paper lane's.

## 1. What changes

**The legend.** The `gencmp-chdefs` prediction set drops its two hydrogen qualifiers. They are "hydrogen: supplement
FLAGGED" for NuWro and "hydrogen: closure B3 failed" for GiBUU. The facts move to Table III's footnote and the note.

**What the legend keeps,** the paper lane's analysis:

| prediction | qualifiers drawn (E-A1) | qualifiers drawn (E-A2) |
|---|---|---|
| GENIE 2.12.10 CV, no MEC | none | none |
| GENIE 2.12.10 + Valencia MEC | none | none |
| NuWro 21.09 | "CH"; "hydrogen: supplement FLAGGED" | **"CH"** |
| GiBUU 2019 | "CH"; "hydrogen: closure B3 failed"; "p_parallel < 4.5 cells only" | **"CH"; "p_parallel < 4.5 cells only"** |
| MINERvA Tune v1 | "prior (not an independent prediction)" | **"prior (not an independent prediction)"** |

**K7's required strings for the set** become "prior (not an independent prediction)" and "p_parallel < 4.5 cells
only". The two flags still stand in NuWro's and GiBUU's labels (`fd_gencmp_e.CHDEFS`, and so in every committed E-1
readout). K7 does not require them on the legend, so it holds.

**The checker** (`fd_g_figures_check.PREDICTION_SETS["gencmp-chdefs"]`) declares the drawn names independently. They are
"NuWro 21.09: CH" and "GiBUU 2019: CH; $p_\parallel$ < 4.5 cells only", and its MUST strings match K7's. The existing
test that the checker's declared names equal the figure tool's legend text, in both sets
(`test_fd_gencmp_e.Sets.test_figure_legend_equals_the_checkers_declared_name_in_both_sets`), holds unchanged.

**The stage-g set** (today's default figures) is unchanged. It is the same object as before
(`test_fd_gencmp_ea2.Sets.test_stage_gs_set_is_unchanged`).

## 2. The redraw

`nd-unfolding/fd_gencmp_ea2.py --out-dir <dir>` (login node, 0 node-h) runs from committed bytes only.

**1. The chain's own figure entry.** That is `fd_gencmp_e.BOOT`: `fd_g_figures.run` with the committed pins file
`fd/gencmp-e/rerun1/chain/pins/chdefs-with-figures.json` and the committed prediction set
`…/pins/predictions-chdefs.json`.
- The argv is the committed ratio sidecar's (ratio, modes and sens; data over prediction; GiBUU on its own axes;
  "C_resp + C_PL5D"; `--prediction-set gencmp-chdefs`), with only the paths changed.
- The six inputs are E-1's with-arm readouts (`…/chain/chdefs/with/readout/`), the with-cpl F0b readout and the H2
  definition. Each is required at the digest of both the pins file and the committed sidecar's `inputs_sha256`, before
  anything runs.

**2. `fd_g_figures_check.py --prediction-set gencmp-chdefs`** on the new directory.

**3. Control D, new**, for each of the three sidecars against amendment E's committed one
(`…/chain/chdefs/with/figures/`).
- **The rule.** Everything is equal except argv, code, versions, the PDF's digest and bytes, and the file name. That
  covers the options, inputs, controls, the `plotted` axes, legends, keys and every plotted item. The one exception is
  the `text` of items drawn from a prediction's label.
- **The label texts.** Each must equal the committed text with "; hydrogen: supplement FLAGGED" and "; hydrogen: closure
  B3 failed" removed, and must carry neither flag. At least one label text per figure must change.
- **Its record** is written as `control_d.json` beside the figures.

**All three figures are redrawn.** The sens figure's prediction labels carry the flags too: committed `sens` items 25
and 35. The director named the ratio figure (paper Fig. 4) and the note's modes figure, and this draws all three. The
paper lane uses the ones it prints.

**A local development run** (this lane's laptop, matplotlib 3.10.1; not a binding run) on the committed bytes gave:
- `fd_g_figures_check`: "OK: 498 checks, 0 failed, 3 sidecars";
- control D: PASS on all three, with 2, 1 and 2 label texts changed (ratio, modes, sens) and no other difference;
- the ratio PDF's legend, read by eye: "NuWro 21.09: CH" and "GiBUU 2019: CH; $p_\parallel$ < 4.5 cells only".

## 3. The run, once bound

- **`$R`** = `/pscratch/sd/j/josephrb/gencmp-ea2-<date>/`, which must not exist beforehand.
- **Deploy.** A fresh clone at the bound commit M‴ into `$R/deploy`. Its porcelain must be empty before and after, and
  the blobs of §5 are verified.
- **The command,** on login37 with root_6_28 activated by prefix, as amendment E's chain ran (matplotlib 3.10.8):

  ```bash
  cd $R/deploy && python3 -I -B nd-unfolding/fd_gencmp_ea2.py --out-dir $R/figures-a2 \
    > $R/logs/ea2.out 2> $R/logs/ea2.err; echo "rc=$?" >> $R/logs/ea2.out
  ```
- **Reads.** Every input is a committed file in the run's own fresh clone, so no pre-existing pscratch file is read and
  no atime moves. O_NOATIME has nothing to apply to.
- **Writes:** only under `$R`. Nothing goes to CFS. HPSS is not needed: every product is committed.
- **Committed in the report's PR:** the three PDFs and sidecars and `control_d.json`, under
  `fd/gencmp-e/rerun1/chain/chdefs/with/figures-a2/`, with the logs and the deploy record under `fd/gencmp-e/a2/`.
- **Stop rule.** Any refusal or non-zero exit is reported unrepaired.

## 4. Tests and mutation receipt

- **`tests/test_fd_gencmp_ea2.py`, 11 tests.**
  - What the legend and K7 drop, and what they keep.
  - The labels still carry the flags, and the stage-g set is unchanged.
  - Control D in both directions: it holds on the flag removal alone, and fails on a changed number, option, legends
    block, other text or dropped item. It counts no change when the flag stays.
  - The redraw end to end from the committed bytes.
  - Refusals: an existing out-dir, a changed input, a committed sidecar with no flag to remove, and a failing figure
    check.
- **Existing suites, unchanged and passing:** `test_fd_gencmp_e.py` (43) and `test_fd_g_figures.py` (47).
- **Mutation receipt:** `fd/gencmp-e/a2/mutants_ea2.py` and `mutants_ea2.log`. 16 mutants across `fd_g_figures.py`,
  `fd_g_figures_check.py` and `fd_gencmp_ea2.py`, run against `test_fd_gencmp_ea2` and `test_fd_gencmp_e`: **killed 16
  of 16**, files restored.
  - The first pass left 2 survivors: "no change accepted", and "figure check skipped". The two refusal tests above were
    added to kill them.

## 5. The code bound (blob digests at this branch's head, recorded in the PR)

Recorded in the PR body at its head: `fd_g_figures.py`, `fd_g_figures_check.py`, `fd_gencmp_ea2.py`,
`tests/test_fd_gencmp_ea2.py`, `fd_gencmp_e.py` (unchanged) and this file.

## 6. Limits

- **A stale comment in bound code.** `fd_gencmp_e.py`'s comment on `CHDEFS` (lines 68-69) says the legend set "carries
  the same strings" as the labels' qualifiers. After E-A2 it carries a subset. The comment is left unedited so that
  amendment E's bound blob does not change; this addendum records the change.
- **The nopl arm's figures are not redrawn.** The paper prints the with arm.
- **What this does not change:** the readouts, every number, R0, XC and C-R.

Nothing is submitted, deposited or tagged.

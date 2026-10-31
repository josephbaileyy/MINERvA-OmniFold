# Amendment 1's bound rerun: report (2026-10-31)

**Under** [BINDING-A1.md](BINDING-A1.md) (#601), which authorizes exactly one rerun of
`run.sh bab87aeb3 18c92c0bc7f874cf2e61432ea65b0e092452d233` into `run-a1`.

**Every check passes. Nothing is installed in the note.** The figures wait for Joseph's second look at
`review-a1/`.

## The run

- **Checked first:**
  - BINDING-A1.md is on main;
  - `AMENDMENT-1.md` at the pin hashes to `f7a0f083eeacc9ec…`;
  - the pin contains the bound PR head `518ad3c7` and is identical to it on `2d-unfolding/`, `technote_style.py`,
    `tools/`, `palette.tsv` and `recolour.tsv`.
- **Driver:** `run.sh`, run from a checkout detached at the pin, with a clean tree.
- **Where:** login37, with no Slurm and 0 node-h.
- **Deploys:** a fresh root, `/pscratch/sd/j/josephrb/2d-closeout-restyle-20261031/run-a1`, with base `bab87aeb37d2`
  and bound `18c92c0bc7f8`.
- **Arms:** "before" (the base's producers), "off" (the bound producers without the option) and "after" (with the
  amended restyle). The "after" arm took 50 s.
- **Inputs:** E_R `a5c13fc3…` and the published covariance `6c6dce72…`, read-only.
- **No stray writes:** 0 files under `$A` newer than each arm's marker. Nothing went to CFS or HPSS.

## The checks ([run-a1/CHECKS.txt](run-a1/CHECKS.txt): `RUN CHECKS :: PASS`), in the bound order

| check | result |
|---|---|
| 2, identity | 22 of 22 pixel-equal: "before" and "off" against the committed copies |
| 3, data and palette | `COMPARE :: PASS` with `--recolour recolour.tsv --palette palette.tsv`. Every figure's data is bit for bit on the colour-free hash, each mapped series has its palette colour, and every other colour is unchanged |
| the named exception | `MEFHC_5iter_pull_full` only: "bins free: hist values equal" |
| 4, 5 | the reports and logs are equal after path replacement, with the same inputs and sha256 |
| 6 | 0 stray files in each arm |
| 7, printed text | 5.00–5.92 pt per figure, against the 4.0 pt floor (`TEXTSIZE :: PASS`), with no raw `_` or `^` |
| overlaps | `OVERLAP :: PASS`: 0 in each of the eleven |

## Files

- `run-a1/`: each arm's PDFs (no PNGs), captures, logs and `SHA256SUMS`, and `CHECKS.txt`. The repository ignores
  `.npz` and `.log` by default, so the capture arrays and step logs are force-added.
- `figs-a1/`: the eleven amended PDFs, byte-equal to `run-a1/after/out/`, with `SHA256SUMS`. These are the files the
  install uses.
- `review-a1/`: Joseph's second-look sheets, one page per figure, with `SHA256SUMS`. The committed copy is on the left
  and the amended figure on the right, both at the printed width.
- The first run's `run/`, `figs/` and `review/` stay as the history.

## Next, not done here

1. Joseph's second look. The director shows him `review-a1/`.
2. After his word: STEP4 part 2, which is the install (DECLARATION.md §5 with `figs-a1/`), T3, and T6 (the primer's
   "red" to "blue").

# Amendment 2's bound rerun: report (2026-10-31)

**Under** [BINDING-A2.md](BINDING-A2.md) (#621), which authorizes exactly one rerun,
`run.sh bab87aeb3 db5276148d0097665800d3992f918d2f4e5e98b0`, into `run-a2`.

**Every check passes. Nothing is installed in the note.** The figures wait for Joseph's third look at `review-a2/`.

## The run

- **Checked first:**
  - BINDING-A2.md is on main;
  - the pin `db5276148` is main's merge of the amendment's PR (#617), so `AMENDMENT-2.md` at the pin is the bound
    text.
- **Driver:** `run.sh`, from a checkout detached at the pin with a clean tree.
- **Where:** a login node (saul), with no Slurm and 0 node-h. The director was told before the connection.
- **Deploys:** a fresh root, `/pscratch/sd/j/josephrb/2d-closeout-restyle-20261031/run-a2`, with base `bab87aeb37d2`
  and bound `db5276148d00`.
- **Arms:** "before" (the base's producers), "off" (the bound producers without the option) and "after" (with the
  amended restyle).
- **Inputs:** E_R `a5c13fc3…` (`xsec.root`) and the published covariance `6c6dce72…`, read-only (`opened.tsv` of each
  arm).
- **No stray writes:** 0 files under `$A` newer than each arm's marker. Nothing went to CFS or HPSS.

## The checks ([run-a2/CHECKS.txt](run-a2/CHECKS.txt): `RUN CHECKS :: PASS`), in the bound order

| check | result |
|---|---|
| 2, identity (first) | 22 of 22 pixel-equal: "before" and "off" against the committed copies |
| 3, data, palette and styles | `COMPARE :: PASS` with `--recolour`, `--palette`, `--styles` and `--restyle`. Every figure's data is bit for bit on the data-only hash, and every figure reads "colours as the palette maps them, line styles as declared" |
| the named exception | `MEFHC_5iter_pull_full` only: "bins free: hist values equal" |
| names | `NAMES :: PASS`: 18 legend entries in 11 figures, each an identity's one name or a declared non-series entry |
| 4, 5 | the reports and logs are equal after path replacement, with the same inputs and sha256 |
| 6 | 0 stray files in each arm |
| 7, printed text | 5.00–5.92 pt per figure, against the 4.0 pt floor (`TEXTSIZE :: PASS`), with no raw `_` or `^` |
| overlaps | `OVERLAP :: PASS`: 0 in each of the eleven |

## Files

- **`run-a2/`:** each arm's PDFs (no PNGs), captures, logs and `SHA256SUMS`, and `CHECKS.txt`. The repository ignores
  `.npz` and `.log`, so the capture arrays and step logs are force-added.
- **`figs-a2/`:** the eleven amended PDFs, byte-equal to `run-a2/after/out/`, with `SHA256SUMS`. These are the files
  the install uses.
- **`review-a2/`:** Joseph's third-look sheets, one page per figure, with `SHA256SUMS`. The committed copy (the
  "before" arm, pixel-equal to it) is on the left, and the amended figure is on the right, both at the printed width.
  - The sheets of fig13 and the two p_T and p_∥ projections carry the header "Red means Tune v1 on the left (the
    committed copy) and This work (OmniFold) on the right."
  - `model_comp_projections` has no header, because its committed copy already drew This work in red (`#C44E52`).
- **History:** the first run's `run/`, `figs/` and `review/`, and amendment 1's `run-a1/`, `figs-a1/` and `review-a1/`,
  stay.

## For Joseph's look

- **What changed:**
  - This work (OmniFold) is now drawn as red filled circles, in every figure;
  - Published is drawn as black squares;
  - "GENIE 2.12.6 + MINERvA Tune v1" is a blue line with no markers;
  - the legend names are the same everywhere;
  - the tension spectrum is grey.
- **What to look at:** in `model_comp_projections`, the Published squares sit almost wholly behind This work's circles,
  because the two agree to about 1 %. That is the data, not a drawing defect.

## Next, not done here

1. Joseph's third look at `review-a2/`.
2. After his word, the install round:
   - DECLARATION.md §5 with `figs-a2/`;
   - STEP4's T3 and T6;
   - AMENDMENT-2 §6's caption truth fixes (sec_results.tex:160; what the bars mean in Fig. 7 and the slices).

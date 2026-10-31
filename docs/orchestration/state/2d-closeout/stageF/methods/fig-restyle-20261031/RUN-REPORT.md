# The bound restyle run: report (2026-10-31)

**Under** [BINDING.md](BINDING.md) (#586), which authorizes exactly one run of
`run.sh bab87aeb3 a2f2394d3d0cb59381ea6957673b6d75185becd6`. **Every check passes. Nothing is installed in the note.**
The restyled figures wait for Joseph's review of the sheets in `review/`.

## The run

- **Driver:** `tools/run.sh` at `a2f2394d`, from a checkout detached at that commit, with a clean tree.
- **Checked first:**
  - `a2f2394d` contains the bound PR head `03c3efc6`, and is identical to it on `2d-unfolding/`, `technote_style.py` and
    `tools/`;
  - `DECLARATION.md` at the pin hashes to `8c71209c9f4d0a66…`, as BINDING.md records.
- **Where:** a Perlmutter login node (login37), with no Slurm and 0 node-h.
- **Deploys:** two clean deploys in `/pscratch/sd/j/josephrb/2d-closeout-restyle-20261031/run/`. That run root did not
  exist before the run. The deploys are:
  - `base/deploy`, from `bab87aeb37d2…`;
  - `bound/deploy`, from `a2f2394d3d0c…`.
- **The three arms** each ran the six figure steps through `capture.py`:
  - "before": the base's producers;
  - "off": the bound producers without the option;
  - "after": the bound producers with `--style restyle-2026-10`.
  The "after" arm took 48 s (`run/after/logs/run.txt`, `steps.tsv`).
- **Inputs, in every arm:** E_R `a5c13fc38d64242b…` and the published covariance `6c6dce72050bb8f1…`
  (`logs/inputs.sha256`).
- **Nothing else was written.** In each arm, 0 files under `$A/2d-unfolding` or `$A/docs` are newer than the arm's
  marker. Nothing went to CFS or HPSS.
<!-- absence-ok: run-root and stray-write statements are preconditions run.sh enforces and counts (it refuses an existing run root; find -newer the marker), not claims that a result does not exist -->

## The checks ([run/CHECKS.txt](run/CHECKS.txt): `RUN CHECKS :: PASS`)

| check | result |
|---|---|
| 2, identity | 22 of 22 pixel-equal at 300 DPI: the eleven PDFs of "before" and of "off" against the committed copies in `re2-integration/figs/` |
| 3, data | every captured figure's data artists, with their RGBA, equal before and after (`COMPARE :: PASS`) |
| 4, other outputs | `model_comp_report.txt`, `tension_report.txt` and every step's log equal, after the run paths are replaced |
| 5, inputs | the same opened files, with the same sha256, in both arms |
| 6, stray writes | 0 in each arm |
| 7, printed text | smallest per figure, 5.00–5.92 pt, against the 4.0 pt floor (`TEXTSIZE :: PASS`); no `_` or `^` in the text of the eleven restyled PDFs |

## Files

- `run/before/`, `run/off/`, `run/after/`: each arm's PDFs (no PNGs), its captures (`capture/<step>/*.npz`, `*.json`,
  `*.textsizes.tsv`, `opened.tsv`), its logs and its `SHA256SUMS`. `run/CHECKS.txt` holds the checks.
- `figs/`: the eleven restyled PDFs, byte-equal to `run/after/out/`, with `figs/SHA256SUMS`. They are the new files
  that integration installs and that the G rows will be re-pointed to (DECLARATION.md §5.2–§5.3).
- `review/`: Joseph's eleven sheets (`tools/sheets.py`), one page each, with `review/SHA256SUMS`. Each shows the
  committed copy on the left and the restyled figure on the right, both at the figure's printed width.

## Next, not done here

1. Joseph's review of `review/`; the director shows him the sheets.
2. Only after his review: integration as DECLARATION.md §5 sets out:
   - the install;
   - `DIGESTS.tsv` and the re-pointed G rows;
   - the note, primer and paper builds;
   - the `figdiag` re-crop as a record.
3. The next note round's truth fixes: Fig. 13's colour, and Fig. 14's "no printed titles".

# The note figure's "rms" relabel: package (2026-11-17, cov2d)

**Under** [DECISION-20261116-joseph-paper-batch.md](../../../../../DECISION-20261116-joseph-paper-batch.md) item 16
("RMS" becomes "standard deviation": the printed 0.535 is `numpy.std`; the value is unchanged) and the methods-short
[FOLLOW-UP-DURING-BEN-REVIEW.md](../methods-short-20261109/FOLLOW-UP-DURING-BEN-REVIEW.md) row 2. The director gave
this package to cov2d on 2026-11-17.

**Status.** Run and installed (section 7).
- The director's go covered connect `d78007ac` at PKG 110a90e8.
- The run passed on 2026-11-17, and check_sd.py passed all 16 checks.
- The note's figure is now b01c1b6c, installed by install_pin.py.
The install (section 5) follows the run, its record and `check_sd.py` PASS.

**Scope.** This package covers the note figure only: `docs/analysis-note/figures/MEFHC_5iter_pull_full.pdf`, note
Fig. 8 (`fig:pull`, `sec_results.tex:64`). Its histogram panel prints `rms =0.54`. Section 6 lists the other places
that print "RMS" and are not in scope.

## 1. The change

The change is to `2d-unfolding/compare_to_paper_fullcov.py`, 1dd5ff52 → 7e641754
([compare_to_paper_fullcov.py.diff](compare_to_paper_fullcov.py.diff)):
- a flag, `--sd-label`, which is off by default;
- with the flag, the label line of the histogram panel reads `SD = 0.54` in place of `rms =0.54`.

Without the flag, the producer draws the installed figure: the "off" arm checks this pixel for pixel (section 3, K2).
The printed log never changes. Its line `pull mean / rms : 0.060 / 0.535` stays, so every reader of the log is
unaffected (K3 compares the logs byte for byte).

**Why "SD" and not the full words.** The label box sits in the upper left of the histogram. Drawn with "standard
deviation = 0.54", the box reaches the zero bin's bar, and the restyle's overlap gate fails. The layout probe on
run-a2's captured arrays showed this, and `test_check_sd.sh`'s long-words mutant keeps it as a test. "SD = 0.54" is as
long as "rms =0.54". The box keeps its place and size, because its widest line is the χ² line. The same batch's Fig. 1
B′ prints "SD 0.535" in its panel. The label is one string in the producer. If the director or Joseph wants other
words, they need a box that fits, which is a layout change.

## 2. The run

[connect-sd.template.sh](connect-sd.template.sh) is filled by [fill_connect_sd.py](fill_connect_sd.py) from git at the
package commit PKG. The connect is one login-node script with no Slurm and 0 node-h. It follows the restyle's method
(fig-restyle-20261031/DECLARATION.md §3–4) for one figure, with the elements the director asked for:
- **Fence.** RE-2-shapes rev 3's, verbatim. It runs at the start and again before the arms, refuses every josephrb job
  that is queued, running or unended since 2026-11-01, and fails closed on any query error or on the group C marker.
- **Input sha.** E_R (`partb/out/ER/xsec.root`, a5c13fc3) and the published covariance (6c6dce72) are hashed with
  O_NOATIME and must equal run-a2's `inputs.sha256`. The producers then read them plainly through ROOT, as run-a2 did.
- **Fresh clone.** The deploy is a new clone at PKG under `/pscratch/sd/j/josephrb/note-pullsd-20261117`, which must
  not exist, and it must be clean.
  - The "before" tree is a `git archive` of db5276148 (fig-restyle's bound commit) from that clone.
  - Twelve code files are checked by sha256: the producer at PKG and at the base, boxes.py, the restyle's capture,
    artists and overlap tools, and restyle_2026_10, technote_style and reported_cells in both trees.
- **Three arms.** Each is the producer through [boxes.py](boxes.py) and the restyle's `capture.py`, with run-a2's argv
  (only the output paths change). Each arm has its own working directory, TMPDIR and MPLCONFIGDIR, runs under nice
  19 with one thread, and stops at 300 s.
  - **before:** the base producer (1dd5ff52) with `--style restyle-2026-10`. This is the installed figure's producer.
  - **off:** the package's producer with the same argv.
  - **after:** the package's producer with `--sd-label` added.
- **No stray writes.** Nothing may be newer than the marker under the shared checkout's `2d-unfolding` and `docs`,
  the deploy or the base tree. The deploy must still be clean after the arms.
- **Fetched back:** `before/`, `off/`, `after/` (no PNGs), `SHA256SUMS`, `code.sha256`, `inputs.sha256`,
  `environment.txt` and `logs/connect.log`.

`boxes.py` runs `capture.py` unchanged, with the same argv, and adds one record. After each save it writes where
every text and axes sits, in figure-fraction coordinates. It draws nothing differently; it reads the figure after the
save.

## 3. The checks ([check_sd.py](check_sd.py), on the laptop after the fetch)

| check | what must hold |
|---|---|
| K1 | the installed figure is fd84d992 |
| K2 | identity: "before" and "off" rasterize at 300 DPI to the installed figure's pixels (the restyle's raster.py) |
| K3 | compare.py, "before" against "after" and against "off": every data artist bit for bit, colours and styles included; the step log byte for byte; the same inputs and digests |
| K4 | "off" draws "before"'s texts; "after" draws them too but one, which is "before"'s with "rms =" replaced once by "SD = " |
| K5 | "off"'s boxes are "before"'s; "after"'s are too, every axes and every text box, except the changed text's own extent, which lies inside its unchanged bbox patch |
| K6 | "before" and "after" differ only inside the label's box (2 px margin at 300 DPI); the left half, which make_figures.sh crops for paper_validation_residual.pdf, is pixel-equal |
| K7 | the restyle's gates on "after": overlap.py, textsize.py at 4.0 pt, no raw `_` or `^`; the PDF's text has the new label, not the old |
| K8 | "after"'s page is 864 × 360 pt (make_figures.sh asserts it before the crop) |

## 4. Tests (laptop, no cluster access)

- **[test_check_sd.sh](test_check_sd.sh)**, output in `test_check_sd.out.txt`. The three arms are drawn by
  [toy_pull.py](toy_pull.py). It runs each deploy's own plotting block, `# Summary plot.` up to the save, on run-a2's
  captured pull map and 205 values, through boxes.py and capture.py.
  - The clean run passes all 16 checks.
  - Ten mutants each fail the check named: one ulp (K3), one more log line (K3), another input (K3), a changed x label
    (K4), no flag (K4), the box moved (K5 and K6), the flag in "off" (K2), a wrong installed digest (K1) and the full
    words (K7 overlap).
- **[test_connect_sd.sh](test_connect_sd.sh)**, a stand-in run of the filled connect
  ([connect/connect-sd.sh](connect/connect-sd.sh), filled at PKG 110a90e8), output in `connect/test_connect_sd.out.txt`.
  - It uses a real clone at PKG, a real base archive and real code-sha checks.
  - Shims answer for squeue, sacct and the O_NOATIME hash, and the toy stands in for the producer.
  - The clean scenario's arms then pass check_sd.py.
  - Each failure scenario must STOP with its reason: a job queued, squeue failing, a job unended, the second fence
    failing (no arm runs), the group C marker, `$W` existing, a wrong E_R digest, a wrong code sha, an arm failing, a
    stray write, and an unfilled template.
- **[test_install_pin.sh](test_install_pin.sh)**, output in `test_install_pin.out.txt`: section 5's install on a minimal
  tree.
  - check_ledger.py --figures passes before and after.
  - make_figures.sh parses, its diff is one line out and seven in, and its install block as written installs the
    eleven figures, the relabelled one with its new digest.
  - A tampered copy fails, and a second install or a wrong listing is refused without writing.

## 5. Re-pins

**In this package (before the run):** `2d-unfolding/ref_c2c1/config.json` `code_sha256` for compare_to_paper_fullcov.py,
1dd5ff52 → 7e641754.
- `ref_c2c1.check_code` refuses a rerun whose code differs from these pins. The functions ref_c2c1 reads from this file
  (`chi2_with_cov` and the flatteners) are unchanged.
- This README is the record of the move.

**Records that stay.** Each records the producer that ran, at its own commit, and no check re-verifies it against the
tree:
- `per-period-benchmark-20261106/receipts/read/readout.json`;
- `secondary-results/component-accounting-20261104/SOURCE-INVENTORY.tsv`;
- `secondary-results/diagnosis-three-items-20261104/SOURCES.md` and `recheck.json`.

**After the run (the receipt):** the run's files go under `run/`, and then [install_pin.py](install_pin.py) runs:
- `figs/` gets the "after" PDF and its SHA256SUMS, and so does `docs/analysis-note/figures/`;
- in make_figures.sh, the fig-restyle install line becomes a comment, and `RSG` names this package's `figs/` for one
  new `install_restyle_fig` line;
- the ledger G row `FIG-MEFHC_5iter_pull_full` is re-pointed, as fig-restyle's ruling 1 has it (re-point, do not
  replace);
- `DIGESTS.tsv` records the old and new digests.

The note build and its gates then run, by the usual route.

## 6. Not in scope (for the director)

- **The note's text** prints "RMS" for the same number in three places:
  - `sec_results.tex:42`, "with RMS `\pullRMSr`";
  - `:55`, the table row "mean / RMS";
  - `:128`, "a pull RMS of `\pullRMS`".
  The paper's `\pullRMS` is in its frozen text. These are text edits under item 16.
- **Fig. 8's caption** does not name the statistic. If "SD" should be defined there, that is a caption edit.
- **The 3D note figure** `eavail_marginal_vs_paper_pull_full` (`sec_3d.tex:97`) is drawn by the same producer
  (`make_figures.sh:126`), so it also prints "rms". It is not in this package. Its quantity is a different
  comparison, and item 16 names only this one.

## 7. The run and the install (2026-11-17)

**The go.** The director gave it for connect `connect/connect-sd.sh` (d78007ac) at PKG 110a90e8. tier3-design acked an
RDX hold before the connect, and was sent the end message after it.

**The run** (login02, no Slurm, 0 node-h). The connect was staged at `/dev/shm/josephrb-pullsd.sh`, and its node sha
matched the go. It started at 17:36:51Z and ended DONE at 17:38:31Z (`run/logs/connect.log`).
- Both fences were clear.
- All 12 code shas were OK, and the deploy was clean at PKG.
- The environment was python 3.11.14, ROOT 6.28/12, matplotlib 3.10.8 and numpy 1.26.4 (`run/environment.txt`).
- E_R (a5c13fc3) and the covariance (6c6dce72) matched their pins, hashed O_NOATIME (`run/inputs.sha256`).
- The three arms ran with rc 0, and each log ends `pull mean / rms : 0.060 / 0.535`.
- No file was newer than the marker, and the deploy was still clean afterwards.

**Fetched files.** `run/` holds `before/`, `off/` and `after/` (no PNGs), `SHA256SUMS` (33 files, all verified after
the fetch), `code.sha256`, `inputs.sha256` and `environment.txt`.
- The connect's own copy of its log, `logs/connect.log`, was taken before its last two lines. It was replaced by the
  full `/dev/shm` log, whose sha 23988164 the removal log records.
- The staged connect and the log were then removed (`run/logs/shm-removal.log`).

**The checks.** `run/CHECKS.txt`: `CHECK_SD :: PASS`, all 16 checks.
- **K2:** "before" and "off" are pixel-equal to fd84d992.
- **K3:** 36 data artists bit for bit, the log byte-equal, the inputs identical.
- **K6:** 6,396 pixels changed, all inside the label's box; the left half is equal.
- **K7:** the gates passed, with the smallest printed text at 5.12 pt.

**The install** (`install_pin.py`):
- the note's `MEFHC_5iter_pull_full.pdf` fd84d992 → b01c1b6c, with its copy in `figs/`;
- the make_figures.sh line and the ledger G row re-pointed, and `DIGESTS.tsv` written;
- `check_ledger.py --figures` passes: G 16 rows and Fig. 1, 0 failures.

The tracked crop `figures/paper_validation_residual.pdf` (the figure's left half) is unchanged, which K6 supports. No
`.tex` includes it. The note PDF is rebuilt by the usual route.

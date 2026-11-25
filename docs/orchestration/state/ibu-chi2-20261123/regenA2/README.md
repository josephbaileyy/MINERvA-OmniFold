# regenA amendment A2: the sec3_twod.tex:11 projection ratios on the paper's pT edges (2026-11-25)

**By** the `ibu-chi-squared-issue` session.
- **Declared:** [`AMENDMENT-A2.txt`](AMENDMENT-A2.txt) (4e60f0eb…) and its reader [`projratio.py`](projratio.py)
  (4f8cc580…), committed at 0d9ef7ca before anything ran. The director's GO.
- **Where:** login02, 2026-11-25T06:19:38Z–06:21:54Z, plain Python, nice 19. 0 node-h, no Slurm, nothing to CFS
  ([`receipts/regenA2_run.sh`](receipts/regenA2_run.sh), f119bfb7…; log [`receipts/run.log`](receipts/run.log)). The
  NERSC certificate was checked at 06:19:19Z, valid to 2026-11-26T03:28:45Z.

**Controls.**
- **C-CLONE:** a fresh clone at 903fb78b and the existing clone at e766ee52, both clean (porcelain --ignored 0) before
  and after.
- **C-PINS:** equal before and after: OLD a5c13fc3, E 5171c7b8, release 6c6dce72, reader 4f8cc580.
- **C-LIT (OLD, with 903fb78b's compare_to_models, which made the printed literals): PASS on all four.**

## Readings

The ratio is ours / published, from compare_to_models.project(). OLD uses 903fb78b's code with both sides on our
edges; E uses e766ee52's code with both sides on the paper's edges. The OLD-to-E difference therefore combines the
edge change with #1318's published-width fix (AMENDMENT-A2.txt). No reading pairs ours-at-0.07 with
published-at-0.075.

| note literal (sec3_twod.tex:11) | rounding | OLD (reproduces the note) | paper's edges |
|---|---|---|---|
| "0.97 in the lowest pT bin" | 2 dp | 0.9675 → **0.97** | **1.0410 → 1.04** |
| "1.04 in the highest" pT bin | 2 dp | 1.0372 → 1.04 | 1.0372 → 1.04 |
| "1.06 and 0.93 in the two highest p‖ bins" | 2 dp | 1.0608, 0.9346 → 1.06, 0.93 | 1.0609, 0.9345 → 1.06, 0.93 |
| "within 2%" in every other bin | integer % | max 2.4991 % → 2 % | max 2.4991 % → 2 % |

**What changes.**
- **The lowest pT bin changes sides:** 0.97 → 1.04. On the paper's edges both the lowest and the highest pT bins sit at
  1.04, so "the ratio rises from 0.97 in the lowest pT bin to 1.04 in the highest" no longer describes the projection.
  The old 0.97 came from the bin-edge mismatch: our first bin was 0–0.07 against the published 0–0.075.
- **The other three literals are unchanged.**
- **"Within 2%" holds only by integer rounding**, at 2.4991 % on both edge sets. The largest deviation is pT bin 12
  (1.5–2.5 GeV/c), at 1.0250 on both: its edges and its p‖ integration don't change.
- The note's wording is Joseph's, through journal-editor.

Per-bin ratios, from [`out/old_projratio.json`](out/old_projratio.json) and [`out/e_projratio.json`](out/e_projratio.json):
- pT, OLD: 0.9675 0.9859 1.0033 1.0186 1.0136 1.0086 1.0024 1.0050 1.0101 1.0104 1.0114 1.0116 1.0250 1.0372
- pT, E: 1.0410 1.0147 1.0033 1.0052 1.0050 1.0144 1.0065 1.0050 1.0101 1.0104 1.0114 1.0116 1.0250 1.0372
- The pT bins whose edges change (0, 1, 3, 4, 5, 6) move. The rest are identical.
- p‖: the largest change is 0.0017, in bin 0 (1.5–2 GeV/c). The p‖ projection integrates over pT widths, which
  change. The two highest p‖ bins move by less than 2e-4.

The outputs' shas are listed in [`receipts/run.log`](receipts/run.log), and [`SHA256SUMS`](SHA256SUMS) covers this
directory.

**Disclosure (2026-11-25).** The runner [`receipts/regenA2_run.sh`](receipts/regenA2_run.sh) (sha256 f119bfb7cdb9921c153acfaf05fbf79f1f67b2cf28f64fe989f9b2cd26f94c83) ran without its sha going to the director first. From now on, every runner's sha goes to the director before it runs.

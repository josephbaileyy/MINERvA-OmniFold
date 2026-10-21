# Fig. 1 and the printed 2D numbers against the adopted 2D result (record)

**Checked by** a Claude agent for the director, 2026-10-21, read-only. It reproduced Fig. 1 byte for byte (`82665808…`) with its named producer `stageF/rebuild/scripts/make_fig1_q.py`. The agent could not write this file, so the director saved its report verbatim below.

**Conclusion:** no mismatch. Fig. 1 draws the adopted central value E_U with the adopted band Q, and the printed numbers (95.6%, 0.074/0.564, 2.65) are E_U's. RE-1's side finding came from checking the release package's stale arrays, which hold the exact-split central value E_C.

**Stale items (KI 100):** the RC7 release arrays and `RC7-README.md:22`, and the expected-value table in `publication/release/figs/fig_numbers.py:85-91`. The 10-11 local PDFs in the shared checkout are also stale and must not be circulated.

---

I checked this from scratch and the deliverables are consistent. The paper's Fig. 1 and all the printed 2D numbers already use the adopted central value E_U (`4f5a1b6d…`) and the adopted band Q (`8ccb4d72…`). RE-1's four discrepancies came from checking the wrong input: the release's `fig_arrays.npz` still holds the old exact-split central value E_C, and RE-1 compared it against the current `values.tex`.

No cluster job ran and no checkout was edited. I worked in the detached worktree `wt-fig1` at origin/main `13cb4a6a`, which is still clean, and I only read the main checkout. All inputs were confirmed on Perlmutter by sha256 and copied locally.

**Q1. What Fig. 1 displays: E_U with the Q band.**
- The paper includes it at `paper_body.tex:726` (`figures/paper_fig1_validation.pdf`, sha256 `82665808e990…`). Its producer is named in `main_paper.tex:159-161` and `paper_body.tex:739`: `stageF/rebuild/scripts/make_fig1_q.py` (`7710d601…`), which runs the release's `make_figs.py` (`9c4dbf24…`).
- That wrapper takes the release arrays and replaces the central value with E_U from `remote_reduce.json` (`make_fig1_q.py:80-84`). It first checks that the old curve it replaces equals E_C. It then adds Q as the band (`:86-111`).
- **I reproduced the printed Fig. 1 byte for byte (`82665808…`)** by running that script unchanged on the pinned inputs. All of its checks passed (median 6.4479, p84 9.1839, max 23.636). Figs. 2 and 3 also came out identical to the paper's.
- I also compared the drawn arrays directly against the source files (`compare_plotted.json`):
  - The plotted curve equals E_U's `hXSec2D` in all 224 bins.
  - The plotted band equals Q's `total_plus_C_PL` exactly on the 205 reported cells and is zero elsewhere.
  - The release arrays' curve equals E_C (`142a45b0…`) in all 224 bins and carries no band of our own. E_U/E_C per bin ranges 0.878–1.053 (median 1.0003).
- For contrast, rendering the release arrays alone gives a different PDF (`d17f088c…`) with no band and an inset of 0.089 / 0.598. That is the file RE-1 compared against.

**Q2. Which central value the printed numbers use: E_U.** `values.tex` (`477decfd…`) cites E_U receipts and keeps the exact-split values in its comments:
- `\binsTen` 95.6 (`:85`, 196/205) comes from `RECEIPT-2d-agreement-windows-lgbm42-20261011.json` (`93f7fb95…`), whose input is E_U.
- `\pullMean` 0.074 and `\pullRMS` 0.564 (`:87-88`) and `\chiPaper` 2.65 (`:125`) come from `chi2_lgbm42_paperonly.txt` (`31add489…`), which reads 2.654 and 0.074 / 0.564. The exact-split control gives 3.661 and 0.089 / 0.598.
- 205 bins, `\ratioTot` 1.011 and `\sigTwoD` 3.073e-38 round the same for both central values (E_U 1.01119 and 3.07302e-38; E_C 1.01129 and 3.07331e-38).

**Q3. Recomputed with `fig_numbers.py` (`54f6d4f7…`).**

| quantity | on the arrays Fig. 1 draws (E_U) | on the release arrays (E_C) | printed |
|---|---|---|---|
| `\binsTen` | 95.610 | 94.146 | 95.6 |
| `\pullMean` | 0.07426 | 0.08895 | 0.074 |
| `\pullRMS` | 0.56442 | 0.59812 | 0.564 |
| `\chiPaper` | 2.6542 | 3.6609 | 2.65 |

The printed set is the one consistent with the adopted central value.

One row still fails on the E_U arrays: ours vs Tune v1 gives 29.7546 against an expected 26.49. That expected value is a hard-coded entry in `fig_numbers.py:91` taken from the exact-split receipt, not from `values.tex`. The note correctly prints 29.8 (`sec_results.tex:271`, receipt `receipt_model_chi2_2d_lgbm42.json` 29.7546). So the checker has a stale expected value, but nothing printed is wrong. As a result, no single set of arrays makes `fig_numbers.py` pass completely today.

**Q4. Conclusion.**
- **Fig. 1 vs the adopted result:** no mismatch.
- **Printed numbers vs the adopted result:** no mismatch.
- **Where these appear:**
  - Fig. 1 is only in the paper.
  - The numbers appear in the paper (`paper_body.tex:157, 682-689`), the note (`sec_execsummary.tex:26`, `sec_results.tex:59-96, 212-216`, `app_statmethods.tex`, `sec_method.tex:137`, `sec_summary.tex:11`, `sec_3d.tex:130`) and the primer (`primer_body.tex:197-198`).
  - The PET note uses none of them.
  - The exact-split values left in the note's appendix are labelled as the cross-check.
- **Nothing in the deliverables needs regenerating.** The correct regeneration is `make_fig1_q.py` followed by `fig_numbers.py` on the arrays it writes. I did both in scratch and they reproduce the deliverables.

Three things are stale, though none is a deliverable error:
1. **The release package.** Release candidate 7 still carries E_C arrays and frozen expected values. `RC7-README.md:22` still says the paper's Fig. 1 is `make_figs.py` output `938c4fc9…`, which stopped being true on 2026-10-11 (`25720215`). The paper discloses this at `main_paper.tex:155-157` and `app_release.tex:25-29`. A new release candidate would need the E_U+Q arrays and the current `values.tex`, which is a separate release decision.
2. **`fig_numbers.py`'s built-in table (`:85-91`)** still holds the exact-split values, including the 26.49 ours-vs-Tune row.
3. **Old local builds.** `main_paper.pdf`, `main_note.pdf` and `main_primer.pdf` in the local checkout were built on 10-11 at 15:52, before the switch commit at 22:47. They still show 94.1 %, 3.66 and 0.089 / 0.598, so don't circulate them.

Everything is in `/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/ee772d13-75a3-4217-970c-8badb94dd2ba/scratchpad/fig1-check/`, with a copy in `/pscratch/sd/j/josephrb/methods-paper/fig1-20261020/` (a few MB, nothing on CFS). Open these first:
- `figs_q/fig1_validation.pdf` (`82665808…`, the reproduced Fig. 1)
- `fn_EU.txt` and `fn_EC.txt` (the checker runs on each set of arrays)
- `compare_plotted.json` (the direct array comparison)
- `SHA256SUMS`
- `tmpq/fig_arrays_q.npz` (`76061935…`), the E_U+Q arrays Fig. 1 is drawn from

None of this is on record until it is committed.
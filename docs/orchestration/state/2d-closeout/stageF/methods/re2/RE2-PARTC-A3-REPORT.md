# RE-2 part C, amendment 3: the Fig. 1 redraw with the legend in sentence case (2026-10-24, re-1 lane)

**Status.** Fig. 1 was redrawn as `RE2-BINDING-C-AMENDMENT-3.md` binds it.
- **The change:** the legend is in sentence case, as Joseph asked. "Published ±1σ" and "This work ±1σ" were
  "published" and "this work".
- **The checks:** the new PDF differs from amendment 2's `cabbbbc3` only there. `pdftotext` differs in exactly the
  two strings, and every changed pixel lies inside the legend's box.
- **Nothing else changed:**
  - no product of the refined chain;
  - no number;
  - Figs. 2 and 3, whose digests are the same as before.

**MEASURES:** that the redraw changed only the legend. **CANNOT AUTHORIZE:** integration, or any printed wording. The
PDF is committed with the integration batch. There is no HPSS step (the amendment).

Paths: `$B` = `/pscratch/sd/j/josephrb/2d-closeout-re2-20261023`. The records are in [`run/partc_a3/`](run/partc_a3/).

## 1. The rename of amendment 2's Fig. 1

`$B/partc-r2/fig1/` became `$B/partc-r2/fig1-a2-cabbbbc3/`, and nothing else in `$B/partc-r2` changed.
- `sha256sum` of every file, taken before ([`fig1_before.sha256`](run/partc_a3/fig1_before.sha256)) and after
  ([`fig1_after.sha256`](run/partc_a3/fig1_after.sha256)): the two lists are equal, 7 files.
- The lists were written beside the run, in `$B/partc-a3/`.

| file | sha256 |
|---|---|
| `fig1_run.log` | `8bbf9ae3c4d18731eb6472a6cb0e61e429654423de8cd42591acb890c5872461` |
| `fig1_validation.pdf` | `cabbbbc3db31810a0c000f10cf346a7b5f01e1035f7860bd34d54a8fb0b537ca` |
| `fig2_joint_localization.pdf` | `57f3cc601281950cf9251b04a627efa3e0d803eca6620178839c48f9d4b0782a` |
| `fig3_generator_context.pdf` | `e9d1bb01fc79e061b95b6e058a2aa2a03275429db5c4531b5e3d9ec63d65fa93` |
| `pins.json` | `e5c596630a9f8397d1368e61ca77f0a2d5514700ec6eaeac82732d132cf65af0` |
| `RUN-fig1.txt` | `fbefcc789c1f19d1c462dfeaa2138214ea778dceee6f7d1a177220a2a84c5221` |
| `uqmedian.tex` | `46c9a1000015aea0523247fcbdd197e8ba6b61440a180951d6b3cf76ed1d89c8` |

## 2. The preflight

On the laptop, a fresh clone was checked out at `1f3b46699efc19c29f67dd5ba98c27091b70845a`, clean (0 changes).
`shasum -c` over the amendment's 30 rows gave **30 of 30 OK** ([`preflight.log`](run/partc_a3/preflight.log);
the table is [`a3_30.sha256`](run/partc_a3/a3_30.sha256)).

## 3. The redraw

**The command:** `bash re2c_fig1_local.sh refined <workdir> <venv python> $B/partc-r2`, from that checkout, at
2026-10-24T17:29:58Z ([`RUN-fig1.txt`](run/partc_a3/RUN-fig1.txt), [`fig1_local.out`](run/partc_a3/fig1_local.out),
[`fig1_run.log`](run/partc_a3/fig1_run.log)).
- **The environment:** python 3.12.2, matplotlib 3.11.2, numpy 2.5.4.
- **The commit:** `1f3b4669`, clean. **The script:** `re2c_fig1.py` `2aadeac8…`.
- **`make_figs.py`:** `4e18c266…`.
- **The inputs:** by digest from `$B/partc-r2/chain.json`, as in amendment 2.
- Every check of `re2c_fig1.py` passed.
- **Where the outputs went:** into the new, empty `$B/partc-r2/fig1/`.

**The new PDF:** `fig1_validation.pdf`, sha256 **`71a2ea488ab758a466d40b7d5a7a061ebd95b1cdb90a79427c3da968238b6427`**.
- It is byte-identical to the pre-binding scratch redraw from `0b13b747`.
- `fig2_joint_localization.pdf` (`57f3cc60…`) and `fig3_generator_context.pdf` (`e9d1bb01…`) keep amendment 2's
  digests.

## 4. The checks against `cabbbbc3`

**Text: pass** ([`pdftotext.diff`](run/partc_a3/pdftotext.diff)). `pdftotext` of the two PDFs differs in exactly the
two strings:

```
5c5
< published §1¾
---
> Published §1¾
8c8
< this work §1¾
---
> This work §1¾
```

**Pixels, method B, the bound check: pass** ([`pixel_diff.txt`](run/partc_a3/pixel_diff.txt)).
- **The method:** matplotlib Agg draws Fig. 1 at 300 dpi with `make_figs.py` `9c4dbf24` and with `4e18c266`, on this
  run's arrays. The legend's box is read from the same canvas
  ([`run/partc_a3_check/legend_png.py`](run/partc_a3_check/legend_png.py)).
- **The legend box:** x 391.6–972.1, y 43.5–288.6, in a 2100×1860 image, identical in both versions.
- **Changed pixels:** 4,415, with their bounding box at x 491–715, y 55–174, **inside the legend box**.

**Pixels, method A, for the record:** the two PDFs rasterised by `pdftoppm` at 300 dpi give 12,346 changed pixels, with
their bounding box at x 401–956, y 55–270. That is also inside the legend box.
- Here the whole legend re-flows by about a pixel, because the capitals drop a descender.

## 5. Every `run/` path named here is tracked

`python3 -I 2d-unfolding/re2/partc/re2c_tracked.py RE2-PARTC-A3-REPORT.md`, output at commit:

```
docs/orchestration/state/2d-closeout/stageF/methods/re2/RE2-PARTC-A3-REPORT.md: 12 run/ paths
  tracked  run/
  tracked  run/partc_a3/
  tracked  run/partc_a3/RUN-fig1.txt
  tracked  run/partc_a3/a3_30.sha256
  tracked  run/partc_a3/fig1_after.sha256
  tracked  run/partc_a3/fig1_before.sha256
  tracked  run/partc_a3/fig1_local.out
  tracked  run/partc_a3/fig1_run.log
  tracked  run/partc_a3/pdftotext.diff
  tracked  run/partc_a3/pixel_diff.txt
  tracked  run/partc_a3/preflight.log
  tracked  run/partc_a3_check/legend_png.py
all tracked
```

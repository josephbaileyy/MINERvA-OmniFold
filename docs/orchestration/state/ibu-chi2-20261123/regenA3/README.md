# Regeneration A3: the REF-C2C1 IBU ladder on the paper's pT edges (2026-11-25)

**By** the `ibu-chi-squared-issue` session, part of the chain in [`../README.md`](../README.md). Requested by the director.
- **Amendment:** [`AMENDMENT-A3.txt`](AMENDMENT-A3.txt) (sha256 0a831cb8bbb5da8e38265a60fcd70ea8e397511f37e62c6b96ce4d7f19522772), committed and pushed at c4980a179c50658d4d8c46106e0b2a85148e8c38, before any read.
- **GO:** the director's, for the one rerun after attempt 1 (below).
- **Reader:** [`ladder.py`](ladder.py), sha256 6c70912f37ba03ef2a2f842494391853806fd1560cbd71a2ad980d9ba444aa12. Runner [`receipts/regenA3_run.sh`](receipts/regenA3_run.sh), sha256 52809d5ca14a21d47d7a85f8ef3f85f6aaec7e4f94de70c095683671eb655cbe.
  Both shas were recorded at run time ([`receipts/attempt2_code_sha_at_run.txt`](receipts/attempt2_code_sha_at_run.txt)).
- **Where:** this laptop, 2026-11-25T07:26:50Z–2026-11-25T07:26:54Z, rc 0. 0 node-h, no NERSC connection. The inputs are Tier 1's committed
  `c2_central.npz` units; there is no new unfold.

## Controls: all PASS ([`out/ladder.json`](out/ladder.json), sha256 565d1f99a3bd702bb1bd7279e97a571eaa6786941b48310fba290c17ec85422a)

- **C-PINS:** pins_before.sha256 equals each of the amendment's six declared pins
  ([`receipts/c_pins_vs_amendment.out`](receipts/c_pins_vs_amendment.out)), and before equals after.
- **C-NDF:** 205 for every distance. **C-KS:** both units store K = 1, 2, 3, 4, 5, 10, 15, 20.
- **C-T1:** K = 5 and 10, OLD and E, equal Tier 1's score.out with relative difference 0.0.
- **C-R2:** OLD reproduces read-2's `D_IBU_every_K` at every K, to at most 9.0e-9 relative (limit 1e-6). Every printed
  macro is identical to read-2's at 2 decimals.
- **C-BOUNDARY (descriptive):** no macro lies within 1e-6 of its 2-decimal rounding boundary. The closest is E's K = 5
  (0.394864, 1.4e-4 below 0.395), which is c2c1-dibu-k5 and also c2c1-dibu-mid-lo.

## Readings, for journal-editor

The print places were found by grep over main_note.tex's \input closure (24 files) at main 7c7a3cfb.
Full-precision values are in `out/ladder.json`.

| macro (make_values_fived16.py:1758-1765) | printed at | OLD (= read-2) | paper's edges |
|---|---|---|---|
| `c2c1-dibu` (K = 10) | sec3_twod.tex:36 | 1.03 (1.026575) | **0.54** (0.538050) |
| `c2c1-der` (D_ER, from Tier 1's score.out) | sec3_twod.tex:36 | 2.27 (2.270318) | **2.12** (2.121436) |
| `c2c1-dibu-mid-lo` (min over K = 2-15) | appC_supplementary.tex:44 | 0.83 (K = 5) | **0.39** (K = 5) |
| `c2c1-dibu-mid-hi` (max over K = 2-15) | appC_supplementary.tex:44 | 1.59 (K = 2) | **1.44** (K = 2) |
| `c2c1-dibu-k20` | appC_supplementary.tex:44 | 2.16 | **1.67** |
| `c2c1-dibu-k1` | appC_supplementary.tex:44 | 3.95 | **4.26** |
| `c2c1-dibu-k5` | not printed (values_fived16.tex:107) | 0.83 | 0.39 |

D_IBU at every K:

| K | 1 | 2 | 3 | 4 | 5 | 10 | 15 | 20 |
|---|---|---|---|---|---|---|---|---|
| OLD | 3.952643 | 1.589235 | 1.080399 | 0.899114 | 0.829947 | 1.026575 | 1.524472 | 2.162867 |
| paper's edges | 4.263318 | 1.440599 | 0.761522 | 0.503165 | 0.394864 | 0.538050 | 1.030417 | 1.674168 |

**Findings for make_values_fived16.py**, not edited here:
- `assert v["c2c1-der"] == "2.27"` fails on the paper's edges (2.12).
- `max(mid) < D_E_R` holds: 1.44 < 2.12.
- `abs(k10["D_IBU"] / c["D_E_R"] - k10["rho"]) < 1e-9` reads read-2's `rho` (0.452172 on our edges). On the paper's edges the
  ratio is 0.253625, so that assertion also needs the new source.
- Tier 1's README gives K = 5 as 0.395 at 3 decimals. At the macro's 2 decimals it prints **0.39**.

## Attempt 1 (no reading)

ladder.py at c4980a17 died in `json.dump` with `TypeError: Object of type bool_ is not JSON serializable`. The cause
was the descriptive C-BOUNDARY flag. It died before printing, and the pins were equal before and after
([`receipts/attempt1_*`](receipts/)). Its partial output is kept unread, as
`receipts/attempt1_partial_ladder.json.unread`. The fix, at 11673a1d, makes boundary() return a Python float: that is
the whole diff. The director gave a GO for one rerun. A first zsh invocation died at its pin step, before Python started, and wrote nothing.
The runner then went to bash.

**Disclosure.** regenA3_run.sh is a launch driver. Its sha should have gone to the director before its first run. The
director accepted it this once, because that run produced nothing.

[`SHA256SUMS`](SHA256SUMS) covers this directory.

# COV2D-G2R: T2A's decomposition at C_T′ (2026-11-14)

**By** the `cov2d` session, as the director's follow-on 1 after D1 (`DECISION-20261114-joseph-d1-g2r-adopted.md`). It
supplies the descriptive readouts that COV2D-G2R-DECLARATION.md:135-137 lists and the readout did not produce
(`../readout/README.md`, "Not produced"): T2A's split ēᵀC_T′⁺ē + tr(C_T′⁺S), and its joint test truncated to the 73
and 139 largest eigenpairs, at G18 and AR23.

**Descriptive only:** this gives no new verdict and no coverage statement at the data's point, the label T2A's code
writes into every record. It authorizes no paper or note wording.

## How it was run

- **Go:** the director, "go fb8e22b6, local run". The run is local, as T2A's own split ran
  (`../../../tier2-20261110/t2a/README.md`:122). It touches no cluster path, so it can't overlap anything that
  watches LL5D paths.
- **Environment** (`run/env.txt`): python 3.12.2, numpy 1.26.4, scipy 1.15.2, matplotlib 3.10.1. Every run used
  `python3 -I -B`.
- **The driver:** `t2a_g2r.py`, sha256 `fb8e22b6533811c5098c9b7d8596b6b91c6caa1f2db247e0fdc91f8df72b4d6e`.
  - It loads the committed `../../../tier2-20261110/t2a/code/t2a_split.py` from its bytes, and refuses any sha256 but
    `462ff4e204530a231af35b850b91d9ffe19eb9f6596ee6aace4aeb29449a2f79`.
  - It replaces only that module's input pins `PINS[T]`, then calls `t2a_split.main()` with T2A's own arguments.
  - In g2r mode the blocks, score and null pins become the G2R readout's files, at the sha256 values in
    `../readout/<T>/out.sha256.txt`. The capture keeps its committed pin, because the 300 error vectors are the same
    (COV2D-G2R-DECLARATION.md:88-90).
  - These stay as committed: `MODULE_PINS`, `RANKS` (73, 139), `N_MC` (2,000,000), `A1_CHI2_TOL`, every control and
    every computation. The three null modules are byte-identical at the G2R commit `401733bc`: `fd_1b_null.py`
    `ec1402db…`, `cov2d_null.py` `a92c0506…`, `cov2d.py` `76cbceba…`.
- **Inputs** (`inputs.sha256.txt`, every file's sha256):
  - from origin/main: the committed `E_<T>.npz` and `capture_<T>.json`, plus COV2D's committed blocks, score, null
    and `t2a_<T>.json` (these four for C0);
  - the G2R readout's `blocks_g2r_<T>.npz`, `score_g2r_<T>.json` and `null_g2r_<T>.json`, as fetched O_NOATIME and
    equal to the node's list (`../readout/d1/node-sha256.raw.txt`);
  - the null modules, from `git archive 401733bc`.

## Control C0: the driver reproduces T2A

In cov2d mode, `PINS` is left as committed. On COV2D's committed blocks, score and null, the driver's records
(`c0/t2a_<T>.json.txt`) equal the committed `../../../tier2-20261110/t2a/t2a_<T>.json` on all 121 leaf keys at both
tunes. Only the 6 path-valued keys are skipped, and 0 keys differ (`c0_compare.py`; `c0/c0_compare.out.txt`: `C0 PASS`
twice). The C0 records are stored as `.json.txt`, because they duplicate committed records and are control evidence,
not results.

## The run at C_T′

`run/stdout_<T>.txt`: `T2A <T> OK rc=0 … controls failed: []` at both tunes. Every control passes:
- the four input pins and the three module pins;
- E is the capture's, and the capture is OK with A0 equal;
- A4, A1 (ndf, χ²/ndf, pulls and counts against `score_g2r_<T>.json`'s grade) and A2;
- A3: the null rebuilt from `laws_at_T` on the G2R blocks reproduces `null_g2r_<T>.json`'s q_joint exactly
  (G18 0.6963645, AR23 0.69201; abs_diff 0).

The records are `run/t2a_g2r_<T>.json`, written by t2a_split byte for byte, and the driver sidecars
`run/t2a_g2r_<T>.driver.json`. `run/summary.out.txt` prints them beside the committed T2A at C_T.

| | G18, C_T′ | G18, C_T | AR23, C_T′ | AR23, C_T |
|---|---|---|---|---|
| ndf | 205 | 205 | 204 | 204 |
| mean χ²/ndf | 25.0338 | 24.1735 | 16.4085 | 16.551 |
| ēᵀC⁺ē (/ndf) | 4470.36 (21.8066) | 4298.53 (20.9684) | 2753.55 (13.4978) | 2776.89 (13.6122) |
| tr(C⁺S) (/ndf) | 661.576 (3.2272) | 657.048 (3.20511) | 593.782 (2.9107) | 599.525 (2.93885) |
| share of ēᵀC⁺ē | 0.871086 | 0.867412 | 0.82261 | 0.822437 |
| rank 73: in region / k_joint | 0/300 / 193 | 0/300 / 193 | 0/300 / 192 | 0/300 / 193 |
| rank 139: in region / k_joint | 0/300 / 190 | 0/300 / 191 | 0/300 / 190 | 0/300 / 190 |

The precision readout (T2-BINDING-1 addendum 1) shows 0 unresolved ranks, and the truncated counts agree between the
two eigensolvers, at both tunes. The figures are gitignored PNGs, listed by sha256 in `figures.sha256.txt`.

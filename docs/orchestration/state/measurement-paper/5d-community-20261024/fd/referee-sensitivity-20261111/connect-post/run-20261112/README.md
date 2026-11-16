# RSN §6 step 5: PASS, and RSN's readings against the declared outcome tables (receipt)

**By** session tier3-design. It ran under the director's go: `rsn_connect_post.sh` `9a16608a…` and
`rsn_connect_post_launch.sh` `f03c18cd…`, re-hashed from main `5bc01d42` (#1113). The run was once, on login27, at
0 node-h, during E96D, ending 18:25:22Z with script rc 0 (`post.session.txt:13772-13773`).

**Before the tools** (`post.session.txt:7-14`):
- J2 61170759 and J3 61170761 are COMPLETED 0:0 (00:13:31 and 00:14:22);
- all 12 products are on disk at their logged sha256s;
- `nc.json` is a PASS;
- the M_P1 deploy is clean, with the bound sha256s;
- the four staged inputs are at their pins;
- the guard's self-test refused, as required.

**The three tools:** `rsn_cmodel.py build`, `rsn_regrade.py` and `rsn_read.py`, each rc 0 (15-29).

**The read set held** (`readlog.txt`, from `post.session.txt:13694-13769`):
- No guard refusal occurred beyond the self-test, and no path was listed OUTSIDE.
- The paths listed lie under the M_P1 deploy, RSN's own `out/` (products, prep, cmodel, stage, the outputs) or
  pv-ladder's frozen products. The interpreter's own prefixes are counted but not listed.
- `of_inputs_5d.npz` and `bkg_dump.npz` do not appear.
- The only NuE constraint file opened is the O_NOATIME-staged copy (`readlog.txt:66`).

**The outputs.** These are byte copies taken from the session's print, plus the npz fetched afterwards by `cat`. Each
re-hashes to the digest the session printed:

| file | sha256 |
|---|---|
| `cmodel/rsn_cmodel.json` | `9d2d315f0e2ee3eedb4f0857f908f1c27ce83091b6cd3da64c8f28c0767d9289` |
| `cmodel/rsn_cmodel.npz` | `faa9d01f690953adced24684117c8e18e0f2419cd5153546e01620c1d00f8a60` |
| `regrade.json` | `cb5f5d17a3f64f4c35851184219d3e040917a908d894ffb9d70674dec78c70ed` |
| `rsn_readout.json` | `6291f48d5efa40a59808c175406b3b9a7bce9c91a11c0604174e5d1b06aef233` |

`regrade.json` records its controls as run: NC-R, the nominal S, and C-INV. The bound code refuses, writing nothing,
unless each holds.

## The readings against RSN-DECLARATION.md rev 3 §3

Every reading is a sensitivity of the stated construction. None is a calibrated uncertainty, and nothing here enters a
reported covariance (`rsn_readout.json` `label`).

Each class below is the one `rsn_read.py` assigned. Each was re-checked by hand against the declared rule, from the
numbers in `rsn_readout.json` and `regrade.json`.

### G6 (referee 3.1): "the fake-data conclusions survive G6"

| | reading | declared rule | class |
|---|---|---|---|
| P1 | listed set {q3, A7_gibuu}, the same as nominal | L^V = L | **unchanged** |
| P2 | prior 0/32 cells, 0/2 truths; vertex-family 2/128, 1/8; non-vertex 0/32, 1/2; held-out 0/64, 0/4 (all as nominal) | descriptive | — |
| P3 | both criteria met at the four held-out records (χ² 9.11, 8.91, 14.19, 13.52) | holds or not | **holds** |
| P4 | median q 1.123; every q_c in [0.542, 1.774]; GiBUU trace share 0.923 against 0.890; tr ratio 1.415 | median in [0.8, 1.25] and every q_c in [0.5, 2] | **C_model similar** |
| P5 | reported σ ratio: median ×1.002, range [0.864, 1.338] | descriptive | — |

C-INV held. A7_gibuu (χ² 171.01, R02 and R06) and stage0c_gibuu (χ² 24.57) grade exactly as nominal.

Of the records G6 could move:
- q3 stays listed (p 9.1e-6 → 5.6e-7);
- W3 stays unlisted (p 0.037 → 0.028);
- A7_nuwro stays unlisted (p 0.093 → 0.077).

### SM (referee 3.2): "a fake-data conclusion changes under SM"

| | reading | declared rule | class |
|---|---|---|---|
| P1 | listed set {q3, A7_nuwro, A7_gibuu}: **A7_nuwro added** | L^V ⊃ L | **more flagged** |
| P2 | vertex-family 2/128 cells, **2/8 truths** (nominal 1/8); prior, non-vertex and held-out as nominal | descriptive | — |
| P3 | both criteria met at the four held-out records (χ² 22.82, 20.97, 15.78, 14.46; p 0.119, 0.180, 0.469, 0.564) | holds or not | **holds** |
| P4 | median q 0.496; GiBUU trace share 0.664 against 0.890; tr ratio 0.112 | median q < 0.8 | **C_model smaller** |
| P5 | reported σ ratio: median ×0.934, range [0.595, 1.028] | descriptive | — |

**The record that changes is A7_nuwro.**
- Under SM it reaches p = 0.0049 against the 0.01 trigger, with χ² 34.33. The nominal is p = 0.093, χ² 23.86.
- No cell of it has |z| > 2, so it is listed by the per-truth p trigger alone.
- A7_gibuu stays listed: χ² 217.84 against 171.01, at the same cells R02 and R06.
- q3 stays listed: p 1.3e-5.
- The held-out records' χ² rises (G18 9.26 → 22.82) but stays within both criteria.
- SM's construction parameter is recorded as `radius` 2.

### WR (referee 1.2, fresh F1.1)

The verdict, scoped as §3.3 declares: "in pvl's noise-free signal-only closures, the equal-weight regression is
immaterial at the A7 GiBUU hybrid and the q3 tilt, and the data move below half the reported sigma".

| | reading | declared rule | class |
|---|---|---|---|
| P6 (data) | max \|δ_c\|/φ_c 2.86; max \|δ_c\|/σ_c 0.089 (the largest δ is +0.72 %); no cell at half σ; χ² 0.245 | not W0 (2.86 > 2), and max \|δ\|/σ ≤ 0.5 | **W1** |
| P7 prior | max \|b^W\| 3.21e-5; equal weights 3.22e-5 | > 1e-4 flags a break | **not broken** |
| P7 NuWro | RMS 0.02685 weighted, 0.02693 equal (ratio 0.997) | ratio in [0.9, 1.1] | **comparable** |
| P7 A7 GiBUU hybrid | χ² 176.61 weighted, 173.05 equal; noise-free flag set under both | flags equal and \|Δχ²\| 3.56 ≤ 0.25·173.05 | **immaterial** |
| P7 q3 tilt | χ² 52.78 weighted, 51.54 equal; flag set under both | flags equal and \|Δχ²\| 1.25 ≤ 0.25·51.54 | **immaterial** |

**What this licenses** (the director's ruling on audit R2) is a stated sensitivity of pvl's noise-free signal-only
full-MC closure, WR against WU. It does not attribute F0b's flags at A7_gibuu and q3. That attribution is T3's B0/MW
reading.

### TR (fresh F1.2(ii), P8)

| point | max \|t_c\| / 2φ_c | max \|t_c\| / σ_c | rel. bias, rel. RMS | class |
|---|---|---|---|---|
| the data | 3.14 | 0.114 | −0.04 %, 6.7 % | **T1** |
| the A7 GiBUU hybrid | 2.54 | 0.069 | +0.02 %, 3.3 % | **T1** |
| the q3 tilt | 0.55 | 0.016 | +0.01 %, 1.6 % | **T0** |

No cell lies beyond half σ at any point.

The classes bound the transfer bias plus the 80 % probe's own estimation noise, and no noise reference is made
(§3.5). TR tests transfer among matched events at fixed truth. It cannot show that misses resemble matched events in
what the five features omit (§2.7).

The ratios to φ_c and σ_c above are re-derived from P6's per-cell δ_c/φ_c and δ_c/σ_c, which carry the same φ_c and
σ_c.

### What no arm changes (§3.4, stated before the run)

These are:
- the 2D benchmark;
- the prior-retention study;
- the rounding study;
- the 2D coverage results;
- LL5D's test;
- the Stage G generator χ².

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:**
  - RSN's §6 step-5 outputs at these digests;
  - the classes above against the declared §3 rules;
  - the enforced read set during E96D.
- **Not citable for:**
  - any paper sentence. Under RSN-BINDING-1 ruling 5, wording is Joseph's, after a PRD-referee read;
  - a calibrated uncertainty;
  - a change to C_model, to a grade or to the estimator;
  - the attribution of F0b's flags, which is T3's.

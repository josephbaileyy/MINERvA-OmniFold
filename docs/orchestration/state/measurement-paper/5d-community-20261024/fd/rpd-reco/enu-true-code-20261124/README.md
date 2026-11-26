# RPD-RECO code for amendment 1: true Eν from RDX's truthx sidecar (2026-11-24)

**By** limitation-resolver, for the director's binding. It implements
[`FD-RPD-RECO-DECLARATION-AMENDMENT-1.md`](../../../FD-RPD-RECO-DECLARATION-AMENDMENT-1.md) (PR #1300, held at
`a0981bf0`), which binds separately. **Nothing here has run on NERSC.**

## The files

| file | before (main) | after |
|---|---|---|
| `nd-unfolding/fd_rpd_reco.py` | `7302cc1d…` | `12f68102…` |
| `nd-unfolding/fd_rpd_reco_custody.py` | `634670b3…` | `6428dead…` |
| `nd-unfolding/tests/test_fd_rpd_reco.py` | `e1b92ef0…` | `eee5ae4c…` |
| `nd-unfolding/tests/fd_rpd_reco_mutation.py` | `f2612369…` | `8dfdeaf1…` |

`fd_rpd_inputs.py` is unchanged.

## What changed in `fd_rpd_reco.py`

**C-JOIN part 1, in `true_energies`** (amendment §4). This runs in `flux-extract` only, and nothing else reads the
sidecar. The steps:
1. It stages the sidecar through `Inputs.copy`. Under flux4's prestage, that is custody prepare's staged copy, read by
   O_NOATIME.
2. It requires the npz members, names, dtypes and shapes exactly. It also requires the meta schema, `npz_sha256` = the
   configured `lat_zero` sha256, `rows`, and the playlist order.
3. Every playlist index must be in range and must never decrease. Each block size must equal its `lat_<PL>` row count.
4. Every Eν must be finite and > 0.
5. Eν in GeV is `truthx_enu / 1000`. The median must lie in [1, 50] GeV (guard `C_JOIN_UNITS`).
6. For each playlist it records the spot rows: the sorted, distinct union of the first row, the last row and 64 rows
   from `SeedSequence([20261124, 17, k + 1])` (`spot_rows`). Each row goes in with its (run, subrun, event) and Eν.

**`flux_extract`** evaluates the factors at the true Eν. It writes `energy` (float64 GeV, every row) into each
`flux-factors-<PL>.npz` and the join record into `flux-extract.json` (`true_energy`).

**C-JOIN part 2, in `omnifile_spot_check`.** `p0` calls it right after `extracted_flux` has checked the flux4 record's
identity. It runs before `common_flux_units` and before any factor product is read, and so meets the director's order
condition. The checks:
- It reads the spot rows from flux4's record and requires them to be:
  - integers, sorted and distinct;
  - covering the first and last dump rows;
  - at least min(64, rows) in number;
  - with ids and energies of matching length.
- `lat_<PL>`'s MCgen must be float32.
- The pinned product's `energy` must equal the record at those rows.
- It stages each omnifile at its c2 pin by O_NOATIME. A mismatch is `INPUT_DIGEST`.
- It reads `mc_signal_reco` with uproot, never ROOT. Each (run, subrun, event) must occur exactly once.
- `truthx_enu / 1000`, `float32(MC)` and `float32(MC_pz)` must equal the record and MCgen bitwise.
- Any failure is a STOP, and `p0.json` is not written.

**`pinned_flux_factors`** requires the `energy` column: float64, finite and > 0, one value per row.

**`aggregate`** reads each signal sample's product once and passes its `energy` to `energy_statistics`.

**`energy_statistics` and `evaluate_energy_controls`** (amendment §5) take the true Eν:
- C-E1 is finite Eν and Eν ≥ Eμ, at the unchanged 99.9%;
- C-E3's formula and gates are unchanged;
- C-E2 keeps the M_n/M_p spread and adds the inversion's deviation from the true Eν. Both are report-only;
  `report_quantiles` returns nulls when nothing is reportable.

**The configuration** gains `true_energy`: `{path, sha256, npz_sha256, omnifiles: {PL: {path, sha256}}}`. `Inputs`
adds each of these paths to its protected roots.

## What changed in `fd_rpd_reco_custody.py`

`prepare` stages `true_energy.path` at its sha256 like the other declared inputs. So the extract reads only the staged
copy, and the trace policy protects the original. A missing pin is `TRUE_ENERGY_PIN`.

## Tests: `tests.txt`

**386 passed** with `python3 -m pytest -q tests/test_fd_rpd_reco.py`: the 324 on main, as adapted, plus 62 new ones.

**The fixture:**
- It writes a real-format sidecar and 12 uproot omnifiles. Their entries are permuted, plus one unrelated entry.
- `lat_<PL>`'s MCgen is float32, as in the dumps.
- The fixture's true Eν is its own mean-mass inversion × (1 + 10⁻⁶). That is far inside C-E3's bars, but a reader that
  fell back to the inversion is caught bitwise.

**The new tests:**
- every part-1 refusal;
- the units band both ways;
- the staged-copy-only read;
- the declared seed;
- every part-2 refusal: missing and duplicate events, one-ulp Eν, MC and MC_pz, and every structural spot-row rule;
- product energy, status, source, playlists and omnifile pins;
- float32 MCgen;
- P0 stops at an omnifile pin mismatch;
- P0's order: a planted part-2 failure is the only call made;
- d2-predict reads the product's energy: scaled by 1%, it STOPs at C_E3;
- the energy-column refusals;
- C-E1 and C-E3 with true Eν, and C-E1's missing denominator clause;
- custody prepare stages and protects the sidecar, and refuses without its pin.

## The line trace: `trace.txt`

Every added statement ran under the full suite:
- `fd_rpd_reco.py`: 132 of 132 statements in its 365 added lines;
- `fd_rpd_reco_custody.py`: 3 of 3.

This is coverage 7.15.4 over the full suite, mapped to `git diff -U0 origin/main`.

## Mutants: `mutation.txt`

`python3 nd-unfolding/tests/fd_rpd_reco_mutation.py` gave **281 of 281 killed (complete, all killed; the comment-only custody control passed)**, against the files above.
- **The new mutants (45):**
  - 42 named mutants, one per new clause: 41 in the producer and 1 in custody prepare;
  - the guard mutants for `C_JOIN`, `C_JOIN_UNITS` and custody's `TRUE_ENERGY_PIN`.
- **Five first survived** across the development runs, on weak tests, not weak code. Each test was fixed before this
  run:
  - a 64-row fixture masked the block check, so a 70-row fixture now tests it;
  - 1B's seeded sample happened to hold its last row, so a 100,000-row case was added;
  - a duplicate overwrote another spot row, so the duplicate is now appended;
  - with 64 of 64 rows as spots, a missing first row also failed the count rule, so a 200-row fixture now tests the
    end rows;
  - a dropped energy also failed the product comparison, so the length test now drops an event id.

The fence harness `tests/fd_rpd_reco_fence_mutation.py`: 24 of 24 killed.

## Not done here

- **No run.** flux4 → P0 → d2-predict + step0 → the c0 harness → c0 each need their package and their own binding.
- **The reads:**
  - agy read the amendment (GO, two non-blocking findings, both taken in #1300).
  - This PR's reads follow the same order. codex-school2 is queued behind COVFIX's.

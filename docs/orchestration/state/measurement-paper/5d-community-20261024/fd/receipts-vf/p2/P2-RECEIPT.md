# V_F Phase 2 receipt: local recomputes and the read-only fetch (option C)

Governed by FD-VF BINDING 2 (#1364) and 2b (#1366), and amendment A4
(`FD-VF-ADDITION-AMENDMENT-A4.md`). Readings go to the director first; nothing here is note wording.

## Platform

All Phase 2 recomputes ran locally on macOS 26.6.2 (arm64), Python 3.12.2, numpy 1.26.4 linked to OpenBLAS
0.3.23.dev (openblas64, MAX_THREADS=3), uproot 5.6.2, scipy 1.15.2. Nothing ran on NERSC except the one read-only
fetch below.

## The fetch

- Attempt 1: a STOP by design, terminal (`attempt1.txt`). A symlinked `MParamFiles` component under the NuE path.
  Ruling 2b took NuE from its committed copy and added the pre-flight.
- Attempt 2: one read, rc 0, 402 of 402 files verified (`attempt2.txt`).
- The wrapper, reader and list are `fetch-vfp2.sh`, `fetch_vfp2_remote.py` and `fetch-list.tsv`. The codex reads are under `reads/`.

## The recomputes and control P

Every V_F copy is in `fd/with-vf/p2/`. In each copy, `vf_patch` records control P (the OLD matrix reproduces the committed readout) and its tolerance under A4. Any value above its tolerance would have been a STOP. `xk-receipt.vf.json` is the replay's own receipt; `xk.vf.json` carries xk's control.

| V_F copy | sha256 | control P | tolerance (achieved max) |
|---|---|---|---|
| `cr.vf.json` | `f58bc91280436c83d5cadf8a123c8184d66068f66208ff04a3e89d6cf5d849f1` | PASS | 1e-12 (0) |
| `e2.vf.json` | `7db5bd32180ce66b5ab5cdfa12770807cee28b868833b84fcf64f05c51159a73` | PASS | 1e-09 (3.24e-10) |
| `e2sens.vf.txt` | `e31bb03a5f3e0a0a439db6d777df0dcbbe2d761dd8796e93296f5096f1d49c84` | PASS | chi2: 1e-09 (2.53e-10); sigma: 1e-12 (0) |
| `eav.vf.json` | `516b625d5d65fe8c3cb7e5b4c967c0fd53533919e5c10f1483b297e7c23cad52` | PASS | exact equality |
| `gch.vf.json` | `968cfb876c02e1024d1977a570a49b48a0e737b4cf71c1951f7da2889694cf94` | PASS | chi2: 1e-12 (0); p: chi2_sf(committed chi2, ndf) == committed p, bitwise; the reproduced p (0); other_fields: 1e-12 |
| `gdefs.vf.json` | `6c202b08b5d9ed0be0880bb97ad1966f102c5cca6138b949a9345ae11aa7b788` | PASS | chi2: 1e-09 (1.74e-10); p: chi2_sf(committed chi2, ndf) == committed p, bitwise; the reproduced p (2.18e-08); other_fields: 1e-12 |
| `gnat.vf.json` | `3607e78c22ba00bf51879b763dff0324176ec785c3a5a730469da6a8a800800e` | PASS | chi2: 1e-09 (1.95e-10); p: chi2_sf(committed chi2, ndf) == committed p, bitwise; the reproduced p (1.77e-08); other_fields: 1e-12 |
| `gover.vf.json` | `879d3dca63db4c2e88b453b2828002e9975247e3a97e52894a0f3b032558845e` | PASS | 1e-12 (0) |
| `prr.vf.json` | `fc9afee77250940de23500947230d04670a23ce9f763d21ea71b4667b4d3feb5` | PASS | (e): 1e-12 (5.47e-13); IBU: 1e-11 (1.07e-12) |
| `rsn.vf.json` | `8e5addb8ec0a7649495fd784eed4e13f77780f654f4185d0e2824d1e2348b101` | PASS | 1e-12 (1.57e-13); p: as rsnregrade's (A4 item 3) |
| `rsnregrade.vf.json` | `10dcdd729d2d86fe797ba4bf801647d3446f5d35aa2578523b6278c5c25f5c7c` | PASS | 1e-12 (9.06e-13); p: fd_f0_regrade.chi2_sf_even(committed chi2, ndf) == committed |
| `vatlas.vf.json` | `380682e69408b51b8299cb473254b7a5f3ae73113aa31797d02b85a41a80472a` | PASS | 1e-12 (0) |
| `xk-receipt.vf.json` | `3ed2a7c1c82e5953c014ebca02b72d4d7b6f7f7c69c57ff1aacd1b25a3df09c7` | PASS | exact equality |
| `xk.vf.json` | `045eb904bbe25a8b84e6598740dce8a3a1f1052dd87e09e2029577cb9074bce4` | PASS | 1e-07 (1.03e-08) |

- **xk.** The OLD replay first failed the 1e-12 check (max 1.03e-8). The director ruled the named category and the
  1e-7 tolerance on 2026-11-26. The evidence is in A4 and `xk-conditioning/`; the OLD replay's own output is
  `xk-old-replay-k.json`. Every printed xk string is identical OLD vs the committed readout (the readings' section 3).
- **Control D** (no flag set and no agreement count falls under V_F) holds in every readout: see the readings.

## Fixes after the confirm reads (2026-11-26; the director's GO)

The reads were codex-school gpt-6.2-sol and claude-personal claude-sonnet-5-5, both under the director's scope rule. Their
reports are in `reads/`. No recomputed value changed.
- **p by function identity.** A committed p written as 0.0 below the floor (`p_below_floor`) now also requires the
  producer's p to be below `fd_f0_regrade.P_FLOOR` (1e-30). Before, that case skipped the identity check. rsn and
  rsnregrade regenerate byte for byte under the tightened check.
- **gch's chi2 tolerance** is 1e-12. A4 item 1 keeps gch at that value, as a bit-identical input; it was 1e-9. Achieved:
  0. Only the tolerance record in `gch.vf.json` changes.
- **prr.vf.json's `table_ii_committed_beside_B0`** keeps its OLD values. They are read by nothing (prr_read.py:452,
  section 4.2), and `vf_patch.not_replaced` now names them. The V_F product's f is asserted equal to the grade
  matrices' f.
- **The readings tool** sweeps every non-float leaf of both arms. It builds section 1's headline from that sweep and
  exits 1 on any control D event that no named ruling covers. See the readings.
  - After the fix-diff read (`reads/p2-fix-*`, NO-GO on 3 findings): every leaf name is now classified, and an
    unclassified name is structural, so any change to it is an event (fail closed).
  - `controls` are now swept.
  - Each ruling checks its premise. q3: B0's q3 clears, and q3 is flagged at the level under both. QD: rho* was at or
    above 1 and stays within 1e-3 of it.
  - PR-3's "clears at these truths" counts as an improvement.
  - The readings' values, moved keys, guards and decision rules are unchanged. 20 p_below_floor clearings move into
    the headline.
  - Mutation, both rounds: 26/26 killed (`mutation/`).
  - After the round-2 read (`reads/p2-fix2-*`, NO-GO on 3 findings: X's `named`/`quadrants_over` and RSN's held-out
    `truths` count classed as descriptive; improvements off a hand-kept allowlist read as STOPs). Changes:
    - The descriptive class is now only the names that change under V_F in this sweep, each checked by hand. Every
      other unclassified name is structural.
    - `named`/`quadrants_over` are flag lists.
    - Outcome strings are judged on the producers' ordinal scales: fd_gencmp.rule, the X rule, rsn_read's T/W/deformed/
      listed classes, PR-3, valid_region, and an arm verdict that comes to survive. An unordered class change is an
      event.
    - The readings are unchanged except for the event-reason wording.
    - Mutation round 3: 6/6 killed.
- **Reproduction.** All 14 copies were regenerated after the fixes; prr, rsn and xk came from the verified fetch. 12 are
  byte-identical, and gch and prr differ only as stated. The opt-in test (`VF_P2_FETCH`, `VF_P2_XK=1`) reproduces
  prr, rsn and xk byte for byte.

## Disclosures

- **FOLLOWUP: xk's CR_G2R substitute** is p2_overlap("cr")'s record, without the `vf_data_product_sha256` that
  `cmd_p2` adds when it writes `cr.vf.json`. Its sha (`xk.vf.json` vf_patch.substituted) is therefore not
  `cr.vf.json`'s. K reads only its `quadrants` (fd_xcov_steps.py:536), and these are value-identical; a test asserts
  equality of the whole record apart from that one field.

- `nd-unfolding/prior_retention/test_prr.py::Truths::test_the_floor_seeds_are_no_campaigns` fails locally, and not
  for environmental reasons. It is a repo-wide grep that now matches newer campaigns' files (msr/msr_build.py,
  msr_project.py, test_msr.py, s2r/test_s2r.py, tier3/t3p_probe.py, test_t3p.py). The other 115 PRR tests passed,
  every grade test among them. That test is a bound file and was not touched. Its fix is a FOLLOWUP.
- The other producers' suites under this interpreter: test_fd_xcov plus test_fd_gencmp 117 OK (1 skip: gencmp's
  Linux-only O_NOATIME test); rsn/test_rsn 52 OK.

## Readings

`fd/receipts-vf/readings/vf_readings.{json,md}`, written by `vf_readings.py`. Phase 1's readings are in `vf_readings_phase1.{json,md}`.

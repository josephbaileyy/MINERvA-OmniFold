# AMENDMENT 1 to the d1/d2 declaration: true Eν from the event loop, after the C-E3 STOP (2026-11-24)

**By** limitation-resolver, for the director to bind.

**Under** Joseph's choice (A), the event-loop Eν route, relayed by the director on 2026-11-24. The director approved
route (R) the same day: read the existing, bound and checked event-loop output instead of re-running it, at 0 node-h.
The conditions are in §2 to §8: the exact source, the join rule, a new control C-JOIN, a units test, custody staging,
tier3-design's ack, the purge risk, and a binding per step.

**Amends** [`FD-RPD-RECO-DECLARATION.md`](FD-RPD-RECO-DECLARATION.md) (sha256 `b0eee33c95ccb037…`, last changed
`e0a9ed77`). It amends §4 "Eν per MC row" and its controls, the code and price of §5 for the steps that rerun, and §7's
Eν tests. Everything not named here stands as declared and bound, including every d1 and d2 rule, C-0, P-F, the
out-of-range STOP, the outcome table, blinding and §8's licences.

**Frozen before any output is read.** No true Eν value has been read by this lane. No new control below has been
evaluated on any input, and C-E3's formula and gates are unchanged.

**MEASURES:** nothing.

**CANNOT AUTHORIZE:** running anything (each step needs its own binding and GO); regenerating any RDX output; a change to
any C-E gate; any reading of d1 or d2.

**CITABLE FOR:** what the Eν source now is, how its rows are joined, and which controls apply to it.

**NOT CITABLE FOR:** any RPD-RECO result, or that C-E3 will pass.

## 1. Why: the C-E3 STOP

- **The run.** d2s0's `d2-predict` (code `7302cc1d`, config `3b2afde4`) refused at C_E3 with "q3 discrepancy
  0.0012597542525496497, 0.030134546090343273 in 8:15" (`fd/rpd-reco/d2s0-20261124/run-20261124/README.md`, #1284).
  - In p∥ [8, 15), the median was within its gate (≤ 0.002), and the 99th percentile was over its gate (≤ 0.03) by 0.45%
    of the gate.
  - No measured key was opened.
- **The declaration's branch.** §4: "If C-E3 fails, the event-loop route returns to the director, priced." This
  amendment is that route. The gates are not loosened.
- **A likely cause** (reasoning, not measured):
  - MAT's truth W (`CVUniverse.h:396-409`) uses the struck nucleon's mass, M_n or M_p. The inversion had to use their
    mean, so it is off by half their difference, 0.65 MeV, on every row.
  - Since ∂Eν/∂M ≈ Eμ/M, that is about 6.5 MeV of Eν at Eμ ≈ 10 GeV. Through q0 = Eν − Eμ, this is a few percent of a
    small q0, which is a tail in q₃′/q₃.
  - True Eν removes this term. Whether C-E3 then passes is measured only by the bound run.

## 2. The Eν source, exactly

**The file.** `/pscratch/sd/j/josephrb/rdx-20261112b/out/dumps/truthx_RDX_ALL.npz`, sha256
`641ba34c5ebde6d1881c705b862fab144a6fbb8a58ef3d84e59f1c8ba030a79e` (`fd/redump-f12i-20261112/run-cm-20261117/README.md`;
`nd-unfolding/rdx/rdx-inputs-SHA256SUMS`).

**Its producer.** tier3-design's RDX, under [`RDX-BINDING-1.md`](fd/redump-f12i-20261112/RDX-BINDING-1.md) (sha256
`a79957863c9ced80…`) and [`RDX-DECLARATION.md`](fd/redump-f12i-20261112/RDX-DECLARATION.md) §2 C1–C2:
- **The event-loop branch.** `nd-unfolding/rdx/runEventLoopOmniFold-truthx.patch` (sha256 `578c64ea600e6cba…`).
  - Under `MNV101_DUMP_TRUTHX`, it writes `truthx_enu`, the universe's `GetEnuTrue()` in MeV, on `mc_signal_reco` and
    `mc_truth_denom`.
  - It is the same accessor that `CVUniverse.h` uses for the truth Q² and W (`:386, 405`).
- **The binary.** `bld_rdx` (md5 `38398191…`), run with `MNV101_DUMP_TRUTHX=1` and no other `MNV101_*` variable
  (`run-c1-20261115/README.md`).
- **The jobs:**
  - the 1A pilot, s1 `61315648`;
  - the other 11 playlists, s2 `61423404`, `61423406`, `61423408`, `61423410`, `61423414`, `61423417`, `61423421`,
    `61423451`, `61423454`, `61423456` and `61423459`;
  - the merge and dump, m `61443055`.

  All are COMPLETED 0:0 in their receipts.
- **The checks it passed:**
  - **C-ALIGN-1A and C-ALIGN-PL:** every common branch of each playlist's RDX loop equals MP-1 S1's zero loop for that
    playlist, bitwise (`run-c1-20261116/`, `run-c2-20261117/`).
  - **C-TRUTHX:** every value finite and `truthx_enu` > 0 (same receipts).
  - **cm's C-TRUTHX-NPZ:** PASS over 32,846,302 MCgen rows. Every sidecar row joined to its playlist's omnifile with 0
    rows differing in MC, MC_pz, w_truth or any truthx double (`run-cm-20261117/README.md`).
- **The 12 per-playlist omnifiles** are `/pscratch/sd/j/josephrb/rdx-20261112b/out/evloop/runEventLoopOmniFold_RDX_<PL>.root`.
  Their sha256s are c2's lines (`run-c2-20261117/c2.session.txt:1150-1161`), which become pins.

**Its layout** (`nd-unfolding/rdx/rdx_dump.py:174-203`, sha256 `122702c6…`):
- `truthx`, float64, (n, 5), with `truthx_names` = (`truthx_enu`, `truthx_vtx_x`, `truthx_vtx_y`, `truthx_vtx_z`,
  `truthx_kep_lead`);
- `mc_id`, int64, (n, 4), with `mc_id_names` = (`playlist_index`, `run`, `subrun`, `event`). The playlist index is the
  position in 1A, 1B, 1C, 1D, 1E, 1F, 1G, 1L, 1M, 1N, 1O, 1P;
- `meta`, a JSON string with `schema` = `rdx-truthx-sidecar/1`, `npz_sha256` = `6ca02c3d8b09dfd1…` (MP-1's
  `lat_zero.npz`, byte-identical to RDX's `lat_RDX_ALL.npz`), `rows`, and the 12 omnifiles in index order.

**tier3-design's ack** (2026-11-24):
- the sidecar and the 12 omnifiles stay in place, and tier3-design has no plan to move, remove or regenerate them;
- no atime watch or fence of tier3-design covers them;
- removing anything under `rdx-20261112b` is Joseph's call.

A fresh ack is taken before each connect that reads them.

## 3. The join rule

**Row i of `lat_<PL>` is sidecar row offset(PL) + i**, where offset(PL) is the sum of the row counts of the playlists
before PL in the order above. Three committed bitwise checks give this:
1. **RPD's C1** passed (`fd/receipts-rpd/run/controls/controls.json`, `keys.MCgen` true).
   - `lat_<PL>`'s MCgen rows, concatenated in that playlist order, equal `lat_zero.npz`'s MCgen in dtype, shape and bytes
     (`nd-unfolding/fd_rpd.py:763`).
   - MCreco, pass_reco and pass_truth are equal in the same way.
2. **`lat_RDX_ALL.npz` is `lat_zero.npz`:** both have sha256 `6ca02c3d…` (`run-cm-20261117/README.md`).
3. **The sidecar's rows are that npz's rows.**
   - `rdx_dump.py` refuses unless its kept-row replica equals the npz's MCgen, MCreco, pass_reco, pass_truth, w_truth and
     w_reco bitwise.
   - Its meta names the npz's sha256.
   - C-TRUTHX-NPZ then joined every row back to the omnifiles.

**Eν in GeV is `truthx_enu / 1000`,** one float64 division per row. The MCgen columns and the flux files' Eν axis are
in GeV (§4 of the declaration; `fd_rpd_reco.py` `mat_flux_swap`).

C-JOIN (§4) checks this rule in code. It does not rely on the three records alone.

## 4. C-JOIN, a new control

C-JOIN is a STOP on any failure, in two parts. Neither part reads a measured key.

**Part 1, in flux4 (`flux-extract`), the only step that reads the sidecar.**
- The sidecar is pinned by sha256 like every other declared input, staged by custody `prepare`, and read only from that
  staged copy, by O_NOATIME.
- The checks:
  - `meta.schema` is `rdx-truthx-sidecar/1`;
  - `meta.npz_sha256` equals the configured `lat_zero` sha256 `6ca02c3d…`;
  - `meta.rows` and the array lengths agree;
  - the names and dtypes are exactly §2's;
  - every playlist index is in 0…11 and the index never decreases down the rows;
  - each playlist's block size equals that `lat_<PL>`'s row count, for all 12;
  - every `truthx_enu` is finite and > 0.
- **The units band.** The median of Eν in GeV over all sidecar rows, after the division, must lie in [1, 50] GeV.
  - For any true median m in [1, 50] GeV, a double conversion gives m/1000 ≤ 0.05 GeV and no conversion gives
    1000·m ≥ 1,000 GeV, so both land outside the band.
  - A true median outside [1, 50] GeV is itself a STOP to the director.
- **The declared spot rows,** per playlist: the first row, the last row, and 64 distinct rows drawn without replacement
  by `numpy.random.default_rng(SeedSequence([20261124, 17, k + 1])).choice(rows, 64, replace=False)`, with k the
  playlist index.
  - flux4 records each spot row's (run, subrun, event) and Eν in GeV in its record. That is 792 rows in all.

**Part 2, in P0, in the numerical environment that reads ROOT files with uproot.**
- **Why P0:** the MAT process (root_6_28) has no uproot. A ROOT tree read inside the traced extract would load
  libraries the custody policy has not pinned, and custody STOPs on those.
- **The director's placement conditions** (2026-11-24):
  - **Order.** Part 2 is the first P0 work that reads flux4's output after P0 checks that output's identity. The flux
    factors, spectra and products are used only after part 2 passes.
  - **A failure is a STOP.** If part 2 fails, P0 STOPs, and flux4's factors are used by nothing. `d2-predict` and every
    later step require P0's passing record, so no flux4 product reaches a control or a reading before part 2 passes.
- **The omnifiles:** the 12 are pinned at c2's sha256s and staged by O_NOATIME copy. A pin mismatch is a STOP.
- **The spot rows** are read from flux4's pinned record, not recomputed from the seed. P0 requires each playlist's
  record to:
  - list sorted, distinct rows inside the dump, including its first and last rows, with at least
    min(64, rows) of them;
  - give one (run, subrun, event) and one Eν per row.
- **The checks, for each spot row:**
  - the row's (run, subrun, event) must be in that playlist's `mc_signal_reco` exactly once;
  - at that entry, `truthx_enu / 1000` equals the recorded Eν, bitwise;
  - `float32(MC)` and `float32(MC_pz)` equal `lat_<PL>`'s MCgen[i, 0] and MCgen[i, 1] bitwise. This is the dump's cast
    (`rdx_truthx_npz.py`), so `lat_<PL>`'s MCgen must itself be float32; any other dtype is a STOP;
  - the recorded Eν equals the `energy` column of flux4's pinned product at row i, bitwise.

## 5. The controls with true Eν

The strata are unchanged: p∥ [1.5, 8), [8, 15) and [15, 60], by reconstructed p∥, over the `pass_reco` weight. Each is
a STOP where the declaration made it one.
- **C-E1:** Eν is finite and Eν ≥ Eμ for at least 99.9% of the `pass_reco` weight in each stratum.
  - The declaration's "denominator > 0" clause belonged to the inversion, and true Eν has no denominator.
  - The 99.9% bar is unchanged.
- **C-E3, unchanged:**
  - q₃′ = √(4EνEμ sin²(θ/2) + (Eν − Eμ)²), against MCgen's q₃;
  - θ = atan2(p_T, p_∥) and Eμ = √(p_T² + p_∥² + m_μ²), from MCgen;
  - in each stratum the weighted median of |q₃′/q₃ − 1| is ≤ 0.002, and the 99th percentile ≤ 0.03.
  - With true Eν, C-E3 tests the q₃′ formula against `Getq3True` and the row join. A misjoined row would fail it by
    orders of magnitude.
- **C-E2, reported, not a gate:**
  - the M_n against M_p spread of the inversion, as before;
  - also, the weighted median and 99th percentile of |Eν_inv/Eν − 1|, where Eν_inv is the declaration's
    mean-mass inversion.
- **The out-of-range STOP, unchanged:** more than 0.1% of PB's `pass_reco` weight in p∥ 1.5–15 outside the common Eν
  range. The flux factor is applied at true Eν by the bound `mat_flux_swap`, unchanged.

## 6. What changes, what reruns, and the price

**The code** (each change goes to the director for its own binding, with tests, a line trace and mutants):
- **`nd-unfolding/fd_rpd_reco.py`:**
  - a checked sidecar reader (C-JOIN part 1);
  - `flux-extract` evaluates the factors at true Eν and writes `energy` (GeV) into each `flux-factors-<PL>.npz`, with
    the spot rows in its record;
  - P0 runs C-JOIN part 2;
  - `pinned_flux_factors` checks the `energy` column;
  - `aggregate` passes that column to the C-E controls.
  - From P0 on, no step reads the sidecar.
- **`nd-unfolding/fd_rpd_reco_custody.py`:** `prepare` stages the sidecar like the other declared inputs, so the trace
  policy protects its original.
- **The configuration** gains the sidecar's path and sha256, the `lat_zero` sha256 and the 12 omnifile pins.

**What reruns, in order, each bound:** flux4 → P0 (dry, then run) → d2-predict + step0 → the c0 harness → c0. The
flux3, P0 and d2s0 records stay as history.

**The price:**
- **Eν itself: 0 node-h.** No event loop, no dump and no GPU.
- **flux4:** a shared-QOS job like flux3, which charged 0.0058 node-h (531 s at 10 of 256 CPUs,
  `fd/rpd-reco/flux3-20261123/run-61861637/README.md`). It adds one 2.4 GB staged copy and the sidecar checks, so flux4
  is priced again with its package.
- **P0 and d2-predict + step0:** login steps, as before.
- **c0** keeps its harness and pricing: c0 draws × S_real × 1.5, against a fresh iris read.

## 7. Tests (added to `nd-unfolding/tests/test_fd_rpd_reco.py`)

- **The sidecar reader, each refusal in the direction it acts:**
  - wrong schema;
  - a `npz_sha256` that is not the configured one;
  - a row-count disagreement;
  - wrong names or dtypes;
  - a playlist index out of range;
  - a decreasing index;
  - a block size that differs from its `lat_<PL>`;
  - a non-finite or non-positive Eν.
- **The units band:** a fixture whose `truthx_enu` is already in GeV (so divided twice) is refused, and so is a reader
  that skips the division.
- **C-JOIN part 2:**
  - a spot row whose id is missing from its omnifile, or appears twice;
  - an Eν, MC or MC_pz that differs by one ulp;
  - a spot-row list that is unsorted, repeated, out of range or missing its first or last row (P0), and one that
    differs from the seed's (flux4);
  - a product `energy` that differs from the record;
  - a MCgen that is not float32;
  - P0 stopping when an omnifile is not at its pin.
- **The C-E controls with true Eν:**
  - C-E3 passes on a consistent fixture and fails with Eν scaled by 1%, the declaration's test;
  - C-E1 fails with Eν < Eμ on more than 0.1% of a stratum's weight;
  - `d2-predict`'s controls read the product's `energy`: scaling it by 1% makes C-E3 STOP.
  - The fixture's true energy is offset by 10⁻⁶ from its own inversion, so a reader that fell back to the inversion is
    caught bitwise.
- **The product:** `pinned_flux_factors` refuses a missing, non-finite or wrong-length `energy` column.
- **The custody prepare** stages the sidecar, and the trace policy lists its original as protected.

## 8. Risks

- **Purge.** The sidecar was written on 2026-11-17 and the omnifiles on 2026-11-15 to 11-17. Their purge exposure is from
  about 2027-01-12, 56 days after they were written. tier3-design knows of no read since (2026-11-24) and has not
  checked their atimes, so this date is an estimate.
  - The flux4 and P0 connects stat each one first.
  - **If any has been purged by run time, the run STOPs.** Nothing is regenerated without the director.
- **C-E3 may still fail**, if the q₃′ formula and `Getq3True` differ by more than the gates in some stratum. That is a STOP
  to the director, as before. The gates are not loosened.
- **The owner of the source is another lane.** tier3-design's ack is on record (§2), and a fresh one comes before each
  connect.

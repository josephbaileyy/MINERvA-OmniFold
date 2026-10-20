# MP3-C: GiBUU 2019 on a free proton, STOPPED at gate B3

**By** the measurement session, 2026-10-20, under MP3-C (PLAN.md §4.2 rank 3; BINDING-PHASE1-20261019 §2 granted the
probe; the director granted production by message on 2026-10-20, under MP3-B's frozen pipeline). This file was written
by the coordinating session from the agent's report text, because the agent's write was refused.

**CITABLE FOR:**
- GiBUU runs on an A = 1 target with free-proton channel content;
- the frozen GiBUU build's sampling closure fails within points on hydrogen and holds on carbon;
- the charge.

**NOT CITABLE FOR:**
- any GiBUU-on-CH number;
- any gate verdict beyond B3;
- anything about A7, whose GiBUU decisions stand as frozen;
- any claim.

**Outcome.** The probe passed. Production generated all 80 tasks. C0, C1′, B1 and B2 passed, with B2 rebuilding the
frozen GiBUU product bitwise. **B3′ failed**, so under the spec ("On B1–B3 failure: no CH prediction is reported;
STOP") no CH prediction or replay exists.

The borrowed GENIE-hydrogen variant was **not** run. The director allowed it only if GiBUU-H "cannot run at all", and
GiBUU ran.

## 1. Card, seeds and environment

- **Card.** The frozen jobcard (`d00a622c…`) with exactly four changes: target_Z 6 → 1, target_A 12 → 1,
  include2p2hQE T → F, numEnsembles 4000 → 48000. GiBUU itself sets an elementary nucleus with density and Pauli
  blocking off.
- **Seeds.** SEED = N·7919 + 12345, with N = 1000 for the probe and N = 1001–1080 for production. They were declared in
  `measurement-paper/phase1/mp3c/SEEDS.txt` (sha256 `c4570937…`) before submission.
- **Environment fix.**
  - The first probe attempt (60029251) segfaulted at startup. The frozen C12 card fails the same way: GiBUU.x's ROOT
    needs the `root_6_28` C++ toolchain on PATH, and `setup_gibuu.sh` does not set it.
  - The fix is to activate `root_6_28` before `setup_gibuu.sh`. It changes the environment only; the card is
    unchanged.
  - `mp3c_probe.sh` changed from blob `a90904b1` to `6c83d89e`. The failed attempt generated no events, and its
    directory was moved aside.

## 2. Probe (60029299): PASS

- **Run.** One task, 19,148 events in 88 s wall on one core (≈ 4.6 ms/event), 1.8 GB RSS.
- **Channels.** Δ 32% of σ, higher resonances 6%, DIS 62%. **QE = 0 and 2p2h = 0.**
- **σ_H/σ_C12 per nucleon.** 0.562 on the 0–20 GeV cut flux against one C12 task; 0.580 in-grid against the full
  80-task C12 product (H ±1.5%). That is the low end beside NuWro's 0.642 and GENIE's 0.66. Those are full-flux
  numbers, and GiBUU's 20 GeV cap (KI 82) weights the low-energy region, so the comparison is not like for like.
- **The spectator target row.** Each event lists the untouched real target proton with perweight 0, which the frozen
  converter already excludes. The agent's extra hadronic-charge +2 check, added beyond the frozen gates, first counted
  that row. It was redefined as a reported diagnostic, not a gate, and that is recorded here.

## 3. Production (60029398)

| step | result |
|---|---|
| generation | 80/80 tasks, rc 0, ≈ 111 s wall each; none discarded |
| C0 | **PASS**: all 80 cards differ from production in exactly the four declared values |
| C1′ (converter identity) | **PASS**: `extract_gibuu` on the 80 frozen C12 files (r = 1) reproduces the pre-fix `gen5d/gibuu_cv_xsec5d.npz` bitwise (xsec, sumw2, nevt) |
| B1 | **PASS** in 80/80 tasks: no QE, no 2p2h, one real proton target per event. Diagnostic: the perturbative charge is +1 instead of +2 in ≈ 3e-4 of events (the final nucleon is absent), carrying a median 5.5e-4 of σ per task (max 1.7e-3) |
| B2 | **PASS**: the frozen `gibuu_cv_xsec5d_fluxfix.npz` is rebuilt bitwise, and its sampling statistics are reproduced |
| **B3′** | **FAIL** (below) |
| B4, readout, replay | not run |

**B3′, the frozen GiBUU build's own sampling closure.**
- The structural checks pass: alignment holds, there is no zero-flux event, the flux density equals the frozen one, and
  E_max is 19.999 GeV.
- At E ≥ 1.5 GeV, the across-bin count test passes (p = 0.186), but the **within-bin χ² is 248.8 / 148, p = 4.1e-7
  < 1e-3: FAIL**.
- The edge-jump test passes (p = 0.48).
- The frozen C12 values for comparison: within-bin 167.0 / 148 (p = 0.136), edge-jump p = 0.196.

**Read-only diagnosis.**
- On hydrogen, counts rise systematically across every 0.5 GeV flux point from 1.5 to about 5 GeV: the sub-bins run
  0.945 → 1.048 of uniform at 1.5–2.0 GeV, a 2.5–5% rise at 2.5–3.5 GeV. Carbon is flat at the same energies
  (0.98–1.02).
- So the test's premise, a constant keep probability within each flux point above 1.5 GeV, holds on carbon but not on
  the free proton.
- The frozen build states that the r(E) reweight depends only on the proposal density, not on the keep probability.
  If that is right, the failure is a failed premise check rather than a demonstrated bias. **That is untested.**

## 4. Options put to the director (2026-10-20)

- (a) A hydrogen-specific B3, declared before it is computed.
- (b) A direct bias test: the per-J-cell H prediction under the frozen r(E), against a reweight that also corrects the
  measured within-point slope, accepted if the per-cell difference is within a declared bound. Recommended.
- (c) The borrowed variant, "mixed: GiBUU carbon + GENIE hydrogen; not GiBUU-on-CH".
- (d) Defer.

The events exist, so (a) or (b) needs only ≈ 0.05 node-h of evaluation. Pending the ruling.

## 5. Jobs and charge (ElapsedRaw × billing / 256 / 3600)

| job | QOS | State | Exit | ElapsedRaw | billing | CPU node-h |
|---|---|---|---|---:|---:|---:|
| 60029251 | debug | FAILED (startup segfault, environment) | 3:0 | 8 | 256 | 0.002222 |
| 60029299 | debug | COMPLETED (probe) | 0:0 | 99 | 256 | 0.027500 |
| 60029398 | debug | FAILED (B3 STOP) | 1:0 | 160 | 256 | 0.044444 |

- **Total:** MP3-C 0.0742 CPU node-h; 0 GPU.
- **Storage.** Under `/pscratch/sd/j/josephrb/measurement-paper/phase1/mp3c/`:
  - `prod/` 1.2 GB (FinalEvents, cards and logs; the ≈ 1.6 GB per task of GiBUU analysis files were deleted);
  - `probe/` 15 MB;
  - `diag/` 269 MB.
  - Nothing is on CFS.

## 6. Not established

- Whether the within-point slope biases the r(E)-reweighted prediction.
- The slope's cause inside GiBUU.
- The cause of the missing final nucleon in ≈ 3e-4 of events.

## 7. Files

- **Code:** `measurement-paper/phase1/mp3c/` (`SEEDS.txt`, `mp3c_card.py`, `mp3c_probe.py`, `mp3c_probe.sh`,
  `mp3c_size.py`, `mp3c_build.py`, `mp3c_eval.py`, `mp3c_prod.sh`).
- **Evidence:** this directory (`logs/`, `probe/probe.json`, `out/build/mp3c_build.json`, the production sha lists and
  a sample card).

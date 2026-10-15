# AUTHORIZATION 2026-10-14 — 2D closeout: per-period unfold test of the playlist spread

**Issued by** the paper-tighten lane, as director, under the 700 node-h delegation
([`AUTHORIZATION-20261012-2d-closeout-delegation.md`](AUTHORIZATION-20261012-2d-closeout-delegation.md)).

**Joseph's approval**, 2026-10-14, in the director's session, answering "Shall I go ahead with the test?": "you can
run the small unfold test". The test was proposed after
[`state/2d-closeout/playlist-spread-20261014/coverage/REPORT.md`](state/2d-closeout/playlist-spread-20261014/coverage/REPORT.md)
found the playlist spread PARTLY COVERED.

**CITABLE FOR:**
- the scope, ceiling and binding of the per-period unfold test;
- the running total of committed grant ceilings under the delegation.

**NOT CITABLE FOR:**
- any result of the test;
- adopting a playlist-consistency uncertainty, or any change to the quoted covariance VL175. That is Joseph's
  decision after the result;
- any Stage C production job, or any change to the Stage C pilot.

## 1. Scope

Unfold three run periods separately with the production driver and the Stage C closeout config, each with its own
POT scale and its own data-POT-weighted flux:
- **P_A** = 1A–1F;
- **P_B** = 1G, 1L, 1M;
- **P_C** = 1N–1P.

Add a **control**: all 12 playlists merged by the same pipeline. It must reproduce XR-L0 and `E_U` to 1e-8 on every
cell and the integral.

The questions are whether the reco-level 1G–1M p_∥ step at 8 GeV/c survives unfolding, and how the 1N–1P excess and
the J36 mix error look after unfolding. The metric is the coverage record's: χ² against VL175 on the marginals and
the 2D cells, set against a noise reference from data, MC and estimator-seed fluctuations.

## 2. Ceiling and jobs

| item | value |
|---|---|
| ceiling | **6.0 charged CPU node-h** for every `pu_*` job, including retries and cancelled jobs, recomputed from `sacct` (ElapsedRaw × billing ÷ 256) |
| jobs | 37 rows of `jobs.tsv`, 1 node each, QOS `shared`, `--constraint=cpu`, 64 CPUs, billing 64, account m3246; every walltime ≤ 00:50:00 |
| enforced reservation | 4.958 node-h for all 37 at their caps |
| median expectation | 1.04 node-h (0.84–1.34), scaled from `sacct` of P0_default `59733771` (935 s), L0 `59660487` (836 s) and 13 P1_fixed replicas `59753253–59753304` (median 934 s) |
| batches | **B0** = control + 3 period centrals (0.604 node-h at caps). **B1** = 3 seed-43 runs + 30 bootstrap replicas, which `launch.py` refuses until `results/control.json` says PASS |
| retries | at most one per job name, for a walltime or node failure, inside the ceiling; an unexplained failure stops the test and goes to the director |
| namespace | `/pscratch/sd/j/josephrb/2d-closeout-period-unfold-20261014/` only. Nothing in `/pscratch/sd/j/josephrb/MINERvA-OmniFold`, the Stage C pilot namespace or CFS is written |
| window | jobs must finish before the Perlmutter maintenance window opens on 2026-10-21 06:00 UTC. On 2026-10-15 at 03:4x UTC every CPU partition was down (`sinfo`), so the queue start is not known |

**Against the delegation.** Committed grant ceilings rise from 26.0 to **32.0** of 700 node-h:
- Stages A–B: 2.0;
- the flux repair: 1.0;
- Stage B diagnostics: 3.0;
- the Stage C pilot: 20.0;
- this test: 6.0.

## 3. Binding

The package is [`state/2d-closeout/period-unfold-20261014/`](state/2d-closeout/period-unfold-20261014/), committed
with this record. The deployed copy under `$NS/code/record/scripts/` must match these sha256 values before B0 is
submitted:

| file | sha256 |
|---|---|
| `jobs.tsv` | `c2283eb37343780b1b4d3754f8e5dc323480b102ddf9a9d0c13d858b237f5421` (also pinned in the sbatch script) |
| `sbatch_period_unfold.sh` | `6a27a17f9cf060bde452d0705a41840e6fec55682bb18be5257fb7b042aea0c6` |
| `launch.py` (`CEILING = 6.0`) | `cd8d46f86b700ee5256558b2e9c9615ed84c3e46e30f0371aa7eca09c0f1b7c4` |
| `analyze_periods.py` | `912af1ddfbae2e28a2cba6e6843b0985e2442adb4b1e775a22d4c547b8d8ebc5` |
| `build_inputs.sh`, `build_flux.py`, `verify_inputs.py`, `periods.py` | `2fb36144…`, `61b580bc…`, `383c434a…`, `d37c1a8f…` |
| producer `unfold_2d_omnifold_unbinned.py` | `74a4ed69c3fa9c4ae5b6866f36343212b8d3f903fddde6c7bd40c382c1167d56` (git archive of main `c67dbdda`) |
| helper `omnifold.py` | `e96234124a31edd7a8dd61fdb16cb48a5b28cbd1b90202f59b0095868378227a` |
| inputs, omnifile / flux | ALL `a7a4bcb3…` / `e3dc9e63…`; PA `1d2f5b37…` / `927f5af2…`; PB `200fd1dd…` / `c64637d5…`; PC `eedbb5dc…` / `95c45a5f…` (full values in the sbatch script and `outputs/SHA256SUMS.inputs`) |

Each job re-checks the producer, helper, input and flux digests, its own `jobs.tsv` row and its granted QOS, CPUs,
TimeLimit and billing. It refuses on any mismatch.

## 4. Director's review of the package

The director read `sbatch_period_unfold.sh`, `jobs.tsv` and the gate in `launch.py` (`CEILING = 6.0`, lines 25 and
55–100). The gate counts terminal `pu_*` charges, plus full caps for in-flight jobs, plus the batch's caps. It refuses
on an unreadable `sacct`, a duplicate name, or B1 without control PASS. The input verification
(`outputs/inputs_verify.json`) is PASS: POT, entry counts and branch values equal the per-playlist sums, and the
control input equals L0's `43f8cc16…`. The analysis self-test (`outputs/selftest.json`) is PASS.

**Known limits, carried to the result.** These are stated in the package and must be stated in its REPORT:
- one seed pair per period;
- possible pull of each period toward its own MC prior at 5 iterations, with no closure test of step survival;
- approximate noise terms for comparisons against the pooled result, and for J36;
- the ill-conditioned full 205-cell χ², so the marginals lead;
- P_A includes 1F, while the reco reference was 1A–1E.

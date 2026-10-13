# AUTHORIZATION 2026-10-13 — 2D closeout: Stage C pilot P0–P3 and the Flux G2 case (P2-G2)

**Issued by** the paper-tighten lane, as director, under
[`AUTHORIZATION-20261012-2d-closeout-delegation.md`](AUTHORIZATION-20261012-2d-closeout-delegation.md) §3.
It responds to the 2d closer's pilot request of 2026-10-13, which uses the unit costs of
[`state/2d-closeout/stageB/REPORT.md`](state/2d-closeout/stageB/REPORT.md) §7. It follows the Stage B outcome
recorded in
[`AUTHORIZATION-20261013-2d-closeout-stageB-exit.md`](AUTHORIZATION-20261013-2d-closeout-stageB-exit.md):
EXIT CONDITIONAL on K1 (the July bridge) and K2 (G2 in a Flux universe).

**CITABLE FOR:**
- the Stage C pilot P0, P1, P2 and P3, as defined in Stage B §7;
- the added item P2-G2 below;
- the pilot's measured costs, memory and walltimes, and the repriced production estimate.

**NOT CITABLE FOR:**
- production (S1–S5);
- a G2 repair or a July rebuild;
- any quoted product, rollup or budget;
- adoption, claims, the KI-85 lift or publication changes;
- edits to the production driver or event loop on `main`, unless they come through their own reviewed PR.

## 1. Two-step activation

The delegation requires a grant to bind a package commit and a manifest digest. The pilot package does not
exist yet. It needs:
- the producer bridge;
- the three-stream bootstrap code of R5;
- the P2 envelope;
- the P2-G2 universe choice;
- the sbatch scripts and their guards.

So this record admits the **scope and the ceiling**, and **no job may be submitted** until both steps below
are done:

1. **Package.** The closer commits a pilot package:
   - `state/2d-closeout/stageC/pilot/DESIGN.md` plus its scripts;
   - a fresh read-only verifier gives APPROVE (one initial review, at most two focused re-reviews, plan §5).
   - The DESIGN freezes, before any job:
     - every check, envelope and threshold in §2;
     - each job's walltime, set at 1.5 × a projection from measured loop rates rather than a one-file smoke;
     - the job list and names;
     - the output namespace.
2. **Binding.** The director reviews the package and commits a short binding addendum to this record. The
   addendum names:
   - the package commit;
   - the manifest digest;
   - the enforced worst-case charge per job.

   The addendum must be on `origin/main` before any job is submitted (delegation §3.1).

The package pins the production driver at sha256 `74a4ed69c3fa9c4ae5b6866f36343212b8d3f903fddde6c7bd40c382c1167d56`
(`main` `ec2088a6`, PR #108: the R0 citation-comment fix, comment only). P0 bridges that digest against L0,
and production pins the same digest.

## 2. Items

| item | content | runs | node-h (Stage B unit costs) | terminal outcome |
|---|---|---|---|---|
| P0 | producer bridge: the current-driver default CV unfold vs L0 (frozen 1e-8), plus the derived path on the CV | 2 × u_CV | 0.12–0.13 | PASS or FAIL. A FAIL stops the pilot: the producer is not frozen |
| P1 | statistical streams at seed 42: 20 joint, 20 fixed-purity and 20 bkg-only, with the checks declared in Stage B §7. The three-stream code is new and needs a reviewed diff and the b ≡ 1 no-op control before its first job | 60 × u_CV | 3.5–4.0 | each declared check PASS or FAIL. The paired σ ratio is MEASURED with its uncertainty and has no pass/fail |
| P2 | universe cases on the July inputs with the frozen producer: `NormDISCC_0`, `MaRES_0`, one large Flux universe and `Muon_Energy_MINOS_0`, on the derived path, plus one default run | 4 × u_U,sel + 1 × u_U | 1.7–3.8 | **K1:** PASS or FAIL against the envelope frozen in the DESIGN |
| P2-G2 | an off/on miss-row-weighting pair on one Flux universe, using a pilot copy of the P5 scripts (named `2dc_C_G2_*`, pinned to the driver above), not the MaRES-specific `sbatch_p5.sh`. **Selection:** the Flux universe with the largest median \|c_off − 1\| over the 205 reported cells, computed from inputs before any P2-G2 run, with its max also quoted. The DESIGN says whether this is the same universe as P2's Flux case and uses one choice where it is suitable. **Re-declared for that universe and frozen before data:** σ_band for a many-universe band, its floor, and the gate values (n_override, the G-c reference). The r1/r3 thresholds stay at P5's 0.10, 0.30 and 2, unless a Flux-specific reason is written into the DESIGN before data. P5 DESIGN §6–7's routing logic is otherwise unchanged. **Seed-43 confirmation** is conditional as in P5 DESIGN §7. Its frozen row applies: a failed or not-MEASURED pair means INCONCLUSIVE. The pair launches on the pre-declared actual-charge check against this record's ceiling, without a further go-ahead, and the check figures are reported | 1 pair, plus 1 conditional pair | 0.35–0.5 per pair (measured P5 pairs 0.348 and 0.376) | **K2:** MATERIAL, NOT RESOLVED ABOVE TRAINER NOISE, NOT MATERIAL or INCONCLUSIVE. Only NOT MATERIAL or NOT RESOLVED passes. MATERIAL or INCONCLUSIVE goes to the director and from the director to Joseph (exit record §1) |
| P3 | laterals from the active files on CFS: `BeamAngleX_0` and `Muon_Energy_MINOS_0` | 2 × u_A | 0.5–1.4 | MEASURED with the u_A cost, or INCONCLUSIVE |

| total | node-h |
|---|---|
| **subtotal** | 6.2–10.3 |
| **admitted** (subtotal / 0.8, a ≥ 20% reserve) | 7.7–12.9 |

## 3. Bounds

| item | value |
|---|---|
| executor | 2D closeout executor (2d closer) |
| ceiling | **≤ 12.9 charged CPU node-h** for every pilot job, retries, controls and cancelled jobs included. Charge is `sacct` ElapsedRaw × billing / 256 |
| against the 700 node-h delegation ceiling | Committed grant ceilings to date are 18.9 node-h: Stages A–B 2.0, flux repair 1.0, Stage B diagnostics 3.0 and this pilot 12.9. Charged so far is 1.2524 node-h. The director measured this from `sacct` on 2026-10-13: every `2dc_*` job since 2026-10-10 was a `2dc_B4`/`2dc_B5` job (26 rows), and no `2dc_AB_*` or `2dc_C04_*` job ran. Stage B §7 requested 15.0 for P0–P5 together; P4–P5 used 1.2524 of it, and this grant takes 12.9 of the remaining 13.75 |
| per job | walltime < 12 h, set at 1.5 × a measured projection; CPU only; shared or regular QOS, never premium |
| job names | `2dc_C_<item>_<tag>` |
| namespace | `/pscratch/sd/j/josephrb/2d-closeout-stageC-pilot-20261013/` (new); durable copies go to CFS `m3246`, sha256 re-measured; nothing is written to a publication namespace |
| inputs | the CFS Stage C copy (`/global/cfs/cdirs/m3246/josephrb/2d-closeout-stageC-inputs-20261012/`, read-only, SHA256 MATCH), the July products and `E_U` `4f5a1b6d…`, each sha-checked by the job |
| attempts | one walltime retry per job, at 1.5 × a projection re-measured from its own partial progress. Any other failure needs a diagnosed infrastructure cause. A scientific result is never a reason to retry. A second failure is INCONCLUSIVE |
| order | P0 first. P1, P2, P2-G2 and P3 run only after P0 PASSES |
| stop | a P0 FAIL, a failed no-op control, a failed identity, a K1 FAIL, or the ceiling about to be exceeded: stop that line of work, diagnose, and report to the director. No replacement product is built under this grant |
| record | `docs/orchestration/state/2d-closeout/stageC/pilot/REPORT.md`, checked by a fresh read-only verifier. It gives the K1 and K2 terminal outcomes, every job's `sacct` row, measured unit costs, peak memory, and a production budget (S1–S5) repriced from the pilot with a ≥ 20% reserve |
| window | until the pilot REPORT, or 2026-10-27 |

Production needs its own grant. The director issues it after the pilot REPORT, if K1 PASSES and K2 routes
NOT MATERIAL or NOT RESOLVED ABOVE TRAINER NOISE. The other branches follow the exit record:
- if K1 FAILS, the cause is diagnosed and reported first. Any July rebuild needs its own committed grant record;
- if K2 routes MATERIAL or INCONCLUSIVE, the question goes to Joseph before any production grant.

The director reports the pilot's terminal outcomes and the Stage B exit to Joseph (delegation §3.6).

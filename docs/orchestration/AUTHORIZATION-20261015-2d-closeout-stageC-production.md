# AUTHORIZATION 2026-10-15 — 2D closeout: Stage C production (S1–S5)

**Issued by** the paper-tighten lane, as director, under
[`AUTHORIZATION-20261012-2d-closeout-delegation.md`](AUTHORIZATION-20261012-2d-closeout-delegation.md) §3. It
follows the Stage C pilot REPORT
([`state/2d-closeout/stageC/pilot/REPORT.md`](state/2d-closeout/stageC/pilot/REPORT.md), PR #129, merge
`677b5ba4`):
- **K1 PASS** on all five comparisons;
- **K2 NOT RESOLVED ABOVE TRAINER NOISE**, with the seed-43 confirmation NOT CONFIRMED;
- 7.2479 of 20.0 node-h charged.

The pilot grant routes production to the director when K1 PASSES and K2 routes NOT MATERIAL or NOT RESOLVED
([`AUTHORIZATION-20261013-2d-closeout-stageC-pilot.md`](AUTHORIZATION-20261013-2d-closeout-stageC-pilot.md) §3).
Both hold. So **Stage B exit is MET**
([`AUTHORIZATION-20261013-2d-closeout-stageB-exit.md`](AUTHORIZATION-20261013-2d-closeout-stageB-exit.md) §1).

**CITABLE FOR:**
- the scope, ceiling and bounds of Stage C production S1–S5;
- Stage B exit MET;
- the running total of committed grant ceilings under the delegation.

**NOT CITABLE FOR:**
- how G2 is carried or disclosed. That is Joseph's decision; the director's recommendation goes to him with this
  record;
- a G2 repair, a July rebuild, or any Stage D/E work;
- adoption of any product, claims, the KI-85 lift or publication changes;
- a playlist-consistency term. That waits on the per-period unfold test
  ([`AUTHORIZATION-20261014-2d-closeout-period-unfold-test.md`](AUTHORIZATION-20261014-2d-closeout-period-unfold-test.md))
  and on Joseph;
- edits to the production driver or event loop on `main`, except through their own reviewed PR.

## 1. Two-step activation

This record admits the **scope and the ceiling** only. **No job may be submitted** until both steps are done:

1. **Package.** The 2d closer commits a production package under `state/2d-closeout/stageC/production/`: a
   DESIGN, scripts and a manifest. A fresh read-only verifier must give APPROVE (one review, at most two focused
   re-reviews). The DESIGN freezes, before any job:
   - the job list, names and output namespace;
   - each family's walltime, at 1.5 × a projection from the pilot's measured elapsed times. For u_CV, use the
     max of the 60 P1 replicas, 2,003 s;
   - the QOS and CPUs per family;
   - the rollup, matrix and repair steps of S5, with their inputs and digests;
   - the gate's batching rule (§2).
2. **Binding.** The director reviews the package and commits a binding addendum to this record. It names:
   - the package commit;
   - the manifest digest;
   - the enforced worst-case charge per job and in total.

   The addendum must be on `origin/main` before any job is submitted.

The package pins the production driver at sha256 `74a4ed69c3fa9c4ae5b6866f36343212b8d3f903fddde6c7bd40c382c1167d56`,
which is the driver P0 bridged. It also pins the helper `omnifold.py` at `e96234124a31…`, as the pilot did.

## 2. Items and price

The run counts are Stage B §7's. The units are the pilot's measured units (pilot REPORT §7).

| item | runs | admitted range (node-h) |
|---|---|---|
| S1 statistical ensemble, 300 replicas, three streams | 300 × u_CV | 22.6–28.0 |
| S2 bkg-only separable arm, 100 replicas | 100 × u_CV | 7.5–9.3 |
| S3 remaining 8 laterals from active files | 8 × u_A | 2.6–3.1 (shared, 128 CPUs) |
| S4 `C_ML` factorial: (i) 20 bootstrap × 5 seed triplets; (ii) 7 universe settings × 5 seeds | 100 × u_CV + 35 × (u_U,sel…u_U) | 12.5–21.5 (shared, 128 CPUs) |
| S5 rollups, C04/X01/KI-92 repairs, matrices | login node | 0 |
| **subtotal** | | 45.3–61.9 |
| **admitted** (subtotal / 0.8, a ≥ 20% reserve) | | 56.6–77.4 |

The pilot's alternatives:
- regular nodes for the universe and lateral unfolds: admitted 66.1–96.4;
- a × 1.85 spread on u_U and u_A: up to 93.5 on shared nodes, or 128.7 on regular nodes.

## 3. Bounds

| item | value |
|---|---|
| executor | 2D closeout executor (2d closer) |
| ceiling | **≤ 100.0 charged CPU node-h** for every production job, including retries, controls and cancelled jobs. Charge is `sacct` ElapsedRaw × billing ÷ 256 |
| why 100 | It covers the shared-QOS admitted high edge (77.4), and the regular-node alternative (96.4) if shared capacity forces regular nodes for the universe and lateral unfolds. It does not cover the regular-node × 1.85 corner (128.7). Reaching it is a stop (below), not a reason to loosen anything |
| against the 700 node-h delegation ceiling | Committed grant ceilings rise from 32.0 to **132.0**: Stages A–B 2.0; flux repair 1.0; Stage B diagnostics 3.0; Stage C pilot 20.0; period-unfold test 6.0; this grant 100.0 |
| gate | It counts terminal charges from `sacct`, plus the **full cap of every job pending or running**, plus the batch's caps, and checks the sum against the ceiling. It refuses on an unreadable `sacct`. Because queued caps count in full, S1/S2/S4(i) are submitted in batches (pilot REPORT §7, "Gate sizing") |
| per job | walltime < 12 h, from §1's projection rule; CPU only; QOS shared (preferred, as measured) or regular, never premium |
| job names | `2dc_P_<item>_<tag>` |
| namespace | `/pscratch/sd/j/josephrb/2d-closeout-stageC-production-20261015/` (new). The durable copy goes to CFS `m3246` with sha256 re-measured. Products are stored as `xsec.root`/JSON/NPZ only: the inputs are already on CFS and are **not** copied again (Joseph's CFS area is over his 3 TB rule; see [`state/2d-closeout/preservation-20261014/cfs-copy-1A-mc/REPORT.md`](state/2d-closeout/preservation-20261014/cfs-copy-1A-mc/REPORT.md)). Nothing is written to a publication namespace |
| inputs | the CFS Stage C copy (`2d-closeout-stageC-inputs-20261012/`, read-only), the July products and `E_U` `4f5a1b6d…`, each sha-checked by the job |
| attempts | one walltime retry per job, at 1.5 × a projection re-measured from its own progress. Any other failure needs a diagnosed infrastructure cause. A scientific result is never a reason to retry. A second failure is INCONCLUSIVE for that job |
| order | a no-op control first (b ≡ 1, reproducing `E_U`/L0 to 1e-8). Then S1–S4 in the order the DESIGN freezes. S5 only after every unfold it reads is terminal |
| stop | a failed control or identity, a gate refusal, the ceiling about to be exceeded, or a product outside a frozen DESIGN check. Stop that line, diagnose, and report to the director. No replacement product or alternative recipe is built under this grant |
| maintenance | Perlmutter maintenance runs 2026-10-21 06:00 to 2026-10-28 06:00 UTC. No job may be planned to straddle it |
| record | `state/2d-closeout/stageC/production/REPORT.md`, checked by a fresh read-only verifier. It gives every job's `sacct` row, the gates, the products and their digests, the S5 matrices, and the terminal outcome |
| window | until the production REPORT, or 2026-11-15 |

## 4. G2, for Joseph

K2 passed. The exit record's pre-declared recommendation therefore applies, and it goes to Joseph:
- carry G2 as a **disclosed approximation**;
- name both universes measured, `MaRES_0` (P5) and `Flux:23` (P2-G2, seeds 42 and 43);
- state that an effect below trainer noise is not excluded.

Production does not depend on that wording. A G2 repair, if Joseph ever asks for one, needs its own priced grant:
43–129 node-h on record.

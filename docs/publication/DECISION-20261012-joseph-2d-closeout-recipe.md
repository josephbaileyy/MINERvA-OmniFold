# DECISION 2026-10-12 — 2D closeout recipe decisions (R2, R5, C07′, G3)

Joseph's rulings on the decisions that the 2D closeout Stage B recipe
(`docs/orchestration/state/2d-closeout/stageB/REPORT.md` §4, PR #96) reserves for him. The paper-tighten lane put
each to him in its session on 2026-10-12, with the options below. The answers are quoted verbatim, each with the
SHA-256 of the answer text plus a final newline.

**CITABLE FOR:** what the Stage C recipe and grants may assume.

**NOT CITABLE FOR:**
- adopting any built product: each needs its own adoption after verification;
- any number;
- a KI-85 lift.

| item | question (summary) | Joseph's answer | sha256 |
|---|---|---|---|
| **R2** (KI 95) | the flux band omits MAT's ν-e/IMD constraint weights; repaired, the total median drops from 6.87 % to about 6.09 % | `Build repair now (Recommended)`: the C04+X01-repaired covariance is built as a committed, verified product, then adopted and re-quoted; the rest of Stage C continues later | `b6b33d0a…` (see [`AUTHORIZATION-20261012-2d-closeout-fluxrepair.md`](../orchestration/AUTHORIZATION-20261012-2d-closeout-fluxrepair.md) §1) |
| **R5** (KI 94, P07) | three-stream seed-42 bootstrap (data, signal MC, background MC), with purity recomputed from the resampled data and background; an estimator-contract change; central value unchanged | `Adopt three-stream (Recommended)` | `cd918ce98e65c88a455b0934fef62e249d860a3efc5ec31d380da2a21b898148` |
| **C07′** | data POT counting has no uncertainty band | `Add a band if documented (Recommended)`: if MAT or the published analysis documents a POT-counting uncertainty, add it as a fully correlated normalization band like the 1.4 % target band; otherwise disclose it as omitted | `91652ac70f3f80797821e81bdfff42e6f8375c723aed3bba96df3e085eb0ca6d` |
| **G3** | the NormDISCC band is null in the products; whether that is intended is a collaboration question | `Disclose; ask collaboration (Recommended)`: keep it null, disclose that it is zero and unconfirmed, and record the question for Joseph or Ben to ask MINERvA; nothing blocks on it | `b2048ea30e6d6f4ff58e27069a5eb50990837889493b1a9128c99abc9b62fd87` |

Contacting the collaboration is Joseph's act, or Ben's. No session sends it.

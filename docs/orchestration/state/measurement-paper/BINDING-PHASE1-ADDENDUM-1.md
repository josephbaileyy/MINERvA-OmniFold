# Binding addendum 1: MP3-A accepted, MP3-B first in step 2, and MP-5 (2026-10-19)

**By** the paper-tighten lane, as director, under [`BINDING-PHASE1-20261019.md`](BINDING-PHASE1-20261019.md). Sent to
the measurement session by message on the same day; this file is the record.

**CITABLE FOR:** the acceptance of MP3-A's readings, the step-2 order, and the MP-5 specification and grant.
**NOT CITABLE FOR:** any result (MP3-A's result lands with the session's phase-1 PR), or any claim.

## 1. MP3-A

MP3-A (GENIE carbon-only against CH over the 109 J cells) is accepted with the session's four readings:
- σ_c is the null-result SD;
- the shape-norm Jacobian is taken at the data;
- the root_6_28 environment is used;
- ν–e events are excluded.

The variants are reported beside the primary values. The T replay stays labelled descriptive, not a re-grade.

## 2. Step-2 order

The session's descriptive replay moved GENIE's T by about +8.6 null SD (total) and +3.9 (shape) when the carbon-only
prediction replaced CH. The smallest decision margin among the ten tests is NuWro shape, at 2.8 null SD
([`../2d-closeout/stageF/methods/M2-AUDIT.md`](../2d-closeout/stageF/methods/M2-AUDIT.md) Q4e).

So **MP3-B (NuWro on CH) runs first in step 2**, right after MP4-A is reported. Its result is a report beside A7. If
it moves NuWro shape across its decision, the session reports to the director at once; the claim question goes to
Joseph.

## 3. MP-5: two definitional mismatches between analysis truth and generator predictions (descriptive; frozen here)

The source is [`../2d-closeout/stageF/methods/M4-W-RECORD.md`](../2d-closeout/stageF/methods/M4-W-RECORD.md).

- **(a) Truth muon-angle axis.** The analysis measures θ from a fixed beam axis tilted −58.87 mrad (MAT
  `TruthFunctions.h:21-27`). The generators measure it about their own ν axis.
  - **Readout:** on the analysis MC (truth tuples carry `mc_incomingPartVec`), the per-J-cell ratio of truth contents
    with θ from the beam axis to θ from the ν axis. Also Δμ_c/σ_c and ΔᵀW⁻¹Δ under the frozen metric, the same
    readout as MP3-A.
- **(b) Generator W convention.** The predictions use a fixed M_n and set W = 0 when W² ≤ 0. The analysis uses the
  struck-nucleon M and drops NaN.
  - **Readout:** the J-cell shifts are already measured, so only Δμ_c/σ_c and ΔᵀW⁻¹Δ are added.
- **Gates:** none. Both readouts are descriptive.
- **Combined campaign:** the rebuilt predictions use the analysis conventions for both, unless MP-5(a) supports
  redefining the analysis truth about the ν axis. The campaign contract states the choice.
- **Grant:** MP-5 is covered by the phase-1 ceiling (35 CPU and 3 GPU node-h in total). It is expected to need
  under 1 node-h.

## 4. Amendment to §3(a) (2026-10-19, after the session's implementation note)

- **The primary readout** is the proxy Δμ_c = μ_G·(R_c − 1), labelled as a proxy, with R_c measured on the Tune v1
  analysis MC. The proxy assumes that the beam-axis versus ν-axis migration is a kinematic smearing of the muon
  direction by about 1 mrad, nearly independent of the interaction model. MnvTune's own Δ is zero by construction,
  and the readout states this.
- **The check, for GENIE CV only:** rebuild the J-cell prediction about a beam axis.
  - Rotate each event's muon by a ν direction drawn from the analysis MC's distribution of the ν direction relative
    to the MAT axis, conditional on Eν in a few bins.
  - The RNG seed is fixed and named before the run.
  - Compare the result with μ_G·R_c cell by cell.
  - If they differ by more than 0.2 σ_c in any cell, the proxy is labelled unreliable for the other generators.
- **Status:** descriptive, with no gate. The work is within the phase-1 ceiling.

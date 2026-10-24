# 5D design, Stage 0: binding of Part A (0a, 0b) and Stage 0c (2026-10-23)

**By** the paper-tighten lane, as director. **Binds** [`STAGE0-PARTA-DECLARATION.md`](STAGE0-PARTA-DECLARATION.md),
merged in PR #292 (`8ab794d4`; the file's sha256 begins `06fade5e9d1c88a7`).

**Under:**
- DESIGN §8 (PR #284);
- Joseph's fixed choices in `DECISION-20261023-joseph-5d-targets-and-paper-round-2.md`, made before any Stage 0
  output: W = 10 % (the bar is 8.6 %), RD1 then RD2, and M2;
- the measurement session's phase-1 grant (`BINDING-PHASE1-20261019.md:53`).

**Part P (HPSS preservation) has passed** (`STAGE0-PRESERVE-REPORT.md`):
- 425 inputs re-verified;
- one tar, sha256 `5bd51c14…`, with `hsi hashverify` OK and the sha256 confirmed on retrieval;
- 0 node-h.

## What is bound

1. **Stage 0c**, the D1 repair, as declared.
   - **Inputs:** the D1 ratio, re-derived from the flux-repaired GENIE, over the unrebuilt GiBUU. The KNOWN_ISSUES
     82 gap above 20 GeV is stated.
   - **Controls, all required:**
     - the unrepaired 5D marginal reproduces the committed s5n ratio within 2 % per bin;
     - the bitwise controls reproduce the old D1 unfold and the old GiBUU pseudo-experiment 801000;
     - the d0 control passes within 1e-5 relative, as the record states (`stage2-exit:106-107`). It is not
       bitwise.
   - **Compute:**
     - one regular CPU job at deploy `97886770`;
     - capped at **1.0 CPU node-h**, about 0.65 expected;
     - stop and report past 1.25× its projection;
     - ledgered.
2. **Part A, 0a and 0b,** read-only on existing products, 0 node-h.
   - **0a passes** only if c_F ≥ 0.60 for every held-out family (NuWro, GENIE MEC, GiBUU after 0c) **and** pooled
     coverage is ≥ 0.68.
   - **0b passes** only if κ* × the M2 envelope has a median over reported cells ≤ **8.6 %**, **and** the
     noise-corrected expected shape-only Δχ² is ≥ 9 for at least 2 stage-1 pairs.
   - **The graded covariance** is DESIGN §8's literal form, C_stat(e) + C_model + the z-cv total. Its double count of
     (a)'s statistics is conservative, as declared. The z-cv-only variant is reported but not graded.
   - **The provisional two-family run decides nothing.** The binding run follows 0c, with GiBUU after the repair.
3. **The result.** It is reported as declared, as PASS or FAIL against these rules, whatever it shows. A FAIL
   together with an R10 failure is DESIGN §9's stop condition.
   - No rule, threshold, truth set or covariance form changes after any output.
   - A code defect found after output comes to the director before any re-read.

## Not changed

- No GPU stage is authorized. Each needs its own binding after Stage 0 and R10 pass, under
  `DECISION-20261023-joseph-gpu-5100-for-5d-stages.md`.
- Before the first GPU binding, the director reminds Joseph about his note to Ben.

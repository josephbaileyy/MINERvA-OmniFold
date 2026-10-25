# DECISION 2026-10-24 — Joseph: approve the RE-2 integration wording, the S1 5D covariance compute with its seed block, and the tape copy of its inputs

**Recorded by** the paper-tighten lane, as director.

**What led to it.** The director asked Joseph for three things:
1. **Approve the integration wording.** These are the 48 reworded passages that carry the adopted refined 2D result
   (`DECISION-20261024-joseph-adopt-re2-2d-refined.md`) into the note, paper and primer.
   - They are on branch `stageF/re2-integration-20261024`, head `ecf730b5`, with records in
     `state/2d-closeout/stageF/methods/re2-integration/`.
   - agy agreed with all 48, after two rounds.
   - Redlines went to Joseph, and a draft copy went to the standalone note repository for Overleaf (`b6dfec1`).
2. **Approve the S1 compute.** That is configuration (e)'s 5D covariance on the 16 H2 cells, as declared in
   `state/measurement-paper/5d-community-20261024/S1-DECLARATION.md` (PR #339, merged at `c840c7bc`).
   - The cap is 15.5 CPU node-h, with 11.2–12.3 expected.
   - The cap includes a 4.5 node-h estimator-seed block, offered separately; without it, the cap is 11.0.
3. **Approve an HPSS copy** of the 5D universe weight bank and the detector dump, the S1 plan's option O4.
   - Their oldest access time is 2026-10-19, so they are exposed to the pscratch purge from about 2026-12-14
     (`S1-PLAN.md:93-98`).

Joseph's answers, verbatim. The first came with a request to explain items 2 and 3 again:

> okay I like the new wording. can you explain what the 5d covariance compute and tape copy are again?

sha256 of the text plus a final newline begins `becd817b2e69ceae`.

After the explanation:

> 1. okay lets the covariance and seed block, will these measurements be good enough for a measurement publication? 2. yes lets do it

sha256 of the text plus a final newline begins `4c3b223f16dca6c4`.

## What is decided

1. **The integration wording is approved.** The branch may be merged once its gates pass. The approval covers the
   wording as reviewed. Mechanical fixes found while merging (registry rows, open sites, conflicts) carry ledger rows.
   Any new printed wording goes back through agy and is reported to Joseph.
2. **The S1 compute is approved: 15.5 CPU node-h cap, seed block included.**
   - It runs as declared, on regular QOS and CPU only. Each job stays under 12 h.
   - The binding is `state/measurement-paper/5d-community-20261024/S1-BINDING.md`.
3. **The HPSS copy of the bank and the detector dump is approved.**
   - It runs at 0 node-h, under the same binding, with the committed Stage 0 preserve script.

## Joseph's question, and where it is answered

Joseph asked whether these measurements will be good enough for a measurement publication. The director answered in
conversation. It is not a decision, so it is not recorded here.
<!-- absence-ok: states where an answer lives, not a claim that a result is absent from the repository -->

## Not changed

- **No GPU.** The new route still has no GPU plan or Ben agreement (`DECISION-20261024-joseph-5d-community-standard-route.md`, "Not changed").
- **Claims, KI-85, `\pubhold` and release text** are Joseph's. Nothing is submitted, deposited or tagged.
- **Publication** of a measurement from MINERvA data still needs collaboration review, which is Joseph's act. Joseph's
  message to Ben stays held.

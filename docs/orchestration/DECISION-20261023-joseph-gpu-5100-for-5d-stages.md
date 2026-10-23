# DECISION 2026-10-23 (sixth) — Joseph: up to 5,100 GPU node-h for the 5D design's stages through the pooled coverage test

**Recorded by** the paper-tighten lane, as director.

**What led to it.** The 5D measurement design (`state/measurement-paper/5d-design-20261023/DESIGN.md` §5, §8) prices
its GPU stages as follows (DESIGN §0):
- stress tests: about 11–14 GPU node-h;
- the (e) covariance: about 25–28, plus inputs not yet priced;
- the pooled coverage pilot: about 321;
- the pooled 400-per-truth coverage test: 2,570–5,141;
- the per-functional test: 28,299.

These figures come from the measured GPU unit (`state/gpu-timing-20261023/REPORT.md`: 0.028559 GPU node-h per
unfold). The director drafted Joseph's note to Ben with these figures.

Joseph's answer, verbatim:

> I approve use of the 5,100 for now, should I hold of on the message then until we need to decide if we need all 28,000?

sha256 of the text plus a final newline begins `79d89f6c42fed70e`.

## What is decided

1. **Up to 5,100 GPU node-h on `m3246_g`** is approved for the 5D design's stages up to and including the pooled
   400-per-truth coverage test.
   - This is Joseph's share decision for the shared group pool (DECISION-20261019 §1b leaves that to him).
   - It authorizes no job by itself.
2. **Release is stage by stage.**
   - Each GPU stage runs only under the director's binding of its own declaration.
   - It runs only after the stages before it pass their pass rules, fixed before output (DESIGN §8).
   - Stage 0 and R10 must report before any GPU stage.
   - A failed stage stops the programme at that point (DESIGN §9).
   - Joseph's campaign criterion still governs each release (DECISION-20261023 first, item 3).
3. **The per-functional test (about 28,300 GPU node-h) is not approved.** It returns to Joseph, and to Ben, if the
   pooled test passes.
4. **Ledger.** Every GPU job is ledgered against the 5,100, and each binding records what remains. The pool is
   re-measured with `iris` before each GPU binding.

## Not changed

- Contact with Ben remains Joseph's act.
- The CPU pool rules are unchanged.
- No submission, deposit or tag.

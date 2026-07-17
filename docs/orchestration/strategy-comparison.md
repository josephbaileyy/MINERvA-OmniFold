# Strategy comparison — what makes persona-debate produce verified new physics

Benchmarking findings only. The physics results referenced here live in `../../physics/` and are keyed by `CLM-###`
in `../../provenance/CLAIMS.md`; the full interleaved narrative is in
`../../provenance/mixed-source/debate-interpretations-report.original.md`.

## Personas vs. methods (match the tool to the question)
- **Interpretation personas** (QBist / Everettian / objective-collapse / Zurek-Darwinist) are right for "is this
  claim interpretation-neutral?" — they localize the hidden assumption (found: the bound's entire interpretational
  dependence sits in one global-unitarity premise).
- **Physics-split personas** (e.g. soft-hair-realist vs IR-skeptic vs collapse-constructor; edge-realist vs
  Type-III-purist vs holo-edge-constructor) are right for a substantive physics crux. Interpretation personas
  converge *uselessly* on such questions; pick personas that disagree on the physics the question turns on.
- **Independent methods** (not personas) are right for a theorem-shaped prove/refute residual: spawn 3 agents on
  *different formalisms* (modular theory / celestial rep-theory / explicit toy model). Value = method diversity + a
  *locatable* disagreement — when 2 agree and 1 dissents, the dissenter's diagnosed error is itself the insight
  (the toy model used global-vacuum orthogonality instead of accessible modular-thermal distinguishability → CLM-005).

## Prompt length
- **Long, richly-specified persona prompts** = tighter fidelity, lowest fabrication risk (preferred for precision).
- **Short prompts** make models self-ground via web search → surfaces fresh refs but looser; treat as a breadth
  probe and verify every auto-fetched citation.

## Agent count & topology
- Agent count = number of independent *conceptual axes*, not more. The 2 most-opposed find the crux fastest; add a
  third only for an orthogonal axis.
- **Flat topology** (moderator is sole router/verifier; workers do NOT sub-spawn) preserves end-to-end citation
  checking. Vindicated: every fabricated citation was caught because it passed through the moderator. Nesting blinds
  that check.
- **Parallel dual-panel works:** two panels / two questions / 6 concurrent jobs / 4 accounts / 1 moderator ran with
  no cross-contamination, and the panels reinforced each other (one's verified result became the other's decider).

## Convergence & the adversarial push
- Agents left to discuss *freely* default to agreeableness — they reproduce a consensus fast but produce none of the
  cracks the adversarial round forces, and can reach a *false/premature* consensus. Free = good for stating a
  consensus, bad for stress-testing one.
- Structure that forces convergence: R1 ends with each persona's falsifiable "concession I'd need"; a later round
  demands sign-able (A)/(B)/(C) language; the final round gives the contrarian a "produce concrete object X (with
  the number) OR concede" ultimatum — and feeds it another panel's *verified* result as a referee constraint. This
  produced explicit, reasoned concessions (the strongest clean-convergence signal), not restatement.

## Hallucination-as-signal (with verification)
A confidently-wrong claim often encodes a correct *question* the model couldn't ground. Steelman + grounded-verify
converts it into either a sharpened open problem or a clean dead-end. Requires the verification pass — it is also
what surfaces the fabricated citations (3 caught to date; see `../../provenance/CLAIMS.md`).

## Reasoning effort
MAX matters for frontier questions: the affine-weight cancellation, the center-label argument, and the modular
thermal-noise floor appeared ONLY at `xhigh`(codex)/opus-max, not at `high`. Match effort to question depth.

## Model casting (empirical)
gemini = most assertive → the must-not-concede contrarian. codex/gpt-5.5 = most citation-dense. Claude = cleanest
consensus drafting → synthesizer/moderator. Trust a persona's *localization* of disagreement, never its verdict;
verify every citation it surfaces.

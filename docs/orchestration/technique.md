# The persona-debate technique

> Source of truth is the `.claude-school` project memory `persona-debate-technique.md` (type: feedback); this is the
> human-facing expansion. Keep the two in sync.

**Core.** To stress-test a physics claim, instantiate N cross-model agents as independent positions, give them ONE
claim-grounded proposition, and route each round's statements between them (moderator = sole router + verifier)
until they sign a joint (A) agree / (B) irreducible-disagreement / (C) neutrality-condition verdict. The moderator
verifies every load-bearing claim (numerics / direct sources) and every citation — a persona is an argued position,
never an authority.

**Pick the mode to the question:**
- interpretation-neutrality → interpretation personas (QBist / Everett / collapse / Darwinist);
- substantive physics crux → physics-split personas (disagree on the physics, not metaphysics);
- theorem-shaped prove/refute → N independent *methods* (different formalisms), not personas.

**Make it converge:** R1 ends with each side's falsifiable "concession I'd need"; a later round demands sign-able
(A)/(B)/(C); the final round hands the contrarian "produce concrete object X (with the number) OR concede," plus a
cross-panel *verified* result as a referee constraint.

**Stop on saturation** (contrarian concedes / all converge on the same residual / turns become "propose the
theorem") then run the verification pass. Match reasoning effort to depth — MAX for frontier questions.

**Casting:** gemini = assertive contrarian; codex/gpt-5.5 = citation-dense; claude = synthesizer/moderator.
**Topology:** flat — the moderator never lets workers sub-spawn, so every citation stays checkable.

Full findings: [`findings/strategy-comparison.md`](findings/strategy-comparison.md),
[`findings/novelty-per-round.md`](findings/novelty-per-round.md). Validated episodes:
[`../provenance/episodes/`](../provenance/episodes/).

---
name: persona-debate-technique
description: How to run multi-agent interpretation-persona debates for stress-testing physics claims (what config works)
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 061c1957-506b-4c18-a5ee-623b037c0426
---

For adjudicating whether a physics claim is interpretation-neutral (or to stress-test hidden assumptions), the
user likes the "persona-debate" technique: instantiate N QM-interpretation personas (QBist, Everettian,
objective-collapse, Zurek-Darwinist, …) as independent cross-model agents, give them ONE claim-grounded
proposition, and route each round's statements to the others until they sign a joint (A) agree / (B) irreducible
disagreement / (C) neutrality-condition verdict.

**Why:** it localizes the exact hidden assumption. In the horizon-record project it revealed that §8 step (i) is a
*global-unitarity* assumption, neutral across all unitary interpretations, with objective collapse the sole escape
(itself gated by an open collapse-⟨T_vv⟩-compensation question). See [[qft-horizon-record-project]].

**How to apply (validated 2026-07-08):**
- Structure that forces convergence (in ~2 rounds): round-1 ends with each persona's falsifiable "concession I
  would need"; round-2 demands *sign-able* (A)/(B)/(C) language. Without these, agents just restate.
- Agent count = number of independent *conceptual axes*, not more. The 2 most-opposed personas find the crux
  fastest; add a persona only to cover an orthogonal axis (e.g. QBist instrumentalism was invisible to a
  collapse-vs-Darwinist pair). Personas sharing an axis add robustness but little new.
- Long, richly-specified persona prompts = tighter fidelity, lowest fabrication risk (preferred). Short prompts
  make models self-ground via web search (surfaces fresh refs) but looser — treat as a breadth probe and verify
  every auto-fetched citation.
- Casting: gemini = most assertive → the must-not-concede contrarian; codex/gpt-5.5 = most citation-dense;
  Claude = cleanest consensus drafting → synthesizer.
- Verify every citation the debate surfaces before using it; personas are argued positions, not authorities —
  trust only their *localization* of disagreement, checked for internal consistency, never their verdicts.
- **Rounds / the limit is set by QUESTION DEPTH, not a round number.** More prompting keeps producing genuinely
  new content *as long as an unresolved crux remains*. On a near-converged question, novelty saturates by ~round 5
  and turns to overreach (a false "closure" on a mis-cited ref). On a genuinely deep/open question (soft-sector
  crux, MAX reasoning), novelty *rose* into round 2 (the decisive argument) and stayed high through round 3.
  Saturation signals (stop here): (a) the contrarian concedes, (b) all camps converge on the SAME residual
  sub-question, (c) turns become "propose the theorem that would settle it" not new arguments. Recipe: run until
  those signals, then STOP + verify. Match reasoning effort to depth: use `xhigh`(codex)/opus-max for frontier
  questions — the sharpest insights appeared ONLY at max, not at `high`.
- **Pick personas that disagree on the PHYSICS the question turns on, not on metaphysics.** QM-interpretation
  personas converged uselessly on the soft-sector question; retiring them for soft-hair-realist vs IR-skeptic vs
  collapse-constructor (disagreeing on "is soft-sector info free?") produced a verified near-resolution.
- **They need the adversarial push.** Left to discuss freely (no mode labels), the personas default to
  agreeableness — reproduce the consensus fast, produce ZERO of the cracks the adversarial round forces, and even
  reach a *false/premature* consensus (the contrarian conceded via an unproven argument). Same agent attacks only
  when told to. Free discussion = good for stating a consensus, bad for stress-testing one.
- **Hallucination-as-signal works (with verification).** A confidently-wrong claim often encodes a correct
  *question* the model couldn't ground. Steelman it + grounded-verify: converts noise into either a sharpened open
  problem or a clean dead-end. Requires the verification pass (it also surfaces the fabricated citations).
- **Parallel dual-panel + FLAT control scales cleanly.** Two independent panels on two questions (6 concurrent R1
  jobs across 4 accounts, one moderator routing both) ran with no cross-contamination, and the panels *reinforced*
  each other (one panel's verified result became the other's decisive referee constraint). Keep it FLAT — do NOT let
  worker accounts spawn their own sub-agents: the moderator must stay the sole router/verifier so every citation is
  checked. Vindicated when the run's one fabricated citation (3rd of the project — a bogus arXiv attribution from a
  delegate) was caught precisely because it still passed through the moderator. Nesting would blind that check.
- **Theorem-shaped residual ⟹ use N independent METHODS, not personas.** For a sharp prove/refute question, spawn
  3 agents on *different formalisms* (e.g. direct modular theory / celestial rep-theory / explicit toy model), not
  interpretation personas. Value = method diversity + a *locatable* disagreement: when 2 methods agree and 1
  dissents, the dissenter's diagnosed ERROR is itself the physics insight (here: the toy model used global-vacuum
  orthogonality instead of accessible modular-thermal distinguishability). Independent methods that disagree then
  reconcile beat three that agree. Always re-derive the load-bearing computation yourself (analytic + numeric).
- **Force contrarian concession with a falsifiable ultimatum + a cross-panel constraint.** The strongest clean-
  convergence signal is an explicit, reasoned concession (not restatement) from the must-not-concede persona. Get it
  by the final-round instruction "produce concrete object X (with the specific number) OR concede and re-sign," and
  by feeding it *another* panel's already-verified result as a referee constraint it must evade. The contrarian
  conceded both prongs when handed the verified thermal-noise floor.
- **Naive-expert / fresh-eyes format is a validated, cheap, high-value mode.** Give generalists (pure
  mathematician, condensed-matter, stat-mech, information theorist, quantum-optics) with NO subtopic background a
  PLAIN-LANGUAGE, jargon-stripped version of the question and tell them to reason only from their own field (no
  web). They validate a result by translating it into an unrelated field's tools, and reliably surface edge cases
  the specialists gloss — e.g. they independently gave the `p>2` summability threshold and flagged the marginal
  `p=2`/log case, and independently rederived the `ln2` floor as Landauer `kT_eff·ln2`. Best for validation-by-
  translation + finding glossed edge cases. Short prompts, no web → very cheap.
- **Conference-style vs routed debate — different tools.** Conference (one question BROADCAST to N distinct expert
  lenses, each a short talk + floor question, moderator synthesizes) = fast PARALLEL BREADTH; each lens contributes a
  distinct decisive piece. Routed debate = adversarial DEPTH on a single crux. Use conference for many-faceted
  questions, debate to stress-test one crux. Fabrications were ~zero in fresh-eyes/conference runs (well-known refs +
  expert framing); they cluster in assertive-contrarian runs asserting niche citations under pressure. Verify anyway.
- **Account usage limits (dispatch via CLI, 2026-07-09).** No hard server rate-limit/429 was reached up to codex
  ×32 / gemini ×16 concurrent per account; the wall you hit is THROUGHPUT SATURATION — wall-time grows ~linearly
  with concurrency (server-side queueing, jobs serialize not reject). codex has a LOCAL limit: at ≥32 concurrent on
  ONE `CODEX_HOME`, processes race the shared models-cache file (`failed to load models cache: EOF`, recovers). So
  the practical ceiling is ~16/account (codex), ~8 (gemini) before latency degrades; use an isolated `CODEX_HOME`
  per job to push codex concurrency higher. The true API/daily-token quota needs sustained volume, not burst, to find.

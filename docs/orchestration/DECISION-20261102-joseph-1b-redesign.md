# DECISION 2026-11-02 (latest) — Joseph: run the 1B stage-1 redesign, clip negative counts, and describe it neutrally

**Recorded by** the paper-tighten lane, as director.

## What led to it

**The stop.** Stage 1 stopped at its N1 guard before any toy, at 0 node-h (`FD-1B-STAGED-STAGE1-STOP`, #696):
- most rows above 10 were ordinary-CV rows compounding over about 38 bands;
- the rest were small-CV rows carrying one large LowQ2 or HighQ2 ratio;
- the audit also found defect D2. The bound toys' `rng.poisson` would have refused negative means from LowQ2_1 and
  HighQ2_1, in 684 of the 900 declared draws.

**The redesign.** `FD-1B-STAGED-REDESIGN-PROPOSAL.md` (#697, revision 2, head `883c26c4`) proposes:
- first-order composition of the natures, a_D = a_u1 + Σ_{j≥2}(a_uj − a_CV), in draw order. Its ground is that C_T is
  a sum of per-band blocks with no cross-band term;
- options (a)–(d) for negative expected counts;
- draft paper clauses (§2c).

`coverage-5b-audit` passed revision 2.

**The director's rulings, before Joseph's:**
- §2d: (ii), an exact float64 pass over every row, at 0 node-h. It falls back to one node under binding 2 ruling 5's
  terms.
- §2b: a non-positive denominator cell fails closed.

**The consults:**
- **Sonnet** (`FD-1B-REDESIGN-CONSULT-{PROMPT,ANSWER}.txt`, #699) recommended running, with three additions:
  - an observable-level measurement of the omitted cross terms;
  - the clipping bias reported per cell in σ units;
  - a rule that a second STOP ends stage 1.
- **Gemini, as PRD referee, at Joseph's request** (`FD-1B-REDESIGN-WORDING-GEMINI-{PROMPT,ANSWER}.txt`):
  - first-order composition is standard multi-universe practice, to be stated neutrally ("propagated linearly,
    consistent with the covariance's construction");
  - the "does not test higher-order effects" clause and the CANNOT SUPPORT line belong out of the paper;
  - clipping, ±1σ endpoint draws and shared universes belong in the note.

  The director corrected two points in Gemini's sample text:
  - it said "coverage of the reported covariance", but the result concerns the procedure's covariance rebuilt at each
    tune;
  - its failure example used invented numbers.

## Joseph's answers, verbatim

1. Asked whether to run the redesign or stop 1B:

   > Run, with additions (Recommended)

   sha256 of the text plus a final newline begins `9a38b7a8e8f30bb5`.
2. Asked how a pseudo-experiment treats a negative expected count:

   > Clip to zero + measure bias (Recommended)

   sha256 begins `a18fa599e16a07a2`.
3. Asked to approve the lane's scope clauses with the consult's additions:

   > lets try to get a prd reviewer perspective, this should happen normally because I have a suspicion this might introduce another caveat

   sha256 begins `b2e4a6e6825ed9c3`. A standing practice follows from this: a PRD-referee read precedes every
   paper-wording choice put to Joseph.
4. After that read, asked how the paper describes the test's scope:

   > Neutral methods sentence (Recommended)

   sha256 begins `1a09327737b07e3a`.

## What is decided

1. **Stage 1 runs** on the redesign, under an implementing amendment (code, tests, mutation receipt) that the audit
   reviews and the director binds.
   - The cap is 73.0 node-h.
   - The composition is first order, in draw order, with k = 1 bitwise.
2. **The three additions:**
   - **(i) Cross terms.** On the login node, at 0 node-h, over the declared draws: each cell's reco-weighted histogram
     under product composition against additive, in units of σ_c. It is descriptive.
   - **(ii) The clipping bias.** Σλ⁻ is recorded per reco cell and per truth cell for every toy, together with the
     unfolded offset in σ_c from one mean unfold per truth. The reading for a flagged cell that the offset could
     explain is fixed before any number is read.
   - **(iii) A second STOP ends stage 1** unless Joseph rules otherwise.
3. **Negative expected counts:** option (a), λ⁺ = max(λ, 0) on the full product, with addition (ii).
4. **The paper's wording, whatever the outcome:**
   - **The method, in one neutral sentence:** 300 pseudo-experiments at each of two held-out tunes, the uncertainties
     propagated linearly as in the covariance's construction, and the covariance rebuilt by the same procedure at
     each tune. The result follows it.
   - **No "does not test" clause.**
   - **The facts the bindings require, stated as description, not as qualifiers:**
     - G18 shares its 2p2h model family with one of the model term's generators;
     - the result concerns the procedure's covariance at those tunes, not the reported intervals at the data.
   - **To the note:** clipping, the ±1σ endpoint draws, the shared universes and the cross-term readout.
   - **The paper lane drafts the text when the result lands.** It goes through the PRD-referee read, and Joseph reads
     it before merge.
5. **The director's rulings §2d (ii) and §2b stand** (above).

Nothing is submitted, deposited or tagged.

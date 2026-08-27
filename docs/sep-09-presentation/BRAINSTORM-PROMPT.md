# Brainstorming prompt — paste into a fresh session

Purpose: generate candidate **theses** for the Sept 9 talk, including ones that need new
compute. Not slides. The deck currently on this branch (`DECK.md`) is the fallback; its
framing is right and its ending is weak, and this prompt exists to fix the ending.

---

```
I'm giving a ~20 min talk on 2026-09-09 to Ben Nachman's ML group at Stanford/SLAC.
Today is 2026-08-25, so there are 15 days.

AUDIENCE: strong on ML and general particle physics. Knows OmniFold at a high level.
Knows NOTHING about neutrino physics or MINERvA. Strongly prefers ML-METHODS content
over uncertainty-quantification content. Nominally a "1 slide" guideline, but people
really give ~8 slides.

RELEVANT: Nachman co-authored OmniFold (Andreassen et al., PRL 124, 2020) and PET is
the OmniLearn backbone (Mikuni & Nachman, 2404.16091). Both the method and the
architecture I use are theirs. Talks that interrogate their own tools land well.

=== THE AESTHETIC I WANT, AND IT IS THE MAIN INSTRUCTION ===

Take an object everyone using this method treats as settled, and ask the question
nobody asked about it. The current draft's object is the RIGHT KIND: not the cross
section, but *the function the step-1 classifier actually learns*. Nobody looks at it;
it's assumed to be the density ratio and then used. That framing is what I want more of.

What I do NOT want is that draft's ENDING. It currently concludes "re-running the fit
moves the answer by 41x the Poisson scale and I don't know why." That is a puzzle, not
a result. A talk needs to land somewhere.

So the bar for every thesis you propose: IT MUST HAVE A CONCLUSION. Either it already
does, or you tell me exactly what would give it one.

=== COMPUTE IS ON THE TABLE ===

I'm willing to spend real compute in the next two weeks to turn a good question into a
conclusive answer. So for each thesis, propose the experiment.

Constraints that decide what's actually feasible by Sept 9 -- verify each against the
repo rather than trusting me:
  - STANDING AUTHORIZATION: any SINGLE Slurm job under 12 h walltime is pre-approved.
    Launch it, don't ask. The grant is about walltime and nothing else -- a short job
    under an explicit hold is still refused and the hold wins.
  - A FAMILY of jobs is NOT pre-approved. The M(ii) family specifically is not
    authorized at any walltime, and family size is a decision reserved for me.
  - Route new compute through nd-unfolding/mnv_guarded_run.py (OI-136: 59 .py files put
    a hardcoded absolute root at sys.path[0], so an entrypoint can import another
    checkout's modules while deployment parity truthfully reports every pinned file
    CURRENT; this already cost 3 h 08 m of A100 on 57266000_0).
  - USEFUL: after my OI-126 ruling, PET is diagnostic / method-development and is OFF
    the publication critical path. Gate 5, Gate 6, C_stat and C_ML are all off it. So
    exploratory PET work touches no publication gate -- it is the safe playground.
    Do NOT reopen the completed OI-126 containment, tail-geometry, target-factor,
    extraction or occupancy probes; their conclusions and retractions are recorded.

For every proposed experiment, tell me:
  (a) the specific question it answers, and what the ANSWER would let me claim;
  (b) whether the artifacts it needs ALREADY EXIST -- check, don't assume. Some of this
      may be pure re-analysis of weights already on disk, which is the cheapest and
      best case;
  (c) GPU/CPU hours and whether it fits the single-job-under-12h grant or needs a
      family (and therefore my authorization);
  (d) an honest probability that it yields something PRESENTABLE by Sept 9;
  (e) WHAT THE NULL RESULT LOOKS LIKE. This matters as much as the positive case: with
      15 days I want experiments that are worth a slide whether or not the effect is
      there. Rank experiments that are presentable EITHER WAY above higher-variance ones.

=== SEEDS -- verify, cost, and replace freely; these are not a menu ===

These came from a session that had read the ledger but not the code. Treat them as
starting points and say plainly if one is unsound or already done.

  1. KILL THE NONDETERMINISM. Re-fit N times with full determinism (deterministic ops,
     single-thread, pinned CUDA) vs GPU default vs CPU-only. If the spread collapses,
     the cause is ESTABLISHED and the conclusion becomes "here is the mechanism, here
     is the flag, here is what it costs." Conclusive either way, and cheap.
  2. MAP THE DISAGREEMENT ACROSS PHASE SPACE. The five VL131 re-fits already happened.
     If their PER-EVENT push weights were saved, compute the re-fit-to-re-fit variance
     of the learned ratio as a function of (pT, p_parallel, E_avail) with ZERO new
     training. Does the disagreement concentrate where the classifier has little
     support, or where the ratio is far from 1? This is the most direct explanation of
     the p_parallel sign flip in OI-126. CHECK WHETHER THOSE WEIGHTS EXIST FIRST -- if
     they do, this is the cheapest path to a conclusive talk and should probably win.
  3. DOES IT DIFFUSE RATHER THAN CONVERGE? Measure the across-re-fit spread of the
     learned map as a function of OmniFold ITERATION. If spread grows with iteration,
     then choosing an iteration count is choosing a point on a diffusion trajectory,
     and "OmniFold doesn't converge, it diffuses" is a genuinely unasked question with
     a clean answer. If spread shrinks, that's a reassuring result and still a slide.
  4. IS THE ENSEMBLE THE RIGHT ESTIMATOR? Average push weights over M re-fits; show
     whether variance falls as 1/sqrt(M) AND whether the ensembled estimator is closer
     to closure truth, not merely more stable. A positive result is a concrete
     recommendation to every OmniFold user.
  5. DOES THE PHYSICS SURVIVE? Propagate the five re-fits through to the low-E_avail
     2p2h comparison. If the conclusion is stable under a 5% estimator wobble, that is
     a reassuring statement worth making; if not, that is a big deal.
  6. ITERATION DYNAMICS, ALREADY MEASURED. VL94-VL97 is a 2x2 of warm/cold model x
     fresh/fixed split plus an annealed-LR arm: all four FAIL the predeclared
     iteration-2 repair rule and three get the SIGN wrong. VL134-VL140 separates two
     annealing arms at 16.23x the pooled within-arm sd, ranges disjoint, 9/9 realized
     pairwise. This may already be conclusive with no new compute. Read the whole
     campaign, not just the rows, and tell me if it is.

=== CRITICAL -- READ BEFORE ANYTHING ELSE ===

1. Read AGENTS.md. Treat it and all generated state as views, never evidence or
   authorization.
2. Run `git fetch github && git log --oneline -40 github/main`. The /pscratch working
   tree runs HUNDREDS of commits behind (230+ on 2026-08-25) and its status docs are
   actively misleading. Read everything via `git show github/main:<path>`.
3. docs/orchestration/LIVE-STATE.md can be FRESH and still false: its `Current DAG node`
   and `Declared state` fields are authored prose the generator copies forward verbatim
   without revalidating. Verify any blocker claim against the governing OI-* record.
4. Respect AGENTS.md "Quarantined and superseded traps". Especially: no 3D/N-D
   covariance band and no sigma or chi-square derived from one; C_stat is never
   "verified"/"adopted"/"the statistical uncertainty"; never cite "bootstrap-centering"
   as a settled mechanism even though the phrase is mine. A thesis I cannot state
   without breaking one of these is NOT viable -- say so outright rather than softening
   the number until it passes.
5. Re-measure volatile state on disk instead of quoting a doc about it.

=== WHERE TO MINE ===

VALIDATION_LEDGER.md (the VL rows carry the sharpest measurements), docs/OPEN_ITEMS.md,
docs/analysis-note/sec_*.tex and app_statmethods.tex, the *_STATUS.md files,
docs/FUTURE_DIRECTIONS.md, docs/HIGHER_DIM_OMNIFOLD_DESIGN.md, and the actual code under
nd-unfolding/ and nd-unfolding/pet/ -- several of these questions are answered by what
is or isn't saved to disk, which no status document will tell you.

=== DELIVERABLE ===

5-8 candidate theses, each a single declarative headline sentence, RANKED by how
interesting they'd be to that specific room. For each:
  - the 2-4 specific measurements backing it, with VL/OI ids;
  - why this room specifically cares;
  - the figure that would carry it, and whether it already exists;
  - the strongest objection someone in the room would raise;
  - IF it needs compute: the experiment, per (a)-(e) above.

Then a bottom line: which ONE would you commit the next 15 days to, and why.

Do not write the talk. Do not use subagents or workflows.
```

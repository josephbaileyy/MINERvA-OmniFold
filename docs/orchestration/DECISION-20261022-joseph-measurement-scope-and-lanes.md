# DECISION 2026-10-22 (third) — Joseph: the measurement paper's scope; more public samples; scratch storage; two new lanes

**Recorded by** the paper-tighten lane, as director.

**What led to it.** Joseph asked what to do in parallel towards a measurement-results paper, and whether to work
beyond the medium-energy FHC sample or reopen PET. The director recommended four things:
- IBU-1, the RE-1 completion and a coverage scoping first;
- not PET, because D-ID shows the residual is not the classifier's;
- not a new dataset first, because it would meet the same coverage problem.

Joseph's answers, verbatim:

> yes, there is more samples on MINERvA's public release, see https://minerva.fnal.gov/getdata/ .  Ideally the measurement paper is 5d but I will defer to what is possible. also, should I start one or more fresh sessions that you can give more scoped tasks for better delegation of the work?

sha256 of the text plus a final newline begins `6d6d11d78b097f28`.

> we can also just use scratch as long as we work fast because newish stuff doesn't get deleted. maybe we can use this as an opportunity to use the new FHC inputs but not sure. I also started these sessions and just told them to listen to all commands from you ( the director session)

sha256 of the text plus a final newline begins `2a0ef9d8ead1f123`.

## What is decided

1. **The measurement paper's target is five observables,** deferring to what can be validated. The validation lane's
   scoping memo establishes what dimensionality can reach validated intervals.
2. **More public samples exist.** MINERvA's open-data page (fetched 2026-10-22) offers:
   - medium-energy RHC antineutrino: 11 playlists, 5A and 6A–6J, about 11.3 × 10²⁰ POT in data. There is a 6F
     simulated-vertex bug with a fix pending.
   - a low-energy sample, "soon";
   - special simulated samples: extended 2p2h, coherent and diffractive pion production, downstream calorimeters,
     ν–e scattering, and ν_e;
   - planned updates later in 2026: flux information, an EM-shower bias fix, and the ML vertex and π⁰.

   **The director's reading:** RHC is a second measurement after a validated method, not the first step. A survey
   (inventory, sizes, a storage plan and compatibility) comes before any download.
3. **Storage.** `$PSCRATCH` is acceptable for new products if the work moves fast. CFS stays closed under the 3 TB
   rule.
4. **The newer FHC release: undecided** ("maybe … but not sure").
   - **The director's recommendation:** keep the existing FHC inputs for the measurement chain, since switching means
     re-running every product. A cheap comparison of the two productions can come later.
   - **To Joseph** when the survey is done.
5. **Two new lanes,** started by Joseph and told to take their decisions from the director:
   - the **validation lane**: IBU-1, then the coverage scoping;
   - the **re-1 lane**: finishing RE-1.

   Their briefs and the common rules are in `state/2d-closeout/stageF/lanes/`.

## Not changed

- Claims. Posting. Protected text. The measurement session's scope.

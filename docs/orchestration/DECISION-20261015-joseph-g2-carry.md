# DECISION 2026-10-15 — Joseph: G2 is carried as a disclosed approximation

**Recorded by** the paper-tighten lane, as director. On 2026-10-15, in his session, the director put the G2
recommendation of
[`AUTHORIZATION-20261015-2d-closeout-stageC-production.md`](AUTHORIZATION-20261015-2d-closeout-stageC-production.md)
§4 to Joseph. That recommendation was pre-declared in
[`AUTHORIZATION-20261013-2d-closeout-stageB-exit.md`](AUTHORIZATION-20261013-2d-closeout-stageB-exit.md) for the case
"if K2 passes". Joseph answered, verbatim:

> "yes you can carry G2 as a disclosed approximation."

The sha256 of the answer text plus a final newline begins `a27d17498585dd9c`.

**CITABLE FOR:**
- how G2 is carried in the 2D construction: as a disclosed approximation, with no repair;
- the content the disclosure must carry (§2).

**NOT CITABLE FOR:**
- final disclosure wording in any deliverable. That is drafted at Stage F and reviewed by Joseph, with Ben;
- adopting any product, central value or uncertainty;
- a claim that the G2 effect is zero. It is not measured to be zero;
- a compute grant, or any message to anyone outside this repository.

## 1. What G2 is, and what was measured

G2 is the approximation in how the systematic-universe unfolds weight events that fail reconstruction (the miss
rows). It enters through each universe's completeness. Two universes were measured, each as an off/on pair:

| universe | record | seeds | routing |
|---|---|---|---|
| `MaRES_0` (vertical) | [`state/2d-closeout/stageB/diagnostics/REPORT.md`](state/2d-closeout/stageB/diagnostics/REPORT.md) P5 | 42 and 43 | NOT RESOLVED ABOVE TRAINER NOISE; seed-43 confirmation NOT CONFIRMED |
| `Flux:23` (largest median \|c_off − 1\| among Flux universes) | [`state/2d-closeout/stageC/pilot/REPORT.md`](state/2d-closeout/stageC/pilot/REPORT.md) K2 (P2-G2) | 42 and 43 | NOT RESOLVED ABOVE TRAINER NOISE; seed-43 confirmation NOT CONFIRMED |

On `Flux:23`, the median r3 = |d|/σ_ML is 0.91 at seed 42 and 0.85 at seed 43. The pre-declared noise-only value is
about 0.95. The two seeds' per-cell patterns are weakly anti-correlated (Pearson −0.295). K2 excludes only a median
effect large enough to push r3 above its 2 σ_ML bound. It does not bound a smaller one.

## 2. What the disclosure must carry

- G2 is an approximation in the universe unfolds' miss-row weighting, and it is not repaired;
- the two universes in which it was tested: `MaRES_0` (P5) and `Flux:23` (P2-G2), each at seeds 42 and 43;
- the result: in neither was an effect resolved above the trainer's seed noise;
- the limit: an effect below trainer noise is not excluded, and 2 of the 187 universes were tested.

## 3. What follows

- **No G2 repair** is planned. The repair price on record, 43–129 node-h, would need its own grant and Joseph's
  request.
- **Stage C production** runs unchanged. Its universe block uses the July dump-mode sweep, which contains the G2
  approximation (production DESIGN §12).
- **The disclosure** is drafted at Stage F, with the claim wording.

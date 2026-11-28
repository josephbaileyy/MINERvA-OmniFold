# Lane rebuild on the paper's pT edges, and the efficiency-convention test (2026-11-24)

**By** the `ibu-chi-squared-issue` session (Claude Opus 5.5). It is part of the chain in [`../README.md`](../README.md).
Joseph asked for the quick rerun and the director gave GO. It ran as the last step of interactive job `ibuchi_t1i`
(61928141, nid200013, srun -n1 -c 32 --mem=96G, 26 s), after the queued `ibuchi_rb` (61926143) was cancelled unstarted.
Receipts are in [`../tier1/receipts/`](../tier1/receipts/). The pre-submit checks for the cancelled job are in
[`precheck_submit.txt`](precheck_submit.txt).

[`DECLARATION.txt`](DECLARATION.txt) (sha256 `8b4a978b3bf7074ee8ed25648d5d53136537877fceedd95fa57a6fb21ae3a028`), [`rebuild.py`](rebuild.py) → `rebuild.npz` (sha256 93990a88…, on
pscratch) and [`rebuild.json`](rebuild.json). [`rerun.py`](rerun.py) → [`score.out`](score.out).

**Controls pass.** The OLD build equals evloop BASE exactly: M, T, B and N to ≤ 4e-14, and C-FAC 3e-14.

| | OLD edges | paper's edges |
|---|---|---|
| this lane's K=10 IBU χ²/205 vs published | 0.9614 | **0.4736** |
| fold residual of the published result, S_ROW (pT 0–0.07 / 0–0.075) | −0.064 | **−0.006** |
| S_COL (p‖ 40–60) | +0.100 | +0.100 |

**Readings.**
- **ROW-CLOSED.** The low-pT row residual is the edge difference.
- **OVERFLOW-PARTIAL.** With the efficiency that counts selected events reconstructed outside the grid (eps_any: 0.795
  against eps_in 0.747 at true p‖ 40–60), our result's own fold residual at 40–60 is +5.7 %, against the published
  result's +10.0 %, so that convention reproduces 57 % of the column. At 20–40 the two agree (+1.54 % vs +1.54 %).
  The IBU distance on the paper's edges drops further, from 0.474 to 0.294.

So the column is about half explained by a reco-anywhere efficiency convention. The rest is still open. This is about
our chain's behaviour under that convention. Whether MINERvA used it is the question put to them.

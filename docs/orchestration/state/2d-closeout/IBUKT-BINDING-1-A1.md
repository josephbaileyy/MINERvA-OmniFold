# IBUKT BINDING 1 addendum A1 (draft for director review)

The proposed fresh run is `ibukt-20261119-c`. The authorization for fixes, guarded rehearsal, and a fresh run is recorded in the [2026-11-19 decision](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/d193fa48aea2244058867b7fce0ace3a606534b8/docs/orchestration/DECISION-20261119-joseph-ibukt-rerun.md). Each stage requires the director's go on the exact script SHA-256 and fence acknowledgments from cov2d and tier3-design that are each under 15 minutes old. The experiment design, controls, licenses, and manuscript fence are governed by [IBUKT BINDING 1](IBUKT-BINDING-1.md) and the [declaration](IBUKT-DECLARATION.md).

## Code and execution identities

| Artifact | Commit | SHA-256 |
|---|---|---|
| `2d-unfolding/ibukt/run_ibukt.py` | `d93ab9ad8be8d68fe4337d4b2edf7d730a39344e` | `ff1b0c35ccc0ff2c71c9001e049e5efdba555f9dba11fd3def858e14c333a00f` |
| `2d-unfolding/ibukt/connect.py`, successor to launcher commit `a27385f4b` | `e2fd6291eaf704c5ec8a5bf6ba5ff3079d5b9831` | `d2c1843c4124a4257a2769fe55994347ce7729fce079f9ade05f5b9bc5110935` |
| `2d-unfolding/ibukt/rehearse.py` | Same tree as this addendum | `76003e86374ca02a70634967b7e856f8d56edbd5422711d875785b81a2b2d799` |

The prepare fix reads the pinned paper covariance diagonal directly with PyROOT. The mask remains the 205 positive diagonal entries on the 224-cell pT-major grid. The guarded rehearsal compares every ordered index against the legacy dense covariance conversion with `numpy.array_equal`. NumPy 1.26 can invoke `lscpu` when its testing module is imported. Parity on the pinned publication file is pending a successful rehearsal.

The rehearsal runs each probe from its own private scratch directory with its own inputs, logs, and guard inventory. Its no-fit topology probe has 64 CPUs of affinity and reports how LightGBM resolves its default thread count, including whether loky attempted to launch `lscpu`. The fit probes use eight threads and synthetic inputs. The launcher limits total rehearsal wall time to ten minutes and stops a timed-out probe's process group. The rehearsal uses zero allocated node-hours.

## Carry-forward and admission

The fresh `envstage` snapshot and every later admission must each contain exactly one `61556304|ibukt-prepare|FAILED|638|1` row from `sacct`. The budget gate charges the prior failure's actual elapsed time of 638 seconds on one node and retains the original scratch artifacts. A missing, changed, or duplicate row causes a STOP.

At screen admission the budget is **0.177 node-h spent + at most 0.373 node-h for fresh prepare + 5.35 node-h reserved for screen and score ≤ 5.90 node-h**, with the first two terms rounded for display. The exact screen threshold is 1,342 seconds for a new one-node prepare after the previous 638 seconds, with 5.25 node-h reserved for screen and 0.10 for score. The screen keeps its 05:15:00 limit and the bound one-pair preflight.

Each cluster action uses `sacct` for scheduler status, protected reads through `O_NOATIME`, CPU only, and scratch-only writes. The rehearsal precedes a new `envstage`. Prepare, screen, and score each require their preceding PASS and their own pinned director go.

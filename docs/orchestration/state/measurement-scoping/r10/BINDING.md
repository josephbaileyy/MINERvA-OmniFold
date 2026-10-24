# R10 binding: more reconstructed information (2026-10-24)

**By** the paper-tighten lane, as director.

**Binds** [`DECLARATION.md`](DECLARATION.md), merged in PR #301 (`e816ec8e`; the file's sha256 begins `d5db7e9f509393ce`).
The declaration's commit is `b4b1136c1bde6ad29281151156237ca3f3042118`.

**Under:**
- the director's assignment of 2026-10-24, which carries the scoping memo's R10 (`../SCOPING.md` §4.2);
- the 5D design's stop rule (`state/measurement-paper/5d-design-20261023/DESIGN.md` §9). Stage 0 has reported STOP,
  so R10 now decides between continuing and stopping.

## Rulings on the departures (§4.4)

1. **K = 200 instead of convergence: accepted.** At f = 4, 10^5 iterations are unaffordable.
2. **C4 is the count only (`BlobNClusters_sz`); `BlobTotalE` is excluded: accepted explicitly.** Summing BlobTotalE over
   candidates would be a further derived variable chosen for this test, and it is not declared. It stays out of R10.
3. **A fourth, missing bin on the sixth axis: accepted.**
4. **OSB is not computed: accepted.** It becomes a follow-up after a pass. <!-- absence-ok: a scope ruling on what R10's declared design runs, not a claim that a result does not exist -->
5. **The null as permutation twins plus the global null (null3 at f = 1): accepted.** Each twin permutes its
   configuration's own cell labels within the f = 1 cells, so the occupancy is the same. The per-configuration and R10
   states are bound as declared.
6. **P1r–P3r are not run: accepted.** <!-- absence-ok: a scope ruling on what R10's declared design runs, not a claim that a result does not exist -->
7. **X0 on debug QOS** as a 20-minute smoke test: **accepted.** X runs on regular QOS.

## The director's condition (from 2026-10-23)

- **"Any of 11" is explicit.** The report names every configuration that passes, with its margin over its twin and
  over f = 1 on both legs.
- **A single narrow pass** goes in the report's first paragraph.

## Shared files

- **`verify_hash_bindings.py`** goes from 151 to 157 pins. The six added pins are exactly r10's; nothing is removed, and
  the power test is recorded in `binding-delta.txt`. Accepted.
- **The rename `cut_keep_fraction` / `min_departures`** makes the results index classify the config as a design file.
  Accepted.

## Compute and order

1. `r10.py --controls-only` runs locally, K0–K2 on the real events, with 0 node-h.
2. Then X0 on debug.
3. Then X on regular QOS. Its limit is 1.25 × X0's projection.
4. Then Y runs locally.

- **Cap:** at most 4 CPU node-h; the worst case is 2.33.
- Each job is under 12 h and ledgered. Products go to pscratch only.
- Stop and report past 1.25×.
- Any control failure means INCOMPLETE.
- A defect found after output comes to the director before any re-read.

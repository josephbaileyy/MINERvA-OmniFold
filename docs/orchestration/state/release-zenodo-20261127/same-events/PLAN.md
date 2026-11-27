# Same events? EVW2D and EVW5D per-event weights (2026-11-27)

**Question.** Do the EVW2D and EVW5D per-event weights cover the same 32,849,103 simulated rows? If they do, App. D
says so in one sentence. Joseph approved the check on 2026-11-27 ("yes you can run the check"), and the director
accepted this plan as written.

## The two keys, from the committed receipts (main `e5ca821f`)

- **EVW5D.** The receipts are `fd/evw5d-20261125/receipts/attempt2/post/evw5d/`: `constants.json` is `8f009d82…`,
  and `SHA256SUMS` gives `weights.npz` as `0fceefcd…`.
  - The key is "(input npz sha256, entry): entry is the row's index in the npz's MCgen; rows are its pass_truth rows
    in order; not a physical event id". The input npz is `07fccc1a…`, `of_inputs_5d.npz`, which was dumped from the
    5D omnifile.
  - `n_rows` is 32849103. `EVW5D-DECLARATION.md` §2 gives `entry` as uint32 and `truth_pt` and `truth_pz` as float32,
    "the npz's own precision".
- **EVW2D.** The receipts are `evw2d-20261124/receipts/run-20261126/post/out/`: `constants.json` is `1fe4449e…`, and
  `SHA256SUMS` gives `weights.npz` as `bf452352…`.
  - The key column is `entry`, "ROOT entry number in mc_signal_reco" of omnifile `43f8cc16…`.
  - `rows` is 32849103. `EVW2D-DECLARATION.md` gives one row per truth-passing `mc_signal_reco` row, `entry` as
    uint32, and `truth_pt` and `truth_pz` as float64.

**The keys refer to different files.** One is an index into a dump of the 5D omnifile; the other is a ROOT entry in
the 2D omnifile. Equal `entry` values do not mean the same event, and neither file carries physical ids (run,
subrun, gate).

## The matching

Rows are matched **by position**. The hypothesis is that both event loops read the same MC AnaTuples in the same
order and kept one row per truth-passing signal event, in the same order. Truth p_T and p∥ are compared row by row.
Equal entry arrays are reported, but they are not the test.

## The check (`same_events.py`), failing closed

- **T0.** The four files' sha256s against the receipts, each read with O_NOATIME. A Python without O_NOATIME
  refuses. Any mismatch stops the check.
- **T1.** Each `weights.npz` is read through an O_NOATIME descriptor (`np.load`, `allow_pickle=False`). The check
  stops unless `entry`, `truth_pt` and `truth_pz` exist with the declared dtypes and are 1-D, and only those columns
  are loaded. Each `constants.json` is read for its key text and its declared row count.
- **T2.** N(EVW5D) == N(EVW2D) == 32,849,103, or the check stops.
- **T3.** Whether each entry array is strictly increasing, whether they are equal, and if not, the count of differing
  rows and the first one.
- **T4.** For each of p_T and p∥, on every row:
  - the exact-equal count after casting EVW2D's float64 to float32;
  - max |Δ| in float32;
  - max |Δ| with EVW5D upcast to float64;
  - the count of rows differing by more than 1 float32 ulp;
  - for any non-zero |Δ|, its distribution (count, median, p90, p99, max, max in ulps), **with no threshold**.
- **T5.** Only if T4 is not exact on every row: the sorted (p_T, p∥) float32 pairs are compared. That separates "the
  same set, in a different order" from a different set.

The verdict is one of `SAME-ROWS-SAME-ORDER`, `SAME-SET-DIFFERENT-ORDER` or `NOT-EXACT`.

## What it can claim

If T4 is exact on all rows: "the EVW2D and EVW5D weights are on the same 32,849,103 truth-selected simulated rows, in
the same order, with identical truth p_T and p∥ (float32)." That is **not** physical-event identity: neither file has
run, subrun or gate ids.

## Running it

`run_same_events.sh SCRIPT_SHA256` runs from the Mac. It refuses unless `same_events.py` has the director's pinned
sha. Then it opens one fresh ssh (`ControlMaster=no`, `BatchMode=yes`) and streams the script to the conda ROOT env's
`python3 -I`, printing the Python and numpy versions first.
- **Footprint:** no Slurm job, no copy of either file off the cluster, and nothing written there. Peak memory is about
  1.5 GB.
- **Acks:** limitation-resolver (EVW2D's owner) and ibu-chi (EVW5D's owner). There is no cov2d round, because
  neither file is on cov2d's protected list and no job is submitted.
- **Record:** the output is captured on the Mac as `same_events.out` and committed here.

`test_same_events.py` checks the script on synthetic fixtures (14 cases):
- each verdict;
- a float64 detail below float32 that is exact after the cast, with its float64 |Δ| reported;
- a sha mismatch in any of the four files, which stops before any comparison;
- a wrong dtype, a missing column, and a row-count or declared-count mismatch;
- the O_NOATIME refusal;
- the pinned paths and shas.

As positive controls, removing the sha stop fails the sha tests, and comparing in float64 instead of after the cast
fails the cast test.

# EVW5D attempt 2 receipts (BINDING 2, steps 1-3: connect, post, fetch)

Namespace `/pscratch/sd/j/josephrb/evw5d-20261125-r2`; run from `launch/bound/` at ce84191d; job 62000819.
Every value below is pasted from a command run on these files.

## Outcome
- sacct: `62000819|evw5d|COMPLETED|0:0|776|1|2026-11-25T15:34:42|2026-11-25T15:47:38|`
- charge: 0.2156 node-h (cap 0.5)
- VERIFY: PASS
- evw5d.done: verdict PASS failed_controls [] findings ['C-COMPLETE']
- SHA256SUMS digest (`shasum -a 256 post/evw5d/SHA256SUMS`): `31075af667c6cda13d76b0e09831a5e40180069615853a30ae34a325b8be8718`

## Product shas (post/evw5d/SHA256SUMS, written on NERSC; `sha256sum -c` OK in post/sha256sum-c.txt)
```
8f009d828163161418e94997428c80a8c723fa3a015fcb63165861aa3312c3aa  constants.json
d2aac0664f8677b29414a0be9cfdf570af54f3df80a851297ccef21ebdf98e01  constants.npz
83436d151d45a2ba01947a7d780a649fd250e1adec60e9003bf78ac351bb951a  product/data_b-_j-.npz
c2ec93fb529769b5b8cdb56966ac115a4e02da90880e83b8fd23513de9b500f6  run.json
0fceefcdcfcd5c48070453707b55f40e55787909f98481dadcdc82dd0897aba6  weights.npz
```
weights.npz (1,741,008,257 B) and product/data_b-_j-.npz are not in this directory; they stay in the namespace until HPSS and fetch-products (BINDING 3).

## Files
- `post.tar.gz` (sha256 `3a4dc3cf5decc9d9ae43812b33b83356a93e5e323de9c75fcc4471b90ea8d325`): the post's archive as fetched; `post/` is its extraction.
- `lane/`: the Mac side. The launcher outputs for connect, post and fetch; the sacct watch; the connect and post session directories; fetch-scp.err (hpss.tar.gz absent: HPSS has not run). <!-- absence-ok: a statement about this lane's own run steps under BINDING 2, not a claim about the repository -->
- `lane/c32.py` -> `lane/c32.txt`: C-COMPLETE's 32 cells (16 adjacent pairs, equal and opposite ofin - denom). `lane/c1effect.py` -> `lane/c1effect.txt`: the change in the sixteen f if c := 1. Both read post/evw5d/constants.npz.

## C-COMPLETE (finding, not a gate)
max |c-1| 4.098e-4 in 32 of 10694 populated fine cells; the 32 are 16 pairs adjacent along one axis with equal and opposite ofin - denom_nd, consistent with float32 MCgen (`nn_dump_inputs.py:84`) vs float64 denominator binning (`:90`) at bin edges. Setting c := 1 changes f by at most 3.2700502574645185e-06 (lane/c1effect.txt). Priced, not built (the director's completeness ruling):
- (a) No compute. The denominator is the saved rows: eavail step 0b (`docs/orchestration/state/eavail-switch-pricing-20261031/step0/step0b.json`, `c_tuple_multiset_equal` true) found that mc_truth_denom's (5 float64 truth, w_truth) tuples equal mc_signal_reco's as multisets. So c = 1 for any binning, and the stored c's 16 edge pairs are disclosed.
- (b) A sidecar denominator keyed by (07fccc1a, entry): float64 truth (about 1.31 GB) or an int32 denominator fine index (about 131 MB), with a control that re-histograms it to denom_nd bitwise. The read takes about 0 node-h on a login node: step 0 read both trees, 32,849,103 rows each, in 31 s on login37 and reproduced denom_nd bitwise (`step0.json`, `control_C1`). weights.npz is unchanged. It needs its own declaration, tests, reads and GO.
- The lane recommends (a) for v1, with (b) in FOLLOWUPS. The director's ruling and Joseph's decision follow.

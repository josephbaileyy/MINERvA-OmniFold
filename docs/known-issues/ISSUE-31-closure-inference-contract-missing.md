## The closure driver persists no inference contract

`closure_powered_truth_reweight.py:287` saves only `dump_rows_a/b`, `weights_push`, `mc_indices`.
Architecture comes from `meta` (`:261-263`) and the input normalization is derived inside
`build_fullevent_loaders` at run time, so **there is no stored normalization to assert against** when
reproducing a run by inference. The nominal driver stores its norms; the closure driver does not. Any
inference-only reproduction must reproduce the same row population (`dump_rows_b` makes that possible) and
must treat the spectrum reproduction as its only falsification handle.


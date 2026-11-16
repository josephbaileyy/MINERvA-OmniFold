# RSN J1 connect: the submit (receipt)

**By** session tier3-design. This ran on the director's go: `rsn_connect_j1.sh` `b8f8c2af…` and
`rsn_connect_j1_launch.sh` `819be111…`, re-hashed from main `a058a47d` (#1091), after the LL5D gates had ended and the
director had announced `rsn_` and `rdx_`. It ran once, on login27 at 13:13:40Z, with script rc 0
(`j1.session.txt:4, 23`). Nothing was retried.

**What passed** (`j1.session.txt`):
- the deploy HEAD is M_RSN `af711298` with porcelain 0;
- `sbatch_rsn.sh` is `f889a0cf…`;
- r1: the recorded, deployed and bound `rsn_regrade.py` digests are all `661608d8…`;
- `squeue --me` was empty;
- `fence.txt` is `5934e327…`: cov2d, t2a, ll5d, e96data, rpd_;
- the bound launcher's smoke passed with one step (rsn_nc).

**The submit.** J1 was submitted at 13:13:43Z as jobid **61168780** (`rsn_J1`, limit 19:00, regular_milan_ss11).
Its end, COMPLETED 0:0 in 00:11:45, is recorded by the J2/J3 connect's step nc
(`../../connect-j23/run-nc-20261112/`).

`j1.session.err.txt` is the ssh session's stderr, NERSC's login banner.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** J1's submit and the preconditions checked before it.
- **Not citable for:** any reading.

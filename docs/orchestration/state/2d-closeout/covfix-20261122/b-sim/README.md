# COVFIX rev 12 §4.5: the (b) SUPPORT rule's simulated pass probability

Script: 2d-unfolding/covfix/covfix_b_threshold_sim.py, sha256 0c3dd7e0c7288e16e3c7b2dec37341f0b26a98546e862396b58fdf2a0a088f69 (commit 0286ccca94d137babaa550c332618adb8beaea48).
Input: covariance-reported.csv from origin/main (fd/with-cpl/deposit-candidate), sha256 76730c5b7143f8933019a502ca23eed635e45340f7d1ed5534813b2242956170.
Python 3.12.2 numpy 1.26.4 scipy 1.15.2, OMP_NUM_THREADS=2, host Darwin arm64.

Real runs, on the frozen measured set (tier3-design's B-SEL labels, k = 13: R00 R01 R02 R04 R05 R06 R08 R09 R10 R12 R13 R14 R15; record selection.json sha256 4d4205d4cb5e5b98a9aacc18e792a074dfbfa7f8aa05cb11f7f8bfb35d44c634, as stated by tier3-design):

    python3 -B covfix_b_threshold_sim.py --cov covariance-reported.csv --cells R00,R01,R02,R04,R05,R06,R08,R09,R10,R12,R13,R14,R15 --truths 3 --replicas 20000   -> real-k13-t3.json
    ... --truths 2 --replicas 20000   -> real-k13-t2.json

Validation dry runs, all 16 cells, 4000 replicas: dry-k16-t3.json and dry-k16-t2.json. They reproduce the spec's provisional Gaussian table within sampling error.

sha256 of the outputs:
    17cb750af2b7c22f6ca55924aad47b5b5a991af435f7b9ea67f65d7944566c09  dry-k16-t2.json
    9827fcd98dc8d003376ec8a4805dbce34a76bf17dd11c865fc72e270e3b67a4e  dry-k16-t3.json
    3d9b8bb40bf2c0e2e7821859b0b2ef73861b6917eefc6b0146e2468af8c81b7e  real-k13-t2.json
    cd28eba817e761dbbf78c2f29e3449577abbf32fcabc63f9586eb40a0e70a316  real-k13-t3.json

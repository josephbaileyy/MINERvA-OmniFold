# RPD-FLUX4-BINDING: e1's flux4 run (RPD-RECO amendment 1)

Director binding for flux4, the first rerun step of RPD-RECO amendment 1 (`FD-RPD-RECO-DECLARATION-AMENDMENT-1.md`, #1300). It is part of e1, which Joseph authorized on 2026-11-22 and asked to move again on 2026-11-26.

## What is bound

The flux4 package merged in #1395 (head `3db6ef7ba3acbf6e749f4e0dc7bbe11e5aae9537`), on main at `3b427f720037d532831d114335ef8f23fa178fd0`. Its clone pin is S = `2415e8d66d1a9160e724d426eaeb54d458d4b4f7` (#1308's merge). sha256:

    f53a86f6dec50965d1d45cb77bcfc904228ebd96ffa18eb9f87babeb53d1ba1d  production-config.ready.json
    8989815086ec0ed771d333b109d3ef627e85dbfebe9d76d7b51f6336fe637215  rpd_flux4_connect.sh
    4da3ee5eb10ca6465aa5649b362ca61f8107ffdf29807a316af647820417b585  rpd_flux4_fetch.sh
    70c64e0cc155e72dfd5f99d10d26c658c358fea608b58bd874f558af54916936  rpd_flux4_launch.sh
    1371a21a867739b6250175fe5fd7667f6175d055d115b5079d66f9b9070fc512  tools/fence_overlap.py
    73d02cd0e364c85c9ce75bea214a8f93df62b155179c206847ce8b6903ba0d4a  tools/gen_flux4.py

The director checked that the package was generated from flux3's reviewed package by counted replacements. The connect, launch and fetch scripts differ from flux3's only in the declared items: the pins at S, the config digest, the root's name, the geanttw sacct fence, the three-lane ack file, step 5b (the sidecar stat) and step 2b (the true-energy join record in place of the flux2 identity). The package passed five suites, 91 checks and 57/57 mutants, and an agy read (gemini-4-hydrogen-high) gave GO with five non-blocking notes, all taken.

## What the GO covers

1. One `rpd_flux4_launch.sh connect <new empty session dir> <login node> <ack.txt>`, which submits ONE job, `rpd_flux4`: shared QOS, 4 CPUs, 16G, `--time 01:00:00`. The ack file carries three lines (cov2d, tier3-design, minerva-lib), each at most 6 h old. The connect refuses while any cov2d*, t2a*, rpd* or geanttw* job is queued or running (sacct). Step 5b requires the sidecar to be a regular file of 2,364,943,114 bytes, by stat only.
2. One `rpd_flux4_launch.sh fetch` after the job ends. Step 2b checks the true-energy join record, and a miss exits 15 after the records are sent.

Not covered: any resubmission, P0 and every later step of the amendment (each needs its own binding), any write outside `/pscratch/sd/j/josephrb/rpd-reco-flux4-20261126/`, and any write to CFS.

## The NuE file

flux-extract constructs `FluxReweighter(14, True, …)` (`fd_rpd_reco.py:1921-1928` at S) inside `staged_mat_prefixes`, so MAT opens only custody's staged copy of the NuE constraint file (`fd_rpd_reco_custody.py:561`), as flux3's strace showed. The original is read once, in custody's stat-bracketed O_NOATIME staging (two reads), and its stat before and after is logged (condition (c)). This is the one declared exception to cov2d's protected paths, on flux3's terms. cov2d's line in the ack file is its no-objection for this run.

## Budget and credential

The measured expectation is about 700 s, about 0.0076 node-h. The ceiling at the 1 h limit is 0.039 node-h. The balance was 488 node-h on 2026-11-26. The charge is read from `sacct`. The NERSC certificate is valid until 2026-11-27T14:22:19Z (ssh-keygen -L, UTC), and no session is used past that time.

## Receipts

A receipts PR carries the connect and fetch outputs, the job's records and sacct line, the true-energy join record, the protected-read record and the stat log.

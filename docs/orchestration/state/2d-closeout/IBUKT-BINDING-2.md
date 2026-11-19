# IBUKT execution binding 2 for review

This binding proposes run `ibukt-20261119-d` under [A2](IBUKT-DECLARATION-A2.md)
and a separate [signed-data study](IBU-SIGNED-DATA-DECLARATION.md). It supersedes
the run-c deployment and budget when reviewed. The original binding's fences
and outcome licenses continue to apply as amended by A2. Each exact launcher
needs a separate stage approval and fresh cov2d and tier3-design fence
acknowledgments under 15 minutes old. Rehearsal, signed-data and Slurm stages
each have their own receipts. This draft records no execution approval.

## Decisions and accounting

[Decision PR #1232](https://github.com/josephbaileyy/MINERvA-OmniFold/pull/1232)
merged at `f0d298611df010a31c5bed7f110af96c29a323e8`. DECISION-20261119d
(SHA-256 `ef5f9862d65a75bdbdea8084eaae022da815cc6f680b147f61effd7788e65a93`)
sets the cap at **6.50 CPU node-hours across all IBUKT attempts**.
DECISION-20261119e authorizes the signed-target choices and the declared data
study with reviewed code and fresh fences. Each admission receipt carries the
cap, merged decision commit, and decision digest.

Fresh `sacct` requires exact terminal rows for jobs 61556304, 61559122 and
61567091, totaling 1,936 seconds on one node. The fresh IBUKT reservation with
0.50 hours for prepare, 5.25 for screen and 0.10 for scoring forecasts 6.3878
node-hours including prior spend. The unchanged one-pair runtime forecast
and the cap both apply. All operations use CPU only, protected reads through
`O_NOATIME`, scratch-only writes and `sacct` for scheduler status.

## Exact code and document identities

The deployment commit is the tree containing the following pins. The connect
launcher additionally pins that commit and this binding. Its SHA-256 belongs
in each stage's approval packet and execution receipt.

| Artifact | SHA-256 |
|---|---|
| `ibukt.py` | `ef8590cf6d6d025b6db1fb8fdd100f76114390ac78eded62274b2c077c290789` |
| `run_ibukt.py` | `f2b4c017e1a2e84c2cb30b43a8824b95c3f7e022f5fca23b0ceac2a750c33683` |
| `config.json` | `60d6c4d747596137423a869ac315c484ef65ad69f3ec209d6fd73d6e573c716c` |
| `jobs.py` | `76d7af1aa1488aa2abd0053dfd241a1052f5127d6b610e8090625ff7686ade45` |
| `screen.sbatch` | `d86d12b0180fd9a3f48e00b9655a45683f90de8c3df5d5d72ff28d35999f8e9a` |
| `rehearse.py` | `ced65b568c23e5fa64ca4750f556cd9bc50de5e0301748cc58143b7012cca1f9` |
| `signed_data.py` | `0d11502f74b18b09fcae7fa8082c1fa622332bb3c9787622fedac230a17c6170` |
| `launch_signed_data.py` | `e0358bdb4326c403a0a766bfb5de249e85a205e596d5b3f49ecca5f8c9c0b9fa` |
| `IBUKT-DECLARATION-A2.md` | `e7911e5d169688c01aa608038afbaaf7dc74305a9409e847a5318c3812ee179f` |
| `IBU-SIGNED-DATA-DECLARATION.md` | `b7a80cf233a3588708c1949c0d04482273c391274aebcb45c0666faefc64182d` |

## Rehearsal and signed-data resource envelope

The guarded synthetic rehearsal uses zero allocated node-hours and must
finish with a PASS summary before fresh IBUKT envstage. The signed-data
study is a separate Linux login-node action. The launcher requires the
approved SHA-256, the pinned ROOT environment, the six staged and
digest-verified inputs, and a clean historical checkout at
`77d76cfc2d621f8faa010b75006811868494652a`. The guard permits that exact
historical checkout as the only additional repository tree. The historical
driver is hash-checked immediately before the REF-C2C1 file-based load.
The launch envelope allows 480 seconds, a 16 GiB virtual address-space
limit, and one thread in the numerical libraries. The launcher measures
wall time and maximum resident memory and records both in terminal PASS or
STOP receipts. These bounds require review before the first measurement.

The publication calculation reads the covariance directly with PyROOT and
uses the same positive-diagonal mask and NumPy pseudoinverse convention as
the reference comparison at `af70e9c4`. The newer comparator in the IBUKT
config (`7e641754…` versus the reference `1dd5ff52…`) changes a plot label.
The signed-data path imports neither module. Its controls reproduce the
recorded E_R and rounded C2 distances before publishing a reading.

A failed identity, inadmissible target, or exhausted envelope is a terminal
STOP for that attempt. Only a complete screen may be scored. Neither study
changes manuscript wording or authorizes publication adoption.

# Authorization of the corrected PET reservation

Joseph approved the exact amendment at `41a216544a526999d8af54d971808bc39dc97aa5`
in the task conversation on 2026-09-11:

> I approve RESOURCE_AMENDMENT-20260911.md at commit 41a21654: one A100, 32 reserved Slurm CPUs and 56 GiB RAM per allocation, with ceilings of 290 GPU-hours, 9,296 reserved Slurm CPU-hours, 200 GiB storage, and two concurrent full jobs. Proceed through calibration and, only if its existing headroom and integrity gates pass, the frozen campaign without further permission requests for covered steps. Preserve all existing scientific criteria, stop conditions and scope restrictions. Report measured resource usage and distinguish synthetic routing conclusions from real-data representation performance.

The machine-readable [authorization](resource-authorization.json) binds the
unchanged [amendment](RESOURCE_AMENDMENT-20260911.md) by SHA-256
`d419c4fa69b8f86f027831169861590924c718b99f35c79b6d2db912ced3af37`. Historical pending wording and its pending
JSON remain preserved. This record supersedes only that pending status and the
original reservation limits. All scientific files and gates remain frozen.

Authorized next action: one guarded calibration allocation, then only if its
existing integrity and 20% headroom gates pass, the fixed 24 paired jobs.
Technical failure stops dependent work without retry or replacement. No new
source access, real-data training, adoption, covariance or Gate-6 work is granted.

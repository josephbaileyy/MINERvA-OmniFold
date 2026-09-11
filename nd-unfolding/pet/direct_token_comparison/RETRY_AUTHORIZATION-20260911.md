# Single calibration retry authorized

Joseph approved the retry proposal at `c9def5d21dcffae34ab819734e94c418dac253af`
in the task conversation:

> I approve the single calibration retry described in RETRY_PROPOSAL-20260911.md at c9def5d2, explicitly granting one exception to the no-retry rule for job 58198332. Use one A100, 32 reserved Slurm CPUs, 56 GiB RAM and at most 118 minutes. Count the failed allocation toward all existing aggregate ceilings. Proceed to the frozen full matrix only if calibration passes the existing integrity and 20% headroom gates. A second technical failure stops execution; all scientific criteria and scope restrictions remain unchanged.

The [machine-readable authorization](retry-authorization.json) binds the
unchanged [proposal](RETRY_PROPOSAL-20260911.md) by SHA-256. Its historical
pending wording and pending JSON remain preserved. One new calibration only,
then the unchanged conditional matrix if every gate passes; a second technical
failure stops. The prior 79 allocated seconds remain charged to all limits.

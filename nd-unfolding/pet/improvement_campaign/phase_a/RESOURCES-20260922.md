# Phase A Resource Measurements

*   **Remaining allocation balance (m3246, m3246_g)**: NOT ESTABLISHED. NERSC `iris` or `sbank` is required to view allocations but is unavailable in the environment. `sreport` lists used CPU minutes (m3246: 1.6M, m3246_g: 21.9M) but not the remaining balance.
*   **Storage quota/usage (/pscratch and CFS)**:
    *   `/pscratch/sd/j/josephrb`: 16.33 TiB used / 20.00 TiB quota (81.7%).
    *   CFS (`m3246` project): 81,060 GB used / 102,400 GB quota (79%). `m3246_g` is the same storage project.
*   **Shared GPU queue depth**: `squeue -q shared` shows 2,470 total jobs in the shared queue.
*   **Cumulative GPU-hours for historical comparison**: 12.70 GPU-hours (and 21.28 CPU-hours), parsed from the job IDs in `campaign_jobs.txt` via `sacct`.

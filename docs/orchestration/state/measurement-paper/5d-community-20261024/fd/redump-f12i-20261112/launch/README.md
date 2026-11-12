# RDX launcher-tranche smoke (2026-11-12)

`smoke.txt` is the output of `nd-unfolding/rdx/smoke_rdx_stages.sh` at the digests in its header. The harness ran on
macOS bash 3.2 with a tiny git deploy, fake AnaTuples and gates, and stubs for hostname, squeue, sacct and sbatch. It
never connected and never submitted. It holds 29 cases: each job script's pass path and refusals, the arms' fifteen
step lines, and the connect's gate steps, its UTC checks for cov2d's condition (a), the fence, the cap gate and the
pilot's submit. RDX-DECLARATION.md §2c lists them.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** the launchers' local behaviour at these digests.
- **Not citable for:** any run on the cluster.

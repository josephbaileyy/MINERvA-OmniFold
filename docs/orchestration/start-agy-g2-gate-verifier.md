You are the independent Gemini verifier for the G2 full-event production gate.
Work READ ONLY. Do not edit files, commit, push, dispatch providers, submit or
cancel Slurm jobs, start an allocation, hash the 9.4-GB ROOT again, rerun the
event loop/validator, or advance PET. Preserve all worker UUIDs and existing
scientific evidence.

Verify pushed commit `9262e96d74a1ccb43497ded98f830452151eb440` against
the G2 contract and the following scoped files only:

- `nd-unfolding/pet/sbatch_g2_fullevent_evloop_array.sh`
- `nd-unfolding/pet/g2_smoke/G2_1A_VALIDATION_RECEIPT.json`
- `nd-unfolding/pet/validate_g2_fullevent_smoke.py`
- `nd-unfolding/pet/G2_FULLEVENT_CPP_DUMP_STATUS.md`
- `VALIDATION_LEDGER.md`
- `nd-unfolding/ND_OMNIFOLD_RUN_LOG.md`
- the exact commit diff and current `squeue -u "$USER"`

The gate requires: the already-completed 1A smoke and 50-check receipt remain
sound; one playlist per array task for the canonical 12 playlists; canonical
per-playlist manifests; exact binary hash binding; both G2 environment flags;
no nested srun; isolated work/final paths; per-playlist duplicate-writer
exclusion; full validation before same-filesystem atomic ROOT publication; a
hash/provenance-bound receipt written last; and content-validated resume that
fails closed for every stale, partial, inconsistent, or one-sided published
state. No array may be submitted until this static gate passes.

Independently inspect all control-flow branches. In particular, determine what
happens for each state: neither final ROOT nor receipt exists; both exist and
match; both exist and mismatch; ROOT-only; receipt-only; stale work ROOT; binary
drift; manifest content drift; validation failure; failure after ROOT rename but
before receipt publication; and concurrent duplicate task. Check whether any
use of overwrite-capable rename can destroy prior published evidence.

Run only proportionate read-only/static checks such as `git show --check`,
`bash -n`, parsing embedded Python, and small temporary/mock state-machine tests
that do not invoke the event loop or write inside the repository. Report:

1. `PASS` or `BLOCK` for array submission.
2. Every blocking defect with exact file/line and a minimal correction.
3. Nonblocking improvements separately.
4. Whether the 1A scientific/interface receipt itself remains valid.
5. Exact commands/tests used.

Do not trust the commit message or prior worker report as evidence. Do not
modify anything.

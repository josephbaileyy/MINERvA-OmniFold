# B5D BINDING 1: the 5D blocks' read connect (login node, 0 node-h) (director, 2026-11-24)

**Authority:** Joseph, directly to the director on 2026-11-24: "yes build the 5D bias block". This builds the 5D bias
block and fluctuation block for the reported 16-cell covariance from existing products, with no new unfolds. The
director's rulings on its design, also of 2026-11-24, are in the declaration:
- (a): f̂ comes from LL5D's toys at G18 and AR23, with the cal sets as a printed flux-only cross-check;
- (b): LL5D's rebuilt block is the expectation, and no S1 data-derived product is read;
- the C_b family is nominal plus the three A7 truths.

**The declaration:** `blocks5d-20261124/B5D-DECLARATION.md`, sha256
`676c17fc5982a01c21f4c7feae2f6c8cd32b0b8ecdc69ec93882e5e30c0f0b1b`. The director accepted it as written. Its eigen-rank
bands are a disclosed departure from COVFIX's 2D bands.

**Binds** the read connect as merged to main in PR #1314 (merge `88458744077a270cc6af623dfb3b1c261b64eab2`), at the read
head `06def4284220187ce45557c4cc41a4cd9bc4e796`, merged with `--match-head-commit`.

| file (under `docs/orchestration/state/ben-b-20261124/blocks5d-20261124/`) | sha256 |
|---|---|
| `connect/b5d_read.sh` | `309d166d062c71c224a37e85aa2a7c1854107d28f587ccdc6041b5749d891e50` |
| `connect/b5d_launch.sh` | `200d5d570889c884c5b82b3a5762ae1f8bf667e9349ce29a36e65b0aaca34a74` |
| `connect/gen_b5d_read.py` | `e1aa69f7140eed5e734aa438a6377714d51a77f4a07d7daec973f569b674e240` |
| `connect/b5d_overlap.py` | `59c5e7a1c0adabcee14c08d851b54cad17a34234ae92a00d15e58a91f936f12a` |
| `connect/overlap-b5d.txt` | `71f3e0b2ce7e2e32147f8d12be236cd045336ef06d3ba7c52e6a658208e5b393` |

**The sources:** 1,655 pinned files, about 498 MB, each read only, through O_NOATIME:
- LL5D's 1,200 toys and its 454 null-role products, at their pins in LL5D's committed manifest;
- the flux constraint
  `/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt`
  (`e38ad7d2…`).

The flux constraint is in cov2d's protected set and is an RPD flux2 staged original. It is the one acked read.

## What the director checked

- **The shas.** The director hashed each file above from `git show` at the read head and at main, and each equals the
  table. The launcher holds the read connect's sha256 exactly once.
- **The read connect.** 1,654 pinned source lines plus the flux constraint. Its only removals are self-deletes of its
  own /dev/shm copy. It has no sbatch, srun or squeue.
- **The scope.** The PR touches only `blocks5d-20261124/` and the generated indexes.
- **The overlap check:** CLEAR, 251,864 pairs, 0 hits. Its only allowed overlaps are the flux constraint's read, against
  its two owners, cov2d and rpd. Its self-test shows that 8 planted hits each STOP.

## Rulings

1. **The read connect is bound** with the shas above. Any changed byte goes back to the director.
2. **The price: 0 node-h.** One login node and no Slurm job. It writes only `/pscratch/sd/j/josephrb/b5d-20261124` and
   `/dev/shm/b5dc.*`. Nothing is written to CFS.
<!-- absence-ok: preconditions checked fresh before the read (acks, a valid certificate), not claims that a result does not exist -->
3. **Preconditions, all required, before the launcher runs:**
   - fresh acks, after this binding is merged:
     - from cov2d and limitation-resolver, each naming the flux constraint's path;
     - from director-helper-3, for IBUB's running job 61924744;
   - a valid NERSC certificate, valid to 2026-11-25T01:36:35Z. A read that cannot finish before then waits for Joseph's
     renewal. A partial read is a STOP, not a resume;
   - the director's GO, by message, naming this binding.
4. **A purged source BAILs.** An HPSS htar fallback runs only on a loginNN, never a DTN, and only as its own amendment.
5. **After the read:** code, tests, a line trace, mutants, then reads by agy on gemini-4-hydrogen-xhigh and by
   codex-school, then the local build under the declaration. The record goes to the director first. If SE > 0.5 in every
   band, the build stops short of V_F, as declared.
6. **Adoption** of the blocks, or of any inflated V_F, into the reported 16-cell covariance is Joseph's decision, made
   with the numbers.
7. **The fallback,** new toys at non-spent truths, is not authorized. It comes to the director priced.
8. **Any STOP or guard refusal after contact is terminal.**

**CITABLE FOR:** that the 5D blocks' read was bound, and on what. **NOT CITABLE FOR:** any block, any factor, any
adoption, any note wording.

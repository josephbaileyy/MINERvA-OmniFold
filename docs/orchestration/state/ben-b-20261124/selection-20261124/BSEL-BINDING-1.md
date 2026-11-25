# BSEL BINDING 1: the (b) selection's read connect (login node, 0 node-h) (director, 2026-11-24)

**Authority:** Joseph's (b) decisions of 2026-11-24 (`DECISION-20261124b-joseph-b-design-185-bias-block-old-namespace.md`
§1): all 16 cells are labelled measured or exploratory on spent truths only, at κ = 1 with the fixed panel. The
estimator is the current one, frozen after S2R failed its declared rule (S2R-BINDING-1; receipt #1309).

**The declaration:** `selection-20261124/B-SEL-DECLARATION.md`, sha256
`04debd573c7b6a0ad57feb61266384515d4ca2b597d0047cf80aeea303faf8db`. Its rule was fixed before any of its inputs was
read for it. The director accepted it as declared.

**Binds** the read connect as merged to main in PR #1310 (merge `a354090479514210562af601dca5465f50527a60`), at the read
head `ab69e5b4831e02c5769f39fc93448c84cfb1fbea`, merged with `--match-head-commit`.

| file (under `docs/orchestration/state/ben-b-20261124/selection-20261124/`) | sha256 |
|---|---|
| `connect/bsel_read.sh` | `199cc946b5a7238873f99702b55caf0872fce95ed3e253cb9fdbc67c400ad547` |
| `connect/bsel_launch.sh` | `a0fc824fa9ac885c555c62e0b39af4369a4cea3dd63293e6c5d3b98b79383c4e` |
| `connect/bsel_overlap.py` | `dd82eacda983048117752afca471f24f5f73a592297796b79b990278e952af9f` |
| `connect/overlap-bsel.txt` | `d3b67cd55dce3f8ae281072ec9d14bd691aeab9e134fcb9320414594755b846d` |

**The six sources,** each pinned in `bsel_read.sh` and read only, through O_NOATIME:
- `/pscratch/sd/j/josephrb/fd-f0b-20261026/fd_f0b_experiments.npz` (`7384c651…`)
- `/pscratch/sd/j/josephrb/fd-f1-20261027/grade/fd_f1_experiments.npz` (`997c7dae…`)
- `/pscratch/sd/j/josephrb/fd-f1-20261027/f1c/closure/f1_closure_genie_v3_g18.npz` (`198205b6…`)
- `/pscratch/sd/j/josephrb/fd-f1-20261027/f1c/closure/f1_closure_genie_v3_ar23.npz` (`532a6ac0…`)
- `/pscratch/sd/j/josephrb/pv-ladder-20261024/products/L-5D-PV_e_closure_tune_v1.npz` (`eb3e2188…`)
- `/pscratch/sd/j/josephrb/pv-ladder-20261024/products/L-5D-PV_e_closure_nuwro.npz` (`fff9030e…`)

## What the director checked

- **The shas.** The director hashed each file above from `git show` at the read head and at main, and each equals the
  table. The launcher holds the read connect's sha256 exactly once.
- **The read connect.** Its only removals are the self-delete of its own /dev/shm copy. It has no sbatch, srun or
  squeue.
- **The read head's delta** from the head first sent (`81be4cfc`) is one records-only commit: the overlap tool, its
  output and self-test, and MANIFEST. No bound byte changed.
- **The overlap check:** CLEAR, 1,216 pairs, 0 hits, with nothing allowed. "Theirs" is IBUB's composition, IBUB's 19
  `ibub-20261124` entries, `s2r-20261124` and `rdx-20261112b`. Its self-test shows that six planted hits each STOP.
- **The stand-ins:** 6 Debian variants, each as expected.

## Rulings

1. **The read connect is bound** with the shas above. Any changed byte goes back to the director.
2. **The price: 0 node-h.** One login node, no Slurm job, nice and O_NOATIME. It writes only
   `/pscratch/sd/j/josephrb/bsel-20261124` and `/dev/shm/bselc.*`. Nothing is written to CFS.
<!-- absence-ok: preconditions checked fresh before the read (acks, a valid certificate), not claims that a result does not exist -->
3. **Preconditions, all required, before the launcher runs:**
   - fresh acks after this binding is merged, from cov2d, limitation-resolver and director-helper-3 (for IBUB's
     running job 61924744);
   - a valid NERSC certificate, valid to 2026-11-25T01:36:35Z. If the read misses it, it waits for Joseph's renewal;
   - the director's GO, by message, naming this binding.
4. **A purged source BAILs** before any copy. An HPSS htar fallback runs only on a loginNN, never a DTN, and only as its
   own amendment.
5. **This read also serves part 3,** the 5D bias and fluctuation blocks. It authorizes no part-3 build. That waits for
   Joseph's decision.
6. **After the read:** `bsel_select.py`, with its tests, a line trace and mutants, runs locally under the declaration.
   The record goes to the director first. Its labels go to cov2d's §4.5 simulation.
7. **Any STOP or guard refusal after contact is terminal.** It is reported, and nothing is retried without the
   director's word.

**CITABLE FOR:** that the (b) selection's read was bound, and on what. **NOT CITABLE FOR:** any label, any threshold,
any note wording.

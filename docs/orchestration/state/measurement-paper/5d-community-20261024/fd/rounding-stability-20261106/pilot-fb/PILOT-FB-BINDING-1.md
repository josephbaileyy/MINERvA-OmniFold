# BINDING 1 (design): PILOT-FB, forced LightGBM bins against the rounding instability (director, 2026-11-17)

**Binds** [`PILOT-FB-DECLARATION.md`](PILOT-FB-DECLARATION.md) rev 3, sha256 `4dd69f440744905245b223b7b65091c6c66722c3fb39c0a2068d9d4794144c72`, as merged in PR #1211 at **M_PFB = `522ac0b67717315f3fe54377bdbf4af71090948d`**. The file is byte-identical to its audited head `9aabd8bb`.

**Under:**
- [`DECISION-20261117b-joseph-note-plan.md`](../../../../../../DECISION-20261117b-joseph-note-plan.md) item 3. That records Joseph's approval of the pilot, "yes I meant the pilot and the bin edge fixing" (2026-11-17).
- RS1's mechanism finding: rounding-level perturbations break ties among equal float32 values and change LightGBM's histogram bins, and a perturbation that keeps the ties removes the spread. The declaration's §1 cites it.

## What the director checked

Independent design reads, over four rounds, all read-only. Reports are kept under `~/codex-reports/pilot-fb-audit/`.
- **Rev 0** (`260123d1`): FAIL from both Codex and Grok. Four blockers:
  - G3 checked a bin count, not the boundaries;
  - admissibility was not guaranteed for every feature, including the −9999 sentinels and pool-versus-training differences;
  - the outcome table was not a partition;
  - the gate timing was inconsistent, with no detector for an unapplied jitter.
- **Rev 1** (`25b9137c`): FAIL from Grok. Admissibility, the partition and the per-role edges were fixed. Two blockers remained:
  - G3 read the loaded bounds at `%lf`, not the boundaries in use;
  - J's equality did not follow the source-array jitter path.
- **Rev 2** (`3be11fc1`): PASS WITH FIXES from both Grok and Codex. Both rev-1 blockers were fixed at the design level, and the G3 (a)–(c) sufficiency argument holds. Four fixes were required:
  - the stored zero threshold;
  - J2's full `build_pseudo` call;
  - INCOMPLETE excluding a deliberate gate stop;
  - activating fixtures for the G3 mutations.
- **Rev 3** (`9aabd8bb`): **PASS (bind)** from Grok's confirmation read. All four fixes are present, nothing else in the science moved, and no new defect was found.

**The price:** expected 0.63 CPU node-h, with a cap of 0.9. There are 24 unfolds in all, and a round-1 wall projection stops a run that would not fit.

## Rulings

1. **The design is bound as declared at M_PFB.** Code with its tests and declared mutants comes next. Then an independent code audit by two readers, and a code addendum to this binding, before any connect.
2. **The cap is 0.9 CPU node-h.** A projection above it at any gate STOPs to the director.
3. **A connect** needs a sha-pinned connect script and the director's go. It also needs a fence notice to cov2d and the other fenced lanes for the new `pfb_` job family, reads made with `O_NOATIME` (plain reads only where the declaration names them), `sacct` (never `squeue`), CPU only, and nothing written to CFS.
4. **Manuscript fence.** No outcome changes any note or paper wording. The outcome goes to Joseph and Ben as an option, under the declaration's licensed statements.
5. **Timing.** The pilot does not block the note release sent to the co-author on 2026-11-19.

Nothing is submitted, deposited or tagged.

## Binding 1, addendum C1: the code (director, 2026-11-18) — DRAFT by tier3-design for the director

**Binds** the PILOT-FB code at commit **`8da6738a`** (PR #1219, receipt head `a0fffaf9`). The commit that merges
#1219 to main is to be recorded here as M_PFBC. The director checked each file at `8da6738a`:

| file | sha256 |
|---|---|
| `nd-unfolding/fb_pilot_edges.py` | `439e92262c85a86b4aca6b7e368972d2cc0a12bca3c55eb02e5ec019b927965a` |
| `nd-unfolding/fb_pilot_gates.py` | `b55ea40d3691521248813b1702d7c3442aa7564e9956d1a8d211a1522371cd09` |
| `nd-unfolding/fb_pilot_probe.py` | `478316c13b2d902cebbb56e68c3e2762ecc49f57063a545ff87c0fdf9678e464` |
| `nd-unfolding/fb_pilot_analyze.py` | `4e1f92b8c3ea056a6f28b66548a1c1dfe75b4893c63d1f40efbaf98230db4b2d` |
| `nd-unfolding/sbatch_pfb.sh` | `5407e3f90ca3755a464346e7e6fd0f200025164dc10b1f97822720e2e25ad168` |
| `nd-unfolding/pfb_smoke_prep.sh` | `307109fee38eab867bc4dd0dd33f0e02198f2b838069d9ff38ff6791bdfd833f` |
| `nd-unfolding/tests/test_fb_pilot.py` | `a2acdd75b886bfcfe86b6868a82ac1fb0220548527d5c1d1493e05001fa8add6` |
| `nd-unfolding/tests/fb_pilot_mutation.py` | `3f09d061b5a7476e8793fb2b936f40b5693e7237ea88e99d544f9e6a53942add` |

Both scripts pin `setup_salloc_env.sh` at sha256 `ea3c6998d33f45c831b80da5e5228032a19fc392018ede54a7f52f2f283d1d48`.

**Receipts:** `pilot-fb/code7/`, the clean-clone receipts at `8da6738a`:
- tests 83/83 under Python 3.10.20, numpy 2.2.6, LightGBM 4.6.0 and scikit-learn 1.7.2;
- 83 run on the laptop Python, 9 LightGBM tests skipped;
- mutation 151/151 killed by their named tests;
- `bash -n` of both scripts;
- clean-clone CI 38/38 at `a0fffaf9`.

Each round's fixes and tests are in `pilot-fb/code1/` through `code7/`.

### What the director checked

Code reads, all read-only; the reports are under `~/codex-reports/pilot-fb-audit/code1/` through `code7/`.
- **Code 1** (`0be8aaac`): FAIL from Codex and from Grok.
- **Code 2** (`89be3731`): Codex FAIL; Grok PASS WITH FIXES.
- **Code 3** (`04cd5f56`): Codex FAIL; Grok PASS WITH FIXES.
- **Code 4** (`cc38f157`): Codex FAIL on the smoke and the job; Grok PASS on the smoke and PASS WITH FIXES on the job.
- **Code 5** (`98a3e0cc`): FAIL on the smoke and the job (codex-school).
- **Code 6** (`e3e2c887`): a read scoped to F1–F6. F2, F3, F5 and F6 were FIXED; F1 and F4 PARTLY FIXED; one
  regression.
- **Code 7** (`c41c5a8c`): a read scoped to G1–G3. G2b was FIXED; G1, G2a, G2c and G3 PARTLY FIXED.
- **Code 7.1** (`8da6738a`): the director's own diff check, **PASS**. The diff `c41c5a8c..8da6738a` holds exactly P1–P3
  in the two scripts, plus their tests and mutants. Every sha matches, and the analyzer, edges, gates and probe are
  unchanged. The director also ran three probes:
  - the attribute parser classifies `-x`, `-rx` and readonly-plus-export as exported, and `-r`, a plain variable and a
    name containing "x" as set;
  - the anchored version regex rejects `24.05.4garbage`, while 23.02.2 parses and is then stopped by the comparison;
  - `/usr/bin/python3 -I -S -B` gives `sys.dont_write_bytecode` True.

### The reviewed launches (the only approved entry)

The smoke, on a login node. The guard refuses inside an allocation before `env -i` clears `SLURM_JOB_ID`:

```
[ -z "${SLURM_JOB_ID-}" ] && /usr/bin/env -i HOME=/global/homes/j/josephrb PATH=/usr/bin:/bin /bin/bash --noprofile --norc <deploy>/nd-unfolding/pfb_smoke_prep.sh <deploy> <pin> /pscratch/sd/j/josephrb/pfb-20261117-stage
```

The job. `env -i` means no SBATCH_EXPORT reaches sbatch, and `#SBATCH --export=NIL` creates no login environment on
the node:

```
/usr/bin/env -i HOME=/global/homes/j/josephrb PATH=/usr/bin:/bin sbatch <deploy>/nd-unfolding/sbatch_pfb.sh <deploy> <pin> /pscratch/sd/j/josephrb/pfb-20261117-stage /pscratch/sd/j/josephrb/pfb-20261117
```

`<deploy>` is a clean checkout at the pin `<pin>`, a commit that carries the bound files unchanged. The job's first
shell is the script's shebang, `/usr/bin/env -S -u BASH_ENV -u ENV /bin/bash --noprofile --norc`. If `sbatch` is not
on `/usr/bin:/bin`, the connect names its absolute path inside the same `env -i`.

### Accepted residual risks (each fails closed, or is detection only)

1. The conda and setup closure's side effects under the declared HOME, and its incomplete pre-execution inventory. The
   xtrace closure is an inventory, not confinement.
2. Slurm opens `slurm-%j.out/.err` in the stage before stage-check runs. A link there is detected and refused, not
   prevented.
3. The live TimeLimit string is first seen on the job. The check fails closed.
4. `bash script` invoked without the shebang. The reviewed launches are the only approved entry.
5. The dynamic loader's own environment ahead of `env -i`. The launches call `/usr/bin/env` by absolute path, and the
   job reproduces the smoke's setup values exactly.
6. INDEX feature content. The job reproduces the smoke's INDEX bytes, which the prep produced.
7. An empty fit column is classified INFEASIBLE.
8. The O_NOATIME copier of RS1's A0 products and the σ receipt into the stage is connect-side and is audited at the
   connect. The analysis requires each copy to be a plain file of its own, at its pin, physically inside the stage
   and not a protected original's inode.
9. **The readings §6 names.** §6's "S3 on R00–R15" is read as the relative policy shift |F_a/F_b − 1|
   (`readouts_cells16_relative_policy_shift`), because the pseudo-data σ is defined on the 153 functionals only. §6's
   "gate overhead" is `readouts_gate_seconds_in_unfold`: each unfold's own gate time, excluding the analysis's
   aggregate checks, the sidecar binding and the round-1 gate (declaration §6, lines 372 and 375).
10. The analyzer's `--stage` is not bound beyond the root check.
11. A setup could define a shell function named like the absolute interpreter path, or set loader-trace variables.
    Either can suppress the refusal record on a mismatch. The job still exits nonzero and never fits (under item 1).
12. A readonly declared variable that the setup clears cannot be restored. The denied-variable path still returns 97,
    and the job refuses.
13. **A director gate replaces the help-text evidence for NIL.** Before the job go, the director reads the
    `sbatch --version` line in the smoke's `smoke-sbatch.txt` and confirms it is at least 23.02.3. The runtime check
    alone does not prove NIL support: an older sbatch could read `--export=NIL` as a variable list and still set
    `SLURM_EXPORT_ENV=NIL`. A vendor-suffixed version line, such as `slurm 25.05.0-1`, makes the smoke exit 8. That
    fails closed, and the director rules on it at the smoke.

### Rulings

1. **The code is bound as merged at M_PFBC**, with the receipts above.
2. **The cap is unchanged at 0.9 CPU node-h.** `--time=0:50:00` on one exclusive node is 0.833 node-h. The round-1
   wall projection (3 × round 1 ≤ 2,900 s) stops a run that would not fit.
3. **The order, each step on its own go:**
   1. cov2d's ack of a fence notice for the new `pfb_` family;
   2. after Ben's read, **the smoke** (0 node-h, login node), by the reviewed launch. It creates the stage, writes
      `smoke-edges/`, `smoke-receipt.json`, `smoke-setup-env.txt` and `smoke-sbatch.txt`, and exits 8 if it finds no
      NIL support;
   3. **the copy connect**: a sha-pinned script, with its own go and audit (item 8). It copies RS1's 21 A0 products and
      the σ receipt into the stage with O_NOATIME, as plain files;
   4. **the director's r13 read** of `smoke-sbatch.txt`;
   5. **the job**, by the reviewed launch, on the director's go. It repeats every preflight check before it creates the
      root;
   6. **the analysis**, then the outcome to Joseph and Ben as an option (the binding's ruling 4).
4. **Any STOP, refusal, exit 8, or failure comes to the director unrepaired.** Nothing is re-run without a new go.
5. **The connect rules of ruling 3 above stand:** `sacct` only (never `squeue`), CPU only, nothing written to CFS, and
   the fence notice.
6. **The manuscript fence stands.** No outcome changes any note or paper wording.

Nothing is submitted, deposited or tagged.

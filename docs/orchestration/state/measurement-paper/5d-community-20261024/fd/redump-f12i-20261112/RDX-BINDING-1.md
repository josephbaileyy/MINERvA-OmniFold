# BINDING 1 (design): RDX, the event-loop re-dump for the fresh referee's F1.2(i) (director, 2026-11-12)

**Binds** [`RDX-DECLARATION.md`](RDX-DECLARATION.md) design rev 3, sha256 `a37c49e49af8d8ea…`, as merged in PR #1090
at **M_RDX = `e747fc6c62a281aeca5d93ec173bb10fe231f672`**, byte-identical to its audited head `b3f61e0c`.

**Under:**
- the fresh referee round's F1.2(i), on whether truth information outside the five features matters
  (`state/2d-closeout/stageF/methods/methods-short-20261109/RESPONSE.md`);
- Joseph's instruction of 2026-11-11 to run new analyses that are not too costly;
- `RSN-BINDING-1.md` ruling 6, the approval in principle with a cap of 2.5 node-h, pilot included;
- [`DECISION-20261112-joseph-1a-cfs-and-redump-timing.md`](../../../../../DECISION-20261112-joseph-1a-cfs-and-redump-timing.md):
  the paper does not wait for this lane.

## What the director checked

**coverage-5b-audit's design reads,** over three rounds:
- **Rev 1** (`faf53d96`): five majors.
  - D1: the appended truth-only miss rows would get `truthx` = 0 through KNOWN_ISSUES #12's rebind.
  - D2: C-BKG needs no pilot.
  - D3: there was no permuted null.
  - D4: "the five features suffice" overreached.
  - D5: the build was not pinned to S0's MANIFEST.
- **Rev 2** (`319d38d0`): D1–D5 closed. One new major, D6: `truthx` was checked only by row count, so a
  misaligned column would read like the permuted null X1p.
- **Rev 3** (`b3f61e0c`): D6 closed. `truthx` and `mc_id` share the sentinel mask, the per-row join gate
  C-TRUTHX-NPZ runs before stage 3, and two mutants are declared. **GO for code**, with no blockers or majors.
  Lows y1–y5 are held for the code audit.

**The reference:** MP-1's bitwise chain (S0 `base_cv` 1A, `lat_zero.npz`), with each arm carrying its own nominal.
`of_inputs_5d.npz` is not the reference, because it came from a different binary and dump path
(`FD-CT-5B-INPUTS.md`:41-43, 53-55).

**The price:** projected about 1.40 node-h, with a ceiling of about 2.17 at the declared limits.

## Rulings

1. **The design is bound as declared at M_RDX.** No code exists yet. Code C1–C4, with tests and declared mutants,
   comes next. Then a code audit and a code addendum to this binding, before any build or connect.
2. **The price:** a **cap of 2.5 CPU node-h**, the pilot included. A projection above it at any gate STOPs to the
   director.
3. **Order:**
   - stage 0 (the build and D5's provenance) and the 1A pilot with C-ALIGN-1A and C-TRUTHX come first;
   - stage 2 only after both pass;
   - stage 3 only after C-TRUTHX-NPZ passes.

   Each connect's shas come to the director first. A new job-name family is announced to every fenced lane before
   its first submit. The inputs exposed to purge are read before 2026-12-15.
4. **C-BKG is out of this lane's scope.** It ran separately on 2026-11-12, at 0 node-h, on S0's `base_cv` 1A (#977,
   `methods-short-20261109/cbkg-20261112/`).
5. **Licence:** as D4 scopes it. Adding E_ν, the true vertex and the leading-proton KE moves the result by no more
   than the declared floor, beyond X1p, in MP-1's chain. Nothing is said about untested quantities.
   <!-- absence-ok: a scoping statement of this lane's licence (D4), not a claim that a result does not exist -->
6. **Timing:** the methods paper does not wait (#1092). A result ready before the paper is final is folded in through
   the usual value checks and reads.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** the bound design, price and order.
- **Not citable for:** any reading. No code exists, and nothing has run.

Nothing is submitted, deposited or tagged.

## Binding 1, addendum C1: the code C1–C4 (director, 2026-11-12)

**Binds** the RDX code and declaration rev 4, as merged in PR #1095 at
**M_RDXC = `950a88ec40339b2bfab5d7440646a35dc87f248b`**. The audited head is `a3f2c05c`. The director re-hashed every
file below at both commits, and each is byte-identical.

| file | sha256 (prefix) |
|---|---|
| `RDX-DECLARATION.md` (rev 4) | `0252f731ed26b215` |
| `nd-unfolding/rdx/runEventLoopOmniFold-truthx.patch` | `578c64ea600e6cba` |
| `nd-unfolding/rdx/rdx_common.py` | `177259b8f8bc6023` |
| `nd-unfolding/rdx/rdx_dump.py` | `9c0878631e0be815` |
| `nd-unfolding/rdx/rdx_unfold.py` | `83d585a490954987` |
| `nd-unfolding/rdx/rdx_provenance.py` | `6a85d86bc371f1d6` |
| `nd-unfolding/rdx/rdx_align.py` | `9d71cf6d1935a004` |
| `nd-unfolding/rdx/rdx_truthx_rows.py` | `db9456c3954dee42` |
| `nd-unfolding/rdx/rdx_truthx_npz.py` | `32372e2dfaa157a1` |
| `nd-unfolding/rdx/test_rdx.py` | `ce8ed1c64ae38e6f` |
| `nd-unfolding/rdx/rdx_mutation.py` | `11d9ae53c081baa3` |

**What the director checked:**
- **coverage-5b-audit's GO** at `a3f2c05c`, with no blockers or majors. Its reruns gave 34 tests OK and 47 of 47 mutants
  killed, line-identical to `code1/`.
- **The director's two checks:**
  1. The patch applies byte-exactly to the pinned source `57792e42` with `-p1`. The audit read it in full: every new
     fill is gated, and the miss rows are written from the truth-loop cache.
  2. A misaligned sidecar cannot pass. The dump's replica of the kept-row walk matches `collect_signal_nd` step for
     step and refuses unless all six arrays equal the npz bitwise. The join compares the kinematics too, so a
     combined `truthx` + `mc_id` shift fails. The audit's own mutants were killed: that shift, the join reduced to
     `truthx` alone, and uniqueness dropped.
- **The departure from C2 and C3's wording,** accepted on 2026-11-12. RDX adds only new files: a build-time patch, a
  sidecar npz and a wrapper. `und.py` (RE1's pin), `rsn_unfold.py` (RSN-BINDING-1) and the tracked `.cpp` (D5's pin)
  are untouched.

**Rulings:**
1. **The code is bound as merged at M_RDXC.**
2. **No job is authorized here.** The launcher tranche is next: the stage-0 build and provenance, the per-playlist
   event-loop job, the merge-and-dump job, and stage 3's arms launcher and task table. It needs its own audit delta
   and an addendum J1. It carries:
   - the `rdx_` job family, announced to every fenced lane before the first submit;
   - the fence list;
   - per-stage input overlap;
   - the cap gate at 2.5 node-h, counting submitted-but-unbilled jobs at their ceiling.
3. **The audit's low z3** (the kept-row walk over about 32.8 M merged rows, unmeasured against the 0:20 merge-and-dump
   limit) is resolved in the launcher tranche, before any merge job, so that it cannot push the price past the cap.
   Lows z1, z2 and z4 go on the follow-up list.
   <!-- absence-ok: a scoping statement about a projected wall time, not a claim that a result does not exist -->

Nothing is submitted, deposited or tagged.

## Binding 1, addendum J1: the launcher tranche (director, 2026-11-12)

**Binds** the RDX launcher tranche and declaration rev 5 (§2c), as merged in PR #1097 at
**M_RDXJ = `3f74c36f8076e61d30c31220e4a45ec075c6a3e0`**. The audited head is `88c6543a`. The director re-hashed every
file below at both commits, and each is byte-identical.

| file | sha256 (prefix) |
|---|---|
| `RDX-DECLARATION.md` (rev 5) | `67b4e8a61f8591a5` |
| `nd-unfolding/rdx/rdx_connect.sh` | `22159ebd99a836ff` |
| `nd-unfolding/rdx/rdx_connect_launch.sh` | `45949bc57f4e4248` |
| `nd-unfolding/rdx/sbatch_rdx_evloop.sh` | `743b9e48cbeb36c3` |
| `nd-unfolding/rdx/sbatch_rdx_merge.sh` | `742503fa085faa5f` |
| `nd-unfolding/rdx/sbatch_rdx_arms.sh` | `e3e031e754351847` |
| `nd-unfolding/rdx/rdx_cap.py` | `457e89efa20b484c` |
| `nd-unfolding/rdx/rdx_merge.py` | `23dce7a447a830f5` |
| `nd-unfolding/rdx/rdx_dump.py` | `122702c647efc451` |
| `nd-unfolding/rdx/rdx_probe_walk.py` | `dedaa80e5fb108e4` |
| `nd-unfolding/rdx/rdx_paths.py` | `948c47e05f22396a` |
| `nd-unfolding/rdx/rdx_tasks.tsv` | `3ec5069127f5f937` |

`rdx_dump.py` changed in this tranche (the vectorized kept-row walk of z3), so this addendum supersedes C1's digest
for it.

**What the director checked:**
- **coverage-5b-audit's GO** at `88c6543a`, after one blocker and one major at `033a3d82`:
  - B1: `POLICY_REL` named a policy file absent from the repo (`prologue3-20261107`), and the smoke's stub at that path hid it. It now names
    `prologue5-20261108`. A test checks that every hard-coded repo path exists at HEAD.
    <!-- absence-ok: the audit's B1 finding about one named path, checked by git ls-files at 033a3d82 -->
  - M1: c1 ignored the walk probe's exit status. It now STOPs before its PASS line, and s2 requires the PASS.
  - The audit's reruns gave 52 tests OK and 51 + 25 mutants killed.
- **z3:** the dump uses the vectorized walk, with the loop kept as the reference and bitwise equality tested. c1's
  probe times both walks on the 1A pilot output, and the merge limit is set from it at step `gmerge`.
- **The NuE flux-constraint exception** (§2c), granted on 2026-11-12 with cov2d's no-objection. Stages 1 and 2 read
  `sorted_NuEConstraint_FHC_RHC_IMD.txt` plainly, once per loop at initialisation, under these terms:
  - the job-start and pre-binary fence checks;
  - the connect's fence check;
  - the rdx_ announcement;
  - the per-job atime and mtime log in ns, with UTC;
  - cov2d's condition (a): s1 takes cov2d's LL5D atime-post UTC time and refuses before it.
- **The AnaTuple check,** accepted: size and mtime against the manifest, with C-ALIGN's bitwise comparison against
  MP-1's hash-pinned references as the guard. A C-ALIGN failure's first diagnostic is a priced sha256 re-hash.

**Rulings:**
1. **The launcher tranche is bound as merged at M_RDXJ.**
2. **Order,** as §2c gives it:
   - s0, then s1, then c1;
   - gs2, then s2, then c2;
   - gmerge, then m, then cm;
   - the commit of `rdx-inputs-SHA256SUMS`, which gives stage 3's pin;
   - gs3a and gs3b, then s3a and s3b.

   **Each step's connect sha comes to the director, and each runs only on the director's go.**
3. **Job family:** `rdx_`, announced to every fenced lane before s1. s1 waits for cov2d's LL5D atime-post time and
   for the director's queue sequencing against E96D, RSN and COV2D-G2R.
4. **Cap:** 2.5 node-h, enforced by `rdx_cap.py` before every submit, with unbilled submissions counted at their
   ceiling. Any projection above the cap STOPs to the director.
5. **Lows** w1–w3, y1–y5 and z1, z2 and z4 go on the follow-up list.

Nothing is submitted, deposited or tagged.

## Binding 1, addendum J2: the s0 fix after the BUILD collision (director, 2026-11-12)

**Binds** the s0 fix, as merged in PR #1099 at **M_RDXS = `ad0535c4a62ac0a20711a4a00f2266ddaf926d7c`**. The audited
head is `13a0ef3d`. The director re-hashed each file at both commits, and each is byte-identical:

| file | sha256 (prefix) |
|---|---|
| `nd-unfolding/rdx/rdx_connect.sh` | `11e7ef921bcc2272` |
| `nd-unfolding/rdx/rdx_connect_launch.sh` | `165fb98ebed89cf8` |
| `nd-unfolding/rdx/sbatch_rdx_evloop.sh` | `7ce210dcab5909fa` |
| `nd-unfolding/rdx/setup_salloc_env.exports` | `e0d3b70088500bdc` |

These supersede J1's digests for the first three files.

**Why:**
- s0 at M_RDXJ STOPped at its build on login27 at 07:37Z (receipt `run-s0-20261112/`). `setup_salloc_env.sh`'s conda
  activation exports `BUILD=x86_64-conda-linux-gnu`, which overwrote the connect's own `BUILD`.
- Provenance had passed in full before the build. The stray `~/x86_64-conda-linux-gnu/` (three entries, all s0's)
  was removed with the director's exact command, rc 0.
- `rdx-20261112` stays in place, spent.

**What the director checked:**
- **coverage-5b-audit's GO** at `13a0ef3d`:
  - `RDXBUILD` replaces `BUILD`, and B is `rdx-20261112b` in the connect and the event-loop job;
  - the collision test runs against the **measured** 82 exports plus the HOST/PREFIX floor;
  - the smoke stub exports every measured name;
  - 54 tests, and 51 + 28 mutants killed.
- **Low w4:** the exports list is a one-node snapshot.

**Rulings:**
1. **Every later RDX step deploys at M_RDXS.** J1's order, cap and fences are otherwise unchanged.
2. **w4 at each s0:** s0 is preceded by the director-approved export probe of 2026-11-12, re-run unchanged. If its
   list contains any name absent from `setup_salloc_env.exports`, that is a STOP to the director before s0.
3. **The s0 go** is given at this addendum.

Nothing is submitted, deposited or tagged.

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

## Binding 1, addendum J3: the c1 fix after the uproot STOP (director, 2026-11-16)

**Binds** the c1 fix, as merged in PR #1166 at **M_RDXC = `11e36cf1a5643ef6db2d480f3d345364d3247592`**. The
audited head is `1ce8941b`. The director re-hashed each file at both commits, and each is byte-identical:

| file | sha256 (prefix) |
|---|---|
| `nd-unfolding/rdx/rdx_connect.sh` | `eae946894be8ce02` |
| `nd-unfolding/rdx/rdx_connect_launch.sh` | `602c728a7b4326f2` |
| `nd-unfolding/rdx/smoke_rdx_stages.sh` | `f02ca57acdfab743` |
| `nd-unfolding/rdx/sbatch_rdx_evloop.sh` (unchanged from J2) | `7ce210dcab5909fa` |
| `nd-unfolding/rdx/setup_salloc_env.exports` (unchanged from J2) | `e0d3b70088500bdc` |

These supersede J2's digests for the connect and the launcher. The job deploy stays at M_RDXS `ad0535c4`: the
checker-path code there equals the PR head, as the audit confirmed.

**Why:** c1 at M_RDXS STOPped on login27 at 22:18:56Z on 2026-11-15 (receipt `run-c1-20261115/`). root_6_28 has PyROOT
but no uproot, and the smoke's python stub had answered the connect's `import uproot` check itself.

**What the director checked:**
- **coverage-5b-audit's clearance** at `1ce8941b`, with no blockers or majors:
  - every checker runs under omnifold_py310 behind `chkenv`, which fails closed (rc 8) without uproot, `omnifile_io`
    or the interpreter;
  - the auditor's own py3.10 control: the real align and rows checkers PASS, and give COULD_NOT_CHECK without uproot;
  - tests 18/18, mutants 36/36 killed, smoke exit 0.
- **Lows for the follow-up list (not blocking):**
  - r1, pre-existing: the rerun reuses the staged `base_cv.root` without re-checking its sha. It fails closed
    through align.
  - r2: `chkenv` prints the numpy and uproot versions but does not pin them.

**Rulings:**
1. **Every later RDX connect uses M_RDXC's launcher and connect.** The job deploy stays at M_RDXS. J1's order, cap and
   fences, and J2's ruling 2, are otherwise unchanged.
2. **The c1 go** is given at this addendum, for one run:
   `bash rdx_connect_launch.sh <new empty dir> <loginNN> c1 ad0535c4a62ac0a20711a4a00f2266ddaf926d7c`.
   - The launcher and connect come from M_RDXC, with their sha256 checked first.
   - Every fence and other lane's hold is checked before the connect.
   - Any STOP comes to the director unrepaired.

Nothing is submitted, deposited or tagged.

## Binding 1, addendum J4: the c2 and m pin-read fix (director, 2026-11-17)

**Binds** the c2/m fix, as merged in PR #1195 at **M_RDXD = `9a333f9f6ca9fb339bbb0734767109de217da5d2`**. The audited
head is `aba25e5f`. The director re-hashed each file at both commits, and each is byte-identical:

| file | sha256 (prefix) |
|---|---|
| `nd-unfolding/rdx/rdx_connect.sh` | `52ad6a0edf92b4ed` |
| `nd-unfolding/rdx/rdx_connect_launch.sh` | `256003a1b997a57d` |
| `nd-unfolding/rdx/smoke_rdx_stages.sh` | `916473e546c60b13` |
| `nd-unfolding/rdx/sbatch_rdx_evloop.sh` (unchanged from J2) | `7ce210dcab5909fa` |
| `nd-unfolding/rdx/setup_salloc_env.exports` (unchanged from J2) | `e0d3b70088500bdc` |

These supersede J3's digests for the connect and the launcher. The job deploy stays at M_RDXS `ad0535c4`. No checker,
job script or deploy module changes.

**Why:** tier3-design read the c2 packet and found the defect before any c2 connect.
- c2's ZERO_LOOPS read and m's MP1_ZERO read imported the deploy's `fd_ct_period_inputs.py` under `/usr/bin/python3`.
  That interpreter is Python 3.6.15 on the login nodes, and the module's `from __future__ import annotations` needs 3.7.
- A read-only probe on login27 (2026-11-17T01:17:20Z; `code4/probe/`) confirmed it. Under SYSPY the import raises
  SyntaxError at :37. Under CHKPY it returns the 1A pin `2745e38c…`.
- c2 would therefore have stopped at its first playlist every time.

**What the director checked:**
- **coverage-5b-audit's clearance** at `aba25e5f`, with no blockers:
  - SYSPY runs only `rdx_paths.py` and `rdx_cap.py`, at :66, :70, :74, :116, :149, :198 and :215, never with `-c`;
  - c2's policy covers its 24 reads;
  - the PASS-path smoke uses the real `rdx_paths stage`;
  - each stub past chkenv was checked against the real code;
  - tests 21/21, mutants 47/47 killed, smoke exit 0;
  - the auditor's own SYSPY mutant stops in the smoke.
- **l1:** c2's outputs are `*_<PL>_pl.json`, so c1's records are not overwritten.
- **l2:** a policy check runs over c2's reads.
- **Lows for the follow-up list (not blocking):**
  - p1: the policy list's completeness; the check is lexical.
  - p2: a 3.6-grammar parse test of `rdx_paths.py` and `rdx_cap.py`.
  - p3: the smoke's pin module is a stand-in.
  - p4: the aligns' RSS on a login node is unmeasured. The 3.94 GB in the audit's first note was the walk probe's,
    not an align's. c1 ran the 1A align on login27 without incident.
    <!-- absence-ok: a risk note (no record measures the aligns' RSS), per coverage-5b-audit's corrected p4; not a result claim -->

**Rulings:**
1. **Every later RDX connect uses M_RDXD's launcher and connect.** J1's order, cap and fences, J2's ruling 2 and J3's
   ruling 1 are otherwise unchanged.
2. **The c2 go** is given at this addendum, for one run:
   `bash rdx_connect_launch.sh <new empty dir> <loginNN> c2 ad0535c4a62ac0a20711a4a00f2266ddaf926d7c`.
   - The launcher and connect come from M_RDXD, with their sha256 checked first.
   - Every fence and other lane's hold is checked before the connect.
   - The session log records each align's peak RSS, if the checker prints it.
   - Any STOP comes to the director unrepaired.
3. **m** (the merge submit) keeps its own go, after c2's PASS receipt is merged.

Nothing is submitted, deposited or tagged.

## Binding 1, addendum J5: the merge job's limit, and the gmerge and m goes (director, 2026-11-17)

**Under:**
- c2's PASS receipt (#1197, merged at main `165203c2`): all 12 zero loops staged on their pins, C-ALIGN-PL and C-TRUTHX
  PASS for all 12, and `out/loops.sha256` written.
- J4's M_RDXD launcher `256003a1b997a57d` and connect `52ad6a0edf92b4ed`. The deploy stays at `ad0535c4`.

**A departure from the declaration's wording (`RDX-DECLARATION.md`:334), ruled by the director:**
- **The rule as written.** The declaration sets the merge limit at "1.5 × the vectorized walk's ×12.25 projection".
  c1's probe projects 175 s for that walk, so the literal limit would be about 0:04:23.
- **Why it cannot apply literally.** The merge job runs four steps, `sbatch_rdx_merge.sh`:74-79: merge, nndump, dump
  and k1. 5B's merge step alone took 3:00 (`FD-CT-5B-REPORT.md`:87). A literal limit would TIMEOUT by construction.
- **What the rule was for.** Binding 1 ruling 3 (low z3) asked that the kept-row walk, unmeasured against the old
  0:20 limit, should not push the price past the cap. The walk projection is therefore one term of the whole job's
  limit, not the whole of it.
  <!-- absence-ok: a scoping statement about a projected wall time (as in ruling 3's own waiver above), not a claim that a result does not exist -->
- **The limit used: 0:45:00.**
  - 5B job A's ALL-lane steps, scaled as follows: merge × 1.52, the RDX/base file-size ratio; the loop walk replaced
    by the vectorized walk, plus a full truthx read for the sidecar.
  - That gives 1,352 s.
  - Then the declaration's own event-loop factor (× 1.5) and rounding (next 15 minutes).
- **Memory:** one exclusive node, 512 GB, against about 36 GiB, which is 5B's per-lane MaxRSS scaled by 1.52.
- **The cap still binds,** as the declaration requires. `rdx_cap.py` projects these totals, with each later job held
  at its ceiling:
  - 1.5809 after m;
  - 1.9475 after s3a;
  - 2.3142 after s3b;
  - 2.3142 is under 2.5, with 0.186 node-h of headroom.

  Any projection above 2.5 STOPs to the director. A merge TIMEOUT bills at most 0.75.

**Rulings:**
1. **The gmerge go**, one run, 0 node-h:
   `bash rdx_connect_launch.sh <new empty dir> <loginNN> gmerge ad0535c4a62ac0a20711a4a00f2266ddaf926d7c 0:45:00`.
   It writes `out/gates/merge.ok` naming the pin and `limit=0:45:00`.
2. **The m go**, one run, only after gmerge exits rc 0 with merge.ok as described:
   `bash rdx_connect_launch.sh <new empty dir> <loginNN> m ad0535c4a62ac0a20711a4a00f2266ddaf926d7c 0:45:00`.
   - Before the connect: cov2d's ack, and every fence and hold checked.
   - The connect's own checks must all pass, in order:
     - loops.sha256;
     - merge.ok;
     - policy;
     - chkenv;
     - the MP1_ZERO pins;
     - the O_NOATIME staging of the two lat_zero files;
     - the launcher smoke;
     - fence;
     - the cap gate at 1.5809.
   - After submit, status comes from sacct over the job id, never squeue alone.
   - Any STOP, or any job failure or TIMEOUT, comes to the director unrepaired. Nothing relaunches.
3. **cm** gets its own go, after m's receipt is merged.

Nothing is submitted, deposited or tagged.

## Binding 1, addendum J6: code5 and the stage-3 pin; the stage-3 goes (director, 2026-11-17)

**Binds** code5 (#1205) and the five-line input pin (#1204). The stage-3 pin is #1204's merge commit, **P3 =
`95d1d529dc7c0d677c849e37bf3def06a5f76827`**, which contains both PRs, as coverage-5b-audit required. The director
re-hashed each file at P3:

| file | sha256 (prefix) |
|---|---|
| `nd-unfolding/rdx/rdx_connect.sh` | `1760327b21f21958` |
| `nd-unfolding/rdx/rdx_connect_launch.sh` | `def31c020870bc66` |
| `nd-unfolding/rdx/sbatch_rdx_arms.sh` | `f77c89a5dd3f59ce` |
| `nd-unfolding/rdx/rdx-inputs-SHA256SUMS` (5 lines) | `e5baf9cc20bb1744` |

These supersede J4's digests for the connect and the launcher.

**Why:** tier3-design traced stage 3 before any go and found two defects. A read-only probe on login27
(`code5/probe/`) confirmed F1.
- **F1.** The arms read their pins under PATH's python3, which on login27 is /usr/bin/python3.6, Python 3.6.15. The
  pin module needs 3.7 or later.
- **F2.** gs3a and gs3b checked a different deploy and pin from s3a and s3b, so no order could pass.

**What the director checked:**
- **coverage-5b-audit's clearance** of #1205 and #1204, audited together on main `7effa70f`, with no blockers or
  majors.
  - Every stage-3 step's interpreter–module pair: SYSPY 3.6 runs only stdlib tools; no Python reads a pin; the job's
    3.11 import closure is unchanged.
  - Tests 24/24 under 3.12 and 3.10; mutants 55/55 killed; the smoke exits 0.
  - The auditor's own kill of SUMS line 5 fails the test.
- **F1 fix (option (a)):** `rdx-inputs-SHA256SUMS` carries the two lat_zero lines at MP1_ZERO's pins (`6ca02c3d…`,
  `f09727d0…`), and the arms read all five by awk.
- **A wording reconciliation:** RDX-DECLARATION:302's input table already names the staged lat_zero copies "at the
  digests the stage-3 pin commits". The three-dump wording at :346 is reconciled to :302.
- `lat_RDX_ALL.npz` and `lat_zero.npz` share sha256 `6ca02c3d…` by design (cm README:39).
- **F2 fix:** gs3a, gs3b, s3a and s3b all use deploy3. gs3a clones it at P3, and the other three STOP if it is
  absent.
- **s1:** policy() runs over s3a's and s3b's six reads.
- **Lows for the follow-up list (not blocking):**
  - q2: a failed checkout after gs3a's clone leaves deploy3 to be removed by hand. It fails closed.
  - q3: a 3.6-grammar parse test for the TimeLimit heredoc.
  - q4: no record shows lightgbm importing in the job env; that closure is unchanged by code5.
  - m1: cm has no policy check.

**Rulings:**
1. **The stage-3 goes, in order, each one run, PIN = P3:**
   - gs3a: `bash rdx_connect_launch.sh <new empty dir> <loginNN> gs3a 95d1d529dc7c0d677c849e37bf3def06a5f76827`.
     0 node-h.
   - s3a: the same command with step s3a, only after gs3a exits rc 0 and S3a.ok names P3.
   - gs3b, then s3b: the same, after s3a's job ends COMPLETED 0:0 and its receipt is merged.
2. **Before every connect:**
   - check the launcher and connect against this table, and the arms and SUMS at P3 in deploy3 after gs3a's clone;
   - every fence and hold, cov2d's ack before each submit and the end message after.
3. **The cap still binds.** It projects 1.5159 after s3a and at most 1.8825 after s3b, both under 2.5.
4. **Status** comes from sacct over the job ids, never squeue alone.
5. **Any STOP**, cap refusal, job failure or TIMEOUT comes to the director unrepaired. Nothing relaunches.

Nothing is submitted, deposited or tagged.

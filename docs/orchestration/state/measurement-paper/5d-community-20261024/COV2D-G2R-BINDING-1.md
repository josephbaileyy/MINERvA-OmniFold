# BINDING 1 (design): COV2D-G2R, the 2D universes' consistent rebuild and the coverage regrade (director, 2026-11-11)

**Binds** [`COV2D-G2R-DECLARATION.md`](COV2D-G2R-DECLARATION.md), sha256 `225a89ae568ad6da…`, as merged in PR #1079 at
**M_G2R = `03037c3ebcb21d38e80e4247998f48c787bc56ec`**, byte-identical to its audited head `c8b30f12`.

**Under:**
- the fresh referee round's major 3 (`state/2d-closeout/stageF/methods/secondary-results/referee-methods-fresh-20261111/gpt.txt`);
- the independent consult, which recommended (a+) (`…/secondary-results/consult-sol-2dregrade-20261111/`);
- **Joseph's answers, verbatim.** Asked about the regrade at the first, wrong price of about 10 node-h: "what does an
  independent reviewer think? 10 node hours isn't too big of a cost" (`1caea9a086833353`), then, after the consult,
  "okay ya I agree" (`01b242951b285beb`). Told that the price was about 70 node-h expected, capped near 107, he
  answered "Yes, full regrade (~70)" (`b91329615d2d708a`). Each sha256 is of the text plus a final newline.

## What the director checked

- **coverage-5b-audit's GO** at `c8b30f12`, after three majors at `5cec0586`:
  - M1: §2 keeps the committed toys on the law. The miss rows' proxies shift the Poisson stream's position, but every
    written count is an exact draw at its correct λ.
  - M2: §7's expected price carries the measured 1.08–1.38× slowdown of the corrected unfold.
  - M3: §10's COVERS rows carry COV2D §12–13's pass figures and limits.
- **The price,** re-derived by the audit: **73.6–93.7 node-h expected** from COV2D's 44.67 node-h for 350 universe
  unfolds; 108.8 held; a job fits its 08:54:00 limit with about 1.2 h to spare. The first price of about 10 node-h used
  the wrong row of AUTHORIZATION-20261015 §2.

## Rulings

1. **The design is bound as declared at M_G2R.** Part (a), the 175 corrected universe unfolds at the data, and part
   (+), 350 at G18 and AR23 with C_T rebuilt and the 2D test regraded under COV2D's unchanged rule.
2. **The price:** a **cap of 110 node-h**, within Joseph's "capped near 107" by the audit's measured slowdown. The
   director reported the 74–94 expected range to Joseph on 2026-11-11. A projection above the cap at any gate STOPs to
   the director. `iris` is read before each connect.
3. **The code amendment (§9)** comes next: the driver flag, the override builder and the regrade script, with tests,
   mutants, an audit and a code addendum to this binding before any job.
4. **Order:** after the maintenance and after LL5D's gate jobs end. Every `$UNI` input is read before 2026-12-19. If
   the per-playlist files that P5 used for block sizes are gone, that is a STOP to the director before any unfold.
5. **Reserved for Joseph:** adopting C_new as the reported 2D covariance (§10, part (a) VALID), and the wording of any
   changed coverage sentence, after a PRD-referee read.
6. **The audit's low h2** (§10 lists four of §13's six CANNOT items) goes on the follow-up list. §13 governs as a whole.

Nothing is submitted, deposited or tagged.

## Binding 1, addendum C1: the code of §9 (director, 2026-11-12)

**Binds** [`COV2D-G2R-AMENDMENT-1.md`](COV2D-G2R-AMENDMENT-1.md) and its code, as merged in PR #1083 at
**M_C1 = `4f3180b509415e4c03bd469e1375e0ba6a511c0b`**. The audited head is `58950749` (code commit `62864b16`). The
director re-hashed every file below at both commits, and each is byte-identical.

| file | sha256 (prefix) |
|---|---|
| `COV2D-G2R-AMENDMENT-1.md` | `6886d7204ff63819` |
| `2d-unfolding/re2/re2_driver.py` | `e226daf3f51954c7` |
| `2d-unfolding/cov2d/g2r/g2r.py` | `dbcc416d35565c18` |
| `2d-unfolding/cov2d/g2r/g2r_prepare.py` | `bb97fba12034e39c` |
| `2d-unfolding/cov2d/g2r/g2r_readout.py` | `590ffba1cb8cb654` |

**What the director checked:**
- **coverage-5b-audit's audit,** over three rounds:
  - At `ebc95e05` it was sent the code, and at `cf502c67` the two §2 conditions below.
  - At `cf502c67` it found **one blocker (B1).** The driver raised UnboundLocalError on `json` at :2314 on every
    `--miss-map` run, because `import json` was local to later branches of `main()`. No test reached the line.
  - At `58950749` it gave a **GO with B1 closed.** A live `main()` run with `--miss-map` reaches the unfold. The new
    `main()`-level test and two provenance mutants catch B1. Reruns gave 27 tests at seeds 0–2, then 11 and 18 OK,
    and 23 of 23 mutants killed. Four lows are held (n3, n5, n6, n7), plus n8.
- **The director's two conditions on amendment §2,** the single universe-independent miss map with the override
  built at run time in place of 175 stored override arrays (about 46 GB):
  1. **Bitwise equality with P5's builder on real universes.** This is a **gate, not yet a measured fact.** G11
     (`g2r.spot_check`) compares the override with P5's builder loop on `$UNI`'s arrays for Flux:0, Flux:87,
     VecFFCCQEshape:1 (the last) and MaRES:0. Any difference makes the run INVALID before any unfold. Only the
     prepare job can run it on real data, so the result arrives with that receipt. Separately, the audit ran P5's
     committed builder (`7f346e1a`) unmodified on per-playlist ROOT fixtures and found it bitwise equal. G11 shares
     the map's key and search code; that limit is stated.
  2. **No state carried between universes.** Met: a test interleaves MaRES:0, the last universe and MaRES:0 again
     in one process, each checked bitwise, and a cached-override mutant is killed. Each unfold is also its own
     driver process.
- **The sweep** after B1: a line tracer over all three suites, following subprocesses. Six executable lines remain
  unexecuted, each explained in amendment §2a. The audit confirmed :845 unreachable. The job addendum lists all six.
- **G6 at a tune** applies the declaration's 10⁻¹² relative tolerance (§8), not the bitwise check first coded. It
  still records whether the result was bitwise. The local difference was about 6×10⁻²¹ (BLAS rounding). n8: G6
  also holds C_T and C_T_minus to 10⁻¹², stricter than §8's C_univ wording; the job addendum states this.

**Rulings:**
1. **Amendment 1 binds as merged at M_C1,** with the runtime-override form of §2 accepted on the two conditions
   above.
2. **No job is authorized here.** A second addendum (J1) must come with the director's go before any connect. J1
   carries:
   - the job scripts and the cluster-environment test (numpy 1.26 and the LightGBM end-to-end check);
   - the cap gate at 110 node-h;
   - the P5 per-playlist file check, a STOP if the files are gone;
   - the six unexecuted lines;
   - n8.
   J1 comes after LL5D's gate jobs 61078463 and 61078506 end.
3. **Reserved for Joseph,** as binding 1 ruling 5: adopting C_new and the wording of any changed coverage sentence.

Nothing is submitted, deposited or tagged.

## Binding 1, addendum J1: the jobs (director, 2026-11-12)

**Binds** [`COV2D-G2R-ADDENDUM-J1.md`](COV2D-G2R-ADDENDUM-J1.md) and its job code, as merged in PR #1111 at

**M_J1 = `401733bce290ce122cfbf38f1526e120f174b3ec`**

The audited head is `5da0221e` (code `79669957`). The director re-hashed each file at both commits, and each is
byte-identical:

| file | sha256 (prefix) |
|---|---|
| `COV2D-G2R-ADDENDUM-J1.md` | `b22a486d6c78258b` |
| `2d-unfolding/cov2d/g2r/jobs/g2r_jobs.py` | `7542a68dd344b4cb` |
| `2d-unfolding/cov2d/g2r/jobs/g2r_env.sh` | `b3ad1d04e6f665b7` |
| `2d-unfolding/cov2d/g2r/jobs/g2r_job.sbatch` | `21e4f4ac7330250e` |
| `2d-unfolding/cov2d/g2r/jobs/g2r_envtest.sbatch` | `3971fe8596574b4e` |
| `2d-unfolding/cov2d/g2r/jobs/g2r_prepare.sbatch` | `3c129b3dd7abb6d4` |
| `2d-unfolding/cov2d/g2r/jobs/g2r_submit.sh` | `a9b2a2ba2f8a902a` |

**What the director checked:**
- **coverage-5b-audit's GO** at `5da0221e`, over three rounds:
  - **B1**, at `ab2e1237`: the envtest demanded bitwise equality, which configuration (a) is measured not to give. It
    is closed with RE-2's ≤ 1e-8 rule.
  - **M1**, at `e3a429ea`: the histogram metric was labelled RE-2's but was weaker. It is closed with RE-2's per-cell
    max |a/b − 1| over b ≠ 0, plus a b = 0 clause.
  - **j5** (NaN and inf handling): closed.
  - The final reruns gave 58 tests at seeds 0–2 and 41 of 41 mutants killed. Low j6 is held.
- **The design departures,** accepted on 2026-11-12:
  - the override-off reruns (Flux:23 and MaRES:0) join D_Ud warm, at 09:18:00;
  - the envtest limit is 01:04:00;
  - the LightGBM override end-to-end check is D_Ua's first run, and every other unfold job waits for it.
- **The cap gate** projects the whole campaign and STOPs (rc 9) above 110 node-h, with unbilled jobs at their
  ceiling. Held after the prepare: 107.2. The envtest and the prepare must actually charge ≤ 2.8 node-h together.

**Rulings:**
1. **The jobs are bound as merged at M_J1.**
2. **Each connect comes to the director with its sha and its diff before it runs,** in this order:
   - the envtest;
   - the prepare;
   - D_Ua (its first run is the override end-to-end check);
   - the other unfold jobs;
   - the readout.

   Each one's slot is sequenced against E96D, LL5D and RDX by the fences and the director.
3. **The P5 per-playlist files** must be read by the prepare before 2026-12-09T23:11Z, and `$UNI` before 2026-12-19.
4. **Adoption:** Joseph decided on 2026-11-12 (`DECISION-20261112-joseph-consult-d1-d7.md` D1) that if part (a) is
   VALID and the held-out constructions validate, the rebuilt covariance becomes the reported 2D covariance. The new
   coverage counts are reported under the unchanged rule. The wording of any changed sentence still goes through a
   PRD-referee read, and then to Joseph.

Nothing is submitted, deposited or tagged.

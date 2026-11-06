# REF-C2C1 BINDING 2, step two: the code, the configuration and the run sequence (director, 2026-11-06)

**Binds** the REF-C2C1 code (#787) and its step-two configuration (#810), as on main at:

**M = `77d76cfc2d621f8faa010b75006811868494652a`**

**Under** [`REF-C2C1-BINDING-1.md`](REF-C2C1-BINDING-1.md) (the design, `63a1efa3…`).

| file | blob at M |
|---|---|
| `2d-unfolding/ref_c2c1/ref_c2c1.py` | `128b4e00505f82153d1d400a482b7b1a5a3d56be` |
| `2d-unfolding/ref_c2c1/ref_c2c1_read.py` | `e51367aa3d9d68b8c89f76cd7f556c70bd4a226f` |
| `2d-unfolding/ref_c2c1/config.json` | `96dbbaa223a3dec4ceba80686f07721e87ec9045` |
| `2d-unfolding/ref_c2c1/test_ref_c2c1.py` | `0d2f1a2445fe22130be94635cabb280837be4edb` |
| `2d-unfolding/ref_c2c1/ref_c2c1_mutation.py` | `0e80efd2d927390e4360cf10134e5b74e7554deb` |
| `2d-unfolding/ref_c2c1/run_suite.py` | `f2711d4ea81141205f6ef8a450707051713faf20` |
| `2d-unfolding/ref_c2c1/run_tests.sh` | `f4dbaf1fe57bcf4ab0f128d70c1725aa64ae8d29` |
| `2d-unfolding/ref_c2c1/test_run_suite.py` | `990ec7894a982709298ce3550ffa3fa1e73fe1b9` |

## What the director checked

- **The audit** (coverage-5b-audit, #787 and #810). Its findings:
  - K1 to K3, the staging root, R1 and R2, and the tfile_guard hardening are all closed;
  - the config delta raises no blocker: the lib's full sha equals the listing; "reuse" rests on C-DRAW's PASS; no test
    reads the committed staging root.
- **The receipts:**
  - the local suite gives 29 tests OK and 43/43 mutants killed;
  - **cluster attempt 4 at #810's head** (`9f593aa5`, #811) is RUN PASS: 29 tests, C-ROO ok, none skipped;
  - the 303-file atime watch was unchanged, porcelain was 0/0, and a stat before and after the run showed the staging
    root absent (attempt 4's stat files). <!-- absence-ok: a measured stat of one path, recorded in #811, not a claim that a result is absent -->

  The ref_c2c1 tree at M equals attempt 4's.
- **The configuration:**
  - `replica_set.choice = "reuse"`, which is Q_R's S1_001..300 at rank 75 (C-DRAW PASS, #784);
  - `inputs.staging.root = /pscratch/sd/j/josephrb/ref-c2c1-20261106/stage`;
  - the RooUnfold library's full sha256 `0b34e1e39102b0dddc5923dad7f69e59c70cd6a2fcbcef07728b72cf2933fefd`, cited to
    #779's `listing.json:4334`.

## Rulings

1. **Step two is bound at M.** The code is frozen unless a control STOPs. The follow-up list (F1, the keyword `option=`
   gap; F2, the lib sha checked only by the connect) stays in the receipt and is not applied now.
2. **The cluster lane is `limitation-resolver`.** A fixed conditional sequence applies: each stage proceeds when the
   previous stage's PASS record is committed on main, and anything else stops and comes to the director. Each connect's
   sha256 and result are reported, without waiting for a go.
   1. **Staging, on a DTN:**
      - refuse if the staging root exists;
      - copy $CV and $MC from their CFS sources by O_NOATIME, and re-read each against 43f8cc16 and d40aea69;
      - stat the shared sources' atime before and after;
      - **print the real O_NOATIME evidence:** the flag value and platform, each source's owner, the digest through the
        noatime open, and the atimes.
   2. **The units:**
      - `er`, `c2_central` and `c1_central`;
      - `c2_replica:1..300` over Q_R;
      - `c1_replica` for its declared 50;
      - every unit at exactly 64 CPUs and OMP/MKL/OPENBLAS 64/1/1;
      - libRooUnfold copied and checked against its full sha by the connect (F2's interim);
      - `--time` as HH:MM:SS, with the TimeLimit check.
   3. **The read,** in a new read directory, under its guards.
   4. **The deletion of the staged copies,** with a B9-form ledger row.
3. **The price.** The cap is 12.5 CPU node-h, with no universe pass. C-DRAW used 0.18, and the reuse makes c2's replica
   side about 0. A projection above the cap stops and reports, and does not shrink the set.
4. **The COV2D fence holds:** no plain read of a COV2D input while a cov2d-* job runs.
5. **Unchanged:** binding 1's ruling 6 (paper wording through the PRD read and Joseph), §1.5's and §2.4's licences, and
   §5's "does not license".

Nothing is submitted, deposited or tagged.

## Director's ruling (2026-11-06): the cells step inserted before the read

limitation-resolver found that the read needs a committed cells file. `ref_c2c1_read.py read --cells F --cells-sha256 S`
refuses unless sha256(F) = S, but ruling 2's sequence had no step that makes F. The declaration (`:69`) wants the 205
reported cells "committed with its sha256 before the run and bound index by index".

**The sequence's stage 3 becomes two stages:**
- **3a, cells:** on a login node, at 0 node-h, from a fresh clean clone at M, run `ref_c2c1_read.py cells --out <new read
  dir>/cells.root`. It reads only the publication's precision ROOT file (a staged O_NOATIME copy) and no unit product. The
  receipt commits `cells.root` and its sha256, and the director merges it.
- **3b, the read:** gated on that cells file being on main, with `--cells-sha256` taken from it, in the same read
  directory.

**Why this satisfies the declaration's intent.** The cells are a deterministic rule applied to the publication alone:
the positive diagonal of `StatOnlyCovariance` on the 224-bin grid. write_cells reads no unit product, so no outcome of
the runs can reach them. Committing them with their sha before the read fixes them before any reading, which is what
"before the run" protects. This is recorded as the director's reading of `:69`.

Nothing is submitted, deposited or tagged.

## Director's ruling (2026-11-06): C-PUB's operand, after the 3b control STOP

**The STOP.** The read (3b) ran b162ba9a from main `fd4c572c` on login27 at 0 node-h and stopped on its own control:
- read.log says "STOP: failed controls ['C-PUB']; no reading was formed";
- the rc was 1, and no readout.json exists;
- STOP.json has sha256 `968e0f2a…` (receipt PR #838).

STOP.json holds controls only. Every other control passes: C-CELLS, C-IN, C-CV, C-REF, C-CPUS, C-SET, C-SIM and C-ROO.
read.stdout is one line of axis labels. The director read both.

**Why C-PUB failed.** The cause is the control's operand, not the code it checks.
- **What the control requires** (`REF-C2C1-DECLARATION.md:115`): "the comparison code, given E_R itself, reproduces
  465.4153 over 205 bins to 1e-8 relative (`tension_report.txt:14`)".
- **What the bound config holds:** `2d-unfolding/ref_c2c1/config.json` (blob `96dbbaa2`) has `"chi2": 465.4153,
  "rtol": 1e-8`, a number printed to four decimals. Rounding to four decimals alone allows an error of up to
  5×10⁻⁵, which is 1.07×10⁻⁷ relative. So the control could pass only by chance.
- **What the read computed:** χ² = 465.4152721915331 over ndf 205. That is 6.0×10⁻⁸ from the rounded constant.
- **The same quantity at full precision** is committed in
  `state/2d-closeout/stageF/methods/re2/run/partc_r2/partc-r2/receipts/receipt_model_chi2.json:190` @ `3c2c3c0c`
  (`results.ours_vs_data.chi2` = 465.41527219152636, ndf 205). It is for the same E_R (sha256 `a5c13fc3…`) and the same
  published covariance (`6c6dce72…`) that the read staged. Its own `tension_report.txt:14` prints that value as 465.4153.
- The read agrees with it to **1.4×10⁻¹⁴ relative**.
- **The declaration's citation is ambiguous.** `tension_report.txt:14` names no path. The file
  `2d-unfolding/tension_report.txt:14` prints 750.4928, which belongs to a different result. The intended file is
  the part C r2 receipt's copy.

**Rulings.**
1. **The classification: a defect in a control's operand.** The checked code is not at fault.
   - It isn't a reading. No reading was formed, and nobody has seen one.
     <!-- absence-ok: the read's own STOP record states no reading was formed; this scopes the ruling, not a result -->
   - Binding 2 ruling 1 ("frozen unless a control STOPs") permits this change.
2. **The fix is the full-precision operand at the unchanged tolerance.** The tolerance is not loosened.
   - `config.json`'s `c_pub.chi2` becomes 465.41527219152636, with `rtol` staying 1e-8.
   - It gains a `source` field: the receipt path, `:190`, commit `3c2c3c0c`, the E_R sha and the covariance sha.
   - The read also checks that the staged E_R and covariance shas equal that source's. On a mismatch it refuses.
3. **The precision rule goes into code.** A test fails if any control's reference constant carries a rounding
   uncertainty larger than its rtol/10. Run it over every constant in `config.json`, not only C-PUB's, and report
   any other constant it flags before the audit.
4. **Scope of the change.** The code PR changes only `config.json` and the read's source check, plus the new test and
   the harness:
   - the harness's REQUIRED mutant "C-PUB's tolerance loosened" must still be killed;
   - add a mutant that restores the rounded constant, which must also be killed.

   The lane shows that no unit code path reads `c_pub`, so the 350 replica units and the three centrals stand on
   their DONE records at `77d76cfc`.
5. **The order of steps:**
   1. the lane's code PR;
   2. coverage-5b-audit's audit of that delta;
   3. the director binds the new M in a section of this file;
   4. 3b re-runs at 0 node-h, from main's bytes, re-hashed on login, with the read connect re-hashed for the new M
      if it embeds M;
   5. the receipt.

   The staged copies stay until the read PASSes: stage 4's deletion waits.
6. **Unchanged:** the readings, bars and licences (§§1.5, 2.4 and 5), the cap and the spend. The spend stays at
   11.0587 of 12.5 node-h, and the re-read adds 0.

Nothing is submitted, deposited or tagged.

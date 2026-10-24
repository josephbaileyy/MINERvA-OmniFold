# C_model,5D build declaration (2026-10-24, session "2d test")

**Status: for the director's binding.** The builder has not been run on any unfold product. Once the director binds
this, it runs once, exactly as §2 gives it, on a Perlmutter login node at 0 node-h.
<!-- absence-ok: checked 2026-10-24: the run directory /pscratch/sd/j/josephrb/cmodel5d-20261024 does not exist, and this session ran the builder only inside test_cmodel5d's synthetic tree -->

**What it builds.** C_model,5D on the 16 H2 reporting cells:
- the construction is `H2-DEFINITION-DECLARATION.md` §3, approved in
  `DECISION-20261024-joseph-h2-16-cell-definition.md`;
- GiBUU's domain is option (i) of `H2-DEFINITION-ADDENDUM-GIBUU-DOMAIN.md` (PR #336).

## 1. Code

- **Code commit:** `dfcbb2c6c1dcb3211b7c6c8c364a6c1f9f171a47`.
- **Builder:** `nd-unfolding/pv-ladder/build_cmodel5d.py`, sha256
  `aaa81575b211f50e007fa75d318fd8d4f48bfb98ac5ae62b398dbf33db37d4ca`.
- **Tests:** `nd-unfolding/pv-ladder/test_cmodel5d.py`, sha256
  `aee4984f777109af0cc21bd5d9a1e5bd3f4d5b62c4a469aefba58dd6879dea89`.
  - 23 tests run on a synthetic tree. Each guard has a case where it fires, checked by its refusal message, and a case
    where it stays silent.
  - No test reads an unfold product.
- **Code it imports, unchanged.** The builder records each file's sha256 in its output:
  - `2d-unfolding/pv2d/cmodel/build_cmodel.py` `caba2265…7eae`: `cmodel`, `absolute`, `matrix_sha256`, `quantiles`;
  - `2d-unfolding/pv2d/pv2d_lib.py` `03aedc97…9abb`: `rel_shift`, `nominal_control`, `positive_control`, `envelope`;
  - `nd-unfolding/pv-ladder/pvl_analyze.py` `cca3a82f…46bc`: `check_meta`, `tasks`;
  - `nd-unfolding/pv-ladder/pvl_lib.py` `f8a7d2c2…5481`;
  - `nd-unfolding/s5p_stage1_inspect.py` `26569afc…3d71`.
- **Committed inputs it reads:**
  - `readouts/h2_definition.json` `b6790761…da89`;
  - `state/s5p/stage1/stage1_inspect.json` `def4c67c…1d9d`;
  - `config.json` `078df3b6…8310`;
  - `tasks.tsv` `4cebbc99…fdc3`;
  - `prep-SHA256SUMS` `29ac6b7c…8403`.

### What the builder refuses on, writing nothing

- a definition sha256 other than `b6790761…`, an expanded fine map other than `930326a3…`, or a Stage-1 receipt other
  than `def4c67c…`;
- any of the six products whose sha256 differs from its declared one (`H2-DEFINITION-DECLARATION.md` §4), or whose
  provenance fails the ladder's own `pvl_analyze.check_meta`:
  - rung, arm, closure, inputs, ratio sha256, features, seed, iterations, threads;
  - for the data products, the refinement and the prior guards;
  - the same code and estimator parameters across the products;
- a P5 sha256 other than `e36f3b25…`;
- an NC that is not bitwise:
  - (a) `L-5D-PV_e_tune_v1` against P5 on the full grid;
  - (b) the same on the 16 cell integrals;
  - (c) the cell integrals by `pvl_lib.integrated` against those by `s5p_stage1_inspect.fine_volume`;
- C_model that is not SᵀS, or h that is not max_k |s_k|;
- an output path that already exists.

### What it labels, without stopping

- **The PC at NuWro:** graded on the 27 base H2 cells under the unchanged rule. A verdict other than PASS labels the
  product "not evidence". The 16-cell readout is labelled "not powered".
- **The other labels:** the component label, the unvalidated-coverage limitation, the GiBUU label (p_∥ < 10 GeV/c,
  the 6–10 E_ν deficit, and the paper's narrower 6), and the step-adjacent caveat.

## 2. The run

**Deploy.** A partial clone at the code commit, as for the ladder (`RUN.md` §3, line 87–88):

```
R=/pscratch/sd/j/josephrb/cmodel5d-20261024
git clone --filter=blob:none https://github.com/josephbaileyy/MINERvA-OmniFold $R/repo
git -C $R/repo checkout --detach dfcbb2c6c1dcb3211b7c6c8c364a6c1f9f171a47
test "$(git -C $R/repo rev-parse HEAD)" = dfcbb2c6c1dcb3211b7c6c8c364a6c1f9f171a47
test -z "$(git -C $R/repo status --porcelain)"
mkdir $R/out
```

**Tests, then the build, on the login node.** This uses `source /pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh`
(Python 3.11). The argv is exact:

```
cd $R/repo/nd-unfolding/pv-ladder
python -W ignore -m unittest test_cmodel5d test_pvl
python build_cmodel5d.py \
    --products /pscratch/sd/j/josephrb/pv-ladder-20261024/products \
    --p5 /pscratch/sd/j/josephrb/methods-paper/re1-20261022/out/5d/k1_p5_rerun.npz \
    --out-json $R/out/cmodel_5d.json \
    --out-npz $R/out/cmodel_5d.npz
```

**The run happens once.**
- If a test fails or the builder refuses, nothing is retried. I report to the director.
- On success, `cmodel_5d.json` is committed as `nd-unfolding/pv-ladder/readouts/cmodel_5d.json`, with a short
  report. The npz stays on pscratch, recorded by its file and matrix sha256.

**Cost:** 0 node-h. It is numpy on six files of about 0.1–0.2 MB and P5, in seconds.

## 3. Order and reads

- This is the first H2-level computation from an (e) data product in this pipeline. It follows Joseph's approval of
  the cells and the director's binding of this declaration, as the ruling on item 2 requires
  (`H2-DEFINITION-DECLARATION.md` §0, §3.5).
- **Nothing is summed with S1's covariance here.** That waits for S1's covariance on the same 16 cells.

**MEASURES:** nothing yet; this declares a build. **CANNOT AUTHORIZE:** the run, which is the director's binding, or
any claim.

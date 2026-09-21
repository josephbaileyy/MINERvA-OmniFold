Independent C5/C7 verification — 2026-09-20 (America/Los_Angeles; measurements continued on 2026-09-21 UTC)

The C5 claim is VERIFIED at its explicitly ruled scope: the guarded assembly's 15 repository modules at fb9ec356 and its eight declared source paths. This is NOT a proof of the input products' complete ancestry. C7's inventory, endpoint, migration-policy, component, assembly, inflation and numerical-PSD checks reproduce. PM-1 is accepted by Joseph's September 19 decision with its historical-input provenance limitation; it has not become an independently measured historical tuple binding.

I do not certify publication readiness. I found two concrete wording defects, including an unsupported lower-bound claim already in the paper and analysis note. They require correction before publication. Neither finding establishes a numerical defect in the audited Z covariance, and this audit does not withdraw Joseph's adoption.

I am the Codex reviewer in this session. I authored none of the pre-existing C5/C7 evidence and do not own cause 5. The measurements and judgments below are my own. I did not inherit a C5 verdict from VL66, count the owning lane's assertion as outside corroboration, or manufacture four MET grades. This record supplies third-lane verification of these two rows only; it does not independently certify every other requirement of §6.4 clause (c), or make verification have preceded the adoption.

The user-authorized scope is PROMPT.md in /Users/josephbailey/local-research/mnv-c5c7-review-20260920. Governing documents were read at repository HEAD c34553e50661bd8bd254d79033fce077802e79b3. Historical executable code was read with git show --no-ext-diff fb9ec3560fd6d62295dffc81b5694c9e26667d5b:<path>, without checkout.

The requested fresh clone was absent: the review directory contained only PROMPT.md and RUN.sh. RUN.sh would delete/create a clone and write several additional files, contrary to PROMPT.md's one-write rule. I did not execute it. I used the existing repository's object database read-only, with pinned revisions, and report this procedural deviation explicitly. Fresh-clone isolation was not achieved. The existing checkout's HEAD and eight pre-existing untracked paths were unchanged in before/after status checks. No repository source, receipt, scientific product or NERSC file was written; no job was submitted; no environment was installed or changed. This verdict is the sole intentional file write.

The governing record is more recent than PROMPT.md's presentation of the September 18 table. DECISION-20260919-joseph-rules-pm1-cause7-and-completion.md expressly amends PM-1's evidence requirement. DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md adopts the exact CV digest as publication-under-exception. The product's own NON-PASSING/adoptable:false metadata is deliberately preserved, and is not evidence that this later adoption does not exist. DISCLOSURE-20260920-clause-c-verification-blocked-and-was-not-recorded.md identifies the independence problem motivating this review. I preserve these distinctions.

Publication findings, in priority order:

1. P1 — The fixed-band seed-sensitivity measurement is not proved to be a lower bound.

   Locations at c34553e5: docs/analysis-note/paper_body.tex:170–173; docs/analysis-note/sec_eavailw.tex:249–253; docs/analysis-note/values.tex:343; docs/orchestration/DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md:73–77.

   These texts infer a lower bound because five bands were held at a fixed seed; the adoption record says allowing them to vary “could only add.” That does not follow. The implemented statistic, nd-unfolding/z_statistics.py:s_proj, is the maximum relative change of sqrt(u^T C u), not a sum of nonnegative magnitudes of component changes. Positive semidefinite covariance components can change in opposite directions between seeds.

   A one-dimensional counterexample uses only positive covariance components. At the baseline, V0=1 and L0=1, so C0=2. With the lateral block held fixed, V1=1.2 and L1=1 give C1=2.2 and s_proj=4.880884817015151%. If that lateral block instead changes to L1=0.8, the total is C1=2 and s_proj=0. Thus allowing a previously fixed component to vary can REDUCE the measured movement. This is a mathematical counterexample to the inference, not a new measurement of this analysis.

   Preserve the measured seed effect and the fixed-band limitation. Replace the lower-bound claim with: “The seed variation does not probe the seed sensitivity of the five fixed-seed lateral bands; its effect on the total covariance when those bands also vary has not been measured.” Appending samples to a maximum of the SAME statistic cannot lower the maximum; changing which covariance components vary changes the statistic's operands and does not have that monotonicity guarantee. No new campaign is required to correct this wording. Any eventual deliverable edit must follow the note/primer/paper and standalone-repository synchronization requirements; no such edits or builds were performed in this read-only audit.

2. P2 — C7's final operative summary drops the top-1%-of-bins qualifier.

   Location at c34553e5: docs/orchestration/OPERATIVE-SHEET-scalar5d.md:709–710. It states that the per-bin ratios run 0.687–1.153. In §4g of that same document, line 578, this is explicitly the range for the TOP 1% OF BINS BY SUPPORT VARIANCE.

   Reading the five support and five active matrices themselves, I obtain extrema of sqrt(diag(L_active)/diag(L_support)) of 0.17724803760759691 and 3.0619466845725776 on positive-support-variance bins. This reproduces §4g's full-range observation and contradicts §4i's unqualified narrower range. The aggregate lateral sqrt-trace change independently reproduces as -0.02877337862288165%. It bounds neither the per-bin effect nor the full covariance effect.

   Correct the final summary to give the full range, with 0.687–1.153 explicitly labeled as the top-1% subset if retained. Low aggregate variance does not make an individual quoted bin irrelevant. The full-range measurement is consistent with the existing detailed evidence; the defect is the dropped qualifier in its final summary.

C5: what was measured, and what the negative finding means.

SPEC §6.1's falsifier is a PET-derived product consumed by a module on Z's construction path. A path containing no “PET” token is not by itself proof of non-PET ancestry. My scoped result is NOT FALSIFIED on the assembly-child import closure and bound source paths, exactly preserving the September 18 ruling's producer-chain residual.

I reconstructed the eager repository import graph from the pinned Python AST, starting at z_build.py and including the propagated guard/shim, then inspected the function-level imports and file reads reached by the actual NPZ build. I compared every recorded module SHA-256 against the Git blob. All 15 match, with no missing repository module identified on that assembly path. A scan that follows every function-local import in every unused helper finds additional training/producer modules; that is not the executed assembly import closure. Conversely, the pilot wrapper and upstream producer processes are not magically included in a child process's sys.modules receipt. “15” is the guarded assembly's repository-module count, not the number of modules in the entire historical pipeline or Python environment.

Every row below is NOT FALSIFIED for direct PET-product consumption on the inspected assembly path:

| Pinned module under nd-unfolding/ | Inspected assembly role / reason |
|---|---|
| adopt_unified_5d.py | Imported by z_contract.py:98 for VERT_BANDS. Its main() is not executed by this NPZ assembly. I read the complete module, including defaults, ROOT reads and writes. No PET operand was found. |
| compare_unified_throw.py | Imported through unified_throw_cov; training/dump helpers are not called by the assembly. |
| flux_universe.py | Imported through unified_throw_cov; its flux-reader helpers are not called by the assembly. |
| mnv_guard_shim/sitecustomize.py | Loads and installs the import guard; no physics covariance input is supplied by it. |
| mnv_guarded_run.py | Controls imports/launches and code provenance; no PET physics operand was found on this path. PET references in comments/examples are not consumption. |
| p4_lib.py | Supplies the five-band constants and component-sum checks over already supplied arrays. |
| seed_offset_policy.py | Imported through unified_throw_cov; producer/seed-scanning helpers are not invoked here. |
| unified_throw_cov.py | Supplies _atomic_savez to the assembly/receipt writers; the training/throw-producing entry point is not run. |
| uq_math.py | Numerical functions/constants, with no PET input opened on this path. |
| z_assembly.py | Inflation and covariance algebra/gates over the supplied arrays. |
| z_build.py | Reads the manifest and its eight named sources via Source; the actual source keys and bound bytes were inspected. |
| z_contract.py | Imports scalar constants and policy; contains the adopt_unified_5d sys.path restoration. |
| z_receipt.py | Hashing, null-operand reading, receipt/product persistence and validation; its input reads follow the declared paths. |
| z_statistics.py | Support, null and other numerical calculations on passed arrays. |
| z_validator.py | Assessment/criteria code; no additional PET product is introduced. |

adopt_unified_5d.py's measured Git-blob SHA-256 is e1260e8dec2d39cb4653a8b4b02a198d04ea103d548a2d90b5f003f0b8044c35, exactly the product/receipt's recorded value. It is genuinely in the closure and was covered by this review. The pinned module does insert the hardcoded data root into sys.path; z_contract.py:97–100 saves and restores the prior list around its import. The adopted numerical D_Z is calculated in z_assembly.py from the inputs; importing adopt_unified_5d for its constants should not be described as executing its main() producer.

All eight manifest files were directly opened and fully hashed. All SHA-256 values match; size, inode and mtime were stable across each hashing pass. The parent file is opened as opaque and hashed for provenance, not used as a covariance budget block.

| Role | Path relative to the cluster nd-unfolding/ directory | Measured SHA-256 |
|---|---|---|
| active | active_universe_5d/standard/candidate/std_final5_candidate.root | 950f8cb15c5a0bd785d65e7f85f4cb40fa86e27383973f82ef15c7ef525c1263 |
| central | products/5d/xsec_5d_MEFHC_5iter_lgbm.root | 630306e20e4e175bde8b459174842a58e4f4b5a694b8a5018e730a952820aec8 |
| ml | uq_cov_mlsplit_5d.root | 27b2e456f80e15d8a5c4da1bcd3b01a201b80385341af68614c85b6b7f8f5374 |
| null | uq_5d/z_pilot_20260916_a5/z-null-source.npz | 2ac9d087ad307e097f57269ee0f9780f3b7a49e5bdb3402592ea5a353681b570 |
| parent | uq_5d/readopt_20260811_footing/stamped_bkgaware_meancentered_20260812.root | 4f168e83eaeb4bc7191a4e13e219c7ff06556e5ad30b9df4fcc249e6720c7ec2 |
| stat | uq_cov_stat_5d.root | 6580016fa7136e6f98867707f4d48557350b26a91773d0c300be20113c2c6934 |
| support | uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware.root | 9f7b2f55d7581bb687e214e7f5a38235fd07b6d9522c2223fa3a3395c803c92a |
| throw | uq_5d/z_precursor_20260914/unified_throw_cov_5d.root | 09a029ed2a7de0ffd144b1ad0ad8d3e0bf8e8b9788797b0af58693c753795560 |

The cluster directory above is /pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding. I did NOT exhaustively trace these products' producer chains. Their scalar filenames, successful hashes and matching arrays do not prove absence of indirectly PET-derived ancestry. That is the accepted residual, not a purported missing sixteenth assembly module. G's and Y's historical dispositions are untouched. No VL66 conclusion supplies this re-trace.

C7: measured construction and migration checks.

The direct key listing of G's support covariance contains 45 unique per-band keys, with no duplicate cycles observed. The five support keys hCov_universe5d_<band> and the five active donor keys hCov_active5d_<band> have exactly these bands:

BeamAngleX, BeamAngleY, MuonResolution, Muon_Energy_MINERvA, Muon_Energy_MINOS.

All ten matrices are 10694 by 10694 and finite. The donor's hRowIndex5D equals Z's row vector exactly. Z's row vector is exactly flatnonzero(central > 0), and its persisted central and support mask equal the declared production central and derived predicate. All ten unfolded endpoints have 65856 grid cells, the same positive support mask and identical physical edges for pt, pz, eavail, q3 and W.

The V set is exactly the 13 imported VERT_BANDS. R contains 27 bands, including MinosEfficiency, GEANT_Neutron, GEANT_Pion and GEANT_Proton. V/R/A are disjoint and exhaust the measured inventory. The actual key list agrees with the receipt and provenance records. “Measured twice, two files” is not two independent physical origins: z_pilot._component_provenance and z_build both obtain the inventory from the support file's keys. This review independently reads that original support file; it does not treat agreement between those two records as separate corroborating provenance.

I opened the ten standard-path unfolded endpoint ROOTs and their corresponding merged ROOTs, not a prepared extraction bundle. Each unfolded endpoint SHA-256 matches p4_standard_manifest.json; all ten hashes are distinct. The merged products stamp the correct band and endpoint index. The actual stored migration counters are:

| Band | Endpoint | Truth entrants / exits | Reco entrants / exits | Migration total | Declared policy |
|---|---:|---|---|---:|---|
| BeamAngleX | 0 | 0 / 0 | 2731 / 2061 | 4792 | NONZERO |
| BeamAngleX | 1 | 0 / 0 | 1936 / 2764 | 4700 | NONZERO |
| BeamAngleY | 0 | 0 / 0 | 2513 / 2294 | 4807 | NONZERO |
| BeamAngleY | 1 | 0 / 0 | 2241 / 2567 | 4808 | NONZERO |
| MuonResolution | 0 | 0 / 0 | 0 / 0 | 0 | ZERO |
| MuonResolution | 1 | 0 / 0 | 0 / 0 | 0 | ZERO |
| Muon_Energy_MINERvA | 0 | 0 / 0 | 0 / 0 | 0 | ZERO |
| Muon_Energy_MINERvA | 1 | 0 / 0 | 0 / 0 | 0 | ZERO |
| Muon_Energy_MINOS | 0 | 0 / 0 | 0 / 0 | 0 | ZERO |
| Muon_Energy_MINOS | 1 | 0 / 0 | 0 / 0 | 0 | ZERO |

The policies are p4_lib.py:64–65. I executed the migration-check AST from fb9ec356:p4_validate_active_lateral.py in isolation, with in-memory records and no production I/O. The valid control passes; changing MuonResolution_0 to nonzero is refused; changing BeamAngleX_0 to zero is refused. Inspection of the surrounding production function shows P4GateError produces FAIL and exit 1, not a warning followed by PASS. The evidence generator likewise publishes failed evidence under failed names and exits nonzero. This is an isolated check of the actual predicate, not a claim that I ran the complete historical launcher.

No actual missing, extra, duplicated, one-sided, wrong-grid or migration-policy-contradicting active band was found. The legacy assembly itself does not open the ten merged endpoints or enforce their migration policies: it consumes donated matrices. The upstream policy enforcement and this endpoint-to-matrix check must remain part of the evidence chain; G5 alone does not establish them.

There is a real historical G5 limitation, already documented in the current operative sheet. At fb9ec356, replacing GEANT_Proton with an invented residual name in the inventory, then deriving R as the production caller does, still returns exhaustive:true and 13/27/5. Missing, extra or duplicate A entries are refused, but a one-for-one residual substitution survives. The implementation is in z_contract.check_band_partition, re-exported through z_assembly. At c34553e5, z_contract.check_declared_residual and the real-input call at z_build.py:661–662 reject that substitution; an isolated current-function check reproduced the refusal. This repair is not retroactive evidence about the old guard. The existing product is supported by its now directly verified exact inventory, not by asserting that the old flag could detect every wrong inventory.

Independent numerical results follow. Relative matrix residuals use max(abs(observed - expected))/max(abs(expected)); no absolute unit floor, eigenvalue clipping or covariance regularization was used.

| Check | Measured result |
|---|---|
| Active endpoint-pair MAT covariance vs persisted band, BeamAngleX | 1.0289318324284707e-16 |
| Same, BeamAngleY | 1.250359910181176e-16 |
| Same, MuonResolution | 1.4927702766095883e-16 |
| Same, Muon_Energy_MINERvA | 1.7368610265063507e-16 |
| Same, Muon_Energy_MINOS | 1.4222343734796268e-16 |
| Active total vs sum of the five bands | 0.0 |
| CV-centered assembly from V/R/A/stat/ML and measured g | 2.1641333629718977e-16 |
| Mean-centered assembly | 2.185506664684276e-16 |
| CV inflation-difference identity | 4.1905478005775325e-16 |
| Mean inflation-difference identity | 3.770256018837015e-16 |
| Each g independently reconstructed from the throw's raw diagonals and shift | 0.0 maximum relative difference, both variants |
| CV covariance de-inflated vs donor's independently stored full block sum | 5.472945186844503e-16 |
| Donor block sum vs stored systematic + separately read stat + ML | 0.0 |

The 40 consumed V/R component-array digests, five active component digests, active-total digest, stat and ML digests all match the Z receipt. The five removed support lateral matrices are not listed as consumed objects in that receipt; I read them directly for the counterfactual and the entire support file was independently hashed. All three raw throw-operand digests match.

The separately stored donor block sum is an independent operand, not a field copied from Z's receipt. Its full-matrix agreement with the de-inflated Z is 5.47e-16 in maximum-entry relative error. For n=10694, the elementary spectral-norm bound n times that error is about 5.9e-12 of the donor's maximum-entry scale, also below the 1e-9 PSD allowance relative to its maximum eigenvalue. I have identified the object actually diagonalized instead of claiming a second eigensolve on an unpersisted Z block sum.

The block sum's sqrt-trace is 4.357646830695704e-38. For the CV variant, g is finite, minimum 1, maximum 17.653141714565614, with 6528 bins greater than 1; for mean, the maximum is 17.467609558724217 with 2807 bins greater than 1. There are no zero block-variance denominators in these products; the persisted pinned masks agree. Reconstructing both variants explicitly includes the mean-shift-squared term only for CV.

I repeated the dense eigensolves on the symmetrized matrices with scipy.linalg.eigh(eigvals_only=True, driver="evr"), limited to one BLAS thread. The tiny negative eigenvalues depend on arithmetic implementation; every measured negative fraction is many orders below the specified relative 1e-9 tolerance.

| Object | Minimum eigenvalue | Maximum eigenvalue | max(0,-minimum)/maximum |
|---|---:|---:|---:|
| z-cv.npz | -1.6306079908811896e-90 | 2.2292239987529526e-75 | 7.314688841468448e-16 |
| z-mean.npz | -1.4368777308489063e-90 | 1.9272637183054818e-75 | 7.455532510684421e-16 |
| Donor's full block sum, identity-linked above to Z's de-inflated block sum | -8.01748605433934e-91 | 1.2059705548627535e-75 | 6.64816070509431e-16 |

Measured symmetry residuals are 2.1641333629718972e-16 for CV and 1.0927533323421377e-16 for mean. Both arrays are finite. The resulting sqrt-traces are 5.674200780785609e-38 (CV) and 5.269506434664456e-38 (mean).

The lateral counterfactual uses only the five active and five support-limited lateral components bound into this audit, not C_Z - C_G and not S's whole total as a substitute for Z. I measure sqrt-trace 1.4742855148740122e-38 for active and 1.474709838719496e-38 for support, ratio 0.9997122662137712. Agreement with S is expected because Z uses those donor components; it is not independent physical corroboration.

PM-1 has an explicit boundary.

I read G's own ROOT combined_source stamp: uq_universe_5d_covariance_combined_bkgaware.root. I opened that original support ROOT and verified its full 9f7b2f55... digest. Its key inventory holds the four retained bands, but it has no per-band migration counters or historical event-tuple binding. Presence in R establishes retention, not weight-only behavior or complete detector-response uncertainty coverage.

The inspected implementation routes kinematic branches through !IsVerticalOnly() in runEventLoopOmniFold.cpp:351 and branch-presence checks in unfold_nd_omnifold_unbinned.py:388. The comment at the former's lines 238–244 expresses intent; it is not executable verification. The previously reported 470-branch tuple has no recorded path/digest in the cited packet, so I could not reach it as an identified historical operand and did not re-measure it. I did not repair its provenance by choosing a plausible tuple.

Under the unamended SPEC wording, empirical clearing of PM-1 on G's historical tuple is NOT established by this review. Under the operative September 19 ruling, the correct disposition is exactly: “PM-1: accepted by decision, with historical-input provenance limitation.” The accepted gap is not a new blocker or a demand for another reconstruction campaign. C7's measured construction/migration evidence is consistent with closure under that amended contract, subject to correcting the false per-bin summary above. This is not blanket validation of the hadronic-response model.

Artifact identities and limits.

| File in uq_5d/z_pilot_20260916_a5/ | Bytes | Measured SHA-256 |
|---|---:|---|
| z-cv.npz | 890500272 | 3d7465f66fbe66b0dfcf09b6fc51249f227fb33e97ae40bc78dda90275e918c5 |
| z-mean.npz | 890383062 | 61b7a4939bd40459452e232d4a5cec3c0b19ad7a21715452f7bb3bc9e0c72dd2 |
| z-receipt-cv.json | 37568 | 9f8f91d9be69d76755e9e89828e2d4631250afb08ce2892ce7378b936336c531 |
| z-manifest.json | 2490 | 44ab73bae181ef222ef8b6aca9450780982b3dfc5feed2967102e694f3b4c080 |
| z-provenance.json | 5577 | d96926fd4ddd31c3d1a50cfedad71c8db940f70e5e467c738c2a1faf5149a465 |


The small P4 records read on the cluster also match the committed c34553e5 blobs byte for byte:

| Record under nd-unfolding/ | SHA-256 |
|---|---|
| active_universe_5d/standard/evidence/p4_standard_manifest.json | 71aace382e8b0450a9099904678bedef132e1a757b1401d8459a74923707bea3 |
| active_universe_5d/standard/evidence/p4_merged_audit.json | 2e3fac26b29c7d29dd19cc82ce65983f45ef677f6c36064dd41bb97c0a12bf9e |
| active_universe_5d/standard/candidate/std_component_manifest.json | 269232245870632884d6e589ac8d7aa9ba7fb4e07d0860e077cbd98fe6de04b5 |

The CV product itself reports variant cv, assembling revision fb9ec3560fd6d62295dffc81b5694c9e26667d5b, NON-PASSING and adoptable:false. These do not turn into measured PASS labels merely because of the external adoption decision.

Unreached or deliberately unmeasured items are named rather than assigned zero: the requested fresh clone was absent; the unidentified historical PM-1 tuple and its link to G were not reached; full producer ancestry was not traced; merged event trees were not reprocessed to independently count event crossings; the approximately 538 GB of merged event files were not fully rehashed; twelve-playlist hadd coverage was not established by reading the migration stamps. Reading those persisted counters is a direct product read, not a recount from raw events. All named assembly products and all ten named endpoint/merged ROOTs were reachable. No source-read failure was converted into an empty inventory or a passing zero census.

The default /usr/bin/python3.11 on the cluster had no NumPy, uproot or ROOT. I found and used the existing /global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python environment, NumPy 2.2.6 and uproot 5.6.9. No PyROOT/TensorFlow mixed import, environment installation, production CLI, sbatch, srun or salloc was used. Scripts ran from stdin with Python -B and disabled uproot object/array caches, read original products with uproot.open and numpy.load(allow_pickle=False), and retained calculations only in memory.

This audit did not repeat the central-value campaigns, grade cause 3, audit every adoption measurement, build publication documents, verify all projections, or synchronize/push either repository. Those tasks cannot be inferred complete from these two rows. The published-paper lower-bound wording and the C7 summary qualifier are concrete remaining corrections identified here.

Reproduction commands and probe bodies.

Local code was read using git show --no-ext-diff at the pinned historical revision; module identities were computed with hashlib.sha256 over those blob bytes and compared against code_identity.import_closure_digests read directly from z-receipt-cv.json. The eager closure probe recursively followed AST Import/ImportFrom nodes outside function bodies, then the reached function-local paths were inspected separately. The counterexample and gate mutations described above ran in local Python -B using AST-extracted predicates, without importing production entry points.

For each of the following remote probe bodies, the command was:

```sh
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o UpdateHostKeys=no \
  -o ControlMaster=no -o ControlPath=none saul.nersc.gov \
  'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 /global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python -B -u -' <<'PY'
# Insert the corresponding body below.
PY
```

The file-hashing-only body also ran with /usr/bin/python3.11 -B -u -, since it has no numerical dependencies. Commands do not create output files. These are the actual independent probe bodies used; their read paths, numerical formulas and comparison scopes are explicit.

Probe A: full source-file hashes.

```python
import json,hashlib,os
from pathlib import Path
p=Path('/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/uq_5d/z_pilot_20260916_a5')
d=json.loads((p/'z-manifest.json').read_text())
for role,s in d['sources'].items():
 q=Path(s['path']);before=q.stat();h=hashlib.sha256()
 with q.open('rb') as f:
  while b:=f.read(8*1024*1024): h.update(b)
 after=q.stat();digest=h.hexdigest()
 print(role,before.st_size,digest,'matches',digest==s['sha256'],'unchanged_during_hash',(before.st_size,before.st_mtime_ns,before.st_ino)==(after.st_size,after.st_mtime_ns,after.st_ino),flush=True)
```

Probe B: original product inventories, support/grid identities, endpoint hashes and merged migration counters.

```python
import json,hashlib,collections
from pathlib import Path
import numpy as np,uproot
p=Path('/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding')
base=p/'uq_5d/z_pilot_20260916_a5'
m=json.loads((base/'z-manifest.json').read_text())
r=json.loads((base/'z-receipt-cv.json').read_text())
a=('BeamAngleX','BeamAngleY','MuonResolution','Muon_Energy_MINERvA','Muon_Energy_MINOS')
def op(path): return uproot.open(path,object_cache=None,array_cache=None,num_workers=1)
def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  while b:=f.read(8*1024*1024): h.update(b)
 return h.hexdigest()
with np.load(base/'z-cv.npz',allow_pickle=False) as z:
 rows=z['hRowIndex5D']; central=z['hXSecND_flat']; mask=z['hSupportMask'].astype(bool)
 print('Z_SUPPORT',np.array_equal(rows,np.flatnonzero(central>0)),np.array_equal(mask,central>0),len(rows),flush=True)
with op(m['sources']['central']['path']) as f:
 x=f['hXSecND_flat'].values(); axes=[f['hXSec_'+s].axis().edges() for s in ['pt','pz','eavail','q3','W']]
 print('Z_CENTRAL_EXACT',np.array_equal(x,central),flush=True)
with op(m['sources']['support']['path']) as f:
 keys=f.keys(cycle=True); names=[k.rsplit(';',1)[0] for k in keys]
 inv=[k[len('hCov_universe5d_'):] for k in names if k.startswith('hCov_universe5d_') and k!='hCov_universe5d_total']
 v=r['inflation']['membership']['bands_vert']; residual=sorted(set(inv)-set(v)-set(a))
 print('SUPPORT_INVENTORY',len(inv),len(set(inv)),sorted(inv),flush=True)
 print('PARTITION',len(v),len(residual),len(a),not(set(v)&set(a)),all(w in residual for w in ['MinosEfficiency','GEANT_Neutron','GEANT_Pion','GEANT_Proton']),flush=True)
 print('RECORDED_INVENTORY_EQUALS_BYTES',sorted(inv)==sorted(r['inflation']['membership']['band_inventory']),flush=True)
with op(m['sources']['active']['path']) as f:
 names=f.keys(cycle=False)
 observed=[k[len('hCov_active5d_'):] for k in names if k.startswith('hCov_active5d_') and k!='hCov_active5d_total']
 print('ACTIVE_INVENTORY',observed,sorted(observed)==sorted(a),flush=True)
 print('ACTIVE_ROWS_EXACT',np.array_equal(f['hRowIndex5D'].values(),rows),flush=True)
man=json.loads((p/'active_universe_5d/standard/evidence/p4_standard_manifest.json').read_text())
for b in a:
 for ep in (0,1):
  tag=f'{b}_{ep}'
  q=p/f'active_universe_5d/standard/unfolds/5d_xsec_MEFHC_5iter_lgbm_uni_full_{tag}.root'
  merged=p/f'active_universe_5d/standard/merged/runEventLoopOmniFold_5D_MEFHC_active_{tag}.root'
  try:
   digest=sha(q)
   with op(q) as f:
    xx=f['hXSecND_flat'].values()
    axes_ok=all(np.array_equal(f['hXSec_'+s].axis().edges(),e) for s,e in zip(['pt','pz','eavail','q3','W'],axes))
    print('ENDPOINT',tag,'sha256',digest,'matches_manifest',digest==man['endpoint_sha256'][tag],
          'n_grid',len(xx),'mask_equal',np.array_equal(xx>0,mask),'axes_equal',axes_ok,
          'globalCompleteness',f['globalCompleteness'].member('fVal'),flush=True)
   with op(merged) as f:
    census={k:f['activeUniverse'+k].member('fVal') for k in ['TruthEntrants','TruthExits','RecoEntrants','RecoExits']}
    def scalar(key):
     o=f[key]
     return o.member('fTitle') if o.classname=='TNamed' else o.member('fVal')
    total=sum(abs(v) for v in census.values()); expected_nonzero=b in ['BeamAngleX','BeamAngleY']
    print('MIGRATION',tag,'stamped_band',scalar('activeUniverseBand'),'stamped_endpoint',scalar('activeUniverseIndex'),
          'census',census,'total',total,'policy','NONZERO' if expected_nonzero else 'ZERO','policy_matches',(total>0)==expected_nonzero,flush=True)
  except Exception as e: print('UNREACHABLE_ENDPOINT',tag,str(q),str(merged),repr(e),flush=True)
print('DONE',flush=True)
```

Probe C: source components, endpoint MAT identities, inflation reconstruction and both total assemblies.

```python
import json,hashlib,time,gc
from pathlib import Path
import numpy as np,uproot
p=Path('/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding')
base=p/'uq_5d/z_pilot_20260916_a5'
m=json.loads((base/'z-manifest.json').read_text());r=json.loads((base/'z-receipt-cv.json').read_text())
V=('2p2h','CCQEPauliSupViaKF','FrAbs_pi','FrElas_N','HighQ2','LowQ2','MaCCQE','MaRES','MFP_N','MvRES','Rvn2pi','Rvp2pi','Flux')
A=('BeamAngleX','BeamAngleY','MuonResolution','Muon_Energy_MINERvA','Muon_Energy_MINOS')
def op(path): return uproot.open(path,object_cache=None,array_cache=None,num_workers=1)
def arrhash(a):
 a=np.ascontiguousarray(a,dtype=np.float64)
 h=hashlib.sha256(f'{a.dtype.str}|{a.shape}|'.encode());h.update(memoryview(a));return h.hexdigest()
def read(role,key):
 with op(m['sources'][role]['path']) as f: x=f[key].values().astype(np.float64)
 expected=r['notes']['inputs'][role]['objects'].get(key,{})
 print('READ',role,key,x.shape,'finite',bool(np.isfinite(x).all()),'hash_match',arrhash(x)==expected.get('sha256') if expected else 'not_recorded',flush=True)
 return x
def rel(x,y):
 worst=0.;scale=0.
 for i in range(0,len(x),128):
  worst=max(worst,float(np.max(np.abs(x[i:i+128]-y[i:i+128]))));scale=max(scale,float(np.max(np.abs(y[i:i+128]))))
 return worst/scale if scale else worst
def sym(x):
 worst=0.;scale=0.
 for i in range(0,len(x),128):
  worst=max(worst,float(np.max(np.abs(x[i:i+128]-x[:,i:i+128].T))));scale=max(scale,float(np.max(np.abs(x[i:i+128]))))
 return worst/scale
with np.load(base/'z-cv.npz',allow_pickle=False) as z: rows=z['hRowIndex5D'];n=len(rows)
sv=np.zeros((n,n));other=np.zeros_like(sv);lateral=np.zeros_like(sv);support_lateral_diag=np.zeros(n)
with op(m['sources']['support']['path']) as f:
 inv=sorted(k[len('hCov_universe5d_'):] for k in f.keys(cycle=False) if k.startswith('hCov_universe5d_') and k!='hCov_universe5d_total')
R=sorted(set(inv)-set(V)-set(A))
for b in V:
 c=read('support','hCov_universe5d_'+b);sv+=c;del c
for b in R:
 c=read('support','hCov_universe5d_'+b);other+=c;del c
for b in A:
 c=read('support','hCov_universe5d_'+b);support_lateral_diag+=np.diag(c);del c
for b in A:
 c=read('active','hCov_active5d_'+b);lateral+=c
 endpoints=[]
 for e in (0,1):
  with op(p/f'active_universe_5d/standard/unfolds/5d_xsec_MEFHC_5iter_lgbm_uni_full_{b}_{e}.root') as f: endpoints.append(f['hXSecND_flat'].values()[rows])
 mean=(endpoints[0]+endpoints[1])/2;d0=endpoints[0]-mean;d1=endpoints[1]-mean
 scale=float(np.max(np.abs(c)));err=0.
 for i in range(0,n,128):
  rebuilt=(d0[i:i+128,None]*d0[None,:]+d1[i:i+128,None]*d1[None,:])/2
  err=max(err,float(np.max(np.abs(c[i:i+128]-rebuilt))))
 print('ACTIVE_ENDPOINT_MAT_IDENTITY',b,err/scale,flush=True);del c
c=read('active','hCov_active5d_total');print('ACTIVE_TOTAL_EQ_SUM5',rel(c,lateral),flush=True);del c
ratio=np.sqrt(np.divide(np.diag(lateral),support_lateral_diag,out=np.ones(n),where=support_lateral_diag>0))
print('LATERAL_COUNTERFACTUAL','sqrttr_active',float(np.sqrt(np.trace(lateral))),'sqrttr_support',float(np.sqrt(support_lateral_diag.sum())),'relative_sqrttr',float(np.sqrt(np.trace(lateral)/support_lateral_diag.sum())-1),'perbin_ratio_minmax',float(ratio.min()),float(ratio.max()),flush=True)
other+=lateral;del lateral
for role,key in [('stat',m['stat_key']),('ml',m['ml_key'])]:
 c=read(role,key);other+=c;del c
print('BLOCKSUM','sqrttr',float(np.sqrt(np.trace(sv)+np.trace(other))),flush=True)
with op(m['sources']['throw']['path']) as f:
 raw={}
 for key in ['C_unified','C_blocksum']:
  obj=f[key];raw[key]=np.diag(obj.values()).astype(np.float64).copy();del obj;gc.collect()
 raw['hJointMeanShift']=f['hJointMeanShift'].values().astype(np.float64)
for key,receipt_key in [('C_unified','diag_c_unified_mean'),('C_blocksum','diag_c_blocksum'),('hJointMeanShift','joint_mean_shift')]:
 print('RAW_HASH',key,arrhash(raw[key])==r['inflation']['raw_operands'][receipt_key],flush=True)
vb=np.clip(raw['C_blocksum'],0,None);vm=np.clip(raw['C_unified'],0,None);ms=raw['hJointMeanShift']
for variant in ('cv','mean'):
 with np.load(base/f'z-{variant}.npz',allow_pickle=False) as z:
  g=z['hInflation_g'];pin=z['hPinnedMask'];c=z['hCov_combined5d_total_uthrow']
  vu=vm+ms**2 if variant=='cv' else vm
  expected=np.ones(n);ok=vb>0;expected[ok]=np.sqrt(np.maximum(vu[ok],vb[ok]))/np.sqrt(vb[ok])
  print('G_RECONSTRUCTION',variant,'max_rel',float(np.max(np.abs(g-expected)/expected)),'finite',bool(np.isfinite(g).all()),'minmax',float(g.min()),float(g.max()),'n_inflated',int((g>1).sum()),'pinned_correct',bool(np.array_equal(pin.astype(bool),~ok) and np.all(g[~ok]==1)),flush=True)
  err=0.;scale=0.;infl_err=0.;infl_scale=0.
  for i in range(0,n,128):
   rebuilt=g[i:i+128,None]*sv[i:i+128]*g[None,:]+other[i:i+128]
   delta=(g[i:i+128,None]*g[None,:]-1)*sv[i:i+128]
   observed=c[i:i+128]-(sv[i:i+128]+other[i:i+128])
   err=max(err,float(np.max(np.abs(c[i:i+128]-rebuilt))));scale=max(scale,float(np.max(np.abs(rebuilt))))
   infl_err=max(infl_err,float(np.max(np.abs(observed-delta))));infl_scale=max(infl_scale,float(np.max(np.abs(delta))))
  print('ASSEMBLY_IDENTITY',variant,err/scale,'INFLATION_DIFFERENCE_IDENTITY',infl_err/infl_scale,'SYMMETRY',sym(c),'FINITE',bool(np.isfinite(c).all()),'SQRTTR',float(np.sqrt(np.trace(c))),flush=True)
  del c
print('DONE_MATRIX_AUDIT_NO_EIGENSOLVE',flush=True)
```

Probe D: de-inflated Z vs stored donor block sum; donor systematic/stat/ML identity.

```python
import json
from pathlib import Path
import numpy as np,uproot
p=Path('/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding');base=p/'uq_5d/z_pilot_20260916_a5'
m=json.loads((base/'z-manifest.json').read_text())
V=('2p2h','CCQEPauliSupViaKF','FrAbs_pi','FrElas_N','HighQ2','LowQ2','MaCCQE','MaRES','MFP_N','MvRES','Rvn2pi','Rvp2pi','Flux')
def op(path):return uproot.open(path,object_cache=None,array_cache=None,num_workers=1)
def get(role,key):
 with op(m['sources'][role]['path']) as f:return f[key].values().astype(np.float64)
def residual(x,y):
 scale=0.;error=0.
 for i in range(0,len(x),128):
  scale=max(scale,float(np.max(np.abs(y[i:i+128]))));error=max(error,float(np.max(np.abs(x[i:i+128]-y[i:i+128]))))
 return error/scale
with np.load(base/'z-cv.npz',allow_pickle=False) as z:
 c=z['hCov_combined5d_total_uthrow'];g=z['hInflation_g']
sv=np.zeros_like(c)
for band in V:
 x=get('support','hCov_universe5d_'+band);sv+=x;del x
 print('BLOCKSUM_VERTICAL_READ',band,flush=True)
for i in range(0,len(c),128):c[i:i+128]-=(g[i:i+128,None]*g[None,:]-1)*sv[i:i+128]
del sv
b=get('active','hCov_stdcombined5d_total_candidate')
print('Z_DEINFLATED_EQUALS_DONOR_BLOCKSUM',residual(c,b),flush=True)
del c
s=get('active','hCov_stdsyst5d_total_candidate')
for role,key in [('stat',m['stat_key']),('ml',m['ml_key'])]:
 x=get(role,key);s+=x;del x
print('DONOR_BLOCKSUM_EQUALS_SYST_STAT_ML',residual(b,s),flush=True)
```

Probe E: independent numerical PSD measurements.

```python
import json,time
from pathlib import Path
import numpy as np,uproot
from scipy.linalg import eigh
p=Path('/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding')
base=p/'uq_5d/z_pilot_20260916_a5'
m=json.loads((base/'z-manifest.json').read_text())
for variant in ('cv','mean','donor_blocksum'):
 if variant=='donor_blocksum':
  with uproot.open(m['sources']['active']['path'],object_cache=None,array_cache=None,num_workers=1) as f:
   c=f['hCov_stdcombined5d_total_candidate'].values().astype(np.float64)
 else:
  with np.load(base/f'z-{variant}.npz',allow_pickle=False) as f:c=f['hCov_combined5d_total_uthrow']
 print('PSD_START',variant,c.shape,flush=True)
 # Use the same symmetrized mathematical object as the production gate; no floor or clipping.
 c=(c+c.T)*0.5
 start=time.monotonic();w=eigh(c,eigvals_only=True,overwrite_a=True,check_finite=False,driver='evr')
 print('PSD_RESULT',variant,'lambda_min',float(w[0]),'lambda_max',float(w[-1]),'negative_fraction',float(max(0,-w[0])/w[-1]),'rtol',1e-9,'pass',bool(w[-1]>0 and w[0]>=-1e-9*w[-1]),'seconds',time.monotonic()-start,flush=True)
 del c,w
```

This verdict is uncommitted at delivery, as required by the read-only instruction. It is prepared for Joseph Bailey to preserve verbatim. Its new measurements should not be represented as committed/live evidence until that preservation occurs.


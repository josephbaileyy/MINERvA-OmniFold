# REPORT: GENCMP X — the sixteen-cell quadrant sums against the 2D result, with their covariance (2026-11-02)

**By** the limitation-resolver lane (Claude), for the director and for Joseph.

**Under** [`FD-GENCMP-X-BINDING.md`](FD-GENCMP-X-BINDING.md):
- the declaration [`FD-GENCMP-X-DECLARATION.md`](FD-GENCMP-X-DECLARATION.md), bound in #666 at M = `260e299b`;
- addendum [X-A1](FD-GENCMP-X-ADDENDUM-A1.md), bound in #672 at M′ = `f14119b1`;
- addendum [X-A2](FD-GENCMP-X-ADDENDUM-A2.md), bound in #684 at M‴ = `b2e2d232`.

**MEASURES:** each (p_T, p_∥) quadrant's sixteen-cell sum against the 2D result's sum over the same region (C-R's d),
with the covariance between the two results built from what they share. Read by the director's ruling 3: agree iff the
joint χ²₄ has p ≥ 0.05 and every |z| ≤ 2.50.

**CANNOT AUTHORIZE:**
- a paper edit. `paper_body.tex:119` is untouched, and §6's text is the declaration's minimum, for Joseph to approve;
- a change to either result's covariance.

**NOT CITABLE FOR:**
- a measured statistical correlation between the two results. Route B's paired estimate failed K2 (§4), so the
  statistical correlation is bounded, not measured;
- an event-by-event weight check of AGKYxF1pi, AhtBY, BhtBY or MinosEfficiency (§3).

**Records** are under `fd/xcov/run/`:
- `v1-probe/`, `v1-a2/` and `k/`: those steps' readouts;
- `logs/` and `receipts/`;
- `sacct.txt`;
- `diag/`: §4's diagnostic;
- `hpss/`: §8's file list.

**Not in git: the two V0 readouts and BOOT's nine lane records.** They stay on pscratch, listed by sha256 in §8's file
list.
- The shared checker `verify_receipt_artifacts.py` gives a false MISSING for them. Each names an input or product bare,
  for example `of_inputs_5d.npz`, and also cites it by its full pscratch path. `classify_bare` tests MISSING before
  BY-PATH.
- This is the same defect that kept E2's vertex configs out of git.
- Their key fields are in §2: V0's digests and outcomes, and BOOT's B0 and lane results.

`$R` = `/pscratch/sd/j/josephrb/gencmp-x-20261102/`.

## 1. Outcome

**Agree, in every reading and at every r.**
- The statistical stream is bounded (route A): K2 failed for the paired statistical block (§4).
- Four bands are also bounded: AGKYxF1pi, AhtBY, BhtBY and MinosEfficiency, which failed V1 (§3).
- The bounded part is varied over r ∈ [0, 1] in the declared one-parameter family, read on its 10,001-point grid. No
  quadrant exceeds 2.50 anywhere on the grid, the joint p never falls below 0.05, and r* does not exist.
<!-- absence-ok: readout facts from k/k.json (quadrants_over empty, changes_at empty, r_star null at every grid point), not a claim that a result was not produced -->

**Every control passed:** K0, K1 (one null band, NormDISCC, §4) and K2 on the joint matrix of the paired blocks, 99 of
99, with no atime deviation.

**With C-R's numbers, for Joseph.** C-R's columns are from the amendment E report's §3.2 (`fd/gencmp-e/c-r/overlap_refined.json`).
K0 verified that X's S₁₆ and S₂D are C-R's, so d is the same quantity in both. C-R's ρ is the single correlation of step
C's rule. X's r is the correlation assigned to the bounded part only. They are different parameters.

| quadrant | C-R: d, % (E_R, Q_R) | C-R reading (ρ*) | C-R z at ρ = 0 | X z, r = 0 | X z, r = 1 |
|---|---:|---|---:|---:|---:|
| QA | +0.141 | agree (1.0003) | +0.015 | +0.051 | +0.163 |
| QB | −0.217 | agree below a correlation (0.9997) | −0.032 | −0.106 | −0.312 |
| QC | −1.478 | agree below a correlation (0.9902) | −0.202 | −0.415 | −0.985 |
| QD | +0.724 | agree below a correlation (0.9982) | +0.092 | +0.275 | +0.694 |
| **joint** | — | — | — | **χ²₄ = 1.170, p = 0.883** | **χ²₄ = 1.240, p = 0.871** |

The X columns are the primary reading: the reported sixteen-cell matrix against Q_R + C_model,2D, with C_model's
vertices paired.

**The printed readings** (`k/k.json`) also agree at every r:

| reading | r = 0: χ²₄, p | r = 1: χ²₄, p | largest \|z\| |
|---|---|---|---:|
| primary | 1.170, 0.883 | 1.240, 0.871 | 0.985 (QC, r = 1) |
| against Q_R alone (C_model,16 unpaired) | 0.782, 0.941 | 0.926, 0.921 | 0.720 (QD, r = 1) |
| sensitivity: the C_PL pair set to 0 | 0.802, 0.938 | 1.163, 0.884 | 0.467 (QC, r = 1) |

The implied per-quadrant correlation between the two results (K + rM)ᵢᵢ / √(C16qᵢᵢ C2qᵢᵢ):
- at r = 0: 0.92, 0.91, 0.77 and 0.89;
- at r = 1: 0.99, 0.99, 0.96 and 0.98.

## 2. Every step, in order

| step | where | from | result | node-h |
|---|---|---|---|---:|
| deploy | saul | fresh clone at M; blobs = the binding's; tests in both environments | OK | 0 |
| V0 | login37, 3:36 | `$R/deploy` at M | **FAIL**: the draw check matched 0 of 100 replicas. The background leg looked for a log line that RE-2 never prints in negweight-refined mode. Route A was read; the other legs passed (`v0/v0.json`, sha256 `eeadfb96…`) | 0 |
| V1 probe | job 60678999, 4:14 | `$R/deploy` | PASS: MaRES and Flux 0–9; projected 1,068 s for 175 universes, within the cap | 0.0706 |
| V1 full | job 60679146, 4:14 | `$R/deploy` | **STOP**: "EtaNCEL:0 wt: 22 files carry its digest" (the exactly-one lookup rule). No readout | 0.0706 |
| X-A1 | #671, bound #672 | — | V0's background leg reads each replica's p1Streams record | — |
| deploy-a1 | saul | fresh clone at M′; blobs and tests | OK | 0 |
| V0-A1 | login37, 3:44 | `$R/deploy-a1` | **PASS**: counts, MC rows, both joins, and all three draw legs for all 100 replicas; route B (`v0-a1/v0.json`, sha256 `ad70afad…`). The first `v0.json` is unchanged | 0 |
| BOOT | job 60679576, 2:55:23 | `$R/deploy-a1` | B0 PASS (the unreplaced replica reproduces S1's bitwise); the native lane and all 8 lanes rc 0; 100 paired replicas | 2.923 |
| V1 dry sweep | login37, 297 s | a clone of X-A2's branch at `a6736d33` | PASS: 175 universes, 350 lookups, 0 zero-match (X-A2 §4) | 0 |
| K own-side dry runs | login37 | X-A2's branch | `a6736d33` stopped (16-cell NormDISCC); `92be5e32` stopped (2D NormDISCC); `312022c3` 101/102; `d670e9a5` 102/102 (X-A2 §4) | 0 |
| X-A2 | #681, bound #684 | — | the lookup takes byte-identical copies; K1's null bands | — |
| deploy-a2 | saul | fresh clone at M‴; 5 of 5 blobs = the binding's; tests 60 OK (omnifold_py310) and 60 OK with 6 skips (root_6_28) | OK | 0 |
| V1 (X-A2) | job 60694933, 29:02 | `$R/deploy-a2` | **34 of 38 bands pass**; 4 bounded (§3) (`v1-a2/v1.json`, sha256 `06707138…`) | 0.484 |
| K | login37, 11.3 s | `$R/deploy-a2` | **agree** (route A); 99/99 controls (`k/k.json`, sha256 `f3dc2a34…`) | 0 |

**Porcelain.** Each step's deploy had empty porcelain before and after. The logs record it, and K's script output
records it for K. Atime deviations: none in V0, V0-A1, the V1 probe, V1-A2 or K.

## 3. V1: four bands bounded

**The rule** (declaration §2.2, as reviewed). For each weight of each universe, the quotient of the two sides'
universe-to-CV ratios is computed on rows where both CV weights are non-zero, sentinel rows excepted. It must be one
constant to RATIO_TOL = 1e-6. Any non-finite quotient fails.

**34 of 38 bands pass.** Over all 350 lookups the largest relative spread on finite rows is 5.96e-8, at float32
precision.

**The four that fail do so on non-finite quotients only:**

| universe | wt: non-finite rows | wr: non-finite rows | finite rows' max spread | passes |
|---|---:|---:|---:|---|
| AGKYxF1pi:0 | 11,913 | 11,913 | 5.96e-8 | no |
| AGKYxF1pi:1 | 45,158 | 45,158 | 5.96e-8 | no |
| AhtBY:0 | 24 | 24 | 5.96e-8 | no |
| AhtBY:1 | 0 | 0 | 5.96e-8 | yes |
| BhtBY:0 | 18 | 18 | 5.96e-8 | no |
| BhtBY:1 | 121 | 121 | 5.96e-8 | no |
| MinosEfficiency:0 | 0 | 18 | 5.96e-8 | no |
| MinosEfficiency:1 | 0 | 18 | 5.96e-8 | no |

There are 32,846,302 rows per weight. A band fails if any of its universes fails, so AhtBY fails through universe 0.
A failed band joins the bounded set (declaration §2.2, ruling 1): its cross block is bounded, not paired.

**Not established.** Whether the non-finite rows are both sides' weights at zero (agreeing) or one side's alone is not
established. Nothing read them. They would change no reading here: the outcome holds at every r with these bands
bounded.
<!-- absence-ok: scoping statement; the cause of the non-finite quotients was not examined, and the report says so -->

**Byte-identical weight files** (X-A2's lookup) resolve in six classes, as the dry sweep found:
- 22 files: EtaNCEL, GEANT_Neutron, GEANT_Pion, GEANT_Proton, MaNCEL, MinosEfficiency, NormDISCC and NormNCRES;
- 8 files: EtaNCEL, MaNCEL, NormDISCC and NormNCRES;
- four 2-file classes (Rvn1pi).

## 4. K

**Controls, 99 of 99:**
- K0: the structural checks;
- K1: per band, lateral shift, normalization, C_PL and C_model block;
- K2: the joint matrix of the paired blocks is PSD.

**The null band.** NormDISCC is null on both sides: its 16-cell blocks are exactly zero, and its 2D blocks' largest
entry is 1.15e-25 of max|C2q|. K1 asserts that, under X-A2's rule. No other band is null.

**Route A for the statistical stream.** `k.json` records the reason: "K2 failed for the statistical block: falls back to
route A".
- V0-A1 and B0 passed and all 100 paired replicas exist, so route B was attempted.
- The joint matrix [[S16stat, K_stat], [K_statᵀ, S2stat]] was not PSD, so under ruling 1 the statistical stream is
  bounded, together with the four V1 bands.

**The diagnostic** (approved by the director; outside the bound steps; changes no reading).
- **Where:** `diag/x_k2_stat_diag.py`, run on login37 in omnifold_py310 with `$R/deploy-a2`'s functions, imported
  read-only.
- **Reads:** inputs through `Inputs` (O_NOATIME, pin-checked), and the paired replicas through `committed_sha`.
- **Writes:** nothing under `$R`. The recursive listing's digest was equal before and after, and the deploy's porcelain
  stayed empty.
- **Prints:** dimensionless magnitudes only (`diag/x_k2_stat_diag.out.json`).
- **Controls:** its R̂ equals `k.json`'s exactly, and the joint matrix is again not PSD.

Results:
- **The joint statistical matrix:** smallest eigenvalue over largest −0.0328 (K2's tolerance is −1e-12).
- **ρ̂ is not above 1.** The paired ρ̂ per quadrant is QA 0.803, QB 0.735, QC 0.678 and QD 0.838. K_stat = R̂ ∘ σ16 σ2ᵀ
  with each side's stated σ, so each quadrant's 2×2 stays PSD up to |ρ| = 1. Every one does.
- **The failure is the 4×4 structure.**
  - The largest scale on the cross block that keeps the joint matrix PSD is t* = 0.927.
  - The most negative direction carries 55% of its weight on the 16-cell side and 45% on the 2D side.
  - Each side's stated statistical correlations differ from the paired replicas' own sample correlations: by up to 0.31
    off the diagonal on the 16-cell side, and up to 0.10 on the 2D side.
  - The replicas' σ is 0.99–1.15 of the stated σ (16-cell) and 0.99–1.07 (2D).
  - The replicas' own 8×8 sample correlation is PSD (smallest eigenvalue 0.066).
- **What that means:** the cross correlations estimated from the paired replicas do not fit the within-side
  correlations of the stated statistical matrices. Those stated matrices are S1's `C_stat` and S5_R's `stat`, built from
  other replica sets.

## 5. Reads and writes

- **Reads:** every pscratch read in V0, V1, BOOT and K went through the bound `Inputs` class (O_NOATIME, pin-checked),
  or through `committed_sha` for products. Atime deviations: none in any readout.
- **Writes:** only under `$R`. Scratch scripts went in `/dev/shm` and were deleted.
- **Archive:** HPSS is deferred (§8).

## 6. The paper's minimum text (declaration §5, route-A row), for Joseph

The declaration fixes the route-A minimum as the route-B sentence plus a clause. Filled in from §1:

> "Summed over each of the four (p_T, p_∥) quadrants, the sixteen-cell result agrees with the two-dimensional result:
> their four differences give χ² = 1.17 for four degrees of freedom (p = 0.88), and none exceeds 2.5 standard
> deviations of its difference. The covariance between the two results is computed from the systematic universes,
> lateral shifts, generator vertices and paired bootstrap replicas they share, with their run-period terms paired period
> by period by construction. The universes' signal weights were checked to agree event by event. The statistical
> correlation and the correlation of four systematic bands, which are not measured, are varied from 0 to 1 within a
> one-parameter family that keeps the joint covariance valid."
<!-- absence-ok: the declaration's fixed minimum text for the route-A outcome (declaration section 5); 'not measured' describes the bounded correlations by design -->

**Two phrases of the route-B sentence do not hold as written under this outcome**, so they are flagged for Joseph and
the director, not changed here:
- **"and paired bootstrap replicas they share".** The paired replicas' cross block was not used (§4). The statistical
  correlation is the bounded one named in the added clause.
- **"The universes' signal weights were checked to agree event by event".** This holds for 34 of 38 bands. The other
  four are the bounded ones in the clause (§3).

**Also for Joseph:**
- χ² = 1.17 is the reading at r = 0. At r = 1 it is 1.24 (p = 0.87).
- `paper_body.tex:119` is not touched.

## 7. Deviations

1. **V0's first draw check could not pass** (X-A1 §1). Its background leg looked for a line that RE-2 does not print
   in negweight-refined mode. Repaired by X-A1. Both V0 runs are in the records.
2. **X-A1's three disclosures** (X-A1 §5):
   - the four-log diagnostic of replicas 1, 2, 3 and 100;
   - the fixture read of `S1_001/xsec.root`;
   - the fixture files written under `/dev/shm`.
3. **The full V1 at M stopped** on the exactly-one lookup rule. Repaired by X-A2. That run wrote no readout. It cost
   0.0706 node-h.
4. **I noticed the V1 stop late.** My watcher was set to fire only when both V1 and BOOT had left the queue. BOOT ran
   on, unaffected: it does not read V1.
5. **X-A2's diagnosis probes and dry runs** ran outside the bound steps (X-A2 §8).
6. **§4's diagnostic** ran outside the bound steps, approved by the director.
7. **V1's time.** The full V1 took 1,722 s against the probe's projection of 1,068 s, within its 1:45 limit.

## 8. HPSS

**Deferred: NERSC HPSS maintenance until 2026-11-06 17:00**, under the director's ruling in
[`RECORD-20261102-director-hpss-deferral.md`](../../../RECORD-20261102-director-hpss-deferral.md) (#685).

**`$R` as it stands on pscratch.** The three deploy clones are excluded. The list holds every file's sha256, size and
path, read O_NOATIME by `fd/xcov/run/receipts/x_filelist.py`:

| run directory | files | bytes | file list | the list's sha256 |
|---|---|---|---|---|
| `gencmp-x-20261102/` | 162 | 1,612,547,259 | `run/hpss/files.sha256` | `2293c8842f5f72da40dcac84cf534d64c3fb8e30ef4e3ad0723d34a6f70ee14a` |

No tar was made. `k.json`'s and `v1.json`'s listed sha256 equal the committed copies'. V0-A1's `maps.npz` (37.7 MB) and
BOOT's replica `.npz` files are in the list but not in git.

**After maintenance.** One catch-up archive runs for E2, E2-A1 and X with the bound procedure. Its result is a
follow-up commit here. `$R` stays until its copy is verified.

## 9. Cost

| job | what | elapsed | node-h |
|---|---|---|---:|
| 60678999 | V1 probe | 4:14 | 0.0706 |
| 60679146 | V1 full at M (stopped) | 4:14 | 0.0706 |
| 60679576 | BOOT | 2:55:23 | 2.923 |
| 60694933 | V1 (X-A2) | 29:02 | 0.484 |
| | **total** (the cap is 5.0) | | **3.548** |

V0, V0-A1, the dry runs, the diagnostics and K ran on login nodes at 0 node-h. Everything ran on regular CPU QOS, one
node per job (`sacct.txt`).

Nothing is submitted, deposited or tagged.

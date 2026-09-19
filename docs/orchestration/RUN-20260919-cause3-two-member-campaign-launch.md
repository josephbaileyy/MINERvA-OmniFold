# RUN RECORD 2026-09-19 — the two-member cause-3 campaign, submitted

**CITABLE FOR:** what was submitted, at what reservation, from which deploy, and under which
admission. **NOT CITABLE FOR** any result — there is none yet. Gate 2 remains **FAIL**; no
scalar-5D covariance is adopted.

Preregistered at **`44e09fd8`** before the first submission:
[`PREREGISTRATION-20260919-cause3-two-member-campaign.md`](PREREGISTRATION-20260919-cause3-two-member-campaign.md).

## 1. The three deploys, each clean and read-only at a named sha

| tree | revision | what runs from it |
|---|---|---|
| `/pscratch/sd/j/josephrb/z2m-20260919/clean` | **`44e09fd8`** | the member arms and `fin5dBKG` — **the same revision for both members**, so the step that produces each member's inputs is identical code |
| `/pscratch/sd/j/josephrb/z2m-assembly/clean` | **`d64257c3`** | `z_build` and `z_grade` — **the preregistered `builder_revision`** |
| `/pscratch/sd/j/josephrb/z2m-bridge/clean` | **`a51f7917`** | `z_null_bridge` only |

⚠ **Three trees rather than one, deliberately.** The preregistration names `d64257c3` as the
builder revision, and `z_grade` refuses any product built at another. The null bridge did not exist
at `d64257c3` — nothing on `main` had ever moved a member's CV executions into the operand slab —
so it runs from its own tree and records its own revision inside the slab it writes. **The
alternative was to amend a committed preregistration mid-production, and the operational
awkwardness is the better price.** Each tree passed `--require-clean --require-checkout
--require-no-nested-checkout --require-not-nested` and was made read-only after its manifest was
recorded.

## 2. Submitted

`sacct` job ids, with the enforced wall cap each was submitted under (`--time` overrides the
script default, which is what makes the reservation the priced one):

| job | arm | tasks | `--time` | reservation |
|---|---|---:|---:|---:|
| **`58597916`** | `uthrow5d_combF` **k = 0** | 1 | `01:00:00` | `1.00` CPU |
| `58598277` | `boot5dG` | 100 | `00:30:00` | `50.00` GPU |
| `58598278` | `ssplit5d` | 24 | `00:45:00` | `18.00` CPU |
| `58598279` | `det5dBKG` | 19 | `01:15:00` | `23.75` GPU |
| `58598280` | `uthrow5d_runF` | 40 | `04:15:00` | `170.00` CPU |
| `58598281` | `uthrow5d_block` | 21 | `07:00:00` | `147.00` CPU |
| `58598282` | `sweep5dBKGrun` (`afterok:58598279`) | 169 | `00:30:00` | `84.50` GPU |
| `58598283` | `uthrow5d_combF` (`afterok:58598280:58598281`) | 1 | `01:00:00` | `1.00` CPU |
| | **k = 1200 total** | **374** | | **`336.00` CPU / `158.25` GPU** |

**Admission, re-measured immediately before each submission, not reused:** R5 headroom
`379.3119` CPU / `481.3914` GPU of the `500` / `500` ceilings, stop date `2026-09-30` **not fired**.
`r5_meter check` returned **`rc 0`** for `336.00`/`158.25` and for `1.00`/`0`. The same meter
returns **`rc 5` — would reach a ceiling** for two fresh members at `672.00`/`316.50`, which is
what decided the campaign's shape.

**Total reserved so far: `337.00` CPU / `158.25` GPU**, against Joseph's `A1` cap of `600` / `400`.

## 3. The k = 0 combine, and what was preserved before it

`mii/member_k000000`'s seven arms were already complete (`577532xx`, `374/374 COMPLETED 0:0`), but
its combine predates the null-operand writer. Before re-running it, the original product was
**MOVED, never deleted**, on the 2026-08-30 precedent for this same namespace:

```
/pscratch/sd/j/josephrb/z2m-20260919/preserved-k0r2-combine-20260919/unified_throw_cov_5d.root
sha256 b1d0ceca67f288eefb949a43a1c5f544d01b45a2b11b34a7c2edc88344e5cbec   2,668,017,742 B
```
verified by `sha256sum -c` **before** the move and re-measured after, with a `RECORD.txt` beside it
naming the origin and the reason.

## 4. Inputs verified present before submitting, not assumed

| input | k = 0 | k = 1200 |
|---|---|---|
| `boot_nd_5d/res_boot_*.npz` | **100** ✓ | the campaign produces them |
| `seedscan_split_5d/res_split_*.npz` | **24** ✓ | " |
| `universe_sweep_bkgaware` (incl. `…_uni_full_CV.root`) | **207** ✓ | " |
| `uthrow_slabs_5d_sb` / `block_slabs_5d_sb` | **40 / 21** ✓ | " |
| shared `active`, `central`, `parent` | present ✓ | same files |

`fin5dBKG` requires the **exact** populations `1-100` and `1-24` — a member with a partial replica
set must refuse rather than quietly combine what it has — and both are met at `k = 0`.

## 5. What runs after the arms, and from where

1. `fin5dBKG` per member, from the **campaign** deploy — builds that member's own `C_stat`,
   `C_ML` and stage-2 support in one job (`1.50` GPU each).
2. `z_null_bridge` per member, from the **bridge** deploy — transcribes that member's two internal
   CV executions into its operand slab. It never recomputes a CV.
3. `z_build` per member, from the **assembly** deploy at the preregistered revision.
4. `z_grade` once, with the preregistration, both members, `--graded-offset 0`, and the graded
   member's own null slab.

**Nothing in that chain may change now.** The grader, every boundary, `S`, `ε` and the
preregistration were all committed before the first job was submitted.

## 6. Disclosed before any result

- **Five of `C_Z`'s 45 bands cannot move with the offset** —
  [`EVIDENCE-20260919-lateral-bands-are-seed-pinned.md`](EVIDENCE-20260919-lateral-bands-are-seed-pinned.md).
  Measured share: **26.0% of `√Tr C_Z`, 6.75% of the trace.** A MET result covers `93.2%` of the
  trace and is silent about the rest.
- **The `k = 0` slabs are three weeks older than the `k = 1200` slabs will be.** Any environment
  drift between them **inflates** the measured spread — it pushes toward an unfavourable result.
  The code is not left to inference: the numerical path is measured identical.
- **The `kappa` arm of the `s_proj` degeneracy test is not evaluated** and cannot be while `kappa`
  is undeclared. Every Rayleigh quotient is recorded so a later `kappa` applies retrospectively.

**Co-Authored-By: Claude Opus 5 (1M context)**

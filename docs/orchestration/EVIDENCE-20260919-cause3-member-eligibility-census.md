# EVIDENCE 2026-09-19 — which existing objects can be cause-3 campaign members, measured

**CITABLE FOR:** the offset-declaration and null-operand census below, the identities and counts
beside each reading, and the measured cost of one complete member.
**NOT CITABLE FOR:** any grade, boundary, adoption or authorization. Nothing here adopts a
covariance or moves a gate. **No compute was spent producing it** beyond metadata reads and one
`sha256sum`.

## 0. Why this was measured

R6 authorizes **one additional member** so that cause 3 can be assessed on ≥ 2 members, and R8 names
**`z-cv.npz`** as the comparison member, conditioned on the code diff since its build. Before
spending the authorization, the question *"can the objects we already have actually serve as the
`k = 0` anchor?"* has to be answered **from the artifacts**, because two separate criteria bear on it
and neither is a code-diff question:

1. **`SPEC` §3.7b branch 2** fails a campaign if *"`est_seed_offset_declared` is `0` on any member"*.
   `Validity.offset_declared_nonzero` is that condition, and it sits in `branch2_failures()`, so it
   **blocks branch 3 (MET) outright**.
2. **R8** requires the graded product's `r_null` to be *"measured in its own production"*, and
   `z_build` structurally requires a `null` source whose support mask equals the production mask.

## 1. The two-key rule, restated from the code that implements it

`seed_offset_policy.declared_offset()` — its own docstring, not a paraphrase:

> `declared = 0` — this leg **did not go through a hooked launcher**. Its seed is its baseline and
> **NOTHING can be concluded about which scan member it is.**
> `declared = 1, value = 0` — this leg **ran hooked, at the archive anchor, deliberately.**
> `declared = 1, value = k` — this leg ran hooked at offset `k`.

The rule exists because *"a leg that silently ran UNHOOKED stamps its baseline — indistinguishable
from a member at `k = 0`."* **A baseline-valued seed is therefore not evidence of being the anchor.**

## 2. Census 1 — the offset stamp, read from every slab

Method: `numpy.load` on each `.npz`, reading `est_seed_offset_declared`, `est_seed_offset` and
`estimator_seed` **by key name**. No file lacked the stamp (`no-stamp = 0` everywhere), so this is a
complete census and not a sample.

### 2a. `z-cv.npz`'s precursor — `uq_5d/z_precursor_20260914/`

| slab set | n | `(declared, offset, estimator_seed)` |
|---|---:|---|
| `uthrow_slabs_5d` | 40 | **`(0, 0, 1000)`** × 40 |
| `block_slabs_5d` | 21 | **`(0, 0, 1000)`** × 21 |

**All 61 slabs are UNDECLARED.** `1000` is `unified_throw_cov.py`'s own group-2 baseline, which is
exactly the reading the two-key rule says carries no information about membership.

### 2b. The `k0r2` anchor — `mii/member_k000000/`

| slab set | n | `(declared, offset, estimator_seed)` |
|---|---:|---|
| `uq_5d/uthrow_slabs_5d_sb` | 40 | **`(1, 0, 1000)`** × 40 |
| `uq_5d/block_slabs_5d_sb` | 21 | **`(1, 0, 1000)`** × 21 |
| `boot_nd_5d` | 100 | **`(1, 0, 42)`** × 100 |
| `seedscan_split_5d` | 24 | **`(1, 0, 42)`** × 24 |

**All 185 slabs are DECLARED at offset 0**, and the seeds are each group's own pinned baseline plus
zero — `1000` for group 2 (`unified_throw_cov`), `42` for group 1 (`bootstrap_nd`,
`seedscan_split`). This is the *"ran hooked, at the archive anchor, deliberately"* state.

### 2c. This directory is the `k0r2` run's own output, not the quarantined rehearsal

Checked, because the quarantined `aa67c426` rehearsal occupied the same path and had the same file
count (517):

- **Every file** under `mii/member_k000000` has an mtime in `2026-08-30 14:43` … `2026-09-01 01:55`,
  which is entirely **after** `DECISION-20260830-joseph-quarantine-k0-member-namespace.md`. The
  authorized move happened.
- **Independently from `sacct`**, not from a launch plan: jobids `57753239` `boot5dG` 100,
  `57753243` `ssplit5d` 24, `57753244` `det5dBKG` 19, `57753245` `uthrow5d_runF` 40, `57753246`
  `uthrow5d_block` 21, `57753247` `sweep5dBKGrun` 169, `57753248` `uthrow5d_combF` 1 —
  **374 / 374 `COMPLETED`, `ExitCode 0:0`.**
- Terminal `uthrow5d_combF` and the combined product agree to the second:
  `unified_throw_cov_5d.root` mtime `2026-09-01T01:55:48-0700`.

**Anchor product identity:**
`/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/mii/member_k000000/uq_5d/unified_throw_cov_5d.root`
`sha256 b1d0ceca67f288eefb949a43a1c5f544d01b45a2b11b34a7c2edc88344e5cbec`, `2,668,017,742` bytes.
Directory: 517 files, `2,733,142,846` bytes.

**This also discharges a standing caveat.** `project-campaign-state` recorded *"COMPLETED IS A
SCHEDULER STATE, NOT A PRODUCT RECEIPT … Nobody has verified the scientific products landed."* They
landed: 185 correctly-stamped slabs and the 2.67 GB combine. **And the verification found the gap in
§3**, which a scheduler state could never have shown.

## 3. Census 2 — the null operands, read from the products with a positive control

The null's operands are the two internal same-run fixed-seed CV executions, stored in the combined
throw product as `hCvExecution0`, `hCvExecution1`, `hCvSupportMask` — that is where the pilot's
`bridge.json` records reading them from, naming the source path, its `sha256 09a029ed…` and each
object's own digest.

Method: byte search of each product for the key name, **paired with a positive control** (`C_unified`,
which both files must contain) so that a zero reading cannot be the search failing.

| product | `hCvExecution` | `C_unified` (control) |
|---|---:|---:|
| `mii/member_k000000/uq_5d/unified_throw_cov_5d.root` | **0** | 2 |
| `uq_5d/z_precursor_20260914/unified_throw_cov_5d.root` | **3** | 2 |

**Corroborated in the code, at the revision each product was built by:**

| revision | role | `hCvExecution` in `unified_throw_cov.py` |
|---|---|---:|
| `7ac0edec` | the deploy that produced `mii/member_k000000` | **0** |
| `e09513d8` | the deploy that produced the z-precursor | 2 |
| `HEAD` (`ce0b717b`) | current | 2 |

First commit to write them: **`d3b6ae2b`** — *"[repair] Z precursor (b)-(g) …"* — an ancestor of
`HEAD` and **not** of the `k0r2` deploy. **The `k0r2` anchor predates the `11b` remedy.** Its
operands were never written, so they cannot be recovered without re-running: `SPEC` §3.6d item 5 is
explicit that a separately produced denominator *"presumes the determinism the null tests."*

## 4. The result, as a table

| candidate `k = 0` anchor | offset declared? | null operands? | why it cannot anchor a gradable campaign |
|---|---|---|---|
| **`z-cv.npz`** (`3d7465f6…`, precursor `09a029ed…`) | **NO** — `(0, 0)` on 61/61 slabs | YES | `Validity.offset_declared_nonzero` fails → `branch2_failures()` non-empty → **branch 2, never MET** |
| **`mii/member_k000000`** (`k0r2`, 374/374) | **YES** — `(1, 0)` on 185/185 slabs | **NO** — 0 of 3 objects | no `r_null` measurable **in its own production**; `z_build` requires a `null` source |

**The two properties the anchor needs are split across two different artifacts, and no existing
member has both.**

## 5. What one member actually costs, measured — reservation is not consumption

From the `577532xx` family's own `ElapsedRaw`, summed per arm:

| arm | n | CPU task-h | GPU task-h | max single task |
|---|---:|---:|---:|---:|
| `boot5dG` | 100 | — | 14.86 | 0.18 h |
| `sweep5dBKGrun` | 169 | — | 26.28 | 0.18 h |
| `det5dBKG` | 19 | — | 13.76 | 0.76 h |
| `ssplit5d` | 24 | 5.83 | — | 0.48 h |
| `uthrow5d_runF` | 40 | 49.11 | — | 2.67 h |
| `uthrow5d_block` | 21 | 31.01 | — | **4.82 h** |
| `uthrow5d_combF` | 1 | 0.58 | — | 0.58 h |
| **TOTAL, one complete member** | **374** | **86.53** | **54.90** | |

Against the authorized **reservation** of `262.00` CPU / `158.25` GPU, actual consumption was
**3.03×** and **2.88×** smaller. The two are different quantities — a reservation is the enforced cap
times the task count — and **which one the cap is denominated in decides whether a second member
fits.**

**⚠ One live risk in the authorized cap, recorded before anyone submits against it.** The
recommended `uthrow5d_block` cap is **3.00 h**, and **1 of this member's 21 block tasks ran 4.82 h**
— the next longest was 2.27 h. The timeout policy allows exactly **one** corrective resubmission per
stage. So a `k₁` member with a comparable distribution would **foreseeably spend its entire recovery
budget on the first timeout**, and a second slow task would **end the campaign with no member
assembled**. `uthrow5d_runF` is clear: **0 of 40** exceeded its `4.25 h` cap.

## 6. What this evidence does not establish

- **It does not price the four downstream stages.** A "member" as priced in
  `DECISION-PACKET-20260918` §12.5 is **seven task arms**, not a `C_Z`. Turning `mii/member_k000000`
  into `C_Z^(0)` still needs the stage-2 universe combine (`fin5dBKG`, `1.5 h` GPU reserved), the
  stat and ML covariances (`adopt5d` / `budget5d`, `1.0 h` CPU each reserved), the active lateral
  candidate (`run_p4_standard.sh`, **no `#SBATCH` header — it runs under an allocation and has no
  reservation of its own**), and the Z assembly. **None of the four appears in §12.5's table.**
- **It does not establish that `z-cv.npz` is wrong.** Its construction is unaffected; what is
  measured here is that its precursor cannot be *certified* as scan member `k = 0`.
- **It grades nothing.** No `s_agg`, `s_med` or `s_proj` was computed, and no `Validity` was
  assembled from a real campaign.

**Co-Authored-By: Claude Opus 5 (1M context)**

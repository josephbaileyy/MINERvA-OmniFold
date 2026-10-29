# PROPOSAL: keep, archive or delete, for the pscratch retention list (2026-10-29)

**By** the measurement session (`coverage`), for the director, who brings it to Joseph.

**Under** the director's request (4) of 2026-10-28, given in a message after PR #460: "By 2026-11-13, draft a
keep/archive/delete proposal with access dates and sizes, measured read-only … For each, say what is on HPSS already,
what is cheap to regenerate, and what is irreplaceable … Don't delete anything. Joseph decides."

**MEASURES:** sizes, file counts, access dates, git-clone HEADs and selected sha256 on pscratch; HPSS archive
inventories; whether files are tracked on `main`. On login28, 2026-10-29T02:01–02:05Z, by `ls`, `stat`, `du`, `find
-printf`, `sha256sum`, `git rev-parse` and `hsi get -` of inventory files.
- No product's contents were read.
- Under `fd-f1-20261027/`, `f1b/` was not entered and no `find` or `du` ran over the parent; each other child was
  measured on its own. `f1b2/` does not exist (`rp1.out`).
  <!-- absence-ok: `ls -la /pscratch/sd/j/josephrb/fd-f1-20261027/` on login28 at 2026-10-29T02:01Z lists 15 children and no f1b2 (rp1.out lines 3-20) -->

**CANNOT AUTHORIZE:** a deletion, an HPSS copy, a NERSC request (that contact is Joseph's), or a change to any record's
retention line.

**CITABLE FOR:** what each directory holds, its size and access ages, where else its contents are, and what each would
cost to rebuild, as far as the records say.

**NOT CITABLE FOR:** a purge date; whether a rebuild would be bitwise.

**Receipts:** [`fd/receipts-ct/retention-proposal/`](fd/receipts-ct/retention-proposal/), probes `rp1.sh`–`rp4`.
`$P` = `/pscratch/sd/j/josephrb`.

## 0. Summary

- **No listed directory is exposed by the 8-week rule before about 2026-12-17.** The oldest access in any of them is
  2026-10-22 (`ibu1-20261022`; `rp1.out`), and NERSC's rule is "assume that any file not accessed within 8 weeks may be
  purged at any time" (`state/2d-closeout/preservation-20261014/REPORT.md:87-88`).
  - 2026-11-20 is the date by which the director asked that retention be raised (`state/measurement-scoping/pv-ladder/RUN.md:275`,
    "the director's instruction of 2026-10-24"), not a measured exposure.
  - NERSC also purges when scratch passes a fullness threshold (`:87`). Ours is at 17.03 of 20.00 TiB, 85.1 %
    (`fd/receipts-ct/preserve/run.log`). So the dates below are a lower bound on safety, not a guarantee.
- **About 21.6 GB of the list's 31.4 GB is git clones** at commits on `main` (§2). They can be re-cloned in minutes from the public
  repository.
- **Three products are on pscratch only:** not in git, and in no HPSS inventory searched (§3).
  - F0's per-experiment table, `fd_f0_experiments.npz` (`7384c651…`, 1,068,642 B). F0b's copy is byte-identical.
  - `cmodel_5d.npz` (`3008d8f6…`), which F0, F0b and Stage G pin.
  - pv-ladder's frozen reweights under `prep/` (22 MB), which its launcher reads through the committed
    `prep-SHA256SUMS` (`state/measurement-scoping/pv-ladder/RUN.md` §6), and its 30 products, whose digests are
    committed but whose files are not.
  - Proposed: one HPSS archive of these three, about 25 MB (§4, A1).
- **cresp.npz is on HPSS** (`mnv-5d-cresp-20261026`, the one inventory line is `4d8b5797…`, `rp2.out`), so the
  director's question about it is answered.
- **RE-1's `k1_p5_rerun.npz`** on pscratch (`e36f3b25…`) is byte-identical to the copy tracked on `main` under
  `fd/receipts-f1/run/cluster/f1b3/prep/` (`rp3.out`; `git show origin/main:… | shasum`).

## 1. Method

- **Exposed from** = the oldest access time among a directory's regular files + 8 weeks **(arithmetic)**.
- **On HPSS** = named in an HPSS archive's own inventory file, read with `hsi get -`. `htar -t` reads only the s5p
  archive, which has an index (`fd/receipts-ct/retention/ret6.out`).
- **In git** = `git ls-tree -r origin/main` at `9a18ddda`, with the digest compared where it matters.
- **Regeneration costs** are from the records named in each row; none was re-measured here.

## 2. The directories

Sizes are apparent bytes (`du --apparent-size`); "clone" is a git checkout whose HEAD is named.

| directory | size, files | oldest → newest access | exposed from | what it holds (`rp1.out`, `rp2.out`) | elsewhere | proposal |
|---|---|---|---|---|---|---|
| `fd-f1-20261027` (not `f1b/`) | deploy 5.17 GB (5 clones: `4b7a9892`, `5015535e`, `5f5e392c`, `741ad029`, `da5f157f`); `f1b3/` 2.61 GB; `preserve/` 1.23 GB; `f1a2/` 99 MB; `f1a/` 26 MB; `f1c/` 8 MB; `grade/`, `logs/`, `gate3/`, `manifest/` < 2 MB | 10-27 → 10-28 | 12-22 | F1's samples, prep, products and receipts | HPSS `mnv-5d-f1-20261028`: `f1a/splines`, `f1b3/{gst,gen5d,prep}`, `f1c/{closure,pe}` (`HANDOFF-20261028-measurement-session.md` §4); `preserve/` is the tar that went there; F1's readout and run receipts are committed | **keep** `f1b/` (the STOP's evidence, never read) and the non-HPSS parts (`f1a2/`, `logs/`, `grade/`, `gate3/`, `manifest/`). The clones and `preserve/` are **delete candidates** after Joseph's word |
| `fd-flux-boot-20261027` | 1.03 GB: clone `f370da5b` + logs 27 KB | 10-27 | 12-22 | 3D's first deploy, the STOP's evidence | logs are the evidence; the clone is re-clonable | **keep** `logs/`; the clone is a delete candidate |
| `fd-flux-boot-20261028` | 1.03 GB: clone `91312bc8`, readout, logs | 10-27 | 12-22 | the 3D run | readout committed (`fd/readout/fd_flux_boot_readout.json`) | **keep** logs; clone a delete candidate |
| `fd-f0-20261025` | 1.02 GB: clone `7fad6e83`; `fd_f0_experiments.npz` 1.07 MB; readout; logs; `preserve/` | 10-25 | 12-20 | F0's re-grade | readout committed; **the table is in neither git nor HPSS** | **archive** the table (A1); keep logs; clone a delete candidate |
| `fd-f0b-20261026` | 1.02 GB: clone `c4396756`; `fd_f0b_experiments.npz` (= F0's, `7384c651…`); readout; logs | 10-26 | 12-21 | F0b | readout committed | as F0 |
| `fd-g-20261025` | 1.02 GB: clone `c4396756`; readout; logs | 10-26 | 12-21 | Stage G | readout committed | keep logs; clone a delete candidate |
| `fd-g-diag-20261026`, `fd-g-followup-20261026`, `fd-g-sens2-20261026` | 1.02–1.03 GB each: clones `d02ce2f2`, `02bf756a`, `3ed50ed5`; readouts; logs | 10-26 | 12-21 | Stage G's diagnostics | readouts committed | as Stage G |
| `fd-g-figures-20261027` | 1.03 GB: clone `933cfe35`; `figures/` 238 KB; `data-product/` 82 KB; logs 945 KB | 10-27 | 12-22 | figures and the 16 × 16 data product | the data product is committed (`fd/data-product/fd_data_product.json`) | keep logs, figures and data product; clone a delete candidate |
| `cresp-20261026` | 940 MB: `repo/` (a clone); `out/` 25 KB; logs | 10-26 → 10-28 | 12-21 | C_resp | **`out/cresp.npz` on HPSS** `mnv-5d-cresp-20261026` (`4d8b5797…`); `cresp.json` tracked at `state/measurement-scoping/assigned-uncertainties/cresp/cresp.json` | keep `out/` and logs; the clone is a delete candidate |
| `cmodel5d-20261024` | 888 MB: `repo/`; `out/` 25 KB (`cmodel_5d.npz` `3008d8f6…`, `cmodel_5d.json` `3cfdc6a5…`); logs | 10-24 → 10-28 | 12-19 | C_model,5D | `cmodel_5d.json` committed (`nd-unfolding/pv-ladder/readouts/`); **the npz is in neither git nor HPSS** | **archive** the npz (A1) |
| `h2def-20261024` | 252 KB | 10-24 | 12-19 | the H2 definition's build | `h2_definition.json` committed | keep (small) |
| `s1-20261024` | 2.96 GB: 2 clones (1.94 GB); `tmp/` 970 MB (12,545 files); `runs/` 26 MB; `products-hpss/` 26.5 MB; assembly and logs | 10-24 → 10-28 | 12-19 | S1's run | HPSS `mnv-5d-s1-products-20261024` and `-inputs-20261024`; readout committed | keep `s1_assembly.npz`, logs, `runs/`; clones, `tmp/` and the two `*-hpss/` staging copies are delete candidates |
| `pv-ladder-20261024` | 893 MB: clone `ee299e10` 867 MB; `prep/` 22.2 MB; `products/` 2.5 MB; readouts, inventory, logs | 10-24 → 10-28 | 12-19 | the prior-variation ladder | readouts committed; **`prep/` and `products/` in neither git nor HPSS**; `prep-SHA256SUMS` and the products' sums committed (`RUN.md` §6) | **archive** `prep/` and `products/` (A1) |
| `proj1d-20261027` | 449 KB | 10-27 | 12-22 | post-hoc 1D projection | `proj1d.json` tracked on `main` | keep (small) |
| `r10-20261024` | 6.46 GB: 2 clones 1.73 GB; `run2/` 2.37 GB; `smoke/` 2.37 GB | 10-23 → 10-24 | 12-18 | R10 | regenerable: the full run charged 0.9053 CPU node-h (`state/measurement-scoping/r10/REPORT.md:200`); `run2/extract/r10_extra.npz` is cited by path | delete candidate for `smoke/` and the clones; keep `run2/` unless Joseph accepts the rebuild |
| `ibu1-20261022` | 904 MB: clone 824 MB; `run/` 77 MB; `kb1/` 2.6 MB | 10-22 → 10-24 | 12-17 | IBU-1 | regenerable at its recorded charge (`state/2d-closeout/stageF/methods/ibu1/REPORT.md:180`); its products are pinned in that report | keep `run/` and `kb1/`; clone a delete candidate |
| `measurement-paper/phase1/mp1/s1/unf/` | 1.06 MB, 11 npz | 10-28 | 12-23 | MP-1's data unfolds, C_resp's inputs | **HPSS** `mnv-5d-ct-3b-inputs-20261028` (`FD-CT-PRESERVE-REPORT.md`) | keep |
| RE-1 `methods-paper/re1-20261022/out/5d/k1_p5_rerun.npz` | 95 KB (its `out/` is 4.62 GB) | 10-28 | 12-23 | S1's G2 operand | **tracked on `main`**, byte-identical (`e36f3b25…`) | keep; the director's request names only this file of `out/` |

<!-- absence-ok: each "neither git nor HPSS" and "not on HPSS" is scoped to the Search line below -->
Search: `git ls-tree -r --name-only origin/main` @ `9a18ddda` for fd_f0_experiments.npz, fd_f0b_experiments.npz,
cmodel_5d.npz, k1_p5_rerun.npz, r10_extra.npz, proj1d.json and the readouts; `hsi get -` of every HPSS archive's
inventory (`mnv-5d-s1-inputs-20261024`, `mnv-5d-s1-products-20261024` both inventories, `mnv-5d-stage0-inputs-20261023`,
`mnv-5d-cresp-20261026`, `mnv-5d-fd-f4-20261025`, `mnv-5d-f1-20261028`, `mnv-re2-*`, `mnv-5d-ct-3b-inputs-20261028`)
filtered for cmodel, experiments, pv-ladder, h2def, ibu1, r10 and proj1d (`rp4.out`, `fd/receipts-ct/retention/ret6.out`).
- **What it cannot see:** archives made before 2026-10 that have no inventory file (`mnv-quoted-products-20260812`,
  `mnv-scalar5d-solecopy-20260925`, `prd-release-preservation-20261008`) were searched by path name only
  (`fd/receipts-ct/retention/ret3.out`). None of the three products existed then.
- **pv-ladder's `prep/` and `products/`:** this probe did not hash them; A1's inventory would, against the committed sums.

## 3. Irreplaceable, cheap, or neither

- **Irreplaceable on present records** (pinned by digest, in neither git nor HPSS):
  - `fd_f0_experiments.npz` `7384c651…`: rebuilding it means rerunning F0 at `7fad6e83`, at 0 node-h, on inputs that
    are all on HPSS; bitwise equality is not established.
  - `cmodel_5d.npz` `3008d8f6…`: F0's and Stage G's pin. Rebuilding it means rerunning C_model,5D.
  - pv-ladder `prep/` reweights: the launcher reads them only through `prep-SHA256SUMS`, so losing them breaks any
    rerun or re-read (`state/measurement-scoping/pv-ladder/RUN.md` §6).
- **Cheap to regenerate:** every git clone (§2: about 21.6 GB in all), by `git clone` at the named HEAD; every readout and
  receipt that is committed; `r10` and `ibu1` at their recorded costs.
- **Neither:** `f1b/`, the F1 STOP's evidence, which must stay untouched and unread
  (`DECISION-20261027-joseph-f1-reprice-and-scope-review-before-r19.md` item 1).

## 4. Proposed actions, each Joseph's

- **A1. One HPSS archive,** about 25 MB, of `fd_f0_experiments.npz`, `cmodel5d-20261024/out/` and pv-ladder's `prep/`
  and `products/`, by `stage0_preserve.sh` as for 3b's inputs. It would cost nothing in node-h and about 25 MB of HPSS.
- **A2. Delete the git clones** listed in §2 after A1, about 21.6 GB of pscratch. Each is re-clonable at its HEAD.
- **A3. Delete `s1-20261024/tmp/` and the `*-hpss/` staging copies,** about 1 GB, whose contents are on HPSS.
- **A4. Keep everything else** on the list: about 7.6 GB after A2, A3 and F1's `preserve/` tar, which is on HPSS
  **(arithmetic from §2; `f1b/` not measured)**. Of that, 4.7 GB is `r10`'s `run2/` and `smoke/`.
- **A5. Re-measure the access dates** in December, before about 2026-12-17. Reading files only to reset their access
  times is not proposed; that is purge evasion.

## 5. Not changed

Nothing was deleted, copied or modified. No record's retention line is changed by this proposal.

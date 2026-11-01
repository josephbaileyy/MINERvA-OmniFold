# The Supplemental Material's three covariance files (prepared, not deposited)

**Status: candidates, not deposited.** Nothing has been uploaded, and no DOI has been minted. Release is Joseph's
(`DECISION-20261031-joseph-three-covariance-files-and-1b-diagnosis.md` item 1, "Yes, three files").

**Prepared by** the measurement session, 2026-11-01, at the director's request.

## The files

All three are the 5D result's 16 × 16 covariance on the reporting cells R00–R15, in (cm²/nucleon)², with rows and
columns in the order R00, R01, …, R15. That is `cells.csv`'s row order, and the order of the rest of this package.

| file | what it is | sha256 |
|---|---|---|
| `covariance-reported.csv` | **the reported covariance**, C_total + C_resp + C_PL,5D = C_e + C_model_abs + C_resp + C_PL,5D | `76730c5b7143f8933019a502ca23eed635e45340f7d1ed5534813b2242956170` |
| `covariance-without-C_PL5D.csv` | the reported covariance without the run-period block: C_total + C_resp | `20a4b9d8e41c2b53a65b20beebf7abcb2bf46d5fb4de2a30af1ca8e327361ad8` |
| `covariance-C_PL5D.csv` | the run-period block C_PL,5D alone | `03babead4dff1bf19980319a867c9b830a5b7f85896792edc6f07a62c6e991c9` |

- **`covariance-reported.csv` is the reported matrix.** It is byte-identical to this package's `covariance.csv`.
- **The files differ only by C_PL,5D:** reported = without + C_PL,5D, entry by entry, bit for bit.
- **C_PL,5D** is the run-period block of the 5B addition, diag(f) P diag(f) (`FD-CT-5B-ADDITION-DECLARATION.md` §1).
- **C_total + C_resp** is the covariance reported before that addition (`fd/deposit-candidate/covariance.csv`, the
  same bytes).

## Where they come from

Each file is a byte copy of the 5B addition's committed data-product CSV:
- `fd/with-cpl/data-product/fd_data_product_cpl_C_total_plus_C_resp_plus_C_PL5D.csv`;
- `…_C_total_plus_C_resp.csv`;
- `…_C_PL5D.csv`.

The data product `fd_data_product_cpl.json` is sha256 `d6752d2c64aad4426375c03a3171a7015f031e2027928cf89aea6cd3bbb84d50`.

`supplement-covariances.json` gives each file's label, matrix key, sha256 and source.

`nd-unfolding/fd_supplement_covariances.py build` writes the three files and the manifest, and `check` verifies them:

    python3 nd-unfolding/fd_supplement_covariances.py check \
      --data-product docs/orchestration/state/measurement-paper/5d-community-20261024/fd/with-cpl/data-product/fd_data_product_cpl.json \
      --package docs/orchestration/state/measurement-paper/5d-community-20261024/fd/with-cpl/deposit-candidate

`check` holds:
- each file to its source's bytes and to the data product's matrix of that key, bit for bit;
- the relation reported = without + C_PL,5D, bit for bit;
- the reported file to `covariance.csv`;
- the manifest to what `build` writes;
- this README to the three names and digests.

## What they are not

They are not a result of their own. Nothing in them is new: every entry is the committed data product's. They make
no claim about coverage; that the coverage of the reported intervals has not been validated stands
(`FD-1B-STAGE2-REPORT.md`).
<!-- absence-ok: a scoping statement of what these files contain and do not claim; the coverage statement is the decision record's, cited -->

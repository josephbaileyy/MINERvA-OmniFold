# Slot 1 from a private genie_xsec product: what would have to change

The director asked whether G21_11a_00_000's SciSoft tarball could in principle be used from a private product
directory instead of CVMFS, answered only from F1's bound pipeline. This lists the bytes that would change, and
changes nothing. The decision belongs to Joseph, through the declaration amendment.

Line numbers are for the branch's current files at `a754e4a4`. These are F1's bound files plus PG's pending tune
additions from `54a5c71b`: 20 inserted and 3 deleted lines across `setup_genie_v3.sh`, `run_gevgen_v3.sh` and
`gen5d_v3.py`.

## What the product is

`genie_xsec-3.04.00-noarch-G2111a00000-k250-e1000.tar.bz2` (sha256
`ae159887772a54891fc4bddb189ab108d74c4a48db68c13ed7166524e8797590`) is a UPS product tree.
- It holds `genie_xsec/v3_04_00/NULL/G2111a00000-k250-e1000/`, with `ups/genie_xsec.table` and `data/`, and the
  `genie_xsec/v3_04_00.version/` entry.
- Its table, at table lines 15–20:
  - sets `GENIEXSECPATH` and `GENIEXSECFILE` to its own `data/`;
  - prepends that `data/` to `GXMLPATH`;
  - sets `GENIE_XSEC_TUNE` to `"G21_11a_00_000"`.
- Its `data/gxspl-NUsmall.xml` (sha256 `fa475f7f…ed1c`) has header `<genie_xsec_spline_list version="3.00">`,
  `<genie_tune name="G21_11a_00_000">`.
- Its README (sha256 `4a2beead…a7fd`) has one version line, `version v3_04_00 qualifier G2111a00000:k250:e1000`.
- The CVMFS genie_xsec listing at revision 1249 (PR #1281) does not include it. G21_11a's model configuration is in
  the genie product, which this record pins at the CVMFS path layout.

## Bytes that would change

**`3d-unfolding/genie/setup_genie_v3.sh`**
1. Lines 27–34, the qualifier case. A `G21_11a_00_000) export GENIE_XSEC_QUAL=G2111a00000:k250:e1000 ;;` entry is
   needed. Line 5's comment names the tunes.
2. Lines 22, 46 and 48, the UPS database. `GENIE_UPS` is the CVMFS products directory, and line 46 sources its
   `setup`. Line 48's `setup -H … genie_xsec v3_04_00 -q G2111a00000:k250:e1000` can find the product only if
   `PRODUCTS` includes the private directory. That takes a new line between 46 and 48, such as
   `export PRODUCTS="<private products dir>:${PRODUCTS}"`. Without it, `setup` fails and `GENIE_XSEC_TUNE` stays
   unset.
3. Line 55, the `GENIE_XSEC_TUNE` check. It needs no change: the private table sets `G21_11a_00_000`, which equals
   the tune.
   - Through table line 19, `GXMLPATH` would then start with the private `data/`, and GENIE searches it before
     `config/<CMC>/<tune>/`.
   - That directory must hold no file named like a GENIE configuration file. Its listing would need a pin, as
     would every CVMFS genie_xsec `data/` the pipeline uses; see "Also found" below.

**`3d-unfolding/genie/run_gevgen_v3.sh`**
4. Lines 22–29, the reduce case. A `G21_11a_00_000) Q=G2111a00000-k250-e1000 ;;` entry is needed.
5. Line 30. `SRC=/cvmfs/larsoft.opensciencegrid.org/products/genie_xsec/v3_04_00/NULL/$Q/data/gxspl-NUsmall.xml` is
   hard-coded to CVMFS, so it would have to name the private root. reduce does not source the setup, so it can't
   take `GENIEXSECFILE` as the file stands.
   - The `genie` step (`--tune "$TUNE"`, `--cross-sections "$GENIE_SPLINES_V3"`, `-e 0,100`) and the `graphs` step
     both read the reduced file in the run directory. They need no path change.

**`3d-unfolding/genie/gen5d_v3.py`**
6. Line 52, `TUNES`: a `G21_11a_00_000` label is needed.
7. Line 65, `PG_SPLINE_PINS`: the pin `("fa475f7f5066b314f177b10c4c821d76f2db072508be2734243a26544ef7ed1c",
   "4a2beead2f261240a4fed7f7d419d2d68c11bc1fa264faa7e129f8223a7ba7fd", "version v3_04_00 qualifier
   G2111a00000:k250:e1000")`.
   - Lines 63–64's comment says the pins come from PG's probe of CVMFS. It would have to name the SciSoft tarball
     and the private copy's check instead.
   - `spline-check` takes `--source` and `--readme` from its caller, so the file has no path to change. The header
     check would pass on this spline (tune `G21_11a_00_000`, format `3.00`), and `E_LO, E_HI = 0.0, 100.0` (line 66)
     is unchanged.

**PG's own files** (the bound PG binary, not F1's):
8. `pg_generate.sh` line 23, `X=/cvmfs/…/genie_xsec/v3_04_00/NULL`, feeds `spline-check`'s `--source` and
   `--readme` (lines 94–95). Slot 1 would need the private root there.
   - Line 125 maps `G21_11b_00_000` to its truth name.
   - `pg_lib.py` lines 30 and 32 name `U0` and the `TRUTH` map.
   - `nd-unfolding/fd_f1_prep.py` line 45 has the truth label. `PG_U0 = "genie_v3_g21"` (line 43) could stay.
   - The README-pg.md contract would need the private directory as a new input.

## What it would also need, outside the bytes

- **Placing and checking the copy.** The private copy would be written to the cluster by us. A check would have to
  bind it: the tarball's sha256, then each extracted file against this record's pins (spline, README, table and
  the `data/` listing).
- **Provenance.** The CVMFS xattr check would not cover it. Only the SciSoft tarball's digest and the record's pins
  would.
- **The declaration.** FD-F1-DECLARATION.md:66 and :76 name CVMFS as the source of genie and genie_xsec, and
  COVFIX §4.2 runs "F1's bound pipeline … unchanged except for the tune names and the seeds". Items 2 and 5 change
  more than the tune names.

## For contrast: slot 2 from CVMFS (G18_02a_00_000)

`G1802a00000-k250-e1000` is on CVMFS (PR #1281). It needs only the table-driven entries, and no path changes:
- setup's qualifier case (`G1802a00000:k250:e1000`);
- reduce's case (`G1802a00000-k250-e1000`);
- a `TUNES` label;
- the `PG_SPLINE_PINS` entry `("f7ad710100f66e2bb9f260e328fe7fb10ac063148b4222eebe0e3b61b8bfa45a",
  "740bc066a9f41f67910e711ebb856be5aed61ee7b71c59895d001d83e80ab0ae", "version v3_04_00 qualifier
  G1802a00000:k250:e1000")`, the SciSoft digests, to be confirmed against the node's bytes;
- PG's truth-name entries.

The spline header names `G18_02a_00_000`, format `3.00`. Its table sets `GENIE_XSEC_TUNE` to `G18_02a_00_000`.

## Also found

Every genie_xsec table read here prepends its own `data/` to `GXMLPATH` (table line 19). That holds for
G1810a0211b, AR2320i00000, G2111a00000, G1802a00000 and GDNu2001a00000. So during F1's generation, the config
search path starts with the spline product's `data/`, ahead of the tune and CMC directories.

The two `data/` directories extracted in full, G1810a0211b's and GDNu2001a00000's, hold only spline files,
`README`, `isotopes.cfg`, `reduce_gxspl.awk` and `xsec_graphs.root`. None is named like a GENIE configuration file. The record pins the genie product's
directories but not these. The probe rebuild should pin each used tune's `data/` listing, with names only, from the
node.

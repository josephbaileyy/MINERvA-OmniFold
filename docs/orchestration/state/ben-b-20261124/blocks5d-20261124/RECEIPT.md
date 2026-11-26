# (b) part 3: the 5D blocks build and the LL5D read (receipt, tier3-design, 2026-11-25)

**What this records:**
- the one local build of the 5D bias block C_b^5D and the fluctuation block V_F^5D under B5D-BINDING-2;
- the LL5D read under B5D-BINDING-1 that fetched its inputs.

It runs `nd-unfolding/b5d/b5d_build.py` (`69f11025…`), which implements B5D-DECLARATION.md (`676c17fc…`) with A1
(`3d6a497d…`) and A2 (`7f120dc6…`). The record went to the director first.

**CITABLE FOR:** that the bound build ran once on the pinned products and what it printed: the band states, f̂, SE, the
traces, C_b, V_F and the diagnostics, as candidate blocks.

**NOT CITABLE FOR:** any adoption of C_b, of the fluctuation block or of V_F into the reported covariance; any coverage
claim; any note wording.

## The build (once)

**Pre-checks, all passed before the run:**
- the five bound files, re-hashed from main at `7666a3a50fad27cec994ad0c6ed13014db41c3f9`, each equal to B5D-BINDING-2's table;
- the tar, sha256 `13e53ec2b40fa33787f61a8f42a4cfa79f19bd4e9ba855a65584ecc224c7cc86`, equal to the read's recorded value;
- all 1,655 fetched copies equal to their pins:
  - LL5D's manifest `hpss_ll5d_u_list.tsv` (`980bb95e…`) for the 1,654 products;
  - `s1_assemble.CONSTRAINT_SHA256` (`e38ad7d2…`) for the flux constraint;
  - the fetched set equal to the manifest's.

**The run:**
- the command was `python3 -B nd-unfolding/b5d/b5d_build.py --repo <a clean worktree at 7666a3a50> --ll5d
  run-20261124/session/records/fetch-b5d --out record`;
- it started at 2026-11-25T05:32:09Z and ended at 2026-11-25T05:35:13Z: 184 s on a laptop, 0 node-h, with no NERSC contact;
- the exit code was 0;
- stdout was `{"verdict": "COMPLETE", "band_states": {"R1": "ACTIVE", "R2": "ACTIVE", "R3": "ACTIVE"}}`;
- C-LEAK's second pass, at 2¹⁰ scale, passed;
- the record's CSVs equal the json's `matrices_sha256`.

| band | f̂ | SE | state |
|---|---|---|---|
| R1, ranks 1–4 | 1.0912 | 0.0273 | ACTIVE |
| R2, ranks 5–8 | 1.2924 | 0.0356 | ACTIVE |
| R3, ranks 9–16 | 2.9774 | 0.0824 | ACTIVE |

Every ensemble keeps every band. `record/blocks5d.txt` prints the per-ensemble factors, the raw toy and reference
traces, the members, and every diagnostic against C_b.

## For the adoption decision (descriptions, not claims)

**The C_b quadratics below are against C_b alone,** not against C_b + C_e or V_F. They are therefore not coverage
statements.

1. **R3's factor of about 3 sits in the eight weakest modes of D,** where the toy trace is 2.2–2.7× the reference while
   R1's is about 1.06×. A1 §4 applies: f̂ is the toy spread relative to LL5D's rebuilt reference block. Joint clipping
   and the stat-bootstrap differences are not in D, and they could drive part of this. L then scales C_e's own ranks
   9–16, which is a rank-band transfer, not a mode match (declaration §4).
2. **C_b is fit to its four members,** each of which sits at quad ≈ 1 by construction. W3, stage0c_gibuu, both F1 tunes
   and LL5D's mean error lie far outside it: quad from about 470 to 1744, with 17–46% of ‖β‖² outside its span.
3. **Adoption is Joseph's decision,** with A1 §7's caveat named. C_b, fit on nominal and the three C_model vertices,
   added beside C_model can pay twice for the same model deviations; the formula proposed has to say which.

## Files

**The record:**

| file | sha256 |
|---|---|
| `record/blocks5d.json` | `c465768b490acc96515c5340585b8ff1f14735254f269af605ffaf182ae521f9` |
| `record/blocks5d.txt` | `171becc2d085382235b6fc74f94ee5040b1322c39b9cdf4f6d1b95d9cfad356f` |
| `record/C_b_abs.csv` | `743ce6d5ad504ea9a80b6613d5b09d7f42e8e034289a16f4083d1289d9eeabc0` |
| `record/C_b_tune_v1_units.csv` | `eb009c35d26ff57ce1b436ddb256b03bf9c2809282826991be07ddc382eb08aa` |
| `record/V_F.csv` | `763f14c6ace6e69109fc11ded75d8654615fe55d5e53281e9911bc5318a03e93` |

**The build's logs** (repo head, exit code, timing, stdout, stderr):

| file | sha256 |
|---|---|
| `build-20261125/exit-code.txt` | `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa` |
| `build-20261125/start-utc.txt` | `d40fbba6e89ec83b020526ea31893aa3d22a0b1955ca77960fac0c84eabec587` |
| `build-20261125/end-utc.txt` | `22ebcb510e725eafaf6f3f0a08041a1d040635d8acd9bb459515a50bb547dd4c` |
| `build-20261125/repo-head.txt` | `de418ab2cf2ee6514e76a142dd705294f73b710a43599b7c63cfbb3618b7227f` |
| `build-20261125/stdout.txt` | `7e3994888ea2af9ea81168e14136d5e6a374cc4f80931ee285a1687d6d2bf4f2` |
| `build-20261125/stderr.txt` | `70bb781f8065e048dcf337b1db499a4bc14a53e6ae19825bc43d842ed7873a2a` |

**The LL5D read, under B5D-BINDING-1** (logs and the checksum file):

| file | sha256 |
|---|---|
| `run-20261124/lane/launcher.out.txt` | `85407054242058a1677722ae591f60075d7d7355b43dc0e13ca43c2c3b27208e` |
| `run-20261124/lane/wend.txt` | `4ffd481276b68880d00bda26cbd1fa232fef03cc47ce443f9094f436c5081345` |
| `run-20261124/session/connect-b5d.log` | `47a42c1fcd4ddb5d533563e30753a948500df8107d5ba6c927f77e7e8f48e9ce` |
| `run-20261124/session/connect-b5d.done` | `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa` |
| `run-20261124/session/fetch.err` | `870a2c3d1469b10ccfa9b77292f7085d138a187dadb4485b57f63ee754d9f622` |
| `run-20261124/session/records-check.txt` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `run-20261124/session/session.err` | `e42ad52c9bd85228170cedf4cee5db9cf3ff240c0269d14cf56414a038d61e75` |
| `run-20261124/session/session.out` | `b20f0b78923c65b91cadc56bb933f7bdddab127a9ca19f0677333f9282481623` |
| `run-20261124/session/records/fetch-b5d/RECORDS.SHA256SUMS` | `653b8c54ee81c447524d4745e64fc1711556dc6d73d00f047ea257ae2f9b104f` |

## Not committed, and where each copy lives

These are excluded under the director's ruling: they are LL5D's pinned products.

**The tar,** `run-20261124/session/fetch-b5d.tar`:
- sha256 `13e53ec2b40fa33787f61a8f42a4cfa79f19bd4e9ba855a65584ecc224c7cc86`, 501,288,960 bytes;
- a copy is on this laptop, untracked;
- the read wrote it under `/pscratch/sd/j/josephrb/b5d-20261124`.

**The 1,654 fetched LL5D products and the fetched flux constraint,** `run-20261124/session/records/fetch-b5d/`:
- each is pinned in LL5D's committed manifest
  `measurement-paper/5d-community-20261024/fd/receipts-ll5d/hpss-u/hpss_ll5d_u_list.tsv` (sha256 `980bb95e…`); the
  constraint is pinned by `s1_assemble.CONSTRAINT_SHA256` (`e38ad7d2…`);
- the sources are `/pscratch/sd/j/josephrb/ll5d-unfolds-r2/` and MINERvA's parameter file
  `/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt`;
- LL5D's HPSS archive is `/home/j/josephrb/mnv-ll5d-unfolds-r2-20261116/` (`toys.tar`, `null_roles.tar`);
- `RECORDS.SHA256SUMS`, committed above, lists every copy's sha256.

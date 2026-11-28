# IBUB code, read 2: agy gemini-3.8-flash-high (2026-11-23)

**By** `director-helper-3`. This is the second agy read of `2d-unfolding/ibub/`. Its inputs came from `git archive` of
commit `50bd9368f`, and `inputs.sha256` lists them. The copy of `ibub_unit.py` equals that commit's blob, sha256
`84c8cabc…`. Read 2's findings were taken as fixes in the commit that adds this record.

**MEASURES:** one reader's findings on `50bd9368f`. **CANNOT AUTHORIZE:** anything.

**What it confirmed:**
- the real `g2r_check` is correct (read 1's BLOCKER came from a mutated copy; see `../code-r1/README.md`);
- all nine of read 1's dispositions;
- the indexing, the pairing, the bootstrap, the bands and σ_band, z\*, the rule, the guards and the barrier.

**Its verdict:** REVISE, on one MAJOR.

| # | label | finding | disposition |
|---|---|---|---|
| 1 | MAJOR | a truncated or empty `.done` marker crashed the readout (JSONDecodeError) | fixed: the unit is missing (INCOMPLETE), with its problem named. A non-JSON npz meta is treated the same way. Tests `test_a_truncated_or_misnamed_marker_is_missing_not_a_crash` and `test_an_npz_whose_meta_is_not_json_is_missing` |
| 2 | MINOR | C-TRUTH's "the done-marker names the same seed" was not checked | fixed: the unit's marker now carries `kind`, `tune` and `seed`. The readout requires the marker's `unit` and `seed` to be the toy's, or the unit is missing. Test; mutant |
| 3 | MINOR | two surviving mutants: the marker's `data_sha256` alone, and the meta's `kind` and `tune` | fixed: `test_a_marker_naming_another_toys_data_is_invalid` and `test_a_unit_naming_another_tune_or_kind_is_invalid`. Both mutants are added to `mutants.py` |
| 4 | MINOR | a malformed marker raised in `refcheck` and in the unit's rerun check | fixed: `ibub_unit.read_marker` reads an absent, empty or malformed marker as `{}`, which is never PASS. Tests in `test_refcheck_is_the_barrier` and `test_a_malformed_marker_beside_products_is_not_overwritten` |
| 5 | NOTE | the readout refuses `--out` under /pscratch | by design: COV2D's open audit refuses every plain open under /pscratch and /global/cfs, so the readout writes to the login node's own disk. The records are then committed |
| 6 | NOTE | the barrier did not check the reference `.root` digests | fixed: `refcheck` requires both products to equal their marker's digests, and the marker to name its unit. Tests; two mutants |

| file | sha256 |
|---|---|
| `prompt.txt` | `42a4f923d94ea4ed05d799d24ee842d90d660cb508cfcca5d2553ee7f9ef6239` |
| `agy-gemini-3.8-flash-high.txt` | `e4f08d20703b81bc72c36c16b50e1f6adfdd00a84efe4164581a849df3c4e679` |
| `rc.txt` | `bdb452ec7822ddca2df0eafa7b1fb13f73a6b73adc818f019e40070b984a57d0` |
| `inputs.sha256` | `dfbb87050f1a49aaed368d4b4aa591eced03b63592c8a3ca7e253a6ed71fab17` |

**The mutant run on `50bd9368f` is discarded.** I edited the files while it ran, then stopped it, and its mutant 34
remained in `ibub_readout.py`. I found it by checking every mutant's sites against the files, and restored it by hand.
The full mutant run that counts is the one on the commit that adds this record. It ran in a separate worktree at that
commit, and its receipt is `../../code/mutants.txt`.

# (b) part 3: the follow-ups after the build (tier3-design, 2026-11-25)

**Authority:** B5D-BINDING-2 ruling 7 (the held LOWs), and the director's split ruling of 2026-11-25:
- A1, A2 and the declaration are not edited, because they governed the run. A1's PSD-wording LOW is an erratum here.
- The code and test LOWs are fixed now. Joseph's standing rule is to fix now and re-pin with a record.

**What describes the run, and what is on main:**
- **The run:** B5D-BINDING-2's table and `record/blocks5d.json` describe the run that produced the record. That run used
  `b5d_build.py` `69f11025…` and `test_b5d.py` `2df87a4d…`; git keeps those bytes, at merge `69e880bb`.
- **Main:** main's code is the post-fix version below. It produces a byte-identical record (see "No output changes").

| file | the bytes that ran (bound) | main, after these fixes |
|---|---|---|
| `nd-unfolding/b5d/b5d_build.py` | `69f11025c4bc0ad0288bb74641c0e76d0286fea1ba9c86531fc25cc7bb27f30d` | `60745a0e28f2c06c8f2d1b06385076e1ed8251cb21c0fb3fe18f9229d6e54fab` |
| `nd-unfolding/b5d/test_b5d.py` | `2df87a4d08487c4b65eb2cc9fe74b5c906321674cae53a6674a260f5294ae857` | `511591f81050a29d8d5817be7f945d61cd5e41ee97d76a2d279eb1951d9fc76a` |

The declaration (`676c17fc…`), A1 (`3d6a497d…`) and A2 (`7f120dc6…`) are unchanged, so C-PIN stays valid.

## Erratum to A1 (not an edit of A1)

**A1's implementation note says:** "C-PSD refuses an indefinite D, a non-finite C_b, or a C_e that is not positive
semidefinite."

**The guard actually does this.** It refuses C_e unless C_e is finite, its largest eigenvalue is positive, and its
smallest eigenvalue is ≥ −1e-12 × its largest. That is the same 1e-12 relative rule as D's kept-mode rule.

**Two consequences:**
- A zero C_e refuses, although it is positive semidefinite.
- A C_e whose negative eigenvalues lie within −1e-12 × λ_max passes. Those modes are not kept, and V_F carries them
  unchanged.

**The pinned C_e** (`fd_data_product_cpl_C_e.csv`, `222c4dd4…`) has λ_min/λ_max = 5.0e-5, as agy measured and as the
guard passed it in the run. Neither consequence applies to the run.

## The code and test fixes

1. **build()'s docstring** now names B-SEL's closure_nuwro bias check alongside the ratio R, as A1 states.
2. **The second-OSError path.** A failure to print the parent-sync warning after the publishing rename is now not a
   STOP either. The output is already published. Before this fix, a closed stderr could turn a published record into
   exit 5.
3. **C-LEAK's exotic type cases:**
   - mappings must be of the same type (a dict paired with an OrderedDict refuses);
   - list traversal adds the item's index to the path, so a list's items are never taken for the exempt
     `fluctuation/V_F` (a malformed `fluctuation=[{"V_F": …}]` is now compared as non-exempt).
4. **Tighter tests:**
   - the generator test now proves `_build` uses `scaled_predictions`' result: doubling its Tune v1 entry quadruples
     C_b,abs;
   - the members' "n/a" rendering is tested;
   - a test shows the parent is synced after the rename and the staging directory before it;
   - a test shows a failed warning print after publishing is not a STOP.

<!-- absence-ok: a coverage statement about two named lines of the code, not the absence of a result -->
**The checks on the new code** (`code-checks/`):
- 70 tests pass;
- the line trace is 99%. The `__main__` guard and the Linux renameat2 branch are not run;
- 77 of 77 mutants are killed in one clean run, with 0 INVALID.

## A disclosure about the bound mutant count

**One mutant in every count reported from 5cf5aa66 through B5D-BINDING-2 did not compile.** That mutant was "V_F
unchecked". When its anchor's indentation was corrected, its replacement was not, so it failed with a SyntaxError,
which the runner counted as KILLED. The bound "73 of 73" therefore rested on 72 valid mutants plus that one.

**What I did:**
- **Re-ran it on the bound code.** Corrected, the mutant runs against the bound `b5d_build.py` and `test_b5d.py`
  (`69f11025…`, `2df87a4d…`) and is KILLED, by `test_a_nonfinite_v_f_stops`.
- **Checked the rest.** Every other mutant in the bound set compiles against the bound code.
- **Fixed the runner.** `code-checks/mutants.py` now compiles each mutated source first and prints INVALID, never
  KILLED, for one that does not compile.

## No output changes (the verification run)

**The build is deterministic on the fetched products:** fixed seeds, no timestamps or paths in the record.

**One verification run of the fixed code**, authorized by the director:
- it read the same pinned products (tar `13e53ec2…`) into a fresh directory;
- code `60745a0e…`;
- it started at 2026-11-25T07:11:50Z and ended at 2026-11-25T07:12:08Z;
- the exit code was 0;
- the files are in `verify-20261125/` (`comparison.txt`, exit code, timing, stdout, stderr, code sha, repo head).

**Its record is byte-identical to the committed record**, compared against merge `f4f089f8`:

| file | sha256 | |
|---|---|---|
| `blocks5d.json` | `c465768b490acc96515c5340585b8ff1f14735254f269af605ffaf182ae521f9` | identical |
| `blocks5d.txt` | `171becc2d085382235b6fc74f94ee5040b1322c39b9cdf4f6d1b95d9cfad356f` | identical |
| `C_b_abs.csv` | `743ce6d5ad504ea9a80b6613d5b09d7f42e8e034289a16f4083d1289d9eeabc0` | identical |
| `C_b_tune_v1_units.csv` | `eb009c35d26ff57ce1b436ddb256b03bf9c2809282826991be07ddc382eb08aa` | identical |
| `V_F.csv` | `763f14c6ace6e69109fc11ded75d8654615fe55d5e53281e9911bc5318a03e93` | identical |

The verification output is not a new reading, and nothing was overwritten. The record copy itself is not committed,
since its bytes are those above.

**CITABLE FOR:** what changed in the code and tests after the run, and that the record is reproduced byte for byte.

**NOT CITABLE FOR:** any block, factor, band state, adoption, coverage claim or note wording beyond RECEIPT.md.

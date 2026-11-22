# RPL (i) the scale fit: code, tests and mutation receipt (2026-11-22)

**By** limitation-resolver, for the director, under [`RPL-DECLARATION.md`](../RPL-DECLARATION.md) check (i). This is
the code only. Nothing has run on cluster inputs, and no data step, fit or outcome is formed here. The run waits for
P-RPD (RPD-RECO's chain through d2) and the director's binding of this code.

## Files

- `nd-unfolding/rpl_scale_fit.py` (sha256 `bf7c9b6f5fe7b06ec9be30c49c8e5d3d12f013bed1ae2649238c5f504fa281d5`): the fit
  of α in p → p/(1+α) for PB against PA on `PZ_EDGES`, the reproduction control R0 against c0, the planted-scale
  control (+1%, +3%), the outcome table and the descriptive fits. It reads RPD-RECO's records through their predecessor
  chain and replays RPD-RECO's own draws.
- `nd-unfolding/tests/test_rpl_scale_fit.py` (`94e9443b3e5fe2341320040b47cece8d89ce085e11948886f72ac13353f5fe78`):
  49 tests, local fixtures only. The integration tests run RPD-RECO's chain (pins .. d2) on its real-format fixture,
  with a continuous p_par spectrum.
- `nd-unfolding/tests/rpl_scale_fit_mutation.py` (`d63523d8b848e14aa235fc1ba48a9d6f7ecbba6b5c683fd5fe0a64694e984447`):
  30 mutants, each a single-fragment change in a temporary copy beside unmodified RPD-RECO modules, run against the
  suite with `pytest -x` and every thread cap at 1.

## Receipt

- `MUTATIONS.json` (`80da0a2ed5c0783253b7e7beaa2b480cb9c4bdd098b2d576c089e88e30ebbafb`), schema
  `rpl-scale-fit-mutation/1`: **30 of 30 killed**, recorded at the module, suite and harness shas above.
  `mutation.log.txt` is the harness's console output (`MUTATION :: 30/30 killed`, rc 0).
- An earlier run at a previous suite killed 27 of 30. The survivors were real test gaps: `used-bins-or` (a bin used
  when only one prediction reaches 25), `refit-subset` (σ_α from fewer than the 200 refits) and `wall-skipped` (no wall
  check per sample). Three tests were added for them, and this receipt is the rerun at the final suite.
- Line coverage of `rpl_scale_fit.py` under the suite (coverage 7.15.4): 336 of 337 lines; the one line outside it is
  the `if __name__ == "__main__":` call, since the tests call `main()` directly.

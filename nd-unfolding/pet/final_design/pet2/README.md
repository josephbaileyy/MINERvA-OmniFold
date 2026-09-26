# PET2-small hybrid path (P2pre / P2scr)

PET2-small (Keras port of Gregor's PET2, 2,758,702 parameters) at OmniFold step 1 on its own
33-token inputs, pretrained (export `2480f269…`) or scratch; our truth PET at step 2. Simulation
only; diagnostic method development.

| file | role |
|---|---|
| `theirs_rows.py` | PET2 step-1 inputs for any sorted inventory row set via `join_sig.npz` (historical `materialize_theirs`), non-finite policies, R1/R2 transforms on stored values, keyed cache, `crosscheck`, `census` |
| `pet2_response.py` | R1 / R2 on PET2's stored tokens, add_info and globals; per-field treatment table in its docstring |
| `hybrid_driver.py` | `B2MultiFold` subclass: PET2 step 1, init verification at the first optimizer step, recipe audit, throughput / GPU memory |
| `run_pet2_replicate.py` | runner on top of `runner/run_design.py` (pool and bank draws, dev/null/products/R1/R2, bootstrap members) |
| `make_pet2_configs.py` | P2pre / P2scr / P2preS1 / P2scrS1 configs and 8-column manifests (`runner` column) |
| `test_pet2.py`, `test_design_lib_dispatch.sh` | local tests; the shell test needs bash >= 4 |

## Stored non-finite PET2 inputs

**Census** (`theirs_rows.py census`, CPU job 58891690, commit `d5acfea2`, all 489 signal-MC
shards; output `/pscratch/sd/j/josephrb/pet-final-design-20260925/impl-pet2/census/nonfinite-census.json`):

| stored value class | built rows (tokens/entries) | used by a reco-passing inventory row |
|---|---|---|
| token momentum px/py/pz | 218 (344) | **4 rows (4 tokens)** |
| token log E / PID | 0 | 0 |
| add_info (dE/dx, x, y, z, t) | 18,829 (19,999) | **31 rows (42 tokens)**, mostly muon (PID 0) and prong (PID 3) tokens |
| globals | 5 (15) | 0 |

So at most 35 of the 20,573,521 reco-passing rows are affected. 31 is an upper bound for add_info:
a stored +-inf dE/dx becomes finite under the historical conversion (mapped to 100), so it is
never repaired.

**Historical treatment:** none. `materialize_theirs` passes stored values through; its three caches
(tuning, pilot, final) contain no such row (crosscheck job 58880787 byte-equal; NaN scan). Had
the historical rows included one, NaN would have entered the network.

**Policy** (orchestrator decision): the default refuses, and the refusal names the row, token,
column, shard and stored value. `--nonfinite-momentum zero` / `--nonfinite-addinfo zero` opt in:
the stored non-finite momentum components, or the add_info entries that the historical conversion
would leave non-finite (NaN dE/dx, non-finite x/y/z/t), are set to 0 BEFORE the historical
conversion. Every repair (row, token, column, stored value) is recorded in the receipt
(`theirs_inputs.nonfinite_repairs`), and the policies enter the run identity and the cache key. A
non-finite log E, PID or global is always refused. Both P2 variants use the same flags; the dev2P
manifest opts into both.

**Observed repair** (smoke job 58887741, pool F replicate 0): inventory row 32083012, token 32
(aggregate prong, PID 7), stored px = py = pz = NaN with finite log E. It became eta = phi = 0 and
log pT = log(1e-6).

## Reco-response distortions

R1 (calorimetric energy x s) and R2 (muon momentum x s) are applied to the pseudodata's STORED
PET2 inputs. For R1 that means non-muon token energies and momenta, dE/dx, the recoil / passive /
fuzz energies, the diphoton mass and the recomputed per-PID energy sums. For R2 it means the muon
token's momentum at fixed direction, with its energy recomputed. The inputs then pass through the
historical conversion. This is the same physical change the ours path makes (`pet2_response.py`
docstring). With an identity transform this path is byte-identical to `materialize` (tested). The
prior is never transformed.

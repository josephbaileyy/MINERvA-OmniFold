# `n2/`: guarded execution and an unlaunched N2 harness

**Engineering only.** Nothing here has run an experiment, and nothing here can start one. N2 is
**not admitted**. Running it needs Joseph to lift the KNOWN_ISSUES 85 deferral. It also needs the
identity-carrying rebuild (R0) and a real admission record. None of the three exists. N2 is a narrow
data-stream diagnostic. It is not a total-uncertainty or coverage validation, and it is not
automatically the next experiment.

## Modules

| module | scope | what it does |
|---|---|---|
| `execution.py` | **generic** | Loads repository modules from bytes it has already hashed, only from inside the producer's own checkout. Refuses a same-named module imported from anywhere else. Records each executed file's path, sha256 and git blob, HEAD, and whether each file is HEAD's blob. Also records the guard's state, the environment and the input identities. Refuses (exit 3) before any output on a contradiction. Under `--require-provenance` it also refuses on anything unknown. Used by `fixed_truth_toy.py` and `ki85_compare.py`. |
| `identity.py` | **generic** | Takes the event key `(source, mc_run, mc_subrun, mc_nthEvtInFile)` and refuses missing or repeated IDs. Implements the hash split of DESIGN-20261008 §4 and the split manifest. Implements contamination tests C1–C6 on the **materialized** folds. |
| `members.py` | **generic** | Holds the declared plan and its digest. Each member is in exactly one state: `ok`, `failed` or `missing`. Results are published by atomic no-overwrite. The only path to a statistic needs every member to be `ok`. |
| `design.py` | **N2 only** | The DESIGN §16.1 arms and streams (arm T: fresh pseudo-data, MC held; arm B: data-only bootstrap of T001, MC held). Also the seeds, the frozen `E_S` estimator settings, and the `sd_B / sd_T` statistic with its rule. |
| `harness.py` | N2 CLI over the generic parts | Subcommands `plan`, `check-split`, `admit`, `run-member` (one member, through `nd-unfolding/mnv_guarded_run.py` with `--require-provenance`) and `aggregate`. |
| `synthetic_producer.py` | tests only | A numpy world with a known answer. It runs only under a synthetic admission, and a synthetic admission runs only it. |

## What a future admitted investigation can reuse

A prospective transfer test or a redesigned validation would reuse `execution.py`, `identity.py` and
`members.py` unchanged. It would also reuse the admission pattern in `harness.py`: an authorization
record bound by digest, the code commit and module digests, the input digests, the split manifest,
and an absolute output root. Each needs its own design module in place of `design.py`, with its own
arms, statistic and rule. The parts that stay specific to N2 are:

- the two-arm structure;
- holding the MC stream;
- the base-set rule for arm B;
- the seeds;
- the [0.80, 1.25] tolerance;
- `INTENDED_FOLDS`.

## A real launch, once admitted (not available)

1. R0 rebuild with identity branches, then C4 against the production file.
2. R1 materialized folds with a registered salt, then `check-split`.
3. A real N2 producer. **It does not exist.** It must build each experiment's input from the folds: reservoir
   pseudo-data as expanded rows, the training bank and the background template. It must run the
   production driver on that input (`--bootstrap-streams data` for arm B), write the C6 identity
   sidecar, and return the 205 reported values. It must accept `--admission --member --plan-sha256
   --expect --require-provenance --out`, as `synthetic_producer.py` does.
4. An admission record naming that producer and its digest, the commit, the rebuild, the split
   manifest and the authorization. Then `run-member` for each of the 100 members, and `aggregate`.

## Tests

```bash
python3 -m unittest discover -s 2d-unfolding/uq/coverage_fixed_truth/n2 -p 'test_*.py' -v
PYTHONPATH=$(root-config --libdir) python3.13 -m unittest discover \
    -s 2d-unfolding/uq/coverage_fixed_truth/n2 -p 'test_producer*.py' -v   # with PyROOT
```

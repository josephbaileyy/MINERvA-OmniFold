# RE-2 binding, part C: post-processing of the refined 2D rebuild (2026-10-24)

**By** the paper-tighten lane, as director, under `AUTHORIZATION-20261012-2d-closeout-delegation.md` §3 item 2,
`DECISION-20261023-joseph-2d-refined-integrate-ci.md` item 1 and `DECISION-20261024-joseph-2d-model-dependence-component.md`.
**Binds** [`RE2-DECLARATION-C.md`](RE2-DECLARATION-C.md), merged in PR #320 (`a8c8f3d4`; the file's sha256 begins
`e4ae5b43ce025c1c`).

**MEASURES:** nothing; it authorizes the refined post-processing run and its HPSS copy.
**CANNOT AUTHORIZE:**
- adopting `E_R` and `Q_R`, which is Joseph's decision from part C's report;
- folding C_model into `Q_R`;
- any printed wording;
- any edit to `docs/analysis-note/`;
- a coverage statement about `Q_R`.

## The bound code

**Commit `e079ff05447cd36e754654f94b166a6481d3005a`,** the head of PR #320. It is an ancestor of `main`.
- Its 25 files equal the digests in the declaration's §12. The director re-hashed all 25 at this commit: 25 of 25
  OK.
- No file under `2d-unfolding/re2/partc/`, and not `run/launch/re2_hpss.sh`, changed between `8c2b626d` (the commit
  try 4 ran) and `e079ff05`, or between `e079ff05` and `main` at `a8c8f3d4`.
- **The deploy** is a clean checkout of `e079ff05`. Before C1, the lane re-hashes the 25 files against §12 with
  `sha256sum -c`, and records the output and the deploy's `git rev-parse HEAD` in the run's log. A mismatch stops the
  run before C1.

**The director's checks of the PR, at `e079ff05`:**
- `python3 -m unittest test_re2c`: 15 of 15 tests, OK.
- `generate_manifest.py --check --at-sha HEAD`: OK. `verify_hash_bindings.py`: all bindings intact.
- CI `record-checks`: success.
- `re2c_k1roll.py` compares every product exactly, with no numerical tolerance. Its exclusions are named in
  `k1roll.json` and cover only:
  - paths;
  - the copies' own script digests and `arm` records;
  - build_q's module-check values, which record the deploy path;
  - ROOT's rootmap warnings, which the run's stderr captured and the committed stdout did not.
- `try4.strace.log.gz` holds file calls only. Environment blocks print as a count (`/* 266 vars */`), and argv is
  truncated. A search for credential-like strings found only file names (`token.py`, `secrets.py`, `/etc/passwd`
  lookups). It is safe in the public repository.

## Rulings

**Q1–Q4, gaps 1–5 and compute: final,** as recorded in the declaration's §11.

**Condition (d), "a failure is reported, not patched": the reading.**
- Q1's condition governs a **failed reproduction**. A comparison that fails may not be made to pass, by changing a
  tolerance, an exclusion, a number or the code path, without the director.
- It does not forbid repairing a defect in code that is not yet bound, because the binding is what fixes the code.
- **Tries 1–4 are accepted:**
  - every try is recorded, with its commit and outcome (§4.1);
  - try 1's code failure was an import path, which made no comparison pass that would otherwise fail;
  - try 1's two comparator fixes added named non-numerical exclusions (rootmap warnings, deploy paths), not
    tolerances;
  - no try changed a purity product;
  - the bound code is exactly what try 4 ran, cleanly, 36 of 36.
- **From this binding on, the rule is strict.** Any nonzero step in the refined chain stops the run, is reported to
  the director, and is repaired only by an amendment to this binding. That includes a failure in part C's own code.

**The values table's rule: accepted** (the declaration's §11, item 2).
- A number is regenerated only after its positive control reproduces the printed value.
- `re2c_values_unmatched.tsv`'s 21 sites go to integration by hand, each against a source the integration names.
- **`\fpsAbove` (46) stays a declared failure.** 4.502/3.0730 − 1 = 46.5018 %, 0.0018 percentage points above the rounding edge at 46.5. The
  printed 46 may therefore come from unrounded inputs; it is not established as an error. Integration finds its
  source or rewords the sentence. No definition is chosen now.

**Joseph's reviews, before integration prints anything:**
- Fig. 1, visually (ruling Q3). The director may add other figures after reading part C's report.
- The C_model wording (DECISION-20261024 item 3).
- The reworded comparison with MINERvA's published result (§6.2's `\chiPaper` sentence, and the "omits the
  unfolding-model dependence" sentences the declaration's §5 lists).

## Order

1. **C0** is done: the purity K1-roll, before binding (§4.1).
2. **C1–C13:** `bash re2c_run.sh refined <deploy> $B/partc`, on a Perlmutter login node, from the deploy above. No
   Slurm and no QOS; 0 node-h. It stops itself at 15 minutes.
3. **C10:** `bash re2c_fig1_local.sh refined <workdir> <venv python> $B/partc`, on the laptop, in the recorded
   environment. Its inputs come from `chain.json` by digest.
4. **C14:** part C's HPSS bundle, by `re2_hpss.sh` at the bound commit, over `$B/partc/` with Fig. 1's outputs. The
   exact argv goes in the report. The pscratch copy is not deleted.

**Storage:** `$PSCRATCH` and the laptop only. Nothing goes to CFS.

**Grant:** part C charges none of RE-2's room, which stays at 36.8162 node-h.

## Part C's report

`RE2-PARTC-REPORT.md`, beside this record, on a branch, with a PR to the director. It contains:
- the 25-digest check and the deploy's sha;
- each step's argv, status and time, and `chain.json`;
- every refined product's digest;
- the values table: 242 regenerated rows and 8 new products, each with its purity control value; the declared
  failure; and the 21 sites for integration;
- RE2-PLAN §5.3's readouts: `E_R − E_U` in `Q_R`'s σ, and the per-block σ ratios with their percentiles;
- C_model beside `Q_R`, with its two controls and its label and caveats verbatim;
- RO-FPS, printed either way;
- Fig. 1's `RUN-fig1.txt`;
- the HPSS receipt.

**The report makes no adoption statement and no claim change.**

**Every file the report names is tracked.** PR #320 found that `.gitignore` had silently dropped 35 logs that #318
and #319 name. The report runs a check that each path it links or names under `run/` is listed by `git ls-files`,
and records the check's output. `git add -f` is used for ignored record files.

## A record correction: the HPSS receipt's script link

`RE2-HPSS-RECEIPT.md` links `run/launch/re2_hpss.sh` and pins its sha256 `40d5ae10…`. PR #320 parameterized that
file in place, so the link now opens a later version.
- The version the receipt ran is at commit `1442f1d2`. The director re-hashed it there: `40d5ae10…`, equal to the
  receipt's pin.
- This binding adds a note under the receipt's table that says so. No other text of the receipt changes.

Part C may start once this record is on `main`.

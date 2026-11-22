# T3 connect plan (tier3-design, 2026-11-21, DRAFT for the director; nothing runs)

**Under** Joseph's go of 2026-11-21 on item d of the methods scoping ("lets do them", as the director relayed it), and
[`T3-BINDING-1.md`](T3-BINDING-1.md) with addendum V1. **No byte of the bound design or code changes.** The connect
scripts below are new. Each goes to the director with its sha256 before it runs, and each connect needs the director's
go with a window epoch.

## 1. Who submits

**Proposed: tier3-design** (this lane). It wrote and tested the T3 code and ran the RDX connects under the same fence
and read rules. Binding §"Who runs it" leaves the assignment to the director.

## 2. Deploy and code

- **Deploy commit: M_V1 = `8bb4e3b0e1028d960e39de0c202569a08a1218a0`.** A fresh clone into `$OUT/deploy`, clean
  (`status --porcelain --ignored` 0 before and after).
  - `git diff 8bb4e3b0 311ecad09 -- nd-unfolding/tier3 nd-unfolding/prior_retention nd-unfolding/s5e_trace.py
    nd-unfolding/s5p_truths.py` is empty (checked 2026-11-21). So M_V1 and today's main carry the same bound bytes.
  - M_V1 is the commit the binding names.
- **The bound files,** checked by the connect against the binding's table:

| file | sha256 |
|---|---|
| `nd-unfolding/tier3/t3p_arms.py` | `4a685bde238dcc6d…` |
| `nd-unfolding/tier3/t3p_probe.py` | `e27bf07a3e2c6032…` |
| `nd-unfolding/tier3/t3p_read.py` | `f4c221dda95fbbdf…` |
| `nd-unfolding/tier3/sbatch_t3p.sh` | `a21ad29f35a71e46…` |
| `nd-unfolding/tier3/test_t3p.py` | `4879178f4f9783f0…` |
| `nd-unfolding/tier3/t3p_mutation.py` | `ae9667bc71819f09…` |

  The connect script carries the full 64-hex digests, pasted from `shasum -a 256` at M_V1, never typed.
- **FD-PRR's fifteen bound modules** are checked at run time by `t3p_probe.py`'s C-PINS (`P.check_pins(CODE_PINS)`).
- **Tests on the login node, before any sbatch:** `test_t3p.py` under the sourced environment. 69 OK is required, or
  the connect STOPs.

## 3. Jobs, family, price

- **Family `t3p_`:** `t3p_dry`, then `t3p_q3` and `t3p_floor` in either order, each only after `t3p_dry` is DONE with
  C-PAIR passed (the job script enforces this). The director announces the family to every fenced lane before the
  first submit.
- **`--time`** comes from `t3p_probe.py limit <mode>`: dry 2:15:00, q3 2:00:00, floor 5:45:00.
  - **Cap: 10.0 CPU node-h**, the sum of the limits.
  - **Expected: about 6.**
  - The charge is taken from sacct over the three ids.
- **Balance first.** The first connect reads iris's m3246 row and STOPs unless 10.0 ≤ half the remaining balance
  (prr_dry_submit.sh's method). The last committed reading is 1328.8 node-h on 2026-11-13, so half of it is 664.4.
  q3 and floor re-read iris before their sbatch.
- **Out directory:** `$OUT = /pscratch/sd/j/josephrb/t3p-20261121`. It must not exist before connect 1. Nothing is
  written to CFS.

## 4. Inputs (staged once by `t3p_dry`, `t3p_probe.py stage`, O_NOATIME, each copy refused unless it equals its pin)

- **FD-PRR's four inputs, at FD-PRR's pins:**
  - `of_inputs_5d.npz` (1,548,438,020 B);
  - `bkg_dump.npz` (16,017,201 B);
  - `bank_sweep_5d_bkgaware/cv.npz` (2,163,648,810 B);
  - the closure ratio json.

  Paths and digests are as staged in FD-PRR's dry receipt (`fd/receipts-prr/dry/cluster/logs/connect-dry.log.txt`).
- **The A7 GiBUU fine-ratio rho array,** by the committed json's sha256 (FD-PRR A4's rule).
- **The 21 FD-PRR products** C-PAIR (16) and C-P (5) read, from `/pscratch/sd/j/josephrb/fd-prr-20261108/runs/`, each
  against its committed digest (`t3p_probe.prr_digests`).
- **Survival.**
  - Every input was present on 2026-11-11 (AT-RISK).
  - Both input sets are on HPSS: groups `tier3_inputs` and `prr` of `/home/j/josephrb/mnv-at-risk-20261111/`, ARCHIVE
    PASS (`fd/retention-20261110/hpss-20261111/README.md`).
  - Connect 1 runs a stat-only check of every source first. If any is missing or its size differs, it STOPs to the
    director before any sbatch. The fallback is an HPSS restore, under its own go.

## 5. The fence

- **In the job (bound, unchanged):** `$OUT/fence.txt` holds one job-name prefix per line, as the director's go names
  them. Every T3 job refuses without it, or while a listed prefix is queued or running.
  - That check uses `squeue` inside `sbatch_t3p.sh:78`. It is bound bytes, so I leave it unchanged and note it here.
- **In the connect (new):** the lane's own fence uses sacct over the fenced lanes' ids, never squeue.
- **Acks** from every fenced lane, each with a UTC time under 15 minutes old, before each connect. The end message is
  sent after.

## 6. Connects (each on the director's go with a window epoch)

| # | what | node-h |
|---|---|---|
| c1 | survey and stat check; iris; clone at M_V1 and pins; tests; `fence.txt`; one sbatch from the plain login environment (`sbatch --job-name=t3p_dry --time=02:15:00 … sbatch_t3p.sh dry $D $M_V1 $OUT`), the path FD-PRR, ENS1 and E96D submitted by; the job script sources its own environment | ≤ 2.25 |
| c2 | after sacct shows `t3p_dry` terminal: fetch its records (DONE, C-PAIR, C-X, timings) O_NOATIME, with sha256 | 0 |
| c3 | iris; `t3p_q3` sbatch (the same form) | ≤ 2.00 |
| c4 | iris; `t3p_floor` sbatch | ≤ 5.75 |
| c5 | fetch both jobs' records, then `t3p_read.py` per the declaration §7; each result read once | 0 |

- **The connect scripts** are derived from FD-PRR's reviewed `prr_dry_submit.sh` (`934c9c2f…`, committed at
  `fd/receipts-prr/dry/cluster/logs/`), with a diff. Each goes to the director by sha256 before its go.
- **Any STOP, failure or TIMEOUT** goes to the director unrepaired, and nothing is relaunched. A stopped job continues
  only by an addendum the director binds (binding ruling 1; declaration §9.3).

<!-- absence-ok: a plan for unrun connects -->

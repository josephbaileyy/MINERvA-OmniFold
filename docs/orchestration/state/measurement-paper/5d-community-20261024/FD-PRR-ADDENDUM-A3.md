# FD-PRR ADDENDUM A3: the job script reads a Slurm time limit in every form Slurm prints it (2026-11-09, for coverage-5b-audit and the director's binding; nothing runs)

**By:** the valid-region lane (session director-helper-2), at the director's ruling of 2026-11-09 on the prr_ibu STOP.

**Amends:** `FD-PRR-DECLARATION.md` rev 2, as amended by addendum A1 (code at M_A1 =
`6727020a7c58b00dd00806151c627c8a24f72402`). This addendum is separate from addendum A2 (#980), which it does not
touch. It changes only `sbatch_prr.sh`'s TimeLimit check, with its tests and mutants. No bound limit, price, cap,
reading or licence changes.

**CITABLE FOR:** the defect that refused prr_ibu 61035510; the change to `sbatch_prr.sh`; its tests, its required
mutants and the new digests.

**NOT CITABLE FOR:** anything the declaration does not license; any route-2 or prior-retention result.

## 1. The defect

- **What happened.** prr_ibu, job 61035510, refused 41 s after it started, before writing anything
  (`fd/receipts-prr/ibu/attempt1/README.md`). Its output was a ValueError in `sec()`, then
  `[prr] refusing: Slurm TimeLimit 30:00 exceeds the declared 0:30:00`.
- **The read.** `sbatch_prr.sh:39` at M_A1 takes the job's limit from `squeue -h -j "$SLURM_JOB_ID" -o %l`. squeue
  prints a limit under one hour as M:SS, so prr_ibu's 0:30:00 reads "30:00". The connect's own squeue line shows this
  (`fd/receipts-prr/ibu/attempt1/cluster/logs/connect-ibu.log.txt:44`).
- **The parse.** `sec()` at :48-50 split the value into exactly three fields, `h, m, s = (int(x) for x in
  t.split(":"))`. On two fields it raised ValueError.
- **The message.** :46's `|| { echo "… exceeds the declared …"; exit 2; }` reported any non-zero exit of the check as
  a limit breach. The parse error therefore read as "30:00 exceeds 0:30:00", which is false.

## 2. Why no test caught it

- **The smoke path.** Outside Slurm the job takes its limit from `PRR_TIMELIMIT`, which defaults to `LIMIT`
  (`sbatch_prr.sh:41`). That is `prr_probe.py limit`'s output, always H:MM:SS ("0:30:00").
- **The tested forms.** `test_a_limit_above_the_declared_is_refused` used "5:16:00", "1-00:00:00" and "4:00:00"
  (`test_prr.py:1337-1341` @ M_A1). All three are H:MM:SS or D-HH:MM:SS; none is the M:SS form squeue prints below an
  hour.
- **The connect.** Its check reads scontrol, which always prints [D-]HH:MM:SS, so it passed (connect-ibu.log:43).

## 3. Which jobs it touched

Only prr_ibu. dry, iter, cap and misc have limits of 5:15:00, 7:30:00, 6:30:00 and 7:15:00, all at least one hour,
which squeue prints as H:MM:SS. All four completed with DONE (`fd/receipts-prr/{dry,iter,cap,misc}/`). Their products
and receipts are unchanged by this addendum.

## 4. The change (`sbatch_prr.sh:46-74`)

- **`sec()` reads every form Slurm prints:**
  - without a day: M, M:SS and H:MM:SS;
  - with a day: D-H, D-H:MM and D-H:MM:SS.
  Any other value raises ValueError: UNLIMITED, INVALID, an empty value, more than three fields, or a non-digit.
- **The check's exit codes are separated.** The heredoc exits 0 within the limit, 4 above it, and 3 on a value it
  cannot read. The shell branches on the code (`trc`):
  - 3: `[prr] refusing: could not read the Slurm TimeLimit '<TL>'`;
  - 4: `[prr] refusing: Slurm TimeLimit <TL> exceeds the declared <LIMIT>`, the message as before;
  - any other non-zero code: `[prr] refusing: the TimeLimit check failed (rc N)`.
  Every refusal still exits 2 before anything is written.
- **Why "above" is 4, not 1.** The director's ruling asked for a distinct parse code, such as 3. "Above" moved from 1
  to 4 for a further reason: an uncaught Python error also exits 1, so 1 could not mean "above" without repeating the
  original defect.
- **What does not change:**
  - the LIMIT_H line: `LIMIT` is `prr_probe.py limit`'s own H:MM:SS;
  - `JOB_LIMIT_H`, every declared limit and the 27.0 cap;
  - `prr_probe.py`, `prr_ibu.py`, `prr_read.py` and the queues, which are byte-identical to M_A1;
  - every other line of `sbatch_prr.sh`.

## 5. The tests and the required mutants

New tests, all in `JobScript`. Each runs the job script on the stand-in deploy in dry mode, whose declared limit is
5:15:00:
- **`test_a_sub_hour_limit_in_squeues_m_ss_form_is_read`** (REQUIRED): "30:00" passes, and the dry job reaches DONE.
- **`test_two_fields_are_minutes_and_seconds`**: "316:00" (316 min) is refused with "exceeds the declared 5:15:00",
  writing nothing; "5:16" (5 min 16 s) passes.
- **`test_one_field_is_minutes_and_a_limit_equal_to_the_declared_passes`**: "316" is refused as exceeding; "315",
  equal to the declared limit, passes.
- **`test_the_day_forms_are_read`**: "1-0" and "0-05:16" are refused as exceeding; "0-5" passes.
- **`test_an_unreadable_limit_is_refused_as_unreadable_not_as_exceeding`** (REQUIRED): "UNLIMITED", "INVALID" and
  "1:2:3:4" are each refused with "could not read the Slurm TimeLimit '<TL>'". "exceeds" appears in none of the
  messages, and nothing is written.
- **The existing three cases** in `test_a_limit_above_the_declared_is_refused` stay, unchanged.
- **Against M_A1's `sbatch_prr.sh`,** run in the same suite, all five new tests fail and the ten existing `JobScript`
  tests pass (`fd/receipts-prr/a3/tests-at-MA1.txt`).

New mutants, each killed by its named test:

| mutant | change | killed by |
|---|---|---|
| two fields read as H:M (REQUIRED) | `f[0] * 60 + f[1]` → `f[0] * 3600 + f[1] * 60` | the sub-hour test |
| a parse error reported as exceeds (REQUIRED) | `sys.exit(3)` → `sys.exit(4)` | the unreadable test |
| one field read as hours | `f[0] * 60` → `f[0] * 3600` | the one-field test |
| the day dropped | `int(d) * 86400 + …` → `…` | the day-forms test |
| a limit equal to the declared refused | `tl <= lim` → `tl < lim` | the one-field test |
| the unreadable branch removed | `[ "$trc" -ne 3 ] \|\|` → `true \|\|` | the unreadable test |
| exceeds reported as a failed check | `[ "$trc" -ne 4 ] \|\|` → `true \|\|` | the two-field test |

- **"TimeLimit unchecked"** is M_A1's own mutant. Its anchor moves to the new last line,
  `sys.exit(0 if tl <= lim else 4)` → `sys.exit(0)`, and it is still killed by
  `test_a_limit_above_the_declared_is_refused`.
- **The counts:** 109 tests (104 + 5) and 70 mutants (63 + 7). `prr_mutation.py`'s EXPECTED_TESTS is 109.
- **With A2.** A2 (#980) adds one test and one mutant to the same two files. Whichever of A2 and A3 merges second
  takes the union: 110 tests and 71 mutants. That PR's suite and mutation run are then rerun at its new head (the
  director's ruling).

## 6. The new digests (sha256; the other three files are M_A1's)

| file | at M_A1 | after A3 |
|---|---|---|
| `sbatch_prr.sh` | `10290087…` | `4493aad5dff0a8a0316c0f8b4d159c8f08c7666856474b5cf9c4c963a3a7e975` |
| `test_prr.py` | `44223143…` | `e90f85148cbd65ece046e850ee525b49f61d10e172ddf35a80b364eb486d8db7` |
| `prr_mutation.py` | `4666aa06…` | `f996908e3abe07b1cfc8afc55f91993554af0b363af5fe6dd66b9802a23c1c79` |
| `prr_probe.py`, `prr_ibu.py`, `prr_read.py` | unchanged | `f87ee90c…`, `17acad82…`, `f35bc328…` |

## 7. Receipts

- **Where they are made.** In a clean clone at this addendum's code commit, which the receipt README names. A following
  commit adds only the receipt files.
- **How.** Each run is one serial process under `nice -n 19`, with every thread cap at 1. The runs are:
  - every class but `JobScript`;
  - the `JobScript` class alone;
  - `JobScript` against M_A1's `sbatch_prr.sh`;
  - the 70-mutant run.
- **Where:** `fd/receipts-prr/a3/`.

## 8. Attempt 2 (the director's ruling; not part of this addendum's code)

- **The deploy.** Attempt 2 runs from this addendum's merge commit, once the director binds it.
- **The connect's own paths** carry a "-2" suffix: deploy-ibu-2, logs/connect-ibu-2.log and .done, logs/ibu-2.jobid.
- **The job** keeps the name prr_ibu and writes $OUT/log-ibu and $OUT/route2, so `prr_read.py` is unchanged.
- **Attempt 1's files** stay where they are.
- **The connect and the post** go to the director for their sha256 before launch (BINDING 1 ruling 7).
- **The charge.** prr_ibu 61035510's 41 s counts against the cap: the study stands at 7.3900 of 27.0.

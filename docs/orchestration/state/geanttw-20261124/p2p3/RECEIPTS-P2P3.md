# P2–P3 receipts

All local. Nothing has been pushed, and nothing has run on the cluster. Every run below is on this Mac (Darwin, bash 3.2).

## Heads

| commit | what |
|---|---|
| `800c79b85fee92a9921b7301d59310c7530dad7a` | the frozen P2–P3 code and its approved fixes |
| `f313e5dbf93e80dc91e0f75e973640c98eeedc65` | P0 and c2pre COMPLETED gates; linetrace's digit-name fix |
| `d93dc5c7f8cb48bb2e7f372e5f43f8360fe9c5b3` | the evloop mkdir test tightened; linetrace treats `fi ;;` as a keyword |
| `9fdd024eabcc6237cf6efc4a8018314507d40b8b` | tests for seven refusals no test reached (tests only) |

## pytest and line trace (`code/linetrace.txt`), at d93dc5c7f

`python3 linetrace.py` (rc 0):

```
pytest under trace: rc=0; 579 passed, 2 warnings in 1294.47s (0:21:34)
TOTAL                    1175     16    99%
geanttw_evloop.sbatch: 116/116 executable lines traced; not traced: none
geanttw_build.sh: 154/154 executable lines traced; not traced: none
geanttw_connect.sh: 40/40 executable lines traced; not traced: none
geanttw_remote.sh: 214/214 executable lines traced; not traced: none
geanttw_p3.sbatch: 128/128 executable lines traced; not traced: none
```

The Python lines still untraced are the three `sys.exit(main())` lines, two `sys.modules["ROOT"] = saved` restores,
`p3_slim.tparam`/`tpclass` (real uproot TParameter reads; the tests stand them in, since uproot cannot write a
TParameter), and `p3_readout`'s no-O_NOATIME refusal. macOS has no O_NOATIME, so the tests open the door that makes it optional; `test_noatime_is_required_outside_the_tests` checks that the door is shut outside them. 9fdd024ea adds tests
for the other seven. Coverage of those four modules at 9fdd024ea, from the three test files that own them
(`coverage run` with subprocess patching, `pytest tests/test_c2_check.py tests/test_p3_readout.py tests/test_p3_slim.py`):

```
132 passed, 2 warnings in 120.15s (0:02:00)
Name              Stmts   Miss  Cover   Missing
-----------------------------------------------
c2_check.py          86      0   100%
p3_readout.py       213      3    99%   85, 110, 295
p3_slim.py          282      4    99%   120, 124, 150, 399
slim_tparams.py      48      1    98%   69
-----------------------------------------------
TOTAL               629      8    99%
```

The full suite under trace was not rerun at 9fdd024ea.

## The plain suite at the final head, b2140be7a

b2140be7a is the merge of origin/main (7428eea60, as a merge commit) plus the regenerated MANIFEST.tsv. The merge
changed no package file. `python3 -m pytest -q -p no:cacheprovider tests/` in `code/`, 2026-11-28T16:28:21Z to
16:39:12Z, with the checkout clean afterwards:

```
head=b2140be7aeb246b1971c045466ef29102e1095df
pytest rc=0
585 passed, 2 warnings in 634.48s (0:10:34)
```

585 is the 579 above plus the six tests 9fdd024ea adds. No record-checks step runs this suite. On b2140be7a all 42
of record-checks.yml's run steps (its other 2 steps are `uses:`) exit 0 locally with BASE=origin/main.

## Mutation (`code/mutation.txt`), at f313e5dbf

`python3 mutation.py --jobs 6` (rc 1). The unmutated control passed for every file (mutation.py prints only a
failing control).

```
mutants 560; killed 559; not killed 1 (survived or timed out)
  dumpcmp.py: 21 mutants, 21 killed
  p0_check.py: 63 mutants, 63 killed
  geanttw_sacct.py: 54 mutants, 54 killed
  geanttw_provenance.py: 13 mutants, 13 killed
  geanttw_evloop.sbatch: 50 mutants, 49 killed
  geanttw_build.sh: 23 mutants, 23 killed
  geanttw_connect.sh: 16 mutants, 16 killed
  geanttw_remote.sh: 85 mutants, 85 killed
  p2_limits.py: 12 mutants, 12 killed
  c2_check.py: 22 mutants, 22 killed
  p3_slim.py: 69 mutants, 69 killed
  slim_tparams.py: 9 mutants, 9 killed
  p3_readout.py: 77 mutants, 77 killed
  geanttw_p3.sbatch: 46 mutants, 46 killed
```

Survivor:

```
geanttw_evloop.sbatch:111 exit 2->true SURVIVED
```

### Its re-score at d93dc5c7f

d93dc5c7f adds `assert r.stderr.count("REFUSE") == 1` to `test_an_unmakeable_run_dir_refuses`: the mutant fell
through to the fence's `mktemp`, which also exits 2.

By hand, in a scratch copy with line 111's `exit 2` replaced by `true`:

```
$ GEANTTW_REPO=<repo> python3 -m pytest -q -p no:cacheprovider tests/test_shell_scripts.py -k unmakeable_run_dir
FAILED tests/test_shell_scripts.py::TestEvloopFullRun::test_an_unmakeable_run_dir_refuses
1 failed, 168 deselected in 1.04s
```

and on the unmutated code: `1 passed, 168 deselected in 0.85s`.

With mutation.py's own `run_one`, that one mutant and the file's control (`python3 one_mutant.py <code dir>`), where `one_mutant.py` is:

```python
"""Re-score one mutant with mutation.py's own run_one, after its unmutated control."""
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import mutation as M
sel = [m for m in M.mutants() if m[0] == "geanttw_evloop.sbatch" and m[1] == 111 and m[5] == "exit 2->true"]
print("selected:", sel)
assert len(sel) == 1, sel
print("control:", M.run_one(("geanttw_evloop.sbatch", 1, 0, 0, "", "control")))
print("mutant:", M.run_one(sel[0]))
```

Its output:

```
selected: [('geanttw_evloop.sbatch', 111, 61, 67, 'true', 'exit 2->true')]
control: ('geanttw_evloop.sbatch', 1, 'control', 'SURVIVED')
mutant: ('geanttw_evloop.sbatch', 111, 'exit 2->true', 'KILLED')
```

## What changed after the mutation run

`git diff --stat f313e5dbf d93dc5c7f`:

```
 docs/orchestration/state/geanttw-20261124/code/linetrace.py            | 3 ++-
 .../state/geanttw-20261124/code/tests/test_shell_scripts.py            | 1 +
 2 files changed, 3 insertions(+), 1 deletion(-)
```

`git diff --stat d93dc5c7f 9fdd024ea`:

```
 .../geanttw-20261124/code/tests/test_c2_check.py   | 14 ++++++++++
 .../geanttw-20261124/code/tests/test_p3_readout.py |  9 +++++++
 .../geanttw-20261124/code/tests/test_p3_slim.py    | 31 ++++++++++++++++++++++
 3 files changed, 54 insertions(+)
```

No launch or sbatch script changed after f313e5dbf:

```
geanttw_build.sh: unchanged since f313e5dbf
geanttw_connect.sh: unchanged since f313e5dbf
geanttw_remote.sh: unchanged since f313e5dbf
geanttw_evloop.sbatch: unchanged since f313e5dbf
geanttw_p3.sbatch: unchanged since f313e5dbf
```

The changed files, at 9fdd024ea:

```
4458874c4e2aee625eb552d3463f271d28e5033505a3425d7eb9abe801e5fea4  linetrace.py
5d9ddc3112a50714577e0b229ce60ad7aa0312374540907d82c36237b9b3e185  tests/test_shell_scripts.py
29e32fc49025abb0a7e7627d5e5671a062d5dea8c9aef22b083f1fb1d2851d67  tests/test_c2_check.py
e4c32dec2808bf0a574ef0d85ba36104bcc7480b4dea709cac154a2ceeff1459  tests/test_p3_readout.py
2920590bb3a131f428c8cd8525d907d51520f356a5f791c4e294a146a4e3dea3  tests/test_p3_slim.py
```

A stricter assertion or an added test cannot turn a kill into a survivor, so the mutation receipt holds for 9fdd024ea.

## Readers

| read | head | reader | model | session |
|---|---|---|---|---|
| confirm 1 | 800c79b85 | Grok CLI, `--sandbox read-only` | grok-4.7 (reported `grok-4.7-build`), reasoning effort high | `01a220cb-f463-7e22-bf58-84bcce1e682a` |
| confirm 2 | f313e5dbf | Grok CLI, `--sandbox read-only` | grok-4.7 (reported `grok-4.7-build`), reasoning effort high | `01a220e4-b779-70a3-9de0-8fd0e18280fa` |

Joseph chose Grok in place of codex-school2 for these reads. The read copy was hashed before and after each read and
was unchanged. Verdicts are relayed to the director, not recorded here.

## SHA256SUMS-P2P3

Generated at the commit that adds this file, over the P2–P3 package files. Check it with
`shasum -a 256 -c SHA256SUMS-P2P3` from `docs/orchestration/state/geanttw-20261124/`. SHA256SUMS-P0 pins P0's
files at `389e520a5`, where it verifies 18/18; P2–P3 amends nine of those files in place, so it does not verify on
later trees.

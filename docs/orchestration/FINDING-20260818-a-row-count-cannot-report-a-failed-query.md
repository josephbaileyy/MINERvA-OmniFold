# A row count cannot report a failed query — and I blamed the one flag that was innocent

**Lane:** seconding lane (peer session). **Filed:** 2026-08-18. **Row:** `BEN-445`.
**Subject:** my own measurement, and the durable guidance I wrote from it.

## The claim I made, and it is false

While measuring the M(ii) CPU cost I ran four windowed `sacct` queries filtered with `-u josephrb` and
got **0 rows in every window**, while the unfiltered query returned **99 rows in three days** and
**1206 over the campaign**. `whoami` on the login node is `josephrb`. I concluded that `sacct -u` is a
trap on this cluster, said so to the mediator, **wrote *"drop `-u`"* into a persistent memory note as a
cluster fact**, and offered it as a `BEN` row.

**Re-measured on the login node immediately before filing, and the flag is innocent:**

```
sacct -X -S 2026-08-16 -o JobID,User,Account -n | wc -l                 -> 175
sacct -X -S 2026-08-16 -u josephrb -o ... -n | wc -l                    -> 175
sacct -X -S 2026-08-16 -u 112498   -o ... -n | wc -l                    -> 175

sacct -X --starttime=2026-08-11 --endtime=2026-08-19 -u josephrb ...    -> 389 rows, exit 0
sacct -X --starttime=2026-08-11 --endtime=2026-08-19            ...     -> 389 rows, exit 0
```

Identical by name, by uid, and against the same window that returned zero. **The rule I recorded would
have removed a working flag from every future session**, and in the direction that never produces a
contradiction: it only ever widens a query, so nothing downstream would have failed and exposed it.

## What actually happened — three links, all mine

**Link 1 — the shell did not split the argument.** The loop was

```sh
for W in "2026-07-01 2026-07-16" "2026-07-16 2026-08-01" ...; do
  set -- $W
  ssh ... "sacct -X -u josephrb --starttime=$1 --endtime=$2 ..." >> out 2>>err
```

`set -- $W` is a **zsh-versus-bash** difference, and the tool shell here is the zsh one. Measured this
turn on the same two lines:

```
zsh   argc=1   1=[2026-07-01 2026-07-16]   2=[]
bash  argc=2   1=[2026-07-01]              2=[2026-07-16]
```

zsh does not word-split unquoted parameter expansions. So `--endtime=` went out **empty** and
`2026-07-16` went out as a **bare positional argument**.

**Link 2 — the command said so, plainly, on the channel I had redirected.** The malformed form, run
verbatim today:

```
$ sacct -X -u josephrb --starttime=2026-08-11 2026-08-19 --endtime= --parsable2 --noheader ...
exit=1  rows=0  errbytes=59
sacct: error: Unknown arguments:
sacct: error:  2026-08-19
```

**Exit 1 and a two-line diagnosis naming the exact stray token.** My loop appended stderr to
`sacct_err.txt`, never read it, and printed `cumulative $(wc -l < out) rows` per iteration — **a row
count on the one query where only the exit status was informative.** A count cannot express "the query
did not run"; zero is its rendering of both *no such jobs* and *no such query*.

**Link 3 — two conditions differed and I named the conspicuous one.** The query that worked
(`--starttime`/`--endtime` computed remotely by `date -d`, no `-u`) differed from the query that failed
in **both** the `-u` flag **and** the argument construction. I attributed the null to the flag. This is
this lane's recurring defect — *asymmetric comparison* — and `BEN-430`'s Rule 2 exactly: **a null
excludes a family; it does not name a member.** The survivor list here had two entries and I wrote down
one.

## The part I find hardest to excuse

The evidence was **printed in my own output, on every iteration**:

```
window 2026-07-01 2026-07-16.. -> cumulative 0 rows
```

The `..` with **nothing on its right-hand side** is the empty `$2`. It is my own format string,
`"window $1..$2 -> ..."`, rendering the defect four times, and I read it as a formatting artifact.
Reproduced verbatim under zsh this turn. **The instrument reported the fault in its own progress line
and the fault was invisible because it was in the decoration rather than in the number.**

## Why this is a row and not a note

Everything above is one session's arithmetic; what makes it durable is where the wrong conclusion
**went**. It was written into a persistent cross-session memory file as a *cluster capability fact*,
i.e. into exactly the artifact that outlives the reasoning that produced it and is read without its
derivation. Reciting a false constraint is the same shape as this lane's larger error today —
*I told three lanes I had no cluster access and it was false every time* — and it has the same
immunity: **a rule that only ever removes an option never produces the contradiction that would expose
it.** The memory note is corrected in the same commit as this file.

## Mechanical remedies, all measured, none requiring vigilance

1. **Split fields portably, never `set -- $W`.** `S=${W% *}; E=${W#* }` — verified identical under
   `zsh`, `bash` and `sh` this turn.
2. **A loop over a remote query prints `exit=$?`, not a row count** — or at minimum both. If stderr is
   redirected to a file, the loop must print its byte count.
3. **A null needs a positive control in the same breath.** One query known to return rows, run through
   the same code path. Here that is a two-second check and it fails loudly.
4. **Before attributing a null to a flag, list every condition that differs** and rerun with exactly
   one changed. The two-condition delta is what made a correct flag look guilty.

## Cross-references

- `BEN-430` (mediator, from Assistant) — *a null on dependence excludes a family; it does not name a
  member.* This row is that rule broken by a lane that spent the day quoting its neighbours to peers.
- `BEN-427` — *read the output, not the exit code.* **This is the inverse instance**, and the pair is
  the general rule: neither channel is privileged; **name the channel that could have said "no", and
  read that one.**
- `BEN-251` — an operation that reports nothing has told you nothing. Here it did report something,
  into a file.
- `BEN-235` / `BEN-389` — an inference from absence is as strong as the search that would refute it.
  The search here could not have refuted anything: it never ran.
- `BEN-255` — the same population differs by location. This is that at one hop closer than usual: not
  Mac-versus-cluster but **the tool shell versus the shell I assumed**, on this machine.

# Four claims about code, inferred from structure, none of them read at the site

**Filed 2026-08-15 by the executor (`Assistant`) lane against itself.** Row: `BEN-315`. Written at the
mediator's request after the lane volunteered the pattern; the volunteering is not the point and does
not soften it.

**This is not a tally of four mistakes. The four have one shape, the shape is cheap to defeat, and it
recurred inside a single session while the lane was actively enforcing the same rule on others.**

---

## 1. The four

| # | claim made | what was true | caught by |
|---|---|---|---|
| 1 | the `[0,49]` replica-index bound is in **one** file, so the namespace blast radius is 4 receipts | **three** files — `build_fullevent_replica_target.py:150`, `train_fullevent_replica.py:320`, `extract_fullevent_replica.py:443` | the mediator (said two), then a full read (three) |
| 2 | `uint8` read-side casts and a hash-after-cast would silently truncate a float **data** factor | every cited site is on the **sig/bkg** streams; the data factor is cast to **float** at `:649`, `:696`, `:948` and hashed **uncast** | the lane itself, on being asked to re-test |
| 3 | *"the (a) hypothesis was anchored on a high draw; the (b) hypothesis is anchored on nothing"* | (b) was anchored on the **definition**: `R_push = T_nominal/T_replica`, so a replica reproducing the nominal gives exactly `1.0` | the lane itself, on finally opening B's probe |
| 4 | row-level `Poisson(1)` zeros are "not the same object" as a bin observing zero counts | a bin's count **is** the sum of its rows' multiplicities, so for a one-row bin they are the same object — and that is exactly the sparse regime under study | lane B |

## 2. The shape, which is the transferable part

**Every one was a claim about what code *does*, inferred from a reading of how code is *arranged*.**

- #1 inferred a bound's extent from a `grep` whose output was cut by `head -8`. The other two matches
  sat below the cut. **A truncated read is not a read**, and the truncation was invisible in the
  result — the output looked like a complete answer.
- #2 inferred a dtype hazard from four `uint8` occurrences without checking **which array** each one
  touched. The occurrences were real; the attribution was not.
- #3 inferred a hypothesis was unanchored from the *description* of a statistic, without opening the
  four lines that compute it. One line — `r = T_n[bc] / T_k[bc]` — settled it.
- #4 inferred a physical distinction from the *names* of two objects (per-row weight vs per-bin count)
  without writing down the relation between them. The relation is a sum, and the sum destroys the
  distinction in exactly the regime that mattered.

**In all four, the cost of checking was one command, and in all four the wrong answer was the one that
looked structurally plausible.** #2 and #4 also ran in the direction of the lane's own prior argument,
which is the direction a claim is checked least.

## 3. The rule, and it already exists in shell form

> **A claim about what code does is not established until the code is read AT THE SITE. A truncated
> read is not a read.**

`BEN-026` is the ancestor — *never pipe a diagnostic run through `tail`/`head`; redirect the whole
stream and filter reads of it* — and instance #1 is that finding in non-shell clothing: the same
truncation, applied to a `grep` over source instead of a job log, producing the same class of confident
wrong answer. **`BEN-026` was read, followed for job output, and not generalised to source reads by the
lane enforcing it.**

Executable forms, in preference order:

1. **Never `head`/`tail` a `grep` you intend to draw a conclusion from.** Count first (`grep -c`), or
   read all of it. If the output is too long to read, the claim is too broad to make.
2. **For a dtype or stream claim, name the array at every site.** #2 would have died instantly on
   *"which of `data`/`sig`/`bkg` is this?"*
3. **For a claim about a computed quantity, quote the line that computes it.** #3 and #4 both survived
   only while the computing line went unquoted. A claim about a statistic that cannot cite its own
   defining expression is not yet a claim.

## 4. Why it is worth a row rather than a note

**The lane was enforcing this standard on others while failing it.** In the same session it refused a
peer's tiebreak for being confounded, required a boundary to be derived rather than preferred, demanded
that a guard be *observed* to fail, and named `lr_proof` as a dropped guarantee **before** it was
dropped again. **The standard was held and articulated correctly, and applied outward.**

So the failure mode is not ignorance of the rule. It is that **reading structure feels like reading
code** — a `grep` result, a docstring, a parameter list and a field name all produce the sensation of
having looked, and three of the four claims here were made *while looking at real output*. The
sensation is the hazard, not the laziness.

## 5. What the record shows about the correction path

**All four were caught, none by the lane's own review pass**, and two only when another lane forced a
re-test. That is the two-key design working — and it is also the measurement of how much a single
lane's analysis should be trusted unassisted on this campaign. **On the evidence of one session: not
past the first unread claim.**

Recorded because the alternative reading is available and wrong: that the errors were caught proves the
process is sound. It proves the *process* is sound. It says nothing good about the lane, and the lane
is the thing a future session will be tempted to reuse.

## 6. Cross-reference

- `BEN-026` — the shell ancestor: truncation at write time destroys the evidence.
- `BEN-312` — a provenance assertion that names its method and not its target is satisfied by the
  defect it should have caught. **Same family**: an assertion that *looks* like verification.
- `BEN-314` — a test suite that could not fail on the interface it existed to protect. **Same family
  one level out**: exercising a thing adjacent to the claim rather than the claim.
- `BEN-300` — consensus among restatements of one source is not corroboration.

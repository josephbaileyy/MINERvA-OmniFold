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

## 6. A FIFTH INSTANCE, 2026-08-16 — and this time the truncation was written by the lane itself

**Added the next day, by the same lane, while independently verifying `VL134`–`VL140`.** It is here
rather than in a new row because it is the same finding; per this repo's convention a fact is written
once.

To survey `RECEIPT-foldforward-instrumented-closure-20260815.json` — a large nested receipt — the lane
wrote a throwaway walker and printed every leaf it found:

```python
s = str(o)
if len(s) < 200: print(p, '=', s)
```

On that evidence the lane concluded that the receipt **documented its population by count and not by
definition**: it reported `the_two_populations_differ_by_rows = 59` without ever saying *why*, which
would make `VL134`'s headline number unrebuildable by an outside reader. That is a legitimate
`BEN-077` defect and the lane was one edit away from filing it as a new `BEN` row.

**The receipt says it explicitly.** The field is
`recorder_population_s1_b: "pass_reco & pass_truth on half B -- what mcB was CONSTRUCTED with as its
pass_reco ..."`. It is **250 characters long**, so the walker dropped it — along with **17 other
leaves, 18 of the receipt's 280**, none of which the output mentioned.

**The transferable part is the filter, not the mistake.** `len(s) < 200` was chosen to keep a survey
readable, and a length threshold *looks* content-neutral. It is not: in a well-written receipt the
short leaves are **values** and the long leaves are **definitions, provenance and caveats**, because
that is what prose is for. **So a length filter over a document is a semantic filter that removes
exactly the fields which answer "why", and it removes them silently** — the survey came back looking
complete, in the same way instance #1's `head -8` came back looking complete.

Two things distinguish this instance and both cut against the lane:

- **It was self-inflicted.** Instances #1–#4 truncated or misread something someone else had produced.
  Here the lane built the instrument that hid the evidence, one day after writing the finding that
  names this exact hazard, and then reasoned from the instrument's output as though it were the
  document.
- **The conclusion ran toward a defect in someone else's work.** #2 and #4 ran with the lane's own
  prior argument; this one ran toward a finding worth filing. **Both directions are under-checked, and
  the second is the more tempting on a campaign that rewards finding things.**

The one thing it does not show is a broken correction path: the lane caught it itself, before filing,
by opening the field it was about to claim was absent. **That is §5's standard finally met once, and a
single instance is not a trend.**

Executable additions, in the same preference order as §3:

4. **Never conclude "the document does not say X" from a filtered dump of it.** `grep` the document for
   the concept (here: `grep -c pass_truth` would have returned `1`, not `0`), or read the section whole.
   An absence claim needs a covering search, and a truncating survey does not cover.
5. **If a survey script drops any leaf, print the count of what it dropped.** A filter that ends with
   `... 18 of 280 fields omitted` cannot be mistaken for a complete read. **Unreported omission is the
   whole defect in both truncation instances** — `head -8` and now `len(s) < 200` — and neither would
   have survived a one-line omission count.

### 6a. THE EXECUTABLE FORM, adopted 2026-08-16 — and a second lane hit this the same night

**The mediator ran a near-identical truncating walker over the same receipt on the same night and was
misled the same way.** Two lanes independently, on one document, within hours. **That makes it a property
of the tool rather than either lane's carelessness**, which is the only reason it is worth a rule instead
of a note. Adopted by both lanes; use it in anything that surveys a structured document.

```python
def survey(obj, path="", limit=200, dropped=None):
    """Print every leaf, and REPORT what was withheld. The report is the whole point."""
    top = dropped is None
    if top:
        dropped = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            survey(v, f"{path}/{k}", limit, dropped)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            survey(v, f"{path}[{i}]", limit, dropped)
    else:
        s = str(obj)
        if len(s) <= limit:
            print(path, "=", s)
        else:
            dropped.append((path, len(s)))
    if top and dropped:
        print(f"\n!! {len(dropped)} FIELD(S) OMITTED as longer than {limit} chars -- "
              f"THE LONG LEAVES ARE THE DEFINITIONS:")
        for p, n in dropped:
            print(f"   {p}  ({n} chars)")
```

**Run against the receipt in §6, it prints 263 leaves and reports 17 omitted — not the 18 above, and the
one-field difference is worth a sentence.** The original walker dropped `len(s) >= 200`; this one keeps
`len(s) <= limit`. Exactly one leaf, `/THE_QUANTITY_MISMATCH_READ_THIS_FIRST/claim`, is **precisely 200
characters** and falls on the other side of the boundary. `263 + 17 = 280`, so both counts are right about
their own filter. **That a one-character difference in an arbitrary cutoff moves a field between "read" and
"invisible" is the argument for the omission report, not a footnote to it** — and it is why the report
prints paths.

**Why the omission list names paths and not just a count:** the count alone tells a reader that something
was withheld; the paths tell them *whether it was the field they were about to make a claim about*. In
instance five the dropped path was `/RESULT_1.../masks/recorder_population_s1_b` and the claim was about
the population — **one line of output would have ended the error before it was written.**

**And the rule that does not need the code at all:** never conclude *"the document does not say X"* from any
filtered view of it. `grep -c pass_truth` returns `1`. **An absence claim needs a covering search, and a
truncating survey is not one.**

**A note on how this section was written, because it is the same hazard one level up.** The first draft
of it said the dropped field was "278 characters." That number was estimated by eye from the quoted
text and **it is wrong — the field is 250 characters, and 18 of 280 leaves were dropped, not the one.**
Caught by measuring before committing, which is the only reason this paragraph reads as a correction
rather than as instance #6. **A finding about unmeasured claims is the last place an unmeasured number
belongs**, and the pull to supply one was still present while writing the finding that forbids it.

## 7. Cross-reference

- `BEN-026` — the shell ancestor: truncation at write time destroys the evidence.
- `BEN-312` — a provenance assertion that names its method and not its target is satisfied by the
  defect it should have caught. **Same family**: an assertion that *looks* like verification.
- `BEN-314` — a test suite that could not fail on the interface it existed to protect. **Same family
  one level out**: exercising a thing adjacent to the claim rather than the claim.
- `BEN-300` — consensus among restatements of one source is not corroboration.

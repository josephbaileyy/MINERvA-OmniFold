# A citation you cannot re-derive: `BEN-228`'s remedy assumes the citation is yours to update

**Filed 2026-08-15 by the propagation-correction lane** (`BEN-320`, block `320-329`). Raised while
correcting the mediator's relay of `f4267b4` out of the P5A `NOT_CANONICAL.json` generator; subject
items `OI-71` and `CLM-012`. **This is a near-miss report: the defect did not land.** Two of the three
hazards below were caught by a purpose-built gate, and one was caught only because the gate exists.

## 1. The situation

`BEN-228` established the rule this repo now follows for line citations:

> **derive every cited line AFTER the last edit to its file, searching for the CONTENT not the line;
> re-derive, never re-use.** Prefer content addresses that survive insertion over coordinates.

That rule has an unstated premise: **that the citation is an object you may edit.** Every instance
`BEN-228` was filed on satisfies it — a `*_STATUS.md` one-liner, a free-list cell in `FINDINGS.md`, a
`MANIFEST.tsv` field, a digest in prose. All are living documents, all belong to the lane doing the
editing or to a document whose whole purpose is to be maintained.

The task here broke that premise. Correcting the overstatement in
`nd-unfolding/pet/sbatch_p5a_fullevent_nominal_extract.sh` required rewriting a **header comment**,
which sits *above* guard `G1` — and `G1` is cited by coordinate, as
`sbatch_p5a_fullevent_nominal_extract.sh:153-182`, in three places:

| Citing artifact | Kind | May I edit it? |
|---|---|---|
| `state/RECEIPT-vl100-shape-corrected-foldforward-20260815.json:301` | emitted receipt | **No** — a receipt records what its run asserted |
| `state/probe-vl100-shape-correction-scan-20260815.py:249` | the probe that wrote that receipt | **No** — same, it is the producing artifact |
| `BEN-311` in `FINDINGS.md` | **another lane's row** | **No** — `BEN-159`/`BEN-223` both refused exactly this |

## 2. Why all three of `BEN-228`'s options were closed

* **Cannot re-derive.** Re-deriving means *updating the citation to the new coordinate*. Two of the
  three citing artifacts are receipts. Rewriting a receipt to keep a line number true destroys the
  thing the receipt is for, and it is the same class of act as repinning a launcher to make a gate pass.
* **Cannot re-address.** `BEN-228`'s preferred remedy — replace the coordinate with a content address
  that survives insertion — requires editing the citing artifact. Already emitted. Not available.
* **Cannot leave it stale.** A `G1` citation that resolves to a block of comment prose is precisely how
  `BEN-215`/`BEN-216` read: a citation that points at something other than what it claims. And `G1` is
  not an incidental target — it is *the* arm-schema guard, the remedy `BEN-311` holds up as already
  existing in the repo. A stale pointer to it degrades the one row that says the trap has a fix.

## 3. The fourth option, which `BEN-228` does not name

**Make the edit line-count-neutral, and verify the neutrality.**

The header correction was written to occupy exactly the lines it replaced — 13 removed, 13 added — so
the coordinate `:153-182` remains *true* rather than being updated. Verified in two steps, because the
first alone is not sufficient:

```
git diff --numstat nd-unfolding/pet/sbatch_p5a_fullevent_nominal_extract.sh
  -> 13  13
sed -n '153,182p' nd-unfolding/pet/sbatch_p5a_fullevent_nominal_extract.sh
  -> re-read, confirms G1's comment banner and body still occupy the range
```

`numstat` alone would pass if 13 lines were removed *above* and 13 added *below* the cited range, so
**the range must be re-read, not inferred from the line counts.**

### The generalisation: an edit's line count can be part of its contract

In a file whose line ranges are cited by anything you cannot edit, **where you spend lines is
constrained, not just what you write.** The file partitions:

* **above the last cited range** — line-count-frozen; corrections here must be neutral;
* **below it** — free to restructure.

Here that boundary is `:182`, and it is why the substantive rewrite (the `vl100_quotability_scope`
contract, ~40 lines net) went into the generator body **below** the guards while the header correction
above them was squeezed into 13 lines. That was a deliberate placement decision, not a stylistic one.

### Cheap executable form, measured as absent and NOT written

A pre-commit check that greps emitted receipts for `<tracked-file>:<a>-<b>` citations and fails when a
commit changes the line count above `a`. **Not written here**, and the reason matters: this repo already
has a citation gate that failed *closed* on a real defect in this very commit (§4), and adding a second
prose-scanning gate runs into `BEN-228`'s own measured objection — a prose scanner cannot distinguish an
assertion from a quotation of a retracted assertion, and retaining superseded text beside its correction
is a deliberate convention here. Recording the check as available is worth more than arming it.

## 4. Two things the gate caught that a careful reader did not

Both are recorded because **the near-miss is the finding**; neither reached a commit.

**(a) A non-covering pin search — mine.** Before editing the launcher I checked whether it was
hash-pinned, by grepping its filename and filtering the hits on `sha|pin|hash`. That returned nothing
alarming. It was **non-covering**: `state/p5a-extraction-submitted-56978466.json` pairs
`launcher_current` with `launcher_current_sha256` on **separate lines**, so a line-filtered grep cannot
see the pair. `verify_hash_bindings.py` found it immediately. This is the shape already on file as *a
null result from a non-covering search is not evidence of absence* — committed here against my own
check, in the same turn as a finding about relaying unverified claims.

**(b) A checker exiting 0 through a pipe — `BEN-026`'s trap, live.** The commit was run as
`git commit -F … 2>&1 | tail -20; echo "=== rc=$? ==="`. The gate printed `*** BINDINGS BROKEN ***`
and `LONGFORM :: FAIL`, the commit did not happen — **and `rc` printed `0`**, because `$?` carried
`tail`'s status, not `git`'s. The verdict was read off the gate's own text and confirmed against
`git log -1`. **A pipeline's exit code is the last stage's**, so any `| tail` in front of a checker
converts a hard failure into a silent pass. This is the sixth instrument in this campaign to report
success over failure.

## 5. A second, independent hazard in the same file: `bash -n` cannot see a heredoc

`sbatch_p5a_fullevent_nominal_extract.sh` carries **three** `python3 - <<'PY'` heredocs, at `:161`,
`:269` and `:438`. `bash -n` validates the shell and treats each heredoc as an **opaque string**: the
Python inside can be syntactically broken and `bash -n` still exits 0.

**The cost asymmetry is what makes this worth a row.** The largest heredoc (`:438-627`) is the
receipt writer, and it runs *last* — after the full-inventory reweight over 49,152,885 rows. A syntax
error there is discovered **after the GPU is spent**, at the moment the run tries to record what it did.
That is the same failure geometry as job `56978466`, which passed all six guards, completed the
expensive reweight, and then died on `ModuleNotFoundError: No module named 'ROOT'` in the xsec stage.

**What was actually run here**, and what should be run before committing any edit to a launcher heredoc:

1. `bash -n` on the launcher — necessary, not sufficient;
2. extract every `<<'PY'` block and `compile()` each one — all three compile;
3. **execute** the receipt writer against stub arguments and parse its output — it emits valid JSON,
   the corrected keys are present, and the restated values (`0.173`, `68x`) are absent from the whole
   emitted document.

Step 3 is the one that earns its keep: it is the difference between "the code parses" and "the artifact
this run exists to produce is well-formed." A receipt-writing stage is the worst possible place for an
unexercised code path, because it is the stage whose failure destroys the evidence of everything that
succeeded before it.

## 6. What this finding does not claim

* It does **not** claim the line-neutral edit is generally preferable to re-addressing. Where the
  citation *is* yours, `BEN-228`'s remedy is better — a content address survives future edits and a
  neutral coordinate only survives this one.
* It does **not** propose relaxing the receipt-immutability convention to make citations maintainable.
  The convention is load-bearing; this finding is about what to do *given* it.
* The `:153-182` range is true **as of this commit**. It is a coordinate, so it is exactly as fragile as
  `BEN-228` says coordinates are — the next lane to edit above `:153` breaks it and will get no warning,
  because the check in §3 was deliberately not armed. **That exposure is known and accepted, not
  fixed**, and is stated here rather than left for someone to discover.

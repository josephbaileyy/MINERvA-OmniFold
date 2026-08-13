# ADVISORY 2026-08-13 — the advisor review list, rebuilt from the tree rather than from a handoff

**Status: ADVISORY / census.** Lane A (E_avail). Commissioned by `personal-orchestrator` relaying Joseph,
with an instruction I took literally: *"Rebuild it yourself from the OI rows, the two reports, and the Slack
history, and report back what you find that I have not named here — including anything that turns out not
to be Gregor's at all. Do not assume my list is the list."*

**Headline: the list is recoverable, it is six items, and NONE OF THE SIX IS E_avail.**

---

## 1. The authoritative source is the note's own comment macros

`docs/analysis-note/main_note.tex:17-19` defines three:

```latex
\newcommand{\bpn}[1]{\textcolor{blue}{\textbf{[BPN: #1]}}}
\newcommand{\jrb}[1]{\textcolor{violet}{\textbf{[JRB: #1]}}}
\newcommand{\gk}[1]{\textcolor{orange}{\textbf{[GK: #1]}}}
```

Counted across all 20 `.tex` files: **`\gk` 6, `\bpn` 3, `\jrb` 7.** `\gk` is the only Gregor channel in
the repo, and it is complete and greppable. There is no other `GK:` marker, no `% gk` comment, and his name
appears in no `.tex` file.

**The 7 replies account exactly**, which is what makes the census closed rather than approximate:
4 answer `\gk` items (`app_statmethods` 1, `sec_experiment` 1, `sec_systematics` 2) and 3 answer `\bpn`
items (`sec_validation` 3). 4 + 3 = 7.

## 2. Gregor's six, with status measured from the presence of an adjacent `\jrb{}`

| # | file:line | the query | status |
|---|---|---|---|
| G1 | `app_statmethods.tex:14` | *"Is 'seedscan' standard terminology for this? Googling it, I don't really find it used elsewhere."* | **CLOSED** — renamed throughout to "training-seed variation"; artifact names keep `seedscan` as provenance |
| G2 | `sec_systematics.tex:122` | `\sqrt{\mathrm{Tr}C}` notation | **CLOSED** — *"Fixed!"* |
| G3 | `sec_systematics.tex:129` | the word "matrix" | **CLOSED** — *"Fixed!"* |
| G4 | `sec_experiment.tex:46` | *"Are these the selection criteria for events that have `E_recoil_CCinc` set to a positive value?"* | **CLOSED** — long reply at `:47`; and see §4 |
| G5 | `sec_results.tex:5` | *"I feel like section 4 already belongs in Results?"* | **OPEN — no reply anywhere** |
| G6 | `sec_experiment.tex:104` | the note mixes generic method description with MINERvA-specific plots; suggests Introduction → Methods → Data → Results | **OPEN — no reply anywhere** |

**Both open items are about the note's ORGANISATION, and no lane is working on either.** They are the only
unanswered advisor queries in the repo. They are also the two that cannot be discharged by a computation,
which is a plausible reason they have been passed over for five days while the physics threads absorbed
every lane.

## 3. Three items in the tree are NOT Gregor's

`sec_validation.tex` carries three `\jrb{}` replies with no `\gk{}` in the file. They answer **`\bpn`** — a
second reviewer, `main_note.tex:17`. The subjects: whether the closure test should set an uncertainty; move
the GBDT-vs-NN comparison to an appendix because *"The NN in Fig. 15 looks quite bad!"*; and Fig. 17/18
placement. All three are answered, one with a substantive correction (the pre-2026-06-28 point-cloud file's
spurious `k=0` spike).

**Recorded because the assignment was "the problems Gregor raised" and a lane sweeping `\jrb{}` replies for
context would pick these up as his.** They are a different reviewer's and they are closed.

## 4. E_avail is Gregor's only INDIRECTLY, and the scoping matters

`docs/OPEN_ITEMS-ARCHIVE-2026-08.md:991-1000` is explicit and was written at the time:

> *"raised **indirectly** by Gregor in the 2026-08-11 review round. **His literal question** (do the quoted
> criteria give `E_recoil_CCinc` a positive value?) **is answered** … **Chasing the name is what surfaced
> the actual item, which is not about that branch**."*

So: G4 is closed, and everything in `OI-30` / `OI-56` — the `135` constant, the four-species mismatch, the
materiality projection, the two advisories — is **downstream discovery by this campaign, not an advisor
request.** Nobody outside is waiting on it and no advisor has been told it exists.

**That is not an argument for deprioritising it** — `docs/orchestration/ADVISORY-20260813-eavail-published-conventions.md`
§6 raises the first item in the thread that touches a published number. It is an argument against the
framing that Gregor is blocked on it, and against the `OI-30` row's owner field reading `Eavail definition
/ Gregor`, which implies he owes an answer. **What he is actually owed** per that archive row is narrower:
*which construction `minerva-ml` intends*.

## 5. There is no Slack or email record, and the tree says so

The handoff named *"a Slack thread"* as one of its two reconstruction sources. **I cannot corroborate it
from here, and the repo's own record says the channel does not exist.**
`nd-unfolding/ND_OMNIFOLD_RUN_LOG.md:5490-5501`, written when a lane was asked to send Gregor a correction
and verified it three ways:

> *"**There is no correspondence with Gregor in it at all**, and his address appears nowhere in the repo, so
> there is no thread to reply into and no recipient to address."*

plus: the connected Gmail surface has **no send tool**, and the mailbox is Joseph's personal account. The
standing memory that this channel *"accepts drafts and delivers nothing"* is consistent.

**Consequence for this census: `\gk{}` is not merely the best source, it is the only one in the repo.** If
Gregor raised anything outside the note's comments, it is unrecoverable from the tree, and neither I nor the
handoff can enumerate it. **That is the honest bound on §2's completeness** — six items *recorded*, not six
items *raised*.

## 6. A cited primary source in the handoff does not exist

The handoff named `OI30-RESIDUALS-REPORT.md`, *"~57 KB — the more thorough of the two"*, and cited
*"its §'lines 866–871'"* as bounding the strange-species truncation exposure with measured operands.

**Measured — it does not exist:**

- absent from the working tree, and from all four lane worktrees under `.claude/worktrees/`;
- `find /Users/josephbailey/local-research -iname "*OI30*"` returns only the advisory, in four copies;
- `git log --all --diff-filter=A -- '*OI30*' '*RESIDUALS*'` returns **nothing** — never added on any branch;
- the file it could be confused with, `ADVISORY-20260813-oi30-eavail-residuals.md`, is **396 lines / 26,182
  bytes**, so a line-866 citation cannot refer to it either.

The substance attributed to it is real and is in the tree — the `part_gen[:,:,4]` route, the 0.1286% binning
fidelity, and the zero-η/K⁰_S census are in the **`OI-56` row** of `docs/OPEN_ITEMS.md`. So the content
exists and the container does not.

**Recorded as a check rather than a complaint** (`BEN-216`), and the handoff deserves the opposite of a
complaint: it flagged its own uncertainty — *"I am not certain that list is complete… Do not assume my list
is the list"* — which is why I rebuilt from the tree and found §2 and §5 at all. **The failure is narrow and
mechanical: a path and a line range were quoted without an `ls`.** A fresh lane's first act is to open the
sources it was handed, and one of two was a dead end.

---

## What I would put in front of Joseph, in order

1. **G5 and G6 are unowned and are the only unanswered advisor queries in the repo.** Both are structural
   note edits, neither is blocked on any computation or any gate, and G6 proposes reordering §§2–4. If the
   note is close to circulation this is the cheapest outstanding item in the campaign and it has been open
   five days because it is not a physics thread.
2. **`ADVISORY-20260813-eavail-published-conventions.md` §6** — the Ascencio cross-check's missing
   definitional caveat. The only item in this thread that touches a published number.
3. **The `OI-30` owner field** reads `Eavail definition / Gregor`, implying he owes an answer he was never
   asked for. What he is owed is `minerva-ml`'s intended construction, and only that.

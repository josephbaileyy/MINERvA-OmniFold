# FINDING 2026-08-15 — a claim TRUE WHEN WRITTEN, fixed hours later, copied into four documents and a ruling (`BEN-352`)

**Filed by:** Lane A (Eavail), documentation-correction pass, 2026-08-15.
**Cluster access: READ-ONLY throughout.** No `sbatch`/`scancel`/`scontrol`, no writes to `/pscratch`,
nothing repinned, nothing promoted, nothing into `docs/analysis-note/`.

---

## The shape, in one sentence

**A statement about code was true on the day it was written, was fixed by a commit landing the SAME DAY,
was never rechecked, and was copied forward into four documents and one of the principal's rulings — where
it became the sole load-bearing premise of a "this is irreversible" argument. It was refuted only because
the principal made his grant conditional on corroboration from someone other than the author.**

This is not the ordinary stale-doc failure. **Every copy was faithful. Nobody misread anything.** The
defect entered at the single point where a claim about code was written down instead of checked, and
propagation did the rest. The repo's own `CLAUDE.md` names the antidote and it was not applied here:
*"a document costs tokens in every future session forever; a check costs zero and cannot be skipped.
Prefer the executable form of any rule you are tempted to write down."*

---

## THE FALSE CLAIM

> *"Stage 3 writes ten receipts with no `bkg_mode`, the launcher skips any endpoint that already has a
> receipt, and deletions are frozen — so a pre-G-1 stage 3 creates an unfixable provenance regression."*

Paired everywhere with a second claim, **false on both halves**:

> *"G-1 is code-only and not on the cluster checkout."*

## WHAT THE CODE ACTUALLY DOES

`nd-unfolding/run_p4_unfold_std.sh:77-84` — the resume gate:

```bash
if [[ -s "${OUT}" && -s "${REC}" ]] && valid_root "${OUT}"; then
  if RCHK=$(python3 p4_check_receipt.py --receipt "${REC}" --tag "${tag}" \
              --root "${OUT}" --merged "${MERGED}" 2>&1); then
    echo "[unfold] SKIP ${tag} (receipt validated)"; return 0
  fi
  echo "[unfold] STALE ${tag} -> re-running: ${RCHK}"
  rm -f "${REC}"                       # D2: never leave a stale ROOT/receipt pair behind
fi
```

**The skip requires `p4_check_receipt.py` to PASS. Receipt existence is necessary and not sufficient.**
On failure the launcher prints `STALE ... -> re-running`, deletes the receipt, and falls through to a
transactional re-run. And `bkg_mode` is precisely what the validator checks:

| what | where |
|---|---|
| `bkg_mode` is in `RECEIPT_REQUIRED_KEYS` | `nd-unfolding/p4_lib.py:796-797` |
| a missing required key fails closed (*"incomplete legacy format"*) | `nd-unfolding/p4_lib.py:949-950` |
| `bkg_mode` is **COMPARED** to the declared value, not merely present | `nd-unfolding/p4_lib.py:961-962` |

**A pre-G-1 receipt has no `bkg_mode`, therefore FAILS the gate, therefore is DELETED AND RE-RUN.**

> ### THE GATE CAST AS THE TRAP IS THE REPAIR MECHANISM.

The cost of a pre-G-1 stage 3 is **compute, not irreversibility**. The deletion freeze never applied
either: the `rm -f` is the launcher's own, operating on scratch, not on a tracked file.

## ORIGIN — and this is the transferable part

**The claim described the PRE-repair-4 skip and was TRUE when written on 2026-08-07.** The gate then was
`[[ -s ROOT && -s RECEIPT ]]` plus a ROOT-key/dimension check. `nd-unfolding/p4_lib.py:784-787` documents
that form and its removal, in the repo's own words:

> *"Before repair-4 the resume path skipped an endpoint on `[[ -s ROOT && -s RECEIPT ]]` plus a
> ROOT-key/dimension check. … so 'resumable' meant 'any nonempty file pair is accepted forever'."*

It was fixed by **`febb9a1`** (2026-08-07, *"Repair-4 defects 2 and 3a/3d: make the resume path
content-validating and bind what was declared"*) — **the same day the claim was written.** The window
between "true" and "false" was hours. Nothing in any of the four documents recorded a dependency on the
launcher's implementation, so nothing prompted a recheck when that implementation changed.

## THE COLLATERAL CLAIM: G-1's location, false on both halves

| half | status | measurement (this session) |
|---|---|---|
| *"code-only"* | **FALSE** | Stage 3 ran on it 2026-08-08 and produced ten ROOTs + ten receipts |
| *"not on the cluster checkout"* | **FALSE** | cluster `HEAD` = `683bdcc`; `git merge-base --is-ancestor 5a4009f HEAD` → **true** |

The cluster working tree carries the wiring live: `run_p4_unfold_std.sh:37` reads `bkg_mode` from
`P4Config`, `:90` passes `--bkg-mode` to the driver.

> **COORDINATE DISCIPLINE, because this finding is about a citation that decayed.** Those two line
> numbers are the **CLUSTER tree's at `683bdcc`**; the same two statements are **`:41` and `:111` at local
> `HEAD`**. The two trees are forked (`OI-74`) and the file has grown between them. **Every other
> `file:line` in this document is local `HEAD`**, which is the tracked canonical code and the right
> referent for a claim about what the chain does. A line number without its tree is `BEN-066`'s decay,
> and it would be a poor finding that reproduced the defect it documents.

## THE MEASURED FACT IT ALL TURNS ON

Read-only on `saul.nersc.gov`, in
`/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/active_universe_5d/standard/unfolds/`:
**ten ROOTs and ten `.done` receipts, all dated 2026-08-08**, each

```
mode      = produced
bkg_mode  = purity
code_rev  = 42268b6dfa2e60a0e4bd491b11ad9b11d0228273
```

Receipt `t` stamps span `2026-08-08T13:41:45Z` → `14:59:03Z`; ROOT mtimes `06:40`–`07:59` local.
`42268b6` **contains** all three relevant commits, each verified by `git merge-base --is-ancestor`:

| commit | date | what | contained in `42268b6` |
|---|---|---|---|
| `5a4009f` | 2026-08-07 | **G-1** — the lane can express a background footing | YES |
| `febb9a1` | 2026-08-07 | the resume gate becomes content-validating | YES |
| `2654731` | 2026-08-08 | the legacy-attest path is **deleted** | YES |

**STAGE 3 RAN, POST-G-1, ON 2026-08-08.** The run is holder allocation **`56495756`** (`gbdt-hold`,
`WorkDir` `/pscratch/sd/j/josephrb/MINERvA-OmniFold`), step **`56495756.0`** (`bash`, `COMPLETED`,
`05:21:46`→`07:59:04`, elapsed `02:37:18`). The allocation shows `TIMEOUT` at `08:21:46` — that is the
**holder** expiring after the work finished, four seconds after the last receipt was stamped, not a
failed unfold. **Reading the allocation's `TIMEOUT` as a failed stage 3 would be the next misread
available here, so it is written down.**

`mode=produced` also refutes a third claim (`P4_STANDARD_STATUS.md`): that *"stage 3 legacy-attests with
no re-unfold."* There is no such path to take — `2654731` deleted it, and `run_p4_unfold_std.sh:85-103`
retains the reasoning. The ten ROOTs were **re-unfolded**.

---

## THE PROPAGATION — five live carriers, not the three first reported

| # | file | what it carried | disposition |
|---|---|---|---|
| 1 | `nd-unfolding/active_universe_5d/standard/P4_STANDARD_STATUS.md` | **five** stale counts (`:38`, and the 2026-08-07 addendum: G-1 not on cluster, legacy-attests, stage 3 not run, launcher skips on existence, zero `.done`) + a sixth in the Unfold bullet | struck in place, superseded text retained |
| 2 | `docs/orchestration/RUNBOOK-20260807-gbdt-closeout.md:38` | both preconditions, verbatim | struck in place |
| 3 | `docs/orchestration/DECISION-20260815-joseph-oi6-oi8-oi126.md` | the `OI-8` precondition **and** its verbatim restatement in the `OI-6` section | struck; `OI-8` reissued IN FORCE on a corrected basis |
| 4 | `nd-unfolding/ND_OMNIFOLD_RUN_LOG.md:3614`, `:5705-5706` | *"Stage 3 was deliberately NOT run"* + the two preconditions | **append-only: correction APPENDED, originals left standing** |
| 5 | `docs/OPEN_ITEMS-ARCHIVE-2026-08.md:179` | the same claim | ARCHIVAL — left as-is by retention convention |

Also present in four `runs/standard-p4-verifier/*-transcript.txt` files. **Those are MACHINE records of
what a verifier was shown and are deliberately not edited** — but they are worth noting, because *the
verifier read the false claim too*, in two separate rounds.

**The RUN_LOG is the instructive one.** Its entries were **correct as chronology** — they faithfully record
what the lane believed and decided on 2026-08-07 — and are **false as present-tense fact**. An append-only
log cannot go stale by being wrong; it goes stale by being *read as current*. Rewriting `:3614` would have
destroyed the evidence that the belief was once reasonable, which is the whole content of this finding.

---

## WHY IT WAS CAUGHT — the mechanism, and it was not a lane's initiative

**Joseph's grant on `OI-8` was conditional:** *"go ahead with it if anyone else agrees with you."* The
mediator recorded the condition honestly, named the exact claim as unverified, marked the asymmetry, and
**assigned the check to a lane that did not author the ruling.** That check refuted it.

**The corroborator returned AGREED-WITH-CORRECTION**: it agreed with the *disposition* (the G-1
cluster-landing request is dead) while *refuting the basis*. **Agreement on a disposition is not agreement
with the reasoning that reached it, and here the two came apart.** A corroboration protocol that recorded
only *"agreed / not agreed"* would have logged this as clean agreement and preserved the false premise
inside a now-in-force ruling.

**So the load-bearing safeguard was the PRINCIPAL'S requirement, not any lane's diligence** — and this is
the second time in as many days that a required non-author check has been the only thing standing between
a plausible claim and a ruling. `BEN-300`'s rule (consensus among restatements of one source is not
corroboration) is what made the mediator refuse its own confidence here; it worked.

---

## RULES

1. **A claim about what code does is a claim with a shelf life, and its expiry is invisible from the
   document that carries it.** When you write one, cite `file:line` — not because the reader needs the
   pointer, but because **a citation is the only form of the claim that a future reader can cheaply
   falsify.** Every copy of this claim was prose; none named the gate it described.
2. **Prefer the executable form** (`CLAUDE.md`). *"The launcher skips on receipt existence"* was a
   testable proposition for its entire false lifetime. One test asserting *"a receipt lacking `bkg_mode`
   is rejected and re-run"* would have gone red on 2026-08-07 and stayed red. **Such a test now exists in
   substance** — `p4_lib.validate_endpoint_receipt` is exercised by `tests/test_p4_repair.py` — which is
   why the claim's falseness was cheap to establish and expensive only to *notice*.
3. **A copied claim inherits the original's evidence, not the copier's confidence** (`BEN-082`). Restated
   here because this instance adds a wrinkle: **the original's evidence was GOOD. It just expired.** The
   `BEN-082` shape usually implies the source was weak; here the source was strong and *dated*.
4. **When corroboration is required, record WHAT was corroborated — disposition or basis — separately.**
   A single agree/disagree bit cannot express AGREED-WITH-CORRECTION, and that is the verdict that saved
   this ruling.
5. **Do not infer authorization from artifact quality.** See the escalation below. A correct receipt
   attests to provenance; **it says nothing whatever about permission.**

---

## TWO THINGS THIS FINDING DELIBERATELY DOES NOT RESOLVE — `OI-75`

Both are escalated to Joseph. **Recorded plainly, not adjudicated and not excused.**

1. **THE 2026-08-08 RUN IS UNRECONCILED WITH A STANDING HOLD.** `P4_STANDARD_STATUS.md:4` records
   Joseph's hold — scope *"code/tests/receipts only — **no cluster P4 run**"* — and **there was no record
   of the 2026-08-08 run anywhere in this repo** before this correction. **Whether it was authorized is
   Joseph's question. It is already put to him and unanswered.** This lane takes no position, and neither
   this finding nor the RUN_LOG entry it landed beside may be read as retroactive authorization.
2. **THE TEN PRODUCTS ARE UNTRACKED AND EXIST ONLY ON PURGEABLE SCRATCH.** `git ls-files` over that
   directory returns **0** on both the cluster and local checkouts; `git status --ignored` marks every
   ROOT `!!`. By this repo's own rule — *a result does not exist until its commit lands* — **they do not
   exist, and that is exactly why five documents said stage 3 never ran.** The products total **4.8 MB**
   (ten ROOTs at ~480 KB each), **not** the ~20 GB an earlier relay of this escalation assumed — the
   53.8 GB × 10 figure in `p4_lib.py:790` describes the **merged inputs**, not these outputs. The size is
   recorded to keep the disposition honest and **is not a recommendation to commit them**: that is a
   provenance and authorization decision blocked on item 1, not a storage decision.

**Nothing here clears a gate.** The `standard-p4-verifier` `BLOCK` (14 defects outstanding,
`authorizes_covariance_stages_4_6: False`) and the "NOT BUILT" status of the standard 5D lateral are
**unaffected**. This finding corrects what is true about G-1 and stage 3 and nothing else.

---

## Cross-references

- `docs/orchestration/FINDINGS.md` — `BEN-352` row.
- `docs/orchestration/DECISION-20260815-joseph-oi6-oi8-oi126.md` — `OI-8`, now IN FORCE on the corrected basis.
- `docs/OPEN_ITEMS.md` — `OI-8` (closed), `OI-75` (the two escalations).
- `nd-unfolding/ND_OMNIFOLD_RUN_LOG.md` — 2026-08-15 appended entry.
- `BEN-082` (a relayed claim inherits the original's evidence), `BEN-300` (restatements are not
  corroboration), `BEN-066` (references decay silently).

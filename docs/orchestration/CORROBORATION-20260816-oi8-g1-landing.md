# CORROBORATION — `OI-8` / the G-1 cluster-landing ruling

**Requested by the mediator under Joseph's condition on `OI-8`** — *"Okay your recommendation sounds good,
go ahead with it if anyone else agrees with you."* The mediator authored the ruling being checked
(`361d83e`, `DECISION-20260815-joseph-oi6-oi8-oi126.md`) and asked explicitly for a refutation attempt
rather than a confirmation, on `BEN-300` grounds. Checked by peer session `B`, 2026-08-16.

**Every number and quotation below is from a command run in the checking session**, against
`origin/main` and against the cluster tree read-only.

---

## VERDICT: **AGREE-WITH-CORRECTION**

**The ruling's conclusion is right and I corroborate it: the G-1 cluster-landing request is DEAD AS
SUPERSEDED.** Joseph's condition is met on the conclusion.

**But three of its supporting statements are false, and the precondition it leaves standing is
over-strict because its stated mechanism does not exist.** The conclusion survives on a *different and
stronger* basis than the one given.

---

## 1. THE LOAD-BEARING CLAIM IS FALSE — the launcher does NOT skip on receipt existence

The claim under test, as the mediator posed it: *"the stage-3 launcher SKIPS endpoints that already carry
a `bkg_mode` receipt."* The runbook's own wording (`RUNBOOK-20260807-gbdt-closeout.md:38`) is *"it writes
ten receipts with no `bkg_mode`, the launcher skips endpoints that already have one"*.

**Measured in the code. The skip is CONTENT-VALIDATING, and a receipt that fails validation is deleted and
the endpoint re-run.** `nd-unfolding/run_p4_unfold_std.sh:73-84`:

```bash
  # D2a: the skip is now CONTENT-validating. A ROOT plus any nonempty .done used to be enough;
  # the gate below re-derives root/central/config/bkg_mode identities live, compares the merged
  # sha against the orchestrator receipt, and (PB2) re-derives the producing closure and compares
  # every member's blob. A reject falls through and re-runs the endpoint.
  if [[ -s "${OUT}" && -s "${REC}" ]] && valid_root "${OUT}"; then
    if RCHK=$(python3 p4_check_receipt.py --receipt "${REC}" --tag "${tag}" \
                --root "${OUT}" --merged "${MERGED}" 2>&1); then
      echo "[unfold] SKIP ${tag} (receipt validated)"; return 0
    fi
    echo "[unfold] STALE ${tag} -> re-running: ${RCHK}"
    rm -f "${REC}"                       # D2: never leave a stale ROOT/receipt pair behind
  fi
```

**And a receipt without `bkg_mode` cannot validate.** `nd-unfolding/p4_lib.py:796-797`:

```python
RECEIPT_REQUIRED_KEYS = ("tag", "mode", "root_sha256", "merged_sha256", "central5d_sha256",
                         "config_hash", "bkg_mode", "code_rev", "unfold_blob", "t")
```

`nd-unfolding/p4_lib.py:949-950`, which runs before any value comparison:

```python
    missing = [k for k in RECEIPT_REQUIRED_KEYS if k not in rec]
    require(not missing, f"receipt {tag} missing required keys {missing} (incomplete legacy format)")
```

and `:961-962` for the value itself:

```python
    require(rec["bkg_mode"] == bkg_mode,
            f"receipt {tag} bkg_mode {rec['bkg_mode']!r} != declared {bkg_mode!r}")
```

`p4_check_receipt.py:105-113` passes `bkg_mode=cfg.bkg_mode` into that validator, and on any
`P4GateError` prints `RECEIPT-REJECT ::` and `sys.exit(1)` (`:122`, with `:124` catching anything
unexpected so it can never read as PASS) — the non-zero exit the launcher's `if` treats as a reject.

**And the checker's own docstring states the conclusion outright**, `p4_check_receipt.py:6`:

> *"otherwise print `RECEIPT-REJECT :: <reason>` and exit 1, **which makes the launcher re-run**"*

So this is not a subtle reading of the control flow — **the script says what it does, and it is the
opposite of the runbook's characterisation of it.**

**Chain, end to end: a pre-G-1 receipt lacking `bkg_mode` → `missing required keys ['bkg_mode']` →
`P4GateError` → `RECEIPT-REJECT` → exit 1 → launcher prints `STALE … -> re-running`, deletes the receipt,
and re-produces the endpoint.**

**So the hazard is self-repairing, not unfixable.** The "unfixable provenance regression" rests on a skip
behaviour the launcher does not have. Note also that the launcher **deletes the stale receipt itself**
(`rm -f "${REC}"`), so the frozen-deletions policy does not trap the bad receipt either — the repair path
does not require anyone to delete anything by hand.

**One thing this does NOT overturn:** the current launcher also *stamps* `bkg_mode` into every receipt it
writes (`run_p4_unfold_std.sh:119-120`, and `:41` aborts if it cannot resolve the value), so in the
current tree stage 3 cannot produce a `bkg_mode`-less receipt in the first place. The hazard needs a
pre-G-1 tree to arise at all — and §2 shows there isn't one.

## 2. "G-1 is code-only and not on the cluster checkout" IS FALSE — it is committed there

This claim appears in the ruling (*"G-1 is code-only and not on the cluster checkout"*) and in the
runbook precondition it preserves. Measured on the cluster tree this session:

```
cluster HEAD                                  683bdccad5a94d13ef231bf0729758085634a178
cluster HEAD date                             2026-08-11T08:01:25-04:00
git show HEAD:nd-unfolding/p4_lib.py     -> bkg_mode in RECEIPT_REQUIRED_KEYS : yes
git show HEAD:nd-unfolding/p4_evidence.py -> "footing evidence (G-1)" block    : present
git status --porcelain -- p4_lib.py p4_evidence.py run_p4_unfold_std.sh : EMPTY (none dirty)
```

**G-1 is present in the cluster checkout, as a committed change, in a clean state for all three relevant
files.** It is not code-only and it is not absent.

**This makes the ruling's conclusion stronger than its argument.** The mediator's basis is that zero
unique cluster commits leave *nothing to land*. The measurement says something better: **the landing
already happened, on or before 2026-08-11.** The archived form of the item (`OPEN_ITEMS-ARCHIVE-2026-08.md:172`)
was *"Waiting on Joseph — how the G-1 footing patch reaches the cluster checkout"*; it reached it by
ordinary means while the question sat open.

## 3. The fork receipt's ancestry claim SURVIVES re-measurement — with one drift

`state/cluster-local-fork-freeze-20260812.json` is dated `2026-08-12T05:38:24Z`. Re-measured against
`origin/main` after `git fetch`:

| claim | receipt | measured 2026-08-16 |
|---|---|---|
| cluster HEAD is a strict ancestor of `origin/main` | `true` | **true** |
| commits cluster ahead of `origin/main` | `0` | **0** |
| uncommitted paths in the cluster tree | `751` | **754** |
| commits `origin/main` ahead of cluster | — | **646** |

**The two load-bearing numbers hold.** The dirty-path count has drifted `751 → 754`, which does not touch
the ancestry argument but does mean the receipt is four days stale on that field; anyone quoting `751`
should re-derive it (`OI-74` already owns that tree's reconciliation).

## 4. Nothing other than stage 3 depends on G-1 landing

Searched every `G-1` reference in the tracked documentation. They are: the runbook's own specification of
G-1 (`:214`, `:218`, `:242`, `:259`), `OI-8` itself, the archived landing item, and
`REPAIR4-DEFECT-STATUS-20260807.md:74,108` — which records that **G-1 added `bkg_mode` only and repaired
none of the six defects**, so the standard-5D lateral component stays BLOCKED on the never-made repair-4
regardless of anything here. **No consumer depends on a G-1 *landing action*.** The mediator's finding is
confirmed, and I looked for counterexamples rather than for confirmation.

## 5. What the precondition should say instead

As written — *"no standard-P4 stage-3 run from a tree that does not contain G-1"* — the precondition is
**over-strict and justified by a mechanism that does not exist.** Two corrections, and the second matters
more than the first:

1. **The irreversibility is false.** A `bkg_mode`-less receipt is rejected, deleted and re-run by the
   launcher's own content-validating skip. Any such regression repairs itself on the next stage-3 pass.
2. **The precondition is unreachable anyway**, because both `origin/main` and the cluster checkout contain
   G-1, and the launcher aborts (`:41`) rather than run without a resolvable `bkg_mode`. There is no tree
   in play from which a pre-G-1 stage 3 could be launched.

**Recommended replacement, if anything is kept at all:** *stage 3 must run from a tree whose
`RECEIPT_REQUIRED_KEYS` contains `bkg_mode`* — which is **machine-checkable in one grep**, is already true
everywhere, and states the property that actually matters instead of a repository-landing event. That is
also the form the campaign's own convention prefers: **the executable form of a rule over the prose
form.** Retaining the prose precondition costs a future lane a blocked stage 3 for a hazard that cannot
occur.

---

## What this corroboration does and does not settle

**Settles:** the conclusion — the G-1 landing request is dead. Joseph's *"if anyone else agrees"* condition
is met **on the conclusion**, and I say so plainly rather than hedging.

**Does not settle, and is flagged rather than decided:** whether the surviving precondition should be
rewritten, dropped, or converted to the one-grep check in §5. That edits a runbook this lane does not own,
and it is the mediator's and the standard-P4 owner's call. **The ruling as committed contains three false
supporting statements** (§1's skip mechanism, §2's cluster-checkout claim, and the irreversibility that
follows from §1), and those should be corrected in place whatever is decided about the precondition —
otherwise the next reader inherits the same reasoning.

**Not checked:** whether stage 3 is otherwise ready to run. The standard-5D lateral remains BLOCKED on
repair-4 per `REPAIR4-DEFECT-STATUS-20260807.md`, which is independent of everything above and unaffected
by this verdict.

> **FIXED 2026-09-23** at `b6b19496`: the shared pre-commit hook runs the guard as a warning whenever the report is staged. The body below records the state before this fix.

# ISSUE-71 — Nothing runs the loop-ledger guard on the live ledger automatically (its mutation suite runs it on copies; its runner is run by hand), so its docstring's central claim about itself is not yet true

**Severity:** MEDIUM. **Status:** FIXED (2026-09-23). **Index row:** `KNOWN_ISSUES.md` row 71. **Updated:** 2026-09-23.

Moved here from the index on 2026-09-22 (self-round 52), text unchanged, because `KNOWN_ISSUES.md`
is an index and not a copy: its own header says so, it was compacted to 8,720 B at `1f714b7f` to
obey that, and this lane had grown it from 65,681 B (at `177af61b`) to 96,816 B, almost all of it in these thirteen rows.

## Detail

`probes/probe-20260922-ledger-reconciles.py` says *"the totals are no longer defended by care; they are defended by this check"*. Measured: `grep -rn 'probe-20260922-ledger-reconciles'` outside the three documents that mention it returns **nothing**, and it is absent from `.githooks/pre-commit`. **A check nothing invokes is still defended by someone remembering to run it** — the catalogued *a check with no caller* shape (`OI-148`). Its only automated caller is its own mutation suite (`probe-20260922-ledger-guard-mutations.py`), which exercises it but does not guard the live ledger. **NOT WIRED UP HERE, DELIBERATELY, AND THIS IS A JUDGEMENT CALL A LATER LANE MAY OVERRIDE:** the natural caller is the shared `.githooks/pre-commit`, which **other live sessions run on every commit in this same checkout**. A new failing check there would block peers' commits for a defect in a document they do not own, and the guard refuses (exit 2) on shapes that are legitimate mid-edit. Adding it is a change to shared infrastructure with a blast radius beyond this lane, so it is recorded rather than made. **CHECK:** run the guard and its suite by hand after any ledger edit — or wire it in as a **warning**, not a refusal, if a later lane decides the shared hook is the right home.

**Update 2026-09-23.** The guard now has a TRACKED caller besides its own suite: `probes/probe-20260922-seven-gates.sh`, which this lane runs before every commit. That is still a caller run by hand, not by the shared pre-commit hook, so this issue's substance — nothing runs the guard automatically — stands. ⚠ The title said *"has no caller"* until self-round 77, which has been false since the runner was committed; round 77's *"no AUTOMATIC caller (only a runner run by hand)"* then left out the mutation suite, which runs it automatically but on copies (review #19a).

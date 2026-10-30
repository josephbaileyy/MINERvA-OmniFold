# DECISION 2026-10-30 (later) — Joseph: the two paper pairs, the abstract χ² split (A4) and the Data Availability reorder (A1), are approved

**Recorded by** the paper-tighten lane, as director.

**What led to it.** `DECISION-20261030-joseph-r22-protected-gaps.md` item 1 allowed sol2's A1 and A4 gaps, provided
each came to Joseph as a pinned before/after pair before adoption. The paper rewrite lane pinned two pairs for
`main_paper.tex`, each pin being `sha256(before + NUL + after)[:16]`:
- **G1:paper-s-06 (A4, the abstract's χ² sentence),** pin `bbb99991e62f584b`. The after-text is byte-identical to the
  note-abstract split Joseph approved in #536.
- **G1:paper-s-09 (A1, the Data Availability package sentence),** pin `083bfb80f9fac8fd`. It is a reordering that keeps
  "candidate", "not yet deposited", the 16 MB figure and the three dependencies.

The director put each after-text to Joseph in full. On the DA reorder, the director recommended keeping the original,
as a weak register change to protected text. Joseph chose otherwise.

On the abstract χ² sentence, Joseph's answer, verbatim:

> Approve (Recommended)

sha256 of the text plus a final newline begins `b012841bf16cb4da`.

On the Data Availability sentence, Joseph's answer, verbatim:

> Approve the reorder

sha256 of the text plus a final newline begins `a3fb2eeab356e768`.

## What is decided

1. **Both pairs are approved exactly as pinned.** The lane applies them through `PAIRS` / `PAIR_PINS`, so that
   `main_paper.tex` may differ from the base by exactly these two pairs.
2. **The paper with both pairs is judged again** under the paper round's pre-committed rule, with a fresh pairwise and
   P1. If that judgement fails, the pairs are not adopted.
3. `\pubhold` and the rest of Data Availability are unchanged.

## Not changed

- Every number and claim. Nothing is submitted, deposited or tagged.

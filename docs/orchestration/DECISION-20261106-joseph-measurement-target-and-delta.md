# DECISION 2026-11-06 — Joseph: aim for the measurement paper, with the methods study as the stated fallback; NCSA Delta available for compute

**Recorded by** the paper-tighten lane, as director.

## What led to it

A message relayed from the Grok session reached the director, attributed to Joseph: "Keep the paper a measurement. Do
not draft the scope package as a methods study…", and noting NCSA Delta. A peer's relay is not Joseph's decision, so
the director asked him directly. Separately, the interpreter session asked him in its own terminal.

## Joseph's answers, verbatim

To the director, asked whether the relayed text was his ruling, with three options (yes; not decided yet; keep
measurement but show methods as fallback):

> Keep measurement, but show methods as fallback

sha256 of the text plus a final newline begins `0eec4534d13c6c5d`.

To the interpreter session, relayed verbatim to the director:

> yes thats mine, I mean what I really am trying to say is we really want to go for the measurement paper if possible and we can use NCSA Delta for any compute if necessary honestly, just think about efficiency and getting things done

sha256 of the text plus a final newline begins `075f2bc3724a7420`.

## What is decided

1. **The target is the measurement paper, if possible.**
   - The scope-decision package (OI-205) prepares the measurement options as primary: (A) as now framed, and (B)
     narrowed.
   - The methods study (C) is set out as the stated fallback, for the case where the measurement's conditions fail.
   - The decision itself still comes to Joseph once the coverage readouts are on main.
2. **The campaigns close as fast as their bound sequences allow.** Efficiency is the operating priority.
3. **NCSA Delta is available for compute "if necessary".** The director's operational reading:
   - **COV2D and 1B stay on Perlmutter.** Their bindings pin Perlmutter's environment: QOS `regular_1`, `showquota`,
     the CFS inputs, the root_6_28 and MAT environments, and the atime guards. Moving either would need a new binding
     and new tests. For COV2D, any new failure would risk the third STOP. Moving would cost time, not save it.
   - **Delta is the default for new compute outside those bindings,** where its inputs can be staged there. Examples:
     a later study, or a campaign whose Perlmutter queue is the bottleneck. Each such use is priced and bound like any
     other. Delta needs its own environment and access, and no lane has set those up yet. The director will ask Joseph
     when a concrete use arises.

Nothing is submitted, deposited or tagged.

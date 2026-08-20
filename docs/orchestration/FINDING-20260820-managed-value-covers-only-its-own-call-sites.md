# FINDING 2026-08-20 — a managed-value discipline covers only the call sites that go through the manager

**`BEN-491`.** Nominated by lane B; the mechanism was reached independently by lane C from the
`petClosure` side and the executable form is lane D's.

## The mechanism

Marking a value as retracted *at its macro* protects every site that expands that macro and nothing
else. The same number written as a literal is unprotected, and — the part that makes it survive — it
is **invisible to a sweep that searches macro names**. So the discipline reports containment while the
bypasses are exactly the sites it cannot see.

## Three sightings in two days, each in a different file

1. **`\petRatio`'s operands**, documented inside `INDEX-retracted-and-superseded-values.md` itself.
2. **`paper_body.tex:146`** printed `\SI{9}{\percent}` as an inline literal while `values.tex:74`
   defines `\petGbdtGap` = 9 marked *"niter=2 LEGACY, struck at use"*. `grep petGbdtGap
   paper_body.tex` returned **nothing**, so strike-at-use could not reach it. Worse, the note's figure
   is a **range**, `\dead{6.5-9.9%}`, so the single `9` was the **top of a struck range quoted as a
   level of agreement**.
3. **`sec_systematics.tex:174-177`**'s `0.28` / `0.09` / `0.18` derived comparisons — in the very
   block whose four macros were struck. `PROCEDURE-gbdtFive-macro-update.md` calls them *"a derived
   comparison against the old products"* and warns that because they are inline literals *"a
   macro-only edit leaves it stale and silently attached to superseded inputs"*.

## Two wrinkles that matter for prediction

**Instance 2 is COMPOSITE** — macro-versus-literal stacked on the document-boundary mechanism — which
is why it reached an **external** build while the others did not. A predictor modelling only the pure
form underranks it.

**Instance 3's bypassed value CHANGED after the procedure named it.** `d75833ab` moved `0.30` to
`0.28` on 2026-08-12, after the 2026-08-11 procedure. So `PROCEDURE:165`'s instruction to *"handle
0.30% at :171-172 explicitly"* **is now unfollowable and fails silently**: an editor greps, finds
nothing, and reads the null as already-handled. A remediation procedure decayed into an instruction
whose failure looks like success, by the exact mechanism it was written to warn about.

## The form first proposed was unrunnable, and lane D refused it

*"A legacy sweep must search VALUES, not macro names"* **cannot be executed.** You cannot search for
the values of a legacy set unless you already know them, and if you knew them you would already have
found the bypasses. It states the answer, not a procedure.

**EXECUTABLE FORM.** Seed from the retraction index's **value list** — the artifact that already holds
them — grep each value across the corpus, and **subtract** the sites that resolve through its macro.
The remainder is the bypass set. A set difference, runnable today, with a natural negative control:
**an empty bypass set is genuine containment.**

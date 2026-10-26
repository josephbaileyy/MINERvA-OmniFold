# Records: R-EDIT ledger rows for verified record-paragraph edits (2026-10-26)

**Lane:** paper rewrite, for the director.

**Base:** origin/main `b6bca37f`; main `703ffcce` (#379, #381, #380) merged in.

**What this is.** A change to `docs/analysis-note/check_note_records.py`, the records-move checker. Its probe P5
required every base RECORD paragraph to print verbatim in the records closure, with no exception. A record paragraph
can now change in its pointer tokens, and only in them, under a ledger row that names the old and the new text by
digest. No record, note or ledger text changes in this PR.

## Authority

The director's ruling of 2026-10-26, on the conflict between the `rvp1pi` pointer edit and P5. The message is quoted
here as received, for the part that governs this PR:

> Director ruling on the rvp1pi/P5 conflict: (b), the R-EDIT mechanism, in its own PR before n2 starts. Not (a), not
> (c).
>
> **Why not (a).** Joseph's standing rule (2026-09-23) is "fix it now and not wait for a future point". When the only
> blocker is pin or proof cost, do the fix and the re-pin together, with a record. "Fix in n2" is that kind of
> deferral. The PDF not being posted doesn't make the pointer less wrong. (c) weakens the no-loss proof; I agree it's
> out.
>
> **Sequencing.**
> 1. n1's register PR goes as you have it: records untouched, scored on its own. Don't hold n1 for this.
> 2. Next PR, "records: R-EDIT ledger rows for verified record-paragraph edits":
>    - **Rows.** An R-EDIT row carries:
>      - the base paragraph's sha256 (it must equal the frozen inventory entry);
>      - the sha256 of the exact new text;
>      - the reason;
>      - the authority: cite this ruling, transcribed in the PR's record with my message quoted.
>    - **P5 rule.** P5 accepts a base record paragraph only if one of these holds:
>      - it is verbatim;
>      - an R-EDIT row's old hash equals the base entry and the closure holds exactly the row's new text.
>    - **Scope.** R-EDIT is limited to cross-reference and pointer tokens. The checker diffs old against new and fails
>      if anything other than `\ref`/`\S`/section-number tokens changed. Without this, R-EDIT becomes a general
>      escape hatch from the no-loss proof.
>    - **Self-tests, as planted defects.** Each must fire, or for the two control cases stay silent, and the harness
>      prints which:
>      - an unrecorded edit fails;
>      - a recorded pointer edit passes (control);
>      - a wrong old hash fails;
>      - new text that differs from the row's hash fails;
>      - a recorded edit that changes a non-pointer word fails;
>      - a deleted paragraph with an R-EDIT row still fails as a loss;
>      - an R-EDIT row whose base paragraph is unchanged fails as stale.
>    - **The edit.** Apply the rvp1pi edit (§4.4 → `\S\ref{sec:uq-2d-scope}`) with its row, from your saved copy.
>    - **Before opening the PR,** all four modes must pass: probe, --self-test with the new counts, pin and
>      --self-test-pin. Then agy agreement on the one printed cell.

An R-EDIT row's authority cell cites this file.

## The rule as built

**The row.** It goes in `records-move-ledger.md`:

```
| R-EDIT-<n> | <old sha256> | <new sha256> | <reason> | <authority> |
```

Each sha256 is the digest of a paragraph as P5 reads it: printed text, comments removed, whitespace collapsed.
`check_note_records.py redit-digest <file.tex>` prints every paragraph's digest.

**What P5 checks.** It accepts the base paragraph whose digest is `<old>` only if all of these hold, and each failure
names its row:
1. `<old>` is the digest of a RECORD paragraph of the frozen inventory (`records-inventory-base.json`). Otherwise it
   fails: "old digest … is the digest of no base RECORD paragraph".
2. That paragraph no longer prints verbatim in the records. Otherwise it fails as **stale**.
3. A records paragraph has the digest `<new>`. Otherwise:
   - if a paragraph exists that differs from the base only in pointer tokens, it fails as "the edited paragraph is
     not the row's new text";
   - if no such paragraph exists, it fails as **lost**.
4. With every pointer token masked, the old and new paragraphs are identical. Otherwise it fails as "the edit changes
   more than pointer tokens", and names the first differing words.
5. The two paragraphs have the same number of pointer tokens in each class: section signs (`\S`, `\S\S`); references
   (`\ref`, `\ref*`, `\nsec`, `\napp`); section numbers. Otherwise it fails as "the edit deletes or adds pointer
   tokens", and names each class's counts. An edit retargets a pointer; it never deletes or adds one. Without this
   rule, masking alone would let a recorded edit delete a pointer, which is a loss of record content.

Reason and authority must not be empty. A malformed row fails.

**Pointer tokens:**
- `\S`, `\S\S`, but never the start of `\SI` or `\SIrange` (the pattern requires no letter to follow);
- `\ref{…}`, `\ref*{…}`, `\nsec{…}`, `\napp{…}`;
- a section number written after a section sign (`§ 4.4`).

A bare number is deliberately not a pointer token. A pattern matching any dotted number would also mask a value such
as `4.502`, and would let a recorded change of a printed value pass as a pointer edit. The "recorded number change" case below
tests exactly that.

## Self-test

`check_note_records.py --self-test docs/analysis-note/records-inventory-base.json docs/analysis-note`, rc 0:

```
  fired  unrecorded pointer edit              -> P5 RECORD paragraph not verbatim in the records closure: '\\paragraph{From \\S\\ref{sec:invert}, ran
  silent recorded pointer edit (control)      -> no failure
  fired  R-EDIT row with a wrong old digest   -> P5 R-EDIT row R-EDIT-90: old digest 000000000000 is the digest of no base RECORD paragraph
  fired  R-EDIT new text not the row's        -> P5 R-EDIT row R-EDIT-90: the edited paragraph is not the row's new text: its digest is b95dbb4f1599,
  fired  recorded word change                 -> P5 R-EDIT row R-EDIT-90: the edit changes more than pointer tokens: 'deficiency at $N\\le n$.} After
  fired  recorded number change               -> P5 R-EDIT row R-EDIT-90: the edit changes more than pointer tokens: '($N=50$ replicas, $n=205$ bins)
  fired  recorded pointer deletion            -> P5 R-EDIT row R-EDIT-90: the edit deletes or adds pointer tokens: reference 1 -> 0, section sign 1 -
  fired  recorded pointer insertion           -> P5 R-EDIT row R-EDIT-90: the edit deletes or adds pointer tokens: reference 1 -> 2, section sign 1 -
  fired  deleted paragraph with a row         -> P5 R-EDIT row R-EDIT-90: base paragraph 7447daa4e5ad is lost: no records paragraph has the row's new
  fired  R-EDIT row, paragraph unchanged      -> P5 R-EDIT row R-EDIT-90: stale: base paragraph 7447daa4e5ad still prints verbatim in the records: '\
RECORDS-MOVE SELF-TEST :: PASS (delivered move silent: True; 30 of 30 planted defects fired their probe; 3 of 3 listed drops and recorded pointer edits stayed silent)
```

**What the cases are.**
- The planted cases all act on one record paragraph: `app_history.tex:148`, "From \S\ref{sec:invert}, rank
  deficiency at $N\le n$".
- Each planted row's digests are computed from the frozen inventory, so they are those of the real base paragraph.

**The counts before and after.** Before this change the self-test had 21 of 21 planted defects and 2 of 2 silent
cases. It now has 30 of 30 and 3 of 3:
- the director's seven cases;
- one number-change case, beyond the seven;
- a recorded pointer deletion and a recorded pointer insertion, added at the director's review of this PR. Each fires
  on the count rule (rule 5), not on the masked comparison.

**Why the control matters.** It is the only case that exercises the acceptance path. If `redit_accepted` accepted
nothing, the control would fire P5 and the self-test would fail.

## The four modes, at this commit

| mode | result |
|---|---|
| `probe docs/analysis-note/records-inventory-base.json docs/analysis-note` | RECORDS-MOVE :: PASS |
| `--self-test …` | PASS: 30 of 30 fired, 3 of 3 silent |
| `pin` | RECORDS-PIN :: PASS |
| `--self-test-pin` | PASS, 9 of 9 |

## The rvp1pi edit: not in this PR, and why

The tracker row's pointer has to follow the Rvn1pi/Rvp1pi account.
- **On main** (`b6bca37f`), that account still prints under `sec:uq-2d-construction`, at `sec_systematics.tex:232-235`.
- **In note register round n1**, which is not yet merged, it moves to `sec:uq-2d-scope`.

So the edit to `\S\ref{sec:uq-2d-scope}` is true only once n1 is on main. If it merged first, the records would
point at the wrong section. A note in a PR saying "merge after n1" is not a hold anything enforces, so the edit is
left out here. The mechanism has no ordering hazard and can merge at any time.

**The follow-up** lands when n1 is merged:
- one commit with the edit, from the saved copy;
- its row:

  ```
  | R-EDIT-1 | de3e8f2f96e0d5a1a630fca2cd5962eb89060915bf6604bb77538164df87520d | 8c9ed3d73e270f129bed3ba965dc669ccacaa83ccc85407bedce05ddb5770c28 | rvp1pi tracker row: the Rvn1pi/Rvp1pi account prints at sec:uq-2d-scope since note round n1 | director ruling 2026-10-26, quoted in methods/records-redit-20261026/REPORT.md |
  ```

- the four modes;
- agy on the printed cell.

**Forward check, already run.** This checker was copied into n1's note tree (`080ca790`), and the edit applied there.
- Without the row, P5 fails.
- With the row, probe reports 0 failures (verdict SKIP only because the copy is outside git, so P8 cannot run).
- The edited `app_provenance.tex` is byte-identical to the saved copy.
- The two digests above are those of the base paragraph and of the edited one. With pointers masked, the two are
  identical, and the only token difference is `\S\ref{sec:uq-2d-construction}` → `\S\ref{sec:uq-2d-scope}`.

# DECISION 2026-10-31 (later) — Joseph: OI-151, the laptop is not a usage host (option C)

**Recorded by** the paper-tighten lane, as director.

**What led to it.** OI-151: `usagectl`'s home validator refuses this laptop's symlinked codex homes, for example
`~/codex-homes/school` → `~/.codex-school`. The options were:
- (B) invert the links, which moves Joseph's credential directories by hand;
- (C) accept that the laptop is not a usage host. Perlmutter's login nodes read quota, and the Mac's live-state render
  already says NOT ASSESSABLE (#476).

The director recommended (C), and explained both options to Joseph on 2026-10-31.

Joseph's words, verbatim, in his own message:

> OI-151 lets do (C)

sha256 of the text plus a final newline begins `700fb1a3df8c6af9`.

## What is decided

1. **Option C.** The laptop is not a usage host. Quota is read on a Perlmutter login node. The validator, `profiles.json`
   and every credential directory stay as they are.
2. **OI-151 is retired** by the close-items session, citing this record.

## Not changed

- Every credential directory, `profiles.json` and `usagectl`. Nothing is submitted, deposited or tagged.

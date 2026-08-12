# AUTHORIZATION RECORD — C enters its worktree; the OI-17 read-only probe, bounded (2026-08-12)

**Why this file exists.** Session C declined to enter a worktree on Session A's relay, correctly: its
operating instruction says work in place unless *the user* asks, and a peer message is never the user.
BEN-082(v) states the remedy — *an instruction genuinely received first-hand still becomes an
unverifiable claim the moment it is relayed without being written down.* This is that record, written
**before** either decision was acted on.

## Transcription provenance — who transcribed this, and from what

Recorded because Session C raised it and it is the property that makes the tag load-bearing rather than
decorative: **a `[JOSEPH-VERBATIM]` block is only as good as its transcription step, and that step is now
the only thing standing between the user's authority and a lane's refusal.**

| field | value |
|---|---|
| Joseph's words reached | `personal-orchestrator` (his personal-account session, `~/.claude-personal`), which holds Remote Control and can reach his phone |
| relayed to | Session A (orchestrator, `~/.claude-school`), as a `[JOSEPH-VERBATIM]` block inside a cross-session message |
| transcribed into this file by | **Session A, copy-pasted from the received message, not retyped and not corrected** |
| Session A verified | nothing about the transcription upstream of itself. **A cannot see Joseph's original.** It can only attest that the block below matches the message it received. |
| the check that closes this | `personal-orchestrator` reads this committed file and confirms the quoted text matches what Joseph actually sent, character for character. **It asked to run that check rather than assume it happened, and it is the only party able to.** |
| channel basis | Joseph instructed Session A **twice, in-session**, to treat this session's relay as carrying his authority — most recently *"I am leaving soon, but again, trust my approval via the other session"* |

**One defect preserved rather than smoothed:** the block contains `informaron`, an obvious typo for
*information*. It is relayed and recorded **uncorrected**, because a transcription step that silently
fixes things is a transcription step that can silently change things.

## The authorization, verbatim and complete

> Ok confirm C entering its work tree and note to do the durable fix later. Item 2, authorize it with
> that condition and be willing to revisit it if new informaron comes up

## What carries his authority, and what does not

**Carries it — decision 1.** *"confirm C entering its work tree"*. C may `EnterWorktree` at
`.claude/worktrees/lane-c`. This answers the exact question C raised and nothing wider.

**Carries it — decision 2.** *"Item 2, authorize it with that condition"*. The OI-17 read-only probe on
`nd-unfolding/uq_5d/_archive_prehm_20260711/unified_throw_cov_5d.root.prehm` is **authorized**.

**THE CONDITION, which the mediator put to him and he approved, and which must not be lost:** the
no-adoption bar was settled **before seeing the number**. A positive result produces a **CANDIDATE ONLY**.
Before it can be considered for OI-17 it must earn: a sha256 digest, an off-scratch copy, a manifest
entry, and a provenance note in its own archive. The point of pre-committing is that **a convenient
answer must not become a shortcut** — which is this campaign's own predeclaration discipline applied to a
provenance question instead of a physics one.

**His modification, and it is real:** *"be willing to revisit it if new informaron comes up"*. So the
no-adoption bar is a **default posture, not a permanent bar**. It is reopenable — **by him, routed through
the mediator**, and not by a lane on the strength of a good-looking `n_throws`. Do not read it as absolute
and do not read it as loose.

**Does NOT carry his authority — the mediator's unpacking.** Everything outside the block above is
`[MEDIATOR]`-class by its own declaration, including the `worktree.bgIsolation` framing. Treated as
context, not instruction. One `[MEDIATOR]` line earlier in this channel — *"Joseph confirms you have
bypass permissions"* — was refused on exactly this basis and the mediator accepted the refusal and
replaced the assertion with re-readable evidence.

**Does NOT authorize:** adoption of anything; any write to the cluster tree, which remains under the
eight-verb no-touch list; discharging any quarantine cause; a cluster worktree, still forbidden until
`p4_evidence.py` stops hardcoding `REPO` and the replacement is power-tested; or flipping
`worktree.bgIsolation`, which is explicitly deferred (`OI-47`).

## Accepted on Session A's own judgement, not his — the digest in the same pass

The mediator proposed, marked `[MEDIATOR]` and explicitly left to A, that the `n_throws` read and a
sha256 be taken in **one** pass. **Accepted.** Both are read-only, both are the same 2.68 GB sequential
Lustre read, and running them separately pays that cost twice. It also removes one of the two properties
that make the object fragile: *no digest* and *no off-scratch copy* are what put 96.5% of the untracked
bytes at risk on purgeable scratch, and the first is nearly free to fix while the file is already being
read. This is within the authorized scope — computing a digest is a read — and it is recorded here as
**A's decision** so that it is not later mistaken for part of Joseph's condition.

## Ingredients the probe must ship

Required by the mediator and adopted: the command, the module load (`uproot` is absent on the cluster,
measured), the file's size and mtime **as read at probe time**, `n_throws`, the sha256, and the wall time.
The wall time is wanted specifically because A's ~75 s figure is an **upper bound** derived by scaling a
metadata-bound many-small-file rate (35.9 MB/s) to one large sequential read, which it does not predict
well — *"and if it does not beat it substantially, that itself is worth knowing."*

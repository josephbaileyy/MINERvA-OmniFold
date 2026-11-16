# BINDING 1: RPL, locating the run-period step (director, 2026-11-10)

**Binds** [`RPL-DECLARATION.md`](RPL-DECLARATION.md) (sha256 `705845b534f74565`) and the committed check (iii) record
[`iii/README.md`](iii/README.md) (`dd0cd740d928f396`), as merged in PR #1042 at
**M_RPL = `a1a8b161896f88988d02cabbcaadc13bf50632a7`**. Both are byte-identical at the audited head `30c449f5` and at
M_RPL. The PR's later merge of main, `9ee0205e`, changed only the index files.

**Under** the confirming referee round (`referee-methods-confirm-20261110/claude.txt` M6, :116-123) and Joseph's go on
the paused follow-up work, 2026-11-10.

## What the director checked

- **coverage-5b-audit's three rounds:**
  - revision 1: 2 blocking, 7 major and 7 minor findings;
  - revision 2: B1 and B2 resolved, then R1–R4 and R5–R9;
  - revision 3: "no blocking or major findings remain"; its three minors were folded in at `30c449f5`.
- **The licence is descriptive.** It is not citable for a cause, for which period is right, for C_PL or any result, or
  for coverage. A finding enters the paper only by Joseph's decision.
- **Sequencing protects RPD-RECO's pre-registration.** Check (i)'s fit, check (ii-b) and any data/MC quantity from
  (ii-a)'s joined rows wait for RPD-RECO's d1/d2 record, named by sha256 as precondition P-RPD. limitation-resolver
  confirmed that none of RPL's earlier reads is material to RPD-RECO.
- **(iii) is done** and reads STEP-NOT-MENTIONED. The paper's time- and intensity-dependent treatments are quoted
  separately, as (iii-b), with no outcome.

## Rulings

1. **Before P-RPD,** only these run, each with its scripts' sha256s sent to the director and a go before it runs:
   - (ii-a)'s inventory, at 0 node-h. `rpl_inventory.sh` `b8a9058c` and `rpl_launch.sh` `0e473dc8` are verified, with
     cov2d_fence.sh `16a2a5cd`;
   - (ii-a)'s one-file dry run;
   - (i)'s MC-only band-size read. `rpl_bandsize.sh` `b13c9437` is approved in content; its launcher is reviewed
     separately. It must run well before 2026-12-09, when its inputs become exposed to purge (`AT-RISK.md`, #1048).
2. **Reads:**
   - every read is an O_NOATIME read, with EPERM raised and never retried plainly;
   - cov2d_fence.sh runs before any connect, with no cov2d job queued;
   - nothing is written to CFS;
   - launchers use the detached-remote pattern, with ServerAlive on both hops.
3. **(ii-a)'s job,** if the inventory finds unique keys, is priced by the dry run and needs its own go. If the keys are
   absent or not unique, (ii-a) is reported as not made.
4. **Each result is read once** from its committed record. A failed control means the check is reported as not made.
5. **No data/MC comparison** is formed before P-RPD.

Nothing is submitted, deposited or tagged.

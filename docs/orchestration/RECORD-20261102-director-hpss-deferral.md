# RECORD 2026-11-02 — director: HPSS copies deferred during NERSC's archive maintenance

**By** the paper-tighten lane, as director.

**What prompted it.**
- **The outage.** NERSC's HPSS is in maintenance until **2026-11-06, 17:00** (nersc.gov/users/status, as Joseph
  relayed it on 2026-11-02). Every `hsi` call since about 08:15Z has waited on the maintenance flag.
- **What is blocked.** The bindings of GENCMP amendment E (E2, E2-A1), X, and 1B staged stages 0 and 1 each require an
  HPSS copy at the campaign's end, before the report.

**What is waiting** (sizes on pscratch, measured on 2026-11-02, deploy clones excluded):

| directory or file | size |
|---|---|
| `$P/fd-1b-staged-20261102/stage0-d0.tar` | 2,027,520 B (sha256 `a97f366c…`) |
| `$P/fd-1b-staged-20261102/stage0.tar` | 22,835,200 B (sha256 `51747c95…`) |
| `$P/gencmp-e2-20261102/` | 1.6 G |
| `$P/gencmp-e2a1-20261102/` | 1.6 G |
| `$P/gencmp-x-20261102/` | 1.6 G |

Stage 1's products are added as they are made.

**Why nothing is at risk.**
- **The purge rule.** pscratch purges files after 8 weeks without access.
- **When these files are exposed.** They were written on 2026-11-01 and 2026-11-02, so none is exposed before about
  2026-12-27.
- **The margin.** That is seven weeks after HPSS returns.

**The ruling.**
1. **Reports are not held for HPSS.** Each report's HPSS section reads "deferred: NERSC HPSS maintenance until
   2026-11-06 17:00". It lists each tar or directory with its sha256, or its file list's digest, as it stands on pscratch.
   Its merge is not held for the copy.
2. **One catch-up step, after maintenance clears,** copies everything in the table and stage 1's products.
   - Each lane runs it for its own campaign.
   - It uses the bound procedure: `hpssquota` first, `htar`/`hsi put` from an explicit list, then `hashcreate`,
     `hashverify`, and a retrieval compared by sha256.
   - Each lane records its result in a follow-up commit to its own report.
3. **The pscratch originals and tars stay** until their HPSS copies are verified.
4. **No interim CFS copy** is made unless Joseph asks for one. His CFS area is at 3.8 TB, against his 3 TB rule.
5. **Every other binding rule stands.**

Nothing is submitted, deposited or tagged.

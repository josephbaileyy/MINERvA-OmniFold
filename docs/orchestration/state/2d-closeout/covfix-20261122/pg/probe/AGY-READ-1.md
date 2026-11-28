# PG probe: agy read 1 and its dispositions

A sandboxed, read-only agy read (Gemini 3.8 Flash (High), `--sandbox`) of copies of `pg-probe.py`,
`pg-probe-launch.sh`, `test_pg_probe.py`, `mutants.py`, `LINE-TRACE.md`, §4.1–§4.2 of the declaration and §1.3 of
FD-F1-REPORT.md. Its input files' sha256 were unchanged after the read. The findings below are restated by the PG
session, not quoted, and each one's disposition is the PG session's.

| # | finding, restated | disposition |
|---|---|---|
| 1 | GNUPGHOME under `$SCRATCH` (Lustre) may not support gpg-agent's Unix socket, so the round trip would fail there | **Changed.** It is unverified whether Lustre refuses the socket. The node-local temp dir avoids the question and keeps the socket path short, which a local run showed matters: a 130-character path made gpg-agent fail to start. This departs from the director's "under the session's own scratch". Flagged to the director |
| 2 | a failed `gpgconf --kill` or a failing `ps` could read as "no agent survives" | **Fixed.** The kill must exit 0. A non-zero `ps` returns None, and the pass requires a measured list both before and after the kill. Tests and mutants added |
| 3 | a qualifier directory without its spline file or README read as "absent", which would trigger the 02a fallback | **Fixed.** `present` is now the directory and `complete` the two files. An incomplete entry is a STOP, never a fallback |
| 4 | a fallback to 02a did not check §4.1's premise that 02a shares 02b's classes | **Fixed.** When both configs resolve and differ, it is a STOP |
| 5 | conflicting override files were resolved by filename order | **Fixed.** Override files that disagree make the slot unresolved |
| 6 | a failure between creating GNUPGHOME and the `try` would leave the directory | **Fixed.** Creation is inside the `try`, and cleanup is guarded |
| 7 | a tune's own configuration may sit beside the CMC (`config/<tune>/`), not inside it | **Fixed: both are read.** F1's probe12 listing of `config/AR23_20i/` showed no nested tune directory, which is consistent with this finding. The CMC's `ModelConfiguration.xml` stays the base, and the spent-tune class control checks the reading |
| 8 | the "new pairing" test reuses a spent tune's exact pairing | **No change.** With the pooled spent set {NievesQELCCPXSec, NievesSimoVacasMECPXSec, SuSAv2MECPXSec}, every pairing of spent classes that is not a spent tune's own puts a class in the other slot, and `test_cross_slot_class_counts_as_spent` covers that case |
| 9 | the trace claimed coverage for a surviving agent and a touched ~/.gnupg that only a stub tested | **Fixed.** A touched ~/.gnupg, a failed kill and a blind `ps` now each have a test that fails without the check, and an HMAC fake gpg isolates them |
| 10 | with fd 0 closed, the pipe's write end could land on fd 3 and give a false "fd 3 open" | **Fixed.** fd 3 is checked before the pipe is made, and the probe never closes an fd it does not own |
| 11 | an uncanonicalised GNUPGHOME could miss an agent whose command line uses the real path | **Fixed.** `realpath` |
| 12 | a failed ssh connection leaves `pg-probe.out`, which blocks a rerun | **No change, by design.** A connect attempt is a record, and rerunning one is the director's decision, not the launcher's |

After the changes: 42 tests pass (`tests-local.log`) and 33 of 33 mutants are killed (`mutants.log`).

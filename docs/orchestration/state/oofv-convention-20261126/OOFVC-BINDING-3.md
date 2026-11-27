# OOFVC-BINDING-3: the OOFVC run in the r3 namespace, after the units false STOP

Follows OOFVC-BINDING-2 (#1405). In r2 the pilot and the eleven dumps passed (C-ROUTE in all twelve, with NuE brackets complete). Units job 62065064 then ended FAILED 8:0 in 114 s at a false STOP of C-ROUTE: ROOT 6.28's AsNumpy returns UChar_t flags as one-character strings, and `!= 0` read every row as routed to both trees. No unit ran, C-JOIN was not reached, and nothing moved. The charge was about 0.032 node-h, and the OOFVC total about 0.042. The receipts are in `receipts/attempt2-r2/`. The fix merged in #1410 (head `ba76d570fef2b330cb6f07e95183f253812b3399`): every read is normalized, other object columns are refused, flags outside {0,1} are refused (C-READ), with tests shaped like ROOT 6.28's output and 60/60 mutants killed.

## What is bound

Main at `51b6b4d8703d4b5f6f0a99b5ec20ab41d6caf35f`:
- `OOFVC-DECLARATION.md` (revision 9) sha256 `0f326b27b4fde487aaaa513b137dec361f0d4888fe12bff70340fbd99e1dba6c`;
- tool commit `b8077dfc73a47823e1e9235020dab28953941f11`;
- `launch/bound/`: `oofvc_dump.sh` `185c8b173c772ef880a722a95e42fd02b87ad99d661fe048322910f8186cf798`, `oofvc_units.sh` `f67bd73747807cbb31c614f18e795bce64ed770e3c99091d0ff4aba18e76566c`, `oofvc_post.sh` `567938b9cdf0d69285d0692c0130959c92d2ab58e9f30f43250b10ac5a0b4dde`, `oofvc_launch.sh` `8f09ec2d365a48041f1e11e9d70c0f46822dee0ebb9f992e7ca09d6e06982370`.

The namespace is `/pscratch/sd/j/josephrb/oofvc-20261126-r3/`. The first root and r2 stay untouched. Removing them is Joseph's call, and both go on the post-receipt list for him.

## Terms

Everything else stands as in OOFVC-BINDING-1 and -2: the NuE exception on §2.7's terms, the CFS CV dd iflag=noatime read with its bracket, the four steps one per GO with a cert check and fresh cov2d and limitation-resolver acks, route B only through the director, no resubmission, and the 2.0 node-h cap. cov2d re-confirmed its no-objection for r3 at 2026-11-27T01:28:31Z. The NERSC certificate is valid until 2026-11-27T14:22:19Z.

# OOFVC-BINDING-2: the OOFVC run in the r2 namespace, after the pilot's false STOP

Follows OOFVC-BINDING-1 (#1401). Attempt 1's pilot, job 62053260, ended FAILED 2:0 in 49 s at a false STOP in the NuE path check: it compared the canonical path with the literal one through the MParamFiles symlink. The binary never ran, and the charge was about 0.0002 node-h. The receipts are in `receipts/attempt1-pilot/`. The fix merged in #1404 (head `b2127ce3aee3c01df7d7cb7d823d28f6b52229ac`) and compares canonical against canonical, with both files required present, plus a symlink fixture test and the mutants SH_NUE_CANON and SH_NUE_EXISTS.

## What is bound

Main at `166a5dc079141cc9bec9c05dbac8b565c67e675c`:
- `OOFVC-DECLARATION.md` (revision 8) sha256 `5e9803ba1eb7619756d340d4e955b42c5f822a4b0b9252133ad79b003b3e73d5`;
- tool commit `d3127bd40fb48456993ee9e1fda23b81c3d74f89`;
- `2d-unfolding/oofvc/launch/bound/`: `oofvc_dump.sh` `7306001cd8a199b9d0f0efcc2562a58fd16dc5b337786e2391732a22c10ae290`, `oofvc_units.sh` `f5f19360af663c5afc17ecfba9164302e872344990b4d48632ce5fadff040584`, `oofvc_post.sh` `35c699f55a60ca876e0d629f0321c18b62169b6d1ec7d5d1c8fd9dd9bb8d8565`, `oofvc_launch.sh` `290ae9fd1b34b2bbb859c9f83a33fbcd25bb63546b3bd622572feeaa7b7f1dd6`.

The namespace is `/pscratch/sd/j/josephrb/oofvc-20261126-r2/`. Attempt 1's root `/pscratch/sd/j/josephrb/oofvc-20261126/` stays untouched, and its removal is a post-receipt step through the director.

## Terms

Everything else stands as in OOFVC-BINDING-1:
- the NuE exception on §2.7's terms, with the LL5D atime-post 2026-11-15T02:21:21Z, (b), (c) and the sacct fences;
- the CFS CV read by dd iflag=noatime with its atime bracket;
- the four steps, one per GO, with a cert check by command and fresh cov2d and limitation-resolver acks before each;
- route B only through the director, priced;
- no resubmission;
- the expected 0.3 node-h, capped at 2.0 node-h.

cov2d re-confirmed its no-objection for the r2 namespace at 2026-11-26T23:45:54Z, naming both reads and having checked the fix at b2127ce3. The NERSC certificate is valid until 2026-11-27T14:22:19Z.

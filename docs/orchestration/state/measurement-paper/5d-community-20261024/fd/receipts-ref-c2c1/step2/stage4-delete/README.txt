REF-C2C1 step two, stage 4: the deletion of the staged copies, the B9-form ledger row (REF-C2C1-BINDING-2.md ruling 2.4;
the director's GO of 2026-11-06 after the read's receipt #844 merged). Run by limitation-resolver:
refc2c1_stage4_delete_login.sh, sha256 2cc0415421a72a1b69a599b95201f38d0480219e19105bd9f2fa6d69bcd73c2b, on login04 at
2026-11-06T15:23:49Z-15:23:59Z, rc 0, at 0 node-h. Copied by O_NOATIME reads (pull_tar.py) from
/pscratch/sd/j/josephrb/ref-c2c1-20261106/stage4-ledger/. Full sha256 of each file: SHA256SUMS.txt.

SCOPE: only the $CV/$MC staging root that binding 2 §2.1 created, /pscratch/sd/j/josephrb/ref-c2c1-20261106/stage
(../stage/, #815). read/, read-2/, the units, the deploys and every COV2D path are untouched. The script uses literal
paths only; the one variable rm is the script deleting its own /dev/shm copy (`rm -f -- "$SELF"`), as in every connect.
Before the run it was sandbox-tested in /dev/shm against five cases: the clean case deletes both copies and the root,
while a wrong digest, an extra file, a subdirectory or a missing copy each STOP with nothing deleted.

LEDGER ROW (ledger.log):
- Contents of the root before, by stat only (root-contents-before.txt): exactly its two copies, nothing else.
    f 2144008221  josephrb 644  runEventLoopOmniFold_MEFHC.root
    f       5143  josephrb 644  runEventLoopMC_MEFHC.root
- `ls -la` before (15:23:49Z), and each copy's sha256 through an O_NOATIME read, equal to stage.json's pins:
    runEventLoopOmniFold_MEFHC.root  43f8cc16ab2688200d3e2e0ebb48012b23ada6d7882b8c68ecfc51c609aeb8df  (pin 43f8cc16...)
    runEventLoopMC_MEFHC.root        d40aea69235cdc98644e1bb3e622e579d6b81904c004c83fe50465079989f316  (pin d40aea69...)
- The deletion:
    2026-11-06T15:23:58.465Z  rm -v -- /pscratch/sd/j/josephrb/ref-c2c1-20261106/stage/runEventLoopOmniFold_MEFHC.root
    2026-11-06T15:23:58.982Z  rm -v -- /pscratch/sd/j/josephrb/ref-c2c1-20261106/stage/runEventLoopMC_MEFHC.root
    2026-11-06T15:23:58.989Z  rmdir -v -- /pscratch/sd/j/josephrb/ref-c2c1-20261106/stage
- After (15:23:58Z): `ls -la` of /pscratch/sd/j/josephrb/ref-c2c1-20261106, and each of the three paths reads "absent".
  Every other entry there is unchanged.
- The CFS sources ($CV, $MC) were not touched. They are the originals the copies were made from (inputs.CV_source,
  inputs.MC_source).

Files: ledger.log, root-contents-before.txt, stage4.done (0), the script as run, and pull_tar.py.

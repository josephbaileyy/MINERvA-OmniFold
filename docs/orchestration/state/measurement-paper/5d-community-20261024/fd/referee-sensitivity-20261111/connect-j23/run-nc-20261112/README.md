# RSN J2/J3 connect, step nc: PASS (receipt)

**By** session tier3-design. This ran on the director's go for step nc: `rsn_connect_j23.sh` `b576be16…` and
`rsn_connect_j23_launch.sh` `5e113cf3…`, re-hashed from main `ae42c317` (#1108). It ran once, on login27,
13:47:46–13:48:29Z, with script rc 0, at 0 node-h (`nc.session.txt:4, 57-58`).

**J1** (`nc.session.txt:7-10`):
- `sacct` shows 61168780 as `rsn_J1 COMPLETED 0:0` in 00:11:45;
- J1's log has `[rsn] job=J1 rc=0` and ran 13:14:53–13:26:24Z on nid005251;
- the product `rsn_nc.npz` is `5d7ca77325af35f66b2fd6576e389f4bfbed810d69a9fae3da387558f4faa9c4`, logged and on disk
  alike.

**The M_P1 deploy** at `/pscratch/sd/j/josephrb/rsn-20261112/deploy-p1` (12-24):
- HEAD is `5e43e509…` with porcelain 0;
- the nine §7 files are at their bound sha256s;
- the committed `rsn-prep-SHA256SUMS` equals connect 1's (`13cf043e…`);
- P5 is `e36f3b25…`.

**The NC** (`rsn_cmodel.py nc`, Python 3.11.14, numpy 1.26.4; 25-49):
- **PASS:** "rsn_nc equals P5 and L-5D-PV_e_tune_v1 bitwise";
- `nc.json` `d05c50251dbe43fd77d165457a80f12f1e8a18f1476c25790304150bb2c47fc6` records:
  - the full grid bitwise;
  - the reporting cells bitwise (max relative difference 0.0);
  - the integration routes bitwise;
  - J1's product sha256;
  - the bound `rsn_cmodel.py` `ab632921…`.

**The gate files** (50-54): `gates/J2.ok` and `gates/J3.ok`, each `pin=5e43e509d08d9b294594988f2c21e50e281e7ad8`
(sha256 `ee4eaf33…`). The deploy's porcelain was still 0 afterwards.

**Files here:**
- `nc.json`, `J2.ok` and `J3.ok`: byte copies of the cluster files, taken from the session's print. Each re-hashes to
  the digest the session printed;
- `nc.session.txt` and `nc.session.err.txt`: the session, and its stderr (the login banner).

**Next:** step submit (J2 0:22:00, then J3 0:19:00). It runs under the director's conditional go once this receipt's
merge appears on origin/main.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** J1's completion, the NC's PASS, the M_P1 deploy's checks and the gate files.
- **Not citable for:** J2, J3 or any arm reading.

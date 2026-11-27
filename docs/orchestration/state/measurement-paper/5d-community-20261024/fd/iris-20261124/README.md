# iris balance receipt, 2026-11-24T06:55:33Z (login05)

**By** limitation-resolver, at the director's request (2026-11-24): one read-only query for the COVFIX ceiling binding,
in the E96 lane's form (`timeout 120 iris < /dev/null`). Nothing else ran, and nothing was written on the cluster.

**How it ran.**
- The Mac launched one ssh session to saul.nersc.gov, which hopped to login05 and ran exactly the line in
  [`remote-command.txt`](remote-command.txt):
  `echo "utc $(date -u +%FT%TZ)"; echo "node $(hostname)"; echo "== iris"; timeout 120 iris < /dev/null 2>&1; echo "iris rc=$?"`.
- The cert was valid to 2026-11-25T01:36:35Z.
- ssh rc 0 ([`ssh-rc.txt`](ssh-rc.txt)) and iris rc 0.
- [`iris.out`](iris.out) is the session's whole stdout, verbatim. [`iris.err`](iris.err) holds only the login banner.

**The output, verbatim** (from `iris.out`):

```
utc 2026-11-24T06:55:33Z
node login05
== iris
Project      Charged(user)    Allocated(user)     Charged    Allocated
---------  ---------------  -----------------  ----------  -----------
m3246               2612.2            10000.0     19369.6      20000.0
m3246_g             1296.2            90000.0    152511.9     180000.0
iris rc=0
```

**The project's remaining hours,** read from the `m3246` row (the CPU allocation; `m3246_g` is the GPU allocation):
- **remaining for all users: 20000.0 − 19369.6 = 630.4 node-h**, the project pool;
- remaining under this user's own allocation: 10000.0 − 2612.2 = 7387.8 node-h.

This is a point-in-time balance of an allocation-year pool, not a ceiling. It is CITABLE FOR the balance at that time,
and NOT CITABLE FOR any physics result.

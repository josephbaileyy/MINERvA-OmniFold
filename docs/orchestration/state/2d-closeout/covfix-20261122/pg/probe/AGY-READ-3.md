# PG probe rev 3: agy read 3

agy (Gemini 3.8 Flash (High), `--sandbox`) did a read-only review of copies of these files:
- `pg-probe.py`, `pg-probe-launch.py`, `test_pg_probe.py`, `mutants.py`;
- `LINE-TRACE.md`, `CODEX2-READ-2.md`;
- §4.1–§4.2 of the declaration;
- the public GENIE R-3_04_00 configuration files and GnuPG `homedir.c` and `zb32.c` that `CODEX2-READ-2.md` cites.

The sha256 of every input was unchanged after the read.

Restated by the PG session:
- agy judged each of codex-school2's 6 blocking items from read 2 fixed in the code.
- It checked the zbase32 alphabet, the 120-bit SHA-1 suffix and the `/run/user/<uid>/gnupg/d.` layout against the
  GnuPG sources, and the hybrid's default and branches against the GENIE files.
- It reported no findings in any category.

A read that finds nothing is weak evidence on its own. The rev 3 checks rest on the tests and mutants
(`tests-local.log`, `mutants.log`) and on codex-school2's confirm, which cov2d runs.

**Changes after this read.** agy read the copies before the first full mutant run. Three mutants survived it, and
the PG session then made these changes, which agy has not read:
- `catalog` dropped its separate empty-spline branch. An empty file already fails the structural check, because it
  has no root element.
- `_inside` now compares real paths on both sides. Before, a socket dir reached through a link failed the
  reported-socket check by accident, and the explicit real-path check could never fire alone.
- `test_invalid_receipts_are_kept` gained a complete STOP record followed by a trailing line, and one repeated twice.
